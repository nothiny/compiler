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

    def identity_part(self) -> str:
        parts = []
        if self.witness_drop_tail_predicates:
            parts.append("witness-drop-tail-predicates")
        if self.witness_drop_stage_barrier:
            parts.append("witness-drop-stage-barrier")
        if self.witness_drop_atomic_masks:
            parts.append("witness-drop-atomic-masks")
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

        # the reduction stage plan (T009): the two-phase split eligibility,
        # the partials and their merge rules (a100c/plan/stages.py); the
        # kernel body's (prefix, region, suffix) split follows it
        self.stage_plan = stages_mod.build_stage_plan(self.tir_module)
        self._body_split = self._split_body(statements)
        self._prescan_scans(fn.body)

        # the workspace requirements: scans materialize the block through
        # the worker-private region; the two-phase partials live in the
        # shared region (stride fixed at the maximum worker count)
        private_bytes = self.plan.workspace_private
        if self._scan_accs:
            private_bytes = max(private_bytes, arange_extent * 4)
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
            private_bytes += arange_extent * 4
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
        self._lower_statements(ctx, region, fn, view_regs)

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
            ctx.emit0(mir.MOp("sstore", [ws, reg], [],
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
            reloaded = ctx.emit(mir.MOp(
                "sload", [ws],
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

        tag = "schunk" if strided else "chunk"
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
            vtype = self._value_vtype(op.results[0].type)
            switched = self._open_region(ctx, vtype, loc)
            reg = ctx.emit(mir.MOp(
                "s2v", [operand],
                [ctx.vreg(vtype, hint="splat", loc=loc)], loc=loc))
            if switched:
                self._restore_region(ctx, loc)
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
                switched = self._open_region(
                    ctx, lreg.type if lreg.is_vector() else rreg.type, loc)
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
            # pointer form; the address resolution treats it as the base)
            self.values[op.results[0].vid] = self._need(op.operands[0], loc)
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

    def _lower_convert(self, ctx: _Ctx, op: tir.Op, loc) -> None:
        """The conversions this path executes: int32 -> fp32 (the mean/
        normalize kernels' accumulation typing) via vfcvt; the bool -> int
        0/1 class (a compare's lanes extended to their integer class --
        held at the data SEW, exact because the class {0,1} is closed
        under this slice's block arithmetic, and widened to the declared
        type at the scalar consumers); the scalar int widen/narrow forms;
        everything else refuses with a located diagnostic naming the
        conversions lane."""
        src, dst = op.operands[0], op.results[0]
        sreg = self._need(src, loc)
        if sreg.is_vector() or sreg.is_mask():
            if src.type.is_int() and src.type.bitwidth() == 32 \
                    and dst.type.is_float() and dst.type.bitwidth() == 32:
                reg = ctx.emit(mir.MOp(
                    "vunary", [sreg],
                    [ctx.vreg(mir.VectorType(32, 1, "float"),
                              hint="cvt", loc=loc)],
                    attrs={"op": "fcvt"}, loc=loc))
                self._bind_result(op, reg)
                return
            if src.type.is_bool() and dst.type.is_int() \
                    and dst.type.bitwidth() in (32, 64):
                # the 0/1 value class: vsel(1, 0) at the data SEW, in the
                # destination's own signedness kind
                kind = "uint" if dst.type.is_int_unsigned() else "int"
                one = self._splat_const(ctx, 1,
                                        mir.VectorType(self._sew, 1, kind),
                                        loc)
                zero = self._splat_const(ctx, 0,
                                         mir.VectorType(self._sew, 1, kind),
                                         loc)
                if sreg.is_mask():
                    v0 = ctx.emit(mir.MOp(
                        "vmovmask", [sreg],
                        [ctx.vreg(mir.MaskType(), hint="v0c", loc=loc,
                                  fixed_phys="v0")], loc=loc))
                else:
                    v0 = sreg
                reg = ctx.emit(mir.MOp(
                    "vsel", [v0, one, zero],
                    [ctx.vreg(mir.VectorType(self._sew, 1, "int"),
                              hint="b01", loc=loc)], loc=loc))
                self._bind_result(op, reg)
                return
            if src.type.is_int() and dst.type.is_int() \
                    and src.type.bitwidth() == 32 \
                    and dst.type.bitwidth() == 64:
                # the widening 0/1-class/int form: the widened lanes stay
                # non-negative under this slice's block arithmetic (vwadd
                # with x0 sext-extends, exact for the class and for the
                # slice's i32-lane values consumed at 64 bits)
                reg = ctx.emit(mir.MOp(
                    "vwaddx0", [sreg],
                    [ctx.vreg(mir.VectorType(64, 2, "int"), hint="cw",
                              loc=loc)], attrs={"mode": "sext"}, loc=loc))
                self._bind_result(op, reg)
                return
            raise self._err(loc, "convert",
                            "value conversion is not in the vector slice "
                            "(the int32<->fp32 and bool->int forms are; "
                            "the conversion matrix is the conversions "
                            "lane)")
        if src.type.is_int() and src.type.bitwidth() == 32 \
                and dst.type.is_float() and dst.type.bitwidth() == 32:
            splat = self._splat_reg(ctx, sreg,
                                    mir.VectorType(32, 1, "int"), loc)
            cvt = ctx.emit(mir.MOp(
                "vunary", [splat],
                [ctx.vreg(mir.VectorType(32, 1, "float"),
                          hint="cvt", loc=loc)],
                attrs={"op": "fcvt"}, loc=loc))
            self._bind_result(op, self._scalarize(ctx, cvt, loc))
            return
        if src.type.is_int() and dst.type.is_int():
            if src.type.bitwidth() < dst.type.bitwidth():
                self._bind_result(op, scalar_mod.widen_to(ctx, sreg,
                                                          dst.type.bitwidth(),
                                                          loc))
                return
            if src.type.bitwidth() > dst.type.bitwidth():
                self._bind_result(op, scalar_mod.narrow_to(
                    ctx, sreg, dst.type.bitwidth(), loc))
                return
        if src.type.is_bool() and dst.type.is_int():
            # the scalar 0/1 class, through the vector path
            one = self._splat_const(ctx, 1, mir.VectorType(32, 1, "int"),
                                    loc)
            zero = self._splat_const(ctx, 0, mir.VectorType(32, 1, "int"),
                                     loc)
            if sreg.is_mask():
                v0 = sreg
            else:
                v0 = self._mask_of_bool(ctx, sreg, loc)
            sel = ctx.emit(mir.MOp(
                "vsel", [v0, one, zero],
                [ctx.vreg(mir.VectorType(32, 1, "int"), hint="bs1",
                          loc=loc)], loc=loc))
            reg = self._scalarize(ctx, sel, loc)
            if dst.type.bitwidth() == 64:
                reg = scalar_mod.widen_to(ctx, reg, 64, loc)
            self._bind_result(op, reg)
            return
        if src.type.is_float() and src.type.is_int() \
                and src.type.bitwidth() == dst.type.bitwidth():
            raise self._err(loc, "convert",
                            "float->int conversion selects a semantic "
                            "rounding mode (the conversions lane owns the "
                            "rounding forms)")
        raise self._err(loc, "convert",
                        "value conversion is not in the vector slice "
                        "(the int32->fp32 form is; the conversion matrix "
                        "is the conversions lane)")

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
        if vop in ("sdiv", "udiv", "frem", "srem", "urem"):
            raise self._err(loc, code,
                            "integer division/remainder is not in the "
                            "vector slice (the non-negative power-of-two "
                            "remainder folds to a mask at the frontend; "
                            "every other form is a located refusal)")
        if vop == "fdiv" and lreg.type.kind != "float":
            raise self._err(loc, code,
                            "fdiv requires floating operands")
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
            operands = [unit_base, vreg]
            attrs = {"sew": self._sew}
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
        kind = "float" if ty.is_float() else (
            "uint" if ty.is_int_unsigned() else "int")
        return mir.VectorType(ty.bitwidth(), 1, kind)

    def _value_vtype(self, ty: tir.Type) -> mir.VectorType:
        """The register form of one TIR block type at the chunk's vl: the
        data class at (SEW, 1), the wider integer index class at its
        EMUL (the i64 offsets of int64 index arithmetic)."""
        if ty.is_int() and ty.bitwidth() > self._sew:
            return self._index_vtype(ty.bitwidth())
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
