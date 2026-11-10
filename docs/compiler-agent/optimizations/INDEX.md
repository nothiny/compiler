# Optimization records index

One record per optimization attempt, linked by transformation, IR
structure, lesson and outcome (the optimization-record guide's layout).
Evidence roots are absolute under this project.

## Records

| id | record | transformation | IR/structure | outcome |
|---|---|---|---|---|
| OPT-2026-11-10-MATMUL-BPACK | [matmul/candidates/vector-pack/RECORD.md](matmul/candidates/vector-pack/RECORD.md) | IME B-operand staging pack: per-element scalar copy loops → one strided vector load (vlse) + unit store per staged column; runtime-AVL region; scalar fallback + `A100C_MATRIX_PACK=scalar` switch in the artifact identity | matrix lowering's pack loops (MIR blocks pb/pq); uniform byte stride + guarded count; pre-zeroed contiguous staging | accepted (kept): matmul family 312/312 PASS; per-call dynamic instructions -30.6%..-79.1% on IME-path cases, 0.0% change elsewhere; reload traffic -67..-85% |
| OPT-2026-11-10-EMIT-PEEPHOLE (prior round, commit 0f84bdc) | commit message of 0f84bdc (no separate record was written; noted here for discoverability) | emitter peephole: within-block vsetvli elimination (AVL-constant comparison) + li dedup | emitted asm straight-line blocks | accepted: ~-10% static instructions; superseded scope: dynamic loop-body costs remained (see the matmul round's B2 bottleneck) |

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
  retrospective).
