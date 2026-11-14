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
  name-generality PASS (alpha/beta probes emit identical bodies), and
  the `--witness` run FAILS as it must (exit 1, locating the injected
  operator-file literal at `a100c/backend/select.py:138`) -- the check
  is load-bearing at this revision.
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

## Increment (52b9ded): address-chain block CSE

The candidate profile's remaining decomposition (attention-f16 24.56M:
op:sadd 2.11M + scale multiplies + ws reloads) showed every workspace
staging access rebuilding `base = ws + record-offset` and the e64
widen-and-scale chain -- the load and store paths of one record each
built their own copy.  Under the same switch and the same block-scoped
Context caches: one record base per (workspace reg, offset) and one
scaled index per (index reg, esz, vl) per block.

| case | 1ddb981 | 52b9ded | change |
|---|---:|---:|---:|
| attention [4,4,32,64] f16 | 24,556,658 | 23,787,142 | -3.13% |
| matmul16 [16,16,16] f16 | 25,263 | 24,257 | -3.98% |
| softmax97 [4,97] f16 | 9,518 | 9,555 | +0.39% (recorded) |

Both round test modules stay green (execution-match ON/OFF identical at
1 and 2 workers, both witnesses unchanged); attention + softmax +
matmul spot scans 27/27 PASS after the increment
(`evidence/addrcse-metrics/`).

## Post-round re-measurements (the recorded follow-ups, resolved or scoped)

**The unified round's W1 spill regressions are gone** (re-measured at
52b9ded, same protocol; the const/materialization caches are in effect
the pressure-aware sharing that round called for):

| case | pre-W1 (4217b79) | unified round end | current (52b9ded) |
|---|---:|---:|---:|
| linear-dropout-f16 [16,128,128] | 15,326,685 | +9.1% | 7,390,024 (**-51.8%**) |
| log-softmax-linear-f16 [17,33] | 2,072,263 | +2.9% | 1,010,936 (**-51.2%**) |
| naive_attn-f16 [2,17,4,8,16,13] | ~920,000 | +13.7% | 318,899 (**~ -65%**) |

**The runtime dispatch floor, attributed** (attention-f16 at 52b9ded):
the runtime region's `operator_entry` is 1,048,064 instructions per call
(4.4% of 23.79M; `main` 198k, loader 55k) -- material on the smallest
cases (~600 ops of a ~2.2k call), minor on large ones.  The cheap part
(the whole-image byte loops) was taken by the unified round; what
remains is the pool dispatch itself (wake/handoff), a shared surface
with diminishing returns -- recorded, not pursued.

**P2 (prefix mask -> exact vl), scoped but not landed.**  The P1 clamp
bounds the chunk LOOP (`upper = min(live, B)`); the final PARTIAL chunk
still executes at the static plan vl and NEEDS its mask, so "drop the
mask machinery inside clamped bodies" is only valid for FULL chunks.
The correct shape is either (a) a full-chunk loop with the UNMASKED
body over `[0, (live/vl)*vl)` plus one masked tail chunk (the body
lowered twice), or (b) a per-chunk dynamic avl `min(vl, live - elem)`
carried as a register through every region setter (the avl leaves the
sconst domain; ~25 emission sites).  Both are day-class changes.  MEASURED (52b9ded, sin_kernel [16]'s
chunk body): the mask machinery is 6 of 30 instructions (20% of the
body; per masked access ~4-5 ops -- two v0 pins, the .t access, the
vmerge, the amortized mask compute -- plus the count popcount), so the
expected saving for the masked-elementwise class is 15-20% of the
chunk-body cost.
the win is the per-access pin + masked-access + merge (~4 vector ops
per masked memory op per chunk) across the corpus's commonest pattern
(`i < n` masks).  Recorded as the next round's primary candidate.

**Elementwise pointer recurrence, scoped.**  The (non-staged) view
load/store path still rebuilds a 6-op scalar address chain per access
per chunk (`base + (elem + block_start) * esz`: the sin_kernel body's
mv/mv/add/li/mul/add).  The affine-in-elem address is the
matrix-row-reuse pattern applied to the chunk loop: carry one pointer
per view as a loop param (`p += vl*esz` at the back edge; the loop
already carries merge params).  The clamp analysis already walks every
statement, so the view set is collectable at `_ensure_chunk` time.
Recorded as the second next candidate.

## Negative result (attempted, reverted): the x0-destination vsetvli

Hypothesis: a vsetvli whose vl result is dead could write x0 instead of
its allocated register, preserving its own AVL register so one li serves
every same-AVL setter in a block (the per-setter rematerialized `li`
the dst==avl clobber forces).  The emitted-text change (MIR identical)
broke 14 of 17 smoke cases (MISMATCH from element 0 + one SIGSEGV:
matmul/attention wrong, sin_kernel unaffected) -- some dst registers of
MIR-dead vsetvli results are still load-bearing at runtime, most
plausibly through allocator-INSERTED code (the T029 remat / T032
reload class) or the emitter's li/vl-state expectations, neither of
which the op-indexed `_live_after_at` liveness sees.  Reverted the same
hour.  Two follow-up experiments narrowed it further: (a) disabling the
peephole's li-dedup entirely (fresh compile, cache-voided -- the first
attempt of this experiment silently hit the broken artifact's cache
because the peephole switch is not in the cache key) still mismatches,
exonerating the li tracking; (b) restricting the rewrite to
non-block-end vsetvlis (the block-end/edge-move class) still
mismatches 14/15.  The emitted-text delta is exactly the 120 dst
rewrites, the MIR is unchanged, no vsetvli result rid is used anywhere
in the allocated MIR, and an emitter-op trace found only three
dst-register "reads" that all turned out to be artifacts of the branch
edge's parallel moves (not MIR ops).  The mechanism stays unidentified:
something at runtime reads those vl values or depends on the register
write in a way invisible to both the MIR-level liveness and the traced
op stream (the spill/restore machinery's vsetvli x0,x0 region dance is
the remaining suspect class).  Bisect pairs preserved under
a100c/cache/: 970a8e53... (pre) vs 21d1106c.../0620280a.../7e5442520c8e
(the three broken variants).  The idea stays attractive (~1 li per
region setter) but is CLOSED for this line until the spill-restore
interplay is traced; any restart should begin from the trace, not from
the text diff.

**Closed permanently (the empirical bisect).**  An op-index-parity
bisect (the A100C_X0DST_MASK harness: rewrite only setters whose op
index has bit k = v) ran all four half-subsets -- EVERY 60-rewrite
subset mismatches all three matmul [16,16,16] cases.  A single bad
setter cannot explain that: the deadness premise is systemically
unsound at runtime for this kernel class, in a way three sessions of
analysis (MIR-unchanged text diffs, rid-liveness, emitter op traces,
li-dedup and block-end eliminations) could not isolate.  Direction
closed; the bisect harness and the four broken artifacts remain
reproducible for any future revisit.
## P2 (the full/tail chunk-body split): implemented, fully validated, DEFAULT OFF

The scoped design landed: when the ELEMENTWISE clamp owns the chunk loop
(mask_vid present; the neutral trim never splits) and the region is
straight-line (no nested If/Loop -- the first revision's igamma
regression: a replayed branchy body doubles the register demand and the
emission ran out of scratch for a cyclic branch-edge move, a located
refusal), the loop splits at `full_end = upper & -vl` into a full-chunk
loop whose body lowers the region statements with the shared prefix
mask bypassed (a full chunk's mask is provably all-true) plus ONE masked
tail chunk -- the tail REPLAYS the same statement list with the bypass
off (state snapshotted/restored around the replay; the items accounting
mirrors today's exactly, decided by the same statements' count-register
behavior).  `A100C_CHUNK_MASK_SPLIT=on` enables it; the default is OFF.

**The honest measurement flipped the default.**  The per-body saving is
real (sin16's body: 30 -> 27 instructions, the pin/.t/merge/count chain
gone; the compare stays for its non-memory consumers), but the manifest
geometry is 1 chunk per program (grid = cdiv(n, BLOCK)): the split's
~4-op per-program overhead (the head's full_end/sand/slt + the tail
head's retest) exceeds the 3-5-op per-chunk saving, and the same-tree
on/off contrast measures **+0.3%..+1.5% on the tiny masked cases, 0.0%
on the mid ones** (sin16 1327->1331, sin19 1599->1623, cos128
2783->2815, cos103 2525->2537, smx97/cos/sells 0.0%; the first
amax17-on reading of -15.8% was a NOISE-CLASS OUTLIER -- the on/off
artifacts are byte-identical programs (1218 instructions, zero diff)
and the re-measure gives on=1170.2 vs off=1178.6, inside the +-0.7%
band).  The split only wins on multi-chunk-per-program shapes (the
clamp's original motivation: a small-n instance of a large-BLOCK
kernel), which the manifest does not carry.  Per the round's rule --
no reproduced benefit on the observable surface, no default ship -- the
mechanism stays behind the switch with the geometry finding recorded.

Validation of the ON path (the shipped-off mechanism is still fully
exercised): the 54-case cross-family smoke (attention/matmul/softmax/
sin/cos/blackman/synthesis/igamma/linear_dropout) 54/54 PASS; both round
test modules ALL PASS; the elementwise+softmax family scan (167
operators, 4 independent roots, the switch ON) **861/861 PASS**,
0 non-PASS (`evidence/p2-family-scan/`, `evidence/p2-contrast-metrics/`).

## Program-region re-verification (the measurement lesson, 2026-11-15)

The round's criterion table used PER-CALL totals; the tiny cases' totals
carry the invariant ~500-600-op runtime dispatch floor plus a +-10-25%
RUNTIME-region noise band (identical programs measured 1069 vs 1327 on
sin16; amax17 985 vs 1170).  The PROGRAM-REGION counts are deterministic
and re-verify every headline claim STRONGER:

| case | baseline | candidate | program-region change |
|---|---:|---:|---:|
| attention [4,4,32,64] bf16/f16/f32 | 37.2M/29.6M/17.7M | 28.9M/23.3M/14.0M | **-21.3 .. -22.2%** |
| matmul16 [16,16,16] bf16/f16/f32 | 26.6k/22.1k/19.1k | 21.9k/17.3k/16.1k | **-15.8 .. -21.9%** |
| matmul-tail [8,32,24] bf16/f16/f32 | 53.1k/44.2k/38.2k | 43.8k/34.5k/32.1k | **-15.8 .. -21.9%** |
| softmax97 [4,97] bf16/f16/f32 | 6.9k/6.2k/5.1k | 5.7k/5.1k/4.3k | **-14.0 .. -18.9%** |
| softmax16 [4,16] bf16/f16/f32 | 2.0k/1.8k/1.5k | 1.7k/1.5k/1.3k | **-13.1 .. -17.2%** |

The recorded softmax16-f32 "+1.34% regression" was runtime noise: its
program region improved **-13.05%**.  Future small-case comparisons read
the program-region field, not the per-call total.
## The profiling pc->MIR join repair (2026-11-15, commit e3b9365)

Target selection from the joined tables found a contradiction: the
tables reported vslidedn=1.31M/vextract=1.30M per call for attention
while the RAW per-pc plugin counts contain ZERO vslidedown.vi and
vmv.x.s=149,505 -- the narrow-data GUARDED path takes its fast arm
every time (the K/V per-lane walk never execute; C8's residual is
already covered).  The join (insn_manifest.py) keyed pcs by DUMP
POSITION, but op.index is neither positional (the allocator inserts
~500 index=-1 ops after select.py's renumber) nor unique (build
history repeats indices).  Every pre-fix origin/opcode table from
collect_metrics is therefore unreliable; per-call totals and raw
per-pc counts were always correct (all measured claims in this round
used those and stand).

Fixed three ways (dump '; op=<index>' annotation; the post-allocation
renumber + identity-based selection re-key in BOTH the driver and the
factory pipeline -- the factory is the path A100_COMPILER_FACTORY
actually runs; the manifest resolves by the true index).  A/B: the
emitted instruction stream is identical (only .Lbrc label numbers
change); 17/17 smoke, both test modules, no-name-dispatch PASS; the
FIXED table matches the raw counts EXACTLY (vextract==vmv.x.s==
149,505/call, s2v==vmv.v.x==950,785, vslidedn absent on both sides).

**The REAL attention-f16 cost structure (per call, fixed tooling):**
vsetvli 4.30M (18%), sconst 4.03M (17%), sadd 2.13M, vbinx 1.65M,
sreload 1.18M, brc 0.98M, s2v 0.95M, br 0.77M, vid 0.76M.  The next
round's targets, in order: the vsetvli e16-e32-e64 alternation (the
staging/convert region dance), loop-invariant sconst hoisting (the
mir-licm lesson applies -- pressure-bounded only), and the sreload
class.  The x0-dst direction is closed (see the negative-result
section); P2 is validated and default-off (see its section).
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
