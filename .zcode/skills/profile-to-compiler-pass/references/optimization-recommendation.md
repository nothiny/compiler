# Optimization recommendation contract

`OPTIMIZATION_RECOMMENDATION.json` answers what the evidence says to optimize
before committing to a particular IR rewrite. It remains useful when the
project's IR is only partially exported or when the bottleneck belongs outside
the compiler.

## Envelope

~~~
{
  "schema_version": 1,
  "campaign_id": "<profile campaign>",
  "status": "proposed|evidence_needed|out_of_scope|accepted|rejected",
  "recommendations": [
    {
      "id": "<stable id>",
      "action": {
        "category": "<structural optimization category>",
        "description": "<what to optimize>",
        "scope": "existing_pass|new_pass|lowering|runtime|workload",
        "candidate_existing_pass": "<opaque project pass name or null>"
      },
      "evidence_refs": ["<manifest observation>", "<bottleneck id>"],
      "observed_in": ["<workload id the structure was observed in>"],
      "ir_context": {
        "mapping_status": "verified|partial|unavailable",
        "level_id": "<opaque project level or null>",
        "structural_properties": ["<observed IR property>"],
        "references": ["<snapshot, source, or trace reference>"],
        "limits": "<what the mapping cannot prove>"
      },
      "mechanism": "<why the action could improve the measured cost>",
      "legality_questions": ["<condition to prove>"],
      "risks": ["<resource, semantic, or generality risk>"],
      "expected_evidence": ["<metric or code change to check>"],
      "required_followup": ["<smallest next experiment>"],
      "confidence": "low|medium|high",
      "disposition": {"state": "deferred|out_of_scope",
                      "reason": "<why this one was not taken up>"}
    }
  ]
}
~~~

`category` describes the mechanism rather than an IR opcode. Examples include
reducing memory traffic, improving access regularity, shortening live ranges,
exposing parallel work, reducing dependency depth, or changing a legal
schedule. The adapter and project facts may use a more precise vocabulary.

## Decision rules

- Prefer an existing pass named by the current `PASS_CATALOG`. A recommendation
  is not permission to add another pass.
- `mapping_status: verified` requires a checked relation between the profiled
  generated range and the current IR structure or pass trace. A familiar
  operator or symbol name is not enough.
- `mapping_status: partial` or `unavailable` must include a follow-up that can
  improve the mapping. It must not emit a concrete rewrite as if it were
  proven.
- `scope: workload` or `scope: runtime` is a valid result when the profile
  identifies a problem the compiler cannot fix safely.
- An optimization batch may act on a recommendation only when its mapping
  is `verified`, its legality conditions are expressible in the current IR,
  and its chosen layer fits the cause. Reuse an existing pass/configuration when
  it covers the action; implement a new pass only when that route is insufficient.
  For lowering/runtime detail changes, explain why a reusable pass is unsuitable.

## Required adapter context

The adapter supplies opaque snapshots rather than a shared IR schema:

- level identifier, exporter or printer entry, dump path and digest;
- verifier entry and executed result;
- before/after pass snapshots and pass catalog entry;
- source or origin mapping with its precision and limits;
- pass switch, fallback, and trace references.

The recommendation layer may compare these fields across experiments, but it
must never infer that two levels or operations with similar names have the same
semantics.

## `observed_in` is what makes a general claim checkable

Each recommendation names the profiled workloads its structural observation was
actually seen in. They must be workloads the campaign manifest declares, so the
breadth of the evidence is **read from the campaign** and never asserted by the
bundle that benefits from it.

A bundle cites recommendation ids (`--evidence`), and the engine computes the
union of their `observed_in`:

- one workload — the transformation is a specialisation of that case however it
  is labelled. It may be recorded as a `fastpath` with the general path it
  falls back to, which keeps the fine-grained path alive and says what the
  bundle is; it may not be recorded as `targeted`.
- more than one — the same structure was observed in more than one profiled
  workload, so `targeted` is a claim the evidence supports.

Whether two observations *really* share a structural property is a reading, not
a count, so `ir_context.structural_properties` is rendered for the reviewer
while the engine only counts workload ids. The way to widen a narrow claim is
never to relabel it: profile more of the declared surface, and come back when
the structure has been seen more than once.

## Recommendation dispositions guide later choices

Choose recommendations using evidence, expected benefit and remaining budget.
Unselected recommendations do not prevent acceptance of a measured improvement.
When recording a disposition, use the existing evidence format:

- **accepted** should be supported by the implemented passes and task evidence;
  a written disposition alone does not prove implementation.
- **deferred** records `disposition: {state, reason}` to explain a future choice.
- **out_of_scope** uses the same shape for costs outside the compiler's scope.

Task evidence can retain useful deferred ideas. G9 does not
require every recommendation to have a disposition or a final profiling campaign.
Actual selected evidence must still identify its campaign and remain applicable
when it is used to justify a change.
