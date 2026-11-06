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
refused by the frontend.  Dots inside runtime loops lower through the
matrix region path (T030: the staged carries' back-edge copy repaired;
T014's located refusal removed).
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


def _storage_pointee(pointee: tir.Type) -> tir.Type:
    """The memory-lane view of one pointee type.

    A bool pointee is backed by ONE BYTE per element (the bundle's bool
    views are 1-byte numpy bools, native_io DTYPES['bool']), so its block
    accesses run the i8 lane -- the same proven-safe forms int8 uses --
    with the i1 value materialized as 0/1 bytes (loads test ``!= 0``,
    stores write the mask's 0/1).  Every other pointee is its own
    storage."""
    if pointee.is_bool():
        return tir.INT8
    return pointee


class _Ctx:
    """Emission helper: vreg creation and ordered op append.

    Region tracking (T014): ``switch`` resets the block's region knowledge
    (regions do not cross block boundaries -- the MIR invariant); the
    first vector op emitted into a regionless block opens the *pass's*
    data region right there, so every block's implicit region is the one
    that was active when the block's first vector op was emitted -- never
    the final pass's region applied after the fact (a prefix scalar's
    splat at e32 must not land in an e16 region because the kernel also
    has an fp16 pass).
    """

    def __init__(self, module: mir.MModule, function: mir.MFunction):
        self.module = module
        self.function = function
        self.blocks: Dict[str, mir.Block] = {}
        self.cur: Optional[mir.Block] = None
        self._hint_counts: Dict[str, int] = {}
        self._region_known: set = set()
        #: the ACTIVE (sew, lmul, vl) at the current emission position
        #: (None at a block's start -- the MIR invariant: no region crosses
        #: blocks).  Every emitted vsetvli updates it (through
        #: _note_region; the vl is None when the emitter did not record
        #: its avl constant).  The region helpers use it to skip a
        #: redundant switch -- exactly, never assumed -- and never mistake
        #: a helper's leftover region (an e64m2 address form) for the
        #: pass's data region (T028: resolve_conj's fneg at e16 ran in a
        #: stale e64m2 -- _open_region's old "is the data region" no-op
        #: test was unsound against leftovers)
        self.active_region: Optional[Tuple[int, int, Optional[int]]] = None
        #: the region provider: () -> (sew, lmul, vl) of the current pass
        self.default_region = None

    def add_block(self, name: str, params=(), loc=None) -> mir.Block:
        block = mir.Block(name, list(params), loc)
        self.function.blocks.append(block)
        self.blocks[name] = block
        return block

    def switch(self, block: mir.Block) -> None:
        self.cur = block
        self._region_known.discard(id(block))
        self.active_region = None

    def _note_region(self, op: mir.MOp) -> None:
        if op.opcode == "vsetvli":
            if self.cur is not None:
                self._region_known.add(id(self.cur))
            self.active_region = (op.attrs["sew"], op.attrs["lmul"], None)
        elif op.opcode in mir.VEC_OPS and self.cur is not None \
                and id(self.cur) not in self._region_known:
            # the block's first vector op: open the pass's data region
            # before it (the implicit-region contract; ops that manage
            # their own regions emit a vsetvli first and mark the block)
            if self.default_region is not None:
                sew, lmul, vl = self.default_region()
                avl = mir.MOp("sconst", [],
                              [self.vreg(mir.I32, hint="bvl", loc=op.loc)],
                              attrs={"value": int(vl)}, loc=op.loc)
                self.cur.ops.append(avl)
                self.cur.ops.append(mir.MOp(
                    "vsetvli", [avl.results[0]],
                    [self.vreg(mir.I32, hint="brg", loc=op.loc)],
                    attrs={"sew": sew, "lmul": lmul,
                           "policy": "ta,ma"}, loc=op.loc))
                self.active_region = (sew, lmul, vl)
            self._region_known.add(id(self.cur))

    def vreg(self, mtype, hint: str = "t", loc=None,
             fixed_phys: Optional[str] = None) -> mir.VReg:
        n = self._hint_counts.get(hint, 0) + 1
        self._hint_counts[hint] = n
        return mir.VReg(mtype, name=f"{hint}{n}", fixed_phys=fixed_phys,
                        loc=loc)

    def emit(self, op: mir.MOp) -> mir.VReg:
        self._note_region(op)
        self.cur.ops.append(op)
        assert len(op.results) == 1, op.opcode
        return op.results[0]

    def emit0(self, op: mir.MOp) -> None:
        self._note_region(op)
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


#: TIR dtype names -> the tiles planner's operand names (T014)
_TILES_DTYPE_NAME = {"i8": "int8", "u8": "uint8", "fp16": "float16",
                     "bf16": "bfloat16", "fp32": "float32",
                     "i32": "int32"}


class _MatrixIface:
    """The emission interface the composed dot emitters consume (T014):
    the vectorize lowering's context, the private workspace base, region
    control, the scalar loop forms and the 16-bit float conversions --
    the services the IME slice's own ``_Ctx`` provides, against the
    composed program's address space."""

    def __init__(self, sl: "SliceLowering", ctx: _Ctx, loc=None):
        self.sl = sl
        self.ctx = ctx
        self.loc = loc

    def vreg(self, mtype, hint: str = "t", loc=None,
             fixed_phys=None):
        return self.ctx.vreg(mtype, hint=hint, loc=loc,
                             fixed_phys=fixed_phys)

    def emit(self, op: mir.MOp) -> mir.VReg:
        return self.ctx.emit(op)

    def emit0(self, op: mir.MOp) -> None:
        self.ctx.emit0(op)

    def const(self, bits: int, mtype, loc):
        return self.ctx.const(bits, mtype, loc)

    def region(self, sew: int, lmul: int, vl: int, loc) -> None:
        avl = self.ctx.const(vl, mir.I32, loc)
        self.ctx.emit0(mir.MOp(
            "vsetvli", [avl],
            [self.ctx.vreg(mir.I32, hint="mgr", loc=loc)],
            attrs={"sew": sew, "lmul": lmul, "policy": "ta,ma"}, loc=loc))

    def ws(self, loc) -> mir.VReg:
        return self.sl._workspace_private_reg(self.ctx, loc)

    def loop(self, lower, upper, inits, loc, tag):
        return scalar_mod.begin_counted_loop(self.ctx, lower, upper, inits,
                                             loc, tag)

    def close(self, frame, back, loc) -> None:
        scalar_mod.close_loop(self.ctx, frame, back)
        self.ctx.switch(frame.exit)

    def tag(self, hint: str) -> str:
        return self.sl._tag(hint)

    def widen_f16(self, reg: mir.VReg, ty16) -> mir.VReg:
        return self.sl._f16_to_f32(self.ctx, reg, ty16, self.loc)

    def narrow_f32(self, reg: mir.VReg, ty16) -> mir.VReg:
        return self.sl._f32_to_ff(self.ctx, reg, ty16, self.loc)


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
        #: T028: a pass split fired at a partial consumer (the two-phase
        #: worker split cannot host mid-region merged-value consumers)
        self._pass_split_at_partial = False
        #: T028: the open restructured regions (the nested segmentations'
        #: liveout tables key on the region statement)
        self._region_stack: list = []
        #: T028: the restructured regions' nested cross-pass liveouts
        #: (region id -> pass index -> [(vid, slot)])
        self._nested_liveouts: Dict[int, Dict[int, list]] = {}
        # -- T014: the matrix-breadth lane ---------------------------------
        #: open matrix-region loop frames: the staged carries (name -> the
        #: record + the body-end value) and the pointer recurrences
        self._matrix_frames: List[dict] = []
        #: the active uniform pointer recurrences, one layer per loop
        #: frame (carried vid -> the frame's scalar offset param); the
        #: address resolution adds every active layer's offset for each
        #: mapped vid its chain passes (nested loops over one pointer
        #: accumulate both steps)
        self._ptr_recurrences: List[Dict[int, mir.VReg]] = []
        #: matrix segments emitted (IR-OBSERVABILITY: the countable
        #: record carrying the plan each dot lowered under)
        self._matrix_segments: List[dict] = []
        #: matrix-region nesting depth (staging stores are legal at a
        #: matrix region's own top level: the per-iteration redefinition
        #: IS the semantics of a staged loop carry)
        self._matrix_depth: int = 0
        #: the dots' breadth plans (result vid -> plan; T014)
        self._dot_plans: Dict[int, object] = {}
        #: the IME segments' transient staging area offset (None when no
        #: IME dot exists)
        self._matrix_stage_off: Optional[int] = None
        #: the narrow-data fallback's workspace scratch offset (the
        #: per-lane scalar loop's lane staging; None when no sub-32-bit
        #: unproven load/store exists)
        self._narrow_ws_offset: Optional[int] = None

    # -- helpers ---------------------------------------------------------------
    def _err(self, loc, construct: str, message: str):
        return VectorizeError(loc, construct, message)

    def value(self, t: tir.Value) -> Optional[mir.VReg]:
        for layer in reversed(self._overrides):
            if t.vid in layer:
                return layer[t.vid]
        return self.values.get(t.vid)

    def _need(self, t: tir.Value, loc, consumer_shape=None) -> mir.VReg:
        # a lazy view base re-materializes at every use (multi-view kernels
        # whose base registers would crowd the GPR file -- the target's own
        # register budget decided at entry binding)
        view_index = getattr(self, "_lazy_view_index", {}).get(t.vid)
        if view_index is not None:
            return ctx_emit_view_load(self, loc, view_index)
        reg = self.value(t)
        if reg is None and self._recurrence_of(t) is not None:
            # a carried pointer block has no register by design (the
            # uniform-recurrence repair); only the address resolution
            # may consume it
            raise self._err(
                loc, t.name,
                f"the loop-carried pointer '{t.name}' is consumed by a "
                "non-address form (its value exists only as the address "
                "recurrence the loads resolve; a pointer comparison or "
                "arithmetic on the carried block is not in this lane)")
        if reg is None:
            rec = getattr(self, "_staged", {}).get(t.vid)
            if rec is not None:
                # a staged value: materialize its lanes from the private
                # workspace at the current pass's chunk position
                # (lane-aligned: the consumer pass's extent equals the
                # value's extent -- the verifier's lane-alignment rules;
                # T029: a consumer that BROADCASTS the block's extent-1
                # axes maps the flat position through the block's own
                # axes instead)
                return self._load_staged(t, rec, loc,
                                         consumer_shape=consumer_shape)
            prod = t.producer
            if prod is not None and prod.op == "const":
                # a constant whose register was bound in an earlier pass:
                # constants are pure -- re-emit at the current position
                # (registers do not survive a pass loop).  The re-emitted
                # register joins _pass_bound when a chunk is open: a
                # re-emission inside a pass body must drop at the pass
                # close too (T028: the CSE-merged loop-bound const bound
                # in an earlier chunk body survived into a later
                # restructured region's head -- use-before-definition)
                creg = scalar_mod.lower_const(self._ctx,
                                              prod.attrs["value"],
                                              t.type, loc)
                self.values[t.vid] = creg
                if self._chunk is not None:
                    self._pass_bound.add(t.vid)
                if self._names is not None:
                    for key in t.scope_names():
                        self._names.define(key, t)
                return creg
            if prod is not None and t.rank == 0 \
                    and all(getattr(o, "rank", 0) == 0
                            for o in prod.operands) \
                    and (prod.op in tir.BIN_ARITH
                         or prod.op in tir.BIN_BITWISE
                         or prod.op in tir.CMP_PREDS
                         or prod.op in tir.MAXMIN_OPS):
                # T030: a PURE scalar tree re-materializes at the current
                # position -- a value bound inside an earlier pass's
                # chunk body does not survive the pass loop (the strength
                # reduced pid*BLOCK term of one pass's addresses, reused
                # by a later pass's store: the register did not dominate
                # and the verifier rejected it)
                creg = self._materialize_scalar_tree(self._ctx, t, loc)
                self.values[t.vid] = creg
                if self._chunk is not None:
                    self._pass_bound.add(t.vid)
                if self._names is not None:
                    for key in t.scope_names():
                        self._names.define(key, t)
                return creg
            raise self._err(loc, t.name,
                            f"TIR value '{t.name}' is not lowered before its "
                            "use (use-before-definition in the lowering)")
        return reg

    def _staged_lane_index(self, ctx: _Ctx, t: tir.Value, consumer_shape,
                           loc) -> mir.VReg:
        """The staged-region lane index at the current chunk position.

        The lane-aligned form (the consumer's flat extent equals the
        block's) is ``elem + lane``.  When the consumer's shape
        BROADCASTS the block's extent-1 axes (the ptradd offsets
        ``(N, 1)`` and ``(1, M)`` feeding an ``(N, M)`` addressing
        space), the flat chunk position decomposes over the consumer's
        axes and re-composes over the block's own: an extent-1 axis
        contributes its single element regardless of the consumer's
        position along it.  T029: the unmapped flat read crossed into
        the neighbouring staged regions, the materialized offsets were
        garbage and the indexed access went out of bounds."""
        vl = self._vl
        ity = self._idx_vtype(vl)
        self._vregion(ctx, ity, loc)
        vid = ctx.emit(mir.MOp(
            "vid", [], [ctx.vreg(ity, hint="svid", loc=loc)], loc=loc))
        idx = ctx.emit(mir.MOp(
            "vbinx", [vid, self._chunk["elem"]],
            [ctx.vreg(ity, hint="sidx", loc=loc)],
            attrs={"op": "add"}, loc=loc))
        if consumer_shape is None:
            return idx
        cext = [e.value for e in consumer_shape]
        bext = [e.value for e in t.shape]
        cflat = 1
        for e in cext:
            cflat *= int(e)
        bflat = 1
        for e in bext:
            bflat *= int(e)
        if cflat == bflat:
            return idx                     # lane-aligned (the standard rule)
        if len(cext) != len(bext):
            # T032: a lower-rank staged block in a higher-rank addressing
            # space is the standard leading-axis broadcast (argmin_tiled's
            # ``offs_n * stride`` rank-1 offset in the (M, N) tile form):
            # pad the block's leading extent-1 axes and let the per-axis
            # map below decide (an axis the block does not cover is a
            # broadcast axis; anything else refuses located)
            if len(cext) > len(bext):
                bext = [1] * (len(cext) - len(bext)) + list(bext)
            else:
                raise self._err(
                    loc, "layout",
                    f"the staged block '{t.name}' (rank {len(bext)}) is "
                    f"consumed at rank {len(cext)} with a different flat "
                    f"extent ({cflat} vs {bflat}); no axis map is derivable "
                    "(a located refusal, never a wrong region read)")
        n = len(cext)
        # the block-axis -> consumer-axis assignment.  Positional first
        # (the broadcast semantics the value's own TIR ops declared);
        # T033 adds the unique-matching fallback for the reshape-padded
        # forms -- a rank-1 (8,) offset the case layer reshaped to (8,1)
        # inside an (8,32) addressing space pads to (1,8), whose 8-aligns
        # with the consumer's AXIS 0, not axis 1 (tiled_argmin's staged
        # r_offs).  A non-1 block axis pairs with a distinct equal-extent
        # consumer axis; exactly one such pairing is determined (never a
        # guess), none or several refuses located.
        assign: Optional[Dict[int, int]] = {}
        for b_ax in range(n):
            if int(bext[b_ax]) <= 1:
                continue
            if int(bext[b_ax]) != int(cext[b_ax]):
                assign = None
                break
            assign[b_ax] = b_ax
        if assign is None:
            solutions: List[Dict[int, int]] = []

            def _match(b_ax: int, used, cur):
                if b_ax == n:
                    solutions.append(dict(cur))
                    return
                if int(bext[b_ax]) <= 1:
                    _match(b_ax + 1, used, cur)
                    return
                for c_ax in range(n):
                    if c_ax in used \
                            or int(cext[c_ax]) != int(bext[b_ax]):
                        continue
                    cur[b_ax] = c_ax
                    _match(b_ax + 1, used | {c_ax}, cur)
                    del cur[b_ax]

            _match(0, frozenset(), {})
            if len(solutions) == 1:
                assign = solutions[0]
        if assign is None:
            raise self._err(
                loc, "layout",
                f"the staged block '{t.name}' (axes {bext}) does not "
                f"align with its consumer's axes {cext} (no unique "
                "broadcast axis map is derivable; a located refusal)")
        cstrides = [1] * n
        for ax in range(n - 2, -1, -1):
            cstrides[ax] = cstrides[ax + 1] * int(cext[ax + 1])
        bstrides = [1] * n
        for ax in range(n - 2, -1, -1):
            bstrides[ax] = bstrides[ax + 1] * int(bext[ax + 1])

        def _splat(value: int, hint: str) -> mir.VReg:
            c = ctx.const(int(value), mir.I32, loc)
            return ctx.emit(mir.MOp(
                "s2v", [c], [ctx.vreg(ity, hint=hint, loc=loc)], loc=loc))

        acc: Optional[mir.VReg] = None
        for b_ax in range(n):
            if int(bext[b_ax]) <= 1:
                continue           # a broadcast axis contributes nothing
            c_ax = assign[b_ax]
            comp = idx
            if cstrides[c_ax] > 1:
                comp = ctx.emit(mir.MOp(
                    "vbin", [comp, _splat(cstrides[c_ax], "sms")],
                    [ctx.vreg(ity, hint="smd", loc=loc)],
                    attrs={"op": "sdiv"}, loc=loc))
            if c_ax > 0:
                comp = ctx.emit(mir.MOp(
                    "vbin", [comp, _splat(cext[c_ax], "smr")],
                    [ctx.vreg(ity, hint="smm", loc=loc)],
                    attrs={"op": "srem"}, loc=loc))
            if bstrides[b_ax] > 1:
                comp = ctx.emit(mir.MOp(
                    "vbin", [comp, _splat(bstrides[b_ax], "smb")],
                    [ctx.vreg(ity, hint="smu", loc=loc)],
                    attrs={"op": "mul"}, loc=loc))
            if acc is None:
                acc = comp
            else:
                acc = ctx.emit(mir.MOp(
                    "vbin", [acc, comp],
                    [ctx.vreg(ity, hint="sma", loc=loc)],
                    attrs={"op": "add"}, loc=loc))
        if acc is None:
            # every axis broadcast: the single staged element serves all
            # lanes
            acc = _splat(0, "smz")
        return acc

    def _load_staged(self, t: tir.Value, rec: dict, loc,
                     consumer_shape=None) -> mir.VReg:
        """Materialize one staged value's lanes at the current position:
        ``ws[offset + (elem + lane) * esz]`` through the indexed load
        (the standard convention) or the unit-stride load at the scalar
        chunk address (the matrix lane's native sub-32 records -- the
        narrow indexed forms crash the pinned QEMU)."""
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
        if rec.get("native"):
            lmul = max(1, vl * lane_sew // self.target.vlen_bits)
            vtype = mir.VectorType(lane_sew, lmul, kind)
            self._vregion(ctx, vtype, loc, vl=vl)
            ws = self._workspace_private_reg(ctx, loc)
            base = ctx.emit(mir.MOp(
                "sadd", [ws, ctx.const(rec["offset"], mir.I64, loc)],
                [ctx.vreg(mir.I64, hint="nlb", loc=loc)], loc=loc))
            elem64 = scalar_mod.widen_to(ctx, self._chunk["elem"], 64, loc)
            byteoff = ctx.emit(mir.MOp(
                "smul", [elem64, ctx.const(rec["esz"], mir.I64, loc)],
                [ctx.vreg(mir.I64, hint="nlo", loc=loc)], loc=loc))
            addr = ctx.emit(mir.MOp(
                "sadd", [base, byteoff],
                [ctx.vreg(mir.I64, hint="nla", loc=loc)], loc=loc))
            opcode = "vuload8" if lane_sew == 8 else "vuload16"
            reg = ctx.emit(mir.MOp(
                opcode, [addr],
                [ctx.vreg(vtype, hint="nld", loc=loc)], loc=loc))
            self._restore_region(ctx, loc)
            self.values[t.vid] = reg
            if self._names is not None:
                for key in t.scope_names():
                    self._names.define(key, t)
            return reg
        sew_v = lane_sew
        lmul = max(1, vl * sew_v // self.target.vlen_bits)
        idx = self._staged_lane_index(ctx, t, consumer_shape, loc)
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
        if self._region_depth > 0 and \
                not (self._matrix_depth > 0
                     and self._region_depth == self._matrix_depth):
            raise self._err(
                loc, "layout",
                f"a block value ('{t.name}') defined inside a runtime "
                "region cannot cross a pass boundary (the layout lane "
                "stages top-level values only; a matrix region's own "
                "top level stages per iteration -- the staged loop carry "
                "semantics)")
        if self._chunk is None:
            raise self._err(
                loc, "layout",
                f"a staged value ('{t.name}') is produced outside any "
                "pass (the segmentation and the emission disagree)")
        ctx = self._ctx
        rec = self._staged[t.vid]
        vl = self._vl
        if rec.get("native"):
            # T014: a native record stores through the unit-stride form
            # at a scalar address (the narrow indexed forms crash the
            # pinned QEMU -- the probed e8/e16 + e64m2 constraint).  The
            # analysis only flags sub-32 records native; 32-bit records
            # keep the standard (identical) convention.
            kind = "float" if rec["type"].is_float() else \
                ("uint" if rec["type"].is_int_unsigned() else "int")
            vtype = mir.VectorType(rec["lane_sew"], 1, kind)
            self._vregion(ctx, vtype, loc, vl=vl)
            ws = self._workspace_private_reg(ctx, loc)
            base = ctx.emit(mir.MOp(
                "sadd", [ws, ctx.const(rec["offset"], mir.I64, loc)],
                [ctx.vreg(mir.I64, hint="nsb", loc=loc)], loc=loc))
            elem64 = scalar_mod.widen_to(ctx, self._chunk["elem"], 64, loc)
            byteoff = ctx.emit(mir.MOp(
                "smul", [elem64, ctx.const(rec["esz"], mir.I64, loc)],
                [ctx.vreg(mir.I64, hint="nso", loc=loc)], loc=loc))
            addr = ctx.emit(mir.MOp(
                "sadd", [base, byteoff],
                [ctx.vreg(mir.I64, hint="nsa", loc=loc)], loc=loc))
            opcode = "vustore8" if rec["lane_sew"] == 8 else "vustore16"
            ctx.emit0(mir.MOp(opcode, [addr, reg], [], loc=loc))
            self._restore_region(ctx, loc)
            return
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
        # T028: a pass split at a partial consumer means a statement between
        # the region's passes reads a MERGED reduction value -- the
        # worker-strided two-phase split cannot host that (each worker's
        # phase-1 would read its own partial); the reduction rides the
        # normal per-program path instead
        if self._pass_split_at_partial and self.stage_plan is not None \
                and self.stage_plan.eligible:
            self.stage_plan.eligible = False
            self.stage_plan.reason = (
                "a statement between the region's passes consumes a merged "
                "reduction value (the worker-strided two-phase split cannot "
                "host mid-region merged-value consumers; the reduction "
                "rides the normal per-program path)")

        # per-pass parameters (extent, SEW, vl, chunk count); the legacy
        # defaults come from the first arange (single-pass kernels keep
        # exactly today's shape)
        self._pass_params: List[Optional[dict]] = \
            self._compute_pass_params(self._segments)
        has_passes = any(p is not None for p in self._pass_params)
        # the arange is the LEGACY single-pass reference: it is required only
        # when no pass segment exists and the body still has block-level
        # statements (their legacy chunk needs a region and an extent).  A
        # scalar-only kernel (no block statement at all: bn_inc's atomic
        # counter, final_mean's scalar loads) has neither and lowers without
        # one; block-extent kernels without an arange (blocks built from
        # tl.full/loop carries) take the first PASS's parameters.
        body_has_blocks = any(self._stmt_is_block(st)
                              for st in fn.body.statements)
        arange_extent, arange_op = (0, None)
        if not has_passes and (body_has_blocks or self._scan_accs):
            arange_extent, arange_op = self._find_arange(fn.body)
        else:
            arange_extent, arange_op = self._find_arange_optional(fn.body)
        max_extent = arange_extent
        for seg in self._segments:
            if seg[0] == "pass":
                max_extent = max(max_extent, seg[2])
        # the default region (the prefix scalars' index class and the
        # single-pass form): the FIRST PASS's -- never a leading scalar
        # segment's None (the reduce_kernel fp16 form: the leading index
        # statements are pass-agnostic scalars, the pass is e16, and the
        # bogus e32 default opened the first vector op in the wrong region);
        # else the arange's; else the void default (scalar-only kernels)
        first = next((p for p in self._pass_params if p is not None), None)
        if first is None:
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
        # T014: the IME dot segments' transient staging area -- the dense
        # A tile (128B), the B tile (128B) and the C accumulator staging
        # (256B); ONE area serves every IME dot (the segments run
        # sequentially within one program instance)
        if any(getattr(p, "path", None) == "ime"
               for p in self._dot_plans.values()):
            self._matrix_stage_off = private_bytes
            private_bytes += 512
        # T014: the narrow-data fallback's scratch -- one chunk of vl
        # lanes at up to 4 bytes (the per-lane scalar loop's carrier)
        if any(isinstance(op, tir.Op) and op.op in ("load", "store")
               and op.operands[0].type.pointee.bitwidth() < 32
               for op in self._walk_ops(fn.body)):
            self._narrow_ws_offset = private_bytes
            private_bytes += 32 * 4 + 8
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
            # every value the region defines, nested regions included: a
            # loop's join (a scalar a suffix consumes) is chunk-invariant
            # live-out state exactly like a top-level op result (T026: the
            # while-loop join `status` reaching the trailing store)
            region_defined = self._pass_defined_vids(region)
            partial_vids = {p.value_id for p in
                            (self.stage_plan.partials
                             if self.stage_plan else [])}
            partial_vids.update(p.pair_value_id for p in
                                (self.stage_plan.partials
                                 if self.stage_plan else [])
                                if p.pair_value_id is not None)
            partial_vids.update(f["vid"] for f in self._scan_accs)
            prefix_defined = self._pass_defined_vids(self._body_split[0])

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
        # the values whose exit binding is a MERGE, never a per-chunk
        # liveout spill: a rank-0 plan partial binds its merged value at
        # the pass exit (the chunk accumulator's back edge); a liveout
        # reload would clobber that binding with the LAST chunk's partial
        # (the same exclusion the region-level liveout table applies)
        merge_bound_vids = {p.value_id for p in
                            (self.stage_plan.partials
                             if self.stage_plan else [])}
        merge_bound_vids.update(
            p.pair_value_id for p in (self.stage_plan.partials
                                      if self.stage_plan else [])
            if p.pair_value_id is not None)
        merge_bound_vids.update(f["vid"] for f in self._scan_accs)
        seg_index = 0
        for si, seg in enumerate(self._segments):
            if seg[0] != "pass":
                continue
            defined = self._pass_defined_vids(seg[1])
            later_uses: set = set()
            for later in self._segments[si + 1:]:
                # T030: a SCALAR segment's statements consume values too
                # (the rng lane's converts of a pass-1 scalar load) --
                # skipping them left the cross-pass scalar without its
                # liveout slot, and the register (bound inside the closed
                # chunk body) did not dominate the use
                if later[0] in ("layout", "matrix", "preduce"):
                    later_uses.update(v.vid for v in
                                      self._region_uses(later[1])
                                      if v.rank == 0)
                elif later[0] == "scalar":
                    for st in later[1]:
                        later_uses.update(v.vid
                                          for v in self._region_uses(st)
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
                    if vid in merge_bound_vids:
                        continue    # the merged value binds at the exit
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
        # T028: the SAME contract for the restructured regions' nested
        # segmentations (a scalar defined in one body pass's chunk loop
        # and consumed by a later body segment cannot keep its register
        # across the pass close).  The slot pool extends the workspace;
        # the walk mirrors _lower_matrix_region's segmentation (the carry
        # hoist only MOVES trailing scalar defs out of passes, so the
        # un-hoisted walk over-allocates at worst -- a slot whose value
        # never binds is never stored or reloaded).
        self._nested_liveouts: Dict[int, Dict[int, list]] = {}

        def nested_liveout_walk(segments: list, into: dict) -> None:
            for si, seg in enumerate(segments):
                if seg[0] != "pass":
                    continue
                defined = self._pass_defined_vids(seg[1])
                later_uses: set = set()
                for later in segments[si + 1:]:
                    # T030: scalar segments consume values too (the same
                    # fix as the top-level walk above)
                    if later[0] in ("layout", "matrix", "preduce"):
                        later_uses.update(v.vid for v in
                                          self._region_uses(later[1])
                                          if v.rank == 0)
                    else:
                        for st in later[1]:
                            later_uses.update(v.vid
                                              for v in self._region_uses(st)
                                              if v.rank == 0)
                cross = set()
                for vid in defined:
                    if vid in later_uses and vid not in self._staged:
                        if vid in merge_bound_vids:
                            continue    # the merged value binds at the exit
                        v = self._value_by_vid(vid)
                        if v.producer is not None \
                                and v.producer.op == "const":
                            continue
                        cross.add(vid)
                if cross:
                    into[si] = [(vid, private_bytes + 8 * k)
                                for k, vid in enumerate(sorted(cross))]

        def walk_regions(stmts) -> None:
            nonlocal private_bytes
            for st in stmts:
                if not isinstance(st, (tir.Loop, tir.If)):
                    continue
                if not (self._is_matrix_region(st)
                        or self._is_mixed_extent_region(st)):
                    walk_regions(self._region_body_statements(st))
                    continue
                body = list(st.body.statements) if isinstance(st, tir.Loop) \
                    else list(st.then.statements) + list(st.els.statements)
                segs = self._segment_region(body)
                if isinstance(st, tir.Loop):
                    # mirror _lower_matrix_region's carry hoist exactly (a
                    # split pass shifts the later segment indices)
                    end_names = self._tir_end_names(body)
                    carry_ids = set()
                    head_v = end_names.get(st.carried[0][0])
                    if head_v is not None and head_v.producer is not None:
                        carry_ids.add(id(head_v.producer))
                    for entry in self._classify_carried(st):
                        if entry[0] == "scalar":
                            v = end_names.get(entry[1])
                            if v is not None and v.producer is not None:
                                carry_ids.add(id(v.producer))
                    if carry_ids:
                        segs = self._hoist_carry_stmts(segs, carry_ids)
                liveouts: Dict[int, list] = {}
                nested_liveout_walk(segs, liveouts)
                if liveouts:
                    self._nested_liveouts[id(st)] = liveouts
                    n = sum(len(v) for v in liveouts.values())
                    private_bytes += 8 * n
                # recurse into the body's own restructured regions
                for seg in segs:
                    if seg[0] == "matrix":
                        walk_regions([seg[1]])
                    elif seg[0] == "pass":
                        walk_regions(seg[1])

        walk_regions(region)
        self.plan.workspace_private = private_bytes

        module = mir.MModule(self.tir_module.name, self.tir_module.source_path)
        launch = mir.VReg(mir.I64, name="launch")
        function = mir.MFunction("operator_entry", [launch], fn.loc)
        module.functions.append(function)
        ctx = _Ctx(module, function)
        self._ctx = ctx
        # the implicit-region provider: the pass parameters active when a
        # block's first vector op is emitted (T014's per-block region fix)
        ctx.default_region = lambda: (self._sew, 1, self._vl)
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

        T028: the mid-region partial guard moved into the segmentation
        (``_segment_region`` splits the pass at the first statement that
        consumes a partial the pass itself defines -- the merged value
        binds at that pass's exit, so the consumer lowers between passes
        or in the next pass, never per-chunk on the partial)."""
        idx = [i for i, st in enumerate(statements) if self._stmt_is_block(st)]
        if not idx:
            return list(statements), [], []
        first, last = idx[0], idx[-1]
        prefix = list(statements[:first])
        region = list(statements[first:last + 1])
        suffix = list(statements[last + 1:])
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
                    "tir_type": op.results[0].type,
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

    def _find_arange_optional(self, body: tir.Block) -> Tuple[int, None]:
        """The first arange's extent when one exists, else 0 -- never a
        refusal (the caller decided the arange is not required: block
        extents come from the pass segments, or the kernel is scalar-only)."""
        for op in self._walk_ops(body):
            if op.op == "arange":
                return op.attrs["end"] - op.attrs["start"], None
        return 0, None

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

    # -- T028: the partial-axis reduction lane --------------------------------

    def _is_partial_reduce(self, st) -> bool:
        """A top-level reduce op whose axes do not cover the operand's
        every axis: the result is a block of another shape -- the staging
        lane owns it (the operand stages to the workspace; a dedicated
        loop materializes the reduced result block)."""
        return isinstance(st, tir.Op) and st.op == "reduce" \
            and st.operands[0].rank > 0 \
            and len(st.attrs["axes"]) != st.operands[0].rank

    # -- T014: the matrix-breadth lane --------------------------------------

    def _contains_dot(self, st) -> bool:
        """Does the statement transitively contain a ``linalg.dot`` op?"""
        if isinstance(st, tir.Op):
            return st.op == "linalg.dot"
        if isinstance(st, tir.If):
            return any(self._contains_dot(s)
                       for s in list(st.then.statements)
                       + list(st.els.statements))
        if isinstance(st, tir.Loop):
            return any(self._contains_dot(s) for s in st.body.statements)
        return False

    def _is_matrix_region(self, st) -> bool:
        """A runtime region (loop or if) hosting a dot: the region is
        restructured -- the MIR loop runs at the segment level and the
        body's statements lower through their own passes and matrix
        segments (the chunk loop cannot wrap a dot: the dot needs its
        whole operand blocks)."""
        return isinstance(st, (tir.Loop, tir.If)) and self._contains_dot(st)

    # -- T028: the mixed-extent region restructure -----------------------------

    def _region_extents(self, st, depth: int = 0) -> set:
        """The set of flat block extents a runtime region's body uses
        (non-raising: the mixed-extent boundary is decided by the caller,
        which restructures instead of refusing)."""
        if depth > 8:
            return set()
        out: set = set()
        if isinstance(st, tir.Op):
            for v in list(st.results) + list(st.operands):
                if v.rank > 0:
                    n = tir.flat_extent(v.shape)
                    if n is not None and n != 1:
                        out.add(n)
            return out
        if isinstance(st, tir.If):
            for s in list(st.then.statements) + list(st.els.statements):
                out |= self._region_extents(s, depth + 1)
            if st.cond.rank > 0:
                n = tir.flat_extent(st.cond.shape)
                if n is not None and n != 1:
                    out.add(n)
            return out
        if isinstance(st, tir.Loop):
            for b in (st.lower, st.upper, st.step, st.cond):
                if b is not None and b.rank > 0:
                    n = tir.flat_extent(b.shape)
                    if n is not None and n != 1:
                        out.add(n)
            for _, init in st.carried:
                if init.rank > 0:
                    n = tir.flat_extent(init.shape)
                    if n is not None and n != 1:
                        out.add(n)
            for s in st.body.statements:
                out |= self._region_extents(s, depth + 1)
            return out
        return out

    def _region_body_statements(self, st) -> list:
        if isinstance(st, tir.If):
            return list(st.then.statements) + list(st.els.statements)
        if isinstance(st, tir.Loop):
            return list(st.body.statements)
        return []

    def _is_mixed_extent_region(self, st) -> bool:
        """A runtime region whose body mixes block extents (or hosts a
        layout/partial-reduce/dot segment, or hosts a reduction whose
        partial a later statement of the same body consumes): the chunk
        loop cannot host it -- the region restructures at the segment
        level exactly like a dot-hosting region (T032, the repair of
        T028's recorded boundary).

        T028 disabled this restructure after reproduced staging-path
        hangs (a staged block carry across the back edge; a masked 2-D
        access with a ragged row tail).  T030's element-counter repair of
        the back-edge copy fixed the hang mechanism (the copy loop's
        induction never advanced past chunk one), and T032 completes the
        design: EVERY block carry of a restructured loop stages through
        the workspace (the analysis stages init and end value below --
        no block register crosses the restructured back edge, so no
        carry exclusion remains), and the staging allocation stays the
        bounded bump over the finite staged set (compile-time extents;
        no retry loop anywhere in the analysis).  A heterogeneous region
        the staging cannot host still refuses with a located diagnostic
        (never a hang): the per-site refusals in _store_staged,
        _copy_staged_region, _emit_staging_loop and the emission-time
        block-carry check are the boundary."""
        if not isinstance(st, (tir.Loop, tir.If)):
            return False
        if self._is_matrix_region(st):
            return False          # the dot lane already owns it
        exts = self._region_extents(st)
        if len(exts) > 1:
            return True
        for s in self._region_body_statements(st):
            if self._is_layout_op(s) or self._is_partial_reduce(s) \
                    or self._is_matrix_stmt(s):
                return True
            if isinstance(s, (tir.Loop, tir.If)) \
                    and self._is_mixed_extent_region(s):
                return True
        # T032: a reduction whose rank-0 partial a LATER statement of
        # the same body consumes (argmax's remainder branch: the reduce
        # feeds a where-chain inside the arm).  Inside one chunk-region
        # iteration the consumer would read the PER-CHUNK partial (the
        # accumulator's state mid-loop), not the merged value that binds
        # at the pass exit; the restructured body's own segmentation
        # splits the producer's and the consumer's passes exactly like
        # the top-level partial-consumer split.
        if self._region_hosts_consumed_partial(st):
            return True
        return False

    def _region_hosts_consumed_partial(self, st) -> bool:
        """Does the region's body host a reduce whose rank-0 plan partial
        is consumed by a later statement of the same body?  (Scans are
        excluded: their in-pass consumption is the scan's own per-chunk
        prefix design.)"""
        partials = self._rank0_partial_vids()
        if not partials:
            return False

        def walk(stmts, produced: set) -> bool:
            for s in stmts:
                if isinstance(s, tir.Op):
                    if s.op == "reduce" \
                            and any(r.vid in partials for r in s.results):
                        produced.update(r.vid for r in s.results
                                        if r.vid in partials)
                        continue
                    if any(o.vid in produced for o in s.operands):
                        return True
                elif isinstance(s, tir.If):
                    if s.cond.vid in produced:
                        return True
                    if walk(list(s.then.statements)
                            + list(s.els.statements), produced):
                        return True
                elif isinstance(s, tir.Loop):
                    for bound in (s.lower, s.upper, s.step, s.cond):
                        if bound is not None and bound.vid in produced:
                            return True
                    if any(init.vid in produced for _, init in s.carried):
                        return True
                    if walk(list(s.body.statements), produced):
                        return True
            return False

        return walk(self._region_body_statements(st), set())

    def _is_matrix_stmt(self, st) -> bool:
        """A top-level statement the matrix lane owns: a dot, or a region
        hosting one."""
        if isinstance(st, tir.Op):
            return st.op == "linalg.dot"
        return self._is_matrix_region(st)

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
            if st.op == "linalg.dot":
                # the matrix lane's segment: it never constrains a pass
                # (the segmentation routes it out before extents matter)
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
            if self._is_matrix_region(st):
                return None          # restructured: never in a pass
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
            if self._is_matrix_region(st):
                return None          # restructured: never in a pass
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
                    # a bool pointee is backed one byte per element (the
                    # dtype-surface bool lane): the memory runs at SEW 8
                    # with the i1 value materialized as 0/1 bytes
                    # (_storage_pointee / the bool load-store lane)
                    sew = _storage_pointee(pointee).bitwidth()
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
        # the rank-0 partials the plan declares (their merged value binds
        # at the pass exit) and whether one has been defined yet -- a
        # BETWEEN-passes consumer of one is as unhostable for the
        # worker-strided two-phase split as a mid-pass consumer (phase 1
        # would read the worker's own partial, not the merged value)
        partial_vids = self._rank0_partial_vids()
        partial_seen = False

        def close():
            nonlocal cur, cur_extent, cur_sew
            if cur:
                segs.append(("pass", cur, cur_extent, cur_sew))
                cur, cur_extent, cur_sew = [], None, None

        for st in region:
            if self._is_matrix_stmt(st):
                # T014: the matrix lane -- a dot (or a runtime region
                # hosting one) is its own segment; the pass closes and
                # the dot lowers through the workspace tile pipeline
                close()
                segs.append(("matrix", st))
                partial_seen = partial_seen or \
                    self._produces_partial(st, partial_vids)
                continue
            if self._is_mixed_extent_region(st):
                # T028: a mixed-extent (or layout/preduce-hosting) runtime
                # region restructures at the segment level -- the body's
                # statements lower through their own passes (the chunk
                # loop cannot host mixed extents homogeneously)
                close()
                segs.append(("matrix", st))
                partial_seen = partial_seen or \
                    self._produces_partial(st, partial_vids)
                continue
            if self._is_partial_reduce(st):
                # T028: a partial-axis reduction -- the result block has
                # another shape than the operand; the pass closes and the
                # staging loop materializes the reduced block
                close()
                segs.append(("preduce", st))
                partial_seen = partial_seen or \
                    self._produces_partial(st, partial_vids)
                continue
            if self._is_layout_op(st):
                close()
                segs.append(("layout", st))
                continue
            # T028: the pass splits at the first statement that consumes a
            # reduction partial the pass itself defines -- the merged value
            # binds at the pass's EXIT (the chunk accumulator's back edge),
            # so the consumer must lower after that pass closes (a mid-pass
            # emission would read the per-chunk partial).  The consumer
            # opens the next segment: a scalar statement lowers straight-
            # line between passes; a block statement re-opens a pass that
            # splats the merged scalar.
            if cur and self._consumes_partial_defined_in(st, cur):
                close()
                self._pass_split_at_partial = True
            elif not cur and partial_seen and partial_vids and \
                    self._consumes_partial(st, partial_vids, ()):
                # a BETWEEN-passes consumer of an earlier pass's merged
                # partial (the pass closed on an extent/SEW change before
                # the consumer): the merged value binds at the pass exit,
                # so the consumer is correct on the normal per-program
                # path -- but the worker-strided two-phase split cannot
                # host it (phase 1 would read the worker's own partial)
                self._pass_split_at_partial = True
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
            partial_seen = partial_seen or \
                self._produces_partial(st, partial_vids)
        close()
        return segs

    def _rank0_partial_vids(self) -> set:
        """The plan partials whose merged value binds at a pass exit (the
        rank-0 ones; a block-valued partial is chunk-local by design)."""
        if self.stage_plan is None or not self.stage_plan.partials:
            return set()
        vids = set()
        for p in self.stage_plan.partials:
            v = self._value_by_vid(p.value_id)
            if v.rank > 0:
                continue
            vids.add(p.value_id)
            if p.pair_value_id is not None:
                vids.add(p.pair_value_id)
        return vids

    def _consumes_partial_defined_in(self, st, cur: list) -> bool:
        """Does the statement consume a plan partial that a statement in
        the open pass run defines?  (The scan carries are excluded: their
        in-pass consumption is the scan's own per-chunk prefix design.
        BLOCK-valued partials are excluded too: a loop-carried block
        accumulator is chunk-LOCAL by design -- the source loop nests
        inside the chunk region, so its exit param is the final
        per-element value for that chunk's lanes and an in-pass consumer
        reads exactly that; only a rank-0 partial's merged value binds at
        the pass exit.)"""
        if self.stage_plan is None or not self.stage_plan.partials:
            return False
        partial_vids = set()
        for p in self.stage_plan.partials:
            v = self._value_by_vid(p.value_id)
            if v.rank > 0:
                continue          # a block carry: chunk-local, no split
            partial_vids.add(p.value_id)
            if p.pair_value_id is not None:
                partial_vids.add(p.pair_value_id)
        if not partial_vids:
            return False
        for s in cur:
            if self._produces_partial(s, partial_vids):
                return self._consumes_partial(st, partial_vids, ())
        return False

    def _hoist_carry_stmts(self, segments: list, ids: set) -> list:
        """Pull the trailing carried-name definitions out of a matrix
        body's pass segments (T014): the induction increment, the while
        condition's re-evaluation and the scalar carries' final values
        must dominate the loop's BACK EDGE -- a mid-pass emission sits
        inside the chunk loop, whose body does not dominate the edge.
        Only the TRAILING run is hoisted (a definition the pass's earlier
        statements consume stays in place; the frontend appends the
        increments last, which is exactly the trailing run)."""
        out: list = []
        for seg in segments:
            if seg[0] != "pass":
                out.append(seg)
                continue
            stmts = seg[1]
            i = len(stmts)
            while i > 0 and id(stmts[i - 1]) in ids:
                i -= 1
            if i == len(stmts):
                out.append(seg)
                continue
            kept, hoisted = stmts[:i], stmts[i:]
            if kept:
                out.append(("pass", kept, seg[2], seg[3]))
            out.append(("scalar", hoisted))
        return out

    def _flat_segments(self, statements, out: list) -> None:
        """Flatten one statement list's segmentation, recursing into
        matrix regions (T014): a matrix region's body segments the same
        way, and the staging analysis needs the sub-segment def/use order
        inside it -- a load in the body's pass feeds the body's dot, and
        the dot's result feeds the body's later passes or the next
        iteration.  If-arms are walked sequentially (conservative for the
        def/use order: staging an extra value is always correct)."""
        for seg in self._segment_region(statements):
            if seg[0] == "matrix" and isinstance(seg[1], (tir.Loop, tir.If)):
                st = seg[1]
                if isinstance(st, tir.If):
                    self._flat_segments(list(st.then.statements), out)
                    self._flat_segments(list(st.els.statements), out)
                else:
                    self._flat_segments(list(st.body.statements), out)
                # the region's own joins define values at this position
                out.append(("matrix_region_join", st))
                continue
            out.append(seg)

    def _analyze_staging(self) -> None:
        """Compute the staged-value set and the workspace layout.

        A value is staged when (a) it is a block operand of a layout op
        or a dot (the matrix segment reads whole operand regions), (b)
        it is a block value whose definition segment precedes its first
        use segment (it crosses a pass boundary; registers do not survive
        a pass loop), or (c) it is a dot result (the matrix segment
        writes it; consumers materialize it chunk by chunk).  Layout
        results are staged by construction.  Matrix regions are
        flattened into their sub-segments (T014).
        """
        flat: list = []
        self._flat_segments(
            self._body_split[1] if self._body_split else [], flat)
        # (a) layout operands + dot operands/results (T014: the dot's
        # breadth plan decides the staging convention -- the IME path's
        # 8/16-bit operands and results stage at their NATIVE width so
        # the tile pipeline reads them through the safe unit-stride
        # forms; bf16 keeps the standard exact-fp32-widened convention
        # the vector path FMAs from)
        for seg in flat:
            if seg[0] == "layout":
                op = seg[1]
                for v in op.operands:
                    if v.rank > 0 and v.vid not in self._staged:
                        self._staged[v.vid] = {"pending": True}
                        self._stage_out.add(v.vid)
            elif seg[0] == "preduce":
                # T028: the partial-axis reduction's operand stages (the
                # staging loop reads whole reduced sets) and its result is
                # staged by construction (the loop writes it; consumers
                # materialize it chunk by chunk)
                op = seg[1]
                v = op.operands[0]
                if v.rank > 0 and v.vid not in self._staged:
                    self._staged[v.vid] = {"pending": True}
                    self._stage_out.add(v.vid)
                for r in op.results:
                    self._staged[r.vid] = {"pending": True}
            elif seg[0] == "matrix" and isinstance(seg[1], tir.Op) \
                    and seg[1].op == "linalg.dot":
                op = seg[1]
                plan = self._dot_plan_of(op)
                self._dot_plans[op.results[0].vid] = plan
                native_ime = plan.path == "ime"
                for v in op.operands:
                    if v.rank > 0 and v.vid not in self._staged:
                        self._staged[v.vid] = {"pending": True}
                        self._stage_out.add(v.vid)
                    if v.rank > 0 and native_ime \
                            and v.type.bitwidth() < 32 \
                            and v.type.name != "bf16":
                        self._staged[v.vid]["native"] = True
                for r in op.results:
                    self._staged[r.vid] = {"pending": True}
                    if native_ime and r.type.bitwidth() < 32:
                        self._staged[r.vid]["native"] = True
        # (b) cross-pass block values: definition segment index vs use.
        # T033: the SCALAR segments participate too -- their block-shaped
        # statements (the splat-agnostic extent-1 forms: the leading
        # address chains of a bf16-load/fp32-store kernel) open the
        # default chunk at their lowering and bind INSIDE it, so a later
        # pass's address walk needs them staged exactly like a pass-body
        # value (skipping the scalar segments left softsign's (1,) bf16
        # offsets un-staged: use-before-definition at the store's pass).
        defined_in: Dict[int, int] = {}
        seg_index = 0
        for seg in flat:
            if seg[0] == "scalar":
                for st in seg[1]:
                    for r in getattr(st, "results", ()):
                        defined_in[r.vid] = seg_index
                    self._region_defs(st, defined_in, seg_index)
                seg_index += 1
                continue
            if seg[0] == "layout":
                op = seg[1]
                for r in op.results:
                    defined_in[r.vid] = seg_index
                    # T030: never clobber an existing record -- part (a)
                    # already staged a dot-operand layout result with its
                    # NATIVE convention (the transposed fp16 A tile of
                    # matmul_at_b: the overwrite silently dropped the
                    # native flag, the permute's staging loop wrote
                    # 32-bit lanes into the region the IME tile pipeline
                    # reads as raw 16-bit)
                    if r.vid not in self._staged:
                        self._staged[r.vid] = {"pending": True}
                seg_index += 1
                continue
            if seg[0] == "preduce":
                for r in seg[1].results:
                    defined_in[r.vid] = seg_index
                seg_index += 1
                continue
            if seg[0] == "matrix" and isinstance(seg[1], tir.Op) \
                    and seg[1].op == "linalg.dot":
                for r in seg[1].results:
                    defined_in[r.vid] = seg_index
                seg_index += 1
                continue
            if seg[0] == "matrix_region_join":
                for r in getattr(seg[1], "join_results", ()):
                    defined_in[r.vid] = seg_index
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
        for seg in flat:
            uses: List[tir.Value] = []
            if seg[0] == "scalar":
                for st in seg[1]:
                    uses.extend(self._region_uses(st))
            elif seg[0] == "layout":
                uses.extend(seg[1].operands)
            elif seg[0] == "preduce":
                uses.extend(seg[1].operands)
            elif seg[0] == "matrix" and isinstance(seg[1], tir.Op):
                uses.extend(seg[1].operands)
            elif seg[0] == "matrix_region_join":
                uses.extend(self._region_uses(seg[1]))
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
        # an IN-PASS runtime region's join consumed by a later pass: the
        # join's register is the region-exit block param, which does not
        # survive the pass close (the pre-check state emitted the param's
        # use inside the later pass's chunk body and the MIR verifier
        # rejected it as use-before-definition -- a silent-guess emission,
        # never the designed boundary).  T031: the join STAGES -- its
        # lanes store to the private workspace at the region's join (the
        # chunk body's top level, where the region's own register still
        # dominates) and the later pass materializes them chunk by chunk,
        # exactly like a top-level staged value.
        seg_index = 0
        for seg in flat:
            if seg[0] == "pass":
                for st in seg[1]:
                    for jv in getattr(st, "join_results", ()):
                        if jv.rank == 0 or jv.vid in self._staged:
                            continue
                        if self._join_used_later(jv, flat, seg_index):
                            self._staged[jv.vid] = {"pending": True}
                            self._stage_out.add(jv.vid)
            seg_index += 1
        # (c) T014/T032: the restructured regions' staged loop carries --
        # the body-end value must stage (the back-edge copy writes its
        # region); the loop's join aliases the init's record (resolved
        # after the allocation below).  T032: an ordinary BLOCK carry
        # stages too (the restructured loop's back edge cannot keep a
        # block register): both the init (its producer stores before the
        # loop) and the end value (its definition stores inside the body)
        # get regions, and the join aliases the init -- the workspace IS
        # the carry.  A carry whose body-end value does not exist keeps
        # the emission's located refusal.
        self._staged_join_aliases: List[Tuple[int, int]] = []
        # T032: the sequential name environment of the flat walk -- the
        # pre-if binding of a ONE-ARMED if's join names (the else arm
        # keeps the pre-if value; chunk_gdn2's guarded tile accumulators
        # assign only inside the guard)
        env: Dict[str, tir.Value] = {}
        for seg in flat:
            if seg[0] != "matrix_region_join":
                if seg[0] in ("scalar", "pass"):
                    env.update(self._tir_end_names(seg[1]))
                elif seg[0] in ("layout", "preduce"):
                    for r in seg[1].results:
                        for key in r.scope_names():
                            env[key] = r
                elif seg[0] == "matrix" and isinstance(seg[1], tir.Op):
                    for r in seg[1].results:
                        for key in r.scope_names():
                            env[key] = r
                continue
            st = seg[1]
            if isinstance(st, tir.Loop):
                for entry in self._classify_carried(st):
                    if entry[0] not in ("staged", "block"):
                        continue
                    init_rec = self._staged.get(entry[2].vid)
                    if init_rec is None:
                        # T032: a "block" carry the def/use walk did not
                        # stage (the init's only cross-boundary use is
                        # the carry itself): stage it now -- its producer
                        # stores to the region before the loop opens
                        self._staged[entry[2].vid] = {"pending": True}
                        self._stage_out.add(entry[2].vid)
                        init_rec = self._staged[entry[2].vid]
                    if entry[3] is not None and entry[3].vid not in \
                            self._staged:
                        self._staged[entry[3].vid] = {"pending": True}
                        # T030: the back-edge copy moves bytes between
                        # the end value's region and the init's region,
                        # so the end value stages under the INIT's
                        # convention -- an IME dot operand's native
                        # 8/16-bit record propagates to the body-end
                        # value (the double-buffered prefetch carry:
                        # the load before the loop and the rebind inside
                        # it are the same logical block next iteration;
                        # a standard end record beside a native init
                        # record is the width mismatch the copy refuses)
                        if init_rec.get("native"):
                            self._staged[entry[3].vid]["native"] = True
                    # the body's definition of the end value stores to
                    # its region (the back-edge copy reads it); without a
                    # later TIR use the def/use walk would have missed it
                    if entry[3] is not None:
                        self._stage_out.add(entry[3].vid)
                    for (cname, init), jv in zip(st.carried,
                                                 st.join_results):
                        if init.vid == entry[2].vid:
                            self._staged_join_aliases.append((jv.vid,
                                                              init.vid))
                # the loop's joins rebind the carried names for the walk
                # that follows (a later one-armed if's else fallback reads
                # them)
                for (cname, init), jv in zip(st.carried, st.join_results):
                    env[cname] = jv
                continue
            if isinstance(st, tir.If):
                # T032: a restructured if's BLOCK joins flow through the
                # workspace -- the join gets its OWN region (never one
                # arm's: the untaken arm would leave a borrowed region
                # unwritten), and each arm's final value of the join name
                # stages (its producer stores); the emission copies the
                # arm-final region into the join region at every arm
                # close, so whichever arm runs leaves the join's bytes
                # correct (scalar joins keep the block-parameter join)
                arm_ends = [self._tir_end_names(arm.statements)
                            for arm in (st.then, st.els)]
                sources: Dict[str, tuple] = {}
                for jname, jv in zip(st.join_names, st.join_results):
                    if jv.rank == 0:
                        continue          # the scalar parameter join
                    # an arm that does not rebind the name keeps the PRE-IF
                    # value (the one-armed guard form: the else arm's
                    # final is the name's binding before the if)
                    finals = [arm_ends[i].get(jname)
                              if arm_ends[i].get(jname) is not None
                              else env.get(jname) for i in (0, 1)]
                    if any(f is None for f in finals):
                        continue      # the emission's located refusal
                    if jv.vid not in self._staged:
                        self._staged[jv.vid] = {"pending": True}
                    for f in finals:
                        if f.vid not in self._staged:
                            self._staged[f.vid] = {"pending": True}
                        self._stage_out.add(f.vid)
                    sources[jname] = (jv, finals)
                if sources:
                    self._if_join_sources = getattr(self,
                                                    "_if_join_sources", {})
                    self._if_join_sources[id(st)] = sources
                # the joins define the names for the walk that follows
                for jname, jv in zip(st.join_names, st.join_results):
                    env[jname] = jv
                continue
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
            rec = self._staged[vid]
            if rec.get("offset") is not None:
                continue          # an aliased record: already allocated
            v = self._value_by_vid(vid)
            extent = self._flat_extent_of(v.shape, v.loc, "layout")
            rec["offset"] = offset
            rec["extent"] = extent
            rec["type"] = v.type
            # the staging lane width: the indexed memory forms with an
            # e64 index SEGFAULT the pinned QEMU when the data element
            # is narrower than 32 bits (probed: e8/e16 data + e64m2
            # index at avl 32 crashes; e32 data works -- complex_pack's
            # fp16 staging already rides the fp32 compute lanes).  Every
            # staged region therefore uses 32-bit (or wider) lanes --
            # EXCEPT the matrix lane's native records (T014): the IME
            # tile pipeline reads those through unit-stride forms at
            # compiler-known scalar addresses, never an index vector, so
            # the dense 8/16-bit layout is safe and needs no conversion.
            if rec.get("native"):
                rec["lane_sew"] = v.type.bitwidth()
                rec["esz"] = rec["lane_sew"] // 8
            else:
                rec["lane_sew"] = max(32, v.type.bitwidth())
                if v.type.is_bool():
                    rec["esz"] = 4
                    rec["mask"] = True
                else:
                    rec["esz"] = rec["lane_sew"] // 8
            offset += extent * rec["esz"]
        self._layout_ws_end = offset
        # the staged loop-carried joins alias their init's record (the
        # back-edge copy leaves it holding the final value)
        for join_vid, init_vid in getattr(
                self, "_staged_join_aliases", []):
            self._staged[join_vid] = self._staged[init_vid]

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

    def _join_used_later(self, jv: tir.Value, flat: list,
                         seg_index: int) -> bool:
        """Is one region-join value consumed by a segment after its
        defining segment?  (The def/use staging walk skips producer-less
        values -- a join has no producer op -- so the cross-pass check
        walks them explicitly.)"""
        for later in range(seg_index + 1, len(flat)):
            seg = flat[later]
            uses: List[tir.Value] = []
            if seg[0] == "scalar":
                continue
            if seg[0] in ("layout", "preduce"):
                uses.extend(seg[1].operands)
            elif seg[0] == "matrix" and isinstance(seg[1], tir.Op):
                uses.extend(seg[1].operands)
            elif seg[0] == "matrix_region_join":
                uses.extend(self._region_uses(seg[1]))
            else:
                for st in seg[1]:
                    uses.extend(self._region_uses(st))
            if any(v.vid == jv.vid for v in uses):
                return True
        return False

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

    # -- T014: carried-value classification (the pointer-recurrence repair
    # and the matrix regions' staged carries) ----------------------------------

    def _tir_end_names(self, statements) -> Dict[str, tir.Value]:
        """The name -> value binding at the end of a TIR statement list
        (the lowering's own scoping rule, simulated on TIR: ops define
        their results under every scope name; regions define their
        joins under the join names).  Used to find a loop's back-edge
        value for each carried name BEFORE the body is lowered."""

        names: Dict[str, tir.Value] = {}

        def bind(v: tir.Value) -> None:
            for key in v.scope_names():
                names[key] = v

        def walk(stmts) -> None:
            for st in stmts:
                if isinstance(st, tir.Op):
                    for r in st.results:
                        bind(r)
                elif isinstance(st, tir.If):
                    walk(st.then.statements)
                    walk(st.els.statements)
                    for name, jv in zip(st.join_names, st.join_results):
                        names[name] = jv
                        bind(jv)
                elif isinstance(st, tir.Loop):
                    walk(st.body.statements)
                    for (cname, _init), jv in zip(st.carried,
                                                  st.join_results):
                        names[cname] = jv
                        bind(jv)

        walk(statements)
        return names

    def _region_defined_vids(self, stmt, out: set) -> None:
        """Every vid defined inside a region (transitively), including
        the joins."""
        if isinstance(stmt, tir.Op):
            out.update(r.vid for r in stmt.results)
        elif isinstance(stmt, tir.If):
            for s in list(stmt.then.statements) + list(stmt.els.statements):
                self._region_defined_vids(s, out)
            out.update(r.vid for r in stmt.join_results)
        elif isinstance(stmt, tir.Loop):
            for s in stmt.body.statements:
                self._region_defined_vids(s, out)
            out.update(r.vid for r in stmt.join_results)

    def _value_outside(self, v: tir.Value, inside: set,
                       seen: Optional[set] = None,
                       carried: Optional[set] = None) -> bool:
        """Is ``v`` loop-invariant (a legal uniform-recurrence step)?

        A value is invariant when every leaf of its producer tree is a
        parameter, a constant, or a value defined outside the loop body.
        Statement location is irrelevant for PURE trees (the frontend
        lowers ``p += BK * s`` inside the body; the tree re-materializes
        at the loop level).  A CARRIED name's init vid denotes the
        current iteration's value inside the body (the override
        semantics) -- any dependence on one makes the tree
        iteration-dependent, so it is not a legal step."""
        if seen is None:
            seen = set()
        if carried is None:
            carried = frozenset()
        if v.vid in seen:
            return True
        seen.add(v.vid)
        if v.vid in carried:
            return False
        prod = v.producer
        if prod is None or prod.op == "const":
            return True
        if v.vid not in inside:
            return True              # defined before the loop: invariant
        # a body-defined pure tree: invariant iff its operands are
        return all(self._value_outside(o, inside, seen, carried)
                   for o in prod.operands)

    def _classify_carried(self, stmt: tir.Loop) -> List[tuple]:
        """Classify the loop's carried entries (beyond the induction /
        condition) for the emission:

        * ``("scalar", name, init)`` -- an ordinary scalar param;
        * ``("recurrence", name, init, step_value)`` -- a uniform
          pointer-block carry whose back edge is
          ``ptradd(carried, scalar)`` with a loop-invariant step: the
          carried pointer becomes a SCALAR offset param (the repair for
          the address-recurrence miscompile: the static ptradd tree
          never sees the step, so a vector param reads the first
          iteration's addresses forever);
        * ``("staged", name, init, end_value)`` -- a block carry that
          flows through the workspace (the dot pipeline's accumulator
          chain); the back edge copies the end value's region into the
          init's region;
        * ``("block", name, init, end_value)`` -- an ordinary block carry
          (the normal path keeps its chunk vreg param; the matrix path
          refuses it);
        * ``("refused", name, init, why)`` -- a carry with no legal form
          in this lane (a located refusal at emission).
        """
        inside: set = set()
        for s in stmt.body.statements:
            self._region_defined_vids(s, inside)
        carried_vids = {init.vid for _, init in stmt.carried}
        end_names = self._tir_end_names(stmt.body.statements)
        out: List[tuple] = []
        def _bare_step(v):
            """The uniform step of a pointer recurrence: a rank-0 value,
            or the frontend's broadcast-of-scalar expansion of one (the
            augmented ``p += s`` on a block pointer broadcasts the scalar
            step over the block shape)."""
            if v.rank == 0:
                return v
            prod = v.producer
            if prod is not None and prod.op == "broadcast" \
                    and prod.operands[0].rank == 0:
                return prod.operands[0]
            return None

        for cname, init in stmt.carried[1:]:
            if init.rank == 0:
                out.append(("scalar", cname, init))
                continue
            end = end_names.get(cname)
            step = None
            if end is not None and end.producer is not None \
                    and end.producer.op == "ptradd" \
                    and end.producer.operands[0].vid == init.vid:
                step = _bare_step(end.producer.operands[1])
            if step is not None and self._value_outside(
                    step, inside, carried=carried_vids):
                out.append(("recurrence", cname, init, step))
                continue
            if init.vid in self._staged:
                if end is None:
                    out.append(("refused", cname, init,
                                "the carried name is not redefined by the "
                                "body (the verifier requires it)"))
                else:
                    out.append(("staged", cname, init, end))
                continue
            # an ordinary block carry: the normal path keeps its chunk
            # vreg param (today's behavior); the matrix path refuses it
            # (a block register cannot survive the restructured loop)
            out.append(("block", cname, init, end))
        return out

    def _recurrence_of(self, v: tir.Value) -> Optional[tuple]:
        """The active pointer-recurrence frame for a vid, if any (the
        innermost frame wins; nested frames over the same pointer
        accumulate -- every active layer's offset is added by the address
        resolution)."""
        for frame in reversed(self._ptr_recurrences):
            rec = frame.get(v.vid)
            if rec is not None:
                return rec
        return None

    def _active_recurrence_offsets(self, v: tir.Value) -> List[mir.VReg]:
        """Every active recurrence layer's offset register for one vid
        (nested loops carrying the same pointer each add their step)."""
        return [frame[v.vid][1] for frame in self._ptr_recurrences
                if v.vid in frame]

    def _value_by_vid(self, vid: int) -> tir.Value:
        # MECH-COMPILE-COST-LINEAR: an indexed map built once per module,
        # never a rebuild-and-scan per query (the per-statement partial
        # checks of the segmentation made the walk cubic on big unrolled
        # bodies -- complex_svd's ~1400-statement static_range nest went
        # from seconds past every budget to linear)
        index = getattr(self, "_vid_index", None)
        if index is None:
            index = {}
            for fn in self.tir_module.functions:
                for v in self._walk_values(fn.body):
                    index.setdefault(v.vid, v)
            self._vid_index = index
        v = index.get(vid)
        if v is None:
            raise self._err(None, "layout", f"no TIR value with vid {vid}")
        return v

    def _walk_values(self, block: tir.Block):
        """Every TIR value mentioned in the block (results, operands,
        region bounds and joins), nested regions included."""
        for stmt in block.statements:
            if isinstance(stmt, tir.Op):
                for r in stmt.results:
                    yield r
                for o in stmt.operands:
                    yield o
            elif isinstance(stmt, tir.If):
                yield stmt.cond
                for v in stmt.join_results:
                    yield v
                for b in (stmt.then, stmt.els):
                    yield from self._walk_values(b)
            elif isinstance(stmt, tir.Loop):
                for v in (stmt.lower, stmt.upper, stmt.step, stmt.cond):
                    if v is not None:
                        yield v
                for _, init in stmt.carried:
                    yield init
                for v in stmt.join_results:
                    yield v
                yield from self._walk_values(stmt.body)

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
                       # a 64-bit record loads the full register (the
                       # repertoire's single 64-bit row -- extension is
                       # vacuous there, and every 64-bit sload in the
                       # emitted programs carries this tag); narrower
                       # records extend by the record's own signedness
                       "ext": "sext" if (binding.signed
                                         or binding.width == 64) else "zext"},
                loc=loc))
            # the TIR value at its declared type.  The record width and the
            # kernel's signature are independent by construction (the packer
            # writes the host scalar at ITS own width -- a Python float is a
            # float64 record -- while the kernel declares the argument an
            # fp32 scalar), so a width disagreement CONVERTS on read, never
            # refuses: floats through the declared RTNE narrowing / exact
            # widening (raw bits in a GPR at the declared width), integers
            # through the truncation of the wide form (a 32-bit value never
            # binds to an i64 reg -- the binop type rules would see a
            # phantom mismatch)
            ty = binding.tir_type
            tir_reg = reg
            if ty.is_float():
                if ty.width != binding.width:
                    tir_reg = scalar_mod.convert_float_scalar(
                        ctx, reg, binding.width, ty, loc)
                # a floating scalar binds at its own width (raw bits);
                # arithmetic on it lowers through the vector path and
                # it never feeds grid/index arithmetic
                wide = tir_reg
            else:
                wide = reg
                if binding.width != 64:
                    wide = ctx.emit(mir.MOp(
                        "smove", [reg],
                        [ctx.vreg(mir.I64,
                                  hint=binding.name + "w", loc=loc)],
                        loc=loc))
                if ty.width != binding.width:
                    tir_reg = ctx.emit(mir.MOp(
                        "strunc", [wide],
                        [ctx.vreg(mir.ScalarType(ty.width, signed=ty.signed),
                                  hint=binding.name + "n", loc=loc)], loc=loc))
            grid_scalar_regs[binding.name] = wide
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
            # the split path runs the single program -- program 0 on
            # EVERY grid axis (a 2-axis grid's ``tl.program_id(1)`` is 0
            # here exactly like axis 0; refusing because only axis 0 was
            # populated rejected multi-axis kernels whose split gate can
            # never fire for their real grids)
            for axis in range(self.grid.ndim):
                self._pid_axis_regs[axis] = ctx.const(0, mir.I32, loc)
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

        # T032: the workspace bases load ONCE at the path top (dominating
        # every pass, region and merge the path emits) when the kernel
        # uses a workspace at all -- the lazily-loaded per-scope bases
        # otherwise pile up live across nested restructured regions (see
        # _drop_ws_caches).  A workspace-free kernel keeps its registers.
        self._ws_path_scoped = bool(
            self.plan.workspace_private > 0
            or (self.stage_plan is not None and self.stage_plan.eligible))
        if self._ws_path_scoped:
            self._workspace_private_reg(ctx, loc)
            self._workspace_shared_reg(ctx, loc)

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
                "tir_type": acc.get("tir_type"),
            })
        # T032: the kernel-level merge list -- every segmentation level
        # (the top-level passes AND the restructured regions' nested
        # passes) filters its frames from THIS list: the nested walk
        # otherwise inherits the outer pass's filtered remnant and a
        # reduce inside the region never meets its accumulator frame
        # (the plan-and-lowering disagreement the back edge refuses)
        self._kernel_merges = list(self._chunk_merges)
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

    def _drop_ws_caches(self) -> None:
        """Drop the cached workspace-base registers (dominance scoping: a
        register lazily loaded inside a pass body or a region arm does not
        dominate the code after that scope's close).  T032: a PATH-SCOPED
        base (loaded once at the program path's top, before any pass or
        region opens -- see _emit_program_path) dominates the whole path
        emission, so the scope closes keep it: the nested restructured
        regions otherwise re-load one base per level and hold BOTH live
        (adaptive_avg_pool2d's double-nested loops: 28 simultaneous GPR
        values against 25 allocatable -- the allocation non-convergence)."""
        if getattr(self, "_ws_path_scoped", False):
            self._wid64 = None
            return
        self._ws_private = None
        self._ws_shared = None
        self._wid64 = None

    def _merge_frame_of(self, partial: "stages_mod.PartialSpec") -> dict:
        vtype = self._vtype(partial.dtype)
        index = partial.merge in (stages_mod.MERGE_MIN_INDEX,
                                  stages_mod.MERGE_MAX_INDEX)
        widen = 0
        narrow = None
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
        elif partial.dtype.is_float() and partial.dtype.bitwidth() == 16 \
                and not index:
            # T028, the declared fp32-lane policy (T012) for 16-bit float
            # sums: bf16 has no native vector arithmetic and fp16 rides the
            # single-rounding policy -- the accumulator and the workspace
            # partial ride fp32 lanes (the vred already computed the
            # per-chunk partial in fp32) and the merged value rounds back
            # to the element type at the exit binding (one rounding)
            vtype = mir.VectorType(32, 1, "float")
            narrow = partial.dtype
        return {
            "kind": partial.merge, "vid": partial.value_id,
            "pair_vid": partial.pair_value_id, "vtype": vtype,
            "index": index, "source": "plan", "acc": None,
            "partial": partial, "widen_exit": widen,
            "narrow_exit": narrow,
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
            if exit_params[pi].is_vector():
                self._vregion(ctx, exit_params[pi].type, loc)
            value = self._scalarize(ctx, exit_params[pi], loc)
            if exit_params[pi + 1].is_vector():
                self._vregion(ctx, exit_params[pi + 1].type, loc)
            idx = self._scalarize(ctx, exit_params[pi + 1], loc)
            ctx.emit0(mir.MOp(
                "sstore", [wsbase, value], [],
                attrs={"width": 32, "offset": slot_off}, loc=loc))
            ctx.emit0(mir.MOp(
                "sstore", [wsbase, idx], [],
                attrs={"width": 32, "offset": slot_off + 4}, loc=loc))
            return
        if frame.get("narrow_exit") is not None:
            # the fp32-lane partial: the exit parameter IS the fp32
            # accumulator (the element-typed binding is the rounded value;
            # the slot holds the exact class the merge combines)
            self._vregion(ctx, exit_params[pi].type, loc)
            value = self._scalarize(ctx, exit_params[pi], loc)
        else:
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
        # the identity seeds (each splat opens its own region at the frame's
        # accumulator type -- a partial at another SEW than the pass must
        # not splat into the pass's region)
        inits: List[mir.VReg] = []
        for f in frames:
            if f["index"]:
                ident_val = stages_mod.identity_for(
                    "min" if f["kind"] == stages_mod.MERGE_MIN_INDEX
                    else "max", f["partial"].dtype)
                ident_idx = stages_mod._index_identity(tir.INT32)
                self._vregion(ctx, f["vtype"], loc)
                inits.append(self._splat_const(ctx, ident_val, f["vtype"],
                                               loc,
                                               tir_type=f["partial"].dtype))
                self._vregion(ctx, mir.VectorType(32, 1, "int"), loc)
                inits.append(self._splat_const(ctx, ident_idx,
                                               mir.VectorType(32, 1, "int"),
                                               loc))
            else:
                ident = stages_mod.identity_for(
                    self._merge_op_kind(f["kind"]), f["partial"].dtype)
                self._vregion(ctx, f["vtype"], loc)
                inits.append(self._splat_const(ctx, ident, f["vtype"], loc,
                                               tir_type=f["partial"].dtype))
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
        # value side is internal: only the index binds); each extract runs
        # at its own SEW (the exit block carries no region across the edge)
        pi = 0
        for f in frames:
            if f["index"]:
                merged_v = frame.exit.params[pi + 1]
                merged_i = frame.exit.params[pi + 2]
                pi += 2
                if f["pair_vid"] is not None:
                    self._vregion(ctx, merged_v.type, loc)
                    self.values[f["vid"]] = self._scalarize(ctx, merged_v,
                                                           loc)
                    self._vregion(ctx, merged_i.type, loc)
                    self.values[f["pair_vid"]] = self._scalarize(
                        ctx, merged_i, loc)
                else:
                    self._vregion(ctx, merged_i.type, loc)
                    self.values[f["vid"]] = self._scalarize(ctx, merged_i,
                                                           loc)
            else:
                merged = frame.exit.params[pi + 1]
                pi += 1
                self._vregion(ctx, merged.type, loc)
                if f.get("narrow_exit") is not None:
                    # the fp32-lane policy's one rounding at the element
                    # type (the merged fp32 accumulator narrows here)
                    narrow_vec = self._f32_to_ff(ctx, merged,
                                                 f["narrow_exit"], loc)
                    self._vregion(ctx, narrow_vec.type, loc)
                    self.values[f["vid"]] = self._scalarize(
                        ctx, narrow_vec, loc)
                else:
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
        # the suffix's live-out scalars (chunk-invariant region values,
        # e.g. a loop join the suffix consumes) rebind to registers in
        # this merge block: the chunk-body registers the back edge stored
        # from do not dominate it (the normal path reloads at the chunk
        # exit; the split path runs the suffix here)
        self._reload_liveouts(ctx, loc)
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
        self._vregion(ctx, vtype, loc)
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

    def _scalar_bool_gpr(self, ctx: _Ctx, reg: mir.VReg,
                         loc) -> mir.VReg:
        """The rank-0 bool's register: the scalar-bool convention is the
        i64 0/1 GPR (scalar comparisons, scalar bool loads, branch
        conditions); a mask-held rank-0 bool (a convert that ran through
        the vector lane's vcmp) normalizes through the lane-count test --
        the mask's lanes all carry the splatted scalar's bit, so any set
        lane means True and an all-zero mask means False.  A VECTOR-held
        rank-0 bool (T032: the bool->int convert's 0/1 class at the
        converted width) extracts lane 0 -- the raw bits are the 0/1
        value at that width, exactly (blocked_jacobi_rank's
        ``rank += (bool).to(tl.int32)`` -- the vector register met the
        scalar accumulator's GPR and the add refused)."""
        if reg.is_vector():
            return self._scalarize(ctx, reg, loc)
        return self._bool_scalar(ctx, reg, loc)

    def _scalarize(self, ctx: _Ctx, reg: mir.VReg, loc) -> mir.VReg:
        """The scalar form of a value: lane-0 vectors extract to a GPR
        (raw bits for floats); scalars pass through.

        T033: ``vextract`` (vmv.x.s) reads element 0 at the ACTIVE SEW,
        so the extract runs inside the value's own region -- a convert
        chain's tail (the bf16 emulation restores the pass's e32 region
        before the caller extracts its 16-bit result) leaves the ambient
        region wider than the value, and the extract would read the wrong
        element width.  The ambient region is restored exactly afterwards
        (its avl included, when tracked)."""
        if reg.is_vector():
            sty = mir.ScalarType(reg.type.sew, signed=reg.type.kind != "uint",
                                 float=reg.type.kind == "float")
            want = (reg.type.sew, reg.type.lmul, self._vl)
            prev = ctx.active_region
            mismatched = prev != want
            if mismatched:
                self._vregion(ctx, reg.type, loc)
            out = ctx.emit(mir.MOp(
                "vextract", [reg],
                [ctx.vreg(sty, hint="x0", loc=loc)], loc=loc))
            if mismatched:
                # restore the ambient region exactly (avl included when
                # tracked; an untracked avl restores the pass region --
                # the next region-managing op re-establishes its own)
                if prev is not None and prev[2] is not None:
                    self._vregion(
                        ctx, mir.VectorType(prev[0], prev[1], "int"), loc,
                        vl=prev[2])
                else:
                    self._restore_region(ctx, loc)
            return out
        return reg

    def _merge_op_kind(self, merge: str) -> str:
        return {"sum": "sum", "product": "cumprod", "min": "min",
                "max": "max", "xor": "xor_sum", "or": "reduce_or",
                "pass": "sum"}[merge]

    def _splat_const(self, ctx: _Ctx, value, vtype: mir.VectorType,
                     loc, tir_type: "tir.Type" = None) -> mir.VReg:
        """Splat one constant at a vector type: float identities travel as
        their raw IEEE bits (``li`` the bit pattern, ``vmv.v.x`` the
        splat) -- ``int(value)`` on a non-finite float raises and on a
        16-bit float would encode the VALUE, not the bits (the T024
        overflow class: the fp64 max-index identity is -inf)."""
        sty = mir.ScalarType(vtype.sew, signed=vtype.kind != "uint",
                             float=vtype.kind == "float")
        if sty.float:
            import struct as _struct
            if vtype.sew == 32:
                bits = _struct.unpack("<I",
                                      _struct.pack("<f", float(value)))[0]
            elif vtype.sew == 64:
                bits = _struct.unpack("<Q",
                                      _struct.pack("<d", float(value)))[0]
            elif vtype.sew == 16:
                if tir_type is not None and tir_type.name == "bf16":
                    # bf16: the top 16 bits of the IEEE single word
                    # (round-to-nearest-even on the truncated half; the
                    # identities -- 0, 1, +/-inf -- are exact under it)
                    f32 = _struct.unpack("<I",
                                         _struct.pack("<f", float(value)))[0]
                    bits = (f32 >> 16) & 0xFFFF
                elif tir_type is not None:
                    bits = _struct.unpack("<H",
                                          _struct.pack("<e", float(value)))[0]
                elif float(value) == 0.0:
                    # +0.0 is 0x0000 in every 16-bit float format: the
                    # one format-agnostic constant
                    bits = 0
                else:
                    raise self._err(
                        loc, "splat",
                        f"a 16-bit float identity {value!r} without its "
                        "TIR type (fp16 and bf16 encode different bits; "
                        "refused, not guessed)")
            else:
                raise self._err(loc, "splat",
                                f"no float bit encoding at SEW {vtype.sew}")
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
        needed (vmand composes the tie condition).  The value side and the
        index side may sit at different SEWs (an fp64 argmax value with an
        i32 index): each side's ops open their own region (the
        vsetvli-region consistency invariant)."""
        cur_region = [None]

        def at(vtype: mir.VectorType):
            key = (vtype.sew, vtype.lmul)
            if cur_region[0] != key:
                self._vregion(ctx, vtype, loc)
                cur_region[0] = key

        # min-index: the candidate wins when cand < acc; max-index: when
        # acc < cand (no floating gt: the swapped lt is the predicate)
        lhs, rhs = ((cand_v, acc_v)
                    if kind == stages_mod.MERGE_MIN_INDEX else (acc_v,
                                                                cand_v))
        at(acc_v.type)
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
        at(acc_i.type)
        i1 = ctx.emit(mir.MOp(
            "vsel", [v0a, cand_i, acc_i],
            [ctx.vreg(acc_i.type, hint="pi", loc=loc)], loc=loc))
        at(acc_v.type)
        eq = ctx.emit(mir.MOp(
            "vcmp", [cand_v, acc_v],
            [ctx.vreg(mir.MaskType(), hint="pe", loc=loc)],
            attrs={"pred": "eq", "fp": acc_v.type.kind == "float"},
            loc=loc))
        at(acc_i.type)
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
        at(acc_v.type)
        v2 = ctx.emit(mir.MOp(
            "vsel", [v0b, cand_v, v1],
            [ctx.vreg(acc_v.type, hint="pv2", loc=loc)], loc=loc))
        at(acc_i.type)
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
        if reg.is_vector():
            self._vregion(ctx, reg.type, loc)
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
            # each frame's extracts run at the accumulator's own SEW (the
            # exit block's implicit region is the LAST pass's -- a partial
            # at another width would extract its bits wrong)
            if frame["source"] == "plan" and frame.get("index"):
                if frame["pair_vid"] is not None:
                    self._vregion(ctx, exit_params[pi].type, loc)
                    self.values[frame["vid"]] = self._scalarize(
                        ctx, exit_params[pi], loc)
                    self._vregion(ctx, exit_params[pi + 1].type, loc)
                    self.values[frame["pair_vid"]] = self._scalarize(
                        ctx, exit_params[pi + 1], loc)
                else:
                    self._vregion(ctx, exit_params[pi + 1].type, loc)
                    self.values[frame["vid"]] = self._scalarize(
                        ctx, exit_params[pi + 1], loc)
                pi += 2
            else:
                self._vregion(ctx, exit_params[pi].type, loc)
                if frame.get("narrow_exit") is not None:
                    # the fp32-lane policy's one rounding at the element
                    # type (the merged fp32 accumulator narrows here)
                    narrow_vec = self._f32_to_ff(ctx, exit_params[pi],
                                                 frame["narrow_exit"], loc)
                    self._vregion(ctx, narrow_vec.type, loc)
                    self.values[frame["vid"]] = self._scalarize(
                        ctx, narrow_vec, loc)
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
            if reg.type.width == 32:
                return scalar_mod.widen_to(ctx, reg, width, loc)
            # a sub-32-bit data-SEW class (the bool lane's SEW 8, an
            # fp16 pass's 16): the 0/1 class is non-negative, so the
            # exact widening is the ZERO-extension -- splat, the vwiden
            # zext chain, extract (the scalar core has no 8->64 / 16->64
            # form and smove's 32->64 view convention does not hold for
            # the byte/half GPRs; the 16->64 and 8->64 forms were
            # located refusals)
            unsigned = False
            partial = frame.get("partial")
            if partial is not None and getattr(partial, "dtype", None) \
                    is not None:
                unsigned = partial.dtype.is_int_unsigned()
            vty = mir.VectorType(reg.type.width, 1,
                                 "uint" if unsigned else "int")
            self._vregion(ctx, vty, loc)
            vec = ctx.emit(mir.MOp(
                "s2v", [reg], [ctx.vreg(vty, hint="wxs", loc=loc)],
                loc=loc))
            wide = self._int_widen(ctx, vec, reg.type.width, width,
                                   False, loc,
                                   dst_kind="uint" if unsigned else "int")
            self._vregion(ctx, wide.type, loc)
            out = self._scalarize(ctx, wide, loc)
            self._restore_region(ctx, loc)
            return out
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
        workspace base re-loads here when the cached register was defined
        inside the chunk body (it does not dominate the exit); a
        PATH-SCOPED base (T032, loaded before any pass opened) dominates
        the exit and is reused -- a second live base register beside the
        path's own is exactly the pressure the restructured regions
        cannot afford."""
        if not self._liveouts:
            return
        if getattr(self, "_ws_path_scoped", False):
            ws = self._workspace_private_reg(ctx, loc)
        else:
            launch = ctx.function.params[0]
            ws = ctx.emit(mir.MOp(
                "sload", [launch],
                [ctx.vreg(mir.I64, hint="wsr", loc=loc)],
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
        # value identity and the worst index).  Each splat opens its OWN
        # region at its vector type: the accumulators may sit at a different
        # SEW than the pass (a partial over fp32 data in an fp16 pass -- the
        # multi-width reduce), and a block that already opened a region for
        # an earlier splat must switch before the next (the vsetvli-region
        # consistency invariant; the amp_foreach/mean bf16 class).
        merge_inits: List[mir.VReg] = []
        for frame in self._chunk_merges:
            if frame["source"] == "scan":
                ident = stages_mod.identity_for(
                    "cumsum" if frame["kind"] == "cumsum" else "cumprod",
                    self._tir_type_of(frame["vtype"]))
                self._vregion(ctx, frame["vtype"], loc)
                merge_inits.append(self._scan_init_reg(ctx, frame, ident,
                                                       loc))
            elif frame["index"]:
                p = frame["partial"]
                ident_val = stages_mod.identity_for(
                    "min" if p.merge == stages_mod.MERGE_MIN_INDEX else "max",
                    p.dtype)
                ident_idx = stages_mod._index_identity(tir.INT32)
                self._vregion(ctx, frame["vtype"], loc)
                merge_inits.append(self._splat_const(ctx, ident_val,
                                                     frame["vtype"], loc,
                                                     tir_type=p.dtype))
                self._vregion(ctx, mir.VectorType(32, 1, "int"), loc)
                merge_inits.append(self._splat_const(
                    ctx, ident_idx, mir.VectorType(32, 1, "int"), loc))
            else:
                p = frame["partial"]
                ident = stages_mod.identity_for(self._merge_op_kind(p.merge),
                                                p.dtype)
                self._vregion(ctx, frame["vtype"], loc)
                merge_inits.append(self._splat_const(ctx, ident,
                                                     frame["vtype"], loc,
                                                     tir_type=p.dtype))

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
        self._emit_segments_list(ctx, fn, view_regs, self._segments,
                                 strided=strided)

    def _emit_segments_list(self, ctx: _Ctx, fn: tir.Function,
                            view_regs: Dict[str, mir.VReg], segments: list,
                            strided: Optional[bool] = None,
                            close_all: bool = False) -> None:
        """Emit one segmentation (T014: also the matrix regions' bodies --
        every pass closes before the region's back edge; the top-level
        form keeps the last pass open for the caller's close)."""
        # T032: the kernel-level merge list (see _emit_program_path) --
        # every nesting level filters from the same complete set
        all_merges = list(getattr(self, "_kernel_merges", None)
                          or self._chunk_merges)
        n_passes = sum(1 for seg in segments if seg[0] == "pass")
        seen_pass = 0
        saved_liveouts = self._liveouts
        params_list = self._compute_pass_params(segments)
        for si, seg in enumerate(segments):
            if seg[0] == "scalar":
                self._lower_statements(ctx, seg[1], fn, view_regs)
                continue
            if seg[0] == "layout":
                if self._chunk is not None:
                    self._close_pass(ctx, fn, strided)
                self._lower_layout_segment(ctx, fn, seg[1])
                continue
            if seg[0] == "preduce":
                if self._chunk is not None:
                    self._close_pass(ctx, fn, strided)
                self._lower_partial_reduce_segment(ctx, fn, seg[1])
                continue
            if seg[0] == "matrix":
                if self._chunk is not None:
                    self._close_pass(ctx, fn, strided)
                if isinstance(seg[1], tir.Op) and seg[1].op == "linalg.dot":
                    self._lower_matrix_segment(ctx, fn, seg[1])
                else:
                    self._lower_matrix_region(ctx, seg[1], fn, view_regs)
                continue
            # a pass: configure its parameters and merges
            params = params_list[si]
            if params is None:      # pragma: no cover - segmentation shape
                raise self._err(None, "layout", "pass without parameters")
            defined = self._pass_defined_vids(seg[1])
            self._chunk_merges = [f for f in all_merges
                                  if f["vid"] in defined]
            if not self._chunk_merges and seen_pass == 0 and n_passes == 1 \
                    and segments is self._segments \
                    and not any(s[0] == "matrix"
                                and isinstance(s[1], (tir.Loop, tir.If))
                                for s in segments):
                # the single-pass form -- T032: only when NO restructured
                # region follows: a matrix region's own passes own their
                # reduces' accumulator frames now, and attaching them to
                # this pass left the back edge reading values the pass
                # never defined (the plan-and-lowering disagreement)
                self._chunk_merges = all_merges
            seen_pass += 1
            self._sew = params["sew"]
            self._vl = params["vl"]
            # this pass's cross-pass scalar liveouts (store at the back
            # edge, reload at the exit -- registers do not survive loops).
            # The top-level segmentation reads the plan-level table; a
            # restructured region's nested segmentation reads its own
            # (T028 -- same contract, its own slot pool)
            if segments is self._segments:
                self._liveouts = list(self._pass_liveouts.get(si, []))
            else:
                nested = {}
                if self._region_stack:
                    nested = self._nested_liveouts.get(
                        id(self._region_stack[-1]), {})
                self._liveouts = list(nested.get(si, []))
            if seen_pass == n_passes and segments is self._segments:
                self._liveouts.extend(saved_liveouts)
            self._open_pass(ctx, fn, params)
            self._lower_statements(ctx, seg[1], fn, view_regs)
            if seen_pass < n_passes or close_all:
                self._close_pass(ctx, fn, strided)
        self._liveouts = saved_liveouts
        # no pass at all (scalar-only region): nothing stays open
        if self._chunk is not None and (seen_pass < n_passes or close_all):
            self._close_pass(ctx, fn, strided)

    def _compute_pass_params(self, segments: list) -> List[Optional[dict]]:
        """The per-pass parameters (extent, SEW, vl, chunks) of one
        segmentation -- the same decision the top-level lowering makes
        (T014: the matrix regions' bodies compute their own)."""
        params: List[Optional[dict]] = []
        for seg in segments:
            if seg[0] != "pass":
                params.append(None)
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
                        None, "tl.arange",
                        f"block extent {extent} does not split into "
                        f"uniform vector chunks at SEW {sew} "
                        "(mixed-chunk tails are not in the slice)")
                vl = vls.pop()
            else:
                # the largest power-of-two chunk size at or below the cap
                # that divides the extent (every iteration full)
                vl = cap
                while vl > 1 and extent % vl:
                    vl //= 2
                if extent % vl:
                    raise self._err(
                        None, "tl.arange",
                        f"block extent {extent} does not split into "
                        f"uniform vector chunks at SEW {sew}")
                chunks = tuple((vl, 1) for _ in range(extent // vl))
            params.append({"extent": extent, "sew": sew, "vl": vl,
                           "chunks": chunks})
        return params

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
        # T030: every value bound inside the pass's chunk body drops
        # BEFORE the exit bindings -- a chunk-body register does not
        # dominate the pass exit (a zero-trip pass leaves it undefined)
        # and must not survive into a later pass.  Constants and pure
        # scalar trees re-materialize at their next use; staged values
        # reload from their regions; the merge/liveout bindings below are
        # made AT the exit and stay.  The liveout vids keep their (stale)
        # body binding until _reload_liveouts reads its TYPE and rebinds
        # to the reloaded register.  (The old const-only drop left a
        # pass-1 address term live in pass 33's body -- the use-before-
        # definition the MIR verifier rejected on triton_linear_activation.)
        liveout_vids = {vid for vid, _slot in self._liveouts}
        for vid in self._staged:
            if vid in liveout_vids:
                continue
            self.values.pop(vid, None)
        for vid in list(self._pass_bound):
            if vid in liveout_vids:
                continue
            self.values.pop(vid, None)
        self._pass_bound = set()
        exit_name = self._chunk["exit"]
        ctx.switch(ctx.blocks[exit_name])
        self._bind_chunk_merges(ctx, loc)
        self._reload_liveouts(ctx, loc)
        # the next pass's entry items: this pass's accumulated count
        self._path_items = self._chunk["exit_params_items"]
        # the workspace base registers were defined inside the closed
        # loop and no longer dominate -- the next pass/staging loop
        # reloads them
        self._drop_ws_caches()
        self._chunk = None
        self._count_reg = None

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
        # T032: the result's scope names bind HERE (the value exists as a
        # staged region; uses materialize from it) -- a later region join
        # reading the name by lexical scoping found nothing when no use
        # had materialized the record yet (chunk_gdn2's nested one-armed
        # guards joining the transposed tile)
        if self._names is not None:
            for r in op.results:
                for key in r.scope_names():
                    self._names.define(key, r)
        self._layout_stagings.append({
            "op": code, "loc": str(loc),
            "results": [r.name for r in op.results],
        })

    # -- T028: the partial-axis reduction segment -----------------------------

    def _lower_partial_reduce_segment(self, ctx: _Ctx, fn: tir.Function,
                                      op: tir.Op) -> None:
        """One top-level partial-axis reduce through the staging lane: the
        operand's whole block is staged (its producing pass stored the
        bytes); a dedicated loop walks the RESULT block's flat positions,
        reducing each position's operand set (the kept axes fix the
        position, the reduced axes enumerate the set) and storing the
        reduced value to the result's staged region.

        The last-axis single-axis value form reduces each row with chunked
        vred (the running accumulator rides the chunk loop as the vred
        identity's lane 0 -- vs1[0] joins the reduction, so
        ``vred(chunk, running) = running ⊕ reduce(chunk)``); every other
        form (a non-last axis, a multi-axis set, the index forms) walks
        the operand elements scalarly -- the combine runs through the
        lane-0 vector path (the target's scalar float arithmetic form).

        16-bit float operands stage fp32-widened (the staging record's
        convention), so the reduction runs in fp32 lanes and the result
        record narrows once at its consumers -- the declared fp32-lane
        policy (T012)."""
        loc = op.loc or fn.loc
        value = op.operands[0]
        src_rec = self._staged[value.vid]
        if src_rec.get("native") and src_rec["type"].bitwidth() < 32:
            raise self._err(
                loc, "reduce",
                "a partial-axis reduction over a matrix-native staged "
                "operand is not in the lane (the record's narrow native "
                "lanes have no widening here; a located refusal, never a "
                "wrong-width combine)")
        attrs = op.attrs
        kind = attrs["kind"]
        axes = tuple(attrs["axes"])
        rank = value.rank
        shape = [int(e.value) for e in value.shape]
        if any(isinstance(e.value, tir.Sym) or not isinstance(e.value, int)
               for e in value.shape):
            raise self._err(
                loc, "reduce",
                "a partial-axis reduction needs compile-time block axes "
                "(the staging lane addresses the reduced sets by "
                "constants)")
        kept = [a for a in range(rank) if a not in axes]
        index_form = kind in ("argmax", "argmin")
        ret_idx = bool(attrs.get("return_indices"))
        if (index_form or ret_idx) and len(axes) != 1:
            raise self._err(
                loc, "reduce",
                "an index-form partial reduction over multiple axes is "
                "not in the lane (the index result has no single axis to "
                "name)")
        # the operand's row-major axis strides
        strides = [1] * rank
        for a in range(rank - 2, -1, -1):
            strides[a] = strides[a + 1] * shape[a + 1]
        red_shape = [shape[a] for a in axes]
        kept_shape = [shape[a] for a in kept]
        K = 1
        for e in kept_shape:
            K *= e
        T = 1
        for e in red_shape:
            T *= e
        if K == 0 or T == 0:
            raise self._err(loc, "reduce", "a zero-extent reduced block")
        # the result record(s): the value block (and the index block for
        # the return_indices form; the bare argmax/argmin result IS the
        # index block)
        res_value = op.results[0]
        res_rec = self._staged[res_value.vid]
        idx_rec = None
        if ret_idx:
            idx_rec = self._staged[op.results[1].vid]
        elif index_form:
            idx_rec = res_rec
        # the reduction's compute class: the staged lanes' type (fp32 for
        # widened 16-bit floats -- the declared policy) and the TIR type
        # the identities follow
        lane_sew = src_rec["lane_sew"]
        lane_kind = "float" if src_rec["type"].is_float() else \
            ("uint" if src_rec["type"].is_int_unsigned() else "int")
        lane_vtype = mir.VectorType(lane_sew, 1, lane_kind)
        lane_ty = self._tir_type_of(lane_vtype)
        if lane_ty.bitwidth() != src_rec["type"].bitwidth() \
                and not src_rec["type"].is_float():
            # an integer record widened to 32-bit lanes: the identity and
            # the combine follow the SOURCE width's semantics only when
            # the record kept it; the staging convention widens sub-32
            # integers zero/sign-agnostically (the low bits survive), so
            # the reduction follows the widened class
            pass
        vred_kind = {"sum": "sum", "max": "max", "min": "min",
                     "argmax": "max", "argmin": "min",
                     "xor_sum": "xor", "reduce_or": "or"}[kind]
        ws = self._workspace_private_reg(ctx, loc)
        src_base = ctx.emit(mir.MOp(
            "sadd", [ws, ctx.const(src_rec["offset"], mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="prb", loc=loc)], loc=loc))
        esz = src_rec["esz"]
        # the last-axis value form: chunked vred per result position
        if axes == (rank - 1,) and not index_form and not ret_idx:
            self._preduce_last_axis(ctx, fn, op, kind, vred_kind, lane_vtype,
                                    lane_ty, src_base, esz, shape[-1], K,
                                    res_rec, loc)
            self._layout_stagings.append({
                "op": f"partial-reduce-{kind}-last-axis", "loc": str(loc),
                "results": [res_value.name],
            })
            if self._names is not None:
                for r in op.results:
                    for key in r.scope_names():
                        self._names.define(key, r)
            return
        # the general form: a scalar walk over the reduced sets
        self._preduce_general(ctx, fn, op, kind, lane_vtype, lane_ty,
                              src_base, esz, strides, kept, kept_shape, K,
                              axes, red_shape, T, res_rec, idx_rec, loc)
        self._layout_stagings.append({
            "op": f"partial-reduce-{kind}", "loc": str(loc),
            "results": [r.name for r in op.results],
        })
        # T032: the staged results' scope names bind at the segment (the
        # same rule the layout segment follows)
        if self._names is not None:
            for r in op.results:
                for key in r.scope_names():
                    self._names.define(key, r)

    def _preduce_lane_scalar_type(self, lane_vtype: mir.VectorType) -> \
            mir.ScalarType:
        return mir.ScalarType(lane_vtype.sew,
                              signed=lane_vtype.kind != "uint",
                              float=lane_vtype.kind == "float")

    def _preduce_combine_scalar(self, ctx: _Ctx, a: mir.VReg, b: mir.VReg,
                                lane_vtype: mir.VectorType, kind: str,
                                loc) -> mir.VReg:
        """One combine step through the lane-0 vector path (the target's
        scalar float arithmetic form; integers ride the same shape)."""
        self._vregion(ctx, lane_vtype, loc)
        as_ = self._splat_reg(ctx, a, lane_vtype, loc)
        bs = self._splat_reg(ctx, b, lane_vtype, loc)
        if kind in ("sum", "xor_sum", "reduce_or"):
            vop = {"sum": "add", "xor_sum": "xor",
                   "reduce_or": "or"}[kind]
            reg = ctx.emit(mir.MOp(
                "vbin", [as_, bs],
                [ctx.vreg(lane_vtype, hint="prs", loc=loc)],
                attrs={"op": vop}, loc=loc))
        elif kind in ("max", "min"):
            # max: b wins when a < b; min: b wins when b < a (the floating
            # forms have no gt -- the swapped lt is the same predicate)
            lhs, rhs = ((as_, bs) if kind == "max" else (bs, as_))
            take = ctx.emit(mir.MOp(
                "vcmp", [lhs, rhs],
                [ctx.vreg(mir.MaskType(), hint="prt", loc=loc)],
                attrs={"pred": "lt", "fp": lane_vtype.kind == "float"},
                loc=loc))
            v0 = self._vmovmask_of(ctx, take, loc)
            reg = ctx.emit(mir.MOp(
                "vsel", [v0, bs, as_],
                [ctx.vreg(lane_vtype, hint="prw", loc=loc)], loc=loc))
        else:
            raise self._err(loc, "reduce", f"kind {kind!r} is not a value "
                            "combine")
        self._vregion(ctx, lane_vtype, loc)
        return self._scalarize(ctx, reg, loc)

    def _preduce_last_axis(self, ctx: _Ctx, fn: tir.Function, op: tir.Op,
                           kind: str, vred_kind: str,
                           lane_vtype: mir.VectorType, lane_ty,
                           src_base: mir.VReg, esz: int, C: int, K: int,
                           res_rec: dict, loc) -> None:
        """Reduce each contiguous row with chunked vred: the running
        accumulator rides the chunk loop as the identity operand's lane 0
        (vs1[0] joins the reduction)."""
        sty = self._preduce_lane_scalar_type(lane_vtype)
        ident = stages_mod.identity_for(
            {"xor": "xor_sum", "or": "reduce_or"}.get(vred_kind, vred_kind),
            lane_ty)
        ws = self._workspace_private_reg(ctx, loc)
        res_base = ctx.emit(mir.MOp(
            "sadd", [ws, ctx.const(res_rec["offset"], mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="prr", loc=loc)], loc=loc))
        vl = min(self.target.vlmax(lane_vtype.sew, 1), 32)
        C64 = ctx.const(C, mir.I64, loc)
        # for k in [0, K): reduce row k; store res[k]
        kframe = scalar_mod.begin_counted_loop(
            ctx, ctx.const(0, mir.I64, loc), ctx.const(K, mir.I64, loc),
            [], loc, self._tag("prk"))
        k = kframe.params[0]
        row_off = ctx.emit(mir.MOp(
            "smul", [k, C64],
            [ctx.vreg(mir.I64, hint="prko", loc=loc)], loc=loc))
        # running = splat(identity) at the lane type
        self._vregion(ctx, lane_vtype, loc)
        running = self._splat_const(ctx, ident, lane_vtype, loc,
                                    tir_type=lane_ty)
        # for c0 in [0, C) step vl: running = vred(chunk, running)
        cframe = scalar_mod.begin_counted_loop(
            ctx, ctx.const(0, mir.I64, loc), C64, [running], loc,
            self._tag("prc"))
        c0 = cframe.params[0]
        cur = cframe.params[1]
        rem = ctx.emit(mir.MOp(
            "ssub", [C64, c0],
            [ctx.vreg(mir.I64, hint="prrm", loc=loc)], loc=loc))
        rem32 = ctx.emit(mir.MOp(
            "strunc", [rem],
            [ctx.vreg(mir.I32, hint="prr3", loc=loc)], loc=loc))
        # the region's avl is the REMAINING row extent (the tail chunk
        # loads exactly what is left)
        ctx.emit(mir.MOp(
            "vsetvli", [rem32], [ctx.vreg(mir.I32, hint="prvl", loc=loc)],
            attrs={"sew": lane_vtype.sew, "lmul": lane_vtype.lmul,
                   "policy": "ta,ma"}, loc=loc))
        ctx.active_region = (lane_vtype.sew, lane_vtype.lmul, None)
        byte = ctx.emit(mir.MOp(
            "smul", [ctx.emit(mir.MOp(
                "sadd", [row_off, c0],
                [ctx.vreg(mir.I64, hint="prc0", loc=loc)], loc=loc)),
                ctx.const(esz, mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="prby", loc=loc)], loc=loc))
        addr = ctx.emit(mir.MOp(
            "sadd", [src_base, byte],
            [ctx.vreg(mir.I64, hint="prad", loc=loc)], loc=loc))
        chunk = ctx.emit(mir.MOp(
            "vunit_load", [addr],
            [ctx.vreg(lane_vtype, hint="prld", loc=loc)],
            attrs={"sew": lane_vtype.sew}, loc=loc))
        nxt = ctx.emit(mir.MOp(
            "vred", [chunk, cur],
            [ctx.vreg(lane_vtype, hint="prr2", loc=loc)],
            attrs={"kind": vred_kind}, loc=loc))
        c_next = ctx.emit(mir.MOp(
            "sadd", [c0, ctx.const(vl, mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="prcn", loc=loc)], loc=loc))
        scalar_mod.close_loop(ctx, cframe, [c_next, nxt])
        ctx.switch(cframe.exit)
        # store res[k] = lane 0 of the final running value
        self._vregion(ctx, lane_vtype, loc)
        final = self._scalarize(ctx, cframe.exit.params[1], loc)
        res_addr = ctx.emit(mir.MOp(
            "smul", [k, ctx.const(res_rec["esz"], mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="prre", loc=loc)], loc=loc))
        res_addr = ctx.emit(mir.MOp(
            "sadd", [res_base, res_addr],
            [ctx.vreg(mir.I64, hint="prra", loc=loc)], loc=loc))
        ctx.emit0(mir.MOp(
            "sstore", [res_addr, final], [],
            attrs={"width": sty.width, "offset": 0}, loc=loc))
        k_next = ctx.emit(mir.MOp(
            "sadd", [k, ctx.const(1, mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="prkn", loc=loc)], loc=loc))
        scalar_mod.close_loop(ctx, kframe, [k_next])
        ctx.switch(kframe.exit)

    def _preduce_general(self, ctx: _Ctx, fn: tir.Function, op: tir.Op,
                         kind: str, lane_vtype: mir.VectorType, lane_ty,
                         src_base: mir.VReg, esz: int, strides, kept,
                         kept_shape, K: int, axes, red_shape, T: int,
                         res_rec: dict, idx_rec, loc) -> None:
        """The general partial reduction: for every result flat position
        k, reduce the operand elements at the positions the reduced axes
        enumerate (the kept axes' contribution to the operand's flat index
        is hoisted out of the inner loop; the reduced axes' contribution
        decomposes t).  The index forms track the reduced-axis position of
        the best element under the declared tie-break."""
        sty = self._preduce_lane_scalar_type(lane_vtype)
        index_form = kind in ("argmax", "argmin")
        ret_idx = bool(op.attrs.get("return_indices"))
        left = bool(op.attrs.get("tie_break_left", True))
        ident = stages_mod.identity_for(kind, lane_ty)
        ident_idx = stages_mod._index_identity(tir.INT32)
        ws = self._workspace_private_reg(ctx, loc)
        res_base = ctx.emit(mir.MOp(
            "sadd", [ws, ctx.const(res_rec["offset"], mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="pgb", loc=loc)], loc=loc))
        idx_base = None
        if idx_rec is not None and idx_rec is not res_rec:
            idx_base = ctx.emit(mir.MOp(
                "sadd", [ws, ctx.const(idx_rec["offset"], mir.I64, loc)],
                [ctx.vreg(mir.I64, hint="pgi", loc=loc)], loc=loc))
        # the identity as a SCALAR GPR (raw IEEE bits for floats -- the
        # combine splats both sides through the lane-0 vector path, so the
        # running value rides the loop as a plain scalar)
        if sty.float:
            import struct as _struct
            if sty.width == 32:
                bits = _struct.unpack("<I", _struct.pack("<f",
                                                          float(ident)))[0]
            elif sty.width == 64:
                bits = _struct.unpack("<Q", _struct.pack("<d",
                                                          float(ident)))[0]
            else:
                raise self._err(loc, "reduce",
                                f"no float identity encoding at SEW "
                                f"{sty.width}")
            ident_scalar = ctx.const(bits, sty, loc)
        else:
            ident_scalar = ctx.const(int(ident) &
                                     ((1 << sty.width) - 1), sty, loc)
        idx_sty = mir.ScalarType(32, signed=True)
        ident_idx_scalar = ctx.const(int(ident_idx) & 0xFFFFFFFF, idx_sty,
                                     loc)
        # the kept/result strides (row-major over the kept axes)
        kept_strides = []
        acc = 1
        for e in reversed(kept_shape):
            kept_strides.append(acc)
            acc *= e
        kept_strides.reverse()
        red_strides = []
        acc = 1
        for e in reversed(red_shape):
            red_strides.append(acc)
            acc *= e
        red_strides.reverse()
        # the operand-axis stride of each kept / reduced position slot
        kept_op_strides = [strides[a] for a in kept]
        red_op_strides = [strides[a] for a in axes]
        # for k in [0, K)
        kframe = scalar_mod.begin_counted_loop(
            ctx, ctx.const(0, mir.I64, loc), ctx.const(K, mir.I64, loc),
            [], loc, self._tag("pgk"))
        k = kframe.params[0]
        # the kept axes' flat contribution (hoisted): decompose k
        # (T032: the divisor is the axis's OWN k-stride -- the [i+1]
        # indexing read the next axis's stride and collapsed every
        # multi-kept-axis form onto the major axis's elements; the
        # single-kept-axis forms never executed the division and passed)
        kept_contrib = ctx.const(0, mir.I64, loc)
        krem = k
        for i, e in enumerate(kept_shape):
            if i + 1 < len(kept_shape):
                idx_i = ctx.emit(mir.MOp(
                    "sdiv", [krem, ctx.const(kept_strides[i],
                                             mir.I64, loc)],
                    [ctx.vreg(mir.I64, hint=f"pgd{i}", loc=loc)], loc=loc))
            else:
                idx_i = krem
            kept_contrib = ctx.emit(mir.MOp(
                "sadd", [kept_contrib, ctx.emit(mir.MOp(
                    "smul", [idx_i, ctx.const(kept_op_strides[i],
                                              mir.I64, loc)],
                    [ctx.vreg(mir.I64, hint=f"pgs{i}", loc=loc)], loc=loc))],
                [ctx.vreg(mir.I64, hint=f"pgc{i}", loc=loc)], loc=loc))
            if i + 1 < len(kept_shape):
                # T032: the scalar core has no srem (SBIN_OPS; the
                # remainder is the division's complement) -- a multi-
                # kept-axis preduce decomposes k as k - idx*stride
                krem = ctx.emit(mir.MOp(
                    "ssub", [krem, ctx.emit(mir.MOp(
                        "smul", [idx_i, ctx.const(kept_strides[i],
                                                  mir.I64, loc)],
                        [ctx.vreg(mir.I64, hint=f"pgm{i}", loc=loc)],
                        loc=loc))],
                    [ctx.vreg(mir.I64, hint=f"pgr{i}", loc=loc)], loc=loc))
        # for t in [0, T): running /= element(k, t)
        tframe = scalar_mod.begin_counted_loop(
            ctx, ctx.const(0, mir.I64, loc), ctx.const(T, mir.I64, loc),
            [ident_scalar, ident_idx_scalar], loc, self._tag("pgt"))
        t = tframe.params[0]
        cur = tframe.params[1]
        cur_idx = tframe.params[2]
        # the reduced axes' flat contribution: decompose t (the same
        # own-stride rule as the kept decomposition -- T032)
        red_contrib = ctx.const(0, mir.I64, loc)
        trem = t
        red_pos = None
        for i, e in enumerate(red_shape):
            if i + 1 < len(red_shape):
                idx_i = ctx.emit(mir.MOp(
                    "sdiv", [trem, ctx.const(red_strides[i],
                                             mir.I64, loc)],
                    [ctx.vreg(mir.I64, hint=f"pgu{i}", loc=loc)], loc=loc))
            else:
                idx_i = trem
            if len(red_shape) == 1:
                red_pos = idx_i
            red_contrib = ctx.emit(mir.MOp(
                "sadd", [red_contrib, ctx.emit(mir.MOp(
                    "smul", [idx_i, ctx.const(red_op_strides[i],
                                              mir.I64, loc)],
                    [ctx.vreg(mir.I64, hint=f"pgv{i}", loc=loc)], loc=loc))],
                [ctx.vreg(mir.I64, hint=f"pgw{i}", loc=loc)], loc=loc))
            if i + 1 < len(red_shape):
                # T032: same as the kept decomposition -- no scalar srem
                trem = ctx.emit(mir.MOp(
                    "ssub", [trem, ctx.emit(mir.MOp(
                        "smul", [idx_i, ctx.const(red_strides[i],
                                                  mir.I64, loc)],
                        [ctx.vreg(mir.I64, hint=f"pgy{i}", loc=loc)],
                        loc=loc))],
                    [ctx.vreg(mir.I64, hint=f"pgx{i}", loc=loc)], loc=loc))
        flat = ctx.emit(mir.MOp(
            "sadd", [kept_contrib, red_contrib],
            [ctx.vreg(mir.I64, hint="pgf", loc=loc)], loc=loc))
        byte = ctx.emit(mir.MOp(
            "smul", [flat, ctx.const(esz, mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="pgn", loc=loc)], loc=loc))
        addr = ctx.emit(mir.MOp(
            "sadd", [src_base, byte],
            [ctx.vreg(mir.I64, hint="pgy", loc=loc)], loc=loc))
        v = ctx.emit(mir.MOp(
            "sload", [addr], [ctx.vreg(sty, hint="pgl", loc=loc)],
            attrs={"width": sty.width, "offset": 0, "ext": "sext"},
            loc=loc))
        # the combine (and the index bookkeeping for the index forms):
        # take the new element when it is strictly better (tie-break-left:
        # the FIRST occurrence of the extremum wins) or weakly better
        # (tie-break-right: the later occurrence wins on a tie)
        if index_form or ret_idx:
            self._vregion(ctx, lane_vtype, loc)
            vs = self._splat_reg(ctx, v, lane_vtype, loc)
            cs = self._splat_reg(ctx, cur, lane_vtype, loc)
            # max-forms: cur < new; min-forms: new < cur (no floating gt:
            # the swapped lt is the same predicate); "le" for right ties
            if kind in ("argmax", "max"):
                lhs, rhs = cs, vs
            else:
                lhs, rhs = vs, cs
            take = ctx.emit(mir.MOp(
                "vcmp", [lhs, rhs],
                [ctx.vreg(mir.MaskType(), hint="pgt2", loc=loc)],
                attrs={"pred": "lt" if left else "le",
                       "fp": lane_vtype.kind == "float"},
                loc=loc))
            v0 = self._vmovmask_of(ctx, take, loc)
            new_val = ctx.emit(mir.MOp(
                "vsel", [v0, vs, cs],
                [ctx.vreg(lane_vtype, hint="pgz", loc=loc)], loc=loc))
            self._vregion(ctx, lane_vtype, loc)
            new_val_s = self._scalarize(ctx, new_val, loc)
            red32 = ctx.emit(mir.MOp(
                "strunc", [red_pos if red_pos is not None else t],
                [ctx.vreg(idx_sty, hint="pgj", loc=loc)], loc=loc))
            self._vregion(ctx, mir.VectorType(32, 1, "int"), loc)
            new_idx = ctx.emit(mir.MOp(
                "vsel", [v0, self._splat_reg(ctx, red32, mir.VectorType(
                    32, 1, "int"), loc), self._splat_reg(
                        ctx, cur_idx, mir.VectorType(32, 1, "int"), loc)],
                [ctx.vreg(mir.VectorType(32, 1, "int"), hint="pgq",
                          loc=loc)], loc=loc))
            new_idx_s = self._scalarize(ctx, new_idx, loc)
        else:
            new_val_s = self._preduce_combine_scalar(ctx, cur, v,
                                                     lane_vtype, kind, loc)
            new_idx_s = cur_idx
        t_next = ctx.emit(mir.MOp(
            "sadd", [t, ctx.const(1, mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="pgtn", loc=loc)], loc=loc))
        scalar_mod.close_loop(ctx, tframe, [t_next, new_val_s, new_idx_s])
        ctx.switch(tframe.exit)
        # store the result (and the index block for the pair forms); the
        # running value is a scalar GPR already (raw bits for floats)
        final_v = tframe.exit.params[1]
        final_i = tframe.exit.params[2]
        res_addr = ctx.emit(mir.MOp(
            "smul", [k, ctx.const(res_rec["esz"], mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="pgre", loc=loc)], loc=loc))
        res_addr = ctx.emit(mir.MOp(
            "sadd", [res_base, res_addr],
            [ctx.vreg(mir.I64, hint="pgra", loc=loc)], loc=loc))
        final_scalar = final_v
        if index_form:
            # the result IS the index (the value never exists as a TIR
            # value the plan can point at)
            ctx.emit0(mir.MOp(
                "sstore", [res_addr, final_i], [],
                attrs={"width": 32, "offset": 0}, loc=loc))
        else:
            ctx.emit0(mir.MOp(
                "sstore", [res_addr, final_scalar], [],
                attrs={"width": sty.width, "offset": 0}, loc=loc))
            if ret_idx:
                i_addr = ctx.emit(mir.MOp(
                    "smul", [k, ctx.const(idx_rec["esz"], mir.I64, loc)],
                    [ctx.vreg(mir.I64, hint="pgie", loc=loc)], loc=loc))
                i_addr = ctx.emit(mir.MOp(
                    "sadd", [idx_base, i_addr],
                    [ctx.vreg(mir.I64, hint="pgia", loc=loc)], loc=loc))
                ctx.emit0(mir.MOp(
                    "sstore", [i_addr, final_i], [],
                    attrs={"width": 32, "offset": 0}, loc=loc))
        k_next = ctx.emit(mir.MOp(
            "sadd", [k, ctx.const(1, mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="pgkn", loc=loc)], loc=loc))
        scalar_mod.close_loop(ctx, kframe, [k_next])
        ctx.switch(kframe.exit)

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
        pass's lane count; the staging loops pass their own.  A redundant
        switch is skipped only when the ACTIVE region matches in (sew,
        lmul) AND avl -- the tracking makes this exact, never assumed (an
        untracked avl, or a different one, always switches)."""
        want_vl = self._vl if vl is None else vl
        if ctx.active_region == (vtype.sew, vtype.lmul, want_vl):
            return
        avl = ctx.const(want_vl, mir.I32, loc)
        ctx.emit(mir.MOp(
            "vsetvli", [avl], [ctx.vreg(mir.I32, hint="cvr", loc=loc)],
            attrs={"sew": vtype.sew, "lmul": vtype.lmul,
                   "policy": "ta,ma"}, loc=loc))
        ctx.active_region = (vtype.sew, vtype.lmul, want_vl)

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
        # T030: a NATIVE source record (an IME dot operand/result at its
        # own 8/16-bit width) cannot be read through the indexed form --
        # the narrow indexed loads crash the pinned QEMU (the probed
        # constraint); a located refusal, never a crashing emission
        for s_rec, _map in sources:
            if s_rec.get("native") and s_rec["lane_sew"] < 32:
                raise self._err(
                    loc, "layout",
                    f"a layout op over a matrix-native staged operand "
                    f"('{result.name}'s source) is not in the lane (the "
                    "record's narrow native lanes have no safe indexed "
                    "read here; a located refusal, never a crashing "
                    "emission)")
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
        # widened lane carries the value's bytes exactly).  T030: a
        # NATIVE result record (an IME dot operand staged at its own
        # narrow width) stores at ITS lane width through the UNIT-STRIDE
        # form at a scalar address (the narrow indexed forms crash the
        # pinned QEMU -- the probed e8/e16 + e64-index constraint, the
        # same rule _store_staged's native path follows): the source's
        # widened lanes narrow exactly (fp16: the RTNE round trip of the
        # exact widening; a narrow int: the low-bit view).  Without the
        # conversion the loop wrote 32-bit lanes into the 16-bit region
        # at 2-byte spacing (matmul_at_b's transposed fp16 A operand:
        # every element wrong).
        doff, _ = self._ws_scaled(ctx, idx, rec["esz"], loc, vl)
        dbase = ctx.emit(mir.MOp(
            "sadd", [ws, ctx.const(rec["offset"], mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="ldb", loc=loc)], loc=loc))
        if rec.get("native") and rec["lane_sew"] != lane_sew:
            store_val = merged
            if merged.type.kind == "float":
                store_val = self._f32_to_ff(ctx, merged, rec["type"], loc)
            else:
                store_val = self._int_narrow(ctx, merged, lane_sew,
                                             rec["type"].bitwidth(), loc)
            # the unit-stride store at the chunk's scalar base: the
            # iteration's lanes are the CONSECUTIVE flat positions
            # [elem, elem+vl) of the result region
            elem64 = scalar_mod.widen_to(ctx, elem, 64, loc)
            byteoff = ctx.emit(mir.MOp(
                "smul", [elem64, ctx.const(rec["esz"], mir.I64, loc)],
                [ctx.vreg(mir.I64, hint="lnb", loc=loc)], loc=loc))
            naddr = ctx.emit(mir.MOp(
                "sadd", [dbase, byteoff],
                [ctx.vreg(mir.I64, hint="lna", loc=loc)], loc=loc))
            nvtype = mir.VectorType(rec["lane_sew"], 1, lane_kind)
            self._vregion(ctx, nvtype, loc, vl=vl)
            ctx.emit0(mir.MOp(
                "vustore8" if rec["lane_sew"] == 8 else "vustore16",
                [naddr, store_val], [], loc=loc))
            self._restore_region(ctx, loc)
        else:
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
            return self._splat_const(ctx, ident, vtype, loc,
                                     tir_type=frame.get("tir_type"))
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
        # T032: a frame that reached this edge without its accumulator
        # initialized (the chunk opened under a different per-pass filter
        # than the one active at the close -- a block statement opening
        # the chunk mid-list, naive_attn's shape) is a plan-and-lowering
        # disagreement: refuse LOCATED, never read .type off the missing
        # register (the census crash class)
        for frame in self._chunk_merges:
            if frame["source"] == "scan":
                continue
            if frame.get("index"):
                if frame.get("acc_v") is None:
                    raise self._err(
                        loc, "merge",
                        "a partial's accumulator was never initialized "
                        "in this chunk (the plan and the lowering "
                        "disagree on the chunk's merge frames)")
            elif frame.get("acc") is None:
                raise self._err(
                    loc, "merge",
                    "a partial's accumulator was never initialized in "
                    "this chunk (the plan and the lowering disagree on "
                    "the chunk's merge frames)")
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
        # re-establish the data region: the merge combines are vector ops.
        # The blanket region stays at the pass's data SEW (the combines that
        # follow may mix widths); each frame's combine group opens its OWN
        # region at the accumulator's type (a partial at another SEW than
        # the pass -- the multi-width reduce -- must not run in the pass's
        # region; the vsetvli-region consistency invariant).
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
            self._vregion(ctx, frame["acc_v"].type if frame.get("index")
                          else frame["acc"].type, loc)
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
                if frame.get("cand_val") is not None:
                    # the fp32-lane partial of a 16-bit float sum: combine
                    # the fp32 value (the element-typed binding is rounded;
                    # the accumulator's class is the exact partial)
                    cand = self._cand_of_reg(ctx, frame["cand_val"],
                                             frame["acc"], loc)
                else:
                    cand = self._cand_of(ctx, frame["vid"], frame["acc"],
                                         loc)
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
        if reg.is_vector():
            self._vregion(ctx, reg.type, loc)
        scalar = self._scalarize(ctx, reg, loc)
        self._vregion(ctx, acc.type, loc)
        return ctx.emit(mir.MOp(
            "s2v", [scalar], [ctx.vreg(acc.type, hint="mc", loc=loc)],
            loc=loc))

    def _cand_of(self, ctx: _Ctx, vid: int, acc: mir.VReg,
                 loc) -> mir.VReg:
        """The candidate vector for one merge step: the body's current
        value of the partial, splatted to the accumulator's type (lane 0
        carries the value; the other lanes are never read).  The extract and
        the splat each open their OWN region: the partial's register, the
        accumulator and the pass region may sit at three different SEWs
        (the multi-width reduce class)."""
        reg = self.values.get(vid)
        if reg is None:
            raise self._err(loc, "merge",
                            "a partial has no lowered value at the chunk "
                            "back edge (the plan and the lowering disagree)")
        if reg.is_vector() and reg.type == acc.type:
            return reg
        if reg.is_vector():
            self._vregion(ctx, reg.type, loc)
        scalar = self._scalarize(ctx, reg, loc)
        if scalar.type.width != acc.type.sew:
            raise self._err(loc, "merge",
                            f"partial width {scalar.type.width} does not "
                            f"match the accumulator SEW {acc.type.sew}")
        self._vregion(ctx, acc.type, loc)
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

        # T030: the register cache is scoped to the dominance rule -- a
        # value lazily materialized inside one arm (a staged region's
        # reload, a re-emitted constant) does not dominate the sibling arm
        # or the code after the join, so each arm starts from the pre-if
        # cache and neither arm's bindings survive the join (the joins are
        # the only values that may cross; conv1x1_pool_fc's staged
        # materialization cached in the then-arm, reused by the else-arm's
        # back edge -- a use-before-definition the MIR verifier rejected)
        saved_values = dict(self.values)
        arm_values = []
        for block, arm in ((frame.then_block, stmt.then),
                           (frame.else_block, stmt.els)):
            self.values = dict(saved_values)
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
                reg = self._need(v, loc)
                if v.type.is_bool() and v.rank == 0:
                    # T033: a rank-0 bool join value normalizes to the
                    # scalar-bool convention (the i64 0/1 GPR) -- one arm
                    # may hold it as a floating compare's MASK (cumprod's
                    # ``finished | (last_val == 0.0)``) while the other
                    # keeps the outer GPR form; the arms must meet at one
                    # type (the T026 class at the join)
                    reg = self._scalar_bool_gpr(ctx, reg, loc)
                values.append(reg)
            scalar_mod.close_arm(ctx, frame, join_name, values)
            arm_values.append(values)
            names.pop()
        self.values = dict(saved_values)

        params = scalar_mod.join_if(ctx, frame, join_name, arm_values, loc)
        ctx.switch(ctx.blocks[join_name])
        for value, param in zip(stmt.join_results, params):
            if value.vid in self._stage_out:
                # T031: a block join crossing a pass boundary stages HERE
                # (the chunk body's top level -- the join register still
                # dominates): each chunk's lanes store to the private
                # workspace; the register stays bound for same-pass
                # consumers and _close_pass drops it (later passes
                # materialize the staged region chunk by chunk)
                self._store_staged(value, param, loc)
            self.values[value.vid] = param
            for key in value.scope_names():
                names.define(key, value)

    def _lower_loop(self, ctx: _Ctx, stmt: tir.Loop, fn: tir.Function,
                    view_regs: Dict[str, mir.VReg]) -> None:
        loc = stmt.loc or fn.loc
        names = self._names
        if self._is_matrix_region(stmt):
            self._lower_matrix_region(ctx, stmt, fn, view_regs)
            return
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
        # builder adds the induction param itself.  T014: a uniform
        # pointer recurrence's carried block becomes a SCALAR offset
        # param (the address-recurrence repair); its step is
        # re-materialized at the loop level (a body-level register would
        # not dominate the back edge).
        entries = self._classify_carried(stmt)
        carried_inits = []
        step_regs = []
        for entry in entries:
            if entry[0] == "refused":
                raise self._err(loc, "loop",
                                f"carried '{entry[1]}': {entry[3]}")
            if entry[0] == "recurrence":
                zero = ctx.const(
                    0, mir.ScalarType(entry[3].type.width, signed=True),
                    loc)
                carried_inits.append(zero)
                step_regs.append(
                    self._materialize_scalar_tree(ctx, entry[3], loc))
            else:
                carried_inits.append(self._need(entry[2], loc))
        tag = self._tag("loop")
        # T030: the register cache is scoped to the dominance rule -- a
        # value lazily materialized inside the body does not dominate the
        # exit, so the cache restores at the close (the joins bind fresh;
        # see _lower_if for the arm form)
        saved_values = dict(self.values)
        frame = scalar_mod.begin_counted_loop(
            ctx, lower, upper, carried_inits, loc, tag,
            descending=getattr(stmt, "descending", False))

        # inside the body, uses of a carried entry denote the current
        # iteration's value (the head parameter) -- the induction
        # (carried[0] <-> params[0]) included
        override: Dict[int, mir.VReg] = {
            stmt.carried[0][1].vid: frame.params[0]}
        rec_layer: Dict[int, tuple] = {}
        for entry, param in zip(entries, frame.params[1:]):
            if entry[0] == "recurrence":
                rec_layer[entry[2].vid] = (entry[2], param)
            else:
                override[entry[2].vid] = param
        self._overrides.append(override)
        self._ptr_recurrences.append(rec_layer)

        names.push()
        for (cname, init), param in zip(stmt.carried, frame.params):
            names.define(cname, init)
        self._region_depth += 1
        self._lower_statements(ctx, stmt.body.statements, fn, view_regs)
        self._region_depth -= 1
        back = []
        ind_v = names.get(stmt.carried[0][0])
        if ind_v is None:
            raise self._err(
                loc, "loop",
                f"carried '{stmt.carried[0][0]}' has no value at the "
                "body end")
        back.append(self._need(ind_v, loc))
        step_i = 0
        for entry, param in zip(entries, frame.params[1:]):
            if entry[0] == "recurrence":
                add = ctx.emit(mir.MOp(
                    "sadd", [param, step_regs[step_i]],
                    [ctx.vreg(param.type, hint="rof", loc=loc)], loc=loc))
                back.append(add)
                step_i += 1
            else:
                v = names.get(entry[1])
                if v is None:
                    raise self._err(
                        loc, "loop",
                        f"carried '{entry[1]}' has no value at the body "
                        "end")
                back.append(self._need(v, loc))
        scalar_mod.close_loop(ctx, frame, back)
        self._overrides.pop()
        self._ptr_recurrences.pop()
        names.pop()
        # the back edge's registers (the copy loop's cached workspace
        # base among them) do not dominate the exit; the body's cache
        # bindings do not either (the joins bind fresh)
        self.values = dict(saved_values)
        self._drop_ws_caches()

        ctx.switch(frame.exit)
        # the joins: position-aligned with the carried entries; a
        # recurrence entry's join keeps the frame's exit offset (the
        # layer is popped, so the join vid gets its own mapping)
        exit_rec: Dict[int, tuple] = {}
        rec_param_by_init: Dict[int, mir.VReg] = {}
        for entry, param in zip(entries, frame.exit.params[1:]):
            if entry[0] == "recurrence":
                rec_param_by_init[entry[2].vid] = param
        for (cname, init), jv, param in zip(stmt.carried, stmt.join_results,
                                            frame.exit.params):
            if init.vid in rec_param_by_init:
                exit_rec[jv.vid] = (init, rec_param_by_init[init.vid])
                continue
            if jv.vid in self._stage_out:
                # T031: a block join crossing a pass boundary stages at
                # the loop exit (the chunk body's top level); the register
                # stays bound for same-pass consumers and _close_pass
                # drops it (later passes materialize the staged region)
                self._store_staged(jv, param, loc)
            self.values[jv.vid] = param
            for key in jv.scope_names():
                names.define(key, jv)
        if exit_rec:
            self._ptr_recurrences.append(exit_rec)
        if exit_rec:
            self._ptr_recurrences.append(exit_rec)

    def _lower_while(self, ctx: _Ctx, stmt: tir.Loop, fn: tir.Function,
                     view_regs: Dict[str, mir.VReg], loc, names) -> None:
        cond_init = self._bool_scalar(ctx, self._need(stmt.cond, loc), loc)
        # carried[0] IS the condition (the frontend's while form); the
        # builder adds the cond param itself.  T014: the uniform pointer
        # recurrences become scalar offset params (see _lower_loop).
        entries = self._classify_carried(stmt)
        carried_inits = []
        step_regs = []
        for entry in entries:
            if entry[0] == "refused":
                raise self._err(loc, "while",
                                f"carried '{entry[1]}': {entry[3]}")
            if entry[0] == "recurrence":
                zero = ctx.const(
                    0, mir.ScalarType(entry[3].type.width, signed=True),
                    loc)
                carried_inits.append(zero)
                step_regs.append(
                    self._materialize_scalar_tree(ctx, entry[3], loc))
            else:
                carried_inits.append(self._need(entry[2], loc))
        tag = self._tag("while")
        # T030: the register cache is scoped to the dominance rule (see
        # _lower_loop): the body's bindings do not dominate the exit
        saved_values = dict(self.values)
        frame = scalar_mod.begin_while_loop(ctx, cond_init, carried_inits,
                                            loc, tag)

        override: Dict[int, mir.VReg] = {
            stmt.carried[0][1].vid: frame.params[0]}
        rec_layer: Dict[int, tuple] = {}
        for entry, param in zip(entries, frame.params[1:]):
            if entry[0] == "recurrence":
                rec_layer[entry[2].vid] = (entry[2], param)
            else:
                override[entry[2].vid] = param
        self._overrides.append(override)
        self._ptr_recurrences.append(rec_layer)

        names.push()
        for (cname, init), param in zip(stmt.carried, frame.params):
            names.define(cname, init)
        self._region_depth += 1
        self._lower_statements(ctx, stmt.body.statements, fn, view_regs)
        self._region_depth -= 1
        back = []
        cond_v = names.get(stmt.carried[0][0])
        if cond_v is None:
            raise self._err(
                loc, "while",
                f"carried '{stmt.carried[0][0]}' has no value at the "
                "body end")
        back.append(self._bool_scalar(ctx, self._need(cond_v, loc), loc))
        step_i = 0
        for entry, param in zip(entries, frame.params[1:]):
            if entry[0] == "recurrence":
                add = ctx.emit(mir.MOp(
                    "sadd", [param, step_regs[step_i]],
                    [ctx.vreg(param.type, hint="wof", loc=loc)], loc=loc))
                back.append(add)
                step_i += 1
            else:
                v = names.get(entry[1])
                if v is None:
                    raise self._err(
                        loc, "while",
                        f"carried '{entry[1]}' has no value at the body "
                        "end")
                back.append(self._need(v, loc))
        scalar_mod.close_loop(ctx, frame, back)
        self._overrides.pop()
        self._ptr_recurrences.pop()
        names.pop()
        # the back edge's registers (the copy loop's cached workspace
        # base among them) do not dominate the exit; the body's cache
        # bindings do not either (the joins bind fresh)
        self.values = dict(saved_values)
        self._drop_ws_caches()

        ctx.switch(frame.exit)
        exit_rec: Dict[int, tuple] = {}
        rec_param_by_init: Dict[int, mir.VReg] = {}
        for entry, param in zip(entries, frame.exit.params[1:]):
            if entry[0] == "recurrence":
                rec_param_by_init[entry[2].vid] = param
        for (cname, init), jv, param in zip(stmt.carried, stmt.join_results,
                                            frame.exit.params):
            if init.vid in rec_param_by_init:
                exit_rec[jv.vid] = (init, rec_param_by_init[init.vid])
                continue
            if jv.vid in self._stage_out:
                # T031: a block join crossing a pass boundary stages at
                # the while exit (the chunk body's top level); the register
                # stays bound for same-pass consumers and _close_pass
                # drops it (later passes materialize the staged region)
                self._store_staged(jv, param, loc)
            self.values[jv.vid] = param
            for key in jv.scope_names():
                names.define(key, jv)
        if exit_rec:
            self._ptr_recurrences.append(exit_rec)

    # -- T014: the matrix regions ------------------------------------------------

    def _dot_plan_of(self, op: tir.Op):
        """The breadth plan of one TIR dot (the planner's decision as
        data: the IME family for int8/fp16, the vector-FP32 path for
        fp32 IEEE and bf16 -- with the budget-bounded chunk record)."""
        from a100c.plan import tiles as tiles_mod
        attrs = op.attrs
        a, b = op.operands[0], op.operands[1]
        names = {}
        for key, attr in (("a_dtype", "a_dtype"), ("b_dtype", "b_dtype"),
                          ("out_dtype", "out_dtype")):
            name = _TILES_DTYPE_NAME.get(attrs.get(attr))
            if name is None:
                raise self._err(
                    op.loc, "tl.dot",
                    f"dot {attr} {attrs.get(attr)!r} is not a declared "
                    "operand dtype (F037: the corpus dtype surface)")
            names[key] = name
        extents = []
        for v, axis in ((a, 0), (a, 1), (b, 1)):
            e = v.shape[axis].value
            if not isinstance(e, int) or isinstance(e, bool):
                raise self._err(
                    op.loc, "tl.dot",
                    f"the dot's block extents must be compile-time "
                    f"(axis {axis} of the {('a', 'b')[v is b]} operand is "
                    "runtime-symbolic)")
            extents.append(e)
        desc = tiles_mod.BreadthDotDescription(
            a_dtype=names["a_dtype"], b_dtype=names["b_dtype"],
            out_dtype=names["out_dtype"],
            block_m=extents[0], block_n=extents[2], block_k=extents[1],
            acc_mode=attrs.get("acc_mode", "zero"),
            source="matrix-breadth")
        try:
            return tiles_mod.plan_dot_breadth(desc)
        except tiles_mod.TilePlanError as exc:
            raise self._err(op.loc, "tl.dot", str(exc)) from None

    def _lower_matrix_segment(self, ctx: _Ctx, fn: tir.Function,
                              op: tir.Op) -> None:
        """Emit one top-level dot as a matrix segment: the operands are
        staged regions, the result becomes a staged region, and the tile
        pipeline (IME) or the FMA path (vector) runs between the passes."""
        from a100c.lower import matrix as matrix_mod
        loc = op.loc
        a, b = op.operands[0], op.operands[1]
        acc = op.operands[2] if len(op.operands) > 2 else None
        result = op.results[0]
        plan = self._dot_plans.get(result.vid)
        if plan is None:
            raise self._err(
                loc, "tl.dot",
                "the dot has no plan (the staging analysis and the "
                "emission disagree)")
        for v, name in ((a, "input"), (b, "other"), (acc, "acc")):
            if v is not None and v.vid not in self._staged:
                raise self._err(
                    loc, "tl.dot",
                    f"the dot operand '{name}' is not staged (the "
                    "segmentation and the staging analysis disagree)")
        if result.vid not in self._staged:
            raise self._err(
                loc, "tl.dot",
                "the dot result is not staged (the segmentation and the "
                "staging analysis disagree)")
        spec = matrix_mod.ComposedDotSpec(
            plan=plan,
            a_rec=self._staged[a.vid], b_rec=self._staged[b.vid],
            acc_rec=self._staged[acc.vid] if acc is not None else None,
            res_rec=self._staged[result.vid],
            block_m=plan.block_m, block_n=plan.block_n,
            block_k=plan.block_k,
            stage_off=self._matrix_stage_off
            if plan.path == "ime" else None,
            loc=loc)
        iface = _MatrixIface(self, ctx, loc=loc)
        record = matrix_mod.emit_composed_dot(iface, spec)
        row = {"loc": str(loc)}
        row.update(plan.describe())
        row.update(record)
        self._matrix_segments.append(row)

    def _materialize_scalar_tree(self, ctx: _Ctx, v: tir.Value,
                                 loc) -> mir.VReg:
        """Re-emit a loop-invariant scalar tree at the current position.

        The uniform-recurrence step's TIR statement sits inside the loop
        body (the frontend lowers ``p += BK * s`` there), where its
        register would not dominate the back edge; the tree is pure over
        outside values (checked by the classification), so it re-emits at
        the loop level -- constants and scalar binops/comparisons only;
        anything else is a located refusal (a non-scalar or impure step
        is not a uniform recurrence)."""
        # NOTE: no register reuse here -- a value already lowered may sit
        # in a block that does not dominate this position (the two-phase
        # split re-emits regions; the reuse crossed emissions and the
        # verifier rejected the use).  Constants and pure scalar trees
        # re-materialize: the cost is one instruction each.
        prod = v.producer
        if prod is None:
            return self._need(v, loc)
        if prod.op == "const":
            return scalar_mod.lower_const(ctx, prod.attrs["value"], v.type,
                                          loc)
        if prod.op in ("program_id", "num_programs"):
            # the entry-level invariant registers (the axis decomposition
            # at the program/phase level): dominant wherever the phase's
            # own lowering could bind them, so a dropped in-pass binding
            # re-binds to the same register (T030: a pid consumed by a
            # later pass's addresses after its in-region binding dropped)
            axis = prod.attrs.get("axis")
            table = self._pid_axis_regs if prod.op == "program_id" \
                else self._np_regs
            reg = table.get(axis)
            if reg is not None:
                return reg
        if prod.op in tir.BIN_ARITH or prod.op in tir.BIN_BITWISE:
            lreg = self._materialize_scalar_tree(ctx, prod.operands[0], loc)
            rreg = self._materialize_scalar_tree(ctx, prod.operands[1], loc)
            if lreg.type.width != rreg.type.width:
                if lreg.type.width < rreg.type.width:
                    lreg = scalar_mod.widen_to(ctx, lreg, rreg.type.width,
                                               loc)
                else:
                    rreg = scalar_mod.widen_to(ctx, rreg, lreg.type.width,
                                               loc)
            return scalar_mod.lower_binop(ctx, prod, lreg, rreg, loc)
        if prod.op in tir.CMP_PREDS:
            lreg = self._materialize_scalar_tree(ctx, prod.operands[0], loc)
            rreg = self._materialize_scalar_tree(ctx, prod.operands[1], loc)
            if lreg.type.width != rreg.type.width:
                if lreg.type.width < rreg.type.width:
                    lreg = scalar_mod.widen_to(ctx, lreg, rreg.type.width,
                                               loc)
                else:
                    rreg = scalar_mod.widen_to(ctx, rreg, lreg.type.width,
                                               loc)
            return scalar_mod.lower_cmp(ctx, prod, lreg, rreg, loc)
        if prod.op in tir.MAXMIN_OPS:
            # the scalar maxmin form (the same splat/extract sequence the
            # ordinary lowering uses): a clamp term of one pass's addresses,
            # re-materialized at a later pass's use
            lhs, rhs = prod.operands
            if lhs.rank or rhs.rank:
                raise self._err(
                    loc, "ptradd",
                    f"the scalar value '{v.name}' is not a re-materializable "
                    f"scalar tree (a maxmin with a block operand)")
            lreg = self._materialize_scalar_tree(ctx, lhs, loc)
            rreg = self._materialize_scalar_tree(ctx, rhs, loc)
            vtype = mir.VectorType(
                lreg.type.width if lreg.type.width >= rreg.type.width
                else rreg.type.width, 1,
                "float" if lreg.type.float or rreg.type.float
                else ("uint" if lreg.type.signed is False
                      and rreg.type.signed is False else "int"))
            self._vregion(ctx, vtype, loc)
            ls = self._splat_reg(ctx, lreg, vtype, loc)
            rs = self._splat_reg(ctx, rreg, vtype, loc)
            res = self._vector_maxmin(ctx, prod.op, ls, rs, loc)
            self._vregion(ctx, res.type, loc)
            out = self._scalarize(ctx, res, loc)
            self._restore_region(ctx, loc)
            return out
        if prod.op == "convert" and prod.operands[0].rank == 0:
            # T032: a SCALAR convert is pure over outside values (a width
            # or float/int class change of a loop-invariant scalar --
            # chunk_gdn2's ``p += i.to(int64) * K`` recurrence step): the
            # same splat-convert-extract sequence the ordinary lowering
            # uses, re-emitted at the current position
            src, dst = prod.operands[0], v
            sreg = self._materialize_scalar_tree(ctx, src, loc)
            if sreg.is_vector():                    # pragma: no cover
                raise self._err(
                    loc, "ptradd",
                    f"the scalar value '{v.name}' is not a re-materializable "
                    f"scalar tree (a convert of a non-scalar register)")
            if src.type.is_int() and dst.type.is_int() \
                    and src.type.bitwidth() < dst.type.bitwidth():
                return scalar_mod.widen_to(
                    ctx, sreg, dst.type.bitwidth(), loc,
                    unsigned=dst.type.is_int_unsigned())
            vtype = self._vtype(src.type)
            self._vregion(ctx, vtype, loc)
            splat = self._splat_reg(ctx, sreg, vtype, loc)
            cvt = self._convert_vector(ctx, splat, src.type, dst.type, loc,
                                       rounding=prod.attrs.get("rounding"))
            if cvt.is_vector():
                self._vregion(ctx, cvt.type, loc)
            out = self._scalarize(ctx, cvt, loc)
            self._restore_region(ctx, loc)
            return out
        raise self._err(
            loc, "ptradd",
            f"the scalar value '{v.name}' is not a re-materializable "
            f"scalar tree ('{prod.op}' is not pure over outside values; "
            "the uniform-recurrence step and the cross-pass re-materialization "
            "share this rule)")

    def _lower_matrix_region(self, ctx: _Ctx, stmt, fn: tir.Function,
                             view_regs: Dict[str, mir.VReg]) -> None:
        """Lower one dot-hosting runtime region (T014): the MIR loop (or
        two-arm if) runs at the SEGMENT level -- outside any pass chunk
        loop -- and the body's statements lower through their own passes,
        matrix segments and layout segments.  Block values flow through
        the workspace (the staged carries); uniform pointer recurrences
        become scalar offset params (the address-recurrence repair)."""
        loc = stmt.loc or fn.loc
        if isinstance(stmt, tir.If):
            self._lower_matrix_if(ctx, stmt, fn, view_regs)
            return
        # T030: the dot-in-loop boundary is REPAIRED -- the staged carries'
        # back-edge copy (the loop-carried memory phi) now indexes its lanes
        # by the element counter (the reproduced defect copied elements
        # 1..vl on the second chunk, losing everything beyond the first
        # chunk's lane 0).  Dots inside runtime-bound loops lower through
        # the same staged tile pipeline as top-level dots; T014's located
        # refusal is gone.  (T028: the mixed-extent restructure without
        # dots shares this path and stays executed-compared.)
        if not isinstance(stmt, tir.Loop):  # pragma: no cover - dispatch
            raise self._err(loc, "tl.dot", "unknown matrix region form")
        names = self._names
        is_while = stmt.cond is not None
        entries = self._classify_carried(stmt)
        for entry in entries:
            if entry[0] == "refused":
                raise self._err(loc, "loop" if not is_while else "while",
                                f"carried '{entry[1]}': {entry[3]}")
            if entry[0] == "block":
                raise self._err(
                    loc, "tl.dot",
                    f"a block value ('{entry[1]}') is carried across a "
                    "dot-hosting loop without staging or a uniform "
                    "pointer recurrence: the restructured loop cannot "
                    "keep a block register (route it through the dot "
                    "pipeline's accumulator chain or stage it)")
        # the matrix region runs at the segment level: close any open pass
        if self._chunk is not None:
            self._close_pass(ctx, fn, None)
        # the MIR loop params: the induction/cond + the scalar entries +
        # one scalar offset param per recurrence entry (staged entries
        # carry through the workspace: no param)
        carried_inits: List[mir.VReg] = []
        step_regs: List[mir.VReg] = []
        param_entries: List[tuple] = []
        for entry in entries:
            if entry[0] == "recurrence":
                carried_inits.append(ctx.const(
                    0, mir.ScalarType(entry[3].type.width, signed=True),
                    loc))
                step_regs.append(
                    self._materialize_scalar_tree(ctx, entry[3], loc))
                param_entries.append(entry)
            elif entry[0] == "staged":
                continue                    # the workspace is the carry
            else:
                carried_inits.append(self._need(entry[2], loc))
                param_entries.append(entry)
        if is_while:
            cond_init = self._bool_scalar(ctx, self._need(stmt.cond, loc),
                                          loc)
            saved_values = dict(self.values)
            frame = scalar_mod.begin_while_loop(ctx, cond_init,
                                                carried_inits, loc,
                                                self._tag("mwhile"))
        else:
            if stmt.lower is None or stmt.upper is None or stmt.step is None:
                raise self._err(loc, "loop", "malformed matrix loop form")
            lower = self._need(stmt.lower, loc)
            upper = self._need(stmt.upper, loc)
            step = self._need(stmt.step, loc)
            saved_values = dict(self.values)
            frame = scalar_mod.begin_counted_loop(
                ctx, lower, upper, carried_inits, loc, self._tag("mloop"),
                descending=getattr(stmt, "descending", False))

        # inside the body, uses of a carried entry denote the current
        # iteration's value (the head parameter) -- the induction /
        # condition (carried[0] <-> params[0]) included, exactly as the
        # ordinary loop and while paths.  T030: the missing induction
        # override made every body-level use of the induction (the k-rem
        # tail bound, the hoisted induction increment) resolve to the
        # PRE-LOOP init constant -- the increment then re-computed
        # init+step every iteration, the loop never exited and the
        # pointer recurrences advanced until the loads left the buffers
        # (the multi-iteration k-loop segfault behind T014's guard).
        override: Dict[int, mir.VReg] = {
            stmt.carried[0][1].vid: frame.params[0]}
        rec_layer: Dict[int, tuple] = {}
        for entry, param in zip(param_entries, frame.params[1:]):
            if entry[0] == "recurrence":
                rec_layer[entry[2].vid] = (entry[2], param)
            else:
                override[entry[2].vid] = param
        self._overrides.append(override)
        self._ptr_recurrences.append(rec_layer)

        names.push()
        for (cname, init), param in zip(stmt.carried, frame.params):
            names.define(cname, init)
        self._region_depth += 1
        self._matrix_depth += 1
        self._region_stack.append(stmt)
        saved_items = self._path_items
        saved_sew, saved_vl = self._sew, self._vl
        try:
            body_segments = self._segment_region(
                list(stmt.body.statements))
            # the trailing SCALAR carried-name definitions hoist out of
            # the passes (the induction increment, the while condition's
            # re-evaluation and the scalar carries' final values must
            # dominate the back edge; the staged carries flow through
            # the workspace and the recurrence steps need no register,
            # so their defining statements stay where they are)
            end_names = self._tir_end_names(stmt.body.statements)
            carry_ids = set()
            head_v = end_names.get(stmt.carried[0][0])
            if head_v is not None and head_v.producer is not None:
                carry_ids.add(id(head_v.producer))
            for entry in entries:
                if entry[0] == "scalar":
                    v = end_names.get(entry[1])
                    if v is not None and v.producer is not None:
                        carry_ids.add(id(v.producer))
            if carry_ids:
                body_segments = self._hoist_carry_stmts(body_segments,
                                                        carry_ids)
            self._emit_segments_list(ctx, fn, view_regs, body_segments,
                                     close_all=True)
        finally:
            self._matrix_depth -= 1
            self._region_depth -= 1
            self._region_stack.pop()
            # the body's registers (items chaining, pass parameters, the
            # cached workspace bases) do not dominate the loop exit: the
            # post-loop segments restart from the pre-loop state
            self._path_items = saved_items
            self._sew, self._vl = saved_sew, saved_vl
            self._drop_ws_caches()

        # the back edge: the induction/cond + the scalar entries re-read
        # from the body-end name binding; the recurrence offsets advance
        # by their (invariant) step; the staged carries copy their
        # body-end region into the init's region (the loop-carried
        # memory phi)
        back = []
        head_v = names.get(stmt.carried[0][0])
        if head_v is None:
            raise self._err(loc, "matrix loop",
                            f"carried '{stmt.carried[0][0]}' has no value "
                            "at the body end")
        back.append(self._need(head_v, loc)
                    if not is_while else
                    self._bool_scalar(ctx, self._need(head_v, loc), loc))
        step_i = 0
        for entry in entries:
            if entry[0] == "recurrence":
                param = frame.params[len(back)]
                back.append(ctx.emit(mir.MOp(
                    "sadd", [param, step_regs[step_i]],
                    [ctx.vreg(param.type, hint="mof", loc=loc)], loc=loc)))
                step_i += 1
                continue
            if entry[0] == "staged":
                self._copy_staged_region(ctx, entry[3], entry[2], loc)
                continue
            v = names.get(entry[1])
            if v is None:
                raise self._err(loc, "matrix loop",
                                f"carried '{entry[1]}' has no value at the "
                                "body end")
            back.append(self._need(v, loc))
        scalar_mod.close_loop(ctx, frame, back)
        self._overrides.pop()
        self._ptr_recurrences.pop()
        names.pop()
        # the back edge's registers (the copy loop's cached workspace
        # base among them) do not dominate the exit; the body's cache
        # bindings do not either (T030: the dominance-scoped register
        # cache -- a const or staged reload materialized inside one
        # matrix region's body must not surface in a sibling region;
        # the joins and the staged aliases bind fresh)
        self.values = dict(saved_values)
        self._drop_ws_caches()

        ctx.switch(frame.exit)
        # the joins: carried[i] <-> join_results[i]; the exit params align
        # with the NON-staged entries in order (staged entries carry
        # through the workspace -- their joins alias the init's record,
        # which the back-edge copy left holding the final value)
        rec_param_by_init: Dict[int, mir.VReg] = {}
        scalar_param_by_init: Dict[int, mir.VReg] = {}
        for entry, param in zip(param_entries, frame.exit.params[1:]):
            if entry[0] == "recurrence":
                rec_param_by_init[entry[2].vid] = param
            else:
                scalar_param_by_init[entry[2].vid] = param
        exit_rec: Dict[int, tuple] = {}
        for i, ((cname, init), jv) in enumerate(zip(stmt.carried,
                                                    stmt.join_results)):
            if i == 0:
                # the induction / condition join: the exit's first param
                self.values[jv.vid] = frame.exit.params[0]
                for key in jv.scope_names():
                    names.define(key, jv)
                continue
            if init.vid in rec_param_by_init:
                exit_rec[jv.vid] = (init, rec_param_by_init[init.vid])
                continue
            if init.vid in scalar_param_by_init:
                self.values[jv.vid] = scalar_param_by_init[init.vid]
                for key in jv.scope_names():
                    names.define(key, jv)
                continue
            # a staged carry: the join aliases the init's record
            self._staged[jv.vid] = self._staged[init.vid]
            for key in jv.scope_names():
                names.define(key, jv)
        if exit_rec:
            self._ptr_recurrences.append(exit_rec)

    def _lower_matrix_if(self, ctx: _Ctx, stmt: tir.If, fn: tir.Function,
                         view_regs: Dict[str, mir.VReg]) -> None:
        """A dot-hosting (or restructured, T032) if: the region splits at
        the segment level; each arm lowers its own segments.  SCALAR joins
        keep the block-parameter join; a BLOCK join flows through the
        workspace (T032): the join's staged region is written by BOTH
        arms (each arm's close copies its final value's region in), so
        whichever arm runs leaves the join's bytes correct -- the untaken
        arm's region is never borrowed."""
        loc = stmt.loc or fn.loc
        names = self._names
        if self._chunk is not None:
            self._close_pass(ctx, fn, None)
        if stmt.cond.rank != 0:
            raise self._err(
                loc, "tl.dot",
                "a dot-hosting if with a BLOCK condition is not in the "
                "matrix lane (the block condition needs the chunk region "
                "the dot cannot share)")
        cond = self._bool_scalar(ctx, self._need(stmt.cond, loc), loc)
        tag = self._tag("mif")
        frame = scalar_mod.begin_if(ctx, cond, loc, tag)
        # T032: the block joins the analysis staged (join region + each
        # arm's final region); every other join is the scalar param form
        join_sources = getattr(self, "_if_join_sources", {}).get(id(stmt),
                                                                {})
        block_joins = {name for name in stmt.join_names
                       if name in join_sources}
        # T030: the register cache is scoped to the dominance rule (see
        # _lower_if): each arm starts from the pre-if cache and neither
        # arm's bindings survive the join
        saved_values = dict(self.values)
        arm_values = []
        for block, arm in ((frame.then_block, stmt.then),
                           (frame.else_block, stmt.els)):
            self.values = dict(saved_values)
            ctx.switch(block)
            names.push()
            self._region_depth += 1
            self._matrix_depth += 1
            saved_items = self._path_items
            saved_sew, saved_vl = self._sew, self._vl
            try:
                self._emit_segments_list(
                    ctx, fn, view_regs,
                    self._segment_region(list(arm.statements)),
                    close_all=True)
                # T032: the arm's block joins write the JOIN's region
                # here (the arm's own final values are staged; the copy
                # loop is segment-level MIR inside the arm)
                for name in sorted(block_joins):
                    jv, finals = join_sources[name]
                    final = finals[0 if arm is stmt.then else 1]
                    self._copy_staged_region(ctx, final, jv, loc,
                                             construct="if")
            finally:
                self._matrix_depth -= 1
                self._region_depth -= 1
                self._path_items = saved_items
                self._sew, self._vl = saved_sew, saved_vl
                self._drop_ws_caches()
            values = []
            for name in stmt.join_names:
                v = names.get(name)
                if v is None:
                    raise self._err(
                        loc, "if",
                        f"join '{name}' has no value at the end of an "
                        "arm (the frontend and the verifier disagree)")
                if name in block_joins:
                    continue          # the workspace region is the join
                if v.rank > 0:
                    raise self._err(
                        loc, "tl.dot",
                        f"join '{name}' is a BLOCK value defined across a "
                        "dot-hosting if without a staged join region (a "
                        "region join of staged values is not in the "
                        "matrix lane)")
                values.append(self._need(v, loc))
            scalar_mod.close_arm(ctx, frame, f"{tag}.join", values)
            arm_values.append(values)
            names.pop()
        self.values = dict(saved_values)
        params = scalar_mod.join_if(ctx, frame, f"{tag}.join", arm_values,
                                    loc)
        ctx.switch(ctx.blocks[f"{tag}.join"])
        scalar_joins = [value for name, value in zip(stmt.join_names,
                                                     stmt.join_results)
                        if name not in block_joins]
        for value, param in zip(scalar_joins, params):
            self.values[value.vid] = param
        for value in stmt.join_results:
            for key in value.scope_names():
                names.define(key, value)

    def _copy_staged_region(self, ctx: _Ctx, src: tir.Value,
                           dst: tir.Value, loc, construct: str = "tl.dot") \
            -> None:
        """The loop-carried memory phi: copy the body-end value's staged
        region into the carried init's region (both standard-convention
        regions: >= 32-bit lanes, indexed forms are safe).  T032: the
        restructured if's arm close uses the same copy (the join region
        is written by both arms)."""
        src_rec = self._staged.get(src.vid)
        dst_rec = self._staged.get(dst.vid)
        if src_rec is None or dst_rec is None:
            raise self._err(
                loc, construct,
                f"the staged carry '{dst.name}' has no staged region at "
                "the back edge (the staging analysis and the emission "
                "disagree)")
        n = src_rec.get("extent")
        if n != dst_rec.get("extent") or src_rec.get("esz") != \
                dst_rec.get("esz") or src_rec.get("lane_sew") != \
                dst_rec.get("lane_sew"):
            raise self._err(
                loc, construct,
                f"the staged carry '{dst.name}' changes shape or width "
                "across the loop (the regions must match for the "
                "back-edge copy)")
        esz = src_rec["esz"]
        sew = src_rec["lane_sew"]
        kind = "float" if src_rec["type"].is_float() else \
            ("uint" if src_rec["type"].is_int_unsigned() else "int")
        vl = min(32, self.target.vlmax(sew, 1))
        while vl > 1 and n % vl:
            vl //= 2
        if n % vl:
            vl = 1
        native = bool(src_rec.get("native"))
        ws = self._workspace_private_reg(ctx, loc)
        from_off = ctx.const(src_rec["offset"], mir.I64, loc)
        to_off = ctx.const(dst_rec["offset"], mir.I64, loc)
        # a scalar loop over n/vl chunks of vl lanes; the chunk's byte
        # offset is i*esz (i counts lanes)
        i_init = ctx.const(0, mir.I32, loc)
        n_reg = ctx.const(n, mir.I32, loc)
        vl_reg = ctx.const(vl, mir.I32, loc)
        frame = scalar_mod.begin_counted_loop(
            ctx, i_init, n_reg, [], loc, self._tag("mcarry"))
        i_p = frame.params[0]
        sb = ctx.emit(mir.MOp(
            "sadd", [ws, from_off],
            [ctx.vreg(mir.I64, hint="cvs", loc=loc)], loc=loc))
        db = ctx.emit(mir.MOp(
            "sadd", [ws, to_off],
            [ctx.vreg(mir.I64, hint="cvd", loc=loc)], loc=loc))
        if native:
            # the sub-32 native records copy through the unit-stride
            # forms at scalar addresses (the narrow indexed forms crash
            # the pinned QEMU)
            elem64 = scalar_mod.widen_to(ctx, i_p, 64, loc)
            byteoff = ctx.emit(mir.MOp(
                "smul", [elem64, ctx.const(esz, mir.I64, loc)],
                [ctx.vreg(mir.I64, hint="cvb", loc=loc)], loc=loc))
            sa = ctx.emit(mir.MOp(
                "sadd", [sb, byteoff],
                [ctx.vreg(mir.I64, hint="cva", loc=loc)], loc=loc))
            da = ctx.emit(mir.MOp(
                "sadd", [db, byteoff],
                [ctx.vreg(mir.I64, hint="cve", loc=loc)], loc=loc))
            vtype = mir.VectorType(sew, 1, kind)
            self._vregion(ctx, vtype, loc, vl=vl)
            opcode = "vuload8" if sew == 8 else "vuload16"
            val = ctx.emit(mir.MOp(
                opcode, [sa],
                [ctx.vreg(vtype, hint="cvl", loc=loc)], loc=loc))
            ctx.emit0(mir.MOp(
                "vustore8" if sew == 8 else "vustore16", [da, val], [],
                loc=loc))
            self._restore_region(ctx, loc)
        else:
            # the standard convention: indexed forms (>= 32-bit lanes)
            self._vregion(ctx, mir.VectorType(sew, 1, kind), loc, vl=vl)
            ity = mir.VectorType(32, 1, "int")
            self._vregion(ctx, ity, loc, vl=vl)
            vid = ctx.emit(mir.MOp(
                "vid", [], [ctx.vreg(ity, hint="cvd2", loc=loc)], loc=loc))
            # T030: the lane index is vid + i, with i the loop's ELEMENT
            # counter (the back edge steps i by vl).  The recorded defect
            # divided i by vl first -- the second iteration then copied
            # elements 1..vl instead of vl..2*vl-1, and the carried region
            # lost every element beyond lane 0 of chunk two (the reproduced
            # wrong-answer defect behind T014's dot-in-loop guard).
            idx = ctx.emit(mir.MOp(
                "vbinx", [vid, i_p],
                [ctx.vreg(ity, hint="cvx", loc=loc)], attrs={"op": "add"},
                loc=loc))
            scaled, _ = self._ws_scaled(ctx, idx, esz, loc, vl)
            self._vregion(ctx, mir.VectorType(sew, 1, kind), loc, vl=vl)
            val = ctx.emit(mir.MOp(
                "vloadix", [sb, scaled],
                [ctx.vreg(mir.VectorType(sew, 1, kind), hint="cvl",
                          loc=loc)],
                attrs={"eew": 64, "sew": sew}, loc=loc))
            ctx.emit0(mir.MOp(
                "vstoreix", [db, scaled, val], [],
                attrs={"eew": 64, "sew": sew}, loc=loc))
            self._restore_region(ctx, loc)
        i2 = ctx.emit(mir.MOp(
            "sadd", [i_p, vl_reg],
            [ctx.vreg(mir.I32, hint="cvn", loc=loc)], loc=loc))
        scalar_mod.close_loop(ctx, frame, [i2])
        ctx.switch(frame.exit)

    # -- one TIR op --------------------------------------------------------------
    def _lower_tir_op(self, ctx: _Ctx, op: tir.Op, fn: tir.Function,
                      view_regs: Dict[str, mir.VReg]) -> None:
        """Lower one TIR op at the current position; returns the store mask
        (the stats count source) when the op is a masked store."""
        loc = op.loc
        code = op.op

        if code == "linalg.dot":
            # the matrix lane owns the dot: the segmentation routes it to
            # a matrix segment (its own workspace tile pipeline).  Reaching
            # this dispatch means the dot sits somewhere the segmentation
            # did not restructure (inside an if-arm, a non-dot loop, ...) --
            # a located refusal, never a chunk-sliced wrong answer.
            raise self._err(
                loc, "tl.dot",
                "a dot inside this region form is not in the matrix lane "
                "(the dot needs its whole operand blocks: it must sit at "
                "a segment top level -- a dot inside an if-arm or an "
                "unrestructured loop is a located refusal)")
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
            # every float width of the corpus surface (16 included -- fp16
            # and bf16) materializes at its OWN width as the raw IEEE bits
            # under the declared constant rounding (scalar.lower_const /
            # float_const_bits: RTNE, one rounding); the consumers splat
            # those bits directly, so no re-rounding happens downstream
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
            base, offset = op.operands
            if self._recurrence_of(base) is not None:
                # the uniform pointer recurrence's back-edge step: the
                # carried pointer's value IS the recurrence (no register
                # exists); the loop's back edge advances the scalar offset
                # param instead.  The result keeps only its name binding
                # (the back edge and the join read it through the frame).
                if self._names is not None:
                    for key in op.results[0].scope_names():
                        self._names.define(key, op.results[0])
                return
            self.pointer_ops[op.results[0].vid] = op
            self.values[op.results[0].vid] = self._need(op.operands[0], loc)
            return
        if code in tir.BIN_ARITH or code in tir.BIN_BITWISE:
            lhs, rhs = op.operands
            lreg, rreg = self._need(lhs, loc), self._need(rhs, loc)
            if lreg.is_scalar() and rreg.is_scalar():
                if lreg.type.float or rreg.type.float:
                    reg = self._scalar_float_binop(ctx, op, lreg, rreg, loc)
                elif (code in tir.BIN_BITWISE
                      and op.results[0].type.is_bool()
                      and (lreg.is_mask() != rreg.is_mask())):
                    # a scalar boolean combines from both MIR bool forms
                    # (the mask of a floating comparison, the i64 0/1 of an
                    # integer comparison or constant): normalise the GPR
                    # side to the mask form so the scalar core sees one
                    # type (T026: the stop channel's `&`)
                    if lreg.is_mask():
                        rreg = self._mask_of_bool(ctx, rreg, loc)
                    else:
                        lreg = self._mask_of_bool(ctx, lreg, loc)
                    reg = ctx.emit(mir.MOp(
                        "vmand" if code == "bit.and" else "vmor",
                        [lreg, rreg],
                        [ctx.vreg(mir.MaskType(), hint="sand", loc=loc)],
                        loc=loc))
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
                    if lreg.is_mask() and rreg.is_mask() \
                            and code in ("cmp.eq", "cmp.ne"):
                        # T033: i1 == i1 / i1 != i1 over boolean blocks
                        # is exact in the mask domain (the pinned
                        # create_icmpEQ/NE on i1): lane equality is XNOR
                        # -- the xor of the masks, complemented -- and
                        # inequality is the xor itself (the 0/1 mask
                        # lanes carry the same bits the icmp would read).
                        # No element width is touched (never a .sew read
                        # off a MaskType).
                        x = ctx.emit(mir.MOp(
                            "vmxor", [lreg, rreg],
                            [ctx.vreg(mir.MaskType(), hint="mxor", loc=loc)],
                            loc=loc))
                        if code == "cmp.eq":
                            reg = ctx.emit(mir.MOp(
                                "vmnot", [x],
                                [ctx.vreg(mir.MaskType(), hint="mnot",
                                          loc=loc)],
                                loc=loc))
                        else:
                            reg = x
                        self._bind_result(op, reg)
                        return
                    if lreg.is_mask() or rreg.is_mask():
                        # a boolean-block comparison (i1 vs i1): the mask
                        # register forms are and/or/complement/xor only --
                        # any other predicate over masks is not in the
                        # slice (a located refusal, never a .sew read off
                        # a MaskType)
                        raise self._err(
                            loc, code,
                            "a boolean block comparison is not in the slice "
                            "(mask values have no element width; only "
                            "and/or/complement/xor combine them)")
                    if lreg.is_vector() and rreg.is_vector() \
                            and lreg.type != rreg.type \
                            and lreg.type.kind != "float" \
                            and rreg.type.kind != "float":
                        # the operands AGREE in TIR but ride different lane
                        # widths (the bool->int 0/1 class keeps the data SEW
                        # while the broadcast splat runs at the declared
                        # type): widen the narrower side to the wider -- the
                        # 0/1 class is exact under either extension
                        if lreg.type.sew < rreg.type.sew:
                            lreg = self._int_widen(
                                ctx, lreg, lreg.type.sew, rreg.type.sew,
                                rreg.type.kind != "uint", loc,
                                dst_kind=rreg.type.kind)
                        elif rreg.type.sew < lreg.type.sew:
                            rreg = self._int_widen(
                                ctx, rreg, rreg.type.sew, lreg.type.sew,
                                lreg.type.kind != "uint", loc,
                                dst_kind=lreg.type.kind)
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
            if operand.is_mask():
                # a boolean block operand (an i1 block value lives in a
                # mask register): the complement is the mask-register
                # form -- the vmnot MIR op, emitted vmnand.mm m, m (the
                # pinned binutils has no vmnot.mm pseudo, probed); one
                # mask in and one mask out, no element width and no
                # region switch (the T024 crash class: this path must
                # never read .sew)
                if code not in ("logical.not", "bit.invert"):
                    raise self._err(
                        loc, code,
                        f"a unary '{code}' on a boolean block is not in "
                        "the slice (masks complement; arithmetic negation "
                        "of i1 is not a source construct)")
                reg = ctx.emit(mir.MOp(
                    "vmnot", [operand],
                    [ctx.vreg(mir.MaskType(), hint="mnot", loc=loc)],
                    loc=loc))
                self._bind_result(op, reg)
                return
            vop = {"arith.fneg": "fneg", "arith.neg": "sub0",
                   "logical.not": "not", "bit.invert": "not"}.get(code)
            if vop == "sub0":
                raise self._err(loc, code,
                                "integer vector negation is not in the "
                                "slice (fneg is; neg lowers via 0-x later)")
            if vop is None:
                raise self._err(loc, code, "unary op is not in the slice")
            # the region discipline the binop/cmp paths follow: a
            # non-pass element width opens its own region and restores
            # afterwards (T013's bit.invert -- the uniform conversion's
            # ~x -- found the gap: the vunary ran at a stale setting)
            switched = self._open_region(ctx, operand.type, loc)
            reg = ctx.emit(mir.MOp(
                "vunary", [operand],
                [ctx.vreg(operand.type, hint="un", loc=loc)],
                attrs={"op": vop}, loc=loc))
            if switched:
                self._restore_region(ctx, loc)
            self._bind_result(op, reg)
            return
        if code in tir.MATH_UNARY_OPS:
            operand = self._need(op.operands[0], loc)
            if operand.is_scalar():
                reg = self._scalar_math_unary(ctx, code, operand, loc)
                self._bind_result(op, reg)
                return
            reg = self._vector_math_unary(ctx, code, operand, loc)
            self._bind_result(op, reg)
            return
        if code in tir.ABS_OPS:
            operand = self._need(op.operands[0], loc)
            if operand.is_scalar():
                # the scalar form rides the splat-compute-extract path,
                # with the region opened around the whole group (the abs
                # helper restores the pass's region on its way out; the
                # splats and the extract must not run at the stale
                # setting -- det's fp16 pivot scan found it)
                vtype = mir.VectorType(operand.type.width,
                                       1 if not operand.is_vector() else
                                       operand.type.lmul,
                                       "float" if code == "math.fabs"
                                       else operand.type.kind)
                self._vregion(ctx, vtype, loc)
                splat = self._splat_reg(ctx, operand, vtype, loc)
                res = self._vector_abs(ctx, code, splat, loc)
                self._vregion(ctx, res.type, loc)
                self._bind_result(op, self._scalarize(ctx, res, loc))
                self._restore_region(ctx, loc)
                return
            reg = self._vector_abs(ctx, code, operand, loc)
            self._bind_result(op, reg)
            return
        if code in tir.MAXMIN_OPS:
            lhs, rhs = op.operands
            lreg, rreg = self._need(lhs, loc), self._need(rhs, loc)
            if lreg.is_scalar() and rreg.is_scalar():
                vtype = mir.VectorType(
                    lreg.type.width if lreg.type.width >= rreg.type.width
                    else rreg.type.width, 1,
                    "float" if lreg.type.float or rreg.type.float
                    else ("uint" if lreg.type.signed is False
                          and rreg.type.signed is False else "int"))
                # the region opens BEFORE the splats and closes after
                # the extract (the maxmin helper restores the pass's
                # region on its way out; a 16-bit pass would run the
                # wider splats and extract at its own stale setting -- the
                # perf/max nan-index and std_reduce variance forms)
                self._vregion(ctx, vtype, loc)
                ls = self._splat_reg(ctx, lreg, vtype, loc)
                rs = self._splat_reg(ctx, rreg, vtype, loc)
                res = self._vector_maxmin(ctx, code, ls, rs, loc)
                self._vregion(ctx, res.type, loc)
                self._bind_result(op, self._scalarize(ctx, res, loc))
                self._restore_region(ctx, loc)
                return
            if lreg.is_scalar():
                lreg = self._splat_reg(
                    ctx, lreg, mir.VectorType(
                        rreg.type.sew, rreg.type.lmul, rreg.type.kind),
                    loc)
            if rreg.is_scalar():
                rreg = self._splat_reg(
                    ctx, rreg, mir.VectorType(
                        lreg.type.sew, lreg.type.lmul, lreg.type.kind),
                    loc)
            if lreg.type != rreg.type:
                raise self._err(loc, code,
                                f"maxmin operand types differ: "
                                f"{lreg.type!r} vs {rreg.type!r}")
            reg = self._vector_maxmin(ctx, code, lreg, rreg, loc)
            self._bind_result(op, reg)
            return
        if code == "math.fma":
            x, y, z = op.operands
            xreg, yreg, zreg = (self._need(x, loc), self._need(y, loc),
                                self._need(z, loc))
            if xreg.is_scalar() and yreg.is_scalar() \
                    and zreg.is_scalar():
                vtype = mir.VectorType(
                    max(r.type.width for r in (xreg, yreg, zreg)), 1,
                    "float")
                self._vregion(ctx, vtype, loc)
                xs = self._splat_reg(ctx, xreg, vtype, loc)
                ys = self._splat_reg(ctx, yreg, vtype, loc)
                zs = self._splat_reg(ctx, zreg, vtype, loc)
                reg = self._vector_fma(ctx, xs, ys, zs, loc)
                self._vregion(ctx, reg.type, loc)
                self._bind_result(op, self._scalarize(ctx, reg, loc))
                self._restore_region(ctx, loc)
                return
            vtype = xreg.type if xreg.is_vector() else \
                mir.VectorType(xreg.type.width, 1, "float")
            for name, reg in (("x", xreg), ("y", yreg), ("z", zreg)):
                if reg.is_scalar():
                    raise self._err(
                        loc, code,
                        f"a scalar {name} operand with block partners is "
                        "not splatted here (the frontend's broadcast "
                        "should have unified them)")
            reg = self._vector_fma(ctx, xreg, yreg, zreg, loc)
            self._bind_result(op, reg)
            return
        if code == "rng.philox":
            self._lower_philox(ctx, op, loc)
            return
        if code == "select.where":
            cond, x, y = op.operands
            mreg = self._need(cond, loc)
            xreg, yreg = self._need(x, loc), self._need(y, loc)
            if x.type.is_pointer() and y.type.is_pointer():
                # the pinned where allows two pointer operands: a scalar
                # pointer select in the i64 domain (the selected base
                # binds as a pointer value for the consumer ptradds --
                # the rng_dual target-pointer form)
                if not (xreg.is_scalar() and yreg.is_scalar()):
                    raise self._err(
                        loc, "select.where",
                        "a block-valued pointer select is not in this "
                        "lane (the corpus's pointer selects are scalars)")
                if not mreg.is_mask():
                    mreg = self._mask_of_bool(ctx, mreg, loc)
                v64 = mir.VectorType(64, 1, "int")
                switched = self._open_region(ctx, v64, loc)
                xs = self._splat_reg(ctx, xreg, v64, loc)
                ys = self._splat_reg(ctx, yreg, v64, loc)
                v0 = ctx.emit(mir.MOp(
                    "vmovmask", [mreg],
                    [ctx.vreg(mir.MaskType(), hint="pw0", loc=loc,
                              fixed_phys="v0")], loc=loc))
                sel = ctx.emit(mir.MOp(
                    "vsel", [v0, xs, ys],
                    [ctx.vreg(v64, hint="psel", loc=loc)], loc=loc))
                reg = self._scalarize(ctx, sel, loc)
                if switched:
                    self._restore_region(ctx, loc)
                self.values[op.results[0].vid] = reg
                if self._names is not None:
                    for key in op.results[0].scope_names():
                        self._names.define(key, op.results[0])
                return
            if xreg.is_scalar() and yreg.is_scalar():
                # a scalar select: splat both branches, select, extract
                if not mreg.is_mask():
                    mreg = self._mask_of_bool(ctx, mreg, loc)
                vtype = self._vtype(x.type)
                # the region discipline every vector path follows (the
                # scalar-select splats at the branch type -- a non-pass
                # width in fp16/bf16 passes must open its own region; the
                # rng_dual offsets select in the fp16 pass found it)
                switched = self._open_region(ctx, vtype, loc)
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
                reg = self._scalarize(ctx, sel, loc)
                if switched:
                    self._restore_region(ctx, loc)
                self._bind_result(op, reg)
                return
            v0 = ctx.emit(mir.MOp(
                "vmovmask", [mreg],
                [ctx.vreg(mir.MaskType(), hint="v0", loc=loc,
                          fixed_phys="v0")], loc=loc))
            # the region discipline the binop/cmp/unary paths follow (a
            # non-pass element width opens its own region and restores;
            # the uniform conversion's where found the gap)
            switched = self._open_region(ctx, xreg.type, loc)
            reg = ctx.emit(mir.MOp(
                "vsel", [v0, xreg, yreg],
                [ctx.vreg(xreg.type, hint="sel", loc=loc)],
                loc=loc))
            if switched:
                self._restore_region(ctx, loc)
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
            if ty.is_bool():
                # T032: a boolean block's register form is the MASK
                # (region-independent -- an e1 vector has no legal
                # vsetvli region, SEW < 8 is not a vector element
                # width).  The 0/1 splat compares against zero, exactly
                # the broadcast lane's scalar-bool form (any_kernel_dim's
                # tl.zeros([M, N], tl.int1) accumulator, staged across
                # the restructured loop).
                ity = self._idx_vtype(self._vl)
                self._vregion(ctx, ity, loc)
                splat = self._splat_reg(ctx, kreg, ity, loc)
                zero = self._splat_const(ctx, 0, ity, loc)
                reg = ctx.emit(mir.MOp(
                    "vcmp", [splat, zero],
                    [ctx.vreg(mir.MaskType(), hint="czm", loc=loc)],
                    attrs={"pred": "ne", "fp": False}, loc=loc))
                self._restore_region(ctx, loc)
                self._bind_result(op, reg)
                return
            vtype = self._vtype(ty)
            # the region discipline every vector op follows (a non-pass
            # element width opens its own region and restores -- T013:
            # tl.zeros of a narrower type inside a wider pass ran at the
            # stale setting; bucketize's int32 zeros in the fp64 pass
            # found it)
            switched = self._open_region(ctx, vtype, loc)
            reg = ctx.emit(mir.MOp(
                "s2v", [kreg],
                [ctx.vreg(vtype, hint="cst", loc=loc)], loc=loc))
            if switched:
                self._restore_region(ctx, loc)
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
        partials at the back edge.

        T028 (the block-model generalization): the reduction runs at the
        OPERAND's own width, not the pass's data SEW -- a block converted
        from fp16 data to fp32 for the reduction (mean_dim's ``.to(cdtype)``
        form) lowers in the fp16 pass with the vred in fp32 lanes.  16-bit
        float sums follow the declared fp32-lane policy (T012): the vred and
        the merge accumulator ride fp32 (bf16 has no native vector
        arithmetic; fp16 rides the single-rounding policy) and the merged
        value rounds back to the element type at the exit.  Every op group
        opens its own vsetvli region (the mixed-SEW region invariant)."""
        if self._chunk is None:
            raise self._err(loc, "reduce",
                            "a reduction outside the vector chunk region "
                            "(the operand must be a block value)")
        attrs = op.attrs
        kind = attrs["kind"]
        value = op.operands[0]
        if value.rank > 0 and len(attrs["axes"]) != value.rank:
            # a partial-axis reduction of a multi-axis block: the result is
            # a block of another shape -- the staging lane owns it (top-level
            # forms lower through _lower_partial_reduce_segment; reaching
            # here means the op sits inside a runtime region)
            raise self._err(
                loc, "reduce",
                "a partial-axis reduction inside a runtime region is not in "
                "the layout lane (the staging loop that materializes the "
                "reduced block lowers top-level only)")
        vreg = self._need(value, loc)
        if not vreg.is_vector():
            raise self._err(loc, "reduce",
                            "the reduction operand is not a block value at "
                            "this position (a scalar cannot reduce)")
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
        # the fp32-lane policy for 16-bit float sums: the vred rides fp32
        # lanes and the partial stays fp32 (the accumulator's own class);
        # the typed result narrows back at the element type
        red_reg = vreg
        red_ty = value.type
        fp32_policy = False
        if vreg.type.kind == "float" and vreg.type.sew == 16 \
                and not index_form and not ret_idx:
            red_reg = self._f16_to_f32(ctx, vreg, value.type, loc)
            red_ty = tir.FLOAT32
            fp32_policy = True
        if not index_form and not ret_idx and kind in ("max", "min") \
                and not vreg.is_mask() and vreg.type.sew < \
                value.type.bitwidth() and value.type.is_int() \
                and vreg.type.kind in ("int", "uint"):
            # a bool-converted {0,1} class riding a lane below the
            # promoted reduction type (i1 -> int32, the pinned max/min
            # promotion): widen to the declared width so the vred AND the
            # merge accumulator both ride it (the sum merge's own 0/1
            # class keeps the pass lane by design)
            red_reg = self._int_widen(
                ctx, vreg, vreg.type.sew, value.type.bitwidth(), False,
                loc, dst_kind="uint" if value.type.is_int_unsigned()
                else "int")
            red_ty = value.type
        elif not index_form and not ret_idx and not vreg.is_mask() \
                and vreg.type.kind in ("int", "uint") \
                and vreg.type.sew < value.type.bitwidth():
            # T031: a 0/1 class narrower than its MERGE ACCUMULATOR (the
            # bool backing store's e8 pass feeding an i32 sum): the
            # accumulator rides the declared width (the frame's generic
            # form), so the vred widens to it -- exact for the {0,1}
            # class, and the per-chunk partial can no longer overflow
            # the narrow lane (a 128-lane block of 1s sums past 255 in
            # e8).  The i64-promoted 0/1 SUM keeps its own design (the
            # accumulator rides the pass lane and the exit widens) --
            # its vreg already sits at the accumulator's width, so this
            # branch does not fire for it.
            frame_sew = None
            for f in self._chunk_merges:
                if f.get("vid") == op.results[0].vid \
                        and f.get("source") == "plan" and not f.get("index"):
                    frame_sew = f["vtype"].sew
                    break
            if frame_sew is not None and frame_sew > vreg.type.sew \
                    and frame_sew <= value.type.bitwidth():
                red_reg = self._int_widen(
                    ctx, vreg, vreg.type.sew, frame_sew, False, loc,
                    dst_kind="int")
                if frame_sew == value.type.bitwidth():
                    red_ty = value.type
        part = self._vred(ctx, red_reg, vred_kind, loc, tir_type=red_ty)
        if index_form or ret_idx:
            self._vregion(ctx, vreg.type, loc)
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
        # the typed per-chunk value (the element type; the fp32 partial
        # below is what the merge accumulator combines)
        if fp32_policy:
            # the fp32-lane policy's one rounding at the element type
            typed_vec = self._f32_to_ff(ctx, part, value.type, loc)
            self._vregion(ctx, typed_vec.type, loc)
            typed = self._scalarize(ctx, typed_vec, loc)
        else:
            # T033: the T009 {0,1} class (bool -> an int wider than the
            # pass SEW) can leave the vred's partial at a lane below the
            # declared result (cholesky's fp16 pass sums its i32 status
            # counts at the e16 class) when NO merge frame owns the
            # accumulator: widen the vector class exactly -- {0,1} is
            # extension-invariant -- so the extracted scalar meets the
            # declared type the frontend unified the consumers at.  A
            # plan frame keeps its own design (the T031 i64-promoted 0/1
            # sum rides the accumulator's pass lane and the EXIT widens;
            # count_nonzero's e32 accumulator with the i64 result).
            has_frame = any(
                f.get("vid") == op.results[0].vid and f.get("source") == "plan"
                and not f.get("index") for f in self._chunk_merges)
            if not part.type.kind == "float" and value.type.is_int() \
                    and part.type.sew < value.type.bitwidth() \
                    and not index_form and not ret_idx and not has_frame:
                part = self._int_widen(
                    ctx, part, part.type.sew, value.type.bitwidth(), False,
                    loc, dst_kind="uint" if value.type.is_int_unsigned()
                    else "int")
            self._vregion(ctx, part.type, loc)
            typed = self._scalarize(ctx, part, loc)
        # the fp32 partial for a 16-bit float sum rides the accumulator's
        # own class (the merge frame's vtype): record it so the back edge
        # combines the fp32 value, not the narrowed element-typed scalar
        partial_scalar = None
        if fp32_policy:
            self._vregion(ctx, part.type, loc)
            partial_scalar = self._scalarize(ctx, part, loc)
        self._bind_result(op, typed)
        if partial_scalar is not None:
            for frame in self._chunk_merges:
                if frame["source"] == "plan" and frame["vid"] == \
                        op.results[0].vid and not frame.get("index"):
                    frame["cand_val"] = partial_scalar

    def _vred(self, ctx: _Ctx, vreg: mir.VReg, kind: str,
              loc, tir_type=None) -> mir.VReg:
        """One vector reduction of the current chunk slice against the
        per-op-and-dtype identity splat (the identity rides vs1[0]).  The
        vred opens its OWN region at the operand's type: the operand may
        sit at another SEW than the pass (the multi-width reduce)."""
        ident_ty = tir_type if tir_type is not None \
            else self._tir_type_of(vreg.type)
        ident = stages_mod.identity_for(
            {"xor": "xor_sum", "or": "reduce_or"}.get(kind, kind),
            ident_ty)
        self._vregion(ctx, vreg.type, loc)
        ident_vec = self._splat_const(ctx, ident, vreg.type, loc,
                                      tir_type=ident_ty)
        return ctx.emit(mir.MOp(
            "vred", [vreg, ident_vec],
            [ctx.vreg(vreg.type, hint="vr", loc=loc)],
            attrs={"kind": kind}, loc=loc))

    def _block_index_vec(self, ctx: _Ctx, loc) -> mir.VReg:
        """The block-space indices of the current chunk's lanes (vid +
        elem -- the same index space tl.arange produces).  The i32 index
        class opens its own region (a non-32-bit pass must not run the
        index lanes at its data SEW)."""
        ity = mir.VectorType(32, 1, "int")
        self._vregion(ctx, ity, loc)
        vid = ctx.emit(mir.MOp(
            "vid", [], [ctx.vreg(ity, hint="aid", loc=loc)], loc=loc))
        return ctx.emit(mir.MOp(
            "vbinx", [vid, self._chunk["elem"]],
            [ctx.vreg(ity, hint="aidx", loc=loc)],
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
        """A mask from an i64 0/1 bool: splat and compare against zero.

        The e64 region is opened EXPLICITLY (never assumed): in a
        non-32-bit pass the hardcoded v64m1 splat would run at the active
        (stale) setting -- the rng_dual scalar-pointer select in the fp16
        pass found it."""
        vtype = mir.VectorType(64, 1, "int")
        self._vregion(ctx, vtype, loc)
        splat = ctx.emit(mir.MOp(
            "s2v", [bool_reg], [ctx.vreg(vtype, hint="bs", loc=loc)],
            loc=loc))
        zero = self._splat_const(ctx, 0, vtype, loc)
        reg = ctx.emit(mir.MOp(
            "vcmp", [splat, zero],
            [ctx.vreg(mir.MaskType(), hint="bm", loc=loc)],
            attrs={"pred": "ne", "fp": False}, loc=loc))
        self._restore_region(ctx, loc)
        return reg

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
                                             self._tag("scanp"))
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
            sixteen = self._splat_const(ctx, 16,
                                        mir.VectorType(32, lmul, "uint"),
                                        loc)
            one = self._splat_const(ctx, 1,
                                    mir.VectorType(32, lmul, "uint"), loc)
            add = ctx.emit(mir.MOp(
                "vbin", [bits, half],
                [ctx.vreg(bits.type, hint="cva", loc=loc)],
                attrs={"op": "add"}, loc=loc))
            # the round-to-nearest-even correction is the LSB OF THE HIGH
            # HALF: (bits >> 16) & 1 -- T013 found the previous form
            # adding (bits >> 1) instead (a whole half of the value rode
            # into the sum; the rng_dual bf16 store was the first
            # executed non-trivial rounding)
            high = ctx.emit(mir.MOp(
                "vbin", [bits, sixteen],
                [ctx.vreg(bits.type, hint="cvs", loc=loc)],
                attrs={"op": "srl"}, loc=loc))
            lsb = ctx.emit(mir.MOp(
                "vbin", [high, one],
                [ctx.vreg(bits.type, hint="cvl", loc=loc)],
                attrs={"op": "and"}, loc=loc))
            rounded = ctx.emit(mir.MOp(
                "vbin", [add, lsb],
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
            # then the float-kind view of the bf16 bits (through _vmovv
            # so the retyping move opens its own region -- T013: the raw
            # emit ran at the ambient region, stale when the pass's data
            # is wider than 16 bits; the rng_dual bf16 store found it)
            low = self._int_narrow(ctx, down, 32, 16, loc)
            dl = max(1, self._vl * 16 // self.target.vlen_bits)
            out = self._vmovv(ctx, low, mir.VectorType(16, dl, "float"),
                              loc)
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
                    loc, dst_kind: Optional[str] = None) -> mir.VReg:
        """Exact integer narrowing (sw -> dw, sw > dw): the register view
        retyped to the destination width (vmovv at the SOURCE's region --
        every used byte survives) and vrgather with the strided lane
        index: each destination lane takes the low half of its source
        lane.  ``dst_kind`` (T013): the destination's element kind -- an
        unsigned destination views the gathered lanes unsigned (the
        philox hi word's i64 -> u32 truncation) instead of the default
        signed view."""
        if dw >= sw:
            raise self._err(loc, "convert", "int_narrow requires sw > dw")
        factor = sw // dw
        lmul = max(1, self._vl * dw // self.target.vlen_bits)
        # the retyping view keeps the SOURCE's register-group footprint
        # (the copy at the wider-SEW region writes a group of the
        # region's LMUL -- a narrower destination group would overflow
        # into a register the allocation does not own; T013: the philox
        # hi word's i64 -> u32 truncation from an m2 source found the
        # odd-base SIGILL), then the gathered result re-views down to
        # the lanes-derived destination class
        view_lmul = max(reg.type.lmul, lmul)
        viewed = self._vmovv(ctx, reg, mir.VectorType(dw, view_lmul, "int"),
                             loc)
        self._vregion(ctx, viewed.type, loc)
        vid = ctx.emit(mir.MOp(
            "vid", [], [ctx.vreg(mir.VectorType(dw, view_lmul, "int"),
                                 hint="cvi", loc=loc)], loc=loc))
        sty = mir.ScalarType(dw, signed=True)
        kreg = ctx.const(factor, sty, loc)
        fac = ctx.emit(mir.MOp(
            "s2v", [kreg], [ctx.vreg(mir.VectorType(dw, view_lmul, "int"),
                                     hint="cvk", loc=loc)], loc=loc))
        idx = ctx.emit(mir.MOp(
            "vbin", [vid, fac],
            [ctx.vreg(mir.VectorType(dw, view_lmul, "int"), hint="cvx",
                      loc=loc)],
            attrs={"op": "mul"}, loc=loc))
        gathered = ctx.emit(mir.MOp(
            "vrgather", [viewed, idx],
            [ctx.vreg(mir.VectorType(dw, view_lmul, dst_kind or "int"),
                      hint="cvg", loc=loc)], loc=loc))
        self._restore_region(ctx, loc)
        if view_lmul == lmul:
            return gathered
        return self._vmovv(
            ctx, gathered,
            mir.VectorType(dw, lmul, dst_kind or "int"), loc)

    def _int_widen(self, ctx: _Ctx, reg: mir.VReg, sw: int, dw: int,
                   signed: bool, loc, dst_kind: Optional[str] = None) -> mir.VReg:
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
            kind = dst_kind if (dst_kind is not None and w == dw) \
                else ("int" if signed else "uint")
            want = mir.VectorType(
                w, max(1, self._vl * w // self.target.vlen_bits),
                kind)
            cur = self._vmovv(ctx, wide, want, loc) if \
                (want.sew, want.lmul) != (wide.type.sew,
                                          wide.type.lmul) else wide
        # the destination kind re-view when the last step's product
        # already matched (no _vmovv ran): an explicit view move
        if dst_kind is not None and cur.type.kind != dst_kind:
            cur = self._vmovv(ctx, cur, mir.VectorType(
                cur.type.sew, cur.type.lmul, dst_kind), loc)
        self._restore_region(ctx, loc)
        return cur

    def _convert_vector(self, ctx: _Ctx, sreg: mir.VReg, src: tir.Type,
                        dst: tir.Type, loc,
                        rounding=None) -> mir.VReg:
        """The conversion matrix over the corpus dtype surface (vector
        form, at the current pass's vl)."""
        sw, dw = src.bitwidth(), dst.bitwidth()
        # fp64 staging (buffers of fp64 tensors) is outside the executed
        # corpus surface (the 16 dead dtype dispatch branches fold at
        # specialization) -- but the INTERNAL compute width is not:
        # position_quantize (the math.round family) computes its phase in
        # fp64, which needs exactly two routes: i64 -> f64 (the block
        # index becomes the phase) and f64 -> f32 (the reduced phase
        # feeds the fp32 sin).  Everything else fp64 stays the declared
        # boundary refusal.
        if (sw == 64 and src.is_float()) or (dw == 64 and dst.is_float()):
            allowed = ((src.is_int() and dst.is_float()
                        and dw == 64)
                       or (src.is_float() and dst.is_float()
                           and sw == 64 and dw == 32)
                       or (src.is_float() and dst.is_float()
                           and sw == 32 and dw == 64))
            if not allowed:
                raise self._err(
                    loc, "convert",
                    f"fp64 conversions are not in the lane (the corpus "
                    f"dtype surface has no fp64 tensors; the internal-"
                    f"compute routes int->f64 and f64->f32 are the "
                    f"exception): {src!r} -> {dst!r}")
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
                # the widening chain extends by the SOURCE's signedness;
                # the final register view carries the DESTINATION's kind
                # (int32 -> uint64 sexts the value and views it unsigned
                # -- the randint offsets' start + arange mix found the
                # kind gap)
                return self._int_widen(
                    ctx, sreg, sw, dw, src.is_int_signed(), loc,
                    dst_kind="uint" if dst.is_int_unsigned() else "int")
            return self._int_narrow(
                ctx, sreg, sw, dw, loc,
                dst_kind="uint" if dst.is_int_unsigned() else "int")
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
            if sw == 64 and dw == 32:
                # i64 -> f32: the exact two-step route (i64 -> f64 is the
                # 53-bit RTNE rounding, f64 -> f32 the final RTNE
                # narrowing).  For |x| < 2^53 the first step is exact and
                # the result equals the single-rounding conversion; the
                # corpus's int64 values (indices, extents, counts) are
                # far below that bound.  Narrowing through i32 first
                # would WRAP -- never done.
                f64 = self._convert_vector(ctx, sreg, src, tir.FLOAT64,
                                           loc)
                return self._convert_vector(ctx, f64, tir.FLOAT64, dst,
                                            loc)
            raise self._err(
                loc, "convert",
                f"int{sw} -> f{dw} has no exact route in the conversion "
                "matrix")
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
            if sw == 32 and dw == 64:
                # T013: the exact fp32 -> fp64 widening (igamma's high-
                # precision lane): the widening convert at the SOURCE's
                # region, destination doubling SEW and LMUL (the vfwcvt
                # convention)
                self._vregion(ctx, sreg.type, loc)
                wide = ctx.emit(mir.MOp(
                    "vfwcvt", [sreg],
                    [ctx.vreg(mir.VectorType(
                        64, sreg.type.lmul * 2, "float"),
                        hint="cvd", loc=loc)],
                    attrs={"op": "ff"}, loc=loc))
                dl = max(1, self._vl * 64 // self.target.vlen_bits)
                out = self._vmovv(
                    ctx, wide, mir.VectorType(64, dl, "float"), loc)                     if wide.type.lmul != dl else wide
                self._restore_region(ctx, loc)
                return out
            if sw == 32 and dw == 16:
                return self._f32_to_ff(ctx, sreg, dst, loc,
                                       rounding=rounding)
            if sw == 64 and dw == 32:
                # T013: the internal-compute route (position_quantize's
                # fp64 phase feeding the fp32 sin): the narrowing convert
                # at the destination's region, source re-viewed at the
                # double-LMUL group the instruction reads (the f32->f16
                # convention)
                dl = max(1, self._vl * 32 // self.target.vlen_bits)
                src2 = self._vmovv(ctx, sreg,
                                   mir.VectorType(64, dl * 2, "float"),
                                   loc)
                vtype = mir.VectorType(32, dl, "float")
                self._vregion(ctx, vtype, loc)
                out = ctx.emit(mir.MOp(
                    "vfncvt", [src2],
                    [ctx.vreg(vtype, hint="cvd", loc=loc)],
                    attrs={"op": "ff"}, loc=loc))
                self._restore_region(ctx, loc)
                return out
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
            # extracts lane 0 -- and a scalar BOOL result binds the
            # scalar-bool GPR convention (the i64 0/1 the comparisons,
            # the scalar bool loads and the branch conditions speak);
            # a mask-held rank-0 bool would crash the scalar consumers
            # (the any_kernel store class: 'MaskType' has no width)
            reg = self._convert_vector(ctx, sreg, src.type, dst.type, loc,
                                       rounding=rounding)
            if op.results[0].rank > 0:
                self._bind_result(op, reg)
            else:
                if reg.is_vector():
                    self._vregion(ctx, reg.type, loc)
                self._bind_result(
                    op, self._scalar_bool_gpr(ctx, reg, loc))
            return
        if src.type.is_int() and dst.type.is_int():
            # the scalar core's own widen (and the 64->32 narrow; the
            # sub-32 narrowing rides the vector path -- the scalar core
            # has no form there).  The widened view carries the
            # DESTINATION's signedness (the philox key path widens an
            # i32 seed into the uint64 view -- the scalar binop type
            # rules must see matching operand types)
            if src.type.bitwidth() < dst.type.bitwidth():
                self._bind_result(op, scalar_mod.widen_to(
                    ctx, sreg, dst.type.bitwidth(), loc,
                    unsigned=dst.type.is_int_unsigned()))
                return
            if src.type.bitwidth() > dst.type.bitwidth() \
                    and dst.type.bitwidth() >= 32:
                self._bind_result(op, scalar_mod.narrow_to(
                    ctx, sreg, dst.type.bitwidth(), loc))
                return
        # the scalar form: splat, convert, extract.  The region is set
        # EXPLICITLY (never assumed): in a mixed-SEW pass the active
        # region at this point may be a helper's leftover (a same-width
        # signedness convert's vmovv leaves its own region behind), and a
        # stale setting would mis-execute the splat (the philox key path
        # found it); the pass's data region is restored afterwards.
        splat_ty = src.type
        vtype = self._vtype(splat_ty)
        self._vregion(ctx, vtype, loc)
        splat = self._splat_reg(ctx, sreg, vtype, loc)
        cvt = self._convert_vector(ctx, splat, src.type, dst.type, loc,
                                   rounding=rounding)
        # the extract runs at the CONVERTED value's width (the conversion
        # matrix restores the pass's data region on its way out -- a
        # mixed-SEW pass would mis-extract the wider result)
        if cvt.is_vector():
            self._vregion(ctx, cvt.type, loc)
        reg = self._scalar_bool_gpr(ctx, self._scalarize(ctx, cvt, loc),
                                    loc)
        self._restore_region(ctx, loc)
        self._bind_result(op, reg)

    # -- T013: special math functions through the real vector path --------
    def _scalar_math_unary(self, ctx: _Ctx, code: str, operand: mir.VReg,
                           loc) -> mir.VReg:
        """A scalar math operand rides the splat-compute-extract path (the
        scalar core has no transcendentals; pow_scalar_tensor's
        ``tl.floor(val0)`` is the corpus's scalar form)."""
        vtype = mir.VectorType(operand.type.width, 1, "float")
        # the region is set explicitly and restored (a non-32-bit pass
        # would otherwise run the splat at a stale setting); it is
        # RE-OPENED for the extract -- _vector_math_unary restores the
        # pass region on exit and the vextract reads at the math width
        self._vregion(ctx, vtype, loc)
        splat = self._splat_reg(ctx, operand, vtype, loc)
        res = self._vector_math_unary(ctx, code, splat, loc)
        self._vregion(ctx, vtype, loc)
        reg = self._scalarize(ctx, res, loc)
        self._restore_region(ctx, loc)
        return reg

    def _vector_math_unary(self, ctx: _Ctx, code: str, operand: mir.VReg,
                           loc) -> mir.VReg:
        """One special math function on a float vector.

        Direct RVV forms: sqrt/sqrt_rn (vfsqrt.v, exactly rounded -- the
        approximable and precise forms coincide on this target) and rsqrt
        (1/sqrt through vfsqrt + vfdiv, both exactly rounded).

        Libm calls: exp/exp2/log/log2/sin/cos/erf and floor/ceil have no
        vector form on RVV 1.0 (a recorded absence) -- the vmath op calls
        the declared sysroot's libm per element at the region's lane
        count.  fp32 uses the float functions, the fp64 internal-compute
        width the double ones.
        """
        vtype = operand.type
        if vtype.kind != "float":
            raise self._err(loc, code,
                            f"{code} requires a float vector, got "
                            f"{vtype!r}")
        switched = self._open_region(ctx, vtype, loc)
        try:
            if code in ("math.sqrt", "math.sqrt_rn"):
                reg = ctx.emit(mir.MOp(
                    "vunary", [operand],
                    [ctx.vreg(vtype, hint="sqr", loc=loc)],
                    attrs={"op": "fsqrt"}, loc=loc))
                return reg
            if code == "math.rsqrt":
                sqr = ctx.emit(mir.MOp(
                    "vunary", [operand],
                    [ctx.vreg(vtype, hint="rsq", loc=loc)],
                    attrs={"op": "fsqrt"}, loc=loc))
                if vtype.sew == 64:
                    one = self._splat_const(
                        ctx, 0x3ff0000000000000, vtype, loc)
                else:
                    one = self._splat_const(ctx, 1.0, vtype, loc)
                return ctx.emit(mir.MOp(
                    "vbin", [one, sqr],
                    [ctx.vreg(vtype, hint="rsh", loc=loc)],
                    attrs={"op": "fdiv"}, loc=loc))
            fn = {"math.exp": "exp", "math.exp2": "exp2",
                  "math.log": "log", "math.log2": "log2",
                  "math.sin": "sin", "math.cos": "cos",
                  "math.erf": "erf", "math.floor": "floor",
                  "math.ceil": "ceil"}[code]
            # fp32 -> the float functions (expf, ...); fp64 -> the double
            # forms (exp, ...) -- the internal-compute width
            if vtype.sew == 32:
                fn = fn + "f"
            vl = min(self._vl, self.target.vlmax(vtype.sew, vtype.lmul))
            return ctx.emit(mir.MOp(
                "vmath", [operand],
                [ctx.vreg(vtype, hint="mth", loc=loc)],
                attrs={"fn": fn, "sew": vtype.sew, "vl": vl}, loc=loc))
        finally:
            if switched:
                self._restore_region(ctx, loc)

    def _vector_abs(self, ctx: _Ctx, code: str, operand: mir.VReg,
                    loc) -> mir.VReg:
        """fabs (vfsgnjx) / iabs (max(x, 0-x), the signed-integer form --
        exact including INT_MIN's wrap, matching the pinned iabs)."""
        vtype = operand.type
        switched = self._open_region(ctx, vtype, loc)
        try:
            if code == "math.fabs":
                return ctx.emit(mir.MOp(
                    "vunary", [operand],
                    [ctx.vreg(vtype, hint="abs", loc=loc)],
                    attrs={"op": "fabs"}, loc=loc))
            zero = self._splat_const(ctx, 0, vtype, loc)
            neg = ctx.emit(mir.MOp(
                "vbin", [zero, operand],
                [ctx.vreg(vtype, hint="ngv", loc=loc)],
                attrs={"op": "sub"}, loc=loc))
            return ctx.emit(mir.MOp(
                "vbin", [operand, neg],
                [ctx.vreg(vtype, hint="iab", loc=loc)],
                attrs={"op": "max"}, loc=loc))
        finally:
            if switched:
                self._restore_region(ctx, loc)

    def _vector_maxmin(self, ctx: _Ctx, code: str, lreg: mir.VReg,
                       rreg: mir.VReg, loc) -> mir.VReg:
        """maximum/minimum with the NaN policy the TIR op code carries.

        Integers: vmax/vmin (signed) or vmaxu/vminu (unsigned) -- the
        exact pinned create_maxsi/maxui/minsi/minui.

        Floats: the vfmax/vfmin building block plus the NaN corrections
        the policy requires -- maxnum (NONE, the default) returns the
        OTHER operand on NaN, maximum (ALL) propagates a quiet NaN.  The
        corrections make the result independent of vfmax's own NaN
        convention (vfmax is only ever consulted when neither operand is
        NaN).
        """
        vtype = lreg.type
        switched = self._open_region(ctx, vtype, loc)
        try:
            if code.endswith("f"):
                m = ctx.emit(mir.MOp(
                    "vbin", [lreg, rreg],
                    [ctx.vreg(vtype, hint="mxm", loc=loc)],
                    attrs={"op": "fmax" if code.startswith("arith.max")
                           else "fmin"}, loc=loc))
                nanl = ctx.emit(mir.MOp(
                    "vcmp", [lreg, lreg],
                    [ctx.vreg(mir.MaskType(), hint="nl", loc=loc)],
                    attrs={"pred": "ne", "fp": True}, loc=loc))
                nanr = ctx.emit(mir.MOp(
                    "vcmp", [rreg, rreg],
                    [ctx.vreg(mir.MaskType(), hint="nr", loc=loc)],
                    attrs={"pred": "ne", "fp": True}, loc=loc))
                if code in ("arith.maxnumf", "arith.minnumf"):
                    # where(isnan(y), x, m) then where(isnan(x), y, that)
                    v0r = ctx.emit(mir.MOp(
                        "vmovmask", [nanr],
                        [ctx.vreg(mir.MaskType(), hint="m0r", loc=loc,
                                  fixed_phys="v0")], loc=loc))
                    inner = ctx.emit(mir.MOp(
                        "vsel", [v0r, lreg, m],
                        [ctx.vreg(vtype, hint="mni", loc=loc)], loc=loc))
                    v0l = ctx.emit(mir.MOp(
                        "vmovmask", [nanl],
                        [ctx.vreg(mir.MaskType(), hint="m0l", loc=loc,
                                  fixed_phys="v0")], loc=loc))
                    return ctx.emit(mir.MOp(
                        "vsel", [v0l, rreg, inner],
                        [ctx.vreg(vtype, hint="mnm", loc=loc)], loc=loc))
                # maximum/minimum: any NaN -> a quiet NaN
                any_nan = ctx.emit(mir.MOp(
                    "vmor", [nanl, nanr],
                    [ctx.vreg(mir.MaskType(), hint="mno", loc=loc)],
                    loc=loc))
                if vtype.sew == 64:
                    qnan = self._splat_const(
                        ctx, 0x7ff8000000000000, vtype, loc)
                else:
                    qnan = self._splat_const(ctx, float("nan"), vtype, loc)
                v0 = ctx.emit(mir.MOp(
                    "vmovmask", [any_nan],
                    [ctx.vreg(mir.MaskType(), hint="m0n", loc=loc,
                              fixed_phys="v0")], loc=loc))
                return ctx.emit(mir.MOp(
                    "vsel", [v0, qnan, m],
                    [ctx.vreg(vtype, hint="mxm", loc=loc)], loc=loc))
            vop = {"arith.maxsi": "max", "arith.maxui": "maxu",
                   "arith.minsi": "min", "arith.minui": "minu"}[code]
            return ctx.emit(mir.MOp(
                "vbin", [lreg, rreg],
                [ctx.vreg(vtype, hint="mm", loc=loc)],
                attrs={"op": vop}, loc=loc))
        finally:
            if switched:
                self._restore_region(ctx, loc)

    def _vector_fma(self, ctx: _Ctx, xreg: mir.VReg, yreg: mir.VReg,
                    zreg: mir.VReg, loc) -> mir.VReg:
        """x * y + z with one rounding: vfmacc accumulates into vd, which
        the emitter pre-loads with z (the MIR op carries z as its third
        operand exactly for that copy)."""
        vtype = xreg.type
        switched = self._open_region(ctx, vtype, loc)
        try:
            reg = ctx.emit(mir.MOp(
                "vfmacc", [xreg, yreg, zreg],
                [ctx.vreg(vtype, hint="fma", loc=loc)], loc=loc))
            return reg
        finally:
            if switched:
                self._restore_region(ctx, loc)

    def _lower_philox(self, ctx: _Ctx, op: tir.Op, loc) -> None:
        """The Philox4_32 round recurrence as vector ops (bit-exact: the
        umulhi/mul/xor/add chain is the pinned random.py philox_impl over
        the uint32 counter words; the key raises ride vector adds).

        Per round (counter words c0..c3, key words k0/k1):
          c0' = umulhi(B, c2) ^ c1 ^ k0
          c2' = umulhi(A, c0) ^ c3 ^ k1
          c1' = B * c2   (wrapping)
          c3' = A * c0   (wrapping)
          k0 += PHILOX_KEY_A;  k1 += PHILOX_KEY_B   (wrapping)
        with A = 0xD2511F53, B = 0xCD9E8D57, KEY_A = 0x9E3779B9,
        KEY_B = 0xBB67AE85 -- the pinned constants.
        """
        PHILOX_A, PHILOX_B = 0xD2511F53, 0xCD9E8D57
        PHILOX_KEY_A, PHILOX_KEY_B = 0x9E3779B9, 0xBB67AE85
        k0 = self._need(op.operands[0], loc)
        k1 = self._need(op.operands[1], loc)
        counters = [self._need(v, loc) for v in op.operands[2:6]]
        rounds = op.attrs["rounds"]
        for i, c in enumerate(counters):
            if not c.is_vector() or c.type.kind != "uint" \
                    or c.type.sew != 32:
                raise self._err(
                    loc, "rng.philox",
                    f"counter word {i} must be a uint32 vector, got "
                    f"{c.type!r}")
        for name, k in (("k0", k0), ("k1", k1)):
            if not k.is_scalar():
                raise self._err(
                    loc, "rng.philox",
                    f"key word {name} must be a scalar (the pinned "
                    "implementation keeps the key rank-0)")
        vtype = counters[0].type
        for i, c in enumerate(counters[1:], 1):
            if c.type != vtype:
                raise self._err(
                    loc, "rng.philox",
                    f"counter word {i} type {c.type!r} differs from "
                    f"{vtype!r}")
        switched = self._open_region(ctx, vtype, loc)
        try:
            a = self._splat_const(ctx, PHILOX_A, vtype, loc)
            b = self._splat_const(ctx, PHILOX_B, vtype, loc)
            keya = self._splat_const(ctx, PHILOX_KEY_A, vtype, loc)
            keyb = self._splat_const(ctx, PHILOX_KEY_B, vtype, loc)
            k0v = self._splat_reg(ctx, k0, vtype, loc)
            k1v = self._splat_reg(ctx, k1, vtype, loc)
            c0, c1, c2, c3 = counters
            for _r in range(rounds):
                hi_b = ctx.emit(mir.MOp(
                    "vbin", [b, c2],
                    [ctx.vreg(vtype, hint="phb", loc=loc)],
                    attrs={"op": "umulhi"}, loc=loc))
                lo_b = ctx.emit(mir.MOp(
                    "vbin", [b, c2],
                    [ctx.vreg(vtype, hint="plb", loc=loc)],
                    attrs={"op": "mul"}, loc=loc))
                hi_a = ctx.emit(mir.MOp(
                    "vbin", [a, c0],
                    [ctx.vreg(vtype, hint="pha", loc=loc)],
                    attrs={"op": "umulhi"}, loc=loc))
                lo_a = ctx.emit(mir.MOp(
                    "vbin", [a, c0],
                    [ctx.vreg(vtype, hint="pla", loc=loc)],
                    attrs={"op": "mul"}, loc=loc))
                x0 = ctx.emit(mir.MOp(
                    "vbin", [hi_b, c1],
                    [ctx.vreg(vtype, hint="px0", loc=loc)],
                    attrs={"op": "xor"}, loc=loc))
                new0 = ctx.emit(mir.MOp(
                    "vbin", [x0, k0v],
                    [ctx.vreg(vtype, hint="pn0", loc=loc)],
                    attrs={"op": "xor"}, loc=loc))
                x2 = ctx.emit(mir.MOp(
                    "vbin", [hi_a, c3],
                    [ctx.vreg(vtype, hint="px2", loc=loc)],
                    attrs={"op": "xor"}, loc=loc))
                new2 = ctx.emit(mir.MOp(
                    "vbin", [x2, k1v],
                    [ctx.vreg(vtype, hint="pn2", loc=loc)],
                    attrs={"op": "xor"}, loc=loc))
                k0v = ctx.emit(mir.MOp(
                    "vbin", [k0v, keya],
                    [ctx.vreg(vtype, hint="pk0", loc=loc)],
                    attrs={"op": "add"}, loc=loc))
                k1v = ctx.emit(mir.MOp(
                    "vbin", [k1v, keyb],
                    [ctx.vreg(vtype, hint="pk1", loc=loc)],
                    attrs={"op": "add"}, loc=loc))
                c0, c1, c2, c3 = new0, lo_b, new2, lo_a
            for i, r in enumerate(op.results):
                self.values[r.vid] = (c0, c1, c2, c3)[i]
                if self._names is not None:
                    for key in r.scope_names():
                        self._names.define(key, r)
        finally:
            if switched:
                self._restore_region(ctx, loc)

    # -- scalar float arithmetic through the vector path -------------------------
    def _scalar_float_binop(self, ctx: _Ctx, op: tir.Op, lreg: mir.VReg,
                            rreg: mir.VReg, loc) -> mir.VReg:
        # the computation type: both operands at the float width (the
        # frontend converts both sides to one type before the op)
        width = lreg.type.width if lreg.type.float else rreg.type.width
        rty = op.results[0].type
        vop = {"arith.add": "add", "arith.sub": "sub", "arith.mul": "mul",
               "arith.fdiv": "fdiv",
               "arith.div_rn": "fdiv"}.get(op.op)
        if vop is None:
            raise self._err(loc, op.op,
                            "scalar floating op is not in the vector path")
        if width == 16:
            # T031: the fp32-lane policy for 16-bit float SCALARS (the
            # vector binop's own declared policy -- the scalar path ran
            # the bits through the e16 lanes, which are FP16 on this
            # target: bf16 bits read as fp16 silently miscompiled
            # blocked_jacobi's alpha * beta).  Widen (exact), compute at
            # e32, one rounding back at the 16-bit type.
            ty16 = op.operands[0].type
            if not (ty16.is_float() and ty16.bitwidth() == 16):
                ty16 = op.operands[1].type
            v16 = mir.VectorType(16, 1, "float")
            self._vregion(ctx, v16, loc)
            ls = self._splat_reg(ctx, lreg, v16, loc)
            rs = self._splat_reg(ctx, rreg, v16, loc)
            l32 = self._f16_to_f32(ctx, ls, ty16, loc)
            r32 = self._f16_to_f32(ctx, rs, ty16, loc)
            self._vregion(ctx, l32.type, loc)
            res = ctx.emit(mir.MOp(
                "vbin", [l32, r32],
                [ctx.vreg(l32.type, hint="fb", loc=loc)],
                attrs={"op": vop}, loc=loc))
            if rty.is_float() and rty.bitwidth() == 16:
                back = self._f32_to_ff(ctx, res, rty, loc)
                out = self._scalarize(ctx, back, loc)
            else:
                out = self._scalarize(ctx, res, loc)
            self._restore_region(ctx, loc)
            return out
        vtype = mir.VectorType(width, 1, "float")
        # the region is opened EXPLICITLY (never assumed): the scalar float
        # path may run in a block whose implicit region is a non-float pass
        # (the suffix's ``summed / N`` in the fp16 pass's exit block -- the
        # mean_dim form)
        self._vregion(ctx, vtype, loc)
        ls = self._splat_reg(ctx, lreg, vtype, loc)
        rs = self._splat_reg(ctx, rreg, vtype, loc)
        res = ctx.emit(mir.MOp(
            "vbin", [ls, rs], [ctx.vreg(vtype, hint="fb", loc=loc)],
            attrs={"op": vop}, loc=loc))
        out = self._scalarize(ctx, res, loc)
        self._restore_region(ctx, loc)
        return out

    def _scalar_float_cmp(self, ctx: _Ctx, op: tir.Op, lreg: mir.VReg,
                          rreg: mir.VReg, loc) -> mir.VReg:
        """A scalar floating comparison: the result is a MASK (the i1
        scalar's MIR form; branch conditions scalarize it via vpopc, the
        where path consumes it directly)."""
        width = lreg.type.width if lreg.type.float else rreg.type.width
        if width == 16:
            # T031: the fp32-lane policy (bf16 bits at the e16 lanes are
            # fp16 -- the comparison would read the wrong values)
            ty16 = op.operands[0].type
            if not (ty16.is_float() and ty16.bitwidth() == 16):
                ty16 = op.operands[1].type
            v16 = mir.VectorType(16, 1, "float")
            self._vregion(ctx, v16, loc)
            ls = self._splat_reg(ctx, lreg, v16, loc)
            rs = self._splat_reg(ctx, rreg, v16, loc)
            l32 = self._f16_to_f32(ctx, ls, ty16, loc)
            r32 = self._f16_to_f32(ctx, rs, ty16, loc)
            self._vregion(ctx, l32.type, loc)
            reg = ctx.emit(mir.MOp(
                "vcmp", [l32, r32],
                [ctx.vreg(mir.MaskType(), hint="fm", loc=loc)],
                attrs={"pred": op.op.split(".")[1], "fp": True}, loc=loc))
            self._restore_region(ctx, loc)
            return reg
        vtype = mir.VectorType(width, 1, "float")
        self._vregion(ctx, vtype, loc)
        ls = self._splat_reg(ctx, lreg, vtype, loc)
        rs = self._splat_reg(ctx, rreg, vtype, loc)
        reg = ctx.emit(mir.MOp(
            "vcmp", [ls, rs],
            [ctx.vreg(mir.MaskType(), hint="fm", loc=loc)],
            attrs={"pred": op.op.split(".")[1], "fp": True}, loc=loc))
        self._restore_region(ctx, loc)
        return reg

    def _scalar_float_unary(self, ctx: _Ctx, code: str, operand: mir.VReg,
                            loc) -> mir.VReg:
        vtype = mir.VectorType(operand.type.width, 1, "float")
        self._vregion(ctx, vtype, loc)
        splat = self._splat_reg(ctx, operand, vtype, loc)
        res = ctx.emit(mir.MOp(
            "vunary", [splat], [ctx.vreg(vtype, hint="fu", loc=loc)],
            attrs={"op": "fneg"}, loc=loc))
        out = self._scalarize(ctx, res, loc)
        self._restore_region(ctx, loc)
        return out

    def _vbin(self, ctx: _Ctx, op: tir.Op, lreg: mir.VReg, rreg: mir.VReg,
              loc) -> mir.VReg:
        code = op.op
        if lreg.is_mask() and rreg.is_mask():
            # boolean block logic: the mask-register forms (the block
            # pointer's per-axis boundary conditions combine with and;
            # Python and/or over runtime booleans lowers to the same
            # bit.and/bit.or forms, T026)
            if code == "bit.and":
                reg = ctx.emit(mir.MOp(
                    "vmand", [lreg, rreg],
                    [ctx.vreg(mir.MaskType(), hint="mand", loc=loc)],
                    loc=loc))
                self._bind_result(op, reg)
                return reg
            if code == "bit.or":
                reg = ctx.emit(mir.MOp(
                    "vmor", [lreg, rreg],
                    [ctx.vreg(mir.MaskType(), hint="mor", loc=loc)],
                    loc=loc))
                self._bind_result(op, reg)
                return reg
            if code in ("arith.add", "arith.sub", "arith.mul"):
                # T033: int1 block arithmetic is exact in the mask domain
                # -- the pinned semantic's create_add/sub/mul on i1 is
                # addition/subtraction/multiplication mod 2, and mod 2
                # a+b == a-b == a^b while a*b == a&b (the 0/1 mask lanes
                # ARE the mod-2 residues).  The corpus form is the
                # broadcast idiom ``mask[:, None] + tl.zeros((1, 2),
                # tl.int1)`` (fused_pool_reduce); the result type is i1.
                if code == "arith.mul":
                    reg = ctx.emit(mir.MOp(
                        "vmand", [lreg, rreg],
                        [ctx.vreg(mir.MaskType(), hint="mand", loc=loc)],
                        loc=loc))
                else:
                    reg = ctx.emit(mir.MOp(
                        "vmxor", [lreg, rreg],
                        [ctx.vreg(mir.MaskType(), hint="mxor", loc=loc)],
                        loc=loc))
                self._bind_result(op, reg)
                return reg
            raise self._err(loc, code,
                            "boolean block logic beyond and/or/xor is not "
                            "in the slice (the boundary conditions combine "
                            "with & and |)")
        if (lreg.is_mask() or rreg.is_mask()) and op.results \
                and op.results[0].type.is_bool() and op.results[0].rank == 0:
            # a scalar boolean combines from both MIR bool forms -- the
            # mask (a floating comparison) and the GPR 0/1 (an integer
            # comparison): normalise the GPR side to the mask form (T026:
            # good_diag & (bad_vals == 0))
            if lreg.is_mask():
                rreg = self._mask_of_bool(ctx, rreg, loc)
            else:
                lreg = self._mask_of_bool(ctx, lreg, loc)
            if code == "bit.and":
                reg = ctx.emit(mir.MOp(
                    "vmand", [lreg, rreg],
                    [ctx.vreg(mir.MaskType(), hint="mand", loc=loc)],
                    loc=loc))
                self._bind_result(op, reg)
                return reg
            if code == "bit.or":
                reg = ctx.emit(mir.MOp(
                    "vmor", [lreg, rreg],
                    [ctx.vreg(mir.MaskType(), hint="mor", loc=loc)],
                    loc=loc))
                self._bind_result(op, reg)
                return reg
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
               "bit.shl": "sll",
               # T013: the precise division lowers to the same exactly-
               # rounded vfdiv (the codes stay distinct in TIR so an
               # approximating fast path can never silently claim it)
               "arith.div_rn": "fdiv"}.get(code)
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
    def _recurrence_byte_adjust(self, ctx: _Ctx, ptr: tir.Value,
                               pointee: tir.Type, loc) -> mir.VReg:
        """The uniform pointer recurrences' byte adjustment of one access:
        every active layer over the pointer's chain adds its scalar
        offset (in elements) scaled by the pointee size.  The WIDE
        (unit-stride) access path bypasses _address_of, so it must apply
        the same adjustment the indexed path does (the pre-repair
        miscompile: the proof's scalar terms never see the carried
        step)."""
        esz = 1 if pointee.is_bool() else pointee.bitwidth() // 8
        rec_offsets: List[mir.VReg] = []
        node = ptr
        while True:
            rec_offsets.extend(self._active_recurrence_offsets(node))
            if node.producer is None or node.producer.op != "ptradd":
                break
            node = node.producer.operands[0]
        if not rec_offsets:
            return None
        total = ctx.const(0, mir.I64, loc)
        for extra in rec_offsets:
            wide = scalar_mod.widen_to(ctx, extra, 64, loc) \
                if extra.type.width != 64 else extra
            scaled = ctx.emit(mir.MOp(
                "smul", [wide, ctx.const(esz, mir.I64, loc)],
                [ctx.vreg(mir.I64, hint="rwb", loc=loc)], loc=loc))
            total = ctx.emit(mir.MOp(
                "sadd", [total, scaled],
                [ctx.vreg(mir.I64, hint="rwa", loc=loc)], loc=loc))
        return total

    def _address_of(self, ctx: _Ctx, ptr: tir.Value, loc):
        """Resolve one TIR pointer value to (base reg, offset reg, pointee).

        A ptradd chain (``p + a + b + off`` lowers left-associatively in
        the frontend) is flattened into ONE whole-tree sum: base + (a + b +
        off) in one expression -- never accumulated one dimension at a
        time (FE-ADDRESS-EXPRESSIONS, IR-LOWERING-CONTRACT).  A bare
        pointer parameter (``tl.load(w_ptr)``) is the zero-offset form.

        T014 (the uniform pointer-recurrence repair): when the chain
        passes a loop-carried pointer block whose back edge is a uniform
        ``p += step``, the carried value has no register (a vector of
        addresses cannot be an MIR loop param alongside the whole-tree
        scalar-base address form).  Every active recurrence layer's
        scalar offset param is added to the tree sum instead -- the
        carried pointer at iteration i addresses exactly ``tree + i *
        step``, which is what the source recurrence computes.  A JOIN
        use of a carried pointer resolves through the frame's init value
        (the static tree) plus the exit offset register.
        """
        # a join (or bare) use of a carried pointer: the static chain is
        # the frame's init value; the walk below adds the offsets
        join_offset: Optional[mir.VReg] = None
        if ptr.producer is None or \
                ptr.producer.op not in ("ptradd", "bitcast", "hint",
                                        "select.where"):
            rec = self._recurrence_of(ptr)
            if rec is not None:
                ptr, join_offset = rec[0], rec[1]
        offsets = []
        rec_offsets: List[mir.VReg] = []
        node = ptr
        while True:
            rec_offsets.extend(self._active_recurrence_offsets(node))
            if node.producer is None:
                break
            if node.producer.op == "ptradd":
                base_value, offset_value = node.producer.operands
                offsets.append(offset_value)
                node = base_value
                continue
            if node.producer.op in ("reshape", "realize"):
                # T032: shape metadata on a POINTER block (``p[None, :]``
                # -- the expand_dims form argmin_tiled's tile addressing
                # uses) preserves the pointer value; the whole-tree walk
                # follows through to the real chain root
                node = node.producer.operands[0]
                continue
            break
        # T030: the join-resolved layer's own offset register (the loop's
        # EXIT param) joins the tree sum here -- the walk above only sees
        # layers keyed by the CHAIN's vids, and the exit layer is keyed by
        # the JOIN's vid.  Without it, the store after a matrix region
        # addressed the pre-loop tile: matmul_k32_persistent_n_2stage's
        # final store overwrote tile 0 with tile 1's data and left the
        # last tile unwritten.  (The membership check keeps a bare
        # carried pointer -- whose head param the walk already collected
        # -- from double-counting.)
        if join_offset is not None and join_offset not in rec_offsets:
            rec_offsets.append(join_offset)
        if node.producer is not None \
                and node.producer.op not in ("bitcast", "hint",
                                             "select.where"):
            raise self._err(loc, ptr.name,
                            f"pointer '{ptr.name}' is not a ptradd-formed "
                            "address (the slice's whole-tree address form)")
        if node.producer is not None \
                and node.producer.op == "select.where":
            if not node.type.is_pointer():
                raise self._err(loc, ptr.name,
                                f"pointer '{ptr.name}' selects a non-pointer "
                                "root (a malformed address)")
        base_reg = self._need(node, loc)
        if not offsets:
            offset_reg = ctx.const(0, mir.I32, loc)
        else:
            # T029: the ptradd chain's addressing space (the pointer
            # block's shape) is the consumer shape for the staged offset
            # reads -- a consumer that broadcasts an offset block's
            # extent-1 axes maps its staged reads through the block's
            # own axes
            offset_reg = self._sum_offsets(ctx, list(reversed(offsets)),
                                           loc, consumer_shape=ptr.shape)
        for extra in rec_offsets:
            if offset_reg.is_vector():
                # the tree's index class is a vector: the scalar offset
                # adds lane-wise (the region discipline of _sum_offsets);
                # a wider scalar widens the lane class first (T029: the
                # sum never refuses on the offset width)
                if extra.type.width > offset_reg.type.sew:
                    offset_reg = self._widen_index_class(
                        ctx, offset_reg, extra.type.width, loc)
                switched = self._open_region(ctx, offset_reg.type, loc)
                try:
                    offset_reg = ctx.emit(mir.MOp(
                        "vbinx", [offset_reg, extra],
                        [ctx.vreg(offset_reg.type, hint="rof",
                                  loc=loc)],
                        attrs={"op": "add"}, loc=loc))
                finally:
                    if switched:
                        self._restore_region(ctx, loc)
            else:
                if offset_reg.type.width < extra.type.width:
                    offset_reg = scalar_mod.widen_to(ctx, offset_reg,
                                                     extra.type.width, loc)
                elif extra.type.width < offset_reg.type.width:
                    extra = scalar_mod.widen_to(ctx, extra,
                                                offset_reg.type.width,
                                                loc)
                offset_reg = ctx.emit(mir.MOp(
                    "sadd", [offset_reg, extra],
                    [ctx.vreg(offset_reg.type, hint="rof", loc=loc)],
                    loc=loc))
        return base_reg, offset_reg, node.type.pointee

    def _widen_index_class(self, ctx: _Ctx, reg: mir.VReg, width: int,
                           loc) -> mir.VReg:
        """Widen one index-class vector to ``width`` (vi32 -> vi64): the
        per-lane SIGNED extension through the legalized widening form,
        LMUL doubled, executed in the source's own region (the
        ``materialize_address`` convention).

        T029 (the ptradd width repair): a 64-bit scalar offset meeting a
        32-bit vector index widens the lane class -- never a refusal on
        the width.  The semantics are the source's own promotion point:
        the i32 lanes have already wrapped in i32 (``a wrapping index is
        never widened before the wrap``), and sign extension distributes
        over the remaining modular sum (sext((a+b) mod 2^32) ==
        sext(a) + sext(b) mod 2^64), so summing the widened lanes at 64
        bits equals the per-step pointer adds the source performs.
        """
        if not reg.is_vector() or reg.type.sew * 2 != width or width != 64:
            raise self._err(
                loc, "ptradd",
                f"cannot widen the vector index class {reg.type!r} to "
                f"width {width} (only the vi32 -> vi64 doubling is "
                "lowered)")
        lmul = reg.type.lmul * 2
        if lmul not in (1, 2, 4, 8):
            raise self._err(
                loc, "ptradd",
                f"the widened index class needs LMUL {lmul} "
                "(outside 1..8)")
        # the widening executes in the SOURCE's own region (the
        # materialize_address form: result kind "int", mode sext -- the
        # pinned ptradd semantics sign-extend i32 offsets); the caller's
        # add re-opens the widened class itself
        switched = self._open_region(ctx, reg.type, loc)
        try:
            return ctx.emit(mir.MOp(
                "vwiden", [reg],
                [ctx.vreg(mir.VectorType(64, lmul, "int"), hint="oix",
                          loc=loc)],
                attrs={"mode": "sext"}, loc=loc))
        finally:
            if switched:
                self._restore_region(ctx, loc)

    def _sum_offsets(self, ctx: _Ctx, values, loc,
                     consumer_shape=None) -> mir.VReg:
        """Sum the flattened ptradd offsets, left-associatively, preserving
        each value's width and shape (modular i32 arithmetic associates).
        Index-class (i64/EMUL-2) accumulators open their own region for
        the vector adds and restore the data region after.

        T029: a wider scalar (or a wider-SEW vector) operand widens the
        vector lane class to the operand's width instead of refusing --
        the equivalent addressing semantics at the source's own promotion
        point (see :meth:`_widen_index_class`).  ``consumer_shape`` is
        the addressing space's shape (the pointer block's), threading
        the broadcast-axis map into the staged offset reads."""
        if len(values) == 1:
            return self._need(values[0], loc, consumer_shape)
        acc = self._need(values[0], loc, consumer_shape)
        for v in values[1:]:
            reg = self._need(v, loc, consumer_shape)
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
                    acc = self._widen_index_class(ctx, acc,
                                                  reg.type.width, loc)
                switched = self._open_region(ctx, acc.type, loc)
                acc = ctx.emit(mir.MOp(
                    "vbinx", [acc, reg],
                    [ctx.vreg(acc.type, hint="os", loc=loc)],
                    attrs={"op": "add"}, loc=loc))
                if switched:
                    self._restore_region(ctx, loc)
            elif acc.is_scalar() and reg.is_vector():
                if acc.type.width > reg.type.sew:
                    reg = self._widen_index_class(ctx, reg,
                                                  acc.type.width, loc)
                    switched = self._open_region(ctx, reg.type, loc)
                    acc = ctx.emit(mir.MOp(
                        "vbinx", [reg, acc],
                        [ctx.vreg(reg.type, hint="os", loc=loc)],
                        attrs={"op": "add"}, loc=loc))
                    if switched:
                        self._restore_region(ctx, loc)
                    continue
                switched = self._open_region(ctx, reg.type, loc)
                acc = ctx.emit(mir.MOp(
                    "vbinx", [reg, acc],
                    [ctx.vreg(reg.type, hint="os", loc=loc)],
                    attrs={"op": "add"}, loc=loc))
                if switched:
                    self._restore_region(ctx, loc)
            else:
                if acc.type != reg.type:
                    if acc.type.sew != reg.type.sew:
                        # T029: mixed-SEW vector offsets (a widened i64
                        # class meeting a fresh vi32 term): widen the
                        # narrower lane class, then add at the wider SEW
                        if acc.type.sew < reg.type.sew:
                            acc = self._widen_index_class(
                                ctx, acc, reg.type.sew, loc)
                        else:
                            reg = self._widen_index_class(
                                ctx, reg, acc.type.sew, loc)
                    if acc.type.sew == reg.type.sew \
                            and acc.type.lmul != reg.type.lmul:
                        # T032: a same-SEW lane-GROUP mismatch (a staged
                        # e64 term materialized at its own used-bits
                        # class m1 meeting a vwiden-produced m2 term --
                        # vwiden architecturally doubles the group):
                        # view the narrower group as the wider one (the
                        # register-view move is avl-capped, both groups
                        # hold the pass's lanes)
                        if acc.type.lmul < reg.type.lmul:
                            acc = self._vmovv(ctx, acc, reg.type, loc)
                        else:
                            reg = self._vmovv(ctx, reg, acc.type, loc)
                    if acc.type != reg.type:
                        # a same-SEW kind mismatch (a different lane
                        # class) is a different construct and keeps
                        # its located refusal
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
                # the guarded scalar load (the pinned masked scalar form:
                # NO access at a disabled position -- a branch around the
                # load, the declared ``other`` on the disabled arm)
                reg = self._lower_masked_scalar_load(
                    ctx, base_reg, offset_reg, pointee, mask, other,
                    default, loc)
                self._bind_result(op, reg)
                return
            reg = scalar_mod.scalar_load(ctx, base_reg, offset_reg, pointee,
                                         loc)
            self._bind_result(op, reg)
            return
        if self._chunk is None:
            raise self._err(loc, "tl.load",
                            "a block load appears outside the vector chunk "
                            "region (block values must live inside it)")
        mreg = self._need(mask, loc) if mask is not None else None
        if pointee.is_bool():
            # the dtype-surface bool lane: one byte per element on the
            # i8 storage lane, the i1 result the != 0 lane test
            self._lower_bool_load(ctx, op, ptr, base_reg, offset_reg,
                                  mreg, other, default, loc)
            return
        # the wide-access proof (T011): a proven-contiguous access selects
        # the unit-stride form; an unproven one keeps the indexed form
        # (MECH-MASKED-VECTOR-ACCESS -- the proof never guesses)
        wide = scalar_mod.prove_wide_access(self, ptr, self._vl)
        unit_base = self._unit_stride_base(ctx, wide, base_reg, pointee,
                                           loc) if wide is not None else None
        if unit_base is not None:
            # T014: the unit-stride base must carry the uniform pointer
            # recurrences' adjustment (the proof's scalar terms do not
            # see the carried step)
            adjust = self._recurrence_byte_adjust(ctx, ptr, pointee, loc)
            if adjust is not None:
                unit_base = ctx.emit(mir.MOp(
                    "sadd", [unit_base, adjust],
                    [ctx.vreg(mir.I64, hint="wra", loc=loc)], loc=loc))
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
        elif self._sew < 32:
            # T014: the narrow-data fallback -- an unproven-contiguous
            # sub-32-bit block load lowers as a per-lane scalar loop
            # through the workspace (every indexed form with sub-32-bit
            # data faults the pinned QEMU, probed across index widths
            # and register assignments; the width-matched scalar loads
            # are the slice's proven safe form).  The masked form
            # performs no access at disabled lanes and writes the
            # declared ``other`` there.
            reg = self._lower_load_narrow(ctx, op, base_reg, offset_reg,
                                          pointee, mreg, other, default,
                                          loc)
            self._bind_result(op, reg)
            return
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

    # -- T014: the narrow-data load/store fallback ------------------------------

    def _narrow_lane0(self, ctx: _Ctx, reg: mir.VReg, loc) -> mir.VReg:
        """Lane 0 of a vector as a scalar (the slide+extract step of the
        per-lane scalar loop; the op runs in the VALUE's own region --
        the offsets ride e64m2 while the data region is narrower)."""
        self._vregion(ctx, reg.type, loc)
        sty = mir.ScalarType(reg.type.sew, signed=reg.type.kind != "uint",
                             float=reg.type.kind == "float")
        out = ctx.emit(mir.MOp(
            "vextract", [reg], [ctx.vreg(sty, hint="nl0", loc=loc)],
            loc=loc))
        return out

    def _narrow_slide(self, ctx: _Ctx, reg: mir.VReg, loc) -> mir.VReg:
        """Slide one lane down (the per-lane walk; the value's own
        region)."""
        self._vregion(ctx, reg.type, loc)
        return ctx.emit(mir.MOp(
            "vslidedn", [reg],
            [ctx.vreg(reg.type, hint="nsl", loc=loc)], loc=loc))

    def _narrow_mask01(self, ctx: _Ctx, mreg: mir.VReg,
                       rtype: mir.VectorType, loc) -> mir.VReg:
        """The mask as a 0/1 vector at SEW 32 (the per-lane activity --
        32-bit so the extracted lane scalar widens to i64 in the scalar
        core; independent of the data SEW)."""
        i32 = mir.VectorType(32, 1, "int")
        self._vregion(ctx, i32, loc)
        zero = self._splat_const(ctx, 0, i32, loc)
        one = self._splat_const(ctx, 1, i32, loc)
        v0 = ctx.emit(mir.MOp(
            "vmovmask", [mreg],
            [ctx.vreg(mir.MaskType(), hint="nm0", loc=loc,
                      fixed_phys="v0")], loc=loc))
        out = ctx.emit(mir.MOp(
            "vsel", [v0, one, zero],
            [ctx.vreg(i32, hint="nm1", loc=loc)], loc=loc))
        return out

    def _narrow_addr_vec(self, ctx: _Ctx, base_reg: mir.VReg,
                          scaled: mir.VReg, m01: Optional[mir.VReg],
                          redirect: mir.VReg, loc) -> mir.VReg:
        """The per-lane byte addresses as ONE vector (T014): the masked
        form redirects disabled lanes to the scratch slot (the
        block-atomic carrier form -- no source access, no per-lane
        branch): ``redirect + (base + off - redirect) & -active``."""
        aty = scaled.type                     # (64, lmul)
        self._vregion(ctx, aty, loc)
        addr = ctx.emit(mir.MOp(
            "vbinx", [scaled, base_reg],
            [ctx.vreg(aty, hint="nva", loc=loc)], attrs={"op": "add"},
            loc=loc))
        if m01 is None:
            return addr
        # the disabled lanes redirect to the scratch slot through the
        # v0 activity mask (the select form -- T029: the previous
        # ``& -active`` widened the 0/1 mask to the doubled class and
        # met the address class in a vbin; a NATIVE i64 index class
        # (m1 at the pass's lanes) and the doubled mask class (m2) hold
        # the same active lanes but the vbin demanded matching types --
        # the mask register is LMUL-free, so the select never crosses
        # classes)
        self._vregion(ctx, m01.type, loc)
        zero32 = self._splat_reg(ctx, ctx.const(0, mir.I32, loc),
                                 m01.type, loc)
        m = ctx.emit(mir.MOp(
            "vcmp", [m01, zero32],
            [ctx.vreg(mir.MaskType(), hint="nnm", loc=loc)],
            attrs={"pred": "ne", "fp": False}, loc=loc))
        v0 = ctx.emit(mir.MOp(
            "vmovmask", [m],
            [ctx.vreg(mir.MaskType(), hint="nv0", loc=loc,
                      fixed_phys="v0")], loc=loc))
        self._vregion(ctx, aty, loc)
        zero = self._splat_reg(ctx, ctx.const(0, mir.I64, loc), aty, loc)
        red_s = self._splat_reg(ctx, redirect, aty, loc)
        diff = ctx.emit(mir.MOp(
            "vbin", [addr, red_s],
            [ctx.vreg(aty, hint="nvd", loc=loc)], attrs={"op": "sub"},
            loc=loc))
        sel = ctx.emit(mir.MOp(
            "vsel", [v0, diff, zero],
            [ctx.vreg(aty, hint="nvs", loc=loc)], loc=loc))
        out = ctx.emit(mir.MOp(
            "vbin", [red_s, sel],
            [ctx.vreg(aty, hint="nvo", loc=loc)], attrs={"op": "add"},
            loc=loc))
        self._restore_region(ctx, loc)
        return out

    def _lower_load_narrow(self, ctx: _Ctx, op: tir.Op, base_reg: mir.VReg,
                           offset_reg: mir.VReg, pointee: tir.Type,
                           mreg: Optional[mir.VReg], other, default,
                           loc, rtype_ty=None) -> mir.VReg:
        """The per-lane scalar loop of one sub-32-bit block load (the
        address vector's lanes redirect the disabled ones to the
        scratch's ``other`` slot -- no source access there; the width-
        matched scalar loads are the slice's proven safe form).

        ``rtype_ty`` overrides the result's register type (the bool
        lane's i8 storage view; the op's own result type otherwise)."""
        rtype = self._vtype(rtype_ty if rtype_ty is not None
                            else op.results[0].type)
        sew = rtype.sew
        esz = sew // 8
        vl = self._vl
        scaled, tree = addr_mod.materialize_address(
            ctx, base_reg, offset_reg, pointee, loc, vl, (self._sew, 1))
        self.trees.append(tree)
        ws = self._workspace_private_reg(ctx, loc)
        scratch = ctx.emit(mir.MOp(
            "sadd", [ws, ctx.const(self._narrow_ws_offset, mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="nws", loc=loc)], loc=loc))
        redirect = ctx.emit(mir.MOp(
            "sadd", [scratch, ctx.const(32 * 4, mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="nwr", loc=loc)], loc=loc))
        sty = mir.ScalarType(sew, signed=True, float=rtype.kind == "float")
        m01 = self._narrow_mask01(ctx, mreg, rtype, loc) \
            if mreg is not None else None
        # the disabled lanes' declared default, staged into the redirect
        # slot (a splat scalar stores once; a block other stores per lane
        # off the address-class slide below)
        ovec = None
        if mreg is not None:
            if other is not None or default == tir.MaskedDefault.VALUE:
                oreg = self._need(other, loc)
                if oreg.is_vector():
                    ovec = oreg
                else:
                    ctx.emit0(mir.MOp(
                        "sstore", [redirect, oreg], [],
                        attrs={"width": sew, "offset": 0}, loc=loc))
            else:
                zero = ctx.const(0, sty, loc)
                ctx.emit0(mir.MOp(
                    "sstore", [redirect, zero], [],
                    attrs={"width": sew, "offset": 0}, loc=loc))
        addr_vec = self._narrow_addr_vec(ctx, base_reg, scaled, m01,
                                         redirect, loc)
        off = addr_vec
        for j in range(vl):
            addr = self._narrow_lane0(ctx, off, loc)
            slot = ctx.emit(mir.MOp(
                "sadd", [scratch, ctx.const(j * esz, mir.I64, loc)],
                [ctx.vreg(mir.I64, hint="nls", loc=loc)], loc=loc))
            if ovec is not None:
                oval = self._narrow_lane0(ctx, ovec, loc)
                ctx.emit0(mir.MOp(
                    "sstore", [redirect, oval], [],
                    attrs={"width": sew, "offset": 0}, loc=loc))
                ovec = self._narrow_slide(ctx, ovec, loc)
            val = ctx.emit(mir.MOp(
                "sload", [addr],
                [ctx.vreg(sty, hint="nlv", loc=loc)],
                attrs={"width": sew, "offset": 0, "ext": "zext"},
                loc=loc))
            ctx.emit0(mir.MOp(
                "sstore", [slot, val], [],
                attrs={"width": sew, "offset": 0}, loc=loc))
            off = self._narrow_slide(ctx, off, loc)
        self._vregion(ctx, rtype, loc)
        return ctx.emit(mir.MOp(
            "vunit_load", [scratch],
            [ctx.vreg(rtype, hint="nld", loc=loc)],
            attrs={"sew": sew}, loc=loc))

    # -- the dtype-surface bool lane (a 1-byte backing store) -----------------

    def _guard_block_names(self, tag: str) -> Tuple[str, str, str]:
        """Three unique block names for one scalar guard (then/else/join)."""
        n = getattr(self, "_scalar_guard_n", 0) + 1
        self._scalar_guard_n = n
        return (f"{tag}.t{n}", f"{tag}.e{n}", f"{tag}.j{n}")

    def _lower_masked_scalar_load(self, ctx: _Ctx, base_reg: mir.VReg,
                                  offset_reg: mir.VReg, pointee: tir.Type,
                                  mask, other, default,
                                  loc) -> mir.VReg:
        """The pinned masked SCALAR load: the disabled position performs
        NO access (a branch around the load -- the address may be
        out-of-range exactly there), the declared ``other`` (or an undef
        zero when none) on the disabled arm; the join carries the value."""
        mreg = self._bool_scalar(ctx, self._need(mask, loc), loc)
        m64 = mreg if mreg.type == mir.I64 else \
            scalar_mod.widen_to(ctx, mreg, 64, loc)
        if pointee.is_bool():
            rty = mir.I64          # the scalar-bool 0/1 convention
        else:
            rty = mir.ScalarType(pointee.bitwidth(), signed=True,
                                 float=pointee.is_float())
        tname, ename, jname = self._guard_block_names("msl")
        then_b = ctx.add_block(tname, [], loc)
        else_b = ctx.add_block(ename, [], loc)
        res = mir.VReg(rty, name=f"mslv{self._scalar_guard_n}")
        join_b = ctx.add_block(jname, [res], loc)
        ctx.emit0(mir.MOp(
            "brc", [m64], [],
            attrs={"true_target": tname, "true_args": [],
                   "false_target": ename, "false_args": []}, loc=loc))
        ctx.switch(then_b)
        val = scalar_mod.scalar_load(ctx, base_reg, offset_reg, pointee,
                                     loc)
        if val.type != rty:
            val = scalar_mod.convert_width(ctx, val, rty.width, loc)
        ctx.emit0(mir.MOp(
            "br", [], [], attrs={"target": jname, "args": [val]},
            loc=loc))
        ctx.switch(else_b)
        if other is not None or default == tir.MaskedDefault.VALUE:
            oreg = self._scalar_bool_gpr(ctx, self._need(other, loc),
                                         loc) \
                if pointee.is_bool() else self._need(other, loc)
        else:
            # no declared default: the value is undefined there -- any
            # value is a legal compilation (a zero keeps it simple)
            oreg = scalar_mod.lower_const(ctx, 0, pointee, loc)
        if oreg.type != rty:
            oreg = scalar_mod.convert_width(ctx, oreg, rty.width, loc)
        ctx.emit0(mir.MOp(
            "br", [], [], attrs={"target": jname, "args": [oreg]},
            loc=loc))
        ctx.switch(join_b)
        return res

    def _lower_masked_scalar_store(self, ctx: _Ctx, base_reg: mir.VReg,
                                   offset_reg: mir.VReg, pointee: tir.Type,
                                   value, mask, loc) -> None:
        """The pinned masked SCALAR store: the disabled position performs
        NO access (a branch around the store)."""
        mreg = self._bool_scalar(ctx, self._need(mask, loc), loc)
        m64 = mreg if mreg.type == mir.I64 else \
            scalar_mod.widen_to(ctx, mreg, 64, loc)
        vreg = self._need(value, loc)
        tname, jname = self._guard_block_names("mss")[:2]
        then_b = ctx.add_block(tname, [], loc)
        join_b = ctx.add_block(jname, [], loc)
        ctx.emit0(mir.MOp(
            "brc", [m64], [],
            attrs={"true_target": tname, "true_args": [],
                   "false_target": jname, "false_args": []}, loc=loc))
        ctx.switch(then_b)
        scalar_mod.scalar_store(ctx, base_reg, offset_reg, vreg, pointee,
                                loc)
        ctx.emit0(mir.MOp(
            "br", [], [], attrs={"target": jname, "args": []}, loc=loc))
        ctx.switch(join_b)

    def _mask01_at(self, ctx: _Ctx, mreg: mir.VReg, vtype: mir.VectorType,
                   loc) -> mir.VReg:
        """A mask as a 0/1 vector at an explicit type (the
        _narrow_mask01 form generalized off i32: the bool lane's i8
        bytes)."""
        self._vregion(ctx, vtype, loc)
        zero = self._splat_const(ctx, 0, vtype, loc)
        one = self._splat_const(ctx, 1, vtype, loc)
        v0 = ctx.emit(mir.MOp(
            "vmovmask", [mreg],
            [ctx.vreg(mir.MaskType(), hint="m01", loc=loc,
                      fixed_phys="v0")], loc=loc))
        out = ctx.emit(mir.MOp(
            "vsel", [v0, one, zero],
            [ctx.vreg(vtype, hint="m02", loc=loc)], loc=loc))
        self._restore_region(ctx, loc)
        return out

    def _bool_mask_of(self, ctx: _Ctx, reg: mir.VReg,
                      loc) -> mir.VReg:
        """The mask form of one i1 value register: a mask register is
        itself; the scalar-bool convention (an i64 0/1 GPR) tests against
        zero; a data-vector-held i1 lane-compares against zero."""
        if reg.is_mask():
            return reg
        if reg.is_vector():
            self._vregion(ctx, reg.type, loc)
            zero = self._splat_const(ctx, 0, reg.type, loc)
            m = ctx.emit(mir.MOp(
                "vcmp", [reg, zero],
                [ctx.vreg(mir.MaskType(), hint="bmm", loc=loc)],
                attrs={"pred": "ne", "fp": reg.type.kind == "float"},
                loc=loc))
            self._restore_region(ctx, loc)
            return m
        return self._mask_of_bool(ctx, reg, loc)

    def _lower_bool_load(self, ctx: _Ctx, op: tir.Op, ptr,
                         base_reg: mir.VReg, offset_reg: mir.VReg,
                         mreg: Optional[mir.VReg], other, default,
                         loc) -> None:
        """A block load from a bool backing store: the storage is one
        byte per element, so the access runs the i8 lane -- the unit-
        stride form when the wide proof holds, else the per-lane narrow
        fallback (the same proven-safe forms int8 uses) -- and the i1
        result is the ``!= 0`` lane test.  The declared disabled-position
        default substitutes at the i8 level BEFORE the test, so
        ``other=True`` yields True exactly and the disabled lanes
        perform no access."""
        storage = _storage_pointee(op.operands[0].type.pointee)
        stype = self._vtype(storage)
        wide = scalar_mod.prove_wide_access(self, ptr, self._vl)
        unit_base = self._unit_stride_base(ctx, wide, base_reg, storage,
                                           loc) if wide is not None else None
        if unit_base is not None:
            adjust = self._recurrence_byte_adjust(ctx, ptr, storage, loc)
            if adjust is not None:
                unit_base = ctx.emit(mir.MOp(
                    "sadd", [unit_base, adjust],
                    [ctx.vreg(mir.I64, hint="bwa", loc=loc)], loc=loc))
            self._vregion(ctx, stype, loc)
            operands = [unit_base]
            attrs = {"sew": stype.sew}
            if mreg is not None \
                    and not self.options.witness_drop_tail_predicates:
                v0 = ctx.emit(mir.MOp(
                    "vmovmask", [mreg],
                    [ctx.vreg(mir.MaskType(), hint="bv0", loc=loc,
                              fixed_phys="v0")], loc=loc))
                operands.append(v0)
                attrs["default"] = "undef"
            raw = ctx.emit(mir.MOp(
                "vunit_load", operands,
                [ctx.vreg(stype, hint="bld", loc=loc)], attrs=attrs,
                loc=loc))
            self._wide_selections.append(
                {"op": "load", "source": wide.source,
                 "detail": wide.detail, "loc": str(loc)})
        else:
            # the narrow fallback at the i8 width (the default's own
            # select happens after, at the i8 level)
            raw = self._lower_load_narrow(ctx, op, base_reg, offset_reg,
                                          storage, mreg, None, None, loc,
                                          rtype_ty=storage)
        if other is not None or default == tir.MaskedDefault.VALUE:
            oreg = self._need(other, loc)
            other8 = self._mask01_at(ctx, self._bool_mask_of(ctx, oreg,
                                                             loc),
                                     stype, loc)
            v0 = ctx.emit(mir.MOp(
                "vmovmask", [mreg],
                [ctx.vreg(mir.MaskType(), hint="bo0", loc=loc,
                          fixed_phys="v0")], loc=loc))
            self._vregion(ctx, stype, loc)
            raw = ctx.emit(mir.MOp(
                "vsel", [v0, raw, other8],
                [ctx.vreg(stype, hint="blo", loc=loc)], loc=loc))
            self._restore_region(ctx, loc)
        self._vregion(ctx, stype, loc)
        zero = self._splat_const(ctx, 0, stype, loc)
        b = ctx.emit(mir.MOp(
            "vcmp", [raw, zero],
            [ctx.vreg(mir.MaskType(), hint="blm", loc=loc)],
            attrs={"pred": "ne", "fp": False}, loc=loc))
        self._restore_region(ctx, loc)
        self._bind_result(op, b)

    def _lower_bool_store(self, ctx: _Ctx, op: tir.Op, ptr,
                          base_reg: mir.VReg, offset_reg: mir.VReg,
                          vreg: mir.VReg, mask_reg: Optional[mir.VReg],
                          loc) -> None:
        """A block store to a bool backing store: the i1 value (a mask)
        materializes as 0/1 bytes on the i8 lane and the same
        proven-safe access forms int8 uses perform the write (no access
        at the disabled lanes)."""
        storage = _storage_pointee(op.operands[0].type.pointee)
        stype = self._vtype(storage)
        bytes8 = self._mask01_at(ctx, self._bool_mask_of(ctx, vreg, loc),
                                 stype, loc)
        wide = scalar_mod.prove_wide_access(self, ptr, self._vl)
        unit_base = self._unit_stride_base(ctx, wide, base_reg, storage,
                                           loc) if wide is not None else None
        if unit_base is not None:
            adjust = self._recurrence_byte_adjust(ctx, ptr, storage, loc)
            if adjust is not None:
                unit_base = ctx.emit(mir.MOp(
                    "sadd", [unit_base, adjust],
                    [ctx.vreg(mir.I64, hint="bws", loc=loc)], loc=loc))
            self._vregion(ctx, stype, loc)
            operands = [unit_base, bytes8]
            attrs = {"sew": stype.sew}
            if mask_reg is not None \
                    and not self.options.witness_drop_tail_predicates:
                v0 = ctx.emit(mir.MOp(
                    "vmovmask", [mask_reg],
                    [ctx.vreg(mir.MaskType(), hint="bs0", loc=loc,
                              fixed_phys="v0")], loc=loc))
                operands.append(v0)
                attrs["default"] = "no-access"
            ctx.emit0(mir.MOp("vunit_store", operands, [], attrs=attrs,
                              loc=loc))
            self._wide_selections.append(
                {"op": "store", "source": wide.source,
                 "detail": wide.detail, "loc": str(loc)})
            return
        self._lower_store_narrow(ctx, base_reg, offset_reg, storage,
                                 bytes8, mask_reg, loc)

    def _lower_store_narrow(self, ctx: _Ctx, base_reg: mir.VReg,
                            offset_reg: mir.VReg, pointee: tir.Type,
                            vreg: mir.VReg, mask_reg: Optional[mir.VReg],
                            loc) -> Optional[mir.VReg]:
        """The per-lane scalar loop of one sub-32-bit block store (the
        value staged to the workspace first; disabled lanes redirect to
        the scratch's guard slot -- no source access)."""
        stype = vreg.type if vreg.is_vector() else \
            self._vtype(vreg.type)
        sew = stype.sew
        esz = sew // 8
        vl = self._vl
        scaled, tree = addr_mod.materialize_address(
            ctx, base_reg, offset_reg, pointee, loc, vl, (self._sew, 1))
        self.trees.append(tree)
        ws = self._workspace_private_reg(ctx, loc)
        scratch = ctx.emit(mir.MOp(
            "sadd", [ws, ctx.const(self._narrow_ws_offset, mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="nws", loc=loc)], loc=loc))
        redirect = ctx.emit(mir.MOp(
            "sadd", [scratch, ctx.const(32 * 4, mir.I64, loc)],
            [ctx.vreg(mir.I64, hint="nwr", loc=loc)], loc=loc))
        self._vregion(ctx, stype, loc)
        ctx.emit0(mir.MOp(
            "vunit_store", [scratch, vreg], [],
            attrs={"sew": sew}, loc=loc))
        m01 = self._narrow_mask01(ctx, mask_reg, stype, loc) \
            if mask_reg is not None else None
        addr_vec = self._narrow_addr_vec(ctx, base_reg, scaled, m01,
                                         redirect, loc)
        off = addr_vec
        for j in range(vl):
            addr = self._narrow_lane0(ctx, off, loc)
            slot = ctx.emit(mir.MOp(
                "sadd", [scratch, ctx.const(j * esz, mir.I64, loc)],
                [ctx.vreg(mir.I64, hint="nss", loc=loc)], loc=loc))
            val = ctx.emit(mir.MOp(
                "sload", [slot],
                [ctx.vreg(mir.ScalarType(sew, signed=True,
                                         float=stype.kind == "float"),
                          hint="nsv", loc=loc)],
                attrs={"width": sew, "offset": 0, "ext": "zext"},
                loc=loc))
            ctx.emit0(mir.MOp(
                "sstore", [addr, val], [],
                attrs={"width": sew, "offset": 0}, loc=loc))
            off = self._narrow_slide(ctx, off, loc)
        return mask_reg

    def _unit_stride_base(self, ctx: _Ctx, wide, base_reg: mir.VReg,
                          pointee: tir.Type, loc) -> Optional[mir.VReg]:
        """The scalar byte base of one proven-contiguous access:
        ``base + (elem + scalar terms) * esz`` (the arange's lanes are the
        consecutive elements from there)."""
        esz = 1 if pointee.is_bool() else pointee.bitwidth() // 8
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
                # the pinned masked SCALAR store: no access at the
                # disabled position (a branch around the store)
                self._lower_masked_scalar_store(ctx, base_reg, offset_reg,
                                                pointee, value, mask, loc)
                return None
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
        if pointee.is_bool():
            # the dtype-surface bool lane: 0/1 bytes on the i8 storage
            # lane (no access at the disabled lanes)
            self._lower_bool_store(ctx, op, ptr, base_reg, offset_reg,
                                   vreg, mask_reg, loc)
            return mask_reg
        # the wide-access proof (T011): the store side selects the same
        # unit-stride form a proven-contiguous access proves
        wide = scalar_mod.prove_wide_access(self, ptr, self._vl)
        unit_base = self._unit_stride_base(ctx, wide, base_reg, pointee,
                                           loc) if wide is not None else None
        if unit_base is not None:
            # T014: the store's unit-stride base carries the same
            # recurrence adjustment
            adjust = self._recurrence_byte_adjust(ctx, ptr, pointee, loc)
            if adjust is not None:
                unit_base = ctx.emit(mir.MOp(
                    "sadd", [unit_base, adjust],
                    [ctx.vreg(mir.I64, hint="wrs", loc=loc)], loc=loc))
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
        if self._sew < 32:
            # T014: the narrow-data fallback (the store half): the value
            # goes to the workspace scratch, then per-lane scalar stores
            # perform the writes the indexed form cannot (no access at
            # disabled lanes)
            return self._lower_store_narrow(ctx, base_reg, offset_reg,
                                            pointee, vreg, mask_reg, loc)
        scaled, tree = addr_mod.materialize_address(
            ctx, base_reg, offset_reg, pointee, loc, self._vl, (self._sew, 1))
        self.trees.append(tree)
        # T032: the store runs in the VALUE's own region -- a pass mixes
        # value widths (its SEW is the max of its memory ops' pointees:
        # add_base_max's fp32 vals beside int64 indices at SEW 64), and
        # the restored data region is the pass's, not the value's (the
        # unit-stride path already follows the value's type)
        stype = vreg.type if vreg.is_vector() else \
            self._vtype(op.operands[1].type)
        self._vregion(ctx, stype, loc)
        operands = [base_reg, scaled, vreg]
        attrs = {"eew": 64, "sew": stype.sew}
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
        """Open the region one vector op needs; returns whether
        :meth:`_restore_region` must follow (the materialize_address
        switch/restore pattern, generalized).  The no-op test compares
        against the ACTIVE region (never against the pass's data region
        alone: a helper's leftover region -- an e64m2 address form --
        must be switched away even when the wanted type IS the data
        region)."""
        if not isinstance(vtype, mir.VectorType):
            # a mask-typed value has no element width: the mask paths
            # (complement, and/or) are region-independent, so a mask
            # reaching here is a lowering bug -- refuse located, never
            # read .sew off a MaskType (the T024 crash class)
            raise self._err(
                loc, "region",
                f"a {vtype!r} value has no vsetvli region (mask values are "
                "region-independent; the path that reaches here must "
                "handle masks before the region switch)")
        want = (vtype.sew, vtype.lmul, self._vl)
        if ctx.active_region != want:
            avl = ctx.const(self._vl, mir.I32, loc)
            ctx.emit(mir.MOp(
                "vsetvli", [avl], [ctx.vreg(mir.I32, hint="rgo", loc=loc)],
                attrs={"sew": vtype.sew, "lmul": vtype.lmul,
                       "policy": "ta,ma"}, loc=loc))
            ctx.active_region = want
        # the caller restores unless the wanted region IS the data region
        # (then the post-op state is the pass's own)
        return (want[0], want[1]) != (self._sew, 1)

    def _restore_region(self, ctx: _Ctx, loc) -> None:
        self._vregion(ctx, mir.VectorType(self._sew, 1, "int"), loc)


def lower_to_mir(tir_module: tir.Module, plan: ExecutionPlan,
                 target: TargetModel, layout: ArgumentLayout,
                 grid: GridModel, options: Optional[LowerOptions] = None) -> mir.MModule:
    """Lower one verified TIR module to a verified-shape MIR module."""
    lowering = SliceLowering(tir_module, plan, target, layout, grid, options)
    module = lowering.lower()
    module.meta["sew"] = lowering._sew
    module.meta["block_extent"] = plan.block_extent
    module.meta["matrix_segments"] = list(lowering._matrix_segments)
    module.meta["matrix_staging_offset"] = lowering._matrix_stage_off
    module.meta["chunks"] = [[vl, n] for vl, n in plan.chunks]
    module.meta["address_trees"] = [t.describe() for t in lowering.trees]
    module.meta["wide_selections"] = list(lowering._wide_selections)
    module.meta["witness"] = lowering.options.identity_part()
    module.meta["grid"] = lowering.grid.describe()
    module.meta["stats_mode"] = ("elements" if lowering._count_reg is not None
                                 else "chunks" if lowering._stats_chunk_granular
                                 else "none")
    return module
