# OPT-2026-11-15-K3-BRANCH-FUSE — emission-stage branch-control simplification

Status: **accepted** — the two rules fire across every measured loop-bearing
case, 7 of 8 paired cases improve (-1.78%..-4.45% per-call guest dynamic
instructions, the eighth within the measured noise envelope), the full-input
regression at the final revision is 2,728/2,734 PASS with exactly the
pre-existing six TIMEOUTs and zero new non-PASS, and the validation chain is
green except two recorded pre-existing failures (see Validation). One
compile-time defect of the first implementation (an O(branches × lines)
referent rescan) was caught BY the full-input run's case budget, root-caused
by paired timing against HEAD, and repaired in-round with identical emitted
code (see Compile-time impact).

## Goal and outcome

Human-directed first round through the new `develop-optimization-pass` skill:
build the skill, then use it to land one complete optimization. Baseline
tree 57f3c37 (the store-half round's HEAD); candidate tree = baseline +
this round (emit.py / driver.py / factory.py / test_emit.py adaptation /
new test module + census tool). Switch: `A100C_BRANCH_FUSE=off` restores the
pre-round emission (in the artifact identity; the off build's instruction
stream was verified byte-identical to a pre-edit same-identity build).

## Why this optimization

Census of a fresh `ops/suite/perf/attention_forward_triton.py` [4,4,32,64]
f16 compile at the baseline tree: the brc emitter's per-edge argument-move
placement (emit.py's brc arm) makes every taken edge route through a stub
block; 26 brc sites, 25 bare stubs (one bare `j`), 8 with the condition
computed by an immediately preceding `slt`. Every loop-head iteration
therefore paid `slt + bne + j(stub)` — three control instructions where one
suffices. No existing peephole touched branches (the seven existing rules
cover vsetvli/li/splat forms). The branch category was 1.32M of attention's
15.83M per-call instructions (8.4%) and up to 87.8% on small loop-dominated
cases (softmax-inner [97]).

## Transformation and reuse contract

Two rules at the emission stage, one switch, counters in
`artifact.json stages.emission.peephole_branch` and per-site
`[peephole-stub]` / `[peephole-cmpfuse]` trace comments.

### Rule 1: bare-stub elimination

- **Match**: an emitted conditional branch (`bne/beq/blt/bge/bltu/bgeu`)
  targeting a `.LbrcN_true` stub whose block contains exactly one
  instruction `j T` and nothing else (the edge's argument moves were empty).
- **Legality**: the stub is a pure trampoline — every path through it
  continues to T with no state change; retargeting preserves all paths.
  Guards: (a) the retargeted conditional must stay inside the CB-format
  ±4 KiB displacement, bounded conservatively at 4 bytes per emitted line
  between branch and target (comments/labels emit nothing); (b) the stub
  label has no referent other than this branch (symbol-boundary lookaround
  count == 2: the branch + the label definition; a `\b` boundary never
  matches before the label's leading dot — the first implementation's
  refusal bug, caught by the all-declined counters in smoke).
- **Transform**: branch target becomes T; the stub label and jump become
  trace comments (op indices preserved).
- **Profitability**: pure removal of one unconditional jump per dynamic
  execution of the taken edge — no allocation, layout or liveness effect.
- **Refusal** (counted as `stubs_declined`): stubs carrying argument moves
  (exactly 1 per measured case — the argument-carrying brc), out-of-range
  targets, multiply-referenced labels.
- **Analysis deps**: consumes the final emitted stream; invalidates nothing
  (runs before the existing `_peephole`, whose state resets make the passes
  commute; deleted `j`/label lines became comments, which reset the same).
- **Placement**: emitter peephole — the stub exists only because the brc
  emitter places per-edge moves after the branch; no earlier stage can see
  it.

### Rule 2: compare+branch fusion

- **Match**: an MIR `slt`/`sltu` immediately before a `brc` in the same
  block whose condition vreg is read nowhere else in the module (exact
  def-use count over operands AND br/brc edge args — the loop head passes
  only the induction, not the cond), plus the textual verification that the
  emitted stream still shows `slt rd, a, b` directly followed by
  `bne rd, zero, L`.
- **Legality**: the compare's value has exactly one reader (the branch);
  deleting it removes a dead write, and the fused `blt/bltu a, b, L` reads
  exactly the two sources the compare read at the adjacent position.
  Adjacency (no label, no scheduled instruction between) is load-bearing: a
  label between means control can reach the branch without the compare, and
  a moved instruction between could clobber `a`/`b`'s registers — both
  decline. The MIR proof replaced a textual whole-function read census
  (first implementation): the census was sound but fired zero times because
  the allocator reuses the compare's physical register for later values
  before re-reading it — reads of OTHER values blocked every fusion. The
  MIR def-use count is exact and unaffected by register reuse. Spilled
  conditions decline automatically (an sspill/sreload of the cond adds a
  use / changes the defining op).
- **Transform**: the compare line becomes a trace comment; the branch
  becomes `blt a, b, L` / `bltu a, b, L` (target unchanged — rule 1 then
  retargets a bare stub if present).
- **Profitability**: one scalar-arith instruction removed per dynamic
  execution; no pressure effect (a value dies at the branch either way).
- **Refusal** (counted as `cmp_declined`): use-count != 1, non-adjacent
  pair, textual-verification failure. Measured declines: 0 on every census
  case.
- **Analysis deps**: the emitter computes the module-wide use-count map at
  construction; the rewrite happens post-allocation on the final stream and
  invalidates nothing upstream.
- **Placement**: emission — the fusion decision needs the post-allocation
  physical form (the emitted pair) plus the MIR def-use facts the emitter
  already holds; a MIR-level fused-branch op would be a repertoire/contract
  change disproportionate to the rewrite.

Both rules default ON; `A100C_BRANCH_FUSE=off` (CompileOptions.branch_fuse
→ identity_part "no-branch-fuse" → emit_assembly) is the rollback and the
paired-measurement control.

## Validation and measurements

Commands and raw evidence under `evidence/` in this directory
(base-/off-/on-metrics, census, multiworker, full-input). All compilations
through the normal factory path; all comparisons under each case's own
policy.

- **Unit + round tests**: `a100c/tests/test_branch_fuse.py` all PASS
  (positive forms, the four refusal classes — stub-with-moves,
  out-of-range, multi-referenced label, instruction-between-pair — the off
  control, execution match at 1 and 4 workers on both builds).
- **Existing suites**: test_emit (one form-assertion adapted to the
  branch-form-agnostic check: the condition-read-before-edge-moves invariant
  now locates the first conditional-to-stub regardless of mnemonic),
  test_control_flow, test_lower_scalar, test_guarded_narrow_access,
  test_backend_vector_state, test_local_materialization,
  test_k3_lowering_optimizations, test_chunk_geometry_boundary,
  test_elementwise_width, test_driver_cache, test_e2e_slice,
  test_runtime_smoke, test_lowering_option_identity — all PASS.
- **Witnesses**: no-name-dispatch positive 0 / witness caught (exit 1);
  numeric-policy witness caught; masked-tails real artifact PASS with the
  guard intact and the degraded build corrupting the guard as required.
  **stage-barriers witness FAILS — pre-existing**: the degraded (barrier
  removed) build produced correct results across all repeats; the same
  failure occurs with `A100C_BRANCH_FUSE=off` (whose emission is
  byte-identical to the baseline), so it is independent of this round —
  recorded for the correctness stream (the advisory check's own sensitivity;
  see also the two pre-existing declared-test failures below).
- **Off-control**: the off build's instruction stream is byte-identical
  (modulo header comments: revision/options) to a pre-edit same-identity
  compile; paired metrics' off side reproduces the baseline totals within
  steady-state noise.
- **Multi-worker**: 84/84 PASS at threads 2/4/8 over
  attention_forward_triton, flash_decode, vdot_kernel_complex (the
  stage-barrier specimen) and frobenius_norm_persistent_two_phase.
- **Paired metrics** (per-call guest dynamic instructions, same tree,
  off vs on; re-collected at the FINAL revision — `evidence/final-off-metrics/`
  and `evidence/final-on-metrics/`; the first collection at the pre-fix
  revision is kept beside them and agrees within the noise envelope):

  | case | off | on | on-vs-off | branch cat |
  |---|---:|---:|---:|---:|
  | attention [4,4,32,64] f16 | 15,830,620 | 15,242,311 | **-3.72%** | -29.2% |
  | flash_decode [2,2,32,32] bf16 | 109,525 | 106,587 | **-2.68%** | -9.1% |
  | linear-dropout [16,128,128] f16 | 6,752,616 | 6,610,023 | **-2.11%** | -29.5% |
  | matmul16 [16,16,16] f16 | 22,895 | 22,339 | **-2.43%** | -3.4% |
  | softmax-inner [97] f16 | 8,321 | 8,401 | +0.96% (noise) | -0.7% |
  | softmax_log [4,97] f32 | 121,241 | 119,083 | **-1.78%** | -7.2% |
  | softmax [20,17] f16 | 75,727 | 73,076 | **-3.50%** | -10.6% |
  | synthesis [1,4,16,64] f32 | 212,873 | 203,396 | **-4.45%** | -17.2% |

  Seven of eight improve (-1.78%..-4.45%); softmax-inner's total moved
  -0.19% then +0.96% across the two collections while its off side itself
  moved 8,349→8,321 — the smallest case's steady-state difference carries
  a ±~1% run-to-run envelope that exceeds the effect size there, while the
  structural branch-category delta is consistently negative and its census
  form is 8/8 blt with 7 stubs removed. Recorded as within noise, not as a
  regression or a win. Judge quantity is the calibrated per-call guest
  dynamic instruction count; no wall-clock or board claim.
- **Census (accept/decline)**: `tools/profiling/branch_census.py` over the
  paired set: 25-39 stubs removed per case (every bare stub; exactly the
  one argument-carrying stub declines per case), 8-35 compare+branch
  fusions, 0 compare declines; post-transform conditional forms are
  dominated by blt/bltu (e.g. flash_decode: 26 blt, 0 residual bne).
- **Full-input regression (final revision)**: run `branchfuse-full` over
  all 2,734 cases with the rules enabled — **2,728 PASS / 6 TIMEOUT, the
  six being exactly the pre-existing class** (complex_svd [17] ×3 dtypes +
  deconv3d [1,4,8,8,8] ×3 dtypes, the case budget sitting at their compile
  time since before this round) — **zero new non-PASS**. Evidence:
  `evidence/full-input/shard0..7/` + `evidence/full-input/marginal/`
  (the marginal operators run serially; the chunk_gdn2 [17] cases that the
  pre-fix peephole's compile-time cost had pushed over the budget PASS at
  the final revision — see the compile-time note below). The first full
  run at the pre-fix revision (2,726/8) is preserved under
  `evidence/full-input/prefix-revision/` as the incident record.
- **Corpus-wide aggregation (generality, final revision)**: summed over
  every artifact the scan freshly compiled (2,118 with emission stats):
  **40,216 bare stubs removed (2,111 declined — ~1 per artifact, the
  argument-carrying brc), 31,634 compare+branch fusions, 0 compare
  declines; 2,110/2,118 artifacts (99%) fire at least once** (the 8
  zero-fire artifacts are branch-free kernels). The pattern is structural
  across the corpus, not a per-family special case.
- **Pre-existing failures recorded (not this round's, proven by worktree
  runs at 57f3c37 and 639ab22)**: (1) `test_passes_basic` fails its
  vdot_kernel_complex all-off-vs-plain byte-identity check (the test-local
  PassesCompiler harness no longer mirrors the driver's full pipeline for
  this case; the op-index shift signature suggests a driver-side stage the
  harness lacks — grid flattening is the prime suspect); (2)
  `architecture-check --run` fails on declared tests that were removed by
  earlier rounds (test_evidence_files / test_repeated_calls /
  test_final_regression) and declared symbol names that never matched the
  current mir.py/allocate.py naming; no ARCHITECTURE_VERIFICATION.json
  record exists. Both predate this round and need their own follow-up in
  the correctness stream.

- **Compile-time impact (measured, then repaired in-round)**: the first
  implementation's stub-referent check rescanned the whole stream per
  branch — O(branches × lines). On the corpus's biggest function
  (chunk_gdn2_inter_solve_fused [17], ~480 qualifying branches over ~40k
  emitted lines) that added ~25s to a ~165s compile and pushed the two
  budget-marginal chunk_gdn2 [17] cases over the scan's per-case budget
  (TIMEOUTs in the first full-input run — NOT in the known pre-existing
  six). Root-caused by timing the same case at HEAD (164.5s), at the
  candidate (190.0s) and after the fix (162.9s); the fix is a single-pass
  stub-label reference census (identical fired/declined counters,
  identical emitted code, chunk_gdn2 back under budget with HEAD-level
  headroom). Lesson recorded: a peephole's own asymptotics are part of its
  correctness envelope on this corpus — the case budget sits AT the
  heaviest cases' compile time, so an O(n²) stream pass is a
  full-input regression even when every emitted instruction is right.
  The full-input regression and paired metrics below were RE-RUN at the
  final (post-fix) revision.

## Good and bad practices (this round's lessons)

- **A textual read census is the wrong proof for values whose physical
  register is recycled** (observed): the allocator's reuse makes
  "no textual reads" almost never true even for single-use values. The
  exact def-use facts live one layer down (MIR operands + edge args) and
  the emitter already holds them — surface-level proofs should be replaced
  by representation-level facts when the representation is at hand.
- **Counters as the first smoke test** (observed): the all-declined
  counters exposed the `\b`-before-dot regex bug in seconds; an
  accept/decline counter is cheaper than any miscompile hunt.
- **Form-agnostic test assertions** (observed): test_emit's
  `text.index("bne ")` broke on a legitimate emission change; assertions
  should pin invariants (condition read before edge moves), not one
  mnemonic.
- **Scoped harness drift** (observed, bad): test-local pipeline mirrors
  (PassesCompiler) rot as the real driver gains stages; the declared
  all-off byte-identity check then fails for harness reasons, masking
  whether the compiler's general path is intact.

## Migration recipe

Needs, mapped to interfaces: (1) a branch emission that routes empty-move
edges through a trampoline (any emitter with per-edge moves after the
branch); (2) exact def-use over operands AND edge-argument lists, at the
point of emission; (3) the emitted-stream index of each instruction for
textual re-verification; (4) a conservative conditional-branch range bound
(4 bytes/instruction-line); (5) counters + trace comments for accept and
decline observability; (6) a behavior switch in the artifact identity.
Portable parts: both rule functions are stream-index based and
target-generic (RISC-V CB-range guard is the only target constant);
the use-count map is any SSA-ish def-use over operands and edge args.

## Replay

```bash
set -a; . ./.env; set +a
# the paired contrast (same tree)
A100C_BRANCH_FUSE=off python3 -B tools/profiling/collect_metrics.py \
  --operator suite/perf/attention_forward_triton.py --shape 4,4,32,64 \
  --dtype float16 --threads 1 --out <off-dir>
python3 -B tools/profiling/collect_metrics.py \
  --operator suite/perf/attention_forward_triton.py --shape 4,4,32,64 \
  --dtype float16 --threads 1 --out <on-dir>
# the accept/decline census
python3 -B tools/profiling/branch_census.py \
  --operator suite/perf/matmul.py --shape 16,16,16 --dtype float16
# the round's tests
python3 -B a100c/tests/test_branch_fuse.py
# the compile-time control on the heaviest identity (the budget-marginal class)
time python3 -c "import importlib.util; from a100c.factory import make_compiler; \
  spec = importlib.util.spec_from_file_location('op', \
  'ops/suite/dev/chunk_gdn2_fwd_kernel_inter_solve_fused.py'); \
  m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); \
  make_compiler().compile_case(m.make_case(shape=(17,), dtype='bfloat16', seed=30))"
# the full-input regression (sharded form; the budget-marginal operators serial)
python3 -B tools/run_scan.py run --operator <op-subset> \
  --report <dir>/report.json --run-id branchfuse-full --journal <dir>/journal.jsonl
```

Baseline root: 57f3c37. Candidate root: this round's tree. The skill used:
`develop-optimization-pass` (loaded via the Skill tool in the working
session; raw subagent dispatch is engine-gated in this project — the
hook's response is recorded in the session log — so the round ran in the
direct human-guided session mode the optimization skill documents).
