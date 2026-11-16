---
name: compiler-design-retrospective
description: Synthesize compiler optimization records into evidence-backed architecture and data-structure good/bad practices and successor design recommendations. Use for cross-round retrospectives; does not implement a redesign or start optimization rounds.
---

# Compiler design retrospective

For copyable prompts covering multi-round optimization, this retrospective,
successor design and pass reuse, see the
[human-guided lifecycle](../optimization/references/human-guided-lifecycle.md).

## Scope and sources

Use when the human asks to review accumulated optimization experience or prepare
the design of a successor compiler. Read the selected projects' optimization
indexes, relevant records, architecture documents and cited code/IR evidence.
Follow the existing [optimization record guide](../optimization/references/optimization-record.md).
Records are derived knowledge; the target description and operator corpus remain
the only required project inputs. Missing historical records limit the conclusions,
not permission to invent experience or require a new input package.

Write the requested retrospective in the current project's `docs/compiler-agent/`.
Use its existing layout or `design-retrospectives/<topic>.md`, linked from the
optimization index. Keep source projects and historical attempts unchanged.
Record source project paths, record ids, revisions and evidence locations so the
reasoning can be reconstructed without this conversation.

This is a human-directed synthesis task. Do not edit compiler code, architecture
contracts, engine state or acceptance scope, run new performance experiments, or
start another optimization round merely to complete the retrospective. Identify
missing evidence and the smallest useful check; undertake it only within the
human's requested scope. No manager task or engine gate is required for direct use.

## Build an evidence-grounded retrospective

1. Bound the review by the human's topic or selected history. Inventory accepted,
   failed, reverted and incomplete attempts. State exclusions and unavailable
   evidence; do not select only successful optimizations.
2. Group attempts by shared mechanisms and representation needs, such as memory
   effects, layout knowledge, def-use access, analysis invalidation or lowering
   boundaries. Operator names and identical pass names do not establish shared
   semantics. Track the revision at which a property held; a later repair may
   already have removed the obstacle.
3. Trace each proposed lesson from a concrete architecture/data-structure property
   to an observed consequence: transformation expressibility, proof of legality,
   implementation duplication, correctness failures, or measured performance.
   Keep implementation convenience separate from runtime benefit. A profile
   symptom alone cannot prove a design defect.
4. Compare supporting and contradictory attempts. Repeated reports derived from
   one experiment are one evidence source. Explain context and tradeoffs rather
   than ranking designs by raw mention counts. Distinguish compiler-independent
   mechanisms from K3 A100 constraints and measurements of particular workloads.
5. Recommend the smallest design change that addresses the supported issue, or
   preserve an enabling design. Explain what information/interfaces the successor
   needs, which passes benefit, migration cost and what remains unproven. Avoid
   adding an IR level or generic framework without a demonstrated consumer.

## Deliverable

Include a source/coverage summary and a lesson table with stable lesson ids:

| Field | Required content |
|---|---|
| Practice | Good, bad, or conditional; architecture or concrete data structure |
| Property and mechanism | What the design enables or obstructs, and why |
| Evidence | Source records, revisions, code/IR locations and actual results |
| Limits | Counterexamples, unavailable evidence and applicability boundaries |
| Confidence | Observed in cited context, hypothesis, or contradicted |
| Successor action | Keep/change/avoid/investigate, interface needed and tradeoff |
| Pass impact | Optimizations enabled, portable parts and required adaptations |
| Validation | Smallest check needed to test the design recommendation |

Use this table as a content guide, not a requirement to invent an entry for every
category. Report no supported finding where appropriate. Label an unimplemented
successor design as a proposal even when its motivating defect is well established.

Finish with prioritized successor design recommendations, unresolved conflicts
and a pass reuse shortlist. For each shortlisted pass cite its original record,
required semantic properties/analyses, known ordering constraints and missing
capabilities. Preserve counterexamples and link superseding retrospectives rather
than silently rewriting earlier conclusions.

## Handoff

Return the retrospective and evidence limits to the human. If a successor design
is requested, use [compiler-planning](../compiler-planning/SKILL.md) to consume
the findings and record which lessons informed architecture decisions. If a pass
port is requested, use [compiler-pass-porting](../compiler-pass-porting/SKILL.md).
Neither follows automatically from finishing this skill. A retrospective is
advisory knowledge, not correctness, performance or architecture-review approval.
