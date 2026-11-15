# The rule contract

Every rewrite rule is written down with these seven fields **before** it is
implemented. The contract is the unit of review, the unit of recording, and the
unit of reuse: a rule is widened, narrowed or retired by editing its contract,
never by silently changing code behavior. Keep the filled contract in the
round's RECORD.md under "Transformation and reuse contract".

## The seven fields

1. **Match pattern** — the structural shape the rule recognizes, expressed in
   IR/representation terms (opcodes, operand shapes, region state, block form),
   never in operator/kernel/benchmark names or file paths. State the
   representation it matches in (`tir/v1`, `mir/v1`, the emitted stream) and
   give one real before-example from a compiled artifact.
2. **Legality conditions** — the semantic facts that must hold and *why* they
   preserve behavior: dominance, dead-value proofs, memory semantics, mask
   defaults, wrap/overflow policy, zero-trip safety, region invariants. Each
   condition names its proof mechanism in this repo (MIR verifier, TIR
   verifier, textual dst-reader proof, structural predicate, runtime guard).
   A condition without a proof mechanism is a hypothesis, not a condition.
3. **Transform** — exactly what the matched form becomes, with one
   after-example. If the transform has degrees of freedom (cap, order, layout),
   state how they are chosen and bounded.
4. **Profitability** — when the rewrite is worth applying. "Always profitable
   when legality holds" is acceptable only for pure instruction removal with
   no pressure/layout side effects; anything that can perturb register
   allocation, block layout or cache identity needs a measured or bounded
   argument, and a refusal when the argument does not hold.
5. **Refusal conditions** — the complement of 2+4: every shape where the rule
   declines and keeps the original form. Refusals must be *observable*
   (a declined counter with the unmet condition, or an annotation), because a
   later round widens a rule by attacking a recorded refusal, not a silent one.
6. **Analysis dependencies** — which analyses/facts the rule consumes, and
   which it invalidates for later consumers. At the emitter (post-allocation)
   and in single-pass textual peepholes, say so explicitly: they consume the
   final stream and invalidate nothing upstream, but they also cannot rely on
   anything upstream that the stream does not show.
7. **Placement** — the pipeline position (which IR, which stage, before/after
   which consumers) and *why that is the first position that can see the
   pattern*. If an earlier stage could match it, the later placement needs a
   reason (e.g. the value only exists after allocation).

## Proof mechanisms available in this repo

- **TIR/MIR structural verifier** (`a100c/ir/tir.py`, `a100c/ir/mir.py`): both
  run in the pipeline after every mutating stage; a rewrite that breaks the
  contract fails the build loudly. Use for type/shape/region/operand legality.
- **Textual dst-reader proof** (the emitter peepholes in
  `a100c/backend/emit.py`): proves a physical register is unread after a point
  by scanning the final emitted stream. Two known holes, both already fixed in
  the helpers — do not reintroduce them:
  - a later `vsetvli rd, rd_avl, ...` *reads* its rd as AVL before writing it
    (the avl-read-before-dst-write order);
  - `slt t0, t1, t0` reads t0 as rs2 *before* writing it as rd — every
    occurrence of the register must be checked, not only the first position.
  Conservative bias is the design: an overestimate blocks an elimination; an
  underestimate is a miscompile. Whole-function scans (a register read nowhere
  in the entire remaining stream) are sound without path sensitivity.
  **Known over-conservatism** (branch-fuse round): a textual read census is
  the wrong proof for a value whose physical register the allocator recycles
  for later values — reads of *other* values in the same register block every
  rewrite even when the value itself is single-use. When the representation's
  exact def-use is at hand (MIR operands + br/brc edge args), use it instead
  of proving death on the stream.
- **Regex over dot-prefixed symbols** (branch-fuse round): a `\b` word
  boundary never matches immediately before a leading dot, so
  `\b\.Llabel\b` finds nothing — a label-reference count silently becomes 0
  and every candidate declines. Use a symbol-boundary lookaround
  (`(?<![\w.])symbol(?![\w.])`) for `.L`-style symbols.
- **Accept/declined counters as the first smoke test** (branch-fuse round):
  the counters exposed an all-declined bug (the regex above) in one compile;
  ship the counters with the rule and read them before any execution test.
- **Compile-time structural predicates** (see the guard-predicate case): a
  predicate over representation facts whose conjuncts are each proven
  structurally; when it holds, a stronger direct form replaces a runtime proof.
- **Behavior switches** (`A100C_<NAME>=off` through `CompileOptions` into
  `identity_part()`): the rollback path and the A/B measurement control; the
  off-form must be byte-comparable to the pre-rule emission for the same input.
- **Witness checks** (`tools/check_*.py --witness`): each injects a defect and
  must fail. A rule that changes masked memory, synchronization or numeric
  policy needs its witness exercised at the candidate revision.

## Worked example (filled contract, abridged)

> **Rule: bare brc-stub elimination** — *match*: emitted
> `bne cond, zero, .LbrcN_true` where the stub block `.LbrcN_true:` contains
> exactly one instruction `j T` and nothing else (the brc's true-edge argument
> moves were empty). *legality*: the stub is a pure trampoline — control that
> reaches it continues to T with no state change; retargeting the branch and
> deleting the stub preserves every path. Extra guard: the retargeted
> conditional branch must stay within the ±4 KiB CB-format range, checked
> conservatively (≤4 bytes per emitted instruction between branch and target);
  the stub label must have no other referents. *transform*: branch target
> becomes T; the two stub lines become an annotated comment. *profitability*:
> removes one unconditional jump per dynamic execution of the branch's taken
> edge — pure removal, no allocation/layout perturbation. *refusal*: stubs
> carrying argument moves; out-of-range targets; multiply-referenced labels.
> *analysis*: consumes the final stream post-allocation; invalidates nothing.
> *placement*: emitter peephole — the stub exists only because the emitter
> places per-edge argument moves after the branch, so no earlier stage can see
> it.

Fill all seven at this concreteness level. If you cannot, the candidate is a
diagnosis task, not an implementation task.
