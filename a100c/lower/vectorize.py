"""RVV vectorization: TIR -> MIR for the elementwise vector slice.

Lowers one straight-line elementwise kernel (the frontend's elementwise
core) into the complete native program shape required by the runtime ABI
(a100rt.h):

  entry      bundle/view/scalar binding, native grid evaluation, worker
             range start;
  program    the strided worker loop over source program instances
             (plan/partition), block base and bounds;
  chunk      the vector loop over the block at the target's (SEW, LMUL)
             with exact vl per chunk, masked tails (v0), whole-tree i64
             addresses (lower/addresses), and the stats popcount;
  exit       the stats store.

The TIR data path is lowered *faithfully op by op* inside the chunk body
(MECH-GENERAL-PATH-FIRST: the general, unoptimized path lands first; CSE/
LICM and friends are later tasks' switched passes on top of it).

Boundaries of this slice (each a located refusal, never a silent
approximation): kernels with control flow, non-32-bit element widths
(the whole-tree EEW=64/EMUL=2 address form is tuned to SEW=32), masked
loads with ``other=``, conversions, reductions and every matrix-routed
construct (lower/matrix refuses those).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from a100c.ir import mir, tir
from a100c.lower import addresses as addr_mod
from a100c.lower import scalar as scalar_mod
from a100c.lower.binding import ArgumentLayout
from a100c.plan.grid import Bin, GridModel, Lit, Ref
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
        self.pointer_ops: Dict[int, tir.Op] = {}
        self.trees: List[addr_mod.AddressTree] = []

    # -- helpers ---------------------------------------------------------------
    def _err(self, loc, construct: str, message: str):
        return VectorizeError(loc, construct, message)

    def value(self, t: tir.Value) -> Optional[mir.VReg]:
        return self.values.get(t.vid)

    def _need(self, t: tir.Value, loc) -> mir.VReg:
        reg = self.values.get(t.vid)
        if reg is None:
            raise self._err(loc, t.name,
                            f"TIR value '{t.name}' is not lowered before its "
                            "use (use-before-definition in the slice lowering)")
        return reg

    # -- entry -----------------------------------------------------------------
    def lower(self) -> mir.MModule:
        fns = self.tir_module.functions
        if len(fns) != 1:
            raise self._err(None, "module",
                            "the slice compiles exactly one kernel function")
        fn = fns[0]
        statements = self._straight_line(fn)
        arange_extent, arange_op = self._find_arange(statements)
        sew, _kind = self._element_width(statements, arange_extent)
        self._sew = sew
        self._statements = statements
        self._vl = 0

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

        self._emit_entry(ctx, fn)
        return module

    # -- structure analysis ------------------------------------------------------
    def _straight_line(self, fn: tir.Function) -> list:
        for stmt in fn.body.statements:
            if isinstance(stmt, (tir.If, tir.Loop)):
                raise self._err(
                    stmt.loc, type(stmt).__name__.lower(),
                    "structured control flow is not lowered by the vector "
                    "slice (the elementwise core is straight-line)")
            if not isinstance(stmt, tir.Op):
                raise self._err(None, "statement",
                                f"statement {stmt!r} is not an op")
        return list(fn.body.statements)

    def _find_arange(self, statements) -> Tuple[int, Optional[tir.Op]]:
        found = None
        for op in statements:
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

    def _element_width(self, statements, arange_extent) -> Tuple[int, str]:
        """The data SEW: the pointee width every memory op must agree on."""
        sew = None
        kind = "int"
        for op in statements:
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

    # -- the entry block ----------------------------------------------------------
    def _emit_entry(self, ctx: _Ctx, fn: tir.Function) -> None:
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

        # native grid evaluation (runtime; reading bundle scalars / extents)
        program_count = self._emit_grid_expr(ctx, self.grid.expr,
                                             grid_scalar_regs, views, loc)

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

        self._emit_program_loop(ctx, fn, program_count, wcount64, stats,
                                view_regs)

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
            kind, name = tie[0], tie[1]
            if kind == "scalar":
                reg = scalar_regs.get(name)
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
        raise self._err(loc, "grid", f"unknown grid expression node {expr!r}")

    # -- the program / chunk loops ---------------------------------------------------
    def _emit_program_loop(self, ctx: _Ctx, fn: tir.Function,
                           program_count: mir.VReg, wcount64: mir.VReg,
                           stats: mir.VReg, view_regs: Dict[str, mir.VReg]) -> None:
        loc = fn.loc
        B = self.plan.block_extent
        vl = self.plan.chunks[0][0] if self.plan.chunks else B

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
        pid32 = ctx.emit(mir.MOp(
            "strunc", [pid_b],
            [ctx.vreg(mir.I32, hint="pid32", loc=loc)], loc=loc))
        base = ctx.emit(mir.MOp(
            "smul", [pid32, ctx.const(B, mir.I32, loc)],
            [ctx.vreg(mir.I32, hint="base", loc=loc)], loc=loc))
        elem0 = base
        chunk = ctx.add_block("chunk_head", [], loc)
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "chunk_head",
                                 "args": [elem0, base, items_b, pid32, pid_b]},
                          loc=loc))

        # chunk_head(elem, base, items, pid32, pid)
        elem_h = mir.VReg(mir.I32, name="elem.loop")
        base_h = mir.VReg(mir.I32, name="base.loop")
        items_c = mir.VReg(mir.I64, name="items.chunk")
        pid32_h = mir.VReg(mir.I32, name="pid32.loop")
        pid_c = mir.VReg(mir.I64, name="pid.chunk")
        ctx.switch(chunk)
        chunk.params += [elem_h, base_h, items_c, pid32_h, pid_c]
        extent = ctx.const(B, mir.I32, loc)
        upper = ctx.emit(mir.MOp(
            "sadd", [base_h, extent],
            [ctx.vreg(mir.I32, hint="upper", loc=loc)], loc=loc))
        ccont = ctx.emit(mir.MOp(
            "slt", [elem_h, upper],
            [ctx.vreg(mir.I64, hint="cgo", loc=loc)], loc=loc))
        ctx.emit0(mir.MOp("brc", [ccont], [],
                          attrs={"true_target": "chunk_body",
                                 "true_args": [elem_h, base_h, items_c,
                                               pid32_h, pid_c],
                                 "false_target": "prog_next",
                                 "false_args": [pid_c, items_c]}, loc=loc))

        # chunk_body: the whole TIR data path, vectorized
        cbody_params = [mir.VReg(mir.I32, name="elem.body"),
                        mir.VReg(mir.I32, name="base.cbody"),
                        mir.VReg(mir.I64, name="items.cbody"),
                        mir.VReg(mir.I32, name="pid32.cbody"),
                        mir.VReg(mir.I64, name="pid.cbody")]
        cbody = ctx.add_block("chunk_body", cbody_params, loc)
        ctx.switch(cbody)
        elem_b, base_b, items_b2, pid32_b, pid_b2 = cbody_params

        avl = ctx.const(vl, mir.I32, loc)
        ctx.emit(mir.MOp(
            "vsetvli", [avl], [ctx.vreg(mir.I32, hint="vl", loc=loc)],
            attrs={"sew": self._sew, "lmul": 1, "policy": "ta,ma"}, loc=loc))

        # the TIR program_id value is the i32 loop program index
        for op in self._statements:
            if op.op == "program_id":
                self.values[op.results[0].vid] = pid32_b

        chunk_local = ctx.emit(mir.MOp(
            "ssub", [elem_b, base_b],
            [ctx.vreg(mir.I32, hint="cidx", loc=loc)], loc=loc))
        self._chunk_local = chunk_local

        counted_mask: Optional[mir.VReg] = None
        for op in self._statements:
            mask_reg = self._lower_tir_op(ctx, op, fn, view_regs)
            if mask_reg is not None and counted_mask is None:
                counted_mask = mask_reg

        # stats: count the active elements this chunk stored
        if counted_mask is not None and self.plan.counts_elements:
            cnt = ctx.emit(mir.MOp(
                "vpopc", [counted_mask],
                [ctx.vreg(mir.I64, hint="cnt", loc=loc)], loc=loc))
            items_next = ctx.emit(mir.MOp(
                "sadd", [items_b2, cnt],
                [ctx.vreg(mir.I64, hint="items2", loc=loc)], loc=loc))
        else:
            items_next = items_b2
        elem_next = ctx.emit(mir.MOp(
            "sadd", [elem_b, ctx.const(vl, mir.I32, loc)],
            [ctx.vreg(mir.I32, hint="elem2", loc=loc)], loc=loc))
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "chunk_head",
                                 "args": [elem_next, base_b, items_next,
                                          pid32_b, pid_b2]}, loc=loc))

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

    # -- one TIR op --------------------------------------------------------------
    def _lower_tir_op(self, ctx: _Ctx, op: tir.Op, fn: tir.Function,
                      view_regs: Dict[str, mir.VReg]) -> Optional[mir.VReg]:
        """Lower one TIR op inside the chunk body; returns the store mask
        (the stats count source) when the op is a masked store."""
        loc = op.loc
        code = op.op

        if code == "program_id":
            return None                       # pre-mapped to the loop index
        if code == "const":
            reg = scalar_mod.lower_const(ctx, op.attrs["value"],
                                         op.results[0].type, loc)
            self.values[op.results[0].vid] = reg
            return None
        if code == "arange":
            vid = ctx.emit(mir.MOp(
                "vid", [], [ctx.vreg(mir.VectorType(32, 1, "int"),
                                     hint="iota", loc=loc)], loc=loc))
            reg = ctx.emit(mir.MOp(
                "vbinx", [vid, self._chunk_local],
                [ctx.vreg(mir.VectorType(32, 1, "int"), hint="ar",
                          loc=loc)],
                attrs={"op": "add"}, loc=loc))
            self.values[op.results[0].vid] = reg
            return None
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
            self.values[op.results[0].vid] = reg
            return None
        if code == "realize":
            self.values[op.results[0].vid] = self._need(op.operands[0], loc)
            return None
        if code == "ptradd":
            self.pointer_ops[op.results[0].vid] = op
            self.values[op.results[0].vid] = self._need(op.operands[0], loc)
            return None
        if code in tir.BIN_ARITH or code in tir.BIN_BITWISE:
            lhs, rhs = op.operands
            lreg, rreg = self._need(lhs, loc), self._need(rhs, loc)
            if lreg.is_scalar() and rreg.is_scalar():
                reg = scalar_mod.lower_binop(ctx, op, lreg, rreg, loc)
            else:
                reg = self._vbin(ctx, op, lreg, rreg, loc)
            self.values[op.results[0].vid] = reg
            return None
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
            self.values[op.results[0].vid] = reg
            return None
        if code in tir.UNARY_OPS:
            operand = self._need(op.operands[0], loc)
            if operand.is_scalar():
                raise self._err(loc, code,
                                "scalar unary op is not in the slice's "
                                "scalar core")
            vop = {"arith.fneg": "fneg", "arith.neg": "sub0",
                   "logical.not": "not", "bit.invert": "not"}.get(code)
            if vop == "sub0":
                raise self._err(loc, code,
                                "integer negation is not in the slice "
                                "(fneg is; neg lowers via 0-x later)")
            if vop is None:
                raise self._err(loc, code, "unary op is not in the slice")
            reg = ctx.emit(mir.MOp(
                "vunary", [operand],
                [ctx.vreg(operand.type, hint="un", loc=loc)],
                attrs={"op": vop}, loc=loc))
            self.values[op.results[0].vid] = reg
            return None
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
            self.values[op.results[0].vid] = reg
            return None
        if code == "load":
            self._lower_load(ctx, op, loc)
            return None
        if code == "store":
            return self._lower_store(ctx, op, loc)
        if code in ("zeros", "full"):
            ty = op.results[0].type
            value = 0 if code == "zeros" else op.attrs["value"]
            kreg = scalar_mod.lower_const(ctx, value, ty, loc)
            reg = ctx.emit(mir.MOp(
                "s2v", [kreg],
                [ctx.vreg(self._vtype(ty), hint="cst", loc=loc)], loc=loc))
            self.values[op.results[0].vid] = reg
            return None
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
            return None
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
        """Resolve one TIR pointer value to (base reg, offset reg, pointee)."""
        if ptr.producer is None or ptr.producer.op != "ptradd":
            raise self._err(loc, ptr.name,
                            f"pointer '{ptr.name}' is not a ptradd-formed "
                            "address (the slice's whole-tree address form)")
        base_value, offset_value = ptr.producer.operands
        if base_value.producer is not None:
            raise self._err(
                loc, ptr.name,
                f"pointer base '{base_value.name}' is not a parameter (no "
                "pointer-arithmetic chains in the slice)")
        base_reg = self._need(base_value, loc)
        offset_reg = self._need(offset_value, loc)
        return base_reg, offset_reg, base_value.type.pointee

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
        self.values[op.results[0].vid] = reg

    def _lower_store(self, ctx: _Ctx, op: tir.Op, loc) -> Optional[mir.VReg]:
        ptr, value = op.operands[0], op.operands[1]
        mask = op.operands[2] if len(op.operands) > 2 else None
        base_reg, offset_reg, pointee = self._address_of(ctx, ptr, loc)
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
    return module
