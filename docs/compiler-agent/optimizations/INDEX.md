# Optimization records index

One record per optimization attempt, linked by transformation, IR
structure, lesson and outcome (the optimization-record guide's layout).
Evidence roots are absolute under this project.

## Records

| id | record | transformation | IR/structure | outcome |
|---|---|---|---|---|
| OPT-2026-11-10-MATMUL-BPACK | [matmul/candidates/vector-pack/RECORD.md](matmul/candidates/vector-pack/RECORD.md) | IME B-operand staging pack: per-element scalar copy loops → one strided vector load (vlse) + unit store per staged column; runtime-AVL region; scalar fallback + `A100C_MATRIX_PACK=scalar` switch in the artifact identity | matrix lowering's pack loops (MIR blocks pb/pq); uniform byte stride + guarded count; pre-zeroed contiguous staging | accepted (kept): matmul family 312/312 PASS; per-call dynamic instructions -30.6%..-79.1% on IME-path cases, 0.0% change elsewhere; reload traffic -67..-85% |
| OPT-2026-11-10-EMIT-PEEPHOLE (prior round, commit 0f84bdc) | commit message of 0f84bdc (no separate record was written; noted here for discoverability) | emitter peephole: within-block vsetvli elimination (AVL-constant comparison) + li dedup | emitted asm straight-line blocks | accepted: ~-10% static instructions; superseded scope: dynamic loop-body costs remained (see the matmul round's B2 bottleneck) |
| OPT-2026-11-10-ELEMENTWISE-VMATH-POLY | [elementwise/candidates/vector-poly/DESIGN.md](elementwise/candidates/vector-poly/DESIGN.md) | fp32 vmath vector-polynomial path (exp/exp2/log/log2/erf/floor) replacing the per-element libm-call loop; per-(fn,sew) structural dispatch in `_vector_math_unary`; `A100C_VMATH_LIBM=1` rollback switch into the artifact identity | lowering-level fix in a100c/lower/vectorize.py (no new MIR pass; emit.py untouched); host-validated f32 op-sequence simulation with fitted coefficients | designed + numerically validated, **not yet implemented** (user implements); baseline 683/683 PASS at 4217b79; expected -93..-97% dynamic instructions on transcendental cases |
| OPT-2026-11-10-UNIFIED-ROUND | [unified-round/ROUND.md](unified-round/ROUND.md) | the executed round: W1 vmath vector-polynomial (softmax -76.8% / elementwise -87.8% median), W2-P1/P1b matmul full-tile peels (flagship -84.6% vs the round's original baseline), the W3 mir-licm negative result (unwired, analysis module kept), W2-C8 strided narrow forms (~0 on profiled cases, kept) + the prerequisite emission-peephole vl fix | lowering (vectorize.py exp dispatch), matrix.py peels, emit.py peephole fix; criterion: per-call guest dynamic instructions | executed at 9dd0bc8; family scans softmax 146/146 + elementwise 683/683; full-input regression pending/attached; known spill-class regressions recorded (linear-dropout +9.1%, naive_attn +13.7%) |
| OPT-2026-11-10-UNIFIED-PLAN | [UNIFIED-OPTIMIZATION-PLAN.md](UNIFIED-OPTIMIZATION-PLAN.md) | cross-family consolidation of the four family rounds (matmul P0-P8 / attention C1-C8 / softmax W1-W6 + candidate #1 / elementwise vector-poly) into one deduplicated sequence: W1 unified vmath vector-polynomial (merging the three overlapping designs into one lowering-local implementation, single `A100C_VMATH_LIBM` switch), W2 lowering/allocator-local fixes (pack-b peel, A-staging peel, narrow-data vectorization, loop-depth-aware reload), W3 mir-optimize stage via DesignIssue -> contract revision -> independent review, W4 conditional follow-ups | plan only (not an attempt): no compiler code changed, engine state untouched; criterion stays the proxy metric (per-call guest dynamic instructions, calibrated QEMU plugin) with correctness_only acceptance preserved | plan; implementation awaits user instruction and re-anchors all baselines at the then-current HEAD (T044 repair wave in flight) |

## Related evidence roots

- `matmul/baseline/` — scope, correctness scan (312/312), profile artifacts
  (PROFILE_MANIFEST / BOTTLENECKS / OPTIMIZATION_RECOMMENDATION), metric
  sweeps (16 cases t1 + 3 cases 1/2/4/8) with per-loop-nest attribution.
- `matmul/tooling/` — the round's observability chain (QEMU plugin,
  manifest join, collectors, calibration + emulator probes) and its docs.
- `matmul/candidates/vector-pack/` — the accepted candidate: scan, metrics,
  comparison, record.
- `matmul/regression/full-input/` — the full-input regression at the
  candidate revision.
- `matmul/retrospective.md` — cross-round synthesis (compiler-design-
  retrospective; covers this round + the prior emission-peephole round,
  lesson ids L1-L8).
- `elementwise/baseline/` — the elementwise round's correctness precondition
  (134 operators / 683 cases PASS at 4217b79) and baseline metrics (13
  representative cases, guest dynamic instructions per call) plus the vmath
  census; `elementwise/tooling/` — the f32 polynomial coefficient derivation
  and strict-simulation validation script; `elementwise/candidates/
  vector-poly/DESIGN.md` — the designed (not yet implemented) candidate:
  fp32 vmath vector-polynomial path with per-case-tolerance verification
  plan and an A100C_VMATH_LIBM rollback switch.
