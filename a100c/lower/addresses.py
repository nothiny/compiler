"""Address materialization for the vector slice (FE-ADDRESS-EXPRESSIONS).

Every tensor access materializes its address as ONE whole tree in i64
(IR-LOWERING-CONTRACT):

    address = view.data + sext_i32(element_index) * sizeof(pointee)

- the element index expression is the TIR's own offset value, lowered as a
  vector at the region's SEW;
- the widening to i64 is *signed* (the pinned ptradd semantics sign-extends
  i32 offsets; a wrapping index is never widened before the wrap);
- the scale is the pointee size -- a compile-time constant of the pointer's
  element type, matching Triton's element-typed pointer arithmetic (the
  kernel addresses flat storage from the view's data base; host strides are
  not part of kernel pointer semantics);
- the base is added by the indexed memory operation itself (EEW=64 index at
  EMUL = 2xLMUL for SEW=32 LMUL=1).

The tree is checkable against an independent index computation
(``check_address_model``): for every lane, the emitted form must equal
base + index * esz over Python integers -- the FE-ADDRESS-EXPRESSIONS
witness.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from a100c.ir import mir, tir

__all__ = ["AddressTree", "materialize_address", "check_address_model",
           "AddressError"]


@dataclass
class AddressTree:
    """The whole-tree address form of one access (the lowering's contract)."""

    base: str                        # the base vreg name (i64 view data)
    index: str                       # the element-index vreg name (vector)
    index_sew: int
    esz: int                         # pointee size in bytes
    eew: int = 64                    # the indexed op's index EEW

    def describe(self) -> str:
        return (f"{self.base} + sext(vi{self.index_sew} {self.index}) "
                f"* {self.esz}")


class AddressError(Exception):
    def __init__(self, loc, message: str):
        super().__init__(f"address materialization: {message}"
                         + (f" (at {loc})" if loc else ""))
        self.loc = loc
        self.message = message


def materialize_address(ctx, base_reg: mir.VReg, offset_reg: mir.VReg,
                        pointee: tir.Type, loc, vl: int,
                        region: Tuple[int, int] = (32, 1)) -> Tuple[mir.VReg, AddressTree]:
    """Emit the whole-tree byte-offset vector of one access.

    ``ctx`` is the vectorizer's emission context (``emit``/``vreg``/``const``).
    Returns (byte-offset vector at EEW=64, tree record).  The memory op adds
    ``base_reg`` itself.  The i64 scale executes in its own e64m2 region
    (probe-verified region switching); the data region is restored after.
    """
    if not offset_reg.is_vector() or offset_reg.type.sew != 32:
        raise AddressError(
            loc, f"offset '{offset_reg.name}' must be a vi32 vector (i32 "
                 f"index arithmetic), got {offset_reg.type!r}")
    if base_reg.type != mir.I64:
        raise AddressError(
            loc, f"base '{base_reg.name}' must be an i64 view data pointer, "
                 f"got {base_reg.type!r}")
    esz = pointee.bitwidth() // 8
    wide = ctx.emit(mir.MOp(
        "vwiden", [offset_reg],
        [ctx.vreg(mir.VectorType(64, 2, "int"), hint="addrw", loc=loc)],
        attrs={"mode": "sext"}, loc=loc))
    avl = ctx.const(vl, mir.I32, loc)
    ctx.emit(mir.MOp("vsetvli", [avl],
                     [ctx.vreg(mir.I32, hint="rega", loc=loc)],
                     attrs={"sew": 64, "lmul": 2, "policy": "ta,ma"}, loc=loc))
    esz_reg = ctx.const(esz, mir.I64, loc)
    scaled = ctx.emit(mir.MOp(
        "vbinx", [wide, esz_reg],
        [ctx.vreg(mir.VectorType(64, 2, "int"), hint="addrs", loc=loc)],
        attrs={"op": "mul"}, loc=loc))
    restore = ctx.const(vl, mir.I32, loc)
    ctx.emit(mir.MOp("vsetvli", [restore],
                     [ctx.vreg(mir.I32, hint="regr", loc=loc)],
                     attrs={"sew": region[0], "lmul": region[1],
                            "policy": "ta,ma"}, loc=loc))
    tree = AddressTree(base=base_reg.name, index=offset_reg.name,
                       index_sew=32, esz=esz)
    return scaled, tree


def check_address_model(tree: AddressTree, base: int, lane_indices: List[int],
                        expected: Optional[List[int]] = None) -> List[int]:
    """Independent check: the tree's value per lane (base + idx * esz).

    The witness for FE-ADDRESS-EXPRESSIONS: the model is evaluated in Python
    integers, independently of the emitted ops, and compared against the
    expected byte offsets (or returned for the caller to check).
    """
    got = [base + idx * tree.esz for idx in lane_indices]
    if expected is not None and got != list(expected):
        raise AddressError(None, f"address model mismatch: {got} != {expected}")
    return got
