"""Constant folding and propagation on TIR (T015).

Folds operations whose operands are compile-time constants and replaces
them with constant materialisations; propagates value-identical
identities away.  Every fold is exact under the source contract
(IR-NUMERIC-POLICY):

* integer folds wrap to the operand width with the operand's
  signedness (two's complement -- the wrap semantics the verifier's
  index-math contract declares);
* signed division/remainder fold only with a nonzero constant divisor
  and never on the INT_MIN / -1 overflow case; unsigned forms reduce
  the operands modulo the width first;
* float add/sub/mul fold through fp64 and round once to the operand
  width (exact: the intermediate carries more than 2p+2 bits); float
  division/remainder and every special math function are DECLINED (the
  lowering owns their accuracy contracts -- a recorded policy, never a
  guessed rounding);
* float-to-int conversion folds only when the truncated value is in
  range and the operand is finite (out-of-range/NaN is undefined at the
  source level);
* identity elimination (``x + 0``, ``x * 1``, ``x & 0`` ...) applies to
  INTEGER and BOOL operands only: the float forms are refused because
  ``x * 0`` is not ``0`` for NaN/Inf and ``x + 0`` is not ``x`` for
  ``-0.0`` (absolute_kernel's ``0 * x`` guard is exactly this refusal);
* path conditions: inside an ``if`` arm the condition value is known
  (true in the then-arm, false in the else-arm), so a ``where`` on the
  arm's own condition folds to the taken branch.

Folds never treat a loop-carried initialiser as its outside value: an
operand reinterpreted inside a loop body (the MIR head-parameter
override) makes the operation per-iteration, and folding it would
freeze the initial value (the induction increment ``add(0, step)`` is
the canonical trap -- declined, recorded).
"""
from __future__ import annotations

import math
import struct
from typing import Dict, List, Optional, Tuple

from a100c.ir import tir
from a100c.passes import rewrite
from a100c.passes.analyses import LoopStructure, Pos, _child_step

__all__ = ["ConstPropPass"]


# ---------------------------------------------------------------------------
# exact width-preserving arithmetic
# ============================================================================

def _mask(width: int) -> int:
    return (1 << width) - 1


def _to_int(value: int, type_: tir.Type) -> int:
    """Normalise a Python int into the type's two's-complement range."""
    v = value & _mask(type_.width)
    if type_.signed and v >= (1 << (type_.width - 1)):
        v -= (1 << type_.width)
    return v


def _as_unsigned(value: int, type_: tir.Type) -> int:
    return value & _mask(type_.width)


def _int_min(type_: tir.Type) -> int:
    return -(1 << (type_.width - 1))


def _int_max(type_: tir.Type) -> int:
    if type_.signed:
        return (1 << (type_.width - 1)) - 1
    return _mask(type_.width)


def _round_float(value: float, type_: tir.Type) -> Optional[float]:
    """Round one fp64 value to the destination width (round-to-nearest,
    ties-to-even -- IEEE).  Returns None for widths this cannot express
    (never guessed)."""
    try:
        if type_.width == 64:
            return float(value)
        if type_.width == 32:
            return struct.unpack("<f", struct.pack("<f", value))[0]
        if type_.width == 16 and type_.name == "fp16":
            return struct.unpack("<e", struct.pack("<e", value))[0]
        if type_.width == 16 and type_.name == "bf16":
            # bf16: the top 16 bits of fp32, round-to-nearest-even on the
            # low 16 bits (an overflow past the finite range rounds to
            # inf, exactly like the hardware conversion)
            bits = struct.unpack("<I", struct.pack("<f", value))[0]
            low = bits & 0xFFFF
            rounded = bits & 0xFFFF0000
            if low > 0x8000 or (low == 0x8000 and (rounded & 0x10000)):
                rounded += 0x10000
            if 0x7F7F_FFFF < rounded < 0x7F80_0000:
                rounded = 0x7F80_0000          # round up to +inf
            elif 0xFF7F_FFFF < rounded < 0xFF80_0000:
                rounded = 0xFF80_0000          # round up to -inf
            return struct.unpack("<f", struct.pack("<I", rounded))[0]
    except (OverflowError, ValueError):
        return None
    return None


def _float_ok(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


# ---------------------------------------------------------------------------
# the fold evaluator
# ============================================================================

def _const_of(v: tir.Value) -> Optional[object]:
    """The compile-time constant a value carries: a const op's result,
    or a broadcast of one (the frontend materialises constant blocks as
    broadcasts of rank-0 constants)."""
    if v.producer is None:
        return None
    if v.producer.op == "const":
        return v.producer.attrs.get("value")
    if v.producer.op == "broadcast":
        operand = v.producer.operands[0]
        if operand.rank == 0 and operand.producer is not None \
                and operand.producer.op == "const":
            return operand.producer.attrs.get("value")
    return None


_BIN = {"arith.add", "arith.sub", "arith.mul", "bit.and", "bit.or",
        "bit.xor", "bit.shl", "bit.ashr", "bit.lshr", "arith.sdiv",
        "arith.udiv", "arith.srem", "arith.urem", "arith.fdiv",
        "arith.frem", "arith.div_rn"}

_FLOAT_IDENT = {"arith.add", "arith.sub", "arith.mul"}


def _fold_binop(op: tir.Op) -> Optional[Tuple[str, object]]:
    """Fold a two-operand op over constants.  Returns ("const", value) or
    ("identity", index) -- the operand index that survives an identity
    elimination -- or None (not foldable / refused)."""
    code = op.op
    lhs, rhs = op.operands
    type_ = lhs.type
    a = _const_of(lhs)
    b = _const_of(rhs)

    if type_.is_float():
        if code not in _FLOAT_IDENT:
            return None                 # fdiv/frem/div_rn: rounding policy
        if a is None or b is None:
            return None                 # float identity: refused below
        if not (_float_ok(a) and _float_ok(b)):
            return None
        if code == "arith.add":
            v = float(a) + float(b)
        elif code == "arith.sub":
            v = float(a) - float(b)
        else:
            v = float(a) * float(b)
        rounded = _round_float(v, type_)
        if rounded is None or not math.isfinite(rounded):
            return None                 # inf/NaN stay materialised ops
        return ("const", rounded)

    # integer / bool operands
    if a is not None and b is not None:
        if type_.is_bool():
            a_b, b_b = bool(a), bool(b)
            if code == "bit.and":
                return ("const", a_b and b_b)
            if code == "bit.or":
                return ("const", a_b or b_b)
            if code == "bit.xor":
                return ("const", a_b != b_b)
            return None
        if not (isinstance(a, int) and isinstance(b, int)):
            return None
        w = type_.width
        if code == "arith.add":
            return ("const", _to_int(a + b, type_))
        if code == "arith.sub":
            return ("const", _to_int(a - b, type_))
        if code == "arith.mul":
            return ("const", _to_int(a * b, type_))
        if code == "bit.and":
            return ("const", _to_int(a & b, type_))
        if code == "bit.or":
            return ("const", _to_int(a | b, type_))
        if code == "bit.xor":
            return ("const", _to_int(a ^ b, type_))
        if code == "bit.shl":
            if not (0 <= b < w):
                return None
            return ("const", _to_int(a << b, type_))
        if code == "bit.ashr":
            if not (0 <= b < w):
                return None
            return ("const", _to_int(a >> b, type_))
        if code == "bit.lshr":
            if not (0 <= b < w):
                return None
            return ("const", _to_int(_as_unsigned(a, type_) >> b, type_))
        if code == "arith.sdiv":
            if b == 0 or (a == _int_min(type_) and b == -1):
                return None
            q = abs(a) // abs(b)
            if (a < 0) != (b < 0):
                q = -q
            return ("const", _to_int(q, type_))
        if code == "arith.srem":
            if b == 0 or (a == _int_min(type_) and b == -1):
                return None
            q = abs(a) // abs(b)
            if (a < 0) != (b < 0):
                q = -q
            return ("const", _to_int(a - q * b, type_))
        if code in ("arith.udiv", "arith.urem"):
            if b == 0:
                return None
            ua, ub = _as_unsigned(a, type_), _as_unsigned(b, type_)
            if code == "arith.udiv":
                return ("const", _to_int(ua // ub, type_))
            return ("const", _to_int(ua % ub, type_))
        return None

    # identity elimination: integer/bool only, one constant operand
    if type_.is_bool() or type_.is_int():
        ones = _mask(type_.width)
        if code == "arith.add" and b == 0:
            return ("identity", 0)
        if code == "arith.add" and a == 0:
            return ("identity", 1)
        if code == "arith.sub" and b == 0:
            return ("identity", 0)
        if code == "arith.mul" and b == 1:
            return ("identity", 0)
        if code == "arith.mul" and a == 1:
            return ("identity", 1)
        if code == "arith.mul" and (a == 0 or b == 0):
            return ("const", 0)
        if code == "bit.and" and (a == 0 or b == 0):
            return ("const", 0)
        if code == "bit.or" and b == 0:
            return ("identity", 0)
        if code == "bit.or" and a == 0:
            return ("identity", 1)
        if code == "bit.xor" and b == 0:
            return ("identity", 0)
        if code == "bit.xor" and a == 0:
            return ("identity", 1)
        if code == "bit.shl" and b == 0:
            return ("identity", 0)
        if code == "bit.and":
            if a == ones and b == ones:
                return ("const", _to_int(-1, type_))
            if a == ones:
                return ("identity", 1)
            if b == ones:
                return ("identity", 0)
    return None


def _fold_cmp(op: tir.Op) -> Optional[bool]:
    lhs, rhs = op.operands
    a = _const_of(lhs)
    b = _const_of(rhs)
    if a is None or b is None:
        return None
    type_ = lhs.type
    if type_.is_float():
        if not (_float_ok(a) and _float_ok(b)):
            return None
        a, b = float(a), float(b)
    elif type_.is_bool():
        a, b = bool(a), bool(b)
    elif not type_.signed:
        a, b = _as_unsigned(a, type_), _as_unsigned(b, type_)
    code = op.op
    if code == "cmp.lt":
        return a < b
    if code == "cmp.le":
        return a <= b
    if code == "cmp.gt":
        return a > b
    if code == "cmp.ge":
        return a >= b
    if code == "cmp.eq":
        return a == b
    if code == "cmp.ne":
        return a != b
    return None


def _fold_unary(op: tir.Op) -> Optional[object]:
    v = op.operands[0]
    value = _const_of(v)
    if value is None:
        return None
    type_ = v.type
    if op.op == "arith.neg" and type_.is_int():
        return _to_int(-value, type_)
    if op.op == "arith.fneg" and _float_ok(value):
        return -float(value)
    if op.op == "logical.not":
        return not bool(value)
    if op.op == "bit.invert" and type_.is_int():
        return _to_int(~value, type_)
    return None


def _fold_convert(op: tir.Op) -> Optional[object]:
    v = op.operands[0]
    value = _const_of(v)
    if value is None:
        return None
    src, dst = v.type, op.results[0].type
    if src.is_bool():
        if dst.is_int():
            return _to_int(1 if value else 0, dst)
        if dst.is_float():
            return 1.0 if value else 0.0
        return None
    if src.is_int():
        if dst.is_bool():
            return value != 0
        if dst.is_int():
            return _to_int(value, dst)
        if dst.is_float():
            return _round_float(float(value), dst)
        return None
    if src.is_float() and _float_ok(value):
        x = float(value)
        if dst.is_bool():
            return x != 0.0
        if dst.is_int():
            if not math.isfinite(x):
                return None
            t = math.trunc(x)
            if t < _int_min(dst) or t > _int_max(dst):
                return None
            return _to_int(int(t), dst)
        if dst.is_float():
            return _round_float(x, dst)
    return None


def _fold_bitcast(op: tir.Op) -> Optional[object]:
    v = op.operands[0]
    value = _const_of(v)
    if value is None:
        return None
    src, dst = v.type, op.results[0].type
    if src.is_int() and dst.is_int():
        return _to_int(value, dst)
    try:
        if src.is_float() and dst.is_int():
            if src.width == 32:
                bits = struct.unpack("<I", struct.pack("<f", float(value)))[0]
                return _to_int(bits, dst)
            if src.width == 64:
                bits = struct.unpack("<Q", struct.pack("<d", float(value)))[0]
                return _to_int(bits, dst)
            if src.name == "fp16":
                bits = struct.unpack("<H", struct.pack("<e", float(value)))[0]
                return _to_int(bits, dst)
        if src.is_int() and dst.is_float():
            if dst.width == 32:
                return struct.unpack("<f", struct.pack(
                    "<I", _as_unsigned(value, src)))[0]
            if dst.width == 64:
                return struct.unpack("<d", struct.pack(
                    "<Q", _as_unsigned(value, src)))[0]
            if dst.name == "fp16":
                return struct.unpack("<e", struct.pack(
                    "<H", _as_unsigned(value, src)))[0]
    except (OverflowError, ValueError):
        return None
    return None


def _fold_maxmin(op: tir.Op) -> Optional[object]:
    lhs, rhs = op.operands
    a = _const_of(lhs)
    b = _const_of(rhs)
    if a is None or b is None:
        return None
    code = op.op
    if code.endswith("f"):
        if not (_float_ok(a) and _float_ok(b)):
            return None
        if math.isnan(float(a)) or math.isnan(float(b)):
            return None                 # NaN policy is carried by the op code
        if float(a) == 0.0 and float(b) == 0.0:
            return None                 # the +/-0.0 tie is policy-bound
        if code in ("arith.maxnumf", "arith.maximumf"):
            return max(float(a), float(b))
        return min(float(a), float(b))
    if code.endswith("si"):
        return max(a, b) if code.startswith("arith.max") else min(a, b)
    ua, ub = _as_unsigned(a, lhs.type), _as_unsigned(b, rhs.type)
    return (ua if ua > ub else ub) if code.startswith("arith.max") \
        else (ua if ua < ub else ub)


# ---------------------------------------------------------------------------
# the pass
# ============================================================================

class ConstPropPass:
    name = "constprop"
    ANALYSES_CONSUMED = ("loops",)
    ANALYSES_PRESERVED = ()
    ANALYSES_INVALIDATED = ("dominance", "liveness", "loops",
                            "memory_effects")

    def run(self, module: tir.Module, ctx) -> bool:
        # the loop view is refreshed after EVERY mutation: an insertion
        # before a loop shifts its position, and a stale enclosure answer
        # would silently unguard the loop-carried reinterpretation (the
        # IR-ANALYSIS-VALIDITY rule: a stale analysis result is never
        # read -- the suite's digest check recomputes on demand)
        state = {"loops": ctx.get("loops")}
        trace = ctx.trace
        changed = [False]

        def refresh_loops() -> None:
            # the frozen-view contract: re-bind after the mutation, then
            # read (the suite recomputes through the digest check)
            ctx.refresh()
            state["loops"] = ctx.get("loops")

        def materialise(value, type_: tir.Type, shape: tir.Shape,
                        loc) -> Tuple[List[tir.Op], tir.Value]:
            """A constant at ``shape``: a rank-0 const broadcast over the
            extent values, realised where the folded result had real
            extents (a real extent is always consumable where a broadcast
            one was expected; the reverse is the verifier's rejection)."""
            c = tir.Op.const(value, type_, loc)
            if not shape:
                return [c], c.result()
            bc = tir.Op.broadcast(
                c.result(),
                tuple(tir.Extent(e.value, True) for e in shape), loc)
            if any(not e.broadcast for e in shape):
                rz = tir.Op.realize(bc.result(), loc)
                return [c, bc, rz], rz.result()
            return [c, bc], bc.result()

        def swap(block: tir.Block, index: int, new_ops: List[tir.Op],
                 old: tir.Op, new_value: tir.Value, what: str) -> int:
            """Insert the materialisation, rewire the uses, drop the old
            op unless a region join resolves through its def.  Returns the
            statement count consumed.  (The loop view is refreshed by the
            CALLER once the swap fully settles -- a mid-swap refresh would
            bind the analysis to the transient between insert and delete,
            whose statement indices match neither state.)"""
            block.statements[index:index] = new_ops
            result = old.results[0]
            n = rewrite.guarded_replace_uses(module, result, new_value,
                                             state["loops"])
            rewrite.copy_aliases(result, new_value)
            if n == 0:
                # every use site was a guarded (loop-carried) meaning:
                # the materialisation is unused -- take it back out
                del block.statements[index:index + len(new_ops)]
                trace.record_decline(
                    "uses remain at loop-carried sites: the fold changes "
                    "nothing (the def stays)")
                return 1
            changed[0] = True
            if result.vid not in rewrite.protected_defs(module) \
                    and rewrite.count_uses(module, result) == 0:
                del block.statements[index + len(new_ops)]
                rewrite.drop_protected_cache(module)
                trace.record_fired(what)
                return len(new_ops)
            trace.record_decline(
                "region-final binding kept: the join resolves the name "
                "at the def (the folded materialisation still replaces "
                "the uses)")
            trace.record_fired(what)
            return len(new_ops) + 1

        def walk_block(block: tir.Block, base: Pos,
                       path_conds: Dict[int, bool]) -> None:
            i = 0
            while i < len(block.statements):
                st = block.statements[i]
                here = base + (_child_step("op", i),)
                if isinstance(st, tir.If):
                    then_conds = dict(path_conds)
                    then_conds[st.cond.vid] = True
                    walk_block(st.then, here + (_child_step("then", 0),),
                               then_conds)
                    else_conds = dict(path_conds)
                    else_conds[st.cond.vid] = False
                    walk_block(st.els, here + (_child_step("else", 0),),
                               else_conds)
                    i += 1
                    continue
                if isinstance(st, tir.Loop):
                    walk_block(st.body, here + (_child_step("body", 0),),
                               dict(path_conds))
                    i += 1
                    continue
                if not isinstance(st, tir.Op) or not st.results:
                    i += 1
                    continue
                result = st.results[0]
                if rewrite.count_uses(module, result) == 0:
                    # nothing consumes the result: folding it changes no
                    # use (DCE owns the dead def)
                    i += 1
                    continue
                reinterpreted = state["loops"].reinterpret_inits(here)

                def _reinterpreted(o: tir.Value) -> bool:
                    """An operand whose meaning at this position is the
                    CURRENT iteration's value: the carried init itself,
                    or a rank-0 broadcast of one (``_const_of`` reads
                    through that broadcast -- folding it would treat the
                    per-iteration channel as its initial constant)."""
                    if o.vid in reinterpreted:
                        return True
                    prod = o.producer
                    if prod is not None and prod.op == "broadcast":
                        inner = prod.operands[0]
                        if inner.rank == 0 \
                                and inner.vid in reinterpreted:
                            return True
                    return False

                if any(_reinterpreted(o) for o in st.operands):
                    if st.op in _BIN or st.op in tir.CMP_PREDS:
                        trace.record_decline(
                            "loop-carried operand: the operation is "
                            "per-iteration inside the body (the induction "
                            "update is never folded)")
                    i += 1
                    continue
                fold: Optional[Tuple[str, object]] = None
                what = ""
                if st.op in _BIN:
                    fold = _fold_binop(st)
                    what = f"fold {st.op}"
                elif st.op in tir.CMP_PREDS:
                    v = _fold_cmp(st)
                    fold = ("const", v) if v is not None else None
                    what = f"fold {st.op}"
                elif st.op in ("arith.neg", "arith.fneg", "logical.not",
                               "bit.invert"):
                    v = _fold_unary(st)
                    fold = ("const", v) if v is not None else None
                    what = f"fold {st.op}"
                elif st.op == "convert":
                    v = _fold_convert(st)
                    fold = ("const", v) if v is not None else None
                    what = "fold convert"
                elif st.op == "bitcast":
                    v = _fold_bitcast(st)
                    fold = ("const", v) if v is not None else None
                    what = "fold bitcast"
                elif st.op in tir.MAXMIN_OPS:
                    v = _fold_maxmin(st)
                    fold = ("const", v) if v is not None else None
                    what = f"fold {st.op}"
                elif st.op == "select.where":
                    cond = st.operands[0]
                    root = cond
                    if root.producer is not None \
                            and root.producer.op == "broadcast" \
                            and root.producer.operands[0].rank == 0:
                        root = root.producer.operands[0]
                    known = path_conds.get(root.vid)
                    cval = _const_of(root)
                    if cval is not None:
                        known = bool(cval)
                    if known is True:
                        fold = ("identity", 1)
                        what = "path-condition where -> then"
                    elif known is False:
                        fold = ("identity", 2)
                        what = "path-condition where -> else"
                if fold is None:
                    self._record_decline(st, trace)
                    i += 1
                    continue
                kind, value = fold
                if kind == "identity":
                    survivor = st.operands[value]
                    n = rewrite.guarded_replace_uses(module, result,
                                                     survivor,
                                                     state["loops"])
                    rewrite.copy_aliases(result, survivor)
                    if n == 0:
                        # every use site was a guarded (loop-carried)
                        # meaning: nothing changed
                        trace.record_decline(
                            "uses remain at loop-carried sites: the fold "
                            "changes nothing (the def stays)")
                        i += 1
                        continue
                    changed[0] = True
                    if result.vid not in rewrite.protected_defs(module) \
                            and rewrite.count_uses(module, result) == 0:
                        del block.statements[i]
                        rewrite.drop_protected_cache(module)
                        refresh_loops()
                        i -= 1
                    else:
                        trace.record_decline(
                            "region-final binding kept: the join resolves "
                            "the name at the def")
                    trace.record_fired(what)
                    i += 1
                    continue
                new_ops, new_value = materialise(
                    value, result.type, result.shape, st.loc)
                i += swap(block, i, new_ops, st, new_value, what)
                refresh_loops()

        for fn in module.functions:
            walk_block(fn.body, (), {})
        return changed[0]

    @staticmethod
    def _record_decline(st: tir.Op, trace) -> None:
        """Record only the legality refusals (an operation that is merely
        not foldable is not a decline)."""
        if st.op in ("arith.fdiv", "arith.frem", "arith.div_rn"):
            if _const_of(st.operands[0]) is not None \
                    and _const_of(st.operands[1]) is not None:
                trace.record_decline(
                    "float division/remainder folding declined (rounding "
                    "policy: the exact form is kept)")
        elif st.op in _FLOAT_IDENT and st.operands[0].type.is_float():
            a = _const_of(st.operands[0])
            b = _const_of(st.operands[1])
            if (st.op in ("arith.add", "arith.sub")
                    and (a == 0 or b == 0)) \
                    or (st.op == "arith.mul" and (a in (0, 1) or b in (0, 1))):
                trace.record_decline(
                    "float identity folding declined (NaN/Inf/-0.0 "
                    "semantics: 0*x is not 0 and x+0 is not x)")
        elif st.op == "convert" and st.operands[0].type.is_float() \
                and st.results[0].type.is_int():
            if _const_of(st.operands[0]) is not None:
                trace.record_decline(
                    "float-to-int folding declined (out-of-range/NaN is "
                    "undefined at the source level)")
