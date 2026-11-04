"""TIR (tir/v1): typed block-tensor dataflow with structured control flow.

The data structures carry, with a named owner for every check
(IR-SEMANTIC-FIDELITY, COMPILER_ARCHITECTURE.md 2.1):

======================  ============================================  ==========================
source property         carrier in TIR                                who checks
======================  ============================================  ==========================
element width           ``Type.width`` on every value                 TIR verifier; type rules
signedness              ``Type.signed`` (separate from width)         TIR verifier; legalisation
conversion vs bit       distinct ops ``convert`` / ``bitcast``        verifier (no identity
reinterpretation        (never one cast)                              folding across them)
mask + disabled-        ``mask`` operand plus a *declared*            verifier (masked op
position default        ``masked_default`` (value / undef /           without default is
                        no-access) on load/store                     malformed); lowering
shape/stride/layout     ``Shape`` with per-axis extent and a          shape inference; verifier
                        ``broadcast`` flag distinct from real extent
index math width        pointer offsets typed i32/i64                verifier; lowering
compile-time vs         constexpr values folded away by the          specialization stage
runtime boundary        frontend; runtime scalars/pointers stay
                        symbolic values
structured groups       values carry rank/extent                      verifier; tile planner
control flow            structured regions (``If``/``Loop``) with      verifier (carried value
                        explicit join parameters                      without join malformed)
======================  ============================================  ==========================

Broadcast flags: an extent flagged ``broadcast`` exists only by replication
(the value's lanes along it are copies of a single source lane); a real
extent is backed by distinct lanes.  Memory ops consume shapes as storage
footprints, so their pointer (and stored-value) operands must have real
extents -- converting a broadcast extent into a real one requires an
explicit ``realize`` op.  The verifier rejects a broadcast extent consumed
as a real extent.

The verifier rejects one hand-built malformed module per invariant class
(use-before-definition, type contradiction, masked operation without declared
default, broadcast extent consumed as real extent, carried value without
join) and accepts the real frontend's output for valid kernels
(IR-WELLFORMED).
"""
from __future__ import annotations

from typing import Optional, Sequence, Tuple, Union

__all__ = [
    "SrcLoc", "Type", "Shape", "Extent", "Sym", "Value", "Op", "Block",
    "If", "Loop", "Function", "Module", "MaskedDefault", "TirError",
    "Invariant", "verify_module", "verify", "unify_shapes", "value_shape",
    "is_real", "real_shape",
]

# ---------------------------------------------------------------------------
# Source attribution
# ---------------------------------------------------------------------------


class SrcLoc:
    """Location of the source construct that produced a TIR node."""

    __slots__ = ("path", "line", "col")

    def __init__(self, path: str, line: int, col: int):
        self.path = path
        self.line = line
        self.col = col

    def __str__(self) -> str:
        return f"{self.path}:{self.line}:{self.col}"

    def __repr__(self) -> str:
        return f"SrcLoc({self})"


# ---------------------------------------------------------------------------
# Types
# ----------------------------------------------------------------===========


class Type:
    """Scalar element type: width and signedness are separate carriers.

    ``kind`` is one of ``int``, ``uint``, ``float``, ``bool``, ``pointer``.
    Pointer types carry their pointee type in ``pointee``.  ``name`` keeps
    float16 and bfloat16 distinct at the same width.
    """

    __slots__ = ("kind", "width", "name", "pointee")

    def __init__(self, kind: str, width: int, name: Optional[str] = None,
                 pointee: "Optional[Type]" = None):
        assert kind in ("int", "uint", "float", "bool", "pointer")
        self.kind = kind
        self.width = width
        self.name = name or self._default_name(kind, width)
        self.pointee = pointee

    @staticmethod
    def _default_name(kind: str, width: int) -> str:
        prefix = {"int": "i", "uint": "u", "float": "f", "bool": "i",
                  "pointer": "ptr"}[kind]
        return f"{prefix}{width}" if kind != "bool" else "i1"

    # -- constructors ------------------------------------------------------
    @staticmethod
    def bool_() -> "Type":
        return Type("bool", 1, "i1")

    @staticmethod
    def int(width: int) -> "Type":
        return Type("int", width)

    @staticmethod
    def uint(width: int) -> "Type":
        return Type("uint", width)

    @staticmethod
    def float(width: int, name: Optional[str] = None) -> "Type":
        return Type("float", width, name)

    @staticmethod
    def pointer(pointee: "Type") -> "Type":
        return Type("pointer", 64, "ptr", pointee)

    # -- predicates --------------------------------------------------------
    @property
    def signed(self) -> bool:
        """Signedness, separate from width."""
        return self.kind in ("int", "pointer")

    def is_bool(self) -> bool:
        return self.kind == "bool"

    def is_int(self) -> bool:
        return self.kind in ("int", "uint")

    def is_int_signed(self) -> bool:
        return self.kind == "int"

    def is_int_unsigned(self) -> bool:
        return self.kind == "uint"

    def is_float(self) -> bool:
        return self.kind == "float"

    def is_pointer(self) -> bool:
        return self.kind == "pointer"

    def is_index(self) -> bool:
        """Index arithmetic carriers: i32/i64 (bool is not index arithmetic)."""
        return self.kind == "int" and self.width in (32, 64)

    def is_numeric(self) -> bool:
        return self.kind in ("int", "uint", "float", "bool")

    def bitwidth(self) -> int:
        return self.width

    def __eq__(self, other) -> bool:
        if not isinstance(other, Type):
            return NotImplemented
        return (self.kind == other.kind and self.width == other.width
                and self.name == other.name and self.pointee == other.pointee)

    def __hash__(self) -> int:
        return hash((self.kind, self.width, self.name))

    def __repr__(self) -> str:
        if self.kind == "pointer":
            return f"*{self.pointee!r}"
        return self.name


INT1 = Type.bool_()
INT8 = Type.int(8)
INT16 = Type.int(16)
INT32 = Type.int(32)
INT64 = Type.int(64)
UINT8 = Type.uint(8)
UINT16 = Type.uint(16)
UINT32 = Type.uint(32)
UINT64 = Type.uint(64)
FLOAT16 = Type.float(16, "fp16")
BFLOAT16 = Type.float(16, "bf16")
FLOAT32 = Type.float(32, "fp32")
FLOAT64 = Type.float(64, "fp64")

# ---------------------------------------------------------------------------
# Shapes
# ----------------------------------------------------------------===========


class Sym:
    """A runtime-symbolic extent (never a baked value)."""

    __slots__ = ("name",)

    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other) -> bool:
        return isinstance(other, Sym) and other.name == self.name

    def __hash__(self) -> int:
        return hash(("sym", self.name))

    def __repr__(self) -> str:
        return f"?{self.name}"


ExtentLike = Union[int, Sym]


class Extent:
    """One axis: extent value plus the broadcast flag.

    ``broadcast=True``: the extent exists only by broadcasting (the value's
    lanes along it are replicates).  ``broadcast=False``: a real extent
    backed by distinct lanes.  The flag is carried separately from the value
    so the verifier can reject a broadcast extent consumed as a real one.
    """

    __slots__ = ("value", "broadcast")

    def __init__(self, value: ExtentLike, broadcast: bool = False):
        self.value = value
        self.broadcast = broadcast

    def is_one(self) -> bool:
        return self.value == 1 and not isinstance(self.value, Sym)

    def __eq__(self, other) -> bool:
        return (isinstance(other, Extent) and other.value == self.value
                and other.broadcast == self.broadcast)

    def __hash__(self) -> int:
        return hash((self.value, self.broadcast))

    def __repr__(self) -> str:
        return f"{self.value}{'b' if self.broadcast else ''}"


Shape = Tuple[Extent, ...]


def real_shape(extents: Sequence[ExtentLike]) -> Shape:
    """A shape whose every extent is real."""
    return tuple(Extent(e, False) for e in extents)


def is_real(shape: Shape) -> bool:
    return not any(e.broadcast for e in shape)


def value_shape(shape: Shape) -> tuple:
    """The extents without the broadcast flags."""
    return tuple(e.value for e in shape)


def unify_shapes(a: Shape, b: Shape) -> Optional[Shape]:
    """Broadcast-unify two shapes (right-aligned, numpy-style per the pinned
    Triton 3.8 ``broadcast_impl_value``).

    Returns the unified shape (an axis is flagged broadcast only when BOTH
    operands' lanes replicate along it), or None when the extents disagree.
    """
    if len(a) > len(b):
        a, b = b, a
    pad = len(b) - len(a)
    out: list = []
    for i in range(len(b)):
        if i < pad:
            ea = Extent(1, True)      # implicit left-expansion of the shorter
        else:
            ea = a[i - pad]
        eb = b[i]
        if ea.value == eb.value:
            out.append(Extent(ea.value, ea.broadcast and eb.broadcast))
        elif ea.is_one():
            out.append(Extent(eb.value, eb.broadcast and True))
        elif eb.is_one():
            out.append(Extent(ea.value, ea.broadcast and True))
        else:
            return None
    return tuple(out)


# ---------------------------------------------------------------------------
# Values
# ============================================================================


class Value:
    """An SSA value: type, shape, producing op and source location."""

    __slots__ = ("vid", "name", "type", "shape", "loc", "producer")

    _next = 0

    def __init__(self, type: Type, shape: Shape, loc: Optional[SrcLoc] = None,
                 name: Optional[str] = None, producer: "Optional[Op]" = None):
        Value._next += 1
        self.vid = Value._next
        self.name = name or f"v{self.vid}"
        self.type = type
        self.shape = shape
        self.loc = loc
        self.producer = producer

    @property
    def rank(self) -> int:
        return len(self.shape)

    def __repr__(self) -> str:
        ext = ",".join(repr(e) for e in self.shape)
        return f"{self.name}:{self.type!r}[{ext}]"


# ---------------------------------------------------------------------------
# Masked-operation defaults
# ----------------------------------------------------------------===========


class MaskedDefault:
    """Declared disabled-position semantics of a masked memory op.

    A masked op MUST declare what its disabled positions do; the declaration
    is one of:

    ``VALUE``      disabled positions yield the recorded ``other`` operand
                   (``tl.load(..., other=...)``);
    ``UNDEF``      disabled positions yield an undefined value (a masked load
                   without ``other``: never zero-filled, no access happens);
    ``NO_ACCESS``  disabled positions perform no access (the only legal store
                   semantics).

    A masked op whose ``masked_default`` attribute is absent is malformed.
    """

    VALUE = "value"
    UNDEF = "undef"
    NO_ACCESS = "no-access"


# ---------------------------------------------------------------------------
# Ops
# ============================================================================

#: binary arithmetic op codes (operands pre-unified: equal types, equal
#: extent values)
BIN_ARITH = {"arith.add", "arith.sub", "arith.mul", "arith.fdiv",
             "arith.sdiv", "arith.udiv", "arith.srem", "arith.urem",
             "arith.frem"}
#: bitwise/logical op codes (integer or bool operands)
BIN_BITWISE = {"bit.and", "bit.or", "bit.xor", "bit.shl", "bit.ashr",
               "bit.lshr"}
#: comparison predicates
CMP_PREDS = {"cmp.lt", "cmp.le", "cmp.gt", "cmp.ge", "cmp.eq", "cmp.ne"}
#: unary op codes
UNARY_OPS = {"arith.neg", "arith.fneg", "logical.not", "bit.invert"}


def _and_flags(shapes: Sequence[Shape]) -> Shape:
    """Per-axis AND of broadcast flags over shapes with equal extent values."""
    if not shapes:
        return ()
    out = []
    for i in range(len(shapes[0])):
        flag = all(s[i].broadcast for s in shapes)
        out.append(Extent(shapes[0][i].value, flag))
    return tuple(out)


class Op:
    """One TIR operation: operands, attributes, results, source location."""

    def __init__(self, op: str, operands: Sequence[Value], loc: Optional[SrcLoc],
                 type: Optional[Type] = None, shape: Optional[Shape] = None,
                 attrs: Optional[dict] = None, results: int = 1):
        self.op = op
        self.operands = tuple(operands)
        self.loc = loc
        self.attrs = dict(attrs or {})
        self.results: Tuple[Value, ...] = ()
        if results:
            assert type is not None and shape is not None
            self.results = tuple(
                Value(type, shape, loc, name=None, producer=self)
                for _ in range(results))

    def result(self) -> Value:
        assert len(self.results) == 1
        return self.results[0]

    # -- factory helpers ---------------------------------------------------

    @staticmethod
    def const(value, type: Type, loc: Optional[SrcLoc] = None) -> "Op":
        op = Op("const", (), loc, type, (), attrs={"value": value})
        op.results[0].name = f"c{op.results[0].vid}"
        return op

    @staticmethod
    def program_id(axis: int, loc: Optional[SrcLoc] = None) -> "Op":
        return Op("program_id", (), loc, INT32, (), attrs={"axis": axis})

    @staticmethod
    def arange(start: int, end: int, loc: Optional[SrcLoc] = None) -> "Op":
        return Op("arange", (), loc, INT32, real_shape([end - start]),
                  attrs={"start": start, "end": end})

    @staticmethod
    def zeros(shape: Shape, type: Type, loc: Optional[SrcLoc] = None) -> "Op":
        return Op("zeros", (), loc, type, shape)

    @staticmethod
    def full(shape: Shape, value, type: Type,
             loc: Optional[SrcLoc] = None) -> "Op":
        return Op("full", (), loc, type, shape, attrs={"value": value})

    @staticmethod
    def binop(op: str, lhs: Value, rhs: Value,
              loc: Optional[SrcLoc] = None) -> "Op":
        """Result flags: lanes replicate iff both operands' lanes replicate."""
        shape = _and_flags([lhs.shape, rhs.shape])
        return Op(op, (lhs, rhs), loc, lhs.type, shape)

    @staticmethod
    def cmp(pred: str, lhs: Value, rhs: Value,
            loc: Optional[SrcLoc] = None) -> "Op":
        shape = _and_flags([lhs.shape, rhs.shape])
        return Op(pred, (lhs, rhs), loc, INT1, shape)

    @staticmethod
    def unary(op: str, operand: Value, loc: Optional[SrcLoc] = None) -> "Op":
        return Op(op, (operand,), loc, operand.type, operand.shape)

    @staticmethod
    def where(cond: Value, x: Value, y: Value,
              loc: Optional[SrcLoc] = None) -> "Op":
        shape = _and_flags([cond.shape, x.shape, y.shape])
        return Op("select.where", (cond, x, y), loc, x.type, shape)

    @staticmethod
    def convert(value: Value, type: Type, loc: Optional[SrcLoc] = None) -> "Op":
        """Value conversion (change of numeric representation)."""
        return Op("convert", (value,), loc, type, value.shape,
                  attrs={"from": value.type})

    @staticmethod
    def bitcast(value: Value, type: Type, loc: Optional[SrcLoc] = None) -> "Op":
        """Bit-level reinterpretation (width preserved, value re-read)."""
        return Op("bitcast", (value,), loc, type, value.shape,
                  attrs={"from": value.type})

    @staticmethod
    def broadcast(value: Value, shape: Shape,
                  loc: Optional[SrcLoc] = None) -> "Op":
        """Expand a value to ``shape``; expanded axes are flagged broadcast."""
        return Op("broadcast", (value,), loc, value.type, shape,
                  attrs={"from_shape": value.shape})

    @staticmethod
    def realize(value: Value, loc: Optional[SrcLoc] = None) -> "Op":
        """Materialize broadcast extents into real ones."""
        shape = tuple(Extent(e.value, False) for e in value.shape)
        return Op("realize", (value,), loc, value.type, shape)

    @staticmethod
    def ptradd(base: Value, offset: Value,
               loc: Optional[SrcLoc] = None) -> "Op":
        """Pointer + element offset (offsets are element counts, not bytes).

        Like the pinned Triton ``add`` on a pointer, the base and the offset
        are broadcast-unified by the op itself (the whole-tree address form:
        base + offsets in one expression); the result's lanes replicate only
        where both operands' lanes replicate.
        """
        assert base.type.is_pointer()
        shape = unify_shapes(base.shape, offset.shape)
        if shape is None:
            raise ValueError(
                f"ptradd cannot unify base shape "
                f"{base.shape} with offset shape {offset.shape}")
        return Op("ptradd", (base, offset), loc, base.type, shape)

    @staticmethod
    def load(ptr: Value, mask: Optional[Value], masked_default: Optional[str],
             other: Optional[Value] = None,
             loc: Optional[SrcLoc] = None) -> "Op":
        attrs: dict = {}
        if mask is not None:
            attrs["masked_default"] = masked_default
        return Op("load", tuple(v for v in (ptr, mask, other) if v is not None),
                  loc, ptr.type.pointee, ptr.shape, attrs=attrs)

    @staticmethod
    def store(ptr: Value, value: Value, mask: Optional[Value],
              masked_default: Optional[str],
              loc: Optional[SrcLoc] = None) -> "Op":
        attrs: dict = {}
        if mask is not None:
            attrs["masked_default"] = masked_default
        return Op("store", tuple(v for v in (ptr, value, mask) if v is not None),
                  loc, None, None, attrs=attrs, results=0)

    @staticmethod
    def barrier(loc: Optional[SrcLoc] = None) -> "Op":
        return Op("debug_barrier", (), loc, None, None, results=0)

    def __repr__(self) -> str:
        return f"Op({self.op})"


# ---------------------------------------------------------------------------
# Structured control flow
# ============================================================================


class Block:
    """An ordered statement list (Ops and structured control flow)."""

    def __init__(self):
        self.statements: list = []


class If:
    """Structured two-arm region with explicit join parameters.

    Values defined inside an arm are visible only inside that arm; escaping
    them requires a ``join_names`` entry whose name both arms define.  The
    verifier binds ``join_results`` (one Value per join name) which are the
    only values visible after the construct.
    """

    def __init__(self, cond: Value, loc: Optional[SrcLoc] = None):
        self.cond = cond
        self.loc = loc
        self.then = Block()
        self.els = Block()
        self.join_names: Tuple[str, ...] = ()
        self.join_results: Tuple[Value, ...] = ()


class Loop:
    """Structured loop with carried values.

    ``carried``: tuple of (name, initial Value).  The body must redefine
    every carried name; the value visible after the loop is the join of the
    body's definitions (loop-carried join).
    """

    def __init__(self, lower: Optional[Value], upper: Optional[Value],
                 step: Optional[Value], loc: Optional[SrcLoc] = None):
        self.lower = lower
        self.upper = upper
        self.step = step
        self.loc = loc
        self.body = Block()
        self.carried: Tuple[Tuple[str, Value], ...] = ()
        self.join_results: Tuple[Value, ...] = ()


class Function:
    """One kernel function: parameters and a body block."""

    def __init__(self, name: str, params: Sequence[Value],
                 loc: Optional[SrcLoc] = None):
        self.name = name
        self.params = tuple(params)
        self.loc = loc
        self.body = Block()


class Module:
    """A TIR module: the frontend's output for one specialization."""

    def __init__(self, name: str, source_path: str):
        self.name = name
        self.source_path = source_path
        self.functions: list = []


# ---------------------------------------------------------------------------
# Verifier
# ============================================================================


class Invariant:
    """The verifier's invariant classes (one malformed module each)."""

    USE_BEFORE_DEFINITION = "use-before-definition"
    TYPE_CONTRADICTION = "type-contradiction"
    MASKED_WITHOUT_DEFAULT = "masked-op-without-declared-default"
    BROADCAST_AS_REAL = "broadcast-extent-consumed-as-real"
    CARRIED_WITHOUT_JOIN = "carried-value-without-join"
    MALFORMED = "malformed"


class TirError(Exception):
    """A verifier rejection: invariant class, location and message."""

    def __init__(self, invariant: str, loc: Optional[SrcLoc], message: str):
        super().__init__(f"{invariant}: {message}"
                         + (f" (at {loc})" if loc else ""))
        self.invariant = invariant
        self.loc = loc
        self.message = message


class _Scope:
    """Lexical scope: name -> Value, plus closed-region tracking."""

    def __init__(self):
        self.values: dict = {}
        self.closed: dict = {}     # value vid -> region description

    def define(self, name: str, value: Value) -> None:
        self.values[name] = value

    def copy(self) -> "_Scope":
        s = _Scope()
        s.values = dict(self.values)
        s.closed = dict(self.closed)
        return s


def verify_module(module: Module) -> list:
    """Verify a module; return the list of TirError (empty = valid)."""
    errors: list = []
    for fn in module.functions:
        scope = _Scope()
        for p in fn.params:
            scope.define(p.name, p)
        _verify_block(fn.body, scope, errors, region="function body")
    return errors


def verify(module: Module) -> None:
    """Verify a module; raise the first rejection found."""
    errors = verify_module(module)
    if errors:
        raise errors[0]


def _check_use(value: Value, what: str, loc, scope: _Scope,
               errors: list) -> None:
    """One operand use: closed region -> carried-without-join; not yet
    defined -> use-before-definition."""
    if value.producer is None:
        return                          # function parameter
    if value.vid in scope.closed:
        errors.append(TirError(
            Invariant.CARRIED_WITHOUT_JOIN, loc,
            f"{what} uses value '{value.name}' defined in a closed region "
            f"({scope.closed[value.vid]}) without a join"))
    elif value.producer not in _live_ops(scope):
        errors.append(TirError(
            Invariant.USE_BEFORE_DEFINITION, loc,
            f"{what} uses value '{value.name}' before its definition"))


def _live_ops(scope: _Scope) -> set:
    return {v.producer for v in scope.values.values()
            if v.producer is not None}


def _require_real(value: Value, what: str, op: Op, errors: list) -> None:
    if not is_real(value.shape):
        bad = [i for i, e in enumerate(value.shape) if e.broadcast]
        errors.append(TirError(
            Invariant.BROADCAST_AS_REAL, op.loc,
            f"{what} '{value.name}' consumes broadcast extent(s) at axis/axes "
            f"{bad} as a real extent; an explicit realize is required first"))


def _same_values(a: Shape, b: Shape) -> bool:
    return value_shape(a) == value_shape(b)


def _type_rule_errors(op: Op, errors: list) -> None:
    """The op-level type rules (the type-contradiction invariant class)."""
    op_name = op.op
    ops = op.operands

    def err(msg: str) -> None:
        errors.append(TirError(Invariant.TYPE_CONTRADICTION, op.loc, msg))

    if op_name in BIN_ARITH or op_name in BIN_BITWISE:
        if len(ops) != 2:
            return err(f"'{op_name}' needs two operands")
        lhs, rhs = ops
        if lhs.type != rhs.type:
            return err(f"'{op_name}' operand types differ: {lhs.type!r} vs "
                       f"{rhs.type!r} (the lowering must insert explicit "
                       "converts)")
        if lhs.type.is_pointer():
            return err(f"'{op_name}' on pointer operands")
        if op_name in BIN_BITWISE and not (lhs.type.is_int()
                                           or lhs.type.is_bool()):
            return err(f"'{op_name}' requires integer or bool operands, got "
                       f"{lhs.type!r}")
        if op_name in {"arith.sdiv", "arith.udiv", "arith.srem",
                       "arith.urem"} and not lhs.type.is_int():
            return err(f"'{op_name}' requires integer operands, got "
                       f"{lhs.type!r}")
        if not _same_values(lhs.shape, rhs.shape):
            return err(f"'{op_name}' operand extent values differ "
                       f"({lhs.shape} vs {rhs.shape}); broadcasting must be "
                       "an explicit broadcast op")
        if op.results:
            if op.results[0].type != lhs.type:
                return err(f"'{op_name}' result type must equal the operand "
                           "type")
            if value_shape(op.results[0].shape) != value_shape(lhs.shape):
                return err(f"'{op_name}' result extents must equal the "
                           "operand extents")
    elif op_name in CMP_PREDS:
        if len(ops) != 2:
            return err(f"comparison '{op_name}' needs two operands")
        lhs, rhs = ops
        if lhs.type != rhs.type:
            return err(f"comparison '{op_name}' operand types differ: "
                       f"{lhs.type!r} vs {rhs.type!r}")
        if lhs.type.is_pointer():
            return err(f"comparison '{op_name}' on pointer operands")
        if not _same_values(lhs.shape, rhs.shape):
            return err(f"comparison '{op_name}' operand extent values differ")
        if op.results and not op.results[0].type.is_bool():
            return err("comparison result must be i1")
    elif op_name in UNARY_OPS:
        if len(ops) != 1:
            return err(f"'{op_name}' needs one operand")
        v = ops[0]
        if op_name in ("arith.neg", "arith.fneg"):
            if v.type.is_bool() or v.type.is_pointer() or not v.type.is_numeric():
                return err(f"'{op_name}' requires a numeric operand, got "
                           f"{v.type!r}")
        elif op_name == "logical.not":
            if not v.type.is_bool():
                return err("'logical.not' requires a bool operand")
        elif op_name == "bit.invert":
            if not (v.type.is_int() or v.type.is_bool()):
                return err("'bit.invert' requires an integer operand, got "
                           f"{v.type!r}")
        if op.results and (op.results[0].type != v.type
                           or op.results[0].shape != v.shape):
            return err(f"'{op_name}' must preserve the operand type and shape")
    elif op_name == "select.where":
        if len(ops) != 3:
            return err("'select.where' needs three operands")
        cond, x, y = ops
        if not cond.type.is_bool():
            return err("'select.where' condition must be i1")
        if x.type != y.type:
            return err(f"'select.where' branches differ: {x.type!r} vs "
                       f"{y.type!r}")
        if not (_same_values(cond.shape, x.shape)
                and _same_values(x.shape, y.shape)):
            return err("'select.where' operand extent values differ")
        if op.results and op.results[0].type != x.type:
            return err("'select.where' result type must equal the branches")
    elif op_name == "convert":
        v = ops[0]
        if not op.results:
            return err("'convert' must produce a value")
        dst = op.results[0].type
        if not (v.type.is_numeric() and dst.is_numeric()):
            return err(f"'convert' converts numeric types only "
                       f"({v.type!r} -> {dst!r}); pointer/value "
                       "reinterpretation is a different construct")
        if v.type == dst:
            return err("'convert' to the same type is not a conversion")
        if op.results[0].shape != v.shape:
            return err("'convert' must preserve the shape")
    elif op_name == "bitcast":
        v = ops[0]
        if not op.results:
            return err("'bitcast' must produce a value")
        dst = op.results[0].type
        if v.type.bitwidth() != dst.bitwidth():
            return err(f"'bitcast' must preserve width: {v.type!r} -> "
                       f"{dst!r}")
        if v.type == dst:
            return err("'bitcast' to the same type is not a reinterpretation "
                       "(convert and bitcast are distinct constructs)")
        if op.results[0].shape != v.shape:
            return err("'bitcast' must preserve the shape")
    elif op_name == "broadcast":
        v = ops[0]
        if not op.results:
            return err("'broadcast' must produce a value")
        src, dst = v.shape, op.results[0].shape
        if len(src) > len(dst):
            return err("'broadcast' cannot reduce rank")
        pad = len(dst) - len(src)
        for i in range(pad):
            if not dst[i].broadcast:
                return err(f"'broadcast' padded axis {i} must be flagged "
                           "broadcast")
        for i, (s, d) in enumerate(zip(src, dst[pad:])):
            if s.value == d.value:
                if s.broadcast != d.broadcast:
                    return err(f"'broadcast' axis {pad + i} changed the "
                               "broadcast flag without expansion")
            elif s.is_one():
                if not d.broadcast:
                    return err(f"'broadcast' expanded axis {pad + i} must be "
                               "flagged broadcast")
            else:
                return err(f"'broadcast' extent mismatch at axis {pad + i}: "
                           f"{s.value} -> {d.value}")
        if op.results[0].type != v.type:
            return err("'broadcast' must preserve the element type")
    elif op_name == "realize":
        v = ops[0]
        if not op.results:
            return err("'realize' must produce a value")
        dst = op.results[0].shape
        if value_shape(v.shape) != value_shape(dst):
            return err("'realize' must preserve the extents")
        if not is_real(dst):
            return err("'realize' must produce real extents")
        if is_real(v.shape):
            return err("'realize' of an already-real shape changes nothing "
                       "(it is not a realize)")
        if op.results[0].type != v.type:
            return err("'realize' must preserve the element type")
    elif op_name == "ptradd":
        if len(ops) != 2:
            return err("'ptradd' needs a base and an offset")
        base, offset = ops
        if not base.type.is_pointer():
            return err(f"'ptradd' base must be a pointer, got {base.type!r}")
        if not offset.type.is_index():
            return err(f"'ptradd' offset must be i32/i64 index arithmetic, "
                       f"got {offset.type!r}")
        unified = unify_shapes(base.shape, offset.shape)
        if unified is None:
            return err(f"'ptradd' cannot unify base shape {base.shape} with "
                       f"offset shape {offset.shape}")
        if op.results:
            if op.results[0].type != base.type:
                return err("'ptradd' must preserve the pointer type")
            if op.results[0].shape != unified:
                return err("'ptradd' result shape must be the unified "
                           f"base/offset shape {unified}, got "
                           f"{op.results[0].shape}")
    elif op_name == "load":
        if not ops:
            return err("'load' needs a pointer operand")
        ptr = ops[0]
        if not ptr.type.is_pointer():
            return err(f"'load' pointer operand must be a pointer, got "
                       f"{ptr.type!r}")
        mask = ops[1] if len(ops) > 1 else None
        other = ops[2] if len(ops) > 2 else None
        if mask is not None:
            if not mask.type.is_bool():
                return err("'load' mask must be i1")
            if not _same_values(mask.shape, ptr.shape):
                return err("'load' mask extents must equal the pointer "
                           "extents")
            declared = op.attrs.get("masked_default")
            if declared is None:
                errors.append(TirError(
                    Invariant.MASKED_WITHOUT_DEFAULT, op.loc,
                    "masked 'load' without a declared disabled-position "
                    "default (an 'other' value or undef)"))
            if other is not None:
                if declared != MaskedDefault.VALUE:
                    return err("masked 'load' with an 'other' operand must "
                               "declare default=value")
                if other.type != ptr.type.pointee:
                    return err("'load' other type must equal the pointee "
                               "type")
                if not _same_values(other.shape, ptr.shape):
                    return err("'load' other extents must equal the pointer "
                               "extents")
        elif other is not None:
            return err("'load' other operand without a mask")
        if op.results:
            if op.results[0].type != ptr.type.pointee:
                return err("'load' result type must equal the pointee type")
            if op.results[0].shape != ptr.shape:
                return err("'load' result shape must equal the pointer shape")
    elif op_name == "store":
        if op.results:
            return err("'store' produces no value")
        if len(ops) not in (2, 3):
            return err("'store' needs pointer, value and optional mask")
        ptr, value = ops[0], ops[1]
        if not ptr.type.is_pointer():
            return err(f"'store' pointer operand must be a pointer, got "
                       f"{ptr.type!r}")
        if value.type != ptr.type.pointee:
            return err(f"'store' value type {value.type!r} must equal the "
                       f"pointee type {ptr.type.pointee!r} (the lowering must "
                       "insert an explicit convert)")
        if not _same_values(value.shape, ptr.shape):
            return err("'store' value extents must equal the pointer extents")
        if len(ops) == 3:
            mask = ops[2]
            if not mask.type.is_bool():
                return err("'store' mask must be i1")
            if not _same_values(mask.shape, ptr.shape):
                return err("'store' mask extents must equal the pointer "
                           "extents")
            if op.attrs.get("masked_default") is None:
                errors.append(TirError(
                    Invariant.MASKED_WITHOUT_DEFAULT, op.loc,
                    "masked 'store' without declared disabled-position "
                    "semantics (no-access)"))
            elif op.attrs["masked_default"] != MaskedDefault.NO_ACCESS:
                return err("masked 'store' must declare no-access semantics "
                           "for disabled positions")
    elif op_name == "const":
        if op.operands:
            return err("'const' takes no operands")
        if not op.results:
            return err("'const' must produce a value")
        v = op.attrs.get("value")
        t = op.results[0].type
        if t.is_bool() and not isinstance(v, bool):
            return err("'const' i1 requires a bool value")
        if t.is_int() and not isinstance(v, int):
            return err("'const' integer requires an int value")
        if t.is_float() and not isinstance(v, (int, float)):
            return err("'const' float requires a numeric value")
        if t.is_pointer():
            return err("'const' cannot produce a pointer (pointers are "
                       "parameters or ptradd results)")
        if op.results[0].shape != ():
            return err("'const' produces a zero-dimensional value")
    elif op_name == "program_id":
        if not op.results:
            return err("'program_id' must produce a value")
        if op.attrs.get("axis") not in (0, 1, 2):
            return err("'program_id' axis must be 0, 1 or 2")
        if op.results[0].type != INT32 or op.results[0].shape != ():
            return err("'program_id' must produce an i32 zero-dimensional "
                       "value")
    elif op_name == "arange":
        if not op.results:
            return err("'arange' must produce a value")
        start, end = op.attrs.get("start"), op.attrs.get("end")
        if not (isinstance(start, int) and isinstance(end, int)):
            return err("'arange' bounds must be compile-time integers")
        if end <= start:
            return err("'arange' end must be greater than start")
        rng = end - start
        if rng & (rng - 1):
            return err("'arange' range must be a power of two")
        if not (-2**31 <= start < 2**31 and -2**31 <= end < 2**31):
            return err("'arange' bounds must fit in int32")
        if op.results[0].type != INT32:
            return err("'arange' must produce i32")
        if op.results[0].shape != real_shape([rng]):
            return err("'arange' extents must be [end-start] (real)")
    elif op_name in ("zeros", "full"):
        if not op.results:
            return err(f"'{op_name}' must produce a value")
        t = op.results[0].type
        if not t.is_numeric():
            return err(f"'{op_name}' requires a numeric element type")
        if not is_real(op.results[0].shape):
            return err(f"'{op_name}' creates storage; its extents must be real")
        if op_name == "full":
            v = op.attrs.get("value")
            if t.is_bool() and not isinstance(v, bool):
                return err("'full' i1 requires a bool value")
            if t.is_int() and not isinstance(v, int):
                return err("'full' integer requires an int value")
            if t.is_float() and not isinstance(v, (int, float)):
                return err("'full' float requires a numeric value")
    elif op_name == "debug_barrier":
        if op.operands or op.results:
            return err("'debug_barrier' takes no operands and produces "
                       "nothing")
    else:
        errors.append(TirError(Invariant.MALFORMED, op.loc,
                               f"unknown op '{op_name}'"))


def _verify_block(block: Block, scope: _Scope, errors: list,
                  region: str) -> None:
    for stmt in block.statements:
        if isinstance(stmt, If):
            _check_use(stmt.cond, "'if' condition", stmt.loc, scope, errors)
            if not stmt.cond.type.is_bool():
                errors.append(TirError(Invariant.TYPE_CONTRADICTION, stmt.loc,
                                       "'if' condition must be i1"))
            then_scope = scope.copy()
            else_scope = scope.copy()
            _verify_block(stmt.then, then_scope, errors,
                          region=f"{region} / then-arm")
            _verify_block(stmt.els, else_scope, errors,
                          region=f"{region} / else-arm")
            results = []
            for name in stmt.join_names:
                t = then_scope.values.get(name)
                e = else_scope.values.get(name)
                if t is None or e is None:
                    errors.append(TirError(
                        Invariant.CARRIED_WITHOUT_JOIN, stmt.loc,
                        f"join '{name}' of the if at {stmt.loc} is not "
                        "defined by both arms"))
                    continue
                if t.type != e.type:
                    errors.append(TirError(
                        Invariant.TYPE_CONTRADICTION, stmt.loc,
                        f"join '{name}' has different types in the arms: "
                        f"{t.type!r} vs {e.type!r}"))
                    continue
                if value_shape(t.shape) != value_shape(e.shape):
                    errors.append(TirError(
                        Invariant.TYPE_CONTRADICTION, stmt.loc,
                        f"join '{name}' has different extent values in the "
                        "arms"))
                    continue
                jv = Value(t.type, t.shape, stmt.loc, name=name)
                results.append(jv)
                scope.define(name, jv)
            stmt.join_results = tuple(results)
            exported = {jv.vid for jv in results}
            for arm_scope in (then_scope, else_scope):
                for name, v in arm_scope.values.items():
                    if v.producer is None:
                        continue
                    outer = scope.values.get(name)
                    if (outer is not v and v.vid not in exported
                            and v.vid not in scope.closed):
                        scope.closed.setdefault(
                            v.vid, f"if-arm at {stmt.loc}")
        elif isinstance(stmt, Loop):
            for what, bound in (("'loop' lower bound", stmt.lower),
                                ("'loop' upper bound", stmt.upper),
                                ("'loop' step", stmt.step)):
                if bound is not None:
                    _check_use(bound, what, stmt.loc, scope, errors)
                    if not bound.type.is_index():
                        errors.append(TirError(
                            Invariant.TYPE_CONTRADICTION, stmt.loc,
                            f"{what} must be i32/i64"))
            body_scope = scope.copy()
            for name, init in stmt.carried:
                _check_use(init, f"'loop' carried initial value '{name}'",
                           stmt.loc, scope, errors)
                body_scope.define(name, init)
            _verify_block(stmt.body, body_scope, errors,
                          region=f"{region} / loop-body")
            results = []
            for name, init in stmt.carried:
                final = body_scope.values.get(name)
                if final is None or final.vid == init.vid:
                    errors.append(TirError(
                        Invariant.CARRIED_WITHOUT_JOIN, stmt.loc,
                        f"loop at {stmt.loc} carries '{name}' but the body "
                        "never redefines it (carried value without join)"))
                    continue
                if final.type != init.type or value_shape(final.shape) != \
                        value_shape(init.shape):
                    errors.append(TirError(
                        Invariant.TYPE_CONTRADICTION, stmt.loc,
                        f"loop-carried '{name}' changes type/shape in the "
                        "body"))
                    continue
                jv = Value(final.type, final.shape, stmt.loc, name=name)
                results.append(jv)
                scope.define(name, jv)
            stmt.join_results = tuple(results)
            exported = {jv.vid for jv in results}
            for name, v in body_scope.values.items():
                if v.producer is None:
                    continue
                outer = scope.values.get(name)
                if (outer is not v and v.vid not in exported
                        and v.vid not in scope.closed):
                    scope.closed.setdefault(v.vid, f"loop body at {stmt.loc}")
        elif isinstance(stmt, Op):
            for i, operand in enumerate(stmt.operands):
                _check_use(operand, f"op '{stmt.op}' operand {i}", stmt.loc,
                           scope, errors)
            _type_rule_errors(stmt, errors)
            if stmt.op in ("load", "store"):
                _require_real(stmt.operands[0], "memory pointer operand",
                              stmt, errors)
                if stmt.op == "store":
                    _require_real(stmt.operands[1], "store value operand",
                                  stmt, errors)
            for r in stmt.results:
                scope.define(r.name, r)
        else:
            errors.append(TirError(Invariant.MALFORMED, None,
                                   f"unknown statement {stmt!r}"))
