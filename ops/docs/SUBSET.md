# The declared subset (suite-v3)

> We do not build a compiler for all of Triton. We build it for a **declared
> subset**, chosen by the target workload: **LLM inference**. Generality is
> then measured *inside* the subset, on held-out operators from the same
> subset (recorded by origin in `suite/heldout.json` on the maintenance branch;
> the release package does not contain them). This document is the definition of that
> subset: five principles, what each removed, what is included (generated from
> the kept operators), and what is explicitly excluded.

The subset is materialised as a **pool of 1000 operators** in
`$POOL` (a maintainer-local directory outside the repository and the release; `pool.json`,
`removed.json`). The workflow input shipped in this repository is a
500-operator selection out of that pool: `suite/dev` 400 correctness operators
and `suite/perf` 100 performance operators. The other 500 pool operators are
the held-out set. Selection and numbers are in [`SUITE_V3.md`](SUITE_V3.md).

## 1. Why a declared subset

Target-independent Triton is not a useful goal for an inference compiler: it
includes training, vendor numeric formats, and thousands of near-duplicate
kernels. A compiler that claims all of it is either never finished or never
tested. We therefore fix the workload first (autoregressive LLM inference,
prefill and decode), take the five principles below as the *definition* of
what is in scope, and treat everything outside as "not implemented" rather
than "unsupported by accident". The subset is still large enough to be hard:
1000 operators, 5612 correctness cases, 75 semantic features and 1612
feature interactions.

Universe audited: 1600 verified operators = 350 in the tracked groups
(`basic/` 48, `medium/` 47, `hard/` 155, `bench/` 100) + 1250 in the upstream
hidden pool. Family counts before/after are in [`SUITE_V3.md`](SUITE_V3.md).

## 2. The five principles

### 2.1 Principle 1 — forward (inference) kernels only

**Reason.** A backward kernel is not on the inference path: it exists to
propagate gradients, accumulate them atomically, or recompute activations for
a training step. Compiling it says nothing about inference quality.

**Removed: 106 operators.** 100 match `bwd|backward|grad` in their name. Six
more are gradient-only kernels whose names do not say so and which were
verified by reading the kernel body; they are listed explicitly in
`BACKWARD_EXTRA` in `harness/tools/build_v3_pool.py`:

| origin | why it is backward |
|---|---|
| `hidden/adam_update_triton.py` | optimiser update (`grad_ptr`, `exp_avg`) |
| `hidden/masked_add_cuda.py` | `grad += p * alpha` |
| `hidden/interior_copy_kernel.py` | conv/pool backward interior copy (`grad_output → grad_input`) |
| `hidden/interior_copy_kernel_row.py` | same, row variant |
| `hidden/jsd__jsd_kernel.py` | fused JSD loss that writes `dX` |
| `hidden/backends__ascend__ops__jsd__jsd_kernel.py` | same |

64 of these 106 were in the v2 suite; v3 is the first forward-only suite.
Forward scatter/atomic operators (`scatter_add`, `index_add`, histogram) are
**kept**: they are forward inference (embedding bags, bucketing), not gradient
accumulation.

### 2.2 Principle 2 — portable numeric semantics only

**Reason.** Every numeric semantics in the subset must have one right answer
on any target. Reduced-mantissa and vendor formats do not.

- **8-bit floating formats (e3m4, e4m3, e5m2, fp8 of any kind) are excluded
  from the subset entirely and are not implemented.** No upstream operator in
  the universe uses them, so this removes 0 operators, but the exclusion is
  declared: `tl.float8*` and `dtype.is_fp8*` are not in the included API.
- **`tl.dot` has exactly two semantics:** bf16/fp16 operands with fp32
  accumulation, and fp32 operands computed exactly (IEEE). tf32 and tf32x3
  are vendor reduced-mantissa formats and are excluded. Therefore **no
  operator may pass `input_precision=` or `allow_tf32=` to `tl.dot`**.
  127 upstream files pass one of them; 68 of those are in the pool (the other
  59 were removed by principle 1 (47 backward), principle 2 (2 libdevice) and
  principle 5 (10 duplicates)). All 68 are stripped:
  the keyword argument, the `*_PRECISION` / `ALLOW_TF32` / `USE_TF32`
  constexpr parameter that fed it, any module-level constant, the case-layer
  `meta` key, and the `linalg.dot.input_precision` metadata tag. fp32 dot is
  IEEE *by definition of the subset*; the harness enforces it by setting
  `TRITON_F32_DEFAULT=ieee` (Triton 3.8 knob) before any operator imports
  Triton (`harness/opslib/device.py`), unless the caller already set it.
  Operator files never mention the knob.
- **libdevice transcendentals are vendor numeric implementations**
  (`__nv_expf`, `__nv_erff`, ...), not portable semantics. **46 operators**
  that call `tl.extra`/`tl.math`/libdevice are removed.
- **float64 tensor cases are removed (7 operators).** fp64 is IEEE, but it is
  not an inference dtype and is not implemented by every accelerator target;
  keeping it would make "one right answer on any target" false for those
  targets. (fp64 appears only in 7 median / Gram / SVD / fp64-mean kernels;
  all other `tl.float64` occurrences in the pool are dead dtype-dispatch
  comparisons for upstream fp64 entry points, never a float64 case.)
- **int8 stays**: quantised inference is plain integer arithmetic. The pool
  keeps 12 quantisation operators and 5 operators with int8 cases.

### 2.3 Principle 3 — the subset is closed over the corpus

**Reason.** The declared API is exactly the constructs the kept operators
use. A construct no kept operator uses is not declared, so the compiler is
never asked to implement an abstraction it cannot be tested on.

- **1 operator is removed** because it calls a construct Triton 3.8 does not
  have (`bench/tanh.py` uses `tl.tanh`; the pool's replacement uses
  `2/(exp(2x)+1)`).
- **`tl.fdiv`** is used by exactly one operator in the universe and by none
  in the pool; it is consequently *not* declared.
- `input_precision`, `allow_tf32`, fp8 dtype constants and
  `linalg.dot.input_precision` vanish from the API because principle 2 strips
  them from every kept operator. This is the closure rule doing real work:
  the feature count drops from 76 to 75 and the interaction count from 1658
  to 1612 exactly because `dot.precision_kw` is no longer a construct of the
  subset.
- **Principle 4 — autotuning stays.** `@triton.autotune` is how real
  high-performance kernels declare their tuning space (decode vs prefill
  tiles, model sizes); a performance compiler must consume it. Autotune is
  never a removal reason. 21 pool operators declare an autotune space.

### 2.4 Principle 5 — representatives by structure, not by count or length

**Reason.** Compilation difficulty comes from structure (loop nests, layouts,
reductions, register pressure, multi-dot pipelines), not from the number of
operators. Hundreds of "same GEMM + a different epilogue" variants exercise
the same compiler abstraction; a 600-line chunked linear-attention kernel
exercises a different one. **We never select or drop by kernel line count.**

**Removed by this principle: 440 operators**, in three groups:

| group | count | rule |
|---|---:|---|
| exact structural duplicates | 224 | same feature set + same operation signature + same tile rank: one representative survives, the removed entry names it |
| redundant variants of an over-represented skeleton | 164 | adds no feature or interaction the pool does not already cover; largest skeleton loses its most expensive redundant member first, never the last member of a skeleton |
| no semantic-size correctness case exists | 52 | see below |

The 52 "no semantic-size case" operators are not removed for being wrong
Triton; they are removed because the corpus contract requires every
correctness operator to have a semantic-size case (`AGENTS.md`: dot
`M,N,K ≤ 128`, attention `seq ≤ 128`). Fifty of them hard-code a
performance-size axis *inside the case layer* (typically
`B = standard_normal((K, 32768))` with the tensor shape parameter controlling
only `M`; the swizzled tile order is then incorrect or meaningless for small
`M`), and two have `SHAPES` entries that are not tensor shapes at all. Every
one is listed in `removed.json` with the failing case and status. A
semantic-size representative of the same skeleton is always kept.

**What is protected, regardless of duplication:**

- **All 82 forward linear-attention kernels** — the `chunk_*` (51),
  `fused_recurrent_*` (12), delta-rule / gated-delta-rule (13), `wy_fast` (4),
  `cumsum` (6), `cumprod` (4) families. They are the register-allocation
  stress tests of the subset; Qwen3.5 uses them in 48 of 64 layers.
- **All 16 forward attention kernels** (flash / decode / paged / varlen).
- **The 100 performance-lane operators** (`bench/`, of which 96 survive
  principles 1–3), because each already carries a steady-state workload rule.
- **Full coverage**: the pool keeps **75/75 features and 1612/1612
  interactions** of the forward+portable universe. Nothing is dropped if it
  is the only cover of a feature or interaction.

## 3. What remains

The subset has a common shape: **dense-tensor, forward, tile programs with
compile-time tile shapes, one launch each**, over **fp32 / bf16 / fp16 / int8**
(plus int32 / int64 / int16 / uint / bool as index, mask and bit types), in
three computational forms of an inference graph:

| form | what it is | examples in the pool |
|---|---|---|
| (a) memory-bound elementwise / norm / softmax fused with reductions | one pass over a tensor, transcendental epilogues, row/column reductions fused into the store | `rmsnorm`, `layernorm`, `softmax`, `swiglu`, `rope`, `argmax`, fused residual+norm |
| (b) dot-driven tile pipelines | GEMM with epilogue, attention, chunked linear attention, multi-dot solve pipelines | `matmul_*`, flash/paged attention, `chunk_*`, `fused_recurrent_*`, `wy_fast` |
| (c) selection / scan / index | argmax/top-k, cumsum/cumprod, gather/scatter, sort/histogram/median, unique | `argmax`, `topk_stage*`, `cumsum`, `gather_1d`, `median_*`, `unique_dim_*` |

Declared case dtypes in the pool (one operator may declare several):

| dtype | operators | role |
|---|---:|---|
| float32 | 946 | default compute and accumulation; also the only dtype for kernels that call an fp32/fp64-only Triton math intrinsic |
| float16 / bfloat16 | 873 / 869 | low-precision tensor-core operands, fp32 accumulation; bf16 is the primary perf-lane dtype |
| int8 | 5 | quantised inference / dequantisation |
| int32 / int64 | 29 / 24 | indices, masks, counters |
| int16 / uint16 / uint32 / uint64 / uint8 | 3 / 2 / 2 / 2 / 2 | bit tricks (histograms, radix select) |
| bool | 7 | masks and selection |

The low-precision counts are operator declarations, not guaranteed passes:
a declaration that stock Triton rejects (e.g. a direct `tl.exp` on bf16) is
removed for that operator and recorded in `SUITE_V3.md` §10.5. Integer and
bool operators keep their integer dtype; `int8` appears only on quantised
paths and `int32`/`int64` where index width is part of the semantics.

## 4. Numeric semantics

| construct | semantics in the subset | enforcement |
|---|---|---|
| `tl.dot` with bf16/fp16 operands | multiply in the operand dtype, accumulate in fp32 | `acc = tl.zeros(..., tl.float32)` / `out_dtype=tl.float32` in the operator; no precision keyword |
| `tl.dot` with fp32 operands | exact IEEE fp32 (no tf32 / tf32x3) | harness pins `TRITON_F32_DEFAULT=ieee`; no operator passes a precision knob |
| elementwise / reduction arithmetic | IEEE fp32 unless the operator declares fp16/bf16 cases; every enriched case uses the shared dtype table below | `ref` is NumPy and is evaluated from the low-precision inputs |
| int8 / int arithmetic | plain two's-complement integer arithmetic | `ref` is NumPy; integer/bool outputs are compared exactly |
| transcendental functions | only `tl.*` portable math (`tl.exp`, `tl.log`, `tl.sqrt`, `tl.sigmoid`, `tl.erf`, ...) | libdevice-derived ops removed by principle 2 |

### 4.1 Case tolerance table

Tolerances are a property of the **case dtype**, not of an operator. The
single table lives in `harness/opslib/case.py` (`DTYPE_TOLERANCES`) and is
applied uniformly by `case_utils.dtype_case` / `comparison_for`, to the dtypes the
enrichment adds:

| case dtype | rtol | atol | comparator |
|---|---:|---:|---|
| float32 | 1e-3 | 1e-3 | `allclose` (only for operators that had no fp32 case before) |
| float16 | 1e-2 | 1e-2 | `allclose` (10-bit significand, fp32 accumulation) |
| bfloat16 | 2e-2 | 2e-2 | `allclose` (8-bit significand, fp32 accumulation) |
| any integer / bool output | exact | exact | `array_equal` |

Exact comparisons and the two semantic comparators (`quantized_interval`,
`allclose_sign_invariant`) are preserved: they express the answer's meaning,
not a numeric slack. No operator may supply a per-shape or per-dtype tolerance
to make a case pass; a new dtype/shape that fails under this table is dropped
and recorded in `SUITE_V3.md` §10.5.

**Scope:** the table applies only to the dtypes task 2 *added* to an operator. Every
dtype an operator already declared keeps its own case builder and its original,
tighter tolerances (`_ENRICH_ORIGINAL_DTYPES` in the enrichment wrapper routes
them to the original `make_case`), so enrichment never loosens an existing check.

## 5. Included constructs (generated from the kept operators)

Generated with the same AST scanner that produces
[`API_INVENTORY.md`](API_INVENTORY.md), pointed at the pool:

```bash
python3 harness/compiler_api/api_inventory.py --dir $POOL/ops \
        --out $POOL/work/pool_api.md
```

The numbers are operator files using the construct (each file counted once).
The suite's own inventory is [`API_INVENTORY.md`](API_INVENTORY.md).

## 调用与装饰器(`tl.*(...)`、`triton.*(...)`、`@...`)

| 构造 | pool | 合计 |
|---|---:|---:|
| `@triton.jit` | 1000 | 1000 |
| `tl.store` | 984 | 984 |
| `tl.load` | 969 | 969 |
| `tl.arange` | 957 | 957 |
| `tl.program_id` | 937 | 937 |
| `tl.sum` | 410 | 410 |
| `tl.where` | 358 | 358 |
| `tl.zeros` | 345 | 345 |
| `tl.dot` | 218 | 218 |
| `tl.cdiv` | 170 | 170 |
| `tl.maximum` | 141 | 141 |
| `tl.abs` | 125 | 125 |
| `tl.exp` | 121 | 121 |
| `tl.max` | 121 | 121 |
| `tl.full` | 100 | 100 |
| `tl.rsqrt` | 99 | 99 |
| `tl.minimum` | 84 | 84 |
| `tl.log` | 73 | 73 |
| `tl.sqrt` | 73 | 73 |
| `tl.sigmoid` | 58 | 58 |
| `tl.min` | 55 | 55 |
| `tl.reshape` | 52 | 52 |
| `tl.multiple_of` | 43 | 43 |
| `tl.constexpr` | 41 | 41 |
| `tl.trans` | 39 | 39 |
| `tl.exp2` | 32 | 32 |
| `tl.range` | 29 | 29 |
| `tl.num_programs` | 27 | 27 |
| `tl.static_range` | 27 | 27 |
| `@triton.autotune` | 21 | 21 |
| `tl.philox` | 19 | 19 |
| `tl.argmax` | 13 | 13 |
| `tl.atomic_add` | 13 | 13 |
| `tl.debug_barrier` | 12 | 12 |
| `tl.erf` | 10 | 10 |
| `tl.floor` | 10 | 10 |
| `tl.make_block_ptr` | 10 | 10 |
| `tl.sin` | 10 | 10 |
| `tl.cast` | 9 | 9 |
| `tl.cos` | 9 | 9 |
| `tl.argmin` | 8 | 8 |
| `tl.div_rn` | 7 | 7 |
| `tl.advance` | 6 | 6 |
| `tl.join` | 6 | 6 |
| `tl.log2` | 6 | 6 |
| `tl.permute` | 6 | 6 |
| `tl.split` | 6 | 6 |
| `tl.zeros_like` | 6 | 6 |
| `tl.cumsum` | 5 | 5 |
| `tl.atomic_max` | 4 | 4 |
| `tl.broadcast_to` | 4 | 4 |
| `tl.rand` | 4 | 4 |
| `tl.atomic_min` | 3 | 3 |
| `tl.cumprod` | 3 | 3 |
| `tl.dtype` | 3 | 3 |
| `tl.expand_dims` | 3 | 3 |
| `tl.fma` | 3 | 3 |
| `tl.pointer_type` | 3 | 3 |
| `tl.static_assert` | 3 | 3 |
| `tl.atomic_xchg` | 2 | 2 |
| `tl.cat` | 2 | 2 |
| `tl.ceil` | 2 | 2 |
| `tl.clamp` | 2 | 2 |
| `tl.histogram` | 2 | 2 |
| `tl.max_contiguous` | 2 | 2 |
| `tl.randn` | 2 | 2 |
| `tl.ravel` | 2 | 2 |
| `tl.sqrt_rn` | 2 | 2 |
| `tl.squeeze` | 2 | 2 |
| `tl.add` | 1 | 1 |
| `tl.atomic_and` | 1 | 1 |
| `tl.atomic_cas` | 1 | 1 |
| `tl.atomic_or` | 1 | 1 |
| `tl.atomic_xor` | 1 | 1 |
| `tl.broadcast` | 1 | 1 |
| `tl.flip` | 1 | 1 |
| `tl.gather` | 1 | 1 |
| `tl.interleave` | 1 | 1 |
| `tl.mul` | 1 | 1 |
| `tl.rand4x` | 1 | 1 |
| `tl.randint` | 1 | 1 |
| `tl.randint4x` | 1 | 1 |
| `tl.randn4x` | 1 | 1 |
| `tl.reduce_or` | 1 | 1 |
| `tl.softmax` | 1 | 1 |
| `tl.sort` | 1 | 1 |
| `tl.sub` | 1 | 1 |
| `tl.swizzle2d` | 1 | 1 |
| `tl.to_tensor` | 1 | 1 |
| `tl.topk` | 1 | 1 |
| `tl.unsqueeze` | 1 | 1 |
| `tl.view` | 1 | 1 |
| `tl.xor_sum` | 1 | 1 |

## dtype 与常量(`tl.float16`、`tl.constexpr` 等非调用属性)

| 构造 | pool | 合计 |
|---|---:|---:|
| `tl.constexpr` | 921 | 921 |
| `tl.float32` | 660 | 660 |
| `tl.int64` | 294 | 294 |
| `tl.int32` | 120 | 120 |
| `tl.float64` | 37 | 37 |
| `tl.bfloat16` | 36 | 36 |
| `tl.float16` | 31 | 31 |
| `tl.uint32` | 26 | 26 |
| `tl.tensor` | 18 | 18 |
| `tl.int1` | 12 | 12 |
| `tl.int16` | 7 | 7 |
| `tl.uint64` | 7 | 7 |
| `tl.int8` | 6 | 6 |
| `tl.uint16` | 3 | 3 |
| `tl.uint8` | 1 | 1 |

## 6. Explicitly excluded

| excluded | why |
|---|---|
| fp8 / e4m3 / e5m2 / e3m4, `tl.float8*`, `dtype.is_fp8*` | vendor numeric formats; no right answer on every target; not implemented |
| tf32 / tf32x3 / `input_precision=` / `allow_tf32=` | vendor reduced-mantissa formats; stripped from all kept operators; fp32 dot is IEEE by definition |
| backward kernels (gradients, atomic gradient accumulation, recomputation) | not on the inference path (principle 1) |
| libdevice / `tl.extra` / `tl.math` | vendor numeric implementations (principle 2) |
| float64 tensor cases | not an inference dtype, not implemented on every accelerator (principle 2) |
| `dot_scaled` / fp4 / int4 | vendor formats, declared unsupported |
| `inline_asm_elementwise` | bypasses the compiler; declared unsupported |
| tensor descriptors / TMA (`make_tensor_descriptor`, `TensorDescriptor`) | declared unsupported |
| `tl.tanh`, `tl.pow`, `tl.bool` | do not exist in Triton 3.8 (principle 3) |
| `tl.fdiv` | no kept operator uses it (principle 3: closure) |
| any other construct absent from §5 | closure: the declared API is exactly what the kept operators use |

## 7. Reproduce

The pool/suite build commands use maintenance-only tools; they are in
`docs/history/reproduce-v3.md` on the maintenance branch.

## 8. Limits

1. The features/interactions are AST approximations, not a specification.
2. The subset boundary is a *choice*, not a theorem: a model with fp8
   inference (e.g. FP8 KV cache) would need the excluded formats.
3. The 52 "no semantic-size case" removals remove some deep-GEMM scheduling
   variants; their skeleton is still represented at semantic sizes.
4. Held-out evaluation must use the recorded held-out set (pool minus suite), not
   a random sample of the universe, otherwise removed-by-design constructs
   leak back in.
