"""AST -> TIR lowering for the elementwise core (task T006) plus the
structured control flow and grid-generality forms (task T008).

Lowered today: masked load with ``other`` / store, arithmetic, comparison,
logical/bitwise ops, ``where``, constants, ``program_id``,
``num_programs``, and the tensor-creation forms ``tl.arange`` (start/end
define the block index space), ``tl.zeros``, ``tl.full``,
``tl.zeros_like``; and the control-flow forms -- runtime ``if``/``else``
with explicit join parameters for carried values, ``for`` over
``range()``/``tl.range(...)`` (step; the pragma parameters classified
ignorable-with-reason by the declared surface), ``tl.static_range``
compile-time unrolling, ``while`` loops with a carried condition.

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

Region semantics: a source variable re-bound inside a region becomes a
*new* value at the join (never a lexical restore of its earlier binding),
and a name defined on one path only (or only inside a loop body) does not
survive the region -- the closed-region diagnostic names the construct.
Early ``return``, ``break``/``continue`` and ``for``/``while`` ``else``
are refused with located diagnostics.

Anything else -- subscripts, reductions, casts, math -- is
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


@dataclass
class TupleVal:
    """A runtime tuple value bound to one name (the inlined-function form
    ``result = (a, b)`` ... ``(x, y) = result``); it exists only to be
    unpacked, never consumed as a value."""
    values: list


@dataclass
class BlockPtrVal:
    """A block pointer under construction (T011): the frontend-side
    descriptor of ``tl.make_block_ptr`` / ``tl.advance``.

    The descriptor lives only in the lowering environment -- the TIR
    carriers are the ones the boundary semantics already own: the
    whole-tree ``ptradd`` address form, the ``mask`` operand with its
    declared disabled-position default, and the padding ``other`` value.
    ``tl.load``/``tl.store`` on a BlockPtrVal desugar into exactly those
    carriers; nothing block-pointer-specific survives into TIR (the
    semantics are the mask's, the geometry is the address tree's).

    Each term (``shape``/``strides``/``offsets`` per axis) is a
    ``tir.Value`` or a compile-time int.  Runtime terms carry across
    source loops under derived names (``name#off1``), which is what makes
    ``tl.advance`` inside a ``for`` ordinary loop-carried arithmetic.
    """

    base: tir.Value                       # the pointer parameter
    shape: list                           # per-axis extent terms
    strides: list                         # per-axis stride terms
    offsets: list                         # per-axis offset terms
    block_shape: Tuple[int, ...]          # constexpr extents
    order: Tuple[int, ...]                # constexpr memory order
    loc: object = None

    def derived_terms(self, name: str):
        """(derived-name, tir.Value) for every runtime term: the carried
        state of a block pointer reassigned inside a loop."""
        out = []
        for kind, terms in (("shape", self.shape), ("stride", self.strides),
                            ("off", self.offsets)):
            for i, t in enumerate(terms):
                if isinstance(t, tir.Value):
                    out.append((f"{name}#{kind}{i}", t))
        return out

    def substitute(self, by_vid: dict) -> "BlockPtrVal":
        """A copy with runtime terms replaced by their join values (after
        a region closes, uses of the descriptor denote the joined state)."""

        def sub(t):
            if isinstance(t, tir.Value) and t.vid in by_vid:
                return by_vid[t.vid]
            return t

        return BlockPtrVal(base=self.base,
                           shape=[sub(t) for t in self.shape],
                           strides=[sub(t) for t in self.strides],
                           offsets=[sub(t) for t in self.offsets],
                           block_shape=self.block_shape, order=self.order,
                           loc=self.loc)


@dataclass
class PointerTypeVal:
    """The value of ``tl.pointer_type(elem)`` (a cast target, not a
    dtype): the pointer-table pattern's int-to-pointer reinterpretation
    target.  ``pointee`` is the ELEMENT type (the cast builds the pointer
    type around it)."""
    pointee: tir.Type


#: method-call forms that map to declared constructs (``.to`` is ``tl.cast``)
_METHOD_CONSTRUCTS = {".to": "tl.cast"}

#: parameters each implemented construct requires
_REQUIRED_PARAMS = {
    "tl.load": ("pointer",),
    "tl.store": ("pointer", "value"),
    "tl.arange": ("start", "end"),
    "tl.program_id": (),
    "tl.num_programs": (),
    "tl.where": ("condition", "x", "y"),
    "tl.zeros": ("shape", "dtype"),
    "tl.full": ("shape", "value", "dtype"),
    "tl.zeros_like": ("input",),
    "tl.constexpr": ("value",),
    "tl.multiple_of": ("input", "values"),
    "tl.max_contiguous": ("input", "values"),
    "tl.sum": ("input",),
    "tl.max": ("input",),
    "tl.min": ("input",),
    "tl.argmax": ("input", "axis"),
    "tl.argmin": ("input", "axis"),
    "tl.xor_sum": ("input",),
    "tl.reduce_or": ("input",),
    "tl.cumsum": ("input", "axis"),
    "tl.cumprod": ("input", "axis"),
    "tl.histogram": ("input", "num_bins"),
    "tl.sort": ("x",),
    "tl.topk": ("x", "k"),
    "tl.cast": ("input", "dtype"),
    # T011: memory access breadth and atomics
    "tl.cdiv": ("x", "div"),
    "tl.make_block_ptr": ("base", "shape", "strides", "offsets",
                          "block_shape", "order"),
    "tl.advance": ("base", "offsets"),
    "tl.gather": ("src", "index"),
    "tl.interleave": ("a", "b"),
    "tl.atomic_add": ("pointer", "val"),
    "tl.atomic_max": ("pointer", "val"),
    "tl.atomic_min": ("pointer", "val"),
    "tl.atomic_xchg": ("pointer", "val"),
    "tl.atomic_and": ("pointer", "val"),
    "tl.atomic_or": ("pointer", "val"),
    "tl.atomic_xor": ("pointer", "val"),
    "tl.atomic_cas": ("pointer", "cmp", "val"),
}

#: reduction constructs -> the TIR reduce kind
_REDUCE_KINDS = {
    "tl.sum": "sum", "tl.max": "max", "tl.min": "min",
    "tl.argmax": "argmax", "tl.argmin": "argmin",
    "tl.xor_sum": "xor_sum", "tl.reduce_or": "reduce_or",
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
        self._block_stack: List[tir.Block] = [self.fn.body]
        #: names whose definition is closed inside a region (diagnostics)
        self._closed_names: Dict[str, str] = {}
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
            # a name bound to a runtime tuple unpacks later (the inlined
            # function form ``result = (a, b)`` ... ``(x, y) = result``)
            if len(targets) == 1 and isinstance(targets[0], ast.Name) \
                    and isinstance(st.value, ast.Tuple):
                values = [self._lower_expr(e) for e in st.value.elts]
                if any(isinstance(v, ConstVal) for v in values):
                    raise self._err(
                        st, "assignment",
                        "packing compile-time values into a tuple is a "
                        "Python-level construct the kernel path does not "
                        "bind")
                self.symbols[targets[0].id] = TupleVal(values)
                self.env.values[targets[0].id] = tuple(
                    _runtime_symbol(targets[0].id, v) for v in values)
                return
            if isinstance(targets[0], ast.Tuple) and len(targets) == 1 \
                    and isinstance(st.value, ast.Name) \
                    and isinstance(self.symbols.get(st.value.id), TupleVal):
                values = self.symbols[st.value.id].values
                names = [e.id for e in targets[0].elts
                         if isinstance(e, ast.Name)]
                if len(names) != len(targets[0].elts):
                    raise self._err(
                        st, "assignment",
                        "tuple-unpack targets must be plain names")
                if len(names) != len(values):
                    raise self._err(
                        st, "assignment",
                        f"cannot unpack {len(values)} value(s) into "
                        f"{len(names)} target(s)")
                for name, v in zip(names, values):
                    self._bind(name, v)
                return
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
            if isinstance(st.value, ast.Call) and len(targets) == 1 \
                    and isinstance(targets[0], ast.Tuple):
                # tuple unpacking of a multi-result call (tl.max/min with
                # return_indices=True yields (values, indices))
                names = [e.id for e in targets[0].elts
                         if isinstance(e, ast.Name)]
                if len(names) != len(targets[0].elts):
                    raise self._err(
                        st, "assignment",
                        "tuple-unpack targets must be plain names")
                values = self._lower_call_multi(st.value)
                if not isinstance(values, list):
                    raise self._err(
                        st, "assignment",
                        "the call does not produce multiple values to "
                        "unpack")
                if len(values) != len(names):
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
                self._lower_runtime_if(st)
        elif isinstance(st, ast.Pass):
            pass
        elif isinstance(st, (ast.For, ast.AsyncFor)):
            self._lower_for(st)
        elif isinstance(st, ast.While):
            self._lower_while(st)
        elif isinstance(st, ast.Return):
            raise self._err(st, "return",
                            "early return is not lowered by the control-flow "
                            "core (a region terminator is not in this path; "
                            "guarded stores and constexpr dispatch cover the "
                            "corpus forms)")
        elif isinstance(st, (ast.Break, ast.Continue)):
            raise self._err(st, type(st).__name__.lower(),
                            "break/continue are not in the structured "
                            "control-flow core")
        else:
            raise self._err(
                st, type(st).__name__,
                "statement is not in the elementwise core")

    def _bind(self, name: str, value: Union[tir.Value, ConstVal]) -> None:
        if isinstance(value, (BlockPtrVal, PointerTypeVal)):
            # a frontend-side descriptor: never a TIR value itself.  A
            # block pointer's RUNTIME terms bind under derived names
            # (``name#off0`` ...) so the loop machinery carries them like
            # any scalar; the descriptor is rebuilt from the joins after
            # the region closes.
            self.symbols[name] = value
            from a100c.frontend.specialize import NOT_CONSTEXPR as _NC
            self.env.values[name] = _NC
            if isinstance(value, BlockPtrVal):
                for dname, dval in value.derived_terms(name):
                    self._bind(dname, dval)
            return
        self.symbols[name] = value
        if isinstance(value, ConstVal):
            self.env.values[name] = value.value
        else:
            # the source name becomes a scope alias of the value, which is
            # what the TIR verifier's region joins resolve (name-based)
            value.add_alias(name)
            self.env.values[name] = _runtime_symbol(name, value)

    def _read_name(self, node: ast.AST, st: ast.AST):
        assert isinstance(node, ast.Name)
        if node.id not in self.symbols:
            closed = self._closed_names.get(node.id)
            if closed:
                raise self._err(
                    st, node.id,
                    f"name '{node.id}' was defined inside {closed} and does "
                    "not survive the region (a value defined in a region is "
                    "visible after it only through an explicit join/carried "
                    "entry)")
            raise self._err(st, node.id,
                            f"name '{node.id}' is not defined")
        return self.symbols[node.id]

    # ------------------------------------------------------------------ regions
    # Structured control flow (T008): regions lower into nested TIR blocks
    # with explicit join parameters.  A name re-bound inside a region becomes
    # a NEW value at the join (never a lexical restore of an earlier
    # binding); a name defined on one path only and used after the region is
    # rejected (the closed-region diagnostic names the construct).
    def _push_block(self, block: tir.Block) -> None:
        self._block_stack.append(block)
        self._block = block

    def _pop_block(self) -> None:
        self._block_stack.pop()
        self._block = self._block_stack[-1]

    def _region_snapshot(self) -> tuple:
        return (dict(self.symbols), dict(self.env.values))

    def _region_restore(self, snap: tuple) -> None:
        symbols, env_values = snap
        self.symbols = dict(symbols)
        self.env.values = dict(env_values)

    def _materialize_in(self, block: tir.Block, value, loc):
        """Materialize a ConstVal as a const op appended to ``block``."""
        if isinstance(value, tir.Value):
            return value
        saved = self._block
        self._block = block
        try:
            return self._materialize(value, loc)
        finally:
            self._block = saved

    @staticmethod
    def _region_desc(st: ast.stmt) -> str:
        return f"the {type(st).__name__.lower()} at line " \
               f"{getattr(st, 'lineno', 0)}"

    def _check_no_jump(self, st: ast.stmt) -> None:
        if isinstance(st, (ast.Break, ast.Continue)):
            raise self._err(st, type(st).__name__.lower(),
                            "break/continue are not in the structured "
                            "control-flow core")

    def _region_blockptr_state(self, assigned: set):
        """Extend a region's assigned-name set with the derived term names
        of the block pointers it reassigns.

        A BlockPtrVal symbol never rides a loop as a value: its runtime
        terms (bound as ``name#off<i>`` ...) are the carried state, exactly
        like any scalar the body reassigns.  Returns (extended set, the
        block-pointer names)."""
        bp_names = [n for n in sorted(assigned)
                    if isinstance(self.symbols.get(n), BlockPtrVal)]
        out = set(assigned)
        for n in bp_names:
            for dname, _v in self.symbols[n].derived_terms(n):
                if dname in self.symbols:
                    out.add(dname)
        return out, bp_names

    def _rebind_blockptrs_after_region(self, bp_names, body_syms, carried,
                                       joins) -> None:
        """After a region's joins bind, rebuild every block-pointer symbol
        from the joined terms (uses of the descriptor after the region
        denote the joined state)."""
        by_vid = {}
        for (cname, init), jv in zip(carried, joins):
            if isinstance(init, tir.Value):
                by_vid[init.vid] = jv
        for cname in bp_names:
            final = body_syms.get(cname)
            if isinstance(final, BlockPtrVal):
                self._bind(cname, final.substitute(by_vid))

    def _assigned_names(self, stmts) -> set:
        """Every name a statement list assigns, regions included -- the
        conservative pre-pass that marks carried candidates runtime before
        a loop body is lowered (a carried value recomputes each iteration;
        folding it against its initial value would be wrong)."""
        out: set = set()

        def visit(st):
            if isinstance(st, ast.Assign):
                for t in st.targets:
                    _collect(t, out)
            elif isinstance(st, (ast.AnnAssign, ast.AugAssign)):
                _collect(st.target, out)
            elif isinstance(st, ast.If):
                for s in st.body + (st.orelse or []):
                    visit(s)
            elif isinstance(st, (ast.For, ast.While)):
                _collect(st.target, out) if isinstance(st, ast.For) else None
                for s in st.body + (st.orelse or []):
                    visit(s)

        def _collect(t, out):
            if isinstance(t, ast.Name):
                out.add(t.id)
            elif isinstance(t, (ast.Tuple, ast.List)):
                for e in t.elts:
                    _collect(e, out)

        for st in stmts:
            visit(st)
        return out

    def _mark_region_runtime(self, assigned: set) -> None:
        """Names assigned in a region that currently hold constexpr values
        become runtime in the folding env (their value is re-derived inside
        the region; folding against the outer value would be wrong)."""
        from a100c.frontend.specialize import RuntimeValue
        for name in assigned:
            v = self.symbols.get(name)
            if isinstance(v, ConstVal):
                ty = None
                try:
                    if isinstance(_py_scalar(v.value), (int, float, bool)):
                        ty = ftypes.literal_type(v.value)
                except ftypes.TypeRuleError:
                    ty = None
                self.env.values[name] = RuntimeValue(name, ty, ())

    # -- runtime if ---------------------------------------------------------------
    def _lower_runtime_if(self, st: ast.If) -> None:
        loc = self._loc(st)
        cond_v = self._lower_expr(st.test)
        if isinstance(cond_v, ConstVal):
            # the arms re-bound names since the first fold attempt: re-fold
            taken = st.body if cond_v.value else (st.orelse or [])
            self.fold.record_branch(st, bool(cond_v.value),
                                    "body" if cond_v.value else "orelse")
            self._lower_stmts(taken)
            return
        if not cond_v.type.is_bool():
            cond_v = self._emit_convert(cond_v, tir.INT1, loc)
        if cond_v.shape != ():
            raise self._err(
                st, "if",
                "a block-tensor condition cannot branch (Triton branches on "
                "scalars; use tl.where for per-element selection)")
        node = tir.If(cond_v, loc)
        snap = self._region_snapshot()

        self._push_block(node.then)
        self._lower_stmts(st.body)
        then_syms = dict(self.symbols)
        self._pop_block()

        self._push_block(node.els)
        self._lower_stmts(st.orelse)
        else_syms = dict(self.symbols)
        self._pop_block()

        self._region_restore(snap)
        # joins: names an arm actually re-binds (a name bound on one path
        # only stays closed).  ConstVal sides materialize inside their arm;
        # equal constexpr bindings stay constexpr.
        outer = snap[0]
        join_names = []
        for name in sorted(set(then_syms) | set(else_syms)):
            t, e = then_syms.get(name), else_syms.get(name)
            o = outer.get(name)
            if t is None or e is None:
                self._closed_names.setdefault(name, self._region_desc(st))
                continue
            if t is o and e is o:
                continue            # not re-bound by either arm
            if isinstance(t, ConstVal) and isinstance(e, ConstVal) \
                    and _const_eq(t.value, e.value):
                self._bind(name, t)
                continue
            if isinstance(t, (BlockPtrVal, PointerTypeVal)) \
                    or isinstance(e, (BlockPtrVal, PointerTypeVal)):
                raise self._err(
                    st, "if",
                    f"the arms re-bind '{name}' as a block pointer or a "
                    "pointer type; re-binding a descriptor across a "
                    "branch is not in this slice (advance it in a loop, "
                    "or rebuild it after the branch)")
            t_v = self._materialize_in(node.then, t, loc)
            e_v = self._materialize_in(node.els, e, loc)
            if t_v.type != e_v.type:
                raise self._err(
                    st, "if",
                    f"the arms bind '{name}' with different types "
                    f"({t_v.type!r} vs {e_v.type!r}); branch unification "
                    "is not in this path")
            if tir.value_shape(t_v.shape) != tir.value_shape(e_v.shape):
                raise self._err(
                    st, "if",
                    f"the arms bind '{name}' with different extent values "
                    f"({list(t_v.shape)} vs {list(e_v.shape)})")
            join_names.append(name)
        node.join_names = tuple(join_names)
        joins = []
        for name in join_names:
            side = then_syms[name]
            jv = tir.Value(side.type, side.shape, loc, name=name)
            jv.add_alias(name)
            joins.append(jv)
        node.join_results = tuple(joins)
        self._block.statements.append(node)
        # the join results bind after the construct (fresh values: a
        # re-bound source variable never merges with its earlier binding)
        for name, value in zip(join_names, joins):
            self._bind(name, value)

    # -- for ---------------------------------------------------------------------
    def _for_form(self, st: ast.For):
        """Classify the iterator: (form, arg-exprs, pragma-kwargs) or None."""
        it = st.iter
        if not isinstance(it, ast.Call):
            return None
        func = it.func
        if isinstance(func, ast.Name) and func.id == "range":
            return "range", list(it.args), {}
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) \
                and func.value.id == "tl" and not it.keywords:
            if func.attr in ("range", "static_range"):
                return f"tl.{func.attr}", list(it.args), {}
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) \
                and func.value.id == "tl" and func.attr == "range":
            # tl.range with pragma keyword arguments
            return "tl.range", list(it.args), \
                {kw.arg: kw.value for kw in it.keywords}
        return None

    def _lower_for(self, st: ast.For) -> None:
        if isinstance(st, ast.AsyncFor):
            raise self._err(st, "asyncfor",
                            "async for is not a Triton construct")
        if st.orelse:
            raise self._err(st, "for.else",
                            "for/else is not in the structured control-flow "
                            "core")
        if not isinstance(st.target, ast.Name):
            raise self._err(st, "for",
                            "the loop target must be a plain name")
        form = self._for_form(st)
        if form is None:
            raise self._err(
                st, "for",
                "the iterator is not range()/tl.range()/tl.static_range() "
                "(iterating a value is not in the control-flow core)")
        kind, args, pragma_kwargs = form
        if kind == "tl.static_range":
            self._check_construct("tl.static_range", st.iter)
            bound, _ = self._bind_call_args("tl.static_range", st.iter)
            args = [bound.get(p) for p in ("arg1", "arg2", "step")
                    if p in bound]
            self._lower_static_range(st, args)
            return
        if kind == "tl.range":
            self._check_construct("tl.range", st.iter)
            bound, _ = self._bind_call_args("tl.range", st.iter)
            args = [bound.get(p) for p in ("arg1", "arg2", "step")
                    if p in bound]
            # the pragma parameters (num_stages, loop_unroll_factor,
            # disallow_acc_multi_buffer, flatten, warp_specialize,
            # disable_licm) are classified ignorable-with-reason by the
            # declared surface and recorded by _bind_call_args -- the
            # classification is countable in the fold record
        self._lower_counted_for(st, args, kind)

    def _lower_static_range(self, st: ast.For, args) -> None:
        """tl.static_range: compile-time unrolling (bounds are constexpr)."""
        if not 1 <= len(args) <= 3:
            raise self._err(st, "tl.static_range",
                            "static_range takes 1-3 bounds")
        vals = []
        for a in args:
            v = py_scalar(self.env.evaluate(a, self.source.path))
            if v is NOT_CONSTEXPR or isinstance(v, bool) \
                    or not isinstance(v, int):
                raise self._err(
                    st, "tl.static_range",
                    "static_range bounds must be compile-time integers "
                    "(a runtime bound needs tl.range)")
            vals.append(v)
        start = vals[0] if len(vals) > 1 else 0
        stop = vals[1] if len(vals) > 1 else vals[0]
        step = vals[2] if len(vals) > 2 else 1
        if step == 0:
            raise self._err(st, "tl.static_range", "step cannot be zero")
        name = st.target.id
        k = start
        while (step > 0 and k < stop) or (step < 0 and k > stop):
            self._bind(name, ConstVal(k))
            for s in st.body:
                self._check_no_jump(s)
                self._lower_stmt(s)
            k += step
        # the induction name after the loop: the last visited value, or the
        # start when the body never ran (unrolling is straight-line, so
        # every other name the body bound simply stays bound)
        self._bind(name, ConstVal(k - step))

    def _lower_counted_for(self, st: ast.For, args, kind: str) -> None:
        """range()/tl.range(): the counted Loop form with carried values."""
        loc = self._loc(st)
        if not 1 <= len(args) <= 3:
            raise self._err(st, kind,
                            "the range takes 1-3 bounds (start, stop, step)")
        if len(args) == 1:
            lower_expr, upper_expr, step_expr = None, args[0], None
        elif len(args) == 2:
            lower_expr, upper_expr, step_expr = args[0], args[1], None
        else:
            lower_expr, upper_expr, step_expr = args

        def bound_value(expr, what):
            if expr is None:
                return None
            v = self._lower_expr(expr)
            if isinstance(v, ConstVal):
                if isinstance(v.value, bool) or not isinstance(v.value, int):
                    raise self._err(st, kind,
                                    f"loop {what} must be an integer")
                return v
            if not v.type.is_int():
                raise self._err(st, kind,
                                f"loop {what} must have integer type, got "
                                f"{v.type!r}")
            if v.shape != ():
                raise self._err(st, kind,
                                f"loop {what} must be scalar (rank 0)")
            return v

        lower_v = bound_value(lower_expr, "lower bound")
        upper_v = bound_value(upper_expr, "upper bound")
        step_v = bound_value(step_expr, "step")
        step_const = step_v.value if isinstance(step_v, ConstVal) else 1
        if step_v is not None and isinstance(step_v, ConstVal) \
                and step_v.value <= 0:
            raise self._err(
                st, kind,
                f"step {step_v.value} is not positive; a descending range "
                "is not in the control-flow core")
        if isinstance(upper_v, ConstVal) and isinstance(lower_v, ConstVal) \
                and step_const > 0 and upper_v.value <= lower_v.value:
            # zero-trip loop: carried names keep their values; the body
            # never runs (straight-line skip, recorded in the fold)
            self.fold.record_branch(st, False, "orelse")
            return

        # the index type: i64 if any runtime bound is i64, else i32
        idx_ty = tir.INT32
        for v in (lower_v, upper_v, step_v):
            if isinstance(v, tir.Value) and v.type.width == 64:
                idx_ty = tir.INT64

        def as_index(v):
            if v is None:
                return None
            if isinstance(v, ConstVal):
                return self._emit(tir.Op.const(v.value, idx_ty, loc), "lb")
            if v.type != idx_ty:
                return self._emit_convert(v, idx_ty, loc)
            return v

        lower_i = as_index(lower_v)
        if lower_i is None:
            lower_i = self._emit(tir.Op.const(0, idx_ty, loc), "lb")
        upper_i = as_index(upper_v)
        step_i = as_index(step_v)
        if step_i is None:
            step_i = self._emit(tir.Op.const(1, idx_ty, loc), "st")

        name = st.target.id
        snap = self._region_snapshot()
        # carried candidates: names the body assigns that are visible
        # before the loop; their initial values materialize in the
        # enclosing block (the preheader) and the body sees the init value
        # -- uses of it inside the body denote the current iteration's
        # value (the loop-carried entry), never a re-materialized constant
        assigned = self._assigned_names(st.body)
        assigned, bp_names = self._region_blockptr_state(assigned)
        preheader_inits: Dict[str, tir.Value] = {}
        for cname in sorted(assigned):
            if cname == name or cname not in self.symbols:
                continue
            v = self.symbols[cname]
            if isinstance(v, BlockPtrVal):
                # the descriptor itself never rides as a value (its
                # derived term names do); the body scope's copy sees it
                # with the preheader terms, and the post-loop rebind
                # rebuilds it from the joins
                continue
            if isinstance(v, ConstVal):
                v = self._materialize_in(self._block, v, loc)
            preheader_inits[cname] = v
        node = tir.Loop(lower_i, upper_i, step_i, loc)
        self._push_block(node.body)
        self.symbols = dict(self.symbols)
        self.env.values = dict(self.env.values)
        self._bind(name, lower_i)
        for cname, init in preheader_inits.items():
            self._bind(cname, init)
        self._mark_region_runtime(assigned - {name})
        for s in st.body:
            self._check_no_jump(s)
            self._lower_stmt(s)
        if self.symbols.get(name) is not lower_i:
            raise self._err(
                st, "for",
                f"the loop body rebinds the induction name '{name}'; the "
                "induction is compiler-owned in the counted form")
        # the induction increment, appended at the body end (visible in
        # TIR; uses of the induction inside the body denote the current
        # iteration's value, the carried entry)
        inc = self._emit(tir.Op.binop("arith.add", lower_i, step_i, loc),
                         "inc")
        self._bind(name, inc)
        body_syms = dict(self.symbols)
        self._pop_block()
        self._region_restore(snap)

        carried = [(name, lower_i)]
        for cname in sorted(preheader_inits):
            outer = self.symbols.get(cname)
            if outer is None or outer is body_syms.get(cname):
                continue
            carried.append((cname, preheader_inits[cname]))
        for cname in sorted(body_syms):
            if cname in preheader_inits or cname == name:
                continue
            if self.symbols.get(cname) is None:
                self._closed_names.setdefault(cname, self._region_desc(st))
        node.carried = tuple(carried)
        self._block.statements.append(node)
        # the body's final values: materialized inside the body when the
        # body left them constexpr, then joined
        finals = []
        for cname, _ in carried:
            finals.append(self._materialize_in(node.body, body_syms[cname],
                                               loc))
        joins = []
        for (cname, _), final in zip(carried, finals):
            jv = tir.Value(final.type, final.shape, loc, name=cname)
            jv.add_alias(cname)
            joins.append(jv)
        node.join_results = tuple(joins)
        for (cname, _), value in zip(carried, joins):
            self._bind(cname, value)
        self._rebind_blockptrs_after_region(bp_names, body_syms, carried,
                                            joins)

    # -- while -------------------------------------------------------------------
    def _lower_while(self, st: ast.While) -> None:
        if st.orelse:
            raise self._err(st, "while.else",
                            "while/else is not in the structured "
                            "control-flow core")
        loc = self._loc(st)
        cond = self.env.evaluate(st.test, self.source.path)
        if cond is not NOT_CONSTEXPR:
            if cond:
                raise self._err(
                    st, "while",
                    "while True never terminates (no break exists in the "
                    "control-flow core)")
            self.fold.record_branch(st, False, "orelse")
            return                      # zero-trip: the body never runs
        cond_v = self._lower_expr(st.test)
        if isinstance(cond_v, ConstVal):
            raise self._err(st, "while", "condition folded after all")
        if not cond_v.type.is_bool():
            cond_v = self._emit_convert(cond_v, tir.INT1, loc)
        if cond_v.shape != ():
            raise self._err(
                st, "while",
                "a block-tensor condition cannot loop (Triton loops on "
                "scalars)")
        snap = self._region_snapshot()
        # carried candidates: names the body assigns that are visible
        # before the loop (the condition rides first)
        assigned = self._assigned_names(st.body)
        assigned, bp_names = self._region_blockptr_state(assigned)
        preheader_inits: Dict[str, tir.Value] = {}
        for cname in sorted(assigned):
            if cname not in self.symbols:
                continue
            v = self.symbols[cname]
            if isinstance(v, BlockPtrVal):
                continue           # the derived term names carry it
            if isinstance(v, ConstVal):
                v = self._materialize_in(self._block, v, loc)
            preheader_inits[cname] = v
        node = tir.Loop(None, None, None, loc, cond=cond_v)
        cond_name = self._fresh_name("%while.cond")
        cond_v.add_alias(cond_name)      # the carried condition entry
        self._push_block(node.body)
        self.symbols = dict(self.symbols)
        self.env.values = dict(self.env.values)
        self._bind(cond_name, cond_v)
        for cname, init in preheader_inits.items():
            self._bind(cname, init)
        self._mark_region_runtime(assigned)
        for s in st.body:
            self._check_no_jump(s)
            self._lower_stmt(s)
        # re-evaluate the condition over the body's final state; bound to
        # the carried cond name (the back edge carries it to the head)
        cond2 = self._lower_expr(st.test)
        if isinstance(cond2, ConstVal):
            cond2 = self._materialize_in(node.body, cond2, loc)
        if not cond2.type.is_bool():
            cond2 = self._emit_convert(cond2, tir.INT1, loc)
        self._bind(cond_name, cond2)
        body_syms = dict(self.symbols)
        self._pop_block()
        self._region_restore(snap)

        carried = [(cond_name, cond_v)]
        for cname in sorted(preheader_inits):
            outer = self.symbols.get(cname)
            if outer is None or outer is body_syms.get(cname):
                continue
            carried.append((cname, preheader_inits[cname]))
        for cname in sorted(body_syms):
            if cname in preheader_inits or cname == cond_name:
                continue
            if self.symbols.get(cname) is None:
                self._closed_names.setdefault(cname, self._region_desc(st))
        node.carried = tuple(carried)
        self._block.statements.append(node)
        finals = []
        for cname, _ in carried:
            finals.append(self._materialize_in(node.body, body_syms[cname],
                                               loc))
        joins = []
        for (cname, _), final in zip(carried, finals):
            jv = tir.Value(final.type, final.shape, loc, name=cname)
            jv.add_alias(cname)
            joins.append(jv)
        node.join_results = tuple(joins)
        for (cname, _), value in zip(carried, joins):
            if cname == cond_name:
                continue            # internal: not visible after the loop
            self._bind(cname, value)
        self._rebind_blockptrs_after_region(bp_names, body_syms, carried,
                                            joins)

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
            l, r, t = self._binary_operands(lhs, rhs, loc, div_or_mod=True,
                                            preserve_order=True)
            if t.is_int():
                lf = self._emit_convert(l, tir.FLOAT32, loc)
                rf = self._emit_convert(r, tir.FLOAT32, loc)
                return self._emit(tir.Op.binop("arith.fdiv", lf, rf, loc),
                                  "div")
            return self._emit(tir.Op.binop("arith.fdiv", l, r, loc), "div")
        if isinstance(op, ast.FloorDiv):
            l, r, t = self._binary_operands(lhs, rhs, loc, div_or_mod=True,
                                            preserve_order=True)
            if not t.is_int():
                raise self._err(
                    node, "//",
                    f"floordiv requires integer operands, got {t!r}")
            code = "arith.sdiv" if t.is_int_signed() else "arith.udiv"
            return self._emit(tir.Op.binop(code, l, r, loc), "fdiv")
        if isinstance(op, ast.Mod):
            l, r, t = self._binary_operands(lhs, rhs, loc, div_or_mod=True,
                                            preserve_order=True)
            if t.is_int():
                # the non-negative power-of-two remainder folds to a mask:
                # i % 2^k == i & (2^k - 1) exactly when i is provably
                # non-negative (the arange-derived forms; every other
                # shape keeps the declared remainder op)
                if isinstance(rhs, ConstVal):
                    rv = _py_scalar(rhs.value)
                    if isinstance(rv, int) and not isinstance(rv, bool) \
                            and rv > 0 and rv & (rv - 1) == 0 \
                            and self._nonnegative_arange(lhs):
                        k = self._emit(tir.Op.const(rv - 1, t, loc), "msk")
                        return self._emit(
                            tir.Op.binop("bit.and", l,
                                         self._broadcast_to(k, l.shape, loc),
                                         loc), "mod")
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
        if isinstance(op, (ast.LShift, ast.RShift)):
            # shifts are NOT commutative: the literal normalization must
            # not move the amount to the value's side (preserve_order)
            l, r, t = self._binary_operands(lhs, rhs, loc,
                                            preserve_order=True)
            if not (t.is_int() or t.is_bool()):
                raise self._err(node, "<<" if isinstance(op, ast.LShift)
                                else ">>",
                                f"shift requires integer operands, got {t!r}")
            if isinstance(op, ast.LShift):
                return self._emit(tir.Op.binop("bit.shl", l, r, loc), "shl")
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
        l, r, t = self._binary_operands(lhs, rhs, loc, preserve_order=True)
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
        if operand.shape != ():
            # a block operand needs the zero broadcast to its shape (the
            # binop verifier requires equal extents)
            zero = self._broadcast_to(zero, operand.shape, loc)
        return self._emit(tir.Op.binop("arith.sub", zero, operand, loc),
                          "neg")

    def _nonnegative_arange(self, operand) -> bool:
        """Is the operand provably an arange-derived non-negative value?

        The guard of the power-of-two remainder fold: the arange construct
        itself guarantees ``start >= 0`` lanes; a hint wrapper is
        transparent.  Every other form declines (the fold never applies to
        a value it cannot prove non-negative)."""
        node = operand
        seen = 0
        while isinstance(node, tir.Value) and node.producer is not None \
                and seen < 16:
            seen += 1
            prod = node.producer
            if prod.op == "hint":
                node = prod.operands[0]
                continue
            if prod.op == "arange":
                return prod.attrs["start"] >= 0
            return False
        return False

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
        l, r, t = self._binary_operands(lhs, rhs, loc, preserve_order=True)
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
        l, r, t = self._binary_operands(x, y, loc, preserve_order=True)
        target, _, _ = fshapes.unify_pair(cond_v.shape, l.shape, loc)
        target, _, _ = fshapes.unify_pair(target, r.shape, loc)
        cond_b = self._broadcast_to(cond_v, target, loc)
        lb = self._broadcast_to(l, target, loc)
        rb = self._broadcast_to(r, target, loc)
        return self._emit(tir.Op.where(cond_b, lb, rb, loc), "sel")

    # -- the pinned unification ------------------------------------------------
    def _binary_operands(self, lhs, rhs, loc,
                         div_or_mod: bool = False,
                         preserve_order: bool = False) -> Tuple[tir.Value,
                                                            tir.Value,
                                                            tir.Type]:
        """Pinned binary_op_type_checking_impl: literals become constants of
        the computation type, tensor operands get explicit converts, shapes
        unify with explicit broadcast ops.

        ``preserve_order`` keeps the source operand order (a comparison's
        predicate is not commutative: ``flag > 0`` must compare flag
        against the literal, never the literal against flag)."""
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
            if preserve_order and not l_lit:
                return self._broadcast_pair(ten_v, lit_v, loc)
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
    def _lower_call_multi(self, node: ast.Call) -> Union[List[tir.Value],
                                                         None]:
        """Lower a call that may produce multiple values (the reduction
        index forms with return_indices=True); None when the call is
        single-result (the caller falls back to the plain path)."""
        construct = self._callee_construct(node)
        if construct not in ("tl.max", "tl.min"):
            return None
        bound, provided = self._bind_call_args(construct, node)
        if "return_indices" not in bound:
            return None
        flag = self.env.evaluate(bound["return_indices"], self.source.path)
        if flag is NOT_CONSTEXPR or not flag:
            return None
        self._check_construct(construct, node)
        for required in _REQUIRED_PARAMS.get(construct, ()):
            if required not in provided:
                raise self._err(
                    node, construct,
                    f"missing required parameter {required!r}")
        values = self._lower_tl_maxmin(bound, node, self._loc(node),
                                       construct, want_indices=True)
        assert isinstance(values, list)
        return values

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
        receiver = self._method_receiver(node)
        bound, provided = self._bind_call_args(construct, node,
                                               method_receiver=receiver)
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

    def _method_receiver(self, node: ast.Call) -> Optional[ast.expr]:
        """A value-method call's receiver (``x`` in ``x.to(dtype)``): None
        for plain tl.* / triton.* calls."""
        func = node.func
        if not isinstance(func, ast.Attribute):
            return None
        base = self._dotted(func.value)
        if base in ("tl", "triton.language", "triton"):
            return None
        return func.value

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

    def _bind_call_args(self, construct: str, node: ast.Call,
                        method_receiver: Optional[ast.expr] = None):
        """Bind call arguments to the construct's declared parameter surface,
        consulting the classification: implemented -> bound, ignorable ->
        dropped with a record, refused -> located diagnostic.

        ``method_receiver``: a value-method call (``x.to(dtype)``) binds
        its receiver as the construct's first parameter, and the call's
        own positional arguments start at the second.

        Returns ``(kept, provided)``: the arguments the handler may consume
        (ignorable ones dropped -- this is what makes the classification
        load-bearing) and every parameter the call provided.
        """
        entry = self.surface.construct(construct)
        assert entry is not None
        names = list(entry.parameters)
        bound: Dict[str, ast.expr] = {}
        if method_receiver is not None:
            if not names:
                raise self._err(
                    node, construct,
                    "the construct takes no value receiver")
            bound[names[0]] = method_receiver
            names = names[1:]
        for i, arg in enumerate(node.args):
            if i >= len(names):
                raise self._err(
                    node, construct,
                    f"too many positional arguments (declared parameters: "
                    f"{list(entry.parameters)})")
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
        if isinstance(ptr, BlockPtrVal):
            return self._load_blockptr(ptr, args, node, loc)
        if isinstance(ptr, PointerTypeVal):
            raise self._err(node, "tl.load",
                            "load pointer must be a pointer value, not a "
                            "pointer type")
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
        if "boundary_check" in args:
            raise self._err(node, "tl.load",
                            "boundary_check applies to a block pointer "
                            "(tl.make_block_ptr's result)")
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
        volatile = False
        if "volatile" in args:
            v = self.env.evaluate(args["volatile"], self.source.path)
            if v is NOT_CONSTEXPR or not isinstance(v, bool):
                raise self._err(node, "tl.load",
                                "volatile must be a compile-time boolean")
            volatile = v
        return self._emit(tir.Op.load(ptr_real, mask_v, default, other_v,
                                      loc, volatile=volatile), "ld")

    def _boundary_axes(self, args, node, loc):
        """The boundary_check tuple: a compile-time sequence of axes."""
        if "boundary_check" not in args:
            return ()
        v = self.env.evaluate(args["boundary_check"], self.source.path)
        if v is NOT_CONSTEXPR:
            raise self._err(node, "tl.load/tl.store",
                            "boundary_check must be a compile-time tuple "
                            "of axes")
        if isinstance(v, (tuple, list)):
            return tuple(int(x) for x in v)
        if isinstance(v, int) and not isinstance(v, bool):
            return (int(v),)
        raise self._err(node, "tl.load/tl.store",
                        f"boundary_check must be a tuple of axes, got "
                        f"{v!r}")

    def _load_blockptr(self, bp: BlockPtrVal, args, node, loc) -> tir.Value:
        """tl.load on a block pointer: the desugaring (whole-tree ptradd
        address + boundary mask + padding ``other``)."""
        boundary = self._boundary_axes(args, node, loc)
        padding = "zero"
        if "padding_option" in args:
            v = self.env.evaluate(args["padding_option"], self.source.path)
            if v is NOT_CONSTEXPR or v != "zero":
                raise self._err(node, "tl.load",
                                f"padding_option {v!r} is not declared "
                                "(the pinned Triton 3.8 form is 'zero')")
            padding = v
        ptr, masks = self._blockptr_desugar(bp, boundary, node, loc)
        pointee = ptr.type.pointee
        mask_v = None
        other_v = None
        default = None
        if masks is not None:
            mask_v = self._broadcast_value_to(masks, ptr.shape, loc, node)
            default = tir.MaskedDefault.UNDEF
            if boundary:
                # padding_option 'zero': the declared disabled-position
                # value (the load itself performs no access there)
                other_v = self._broadcast_value_to(
                    self._const_at(0, pointee, loc), ptr.shape, loc, node)
                default = tir.MaskedDefault.VALUE
        elif boundary:
            raise self._err(node, "tl.load",
                            "boundary_check produced no mask (an internal "
                            "desugaring inconsistency)")
        volatile = False
        if "volatile" in args:
            v = self.env.evaluate(args["volatile"], self.source.path)
            if v is NOT_CONSTEXPR or not isinstance(v, bool):
                raise self._err(node, "tl.load",
                                "volatile must be a compile-time boolean")
            volatile = v
        ptr_real = self._realize_if_needed(ptr, loc)
        return self._emit(tir.Op.load(ptr_real, mask_v, default, other_v,
                                      loc, volatile=volatile), "ld")

    def _lower_tl_store(self, args: Dict[str, ast.expr], node: ast.Call,
                       loc) -> None:
        ptr = self._lower_expr(args["pointer"])
        blockptr = None
        if isinstance(ptr, BlockPtrVal):
            blockptr = ptr
        elif isinstance(ptr, PointerTypeVal):
            raise self._err(node, "tl.store",
                            "store pointer must be a pointer value, not a "
                            "pointer type")
        elif isinstance(ptr, ConstVal):
            raise self._err(node, "tl.store",
                            "store pointer must be a pointer value")
        elif not ptr.type.is_pointer():
            raise self._err(node, "tl.store",
                            f"unsupported pointer type {ptr.type!r}")
        if blockptr is not None:
            boundary = self._boundary_axes(args, node, loc)
            ptr, masks = self._blockptr_desugar(blockptr, boundary, node,
                                                loc)
            if "mask" in args:
                raise self._err(node, "tl.store",
                                "a block-pointer store takes no separate "
                                "mask (boundary_check is the mask)")
            mask_v = self._broadcast_value_to(masks, ptr.shape, loc,
                                               node) if masks is not None \
                else None
        else:
            if "boundary_check" in args:
                raise self._err(node, "tl.store",
                                "boundary_check applies to a block pointer "
                                "(tl.make_block_ptr's result)")
            mask_v = None
            if "mask" in args:
                mask = self._lower_expr(args["mask"])
                mask_v = self._materialize(mask, loc)
                if not mask_v.type.is_bool():
                    raise self._err(node, "tl.store",
                                    f"mask must be boolean, got "
                                    f"{mask_v.type!r}")
        pointee = ptr.type.pointee
        value = self._lower_expr(args["value"])
        if isinstance(value, ConstVal):
            value_v = self._const_at(value.value, pointee, loc)
        else:
            value_v = self._convert_if_needed(value, pointee, loc)
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

    def _lower_tl_num_programs(self, args, node, loc) -> tir.Value:
        axis = self._constexpr_int(args.get("axis"), node, "tl.num_programs",
                                   "axis")
        if axis not in (0, 1, 2):
            raise self._err(node, "tl.num_programs",
                            f"num_programs axis must be 0, 1, or 2 but got "
                            f"{axis}")
        return self._emit(tir.Op.num_programs(axis, loc), "np")

    def _lower_tl_where(self, args, node, loc) -> tir.Value:
        cond = self._lower_expr(args["condition"])
        x = self._lower_expr(args["x"])
        y = self._lower_expr(args["y"])
        cond_v = self._materialize(cond, loc)
        if not cond_v.type.is_bool():
            # pinned: deprecated non-bool condition, cast to int1
            cond_v = self._emit_convert(cond_v, tir.INT1, loc)
        l, r, t = self._binary_operands(x, y, loc, preserve_order=True)
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
        """tl.multiple_of: the divisibility promise recorded on the value
        (the TIR ``hint`` op carries it; the wide-access proof consumes
        it, and ignoring it is always safe)."""
        inp = self._lower_expr(args["input"])
        if "values" in args:
            values = self.env.evaluate(args["values"], self.source.path)
            if values is NOT_CONSTEXPR:
                raise self._err(node, "tl.multiple_of",
                                "values must be compile-time")
            return self._record_hint(inp, node, loc,
                                     multiple_of=values)
        return inp

    def _lower_tl_max_contiguous(self, args, node, loc):
        """tl.max_contiguous: the contiguity promise recorded on the value
        (the TIR ``hint`` op carries it; the wide-access proof consumes
        it, and ignoring it is always safe)."""
        inp = self._lower_expr(args["input"])
        if "values" in args:
            values = self.env.evaluate(args["values"], self.source.path)
            if values is NOT_CONSTEXPR:
                raise self._err(node, "tl.max_contiguous",
                                "values must be compile-time")
            return self._record_hint(inp, node, loc,
                                     max_contiguous=values)
        return inp

    def _record_hint(self, inp, node, loc, multiple_of=None,
                     max_contiguous=None):
        """Wrap a value with a recorded promise (the hint op is an
        identity: it preserves type and shape and never converts)."""
        if not isinstance(inp, tir.Value):
            raise self._err(
                node, "tl.multiple_of/tl.max_contiguous",
                "a hint attaches to a runtime value (a compile-time value "
                "needs no promise)")
        for v in (multiple_of, max_contiguous):
            if v is not None and (isinstance(v, bool)
                                  or not isinstance(v, int) or v < 1):
                raise self._err(
                    node, "tl.multiple_of/tl.max_contiguous",
                    f"hint values must be positive integers, got {v!r}")
        return self._emit(tir.Op.hint(inp, multiple_of, max_contiguous, loc),
                          "hnt")

    # -- T011: cdiv, block pointers, atomics, gather, interleave -------------

    def _lower_tl_cdiv(self, args, node, loc):
        """tl.cdiv: the pinned ``(x + div - 1) // div`` desugar (integer
        ``//`` is the truncating sdiv/udiv of the pinned rules; both
        constexpr operands fold)."""
        x = self._lower_expr(args["x"])
        div = self._lower_expr(args["div"])
        if isinstance(x, ConstVal) and isinstance(div, ConstVal):
            xv, dv = _py_scalar(x.value), _py_scalar(div.value)
            if isinstance(xv, int) and isinstance(dv, int) \
                    and not isinstance(xv, bool) \
                    and not isinstance(dv, bool) and dv != 0:
                t = xv + dv - 1
                q = abs(t) // abs(dv)
                if (t < 0) != (dv < 0):
                    q = -q
                return ConstVal(q)
        if isinstance(div, ConstVal):
            dv = _py_scalar(div.value)
            if not isinstance(dv, int) or isinstance(dv, bool) or dv == 0:
                raise self._err(node, "tl.cdiv",
                                f"divisor must be a non-zero integer, got "
                                f"{dv!r}")
            dec = ConstVal(dv - 1)
        else:
            one = self._emit(tir.Op.const(1, tir.INT32, loc), "one")
            l, r, _t = self._binary_operands(div, one, loc)
            dec = self._emit(tir.Op.binop("arith.sub", l, r, loc), "sub")
        l, r, _t = self._binary_operands(x, dec, loc)
        num = self._emit(tir.Op.binop("arith.add", l, r, loc), "add")
        if isinstance(div, ConstVal):
            dv = _py_scalar(div.value)
            l, r, t = self._binary_operands(num, div, loc, div_or_mod=True,
                                            preserve_order=True)
        else:
            l, r, t = self._binary_operands(num, div, loc, div_or_mod=True,
                                            preserve_order=True)
        if not t.is_int():
            raise self._err(node, "tl.cdiv",
                            f"cdiv requires integer operands, got {t!r}")
        code = "arith.sdiv" if t.is_int_signed() else "arith.udiv"
        return self._emit(tir.Op.binop(code, l, r, loc), "cdiv")

    def _lower_make_block_ptr(self, args, node, loc) -> BlockPtrVal:
        base = self._lower_expr(args["base"])
        if isinstance(base, ConstVal) or not isinstance(base, tir.Value) \
                or not base.type.is_pointer():
            raise self._err(node, "tl.make_block_ptr",
                            "base must be a pointer value")
        shape_node = args["shape"]
        strides_node = args["strides"]
        offsets_node = args["offsets"]
        block_node = args["block_shape"]
        order_node = args.get("order")

        def terms(expr, what):
            vals = self.env.evaluate(expr, self.source.path) \
                if expr is not None else NOT_CONSTEXPR
            if vals is not NOT_CONSTEXPR:
                if isinstance(vals, (tuple, list)) and all(
                        isinstance(v, int) and not isinstance(v, bool)
                        for v in vals):
                    return [ConstVal(int(v)) for v in vals]
                # a tuple holding runtime symbols falls through to the
                # per-element AST path below
            if isinstance(expr, ast.Tuple):
                # a runtime tuple expression: each element lowers on its
                # own (the whole tuple never becomes one TIR value)
                return [self._lower_expr(e) for e in expr.elts]
            lowered = self._lower_expr(expr)
            if isinstance(lowered, TupleVal):
                return list(lowered.values)
            if isinstance(lowered, ConstVal) \
                    and isinstance(lowered.value, (tuple, list)):
                return [ConstVal(int(v)) for v in lowered.value]
            raise self._err(node, "tl.make_block_ptr",
                            f"{what} must be a compile-time tuple or a "
                            "runtime tuple expression")

        shape = terms(shape_node, "shape")
        strides = terms(strides_node, "strides")
        offsets = terms(offsets_node, "offsets")
        block_vals = self.env.evaluate(block_node, self.source.path)
        if block_vals is NOT_CONSTEXPR \
                or not isinstance(block_vals, (tuple, list)):
            raise self._err(node, "tl.make_block_ptr",
                            "block_shape must be a compile-time tuple")
        block_shape = tuple(int(v) for v in block_vals)
        if order_node is None:
            order = tuple(range(len(block_shape) - 1, -1, -1))
        else:
            ov = self.env.evaluate(order_node, self.source.path)
            if ov is NOT_CONSTEXPR or not isinstance(ov, (tuple, list)):
                raise self._err(node, "tl.make_block_ptr",
                                "order must be a compile-time tuple")
            order = tuple(int(v) for v in ov)
        rank = len(block_shape)
        if not (len(shape) == len(strides) == len(offsets) == rank):
            raise self._err(node, "tl.make_block_ptr",
                            f"shape/strides/offsets/block_shape ranks "
                            f"disagree ({len(shape)}/{len(strides)}/"
                            f"{len(offsets)}/{rank})")
        if sorted(order) != list(range(rank)):
            raise self._err(node, "tl.make_block_ptr",
                            f"order {order} is not a permutation of the "
                            "axes")
        for v in block_shape:
            if v < 1:
                raise self._err(node, "tl.make_block_ptr",
                                "block_shape extents must be positive")
        return BlockPtrVal(base=base, shape=shape, strides=strides,
                           offsets=offsets, block_shape=block_shape,
                           order=order, loc=loc)

    def _lower_advance(self, args, node, loc) -> BlockPtrVal:
        bp = self._lower_expr(args["base"])
        if not isinstance(bp, BlockPtrVal):
            raise self._err(node, "tl.advance",
                            "advance applies to a block pointer "
                            "(tl.make_block_ptr's result)")
        offs = self.env.evaluate(args["offsets"], self.source.path)
        if offs is not NOT_CONSTEXPR:
            if not isinstance(offs, (tuple, list)):
                raise self._err(node, "tl.advance",
                                "offsets must be a tuple")
            deltas = [ConstVal(int(v)) for v in offs]
        else:
            expr = args["offsets"]
            if isinstance(expr, ast.Tuple):
                deltas = [self._lower_expr(e) for e in expr.elts]
            else:
                lowered = self._lower_expr(expr)
                if isinstance(lowered, TupleVal):
                    deltas = list(lowered.values)
                else:
                    raise self._err(node, "tl.advance",
                                    "offsets must be a compile-time tuple "
                                    "or a runtime tuple expression")
        if len(deltas) != len(bp.offsets):
            raise self._err(node, "tl.advance",
                            f"offsets rank {len(deltas)} does not match the "
                            f"block pointer's {len(bp.offsets)}")
        new_offsets = []
        for old, delta in zip(bp.offsets, deltas):
            if isinstance(old, ConstVal) and isinstance(delta, ConstVal):
                new_offsets.append(ConstVal(old.value + delta.value))
                continue
            l, r, _t = self._binary_operands(old, delta, loc)
            new_offsets.append(self._emit(
                tir.Op.binop("arith.add", l, r, loc), "adv"))
        return BlockPtrVal(base=bp.base, shape=list(bp.shape),
                           strides=list(bp.strides), offsets=new_offsets,
                           block_shape=bp.block_shape, order=bp.order,
                           loc=loc)

    # -- the block-pointer desugaring ----------------------------------------

    def _bp_arange(self, extent: int, loc):
        """The (shared) arange of one block extent: every block-pointer
        access of the same extent reuses ONE arange op (the kernel keeps
        a single index space -- the one-arange form the slice lowers)."""
        cache = getattr(self, "_bp_aranges", None)
        if cache is None:
            cache = self._bp_aranges = {}
        if extent not in cache:
            cache[extent] = self._emit(tir.Op.arange(0, extent, loc), "bpr")
        return cache[extent]

    def _bp_scalar(self, term, loc):
        """Materialize one descriptor term as a scalar TIR value."""
        if isinstance(term, ConstVal):
            v = _py_scalar(term.value)
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise self._err(loc_node(loc), "tl.make_block_ptr",
                                f"a block-pointer term must be an integer, "
                                f"got {v!r}")
            try:
                ty = ftypes.literal_type(v)
            except ftypes.TypeRuleError as exc:
                raise self._err(loc_node(loc), "literal", exc.message)
            return self._emit(tir.Op.const(v, ty, loc), "bpt")
        return term

    def _bp_term_add(self, a, b, loc):
        if isinstance(a, ConstVal) and isinstance(b, ConstVal):
            return ConstVal(_py_scalar(a.value) + _py_scalar(b.value))
        l, r, _t = self._binary_operands(a, b, loc)
        return self._emit(tir.Op.binop("arith.add", l, r, loc), "bpa")

    def _bp_term_mul(self, a, b, loc):
        if isinstance(a, ConstVal) and isinstance(b, ConstVal):
            av, bv = _py_scalar(a.value), _py_scalar(b.value)
            if isinstance(av, int) and isinstance(bv, int) \
                    and not isinstance(av, bool) \
                    and not isinstance(bv, bool):
                return ConstVal(av * bv)
        if isinstance(b, ConstVal) and _py_scalar(b.value) == 1:
            return a
        if isinstance(a, ConstVal) and _py_scalar(a.value) == 1:
            return b
        l, r, _t = self._binary_operands(a, b, loc)
        return self._emit(tir.Op.binop("arith.mul", l, r, loc), "bpm")

    def _bp_term_cmp_lt(self, a, b, loc):
        l, r, _t = self._binary_operands(a, b, loc, preserve_order=True)
        return self._emit(tir.Op.cmp("cmp.lt", l, r, loc), "bpc")

    def _bp_term_and(self, a, b, loc):
        if a is None:
            return b
        if b is None:
            return a
        l, r, _t = self._binary_operands(a, b, loc)
        return self._emit(tir.Op.binop("bit.and", l, r, loc), "bpi")

    def _blockptr_desugar(self, bp: BlockPtrVal, boundary, node, loc):
        """One block pointer + boundary_check -> (ptr, mask, axes_ok).

        The geometry desugars into the whole-tree ptradd address form;
        the boundary semantics into the mask operand (the declared
        disabled-position default; padding 'zero' supplies ``other`` at
        the load).  Axes with block extent 1 fold into scalar offset
        terms; one remaining axis is the plain 1-D arange form; two
        remaining axes flatten row-major (fast axis last, per ``order``)
        with the row index recovered as ``flat >> log2(extent_fast)``
        and the column as ``flat & (extent_fast - 1)`` -- exact for the
        non-negative arange (the power-of-2 block extents the arange
        construct itself requires).
        """
        rank = len(bp.block_shape)
        for ax in boundary:
            if not isinstance(ax, int) or isinstance(ax, bool) \
                    or not 0 <= ax < rank:
                raise self._err(node, "tl.load/tl.store",
                                f"boundary_check axis {ax!r} outside the "
                                f"block pointer's rank {rank}")
        big = [ax for ax in range(rank) if bp.block_shape[ax] != 1]
        # the folded scalar terms: extent-1 axes contribute off*stride
        folded = ConstVal(0)
        for ax in range(rank):
            if bp.block_shape[ax] != 1:
                continue
            folded = self._bp_term_add(
                folded, self._bp_term_mul(bp.offsets[ax], bp.strides[ax],
                                          loc), loc)
        masks = None
        for ax in boundary:
            if bp.block_shape[ax] == 1:
                # a folded axis's condition is scalar; it broadcasts into
                # the block mask below
                cond = self._bp_term_cmp_lt(bp.offsets[ax], bp.shape[ax],
                                            loc)
                masks = self._bp_term_and(masks, cond, loc)
        if not big:
            raise self._err(node, "tl.load/tl.store",
                            "a block pointer whose every block extent is 1 "
                            "is a scalar access; the masked scalar path is "
                            "not in this slice (a located refusal)")
        if len(big) == 1:
            ax = big[0]
            n = bp.block_shape[ax]
            if n & (n - 1):
                raise self._err(node, "tl.load/tl.store",
                                f"block extent {n} is not a power of two "
                                "(the arange construct requires one)")
            i = self._bp_arange(n, loc)
            idx = self._bp_term_add(bp.offsets[ax], i, loc)
            offset = self._bp_term_mul(idx, bp.strides[ax], loc)
            offset = self._bp_term_add(offset, folded, loc)
            if ax in boundary:
                cond = self._bp_term_cmp_lt(
                    self._bp_term_add(bp.offsets[ax], i, loc),
                    bp.shape[ax], loc)
                masks = self._bp_term_and(masks, cond, loc)
        elif len(big) == 2:
            fast = bp.order[-1]
            slow = bp.order[-2]
            if {fast, slow} != set(big):
                raise self._err(node, "tl.load/tl.store",
                                f"the memory order {bp.order} does not "
                                "place the two non-unit axes last")
            bf, bs = bp.block_shape[fast], bp.block_shape[slow]
            if bf & (bf - 1) or (bf * bs) & (bf * bs - 1):
                raise self._err(node, "tl.load/tl.store",
                                f"block extents ({bs}, {bf}) must be "
                                "powers of two (the flattened arange and "
                                "the shift/mask index recovery require "
                                "them)")
            flat = self._bp_arange(bf * bs, loc)
            k = bf.bit_length() - 1
            row = self._emit(tir.Op.binop(
                "bit.lshr", flat,
                self._broadcast_to(
                    self._emit(tir.Op.const(k, tir.INT32, loc), "bpk"),
                    flat.shape, loc), loc), "bpr")
            col = self._emit(tir.Op.binop(
                "bit.and", flat,
                self._broadcast_to(
                    self._emit(tir.Op.const(bf - 1, tir.INT32, loc), "bpm"),
                    flat.shape, loc), loc), "bpc")
            row_idx = self._bp_term_add(bp.offsets[slow], row, loc)
            col_idx = self._bp_term_add(bp.offsets[fast], col, loc)
            offset = self._bp_term_add(
                self._bp_term_mul(row_idx, bp.strides[slow], loc),
                self._bp_term_mul(col_idx, bp.strides[fast], loc), loc)
            offset = self._bp_term_add(offset, folded, loc)
            if slow in boundary:
                cond = self._bp_term_cmp_lt(row_idx, bp.shape[slow], loc)
                masks = self._bp_term_and(masks, cond, loc)
            if fast in boundary:
                cond = self._bp_term_cmp_lt(col_idx, bp.shape[fast], loc)
                masks = self._bp_term_and(masks, cond, loc)
        else:
            raise self._err(node, "tl.load/tl.store",
                            "a block pointer with three or more non-unit "
                            "axes is not in this slice (the layout lane "
                            "owns multi-axis blocks)")
        ptr = self._emit(tir.Op.ptradd(bp.base,
                                       self._bp_scalar(offset, loc), loc),
                         "bpp")
        return ptr, masks

    # -- atomics ---------------------------------------------------------------

    def _atomic_sem_scope(self, args, node, loc):
        sem = "acq_rel"
        if "sem" in args:
            v = self.env.evaluate(args["sem"], self.source.path)
            if v is NOT_CONSTEXPR or not isinstance(v, str) \
                    or v not in ("relaxed", "acquire", "release", "acq_rel"):
                raise self._err(node, "tl.atomic",
                                f"sem must be one of relaxed/acquire/"
                                f"release/acq_rel, got {v!r}")
            sem = v
        scope = "gpu"
        if "scope" in args:
            v = self.env.evaluate(args["scope"], self.source.path)
            if v is NOT_CONSTEXPR or not isinstance(v, str) \
                    or v not in ("gpu", "sys", "cta"):
                raise self._err(node, "tl.atomic",
                                f"scope must be one of gpu/sys/cta, got "
                                f"{v!r}")
            scope = v
        return sem, scope

    def _lower_tl_atomic_rmw(self, args, node, loc, construct, op_kind):
        ptr = self._lower_expr(args["pointer"])
        if isinstance(ptr, (BlockPtrVal, PointerTypeVal, ConstVal)):
            raise self._err(node, construct,
                            "the atomic's pointer must be a pointer value")
        if not ptr.type.is_pointer():
            raise self._err(node, construct,
                            f"unsupported pointer type {ptr.type!r}")
        pointee = ptr.type.pointee
        val = self._lower_expr(args["val"])
        if isinstance(val, ConstVal):
            val_v = self._const_at(val.value, pointee, loc)
        else:
            val_v = self._convert_if_needed(val, pointee, loc)
        mask_v = None
        if "mask" in args:
            mask = self._lower_expr(args["mask"])
            if isinstance(mask, ConstVal):
                raise self._err(node, construct,
                                "a compile-time mask folds at "
                                "specialization (remove it or use a "
                                "runtime block mask)")
            mask_v = self._materialize(mask, loc)
            if not mask_v.type.is_bool():
                raise self._err(node, construct,
                                f"mask must be boolean, got "
                                f"{mask_v.type!r}")
            if ptr.rank == 0:
                raise self._err(node, construct,
                                "a masked scalar atomic is not in this "
                                "slice (the mask must be a block value)")
            if mask_v.rank == 0:
                raise self._err(node, construct,
                                "the mask must be a block value when the "
                                "pointer is one")
        for v, what in ((val_v, "value"), (mask_v, "mask")):
            if v is None:
                continue
            if _exceeds(v.shape, ptr.shape):
                raise self._err(node, construct,
                                f"{what} shape {list(v.shape)} exceeds the "
                                f"pointer shape {list(ptr.shape)}")
        val_v = self._broadcast_value_to(val_v, ptr.shape, loc, node)
        if mask_v is not None:
            mask_v = self._broadcast_value_to(mask_v, ptr.shape, loc, node)
        ptr_real = self._realize_if_needed(ptr, loc)
        val_real = self._realize_if_needed(val_v, loc)
        sem, scope = self._atomic_sem_scope(args, node, loc)
        return self._emit(tir.Op.atomic_rmw(op_kind, ptr_real, val_real,
                                            mask_v,
                                            tir.MaskedDefault.NO_ACCESS,
                                            sem, scope, loc), "atm")

    def _lower_tl_atomic_cas(self, args, node, loc):
        ptr = self._lower_expr(args["pointer"])
        if isinstance(ptr, (BlockPtrVal, PointerTypeVal, ConstVal)):
            raise self._err(node, "tl.atomic_cas",
                            "the atomic's pointer must be a pointer value")
        if not ptr.type.is_pointer():
            raise self._err(node, "tl.atomic_cas",
                            f"unsupported pointer type {ptr.type!r}")
        pointee = ptr.type.pointee
        cmp_v = self._lower_expr(args["cmp"])
        val_v = self._lower_expr(args["val"])
        if isinstance(cmp_v, ConstVal):
            cmp_v = self._const_at(cmp_v.value, pointee, loc)
        else:
            cmp_v = self._convert_if_needed(cmp_v, pointee, loc)
        if isinstance(val_v, ConstVal):
            val_v = self._const_at(val_v.value, pointee, loc)
        else:
            val_v = self._convert_if_needed(val_v, pointee, loc)
        sem, scope = self._atomic_sem_scope(args, node, loc)
        return self._emit(tir.Op.atomic_cas(
            self._realize_if_needed(ptr, loc),
            self._realize_if_needed(
                self._broadcast_value_to(cmp_v, ptr.shape, loc, node), loc),
            self._realize_if_needed(
                self._broadcast_value_to(val_v, ptr.shape, loc, node), loc),
            None, tir.MaskedDefault.NO_ACCESS, sem, scope, loc), "cas")

    # -- gather / interleave -----------------------------------------------------

    def _lower_tl_gather(self, args, node, loc):
        src = self._lower_expr(args["src"])
        if isinstance(src, ConstVal):
            raise self._err(node, "tl.gather",
                            "a gather over a compile-time value folds at "
                            "specialization")
        if not isinstance(src, tir.Value):
            raise self._err(node, "tl.gather",
                            "gather's source must be a block value")
        index = self._lower_expr(args["index"])
        if isinstance(index, ConstVal):
            raise self._err(node, "tl.gather",
                            "a compile-time index folds at specialization")
        index_v = self._materialize(index, loc)
        axis = 0
        if "axis" in args:
            v = self.env.evaluate(args["axis"], self.source.path)
            if v is NOT_CONSTEXPR or isinstance(v, bool) \
                    or not isinstance(v, int):
                raise self._err(node, "tl.gather",
                                "axis must be a compile-time integer")
            axis = v
        return self._emit(tir.Op.gather(src, index_v, axis, loc), "gth")

    def _lower_tl_interleave(self, args, node, loc):
        a = self._lower_expr(args["a"])
        b = self._lower_expr(args["b"])
        if isinstance(a, ConstVal) or isinstance(b, ConstVal):
            raise self._err(node, "tl.interleave",
                            "interleave operates on runtime block values")
        if not isinstance(a, tir.Value) or not isinstance(b, tir.Value):
            raise self._err(node, "tl.interleave",
                            "interleave operates on block values")
        return self._emit(tir.Op.interleave(a, b, loc), "itl")

    def _lower_tl_pointer_type(self, args, node, loc) -> PointerTypeVal:
        if "address_space" in args or "const" in args:
            raise self._err(node, "tl.pointer_type",
                            "address_space/const pointer types are not in "
                            "the declared surface (the plain pointer_type "
                            "form is)")
        elem = self._constexpr_dtype(args["element_ty"], node,
                                     "tl.pointer_type")
        return PointerTypeVal(elem)

    def _lower_tl_debug_barrier(self, args, node, loc):
        """tl.debug_barrier: intra-program ordering, a statement (no
        result).  The lowering emits the explicit fence; the construct
        declares no cross-worker synchronization."""
        if args:
            raise self._err(node, "tl.debug_barrier",
                            "tl.debug_barrier takes no parameters")
        self._emit(tir.Op.barrier(loc), "bar")
        return None

    # -- reductions (T009) ----------------------------------------------------
    def _reduction_operand(self, args, node, loc, construct) -> tir.Value:
        value = self._lower_expr(args["input"] if "input" in args
                                 else args["x"])
        if isinstance(value, ConstVal):
            raise self._err(
                node, construct,
                "a reduction over a compile-time value folds at "
                "specialization (no runtime reduction is produced)")
        if value.rank == 0:
            raise self._err(
                node, construct,
                "a reduction requires a block (rank>0) operand")
        return value

    def _reduction_axis(self, args, node, construct, rank: int,
                        param: str = "axis"):
        if param not in args:
            return None
        axis = py_scalar(self.env.evaluate(args[param], self.source.path))
        if axis is NOT_CONSTEXPR:
            raise self._err(
                node, construct,
                f"{param} must be a compile-time integer (a runtime axis "
                "is not a legal Triton reduction)")
        from a100c.plan import stages as stages_mod
        try:
            return stages_mod.normalize_axes(axis, rank)
        except ValueError as exc:
            raise self._err(node, construct, exc.args[0])

    def _promote_reduction_input(self, value: tir.Value, kind: str,
                                 dtype_arg, node, loc, construct) -> tir.Value:
        """The pinned Triton 3.8 reductions' input promotions (standard.py):
        sum promotes integer widths < 32 to the same-sign 32-bit type
        (overflow prevention); max/min/argmax/argmin additionally promote
        bfloat16 to fp32 (no FMAX/FMIN/CMP for bf16 in hardware) and every
        <32-bit type to fp32/int32.  ``dtype=`` overrides (the input
        converts before the reduction)."""
        ty = value.type
        if dtype_arg is not None:
            target = self._constexpr_dtype(dtype_arg, node, construct)
            return self._convert_if_needed(value, target, loc)
        target = ty
        if kind == "sum":
            if ty.is_int() and ty.bitwidth() < 32:
                target = tir.INT32 if ty.is_int_signed() else tir.UINT32
        elif kind in ("max", "min", "argmax", "argmin"):
            if ty.name == "bf16":
                target = tir.FLOAT32
            elif ty.bitwidth() < 32:
                if ty.is_float():
                    target = tir.FLOAT32
                elif ty.is_int():
                    target = tir.INT32 if ty.is_int_signed() else tir.UINT32
        return self._convert_if_needed(value, target, loc)

    def _lower_tl_reduction(self, args: Dict[str, ast.expr], node: ast.Call,
                            loc, construct: str) -> tir.Value:
        """tl.sum / tl.max / tl.min / tl.argmax / tl.argmin / tl.xor_sum /
        tl.reduce_or: the TIR ``reduce`` op carrying the per-op-and-dtype
        identity, axes, keep_dims and the declared tie-break."""
        from a100c.plan import stages as stages_mod
        kind = _REDUCE_KINDS[construct]
        value = self._reduction_operand(args, node, loc, construct)
        spec = stages_mod.REDUCTION_OPS[construct]
        value = self._promote_reduction_input(
            value, kind, args.get("dtype"), node, loc, construct)
        axes = self._reduction_axis(args, node, construct, value.rank)
        if axes is None:
            axes = tuple(range(value.rank))
        if len(axes) != len(value.shape):
            raise self._err(
                node, construct,
                "reducing every axis of a multi-axis block is not in this "
                "path (the block forms are rank 1; partial axis sets come "
                "with the layout lane's multi-axis blocks)")
        if kind in ("xor_sum", "reduce_or") and not value.type.is_int():
            raise self._err(
                node, construct,
                f"{construct} requires integer operands, got "
                f"{value.type!r}")
        keep_dims = False
        if "keep_dims" in args:
            kd = self.env.evaluate(args["keep_dims"], self.source.path)
            if kd is not NOT_CONSTEXPR:
                keep_dims = bool(kd)
        tie_break_left = True
        tie_param = ("tie_break_left" if kind in ("argmax", "argmin")
                     else "return_indices_tie_break_left")
        if tie_param in args:
            tb = self.env.evaluate(args[tie_param], self.source.path)
            if tb is not NOT_CONSTEXPR:
                tie_break_left = bool(tb)
        if kind in ("argmax", "argmin"):
            identity = stages_mod.identity_for(kind, tir.INT32)
            op = tir.Op.reduce(value, kind, axes, keep_dims, identity,
                               loc=loc, tie_break_left=tie_break_left)
            self._emit(op, "arg")
            return op.results[0]
        identity = stages_mod.identity_for(kind, value.type)
        op = tir.Op.reduce(value, kind, axes, keep_dims, identity, loc=loc,
                           tie_break_left=tie_break_left)
        self._emit(op, "red")
        return op.results[0]

    def _lower_tl_maxmin(self, args: Dict[str, ast.expr], node: ast.Call,
                         loc, construct: str,
                         want_indices: bool = False):
        """tl.max / tl.min: the value form, or the (value, index) pair when
        return_indices=True (two TIR results on one reduce op)."""
        from a100c.plan import stages as stages_mod
        kind = _REDUCE_KINDS[construct]
        value = self._reduction_operand(args, node, loc, construct)
        value = self._promote_reduction_input(value, kind, None, node, loc,
                                              construct)
        axes = self._reduction_axis(args, node, construct, value.rank)
        if axes is None:
            axes = tuple(range(value.rank))
        if len(axes) != len(value.shape):
            raise self._err(
                node, construct,
                "reducing every axis of a multi-axis block is not in this "
                "path (the block forms are rank 1)")
        keep_dims = False
        if "keep_dims" in args:
            kd = self.env.evaluate(args["keep_dims"], self.source.path)
            if kd is not NOT_CONSTEXPR:
                keep_dims = bool(kd)
        tie_break_left = True
        if "return_indices_tie_break_left" in args:
            tb = self.env.evaluate(args["return_indices_tie_break_left"],
                                   self.source.path)
            if tb is not NOT_CONSTEXPR:
                tie_break_left = bool(tb)
        return_indices = False
        if "return_indices" in args:
            ri = self.env.evaluate(args["return_indices"], self.source.path)
            if ri is not NOT_CONSTEXPR:
                return_indices = bool(ri)
        if return_indices and not want_indices:
            raise self._err(
                node, construct,
                "return_indices=True yields (values, indices); unpack the "
                "two results into names")
        if want_indices and not return_indices:
            raise self._err(
                node, construct,
                "the call does not set return_indices=True (nothing to "
                "unpack)")
        identity = stages_mod.identity_for(kind, value.type)
        op = tir.Op.reduce(value, kind, axes, keep_dims, identity, loc=loc,
                           tie_break_left=tie_break_left,
                           return_indices=return_indices)
        if return_indices:
            self._block.statements.append(op)
            for i, r in enumerate(op.results):
                r.name = self._fresh_name("red" if i == 0 else "ridx")
            return [op.results[0], op.results[1]]
        self._emit(op, "red")
        return op.results[0]

    def _lower_tl_scan(self, args: Dict[str, ast.expr], node: ast.Call,
                       loc, construct: str) -> tir.Value:
        """tl.cumsum / tl.cumprod: the TIR ``scan`` op (inclusive prefix
        scan along one axis, with the carry identity)."""
        from a100c.plan import stages as stages_mod
        kind = "cumsum" if construct == "tl.cumsum" else "cumprod"
        value = self._reduction_operand(args, node, loc, construct)
        value = self._promote_reduction_input(
            value, "sum", args.get("dtype"), node, loc, construct)
        axes = self._reduction_axis(args, node, construct, value.rank)
        if axes is None or len(axes) != 1:
            raise self._err(
                node, construct,
                "a scan requires exactly one axis (cumsum/cumprod scan one "
                "dimension)")
        axis = axes[0]
        reverse = False
        if "reverse" in args:
            rv = self.env.evaluate(args["reverse"], self.source.path)
            if rv is not NOT_CONSTEXPR:
                reverse = bool(rv)
        identity = stages_mod.identity_for(kind, value.type)
        op = tir.Op.scan(value, kind, axis, reverse, identity, loc=loc)
        return self._emit(op, "scan")

    def _lower_tl_softmax(self, args: Dict[str, ast.expr], node: ast.Call,
                          loc, construct: str) -> tir.Value:
        """tl.softmax: the composite is exp(x - max(x)) / sum(exp(x -
        max(x))) -- the reduction structure (axis, keep_dims, stable max
        subtraction) is declared in a100c/plan/stages.py, but the
        elementwise exp is the math-ops lane's construct; refused with a
        located diagnostic naming the dependency (never miscompiled)."""
        raise self._err(
            node, "tl.softmax",
            "tl.softmax lowers to max/sum reductions over exp terms; the "
            "elementwise exp is the math-ops lane's construct (the "
            "reduction structure -- axis, keep_dims, the stable max "
            "subtraction -- is declared in a100c/plan/stages.py)")

    def _lower_tl_histogram(self, args: Dict[str, ast.expr], node: ast.Call,
                            loc, construct: str) -> tir.Value:
        value = self._reduction_operand(args, node, loc, construct)
        num_bins = self._constexpr_int(args["num_bins"], node, construct,
                                       "num_bins")
        if not value.type.is_int():
            raise self._err(
                node, construct,
                f"tl.histogram requires an integer input (bin membership), "
                f"got {value.type!r}")
        if "mask" in args:
            raise self._err(
                node, construct,
                "tl.histogram's mask parameter is not in this path (the "
                "masked form needs the memory lane's masked-block forms)")
        op = tir.Op.histogram(value, num_bins, loc=loc)
        return self._emit(op, "hist")

    def _lower_tl_sort(self, args: Dict[str, ast.expr], node: ast.Call,
                       loc, construct: str) -> tir.Value:
        value = self._reduction_operand(args, node, loc, construct)
        dim = self._scan_dim(args, node, construct, value.rank)
        descending = False
        if "descending" in args:
            d = self.env.evaluate(args["descending"], self.source.path)
            if d is not NOT_CONSTEXPR:
                descending = bool(d)
        op = tir.Op.sort(value, dim, descending, loc=loc)
        return self._emit(op, "sort")

    def _lower_tl_topk(self, args: Dict[str, ast.expr], node: ast.Call,
                       loc, construct: str) -> tir.Value:
        value = self._reduction_operand(args, node, loc, construct)
        dim = self._scan_dim(args, node, construct, value.rank)
        k = self._constexpr_int(args["k"], node, construct, "k")
        if not 1 <= k <= value.shape[dim].value:
            raise self._err(
                node, construct,
                f"k={k} outside 1..{value.shape[dim].value} (the block "
                "extent along dim)")
        descending = True
        if "descending" in args:
            d = self.env.evaluate(args["descending"], self.source.path)
            if d is not NOT_CONSTEXPR:
                descending = bool(d)
        op = tir.Op.topk(value, k, dim, descending, loc=loc)
        return self._emit(op, "topk")

    def _scan_dim(self, args, node, construct, rank: int) -> int:
        if "dim" not in args:
            return rank - 1              # the pinned default: last dim
        dim = py_scalar(self.env.evaluate(args["dim"], self.source.path))
        if dim is NOT_CONSTEXPR or isinstance(dim, bool) \
                or not isinstance(dim, int):
            raise self._err(node, construct, "dim must be a compile-time "
                            "integer")
        d = dim + rank if dim < 0 else dim
        if not 0 <= d < rank:
            raise self._err(node, construct,
                            f"dim {dim} outside rank {rank}")
        return d

    def _lower_tl_cast(self, args: Dict[str, ast.expr], node: ast.Call,
                       loc, construct: str) -> tir.Value:
        """tl.cast / ``.to``: value conversion, distinct from bitcast.

        The identity cast folds (a same-type ``.to`` is a no-op -- the
        pinned semantics make it one); every *real* conversion emits the
        TIR ``convert`` op whose legalisation the conversions lane owns
        (this path executes the int32->fp32 form the reduction families'
        mean/normalize kernels need; the rest refuse with a located
        diagnostic at the lowering, never a silent reinterpretation)."""
        value = self._lower_expr(args["input"])
        if isinstance(value, ConstVal):
            raise self._err(
                node, construct,
                "a compile-time value converts at specialization (no "
                "runtime convert is produced)")
        if "bitcast" in args:
            flag = self.env.evaluate(args["bitcast"], self.source.path)
            if flag is not NOT_CONSTEXPR and flag:
                raise self._err(
                    node, construct,
                    "bitcast=True is bit-level reinterpretation, a distinct "
                    "construct (the conversions lane owns the bitcast "
                    "matrix)")
        if "fp_downcast_rounding" in args:
            raise self._err(
                node, construct,
                "fp_downcast_rounding selects a semantic rounding mode "
                "(the conversions lane owns the rounding forms)")
        # the pointer-table pattern: .to(tl.pointer_type(elem)) reinterprets
        # a same-width integer as a pointer (the distinct bitcast construct,
        # never a value convert)
        dtype_node = args["dtype"]
        if isinstance(dtype_node, ast.Call) \
                and isinstance(dtype_node.func, ast.Attribute) \
                and isinstance(dtype_node.func.value, ast.Name) \
                and dtype_node.func.value.id == "tl" \
                and dtype_node.func.attr == "pointer_type":
            ptarget = self._lower_tl_pointer_type(
                self._bind_call_args("tl.pointer_type", dtype_node)[0],
                dtype_node, loc)
            if not value.type.is_int() or value.type.bitwidth() != 64:
                raise self._err(
                    node, construct,
                    f"the int-to-pointer reinterpretation requires a "
                    f"64-bit integer, got {value.type!r} -> "
                    f"*{ptarget.pointee!r} (the value convert is a "
                    "different construct)")
            return self._emit(tir.Op.bitcast(value, tir.Type.pointer(
                ptarget.pointee), loc), "pbc")
        target = self._constexpr_dtype(args["dtype"], node, construct)
        if target == value.type:
            return value                 # the identity cast folds
        if not ftypes.convert_ok(value.type, target):
            raise self._err(
                loc_node(loc), "convert",
                f"cannot convert {value.type!r} to {target!r}")
        op = tir.Op.convert(value, target, loc)
        return self._emit(op, "cvt")

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
    "tl.num_programs": Lowering._lower_tl_num_programs,
    "tl.where": Lowering._lower_tl_where,
    "tl.zeros": Lowering._lower_tl_zeros,
    "tl.full": Lowering._lower_tl_full,
    "tl.zeros_like": Lowering._lower_tl_zeros_like,
    "tl.constexpr": Lowering._lower_tl_constexpr,
    "tl.multiple_of": Lowering._lower_tl_multiple_of,
    "tl.max_contiguous": Lowering._lower_tl_max_contiguous,
    # T011: memory access breadth and atomics
    "tl.cdiv": Lowering._lower_tl_cdiv,
    "tl.make_block_ptr": Lowering._lower_make_block_ptr,
    "tl.advance": Lowering._lower_advance,
    "tl.pointer_type": Lowering._lower_tl_pointer_type,
    "tl.gather": Lowering._lower_tl_gather,
    "tl.interleave": Lowering._lower_tl_interleave,
    "tl.atomic_add": lambda self, a, n, l: Lowering._lower_tl_atomic_rmw(
        self, a, n, l, "tl.atomic_add", "add"),
    "tl.atomic_max": lambda self, a, n, l: Lowering._lower_tl_atomic_rmw(
        self, a, n, l, "tl.atomic_max", "max"),
    "tl.atomic_min": lambda self, a, n, l: Lowering._lower_tl_atomic_rmw(
        self, a, n, l, "tl.atomic_min", "min"),
    "tl.atomic_xchg": lambda self, a, n, l: Lowering._lower_tl_atomic_rmw(
        self, a, n, l, "tl.atomic_xchg", "xchg"),
    "tl.atomic_and": lambda self, a, n, l: Lowering._lower_tl_atomic_rmw(
        self, a, n, l, "tl.atomic_and", "and"),
    "tl.atomic_or": lambda self, a, n, l: Lowering._lower_tl_atomic_rmw(
        self, a, n, l, "tl.atomic_or", "or"),
    "tl.atomic_xor": lambda self, a, n, l: Lowering._lower_tl_atomic_rmw(
        self, a, n, l, "tl.atomic_xor", "xor"),
    "tl.atomic_cas": Lowering._lower_tl_atomic_cas,
    "tl.debug_barrier": Lowering._lower_tl_debug_barrier,
    # reductions, scans and their index forms (T009); the table carries
    # the construct so one handler serves a family
    "tl.sum": lambda self, a, n, l: Lowering._lower_tl_reduction(
        self, a, n, l, "tl.sum"),
    "tl.max": lambda self, a, n, l: Lowering._lower_tl_maxmin(
        self, a, n, l, "tl.max"),
    "tl.min": lambda self, a, n, l: Lowering._lower_tl_maxmin(
        self, a, n, l, "tl.min"),
    "tl.argmax": lambda self, a, n, l: Lowering._lower_tl_reduction(
        self, a, n, l, "tl.argmax"),
    "tl.argmin": lambda self, a, n, l: Lowering._lower_tl_reduction(
        self, a, n, l, "tl.argmin"),
    "tl.xor_sum": lambda self, a, n, l: Lowering._lower_tl_reduction(
        self, a, n, l, "tl.xor_sum"),
    "tl.reduce_or": lambda self, a, n, l: Lowering._lower_tl_reduction(
        self, a, n, l, "tl.reduce_or"),
    "tl.cumsum": lambda self, a, n, l: Lowering._lower_tl_scan(
        self, a, n, l, "tl.cumsum"),
    "tl.cumprod": lambda self, a, n, l: Lowering._lower_tl_scan(
        self, a, n, l, "tl.cumprod"),
    "tl.softmax": lambda self, a, n, l: Lowering._lower_tl_softmax(
        self, a, n, l, "tl.softmax"),
    "tl.histogram": lambda self, a, n, l: Lowering._lower_tl_histogram(
        self, a, n, l, "tl.histogram"),
    "tl.sort": lambda self, a, n, l: Lowering._lower_tl_sort(
        self, a, n, l, "tl.sort"),
    "tl.topk": lambda self, a, n, l: Lowering._lower_tl_topk(
        self, a, n, l, "tl.topk"),
    "tl.cast": lambda self, a, n, l: Lowering._lower_tl_cast(
        self, a, n, l, "tl.cast"),
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


def _const_eq(a, b) -> bool:
    """Constexpr equality for join folding (numeric == across int/float)."""
    if isinstance(a, bool) != isinstance(b, bool):
        return False
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return type(a) is type(b) and a == b
    return a == b and type(a) is type(b)


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
