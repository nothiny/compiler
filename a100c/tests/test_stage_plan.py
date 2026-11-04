#!/usr/bin/env python3
"""test_stage_plan.py -- the reduction stage plan (T009, gate G5).

  acceptance[3]: workspace ownership in the stage plan is disjoint per
      worker outside the declared merge; a plan violating ownership is
      rejected by this test.

  Also verified: the per-operation-and-dtype identity table (signedness-
      correct lattice bounds -- the AM0282 discipline), the declared
      tie-breaks and empty-extent results, the pure merge model against
      independent numpy oracles, the two-phase plan built from real TIR
      modules (the persistent accumulate form, the arg-select pair form,
      the plain block-reduction form and the ineligible forms), and the
      split-K feed's workspace contract.

Run: python3 a100c/tests/test_stage_plan.py   (exit 0 = all checks PASS)
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
sys.path.insert(0, str(ROOT / "ops" / "harness"))

import numpy as np  # noqa: E402

from a100c.frontend import lower_tir, source, specialize  # noqa: E402
from a100c.ir import tir  # noqa: E402
from a100c.plan import stages  # noqa: E402

FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(name)
    return ok


# ---------------------------------------------------------------------------
# The identity table: per operation and dtype, signedness-correct
# ---------------------------------------------------------------------------


def check_identity_table():
    """Every (op, dtype) identity is the lattice bound for the type's own
    signedness: a signed min reduces from INT_MAX, an unsigned min from
    all-ones, a float max from -inf -- never one constant for both
    signednesses (AM0282)."""
    bad = []
    cases = [
        # the min identity is the lattice TOP (min(x, id) = x needs
        # id >= x): INT_MAX signed, all-ones unsigned, +inf floating
        ("min", tir.INT8, 127), ("min", tir.INT16, 32767),
        ("min", tir.INT32, 2**31 - 1), ("min", tir.INT64, 2**63 - 1),
        ("min", tir.UINT8, 0xFF), ("min", tir.UINT16, 0xFFFF),
        ("min", tir.UINT32, 0xFFFFFFFF), ("min", tir.UINT64, 2**64 - 1),
        # the max identity is the lattice BOTTOM: INT_MIN signed, 0
        # unsigned, -inf floating
        ("max", tir.INT8, -128), ("max", tir.UINT8, 0),
        ("max", tir.INT32, -2**31), ("max", tir.UINT32, 0),
        ("max", tir.FLOAT16, float("-inf")),
        ("max", tir.BFLOAT16, float("-inf")),
        ("max", tir.FLOAT32, float("-inf")),
        ("min", tir.FLOAT32, float("inf")),
        ("min", tir.FLOAT16, float("inf")),
        ("sum", tir.FLOAT32, 0.0), ("sum", tir.INT32, 0),
        ("xor_sum", tir.INT32, 0), ("reduce_or", tir.UINT32, 0),
        ("cumsum", tir.INT32, 0), ("cumprod", tir.INT32, 1),
        ("cumprod", tir.FLOAT32, 1.0),
        ("argmin", tir.INT32, 2**31 - 1),  # the index lane's worst
    ]
    for kind, ty, want in cases:
        got = stages.identity_for(kind, ty)
        if got != want:
            bad.append(f"{kind}/{ty!r}: {got!r} != {want!r}")
    check("identity-table-per-op-and-dtype-signedness-correct", not bad,
          "; ".join(bad[:3]))

    # the same-name-different-signedness discipline: i32 vs u32 differ
    check("signed-and-unsigned-identities-differ",
          stages.identity_for("min", tir.INT32) !=
          stages.identity_for("min", tir.UINT32),
          f"{stages.identity_for('min', tir.INT32)} vs "
          f"{stages.identity_for('min', tir.UINT32)}")


def check_empty_extent_and_tie_break():
    """Empty-extent results are the exact identity (integer/index/boolean
    reductions have no tolerance); argmax/argmin declare the leftmost
    index among equal extrema (the pinned Triton 3.8 tie_break_left)."""
    check("empty-extent-sum-is-exact-identity",
          stages.empty_extent_result("sum", tir.INT32) == 0)
    check("empty-extent-min-is-exact-identity",
          stages.empty_extent_result("min", tir.INT32) == 2**31 - 1)
    check("empty-extent-arg-index-is-worst",
          stages.empty_extent_result("argmin", tir.INT32) == 2**31 - 1)
    spec = stages.REDUCTION_OPS["tl.argmax"]
    check("argmax-tie-break-left-is-the-declared-default",
          spec.tie_break_left is True)
    spec_min = stages.REDUCTION_OPS["tl.min"]
    check("min-return-indices-tie-break-left-declared",
          spec_min.index_form and spec_min.tie_break_left)
    # the merge model: leftmost index wins ties
    got = stages.merge_partials(stages.MERGE_MIN_INDEX, (3.0, 7), (3.0, 2),
                                tie_break_left=True)
    check("merge-tie-takes-the-left-index", got == (3.0, 2), str(got))
    got = stages.merge_partials(stages.MERGE_MAX_INDEX, (5, 4), (5, 1),
                                tie_break_left=True)
    check("merge-max-tie-takes-the-left-index", got == (5, 1), str(got))


def check_merge_model_against_numpy():
    """The pure merge model agrees with independent numpy oracles over
    random partials (the model the lowering emits natively)."""
    rng = np.random.default_rng(7)
    bad = []
    for _ in range(200):
        parts = rng.normal(2.0, 3.0, 5)
        merged = None
        for p in parts:
            merged = p if merged is None else \
                stages.merge_partials(stages.MERGE_SUM, merged, p)
        if abs(merged - parts.sum()) > 1e-9:
            bad.append("sum")
            break
    for _ in range(200):
        parts = rng.integers(-1000, 1000, 5)
        merged = None
        for p in parts:
            merged = int(p) if merged is None else \
                stages.merge_partials(stages.MERGE_MIN, merged, int(p))
        if merged != parts.min():
            bad.append("min-int")
            break
    # the argmin pair merge vs numpy's first-occurrence semantics
    for _ in range(200):
        xs = rng.integers(-5, 5, 32)
        best = (int(xs[0]), 0)
        for i in range(1, len(xs)):
            best = stages.merge_partials(stages.MERGE_MIN_INDEX, best,
                                         (int(xs[i]), i))
        want = int(np.argmin(xs))     # numpy: first occurrence
        if best[1] != want:
            bad.append(f"argmin-tie: {best[1]} != {want}")
            break
    # the argmax pair merge vs numpy's first-occurrence semantics
    for _ in range(200):
        xs = rng.integers(-5, 5, 32)
        best = (int(xs[0]), 0)
        for i in range(1, len(xs)):
            best = stages.merge_partials(stages.MERGE_MAX_INDEX, best,
                                         (int(xs[i]), i))
        want = int(np.argmax(xs))
        if best[1] != want:
            bad.append(f"argmax-tie: {best[1]} != {want}")
            break
    # xor / or merges are exact
    for _ in range(100):
        parts = rng.integers(0, 2**31, 4, dtype=np.int64)
        mx = None
        mo = None
        for p in parts:
            mx = int(p) if mx is None else \
                stages.merge_partials(stages.MERGE_XOR, mx, int(p))
            mo = int(p) if mo is None else \
                stages.merge_partials(stages.MERGE_OR, mo, int(p))
        if mx != int(np.bitwise_xor.reduce(parts.astype(np.int64))) or \
                mo != int(np.bitwise_or.reduce(parts.astype(np.int64))):
            bad.append("bit-merge")
            break
    check("merge-model-matches-independent-oracles", not bad,
          "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# Workspace ownership (acceptance[3])
# ---------------------------------------------------------------------------


def check_workspace_ownership():
    """Per-worker regions are disjoint outside the declared merge at every
    worker count; slots fit their region; a hand-built violating plan is
    REJECTED by the validation."""
    bad = []
    for workers in (1, 2, 4, 8):
        for sizes in ([4], [4, 8], [8, 8, 8], [4, 4, 4, 4]):
            layout = stages.WorkspaceLayout.for_partials(sizes, workers)
            ok, why = layout.validate()
            if not ok:
                bad.append(f"W={workers} sizes={sizes}: {why}")
            # the per-worker regions are disjoint: no byte is written by
            # two workers outside the merge
            regions = [layout.region_of(w) for w in range(workers)]
            for i, a in enumerate(regions):
                for b in regions[i + 1:]:
                    if a.worker != b.worker and a.overlaps(b):
                        bad.append(f"W={workers}: workers {a.worker}/"
                                   f"{b.worker} overlap")
            # every slot address of every worker lands in that worker's
            # own region
            for w in range(workers):
                for slot in range(len(sizes)):
                    addr = layout.slot_address(w, slot)
                    if not regions[w].contains(addr, 1):
                        bad.append(f"W={workers} slot {slot} outside "
                                   f"worker {w}'s region")
    check("workspace-ownership-disjoint-per-worker", not bad,
          "; ".join(bad[:3]))

    # a violating plan is rejected: overlapping slots inside one worker
    violating = stages.TwoPhasePlan(
        eligible=True,
        partials=(stages.PartialSpec(1, "a", stages.MERGE_SUM, tir.FLOAT32),
                  stages.PartialSpec(2, "b", stages.MERGE_SUM, tir.FLOAT32)))
    violating.layout = stages.WorkspaceLayout(
        slots=(0, 4), slot_sizes=(8, 8), workers=8, stride=8, total_bytes=64)
    errors = stages.validate_stage_plan(violating)
    check("violating-ownership-plan-rejected", bool(errors),
          "; ".join(errors[:1]))

    # a slot spilling into the next worker's region is rejected
    spill = stages.TwoPhasePlan(
        eligible=True,
        partials=(stages.PartialSpec(1, "a", stages.MERGE_SUM, tir.FLOAT32),))
    spill.layout = stages.WorkspaceLayout(slots=(0,), slot_sizes=(16,),
                                          workers=4, stride=8, total_bytes=32)
    errors = stages.validate_stage_plan(spill)
    check("slot-spilling-into-neighbour-region-rejected",
          any("spills" in e for e in errors), "; ".join(errors[:1]))

    # a plan whose total cannot hold every region is rejected
    short = stages.TwoPhasePlan(
        eligible=True,
        partials=(stages.PartialSpec(1, "a", stages.MERGE_SUM, tir.FLOAT32),))
    short.layout = stages.WorkspaceLayout(slots=(0,), slot_sizes=(8,),
                                          workers=8, stride=8, total_bytes=16)
    errors = stages.validate_stage_plan(short)
    check("undersized-workspace-plan-rejected", bool(errors),
          "; ".join(errors[:1]))

    # an eligible plan without a declared layout is rejected
    nolayout = stages.TwoPhasePlan(
        eligible=True,
        partials=(stages.PartialSpec(1, "a", stages.MERGE_SUM, tir.FLOAT32),))
    errors = stages.validate_stage_plan(nolayout)
    check("plan-without-layout-rejected",
          any("layout" in e for e in errors), "; ".join(errors[:1]))

    # an invalid worker count is rejected (F053)
    badcount = stages.WorkspaceLayout(slots=(0,), slot_sizes=(8,),
                                      workers=3, stride=8, total_bytes=24)
    ok, why = badcount.validate()
    check("non-1-2-4-8-worker-plan-rejected", not ok, why)

    # a well-formed plan validates at every worker count
    good = stages.TwoPhasePlan(
        eligible=True,
        partials=(stages.PartialSpec(1, "acc", stages.MERGE_SUM,
                                     tir.FLOAT32),))
    good.layout = good.layout_for(8)
    bad = [f"W={w}: {stages.validate_stage_plan(good, w)}"
           for w in (1, 2, 4, 8) if stages.validate_stage_plan(good, w)]
    check("well-formed-plan-validates-at-1-2-4-8", not bad,
          "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# The two-phase plan built from real TIR modules
# ---------------------------------------------------------------------------

TEMPLATE = ('"""probe operator %s"""\n'
            'OPERATOR = {"name": "probe/%s", "group": "probe", "channel": "local",\n'
            '            "execution": "triton_kernel", "verification": "correctness",\n'
            '            "tags": []}\n'
            'SHAPES = ((257,),)\n'
            'import numpy as np\n'
            'import triton\n'
            'import triton.language as tl\n'
            '\n'
            '@triton.jit\n'
            'def %s_kernel(x_ptr, o_ptr, n, BLOCK: tl.constexpr):\n'
            '%s\n'
            '\n'
            'def ref(args, meta):\n'
            '    return {"o_ptr": np.zeros(4, np.float32)}\n'
            '\n'
            'def _make_case(shape=(257,), dtype="float32", seed=0):\n'
            '    return {"args": {"x_ptr": np.zeros(4, np.float32),\n'
            '                     "o_ptr": np.zeros(4, np.float32), "n": 16},\n'
            '            "meta": {"BLOCK": 128}, "grid": (1,)}\n')


def _lower(body: str):
    text = TEMPLATE % ("plan", "plan", "plan", textwrap.indent(body, "    "))
    src = source.load_operator_text(text, "<plan>", "plan.py")
    case = {"args": {"x_ptr": np.zeros(16, np.float32),
                     "o_ptr": np.zeros(16, np.float32), "n": 16},
            "meta": {"BLOCK": 128}, "grid": (1,), "outputs": ("o_ptr",)}
    spec = specialize.specialize(src, case)
    module = lower_tir.lower(src, spec)
    return module, tir.verify_module(module)


def check_two_phase_plan_forms():
    """The plan analysis classifies the corpus persistent-reduction forms:
    the accumulate loop (vdot), the arg-select pair loop (argmin), the
    plain block reduction; elementwise and store-after-reduction forms
    with no escaping partial are ineligible (with a reason)."""
    mod, errs = _lower("""
        acc = tl.zeros([], dtype=tl.float32)
        for start in range(0, n, BLOCK):
            i = start + tl.arange(0, BLOCK)
            x = tl.load(x_ptr + i, mask=i < n, other=0.0)
            acc += tl.sum(x, axis=0)
        tl.store(o_ptr, acc)
    """)
    check("vdot-form-lowers-and-verifies", not errs, str(errs[:1]))
    plan = stages.build_stage_plan(mod)
    ok = plan.eligible and len(plan.partials) == 1 and \
        plan.partials[0].merge == stages.MERGE_SUM
    check("vdot-form-plan-eligible-sum-merge", ok, plan.describe()["reason"])
    check("vdot-form-plan-validates",
          not stages.validate_stage_plan(plan))

    mod2, errs2 = _lower("""
        best_val = float('inf')
        best_idx = 0
        for start in range(0, n, BLOCK):
            offs = start + tl.arange(0, BLOCK)
            vals = tl.load(x_ptr + offs, mask=offs < n, other=float('inf'))
            local_min = tl.min(vals, axis=0)
            local_arg = tl.argmin(vals, axis=0)
            cond = local_min < best_val
            best_val = tl.where(cond, local_min, best_val)
            best_idx = tl.where(cond, start + local_arg, best_idx)
        tl.store(o_ptr, best_idx)
    """)
    check("argmin-form-lowers-and-verifies", not errs2, str(errs2[:1]))
    plan2 = stages.build_stage_plan(mod2)
    ok2 = plan2.eligible and plan2.partials and \
        plan2.partials[0].merge == stages.MERGE_MIN_INDEX and \
        plan2.partials[0].pair_value_id is not None
    check("argmin-form-plan-eligible-pair-merge", ok2,
          str([p.describe() for p in plan2.partials]))
    check("argmin-form-plan-validates",
          not stages.validate_stage_plan(plan2))

    mod3, errs3 = _lower("""
        i = tl.arange(0, BLOCK)
        x = tl.load(x_ptr + i, mask=i < n, other=0.0)
        s = tl.sum(x, axis=0)
        tl.store(o_ptr, s)
    """)
    check("block-reduction-form-lowers-and-verifies", not errs3,
          str(errs3[:1]))
    plan3 = stages.build_stage_plan(mod3)
    ok3 = plan3.eligible and plan3.partials and \
        plan3.partials[0].merge == stages.MERGE_SUM
    check("block-reduction-form-plan-eligible", ok3, plan3.describe()["reason"])
    check("block-reduction-form-plan-validates",
          not stages.validate_stage_plan(plan3))

    # ineligible: elementwise only (nothing to merge)
    mod4, errs4 = _lower("""
        i = tl.arange(0, BLOCK)
        x = tl.load(x_ptr + i, mask=i < n, other=0.0)
        tl.store(o_ptr + i, x)
    """)
    plan4 = stages.build_stage_plan(mod4)
    check("elementwise-form-plan-ineligible-with-reason",
          (not plan4.eligible) and bool(plan4.reason), plan4.reason)

    # ineligible: a carried update without merge semantics that escapes
    mod5, errs5 = _lower("""
        acc = tl.zeros([], dtype=tl.float32)
        for start in range(0, n, BLOCK):
            i = start + tl.arange(0, BLOCK)
            x = tl.load(x_ptr + i, mask=i < n, other=0.0)
            acc = acc - tl.sum(x, axis=0)
        tl.store(o_ptr, acc)
    """)
    plan5 = stages.build_stage_plan(mod5)
    check("non-reduction-carried-update-refuses-the-split",
          (not plan5.eligible) and "merge rule" in plan5.reason, plan5.reason)


def check_split_k_feed():
    """The split-K feed model: partial tiles in owned workspace regions,
    summed under the accumulation dtype (exact for the integer modular
    accumulator, F051)."""
    feed = stages.SplitKFeed(m=8, n=16, acc_dtype=tir.INT32)
    layout = feed.layout_for(8)
    ok, why = layout.validate()
    check("split-k-feed-workspace-owns-disjoint-regions", ok, why)
    check("split-k-feed-merges-by-exact-sum",
          feed.merge_rule() == stages.MERGE_SUM)
    check("split-k-feed-partial-tile-size",
          feed.partial_bytes() == 8 * 16 * 4,
          str(feed.partial_bytes()))
    # the integer merge is exact (modular): random partials summed in
    # int32 wrap exactly like the hardware's 32-bit accumulator (F051)
    rng = np.random.default_rng(3)
    parts = rng.integers(-2**31, 2**31 - 1, 4, dtype=np.int64)
    merged = None
    for p in parts:
        merged = int(p) if merged is None else \
            stages.merge_partials(stages.MERGE_SUM, merged, int(p))
    want = int(np.sum(parts.astype(np.int32), dtype=np.int32))
    got = ((int(merged) + 2**31) % 2**32) - 2**31
    check("split-k-integer-merge-is-modular-exact",
          got == want, f"{got} vs {want}")


def main() -> int:
    check_identity_table()
    check_empty_extent_and_tie_break()
    check_merge_model_against_numpy()
    check_workspace_ownership()
    check_two_phase_plan_forms()
    check_split_k_feed()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_stage_plan: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
