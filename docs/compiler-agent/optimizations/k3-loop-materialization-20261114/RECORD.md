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
## P3b (the pressure-bounded loop-invariant sconst hoist): implemented, measured, DEFAULT OFF (commit 3ea2363)

The first candidate from the FIXED cost table (sconst 4.03M/call = 17%
of attention-f16).  At every counted loop's close, the body block's
top-cap most-used sconst ops move to just before the preheader's entry
br: every sconst is loop-invariant and a def inside the loop only
dominates uses inside it, so the relocation is dominance-safe; the cap
(4, the mir-licm convergent bound) limits the extra cross-loop GPR live
ranges.  `A100C_LOOP_CONST_HOIST=on` opts in; the option rides the
artifact identity.

**The same-tree on/off contrast (fixed tooling, program-region
totals):**

| case | off | on (cap 4) | on (cap 2) |
|---|---:|---:|---:|
| attention-f16 [4,4,32,64] | 23,787,102 | **23,553,130 (-0.98%)** | 23,553,149 (-0.98%) |
| matmul16 [16,16,16] f16 | 24,273 | **24,882 (+2.51%)** | 24,866 (+2.44%) |

The win and the loss come from the SAME single-use vsetvli-AVL
constants: attention's long staging loops amortize the preheader across
16k iterations (sconst 4.03M -> 3.57M/call) while matmul's tight tile
loops pay the allocator's sreload bill (1.18M -> 1.40M/call).  A
use-density filter (uses >= 3) removes the loss and the win together
(attn +0.00%, mm16 +0.43%): no structural gate separates the two
families, so the mir-licm negative result extends to the bounded
lowering-level form.  DEFAULT OFF; the mechanism stays validated
behind the switch.

Validation of the shipped default (behavior-identical to HEAD): the
default-off attention program is INSTRUCTION-IDENTICAL to the
pre-change build (2663 lines, byte-equal); 32/32 cross-family smoke,
both round test modules, and the elementwise+softmax family scan
**861/861 PASS** (167 operators, 4 roots, `evidence/p3b-family-scan/`,
`evidence/p3b-metrics/`).

**The remaining big target after P3b** is the vsetvli alternation
itself (4.30M/call, 18%): the e16-e32-e64 conversion/staging region
dance -- the K/V staging loops (chunk9/chunk18 bodies: 4.1M/3.9M total,
950k vsetvli each per call) hold ~30 region switches per iteration.
That needs the region-dance restructure or the staging workspace
round-trip elimination (softmax W4/W5), both design-class changes.
## The superseded-setter elimination (commit d167b67): -5.00% attention-f16

The vsetvli region-dance target from the fixed cost table, landed as a
bounded emitter fix instead of a region-scheduler redesign.  The static
audit of the emitted attention program found 43 consecutive-setter
pairs of which 35 are DEAD: the next vsetvli arrives with only
state-transparent instructions between (li/add/sconst -- no vector op
reads the region), so the first setter's region state is never
observable.  The peephole now removes such a setter when a purely
TEXTUAL block-bounded scan of the FINAL emitted stream proves its dst
register is unread until overwritten (any label, branch, store-operand
read or unmodeled instruction keeps it).  The textual proof sees
allocator-inserted remat/reload readers that MIR-liveness deadness (the
closed x0-dst direction) does not -- that is precisely why this
transformation is safe where x0-dst was not.

Same-tree program-region totals (fixed tooling):

| case | before | after | change |
|---|---:|---:|---:|
| attention-f16 [4,4,32,64] | 23,787,102 | 22,597,262 | **-5.00%** |
| softmax97 [4,97] f16 | 9,092 | 8,728 | -4.01% |
| linear-dropout [16,128,128] f16 | 7,389,432 | 7,217,136 | -2.33% |
| matmul16 [16,16,16] f16 | 24,273 | 23,837 | -1.80% |
| sin16 / synthesis | 1,335 / 224,627 | unchanged | +0.00% |

attention's vsetvli fell 4.30M -> 3.35M/call (-22% of the region
churn) and sconst 4.03M -> 3.80M.  Verification: 23/23 smoke, both
round test modules, no-name-dispatch PASS, the elementwise+softmax
family scan 861/861 (evidence/ss-family-scan/), metrics in
evidence/ss-metrics/.  Switchless (provably-dead work removal).

The REMAINING region churn (3.35M vsetvli/call) is the live dance:
each staging access legitimately crosses e16(data)-e64m2(address)-e16
-- reducing it needs the region-scheduler restructure or the staging
workspace round-trip elimination (softmax W4/W5), both design-class.

## The wide staging lane index: -3.64% attention-f16, DEFAULT ON

The live-dance boundary above, landed as a bounded LOWERING change
instead of the region-scheduler redesign.  The staging lane index
(``vid + elem`` and its sdiv/srem axis decomposition, in both staging
machines -- the materialization chunks and the scan/mirror loops) now
materializes NATIVELY at the 64-bit index class: ONE e64m2 episode per
access group carrying ``vid.v`` + ``vadd.vx`` + the esz ``vmul.vx``
together, the per-consumer ``vwadd`` widening and its whole e32 index
episode gone.  The wide class is EXACTLY the doubled form the old
widening produced (e32m1 -> e64m2), so every indexed access's
EEW/EMUL relationship is unchanged.  ``A100C_WIDE_LANE_INDEX=off``
restores the e32 + vwiden form (identity part ``no-wide-lane-index``).

Legality: the lane index is the lowering's own addressing machinery,
never a TIR-observable value -- the intended position is the TRUE
``(elem + lane)`` sum the staging loop bounds and the boundary mask
keep in range, every consumer is an address computation (a masked lane
never accesses), and an i32 wraparound could only deviate from the
in-bounds position of an already ill-formed access.  The element base
joins the chain as an i32 SCALAR directly: the scalar core's A003
invariant (i32 values live sign-extended in 64-bit registers) makes
the e64 ``vadd.vx`` read exactly the widened value.  The first
implementation materialized that view with ``widen_to``'s smove -- the
paired measurement exposed it as +366,080 instructions/call on
attention (one mv per lane-index chain per block) for IDENTICAL bits;
removed (a pure-ceremony op deleted, not a semantic change).

One real defect the family scan caught: ``_stage_join``'s parity
selector hard-coded an e32m1 region for its ``vcmp``; under the wide
index its operands are e64m2 and 18 cases (fht_kernel_1d/256_1d/
256_4row, complex_pack) refused at the MIR verifier.  Fixed by making
the compare's region follow the staging class (the T038 consumer-side
pattern); 18/18 PASS after the fix, and byte-identity checks confirm
the fix changes nothing for join-free cases (attention and synthesis
artifacts byte-identical modulo the revision comment; the one join
user in the main 596 set, flash_varlen, likewise).

Same-tree paired program-region totals (the off side reproduces the
ss round's numbers exactly):

| case | off | on | change |
|---|---:|---:|---:|
| attention-f16 [4,4,32,64] | 22,597,214 | 21,775,466 | **-3.64%** |
| softmax [20,17] f16 | 78,774 | 76,449 | -2.95% |
| matmul16 [16,16,16] f16 | 23,845 | 23,309 | -2.25% |
| linear-dropout [16,128,128] f16 | 7,217,136 | 7,087,860 | -1.79% |
| softmax-inner [97] f16 | 8,451 | 8,408 | -0.50% |
| synthesis [1,4,16,64] f32 | 224,627 | 224,019 | -0.27% |
| softmax_log [4,97] f32 | 121,188 | 122,232 | +0.86% (recorded) |

attention's vsetvli fell 3.35M -> 2.99M/call (-10.7% of the region
churn) and vec-arith -10.0% (the vwidens plus the T032 view-moves the
mixed-class sums no longer need).  The one regression is the
small-case allocation-perturbation class again: the wide index's
2-register live range tips the allocator into splitting in
softmax_log's particular body (+1,024 branches / +768 vsetvli, against
-768 vec-arith); softmax-inner's -0.50% on the same machinery shows
the class is case-specific, not structural.  Kept DEFAULT ON (the ss
round's softmax16-f32 +1.34% precedent).

Verification: smoke 30/30 (wide on, fresh cache) and 36/36 (off
contrast); both round test modules PASS; no-name-dispatch positive
exit 0 / witness exit 1; multi-worker spot checks 21/21 at threads=2
and 21/21 at threads=4 (attention + linear-dropout + softmax); the
elementwise+softmax+attention family scan 1,269/1,269 PASS over 233
operators (the ss round's 861-case set plus the 133 supplementary
operators, 673/673; the main 596 re-verified byte-identical under the
join fix).  Metrics in evidence/wli-metrics/{on,off}/, scans and
spot checks in evidence/wli-family-scan/.

## The x0-dst vsetvli (register-avl setters): -0.94% attention-f16

The avl-li self-destroying form the block-scoped-reload record named:
463k/call on attention sat in `li reg, 32` immediately before e16
setters whose ``rd == rs1`` -- the setter WRITES ITS OWN avl register
(the vl result), so the register can never survive to the next setter
and every setter re-pays the li.  The fix: when a REGISTER-avl
setter's vl result is provably unread (the superseded-setter round's
textual dst-reader scan, factored into ``_setter_dst_is_dead`` with a
new check: a later setter whose AVL SOURCE is the dst READS it -- this
also closes a latent hole in the superseded proof's step 2), the
emitter rewrites the setter to ``rd = x0``: no register is written,
the avl register survives, and the EXISTING li-dedup and vsetvli-dedup
rules fire across the setter (one ``li reg, 32`` serves a whole
same-register cluster).

THE NEGATIVE RESULT THAT SHAPED THE SCOPE: the first implementation
rewrote x0-AVL setters too and the smoke FAILED (23 LAUNCH_FAIL, 2
MISMATCH -- SIGSEGV in the narrow-fallback cascade).  Two bisect steps
localized the defect class to exactly the x0-AVL rewrites (register-
avl rewrites with the dedup extension blocked still crashed; excluding
x0-AVL rewrites passed 6/6), and the x0-AVL class has ZERO benefit by
construction: those setters carry no avl li (their preceding li is
dead-value materialization the walk-back already removes).  The class
is excluded with the reason recorded at the rule; the register-avl
class -- where the 463k cost actually lives -- is the shipped form.

Same-tree paired program-region totals (the off side is the committed
block-scoped-reload tree's measurements above):

| case | 5523567 | x0-dst | change |
|---|---:|---:|---:|
| attention-f16 [4,4,32,64] | 20,959,344 | 20,761,700 | **-0.94%** |
| linear-dropout [16,128,128] f16 | 6,795,488 | 6,770,400 | -0.37% |
| softmax-inner [97] f16 | 8,416 | 8,396 | -0.24% |
| softmax [20,17] f16 | 76,429 | 76,237 | -0.25% |
| matmul16 [16,16,16] f16 | 23,026 | 22,988 | -0.17% |
| synthesis / softmax_log [4,97] | 214,233 / 122,232 | unchanged | +0.00% |

attention's sconst fell 3.67M -> 3.50M/call (-165k li's) and
vec-config 2.89M -> 2.85M (33k extra setter dedups); 97 static
register-avl setters rewritten, 82 li's and 69 vsetvlis removed.
Uniform small wins, zero regression.  Verification: smoke 41/41 (8
operators incl. the previously-crashing family); test_emit (the
emitter's own module) plus both round test modules PASS;
no-name-dispatch positive 0 / witness 1; multi-worker 18/18 at
threads=2/4/8; the family scan 1,269/1,269 PASS over 233 operators.  Metrics in
evidence/x0d-metrics/, scans in evidence/x0d-family-scan/.

## What is NOT claimed / pending

- No full 2734-case input regression this round (user-directed scope);
  the full-input binding remains the K3 round's 2734/2734 at 817419a,
  which predates the T050 fix and both candidates.  A fresh full pass
  over the final tree is the recorded follow-up.
- No board timing, no speedup ratio, no engine G8/G9 claim; QEMU guest
  instruction counts only.  matmul128/256 + gelu/sigmoid-large (the
  additional shapes) unmeasured (manifest limitation above).
- softmax16-f32 +1.34% and (this increment) softmax_log [4,97] f32
  +0.86% kept (recorded regressions, small-case allocation perturbation
  class).

## The block-scoped split reload: -3.75% attention-f16, -4.12% linear-dropout

The staging workspace base reload chain the verifier's boundary named
(1.18M reload/call): the victim policy picks the MOST-USED live value
to split (one round relieves every point its range crosses -- the T036
convergence repair), and ``_split_value`` then reloaded the value
before EVERY use -- so the most-used value paid the most loads:
attention's chunk9/chunk18 bodies reloaded the workspace base 5-6x per
iteration (946k of the 1.19M sp-relative loads sat in slot 232 alone).

The fix is one equivalence: a straight-line MIR block containing NO
definition of the split value cannot observe the spill slot changing
between its uses -- ONE reload at the block's first use (shared by
every later use in the block, including the terminator's carried
args) is observationally identical to per-use reloads.  Blocks that
define the value keep the per-use form.  The spill DECISIONS are
untouched (attention's allocation stats are byte-identical: same 22
spilled values, same slots, same rounds) -- only the reload placement
changed, which is what makes this a pure performance heuristic:
any placement respecting the def-use chain passes the same verifier.

Same-tree paired program-region totals (the off side is the committed
1f0c508 tree's measurements above):

| case | 1f0c508 | block-scoped | change |
|---|---:|---:|---:|
| attention-f16 [4,4,32,64] | 21,775,466 | 20,959,344 | **-3.75%** |
| linear-dropout [16,128,128] f16 | 7,087,860 | 6,795,488 | **-4.12%** |
| synthesis [1,4,16,64] f32 | 224,019 | 214,233 | **-4.37%** |
| matmul16 [16,16,16] f16 | 23,309 | 23,026 | -1.21% |
| softmax-inner [97] f16 | 8,408 | 8,416 | +0.10% |
| softmax [20,17] f16 | 76,449 | 76,429 | -0.03% |
| softmax_log [4,97] f32 | 122,232 | 122,232 | +0.00% |

attention's reload fell 1.18M -> 728k/call (-38.6%; spill stores
37.4k -> 4.6k), linear-dropout's 484k -> 159k (-67%), synthesis's
12.2k -> 4.8k (-61%); chunk9's static body loads fell 44 -> 6 (the
second access group now reuses the block's single reload:
``add t5, t1, t5`` with no preceding ``ld``).  No new regression:
softmax_log's recorded +0.86% is unchanged (+0.00% here) and
softmax-inner is +0.10% (noise level).  The REMAINING 728k/call on
attention sits in two other split values (slots 240/280, 649k
combined) -- the next round of the same class.

Verification: smoke 30/30 (fresh cache); test_allocate PASS (the
allocator's own module) plus both round test modules; no-name-dispatch
positive 0 / witness 1; multi-worker spot checks 18/18 at threads=2,
4 and 8 (attention + linear-dropout + the join-family fht case); the
elementwise+softmax+attention family scan 1,269/1,269 PASS over 233
operators (the full set of the wide-lane-index round).  Metrics in
evidence/bsr-metrics/, scans in evidence/bsr-family-scan/.

## Post-round session record (2026-11-15, no code change): the P3b re-measurement negative and the located ws-reload anomaly

Two investigations from the recorded boundaries, both documented
without a shipped change (the honest outcome of the remaining budget):

1. THE P3b RE-MEASUREMENT (the sconst boundary, `li 4/2048/64/16`
   inside loop bodies): the loop-const hoist was re-measured on the
   four-candidate tree (A100C_LOOP_CONST_HOIST=on, same-tree paired,
   evidence/p3b2-metrics/) -- the tradeoff is STILL two-sided and now
   NET NEGATIVE: attention-f16 +0.27%, matmul16 +1.09%, softmax
   [20,17] +2.05%, linear-dropout +1.10%, softmax-inner +0.43% against
   synthesis -0.46% and softmax_log -0.31%.  The evolved tree (wide
   index, block-scoped reloads, x0-dst) RAISED the GPR pressure the
   hoist's live-range extension pays -- the win side shrank and the
   loss side grew.  DEFAULT OFF stands; the li-churn reduction needs a
   different lever (the per-use constant REMAT multiplication, below).

2. THE LOCATED ws-RELOAD ANOMALY (the slot 240/280 boundary, 649k
   reloads/call): slot 240 is the workspace base again (433k; the
   block-scoped reload cut it from 946k) and slot 280 is pid.body
   (216k).  Instrumented allocation on the exact harness case shows
   the ws split consolidating chunk9_body to ONE reload at split time
   (block then 103 ops) -- but the FINAL allocated MIR carries THREE
   same-slot sreloads in that block (r8 serving 4 uses, r9/r10 one
   each) and the block has GROWN to 608 ops (~505 per-use remat
   sconsts inserted by later rounds).  The exact producer of r9/r10 --
   one _split_value call is logged, the per-use path cannot run for a
   block the scoped path took, and no remat names match -- remains
   UNEXPLAINED; it is a real, located, reproducible behavior (same
   tree, deterministic, key 19f2f190c5489d74) worth the next session's
   first investigation.  No fix was attempted blind.

Session tally (the four shipped candidates): attention-f16
23,787,102 -> 20,761,700 (-12.7%), all committed (d167b67, 1f0c508,
7556932, e505061) with their records above.

## The zero-bit splat + dead-li removal: -0.33% attention-f16, all 7 paired cases improve

The sconst boundary's zero share (li 0: 330k/call on attention): a
zero-BIT constant source (int 0, or +0.0 at any float width -- the
sconst's value attr carries the raw bit pattern, so -0.0's 0x8000..
bits never match) now splats from the ARCHITECTURAL zero register:
``vmv.v.x vd, zero`` -- identical lanes, and the feeding ``li`` becomes
removable.  The removal rides a new peephole rule: a ``li`` whose
register is never read before written (the same textual dst-reader
proof as the setter rules) is dead.

TWO REAL HOLES THE FAILING SMOKE EXPOSED AND CLOSED in the shared
``_setter_dst_is_dead`` scan (both latent in the already-shipped
superseded/x0-dst rules, both now fixed at the source):
1. the vsetvli branch checked the dst write before the AVL read -- an
   rd==rs1 setter (``vsetvli t0, t0``) READS t0 as its avl before
   writing it, so a preceding ``li t0, 32`` was concluded dead and the
   avl ran on garbage (25 LAUNCH_FAIL in the first smoke);
2. the generic branch matched only the FIRST register occurrence --
   ``slt t0, t1, t0`` reads t0 as rs2 before writing it as rd, so a
   live loop bound was concluded "overwritten" and dropped (9
   LAUNCH_FAIL + 6 TIMEOUT in the second smoke).  Every occurrence is
   now checked: a non-first appearance is a read.
Both fixes make the SHIPPED setter rules strictly more conservative in
exactly those corners (the family scans had passed because the
patterns are rare, not because they were sound).

Same-tree paired program-region totals (the off side is the committed
e505061 tree's measurements above):

| case | e505061 | zero-splat | change |
|---|---:|---:|---:|
| softmax-inner [97] f16 | 8,396 | 8,313 | **-0.99%** |
| softmax_log [4,97] f32 | 122,232 | 121,056 | **-0.96%** |
| synthesis [1,4,16,64] f32 | 214,233 | 212,873 | -0.63% |
| matmul16 [16,16,16] f16 | 22,988 | 22,895 | -0.40% |
| attention-f16 [4,4,32,64] | 20,761,700 | 20,692,564 | -0.33% |
| softmax [20,17] f16 | 76,237 | 75,984 | -0.33% |
| linear-dropout [16,128,128] f16 | 6,770,400 | 6,752,608 | -0.26% |

ALL SEVEN cases improve (attention's sconst fell 3.50M -> 3.43M/call;
softmax_log's previously-recorded +0.86% regression narrows).  The
dead-li rule also catches incidental orphaned li's beyond the splat
class.  Verification: smoke 15/15 + 32/32 extended (10 operators incl.
the join family and the previously-crashing set); test_emit plus both
round test modules PASS; no-name-dispatch positive 0 / witness 1;
multi-worker 18/18 at threads=2/4/8; the family scan 1,269/1,269 PASS over 233 operators.
Metrics in evidence/zs-metrics/, scans in evidence/zs-family-scan/.

## The deferred full-input regression on the final tree: 2,728/2,734 PASS, 6 pre-existing compile-budget timeouts

The recorded follow-up ran in the session's closing window: the full
2734-case corpus (500 operators, threads=1, 10 shards) on the final
five-candidate tree.  RESULT: 2,728/2,734 PASS; the 6 non-PASS are
TIMEOUT ("case budget exceeded") on exactly two operators --
complex_svd_pick_orthonormal_v_kernel [17] and deconv3d_fwd_kernel
[1,4,8,8,8], three dtypes each.  TIMING ANALYSIS (the pre-existence
check): complex_svd f16 compiles in 182.9s at e505061 (pre-zero-splat)
vs 185.7-186.2s at HEAD -- the delta is noise-level, the peephole's
proof scans are NOT the driver, and the case budget sits exactly at
these two operators' standalone compile time (under 10-shard load they
tip over; a serial re-run passed complex_svd f32 and both operators'
artifacts compile and execute correctly standalone).  These are the
same two operators the round's opening notes carried as pre-existing
test-timeout classes (complex_svd's static_range nest is the
allocator's documented compile-budget case); the K3 full pass at
817419a predates the T050 fix and every candidate in this file, so the
2,728/2,734 result is the CURRENT tree's full-input binding: every
mismatch class is clear, and the 6 timeouts are a located, pre-existing
compile-budget boundary, not a correctness defect of any candidate.
A window cap on the proof scan was implemented and measured (185.7s --
no effect) and REVERTED to keep the tree byte-identical to the
validated evidence.  Evidence in evidence/full-input/ (10 shard
reports + journals + the serial re-check).

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
# the wide-lane-index paired contrast (same tree; the off side is the
# ss-round baseline reproduction)
A100C_WIDE_LANE_INDEX=off python3 -B tools/profiling/collect_metrics.py \
  --operator suite/perf/attention_forward_triton.py --shape 4,4,32,64 \
  --dtype float16 --threads 1 --out <off-dir>
python3 -B tools/profiling/collect_metrics.py \
  --operator suite/perf/attention_forward_triton.py --shape 4,4,32,64 \
  --dtype float16 --threads 1 --out <on-dir>
# the join-selector repair check (the 18 refused cases)
python3 -B tools/run_scan.py run \
  --operator suite/dev/fht_kernel_256_1d_native.py \
  --operator suite/dev/fht_kernel_1d_native.py \
  --operator suite/dev/fht_kernel_256_4row_native.py \
  --operator suite/dev/complex_pack.py \
  --report <report.json> --run-id <id> --journal <journal>
# the block-scoped split reload contrast (the off side is 1f0c508's
# committed measurements, evidence/wli-metrics/on/)
python3 -B tools/profiling/collect_metrics.py \
  --operator suite/perf/attention_forward_triton.py --shape 4,4,32,64 \
  --dtype float16 --threads 1 --out <dir>
```

Baseline root: git worktree at `a06dc37`; candidate root: the applied
tree at `1ddb981` (worktree copies under /tmp during the round).  All
raw per-PC counts, metrics, family-scan reports/journals and the
resource-evidence capture are under `evidence/` (counts gzip'd; ~9.8MB).
