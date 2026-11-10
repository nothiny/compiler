# DesignIssue: the mir-optimize stage (W3 of the unified optimization round)

Status: **proposed** — drafted under direct human guidance (the unified
optimization plan, `UNIFIED-OPTIMIZATION-PLAN.md` §2.W3) while the engine
is occupied with the correctness repair stream (T044). The independent
review is performed by a read-only reviewer session before implementation;
engine-level reconciliation of this contract revision is recorded as a
follow-up (the engine's workflow_issue route is refused while a task
attempt is open, and its repair budget is correctness-scoped).

## Observed (quantified evidence)

Post-lowering loop-body rematerialization is the largest remaining
per-call dynamic-instruction cost class in the measured families, and it
is invisible to every declared TIR pass (the TIR pipeline runs before the
cost is created; TIR LICM fired=0 on the affected corpora):

- sconst constant rematerialization: 15-27% of per-call guest dynamic
  instructions (linear-dropout softmax f16: 4.09M of 15.33M).
- vsetvli region churn: 7-15% (the same case: 2.11M = 14%).
- per-iteration address multiply trees and slt+bne predicate pairs:
  8-15% + branch classes (matmul k64: 73728 slt+bne pairs per call).
- allocator "store at block entry, reload before every use" traffic:
  2-10% ([op-1] "frame" attribution: 522K/call on the matmul flagship).

Sources: `docs/compiler-agent/optimizations/UNIFIED-OPTIMIZATION-PLAN.md`
§1.2 (the cross-family bottleneck taxonomy), the matmul round's
`matmul/baseline/` profile artifacts, `/tmp/attn_metrics/` (6 attention
cases), the softmax round's W2/W3 quantification. All measurements are
the declared proxy metric (per-call guest dynamic instructions, calibrated
QEMU plugin), not wall-clock.

## Root cause

The lowering emits loop bodies that re-materialize loop-invariant scalars,
addresses, predicates and region settings on every iteration. The declared
pipeline has no MIR-level optimization stage: mir/v1's pass list is empty,
so nothing between lowering and legalisation can move or simplify this
work. The emitter's peephole (OPT-2026-11-10-EMIT-PEEPHOLE) only removes
static duplicates inside a block; the cost is dynamic, inside loop bodies.

## Proposed change

A new pipeline stage **mir-optimize** (mir/v1 → mir/v1) between `lowering`
and `legalisation`, owned by one new module
`a100c/passes/mir_optimize.py` (MIR-CFG loop analysis + four passes):

1. **mir-licm** — loop-invariant code motion over the MIR CFG. Natural
   loops from back-edges + dominators (the explicit CFG and block
   parameters carry the structure). Legality: only speculatable pure
   integer/scalar operations and sconst rematerializations are hoisted
   (RISC-V integer add/mul/div do not trap; division-by-zero is not a
   trap on this target); **memory accesses are never hoisted** (no
   speculative faults); vsetvli is hoisted only under the per-point
   region-state model (see pass 4).
2. **mir-strength-reduction** — affine induction variables on back-edges
   (i = i + c) become block-parameter pointer recursions (p += S),
   replacing per-iteration base + i*S address multiply trees. The
   induction variable remains maintained when it has uses besides the
   address; otherwise it is dropped. `begin_counted_loop`'s bounds are
   the analysis input.
3. **mir-loop-predicate** — counted-loop predicate resolution + loop
   rotation: when the trip count is known at the loop head, the
   per-iteration slt+bne pair folds away (one test per loop instead of
   one per iteration); zero-trip safety is preserved by the rotated
   guard.
4. **mir-vsetvli-hoist** — a vsetvli whose (SEW, LMUL, vl) region is
   invariant across a loop body and unopposed by any region-switching
   operation inside it is hoisted to the preheader. Region consistency
   is a MIR verifier invariant; the pass models the region state per
   program point (the stage's principal technical risk — guarded by the
   verifier and witness tests).

## Contract impact (exact field changes)

`ARCHITECTURE_CONSTRAINTS.json` (root + docs copy, byte-identical):

1. `modules` += `a100c/passes/mir_optimize.py` (responsibility: MIR-CFG
   loop analysis and the four mir-optimize passes; loop-invariant motion
   under speculation and region-consistency legality).
2. `stages` += `mir-optimize` between `lowering` and `legalisation`
   (module `a100c/passes/mir_optimize.py`, mir/v1 → mir/v1, tests
   `a100c/tests/test_mir_passes.py`).
3. `ir_levels[MIR].passes` = ["mir-licm", "mir-strength-reduction",
   "mir-loop-predicate", "mir-vsetvli-hoist"] (was empty).
4. `passes` += four entries (module `a100c/passes/mir_optimize.py`,
   ir mir/v1, stage mir-optimize, optional false, per-pass off-switches
   `A100C_MIRPASS_LICM/SR/PRED/VSETVLI=off`, trace counters
   `pass.mir.*`, profitability as above).
5. `validation_checks` += `mir-passes-legality-and-results` →
   `a100c/tests/test_mir_passes.py`.

The generated AGENTS.md block is re-rendered to match. No existing
module, stage, pass or test entry changes.

## Decisions taken (for the reviewer)

- **One module, four pass entries.** The four passes share the MIR-CFG
  loop analysis (natural loops, dominators, per-point region state);
  a single `a100c/passes/mir_optimize.py` keeps the module list growth
  minimal while the declared-pass entries (the schema's per-pass
  switch/trace/profitability fields) stay per-pass.
- **`a100c/passes/analyses.py` is NOT changed.** Its declared analyses
  (dominance, liveness, loop structure, memory effects) are the TIR pass
  infrastructure with a TIR-scoped invalidation contract; the MIR-CFG
  analysis is local to the new module (different graph structure, no
  shared invalidation surface).
- **optional: false (default-on with off-switch)** for all four passes,
  mirroring the six TIR passes: they run in the normal pipeline, each
  with an `A100C_MIRPASS_*=off` escape hatch that lands in the artifact
  identity (the rollback path). This creates the same correctness
  obligation the TIR passes carry: the full-input regression must pass
  with them enabled.
- **No master switch declared.** The per-pass switches follow the
  `A100C_PASS_*` pattern exactly; a composite `A100C_MIR_OPT=off` would
  be redundant with four off-switches and is not part of the contract.
- **Stage position.** Between lowering and legalisation: the passes
  consume the lowered CFG form and must run before legalisation fixes
  forms into repertoire-legal sequences ( LICM/SR rewrites would fight
  the legaliser's expansions after that point).

## Migration / rollout

- Implementation adds the module + the stage call site in the compile
  pipeline (`a100c/driver.py` `_compile_into` and `a100c/factory.py`,
  after the mir verifier, before legalisation). `compiler_revision`
  covers `a100c/passes/mir_optimize.py` only if it is added to
  `_REVISION_FILES` — the revision list gains the new pass module (the
  same list already names every pass module).
- Cache invalidation: compiler_revision changes → all artifacts rebuild
  (the established behavior for every compiler change).
- Rollback: per-pass `A100C_MIRPASS_*=off` (in the artifact identity) or
  `git revert` of the implementation commit.
- The declared test `a100c/tests/test_mir_passes.py` does not exist until
  implementation; the architecture check's declaration-only mode treats a
  declared-but-missing path as pending, and the review is asked to accept
  the declaration on that basis (the same posture the original G3 review
  applied to pre-implementation declarations).

## Regression risks and guards

| Risk | Guard |
|---|---|
| Region-consistency violation by mir-licm / mir-vsetvli-hoist | the MIR verifier runs on the stage's output in the pipeline; witness tests in test_mir_passes.py inject a region-inconsistent hoist and must be caught |
| Speculated operation traps | only provably non-trapping integer/scalar ops are hoisted; memory ops never; witness test |
| Address-equivalence break in mir-strength-reduction | i64 whole-tree address recomputation check (the declared independent index-computation check) plus per-case comparison in the family scans |
| Zero-trip loop safety lost by rotation | predicate-resolution legality requires the counted-loop bounds; witness test with a zero-trip loop |
| Register pressure increase from hoisted values | the allocator's spill path is correctness-preserving; spill counters are monitored in the metrics, not a gate |

## Review mechanism note

Direct human-guided round: the review is a fresh read-only reviewer
session over this record plus the revised contract (both JSON copies +
the AGENTS.md render), returning PASS / REQUEST_CHANGES / BLOCKED with
evidence. A recorded engine-side reconciliation (re-running the engine's
architecture review over the same revision) is noted as a follow-up for
whenever the engine is free; this document and the byte-identical copies
are the artifacts both reviews consume.
