# K3 A100 assembly optimization: authorized implementation scope

The user authorized implementation on 2026-11-11 after a five-hour read-only
exploration, focused on matrix multiplication/IME, attention, elementwise and
softmax. The other editing session has ended. The available execution endpoint
is QEMU; the user explicitly selected generated assembly and dynamic guest
instruction counts as the optimization evidence. No hardware latency, throughput
or speedup will be inferred from those counts.

This is a human-guided batch with independent worker reports. It does not change
the engine's `correctness_only` acceptance policy, initialize/reopen the workflow,
complete stale tasks or assert G9. The current baseline does **not** satisfy a
full-input PASS precondition: its historical full report has 2732 PASS and two
deconv3d compilation/staging timeouts. Those failures remain in scope.

## Baseline and rollback boundary

- Compiler source baseline: Git `c8ade47ad9a537c3fce84eb8daf5de6799d907a7`, reported
  compiler digest `fc3ccea383db5f55`. The old revision-file list omits some code
  dependencies, so the digest alone is insufficient provenance.
- Frozen source: `/tmp/a100-k3-baseline-review-gcdf_716`. Exact copied-file hashes,
  profiling adapter/plugin identity and immutable input linkage are recorded in
  `validation/BASELINE_SNAPSHOT.json`. No shared cache/build tree was copied.
- `validation/BASELINE_CORRECTNESS_AUDIT.json` independently parses all 2734
  historical rows, verifies unique IDs/no omissions and retains both timeout rows.
- Preserve the inherited runtime build executable, hook log, board packages and
  unrelated untracked work. Commit only reviewed source/text and new evidence.

## Target contract and boundaries

Use the current reviewed TIR/MIR architecture, RV64/lp64d, RVV 1.0 VLEN=1024,
ELEN=64, and recorded IME operand constraints. Applicable IME instructions require
their own legal register groups, alignment/parity, accumulator, no-overlap and
format rules. BF16 IME remains unverified under the pinned QEMU format-control
gap; ordinary FP32 vector lowering remains its fallback. Worker counts are
1/2/4/8, at most eight compute workers per operator program. QEMU does not prove
silicon CPU IDs, topology, timing or native instruction compatibility.

Keep every original input operator/case, its reference and comparison policy.
Integer/index/boolean outputs are exact. No operator-name dispatch or oracle
fallback is allowed. New fast paths match structural IR properties and decline
when their legality requirements cannot be proved.

## Bounded delegated work

1. **Lowering owner (`lowering_opt`)**: adapt kept-axis reductions, neutral
   reduction-domain trimming and ordinary matrix row reuse to the current
   lowering. Carry each switch through LowerOptions, CompileOptions and the
   actual factory entry point. Preserve arithmetic order/rounding and a general
   path. Repair the chunk geometry ownership bug discovered during exploration
   before composing incompatible segment widths. Add meaningful positive and
   rejection/native result checks.
2. **Backend owner (`backend_opt`)**: inspect the current backend and adapt the
   bounded backend/cache work selected by the manager. Complete compiler/runtime
   dependency identity is a prerequisite for trustworthy on/off comparisons.
   Preserve legal RVV/IME state and source constraints; do not introduce a new
   persistent IR or unreviewed MIR optimization stage.
3. **Independent validation/review owner (`baseline_review`)**: freeze current
   baseline, preserve/recheck the inherited T044 regression test, collect paired
   assembly counts through the original comparator, inspect candidate guards and
   factory integration, and execute/merge the unchanged full runner once the
   manager confirms the final frozen candidate.

Workers own disjoint write surfaces and do not submit another worker's report.
Independent review findings return to the implementation owner for correction.

## Compatible completion increment within the same user scope

The first increment improves three structural cost classes, but its independent
profiles leave FP16 IME and large GELU unchanged. For example matmul128 FP16
remains 7,438,232 program instructions/call, and backend-only GELU262144 FP32
remains 1,990,955. Their raw zero-gain evidence is retained; it cannot be relabeled
as a win or replaced by the earlier exploration's results.

The original user request includes both IME and elementwise, so the manager
authorized two compatible mechanisms already justified in the read-only
exploration: guarded narrow memory access and pressure-aware elementwise SIMD
width. This completes the same five-category implementation scope; it does not
start another optimization round or change engine acceptance policy.

- The backend owner implements guarded narrow load/store support with its own
  helper and bounded integration seam. Eligibility must preserve actual i64 byte
  addresses, active masks, memory element width/EMUL, `other` dtype, volatile
  behavior and a correct original access path when a proof/guard fails.
- The lowering owner implements pressure-aware elementwise width selection.
  Wider candidates must respect real scalar/vector/mask liveness, EEW/EMUL and
  register-group constraints. Scalarized accesses, unsupported cross-lane work,
  side effects or excessive pressure retain the narrower path. Bigger LMUL is
  not an unconditional profitability rule.
- Keep the first increment as a committed rollback boundary. Retain its 14-case
  profile comparison separately. The final composed candidate receives a fresh
  14-case comparison against the **same current baseline**, plus final guard/state
  review and one stable complete-original-input execution campaign.

## Reuse and applicability

The prior exploration's report and catalog are at
`/tmp/a100-readonly-review-b-te2m9tiu/exploration/READ_ONLY_OPTIMIZATION_REPORT.txt`
and `EXPERIMENT_CATALOG.json`. Its mature `profile_pristine_v1.py` adapter is reused
with a current-root parameter and current-source provenance. It annotates MIR
identities in assembly **comments** only, verifies reassembled program bytes and
maps real objdump instruction starts, including pseudo expansions. Per-PC repeat
differences are restricted to the stable program image. Shared-library ASLR does
not enter program cost; whole-process category differences are retained separately.

Historical performance numbers are mechanism evidence, not candidate results.
The old C7 broadcast-view/early-flat-alias component failed SVD; a views-off
ablation passed one FP32 case. Therefore no whole prototype factory, view rewrite
or arena package is copied wholesale. This batch requires fresh checks through
the production entry point and isolates candidate algorithms with switches.

## Verification and measurement

- For each measured case, two independent repeated-run pairs must give the same
  program instruction count. Every individual run uses the original case
  comparator and runtime repeat-consistency check, plus ELF/assembly identity.
- Preserve `program_guest_instructions_per_call`, whole-process and outside-
  program counts as different boundaries. Runtime restore/compare work is not an
  operator code-generation win; QEMU wall time is auxiliary only.
- Representative cases are in `validation/PROFILE_CASES.json`; each marks whether
  its shape belongs to the original manifest. Larger supported-generator shapes
  never increase original-corpus coverage.
- After candidate freeze, use the existing runner with four disjoint lists of
  complete operators, each with its own fresh cache/runtime build directory.
  `validation/sharded_regression_v1.py` prepares and audits the partition. This
  runner concurrency is **not** useful multi-worker execution of a single operator.
- Merge only complete raw reports whose union exactly equals the original 2734
  IDs with unchanged metadata and valid PASS stage booleans. Keep all failures and
  resource bindings. Raise the recorded timeout budget for the two existing slow
  cases; an exhausted budget remains a failure, never a skipped PASS.
- Final correctness, instruction reduction and unavailable silicon evidence are
  reported separately. No full correctness claim is made until every original
  case is executed and compared at the candidate identity.
