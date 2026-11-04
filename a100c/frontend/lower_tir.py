"""AST -> TIR lowering for the elementwise core (task T006).

Lowered today: masked load with ``other`` / store, arithmetic, comparison,
logical/bitwise ops, ``where``, constants, ``program_id``, and the
tensor-creation forms ``tl.arange`` (start/end define the block index
space), ``tl.zeros``, ``tl.full``, ``tl.zeros_like``.

Everything is typed per the pinned Triton 3.8 semantics
(``a100c/frontend/types.py``); the implicit casts the pinned semantics
perform (binary-op unification, store value, load ``other``, ``where``
branches) become *explicit* ``convert`` ops in TIR, and implicit
broadcasting becomes explicit ``broadcast`` ops with flagged extents --
so the TIR verifier's type and shape invariants are strict.

Constexpr folding: ``if``/conditional expressions on compile-time
conditions take only the live branch (dead dtype-dispatch branches -- the
16 ``tl.float64`` branches no declared case dtype exercises -- disappear
while the comparison itself is evaluated and recorded in the fold record).

Anything else -- control flow, subscripts, reductions, casts, math -- is
refused with a located diagnostic naming the construct (never silently
compiled); later tasks in the DAG implement those.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

from a100c.frontend import shapes as fshapes
from a100c.frontend import types as ftypes
from a100c.frontend.source import FrontendError, OperatorSource
from a100c.frontend.specialize import (DTypeValue, NOT_CONSTEXPR,
                                       Specialization, TypeObject,
                                       py_scalar)
from a100c.frontend.surface import (CLASS_IGNORABLE, CLASS_IMPLEMENTED,
                                    CLASS_REFUSED, EXCLUDED_CONSTRUCTS,
                                    Surface, DEFAULT_SURFACE)
from a100c.ir import tir

__all__ = ["ConstVal", "Lowering", "lower", "IgnoredParam"]


@dataclass
class ConstVal:
    """A compile-time value flowing through the lowering (a literal, a
    constexpr parameter, a folded expression or a dtype)."""
    value: object


@dataclass
class IgnoredParam:
    construct: str
    param: str
    reason: str


#: method-call forms that map to declared constructs (``.to`` is ``tl.cast``)
_METHOD_CONSTRUCTS = {".to": "tl.cast"}

#: parameters each implemented construct requires
_REQUIRED_PARAMS = {
    "tl.load": ("pointer",),
    "tl.store": ("pointer", "value"),
    "tl.arange": ("start", "end"),
    "tl.program_id": (),
    "tl.where": ("condition", "x", "y"),
    "tl.zeros": ("shape", "dtype"),
    "tl.full": ("shape", "value", "dtype"),
    "tl.zeros_like": ("input",),
    "tl.constexpr": ("value",),
    "tl.multiple_of": ("input", "values"),
    "tl.max_contiguous": ("input", "values"),
}


class Lowering:
    """One (source, specialization) -> TIR lowering run."""

    def __init__(self, source: OperatorSource, spec: Specialization,
                 surface: Optional[Surface] = None):
        self.source = source
        self.spec = spec
        self.surface = surface or DEFAULT_SURFACE
        self.fold = spec.fold
        self.env = spec.env()
        self.ignored: List[IgnoredParam] = []
        self._names: set = set()
        self.module = tir.Module(source.kernel_name, source.path)
        loc = None
        if source.kernel_ast is not None:
            loc = tir.SrcLoc(source.path, source.kernel_ast.lineno,
                             source.kernel_ast.col_offset + 1)
        self.fn = tir.Function(source.kernel_name, [], loc)
        self.module.functions.append(self.fn)
        self._block = self.fn.body
        self.symbols: Dict[str, Union[tir.Value, ConstVal]] = {}
        self._bind_params()

    # ------------------------------------------------------------------ setup
    def _bind_params(self) -> None:
        for p in self.source.params:
            if p.is_constexpr:
                self.symbols[p.name] = ConstVal(
                    self.spec.param_constexprs.get(p.name))
            elif p.name in self.spec.pointer_types:
                pointee = self.spec.pointer_types[p.name]
                v = tir.Value(tir.Type.pointer(pointee), (),
                              tir.SrcLoc(self.source.path,
                                         self._param_line(p.name), 1),
                              name=self._fresh_name(p.name))
                self.symbols[p.name] = v
                self.fn.params += (v,)
            elif p.name in self.spec.scalar_types:
                v = tir.Value(self.spec.scalar_types[p.name], (),
                              tir.SrcLoc(self.source.path,
                                         self._param_line(p.name), 1),
                              name=self._fresh_name(p.name))
                self.symbols[p.name] = v
                self.fn.params += (v,)

    def _param_line(self, name: str) -> int:
        if self.source.kernel_ast is not None:
            for a in self.source.kernel_ast.args.args:
                if a.arg == name:
                    return a.lineno
        return 1

    def _fresh_name(self, hint: str) -> str:
        hint = hint or "v"
        name = hint
        i = 1
        while name in self._names:
            i += 1
            name = f"{hint}.{i}"
        self._names.add(name)
        return name

    def _loc(self, node: ast.AST) -> tir.SrcLoc:
        return tir.SrcLoc(self.source.path,
                          getattr(node, "lineno", 0) or 1,
                          (getattr(node, "col_offset", 0) or 0) + 1)

    def _err(self, node: ast.AST, construct: str, message: str):
        loc = self._loc(node)
        return FrontendError(self.source.path, loc.line, loc.col, construct,
                             message)

    def _emit(self, op: tir.Op, hint: str = "") -> tir.Value:
        self._block.statements.append(op)
        if op.results:
            r = op.result()
            r.name = self._fresh_name(hint or r.name)
            return r
        return None  # type: ignore[return-value]

    # ------------------------------------------------------------------ entry
    def lower(self) -> tir.Module:
        assert self.source.kernel_ast is not None
        self._lower_stmts(self.source.kernel_ast.body)
        return self.module

    # ------------------------------------------------------------------ stmts
    def _lower_stmts(self, stmts: List[ast.stmt]) -> None:
        for st in stmts:
            self._lower_stmt(st)

    def _lower_stmt(self, st: ast.stmt) -> None:
        if isinstance(st, ast.Assign):
            targets = st.targets
            if isinstance(st.value, ast.Tuple) and all(
                    isinstance(t, ast.Name) or
                    (isinstance(t, ast.Tuple)
                     and all(isinstance(e, ast.Name) for e in t.elts))
                    for t in targets):
                # tuple unpacking of a tuple expression: each element is an
                # independent value (a Python-level construct, not a tl one)
                values = [self._lower_expr(e) for e in st.value.elts]
                for t in targets:
                    names = ([t.id] if isinstance(t, ast.Name)
                             else [e.id for e in t.elts])
                    if len(names) != len(values):
                        raise self._err(
                            st, "assignment",
                            f"cannot unpack {len(values)} value(s) into "
                            f"{len(names)} target(s)")
                    for name, v in zip(names, values):
                        self._bind(name, v)
                return
            if not all(isinstance(t, ast.Name) for t in targets):
                raise self._err(
                    st, "assignment",
                    "only plain-name assignment targets are in the "
                    "elementwise core (subscript stores are not)")
            value = self._lower_expr(st.value)
            self._bind(targets[0].id, value)
            for extra in targets[1:]:
                self._bind(extra.id, value)
        elif isinstance(st, ast.AnnAssign):
            if st.value is None:
                raise self._err(st, st.target.id,
                                "annotation without a value is not a "
                                "lowerable statement")
            annotation = self._dotted(st.annotation)
            value = self._lower_expr(st.value)
            if annotation in ("tl.constexpr", "constexpr"):
                if not isinstance(value, ConstVal):
                    raise self._err(
                        st, "tl.constexpr",
                        f"'{st.target.id}' is annotated tl.constexpr but its "
                        "value is not compile-time")
            if isinstance(st.target, ast.Name):
                self._bind(st.target.id, value)
            else:
                raise self._err(st, "assignment",
                                "only plain-name annotation targets are in "
                                "the elementwise core")
        elif isinstance(st, ast.AugAssign):
            if not isinstance(st.target, ast.Name):
                raise self._err(st, "augmented assignment",
                                "only plain-name augmented assignment is in "
                                "the elementwise core")
            current = self._read_name(st.target, st)
            binop = ast.BinOp(left=st.target, op=st.op, right=st.value)
            ast.copy_location(binop, st)
            value = self._lower_binop(binop)
            self._bind(st.target.id, value)
        elif isinstance(st, ast.Expr):
            if isinstance(st.value, ast.Call):
                self._lower_call(st.value)
            elif isinstance(st.value, (ast.Name, ast.Constant)):
                pass                        # a bare name/literal: no effect
            else:
                # attribute/docstring-like or pure expression: fold check
                # only (no runtime effect is possible in the core op set)
                self.env.evaluate(st.value, self.source.path)
        elif isinstance(st, ast.If):
            cond = self.env.evaluate(st.test, self.source.path)
            if cond is not NOT_CONSTEXPR:
                taken = st.body if cond else (st.orelse or [])
                self.fold.record_branch(st, cond,
                                        "body" if cond else "orelse")
                self._lower_stmts(taken)
            else:
                raise self._err(
                    st, "if",
                    "runtime 'if' is control flow and is not lowered by the "
                    "elementwise core (only compile-time-constant conditions "
                    "fold)")
        elif isinstance(st, ast.Pass):
            pass
        elif isinstance(st, (ast.For, ast.AsyncFor, ast.While)):
            raise self._err(
                st, type(st).__name__.lower(),
                "loops are not lowered by the elementwise core")
        elif isinstance(st, ast.Return):
            raise self._err(st, "return",
                            "return is not lowered by the elementwise core")
        else:
            raise self._err(
                st, type(st).__name__,
                "statement is not in the elementwise core")

    def _bind(self, name: str, value: Union[tir.Value, ConstVal]) -> None:
        self.symbols[name] = value
        if isinstance(value, ConstVal):
            self.env.values[name] = value.value
        else:
            self.env.values[name] = _runtime_symbol(name, value)

    def _read_name(self, node: ast.AST, st: ast.AST):
        assert isinstance(node, ast.Name)
        if node.id not in self.symbols:
            raise self._err(st, node.id,
                            f"name '{node.id}' is not defined")
        return self.symbols[node.id]

    # ------------------------------------------------------------------ exprs
    def _lower_expr(self, node: ast.expr) -> Union[tir.Value, ConstVal]:
        folded = self.env.evaluate(node, self.source.path)
        if folded is not NOT_CONSTEXPR:
            return ConstVal(folded)
        if isinstance(node, ast.Constant):
            return ConstVal(node.value)
        if isinstance(node, ast.Name):
            if node.id not in self.symbols:
                raise self._err(node, node.id,
                                f"name '{node.id}' is not defined")
            return self.symbols[node.id]
        if isinstance(node, ast.BinOp):
            return self._lower_binop(node)
        if isinstance(node, ast.UnaryOp):
            return self._lower_unary(node)
        if isinstance(node, ast.Compare):
            return self._lower_compare(node)
        if isinstance(node, ast.BoolOp):
            raise self._err(
                node, f"'{type(node.op).__name__.lower()}'",
                "Python and/or on runtime values is not supported (Triton "
                "uses & and | on boolean tensors)")
        if isinstance(node, ast.IfExp):
            return self._lower_ifexp(node)
        if isinstance(node, ast.Call):
            return self._lower_call(node)
        if isinstance(node, ast.Attribute):
            raise self._err(
                node, f".{node.attr}",
                "attribute is not in the elementwise core (only compile-time "
                "dtype attributes fold)")
        if isinstance(node, ast.Subscript):
            raise self._err(
                node, "subscript",
                "subscripting (expand_dims / slicing / layout) is not "
                "lowered by the elementwise core")
        raise self._err(node, type(node).__name__,
                        "expression is not in the elementwise core")

    # -- binary operations ---------------------------------------------------
    def _lower_binop(self, node: ast.BinOp) -> Union[tir.Value, ConstVal]:
        lhs = self._lower_expr(node.left)
        rhs = self._lower_expr(node.right)
        op = node.op
        loc = self._loc(node)
        hint = "bin"

        if isinstance(op, ast.Add):
            return self._emit_addsub(lhs, rhs, loc, node, sub=False)
        if isinstance(op, ast.Sub):
            return self._emit_addsub(lhs, rhs, loc, node, sub=True)
        if isinstance(op, ast.Mult):
            l, r, t = self._binary_operands(lhs, rhs, loc)
            return self._emit(tir.Op.binop("arith.mul", l, r, loc), "mul")
        if isinstance(op, ast.Div):
            l, r, t = self._binary_operands(lhs, rhs, loc, div_or_mod=True)
            if t.is_int():
                lf = self._emit_convert(l, tir.FLOAT32, loc)
                rf = self._emit_convert(r, tir.FLOAT32, loc)
                return self._emit(tir.Op.binop("arith.fdiv", lf, rf, loc),
                                  "div")
            return self._emit(tir.Op.binop("arith.fdiv", l, r, loc), "div")
        if isinstance(op, ast.FloorDiv):
            l, r, t = self._binary_operands(lhs, rhs, loc, div_or_mod=True)
            if not t.is_int():
                raise self._err(
                    node, "//",
                    f"floordiv requires integer operands, got {t!r}")
            code = "arith.sdiv" if t.is_int_signed() else "arith.udiv"
            return self._emit(tir.Op.binop(code, l, r, loc), "fdiv")
        if isinstance(op, ast.Mod):
            l, r, t = self._binary_operands(lhs, rhs, loc, div_or_mod=True)
            if t.is_int():
                code = "arith.srem" if t.is_int_signed() else "arith.urem"
                return self._emit(tir.Op.binop(code, l, r, loc), "rem")
            return self._emit(tir.Op.binop("arith.frem", l, r, loc), "rem")
        if isinstance(op, ast.Pow):
            raise self._err(
                node, "**",
                "tensor pow is not supported by the pinned Triton 3.8 "
                "semantics (constexpr powers fold at specialization)")
        if isinstance(op, (ast.BitAnd, ast.BitOr, ast.BitXor)):
            l, r, t = self._binary_operands(lhs, rhs, loc)
            if not (t.is_int() or t.is_bool()):
                raise self._err(
                    node, type(op).__name__,
                    f"bitwise op requires integer or bool operands, got "
                    f"{t!r}")
            code = {ast.BitAnd: "bit.and", ast.BitOr: "bit.or",
                    ast.BitXor: "bit.xor"}[type(op)]
            return self._emit(tir.Op.binop(code, l, r, loc), "bit")
        if isinstance(op, ast.LShift):
            l, r, t = self._binary_operands(lhs, rhs, loc)
            if not (t.is_int() or t.is_bool()):
                raise self._err(node, "<<",
                                f"shift requires integer operands, got {t!r}")
            return self._emit(tir.Op.binop("bit.shl", l, r, loc), "shl")
        if isinstance(op, ast.RShift):
            l, r, t = self._binary_operands(lhs, rhs, loc)
            if not (t.is_int() or t.is_bool()):
                raise self._err(node, ">>",
                                f"shift requires integer operands, got {t!r}")
            code = "bit.ashr" if t.is_int_signed() else "bit.lshr"
            return self._emit(tir.Op.binop(code, l, r, loc), "shr")
        raise self._err(node, type(op).__name__,
                        "binary operator is not in the elementwise core")

    def _emit_addsub(self, lhs, rhs, loc, node, sub: bool):
        """ptr + int / int + ptr / ptr - int, else plain add/sub."""
        l_ptr = isinstance(lhs, tir.Value) and lhs.type.is_pointer()
        r_ptr = isinstance(rhs, tir.Value) and rhs.type.is_pointer()
        if l_ptr or r_ptr:
            if l_ptr and r_ptr:
                raise self._err(node, "+" if not sub else "-",
                                "cannot add pointers together")
            ptr, offset = (lhs, rhs) if l_ptr else (rhs, lhs)
            if sub and r_ptr:
                raise self._err(node, "-",
                                "cannot subtract a pointer from an integer")
            if sub:
                offset = self._negate(offset, loc)
            off_v, _ = self._as_index_value(offset, loc, node)
            return self._emit(tir.Op.ptradd(ptr, off_v, loc), "padd")
        l, r, t = self._binary_operands(lhs, rhs, loc)
        code = "arith.sub" if sub else "arith.add"
        return self._emit(tir.Op.binop(code, l, r, loc), "sub" if sub else "add")

    def _negate(self, operand: Union[tir.Value, ConstVal],
                loc) -> Union[tir.Value, ConstVal]:
        if isinstance(operand, ConstVal):
            v = operand.value
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                return ConstVal(-v)
            raise self._err(loc_node(loc), "neg",
                            f"cannot negate constexpr {v!r}")
        if operand.type.is_float():
            return self._emit(tir.Op.unary("arith.fneg", operand, loc), "neg")
        zero = self._emit(tir.Op.const(0, operand.type, loc), "zero")
        return self._emit(tir.Op.binop("arith.sub", zero, operand, loc),
                          "neg")

    def _as_index_value(self, operand, loc, node) -> Tuple[tir.Value, str]:
        """Materialize a pointer offset as i32/i64 index arithmetic."""
        if isinstance(operand, ConstVal):
            v = operand.value
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise self._err(node, "ptradd",
                                f"pointer offset must be an integer, got "
                                f"{v!r}")
            try:
                ty = ftypes.literal_type(v)
            except ftypes.TypeRuleError as exc:
                raise self._err(node, "ptradd", exc.message)
            if not ty.is_int():
                raise self._err(node, "ptradd",
                                "pointer offset must be an integer")
            return self._emit(tir.Op.const(v, ty, loc), "off"), "off"
        if not operand.type.is_int():
            raise self._err(
                node, "ptradd",
                f"pointer offset must have integer type, got "
                f"{operand.type!r}")
        if not operand.type.is_index():
            return self._emit_convert(operand, tir.INT32, loc), "off"
        return operand, "off"

    # -- unary / compare / ifexp ----------------------------------------------
    def _lower_unary(self, node: ast.UnaryOp) -> Union[tir.Value, ConstVal]:
        v = self._lower_expr(node.operand)
        loc = self._loc(node)
        if isinstance(node.op, ast.USub):
            return self._negate(v, loc)
        if isinstance(node.op, ast.UAdd):
            return v
        if isinstance(node.op, ast.Not):
            if isinstance(v, ConstVal):
                return ConstVal(not v.value)
            if not v.type.is_bool():
                raise self._err(
                    node, "not",
                    f"unary not requires a bool operand, got {v.type!r}")
            return self._emit(tir.Op.unary("logical.not", v, loc), "not")
        if isinstance(node.op, ast.Invert):
            if isinstance(v, ConstVal):
                return ConstVal(~v.value)
            if not (v.type.is_int() or v.type.is_bool()):
                raise self._err(
                    node, "~",
                    f"unary invert requires an integer operand, got "
                    f"{v.type!r}")
            return self._emit(tir.Op.unary("bit.invert", v, loc), "inv")
        raise self._err(node, type(node.op).__name__,
                        "unary operator is not in the elementwise core")

    def _lower_compare(self, node: ast.Compare) -> tir.Value:
        if len(node.ops) != 1:
            raise self._err(
                node, "comparison",
                "chained comparisons are not in the elementwise core")
        lhs = self._lower_expr(node.left)
        rhs = self._lower_expr(node.comparators[0])
        loc = self._loc(node)
        l, r, t = self._binary_operands(lhs, rhs, loc)
        pred = {ast.Lt: "cmp.lt", ast.LtE: "cmp.le", ast.Gt: "cmp.gt",
                ast.GtE: "cmp.ge", ast.Eq: "cmp.eq",
                ast.NotEq: "cmp.ne"}.get(type(node.ops[0]))
        if pred is None:
            raise self._err(node, type(node.ops[0]).__name__,
                            "comparison operator is not in the elementwise "
                            "core")
        return self._emit(tir.Op.cmp(pred, l, r, loc), "cmp")

    def _lower_ifexp(self, node: ast.IfExp) -> Union[tir.Value, ConstVal]:
        cond = self.env.evaluate(node.test, self.source.path)
        if cond is not NOT_CONSTEXPR:
            taken = node.body if cond else node.orelse
            self.fold.record_branch(node, cond,
                                    "body" if cond else "orelse")
            return self._lower_expr(taken)
        # runtime conditional expression: a select (pinned visit_IfExp)
        cond_v = self._lower_expr(node.test)
        if isinstance(cond_v, ConstVal):   # pragma: no cover - env covered
            raise self._err(node, "ifexp", "condition folded after all")
        loc = self._loc(node)
        if not cond_v.type.is_bool():
            cond_v = self._emit_convert(cond_v, tir.INT1, loc)
        x = self._lower_expr(node.body)
        y = self._lower_expr(node.orelse)
        l, r, t = self._binary_operands(x, y, loc)
        target, _, _ = fshapes.unify_pair(cond_v.shape, l.shape, loc)
        target, _, _ = fshapes.unify_pair(target, r.shape, loc)
        cond_b = self._broadcast_to(cond_v, target, loc)
        lb = self._broadcast_to(l, target, loc)
        rb = self._broadcast_to(r, target, loc)
        return self._emit(tir.Op.where(cond_b, lb, rb, loc), "sel")

    # -- the pinned unification ------------------------------------------------
    def _binary_operands(self, lhs, rhs, loc,
                         div_or_mod: bool = False) -> Tuple[tir.Value,
                                                            tir.Value,
                                                            tir.Type]:
        """Pinned binary_op_type_checking_impl: literals become constants of
        the computation type, tensor operands get explicit converts, shapes
        unify with explicit broadcast ops."""
        node = loc_node(loc)
        l_lit = isinstance(lhs, ConstVal)
        r_lit = isinstance(rhs, ConstVal)
        if l_lit and r_lit:
            # two literals (e.g. tl.where(cond, 1.0, 0.0)): the expression
            # did not fold because the *shape* comes from elsewhere; both
            # become constants of their common computation type.
            l_value, r_value = _py_scalar(lhs.value), _py_scalar(rhs.value)
            for v in (l_value, r_value):
                if isinstance(v, (DTypeValue, TypeObject)):
                    raise self._err(
                        node, "binary op",
                        "a dtype value cannot participate in arithmetic")
            try:
                l_ty = ftypes.literal_type(l_value)
                r_ty = ftypes.literal_type(r_value)
                comp = ftypes.computation_type(l_ty, True, r_ty, True,
                                               div_or_mod)
            except ftypes.TypeRuleError as exc:
                raise self._err(node, "binary op", exc.message)
            l = self._emit(tir.Op.const(l_value, comp, loc), "lit")
            r = self._emit(tir.Op.const(r_value, comp, loc), "lit")
            return self._broadcast_pair(l, r, loc)
        if l_lit or r_lit:
            lit, ten = (lhs, rhs) if l_lit else (rhs, lhs)
            lit_value = _py_scalar(lit.value)
            if isinstance(lit_value, (DTypeValue, TypeObject)):
                raise self._err(
                    node, "binary op",
                    "a dtype value cannot participate in arithmetic")
            try:
                lit_ty = ftypes.literal_type(lit_value)
            except ftypes.TypeRuleError as exc:
                raise self._err(node, "literal", exc.message)
            try:
                comp = ftypes.binop_unify(
                    lit_ty, True, lit_value,
                    ten.type, False, None, div_or_mod=div_or_mod)
            except ftypes.TypeRuleError as exc:
                raise self._err(node, "binary op", exc.message)
            lit_v = self._emit(tir.Op.const(lit_value, comp, loc), "lit")
            ten_v = self._convert_if_needed(ten, comp, loc)
            return self._broadcast_pair(lit_v, ten_v, loc)
        # both runtime values
        if lhs.type.is_pointer() or rhs.type.is_pointer():
            raise self._err(
                node, "binary op",
                "pointer operands require + or - with an integer offset")
        try:
            comp = ftypes.computation_type(lhs.type, False, rhs.type, False,
                                           div_or_mod)
        except ftypes.TypeRuleError as exc:
            raise self._err(node, "binary op", exc.message)
        l = self._convert_if_needed(lhs, comp, loc)
        r = self._convert_if_needed(rhs, comp, loc)
        return self._broadcast_pair(l, r, loc)

    def _convert_if_needed(self, value: tir.Value, target: tir.Type,
                           loc) -> tir.Value:
        if value.type == target:
            return value
        return self._emit_convert(value, target, loc)

    def _emit_convert(self, value: tir.Value, target: tir.Type,
                      loc) -> tir.Value:
        if not ftypes.convert_ok(value.type, target):
            raise self._err(
                loc_node(loc), "convert",
                f"cannot convert {value.type!r} to {target!r}")
        return self._emit(tir.Op.convert(value, target, loc), "cvt")

    def _broadcast_pair(self, l: tir.Value, r: tir.Value,
                        loc) -> Tuple[tir.Value, tir.Value, tir.Type]:
        try:
            target, l_exp, r_exp = fshapes.unify_pair(l.shape, r.shape, loc)
        except fshapes.ShapeError as exc:
            raise self._err(loc_node(loc), "broadcast", exc.message)
        return (self._broadcast_to(l, target, loc),
                self._broadcast_to(r, target, loc), l.type)

    def _broadcast_to(self, value: tir.Value, target: tir.Shape,
                      loc) -> tir.Value:
        if value.shape == target:
            return value
        # an axis that exists only by broadcasting must be materialized
        # (realize) before it can serve a *real* target extent; padded axes
        # (the value has fewer dimensions) are plain expansions
        if value.shape and len(value.shape) <= len(target):
            tail = target[len(target) - len(value.shape):]
            if any(src.broadcast and not dst.broadcast
                   for src, dst in zip(value.shape, tail)):
                value = self._emit(tir.Op.realize(value, loc), "rz")
        try:
            expanded = fshapes.broadcast_to(value.shape, target, loc)
        except fshapes.ShapeError as exc:
            raise self._err(loc_node(loc), "broadcast", exc.message)
        if expanded == value.shape:
            return value
        return self._emit(tir.Op.broadcast(value, expanded, loc), "bc")

    def _const_at(self, value, target: tir.Type, loc) -> tir.Value:
        """A constant of a *target* type: built at the literal's own type
        then converted, exactly like the pinned cast of to_tensor(value)
        (so float literals at integer pointee types convert, not reinterpret
        or silently re-type)."""
        value = _py_scalar(value)
        if isinstance(value, (DTypeValue, TypeObject)):
            raise self._err(loc_node(loc), "const",
                            "a dtype value is not a constant")
        try:
            lit_ty = ftypes.literal_type(value)
        except ftypes.TypeRuleError as exc:
            raise self._err(loc_node(loc), "literal", exc.message)
        c = self._emit(tir.Op.const(value, lit_ty, loc), "lit")
        return self._convert_if_needed(c, target, loc)

    def _materialize(self, operand: Union[tir.Value, ConstVal], loc,
                     target: Optional[tir.Type] = None) -> tir.Value:
        if isinstance(operand, ConstVal):
            v = operand.value
            ty = target or _literal_tir_type(v, self, loc)
            return self._emit(tir.Op.const(v, ty, loc), "lit")
        return operand

    # ------------------------------------------------------------------ calls
    def _lower_call(self, node: ast.Call) -> Union[tir.Value, ConstVal,
                                                   None]:
        construct = self._callee_construct(node)
        loc = self._loc(node)
        if construct is None:
            raise self._err(
                node, _callee_text(node),
                "call target is not in the elementwise core (only tl.* "
                "constructs are lowerable)")
        self._check_construct(construct, node)
        bound, provided = self._bind_call_args(construct, node)
        for required in _REQUIRED_PARAMS.get(construct, ()):
            if required not in provided:
                raise self._err(
                    node, construct,
                    f"missing required parameter {required!r}")
        handler = _CONSTRUCT_HANDLERS.get(construct)
        if handler is None:  # pragma: no cover - table completeness
            raise self._err(node, construct,
                            "no lowering handler registered")
        return handler(self, bound, node, loc)

    def _callee_construct(self, node: ast.Call) -> Optional[str]:
        func = node.func
        if isinstance(func, ast.Attribute):
            base = self._dotted(func.value)
            if base in ("tl", "triton.language"):
                return f"tl.{func.attr}"
            if base == "triton":
                return f"triton.{func.attr}"
            # method call on a value: x.to(...) maps to its construct
            return _METHOD_CONSTRUCTS.get(f".{func.attr}")
        if isinstance(func, ast.Name):
            if func.id == "constexpr":
                return "tl.constexpr"
            # pinned builtin_namespace: min/max are tl.minimum/tl.maximum
            # (constexpr uses fold before reaching here)
            return {"min": "tl.minimum", "max": "tl.maximum"}.get(func.id)
        return None

    def _dotted(self, node: ast.expr) -> Optional[str]:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            base = self._dotted(node.value)
            if base is None:
                return None
            return f"{base}.{node.attr}"
        return None

    def _check_construct(self, construct: str, node: ast.Call) -> None:
        entry = self.surface.construct(construct)
        if entry is None:
            if construct in EXCLUDED_CONSTRUCTS:
                raise self._err(node, construct,
                                EXCLUDED_CONSTRUCTS[construct])
            raise self._err(
                node, construct,
                "construct is outside the declared surface (not in the "
                "107-construct api-spec) and is refused")
        if not self.surface.is_implemented(construct):
            reason = entry.param_classifications[0].reason \
                if entry.param_classifications else "not implemented"
            raise self._err(
                node, construct,
                f"construct is declared in the surface but not implemented "
                f"by the elementwise core: {reason}")

    def _bind_call_args(self, construct: str, node: ast.Call):
        """Bind call arguments to the construct's declared parameter surface,
        consulting the classification: implemented -> bound, ignorable ->
        dropped with a record, refused -> located diagnostic.

        Returns ``(kept, provided)``: the arguments the handler may consume
        (ignorable ones dropped -- this is what makes the classification
        load-bearing) and every parameter the call provided.
        """
        entry = self.surface.construct(construct)
        assert entry is not None
        names = list(entry.parameters)
        bound: Dict[str, ast.expr] = {}
        for i, arg in enumerate(node.args):
            if i >= len(names):
                raise self._err(
                    node, construct,
                    f"too many positional arguments (declared parameters: "
                    f"{names})")
            bound[names[i]] = arg
        for kw in node.keywords:
            if kw.arg is None:
                raise self._err(node, construct,
                                "keyword arguments require a name")
            if kw.arg not in names:
                raise self._err(
                    node, construct,
                    f"unknown parameter {kw.arg!r} (declared parameters: "
                    f"{names})")
            if kw.arg in bound:
                raise self._err(node, construct,
                                f"parameter {kw.arg!r} given twice")
            bound[kw.arg] = kw.value
        kept: Dict[str, ast.expr] = {}
        for name, arg in bound.items():
            # an explicit None is the declared default: identical to absent
            if isinstance(arg, ast.Constant) and arg.value is None:
                continue
            cls = self.surface.classify_param(construct, name)
            if cls.classification == CLASS_IGNORABLE:
                self.ignored.append(IgnoredParam(construct, name,
                                                 cls.reason))
                continue
            if cls.classification == CLASS_REFUSED:
                raise self._err(node, f"{construct}({name}=...)",
                                f"parameter is refused: {cls.reason}")
            kept[name] = arg
        return kept, set(bound)

    # -- construct handlers ----------------------------------------------------
    def _lower_tl_load(self, args: Dict[str, ast.expr], node: ast.Call,
                       loc) -> tir.Value:
        ptr = self._lower_expr(args["pointer"])
        if isinstance(ptr, ConstVal):
            raise self._err(node, "tl.load",
                            "load pointer must be a pointer value")
        if not ptr.type.is_pointer():
            raise self._err(node, "tl.load",
                            f"unsupported pointer type {ptr.type!r}")
        pointee = ptr.type.pointee
        mask_v = None
        other_v = None
        default = None
        if "mask" in args:
            mask = self._lower_expr(args["mask"])
            mask_v = self._materialize(mask, loc)
            if not mask_v.type.is_bool():
                raise self._err(node, "tl.load",
                                f"mask must be boolean, got {mask_v.type!r}")
            if "other" in args:
                other = self._lower_expr(args["other"])
                if isinstance(other, ConstVal):
                    other_v = self._const_at(other.value, pointee, loc)
                else:
                    other_v = self._convert_if_needed(other, pointee, loc)
                default = tir.MaskedDefault.VALUE
            else:
                default = tir.MaskedDefault.UNDEF
        elif "other" in args:
            raise self._err(node, "tl.load",
                            "'other' cannot be provided without 'mask'")
        # pinned: a scalar pointer cannot take block mask/other
        if ptr.rank == 0:
            for v, what in ((mask_v, "mask"), (other_v, "other")):
                if v is not None and v.rank > 0:
                    raise self._err(
                        node, "tl.load",
                        f"{what} argument cannot be block type if the "
                        "pointer argument is not block")
        # broadcast mask/other to the pointer shape (explicit)
        if mask_v is not None:
            mask_v = self._broadcast_value_to(mask_v, ptr.shape, loc, node)
        if other_v is not None:
            other_v = self._broadcast_value_to(other_v, ptr.shape, loc, node)
        ptr_real = self._realize_if_needed(ptr, loc)
        return self._emit(tir.Op.load(ptr_real, mask_v, default, other_v,
                                      loc), "ld")

    def _lower_tl_store(self, args: Dict[str, ast.expr], node: ast.Call,
                        loc) -> None:
        ptr = self._lower_expr(args["pointer"])
        if isinstance(ptr, ConstVal):
            raise self._err(node, "tl.store",
                            "store pointer must be a pointer value")
        if not ptr.type.is_pointer():
            raise self._err(node, "tl.store",
                            f"unsupported pointer type {ptr.type!r}")
        pointee = ptr.type.pointee
        value = self._lower_expr(args["value"])
        if isinstance(value, ConstVal):
            value_v = self._const_at(value.value, pointee, loc)
        else:
            value_v = self._convert_if_needed(value, pointee, loc)
        mask_v = None
        if "mask" in args:
            mask = self._lower_expr(args["mask"])
            mask_v = self._materialize(mask, loc)
            if not mask_v.type.is_bool():
                raise self._err(node, "tl.store",
                                f"mask must be boolean, got {mask_v.type!r}")
        # the pointer shape is the target (pinned _broadcast_ptr_val_mask)
        for v, what in ((value_v, "value"), (mask_v, "mask")):
            if v is None:
                continue
            if _exceeds(v.shape, ptr.shape):
                raise self._err(
                    node, "tl.store",
                    f"{what} shape {list(v.shape)} exceeds the pointer "
                    f"shape {list(ptr.shape)}")
        value_v = self._broadcast_value_to(value_v, ptr.shape, loc, node)
        if mask_v is not None:
            mask_v = self._broadcast_value_to(mask_v, ptr.shape, loc, node)
        ptr_real = self._realize_if_needed(ptr, loc)
        value_real = self._realize_if_needed(value_v, loc)
        default = (tir.MaskedDefault.NO_ACCESS if mask_v is not None
                   else None)
        self._emit(tir.Op.store(ptr_real, value_real, mask_v, default, loc),
                   "st")

    def _lower_tl_arange(self, args, node, loc) -> tir.Value:
        start = self._constexpr_int(args["start"], node, "tl.arange", "start")
        end = self._constexpr_int(args["end"], node, "tl.arange", "end")
        if not (-2**31 <= start < 2**31 and -2**31 <= end < 2**31):
            raise self._err(node, "tl.arange", "arange must fit in int32")
        if end <= start:
            raise self._err(
                node, "tl.arange",
                "arange's end argument must be greater than the start "
                "argument")
        rng = end - start
        if rng & (rng - 1):
            raise self._err(node, "tl.arange",
                            "arange's range must be a power of 2")
        return self._emit(tir.Op.arange(start, end, loc), "ar")

    def _lower_tl_program_id(self, args, node, loc) -> tir.Value:
        axis = self._constexpr_int(args.get("axis"), node, "tl.program_id",
                                   "axis")
        if axis not in (0, 1, 2):
            raise self._err(node, "tl.program_id",
                            f"program_id axis must be 0, 1, or 2 but got "
                            f"{axis}")
        return self._emit(tir.Op.program_id(axis, loc), "pid")

    def _lower_tl_where(self, args, node, loc) -> tir.Value:
        cond = self._lower_expr(args["condition"])
        x = self._lower_expr(args["x"])
        y = self._lower_expr(args["y"])
        cond_v = self._materialize(cond, loc)
        if not cond_v.type.is_bool():
            # pinned: deprecated non-bool condition, cast to int1
            cond_v = self._emit_convert(cond_v, tir.INT1, loc)
        l, r, t = self._binary_operands(x, y, loc)
        target, _, _ = fshapes.unify_pair(cond_v.shape, l.shape, loc)
        target, _, _ = fshapes.unify_pair(target, r.shape, loc)
        cond_b = self._broadcast_to(cond_v, target, loc)
        lb = self._broadcast_to(l, target, loc)
        rb = self._broadcast_to(r, target, loc)
        return self._emit(tir.Op.where(cond_b, lb, rb, loc), "sel")

    def _lower_tl_zeros(self, args, node, loc) -> tir.Value:
        shape = self._constexpr_shape(args["shape"], node, "tl.zeros")
        dtype = self._constexpr_dtype(args["dtype"], node, "tl.zeros")
        return self._emit(tir.Op.zeros(tir.real_shape(shape), dtype, loc),
                          "z")

    def _lower_tl_full(self, args, node, loc) -> tir.Value:
        shape = self._constexpr_shape(args["shape"], node, "tl.full")
        dtype = self._constexpr_dtype(args["dtype"], node, "tl.full")
        value = py_scalar(self.env.evaluate(args["value"],
                                            self.source.path))
        if value is NOT_CONSTEXPR:
            raise self._err(
                node, "tl.full",
                "full with a runtime value is not in the elementwise core "
                "(the value must be compile-time)")
        return self._emit(
            tir.Op.full(tir.real_shape(shape), _const_value(value, dtype),
                        dtype, loc), "f")

    def _lower_tl_zeros_like(self, args, node, loc) -> tir.Value:
        inp = self._lower_expr(args["input"])
        if isinstance(inp, ConstVal):
            raise self._err(node, "tl.zeros_like",
                            "zeros_like requires a tensor value")
        shape = tir.real_shape([e.value for e in inp.shape])
        return self._emit(tir.Op.zeros(shape, inp.type, loc), "zl")

    def _lower_tl_constexpr(self, args, node, loc) -> ConstVal:
        value = self.env.evaluate(args["value"], self.source.path)
        if value is NOT_CONSTEXPR:
            raise self._err(
                node, "tl.constexpr",
                "tl.constexpr(...) requires a compile-time value")
        return ConstVal(value)

    def _lower_tl_multiple_of(self, args, node, loc):
        inp = self._lower_expr(args["input"])
        if "values" in args:
            values = self.env.evaluate(args["values"], self.source.path)
            if values is NOT_CONSTEXPR:
                raise self._err(node, "tl.multiple_of",
                                "values must be compile-time")
        return inp

    def _lower_tl_max_contiguous(self, args, node, loc):
        inp = self._lower_expr(args["input"])
        if "values" in args:
            values = self.env.evaluate(args["values"], self.source.path)
            if values is NOT_CONSTEXPR:
                raise self._err(node, "tl.max_contiguous",
                                "values must be compile-time")
        return inp

    # -- helpers ---------------------------------------------------------------
    def _constexpr_int(self, node: Optional[ast.expr], call: ast.Call,
                       construct: str, param: str) -> int:
        if node is None:
            raise self._err(call, construct,
                            f"missing required parameter {param!r}")
        value = py_scalar(self.env.evaluate(node, self.source.path))
        if value is NOT_CONSTEXPR or isinstance(value, bool) or \
                not isinstance(value, int):
            raise self._err(
                call, f"{construct}.{param}",
                f"{param} must be a compile-time integer")
        return value

    def _constexpr_shape(self, node: ast.expr, call: ast.Call,
                         construct: str) -> Tuple[int, ...]:
        value = py_scalar(self.env.evaluate(node, self.source.path))
        if value is NOT_CONSTEXPR or not isinstance(value, (tuple, list)):
            raise self._err(
                call, construct,
                "shape must be a compile-time sequence of integers")
        out = []
        for item in value:
            item = py_scalar(item)
            if isinstance(item, bool) or not isinstance(item, int):
                raise self._err(
                    call, construct,
                    f"shape extents must be compile-time integers, got "
                    f"{item!r}")
            out.append(item)
        return tuple(out)

    def _constexpr_dtype(self, node: ast.expr, call: ast.Call,
                         construct: str) -> tir.Type:
        value = self.env.evaluate(node, self.source.path)
        ty = None
        if isinstance(value, DTypeValue):
            ty = value.ty
        elif isinstance(value, str):
            try:
                ty = ftypes.dtype_by_name(value)
            except ftypes.TypeRuleError:
                ty = None
        if ty is None:
            raise self._err(
                call, construct,
                f"dtype must be a compile-time dtype, got {value!r}")
        return ty

    def _broadcast_value_to(self, value: tir.Value, target: tir.Shape, loc,
                            node) -> tir.Value:
        if _exceeds(value.shape, target):
            raise self._err(
                node, "broadcast",
                f"value shape {list(value.shape)} exceeds the target shape "
                f"{list(target)}")
        return self._broadcast_to(value, target, loc)

    def _realize_if_needed(self, value: tir.Value, loc) -> tir.Value:
        if tir.is_real(value.shape):
            return value
        return self._emit(tir.Op.realize(value, loc), "rz")


_CONSTRUCT_HANDLERS = {
    "tl.load": Lowering._lower_tl_load,
    "tl.store": Lowering._lower_tl_store,
    "tl.arange": Lowering._lower_tl_arange,
    "tl.program_id": Lowering._lower_tl_program_id,
    "tl.where": Lowering._lower_tl_where,
    "tl.zeros": Lowering._lower_tl_zeros,
    "tl.full": Lowering._lower_tl_full,
    "tl.zeros_like": Lowering._lower_tl_zeros_like,
    "tl.constexpr": Lowering._lower_tl_constexpr,
    "tl.multiple_of": Lowering._lower_tl_multiple_of,
    "tl.max_contiguous": Lowering._lower_tl_max_contiguous,
}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def loc_node(loc):
    """A stand-in AST node carrying a location for error reporting."""
    if isinstance(loc, tir.SrcLoc):
        node = ast.Expr(value=ast.Constant(value=None))
        node.lineno = loc.line
        node.col_offset = loc.col - 1
        return node
    return loc


def _py_scalar(value):
    return py_scalar(value)


def _callee_text(node: ast.Call) -> str:
    try:
        return ast.unparse(node.func)
    except Exception:  # pragma: no cover
        return "call"


def _runtime_symbol(name: str, value: tir.Value):
    from a100c.frontend.specialize import RuntimeValue
    return RuntimeValue(name, value.type, value.shape)


def _literal_tir_type(value, lowering, loc) -> tir.Type:
    try:
        return ftypes.literal_type(value)
    except ftypes.TypeRuleError as exc:
        raise lowering._err(loc_node(loc), "literal", exc.message)


def _const_value(value, ty: tir.Type):
    """Check a constant value is compatible with its type (bool for i1, and
    numeric for the rest)."""
    if ty.is_bool() and not isinstance(value, bool):
        raise FrontendError("<const>", 0, 0, "const",
                            f"i1 constant requires a bool, got {value!r}")
    if ty.is_int() and isinstance(value, bool):
        return int(value)
    if ty.is_float() and isinstance(value, bool):
        return float(value)
    return value


def _exceeds(shape: tir.Shape, target: tir.Shape) -> bool:
    """True when ``shape`` cannot broadcast to ``target`` (it is bigger or
    disagrees)."""
    if len(shape) > len(target):
        return True
    pad = len(target) - len(shape)
    for s, t in zip(shape, target[pad:]):
        if s.value != t.value and not s.is_one():
            return True
    return False


def lower(source: OperatorSource, spec: Specialization,
          surface: Optional[Surface] = None) -> tir.Module:
    """Lower one (source, specialization) to a verified-shape TIR module."""
    lowering = Lowering(source, spec, surface)
    return lowering.lower()
