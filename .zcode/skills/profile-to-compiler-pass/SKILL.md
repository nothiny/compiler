---
name: profile-to-compiler-pass
description: >-
  Analyze real execution profiles and the current compiler's IR to recommend
  what to optimize, reuse an existing pass, or design a justified new pass.
  Supports human-guided profiling and pass reuse without assuming a fixed IR;
  records measured outcomes and reusable architecture lessons.
---

# profile-to-compiler-pass

For copyable human-directed profiling and implementation prompts, followed by
cross-round learning and reuse, see the
[lifecycle guide](../optimization/references/human-guided-lifecycle.md).

## Human-directed scope

Use this skill independently after correctness delivery, when the human asks for
profiling, optimization recommendations, pass implementation or reuse of a known
optimization. Follow the requested scope: diagnosis alone ends with recommendations;
implementation includes measurement, full regression and an optimization record.
Do not automatically launch another round or delegate workers. A manager task is
optional; when present, honor its scope, budget and existing reporting contract.
No state-machine transition or acceptance-scope change is needed for direct use.

Prefer existing pass configuration, then a reusable new pass, before modifying
lowering/emitter/runtime details. Explain an evidence-backed exception when the
cost belongs in those layers. One profile can support a compatible batch; isolate
passes or reprofile when the result or changed bottleneck warrants it.

For a known optimization being ported, first read its
[optimization record](../optimization/references/optimization-record.md), inspect
the current IR and verify its semantic preconditions. Reuse prior reasoning and
collect only missing evidence. Broad profiling may be omitted with a documented
reason; current correctness and independent performance measurements remain
required. Historical profiles retain their original identities and must not be
relabeled as measurements of the new compiler. In this reuse mode, the fresh-profile
adapter steps and profile-only outputs below apply only to newly collected data;
record applicability checks and prior evidence links in the optimization record.
Use [compiler-pass-porting](../compiler-pass-porting/SKILL.md) for the complete
source-to-destination mapping and implementation procedure. Cross-round design
synthesis belongs to [compiler-design-retrospective](../compiler-design-retrospective/SKILL.md)
when requested; it is not another profiling requirement.

## Purpose

Use this skill when a compiler already builds, executes, and compares correctly
and a real profile is available or will be collected for the compiled artifact.
For reuse of a documented optimization, follow the reduced-profiling route above.
First recommend what to optimize; when justified, design a reusable transformation through the
compiler's pass manager. A
single benchmark-specific rewrite, an emitter special case, or an unmeasured
performance guess is outside the skill's scope.

The shared procedure is target-independent. The project supplies a target
description, an operator corpus, and, for fresh profile collection, a
**backend-specific adapter** for the measurement system available in that project. The adapter is deliberately
allowed to contain concrete profiler, metric, generated-code, and resource
knowledge. Concrete reusable implementations live in the optional `adapters/`
extension directory or in the target project; commands and experiment bindings
are always declared in the target project. Its output is the generic manifest and hypothesis evidence defined
below. One workflow run is bound to one target description; evidence from
different runs must not be merged into a single current measurement. Prior-run
records may be cited separately to justify reuse.

## Inputs

Read these sources before running a command:

- the sourced target facts and their provenance;
- environment and permission facts, including the declared measurement route;
- compiler architecture, IR representations, pass manager, verifier, and
  source-attribution facilities;
- the operator corpus, comparison policy, and known-good revision;
- the current optimization plan and any open design issues;
- the project-provided backend adapter contract.

The adapter is a project capability, not a third required workload input. It
may select the concrete backend toolchain and report interface, but it must
declare those choices and normalize their results into the shared contracts.
Do not invent commands, report APIs, metrics, permissions, or code mappings. If
a capability is absent, report `adapter_required`, `environment_blocked`, or
`evidence_needed` with the exact missing evidence.

For the bundled adapter, read `adapters/a100/README.md` and its configuration
example from the workflow checkout. Use
the recorded RISC-V target and environment facts for the run.
Derive its configuration from the current project's actual runner, compiled
artifact, report paths, IR exports, and pass catalog; the agent writes this
configuration as an experiment artifact, not a new user-supplied input.
Collection may be sharded across verified, available A100 core sets using
`adapters/shard.py` (`--cores`, one child per core set, `{cases}` round-robin).
Identify eligible cores from the declared target-side topology and enablement
evidence; never assume core IDs or availability. Check the declared counter
scope and interference before collecting in parallel: counters need not be
core-local, and co-running cases does not establish comparable latency.
Run the adapter's normalize/attribute/recommend once over the merged reports.
Invoke its script using the workflow checkout's absolute path so the project
need not import or install this repository. An existing project adapter takes
precedence when it exposes the required evidence.

## Outputs

Write the following artifacts under the project's existing evidence directory
or the paths declared by its workflow. Keep raw reports beside their summaries.

- `PROFILE_MANIFEST.json`: identity, provenance, normalized observations, and
  code-attribution status for every consumed report instance.
- `BOTTLENECKS.json`: observations, falsifiable causes, alternatives, and the
  smallest experiment that can distinguish them.
- `OPTIMIZATION_RECOMMENDATION.json`: the required answer to "what should be
  optimized?", expressed using observed structural properties and the current
  project's existing pass or lowering layers.
- Optional design notes for the chosen batch, in the project's existing format.
- An [optimization record](../optimization/references/optimization-record.md) for
  every implemented attempt, including architecture/data-structure good and bad
  practices and a pass migration recipe.
- The existing optimization plan, task evidence when applicable, correctness result,
  benchmark report, profile comparison, and optimization metrics artifact.

These artifacts supplement existing gates. They do not weaken comparison
policies, replace raw evidence, or create a parallel state machine.

## Preconditions

The adapter and profile requirements below apply to fresh collection. For a
known-pass port with no fresh profile, use the reuse route above and the project's
existing build, comparison and benchmark tools.

- The compiler has a known-good revision and a runnable correctness suite.
- The project has declared how to build, execute, compare, benchmark, and
  export IR and generated artifacts.
- A backend-specific project adapter implements the interface described in
  `references/profile-manifest.md`.
- Measurement dependencies and permissions are provisioned before the run.
  This skill never installs packages, elevates permissions, or changes device
  configuration.
- The working tree and any isolation directory have been inspected. Preserve
  unrelated user changes and use a copy or branch for experiments when the
  project permits it.

Historical experiment directories are read-only examples. Their IR syntax,
pipeline stages, pass names, and paths are never defaults for another run.
Read `references/reference-sourcing.md` when selecting or adapting a parser.

## Procedure

### 1. Establish the experiment contract

Record the compiler revision, generated-artifact digest, target-fact
references, workload identity, shape and type metadata, layout, launch or
invocation configuration, active pass pipeline, comparison policy, benchmark
method, noise rule, and rollback revision. Separate build, setup, and steady
state execution time. Preserve the exact commands in task evidence.

The benchmark must measure the compiled artifact's own work. A driver that
parallelizes independent compilations, a setup-only timer, or a profiler's
replay timing cannot stand in for the declared steady-state metric. Keep
profiler conditions and benchmark conditions separate and record the
differences.

### 2. Preflight the adapter

Call the adapter's preflight operation using the project-declared entry point.
Record its tool and data-source versions, target identity, permissions,
supported observation classes, and all failures. Distinguish at least:

~~~
absent
present_but_unusable
unsupported
collection_error
parse_error
missing_observation
collected
zero
~~~

`zero` is a collected value; it is never a synonym for missing data. A
preflight failure is work to classify and repair. Do not continue with a
static guess while presenting it as profile evidence.

### 3. Collect and normalize real profile evidence

Ask the adapter to collect a profile of the compiler's actual generated
artifact and to retain the raw report. Enumerate every relevant report scope,
invocation, and observation instance. Select instances by workload identity,
invocation identity, compiler revision, artifact digest, target fingerprint,
and shape metadata. Never select the first instance merely because it is
convenient, and never match by a generated name alone.

Normalize only after preserving the source location of each value. For every
metric, retain its original name, value, unit, scope, collection status, and
evidence path. Keep unsupported observations distinct from parse failures and
from values that happen to be zero. The manifest contract is in
`references/profile-manifest.md`.

Adapter-generated recommendations are preliminary prompts for diagnosis.
They do not create bottleneck evidence or certify a transformation. A failed
collection or incomplete identity match remains a failed or incomplete
campaign even if files were written successfully. Consume raw reports and
the adapter's status before proceeding to the next step.

### 4. Form falsifiable bottleneck hypotheses

For each candidate, separate what was observed from why it might have
happened. Populate `BOTTLENECKS.json` using
`references/bottleneck-contract.md` with:

- workload and invocation identity;
- raw evidence references and generated-code locations;
- observed symptom and candidate causes;
- supporting evidence, contradictions, and competing explanations;
- unknowns and confidence rationale;
- the smallest follow-up experiment that distinguishes the explanations;
- the proposed action layer: pass, existing-pass configuration, lowering,
  runtime, `evidence_needed`, or `out_of_scope`.

A single counter, stall class, utilization value, or code hotspot is a lead,
not a transformation rule. If the evidence cannot distinguish causes, stop at
`evidence_needed` and specify the next bounded collection. If the cause is
outside the compiler, record `out_of_scope` rather than manufacturing a pass.

### 5. Attribute the hotspot to IR and compiler decisions

First discover the current project's representations, printers or exporters,
verifiers, pass catalog, switches, fallbacks, and trace format. Treat every IR
level and operation name as opaque project data. Do not assume a fixed number
of levels, a particular textual syntax, or a familiar pass name. The adapter
must retain an `IR_SNAPSHOT` for each inspected level and a `PASS_CATALOG` for
the passes available in this compilation.

Use the strongest available mapping in this order:

1. compiler-provided origin spans or source maps;
2. a checked mapping from generated-artifact ranges to IR operations and pass
   trace entries;
3. a minimal reproduction with IR dumps, generated-artifact diffs, and pass
   on/off comparisons.

State the confidence and limits of the mapping. Do not claim an exact
operation-level correspondence when only a symbol, block, or time interval is
known. Group observations by shared language or IR structure, not by operator
name or benchmark label. If the IR cannot express the proposed change, raise
the existing design-issue and replanning path before implementation.

### 6. Recommend the optimization before naming a pass

Write `OPTIMIZATION_RECOMMENDATION.json` using
`references/optimization-recommendation.md`. This is mandatory even when the
mapping is incomplete. State the optimization mechanism, its scope
(`existing_pass`, `new_pass`, `lowering`, `runtime`, or `workload`), the
structural properties that make it applicable, the evidence, competing
explanations, expected benefit, risks, confidence, and the next experiment.
Prefer an existing pass or pass configuration from `PASS_CATALOG`; do not
invent a new pass merely to turn a profile symptom into a task.

If the mapping is `partial` or `unavailable`, return the recommendation with
`evidence_needed` and the smallest required follow-up. A recommendation may
say what kind of optimization to investigate without claiming a concrete IR
rewrite.

### 7. Author the pass contract only when justified

Choose a compatible batch from the profile evidence and assigned budget. Explain
structural matching, legality, analysis dependencies, expected benefit, fallback
and rollback at the level needed to implement and review the change. Reuse
existing modules and analyses; several passes may share an implementation module.
Separate proposal files, per-pass switches and cost-model calibration witnesses
are tools to use when helpful, not mandatory delivery formats.

If the batch changes the architecture contract, edit
`ARCHITECTURE_CONSTRAINTS.json` directly and report the complete change to the
human or, in engine-managed work, the manager. Obtain fresh independent review
before further implementation against the changed contract. In engine-managed work, the manager uses the existing
review-input/review-report workflow; direct sessions follow the project's review
requirements without creating an engine task merely to use this skill. Review
the batch together; do not split the work into one task or approval per pass. A design defect still
requires a DesignIssue and planner replan. Deliveries remain preserved while
review is pending. Existing contract declarations and provenance remain readable.

Reprofile when a bottleneck changes or a decision needs fresh data, rather than
because another compatible pass was implemented. Keep the current full-input
regression and comparable measured improvement as acceptance evidence.

### 8. Implement and verify attributable candidates

Keep candidate changes and measurements attributable within the assigned budget.
Keep implementation and verification within the authorized scope; a new
hypothesis does not itself require another task or worker.

Register the pass through the compiler's pass manager, preserving an
independent on/off switch and trace entry. Run the IR verifier, legal and
illegal match tests, boundary and masking cases, alias/order cases where
relevant, the full correctness suite, and the project's comparison policy.

Keep three comparable variants:

~~~
known-good baseline
candidate revision with the new pass disabled
candidate revision with the new pass enabled
~~~

The disabled candidate controls for unrelated code changes. A correctness
failure cannot be repaired by deleting inputs, changing the reference, or
loosening the declared tolerance.

### 9. Measure independently and re-profile

Run the fixed steady-state workload outside the profiler, preserving raw
samples and the predeclared noise rule. Require an improvement beyond that
rule, with no unexplained material regression on the agreed representative
set. Re-run the adapter when the mechanism needs confirmation or the bottleneck
has changed; compare identity-matched instances and record the limits of the
comparison. A final full profiling campaign is not mandatory.

An improved metric does not prove the original mechanism. If the profile
change contradicts the hypothesis, update the bottleneck record and either
run the discriminating experiment or roll back. A counter improvement alone
does not replace execution-time or throughput evidence when the project metric
is execution time or throughput.

### 10. Accept, roll back, or replan

For an implementation request, record the chosen candidate's evidence, implement
it and measure the result. Use adapter manifests, bottleneck records and conditional
pass proposals when they support the actual decision, not as separate mandatory
tasks. Current full input regression and comparable measured improvement decide
the performance outcome. In engine-managed work, submit the existing optimization
metrics; direct sessions retain equivalent raw evidence and an optimization record
without claiming an engine gate passed.

Reprofile when a change affects the relevant bottleneck or the available evidence
cannot justify the next choice. Historical observations can explain a hypothesis,
but cannot certify current performance or correctness. Keep claims within the
scope actually measured and preserve legal guards and fallback for specializations.

Accept a performance improvement only when correctness, comparison policy,
independent benchmark, any collected profile evidence and required review pass.
Write the optimization record before reporting an implemented attempt complete;
separate verified lessons from hypotheses and include migration requirements.
For unsuccessful attempts, retain the failure evidence in the isolated attempt, roll back the candidate, or raise a design
issue. Do not claim completion from a generated artifact or an unexecuted
plan.

## Validation

Before reporting success, verify applicable checks from repository evidence.
Profile-specific checks apply to fresh collections; reduced-profiling reuse must
instead document prior evidence, current applicability checks and remaining limits:

- raw profile reports and normalized manifest have matching digests;
- every consumed observation has an identity, unit, scope, status, and source;
- each bottleneck has alternatives, contradictions, uncertainty, and a next
  experiment or an explicit out-of-scope reason;
- every recommendation states what to optimize, its scope, evidence,
  uncertainty, and required follow-up;
- the batch explains legality, analysis invalidation, tests, fallback and rollback;
- baseline, pass-off, and pass-on are measured on the same workload contract;
- the full correctness result is current for the candidate revision;
- the independent metric exceeds the recorded noise rule and any required
  efficiency objective;
- the optimization record explains why the change was chosen, its outcome,
  architecture/data-structure lessons and reuse conditions;
- for engine-managed work, the existing optimization gate accepts the evidence.
  Direct human-guided work does not require or assert that gate.

Run the project's normal tests and any skill/documentation lint. A target
independence check must pass for this shared skill. Keep target-specific
commands, metrics, and readers outside the shared workflow knowledge paths.

For a deterministic pre-review check, run
`scripts/validate_contracts.py --manifest PROFILE_MANIFEST.json
--bottlenecks BOTTLENECKS.json --recommendation
OPTIMIZATION_RECOMMENDATION.json --root
<evidence-root>`.
The validator checks required fields, enumerated statuses, and (when `--root`
is supplied) the recorded artifact and report digests; it does not approve a
proposal or replace the project's gates.

## Failure classifications

Use exactly one primary classification per attempt:

~~~
environment_blocked
adapter_required
evidence_needed
design_issue
local_fix
no_profitable_change
accepted
~~~

Keep the raw evidence and the next action for every non-accepted result.

## Artifacts modified

This skill authors project-side evidence, optimization recommendations, and
conditional pass proposals. The bundled optional adapters keep concrete
profiler integrations outside shared workflow knowledge; their per-experiment
configurations and outputs belong to the target project. Implement and verify
passes only within the human-authorized scope or existing assigned task. The skill
does not change the state engine, comparison policy, or gate implementation.
