"""Stage/synchronization/merge planning for cross-worker dependencies
(T009; COMPILER_ARCHITECTURE.md 5, "Stages, visibility and merge
semantics"; IR-EFFECTS-SYNC; F018/F053/F054/A006).

Three responsibilities, one module:

1. **The reduction operation table** (as data, MECH-TARGET-DESCRIPTION-AS-
   DATA style): every reduction/scan construct the source language declares
   -- ``tl.sum``, ``tl.max``, ``tl.min``, ``tl.argmax``, ``tl.argmin``
   (``return_indices``, ``return_indices_tie_break_left``), ``tl.xor_sum``,
   ``tl.reduce_or``, ``tl.cumsum``/``tl.cumprod`` scans, and the composite
   forms ``tl.softmax``/``tl.histogram``/``tl.sort``/``tl.topk`` -- with its
   combine rule, its *per-operation-and-dtype identity element*
   (signedness-correct: a signed min reduces from INT_MIN's dual, an
   unsigned min from 0xFFFFFFFF, never one hand-written constant for both),
   its index tie-break, its empty-extent result and its merge rule (how two
   partial results combine under the source's own semantics).  The frontend
   reads the identity when it builds the TIR ``reduce`` op; the lowering
   reads it when it initializes accumulators; the verifier checks the
   carried identity against this table.

2. **The two-phase cross-worker split plan.**  A reduction whose iteration
   space is one source program (single-program grids: the persistent
   reduction form, ``pat.persistent_reduce``) is split across the call's
   workers: phase 1 computes per-worker partials over worker-owned ranges
   and writes them to **owned workspace regions**; a stage barrier
   (``a100rt_stage_barrier``, pthread-based, F054/A006 -- no assumed
   coherence) establishes visibility; the merge step combines the partials
   under the source's own semantics (exact for integer/index/boolean;
   floating accumulation order regrouped only within the case's declared
   tolerance, F052).  Workspace ownership is *disjoint per worker outside
   the declared merge*: the layout computes per-worker slots and
   ``WorkspaceLayout.validate`` rejects any plan whose writers overlap (or
   whose slots cross the region bounds) -- the stage-plan test constructs
   such a violating plan and requires the rejection.

3. **Split-K style reduction feeds for dot.**  ``SplitKFeed`` models the
   K-range split of a ``tl.dot`` pipeline (partial output tiles per K slice
   in owned workspace, barrier, merge under the accumulation dtype).  The
   matrix lane (T010/T014) consumes the model; this module owns the
   workspace/merge contract it must satisfy.

The module is the *pure model*: the lowering (a100c/lower/vectorize.py)
emits the same structure natively and consults this plan; the tests verify
the model directly (test_stage_plan.py) and the executed artifacts
(test_reductions.py, tools/check_stage_barriers.py).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from a100c.ir import tir

__all__ = [
    "REDUCTION_OPS", "ReductionOpSpec", "identity_for", "reduce_result_shape",
    "normalize_axes", "empty_extent_result", "merge_partials",
    "MERGE_SUM", "MERGE_MIN", "MERGE_MAX", "MERGE_XOR", "MERGE_OR",
    "MERGE_MIN_INDEX", "MERGE_MAX_INDEX", "MERGE_PRODUCT", "MERGE_PASS",
    "LoopCarriedClass", "classify_carried_update", "carried_merge_kind",
    "WorkspaceRegion", "WorkspaceLayout", "PartialSpec", "TwoPhasePlan",
    "SplitKFeed", "build_stage_plan", "validate_stage_plan",
    "SOFTMAX_COMPOSITE", "SPLIT_WORKERS",
]

#: worker counts a two-phase split may use (F053: at most 8 compute workers)
SPLIT_WORKERS = (1, 2, 4, 8)

#: per-worker workspace slot alignment (a100rt.h: private regions are
#: 64-byte aligned and padded so no two workers share a cache line; the
#: shared region's per-worker slots use the same discipline)
SLOT_ALIGN = 8


# ---------------------------------------------------------------------------
# 1. The reduction operation table
# ---------------------------------------------------------------------------

#: merge rules (how two partials combine under the source's own semantics)
MERGE_SUM = "sum"              # partial_a + partial_b (exact int; tolerance fp)
MERGE_MIN = "min"              # min(partial_a, partial_b)
MERGE_MAX = "max"              # max(partial_a, partial_b)
MERGE_XOR = "xor"              # partial_a ^ partial_b (exact)
MERGE_OR = "or"                # partial_a | partial_b (exact)
MERGE_MIN_INDEX = "min-index"  # (val, idx) pair: smaller val, tie -> smaller idx
MERGE_MAX_INDEX = "max-index"  # (val, idx) pair: larger val, tie -> smaller idx
MERGE_PRODUCT = "product"      # partial_a * partial_b (exact int; tolerance fp)
MERGE_PASS = "pass"            # sequential carry (scans): later value wins


@dataclass(frozen=True)
class ReductionOpSpec:
    """One reduction operation's declared semantics (per Triton 3.8)."""
    name: str                        # tl.* construct name
    kind: str                        # TIR reduce kind
    merge: str                       # partial-combination rule
    index_form: bool = False         # produces (or pairs with) an index
    tie_break_left: bool = True      # default tie direction (declared)
    #: ops that also express a scan form (cumsum/cumprod)
    scan_carry: Optional[str] = None # merge rule of the scan's carry
    commutative: bool = True
    notes: str = ""


REDUCTION_OPS: Dict[str, ReductionOpSpec] = {
    "tl.sum": ReductionOpSpec(
        "tl.sum", "sum", MERGE_SUM,
        notes="axis=None reduces every axis; dtype= re-types the accumulator "
              "before the reduction (the identity follows the accumulator "
              "type)"),
    "tl.max": ReductionOpSpec(
        "tl.max", "max", MERGE_MAX, index_form=True,
        notes="return_indices=True yields (values, indices); "
              "return_indices_tie_break_left defaults True (leftmost)"),
    "tl.min": ReductionOpSpec(
        "tl.min", "min", MERGE_MIN, index_form=True,
        notes="return_indices=True yields (values, indices); "
              "return_indices_tie_break_left defaults True (leftmost)"),
    "tl.argmax": ReductionOpSpec(
        "tl.argmax", "argmax", MERGE_MAX_INDEX, index_form=True,
        notes="returns the index of the maximum; tie_break_left defaults "
              "True (leftmost index among equal maxima)"),
    "tl.argmin": ReductionOpSpec(
        "tl.argmin", "argmin", MERGE_MIN_INDEX, index_form=True,
        notes="returns the index of the minimum; tie_break_left defaults "
              "True (leftmost index among equal minima)"),
    "tl.xor_sum": ReductionOpSpec(
        "tl.xor_sum", "xor_sum", MERGE_XOR,
        notes="bitwise xor reduction, integer operands, exact"),
    "tl.reduce_or": ReductionOpSpec(
        "tl.reduce_or", "reduce_or", MERGE_OR,
        notes="bitwise or reduction, integer operands, exact"),
    "tl.cumsum": ReductionOpSpec(
        "tl.cumsum", "cumsum", MERGE_SUM, commutative=False,
        scan_carry=MERGE_SUM,
        notes="inclusive prefix scan; reverse=True suffix scan; the scan's "
              "chunk carry merges by sum"),
    "tl.cumprod": ReductionOpSpec(
        "tl.cumprod", "cumprod", MERGE_PRODUCT, commutative=False,
        scan_carry=MERGE_PRODUCT,
        notes="inclusive prefix product scan; reverse=True suffix scan; the "
              "chunk carry merges by product (exact int; tolerance fp)"),
    "tl.histogram": ReductionOpSpec(
        "tl.histogram", "histogram", MERGE_SUM,
        notes="out[b] = count of input elements equal to b, b in "
              "[0, num_bins); elements outside the range are not counted; "
              "the result dtype is int32 and merges by exact sum"),
    "tl.sort": ReductionOpSpec(
        "tl.sort", "sort", MERGE_PASS, commutative=False,
        notes="whole-block reorder along dim (descending flag); not a "
              "partial-mergeable reduction -- the block is reordered once"),
    "tl.topk": ReductionOpSpec(
        "tl.topk", "topk", MERGE_PASS, commutative=False,
        notes="k largest (descending default) along dim, sorted; value ties "
              "keep source order (stable); not partial-mergeable"),
    "tl.softmax": ReductionOpSpec(
        "tl.softmax", "softmax", MERGE_PASS, commutative=False,
        notes="composite: subtract the axis max (reduce max, keep_dims), "
              "exponentiate, normalize by the axis sum (reduce sum, "
              "keep_dims); the reduction structure is declared here, the "
              "elementwise exp is the math-ops lane"),
}

#: kinds the TIR ``reduce`` op accepts (value kinds; the index forms are
#: carried by attrs on the same op)
REDUCE_KINDS = {s.kind for s in REDUCTION_OPS.values()} - {
    "cumsum", "cumprod", "softmax", "sort", "topk", "histogram"}
#: scan kinds (the TIR ``scan`` op)
SCAN_KINDS = {"cumsum", "cumprod"}


def _int_bounds(width: int, signed: bool) -> Tuple[int, int]:
    if signed:
        return -(1 << (width - 1)), (1 << (width - 1)) - 1
    return 0, (1 << width) - 1


def identity_for(kind: str, ty: tir.Type):
    """The identity element of one reduction kind at one element type.

    Derived from the lattice the operation reduces over -- never one
    hand-written constant: a signed min reduces from INT_MAX(w), an
    unsigned min from 0xFF..FF(w); a float max from -inf, a float min
    from +inf (IEEE, so the identity never wins a comparison against a
    real element).  This is the AM0282 discipline: the identity is the
    lattice's top/bottom for the *signedness in the type*, and the
    stage-plan test re-derives it for every op x dtype pair.
    """
    if kind in ("sum", "xor_sum", "reduce_or", "cumsum"):
        if ty.is_bool():
            return False
        if ty.is_float():
            return 0.0
        return 0
    if kind in ("max", "argmax", "softmax-max"):
        # the max identity is the lattice's BOTTOM: the smallest value
        # the type's own signedness can hold (a signed max reduces from
        # INT_MIN, an unsigned max from 0 -- never one constant for both)
        if ty.is_float():
            return -math.inf
        if ty.is_bool():
            return False
        lo, _ = _int_bounds(ty.bitwidth(), ty.is_int_signed())
        return lo
    if kind in ("min", "argmin"):
        # the min identity is the lattice's TOP: the largest value of the
        # signedness (a signed min reduces from INT_MAX, an unsigned min
        # from all-ones)
        if ty.is_float():
            return math.inf
        if ty.is_bool():
            return True
        _, hi = _int_bounds(ty.bitwidth(), ty.is_int_signed())
        return hi
    if kind == "cumprod":
        if ty.is_bool():
            return True
        if ty.is_float():
            return 1.0
        return 1
    raise KeyError(f"no identity declared for reduction kind {kind!r}")


def _index_identity(ty: tir.Type):
    """The index lane's identity for an (value, index) pair merge: the
    worst index, so a real lane always wins (indices are non-negative)."""
    if ty.is_int_unsigned():
        return (1 << ty.bitwidth()) - 1
    return (1 << (ty.bitwidth() - 1)) - 1     # INT_MAX: worst for min-idx


def normalize_axes(axis, rank: int, loc=None) -> Tuple[int, ...]:
    """Normalize the source ``axis`` (None | int | tuple) to a sorted tuple
    of non-negative axes; raise (located at the caller) on out-of-range."""
    if axis is None:
        return tuple(range(rank))
    if isinstance(axis, (tuple, list)):
        axes = tuple(axis)
    else:
        axes = (axis,)
    out = []
    for a in axes:
        if isinstance(a, bool) or not isinstance(a, int):
            raise ValueError("reduction axis must be an integer")
        aa = a + rank if a < 0 else a
        if not 0 <= aa < rank:
            raise ValueError(
                f"reduction axis {a} outside rank {rank}")
        out.append(aa)
    return tuple(sorted(set(out)))


def reduce_result_shape(shape: tir.Shape, axes: Sequence[int],
                        keep_dims: bool) -> tir.Shape:
    """The reduce result shape: reduced axes removed (or kept at extent 1
    with keep_dims; kept axes are real -- they back storage)."""
    axes = set(axes)
    out: List[tir.Extent] = []
    for i, e in enumerate(shape):
        if i in axes:
            if keep_dims:
                out.append(tir.Extent(1, False))
        else:
            out.append(e)
    return tuple(out)


def empty_extent_result(kind: str, ty: tir.Type):
    """The exact result of reducing an empty extent: the identity element
    (for index forms, the worst index; a source reducing zero elements has
    no tie to break, so the identity is the declared answer)."""
    if kind in ("argmax", "argmin"):
        return _index_identity(tir.INT32)
    return identity_for(kind, ty)


def merge_partials(kind: str, a, b, tie_break_left: bool = True):
    """The pure model of one merge step (test oracle; the lowering emits
    the same rule natively).  ``a`` is the earlier partial (worker 0 side),
    ``b`` the later; index forms take (value, index) pairs."""
    if kind == MERGE_SUM:
        return a + b
    if kind == MERGE_PRODUCT:
        return a * b
    if kind == MERGE_XOR:
        return a ^ b
    if kind == MERGE_OR:
        return a | b
    if kind == MERGE_MIN:
        return a if a <= b else b
    if kind == MERGE_MAX:
        return a if a >= b else b
    if kind in (MERGE_MIN_INDEX, MERGE_MAX_INDEX):
        av, ai = a
        bv, bi = b
        if kind == MERGE_MIN_INDEX:
            better = bv < av
            tie = bv == av
        else:
            better = bv > av
            tie = bv == av
        if better:
            return (bv, bi)
        if tie:
            left_wins = (bi < ai) if tie_break_left else (bi > ai)
            return ((bv, bi) if left_wins else (av, ai))
        return (av, ai)
    if kind == MERGE_PASS:
        return b
    raise KeyError(f"unknown merge kind {kind!r}")


# ---------------------------------------------------------------------------
# 2. Loop-carried reduction recognition
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LoopCarriedClass:
    """How one loop-carried (or chunk-carried) value merges across the
    iterations the split divides (the persistent-reduction form)."""
    name: str
    merge: str                      # MERGE_* rule
    identity: object                # the merge identity at the value's type
    index_pair: bool = False        # an (value, index) pair carried twice

    def describe(self) -> dict:
        return {"name": self.name, "merge": self.merge,
                "identity": repr(self.identity), "index_pair": self.index_pair}


#: TIR binop -> merge rule for the accumulate form ``acc = acc OP term``
_ACCUMULATE_MERGES = {
    "arith.add": MERGE_SUM,
    "arith.mul": MERGE_PRODUCT,
    "bit.and": "and",
    "bit.or": MERGE_OR,
    "bit.xor": MERGE_XOR,
}


def classify_carried_update(update_op: "tir.Op") -> Optional[str]:
    """Classify one carried-value update op as a merge rule.

    Two source forms are recognized (the corpus persistent-reduction
    forms):

    * accumulate: ``acc = acc + term`` / ``acc = acc * term`` /
      ``acc = acc & term`` ... -- the merge rule follows the operator;
    * arg-select pair: ``best_val = tl.where(local < best_val, local,
      best_val)`` with its paired index select -- the merge is the
      (value, index) pair rule with tie-break-left.

    Anything else returns None: the carried value has no declared
    cross-iteration merge, and a split of its loop is refused (the loop
    stays whole inside one program; correctness is preserved).
    """
    if update_op.op in _ACCUMULATE_MERGES:
        lhs, rhs = update_op.operands
        # acc on either side; the other side is the per-iteration term
        return _ACCUMULATE_MERGES[update_op.op]
    if update_op.op == "select.where":
        return MERGE_PASS        # the pair rule is decided by the caller
    if update_op.op == "reduce":
        return update_op.attrs.get("merge", MERGE_PASS)
    return None


def carried_merge_kind(loop: "tir.Loop") -> Dict[str, LoopCarriedClass]:
    """Per carried name of one loop: the merge class, or an absent entry
    when the update has no merge semantics (the caller refuses the split
    for those names if they escape the region)."""
    out: Dict[str, LoopCarriedClass] = {}
    # collect the body's final binding of each carried name: the lowering
    # binds by scope name, so walk the body's ops and keep the last
    # producer of each carried name
    final: Dict[str, tir.Op] = {}
    for st in _walk_statements(loop.body.statements):
        if isinstance(st, tir.Op):
            for r in st.results:
                for key in r.scope_names():
                    final[key] = st
    for name, init in loop.carried:
        op = final.get(name)
        if op is None:
            continue
        ty = init.type
        if op.op == "reduce":
            kind = op.attrs["kind"]
            merge = REDUCTION_OPS[f"tl.{kind}"].merge if \
                f"tl.{kind}" in REDUCTION_OPS else MERGE_PASS
            out[name] = LoopCarriedClass(name, merge,
                                         identity_for(kind, ty))
        elif op.op in _ACCUMULATE_MERGES:
            rule = _ACCUMULATE_MERGES[op.op]
            ident = {"sum": 0, "product": 1, "and": -1, "or": 0,
                     "xor": 0}[rule]
            if ty.is_float():
                ident = float(ident) if rule != "and" else ident
            out[name] = LoopCarriedClass(name, rule, ident)
        elif op.op == "select.where":
            # the arg-select pair: the value select's condition decides;
            # treat as the pair rule -- the paired index must exist under
            # a name whose select shares the condition
            out[name] = LoopCarriedClass(name, MERGE_PASS, None)
    return out


def _walk_statements(statements):
    for st in statements:
        yield st
        if isinstance(st, tir.If):
            yield from _walk_statements(st.then.statements)
            yield from _walk_statements(st.els.statements)
        elif isinstance(st, tir.Loop):
            yield from _walk_statements(st.body.statements)


# ---------------------------------------------------------------------------
# 3. Workspace ownership and the two-phase plan
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WorkspaceRegion:
    """One worker's owned write range inside the shared workspace."""
    worker: int
    offset: int                    # byte offset from the region base
    size: int                      # byte size

    def overlaps(self, other: "WorkspaceRegion") -> bool:
        return (self.worker == other.worker
                and self.offset < other.offset + other.size
                and other.offset < self.offset + self.size)

    def contains(self, offset: int, size: int) -> bool:
        return self.offset <= offset and offset + size <= self.offset + self.size

    def describe(self) -> dict:
        return {"worker": self.worker, "offset": self.offset,
                "size": self.size}


@dataclass
class WorkspaceLayout:
    """The per-worker owned slot layout of the shared workspace region.

    Every partial lives at ``base + worker * stride + slot_offset``; the
    layout is *disjoint by construction* and ``validate`` proves it (the
    stage-plan test builds a violating layout and requires the rejection:
    acceptance[3])."""
    #: region-relative byte offsets of the partial slots
    slots: Tuple[int, ...] = ()
    #: byte size of each slot (a slot may not spill into its neighbour)
    slot_sizes: Tuple[int, ...] = ()
    workers: int = 1
    stride: int = 0
    total_bytes: int = 0

    @staticmethod
    def for_partials(partial_bytes: Sequence[int], workers: int,
                     align: int = SLOT_ALIGN) -> "WorkspaceLayout":
        offsets = []
        off = 0
        sizes = []
        for b in partial_bytes:
            offsets.append(off)
            size = _align_up(b, align)
            sizes.append(size)
            off += size
        stride = _align_up(off, align)
        total = stride * workers
        return WorkspaceLayout(slots=tuple(offsets),
                               slot_sizes=tuple(sizes), workers=workers,
                               stride=stride, total_bytes=total)

    def region_of(self, worker: int) -> WorkspaceRegion:
        if not 0 <= worker < self.workers:
            raise ValueError(f"worker {worker} outside 0..{self.workers - 1}")
        return WorkspaceRegion(worker, worker * self.stride, self.stride)

    def slot_address(self, worker: int, slot: int) -> int:
        """Byte offset of one partial slot for one worker (absolute)."""
        if not 0 <= slot < len(self.slots):
            raise ValueError(f"slot {slot} outside the layout")
        return worker * self.stride + self.slots[slot]

    def describe(self) -> dict:
        return {"slots": list(self.slots),
                "slot_sizes": list(self.slot_sizes),
                "workers": self.workers, "stride": self.stride,
                "total_bytes": self.total_bytes}

    def validate(self) -> Tuple[bool, str]:
        """Ownership disjointness and bounds: every worker's owned region
        is disjoint from every other's (no byte is written by two workers
        outside the declared merge), every slot fits inside its own
        worker's region without spilling into a neighbour, and the total
        covers every region.  A hand-built layout that violates any of
        these is rejected here (acceptance[3])."""
        if self.workers not in SPLIT_WORKERS:
            return False, f"worker count {self.workers} not in 1/2/4/8 (F053)"
        if self.stride <= 0:
            return False, "stride must be positive"
        if len(self.slot_sizes) != len(self.slots):
            return False, "slot sizes and slot offsets disagree"
        if self.total_bytes < self.stride * self.workers:
            return False, (f"total {self.total_bytes} bytes cannot hold "
                           f"{self.workers} regions of {self.stride}")
        # the slot table: region-relative, disjoint, inside the stride
        prev_end = 0
        for i, (off, size) in enumerate(zip(self.slots, self.slot_sizes)):
            if off < 0 or size <= 0:
                return False, f"slot {i} has a non-positive extent"
            if off < prev_end:
                return False, (f"slot {i} overlaps its predecessor (a "
                               "worker's own slots must be disjoint)")
            if off + size > self.stride:
                return False, (f"slot {i} ({size} bytes at region offset "
                               f"{off}) spills past its worker's "
                               f"{self.stride}-byte region into another "
                               "worker's ownership")
            prev_end = off + size
        # the per-worker regions are [w*stride, (w+1)*stride): with
        # stride > 0 they are pairwise disjoint by construction; the
        # spill check above is what a lying hand-built layout trips
        for w in range(self.workers):
            if (w + 1) * self.stride > self.total_bytes:
                return False, (f"worker {w}'s region ends past the "
                               f"{self.total_bytes}-byte workspace")
        return True, (f"{self.workers} disjoint owned regions of "
                      f"{self.stride} bytes (merge reads all, writes one)")


def _align_up(n: int, align: int) -> int:
    return (n + align - 1) & ~(align - 1)


@dataclass
class PartialSpec:
    """One partial that flows through the two-phase split."""
    #: the TIR value id of the region-exit result (the lowering binds the
    #: merged value there)
    value_id: int
    name: str
    merge: str                     # MERGE_* rule
    dtype: tir.Type
    bytes_: int = 4
    #: for index-pair merges: the paired index value id and dtype
    pair_value_id: Optional[int] = None
    pair_dtype: Optional[tir.Type] = None
    tie_break_left: bool = True

    def slot_bytes(self) -> int:
        if self.merge in (MERGE_MIN_INDEX, MERGE_MAX_INDEX):
            return 2 * 4           # the (value, index) pair, 4 bytes each
        return _align_up(max(4, (self.dtype.bitwidth() + 7) // 8), 4)

    def describe(self) -> dict:
        return {"name": self.name, "merge": self.merge,
                "dtype": repr(self.dtype), "bytes": self.slot_bytes(),
                "tie_break_left": self.tie_break_left}


@dataclass
class TwoPhasePlan:
    """The cross-worker two-phase split of one kernel's reduction region.

    Structure (COMPILER_ARCHITECTURE.md 5, partition policy (c)):

      phase 1  every worker computes its partials over its worker-owned
               share (strided chunk ranges: worker w takes chunks w, w+W,
               ...) and stores them to its owned workspace region;
      barrier  one ``a100rt_stage_barrier`` (every worker of the call
               reaches it exactly once -- the runtime's stage contract);
      merge    worker 0 (the merge owner) loads every worker's partials
               and combines them under the source's own semantics; the
               kernel's post-region statements run there exactly once.
    """
    eligible: bool = False
    reason: str = ""
    #: partials: the region-exit values that must merge (order = slot order)
    partials: Tuple[PartialSpec, ...] = ()
    workers: Tuple[int, ...] = SPLIT_WORKERS
    #: the split is taken at runtime when worker_count > 1 and the grid
    #: has at most one program (single-program persistent reductions;
    #: multi-program grids already distribute whole programs per worker)
    policy: str = "single-program-grids"
    merge_owner: int = 0
    barriers: int = 1              # per worker per call, on the split path
    #: the workspace layout at the maximum worker count (8); smaller
    #: counts use the same slot table with a smaller stride product
    layout: Optional[WorkspaceLayout] = None

    def layout_for(self, workers: int) -> WorkspaceLayout:
        return WorkspaceLayout.for_partials(
            [p.slot_bytes() for p in self.partials], workers)

    def describe(self) -> dict:
        return {
            "eligible": self.eligible,
            "reason": self.reason,
            "policy": self.policy,
            "merge_owner": self.merge_owner,
            "barriers": self.barriers,
            "partials": [p.describe() for p in self.partials],
            "layout": self.layout.describe() if self.layout else None,
        }


@dataclass
class SplitKFeed:
    """Split-K style reduction feed for ``tl.dot`` (plan model).

    The K range of one dot splits across the call's workers; each worker
    accumulates its K slice into a partial output tile in its owned
    workspace region; the stage barrier establishes visibility; the merge
    adds the partial tiles in the accumulation dtype (exact for integer
    accumulation, which is modular in the 32-bit destination, F051;
    within the declared tolerance for floating accumulation, F052).  The
    matrix lane (T010/T014) consumes this contract; the workspace
    ownership and merge rules are owned here.
    """
    m: int = 0                     # output tile rows
    n: int = 0                     # output tile columns
    acc_dtype: tir.Type = tir.INT32
    workers: Tuple[int, ...] = SPLIT_WORKERS

    def partial_bytes(self) -> int:
        return _align_up(self.m * self.n *
                         max(4, (self.acc_dtype.bitwidth() + 7) // 8), 64)

    def layout_for(self, workers: int) -> WorkspaceLayout:
        return WorkspaceLayout.for_partials([self.partial_bytes()], workers)

    def merge_rule(self) -> str:
        return MERGE_SUM

    def describe(self) -> dict:
        return {"m": self.m, "n": self.n,
                "acc_dtype": repr(self.acc_dtype),
                "partial_bytes": self.partial_bytes(),
                "merge": self.merge_rule()}


#: tl.softmax's declared reduction structure (the composite the math-ops
#: lane completes): stable max subtraction, then exp, then the sum
#: normalization; keep_dims keeps the broadcast shape.
SOFTMAX_COMPOSITE = {
    "steps": ("reduce-max-keep-dims", "exp", "reduce-sum-keep-dims", "div"),
    "max_identity": "-inf (per float dtype)",
    "sum_identity": "0.0 (per float dtype)",
    "missing_dependency": "elementwise exp (math-ops lane)",
}


# ---------------------------------------------------------------------------
# 4. Plan construction and validation
# ---------------------------------------------------------------------------

def _escapes_region(value: tir.Value, region_stmts: Sequence,
                    stmts_after: Sequence) -> bool:
    """Does the value flow into an observable effect after the region?

    Transitive through the suffix's own statements: a region value escapes
    when it reaches a store, a loop bound, a region condition or a region
    carried init (control or memory effect) after the region closes --
    not merely when a dead suffix value mentions it."""
    ids = {id(s) for s in region_stmts}

    def statements(stmts):
        for st in stmts:
            if id(st) in ids:
                continue
            yield st
            if isinstance(st, tir.If):
                yield from statements(st.then.statements)
                yield from statements(st.els.statements)
            elif isinstance(st, tir.Loop):
                yield from statements(st.body.statements)

    # fixpoint: the set of values tainted by `value`
    tainted = {value.vid}
    changed = True
    stmt_list = list(statements(stmts_after))
    while changed:
        changed = False
        for st in stmt_list:
            if isinstance(st, tir.Op):
                if any(o.vid in tainted for o in st.operands):
                    for r in st.results:
                        if r.vid not in tainted:
                            tainted.add(r.vid)
                            changed = True
            elif isinstance(st, tir.If):
                if st.cond.vid in tainted:
                    return True
            elif isinstance(st, tir.Loop):
                for bound in (st.lower, st.upper, st.step, st.cond):
                    if bound is not None and bound.vid in tainted:
                        return True
                if any(init.vid in tainted for _, init in st.carried):
                    return True
    # observable effect: a store whose value or pointer is tainted --
    # including a store INSIDE the region (a region-internal store of a
    # partial would write the per-chunk value; its final write needs the
    # merged value, so the partial escapes through it).  An atomic is the
    # same class of effect (T011): a region value feeding an atomic's
    # value or pointer escapes (the atomic must run on the merged value).
    for st in stmt_list:
        if isinstance(st, tir.Op) and st.op in ("store", "atomic_rmw",
                                                "atomic_cas"):
            if any(o.vid in tainted for o in st.operands):
                return True
    for st in region_stmts:
        if isinstance(st, tir.Op) and st.op in ("store", "atomic_rmw",
                                                "atomic_cas"):
            if any(o.vid in tainted for o in st.operands):
                return True
    return False


def _statements_scalar_only(stmts: Sequence) -> Tuple[bool, str]:
    """Every statement is scalar-rank (rank-0 values only): the split's
    merge path runs once on the merge owner, so block-level statements
    after the region cannot execute there."""
    for st in stmts:
        if isinstance(st, tir.Op):
            if any(getattr(o, "rank", 0) > 0 for o in st.operands) or \
                    any(r.rank > 0 for r in st.results):
                return False, f"block-level op '{st.op}' after the region"
            if st.op == "debug_barrier":
                return False, "debug_barrier after the region (the stage " \
                              "contract requires equal barrier counts)"
        elif isinstance(st, tir.If):
            if st.cond.shape != ():
                return False, "block condition after the region"
            ok, why = _statements_scalar_only(st.then.statements)
            if not ok:
                return ok, why
            ok, why = _statements_scalar_only(st.els.statements)
            if not ok:
                return ok, why
        elif isinstance(st, tir.Loop):
            for bound in (st.lower, st.upper, st.step, st.cond):
                if bound is not None and bound.shape != ():
                    return False, "block loop bound after the region"
            ok, why = _statements_scalar_only(st.body.statements)
            if not ok:
                return ok, why
    return True, ""


def build_stage_plan(module: tir.Module) -> TwoPhasePlan:
    """Analyze one TIR module and build its two-phase split plan.

    Eligibility (each refusal reason is a *plan* decision, never a compile
    error: an ineligible kernel simply runs the normal per-program path):

    * the kernel's body, after its scalar prefix, is a reduction region
      (the block-level statements that produce region-exit scalar results
      via reduce ops or reduction-carried loops);
    * the statements after the region are scalar-only and contain no
      ``debug_barrier`` (the merge path runs on one worker; the stage
      contract requires equal barrier counts);
    * at least one region-exit value escapes into the post-region code
      (otherwise there is nothing to merge: the region's stores are
      elementwise and the program split already covers them).
    """
    plan = TwoPhasePlan()
    if len(module.functions) != 1:
        plan.reason = "module does not have exactly one function"
        return plan
    fn = module.functions[0]
    stmts = list(fn.body.statements)

    # split point: the first block-level statement (the region opens
    # there in the lowering); the region runs to the last block-level
    # statement; everything after is the post-region suffix
    def is_block_level(st) -> bool:
        if isinstance(st, tir.Op):
            return any(getattr(o, "rank", 0) > 0 for o in st.operands) or \
                any(r.rank > 0 for r in st.results)
        if isinstance(st, tir.If):
            return any(is_block_level(s) for s in
                       list(st.then.statements) + list(st.els.statements))
        if isinstance(st, tir.Loop):
            for bound in (st.lower, st.upper, st.step, st.cond):
                if bound is not None and bound.rank > 0:
                    return True
            return any(init.rank > 0 for _, init in st.carried) or \
                any(is_block_level(s) for s in st.body.statements)
        return False

    first = next((i for i, s in enumerate(stmts) if is_block_level(s)),
                 len(stmts))
    last = max([i for i, s in enumerate(stmts) if is_block_level(s)],
               default=-1)
    if first > last:
        plan.reason = "no block-level region (a scalar-only kernel needs " \
                      "no split)"
        return plan
    region = stmts[first:last + 1]
    suffix = stmts[last + 1:]

    ok, why = _statements_scalar_only(suffix)
    if not ok:
        plan.reason = f"post-region statements are not scalar-only: {why}"
        return plan
    # a debug_barrier inside the region breaks only the TWO-PHASE SPLIT
    # (the stage contract requires equal barrier counts per worker); the
    # within-program chunk merge still applies, so the partials are built
    # below regardless and the plan stays ineligible
    barrier_in_region = any(
        isinstance(st, tir.Op) and st.op == "debug_barrier"
        for st in _walk_statements(list(region) + list(suffix)))

    # region-exit values: reduce results and loop-exit joins defined in
    # the region that the suffix uses
    partials: List[PartialSpec] = []

    # (a) arg-select pairs: loops carrying (best_val, best_idx) selected
    # under one condition -- one partial covers the pair (the argmin /
    # argmax persistent form); either side escaping makes it a partial
    for loop in [st for st in _walk_statements(region)
                 if isinstance(st, tir.Loop)]:
        for val_join, idx_join in _select_pairs_of(loop):
            if _escapes_region(val_join, region, suffix) or \
                    _escapes_region(idx_join, region, suffix):
                partials.append(PartialSpec(
                    value_id=val_join.vid, name=val_join.name,
                    merge=_pair_direction(val_join, loop),
                    dtype=val_join.type,
                    pair_value_id=idx_join.vid, pair_dtype=idx_join.type,
                    tie_break_left=True))
    consumed = {p.pair_value_id for p in partials if p.pair_value_id}
    consumed.update(p.value_id for p in partials)

    # (b) loop-exit joins with an accumulate merge (vdot's acc += sum)
    for st in _walk_statements(region):
        if not isinstance(st, tir.Loop):
            continue
        for join in st.join_results:
            if join.vid in consumed:
                continue
            if not _escapes_region(join, region, suffix):
                continue
            merge = _loop_join_merge(join, region)
            if merge is None:
                plan.reason = (f"region value '{join.name}' escapes "
                               "without a merge rule (its loop update is "
                               "not a recognized reduction form)")
                return plan
            partials.append(PartialSpec(
                value_id=join.vid, name=join.name, merge=merge,
                dtype=join.type))
            consumed.add(join.vid)

    # (c) reduce results that escape (the plain block-reduction form)
    for st in _walk_statements(region):
        if isinstance(st, tir.Op) and st.op == "reduce":
            for value in st.results:
                if value.vid in consumed or \
                        not _escapes_region(value, region, suffix):
                    continue
                attrs = st.attrs
                kind = attrs["kind"]
                if kind in ("argmax", "argmin"):
                    partials.append(PartialSpec(
                        value_id=value.vid, name=value.name,
                        merge=MERGE_MAX_INDEX if kind == "argmax"
                        else MERGE_MIN_INDEX,
                        dtype=st.operands[0].type,
                        pair_value_id=None, pair_dtype=tir.INT32,
                        tie_break_left=bool(attrs.get("tie_break_left",
                                                      True))))
                elif attrs.get("return_indices"):
                    # the (value, index) pair: index-typed second result
                    idx_result = st.results[1]
                    partials.append(PartialSpec(
                        value_id=value.vid, name=value.name,
                        merge=MERGE_MAX_INDEX if kind == "max"
                        else MERGE_MIN_INDEX,
                        dtype=value.type,
                        pair_value_id=idx_result.vid,
                        pair_dtype=idx_result.type,
                        tie_break_left=bool(attrs.get("tie_break_left",
                                                      True))))
                    consumed.add(idx_result.vid)
                else:
                    spec = REDUCTION_OPS.get(f"tl.{kind}")
                    partials.append(PartialSpec(
                        value_id=value.vid, name=value.name,
                        merge=spec.merge if spec else MERGE_SUM,
                        dtype=value.type))
                consumed.add(value.vid)

    if not partials:
        plan.reason = "no region-exit value escapes into the suffix"
        return plan

    plan.partials = tuple(partials)
    if barrier_in_region:
        plan.reason = ("a debug_barrier inside the reduction region (the "
                       "two-phase split requires equal barrier counts per "
                       "worker); the within-program chunk merge still "
                       "applies")
        return plan
    plan.layout = plan.layout_for(max(SPLIT_WORKERS))
    plan.eligible = True
    plan.reason = (f"{len(partials)} partial(s), two-phase split at "
                   f"{plan.policy}; merge owner worker {plan.merge_owner}")
    return plan


def _select_pairs_of(loop: "tir.Loop") -> List[Tuple[tir.Value, tir.Value]]:
    """The (value, index) select-carried pairs of one loop: names whose
    final body binding is a ``select.where`` -- the argmin/argmax merge
    form (``best_val = where(cond, local, best_val)`` with its paired
    index select).  The induction and plain accumulators are excluded
    (their bindings are arith ops)."""
    final: Dict[str, tir.Op] = {}
    for b in _walk_statements(loop.body.statements):
        if isinstance(b, tir.Op):
            for r in b.results:
                for key in r.scope_names():
                    final[key] = b
    selected = [name for name, op in final.items()
                if isinstance(op, tir.Op) and op.op == "select.where"]
    joins = {j.name: j for j in loop.join_results}
    pairs: List[Tuple[tir.Value, tir.Value]] = []
    used: set = set()
    for name in selected:
        val = joins.get(name)
        if val is None or val.type.is_int() or name in used:
            continue
        for other in selected:
            idx = joins.get(other)
            if idx is None or not idx.type.is_int() or other in used:
                continue
            pairs.append((val, idx))
            used.update((name, other))
            break
    return pairs


def _pair_direction(value: tir.Value, loop: "tir.Loop") -> str:
    """min or max: read the carried identity's sense (inf/-inf, INT_MAX/
    INT_MIN -- the source's own get_dtype_min/max idiom)."""
    for name, init in loop.carried:
        if name == value.name:
            prod = init.producer
            if prod is not None and prod.op == "const":
                v = prod.attrs.get("value")
                if isinstance(v, float):
                    if v == math.inf:
                        return MERGE_MIN_INDEX
                    if v == -math.inf:
                        return MERGE_MAX_INDEX
                if isinstance(v, int) and not isinstance(v, bool):
                    if v > 0:
                        return MERGE_MIN_INDEX
                    if v < 0:
                        return MERGE_MAX_INDEX
    return MERGE_MIN_INDEX


def _loop_join_merge(value: tir.Value, region) -> Optional[str]:
    """The merge rule of a loop-exit join: the update op of its carried
    name (accumulate + -> sum, * -> product, ...)."""
    for st in _walk_statements(region):
        if isinstance(st, tir.Loop):
            if any(j is value for j in st.join_results):
                classes = carried_merge_kind(st)
                for name, c in classes.items():
                    join = {j.name: j for j in st.join_results}
                    if join.get(name) is value and c.merge != MERGE_PASS:
                        return c.merge
                return None
    return None


def validate_stage_plan(plan: TwoPhasePlan,
                        workers: int = 8) -> List[str]:
    """Validate one stage plan at one worker count: eligibility, workspace
    ownership disjointness, barrier count, merge-owner sanity.  Returns
    the list of violations (empty = valid); the stage-plan test feeds a
    deliberately violating plan and requires the rejection."""
    errors: List[str] = []
    if not plan.eligible:
        if not plan.reason:
            errors.append("ineligible plan without a reason")
        return errors
    if workers not in SPLIT_WORKERS:
        errors.append(f"worker count {workers} not in 1/2/4/8 (F053)")
        return errors
    if plan.barriers != 1:
        errors.append(f"a two-phase split crosses exactly one stage "
                      f"barrier per worker, plan declares {plan.barriers}")
    if not 0 <= plan.merge_owner < workers:
        errors.append(f"merge owner {plan.merge_owner} outside 0..{workers - 1}")
    if not plan.partials:
        errors.append("an eligible plan carries at least one partial")
    if plan.layout is None:
        errors.append("an eligible plan declares its workspace layout")
    else:
        ok, why = plan.layout.validate()
        if not ok:
            errors.append(f"declared workspace ownership violated: {why}")
    layout = plan.layout_for(workers)
    ok, why = layout.validate()
    if not ok:
        errors.append(f"workspace ownership violated: {why}")
    for p in plan.partials:
        if p.merge not in (MERGE_SUM, MERGE_MIN, MERGE_MAX, MERGE_XOR,
                           MERGE_OR, MERGE_MIN_INDEX, MERGE_MAX_INDEX,
                           MERGE_PRODUCT):
            errors.append(f"partial {p.name!r} has no declared merge rule "
                          f"({p.merge!r})")
    return errors
