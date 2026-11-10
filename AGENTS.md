# Compiler project instructions

This project builds the compiler described by `chip.md` for the read-only input
corpus `ops/`. The workflow is supplied by the zcode plugin; use `/workflow` for
status and `/workflow-run` when the user starts the experiment. Read `KICKOFF.md`
first. This project starts uninitialized: only after the user starts the run,
call `workflow_init` with `chip.md` and `ops` if
`docs/compiler-agent/PROJECT_STATE.json` does not exist. Otherwise resume that
state without reinitializing. Define tasks from the current workflow guidance;
no task is pre-created. Do not dispatch workers before the user starts the run.
For initial environment/chip/workload analysis, use the registered `planning`
capability with `phase-environment-analysis`, `phase-chip-analysis` or
`phase-workload-analysis` tags respectively. The tag selects the analysis skill;
`analysis` is not a registered task capability in this installed workflow.

## Scope and state

- Acceptance is `correctness_only`: no performance targets, timings, benchmarks,
  speedups or measured performance round. This does not remove basic compiler
  optimizations: implement and enable CSE, DCE, constant folding/propagation,
  copy propagation, strength reduction and LICM under their legality conditions.
  Plan them as ordinary `coding`, purpose `input` work before full validation;
  reserve capability/purpose/tag `optimization` and G9 for measured performance
  work. Validate actual rewrites and unchanged results without a speedup target.
  Current full executed-and-compared regression
  and required resource evidence determine completion. Never assert a G9 pass.
- Preserve every input operator, shape/dtype case and original comparison policy.
  Do not edit kernels, references, tolerances or the corpus harness to obtain a pass.
- Integer, index and boolean results are exact; floating results obey each case's
  declared comparison. No operator-name dispatch, precomputed answers or reference fallback.
- Durable state and evidence live in `docs/compiler-agent/`; task delivery and
  environment/reference probes are not candidate compiler correctness.

## Design and implementation

- Derive architecture, stages, representations and interfaces from the two inputs
  and sourced Facts. `ARCHITECTURE_CONSTRAINTS.json`, once reviewed, is the design
  contract; semantic changes require a DesignIssue, replanning and fresh review.
  Planning declares the design and executable dependencies without implementing it.
- Keep compiler responsibilities explicit: lowering, instruction selection,
  allocation, emission, driver and native runtime have clear producer/consumer
  boundaries. Implement the required stages and test actual integrations; there
  is no prescribed number of IRs, modules, tasks or lines.
- Generate a complete single-operator native executable from program-level
  assembly and common native services. Python may compile, prepare and compare
  outside that program; runtime dispatch, range loops, stages and synchronization
  must not start, embed or call Python. Cache complete programs by every bound
  source, target, option, grid/launch and argument-layout dependency.
- Support correct 1/2/4/8-worker execution, useful multi-worker work, RVV tails and
  applicable real IME execution. Preserve operand constraints, ownership, stage
  visibility and merge semantics. Bind representative dynamic observations to
  the same prepared run, case and artifact; a listing or idle pool is insufficient.
- Search the local knowledge pack with `workflow_target_search` and read sources
  with `workflow_target_source`. Use `docs/compiler-agent/TARGET_SUMMARY.md` and sourced Facts; do not
  invent core IDs or treat QEMU as a board timing/topology model. The fixed QEMU
  BF16 IME format-control gap remains unverified; an FP16 run cannot prove BF16.
  Use current state, `a100_support/lock.json` and current execution reports for readiness.

## Execution and evidence

- `.env` declares the installed tools and workflow home. `a100_support/` supplies native
  transport, QEMU execution and compiled x86 Triton CPU question-validation adapters.
  The x86 reference never substitutes for executing generated target code.
  Integrate the compiler with `a100_support/native_device.py`; set
  `A100_COMPILER_FACTORY=module:factory` in `.env` once it is implemented.
- Use workflow tools for state and delegation. Shell fallback commands must
  load the declared PYTHONPATH from `.env` before invoking
  `python3 -m compiler_agent --root .`. Prefer MCP report tools for worker reports.
- A compiler fix needs an independent executed comparison. Keep full input
  coverage and useful regression tests, including repeated calls and synchronization;
  generated/built-only results and skipped cases do not pass.
- The manager delegates tasks by capability and records independent review.
  Every worker follows its bounded TaskInput and files its own report. Preserve
  completed work and record real failures; missing records require verification.
- The controller owns the private challenge broker. Question execution uses the
  existing container boundary; same-host user permissions are not hidden-data
  isolation. Do not mount private storage or the Docker socket into question workers.

The prepared adapters live only in `a100_support/`. The compiler may create its
own `tools/` directory; do not import prepared adapters through that namespace.

<!-- BEGIN ARCHITECTURE_CONSTRAINTS (generated; do not edit here) -->

# Compiler project agent contract

This block is generated from `ARCHITECTURE_CONSTRAINTS.json`.
Do not replace structural checks with prose claims; edit the JSON and
re-render, never this block.

## Responsibility layout

- `a100c/__init__.py` — package root: pipeline entry points and compiler revision identity
- `a100c/target.py` — target model as data: RVV 1.0 VLEN=1024/ELEN=64 parameters, IME tile families with operand constraints (LMUL=1, MUL_C, parity, overlap, format), scalar repertoire, lp64d ABI facts - derived from recorded facts only
- `a100c/frontend/source.py` — operator module and case-layer loading; single-@triton.jit and source-contract invariants; refusal with source locations
- `a100c/frontend/surface.py` — declared 107-construct/280-parameter surface as data; per-parameter classification implemented / ignorable-with-reason / refused
- `a100c/frontend/specialize.py` — case binding; meta-tier specialization identity (pointer dtypes, scalar classes honoring do_not_specialize, constexprs incl. deterministic autotune config); constexpr folding; dead-branch elimination
- `a100c/frontend/types.py` — source type rules: literal typing, promotion/unification, result types, value conversion distinct from bitcast, zero-dim values
- `a100c/frontend/shapes.py` — rank/extent inference with broadcast extents distinguished from real extents; declared alignment rules; disagreement is a diagnostic
- `a100c/frontend/gridmodel.py` — case-layer grid extraction with provenance over bundle-visible quantities (scalar args, view extents, constexprs); runtime grid-evaluation plan; compile-time equality self-check; refusal outside the extractable domain
- `a100c/frontend/lower_tir.py` — AST-to-TIR lowering for the declared surface
- `a100c/ir/tir.py` — TIR representation (typed block-tensor dataflow, structured control flow with explicit joins, masks with declared defaults) and its structural verifier
- `a100c/ir/mir.py` — MIR representation (CFG with block parameters, virtual registers, vsetvli regions, masked memory ops, IME tile ops with operand contract, worker partition and stage structure) and its verifier incl. IME legality
- `a100c/ir/dump.py` — per-stage textual dumps with source attribution; per-pass trace counters; determinism of dumps
- `a100c/passes/pipeline.py` — pass pipeline registration, ordering, per-pass switches; the basic optimizations run in the normal pipeline
- `a100c/passes/analyses.py` — shared analysis owner: dominance, liveness, loop structure, memory effects, with a declared invalidation contract
- `a100c/passes/cse.py` — common subexpression elimination under availability and effect/alias proofs
- `a100c/passes/dce.py` — dead code elimination preserving observable stores, atomics, synchronization and stage effects
- `a100c/passes/constprop.py` — constant folding and propagation under source width, signedness, overflow, rounding and path conditions
- `a100c/passes/copyprop.py` — copy propagation under dominance, control-flow joins, value identity and pointer semantics
- `a100c/passes/strength_reduction.py` — strength reduction with equivalent integer/index behavior and the declared floating policy
- `a100c/passes/licm.py` — loop-invariant code motion under invariance, effects, aliasing, masks and zero-trip safety
- `a100c/plan/partition.py` — work partition for 1/2/4/8 workers: strided program-instance ranges (default), contiguous output-tile chunks when repartitioning is legal, tails and coverage
- `a100c/plan/stages.py` — stage/synchronization/merge planning for cross-worker dependencies; workspace ownership, visibility and lifetime
- `a100c/plan/tiles.py` — dot tiling to IME tiles (8x16x8 INT8, 8x8x8 FP16), packing decisions, zero-padded staging for tails, vector-file-budget-bounded chunking with an ordinary path retained
- `a100c/lower/vectorize.py` — RVV vectorization: vsetvli regions, exact vl, masked tails, wide-access selection from proven contiguity/alignment
- `a100c/lower/matrix.py` — IME matrix lowering: tile mapping (vs1 row-major A, vs2 column-major B), accumulation typing, register grouping constraints, MCPM-controlled format, BF16 gap handling via the vector FP32 path
- `a100c/lower/scalar.py` — scalar/int64/bool lowering with declared wrap semantics, atomics with mask and signedness, debug_barrier ordering, control flow to MIR branches
- `a100c/lower/addresses.py` — whole-tree i64 address materialization with broadcast extents applied before accumulation; independent index-computation check
- `a100c/backend/repertoire.py` — declared instruction repertoire as data (RVV, IME smt.* with constraints and recorded absences, scalar RV64); adding an operation is a table edit
- `a100c/backend/legalize.py` — legalisation: expressible-but-illegal MIR forms rewritten to legal sequences; guarantees post-state is inside the declared repertoire
- `a100c/backend/select.py` — one generic constraint-checked matcher over the repertoire table; no entry means a located refusal
- `a100c/backend/allocate.py` — GPR and vector-register allocation from real liveness over the real CFG; 32x128B vector budget; IME group parity; compiler-owned spill/split with stack slots
- `a100c/backend/emit.py` — mechanical program-level assembly emission (entry, bundle binding, native grid evaluation, worker range loops, stages, constants, workspace); traceable to selected MIR ops
- `a100c/driver.py` — pipeline orchestration and the artifact cache keyed by every bound dependency (specialization identity, compiler revision, target model, options, argument-layout version)
- `a100c/factory.py` — A100_COMPILER_FACTORY entry: compile_case(case) -> ExecutableArtifact per the a100_support/native_device.py protocol
- `a100c/runtime/` — precompiled native C runtime: process main (--bundle/--threads/--repeats), persistent pthread pool (1/2/4/8), stage barriers and C11 atomics, workspace allocation, a100-native-io/v1 bundle reader with relocation patch/restore and input snapshot/restore for repeats; built by the declared cross toolchain only
- `a100c/runtime/build.py` — native build orchestration: cross as/ld, runtime compilation and linking into the standalone ELF64 RISC-V executable
- `tools/run_scan.py` — compile/run/full-scan driver: corpus enumeration via the corpus harness, compile-once-per-identity scheduling, staging/execution/comparison via the native device protocol, input-regression/v1 manifest builder and report writer
- `tools/check_no_name_dispatch.py` — generality check: nothing below the frontend branches on operator/kernel/benchmark names; --witness injects a name branch into a scratch copy and must be caught (witness exits nonzero)
- `tools/check_numeric_policy.py` — comparison-policy check: tolerances and references are read from the case; --witness widens a tolerance in a scratch copy and must fail
- `tools/check_masked_tails.py` — ragged-tail check: tail lanes address a poisoned guard region and must not touch it; --witness removes the tail predicate in a scratch build and must fail
- `tools/check_stage_barriers.py` — synchronization check: a two-phase multi-worker case is correct with the declared barrier; --witness removes the barrier in a scratch build and must fail
- `a100c/tests/` — declared test tree: standalone runnable unittest modules (one per stage/IR/check), bootstrapping sys.path via a100c/tests/_bootstrap.py

## IR layers (2–3 persistent representations)

1. **TIR** (`tir/v1`): `a100c/ir/tir.py`; properties: typed block-tensor dataflow; element width and signedness carried as separate type components, value conversion and bit-level reinterpretation are distinct operations and never fold into each other, mask semantics with a per-operation declared disabled-position default (load other / store none / atomic none), shapes with per-axis extents and broadcast extents distinguished from real extents, reductions carry operation, axes, keep_dims, per-op-and-dtype identity and index tie-break, dot carries operand dtypes, accumulation type, out_dtype and the ieee/tolerance numeric class, index arithmetic typed with declared wrap semantics; addresses formed in i64, launch geometry (grid extents) remains runtime-symbolic, structured control flow with explicit join parameters for loop-carried values, RNG ops (philox family) are bit-exact semantic operations; passes: cse, dce, const-fold-propagate, copy-propagate, strength-reduction, licm; tests: `a100c/tests/test_tir_verifier.py`
2. **MIR** (`mir/v1`): `a100c/ir/mir.py`; properties: virtual-register dataflow over RVV/IME/scalar operations with an explicit CFG (blocks, branches, block parameters as joins), vsetvli regions carrying SEW/LMUL/vl and tail policy; region consistency is a verifier invariant, masked vector memory operations with inactive-position semantics (no access, declared default), IME tile operations carrying the sourced operand contract: LMUL=1, vs1 row-major A, vs2 column-major B, vd even-numbered when MUL_C=2, no destination/source overlap, family operand format, worker partition structure: per-worker entry, range loops, stage barriers, merge operations, workspace addresses with ownership, address materialization in i64 as whole trees, spill slots in the frame, restored before use, storage not reused while live; passes: ; tests: `a100c/tests/test_mir_verifier.py`

Further transformations belong to lowering or pass stages; do not add a fourth persistent IR layer.

## Pipeline verification

- **frontend`**: `a100c/frontend/lower_tir.py`; source → tir/v1; tests: `a100c/tests/test_frontend_surface.py`, `a100c/tests/test_specialize.py`, `a100c/tests/test_frontend_types.py`, `a100c/tests/test_frontend_shapes.py`, `a100c/tests/test_grid_model.py`, `a100c/tests/test_tir_verifier.py`
- **tir-optimize`**: `a100c/passes/pipeline.py`; tir/v1 → tir/v1; tests: `a100c/tests/test_passes_basic.py`
- **planning`**: `a100c/plan/partition.py`; tir/v1 → tir/v1; tests: `a100c/tests/test_partition.py`, `a100c/tests/test_stage_plan.py`
- **lowering`**: `a100c/lower/vectorize.py`; tir/v1 → mir/v1; tests: `a100c/tests/test_lower_vector.py`, `a100c/tests/test_lower_scalar.py`, `a100c/tests/test_lower_matrix.py`, `a100c/tests/test_control_flow.py`, `a100c/tests/test_reductions.py`, `a100c/tests/test_memory_forms.py`, `a100c/tests/test_atomics.py`, `a100c/tests/test_layout_ops.py`, `a100c/tests/test_conversions.py`, `a100c/tests/test_math_ops.py`, `a100c/tests/test_rng.py`, `a100c/tests/test_matrix_breadth.py`
- **legalisation`**: `a100c/backend/legalize.py`; mir/v1 → mir/v1; tests: `a100c/tests/test_legalize.py`
- **selection`**: `a100c/backend/select.py`; mir/v1 → mir/v1; tests: `a100c/tests/test_select.py`
- **allocation`**: `a100c/backend/allocate.py`; mir/v1 → mir/v1; tests: `a100c/tests/test_allocate.py`
- **emission`**: `a100c/backend/emit.py`; mir/v1 → artifact; tests: `a100c/tests/test_emit.py`
- **native-build`**: `a100c/runtime/build.py`; artifact → artifact; tests: `a100c/tests/test_build.py`, `a100c/tests/test_runtime_smoke.py`
- **scan-validation`**: `tools/run_scan.py`; source → artifact; tests: `a100c/tests/test_e2e_slice.py`, `a100c/tests/test_driver_cache.py`, `a100c/tests/test_compile_sweep.py`, `a100c/tests/test_scan_report.py`, `a100c/tests/test_ime_evidence.py`, `a100c/tests/test_evidence_files.py`, `a100c/tests/test_repeated_calls.py`, `a100c/tests/test_final_regression.py`

## Behaviour properties (run them; a property without a witness is recorded as vacuous)

- **no-operator-name-dispatch** (required) — `python3 tools/check_no_name_dispatch.py`; module: `a100c`; witness (must fail): `python3 tools/check_no_name_dispatch.py --witness`
- **numeric-policy-reads-the-case** (advisory) — `python3 tools/check_numeric_policy.py`; module: `tools`; witness (must fail): `python3 tools/check_numeric_policy.py --witness`
- **masked-tail-no-out-of-range-access** (advisory) — `python3 tools/check_masked_tails.py`; module: `a100c/lower/vectorize.py`; witness (must fail): `python3 tools/check_masked_tails.py --witness`
- **stage-barrier-required-for-cross-worker-visibility** (advisory) — `python3 tools/check_stage_barriers.py`; module: `a100c/plan/stages.py`; witness (must fail): `python3 tools/check_stage_barriers.py --witness`

## Declared validation checks

- **frontend-surface-enumeration**: `a100c/tests/test_frontend_surface.py`
- **specialization-identity**: `a100c/tests/test_specialize.py`
- **tir-verifier-rejects-malformed**: `a100c/tests/test_tir_verifier.py`
- **basic-passes-legality-and-results**: `a100c/tests/test_passes_basic.py`
- **partition-covers-1-2-4-8-workers**: `a100c/tests/test_partition.py`
- **grid-model-runtime-evaluation**: `a100c/tests/test_grid_model.py`
- **rvv-masked-tails**: `a100c/tests/test_lower_vector.py`
- **ime-operand-constraints**: `a100c/tests/test_lower_matrix.py`
- **ime-executed-instruction-evidence**: `a100c/tests/test_ime_evidence.py`
- **reduction-and-merge-semantics**: `a100c/tests/test_reductions.py`
- **atomics-and-memory-forms**: `a100c/tests/test_atomics.py`
- **conversion-matrix**: `a100c/tests/test_conversions.py`
- **rng-bit-exact**: `a100c/tests/test_rng.py`
- **allocation-completeness**: `a100c/tests/test_allocate.py`
- **mir-verifier-rejects-illegal-ime**: `a100c/tests/test_mir_verifier.py`
- **runtime-transport-and-pool**: `a100c/tests/test_runtime_smoke.py`
- **artifact-cache-identity**: `a100c/tests/test_driver_cache.py`
- **end-to-end-slice-comparison**: `a100c/tests/test_e2e_slice.py`
- **full-compile-sweep**: `a100c/tests/test_compile_sweep.py`
- **full-scan-report**: `a100c/tests/test_scan_report.py`
- **parallel-and-resource-evidence**: `a100c/tests/test_evidence_files.py`
- **repeated-call-synchronization**: `a100c/tests/test_repeated_calls.py`
- **final-regression-recorded**: `a100c/tests/test_final_regression.py`
- **no-operator-name-dispatch**: `tools/check_no_name_dispatch.py`

## CFG and register allocation

- CFG: `a100c/ir/mir.py`; tests: `a100c/tests/test_mir_verifier.py`
- register allocation: MIR `a100c/ir/mir.py`, allocator `a100c/backend/allocate.py`; tests: `a100c/tests/test_allocate.py`

## Declared optimization passes

- **cse**
  - module: a100c/passes/cse.py
  - ir: tir/v1
  - stage: tir-optimize
  - optional: False
  - switch: A100C_PASS_CSE=off
  - trace_counter: pass.cse.rewrites
  - profitability: always profitable when legality holds; memory reuse requires an effect/alias proof
  - tests: ['a100c/tests/test_passes_basic.py']
- **dce**
  - module: a100c/passes/dce.py
  - ir: tir/v1
  - stage: tir-optimize
  - optional: False
  - switch: A100C_PASS_DCE=off
  - trace_counter: pass.dce.removed
  - profitability: always profitable when legality holds; observable stores, atomics, synchronization and stage effects are preserved
  - tests: ['a100c/tests/test_passes_basic.py']
- **const-fold-propagate**
  - module: a100c/passes/constprop.py
  - ir: tir/v1
  - stage: tir-optimize
  - optional: False
  - switch: A100C_PASS_CONSTPROP=off
  - trace_counter: pass.constprop.folds
  - profitability: always profitable when legality holds; source width, signedness, overflow, rounding and path conditions survive
  - tests: ['a100c/tests/test_passes_basic.py']
- **copy-propagate**
  - module: a100c/passes/copyprop.py
  - ir: tir/v1
  - stage: tir-optimize
  - optional: False
  - switch: A100C_PASS_COPYPROP=off
  - trace_counter: pass.copyprop.rewrites
  - profitability: always profitable when legality holds; dominance, joins, value identity and pointer semantics survive
  - tests: ['a100c/tests/test_passes_basic.py']
- **strength-reduction**
  - module: a100c/passes/strength_reduction.py
  - ir: tir/v1
  - stage: tir-optimize
  - optional: False
  - switch: A100C_PASS_STRENGTH=off
  - trace_counter: pass.strength.rewrites
  - profitability: applies to affine index/address expressions (division/remainder by constants, repeated index work) with equivalent integer/index behavior and the declared floating policy
  - tests: ['a100c/tests/test_passes_basic.py']
- **licm**
  - module: a100c/passes/licm.py
  - ir: tir/v1
  - stage: tir-optimize
  - optional: False
  - switch: A100C_PASS_LICM=off
  - trace_counter: pass.licm.hoisted
  - profitability: hoists invariant pure expressions only; masked or trapping accesses are never hoisted; zero-trip loop safety preserved
  - tests: ['a100c/tests/test_passes_basic.py']

## Declared verification

- Run it with `architecture-check --run` (test command: `python3 {test}`); the record (`ARCHITECTURE_VERIFICATION.json`) supports optional architecture diagnostics; each declared test's digest is bound to it.
- A `behaviour` entry marked `advisory` is maturity, not a defect: it is recorded and offered to the optimization phase. `required` entries must hold.
- A property without a `witness` (a command that must fail) cannot be shown able to fail, and is recorded as vacuous.

## Input-scoped implementation

- Preserve the input semantics and independently compared execution.
- Change semantic contracts through review; metadata does not reopen implementation.
- Current full input regression determines correctness completion.

<!-- END ARCHITECTURE_CONSTRAINTS -->
