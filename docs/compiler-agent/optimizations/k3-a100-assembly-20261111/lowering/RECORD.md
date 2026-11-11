# Layout-aware native lowering for K3 A100

This batch ports three bounded mechanisms from the read-only exploration
snapshot `fc3ccea383db5f55` onto the compiler that began at `c8ade47`.
It preserves the current TIR/MIR architecture and the original corpus,
references and comparison policies. See [APPLICABILITY.md](APPLICABILITY.md).
No engine performance gate or real-board result is asserted.

The source mechanisms are documented in
`/tmp/a100-readonly-review-b-te2m9tiu/exploration/READ_ONLY_OPTIMIZATION_REPORT.txt`;
the source prototype files remain unchanged. The destination implementations
are ordinary lowering methods, without prototype monkeypatches.

## Changes

* **Independent kept-axis sums:** contiguous reduced axes followed by a
  contiguous kept suffix use FP32 SIMD lanes for independent outputs. Each
  lane visits reduction positions in the same increasing order as the old
  scalar walk. The input products, conversions and rounding boundaries stay
  before the reduction. A suffix-dividing width prevents cross-boundary
  loads. Inner addresses advance by the suffix stride; unsupported types,
  index forms and noncontiguous axes retain the scalar implementation.
* **Neutral-domain trimming:** existing P1 only handles single-pass
  elementwise functions. The new reduction proof requires one shared
  rank-one prefix mask, equal pass extents and explicit exact neutral
  selection at every sum/min/max. Only wholly inactive chunks disappear;
  partial chunks keep their masks and combines. The proof accepts unshifted
  signed 32/64-bit prefixes. Offset sums, unsigned bounds, non-neutral
  padding, volatile access, bitcast, index reduction, unsupported layout
  and control-flow effects decline it.
* **Ordinary matrix rows:** a dense FP32/BF16 staged matrix kernel reuses
  each B vector across two independent rows and carries A/B pointers through
  K. Every output retains its K-ordered FMA chain and chain accumulator.
  MR2 is bounded to even M, complete N chunks and LMUL1; other cases retain
  the original masked kernel. FP16 IME selection is unchanged.

Each algorithm has a default-on `CompileOptions` / `LowerOptions` field and
a distinct off identity. Environment switches are
`A100C_KEPT_AXIS_REDUCTION=off`, `A100C_NEUTRAL_REDUCTION_TRIM=off`,
`A100C_MATRIX_ROW_REUSE=off`. The production factory forwards all fields.
The driver option-identity test also executes both plain and factory paths.
Lowered metadata records actual matches, not a claim that every case fires.

The independent geometry fix is commit `8723514`: an already-open chunk
closes before a subsequent pass changes extent, VL or SEW. Its old stride
could otherwise remain 16 while the next pass executes 32 lanes, affecting
another program's output. It is a correctness prerequisite and is held
constant in both sides of the algorithm measurements.

## Destination instruction evidence

[METRICS.json](METRICS.json) contains six paired measurements. Both sides use
the same frozen backend and geometry fix; the three lowering switches are
disabled together in the off column. Thus this is a controlled lowering
comparison, not a claim about the whole unmodified `c8ade47` compiler.

| Sample, threads=1 | Off instructions/launch | On | Reduction |
|---|---:|---:|---:|
| softmax [4,97], FP32 | 36,267 | 5,216 | 85.62% |
| attention [4,4,32,64], FP32 | 48,742,076 | 18,629,308 | 61.78% |
| matmul [16,16,16], FP32 | 31,676 | 19,583 | 38.18% |
| matmul [16,16,16], BF16 | 51,822 | 39,730 | 23.33% |
| matmul [256,256,256], FP32, extra size | 55,710,022 | 30,906,443 | 44.52% |
| matmul [16,16,16], FP16 IME | 34,520 | 34,520 | 0% |

These are dynamic **guest program instructions**, all workers summed per
complete launch, not cycles, QEMU elapsed-time speedups or silicon results.
Five rows use original declared sizes; the 256-cubed row uses the unchanged
case builder at an additional size and contributes no original-case coverage.

`collect_pair.py` reassembles `program.S` and compares its text bytes with the
shipped non-PIE ELF's native program interval. It differences every PC in that
stable interval using two independent repeats-1/repeats-3 pairs. Every program
PC delta is nonnegative and divisible by two; both pairs give exactly the same
instruction count. Shared-library ASLR PCs and allocated MIR op ordinals are
not used. All 48 native profile launches passed their original case comparison
and repeat consistency. Raw bundle/count paths and SHA256s remain in each
`metrics/*/{off,on}/profile.json`; emitted assembly is beside it. The frozen
source hashes are in [MEASUREMENT_SNAPSHOT.json](MEASUREMENT_SNAPSHOT.json).

## Correctness scope

* `test_k3_lowering_optimizations.py`: 64 native executions. The kept-axis
  checks use independent sequential FP32 references, including cancellation
  that detects addition regrouping, rank-3/4 and noncontiguous-axis rejection,
  and exact widening of FP16 sources. Neutral checks include empty/partial
  domains, observable non-neutral padding, NaN, infinities, signed zero,
  observable bitcasts, argmax padding, offset/unsigned/volatile rejection.
  Matrix checks exercise MR2 and odd-M fallback, with/without chain input.
  Every execution repeats three times. Original corpus matrix cases also
  exercise K/N tails and FP16/BF16 conversion boundaries.
* `test_chunk_geometry_boundary.py`: all six original varlen attention
  cases at 1/2/4/8 workers, each with three repeats: 24 independent original
  comparisons, all PASS. See [geometry-repeats.log](geometry-repeats.log).
* Targeted scans: 27 original cases at 1 worker and the same 27 at 8 workers
  (attention_forward, naive decoding, matmul, softmax), plus six naive decoding
  cases each at 2 and 4 workers: 66 PASS case-thread checks. The reports are
  `initial-t1/`, `initial-t8/`, `geometry-t2/`, `geometry-t4/`.
* Full-corpus acceptance is the independent final frozen scan owned by the
  validation task. These targeted/probe results do not substitute for it.
  The input baseline contained two deconv compile-time timeouts, not passes.

## Boundaries and architecture lessons

Dense staging is an effective reuse boundary: changing loops over private
records permits the sum/matrix algorithms without changing source memory
effects or rounding boundaries. Explicit suffix extents and pointer-carried
block parameters are enough for the transformation; no extra persistent IR
or speculative LICM is required.

The chunk-loop geometry had been mutable global lowering state. Recording
the geometry at open time prevents later passes from silently changing its
meaning; a future immutable pass context could make that ownership explicit.

The existing C8 strided narrow forms recognize one affine arange. Matrix
input addresses still contain multiple broadcast terms and can fall back to
scalar halfword loads/staging. In the measured FP16 sample, the program
executes 16 IME instructions but 4,534 vector configurations, 1,280 `lhu`,
2,304 `sh` and 2,304 each of extract/slide operations. See
[IME_HOTSPOT.json](IME_HOTSPOT.json). This justifies a future guarded-contiguous
narrow-memory change; it is not included in this bounded batch, and these
instruction counts alone do not establish a cycle bottleneck.

The historical broadcast-view/early-flat-alias SVD regression, pressure-blind
LICM, maximal LMUL and larger IME tiles are not enabled here. Their source
negative results remain intact.
