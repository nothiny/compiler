# Full-corpus kickoff — A100 correctness experiment

Build a compiler that compiles **every operator** in the `ops/` corpus for the
target described by `chip.md`, executes each complete native operator under the
declared QEMU endpoint, and verifies its outputs against its independent reference.
Then run the compiler-development workflow to completion.

The target is A100 and acceptance is **correctness_only**: no benchmark target,
performance metric or measured performance round is required. Basic compiler
optimizations remain part of implementation and must not be omitted under this
scope.

You are the audit agent (manager of the run). The workflow home is
`/home/i_yinzida/compiler-agent-workflow`; this project is
`/home/i_yinzida/compiler-a100-experiment-001`. Read `AGENTS.md`. After the user
starts the run, initialize with `workflow_init` (`chip=chip.md`, `ops=ops`) only
if `docs/compiler-agent/PROJECT_STATE.json` is absent. Otherwise resume the
existing state. Create tasks from current guidance; none are pre-created.
`/workflow` inspects state. Start work only after `/workflow-run` or an explicit
user instruction to start the experiment.

## How this order is executed: you delegate all of it

**Read this before anything else, because it decides who does the work below.**

You own the run, not one task, and **you execute no task yourself** — not the
analysis phases, not planning, not a coding task, not final
validation. Every phase is delegated: follow `workflow_next`; when it requests
`organize_work`, submit concrete tasks with `workflow_task_submit`.
Initial analysis tasks use capability `planning` and the corresponding
`phase-environment-analysis`, `phase-chip-analysis` or `phase-workload-analysis`
tag so the correct skill is loaded. Use registered capabilities; do not submit
an `analysis` capability, which this installed workflow does not register.
`/task-delegate <id>` dispatches a task to a fresh subagent whose contract the
engine writes to disk.
The architecture review, the debug hand-off and the audit are delegated the
same way (`/review-delegate`, `/debug-delegate`, `/audit-delegate`).

So read the rest of this order as **the requirements the workers must satisfy**,
not as a list of things for you to do.  Where a section below says "read",
"record", "build", "write" or "inspect", the actor is the worker
whose task owns that phase — and your job is to make sure such a task exists,
is delegated, and is reported.  Three consequences:

- **You author no artifact.**  `CHIP_ANALYSIS.md`, `OPERATOR_INVENTORY.md`,
  `COMPILER_ARCHITECTURE.md`, `ARCHITECTURE_CONSTRAINTS.json`,
  `FAILURE_CENSUS.json`, the execution and comparison reports — each is a
  task's declared output. Follow current manager guidance for any audit objective;
  the computed acceptance requirements determine completion.
- **You run no build, test, profile or benchmark command.**  A worker runs it
  inside its task and reports the result; a missing tool is an environment
  fact to record, not a command for you to retry.
- **You read the workflow's own contracts, not the project's material.**
  `docs/ARCHITECTURE.md`, `docs/WORKFLOW.md` and `docs/STATE_MODEL.md` in the
  workflow home are yours.  The target description, the corpus contracts and
  the specification reach the workers inside their bundles — pulling them into
  your context is how a manager runs out of room to track the run.

The single exception is the stall escalation: at rung ≥ 2 a report alone has
already failed, so you land **one bounded task** — and even then you land it
by delegating with a directive input, not by editing the tree yourself.

**The corpus ships its own contracts, and they are corpus declarations on the
same level as `chip.md`.**  Its entry document (the `AGENTS.md` or `README.md`
at the corpus root) names the input, the harness and a reading order; the
workers read the corpus in that order before planning.  This order names no
corpus file on purpose: what the corpus provides — its layout, its harness
commands, its machine-readable index, its construct inventory, its benchmark
and baselines — is whatever the corpus itself declares, and a statement here
would only be a second copy that drifts.

## What is being built: a compiler for the declared language, not for this corpus

Read this before the layout, because it decides what "done" means.

**The surface to implement is the one the language's specification declares**
— the public API of the source language the corpus is written in, at the
version the corpus pins, construct by construct **and parameter by
parameter** — not the list of constructs this corpus happens to call (a
construct inventory the corpus ships is that list: a sample).  Record it with
`api-spec` and account for it in `FRONTEND_COVERAGE.json`. Follow current
engine guidance for review and validation; do not substitute corpus counts for
language coverage.

**When the corpus declares a subset of the language, that subset is the
surface.**  A corpus may state that it targets a defined subset of the
language -- its subset document names the principles, the included
constructs and the explicitly excluded ones.  Then the surface to implement is
that subset, still construct by construct and parameter by parameter: the
`api-spec` record is the subset's, every included construct is implemented
with all the parameters the specification gives it (not only the values the
corpus passes), an excluded construct is `declared-unsupported` with a refusal
witness, and generality is measured inside the subset.  The subset narrows
*which* constructs; it never narrows how completely each one is handled.

**The corpus is a sample of that surface, not the contract.**  It calls
constructs with the parameters it happens to need and with their defaults.  So:

- a construct the corpus never calls is a construct about which no corpus
  result says anything;
- a *parameter* the corpus never varies is untested however green the run is —
  and the first caller who varies it is then the test.

"every corpus case passes" is a statement about the corpus.  It is
compatible with a compiler that handles only the corpus, and that is the
failure mode this order exists to prevent.

**Outside the declared support set, refuse loudly at compile time.**  Every
construct is either implemented (with evidence and its covered parameters
named) or `declared-unsupported` **with a refusal witness**: a command that
must fail, proving the compiler rejects the construct with a diagnostic
carrying a source location.  Declaring something unsupported is a legitimate
engineering answer.  Declaring it unsupported and then silently mis-compiling
it is the defect.  A silent wrong answer is worse than a refusal, always.

**Two rings — and the outer one is the operator's.**

- the **inner ring** is the corpus under `ops/`.  Develop against it, fix
  against it, and retain fixes in reproducible regressions. Targeted development
  runs never remove a case from the full input set.
- the **outer ring** is held by the operator, outside this project: operators
  this run never sees, evaluated on the finished compiler after `DONE`, for
  correctness. Do **not** build a held-out set from the
  corpus and do not go looking for one — anything this run can read is inner
  ring.  Declare one with `heldout` only when the target addendum names it
  (it then lives outside the scanned corpus root, is sealed by digest, no task
  reads it, and the final validation runs it once).  The consequence is the
  requirement: the compiler must generalise.  No operator-specific table,
  configuration or code path; the compiler must accept a new legal kernel through
  its declared language features, rather than replay a cache of known operators.

**Optional differential campaigns.** Exercise the declared surface with a
campaign when additional evidence is useful. The manager sets its scope and
budget; the worker chooses reproducible cases from the declared specification
and observed risks, without inspecting held-out inputs. Record outcomes through
`fuzz-campaign`; no engine-generated plan or fixed case quota is required.

**Classify every failure on unseen input under a taxonomy declared up front:**
`declared-unsupported` (outside the support set, refused loudly — compliant),
`in-spec-defect` (the compiler's bug — debug or replan), `corpus-defect` (the
case is wrong).  A category invented after the results lets every failure
become whichever one is cheapest.

## The operator corpus — what it is and how it is used

The corpus under `ops/` is the **inner ring**: the sample you develop against.
It is not one program to compile: it is a set of **self-contained operator
files**, each of which the compiler must handle independently, in every
declared shape and dtype.  Everything concrete about it — which directories are
the input, how many operators and cases there are, how a case is built and
compared, which commands run it, how the benchmark is laid out — comes from the
corpus's own documents and is measured with the corpus's own commands.  The
rules below are the ones that hold for any such corpus.

### Read the corpus the way it says, and declare what it declares

- **The input is what the corpus declares as input** — never everything with a
  source extension under `ops/`, and never the runner.  Declare it before the
  scan, citing the document that says so, so the scan counts operators and not
  the harness. Use `operator-set` with the corpus-declared globs and source
  citation, then `ingest-ops`. Anything the corpus says is not input (a selection
  pool, a maintenance tree) is not input, even if it happens to be present.
- **The numbers come from the corpus's own enumeration**, run in the project
  and recorded with `record-case-totals` and `group-order` — operators, cases
  and compile identities per tier.  **Never hand-copy a number** from a
  document, this order included; a number in a report derives from the command
  that produced it.  A declared tier that executes zero cases is a harness
  defect, not coverage.
- **A machine-readable index, when the corpus ships one, is the source** for
  the frontend coverage matrix, the task split and per-operator facts
  (parameters, constexpr values, grids, shapes, dtypes, features).  Read it
  instead of re-deriving the same facts from the source, and never regenerate
  or edit it.
- **The corpus's harness is the correctness gate.**  A compiler plugs in
  through the device protocol the corpus defines; the harness builds every
  case, launches it through that device, and compares against the case's own
  reference.  Its per-case status vocabulary and its failure-attribution table
  are the classification the census uses — read them from the corpus, do not
  invent a parallel one.  A reference device the corpus ships proves the
  harness right before a failure is trusted; it is never the compiler.
- **Known exceptions are the corpus's to declare.**  A case the corpus
  documents as failing on its reference device for a stated reason is not a
  compiler failure; nothing else is excused.

### What the compiler does with one case

For each `(operator, shape, dtype)` the compiler lowers the operator's kernel
through the **full pipeline** to the target's own artifact, binds the case's
buffers and compile-time values to the compiled unit, launches it with the
case's grid, reads the outputs back, and the harness compares them under the
case's declared comparison — integer / index / boolean **exact**, floating
point within the declared tolerance. The project adapter prepares host buffers
and invokes the complete native program; every convention the corpus states about buffer
views, element types and repeated launches over the same buffers is part of
the contract.

### Compilation identity and reuse

Compile and cache complete native programs through one compiler entry point.
The cache key covers every dependency that affects generated code: source and
helpers, signature, compile-time values, target features, compiler options,
argument layout and the native runtime interface. Runtime shape, grid and worker
values remain runtime inputs when the program supports them dynamically. If a
value is embedded or specialized, include it in the identity; do not reuse a
program with stale baked-in launch or workspace assumptions.

Reuse compiled code across compatible cases and repeated invocations. Never
recompile or return to Python for individual program instances. The compiler
receives the execution contract, not oracle outputs; a code cache never stores
answers in place of computation.

## Working-period discipline — how increments land

- **An end-to-end vertical slice before breadth.** After independent architecture
  review, delegate a small operator through parsing, semantic representation,
  lowering, assembly generation,
  assembly/linking, native execution and independent comparison. Exercise its
  one-worker and multi-worker paths. Then bring up a suitable matrix example
  with real instruction execution before expanding matrix coverage.
- **Use the whole corpus to classify failures.** After the slice establishes
  the execution path, scan every declared group. Classify failures by the first
  incorrect stage or shared language feature, then repair against that evidence.
  Do not finish one group while leaving the rest unexamined. Follow the current
  engine's repair budgets; a targeted pass is not a full regression pass.
- **Land executable increments.** A worker delivers a component together with
  its actual consumer integration and relevant verification. Keep compile/run
  and full-scan drivers in the compiler project's `tools/`, separate from the
  prepared `a100_support/` adapters. Drivers call the same compiler pipeline.
- **Preserve work across sessions.** Commit completed increments. Record a
  deliberate interruption through the workflow handoff protocol with remaining
  work and reproducible commands; do not report a budget boundary as a compiler
  bug or leave progress only in conversation.
- **Bound long commands.** A timed-out compile, execution or reproduction is
  unfinished or unverified work, never a pass. Keep its failure evidence. Workers
  may run bounded scans in the background while doing independent work; the
  manager follows the harness's worker wait/report protocol, without sleep loops.

## IR and pipeline design — explicit contracts

Choose representations and stages from the source semantics and sourced A100
facts. Record their producer/consumer contracts in the architecture and task DAG
before implementation, and obtain independent review. There is no prescribed
number of IR levels, modules, passes, tasks or source lines.

- **Preserve semantics before lowering.** Represent types and signedness,
  shapes and broadcasting, masks and inactive values, cast versus bitcast,
  indexing, control flow and collective semantics explicitly where needed.
  A later stage must not guess information an earlier stage discarded.
- **Make work distribution representable.** The design identifies logical
  program IDs, native worker ranges, vector lanes, matrix tiles, temporary
  storage and stage dependencies. Repartitioning the source grid must preserve
  coverage and observable semantics. Parallel execution is generated program
  behavior, not concurrent execution of unrelated test cases by the harness.
- **Make stage boundaries inspectable.** Provide diagnostics and representation
  dumps that can locate the first incorrect stage. Check relevant invariants
  such as operand types, masks, control-flow joins and legal target operands;
  include rejection cases when validating those checks. Use structural checks
  and round trips where appropriate to the chosen representation, without
  imposing a universal verifier package or fixed test quota.
- **Declare transforms and their dependencies.** The pipeline has a single
  declared ordering, with the information each stage consumes and invalidates.
  Transformations must consume valid dependence, alias or liveness information
  when their legality depends on it. Do not duplicate lowering inside drivers.
- **Change defective contracts through replanning.** A representation that
  cannot express required behavior is a design issue. Repair that boundary and
  obtain fresh review instead of patching the emitter to hide the mismatch.

## Compiler engineering — responsibilities that reach execution

These requirements guide implementation and review of the behavior the inputs
need. They preserve the basic optimization pipeline below, without adding a
separate depth gate, component ladder, speculative pass suite, autotuner,
calibrated cost model or performance objective. A placeholder module,
an unused interface or a pass that the pipeline never calls is not evidence of
an implemented capability.

### Frontend and semantic fidelity

Read each kernel and its legal helper calls through the declared language
surface. Resolve signatures, constexpr values, types, shapes and broadcasting
consistently; preserve masks, pointer/alias semantics, reductions, scans and
atomic behavior when used. Parsing, inference and unsupported-input diagnostics
carry source locations. Compile by language constructs rather than operator
names, and check the joins between frontend output and its downstream consumer.

### Analyses and transformation pipeline

Implement the control-flow, dependence and liveness analyses the chosen lowering,
parallel partition and allocation actually consume. A transform must preserve
or invalidate those results when it changes their subject. Register the chosen
passes/stages in one pipeline or pass manager; make their ordering and diagnostic
trace inspectable, and support stage-local verification/dumps for debugging.
Canonicalization, legalization and any other implemented transforms must be
exercised through the real pipeline and compared under the original case policy.
Do not add speculative passes or performance tasks merely to fill a checklist.

### Basic optimizations are implementation work

Implement and enable the workflow's basic general optimizations: common
subexpression elimination (CSE), dead-code elimination (DCE), constant folding
and propagation, copy propagation, strength reduction and loop-invariant code
motion (LICM). Schedule their implementation and consumer integration before
full validation. They are ordinary `coding` tasks with purpose `input`, using
the actual implementation dependencies and relevant component tags. Do not mark
them with capability/purpose/tag `optimization` or gate G9: those metadata select
the measured performance work that this scope excludes.
Mechanisms may share passes or modules; no separate task or module per mechanism
is required.

Apply rewrites by semantic structure and proven preconditions. Preserve effects,
atomics, aliasing, masks, zero-trip loops, arithmetic width/overflow and the
original floating comparison policy. CSE and LICM must not reuse or move memory
accesses without the needed dependence/alias proof. Unsupported preconditions
decline a rewrite; they do not justify replacing an entire pass with a stub.

Check positive rewrites and relevant rejection cases using independently stated
IR/code expectations, then compare executed outputs against the original
reference. Pass switches or traces can show which transformation ran and help
localize a regression; they require no timing or fixed counter quota. A pass
with no eligible pattern in one case may do nothing. The full native regression
uses the normal pipeline with these optimizations enabled, including the required
worker and applicable matrix paths. Skipping their implementation because the
unoptimized corpus passes is not the requested compiler delivery.

Keep this work in the reviewed implementation plan and its tests; do not invent
a new engine gate, pass-count/line-count threshold, tuning requirement or
post-correctness performance phase to enforce it.

### Native backend, allocation and ABI

Lower semantic operations to legal scalar, RVV and applicable IME instructions
using sourced operand and register constraints. This native backend owns physical
register assignment, preserved/clobbered state, spill/reload correctness, stack
layout and the calling convention where needed; the assembler/linker do not
replace those responsibilities. A simple legal allocator is acceptable: there
is no required allocation algorithm, spill-reduction target or scheduling score.

Bind argument types, buffer sizes, strides, scalars, aliases, alignment, workspace
and constants consistently across emission and execution. Host addresses are not
guest addresses; use the prepared adapter's marshaling/relocation contract.
Check calls, tails and pressure cases that could otherwise corrupt values.
Instruction selection uses semantic patterns and target facts, never per-operator
branches. Mechanical instruction emission and tool invocation consume that
lowered representation; do not generate operator C/C++ and outsource codegen.

### Complete-program runtime and driver

The compiler-generated program owns entry/argument binding, work ranges, native
program loops, vector/matrix computation, stages and result production. A common
native runtime may provide threads, barriers, allocation and I/O. Clearly define
private/shared data, lifetimes and the interface between generated code and those
services. The worker pool and reusable buffers belong to one executable process;
repeated calls within it reuse them. A new process has a new runtime instance.

Connect the compiler to `a100_support/native_device.py` and its `compile_case`
interface. The host adapter may compile, marshal inputs, start one complete
operator program and compare outputs. It must never iterate over program IDs or
schedule partial kernels in Python. Provide a reproducible compile/run interface
and relevant integration checks, including repeated execution with case-defined
input reset and synchronization. No benchmark or timing interface is required.

## Authority and precedence

- The engine (gates G0-G9, schemas, task lifecycle, evidence digests) is
  mechanical and is **not** amendable by this order.  Author evidence the way
  the engine verifies it; never fight or proxy a gate.
- The per-task role contracts (`agents/*.md`) and skills (`skills/*/SKILL.md`)
  are delivered by the engine with each task's context bundle and stay
  authoritative for how a task is executed.  This order binds the **whole
  run**: what the plan must contain, what the evidence must look like, and
  what overrides the engine's defaults.  Where this order is stricter than a
  skill, this order wins.
- **Continuity across attempts.**  Every later attempt starts from
  `PROJECT_STATE.json` with the built-in takeover prompt, not from this text.
  Anything in this order that must survive the first session — the bar,
  components, priorities, protocols — is transcribed at planning time into the
  artifacts the engine and the takeovers read: the task DAG, the architecture
  contract, and recorded facts/decisions. An audit objective is optional and
  cannot add a performance or depth completion gate. A directive
  that lives only in this file is a directive a later session may never see.

Named state, planning and verification artifacts are created by their owning
tasks after launch. Do not pre-create empty reports, task definitions or state
renderings during project preparation.

## Completion criterion — every operator compiles AND verifies numerically

- The run may reach `DONE` only when **every operator the corpus declares as
  input**, in every tier, recursively, passes **both** gates below.  Neither gate may be
  traded for the other, and neither may be satisfied for only part of the
  corpus.

  1. **It compiles.**  Each operator is lowered through the full pipeline
     (frontend -> semantic IR -> backend -> target artifact) and built with
     the target's own toolchain.
  2. **It verifies numerically.**  The built kernel is executed under the declared
     target endpoint with **every declared shape** in `SHAPES` and **every declared
     dtype** in `DTYPES`, and its outputs are compared against the operator's
     own reference: integer / index / boolean outputs must match **exactly**;
     floating-point outputs must stay within the tolerance the case declares.
     Never widen a tolerance and never weaken a reference to make a comparison
     pass.

- An operator that does not compile, or whose outputs do not verify, is
  **unfinished work**, not a documented limitation: implement the missing
  language feature or fix the wrong lowering — do not exclude the operator and
  do not record it as unsupported.
- **Enumerate the corpus recursively and record per-tier case counts.**  A
  tier whose operators live in subdirectories is invisible to a flat glob; a
  declared tier with an executed-case count of zero is a harness defect, not
  coverage.  Record operators, total cases, passed, failed per tier with the
  validation.
- Numerical verification coverage is as mandatory as compilation coverage:
  no operator may be left un-compilable, un-executed, un-compared, skipped,
  sampled down, or narrowed out.
- Generalize by **language feature**: never dispatch on an operator name, never
  add a per-operator task, never paste a whole kernel.  A feature gap is fixed
  once, for every operator that uses it.  **A seeded repair batch is the
  exception to the last sentence**: it owns a case set, and making that set
  pass is its job -- a narrow fix that serves only the set is acceptable.  It
  is never an exception to the name rule: no branch on an operator, kernel or
  benchmark name and no pasted kernel, in a repair batch as anywhere else.

## Scope narrowing is forbidden (operator directive)

- **Never narrow the declared scope.**  Do not call `narrow-scope`, do not
  declare a subset or a prefix of the corpus's tier order, and do not record
  any decision that reduces the supported set below the entire corpus.  This
  directive **overrides every stall-rung instruction** that offers scope
  narrowing as a way out, at every rung.
- The declared supported set stays the **full corpus** for the whole run.  A
  failing tier, an unsupported feature or a hard kernel is **work**: fix it,
  delegate to the debug agent when out of hypotheses, raise a design issue and
  replan — the resolution is always a fix, never a smaller claim.
- The final validation must state the full scope it covered; a partial pass is
  never reported as coverage.
- If you conclude that no further progress is possible without narrowing the
  scope or leaving an operator un-compiled or un-verified, stop and report
  `BLOCKED` with the evidence.  Do not narrow.

## Evidence discipline — what counts and what does not

- **Only executed-and-compared counts as done.**  "Generated" or "built" is
  not a pass; no pre-generated artifact substitutes for a generated one.
- **Prepare the full manifest before execution.** Use the current regression
  prepare/record protocol and the corpus's independent comparisons. Record
  per-case executed results and bind them to the prepared input, run and actual
  executable. Summaries, task completion and legacy boolean checks cannot stand
  in for current full execution evidence.
- **A green validation describes the revision it ran at.**  A change to the
  compiler, the tests or the harness after the validation invalidates it;
  re-run from a clean state rather than editing the stamp.
- **An invocation that never reported is a failure, not a live one.**  A dead
  debug or audit call (provider error, killed turn, stop mid-flight) is
  closed as an orphan so it is visible and counted; check the invocation
  ledgers before concluding the run is merely slow, and report a task
  debugged repeatedly with no adopted outcome while it is still failing.

## Debug protocol — when something fails

- **Reproduce deterministically and minimise.**  Smallest shape, smallest
  input, fewest operators that still fail; a failure that disappears when
  minimised is two failures.  Record the exact command.
- **Walk the declared pipeline stages in order** — the stages the plan names,
  never a fixed list.  Compare the last correct representation with the first
  incorrect one; the first mismatch is the failing stage, later mismatches
  are consequences.  **Never fix the emitter or last stage to compensate for
  an upstream defect.**
- A local bug in one stage is a local fix; a producer/consumer contract
  mismatch or a stage that cannot express what an earlier stage requires is a
  **design issue** — raise it and replan; do not patch around it.
- **A candidate fix is verified on a disposable copy under a bound**, never
  in the project tree; an unverified fix is a hypothesis, and once applied
  the **full declared verification** runs, not just the reproduction.  Every
  fix leaves the regression test that would have caught it.
- **Record whether a debug fix was adopted** (`accepted` / `rejected`); the
  per-task debug ledger is what stops the run repeating a hypothesis that
  already failed.
- When out of hypotheses, delegate with `workflow_debug_input` (task id +
  reproduction) through a read-only Agent child — the child files its own
  `workflow_debug_report`. A `LOCAL_FIX` comes back as a delegated coding
  task (never apply a patch yourself); a `DESIGN_ISSUE` goes to replanning.

## Gate semantics — read them correctly

A red gate for a not-yet-run phase is pending work, not a defect. Advance to the
phase that owns its deliverable; do not replan merely because it has not run.
Use the current engine's computed requirements and manager guidance. This project
pins `correctness_only`: complete current full executed-and-compared regression
with required resource evidence, then final validation and DONE. Do not require
G9 or turn a passing correctness result into a performance-optimization task.
The normal implementation and validated program include the basic optimizations;
skipping a measured performance phase does not remove them from the compiler.
Environment probes and x86 reference passes are not candidate compiler evidence.

## Target addendum — A100 native execution

- `chip.md` owns the target and acceptance contract. Search the local knowledge
  pack with `workflow_target_search`, then read citations with
  `workflow_target_source` before recording hardware Facts.
- The compiler emits program-level assembly for a **complete single operator**:
  entry/argument binding, program-ID/range loops, vector or matrix computation,
  stages, synchronization and workspace use. Assemble and link with the declared
  native tools. A common precompiled C/C++ runtime is allowed; do not delegate
  operator lowering to a generated C/C++ wrapper or another code generator.
- Python may compile, prepare inputs and compare results outside the executable.
  Once launched, the operator program must run without Python, including native
  worker scheduling and every program iteration. The reference service remains
  separate: compiled x86 Triton CPU validates attack questions only.
- Support 1/2/4/8 compute workers, RVV and applicable real IME instruction paths.
  Plan and review work coverage, tails, private/shared workspace, persistent pool
  reuse, synchronization and result merging. Representative multi-worker/matrix
  cases require actual useful worker activity and dynamically executed matrix
  instructions bound to the same prepared run, case and executable.
- Validate the complete operator's outputs for each worker configuration under
  the original comparison policy. Include uneven ranges, vector/matrix tails
  and repeated calls where relevant. Multi-stage work follows its dependencies:
  local computation, necessary synchronization/merge, then dependent work.
  Keep independent work within workers where possible. Check data visibility,
  race freedom and workspace reuse across the complete call.
- For matrix lowering, derive tile/layout, accumulation type, register grouping,
  overlap restrictions and implicit control state from the cited specification.
  Check ordinary/vector tails and real matrix execution against the independent
  result. These are correctness requirements; no throughput claim, timing,
  thread-count speedup, tile sweep or performance comparison is required.
- QEMU guest threads are the current functional execution units. Board topology,
  core placement and hardware resource discovery are checked when porting; do not
  invent physical A100 core IDs from the QEMU configuration.
- Preserve the pinned emulator's BF16 IME format-control gap as unverified. Keep
  BF16 semantic cases; do not report vector or FP16 success as BF16 IME proof.
- Reuse `a100_support/` for prepared execution/reference adapters. The compiler's
  own drivers may use `tools/`. Integrate through `a100_support/native_device.py`
  and configure `A100_COMPILER_FACTORY=module:factory` after implementation.

## Stopping rule

Continue autonomously after launch until the workflow reaches DONE, with every
input operator executed and compared under the declared policy, or report a true
external blocker with its exact evidence and smallest next step. A failing case,
an unsupported in-scope construct or a complex kernel is work: fix it, delegate
debugging, or raise a design issue and replan; never skip it or narrow the corpus.
Follow explicit repair budgets and preserve unfinished failures when one expires.

Use the project's `workflow_*` MCP tools and slash commands. For a shell fallback,
load `.env` and its declared PYTHONPATH before calling
`python3 -m compiler_agent --root . --json <cmd>` from the project directory.
