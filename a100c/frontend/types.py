"""Type rules for the frontend, per the *pinned* Triton 3.8 semantics.

The reference environment pins ``triton.__version__ == 3.8.0`` (F013/F049);
the rules below mirror ``triton/language/semantic.py`` of that pinned
source (``to_tensor_type``, ``integer_promote_impl``,
``computation_type_impl``, ``binary_op_type_checking_impl``,
``broadcast_impl_value``, ``load``/``store``/``where`` typing) — not what
the target happens to support.  Target gaps are handled by legalisation,
never by changing these rules (FE-TYPE-RULES).

Distinct constructs, never one cast (IR-SEMANTIC-FIDELITY):

* ``convert`` — value conversion (numeric change of representation);
* ``bitcast`` — bit-level reinterpretation (width preserved, value re-read).

Zero-dimensional values: scalar arguments and literals are rank-0 values;
broadcasting a rank-0 value splats it (all axes flagged broadcast).
"""
from __future__ import annotations

from typing import Optional, Tuple

from a100c.ir.tir import (BFLOAT16, FLOAT16, FLOAT32, FLOAT64, INT1, INT16,
                          INT32, INT64, INT8, Type, UINT16, UINT32, UINT64,
                          UINT8)

__all__ = [
    "TypeRuleError", "DTYPE_BY_NAME", "dtype_by_name", "literal_type",
    "scalar_arg_type", "scalar_class", "integer_promote", "computation_type",
    "Kind", "kind_rank", "binop_unify", "div_unify", "convert_ok",
    "bitcast_ok", "mantissa_width", "INT_MIN32", "INT_MAX32",
]


class TypeRuleError(Exception):
    """A type-rule violation (the frontend reports it with a source location)."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


#: The corpus dtype surface (F037): bfloat16, bool, float16, float32, int16,
#: int32, int64, int8 (+ the uint aliases that appear as bit-trick dtypes and
#: pointer element types).  ``float64`` exists as a constant for dead dtype
#: dispatch comparisons (OPERATOR_INVENTORY 3); no fp64 tensor case exists.
DTYPE_BY_NAME = {
    "bool": INT1, "int1": INT1,
    "int8": INT8, "uint8": UINT8,
    "int16": INT16, "uint16": UINT16,
    "int32": INT32, "uint32": UINT32,
    "int64": INT64, "uint64": UINT64,
    "float16": FLOAT16, "fp16": FLOAT16,
    "bfloat16": BFLOAT16, "bf16": BFLOAT16,
    "float32": FLOAT32, "fp32": FLOAT32,
    "float64": FLOAT64, "fp64": FLOAT64,
}

INT_MIN32, INT_MAX32 = -2**31, 2**31 - 1
INT_MIN64, INT_MAX64 = -2**63, 2**63 - 1


def dtype_by_name(name: str) -> Type:
    t = DTYPE_BY_NAME.get(str(name))
    if t is None:
        raise TypeRuleError(f"unknown dtype name {name!r}")
    return t


# ---------------------------------------------------------------------------
# Literal typing (pinned to_tensor_type)
# ---------------------------------------------------------------------------

_MIN_F32 = 2.0 ** -126
_MAX_F32 = (2 - 2.0 ** -23) * 2.0 ** 127


def literal_type(value) -> Type:
    """The type of a Python literal appearing in kernel source."""
    if isinstance(value, bool):
        return INT1
    if isinstance(value, int):
        if INT_MIN32 <= value <= INT_MAX32:
            return INT32
        if 2**31 <= value < 2**32:
            return UINT32
        if INT_MIN64 <= value <= INT_MAX64:
            return INT64
        if 2**63 <= value < 2**64:
            return UINT64
        raise TypeRuleError(f"non-representable integer literal {value}")
    if isinstance(value, float):
        a = abs(value)
        if (a == float("inf") or a == 0.0 or value != value
                or _MIN_F32 <= a <= _MAX_F32):
            return FLOAT32
        return FLOAT64
    raise TypeRuleError(f"cannot type literal {value!r} of type "
                        f"{type(value).__name__}")


def scalar_arg_type(value) -> Type:
    """The type of a *runtime* scalar argument (pinned mangle_type rules:
    Python bool -> i1, Python int -> i32/i64/u64 by magnitude, Python float
    -> fp32; numpy scalars by their dtype)."""
    import numpy as np

    if isinstance(value, (bool, np.bool_)):
        return INT1
    if isinstance(value, int):
        if INT_MIN32 <= value <= INT_MAX32:
            return INT32
        if INT_MIN64 <= value <= INT_MAX64:
            return INT64
        return UINT64
    if isinstance(value, np.integer):
        return dtype_by_name(np.dtype(value.dtype).name)
    if isinstance(value, float):
        return FLOAT32
    if isinstance(value, np.floating):
        return dtype_by_name(np.dtype(value.dtype).name)
    raise TypeRuleError(f"cannot type runtime scalar {value!r} of type "
                        f"{type(value).__name__}")


def scalar_class(value) -> Tuple[str, object]:
    """The specialization class of one runtime scalar argument, mirroring the
    corpus's declared meta tier (ops/harness/compiler_api/identity.py
    ``_scalar_signature``):

    ndarray -> ("ptr", dtype name); bool -> ("bool", value);
    int -> ("int", "one" | "div16" | "other"); float -> ("float", numpy
    dtype name of the Python type); anything else -> ("object", type name).
    """
    import numpy as np

    if isinstance(value, np.ndarray):
        return ("ptr", str(value.dtype))
    if isinstance(value, (bool, np.bool_)):
        return ("bool", bool(value))
    if isinstance(value, (int, np.integer)):
        v = int(value)
        if v == 1:
            return ("int", "one")
        if v % 16 == 0:
            return ("int", "div16")
        return ("int", "other")
    if isinstance(value, (float, np.floating)):
        return ("float", np.dtype(type(value)).name)
    return ("object", type(value).__name__)


# ---------------------------------------------------------------------------
# Promotion (pinned integer_promote_impl / computation_type_impl)
# ---------------------------------------------------------------------------

class Kind:
    """Type-kind ordering for the scalar participation rule: bool < int < fp
    (signed and unsigned share one integral kind, exactly as pinned)."""
    BOOLEAN = 0
    INTEGRAL = 1
    FLOATING = 2


def kind_rank(t: Type) -> int:
    if t.is_bool():
        return Kind.BOOLEAN
    if t.is_int():
        return Kind.INTEGRAL
    if t.is_float():
        return Kind.FLOATING
    raise TypeRuleError(f"kind of non-numeric type {t!r}")


def integer_promote(a: Type, b: Type) -> Type:
    """Usual arithmetic conversions (pinned integer_promote_impl).

    ``i1`` is an integer type of width 1 (pinned SINT_TYPES contains int1):
    bool participates in integer promotion as a signed 1-bit integer, and
    bool-with-bool promotes to the bool type itself."""
    if a.is_bool() and b.is_bool():
        return INT1
    if a.is_bool():
        a = Type.int(1)
    if b.is_bool():
        b = Type.int(1)
    a_rank, b_rank = a.width, b.width
    if a.is_int_signed() == b.is_int_signed():
        return a if a_rank > b_rank else b
    if a.is_int_unsigned():
        return a if a_rank >= b_rank else b
    # b unsigned, a signed
    return b if b_rank >= a_rank else a


def mantissa_width(t: Type) -> int:
    return {FLOAT16: 10, BFLOAT16: 7, FLOAT32: 23, FLOAT64: 52}[t]


def computation_type(a: Type, a_is_literal: bool, b: Type, b_is_literal: bool,
                     div_or_mod: bool) -> Type:
    """Pinned computation_type_impl: the scalar participation rule, the fp
    hierarchy, the fp16/bf16 div/mod exception, then integer promotion."""
    # 0) a literal of a lower-or-equal kind does not participate
    if a_is_literal != b_is_literal:
        lit_ty, ten_ty = (a, b) if a_is_literal else (b, a)
        if kind_rank(lit_ty) <= kind_rank(ten_ty):
            if div_or_mod and ten_ty in (FLOAT16, BFLOAT16):
                return FLOAT32
            return ten_ty
    # 1) fp64 wins
    if a is FLOAT64 or b is FLOAT64:
        return FLOAT64
    # 2) fp32 next
    if a is FLOAT32 or b is FLOAT32:
        return FLOAT32
    # 3) fp16 unless / or %
    if a is FLOAT16 or b is FLOAT16:
        return FLOAT32 if div_or_mod else FLOAT16
    # 4) bf16 only when both are bf16
    if a is BFLOAT16 and b is BFLOAT16:
        return FLOAT32 if div_or_mod else BFLOAT16
    if a is BFLOAT16 or b is BFLOAT16:
        return FLOAT32
    # 5) fp8 is excluded by the declared subset (SUBSET.md 6)
    if not (a.is_int() or a.is_bool()) or not (b.is_int() or b.is_bool()):
        raise TypeRuleError(f"unexpected type pair {a!r} and {b!r}")
    # 6) both integers (i1 is a signed integer of width 1, pinned)
    a_sn = a.is_int_signed() or a.is_bool()
    b_sn = b.is_int_signed() or b.is_bool()
    if div_or_mod and a_sn != b_sn:
        raise TypeRuleError(
            f"cannot use /, // or % with {a!r} and {b!r}: different "
            "signedness; cast them to the same signedness")
    return integer_promote(a, b)


_SIGNED_MIN = {1: 0, 8: -2**7, 16: -2**15, 32: INT_MIN32, 64: INT_MIN64}
_SIGNED_MAX = {1: 1, 8: 2**7 - 1, 16: 2**15 - 1, 32: INT_MAX32,
               64: INT_MAX64}
_UNSIGNED_MAX = {1: 1, 8: 2**8 - 1, 16: 2**16 - 1, 32: 2**32 - 1,
                 64: 2**64 - 1}


def _check_literal_range(lit_value, lit_ty: Type, ret: Type) -> None:
    """Pinned range check: an integer literal must be representable in the
    computation type (its lanes would be created with that type)."""
    if not (lit_ty.is_int() and ret.is_int()):
        return
    if isinstance(lit_value, bool):
        return
    lo, hi = ((_SIGNED_MIN[ret.width], _SIGNED_MAX[ret.width])
              if ret.is_int_signed() else (0, _UNSIGNED_MAX[ret.width]))
    if not (lo <= lit_value <= hi):
        raise TypeRuleError(
            f"literal {lit_value} is out of range for {ret!r}")


def _check_negative_literal_unsigned(lit_value, lit_ty: Type, ret: Type) -> None:
    """Pinned rule: a negative literal with an unsigned result is an error."""
    if (isinstance(lit_value, (int,)) and not isinstance(lit_value, bool)
            and lit_value < 0 and ret.is_int_unsigned()):
        raise TypeRuleError(
            "binary operation between an unsigned tensor and a negative "
            "literal; perform an explicit cast on one of them")


def binop_unify(lhs_ty: Type, lhs_is_literal: bool, lhs_value,
                rhs_ty: Type, rhs_is_literal: bool, rhs_value,
                div_or_mod: bool = False) -> Type:
    """The computation type of a binary operation over typed operands
    (pinned binary_op_type_checking_impl), with the literal range checks."""
    if lhs_ty.is_pointer() and rhs_ty.is_pointer():
        raise TypeRuleError("cannot operate on two pointers")
    if lhs_ty.is_pointer() and rhs_ty.is_float():
        raise TypeRuleError("pointer + float is not allowed")
    if rhs_ty.is_pointer() and lhs_ty.is_float():
        raise TypeRuleError("float + pointer is not allowed")
    if lhs_ty.is_pointer() or rhs_ty.is_pointer():
        # pointer + int is legal; typed by the pointer side (ptradd)
        return lhs_ty if lhs_ty.is_pointer() else rhs_ty
    ret = computation_type(lhs_ty, lhs_is_literal, rhs_ty, rhs_is_literal,
                           div_or_mod)
    if lhs_is_literal:
        _check_negative_literal_unsigned(lhs_value, lhs_ty, ret)
        _check_literal_range(lhs_value, lhs_ty, ret)
    if rhs_is_literal:
        _check_negative_literal_unsigned(rhs_value, rhs_ty, ret)
        _check_literal_range(rhs_value, rhs_ty, ret)
    return ret


def div_unify(lhs_ty, lhs_is_literal, lhs_value, rhs_ty, rhs_is_literal,
              rhs_value) -> Type:
    """True division unification (pinned div): the / % exception applies."""
    return binop_unify(lhs_ty, lhs_is_literal, lhs_value,
                       rhs_ty, rhs_is_literal, rhs_value, div_or_mod=True)


# ---------------------------------------------------------------------------
# convert / bitcast legality (distinct constructs)
# ---------------------------------------------------------------------------

def convert_ok(src: Type, dst: Type) -> bool:
    """Value conversion: numeric to numeric, never pointer."""
    return src.is_numeric() and dst.is_numeric() and src != dst


def bitcast_ok(src: Type, dst: Type) -> bool:
    """Bit-level reinterpretation: equal width, different type."""
    return (src.bitwidth() == dst.bitwidth() and src != dst
            and not src.is_pointer() and not dst.is_pointer())
