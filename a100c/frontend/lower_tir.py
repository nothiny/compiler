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
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from a100c.frontend import shapes as fshapes
from a100c.frontend import types as ftypes
from a100c.frontend.source import FrontendError, OperatorSource
from a100c.frontend.specialize import (ConstexprEnv, DTypeValue,
                                       NOT_CONSTEXPR, Specialization,
                                       TypeObject, py_scalar)
from a100c.frontend.surface import (CLASS_IGNORABLE, CLASS_IMPLEMENTED,
                                    CLASS_REFUSED, EXCLUDED_CONSTRUCTS,
                                    Surface, DEFAULT_SURFACE)
from a100c.ir import tir

__all__ = ["ConstVal", "Lowering", "lower", "IgnoredParam"]

#: the early-return state's source-level name: one i1 per function, bound
#: true at entry when the kernel has any ``return``, re-bound false at
#: every return site and carried through every region join and loop
#: channel (the guard semantics the terminator needs)
_RET_ACTIVE = "%ret.active"


class _ArmState:
    """One lowered if-arm's post-state: the final bindings, the folding
    env, the return state and the sequence terminator that fired (None
    when the arm ran to completion)."""

    __slots__ = ("symbols", "env_values", "ret_active", "ret_fired",
                 "term_kind")

    def __init__(self, symbols, env_values, ret_active, ret_fired,
                 term_kind):
        self.symbols = symbols
        self.env_values = env_values
        self.ret_active = ret_active
        self.ret_fired = ret_fired
        self.term_kind = term_kind

    @property
    def terminated(self) -> bool:
        return self.term_kind is not None


class _JumpScan:
    """The region terminators a statement list contains.

    ``returns`` counts every Return in the subtree (a return inside a
    nested loop still terminates the enclosing regions); ``breaks`` and
    ``continues`` count only the jumps that belong to THIS loop level --
    a jump inside a nested loop belongs to that loop."""

    __slots__ = ("returns", "breaks", "continues")

    def __init__(self, returns: int, breaks: int, continues: int):
        self.returns = returns
        self.breaks = breaks
        self.continues = continues


def _scan_jumps(stmts) -> _JumpScan:
    ret = brk = cont = 0

    def walk(ss):
        nonlocal ret, brk, cont
        for st in ss:
            if isinstance(st, ast.Return):
                ret += 1
            elif isinstance(st, ast.Break):
                brk += 1
            elif isinstance(st, ast.Continue):
                cont += 1
            elif isinstance(st, ast.If):
                walk(st.body)
                walk(st.orelse or [])
            elif isinstance(st, (ast.For, ast.While)):
                # a nested loop's jumps belong to it; its returns still
                # terminate this level too
                ret += _scan_jumps(st.body).returns

    walk(stmts)
    return _JumpScan(ret, brk, cont)


@dataclass
class ConstVal:
    """A compile-time value flowing through the lowering (a literal, a
    constexpr parameter, a folded expression or a dtype)."""
    value: object
    #: the pinned ``visit_Assign`` rule: a Python scalar bound to a plain
    #: local name becomes a rank-0 TENSOR of its ``to_tensor`` type
    #: (float -> fp32, int by range, bool -> i1) -- it PARTICIPATES in
    #: binary-op type promotion exactly like a tensor operand, unlike a
    #: source literal in a BinOp (``x_fp16 * alpha`` is fp32 when
    #: ``alpha = 1.5`` is a name, fp16 when ``x_fp16 * 1.5`` is written
    #: inline; probed against the pinned 3.8 tracer).  A constexpr
    #: parameter or a ``tl.constexpr``-annotated binding stays a pure
    #: compile-time value (``tensor_sem`` False).
    tensor_sem: bool = False


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
_METHOD_CONSTRUCTS = {
    ".to": "tl.cast",
    # the pinned tensor member ``cast`` (same parameter surface as ``.to``:
    # dtype, fp_downcast_rounding, bitcast -- the corpus's geglu/vocab-CE/
    # grpo-loss method-form calls)
    ".cast": "tl.cast",
    # T012: the layout/shape method forms (the pinned tensor members)
    ".reshape": "tl.reshape", ".trans": "tl.trans", ".permute": "tl.permute",
    ".expand_dims": "tl.expand_dims", ".unsqueeze": "tl.unsqueeze",
    ".squeeze": "tl.squeeze", ".broadcast_to": "tl.broadcast_to",
    ".ravel": "tl.ravel", ".view": "tl.view", ".flip": "tl.flip",
    ".to_tensor": "tl.to_tensor",
}

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
    "tl.static_assert": ("cond",),
    "tl.dtype": ("name",),
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
    # T012: layout, shape and dtype-conversion breadth
    "tl.reshape": ("input",),
    "tl.trans": ("input",),
    "tl.permute": ("input",),
    "tl.join": ("a", "b"),
    "tl.split": ("a",),
    "tl.cat": ("input", "other"),
    "tl.expand_dims": ("input", "axis"),
    "tl.unsqueeze": ("x", "dim"),
    "tl.squeeze": ("x", "dim"),
    "tl.broadcast_to": ("input",),
    "tl.broadcast": ("input", "other"),
    "tl.ravel": ("x",),
    "tl.view": ("input",),
    "tl.flip": ("x",),
    "tl.swizzle2d": ("i", "j", "size_i", "size_j", "size_g"),
    "tl.to_tensor": ("x",),
    # T013: special math functions and bit-exact RNG
    "tl.exp": ("x",), "tl.exp2": ("x",), "tl.log": ("x",),
    "tl.log2": ("x",), "tl.sin": ("x",), "tl.cos": ("x",),
    "tl.erf": ("x",), "tl.sqrt": ("x",), "tl.sqrt_rn": ("x",),
    "tl.rsqrt": ("x",), "tl.floor": ("x",), "tl.ceil": ("x",),
    "tl.abs": ("x",),
    "tl.maximum": ("x", "y"), "tl.minimum": ("x", "y"),
    "tl.clamp": ("x", "min", "max"),
    "tl.fma": ("x", "y", "z"),
    "tl.div_rn": ("x", "y"),
    "tl.sigmoid": ("x",),
    "tl.softmax": ("x",),
    # T014: the matrix-breadth lane
    "tl.dot": ("input", "other"),
    "tl.add": ("x", "y"), "tl.sub": ("x", "y"), "tl.mul": ("x", "y"),
    "tl.philox": ("seed", "c0", "c1", "c2", "c3"),
    "tl.rand": ("seed", "offset"), "tl.randn": ("seed", "offset"),
    "tl.randint": ("seed", "offset"),
    "tl.rand4x": ("seed", "offsets"),
    "tl.randint4x": ("seed", "offset"),
    "tl.randn4x": ("seed", "offset"),
}

#: constructs whose call produces multiple values (the tuple-unpack forms):
#: tl.max/min with return_indices, tl.split, tl.broadcast, tl.swizzle2d and
#: the 4x RNG family / tl.philox (four counter words each)
_MULTI_RESULT_CONSTRUCTS = {"tl.max", "tl.min", "tl.split", "tl.broadcast",
                            "tl.swizzle2d", "tl.philox", "tl.rand4x",
                            "tl.randint4x", "tl.randn4x"}

#: reduction constructs -> the TIR reduce kind
_REDUCE_KINDS = {
    "tl.sum": "sum", "tl.max": "max", "tl.min": "min",
    "tl.argmax": "argmax", "tl.argmin": "argmin",
    "tl.xor_sum": "xor_sum", "tl.reduce_or": "reduce_or",
}

#: T013: special math constructs -> the TIR math op code
_MATH_UNARY_CODES = {
    "tl.exp": "math.exp", "tl.exp2": "math.exp2",
    "tl.log": "math.log", "tl.log2": "math.log2",
    "tl.sin": "math.sin", "tl.cos": "math.cos",
    "tl.erf": "math.erf", "tl.sqrt": "math.sqrt",
    "tl.sqrt_rn": "math.sqrt_rn", "tl.rsqrt": "math.rsqrt",
    "tl.floor": "math.floor", "tl.ceil": "math.ceil",
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
        #: the early-return state (T026): ``%ret.active`` is the i1 name
        #: bound once at function entry when the kernel has any return;
        #: ``_ret_active`` holds the may-have-returned binding for the
        #: sequence being lowered (None = definitely active) and
        #: ``_ret_fired`` records that a return site lowered in the
        #: current arm (the join must carry the flag out of the region)
        self._ret_active: Optional[tir.Value] = None
        self._ret_fired = False
        #: the stop channels of the open loops (break/return set them to
        #: false; the loop's re-evaluated condition ANDs the channel) and
        #: the plain loop depth (break/continue legality)
        self._loop_stop_stack: List[str] = []
        self._loop_depth = 0
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

    def _emit_multi(self, op: tir.Op, results: int, hint: str) -> tir.Op:
        """Emit a multi-result op (tl.split's two values): every result
        gets a fresh name; the caller binds the names."""
        assert len(op.results) == results
        self._block.statements.append(op)
        for i, r in enumerate(op.results):
            r.name = self._fresh_name(f"{hint}{i + 1}")
        return op

    # ------------------------------------------------------------------ entry
    def lower(self) -> tir.Module:
        assert self.source.kernel_ast is not None
        body = self.source.kernel_ast.body
        if _scan_jumps(body).returns:
            # the early-return state: one i1 bound at function entry,
            # carried through every region join (the value visible after
            # a branch is the join of the arms' bindings -- the return
            # site binds false, the not-taken path keeps the outer value)
            loc = tir.SrcLoc(self.source.path,
                             self.source.kernel_ast.body[-1].lineno
                             if body else 1, 1)
            active = self._emit(tir.Op.const(True, tir.INT1, loc), "act")
            self._bind(_RET_ACTIVE, active)
        self._lower_stmts(body)
        return self.module

    # ------------------------------------------------------------------ stmts
    def _lower_stmts(self, stmts: List[ast.stmt]) -> Optional[str]:
        """Lower one statement sequence.

        Returns the terminator that ended it -- ``'return'``/``'break'``/
        ``'continue'`` when a region terminator fired (the remaining
        statements are dead: Triton's dead block after a return) -- or
        None when the sequence ran to completion.  A statement may also
        CONSUME trailing statements (the tail relocation into a branch's
        live arm); it reports ``("consumed", k)`` and the sequence skips
        them.  Once a return may have fired on this path, the remaining
        statements lower inside one guard on the active flag (the guard
        semantics the return state carries through the joins)."""
        i = 0
        n = len(stmts)
        while i < n:
            if self._ret_active is not None:
                return self._lower_active_guard(stmts[i:])
            result = self._lower_stmt(stmts[i], stmts[i + 1:])
            if result is None:
                i += 1
            elif isinstance(result, tuple):
                i += 1 + result[1]        # the relocation consumed the tail
            else:
                return result             # the sequence's terminator
        return None

    def _lower_active_guard(self, stmts: List[ast.stmt]) -> Optional[str]:
        """``if <active>: <stmts>`` -- the region terminator's guard.

        The statements after a possible return run only while the
        function is active; the returned path falls through the empty
        else arm.  Inside the guard's then arm the state is definitely
        active again (a nested return site re-binds the flag and nests
        its own guard)."""
        if not stmts:
            return None
        loc = self._loc(stmts[0])
        cond = self._ret_active
        node, _, _ = self._emit_runtime_if(
            cond, loc,
            lambda: self._lower_stmts(stmts),
            lambda: None)
        del node
        return None

    def _lower_stmt(self, st: ast.stmt,
                    tail: Sequence[ast.stmt] = ()):
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
            # the pinned ``visit_Assign`` sanitize rule: a plain Python
            # scalar bound by assignment is a rank-0 TENSOR of its
            # to_tensor type (it participates in promotion; a source
            # literal in a BinOp does not -- ConstVal.tensor_sem)
            if isinstance(value, ConstVal) and \
                    isinstance(_py_scalar(value.value), (bool, int, float)) \
                    and not isinstance(value.value, (DTypeValue, TypeObject)):
                value = ConstVal(value.value, tensor_sem=True)
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
                term = self._lower_stmts(taken)
                # the taken arm's own tail consumption is internal to it;
                # only a terminator propagates (the fold is transparent to
                # the enclosing sequence's tail)
                return term if isinstance(term, str) else None
            return self._lower_runtime_if(st, tail)
        elif isinstance(st, ast.Pass):
            pass
        elif isinstance(st, (ast.For, ast.AsyncFor)):
            self._lower_for(st)
        elif isinstance(st, ast.While):
            self._lower_while(st)
        elif isinstance(st, ast.Return):
            return self._lower_return(st)
        elif isinstance(st, ast.Break):
            return self._lower_break(st)
        elif isinstance(st, ast.Continue):
            return self._lower_continue(st)
        else:
            raise self._err(
                st, type(st).__name__,
                "statement is not in the elementwise core")

    # -- region terminators (T026) ------------------------------------------
    def _lower_return(self, st: ast.Return) -> str:
        """A bare early return: the region terminator with guard
        semantics.  The returned value of a kernel is discarded by the
        pinned ABI (Triton records it and the kernel entry returns void);
        the expression still evaluates for its effects.  The return state
        is the active flag (bound false here, joined across every region
        the path exits) and every open loop's stop channel (the loop
        exits rather than iterating on a returned path)."""
        if st.value is not None:
            self._lower_expr(st.value)
        loc = self._loc(st)
        for stop_name in reversed(self._loop_stop_stack):
            f = self._emit(tir.Op.const(False, tir.INT1, loc), "stop")
            self._bind(stop_name, f)
        f = self._emit(tir.Op.const(False, tir.INT1, loc), "ret")
        self._bind(_RET_ACTIVE, f)
        self._ret_fired = True
        return "return"

    def _lower_break(self, st: ast.Break) -> str:
        """``break`` as a loop exit: the innermost open loop's stop
        channel goes false (the loop's re-evaluated condition ANDs it, so
        the head test fails on the next iteration); the remaining body
        statements are dead (the sequence terminator)."""
        if not self._loop_depth:
            raise self._err(st, "break",
                            "'break' outside a loop is not a legal kernel "
                            "statement")
        if not self._loop_stop_stack:
            raise self._err(st, "break",
                            "'break' inside this loop form is not in the "
                            "structured control-flow core")
        loc = self._loc(st)
        f = self._emit(tir.Op.const(False, tir.INT1, loc), "stop")
        self._bind(self._loop_stop_stack[-1], f)
        return "break"

    def _lower_continue(self, st: ast.Continue) -> str:
        """``continue``: the remaining body statements are dead; the
        induction increment and the condition re-evaluation still run at
        the body end (the back-edge values are the bindings at the
        continue point)."""
        if not self._loop_depth:
            raise self._err(st, "continue",
                            "'continue' outside a loop is not a legal "
                            "kernel statement")
        return "continue"

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
    def _lower_runtime_if(self, st: ast.If,
                          tail: Sequence[ast.stmt] = ()):
        """The runtime if: a two-arm region with explicit join parameters.

        Each arm starts from the pre-branch state (the snapshot restored
        between the arms -- the else arm must never see the then arm's
        bindings).  A name assigned on one path keeps the outer binding on
        the other (Python's branch semantics): the join takes the outer
        value as the not-assigned side, so every value carried across the
        branch joins.  A region terminator that fires in one arm relocates
        the enclosing sequence's remaining statements into the other arm
        (they must not run on the terminated path) -- the caller is told
        the tail was consumed so it does not lower it again.

        Returns None (nothing consumed), ``("consumed", k)`` when the
        first ``k`` tail statements relocated into the live arm, or the
        sequence terminator when both arms terminated."""
        loc = self._loc(st)
        cond_v = self._lower_expr(st.test)
        if isinstance(cond_v, ConstVal):
            # the arms re-bound names since the first fold attempt: re-fold
            taken = st.body if cond_v.value else (st.orelse or [])
            self.fold.record_branch(st, bool(cond_v.value),
                                    "body" if cond_v.value else "orelse")
            return self._lower_stmts(taken)
        if not cond_v.type.is_bool():
            cond_v = self._emit_convert(cond_v, tir.INT1, loc)
        if cond_v.shape != ():
            raise self._err(
                st, "if",
                "a block-tensor condition cannot branch (Triton branches on "
                "scalars; use tl.where for per-element selection)")

        def then_fn():
            return self._lower_stmts(st.body)

        def else_fn():
            return self._lower_stmts(st.orelse)

        node, then_state, else_state = self._emit_runtime_if(
            cond_v, loc, then_fn, else_fn, tail)
        del node
        if then_state.terminated and else_state.terminated:
            return "return" if ("return" in (then_state.term_kind,
                                             else_state.term_kind)
                                ) else (then_state.term_kind
                                        or else_state.term_kind)
        if tail and then_state.terminated != else_state.terminated:
            return ("consumed", len(tail))    # the tail relocated
        return None

    def _region_restore_arm(self, arm) -> None:
        """Re-enter an arm's post-lowering state for the tail relocation."""
        self.symbols = dict(arm.symbols)
        self.env.values = dict(arm.env_values)
        self._ret_active = arm.ret_active
        self._ret_fired = arm.ret_fired

    def _emit_runtime_if(self, cond_v: tir.Value, loc,
                         then_fn, else_fn, tail: Sequence[ast.stmt] = ()):
        """The shared region-if machinery: build the ``tir.If``, lower each
        arm from the pre-branch snapshot (the else arm NEVER sees the then
        arm's bindings), relocate the tail when a region terminator fired
        in exactly one arm, then bind the joins.

        The arm callables return their sequence terminator.  Returns the
        node and the per-arm states."""
        node = tir.If(cond_v, loc)
        snap = self._region_snapshot()
        saved_fired = self._ret_fired

        self._push_block(node.then)
        self._ret_active = None
        self._ret_fired = False
        term_then = then_fn()
        then_state = _ArmState(dict(self.symbols), dict(self.env.values),
                               self._ret_active, self._ret_fired,
                               term_then)
        self._pop_block()

        self._region_restore(snap)
        self._push_block(node.els)
        self._ret_active = None
        self._ret_fired = False
        term_else = else_fn()
        else_state = _ArmState(dict(self.symbols), dict(self.env.values),
                               self._ret_active, self._ret_fired,
                               term_else)
        self._pop_block()

        self._region_restore(snap)
        # the tail relocation: a terminator that fired in exactly one arm
        # means the sequence's remaining statements must run only on the
        # other arm's path -- lower them inside that arm, after its own
        # statements, BEFORE the joins are computed (the relocated
        # statements' bindings join like any arm-local binding)
        if tail and then_state.terminated != else_state.terminated:
            arm = else_state if then_state.terminated else then_state
            block = node.els if then_state.terminated else node.then
            self._push_block(block)
            self._region_restore_arm(arm)
            self._lower_stmts(list(tail))
            arm.symbols = dict(self.symbols)
            arm.env_values = dict(self.env.values)
            arm.ret_active = self._ret_active
            arm.ret_fired = self._ret_fired
            self._pop_block()
            self._region_restore(snap)
        # joins: every name a path re-binds joins (the other path's side is
        # its own binding -- the outer value when it does not assign).
        # ConstVal sides materialize inside their arm under the join name;
        # equal constexpr bindings stay constexpr.
        outer = snap[0]
        join_names = []
        for name in sorted(set(then_state.symbols) | set(else_state.symbols)):
            t, e = then_state.symbols.get(name), else_state.symbols.get(name)
            o = outer.get(name)
            if t is None and e is None:
                continue
            if t is None or e is None:
                if o is None:
                    # defined inside one arm only and never before it:
                    # the closed-region diagnostic (a use after the region
                    # is a located error, never a guess)
                    self._closed_names.setdefault(
                        name, f"the if at line {loc.line}")
                    continue
                # assigned on one path: the other path keeps the outer
                # binding (the value carried across the branch joins)
                if t is None:
                    t = o
                else:
                    e = o
            if t is o and e is o:
                continue            # not re-bound by either arm
            if isinstance(t, ConstVal) and isinstance(e, ConstVal) \
                    and _const_eq(t.value, e.value):
                self._bind(name, t)
                continue
            if isinstance(t, (BlockPtrVal, PointerTypeVal, TupleVal)) \
                    or isinstance(e, (BlockPtrVal, PointerTypeVal, TupleVal)):
                raise FrontendError(
                    self.source.path, loc.line, loc.col, "if",
                    f"the arms re-bind '{name}' as a block pointer, a "
                    "pointer type or a runtime tuple; re-binding a "
                    "descriptor or a tuple across a branch is not in this "
                    "slice (advance it in a loop, or rebuild it after the "
                    "branch)")
            t_v = self._materialize_join_side(node.then, t, name, loc)
            e_v = self._materialize_join_side(node.els, e, name, loc)
            if t_v.type != e_v.type:
                raise FrontendError(
                    self.source.path, loc.line, loc.col, "if",
                    f"the arms bind '{name}' with different types "
                    f"({t_v.type!r} vs {e_v.type!r}); branch unification "
                    "is not in this path")
            if tir.value_shape(t_v.shape) != tir.value_shape(e_v.shape):
                raise FrontendError(
                    self.source.path, loc.line, loc.col, "if",
                    f"the arms bind '{name}' with different extent values "
                    f"({list(t_v.shape)} vs {list(e_v.shape)})")
            join_names.append(name)
        node.join_names = tuple(join_names)
        joins = []
        for name in join_names:
            side = self._materialize_join_side(node.then,
                                               then_state.symbols[name],
                                               name, loc)
            jv = tir.Value(side.type, side.shape, loc, name=name)
            jv.add_alias(name)
            joins.append(jv)
        node.join_results = tuple(joins)
        self._block.statements.append(node)
        # the join results bind after the construct (fresh values: a
        # re-bound source variable never merges with its earlier binding)
        for name, value in zip(join_names, joins):
            self._bind(name, value)
        # the return state: a return site in either arm re-bound the flag;
        # the join carries it out (None when no return can have fired)
        self._ret_fired = saved_fired or then_state.ret_fired \
            or else_state.ret_fired
        if then_state.ret_fired or else_state.ret_fired:
            v = self.symbols.get(_RET_ACTIVE)
            self._ret_active = v if isinstance(v, tir.Value) else None
        else:
            self._ret_active = None
        return node, then_state, else_state

    def _materialize_join_side(self, block: tir.Block, value, name: str,
                               loc) -> tir.Value:
        """Materialize a ConstVal join side inside its arm under the join
        name: the arm's scope must DEFINE the name (the verifier's
        both-arms rule) -- a bare constant op without the alias would
        leave the arm's binding invisible."""
        if isinstance(value, tir.Value):
            return value
        v = self._materialize_in(block, value, loc)
        v.add_alias(name)
        return v

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
        scan = _scan_jumps(st.body)
        if scan.breaks or scan.continues:
            raise self._err(
                st, "tl.static_range",
                "break/continue inside tl.static_range is not in the "
                "structured control-flow core (the loop unrolls at compile "
                "time; use tl.range for a runtime loop exit)")
        k = start
        while (step > 0 and k < stop) or (step < 0 and k > stop):
            self._bind(name, ConstVal(k))
            # a return inside the unrolled body lowers under the active
            # flag's guards like any statement (the remaining iterations
            # guard on the flag: they must not run after a return)
            self._lower_stmts(st.body)
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
        jumps = _scan_jumps(st.body)
        if jumps.returns or jumps.breaks:
            # a break/return inside the body needs the loop-exit channel:
            # the counted form lowers as the while form (the head test
            # `i < upper` ANDs the stop channel, so the loop exits at the
            # next head test after a break/return)
            self._lower_counted_as_while(st, loc, name, lower_i, upper_i,
                                         step_i, jumps)
            return
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
            else:
                v = self._fresh_channel_init(v, cname)
            preheader_inits[cname] = v
        node = tir.Loop(lower_i, upper_i, step_i, loc)
        self._push_block(node.body)
        self.symbols = dict(self.symbols)
        self.env.values = dict(self.env.values)
        self._bind(name, lower_i)
        for cname, init in preheader_inits.items():
            self._bind(cname, init)
        self._mark_region_runtime(assigned - {name})
        self._lower_stmts(st.body)
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
        # the shared loop close: drop channels the lowered body never
        # re-binds, give every final a region-visible definition, join
        live, joins = self._finish_loop_channels(node, loc, carried,
                                                 preheader_inits, body_syms)
        self._rebind_blockptrs_after_region(bp_names, body_syms, live,
                                            joins)

    # -- while -------------------------------------------------------------------
    def _lower_while(self, st: ast.While) -> None:
        if st.orelse:
            raise self._err(st, "while.else",
                            "while/else is not in the structured "
                            "control-flow core")
        loc = self._loc(st)
        jumps = _scan_jumps(st.body)
        # the condition may depend on names the body re-assigns (``j = 0``
        # before the loop, ``j < K`` as the test, ``j += 1`` inside): they
        # are runtime BEFORE the first fold attempt -- folding the test
        # against the pre-loop constant would decide ``while True`` from
        # the first iteration's value
        self._mark_region_runtime(self._assigned_names(st.body))
        cond = self.env.evaluate(st.test, self.source.path)
        if cond is not NOT_CONSTEXPR:
            if cond:
                if not (jumps.breaks or jumps.returns):
                    raise self._err(
                        st, "while",
                        "while True never terminates (no break exists in "
                        "the control-flow core)")
                # ``while True`` with a loop exit: the constant-true
                # condition rides the while form like any other (the stop
                # channel terminates the loop at the next head test)
                cond_v = self._emit(tir.Op.const(True, tir.INT1, loc), "tru")
            else:
                self.fold.record_branch(st, False, "orelse")
                return                  # zero-trip: the body never runs
        else:
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
        stop0 = self._emit(tir.Op.const(True, tir.INT1, loc), "go")
        self._lower_while_form(st, loc, cond_v, jumps, stop0,
                               induction=None)

    # -- the shared while-form builder ---------------------------------------
    def _lower_counted_as_while(self, st, loc, name, lower_i, upper_i,
                                step_i, jumps) -> None:
        """A counted range whose body contains a break/return, lowered as
        the while form: the head test ``i < upper`` ANDs the stop channel
        (the induction becomes an ordinary carried channel with the
        increment appended at the body end, exactly like the counted
        form's)."""
        cond0 = self._emit(tir.Op.cmp("cmp.lt", lower_i, upper_i, loc), "lpc")
        stop0 = self._emit(tir.Op.const(True, tir.INT1, loc), "go")
        self._lower_while_form(st, loc, cond0, jumps, stop0,
                               induction=(name, lower_i, upper_i, step_i))

    def _lower_while_form(self, st, loc, cond_v, jumps, stop0,
                          induction) -> None:
        """Build the while-form ``tir.Loop`` with carried values.

        ``induction`` is ``(name, lower, upper, step)`` for a converted
        counted range (None for a plain while).  The stop channel
        (break/return) and the active flag (return) ride as carried
        names; the condition re-evaluation at the body end is guarded by
        the stop channel when a loop exit can have fired (the source does
        not re-test the condition on a path that left the loop)."""
        snap = self._region_snapshot()
        # carried candidates: names the body assigns that are visible
        # before the loop (the condition rides first)
        assigned = self._assigned_names(st.body)
        assigned, bp_names = self._region_blockptr_state(assigned)
        preheader_inits: Dict[str, tir.Value] = {}
        for cname in sorted(assigned):
            if induction is not None and cname == induction[0]:
                continue        # the induction binds explicitly below
            if cname not in self.symbols:
                continue
            v = self.symbols[cname]
            if isinstance(v, BlockPtrVal):
                continue           # the derived term names carry it
            if isinstance(v, ConstVal):
                v = self._materialize_in(self._block, v, loc)
            else:
                v = self._fresh_channel_init(v, cname)
            preheader_inits[cname] = v
        stop_name = self._fresh_name("%loop.go")
        preheader_inits[stop_name] = stop0
        if jumps.returns:
            active = self.symbols.get(_RET_ACTIVE)
            if isinstance(active, tir.Value):
                preheader_inits[_RET_ACTIVE] = active
        node = tir.Loop(None, None, None, loc, cond=cond_v)
        cond_name = self._fresh_name("%while.cond")
        cond_v.add_alias(cond_name)      # the carried condition entry
        self._push_block(node.body)
        self.symbols = dict(self.symbols)
        self.env.values = dict(self.env.values)
        self._bind(cond_name, cond_v)
        if induction is not None:
            self._bind(induction[0], induction[1])
        for cname, init in preheader_inits.items():
            self._bind(cname, init)
        self._mark_region_runtime(assigned)
        self._loop_depth += 1
        self._loop_stop_stack.append(stop_name)
        try:
            self._lower_stmts(st.body)
            if induction is not None:
                name, lower_i, _upper_i, step_i = induction
                if self.symbols.get(name) is not lower_i:
                    raise self._err(
                        st, "for",
                        f"the loop body rebinds the induction name "
                        f"'{name}'; the induction is compiler-owned in the "
                        "counted form")
                # the induction increment (the channel's back-edge value)
                inc = self._emit(
                    tir.Op.binop("arith.add", lower_i, step_i, loc), "inc")
                self._bind(name, inc)
        finally:
            self._loop_depth -= 1
            self._loop_stop_stack.pop()
        # the condition re-evaluation over the body's final state, bound
        # to the carried cond name (the back edge carries it to the head);
        # guarded by the stop channel when a loop exit can have fired (a
        # while's test may carry effects -- the source does not re-test
        # it on a path that left the loop).  The converted counted form's
        # test ``i < upper`` is pure: no guard needed.
        stop_v = self.symbols.get(stop_name)
        needs_stop = jumps.returns > 0 or jumps.breaks > 0
        if induction is not None:
            name, lower_i, upper_i, step_i = induction
            ind_next = self.symbols.get(name)
            c = self._emit(tir.Op.cmp("cmp.lt", ind_next, upper_i, loc),
                           "lpc")
            if needs_stop and isinstance(stop_v, tir.Value):
                c = self._emit(tir.Op.binop("bit.and", c, stop_v, loc), "go")
            self._bind(cond_name, c)
        elif needs_stop and isinstance(stop_v, tir.Value):
            def then_fn():
                c = self._lower_cond_expr(st.test, loc)
                self._bind(cond_name, c)

            def else_fn():
                f = self._emit(tir.Op.const(False, tir.INT1, loc), "cf")
                self._bind(cond_name, f)

            self._emit_runtime_if(stop_v, loc, then_fn, else_fn)
        else:
            c = self._lower_cond_expr(st.test, loc)
            self._bind(cond_name, c)
        body_syms = dict(self.symbols)
        self._pop_block()
        self._region_restore(snap)

        carried = [(cond_name, cond_v)]
        if induction is not None:
            carried.append((induction[0], induction[1]))
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
        live, joins = self._finish_loop_channels(node, loc, carried,
                                                 preheader_inits, body_syms,
                                                 skip_bind=(cond_name,))
        self._rebind_blockptrs_after_region(bp_names, body_syms, live,
                                            joins)
        if jumps.returns and isinstance(self.symbols.get(_RET_ACTIVE),
                                        tir.Value):
            # a return can have fired inside: the post-loop statements
            # guard on the flag (the channel's join)
            self._ret_active = self.symbols[_RET_ACTIVE]

    def _lower_cond_expr(self, test, loc) -> tir.Value:
        """The loop condition as an i1 value (materializing a constexpr
        re-evaluation like ``while True``)."""
        c = self._lower_expr(test)
        if isinstance(c, ConstVal):
            c = self._materialize(c, loc)
        if not c.type.is_bool():
            c = self._emit_convert(c, tir.INT1, loc)
        return c

    # -- the shared loop close (T026) -----------------------------------------
    def _fresh_channel_init(self, v: tir.Value, cname: str) -> tir.Value:
        """A carried channel's init must not share its value with a name
        that stays loop-invariant: inside the body, uses of the INIT
        value denote the current iteration (the lowering's head-parameter
        override) -- ``t_cur = x`` before the loop would reinterpret
        every body use of ``x`` as the carried value.  A shared init gets
        a fresh identity copy (one value per meaning)."""
        if any(n != cname for n in v.aliases):
            return self._identity_value(self._block, v, self._loc_of(v))
        return v

    @staticmethod
    def _loc_of(v: tir.Value):
        return v.loc

    def _identity_value(self, block: tir.Block, value: tir.Value,
                        loc) -> tir.Value:
        """A fresh value equal to ``value``: the identity select
        ``where(true, v, v)`` (both branches the same value).  The passes
        keep it as a region-final binding (copyprop/LICM's protected set)
        while folding its ordinary uses; the lowering reinterprets its
        operand per-iteration under the head-parameter override."""
        saved = self._block
        self._block = block
        try:
            c = self._emit(tir.Op.const(True, tir.INT1, loc), "idc")
            if value.shape:
                target = tuple(tir.Extent(e.value, True)
                               for e in value.shape)
                c = self._emit(tir.Op.broadcast(c, target, loc), "idb")
            return self._emit(tir.Op.where(c, value, value, loc), "id")
        finally:
            self._block = saved

    def _collect_region_vids(self, block: tir.Block, out: set) -> None:
        """Every value vid defined inside a region (op results and nested
        region joins, transitively)."""
        for stmt in block.statements:
            if isinstance(stmt, tir.Op):
                out.update(r.vid for r in stmt.results)
            elif isinstance(stmt, tir.If):
                self._collect_region_vids(stmt.then, out)
                self._collect_region_vids(stmt.els, out)
                out.update(r.vid for r in stmt.join_results)
            elif isinstance(stmt, tir.Loop):
                self._collect_region_vids(stmt.body, out)
                out.update(r.vid for r in stmt.join_results)

    def _finish_loop_channels(self, node: tir.Loop, loc, carried,
                              preheader_inits, body_syms,
                              skip_bind=()):
        """The shared loop close: drop the channels the lowered body never
        re-binds (every assignment folded away -- the name keeps its outer
        binding), give every remaining final a definition the region
        replay can see (a ConstVal final materializes under the carried
        name; a final whose value is defined OUTSIDE the body -- a channel
        copy ``prev = cur`` or a re-assigned outer value -- gets the
        identity select), then bind the joins."""
        inits = dict(preheader_inits)
        body_defs: set = set()
        self._collect_region_vids(node.body, body_defs)
        live = []
        for cname, init in carried:
            if cname in inits and body_syms.get(cname) is inits[cname]:
                continue
            live.append((cname, init))
        node.carried = tuple(live)
        finals = []
        for cname, _init in live:
            final = body_syms[cname]
            if isinstance(final, ConstVal):
                final = self._materialize_in(node.body, final, loc)
                final.add_alias(cname)
            elif isinstance(final, tir.Value) and final.vid not in body_defs:
                final = self._identity_value(node.body, final, loc)
                final.add_alias(cname)
            finals.append(final)
        joins = []
        for (cname, _init), final in zip(live, finals):
            jv = tir.Value(final.type, final.shape, loc, name=cname)
            jv.add_alias(cname)
            joins.append(jv)
        node.join_results = tuple(joins)
        for (cname, _init), value in zip(live, joins):
            if cname in skip_bind:
                continue        # internal: not visible after the loop
            self._bind(cname, value)
        return live, joins

    # ------------------------------------------------------------------ exprs
    def _lower_expr(self, node: ast.expr) -> Union[tir.Value, ConstVal]:
        if isinstance(node, ast.Name):
            # the symbol's own binding FIRST: a name-bound constant keeps
            # its ``tensor_sem`` marker (the pinned visit_Assign to_tensor
            # rule -- the plain env fold would erase it and the constant
            # would stop participating in the promotion)
            if node.id in self.symbols:
                return self.symbols[node.id]
            folded = self.env.evaluate(node, self.source.path)
            if folded is not NOT_CONSTEXPR:
                return ConstVal(folded)
            raise self._err(node, node.id,
                            f"name '{node.id}' is not defined")
        folded = self.env.evaluate(node, self.source.path)
        if folded is not NOT_CONSTEXPR:
            return ConstVal(folded)
        if isinstance(node, ast.Constant):
            return ConstVal(node.value)
        if isinstance(node, ast.BinOp):
            return self._lower_binop(node)
        if isinstance(node, ast.UnaryOp):
            return self._lower_unary(node)
        if isinstance(node, ast.Compare):
            return self._lower_compare(node)
        if isinstance(node, ast.BoolOp):
            return self._lower_boolop(node)
        if isinstance(node, ast.IfExp):
            return self._lower_ifexp(node)
        if isinstance(node, ast.Call):
            return self._lower_call(node)
        if isinstance(node, ast.Attribute):
            # the pinned 2-D transposition attribute (``x.T``): the AST
            # visitor owns it in the reference too
            if node.attr == "T":
                base = self._lower_expr(node.value)
                return self._lower_transpose_attr(base, node)
            if node.attr == "shape":
                # ``x.shape`` is constexpr in the pinned language (block
                # extents are compile-time); fold it when every extent is
                # an integer and refuse (located) when one is symbolic
                base = self._lower_expr(node.value)
                return self._lower_shape_attr(base, node)
            raise self._err(
                node, f".{node.attr}",
                "attribute is not in the elementwise core (only compile-time "
                "dtype attributes fold)")
        if isinstance(node, ast.Subscript):
            return self._lower_subscript(node)
        if isinstance(node, (ast.Tuple, ast.List)):
            # a compile-time sequence folds element-wise (the reshape
            # shape ``(x.shape[0], 16)``: each element folds through the
            # lowering's attribute path -- ``x.shape`` is constexpr in
            # the pinned language, so a sequence of folded extents is a
            # compile-time sequence).  A runtime element declines (the
            # elementwise core never sees a runtime sequence).
            items = [self._lower_expr(e) for e in node.elts]
            if all(isinstance(i, ConstVal) for i in items):
                return ConstVal(tuple(i.value for i in items))
            raise self._err(
                node, type(node).__name__,
                "a runtime sequence is not in the elementwise core (a "
                "compile-time sequence of folded constants is)")
        raise self._err(node, type(node).__name__,
                        "expression is not in the elementwise core")

    # -- binary operations ---------------------------------------------------
    def _lower_binop(self, node: ast.BinOp) -> Union[tir.Value, ConstVal]:
        lhs = self._lower_expr(node.left)
        rhs = self._lower_expr(node.right)
        op = node.op
        loc = self._loc(node)
        hint = "bin"

        if isinstance(lhs, ConstVal) and isinstance(rhs, ConstVal):
            # two folded constants: constexpr arithmetic (the pinned
            # tracer folds a BinOp of two constexprs at trace time).  The
            # operands fold here when the env could not see them -- a
            # shape-derived extent (``16 // x.shape[1]``) whose operands
            # fold only through the lowering's attribute path.
            l, r = _py_scalar(lhs.value), _py_scalar(rhs.value)
            if isinstance(l, (int, float)) and isinstance(r, (int, float)):
                try:
                    folded = ConstexprEnv._binop(op, l, r)
                except (ZeroDivisionError, TypeError, ValueError,
                        OverflowError):
                    raise self._err(
                        node, type(op).__name__,
                        f"constexpr operation {l!r} "
                        f"{type(op).__name__} {r!r} is not defined") from None
                # a to_tensor'd operand (a name-bound constant) keeps the
                # result a rank-0 tensor of the folded value's type (the
                # pinned scalar rule: the tensor side types the result)
                return ConstVal(folded,
                                tensor_sem=(lhs.tensor_sem
                                            or rhs.tensor_sem))

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

    def _lower_boolop(self, node: ast.BoolOp) -> Union[tir.Value, ConstVal]:
        """Python ``and``/``or`` over runtime values, with the semantics
        the pinned Triton 3.8 pins for them (code_generator.visit_BoolOp
        + semantic.logical_and/logical_or):

        * the values evaluate IN ORDER (side effects execute even when a
          constexpr value short-circuits the decision);
        * a constexpr value short-circuits: a falsey ``and`` operand is
          the result, a truthy ``or`` operand is the result; every other
          constexpr drops out of the combination;
        * with no runtime value left, the final value is the result (the
          disjunction of falsey values / conjunction of truthy values);
        * the runtime values combine right-to-left pairwise through
          ``logical_and``/``logical_or`` -- the i1 (``&``/``|``) forms
          with the operand broadcast -- exactly the bitwise path the
          boundary conditions already use.
        """
        is_and = isinstance(node.op, ast.And)
        construct = f"'{'and' if is_and else 'or'}'"
        loc = self._loc(node)
        values: List[tir.Value] = []
        last = None
        for sub in node.values:
            v = self._lower_expr(sub)     # side effects execute, in order
            if isinstance(v, ConstVal):
                try:
                    truth = bool(_py_scalar(v.value))
                except Exception:                          # noqa: BLE001
                    truth = True
                if (not truth) and is_and:
                    return v              # a falsey and-operand is the result
                if truth and not is_and:
                    return v              # a truthy or-operand is the result
                # no effect on the combination: dropped
            else:
                values.append(v)
            last = v
        if not values:
            # every value was a non-short-circuiting constexpr: the final
            # value is the result
            assert last is not None
            return last
        while len(values) >= 2:
            rhs = values.pop()
            lhs = values.pop()
            values.append(self._logical_combine(lhs, rhs, loc, construct,
                                                is_and))
        return values[0]

    def _logical_combine(self, lhs: tir.Value, rhs: tir.Value, loc,
                         construct: str, is_and: bool) -> tir.Value:
        """``logical_and``/``logical_or`` over two runtime values: both
        operands must be i1 (the pinned bitcast to int1 accepts nothing
        wider), then the bitwise op with the operand broadcast."""
        for side in (lhs, rhs):
            if not side.type.is_bool():
                raise FrontendError(
                    self.source.path, loc.line, loc.col, construct,
                    f"logical {construct.strip(chr(39))} requires boolean "
                    f"operands, got {side.type!r} (the pinned Triton "
                    "bitcasts each operand to int1, which accepts only i1)")
        l, r, _t = self._binary_operands(lhs, rhs, loc)
        code = "bit.and" if is_and else "bit.or"
        return self._emit(tir.Op.binop(code, l, r, loc), "log")

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
        op = node.ops[0]
        if isinstance(op, (ast.Is, ast.IsNot)):
            # identity must have folded at specialization (``x is [not]
            # None`` on an argument's presence); typing the None literal
            # here was the T024 'literal' class -- refuse naming the
            # construct instead, never the literal's absent type
            raise self._err(
                node, "is" if isinstance(op, ast.Is) else "is not",
                "an identity comparison did not fold at specialization "
                "(only ``x is [not] None`` on an argument's presence "
                "folds; a runtime identity comparison is not in the "
                "elementwise core)")
        if isinstance(op, (ast.In, ast.NotIn)):
            raise self._err(
                node, "in" if isinstance(op, ast.In) else "not in",
                "membership tests are not in the elementwise core")
        lhs = self._lower_expr(node.left)
        rhs = self._lower_expr(node.comparators[0])
        loc = self._loc(node)
        l, r, t = self._binary_operands(lhs, rhs, loc, preserve_order=True)
        pred = {ast.Lt: "cmp.lt", ast.LtE: "cmp.le", ast.Gt: "cmp.gt",
                ast.GtE: "cmp.ge", ast.Eq: "cmp.eq",
                ast.NotEq: "cmp.ne"}.get(type(op))
        if pred is None:
            raise self._err(node, type(op).__name__,
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
        l, r = self._where_operands(x, y, loc, node)
        target, _, _ = fshapes.unify_pair(cond_v.shape, l.shape, loc)
        target, _, _ = fshapes.unify_pair(target, r.shape, loc)
        cond_b = self._broadcast_to(cond_v, target, loc)
        lb = self._broadcast_to(l, target, loc)
        rb = self._broadcast_to(r, target, loc)
        return self._emit(tir.Op.where(cond_b, lb, rb, loc), "sel")

    def _where_operands(self, x, y, loc, node):
        """The where/ifexp operand unification: the pinned semantic passes
        ``allow_lhs_ptr=allow_rhs_ptr=True``, so TWO pointers of one type
        select directly (the rng_dual target-pointer form); everything
        else goes through the arithmetic unification."""
        x_ptr = isinstance(x, tir.Value) and x.type.is_pointer()
        y_ptr = isinstance(y, tir.Value) and y.type.is_pointer()
        if x_ptr or y_ptr:
            if not (x_ptr and y_ptr):
                raise self._err(
                    node, "where",
                    "a pointer selects against a pointer (the pinned "
                    "where allows two pointers of one type, never a "
                    "pointer/value mix)")
            if x.type != y.type:
                raise self._err(
                    node, "where",
                    f"pointer types differ in the select: {x.type!r} vs "
                    f"{y.type!r}")
            return x, y
        l, r, _t = self._binary_operands(x, y, loc, preserve_order=True)
        return l, r

    # -- the pinned unification ------------------------------------------------
    def _binary_operands(self, lhs, rhs, loc,
                         div_or_mod: bool = False,
                         preserve_order: bool = False,
                         literal_participates: bool = False
                         ) -> Tuple[tir.Value, tir.Value, tir.Type]:
        """Pinned binary_op_type_checking_impl: literals become constants of
        the computation type, tensor operands get explicit converts, shapes
        unify with explicit broadcast ops.

        ``preserve_order`` keeps the source operand order (a comparison's
        predicate is not commutative: ``flag > 0`` must compare flag
        against the literal, never the literal against flag).

        ``literal_participates`` marks the constructs whose pinned form
        converts a scalar argument through ``to_tensor`` BEFORE the
        unification (``tl.maximum`` / ``tl.minimum``: the constexpr call
        argument becomes an fp32 rank-0 tensor and participates in the
        promotion).  A ConstVal carrying ``tensor_sem`` (a plain-assignment
        name binding) participates the same way in every binop; a source
        literal in a BinOp does not (the scalar rule of
        computation_type_impl)."""
        node = loc_node(loc)
        l_lit = isinstance(lhs, ConstVal)
        r_lit = isinstance(rhs, ConstVal)
        l_sem = l_lit and (literal_participates or lhs.tensor_sem)
        r_sem = r_lit and (literal_participates or rhs.tensor_sem)
        if l_lit and r_lit:
            # two folded constants (e.g. tl.where(cond, 1.0, 0.0)): the
            # expression did not fold because the *shape* comes from
            # elsewhere; both become constants of their common
            # computation type.  A to_tensor'd side participates with its
            # own type (a source literal does not).
            l_value, r_value = _py_scalar(lhs.value), _py_scalar(rhs.value)
            for v in (l_value, r_value):
                if isinstance(v, (DTypeValue, TypeObject)):
                    raise self._err(
                        node, "binary op",
                        "a dtype value cannot participate in arithmetic")
            try:
                l_ty = ftypes.literal_type(l_value)
                r_ty = ftypes.literal_type(r_value)
                comp = ftypes.computation_type(l_ty, not l_sem, r_ty,
                                               not r_sem, div_or_mod)
            except ftypes.TypeRuleError as exc:
                raise self._err(node, "binary op", exc.message)
            l = self._emit(tir.Op.const(l_value, comp, loc), "lit")
            r = self._emit(tir.Op.const(r_value, comp, loc), "lit")
            return self._broadcast_pair(l, r, loc)
        if l_lit or r_lit:
            lit, ten = (lhs, rhs) if l_lit else (rhs, lhs)
            lit_sem = l_sem if l_lit else r_sem
            lit_value = _py_scalar(lit.value)
            if isinstance(lit_value, (DTypeValue, TypeObject)):
                raise self._err(
                    node, "binary op",
                    "a dtype value cannot participate in arithmetic")
            try:
                lit_ty = ftypes.literal_type(lit_value)
            except ftypes.TypeRuleError as exc:
                raise self._err(node, "literal", exc.message)
            if lit_sem:
                # the pinned to_tensor form: the scalar is a rank-0
                # tensor of its own type and participates in the
                # promotion (computation_type over two tensor types; the
                # scalar range/negative checks do not apply)
                try:
                    comp = ftypes.computation_type(
                        lit_ty, False, ten.type, False, div_or_mod)
                except ftypes.TypeRuleError as exc:
                    raise self._err(node, "binary op", exc.message)
            else:
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
        index forms with return_indices=True, tl.split, tl.broadcast,
        tl.swizzle2d); None when the call is single-result (the caller
        falls back to the plain path)."""
        construct = self._callee_construct(node)
        if construct in ("tl.split", "tl.broadcast", "tl.swizzle2d"):
            self._check_construct(construct, node)
            bound, provided = self._bind_call_args(construct, node)
            for required in _REQUIRED_PARAMS.get(construct, ()):
                if required not in provided:
                    raise self._err(
                        node, construct,
                        f"missing required parameter {required!r}")
            if construct == "tl.split":
                return self._lower_tl_split(bound, node, self._loc(node),
                                            construct)
            if construct == "tl.broadcast":
                return self._lower_tl_broadcast(bound, node, self._loc(node),
                                                construct)
            return self._lower_tl_swizzle2d(bound, node, self._loc(node))
        if construct in ("tl.philox", "tl.rand4x", "tl.randint4x",
                         "tl.randn4x"):
            # the 4x RNG family and the philox primitive produce four
            # values (the tuple-unpack forms are the legal uses)
            self._check_construct(construct, node)
            bound, provided = self._bind_call_args(construct, node)
            for required in _REQUIRED_PARAMS.get(construct, ()):
                if required not in provided:
                    raise self._err(
                        node, construct,
                        f"missing required parameter {required!r}")
            handler = _CONSTRUCT_HANDLERS[construct]
            values = handler(self, bound, node, self._loc(node))
            assert isinstance(values, list)
            return values
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
        if construct in _MULTI_RESULT_CONSTRUCTS and \
                construct not in ("tl.max", "tl.min"):
            raise self._err(
                node, construct,
                "the construct produces multiple values; unpack them into "
                "names (a, b = ...)")
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
        # a parameter named ``*x`` is variadic: it absorbs every remaining
        # positional argument (tl.reshape(x, (n, m)) and tl.reshape(x, n, m)
        # bind the same construct)
        variadic = next((n for n in names if n.startswith("*")), None)
        for i, arg in enumerate(node.args):
            if variadic is not None and i >= names.index(variadic):
                bound.setdefault(variadic, [])
                if not isinstance(bound[variadic], list):
                    raise self._err(
                        node, construct,
                        f"parameter {variadic!r} given twice")
                bound[variadic].append(arg)
                continue
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
        l, r = self._where_operands(x, y, loc, node)
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
            # a runtime scalar value splats over the shape (the pinned
            # semantic; the T012 layout lane's block-broadcast construct)
            v = self._lower_expr(args["value"])
            if isinstance(v, ConstVal):
                raise self._err(
                    node, "tl.full",
                    "full with a runtime value is not in the elementwise "
                    "core (the value must be compile-time)")
            if v.rank != 0:
                raise self._err(
                    node, "tl.full",
                    "full with a block value is not the splat form")
            v = self._convert_if_needed(v, dtype, loc)
            return self._broadcast_to(v, tir.real_shape(shape), loc)
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

    def _lower_tl_static_assert(self, args, node, loc):
        """tl.static_assert(cond, msg): the compile-time assertion (the
        pinned builtin).  A constexpr-true condition emits nothing; a
        constexpr-false condition is a located refusal carrying the
        message; a runtime condition cannot be checked at compile time
        and is a located refusal (never a silent no-op)."""
        cond = self.env.evaluate(args["cond"], self.source.path)
        if cond is NOT_CONSTEXPR:
            raise self._err(
                node, "tl.static_assert",
                "tl.static_assert requires a compile-time condition (a "
                "runtime condition cannot be checked at compile time)")
        if not cond:
            msg = ""
            if "msg" in args:
                m = self.env.evaluate(args["msg"], self.source.path)
                if m is not NOT_CONSTEXPR and isinstance(m, str):
                    msg = m
            raise self._err(
                node, "tl.static_assert",
                f"static_assert failed{': ' + msg if msg else ''} "
                f"(condition is {cond!r})")
        return ConstVal(None)

    def _lower_tl_dtype(self, args, node, loc) -> ConstVal:
        """tl.dtype(name): the pinned dtype registry constructor -- a
        constexpr dtype value from its name (the corpus's
        ``tl.dtype(f'uint{nbits}')`` order-key form).  The result flows
        as any dtype constant: a cast target, tl.full's dtype= operand."""
        value = self.env.evaluate(args["name"], self.source.path)
        if value is NOT_CONSTEXPR:
            raise self._err(
                node, "tl.dtype",
                "tl.dtype(name) requires a compile-time dtype name")
        if isinstance(value, DTypeValue):
            return ConstVal(value)
        if not isinstance(value, str):
            raise self._err(
                node, "tl.dtype",
                f"tl.dtype(name) requires a dtype name string, got "
                f"{value!r}")
        try:
            ty = ftypes.dtype_by_name(value)
        except ftypes.TypeRuleError as exc:
            raise self._err(node, "tl.dtype", exc.message) from None
        return ConstVal(DTypeValue(ty))

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
        <32-bit type to fp32/int32.  A bool block is pinned int1 (an
        unsigned 1-bit integer): sum(uint32) and max/min(int32) (probed
        against the pinned tracer).  ``dtype=`` overrides (the input
        converts before the reduction)."""
        ty = value.type
        if dtype_arg is not None:
            target = self._constexpr_dtype(dtype_arg, node, construct)
            return self._convert_if_needed(value, target, loc)
        target = ty
        if kind == "sum":
            if (ty.is_int() or ty.is_bool()) and ty.bitwidth() < 32:
                if ty.is_bool():
                    target = tir.UINT32     # pinned: int1 is unsigned
                else:
                    target = tir.INT32 if ty.is_int_signed() else tir.UINT32
        elif kind in ("max", "min", "argmax", "argmin"):
            if ty.name == "bf16":
                target = tir.FLOAT32
            elif ty.bitwidth() < 32:
                if ty.is_float():
                    target = tir.FLOAT32
                elif ty.is_int() or ty.is_bool():
                    # pinned max/min convert every <32-bit non-float to
                    # the SIGNED int32
                    target = tir.INT32
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
        """tl.softmax: the pinned standard.py composition, declared as
        SOFTMAX_COMPOSITE in a100c/plan/stages.py -- ``z = x -
        max(x, dim, keep_dims); num = exp(z); den = sum(num, dim,
        keep_dims); fdiv(num, den)`` (the stable max subtraction; the
        ieee_rounding flag selects the division flavour and both map to
        the target's exactly-rounded vfdiv)."""
        from a100c.plan import stages as stages_mod
        x = self._reduction_operand(args, node, loc, construct)
        if not x.type.is_float():
            raise self._err(
                node, construct,
                f"tl.softmax requires a floating block (the exp "
                f"dependency's pinned _check_dtype), got {x.type!r}")
        if x.type.bitwidth() < 32:
            # the pinned composition promotes through its own max
            # reduction (standard.max: bf16 -> fp32, then every <32-bit
            # float -> fp32), so ``z = x - max(x)`` and every later stage
            # is fp32 and exp's _check_dtype holds; the RESULT is fp32
            # for a 16-bit input (probed against the pinned tracer)
            x = self._emit_convert(x, tir.FLOAT32, loc)
        rank = x.rank
        if rank != 1:
            raise self._err(
                node, construct,
                f"tl.softmax in this lane lowers a rank-1 block (the "
                f"keep_dims broadcast back), got rank {rank}")
        dim = 0
        if "dim" in args:
            d = py_scalar(self.env.evaluate(args["dim"], self.source.path))
            if d is not NOT_CONSTEXPR:
                if isinstance(d, bool) or not isinstance(d, int) \
                        or not 0 <= d < rank:
                    raise self._err(
                        node, construct,
                        f"tl.softmax dim {d!r} outside 0..{rank - 1}")
                dim = d
        keep_dims = False
        if "keep_dims" in args:
            kd = self.env.evaluate(args["keep_dims"], self.source.path)
            if kd is not NOT_CONSTEXPR:
                keep_dims = bool(kd)
        if not keep_dims:
            # the composition needs the broadcastable keep_dims form
            # (extent-1 reduced axes); a non-keep_dims result reshapes
            # back at the end
            keep_dims = True
        identity = stages_mod.identity_for("max", x.type)
        max_op = tir.Op.reduce(x, "max", (dim,), keep_dims, identity,
                               loc=loc)
        self._emit(max_op, "smx")
        l, r, _t = self._binary_operands(
            x, max_op.results[0], loc, preserve_order=True)
        z = self._emit(tir.Op.binop("arith.sub", l, r, loc), "sub")
        num = self._emit(tir.Op.math_unary("math.exp", z, loc), "exp")
        sum_ident = stages_mod.identity_for("sum", x.type)
        den_op = tir.Op.reduce(num, "sum", (dim,), True, sum_ident,
                               loc=loc)
        self._emit(den_op, "sms")
        nl, nr, _t2 = self._binary_operands(
            num, den_op.results[0], loc, preserve_order=True)
        out = self._emit(tir.Op.binop("arith.fdiv", nl, nr, loc), "div")
        if not (rank and out.rank == rank and dim == 0):
            raise self._err(node, construct,
                            "the softmax composition changed the rank")
        return out

    # -- T013: special math functions ----------------------------------------

    def _lower_math_unary(self, args: Dict[str, ast.expr], node: ast.Call,
                          loc, construct: str) -> tir.Value:
        """exp/exp2/log/log2/sin/cos/erf/sqrt/sqrt_rn/rsqrt/floor/ceil: the
        pinned ``_check_dtype`` admits fp32/fp64 blocks only -- a 16-bit
        operand is a located type error (never a silent promotion), and
        fp64 is the internal-compute width (position_quantize's phase
        reduction)."""
        code = _MATH_UNARY_CODES[construct]
        x = self._lower_expr(args["x"])
        if isinstance(x, ConstVal):
            # the pinned to_tensor makes a rank-0 tensor and the math op
            # runs on it (igamma's tl.log(pi) on a Python float): the
            # scalar path lowers rank-0 math through the vector splat
            v = _py_scalar(x.value)
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise self._err(
                    node, construct,
                    f"a {construct} operand must be numeric, got {v!r}")
            x = self._materialize(ConstVal(float(v)), loc,
                                  target=tir.FLOAT32)
        if not x.type.is_float():
            raise self._err(
                node, construct,
                f"{construct} requires a floating block (the pinned "
                f"_check_dtype admits fp32/fp64), got {x.type!r}")
        if x.type.bitwidth() not in (32, 64):
            raise self._err(
                node, construct,
                f"{construct} requires fp32 or fp64 operands (the pinned "
                f"_check_dtype); 16-bit compute goes through the fp32 "
                f"lanes, got {x.type!r}")
        return self._emit(tir.Op.math_unary(code, x, loc), "mth")

    def _lower_tl_abs(self, args: Dict[str, ast.expr], node: ast.Call,
                      loc, construct: str) -> tir.Value:
        """tl.abs: fabs on floats, iabs on signed integers, the identity
        on unsigned (the pinned dispatch)."""
        x = self._lower_expr(args["x"])
        if isinstance(x, ConstVal):
            v = _py_scalar(x.value)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                return ConstVal(abs(v))
            raise self._err(node, construct,
                            f"cannot abs constexpr {v!r}")
        if x.type.is_float() or (x.type.is_int() and x.type.is_int_signed()):
            return self._emit(tir.Op.abs_value(x, loc), "abs")
        if x.type.is_int():
            return x                  # unsigned: the pinned identity
        raise self._err(
            node, construct,
            f"tl.abs requires a numeric block, got {x.type!r}")

    def _lower_tl_maxmin_bin(self, args: Dict[str, ast.expr],
                             node: ast.Call,
                             loc, construct: str) -> tir.Value:
        """tl.maximum / tl.minimum: the propagate_nan policy selects the op
        code -- NONE (the default) is the maxnum form (the other operand
        on NaN), ALL propagates a quiet NaN; integers take their own
        signedness-carrying forms."""
        propagate_nan = self._propagate_nan(args, node, construct)
        x = self._lower_expr(args["x"])
        y = self._lower_expr(args["y"])
        if isinstance(x, ConstVal) and isinstance(y, ConstVal) \
                and not (x.tensor_sem or y.tensor_sem):
            raise self._err(
                node, construct,
                "two constexpr operands have no block lanes (Python "
                "min/max folds at specialization)")
        # the pinned core.maximum/minimum convert each argument through
        # to_tensor BEFORE the unification: a scalar argument is an fp32
        # (or integer) rank-0 tensor that participates in the promotion
        # (``tl.maximum(a_fp16, 1e-12)`` is fp32)
        l, r, t = self._binary_operands(x, y, loc,
                                        literal_participates=True)
        if t.is_bool():
            raise self._err(
                node, construct,
                f"boolean {construct} is not in the pinned semantics "
                "(Unexpected dtype)")
        if t.is_float():
            base = ("maximum" if construct == "tl.maximum"
                    else "minimum") if propagate_nan \
                else ("maxnum" if construct == "tl.maximum" else "minnum")
            code = f"arith.{base}f"
        elif t.is_int():
            sfx = "si" if t.is_int_signed() else "ui"
            code = ("arith.max" if construct == "tl.maximum"
                    else "arith.min") + sfx
        else:
            raise self._err(
                node, construct,
                f"{construct} requires numeric operands, got {t!r}")
        return self._emit(tir.Op.maxmin(code, l, r, loc), "mm")

    def _propagate_nan(self, args: Dict[str, ast.expr], node,
                       construct: str) -> bool:
        """The propagate_nan parameter (constexpr; the pinned default is
        PropagateNan.NONE)."""
        if "propagate_nan" not in args:
            return False
        v = self.env.evaluate(args["propagate_nan"], self.source.path)
        if v is NOT_CONSTEXPR:
            raise self._err(
                node, construct,
                "propagate_nan must be a compile-time value "
                "(tl.PropagateNan.ALL / tl.PropagateNan.NONE)")
        v = _py_scalar(v)
        if isinstance(v, bool):
            return v
        text = str(v)
        if "ALL" in text or v is True:
            return True
        if "NONE" in text or v is False or v is None:
            return False
        raise self._err(
            node, construct,
            f"propagate_nan {v!r} is neither NONE nor ALL")

    def _lower_tl_clamp(self, args: Dict[str, ast.expr], node: ast.Call,
                        loc, construct: str) -> tir.Value:
        """tl.clamp: the minimum(maximum(x, min), max) composition at the
        unified type, with the propagate_nan policy carried by both
        maxmin ops (the floating-only pinned semantic)."""
        propagate_nan = self._propagate_nan(args, node, construct)
        x = self._lower_expr(args["x"])
        lo = self._lower_expr(args["min"])
        hi = self._lower_expr(args["max"])
        # the pinned unification order: (min, max), then (x, min), then
        # (x, max)
        lo_v, hi_v, _t = self._binary_operands(lo, hi, loc,
                                               preserve_order=True)
        x1, lo_b, t = self._binary_operands(x, lo_v, loc,
                                            preserve_order=True)
        x2, hi_b, t2 = self._binary_operands(x1, hi_v, loc,
                                             preserve_order=True)
        if not t.is_float():
            raise self._err(
                node, construct,
                f"tl.clamp requires floating operands (the pinned "
                f"semantic), got {t!r}")
        sfx = "f"
        base_hi = ("maximum" if propagate_nan else "maxnum")
        base_lo = ("minimum" if propagate_nan else "minnum")
        inner = self._emit(tir.Op.maxmin(f"arith.{base_hi}{sfx}",
                                         x2, lo_b, loc), "clp")
        return self._emit(tir.Op.maxmin(f"arith.{base_lo}{sfx}",
                                        inner, hi_b, loc), "clp")

    def _lower_tl_fma(self, args: Dict[str, ast.expr], node: ast.Call,
                      loc, construct: str) -> tir.Value:
        """tl.fma: x * y + z with one rounding; the pinned legalization
        chain unifies x/y, then z with each.

        The pinned fma runs ``to_tensor`` on every operand *before* the
        pairwise legalization, so a Python float scalar participates as a
        full fp32 value (not as a non-participating scalar): fma(KC, x2,
        K) with an fp16 x2 legalizes to fp32, unlike the plain binop
        ``x * KC`` which stays fp16.  Materialize literal operands as
        constants of their literal type first (T016: the gelu exp2
        operand arrived fp16 and the pinned _check_dtype refused it)."""
        x = self._fma_operand(args["x"], node, loc)
        y = self._fma_operand(args["y"], node, loc)
        z = self._fma_operand(args["z"], node, loc)
        if all(isinstance(v, ConstVal) for v in (x, y, z)):
            raise self._err(
                node, construct,
                "three constexpr operands have no block lanes")
        x1, y1, t = self._binary_operands(x, y, loc)
        z1, x2, t2 = self._binary_operands(z, x1, loc,
                                           preserve_order=True)
        # y1 is already at x1's type; re-unify with the (possibly
        # widened) x2 shape (z's shape may have broadcast the pair)
        target, _, _ = fshapes.unify_pair(x2.shape, y1.shape, loc)
        target2, _, _ = fshapes.unify_pair(target, z1.shape, loc)
        xb = self._broadcast_to(x2, target2, loc)
        yb = self._broadcast_to(y1, target2, loc)
        zb = self._broadcast_to(z1, target2, loc)
        if not t.is_float():
            raise self._err(
                node, construct,
                f"tl.fma requires floating operands, got {t!r}")
        return self._emit(tir.Op.fma(xb, yb, zb, loc), "fma")

    def _fma_operand(self, node: ast.expr, call: ast.Call, loc):
        """One tl.fma operand: a literal becomes a constant of its own
        literal type (the pinned to_tensor-then-legalize order); a
        runtime value passes through untouched."""
        value = self._lower_expr(node)
        if not isinstance(value, ConstVal):
            return value
        raw = py_scalar(value.value)
        if isinstance(raw, (DTypeValue, TypeObject)):
            raise self._err(
                call, "tl.fma",
                "a dtype value cannot participate in arithmetic")
        try:
            lit_ty = ftypes.literal_type(raw)
        except ftypes.TypeRuleError as exc:
            raise self._err(call, "tl.fma", exc.message) from None
        return self._emit(tir.Op.const(raw, lit_ty, loc), "lit")

    def _lower_tl_div_rn(self, args: Dict[str, ast.expr], node: ast.Call,
                         loc, construct: str) -> tir.Value:
        """tl.div_rn: the precise (round-to-nearest) division; fp32 only
        per the pinned _check_dtype."""
        x = self._lower_expr(args["x"])
        y = self._lower_expr(args["y"])
        if isinstance(x, ConstVal) and isinstance(y, ConstVal):
            raise self._err(
                node, construct,
                "two constexpr operands have no block lanes")
        l, r, t = self._binary_operands(x, y, loc, preserve_order=True)
        if not t.is_float() or t.bitwidth() != 32:
            raise self._err(
                node, construct,
                f"tl.div_rn requires fp32 operands (the pinned "
                f"_check_dtype), got {t!r}")
        return self._emit(tir.Op.binop("arith.div_rn", l, r, loc), "dvr")

    def _lower_tl_sigmoid(self, args: Dict[str, ast.expr], node: ast.Call,
                          loc, construct: str) -> tir.Value:
        """tl.sigmoid: the pinned standard.py composition ``1 / (1 +
        exp(-x))`` at the operand's float width."""
        x = self._lower_expr(args["x"])
        if isinstance(x, ConstVal):
            raise self._err(
                node, construct,
                "a compile-time operand has no block lanes")
        if not x.type.is_float() or x.type.bitwidth() not in (32, 64):
            raise self._err(
                node, construct,
                f"tl.sigmoid requires an fp32/fp64 block (the exp "
                f"dependency's pinned _check_dtype), got {x.type!r}")
        neg = self._emit(tir.Op.unary("arith.fneg", x, loc), "neg")
        e = self._emit(tir.Op.math_unary("math.exp", neg, loc), "exp")
        one, denom, _t = self._binary_operands(ConstVal(1), e, loc,
                                               preserve_order=True)
        s = self._emit(tir.Op.binop("arith.add", one, denom, loc), "add")
        one2, s2, _t2 = self._binary_operands(ConstVal(1), s, loc,
                                              preserve_order=True)
        return self._emit(tir.Op.binop("arith.fdiv", one2, s2, loc), "div")

    def _lower_tl_arith_fn(self, args: Dict[str, ast.expr], node, loc,
                           construct: str) -> tir.Value:
        """tl.add / tl.sub / tl.mul: the explicit function forms of the
        AST operators (position_quantize's spelled-out arithmetic) -- the
        same pinned unification and the same TIR binops."""
        x = self._lower_expr(args["x"])
        y = self._lower_expr(args["y"])
        code = {"tl.add": "arith.add", "tl.sub": "arith.sub",
                "tl.mul": "arith.mul"}[construct]
        l, r, _t = self._binary_operands(x, y, loc, preserve_order=True)
        return self._emit(tir.Op.binop(code, l, r, loc), "bin")

    # -- T013: bit-exact RNG ---------------------------------------------------

    def _rng_rounds(self, args: Dict[str, ast.expr], node, construct) -> int:
        """The n_rounds constexpr (the pinned default is 10)."""
        if "n_rounds" not in args:
            return 10
        v = py_scalar(self.env.evaluate(args["n_rounds"], self.source.path))
        if v is NOT_CONSTEXPR or isinstance(v, bool) \
                or not isinstance(v, int) or v < 1:
            raise self._err(
                node, construct,
                f"n_rounds must be a positive compile-time integer, got "
                f"{v!r}")
        return v

    def _lower_tl_philox(self, args: Dict[str, ast.expr], node, loc,
                         construct: str) -> List[tir.Value]:
        """tl.philox(seed, c0, c1, c2, c3): the pinned random.py lowering
        -- the seed converts to uint64, splits into the (lo, hi) key
        words, the counters bitcast to the counter width; the rounds run
        in the lowering.  The 32-bit counter family only (the corpus's
        philox callers; 64-bit counters are a located refusal)."""
        rounds = self._rng_rounds(args, node, construct)
        seed_lo, seed_hi = self._philox_key(args["seed"], node, loc,
                                            construct)
        counters = []
        for name in ("c0", "c1", "c2", "c3"):
            c = self._philox_counter(args[name], node, loc, construct, name)
            counters.append(c)
        # the pinned philox_impl broadcasts its counter words against
        # each other (a scalar c1 against the block c0 -- the randint
        # kernels' form): unify the extents here (rank-0 words broadcast;
        # a genuine extent disagreement is a located diagnostic, never a
        # silent stretch)
        target = counters[0].shape
        for c in counters[1:]:
            try:
                target, _, _ = fshapes.unify_pair(target, c.shape, loc)
            except fshapes.ShapeError as exc:
                raise self._err(
                    node, construct,
                    f"the philox counter words cannot unify: {exc.message}")
        unified = [self._broadcast_to(c, target, loc) for c in counters]
        op = tir.Op.philox(seed_lo, seed_hi, *unified, rounds, loc)
        self._block.statements.append(op)
        for i, r in enumerate(op.results):
            r.name = self._fresh_name(f"phx{i}")
        return list(op.results)

    def _philox_key(self, seed_expr: ast.expr, node, loc,
                    construct: str) -> Tuple[tir.Value, tir.Value]:
        """The (k0, k1) key words from the seed: to_tensor -> uint64 ->
        (lo 32 bits, hi 32 bits), exactly the pinned chain."""
        seed = self._lower_expr(seed_expr)
        if isinstance(seed, ConstVal):
            v = _py_scalar(seed.value)
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise self._err(
                    node, construct,
                    f"the philox seed must be an integer, got {v!r}")
            seed = self._emit(tir.Op.const(int(v), tir.INT64, loc), "sd")
        if not seed.type.is_int():
            raise self._err(
                node, construct,
                f"the philox seed must be an integer (the pinned "
                f"static_assert), got {seed.type!r}")
        if seed.shape != ():
            raise self._err(
                node, construct,
                "a block seed is not in this lane (the corpus seeds are "
                "scalars; the key words stay rank-0 across the rounds)")
        if seed.type != tir.UINT64:
            seed = self._emit_convert(seed, tir.UINT64, loc)
        # lo = low 32 bits of the uint64 seed; hi = (seed >>u 32)'s low 32
        lo32 = self._emit_convert(seed, tir.UINT32, loc)
        sh_l, sh_r, _t = self._binary_operands(
            seed, ConstVal(32), loc, preserve_order=True)
        shifted = self._emit(tir.Op.binop("bit.lshr", sh_l, sh_r, loc),
                             "shr")
        hi32 = self._emit_convert(shifted, tir.UINT32, loc)
        return lo32, hi32

    def _philox_counter(self, expr: ast.expr, node, loc, construct: str,
                        name: str) -> tir.Value:
        """One counter word: a 32-bit integer block bitcast to uint32
        (the pinned ``.to(int_dtype, bitcast=True)``)."""
        c = self._lower_expr(expr)
        if isinstance(c, ConstVal):
            v = _py_scalar(c.value)
            if isinstance(v, bool) or not isinstance(v, int):
                raise self._err(
                    node, construct,
                    f"the philox counter {name} must be an integer, got "
                    f"{v!r}")
            c = self._emit(tir.Op.const(v, tir.INT32, loc), name)
        if not c.type.is_int():
            raise self._err(
                node, construct,
                f"the philox counter {name} must be an integer block, "
                f"got {c.type!r}")
        if c.type.bitwidth() != 32:
            raise self._err(
                node, construct,
                f"the philox counter {name} must be 32-bit (the 64-bit "
                f"counter family is a located refusal; the corpus's "
                f"callers are all uint32), got {c.type!r}")
        if c.type == tir.UINT32:
            return c
        return self._emit(tir.Op.bitcast(c, tir.UINT32, loc), "bc")

    def _randint4x_values(self, args: Dict[str, ast.expr], node, loc,
                          construct: str) -> List[tir.Value]:
        """The randint4x desugar: counter = (offset_lo, offset_hi, 0, 0)
        with the offset's low/high words per the pinned split (a 32-bit
        offset has hi = 0), then philox."""
        rounds = self._rng_rounds(args, node, construct)
        # the surface's parameter name: "offset" (rand/randn/randint and
        # the 4x int/normal forms) or "offsets" (tl.rand4x)
        offset = self._lower_expr(args.get("offsets", args.get("offset")))
        if isinstance(offset, ConstVal):
            v = _py_scalar(offset.value)
            if isinstance(v, bool) or not isinstance(v, int):
                raise self._err(
                    node, construct,
                    f"the offset must be an integer block, got {v!r}")
            offset = self._emit(tir.Op.const(v, tir.INT32, loc), "off")
        if not offset.type.is_int():
            raise self._err(
                node, construct,
                f"the offset must be an integer block, got "
                f"{offset.type!r}")
        if offset.rank == 0:
            raise self._err(
                node, construct,
                "the offset must be a block (a scalar offset has no "
                "lanes to draw)")
        width = offset.type.bitwidth()
        lo = self._emit_convert(offset, tir.UINT32, loc)
        if width > 32:
            code = "bit.lshr" if not offset.type.is_int_signed() \
                else "bit.ashr"
            sh_l, sh_r, _t = self._binary_operands(
                offset, ConstVal(32), loc, preserve_order=True)
            shifted = self._emit(
                tir.Op.binop(code, sh_l, sh_r, loc), "shr")
            hi = self._emit_convert(shifted, tir.UINT32, loc)
        else:
            hi = self._emit(tir.Op.zeros(
                tir.real_shape([e.value for e in offset.shape]),
                tir.UINT32, loc), "z")
        # keep the low word at the offset's own shape (hi may be a zeros
        # block of the same extents)
        shape = lo.shape
        hi = self._broadcast_to(hi, shape, loc)
        zero = self._emit(tir.Op.zeros(
            tir.real_shape([e.value for e in shape]), tir.UINT32, loc), "z")
        seed_lo, seed_hi = self._philox_key(args["seed"], node, loc,
                                            construct)
        op = tir.Op.philox(seed_lo, seed_hi, lo, hi, zero, zero, rounds,
                           loc)
        self._block.statements.append(op)
        for i, r in enumerate(op.results):
            r.name = self._fresh_name(f"ri{i}")
        return list(op.results)

    def _rng_uniform(self, word: tir.Value, loc) -> tir.Value:
        """uint_to_uniform_float: bitcast to int32, ``where(x < 0, ~x, x)``
        then ``x * 4.6566127342e-10`` -- every step the pinned op, so the
        result is bit-exact against the reference vectors."""
        x = self._emit(tir.Op.bitcast(word, tir.INT32, loc), "bc")
        zero = self._emit(tir.Op.const(0, tir.INT32, loc), "z")
        zero_b = self._broadcast_to(zero, x.shape, loc)
        neg = self._emit(tir.Op.cmp("cmp.lt", x, zero_b, loc), "lt")
        inv = self._emit(tir.Op.unary("bit.invert", x, loc), "inv")
        pos = self._emit(tir.Op.where(neg, inv, x, loc), "sel")
        l, r, _t = self._binary_operands(pos, ConstVal(4.6566127342e-10),
                                         loc)
        return self._emit(tir.Op.binop("arith.mul", l, r, loc), "unf")

    def _lower_tl_rand(self, args: Dict[str, ast.expr], node, loc,
                       construct: str) -> tir.Value:
        """tl.rand: uniform(randint(seed, offset)) -- U(0, 1) fp32."""
        words = self._randint4x_values(args, node, loc, construct)
        return self._rng_uniform(words[0], loc)

    def _lower_tl_randint(self, args: Dict[str, ast.expr], node, loc,
                          construct: str) -> tir.Value:
        """tl.randint: the first philox word (a uint32 block; the consumer
        converts or bitcasts)."""
        words = self._randint4x_values(args, node, loc, construct)
        return words[0]

    def _rng_pair_normal(self, u1: tir.Value, u2: tir.Value,
                         loc) -> Tuple[tir.Value, tir.Value]:
        """pair_uniform_to_normal: the pinned Box-Muller pair -- ``u1 =
        maximum(1e-7, u1); th = 6.283185307179586 * u2; r = sqrt(-2.0 *
        log(u1)); (r * cos(th), r * sin(th))``."""
        one, u1v, _t = self._binary_operands(ConstVal(1.0e-7), u1, loc,
                                             preserve_order=True)
        u1m = self._emit(tir.Op.maxmin("arith.maxnumf", one, u1v, loc),
                         "mm")
        th_l, th_r, _t2 = self._binary_operands(
            ConstVal(6.283185307179586), u2, loc, preserve_order=True)
        th = self._emit(tir.Op.binop("arith.mul", th_l, th_r, loc), "mul")
        ln = self._emit(tir.Op.math_unary("math.log", u1m, loc), "log")
        neg2_l, neg2_r, _t3 = self._binary_operands(
            ConstVal(-2.0), ln, loc, preserve_order=True)
        arg = self._emit(tir.Op.binop("arith.mul", neg2_l, neg2_r, loc),
                         "mul")
        r = self._emit(tir.Op.math_unary("math.sqrt", arg, loc), "sqrt")
        c = self._emit(tir.Op.math_unary("math.cos", th, loc), "cos")
        s = self._emit(tir.Op.math_unary("math.sin", th, loc), "sin")
        r_l, c_r, _t4 = self._binary_operands(r, c, loc)
        s_l, s_r, _t5 = self._binary_operands(r, s, loc)
        n1 = self._emit(tir.Op.binop("arith.mul", r_l, c_r, loc), "mul")
        n2 = self._emit(tir.Op.binop("arith.mul", s_l, s_r, loc), "mul")
        return n1, n2

    def _lower_tl_randn(self, args: Dict[str, ast.expr], node, loc,
                        construct: str) -> tir.Value:
        """tl.randn: the first normal of the (u1, u2) Box-Muller pair."""
        words = self._randint4x_values(args, node, loc, construct)
        u1 = self._rng_uniform(words[0], loc)
        u2 = self._rng_uniform(words[1], loc)
        n1, _n2 = self._rng_pair_normal(u1, u2, loc)
        return n1

    def _lower_tl_rand4x(self, args: Dict[str, ast.expr], node, loc,
                         construct: str) -> List[tir.Value]:
        """tl.rand4x: the uniform conversion of each philox word."""
        words = self._randint4x_values(args, node, loc, construct)
        return [self._rng_uniform(w, loc) for w in words]

    def _lower_tl_randint4x(self, args: Dict[str, ast.expr], node, loc,
                            construct: str) -> List[tir.Value]:
        """tl.randint4x: the four philox words."""
        return self._randint4x_values(args, node, loc, construct)

    def _lower_tl_randn4x(self, args: Dict[str, ast.expr], node, loc,
                          construct: str) -> List[tir.Value]:
        """tl.randn4x: two Box-Muller pairs over the four uniforms."""
        words = self._randint4x_values(args, node, loc, construct)
        u = [self._rng_uniform(w, loc) for w in words]
        n1, n2 = self._rng_pair_normal(u[0], u[1], loc)
        n3, n4 = self._rng_pair_normal(u[2], u[3], loc)
        return [n1, n2, n3, n4]

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

    # -- T014: the matrix-breadth lane -------------------------------------

    def _lower_tl_dot(self, args: Dict[str, ast.expr], node: ast.Call,
                      loc, construct: str) -> tir.Value:
        """tl.dot: the matrix product of two rank-2 blocks (T014).

        The typing rules are the pinned Triton 3.8 ``Semantic.dot``
        (F049), not what the target happens to serve:

          * both operands are block tensors of the SAME dtype in
            {int8, uint8, float16, bfloat16, float32} (fp64 is outside
            the corpus dtype surface, F037; non-i8 integers are refused
            by the pinned semantics itself: "only int8 supported");
          * ``out_dtype`` defaults to float32 with no ``acc`` and to the
            accumulator's dtype with one; ``out_dtype=bfloat16`` is the
            pinned ValueError; integer dots produce int32;
            float16/bfloat16/float32 dots produce float32, or float16
            for float16 operands when explicitly requested (fp32
            accumulation, one final rounding);
          * the ``acc`` block must match the result shape and dtype;
          * fp32 dots carry the IEEE numeric class: the declared subset
            strips ``input_precision``/``allow_tf32`` and the runner
            pins ``TRITON_F32_DEFAULT=ieee`` (F052) -- no reduced
            precision path exists to select.

        The lowered ``linalg.dot`` op carries the operand dtypes, the
        accumulation type and the ieee flag; the lowering consumes them
        (IME tiles for int8/float16, the vector FP32 path for fp32 IEEE
        and bfloat16 -- the recorded emulator gap, F010/F034).
        """
        a = self._lower_expr(args["input"])
        b = self._lower_expr(args["other"])
        if isinstance(a, ConstVal) or isinstance(b, ConstVal):
            raise self._err(
                node, construct,
                "tl.dot operands must be block tensors (not compile-time "
                "scalars)")
        for v, name in ((a, "input"), (b, "other")):
            if v.rank < 2:
                raise self._err(
                    node, construct,
                    f"tl.dot operand '{name}' must be rank-2 (got rank "
                    f"{v.rank}); the batched rank-3 form is not in this "
                    "lane")
            if len(v.shape) != 2:
                raise self._err(
                    node, construct,
                    f"tl.dot operand '{name}' must be rank-2, got "
                    f"{list(v.shape)} (the batched rank-3 form is not in "
                    "this lane)")
        if a.type != b.type:
            raise self._err(
                node, construct,
                f"both operands must be the same dtype (the pinned "
                f"semantics); got {a.type!r} and {b.type!r}")
        if a.type.is_pointer() or a.type.is_bool():
            raise self._err(
                node, construct,
                f"tl.dot requires numeric operands, got {a.type!r}")
        if a.type.name == "fp64":
            raise self._err(
                node, construct,
                "fp64 tl.dot is outside the corpus dtype surface (F037: "
                "bfloat16/bool/float16/float32/int16/int32/int64/int8 only)")
        if a.type.is_int() and a.type.width != 8:
            raise self._err(
                node, construct,
                f"only int8 integer dots are supported by the pinned "
                f"semantics ('only int8 supported!'); got {a.type!r}")
        if tir.value_shape(a.shape)[1] != tir.value_shape(b.shape)[0]:
            raise self._err(
                node, construct,
                f"tl.dot reduction extents differ: {list(a.shape)} x "
                f"{list(b.shape)} (second index of the first shape must "
                "equal the first index of the second)")

        # the accumulator and the out_dtype (the pinned resolution order)
        acc = None
        if "acc" in args and args["acc"] is not None:
            acc = self._lower_expr(args["acc"])
            if isinstance(acc, ConstVal):
                raise self._err(
                    node, construct,
                    "tl.dot's acc must be a block tensor (not a "
                    "compile-time scalar)")
            if len(acc.shape) != 2 or \
                    tir.value_shape(acc.shape) != \
                    (tir.value_shape(a.shape)[0],
                     tir.value_shape(b.shape)[1]):
                raise self._err(
                    node, construct,
                    f"accumulator shape {list(acc.shape)} is incompatible "
                    f"with the result "
                    f"({tir.value_shape(a.shape)[0]}, "
                    f"{tir.value_shape(b.shape)[1]})")
        explicit_out = None
        if "out_dtype" in args and args["out_dtype"] is not None:
            explicit_out = self._constexpr_dtype(args["out_dtype"], node,
                                                 construct)
        if explicit_out is not None and explicit_out.name == "bf16":
            raise self._err(
                node, construct,
                "out_dtype=bfloat16 is unsupported (the pinned Triton 3.8 "
                "raises; cast the float32 result with .to(tl.bfloat16))")

        # the result type (the pinned rules)
        if a.type.is_int():
            # integer dots: int32 result, always (the pinned semantics)
            if explicit_out is not None and explicit_out != tir.INT32:
                raise self._err(
                    node, construct,
                    f"integer dots accumulate int32 (the pinned "
                    f"semantics); out_dtype {explicit_out!r}")
            result_ty = tir.INT32
        elif a.type.name in ("fp32", "bf16"):
            if explicit_out is not None and explicit_out != tir.FLOAT32:
                raise self._err(
                    node, construct,
                    f"{a.type.name} dots produce float32 (the pinned "
                    f"semantics); out_dtype {explicit_out!r}")
            result_ty = tir.FLOAT32
        else:
            # fp16 operands: fp32, or fp16 with one final rounding
            if explicit_out is None:
                explicit_out = tir.FLOAT32
            if explicit_out not in (tir.FLOAT32, tir.FLOAT16):
                raise self._err(
                    node, construct,
                    f"fp16 dots produce float32 (or float16 with one "
                    f"final rounding); out_dtype {explicit_out!r}")
            result_ty = explicit_out
        if acc is not None:
            if acc.type != result_ty:
                raise self._err(
                    node, construct,
                    f"expected accumulator dtype {result_ty!r}, got "
                    f"{acc.type!r}; pass out_dtype={acc.type.name} to use "
                    "this accumulator dtype")
            if explicit_out is not None and acc.type != explicit_out:
                raise self._err(
                    node, construct,
                    f"expected accumulator dtype {explicit_out!r}, got "
                    f"{acc.type!r}")

        operands = [a, b] + ([acc] if acc is not None else [])
        op = tir.Op(
            "linalg.dot", operands, loc, result_ty,
            tir.real_shape([tir.value_shape(a.shape)[0],
                            tir.value_shape(b.shape)[1]]),
            attrs={
                "a_dtype": a.type.name, "b_dtype": b.type.name,
                "out_dtype": result_ty.name,
                # fp32 dots are IEEE by construction: the subset strips
                # the precision knobs and the runner pins ieee (F052)
                "ieee": a.type.name == "fp32",
                "acc_mode": "chain" if acc is not None else "zero",
            })
        return self._emit(op, "dot")

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
        rounding = None
        if "fp_downcast_rounding" in args:
            r = self.env.evaluate(args["fp_downcast_rounding"],
                                  self.source.path)
            if r is not NOT_CONSTEXPR:
                if r not in ("rtne", "rtz"):
                    raise self._err(
                        node, construct,
                        f"fp_downcast_rounding {r!r} is not declared "
                        "(rtne / rtz)")
                rounding = str(r)
        if "bitcast" in args:
            flag = self.env.evaluate(args["bitcast"], self.source.path)
            if flag is not NOT_CONSTEXPR and flag:
                # bit-level reinterpretation: the DISTINCT construct (width
                # preserved, value re-read; never a value conversion)
                dtype_node = args["dtype"]
                if isinstance(dtype_node, ast.Call) \
                        and isinstance(dtype_node.func, ast.Attribute) \
                        and isinstance(dtype_node.func.value, ast.Name) \
                        and dtype_node.func.value.id == "tl" \
                        and dtype_node.func.attr == "pointer_type":
                    raise self._err(
                        node, construct,
                        "bitcast=True to a pointer type is not declared "
                        "(the int-to-pointer reinterpretation is the "
                        "pointer-table pattern's own form)")
                target = self._constexpr_dtype(args["dtype"], node,
                                               construct)
                if not ftypes.bitcast_ok(value.type, target):
                    raise self._err(
                        node, construct,
                        f"cannot bitcast {value.type!r} to {target!r}: "
                        "bit-level reinterpretation preserves the width "
                        "and never converts values")
                return self._emit(tir.Op.bitcast(value, target, loc), "pbc")
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
        if rounding is not None:
            op.attrs["rounding"] = rounding
        return self._emit(op, "cvt")

    # -- helpers ---------------------------------------------------------------
    def _constexpr_int(self, node: Optional[ast.expr], call: ast.Call,
                       construct: str, param: str) -> int:
        if node is None:
            raise self._err(call, construct,
                            f"missing required parameter {param!r}")
        value = py_scalar(self.env.evaluate(node, self.source.path))
        if value is NOT_CONSTEXPR:
            # the lowering's own fold: a shape-derived bound (``16 //
            # x.shape[1]``) is compile-time in the pinned language even
            # though the constexpr env cannot see the local block
            # (IR-SEMANTIC-FIDELITY: block extents are compile-time);
            # anything that does not fold keeps the located refusal
            try:
                lowered = self._lower_expr(node)
            except FrontendError:
                lowered = None
            if isinstance(lowered, ConstVal):
                value = py_scalar(lowered.value)
        if value is NOT_CONSTEXPR or isinstance(value, bool) or \
                not isinstance(value, int):
            raise self._err(
                call, f"{construct}.{param}",
                f"{param} must be a compile-time integer")
        return value

    def _constexpr_shape(self, node: ast.expr, call: ast.Call,
                         construct: str) -> Tuple[int, ...]:
        value = py_scalar(self.env.evaluate(node, self.source.path))
        if value is NOT_CONSTEXPR:
            # ``x.shape`` of a runtime tensor folds in the lowering's
            # attribute path (the extents are compile-time even though the
            # value is not): tl.full(vals.shape, ...) -- the order-key form
            lowered = self._lower_expr(node)
            if isinstance(lowered, ConstVal):
                value = py_scalar(lowered.value)
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
        elif isinstance(value, TypeObject):
            # ``x.dtype`` of a runtime tensor folds to its (compile-time)
            # element type -- the asinh form ``y32.to(x.dtype)`` (the
            # math.transcendental lane's round trip back to the buffer
            # dtype)
            ty = value.element_ty.ty
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

    # -- T012: layout, shape and dtype-conversion breadth -------------------

    def _shape_args(self, args, node, construct) -> Tuple[int, ...]:
        """The declared shape from a construct's ``*shape`` binding: one
        sequence (``reshape(x, (n, m))`` / ``reshape(x, [n])``) or several
        bare integers (``reshape(x, n, m)``), per the pinned surface."""
        if not isinstance(args, list):
            args = [args]
        if len(args) == 1:
            value = py_scalar(self.env.evaluate(args[0], self.source.path))
            if value is NOT_CONSTEXPR:
                # the lowering's fold (the pinned constexpr shape: a
                # sequence of shape-derived extents folds element-wise
                # -- ``(x.shape[0], 16)`` of a runtime block's extents)
                try:
                    lowered = self._lower_expr(args[0])
                except FrontendError:
                    lowered = None
                if isinstance(lowered, ConstVal):
                    value = py_scalar(lowered.value)
            if value is NOT_CONSTEXPR or not isinstance(value,
                                                        (tuple, list)):
                raise self._err(
                    node, construct,
                    "shape must be a compile-time sequence of integers")
            items = list(value)
        else:
            items = []
            for a in args:
                v = py_scalar(self.env.evaluate(a, self.source.path))
                if v is NOT_CONSTEXPR:
                    try:
                        lowered = self._lower_expr(a)
                    except FrontendError:
                        lowered = None
                    if isinstance(lowered, ConstVal):
                        v = py_scalar(lowered.value)
                items.append(v)
            if any(v is NOT_CONSTEXPR for v in items):
                raise self._err(
                    node, construct,
                    "shape extents must be compile-time integers")
        out = []
        for item in items:
            item = py_scalar(item)
            if isinstance(item, bool) or not isinstance(item, int):
                raise self._err(
                    node, construct,
                    f"shape extents must be compile-time integers, got "
                    f"{item!r}")
            if item < 1:
                raise self._err(
                    node, construct,
                    f"shape extents must be positive, got {item}")
            out.append(item)
        return tuple(out)

    def _reshaped_shape(self, src: tir.Shape, extents: Tuple[int, ...],
                        node, construct) -> tir.Shape:
        """The reshape result shape with the covered-axes broadcast flags
        (the verifier's rule, built here): each result axis covers a
        contiguous run of source axes (multiplicatively); an axis that
        splits a source axis, or an inserted extent-1 axis, is REAL (the
        conservative flag -- realize is the lowering's identity)."""
        try:
            return _reshape_flags(src, extents)
        except ValueError as exc:
            raise self._err(node, construct, str(exc))

    def _lower_tl_reshape(self, args: Dict[str, ast.expr], node: ast.Call,
                          loc, construct: str,
                          can_reorder: bool = False) -> tir.Value:
        """tl.reshape / tl.view / tl.ravel / tl.squeeze / tl.unsqueeze /
        tl.expand_dims: the flat-identity axis re-partition (the result's
        lanes are the source's lanes; ``can_reorder`` (tl.view, ravel's
        flag) permits any permutation and the identity is the realized
        choice -- recorded, countable)."""
        value = self._lower_expr(args["input"])
        if isinstance(value, ConstVal):
            raise self._err(
                node, construct,
                "a compile-time value reshapes at specialization (no "
                "runtime layout op is produced)")
        extents = self._shape_args(args.get("*shape"), node, construct)
        if not extents:
            raise self._err(
                node, construct,
                "the unsplat form (reshape to a scalar) is not in the "
                "layout lane (a rank-0 result from a block)")
        if construct == "tl.view":
            can_reorder = True     # the pinned deprecation alias
        shape = self._reshaped_shape(value.shape, extents, node, construct)
        if shape == value.shape:
            return value                 # the identity reshape folds
        return self._emit(tir.Op.reshape(value, shape, loc,
                                         can_reorder=can_reorder), "rs")

    def _wrap_axis(self, axis: int, ndim: int, node, construct,
                   param: str) -> int:
        if not (-ndim <= axis < ndim):
            raise self._err(
                node, f"{construct}.{param}",
                f"axis {axis} outside the rank {ndim}")
        return axis if axis >= 0 else axis + ndim

    def _lower_tl_ravel(self, args, node, loc, construct) -> tir.Value:
        """tl.ravel(x, can_reorder): reshape to ``[x.numel]``."""
        value = self._lower_expr(args["x"])
        if isinstance(value, ConstVal):
            raise self._err(
                node, construct,
                "a compile-time value reshapes at specialization")
        can_reorder = False
        if "can_reorder" in args:
            flag = self.env.evaluate(args["can_reorder"], self.source.path)
            if flag is not NOT_CONSTEXPR:
                can_reorder = bool(flag)
        numel = tir.flat_extent(value.shape)
        if numel is None:
            raise self._err(
                node, construct,
                "ravel requires a compile-time-shaped block")
        shape = self._reshaped_shape(value.shape, (numel,), node, construct)
        if shape == value.shape:
            return value
        return self._emit(tir.Op.reshape(value, shape, loc,
                                         can_reorder=can_reorder), "rs")

    def _lower_tl_squeeze(self, args, node, loc, construct) -> tir.Value:
        """tl.squeeze(x, dim): remove a length-1 axis (a reshape form)."""
        value = self._lower_expr(args["x"])
        if isinstance(value, ConstVal):
            raise self._err(
                node, construct,
                "a compile-time value reshapes at specialization")
        dim = self._constexpr_int(args.get("dim"), node, construct, "dim")
        ndim = len(value.shape)
        dim = self._wrap_axis(dim, ndim, node, construct, "dim")
        if value.shape[dim].value != 1:
            raise self._err(
                node, construct,
                f"squeeze requires a length-1 axis at dim {dim}, got "
                f"{value.shape[dim].value}")
        extents = tuple(e.value for i, e in enumerate(value.shape)
                        if i != dim)
        if not extents:
            raise self._err(
                node, construct,
                "squeezing to a scalar is not in the layout lane (a rank-0 "
                "result from a block)")
        shape = self._reshaped_shape(value.shape, extents, node, construct)
        return self._emit(tir.Op.reshape(value, shape, loc), "rs")

    def _lower_tl_expand_dims(self, args, node, loc,
                              construct) -> tir.Value:
        """tl.expand_dims(x, axis) / tl.unsqueeze(x, dim): insert length-1
        axes (a reshape form; the axis indices refer to the result)."""
        value = self._lower_expr(args["input"] if "input" in args
                                 else args["x"])
        if isinstance(value, ConstVal):
            raise self._err(
                node, construct,
                "a compile-time value reshapes at specialization")
        axis_node = args.get("axis", args.get("dim"))
        axis_val = py_scalar(self.env.evaluate(axis_node,
                                               self.source.path))
        if axis_val is NOT_CONSTEXPR:
            raise self._err(
                node, construct,
                "axis must be a compile-time integer or sequence")
        axes = list(axis_val) if isinstance(axis_val, (tuple, list)) \
            else [axis_val]
        axes = [py_scalar(a) for a in axes]
        if any(isinstance(a, bool) or not isinstance(a, int) for a in axes):
            raise self._err(
                node, construct,
                "axis must be a compile-time integer or sequence")
        if not axes:
            raise self._err(node, construct, "axis must not be empty")
        new_ndim = len(value.shape) + len(axes)
        wrapped = [self._wrap_axis(a, new_ndim, node, construct, "axis")
                   for a in axes]
        if len(set(wrapped)) != len(wrapped):
            raise self._err(
                node, construct,
                f"expand_dims received duplicate axes, normalized axes = "
                f"{wrapped}")
        if value.rank == 0:
            raise self._err(
                node, construct,
                "expand_dims of a scalar (the pinned splat form) is not in "
                "the layout lane; a scalar already broadcasts to any shape")
        extents = list(e.value for e in value.shape)
        for a in sorted(wrapped):
            extents.insert(a, 1)
        shape = self._reshaped_shape(value.shape, tuple(extents), node,
                                     construct)
        return self._emit(tir.Op.reshape(value, shape, loc), "rs")

    def _dims_args(self, args, node, construct,
                   default_last_two: bool = False) -> Tuple[int, ...]:
        """The axis order from a ``*dims`` binding (permute/trans)."""
        raw = args.get("*dims")
        if raw is None:
            if default_last_two:
                return ()          # trans with no dims: swap the last two
            raise self._err(node, construct, "missing required parameter "
                            "'dims'")
        items = raw if isinstance(raw, list) else [raw]
        dims = []
        for a in items:
            v = py_scalar(self.env.evaluate(a, self.source.path))
            if v is NOT_CONSTEXPR:
                raise self._err(
                    node, construct,
                    f"dims must be compile-time integers, got {v!r}")
            if isinstance(v, (tuple, list)):
                # tl.permute(x, (0, 2, 1)): one iterable argument
                dims.extend(py_scalar(x) for x in v)
            elif isinstance(v, bool) or not isinstance(v, int):
                raise self._err(
                    node, construct,
                    f"dims must be compile-time integers, got {v!r}")
            else:
                dims.append(v)
        return tuple(dims)

    def _lower_tl_permute(self, args, node, loc, construct,
                          default_last_two: bool = False) -> tir.Value:
        """tl.trans / tl.permute: the axis permutation (trans with no dims
        swaps the last two axes, per the pinned surface)."""
        value = self._lower_expr(args["input"])
        if isinstance(value, ConstVal):
            raise self._err(
                node, construct,
                "a compile-time value has no layout (dims fold first)")
        dims = self._dims_args(args, node, construct,
                               default_last_two=default_last_two)
        rank = len(value.shape)
        if not dims and default_last_two:
            if rank < 2:
                raise self._err(
                    node, construct,
                    f"trans invoked with a {rank}-dimensional tensor")
            dims = tuple(list(range(rank - 2)) + [rank - 1, rank - 2])
        if len(dims) != rank:
            raise self._err(
                node, construct,
                f"permute dims must have the same length as the input "
                f"shape, got {len(dims)} and {rank}")
        dims = tuple(self._wrap_axis(d, rank, node, construct, "dims")
                     for d in dims)
        if sorted(dims) != list(range(rank)):
            raise self._err(
                node, construct,
                f"permute dims must be a permutation of 0..{rank - 1}, "
                f"but were {dims}")
        if dims == tuple(range(rank)):
            return value                 # the identity permutation folds
        return self._emit(tir.Op.permute(value, dims, loc), "pm")

    def _lower_transpose_attr(self, base, node) -> tir.Value:
        """``x.T``: the 2-D transposition (the pinned AST-visitor form)."""
        if isinstance(base, ConstVal):
            raise self._err(
                node, ".T",
                "a compile-time value has no layout")
        rank = len(base.shape)
        if rank != 2:
            raise self._err(
                node, ".T",
                f"the .T attribute transposes a 2-D block, got rank {rank}")
        dims = (1, 0)
        return self._emit(tir.Op.permute(base, dims, self._loc(node)), "pm")

    def _lower_shape_attr(self, base, node) -> ConstVal:
        """``x.shape``: the pinned constexpr shape tuple.  Block extents
        are compile-time in the source language, so every integer extent
        folds; a runtime-symbolic extent is a located refusal (never a
        baked value)."""
        if isinstance(base, ConstVal):
            raise self._err(
                node, ".shape",
                "a compile-time scalar has no shape")
        symbolic = [i for i, e in enumerate(base.shape)
                    if isinstance(e.value, tir.Sym)]
        if symbolic:
            raise self._err(
                node, ".shape",
                f"axis {symbolic[0]} of {base.name or 'value'} has a "
                "runtime-symbolic extent; x.shape is compile-time in the "
                "source language and a symbolic extent cannot be baked")
        return ConstVal(tuple(int(e.value) for e in base.shape))

    def _lower_subscript(self, node: ast.Subscript):
        """``x[:, None]`` / ``x[None]``: the pinned ``__getitem__`` -- every
        ``None`` inserts an axis (expand_dims at that position), a full
        slice is a no-op, anything else is refused."""
        # a constant integer index on a multi-result call selects one
        # result (``tl.swizzle2d(...)[0]``, the Python-level tuple form)
        if isinstance(node.value, ast.Call) and \
                isinstance(node.slice, ast.Constant) and \
                isinstance(node.slice.value, int) and \
                not isinstance(node.slice.value, bool):
            construct = self._callee_construct(node.value)
            if construct in _MULTI_RESULT_CONSTRUCTS:
                values = self._lower_call_multi(node.value)
                assert isinstance(values, list)
                idx = node.slice.value
                if not 0 <= idx < len(values):
                    raise self._err(
                        node, construct,
                        f"result index {idx} outside 0..{len(values) - 1}")
                return values[idx]
        base = self._lower_expr(node.value)
        if isinstance(base, ConstVal):
            # a compile-time sequence indexed by a constant integer folds
            # (``x.shape[1]``: the pinned constexpr shape tuple)
            if isinstance(node.slice, ast.Constant) and \
                    isinstance(node.slice.value, int) and \
                    not isinstance(node.slice.value, bool) and \
                    isinstance(base.value, (tuple, list)):
                idx = node.slice.value
                if not 0 <= idx < len(base.value):
                    raise self._err(
                        node, "subscript",
                        f"index {idx} outside the compile-time sequence "
                        f"of length {len(base.value)}")
                return ConstVal(base.value[idx])
            raise self._err(
                node, "subscript",
                "a compile-time value has no layout (indexing folds first)")
        sl = node.slice
        parts = sl.elts if isinstance(sl, ast.Tuple) else [sl]
        if isinstance(sl, ast.Slice):
            parts = [sl]
        value = base
        for dim, p in enumerate(parts):
            if isinstance(p, ast.Constant) and p.value is None:
                if value.rank == 0:
                    raise self._err(
                        node, "subscript",
                        "expand_dims of a scalar (the pinned splat form) is "
                        "not in the layout lane")
                extents = list(e.value for e in value.shape)
                extents.insert(dim, 1)
                shape = self._reshaped_shape(value.shape, tuple(extents),
                                             node, "subscript")
                value = self._emit(tir.Op.reshape(value, shape,
                                                  self._loc(node)), "rs")
            elif isinstance(p, ast.Slice):
                if not (p.lower is None and p.upper is None
                        and p.step is None):
                    raise self._err(
                        node, "subscript",
                        f"unsupported tensor index: {ast.unparse(p)}")
            else:
                raise self._err(
                    node, "subscript",
                    f"unsupported tensor index: "
                    f"{ast.unparse(p) if hasattr(ast, 'unparse') else p!r}")
        return value

    def _lower_tl_join(self, args, node, loc, construct) -> tir.Value:
        """tl.join(a, b): broadcast-unify the operands (the pinned first
        step), then append a minor extent-2 axis."""
        a = self._lower_expr(args["a"])
        b = self._lower_expr(args["b"])
        if isinstance(a, ConstVal) or isinstance(b, ConstVal):
            raise self._err(
                node, construct,
                "a scalar operand joins through the pinned splat form "
                "(not in the layout lane); the corpus joins blocks")
        try:
            target, a_exp, b_exp = fshapes.unify_pair(a.shape, b.shape, loc)
        except fshapes.ShapeError as exc:
            raise self._err(node, construct, exc.message)
        a_v = self._broadcast_to(a, target, loc)
        b_v = self._broadcast_to(b, target, loc)
        return self._emit(tir.Op.join(a_v, b_v, loc), "jn")

    def _lower_tl_split(self, args, node, loc, construct) -> List[tir.Value]:
        """tl.split(a): the last axis must be extent 2; two results."""
        a = self._lower_expr(args["a"])
        if isinstance(a, ConstVal):
            raise self._err(
                node, construct,
                "a compile-time value has no layout")
        if a.rank == 0:
            raise self._err(
                node, construct,
                "split requires a non-scalar tensor")
        if a.rank == 1:
            raise self._err(
                node, construct,
                "the rank-1 split-to-scalars form (the pinned unsplat "
                "route) is a declared-unsupported refusal: split a rank-2 "
                "block instead")
        if a.shape[-1].value != 2:
            raise self._err(
                node, construct,
                f"expected last dimension to be 2 for split, got "
                f"{a.shape[-1].value}")
        op = self._emit_multi(tir.Op.split(a, loc), 2, "sp")
        return list(op.results)

    def _lower_tl_cat(self, args, node, loc, construct) -> tir.Value:
        """tl.cat(input, other, can_reorder, dim): the pinned desugar --
        join introduces the minor dim, permute moves it before the concat
        dim, reshape merges (``can_reorder=True`` may reorder and the
        identity order is the realized choice)."""
        a = self._lower_expr(args["input"])
        b = self._lower_expr(args["other"])
        if isinstance(a, ConstVal) or isinstance(b, ConstVal):
            raise self._err(
                node, construct,
                "a scalar operand cats through the pinned splat form "
                "(not in the layout lane)")
        can_reorder = False
        if "can_reorder" in args:
            flag = self.env.evaluate(args["can_reorder"], self.source.path)
            if flag is not NOT_CONSTEXPR:
                can_reorder = bool(flag)
        dim = 0
        if "dim" in args and not can_reorder:
            dim = self._constexpr_int(args["dim"], node, construct, "dim")
        if len(a.shape) != len(b.shape):
            raise self._err(
                node, construct,
                f"tensors must have the same rank, got {len(a.shape)} and "
                f"{len(b.shape)}")
        rank = len(a.shape)
        dim = self._wrap_axis(dim, rank, node, construct, "dim")
        for i in range(rank):
            if i != dim and a.shape[i].value != b.shape[i].value:
                raise self._err(
                    node, construct,
                    f"tensor dims must match except in the concat dimension "
                    f"{dim}, got {list(a.shape)} and {list(b.shape)}")
        try:
            target, a_exp, b_exp = fshapes.unify_pair(a.shape, b.shape, loc)
        except fshapes.ShapeError as exc:
            raise self._err(node, construct, exc.message)
        a_v = self._broadcast_to(a, target, loc)
        b_v = self._broadcast_to(b, target, loc)
        c = self._emit(tir.Op.join(a_v, b_v, loc), "jn")
        order = list(range(rank))
        order.insert(dim, rank)
        c = self._emit(tir.Op.permute(c, tuple(order), loc), "pm")
        new_shape = list(e.value for e in a_v.shape)
        new_shape[dim] = a_v.shape[dim].value + b_v.shape[dim].value
        shape = self._reshaped_shape(c.shape, tuple(new_shape), node,
                                     construct)
        return self._emit(tir.Op.reshape(c, shape, loc,
                                         can_reorder=can_reorder), "rs")

    def _lower_tl_broadcast_to(self, args, node, loc,
                               construct) -> tir.Value:
        """tl.broadcast_to(input, *shape): explicit broadcast to a shape of
        equal rank (each axis equal or a source singleton)."""
        value = self._lower_expr(args["input"])
        if isinstance(value, ConstVal):
            raise self._err(
                node, construct,
                "a scalar splats to any shape (the pinned splat form is "
                "not this construct)")
        extents = self._shape_args(args.get("*shape"), node, construct)
        if len(extents) != len(value.shape):
            raise self._err(
                node, construct,
                f"Cannot broadcast, rank mismatch: {list(value.shape)}, "
                f"{list(extents)}")
        target = tir.real_shape(extents)
        for i, e in enumerate(value.shape):
            if extents[i] != e.value and e.value != 1:
                raise self._err(
                    node, construct,
                    f"Cannot broadcast, the expanded size of the tensor "
                    f"({extents[i]}) must match the existing size "
                    f"({e.value}) at non-singleton dimension {i}")
        return self._broadcast_to(value, target, loc)

    def _lower_tl_broadcast(self, args, node, loc,
                            construct) -> List[tir.Value]:
        """tl.broadcast(input, other): the pinned ``broadcast_impl_value`` --
        returns the two unified operands."""
        a = self._lower_expr(args["input"])
        b = self._lower_expr(args["other"])
        if isinstance(a, ConstVal) or isinstance(b, ConstVal):
            raise self._err(
                node, construct,
                "a scalar operand broadcasts through the pinned splat "
                "form (not in the layout lane)")
        try:
            target, a_exp, b_exp = fshapes.unify_pair(a.shape, b.shape, loc)
        except fshapes.ShapeError as exc:
            raise self._err(node, construct, exc.message)
        return [self._broadcast_to(a, target, loc),
                self._broadcast_to(b, target, loc)]

    def _lower_tl_flip(self, args, node, loc, construct) -> tir.Value:
        """tl.flip(x, dim): reverse one axis (power-of-two extent, the
        pinned static_assert)."""
        value = self._lower_expr(args["x"])
        if isinstance(value, ConstVal):
            raise self._err(
                node, construct,
                "a compile-time value has no layout")
        dim = 0
        if "dim" in args:
            dim = self._constexpr_int(args["dim"], node, construct, "dim")
        ndim = len(value.shape)
        if ndim == 0:
            raise self._err(
                node, construct,
                "flip requires a block operand")
        dim = self._wrap_axis(dim, ndim, node, construct, "dim")
        ext = value.shape[dim].value
        if not isinstance(ext, int) or ext < 1 or (ext & (ext - 1)):
            raise self._err(
                node, construct,
                f"flip requires a power-of-two extent at dim {dim} (the "
                f"pinned static_assert), got {ext!r}")
        return self._emit(tir.Op.flip(value, dim, loc), "fl")

    def _lower_tl_swizzle2d(self, args, node,
                            loc) -> List[tir.Value]:
        """tl.swizzle2d(i, j, size_i, size_j, size_g): the pinned arithmetic
        definition (standard.py) -- an index-space transformation, no data
        movement; returns (new_i, new_j)."""
        i = self._lower_expr(args["i"])
        j = self._lower_expr(args["j"])
        if isinstance(i, ConstVal) or isinstance(j, ConstVal):
            raise self._err(
                node, "tl.swizzle2d",
                "swizzle2d operates on runtime index blocks")
        if i.rank == 0 or j.rank == 0:
            raise self._err(
                node, "tl.swizzle2d",
                "swizzle2d operates on blocks (the scalar index form folds "
                "at specialization)")
        if not i.type.is_int() or not j.type.is_int():
            raise self._err(
                node, "tl.swizzle2d",
                f"swizzle2d operates on integer index blocks, got "
                f"{i.type!r} and {j.type!r}")
        size_i = self._constexpr_int(args["size_i"], node, "tl.swizzle2d",
                                     "size_i")
        size_j = self._constexpr_int(args["size_j"], node, "tl.swizzle2d",
                                     "size_j")
        size_g = self._constexpr_int(args["size_g"], node, "tl.swizzle2d",
                                     "size_g")

        def const(v):
            return self._emit(tir.Op.const(v, i.type, loc), "k")

        def bin(op, a, b):
            # the operands are pre-unified exactly like the elementwise
            # core's binary path (broadcast_impl_value: an explicit
            # broadcast op when the shapes differ)
            if a.shape != b.shape:
                try:
                    target, a_exp, b_exp = fshapes.unify_pair(a.shape,
                                                              b.shape, loc)
                except fshapes.ShapeError as exc:
                    raise self._err(node, "tl.swizzle2d", exc.message)
                a = self._broadcast_to(a, target, loc)
                b = self._broadcast_to(b, target, loc)
            if a.type != b.type:
                raise self._err(node, "tl.swizzle2d",
                                f"operand types differ: {a.type!r} vs "
                                f"{b.type!r}")
            return self._emit(tir.Op.binop(op, a, b, loc), "sw")

        # the pinned body (triton/language/standard.py), verbatim in form
        ij = bin("arith.add", bin("arith.mul", i, const(size_j)), j)
        size_gj = size_g * size_j
        group_id = bin("arith.sdiv", ij, const(size_gj))
        off_i = bin("arith.mul", group_id, const(size_g))
        # size_g' = min(size_i - off_i, size_g): a runtime minimum
        remaining = bin("arith.sub", const(size_i), off_i)
        c = const(size_g)
        if remaining.rank > 0 and c.rank == 0:
            c = self._broadcast_to(c, remaining.shape, loc)
        take_remaining = self._emit(tir.Op.cmp("cmp.lt", remaining, c,
                                               loc), "swc")
        size_g_eff = self._emit(tir.Op.where(take_remaining, remaining, c,
                                             loc), "sw")
        ij = bin("arith.srem", ij, const(size_gj))
        new_i = bin("arith.add", off_i, bin("arith.srem", ij, size_g_eff))
        new_j = bin("arith.sdiv", ij, size_g_eff)
        return [new_i, new_j]

    def _lower_tl_to_tensor(self, args, node, loc, construct) -> tir.Value:
        """tl.to_tensor(x): a Python scalar becomes a rank-0 tensor of its
        own type; a tensor is returned unchanged (the pinned semantics)."""
        value = self._lower_expr(args["x"])
        if isinstance(value, ConstVal):
            v = py_scalar(value.value)
            if isinstance(v, (DTypeValue, TypeObject)):
                raise self._err(
                    node, construct,
                    "a dtype value is not a constant")
            try:
                lit_ty = ftypes.literal_type(v)
            except ftypes.TypeRuleError as exc:
                raise self._err(node, construct, exc.message)
            return self._emit(tir.Op.const(v, lit_ty, loc), "lit")
        return value


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
    "tl.static_assert": Lowering._lower_tl_static_assert,
    "tl.dtype": Lowering._lower_tl_dtype,
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
    # T012: layout, shape and dtype-conversion breadth
    "tl.reshape": lambda self, a, n, l: Lowering._lower_tl_reshape(
        self, a, n, l, "tl.reshape"),
    "tl.view": lambda self, a, n, l: Lowering._lower_tl_reshape(
        self, a, n, l, "tl.view"),
    "tl.ravel": lambda self, a, n, l: Lowering._lower_tl_ravel(
        self, a, n, l, "tl.ravel"),
    "tl.squeeze": lambda self, a, n, l: Lowering._lower_tl_squeeze(
        self, a, n, l, "tl.squeeze"),
    "tl.expand_dims": lambda self, a, n, l: Lowering._lower_tl_expand_dims(
        self, a, n, l, "tl.expand_dims"),
    "tl.unsqueeze": lambda self, a, n, l: Lowering._lower_tl_expand_dims(
        self, a, n, l, "tl.unsqueeze"),
    "tl.trans": lambda self, a, n, l: Lowering._lower_tl_permute(
        self, a, n, l, "tl.trans", default_last_two=True),
    "tl.permute": lambda self, a, n, l: Lowering._lower_tl_permute(
        self, a, n, l, "tl.permute"),
    "tl.join": lambda self, a, n, l: Lowering._lower_tl_join(
        self, a, n, l, "tl.join"),
    "tl.cat": lambda self, a, n, l: Lowering._lower_tl_cat(
        self, a, n, l, "tl.cat"),
    "tl.broadcast_to": lambda self, a, n, l:
        Lowering._lower_tl_broadcast_to(self, a, n, l, "tl.broadcast_to"),
    "tl.flip": lambda self, a, n, l: Lowering._lower_tl_flip(
        self, a, n, l, "tl.flip"),
    "tl.to_tensor": lambda self, a, n, l: Lowering._lower_tl_to_tensor(
        self, a, n, l, "tl.to_tensor"),
    # T013: special math functions and bit-exact RNG (the math-ops lane)
    "tl.add": lambda self, a, n, l: Lowering._lower_tl_arith_fn(
        self, a, n, l, "tl.add"),
    "tl.sub": lambda self, a, n, l: Lowering._lower_tl_arith_fn(
        self, a, n, l, "tl.sub"),
    "tl.mul": lambda self, a, n, l: Lowering._lower_tl_arith_fn(
        self, a, n, l, "tl.mul"),
    "tl.exp": lambda self, a, n, l: Lowering._lower_math_unary(
        self, a, n, l, "tl.exp"),
    "tl.exp2": lambda self, a, n, l: Lowering._lower_math_unary(
        self, a, n, l, "tl.exp2"),
    "tl.log": lambda self, a, n, l: Lowering._lower_math_unary(
        self, a, n, l, "tl.log"),
    "tl.log2": lambda self, a, n, l: Lowering._lower_math_unary(
        self, a, n, l, "tl.log2"),
    "tl.sin": lambda self, a, n, l: Lowering._lower_math_unary(
        self, a, n, l, "tl.sin"),
    "tl.cos": lambda self, a, n, l: Lowering._lower_math_unary(
        self, a, n, l, "tl.cos"),
    "tl.erf": lambda self, a, n, l: Lowering._lower_math_unary(
        self, a, n, l, "tl.erf"),
    "tl.sqrt": lambda self, a, n, l: Lowering._lower_math_unary(
        self, a, n, l, "tl.sqrt"),
    "tl.sqrt_rn": lambda self, a, n, l: Lowering._lower_math_unary(
        self, a, n, l, "tl.sqrt_rn"),
    "tl.rsqrt": lambda self, a, n, l: Lowering._lower_math_unary(
        self, a, n, l, "tl.rsqrt"),
    "tl.floor": lambda self, a, n, l: Lowering._lower_math_unary(
        self, a, n, l, "tl.floor"),
    "tl.ceil": lambda self, a, n, l: Lowering._lower_math_unary(
        self, a, n, l, "tl.ceil"),
    "tl.abs": lambda self, a, n, l: Lowering._lower_tl_abs(
        self, a, n, l, "tl.abs"),
    "tl.maximum": lambda self, a, n, l: Lowering._lower_tl_maxmin_bin(
        self, a, n, l, "tl.maximum"),
    "tl.minimum": lambda self, a, n, l: Lowering._lower_tl_maxmin_bin(
        self, a, n, l, "tl.minimum"),
    "tl.clamp": lambda self, a, n, l: Lowering._lower_tl_clamp(
        self, a, n, l, "tl.clamp"),
    "tl.fma": lambda self, a, n, l: Lowering._lower_tl_fma(
        self, a, n, l, "tl.fma"),
    "tl.div_rn": lambda self, a, n, l: Lowering._lower_tl_div_rn(
        self, a, n, l, "tl.div_rn"),
    "tl.sigmoid": lambda self, a, n, l: Lowering._lower_tl_sigmoid(
        self, a, n, l, "tl.sigmoid"),
    "tl.softmax": lambda self, a, n, l: Lowering._lower_tl_softmax(
        self, a, n, l, "tl.softmax"),
    "tl.philox": lambda self, a, n, l: Lowering._lower_tl_philox(
        self, a, n, l, "tl.philox"),
    "tl.rand": lambda self, a, n, l: Lowering._lower_tl_rand(
        self, a, n, l, "tl.rand"),
    "tl.randn": lambda self, a, n, l: Lowering._lower_tl_randn(
        self, a, n, l, "tl.randn"),
    "tl.randint": lambda self, a, n, l: Lowering._lower_tl_randint(
        self, a, n, l, "tl.randint"),
    "tl.rand4x": lambda self, a, n, l: Lowering._lower_tl_rand4x(
        self, a, n, l, "tl.rand4x"),
    "tl.randint4x": lambda self, a, n, l: Lowering._lower_tl_randint4x(
        self, a, n, l, "tl.randint4x"),
    "tl.randn4x": lambda self, a, n, l: Lowering._lower_tl_randn4x(
        self, a, n, l, "tl.randn4x"),
    # T014: the matrix-breadth lane -- tl.dot through the real pipeline
    "tl.dot": lambda self, a, n, l: Lowering._lower_tl_dot(
        self, a, n, l, "tl.dot"),
    # multi-result constructs: the single-value call path refuses them
    # before the handler runs (the tuple-unpack form is the legal use);
    # registered so the surface's construct/handler consistency holds
    "tl.split": lambda self, a, n, l: (_ for _ in ()).throw(
        self._err(n, "tl.split",
                  "tl.split produces two values; unpack them (a, b = ...)")),
    "tl.broadcast": lambda self, a, n, l: (_ for _ in ()).throw(
        self._err(n, "tl.broadcast",
                  "tl.broadcast produces the two unified operands; unpack "
                  "them (a, b = ...)")),
    "tl.swizzle2d": lambda self, a, n, l: (_ for _ in ()).throw(
        self._err(n, "tl.swizzle2d",
                  "tl.swizzle2d produces (new_i, new_j); unpack them")),
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
    if ty.is_bool():
        # the pinned to_tensor route: a Python int/float reaches the i1
        # target as a numeric tensor and converts by ``!= 0`` -- the
        # full-constant form ``tl.full((N,), 1, tl.int1)`` is True
        # (probed against the pinned tracer); a non-numeric value still
        # refuses
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        raise FrontendError("<const>", 0, 0, "const",
                            f"i1 constant requires a bool or a numeric "
                            f"value, got {value!r}")
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


def _reshape_flags(src: tir.Shape, extents) -> tir.Shape:
    """The reshape covering rule (frontend and verifier share it): each
    result axis covers a contiguous multiplicative run of source axes.
    An axis that splits a source axis, or an inserted extent-1 axis, is
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
            f"cannot reshape {list(src)} to {list(extents)}: the element "
            f"counts differ ({total_src} vs {total_dst})")
    si = 0
    rem = src_vals[0] if src_vals else None
    out = []
    for de in extents:
        if de == 1:
            # consume one extent-1 source axis when the next unconsumed
            # axis is extent 1 (its flag is inherited); otherwise this is
            # an inserted axis (real)
            if rem == 1 and si < len(src_vals):
                out.append(tir.Extent(1, src[si].broadcast))
                si += 1
                rem = src_vals[si] if si < len(src_vals) else None
            else:
                out.append(tir.Extent(1, False))
            continue
        need = de
        flags = []
        aligned = True
        while need > 1:
            if rem is None:
                raise ValueError(
                    f"cannot reshape {list(src)} to {list(extents)}: the "
                    f"axes do not tile (ran out of source extent at "
                    f"extent {de})")
            if rem <= need and need % rem == 0:
                flags.append(src[si].broadcast)
                need //= rem
                si += 1
                rem = src_vals[si] if si < len(src_vals) else None
            elif rem % need == 0:
                # this result axis splits a source axis: conservative real
                rem //= need
                need = 1
                aligned = False
            else:
                raise ValueError(
                    f"cannot reshape {list(src)} to {list(extents)}: the "
                    f"axes do not tile (extent {de} vs remaining source "
                    f"extent {rem})")
        out.append(tir.Extent(de, aligned and all(flags)))
    # leftover source extent must be 1 (droppable extent-1 axes)
    if rem is not None and rem != 1:
        raise ValueError(
            f"cannot reshape {list(src)} to {list(extents)}: source extent "
            f"{rem} is left uncovered")
    for v in src_vals[si:]:
        if v != 1:
            raise ValueError(
                f"cannot reshape {list(src)} to {list(extents)}: source "
                f"axes {src_vals[si:]} are left uncovered")
    return tuple(out)


def lower(source: OperatorSource, spec: Specialization,
          surface: Optional[Surface] = None) -> tir.Module:
    """Lower one (source, specialization) to a verified-shape TIR module."""
    lowering = Lowering(source, spec, surface)
    return lowering.lower()
