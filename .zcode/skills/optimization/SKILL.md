---
name: optimization
description: Optimize an already correct compiler under human direction, using profiling and reusable passes first; record measured results and architecture/data-structure lessons for future compiler designs.
---

# Optimization

For a complete human-guided lifecycle with copyable prompts, read
[optimization through successor design and pass porting](references/human-guided-lifecycle.md).
Load it when the human asks how to run these stages; it is not a mandatory campaign.

## Separate implementation from optimization

Use this skill after the compiler has passed current full input execution and
comparison. Correctness delivery is complete independently of later performance
work. Do not automatically start optimization because implementation finished.
A human may request diagnosis, one pass, a local improvement, or several rounds;
perform the requested scope and return the result without starting another round.
A request to profile or recommend alone does not authorize implementation.
Within an authorized implementation scope, complete implementation, verification
and documentation without requesting permission for every routine step.

This skill can be used directly in a human-guided session without a manager,
delegated worker, engine task, optimization gate or acceptance-scope change.
Keep the existing state machine and target input unchanged. If invoked inside an
existing engine-managed optimization task, honor its contract and reporting route.
Manual evidence does not assert or bypass engine gates.

For reuse of a known optimization on another compiler or IR revision, use
[compiler-pass-porting](../compiler-pass-porting/SKILL.md) within the requested
scope. When the human asks to synthesize lessons across rounds, use
[compiler-design-retrospective](../compiler-design-retrospective/SKILL.md).
These are optional routes, not automatic follow-up stages of every optimization.

## Choose the optimization

1. Establish a reproducible baseline with the current compiler revision, artifact
   identity, workload, environment, commands, units, timing boundaries, samples
   and comparison policy. Preserve a rollback revision and unrelated changes.
2. Read relevant prior optimization records before collecting new evidence.
   For a new performance problem, profile the actual generated program and map
   the measured bottleneck to IR and compiler decisions. Use
   [profile-to-compiler-pass](../profile-to-compiler-pass/SKILL.md) for attribution
   and pass design. Report recommendations first when that is the requested scope.
3. Prefer an existing pass/configuration, then a reusable new pass. Match
   structural IR properties; define legality, analysis dependencies/invalidation,
   ordering and interactions. Use lowering, code generation or runtime detail
   changes when the evidence supports them and explain why a pass cannot suitably
   address the cost. Do not force a runtime problem into an IR rewrite.
4. Implement the authorized candidate or compatible batch. Preserve switches or
   another practical way to compare enabled and disabled behavior. Avoid operator
   name dispatch, precomputed answers and reference fallbacks. Fastpaths require
   structural guards and a correct fallback.
5. Run relevant legality and rejection checks, then full input execution and
   comparison at the candidate revision. Measure against the comparable baseline
   outside the profiler; accept a performance claim only for reproduced improvement
   beyond recorded noise. Repair or roll back unsuccessful candidates and retain
   the evidence. Never change original references, cases or comparison tolerances.
6. Record the optimization and architecture lessons using
   [the optimization record guide](references/optimization-record.md), including
   unsuccessful attempts. Return the outcome and useful next choices to the human.

Use existing profiles across compatible changes when they still justify the
choice. Reprofile when the bottleneck changes or a decision lacks evidence;
there is no mandatory full profiling campaign after every pass. When porting a
previous optimization, inspect its applicability and current IR first. If prior
evidence plus current structural checks justify the mechanism, skip broad
profiling or collect only the missing targeted observations. Historical speedup
never proves speedup on the new compiler: run current correctness and comparable
performance measurements, and record why profiling was reduced or omitted.

## Measurement and evidence

For K3 A100 single-operator executables, follow `A100-NATIVE-OPERATOR` and
`A100-OPERATOR-TIMING` in the
[target knowledge](../../docs/compiler-knowledge/targets/k3-a100.md).
Compare native full-operator calls across relevant 1/2/4/8-thread configurations,
vectorization choices and tile sizes within the requested experiment. Choose the
fastest correct configuration per workload while preserving required multi-core
and applicable IME paths. Derive eligible cores and tools from sourced facts.
Separate startup-inclusive process time from in-process steady-state time;
include dispatch, all stages, packing, synchronization, merge and necessary
per-call preparation inside the declared operator boundary.

Keep raw reports, commands and summaries under `docs/compiler-agent/`. Use the
project's full regression runner; when using engine regression recording, prepare
the manifest with `regression-prepare` before execution and submit the per-case
report with `regression-record`. Record engine optimization metrics only when
already operating in a phase and scope that support them. Direct human-guided
work uses the documented evidence without changing engine policy to permit it.

Keep long-running commands bounded with a timeout; an unbounded wait is not
progress. Missing evidence is not a measured zero;
a stopped experiment or exhausted budget is not successful optimization. Preserve
partial deliveries and classify unavailable external requirements with evidence.
