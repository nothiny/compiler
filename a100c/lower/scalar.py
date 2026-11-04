"""Scalar (rank-0) lowering for the vector slice.

Implements the minimal scalar core the slice needs -- constant, arithmetic,
comparison, move, loads of bundle records -- and REFUSES everything else with
a located diagnostic.  A refusal is a recorded boundary of this task's slice,
never a silent approximation (MECH-DIAGNOSTIC-REFUSAL).
"""
from __future__ import annotations

from typing import Optional

from a100c.ir import mir, tir

__all__ = ["ScalarLoweringError", "scalar_type_of", "lower_const",
           "lower_binop", "lower_cmp", "refuse"]

#: binary TIR op -> MIR scalar opcode (the minimal set the slice lowers;
#: integer only; fp scalar arithmetic is not in the slice and is refused)
_BIN_MAP = {
    "arith.add": "sadd", "arith.sub": "ssub", "arith.mul": "smul",
    "arith.sdiv": "sdiv", "arith.udiv": "sdivu",
    "bit.and": "sand", "bit.or": "sor", "bit.xor": "sxor",
    "bit.shl": "sshl", "bit.ashr": "ssra",
}

#: comparison TIR op -> MIR scalar opcode (the comparison the slice's loop
#: and mask structure produces; others are refused, not approximated)
_CMP_MAP = {
    "cmp.lt": "slt",
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
                loc, "const", f"float width {ty.width} is not in the slice")
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
        refuse(loc, op.op,
               f"scalar binary op is not implemented by the slice's scalar "
               f"core ({sorted(_BIN_MAP)})")
    if lhs.type != rhs.type:
        refuse(loc, op.op,
               f"scalar operand types differ: {lhs.type!r} vs {rhs.type!r} "
               "(the frontend inserts explicit converts)")
    if lhs.type.float:
        refuse(loc, op.op,
               "scalar floating arithmetic is not in the slice (float values "
               "appear only as splatted vector constants)")
    if code in ("srem", "sremu"):
        refuse(loc, op.op, "scalar remainder is not in the slice")
    return ctx.emit(mir.MOp(code, [lhs, rhs],
                            [ctx.vreg(lhs.type, hint="s", loc=loc)],
                            loc=loc))


def lower_cmp(ctx, op: tir.Op, lhs: mir.VReg, rhs: mir.VReg,
              loc) -> mir.VReg:
    if op.op not in _CMP_MAP:
        refuse(loc, op.op, "comparison is not in the scalar core")
    if lhs.type != rhs.type or lhs.type.float:
        refuse(loc, op.op,
               f"scalar comparison on {lhs.type!r}/{rhs.type!r} is not in "
               "the slice")
    # every comparison produces an i64 0/1 (the brc consumes it directly)
    return ctx.emit(mir.MOp(_CMP_MAP[op.op], [lhs, rhs],
                            [ctx.vreg(mir.I64, hint="b", loc=loc)],
                            loc=loc))
