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
    "is_real", "real_shape", "flat_extent", "LAYOUT_OPS", "MATRIX_OPS",
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


def flat_extent(shape: Shape) -> Optional[int]:
    """The flat element count of a compile-time shape (None when any extent
    is runtime-symbolic -- layout blocks must be compile-time shaped)."""
    total = 1
    for e in shape:
        if isinstance(e.value, Sym) or isinstance(e.value, bool) \
                or not isinstance(e.value, int):
            return None
        total *= e.value
    return total


#: layout data-movement ops (the T012 lane): they relate distinct flat index
#: spaces (or permute one) and lower through the multi-pass staging model.
#: ``reshape`` is *metadata* (flat-identity) and ``broadcast`` is a layout op
#: only for block operands with a non-equal target shape.
LAYOUT_OPS = {"permute", "flip", "join", "split", "interleave"}


def _reshape_covering(src: Shape, extents) -> Shape:
    """The covered-axes rule: each result axis covers a contiguous
    multiplicative run of source axes; a splitting or inserted axis is
    REAL (the conservative flag).  Raises ValueError when the extents do
    not tile."""
    src_vals = [e.value for e in src]
    total_src, total_dst = 1, 1
    for v in src_vals:
        total_src *= v
    for v in extents:
        total_dst *= v
    if total_src != total_dst:
        raise ValueError(
            f"element counts differ ({total_src} vs {total_dst})")
    si = 0
    rem = src_vals[0] if src_vals else None
    out = []
    for de in extents:
        if de == 1:
            if rem == 1 and si < len(src_vals):
                out.append(Extent(1, src[si].broadcast))
                si += 1
                rem = src_vals[si] if si < len(src_vals) else None
            else:
                out.append(Extent(1, False))
            continue
        need = de
        flags = []
        aligned = True
        while need > 1:
            if rem is None:
                raise ValueError(
                    f"the axes do not tile (ran out of source extent at "
                    f"extent {de})")
            if rem <= need and need % rem == 0:
                flags.append(src[si].broadcast)
                need //= rem
                si += 1
                rem = src_vals[si] if si < len(src_vals) else None
            elif rem % need == 0:
                rem //= need
                need = 1
                aligned = False
            else:
                raise ValueError(
                    f"the axes do not tile (extent {de} vs remaining "
                    f"source extent {rem})")
        out.append(Extent(de, aligned and all(flags)))
    if rem is not None and rem != 1:
        raise ValueError(f"source extent {rem} is left uncovered")
    for v in src_vals[si:]:
        if v != 1:
            raise ValueError(
                f"source axes {src_vals[si:]} are left uncovered")
    return tuple(out)


# ---------------------------------------------------------------------------
# Values
# ============================================================================


class Value:
    """An SSA value: type, shape, producing op and source location.

    ``name`` is the dump/primary name; ``aliases`` carries every *source
    name* the value is currently bound to.  The verifier's lexical scopes
    define the value under ``name`` and every alias, which is what makes
    region joins name-based (a source variable re-bound on one path of a
    branch joins under its source name at the region close) while dumps
    stay unambiguous.
    """

    __slots__ = ("vid", "name", "aliases", "type", "shape", "loc", "producer")

    _next = 0

    def __init__(self, type: Type, shape: Shape, loc: Optional[SrcLoc] = None,
                 name: Optional[str] = None, producer: "Optional[Op]" = None):
        Value._next += 1
        self.vid = Value._next
        self.name = name or f"v{self.vid}"
        self.aliases: Tuple[str, ...] = ()
        self.type = type
        self.shape = shape
        self.loc = loc
        self.producer = producer

    def scope_names(self) -> Tuple[str, ...]:
        return (self.name,) + self.aliases

    def add_alias(self, name: str) -> None:
        if name and name != self.name and name not in self.aliases:
            self.aliases = self.aliases + (name,)

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
             "arith.frem",
             # T013: the precise (round-to-nearest) division, distinct
             # from the approximable fdiv (both lower to the target's
             # exactly-rounded vfdiv; the codes stay distinct so a future
             # fast path can never silently replace the precise form)
             "arith.div_rn"}
#: bitwise/logical op codes (integer or bool operands)
BIN_BITWISE = {"bit.and", "bit.or", "bit.xor", "bit.shl", "bit.ashr",
               "bit.lshr"}
#: comparison predicates
CMP_PREDS = {"cmp.lt", "cmp.le", "cmp.gt", "cmp.ge", "cmp.eq", "cmp.ne"}
#: unary op codes
UNARY_OPS = {"arith.neg", "arith.fneg", "logical.not", "bit.invert"}

#: T013: special math unary op codes (the math-ops lane).  The pinned
#: Triton 3.8 ``_check_dtype`` admits fp32/fp64 operands only for these
#: constructs (a 16-bit operand is a frontend type error, never a silent
#: promotion); fp64 is the internal-compute width position_quantize uses.
MATH_UNARY_OPS = {"math.exp", "math.exp2", "math.log", "math.log2",
                  "math.sin", "math.cos", "math.erf", "math.sqrt",
                  "math.sqrt_rn", "math.rsqrt", "math.floor", "math.ceil"}
#: tl.abs: the floating form and the signed-integer form are distinct ops
#: (the pinned semantic dispatches fabs / iabs; unsigned abs is the
#: identity, emitted as no op at all)
ABS_OPS = {"math.fabs", "math.iabs"}
#: T013: tl.maximum / tl.minimum.  The NaN policy is carried BY THE OP
#: CODE, never by an ignorable attribute: ``maxnum`` returns the other
#: operand when one is NaN (propagate_nan=NONE, the default) while
#: ``maximum`` propagates a quiet NaN (propagate_nan=ALL); the integer
#: forms carry the operand signedness (IR-SEMANTIC-FIDELITY).
MAXMIN_OPS = {"arith.maxnumf", "arith.minnumf", "arith.maximumf",
              "arith.minimumf", "arith.maxsi", "arith.maxui",
              "arith.minsi", "arith.minui"}

#: T014: tl.dot -- the matrix product of two rank-2 blocks.  The op
#: carries the operand dtypes, the accumulation type (``out_dtype``) and
#: the numeric class (``ieee``: fp32 dots are exact IEEE, never tf32 --
#: the subset strips input_precision/allow_tf32 and the runner pins
#: TRITON_F32_DEFAULT=ieee, F052).  The optional third operand is the
#: ``acc`` block (the pinned semantics require its dtype to equal
#: out_dtype); the result is (M, N) at out_dtype.
MATRIX_OPS = {"linalg.dot"}


def _and_flags(shapes: Sequence[Shape]) -> Shape:
    """Per-axis AND of broadcast flags over shapes with equal extent values."""
    if not shapes:
        return ()
    out = []
    for i in range(len(shapes[0])):
        flag = all(s[i].broadcast for s in shapes)
        out.append(Extent(shapes[0][i].value, flag))
    return tuple(out)


def _reduced_shape(shape: Shape, axes: Sequence[int],
                   keep_dims: bool) -> Shape:
    """The reduce result shape (reduced axes removed, or kept at 1)."""
    axeset = set(axes)
    out: list = []
    for i, e in enumerate(shape):
        if i in axeset:
            if keep_dims:
                out.append(Extent(1, False))
        else:
            out.append(e)
    return tuple(out)


def _topk_shape(shape: Shape, dim: int, k: int) -> Shape:
    return tuple(Extent(k, False) if i == dim else e
                 for i, e in enumerate(shape))


def _identity_ok(got, want, ty: Type) -> bool:
    """Compare a carried identity with the table's identity at the type:
    ints bitwise (bool as 0/1), floats bitwise through their IEEE bits (so
    -inf/inf/0.0 compare exactly, never numerically-loosely)."""
    if got is None:
        return False
    if ty.is_float():
        if isinstance(got, bool) or not isinstance(got, (int, float)):
            return False
        import math as _math
        import struct as _struct
        width = ty.bitwidth()
        if width == 32:
            a = _struct.unpack("<I", _struct.pack("<f", float(got)))[0]
            b = _struct.unpack("<I", _struct.pack("<f", float(want)))[0]
        elif width == 64:
            a = _struct.unpack("<Q", _struct.pack("<d", float(got)))[0]
            b = _struct.unpack("<Q", _struct.pack("<d", float(want)))[0]
        else:
            # fp16/bf16 identities compare numerically (they convert)
            return float(got) == float(want)
        return a == b
    if ty.is_bool():
        return isinstance(got, bool) and got == bool(want)
    if isinstance(got, bool) or not isinstance(got, int):
        return False
    mask = (1 << ty.bitwidth()) - 1
    return (int(got) & mask) == (int(want) & mask)


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
    def num_programs(axis: int, loc: Optional[SrcLoc] = None) -> "Op":
        """The runtime grid extent of ``axis`` (launch geometry is runtime)."""
        return Op("num_programs", (), loc, INT32, (), attrs={"axis": axis})

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
             loc: Optional[SrcLoc] = None,
             volatile: bool = False) -> "Op":
        attrs: dict = {}
        if mask is not None:
            attrs["masked_default"] = masked_default
        if volatile:
            attrs["volatile"] = True
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

    # -- T011: memory access breadth and atomics --------------------------

    @staticmethod
    def hint(value: Value, multiple_of: Optional[int] = None,
             max_contiguous: Optional[int] = None,
             loc: Optional[SrcLoc] = None) -> "Op":
        """An alignment/contiguity promise attached to a value
        (``tl.multiple_of`` / ``tl.max_contiguous``).

        The hint is a *promise about the value's lanes*, never a
        requirement: the identity result carries the recorded facts and
        the wide-access proof consults them; a proof without a hint
        declines (the access keeps its masked/indexed form).  Ignoring a
        hint is always safe.
        """
        attrs = {}
        if multiple_of is not None:
            attrs["multiple_of"] = int(multiple_of)
        if max_contiguous is not None:
            attrs["max_contiguous"] = int(max_contiguous)
        return Op("hint", (value,), loc, value.type, value.shape,
                  attrs=attrs)

    @staticmethod
    def atomic_rmw(op: str, ptr: Value, val: Value,
                   mask: Optional[Value], masked_default: Optional[str],
                   sem: str, scope: str,
                   loc: Optional[SrcLoc] = None) -> "Op":
        """An atomic read-modify-write (``tl.atomic_add/max/min/xchg/and/
        or/xor``): the result is the OLD value at every position.

        Carries (IR-SEMANTIC-FIDELITY): the operation ``op``; the mask
        with its DECLARED disabled-position semantics (no-access -- a
        masked atomic performs no access at disabled positions); the
        ``sem``/``scope`` ordering pair the lowering maps onto the
        declared RVWMO model; the pointee's own signedness (min/max keep
        it).  The old value at disabled positions is undefined.
        """
        attrs = {"op": op, "sem": sem, "scope": scope}
        if mask is not None:
            attrs["masked_default"] = masked_default
        return Op("atomic_rmw",
                  tuple(v for v in (ptr, val, mask) if v is not None),
                  loc, ptr.type.pointee, ptr.shape, attrs=attrs)

    @staticmethod
    def atomic_cas(ptr: Value, cmp: Value, val: Value,
                   mask: Optional[Value], masked_default: Optional[str],
                   sem: str, scope: str,
                   loc: Optional[SrcLoc] = None) -> "Op":
        """An atomic compare-and-swap (``tl.atomic_cas``): when the old
        value equals ``cmp`` it becomes ``val``; the result is the OLD
        value (undefined at disabled positions of a masked form)."""
        attrs = {"sem": sem, "scope": scope}
        if mask is not None:
            attrs["masked_default"] = masked_default
        return Op("atomic_cas",
                  tuple(v for v in (ptr, cmp, val, mask) if v is not None),
                  loc, ptr.type.pointee, ptr.shape, attrs=attrs)

    @staticmethod
    def gather(src: Value, index: Value, axis: int,
               loc: Optional[SrcLoc] = None) -> "Op":
        """``out[i...] = src[index[i...]]`` along ``axis``
        (``tl.gather``): the result carries the index's shape."""
        return Op("gather", (src, index), loc, src.type, index.shape,
                  attrs={"axis": axis})

    @staticmethod
    def interleave(a: Value, b: Value,
                   loc: Optional[SrcLoc] = None) -> "Op":
        """``r[2i] = a[i]``, ``r[2i+1] = b[i]`` (``tl.interleave``): the
        last extent doubles (a compile-time extent; a symbolic last axis
        is constructed by the frontend as an explicit expression, never
        guessed here)."""
        last = a.shape[-1]
        if not isinstance(last.value, int):
            raise ValueError(
                "interleave requires a compile-time last extent (the "
                "doubled extent must be nameable)")
        shape = list(a.shape)
        shape[-1] = Extent(last.value * 2, last.broadcast)
        return Op("interleave", (a, b), loc, a.type, tuple(shape))

    # -- T012: layout, shape and dtype-conversion breadth -------------------

    @staticmethod
    def reshape(value: Value, shape: Shape, loc: Optional[SrcLoc] = None,
                can_reorder: bool = False) -> "Op":
        """Re-partition the axes without touching the flat element order
        (``tl.reshape`` with ``can_reorder=False``; ``can_reorder=True``
        (``tl.view``) permits any permutation and the identity is the
        realized choice -- the classification is carried for the count).

        The op is *metadata on the data path*: the result's lanes are the
        source's lanes (the lowering's register/workspace identity).
        """
        return Op("reshape", (value,), loc, value.type, shape,
                  attrs={"from_shape": value.shape,
                         "can_reorder": bool(can_reorder)})

    @staticmethod
    def permute(value: Value, dims: Sequence[int],
                loc: Optional[SrcLoc] = None) -> "Op":
        """Axis permutation (``tl.trans`` / ``tl.permute``): result axis j
        is source axis ``dims[j]``.  The flat element order changes; the
        lowering realizes it through the staging map."""
        shape = tuple(value.shape[d] for d in dims)
        return Op("permute", (value,), loc, value.type, shape,
                  attrs={"dims": tuple(int(d) for d in dims)})

    @staticmethod
    def join(a: Value, b: Value,
             loc: Optional[SrcLoc] = None) -> "Op":
        """Append a minor extent-2 axis (``tl.join``): ``r[..., 0] = a``,
        ``r[..., 1] = b`` (the operands are pre-unified by the frontend,
        exactly the pinned ``broadcast_impl_value`` first step)."""
        shape = tuple(a.shape) + (Extent(2, False),)
        return Op("join", (a, b), loc, a.type, shape,
                  attrs={"from_shape": a.shape})

    @staticmethod
    def split(value: Value, loc: Optional[SrcLoc] = None) -> "Op":
        """Split the last extent-2 axis into two values (``tl.split``):
        ``lhs[..., i] = value[..., i]``."""
        shape = tuple(value.shape[:-1])
        return Op("split", (value,), loc, value.type, shape, results=2)

    @staticmethod
    def flip(value: Value, dim: int,
             loc: Optional[SrcLoc] = None) -> "Op":
        """Reverse one axis (``tl.flip``; the pinned surface requires a
        power-of-two extent there)."""
        return Op("flip", (value,), loc, value.type, value.shape,
                  attrs={"dim": int(dim)})

    @staticmethod
    def reduce(value: Value, kind: str, axes: Sequence[int],
               keep_dims: bool, identity, loc: Optional[SrcLoc] = None,
               tie_break_left: bool = True, return_indices: bool = False,
               index_type: Optional[Type] = None,
               accumulate_type: Optional[Type] = None) -> "Op":
        """The reduction contract carrier (COMPILER_ARCHITECTURE.md 2.1).

        Carries: the operation ``kind`` (sum/max/min/argmax/argmin/
        xor_sum/reduce_or), the reduced ``axes``, ``keep_dims``, the
        per-operation-and-dtype ``identity`` element (signedness-correct,
        derived by the plan's table and checked by the verifier), the
        index forms' declared ``tie_break_left`` and the value forms'
        ``return_indices`` (two results: value, index).

        The accumulator may be re-typed before the reduction
        (``accumulate_type`` -- tl.sum's ``dtype=``): the operand converts
        to it first, the identity follows it and the result carries it.
        """
        acc_ty = accumulate_type or value.type
        index_ty = index_type or INT32
        if kind in ("argmax", "argmin"):
            rtype, results = index_ty, 1
        elif return_indices:
            rtype, results = acc_ty, 2
        else:
            rtype, results = acc_ty, 1
        shape = _reduced_shape(value.shape, axes, keep_dims)
        op = Op("reduce", (value,), loc, rtype, shape, attrs={
            "kind": kind, "axes": tuple(axes), "keep_dims": keep_dims,
            "identity": identity, "tie_break_left": tie_break_left,
            "return_indices": return_indices, "index_type": index_ty,
            "accumulate_type": acc_ty,
        }, results=results)
        if return_indices and len(op.results) == 2:
            # the index result carries the index type (the constructor
            # types every result with the value type)
            op.results[1].type = index_ty
        return op

    @staticmethod
    def scan(value: Value, kind: str, axis: int, reverse: bool, identity,
             loc: Optional[SrcLoc] = None) -> "Op":
        """An inclusive scan (cumsum/cumprod) along one axis: the result
        has the operand's type and shape; the carry's identity element is
        carried for the chunked lowering (and the empty prefix)."""
        return Op("scan", (value,), loc, value.type, value.shape, attrs={
            "kind": kind, "axis": axis, "reverse": reverse,
            "identity": identity,
        })

    @staticmethod
    def sort(value: Value, dim: int, descending: bool,
             loc: Optional[SrcLoc] = None) -> "Op":
        """A whole-block sort along ``dim`` (tl.sort)."""
        return Op("sort", (value,), loc, value.type, value.shape, attrs={
            "dim": dim, "descending": descending,
        })

    @staticmethod
    def topk(value: Value, k: int, dim: int, descending: bool,
             loc: Optional[SrcLoc] = None) -> "Op":
        """The k largest values along ``dim`` (tl.topk), sorted."""
        shape = tuple(Extent(k, False) if i == dim else e
                      for i, e in enumerate(value.shape))
        return Op("topk", (value,), loc, value.type, shape, attrs={
            "k": k, "dim": dim, "descending": descending,
        })

    @staticmethod
    def histogram(value: Value, num_bins: int,
                  loc: Optional[SrcLoc] = None) -> "Op":
        """out[b] = count of elements equal to b, b in [0, num_bins)."""
        return Op("histogram", (value,), loc, INT32,
                  real_shape([num_bins]), attrs={"num_bins": num_bins})

    # -- T013: special math functions and bit-exact RNG ----------------------

    @staticmethod
    def math_unary(op: str, operand: Value,
                   loc: Optional[SrcLoc] = None) -> "Op":
        """One special math function application (``math.exp`` &c): the
        result preserves the operand's type and shape."""
        return Op(op, (operand,), loc, operand.type, operand.shape)

    @staticmethod
    def abs_value(operand: Value,
                  loc: Optional[SrcLoc] = None) -> "Op":
        """``tl.abs``: the float form (``math.fabs``) or the signed-integer
        form (``math.iabs``); unsigned abs is the identity (no op)."""
        if operand.type.is_float():
            op = "math.fabs"
        elif operand.type.is_int() and operand.type.is_int_signed():
            op = "math.iabs"
        else:
            raise ValueError(
                f"abs of {operand.type!r} is the identity (no op)")
        return Op(op, (operand,), loc, operand.type, operand.shape)

    @staticmethod
    def maxmin(op: str, lhs: Value, rhs: Value,
               loc: Optional[SrcLoc] = None) -> "Op":
        """``tl.maximum`` / ``tl.minimum`` on pre-unified operands; the op
        code carries the NaN policy and the signedness."""
        shape = _and_flags([lhs.shape, rhs.shape])
        return Op(op, (lhs, rhs), loc, lhs.type, shape)

    @staticmethod
    def fma(x: Value, y: Value, z: Value,
            loc: Optional[SrcLoc] = None) -> "Op":
        """``tl.fma``: x * y + z with ONE rounding (fused), the operands
        pre-unified by the frontend exactly like the pinned
        ``binary_op_type_legalization`` chain."""
        shape = _and_flags([x.shape, y.shape, z.shape])
        return Op("math.fma", (x, y, z), loc, x.type, shape)

    @staticmethod
    def philox(k0: Value, k1: Value, c0: Value, c1: Value, c2: Value,
               c3: Value, rounds: int,
               loc: Optional[SrcLoc] = None) -> "Op":
        """The Philox counter-based RNG primitive (``tl.philox``).

        Carries (IR-SEMANTIC-FIDELITY): the 32-bit counter words
        ``c0..c3`` as uint32 blocks of one shape, the key words ``k0``/``k1``
        as rank-0 uint32 scalars (the pinned implementation keeps the key
        0-d across the rounds), and the round count (a constexpr; the
        pinned default is 10).  Four uint32 results (the new counter).
        The round recurrence itself is the lowering's: umulhi/mul of the
        PHILOX constants, xor with the key words, wrapping key raises.
        """
        return Op("rng.philox", (k0, k1, c0, c1, c2, c3), loc,
                  c0.type, c0.shape, attrs={"rounds": int(rounds)},
                  results=4)

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
        #: T034: the per-arm join SIDES the frontend resolved --
        #: ``(name, then_value, else_value)`` per join name.  The name
        #: environment the MIR lowering maintains is alias-driven, and a
        #: value bound under a name in ONE arm carries that alias
        #: everywhere it is lowered (pdist's ``hi = mid`` in the else arm
        #: aliased ``mid`` as ``hi``; the mid's lowering then defined
        #: ``names['hi']`` in the enclosing scope, and the THEN arm's
        #: close passed ``mid`` as its ``hi`` side -- the binary search
        #: collapsed).  The recorded sides are authoritative.
        self.join_sides: Tuple[Tuple[str, Value, Value], ...] = ()


class Loop:
    """Structured loop with carried values.

    ``carried``: tuple of (name, initial Value).  The body must redefine
    every carried name; the value visible after the loop is the join of the
    body's definitions (loop-carried join).

    Two forms (one construct, the ``cond`` field selects):

    * counted range form: ``lower``/``upper``/``step`` all present, the body
      executes while the induction value (``carried[0]``'s name) is below
      ``upper`` -- or, when ``descending`` is set (a compile-time negative
      ``step``), while it is above ``upper``; the frontend appends the
      induction increment inside the body so the carried-join invariant
      covers it like any other carried name;
    * while form: ``cond`` present and the three bounds ``None``; ``cond``
      names the *initial* condition value, and the body must redefine the
      cond's name (it is carried) by re-evaluating the condition over the
      current carried state each iteration.
    """

    def __init__(self, lower: Optional[Value], upper: Optional[Value],
                 step: Optional[Value], loc: Optional[SrcLoc] = None,
                 cond: Optional[Value] = None, descending: bool = False):
        self.lower = lower
        self.upper = upper
        self.step = step
        self.cond = cond
        #: a descending counted range (compile-time negative step): the
        #: body runs while the induction stays ABOVE ``upper`` (T033; the
        #: pinned Triton lowering of ``range(a, b, -s)``).  The verifier
        #: pins the flag to the step's compile-time sign.
        self.descending = bool(descending)
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
        if op.attrs.get("volatile") not in (None, True):
            return err("'load' volatile must be a flag (the not-elidable "
                       "carrier)")
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
    elif op_name == "num_programs":
        if not op.results:
            return err("'num_programs' must produce a value")
        if op.attrs.get("axis") not in (0, 1, 2):
            return err("'num_programs' axis must be 0, 1 or 2")
        if op.results[0].type != INT32 or op.results[0].shape != ():
            return err("'num_programs' must produce an i32 zero-dimensional "
                       "value (the runtime grid extent)")
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
    elif op_name == "hint":
        if len(ops) != 1 or len(op.results) != 1:
            return err("'hint' takes one operand and produces one value")
        v = ops[0]
        if op.results[0].type != v.type \
                or op.results[0].shape != v.shape:
            return err("'hint' preserves the operand's type and shape "
                       "(it is a recorded promise, never a conversion)")
        for key in ("multiple_of", "max_contiguous"):
            val = op.attrs.get(key)
            if val is not None and (not isinstance(val, int)
                                    or isinstance(val, bool) or val < 1):
                return err(f"'hint' {key} must be a positive integer")
    elif op_name in ("atomic_rmw", "atomic_cas"):
        need = 2 if op_name == "atomic_rmw" else 3
        if not op.results:
            return err(f"'{op_name}' must produce the old value")
        ptr = ops[0]
        if not ptr.type.is_pointer():
            return err(f"'{op_name}' pointer operand must be a pointer, "
                       f"got {ptr.type!r}")
        if op.results[0].type != ptr.type.pointee:
            return err(f"'{op_name}' result type must equal the pointee "
                       "type (the old value)")
        if not _same_values(op.results[0].shape, ptr.shape):
            return err(f"'{op_name}' result extents must equal the pointer "
                       "extents")
        vals = ops[1:need]              # the value operands (never the mask)
        for i, v in enumerate(vals):
            if v.type != ptr.type.pointee:
                return err(f"'{op_name}' operand {i + 1} type {v.type!r} "
                           f"must equal the pointee type "
                           f"{ptr.type.pointee!r}")
            if not _same_values(v.shape, ptr.shape):
                return err(f"'{op_name}' operand {i + 1} extents must "
                           "equal the pointer extents")
        mask = ops[need] if len(ops) > need else None
        if mask is not None:
            if not mask.type.is_bool():
                return err(f"'{op_name}' mask must be i1")
            if not _same_values(mask.shape, ptr.shape):
                return err(f"'{op_name}' mask extents must equal the "
                           "pointer extents")
            declared = op.attrs.get("masked_default")
            if declared is None:
                errors.append(TirError(
                    Invariant.MASKED_WITHOUT_DEFAULT, op.loc,
                    f"masked '{op_name}' without a declared disabled-"
                    "position default (no-access)"))
            elif declared != MaskedDefault.NO_ACCESS:
                return err(f"masked '{op_name}' must declare no-access "
                           "semantics for disabled positions (a masked "
                           "atomic performs no access there)")
        if op_name == "atomic_rmw" and op.attrs.get("op") not in (
                "add", "max", "min", "xchg", "and", "or", "xor"):
            return err(f"'atomic_rmw' op {op.attrs.get('op')!r} is not "
                       "declared")
        if op.attrs.get("sem") not in ("relaxed", "acquire", "release",
                                       "acq_rel"):
            return err(f"'{op_name}' sem {op.attrs.get('sem')!r} is not "
                       "declared")
        if op.attrs.get("scope") not in ("gpu", "sys", "cta"):
            return err(f"'{op_name}' scope {op.attrs.get('scope')!r} is "
                       "not declared")
    elif op_name == "gather":
        if len(ops) != 2 or len(op.results) != 1:
            return err("'gather' takes a source and an index and produces "
                       "one value")
        src, index = ops
        if src.rank == 0 or index.rank == 0:
            return err("'gather' operates on block values")
        if not index.type.is_int():
            return err(f"'gather' index must be integer, got "
                       f"{index.type!r}")
        if op.results[0].type != src.type:
            return err("'gather' preserves the source element type")
        if op.results[0].shape != index.shape:
            return err("'gather' result shape is the index's shape")
        axis = op.attrs.get("axis")
        if not isinstance(axis, int) or isinstance(axis, bool) \
                or not 0 <= axis < src.rank:
            return err(f"'gather' axis {axis!r} outside the source rank "
                       f"{src.rank}")
    elif op_name == "interleave":
        if len(ops) != 2 or len(op.results) != 1:
            return err("'interleave' takes two operands and produces one "
                       "value")
        a, b = ops
        if a.type != b.type:
            return err(f"'interleave' operand types differ: {a.type!r} vs "
                       f"{b.type!r}")
        if a.rank == 0:
            return err("'interleave' operates on block values")
        if not _same_values(a.shape, b.shape):
            return err("'interleave' operand extent values must agree")
        if op.results[0].type != a.type:
            return err("'interleave' preserves the element type")
        last = a.shape[-1].value
        if not isinstance(last, int) \
                or value_shape(op.results[0].shape)[-1] != last * 2:
            return err("'interleave' result last extent must double the "
                       "operands' (a compile-time extent)")
        if value_shape(op.results[0].shape)[:-1] != \
                value_shape(a.shape)[:-1]:
            return err("'interleave' preserves the leading extents")
    elif op_name == "reduce":
        if len(ops) != 1 or not op.results:
            return err("'reduce' takes one operand and produces a value")
        v = ops[0]
        if v.rank == 0:
            return err("'reduce' cannot reduce a rank-0 value")
        if not is_real(v.shape):
            return err("'reduce' operand consumes a broadcast extent as "
                       "real (an explicit realize is required first)")
        kind = op.attrs.get("kind")
        axes = op.attrs.get("axes")
        if kind not in ("sum", "max", "min", "argmax", "argmin", "xor_sum",
                        "reduce_or"):
            return err(f"'reduce' kind {kind!r} is not declared")
        if not isinstance(axes, tuple) or not axes:
            return err("'reduce' requires a non-empty axes tuple")
        rank = len(v.shape)
        for a in axes:
            if not isinstance(a, int) or isinstance(a, bool) \
                    or not 0 <= a < rank:
                return err(f"'reduce' axis {a!r} outside rank {rank}")
        if len(set(axes)) != len(axes):
            return err("'reduce' axes repeat")
        keep = bool(op.attrs.get("keep_dims"))
        expected = _reduced_shape(v.shape, axes, keep)
        acc_ty = op.attrs.get("accumulate_type") or v.type
        index_form = kind in ("argmax", "argmin")
        ret_idx = bool(op.attrs.get("return_indices"))
        if index_form:
            if ret_idx:
                return err("'reduce' index forms do not take "
                           "return_indices (they are the index form)")
            if len(op.results) != 1:
                return err("'reduce' index forms produce one index result")
            if not op.results[0].type.is_index():
                return err("'reduce' argmax/argmin must produce i32/i64 "
                           f"(the index type), got {op.results[0].type!r}")
        elif ret_idx:
            if kind not in ("max", "min"):
                return err("'reduce' return_indices is declared for max/min")
            if len(op.results) != 2:
                return err("'reduce' return_indices produces (value, index)")
            if op.results[0].type != acc_ty:
                return err("'reduce' value result must carry the "
                           "accumulator type")
            if not op.results[1].type.is_index():
                return err("'reduce' index result must be i32/i64")
        else:
            if len(op.results) != 1:
                return err("'reduce' produces one result")
            if op.results[0].type != acc_ty:
                return err("'reduce' result must carry the accumulator "
                           f"type {acc_ty!r}, got {op.results[0].type!r}")
        if op.results[0].shape != expected:
            return err(f"'reduce' result shape {op.results[0].shape} is not "
                       f"the reduced shape {expected}")
        if ret_idx and op.results[1].shape != expected:
            return err("'reduce' index result shape must equal the value "
                       "result shape")
        # the identity element: per operation and dtype, signedness-correct
        # (checked against the plan's table -- the lattice top/bottom, so a
        # hand-written wrong constant is a rejection, never a silent pass)
        from a100c.plan import stages as _stages
        ident = op.attrs.get("identity")
        id_ty = acc_ty if not index_form else \
            op.attrs.get("index_type")
        try:
            want = _stages.identity_for(kind, id_ty)
        except KeyError:
            return err(f"'reduce' kind {kind!r} has no declared identity")
        if not _identity_ok(ident, want, id_ty):
            return err(f"'reduce' identity {ident!r} is not the declared "
                       f"per-op-and-dtype identity {want!r} for "
                       f"{id_ty!r} (signedness-correct lattice bound)")
    elif op_name == "scan":
        if len(ops) != 1 or len(op.results) != 1:
            return err("'scan' takes one operand and produces one value")
        v = ops[0]
        kind = op.attrs.get("kind")
        if kind not in ("cumsum", "cumprod"):
            return err(f"'scan' kind {kind!r} is not declared")
        axis = op.attrs.get("axis")
        if not isinstance(axis, int) or isinstance(axis, bool) \
                or not 0 <= axis < v.rank:
            return err(f"'scan' axis {axis!r} outside rank {v.rank}")
        if v.rank == 0:
            return err("'scan' cannot scan a rank-0 value")
        if op.results[0].type != v.type or op.results[0].shape != v.shape:
            return err("'scan' preserves the operand's type and shape")
        from a100c.plan import stages as _stages
        want = _stages.identity_for(
            "cumsum" if kind == "cumsum" else "cumprod", v.type)
        if not _identity_ok(op.attrs.get("identity"), want, v.type):
            return err(f"'scan' identity {op.attrs.get('identity')!r} is "
                       f"not the declared identity {want!r} for {v.type!r}")
    elif op_name == "sort":
        if len(ops) != 1 or len(op.results) != 1:
            return err("'sort' takes one operand and produces one value")
        v = ops[0]
        dim = op.attrs.get("dim")
        if not isinstance(dim, int) or isinstance(dim, bool) \
                or not 0 <= dim < v.rank:
            return err(f"'sort' dim {dim!r} outside rank {v.rank}")
        if op.results[0].type != v.type or op.results[0].shape != v.shape:
            return err("'sort' preserves the operand's type and shape")
        if not isinstance(op.attrs.get("descending"), bool):
            return err("'sort' descending must be a bool")
    elif op_name == "topk":
        if len(ops) != 1 or len(op.results) != 1:
            return err("'topk' takes one operand and produces one value")
        v = ops[0]
        dim = op.attrs.get("dim")
        k = op.attrs.get("k")
        if not isinstance(dim, int) or isinstance(dim, bool) \
                or not 0 <= dim < v.rank:
            return err(f"'topk' dim {dim!r} outside rank {v.rank}")
        if not isinstance(k, int) or isinstance(k, bool) or k < 1 \
                or k > v.shape[dim].value:
            return err(f"'topk' k {k!r} outside 1..{v.shape[dim].value}")
        if op.results[0].type != v.type:
            return err("'topk' preserves the element type")
        if value_shape(op.results[0].shape) != \
                value_shape(_topk_shape(v.shape, dim, k)):
            return err("'topk' result shape must replace dim's extent "
                       "with k")
    elif op_name == "reshape":
        v = ops[0]
        if len(ops) != 1 or len(op.results) != 1:
            return err("'reshape' takes one operand and produces one value")
        src, dst = v.shape, op.results[0].shape
        if op.results[0].type != v.type:
            return err("'reshape' must preserve the element type")
        ns, nd = flat_extent(src), flat_extent(dst)
        if ns is None or nd is None:
            return err("'reshape' requires compile-time extents (a symbolic "
                       "axis is not re-partitionable)")
        if ns != nd:
            return err(f"'reshape' cannot change the element count: "
                       f"{list(src)} ({ns}) -> {list(dst)} ({nd})")
        # the covered-axes rule (the frontend's _reshape_flags, restated):
        # each result axis covers a contiguous multiplicative run; an axis
        # that splits a source axis or is inserted at extent 1 is REAL
        try:
            want = _reshape_covering(src, [e.value for e in dst])
        except ValueError as exc:
            return err(f"'reshape' covering failed: {exc}")
        if tuple(dst) != want:
            return err(f"'reshape' result flags {list(dst)} do not match "
                       f"the covered-axes rule {list(want)}")
        if not isinstance(op.attrs.get("can_reorder"), bool):
            return err("'reshape' can_reorder must be a bool")
    elif op_name == "permute":
        v = ops[0]
        if len(ops) != 1 or len(op.results) != 1:
            return err("'permute' takes one operand and produces one value")
        dims = op.attrs.get("dims")
        rank = len(v.shape)
        if not isinstance(dims, tuple) or len(dims) != rank:
            return err(f"'permute' dims {dims!r} must permute rank {rank}")
        if sorted(dims) != list(range(rank)):
            return err(f"'permute' dims {dims!r} is not a permutation of "
                       f"0..{rank - 1}")
        want = tuple(v.shape[d] for d in dims)
        if op.results[0].shape != want:
            return err(f"'permute' result shape {list(op.results[0].shape)} "
                       f"is not the permuted shape {list(want)}")
        if op.results[0].type != v.type:
            return err("'permute' must preserve the element type")
    elif op_name == "join":
        if len(ops) != 2 or len(op.results) != 1:
            return err("'join' takes two operands and produces one value")
        a, b = ops
        if a.type != b.type:
            return err(f"'join' operand types differ: {a.type!r} vs "
                       f"{b.type!r} (the frontend pre-unifies the operands)")
        if a.shape != b.shape:
            return err(f"'join' operand shapes differ: {list(a.shape)} vs "
                       f"{list(b.shape)} (broadcast_impl_value runs first)")
        want = tuple(a.shape) + (Extent(2, False),)
        if op.results[0].shape != want:
            return err(f"'join' result shape {list(op.results[0].shape)} is "
                       f"not the operands' shape with a minor 2-axis "
                       f"{list(want)}")
        if op.results[0].type != a.type:
            return err("'join' must preserve the element type")
    elif op_name == "split":
        if len(ops) != 1 or len(op.results) != 2:
            return err("'split' takes one operand and produces two values")
        v = ops[0]
        if len(v.shape) < 2:
            return err("'split' requires rank >= 2 (the rank-1 "
                       "split-to-scalars form is a declared-unsupported "
                       "frontend refusal)")
        last = v.shape[-1]
        if last.value != 2 or last.broadcast:
            return err(f"'split' requires a real last extent of 2, got "
                       f"{last!r}")
        want = tuple(v.shape[:-1])
        for r in op.results:
            if r.shape != want:
                return err(f"'split' result shape {list(r.shape)} is not the "
                           f"source shape without the last axis "
                           f"{list(want)}")
            if r.type != v.type:
                return err("'split' must preserve the element type")
    elif op_name == "flip":
        v = ops[0]
        if len(ops) != 1 or len(op.results) != 1:
            return err("'flip' takes one operand and produces one value")
        dim = op.attrs.get("dim")
        if not isinstance(dim, int) or isinstance(dim, bool) \
                or not 0 <= dim < len(v.shape):
            return err(f"'flip' dim {dim!r} outside the rank {len(v.shape)}")
        ext = v.shape[dim].value
        if not isinstance(ext, int) or ext < 1 or (ext & (ext - 1)):
            return err(f"'flip' requires a power-of-two extent at dim {dim} "
                       f"(the pinned surface's static_assert), got {ext!r}")
        if op.results[0].type != v.type or op.results[0].shape != v.shape:
            return err("'flip' preserves the operand's type and shape")
    elif op_name == "histogram":
        if len(ops) != 1 or len(op.results) != 1:
            return err("'histogram' takes one operand and produces one "
                       "value")
        v = ops[0]
        num_bins = op.attrs.get("num_bins")
        if not isinstance(num_bins, int) or isinstance(num_bins, bool) \
                or num_bins < 1:
            return err("'histogram' num_bins must be a positive integer")
        if not v.type.is_int():
            return err("'histogram' requires an integer operand "
                       f"(bin membership), got {v.type!r}")
        if op.results[0].type != INT32:
            return err("'histogram' produces i32 counts")
        if op.results[0].shape != real_shape([num_bins]):
            return err("'histogram' produces [num_bins]")
    elif op_name in MATH_UNARY_OPS:
        if len(ops) != 1 or len(op.results) != 1:
            return err(f"'{op_name}' takes one operand and produces one "
                       "value")
        v = ops[0]
        if not v.type.is_float():
            return err(f"'{op_name}' requires a floating operand (the "
                       f"pinned _check_dtype), got {v.type!r}")
        if v.type.bitwidth() not in (32, 64):
            return err(f"'{op_name}' requires fp32 or fp64 operands, got "
                       f"{v.type!r}")
        if op.results[0].type != v.type \
                or op.results[0].shape != v.shape:
            return err(f"'{op_name}' must preserve the operand's type and "
                       "shape")
    elif op_name in ABS_OPS:
        if len(ops) != 1 or len(op.results) != 1:
            return err(f"'{op_name}' takes one operand and produces one "
                       "value")
        v = ops[0]
        if op_name == "math.fabs" and not v.type.is_float():
            return err("'math.fabs' requires a floating operand, got "
                       f"{v.type!r}")
        if op_name == "math.iabs" and not (v.type.is_int()
                                           and v.type.is_int_signed()):
            return err("'math.iabs' requires a signed integer operand, "
                       f"got {v.type!r}")
        if op.results[0].type != v.type \
                or op.results[0].shape != v.shape:
            return err(f"'{op_name}' must preserve the operand's type and "
                       "shape")
    elif op_name in MAXMIN_OPS:
        if len(ops) != 2 or len(op.results) != 1:
            return err(f"'{op_name}' takes two operands and produces one "
                       "value")
        lhs, rhs = ops
        if lhs.type != rhs.type:
            return err(f"'{op_name}' operand types differ: {lhs.type!r} vs "
                       f"{rhs.type!r} (the lowering must insert explicit "
                       "converts)")
        if op_name.endswith("f") and not lhs.type.is_float():
            return err(f"'{op_name}' requires floating operands, got "
                       f"{lhs.type!r}")
        if op_name.endswith(("si", "ui")):
            if not lhs.type.is_int():
                return err(f"'{op_name}' requires integer operands, got "
                           f"{lhs.type!r}")
            signed = op_name.endswith("si")
            if lhs.type.is_int_signed() != signed:
                return err(f"'{op_name}' signedness disagrees with the "
                           f"operand {lhs.type!r}")
        if not _same_values(lhs.shape, rhs.shape):
            return err(f"'{op_name}' operand extent values differ "
                       f"({lhs.shape} vs {rhs.shape}); broadcasting must be "
                       "an explicit broadcast op")
        if op.results and (op.results[0].type != lhs.type
                           or value_shape(op.results[0].shape)
                           != value_shape(lhs.shape)):
            return err(f"'{op_name}' result must equal the operand type "
                       "and extents")
    elif op_name == "math.fma":
        if len(ops) != 3 or len(op.results) != 1:
            return err("'math.fma' takes three operands and produces one "
                       "value")
        x, y, z = ops
        for a, b in ((x, y), (x, z)):
            if a.type != b.type:
                return err(f"'math.fma' operand types differ: {a.type!r} "
                           f"vs {b.type!r}")
        if not x.type.is_float():
            return err("'math.fma' requires floating operands, got "
                       f"{x.type!r}")
        if not (_same_values(x.shape, y.shape)
                and _same_values(x.shape, z.shape)):
            return err("'math.fma' operand extent values differ; "
                       "broadcasting must be an explicit broadcast op")
        if op.results[0].type != x.type \
                or value_shape(op.results[0].shape) != value_shape(x.shape):
            return err("'math.fma' result must equal the operand type and "
                       "extents")
    elif op_name in MATRIX_OPS:
        if len(ops) not in (2, 3) or len(op.results) != 1:
            return err("'linalg.dot' takes (a, b[, acc]) and produces one "
                       "value")
        a, b = ops[0], ops[1]
        acc = ops[2] if len(ops) == 3 else None
        if a.type != b.type:
            return err(f"'linalg.dot' operand types differ: {a.type!r} vs "
                       f"{b.type!r} (the pinned semantics require equal "
                       "operand dtypes)")
        if len(a.shape) != 2 or len(b.shape) != 2:
            return err(f"'linalg.dot' operands must be rank-2 blocks "
                       f"({list(a.shape)} x {list(b.shape)}); the batched "
                       "rank-3 form is not in this lane")
        if value_shape(a.shape)[1] != value_shape(b.shape)[0]:
            return err(f"'linalg.dot' reduction extents differ: "
                       f"{list(a.shape)} x {list(b.shape)}")
        out_dtype = op.attrs.get("out_dtype")
        if not isinstance(out_dtype, str) or not out_dtype:
            return err("'linalg.dot' must carry its out_dtype attribute "
                       "(the accumulation type)")
        ieee = op.attrs.get("ieee", False)
        if not isinstance(ieee, bool):
            return err("'linalg.dot' ieee attribute must be a boolean")
        res = op.results[0]
        want_shape = (a.shape[0], b.shape[1])
        if value_shape(res.shape) != value_shape(want_shape) \
                or len(res.shape) != 2:
            return err(f"'linalg.dot' result must be "
                       f"({want_shape[0].value}, {want_shape[1].value}), "
                       f"got {list(res.shape)}")
        if acc is not None:
            if value_shape(acc.shape) != value_shape(res.shape) \
                    or len(acc.shape) != 2:
                return err(f"'linalg.dot' accumulator shape "
                           f"{list(acc.shape)} is incompatible with the "
                           f"result {list(res.shape)}")
            if acc.type != res.type:
                return err(f"'linalg.dot' accumulator dtype {acc.type!r} "
                           f"must equal out_dtype {res.type!r}")
        for v, name in ((a, "a"), (b, "b"), (acc, "acc")):
            if v is None:
                continue
            if v.type.is_pointer() or v.type.is_bool():
                return err(f"'linalg.dot' operand '{name}' must be numeric, "
                           f"got {v.type!r}")
            _require_real(v, f"'linalg.dot' operand '{name}'", op, errors)
    elif op_name == "rng.philox":
        if len(ops) != 6 or len(op.results) != 4:
            return err("'rng.philox' takes (k0, k1, c0, c1, c2, c3) and "
                       "produces the four counter words")
        k0, k1, c0, c1, c2, c3 = ops
        for name, v in (("k0", k0), ("k1", k1)):
            if v.type != UINT32 or v.shape != ():
                return err(f"'rng.philox' key word {name} must be a rank-0 "
                           f"uint32 scalar, got {v.type!r} {list(v.shape)}")
        for name, v in (("c0", c0), ("c1", c1), ("c2", c2), ("c3", c3)):
            if v.type != UINT32:
                return err(f"'rng.philox' counter word {name} must be "
                           f"uint32, got {v.type!r}")
            if not _same_values(v.shape, c0.shape):
                return err(f"'rng.philox' counter word {name} extent "
                           f"values differ from c0 ({list(v.shape)} vs "
                           f"{list(c0.shape)})")
        rounds = op.attrs.get("rounds")
        if not isinstance(rounds, int) or isinstance(rounds, bool) \
                or rounds < 1:
            return err(f"'rng.philox' rounds must be a positive integer, "
                       f"got {rounds!r}")
        for r in op.results:
            if r.type != UINT32 or r.shape != c0.shape:
                return err("'rng.philox' produces four uint32 results at "
                           "the counter shape")
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
            if stmt.cond.shape != ():
                errors.append(TirError(
                    Invariant.TYPE_CONTRADICTION, stmt.loc,
                    "'if' condition must be scalar (rank 0); a block "
                    "condition is not a legal Triton branch"))
            then_scope = scope.copy()
            else_scope = scope.copy()
            _verify_block(stmt.then, then_scope, errors,
                          region=f"{region} / then-arm")
            _verify_block(stmt.els, else_scope, errors,
                          region=f"{region} / else-arm")
            # the pre-branch bindings: the close rule below decides
            # "defined inside an arm" by comparing against what the name
            # bound BEFORE the region -- the join results have already
            # re-bound the scope by then, and comparing against the JOIN
            # would close the outer value the not-assigning arm kept (the
            # one-path join's else side)
            pre_if = dict(scope.values)
            results = []
            provided = tuple(stmt.join_results)
            for i, name in enumerate(stmt.join_names):
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
                if i < len(provided):
                    jv = provided[i]
                    if jv.type != t.type or \
                            value_shape(jv.shape) != value_shape(t.shape):
                        errors.append(TirError(
                            Invariant.TYPE_CONTRADICTION, stmt.loc,
                            f"join '{name}' result does not match the arms' "
                            f"binding ({jv.type!r} vs {t.type!r})"))
                        continue
                else:
                    jv = Value(t.type, t.shape, stmt.loc, name=name)
                jv.add_alias(name)
                results.append(jv)
                # T043 (the tril class): an arm that assigns a name to an
                # already-defined value (``c_tile = acc``, acc a loop
                # join) encodes the binding as an ALIAS on that value --
                # op results already define every scope name at their
                # definition point (pdist's ``hi = mid``), so an
                # op-defined side is visible in the pre-if scope and the
                # both-arms rule resolves it.  A join-defined side must
                # behave identically: the join defines the value's scope
                # names (the join name plus its aliases), or the alias
                # stays invisible and the both-arms rule rejects a sound
                # outer-value side.
                for key in jv.scope_names():
                    scope.define(key, jv)
            if provided and len(provided) != len(results):
                errors.append(TirError(
                    Invariant.MALFORMED, stmt.loc,
                    f"the if at {stmt.loc} carries {len(provided)} join "
                    f"result(s) for {len(stmt.join_names)} join name(s)"))
            stmt.join_results = tuple(results)
            exported = {jv.vid for jv in results}
            for arm_scope in (then_scope, else_scope):
                for name, v in arm_scope.values.items():
                    if v.producer is None:
                        continue
                    outer = pre_if.get(name)
                    if (outer is not v and v.vid not in exported
                            and v.vid not in scope.closed):
                        scope.closed.setdefault(
                            v.vid, f"if-arm at {stmt.loc}")
        elif isinstance(stmt, Loop):
            if stmt.cond is not None:
                # while form: cond is the initial condition value; the body
                # re-evaluates it each iteration by redefining its name
                _check_use(stmt.cond, "'while' condition", stmt.loc, scope,
                           errors)
                if not stmt.cond.type.is_bool():
                    errors.append(TirError(
                        Invariant.TYPE_CONTRADICTION, stmt.loc,
                        "'while' condition must be i1"))
                if stmt.cond.shape != ():
                    errors.append(TirError(
                        Invariant.TYPE_CONTRADICTION, stmt.loc,
                        "'while' condition must be scalar (rank 0); a block "
                        "condition is not a legal Triton loop condition"))
                if any(b is not None for b in (stmt.lower, stmt.upper,
                                               stmt.step)):
                    errors.append(TirError(
                        Invariant.MALFORMED, stmt.loc,
                        "a while-form loop carries a condition and no "
                        "lower/upper/step bounds"))
                if not (set(stmt.cond.scope_names())
                        & {n for n, _ in stmt.carried}):
                    errors.append(TirError(
                        Invariant.CARRIED_WITHOUT_JOIN, stmt.loc,
                        f"while-loop at {stmt.loc} does not carry its "
                        f"condition '{stmt.cond.name}'; the body could never "
                        "update the tested value (infinite loop form)"))
            else:
                for what, bound in (("'loop' lower bound", stmt.lower),
                                    ("'loop' upper bound", stmt.upper),
                                    ("'loop' step", stmt.step)):
                    if bound is None:
                        errors.append(TirError(
                            Invariant.MALFORMED, stmt.loc,
                            f"{what} is required by the counted range form "
                            "(only the while form omits bounds)"))
                        continue
                    _check_use(bound, what, stmt.loc, scope, errors)
                    if not bound.type.is_index():
                        errors.append(TirError(
                            Invariant.TYPE_CONTRADICTION, stmt.loc,
                            f"{what} must be i32/i64"))
                    if bound.shape != ():
                        errors.append(TirError(
                            Invariant.TYPE_CONTRADICTION, stmt.loc,
                            f"{what} must be scalar (rank 0); loop bounds "
                            "are per-program scalars")
                        )
                # the descending flag is pinned to the step's compile-time
                # sign (T033): a negative constant step must be declared
                # descending, and a declared descent must carry one
                step_prod = stmt.step.producer if stmt.step is not None \
                    else None
                step_const = step_prod.attrs.get("value") \
                    if step_prod is not None and step_prod.op == "const" \
                    else None
                if isinstance(step_const, int) and not isinstance(
                        step_const, bool):
                    if step_const == 0:
                        errors.append(TirError(
                            Invariant.MALFORMED, stmt.loc,
                            "'loop' step is zero"))
                    elif (step_const < 0) != stmt.descending:
                        errors.append(TirError(
                            Invariant.MALFORMED, stmt.loc,
                            f"'loop' step {step_const} disagrees with the "
                            f"descending flag ({stmt.descending}); a "
                            "negative constant step must be declared "
                            "descending"))
                elif stmt.descending:
                    errors.append(TirError(
                        Invariant.MALFORMED, stmt.loc,
                        "a descending 'loop' requires a compile-time "
                        "negative step"))
            body_scope = scope.copy()
            for name, init in stmt.carried:
                _check_use(init, f"'loop' carried initial value '{name}'",
                           stmt.loc, scope, errors)
                body_scope.define(name, init)
            _verify_block(stmt.body, body_scope, errors,
                          region=f"{region} / loop-body")
            # the pre-loop bindings (the join results below re-bind the
            # scope; the close rule must compare against what the names
            # bound before the loop -- see the if's pre_if note)
            pre_loop = dict(scope.values)
            results = []
            provided = tuple(stmt.join_results)
            for i, (name, init) in enumerate(stmt.carried):
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
                if i < len(provided):
                    jv = provided[i]
                    if jv.type != final.type or \
                            value_shape(jv.shape) != value_shape(final.shape):
                        errors.append(TirError(
                            Invariant.TYPE_CONTRADICTION, stmt.loc,
                            f"loop-carried '{name}' result does not match "
                            f"the body's binding ({jv.type!r} vs "
                            f"{final.type!r})"))
                        continue
                else:
                    jv = Value(final.type, final.shape, stmt.loc, name=name)
                jv.add_alias(name)
                results.append(jv)
                # T043: same rule as the if join and op results -- the
                # join value's scope names (aliases included) all bind at
                # the join, so a later arm's alias-only assignment of one
                # of those names resolves against this value
                for key in jv.scope_names():
                    scope.define(key, jv)
            if provided and len(provided) != len(results):
                errors.append(TirError(
                    Invariant.MALFORMED, stmt.loc,
                    f"the loop at {stmt.loc} carries {len(provided)} join "
                    f"result(s) for {len(stmt.carried)} carried name(s)"))
            stmt.join_results = tuple(results)
            exported = {jv.vid for jv in results}
            for name, v in body_scope.values.items():
                if v.producer is None:
                    continue
                outer = pre_loop.get(name)
                if (outer is not v and v.vid not in exported
                        and v.vid not in scope.closed):
                    scope.closed.setdefault(v.vid, f"loop body at {stmt.loc}")
        elif isinstance(stmt, Op):
            for i, operand in enumerate(stmt.operands):
                _check_use(operand, f"op '{stmt.op}' operand {i}", stmt.loc,
                           scope, errors)
            _type_rule_errors(stmt, errors)
            if stmt.op in ("load", "store", "atomic_rmw", "atomic_cas"):
                _require_real(stmt.operands[0], "memory pointer operand",
                              stmt, errors)
                if stmt.op in ("store", "atomic_rmw", "atomic_cas"):
                    _require_real(stmt.operands[1],
                                  f"{stmt.op} value operand", stmt, errors)
            if stmt.op == "gather":
                _require_real(stmt.operands[1], "gather index operand",
                              stmt, errors)
            for r in stmt.results:
                for key in r.scope_names():
                    scope.define(key, r)
        else:
            errors.append(TirError(Invariant.MALFORMED, None,
                                   f"unknown statement {stmt!r}"))
