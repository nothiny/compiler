# Bottleneck hypothesis contract

`BOTTLENECKS.json` records what a profile shows and the competing explanations
that remain. It is a hypothesis ledger, not an automatic pass selector.

## Candidate envelope

Each candidate contains:

~~~
{
  "id": "<stable id>",
  "workload": {"id": "<id>", "invocation": "<id>"},
  "evidence": ["<manifest observation or raw-report reference>"],
  "observation": "<measured phenomenon>",
  "candidate_causes": [
    {"id": "cause-a", "statement": "<falsifiable cause>", "confidence": "low|medium|high"}
  ],
  "support": ["<evidence reference>"],
  "contradictions": ["<evidence reference or none>"],
  "alternatives": ["<competing explanation>"],
  "unknowns": ["<missing fact or mapping>"],
  "attribution": {
    "status": "exact|range|partial|unavailable",
    "artifact_ranges": ["<range reference>"],
    "ir_nodes": ["<node reference>"],
    "passes": ["<trace entry>"],
    "limits": "<what the mapping cannot prove>"
  },
  "next_experiment": {
    "question": "<what it distinguishes>",
    "procedure": "<bounded command or project action>",
    "success_observation": "<what would support the cause>",
    "failure_observation": "<what would reject it>"
  },
  "action_layer": "pass|existing_pass|lowering|runtime|evidence_needed|out_of_scope",
  "status": "open|rejected|confirmed|inconclusive"
}
~~~

The `observation` must be directly supported by a manifest or raw report.
`candidate_causes` are explanations, not facts. A confidence value describes
the current evidence and must not be used as a substitute for the next
experiment.

## Attribution rules

Use compiler source maps or origin metadata when available. Otherwise cite the
artifact range, IR dump, pass trace, and comparison that support the mapping.
State whether the result identifies an operation, a block, a loop, a generated
range, or only a whole invocation. Never upgrade a coarse mapping to an exact
one because an operator or benchmark has a familiar name.

## Decision rules

- One observation may keep several causes open.
- A counter change without an independent metric is supporting evidence, not a
  confirmed speedup.
- A missing or ambiguous report instance yields `evidence_needed`.
- A cause that cannot be addressed in the compiler is `out_of_scope` and keeps
  its evidence for the next planning round.
- A cause that requires a new IR property raises the existing design-issue and
  replanning process before a pass is implemented.
- A rejected hypothesis remains in the ledger with its disconfirming evidence
  so the same experiment is not repeated without new information.
