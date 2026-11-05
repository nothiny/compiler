"""Scalar (rank-0) lowering and the structured-control-flow core (T008),
extended by the memory-access-breadth and atomics core (T011).

Three responsibilities, one module (the declared outputs of T008/T011):

* the **scalar core**: constants, integer/bool arithmetic, the full
  comparison set, integer remainder, width conversions and scalar
  (rank-0) memory accesses.  Every refusal is a located diagnostic, never
  a silent approximation (MECH-DIAGNOSTIC-REFUSAL).
* the **control-flow core**: the structured TIR regions (``If`` with
  explicit join parameters, counted ``Loop`` and while-form ``Loop`` with
  carried values) lowered onto the MIR CFG -- block parameters are the
  joins, exactly the carrier the TIR verifier enforces
  (IR-SEMANTIC-FIDELITY).  A source variable re-bound on one path of a
  branch becomes a *new* value at the join (a fresh block parameter), never
  a lexical restore of its earlier binding.

Numeric policy (A003, standard RV64IMAFDC semantics): i32 values live
sign-extended in 64-bit registers; ``*w`` forms re-establish that
invariant; comparisons produce an i64 0/1 consumed directly by ``brc``.
Unsigned shifts compare/shift on the full register (``srl``/``srlw``),
signed division truncates toward zero, and division/remainder by zero
yields the RISC-V all-ones/dividend results (never a trap -- the corpus
never divides by zero, and the semantic is the target's declared one).

T011 additions (memory access breadth and atomics), all in this module:

* the **atomic core**: ``tl.atomic_add/max/min/xchg/and/or/xor/cas`` with
  ``sem``/``scope`` mapped onto the declared RVWMO model (A006) through
  :data:`ATOMIC_ORDERING` -- the aq/rl ordered-form bits on every AMO and
  explicit ``fence`` instructions where the scope requires them; a masked
  atomic performs no access at disabled positions (realized branchlessly:
  the disabled lane's address is redirected to a private workspace slot,
  so the out-of-range address is never presented to memory; the
  ``witness_drop_atomic_masks`` degraded build removes the redirection and
  must corrupt a poisoned guard region -- MECH-WITNESS-TEST); signedness
  is kept (amomax/amomin select their ``u`` forms from the pointee's own
  signedness); floating pointees have no AMO arithmetic on this target
  and are synthesized from the lr/sc pair on the raw bits (exact: one
  retry loop, the value computed through the vector float path).
* the **intra-program ordering**: ``tl.debug_barrier`` lowers to an
  explicit ``fence iorw, iorw`` (a program-order fence for the one worker
  thread that executes a program instance -- never the cross-worker
  stage barrier, which would desynchronize the pool when programs are
  strided across workers).
* the **wide-access proof**: ``tl.multiple_of``/``tl.max_contiguous``
  hints (carried by the TIR ``hint`` op) and the structural
  arange-plus-scalars offset form feed a declared contiguity/alignment
  proof; a proven access selects the unit-stride ``vle/vse`` form and an
  unproven one keeps the masked/indexed form (MECH-MASKED-VECTOR-ACCESS).
* **tl.gather** (register permute, ``vrgather.vv``) and **tl.interleave**
  (the standalone program-level lowering for the 2x-extent result the
  one-extent chunk region cannot host).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from a100c.ir import mir, tir

__all__ = ["ScalarLoweringError", "scalar_type_of", "lower_const",
           "float_const_bits", "convert_float_scalar",
           "lower_binop", "lower_cmp", "lower_not", "lower_rem",
           "refuse", "widen_to", "narrow_to",
           "scalar_load", "scalar_store",
           "begin_if", "IfFrame", "close_arm", "join_if",
           "begin_counted_loop", "begin_while_loop", "LoopFrame",
           "emit_axis_decomposition", "emit_grid_product",
           # T011: memory access breadth and atomics
           "ATOMIC_SEMS", "ATOMIC_SCOPES", "ATOMIC_ORDERING",
           "AtomicOrdering", "atomic_ordering", "atomic_repertoire_rows",
           "lower_atomic_rmw", "lower_atomic_cas", "emit_debug_barrier",
           "WideProof", "prove_wide_access", "lower_gather",
           "InterleaveOptions", "interleave_binding", "lower_interleave"]

#: binary TIR op -> MIR scalar opcode (integer only; scalar floating
#: arithmetic is refused -- floats appear as splatted vector constants and
#: as raw bits in GPRs)
_BIN_MAP = {
    "arith.add": "sadd", "arith.sub": "ssub", "arith.mul": "smul",
    "arith.sdiv": "sdiv", "arith.udiv": "sdivu",
    "bit.and": "sand", "bit.or": "sor", "bit.xor": "sxor",
    "bit.shl": "sshl", "bit.ashr": "ssra", "bit.lshr": "srl",
}


class ScalarLoweringError(Exception):
    def __init__(self, loc, construct: str, message: str):
        super().__init__(f"scalar lowering: {construct}: {message}"
                         + (f" (at {loc})" if loc else ""))
        self.loc = loc
        self.construct = construct
        self.message = message


def refuse(loc, construct: str, message: str):
    raise ScalarLoweringError(loc, construct, message)


def scalar_type_of(ty: tir.Type) -> mir.ScalarType:
    if ty.is_float():
        # raw bits in a GPR at the float width (used for splats)
        return mir.ScalarType(ty.width, signed=True, float=True)
    return mir.ScalarType(ty.width, signed=ty.signed)


def float_const_bits(value, ty: tir.Type, loc) -> int:
    """The raw IEEE bit pattern of one float constant at ``ty``'s width,
    under the declared constant rounding (round-to-nearest, ties-to-even).

    This is the single encoding every float-constant site shares: the
    constprop fold rounds a folded ``convert`` to the same value
    (``a100c/passes/constprop.py::_round_float``), and the runtime
    downcast (``vfncvt.f.f.w`` under the default FRM) is the same RTNE.
    A 16-bit target rounds the value in its OWN format:

    * ``fp16``: the IEEE half word (``<e``) -- a single fp64 -> fp16
      rounding; a value beyond the finite range is the IEEE infinity of
      its sign (the RTNE answer, exactly what the hardware convert
      produces), never a crash and never a guess;
    * ``bf16``: the RTNE bit rounding of the IEEE single word (the
      transport's own staging algorithm: round the low 16 bits, carry
      into the exponent, overflow past the finite range rounds to inf).
    """
    import struct
    value = float(value)
    if ty.width == 32:
        return struct.unpack("<I", struct.pack("<f", value))[0]
    if ty.width == 64:
        return struct.unpack("<Q", struct.pack("<d", value))[0]
    if ty.width == 16 and ty.name != "bf16":
        # the IEEE half word (fp16 -- the only 16-bit non-bf16 float the
        # declared surface has, under its default "f16" name too)
        try:
            return struct.unpack("<H", struct.pack("<e", value))[0]
        except OverflowError:
            return 0x7C00 if value > 0 else 0xFC00
    if ty.width == 16 and ty.name == "bf16":
        f32 = struct.unpack("<I", struct.pack("<f", value))[0]
        low = f32 & 0xFFFF
        rounded = f32 & 0xFFFF0000
        if low > 0x8000 or (low == 0x8000 and (rounded & 0x10000)):
            rounded += 0x10000
        if 0x7F7F_FFFF < rounded < 0x7F80_0000:
            rounded = 0x7F80_0000          # round up to +inf
        elif 0xFF7F_FFFF < rounded < 0xFF80_0000:
            rounded = 0xFF80_0000          # round up to -inf
        return (rounded >> 16) & 0xFFFF
    raise ScalarLoweringError(
        loc, "const", f"float width {ty.width} is not in the scalar core")


def lower_const(ctx, value, ty: tir.Type, loc) -> mir.VReg:
    """A scalar constant: raw bits (floats via their IEEE bit pattern)."""
    if ty.is_float():
        bits = float_const_bits(value, ty, loc)
    elif ty.is_bool():
        bits = 1 if value else 0
    elif ty.is_int():
        bits = int(value) & ((1 << ty.width) - 1)
        if ty.signed and bits >= (1 << (ty.width - 1)):
            bits -= (1 << ty.width)
    else:
        raise ScalarLoweringError(
            loc, "const", f"constant of type {ty!r} is not a scalar constant")
    return ctx.const(bits, scalar_type_of(ty), loc)


# ---------------------------------------------------------------------------
# The record/binding conversion (the scalar record width and the kernel's
# declared scalar type are independent by construction)
# ---------------------------------------------------------------------------

def _vsetvli1(ctx, sew: int, lmul: int, loc) -> None:
    """One vsetvli at avl=1 (the scalar conversion's own lane count)."""
    avl = ctx.const(1, mir.I32, loc)
    ctx.emit(mir.MOp(
        "vsetvli", [avl], [ctx.vreg(mir.I32, hint="bvr", loc=loc)],
        attrs={"sew": sew, "lmul": lmul, "policy": "ta,ma"}, loc=loc))


def convert_float_scalar(ctx, reg: mir.VReg, from_width: int,
                         ty: tir.Type, loc) -> mir.VReg:
    """Convert one raw-bits float scalar from its RECORD width to the
    kernel's DECLARED scalar type (the binding-side read conversion).

    The bundle record holds the host value at its own width -- the packer
    writes the Python/numpy scalar as packed, so a Python float argument
    is a float64 record while the kernel's signature declares the
    argument an fp32 scalar (the pinned mangle_type rule).  The two
    widths are independent by construction, so the binding CONVERTS on
    read under the declared semantics instead of refusing on the
    disagreement:

    * narrowing (record wider): ``vfncvt.f.f.w`` under the default FRM --
      round-to-nearest-even, the pinned downcast rounding;
    * widening (record narrower): ``vfwcvt.f.f.v`` -- exact;
    both stepwise through the IEEE binary widths (64 <-> 32 <-> 16), one
    lane: splat the record's raw bits, convert, extract lane 0 (the same
    splat-convert-extract form the scalar convert path uses -- the scalar
    core holds floats as raw bits in GPRs by design).

    Only the IEEE binary widths the corpus dtype surface declares take
    this path.  A bf16 *record* cannot arise (numpy has no bfloat16
    scalar, so the packer never writes one); a bf16 declared scalar type
    cannot arise from ``scalar_arg_type`` either -- both are refused
    located rather than guessed.
    """
    if not ty.is_float():
        refuse(loc, "scalar-binding",
               f"the record conversion converts float scalars; {ty!r} is "
               "not a float type")
    to_width = ty.width
    if ty.name == "bf16":
        refuse(loc, "scalar-binding",
               "a bfloat16 scalar parameter cannot arise from the declared "
               "argument surface (numpy has no bfloat16 scalar and a Python "
               "float binds as fp32); refusing located rather than guessing "
               "a conversion")
    if from_width not in (16, 32, 64) or to_width not in (16, 32, 64):
        refuse(loc, "scalar-binding",
               f"float scalar record width {from_width} -> {to_width} is "
               "outside the IEEE binary widths the dtype surface declares "
               "(16/32/64)")
    if from_width == to_width:
        return reg
    # splat the record's raw bits at the record's own width (the region
    # is opened explicitly: the entry block has none)
    _vsetvli1(ctx, from_width, 1, loc)
    vec = ctx.emit(mir.MOp(
        "s2v", [reg],
        [ctx.vreg(mir.VectorType(from_width, 1, "float"),
                  hint="rbs", loc=loc)], loc=loc))
    width = from_width
    while width > to_width:
        # one narrowing step: the source re-viewed at the DOUBLE-LMUL
        # group the instruction actually reads (the probed no-overlap
        # form), the destination at half SEW
        src2 = ctx.emit(mir.MOp(
            "vmovv", [vec],
            [ctx.vreg(mir.VectorType(width, 2, "float"),
                      hint="rbw", loc=loc)], loc=loc))
        _vsetvli1(ctx, width // 2, 1, loc)
        vec = ctx.emit(mir.MOp(
            "vfncvt", [src2],
            [ctx.vreg(mir.VectorType(width // 2, 1, "float"),
                      hint="rbn", loc=loc)],
            attrs={"op": "ff"}, loc=loc))
        width //= 2
    while width < to_width:
        # one widening step: the source at the region, the destination
        # doubling SEW and LMUL (the vfwcvt convention), then the group
        # re-viewed down to LMUL 1 for the next step / the extract
        _vsetvli1(ctx, width, 1, loc)
        wide = ctx.emit(mir.MOp(
            "vfwcvt", [vec],
            [ctx.vreg(mir.VectorType(width * 2, 2, "float"),
                      hint="rbw", loc=loc)],
            attrs={"op": "ff"}, loc=loc))
        width *= 2
        _vsetvli1(ctx, width, 1, loc)
        vec = ctx.emit(mir.MOp(
            "vmovv", [wide],
            [ctx.vreg(mir.VectorType(width, 1, "float"),
                      hint="rbv", loc=loc)], loc=loc))
    return ctx.emit(mir.MOp(
        "vextract", [vec],
        [ctx.vreg(scalar_type_of(ty), hint="rbx", loc=loc)], loc=loc))


def lower_binop(ctx, op: tir.Op, lhs: mir.VReg, rhs: mir.VReg,
                loc) -> mir.VReg:
    code = _BIN_MAP.get(op.op)
    if code is None:
        if op.op in ("arith.srem", "arith.urem"):
            return lower_rem(ctx, op, lhs, rhs, loc,
                             signed=op.op == "arith.srem")
        refuse(loc, op.op,
               f"scalar binary op is not implemented by the scalar core "
               f"({sorted(_BIN_MAP)})")
    if lhs.type != rhs.type:
        refuse(loc, op.op,
               f"scalar operand types differ: {lhs.type!r} vs {rhs.type!r} "
               "(the frontend inserts explicit converts)")
    if lhs.type.float:
        refuse(loc, op.op,
               "scalar floating arithmetic is not in the scalar core (float "
               "values appear only as splatted vector constants)")
    return ctx.emit(mir.MOp(code, [lhs, rhs],
                            [ctx.vreg(lhs.type, hint="s", loc=loc)],
                            loc=loc))


def lower_rem(ctx, op: tir.Op, lhs: mir.VReg, rhs: mir.VReg, loc,
              signed: bool = True) -> mir.VReg:
    """Integer remainder: ``a - (a / b) * b`` (C truncation semantics).

    The signed form uses ``sdiv`` (truncating, like C ``%``); the unsigned
    form ``sdivu``.  No repertoire entry is needed -- the sequence uses the
    declared div/mul/sub instructions only.
    """
    if lhs.type != rhs.type or lhs.type.float:
        refuse(loc, op.op if op is not None else "rem",
               f"scalar remainder on {lhs.type!r}/{rhs.type!r} is not in "
               "the scalar core")
    div = ctx.emit(mir.MOp("sdiv" if signed else "sdivu", [lhs, rhs],
                           [ctx.vreg(lhs.type, hint="q", loc=loc)], loc=loc))
    prod = ctx.emit(mir.MOp("smul", [div, rhs],
                            [ctx.vreg(lhs.type, hint="r", loc=loc)], loc=loc))
    return ctx.emit(mir.MOp("ssub", [lhs, prod],
                            [ctx.vreg(lhs.type, hint="rem", loc=loc)],
                            loc=loc))


#: the full comparison set, realized with the declared repertoire rows only
#: (slt/sltu + sub/xor); every comparison produces an i64 0/1.  Ordering
#: predicates select their unsigned form when the operands are unsigned
#: (A003: signedness is a property of the compared type, never of the
#: predicate); equality is width-exact through the subtract-low-bits form.
def lower_cmp(ctx, op: tir.Op, lhs: mir.VReg, rhs: mir.VReg,
              loc) -> mir.VReg:
    if lhs.type != rhs.type:
        refuse(loc, op.op,
               f"scalar comparison on {lhs.type!r}/{rhs.type!r}: operand "
               "types differ (the frontend inserts explicit converts)")
    if lhs.type.float:
        refuse(loc, op.op,
               f"scalar comparison on {lhs.type!r} is not in the scalar "
               "core (float conditions are not exercised by the corpus "
               "control-flow families)")
    pred = op.op.split(".", 1)[1]
    one = ctx.const(1, mir.I64, loc)
    ordered = "slt" if lhs.type.signed else "sltu"

    def boolean(opcode: str, a: mir.VReg, b: mir.VReg) -> mir.VReg:
        return ctx.emit(mir.MOp(opcode, [a, b],
                                [ctx.vreg(mir.I64, hint="b", loc=loc)],
                                loc=loc))

    if pred == "lt":
        return boolean(ordered, lhs, rhs)
    if pred == "gt":
        return boolean(ordered, rhs, lhs)
    if pred == "ge":                      # !(lhs < rhs)
        lt = boolean(ordered, lhs, rhs)
        return ctx.emit(mir.MOp("sxor", [lt, one],
                                [ctx.vreg(mir.I64, hint="b", loc=loc)],
                                loc=loc))
    if pred == "le":                      # !(rhs < lhs)
        gt = boolean(ordered, rhs, lhs)
        return ctx.emit(mir.MOp("sxor", [gt, one],
                                [ctx.vreg(mir.I64, hint="b", loc=loc)],
                                loc=loc))
    if pred == "eq":                      # (lhs - rhs) == 0, unsigned < 1
        diff = ctx.emit(mir.MOp("ssub", [lhs, rhs],
                                [ctx.vreg(lhs.type, hint="d", loc=loc)],
                                loc=loc))
        return boolean("sltu", diff, ctx.const(1, diff.type, loc))
    if pred == "ne":
        diff = ctx.emit(mir.MOp("ssub", [lhs, rhs],
                                [ctx.vreg(lhs.type, hint="d", loc=loc)],
                                loc=loc))
        eq = boolean("sltu", diff, ctx.const(1, diff.type, loc))
        return ctx.emit(mir.MOp("sxor", [eq, one],
                                [ctx.vreg(mir.I64, hint="b", loc=loc)],
                                loc=loc))
    refuse(loc, op.op, f"comparison predicate {pred!r} is not in the "
           "scalar core")


def lower_not(ctx, operand: mir.VReg, loc) -> mir.VReg:
    """Scalar logical not on an i64 0/1 (or i1-held) value."""
    if operand.type.float:
        refuse(loc, "logical.not", "scalar float logical-not is not in the "
               "scalar core")
    one = ctx.const(1, mir.I64, loc)
    return ctx.emit(mir.MOp("sxor", [operand, one],
                            [ctx.vreg(mir.I64, hint="nb", loc=loc)],
                            loc=loc))


# ---------------------------------------------------------------------------
# Width conversions (i32 values live sign-extended; the invariants)
# ---------------------------------------------------------------------------

def widen_to(ctx, reg: mir.VReg, width: int, loc,
             unsigned: Optional[bool] = None) -> mir.VReg:
    """Widen an i32 scalar to i64 (the register already holds the extended
    value; ``smove`` realizes the view).  Other widths are refused.

    ``unsigned`` (T013): the widened view's signedness -- the philox key
    path widens an i32 seed to the UINT64 view, and the scalar binop
    type rules must see matching operand types."""
    if reg.type.width == width:
        return reg
    if reg.type.width == 32 and width == 64 and not reg.type.float:
        signed = True if unsigned is None else (not unsigned)
        sty = mir.ScalarType(64, signed=signed)
        return ctx.emit(mir.MOp(
            "smove", [reg],
            [ctx.vreg(sty, hint="w", loc=loc)], loc=loc))
    refuse(loc, "width",
           f"scalar widening {reg.type.width} -> {width} is not in the "
           "scalar core (32 -> 64 only)")


def narrow_to(ctx, reg: mir.VReg, width: int, loc) -> mir.VReg:
    """Narrow an i64 scalar to i32 (``strunc``; legalised to ``swext``)."""
    if reg.type.width == width:
        return reg
    if reg.type.width == 64 and width == 32 and not reg.type.float:
        return ctx.emit(mir.MOp(
            "strunc", [reg],
            [ctx.vreg(mir.I32, hint="n", loc=loc)], loc=loc))
    refuse(loc, "width",
           f"scalar narrowing {reg.type.width} -> {width} is not in the "
           "scalar core (64 -> 32 only)")


def convert_width(ctx, reg: mir.VReg, width: int, loc) -> mir.VReg:
    if reg.type.width < width:
        return widen_to(ctx, reg, width, loc)
    if reg.type.width > width:
        return narrow_to(ctx, reg, width, loc)
    return reg


# ---------------------------------------------------------------------------
# Scalar memory (rank-0 loads/stores over ptradd trees)
# ---------------------------------------------------------------------------

def _scalar_address(ctx, base_reg: mir.VReg, offset_reg: mir.VReg,
                    pointee: tir.Type, loc) -> mir.VReg:
    """base + offset*elemsize, one whole-tree expression in i64."""
    elemsize = pointee.bitwidth() // 8
    off64 = convert_width(ctx, offset_reg, 64, loc) \
        if offset_reg.type.width != 64 else offset_reg
    if elemsize != 1:
        scaled = ctx.emit(mir.MOp(
            "smul", [off64, ctx.const(elemsize, mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="sa", loc=loc)], loc=loc))
    else:
        scaled = off64
    return ctx.emit(mir.MOp(
        "sadd", [base_reg, scaled],
        [ctx.vreg(mir.I64, hint="ad", loc=loc)], loc=loc))


def scalar_load(ctx, base_reg: mir.VReg, offset_reg: mir.VReg,
                pointee: tir.Type, loc) -> mir.VReg:
    """One rank-0 load: address = base + offset*elemsize (i64), then a
    width-exact scalar load at displacement 0."""
    if pointee.is_bool():
        refuse(loc, "tl.load",
               "scalar bool loads are not in the scalar core (no i1 "
               "storage form)")
    width = pointee.bitwidth()
    if width not in (8, 16, 32, 64):
        refuse(loc, "tl.load",
               f"scalar load width {width} is not in the scalar core")
    addr = _scalar_address(ctx, base_reg, offset_reg, pointee, loc)
    mtype = mir.ScalarType(width, signed=True, float=pointee.is_float())
    return ctx.emit(mir.MOp(
        "sload", [addr], [ctx.vreg(mtype, hint="sl", loc=loc)],
        attrs={"width": width, "offset": 0,
               "ext": "sext" if pointee.is_int_signed() or pointee.is_float()
               else "zext"},
        loc=loc))


def scalar_store(ctx, base_reg: mir.VReg, offset_reg: mir.VReg,
                 value_reg: mir.VReg, pointee: tir.Type, loc) -> None:
    if pointee.is_bool():
        refuse(loc, "tl.store",
               "scalar bool stores are not in the scalar core")
    width = pointee.bitwidth()
    if width not in (8, 16, 32, 64):
        refuse(loc, "tl.store",
               f"scalar store width {width} is not in the scalar core")
    addr = _scalar_address(ctx, base_reg, offset_reg, pointee, loc)
    val = convert_width(ctx, value_reg, width, loc) \
        if value_reg.type.width != width and not value_reg.type.float \
        else value_reg
    ctx.emit0(mir.MOp("sstore", [addr, val], [],
                      attrs={"width": width, "offset": 0}, loc=loc))


# ---------------------------------------------------------------------------
# Structured control flow -> MIR CFG (the T008 core)
# ---------------------------------------------------------------------------

class IfFrame:
    """An open two-arm region: the arms are being lowered; the join block
    is created by :func:`join_if` from the arms' final values."""

    __slots__ = ("tag", "then_block", "else_block", "loc")

    def __init__(self, tag: str, then_block: mir.Block, else_block: mir.Block,
                 loc):
        self.tag = tag
        self.then_block = then_block
        self.else_block = else_block
        self.loc = loc


def begin_if(ctx, cond: mir.VReg, loc, tag: str) -> IfFrame:
    """Terminate the current block on ``cond`` and open the two arms.

    ``cond`` is the i64 0/1 a comparison produces; ``brc`` tests it against
    zero.  Arms are lowered into fresh blocks; each must be closed with
    :func:`close_arm`.
    """
    then_b = ctx.add_block(f"{tag}.then", [], loc)
    else_b = ctx.add_block(f"{tag}.else", [], loc)
    ctx.emit0(mir.MOp("brc", [cond], [],
                      attrs={"true_target": then_b.name,
                             "true_args": [],
                             "false_target": else_b.name,
                             "false_args": []}, loc=loc))
    return IfFrame(tag, then_b, else_b, loc)


def close_arm(ctx, frame: IfFrame, join_name: str,
              values: Sequence[mir.VReg]) -> None:
    """Close the *current* arm with a branch to the (future) join block,
    passing the arm's final value of every join name, in order."""
    ctx.emit0(mir.MOp("br", [], [],
                      attrs={"target": join_name, "args": list(values)},
                      loc=frame.loc))


def join_if(ctx, frame: IfFrame, join_name: str,
            arm_values: Sequence[Sequence[mir.VReg]], loc) -> List[mir.VReg]:
    """Create the join block: one block parameter per join name.

    ``arm_values`` holds, per arm, the final value of each join name (the
    then arm first).  The parameters ARE the joins -- fresh values, never a
    lexical restore of an arm's or an outer binding -- which is exactly the
    carrier the TIR verifier demands for values re-bound inside a region.
    """
    if len(arm_values) != 2:
        raise ScalarLoweringError(loc, "if",
                                  "an if has exactly two arms")
    for then_v, else_v in zip(arm_values[0], arm_values[1]):
        if then_v.type != else_v.type:
            raise ScalarLoweringError(
                loc, "if",
                f"join values differ in type: {then_v.type!r} vs "
                f"{else_v.type!r} (the frontend must unify them)")
    params = [ctx.vreg(v.type, hint=f"j{frame.tag}", loc=loc)
              for v in arm_values[0]]
    ctx.add_block(join_name, params, loc)
    return params


class LoopFrame:
    """An open loop: head (test), body and exit blocks with the carried
    values as head/exit block parameters (the loop-carried joins)."""

    __slots__ = ("tag", "head", "body", "exit", "params", "loc")

    def __init__(self, tag: str, head: mir.Block, body: mir.Block,
                 exit_b: mir.Block, params: List[mir.VReg], loc):
        self.tag = tag
        self.head = head
        self.body = body
        self.exit = exit_b
        self.params = params
        self.loc = loc


def begin_counted_loop(ctx, lower: mir.VReg, upper: mir.VReg,
                       carried_inits: Sequence[mir.VReg], loc,
                       tag: str) -> LoopFrame:
    """The counted range form:

    ``head(i, carried...) { c = i <u upper; brc c -> body, exit }``

    The induction value ``i`` is ``params[0]``; the body is entered with
    the current carried values and closed by the caller with the back-edge
    branch to the head.
    """
    width = lower.type.width
    upper_n = convert_width(ctx, upper, width, loc)
    head_params = [ctx.vreg(lower.type, hint=f"i.{tag}", loc=loc)]
    head_params += [ctx.vreg(v.type, hint=f"c{tag}", loc=loc)
                    for v in carried_inits]
    head = ctx.add_block(f"{tag}.head", head_params, loc)
    body = ctx.add_block(f"{tag}.body", list(head_params), loc)
    exit_params = [ctx.vreg(lower.type, hint=f"i.{tag}x", loc=loc)]
    exit_params += [ctx.vreg(v.type, hint=f"c{tag}x", loc=loc)
                    for v in carried_inits]
    exit_b = ctx.add_block(f"{tag}.exit", exit_params, loc)
    ctx.emit0(mir.MOp("br", [], [],
                      attrs={"target": head.name,
                             "args": [lower] + list(carried_inits)}, loc=loc))
    ctx.switch(head)
    # non-negative induction over a non-negative bound: slt == sltu here,
    # and slt keeps the signed forms of pathological bounds safe
    cont = ctx.emit(mir.MOp("slt", [head_params[0], upper_n],
                            [ctx.vreg(mir.I64, hint="go", loc=loc)],
                            loc=loc))
    ctx.emit0(mir.MOp("brc", [cont], [],
                      attrs={"true_target": body.name,
                             "true_args": list(head_params),
                             "false_target": exit_b.name,
                             "false_args": list(head_params)}, loc=loc))
    ctx.switch(body)
    return LoopFrame(tag, head, body, exit_b, head_params, loc)


def begin_while_loop(ctx, cond_init: mir.VReg,
                     carried_inits: Sequence[mir.VReg], loc,
                     tag: str) -> LoopFrame:
    """The while form:

    ``head(c, carried...) { brc c -> body, exit }``

    ``c`` (params[0]) is the condition value carried across iterations; the
    body re-evaluates it before the back edge (the frontend emits the
    re-evaluation as the body's final statements).
    """
    head_params = [ctx.vreg(cond_init.type, hint=f"w.{tag}", loc=loc)]
    head_params += [ctx.vreg(v.type, hint=f"c{tag}", loc=loc)
                    for v in carried_inits]
    head = ctx.add_block(f"{tag}.head", head_params, loc)
    body = ctx.add_block(f"{tag}.body", list(head_params), loc)
    exit_params = [ctx.vreg(cond_init.type, hint=f"w.{tag}x", loc=loc)]
    exit_params += [ctx.vreg(v.type, hint=f"c{tag}x", loc=loc)
                    for v in carried_inits]
    exit_b = ctx.add_block(f"{tag}.exit", exit_params, loc)
    ctx.emit0(mir.MOp("br", [], [],
                      attrs={"target": head.name,
                             "args": [cond_init] + list(carried_inits)},
                      loc=loc))
    ctx.switch(head)
    ctx.emit0(mir.MOp("brc", [head_params[0]], [],
                      attrs={"true_target": body.name,
                             "true_args": list(head_params),
                             "false_target": exit_b.name,
                             "false_args": list(head_params)}, loc=loc))
    ctx.switch(body)
    return LoopFrame(tag, head, body, exit_b, head_params, loc)


def close_loop(ctx, frame: LoopFrame,
               back_edge_values: Sequence[mir.VReg]) -> None:
    """The back edge: body -> head with the new induction/cond value and
    the body's final carried values."""
    if len(back_edge_values) != len(frame.params):
        raise ScalarLoweringError(
            frame.loc, "loop",
            f"back edge passes {len(back_edge_values)} value(s); the head "
            f"takes {len(frame.params)}")
    for new, param in zip(back_edge_values, frame.params):
        if new.type != param.type:
            raise ScalarLoweringError(
                frame.loc, "loop",
                f"back-edge value {new.type!r} does not match head param "
                f"{param.type!r} (a carried value changed width in the body)")
    ctx.emit0(mir.MOp("br", [], [],
                      attrs={"target": frame.head.name,
                             "args": list(back_edge_values)}, loc=frame.loc))


# ---------------------------------------------------------------------------
# Grid decomposition (multi-axis program_id; AM0287: the axis-k divisor is
# the product of the extents of axes 0..k-1 -- axis 0 varies fastest)
# ---------------------------------------------------------------------------

def emit_axis_decomposition(ctx, pid: mir.VReg, extents: Sequence[mir.VReg],
                            loc) -> List[mir.VReg]:
    """Decompose the linear worker-range program index into per-axis
    program ids: ``pid_k = (pid / stride_k) % extent_k`` with
    ``stride_k = prod(extents[0..k-1])``.

    All arithmetic is i64 on non-negative values (division is exact and
    the remainder equals the modulus).
    """
    pids: List[mir.VReg] = []
    stride = ctx.const(1, mir.I64, loc)
    for k, extent in enumerate(extents):
        if k == 0:
            axis = pid
        else:
            axis = ctx.emit(mir.MOp(
                "sdivu", [pid, stride],
                [ctx.vreg(mir.I64, hint="gq", loc=loc)], loc=loc))
        # axis %= extent  (a - (a/e)*e, exact on non-negative values)
        q = ctx.emit(mir.MOp(
            "sdivu", [axis, extent],
            [ctx.vreg(mir.I64, hint="gq", loc=loc)], loc=loc))
        prod = ctx.emit(mir.MOp(
            "smul", [q, extent],
            [ctx.vreg(mir.I64, hint="gr", loc=loc)], loc=loc))
        axis = ctx.emit(mir.MOp(
            "ssub", [axis, prod],
            [ctx.vreg(mir.I64, hint="gpid", loc=loc)], loc=loc))
        pids.append(axis)
        stride = ctx.emit(mir.MOp(
            "smul", [stride, extent],
            [ctx.vreg(mir.I64, hint="gs", loc=loc)], loc=loc))
    return pids


def emit_grid_product(ctx, extents: Sequence[mir.VReg],
                      loc) -> mir.VReg:
    """The linear program count: prod(extents), in i64."""
    total = ctx.const(1, mir.I64, loc)
    for extent in extents:
        total = ctx.emit(mir.MOp(
            "smul", [total, extent],
            [ctx.vreg(mir.I64, hint="gn", loc=loc)], loc=loc))
    return total


# ===========================================================================
# Memory access breadth and atomics (T011)
# ===========================================================================
#
# The RVWMO model this section implements is the declared one (A006:
# memory between A100 harts is RVWMO with explicit synchronization; the
# pinned execution endpoint is QEMU user mode, where all worker threads
# share one address space and the AMO/lr/sc/fence instructions are the
# ordering primitives).  The mapping from the source ``sem``/``scope``
# parameters to emitted forms is DATA -- :data:`ATOMIC_ORDERING` -- never
# a per-call guess, and every emitted atomic carries the ordered form its
# case's scope requires.

#: the declared sem values (Triton 3.8 ``AtomicSem``) and scopes
ATOMIC_SEMS = ("relaxed", "acquire", "release", "acq_rel")
ATOMIC_SCOPES = ("gpu", "sys", "cta")


@dataclass(frozen=True)
class AtomicOrdering:
    """The emitted ordering of one atomic, per the declared RVWMO mapping.

    ``aq``/``rl`` select the AMO's ordered-form suffix (.aq / .rl /
    .aqrl); ``lead``/``trail`` are explicit ``fence`` instructions the
    scope requires around the atomic sequence (None when the aq/rl bits
    are sufficient).
    """

    aq: bool
    rl: bool
    lead: Optional[Tuple[str, str]] = None
    trail: Optional[Tuple[str, str]] = None

    def describe(self) -> dict:
        return {"aq": self.aq, "rl": self.rl,
                "lead": list(self.lead) if self.lead else None,
                "trail": list(self.trail) if self.trail else None}


#: the declared sem x scope -> RVWMO form table (A006):
#:
#: * sem selects the aq/rl bits exactly as the RISC-V privileged spec
#:   prescribes for atomic RMWs (acquire -> .aq, release -> .rl,
#:   acq_rel -> .aqrl, relaxed -> the plain form);
#: * scope ``cta`` orders one program instance -- it executes on one
#:   worker thread, so the aq/rl bits (which order the issuing hart's
#:   memory operations) already cover the declared scope;
#: * scope ``gpu`` covers the device's harts: under the declared model
#:   they share one RVWMO domain with the memory in question, so the
#:   aq/rl bits are again the ordered form the scope requires;
#: * scope ``sys`` additionally brackets the sequence with the full
#:   ``fence iorw, iorw`` (the strongest declared form; stronger ordering
#:   than requested is always value-safe).
ATOMIC_ORDERING: Dict[Tuple[str, str], AtomicOrdering] = {
    (sem, scope): AtomicOrdering(
        aq=sem in ("acquire", "acq_rel"),
        rl=sem in ("release", "acq_rel"),
        lead=("iorw", "iorw") if scope == "sys" else None,
        trail=("iorw", "iorw") if scope == "sys" else None,
    )
    for sem in ATOMIC_SEMS for scope in ATOMIC_SCOPES
}


def atomic_ordering(sem: str, scope: str) -> AtomicOrdering:
    """The declared ordering for one (sem, scope); unknown values refuse."""
    try:
        return ATOMIC_ORDERING[(sem, scope)]
    except KeyError:
        refuse(None, "tl.atomic",
               f"sem={sem!r}/scope={scope!r} is not in the declared RVWMO "
               f"mapping (sems {ATOMIC_SEMS}, scopes {ATOMIC_SCOPES})")


# ---------------------------------------------------------------------------
# The atomic repertoire rows (registered as data on import)
# ---------------------------------------------------------------------------

_AMO_OPS = ("add", "xchg", "and", "or", "xor")     # signedness-free forms
_AMO_MINMAX = ("max", "min")                        # signedness-selecting
_AMO_SFX = {False: "", True: "aq"}                  # placeholder, see below


def _amo_suffix(aq: bool, rl: bool) -> str:
    if aq and rl:
        return ".aqrl"
    if aq:
        return ".aq"
    if rl:
        return ".rl"
    return ""


def atomic_repertoire_rows() -> List["object"]:
    """The atomic/fence/permute rows of the repertoire, as data
    (TGT-INSTRUCTION-REPERTOIRE; adding these is a table edit).

    Rows are additive: no existing row shares these opcodes, so a
    selection that lowers no atomic construct cannot change.  Evidence:
    the AMO/lr/sc/fence instructions are RV64IMAFDC (F002) and execute
    under the pinned QEMU endpoint (probed by the T011 executed tests).
    """
    from a100c.backend.repertoire import InstructionEntry
    rows: List[InstructionEntry] = []
    ev = "RV64IMAFDC (F002); executed under the pinned QEMU (T011)"
    for width, sfx in ((32, "w"), (64, "d")):
        for aq in (False, True):
            for rl in (False, True):
                o = _amo_suffix(aq, rl)
                for op in _AMO_OPS:
                    mn = "amoswap" if op == "xchg" else f"amo{op}"
                    rows.append(InstructionEntry(
                        f"{mn}.{sfx}{o}", "satomic",
                        (("op", op), ("width", width), ("aq", aq),
                         ("rl", rl), ("unsigned", False)),
                        f"{mn}.{sfx}{o} {{rd}}, {{rs2}}, ({{rs1}})",
                        evidence=ev,
                        notes="the RVWMO ordered form (aq/rl bits) the "
                              "declared sem/scope mapping selects"))
                for op in _AMO_MINMAX:
                    for unsigned in (False, True):
                        u = "u" if unsigned else ""
                        rows.append(InstructionEntry(
                            f"amo{op}{u}.{sfx}{o}", "satomic",
                            (("op", op), ("width", width), ("aq", aq),
                             ("rl", rl), ("unsigned", unsigned)),
                            f"amo{op}{u}.{sfx}{o} {{rd}}, {{rs2}}, "
                            f"({{rs1}})",
                            evidence=ev,
                            notes="min/max keep the pointee's signedness "
                                  "(the u forms are the unsigned rows)"))
                rows.append(InstructionEntry(
                    f"lr.{sfx}{o}", "slr",
                    (("width", width), ("aq", aq), ("rl", rl)),
                    f"lr.{sfx}{o} {{rd}}, ({{rs1}})",
                    evidence=ev,
                    notes="load-reserved, the CAS/synthesis half"))
                rows.append(InstructionEntry(
                    f"sc.{sfx}{o}", "ssc",
                    (("width", width), ("aq", aq), ("rl", rl)),
                    f"sc.{sfx}{o} {{rd}}, {{rs2}}, ({{rs1}})",
                    evidence=ev,
                    notes="store-conditional (rd=0 on success)"))
    # the explicit fences of the declared mapping (scope sys, and the
    # intra-program debug_barrier ordering)
    for pred, succ, note in (
            ("iorw", "iorw", "the full fence: scope=sys bracket and the "
                             "intra-program debug_barrier ordering"),
            ("r", "rw", "acquire-fence form (declared, currently unused "
                        "by the mapping)"),
            ("rw", "w", "release-fence form (declared, currently unused "
                        "by the mapping)")):
        rows.append(InstructionEntry(
            f"fence {pred}, {succ}".replace(" ", "_"), "sfence",
            (("pred", pred), ("succ", succ)),
            f"fence {pred}, {succ}", evidence=ev, notes=note))
    # the register permute (tl.gather) and the lane slide the per-lane
    # atomic loop extracts with
    rows.append(InstructionEntry(
        "vrgather.vv", "vrgather", (),
        "vrgather.vv {vd}, {vs2}, {vs1}",
        evidence="RVV 1.0 VLEN=1024 (F006/F026)",
        notes="vd[i] = vs2[vs1[i]] (out-of-range indices give 0); the "
              "tl.gather register permute at the region's SEW"))
    rows.append(InstructionEntry(
        "vslidedown.vi", "vslidedn", (),
        "vslidedown.vi {vd}, {vs2}, 1",
        evidence="RVV 1.0 (F006/F026)",
        notes="slide down by one lane: the per-lane extraction step of "
              "the block atomic loop"))
    for sew in (8, 16, 32, 64):
        rows.append(InstructionEntry(
            f"vle{sew}.v", "vunit_load", (("sew", sew),),
            f"vle{sew}.v {{vd}}, 0({{rs1}})",
            evidence="RVV 1.0 (F006/F026)",
            notes="the unit-stride load a proven-contiguous access "
                  "selects (the masked form appends v0.t; inactive lanes "
                  "perform no access)"))
        rows.append(InstructionEntry(
            f"vse{sew}.v", "vunit_store", (("sew", sew),),
            f"vse{sew}.v {{rs2}}, 0({{rs1}})",
            evidence="RVV 1.0 (F006/F026)",
            notes="the unit-stride store a proven-contiguous access "
                  "selects (the masked form appends v0.t)"))
    return rows


def _register_atomic_rows() -> None:
    """Register the atomic rows into the default repertoire (additive)."""
    from a100c.backend.repertoire import DEFAULT_REPERTOIRE
    have = {(e.opcode, e.mnemonic) for e in DEFAULT_REPERTOIRE.entries}
    for row in atomic_repertoire_rows():
        if (row.opcode, row.mnemonic) not in have:
            DEFAULT_REPERTOIRE.add(row)


_register_atomic_rows()


# ---------------------------------------------------------------------------
# The atomic lowering (TIR atomic_rmw / atomic_cas -> MIR)
# ---------------------------------------------------------------------------

#: workspace byte offsets of the atomic scratch region (relative to the
#: private workspace base): [result_base .. + vl*esz) holds the per-lane
#: old values (reloaded as the block result), then the 8-byte redirect
#: slot disabled lanes' atomics are redirected to.
def _atomic_ws_layout(sl) -> Tuple[int, int, int]:
    base = getattr(sl, "_atomic_ws_offset", 0)
    esz = getattr(sl, "_atomic_max_esz", 4)
    vl = sl._vl
    return base, base + vl * esz, vl * esz


def emit_debug_barrier(ctx, loc) -> None:
    """``tl.debug_barrier`` as intra-program ordering.

    A program instance executes on ONE worker thread; ordering its own
    memory operations requires a program-order fence, not the
    cross-worker stage barrier (programs are strided across workers, so
    per-program barrier calls would desynchronize the pool).  The fence
    is real: no memory operation crosses it in either direction.
    """
    ctx.emit0(mir.MOp("sfence", [], [],
                      attrs={"pred": "iorw", "succ": "iorw"}, loc=loc))


def _emit_fence(ctx, form: Optional[Tuple[str, str]], loc) -> None:
    if form is None:
        return
    ctx.emit0(mir.MOp("sfence", [], [],
                      attrs={"pred": form[0], "succ": form[1]}, loc=loc))


def _atomic_value_reg(sl, ctx, value, pointee: tir.Type, width: int,
                      loc) -> mir.VReg:
    """The atomic's value operand at the AMO width (32/64)."""
    reg = sl._need(value, loc)
    if reg.type.float:
        if reg.type.width != width:
            refuse(loc, "tl.atomic",
                   f"floating pointee of width {reg.type.width} is not in "
                   "the atomic slice (fp32 only; the AMO families are "
                   ".w/.d and the fp synthesis runs at 32 bits)")
        return reg
    if reg.type.width == width:
        return reg
    if reg.type.width < width:
        return widen_to(ctx, reg, width, loc)
    return narrow_to(ctx, reg, width, loc)


def _scalar_atomic_int(ctx, addr: mir.VReg, val: mir.VReg, op_kind: str,
                       pointee: tir.Type, loc,
                       ordering: "AtomicOrdering" = None) -> mir.VReg:
    """One integer AMO; the old value comes back at the pointee width.
    The declared ordering selects the aq/rl bits (the RVWMO ordered form
    the case's sem/scope requires)."""
    width = pointee.bitwidth()
    mtype = mir.ScalarType(width, signed=pointee.is_int_signed())
    o = ordering or ATOMIC_ORDERING[("relaxed", "gpu")]
    return ctx.emit(mir.MOp(
        "satomic", [addr, val],
        [ctx.vreg(mtype, hint="aold", loc=loc)],
        attrs={"op": op_kind, "width": width, "aq": o.aq, "rl": o.rl,
               "unsigned": not pointee.is_int_signed(),
               "float": False}, loc=loc))


def _scalar_fp_compute(sl, ctx, old_f: mir.VReg, val_f: mir.VReg,
                       op_kind: str, width: int, loc) -> mir.VReg:
    """new = old <op> val for the floating synthesis, through the vector
    float path (the scalar float core is splat-and-extract by design)."""
    vtype = mir.VectorType(width, 1, "float")
    os_ = sl._splat_reg(ctx, old_f, vtype, loc)
    vs = sl._splat_reg(ctx, val_f, vtype, loc)
    if op_kind == "add":
        res = ctx.emit(mir.MOp("vbin", [os_, vs],
                               [ctx.vreg(vtype, hint="fa", loc=loc)],
                               attrs={"op": "add"}, loc=loc))
        return sl._scalarize(ctx, res, loc)
    if op_kind in ("max", "min"):
        # NaN behaviour follows the vector compare (vmflt): the corpus
        # atomic families exercise no NaN; propagate_nan is the declared
        # maximum/minimum family's parameter, not the atomic's
        # max: m = old < cand; min: m = old > cand (the swapped-operand
        # lt) -- the CANDIDATE wins the comparison in both directions,
        # so the select's then-branch is the candidate
        pred = "lt" if op_kind == "max" else "gt"
        m = ctx.emit(mir.MOp("vcmp", [os_, vs],
                             [ctx.vreg(mir.MaskType(), hint="fm", loc=loc)],
                             attrs={"pred": pred, "fp": True}, loc=loc))
        v0 = ctx.emit(mir.MOp(
            "vmovmask", [m],
            [ctx.vreg(mir.MaskType(), hint="v0", loc=loc,
                      fixed_phys="v0")], loc=loc))
        sel = ctx.emit(mir.MOp(
            "vsel", [v0, vs, os_],
            [ctx.vreg(vtype, hint="fs", loc=loc)], loc=loc))
        return sl._scalarize(ctx, sel, loc)
    if op_kind == "xchg":
        return val_f
    refuse(loc, "tl.atomic",
           f"floating atomic op {op_kind!r} is not in the synthesis set "
           "(add/max/min/xchg)")


def _bit_view(ctx, reg: mir.VReg, mtype: mir.ScalarType,
              loc) -> mir.VReg:
    """A width-preserving register view move (fp bits <-> int bits; the
    value never changes, only the tracked type)."""
    return ctx.emit(mir.MOp(
        "smove", [reg], [ctx.vreg(mtype, hint="bv", loc=loc)], loc=loc))


def _scalar_atomic_fp(sl, ctx, addr: mir.VReg, val_f: mir.VReg,
                      op_kind: str, pointee: tir.Type,
                      ordering: AtomicOrdering, loc,
                      tag: str = "fpsyn") -> mir.VReg:
    """The floating synthesis: lr/sc on the raw bits, the value computed
    between the pair, one retry loop (the declared RVWMO realization of
    fp atomics on a target whose AMOs are integer-only)."""
    width = pointee.bitwidth()
    ity = mir.ScalarType(width, signed=True)
    fty = mir.ScalarType(width, signed=True, float=True)
    head = ctx.add_block(f"{tag}_head", [], loc)
    ctx.emit0(mir.MOp("br", [], [], attrs={"target": head.name,
                                           "args": []}, loc=loc))
    ctx.switch(head)
    old_b = ctx.emit(mir.MOp(
        "slr", [addr], [ctx.vreg(ity, hint="lr", loc=loc)],
        attrs={"width": width, "aq": ordering.aq, "rl": ordering.rl},
        loc=loc))
    old_f = _bit_view(ctx, old_b, fty, loc)
    new_f = _scalar_fp_compute(sl, ctx, old_f, val_f, op_kind, width, loc)
    new_b = _bit_view(ctx, new_f, ity, loc)
    ok = ctx.emit(mir.MOp(
        "ssc", [addr, new_b],
        [ctx.vreg(mir.I64, hint="sc", loc=loc)],
        attrs={"width": width, "aq": ordering.aq, "rl": ordering.rl},
        loc=loc))
    done = ctx.add_block(f"{tag}_done", [], loc)
    # sc writes 0 on success: nonzero means the reservation was lost and
    # the pair retries
    ctx.emit0(mir.MOp(
        "brc", [ok], [],
        attrs={"true_target": head.name, "true_args": [],
               "false_target": done.name, "false_args": []}, loc=loc))
    ctx.switch(done)
    return old_f


def _scalar_atomic_cas(ctx, addr: mir.VReg, cmp_reg: mir.VReg,
                       val_reg: mir.VReg, pointee: tir.Type,
                       ordering: AtomicOrdering, loc,
                       tag: str = "cas") -> mir.VReg:
    """The CAS retry loop: lr, compare, sc, retry on failure (the
    RISC-V CAS realization; the comparison is on the raw bits, exact for
    every pointee kind)."""
    width = pointee.bitwidth()
    ity = mir.ScalarType(width, signed=True)
    head = ctx.add_block(f"{tag}_head", [], loc)
    ctx.emit0(mir.MOp("br", [], [], attrs={"target": head.name,
                                           "args": []}, loc=loc))
    ctx.switch(head)
    old = ctx.emit(mir.MOp(
        "slr", [addr], [ctx.vreg(ity, hint="cl", loc=loc)],
        attrs={"width": width, "aq": ordering.aq, "rl": ordering.rl},
        loc=loc))
    diff = ctx.emit(mir.MOp(
        "sxor", [old, cmp_reg], [ctx.vreg(ity, hint="cx", loc=loc)],
        loc=loc))
    one = ctx.const(1, ity, loc)
    eq = ctx.emit(mir.MOp(
        "sltu", [diff, one], [ctx.vreg(mir.I64, hint="ce", loc=loc)],
        loc=loc))
    retry = ctx.add_block(f"{tag}_retry", [], loc)
    done = ctx.add_block(f"{tag}_done", [], loc)
    ctx.emit0(mir.MOp(
        "brc", [eq], [],
        attrs={"true_target": retry.name, "true_args": [],
               "false_target": done.name, "false_args": []}, loc=loc))
    ctx.switch(retry)
    ok = ctx.emit(mir.MOp(
        "ssc", [addr, val_reg],
        [ctx.vreg(mir.I64, hint="cs", loc=loc)],
        attrs={"width": width, "aq": ordering.aq, "rl": ordering.rl},
        loc=loc))
    # sc writes 0 on success: nonzero means the reservation was lost and
    # the whole pair retries
    ctx.emit0(mir.MOp(
        "brc", [ok], [],
        attrs={"true_target": head.name, "true_args": [],
               "false_target": done.name, "false_args": []}, loc=loc))
    ctx.switch(done)
    return old


def _splat_i32_const(sl, ctx, value: int, loc) -> mir.VReg:
    k = ctx.const(value, mir.I32, loc)
    return sl._splat_reg(ctx, k, mir.VectorType(32, 1, "int"), loc)


def _mask_to_01(sl, ctx, mask_reg: Optional[mir.VReg], loc) -> mir.VReg:
    """The mask as an i32 0/1 block vector (the branchless lane test);
    None (unmasked) becomes the all-ones splat."""
    if mask_reg is None:
        return _splat_i32_const(sl, ctx, 1, loc)
    if not mask_reg.is_mask():
        # a bool block arrives as a mask value already; a scalar bool is
        # splatted then converted
        mask_reg = sl._mask_of_bool(ctx, mask_reg, loc)
    v0 = ctx.emit(mir.MOp(
        "vmovmask", [mask_reg],
        [ctx.vreg(mir.MaskType(), hint="v0a", loc=loc, fixed_phys="v0")],
        loc=loc))
    ones = _splat_i32_const(sl, ctx, 1, loc)
    zeros = _splat_i32_const(sl, ctx, 0, loc)
    return ctx.emit(mir.MOp(
        "vsel", [v0, ones, zeros],
        [ctx.vreg(mir.VectorType(32, 1, "int"), hint="m01", loc=loc)],
        loc=loc))


def _lower_atomic(sl, ctx, op: tir.Op, loc, is_cas: bool) -> None:
    """One TIR atomic_rmw/atomic_cas: the rank-0 form is one AMO (or its
    synthesis); the block form runs the per-lane loop (extract lane 0,
    slide down, atomic, old value to the workspace, reload as the block).

    A masked atomic performs no access at disabled positions, realized
    branchlessly: the disabled lane's address is redirected to the
    private workspace's redirect slot, so the disabled position's address
    is never presented to memory (the guard-region witness proves the
    redirection is load-bearing: ``witness_drop_atomic_masks`` removes it
    and the poisoned guard is corrupted).
    """
    if is_cas:
        ptr, cmp_v, val = op.operands[0], op.operands[1], op.operands[2]
        mask = op.operands[3] if len(op.operands) > 3 else None
        op_kind = "cas"
    else:
        ptr, val = op.operands[0], op.operands[1]
        mask = op.operands[2] if len(op.operands) > 2 else None
        cmp_v = None
        op_kind = op.attrs["op"]
    sem = op.attrs["sem"]
    scope = op.attrs["scope"]
    ordering = atomic_ordering(sem, scope)
    pointee = ptr.type.pointee
    width = pointee.bitwidth()
    if pointee.is_bool() or width not in (32, 64):
        refuse(loc, "tl.atomic",
               f"atomic pointee width {width} is not in the slice (the "
               "AMO families are 32/64-bit; narrower pointees are a "
               "located refusal, never a wider silent access)")
    if pointee.is_float() and width != 32:
        refuse(loc, "tl.atomic",
               "floating atomics are synthesized at 32 bits (fp32 only in "
               "this slice)")
    base_reg, offset_reg, _pt = sl._address_of(ctx, ptr, loc)
    drop_mask = getattr(sl.options, "witness_drop_atomic_masks", False)

    _emit_fence(ctx, ordering.lead, loc)
    if ptr.rank == 0 and (mask is None or mask.rank == 0):
        # -- the rank-0 form ------------------------------------------------
        if mask is not None:
            refuse(loc, "tl.atomic",
                   "a masked scalar atomic is not in the slice (the mask "
                   "must be a block value)")
        addr = _scalar_address(ctx, base_reg, offset_reg, pointee, loc)
        stag = getattr(sl, "_tag", None)
        stag = stag("scas" if is_cas else "sfp") if callable(stag) \
            else ("scas" if is_cas else "sfp")
        if is_cas:
            cmp_reg = _atomic_value_reg(sl, ctx, cmp_v, pointee, width, loc)
            val_reg = _atomic_value_reg(sl, ctx, val, pointee, width, loc)
            old = _scalar_atomic_cas(ctx, addr, cmp_reg, val_reg, pointee,
                                     ordering, loc, tag=stag)
        elif pointee.is_float():
            val_f = _atomic_value_reg(sl, ctx, val, pointee, width, loc)
            old = _scalar_atomic_fp(sl, ctx, addr, val_f, op_kind, pointee,
                                    ordering, loc, tag=stag)
        else:
            val_reg = _atomic_value_reg(sl, ctx, val, pointee, width, loc)
            old = _scalar_atomic_int(ctx, addr, val_reg, op_kind, pointee,
                                     loc, ordering)
        _emit_fence(ctx, ordering.trail, loc)
        sl._bind_result(op, old)
        return

    # -- the block form: the per-lane loop ----------------------------------
    if sl._chunk is None:
        raise sl._err(loc, "tl.atomic",
                      "a block atomic outside the vector chunk region")
    vl = sl._vl
    esz = width // 8
    ws_base = sl._workspace_private_reg(ctx, loc)
    res_off, redir_off, _span = _atomic_ws_layout(sl)
    val_tir = val
    val_reg = sl._need(val_tir, loc)
    if not val_reg.is_vector():
        vt = mir.VectorType(val_reg.type.width if not val_reg.type.float
                            else width, 1,
                            "float" if pointee.is_float() else
                            ("uint" if not pointee.is_int_signed()
                             else "int"))
        val_reg = sl._splat_reg(ctx, val_reg, vt, loc)
    if val_reg.type.sew != sl._sew:
        raise sl._err(loc, "tl.atomic",
                      f"atomic value SEW {val_reg.type.sew} is not the "
                      f"data SEW {sl._sew}")
    m01 = _mask_to_01(sl, ctx, sl._need(mask, loc), loc) \
        if (mask is not None and not drop_mask) else None
    cmp_reg = None
    if is_cas:
        cmp_reg = sl._need(cmp_v, loc)
        if not cmp_reg.is_vector():
            cmp_reg = sl._splat_reg(
                ctx, cmp_reg,
                mir.VectorType(sl._sew, 1, "int" if not pointee.is_float()
                               else "float"), loc)
    # the loop-carried sliding state: each iteration extracts lane 0 and
    # slides the whole vector down by one, so the carried values ARE the
    # not-yet-processed lanes.  Values provably uniform across the lanes
    # (a splatted scalar, the unmasked all-ones mask) ride as the SCALAR:
    # lane 0 of a splat is the scalar itself, so no vector and no slide --
    # the register pressure of the per-lane loop stays proportional to the
    # genuinely varying values
    off_vec = offset_reg
    if not off_vec.is_vector():
        refuse(loc, "tl.atomic",
               "the block atomic's pointer offset is not a block value")
    # redir/res_base recompute inside the loop from the workspace base:
    # two fewer GPRs live across the whole per-lane loop (the adds are
    # trivial next to the atomic itself)
    redir = None
    res_base = None
    j0 = ctx.const(0, mir.I64, loc)
    jn = ctx.const(vl, mir.I64, loc)
    # a unique loop tag per atomic (block names are branch targets -- every
    # per-lane loop must own its own; the cas/fp retry loops below derive
    # theirs from it)
    _tag = getattr(sl, "_tag", None)
    atag = _tag("atm") if callable(_tag) else "atm"

    def splat_source(reg: mir.VReg):
        """The scalar a register splat came from (None when the value
        genuinely varies per lane).  The frontend's broadcast lowering is
        the s2v of the scalar."""
        if reg is None or not reg.is_vector():
            return None
        for b in ctx.function.blocks:
            for op in b.ops:
                if op.opcode == "s2v" and op.results[0].rid == reg.rid \
                        and op.operands[0].is_scalar():
                    return op.operands[0]
        return None

    # the mask as a lane-scalar: an unmasked atomic is uniformly active
    unmasked = mask is None or drop_mask
    m01_scalar = ctx.const(1, mir.I32, loc) if unmasked else None
    val_scalar = splat_source(val_reg)
    cmp_scalar = splat_source(cmp_reg) if cmp_reg is not None else None
    # the vectors that actually vary: offsets always; the mask/value/cmp
    # only when they are not provably uniform
    m01_vec = None if m01_scalar is not None else m01
    val_vec = None if val_scalar is not None else val_reg
    cmp_vec = None if cmp_scalar is not None else cmp_reg
    carried = [off_vec]
    if m01_vec is not None:
        carried.append(m01_vec)
    if val_vec is not None:
        carried.append(val_vec)
    if cmp_vec is not None:
        carried.append(cmp_vec)
    loop = begin_counted_loop(ctx, j0, jn, carried, loc, atag)
    j = loop.params[0]
    pi = 1
    off_vec = loop.params[pi]; pi += 1
    if m01_vec is not None:
        m01_vec = loop.params[pi]; pi += 1
    if val_vec is not None:
        val_vec = loop.params[pi]; pi += 1
    if cmp_vec is not None:
        cmp_vec = loop.params[pi]; pi += 1

    def slide(reg: mir.VReg) -> mir.VReg:
        return ctx.emit(mir.MOp(
            "vslidedn", [reg],
            [ctx.vreg(reg.type, hint="sl", loc=loc)], loc=loc))

    def extract(reg_or_scalar, hint: str):
        """Lane 0 of the per-lane state: the extract for a vector, the
        scalar itself for a uniform value."""
        if not isinstance(reg_or_scalar, mir.VReg):
            return reg_or_scalar
        if not reg_or_scalar.is_vector():
            return reg_or_scalar
        sty = mir.ScalarType(reg_or_scalar.type.sew, signed=True,
                             float=reg_or_scalar.type.kind == "float")
        return ctx.emit(mir.MOp(
            "vextract", [reg_or_scalar],
            [ctx.vreg(sty, hint=hint, loc=loc)], loc=loc))

    redir = ctx.emit(mir.MOp(
        "sadd", [ws_base, ctx.const(redir_off, mir.I64, loc)],
        [ctx.vreg(mir.I64, hint="wrd", loc=loc)], loc=loc))
    res_base = ctx.emit(mir.MOp(
        "sadd", [ws_base, ctx.const(res_off, mir.I64, loc)],
        [ctx.vreg(mir.I64, hint="wrs", loc=loc)], loc=loc))

    # lane j's address: base + zext(extract(off_vec)) * esz
    off0 = extract(off_vec, "ao")
    off64 = widen_to(ctx, off0, 64, loc)
    byte = ctx.emit(mir.MOp(
        "smul", [off64, ctx.const(esz, mir.I64, loc)],
        [ctx.vreg(mir.I64, hint="ab", loc=loc)], loc=loc)) \
        if esz != 1 else off64
    addr = ctx.emit(mir.MOp(
        "sadd", [base_reg, byte],
        [ctx.vreg(mir.I64, hint="aa", loc=loc)], loc=loc))
    m = extract(m01_vec if m01_vec is not None else m01_scalar, "am")
    # the branchless no-access realization: redirect the disabled lane
    dmask = ctx.emit(mir.MOp(
        "ssub", [ctx.const(0, mir.I32, loc), m],
        [ctx.vreg(mir.I32, hint="mk", loc=loc)], loc=loc))
    dmask64 = widen_to(ctx, dmask, 64, loc)
    diff = ctx.emit(mir.MOp(
        "ssub", [addr, redir],
        [ctx.vreg(mir.I64, hint="ad", loc=loc)], loc=loc))
    sel = ctx.emit(mir.MOp(
        "sand", [diff, dmask64],
        [ctx.vreg(mir.I64, hint="as", loc=loc)], loc=loc))
    safe = ctx.emit(mir.MOp(
        "sadd", [redir, sel],
        [ctx.vreg(mir.I64, hint="af", loc=loc)], loc=loc))
    v = extract(val_vec if val_vec is not None else val_scalar, "av")
    if pointee.is_float():
        # the value lane is float bits; the synthesis consumes float views
        if is_cas:
            c = extract(cmp_vec if cmp_vec is not None else cmp_scalar,
                        "ac")
            old_b = _scalar_atomic_cas(ctx, safe, c, v, pointee, ordering,
                                       loc)
        else:
            old_f = _scalar_atomic_fp(sl, ctx, safe, v, op_kind, pointee,
                                      ordering, loc)
            old_b = _bit_view(ctx, old_f,
                              mir.ScalarType(width, signed=True), loc)
    else:
        if v.type.width != width:
            v = widen_to(ctx, v, width, loc) if v.type.width < width \
                else narrow_to(ctx, v, width, loc)
        if is_cas:
            c = extract(cmp_vec if cmp_vec is not None else cmp_scalar,
                        "ac")
            if c.type.width != width:
                c = widen_to(ctx, c, width, loc) if c.type.width < width \
                    else narrow_to(ctx, c, width, loc)
            old_b = _scalar_atomic_cas(ctx, safe, c, v, pointee, ordering,
                                       loc, tag=atag + "c")
        else:
            old_b = _scalar_atomic_int(ctx, safe, v, op_kind, pointee, loc,
                                       ordering)
    # the result lane: the old value at enabled lanes, 0 at disabled
    # ones.  The mask's 0/-1 must arrive at the VALUE's own type (an
    # unsigned pointee's old value is u32; a signed-kind AND against it
    # is a verifier mismatch, and the bits are the same either way).
    if old_b.type.width == 64 and width == 32:
        old_b = narrow_to(ctx, old_b, 32, loc)
    if old_b.type != dmask.type:
        if old_b.type.width != dmask.type.width:
            dmask_w = widen_to(ctx, dmask, old_b.type.width, loc)
        else:
            dmask_w = ctx.emit(mir.MOp(
                "smove", [dmask],
                [ctx.vreg(old_b.type, hint="mz", loc=loc)], loc=loc))
    else:
        dmask_w = dmask
    oldz = ctx.emit(mir.MOp(
        "sand", [old_b, dmask_w],
        [ctx.vreg(old_b.type, hint="az", loc=loc)], loc=loc))
    slot = ctx.emit(mir.MOp(
        "smul", [j, ctx.const(esz, mir.I64, loc)],
        [ctx.vreg(mir.I64, hint="aj", loc=loc)], loc=loc))
    res_addr = ctx.emit(mir.MOp(
        "sadd", [res_base, slot],
        [ctx.vreg(mir.I64, hint="ar", loc=loc)], loc=loc))
    sty = mir.ScalarType(width, signed=pointee.is_int_signed(),
                         float=pointee.is_float())
    ctx.emit0(mir.MOp("sstore", [res_addr, oldz], [],
                      attrs={"width": width, "offset": 0}, loc=loc))
    # slide for the next lane, then the back edge (the slid vectors are
    # the loop-carried values the next iteration extracts from; uniform
    # scalars pass through unchanged)
    back = [ctx.emit(mir.MOp(
        "sadd", [j, ctx.const(1, mir.I64, loc)],
        [ctx.vreg(mir.I64, hint="an", loc=loc)], loc=loc)),
        slide(off_vec)]
    if m01_vec is not None:
        back.append(slide(m01_vec))
    if val_vec is not None:
        back.append(slide(val_vec))
    if cmp_vec is not None:
        back.append(slide(cmp_vec))
    close_loop(ctx, loop, back)
    # the loop's exit block continues the chunk body; the result base
    # recomputes here (the loop-body copies do not dominate the exit, and
    # the cached workspace register was defined inside the chunk body)
    ctx.switch(loop.exit)
    launch_param = ctx.function.params[0]
    ws_exit = ctx.emit(mir.MOp(
        "sload", [launch_param], [ctx.vreg(mir.I64, hint="wse", loc=loc)],
        attrs={"width": 64, "offset": 16, "ext": "sext"}, loc=loc))
    res_base = ctx.emit(mir.MOp(
        "sadd", [ws_exit, ctx.const(res_off, mir.I64, loc)],
        [ctx.vreg(mir.I64, hint="wrs", loc=loc)], loc=loc))
    # restore the data region (the loop's scalar ops left vtype alone,
    # but the extract/slide ran inside the chunk's region -- re-assert it)
    avl = ctx.const(sl._vl, mir.I32, loc)
    ctx.emit(mir.MOp("vsetvli", [avl],
                     [ctx.vreg(mir.I32, hint="avl", loc=loc)],
                     attrs={"sew": sl._sew, "lmul": 1, "policy": "ta,ma"},
                     loc=loc))
    # the block result: the per-lane old values, reloaded unit-stride
    rtype = mir.VectorType(width, 1,
                           "float" if pointee.is_float() else
                           ("uint" if not pointee.is_int_signed()
                            else "int"))
    if rtype.sew != sl._sew:
        raise sl._err(loc, "tl.atomic",
                      f"atomic result SEW {rtype.sew} is not the data SEW "
                      f"{sl._sew} (narrower pointees are a located "
                      "refusal)")
    result = ctx.emit(mir.MOp(
        "vunit_load", [res_base],
        [ctx.vreg(rtype, hint="aold", loc=loc)],
        attrs={"sew": rtype.sew}, loc=loc))
    _emit_fence(ctx, ordering.trail, loc)
    sl._bind_result(op, result)


def lower_atomic_rmw(sl, ctx, op: tir.Op, loc) -> None:
    """The TIR atomic_rmw entry (the vectorize slice routes here)."""
    _lower_atomic(sl, ctx, op, loc, is_cas=False)


def lower_atomic_cas(sl, ctx, op: tir.Op, loc) -> None:
    """The TIR atomic_cas entry (the vectorize slice routes here)."""
    _lower_atomic(sl, ctx, op, loc, is_cas=True)


# ---------------------------------------------------------------------------
# The wide-access proof (multiple_of / max_contiguous hints; the structural
# arange-plus-scalars form) -- MECH-MASKED-VECTOR-ACCESS
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WideProof:
    """A proven-contiguous, naturally-aligned access.

    ``source``: how contiguity was proven -- ``structural`` (the offset is
    the kernel's arange plus scalar terms, multiplied by the constant 1)
    or ``hint`` (``max_contiguous >= vl`` on the offset value, recorded
    through the TIR ``hint`` op).

    ``scalar_terms``: the TIR scalar values summed into the access's
    element-offset base (empty for the hint path, whose base is the
    offset vector's lane 0).

    ``alignment``: the proven byte alignment of the first lane (the
    structural path is naturally aligned by construction under A004;
    the hint path records the ``multiple_of`` fact).
    """

    source: str
    scalar_terms: Tuple["tir.Value", ...] = ()
    alignment: int = 0
    detail: str = ""


def _flatten_ptradd(ptr: "tir.Value"):
    """The ptradd chain of a pointer value: (base, offsets in tree order).

    Mirrors the slice's ``_address_of`` on the TIR side (the whole-tree
    address form)."""
    offsets: List["tir.Value"] = []
    node = ptr
    while node.producer is not None and node.producer.op == "ptradd":
        offsets.append(node.producer.operands[1])
        node = node.producer.operands[0]
    return node, list(reversed(offsets))


def _split_arange_sum(value: "tir.Value"):
    """Split a vector offset into (scalar TIR terms, constexpr multiplier,
    arange op) when it is ``constexpr * arange + scalars``; None otherwise.

    Follows add / mul-by-constexpr / hint / broadcast-of-arange producers
    only; every other form (runtime strides, indirect values, subtraction)
    declines -- the access keeps its masked/indexed form."""
    scalars: List["tir.Value"] = []
    mult = 1
    node = value
    while True:
        prod = node.producer
        if prod is None:
            return None
        if prod.op == "hint":
            node = prod.operands[0]
            continue
        if prod.op == "broadcast" and prod.operands[0].producer is not None \
                and prod.operands[0].producer.op == "arange":
            return scalars, mult, prod.operands[0].producer
        if prod.op == "arange":
            return scalars, mult, prod
        if prod.op == "arith.add":
            lhs, rhs = prod.operands

            # a broadcast-of-scalar is the frontend's explicit expansion
            # of a scalar term (the lanes replicate one value); the
            # underlying scalar is the term
            def _bare_scalar(v):
                if v.rank == 0:
                    return v
                p = v.producer
                if p is not None and p.op == "broadcast" \
                        and p.operands[0].rank == 0:
                    return p.operands[0]
                return None

            ls, rs = _bare_scalar(lhs), _bare_scalar(rhs)
            if ls is not None and rs is None:
                scalars.append(ls)
                node = rhs
                continue
            if rs is not None and ls is None:
                scalars.append(rs)
                node = lhs
                continue
            return None
        if prod.op == "arith.mul":
            lhs, rhs = prod.operands
            for vec, other in ((lhs, rhs), (rhs, lhs)):
                if vec.rank > 0 and other.rank == 0 \
                        and other.producer is not None \
                        and other.producer.op == "const":
                    mult *= int(other.producer.attrs["value"])
                    node = vec
                    break
            else:
                return None
            continue
        return None


def _hint_attrs(value: "tir.Value") -> Dict[str, int]:
    """The multiple_of / max_contiguous facts recorded on a value (the
    TIR ``hint`` op carries them; absent hints give {})."""
    prod = value.producer
    if prod is not None and prod.op == "hint":
        out: Dict[str, int] = {}
        for key in ("multiple_of", "max_contiguous"):
            v = prod.attrs.get(key)
            if isinstance(v, int) and v > 0:
                out[key] = v
        return out
    return {}


def prove_wide_access(sl, ptr: "tir.Value", vl: int) -> Optional[WideProof]:
    """Prove one access contiguous+aligned for the unit-stride form.

    Declines (returns None) whenever the proof does not hold: an unproven
    access keeps its masked/indexed form, never a guessed wide one
    (MECH-MASKED-VECTOR-ACCESS)."""
    base_node, offsets = _flatten_ptradd(ptr)
    if base_node.producer is not None \
            and base_node.producer.op != "select.where":
        return None                      # not a ptradd-formed address
    # a select.where base (the runtime-selected target pointer) is a
    # valid flat base: the contiguity proof concerns the offsets, and the
    # selected base is one of the transport's aligned view bases (T013:
    # the rng_dual target-pointer form -- without this the 16-bit store
    # fell back to the indexed form, whose EEW=64 index at SEW=16 the
    # pinned QEMU rejects with SIGILL)
    scalar_terms: List["tir.Value"] = []
    vector_term = None
    for off in offsets:
        if off.rank == 0:
            scalar_terms.append(off)
            continue
        if vector_term is not None:
            return None                  # two independent vector terms
        vector_term = off
    if vector_term is None:
        return None                      # a scalar pointer: not wide
    split = _split_arange_sum(vector_term)
    if split is not None:
        terms, mult, _arange = split
        if mult != 1:
            return None                  # a strided run, not contiguous
        scalar_terms.extend(terms)
        hints = _hint_attrs(vector_term)
        align = hints.get("multiple_of", 0)
        return WideProof(
            source="structural" + ("+hint" if hints else ""),
            scalar_terms=tuple(scalar_terms), alignment=align,
            detail=f"offset = arange + {len(scalar_terms)} scalar term(s) "
                   f"at multiplier 1 (naturally aligned under A004)")
    hints = _hint_attrs(vector_term)
    if hints.get("max_contiguous", 0) >= vl:
        return WideProof(
            source="hint", scalar_terms=(),
            alignment=hints.get("multiple_of", 0),
            detail=f"max_contiguous({hints['max_contiguous']}) >= vl({vl})"
                   + (f", multiple_of({hints['multiple_of']})"
                      if "multiple_of" in hints else ""))
    return None


# ---------------------------------------------------------------------------
# tl.gather (the register permute)
# ---------------------------------------------------------------------------

def lower_gather(sl, ctx, op: tir.Op, loc) -> None:
    """``out[i] = src[index[i]]`` along axis 0 as ``vrgather.vv``.

    The register permute is exact when the whole source block is live in
    one chunk (the one-extent region's single-chunk form).  A block the
    chunk plan splits into several vl-sized pieces computes its values
    per chunk, so a register gather could only index the current piece --
    a chunk-crossing gather needs the whole block materialized at once,
    which is the layout lane's multi-chunk path (a located refusal here,
    never a silently wrong permute).  The multi-axis forms and the
    SEW-mismatched index forms refuse the same way."""
    src_t, idx_t = op.operands[0], op.operands[1]
    axis = op.attrs["axis"]
    if axis != 0:
        raise sl._err(loc, "tl.gather",
                      f"gather along axis {axis} of a multi-axis block is "
                      "the layout lane's path (this slice lowers the "
                      "rank-1, axis-0 form)")
    if len(sl.plan.chunks) > 1:
        raise sl._err(loc, "tl.gather",
                      f"the source block ({sl.plan.block_extent} elements) "
                      f"splits into {len(sl.plan.chunks)} vector chunks; a "
                      "register gather could only index the current chunk "
                      "(a chunk-crossing gather needs the whole block "
                      "materialized at once -- the layout lane's "
                      "multi-chunk path)")
    src = sl._need(src_t, loc)
    idx = sl._need(idx_t, loc)
    if not src.is_vector() or not idx.is_vector():
        raise sl._err(loc, "tl.gather",
                      "gather operands must be block values at this "
                      "position")
    if (src.type.sew, src.type.lmul) != (idx.type.sew, idx.type.lmul):
        raise sl._err(loc, "tl.gather",
                      f"index (SEW {idx.type.sew}, LMUL {idx.type.lmul}) "
                      f"differs from the source (SEW {src.type.sew}, LMUL "
                      f"{src.type.lmul}); the single-region register form "
                      "requires matching widths (a mixed-width gather is "
                      "a located refusal)")
    if idx.type.kind == "float":
        raise sl._err(loc, "tl.gather",
                      "the gather index must be an integer block")
    reg = ctx.emit(mir.MOp(
        "vrgather", [src, idx],
        [ctx.vreg(src.type, hint="gth", loc=loc)], loc=loc))
    sl._bind_result(op, reg)


# ---------------------------------------------------------------------------
# tl.interleave (the standalone program-level lowering)
# ---------------------------------------------------------------------------
#
# ``tl.interleave(a, b)`` produces a block whose last extent is twice the
# operands': ``r[2i] = a[i]``, ``r[2i+1] = b[i]``.  The elementwise slice
# hosts one block extent per kernel, so a kernel whose inputs and output
# have different extents cannot ride the chunk region; the construct
# lowers here as a complete program-level MIR module (the same program
# shape the elementwise lane emits: entry binding, worker-strided chunk
# loop, stats, ret), exactly as the IME slice does for its tile pipeline.
# The interleave is realized as two masked indexed scatters at the
# doubled element positions (out[2i] from a, out[2i+1] from b): ragged
# tails are owned by the lane guard and no access happens at disabled
# positions.

from dataclasses import dataclass as _dataclass


@_dataclass
class InterleaveOptions:
    """Options of the standalone interleave lowering."""
    #: element width in bits (the corpus interleave is fp32)
    sew: int = 32
    #: lanes per chunk (the target's (SEW, LMUL=1) vector length; 0 derives)
    vl: int = 0
    #: the element kind (the corpus interleave is fp32)
    float_elements: bool = True

    def identity_part(self) -> str:
        return f"sew{self.sew}-vl{self.vl}"


@_dataclass
class InterleaveBinding:
    """The view indices of the interleave kernel's three arrays."""
    a_index: int
    b_index: int
    out_index: int

    def describe(self) -> dict:
        return {"a": self.a_index, "b": self.b_index,
                "out": self.out_index}


def interleave_binding(names) -> InterleaveBinding:
    """The binding for view names in the sorted bundle order."""
    ordered = sorted(names)
    return InterleaveBinding(a_index=ordered.index("a_ptr"),
                             b_index=ordered.index("b_ptr"),
                             out_index=ordered.index("out_ptr"))


class _InterleaveCtx:
    """The emission helper (the same shape as the slice's _Ctx)."""

    def __init__(self, module: mir.MModule, function: mir.MFunction):
        self.module = module
        self.function = function
        self.blocks: Dict[str, mir.Block] = {}
        self.cur: Optional[mir.Block] = None
        self._hints: Dict[str, int] = {}

    def add_block(self, name: str, params=(), loc=None) -> mir.Block:
        block = mir.Block(name, list(params), loc)
        self.function.blocks.append(block)
        self.blocks[name] = block
        return block

    def switch(self, block: mir.Block) -> None:
        self.cur = block

    def vreg(self, mtype, hint: str = "t", loc=None,
             fixed_phys: Optional[str] = None) -> mir.VReg:
        n = self._hints.get(hint, 0) + 1
        self._hints[hint] = n
        return mir.VReg(mtype, name=f"{hint}{n}", fixed_phys=fixed_phys,
                        loc=loc)

    def emit(self, op: mir.MOp) -> mir.VReg:
        self.cur.ops.append(op)
        assert len(op.results) == 1, op.opcode
        return op.results[0]

    def emit0(self, op: mir.MOp) -> None:
        self.cur.ops.append(op)

    def const(self, bits: int, mtype: mir.ScalarType, loc) -> mir.VReg:
        return self.emit(mir.MOp("sconst", [],
                                 [self.vreg(mtype, hint="k", loc=loc)],
                                 attrs={"value": int(bits)}, loc=loc))


def _iview(ctx: _InterleaveCtx, views: mir.VReg, index: int, hint: str,
           loc) -> mir.VReg:
    return ctx.emit(mir.MOp(
        "sload", [views],
        [ctx.vreg(mir.I64, hint=hint, loc=loc)],
        attrs={"width": 64, "offset": index * 56, "ext": "sext"}, loc=loc))


def _iextent(ctx: _InterleaveCtx, views: mir.VReg, index: int, hint: str,
             loc) -> mir.VReg:
    """The view's axis-0 extent: the shape pointer lives at view+8 in the
    view record (view+0 is the data pointer), extent[0] at shape+0."""
    shape = ctx.emit(mir.MOp(
        "sload", [views],
        [ctx.vreg(mir.I64, hint=hint + "sh", loc=loc)],
        attrs={"width": 64, "offset": index * 56 + 8, "ext": "sext"},
        loc=loc))
    return ctx.emit(mir.MOp(
        "sload", [shape], [ctx.vreg(mir.I64, hint=hint, loc=loc)],
        attrs={"width": 64, "offset": 0, "ext": "sext"}, loc=loc))


def lower_interleave(binding: InterleaveBinding,
                     target=None, options: Optional[InterleaveOptions] = None,
                     loc=None) -> mir.MModule:
    """One interleave kernel -> a complete program-level MIR module.

    ``out = interleave(a, b)`` over the runtime extent n (the a view's
    shape): every worker strides the chunk range (chunks w, w+W, ...),
    loads its a/b slices through the masked indexed form (no access at
    disabled lanes) and scatters them to the even/odd output positions
    through equally masked indexed stores -- useful multi-worker work on
    one artifact at every 1/2/4/8 thread count, with ragged tails owned.
    """
    from a100c.target import DEFAULT_TARGET
    target = target or DEFAULT_TARGET
    options = options or InterleaveOptions()
    sew = options.sew
    vl = options.vl or target.vlmax(sew, 1)
    esz = sew // 8
    pty = tir.Type.float(sew) if options.float_elements else tir.Type.int(sew)
    vt = mir.VectorType(sew, 1,
                        "float" if options.float_elements else "int")
    module = mir.MModule("interleave", loc)
    launch = mir.VReg(mir.I64, name="launch")
    function = mir.MFunction("operator_entry", [launch], loc)
    module.functions.append(function)
    ctx = _InterleaveCtx(module, function)
    ctx.add_block("entry", [launch], loc)
    ctx.switch(ctx.blocks["entry"])

    bundle = ctx.emit(mir.MOp(
        "sload", [launch], [ctx.vreg(mir.I64, hint="bundle", loc=loc)],
        attrs={"width": 64, "offset": 0, "ext": "sext"}, loc=loc))
    views = ctx.emit(mir.MOp(
        "sload", [bundle], [ctx.vreg(mir.I64, hint="views", loc=loc)],
        attrs={"width": 64, "offset": 0, "ext": "sext"}, loc=loc))
    stats = ctx.emit(mir.MOp(
        "sload", [launch], [ctx.vreg(mir.I64, hint="stats", loc=loc)],
        attrs={"width": 64, "offset": 24, "ext": "sext"}, loc=loc))
    worker_id = ctx.emit(mir.MOp(
        "sload", [launch], [ctx.vreg(mir.U32, hint="wid", loc=loc)],
        attrs={"width": 32, "offset": 40, "ext": "zext"}, loc=loc))
    worker_count = ctx.emit(mir.MOp(
        "sload", [launch], [ctx.vreg(mir.U32, hint="wcnt", loc=loc)],
        attrs={"width": 32, "offset": 44, "ext": "zext"}, loc=loc))
    wid64 = ctx.emit(mir.MOp(
        "smove", [worker_id], [ctx.vreg(mir.I64, hint="wid64", loc=loc)],
        loc=loc))
    wcnt64 = ctx.emit(mir.MOp(
        "smove", [worker_count],
        [ctx.vreg(mir.I64, hint="wcnt64", loc=loc)], loc=loc))
    a_data = _iview(ctx, views, binding.a_index, "va", loc)
    b_data = _iview(ctx, views, binding.b_index, "vb", loc)
    out_data = _iview(ctx, views, binding.out_index, "vo", loc)
    n = _iextent(ctx, views, binding.a_index, "vn", loc)

    it = mir.VectorType(32, 1, "int")

    # head(elem, items): elem < n; each worker strides the chunk range
    # from its own first chunk (chunks w, w+W, w+2W, ... -- the same
    # strided ownership the program partition uses)
    elem0 = ctx.emit(mir.MOp(
        "smul", [wid64, ctx.const(vl, mir.I64, loc)],
        [ctx.vreg(mir.I64, hint="e0", loc=loc)], loc=loc))
    items0 = ctx.const(0, mir.I64, loc)
    head = ctx.add_block("il_head", [], loc)
    ctx.emit0(mir.MOp("br", [], [], attrs={"target": head.name,
                                           "args": [elem0, items0]},
                      loc=loc))
    elem_h = mir.VReg(mir.I64, name="elem.loop")
    items_h = mir.VReg(mir.I64, name="items.loop")
    head.params += [elem_h, items_h]
    ctx.switch(head)
    cont = ctx.emit(mir.MOp("slt", [elem_h, n],
                            [ctx.vreg(mir.I64, hint="go", loc=loc)],
                            loc=loc))
    exitb = ctx.add_block("il_exit", [elem_h, items_h], loc)
    ctx.emit0(mir.MOp(
        "brc", [cont], [],
        attrs={"true_target": "il_body", "true_args": [elem_h, items_h],
               "false_target": "il_exit", "false_args": [elem_h, items_h]},
        loc=loc))

    body = ctx.add_block("il_body", [elem_h, items_h], loc)
    ctx.switch(body)
    avl = ctx.const(vl, mir.I32, loc)
    ctx.emit(mir.MOp("vsetvli", [avl],
                     [ctx.vreg(mir.I32, hint="vl", loc=loc)],
                     attrs={"sew": sew, "lmul": 1, "policy": "ta,ma"},
                     loc=loc))
    # the element index i = elem + vid and its lane guard
    vid = ctx.emit(mir.MOp("vid", [],
                           [ctx.vreg(it, hint="vid", loc=loc)], loc=loc))
    elem32 = ctx.emit(mir.MOp(
        "strunc", [elem_h], [ctx.vreg(mir.I32, hint="e32", loc=loc)],
        loc=loc))
    idx = ctx.emit(mir.MOp(
        "vbinx", [vid, elem32],
        [ctx.vreg(it, hint="idx", loc=loc)], attrs={"op": "add"}, loc=loc))
    idxw = ctx.emit(mir.MOp(
        "vwaddx0", [idx],
        [ctx.vreg(mir.VectorType(64, 2, "int"), hint="idxw", loc=loc)],
        attrs={"mode": "sext"}, loc=loc))
    avl2 = ctx.const(vl, mir.I32, loc)
    ctx.emit(mir.MOp("vsetvli", [avl2],
                     [ctx.vreg(mir.I32, hint="vl2", loc=loc)],
                     attrs={"sew": 64, "lmul": 2, "policy": "ta,ma"},
                     loc=loc))
    ns = ctx.emit(mir.MOp(
        "s2v", [n], [ctx.vreg(mir.VectorType(64, 2, "int"), hint="ns",
                              loc=loc)], loc=loc))
    lane_ok = ctx.emit(mir.MOp(
        "vcmp", [idxw, ns],
        [ctx.vreg(mir.MaskType(), hint="lok", loc=loc)],
        attrs={"pred": "lt", "fp": False}, loc=loc))
    avl3 = ctx.const(vl, mir.I32, loc)
    ctx.emit(mir.MOp("vsetvli", [avl3],
                     [ctx.vreg(mir.I32, hint="vl3", loc=loc)],
                     attrs={"sew": sew, "lmul": 1, "policy": "ta,ma"},
                     loc=loc))
    v0 = ctx.emit(mir.MOp(
        "vmovmask", [lane_ok],
        [ctx.vreg(mir.MaskType(), hint="v0", loc=loc, fixed_phys="v0")],
        loc=loc))
    # a[i], b[i]: masked indexed loads (no access at disabled lanes)
    from a100c.lower import addresses as _addr
    a_off = _addr.materialize_address(ctx, a_data, idx, pty, loc, vl,
                                      (sew, 1))[0]
    va = ctx.emit(mir.MOp(
        "vloadix", [a_data, a_off, v0], [ctx.vreg(vt, hint="va", loc=loc)],
        attrs={"eew": 64, "sew": sew, "default": "undef"}, loc=loc))
    b_off = _addr.materialize_address(ctx, b_data, idx, pty, loc, vl,
                                      (sew, 1))[0]
    vb = ctx.emit(mir.MOp(
        "vloadix", [b_data, b_off, v0], [ctx.vreg(vt, hint="vb", loc=loc)],
        attrs={"eew": 64, "sew": sew, "default": "undef"}, loc=loc))
    # out[2i] = a[i], out[2i+1] = b[i]: masked indexed scatters at the
    # doubled element positions, based at this chunk's doubled offset
    # (the interleave as two strided stores)
    e2 = ctx.emit(mir.MOp(
        "smul", [elem_h, ctx.const(2 * esz, mir.I64, loc)],
        [ctx.vreg(mir.I64, hint="e2", loc=loc)], loc=loc))
    out_base = ctx.emit(mir.MOp(
        "sadd", [out_data, e2],
        [ctx.vreg(mir.I64, hint="ob", loc=loc)], loc=loc))
    two = ctx.const(2, mir.I32, loc)
    idx2 = ctx.emit(mir.MOp(
        "vbinx", [vid, two], [ctx.vreg(it, hint="ix2", loc=loc)],
        attrs={"op": "mul"}, loc=loc))
    one = ctx.const(1, mir.I32, loc)
    idx21 = ctx.emit(mir.MOp(
        "vbinx", [idx2, one], [ctx.vreg(it, hint="ix21", loc=loc)],
        attrs={"op": "add"}, loc=loc))
    out_off2 = _addr.materialize_address(ctx, out_base, idx2, pty, loc, vl,
                                         (sew, 1))[0]
    ctx.emit0(mir.MOp(
        "vstoreix", [out_base, out_off2, va, v0], [],
        attrs={"eew": 64, "sew": sew, "default": "no-access"}, loc=loc))
    out_off21 = _addr.materialize_address(ctx, out_base, idx21, pty, loc,
                                          vl, (sew, 1))[0]
    ctx.emit0(mir.MOp(
        "vstoreix", [out_base, out_off21, vb, v0], [],
        attrs={"eew": 64, "sew": sew, "default": "no-access"}, loc=loc))
    # items += the active lanes; elem += W * vl
    items2 = ctx.emit(mir.MOp(
        "vpopc", [lane_ok], [ctx.vreg(mir.I64, hint="pc", loc=loc)],
        loc=loc))
    items_n = ctx.emit(mir.MOp(
        "sadd", [items_h, items2],
        [ctx.vreg(mir.I64, hint="it2", loc=loc)], loc=loc))
    wvl = ctx.emit(mir.MOp(
        "smul", [wcnt64, ctx.const(vl, mir.I64, loc)],
        [ctx.vreg(mir.I64, hint="wvl", loc=loc)], loc=loc))
    elem_n = ctx.emit(mir.MOp(
        "sadd", [elem_h, wvl],
        [ctx.vreg(mir.I64, hint="en", loc=loc)], loc=loc))
    ctx.emit0(mir.MOp("br", [], [],
                      attrs={"target": head.name,
                             "args": [elem_n, items_n]}, loc=loc))

    ctx.switch(exitb)
    ctx.emit0(mir.MOp("sstore", [stats, items_h], [],
                      attrs={"width": 64, "offset": 0}, loc=loc))
    ctx.emit0(mir.MOp("ret", [], [], loc=loc))
    module.meta["interleave"] = {"sew": sew, "vl": vl,
                                 "float": options.float_elements}
    return module
