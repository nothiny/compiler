"""The provenance-tracking case-layer grid model (frontend, T008/T027).

The bundle carries views and scalars but not the grid (a100-native-io/v1,
F046/F047) and the identity contract excludes it (the corpus's own
economics, T003 section 7), so the grid must be *evaluated natively at run
time* from bundle-visible quantities.  This module extracts the grid
*expression* from the operator's case layer (``_make_case``) by
interpreting its AST under a provenance-tracking evaluator:

  - the case parameters (``shape``, ``dtype``, ``seed``) enter symbolically;
  - every value the grid expression consumes must be proven equal to a
    bundle-visible quantity -- a scalar argument or a view extent -- by the
    interpreter's own equality (a shared ``SymVal`` object or a structurally
    equal grid-expression tree), or to an identity-tier constant (a
    ``meta``/``launch_meta``/chosen-config constexpr, which the
    specialization identity signs, exactly like the ``lambda meta:`` form
    folds them);
  - values the interpreter cannot see stay as ``Hole`` leaves carrying the
    operand's identity, so a scalar argument, a view extent or a meta
    constant that provably equals the holed value fills it at run time
    (or as the folded constant); an unfilled hole refuses, located,
    naming it;
  - a compile-time equality self-check re-evaluates every *rewritten* axis
    expression (the exact tree the native routine computes) with the
    compiling case's concrete bundle values and requires it to equal the
    case's own declared ``grid``.

Corpus grid forms covered: multi-axis tuples, ``triton.cdiv`` products,
the ``lambda meta:`` form (meta constexpr leaves are identity-tier
constants, like every other constexpr the specialization folds), shape
derived locals (``n = int(shape[0])``, ``np.prod``, unpacking,
``map(int, shape)``), view extents (``x.shape[0]``, arrays created from
tracked sizes, the two-pass binding of opaque arrays), scalar arguments,
``min``/``max`` chains (any arity) and ``np.ceil(a / b)``; module-level
helper functions the case layer calls (``_case``, ``_aligned``,
``_dims``, ...) are interpreted in the same domain under a step budget;
dict literals with ``**`` spreads merge their mappings; ``for`` loops
over concrete ranges, tracked tuples, concrete lists and ``dict.items()``
unroll, and loops with symbolic bounds conservatively opaque-ify the
names they rebind (an unfillable hole, never a guess); branch merges keep
the provenance both arms agree on.

T033 extends the tie surface (each mechanism is structural -- the
interpreter's own provenance, never a value guess; the compile-time
self-check validates every model against the case's declared grid):

  * a symbolic conditional (``int(shape[0]) if len(shape) > 1 else 3``
    -- the mixed-arity SHAPES form) stays IDENTITY-PRESERVING as a hole
    owned by its own value, fillable by anything the interpreter proved
    equal (cholesky's B flows into STATUS's extent through
    ``np.asarray``); the ``1 if a % k else 0`` indicator combines with
    ``a // k`` into the exact cdiv form (the np.ceil identity);
  * elementwise array arithmetic (``x * 32``, ``np.rint``, ``np.clip``
    over one tracked array with provably-scalar others) preserves the
    per-axis extents, and ``x.reshape(-1)`` flattens to the extent
    product -- the value-massaging chains no longer hide the view
    extents;
  * the QUOTIENT solve: an axis factor the tie tables cannot read
    directly -- an untied shape leaf (rows: only rows*n is visible, n
    rides a scalar), a holed conditional (fht's R: only R*D is visible,
    D is a meta constant) or a product subtree (csr's B*M: only B*M*C
    is visible, M and C are scalars) -- reads as
    ``view_extent // cofactor`` when it appears exactly once as a factor
    of a structurally tracked view-extent product with every other
    factor runtime-readable.  The division is exact (the interpreter
    itself formed the product), the runtime reads the actual extent and
    cofactors, and gn_finalize's product-only shape factors (neither n
    nor g separable) still refuse, located.

A grid input that cannot be tied to a bundle-visible quantity is refused
with a located diagnostic (MECH-DIAGNOSTIC-REFUSAL), never baked; the
extraction/refusal census (:func:`census`) makes both sides countable.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

from a100c.frontend.source import OperatorSource

__all__ = ["GridError", "GridExpr", "Lit", "Ref", "Bin", "MinMax", "Hole",
           "GridModel", "extract_grid", "evaluate_expr", "census",
           "grid_of_case"]


class GridError(Exception):
    """A located refusal from the grid model."""

    def __init__(self, path: str, line: int, col: int, construct: str,
                 message: str):
        super().__init__(f"{path}:{line}:{col}: {construct}: {message}")
        self.path = path
        self.line = line
        self.col = col
        self.construct = construct
        self.message = message


# ---------------------------------------------------------------------------
# The grid expression tree (what the native routine computes at run time)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Lit:
    value: int

    def __repr__(self):
        return repr(self.value)


@dataclass(frozen=True)
class Ref:
    """A symbolic leaf: the case-layer origin of one runtime input."""

    kind: str          # 'shape_extent' | 'case_param' | 'view_extent'
    key: Tuple         # (axis,) / (name,) / (view_name, axis)

    def __repr__(self):
        return f"${self.kind}{self.key}"


@dataclass(frozen=True)
class Bin:
    op: str            # 'add' | 'sub' | 'mul' | 'floordiv'
    left: object
    right: object

    def __repr__(self):
        return f"({self.left!r} {self.op} {self.right!r})"


@dataclass(frozen=True)
class MinMax:
    """max(a, b) / min(a, b) over the runtime grid inputs (the native
    routine realizes it with the declared compare/mask/select scalar
    sequence)."""

    op: str            # 'max' | 'min'
    left: object
    right: object

    def __repr__(self):
        return f"{self.op}({self.left!r}, {self.right!r})"


@dataclass(frozen=True)
class ModNonzero:
    """``1 if a % k else 0`` -- the nonzero indicator of a mod-k remainder
    over the grid's non-negative domain (T033).  Alone it is not a runtime
    grid op; it combines with ``a // k`` (an add whose floordiv side carries
    the same operands) into the exact cdiv form ``(a + k - 1) // k`` -- the
    same positive-domain identity the ``np.ceil(a / b)`` handler uses.  A
    surviving indicator refuses, located, at the tie stage."""

    left: object
    right: object

    def __repr__(self):
        return f"mod_nonzero({self.left!r}, {self.right!r})"


class Hole:
    """An untracked subexpression, kept by the *identity* of the interpreted
    value that produced it (T027).

    Arithmetic the interpreter cannot see no longer collapses the whole
    expression to an opaque value: the tree keeps its shape with holes at
    the untracked operands.  A hole is fillable by anything the interpreter
    proved EQUAL to its owner -- the same ``SymVal`` flowing into a scalar
    argument (``tiles = cdiv(n, blk); args = {"num_tasks": tiles}``), into a
    view extent, or into a meta constexpr the identity signs.  Equality of
    two holes is equality of their owners (one interpreted value), never of
    their descriptions.
    """

    __slots__ = ("owner", "desc")

    def __init__(self, owner, desc: str):
        self.owner = owner      # the SymVal whose value the hole stands for
        self.desc = desc

    def __eq__(self, other):
        return isinstance(other, Hole) and other.owner is self.owner

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return id(self.owner)

    def __repr__(self):
        return f"?({self.desc})"


GridExpr = object


def evaluate_expr(expr, values: Dict):
    """Evaluate a grid expression with concrete leaf values."""
    if isinstance(expr, Lit):
        return expr.value
    if isinstance(expr, Ref):
        if expr.key not in values:
            raise KeyError(f"no concrete value for {expr!r}")
        return values[expr.key]
    if isinstance(expr, Bin):
        lhs = evaluate_expr(expr.left, values)
        rhs = evaluate_expr(expr.right, values)
        if expr.op == "add":
            return lhs + rhs
        if expr.op == "sub":
            return lhs - rhs
        if expr.op == "mul":
            return lhs * rhs
        if expr.op == "floordiv":
            return lhs // rhs
    if isinstance(expr, MinMax):
        lhs = evaluate_expr(expr.left, values)
        rhs = evaluate_expr(expr.right, values)
        return max(lhs, rhs) if expr.op == "max" else min(lhs, rhs)
    if isinstance(expr, Hole):
        raise ValueError(f"unfilled grid hole: {expr!r}")
    if isinstance(expr, ModNonzero):
        raise ValueError(f"an uncombined mod-nonzero indicator: {expr!r}")
    raise ValueError(f"not a grid expression: {expr!r}")


# ---------------------------------------------------------------------------
# The provenance-tracking value domain
# ---------------------------------------------------------------------------


class SymVal:
    """One interpreted value: concrete payload or symbolic origin, plus the
    grid-expression tree it would contribute (None when untracked)."""

    __slots__ = ("origin", "gexpr", "concrete", "opaque")

    def __init__(self, origin=None, gexpr=None, concrete=None, opaque=None):
        self.origin = origin        # Ref or None
        self.gexpr = gexpr          # GridExpr or None
        self.concrete = concrete    # concrete Python value when known
        self.opaque = opaque        # description for opaque values

    @property
    def tracked(self) -> bool:
        return self.gexpr is not None

    def __repr__(self):
        if self.opaque is not None:
            return f"<opaque {self.opaque}>"
        if self.origin is not None:
            return f"<sym {self.origin!r}>"
        return repr(self.concrete)


class SymTuple(SymVal):
    """A tracked tuple (e.g. the shape parameter, the grid assignment)."""

    __slots__ = ("items",)

    def __init__(self, items: List[SymVal], origin=None):
        concrete = tuple(i.concrete for i in items) \
            if all(i.concrete is not None for i in items) else None
        super().__init__(origin=origin, concrete=concrete)
        self.items = items


class SymDict(SymVal):
    """A tracked dict (e.g. the args literal, the meta payload)."""

    __slots__ = ("mapping",)

    def __init__(self, mapping: Dict[str, SymVal]):
        super().__init__()
        self.mapping = dict(mapping)


class SymArray(SymVal):
    """An array whose per-axis extents carry provenance.

    ``extents`` are per-axis SymVals (tracked when the creating expression
    was tracked); ``view`` names the args entry the array flows into (set
    by the two-pass view binding).
    """

    __slots__ = ("extents", "view")

    def __init__(self, extents: List[SymVal], view: Optional[str] = None):
        super().__init__()
        self.extents = extents
        self.view = view


class SymLambda(SymVal):
    """A ``lambda meta: ...`` value with its closure environment."""

    __slots__ = ("node", "closure")

    def __init__(self, node: ast.Lambda, closure: Dict[str, SymVal]):
        super().__init__(opaque="lambda")
        self.node = node
        self.closure = closure


class SymFunc(SymVal):
    """A module-level helper function of the operator file (``_case``,
    ``_aligned``, ``_dims``, ...), callable in the provenance domain under
    the interpreter's step budget.  The jit kernel is never a SymFunc (it
    is the compile unit, not case-layer code)."""

    __slots__ = ("node",)

    def __init__(self, node: ast.FunctionDef):
        super().__init__(opaque=f"function {node.name}")
        self.node = node


class SymIter(SymVal):
    """A bound ``dict.items()`` / ``.keys()`` / ``.values()`` view over a
    tracked dict -- enumerable by a case-layer ``for`` loop."""

    __slots__ = ("base", "mode")

    def __init__(self, base: SymVal, mode: str):
        super().__init__(opaque=f".{mode}")
        self.base = base
        self.mode = mode


def _lit(value) -> SymVal:
    # integer literals carry a grid expression so arithmetic can mix them
    # with symbolic leaves (n + 128 - 1) // 128
    gexpr = Lit(value) if isinstance(value, int) and not isinstance(value, bool) \
        else None
    return SymVal(concrete=value, gexpr=gexpr)


def _opaque(desc: str) -> SymVal:
    return SymVal(opaque=desc)


def _is_array_like(value: SymVal) -> bool:
    return isinstance(value, SymArray) or value.opaque is not None


def _scalar_shaped(value: SymVal) -> bool:
    """A value that participates in arithmetic as a PROVABLE scalar: a
    concrete number, a tracked scalar (gexpr set -- leaves and holes) or
    a plain untracked scalar.  A pure OPAQUE value is not provably
    scalar -- it may be an array of unknown shape (``q +
    np.transpose(q)``: the transposed side is opaque), so an
    extent-preserving rule must not fire on it."""
    if isinstance(value, (SymArray, SymTuple, SymDict, SymIter, SymFunc,
                          SymLambda)):
        return False
    return value.opaque is None or value.concrete is not None \
        or value.gexpr is not None


#: numpy elementwise functions whose call preserves the first array
#: argument's per-axis extents when every other argument is scalar-shaped
#: (the case layer's value-massaging chains: np.rint / np.clip / ... --
#: structural shape facts, case-independent, so a tie built on them is
#: invariant across an identity's cases).  np.ceil has its own cdiv
#: handler below and is deliberately absent (so does every other
#: scalar-only massager the grid expression itself consumes).
_NP_ELEMENTWISE = {"abs", "fabs", "rint", "sqrt", "cbrt", "exp", "expm1",
                   "log", "log1p", "log2", "log10", "sin", "cos", "tan",
                   "asin", "acos", "atan", "sinh", "cosh", "tanh",
                   "arctanh", "clip", "maximum", "minimum", "nan_to_num",
                   "copy", "ascontiguousarray", "signbit", "sign", "conj",
                   "real", "imag", "isfinite", "isinf", "isnan"}


_TRACE_BUILTINS = {"int", "tuple", "len", "min", "max", "abs", "dict",
                   "str", "round", "float", "bool"}

#: numpy/np constructors whose shape argument positions are modeled
_NP_CTORS = {"zeros", "empty", "ones", "full", "zeros_like", "empty_like",
             "ones_like", "arange", "tile", "repeat"}

#: np scalar dtype casts: a value-preserving cast of one tracked scalar
#: (``np.int32(n)`` as a kernel argument keeps ``n``'s provenance -- the
#: grid model ties the argument to the same bundle-visible quantity)
_NP_SCALAR_CASTS = {"bool_", "int8", "int16", "int32", "int64",
                    "uint8", "uint16", "uint32", "uint64",
                    "float16", "float32", "float64", "int_", "float_"}

#: rng methods whose last positional argument is the size (the corpus's
#: observed draw surface: standard_normal/normal/integers/uniform/random/
#: permutation/choice -- plus the common aliases)
_RNG_SIZE_METHODS = {"standard_normal", "normal", "integers", "uniform",
                     "random", "rand", "randn", "choice", "permutation",
                     "beta", "gamma", "poisson", "exponential", "laplace",
                     "logistic", "triangular", "weibull", "multinomial"}

#: pure functions whose call result is memoized per *argument identity*:
#: one interpreted value always yields one result, so two textual
#: occurrences of ``triton.next_power_of_2(x)`` over the same ``x`` are the
#: SAME value (the tie the grid model needs -- one occurrence flowing into
#: ``meta`` and one into the grid expression)
_PURE_CALLS = {"triton.next_power_of_2"}

#: interpretation bounds (a helper beyond them is opaque, never a hang):
_HELPER_STEP_BUDGET = 4000     # statements per helper-function invocation
_HELPER_DEPTH = 6              # helper-call nesting
_LOOP_ITERATION_CAP = 10000    # concrete loop unrolling per statement


class _HelperBudget(Exception):
    """Internal: a helper-function interpretation exceeded its budget."""


class _LoopContinue(Exception):
    """Internal: a ``continue`` inside an unrolling case-layer loop."""


class _LoopBreak(Exception):
    """Internal: a ``break`` inside an unrolling case-layer loop."""


def _loop_effect_names(stmt: ast.For) -> Tuple[List[str], List[str]]:
    """Statically collect the names a loop body affects: (rebound, stored).

    ``rebound``: names assigned/aug-assigned/imported (or bound by a nested
    loop/comprehension) anywhere in the body -- their values depend on the
    unknown iteration count.  ``stored``: names element-stored into via a
    subscript (``args[name] = ...``) -- their containers mutated.
    """
    rebound: List[str] = []
    stored: List[str] = []

    def _target_name(t: ast.expr):
        return t.id if isinstance(t, ast.Name) else None

    def _walk(node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                targets = child.targets if isinstance(child, ast.Assign) \
                    else [child.target]
                for t in targets:
                    if isinstance(t, ast.Subscript):
                        n = _target_name(t.value)
                        if n is not None:
                            stored.append(n)
                    else:
                        for n in ast.walk(t):
                            name = _target_name(n) if isinstance(n, ast.Name) \
                                else None
                            if name is not None:
                                rebound.append(name)
            elif isinstance(child, (ast.Import, ast.ImportFrom)):
                for alias in child.names:
                    rebound.append(alias.asname or alias.name.split(".")[0])
            elif isinstance(child, (ast.FunctionDef, ast.ClassDef)):
                rebound.append(child.name)
            _walk(child)

    _walk(stmt)
    # the loop's own induction variable(s) are rebound per iteration
    for n in ast.walk(stmt.target):
        name = _target_name(n) if isinstance(n, ast.Name) else None
        if name is not None:
            rebound.append(name)
    return rebound, stored


class _Interpreter:
    """Evaluates ``_make_case``'s statements in the provenance domain."""

    def __init__(self, source: OperatorSource,
                 module_constants: Dict[str, object],
                 module_functions: Optional[Dict[str, ast.FunctionDef]] = None):
        self.source = source
        self.constants = module_constants
        self.env: Dict[str, SymVal] = {}
        self.path = source.path
        #: module-level helper functions (name -> def), budget-interpreted
        self.module_functions: Dict[str, ast.FunctionDef] = \
            module_functions or {}
        #: the args-literal entries: arg name -> the SymVal object flowing in
        self.arg_values: Dict[str, SymVal] = {}
        #: the returned payload dict (grid may live there as a lambda)
        self.returned: Optional[SymDict] = None
        #: the raw return value of the interpreted function
        self.retval: Optional[SymVal] = None
        #: interpretation bookkeeping (budgets, depth, pure-call memo)
        self._steps = 0
        self._depth = 0
        self._pure_memo: Dict[tuple, SymVal] = {}

    # -- helpers --------------------------------------------------------------
    def _err(self, node, construct: str, message: str) -> GridError:
        return GridError(self.path, getattr(node, "lineno", 0) or 1,
                         (getattr(node, "col_offset", 0) or 0) + 1,
                         construct, message)

    def _module_value(self, name: str) -> Optional[SymVal]:
        if name in self.constants:
            return self._from_concrete(self.constants[name])
        return None

    def _from_concrete(self, value) -> SymVal:
        if isinstance(value, bool) or isinstance(value, (int, float, str)):
            return _lit(value)
        if isinstance(value, (list, tuple)):
            items = [self._from_concrete(v) for v in value]
            return SymTuple(items)
        if isinstance(value, dict):
            return SymDict({k: self._from_concrete(v)
                            for k, v in value.items()})
        return _opaque(repr(value))

    # -- statements -----------------------------------------------------------
    def run(self, fn: ast.FunctionDef, params: Dict[str, SymVal],
            prelude: Optional[Dict[str, SymVal]] = None) -> Dict[str, SymVal]:
        self.env = dict(params)
        if prelude:
            self.env.update(prelude)
        for stmt in fn.body:
            if isinstance(stmt, ast.Return):
                value = self._eval(stmt.value)
                self.retval = value
                if isinstance(value, SymDict):
                    self.returned = value
                break
            self._stmt(stmt)
        return self.env

    def _stmt(self, stmt: ast.stmt) -> None:
        self._steps += 1
        if isinstance(stmt, ast.Assign):
            value = self._eval(stmt.value)
            for target in stmt.targets:
                self._assign(target, value)
        elif isinstance(stmt, ast.AnnAssign):
            if stmt.value is not None:
                self._assign(stmt.target, self._eval(stmt.value))
        elif isinstance(stmt, ast.AugAssign):
            if isinstance(stmt.target, ast.Name):
                current = self.env.get(stmt.target.id)
                if current is None:
                    raise self._err(stmt, "augmented assignment",
                                    "target is not defined")
                binop = ast.BinOp(left=stmt.target, op=stmt.op,
                                  right=stmt.value)
                ast.copy_location(binop, stmt)
                self._assign(stmt.target, self._eval(binop))
            elif isinstance(stmt.target, ast.Subscript):
                # an in-place element update (``x[:, np.arange(K),
                # np.arange(K)] += 2`` in the case layer): the read and the
                # operand evaluate for provenance, then the store follows
                # _assign's own subscript rule -- a tracked tuple refuses,
                # a tracked array's extents are unchanged (numpy element
                # stores never reshape), an opaque object mutates in place
                # and stays opaque (a grid axis consuming it refuses,
                # located, at the axis check)
                binop = ast.BinOp(left=stmt.target, op=stmt.op,
                                  right=stmt.value)
                ast.copy_location(binop, stmt)
                self._eval(binop)
                self._assign(stmt.target, _opaque("augmented store"))
            else:
                raise self._err(stmt, "augmented assignment",
                                "assignment target outside the grid model")
        elif isinstance(stmt, ast.Delete):
            for t in stmt.targets:
                if isinstance(t, ast.Name):
                    self.env.pop(t.id, None)
        elif isinstance(stmt, ast.Import) or isinstance(stmt, ast.ImportFrom):
            for alias in stmt.names:
                if alias.asname:
                    self.env[alias.asname] = _opaque(f"module {alias.name}")
        elif isinstance(stmt, ast.Expr):
            self._eval(stmt.value)
        elif isinstance(stmt, ast.Pass):
            return
        elif isinstance(stmt, ast.Continue):
            # only meaningful inside an unrolling loop driver; a bare
            # continue outside one is a case-layer form the model refuses
            raise _LoopContinue()
        elif isinstance(stmt, ast.Break):
            raise _LoopBreak()
        elif isinstance(stmt, ast.If):
            cond = self._eval(stmt.test)
            if cond.concrete is None:
                # a symbolic guard: one arm only raises (validation of the
                # case inputs).  The case payload exists, so the guard did
                # not fire -- the fall-through arm is the one that ran.
                body_guard = all(isinstance(s, (ast.Raise, ast.Pass,
                                                ast.Assert))
                                 for s in stmt.body) and stmt.body
                else_guard = all(isinstance(s, (ast.Raise, ast.Pass,
                                                ast.Assert))
                                 for s in stmt.orelse) and stmt.orelse
                if body_guard and not else_guard:
                    for s in stmt.orelse:
                        self._stmt(s)
                elif else_guard and not body_guard:
                    for s in stmt.body:
                        self._stmt(s)
                else:
                    # real work on both arms: interpret BOTH and keep the
                    # provenance the arms agree on -- the same object, or
                    # structurally equal grid expressions, or arrays whose
                    # per-axis extents agree, or dicts merged per key by the
                    # same rule (the corpus's dtype-normalization idiom
                    # rewrites every array entry extent-preserving, so the
                    # views survive the branch).  A genuinely
                    # branch-dependent value is untracked -- a grid axis
                    # consuming it refuses, located, at the axis check.
                    snap = dict(self.env)
                    for s in stmt.body:
                        self._stmt(s)
                    then_env = dict(self.env)
                    self.env = dict(snap)
                    for s in stmt.orelse:
                        self._stmt(s)
                    else_env = dict(self.env)
                    merged = dict(snap)
                    for key in set(then_env) | set(else_env):
                        t, e = then_env.get(key), else_env.get(key)
                        if t is None or e is None:
                            merged[key] = _opaque("branch-dependent value")
                            continue
                        v = self._merge_branch_values(t, e)
                        merged[key] = v if v is not None else _opaque(
                            "branch-dependent value")
                    self.env = merged
            elif cond.concrete:
                for s in stmt.body:
                    self._stmt(s)
            else:
                for s in stmt.orelse:
                    self._stmt(s)
        elif isinstance(stmt, ast.For):
            self._for(stmt)
        elif isinstance(stmt, (ast.While, ast.AsyncFor)):
            raise self._err(stmt, type(stmt).__name__.lower(),
                            "loops in the case layer are outside the grid "
                            "model")
        elif isinstance(stmt, (ast.While, ast.AsyncFor)):
            raise self._err(stmt, type(stmt).__name__.lower(),
                            "loops in the case layer are outside the grid "
                            "model")
        else:
            raise self._err(stmt, type(stmt).__name__,
                            "statement is outside the grid model")

    # -- for loops ---------------------------------------------------------------
    def _iter_items(self, iter_node: ast.expr) -> Optional[List[SymVal]]:
        """The enumerable items of one iterable expression (a concrete
        ``range()``, a tracked tuple, a concrete list/tuple); None when
        the model cannot enumerate it (T034: shared by the statement-loop
        unrolling and the general comprehension evaluation)."""
        if isinstance(iter_node, ast.Call) \
                and isinstance(iter_node.func, ast.Name) \
                and iter_node.func.id == "range":
            vals = []
            for a in iter_node.args:
                v = self._eval(a)
                if v.concrete is None or not isinstance(v.concrete, int) \
                        or isinstance(v.concrete, bool):
                    return None
                vals.append(v.concrete)
            start = vals[0] if len(vals) > 1 else 0
            stop = vals[1] if len(vals) > 1 else vals[0]
            step = vals[2] if len(vals) > 2 else 1
            if not step:
                return None
            return [_lit(k) for k in range(start, stop, step)]
        it = self._eval(iter_node)
        if isinstance(it, SymTuple):
            return list(it.items)
        if it.concrete is not None and isinstance(it.concrete, (list, tuple)) \
                and not isinstance(it.concrete, str):
            return [self._from_concrete(v) for v in it.concrete]
        return None

    def _for(self, stmt: ast.For) -> None:
        """A case-layer ``for`` loop.

        * ``range(...)`` with concrete bounds, tracked tuples, concrete
          lists/tuples and ``dict.items()/.keys()/.values()`` unroll: the
          body runs per iteration with the real interpreted values (the
          corpus's dtype-normalization idiom).
        * ``range(...)`` with a symbolic bound cannot be enumerated: every
          name the body rebinds (and every dict it element-stores into)
          becomes opaque -- the loop ran an unknown number of times, so a
          grid value depending on its bindings is unfillable, never a
          guess.  Arrays keep their extents (numpy element stores never
          reshape).
        * anything else the model cannot enumerate refuses, located.
        """
        rng = stmt.iter
        # -- range() loops ------------------------------------------------------
        if isinstance(rng, ast.Call) and isinstance(rng.func, ast.Name) \
                and rng.func.id == "range":
            vals = []
            symbolic = False
            for a in rng.args:
                v = self._eval(a)
                if v.concrete is None or not isinstance(v.concrete, int) \
                        or isinstance(v.concrete, bool):
                    symbolic = True
                    break
                vals.append(v.concrete)
            if not symbolic:
                start = vals[0] if len(vals) > 1 else 0
                stop = vals[1] if len(vals) > 1 else vals[0]
                step = vals[2] if len(vals) > 2 else 1
                count = abs((stop - start) // step) if step else 0
                if count > _LOOP_ITERATION_CAP:
                    # a concrete but unbounded-in-practice loop: the same
                    # conservative treatment as a symbolic bound
                    self._opaque_loop_effects(stmt)
                    return
                self._unroll(stmt, lambda k: _lit(k), start, stop, step)
                return
            self._opaque_loop_effects(stmt)
            return
        # -- enumerable values (tracked tuples, dict views, concrete lists) ----
        iterated = self._eval(rng)
        items: Optional[List[SymVal]] = None
        if isinstance(iterated, SymTuple):
            items = list(iterated.items)
        elif isinstance(iterated, SymIter) \
                and isinstance(iterated.base, SymDict):
            mapping = iterated.base.mapping
            if iterated.mode == "items":
                items = [SymTuple([_lit(k), v])
                         for k, v in mapping.items()]
            elif iterated.mode == "keys":
                items = [_lit(k) for k in mapping]
            else:
                items = list(mapping.values())
        elif iterated.concrete is not None \
                and isinstance(iterated.concrete, (list, tuple)) \
                and not isinstance(iterated.concrete, str):
            items = [self._from_concrete(v) for v in iterated.concrete]
        if items is None:
            # T034: an iterable the model cannot enumerate (enumerate/
            # zip over opaque lists, an opaque call's result) gets the
            # same conservative treatment as a symbolic range bound:
            # every name the body rebinds becomes opaque, so a grid axis
            # consuming one refuses at the axis tie (unfillable, never a
            # guess) while a loop the grid does not consume no longer
            # blocks extraction (grouped_mm/grouped_gemm's allocations
            # loop -- the grid reads total_tiles, computed before it).
            self._opaque_loop_effects(stmt)
            return
        if len(items) > _LOOP_ITERATION_CAP:
            self._opaque_loop_effects(stmt)
            return
        try:
            for item in items:
                self._bind_loop_target(stmt.target, item)
                try:
                    for s in stmt.body:
                        self._stmt(s)
                except _LoopContinue:
                    pass
        except _LoopBreak:
            pass
        finally:
            self._restore_loop_target(stmt.target)

    def _unroll(self, stmt: ast.For, value_of, start, stop, step) -> None:
        if not isinstance(stmt.target, ast.Name):
            raise self._err(stmt, "for",
                            "the loop target must be a plain name")
        name = stmt.target.id
        saved = self.env.get(name)
        k = start
        try:
            while (step > 0 and k < stop) or (step < 0 and k > stop):
                self.env[name] = value_of(k)
                try:
                    for s in stmt.body:
                        self._stmt(s)
                except _LoopContinue:
                    pass
                k += step
        except _LoopBreak:
            pass
        finally:
            if saved is not None:
                self.env[name] = saved
            else:
                self.env.pop(name, None)

    def _bind_loop_target(self, target: ast.expr, item: SymVal) -> None:
        if isinstance(target, ast.Name):
            self.env[target.id] = item
        elif isinstance(target, (ast.Tuple, ast.List)):
            if isinstance(item, SymTuple) \
                    and len(target.elts) == len(item.items):
                for t, v in zip(target.elts, item.items):
                    self._bind_loop_target(t, v)
            else:
                for t in target.elts:
                    self._bind_loop_target(t, _opaque("unpacked"))

    def _restore_loop_target(self, target: ast.expr) -> None:
        if isinstance(target, ast.Name):
            self.env.pop(target.id, None)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for t in target.elts:
                self._restore_loop_target(t)

    def _opaque_loop_effects(self, stmt: ast.For) -> None:
        """Conservatively apply a loop whose iteration count the model
        cannot see: every rebound name, and every dict element-stored into,
        becomes opaque (an unfillable hole if the grid consumes it)."""
        rebound, stored = _loop_effect_names(stmt)
        for name in rebound:
            self.env[name] = _opaque(f"loop-dependent value ({name})")
        for name in stored:
            base = self.env.get(name)
            if base is None or isinstance(base, SymArray):
                # an array's extents provably survive element stores; an
                # unbound name stays unbound
                if base is None:
                    self.env.pop(name, None)
                continue
            self.env[name] = _opaque(f"loop-dependent dict ({name})")

    # -- branch merging -----------------------------------------------------------
    def _merge_branch_values(self, t: SymVal, e: SymVal) -> Optional[SymVal]:
        """The provenance both branch arms agree on: the same object, or
        structurally equal grid expressions, or equal-provenance composites
        (arrays per-extent, dicts per-key, tuples per-item).  None when the
        arms genuinely disagree."""
        if t is e:
            return t
        if isinstance(t, SymArray) and isinstance(e, SymArray) \
                and len(t.extents) == len(e.extents) \
                and all(self._same_provenance(a, b)
                        for a, b in zip(t.extents, e.extents)):
            return t
        if isinstance(t, SymDict) and isinstance(e, SymDict):
            # per-key: the provenance both arms agree on survives; a key
            # only one arm added carries an untracked value; two untracked
            # (opaque) values keep the pre-branch object -- the two-pass
            # view binding rebinds the local holding it to the payload's
            # actual view, so the entry stays tieable
            merged = {}
            for k in sorted(set(t.mapping) | set(e.mapping)):
                tv, ev = t.mapping.get(k), e.mapping.get(k)
                if tv is None or ev is None:
                    merged[k] = _opaque("branch-dependent value")
                    continue
                v = self._merge_branch_values(tv, ev)
                if v is not None:
                    merged[k] = v
                elif tv.opaque is not None and ev.opaque is not None:
                    merged[k] = ev
                else:
                    merged[k] = _opaque("branch-dependent value")
            return SymDict(merged)
        if isinstance(t, SymTuple) and isinstance(e, SymTuple) \
                and len(t.items) == len(e.items):
            items = []
            for a, b in zip(t.items, e.items):
                v = self._merge_branch_values(a, b)
                if v is None:
                    return None
                items.append(v)
            return SymTuple(items)
        if t.gexpr is not None and t.gexpr == e.gexpr:
            return t
        return None

    @staticmethod
    def _same_provenance(a: SymVal, b: SymVal) -> bool:
        return a is b or (a.gexpr is not None and a.gexpr == b.gexpr)

    def _assign(self, target: ast.expr, value: SymVal) -> None:
        if isinstance(target, ast.Name):
            self.env[target.id] = value
        elif isinstance(target, ast.Tuple):
            if not isinstance(value, SymTuple):
                # unpacking an untracked value: the targets become
                # untracked too (a grid axis consuming one refuses,
                # located, at the axis check)
                for t in target.elts:
                    self._assign(t, _opaque("unpacked"))
                return
            if len(target.elts) != len(value.items):
                raise self._err(target, "assignment", "unpack arity mismatch")
            for t, v in zip(target.elts, value.items):
                self._assign(t, v)
        elif isinstance(target, ast.Subscript):
            base = self.env.get(self._name_of(target.value))
            if isinstance(base, SymTuple):
                raise self._err(target, "subscript store",
                                "mutation of a provenance-tracked tuple "
                                "invalidates the grid model")
            if isinstance(base, SymArray):
                # an element store into a tracked array: extents are
                # provably unchanged (numpy element stores never reshape)
                return
            if isinstance(base, SymDict) and isinstance(target.value, ast.Name):
                # an element store into a tracked dict: copy-on-write so a
                # branch arm's stores never leak into the other arm's view
                # of the same dict (the if-merge then recombines per key)
                index = self._eval(target.slice) \
                    if not isinstance(target.slice, ast.Slice) else None
                if index is not None and isinstance(index.concrete, str) \
                        and index.concrete:
                    new_dict = SymDict(dict(base.mapping))
                    new_dict.mapping[index.concrete] = value
                    self.env[target.value.id] = new_dict
                    return
                # a symbolic or slice key: the dict as a whole is untracked
                self.env[target.value.id] = _opaque(
                    "dict store with a symbolic key")
                return
            # a store into an opaque object (e.g. x[::11] = -0.0): untracked
        else:
            raise self._err(target, "assignment",
                            "assignment target outside the grid model")

    def _name_of(self, node) -> Optional[str]:
        return node.id if isinstance(node, ast.Name) else None

    @staticmethod
    def _int_passthrough(item: SymVal, func: str) -> SymVal:
        """int()/str()/... over one tracked item: the item passes through
        (concrete folded when known)."""
        if func == "int" and item.concrete is not None \
                and isinstance(item.concrete, int):
            return _lit(int(item.concrete))
        return item

    # -- expressions ------------------------------------------------------------
    def _eval(self, node: ast.expr) -> SymVal:
        if isinstance(node, ast.Constant):
            return _lit(node.value)
        if isinstance(node, ast.Lambda):
            return SymLambda(node, dict(self.env))
        if isinstance(node, ast.Name):
            if node.id in self.env:
                return self.env[node.id]
            module_value = self._module_value(node.id)
            if module_value is not None:
                return module_value
            if node.id in self.module_functions:
                return SymFunc(self.module_functions[node.id])
            # an unknown module-level name (an imported helper): untracked.
            # If the grid expression depended on it, the expression would
            # be untracked and the extraction refuses -- conservative,
            # never a guess.
            return _opaque(f"name {node.id}")
        if isinstance(node, (ast.Tuple, ast.List)):
            return SymTuple([self._eval(e) for e in node.elts])
        if isinstance(node, ast.Dict):
            mapping: Dict[str, SymVal] = {}
            for k, v in zip(node.keys, node.values):
                if k is None:
                    # a ``**spread`` entry: merge the spread mapping (later
                    # explicit keys win, exactly like Python dict literals)
                    spread = self._eval(v)
                    if not isinstance(spread, SymDict):
                        return _opaque("dict with an untracked **spread")
                    for sk, sv in spread.mapping.items():
                        mapping[sk] = sv
                    continue
                if not isinstance(k, ast.Constant):
                    # computed keys: the dict as a whole stays untracked
                    # (the args/meta ties it would carry are lost -- a grid
                    # needing them refuses, located, at the tie stage)
                    return _opaque("dict with computed keys")
                mapping[k.value] = self._eval(v)
            return SymDict(mapping)
        if isinstance(node, ast.BinOp):
            return self._binop(node)
        if isinstance(node, ast.UnaryOp):
            v = self._eval(node.operand)
            if v.concrete is None:
                return _opaque(f"unary {type(node.op).__name__.lower()}")
            if isinstance(node.op, ast.USub):
                return _lit(-v.concrete)
            if isinstance(node.op, ast.UAdd):
                return _lit(+v.concrete)
            if isinstance(node.op, ast.Not):
                return _lit(not v.concrete)
            if isinstance(node.op, ast.Invert):
                return _lit(~v.concrete)
        if isinstance(node, ast.Compare):
            left = self._eval(node.left)
            out = None
            for op, comp in zip(node.ops, node.comparators):
                right = self._eval(comp)
                if isinstance(op, (ast.Is, ast.IsNot)):
                    # identity against None is decidable in the domain
                    # (interpreter values are never Python None)
                    out = self._compare(op, left, right)
                    left = right
                    continue
                if left.concrete is None or right.concrete is None:
                    # a symbolic comparison: untracked (a guard may still
                    # prove it never fired; a grid axis consuming it
                    # refuses later -- conservative, never a guess)
                    return _opaque("comparison")
                out = self._compare(op, left.concrete, right.concrete)
                left = right
            return _lit(out)
        if isinstance(node, ast.IfExp):
            cond = self._eval(node.test)
            if cond.concrete is None:
                # a condition the model cannot see (the mixed-arity
                # ``int(shape[0]) if len(shape) > 1 else 3`` form -- the
                # arity is per-case, never guessable).  T033: the value
                # stays IDENTITY-PRESERVING instead of opaque -- a hole
                # owned by this very value, so a scalar argument, a view
                # extent or a meta constant the interpreter proves EQUAL
                # to it fills it at run time (cholesky's B flows into
                # STATUS's extent; fht's R fills from X_ptr // DIM).  The
                # branch-equal arms pass through; the ``1 if a % k else
                # 0`` indicator carries its operands for the cdiv
                # identity.  An unfilled hole still refuses, located.
                def _arm(n):
                    try:
                        return self._eval(n)
                    except GridError:
                        return None            # an arm that cannot even
                                               # evaluate (shape[1] of a
                                               # 1-axis shape): no
                                               # passthrough, no marker

                body = _arm(node.body)
                orelse = _arm(node.orelse)
                if body is not None and orelse is not None:
                    merged = self._merge_branch_values(body, orelse)
                    if merged is not None:
                        return merged
                    if isinstance(node.test, ast.BinOp) \
                            and isinstance(node.test.op, ast.Mod) \
                            and isinstance(body, SymVal) \
                            and isinstance(orelse, SymVal) \
                            and body.concrete == 1 and orelse.concrete == 0:
                        a = self._eval(node.test.left)
                        k = self._eval(node.test.right)
                        atree = self._scalar_gexpr_of(a)
                        ktree = self._scalar_gexpr_of(k)
                        if atree is not None and ktree is not None:
                            return SymVal(gexpr=ModNonzero(atree, ktree))
                out = SymVal(opaque="symbolic conditional expression")
                out.gexpr = Hole(out, "symbolic conditional expression")
                return out
            return self._eval(node.body if cond.concrete else node.orelse)
        if isinstance(node, ast.BoolOp):
            # and/or over case values with Python's short-circuit: a
            # concrete-falsy ``and`` operand (a decidable isinstance over
            # a scalar) decides the chain without the later sides -- the
            # corpus's dtype-normalization guard
            # (``isinstance(value, np.ndarray) and value.dtype.kind == "f"``)
            # is False for scalar entries, so their args binding survives
            out = None
            for v in node.values:
                s = self._eval(v)
                if s.concrete is None:
                    return _opaque("boolop")
                if isinstance(node.op, ast.And):
                    if not bool(s.concrete):
                        out = False
                        break
                else:
                    if bool(s.concrete):
                        out = True
                        break
            if out is None:
                out = isinstance(node.op, ast.And)
            return _lit(out)
        if isinstance(node, ast.Call):
            return self._call(node)
        if isinstance(node, ast.Subscript):
            return self._subscript(node)
        if isinstance(node, ast.Attribute):
            return self._attribute(node)
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
            # (int(v) for v in shape) / [int(v) for v in shape]: the
            # per-item passthrough of a tracked tuple
            if len(node.generators) == 1 and not node.generators[0].ifs \
                    and not node.generators[0].is_async:
                target = node.generators[0].target
                iterated = self._eval(node.generators[0].iter)
                if isinstance(target, ast.Name) and isinstance(iterated,
                                                               SymTuple):
                    elt = node.elt
                    if isinstance(elt, ast.Name) and elt.id == target.id:
                        return SymTuple(list(iterated.items))
                    if isinstance(elt, ast.Call) and isinstance(elt.func,
                                                                ast.Name) \
                            and elt.func.id == "int" \
                            and isinstance(elt.args[0], ast.Name) \
                            and elt.args[0].id == target.id:
                        return SymTuple([
                            self._int_passthrough(item, "int")
                            for item in iterated.items])
                if isinstance(node, ast.ListComp):
                    # T034: a general element expression over an
                    # enumerable iterable (a concrete range(), a tracked
                    # tuple) evaluates per item -- the corpus's
                    # dimension-list idiom
                    # (``[(base_m + 2*g, ...) for g in range(groups)]``)
                    # feeds grouped_gemm's tile-count sum.  The bound
                    # iteration cap keeps the evaluation bounded; a
                    # non-enumerable iterable stays opaque (the grid
                    # consuming it refuses, located).
                    items = self._iter_items(node.generators[0].iter)
                    if items is not None \
                            and len(items) <= _LOOP_ITERATION_CAP:
                        out = []
                        for item in items:
                            self._bind_loop_target(target, item)
                            try:
                                out.append(self._eval(node.elt))
                            finally:
                                self._restore_loop_target(target)
                        return SymTuple(out)
            return _opaque("comprehension")
        if isinstance(node, (ast.SetComp, ast.DictComp, ast.Starred,
                             ast.NamedExpr, ast.Slice)):
            # comprehensions over case data / slices: untracked (nothing
            # tracked escapes them; a grid axis consuming one refuses
            # later)
            return _opaque("comprehension")
        raise self._err(node, type(node).__name__,
                        "expression is outside the grid model")

    @staticmethod
    def _compare(op, lhs, rhs):
        import operator as _op
        table = {ast.Eq: _op.eq, ast.NotEq: _op.ne, ast.Lt: _op.lt,
                 ast.LtE: _op.le, ast.Gt: _op.gt, ast.GtE: _op.ge,
                 ast.In: lambda a, b: a in b,
                 ast.NotIn: lambda a, b: a not in b,
                 # 'x is None' guards in the direct make_case form: the
                 # interpreter's domain values are never Python None, so
                 # identity against None is concrete False
                 ast.Is: lambda a, b: a is b,
                 ast.IsNot: lambda a, b: a is not b}
        return table[type(op)](lhs, rhs)

    def _attribute(self, node: ast.Attribute) -> SymVal:
        base = self._eval(node.value)
        if isinstance(base, SymDict) \
                and node.attr in ("items", "keys", "values"):
            # an enumerable view over a tracked dict (the corpus's
            # dtype-normalization loop: ``for name, value in args.items()``)
            return SymIter(base, node.attr)
        if isinstance(base, SymArray):
            if node.attr == "shape":
                return SymTuple(list(base.extents))
            if node.attr == "size":
                return self._product(base.extents, node)
            if node.attr == "dtype" or node.attr == "ndim":
                return _opaque(f".{node.attr}")
        if isinstance(base, SymTuple) and node.attr == "size":
            return self._product(base.items, node)
        if base.concrete is not None and not hasattr(base, "items"):
            attr = getattr(base.concrete, node.attr, None)
            if attr is not None and not callable(attr):
                return _lit(attr)
        return _opaque(f"attribute .{node.attr}")

    def _product(self, items: List[SymVal], node) -> SymVal:
        """A tracked product (np.prod / .size): folds when concrete, holed
        otherwise (an untracked extent fills from a scalar/view/meta tie)."""
        if all(i.concrete is not None for i in items):
            out = 1
            for i in items:
                out = out * i.concrete
            return _lit(out)
        gexpr = None
        for i in items:
            term = self._scalar_gexpr_of(i)
            if term is None:
                return _opaque("product over a non-scalar extent")
            gexpr = term if gexpr is None else Bin("mul", gexpr, term)
        return SymVal(gexpr=gexpr)

    @staticmethod
    def _why(v: SymVal) -> str:
        if v.opaque:
            return v.opaque
        if v.origin is not None:
            return repr(v.origin)
        return "untracked"

    def _scalar_gexpr_of(self, v: SymVal):
        """The grid-expression tree of one scalar operand: its tracked
        expression, or a Hole carrying the value's identity when the model
        cannot see it.  None when the value is not scalar-shaped at all
        (an array, a tuple, a dict -- those never enter grid arithmetic)."""
        if isinstance(v, (SymArray, SymTuple, SymDict, SymIter, SymFunc,
                          SymLambda)):
            return None
        if v.gexpr is not None:
            return v.gexpr
        return Hole(v, self._why(v))

    def _binop(self, node: ast.BinOp) -> SymVal:
        lhs = self._eval(node.left)
        rhs = self._eval(node.right)
        opname = {ast.Add: "add", ast.Sub: "sub", ast.Mult: "mul",
                  ast.FloorDiv: "floordiv", ast.Div: "div", ast.Mod: "mod",
                  ast.Pow: "pow", ast.BitOr: "bitor", ast.BitAnd: "bitand",
                  ast.BitXor: "bitxor", ast.LShift: "lshift",
                  ast.RShift: "rshift"}.get(type(node.op))
        if opname is None:
            return _opaque(f"operator {type(node.op).__name__}")
        if lhs.concrete is not None and rhs.concrete is not None:
            import operator as _op
            fn = {"add": _op.add, "sub": _op.sub, "mul": _op.mul,
                  "div": _op.truediv, "floordiv": _op.floordiv,
                  "mod": _op.mod, "pow": _op.pow, "bitor": _op.or_,
                  "bitand": _op.and_, "bitxor": _op.xor,
                  "lshift": _op.lshift, "rshift": _op.rshift}[opname]
            return _lit(fn(lhs.concrete, rhs.concrete))
        # T033: elementwise array arithmetic is extent-preserving -- an
        # array combined with a scalar-shaped value (``rng.integers(...) /
        # 16``, ``x * 32``) keeps its per-axis extents (the VALUE is
        # untracked; only the shape survives, which is all the view ties
        # consume).  Two arrays with equal provenance per axis keep them
        # too (``q + np.transpose(q)`` is opaque-side; the equal-extent
        # form is the dtype-normalization idiom).
        if isinstance(lhs, SymArray) or isinstance(rhs, SymArray):
            if isinstance(lhs, SymArray) and not isinstance(rhs, SymArray) \
                    and _scalar_shaped(rhs):
                return SymArray(list(lhs.extents))
            if isinstance(rhs, SymArray) and not isinstance(lhs, SymArray) \
                    and _scalar_shaped(lhs):
                return SymArray(list(rhs.extents))
            if isinstance(lhs, SymArray) and isinstance(rhs, SymArray) \
                    and len(lhs.extents) == len(rhs.extents) \
                    and all(self._same_provenance(a, b)
                            for a, b in zip(lhs.extents, rhs.extents)):
                return SymArray(list(lhs.extents))
            return _opaque(f"{opname}({self._why(lhs)}, {self._why(rhs)})")
        # symbolic arithmetic over scalars: the tree keeps its shape, with
        # Holes at the operands the model cannot see (integer literals
        # already carry Lit leaves from _lit).  A holed subtree fills from
        # a scalar argument, a view extent or a meta constant the
        # interpreter proved equal; an unfilled hole refuses, located.
        # Only add/sub/mul/floordiv carry as runtime-computable grid
        # arithmetic; the other operators stay holes at the operand level
        # (the whole binop becomes one hole tied by the operand identity).
        ltree = self._scalar_gexpr_of(lhs)
        rtree = self._scalar_gexpr_of(rhs)
        if ltree is None or rtree is None:
            return _opaque(f"{opname}({self._why(lhs)}, {self._why(rhs)})")
        if opname not in ("add", "sub", "mul", "floordiv"):
            # mod/bitwise/shift/div/power over scalars: not runtime grid
            # arithmetic -- the result is an untracked scalar (a hole at
            # its consumers, fillable by an identity/structural tie)
            return _opaque(f"operator {opname}")
        if opname == "add":
            # T033: ``a // k + (1 if a % k else 0)`` is exactly
            # ``(a + k - 1) // k`` over the grid's non-negative domain
            # (element counts and block sizes -- the same identity the
            # np.ceil handler pins); the fused_bn_relu grid form
            for quot, ind in ((ltree, rtree), (rtree, ltree)):
                if isinstance(quot, Bin) and quot.op == "floordiv" \
                        and isinstance(ind, ModNonzero) \
                        and quot.left == ind.left and quot.right == ind.right:
                    return SymVal(gexpr=Bin(
                        "floordiv",
                        Bin("add", quot.left,
                            Bin("sub", quot.right, Lit(1))),
                        quot.right))
        return SymVal(gexpr=Bin(opname, ltree, rtree))

    # -- calls ----------------------------------------------------------------
    def _cdiv(self, node: ast.Call, args: List[SymVal]) -> SymVal:
        """triton.cdiv(a, b) = (a + b - 1) // b -- the exact pinned form
        (holed when an operand is untracked, so a tie can fill it)."""
        if len(args) != 2:
            raise self._err(node, "triton.cdiv", "cdiv takes two arguments")
        a, b = args
        if a.concrete is not None and b.concrete is not None:
            return _lit((a.concrete + b.concrete - 1) // b.concrete)
        atree = self._scalar_gexpr_of(a)
        btree = self._scalar_gexpr_of(b)
        if atree is None or btree is None:
            return _opaque(f"triton.cdiv({self._why(a)}, {self._why(b)})")
        return SymVal(gexpr=Bin(
            "floordiv",
            Bin("add", atree,
                Bin("sub", btree, Lit(1))),
            btree))

    def _next_power_of_2(self, node: ast.Call, args: List[SymVal]) -> SymVal:
        """triton.next_power_of_2 -- a PURE function: one argument value has
        exactly one result, so the call is memoized per argument identity.
        Two textual occurrences over the same value are then the same
        interpreted value, and a ``meta`` entry carrying one of them ties
        the other (the identity-tier constant the specialization signs)."""
        if len(args) != 1:
            return _opaque("triton.next_power_of_2")
        a = args[0]
        if a.concrete is not None and isinstance(a.concrete, int) \
                and not isinstance(a.concrete, bool):
            x = int(a.concrete)
            if x < 1:
                return _opaque("triton.next_power_of_2")
            p = 1
            while p < x:
                p <<= 1
            return _lit(p)
        key = ("triton.next_power_of_2", a)
        if key in self._pure_memo:
            return self._pure_memo[key]
        out = _opaque(f"triton.next_power_of_2({self._why(a)})")
        self._pure_memo[key] = out
        return out

    def _np_ctor(self, node: ast.Call, name: str,
                 args: List[SymVal]) -> SymVal:
        """np.zeros/empty/ones/full(...) -- extents from the shape argument."""
        shape_arg = None
        if name in ("zeros", "empty", "ones"):
            shape_arg = args[0] if args else None
        elif name == "full":
            shape_arg = args[0] if args else None
        elif name in ("zeros_like", "empty_like", "ones_like"):
            src = args[0] if args else None
            if isinstance(src, SymArray):
                return SymArray(list(src.extents))
            return _opaque(f"np.{name}")
        elif name in ("arange", "tile", "repeat"):
            return _opaque(f"np.{name}")
        if shape_arg is None:
            return _opaque(f"np.{name}")
        if isinstance(shape_arg, SymTuple):
            return SymArray(list(shape_arg.items))
        if shape_arg.concrete is not None:
            return SymArray([_lit(int(shape_arg.concrete))]
                            if not isinstance(shape_arg.concrete, (list, tuple))
                            else [_lit(int(v))
                                  for v in shape_arg.concrete])
        if shape_arg.tracked:
            return SymArray([shape_arg])
        return _opaque(f"np.{name}")

    def _rng_method(self, node: ast.Call, method: str,
                    args: List[SymVal]) -> SymVal:
        """rng.<draw>(..., size): the trailing size argument is the extent
        (an int or a per-axis tuple)."""
        size = args[-1] if args else None
        if isinstance(size, SymTuple):
            return SymArray(list(size.items))
        if size is not None and size.concrete is not None \
                and isinstance(size.concrete, int):
            return SymArray([_lit(size.concrete)])
        if size is not None and size.tracked:
            return SymArray([size])
        return _opaque(f"rng.{method}")

    def _method_call(self, node: ast.Call, base: SymVal,
                     args: List[SymVal]) -> SymVal:
        method = node.func.attr
        if isinstance(base, SymDict) and method in ("items", "keys", "values"):
            return SymIter(base, method)
        if isinstance(base, SymArray):
            if method == "astype":
                return SymArray(list(base.extents))     # extents preserved
            if method == "reshape":
                if args and isinstance(args[0], SymTuple):
                    return SymArray(list(args[0].items))
                if args and len(args) == 1 \
                        and isinstance(args[0], SymVal) \
                        and args[0].concrete == -1:
                    # T033: ``x.reshape(-1)`` flattens in row-major order:
                    # the extent is the PRODUCT of the base's per-axis
                    # extents (the tracked tree numpy itself computes).
                    # The old form treated the literal -1 as a tracked
                    # extent -- a wrong model only the self-check ever
                    # caught.
                    return SymArray([self._product(list(base.extents),
                                                   node)])
                if args and args[0].tracked:
                    return SymArray([args[0]])
                return _opaque("reshape")
            if method == "sum" and not args:
                # the VALUE sum of an array's contents -- value-dependent,
                # never the extent product (``lens.sum()`` is not
                # ``lens.size``); untracked, fillable only by a tie
                return _opaque("array .sum()")
            if method in _RNG_SIZE_METHODS:
                return self._rng_method(node, method, args)
            return _opaque(f".{method}")
        if base.opaque is not None and "module" in str(base.opaque):
            return _opaque(f".{method}")
        if base.opaque is not None and method in _RNG_SIZE_METHODS:
            return self._rng_method(node, method, args)
        return _opaque(f".{method}")

    def _minmax(self, name: str, args: List[SymVal]) -> SymVal:
        """min/max over scalar operands, any arity (the corpus's
        ``min(n, ci, d, h, w, co, kd, kh, kw)`` guard chains): folds when
        every operand is concrete; otherwise a left-associated MinMax
        chain (the native routine realizes each node with the declared
        compare/mask/select sequence) with holes at the operands the model
        cannot see."""
        if all(a.concrete is not None for a in args):
            fn = min if name == "min" else max
            try:
                return _lit(fn(a.concrete for a in args))
            except TypeError:
                return _opaque(f"{name}(...)")
        chain = None
        for a in args:
            tree = self._scalar_gexpr_of(a)
            if tree is None:
                return _opaque(f"{name}({self._why(a)})")
            chain = tree if chain is None else MinMax(name, chain, tree)
        return SymVal(gexpr=chain)

    # -- module-level helper calls ---------------------------------------------
    def _call_function(self, node: ast.Call, fn: ast.FunctionDef) -> SymVal:
        """Interpret one call to a module-level helper function of the
        operator file in the provenance domain, under the step budget and
        depth bound.  Any failure degrades to an opaque value (the grid
        consuming it refuses, located) -- never a guess, never a hang."""
        if self._depth >= _HELPER_DEPTH:
            return _opaque(f"call {fn.name} (depth)")
        for a in node.args:
            if isinstance(a, ast.Starred):
                self._eval(a.value)
                return _opaque(f"call {fn.name} (star-args)")
        for k in node.keywords:
            if k.arg is None:
                self._eval(k.value)
                return _opaque(f"call {fn.name} (**kwargs)")
        pos_args = [self._eval(a) for a in node.args if isinstance(a, ast.expr)]
        kw_args = {k.arg: self._eval(k.value) for k in node.keywords}

        # bind parameters: positional, then keyword, then defaults
        # (defaults are evaluated in the caller's environment, i.e. the
        # module scope the file wrote them in)
        params = [a.arg for a in fn.args.args]
        defaults = fn.args.defaults
        kwonly = {a.arg for a in fn.args.kwonlyargs}
        if len(pos_args) > len(params) or kwonly - set(kw_args):
            return _opaque(f"call {fn.name} (arity)")
        bound: Dict[str, SymVal] = {}
        for pname, v in zip(params, pos_args):
            bound[pname] = v
        n_default = len(defaults)
        first_default = len(params) - n_default
        for i, pname in enumerate(params):
            if pname in bound:
                continue
            if pname in kw_args:
                bound[pname] = kw_args.pop(pname)
                continue
            if i >= first_default:
                bound[pname] = self._eval(defaults[i - first_default])
                continue
            return _opaque(f"call {fn.name} (unbound {pname})")

        saved_env = self.env
        saved_retval = self.retval
        entry_steps = self._steps
        self._depth += 1
        self.env = dict(bound)
        result: Optional[SymVal] = None
        try:
            for stmt in fn.body:
                if isinstance(stmt, ast.Return):
                    if stmt.value is not None:
                        result = self._eval(stmt.value)
                    break
                self._stmt(stmt)
                if self._steps - entry_steps > _HELPER_STEP_BUDGET:
                    raise _HelperBudget()
            if result is None:
                result = _opaque(f"call {fn.name} (no return)")
        except _HelperBudget:
            result = _opaque(f"call {fn.name} (budget)")
        except GridError as exc:
            result = _opaque(f"call {fn.name} ({exc.construct})")
        except RecursionError:
            result = _opaque(f"call {fn.name} (recursion)")
        except Exception as exc:            # interpretation beyond the model
            result = _opaque(f"call {fn.name} ({type(exc).__name__})")
        finally:
            self.env = saved_env
            self.retval = saved_retval
            self._depth -= 1
        assert result is not None
        return result

    def _call(self, node: ast.Call) -> SymVal:
        func = node.func
        name = func.id if isinstance(func, ast.Name) else None
        dotted = None
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            dotted = f"{func.value.id}.{func.attr}"
        # triton.cdiv -- the pinned ceiling division
        if dotted == "triton.cdiv":
            return self._cdiv(node, [self._eval(a) for a in node.args])
        # triton.next_power_of_2 -- pure, memoized per argument identity
        if dotted in _PURE_CALLS:
            return getattr(self, "_" + dotted.split(".", 1)[1])(
                node, [self._eval(a) for a in node.args])
        # np.<ctor> with a shape argument
        if dotted and dotted.split(".", 1)[0] in ("np", "numpy"):
            tail = dotted.split(".", 1)[1]
            if tail == "prod":
                args = [self._eval(a) for a in node.args]
                if args and isinstance(args[0], SymTuple):
                    return self._product(args[0].items, node)
                if args and isinstance(args[0], SymArray):
                    return self._product(args[0].extents, node)
                return _opaque("np.prod")
            if tail in _NP_CTORS:
                return self._np_ctor(node, tail,
                                     [self._eval(a) for a in node.args])
            if tail in ("asarray", "array") and node.args:
                # T033: np.asarray / np.array over a tracked array or a
                # scalar-shaped value preserves the extents/provenance (a
                # copy never reshapes; the dtype argument never changes an
                # extent) -- cholesky's STATUS passes through it into the
                # args literal.  Anything else stays opaque.
                arg = self._eval(node.args[0])
                if isinstance(arg, SymArray):
                    return arg
                if not isinstance(arg, (SymTuple, SymDict, SymIter,
                                        SymFunc, SymLambda)) \
                        and not isinstance(arg, SymArray):
                    return arg        # a scalar-shaped value passes
                return _opaque(f"np.{tail}")
            if tail in _NP_ELEMENTWISE and node.args:
                # T033: an elementwise np function over one tracked array
                # with scalar-shaped remaining arguments keeps the array's
                # extents (the VALUE is untracked; the shape is structural
                # and case-independent, so a tie built on it is invariant
                # across an identity's cases)
                first = self._eval(node.args[0])
                rest = [self._eval(a) for a in node.args[1:]]
                for k in node.keywords:
                    self._eval(k.value)
                if isinstance(first, SymArray) \
                        and all(_scalar_shaped(r) for r in rest):
                    return SymArray(list(first.extents))
                return _opaque(f"np.{tail}")
            if tail in _NP_SCALAR_CASTS and len(node.args) == 1:
                # a scalar dtype cast preserves the value and its
                # provenance (the cast never changes what the argument
                # equals -- the tie the grid model needs survives it)
                return self._eval(node.args[0])
            if tail == "ceil" and len(node.args) == 1:
                arg = node.args[0]
                if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Div):
                    a = self._eval(arg.left)
                    b = self._eval(arg.right)
                    if a.gexpr is not None and b.gexpr is not None:
                        # ceil(a / b) over the NON-NEGATIVE quantities the
                        # grid domain carries (extents, element counts) is
                        # exactly (a + b - 1) // b -- the cdiv form.  The
                        # negation form -((-a)//b) is wrong here: the
                        # lowering realizes floordiv as UNSIGNED division
                        # (positive-domain convention), and its negative
                        # intermediate (-a) wraps (the tanh SIGILL-class
                        # zero-program launch)
                        return SymVal(gexpr=Bin(
                            "floordiv",
                            Bin("add", a.gexpr,
                                Bin("sub", b.gexpr, Lit(1))),
                            b.gexpr))
                return _opaque("np.ceil")
            return _opaque(dotted)
        if dotted == "math.prod":
            args = [self._eval(a) for a in node.args]
            if args and isinstance(args[0], SymTuple):
                return self._product(args[0].items, node)
            return _opaque("math.prod")
        # method call on a tracked or opaque value (chains included:
        # rng.integers(...).astype(...) evaluates the inner call first)
        if isinstance(func, ast.Attribute):
            base = self._eval(func.value)
            if isinstance(base, (SymArray, SymDict)) \
                    or base.opaque is not None:
                args = [self._eval(a) for a in node.args]
                for k in node.keywords:
                    self._eval(k.value)
                return self._method_call(node, base, args)
        if name == "isinstance" and len(node.args) == 2:
            # decidable in the domain for the corpus's guard idiom
            # (``isinstance(value, np.ndarray)`` -- 227 occurrences): an
            # array-shaped value IS one, a scalar-shaped value is NOT,
            # anything the model cannot see stays unknown
            target = self._eval(node.args[0])
            cls = node.args[1]
            is_ndarray = isinstance(cls, ast.Attribute) \
                and isinstance(cls.value, ast.Name) \
                and cls.value.id in ("np", "numpy") \
                and cls.attr == "ndarray"
            if is_ndarray:
                if isinstance(target, SymArray):
                    return _lit(True)
                if target.concrete is not None:
                    return _lit(hasattr(target.concrete, "shape"))
                if isinstance(target, (SymTuple, SymDict, SymIter, SymFunc,
                                       SymLambda)):
                    return _lit(False)
                if target.opaque is None:
                    # a scalar-shaped value (a tracked leaf): not an array
                    return _lit(False)
            return _opaque("isinstance")
        if name == "hasattr" and len(node.args) == 2:
            # hasattr(value, 'size') guards: an array-shaped value has one
            self._eval(node.args[0])
            self._eval(node.args[1])
            return _opaque("hasattr")
        if name in _TRACE_BUILTINS:
            args = [self._eval(a) for a in node.args]
            if name in ("min", "max") and len(args) >= 2:
                return self._minmax(name, args)
            if any(a.concrete is None for a in args):
                # int()/tuple()/dict() wrapping a symbolic value: the value
                # passes through unchanged (its tracked-ness is what
                # matters; an untracked value flowing into the grid
                # expression makes the extraction refuse later --
                # conservative, never a guess)
                if name in ("int", "tuple", "dict", "float", "bool") \
                        and len(args) == 1:
                    return args[0]
                if name == "len" and len(args) == 1:
                    if isinstance(args[0], SymTuple):
                        return _lit(len(args[0].items))
                    if isinstance(args[0], SymArray):
                        return args[0].extents[0]
                return _opaque(f"{name}() on a symbolic value")
            vals = [a.concrete for a in args]
            if name == "int":
                return _lit(int(*vals))
            if name == "tuple":
                return SymTuple([_lit(v) for v in vals[0]])
            if name == "dict":
                if len(vals) == 1 and isinstance(vals[0], dict):
                    return SymDict({k: _lit(v) for k, v in vals[0].items()})
                return _opaque("dict()")
            if name == "str":
                return _opaque("str()")
            if name == "len":
                if isinstance(args[0], SymTuple):
                    return _lit(len(args[0].items))
                return _lit(len(vals[0]))
            if name in ("abs", "round", "float", "bool"):
                return _lit({  # type: ignore[misc]
                    "abs": abs, "round": round,
                    "float": float, "bool": bool}[name](*vals))
        if name == "map":
            # map(int, shape): the per-item passthrough of a tracked tuple
            if len(node.args) == 2 and isinstance(node.args[0], ast.Name) \
                    and node.args[0].id in ("int", "str", "float", "bool"):
                seq = self._eval(node.args[1])
                if isinstance(seq, SymTuple):
                    return SymTuple([
                        self._int_passthrough(item, node.args[0].id)
                        for item in seq.items])
            return _opaque("map")
        if name == "sum" and len(node.args) == 1 and not node.keywords:
            # T034: builtin sum over an enumerable sequence or generator
            # (the tile-count idiom ``sum(ceil_div(m, BM) * ceil_div(n, BN)
            # for (m, n, k) in dimensions)`` -- grouped_gemm).  Concrete
            # items fold; symbolic items add-chain their grid expressions
            # (the native routine realizes each Bin node); any item the
            # model cannot see stays opaque (the axis check refuses).
            arg = node.args[0]
            items: Optional[List[SymVal]] = None
            if isinstance(arg, ast.GeneratorExp) \
                    and len(arg.generators) == 1 \
                    and not arg.generators[0].ifs \
                    and not arg.generators[0].is_async:
                enum = self._iter_items(arg.generators[0].iter)
                if enum is not None:
                    target = arg.generators[0].target
                    items = []
                    for item in enum:
                        self._bind_loop_target(target, item)
                        try:
                            items.append(self._eval(arg.elt))
                        finally:
                            self._restore_loop_target(target)
            else:
                v = self._eval(arg)
                if isinstance(v, SymTuple):
                    items = list(v.items)
            if items is not None and len(items) <= _LOOP_ITERATION_CAP:
                acc = None
                concrete = 0
                symbolic = False
                for it in items:
                    if it.concrete is not None \
                            and isinstance(it.concrete, int) \
                            and not isinstance(it.concrete, bool):
                        concrete += int(it.concrete)
                        continue
                    tree = self._scalar_gexpr_of(it)
                    if tree is None:
                        return _opaque(f"sum({self._why(it)})")
                    acc = tree if acc is None else Bin("add", acc, tree)
                    symbolic = True
                if not symbolic:
                    return _lit(concrete)
                return SymVal(gexpr=Bin("add", acc, Lit(concrete))
                              if concrete else acc)
            return _opaque("sum")
        # a module-level helper function of the operator file (``_case``,
        # ``_aligned``, ``_dims``, ...): interpreted in the same provenance
        # domain under the step budget -- the payload dict it returns and
        # the arrays it builds carry their tracked extents onward
        if name is not None:
            local = self.env.get(name)
            fn_node = local.node if isinstance(local, SymFunc) else \
                (self.module_functions.get(name)
                 if local is None and name in self.module_functions else None)
            if fn_node is not None:
                return self._call_function(node, fn_node)
        # any other call (fast_rng, _aligned, np.*, _case): untracked
        for a in node.args:
            if isinstance(a, ast.expr):
                self._eval(a)
        for k in node.keywords:
            self._eval(k.value)
        callee = name or dotted or (ast.unparse(node.func)
                                    if hasattr(ast, "unparse") else "call")
        return _opaque(f"call {callee}")

    def _subscript(self, node: ast.Subscript) -> SymVal:
        base = self._eval(node.value)
        index = self._eval(node.slice) if not isinstance(node.slice, ast.Slice) \
            else None
        if isinstance(base, SymTuple):
            if isinstance(index, SymTuple):
                # a multi-dimensional index over a tuple-shaped value: an
                # element access, never an extent (x[1, -1] on a shape-
                # carrying value -- untracked, never int() over a tuple)
                return _opaque("multi-index element access")
            if index is None or index.concrete is None:
                return _opaque("symbolic tuple index")
            if not isinstance(index.concrete, int) \
                    or isinstance(index.concrete, bool):
                return _opaque("non-integer tuple index")
            if not (0 <= index.concrete < len(base.items)):
                raise self._err(node, "subscript", "tuple index out of range")
            return base.items[index.concrete]
        if isinstance(base, SymDict):
            if index is None or index.concrete is None:
                return _opaque("symbolic dict key")
            if index.concrete not in base.mapping:
                return _opaque(f"key {index.concrete!r} not tracked")
            return base.mapping[index.concrete]
        if isinstance(base, SymArray):
            if isinstance(index, SymTuple):
                # a multi-dimensional element access (x[1, -1] in the
                # case layer): the ELEMENT is not a bundle-visible
                # quantity -- untracked (a grid axis consuming it refuses,
                # located, at the tie stage; never int() over a tuple,
                # the T024 interpreter gap)
                return _opaque("multi-index element access")
            if index is None or index.concrete is None \
                    or not isinstance(index.concrete, int) \
                    or isinstance(index.concrete, bool):
                return _opaque("array element access")
            if 0 <= int(index.concrete) < len(base.extents):
                return base.extents[int(index.concrete)]
            # an element read beyond the tracked extents (x[4] of an
            # (R, L) array): an element access, never an extent -- the
            # value is untracked (a grid axis consuming it refuses,
            # located, at the tie stage)
            return _opaque("array element access")
        return _opaque("subscript")


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------


@dataclass
class GridModel:
    """The extracted grid form (one axis expression per grid axis) + the
    bundle-visible ties of every symbolic leaf."""

    #: per-axis grid expressions (axis 0 varies fastest in the linear
    #: worker-range index; the decomposition strides are products of the
    #: preceding extents)
    axes: Tuple[GridExpr, ...]
    #: leaf origin Ref -> ('scalar', argument_name)
    #:                   | ('view_extent', view_name, axis)
    ties: Dict[Tuple, Tuple[str, object]] = field(default_factory=dict)
    ndim: int = 1
    path: str = ""
    #: the self-check record (compile-time equality with the case's grid)
    self_check: Dict[str, object] = field(default_factory=dict)

    @property
    def expr(self) -> GridExpr:
        """The 1-D axis expression (the only form of the vertical slice)."""
        return self.axes[0]

    def strides(self) -> Tuple[int, ...]:
        """Compile-time strides are NOT assumed: extents are runtime.  This
        returns the stride *structure* (axis k stride = product of the
        extents of axes 0..k-1), realized at run time by the decomposition."""
        return tuple(1 if k == 0 else 0 for k in range(self.ndim))

    def describe(self) -> dict:
        return {"ndim": self.ndim,
                "axes": [repr(a) for a in self.axes],
                "ties": {f"{k}": list(v) for k, v in self.ties.items()},
                "self_check": dict(self.self_check)}


def _module_constants(source: OperatorSource) -> Dict[str, object]:
    """Module-level literal assignments (read-only re-parse of the source)."""
    text = _read_source(source)
    out: Dict[str, object] = {}
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return out
    for node in tree.body:
        value = None
        name = None
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)):
            name, value = node.targets[0].id, node.value
        elif (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], (ast.Tuple, ast.List))
                and isinstance(node.value, (ast.Tuple, ast.List))
                and len(node.targets[0].elts) == len(node.value.elts)):
            # tuple-unpacked module constants (BLOCK_M, BLOCK_N = 32, 128
            # -- the corpus's block-size idiom)
            for t, v in zip(node.targets[0].elts, node.value.elts):
                if isinstance(t, ast.Name):
                    try:
                        out[t.id] = ast.literal_eval(v)
                    except (ValueError, SyntaxError):
                        continue
            continue
        elif (isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name)
                and node.value is not None):
            # annotated module constants (BLOCK_N: int = 128)
            name, value = node.target.id, node.value
        if name is not None:
            try:
                out[name] = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                continue
    return out


def _module_functions(tree: ast.Module,
                      kernel_name: str) -> Dict[str, ast.FunctionDef]:
    """Module-level plain ``def`` functions of the operator file, excluding
    the jit kernel (the compile unit -- FE-SOURCE-CONTRACT) and every
    decorated definition (the corpus's case-layer helpers carry no
    decorators).  These are the helper functions the case layer may call
    (``_case``, ``_aligned``, ``_dims``, ``ref``, ...) -- interpreted in
    the provenance domain under the budget."""
    out: Dict[str, ast.FunctionDef] = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.decorator_list \
                and node.name != kernel_name:
            out[node.name] = node
    return out


def _read_source(source: OperatorSource) -> str:
    with open(source.path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _find_make_case(tree: ast.Module) -> Optional[ast.FunctionDef]:
    """The case-layer builder: ``_make_case`` (the declared form), or the
    FIRST ``make_case`` definition when the operator builds its case
    directly (the pre-schema form some corpus operators use -- the later
    enriched re-definition delegates to it)."""
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "_make_case":
            return node
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "make_case":
            return node
    return None


def _declared_grid(case: dict, source: OperatorSource = None) -> Optional[Tuple[int, ...]]:
    """The case's concrete declared grid (a tuple, or a lambda evaluated
    with the meta the launcher would pass -- the trusted case layer,
    host-side)."""
    declared = case.get("grid")
    if declared is None:
        return None
    if callable(declared):
        meta = dict(case.get("meta") or {})
        if source is not None and source.is_autotune \
                and source.autotune_configs:
            meta.update(source.autotune_configs[0].constexprs or {})
        try:
            declared = declared(meta)
        except Exception:
            return None
    try:
        return tuple(int(v) for v in declared)
    except (TypeError, ValueError):
        return None


def _array_args(case: dict) -> Dict[str, tuple]:
    """The case's ndarray arguments: name -> concrete shape."""
    import numpy as np
    out: Dict[str, tuple] = {}
    for name, value in (case.get("args") or {}).items():
        if isinstance(value, np.ndarray):
            out[name] = tuple(int(e) for e in value.shape)
    return out


def _grid_leafs(expr) -> Iterable[Ref]:
    if isinstance(expr, Ref):
        yield expr
    elif isinstance(expr, Bin):
        yield from _grid_leafs(expr.left)
        yield from _grid_leafs(expr.right)
    elif isinstance(expr, MinMax):
        yield from _grid_leafs(expr.left)
        yield from _grid_leafs(expr.right)


def _grid_holes(expr) -> Iterable["Hole"]:
    """Every unfilled hole in a grid expression tree (deduplicated)."""
    seen = set()
    for hole in _iter_holes(expr):
        if id(hole) not in seen:
            seen.add(id(hole))
            yield hole


def _iter_holes(expr) -> Iterable["Hole"]:
    if isinstance(expr, Hole):
        yield expr
    elif isinstance(expr, Bin):
        yield from _iter_holes(expr.left)
        yield from _iter_holes(expr.right)
    elif isinstance(expr, MinMax):
        yield from _iter_holes(expr.left)
        yield from _iter_holes(expr.right)


def _iter_modnonzero(expr) -> Iterable["ModNonzero"]:
    """Every surviving mod-nonzero indicator in a grid expression tree
    (T033): one that never combined with its ``a // k`` into the cdiv form
    is not a runtime grid op and refuses, located."""
    if isinstance(expr, ModNonzero):
        yield expr
    elif isinstance(expr, Bin):
        yield from _iter_modnonzero(expr.left)
        yield from _iter_modnonzero(expr.right)
    elif isinstance(expr, MinMax):
        yield from _iter_modnonzero(expr.left)
        yield from _iter_modnonzero(expr.right)


def _shape_arity(source: OperatorSource, case: dict) -> Tuple[Tuple, Tuple]:
    """The case's shape as (payload-shape, interpreted-shape).

    Schema-3 payloads echo ``shape``; older payloads do not, and the arity
    comes from the operator's own SHAPES table when every entry of it
    agrees (the runner passes shapes of that arity).  A SHAPES table with
    MIXED arities and no payload echo leaves the arity UNKNOWN (None): the
    ``shape`` parameter binds to an untracked value -- ``len(shape)`` and
    unpacking refuse conservatively instead of guessing an arity whose
    IfExp branch produces a wrong model (the fht/cholesky self-check
    class).  Returns (concrete-shape-tuple, arity-or-None)."""
    shape = case.get("shape") or ()
    if len(shape):
        return tuple(int(v) for v in shape), len(shape)
    shapes_table = source.case_literals.get("SHAPES") or ()
    if shapes_table:
        try:
            arities = {len(s) for s in shapes_table}
        except TypeError:
            arities = set()
        if len(arities) == 1:
            return (), arities.pop()
        if len(arities) > 1:
            return (), None          # mixed arities: unknown, never guessed
        try:
            first = shapes_table[0]
            return (), len(first)
        except (TypeError, IndexError):
            pass
    return (), 0


def _interp_once(source: OperatorSource, case: dict,
                 view_bindings: Dict[str, SymArray],
                 module_constants: Dict[str, object],
                 module_functions: Dict[str, ast.FunctionDef],
                 make_case: ast.FunctionDef) -> Tuple[_Interpreter, Dict[str, SymVal]]:
    shape, ndim = _shape_arity(source, case)
    # The shape axes stay SYMBOLIC in the expression (their concrete values
    # are self-check inputs only): folding a case's shape into the grid
    # would bake a runtime launch geometry.  Only the ARITY is used during
    # interpretation (len(shape)/unpacking), which the corpus's own SHAPES
    # tables hold fixed per operator.
    params: Dict[str, SymVal] = {
        "shape": SymTuple([
            SymVal(origin=Ref("shape_extent", (i,)),
                   gexpr=Ref("shape_extent", (i,)))
            for i in range(ndim)])
        if ndim is not None else
        _opaque("shape (unknown arity: mixed SHAPES, no payload echo)"),
        "dtype": SymVal(origin=Ref("case_param", ("dtype",))),
        "seed": SymVal(origin=Ref("case_param", ("seed",))),
    }
    dtype_payload = case.get("dtype")
    if isinstance(dtype_payload, str) and dtype_payload:
        params["dtype"] = SymVal(origin=Ref("case_param", ("dtype",)),
                                 concrete=dtype_payload.rsplit(".", 1)[-1])
    seed_payload = case.get("seed")
    if isinstance(seed_payload, int) and not isinstance(seed_payload, bool):
        params["seed"] = SymVal(origin=Ref("case_param", ("seed",)),
                                concrete=seed_payload)
    interp = _Interpreter(source, module_constants, module_functions)
    try:
        env = interp.run(make_case, params,
                         prelude=view_bindings or None)
    except GridError:
        raise
    except Exception as exc:  # interpretation beyond the model: refuse
        raise GridError(source.path, make_case.lineno, make_case.col_offset + 1,
                        "_make_case",
                        f"case-layer interpretation failed: {exc}") from None
    return interp, env


def extract_grid(source: OperatorSource, case: dict) -> GridModel:
    """Extract the grid form (every axis) from the case layer, with
    provenance.

    Refuses (GridError, located) when: the case layer has no grid
    assignment, a grid axis is not provenance-tracked, a grid input cannot
    be tied to a bundle-visible quantity, or the compile-time self-check
    disagrees with the case's declared grid.
    """
    if source.kernel_ast is None:  # pragma: no cover - loader guarantees it
        raise GridError(source.path, 1, 0, "case layer", "kernel AST missing")
    text = _read_source(source)
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:  # pragma: no cover - loader parsed it already
        raise GridError(source.path, exc.lineno or 1, exc.offset or 1,
                        "case layer", f"syntax error: {exc.msg}") from None
    make_case = _find_make_case(tree)
    if make_case is None:
        raise GridError(source.path, 1, 0, "_make_case",
                        "the case layer has no _make_case function; the grid "
                        "form cannot be extracted (FE-SOURCE-CONTRACT)")
    module_constants = _module_constants(source)
    module_functions = _module_functions(tree, source.kernel_name)
    arrays = _array_args(case)
    args_payload = case.get("args") or {}
    import numbers as _numbers

    def _integral(value) -> bool:
        return not isinstance(value, bool) \
            and isinstance(value, _numbers.Integral)

    # which case arguments the bundle can actually serve at run time: the
    # kernel's own non-constexpr parameters (extra case arguments and
    # oracle_args are identity-signed but never bound -- tying them would
    # move the read to a quantity the emitted program cannot reach)
    oracle_args = set((case.get("oracle_args") or {}).keys())
    kernel_params = {p.name for p in source.params if not p.is_constexpr}
    pointer_params = {n for n in kernel_params if n in arrays}
    scalar_params = {n for n in kernel_params
                     if n not in arrays and n not in oracle_args
                     and _integral(args_payload.get(n))}

    # -- pass 1: find which locals flow into the array args -------------------
    interp, env = _interp_once(source, case, {}, module_constants,
                               module_functions, make_case)
    args_value = env.get("args")
    if not isinstance(args_value, SymDict) and isinstance(interp.returned,
                                                          SymDict):
        args_value = interp.returned.mapping.get("args")
        if not isinstance(args_value, SymDict) and args_value is not None:
            args_value = None
    array_locals: Dict[str, List[str]] = {}
    if isinstance(args_value, SymDict):
        for argname, value in args_value.mapping.items():
            if argname not in arrays or isinstance(value, SymArray):
                continue
            # an opaque value flowing into an array arg: the local(s)
            # holding that same object are rebound to the concrete view
            holders = [n for n, v in env.items() if v is value]
            if holders:
                array_locals.setdefault(argname, []).extend(holders)

    # -- pass 2: rebind those locals to symbolic views --------------------------
    view_bindings: Dict[str, SymArray] = {}
    if array_locals:
        interp, env = _interp_once(source, case, {}, module_constants,
                                   module_functions, make_case)
        for argname in sorted(array_locals):
            shape = arrays[argname]
            # the view extents stay symbolic in the expression (the
            # concrete shapes are self-check inputs only -- never baked)
            sym = SymArray([
                SymVal(origin=Ref("view_extent", (argname, k)),
                       gexpr=Ref("view_extent", (argname, k)))
                for k in range(len(shape))], view=argname)
            for local in array_locals[argname]:
                if local in view_bindings:
                    raise GridError(
                        source.path, make_case.lineno,
                        make_case.col_offset + 1, "grid",
                        f"local '{local}' flows into two array arguments "
                        f"('{view_bindings[local].view}' and '{argname}'); "
                        "the view tie is ambiguous (refused, not guessed)")
                view_bindings[local] = sym
        if view_bindings:
            interp, env = _interp_once(source, case, view_bindings,
                                       module_constants, module_functions,
                                       make_case)

    # -- the grid value: the RETURNED payload is authoritative (the local
    # ``grid`` name is a fallback -- a dead local must never shadow the
    # payload's own grid, the quant_transpose/matmul_triton2 class)
    grid_value = None
    if isinstance(interp.returned, SymDict) \
            and interp.returned.mapping.get("grid") is not None:
        grid_value = interp.returned.mapping.get("grid")
    if grid_value is None:
        grid_value = env.get("grid")
    if isinstance(grid_value, SymLambda):
        grid_value = _run_grid_lambda(source, grid_value, case, make_case)
    if grid_value is None or not isinstance(grid_value, SymTuple):
        raise GridError(source.path, make_case.lineno, make_case.col_offset + 1,
                        "grid",
                        "the case layer never assigns a trackable 'grid' "
                        "(the grid form cannot be extracted)")

    # -- the tie registries: what the interpreter proved equal to what --------
    args_sym = env.get("args")
    if not isinstance(args_sym, SymDict) and isinstance(interp.returned,
                                                        SymDict):
        candidate = interp.returned.mapping.get("args")
        if isinstance(candidate, SymDict):
            args_sym = candidate

    #: bundle scalar reads: the interpreter's own equality between a grid
    #: subtree and a scalar kernel argument (the same SymVal, or a
    #: structurally equal grid expression -- "tie scalars the case passes
    #: as grid inputs")
    scalar_by_id: Dict[int, str] = {}
    scalar_by_gexpr: Dict[object, str] = {}
    #: view-extent reads: a grid subtree equal to a view axis's extent
    view_by_id: Dict[int, Tuple[str, int]] = {}
    view_by_gexpr: Dict[object, Tuple[str, int]] = {}
    #: identity-tier constants: meta/launch_meta entries the specialization
    #: identity signs (folded exactly like the lambda-meta form)
    meta_by_id: Dict[int, int] = {}
    meta_by_gexpr: Dict[object, int] = {}
    meta_names: Dict[int, str] = {}

    if isinstance(args_sym, SymDict):
        for argname in sorted(args_sym.mapping):
            value = args_sym.mapping.get(argname)
            if value is None:
                continue
            if argname in pointer_params and isinstance(value, SymArray):
                shape = arrays.get(argname) or ()
                for axis, extent in enumerate(value.extents):
                    if axis >= len(shape):
                        break
                    view_by_id.setdefault(id(extent), (argname, axis))
                    if extent.gexpr is not None:
                        view_by_gexpr.setdefault(extent.gexpr,
                                                 (argname, axis))
            elif argname in scalar_params:
                scalar_by_id.setdefault(id(value), argname)
                if value.gexpr is not None:
                    scalar_by_gexpr.setdefault(value.gexpr, argname)

    if isinstance(interp.returned, SymDict):
        for table in ("meta", "launch_meta"):
            sym_table = interp.returned.mapping.get(table)
            payload_table = case.get(table) or {}
            if not isinstance(sym_table, SymDict) \
                    or not isinstance(payload_table, dict):
                continue
            for mname in sorted(sym_table.mapping):
                mvalue = payload_table.get(mname)
                if not _integral(mvalue):
                    continue
                sv = sym_table.mapping[mname]
                if sv is None:
                    continue
                if id(sv) not in meta_by_id:
                    meta_by_id[id(sv)] = int(mvalue)
                    meta_names[id(sv)] = f"{table}.{mname}"
                if sv.gexpr is not None:
                    meta_by_gexpr.setdefault(sv.gexpr, int(mvalue))

    # -- the leaf-tie tables (runtime reads for bare shape leaves) ------------
    scalar_ties: Dict[Tuple, str] = {}
    view_ties: Dict[Tuple, Tuple[str, int]] = {}
    if isinstance(args_sym, SymDict):
        for argname, value in args_sym.mapping.items():
            if argname in pointer_params and isinstance(value, SymArray):
                for axis, extent in enumerate(value.extents):
                    # a view extent whose tracked expression IS one leaf
                    # (by structural equality -- origin or a single-axis
                    # product): reading the view axis at run time yields
                    # exactly that leaf's value
                    if isinstance(extent.gexpr, Ref):
                        view_ties.setdefault(extent.gexpr.key,
                                             (argname, axis))
                    elif extent.origin is not None and \
                            extent.origin.kind == "shape_extent":
                        view_ties.setdefault(extent.origin.key,
                                             (argname, axis))
            elif argname in scalar_params and value is not None \
                    and value.origin is not None \
                    and value.origin.kind == "shape_extent":
                # a scalar argument whose value shares the origin (args =
                # {"n": shape[0]}): the grid leaf reads it at run time
                scalar_ties.setdefault(value.origin.key, argname)
    ties: Dict[Tuple, Tuple[str, object]] = {}

    # value-based fallback tie: when the payload echoes the case shape, a
    # view axis whose concrete extent equals a shape axis ties that shape
    # leaf (the self-check validates the model against the declared grid
    # for every compiling case -- a wrong tie refuses loudly, and the
    # runtime always reads the view's actual extent)
    payload_shape = case.get("shape") or ()
    value_view_ties: Dict[Tuple, Tuple[str, int]] = {}
    if len(payload_shape):
        for view, shape in sorted(arrays.items()):
            if view not in pointer_params:
                continue
            for axis, extent in enumerate(shape):
                for i, want in enumerate(payload_shape):
                    if int(extent) == int(want):
                        value_view_ties.setdefault((i,), (view, axis))
                        break

    def _leaf_tied(expr: Ref) -> bool:
        """A shape leaf with a runtime leaf tie keeps its Ref (the tie
        stage binds it); the identity-tier constant is the fallback."""
        return expr.kind == "shape_extent" and (
            expr.key in scalar_ties or expr.key in view_ties
            or expr.key in value_view_ties)

    # -- rewrite each axis: fill what is provably equal to a bundle read or
    # an identity-tier constant; keep everything else for the tie/refusal
    # stage (top-down: the largest provable subtree becomes one read)
    def _rewrite(expr):
        if isinstance(expr, Hole):
            owner = id(expr.owner)
            if owner in scalar_by_id:
                return Ref("bundle_scalar", (scalar_by_id[owner],))
            if owner in view_by_id:
                return Ref("bundle_view", view_by_id[owner])
            if owner in meta_by_id:
                return Lit(meta_by_id[owner])
            return expr
        if isinstance(expr, (Bin, MinMax)):
            if expr in scalar_by_gexpr:
                return Ref("bundle_scalar", (scalar_by_gexpr[expr],))
            if expr in view_by_gexpr:
                return Ref("bundle_view", view_by_gexpr[expr])
            if expr in meta_by_gexpr:
                return Lit(meta_by_gexpr[expr])
            left = _rewrite(expr.left)
            right = _rewrite(expr.right)
            if isinstance(expr, Bin):
                return Bin(expr.op, left, right)
            return MinMax(expr.op, left, right)
        if isinstance(expr, Ref):
            # a bare leaf: prefer a runtime read (a tied scalar argument,
            # a tied view extent), then the identity-tier constant
            # (``meta = {"N": n}`` signs n for this identity)
            if expr in scalar_by_gexpr:
                return Ref("bundle_scalar", (scalar_by_gexpr[expr],))
            if expr in view_by_gexpr:
                return Ref("bundle_view", view_by_gexpr[expr])
            if _leaf_tied(expr):
                return expr
            if expr in meta_by_gexpr:
                return Lit(meta_by_gexpr[expr])
        return expr

    axis_exprs = []
    for item in grid_value.items:
        if item.gexpr is None:
            # an axis the model cannot see as an expression: still
            # extractable when the interpreter proves the very same value
            # flows into a bundle scalar, a view extent or a meta constant
            owner = id(item)
            if owner in scalar_by_id:
                axis_exprs.append(Ref("bundle_scalar",
                                      (scalar_by_id[owner],)))
                continue
            if owner in view_by_id:
                axis_exprs.append(Ref("bundle_view", view_by_id[owner]))
                continue
            if owner in meta_by_id:
                axis_exprs.append(Lit(meta_by_id[owner]))
                continue
            why = item.opaque or repr(item.concrete)
            raise GridError(source.path, make_case.lineno,
                            make_case.col_offset + 1, "grid",
                            "a grid axis is not provenance-tracked (it "
                            "depends on values the model cannot see: "
                            f"{why})")
        axis_exprs.append(_rewrite(item.gexpr))
    if not axis_exprs:
        raise GridError(source.path, make_case.lineno, make_case.col_offset + 1,
                        "grid", "the grid is empty")
    if len(axis_exprs) > 3:
        raise GridError(source.path, make_case.lineno, make_case.col_offset + 1,
                        "grid",
                        f"the grid has {len(axis_exprs)} axes; Triton grids "
                        "are at most 3-D")

    # -- T033: quotient solves -------------------------------------------------
    # An axis factor the tie tables cannot read directly -- an untied
    # shape leaf (masked_cumsum's rows: only rows*n is visible, n rides
    # the n_cols scalar), a holed conditional value (fht's R: only R*D is
    # visible, D is the DIM meta constant) or a product subtree (csr's
    # B*M: only B*M*C is visible, M and C are bundle scalars) -- reads as
    # ``view_extent // cofactor`` when it appears exactly ONCE as a factor
    # of a view extent's structurally tracked product and every other
    # factor is runtime-readable.  The division is exact (the interpreter
    # itself formed the product from the factors), the runtime reads the
    # actual view extent and the actual cofactors (never a baked shape),
    # and the compile-time self-check validates the whole model against
    # the case's declared grid.

    def _factors(e) -> List[object]:
        if isinstance(e, Bin) and e.op == "mul":
            return _factors(e.left) + _factors(e.right)
        return [e]

    def _readable(e) -> bool:
        if isinstance(e, Lit):
            return True
        if isinstance(e, Ref):
            return e.kind in ("bundle_view", "bundle_scalar") or \
                (e.kind == "shape_extent" and _leaf_tied(e))
        if isinstance(e, (Bin, MinMax)):
            return _readable(e.left) and _readable(e.right)
        return False

    view_extent_trees: List[Tuple[str, int, object]] = []
    if isinstance(args_sym, SymDict):
        for argname in sorted(args_sym.mapping):
            value = args_sym.mapping.get(argname)
            if argname not in pointer_params or not isinstance(value,
                                                                SymArray):
                continue
            shape = arrays.get(argname) or ()
            for axis, extent in enumerate(value.extents):
                if axis >= len(shape):
                    break
                if extent.gexpr is not None:
                    view_extent_trees.append((argname, axis, extent.gexpr))

    def _try_solve(target):
        for view, vaxis, tree in view_extent_trees:
            factors = _factors(tree)
            hits = [i for i, f in enumerate(factors) if f == target]
            if len(hits) != 1:
                continue
            cofactors = [_rewrite(f) for i, f in enumerate(factors)
                         if i != hits[0]]
            if not cofactors:
                continue        # the direct tie; view_by_gexpr owns it
            if not all(_readable(c) for c in cofactors):
                continue
            prod = cofactors[0]
            for c in cofactors[1:]:
                prod = Bin("mul", prod, c)
            return Bin("floordiv", Ref("bundle_view", (view, vaxis)), prod)
        return None

    def _subtrees(e) -> List[object]:
        out: List[object] = []

        def walk(x):
            out.append(x)
            if isinstance(x, (Bin, MinMax)):
                walk(x.left)
                walk(x.right)

        walk(e)
        return out

    def _replace(expr, target, repl):
        if expr == target and not isinstance(expr, Lit):
            return repl
        if isinstance(expr, (Bin, MinMax)):
            left = _replace(expr.left, target, repl)
            right = _replace(expr.right, target, repl)
            if isinstance(expr, Bin):
                return Bin(expr.op, left, right)
            return MinMax(expr.op, left, right)
        return expr

    for i in range(len(axis_exprs)):
        expr = axis_exprs[i]
        for _round in range(4):        # at most a few solves per axis
            if all(_readable(s) for s in _subtrees(expr)):
                break
            solved_one = False
            for target in [s for s in _subtrees(expr) if not _readable(s)]:
                # pre-order: a product subtree (csr's B*M) is tried before
                # its factors; the whole axis before its subtrees
                if isinstance(target, (Lit, ModNonzero)):
                    continue
                solved = _try_solve(target)
                if solved is not None:
                    expr = _replace(expr, target, solved)
                    solved_one = True
                    break
            if not solved_one:
                break
        axis_exprs[i] = expr

    # -- ties: every leaf must be a literal or a bundle-visible quantity -------

    def tie_leaf(ref: Ref):
        if ref.kind == "shape_extent":
            if ref.key in scalar_ties:
                ties[ref.key] = ("scalar", scalar_ties[ref.key])
                return
            if ref.key in view_ties:
                view, axis = view_ties[ref.key]
                ties[ref.key] = ("view_extent", view, axis)
                return
            if ref.key in value_view_ties:
                view, axis = value_view_ties[ref.key]
                ties[ref.key] = ("view_extent", view, axis)
                return
            raise GridError(
                source.path, make_case.lineno, make_case.col_offset + 1,
                "grid",
                f"grid input {ref!r} (case-shape axis {ref.key[0]}) cannot "
                "be proven equal to a bundle-visible quantity (no scalar "
                "argument and no view extent shares its origin); refusing "
                "to bake a launch geometry")
        if ref.kind in ("view_extent", "bundle_view"):
            ties[ref.key] = ("view_extent", ref.key[0], ref.key[1])
            return
        if ref.kind == "bundle_scalar":
            ties[ref.key] = ("scalar", ref.key[0])
            return
        if ref.kind == "case_param":
            raise GridError(
                source.path, make_case.lineno, make_case.col_offset + 1,
                "grid",
                f"grid input {ref!r} is a case parameter (dtype/seed) and "
                "is not bundle-visible; refusing to bake a launch geometry")

    for axis_expr in axis_exprs:
        for ref in _grid_leafs(axis_expr):
            tie_leaf(ref)

    # an unfilled hole (or a mod-nonzero indicator that never combined
    # into its cdiv form) names the genuinely untraceable input
    # (MECH-DIAGNOSTIC-REFUSAL): counted, never silently baked
    for axis_expr in axis_exprs:
        holes = list(_grid_holes(axis_expr))
        mods = [m for m in _iter_modnonzero(axis_expr)]
        if holes or mods:
            why = ", ".join(repr(h) for h in (holes + mods)[:4])
            raise GridError(source.path, make_case.lineno,
                            make_case.col_offset + 1, "grid",
                            "a grid axis is not provenance-tracked (it "
                            "depends on values the model cannot see: "
                            f"{why})")

    # -- compile-time equality self-check: the REWRITTEN axes are exactly
    # what the native routine computes at run time -- evaluate them with
    # the compiling case's concrete bundle values
    concrete: Dict[Tuple, int] = {}
    for key, tie in ties.items():
        kind = tie[0]
        if kind == "scalar":
            value = (case.get("args") or {}).get(tie[1])
            if not _integral(value):
                raise GridError(
                    source.path, make_case.lineno, make_case.col_offset + 1,
                    "grid",
                    f"tied scalar argument {tie[1]!r} is not an integer at "
                    "compile time; a grid extent must be integral")
            concrete[key] = int(value)
        elif kind == "view_extent":
            view, axis = tie[1], tie[2]
            shape = arrays.get(str(view))
            if shape is None or not (0 <= int(axis) < len(shape)):
                raise GridError(
                    source.path, make_case.lineno, make_case.col_offset + 1,
                    "grid",
                    f"tied view {view!r} axis {axis} is not an array "
                    "argument of the case")
            concrete[key] = shape[int(axis)]
    try:
        modeled = [evaluate_expr(a, concrete) for a in axis_exprs]
    except (KeyError, ValueError) as exc:
        raise GridError(source.path, make_case.lineno, make_case.col_offset + 1,
                        "grid",
                        f"the rewritten grid model cannot be evaluated "
                        f"against the case payload: {exc}") from None
    declared = _declared_grid(case, source)
    if declared is None or len(declared) != len(modeled):
        raise GridError(source.path, make_case.lineno, make_case.col_offset + 1,
                        "grid",
                        "the case carries no declared grid matching the "
                        "extracted axis count")
    if tuple(modeled) != tuple(declared):
        raise GridError(
            source.path, make_case.lineno, make_case.col_offset + 1, "grid",
            f"grid self-check failed: the extracted model evaluates to "
            f"{tuple(modeled)} but the case declares {tuple(declared)}")

    return GridModel(
        axes=tuple(axis_exprs), ties=ties, ndim=len(axis_exprs),
        path=source.path,
        self_check={"modeled": list(modeled),
                    "declared": list(declared),
                    "tied_scalars": sorted(
                        str(tie[1]) for tie in ties.values()
                        if tie[0] == "scalar"),
                    "tied_views": sorted(
                        f"{tie[1]}[{tie[2]}]" for tie in ties.values()
                        if tie[0] == "view_extent")})


def _run_grid_lambda(source: OperatorSource, lam: SymLambda, case: dict,
                     make_case: ast.FunctionDef) -> Optional[SymVal]:
    """Interpret ``lambda meta: <grid>`` with meta bound to the constexpr
    payload the launcher would pass: the case's meta merged with the
    deterministically chosen autotune config (identity-tier constants fold
    to literals, exactly like every other constexpr the specialization
    folds)."""
    interp = _Interpreter(source, _module_constants(source))
    interp.env = dict(lam.closure)
    meta = dict(case.get("meta") or {})
    if source.is_autotune and source.autotune_configs:
        meta.update(source.autotune_configs[0].constexprs or {})
    params: Dict[str, SymVal] = {}
    for p in lam.node.args.args:
        params[p.arg] = SymDict({k: _lit(v) for k, v in meta.items()})
    if params:
        interp.env.update(params)
    try:
        value = interp._eval(lam.node.body)
    except GridError:
        raise
    except Exception as exc:
        raise GridError(source.path, lam.node.lineno, lam.node.col_offset + 1,
                        "grid",
                        f"the grid lambda interpretation failed: {exc}") \
            from None
    if isinstance(value, SymTuple):
        return value
    # a single (possibly untracked) value: keep it as a one-axis grid -- an
    # untracked axis still extracts when the interpreter proves the same
    # value flows into a bundle scalar / view extent / meta constant, and
    # refuses naming it otherwise
    return SymTuple([value])


def grid_of_case(module, shape=None, dtype=None, seed=None) -> Tuple[dict, dict]:
    """Build one case with the corpus's own make_case and return
    (case, describe-ready context).  A helper for census drivers."""
    case = module.make_case(shape=shape, dtype=dtype, seed=seed)
    return case, {"shape": shape, "dtype": dtype, "seed": seed}


def census(entries: Iterable[Tuple[OperatorSource, dict]]) -> dict:
    """The extraction/refusal census (acceptance[1]): every entry is a
    (source, case) pair; each either extracts (self-checked) or refuses
    with a located diagnostic.  Returns the countable record."""
    report: Dict[str, object] = {
        "entries": 0, "extracted": 0, "refused": 0,
        "refusals": {}, "ndim_histogram": {}, "tie_kinds": {},
        "details": [],
    }
    for source, case in entries:
        report["entries"] += 1
        try:
            model = extract_grid(source, case)
        except GridError as exc:
            report["refused"] += 1
            key = exc.construct
            report["refusals"][key] = report["refusals"].get(key, 0) + 1
            report["details"].append(
                {"source": source.rel_path, "outcome": "refused",
                 "construct": exc.construct,
                 "location": f"{exc.path}:{exc.line}:{exc.col}",
                 "message": exc.message})
            continue
        except Exception as exc:              # unexpected: recorded, counted
            report["refused"] += 1
            key = f"internal:{type(exc).__name__}"
            report["refusals"][key] = report["refusals"].get(key, 0) + 1
            report["details"].append(
                {"source": source.rel_path, "outcome": "refused",
                 "construct": key, "location": "",
                 "message": str(exc)})
            continue
        report["extracted"] += 1
        ndim = model.ndim
        report["ndim_histogram"][ndim] = \
            report["ndim_histogram"].get(ndim, 0) + 1
        for tie in model.ties.values():
            kind = tie[0]
            report["tie_kinds"][kind] = report["tie_kinds"].get(kind, 0) + 1
        report["details"].append(
            {"source": source.rel_path, "outcome": "extracted",
             "ndim": ndim, "axes": [repr(a) for a in model.axes],
             "ties": {f"{k}": list(v) for k, v in model.ties.items()},
             "self_check": dict(model.self_check)})
    return report
