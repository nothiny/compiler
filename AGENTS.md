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
