"""Scalar (rank-0) lowering and the structured-control-flow core (T008).

Two responsibilities, one module (the task's declared output):

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
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

from a100c.ir import mir, tir

__all__ = ["ScalarLoweringError", "scalar_type_of", "lower_const",
           "lower_binop", "lower_cmp", "lower_not", "lower_rem",
           "refuse", "widen_to", "narrow_to",
           "scalar_load", "scalar_store",
           "begin_if", "IfFrame", "close_arm", "join_if",
           "begin_counted_loop", "begin_while_loop", "LoopFrame",
           "emit_axis_decomposition", "emit_grid_product"]

#: binary TIR op -> MIR scalar opcode (integer only; scalar floating
#: arithmetic is refused -- floats appear as splatted vector constants and
#: as raw bits in GPRs)
_BIN_MAP = {
    "arith.add": "sadd", "arith.sub": "ssub", "arith.mul": "smul",
    "arith.sdiv": "sdiv", "arith.udiv": "sdivu",
    "bit.and": "sand", "bit.or": "sor", "bit.xor": "sxor",
    "bit.shl": "sshl", "bit.ashr": "ssra",
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


def lower_const(ctx, value, ty: tir.Type, loc) -> mir.VReg:
    """A scalar constant: raw bits (floats via their IEEE bit pattern)."""
    import struct
    if ty.is_float():
        if ty.width == 32:
            bits = struct.unpack("<I", struct.pack("<f", float(value)))[0]
        elif ty.width == 64:
            bits = struct.unpack("<Q", struct.pack("<d", float(value)))[0]
        else:
            raise ScalarLoweringError(
                loc, "const", f"float width {ty.width} is not in the scalar core")
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
#: (slt/sltu + sub/xor); every comparison produces an i64 0/1
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

    def boolean(opcode: str, a: mir.VReg, b: mir.VReg) -> mir.VReg:
        return ctx.emit(mir.MOp(opcode, [a, b],
                                [ctx.vreg(mir.I64, hint="b", loc=loc)],
                                loc=loc))

    if pred == "lt":
        return boolean("slt", lhs, rhs)
    if pred == "gt":
        return boolean("slt", rhs, lhs)
    if pred == "ge":                      # !(lhs < rhs)
        lt = boolean("slt", lhs, rhs)
        return ctx.emit(mir.MOp("sxor", [lt, one],
                                [ctx.vreg(mir.I64, hint="b", loc=loc)],
                                loc=loc))
    if pred == "le":                      # !(rhs < lhs)
        gt = boolean("slt", rhs, lhs)
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

def widen_to(ctx, reg: mir.VReg, width: int, loc) -> mir.VReg:
    """Widen an i32 scalar to i64 (the register already holds the extended
    value; ``smove`` realizes the view).  Other widths are refused."""
    if reg.type.width == width:
        return reg
    if reg.type.width == 32 and width == 64 and not reg.type.float:
        return ctx.emit(mir.MOp(
            "smove", [reg],
            [ctx.vreg(mir.I64, hint="w", loc=loc)], loc=loc))
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
