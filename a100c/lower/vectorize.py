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
from a100c.plan import stages as stages_mod
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
    #: witness-only degraded build (tools/check_stage_barriers.py): the
    #: stage barrier call is dropped from the two-phase split path so the
    #: cross-worker visibility race becomes observable (the merge reads
    #: partials no barrier has published).  Never set by the normal path;
    #: recorded in the artifact identity when set.
    witness_drop_stage_barrier: bool = False
    #: witness-only degraded build (T011 test_atomics.py): the masked
    #: block atomic's disabled-lane address redirection is dropped, so the
    #: out-of-range lanes touch a poisoned guard region and the run
    #: compares FAIL (MECH-WITNESS-TEST: the no-access property is
    #: load-bearing).  Never set by the normal path; recorded in the
    #: artifact identity when set.
    witness_drop_atomic_masks: bool = False
    #: the declared numeric decision (T012): fp16/bf16 block arithmetic
    #: runs in FP32 with one rounding back at the element type (fp32
    #: stays IEEE).  bf16 has no native vector arithmetic on this target;
    #: fp16 native lanes exist (probed) and the switch selects the
    #: single-rounding policy.  Recorded in the artifact identity.
    fp16_bf16_fp32_lanes: bool = True

    def identity_part(self) -> str:
        parts = []
        if self.witness_drop_tail_predicates:
            parts.append("witness-drop-tail-predicates")
        if self.witness_drop_stage_barrier:
            parts.append("witness-drop-stage-barrier")
        if self.witness_drop_atomic_masks:
            parts.append("witness-drop-atomic-masks")
        if not self.fp16_bf16_fp32_lanes:
            parts.append("native-fp16-lanes")
        return ",".join(parts) if parts else "default"


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


def ctx_emit_view_load(sl: "SliceLowering", loc, view_index: int) -> mir.VReg:
    """One fresh view-base load at a use site (the lazy multi-view form:
    the views pointer is the single live GPR instead of one per view)."""
    ctx = sl._ctx
    return ctx.emit(mir.MOp(
        "sload", [sl._views_reg],
        [ctx.vreg(mir.I64, hint="vw", loc=loc)],
        attrs={"width": 64, "offset": view_index * 56, "ext": "sext"},
        loc=loc))


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
        #: the two-phase split plan (T009; a100c/plan/stages.py)
        self.stage_plan: Optional[stages_mod.TwoPhasePlan] = None
        #: the kernel body's (prefix, region, suffix) split: the region is
        #: the block-level statements (the chunk region); the suffix is
        #: scalar-only by construction and lowers after the region closes
        self._body_split: Optional[Tuple[list, list, list]] = None
        #: open chunk-region merge frames (vid -> spec), in slot order
        self._chunk_merges: List[dict] = []
        #: every wide-access selection (T011): the proven-contiguous loads
        #: and stores that selected the unit-stride form, with the proof's
        #: source (structural / hint) and detail -- the counter that
        #: distinguishes "selected" from "not applicable" (IR-OBSERVABILITY)
        self._wide_selections: List[dict] = []
        #: the atomic scratch region's offset/max element size (set in
        #: lower() from the kernel's atomic ops)
        self._atomic_ws_offset = 0
        self._atomic_max_esz = 4
        #: the emission context (set in lower(); _need's lazy view loads
        #: emit through it)
        self._ctx: Optional[_Ctx] = None
        #: lazy view bases: vid -> view index (multi-view kernels; set in
        #: _emit_entry from the target's register budget)
        self._lazy_view_index: Dict[int, int] = {}
        self._views_reg: Optional[mir.VReg] = None
        #: scan accumulators discovered by the pre-scan (workspace scans)
        self._scan_accs: List[dict] = []
        # -- T012: the multi-pass layout lane --------------------------------
        #: staged block values (vid -> region record): produced in one pass,
        #: consumed in a later pass or by a layout staging loop; the private
        #: workspace holds their bytes
        self._staged: Dict[int, dict] = {}
        #: vids whose producing statement must store to the staging region
        self._stage_out: set = set()
        #: the region's segments (computed in lower()): scalar groups,
        #: extent-homogeneous passes and layout staging points
        self._segments: List[tuple] = []
        #: region depth: >0 inside an if arm or loop body (staging stores
        #: are not emitted there -- a cross-pass value must be top-level)
        self._region_depth: int = 0
        #: per-pass liveout slots (pass index -> [(vid, slot)])
        self._pass_liveouts: Dict[int, List[Tuple[int, int]]] = {}
        #: vids bound inside the currently open pass (loop-local registers)
        self._pass_bound: set = set()
        #: layout staging counter (IR-OBSERVABILITY: the countable record)
        self._layout_stagings: List[dict] = []

    # -- helpers ---------------------------------------------------------------
    def _err(self, loc, construct: str, message: str):
        return VectorizeError(loc, construct, message)

    def value(self, t: tir.Value) -> Optional[mir.VReg]:
        for layer in reversed(self._overrides):
            if t.vid in layer:
                return layer[t.vid]
        return self.values.get(t.vid)

    def _need(self, t: tir.Value, loc) -> mir.VReg:
        # a lazy view base re-materializes at every use (multi-view kernels
        # whose base registers would crowd the GPR file -- the target's own
        # register budget decided at entry binding)
        view_index = getattr(self, "_lazy_view_index", {}).get(t.vid)
        if view_index is not None:
            return ctx_emit_view_load(self, loc, view_index)
        reg = self.value(t)
        if reg is None:
            rec = getattr(self, "_staged", {}).get(t.vid)
            if rec is not None:
                # a staged value: materialize its lanes from the private
                # workspace at the current pass's chunk position
                # (lane-aligned: the consumer pass's extent equals the
                # value's extent -- the verifier's lane-alignment rules)
                return self._load_staged(t, rec, loc)
            prod = t.producer
            if prod is not None and prod.op == "const":
                # a constant whose register was bound in an earlier pass:
                # constants are pure -- re-emit at the current position
                # (registers do not survive a pass loop)
                creg = scalar_mod.lower_const(self._ctx,
                                              prod.attrs["value"],
                                              t.type, loc)
                self.values[t.vid] = creg
                if self._names is not None:
                    for key in t.scope_names():
                        self._names.define(key, t)
                return creg
            raise self._err(loc, t.name,
                            f"TIR value '{t.name}' is not lowered before its "
                            "use (use-before-definition in the lowering)")
        return reg

    def _load_staged(self, t: tir.Value, rec: dict, loc) -> mir.VReg:
        """Materialize one staged value's lanes at the current position:
        ``ws[offset + (elem + lane) * esz]`` through the indexed load."""
        ctx = self._ctx
        if self._chunk is None:
            raise self._err(
                loc, "layout",
                f"a staged value ('{t.name}') is consumed outside any pass "
                "(the segmentation and the emission disagree)")
        vl = self._vl
        lane_sew = rec["lane_sew"]
        kind = "float" if rec["type"].is_float() else \
            ("uint" if rec["type"].is_int_unsigned() else "int")
        sew_v = lane_sew
        lmul = max(1, vl * sew_v // self.target.vlen_bits)
        ity = self._idx_vtype(vl)
        self._vregion(ctx, ity, loc)
        vid = ctx.emit(mir.MOp(
            "vid", [], [ctx.vreg(ity, hint="svid", loc=loc)], loc=loc))
        idx = ctx.emit(mir.MOp(
            "vbinx", [vid, self._chunk["elem"]],
            [ctx.vreg(ity, hint="sidx", loc=loc)],
            attrs={"op": "add"}, loc=loc))
        scaled, _ = self._ws_scaled(ctx, idx, rec["esz"], loc, vl)
        ws = self._workspace_private_reg(ctx, loc)
        base = ctx.emit(mir.MOp(
            "sadd", [ws, ctx.const(rec["offset"], mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="sb", loc=loc)], loc=loc))
        avl = ctx.const(vl, mir.I32, loc)
        ctx.emit(mir.MOp(
            "vsetvli", [avl], [ctx.vreg(mir.I32, hint="slr", loc=loc)],
            attrs={"sew": sew_v, "lmul": lmul, "policy": "ta,ma"},
            loc=loc))
        reg = ctx.emit(mir.MOp(
            "vloadix", [base, scaled],
            [ctx.vreg(mir.VectorType(sew_v, lmul, kind), hint="sld",
                      loc=loc)],
            attrs={"eew": 64, "sew": sew_v}, loc=loc))
        if rec.get("mask"):
            # a boolean block reloads as a mask (the lanes are 0/1)
            zero = self._splat_const(
                ctx, 0, mir.VectorType(sew_v, lmul, kind), loc)
            reg = ctx.emit(mir.MOp(
                "vcmp", [reg, zero],
                [ctx.vreg(mir.MaskType(), hint="slm", loc=loc)],
                attrs={"pred": "ne", "fp": False}, loc=loc))
        elif rec["type"].is_float() and rec["type"].bitwidth() < lane_sew:
            # a 16-bit float reloads through the RTNE narrowing (the
            # exact round trip of the exact widening)
            reg = self._f32_to_ff(ctx, reg, rec["type"], loc)
        elif rec["type"].bitwidth() < lane_sew:
            # a sub-32 integer reloads through the register view (the
            # low bits of each lane are the value)
            reg = self._int_narrow(ctx, reg, lane_sew,
                                   rec["type"].bitwidth(), loc)
        # restore the pass's data region (the consumer ops expect it)
        self._restore_region(ctx, loc)
        self.values[t.vid] = reg
        if self._names is not None:
            for key in t.scope_names():
                self._names.define(key, t)
        return reg

    def _bind_result(self, op: tir.Op, reg: mir.VReg) -> None:
        """Record one op result's MIR register AND its scope names (the
        name environment the region joins and loop back edges read)."""
        self.values[op.results[0].vid] = reg
        if self._chunk is not None:
            self._pass_bound.add(op.results[0].vid)
        if self._names is not None:
            for key in op.results[0].scope_names():
                self._names.define(key, op.results[0])
        # a staged-destined value stores its lanes to the staging region
        # right here (top level of the current pass's chunk body; a value
        # defined inside a runtime region cannot cross a pass boundary)
        if op.results[0].vid in getattr(self, "_stage_out", set()):
            self._store_staged(op.results[0], reg, op.loc)

    def _store_staged(self, t: tir.Value, reg: mir.VReg, loc) -> None:
        if self._region_depth > 0:
            raise self._err(
                loc, "layout",
                f"a block value ('{t.name}') defined inside a runtime "
                "region cannot cross a pass boundary (the layout lane "
                "stages top-level values only)")
        if self._chunk is None:
            raise self._err(
                loc, "layout",
                f"a staged value ('{t.name}') is produced outside any "
                "pass (the segmentation and the emission disagree)")
        ctx = self._ctx
        rec = self._staged[t.vid]
        vl = self._vl
        ity = self._idx_vtype(vl)
        self._vregion(ctx, ity, loc)
        vid = ctx.emit(mir.MOp(
            "vid", [], [ctx.vreg(ity, hint="tvid", loc=loc)], loc=loc))
        idx = ctx.emit(mir.MOp(
            "vbinx", [vid, self._chunk["elem"]],
            [ctx.vreg(ity, hint="tidx", loc=loc)],
            attrs={"op": "add"}, loc=loc))
        scaled, _ = self._ws_scaled(ctx, idx, rec["esz"], loc, vl)
        ws = self._workspace_private_reg(ctx, loc)
        base = ctx.emit(mir.MOp(
            "sadd", [ws, ctx.const(rec["offset"], mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="tb", loc=loc)], loc=loc))
        if not reg.is_vector() and not reg.is_mask():
            raise self._err(
                loc, "layout",
                f"a staged value ('{t.name}') lowered to a scalar register "
                "(the segmentation and the emission disagree)")
        lane_sew = rec["lane_sew"]
        lane_lmul = max(1, vl * lane_sew // self.target.vlen_bits)
        lane_kind = "float" if rec["type"].is_float() else "uint"
        if reg.is_mask():
            # a boolean block stages as 0/1 at the lane width
            i32 = mir.VectorType(lane_sew, lane_lmul, "int")
            self._vregion(ctx, i32, loc, vl=vl)
            one = self._splat_const(ctx, 1, i32, loc)
            zero = self._splat_const(ctx, 0, i32, loc)
            v0 = ctx.emit(mir.MOp(
                "vmovmask", [reg],
                [ctx.vreg(mir.MaskType(), hint="tb0", loc=loc,
                          fixed_phys="v0")], loc=loc))
            bytes_reg = ctx.emit(mir.MOp(
                "vsel", [v0, one, zero],
                [ctx.vreg(i32, hint="tb1", loc=loc)], loc=loc))
            ctx.emit0(mir.MOp(
                "vstoreix", [base, scaled, bytes_reg], [],
                attrs={"eew": 64, "sew": lane_sew}, loc=loc))
            self._restore_region(ctx, loc)
            return
        store_reg = reg
        if reg.type.sew < lane_sew:
            if reg.type.kind == "float":
                # a 16-bit float stages as its exact fp32 widening
                store_reg = self._f16_to_f32(ctx, reg, rec["type"], loc)
            else:
                # a sub-32 integer stages zext-widened (the low bits
                # survive the round trip); _int_widen retypes each step
                # to the lanes-derived class (the register budget)
                store_reg = self._int_widen(
                    ctx, reg, reg.type.sew, lane_sew, False, loc)
        avl = ctx.const(vl, mir.I32, loc)
        ctx.emit(mir.MOp(
            "vsetvli", [avl], [ctx.vreg(mir.I32, hint="tsr", loc=loc)],
            attrs={"sew": store_reg.type.sew,
                   "lmul": store_reg.type.lmul,
                   "policy": "ta,ma"}, loc=loc))
        ctx.emit0(mir.MOp(
            "vstoreix", [base, scaled, store_reg], [],
            attrs={"eew": 64, "sew": store_reg.type.sew}, loc=loc))
        # restore the pass's data region
        self._restore_region(ctx, loc)

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

        # the default region (the prescans and the prefix scalars' index
        # class; refined per pass below)
        self._sew = 32
        self._vl = self.target.vlmax(32, 1)
        # the reduction stage plan (T009): the two-phase split eligibility,
        # the partials and their merge rules (a100c/plan/stages.py); the
        # kernel body's (prefix, region, suffix) split follows it
        self.stage_plan = stages_mod.build_stage_plan(self.tir_module)
        self._body_split = self._split_body(statements)
        self._prescan_scans(fn.body)

        # T012: the multi-pass layout lane.  The region's statements are
        # segmented into extent-homogeneous passes and layout staging
        # points; every pass is its own chunk loop over its own extent at
        # its own SEW, and layout data movement runs through dedicated
        # staging loops over the private workspace.
        region = self._body_split[1] if self._body_split else []
        self._segments = self._segment_region(region)
        self._layout_ws_base = 0
        self._layout_ws_end = 0

        # per-pass parameters (extent, SEW, vl, chunk count); the legacy
        # defaults come from the first arange (single-pass kernels keep
        # exactly today's shape)
        arange_extent, arange_op = self._find_arange(fn.body)
        self._pass_params: List[dict] = []
        max_extent = arange_extent
        for seg in self._segments:
            if seg[0] != "pass":
                self._pass_params.append(None)
                continue
            extent, sew = seg[2], seg[3] or 32
            # the 32-lane cap: every register class stays within m2 (the
            # allocator's declared budget; the e64 index class at 32 lanes
            # is m2 -- wider SEWs simply use fewer lanes per chunk)
            cap = min(self.target.vlmax(sew, 1), 32)
            if extent <= cap:
                chunks = self.target.chunk_plan(extent, sew, 1)
                vls = {vl for vl, _ in chunks}
                if len(vls) != 1:
                    raise self._err(
                        arange_op.loc if arange_op else None, "tl.arange",
                        f"block extent {extent} does not split into uniform "
                        f"vector chunks at SEW {sew} (mixed-chunk tails "
                        "are not in the slice)")
                vl = vls.pop()
            else:
                # the largest power-of-two chunk size at or below the cap
                # that divides the extent (every iteration full)
                vl = cap
                while vl > 1 and extent % vl:
                    vl //= 2
                if extent % vl:
                    raise self._err(
                        arange_op.loc if arange_op else None, "tl.arange",
                        f"block extent {extent} does not split into uniform "
                        f"vector chunks at SEW {sew}")
                chunks = tuple((vl, 1) for _ in range(extent // vl))
            self._pass_params.append({"extent": extent, "sew": sew,
                                      "vl": vl,
                                      "chunks": chunks})
            max_extent = max(max_extent, extent)
        # the default region (the prefix scalars' index class and the
        # single-pass form): the first pass's, else the arange's
        if self._pass_params and self._pass_params[0] is not None:
            first = self._pass_params[0]
        else:
            first = {"extent": arange_extent, "sew": 32,
                     "vl": self.target.vlmax(32, 1), "chunks": ()}
        self._sew = first["sew"]
        self._vl = first["vl"]
        self.plan.chunks = first["chunks"] or ((self._vl, 1),)
        self.plan.block_extent = max_extent
        self._default_pass = first

        # the workspace requirements: scans materialize the block through
        # the worker-private region; the two-phase partials live in the
        # shared region (stride fixed at the maximum worker count)
        private_bytes = self.plan.workspace_private
        if self._scan_accs:
            private_bytes = max(private_bytes, max_extent * 4)
        # the atomic scratch region (T011): per-lane old values reloaded
        # as the block result, then the 8-byte redirect slot disabled
        # lanes' atomics are redirected to (no access at the disabled
        # position's own address)
        self._atomic_ws_offset = private_bytes
        self._atomic_max_esz = 4
        has_atomic = False
        for op in self._walk_ops(fn.body):
            if isinstance(op, tir.Op) and op.op in ("atomic_rmw",
                                                    "atomic_cas"):
                has_atomic = True
                width = op.operands[0].type.pointee.bitwidth()
                if width in (32, 64):
                    self._atomic_max_esz = max(self._atomic_max_esz,
                                               width // 8)
        if has_atomic:
            private_bytes += self._vl * self._atomic_max_esz + 8
        # the gather materialization region: the whole block at 4 bytes
        # (the source stores its chunk slice; the gather reads ws[index])
        self._gather_ws_offset = private_bytes
        has_gather = any(
            isinstance(op, tir.Op) and op.op == "gather"
            for op in self._walk_ops(fn.body))
        if has_gather:
            private_bytes += max_extent * 4
        # the layout staging regions (T012): one per staged block value,
        # at its own element size
        self._layout_ws_base = private_bytes
        self._analyze_staging()
        private_bytes = max(private_bytes, self._layout_ws_end)
        if self._staged and self.stage_plan is not None \
                and self.stage_plan.eligible:
            # cross-chunk staging is sequential within one worker: the
            # worker-strided two-phase split cannot host it (the partial
            # merge still rides the normal path's chunk back edge)
            self.stage_plan.eligible = False
            self.stage_plan.reason = (
                "layout staging (the T012 multi-pass lane) is sequential "
                "per worker; the reduction rides the normal per-program "
                "path")
        # the live-out scalars: chunk-invariant region values the suffix
        # consumes (the trailing store's address arithmetic lowered inside
        # the region) -- stored at the back edge, reloaded at the exit
        self._liveouts: List[Tuple[int, int]] = []
        if self._body_split is not None and self._body_split[1] \
                and self._body_split[2]:
            region, suffix = self._body_split[1], self._body_split[2]
            region_defined = set()
            for st in region:
                if isinstance(st, tir.Op):
                    region_defined.update(r.vid for r in st.results)
            partial_vids = {p.value_id for p in
                            (self.stage_plan.partials
                             if self.stage_plan else [])}
            partial_vids.update(p.pair_value_id for p in
                                (self.stage_plan.partials
                                 if self.stage_plan else [])
                            if p.pair_value_id is not None)
            partial_vids.update(f["vid"] for f in self._scan_accs)
            prefix_defined = set()
            for st in self._body_split[0]:
                if isinstance(st, tir.Op):
                    prefix_defined.update(r.vid for r in st.results)

            def consumed(statements):
                out = set()

                def add(value):
                    if value is None or value.vid in out:
                        return
                    out.add(value.vid)
                    # transitive through the ptradd chains the memory ops
                    # flatten at address resolution: a suffix store of
                    # ``ptr + off`` consumes off's producers too
                    prod = value.producer
                    if prod is not None and prod.op == "ptradd":
                        for operand in prod.operands:
                            add(operand)

                for st in statements:
                    if isinstance(st, tir.Op):
                        for o in st.operands:
                            add(o)
                    elif isinstance(st, tir.If):
                        out.update(consumed(st.then.statements))
                        out.update(consumed(st.els.statements))
                    elif isinstance(st, tir.Loop):
                        for bound in (st.lower, st.upper, st.step, st.cond):
                            if bound is not None:
                                add(bound)
                        for _, init in st.carried:
                            add(init)
                        out.update(consumed(st.body.statements))
                return out

            for vid in sorted(consumed(suffix) & region_defined):
                if vid in partial_vids or vid in prefix_defined:
                    continue
                self._liveouts.append((vid, private_bytes))
                private_bytes += 8
        self.plan.workspace_private = private_bytes
        if self.stage_plan.eligible and self.stage_plan.partials:
            self.plan.workspace_shared = max(
                self.plan.workspace_shared,
                self.stage_plan.layout_for(8).total_bytes)

        # T012: per-pass cross-pass scalar liveouts.  A scalar defined
        # inside one pass's chunk loop and consumed in a later pass (or the
        # suffix) cannot keep its register: it stores at the defining
        # pass's back edge and reloads at the exit.  Constants re-emit
        # instead (pure); staged block values ride the layout regions.
        self._pass_liveouts = {}
        suffix = self._body_split[2] if self._body_split else []
        seg_index = 0
        for si, seg in enumerate(self._segments):
            if seg[0] != "pass":
                continue
            defined = self._pass_defined_vids(seg[1])
            later_uses: set = set()
            for later in self._segments[si + 1:]:
                if later[0] == "scalar":
                    continue
                if later[0] == "layout":
                    later_uses.update(v.vid for v in later[1].operands
                                      if v.rank == 0)
                else:
                    for st in later[1]:
                        later_uses.update(v.vid for v in self._region_uses(st)
                                          if v.rank == 0)
            for st in suffix:
                for v in self._region_uses(st):
                    if v.rank == 0:
                        later_uses.add(v.vid)
            cross = set()
            for vid in defined:
                if vid in later_uses and vid not in self._staged:
                    v = self._value_by_vid(vid)
                    if v.producer is not None and v.producer.op == "const":
                        continue          # constants re-emit at their uses
                    cross.add(vid)
            if cross:
                self._pass_liveouts[si] = [
                    (vid, private_bytes + 8 * k)
                    for k, vid in enumerate(sorted(cross))]
                private_bytes += 8 * len(cross)
            seg_index += 1
        self.plan.workspace_private = private_bytes

        module = mir.MModule(self.tir_module.name, self.tir_module.source_path)
        launch = mir.VReg(mir.I64, name="launch")
        function = mir.MFunction("operator_entry", [launch], fn.loc)
        module.functions.append(function)
        ctx = _Ctx(module, function)
        self._ctx = ctx
        ctx.add_block("entry", [launch], fn.loc)
        ctx.switch(ctx.blocks["entry"])

        self._emit_entry(ctx, fn, statements)
        self._ensure_vsetvli_regions(ctx, module)
        module.meta["stage_plan"] = self.stage_plan.describe()
        return module

    def _split_body(self, statements) -> Tuple[list, list, list]:
        """(prefix, region, suffix): the region is the block-level
        statements (first to last); everything after the last block-level
        statement is scalar-only by construction and lowers after the
        chunk region closes -- once, on the merged values.

        Mid-region guard: a scalar statement positioned between a
        reduction partial's producer and a LATER block-level statement
        would execute per chunk and read the per-chunk partial (not the
        merged value) -- a located refusal names it (the value is only
        correct after the region closes; a later block statement needs
        the chunk region, so the computation cannot be deferred)."""
        idx = [i for i, st in enumerate(statements) if self._stmt_is_block(st)]
        if not idx:
            return list(statements), [], []
        first, last = idx[0], idx[-1]
        prefix = list(statements[:first])
        region = list(statements[first:last + 1])
        suffix = list(statements[last + 1:])
        partial_vids = set()
        if self.stage_plan is not None:
            for p in self.stage_plan.partials:
                partial_vids.add(p.value_id)
                if p.pair_value_id is not None:
                    partial_vids.add(p.pair_value_id)
        if partial_vids:
            producers = [i for i, st in enumerate(region)
                         if self._produces_partial(st, partial_vids)]
            for pi in producers:
                for j in range(pi + 1, len(region)):
                    later = region[j]
                    if self._stmt_is_block(later):
                        break        # the later block statement re-opens
                        # the chunk context; scalars before it run per
                        # chunk -- checked below only when they consume a
                        # partial
                    if self._consumes_partial(later, partial_vids, ()):
                        raise self._err(
                            getattr(later, "loc", None), "reduce",
                            "a scalar computation between the reduction "
                            "and a later block statement would read the "
                            "per-chunk partial (its value is only correct "
                            "after the region closes); restructure the "
                            "kernel or wait for the multi-region path")
        return prefix, region, suffix

    def _consumes_partial(self, st, partial_vids: set,
                          seen: tuple) -> bool:
        """Does the statement consume a reduction partial directly?"""
        if isinstance(st, tir.Op):
            return any(o.vid in partial_vids for o in st.operands)
        if isinstance(st, tir.If):
            if st.cond.vid in partial_vids:
                return True
            return any(self._consumes_partial(s, partial_vids, seen)
                       for s in list(st.then.statements)
                       + list(st.els.statements))
        if isinstance(st, tir.Loop):
            for bound in (st.lower, st.upper, st.step, st.cond):
                if bound is not None and bound.vid in partial_vids:
                    return True
            if any(init.vid in partial_vids for _, init in st.carried):
                return True
            return any(self._consumes_partial(s, partial_vids, seen)
                       for s in st.body.statements)
        return False

    def _produces_partial(self, st, partial_vids: set) -> bool:
        """Does one statement produce a reduction partial (a reduce result
        or a reduction loop's join)?"""
        if isinstance(st, tir.Op) and st.op == "reduce":
            return any(r.vid in partial_vids for r in st.results)
        if isinstance(st, tir.Loop):
            return any(j.vid in partial_vids for j in st.join_results)
        return False

    def _prescan_scans(self, body: tir.Block) -> None:
        """Discover scan ops before the chunk region opens: their running
        accumulators ride the chunk back edge (merge=pass) and their block
        materializes through the worker-private workspace."""
        for op in self._walk_ops(body):
            if isinstance(op, tir.Op) and op.op == "scan":
                if op.attrs.get("reverse"):
                    raise self._err(
                        op.loc, "tl.cumsum/cumprod",
                        "reverse=True (a suffix scan) needs a second pass "
                        "over the block; the forward scan's incremental "
                        "chunk carry cannot express it (a located refusal, "
                        "never a wrong order)")
                if op.results[0].rank != 1 or len(op.results[0].shape) != 1:
                    raise self._err(
                        op.loc, "tl.cumsum/cumprod",
                        "scans along a non-last axis of a multi-axis block "
                        "are not in this path (the layout lane owns "
                        "multi-axis blocks)")
                self._scan_accs.append({
                    "vid": op.results[0].vid,
                    "kind": op.attrs["kind"],
                    "vtype": self._vtype(op.results[0].type),
                    "loc": op.loc,
                })

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
        """The reference arange of the kernel (T012: multiple aranges are
        legal -- each pass owns its own index space; the first is the
        legacy reference for the single-pass form)."""
        found = None
        for op in self._walk_ops(body):
            if op.op == "arange":
                if found is None:
                    found = op
        if found is None:
            raise self._err(None, "tl.arange",
                            "no tl.arange in the kernel body; the vector slice "
                            "lowers the one-block elementwise form")
        return found.attrs["end"] - found.attrs["start"], found

    # -- T012: segmentation (the multi-pass layout lane) -----------------------

    def _flat_extent_of(self, shape: tir.Shape, loc, what: str) -> int:
        n = tir.flat_extent(shape)
        if n is None:
            raise self._err(
                loc, what,
                f"a layout block must be compile-time shaped, got "
                f"{list(shape)} (a runtime-symbolic extent is not "
                "re-partitionable)")
        return n

    def _is_layout_op(self, st) -> bool:
        """A top-level statement that changes the flat index space (or
        permutes it): the pass closes and the op lowers through staging.
        Metadata (reshape/realize/identity) and extent-1 splats stay
        in-pass."""
        if not isinstance(st, tir.Op):
            return False
        if st.op in tir.LAYOUT_OPS:
            return True
        if st.op == "broadcast":
            src = st.operands[0]
            if src.rank == 0:
                return False               # the scalar splat (in-pass)
            n_src = self._flat_extent_of(src.shape, st.loc, "broadcast")
            if n_src == 1:
                return False               # a lane-0 splat (in-pass)
            return True
        return False

    def _seg_is_scalar(self, st) -> bool:
        if isinstance(st, tir.Op):
            return all(getattr(o, "rank", 0) == 0 for o in st.operands) \
                and all(r.rank == 0 for r in st.results)
        if isinstance(st, tir.If):
            return self._seg_is_scalar(st.cond) and \
                all(self._seg_is_scalar(s) for s in st.then.statements) and \
                all(self._seg_is_scalar(s) for s in st.els.statements)
        if isinstance(st, tir.Loop):
            for b in (st.lower, st.upper, st.step, st.cond):
                if b is not None and b.rank > 0:
                    return False
            if any(init.rank > 0 for _, init in st.carried):
                return False
            return all(self._seg_is_scalar(s) for s in st.body.statements)
        return True

    def _stmt_extent(self, st, loc=None) -> Optional[int]:
        """The flat block extent of one statement (None when scalar-only);
        a runtime region must be extent-homogeneous with its pass.  A PURE
        extent-1 statement (a splat source: tl.full([1], ...), the
        extent-1 broadcasts) is pass-agnostic -- it joins any pass; a
        statement with effects (memory, reduction, scan) always
        constrains."""
        if isinstance(st, tir.Op):
            if st.op in ("load", "store", "atomic_rmw", "atomic_cas",
                         "reduce", "scan", "sort", "topk", "histogram",
                         "gather"):
                for v in list(st.results) + list(st.operands):
                    if v.rank > 0:
                        return self._flat_extent_of(v.shape, st.loc or loc,
                                                    st.op)
                return None
            # results first (a broadcast's result carries the pass extent,
            # not its extent-1 source); operands cover the reduce forms
            for v in list(st.results) + list(st.operands):
                if v.rank > 0:
                    n = self._flat_extent_of(v.shape, st.loc or loc,
                                             st.op)
                    if n == 1:
                        continue      # a splat source: pass-agnostic
                    return n
            return None
        if isinstance(st, tir.If):
            ext = None
            for s in list(st.then.statements) + list(st.els.statements):
                e = self._stmt_extent(s, st.loc)
                if e is not None and ext is not None and e != ext:
                    raise self._err(
                        st.loc, "if",
                        f"a runtime region mixes block extents {ext} and "
                        f"{e} (the layout lane lowers extent-homogeneous "
                        "regions)")
                if e is not None:
                    ext = e
            if st.cond.rank > 0:
                c = self._flat_extent_of(st.cond.shape, st.loc, "if")
                if ext is not None and c != ext:
                    raise self._err(
                        st.loc, "if",
                        f"a runtime region mixes block extents {ext} and "
                        f"{c} (the layout lane lowers extent-homogeneous "
                        "regions)")
                ext = c
            return ext
        if isinstance(st, tir.Loop):
            ext = None
            for b in (st.lower, st.upper, st.step, st.cond):
                if b is not None and b.rank > 0:
                    c = self._flat_extent_of(b.shape, st.loc, "loop")
                    if ext is not None and c != ext:
                        raise self._err(
                            st.loc, "loop",
                            f"a runtime region mixes block extents {ext} and "
                            f"{c} (the layout lane lowers extent-homogeneous "
                            "regions)")
                    ext = c
            for _, init in st.carried:
                if init.rank > 0:
                    c = self._flat_extent_of(init.shape, st.loc, "loop")
                    if ext is not None and c != ext:
                        raise self._err(
                            st.loc, "loop",
                            f"a runtime region mixes block extents {ext} "
                            f"and {c} (the layout lane lowers "
                            "extent-homogeneous regions)")
                    ext = c
            for s in st.body.statements:
                e = self._stmt_extent(s, st.loc)
                if e is not None and ext is not None and e != ext:
                    raise self._err(
                        st.loc, "loop",
                        f"a runtime region mixes block extents {ext} and "
                        f"{e} (the layout lane lowers extent-homogeneous "
                        "regions)")
                if e is not None:
                    ext = e
            return ext
        return None

    def _stmt_sew(self, st) -> Optional[int]:
        """The data-SEW contribution of one statement: the pointee width of
        its block memory ops (None when it has none)."""
        sew = None
        if isinstance(st, tir.Op):
            if st.op in ("load", "store"):
                if st.operands[0].rank > 0:
                    pointee = st.operands[0].type.pointee
                    if pointee.is_bool():
                        raise self._err(
                            st.loc, st.op,
                            "i1 pointee widths are not in the slice (a "
                            "bool backing store is the dtype-surface lane)")
                    sew = pointee.bitwidth()
            return sew
        if isinstance(st, (tir.If, tir.Loop)):
            blocks = st.then.statements + st.els.statements \
                if isinstance(st, tir.If) else st.body.statements
            for s in blocks:
                w = self._stmt_sew(s)
                if w is not None and (sew is None or w > sew):
                    sew = w
        return sew

    def _segment_region(self, region: list) -> List[tuple]:
        """Partition the region's statements into segments:

        * ``("scalar", stmts)`` -- straight-line rank-0 statements (emitted
          between passes, outside any chunk loop);
        * ``("pass", stmts, extent, sew)`` -- an extent-homogeneous pass
          (one chunk loop over the extent at the pass's SEW);
        * ``("layout", op)`` -- a layout data-movement op (the pass closes;
          the op lowers through its staging loop(s)).

        Mid-pass scalar statements lower inside the pass (today's
        behavior); scalars between passes lower straight-line.
        """
        segs: List[tuple] = []
        cur: list = []
        cur_extent = None
        cur_sew = None

        def close():
            nonlocal cur, cur_extent, cur_sew
            if cur:
                segs.append(("pass", cur, cur_extent, cur_sew))
                cur, cur_extent, cur_sew = [], None, None

        for st in region:
            if self._is_layout_op(st):
                close()
                segs.append(("layout", st))
                continue
            if self._seg_is_scalar(st):
                if cur:
                    cur.append(st)     # mid-pass scalar: inside the chunk
                else:
                    segs.append(("scalar", [st]))
                continue
            extent = self._stmt_extent(st)
            sew = self._stmt_sew(st)
            if extent is None and not self._seg_is_scalar(st):
                # a block statement whose extents are all splat-agnostic
                # (pure extent-1 sources): it joins the open pass, or
                # lowers straight-line between passes (a splat register
                # is loop-invariant)
                if cur:
                    cur.append(st)
                else:
                    segs.append(("scalar", [st]))
                continue
            if cur and extent != cur_extent:
                close()
            if cur and sew is not None and cur_sew is not None \
                    and sew != cur_sew:
                close()
            if not cur:
                cur_extent, cur_sew = extent, sew
            else:
                if sew is not None:
                    cur_sew = sew if cur_sew is None else max(cur_sew, sew)
            cur.append(st)
        close()
        return segs

    def _analyze_staging(self) -> None:
        """Compute the staged-value set and the workspace layout.

        A value is staged when (a) it is a block operand of a layout op,
        or (b) it is a block value whose definition segment precedes its
        first use segment (it crosses a pass boundary; registers do not
        survive a pass loop).  Layout results are staged by construction.
        """
        # (a) layout operands
        for seg in self._segments:
            if seg[0] != "layout":
                continue
            op = seg[1]
            for v in op.operands:
                if v.rank > 0 and v.vid not in self._staged:
                    self._staged[v.vid] = {"pending": True}
                    self._stage_out.add(v.vid)
        # (b) cross-pass block values: definition segment index vs use
        defined_in: Dict[int, int] = {}
        seg_index = 0
        for seg in self._segments:
            if seg[0] == "scalar":
                continue
            if seg[0] == "layout":
                op = seg[1]
                for r in op.results:
                    defined_in[r.vid] = seg_index
                    self._staged[r.vid] = {"pending": True}
                seg_index += 1
                continue
            for st in seg[1]:
                for r in getattr(st, "results", ()):
                    defined_in[r.vid] = seg_index
                # region joins/loops define values too
                self._region_defs(st, defined_in, seg_index)
            seg_index += 1
        # the uses: walk every statement's operands per segment
        seg_index = 0
        for seg in self._segments:
            if seg[0] == "scalar":
                continue
            uses: List[tir.Value] = []
            if seg[0] == "layout":
                uses.extend(seg[1].operands)
            else:
                for st in seg[1]:
                    uses.extend(self._region_uses(st))
            for v in uses:
                if v.rank == 0 or v.producer is None:
                    continue
                d = defined_in.get(v.vid)
                if d is not None and d < seg_index and \
                        v.vid not in self._staged:
                    self._staged[v.vid] = {"pending": True}
                    self._stage_out.add(v.vid)
            seg_index += 1
        # suffix uses (the plan's liveouts are scalars; block values used
        # by the suffix would cross the last pass -- refuse: the suffix is
        # scalar-only by construction)
        # allocate the workspace regions: a deterministic bump per staged
        # value (correct and simple; the layout regions are the value's
        # own storage -- no aliasing by construction).  Boolean blocks
        # stage as 0/1 bytes and reload as masks (a mask register cannot
        # cross a pass loop; the byte form is the typed carrier).
        offset = self._layout_ws_base
        for vid in sorted(self._staged.keys()):
            v = self._value_by_vid(vid)
            extent = self._flat_extent_of(v.shape, v.loc, "layout")
            rec = self._staged[vid]
            rec["offset"] = offset
            rec["extent"] = extent
            rec["type"] = v.type
            # the staging lane width: the indexed memory forms with an
            # e64 index SEGFAULT the pinned QEMU when the data element
            # is narrower than 32 bits (probed: e8/e16 data + e64m2
            # index at avl 32 crashes; e32 data works -- complex_pack's
            # fp16 staging already rides the fp32 compute lanes).  Every
            # staged region therefore uses 32-bit (or wider) lanes:
            # sub-32 floats stage as their exact fp32 widening (the
            # RTNE round trip is the identity), sub-32 integers stage
            # zext-widened (the low bits survive), boolean blocks as
            # 0/1 lanes.
            rec["lane_sew"] = max(32, v.type.bitwidth())
            if v.type.is_bool():
                rec["esz"] = 4
                rec["mask"] = True
            else:
                rec["esz"] = rec["lane_sew"] // 8
            offset += extent * rec["esz"]
        self._layout_ws_end = offset

    def _region_defs(self, st, defined_in: Dict[int, int], seg_index: int,
                     depth: int = 0) -> None:
        if isinstance(st, tir.Op):
            return
        if isinstance(st, tir.If):
            for v in st.join_results:
                defined_in[v.vid] = seg_index
            for s in list(st.then.statements) + list(st.els.statements):
                self._region_defs(s, defined_in, seg_index, depth + 1)
        elif isinstance(st, tir.Loop):
            for v in st.join_results:
                defined_in[v.vid] = seg_index
            for s in st.body.statements:
                self._region_defs(s, defined_in, seg_index, depth + 1)

    def _region_uses(self, st) -> List[tir.Value]:
        out: List[tir.Value] = []

        def add(value):
            # transitive through the ptradd chains the memory ops flatten
            # at address resolution: a consumer of ``ptr + off`` consumes
            # off's producers too (the liveout analysis's rule, applied to
            # the staging analysis)
            if value is None or value in seen:
                return
            seen.add(value)
            out.append(value)
            prod = value.producer
            if prod is not None and prod.op == "ptradd":
                for operand in prod.operands:
                    add(operand)

        seen: set = set()
        if isinstance(st, tir.Op):
            for v in st.operands:
                add(v)
        elif isinstance(st, tir.If):
            add(st.cond)
            for s in list(st.then.statements) + list(st.els.statements):
                out.extend(self._region_uses(s))
        elif isinstance(st, tir.Loop):
            for b in (st.lower, st.upper, st.step, st.cond):
                if b is not None:
                    add(b)
            for _, init in st.carried:
                add(init)
            for s in st.body.statements:
                out.extend(self._region_uses(s))
        return out

    def _value_by_vid(self, vid: int) -> tir.Value:
        for fn in self.tir_module.functions:
            found = self._find_value(fn.body, vid)
            if found is not None:
                return found
        raise self._err(None, "layout", f"no TIR value with vid {vid}")

    def _find_value(self, block: tir.Block, vid: int) -> Optional[tir.Value]:
        for stmt in block.statements:
            if isinstance(stmt, tir.Op):
                for r in stmt.results:
                    if r.vid == vid:
                        return r
                for o in stmt.operands:
                    if o.vid == vid:
                        return o
            elif isinstance(stmt, tir.If):
                for v in (stmt.cond,):
                    if v.vid == vid:
                        return v
                for b in (stmt.then, stmt.els):
                    r = self._find_value(b, vid)
                    if r is not None:
                        return r
                for v in stmt.join_results:
                    if v.vid == vid:
                        return v
            elif isinstance(stmt, tir.Loop):
                for b in (stmt.lower, stmt.upper, stmt.step, stmt.cond):
                    if b is not None and b.vid == vid:
                        return b
                for _, init in stmt.carried:
                    if init.vid == vid:
                        return init
                r = self._find_value(stmt.body, vid)
                if r is not None:
                    return r
                for v in stmt.join_results:
                    if v.vid == vid:
                        return v
        return None

    def _element_width(self, body: tir.Block, arange_extent) -> Tuple[int, str]:
        """The data SEW: the pointee width every BLOCK memory op must agree
        on.  Rank-0 accesses ride the scalar core (any width it supports,
        including the 64-bit pointer-table loads); only block accesses
        select the vector region."""
        sew = None
        kind = "int"
        for op in self._walk_ops(body):
            if op.op in ("load", "store"):
                if op.operands[0].rank == 0:
                    continue         # the scalar core's own width domain
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
        self._worker_id_reg = worker_id
        self._worker_count_reg = worker_count

        # scalar bindings (record-kind aware); the i64 view used by the grid
        grid_scalar_regs: Dict[str, mir.VReg] = {}
        for binding in self.layout.scalars:
            is_float = binding.tir_type.is_float()
            reg = ctx.emit(mir.MOp(
                "sload", [scalars],
                [ctx.vreg(mir.ScalarType(binding.width,
                                         signed=binding.signed,
                                         float=is_float),
                          hint=binding.name, loc=loc)],
                attrs={"width": binding.width,
                       "offset": binding.record_index * 16 + 8,
                       "ext": "sext" if binding.signed else "zext"},
                loc=loc))
            wide = reg
            if binding.width != 64:
                if binding.tir_type.is_float():
                    # a floating scalar binds at its own width (raw bits);
                    # arithmetic on it lowers through the vector path and
                    # it never feeds grid/index arithmetic
                    pass
                else:
                    wide = ctx.emit(mir.MOp(
                        "smove", [reg],
                        [ctx.vreg(mir.I64, hint=binding.name + "w", loc=loc)],
                        loc=loc))
            grid_scalar_regs[binding.name] = wide
            # the TIR value at its declared type: the record-width load
            # when the types agree; a truncation of the wide form when the
            # record is wider (a 32-bit value never binds to an i64 reg --
            # the binop type rules would see a phantom mismatch)
            tir_reg = reg
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

        # view bindings: data base (flat, pointee-typed pointer semantics).
        # A kernel whose view count strains the GPR file re-materializes
        # each base at its uses instead of keeping every base live across
        # the whole program (the target's own register budget decides --
        # F023's 32 GPRs minus the ABI-reserved; the fixed entry/loop
        # infrastructure and the per-lane atomic loop state both count
        # against it, because the deep multi-view kernels' atomic loops
        # sit exactly there)
        view_regs: Dict[str, mir.VReg] = {}
        budget = self.target.gprs - len(self.target.reserved_gprs)
        has_atomic = any(
            isinstance(op, tir.Op) and op.op in ("atomic_rmw", "atomic_cas")
            for op in self._walk_ops(fn.body))
        loop_state = 13 if has_atomic else 5
        lazy_views = len(self.layout.views) + 10 + loop_state > budget
        self._lazy_view_index: Dict[int, int] = {}
        self._views_reg = views
        for binding in self.layout.views:
            if lazy_views:
                for p in fn.params:
                    if p.name == binding.name:
                        self._lazy_view_index[p.vid] = binding.view_index
                continue
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
        eligible = self.stage_plan is not None and self.stage_plan.eligible
        if not eligible:
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

        # the split gate: a two-phase eligible kernel takes the split path
        # at runtime when the call has more than one worker and the grid
        # holds at most one program (the single-program persistent
        # reduction; multi-program grids already distribute whole programs)
        split_entry = None
        if self.stage_plan is not None and self.stage_plan.eligible:
            # the split gate (the entry block's terminator): the split
            # path runs when the call has more than one worker and the
            # grid holds at most one program
            one = ctx.const(1, mir.I64, loc)
            two = ctx.const(2, mir.I64, loc)
            multi = ctx.emit(mir.MOp(
                "slt", [one, wcount64],
                [ctx.vreg(mir.I64, hint="wmul", loc=loc)], loc=loc))
            small = ctx.emit(mir.MOp(
                "slt", [program_count, two],
                [ctx.vreg(mir.I64, hint="gsm", loc=loc)], loc=loc))
            go_split = ctx.emit(mir.MOp(
                "sand", [multi, small],
                [ctx.vreg(mir.I64, hint="gsplit", loc=loc)], loc=loc))
            split_entry = ctx.add_block("split_entry", [], loc)
            pid_n0 = ctx.emit(mir.MOp(
                "smove", [self._worker_id_reg],
                [ctx.vreg(mir.I64, hint="pid0s", loc=loc)], loc=loc))
            items0 = ctx.const(0, mir.I64, loc)
            ctx.emit0(mir.MOp("brc", [go_split], [],
                              attrs={"true_target": split_entry.name,
                                     "true_args": [],
                                     "false_target": "prog_head",
                                     "false_args": [pid_n0, items0]},
                              loc=loc))

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
        self._emit_program_path(ctx, fn, pid_b, items_b, stats, view_regs,
                                wcount64, strided=None, tag="")

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

        # the split path: phase 1 (worker-strided region), partial stores,
        # the stage barrier, then the merge owner (worker 0) combines the
        # partials under the source's own semantics and runs the suffix
        if split_entry is not None:
            ctx.switch(split_entry)
            pid_s = ctx.emit(mir.MOp(
                "smove", [self._worker_id_reg],
                [ctx.vreg(mir.I64, hint="pid.split", loc=loc)], loc=loc))
            items_s = ctx.const(0, mir.I64, loc)
            self._emit_program_path(ctx, fn, pid_s, items_s, stats,
                                    view_regs, wcount64,
                                    strided=True, tag="s")

        # prog_exit(pid, items)
        pid_e = mir.VReg(mir.I64, name="pid.exit")
        items_e = mir.VReg(mir.I64, name="items.exit")
        exitb = ctx.add_block("prog_exit", [pid_e, items_e], loc)
        ctx.switch(exitb)
        ctx.emit0(mir.MOp("sstore", [stats, items_e], [],
                          attrs={"width": 64, "offset": 0}, loc=loc))
        ctx.emit0(mir.MOp("ret", [], [], loc=loc))

    def _emit_program_path(self, ctx: _Ctx, fn: tir.Function,
                           pid_b: mir.VReg, items_b: mir.VReg,
                           stats: mir.VReg,
                           view_regs: Dict[str, mir.VReg],
                           wcount64: mir.VReg, strided: Optional[bool],
                           tag: str) -> None:
        """One execution path of the kernel body: the normal per-program
        path (``strided=None``) or the split path's phase 1 (``strided``
        truthy: the chunk region runs worker-strided ranges)."""
        loc = fn.loc
        self._pid_b = pid_b
        self._path_items = items_b
        self._chunk_strided = bool(strided)
        self._wcount64 = wcount64
        self._wid64 = None
        self._ws_shared = None
        self._ws_private = None
        self._chunk = None
        self._count_reg = None
        self._stats_chunk_granular = False
        self.values = dict(self.values)
        self._overrides = []

        # program_id decomposition: the split path is program 0 for every
        # worker; the normal path decomposes the loop induction
        self._pid_axis_regs = {}
        if strided:
            self._pid_axis_regs[0] = ctx.const(0, mir.I32, loc)
        elif self.grid.ndim == 1:
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

        # the kernel body: (prefix, region, suffix)
        prefix, region, suffix = self._body_split or (
            list(fn.body.statements), [], [])
        names = _Names()
        for p in fn.params:
            names.define(p.name, p)
        self._names = names
        self._lower_statements(ctx, prefix, fn, view_regs)

        # the chunk region: opens at the region's first block statement;
        # the merge accumulators (the plan's partials + scan carries) ride
        # its back edge in both paths; the split path additionally strides
        # the ranges per worker
        self._chunk_merges = []
        if self.stage_plan is not None:
            # the partials drive the chunk-level merge (the accumulator
            # riding the chunk back edge) whether or not the two-phase
            # split is eligible: an escaping reduction always needs the
            # merged value in the suffix
            for p in self.stage_plan.partials:
                self._chunk_merges.append(self._merge_frame_of(p))
        for acc in self._scan_accs:
            self._chunk_merges.append({
                "kind": acc["kind"], "vid": acc["vid"], "pair_vid": None,
                "vtype": acc["vtype"], "index": False,
                "source": "scan", "acc": None,
            })
        # T012: the region lowers as segments (scalar groups, per-extent
        # passes, layout staging loops); a single-segment kernel keeps
        # exactly today's shape
        self._emit_segments(ctx, fn, view_regs, strided)

        # close the region: the back edge (with the merge combines), then
        # the exit block binds the merged values and reloads the live-out
        # scalars (chunk-invariant region values the suffix consumes --
        # the store's address arithmetic lowered inside the region)
        if self._chunk is not None:
            self._close_chunk_back_edge(ctx, fn, strided=strided)
            exit_name = self._chunk["exit"]
            ctx.switch(ctx.blocks[exit_name])
            self._bind_chunk_merges(ctx, loc)
            self._reload_liveouts(ctx, loc)
        else:
            exit_name = None

        if not strided:
            # the suffix runs once, after the region closed, on the merged
            # values; then the program loop steps (with the region's
            # accumulated items count -- not the path's entry value)
            self._lower_statements(ctx, suffix, fn, view_regs)
            items_out = self._chunk["exit_params_items"] \
                if self._chunk else items_b
            ctx.emit0(mir.MOp("br", [], [],
                              attrs={"target": "prog_next",
                                     "args": [pid_b, items_out]}, loc=loc))
            return

        # -- the split path's two-phase structure ------------------------------
        # phase 1 exit: store every partial to this worker's owned slot
        plan = self.stage_plan
        layout = plan.layout_for(8)
        ws = self._workspace_shared_reg(ctx, loc)
        stride = ctx.const(layout.stride, mir.I64, loc)
        wbase = ctx.emit(mir.MOp(
            "smul", [self._worker_id_reg64(ctx, loc), stride],
            [ctx.vreg(mir.I64, hint="wsoff", loc=loc)], loc=loc))
        wsbase = ctx.emit(mir.MOp(
            "sadd", [ws, wbase],
            [ctx.vreg(mir.I64, hint="wsb", loc=loc)], loc=loc))
        exit_params = list(self._chunk["exit_params"])
        pi = 0
        for i, frame in enumerate(self._chunk_merges):
            if frame["source"] != "plan":
                continue              # scan carries never leave the worker
            self._store_partial(ctx, frame, wsbase, layout.slots[i],
                                exit_params, pi, loc)
            pi += 2 if frame.get("index") else 1
        if not self.options.witness_drop_stage_barrier:
            ctx.emit0(mir.MOp("callbarrier", [ctx.function.params[0]], [],
                              loc=loc))
        # the merge owner: worker 0 combines the partials under the
        # source's own semantics; the suffix runs there exactly once
        # worker 0 owns the merge; every other worker is done (it still
        # reached the barrier the same number of times -- the stage
        # contract)
        not_owner = ctx.emit(mir.MOp(
            "sltu", [ctx.const(0, mir.I64, loc),
                     self._worker_id_reg64(ctx, loc)],
            [ctx.vreg(mir.I64, hint="notown", loc=loc)], loc=loc))
        merge_b = ctx.add_block("split_merge", [], loc)
        skip_b = ctx.add_block("split_skip", [], loc)
        ctx.emit0(mir.MOp("brc", [not_owner], [],
                          attrs={"true_target": skip_b.name,
                                 "true_args": [],
                                 "false_target": merge_b.name,
                                 "false_args": []}, loc=loc))
        ctx.switch(skip_b)
        items_now = self._chunk["exit_params_items"] if self._chunk \
            else items_b
        pid_now = self._pid_b
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "prog_exit",
                                 "args": [pid_now, items_now]}, loc=loc))
        ctx.switch(merge_b)
        self._emit_split_merge(ctx, fn, ws, stride, layout, view_regs,
                               suffix, loc)
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "prog_exit",
                                 "args": [pid_now, items_now]}, loc=loc))

    # -- the split path's merge step -------------------------------------------
    def _worker_id_reg64(self, ctx: _Ctx, loc) -> mir.VReg:
        if getattr(self, "_wid64", None) is None:
            self._wid64 = ctx.emit(mir.MOp(
                "smove", [self._worker_id_reg],
                [ctx.vreg(mir.I64, hint="wid64", loc=loc)], loc=loc))
        return self._wid64

    def _workspace_shared_reg(self, ctx: _Ctx, loc) -> mir.VReg:
        if getattr(self, "_ws_shared", None) is None:
            self._ws_shared = ctx.emit(mir.MOp(
                "sload", [ctx.function.params[0]],
                [ctx.vreg(mir.I64, hint="wssh", loc=loc)],
                attrs={"width": 64, "offset": 8, "ext": "sext"}, loc=loc))
        return self._ws_shared

    def _workspace_private_reg(self, ctx: _Ctx, loc) -> mir.VReg:
        if getattr(self, "_ws_private", None) is None:
            self._ws_private = ctx.emit(mir.MOp(
                "sload", [ctx.function.params[0]],
                [ctx.vreg(mir.I64, hint="wspr", loc=loc)],
                attrs={"width": 64, "offset": 16, "ext": "sext"}, loc=loc))
        return self._ws_private

    def _merge_frame_of(self, partial: "stages_mod.PartialSpec") -> dict:
        vtype = self._vtype(partial.dtype)
        index = partial.merge in (stages_mod.MERGE_MIN_INDEX,
                                  stages_mod.MERGE_MAX_INDEX)
        widen = 0
        if partial.dtype.is_int() and partial.dtype.bitwidth() > self._sew \
                and partial.merge == stages_mod.MERGE_SUM \
                and self._is_01_class_partial(partial.value_id):
            # the cmp-converted 0/1 class (``(x != 0).to(tl.int64)``): the
            # merge rides the data-SEW integer class -- exact, because the
            # class {0,1} is closed under the sum merge and the total
            # stays inside i32 -- and the merged value widens to the
            # declared type where the suffix consumes it (the widening is
            # value-exact for the class)
            vtype = mir.VectorType(self._sew, 1, "int")
            widen = partial.dtype.bitwidth()
        return {
            "kind": partial.merge, "vid": partial.value_id,
            "pair_vid": partial.pair_value_id, "vtype": vtype,
            "index": index, "source": "plan", "acc": None,
            "partial": partial, "widen_exit": widen,
        }

    def _is_01_class_partial(self, vid: int) -> bool:
        """Is the partial's producer a sum-reduce over a bool-converted
        block (the 0/1 value class)?  Structural, from the TIR alone."""
        fns = self.tir_module.functions
        if len(fns) != 1:
            return False
        for op in self._walk_ops(fns[0].body):
            if not isinstance(op, tir.Op) or not op.results:
                continue
            if op.results[0].vid != vid or op.op != "reduce":
                continue
            src = op.operands[0]
            prod = src.producer
            return prod is not None and prod.op == "convert" \
                and isinstance(prod.attrs.get("from"), tir.Type) \
                and prod.attrs["from"].is_bool()
        return False

    def _store_partial(self, ctx: _Ctx, frame: dict, wsbase: mir.VReg,
                       slot_off: int, exit_params, pi: int,
                       loc) -> None:
        """Store one partial (or its (value, index) pair) into this
        worker's owned workspace slot, from the region-exit parameters."""
        if frame.get("index"):
            value = self._scalarize(ctx, exit_params[pi], loc)
            idx = self._scalarize(ctx, exit_params[pi + 1], loc)
            ctx.emit0(mir.MOp(
                "sstore", [wsbase, value], [],
                attrs={"width": 32, "offset": slot_off}, loc=loc))
            ctx.emit0(mir.MOp(
                "sstore", [wsbase, idx], [],
                attrs={"width": 32, "offset": slot_off + 4}, loc=loc))
            return
        value = self._merge_source_reg(ctx, frame["vid"], frame, loc)
        ctx.emit0(mir.MOp(
            "sstore", [wsbase, value],
            [], attrs={"width": 32, "offset": slot_off}, loc=loc))

    def _emit_split_merge(self, ctx: _Ctx, fn: tir.Function, ws: mir.VReg,
                          stride: mir.VReg, layout, view_regs,
                          suffix, loc) -> None:
        """The merge step (worker 0): fold every worker's partial into the
        identity-seeded accumulator under the source's own merge rule,
        then bind the merged values and run the suffix exactly once."""
        plan = self.stage_plan
        frames = [f for f in self._chunk_merges if f["source"] == "plan"]
        # the identity seeds
        inits: List[mir.VReg] = []
        for f in frames:
            if f["index"]:
                ident_val = stages_mod.identity_for(
                    "min" if f["kind"] == stages_mod.MERGE_MIN_INDEX
                    else "max", f["partial"].dtype)
                ident_idx = stages_mod._index_identity(tir.INT32)
                inits.append(self._splat_const(ctx, ident_val, f["vtype"], loc))
                inits.append(self._splat_const(ctx, ident_idx,
                                               mir.VectorType(32, 1, "int"),
                                               loc))
            else:
                ident = stages_mod.identity_for(
                    self._merge_op_kind(f["kind"]), f["partial"].dtype)
                inits.append(self._splat_const(ctx, ident, f["vtype"], loc))
        # the loop over workers w' = 0 .. worker_count-1
        zero = ctx.const(0, mir.I64, loc)
        wcnt64 = ctx.emit(mir.MOp(
            "smove", [self._worker_count_reg],
            [ctx.vreg(mir.I64, hint="wcntm", loc=loc)], loc=loc))
        frame = scalar_mod.begin_counted_loop(
            ctx, zero, wcnt64, inits, loc, "merge")
        params = frame.params[1:]
        # per worker: load the partials and combine
        body = ctx.blocks[frame.body.name]
        ctx.switch(body)
        w_off = ctx.emit(mir.MOp(
            "smul", [frame.params[0], stride],
            [ctx.vreg(mir.I64, hint="mwoff", loc=loc)], loc=loc))
        w_base = ctx.emit(mir.MOp(
            "sadd", [ws, w_off],
            [ctx.vreg(mir.I64, hint="mwb", loc=loc)], loc=loc))
        # re-establish the data region for the vector combine ops
        avl = ctx.const(self._vl, mir.I32, loc)
        ctx.emit(mir.MOp("vsetvli", [avl],
                         [ctx.vreg(mir.I32, hint="mvl", loc=loc)],
                         attrs={"sew": self._sew, "lmul": 1,
                                "policy": "ta,ma"}, loc=loc))
        # the induction step (the back edge's first value)
        i_next = ctx.emit(mir.MOp(
            "sadd", [frame.params[0], ctx.const(1, mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="mi", loc=loc)], loc=loc))
        back = [i_next]
        pi = 0
        for f in frames:
            slot = layout.slots[self._chunk_merges.index(f)]
            if f["index"]:
                acc_v, acc_i = params[pi], params[pi + 1]
                pi += 2
                cand_v = self._load_partial(ctx, w_base, slot,
                                            f["vtype"], loc)
                cand_i = self._load_partial(ctx, w_base, slot + 4,
                                            mir.VectorType(32, 1, "int"),
                                            loc)
                nv, ni = self._combine_pair(ctx, acc_v, acc_i, cand_v,
                                            cand_i, f["kind"], loc)
                back.extend((nv, ni))
            else:
                acc = params[pi]
                pi += 1
                cand = self._load_partial(ctx, w_base, slot, f["vtype"],
                                          loc)
                back.append(self._combine_value(ctx, acc, cand, f["kind"],
                                                loc))
        scalar_mod.close_loop(ctx, frame, back)
        ctx.switch(frame.exit)
        # bind the merged values to the partials' vids (a bare arg form's
        # value side is internal: only the index binds)
        pi = 0
        for f in frames:
            if f["index"]:
                merged_v = frame.exit.params[pi + 1]
                merged_i = frame.exit.params[pi + 2]
                pi += 2
                if f["pair_vid"] is not None:
                    self.values[f["vid"]] = self._scalarize(ctx, merged_v,
                                                           loc)
                    self.values[f["pair_vid"]] = self._scalarize(
                        ctx, merged_i, loc)
                else:
                    self.values[f["vid"]] = self._scalarize(ctx, merged_i,
                                                           loc)
            else:
                merged = frame.exit.params[pi + 1]
                pi += 1
                self.values[f["vid"]] = self._widen_exit(
                    ctx, self._scalarize(ctx, merged, loc), f, loc)
        # the names environment must see the merged bindings
        for f in frames:
            for vid in (f["vid"], f["pair_vid"]):
                if vid is None:
                    continue
                for name, v in self._names.stack[-1].items():
                    if v.vid == vid:
                        self._names.define(name, v)
        self._lower_statements(ctx, suffix, fn, view_regs)

    def _load_partial(self, ctx: _Ctx, base: mir.VReg, off: int,
                      vtype: mir.VectorType, loc) -> mir.VReg:
        raw = ctx.emit(mir.MOp(
            "sload", [base],
            [ctx.vreg(mir.ScalarType(vtype.sew, signed=True,
                                     float=vtype.kind == "float"),
                      hint="pl", loc=loc)],
            attrs={"width": vtype.sew, "offset": off, "ext": "sext"},
            loc=loc))
        return ctx.emit(mir.MOp(
            "s2v", [raw], [ctx.vreg(vtype, hint="pls", loc=loc)], loc=loc))

    def _bool_scalar(self, ctx: _Ctx, reg: mir.VReg, loc) -> mir.VReg:
        """A branch-condition scalar: mask-typed bools (the floating
        compare results) count their set lanes; i64 bools pass through."""
        if reg.is_mask():
            cnt = ctx.emit(mir.MOp(
                "vpopc", [reg], [ctx.vreg(mir.I64, hint="bc", loc=loc)],
                loc=loc))
            return ctx.emit(mir.MOp(
                "sltu", [ctx.const(0, mir.I64, loc), cnt],
                [ctx.vreg(mir.I64, hint="bs", loc=loc)], loc=loc))
        return reg

    def _scalarize(self, ctx: _Ctx, reg: mir.VReg, loc) -> mir.VReg:
        """The scalar form of a value: lane-0 vectors extract to a GPR
        (raw bits for floats); scalars pass through."""
        if reg.is_vector():
            sty = mir.ScalarType(reg.type.sew, signed=reg.type.kind != "uint",
                                 float=reg.type.kind == "float")
            return ctx.emit(mir.MOp(
                "vextract", [reg],
                [ctx.vreg(sty, hint="x0", loc=loc)], loc=loc))
        return reg

    def _merge_op_kind(self, merge: str) -> str:
        return {"sum": "sum", "product": "cumprod", "min": "min",
                "max": "max", "xor": "xor_sum", "or": "reduce_or",
                "pass": "sum"}[merge]

    def _splat_const(self, ctx: _Ctx, value, vtype: mir.VectorType,
                     loc) -> mir.VReg:
        sty = mir.ScalarType(vtype.sew, signed=vtype.kind != "uint",
                             float=vtype.kind == "float")
        if sty.float:
            import struct as _struct
            bits = _struct.unpack("<I", _struct.pack("<f", float(value)))[0] \
                if vtype.sew == 32 else int(value)
            kreg = ctx.const(bits, sty, loc)
        else:
            mask = (1 << vtype.sew) - 1
            kreg = ctx.const(int(value) & mask, sty, loc)
        return ctx.emit(mir.MOp(
            "s2v", [kreg], [ctx.vreg(vtype, hint="ids", loc=loc)], loc=loc))

    def _combine_value(self, ctx: _Ctx, acc: mir.VReg, cand: mir.VReg,
                       kind: str, loc) -> mir.VReg:
        """One value-merge step under the source's own semantics (lane 0
        of the accumulators is the live value; garbage lanes never feed a
        reduction here)."""
        if kind == stages_mod.MERGE_SUM:
            return ctx.emit(mir.MOp(
                "vbin", [acc, cand], [ctx.vreg(acc.type, hint="mg", loc=loc)],
                attrs={"op": "add"}, loc=loc))
        if kind == stages_mod.MERGE_PRODUCT:
            return ctx.emit(mir.MOp(
                "vbin", [acc, cand], [ctx.vreg(acc.type, hint="mg", loc=loc)],
                attrs={"op": "mul"}, loc=loc))
        if kind == stages_mod.MERGE_XOR:
            return ctx.emit(mir.MOp(
                "vbin", [acc, cand], [ctx.vreg(acc.type, hint="mg", loc=loc)],
                attrs={"op": "xor"}, loc=loc))
        if kind == stages_mod.MERGE_OR:
            return ctx.emit(mir.MOp(
                "vbin", [acc, cand], [ctx.vreg(acc.type, hint="mg", loc=loc)],
                attrs={"op": "or"}, loc=loc))
        if kind in (stages_mod.MERGE_MIN, stages_mod.MERGE_MAX):
            # min: the candidate wins when cand < acc; max: when acc <
            # cand (the floating forms have no gt -- a declared absence:
            # the swapped lt is the same predicate)
            lhs, rhs = ((cand, acc) if kind == stages_mod.MERGE_MIN
                        else (acc, cand))
            take = ctx.emit(mir.MOp(
                "vcmp", [lhs, rhs],
                [ctx.vreg(mir.MaskType(), hint="mt", loc=loc)],
                attrs={"pred": "lt", "fp": acc.type.kind == "float"},
                loc=loc))
            v0 = ctx.emit(mir.MOp(
                "vmovmask", [take],
                [ctx.vreg(mir.MaskType(), hint="mv0", loc=loc,
                          fixed_phys="v0")], loc=loc))
            return ctx.emit(mir.MOp(
                "vsel", [v0, cand, acc],
                [ctx.vreg(acc.type, hint="ms", loc=loc)], loc=loc))
        if kind == stages_mod.MERGE_PASS:
            return cand
        raise self._err(loc, "merge", f"unknown merge kind {kind!r}")

    def _combine_pair(self, ctx: _Ctx, acc_v: mir.VReg, acc_i: mir.VReg,
                      cand_v: mir.VReg, cand_i: mir.VReg, kind: str,
                      loc) -> Tuple[mir.VReg, mir.VReg]:
        """One (value, index) pair merge: the smaller/larger value wins;
        on a tie the declared tie-break (left: the smaller index) decides.
        Two select steps -- the second only fixes ties -- so no mask OR is
        needed (vmand composes the tie condition)."""
        # min-index: the candidate wins when cand < acc; max-index: when
        # acc < cand (no floating gt: the swapped lt is the predicate)
        lhs, rhs = ((cand_v, acc_v)
                    if kind == stages_mod.MERGE_MIN_INDEX else (acc_v,
                                                                cand_v))
        take = ctx.emit(mir.MOp(
            "vcmp", [lhs, rhs],
            [ctx.vreg(mir.MaskType(), hint="pt", loc=loc)],
            attrs={"pred": "lt", "fp": acc_v.type.kind == "float"},
            loc=loc))
        v0a = ctx.emit(mir.MOp(
            "vmovmask", [take],
            [ctx.vreg(mir.MaskType(), hint="pv0", loc=loc,
                      fixed_phys="v0")], loc=loc))
        v1 = ctx.emit(mir.MOp(
            "vsel", [v0a, cand_v, acc_v],
            [ctx.vreg(acc_v.type, hint="pv", loc=loc)], loc=loc))
        i1 = ctx.emit(mir.MOp(
            "vsel", [v0a, cand_i, acc_i],
            [ctx.vreg(acc_i.type, hint="pi", loc=loc)], loc=loc))
        eq = ctx.emit(mir.MOp(
            "vcmp", [cand_v, acc_v],
            [ctx.vreg(mir.MaskType(), hint="pe", loc=loc)],
            attrs={"pred": "eq", "fp": acc_v.type.kind == "float"},
            loc=loc))
        less = ctx.emit(mir.MOp(
            "vcmp", [cand_i, acc_i],
            [ctx.vreg(mir.MaskType(), hint="pl", loc=loc)],
            attrs={"pred": "lt", "fp": False}, loc=loc))
        tie = ctx.emit(mir.MOp(
            "vmand", [eq, less],
            [ctx.vreg(mir.MaskType(), hint="ptie", loc=loc)], loc=loc))
        v0b = ctx.emit(mir.MOp(
            "vmovmask", [tie],
            [ctx.vreg(mir.MaskType(), hint="pv0b", loc=loc,
                      fixed_phys="v0")], loc=loc))
        v2 = ctx.emit(mir.MOp(
            "vsel", [v0b, cand_v, v1],
            [ctx.vreg(acc_v.type, hint="pv2", loc=loc)], loc=loc))
        i2 = ctx.emit(mir.MOp(
            "vsel", [v0b, cand_i, i1],
            [ctx.vreg(acc_i.type, hint="pi2", loc=loc)], loc=loc))
        return v2, i2

    def _merge_source_reg(self, ctx: _Ctx, vid: int, frame: dict,
                          loc) -> mir.VReg:
        """The value to store/combine for one partial: its current
        binding, extracted to a scalar (raw bits for floats)."""
        reg = self.values.get(vid)
        if reg is None:
            raise self._err(loc, "merge",
                            "a partial has no lowered value at the region "
                            "exit (the plan and the lowering disagree)")
        return self._scalarize(ctx, reg, loc)

    def _bind_chunk_merges(self, ctx: _Ctx, loc) -> None:
        """Bind the chunk-region exit parameters to the partials' vids:
        post-region uses see the merged (all-chunk) values, scalarized to
        GPRs (raw bits for floats); on the split path they are this
        worker's partials and the merge step rebinds the combined
        values.  An index pair's value side may be internal (a bare
        argmax/argmin: no TIR value escapes) -- it binds nothing but its
        exit parameter still feeds the merge."""
        exit_params = list(self._chunk["exit_params"])
        pi = 0
        for frame in self._chunk_merges:
            if frame["source"] == "plan" and frame.get("index"):
                if frame["pair_vid"] is not None:
                    self.values[frame["vid"]] = self._scalarize(
                        ctx, exit_params[pi], loc)
                    self.values[frame["pair_vid"]] = self._scalarize(
                        ctx, exit_params[pi + 1], loc)
                else:
                    self.values[frame["vid"]] = self._scalarize(
                        ctx, exit_params[pi + 1], loc)
                pi += 2
            else:
                merged = self._scalarize(ctx, exit_params[pi], loc)
                self.values[frame["vid"]] = self._widen_exit(
                    ctx, merged, frame, loc)
                pi += 1

    def _widen_exit(self, ctx: _Ctx, reg: mir.VReg, frame: dict,
                    loc) -> mir.VReg:
        """Widen a merged 0/1-class partial to its declared type at the
        consumer boundary (value-exact for the class)."""
        width = frame.get("widen_exit") or 0
        if width and reg.type.width < width and not reg.type.float:
            return scalar_mod.widen_to(ctx, reg, width, loc)
        return reg

    def _store_liveouts(self, ctx: _Ctx, loc) -> None:
        """At the chunk back edge: spill the live-out scalars to the
        worker-private workspace (their value is chunk-invariant, so any
        iteration's value is the value)."""
        if not self._liveouts:
            return
        ws = self._workspace_private_reg(ctx, loc)
        for vid, slot in self._liveouts:
            reg = self.values.get(vid)
            if reg is None:
                continue          # the region never defined it (dead)
            if reg.is_vector() or reg.is_mask():
                raise self._err(
                    loc, "region",
                    "a live-out region value is a block value (the suffix "
                    "cannot consume it through the scalar live-out path)")
            width = reg.type.width if reg.type.width in (8, 16, 32, 64) \
                else 64
            if -2048 <= slot < 2048:
                base = ws
            else:
                # the 12-bit immediate cannot reach: materialize the
                # address (the layout staging regions push the slots far
                # into the workspace)
                base = ctx.emit(mir.MOp(
                    "sadd", [ws, ctx.const(slot, mir.I64, loc)],
                    [ctx.vreg(mir.I64, hint="lsb", loc=loc)], loc=loc))
                slot = 0
            ctx.emit0(mir.MOp("sstore", [base, reg], [],
                              attrs={"width": width, "offset": slot},
                              loc=loc))

    def _reload_liveouts(self, ctx: _Ctx, loc) -> None:
        """At the chunk exit: reload the live-out scalars and rebind their
        vids (the suffix's uses now read the reloaded registers).  The
        workspace base re-loads here: the cached register was defined
        inside the chunk body and does not dominate the exit."""
        if not self._liveouts:
            return
        launch = ctx.function.params[0]
        ws = ctx.emit(mir.MOp(
            "sload", [launch], [ctx.vreg(mir.I64, hint="wsr", loc=loc)],
            attrs={"width": 64, "offset": 16, "ext": "sext"}, loc=loc))
        for vid, slot in self._liveouts:
            reg = self.values.get(vid)
            if reg is None:
                continue
            width = reg.type.width if reg.type.width in (8, 16, 32, 64) \
                else 64
            if -2048 <= slot < 2048:
                base = ws
            else:
                # the 12-bit immediate cannot reach: materialize the
                # address (the layout staging regions push the slots far
                # into the workspace)
                base = ctx.emit(mir.MOp(
                    "sadd", [ws, ctx.const(slot, mir.I64, loc)],
                    [ctx.vreg(mir.I64, hint="lob", loc=loc)], loc=loc))
                slot = 0
            reloaded = ctx.emit(mir.MOp(
                "sload", [base],
                [ctx.vreg(mir.ScalarType(width, signed=reg.type.signed,
                                         float=reg.type.float),
                          hint="lo", loc=loc)],
                attrs={"width": width, "offset": slot, "ext": "sext"},
                loc=loc))
            self.values[vid] = reloaded

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
    def _ensure_chunk(self, ctx: _Ctx, fn: tir.Function,
                      strided: Optional[bool] = None) -> None:
        """Open the chunk loop over the block extent (block-local index
        space [0, B) in vl-sized pieces).  Opens once, at the first
        block-level statement; everything after lowers inside it.

        The reduction merge accumulators ride the loop as extra carried
        parameters (initialized to the per-op-and-dtype identity, combined
        at the back edge under the source's own merge rule); the split
        path strides the ranges per worker (worker w takes chunks w, w+W,
        w+2W, ... below the runtime extent -- the same strided ownership
        the program partition uses)."""
        if self._chunk is not None:
            return
        if strided is None:
            strided = bool(self._chunk_strided)
        loc = fn.loc
        B = self.plan.block_extent
        vl = self._vl
        items_reg = self._items_in_scope(ctx)
        if strided:
            wid64 = self._worker_id_reg64(ctx, loc)
            wvl = ctx.emit(mir.MOp(
                "smul", [self._wcount64, ctx.const(vl, mir.I64, loc)],
                [ctx.vreg(mir.I64, hint="swvl", loc=loc)], loc=loc))
            elem0_64 = ctx.emit(mir.MOp(
                "smul", [wid64, ctx.const(vl, mir.I64, loc)],
                [ctx.vreg(mir.I64, hint="se0", loc=loc)], loc=loc))
            elem0 = ctx.emit(mir.MOp(
                "strunc", [elem0_64],
                [ctx.vreg(mir.I32, hint="se0t", loc=loc)], loc=loc))
            self._chunk_step = wvl
        else:
            elem0 = ctx.const(0, mir.I32, loc)
            self._chunk_step = None

        # the merge accumulator inits (identity splats; pairs carry the
        # value identity and the worst index)
        merge_inits: List[mir.VReg] = []
        for frame in self._chunk_merges:
            if frame["source"] == "scan":
                ident = stages_mod.identity_for(
                    "cumsum" if frame["kind"] == "cumsum" else "cumprod",
                    self._tir_type_of(frame["vtype"]))
                merge_inits.append(self._scan_init_reg(ctx, frame, ident,
                                                       loc))
            elif frame["index"]:
                p = frame["partial"]
                ident_val = stages_mod.identity_for(
                    "min" if p.merge == stages_mod.MERGE_MIN_INDEX else "max",
                    p.dtype)
                ident_idx = stages_mod._index_identity(tir.INT32)
                merge_inits.append(self._splat_const(ctx, ident_val,
                                                     frame["vtype"], loc))
                merge_inits.append(self._splat_const(
                    ctx, ident_idx, mir.VectorType(32, 1, "int"), loc))
            else:
                p = frame["partial"]
                ident = stages_mod.identity_for(self._merge_op_kind(p.merge),
                                                p.dtype)
                merge_inits.append(self._splat_const(ctx, ident,
                                                     frame["vtype"], loc))

        # unique per pass: the multi-pass lane opens one chunk loop per
        # extent-homogeneous pass (the name collision would merge the CFG)
        tag = self._tag("schunk" if strided else "chunk")
        head = ctx.add_block(f"{tag}_head", [], loc)
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": head.name,
                                 "args": [elem0, items_reg] + merge_inits},
                          loc=loc))
        elem_h = mir.VReg(mir.I32, name="elem.loop")
        items_c = mir.VReg(mir.I64, name="items.chunk")
        head.params += [elem_h, items_c]
        acc_params: List[mir.VReg] = []
        for i, init in enumerate(merge_inits):
            p = mir.VReg(init.type, name=f"mrg{i}", loc=loc)
            head.params.append(p)
            acc_params.append(p)
        ctx.switch(head)
        # (the head's own brc is emitted below, after the exit block)
        extent = ctx.const(B, mir.I32, loc)
        ccont = ctx.emit(mir.MOp(
            "slt", [elem_h, extent],
            [ctx.vreg(mir.I64, hint="cgo", loc=loc)], loc=loc))
        # the exit: pid (for the program step), the items count and every
        # merge accumulator at its all-chunk value
        exit_params = [mir.VReg(mir.I64, name="pid.xreg", loc=loc),
                       mir.VReg(mir.I64, name="items.xreg", loc=loc)]
        exit_params += [mir.VReg(p.type, name=f"mrgx{i}", loc=loc)
                        for i, p in enumerate(acc_params)]
        exitb = ctx.add_block(f"{tag}_exit", list(exit_params), loc)

        # the body SHARES the head's param VRegs (the counted-loop
        # pattern): the head->body edge passes every value to itself, so
        # no parallel moves -- and no move cycles -- exist on it
        cbody = ctx.add_block(f"{tag}_body", [elem_h, items_c] +
                              list(acc_params), loc)
        ctx.switch(cbody)
        elem_b = elem_h

        avl = ctx.const(vl, mir.I32, loc)
        ctx.emit(mir.MOp(
            "vsetvli", [avl], [ctx.vreg(mir.I32, hint="vl", loc=loc)],
            attrs={"sew": self._sew, "lmul": 1, "policy": "ta,ma"}, loc=loc))

        self._chunk = {"head": head, "body": cbody, "elem": elem_b,
                       "items": items_c, "vl": vl, "extent": B,
                       "exit": exitb.name,
                       "exit_params": exit_params[2:],
                       "exit_params_items": exit_params[1],
                       "accs": acc_params, "strided": strided}
        # frame -> its accumulator params (shared head/body: the value
        # entering this chunk iteration)
        pi = 0
        for frame in self._chunk_merges:
            if frame["source"] == "plan" and frame.get("index"):
                frame["acc_v"] = acc_params[pi]
                frame["acc_i"] = acc_params[pi + 1]
                pi += 2
            else:
                frame["acc"] = acc_params[pi]
                pi += 1

        # the head's test (emitted from the head's position)
        saved = ctx.cur
        ctx.switch(head)
        ctx.emit0(mir.MOp(
            "brc", [ccont], [],
            attrs={"true_target": cbody.name,
                   "true_args": [elem_h, items_c] + acc_params,
                   "false_target": exitb.name,
                   "false_args": [self._pid_b, items_c] + acc_params},
            loc=loc))
        ctx.switch(saved)

    def _items_in_scope(self, ctx: _Ctx) -> mir.VReg:
        """The items counter at the current position: the path's entry
        items parameter (the scalar prefix does not modify it)."""
        return self._path_items

    # -- T012: segment emission (the multi-pass layout lane) --------------------

    def _pass_defined_vids(self, stmts) -> set:
        out: set = set()

        def walk(st):
            if isinstance(st, tir.Op):
                out.update(r.vid for r in st.results)
            elif isinstance(st, tir.If):
                for s in list(st.then.statements) + \
                        list(st.els.statements):
                    walk(s)
                out.update(v.vid for v in st.join_results)
            elif isinstance(st, tir.Loop):
                for s in st.body.statements:
                    walk(s)
                out.update(v.vid for v in st.join_results)

        for st in stmts:
            walk(st)
        return out

    def _emit_segments(self, ctx: _Ctx, fn: tir.Function,
                       view_regs: Dict[str, mir.VReg],
                       strided: Optional[bool]) -> None:
        """Emit the region's segments in order.  Every pass except the
        last closes its own chunk loop (chaining pid/items into the next
        pass); the LAST pass stays open for the caller's close (the
        existing single-pass shape)."""
        loc = fn.loc
        all_merges = list(self._chunk_merges)
        pass_index = 0
        n_passes = sum(1 for seg in self._segments if seg[0] == "pass")
        seen_pass = 0
        saved_liveouts = self._liveouts
        for si, seg in enumerate(self._segments):
            if seg[0] == "scalar":
                self._lower_statements(ctx, seg[1], fn, view_regs)
                continue
            if seg[0] == "layout":
                if self._chunk is not None:
                    self._close_pass(ctx, fn, strided)
                self._lower_layout_segment(ctx, fn, seg[1])
                continue
            # a pass: configure its parameters and merges
            params = self._pass_params[si]
            if params is None:      # pragma: no cover - segmentation shape
                raise self._err(None, "layout", "pass without parameters")
            defined = self._pass_defined_vids(seg[1])
            self._chunk_merges = [f for f in all_merges
                                  if f["vid"] in defined]
            if not self._chunk_merges and seen_pass == 0 and n_passes == 1:
                self._chunk_merges = all_merges   # the single-pass form
            seen_pass += 1
            self._sew = params["sew"]
            self._vl = params["vl"]
            # this pass's cross-pass scalar liveouts (store at the back
            # edge, reload at the exit -- registers do not survive loops)
            self._liveouts = list(self._pass_liveouts.get(si, []))
            if seen_pass == n_passes:
                self._liveouts.extend(saved_liveouts)
            self._open_pass(ctx, fn, params)
            self._lower_statements(ctx, seg[1], fn, view_regs)
            if seen_pass < n_passes:
                self._close_pass(ctx, fn, strided)
        self._liveouts = saved_liveouts
        # no pass at all (scalar-only region): nothing stays open
        if self._chunk is not None and seen_pass < n_passes:
            self._close_pass(ctx, fn, strided)

    def _open_pass(self, ctx: _Ctx, fn: tir.Function, params: dict) -> None:
        """Open one pass's chunk loop at the pass's own extent/SEW (the
        existing _ensure_chunk, parameterized)."""
        saved_extent = self.plan.block_extent
        saved_chunks = self.plan.chunks
        self.plan.block_extent = params["extent"]
        self.plan.chunks = params["chunks"]
        try:
            self._ensure_chunk(ctx, fn)
        finally:
            # plan.chunks/block_extent stay at the pass's values for the
            # in-pass queries (gather's chunk count); the describe-level
            # values were recorded in lower()
            self.plan.block_extent = params["extent"]
            self.plan.chunks = params["chunks"]
            _ = saved_extent, saved_chunks

    def _close_pass(self, ctx: _Ctx, fn: tir.Function,
                    strided: Optional[bool]) -> None:
        """Close the current pass's chunk loop and chain its exit values
        into the next segment (pid/items/merges rebind; staged values'
        registers drop)."""
        loc = fn.loc
        self._close_chunk_back_edge(ctx, fn, strided=strided)
        exit_name = self._chunk["exit"]
        ctx.switch(ctx.blocks[exit_name])
        self._bind_chunk_merges(ctx, loc)
        self._reload_liveouts(ctx, loc)
        # the next pass's entry items: this pass's accumulated count
        self._path_items = self._chunk["exit_params_items"]
        # staged values' registers do not survive the pass loop; constants
        # re-emit at their next use; the workspace base registers were
        # defined inside the closed loop and no longer dominate -- the
        # next pass/staging loop reloads them
        for vid in self._staged:
            self.values.pop(vid, None)
        for vid in list(self._pass_bound):
            v = self._value_by_vid(vid)
            if v.producer is not None and v.producer.op == "const":
                self.values.pop(vid, None)
        self._ws_private = None
        self._ws_shared = None
        self._wid64 = None
        self._chunk = None
        self._count_reg = None
        self._pass_bound = set()

    def _lower_layout_segment(self, ctx: _Ctx, fn: tir.Function,
                              op: tir.Op) -> None:
        """Lower one top-level layout op through its staging loop(s): the
        sources are already staged (their passes stored the bytes); the
        results become staged values."""
        loc = op.loc or fn.loc
        code = op.op
        if code == "permute":
            self._stage_permute(ctx, fn, op)
        elif code == "flip":
            self._stage_flip(ctx, fn, op)
        elif code == "join":
            self._stage_join(ctx, fn, op)
        elif code == "interleave":
            self._stage_join(ctx, fn, op)
        elif code == "split":
            self._stage_split(ctx, fn, op)
        elif code == "broadcast":
            self._stage_broadcast(ctx, fn, op)
        else:  # pragma: no cover - segmentation shape
            raise self._err(loc, code, "unknown layout op in a segment")
        self._layout_stagings.append({
            "op": code, "loc": str(loc),
            "results": [r.name for r in op.results],
        })

    # -- the staging loop -------------------------------------------------------

    def _ws_scaled(self, ctx: _Ctx, idx: mir.VReg, esz: int, loc,
                   vl: int) -> mir.VReg:
        """The EEW=64 byte-offset vector of ``idx`` (element counts) times
        ``esz``, at the lane count ``vl``.  The widening form follows the
        double-LMUL convention (the vwiden's destination group); an i64
        index keeps its own LMUL."""
        if idx.type.sew == 32:
            lmul = idx.type.lmul * 2
            avl0 = ctx.const(vl, mir.I32, loc)
            ctx.emit(mir.MOp(
                "vsetvli", [avl0],
                [ctx.vreg(mir.I32, hint="lsw0", loc=loc)],
                attrs={"sew": idx.type.sew, "lmul": idx.type.lmul,
                       "policy": "ta,ma"}, loc=loc))
            wide = ctx.emit(mir.MOp(
                "vwiden", [idx],
                [ctx.vreg(mir.VectorType(64, lmul, "int"), hint="lsw",
                          loc=loc)],
                attrs={"mode": "sext"}, loc=loc))
        elif idx.type.sew == 64:
            lmul = idx.type.lmul
            wide = idx
        else:
            raise self._err(loc, "layout",
                            f"a {idx.type.sew}-bit staging index is not in "
                            "the lane (32/64-bit index arithmetic only)")
        if lmul not in (1, 2, 4, 8):
            raise self._err(loc, "layout",
                            f"the index class needs LMUL {lmul} "
                            "(outside 1..8; a located refusal)")
        avl = ctx.const(vl, mir.I32, loc)
        ctx.emit(mir.MOp(
            "vsetvli", [avl], [ctx.vreg(mir.I32, hint="lswr", loc=loc)],
            attrs={"sew": 64, "lmul": lmul, "policy": "ta,ma"}, loc=loc))
        esz_reg = ctx.const(esz, mir.I64, loc)
        scaled = ctx.emit(mir.MOp(
            "vbinx", [wide, esz_reg],
            [ctx.vreg(mir.VectorType(64, lmul, "int"), hint="lss",
                      loc=loc)],
            attrs={"op": "mul"}, loc=loc))
        return scaled, lmul

    def _staging_region(self, ctx: _Ctx, sew: int, vl: int, loc) -> None:
        avl = ctx.const(vl, mir.I32, loc)
        ctx.emit(mir.MOp(
            "vsetvli", [avl], [ctx.vreg(mir.I32, hint="lsr", loc=loc)],
            attrs={"sew": sew, "lmul": 1, "policy": "ta,ma"}, loc=loc))

    def _vregion(self, ctx: _Ctx, vtype: mir.VectorType, loc,
                 vl: Optional[int] = None) -> None:
        """An explicit vsetvli for one vector type (the conversion matrix's
        region discipline: every emitted convert runs in its own region;
        the pass region is restored afterwards).  ``vl`` defaults to the
        pass's lane count; the staging loops pass their own."""
        avl = ctx.const(vl if vl is not None else self._vl, mir.I32, loc)
        ctx.emit(mir.MOp(
            "vsetvli", [avl], [ctx.vreg(mir.I32, hint="cvr", loc=loc)],
            attrs={"sew": vtype.sew, "lmul": vtype.lmul,
                   "policy": "ta,ma"}, loc=loc))

    def _vmovv(self, ctx: _Ctx, reg: mir.VReg, vtype: mir.VectorType,
               loc, vl: Optional[int] = None) -> mir.VReg:
        """The bit-level register-view move: copies the used lanes (the
        avl caps the copy), typed as ``vtype`` (the view may retype the
        elements or narrow the group).  The region is the side whose
        SEW*LMUL covers the copied bytes: the WIDER-element side (a
        (32,·)->(8,·) retype must copy whole 32-bit lanes -- an e8-region
        copy would drop three quarters of the bytes); at equal SEW the
        narrower LMUL (vmv.v.v forms its groups from the active LMUL,
        and an overlapping vd/vs pair is illegal on this target --
        probed: the m2-region copy with vd inside vs's group raises
        SIGILL)."""
        if reg.type.sew != vtype.sew:
            region_ty = reg.type if reg.type.sew > vtype.sew else vtype
        else:
            region_ty = vtype if vtype.lmul <= reg.type.lmul else reg.type
        self._vregion(ctx, region_ty, loc, vl=vl)
        return ctx.emit(mir.MOp(
            "vmovv", [reg], [ctx.vreg(vtype, hint="cvm", loc=loc)],
            loc=loc))

    def _idx_vtype(self, vl: int) -> mir.VectorType:
        """The i32 index-vector type covering ``vl`` lanes (the staging and
        staged-load index arithmetic; LMUL follows the lane count)."""
        lmul = max(1, vl * 32 // self.target.vlen_bits)
        if lmul not in (1, 2, 4, 8):
            raise self._err(None, "index",
                            f"the i32 index class needs LMUL {lmul} at vl "
                            f"{vl} (outside 1..8)")
        return mir.VectorType(32, lmul, "int")

    def _lane_index(self, ctx: _Ctx, elem: mir.VReg, vl: int, loc) -> mir.VReg:
        """``vid + elem`` at the i32 index class with avl=vl: the flat
        element index of each lane of the current staging iteration."""
        ity = self._idx_vtype(vl)
        self._vregion(ctx, ity, loc, vl=vl)
        vid = ctx.emit(mir.MOp(
            "vid", [], [ctx.vreg(ity, hint="lvid", loc=loc)], loc=loc))
        return ctx.emit(mir.MOp(
            "vbinx", [vid, elem],
            [ctx.vreg(ity, hint="lidx", loc=loc)],
            attrs={"op": "add"}, loc=loc))

    def _staging_const(self, ctx: _Ctx, value: int, vl: int, loc) -> mir.VReg:
        ity = self._idx_vtype(vl)
        self._vregion(ctx, ity, loc, vl=vl)
        sty = mir.ScalarType(32, signed=True)
        kreg = ctx.const(value, sty, loc)
        return ctx.emit(mir.MOp(
            "s2v", [kreg], [ctx.vreg(ity, hint="lsc", loc=loc)], loc=loc))

    def _staging_vbin(self, ctx: _Ctx, op: str, a: mir.VReg, b: mir.VReg,
                      vl: int, loc) -> mir.VReg:
        ity = self._idx_vtype(vl)
        self._vregion(ctx, ity, loc, vl=vl)
        return ctx.emit(mir.MOp(
            "vbin", [a, b],
            [ctx.vreg(ity, hint="lsb", loc=loc)],
            attrs={"op": op}, loc=loc))

    def _emit_staging_loop(self, ctx: _Ctx, fn: tir.Function, result: tir.Value,
                           sources: List[Tuple[dict, object]],
                           selector=None) -> None:
        """One staging loop: for every result flat position k (chunks of
        vl_r at the result's SEW), load ``sources[i][0]`` (a staged region
        record) at the flat position computed by ``sources[i][1]`` (a
        callable over the i32 lane-index vector), select between them when
        ``selector`` (a callable producing a mask over the lanes) is given,
        and store the value at k in the result's region.

        The map callables emit their own (32,1) vector arithmetic through
        the _staging_* helpers; the loop is a dedicated counted chunk loop
        (sequential within one worker -- the layout lane's contract)."""
        loc = result.loc or fn.loc
        rec = self._staged[result.vid]
        esz_r = rec["esz"]
        extent = rec["extent"]
        if extent == 0:
            raise self._err(loc, "layout", "a zero-extent layout block")
        # the staging loop's uniform vl: the largest power-of-two vl that
        # divides the extent, capped at vlmax AND at 32 lanes (every
        # register class stays within m2 -- the allocator's budget; every
        # iteration is full -- the loop is mask-free)
        vl = min(self.target.vlmax(rec["lane_sew"], 1), 32)
        while vl > 1 and extent % vl:
            vl //= 2
        ws = self._workspace_private_reg(ctx, loc)
        if any(s[0]["type"] != sources[0][0]["type"] for s in sources):
            raise self._err(loc, "layout",
                            "a layout op's sources must share the element "
                            "type (join/split/interleave preserve it)")
        # the loop's lanes move the staged lane width (16-bit floats
        # ride their exact fp32 widening; the maps address elements of
        # esz)
        lane_sew = sources[0][0]["lane_sew"]
        lane_kind = "float" if sources[0][0]["type"].is_float() else "uint"

        tag = self._tag("stg")
        head = ctx.add_block(f"{tag}_head", [], loc)
        zero = ctx.const(0, mir.I32, loc)
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": head.name, "args": [zero]},
                          loc=loc))
        elem = mir.VReg(mir.I32, name=f"{tag}.elem")
        head.params += [elem]
        ctx.switch(head)
        extent_c = ctx.const(extent, mir.I32, loc)
        cont = ctx.emit(mir.MOp(
            "slt", [elem, extent_c],
            [ctx.vreg(mir.I64, hint="lgo", loc=loc)], loc=loc))
        body = ctx.add_block(f"{tag}_body", [elem], loc)
        exitb = ctx.add_block(f"{tag}_exit", [], loc)
        ctx.emit0(mir.MOp(
            "brc", [cont], [],
            attrs={"true_target": body.name, "true_args": [elem],
                   "false_target": exitb.name, "false_args": []}, loc=loc))
        ctx.switch(body)

        # the result's flat lane index
        idx = self._lane_index(ctx, elem, vl, loc)
        # the source values
        vals = []
        for src_rec, map_fn in sources:
            sidx = map_fn(ctx, idx, vl, loc)
            soff, _ = self._ws_scaled(ctx, sidx, src_rec["esz"], loc, vl)
            base = ctx.emit(mir.MOp(
                "sadd", [ws, ctx.const(src_rec["offset"], mir.I64, loc)],
                [ctx.vreg(mir.I64, hint="lsb", loc=loc)], loc=loc))
            kind = lane_kind
            sew_s = src_rec["lane_sew"]
            vtype = mir.VectorType(sew_s, 1, kind)
            self._vregion(ctx, vtype, loc, vl=vl)
            vals.append(ctx.emit(mir.MOp(
                "vloadix", [base, soff],
                [ctx.vreg(vtype, hint="lsv", loc=loc)],
                attrs={"eew": 64, "sew": sew_s},
                loc=loc)))
        if selector is not None:
            sel_mask = selector(ctx, idx, vl, loc)
            v0 = ctx.emit(mir.MOp(
                "vmovmask", [sel_mask],
                [ctx.vreg(mir.MaskType(), hint="lsv0", loc=loc,
                          fixed_phys="v0")], loc=loc))
            rtype = vals[0].type
            # vsel(v0, x, y) = v0 ? x : y: the mask selects vals[0] (the
            # even/minor-0 lanes), the fallback is vals[1]
            merged = ctx.emit(mir.MOp(
                "vsel", [v0, vals[0], vals[1]],
                [ctx.vreg(rtype, hint="lsl", loc=loc)], loc=loc))
        else:
            merged = vals[0]
        # store at the result's flat positions (the lane width; the
        # widened lane carries the value's bytes exactly)
        doff, _ = self._ws_scaled(ctx, idx, rec["esz"], loc, vl)
        dbase = ctx.emit(mir.MOp(
            "sadd", [ws, ctx.const(rec["offset"], mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="ldb", loc=loc)], loc=loc))
        self._vregion(ctx, mir.VectorType(lane_sew, 1, lane_kind),
                      loc, vl=vl)
        ctx.emit0(mir.MOp(
            "vstoreix", [dbase, doff, merged], [],
            attrs={"eew": 64, "sew": lane_sew}, loc=loc))
        # the step
        step = ctx.const(vl, mir.I32, loc)
        elem2 = ctx.emit(mir.MOp(
            "sadd", [elem, step],
            [ctx.vreg(mir.I32, hint="lse", loc=loc)], loc=loc))
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": head.name, "args": [elem2]},
                          loc=loc))
        ctx.switch(exitb)

    def _decompose_map(self, ctx: _Ctx, idx: mir.VReg, shape, src_shape,
                       vl: int, loc, drop_axes=(), zero_axes=(),
                       flip_axis=None):
        """The source flat position of each result lane for an
        axis-permuting/broadcasting map: decompose the result lane index
        by ``shape`` (the result shape), transform the per-axis indices
        (``drop_axes``: result axes with no source counterpart;
        ``zero_axes``: source axes held at 0; ``flip_axis``: the result
        axis whose index reverses), and recompose over the SOURCE strides
        (``src_shape``: the operand's own shape -- a singleton source axis
        that expands keeps its stride role).

        Emits (32,1) vector arithmetic; returns the source flat index
        vector."""
        n = len(shape)
        strides = []
        acc = 1
        for e in reversed(shape):
            strides.append(acc)
            acc *= e.value
        strides.reverse()
        src_strides = []
        acc = 1
        for e in reversed(src_shape):
            src_strides.append(acc)
            acc *= e.value
        src_strides.reverse()
        out = None
        si = 0
        for i in range(n):
            axis_idx = idx
            if strides[i] != 1:
                div = self._staging_const(ctx, strides[i], vl, loc)
                axis_idx = self._staging_vbin(ctx, "sdiv", idx, div, vl,
                                              loc)
            if shape[i].value != 1:
                mod = self._staging_const(ctx, shape[i].value, vl, loc)
                axis_idx = self._staging_vbin(ctx, "srem", axis_idx, mod,
                                              vl, loc)
            if flip_axis is not None and i == flip_axis:
                # idx' = extent - 1 - idx
                m1 = self._staging_const(ctx, shape[i].value - 1, vl, loc)
                axis_idx = self._staging_vbin(ctx, "sub", m1, axis_idx, vl,
                                              loc)
            if i in drop_axes:
                continue
            if si in zero_axes or src_shape[si].value == 1:
                si += 1
                continue
            term = axis_idx
            if src_strides[si] != 1:
                st = self._staging_const(ctx, src_strides[si], vl, loc)
                term = self._staging_vbin(ctx, "mul", axis_idx, st, vl,
                                          loc)
            out = term if out is None else self._staging_vbin(
                ctx, "add", out, term, vl, loc)
            si += 1
        if out is None:
            # every source axis is held at 0 (a pure splat through staging)
            out = self._staging_const(ctx, 0, vl, loc)
        return out

    def _stage_permute(self, ctx: _Ctx, fn: tir.Function, op: tir.Op) -> None:
        src = op.operands[0]
        dims = op.attrs["dims"]
        loc = op.loc or fn.loc
        src_rec = self._staged[src.vid]
        # result axis j is source axis dims[j]: the map decomposes the
        # RESULT index and recomposes over the source strides with the
        # axis roles swapped
        res_shape = op.results[0].shape

        def map_fn(ctx, idx, vl, loc):
            return self._permute_map(ctx, idx, res_shape, dims, vl, loc)

        self._emit_staging_loop(ctx, fn, op.results[0],
                                [(src_rec, map_fn)])

    def _permute_map(self, ctx: _Ctx, idx, res_shape, dims, vl, loc):
        """src_flat for a permute: decompose idx by the result shape, then
        recompose over the source strides in the permuted axis order."""
        n = len(res_shape)
        r_strides = []
        acc = 1
        for e in reversed(res_shape):
            r_strides.append(acc)
            acc *= e.value
        r_strides.reverse()
        # the source extents: source axis dims[j] carries res_shape[j]
        s_ext = [0] * n
        for j in range(n):
            s_ext[dims[j]] = res_shape[j].value
        s_strides = []
        acc = 1
        for e in reversed(s_ext):
            s_strides.append(acc)
            acc *= e
        s_strides.reverse()
        out = None
        for j in range(n):
            if s_ext[dims[j]] == 1 and res_shape[j].value == 1:
                continue          # a 1-axis contributes 0
            axis_idx = idx
            if r_strides[j] != 1:
                d = self._staging_const(ctx, r_strides[j], vl, loc)
                axis_idx = self._staging_vbin(ctx, "sdiv", idx, d, vl, loc)
            if res_shape[j].value != 1:
                m = self._staging_const(ctx, res_shape[j].value, vl, loc)
                axis_idx = self._staging_vbin(ctx, "srem", axis_idx, m, vl,
                                              loc)
            if s_strides[dims[j]] != 1:
                st = self._staging_const(ctx, s_strides[dims[j]], vl, loc)
                axis_idx = self._staging_vbin(ctx, "mul", axis_idx, st, vl,
                                              loc)
            out = axis_idx if out is None else self._staging_vbin(
                ctx, "add", out, axis_idx, vl, loc)
        if out is None:
            out = self._staging_const(ctx, 0, vl, loc)
        return out

    def _stage_flip(self, ctx: _Ctx, fn: tir.Function, op: tir.Op) -> None:
        src = op.operands[0]
        dim = op.attrs["dim"]
        loc = op.loc or fn.loc
        src_rec = self._staged[src.vid]

        def map_fn(ctx, idx, vl, loc):
            return self._decompose_map(ctx, idx, op.results[0].shape,
                                       list(op.results[0].shape), vl,
                                       loc, flip_axis=dim)

        self._emit_staging_loop(ctx, fn, op.results[0],
                                [(src_rec, map_fn)])

    def _stage_join(self, ctx: _Ctx, fn: tir.Function, op: tir.Op) -> None:
        a, b = op.operands
        loc = op.loc or fn.loc
        a_rec, b_rec = self._staged[a.vid], self._staged[b.vid]

        def map_a(ctx, idx, vl, loc):
            two = self._staging_const(ctx, 2, vl, loc)
            return self._staging_vbin(ctx, "sdiv", idx, two, vl, loc)

        map_b = map_a

        def selector(ctx, idx, vl, loc):
            # the minor-axis parity: even lanes take a, odd lanes take b
            one = self._staging_const(ctx, 1, vl, loc)
            parity = self._staging_vbin(ctx, "and", idx, one, vl, loc)
            zero = self._staging_const(ctx, 0, vl, loc)
            self._staging_region(ctx, 32, vl, loc)
            return ctx.emit(mir.MOp(
                "vcmp", [parity, zero],
                [ctx.vreg(mir.MaskType(), hint="lsp", loc=loc)],
                attrs={"pred": "eq", "fp": False}, loc=loc))

        self._emit_staging_loop(ctx, fn, op.results[0],
                                [(a_rec, map_a), (b_rec, map_b)],
                                selector=selector)

    def _stage_split(self, ctx: _Ctx, fn: tir.Function, op: tir.Op) -> None:
        src = op.operands[0]
        loc = op.loc or fn.loc
        src_rec = self._staged[src.vid]
        for c, result in enumerate(op.results):

            def map_fn(ctx, idx, vl, loc, c=c):
                two = self._staging_const(ctx, 2, vl, loc)
                off = self._staging_const(ctx, c, vl, loc)
                scaled = self._staging_vbin(ctx, "mul", idx, two, vl, loc)
                return self._staging_vbin(ctx, "add", scaled, off, vl,
                                          loc)

            self._emit_staging_loop(ctx, fn, result, [(src_rec, map_fn)])

    def _stage_broadcast(self, ctx: _Ctx, fn: tir.Function, op: tir.Op) -> None:
        src = op.operands[0]
        loc = op.loc or fn.loc
        src_rec = self._staged[src.vid]
        src_shape = src.shape
        res_shape = op.results[0].shape
        pad = len(res_shape) - len(src_shape)
        drop_axes = tuple(range(pad))
        zero_axes = set()
        for i, e in enumerate(src_shape):
            if e.value == 1 and res_shape[pad + i].value != 1:
                zero_axes.add(i)

        def map_fn(ctx, idx, vl, loc):
            return self._decompose_map(ctx, idx, res_shape, list(src_shape),
                                       vl, loc,
                                       drop_axes=drop_axes,
                                       zero_axes=frozenset(zero_axes))

        self._emit_staging_loop(ctx, fn, op.results[0],
                                [(src_rec, map_fn)])

    def _scan_init_reg(self, ctx: _Ctx, frame: dict, ident,
                       loc) -> mir.VReg:
        """The scan carry's initial register: the identity at the carry's
        own representation (a scalar for integers, a lane-0 vector for
        floats -- scalar float arithmetic runs through the vector path)."""
        vtype = frame["vtype"]
        if vtype.kind == "float":
            return self._splat_const(ctx, ident, vtype, loc)
        sty = mir.ScalarType(vtype.sew, signed=vtype.kind != "uint")
        mask = (1 << vtype.sew) - 1
        kreg = ctx.const(int(ident) & mask, sty, loc)
        return kreg

    def _tir_type_of(self, vtype: mir.VectorType) -> tir.Type:
        if vtype.kind == "float":
            return tir.FLOAT32 if vtype.sew == 32 else tir.FLOAT64
        if vtype.kind == "uint":
            return tir.Type("uint", vtype.sew)
        return tir.Type("int", vtype.sew)

    def _close_chunk_back_edge(self, ctx: _Ctx, fn: tir.Function,
                               strided: Optional[bool] = None) -> None:
        """The chunk loop's back edge, from the block the kernel body ended
        in: elem += vl (or worker_count*vl on the split path); items += the
        stored-element count (exact when the first masked store sits at the
        chunk body's top level, else one vector chunk of useful work per
        iteration -- recorded in meta); every merge accumulator combines
        with the body's current value under the source's own merge rule."""
        loc = fn.loc
        chunk = self._chunk
        if strided is None:
            strided = chunk["strided"]
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
        if strided:
            step = ctx.emit(mir.MOp(
                "strunc", [self._chunk_step],
                [ctx.vreg(mir.I32, hint="sst", loc=loc)], loc=loc))
        else:
            step = ctx.const(chunk["vl"], mir.I32, loc)
        elem_next = ctx.emit(mir.MOp(
            "sadd", [elem_b, step],
            [ctx.vreg(mir.I32, hint="elem2", loc=loc)], loc=loc))
        # re-establish the data region: the merge combines are vector ops
        avl = ctx.const(chunk["vl"], mir.I32, loc)
        ctx.emit(mir.MOp("vsetvli", [avl],
                         [ctx.vreg(mir.I32, hint="bvl", loc=loc)],
                         attrs={"sew": self._sew, "lmul": 1,
                                "policy": "ta,ma"}, loc=loc))
        merge_next: List[mir.VReg] = []
        for frame in self._chunk_merges:
            if frame["source"] == "scan":
                merge_next.append(frame["acc_now"])
                continue
            if frame.get("index"):
                if frame.get("cand_val") is not None:
                    cand_v = self._cand_of_reg(ctx, frame["cand_val"],
                                               frame["acc_v"], loc)
                    cand_i = self._cand_of_reg(ctx, frame["cand_idx"],
                                               frame["acc_i"], loc)
                else:
                    cand_v = self._cand_of(ctx, frame["vid"], frame["acc_v"],
                                           loc)
                    cand_i = self._cand_of(ctx, frame["pair_vid"],
                                           frame["acc_i"], loc)
                v2, i2 = self._combine_pair(ctx, frame["acc_v"],
                                            frame["acc_i"], cand_v, cand_i,
                                            frame["kind"], loc)
                merge_next.extend((v2, i2))
            else:
                cand = self._cand_of(ctx, frame["vid"], frame["acc"], loc)
                merge_next.append(self._combine_value(ctx, frame["acc"],
                                                      cand, frame["kind"],
                                                      loc))
        # the live-out scalars spill before the back edge (inside the
        # body; their value is chunk-invariant so any iteration's is the
        # value the exit reloads)
        self._store_liveouts(ctx, loc)
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": chunk["head"].name,
                                 "args": [elem_next, items_next] +
                                 merge_next}, loc=loc))

    def _cand_of_reg(self, ctx: _Ctx, reg: mir.VReg, acc: mir.VReg,
                     loc) -> mir.VReg:
        """Splat one recorded scalar candidate to the accumulator type."""
        if reg.is_vector() and reg.type == acc.type:
            return reg
        scalar = self._scalarize(ctx, reg, loc)
        return ctx.emit(mir.MOp(
            "s2v", [scalar], [ctx.vreg(acc.type, hint="mc", loc=loc)],
            loc=loc))

    def _cand_of(self, ctx: _Ctx, vid: int, acc: mir.VReg,
                 loc) -> mir.VReg:
        """The candidate vector for one merge step: the body's current
        value of the partial, splatted to the accumulator's type (lane 0
        carries the value; the other lanes are never read)."""
        reg = self.values.get(vid)
        if reg is None:
            raise self._err(loc, "merge",
                            "a partial has no lowered value at the chunk "
                            "back edge (the plan and the lowering disagree)")
        if reg.is_vector() and reg.type == acc.type:
            return reg
        scalar = self._scalarize(ctx, reg, loc)
        if scalar.type.width != acc.type.sew:
            raise self._err(loc, "merge",
                            f"partial width {scalar.type.width} does not "
                            f"match the accumulator SEW {acc.type.sew}")
        return ctx.emit(mir.MOp(
            "s2v", [scalar], [ctx.vreg(acc.type, hint="mc", loc=loc)],
            loc=loc))

    # -- regions -------------------------------------------------------------------
    def _lower_if(self, ctx: _Ctx, stmt: tir.If, fn: tir.Function,
                  view_regs: Dict[str, mir.VReg]) -> None:
        loc = stmt.loc or fn.loc
        cond = self._bool_scalar(ctx, self._need(stmt.cond, loc), loc)
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
            self._region_depth += 1
            self._lower_statements(ctx, arm.statements, fn, view_regs)
            self._region_depth -= 1
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
            if value.vid in self._stage_out:
                raise self._err(
                    loc, "layout",
                    f"a region join value ('{value.name}') cannot cross a "
                    "pass boundary (the layout lane stages top-level "
                    "values only)")
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
        self._region_depth += 1
        self._lower_statements(ctx, stmt.body.statements, fn, view_regs)
        self._region_depth -= 1
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
            if value.vid in self._stage_out:
                raise self._err(
                    loc, "layout",
                    f"a loop join value ('{value.name}') cannot cross a "
                    "pass boundary (the layout lane stages top-level "
                    "values only)")
            self.values[value.vid] = param
            for key in value.scope_names():
                names.define(key, value)

    def _lower_while(self, ctx: _Ctx, stmt: tir.Loop, fn: tir.Function,
                     view_regs: Dict[str, mir.VReg], loc, names) -> None:
        cond_init = self._bool_scalar(ctx, self._need(stmt.cond, loc), loc)
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
        self._region_depth += 1
        self._lower_statements(ctx, stmt.body.statements, fn, view_regs)
        self._region_depth -= 1
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
            if value.vid in self._stage_out:
                raise self._err(
                    loc, "layout",
                    f"a while-join value ('{value.name}') cannot cross a "
                    "pass boundary (the layout lane stages top-level "
                    "values only)")
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
            ty = op.results[0].type
            if ty.is_float() and ty.bitwidth() == 16:
                # the scalar core has no fp16 registers: the constant
                # materializes at fp32 (exact for the literal) and the
                # 16-bit consumers (the broadcast splat) round it once
                reg = scalar_mod.lower_const(ctx, op.attrs["value"],
                                             tir.FLOAT32, loc)
                self._bind_result(op, reg)
                return
            reg = scalar_mod.lower_const(ctx, op.attrs["value"],
                                         op.results[0].type, loc)
            self._bind_result(op, reg)
            return
        if code == "arange":
            if self._chunk is None:
                raise self._err(loc, "tl.arange",
                                "tl.arange used before any block-level "
                                "statement opened the vector chunk region")
            ity = self._vtype(tir.INT32)
            self._vregion(ctx, ity, loc)
            vid = ctx.emit(mir.MOp(
                "vid", [], [ctx.vreg(ity, hint="iota", loc=loc)], loc=loc))
            reg = ctx.emit(mir.MOp(
                "vbinx", [vid, self._chunk["elem"]],
                [ctx.vreg(ity, hint="ar", loc=loc)],
                attrs={"op": "add"}, loc=loc))
            self._restore_region(ctx, loc)
            self._bind_result(op, reg)
            return
        if code == "broadcast":
            operand = self._need(op.operands[0], loc)
            rty = op.results[0].type
            if rty.is_bool() and operand.is_mask():
                # a boolean scalar (a mask register) broadcasts to any
                # shape: the mask is lane-count agnostic (the active vl
                # governs) -- no (1,·) vector form exists (SEW < 8 is not
                # a legal vector element width)
                self._bind_result(op, operand)
                return
            if rty.is_bool() and not operand.is_vector():
                # a boolean scalar held in a GPR (a scalar comparison's
                # 0/1): splat at i32 and compare != 0 -- the mask form
                ity = self._idx_vtype(self._vl)
                self._vregion(ctx, ity, loc)
                splat = self._splat_reg(ctx, operand, ity, loc)
                zero = self._splat_const(ctx, 0, ity, loc)
                reg = ctx.emit(mir.MOp(
                    "vcmp", [splat, zero],
                    [ctx.vreg(mir.MaskType(), hint="bcm", loc=loc)],
                    attrs={"pred": "ne", "fp": False}, loc=loc))
                self._restore_region(ctx, loc)
                self._bind_result(op, reg)
                return
            if not operand.is_vector() and rty.is_float() \
                    and rty.bitwidth() == 16 \
                    and op.operands[0].rank == 0:
                # a 16-bit float splat of a scalar: splat at fp32 and
                # round once (the scalar core holds no fp16 values)
                v32 = self._vtype(tir.FLOAT32)
                self._vregion(ctx, v32, loc)
                splat32 = self._splat_reg(ctx, operand, v32, loc)
                reg = self._f32_to_ff(ctx, splat32, rty, loc)
                self._bind_result(op, reg)
                return
            if operand.is_vector():
                # a block source: the extent-1 splat is in-pass (every lane
                # is lane 0); any other block broadcast is a layout segment
                # (the staging loop lowered it before the pass opened)
                src = op.operands[0]
                n_src = self._flat_extent_of(src.shape, loc, "broadcast")
                if n_src != 1:
                    raise self._err(loc, "broadcast",
                                    "broadcast of a multi-lane block is a "
                                    "layout segment (it lowers through the "
                                    "staging loop; a broadcast here means "
                                    "the op sits inside a runtime region -- "
                                    "not in the layout lane)")
                scalar = self._scalarize(ctx, operand, loc)
                vtype = self._value_vtype(op.results[0].type)
                switched = self._open_region(ctx, vtype, loc)
                reg = ctx.emit(mir.MOp(
                    "s2v", [scalar],
                    [ctx.vreg(vtype, hint="spl1", loc=loc)], loc=loc))
                if switched:
                    self._restore_region(ctx, loc)
                self._bind_result(op, reg)
                return
            vtype = self._value_vtype(op.results[0].type)
            switched = self._open_region(ctx, vtype, loc)
            reg = ctx.emit(mir.MOp(
                "s2v", [operand],
                [ctx.vreg(vtype, hint="splat", loc=loc)], loc=loc))
            if switched:
                self._restore_region(ctx, loc)
            self._bind_result(op, reg)
            return
        if code == "reshape":
            # flat-identity metadata: the register (or the staged region)
            # carries over unchanged; only the shape metadata changes
            src = op.operands[0]
            if src.vid in self._staged:
                self._staged[op.results[0].vid] = self._staged[src.vid]
                if self._names is not None:
                    for key in op.results[0].scope_names():
                        self._names.define(key, op.results[0])
                return
            reg = self._need(src, loc)
            self.values[op.results[0].vid] = reg
            if self._names is not None:
                for key in op.results[0].scope_names():
                    self._names.define(key, op.results[0])
            if op.results[0].vid in self._stage_out:
                # the metadata result is the layout operand: its lanes are
                # the source's lanes -- stage them here
                self._store_staged(op.results[0], reg, loc)
            return
        if code == "realize":
            src = op.operands[0]
            if src.vid in self._staged:
                # the staging loop already materialized real lanes
                self._staged[op.results[0].vid] = self._staged[src.vid]
                if self._names is not None:
                    for key in op.results[0].scope_names():
                        self._names.define(key, op.results[0])
                return
            reg = self._need(src, loc)
            self.values[op.results[0].vid] = reg
            if self._names is not None:
                for key in op.results[0].scope_names():
                    self._names.define(key, op.results[0])
            if op.results[0].vid in self._stage_out:
                self._store_staged(op.results[0], reg, loc)
            return
        if code in ("permute", "flip", "join", "split", "interleave"):
            raise self._err(
                loc, code,
                f"a layout op ('{code}') inside a runtime region is not in "
                "the layout lane (the staging loops lower top-level layout "
                "ops only)")
        if code == "ptradd":
            self.pointer_ops[op.results[0].vid] = op
            self.values[op.results[0].vid] = self._need(op.operands[0], loc)
            return
        if code in tir.BIN_ARITH or code in tir.BIN_BITWISE:
            lhs, rhs = op.operands
            lreg, rreg = self._need(lhs, loc), self._need(rhs, loc)
            if lreg.is_scalar() and rreg.is_scalar():
                if lreg.type.float or rreg.type.float:
                    reg = self._scalar_float_binop(ctx, op, lreg, rreg, loc)
                else:
                    reg = scalar_mod.lower_binop(ctx, op, lreg, rreg, loc)
            else:
                reg = self._vbin(ctx, op, lreg, rreg, loc)
            self._bind_result(op, reg)
            return
        if code in tir.CMP_PREDS:
            lhs, rhs = op.operands
            lreg, rreg = self._need(lhs, loc), self._need(rhs, loc)
            if lreg.is_scalar() and rreg.is_scalar():
                if lreg.type.float or rreg.type.float:
                    reg = self._scalar_float_cmp(ctx, op, lreg, rreg, loc)
                else:
                    reg = scalar_mod.lower_cmp(ctx, op, lreg, rreg, loc)
            else:
                # the declared numeric decision (T012): 16-bit float
                # compares run in FP32 lanes (bf16 bits are NOT fp16
                # bits -- comparing them at e16 misreads the format; the
                # single-rounding policy's fp32 domain)
                if lreg.is_vector() and lreg.type.kind == "float" \
                        and lreg.type.sew == 16 \
                        and self.options.fp16_bf16_fp32_lanes:
                    ty16 = lhs.type if lhs.type.is_float() \
                        and lhs.type.bitwidth() == 16 else rhs.type
                    if not (ty16.is_float() and ty16.bitwidth() == 16):
                        raise self._err(loc, code,
                                        "a 16-bit float compare without "
                                        "its TIR type")
                    l32 = self._f16_to_f32(ctx, lreg, ty16, loc)
                    if rreg.is_vector():
                        r32 = self._f16_to_f32(ctx, rreg, ty16, loc) \
                            if rreg.type.sew == 16 else rreg
                    else:
                        r32 = self._splat_reg(ctx, rreg, l32.type, loc)
                    self._vregion(ctx, l32.type, loc)
                    reg = ctx.emit(mir.MOp(
                        "vcmp", [l32, r32],
                        [ctx.vreg(mir.MaskType(), hint="m3", loc=loc)],
                        attrs={"pred": code.split(".")[1], "fp": True},
                        loc=loc))
                    self._restore_region(ctx, loc)
                else:
                    switched = self._open_region(
                        ctx, lreg.type if lreg.is_vector() else rreg.type,
                        loc)
                    reg = ctx.emit(mir.MOp(
                        "vcmp", [lreg, rreg],
                        [ctx.vreg(mir.MaskType(), hint="m", loc=loc)],
                        attrs={"pred": code.split(".")[1],
                               "fp": lhs.type.is_float()}, loc=loc))
                    if switched:
                        self._restore_region(ctx, loc)
            self._bind_result(op, reg)
            return
        if code in tir.UNARY_OPS:
            operand = self._need(op.operands[0], loc)
            if operand.is_scalar():
                if code == "logical.not":
                    reg = scalar_mod.lower_not(ctx, operand, loc)
                    self._bind_result(op, reg)
                    return
                if code in ("arith.neg", "arith.fneg") \
                        and operand.type.float:
                    reg = self._scalar_float_unary(ctx, code, operand, loc)
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
            if xreg.is_scalar() and yreg.is_scalar():
                # a scalar select: splat both branches, select, extract
                if not mreg.is_mask():
                    mreg = self._mask_of_bool(ctx, mreg, loc)
                vtype = self._vtype(x.type)
                xs = ctx.emit(mir.MOp(
                    "s2v", [xreg], [ctx.vreg(vtype, hint="ssx", loc=loc)],
                    loc=loc))
                ys = ctx.emit(mir.MOp(
                    "s2v", [yreg], [ctx.vreg(vtype, hint="ssy", loc=loc)],
                    loc=loc))
                v0 = ctx.emit(mir.MOp(
                    "vmovmask", [mreg],
                    [ctx.vreg(mir.MaskType(), hint="v0", loc=loc,
                              fixed_phys="v0")], loc=loc))
                sel = ctx.emit(mir.MOp(
                    "vsel", [v0, xs, ys],
                    [ctx.vreg(vtype, hint="ssel", loc=loc)], loc=loc))
                self._bind_result(op, self._scalarize(ctx, sel, loc))
                return
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
            if op.results[0].rank == 0:
                # a rank-0 zeros/full is a scalar constant (tl.zeros([], d)
                # -- the persistent-reduction accumulators)
                self._bind_result(op, kreg)
                return
            reg = ctx.emit(mir.MOp(
                "s2v", [kreg],
                [ctx.vreg(self._vtype(ty), hint="cst", loc=loc)], loc=loc))
            self._bind_result(op, reg)
            return
        if code == "convert":
            self._lower_convert(ctx, op, loc)
            return
        if code == "debug_barrier":
            # intra-program ordering: a program instance executes on one
            # worker thread, so an explicit fence orders its own memory
            # operations (the cross-worker stage barrier would desync the
            # pool -- programs are strided across workers)
            scalar_mod.emit_debug_barrier(ctx, loc)
            return
        if code == "hint":
            # a recorded promise (multiple_of / max_contiguous): an
            # identity at the value level; the wide-access proof reads the
            # attrs from the TIR op itself
            self.values[op.results[0].vid] = self._need(op.operands[0], loc)
            return
        if code == "bitcast":
            # width-preserving reinterpretation: the same register under
            # the target type's view (the pointer-table pattern's int64 ->
            # pointer form keeps the scalar identity; the vector forms
            # retype the register through the bit-level move)
            sreg = self._need(op.operands[0], loc)
            if sreg.is_vector():
                vtype = self._vtype(op.results[0].type)
                if vtype.lmul != sreg.type.lmul:
                    raise self._err(
                        loc, "bitcast",
                        f"the reinterpretation view {vtype!r} does not "
                        f"match the register footprint {sreg.type!r}")
                reg = self._vmovv(ctx, sreg, vtype, loc)
                self._bind_result(op, reg)
                return
            self.values[op.results[0].vid] = sreg
            if self._names is not None:
                for key in op.results[0].scope_names():
                    self._names.define(key, op.results[0])
            return
        if code == "atomic_rmw":
            scalar_mod.lower_atomic_rmw(self, ctx, op, loc)
            return
        if code == "atomic_cas":
            scalar_mod.lower_atomic_cas(self, ctx, op, loc)
            return
        if code == "gather":
            scalar_mod.lower_gather(self, ctx, op, loc)
            return
        if code == "interleave":
            raise self._err(
                loc, "tl.interleave",
                "interleave produces a 2x-extent block; the one-extent "
                "chunk region cannot host its operands -- the construct "
                "lowers through the standalone program-level path "
                "(a100c.lower.scalar.lower_interleave), and the composed "
                "kernel form is the layout lane's (multi-extent blocks)")
        if code == "reduce":
            self._lower_reduce(ctx, op, loc)
            return
        if code == "scan":
            self._lower_scan(ctx, op, loc)
            return
        if code == "sort":
            raise self._err(
                loc, "tl.sort",
                "a whole-block reorder needs the block-materialization "
                "protocol of the layout lane (multi-shape blocks); the "
                "sort semantics (dim, descending, stability) are declared "
                "in a100c/plan/stages.py (a located refusal, never a "
                "wrong order)")
        if code == "topk":
            raise self._err(
                loc, "tl.topk",
                "topk produces a block whose extent differs from the "
                "kernel's block extent (k along dim); multi-shape blocks "
                "are the layout lane's path -- the semantics are declared "
                "in a100c/plan/stages.py")
        if code == "histogram":
            raise self._err(
                loc, "tl.histogram",
                "tl.histogram produces a [num_bins] block whose shape "
                "differs from the kernel's block extent; multi-shape "
                "blocks are the layout lane's path -- the counting "
                "semantics are declared in a100c/plan/stages.py")
        if code in ("dot", "scatter"):
            from a100c.lower import matrix
            matrix.refuse_matrix(loc, code,
                                 f"construct '{code}' routes to the matrix/"
                                 "reduction path")
        raise self._err(loc, code, "op is not lowered by the vector slice")

    # -- reductions (T009) --------------------------------------------------------
    def _lower_reduce(self, ctx: _Ctx, op: tir.Op, loc) -> None:
        """One TIR reduce op inside the chunk region: the intra-program
        RVV reduction over the operand's current chunk slice (vred* with
        the per-op-and-dtype identity splat), extracted to a scalar for
        in-region uses; the plan's chunk accumulator folds the per-chunk
        partials at the back edge."""
        if self._chunk is None:
            raise self._err(loc, "reduce",
                            "a reduction outside the vector chunk region "
                            "(the operand must be a block value)")
        attrs = op.attrs
        kind = attrs["kind"]
        value = op.operands[0]
        vreg = self._need(value, loc)
        if not vreg.is_vector():
            raise self._err(loc, "reduce",
                            "the reduction operand is not a block value at "
                            "this position (a scalar cannot reduce)")
        if vreg.type.sew != self._sew:
            raise self._err(
                loc, "reduce",
                f"reduction operand SEW {vreg.type.sew} is not the data "
                f"SEW {self._sew} (multi-width blocks are a later path)")
        if vreg.type.kind == "uint" and kind in ("max", "min"):
            # the unsigned forms select their own repertoire row
            pass
        keep = bool(attrs.get("keep_dims"))
        if keep:
            raise self._err(
                loc, "reduce",
                "keep_dims=True produces extent-1 block axes; multi-shape "
                "blocks are the layout lane's path (the semantics are "
                "declared in a100c/plan/stages.py)")
        index_form = kind in ("argmax", "argmin")
        ret_idx = bool(attrs.get("return_indices"))
        # the per-chunk value partial (the TIR kind maps onto the vred
        # kinds: xor_sum/reduce_or are the bitwise reductions)
        vred_kind = {"sum": "sum", "max": "max", "min": "min",
                     "argmax": "max", "argmin": "min",
                     "xor_sum": "xor", "reduce_or": "or"}[kind]
        part = self._vred(ctx, vreg, vred_kind, loc)
        if index_form or ret_idx:
            m_scalar = self._scalarize(ctx, part, loc)
            match = ctx.emit(mir.MOp(
                "vcmp", [vreg, self._splat_reg(ctx, m_scalar, vreg.type,
                                               loc)],
                [ctx.vreg(mir.MaskType(), hint="rm", loc=loc)],
                attrs={"pred": "eq", "fp": vreg.type.kind == "float"},
                loc=loc))
            idx_vec = self._block_index_vec(ctx, loc)
            left = bool(attrs.get("tie_break_left", True))
            filler = (1 << 31) - 1 if left else 0
            filler_vec = self._splat_const(
                ctx, filler, mir.VectorType(32, 1, "int"), loc)
            sel_idx = ctx.emit(mir.MOp(
                "vsel", [self._vmovmask_of(ctx, match, loc), idx_vec,
                         filler_vec],
                [ctx.vreg(mir.VectorType(32, 1, "int"), hint="si", loc=loc)],
                loc=loc))
            red_kind = "min" if left else "max"
            arg_part = self._vred(ctx, sel_idx, red_kind, loc)
            a_scalar = self._scalarize(ctx, arg_part, loc)
        if index_form:
            self._bind_result(op, a_scalar)
            # a plan partial whose escaping value is the INDEX: record the
            # internal (value, index) candidate pair for the merge -- the
            # value never exists as a TIR value the plan can point at
            for frame in self._chunk_merges:
                if frame["source"] == "plan" and frame["vid"] == \
                        op.results[0].vid:
                    frame["cand_val"] = m_scalar
                    frame["cand_idx"] = a_scalar
            return
        if ret_idx:
            self._bind_result(op, m_scalar)
            self.values[op.results[1].vid] = a_scalar
            if self._names is not None:
                for key in op.results[1].scope_names():
                    self._names.define(key, op.results[1])
            for frame in self._chunk_merges:
                if frame["source"] == "plan" and frame["vid"] == \
                        op.results[0].vid:
                    frame["cand_val"] = m_scalar
                    frame["cand_idx"] = a_scalar
            return
        self._bind_result(op, self._scalarize(ctx, part, loc))

    def _vred(self, ctx: _Ctx, vreg: mir.VReg, kind: str,
              loc) -> mir.VReg:
        """One vector reduction of the current chunk slice against the
        per-op-and-dtype identity splat (the identity rides vs1[0])."""
        ident = stages_mod.identity_for(
            {"xor": "xor_sum", "or": "reduce_or"}.get(kind, kind),
            self._tir_type_of(vreg.type))
        ident_vec = self._splat_const(ctx, ident, vreg.type, loc)
        return ctx.emit(mir.MOp(
            "vred", [vreg, ident_vec],
            [ctx.vreg(vreg.type, hint="vr", loc=loc)],
            attrs={"kind": kind}, loc=loc))

    def _block_index_vec(self, ctx: _Ctx, loc) -> mir.VReg:
        """The block-space indices of the current chunk's lanes (vid +
        elem -- the same index space tl.arange produces)."""
        vid = ctx.emit(mir.MOp(
            "vid", [], [ctx.vreg(mir.VectorType(32, 1, "int"),
                                 hint="aid", loc=loc)], loc=loc))
        return ctx.emit(mir.MOp(
            "vbinx", [vid, self._chunk["elem"]],
            [ctx.vreg(mir.VectorType(32, 1, "int"), hint="aidx", loc=loc)],
            attrs={"op": "add"}, loc=loc))

    def _vmovmask_of(self, ctx: _Ctx, mask: mir.VReg, loc) -> mir.VReg:
        return ctx.emit(mir.MOp(
            "vmovmask", [mask],
            [ctx.vreg(mir.MaskType(), hint="v0", loc=loc,
                      fixed_phys="v0")], loc=loc))

    def _splat_reg(self, ctx: _Ctx, scalar: mir.VReg,
                   vtype: mir.VectorType, loc) -> mir.VReg:
        return ctx.emit(mir.MOp(
            "s2v", [scalar], [ctx.vreg(vtype, hint="sp", loc=loc)],
            loc=loc))

    def _mask_of_bool(self, ctx: _Ctx, bool_reg: mir.VReg,
                      loc) -> mir.VReg:
        """A mask from an i64 0/1 bool: splat and compare against zero."""
        vtype = mir.VectorType(64, 1, "int")
        splat = ctx.emit(mir.MOp(
            "s2v", [bool_reg], [ctx.vreg(vtype, hint="bs", loc=loc)],
            loc=loc))
        zero = self._splat_const(ctx, 0, vtype, loc)
        return ctx.emit(mir.MOp(
            "vcmp", [splat, zero],
            [ctx.vreg(mir.MaskType(), hint="bm", loc=loc)],
            attrs={"pred": "ne", "fp": False}, loc=loc))

    def _lower_scan(self, ctx: _Ctx, op: tir.Op, loc) -> None:
        """One TIR scan op: materialize the operand's chunk slice to the
        worker-private workspace, run the sequential prefix (carried
        across chunks by the back-edge pass-merge), load the slice back as
        the block result."""
        if self._chunk is None:
            raise self._err(loc, "scan",
                            "a scan outside the vector chunk region")
        kind = op.attrs["kind"]
        vreg = self._need(op.operands[0], loc)
        if not vreg.is_vector() or vreg.type.sew != self._sew:
            raise self._err(loc, "scan",
                            "the scan operand is not a block value at the "
                            "data SEW")
        elem = self._chunk["elem"]
        vl = self._chunk["vl"]
        ws = self._workspace_private_reg(ctx, loc)
        # store this chunk's operand slice: byte offsets (elem + vid) * 4
        byte_idx = self._ws_byte_index(ctx, elem, loc)
        ctx.emit0(mir.MOp(
            "vstoreix", [ws, byte_idx, vreg], [],
            attrs={"eew": 64, "sew": self._sew}, loc=loc))
        # the sequential prefix over this chunk's elements, carried by the
        # chunk back edge (the frame's acc register)
        frame = next(f for f in self._chunk_merges
                     if f["source"] == "scan" and f["vid"] ==
                     op.results[0].vid)
        acc = frame["acc"]
        j0 = ctx.const(0, mir.I64, loc)
        jn = ctx.const(vl, mir.I64, loc)
        loop = scalar_mod.begin_counted_loop(ctx, j0, jn, [acc], loc,
                                             "scanp")
        j = loop.params[0]
        cur = loop.params[1]
        # the element address: ws + (elem + j) * 4 (elem is a runtime
        # chunk register; the base folds the byte offset in)
        elem64 = ctx.emit(mir.MOp(
            "smove", [elem], [ctx.vreg(mir.I64, hint="e64", loc=loc)],
            loc=loc)) if elem.type.width == 32 else elem
        ej = ctx.emit(mir.MOp(
            "sadd", [elem64, j],
            [ctx.vreg(mir.I64, hint="ej", loc=loc)], loc=loc))
        addr = ctx.emit(mir.MOp(
            "smul", [ej, ctx.const(4, mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="ea", loc=loc)], loc=loc))
        ws_i = ctx.emit(mir.MOp(
            "sadd", [ws, addr],
            [ctx.vreg(mir.I64, hint="wsb", loc=loc)], loc=loc))
        sty = mir.ScalarType(self._sew, signed=True,
                             float=vreg.type.kind == "float")
        v = ctx.emit(mir.MOp(
            "sload", [ws_i], [ctx.vreg(sty, hint="sv", loc=loc)],
            attrs={"width": self._sew, "offset": 0, "ext": "sext"},
            loc=loc))
        if vreg.type.kind == "float":
            # the float carry stays a lane-0 vector through the inner loop
            # (scalar float arithmetic runs through the vector path)
            accv = cur if cur.is_vector() else \
                self._splat_reg(ctx, cur, vreg.type, loc)
            vv = self._splat_reg(ctx, v, vreg.type, loc)
            vop = "add" if kind == "cumsum" else "mul"
            nxt = ctx.emit(mir.MOp(
                "vbin", [accv, vv],
                [ctx.vreg(vreg.type, hint="sa", loc=loc)],
                attrs={"op": vop}, loc=loc))
            new_acc = nxt
        else:
            code = "sadd" if kind == "cumsum" else "smul"
            new_acc = ctx.emit(mir.MOp(
                code, [cur, v],
                [ctx.vreg(sty, hint="sa", loc=loc)], loc=loc))
        ctx.emit0(mir.MOp(
            "sstore", [ws_i, self._scalarize(ctx, new_acc, loc)], [],
            attrs={"width": self._sew, "offset": 0}, loc=loc))
        j2 = ctx.emit(mir.MOp(
            "sadd", [j, ctx.const(1, mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="sj", loc=loc)], loc=loc))
        scalar_mod.close_loop(ctx, loop, [j2, new_acc])
        frame["acc_now"] = loop.exit.params[1]
        # the scan's continuation is the inner loop's exit block (its
        # body ended at the back edge)
        ctx.switch(loop.exit)
        avl3 = ctx.const(self._vl, mir.I32, loc)
        ctx.emit(mir.MOp("vsetvli", [avl3],
                         [ctx.vreg(mir.I32, hint="svl", loc=loc)],
                         attrs={"sew": self._sew, "lmul": 1,
                                "policy": "ta,ma"}, loc=loc))
        # the scan result: this chunk's updated slice, loaded back
        result = ctx.emit(mir.MOp(
            "vloadix", [ws, byte_idx],
            [ctx.vreg(vreg.type, hint="scan", loc=loc)],
            attrs={"eew": 64, "sew": self._sew}, loc=loc))
        self._bind_result(op, result)

    def _ws_byte_index(self, ctx: _Ctx, elem: mir.VReg,
                       loc) -> mir.VReg:
        """The byte-offset index vector for a workspace access at the
        current chunk: (elem + vid) * element size, at EEW=64."""
        vid = ctx.emit(mir.MOp(
            "vid", [], [ctx.vreg(mir.VectorType(32, 1, "int"),
                                 hint="wid", loc=loc)], loc=loc))
        offs = ctx.emit(mir.MOp(
            "vbinx", [vid, elem],
            [ctx.vreg(mir.VectorType(32, 1, "int"), hint="wo", loc=loc)],
            attrs={"op": "add"}, loc=loc))
        wide = ctx.emit(mir.MOp(
            "vwaddx0", [offs],
            [ctx.vreg(mir.VectorType(64, 2, "int"), hint="ww", loc=loc)],
            attrs={"mode": "sext"}, loc=loc))
        avl = ctx.const(self._vl, mir.I32, loc)
        ctx.emit(mir.MOp("vsetvli", [avl],
                         [ctx.vreg(mir.I32, hint="wvl", loc=loc)],
                         attrs={"sew": 64, "lmul": 2, "policy": "ta,ma"},
                         loc=loc))
        scaled = ctx.emit(mir.MOp(
            "vbinx", [wide, ctx.const(4, mir.I64, loc)],
            [ctx.vreg(mir.VectorType(64, 2, "int"), hint="wsx", loc=loc)],
            attrs={"op": "mul"}, loc=loc))
        avl2 = ctx.const(self._vl, mir.I32, loc)
        ctx.emit(mir.MOp("vsetvli", [avl2],
                         [ctx.vreg(mir.I32, hint="wvl2", loc=loc)],
                         attrs={"sew": self._sew, "lmul": 1,
                                "policy": "ta,ma"}, loc=loc))
        return scaled

    # -- T012: the conversion matrix -------------------------------------------
    #
    # Every conversion the corpus dtype surface declares, as one table over
    # (src, dst) TIR types.  The routes (each target-legal, each probed or
    # base-V):
    #   * int -> int widen: vwiden (sext/zext by the SOURCE signedness --
    #     the legaliser's vwadd/vwaddu with x0);
    #   * int -> int narrow: the register view retyped to the destination
    #     width (vmovv) and vrgather with the strided lane index (the
    #     low halves of each source lane -- exact truncation);
    #   * int <-> float at equal width: vfcvt.f.x[u].v / vfcvt.rtz.x[u].f.v
    #     (the rtz forms are the pinned fptosi/fptoui truncation);
    #   * int -> float widen: int widen to the float width, then the
    #     same-width form (i16 -> i32 -> f32: exact for the widening half);
    #   * float -> int narrow: f32 -> i16/u16 through vfncvt.rtz (then the
    #     int narrowing for i8/u8);
    #   * fp16 -> fp32: vfwcvt.f.f.v (exact); fp32 -> fp16: vfncvt.f.f.w
    #     (RTNE, the pinned default downcast; rtz selects the rtz form);
    #   * bf16 -> fp32: zext + shift (exact; bf16 is the high half of
    #     fp32); fp32 -> bf16: the transport's own RTNE bit rounding
    #     (bits + 0x7fff + lsb, NaN-quieting) -- bit-identical to the
    #     host staging so both bf16 duality forms read back exactly;
    #   * fp16 <-> bf16: through fp32 (the two step route);
    #   * bool -> X: vsel(1, 0) / vsel(1.0, 0.0) at the destination type;
    #     X -> bool: vcmp ne 0;
    #   * fp64: refused (the corpus dtype surface has no fp64 tensor; the
    #     16 dead dispatch branches fold at specialization).

    def _f16_to_f32(self, ctx: _Ctx, reg: mir.VReg, ty16, loc) -> mir.VReg:
        """A 16-bit float block to fp32 (exact for both fp16 and bf16)."""
        if not ty16.is_float() or ty16.bitwidth() != 16:
            raise self._err(loc, "convert", "not a 16-bit float type")
        if ty16.name == "bf16":
            # (u16 bits) zext -> (bits << 16) as fp32: exact (bf16 IS the
            # high half of fp32)
            fl = max(1, self._vl * 32 // self.target.vlen_bits)
            ubits = self._vmovv(ctx, reg, mir.VectorType(
                16, reg.type.lmul, "uint"), loc)
            self._vregion(ctx, ubits.type, loc)
            wide = ctx.emit(mir.MOp(
                "vwiden", [ubits],
                [ctx.vreg(mir.VectorType(32, reg.type.lmul * 2, "uint"),
                          hint="cvb", loc=loc)],
                attrs={"mode": "zext"}, loc=loc))
            wide = self._vmovv(ctx, wide, mir.VectorType(32, fl, "uint"),
                               loc) if reg.type.lmul * 2 != fl else wide
            self._vregion(ctx, wide.type, loc)
            shifted = ctx.emit(mir.MOp(
                "vbinx", [wide,
                          ctx.const(1 << 16, mir.ScalarType(32), loc)],
                [ctx.vreg(mir.VectorType(32, fl, "uint"),
                          hint="cvs", loc=loc)],
                attrs={"op": "mul"}, loc=loc))
            out = ctx.emit(mir.MOp(
                "vmovv", [shifted],
                [ctx.vreg(mir.VectorType(32, fl, "float"),
                          hint="cvf", loc=loc)], loc=loc))
            self._restore_region(ctx, loc)
            return out
        # fp16: the widening convert at the SOURCE's region (probed),
        # retyped to the lanes-derived fp32 class
        self._vregion(ctx, reg.type, loc)
        wide = ctx.emit(mir.MOp(
            "vfwcvt", [reg],
            [ctx.vreg(mir.VectorType(32, reg.type.lmul * 2, "float"),
                      hint="cvf", loc=loc)],
            attrs={"op": "ff"}, loc=loc))
        fl = max(1, self._vl * 32 // self.target.vlen_bits)
        out = self._vmovv(ctx, wide, mir.VectorType(32, fl, "float"),
                          loc) if reg.type.lmul * 2 != fl else wide
        self._restore_region(ctx, loc)
        return out

    def _f32_to_ff(self, ctx: _Ctx, reg: mir.VReg, dst16, loc,
                   rounding=None) -> mir.VReg:
        """An fp32 block to the 16-bit float type ``dst16`` (one rounding)."""
        if not dst16.is_float() or dst16.bitwidth() != 16:
            raise self._err(loc, "convert", "not a 16-bit float target")
        lmul = reg.type.lmul
        if dst16.name == "bf16":
            # the transport's own RTNE bit rounding: bits + 0x7fff + lsb,
            # NaN inputs quieted (bit 22), then the high half
            bits = self._vmovv(ctx, reg, mir.VectorType(32, lmul, "uint"),
                               loc)
            self._vregion(ctx, bits.type, loc)
            half = self._splat_const(ctx, 0x7fff,
                                     mir.VectorType(32, lmul, "uint"), loc)
            lsb = self._splat_const(ctx, 1,
                                    mir.VectorType(32, lmul, "uint"), loc)
            add = ctx.emit(mir.MOp(
                "vbin", [bits, half],
                [ctx.vreg(bits.type, hint="cva", loc=loc)],
                attrs={"op": "add"}, loc=loc))
            shifted = ctx.emit(mir.MOp(
                "vbin", [bits, lsb],
                [ctx.vreg(bits.type, hint="cvs", loc=loc)],
                attrs={"op": "srl"}, loc=loc))
            rounded = ctx.emit(mir.MOp(
                "vbin", [add, shifted],
                [ctx.vreg(bits.type, hint="cvr", loc=loc)],
                attrs={"op": "add"}, loc=loc))
            # NaN: exponent all ones and a non-zero mantissa
            emask = self._splat_const(ctx, 0x7f800000,
                                      mir.VectorType(32, lmul, "uint"), loc)
            eall = self._splat_const(ctx, 0x7f800000,
                                     mir.VectorType(32, lmul, "uint"), loc)
            mmask = self._splat_const(ctx, 0x007fffff,
                                      mir.VectorType(32, lmul, "uint"), loc)
            zero = self._splat_const(ctx, 0,
                                     mir.VectorType(32, lmul, "uint"), loc)
            exp = ctx.emit(mir.MOp(
                "vbin", [bits, emask],
                [ctx.vreg(bits.type, hint="cve", loc=loc)],
                attrs={"op": "and"}, loc=loc))
            is_exp = ctx.emit(mir.MOp(
                "vcmp", [exp, eall],
                [ctx.vreg(mir.MaskType(), hint="cvn", loc=loc)],
                attrs={"pred": "eq", "fp": False}, loc=loc))
            man = ctx.emit(mir.MOp(
                "vbin", [bits, mmask],
                [ctx.vreg(bits.type, hint="cvm", loc=loc)],
                attrs={"op": "and"}, loc=loc))
            has_man = ctx.emit(mir.MOp(
                "vcmp", [man, zero],
                [ctx.vreg(mir.MaskType(), hint="cvh", loc=loc)],
                attrs={"pred": "ne", "fp": False}, loc=loc))
            is_nan = ctx.emit(mir.MOp(
                "vmand", [is_exp, has_man],
                [ctx.vreg(mir.MaskType(), hint="cvq", loc=loc)], loc=loc))
            qbit = self._splat_const(ctx, 0x00400000,
                                     mir.VectorType(32, lmul, "uint"), loc)
            quieted = ctx.emit(mir.MOp(
                "vbin", [bits, qbit],
                [ctx.vreg(bits.type, hint="cvz", loc=loc)],
                attrs={"op": "or"}, loc=loc))
            v0 = ctx.emit(mir.MOp(
                "vmovmask", [is_nan],
                [ctx.vreg(mir.MaskType(), hint="cv0", loc=loc,
                          fixed_phys="v0")], loc=loc))
            final = ctx.emit(mir.MOp(
                "vsel", [v0, quieted, rounded],
                [ctx.vreg(bits.type, hint="cvw", loc=loc)], loc=loc))
            sixteen = self._splat_const(ctx, 16,
                                        mir.VectorType(32, lmul, "uint"),
                                        loc)
            down = ctx.emit(mir.MOp(
                "vbin", [final, sixteen],
                [ctx.vreg(bits.type, hint="cvd", loc=loc)],
                attrs={"op": "srl"}, loc=loc))
            # the low half: the strided gather at the half-width view,
            # then the float-kind view of the bf16 bits
            low = self._int_narrow(ctx, down, 32, 16, loc)
            dl = max(1, self._vl * 16 // self.target.vlen_bits)
            out = ctx.emit(mir.MOp(
                "vmovv", [low],
                [ctx.vreg(mir.VectorType(16, dl, "float"),
                          hint="cvf", loc=loc)], loc=loc))
            self._restore_region(ctx, loc)
            return out
        # fp16: the narrowing convert at the DESTINATION's region (RTNE
        # default; rtz on request); the destination LMUL covers the pass's
        # lanes at the 16-bit width.  The source is first re-viewed at the
        # DOUBLE-LMUL group (the group the instruction actually reads --
        # a (32,·)-typed source register implies an m2x group whose
        # overlap with vd is an illegal form on this target, probed).
        dl = max(1, self._vl * 16 // self.target.vlen_bits)
        kind = "float" if reg.type.kind == "float" else \
            ("uint" if reg.type.kind == "uint" else "int")
        src2 = self._vmovv(ctx, reg,
                           mir.VectorType(32, dl * 2, kind), loc)
        vtype = mir.VectorType(16, dl, "float")
        self._vregion(ctx, vtype, loc)
        out = ctx.emit(mir.MOp(
            "vfncvt", [src2],
            [ctx.vreg(vtype, hint="cvd", loc=loc)],
            attrs={"op": "ffrtz" if rounding == "rtz" else "ff"}, loc=loc))
        self._restore_region(ctx, loc)
        return out

    def _int_narrow(self, ctx: _Ctx, reg: mir.VReg, sw: int, dw: int,
                    loc) -> mir.VReg:
        """Exact integer narrowing (sw -> dw, sw > dw): the register view
        retyped to the destination width (vmovv at the SOURCE's region --
        every used byte survives) and vrgather with the strided lane
        index: each destination lane takes the low half of its source
        lane."""
        if dw >= sw:
            raise self._err(loc, "convert", "int_narrow requires sw > dw")
        factor = sw // dw
        lmul = max(1, self._vl * dw // self.target.vlen_bits)
        viewed = self._vmovv(ctx, reg, mir.VectorType(dw, lmul, "int"),
                             loc)
        self._vregion(ctx, viewed.type, loc)
        vid = ctx.emit(mir.MOp(
            "vid", [], [ctx.vreg(mir.VectorType(dw, lmul, "int"),
                                 hint="cvi", loc=loc)], loc=loc))
        sty = mir.ScalarType(dw, signed=True)
        kreg = ctx.const(factor, sty, loc)
        fac = ctx.emit(mir.MOp(
            "s2v", [kreg], [ctx.vreg(mir.VectorType(dw, lmul, "int"),
                                     hint="cvk", loc=loc)], loc=loc))
        idx = ctx.emit(mir.MOp(
            "vbin", [vid, fac],
            [ctx.vreg(mir.VectorType(dw, lmul, "int"), hint="cvx",
                      loc=loc)],
            attrs={"op": "mul"}, loc=loc))
        out = ctx.emit(mir.MOp(
            "vrgather", [viewed, idx],
            [ctx.vreg(mir.VectorType(dw, lmul, "int"), hint="cvg",
                      loc=loc)], loc=loc))
        self._restore_region(ctx, loc)
        return out

    def _int_widen(self, ctx: _Ctx, reg: mir.VReg, sw: int, dw: int,
                   signed: bool, loc) -> mir.VReg:
        """Exact integer widening (sw -> dw, a power-of-two factor): the
        vwiden chain at each step's source region (sext for signed
        sources, zext for unsigned -- the pinned extension semantics),
        retyped to the lanes-derived destination class after every step
        (the vwiden's group is double the source's even when the pass's
        lanes only fill part of it)."""
        cur = reg
        w = sw
        while w < dw:
            self._vregion(ctx, cur.type, loc)
            wide = ctx.emit(mir.MOp(
                "vwiden", [cur],
                [ctx.vreg(mir.VectorType(w * 2, cur.type.lmul * 2,
                                         "int" if signed else "uint"),
                          hint="cvw", loc=loc)],
                attrs={"mode": "sext" if signed else "zext"}, loc=loc))
            w *= 2
            want = mir.VectorType(
                w, max(1, self._vl * w // self.target.vlen_bits),
                "int" if signed else "uint")
            cur = self._vmovv(ctx, wide, want, loc) if \
                (want.sew, want.lmul) != (wide.type.sew,
                                          wide.type.lmul) else wide
        self._restore_region(ctx, loc)
        return cur

    def _convert_vector(self, ctx: _Ctx, sreg: mir.VReg, src: tir.Type,
                        dst: tir.Type, loc,
                        rounding=None) -> mir.VReg:
        """The conversion matrix over the corpus dtype surface (vector
        form, at the current pass's vl)."""
        sw, dw = src.bitwidth(), dst.bitwidth()
        # fp64 is outside the executed corpus surface (the 16 dead dtype
        # dispatch branches fold at specialization)
        if (sw == 64 and src.is_float()) or (dw == 64 and dst.is_float()):
            raise self._err(
                loc, "convert",
                f"fp64 conversions are not in the lane (the corpus dtype "
                f"surface has no fp64 tensors): {src!r} -> {dst!r}")
        if src.is_bool():
            # bool -> X: the 0/1 class selected at the destination type.
            # An integer destination WIDER than the pass's SEW keeps the
            # {0,1} class at the data SEW (the class is closed under the
            # pass's arithmetic; the merge/scalar consumers widen it --
            # the exact form for the reduction feeds), exactly the T009
            # contract; narrower destinations take their own width.
            if dst.is_bool():
                return sreg
            v0 = sreg if sreg.is_mask() else self._mask_of_bool(ctx, sreg,
                                                                loc)
            v0 = ctx.emit(mir.MOp(
                "vmovmask", [v0],
                [ctx.vreg(mir.MaskType(), hint="cv0", loc=loc,
                          fixed_phys="v0")], loc=loc))
            if dst.is_int() and dw > self._sew:
                kind = "uint" if dst.is_int_unsigned() else "int"
                vtype = mir.VectorType(self._sew, 1, kind)
                self._vregion(ctx, vtype, loc)
                one = self._splat_const(ctx, 1, vtype, loc)
                zero = self._splat_const(ctx, 0, vtype, loc)
                out = ctx.emit(mir.MOp(
                    "vsel", [v0, one, zero],
                    [ctx.vreg(vtype, hint="cvb", loc=loc)], loc=loc))
                self._restore_region(ctx, loc)
                return out
            if dst.is_float() and dw == 16:
                # the 16-bit float formats differ in their bit layouts:
                # splat at fp32 and convert down (exact for {0, 1})
                v32 = self._vtype(tir.FLOAT32)
                self._vregion(ctx, v32, loc)
                one32 = self._splat_const(ctx, 1.0, v32, loc)
                zero32 = self._splat_const(ctx, 0.0, v32, loc)
                one = self._f32_to_ff(ctx, one32, dst, loc)
                zero = self._f32_to_ff(ctx, zero32, dst, loc)
                v0m = ctx.emit(mir.MOp(
                    "vmovmask", [v0],
                    [ctx.vreg(mir.MaskType(), hint="cv0", loc=loc,
                              fixed_phys="v0")], loc=loc))
                return ctx.emit(mir.MOp(
                    "vsel", [v0m, one, zero],
                    [ctx.vreg(one.type, hint="cvb", loc=loc)], loc=loc))
            vtype = self._vtype(dst)
            self._vregion(ctx, vtype, loc)
            one = self._splat_const(ctx, 1.0 if dst.is_float() else 1,
                                    vtype, loc)
            zero = self._splat_const(ctx, 0.0 if dst.is_float() else 0,
                                     vtype, loc)
            out = ctx.emit(mir.MOp(
                "vsel", [v0, one, zero],
                [ctx.vreg(vtype, hint="cvb", loc=loc)], loc=loc))
            self._restore_region(ctx, loc)
            return out
        if dst.is_bool():
            # X -> bool: != 0 (a mask-typed source IS the bool form)
            if sreg.is_mask():
                self._bind_result(op, sreg)
                return
            vtype = sreg.type
            self._vregion(ctx, vtype, loc)
            zero = self._splat_const(ctx, 0.0 if src.is_float() else 0,
                                     vtype, loc)
            out = ctx.emit(mir.MOp(
                "vcmp", [sreg, zero],
                [ctx.vreg(mir.MaskType(), hint="cvn", loc=loc)],
                attrs={"pred": "ne", "fp": src.is_float()}, loc=loc))
            self._restore_region(ctx, loc)
            return out
        if src.is_int() and dst.is_int():
            if sw == dw:
                # signedness reinterpretation at the same width: the
                # register-view move (bit-identical)
                return self._vmovv(ctx, sreg, self._vtype(dst), loc)
            if sw < dw:
                return self._int_widen(ctx, sreg, sw, dw,
                                       src.is_int_signed(), loc)
            return self._int_narrow(ctx, sreg, sw, dw, loc)
        if src.is_int() and dst.is_float():
            if sw <= dw:
                if sw < dw:
                    wide = self._int_widen(ctx, sreg, sw, dw,
                                           src.is_int_signed(), loc)
                else:
                    wide = sreg
                op = "fcvt" if src.is_int_signed() else "fcvt.fxu"
                self._vregion(ctx, wide.type, loc)
                out = ctx.emit(mir.MOp(
                    "vunary", [wide],
                    [ctx.vreg(self._vtype(dst), hint="cvf", loc=loc)],
                    attrs={"op": op}, loc=loc))
                self._restore_region(ctx, loc)
                return out
            if dw == 16:
                # int -> fp16 through fp32 (the declared fp32-lane
                # policy: the integer converts to fp32, then one final
                # RTNE rounding to fp16; the double rounding stays
                # inside the fp16 tolerance)
                f32 = self._convert_vector(ctx, sreg, src, tir.FLOAT32,
                                           loc)
                return self._f32_to_ff(ctx, f32, dst, loc)
            # sw > dw and dw == 32: i64 -> f32 narrows the integer first
            # (values above 2^31 would wrap) -- refused, never wrong
            raise self._err(
                loc, "convert",
                f"int{sw} -> f{dw} narrows the integer first (values "
                "beyond the narrower width would wrap); the exact route "
                "needs the fp64 staging outside the corpus dtype surface")
        if src.is_float() and dst.is_int():
            if sw == dw:
                op = "fcvt.xf" if dst.is_int_signed() else "fcvt.xuf"
                self._vregion(ctx, sreg.type, loc)
                out = ctx.emit(mir.MOp(
                    "vunary", [sreg],
                    [ctx.vreg(self._vtype(dst), hint="cvi", loc=loc)],
                    attrs={"op": op}, loc=loc))
                self._restore_region(ctx, loc)
                return out
            if sw == 16:
                # f16/bf16 -> i32/u32: widen to f32 (exact), then rtz
                f32 = self._f16_to_f32(ctx, sreg, src, loc)
                op = "fcvt.xf" if dst.is_int_signed() else "fcvt.xuf"
                self._vregion(ctx, f32.type, loc)
                out = ctx.emit(mir.MOp(
                    "vunary", [f32],
                    [ctx.vreg(self._vtype(dst), hint="cvi", loc=loc)],
                    attrs={"op": op}, loc=loc))
                self._restore_region(ctx, loc)
                return out
            if sw == 32 and dw < 32:
                # f32 -> i16/u16: the narrowing rtz convert at the
                # destination's region (the source re-viewed at the
                # double-LMUL group the instruction reads); i8/u8 narrow
                # the integer after
                op = "xf" if dst.is_int_signed() else "xuf"
                dl = max(1, self._vl * 16 // self.target.vlen_bits)
                src2 = self._vmovv(ctx, sreg,
                                   mir.VectorType(32, dl * 2, "float"),
                                   loc)
                vtype = mir.VectorType(16, dl,
                                       "int" if dst.is_int_signed()
                                       else "uint")
                self._vregion(ctx, vtype, loc)
                mid = ctx.emit(mir.MOp(
                    "vfncvt", [src2],
                    [ctx.vreg(vtype, hint="cvi", loc=loc)],
                    attrs={"op": op}, loc=loc))
                if dw == 16:
                    self._restore_region(ctx, loc)
                    return mid
                out = self._int_narrow(ctx, mid, 16, dw, loc)
                return out
            raise self._err(
                loc, "convert",
                f"f{sw} -> i{dw} is not in the conversion matrix")
        # float -> float
        if src.is_float() and dst.is_float():
            if sw == dw:
                # fp16 <-> bf16: through fp32 (the two-step route)
                f32 = self._f16_to_f32(ctx, sreg, src, loc)
                return self._f32_to_ff(ctx, f32, dst, loc,
                                       rounding=rounding)
            if sw == 16 and dw == 32:
                return self._f16_to_f32(ctx, sreg, src, loc)
            if sw == 32 and dw == 16:
                return self._f32_to_ff(ctx, sreg, dst, loc,
                                       rounding=rounding)
            raise self._err(
                loc, "convert",
                f"f{sw} -> f{dw} is not in the conversion matrix")
        raise self._err(loc, "convert",
                        f"no conversion route {src!r} -> {dst!r}")

    def _lower_convert(self, ctx: _Ctx, op: tir.Op, loc) -> None:
        """The full conversion matrix (T012): every corpus dtype pair
        lowers through _convert_vector; scalars ride the splat-convert-
        extract path."""
        src, dst = op.operands[0], op.results[0]
        rounding = op.attrs.get("rounding")
        sreg = self._need(src, loc)
        if sreg.is_vector() and not sreg.is_mask():
            reg = self._convert_vector(ctx, sreg, src.type, dst.type, loc,
                                       rounding=rounding)
            self._bind_result(op, reg)
            return
        if sreg.is_mask() or src.type.is_bool():
            # bool (a mask register): the 0/1 class through the vector
            # path; a block result keeps the vector, a scalar result
            # extracts lane 0
            reg = self._convert_vector(ctx, sreg, src.type, dst.type, loc,
                                       rounding=rounding)
            if op.results[0].rank > 0:
                self._bind_result(op, reg)
            else:
                self._bind_result(op, self._scalarize(ctx, reg, loc))
            return
        if src.type.is_int() and dst.type.is_int():
            # the scalar core's own widen (and the 64->32 narrow; the
            # sub-32 narrowing rides the vector path -- the scalar core
            # has no form there)
            if src.type.bitwidth() < dst.type.bitwidth():
                self._bind_result(op, scalar_mod.widen_to(
                    ctx, sreg, dst.type.bitwidth(), loc))
                return
            if src.type.bitwidth() > dst.type.bitwidth() \
                    and dst.type.bitwidth() >= 32:
                self._bind_result(op, scalar_mod.narrow_to(
                    ctx, sreg, dst.type.bitwidth(), loc))
                return
        # the scalar form: splat, convert, extract
        splat_ty = src.type
        vtype = self._vtype(splat_ty)
        self._open_region(ctx, vtype, loc)
        splat = self._splat_reg(ctx, sreg, vtype, loc)
        cvt = self._convert_vector(ctx, splat, src.type, dst.type, loc,
                                   rounding=rounding)
        self._bind_result(op, self._scalarize(ctx, cvt, loc))

    # -- scalar float arithmetic through the vector path -------------------------
    def _scalar_float_binop(self, ctx: _Ctx, op: tir.Op, lreg: mir.VReg,
                            rreg: mir.VReg, loc) -> mir.VReg:
        vtype = mir.VectorType(32, 1, "float") if (lreg.type.float or
                                                   rreg.type.float) \
            else self._vtype(op.results[0].type)
        # the computation type: both operands at the float width
        width = lreg.type.width if lreg.type.float else rreg.type.width
        vtype = mir.VectorType(width, 1, "float")
        ls = self._splat_reg(ctx, lreg, vtype, loc)
        rs = self._splat_reg(ctx, rreg, vtype, loc)
        vop = {"arith.add": "add", "arith.sub": "sub", "arith.mul": "mul",
               "arith.fdiv": "fdiv"}.get(op.op)
        if vop is None:
            raise self._err(loc, op.op,
                            "scalar floating op is not in the vector path")
        res = ctx.emit(mir.MOp(
            "vbin", [ls, rs], [ctx.vreg(vtype, hint="fb", loc=loc)],
            attrs={"op": vop}, loc=loc))
        return self._scalarize(ctx, res, loc)

    def _scalar_float_cmp(self, ctx: _Ctx, op: tir.Op, lreg: mir.VReg,
                          rreg: mir.VReg, loc) -> mir.VReg:
        """A scalar floating comparison: the result is a MASK (the i1
        scalar's MIR form; branch conditions scalarize it via vpopc, the
        where path consumes it directly)."""
        width = lreg.type.width if lreg.type.float else rreg.type.width
        vtype = mir.VectorType(width, 1, "float")
        ls = self._splat_reg(ctx, lreg, vtype, loc)
        rs = self._splat_reg(ctx, rreg, vtype, loc)
        return ctx.emit(mir.MOp(
            "vcmp", [ls, rs],
            [ctx.vreg(mir.MaskType(), hint="fm", loc=loc)],
            attrs={"pred": op.op.split(".")[1], "fp": True}, loc=loc))

    def _scalar_float_unary(self, ctx: _Ctx, code: str, operand: mir.VReg,
                            loc) -> mir.VReg:
        vtype = mir.VectorType(operand.type.width, 1, "float")
        splat = self._splat_reg(ctx, operand, vtype, loc)
        res = ctx.emit(mir.MOp(
            "vunary", [splat], [ctx.vreg(vtype, hint="fu", loc=loc)],
            attrs={"op": "fneg"}, loc=loc))
        return self._scalarize(ctx, res, loc)

    def _vbin(self, ctx: _Ctx, op: tir.Op, lreg: mir.VReg, rreg: mir.VReg,
              loc) -> mir.VReg:
        code = op.op
        if lreg.is_mask() and rreg.is_mask():
            # boolean block logic: the mask-register forms (the block
            # pointer's per-axis boundary conditions combine with and)
            if code == "bit.and":
                reg = ctx.emit(mir.MOp(
                    "vmand", [lreg, rreg],
                    [ctx.vreg(mir.MaskType(), hint="mand", loc=loc)],
                    loc=loc))
                self._bind_result(op, reg)
                return reg
            raise self._err(loc, code,
                            "boolean block logic beyond and is not in the "
                            "slice (the boundary conditions combine with "
                            "&)")
        if lreg.type != rreg.type:
            raise self._err(loc, code,
                            f"vector operand types differ: {lreg.type!r} vs "
                            f"{rreg.type!r}")
        vop = {"arith.add": "add", "arith.sub": "sub", "arith.mul": "mul",
               "bit.and": "and", "bit.or": "or", "bit.xor": "xor",
               "arith.fdiv": "fdiv", "arith.sdiv": "sdiv",
               "arith.udiv": "udiv", "arith.frem": "frem",
               "arith.srem": "srem", "arith.urem": "urem",
               "bit.lshr": "srl", "bit.ashr": "sra",
               "bit.shl": "sll"}.get(code)
        if vop is None:
            raise self._err(loc, code, "vector binary op is not in the slice")
        if vop in ("sdiv", "udiv", "srem", "urem"):
            # T012: the layout lane's index maps and tl.swizzle2d need
            # division/remainder by compile-time constants (probed under
            # the pinned QEMU: vdiv/vrem/vdivu execute)
            pass
        if vop == "frem":
            raise self._err(loc, code,
                            "vector frem is not in the slice (no target "
                            "form; a located refusal)")
        if vop == "fdiv" and lreg.type.kind != "float":
            raise self._err(loc, code,
                            "fdiv requires floating operands")
        # the declared numeric decision (T012): fp16/bf16 compute lanes run
        # in FP32 with one rounding back at the end (fp32 stays IEEE);
        # bf16 has no native vector arithmetic on this target, and fp16
        # native lanes exist (probed) but the single-rounding policy is
        # the declared default.  The switch is recorded in the artifact
        # identity (options.fp16_bf16_fp32_lanes).
        if lreg.type.kind == "float" and lreg.type.sew == 16:
            ty16 = op.results[0].type if op.results else None
            if ty16 is None or not ty16.is_float() \
                    or ty16.bitwidth() != 16:
                raise self._err(loc, code,
                                "a 16-bit float block without its TIR type "
                                "(the fp32-lane policy needs the fp16/bf16 "
                                "distinction)")
            if ty16.name == "bf16" and \
                    not self.options.fp16_bf16_fp32_lanes:
                # the switch's OFF position documents the boundary:
                # native bf16 vector arithmetic does not exist on this
                # target (the e16 float lanes are fp16); computing bf16
                # bits through them would silently miscompile -- the
                # located refusal names the construct
                raise self._err(
                    loc, code,
                    "bf16 block arithmetic requires the fp32-lane policy "
                    "(fp16_bf16_fp32_lanes=True): native bf16 vector "
                    "arithmetic does not exist on this target and the "
                    "e16 float lanes are fp16 (a located refusal, never "
                    "a silent miscompile)")
            l32 = self._f16_to_f32(ctx, lreg, ty16, loc) \
                if lreg.type.sew == 16 else lreg
            r32 = self._f16_to_f32(ctx, rreg, ty16, loc) \
                if rreg.type.sew == 16 else rreg
            self._vregion(ctx, l32.type, loc)
            res32 = ctx.emit(mir.MOp(
                "vbin", [l32, r32],
                [ctx.vreg(l32.type, hint="vb3", loc=loc)],
                attrs={"op": vop}, loc=loc))
            return self._f32_to_ff(ctx, res32, ty16, loc)
        switched = self._open_region(ctx, lreg.type, loc)
        reg = ctx.emit(mir.MOp(
            "vbin", [lreg, rreg],
            [ctx.vreg(lreg.type, hint="vb", loc=loc)],
            attrs={"op": vop}, loc=loc))
        if switched:
            self._restore_region(ctx, loc)
        return reg

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
        if node.producer is not None \
                and node.producer.op not in ("bitcast", "hint"):
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
        each value's width and shape (modular i32 arithmetic associates).
        Index-class (i64/EMUL-2) accumulators open their own region for
        the vector adds and restore the data region after."""
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
                switched = self._open_region(ctx, acc.type, loc)
                acc = ctx.emit(mir.MOp(
                    "vbinx", [acc, reg],
                    [ctx.vreg(acc.type, hint="os", loc=loc)],
                    attrs={"op": "add"}, loc=loc))
                if switched:
                    self._restore_region(ctx, loc)
            elif acc.is_scalar() and reg.is_vector():
                if acc.type.width > reg.type.sew:
                    raise self._err(
                        loc, "ptradd",
                        f"scalar offset width {acc.type.width} exceeds the "
                        f"vector index SEW {reg.type.sew}")
                switched = self._open_region(ctx, reg.type, loc)
                acc = ctx.emit(mir.MOp(
                    "vbinx", [reg, acc],
                    [ctx.vreg(reg.type, hint="os", loc=loc)],
                    attrs={"op": "add"}, loc=loc))
                if switched:
                    self._restore_region(ctx, loc)
            else:
                if acc.type != reg.type:
                    raise self._err(
                        loc, "ptradd",
                        f"vector offset types differ: {acc.type!r} vs "
                        f"{reg.type!r}")
                switched = self._open_region(ctx, acc.type, loc)
                acc = ctx.emit(mir.MOp(
                    "vbin", [acc, reg],
                    [ctx.vreg(acc.type, hint="os", loc=loc)],
                    attrs={"op": "add"}, loc=loc))
                if switched:
                    self._restore_region(ctx, loc)
        return acc

    def _lower_load(self, ctx: _Ctx, op: tir.Op, loc) -> None:
        ptr = op.operands[0]
        mask = op.operands[1] if len(op.operands) > 1 else None
        other = op.operands[2] if len(op.operands) > 2 else None
        default = op.attrs.get("masked_default")
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
        mreg = self._need(mask, loc) if mask is not None else None
        # the wide-access proof (T011): a proven-contiguous access selects
        # the unit-stride form; an unproven one keeps the indexed form
        # (MECH-MASKED-VECTOR-ACCESS -- the proof never guesses)
        wide = scalar_mod.prove_wide_access(self, ptr, self._vl)
        unit_base = self._unit_stride_base(ctx, wide, base_reg, pointee,
                                           loc) if wide is not None else None
        if unit_base is not None:
            rtype = self._vtype(op.results[0].type)
            self._vregion(ctx, rtype, loc)
            operands = [unit_base]
            attrs = {"sew": rtype.sew}
            if mreg is not None and not self.options.witness_drop_tail_predicates:
                v0 = ctx.emit(mir.MOp(
                    "vmovmask", [mreg],
                    [ctx.vreg(mir.MaskType(), hint="v0", loc=loc,
                              fixed_phys="v0")], loc=loc))
                operands.append(v0)
                attrs["default"] = "undef"
            reg = ctx.emit(mir.MOp(
                "vunit_load", operands,
                [ctx.vreg(rtype, hint="ldu", loc=loc)], attrs=attrs, loc=loc))
            self._wide_selections.append(
                {"op": "load", "source": wide.source,
                 "detail": wide.detail, "loc": str(loc)})
        else:
            scaled, tree = addr_mod.materialize_address(
                ctx, base_reg, offset_reg, pointee, loc, self._vl,
                (self._sew, 1))
            self.trees.append(tree)
            operands = [base_reg, scaled]
            attrs = {"eew": 64, "sew": self._sew}
            if mreg is not None and not self.options.witness_drop_tail_predicates:
                v0 = ctx.emit(mir.MOp(
                    "vmovmask", [mreg],
                    [ctx.vreg(mir.MaskType(), hint="v0", loc=loc,
                              fixed_phys="v0")], loc=loc))
                operands.append(v0)
                attrs["default"] = "undef"
            reg = ctx.emit(mir.MOp(
                "vloadix", operands,
                [ctx.vreg(self._vtype(op.results[0].type), hint="ld",
                          loc=loc)],
                attrs=attrs, loc=loc))
        if other is not None or default == tir.MaskedDefault.VALUE:
            # the declared disabled-position value: the masked load
            # performed no access there (v0.t); the select substitutes the
            # recorded ``other`` operand (never a zero fill)
            oreg = self._need(other, loc)
            if not oreg.is_vector():
                oreg = self._splat_reg(ctx, oreg, reg.type, loc)
            v0 = ctx.emit(mir.MOp(
                "vmovmask", [mreg],
                [ctx.vreg(mir.MaskType(), hint="v0o", loc=loc,
                          fixed_phys="v0")], loc=loc))
            reg = ctx.emit(mir.MOp(
                "vsel", [v0, reg, oreg],
                [ctx.vreg(reg.type, hint="ldo", loc=loc)], loc=loc))
        self._bind_result(op, reg)

    def _unit_stride_base(self, ctx: _Ctx, wide, base_reg: mir.VReg,
                          pointee: tir.Type, loc) -> Optional[mir.VReg]:
        """The scalar byte base of one proven-contiguous access:
        ``base + (elem + scalar terms) * esz`` (the arange's lanes are the
        consecutive elements from there)."""
        esz = pointee.bitwidth() // 8
        elem = self._chunk["elem"]
        acc = ctx.emit(mir.MOp(
            "smove", [elem],
            [ctx.vreg(mir.I64, hint="us0", loc=loc)], loc=loc)) \
            if elem.type.width == 32 else elem
        for term in wide.scalar_terms:
            treg = self._need(term, loc)
            if treg.type.width != 64:
                if treg.type.float:
                    raise self._err(loc, "tl.load/tl.store",
                                    "a floating scalar term cannot feed a "
                                    "proven byte base (the proof declined "
                                    "a non-integer term)")
                treg = ctx.emit(mir.MOp(
                    "smove", [treg],
                    [ctx.vreg(mir.I64, hint="us1", loc=loc)], loc=loc)) \
                    if treg.type.width == 32 else treg
            acc = ctx.emit(mir.MOp(
                "sadd", [acc, treg],
                [ctx.vreg(mir.I64, hint="us2", loc=loc)], loc=loc))
        if esz != 1:
            acc = ctx.emit(mir.MOp(
                "smul", [acc, ctx.const(esz, mir.I64, loc)],
                [ctx.vreg(mir.I64, hint="us3", loc=loc)], loc=loc))
        return ctx.emit(mir.MOp(
            "sadd", [base_reg, acc],
            [ctx.vreg(mir.I64, hint="usb", loc=loc)], loc=loc))

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
        vreg = self._need(value, loc)
        mask_reg = None
        if mask is not None:
            mask_reg = self._need(mask, loc)
        # the wide-access proof (T011): the store side selects the same
        # unit-stride form a proven-contiguous access proves
        wide = scalar_mod.prove_wide_access(self, ptr, self._vl)
        unit_base = self._unit_stride_base(ctx, wide, base_reg, pointee,
                                           loc) if wide is not None else None
        if unit_base is not None:
            stype = vreg.type if vreg.is_vector() else \
                self._vtype(op.operands[1].type)
            self._vregion(ctx, stype, loc)
            operands = [unit_base, vreg]
            attrs = {"sew": stype.sew}
            if mask_reg is not None and not self.options.witness_drop_tail_predicates:
                v0 = ctx.emit(mir.MOp(
                    "vmovmask", [mask_reg],
                    [ctx.vreg(mir.MaskType(), hint="v0", loc=loc,
                              fixed_phys="v0")], loc=loc))
                operands.append(v0)
                attrs["default"] = "no-access"
            ctx.emit0(mir.MOp("vunit_store", operands, [], attrs=attrs,
                              loc=loc))
            self._wide_selections.append(
                {"op": "store", "source": wide.source,
                 "detail": wide.detail, "loc": str(loc)})
            return mask_reg
        scaled, tree = addr_mod.materialize_address(
            ctx, base_reg, offset_reg, pointee, loc, self._vl, (self._sew, 1))
        self.trees.append(tree)
        operands = [base_reg, scaled, vreg]
        attrs = {"eew": 64, "sew": self._sew}
        if mask is not None:
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
        """The register form of one TIR block type at the current pass's
        vl: LMUL covers the pass's lanes at the type's width (the T012
        multi-SEW rule -- for the SEW=32 passes of the single-pass form
        this is exactly the old (SEW, 1) data class / EMUL-2 i64 index
        class)."""
        kind = "float" if ty.is_float() else (
            "uint" if ty.is_int_unsigned() else "int")
        lanes_bits = ty.bitwidth() * self._vl
        lmul = max(1, (lanes_bits + self.target.vlen_bits - 1)
                   // self.target.vlen_bits)
        if lmul not in (1, 2, 4, 8):
            raise self._err(None, "type",
                            f"the {ty!r} value class needs LMUL {lmul} at "
                            f"vl {self._vl} (outside 1..8; a located "
                            "refusal)")
        return mir.VectorType(ty.bitwidth(), lmul, kind)

    def _value_vtype(self, ty: tir.Type) -> mir.VectorType:
        """The register form of one TIR block type at the chunk's vl (the
        _vtype rule; kept as the named entry point the callers use)."""
        return self._vtype(ty)

    def _index_vtype(self, width: int) -> mir.VectorType:
        """The register form of a width-bit INDEX-CLASS block value at the
        chunk's vl (int64 index arithmetic -- pid.to(int64) offsets --
        lives at EMUL 2 so the chunk's lanes fit; A003's declared i64
        index arithmetic)."""
        lanes_bits = width * self._vl
        lmul = (lanes_bits + self.target.vlen_bits - 1) \
            // self.target.vlen_bits
        lmul = max(1, lmul)
        if lmul not in (1, 2, 4, 8):
            raise self._err(None, "index",
                            f"the {width}-bit index class needs LMUL "
                            f"{lmul} at vl {self._vl} (outside 1..8; a "
                            "located refusal)")
        return mir.VectorType(width, lmul, "int")

    def _open_region(self, ctx: _Ctx, vtype: mir.VectorType, loc) -> bool:
        """Open the region one vector op needs (no-op when it is the data
        region); returns whether :meth:`_restore_region` must follow (the
        materialize_address switch/restore pattern, generalized)."""
        if (vtype.sew, vtype.lmul) == (self._sew, 1):
            return False
        avl = ctx.const(self._vl, mir.I32, loc)
        ctx.emit(mir.MOp(
            "vsetvli", [avl], [ctx.vreg(mir.I32, hint="rgo", loc=loc)],
            attrs={"sew": vtype.sew, "lmul": vtype.lmul,
                   "policy": "ta,ma"}, loc=loc))
        return True

    def _restore_region(self, ctx: _Ctx, loc) -> None:
        avl = ctx.const(self._vl, mir.I32, loc)
        ctx.emit(mir.MOp(
            "vsetvli", [avl], [ctx.vreg(mir.I32, hint="rgr", loc=loc)],
            attrs={"sew": self._sew, "lmul": 1, "policy": "ta,ma"},
            loc=loc))


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
    module.meta["wide_selections"] = list(lowering._wide_selections)
    module.meta["witness"] = lowering.options.identity_part()
    module.meta["grid"] = lowering.grid.describe()
    module.meta["stats_mode"] = ("elements" if lowering._count_reg is not None
                                 else "chunks" if lowering._stats_chunk_granular
                                 else "none")
    return module
