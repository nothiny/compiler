---
name: develop-optimization-pass
description: >-
  Develop or improve ONE compiler optimization in this project (a100c): locate a
  real, measured opportunity, write its rule contract before implementing, place
  it in the right layer (pass, lowering, backend, emitter), implement it with a
  behavior switch and traceable counters, validate positive/negative/regression
  evidence, and record it for reuse. Use for any pass-development or
  pass-improvement task under human direction.
---

# develop-optimization-pass

The focused skill for building one optimization inside this repository's
compiler (`a100c/`). It is the middle layer of the optimization skill family:

- [optimization](../optimization/SKILL.md) owns the human-guided lifecycle and
  when optimization is allowed at all;
- [profile-to-compiler-pass](../profile-to-compiler-pass/SKILL.md) owns turning
  fresh profiles into a recommendation;
- **this skill** owns the development loop once a candidate direction exists:
  rule contract → implementation → validation → record;
- [compiler-pass-porting](../compiler-pass-porting/SKILL.md) reuses a recorded
  optimization on a new compiler or IR revision.

Load the references you need, not all of them at once:

- [the rule contract](references/rule-contract.md) — the seven fields every
  rewrite rule must state before implementation, and how each field is *proven*
  (not asserted) in this repo;
- [repo interfaces](references/repo-interfaces.md) — the concrete commands for
  compiling, dumping IR/asm, censusing emitted forms, collecting the paired
  dynamic-instruction metric, running correctness checks and writing records;
- [case library](references/case-library.md) — the distilled, reusable
  techniques and lessons from the recorded rounds in
  `docs/compiler-agent/optimizations/` (query it before designing anything).

## The loop

1. **Locate a real opportunity.** Never start from a transform you want to
   apply; start from a measured or directly observable cost: a metrics origin
   class from `tools/profiling/`, a static census of the emitted forms, or a
   recorded open lead in the round INDEX. Check the case library first: the
   backend may already do it, or a prior round may have measured it net
   negative (a closed lead stays closed until its recorded reason changes).
2. **Write the rule contract first.** Every rewrite you will implement gets
   the seven fields of [the rule contract](references/rule-contract.md) —
   match pattern, legality, transform, profitability, refusal conditions,
   analysis dependencies, placement — written down and reviewed *before* code.
   If a field cannot be stated concretely, the candidate is not ready.
3. **Choose the layer by evidence, not preference.** Existing pass config →
   reusable new pass → lowering → backend selection/allocation → emitter
   peephole. The emitter peephole is legitimate only for costs created at or
   after allocation (e.g. the physical-register form); a cost visible in MIR
   belongs upstream. State why the chosen layer is the first one that can see
   the pattern. Architecture-contract changes (new IR ops, new pipeline stages,
   new declared passes) require the recorded DesignIssue route and fresh
   independent review — see AGENTS.md; do not slip them in as "implementation".
4. **Implement with the established controls.** One behavior switch
   (`A100C_<NAME>=off`, plumbed through `CompileOptions` into
   `identity_part()`), match-position annotations in the emitted stream,
   fired/declined counters in the artifact stats, and tests beside the other
   round tests. No operator/kernel/benchmark-name branching anywhere
   (`tools/check_no_name_dispatch.py --witness` must fail).
5. **Validate the contract, then the corpus.** Positive cases (the rewrite
   fires and the form is as specified), refusal cases (each declined condition
   keeps the original form), boundary/multi-use/shape variants, the stage
   verifiers, the four witness checks, the family scan, then the full-input
   regression. Numeric policy never changes; tolerances and references are read
   from the case. A failed check is evidence, not an obstacle: fix the rule or
   record the refusal.
6. **Measure paired, same tree.** Baseline (or switch-off) vs switch-on under
   the same identity rules, using the recorded paired-case set plus any case
   the census says the new rule accepts or declines interestingly. Report
   regressions as regressions. The proxy metric (guest dynamic instructions
   per call) is the judge; QEMU wall time is auxiliary; no board-speedup claim
   without board evidence.
7. **Record and feed back.** Write the record under
   `docs/compiler-agent/optimizations/` in the established format and update
   `INDEX.md`. Anything the round taught about *how to develop* rules (a new
   proof hole, a new census form, a reusable legality argument) goes back into
   this skill's references — that is what makes the next round cheaper.

## Hard rules

- Correctness is load-bearing: the full-input regression runs at the candidate
  revision with the new rule enabled; a scoped family scan alone does not close
  a round.
- A rewrite that fires zero times on the corpus is still delivered if its
  machinery is validated and the zero is measured and explained (the store-half
  precedent) — but say exactly that; do not let it ride as an unmeasured
  "improvement".
- Declined is a first-class outcome: each refusal condition must be observable
  (counter or annotation), so a future round can widen it deliberately.
- Never present a plan, a scaffold, or a generated artifact as a done
  optimization. Executed-and-compared or not done.
