"""Strength reduction on TIR affine index/address expressions (T015).

Replaces expensive integer operations on index expressions with cheaper
equivalent forms, exactly (MECH-INNER-LOOP-FORMS' arithmetic half):

* ``x * 2^k``          -> ``x << k``
* ``x * c`` with ``c`` a sum of at most two powers of two (and the
  negatives of those) -> shifts and one add/sub (modular arithmetic:
  the identity holds under the width's wraparound for every
  signedness);
* ``x / 2^k`` and ``x % 2^k`` UNSIGNED -> ``x >> k`` / ``x & (2^k-1)``;
* ``x / 2^k`` and ``x % 2^k`` SIGNED -> the sign-correction sequence
  (``a = (x >> (w-1)) & (d-1)``; ``q = (x + a) >> k``; the remainder
  ``r = ((x + a) & (d-1)) - a``) -- exact for every value including
  INT_MIN (the correction cannot overflow: ``x >= -2^(w-1)`` and
  ``a <= 2^(w-1)-1``);
* division/remainder by a non-power-of-two constant -> DECLINED (magic
  numbers are out of scope for the correctness-only delivery; the
  refusal is recorded).

Declared floating policy: floating expressions are never rewritten --
an fdiv by a power of two is exactly a multiplication by the exact
reciprocal, but the pass declines the whole floating class so the
emitted numeric path is never changed by an integer-motivated pass
(recorded per candidate).

Rewrites preserve the operand references (a loop-carried
reinterpretation keeps its meaning -- the induction is never frozen)
and the result's type and extent flags; constant right operands are
splatted to the left operand's shape exactly like the frontend's own
constant materialisation.  ``x * 0`` and ``x * 1`` belong to constprop's
identity elimination and are left to it.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

from a100c.ir import tir
from a100c.passes import rewrite
from a100c.passes.analyses import LoopStructure, Pos, _child_step

__all__ = ["StrengthReductionPass"]


def _const_int(v: tir.Value) -> Optional[int]:
    """The integer constant a value carries: a const op's result or a
    broadcast of one (the frontend's constant-block materialisation)."""
    if v.producer is None:
        return None
    if v.producer.op == "broadcast":
        v = v.producer.operands[0]
        if v.rank != 0 or v.producer is None:
            return None
    if v.producer is not None and v.producer.op == "const":
        value = v.producer.attrs.get("value")
        if isinstance(value, int) and not isinstance(value, bool):
            return value
    return None


def _pow2_terms(c: int, limit: int = 2) -> Optional[List[int]]:
    """The powers of two summing to |c| (at most ``limit`` distinct
    terms), or None."""
    if c == 0:
        return None
    a = abs(c)
    terms: List[int] = []
    k = 0
    while a:
        if a & 1:
            terms.append(k)
            if len(terms) > limit:
                return None
        a >>= 1
        k += 1
    return terms


class StrengthReductionPass:
    name = "strength_reduction"
    ANALYSES_CONSUMED = ()
    ANALYSES_PRESERVED = ()
    ANALYSES_INVALIDATED = ("dominance", "liveness", "loops",
                            "memory_effects")

    def run(self, module: tir.Module, ctx) -> bool:
        trace = ctx.trace
        # the loop view is refreshed after EVERY mutation: an insertion
        # before a loop shifts its position, and a stale enclosure answer
        # would silently unguard the loop-carried reinterpretation (the
        # IR-ANALYSIS-VALIDITY rule -- the suite's digest recomputes)
        state = {"loops": ctx.get("loops")}
        changed = [False]

        def refresh_loops() -> None:
            # the frozen-view contract: re-bind after the mutation, then
            # read (the suite recomputes through the digest check)
            ctx.refresh()
            state["loops"] = ctx.get("loops")

        def splat(value: int, type_: tir.Type, shape: tir.Shape,
                  loc) -> Tuple[List[tir.Op], tir.Value]:
            ops: List[tir.Op] = []
            c = tir.Op.const(value, type_, loc)
            ops.append(c)
            if shape:
                bc = tir.Op.broadcast(
                    c.result(),
                    tuple(tir.Extent(e.value, True) for e in shape), loc)
                ops.append(bc)
                return ops, bc.result()
            return ops, c.result()

        def swap(block: tir.Block, index: int, old: tir.Op,
                 new_ops: List[tir.Op], what: str) -> int:
            """Insert the sequence, rewire the uses to its final result,
            drop the old op unless a region join resolves through its
            def.  Returns the statements consumed.  (The loop view is
            refreshed by the CALLER once the swap settles -- a mid-swap
            refresh would bind the analysis to the transient between
            insert and delete.)"""
            value = new_ops[-1].result()
            if rewrite.count_uses(module, old.results[0]) == 0:
                # a dead op is DCE's, not a strength form's
                return 1
            block.statements[index:index] = new_ops
            result = old.results[0]
            n = rewrite.guarded_replace_uses(module, result, value,
                                             state["loops"])
            rewrite.copy_aliases(result, value)
            if n == 0:
                # every use site was a guarded (loop-carried) meaning:
                # the sequence is unused -- take it back out
                del block.statements[index:index + len(new_ops)]
                refresh_loops()
                trace.record_decline(
                    "uses remain at loop-carried sites: the rewrite "
                    "changes nothing (the def stays)")
                return 1
            changed[0] = True
            if result.vid not in rewrite.protected_defs(module) \
                    and rewrite.count_uses(module, result) == 0:
                del block.statements[index + len(new_ops)]
                rewrite.drop_protected_cache(module)
                refresh_loops()
                trace.record_fired(what)
                return len(new_ops)
            trace.record_decline(
                "region-final binding kept: the join resolves the name "
                "at the def")
            trace.record_fired(what)
            refresh_loops()
            return len(new_ops) + 1

        def rewrite_mul(block: tir.Block, index: int, st: tir.Op) -> int:
            lhs, rhs = st.operands
            type_ = lhs.type
            c = _const_int(rhs)
            x = lhs
            if c is None:
                c = _const_int(lhs)
                x = rhs
            if c is None or c in (0, 1, -1):
                # 0/1 belong to constprop's identity elimination; -1 is
                # a plain negation with no strength to reduce
                if c == -1:
                    trace.record_decline(
                        "mul by -1 is a negation, not a strength form")
                return 1
            terms = _pow2_terms(c, 2)
            if terms is None:
                trace.record_decline(
                    f"mul by {c}: not a sum of <= 2 powers of two "
                    "(magic-number forms are out of scope)")
                return 1
            loc = st.loc
            new_ops: List[tir.Op] = []
            if len(terms) == 1:
                k_ops, k = splat(terms[0], type_, x.shape, loc)
                new_ops.extend(k_ops)
                new_ops.append(tir.Op.binop("bit.shl", x, k, loc))
                what = f"mul by {c} -> shl {terms[0]}"
            else:
                a, b = sorted(terms)
                ka_ops, ka = splat(a, type_, x.shape, loc)
                kb_ops, kb = splat(b, type_, x.shape, loc)
                new_ops.extend(ka_ops)
                new_ops.extend(kb_ops)
                s1 = tir.Op.binop("bit.shl", x, ka, loc)
                s2 = tir.Op.binop("bit.shl", x, kb, loc)
                new_ops.extend((s1, s2))
                new_ops.append(tir.Op.binop("arith.add", s1.result(),
                                            s2.result(), loc))
                what = f"mul by {c} -> shifts+add"
            if c < 0:
                new_ops.append(tir.Op.unary(
                    "arith.neg", new_ops[-1].result(), loc))
                what = f"mul by {c} -> neg(shift form)"
            return swap(block, index, st, new_ops, what)

        def rewrite_divrem(block: tir.Block, index: int,
                           st: tir.Op) -> int:
            code = st.op
            x, d_v = st.operands
            type_ = x.type
            d = _const_int(d_v)
            if d is None or d <= 0:
                if d is not None:
                    trace.record_decline(
                        "division/remainder by a non-positive constant "
                        "has no strength form")
                return 1
            if d & (d - 1):
                trace.record_decline(
                    f"division/remainder by {d} (not a power of two: "
                    "magic-number forms are out of scope)")
                return 1
            k = d.bit_length() - 1
            w = type_.width
            loc = st.loc
            new_ops: List[tir.Op] = []
            unsigned = code in ("arith.udiv", "arith.urem")
            if unsigned:
                if code.endswith("div"):
                    ks_ops, ks = splat(k, type_, x.shape, loc)
                    new_ops.extend(ks_ops)
                    new_ops.append(tir.Op.binop("bit.lshr", x, ks, loc))
                    what = f"{code} by {d} -> lshr {k}"
                else:
                    ms_ops, ms = splat(d - 1, type_, x.shape, loc)
                    new_ops.extend(ms_ops)
                    new_ops.append(tir.Op.binop("bit.and", x, ms, loc))
                    what = f"{code} by {d} -> and {d - 1}"
                return swap(block, index, st, new_ops, what)
            # signed: the sign-correction sequence
            sh_ops, sh = splat(w - 1, type_, x.shape, loc)
            mk_ops, mk = splat(d - 1, type_, x.shape, loc)
            new_ops.extend(sh_ops)
            new_ops.extend(mk_ops)
            sign = tir.Op.binop("bit.ashr", x, sh, loc)
            corr = tir.Op.binop("bit.and", sign.result(), mk, loc)
            fixed = tir.Op.binop("arith.add", x, corr.result(), loc)
            new_ops.extend((sign, corr, fixed))
            if code == "arith.sdiv":
                ks_ops, ks = splat(k, type_, x.shape, loc)
                new_ops.extend(ks_ops)
                new_ops.append(tir.Op.binop("bit.ashr", fixed.result(),
                                            ks, loc))
                what = f"sdiv by {d} -> corrected shift"
            else:
                low = tir.Op.binop("bit.and", fixed.result(), mk, loc)
                new_ops.append(low)
                new_ops.append(tir.Op.binop("arith.sub", low.result(),
                                            corr.result(), loc))
                what = f"srem by {d} -> corrected mask"
            return swap(block, index, st, new_ops, what)

        def walk_block(block: tir.Block, base: Pos) -> None:
            i = 0
            while i < len(block.statements):
                st = block.statements[i]
                here = base + (_child_step("op", i),)
                if isinstance(st, tir.If):
                    walk_block(st.then, here + (_child_step("then", 0),))
                    walk_block(st.els, here + (_child_step("else", 0),))
                    i += 1
                    continue
                if isinstance(st, tir.Loop):
                    walk_block(st.body, here + (_child_step("body", 0),))
                    i += 1
                    continue
                if not isinstance(st, tir.Op) or not st.results:
                    i += 1
                    continue
                if st.op in ("arith.fdiv", "arith.frem", "arith.div_rn"):
                    c = _const_int(st.operands[1])
                    if c is not None and c > 0 and not (c & (c - 1)):
                        trace.record_decline(
                            "floating division by a power of two declined "
                            "(declared policy: the floating class is "
                            "never rewritten by strength reduction)")
                    i += 1
                    continue
                if st.op == "arith.mul" and st.operands[0].type.is_int():
                    i += rewrite_mul(block, i, st)
                    continue
                if st.op in ("arith.sdiv", "arith.udiv", "arith.srem",
                             "arith.urem") \
                        and st.operands[0].type.is_int():
                    i += rewrite_divrem(block, i, st)
                    continue
                i += 1

        for fn in module.functions:
            walk_block(fn.body, ())
        return changed[0]
