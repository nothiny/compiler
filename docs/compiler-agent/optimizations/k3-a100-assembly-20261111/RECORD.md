# K3 A100 assembly optimization record

Completed within the user's QEMU-only assembly implementation scope. Production
source is committed at `51f3c61` (compiler digest `92fa8b4b706f0a76`). The original
full input independently executes and compares **2734/2734 PASS**: dev 2192,
perf 542. This direct human-guided record does not change engine acceptance
policy or assert G8/G9.

## Changes and controls

Implemented neutral reduction-domain trimming, kept-axis SIMD sums, two-row matrix
B reuse/pointer recurrences, guarded narrow load/stores and pressure-aware
elementwise width. Structural guards retain general paths; the five
`A100C_KEPT_AXIS_REDUCTION`, `A100C_NEUTRAL_REDUCTION_TRIM`,
`A100C_MATRIX_ROW_REUSE`, `A100C_GUARDED_NARROW_ACCESS` and
`A100C_ELEMENTWISE_WIDTH` controls accept `off` and enter artifact identity.
No operator-name dispatch, reference fallback, tolerance change or extra IR was
introduced. BF16 matrix operations retain FP32 vector fallback; BF16 IME remains
unverified under the recorded QEMU format-control gap.

Prerequisites close old chunks before geometry changes, preserve complete vector
register groups at runtime/zero AVL, retain observable VL setter results, and
close source/header/SDK cache dependencies. The inherited T044 test was
independently rerun and preserved in `efba263`; it is not the original worker's
report and does not settle stale engine task state.

## Current paired evidence

Baseline Git `c8ade47` is freshly compiled from a frozen copy. Its historical
full report had 2732 PASS and two staging timeouts; that incomplete baseline is
not relabeled as a full PASS. Final pairs use the final production source,
identical cases/seed 30/one worker and two independent repeat-difference pairs.
All 84 final profile launches pass original comparison and repeat consistency;
program bytes, ELF SHA and actual module import/source hashes are checked.
Numbers below are generated-program guest instruction reductions, not board
speedups or complete-call hardware timings. Runtime/process counts stay separate.

| Samples | Change from baseline |
|---|---:|
| Original matmul 16³ and 8×32×24, FP32 | −38.18% to −38.23% |
| Same original matmul, FP16 IME | −34.38% to −34.42% |
| Same original matmul, BF16 vector | −47.54% to −47.58% |
| Original attention [4,4,32,64], three dtypes | −57.58% to −63.04% |
| Original softmax [4,97], three dtypes | −85.62% to −86.18% |
| Original softmax [4,16], three dtypes | −95.61% to −95.99% |
| Additional GELU/sigmoid [262144] FP32 | −50.42% / −50.84% |
| Additional matmul 256³ FP16 IME | −39.08% |

`validation/FINAL_PAIRED_METRICS.json` and `.csv` retain 21 rows: 15 original
shape/dtype samples and six additional shapes. Additional shapes do not increase
original-input coverage. The 14 core rows preserve phase-1 costs: FP16
IME/GELU/sigmoid initially had zero gain. Narrow accesses and adaptive width
complete the same five-category user scope, without opening another round or
substituting historical gains. Actual FP16 IME counts remain 16/4096 for 16³/128³
while surrounding instructions decrease.

## Full validation and limits

`validation/full-input-final/report.json` strictly merges four complete-operator
shards, each with a fresh independent cache/runtime build directory. There are
2734 unique original IDs, no missing/duplicate/extra cases, and every PASS has
compiled/executed/compared flags. Raw shard reports, journals, commands and actual
import bindings remain available. `FINAL_EVIDENCE_AUDIT.json` verifies all 183
copied files against frozen/shared sources and all 690 bound compiler,
transport, comparator and corpus inputs against the prepared plan.

Both previous large deconv timeouts now actually compile, execute and compare
PASS: FP16 596.068s, BF16 614.707s, each with zero reported absolute output error.
Native timeout is 600s and the separate staging deadline 905s. This is evidence
under a larger budget, not a compiler latency improvement. All original SVD
cases pass; the unsafe earlier broadcast-view/flat-alias prototype was not imported.

The full-run FP16 representative binds listing/execution/ELF SHA and 4096 dynamic
`smt.vfwmadot` executions to the compared artifact. Two of four configured workers
have positive native work counters; two are idle. Their identical start/end
values are the process collection window, not independently measured worker
active intervals. They prove neither timing overlap nor physical K3 placement.
Host validation sharding is not single-operator multi-core performance evidence.

Independent final standalone checks are in `backend/final-verification/`:
22 scripts exit zero after a missing prepared matrix-count plugin fixture is
restored; the initial infrastructure failure remains recorded. Advisory limits
are preserved: the masked-tail mutant corrupts its guard but its CLI returns
zero; the stage-barrier-removal witness is vacuous in both current and baseline
tests. Neither counts as a successful witness. No hardware timing, topology or
complete physical K3 compatibility is asserted by this QEMU-only work.

## Implementation lessons

- Reuse actual CFG liveness and indexed EEW/EMUL demand, including mask/v0.
  Bigger LMUL is not automatically profitable: GELU factor four exceeds the
  budget; factor two improves the measured sample.
- Native alias guards compare backing-storage bases, not different view data
  pointers. Runtime N/alias decisions preserve same-ELF small/large/small reuse.
- Complete source discovery and native header/SDK dependencies prevent stale
  artifacts. Header mutation is checked through actual native exit codes.
- Whole-register spills preserve bytes and VL/VTYPE without assuming full VL.
  Configuration elimination must also preserve live VL results.
- Actual module imports, program bytes and artifact SHA establish provenance.
  Old symlink-collector records retain a caveat and separately identified hard-copy
  reruns. A process collection window is not a per-worker timing observation.

`validation/REPLAY.md` provides replay commands. The 25.71MB
`METRICS_RAW_TEXT_EVIDENCE.tar.gz` preserves raw counter/log/program/MIR text with
per-member SHA indexing, excluding bundles, ELF binaries and object files.
