---
name: compiler-pass-porting
description: Assess and port a documented optimization pass to another compiler or IR revision, reusing algorithms and evidence with minimal necessary profiling. Use for known-pass reuse; verify current legality, full correctness and measured benefit before claiming an improvement.
---

# Compiler pass porting

For copyable assessment/implementation prompts and the preceding optimization,
retrospective and successor-design stages, see the
[human-guided lifecycle](../optimization/references/human-guided-lifecycle.md).

## Human-directed scope

Use after the destination compiler has current full input execution/comparison
evidence. A request to assess portability ends with an applicability report;
a request to port includes implementation, verification and documentation. Do not
start a redesign, port additional passes or launch subsequent optimization rounds
outside the requested scope. Routine work within an authorized port does not
require approval at every step.

Use [optimization](../optimization/SKILL.md) for measurement and correctness
rules, and the [optimization record guide](../optimization/references/optimization-record.md)
for the destination record. This skill can run directly without manager tasks,
engine transitions or acceptance-scope changes. Existing engine-managed tasks
retain their contracts; direct reports do not assert engine gates passed.

## Inspect the source and destination

Read the selected source pass, its optimization record, relevant tests, known
counterexamples and any [design retrospective](../compiler-design-retrospective/SKILL.md).
Inspect the destination's actual IR, semantics, pass manager, verifier, analyses,
runtime boundary, target facts and corpus comparison policy. Historical knowledge
is derived evidence, not a third required input. Missing old documentation can be
reconstructed from code and tests, with gaps and uncertainty recorded explicitly.

Record source and destination revisions and dirty changes. Keep the source project
read-only, preserve unrelated destination edits and establish a destination rollback
boundary. Never copy old operator names, IR syntax, hardware values, commands or
speedups as destination facts. The generated compiler and ported code belong in
the destination project, not this workflow repository.

## Applicability map

Before implementation, write a compact map in the destination optimization record:

| Source requirement | Destination evidence and interface | Disposition |
|---|---|---|
| Matched IR structure and semantic preconditions | Actual operations, types, effects and guards | Reuse/adapt/missing/inapplicable |
| Analyses and mutation/invalidation rules | Current APIs and ownership | Reuse/adapt/missing/inapplicable |
| Pipeline position and interactions | Producer/consumer passes and preserved information | Reuse/adapt/missing/inapplicable |
| Target constraints and profitability choices | Sourced destination facts and tunable parameters | Reuse/adapt/missing/inapplicable |
| Tests, fallback and observability | Current verifier, runner and pass controls | Reuse/adapt/missing/inapplicable |

Cover relevant legality conditions explicitly: dtype and integer overflow,
floating-point policy, masking and bounds, aliasing, side effects, dependence and
execution ordering as applicable. Similar opcode or interface names are not proof
of equivalent semantics. Keep missing capabilities distinct from an optimization
that does not apply to the destination's structures.

Reuse an equivalent destination pass or its configuration before introducing a
duplicate. Separate portable transformation/analysis algorithms from source-specific
IR glue and target tuning. Small adaptations within the reviewed architecture
can be implemented as part of an authorized port. If essential information is
unavailable or a semantic contract must change, document the gap and follow the
project's DesignIssue/replanning and review rules; do not silently redesign the
compiler or implement against an unreviewed changed contract.

## Choose the minimum evidence collection

An established mechanism plus verified destination preconditions can justify
porting without broad profiling. Explain which source evidence transfers, which
destination checks establish applicability and why new profiling is omitted.
Do not fabricate a current profile manifest from historical observations.

Collect a targeted profile or IR/code comparison when applicability, execution of
the transformed path, or the source cost mechanism is uncertain. Use
[profile-to-compiler-pass](../profile-to-compiler-pass/SKILL.md) for fresh collection
and attribution. If a destination bottleneck differs or performance contradicts
the hypothesis, diagnose that gap rather than repeatedly copying source tuning.
No adapter is required merely to reuse a pass without fresh profile collection.

Skipping profiling never skips current result checks or the measurements needed
to claim a speedup. Source measurements remain evidence about the source compiler.

## Implement and verify an authorized port

1. Integrate through the destination's pass infrastructure, retaining legal
   structural guards, fallback, analysis invalidation and appropriate ordering.
   Provide a pass switch or equivalent controlled comparison and before/after IR
   evidence that the transformation actually fires. Reject unsafe matches.
2. Adapt source tests to destination semantics and add checks for actual mapping
   risks, including relevant boundary/rejection cases. Run the verifier and
   affected cases, then full input execution and comparison at the resulting
   program identity. Preserve the original cases, references and tolerances;
   never substitute successful generation/build for execution and comparison.
3. Measure a reproducible destination baseline and comparable candidate outside
   the profiler. Compare pass-off/on where needed to distinguish pass benefit
   from integration changes. Keep raw samples, noise rule, commands, target and
   environment facts, artifact identities and complete operator timing boundaries
   under `docs/compiler-agent/`. Preserve required multi-core and applicable IME
   paths; source placement or tuning is not destination execution evidence.
4. Report portability, correctness and performance separately. A pass can be
   applicable and correct with no reproduced gain. Repair or roll back an
   unprofitable candidate under the optimization rules; retain the attempt and
   diagnosis. Mark unavailable execution as outstanding rather than claiming a
   completed port or improvement. Keep long commands bounded by timeouts.

## Record and return

Create a destination optimization record and index entry linked to the source
record and any retrospective lesson ids. Include the applicability map, reused
algorithm/code, adapted interfaces, new checks, omitted/targeted profiling rationale,
measurement and regression evidence, and final disposition.

Record architecture and data-structure good/bad practices actually exposed by the
port: what made reuse straightforward, what forced reimplementation, which earlier
lessons held or failed, and the resulting migration advice. Distinguish observed
facts from hypotheses; no supported finding is preferable to invented praise or
criticism. Leave source records unchanged and link any contradicting new evidence.

Return the result to the human and stop at the requested boundary. New experience
can later be synthesized with compiler-design-retrospective; do not automatically
start that task or another pass port.
