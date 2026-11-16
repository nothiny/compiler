# Case library: distilled knowledge from the recorded rounds

Query `docs/compiler-agent/optimizations/INDEX.md` first — every recorded round
links its transformation, the structure it matched, and its measured outcome.
Before designing a rule, check whether your idea (or its cost class) already
has a record: an accepted record shows the technique and its validation chain;
a negative record (P3b hoisting, the mir-licm blanket hoist, the store half's
zero accepts) is a closed lead that stays closed until its recorded reason
changes. This file distills the reusable techniques; the records carry the
full evidence.

## Measurement facts (how costs are actually distributed)

- Per-call guest dynamic instructions are 85-95% compiler-generated scaffolding
  in the measured families; real vector/IME compute is 5-10% (UNIFIED-OPTIMIZATION-
  PLAN §1.1). Scaffolding classes move as the rounds land — always re-measure.
- Costs created *during or after lowering* (loop-body rematerialization, region
  churn, allocation traffic, emission forms) are invisible to every TIR pass
  (TIR LICM fired=0 on the corpus). Fixing them in TIR is a category error;
  the layers that can see them are lowering, allocation, selection and the
  emitter.
- The QEMU proxy metric counts instructions, not cycles: a same-count rewrite
  (e.g. multiply→shift) shows 0% here even when real silicon benefits. Say so
  explicitly when it applies; board timing needs the board pack, not QEMU.

## Techniques that worked (with their records)

- **Branch-control simplification at emission** (branch-fuse round): bare
  brc-stub trampolines retargeted with a CB-range guard, and MIR-single-use
  compares fused into their branch — the loop-head control sequence fell
  from three instructions to one; -1.6..-4.45% total on every paired case.
  The proof lesson: use the representation's exact def-use (operands + edge
  args), not a textual read census, when the allocator recycles registers.
- **Compile-time structural predicates over proven conjuncts** (guard
  predicate, OPT-2026-11-14): when each conjunct of a property (contiguity,
  alignment, unit coefficient) is structurally provable, replace a runtime
  proof + branch + slow path with the direct form. Decline classes are
  measured, not guessed (4,459 small-divisor sites keep the runtime guard —
  correctly).
- **Block-scoped caches at the emission chokepoint** (loop-materialization
  round): per-block sconst/lane-index/splat caches and exact vsetvli dedup in
  the emitter's Context — sees what TIR/MIR passes cannot.
- **Textual dst-reader proofs** (superseded-setter, dead-li, x0-dst rounds):
  physical-register death on the final stream; conservative bias; the two
  fixed holes (see rule-contract.md) are the reason the helpers look paranoid.
- **Emitter peepholes with counters + annotations** (`[peephole-*]` comments,
  removed-line counts in the stream header): match positions and refusal
  counts stay inspectable in every shipped artifact.
- **IME B-operand staging pack** (matmul round): per-element copy loops → one
  strided vector load per staged column; structural (uniform stride, guarded
  count), family-wide effect.
- **Vector polynomial math** (vmath rounds): per-(fn, sew) structural dispatch
  replacing per-element libm calls, with a libm rollback switch.

## Techniques that failed, and why (do not retry unchanged)

- **Blanket loop-invariant hoisting at MIR** (mir-licm, DESIGN-ISSUE-mir-
  optimize): register-pressure perturbation outweighs per-iteration savings
  (softmax -2.5% but log_softmax_linear +8.1%); unbounded hoisting is a
  compile-time convergence bomb (the allocator rematerializes one value per
  spill round, 64-round cap). The stage stays unwired. The loop analysis
  machinery in `a100c/passes/mir_optimize.py` is reusable.
- **Capped hoisting (P3b)**: a cap of 4 keeps convergence but shrinks wins to
  noise; measured net negative twice. Pressure-aware design (live-range
  accounting, or only multi-use constants) is the recorded open direction.
- **The store half of the guard predicate**: validated machinery, measured
  zero corpus accepts — the corpus's contiguous staging manifests on the load
  side only. Kept wired; the zero is recorded, not hidden.

## Process lessons with numbers attached

- The paired off/on contrast on the same tree is the primary evidence; the
  off side's emission should be byte-identical to the baseline on unchanged
  paths. Compile-cache identity (switches in the key) makes this automatic.
- **Measure the marginal, not the mechanism** (loop-rotation round,
  measured): the rotation removes 94.7k jumps/call on attention and still
  nets +0.04% — an equally real +120k move perturbation from the
  allocator's recoloring of the changed CFG. A pass's profitability field
  must carry the measured NET and the default must follow it (opt-in),
  or a structural argument ships a wash as a win.
- **A transform that creates a first-of-its-kind CFG shape audits its own
  analysis** (loop-rotation round): the rotation's self-loops exposed a
  latent bug in the natural-loop construction (the textbook predecessor
  walk must not run when a back edge's source equals its target, or the
  loop's external entry is swallowed). Re-derive analysis invariants on
  the new shape, in tests.
- **One placement decision can block two optimizations** (loop-rotation
  round): the allocator's before-branch reload placement both cost a load
  per hot iteration AND sat between every compare and its branch — moving
  the reload into the consuming edge fixed the count and unblocked the
  compare+branch fusion in one change. Placement questions deserve the
  same structural scrutiny as count questions.
- A transform's accept class across the family scan (e.g. 52/990 programs)
  is how you learn what a rule *actually* matches; measure it before claiming
  generality.
- **A peephole's own asymptotics are part of its correctness envelope**
  (branch-fuse round, measured): the scan's per-case budget sits AT the
  heaviest identities' compile time (chunk_gdn2 [17] ≈ 164s at HEAD), so an
  O(branches × lines) stream pass (+25s on the biggest function) is a
  full-input regression even when every emitted instruction is right — two
  budget-marginal cases went TIMEOUT until the pass became single-pass.
  Time the heaviest identity before and after any new stream-scanning rule.
- The steady-state instruction difference on the smallest paired cases
  carries a ±~1% run-to-run envelope (softmax-inner moved -0.19% then
  +0.96% across two collections with its own off side moving 8,349→8,321);
  report such cases as within noise, not as wins or regressions, and lean
  on the structural category deltas and the census form.
- The allocator interacts with everything: any rule that changes live-range
  shape can shift coloring decisions — measure the paired set, watch the
  spill/reload counters, and record allocation-perturbation regressions
  honestly (softmax_log +0.86% and +2.05% classes exist in the records).
- Known open leads at the last round's close: the allocator's
  stability/coalescing under CFG-shape changes (the rotation's opt-in
  blocker: attention +101k mv on a -94.7k j win), the ~649k/call reload
  boundary on attention (an unexplained allocator behavior post-split),
  the operator_entry skeleton (10-15%, unattributed), and the structural
  sconst mass (li 4 / li 2048 classes — measured as having no algebraic
  lever).
