"""RVV vectorization: TIR -> MIR for the elementwise + control-flow path.

Lowers one kernel (the frontend's elementwise core plus T008's structured
control flow) into the complete native program shape required by the
runtime ABI (a100rt.h):

  entry      bundle/view/scalar binding, native grid evaluation (one
             expression per grid axis), worker range start;
  program    the strided worker loop over source program instances
             (plan/partition); multi-axis program_id decomposes from the
             linear index (axis k stride = product of extents 0..k-1);
             tl.num_programs reads the runtime grid extents;
  prefix     the kernel's scalar statements (rank-0 values only) lower
             straight into the program body -- scalar loads, loop bounds,
             guards;
  chunk      the vector loop over the block at the target's (SEW, LMUL)
             with exact vl per chunk, masked tails (v0), whole-tree i64
             addresses (lower/addresses), opened at the FIRST block-level
             statement and closing at the end of the program body; source
             regions (if/loop/while) nest inside it, so block values
             carried across a source loop stay chunk-local;
  exit       the stats store.

The TIR data path is lowered *faithfully op by op* inside the regions
(MECH-GENERAL-PATH-FIRST: the general, unoptimized path lands first; CSE/
LICM and friends are later tasks' switched passes on top of it).

Structured control flow (T008): ``If`` lowers to a two-arm CFG with block
parameters as the explicit joins (a value re-bound on one path is a NEW
value after the join); counted ``Loop`` and while-form ``Loop`` lower to
head/body/exit block triples whose head parameters are the loop-carried
values; uses of a carried entry inside the body denote the current
iteration's value (the head parameter), never the pre-loop register.

Boundaries of this path (each a located refusal, never a silent
approximation): non-32-bit element widths (the whole-tree EEW=64/EMUL=2
address form is tuned to SEW=32), masked loads with ``other=``,
conversions, reductions and every matrix-routed construct (lower/matrix
refuses those); a block value escaping the chunk region (used after the
program body's last block-level statement) and early ``return`` are
refused by the frontend.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from a100c.ir import mir, tir
from a100c.lower import addresses as addr_mod
from a100c.lower import scalar as scalar_mod
from a100c.lower.binding import ArgumentLayout
from a100c.frontend.gridmodel import Bin, GridModel, Lit, MinMax, Ref
from a100c.plan.partition import ExecutionPlan
from a100c.target import TargetModel

__all__ = ["LowerOptions", "SliceLowering", "lower_to_mir",
           "VectorizeError"]


class VectorizeError(Exception):
    def __init__(self, loc, construct: str, message: str):
        super().__init__(f"vectorization: {construct}: {message}"
                         + (f" (at {loc})" if loc else ""))
        self.loc = loc
        self.construct = construct
        self.message = message


@dataclass
class LowerOptions:
    #: witness-only degraded build: the tail predicate is dropped from
    #: masked memory ops so tools/check_masked_tails.py can prove the mask
    #: is load-bearing (MECH-WITNESS-TEST).  Never set by the normal path;
    #: recorded in the artifact identity when set.
    witness_drop_tail_predicates: bool = False

    def identity_part(self) -> str:
        return ("witness-drop-tail-predicates"
                if self.witness_drop_tail_predicates else "default")


_VECTOR_KIND = {"float": "float", "int": "int", "uint": "uint"}


class _Ctx:
    """Emission helper: vreg creation and ordered op append."""

    def __init__(self, module: mir.MModule, function: mir.MFunction):
        self.module = module
        self.function = function
        self.blocks: Dict[str, mir.Block] = {}
        self.cur: Optional[mir.Block] = None
        self._hint_counts: Dict[str, int] = {}

    def add_block(self, name: str, params=(), loc=None) -> mir.Block:
        block = mir.Block(name, list(params), loc)
        self.function.blocks.append(block)
        self.blocks[name] = block
        return block

    def switch(self, block: mir.Block) -> None:
        self.cur = block

    def vreg(self, mtype, hint: str = "t", loc=None,
             fixed_phys: Optional[str] = None) -> mir.VReg:
        n = self._hint_counts.get(hint, 0) + 1
        self._hint_counts[hint] = n
        return mir.VReg(mtype, name=f"{hint}{n}", fixed_phys=fixed_phys,
                        loc=loc)

    def emit(self, op: mir.MOp) -> mir.VReg:
        self.cur.ops.append(op)
        assert len(op.results) == 1, op.opcode
        return op.results[0]

    def emit0(self, op: mir.MOp) -> None:
        self.cur.ops.append(op)

    def const(self, bits: int, mtype: mir.ScalarType, loc) -> mir.VReg:
        return self.emit(mir.MOp("sconst", [],
                                 [self.vreg(mtype, hint="k", loc=loc)],
                                 attrs={"value": int(bits)}, loc=loc))


class _Names:
    """The lexical name environment of the lowering (name -> TIR value),
    mirroring the frontend's scoping: regions copy, op results define under
    every scope name, joins define under the join name."""

    def __init__(self):
        self.stack: List[Dict[str, tir.Value]] = [{}]

    def push(self) -> None:
        self.stack.append(dict(self.stack[-1]))

    def pop(self) -> None:
        self.stack.pop()

    def get(self, name: str) -> Optional[tir.Value]:
        return self.stack[-1].get(name)

    def define(self, name: str, value: tir.Value) -> None:
        self.stack[-1][name] = value


class SliceLowering:
    """One (TIR module, plan, layout, grid model) -> MIR lowering run."""

    def __init__(self, tir_module: tir.Module, plan: ExecutionPlan,
                 target: TargetModel, layout: ArgumentLayout,
                 grid: GridModel, options: Optional[LowerOptions] = None):
        self.tir_module = tir_module
        self.plan = plan
        self.target = target
        self.layout = layout
        self.grid = grid
        self.options = options or LowerOptions()
        self.values: Dict[int, mir.VReg] = {}
        #: loop-carried entries: inside a body, the carried init value maps
        #: to the head parameter (uses denote the CURRENT iteration's
        #: value, never the pre-loop register)
        self._overrides: List[Dict[int, mir.VReg]] = []
        self.pointer_ops: Dict[int, tir.Op] = {}
        self.trees: List[addr_mod.AddressTree] = []
        self._tag_count = 0
        self._chunk = None            # the open chunk frame, if any
        #: the stored-element count register (set when the first masked
        #: store sits at the chunk body's top level; None otherwise)
        self._count_reg: Optional[mir.VReg] = None
        self._stats_chunk_granular = False
        self._pid_regs: Dict[int, mir.VReg] = {}
        self._np_regs: Dict[int, mir.VReg] = {}

    # -- helpers ---------------------------------------------------------------
    def _err(self, loc, construct: str, message: str):
        return VectorizeError(loc, construct, message)

    def value(self, t: tir.Value) -> Optional[mir.VReg]:
        for layer in reversed(self._overrides):
            if t.vid in layer:
                return layer[t.vid]
        return self.values.get(t.vid)

    def _need(self, t: tir.Value, loc) -> mir.VReg:
        reg = self.value(t)
        if reg is None:
            raise self._err(loc, t.name,
                            f"TIR value '{t.name}' is not lowered before its "
                            "use (use-before-definition in the lowering)")
        return reg

    def _bind_result(self, op: tir.Op, reg: mir.VReg) -> None:
        """Record one op result's MIR register AND its scope names (the
        name environment the region joins and loop back edges read)."""
        self.values[op.results[0].vid] = reg
        if self._names is not None:
            for key in op.results[0].scope_names():
                self._names.define(key, op.results[0])
        if self._names is not None:
            for key in op.results[0].scope_names():
                self._names.define(key, op.results[0])

    def _tag(self, hint: str) -> str:
        self._tag_count += 1
        return f"{hint}{self._tag_count}"

    # -- entry -----------------------------------------------------------------
    def lower(self) -> mir.MModule:
        fns = self.tir_module.functions
        if len(fns) != 1:
            raise self._err(None, "module",
                            "the slice compiles exactly one kernel function")
        fn = fns[0]
        statements = list(fn.body.statements)
        arange_extent, arange_op = self._find_arange(fn.body)
        sew, _kind = self._element_width(fn.body, arange_extent)
        self._sew = sew

        # the chunk plan at (SEW, LMUL=1); exact vl per chunk
        chunks = self.target.chunk_plan(arange_extent, sew, 1)
        vls = {vl for vl, _ in chunks}
        if len(vls) != 1:
            raise self._err(
                arange_op.loc if arange_op else None, "tl.arange",
                f"block extent {arange_extent} does not split into uniform "
                f"vector chunks at SEW {sew} (mixed-chunk tails are not in "
                "the slice)")
        vl = vls.pop()
        self._vl = vl
        self.plan.chunks = tuple((vl, 1) for _ in range(len(chunks)))
        self.plan.block_extent = arange_extent

        module = mir.MModule(self.tir_module.name, self.tir_module.source_path)
        launch = mir.VReg(mir.I64, name="launch")
        function = mir.MFunction("operator_entry", [launch], fn.loc)
        module.functions.append(function)
        ctx = _Ctx(module, function)
        ctx.add_block("entry", [launch], fn.loc)
        ctx.switch(ctx.blocks["entry"])

        self._emit_entry(ctx, fn, statements)
        self._ensure_vsetvli_regions(ctx, module)
        return module

    def _ensure_vsetvli_regions(self, ctx: _Ctx, module: mir.MModule) -> None:
        """Every block that executes a vector op opens its own vsetvli
        region (the MIR invariant: region state does not cross block
        boundaries -- conservative, matching the hardware's fragility
        across branches).  The inserted region is the data region
        (SEW, LMUL=1); mid-block switches (the e64m2 address form) already
        carry their own restore."""
        for fn in module.functions:
            for b in fn.blocks:
                region = None
                out = []
                for op in b.ops:
                    if op.opcode == "vsetvli":
                        region = (op.attrs["sew"], op.attrs["lmul"])
                    elif op.opcode in mir.VEC_OPS and region is None:
                        loc = op.loc
                        avl = mir.MOp(
                            "sconst", [],
                            [ctx.vreg(mir.I32, hint="rvl", loc=loc)],
                            attrs={"value": int(self._vl)}, loc=loc)
                        out.append(avl)
                        out.append(mir.MOp(
                            "vsetvli", [avl.results[0]],
                            [ctx.vreg(mir.I32, hint="rvs", loc=loc)],
                            attrs={"sew": self._sew, "lmul": 1,
                                   "policy": "ta,ma"}, loc=loc))
                        region = (self._sew, 1)
                    out.append(op)
                b.ops = out

    # -- structure analysis ------------------------------------------------------
    def _walk_ops(self, block: tir.Block):
        for stmt in block.statements:
            if isinstance(stmt, tir.Op):
                yield stmt
            elif isinstance(stmt, tir.If):
                yield from self._walk_ops(stmt.then)
                yield from self._walk_ops(stmt.els)
            elif isinstance(stmt, tir.Loop):
                yield from self._walk_ops(stmt.body)

    def _find_arange(self, body: tir.Block) -> Tuple[int, Optional[tir.Op]]:
        found = None
        for op in self._walk_ops(body):
            if op.op == "arange":
                if found is not None:
                    raise self._err(op.loc, "tl.arange",
                                    "two tl.arange values in one kernel are "
                                    "not in the slice")
                found = op
        if found is None:
            raise self._err(None, "tl.arange",
                            "no tl.arange in the kernel body; the vector slice "
                            "lowers the one-block elementwise form")
        return found.attrs["end"] - found.attrs["start"], found

    def _element_width(self, body: tir.Block, arange_extent) -> Tuple[int, str]:
        """The data SEW: the pointee width every memory op must agree on."""
        sew = None
        kind = "int"
        for op in self._walk_ops(body):
            if op.op in ("load", "store"):
                pointee = op.operands[0].type.pointee
                if pointee.is_bool():
                    raise self._err(op.loc, op.op,
                                    "i8/i1 pointee widths are not in the "
                                    "slice (the whole-tree EEW=64/EMUL=2 "
                                    "address form is tuned to SEW=32)")
                if pointee.bitwidth() != 32:
                    raise self._err(
                        op.loc, op.op,
                        f"element width {pointee.bitwidth()} is not in the "
                        "slice: SEW!=32 kernels need the multi-region address "
                        "plan of a later task (located refusal, never a "
                        "silent approximation)")
                sew = pointee.bitwidth()
                kind = _VECTOR_KIND[pointee.kind] if pointee.kind in _VECTOR_KIND else "int"
        if sew is None:
            sew = 32           # offsets only (no memory ops): i32 region
        return sew, kind

    def _stmt_is_block(self, stmt) -> bool:
        """Does the statement produce or consume a block (rank>0) value?
        The chunk region opens at the first such statement."""
        if isinstance(stmt, tir.Op):
            return any(getattr(o, "rank", 0) > 0 for o in stmt.operands) or \
                any(r.rank > 0 for r in stmt.results)
        if isinstance(stmt, tir.If):
            return any(self._stmt_is_block(s)
                       for s in list(stmt.then.statements)
                       + list(stmt.els.statements))
        if isinstance(stmt, tir.Loop):
            for bound in (stmt.lower, stmt.upper, stmt.step, stmt.cond):
                if bound is not None and bound.rank > 0:
                    return True
            if any(init.rank > 0 for _, init in stmt.carried):
                return True
            return any(self._stmt_is_block(s) for s in stmt.body.statements)
        return False

    # -- the entry block ----------------------------------------------------------
    def _emit_entry(self, ctx: _Ctx, fn: tir.Function, statements) -> None:
        loc = fn.loc
        launch = ctx.function.params[0]

        bundle = ctx.emit(mir.MOp(
            "sload", [launch], [ctx.vreg(mir.I64, hint="bundle", loc=loc)],
            attrs={"width": 64, "offset": 0, "ext": "sext"}, loc=loc))
        views = ctx.emit(mir.MOp(
            "sload", [bundle], [ctx.vreg(mir.I64, hint="views", loc=loc)],
            attrs={"width": 64, "offset": 0, "ext": "sext"}, loc=loc))
        scalars = ctx.emit(mir.MOp(
            "sload", [bundle], [ctx.vreg(mir.I64, hint="scalars", loc=loc)],
            attrs={"width": 64, "offset": 8, "ext": "sext"}, loc=loc))
        stats = ctx.emit(mir.MOp(
            "sload", [launch], [ctx.vreg(mir.I64, hint="stats", loc=loc)],
            attrs={"width": 64, "offset": 24, "ext": "sext"}, loc=loc))
        worker_id = ctx.emit(mir.MOp(
            "sload", [launch], [ctx.vreg(mir.U32, hint="wid", loc=loc)],
            attrs={"width": 32, "offset": 40, "ext": "zext"}, loc=loc))
        worker_count = ctx.emit(mir.MOp(
            "sload", [launch], [ctx.vreg(mir.U32, hint="wcnt", loc=loc)],
            attrs={"width": 32, "offset": 44, "ext": "zext"}, loc=loc))

        # scalar bindings (record-kind aware); the i64 view used by the grid
        grid_scalar_regs: Dict[str, mir.VReg] = {}
        for binding in self.layout.scalars:
            reg = ctx.emit(mir.MOp(
                "sload", [scalars],
                [ctx.vreg(mir.ScalarType(binding.width,
                                         signed=binding.signed),
                          hint=binding.name, loc=loc)],
                attrs={"width": binding.width,
                       "offset": binding.record_index * 16 + 8,
                       "ext": "sext" if binding.signed else "zext"},
                loc=loc))
            wide = reg
            if binding.width != 64:
                if binding.tir_type.is_float():
                    raise self._err(
                        loc, binding.name,
                        f"scalar argument {binding.name!r} is floating; the "
                        "slice's scalar core is integer (grid extents and "
                        "index arithmetic)")
                wide = ctx.emit(mir.MOp(
                    "smove", [reg],
                    [ctx.vreg(mir.I64, hint=binding.name + "w", loc=loc)],
                    loc=loc))
            grid_scalar_regs[binding.name] = wide
            # the TIR value at its declared type
            tir_reg = wide
            ty = binding.tir_type
            if ty.is_float():
                if ty.width != binding.width:
                    raise self._err(
                        loc, binding.name,
                        f"float scalar {binding.name!r} width {ty.width} "
                        f"differs from its record width {binding.width}")
            elif ty.width != binding.width:
                tir_reg = ctx.emit(mir.MOp(
                    "strunc", [wide],
                    [ctx.vreg(mir.ScalarType(ty.width, signed=ty.signed),
                              hint=binding.name + "n", loc=loc)], loc=loc))
            for p in fn.params:
                if p.name == binding.name:
                    self.values[p.vid] = tir_reg

        # view bindings: data base (flat, pointee-typed pointer semantics)
        view_regs: Dict[str, mir.VReg] = {}
        for binding in self.layout.views:
            reg = ctx.emit(mir.MOp(
                "sload", [views],
                [ctx.vreg(mir.I64, hint=binding.name, loc=loc)],
                attrs={"width": 64, "offset": binding.view_index * 56,
                       "ext": "sext"}, loc=loc))
            view_regs[binding.name] = reg
            for p in fn.params:
                if p.name == binding.name:
                    self.values[p.vid] = reg

        # native grid evaluation (runtime; one expression per axis, reading
        # bundle scalars / view extents)
        extents = [self._emit_grid_expr(ctx, expr, grid_scalar_regs, views,
                                        loc)
                   for expr in self.grid.axes]
        self._grid_extents = extents
        program_count = scalar_mod.emit_grid_product(ctx, extents, loc)

        # worker range start: worker_id zero-extended into the i64 induction
        pid = ctx.emit(mir.MOp(
            "smove", [worker_id],
            [ctx.vreg(mir.I64, hint="pid", loc=loc)], loc=loc))
        wcount64 = ctx.emit(mir.MOp(
            "smove", [worker_count],
            [ctx.vreg(mir.I64, hint="wcnt64", loc=loc)], loc=loc))
        items0 = ctx.const(0, mir.I64, loc)

        head = ctx.add_block("prog_head", [], loc)
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "prog_head",
                                 "args": [pid, items0]}, loc=loc))

        self._emit_program_loop(ctx, fn, statements, program_count, wcount64,
                                stats, view_regs)

    # -- grid expression -----------------------------------------------------------
    def _emit_grid_expr(self, ctx: _Ctx, expr, scalar_regs: Dict[str, mir.VReg],
                        views: mir.VReg, loc) -> mir.VReg:
        if isinstance(expr, Lit):
            return ctx.const(expr.value, mir.I64, loc)
        if isinstance(expr, Ref):
            tie = self.grid.ties.get(expr.key)
            if tie is None:
                raise self._err(loc, "grid",
                                f"grid input {expr!r} has no bundle-visible "
                                "tie (the model refused to bake it)")
            kind = tie[0]
            name = tie[1]
            if kind == "scalar":
                reg = scalar_regs.get(str(name))
                if reg is None:
                    raise self._err(loc, "grid",
                                    f"tied scalar {name!r} is not a bound "
                                    "kernel scalar")
                return reg
            if kind == "view_extent":
                # ('view_extent', view_name, axis)
                axis = tie[2] if len(tie) > 2 else 0
                binding = self.layout.view_of(str(name))
                if binding is None:
                    raise self._err(loc, "grid",
                                    f"tied view {name!r} is not a bound "
                                    "kernel pointer")
                shape_ptr = ctx.emit(mir.MOp(
                    "sload", [views],
                    [ctx.vreg(mir.I64, hint="vshape", loc=loc)],
                    attrs={"width": 64, "offset": binding.view_index * 56 + 8,
                           "ext": "sext"}, loc=loc))
                return ctx.emit(mir.MOp(
                    "sload", [shape_ptr],
                    [ctx.vreg(mir.I64, hint="vext", loc=loc)],
                    attrs={"width": 64, "offset": int(axis) * 8,
                           "ext": "sext"}, loc=loc))
            raise self._err(loc, "grid", f"unknown tie kind {kind!r}")
        if isinstance(expr, Bin):
            lhs = self._emit_grid_expr(ctx, expr.left, scalar_regs, views, loc)
            rhs = self._emit_grid_expr(ctx, expr.right, scalar_regs, views, loc)
            code = {"add": "sadd", "sub": "ssub", "mul": "smul",
                    "floordiv": "sdivu"}[expr.op]
            return ctx.emit(mir.MOp(
                code, [lhs, rhs],
                [ctx.vreg(mir.I64, hint="grid", loc=loc)], loc=loc))
        if isinstance(expr, MinMax):
            # max(a, b) = a + ((b - a) & -(a < b));  min swaps the sense
            lhs = self._emit_grid_expr(ctx, expr.left, scalar_regs, views, loc)
            rhs = self._emit_grid_expr(ctx, expr.right, scalar_regs, views, loc)
            take_left = "slt" if expr.op == "min" else "sgt-swap"
            if expr.op == "max":
                # a < b
                c = ctx.emit(mir.MOp(
                    "slt", [lhs, rhs],
                    [ctx.vreg(mir.I64, hint="gmm", loc=loc)], loc=loc))
            else:
                # b < a  (min takes the smaller)
                c = ctx.emit(mir.MOp(
                    "slt", [rhs, lhs],
                    [ctx.vreg(mir.I64, hint="gmm", loc=loc)], loc=loc))
            zero = ctx.const(0, mir.I64, loc)
            mask = ctx.emit(mir.MOp(
                "ssub", [zero, c],
                [ctx.vreg(mir.I64, hint="gmk", loc=loc)], loc=loc))
            diff = ctx.emit(mir.MOp(
                "ssub", [rhs, lhs],
                [ctx.vreg(mir.I64, hint="gmd", loc=loc)], loc=loc))
            sel = ctx.emit(mir.MOp(
                "sand", [diff, mask],
                [ctx.vreg(mir.I64, hint="gms", loc=loc)], loc=loc))
            return ctx.emit(mir.MOp(
                "sadd", [lhs, sel],
                [ctx.vreg(mir.I64, hint="gmx", loc=loc)], loc=loc))
        raise self._err(loc, "grid", f"unknown grid expression node {expr!r}")

    # -- the program loop and the kernel body ------------------------------------
    def _emit_program_loop(self, ctx: _Ctx, fn: tir.Function,
                           statements: list, program_count: mir.VReg,
                           wcount64: mir.VReg, stats: mir.VReg,
                           view_regs: Dict[str, mir.VReg]) -> None:
        loc = fn.loc

        # prog_head(pid, items)
        pid_h = mir.VReg(mir.I64, name="pid.loop")
        items_h = mir.VReg(mir.I64, name="items.loop")
        head = ctx.blocks["prog_head"]
        head.params += [pid_h, items_h]
        ctx.switch(head)
        cont = ctx.emit(mir.MOp("slt", [pid_h, program_count],
                                [ctx.vreg(mir.I64, hint="go", loc=loc)],
                                loc=loc))
        ctx.emit0(mir.MOp("brc", [cont], [],
                          attrs={"true_target": "prog_body",
                                 "true_args": [pid_h, items_h],
                                 "false_target": "prog_exit",
                                 "false_args": [pid_h, items_h]}, loc=loc))

        # prog_body(pid, items)
        pid_b = mir.VReg(mir.I64, name="pid.body")
        items_b = mir.VReg(mir.I64, name="items.body")
        body = ctx.add_block("prog_body", [pid_b, items_b], loc)
        ctx.switch(body)
        self._pid_b = pid_b

        # multi-axis program_id decomposition (axis k stride = product of
        # the extents of axes 0..k-1); 1-D grids skip the arithmetic
        self._pid_axis_regs = {}
        if self.grid.ndim == 1:
            pid0 = ctx.emit(mir.MOp(
                "strunc", [pid_b],
                [ctx.vreg(mir.I32, hint="pid0", loc=loc)], loc=loc))
            self._pid_axis_regs[0] = pid0
        else:
            pids = scalar_mod.emit_axis_decomposition(
                ctx, pid_b, self._grid_extents, loc)
            for axis, p in enumerate(pids):
                self._pid_axis_regs[axis] = ctx.emit(mir.MOp(
                    "strunc", [p],
                    [ctx.vreg(mir.I32, hint=f"pid{axis}", loc=loc)], loc=loc))
        # tl.num_programs reads the runtime grid extents (i32)
        self._np_regs = {
            axis: ctx.emit(mir.MOp(
                "strunc", [extent],
                [ctx.vreg(mir.I32, hint=f"np{axis}", loc=loc)], loc=loc))
            for axis, extent in enumerate(self._grid_extents)}

        # the kernel body: scalar statements lower here; the chunk region
        # opens at the first block-level statement
        names = _Names()
        for p in fn.params:
            names.define(p.name, p)
        self._names = names
        self._lower_statements(ctx, statements, fn, view_regs)

        # close the body: the chunk back edge (from whatever block the
        # statements ended in), or a direct step for a fully scalar kernel
        if self._chunk is not None:
            self._close_chunk_back_edge(ctx, fn)
        else:
            ctx.emit0(mir.MOp("br", [], [],
                              attrs={"target": "prog_next",
                                     "args": [pid_b, items_b]}, loc=loc))

        # prog_next(pid, items): the strided worker step
        pid_n = mir.VReg(mir.I64, name="pid.next")
        items_n = mir.VReg(mir.I64, name="items.next")
        nxt = ctx.add_block("prog_next", [pid_n, items_n], loc)
        ctx.switch(nxt)
        pid2 = ctx.emit(mir.MOp(
            "sadd", [pid_n, wcount64],
            [ctx.vreg(mir.I64, hint="pid2", loc=loc)], loc=loc))
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "prog_head",
                                 "args": [pid2, items_n]}, loc=loc))

        # prog_exit(pid, items)
        pid_e = mir.VReg(mir.I64, name="pid.exit")
        items_e = mir.VReg(mir.I64, name="items.exit")
        exitb = ctx.add_block("prog_exit", [pid_e, items_e], loc)
        ctx.switch(exitb)
        ctx.emit0(mir.MOp("sstore", [stats, items_e], [],
                          attrs={"width": 64, "offset": 0}, loc=loc))
        ctx.emit0(mir.MOp("ret", [], [], loc=loc))

    # -- statement lowering -----------------------------------------------------
    def _lower_statements(self, ctx: _Ctx, statements, fn: tir.Function,
                          view_regs: Dict[str, mir.VReg]) -> None:
        for stmt in statements:
            self._lower_stmt(ctx, stmt, fn, view_regs)

    def _lower_stmt(self, ctx: _Ctx, stmt, fn: tir.Function,
                    view_regs: Dict[str, mir.VReg]) -> None:
        if isinstance(stmt, tir.Op):
            if self._stmt_is_block(stmt):
                self._ensure_chunk(ctx, fn)
            self._lower_tir_op(ctx, stmt, fn, view_regs)
            return
        if isinstance(stmt, tir.If):
            if self._stmt_is_block(stmt):
                self._ensure_chunk(ctx, fn)
            self._lower_if(ctx, stmt, fn, view_regs)
            return
        if isinstance(stmt, tir.Loop):
            if self._stmt_is_block(stmt):
                self._ensure_chunk(ctx, fn)
            self._lower_loop(ctx, stmt, fn, view_regs)
            return
        raise self._err(None, "statement",
                        f"statement {stmt!r} is not lowerable")

    # -- the chunk region ---------------------------------------------------------
    def _ensure_chunk(self, ctx: _Ctx, fn: tir.Function) -> None:
        """Open the chunk loop over the block extent (block-local index
        space [0, B) in vl-sized pieces).  Opens once, at the first
        block-level statement; everything after lowers inside it."""
        if self._chunk is not None:
            return
        loc = fn.loc
        B = self.plan.block_extent
        vl = self._vl
        # the current block is wherever the scalar prefix ended; the items
        # counter is the prog_body parameter (the prefix never modifies it)
        items_reg = self._items_in_scope(ctx)
        elem0 = ctx.const(0, mir.I32, loc)

        head = ctx.add_block("chunk_head", [], loc)
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": head.name,
                                 "args": [elem0, items_reg]}, loc=loc))
        elem_h = mir.VReg(mir.I32, name="elem.loop")
        items_c = mir.VReg(mir.I64, name="items.chunk")
        head.params += [elem_h, items_c]
        ctx.switch(head)
        extent = ctx.const(B, mir.I32, loc)
        ccont = ctx.emit(mir.MOp(
            "slt", [elem_h, extent],
            [ctx.vreg(mir.I64, hint="cgo", loc=loc)], loc=loc))
        ctx.emit0(mir.MOp("brc", [ccont], [],
                          attrs={"true_target": "chunk_body",
                                 "true_args": [elem_h, items_c],
                                 "false_target": "prog_next",
                                 "false_args": [self._pid_b, items_c]},
                          loc=loc))

        cbody_params = [mir.VReg(mir.I32, name="elem.body"),
                        mir.VReg(mir.I64, name="items.cbody")]
        cbody = ctx.add_block("chunk_body", cbody_params, loc)
        ctx.switch(cbody)
        elem_b = cbody_params[0]

        avl = ctx.const(vl, mir.I32, loc)
        ctx.emit(mir.MOp(
            "vsetvli", [avl], [ctx.vreg(mir.I32, hint="vl", loc=loc)],
            attrs={"sew": self._sew, "lmul": 1, "policy": "ta,ma"}, loc=loc))

        self._chunk = {"head": head, "body": cbody, "elem": elem_b,
                       "items": items_c, "vl": vl, "extent": B}

    def _items_in_scope(self, ctx: _Ctx) -> mir.VReg:
        """The items counter at the current position: the prog_body items
        parameter (the scalar prefix does not modify it)."""
        return ctx.blocks["prog_body"].params[1]

    def _close_chunk_back_edge(self, ctx: _Ctx, fn: tir.Function) -> None:
        """The chunk loop's back edge, from the block the kernel body ended
        in: elem += vl; items += the stored-element count (exact when the
        first masked store sits at the chunk body's top level, else one
        vector chunk of useful work per iteration -- recorded in meta)."""
        loc = fn.loc
        chunk = self._chunk
        elem_b = chunk["elem"]
        items_b2 = chunk["items"]
        if self._count_reg is not None:
            items_next = ctx.emit(mir.MOp(
                "sadd", [items_b2, self._count_reg],
                [ctx.vreg(mir.I64, hint="items2", loc=loc)], loc=loc))
        elif self.plan.counts_elements:
            items_next = ctx.emit(mir.MOp(
                "sadd", [items_b2,
                         ctx.const(chunk["vl"], mir.I64, loc)],
                [ctx.vreg(mir.I64, hint="items2", loc=loc)], loc=loc))
            self._stats_chunk_granular = True
        else:
            items_next = items_b2
        elem_next = ctx.emit(mir.MOp(
            "sadd", [elem_b, ctx.const(chunk["vl"], mir.I32, loc)],
            [ctx.vreg(mir.I32, hint="elem2", loc=loc)], loc=loc))
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": chunk["head"].name,
                                 "args": [elem_next, items_next]}, loc=loc))

    # -- regions -------------------------------------------------------------------
    def _lower_if(self, ctx: _Ctx, stmt: tir.If, fn: tir.Function,
                  view_regs: Dict[str, mir.VReg]) -> None:
        loc = stmt.loc or fn.loc
        cond = self._need(stmt.cond, loc)
        tag = self._tag("if")
        join_name = f"{tag}.join"
        frame = scalar_mod.begin_if(ctx, cond, loc, tag)

        names = self._names
        outer: Dict[str, tir.Value] = dict(names.stack[-1])

        arm_values = []
        for block, arm in ((frame.then_block, stmt.then),
                           (frame.else_block, stmt.els)):
            ctx.switch(block)
            names.push()
            self._lower_statements(ctx, arm.statements, fn, view_regs)
            values = []
            for name in stmt.join_names:
                v = names.get(name)
                if v is None:
                    raise self._err(
                        loc, "if",
                        f"join '{name}' has no value at the end of an arm "
                        "(the frontend and the verifier disagree)")
                values.append(self._need(v, loc))
            scalar_mod.close_arm(ctx, frame, join_name, values)
            arm_values.append(values)
            names.pop()

        params = scalar_mod.join_if(ctx, frame, join_name, arm_values, loc)
        ctx.switch(ctx.blocks[join_name])
        for value, param in zip(stmt.join_results, params):
            self.values[value.vid] = param
            for key in value.scope_names():
                names.define(key, value)

    def _lower_loop(self, ctx: _Ctx, stmt: tir.Loop, fn: tir.Function,
                    view_regs: Dict[str, mir.VReg]) -> None:
        loc = stmt.loc or fn.loc
        names = self._names
        if stmt.cond is not None:
            self._lower_while(ctx, stmt, fn, view_regs, loc, names)
            return
        if stmt.lower is None or stmt.upper is None or stmt.step is None:
            raise self._err(
                loc, "loop",
                "malformed control flow: the counted loop form requires "
                "lower/upper/step and the while form requires cond (a "
                "hand-built module bypassed the TIR verifier)")
        lower = self._need(stmt.lower, loc)
        upper = self._need(stmt.upper, loc)
        step = self._need(stmt.step, loc)
        # carried[0] IS the induction (the frontend's counted form); the
        # builder adds the induction param itself
        carried_inits = [self._need(init, loc) for _, init in stmt.carried]
        tag = self._tag("loop")
        frame = scalar_mod.begin_counted_loop(
            ctx, lower, upper, carried_inits[1:], loc, tag)

        # inside the body, uses of a carried entry denote the current
        # iteration's value (the head parameter)
        override: Dict[int, mir.VReg] = {}
        for (_, init), param in zip(stmt.carried, frame.params):
            override[init.vid] = param
        self._overrides.append(override)

        names.push()
        for (cname, init), param in zip(stmt.carried, frame.params):
            names.define(cname, init)
        self._lower_statements(ctx, stmt.body.statements, fn, view_regs)
        back = []
        for cname, _ in stmt.carried:
            v = names.get(cname)
            if v is None:
                raise self._err(
                    loc, "loop",
                    f"carried '{cname}' has no value at the body end")
            back.append(self._need(v, loc))
        scalar_mod.close_loop(ctx, frame, back)
        self._overrides.pop()
        names.pop()

        ctx.switch(frame.exit)
        for value, param in zip(stmt.join_results, frame.exit.params):
            self.values[value.vid] = param
            for key in value.scope_names():
                names.define(key, value)

    def _lower_while(self, ctx: _Ctx, stmt: tir.Loop, fn: tir.Function,
                     view_regs: Dict[str, mir.VReg], loc, names) -> None:
        cond_init = self._need(stmt.cond, loc)
        # carried[0] IS the condition (the frontend's while form); the
        # builder adds the cond param itself
        carried_inits = [self._need(init, loc) for _, init in stmt.carried]
        tag = self._tag("while")
        frame = scalar_mod.begin_while_loop(
            ctx, cond_init, carried_inits[1:], loc, tag)

        override: Dict[int, mir.VReg] = {}
        for (_, init), param in zip(stmt.carried, frame.params):
            override[init.vid] = param
        self._overrides.append(override)

        names.push()
        for (cname, init), param in zip(stmt.carried, frame.params):
            names.define(cname, init)
        self._lower_statements(ctx, stmt.body.statements, fn, view_regs)
        back = []
        for cname, _ in stmt.carried:
            v = names.get(cname)
            if v is None:
                raise self._err(
                    loc, "while",
                    f"carried '{cname}' has no value at the body end")
            back.append(self._need(v, loc))
        scalar_mod.close_loop(ctx, frame, back)
        self._overrides.pop()
        names.pop()

        ctx.switch(frame.exit)
        for value, param in zip(stmt.join_results, frame.exit.params):
            self.values[value.vid] = param
            for key in value.scope_names():
                names.define(key, value)

    # -- one TIR op --------------------------------------------------------------
    def _lower_tir_op(self, ctx: _Ctx, op: tir.Op, fn: tir.Function,
                      view_regs: Dict[str, mir.VReg]) -> None:
        """Lower one TIR op at the current position; returns the store mask
        (the stats count source) when the op is a masked store."""
        loc = op.loc
        code = op.op

        if code == "program_id":
            axis = op.attrs["axis"]
            reg = self._pid_axis_regs.get(axis)
            if reg is None:
                raise self._err(loc, "tl.program_id",
                                f"program_id axis {axis} is outside the "
                                f"grid (the grid has {self.grid.ndim} "
                                "axis/axes)")
            self._bind_result(op, reg)
            return
        if code == "num_programs":
            axis = op.attrs["axis"]
            reg = self._np_regs.get(axis)
            if reg is None:
                raise self._err(loc, "tl.num_programs",
                                f"num_programs axis {axis} is outside the "
                                f"grid (the grid has {self.grid.ndim} "
                                "axis/axes)")
            self._bind_result(op, reg)
            return
        if code == "const":
            reg = scalar_mod.lower_const(ctx, op.attrs["value"],
                                         op.results[0].type, loc)
            self._bind_result(op, reg)
            return
        if code == "arange":
            if self._chunk is None:
                raise self._err(loc, "tl.arange",
                                "tl.arange used before any block-level "
                                "statement opened the vector chunk region")
            vid = ctx.emit(mir.MOp(
                "vid", [], [ctx.vreg(mir.VectorType(32, 1, "int"),
                                     hint="iota", loc=loc)], loc=loc))
            reg = ctx.emit(mir.MOp(
                "vbinx", [vid, self._chunk["elem"]],
                [ctx.vreg(mir.VectorType(32, 1, "int"), hint="ar",
                          loc=loc)],
                attrs={"op": "add"}, loc=loc))
            self._bind_result(op, reg)
            return
        if code == "broadcast":
            operand = self._need(op.operands[0], loc)
            if operand.is_vector():
                raise self._err(loc, "broadcast",
                                "broadcast of a block value is not in the "
                                "slice (only scalar splats)")
            reg = ctx.emit(mir.MOp(
                "s2v", [operand],
                [ctx.vreg(self._vtype(op.results[0].type), hint="splat",
                          loc=loc)], loc=loc))
            self._bind_result(op, reg)
            return
        if code == "realize":
            self.values[op.results[0].vid] = self._need(op.operands[0], loc)
            return
        if code == "ptradd":
            self.pointer_ops[op.results[0].vid] = op
            self.values[op.results[0].vid] = self._need(op.operands[0], loc)
            return
        if code in tir.BIN_ARITH or code in tir.BIN_BITWISE:
            lhs, rhs = op.operands
            lreg, rreg = self._need(lhs, loc), self._need(rhs, loc)
            if lreg.is_scalar() and rreg.is_scalar():
                reg = scalar_mod.lower_binop(ctx, op, lreg, rreg, loc)
            else:
                reg = self._vbin(ctx, op, lreg, rreg, loc)
            self._bind_result(op, reg)
            return
        if code in tir.CMP_PREDS:
            lhs, rhs = op.operands
            lreg, rreg = self._need(lhs, loc), self._need(rhs, loc)
            if lreg.is_scalar() and rreg.is_scalar():
                reg = scalar_mod.lower_cmp(ctx, op, lreg, rreg, loc)
            else:
                reg = ctx.emit(mir.MOp(
                    "vcmp", [lreg, rreg],
                    [ctx.vreg(mir.MaskType(), hint="m", loc=loc)],
                    attrs={"pred": code.split(".")[1],
                           "fp": lhs.type.is_float()}, loc=loc))
            self._bind_result(op, reg)
            return
        if code in tir.UNARY_OPS:
            operand = self._need(op.operands[0], loc)
            if operand.is_scalar():
                if code == "logical.not":
                    reg = scalar_mod.lower_not(ctx, operand, loc)
                    self._bind_result(op, reg)
                    return
                if code == "arith.neg":
                    zero = ctx.const(0, operand.type, loc)
                    reg = ctx.emit(mir.MOp(
                        "ssub", [zero, operand],
                        [ctx.vreg(operand.type, hint="neg", loc=loc)],
                        loc=loc))
                    self._bind_result(op, reg)
                    return
                raise self._err(loc, code,
                                "scalar unary op is not in the slice's "
                                "scalar core")
            vop = {"arith.fneg": "fneg", "arith.neg": "sub0",
                   "logical.not": "not", "bit.invert": "not"}.get(code)
            if vop == "sub0":
                raise self._err(loc, code,
                                "integer vector negation is not in the "
                                "slice (fneg is; neg lowers via 0-x later)")
            if vop is None:
                raise self._err(loc, code, "unary op is not in the slice")
            reg = ctx.emit(mir.MOp(
                "vunary", [operand],
                [ctx.vreg(operand.type, hint="un", loc=loc)],
                attrs={"op": vop}, loc=loc))
            self._bind_result(op, reg)
            return
        if code == "select.where":
            cond, x, y = op.operands
            mreg = self._need(cond, loc)
            xreg, yreg = self._need(x, loc), self._need(y, loc)
            v0 = ctx.emit(mir.MOp(
                "vmovmask", [mreg],
                [ctx.vreg(mir.MaskType(), hint="v0", loc=loc,
                          fixed_phys="v0")], loc=loc))
            reg = ctx.emit(mir.MOp(
                "vsel", [v0, xreg, yreg],
                [ctx.vreg(xreg.type, hint="sel", loc=loc)],
                loc=loc))
            self._bind_result(op, reg)
            return
        if code == "load":
            self._lower_load(ctx, op, loc)
            return
        if code == "store":
            mask = self._lower_store(ctx, op, loc)
            if mask is not None and self._count_reg is None \
                    and self._chunk is not None \
                    and ctx.cur is self._chunk["body"]:
                # the stored-element count: exact only when the first
                # masked store sits at the chunk body's top level (its
                # mask dominates the back edge); nested stores fall back
                # to chunk-granular counting
                self._count_reg = ctx.emit(mir.MOp(
                    "vpopc", [mask],
                    [ctx.vreg(mir.I64, hint="cnt", loc=loc)], loc=loc))
            return
        if code in ("zeros", "full"):
            ty = op.results[0].type
            value = 0 if code == "zeros" else op.attrs["value"]
            kreg = scalar_mod.lower_const(ctx, value, ty, loc)
            reg = ctx.emit(mir.MOp(
                "s2v", [kreg],
                [ctx.vreg(self._vtype(ty), hint="cst", loc=loc)], loc=loc))
            self._bind_result(op, reg)
            return
        if code == "convert":
            raise self._err(loc, "convert",
                            "value conversion is not in the vector slice "
                            "(widths agree in the slice's single-SEW form; "
                            "conversions are a later task's path)")
        if code == "bitcast":
            raise self._err(loc, "bitcast",
                            "bit reinterpretation is not in the vector slice")
        if code == "debug_barrier":
            ctx.emit0(mir.MOp("callbarrier",
                              [ctx.function.params[0]], [], loc=loc))
            return
        if code in ("dot", "reduce", "atomic_rmw", "atomic_cas",
                    "scatter", "gather"):
            from a100c.lower import matrix
            matrix.refuse_matrix(loc, code,
                                 f"construct '{code}' routes to the matrix/"
                                 "reduction path")
        raise self._err(loc, code, "op is not lowered by the vector slice")

    def _vbin(self, ctx: _Ctx, op: tir.Op, lreg: mir.VReg, rreg: mir.VReg,
              loc) -> mir.VReg:
        code = op.op
        if lreg.type != rreg.type:
            raise self._err(loc, code,
                            f"vector operand types differ: {lreg.type!r} vs "
                            f"{rreg.type!r}")
        vop = {"arith.add": "add", "arith.sub": "sub", "arith.mul": "mul",
               "bit.and": "and", "bit.or": "or", "bit.xor": "xor",
               "arith.fdiv": "fdiv", "arith.sdiv": "sdiv",
               "arith.udiv": "udiv", "arith.frem": "frem",
               "arith.srem": "srem", "arith.urem": "urem"}.get(code)
        if vop is None:
            raise self._err(loc, code, "vector binary op is not in the slice")
        if vop in ("fdiv", "sdiv", "udiv", "frem", "srem", "urem"):
            raise self._err(loc, code,
                            "division/remainder is not in the vector slice")
        return ctx.emit(mir.MOp(
            "vbin", [lreg, rreg],
            [ctx.vreg(lreg.type, hint="vb", loc=loc)],
            attrs={"op": vop}, loc=loc))

    # -- memory ops --------------------------------------------------------------
    def _address_of(self, ctx: _Ctx, ptr: tir.Value, loc):
        """Resolve one TIR pointer value to (base reg, offset reg, pointee).

        A ptradd chain (``p + a + b + off`` lowers left-associatively in
        the frontend) is flattened into ONE whole-tree sum: base + (a + b +
        off) in one expression -- never accumulated one dimension at a
        time (FE-ADDRESS-EXPRESSIONS, IR-LOWERING-CONTRACT).  A bare
        pointer parameter (``tl.load(w_ptr)``) is the zero-offset form.
        """
        offsets = []
        node = ptr
        while node.producer is not None and node.producer.op == "ptradd":
            base_value, offset_value = node.producer.operands
            offsets.append(offset_value)
            node = base_value
        if node.producer is not None:
            raise self._err(loc, ptr.name,
                            f"pointer '{ptr.name}' is not a ptradd-formed "
                            "address (the slice's whole-tree address form)")
        base_reg = self._need(node, loc)
        if not offsets:
            offset_reg = ctx.const(0, mir.I32, loc)
        else:
            offset_reg = self._sum_offsets(ctx, list(reversed(offsets)), loc)
        return base_reg, offset_reg, node.type.pointee

    def _sum_offsets(self, ctx: _Ctx, values, loc) -> mir.VReg:
        """Sum the flattened ptradd offsets, left-associatively, preserving
        each value's width and shape (modular i32 arithmetic associates)."""
        if len(values) == 1:
            return self._need(values[0], loc)
        acc = self._need(values[0], loc)
        for v in values[1:]:
            reg = self._need(v, loc)
            if acc.is_scalar() and reg.is_scalar():
                if acc.type.width != reg.type.width:
                    if acc.type.width < reg.type.width:
                        acc = scalar_mod.widen_to(ctx, acc, reg.type.width,
                                                  loc)
                    else:
                        reg = scalar_mod.widen_to(ctx, reg, acc.type.width,
                                                  loc)
                acc = ctx.emit(mir.MOp(
                    "sadd", [acc, reg],
                    [ctx.vreg(acc.type, hint="os", loc=loc)], loc=loc))
            elif acc.is_vector() and reg.is_scalar():
                if reg.type.width > acc.type.sew:
                    raise self._err(
                        loc, "ptradd",
                        f"scalar offset width {reg.type.width} exceeds the "
                        f"vector index SEW {acc.type.sew}")
                acc = ctx.emit(mir.MOp(
                    "vbinx", [acc, reg],
                    [ctx.vreg(acc.type, hint="os", loc=loc)],
                    attrs={"op": "add"}, loc=loc))
            elif acc.is_scalar() and reg.is_vector():
                if acc.type.width > reg.type.sew:
                    raise self._err(
                        loc, "ptradd",
                        f"scalar offset width {acc.type.width} exceeds the "
                        f"vector index SEW {reg.type.sew}")
                acc = ctx.emit(mir.MOp(
                    "vbinx", [reg, acc],
                    [ctx.vreg(reg.type, hint="os", loc=loc)],
                    attrs={"op": "add"}, loc=loc))
            else:
                if acc.type != reg.type:
                    raise self._err(
                        loc, "ptradd",
                        f"vector offset types differ: {acc.type!r} vs "
                        f"{reg.type!r}")
                acc = ctx.emit(mir.MOp(
                    "vbin", [acc, reg],
                    [ctx.vreg(acc.type, hint="os", loc=loc)],
                    attrs={"op": "add"}, loc=loc))
        return acc

    def _lower_load(self, ctx: _Ctx, op: tir.Op, loc) -> None:
        ptr = op.operands[0]
        mask = op.operands[1] if len(op.operands) > 1 else None
        other = op.operands[2] if len(op.operands) > 2 else None
        default = op.attrs.get("masked_default")
        if other is not None or default == tir.MaskedDefault.VALUE:
            raise self._err(loc, "tl.load",
                            "masked load with other= (default=value) is not "
                            "in the slice; the slice's masked loads declare "
                            "undef at disabled positions")
        base_reg, offset_reg, pointee = self._address_of(ctx, ptr, loc)
        if ptr.rank == 0 and (mask is None or mask.rank == 0):
            # a rank-0 load: the scalar core
            if mask is not None:
                raise self._err(loc, "tl.load",
                                "a masked scalar load is not in the scalar "
                                "core (the corpus scalar loads are "
                                "unmasked)")
            reg = scalar_mod.scalar_load(ctx, base_reg, offset_reg, pointee,
                                         loc)
            self._bind_result(op, reg)
            return
        if self._chunk is None:
            raise self._err(loc, "tl.load",
                            "a block load appears outside the vector chunk "
                            "region (block values must live inside it)")
        scaled, tree = addr_mod.materialize_address(
            ctx, base_reg, offset_reg, pointee, loc, self._vl, (self._sew, 1))
        self.trees.append(tree)
        operands = [base_reg, scaled]
        attrs = {"eew": 64, "sew": self._sew}
        if mask is not None and not self.options.witness_drop_tail_predicates:
            mreg = self._need(mask, loc)
            v0 = ctx.emit(mir.MOp(
                "vmovmask", [mreg],
                [ctx.vreg(mir.MaskType(), hint="v0", loc=loc,
                          fixed_phys="v0")], loc=loc))
            operands.append(v0)
            attrs["default"] = "undef"
        reg = ctx.emit(mir.MOp(
            "vloadix", operands,
            [ctx.vreg(self._vtype(op.results[0].type), hint="ld", loc=loc)],
            attrs=attrs, loc=loc))
        self._bind_result(op, reg)

    def _lower_store(self, ctx: _Ctx, op: tir.Op, loc) -> Optional[mir.VReg]:
        ptr, value = op.operands[0], op.operands[1]
        mask = op.operands[2] if len(op.operands) > 2 else None
        base_reg, offset_reg, pointee = self._address_of(ctx, ptr, loc)
        if ptr.rank == 0 and (mask is None or mask.rank == 0):
            if mask is not None:
                raise self._err(loc, "tl.store",
                                "a masked scalar store is not in the scalar "
                                "core")
            vreg = self._need(value, loc)
            scalar_mod.scalar_store(ctx, base_reg, offset_reg, vreg, pointee,
                                    loc)
            return None
        if self._chunk is None:
            raise self._err(loc, "tl.store",
                            "a block store appears outside the vector chunk "
                            "region (block values must live inside it)")
        scaled, tree = addr_mod.materialize_address(
            ctx, base_reg, offset_reg, pointee, loc, self._vl, (self._sew, 1))
        self.trees.append(tree)
        vreg = self._need(value, loc)
        operands = [base_reg, scaled, vreg]
        attrs = {"eew": 64, "sew": self._sew}
        mask_reg = None
        if mask is not None:
            mask_reg = self._need(mask, loc)
            if not self.options.witness_drop_tail_predicates:
                v0 = ctx.emit(mir.MOp(
                    "vmovmask", [mask_reg],
                    [ctx.vreg(mir.MaskType(), hint="v0", loc=loc,
                              fixed_phys="v0")], loc=loc))
                operands.append(v0)
                attrs["default"] = "no-access"
        ctx.emit0(mir.MOp("vstoreix", operands, [], attrs=attrs, loc=loc))
        return mask_reg

    # -- type mapping --------------------------------------------------------------
    def _vtype(self, ty: tir.Type) -> mir.VectorType:
        kind = "float" if ty.is_float() else (
            "uint" if ty.is_int_unsigned() else "int")
        return mir.VectorType(ty.bitwidth(), 1, kind)


def lower_to_mir(tir_module: tir.Module, plan: ExecutionPlan,
                 target: TargetModel, layout: ArgumentLayout,
                 grid: GridModel, options: Optional[LowerOptions] = None) -> mir.MModule:
    """Lower one verified TIR module to a verified-shape MIR module."""
    lowering = SliceLowering(tir_module, plan, target, layout, grid, options)
    module = lowering.lower()
    module.meta["sew"] = lowering._sew
    module.meta["block_extent"] = plan.block_extent
    module.meta["chunks"] = [[vl, n] for vl, n in plan.chunks]
    module.meta["address_trees"] = [t.describe() for t in lowering.trees]
    module.meta["witness"] = lowering.options.identity_part()
    module.meta["grid"] = lowering.grid.describe()
    module.meta["stats_mode"] = ("elements" if lowering._count_reg is not None
                                 else "chunks" if lowering._stats_chunk_granular
                                 else "none")
    return module
