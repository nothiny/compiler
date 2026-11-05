"""Meta-tier specialization identity and constexpr folding
(FE-COMPILE-TIME-VS-RUNTIME, MECH-COMPILE-ONCE-PER-SPECIALIZATION).

The unit of compilation is (kernel, specialization key) at the corpus's
declared *meta* tier: source path + kernel name + per-pointer device dtype
(``pointer_dtypes`` overrides win) + per-scalar Triton specialization class
(int: ==1 / divisible-by-16 / other; float: dtype; bool: value), honoring
``do_not_specialize`` / ``do_not_specialize_on_alignment`` + every constexpr
in ``meta``/``launch_meta`` (for ``@triton.autotune`` operators, the
*deterministically chosen* first config's constexprs; the choice is
correctness-neutral).  Shapes, grid values, buffer contents and scalar
values are runtime and never baked: only value *classes* enter the key.

Constexpr folding: ``tl.constexpr`` conditions, dtype predicates
(``is_floating()``, ``is_int_signed()``, ``is_int_unsigned()``,
``int_bitwidth``, ``ptr.type.element_ty``, ``x.dtype.element_ty``) and dead
dispatch branches (the 16 ``tl.float64`` branches no declared case dtype
exercises) fold at specialization.  Every folded comparison is *evaluated*
and recorded (``FoldRecord``): folding never skips the evaluation.
"""
from __future__ import annotations

import ast
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from a100c.frontend import types as ftypes
from a100c.frontend.source import (AutotuneConfig, FrontendError,
                                   OperatorSource)
from a100c.ir import tir

__all__ = [
    "DTypeValue", "TypeObject", "RuntimeValue", "TlNamespace",
    "NOT_CONSTEXPR", "FoldRecord", "ConstexprEnv", "Specialization",
    "specialize", "identity", "chosen_autotune_config", "py_scalar",
]


# ---------------------------------------------------------------------------
# Constexpr-domain values
# ---------------------------------------------------------------------------

_TYPE_NAMES = {
    tir.INT1: "int1", tir.INT8: "int8", tir.INT16: "int16",
    tir.INT32: "int32", tir.INT64: "int64",
    tir.UINT8: "uint8", tir.UINT16: "uint16", tir.UINT32: "uint32",
    tir.UINT64: "uint64",
    tir.FLOAT16: "float16", tir.BFLOAT16: "bfloat16",
    tir.FLOAT32: "float32", tir.FLOAT64: "float64",
}


class DTypeValue:
    """A dtype in the constexpr domain (the value of ``tl.float32`` or of
    ``ptr.type.element_ty``)."""

    def __init__(self, ty: tir.Type):
        self.ty = ty

    @property
    def name(self) -> str:
        return _TYPE_NAMES.get(self.ty, repr(self.ty))

    def is_floating(self) -> bool:
        return self.ty.is_float()

    def is_standard_floating(self) -> bool:
        return self.ty.is_float() and self.ty is not tir.BFLOAT16

    def is_int_signed(self) -> bool:
        return self.ty.is_int_signed()

    def is_int_unsigned(self) -> bool:
        return self.ty.is_int_unsigned()

    def is_int(self) -> bool:
        return self.ty.is_int()

    def is_bool(self) -> bool:
        return self.ty.is_bool()

    def __eq__(self, other):
        # dtype equality (the pinned ``x.dtype == tl.uint32`` dispatch --
        # T013 found the missing __eq__ folding every such compare to
        # False, which routed fused_exponential's uniform conversion into
        # the dead 64-bit branch)
        if isinstance(other, DTypeValue):
            return self.ty == other.ty
        if isinstance(other, TypeObject):
            return self.ty == other._element
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        return result if result is NotImplemented else not result

    @property
    def int_bitwidth(self) -> int:
        if not self.ty.is_int():
            raise FrontendError("<dtype>", 0, 0, "int_bitwidth",
                                f"int_bitwidth of non-integer dtype "
                                f"{self.name}")
        return self.ty.width

    @property
    def primitive_bitwidth(self) -> int:
        # the pinned tl.dtype.primitive_bitwidth (the bit width of the
        # primitive storage unit; equal to the width for every standard
        # dtype -- the corpus's order-key bit-trick reads it on the
        # element dtype to size a uint mask)
        return self.ty.width

    def __eq__(self, other) -> bool:
        return isinstance(other, DTypeValue) and other.ty == self.ty

    def __hash__(self) -> int:
        return hash(("dtype", self.ty))

    def __repr__(self) -> str:
        return f"tl.{self.name}"


class TypeObject:
    """The value of ``ptr.type`` / ``tensor.dtype`` in the constexpr domain."""

    def __init__(self, element_ty: tir.Type, is_pointer: bool):
        self._element = element_ty
        self._is_pointer = is_pointer

    @property
    def element_ty(self) -> DTypeValue:
        return DTypeValue(self._element)

    @property
    def is_pointer(self) -> bool:
        return self._is_pointer

    def __eq__(self, other):
        if isinstance(other, DTypeValue):
            return self._element == other.ty
        if isinstance(other, TypeObject):
            return (self._element == other._element
                    and self._is_pointer == other._is_pointer)
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        return result if result is NotImplemented else not result

    def __repr__(self) -> str:
        return ("*" if self._is_pointer else "") + repr(self._element)


class RuntimeValue:
    """A runtime symbol: its value is never baked; its type is known so
    dtype predicates on it still fold."""

    def __init__(self, name: str, ty: tir.Type, shape: tir.Shape = ()):
        self.name = name
        self.type = ty
        self.shape = shape

    def __repr__(self) -> str:
        return f"<runtime {self.name}:{self.type!r}>"


class _ConstexprMarker:
    """The ``tl.constexpr`` callable itself."""

    def __call__(self, value):
        return value

    def __repr__(self) -> str:  # pragma: no cover
        return "tl.constexpr"


class _DTypeConstructor:
    """The ``tl.dtype`` callable in the constexpr domain: constructs a
    dtype from its name (the pinned ``dtype(name)`` registry lookup; the
    corpus's ``tl.dtype(f'uint{nbits}')`` order-key form).  An unknown
    name raises -- the evaluator then declines the fold and the lowering
    handler refuses with a located diagnostic."""

    def __call__(self, name):
        from a100c.frontend import types as ftypes
        if isinstance(name, DTypeValue):
            return name
        if not isinstance(name, str):
            raise FrontendError("<dtype>", 0, 0, "tl.dtype",
                                f"tl.dtype(name) requires a dtype name "
                                f"string, got {name!r}")
        try:
            return DTypeValue(ftypes.dtype_by_name(name))
        except ftypes.TypeRuleError as exc:
            raise FrontendError("<dtype>", 0, 0, "tl.dtype",
                                exc.message) from None

    def __repr__(self) -> str:  # pragma: no cover
        return "tl.dtype"


class _PropagateNanNamespace:
    """``tl.PropagateNan`` in the constexpr domain (T013: the
    maximum/minimum NaN policy selector folds to its member name)."""

    def __getattr__(self, name):
        if name in ("ALL", "NONE"):
            return f"PropagateNan.{name}"
        return NOT_CONSTEXPR


class TlNamespace:
    """The ``tl`` name in constexpr evaluation: dtype constants and the
    ``tl.constexpr`` wrapper only.  Anything else on ``tl`` is not
    constexpr-foldable (it is a runtime construct for the lowering to
    classify against the declared surface)."""

    def __init__(self):
        self.PropagateNan = _PropagateNanNamespace()
        self.constexpr = _ConstexprMarker()
        self.dtype = _DTypeConstructor()
        self._dtypes = {n: DTypeValue(t) for t, n in _TYPE_NAMES.items()}
        # dtype aliases that appear in the pinned triton.language
        self._dtypes["fp16"] = DTypeValue(tir.FLOAT16)
        self._dtypes["fp32"] = DTypeValue(tir.FLOAT32)
        self._dtypes["fp64"] = DTypeValue(tir.FLOAT64)
        self._dtypes["bf16"] = DTypeValue(tir.BFLOAT16)

    def getattr(self, name: str):
        if name in self._dtypes:
            return self._dtypes[name]
        if name == "constexpr":
            return self.constexpr
        if name == "dtype":
            return self.dtype
        if name == "PropagateNan":
            return self.PropagateNan
        return NOT_CONSTEXPR


class _NotConstexpr:
    """Sentinel: the expression depends on runtime values."""

    def __repr__(self) -> str:  # pragma: no cover
        return "<not-constexpr>"


NOT_CONSTEXPR = _NotConstexpr()

#: Python builtins the tracer evaluates at trace time on constexpr values
#: (exactly what stock Triton does with plain Python calls in kernel source)
_TRACE_BUILTINS = {
    "float": float, "int": int, "bool": bool, "str": str, "len": len,
    "min": min, "max": max, "abs": abs, "round": round,
}


# ---------------------------------------------------------------------------
# Fold record
# ---------------------------------------------------------------------------

@dataclass
class FoldedComparison:
    text: str
    left: str
    right: str
    result: object


@dataclass
class FoldedBranch:
    text: str
    condition: str
    taken: str
    line: int


@dataclass
class FoldRecord:
    """Every comparison the folding evaluated, and every branch it decided
    (the folded comparison is still evaluated during specialization)."""
    comparisons: List[FoldedComparison] = field(default_factory=list)
    branches: List[FoldedBranch] = field(default_factory=list)

    def record_comparison(self, node: ast.AST, left, right, result) -> None:
        self.comparisons.append(FoldedComparison(
            text=_safe_unparse(node), left=repr(left), right=repr(right),
            result=result))

    def record_branch(self, node: ast.AST, condition, taken: str) -> None:
        self.branches.append(FoldedBranch(
            text=_safe_unparse(node), condition=repr(condition), taken=taken,
            line=getattr(node, "lineno", 0)))

    def float64_comparisons(self) -> List[FoldedComparison]:
        return [c for c in self.comparisons if "float64" in c.text]


def _safe_unparse(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except Exception:  # pragma: no cover
        return type(node).__name__


# ---------------------------------------------------------------------------
# Constexpr evaluation
# ---------------------------------------------------------------------------

class ConstexprEnv:
    """Evaluates expressions in the constexpr domain.

    ``values`` maps names to constexpr values (int/float/bool/str/tuple/
    DTypeValue/TypeObject), RuntimeValue symbols, or the TlNamespace.
    An expression that touches a runtime value evaluates to NOT_CONSTEXPR.
    """

    def __init__(self, fold: Optional[FoldRecord] = None):
        self.values: Dict[str, Any] = {"tl": TlNamespace()}
        self.fold = fold if fold is not None else FoldRecord()

    def evaluate(self, node: ast.AST, path: str = "<kernel>"):
        """Evaluate one expression; NOT_CONSTEXPR when it is runtime."""
        try:
            result = self._eval(node, path)
        except FrontendError as exc:
            if exc.line == 0 and getattr(node, "lineno", None):
                # re-locate a placeholder diagnostic at the expression
                raise FrontendError(path, node.lineno,
                                    (node.col_offset or 0) + 1,
                                    exc.construct, exc.message) from None
            raise
        except Exception:
            return NOT_CONSTEXPR
        if isinstance(result, (RuntimeValue, _NotConstexpr)):
            return NOT_CONSTEXPR
        return result

    # -- internals ----------------------------------------------------------
    def _eval(self, node: ast.AST, path: str):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in self.values:
                return self.values[node.id]
            return NOT_CONSTEXPR
        if isinstance(node, ast.Attribute):
            base = self._eval(node.value, path)
            if base is NOT_CONSTEXPR or base is None:
                return NOT_CONSTEXPR
            if isinstance(base, TlNamespace):
                return base.getattr(node.attr)
            if isinstance(base, (TypeObject,)):
                if node.attr in ("type", "dtype"):
                    return base
                if node.attr == "element_ty":
                    return base.element_ty
                # the dtype members fold on ``x.dtype`` too (the pinned
                # tensor's .dtype IS a tl.dtype: x.dtype.primitive_bitwidth,
                # the corpus's order-key form)
                elem = base.element_ty
                if node.attr == "int_bitwidth":
                    return elem.int_bitwidth
                if node.attr == "primitive_bitwidth":
                    return elem.primitive_bitwidth
                if node.attr in ("is_floating", "is_standard_floating",
                                 "is_int_signed", "is_int_unsigned", "is_int",
                                 "is_bool"):
                    return getattr(elem, node.attr)
                return NOT_CONSTEXPR
            if isinstance(base, DTypeValue):
                if node.attr == "int_bitwidth":
                    return base.int_bitwidth
                if node.attr == "primitive_bitwidth":
                    return base.primitive_bitwidth
                if node.attr in ("is_floating", "is_standard_floating",
                                 "is_int_signed", "is_int_unsigned", "is_int",
                                 "is_bool"):
                    return getattr(base, node.attr)
                return NOT_CONSTEXPR
            if isinstance(base, RuntimeValue):
                # ptr.type / tensor.dtype fold from the runtime type
                if node.attr in ("type", "dtype"):
                    return TypeObject(base.type.pointee if
                                      base.type.is_pointer() else base.type,
                                      base.type.is_pointer())
                if node.attr == "shape":
                    # the pinned constexpr shape tuple: block extents are
                    # compile-time even though the value is not (a
                    # symbolic extent declines the fold, never bakes)
                    vals = []
                    for e in (base.shape or ()):
                        v = getattr(e, "value", e)
                        if isinstance(v, bool) or not isinstance(v, int):
                            return NOT_CONSTEXPR
                        vals.append(int(v))
                    return tuple(vals)
                return NOT_CONSTEXPR
            if hasattr(base, node.attr) and not node.attr.startswith("_"):
                attr = getattr(base, node.attr)
                if callable(attr) or isinstance(
                        attr, (int, float, bool, str, tuple, list)):
                    return attr
            return NOT_CONSTEXPR
        if isinstance(node, ast.BinOp):
            left = self._eval(node.left, path)
            right = self._eval(node.right, path)
            if left is NOT_CONSTEXPR or right is NOT_CONSTEXPR:
                return NOT_CONSTEXPR
            if isinstance(left, (DTypeValue, TypeObject)) or \
                    isinstance(right, (DTypeValue, TypeObject)):
                return NOT_CONSTEXPR
            return self._binop(node.op, left, right)
        if isinstance(node, ast.UnaryOp):
            v = self._eval(node.operand, path)
            if v is NOT_CONSTEXPR:
                return NOT_CONSTEXPR
            return self._unaryop(node.op, v)
        if isinstance(node, ast.BoolOp):
            vals = [self._eval(v, path) for v in node.values]
            # a runtime symbol must never leak through Python and/or:
            # ``below or above`` on runtime booleans once folded to the
            # truthiness of the RuntimeValue objects themselves (True),
            # silently baking a constant (sym_constrain_range, T016
            # census).  Runtime operands decline the fold; the lowering's
            # BoolOp branch refuses them with a located diagnostic.
            if any(v is NOT_CONSTEXPR or isinstance(v, RuntimeValue)
                   for v in vals):
                return NOT_CONSTEXPR
            if isinstance(node.op, ast.And):
                return all(vals)
            return any(vals)
        if isinstance(node, ast.Compare):
            left = self._eval(node.left, path)
            if left is NOT_CONSTEXPR:
                return NOT_CONSTEXPR
            for op, comparator in zip(node.ops, node.comparators):
                right = self._eval(comparator, path)
                if right is NOT_CONSTEXPR:
                    return NOT_CONSTEXPR
                # a runtime value must never fold a comparison: object
                # identity would silently answer == and != (probe-found on
                # 'if pid == 0:', which folded False and dropped the arm)
                if isinstance(left, RuntimeValue) or \
                        isinstance(right, RuntimeValue):
                    return NOT_CONSTEXPR
                result = self._compare(op, left, right)
                # the folded comparison is still evaluated and recorded
                self.fold.record_comparison(node, left, right, result)
                if not result:
                    return False
                left = right
            return True
        if isinstance(node, ast.IfExp):
            cond = self._eval(node.test, path)
            if cond is NOT_CONSTEXPR:
                return NOT_CONSTEXPR
            taken = "body" if cond else "orelse"
            self.fold.record_branch(node, cond, taken)
            return self._eval(getattr(node, taken), path)
        if isinstance(node, ast.Call):
            func = self._eval(node.func, path)
            if func is NOT_CONSTEXPR and isinstance(node.func, ast.Name) \
                    and node.func.id in _TRACE_BUILTINS:
                # Python builtins the tracer runs at trace time
                # (float("-inf"), int(x), len(shape), min/max of consts...)
                func = _TRACE_BUILTINS[node.func.id]
            if func is NOT_CONSTEXPR:
                return NOT_CONSTEXPR
            args = [self._eval(a, path) for a in node.args]
            if any(a is NOT_CONSTEXPR for a in args):
                return NOT_CONSTEXPR
            if callable(func):
                try:
                    return func(*args)
                except Exception:
                    return NOT_CONSTEXPR
            return NOT_CONSTEXPR
        if isinstance(node, ast.Subscript):
            base = self._eval(node.value, path)
            if base is NOT_CONSTEXPR:
                return NOT_CONSTEXPR
            index = self._eval(node.slice, path) \
                if not isinstance(node.slice, ast.Slice) else NOT_CONSTEXPR
            if index is NOT_CONSTEXPR:
                return NOT_CONSTEXPR
            try:
                return base[index]
            except Exception:
                return NOT_CONSTEXPR
        if isinstance(node, (ast.Tuple, ast.List)):
            items = [self._eval(e, path) for e in node.elts]
            if any(i is NOT_CONSTEXPR for i in items):
                return NOT_CONSTEXPR
            return tuple(items)
        if isinstance(node, ast.JoinedStr):
            # an f-string over constexpr values (the corpus's
            # ``tl.dtype(f'uint{nbits}')`` order-key form); each formatted
            # value must itself be compile-time
            parts = []
            for value in node.values:
                if isinstance(value, ast.Constant):
                    parts.append(str(value.value))
                    continue
                if not isinstance(value, ast.FormattedValue):
                    return NOT_CONSTEXPR
                inner = self._eval(value.value, path)
                if inner is NOT_CONSTEXPR:
                    return NOT_CONSTEXPR
                if value.format_spec is not None:
                    spec = self._eval(value.format_spec, path)
                    if spec is NOT_CONSTEXPR:
                        return NOT_CONSTEXPR
                    try:
                        text = format(inner, spec)
                    except Exception:
                        return NOT_CONSTEXPR
                else:
                    text = str(inner)
                if value.conversion in (ord("r"), ord("a")):
                    text = repr(inner) if value.conversion == ord("r") \
                        else ascii(inner)
                parts.append(text)
            return "".join(parts)
        return NOT_CONSTEXPR

    @staticmethod
    def _binop(op, left, right):
        if isinstance(op, ast.Add):
            return left + right
        if isinstance(op, ast.Sub):
            return left - right
        if isinstance(op, ast.Mult):
            return left * right
        if isinstance(op, ast.Div):
            return left / right
        if isinstance(op, ast.FloorDiv):
            return left // right
        if isinstance(op, ast.Mod):
            return left % right
        if isinstance(op, ast.Pow):
            return left ** right
        if isinstance(op, ast.BitAnd):
            return left & right
        if isinstance(op, ast.BitOr):
            return left | right
        if isinstance(op, ast.BitXor):
            return left ^ right
        if isinstance(op, ast.LShift):
            return left << right
        if isinstance(op, ast.RShift):
            return left >> right
        raise ValueError(f"unsupported binop {op}")

    @staticmethod
    def _unaryop(op, v):
        if isinstance(op, ast.USub):
            return -v
        if isinstance(op, ast.UAdd):
            return +v
        if isinstance(op, ast.Invert):
            return ~v
        if isinstance(op, ast.Not):
            return not v
        raise ValueError(f"unsupported unaryop {op}")

    @staticmethod
    def _compare(op, left, right):
        # dtype equality is identity of the represented type
        if isinstance(op, ast.Eq):
            return left == right
        if isinstance(op, ast.NotEq):
            return left != right
        if isinstance(op, ast.Lt):
            return left < right
        if isinstance(op, ast.LtE):
            return left <= right
        if isinstance(op, ast.Gt):
            return left > right
        if isinstance(op, ast.GtE):
            return left >= right
        if isinstance(op, (ast.In, ast.NotIn, ast.Is, ast.IsNot)):
            return NOT_CONSTEXPR
        raise ValueError(f"unsupported comparison {op}")


# ---------------------------------------------------------------------------
# Specialization
# ---------------------------------------------------------------------------

def _is_pointer_arg(value) -> bool:
    return hasattr(value, "dtype") and getattr(value, "ndim", 0) > 0


def _py_scalar(value):
    """Normalize a numpy scalar to its Python equivalent (constexpr values
    flow through Python arithmetic; np.int32(64) is an int to the tracer)."""
    import numpy as np

    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    return value


#: public alias (the lowering normalizes constexpr values through it)
py_scalar = _py_scalar


def config_has(source: OperatorSource, name: str) -> bool:
    """Does the chosen autotune config supply this constexpr?"""
    config = chosen_autotune_config(source)
    return config is not None and name in config.constexprs


def config_value(source: OperatorSource, name: str):
    config = chosen_autotune_config(source)
    return None if config is None else config.constexprs.get(name)


def chosen_autotune_config(source: OperatorSource) -> Optional[AutotuneConfig]:
    """The deterministically chosen config: the FIRST declared config.
    The choice is correctness-neutral and independent of runtime values
    (never re-tuned per key), so it never splits one operator's cases."""
    if not source.autotune_configs:
        return None
    return source.autotune_configs[0]


@dataclass
class Specialization:
    """Everything the compiler may know about one compilation unit+case."""
    source: OperatorSource
    pointer_dtypes: Dict[str, str]          # param -> device dtype name
    pointer_types: Dict[str, tir.Type]      # param -> pointee type
    scalar_types: Dict[str, tir.Type]       # param -> runtime scalar type
    scalar_classes: Dict[str, Tuple]        # param -> class (dns excluded)
    scalar_classes_full: Dict[str, Tuple]   # without dns exclusion (record)
    constexpr_values: Dict[str, object]     # ALL meta/launch_meta entries
    param_constexprs: Dict[str, object]     # constexpr params only
    chosen_config: Optional[AutotuneConfig]
    identity: str
    signature: tuple
    fold: FoldRecord = field(default_factory=FoldRecord)

    def env(self) -> ConstexprEnv:
        """The constexpr environment for this specialization: constexpr
        params, module-level constexpr globals and dtype-visible runtime
        symbols."""
        env = ConstexprEnv(self.fold)
        for name, value in self.source.constexpr_globals.items():
            env.values[name] = _wrap_constexpr(value)
        for p in self.source.params:
            if p.is_constexpr:
                value = self.param_constexprs.get(p.name)
                env.values[p.name] = _wrap_constexpr(value)
            elif p.name in self.pointer_types:
                pointee = self.pointer_types[p.name]
                env.values[p.name] = RuntimeValue(
                    p.name, tir.Type.pointer(pointee))
            elif p.name in self.scalar_types:
                env.values[p.name] = RuntimeValue(p.name,
                                                  self.scalar_types[p.name])
        return env


def _wrap_constexpr(value):
    value = _py_scalar(value)
    if isinstance(value, str):
        ty = ftypes.DTYPE_BY_NAME.get(value)
        if ty is not None:
            return DTypeValue(ty)
        return value
    if isinstance(value, bool) or isinstance(value, (int, float)):
        return value
    if isinstance(value, (list, tuple)):
        return tuple(value)
    # a meta/launch_meta constexpr may carry the reference triton's own
    # dtype object (``meta = {"OUT_DTYPE": tl.float32}`` -- the case
    # builder puts the live constant in the payload).  Recognize it by
    # its type shape, never by importing the reference environment, and
    # map it through the declared dtype surface; an off-surface name
    # (fp8, ...) passes through so the *use* refuses with a located
    # diagnostic instead of the wrap silently inventing a type.
    if (type(value).__module__ == "triton.language.core"
            and type(value).__name__ == "dtype"):
        ty = ftypes.DTYPE_BY_NAME.get(getattr(value, "name", None))
        if ty is not None:
            return DTypeValue(ty)
    return value


def specialize(source: OperatorSource, case: dict) -> Specialization:
    """Build the specialization of ``source`` for one case payload.

    Only type-level information is read from the case: array dtypes
    (with ``pointer_dtypes`` overrides), scalar types and value classes,
    and the constexpr tables.  Buffer contents and scalar values are never
    retained.
    """
    args = case.get("args") or {}
    if not isinstance(args, dict):
        raise FrontendError(source.path, 1, 0, "case",
                            "case['args'] must be a mapping")
    overrides = case.get("pointer_dtypes") or {}
    meta = case.get("meta") or {}
    launch_meta = case.get("launch_meta") or {}

    param_names = source.param_names()
    # Extra case arguments (case-layer values the runner never binds to the
    # kernel, e.g. argmin_kernel_contiguous's N_pre) stay part of the
    # identity signature (the corpus meta tier signs every case argument)
    # but are not typed for the lowering.
    for p in source.params:
        if p.is_constexpr:
            if (p.name not in meta and p.name not in args
                    and not (source.is_autotune and config_has(source, p.name))
                    and not p.has_default):
                raise FrontendError(
                    source.path, _param_line(source, p.name), 1, p.name,
                    f"constexpr parameter {p.name!r} has no value in "
                    "case['meta'], the chosen autotune config or its "
                    "default")
        elif p.name not in args:
            raise FrontendError(
                source.path, _param_line(source, p.name), 1, p.name,
                f"parameter {p.name!r} has no argument in case['args']")

    # -- identity-level signatures: computed over the case arguments exactly
    #    like the corpus's declared meta tier (identity.py), so the induced
    #    equivalence matches it; do_not_specialize names are excluded.
    pointer_dtypes: Dict[str, str] = {}
    scalar_classes: Dict[str, Tuple] = {}
    scalar_classes_full: Dict[str, Tuple] = {}
    for name, value in args.items():
        if _is_pointer_arg(value):
            dtype_name = overrides.get(name) or str(value.dtype)
            pointer_dtypes[name] = dtype_name
        else:
            full = ftypes.scalar_class(value)
            scalar_classes_full[name] = full
            if name in source.do_not_specialize:
                continue                    # excluded from the class entirely
            if name in source.do_not_specialize_on_alignment:
                # ==1 still applies; the div-16 alignment fact does not
                kind, cls = full
                scalar_classes[name] = ((("int", "other") if cls == "div16"
                                          else full)
                                        if kind == "int" else full)
            else:
                scalar_classes[name] = full

    # -- lowering-level typing: kernel parameters only
    pointer_types: Dict[str, tir.Type] = {}
    scalar_types: Dict[str, tir.Type] = {}
    param_constexprs: Dict[str, object] = {}
    for p in source.params:
        if p.is_constexpr:
            if p.name in meta:
                param_constexprs[p.name] = _py_scalar(meta[p.name])
            elif p.name in args:
                param_constexprs[p.name] = _py_scalar(args[p.name])
            elif config_has(source, p.name):
                # the runner's autotune path: the chosen config supplies
                # the constexpr the case meta does not carry
                param_constexprs[p.name] = _py_scalar(
                    config_value(source, p.name))
            elif p.has_default:
                param_constexprs[p.name] = _py_scalar(p.default)
            continue
        value = args[p.name]
        if _is_pointer_arg(value):
            dtype_name = pointer_dtypes[p.name]
            try:
                pointee = ftypes.dtype_by_name(dtype_name)
            except ftypes.TypeRuleError as exc:
                raise FrontendError(
                    source.path, _param_line(source, p.name), 1, p.name,
                    f"pointer dtype {dtype_name!r} is not in the declared "
                    f"dtype surface: {exc.message}") from None
            pointer_types[p.name] = pointee
        else:
            try:
                scalar_types[p.name] = ftypes.scalar_arg_type(value)
            except ftypes.TypeRuleError as exc:
                raise FrontendError(
                    source.path, _param_line(source, p.name), 1, p.name,
                    f"cannot type runtime scalar: {exc.message}") from None

    # the full constexpr view for the identity (mirrors the corpus tier:
    # every entry of meta and launch_meta, plus the chosen autotune config)
    constexpr_values: Dict[str, object] = {}
    for table in ("meta", "launch_meta"):
        for key, value in (case.get(table) or {}).items():
            constexpr_values[f"{table}.{key}"] = value
    config = chosen_autotune_config(source)
    if config is not None:
        for key, value in config.constexprs.items():
            constexpr_values[f"config.{key}"] = value
        if config.num_warps is not None:
            constexpr_values["config.num_warps"] = config.num_warps
        if config.num_stages is not None:
            constexpr_values["config.num_stages"] = config.num_stages

    sig = _signature(source, pointer_dtypes, scalar_classes, constexpr_values)
    ident = _identity_hash(sig)
    return Specialization(
        source=source,
        pointer_dtypes=pointer_dtypes,
        pointer_types=pointer_types,
        scalar_types=scalar_types,
        scalar_classes=scalar_classes,
        scalar_classes_full=scalar_classes_full,
        constexpr_values=constexpr_values,
        param_constexprs=param_constexprs,
        chosen_config=config,
        identity=ident,
        signature=sig,
    )


def _param_line(source: OperatorSource, name: str) -> int:
    if source.kernel_ast is not None:
        for a in source.kernel_ast.args.args:
            if a.arg == name:
                return a.lineno
    return 1


def _signature(source: OperatorSource, pointer_dtypes: Dict[str, str],
               scalar_classes: Dict[str, Tuple],
               constexpr_values: Dict[str, object]) -> tuple:
    """Everything that can change the emitted binary (the corpus meta tier:
    source, kernel, pointers, scalar classes, constexprs -- never shapes,
    grids or values)."""
    ptr_sig = tuple(sorted(pointer_dtypes.items()))
    scalar_sig = tuple(sorted(scalar_classes.items()))
    constexpr_sig = tuple(
        sorted((k, _constexpr_repr(v)) for k, v in constexpr_values.items()))
    return (("source", source.rel_path),
            ("kernel", source.kernel_name),
            ("ptr", ptr_sig),
            ("scalar", scalar_sig),
            ("constexpr", constexpr_sig))


def _constexpr_repr(value) -> str:
    if isinstance(value, list):
        value = tuple(value)
    return repr(value)


def _identity_hash(sig: tuple) -> str:
    blob = json.dumps([list(part) for part in sig], sort_keys=True,
                      default=str).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def identity(spec: Specialization) -> str:
    """The stable identity string of one specialization."""
    return spec.identity
