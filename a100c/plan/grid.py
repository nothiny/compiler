"""The provenance-checked case-layer grid model (launch geometry is runtime).

The bundle carries views and scalars but not the grid (a100-native-io/v1,
F046/F047) and the identity contract excludes it, so the grid must be
*evaluated natively at run time* from bundle-visible quantities.  This module
extracts the grid *expression* from the operator's case layer (``_make_case``)
by interpreting its AST under a provenance-tracking evaluator:

  - the case parameters (``shape``, ``dtype``, ``seed``) enter symbolically;
  - every value the grid expression consumes must be proven equal to a
    bundle-visible quantity -- a scalar argument (by symbolic-origin equality
    through the interpreted ``args`` construction) or a view extent (when the
    array's shape was tracked);
  - a compile-time equality self-check re-evaluates the expression with the
    compiling case's concrete values and requires it to equal the case's own
    declared ``grid``.

A grid input that cannot be tied to a bundle-visible quantity is refused with
a located diagnostic (MECH-DIAGNOSTIC-REFUSAL), never baked.  Only the 1-D
grid form is extracted by the vertical slice; multi-dimensional grids are a
located refusal, not a silent flattening.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from a100c.frontend.source import OperatorSource

__all__ = ["GridError", "GridExpr", "GridModel", "extract_grid",
           "evaluate_expr"]


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

    kind: str          # 'shape_extent' | 'case_param' | 'scalar' | 'view_extent'
    key: Tuple          # (axis,) / (name,) / (view_name, axis)

    def __repr__(self):
        return f"${self.kind}{self.key}"


@dataclass(frozen=True)
class Bin:
    op: str            # 'add' | 'sub' | 'mul' | 'floordiv'
    left: object
    right: object

    def __repr__(self):
        return f"({self.left!r} {self.op} {self.right!r})"


GridExpr = object


def evaluate_expr(expr, values: Dict) -> Tuple[int, ...] | int:
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
        super().__init__(origin=origin,
                         concrete=tuple(i.concrete for i in items)
                         if all(i.concrete is not None for i in items) else None)
        self.items = items


class SymDict(SymVal):
    """A tracked dict (e.g. the args literal)."""

    __slots__ = ("mapping",)

    def __init__(self, mapping: Dict[str, SymVal]):
        super().__init__()
        self.mapping = dict(mapping)


def _lit(value) -> SymVal:
    # integer literals carry a grid expression so arithmetic can mix them
    # with symbolic leaves (n + 128 - 1) // 128
    gexpr = Lit(value) if isinstance(value, int) and not isinstance(value, bool) \
        else None
    return SymVal(concrete=value, gexpr=gexpr)


def _opaque(desc: str) -> SymVal:
    return SymVal(opaque=desc)


_TRACE_BUILTINS = {"int", "tuple", "len", "min", "max", "abs", "dict",
                   "str", "round", "float", "bool"}


class _Interpreter:
    """Evaluates ``_make_case``'s statements in the provenance domain."""

    def __init__(self, source: OperatorSource, module_constants: Dict[str, object]):
        self.source = source
        self.constants = module_constants
        self.env: Dict[str, SymVal] = {}
        self.path = source.path

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
            return SymDict({k: self._from_concrete(v) for k, v in value.items()})
        return _opaque(repr(value))

    # -- statements -----------------------------------------------------------
    def run(self, fn: ast.FunctionDef, params: Dict[str, SymVal]) -> Dict[str, SymVal]:
        self.env = dict(params)
        for stmt in fn.body:
            if isinstance(stmt, ast.Return):
                self._eval(stmt.value)      # the payload is opaque; locals stay
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
                raise self._err(stmt, "if",
                                "the case layer branches on a symbolic "
                                "condition; the grid model cannot prove a "
                                "branch (refused, not guessed)")
            if cond.concrete:
                for s in stmt.body:
                    self._stmt(s)
            else:
                for s in stmt.orelse:
                    self._stmt(s)
        elif isinstance(stmt, (ast.For, ast.While, ast.AsyncFor)):
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
                raise self._err(target, "assignment",
                                "cannot unpack an untracked value")
            if len(target.elts) != len(value.items):
                raise self._err(target, "assignment", "unpack arity mismatch")
            for t, v in zip(target.elts, value.items):
                self._assign(t, v)
        elif isinstance(target, ast.Subscript):
            base = self.env.get(self._name_of(target.value))
            if isinstance(base, SymTuple):
                raise self._err(target, "subscript store",
                                "mutation of a provenance-tracked value "
                                "invalidates the grid model")
            # a store into an opaque object (e.g. x[::11] = -0.0): untracked
        else:
            raise self._err(target, "assignment",
                            "assignment target outside the grid model")

    def _name_of(self, node) -> Optional[str]:
        return node.id if isinstance(node, ast.Name) else None

    # -- expressions ------------------------------------------------------------
    def _eval(self, node: ast.expr) -> SymVal:
        if isinstance(node, ast.Constant):
            return _lit(node.value)
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
                    raise self._err(node, "dict", "dict keys must be literals")
                mapping[k.value] = self._eval(v)
            return SymDict(mapping)
        if isinstance(node, ast.BinOp):
            return self._binop(node)
        if isinstance(node, ast.UnaryOp):
            v = self._eval(node.operand)
            if v.concrete is None:
                raise self._err(node, type(node.op).__name__,
                                "unary op on an untracked value")
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
                if left.concrete is None or right.concrete is None:
                    raise self._err(node, "comparison",
                                    "symbolic comparison in the case layer")
                out = self._compare(op, left.concrete, right.concrete)
                left = right
            return _lit(out)
        if isinstance(node, ast.IfExp):
            cond = self._eval(node.test)
            if cond.concrete is None:
                raise self._err(node, "ifexp",
                                "symbolic conditional expression in the case "
                                "layer")
            return self._eval(node.body if cond.concrete else node.orelse)
        if isinstance(node, ast.Call):
            return self._call(node)
        if isinstance(node, ast.Subscript):
            return self._subscript(node)
        if isinstance(node, ast.Attribute):
            base = self._eval(node.value)
            if base.concrete is not None and not hasattr(base, "items"):
                attr = getattr(base.concrete, node.attr, None)
                if attr is not None and not callable(attr):
                    return _lit(attr)
            return _opaque(f"attribute .{node.attr}")
        raise self._err(node, type(node).__name__,
                        "expression is outside the grid model")

    def _binop(self, node: ast.BinOp) -> SymVal:
        lhs = self._eval(node.left)
        rhs = self._eval(node.right)
        opname = {ast.Add: "add", ast.Sub: "sub", ast.Mult: "mul",
                  ast.FloorDiv: "floordiv", ast.Div: "div", ast.Mod: "mod",
                  ast.Pow: "pow"}.get(type(node.op))
        if opname is None:
            raise self._err(node, type(node.op).__name__,
                            "operator is outside the grid model")
        if lhs.concrete is not None and rhs.concrete is not None:
            import operator as _op
            fn = {"add": _op.add, "sub": _op.sub, "mul": _op.mul,
                  "div": _op.truediv, "floordiv": _op.floordiv,
                  "mod": _op.mod, "pow": _op.pow}[opname]
            return _lit(fn(lhs.concrete, rhs.concrete))
        # symbolic arithmetic: both sides must carry grid expressions
        if lhs.gexpr is None or rhs.gexpr is None:
            raise self._err(node, opname,
                            "grid arithmetic on a value that is not "
                            "provenance-tracked (refused, not guessed)")
        if opname not in ("add", "sub", "mul", "floordiv"):
            raise self._err(node, opname,
                            f"operator {opname!r} is not in the supported grid "
                            "expression set")
        return SymVal(gexpr=Bin(opname, lhs.gexpr, rhs.gexpr))

    @staticmethod
    def _compare(op, lhs, rhs):
        import operator as _op
        return {ast.Eq: _op.eq, ast.NotEq: _op.ne, ast.Lt: _op.lt,
                ast.LtE: _op.le, ast.Gt: _op.gt, ast.GtE: _op.ge}[type(op)](
            lhs, rhs)

    def _call(self, node: ast.Call) -> SymVal:
        name = node.func.id if isinstance(node.func, ast.Name) else None
        if name in _TRACE_BUILTINS:
            args = [self._eval(a) for a in node.args]
            if any(a.concrete is None for a in args):
                # int()/tuple()/dict() wrapping a symbolic value: the value
                # passes through unchanged (its tracked-ness is what matters;
                # an untracked value flowing into the grid expression makes
                # the extraction refuse later -- conservative, never a guess)
                if name in ("int", "tuple", "dict", "float", "bool") \
                        and len(args) == 1:
                    return args[0]
                if name == "len" and len(args) == 1 \
                        and isinstance(args[0], SymTuple):
                    return _lit(len(args[0].items))
                raise self._err(node, name,
                                f"{name}() on a symbolic value is outside the "
                                "grid model")
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
                return _lit(len(vals[0]))
            if name in ("min", "max", "abs", "round", "float", "bool"):
                return _lit({  # type: ignore[misc]
                    "min": min, "max": max, "abs": abs, "round": round,
                    "float": float, "bool": bool}[name](*vals))
        # any other call (fast_rng, _aligned, np.*, _case): untracked
        for a in node.args:
            if isinstance(a, ast.expr):
                self._eval(a)
        for k in node.keywords:
            self._eval(k.value)
        callee = name or (ast.unparse(node.func) if hasattr(ast, "unparse")
                          else "call")
        return _opaque(f"call {callee}")

    def _subscript(self, node: ast.Subscript) -> SymVal:
        base = self._eval(node.value)
        index = self._eval(node.slice) if not isinstance(node.slice, ast.Slice) \
            else None
        if isinstance(base, SymTuple):
            if index is None or index.concrete is None:
                raise self._err(node, "subscript",
                                "symbolic index into a tracked tuple")
            if not isinstance(index.concrete, int):
                raise self._err(node, "subscript",
                                "tuple index must be an integer")
            if not (0 <= index.concrete < len(base.items)):
                raise self._err(node, "subscript", "tuple index out of range")
            return base.items[index.concrete]
        if isinstance(base, SymDict):
            if index is None or index.concrete is None:
                raise self._err(node, "subscript",
                                "symbolic key into a tracked dict")
            if index.concrete not in base.mapping:
                raise self._err(node, "subscript",
                                f"key {index.concrete!r} not in the tracked "
                                "dict")
            return base.mapping[index.concrete]
        return _opaque("subscript")


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------


@dataclass
class GridModel:
    """The extracted 1-D grid form + its bundle-visible ties."""

    expr: GridExpr
    #: leaf origin Ref -> ('scalar', argument_name) | ('view_extent', view, axis)
    ties: Dict[Tuple, Tuple[str, object]] = field(default_factory=dict)
    ndim: int = 1
    path: str = ""
    #: the self-check record (compile-time equality with the case's grid)
    self_check: Dict[str, object] = field(default_factory=dict)

    def describe(self) -> dict:
        return {"ndim": self.ndim, "expr": repr(self.expr),
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
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)):
            try:
                out[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, SyntaxError):
                continue
    return out


def _read_source(source: OperatorSource) -> str:
    with open(source.path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def extract_grid(source: OperatorSource, case: dict) -> GridModel:
    """Extract the 1-D grid form from the case layer, with provenance.

    Refuses (GridError, located) when: the case layer has no grid assignment,
    the grid is not 1-D, a grid input cannot be tied to a bundle-visible
    quantity, or the compile-time self-check disagrees with the case's grid.
    """
    if source.kernel_ast is None:  # pragma: no cover - loader guarantees it
        raise GridError(source.path, 1, 0, "case layer", "kernel AST missing")
    text = _read_source(source)
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:  # pragma: no cover - loader parsed it already
        raise GridError(source.path, exc.lineno or 1, exc.offset or 1,
                        "case layer", f"syntax error: {exc.msg}") from None

    make_case = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "_make_case":
            make_case = node
            break
    if make_case is None:
        raise GridError(source.path, 1, 0, "_make_case",
                        "the case layer has no _make_case function; the grid "
                        "form cannot be extracted (FE-SOURCE-CONTRACT)")

    shape = case.get("shape") or ()
    ndim = len(shape)
    params: Dict[str, SymVal] = {
        "shape": SymTuple([SymVal(
            origin=Ref("shape_extent", (i,)), gexpr=Ref("shape_extent", (i,)))
            for i in range(ndim)]),
        "dtype": SymVal(origin=Ref("case_param", ("dtype",))),
        "seed": SymVal(origin=Ref("case_param", ("seed",))),
    }
    interp = _Interpreter(source, _module_constants(source))
    try:
        env = interp.run(make_case, params)
    except GridError:
        raise
    except Exception as exc:  # interpretation beyond the model: refuse
        raise GridError(source.path, make_case.lineno, make_case.col_offset + 1,
                        "_make_case",
                        f"case-layer interpretation failed: {exc}") from None

    grid_value = env.get("grid")
    if grid_value is None or not isinstance(grid_value, SymTuple):
        raise GridError(source.path, make_case.lineno, make_case.col_offset + 1,
                        "grid",
                        "the case layer never assigns a trackable 'grid' "
                        "(the grid form cannot be extracted)")
    if len(grid_value.items) != 1:
        raise GridError(
            source.path, make_case.lineno, make_case.col_offset + 1, "grid",
            f"the grid has {len(grid_value.items)} dimension(s); only the 1-D "
            "grid form is lowered by the vertical slice (a multi-dimensional "
            "grid is refused, never flattened)")
    axis_expr = grid_value.items[0].gexpr
    if axis_expr is None:
        raise GridError(source.path, make_case.lineno, make_case.col_offset + 1,
                        "grid",
                        "the grid expression is not provenance-tracked "
                        "(it depends on values the model cannot see)")

    # -- ties: every leaf must be a literal or a bundle-visible quantity ----
    args_value = env.get("args")
    scalar_ties: Dict[Tuple, str] = {}
    if isinstance(args_value, SymDict):
        for name, value in args_value.mapping.items():
            if value.origin is not None and value.origin.kind == "shape_extent":
                scalar_ties.setdefault(value.origin.key, name)
    ties: Dict[Tuple, Tuple[str, object]] = {}

    def tie_leaf(ref: Ref):
        if ref.kind == "shape_extent":
            if ref.key in scalar_ties:
                ties[ref.key] = ("scalar", scalar_ties[ref.key])
                return
            raise GridError(
                source.path, make_case.lineno, make_case.col_offset + 1, "grid",
                f"grid input {ref!r} cannot be proven equal to a "
                "bundle-visible quantity (no scalar argument shares its "
                "origin); refusing to bake a launch geometry")
        if ref.kind in ("case_param",):
            raise GridError(
                source.path, make_case.lineno, make_case.col_offset + 1, "grid",
                f"grid input {ref!r} is a case parameter (dtype/seed) and is "
                "not bundle-visible; refusing to bake a launch geometry")

    def walk(expr):
        if isinstance(expr, Ref):
            tie_leaf(expr)
        elif isinstance(expr, Bin):
            walk(expr.left)
            walk(expr.right)

    walk(axis_expr)

    # -- compile-time equality self-check ------------------------------------
    concrete: Dict[Tuple, int] = {}
    for key, tie in ties.items():
        kind, name = tie[0], tie[1]
        if kind == "scalar":
            value = (case.get("args") or {}).get(name)
            if isinstance(value, bool) or not isinstance(value, int):
                raise GridError(
                    source.path, make_case.lineno, make_case.col_offset + 1,
                    "grid",
                    f"tied scalar argument {name!r} is not an integer at "
                    "compile time; a grid extent must be integral")
            concrete[key] = value
    for i, extent in enumerate(shape):
        concrete[("shape_extent", (i,))] = int(extent)
    modeled = evaluate_expr(axis_expr, concrete)
    declared = case.get("grid")
    if declared is None or len(tuple(declared)) != 1:
        raise GridError(source.path, make_case.lineno, make_case.col_offset + 1,
                        "grid", "the case carries no 1-D declared grid")
    declared0 = int(tuple(declared)[0])
    if modeled != declared0:
        raise GridError(
            source.path, make_case.lineno, make_case.col_offset + 1, "grid",
            f"grid self-check failed: the extracted model evaluates to "
            f"{modeled} but the case declares {declared0}")

    return GridModel(
        expr=axis_expr, ties=ties, ndim=1, path=source.path,
        self_check={"modeled": modeled, "declared": declared0,
                    "tied_scalars": sorted(
                        name for _, (kind, name) in ties.items()
                        if kind == "scalar")})
