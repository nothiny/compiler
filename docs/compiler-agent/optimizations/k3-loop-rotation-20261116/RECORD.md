# OPT-2026-11-16-K3-LOOP-ROTATION — the mir-optimize stage: loop rotation
(opt-in) + the edge-reload deferral (default on)

Status: **accepted** — the round lands the project's first MIR-level
optimization stage (contract-revised, independently testable) with its
mir-loop-predicate pass measured honestly as OPT-IN (default off), plus
two default-on emission improvements the round's investigation produced
(the edge-reload deferral and the compare+branch fusion's reload
walk-back): attention -2.79% at the default configuration vs the
branch-fuse round's final, with the off-control byte-identical. Full
validation chain green except the two recorded pre-existing failures;
full-input regression bound below.

## Goal and outcome

Human-directed round two through the develop-optimization-pass skill,
with the explicit priority: a compiler-optimization PASS first,
instruction-level work second. Baseline tree 0b5656c (the branch-fuse
round). Candidate tree = baseline + this round.

## Why this optimization

The branch-fuse round left the loop-control sequence at three
instructions per iteration (head: compare+branch; body: back-edge jump).
The dynamic `j` census (from the branch-fuse final metrics): attention
446,785/call (2.92%), the paired set 1-2.9% — the back edges' share. The
recorded design (DESIGN-ISSUE-mir-optimize.md, pass 3: mir-loop-
predicate) had never been implemented; unlike mir-vsetvli-hoist it has
no recorded blocker. The vsetvli class (2.40M/call, 15.7%) remains
blocked by the regions-do-not-cross-blocks invariant.

## Transformation and reuse contracts

### The mir-loop-predicate pass (the declared mir-optimize stage, OPT-IN:
A100C_MIRPASS_PRED=on, default off)

- **Match**: a natural loop over the explicit MIR CFG with exactly one
  body block B (its terminator the single back edge `br V -> H`); a
  unique preheader P (`br INIT -> H`); H's non-terminator ops empty (the
  while form: the brc reads params[0]) or sconst materializations
  feeding exactly one slt/sltu over head params and loop-invariant
  values (the counted form -- the bound constant is materialized inside
  the head); H's brc true-args the identity head params and false-args a
  substitutable list (head params or loop-invariant values -- the chunk
  loops' `(pid, items)` exit convention); the exit's arity equal to the
  false-arg count.
- **Legality**: the rotated condition reads exactly the values the
  original read at the same iteration boundaries (the single-back-edge
  form makes head-entry values and previous back-edge values the same
  sequence); zero-trip safety is preserved by the preheader guard on the
  initial values; only scalar ops are moved/duplicated (no vsetvli
  region crosses a block -- the MIR invariant holds); H becomes
  unreachable and is removed; the MIR verifier runs on the stage's
  output in the pipeline (a witness test proves it load-bearing).
- **Transform**: P computes the guard (the condition on INIT) and
  branches to B/E; B's back edge becomes the conditional branch (the
  condition on V, at the body's end); H is deleted. Per iteration one
  unconditional jump and one block disappear; the emitter's
  compare+branch fusion applies to both new pairs.
- **Profitability (measured — the honest reason it is opt-in)**: the
  structural win is real (attention's j class -94,720/call, branch
  category -10.1%) but on allocation-pressure-heavy cases the coloring
  perturbation of the changed CFG shape adds moves that offset it
  (attention mv +120,310/call; net +0.04%; the same allocation-
  perturbation class the k3 rounds recorded). Low-pressure cases net
  positive (softmax -0.58%, synth -0.36% pre-deferral). Default OFF;
  one allocator-stability fix (the recorded 649k-reload-boundary lead)
  away from default-on.
- **Refusal** (counted per reason): multi-block bodies (the guarded
  narrow-access loops, the outer program/item loops), heads carrying
  more than the condition computation, non-substitutable false args,
  cond operands defined inside the loop, arity mismatches.
- **Analysis deps**: the MIR-CFG natural-loop analysis (module-local;
  this round fixed its self-loop handling -- a rotated body is a
  self-loop and the textbook walk must not run when the back edge's
  source equals its target, or the loop's external entry is swallowed);
  invalidates nothing downstream (runs before legalise/select/allocate,
  which recompute).
- **Placement**: the new mir-optimize stage between lowering and
  legalisation (contract-revised: stage + pass + test declared; the
  first MIR-level optimization stage; the unwired mir-licm machinery
  stays recorded as measured-negative).

### The edge-reload deferral (default ON: A100C_EDGE_RELOAD=off restores)

- **Match**: an emitter block whose contiguous tail before a brc holds
  scalar sreloads whose fresh results feed only that brc's edge args
  (not its condition) — the allocator's block-scoped reload placement
  for spilled edge-arg values (the chunk heads' pid reload).
- **Legality**: the reload reads only the spill slot (position-
  independent) and its result's live range only shrinks (the
  allocator's fresh-vreg-per-block property makes its uses exactly the
  terminator's edge args); a value consumed by both edges is reloaded
  on each path (the load is idempotent).
- **Transform**: the reload is emitted inside the consuming edge's move
  sequence instead of before the branch.
- **Profitability (measured)**: head-test loops stop reloading per
  iteration (attention scalar-load 683k -> 486k/call) AND the compare
  directly feeding the branch is no longer separated from it — which
  unblocks the compare+branch fusion (the walk-back extension below);
  attention scalar-arith 6.27M -> 5.94M/call.
- **Refusal**: non-tail reloads, reloads feeding the condition,
  vector reloads (region discipline) — all keep today's placement.
- **Analysis deps**: per-block MIR tail scan at emission; invalidates
  nothing.
- **Placement**: the emitter's brc arm — the placement decision exists
  only at emission (the allocator's op is position-fine; the cost is
  the dynamic path).

### The fusion walk-back (extends OPT-BRANCH-FUSE, default on with it)

The compare+branch fusion's MIR-level candidate detection now walks
back over exactly the sreloads the deferral will move (same conditions,
gated on the deferral switch): a head like
`[sconst, slt, sreload, brc]` now fuses (the emitted look-back sees the
slt as the last line). With the deferral off, the pair stays unfused —
consistent with the emission-time look-back.

## Validation and measurements

Commands and raw evidence under `evidence/` in this directory. All
compilations through the normal factory path; comparisons under each
case's own policy.

- **Tests**: the new declared `a100c/tests/test_mir_passes.py` all PASS
  (the three lowered loop forms rotate and verify; the structural
  refusals; the verifier witness — a rotation dropping an edge arg is
  rejected; the stage's default-off/opt-in behavior, distinct cache
  keys; execution match at 1 and 4 workers in both configurations; the
  deferral's form and its off-control). The twelve-suite battery all
  PASS (test_branch_fuse, test_emit, test_local_materialization,
  test_k3_lowering_optimizations, test_control_flow, test_lower_scalar,
  test_guarded_narrow_access, test_backend_vector_state,
  test_driver_cache, test_e2e_slice, test_elementwise_width,
  test_chunk_geometry_boundary). test_passes_basic fails exactly its
  two pre-existing checks (the vdot harness drift, recorded last round).
- **Witnesses**: no-name-dispatch positive 0 / witness caught; numeric
  policy and stage barriers positive 0; masked-tails real artifact PASS
  with the guard intact and the degraded build corrupting it as
  required (the stage-barrier witness's pre-existing sensitivity
  remains recorded, unchanged by this round).
- **Off-control**: with A100C_EDGE_RELOAD=off (rotation already
  default-off) the instruction stream is byte-identical (same staging
  identity) to the branch-fuse round's final artifact — the rollback is
  exact.
- **Multi-worker**: 81/81 PASS at threads 2/4/8 (attention,
  flash_decode, vdot_kernel_complex, frobenius two-phase) at the default
  configuration, plus 12/12 with the rotation opted in at 8 threads.
- **Paired metrics** (per-call guest dynamic instructions; the default
  configuration vs the branch-fuse round's final, and the rotation's
  opt-in marginal at the same tree):

  | case | prev round | default | def delta | rotation on | rot margin |
  |---|---:|---:|---:|---:|---:|
  | attention [4,4,32,64] f16 | 15,242,311 | 14,822,471 | **-2.75%** | 14,828,874 | +0.04% |
  | flash_decode [2,2,32,32] bf16 | 106,587 | 106,607 | +0.02% | 106,644 | +0.03% |
  | linear-dropout [16,128,128] f16 | 6,610,023 | 6,610,031 | 0.00% | 6,615,431 | +0.08% |
  | matmul16 [16,16,16] f16 | 22,339 | 22,085 | **-1.14%** | 22,341 | +1.16% |
  | softmax-inner [97] f16 | 8,401 | 8,132 | **-3.20%** | 8,237 | +1.30% |
  | softmax_log [4,97] f32 | 119,083 | 119,083 | 0.00% | 119,139 | +0.05% |
  | softmax [20,17] f16 | 73,076 | 73,060 | -0.02% | 72,638 | **-0.58%** |
  | synthesis [1,4,16,64] f32 | 203,396 | 203,396 | 0.00% | 202,636 | **-0.37%** |

  Aggregate: **-1.88% at the default configuration, no regression**
  (flash_decode's +0.02% is noise-level; the 0.00% cases carry no
  deferred-reload pattern). The rotation's aggregate marginal is +0.05%
  — the measured basis of its default-off decision: structurally
  positive (softmax -0.58%, synth -0.37%) but pressure-perturbed
  (attention +0.04%, matmul16 +1.16%, softmax-inner +1.30%). Judge
  quantity is the calibrated per-call guest dynamic instruction count;
  no wall-clock or board claim.

- **Full-input regression**: run `looprot-full` — **2,734 cases: 2,728
  PASS + 6 TIMEOUT, exactly the pre-existing six** (complex_svd [17]
  ×3 + deconv3d [1,4,8,8,8] ×3; chunk_gdn2's budget-marginal cases all
  PASS), **zero new non-PASS**. The eight shards covering 2,719 cases
  PASS 2,719/2,719; the three budget-marginal operators ran serially.
  Evidence: `evidence/full-input/shard0..7/` + `marginal/`.
- **Compile time (an in-round catch, repaired)**: the first wiring ran
  the stage's MIR verification UNCONDITIONALLY (to record the disabled
  state) — a third verify_module on chunk_gdn2's ~40k-op module cost
  ~5-8s, a measured +8.5s (+5.1%) on the heaviest identity (176.0s vs
  the previous commit's 167.5s, same method, same machine; the earlier
  162.9s/164.5s numbers were pre-drift). Root-caused by profiling
  (verify_module x3 in the cumulative top ranks), repaired as
  verify-only-when-the-pass-ran (the disabled stage mutates nothing —
  the module is byte-identical to the just-verified lowering output);
  re-timed 163.7s, back at parity. The repair changes no generated
  program (a check, not a transform), so the full-input evidence above
  remains valid; the scan ran with the slower compile and passed
  everything but the known six.

## Good and bad practices (this round's lessons)

- **Measure the marginal, not the mechanism** (observed): the rotation
  removes 94.7k jumps/call on attention and still nets +0.04% — an
  equally real +120k move perturbation from the allocator's recoloring.
  A pass's profitability field must carry the measured NET, and the
  default must follow it (opt-in here), or the structural argument
  ships a wash as a win.
- **A new CFG shape audits its own analysis** (observed): the rotation's
  self-loops exposed a latent bug in the natural-loop construction (the
  textbook walk must not run for a self edge). Every transform that
  creates a first-of-its-kind shape should re-derive its analysis
  invariants on that shape.
- **One placement decision can block two optimizations** (observed):
  the allocator's before-branch reload placement both cost a load per
  iteration AND sat between every compare and its branch — the deferral
  fixed the measurement (hot-path loads) and unblocked the fusion
  (walk-back) in one move. Placement questions deserve the same
  structural scrutiny as count questions.

## Migration recipe

The rotation needs: explicit-CFG blocks with param-carrying terminators
(br/brc with per-target args); a natural-loop analysis (dominators +
back edges, self-edge-safe); the head's condition chain as data (pure
ops over params and invariants); a preheader concept (single outside
predecessor). The deferral needs: the emitter to see the terminator's
arg lists and the block's tail ops; a spill-slot load form; the
fresh-value-per-block property of inserted reloads (or an equivalent
use-locality proof).

## Replay

```bash
set -a; . ./.env; set +a
# the default configuration's paired contrast vs the previous round
python3 -B tools/profiling/collect_metrics.py \
  --operator suite/perf/attention_forward_triton.py --shape 4,4,32,64 \
  --dtype float16 --threads 1 --out <dir>
# the rotation's marginal (opt-in side)
A100C_MIRPASS_PRED=on python3 -B tools/profiling/collect_metrics.py \
  --operator suite/perf/attention_forward_triton.py --shape 4,4,32,64 \
  --dtype float16 --threads 1 --out <dir>
# the off-control (byte-identical to the previous round's emission)
A100C_EDGE_RELOAD=off python3 -B tools/profiling/collect_metrics.py \
  --operator suite/perf/attention_forward_triton.py --shape 4,4,32,64 \
  --dtype float16 --threads 1 --out <dir>
# the round's tests
python3 -B a100c/tests/test_mir_passes.py
python3 -B a100c/tests/test_branch_fuse.py
```

Baseline root: 0b5656c. Candidate root: this round's tree. Skill:
develop-optimization-pass (loaded in the working session, second round
through it).
