"""The provenance-tracking case-layer grid model (frontend, T008).

The bundle carries views and scalars but not the grid (a100-native-io/v1,
F046/F047) and the identity contract excludes it (the corpus's own
economics, T003 section 7), so the grid must be *evaluated natively at run
time* from bundle-visible quantities.  This module extracts the grid
*expression* from the operator's case layer (``_make_case``) by
interpreting its AST under a provenance-tracking evaluator:

  - the case parameters (``shape``, ``dtype``, ``seed``) enter symbolically;
  - every value the grid expression consumes must be proven equal to a
    bundle-visible quantity -- a scalar argument (by symbolic-origin
    equality through the interpreted ``args`` construction) or a view
    extent (an array whose tracked extent flows into ``args``);
  - a compile-time equality self-check re-evaluates every axis expression
    with the compiling case's concrete values and requires it to equal the
    case's own declared ``grid``.

Corpus grid forms covered: multi-axis tuples, ``triton.cdiv`` products,
the ``lambda meta:`` form (meta constexpr leaves are identity-tier
constants, like every other constexpr the specialization folds), shape
derived locals (``n = int(shape[0])``, ``np.prod``), view extents
(``x.shape[0]``, arrays created from tracked sizes) and scalar arguments.

A grid input that cannot be tied to a bundle-visible quantity is refused
with a located diagnostic (MECH-DIAGNOSTIC-REFUSAL), never baked; the
extraction/refusal census (:func:`census`) makes both sides countable.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

from a100c.frontend.source import OperatorSource

__all__ = ["GridError", "GridExpr", "Lit", "Ref", "Bin", "GridModel",
           "extract_grid", "evaluate_expr", "census", "grid_of_case"]


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


_TRACE_BUILTINS = {"int", "tuple", "len", "min", "max", "abs", "dict",
                   "str", "round", "float", "bool"}

#: numpy/np constructors whose shape argument positions are modeled
_NP_CTORS = {"zeros", "empty", "ones", "full", "zeros_like", "empty_like",
             "ones_like", "arange", "tile", "repeat"}

#: rng methods whose last positional argument is the size
_RNG_SIZE_METHODS = {"standard_normal", "normal", "integers", "random",
                     "rand", "randn", "choice", "permutation"}


class _Interpreter:
    """Evaluates ``_make_case``'s statements in the provenance domain."""

    def __init__(self, source: OperatorSource,
                 module_constants: Dict[str, object]):
        self.source = source
        self.constants = module_constants
        self.env: Dict[str, SymVal] = {}
        self.path = source.path
        #: the args-literal entries: arg name -> the SymVal object flowing in
        self.arg_values: Dict[str, SymVal] = {}
        #: the returned payload dict (grid may live there as a lambda)
        self.returned: Optional[SymDict] = None

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
                if isinstance(value, SymDict):
                    self.returned = value
                break
            self._stmt(stmt)
        return self.env

    def _stmt(self, stmt: ast.stmt) -> None:
        if isinstance(stmt, ast.Assign):
            value = self._eval(stmt.value)
            for target in stmt.targets:
                self._assign(target, value)
        elif isinstance(stmt, ast.AnnAssign):
            if stmt.value is not None:
                self._assign(stmt.target, self._eval(stmt.value))
        elif isinstance(stmt, ast.AugAssign):
            current = self.env.get(stmt.target.id) \
                if isinstance(stmt.target, ast.Name) else None
            if current is None:
                raise self._err(stmt, "augmented assignment",
                                "target is not defined")
            binop = ast.BinOp(left=stmt.target, op=stmt.op, right=stmt.value)
            ast.copy_location(binop, stmt)
            self._assign(stmt.target, self._eval(binop))
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
                    # real work on both arms: interpret BOTH and keep only
                    # the bindings that agree (a branch-dependent value is
                    # untracked -- a grid axis consuming it refuses,
                    # located, at the axis check; post-grid mutations of
                    # opaque case dicts simply happen)
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
                        merged[key] = t if t is e else _opaque(
                            "branch-dependent value")
                    self.env = merged
            elif cond.concrete:
                for s in stmt.body:
                    self._stmt(s)
            else:
                for s in stmt.orelse:
                    self._stmt(s)
        elif isinstance(stmt, ast.For):
            rng = stmt.iter
            if not (isinstance(rng, ast.Call)
                    and isinstance(rng.func, ast.Name)
                    and rng.func.id == "range"):
                raise self._err(stmt, "for",
                                "loops in the case layer are outside the "
                                "grid model (only concrete range() loops "
                                "unroll)")
            vals = []
            for a in rng.args:
                v = self._eval(a)
                if v.concrete is None or not isinstance(v.concrete, int) \
                        or isinstance(v.concrete, bool):
                    raise self._err(stmt, "for",
                                    "a case-layer loop with a symbolic "
                                    "bound is outside the grid model "
                                    "(refused, not guessed)")
                vals.append(v.concrete)
            start = vals[0] if len(vals) > 1 else 0
            stop = vals[1] if len(vals) > 1 else vals[0]
            step = vals[2] if len(vals) > 2 else 1
            if not isinstance(stmt.target, ast.Name):
                raise self._err(stmt, "for",
                                "the loop target must be a plain name")
            name = stmt.target.id
            saved = self.env.get(name)
            k = start
            while (step > 0 and k < stop) or (step < 0 and k > stop):
                self.env[name] = _lit(k)
                for s in stmt.body:
                    self._stmt(s)
                k += step
            if saved is not None:
                self.env[name] = saved
            else:
                self.env.pop(name, None)
        elif isinstance(stmt, (ast.While, ast.AsyncFor)):
            raise self._err(stmt, type(stmt).__name__.lower(),
                            "loops in the case layer are outside the grid "
                            "model")
        else:
            raise self._err(stmt, type(stmt).__name__,
                            "statement is outside the grid model")

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
            # an unknown module-level name (a function, the jit kernel, an
            # imported helper): untracked.  If the grid expression depended
            # on it, the expression would be untracked and the extraction
            # refuses -- conservative, never a guess.
            return _opaque(f"name {node.id}")
        if isinstance(node, (ast.Tuple, ast.List)):
            return SymTuple([self._eval(e) for e in node.elts])
        if isinstance(node, ast.Dict):
            mapping: Dict[str, SymVal] = {}
            for k, v in zip(node.keys, node.values):
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
                return _opaque("symbolic conditional expression")
            return self._eval(node.body if cond.concrete else node.orelse)
        if isinstance(node, ast.BoolOp):
            # and/or over case values: folds when every side is concrete;
            # otherwise untracked (a guard consuming it still proves
            # itself; a grid axis consuming it refuses later)
            sides = [self._eval(v) for v in node.values]
            if all(s.concrete is not None for s in sides):
                out = bool(sides[0].concrete)
                for s in sides[1:]:
                    if isinstance(node.op, ast.And):
                        out = out and bool(s.concrete)
                    else:
                        out = out or bool(s.concrete)
                return _lit(out)
            return _opaque("boolop")
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
        """A tracked product (np.prod / .size): folds when concrete."""
        if all(i.concrete is not None for i in items):
            out = 1
            for i in items:
                out = out * i.concrete
            return _lit(out)
        if any(i.gexpr is None for i in items):
            raise self._err(node, "product",
                            "product over an untracked extent (the grid "
                            "input cannot be tied; refused, not guessed)")
        gexpr = items[0].gexpr
        for i in items[1:]:
            gexpr = Bin("mul", gexpr, i.gexpr)
        return SymVal(gexpr=gexpr)

    def _binop(self, node: ast.BinOp) -> SymVal:
        lhs = self._eval(node.left)
        rhs = self._eval(node.right)
        opname = {ast.Add: "add", ast.Sub: "sub", ast.Mult: "mul",
                  ast.FloorDiv: "floordiv", ast.Div: "div", ast.Mod: "mod",
                  ast.Pow: "pow"}.get(type(node.op))
        if opname is None:
            return _opaque(f"operator {type(node.op).__name__}")
        if lhs.concrete is not None and rhs.concrete is not None:
            import operator as _op
            fn = {"add": _op.add, "sub": _op.sub, "mul": _op.mul,
                  "div": _op.truediv, "floordiv": _op.floordiv,
                  "mod": _op.mod, "pow": _op.pow}[opname]
            return _lit(fn(lhs.concrete, rhs.concrete))
        # symbolic arithmetic: both sides must carry grid expressions;
        # otherwise the value is untracked (a grid axis consuming it
        # refuses at the axis check -- conservative, never a guess)
        if lhs.gexpr is None or rhs.gexpr is None:
            def _why(v):
                if v.opaque:
                    return v.opaque
                if v.origin is not None:
                    return repr(v.origin)
                return "untracked"
            return _opaque(f"{opname}({_why(lhs)}, {_why(rhs)})")
        if opname not in ("add", "sub", "mul", "floordiv"):
            return _opaque(f"operator {opname}")
        return SymVal(gexpr=Bin(opname, lhs.gexpr, rhs.gexpr))

    # -- calls ----------------------------------------------------------------
    def _cdiv(self, node: ast.Call, args: List[SymVal]) -> SymVal:
        """triton.cdiv(a, b) = (a + b - 1) // b -- the exact pinned form."""
        if len(args) != 2:
            raise self._err(node, "triton.cdiv", "cdiv takes two arguments")
        a, b = args
        if a.concrete is not None and b.concrete is not None:
            return _lit((a.concrete + b.concrete - 1) // b.concrete)
        if a.gexpr is None or b.gexpr is None:
            def _why2(v):
                if v.opaque:
                    return v.opaque
                if v.origin is not None:
                    return repr(v.origin)
                return "untracked"
            return _opaque(f"triton.cdiv({_why2(a)}, {_why2(b)})")
        return SymVal(gexpr=Bin(
            "floordiv",
            Bin("add", a.gexpr,
                Bin("sub", b.gexpr, Lit(1))),
            b.gexpr))

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
        if isinstance(base, SymArray):
            if method == "astype":
                return SymArray(list(base.extents))     # extents preserved
            if method == "reshape":
                if args and isinstance(args[0], SymTuple):
                    return SymArray(list(args[0].items))
                if args and args[0].tracked:
                    return SymArray([args[0]])
                return _opaque("reshape")
            if method == "sum" and not args:
                return self._product(base.extents, node)
            if method in _RNG_SIZE_METHODS:
                return self._rng_method(node, method, args)
            return _opaque(f".{method}")
        if base.opaque is not None and "module" in str(base.opaque):
            return _opaque(f".{method}")
        if base.opaque is not None and method in _RNG_SIZE_METHODS:
            return self._rng_method(node, method, args)
        return _opaque(f".{method}")

    def _call(self, node: ast.Call) -> SymVal:
        func = node.func
        name = func.id if isinstance(func, ast.Name) else None
        dotted = None
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            dotted = f"{func.value.id}.{func.attr}"
        # triton.cdiv -- the pinned ceiling division
        if dotted == "triton.cdiv":
            return self._cdiv(node, [self._eval(a) for a in node.args])
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
            if tail == "ceil" and len(node.args) == 1:
                arg = node.args[0]
                if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Div):
                    a = self._eval(arg.left)
                    b = self._eval(arg.right)
                    if a.gexpr is not None and b.gexpr is not None:
                        # ceil(a / b) = -((-a) // b) for the positive
                        # extents the grid expression set carries
                        neg = Bin("sub", Lit(0), a.gexpr)
                        return SymVal(gexpr=Bin(
                            "sub", Lit(0), Bin("floordiv", neg, b.gexpr)))
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
            if isinstance(base, SymArray) or base.opaque is not None:
                args = [self._eval(a) for a in node.args]
                for k in node.keywords:
                    self._eval(k.value)
                return self._method_call(node, base, args)
        if name in _TRACE_BUILTINS:
            args = [self._eval(a) for a in node.args]
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
                if name in ("min", "max") and len(args) == 2 \
                        and args[0].gexpr is not None \
                        and args[1].gexpr is not None:
                    # min/max over tracked values: one MinMax node (the
                    # native routine realizes it with the declared
                    # compare/mask/select scalar sequence)
                    return SymVal(gexpr=MinMax(name, args[0].gexpr,
                                               args[1].gexpr))
                if name in ("min", "max") and len(args) == 2:
                    why = args[0].opaque or args[1].opaque or "untracked"
                    return _opaque(f"{name}({why})")
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
            if name in ("min", "max"):
                # min/max over tracked values carries as one MinMax node
                # (the native routine realizes it with the declared
                # compare/mask/select scalar sequence); an untracked
                # operand stays untracked (a grid axis consuming it
                # refuses, located, at the axis check)
                if len(args) == 2 and args[0].gexpr is not None \
                        and args[1].gexpr is not None:
                    return SymVal(gexpr=MinMax(name, args[0].gexpr,
                                               args[1].gexpr))
                why = (args[0].opaque or args[1].opaque
                       if len(args) == 2 else "untracked")
                return _opaque(f"{name}({why})")
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
            if index is None or index.concrete is None:
                return _opaque("symbolic tuple index")
            if not isinstance(index.concrete, int):
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
            if index is None or index.concrete is None:
                return _opaque("symbolic array extent index")
            return base.extents[int(index.concrete)]
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


def _shape_arity(source: OperatorSource, case: dict) -> Tuple[Tuple, Tuple]:
    """The case's shape as (payload-shape, interpreted-shape).

    Schema-3 payloads echo ``shape``; older payloads do not, and the arity
    comes from the operator's own SHAPES table (the runner passes shapes of
    that arity -- a different arity is refused by the operator itself).
    Returns (concrete-shape-tuple, arity)."""
    shape = case.get("shape") or ()
    if len(shape):
        return tuple(int(v) for v in shape), len(shape)
    shapes_table = source.case_literals.get("SHAPES") or ()
    if shapes_table:
        try:
            first = shapes_table[0]
            return (), len(first)
        except (TypeError, IndexError):
            pass
    return (), 0


def _interp_once(source: OperatorSource, case: dict,
                 view_bindings: Dict[str, SymArray],
                 module_constants: Dict[str, object],
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
            for i in range(ndim)]),
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
    interp = _Interpreter(source, module_constants)
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
    arrays = _array_args(case)

    # -- pass 1: find which locals flow into the array args -------------------
    interp, env = _interp_once(source, case, {}, module_constants, make_case)
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
                                   make_case)
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
                                       module_constants, make_case)

    # -- the grid value ---------------------------------------------------------
    grid_value = env.get("grid")
    if grid_value is None and isinstance(interp.returned, SymDict):
        grid_value = interp.returned.mapping.get("grid")
    if isinstance(grid_value, SymLambda):
        grid_value = _run_grid_lambda(source, grid_value, case, make_case)
    if grid_value is None or not isinstance(grid_value, SymTuple):
        raise GridError(source.path, make_case.lineno, make_case.col_offset + 1,
                        "grid",
                        "the case layer never assigns a trackable 'grid' "
                        "(the grid form cannot be extracted)")
    axis_exprs = []
    for item in grid_value.items:
        if item.gexpr is None:
            why = item.opaque or repr(item.concrete)
            raise GridError(source.path, make_case.lineno,
                            make_case.col_offset + 1, "grid",
                            "a grid axis is not provenance-tracked (it "
                            "depends on values the model cannot see: "
                            f"{why})")
        axis_exprs.append(item.gexpr)
    if not axis_exprs:
        raise GridError(source.path, make_case.lineno, make_case.col_offset + 1,
                        "grid", "the grid is empty")
    if len(axis_exprs) > 3:
        raise GridError(source.path, make_case.lineno, make_case.col_offset + 1,
                        "grid",
                        f"the grid has {len(axis_exprs)} axes; Triton grids "
                        "are at most 3-D")

    # -- ties: every leaf must be a literal or a bundle-visible quantity -------
    args_sym = env.get("args")
    if not isinstance(args_sym, SymDict) and isinstance(interp.returned,
                                                        SymDict):
        candidate = interp.returned.mapping.get("args")
        if isinstance(candidate, SymDict):
            args_sym = candidate
    scalar_ties: Dict[Tuple, str] = {}
    view_ties: Dict[Tuple, Tuple[str, int]] = {}
    if isinstance(args_sym, SymDict):
        for argname, value in args_sym.mapping.items():
            if isinstance(value, SymArray):
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
            elif value is not None and value.origin is not None \
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
            for axis, extent in enumerate(shape):
                for i, want in enumerate(payload_shape):
                    if int(extent) == int(want):
                        value_view_ties.setdefault((i,), (view, axis))
                        break

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
        if ref.kind == "view_extent":
            ties[ref.key] = ("view_extent", ref.key[0], ref.key[1])
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

    # -- compile-time equality self-check --------------------------------------
    concrete: Dict[Tuple, int] = {}
    for key, tie in ties.items():
        kind = tie[0]
        if kind == "scalar":
            value = (case.get("args") or {}).get(tie[1])
            if isinstance(value, bool) or not isinstance(value, int):
                raise GridError(
                    source.path, make_case.lineno, make_case.col_offset + 1,
                    "grid",
                    f"tied scalar argument {tie[1]!r} is not an integer at "
                    "compile time; a grid extent must be integral")
            concrete[key] = value
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
    shape = case.get("shape") or ()
    for i, extent in enumerate(shape):
        concrete.setdefault(("shape_extent", (i,)), int(extent))
    modeled = [evaluate_expr(a, concrete) for a in axis_exprs]
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
    if value.tracked or value.concrete is not None:
        return SymTuple([value])
    return None


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
