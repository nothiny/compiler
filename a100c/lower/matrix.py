"""IME matrix lowering: a minimal stub refusing what it does not implement.

The vertical slice (T007) lowers one elementwise operator; no ``tl.dot`` /
matrix path exists behind it yet (the frontend's elementwise core refuses
``tl.dot`` before MIR exists).  This module is the declared refusal point the
later matrix tasks replace: any construct routed here is refused with a
located diagnostic naming the construct and the reason
(MECH-DIAGNOSTIC-REFUSAL), never approximated by a nearby vector form.

The refusal also records the sourced operand contract it will have to honor
when implemented: IME LMUL=1 only, vs1 = A tile row-major, vs2 = B tile
column-major, vd even-numbered when MUL_C=2, destination group never
overlapping vs1/vs2, operand format per family, BF16 IME not claimable under
the pinned emulator (F010/F030/F033/F040/F041).
"""
from __future__ import annotations

__all__ = ["MatrixLoweringError", "refuse_matrix"]

#: the sourced operand contract, recorded with the refusal (F030/F033/F040/F041)
IME_OPERAND_CONTRACT = (
    "IME LMUL=1 only; vs1 = A tile row-major; vs2 = B tile column-major; "
    "vd even-numbered when MUL_C=2; destination group must not overlap "
    "vs1/vs2; operand format per family; the pinned emulator's BF16 IME "
    "format selection is unverified (F010) so BF16 never reaches IME here"
)


class MatrixLoweringError(Exception):
    def __init__(self, loc, construct: str, message: str):
        super().__init__(f"matrix lowering: {construct}: {message}"
                         + (f" (at {loc})" if loc else ""))
        self.loc = loc
        self.construct = construct
        self.message = message


def refuse_matrix(loc, construct: str, message: str):
    """The single refusal path for every matrix-routed construct."""
    raise MatrixLoweringError(
        loc, construct,
        f"{message}; the IME tile path is not implemented by the vertical "
        f"slice (operand contract when implemented: {IME_OPERAND_CONTRACT})")
