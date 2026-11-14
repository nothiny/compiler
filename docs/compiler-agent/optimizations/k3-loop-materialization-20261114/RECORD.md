# K3 loop-body materialization/region round + guarded sinf/cosf polynomials

Two candidates landed in one direct human-guided round at commit `1ddb981`
(on `a06dc37`, the T050-verification revision).  Criterion throughout: the
declared proxy metric -- per-call guest dynamic instructions under the
calibrated QEMU plugin (`tools/profiling/`), 1 compute worker, seed 30 --
never QEMU wall-clock, never a board speedup claim, no engine gate/G9.
Verification scope is the user-directed reduced scope of 2026-11-14
("少做全量扫描，只需要保证优化的算子的正确性即可"): the optimized
operator families, not a full 2734-case pass; the last full-input binding
remains the K3 assembly round's 2734/2734 at `817419a` (pre-T050 fix).

## Target selection (from the current ELF)

The K3-final profiles re-measured on the current tree (attention-f16
30.88M/call) decompose as **const-materialization 27-40% + vec-config
12-16% of every call**; the hottest chunk body of attention-f16 was 173
MIR ops of which 59 sconst + 37 vsetvli + 8 vid + 8 s2v (34%+ pure
materialization).  The emitter's OPT-VLI dedup only removed consecutive
same-config setters (6 of 37); the remaining 31 are the e16-e32-e64
conversion dance.  Separately, sinf/cosf still rode the per-element libm
loop (19 corpus identities).

## Candidate 1: block-scoped materialization + region overhead

- `a100c/lower/vectorize.py` (Context): per-block caches -- one sconst
  per (value, type), one lane-index chain (vid + the chunk's element
  base) per (index type, vl, element), one splat per (bits, type, active
  region) -- and exact vsetvli deduplication at the emission chokepoint:
  a request matching the active region's (sew, lmul, avl) returns the
  establishing setter's vl result (identical config and avl give an
  identical vl).  The avl's constant value is resolved through the const
  cache, so differently-created avls of one value dedup too.  The old
  fragmented tracking (`_note_region`'s `(sew, lmul, None)`) is what
  made `_vregion`/`_open_region` pre-checks miss.
- `a100c/backend/emit.py` (switchless, provably equivalent -- the
  OPT-VLI class): the x0 AVL form for avl >= VLMAX (`vsetvli rd, x0`
  sets exactly the same vl), in `op_text` and the spill-restore path,
  plus the dead-li peephole rule (a `li` immediately above an x0-form
  vsetvli whose dst it feeds is dead: the vsetvli reads no AVL register
  and overwrites the dst).
- Rollback: `A100C_LOCAL_MATERIALIZATION=off` (lowering caches + chokepoint
  dedup; identity-isolated), git revert for the switchless emitter part.

Control (`evidence/base-to-off-diff-control.py`): with the switch OFF the
emitted instruction stream differs from the `a06dc37` baseline by EXACTLY
231 `vsetvli rd, <reg>` -> `vsetvli rd, x0` rewrites and 183 removed
`li` lines -- zero other differences.

### Paired measurement (baseline a06dc37 vs materialization candidate)

| case | baseline | candidate | change |
|---|---:|---:|---:|
| attention [4,4,32,64] bf16 | 38,749,809 | 30,353,522 | **-21.67%** |
| attention [4,4,32,64] f16 | 30,882,417 | 24,556,658 | **-20.48%** |
| attention [4,4,32,64] f32 | 19,039,848 | 15,258,707 | **-19.86%** |
| matmul-tail [8,32,24] bf16 | 62,431 | 53,027 | -15.06% |
| matmul-tail [8,32,24] f16 | 53,110 | 43,360 | -18.36% |
| matmul-tail [8,32,24] f32 | 49,033 | 42,937 | -12.43% |
| matmul16 [16,16,16] bf16 | 34,661 | 29,938 | -13.63% |
| matmul16 [16,16,16] f16 | 29,866 | 25,263 | -15.41% |
| matmul16 [16,16,16] f32 | 28,159 | 25,142 | -10.71% |
| softmax97 [4,97] bf16 | 11,407 | 10,164 | -10.90% |
| softmax97 [4,97] f16 | 10,679 | 9,518 | -10.87% |
| softmax97 [4,97] f32 | 10,579 | 9,892 | -6.49% |
| softmax16 [4,16] bf16 | 5,121 | 4,975 | -2.85% |
| softmax16 [4,16] f16 | 5,102 | 4,805 | -5.83% |
| softmax16 [4,16] f32 | 4,697 | 4,760 | **+1.34% (recorded)** |

The one regression: softmax16-f32 +63 instructions (a 4.7k-call;
allocation perturbation class, recorded not hidden).  matmul128/256 and
gelu/sigmoid-large (the K3 round's additional shapes) have no
manifest-declared case and `collect_metrics` only enumerates manifest
cases -- not measured this round (recorded limitation).

## Candidate 2 (P7): guarded sinf/cosf vector polynomials

`sinf`/`cosf` join `_VMATH_POLY_FNS` at SEW 32: rint(x*2/pi) via the
1.5*2^23 magic, the 3-way Cody-Waite reduction (11-bit terms; q*term
exact in fp32 for |q| < 2^13), one Horner pair in z=r*r, the quadrant
pick and the sign flip through the i32 view.  **The whole-op domain
guard** |x| < 1024 branches the op to the polynomial or the per-element
libm path -- a structural guard with a correct fallback (the fp32-only
reduction's ~ulp(|x|)/2 error stays bounded; nothing outside the guard
ever reads a polynomial value; fp64 sin/cos and every other width keep
vmath).  Coefficients and the exact-op-sequence f32 simulation
(`evidence/sincos_fit.py`, union grid + banded |x| statistics): max
|err| 1.8e-7 for |x| < 4, 4.8e-7 for |x| < 16 (the corpus
distributions), 3.05e-5 at the cap -- the corpus tolerances (atol >=
1e-4) hold with >= 50x margin.

### P7-isolated contrast (same tree, A100C_VMATH_LIBM=1 as the off side)

| case | libm | polynomial | change |
|---|---:|---:|---:|
| synthesis [1,4,16,64] f32 (cos+exp+log) | 917,047 | 244,259 | **-73.4%** |
| cosine_compute [128] f32 | 9,401 | 2,783 | **-70.4%** |
| sin_kernel [16] f32 | 1,715 | 1,335 | -22.2% |
| blackman [122] f32 | 32,474 | 32,292 | -0.6% (no change; the call's cost is its staging, not the math) |

## Verification (the user-directed reduced scope)

- `a100c/tests/test_local_materialization.py`: 11 checks PASS (MIR
  effect: the hottest body's sconst 202 -> 62, vid 12 -> 8, vsetvli
  128 -> 119, zero adjacent duplicate setters; x0 forms 231, zero
  surviving dead feeding li; ON/OFF execution identical at 1 and 2
  workers; ragged tails PASS; the region-on-hit witness REPRODUCES the
  first revision's verifier rejection).  One control honestly VACUOUS:
  the avl-blind dedup witness found no same-(sew,lmul)-different-avl
  pair inside one block on the probed cases (recorded; the avl
  component stays as the exactness condition `_vregion` already
  requires).
- `a100c/tests/test_vmath_sincos.py`: ALL checks PASS (the corpus
  sin/cos operators at 1 and 2 workers; the domain guard with mixed
  1e6/1e30 magnitudes riding the fallback; the switch contrast -- the
  rint magic's bit pattern only in the polynomial build, both builds
  keep the fallback arm, both compare PASS; the guard-stripped witness
  compares WRONG on far-out-of-range lanes; fp64 sin untouched).
- Family regression on the materialization candidate, 4 independent
  hardlink roots (`evidence/famscan-shard{0..3}.json`): **596/596 PASS**
  over the matmul (74 operators) + softmax (33) + attention (3)
  families, threads=1.  Shard 0 ran with `--resource-evidence`: the
  fp16 representative (matmul_k32_fast [128] float16) records
  `smt.vfwmadot: 4096` at 1, 2, 4 and 8 workers bound to the same
  run/case/artifact (`evidence/resource-evidence/`; the representative
  rule's current set has no int8 candidate -- no plain-form int8 dot
  operator exists in the corpus, the T050 round's recorded state).
- sin/cos operator smoke on the stacked tree: 33/33 PASS (8 operators).
  Final-tree spot check (attention + softmax_single_block + matmul):
  21/21 PASS (`evidence/final-spotcheck.json`).
- `tools/check_no_name_dispatch.py`: import scan + behavioral
  name-generality PASS (alpha/beta probes emit identical bodies).  The
  `--witness` run was terminated by its 300s bound before verdict --
  rerun with a longer bound is pending (recorded, not claimed).
- Full a100c test suite at the final tree: 56/59 modules exit 0.
  `test_compile_sweep` (the full-corpus compile sweep) and
  `test_t039_repairs` time out at their bounds -- BOTH pre-existing
  (T044's suite evidence records the same exit=124 pair on Nov 8).
  `test_rng` timing out is NEW at this revision (it passed inside 550s
  at T044 time) and is NOT caused by this round: its first timeout in
  the suite run happened at 10:47, before the candidates were applied
  to the tree (12:00).  An isolated rerun showed the test's Python
  process ballooning past 360 GB RSS within ~4 CPU-minutes (a runaway
  allocation in the test's compile path at the current baseline) and
  was killed to protect the machine.  Recorded as a surfaced
  pre-existing defect for the repair track; the philox bit-exactness
  contracts themselves are unchanged by this round (no RNG path was
  touched).

## What is NOT claimed / pending

- No full 2734-case input regression this round (user-directed scope);
  the full-input binding remains the K3 round's 2734/2734 at 817419a,
  which predates the T050 fix and both candidates.  A fresh full pass
  over the final tree is the recorded follow-up.
- No board timing, no speedup ratio, no engine G8/G9 claim; QEMU guest
  instruction counts only.  matmul128/256 + gelu/sigmoid-large (the
  additional shapes) unmeasured (manifest limitation above).
- softmax16-f32 +1.34% kept (recorded regression, small-case allocation
  perturbation class).

## Replay

```bash
set -a; . ./.env; set +a
# the paired materialization measurement (baseline tree at a06dc37)
python3 -B tools/profiling/collect_metrics.py \
  --operator suite/perf/attention_forward_triton.py --shape 4,4,32,64 \
  --dtype float16 --threads 1 --out <dir>
# the P7 contrast on the final tree
A100C_VMATH_LIBM=1 python3 -B tools/profiling/collect_metrics.py \
  --operator suite/dev/synthesis_kernel.py --shape 1,4,16,64 \
  --dtype float32 --threads 1 --out <dir>
# the round's tests
python3 -B a100c/tests/test_local_materialization.py
python3 -B a100c/tests/test_vmath_sincos.py
# the family regression (one shard form)
python3 -B tools/run_scan.py run --operator <op...> \
  --report <report.json> --run-id <id> --journal <journal>
```

Baseline root: git worktree at `a06dc37`; candidate root: the applied
tree at `1ddb981` (worktree copies under /tmp during the round).  All
raw per-PC counts, metrics, family-scan reports/journals and the
resource-evidence capture are under `evidence/` (counts gzip'd; ~9.8MB).
