# Optimization records and reusable design lessons

Read this guide when documenting an optimization attempt, porting an existing
pass or designing a successor compiler from previous experience.

## Location and scope

Keep records in the generated compiler project's `docs/compiler-agent/`, never
its compiler implementation in the workflow repository. Use the existing record
layout if present; otherwise keep one Markdown record per optimization under
`docs/compiler-agent/optimizations/` and an `INDEX.md` linking those records.
These are derived project documents, not new required user inputs or engine gates.

Give each record a stable id. Preserve prior results and link follow-up attempts;
do not overwrite a failed attempt with its later successful outcome. Link raw
reports, code revisions and measured artifact identities. The index should make
records discoverable by transformation, IR structure, architectural/data-structure
lesson and outcome, rather than only by operator name.

## Record contents

Use the following headings, adapting detail to the actual change:

### Goal and outcome

State the human's requested scope, candidate, baseline/candidate revisions and
status: proposed, accepted, rejected, reverted, or incomplete. For diagnosis-only
requests, record the recommendation and end there; do not fabricate implementation
or practice findings. Record failed attempts and their next useful experiment.

### Why this optimization

Describe the observed cost, raw profile references, IR/code attribution, causal
hypothesis and alternatives. Explain why an existing pass/configuration, new pass
or detail change was selected. If modifying lowering, codegen or runtime, explain
why a reusable pass was unsuitable. For reuse, cite the original record, current
structural checks and why profiling was reduced or omitted. Separate observed
facts, inferred causes and untested hypotheses.

### Transformation and reuse contract

Describe structural matching, semantic preconditions, legal/rejected cases,
required analyses, invalidation, ordering, interacting passes, fallback and
on/off controls. Link implementation files, entry points, tests and before/after
IR examples. Explain which parts are general, target-dependent or tied to this
compiler's representation. A pass name or source patch alone is not a reuse recipe.

### Validation and measurements

Link actual commands, environment/tool versions, workload shapes/types, original
comparison policy, timing boundaries, noise rule, raw samples and full regression
results. Compare baseline and candidate, and pass-off/on when relevant. State
regressions, confidence limits and measured scope. If execution was unavailable,
mark verification outstanding. Distinguish a successful port from a demonstrated
performance improvement; old measurements prove neither for a new compiler.

### Good practices and bad practices

Examine both compiler architecture and concrete data structures encountered in
this attempt. For every finding record:

- the component or representation, relevant revision and code/IR evidence;
- the enabling property or obstacle and how it affected this optimization;
- the context and tradeoff: when the practice applies and when it may not;
- the recommendation for a successor compiler and its validation status
  (observed, hypothesis, or contradicted).

Examples of properties to examine include preserved alias/layout/reduction
semantics, def-use access, analysis reuse/invalidation, mutation interfaces,
phase ownership and source attribution. These are prompts, not predetermined
judgments: a convenient representation is not automatically fast, and one
successful pass does not prove an architecture universally good. If a category
has no supported finding, say so rather than inventing a good or bad practice.

### Successor compiler migration recipe

List the semantic/IR capabilities needed by this optimization and map each to
an interface rather than an old opcode spelling. Identify portable algorithm or
analysis code, compiler-specific glue, target constraints, correctness tests and
calibration parameters. Explain what can be reused directly, what needs adaptation,
and the smallest current inspection or experiment needed to decide applicability.
Preserve links to counterexamples and known limitations.

## Accumulating and consuming experience

Update the index after each implemented attempt, linking related or contradictory
findings. When enough rounds motivate a redesign, compare the records to identify
repeated enabling properties and obstacles. Cite supporting attempts and retain
counterexamples; do not promote an untested suggestion to a proven design rule.
Use [compiler-design-retrospective](../../compiler-design-retrospective/SKILL.md)
when the human requests this synthesis. Link its lesson ids back to the source
records in the index; a retrospective is not required after every optimization.

Use these lessons to choose successor IR/data structures and plan pass ports.
Prior evidence can eliminate repeated diagnosis and broad profiling when current
applicability is established. Recheck legality and results on the successor;
measure there before claiming a speedup. Reprofile only when evidence is missing,
the representation changes the mechanism or observed behavior contradicts it.
Existing records supplied by the human may be consulted across projects; keep
provenance links and write new records in the current project without modifying
source-project history or creating a shared service.
Use [compiler-pass-porting](../../compiler-pass-porting/SKILL.md) for a requested
port, placing the applicability map and port outcome in a new destination record.
