# Operator inventory — `ops/` corpus (workload analysis)

Task T003 (attempt 1). Everything below is derived from the corpus's own
declarations and machine-readable index (`ops/suite/manifest.json`,
`ops/docs/SUBSET.md`, `ops/docs/API_INVENTORY.md`, `ops/docs/SUITE_V3.md`,
`ops/harness/compiler_api/run_cases.py`, `ops/harness/opslib/case.py`) and
from the corpus's own enumeration commands; no number is hand-copied from a
document without a command behind it. The corpus is read-only.

## 1. Corpus identity and size

| property | value | source |
|---|---|---|
| operator files | **500** (`suite/dev` 400, `suite/perf` 100) | operator-set glob `suite/dev/*.py,suite/perf/*.py` (ops/README.md layout; ops/harness/compiler_api/AGENT_GUIDE.md §1) |
| total `.py` files under `ops/` | 542 (42 are harness/runner files, not operators) | ingest-ops (`operator_scope: declared`) |
| (operator, shape, dtype) cases | **2734** (`suite/dev` 2192, `suite/perf` 542) | `run_cases.py --dry-run --group-order`; manifest `cases_total` |
| cases declared = constructible | 2734 = 2734 (every case constructs; `CASE_FAIL` expected 0) | manifest `cases_declared`/`cases_constructible` sums |
| compile identities (meta model) | 2161 (1.26 cases/identity) | SUITE_V3.md §0; `run_cases.py --dry-run --identities` |
| distinct declared shapes | 305 (ranks 1–10; axes from 0 to 393216) | manifest `shape_list` |
| autotune operators | 11 (5 dev, 6 perf) | manifest `autotune` |
| semantic features / interactions covered | 75/75 and 1612/1612 of the declared subset | manifest `coverage` |

Upstream provenance groups recorded in each `OPERATOR` literal (selection
history only — the input grouping is the directory/lane): `hidden` 312, `bench` 96, `hard` 51, `basic` 22, `medium` 19.

### Families (the corpus's own classifier)

| family | operators | cases |
|---|---:|---:|
| `elementwise_reduce` | 246 | 1281 |
| `matmul` | 57 | 312 |
| `norm` | 53 | 283 |
| `select_scan_index` | 50 | 268 |
| `linear_attention` | 32 | 195 |
| `softmax_xent` | 25 | 146 |
| `conv_pool` | 20 | 132 |
| `attention` | 11 | 78 |
| `quant` | 6 | 39 |

## 2. Tier structure and case totals (gate G2 inputs)

The corpus declares exactly two input tiers, in this order
(`ops/harness/compiler_api/run_cases.py`: `GROUP_ORDER = ("suite/dev",
"suite/perf")` — "the two input directories, in the order the corpus
declares them"). A run must support a *prefix* of this order.

Recorded with `group-order --group suite/dev --group suite/perf` and
`record-case-totals`; the case numbers derive from the corpus's own
enumeration command, not from any document:

```bash
cd ops && python3 harness/compiler_api/run_cases.py --manifest suite/manifest.json --dry-run --group-order
# suite/dev    operators= 400 cases=2192
# suite/perf   operators= 100 cases=542
# TOTAL        cases=2734
```

| tier | operators | cases | role (corpus declaration) |
|---|---:|---:|---|
| `suite/dev` | 400 | 2192 | correctness lane; semantic sizes (most axes ≤ 128; 3 verified override shapes exceed it: `nonzero_kernel` [735], `selu_kernel_supreme` [4097]/[393216]) |
| `suite/perf` | 100 | 542 | performance lane; same correctness contract, steady-state timing shapes resolved from `suite/perf/workload.json` by the performance lane |

`suite/dev` is the declared prefix tier: a compiler that passes only
`suite/perf` cannot claim coverage, and one that passes `suite/dev` has not
yet covered the perf lane. A tier with zero executed cases would show as a
harness defect, not as coverage.

## 3. Declared source-language surface (api-spec)

The corpus pins a **declared subset of Triton 3.8** (`ops/docs/SUBSET.md`,
suite-v3): forward-only LLM-inference kernels with portable numeric
semantics. The surface is recorded in `PROJECT_STATE.json`
(`workload.api_spec`) as **107 constructs / 280 parameters**, built from
`ops/docs/API_INVENTORY.md` (the shipped 500-operator suite's own AST
inventory; per-construct operator-file counts = `corpus_calls`), plus
`tl.swizzle2d` (declared in the SUBSET.md §5 pool tables, **0 calls** in the
shipped suite), with parameter surfaces read from the pinned Triton 3.8.0
`triton.language`/`triton.runtime` signatures (`A100_REFERENCE_PYTHON`,
`triton.__version__ == 3.8.0`). Internal `_semantic`/`_generator` plumbing
parameters are excluded from the recorded surface.

Priority by `corpus_calls` (operator files using the construct):
P0 ≥ 100 (11 constructs), P1 10–99 (28), P2 < 10 (68).

| construct | corpus_calls | tier | parameters |
|---|---:|---|---|
| `triton.jit` | 500 | P0 | fn, version, repr, launch_metadata, do_not_specialize, do_not_specialize_on_alignment, debug, noinline |
| `tl.store` | 487 | P0 | pointer, value, mask, boundary_check, cache_modifier, eviction_policy |
| `tl.load` | 481 | P0 | pointer, mask, other, boundary_check, padding_option, cache_modifier, eviction_policy, volatile |
| `tl.arange` | 466 | P0 | start, end |
| `tl.program_id` | 457 | P0 | axis |
| `tl.constexpr` | 450 | P0 | value |
| `tl.float32` | 275 | P0 | — |
| `tl.sum` | 195 | P0 | input, axis, keep_dims, dtype |
| `tl.where` | 182 | P0 | condition, x, y |
| `tl.zeros` | 147 | P0 | shape, dtype |
| `tl.int64` | 139 | P0 | — |
| `tl.maximum` | 78 | P1 | x, y, propagate_nan |
| `tl.dot` | 74 | P1 | input, other, acc, out_dtype |
| `tl.exp` | 73 | P1 | x |
| `tl.max` | 70 | P1 | input, axis, return_indices, return_indices_tie_break_left, keep_dims |
| `tl.abs` | 66 | P1 | x |
| `tl.cdiv` | 59 | P1 | x, div |
| `tl.full` | 56 | P1 | shape, value, dtype |
| `tl.int32` | 54 | P1 | — |
| `tl.sqrt` | 51 | P1 | x |
| `tl.log` | 44 | P1 | x |
| `tl.minimum` | 44 | P1 | x, y, propagate_nan |
| `tl.min` | 30 | P1 | input, axis, return_indices, return_indices_tie_break_left, keep_dims |
| `tl.bfloat16` | 25 | P1 | — |
| `tl.range` | 25 | P1 | arg1, arg2, step, num_stages, loop_unroll_factor, disallow_acc_multi_buffer, flatten, warp_specialize, disable_licm |
| `tl.float16` | 24 | P1 | — |
| `tl.num_programs` | 22 | P1 | axis |
| `tl.reshape` | 22 | P1 | input, *shape, can_reorder |
| `tl.static_range` | 21 | P1 | arg1, arg2, step |
| `tl.multiple_of` | 20 | P1 | input, values |
| `tl.sigmoid` | 17 | P1 | x |
| `tl.float64` | 16 | P1 | — |
| `tl.rsqrt` | 16 | P1 | x |
| `tl.trans` | 14 | P1 | input, *dims |
| `tl.exp2` | 12 | P1 | x |
| `tl.uint32` | 12 | P1 | — |
| `tl.atomic_add` | 11 | P1 | pointer, val, mask, sem, scope |
| `triton.autotune` | 11 | P1 | configs, key, prune_configs_by, reset_to_zero, restore_value, pre_hook, post_hook, warmup, rep, use_cuda_graph, do_bench, cache_results |
| `tl.erf` | 10 | P1 | x |
| `tl.int1` | 9 | P2 | — |
| `tl.make_block_ptr` | 9 | P2 | base, shape, strides, offsets, block_shape, order |
| `tl.cast` | 8 | P2 | input, dtype, fp_downcast_rounding, bitcast |
| `tl.tensor` | 8 | P2 | — |
| `tl.argmax` | 7 | P2 | input, axis, tie_break_left, keep_dims |
| `tl.debug_barrier` | 7 | P2 | — |
| `tl.floor` | 7 | P2 | x |
| `tl.philox` | 7 | P2 | seed, c0, c1, c2, c3, n_rounds |
| `tl.advance` | 5 | P2 | base, offsets |
| `tl.cos` | 5 | P2 | x |
| `tl.join` | 5 | P2 | a, b |
| `tl.log2` | 5 | P2 | x |
| `tl.sin` | 5 | P2 | x |
| `tl.split` | 5 | P2 | a |
| `tl.uint64` | 5 | P2 | — |
| `tl.argmin` | 4 | P2 | input, axis, tie_break_left, keep_dims |
| `tl.cumsum` | 4 | P2 | input, axis, reverse, dtype |
| `tl.div_rn` | 4 | P2 | x, y |
| `tl.int16` | 4 | P2 | — |
| `tl.int8` | 4 | P2 | — |
| `tl.permute` | 4 | P2 | input, *dims |
| `tl.rand` | 4 | P2 | seed, offset, n_rounds |
| `tl.atomic_max` | 3 | P2 | pointer, val, mask, sem, scope |
| `tl.atomic_min` | 3 | P2 | pointer, val, mask, sem, scope |
| `tl.broadcast_to` | 3 | P2 | input, *shape |
| `tl.static_assert` | 3 | P2 | cond, msg |
| `tl.zeros_like` | 3 | P2 | input |
| `tl.atomic_xchg` | 2 | P2 | pointer, val, mask, sem, scope |
| `tl.cat` | 2 | P2 | input, other, can_reorder, dim |
| `tl.clamp` | 2 | P2 | x, min, max, propagate_nan |
| `tl.cumprod` | 2 | P2 | input, axis, reverse |
| `tl.dtype` | 2 | P2 | name |
| `tl.fma` | 2 | P2 | x, y, z |
| `tl.randn` | 2 | P2 | seed, offset, n_rounds |
| `tl.ravel` | 2 | P2 | x, can_reorder |
| `tl.squeeze` | 2 | P2 | x, dim |
| `tl.add` | 1 | P2 | x, y, sanitize_overflow |
| `tl.atomic_and` | 1 | P2 | pointer, val, mask, sem, scope |
| `tl.atomic_cas` | 1 | P2 | pointer, cmp, val, sem, scope |
| `tl.atomic_or` | 1 | P2 | pointer, val, mask, sem, scope |
| `tl.atomic_xor` | 1 | P2 | pointer, val, mask, sem, scope |
| `tl.broadcast` | 1 | P2 | input, other |
| `tl.ceil` | 1 | P2 | x |
| `tl.expand_dims` | 1 | P2 | input, axis |
| `tl.flip` | 1 | P2 | x, dim |
| `tl.gather` | 1 | P2 | src, index, axis |
| `tl.histogram` | 1 | P2 | input, num_bins, mask |
| `tl.interleave` | 1 | P2 | a, b |
| `tl.max_contiguous` | 1 | P2 | input, values |
| `tl.mul` | 1 | P2 | x, y, sanitize_overflow |
| `tl.pointer_type` | 1 | P2 | element_ty, address_space, const |
| `tl.rand4x` | 1 | P2 | seed, offsets, n_rounds |
| `tl.randint` | 1 | P2 | seed, offset, n_rounds |
| `tl.randint4x` | 1 | P2 | seed, offset, n_rounds |
| `tl.randn4x` | 1 | P2 | seed, offset, n_rounds |
| `tl.reduce_or` | 1 | P2 | input, axis, keep_dims |
| `tl.softmax` | 1 | P2 | x, dim, keep_dims, ieee_rounding |
| `tl.sort` | 1 | P2 | x, dim, descending |
| `tl.sqrt_rn` | 1 | P2 | x |
| `tl.sub` | 1 | P2 | x, y, sanitize_overflow |
| `tl.to_tensor` | 1 | P2 | x |
| `tl.topk` | 1 | P2 | x, k, dim, descending |
| `tl.uint16` | 1 | P2 | — |
| `tl.uint8` | 1 | P2 | — |
| `tl.unsqueeze` | 1 | P2 | x, dim |
| `tl.view` | 1 | P2 | input, *shape |
| `tl.xor_sum` | 1 | P2 | input, axis, keep_dims |
| `tl.swizzle2d` | 0 | P2 | i, j, size_i, size_j, size_g |

Constructs with recorded `out_of_scope` reasons:

- `tl.dot` — `input_precision=`/`allow_tf32=` are stripped from every kept
  operator by SUBSET.md principle 2 (fp32 `tl.dot` is exact IEEE; the runner
  pins `TRITON_F32_DEFAULT=ieee`), and `max_num_imprecise_acc` applies to
  fp8, which the subset excludes. Declared parameters: `input, other, acc,
  out_dtype` — bf16/fp16 operands with fp32 accumulation, or fp32 IEEE.
- `tl.float64` — no float64 tensor case exists (SUBSET.md principle 2). The
  16 occurrences are constexpr dtype-dispatch comparisons/branches that are
  dead for the declared case dtypes (verified against the manifest: no
  operator declares a `float64` case). The constant must parse and compare
  during specialization; no fp64 tensor compute path is exercised.

### Explicitly excluded by the subset (SUBSET.md §6) — not part of the surface

| excluded | reason |
|---|---|
| fp8 / e4m3 / e5m2 / e3m4, `tl.float8*`, `dtype.is_fp8*` | vendor numeric formats; no portable right answer |
| tf32 / tf32x3 / `input_precision=` / `allow_tf32=` | vendor reduced-mantissa; stripped from all kept operators |
| backward/gradient kernels | not on the inference path (principle 1) |
| libdevice / `tl.extra` / `tl.math` | vendor numeric implementations (principle 2) |
| float64 tensor cases | not an inference dtype (principle 2) |
| `dot_scaled` / fp4 / int4 | vendor formats, declared unsupported |
| `inline_asm_elementwise` | bypasses the compiler |
| tensor descriptors / TMA | declared unsupported |
| `tl.tanh` / `tl.pow` / `tl.bool` | do not exist in Triton 3.8 (principle 3) |
| `tl.fdiv` | no kept operator uses it (closure, principle 3) |

Nothing the corpus requires lies outside the declared subset: the subset is
closed over the kept operators by construction (principle 3), and the
shipped suite's inventory (106 constructs) is exactly the pool subset minus
`tl.swizzle2d`. There are therefore **no language gaps inside the input**;
the exclusion table above is the complete refusal boundary.

## 4. Feature matrix (75 semantic tags, the corpus's own taxonomy)

Tags come from the corpus's AST feature extractor
(`harness/opslib/features.py`) and are recorded per operator in
`suite/manifest.json`. Counts are operators exhibiting the feature.
Priority: **P0** ≥ 200 operators (blocks most of the corpus), **P1** 20–199
(blocks many), **P2** < 20 (rare but required for full coverage — the suite
keeps 75/75 features, so every P2 feature has at least one owner that must
pass).

### Elementwise arithmetic and comparison

| feature | operators | priority | example operators |
|---|---:|---|---|
| `arith.add` | 496 | P0 | absolute_kernel.py, adaptive_avg_pool2d_kernel.py, add_base_max_kernel.py, alpha_dropout_inplace_kernel.py |
| `arith.mul` | 476 | P0 | absolute_kernel.py, adaptive_avg_pool2d_kernel.py, add_base_max_kernel.py, alpha_dropout_inplace_kernel.py |
| `cmp.compare` | 442 | P0 | absolute_kernel.py, adaptive_avg_pool2d_kernel.py, add_base_max_kernel.py, alpha_dropout_inplace_kernel.py |
| `arith.sub` | 262 | P0 | adaptive_avg_pool2d_kernel.py, add_base_max_kernel.py, alpha_dropout_inplace_kernel.py, amax_kernel.py |
| `arith.div` | 258 | P0 | adaptive_avg_pool2d_kernel.py, argmax_kernel_inner.py, argmin_kernel_contiguous.py, atanh_kernel.py |
| `arith.mod` | 124 | P1 | adaptive_avg_pool2d_kernel.py, argmax_kernel_inner.py, argmin_kernel_contiguous.py, atomic_bitmap.py |
| `arith.neg` | 79 | P1 | absolute_kernel.py, alpha_dropout_inplace_kernel.py, amax_kernel.py, amax_kernel_1.py |

### Indexing and shapes

| feature | operators | priority | example operators |
|---|---:|---|---|
| `construct.arange` | 466 | P0 | absolute_kernel.py, adaptive_avg_pool2d_kernel.py, add_base_max_kernel.py, alpha_dropout_inplace_kernel.py |
| `index.multi_offset` | 202 | P0 | adaptive_avg_pool2d_kernel.py, alpha_dropout_inplace_kernel.py, amax_kernel.py, any_kernel_dim.py |
| `index.rank2` | 9 | P2 | chunk_gated_delta_product_fwd_kernel_h_blockdim64.py, chunk_gdn2_fwd_kernel_intra_sub_chunk.py, chunk_transform_qk_fwd_kernel.py, fused_recurrent_fwd_kernel.py |
| `index.rank3plus` | 1 | P2 | chunk_generalized_iplr_delta_rule_fwd_kernel_o.py |
| `shape.broadcast` | 3 | P2 | fused_gemm_gn_min_kernel_2.py, fused_grouped_gate_kernel.py, implicit_conv2d.py |
| `shape.expand` | 3 | P2 | conv1x1_pool_fc_kernel.py, position_quantize.py, synthesis_kernel.py |
| `pat.reduce_broadcast` | 108 | P1 | backends__ascend__ops__grpo_loss__selective_log_softmax_kernel.py, blocked_jacobi_pair_svals_kernel.py, chunk_gdn2_fwd_kernel_inter_solve_fused.py, chunk_gdn2_fwd_kernel_intra_sub_chunk.py |

### Memory access and masking

| feature | operators | priority | example operators |
|---|---:|---|---|
| `mem.load` | 481 | P0 | absolute_kernel.py, adaptive_avg_pool2d_kernel.py, add_base_max_kernel.py, alpha_dropout_inplace_kernel.py |
| `mem.masked_load` | 372 | P0 | absolute_kernel.py, adaptive_avg_pool2d_kernel.py, add_base_max_kernel.py, alpha_dropout_inplace_kernel.py |
| `mem.other` | 358 | P0 | adaptive_avg_pool2d_kernel.py, alpha_dropout_inplace_kernel.py, amax_kernel.py, amax_kernel_1.py |
| `mem.store` | 487 | P0 | absolute_kernel.py, adaptive_avg_pool2d_kernel.py, add_base_max_kernel.py, alpha_dropout_inplace_kernel.py |
| `mem.masked_store` | 283 | P0 | absolute_kernel.py, adaptive_avg_pool2d_kernel.py, add_base_max_kernel.py, alpha_dropout_inplace_kernel.py |
| `pat.masked_both` | 261 | P0 | absolute_kernel.py, adaptive_avg_pool2d_kernel.py, add_base_max_kernel.py, alpha_dropout_inplace_kernel.py |
| `mem.blockptr` | 9 | P2 | diag_scale_kernel.py, flash_varlen_fwd_kernel.py, grouped_gemm_kernel.py, grouped_mm_kernel.py |
| `mem.boundary_check` | 8 | P2 | diag_scale_kernel.py, flash_varlen_fwd_kernel.py, grouped_gemm_kernel.py, grouped_mm_kernel.py |
| `pat.blockptr_boundary` | 8 | P2 | diag_scale_kernel.py, flash_varlen_fwd_kernel.py, grouped_gemm_kernel.py, grouped_mm_kernel.py |
| `mem.cache_hint` | 26 | P1 | alpha_dropout_inplace_kernel.py, argmin_tiled_kernel.py, fht_kernel_1d_native.py, fht_kernel_256_1d_native.py |
| `mem.alignment_hint` | 20 | P1 | argmin_tiled_kernel.py, flash_varlen_fwd_kernel.py, frobenius_norm_persistent_two_phase_kernel.py, l1_norm_fused_hyper_kernel_c1fb1344.py |
| `mem.padding` | 4 | P2 | diag_scale_kernel.py, leaky_relu_kernel_strided.py, matmul_abt_kernel.py, matmul_kernel_1334dd27.py |

### Broadcasting

| feature | operators | priority | example operators |
|---|---:|---|---|
| `shape.broadcast` | 3 | P2 | fused_gemm_gn_min_kernel_2.py, fused_grouped_gate_kernel.py, implicit_conv2d.py |
| `pat.reduce_broadcast` | 108 | P1 | backends__ascend__ops__grpo_loss__selective_log_softmax_kernel.py, blocked_jacobi_pair_svals_kernel.py, chunk_gdn2_fwd_kernel_inter_solve_fused.py, chunk_gdn2_fwd_kernel_intra_sub_chunk.py |

### Selection, constants and fused patterns

| feature | operators | priority | example operators |
|---|---:|---|---|
| `select.where` | 188 | P1 | absolute_kernel.py, adaptive_avg_pool2d_kernel.py, add_base_max_kernel.py, alpha_dropout_inplace_kernel.py |
| `construct.zeros` | 147 | P1 | adaptive_avg_pool2d_kernel.py, any_kernel_dim.py, argmin_tiled_kernel.py, avg_pool1d_kernel_optimized.py |
| `construct.full` | 56 | P1 | amax_kernel.py, argmax_kernel_non_inner.py, argmin_kernel_opt_k1.py, argmin_split_K_kernel_merged.py |
| `pat.softmax` | 31 | P1 | backends__ascend__ops__grpo_loss__selective_log_softmax_kernel.py, cross_entropy_kernel.py, dropout_softmax_fwd_kernel.py, flash_varlen_fwd_kernel.py |
| `pat.normalize` | 25 | P1 | blocked_jacobi_pair_svals_kernel.py, cyclic_jacobi_pair_kernel.py, frobenius_norm_persistent_two_phase_kernel.py, fused_gemm_gn_min_kernel.py |
| `hint.static_assert` | 3 | P2 | fused_gemm_gn_min_kernel.py, matmul_k64_2d_unmasked_kernel_fc2c17b0.py, selu_kernel_supreme.py |

### Reductions and scans

| feature | operators | priority | example operators |
|---|---:|---|---|
| `red.sum` | 195 | P1 | atomic_bitmap.py, backends__ascend__ops__grpo_loss__selective_log_softmax_kernel.py, blocked_jacobi_pair_svals_kernel.py, cholesky_upper_kernel.py |
| `red.axis` | 180 | P1 | amax_kernel.py, any_kernel_1.py, any_kernel_2.py, any_kernel_dim.py |
| `red.maxmin` | 91 | P1 | amax_kernel.py, amax_kernel_1.py, amax_kernel_2.py, any_kernel_1.py |
| `red.argmaxmin` | 11 | P2 | argmin_kernel_contiguous.py, argmin_tiled_kernel.py, fused_grouped_gate_kernel.py, hidden__argmax_kernel_2.py |
| `red.scan` | 4 | P2 | cumprod_dim1_grouped_mixed_kernel.py, cumprod_dim1_kernel_log2exp2_early.py, masked_cumsum_kernel_db.py, masked_cumsum_vec_kernel.py |
| `red.keep_dims` | 4 | P2 | logsumexp__logsumexp_kernel_non_inner.py, mean_dim_kernel_non_inner.py, nansum_dim_kernel_non_inner.py, position_quantize.py |
| `red.histogram` | 1 | P2 | nanmedian_ascend_histogram_count_kernel.py |
| `red.sort` | 1 | P2 | ranked_distribution_semantic.py |
| `pat.persistent_reduce` | 146 | P1 | amax_kernel.py, any_kernel_dim.py, argmax_kernel_inner.py, argmax_kernel_non_inner.py |

### Dot / matrix multiply

| feature | operators | priority | example operators |
|---|---:|---|---|
| `dot.matmul` | 74 | P1 | chunk_abc_fwd_kernel_intra_K.py, chunk_gated_delta_product_fwd_kernel_h_blockdim64.py, chunk_gdn2_fwd_kernel_inter_solve_fused.py, chunk_gdn2_fwd_kernel_intra_sub_chunk.py |
| `dot.acc` | 4 | P2 | grouped_gemm_kernel.py, grouped_mm_kernel.py, matmul_abt_kernel.py, matmul_kernel.py |
| `dot.out_dtype` | 4 | P2 | flash_varlen_fwd_kernel.py, fused_conv3d_kernel_2.py, matmul_kernel_283adb7c.py, matmul_kernel_8d68babe.py |
| `pat.k_loop` | 53 | P1 | chunk_abc_fwd_kernel_intra_K.py, chunk_gated_delta_product_fwd_kernel_h_blockdim64.py, chunk_gdn2_fwd_kernel_inter_solve_fused.py, chunk_gdn2_fwd_kernel_intra_sub_chunk.py |
| `pat.matmul_epilogue` | 45 | P1 | chunk_abc_fwd_kernel_intra_K.py, chunk_gated_delta_product_fwd_kernel_h_blockdim64.py, chunk_gdn2_fwd_kernel_inter_solve_fused.py, chunk_gdn2_fwd_kernel_intra_sub_chunk.py |
| `pat.dot_reduce` | 12 | P2 | chunk_gdn2_fwd_kernel_inter_solve_fused.py, chunk_gdn2_fwd_kernel_intra_sub_chunk.py, conv1x1_pool_fc_kernel.py, flash_varlen_fwd_kernel.py |

### Atomics

| feature | operators | priority | example operators |
|---|---:|---|---|
| `mem.atomic` | 16 | P2 | atomic_bitmap.py, bincount_kernel.py, bn_inc_and_write_momentum_kernel.py, conv1x1_pool_fc_kernel.py |

### Control flow

| feature | operators | priority | example operators |
|---|---:|---|---|
| `flow.loop` | 244 | P0 | adaptive_avg_pool2d_kernel.py, amax_kernel.py, any_kernel_dim.py, argmax_kernel_inner.py |
| `flow.dynamic_range` | 205 | P0 | adaptive_avg_pool2d_kernel.py, amax_kernel.py, any_kernel_dim.py, argmax_kernel_inner.py |
| `flow.if` | 160 | P1 | alpha_dropout_inplace_kernel.py, amax_kernel.py, amax_kernel_1.py, amax_kernel_2.py |
| `flow.if_pid` | 11 | P2 | add_base_max_kernel.py, conv1x1_pool_fc_kernel.py, fused_bn_relu_kernel.py, l1_norm_fused_kernel_16977248.py |
| `flow.while` | 15 | P2 | blocked_jacobi_rank_kernel.py, cholesky_upper_kernel.py, deconv3d_fwd_kernel.py, frobenius_norm_persistent_two_phase_kernel.py |
| `flow.tl_range` | 25 | P1 | backends__ascend__ops__grpo_loss__selective_log_softmax_kernel.py, count_valid_kernel.py, flash_varlen_fwd_kernel.py, forward_pass_chunks.py |
| `flow.static_range` | 21 | P1 | backends__ascend__ops__grpo_loss__selective_log_softmax_kernel.py, complex_svd_pick_orthonormal_v_kernel.py, complex_svd_project_u_kernel.py, control_flow.py |
| `tune.loop_pragma` | 4 | P2 | fused_l1_norm_kernel_e5b6ba01.py, fused_recurrent_gdn2_fwd_kernel.py, medium__hardsigmoid_kernel.py, pipelined_gemv.py |

### Dtype conversions and casts

| feature | operators | priority | example operators |
|---|---:|---|---|
| `cast.explicit` | 275 | P0 | adaptive_avg_pool2d_kernel.py, add_base_max_kernel.py, alpha_dropout_inplace_kernel.py, amax_kernel.py |
| `cast.to_fp32` | 158 | P1 | adaptive_avg_pool2d_kernel.py, amp_foreach_non_finite_check_and_unscale_kernel.py, amp_update_scale_kernel.py, asinh_kernel.py |
| `cast.to_fp16` | 6 | P2 | gemm_rowstats_group_tc_kernel.py, hardsigmoid_kernel_2.py, masked_cumsum_vec_kernel.py, matmul_kernel_7e8de72a.py |
| `dtype.int` | 160 | P1 | add_base_max_kernel.py, alpha_dropout_inplace_kernel.py, amax_kernel.py, amax_kernel_1.py |
| `dtype.uint` | 13 | P2 | alpha_dropout_inplace_kernel.py, bitcast.py, dropout_softmax_fwd_kernel.py, flash_varlen_fwd_kernel.py |
| `logic.bitwise` | 173 | P1 | adaptive_avg_pool2d_kernel.py, alpha_dropout_inplace_kernel.py, amp_foreach_non_finite_check_and_unscale_kernel.py, argmin_kernel_opt_k1.py |
| `logic.bool` | 46 | P1 | alpha_dropout_inplace_kernel.py, amax_kernel.py, any_kernel_dim.py, argmax_kernel_non_inner.py |

### Layout transformations

| feature | operators | priority | example operators |
|---|---:|---|---|
| `shape.reshape` | 27 | P1 | adaptive_avg_pool2d_kernel.py, avg_pool1d_kernel_optimized.py, chunk_abc_fwd_kernel_intra_K.py, chunk_gated_delta_product_fwd_kernel_h_blockdim64.py |
| `shape.trans` | 18 | P2 | chunk_gdn2_fwd_kernel_inter_solve_fused.py, chunk_gdn2_fwd_kernel_intra_sub_chunk.py, chunk_transform_qk_fwd_kernel.py, complex_pack.py |
| `shape.split_join` | 6 | P2 | complex_pack.py, fht_kernel_1d_native.py, fht_kernel_256_1d_native.py, fht_kernel_256_4row_native.py |

### Special math functions

| feature | operators | priority | example operators |
|---|---:|---|---|
| `math.transcendental` | 125 | P1 | asinh_kernel.py, atanh_kernel.py, backends__ascend__ops__grpo_loss__selective_log_softmax_kernel.py, binary_cross_entropy_elementwise_kernel.py |
| `math.clamp` | 111 | P1 | adaptive_avg_pool2d_kernel.py, add_base_max_kernel.py, amax_kernel.py, backends__ascend__ops__grpo_loss__selective_log_softmax_kernel.py |
| `math.abs` | 66 | P1 | amp_foreach_non_finite_check_and_unscale_kernel.py, asinh_kernel.py, blocked_jacobi_pair_svals_kernel.py, cholesky_upper_kernel.py |
| `math.sqrt_rsqrt` | 62 | P1 | asinh_kernel.py, blocked_jacobi_pair_svals_kernel.py, cholesky_kernel.py, cholesky_upper_kernel.py |
| `math.round` | 7 | P2 | floor_kernel.py, log_normal_kernel_impl.py, position_quantize.py, pow_scalar_tensor.py |
| `arith.pow` | 15 | P2 | amax_kernel.py, amax_kernel_1.py, amax_kernel_2.py, argmax_kernel_inner.py |
| `misc.rng` | 12 | P2 | alpha_dropout_inplace_kernel.py, dropout_softmax_fwd_kernel.py, fused_exponential_kernel_f32_unroll8.py, fused_fill_dropout_kernel.py |

### Launch/runtime contract

| feature | operators | priority | example operators |
|---|---:|---|---|
| `tune.autotune` | 11 | P2 | fused_layernorm_triton.py, max_reduction.py, quant_transpose_kernel.py, reversed_cumsum.py |
| `misc.barrier` | 7 | P2 | atomic_bitmap.py, chunk_gdn2_fwd_kernel_intra_sub_chunk.py, chunk_hgrn_fwd_kernel_o.py, cross_entropy_kernel.py |

### Parallel shape of the corpus

- **Unit of parallel work**: the Triton *program* (SPMD grid instance).
  Every kernel is launched as a grid of independent programs; axes are
  partitioned by `tl.program_id` (`construct.arange` + `tl.program_id` in
  457/500 operators). The compiler must expose the same parallel unit.
- **Independent axes**: rows/tiles/heads/batch elements — one program owns a
  disjoint output tile in the dominant patterns (elementwise rows, matmul
  tiles with 1D grouped swizzle, attention heads × sequence blocks, conv
  output positions). No inter-program communication is needed for
  484/500 operators.
- **Cross-program communication**: only through **atomics** — 16 operators
  (all `suite/dev`: `atomic_bitmap`, `bincount_kernel`, `scatter_atomic_kernel`,
  `splitk_gemv`, `weighted_scatter_add_kernel`, `frobenius_norm_persistent_two_phase_kernel`,
  …) accumulate across programs via `tl.atomic_add/max/min/xchg/and/or/xor/cas`
  (with `sem`/`scope` parameters); two-phase reductions write partials then
  combine.
- **Barriers/synchronization**: `tl.debug_barrier` in 7 operators
  (intra-program ordering, e.g. `atomic_bitmap` orders summary reads after
  atomics). There is no inter-program barrier construct in the subset.
- **Persistent / grid-stride programs**: `pat.persistent_reduce` (146
  operators) loops a reduction over multiple chunks inside one program;
  `tl.num_programs` is read by 22 operators (grid-aware partitioning).
- **Program-internal parallelism**: block-level vector shapes
  (`tl.arange` extents are `tl.constexpr`), intra-block reductions
  (`tl.sum`/`tl.max`/`tl.argmax` … over block axes), and `tl.dot` tile
  pipelines inside one program. `num_warps` (4 dominant, 8 for some) is a
  launch-time parameter of the program, not of the language.
- The runtime may repartition work across native workers
  (chip constraint: 1/2/4/8 A100 compute workers) when semantics permit;
  source program granularity need not be the native scheduling granularity
  (A100-NATIVE-OPERATOR).

### Launch/runtime contract (per case, corpus-declared)

Fields every case carries (`AGENT_GUIDE.md` §1.3):

| field | contract |
|---|---|
| `kernel` | the single `@triton.jit` function (one per file, locked by `harness/tests/test_normalized_corpus.py`) |
| `args` | pointers = numpy arrays; scalars = python/numpy scalars (runtime values, never baked in beyond declared specialization) |
| `meta` | constexpr arguments (part of the compilation identity) |
| `grid` | static tuple **or** callable `lambda meta:` (both forms occur; autotune configs may change it) |
| `outputs` | buffer names to read back and compare |
| `expected` / `comparison` | per-output policy: `{comparator, exact, rtol, atol, equal_nan}` |
| `launch_meta` | `num_warps` (4 in 233 files, 8 in 44), `num_stages` (1 in 207 files, 2–5 in 31) |
| `pointer_dtypes` | device pointer dtype when it differs from the host array: bf16 = host float32 → cast, or host uint16 → bit view; readback is symmetric |
| `allocations` / `pointer_table_relocations` | pointer tables: device addresses written into another buffer (`grouped_gemm_kernel`) |

Comparison policy (`harness/opslib/case.py::DTYPE_TOLERANCES`, a property of
the case dtype, never tuned per operator):

| case dtype | rtol / atol | comparator |
|---|---|---|
| float32 | 1e-3 / 1e-3 | `allclose`, `equal_nan` |
| float16 | 1e-2 / 1e-2 | `allclose`, `equal_nan` |
| bfloat16 | 2e-2 / 2e-2 | `allclose` (host decodes bf16 to fp32; value tolerance) |
| any integer / bool | exact | `array_equal` |

Two semantic comparators are part of the contract: `quantized_interval`
(`position_quantize`) and `allclose_sign_invariant` (implemented in
`harness/opslib/compare.py`, not exercised by the current suite). Integer,
index and boolean outputs are exact everywhere (IR-NUMERIC-POLICY). The
optional `launches` field (repeated launches on one buffer set, single
readback) is declared by the harness but used by **no operator in this
suite**.

## 5. Shape × dtype matrix

Read from the manifest's `shape_list` × `dtype_names` per operator (the
machine-readable index); for every operator `cases == |shape_list| ×
|dtype_names|` (verified, 500/500). **Total (operator, shape, dtype) cases:
2734** (= 2734 recomputed from the matrix = the enumeration
command's 2734 = `A100_CORPUS_CASES.json.manifest`'s 2734 rows).

### dtype distribution

| dtype | operators declaring | cases contributed | role (SUBSET.md §3) |
|---|---:|---:|---|
| `float32` | 465 | 957 | default compute and accumulation |
| `float16` | 413 | 850 | low-precision operand, fp32 accumulation |
| `bfloat16` | 412 | 849 | low-precision operand, fp32 accumulation; primary perf-lane dtype |
| `int32` | 18 | 37 | indices, masks, counters |
| `int64` | 13 | 26 | indices, counters |
| `bool` | 4 | 8 | masks and selection |
| `int8` | 2 | 5 | quantised inference / dequantisation |
| `int16` | 1 | 2 | bit tricks |
| **total** | | **2734** | |

### shape characteristics

- ranks 1–10 (586 rank-1, 215 rank-2, …, 1 rank-10 case shapes); 305
  distinct shapes; axis values from 0 to 393216.
- **Ragged tails are deliberate**: shapes include non-divisible extents
  (`(3,17)`, `(97,100)`, `(7,67)`, `(5,99)` …) so masked tails are exercised
  (`mem.masked_load` 372 ops, `mem.masked_store` 283, `mem.other` 358).
- **Degenerate shapes are deliberate**: 7 cases with a zero axis (zero work),
  34 all-ones cases (size 1), `(1,1)`-style minimums.
- dev-lane dot-class shapes are semantic sizes (`M,N,K ≤ 128`), attention
  `seq ≤ 128`; 3 verified dev overrides exceed 128 (`nonzero_kernel` [735],
  `selu_kernel_supreme` [4097], [393216]). Perf-lane steady-state sizes come
  from `suite/perf/workload.json` at timing time, not from these cases.

### per-operator matrix (500 operators)

`tags` are the corpus's own semantic feature tags from the manifest.

| operator | lane | family | cases | shapes | dtypes | tags |
|---|---|---|---:|---|---|---|
| `suite/dev/absolute_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.neg cmp.compare construct.arange mem.load mem.masked_load mem.masked_store mem.store pat.masked_both select.where |
| `suite/dev/adaptive_avg_pool2d_kernel.py` | dev | conv_pool | 6 | (1,2,5,7,3,4); (2,3,8,9,4,5) | float16, float32, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.clamp mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both select.where shape.reshape |
| `suite/dev/add_base_max_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cmp.compare construct.arange dtype.int flow.if_pid math.clamp mem.load mem.masked_load mem.masked_store mem.store pat.masked_both select.where |
| `suite/dev/alpha_dropout_inplace_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.neg arith.sub cast.explicit cmp.compare construct.arange dtype.int dtype.uint flow.if index.multi_offset logic.bitwise logic.bool mem.cache_hint mem.load mem.masked_load mem.masked_store mem.other mem.store misc.rng pat.masked_both select.where |
| `suite/dev/amax_kernel.py` | dev | elementwise_reduce | 6 | (17); (102) | float32, float16, bfloat16 | arith.add arith.mul arith.neg arith.pow arith.sub cast.explicit cmp.compare construct.arange construct.full dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bool math.clamp mem.load mem.other mem.store pat.persistent_reduce red.axis red.maxmin select.where |
| `suite/dev/amax_kernel_1.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.neg arith.pow arith.sub cast.explicit cmp.compare construct.arange dtype.int flow.if mem.load mem.masked_load mem.other mem.store red.maxmin |
| `suite/dev/amax_kernel_2.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.neg arith.pow arith.sub cmp.compare construct.arange flow.if mem.load mem.masked_load mem.other mem.store red.maxmin |
| `suite/dev/amp_foreach_non_finite_check_and_unscale_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange logic.bitwise math.abs mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both select.where |
| `suite/dev/amp_update_scale_kernel.py` | dev | elementwise_reduce | 6 | (1); (3) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare dtype.int mem.load mem.store select.where |
| `suite/dev/any_kernel_1.py` | dev | elementwise_reduce | 2 | (17); (103) | bool | arith.add arith.mul cast.explicit cmp.compare construct.arange dtype.int mem.load mem.masked_load mem.other mem.store red.axis red.maxmin |
| `suite/dev/any_kernel_2.py` | dev | elementwise_reduce | 2 | (17); (126) | bool | arith.add cast.explicit cmp.compare construct.arange dtype.int mem.load mem.masked_load mem.other mem.store red.axis red.maxmin |
| `suite/dev/any_kernel_dim.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.loop index.multi_offset logic.bool mem.load mem.other mem.store pat.persistent_reduce red.axis red.maxmin |
| `suite/dev/arange_func.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange dtype.int mem.masked_store mem.store |
| `suite/dev/argmax_kernel_inner.py` | dev | select_scan_index | 6 | (17); (114) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.neg arith.pow arith.sub cast.explicit cmp.compare construct.arange dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset mem.load mem.masked_load mem.other mem.store pat.persistent_reduce red.axis red.maxmin select.where |
| `suite/dev/argmax_kernel_non_inner.py` | dev | select_scan_index | 6 | (17); (120) | float32, float16, bfloat16 | arith.add arith.mul arith.neg arith.pow arith.sub cast.explicit cmp.compare construct.arange construct.full dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bool mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.axis red.maxmin select.where |
| `suite/dev/argmin_kernel_contiguous.py` | dev | select_scan_index | 9 | (128,128,2); (100,7,3); (1,1,1) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul cmp.compare construct.arange flow.dynamic_range flow.loop mem.load mem.masked_load mem.other mem.store pat.persistent_reduce red.argmaxmin red.axis red.maxmin select.where |
| `suite/dev/argmin_kernel_opt_k1.py` | dev | select_scan_index | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.pow arith.sub cast.explicit cmp.compare construct.arange construct.full dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.axis red.maxmin select.where |
| `suite/dev/argmin_split_K_kernel_merged.py` | dev | select_scan_index | 6 | (17); (104) | float32, float16, bfloat16 | arith.add arith.mul arith.pow arith.sub cast.explicit cmp.compare construct.arange construct.full dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.axis red.maxmin select.where |
| `suite/dev/argmin_tiled_kernel.py` | dev | select_scan_index | 9 | (4,128,128); (3,17,100); (1,1,1) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange construct.full construct.zeros dtype.int flow.dynamic_range flow.loop index.multi_offset logic.bitwise mem.alignment_hint mem.cache_hint mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.argmaxmin red.axis red.maxmin select.where |
| `suite/dev/asinh_kernel.py` | dev | elementwise_reduce | 6 | (17); (118) | float32, float16, bfloat16 | arith.add arith.mul arith.neg cast.explicit cast.to_fp32 cmp.compare construct.arange flow.if math.abs math.sqrt_rsqrt math.transcendental mem.load mem.masked_load mem.masked_store mem.store pat.masked_both select.where |
| `suite/dev/atanh_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.if math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/atomic_bitmap.py` | dev | elementwise_reduce | 3 | (16,128); (5,32); (1,4) | int32 | arith.add arith.mod arith.mul cast.explicit cmp.compare construct.arange construct.full dtype.int mem.atomic mem.load mem.store misc.barrier red.axis red.sum |
| `suite/dev/avg_pool1d_kernel_optimized.py` | dev | conv_pool | 3 | (1,1,8) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both shape.reshape |
| `suite/dev/backends__ascend__ops__grpo_loss__selective_log_softmax_kernel.py` | dev | softmax_xent | 6 | (2,7,17); (3,7,17) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.if flow.loop flow.static_range flow.tl_range math.clamp math.transcendental mem.load mem.masked_load mem.other mem.store pat.persistent_reduce pat.reduce_broadcast pat.softmax red.maxmin red.sum |
| `suite/dev/binary_cross_entropy_elementwise_kernel.py` | dev | softmax_xent | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange math.clamp math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/bincount_kernel.py` | dev | elementwise_reduce | 2 | (17,7); (97,33) | int32 | arith.add arith.mul cmp.compare construct.arange mem.atomic mem.load mem.masked_load mem.other |
| `suite/dev/bitcast.py` | dev | elementwise_reduce | 1 | (97) | float32 | arith.add arith.mul cast.explicit cmp.compare construct.arange dtype.int dtype.uint mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/blackman_window_kernel.py` | dev | elementwise_reduce | 6 | (17); (122) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int flow.if math.transcendental mem.masked_store mem.store |
| `suite/dev/blocked_jacobi_apply_v_kernel.py` | dev | elementwise_reduce | 3 | (17) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both select.where |
| `suite/dev/blocked_jacobi_pair_svals_kernel.py` | dev | elementwise_reduce | 3 | (17) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.neg arith.sub cmp.compare construct.arange logic.bitwise math.abs math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.normalize pat.reduce_broadcast red.sum select.where |
| `suite/dev/blocked_jacobi_rank_kernel.py` | dev | elementwise_reduce | 6 | (17); (5,6) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.full dtype.int flow.while logic.bitwise mem.load mem.store |
| `suite/dev/bn_inc_and_write_momentum_kernel.py` | dev | elementwise_reduce | 6 | (0); (5) | float32, float16, bfloat16 | arith.add arith.div cast.explicit cast.to_fp32 flow.if math.clamp mem.atomic mem.store |
| `suite/dev/bucketize_kernel.py` | dev | select_scan_index | 6 | (17); (126) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cmp.compare construct.arange construct.full construct.zeros dtype.int flow.dynamic_range flow.if flow.loop math.clamp mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both select.where |
| `suite/dev/calculate_batch_indices_kernel.py` | dev | elementwise_reduce | 2 | (17); (5,3,2,2) | int64 | arith.add arith.div arith.mod arith.mul cmp.compare construct.arange mem.masked_store mem.store |
| `suite/dev/cholesky_kernel.py` | dev | elementwise_reduce | 2 | (17); (4,3) | float32 | arith.add arith.div arith.mul arith.sub cast.explicit cmp.compare construct.zeros dtype.int flow.dynamic_range flow.if flow.loop math.sqrt_rsqrt mem.load mem.store |
| `suite/dev/cholesky_upper_kernel.py` | dev | elementwise_reduce | 6 | (17); (24,5) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full dtype.int flow.while logic.bitwise math.abs math.clamp math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both red.axis red.maxmin red.sum select.where |
| `suite/dev/chunk_abc_fwd_kernel_intra_K.py` | dev | linear_attention | 6 | (2,2,17,9,8,4); (1,3,33,13,16,4) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dot.matmul dtype.int flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both pat.matmul_epilogue select.where shape.reshape |
| `suite/dev/chunk_gated_delta_product_fwd_kernel_h_blockdim64.py` | dev | linear_attention | 9 | (2,2,16,7,9,4,2); (4,2,16,7,9,4,2); (1,3,32,11,13,8,2) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dot.matmul dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset index.rank2 logic.bitwise math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both pat.matmul_epilogue select.where shape.reshape |
| `suite/dev/chunk_gdn2_fwd_kernel_inter_solve_fused.py` | dev | linear_attention | 6 | (17); (3,17,2,7) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dot.matmul dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise logic.bool math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.dot_reduce pat.k_loop pat.masked_both pat.matmul_epilogue pat.persistent_reduce pat.reduce_broadcast red.axis red.sum select.where shape.reshape shape.trans |
| `suite/dev/chunk_gdn2_fwd_kernel_intra_sub_chunk.py` | dev | linear_attention | 6 | (2,17,3,7,8,4); (3,17,3,7,8,4) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full dot.matmul dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset index.rank2 logic.bitwise math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store misc.barrier pat.dot_reduce pat.k_loop pat.masked_both pat.matmul_epilogue pat.persistent_reduce pat.reduce_broadcast red.axis red.sum select.where shape.reshape shape.trans |
| `suite/dev/chunk_gdn2_fwd_kernel_intra_token_parallel.py` | dev | linear_attention | 6 | (2,17,5,7,8,4); (3,17,5,7,8,4) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.axis red.sum select.where |
| `suite/dev/chunk_generalized_iplr_delta_rule_fwd_kernel_o.py` | dev | linear_attention | 6 | (17); (6,17,2,7,6) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dot.matmul dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset index.rank3plus logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both pat.matmul_epilogue select.where shape.reshape |
| `suite/dev/chunk_gla_fwd_A_kernel_intra_sub_intra_merge.py` | dev | linear_attention | 6 | (2,17,3,8,4,3); (3,33,5,16,4,5) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/chunk_hgrn_fwd_kernel_h.py` | dev | linear_attention | 6 | (2,17,13,8); (3,33,29,16) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop logic.bitwise math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/chunk_hgrn_fwd_kernel_o.py` | dev | linear_attention | 6 | (2,17,13,8); (6,17,13,8) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store misc.barrier pat.masked_both |
| `suite/dev/chunk_transform_qk_fwd_kernel.py` | dev | linear_attention | 6 | (4,17,7,9,8); (6,33,11,13,16) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange dot.matmul dtype.int flow.if index.multi_offset index.rank2 logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.matmul_epilogue select.where shape.reshape shape.trans |
| `suite/dev/complete_zero_projection_kernel.py` | dev | elementwise_reduce | 6 | (17); (4,8,4) | float32, float16, bfloat16 | arith.add arith.mul cmp.compare construct.arange mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both select.where |
| `suite/dev/complex_pack.py` | dev | elementwise_reduce | 6 | (128); (1) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cast.to_fp32 construct.arange index.multi_offset mem.load mem.store shape.reshape shape.split_join shape.trans |
| `suite/dev/complex_svd_pick_factor_kernel.py` | dev | elementwise_reduce | 3 | (17) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul cmp.compare construct.arange mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/complex_svd_pick_orthonormal_v_kernel.py` | dev | norm | 3 | (17) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cmp.compare construct.arange flow.loop flow.static_range index.multi_offset logic.bitwise math.clamp math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.axis red.sum select.where |
| `suite/dev/complex_svd_project_u_kernel.py` | dev | elementwise_reduce | 6 | (17); (4,6,5,4) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange construct.zeros flow.loop flow.static_range mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both select.where |
| `suite/dev/complex_to_real_embedding_kernel.py` | dev | elementwise_reduce | 6 | (17); (4,5,4) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.sub cmp.compare construct.arange logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both select.where |
| `suite/dev/control_flow.py` | dev | elementwise_reduce | 3 | (128) | float32, float16, bfloat16 | arith.add arith.mul arith.neg cast.explicit cast.to_fp32 cmp.compare construct.arange flow.if flow.loop flow.static_range mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/conv1x1_pool_fc_kernel.py` | dev | conv_pool | 9 | (2,128,128,128,10); (6,128,128,128,10); (1,128,128,128,10) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.if_pid flow.loop index.multi_offset logic.bitwise math.clamp mem.atomic mem.load mem.masked_load mem.other pat.dot_reduce pat.k_loop pat.matmul_epilogue pat.persistent_reduce red.axis red.sum shape.expand |
| `suite/dev/conv_transpose2d_scatter_init_kernel.py` | dev | conv_pool | 6 | (17); (4,3,2) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros flow.if mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/copy_last_chunk_kernel.py` | dev | linear_attention | 9 | (17); (97); (3,17,1,6,5) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cmp.compare construct.arange dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/count_nonzero_combin_kernel.py` | dev | select_scan_index | 6 | (1,17); (8,97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange dtype.int logic.bitwise mem.load mem.masked_load mem.other mem.store red.sum |
| `suite/dev/count_nonzero_combin_kernel_1.py` | dev | select_scan_index | 2 | (1,3); (8,17) | int64 | arith.add arith.mul cast.explicit cmp.compare construct.arange construct.full dtype.int flow.dynamic_range flow.loop logic.bitwise mem.load mem.masked_load mem.other mem.store pat.persistent_reduce red.sum |
| `suite/dev/count_nonzero_kernel_1.py` | dev | select_scan_index | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange dtype.int mem.atomic mem.load mem.masked_load mem.other red.axis red.sum |
| `suite/dev/count_valid_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full dtype.int flow.loop flow.tl_range logic.bitwise mem.load mem.masked_load mem.other mem.store pat.persistent_reduce red.axis red.sum |
| `suite/dev/cross_entropy_forward_kernel_plain.py` | dev | softmax_xent | 6 | (1,17); (13,17) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int flow.dynamic_range flow.if flow.loop math.clamp math.transcendental mem.load mem.masked_load mem.other mem.store pat.persistent_reduce pat.reduce_broadcast red.maxmin red.sum |
| `suite/dev/cross_entropy_kernel.py` | dev | softmax_xent | 6 | (1,17); (17,97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bool math.clamp math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store misc.barrier pat.masked_both pat.persistent_reduce pat.reduce_broadcast pat.softmax red.maxmin red.sum select.where |
| `suite/dev/csr_value_index_kernel.py` | dev | select_scan_index | 2 | (17); (3,3,8) | int64 | arith.add arith.div arith.mod arith.mul cast.explicit cmp.compare construct.arange dtype.int flow.dynamic_range flow.loop mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/cumprod_dim1_grouped_mixed_kernel.py` | dev | select_scan_index | 3 | (1,1) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cmp.compare construct.arange construct.full flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise math.clamp math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both red.scan select.where |
| `suite/dev/cumprod_dim1_kernel.py` | dev | select_scan_index | 9 | (64,128); (17,100); (1,1) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full flow.dynamic_range flow.if flow.loop mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both select.where |
| `suite/dev/cumprod_dim1_kernel_log2exp2_early.py` | dev | select_scan_index | 3 | (64,128); (17,100); (1,1) | float32 | arith.add arith.mul arith.sub cmp.compare construct.arange construct.zeros flow.dynamic_range flow.if flow.loop logic.bitwise math.clamp math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.axis red.scan red.sum |
| `suite/dev/cyclic_jacobi_init_a_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange flow.if mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/cyclic_jacobi_norm_kernel.py` | dev | norm | 1 | (17) | float32 | arith.add arith.mul cmp.compare construct.arange math.sqrt_rsqrt mem.load mem.masked_load mem.other mem.store red.sum |
| `suite/dev/cyclic_jacobi_pair_kernel.py` | dev | elementwise_reduce | 3 | (17) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.neg arith.sub cmp.compare construct.arange index.multi_offset logic.bitwise math.abs math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.normalize pat.reduce_broadcast red.sum select.where |
| `suite/dev/deconv3d_fwd_kernel.py` | dev | conv_pool | 6 | (1,4,8,8,8); (1,1,1,1,1) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full construct.zeros dtype.int flow.if flow.loop flow.static_range flow.while index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both select.where |
| `suite/dev/deconv3d_leaky_pool.py` | dev | conv_pool | 3 | (1,2,3,2,2,2); (2,2,3,2,2,2); (1,3,5,3,2,2) | float32 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset logic.bitwise mem.atomic mem.load mem.masked_load mem.other select.where |
| `suite/dev/destindex_copy.py` | dev | select_scan_index | 6 | (8,16); (4,32) | float32, float16, bfloat16 | arith.add arith.mul construct.arange mem.load mem.store |
| `suite/dev/diag_scale_kernel.py` | dev | elementwise_reduce | 9 | (128,128); (97,100); (1,1) | float32, float16, bfloat16 | arith.add arith.mul flow.dynamic_range flow.loop mem.blockptr mem.boundary_check mem.load mem.padding mem.store pat.blockptr_boundary |
| `suite/dev/diff_kernel_1d.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cmp.compare construct.arange dtype.int mem.load mem.store |
| `suite/dev/diff_kernel_2d.py` | dev | elementwise_reduce | 6 | (3,17); (5,33) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cmp.compare construct.arange dtype.int index.multi_offset logic.bitwise mem.load mem.store |
| `suite/dev/dist_l2_single_kernel.py` | dev | elementwise_reduce | 6 | (17); (103) | float16, float32, bfloat16 | arith.add arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros flow.dynamic_range flow.if flow.loop math.sqrt_rsqrt mem.load mem.masked_load mem.other mem.store pat.persistent_reduce pat.reduce_broadcast red.sum select.where |
| `suite/dev/dist_reduce_kernel.py` | dev | elementwise_reduce | 2 | (1); (33) | float32 | arith.add cmp.compare construct.arange math.sqrt_rsqrt mem.load mem.masked_load mem.other mem.store red.sum |
| `suite/dev/dot__dot_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int mem.load mem.masked_load mem.other mem.store red.sum |
| `suite/dev/dropout_softmax_fwd_kernel.py` | dev | softmax_xent | 6 | (33,100); (1,1) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full dtype.int dtype.uint flow.if flow.loop flow.static_range index.multi_offset math.clamp math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store misc.rng pat.masked_both pat.persistent_reduce pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where |
| `suite/dev/embedding_kernel.py` | dev | elementwise_reduce | 6 | (17,7,11); (97,13,19) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange dtype.int index.multi_offset mem.load mem.other mem.store |
| `suite/dev/epilogue_kernel.py` | dev | elementwise_reduce | 6 | (64,128); (128,128) | float32, float16, bfloat16 | arith.add arith.mod arith.mul construct.arange math.clamp math.transcendental mem.load mem.store |
| `suite/dev/eye_kernel.py` | dev | elementwise_reduce | 6 | (7,9); (17,13) | float32, float16, bfloat16 | arith.add arith.mul cmp.compare construct.arange index.multi_offset logic.bitwise mem.masked_store mem.store select.where |
| `suite/dev/f_init_recurrence_kernel.py` | dev | elementwise_reduce | 6 | (1,16,1,128); (1,16,1,100) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.neg arith.sub cmp.compare flow.if flow.loop flow.static_range math.abs math.transcendental mem.atomic mem.load |
| `suite/dev/fht_kernel_1d_native.py` | dev | elementwise_reduce | 6 | (17); (51,16) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cmp.compare construct.arange flow.if flow.loop flow.static_range logic.bitwise mem.cache_hint mem.load mem.store shape.reshape shape.split_join shape.trans |
| `suite/dev/fht_kernel_256_1d_native.py` | dev | elementwise_reduce | 3 | (17) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cmp.compare construct.arange flow.if mem.cache_hint mem.load mem.store shape.reshape shape.split_join shape.trans |
| `suite/dev/fht_kernel_256_4row_native.py` | dev | elementwise_reduce | 3 | (17) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cmp.compare construct.arange flow.if mem.cache_hint mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both shape.reshape shape.split_join shape.trans |
| `suite/dev/final_mean_kernel.py` | dev | elementwise_reduce | 6 | (128); (1) | float32, float16, bfloat16 | arith.div cast.explicit mem.load mem.store |
| `suite/dev/finalize_mean_tanh.py` | dev | elementwise_reduce | 9 | (128); (97); (1) | float32, float16, bfloat16 | arith.add arith.mul arith.sub math.transcendental mem.load mem.store |
| `suite/dev/finalize_stats_kernel.py` | dev | elementwise_reduce | 6 | (128); (97); (1) | float32, bfloat16 | arith.add arith.div arith.mul arith.sub construct.full math.clamp math.sqrt_rsqrt mem.load mem.store |
| `suite/dev/flash_varlen_fwd_kernel.py` | dev | attention | 6 | (2,17,19,4,2,16); (3,17,19,6,2,32) | float16, bfloat16, float32 | arith.add arith.div arith.mod arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full construct.zeros dot.matmul dot.out_dtype dtype.int dtype.uint flow.if flow.loop flow.static_range flow.tl_range index.multi_offset logic.bitwise logic.bool math.abs math.clamp math.transcendental mem.alignment_hint mem.blockptr mem.boundary_check mem.load mem.masked_load mem.masked_store mem.other mem.store pat.blockptr_boundary pat.dot_reduce pat.k_loop pat.masked_both pat.matmul_epilogue pat.persistent_reduce pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where shape.reshape shape.split_join shape.trans |
| `suite/dev/flat_radix_init_kernel.py` | dev | elementwise_reduce | 2 | (17); (97) | int32 | arith.add mem.store select.where |
| `suite/dev/flat_radix_init_rank_kernel.py` | dev | elementwise_reduce | 2 | (17); (97) | int32 | arith.add arith.div mem.load mem.store |
| `suite/dev/flat_radix_store_result_kernel.py` | dev | elementwise_reduce | 6 | (17); (114) | float32, float16, bfloat16 | arith.add cmp.compare flow.if mem.load mem.masked_load mem.other mem.store |
| `suite/dev/fliplr_contiguous_kernel.py` | dev | elementwise_reduce | 6 | (2,3,5); (3,3,5) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cmp.compare construct.arange dtype.int mem.load mem.masked_load mem.masked_store mem.store pat.masked_both |
| `suite/dev/fliplr_strided_kernel.py` | dev | elementwise_reduce | 6 | (2,3,5); (3,7,4) | float32, float16, bfloat16 | arith.add arith.mod arith.mul arith.neg arith.sub cast.explicit cmp.compare construct.arange construct.zeros dtype.int flow.loop flow.static_range mem.load mem.masked_load mem.masked_store mem.store pat.masked_both select.where |
| `suite/dev/floor_kernel.py` | dev | elementwise_reduce | 2 | (17); (115) | float32 | arith.add arith.mul cast.explicit cmp.compare construct.arange flow.if math.round mem.load mem.masked_load mem.masked_store mem.store pat.masked_both |
| `suite/dev/forward_pass_chunks.py` | dev | linear_attention | 6 | (2,17,3,13); (4,65,5,61) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop flow.tl_range math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/frobenius_norm_persistent_two_phase_kernel.py` | dev | norm | 3 | (128); (100); (1) | float32 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros flow.dynamic_range flow.if flow.loop flow.while math.sqrt_rsqrt mem.alignment_hint mem.atomic mem.cache_hint mem.load mem.masked_load mem.other mem.store pat.normalize pat.persistent_reduce pat.reduce_broadcast red.axis red.sum |
| `suite/dev/fused_activation.py` | dev | elementwise_reduce | 2 | (128); (99) | float32 | arith.add arith.mod arith.mul cmp.compare construct.arange flow.if math.clamp math.transcendental mem.cache_hint mem.load mem.store |
| `suite/dev/fused_bn_relu_kernel.py` | dev | elementwise_reduce | 2 | (2,3,7); (3,5,11) | float32 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.if_pid index.multi_offset logic.bool math.clamp math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/fused_conv3d_kernel.py` | dev | conv_pool | 9 | (1,8,8,8,8,16,3,3,3); (2,4,7,6,5,6,2,2,2); (1,4,8,8,8,32,3,3,3) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.neg cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop flow.static_range index.multi_offset logic.bitwise math.clamp math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both select.where shape.reshape |
| `suite/dev/fused_conv3d_kernel_2.py` | dev | conv_pool | 9 | (1,8,8,8,8,16,3,3,3); (2,4,7,6,5,6,2,2,2); (1,2,3,3,3,8,1,1,1) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dot.matmul dot.out_dtype flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise math.clamp math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both pat.matmul_epilogue select.where shape.trans |
| `suite/dev/fused_exponential_kernel_f32_unroll8.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full dtype.int dtype.uint flow.if index.multi_offset logic.bitwise logic.bool math.clamp math.transcendental mem.masked_store mem.store misc.rng select.where |
| `suite/dev/fused_fill_dropout_kernel.py` | dev | elementwise_reduce | 6 | (128); (1) | float32, float16, bfloat16 | arith.add arith.mul cmp.compare construct.arange mem.masked_store mem.store misc.rng select.where |
| `suite/dev/fused_gemm_gn_min_kernel.py` | dev | matmul | 2 | (64,128,128); (128,128,128) | float32 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop hint.static_assert index.multi_offset math.sqrt_rsqrt mem.atomic mem.load mem.masked_load pat.dot_reduce pat.k_loop pat.normalize pat.persistent_reduce pat.reduce_broadcast red.axis red.maxmin red.sum shape.reshape |
| `suite/dev/fused_gemm_gn_min_kernel_2.py` | dev | matmul | 2 | (64,128,128); (37,96,128) | float32 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.clamp math.sqrt_rsqrt mem.atomic mem.load mem.masked_load mem.other pat.dot_reduce pat.k_loop pat.matmul_epilogue pat.normalize pat.persistent_reduce pat.reduce_broadcast red.axis red.maxmin red.sum shape.broadcast shape.reshape |
| `suite/dev/fused_grouped_gate_kernel.py` | dev | elementwise_reduce | 6 | (32,64); (17,32) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.sub cmp.compare construct.arange construct.zeros flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise logic.bool math.transcendental mem.load mem.masked_load mem.other mem.store pat.persistent_reduce pat.reduce_broadcast pat.softmax red.argmaxmin red.axis red.maxmin red.sum select.where shape.broadcast shape.reshape |
| `suite/dev/fused_l1_norm_and_divide_kernel_2d6d4854.py` | dev | norm | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mul cmp.compare construct.arange flow.while math.abs mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both red.axis red.sum |
| `suite/dev/fused_l1_norm_kernel_76761630.py` | dev | norm | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cmp.compare construct.arange dtype.int flow.dynamic_range flow.loop index.multi_offset math.abs mem.cache_hint mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.sum |
| `suite/dev/fused_l1_norm_kernel_e5b6ba01.py` | dev | norm | 6 | (16); (32) | float32, float16, bfloat16 | arith.add arith.div arith.mul cmp.compare construct.arange flow.loop flow.tl_range index.multi_offset math.abs mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.sum tune.loop_pragma |
| `suite/dev/fused_l1_normalize_kernel_765f90f7.py` | dev | norm | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mul cmp.compare construct.arange construct.full construct.zeros flow.dynamic_range flow.loop index.multi_offset math.abs mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.axis red.sum |
| `suite/dev/fused_l1_normalize_kernel_823e70aa.py` | dev | norm | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mul cmp.compare construct.arange construct.zeros flow.loop flow.tl_range index.multi_offset math.abs mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.axis red.sum |
| `suite/dev/fused_layernorm_triton.py` | dev | norm | 6 | (4,64); (7,67) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.normalize pat.reduce_broadcast red.axis red.sum select.where tune.autotune |
| `suite/dev/fused_lstm_layer_kernel.py` | dev | elementwise_reduce | 3 | (2,8,32); (4,8,32); (1,1,8) | float32 | arith.add arith.mul arith.sub construct.arange flow.dynamic_range flow.if flow.loop math.transcendental mem.load mem.store misc.barrier |
| `suite/dev/fused_max_bincount_kernel.py` | dev | elementwise_reduce | 2 | (17,7); (97,33) | int32 | arith.add arith.mul cmp.compare construct.arange logic.bitwise mem.atomic mem.load mem.masked_load mem.other red.axis red.maxmin |
| `suite/dev/fused_pool_hardtanh_mean_flat.py` | dev | conv_pool | 9 | (8,16,64,64); (2,3,32,32); (1,1,16,16) | float32, float16, bfloat16 | arith.add arith.mul construct.arange flow.dynamic_range flow.loop index.multi_offset math.clamp mem.load mem.store pat.persistent_reduce red.axis red.maxmin red.sum shape.reshape |
| `suite/dev/fused_pool_reduce_kernel.py` | dev | conv_pool | 6 | (8,16,64,64); (2,3,30,34) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.neg arith.sub cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.clamp math.transcendental mem.load mem.masked_load mem.other mem.store pat.persistent_reduce pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where shape.reshape |
| `suite/dev/fused_recurrent_fwd_kernel.py` | dev | linear_attention | 6 | (2,17,3,7,9); (9,17,3,7,9) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset index.rank2 logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.axis red.sum |
| `suite/dev/fused_recurrent_gdn2_fwd_kernel.py` | dev | linear_attention | 9 | (2,9,2,4,5,7); (2,18,2,4,5,7); (1,17,3,6,8,9) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dtype.int flow.if flow.loop flow.tl_range index.multi_offset logic.bitwise logic.bool math.sqrt_rsqrt math.transcendental mem.cache_hint mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.normalize pat.persistent_reduce pat.reduce_broadcast red.axis red.sum select.where tune.loop_pragma |
| `suite/dev/fused_recurrent_gsa_inference_kernel.py` | dev | linear_attention | 6 | (4,3,7,9,5); (6,4,11,13,7) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where |
| `suite/dev/fused_recurrent_hgrn_fwd_kernel.py` | dev | linear_attention | 6 | (3,17,13); (2,33,29) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/fused_recurrent_rwkv6.py` | dev | linear_attention | 3 | (2,2,16,32,32); (2,2,16,64,32); (1,2,32,32,32) | float32 | arith.add arith.mul arith.neg construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset math.transcendental mem.load mem.store pat.persistent_reduce red.axis red.sum |
| `suite/dev/fused_reduction_kernel_stage2.py` | dev | elementwise_reduce | 6 | (128,128); (1,1) | float32, float16, bfloat16 | arith.add arith.mul construct.arange math.clamp mem.load mem.store red.sum |
| `suite/dev/fused_stage1_kernel.py` | dev | elementwise_reduce | 9 | (32,128); (17,100); (1,1) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.neg arith.sub cast.explicit cmp.compare construct.arange dtype.int math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store misc.rng pat.masked_both pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where |
| `suite/dev/gdn_gate_fwd_kernel.py` | dev | linear_attention | 6 | (17,5,8); (19,5,8) | float32, float16, bfloat16 | arith.add arith.mul arith.neg cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int flow.if math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both select.where |
| `suite/dev/geglu_forward_kernel_flat.py` | dev | elementwise_reduce | 6 | (3,17); (5,97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.loop flow.tl_range math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/geglu_tanh_forward_kernel.py` | dev | elementwise_reduce | 6 | (3,17); (28,17) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/gelu_kernel_nomask.py` | dev | elementwise_reduce | 6 | (128); (32) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg construct.arange math.transcendental mem.load mem.store |
| `suite/dev/gelu_min.py` | dev | elementwise_reduce | 2 | (128); (1) | float32 | arith.add arith.mul cmp.compare construct.arange construct.full flow.dynamic_range flow.loop math.clamp math.transcendental mem.load mem.masked_load mem.other mem.store pat.persistent_reduce red.axis red.maxmin select.where |
| `suite/dev/gemm_rowstats_group_tc_kernel.py` | dev | matmul | 2 | (64,128,128); (128,128,128) | float32 | arith.add arith.mul arith.neg cast.explicit cast.to_fp16 cmp.compare construct.arange construct.full construct.zeros dot.matmul flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise math.clamp mem.atomic mem.load mem.masked_load mem.other pat.dot_reduce pat.k_loop pat.matmul_epilogue pat.persistent_reduce red.axis red.maxmin red.sum select.where |
| `suite/dev/gemm_smallk_kernel_5ee47e3f.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.mul cmp.compare construct.arange dot.matmul index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/generalized_delta_rule__dplr__wy_fast_fwd__wu_fwd_kernel.py` | dev | linear_attention | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange dot.matmul dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both pat.matmul_epilogue select.where shape.reshape |
| `suite/dev/gn_finalize_kernel.py` | dev | elementwise_reduce | 9 | (128,8); (7,3); (1,1) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub math.sqrt_rsqrt mem.load mem.store |
| `suite/dev/gn_finalize_kernel_2.py` | dev | elementwise_reduce | 9 | (128); (17); (1) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub flow.loop flow.tl_range math.sqrt_rsqrt mem.load mem.store |
| `suite/dev/gqa.py` | dev | attention | 3 | (2,4,2,32,32); (2,4,2,64,32); (1,4,2,64,32) | float32 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange construct.full construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset math.clamp math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.dot_reduce pat.k_loop pat.masked_both pat.matmul_epilogue pat.persistent_reduce pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where shape.trans |
| `suite/dev/gram_jacobi_sym_kernel.py` | dev | elementwise_reduce | 6 | (17); (30,5) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.while index.multi_offset logic.bitwise math.abs math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.normalize pat.reduce_broadcast red.axis red.sum select.where |
| `suite/dev/group_norm_forward_affine_kernel.py` | dev | norm | 6 | (3,2,4,5); (5,3,2,7) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.loop flow.tl_range index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/group_norm_forward_single_task_kernel.py` | dev | norm | 6 | (3,2,4,5); (6,2,4,5) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.clamp math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.normalize pat.persistent_reduce pat.reduce_broadcast red.axis red.sum |
| `suite/dev/group_norm_forward_stats_kernel.py` | dev | norm | 6 | (3,2,4,5); (7,2,4,5) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros flow.loop flow.tl_range index.multi_offset logic.bitwise math.clamp math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.normalize pat.persistent_reduce pat.reduce_broadcast red.axis red.sum |
| `suite/dev/grouped_gemm_kernel.py` | dev | matmul | 6 | (3,17,19,13); (4,33,35,21) | bfloat16, float32, float16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cmp.compare construct.zeros dot.acc dot.matmul flow.dynamic_range flow.if flow.loop flow.tl_range logic.bool math.clamp mem.blockptr mem.boundary_check mem.load mem.store pat.blockptr_boundary pat.k_loop pat.matmul_epilogue |
| `suite/dev/grouped_mm_kernel.py` | dev | matmul | 6 | (3,23,19,17); (4,67,35,29) | bfloat16, float32, float16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cmp.compare construct.arange construct.zeros dot.acc dot.matmul dtype.int flow.if flow.loop flow.tl_range index.multi_offset logic.bitwise logic.bool math.clamp mem.blockptr mem.boundary_check mem.load mem.masked_store mem.store pat.blockptr_boundary pat.k_loop pat.matmul_epilogue |
| `suite/dev/grouped_strided_sum.py` | dev | elementwise_reduce | 9 | (3,0,5); (6,0,5); (3,0,10) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros flow.while index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both red.axis red.sum |
| `suite/dev/grpo_loss__selective_log_softmax_kernel.py` | dev | softmax_xent | 6 | (2,7,17); (3,11,67) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int flow.dynamic_range flow.if flow.loop math.clamp math.transcendental mem.load mem.masked_load mem.other mem.store pat.persistent_reduce pat.reduce_broadcast pat.softmax red.maxmin red.sum |
| `suite/dev/hardsigmoid_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange math.clamp mem.load mem.masked_load mem.masked_store mem.store pat.masked_both |
| `suite/dev/hardsigmoid_kernel_2.py` | dev | elementwise_reduce | 8 | (128); (97) | int16, float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cast.to_fp16 cast.to_fp32 cmp.compare construct.arange dtype.int flow.if math.clamp mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/hidden__argmax_kernel_2.py` | dev | select_scan_index | 6 | (17); (126) | float32, float16, bfloat16 | arith.add arith.mul arith.neg arith.pow arith.sub cmp.compare construct.arange flow.if mem.load mem.masked_load mem.other mem.store red.argmaxmin red.axis |
| `suite/dev/hidden__prepare_wy_repr_fwd_kernel_chunk32.py` | dev | linear_attention | 4 | (2,33,3,32); (3,33,3,32) | float32, float16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cmp.compare construct.arange dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.axis red.sum select.where |
| `suite/dev/hidden__rms_norm_loop_kernel.py` | dev | norm | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bool math.sqrt_rsqrt mem.cache_hint mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.normalize pat.persistent_reduce pat.reduce_broadcast red.sum |
| `suite/dev/huber_loss_element_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cmp.compare construct.arange math.abs mem.load mem.masked_load mem.masked_store mem.store pat.masked_both select.where |
| `suite/dev/huber_loss_fused_kernel.py` | dev | elementwise_reduce | 6 | (17); (101) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop math.abs mem.load mem.masked_load mem.other mem.store pat.persistent_reduce pat.reduce_broadcast red.axis red.sum select.where |
| `suite/dev/huber_loss_reduce_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange math.abs mem.load mem.masked_load mem.other mem.store pat.reduce_broadcast red.axis red.sum select.where |
| `suite/dev/hypot_inplace_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.store pat.masked_both |
| `suite/dev/igamma_kernel.py` | dev | elementwise_reduce | 6 | (17); (118) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.dynamic_range flow.loop math.abs math.clamp math.transcendental mem.load mem.masked_load mem.masked_store mem.store pat.masked_both select.where |
| `suite/dev/implicit_conv2d.py` | dev | conv_pool | 9 | (1,4,5,7,7); (2,8,6,5,19); (1,4,5,14,7) | float16, float32, bfloat16 | arith.add arith.div arith.mod arith.mul cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both shape.broadcast |
| `suite/dev/index_select_kernel.py` | dev | select_scan_index | 6 | (17); (113) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange dtype.int index.multi_offset logic.bitwise logic.bool mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/init_minmax.py` | dev | elementwise_reduce | 6 | (17); (120) | float32, float16, bfloat16 | arith.add arith.mul cmp.compare construct.arange construct.full mem.masked_store mem.store |
| `suite/dev/int8_quantization.py` | dev | quant | 6 | (8,16); (4,8) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.pow arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int index.multi_offset math.abs mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both red.maxmin select.where |
| `suite/dev/jagged_to_padded_dense_forward_kernel.py` | dev | elementwise_reduce | 6 | (17); (8,16,11,9,8,7,13,10,15,12) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cmp.compare construct.arange dtype.int flow.if flow.loop flow.tl_range index.multi_offset mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/kda_gate_fwd_kernel.py` | dev | linear_attention | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.neg cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int flow.if index.multi_offset logic.bitwise logic.bool math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both select.where |
| `suite/dev/kernel_1.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int flow.if mem.load mem.masked_load mem.other mem.store pat.reduce_broadcast red.sum |
| `suite/dev/kldiv_kernel_forward.py` | dev | elementwise_reduce | 6 | (3,17); (5,97) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cmp.compare construct.arange dtype.int flow.dynamic_range flow.if flow.loop logic.bool math.clamp math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.axis red.sum |
| `suite/dev/kv_cache_write.py` | dev | elementwise_reduce | 9 | (6,4,2,8); (12,8,4,16); (3,2,1,4) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul construct.arange mem.load mem.store |
| `suite/dev/l1_fused_aligned_unroll2_kernel_9da16ab1.py` | dev | elementwise_reduce | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.neg arith.sub cast.explicit cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop logic.bitwise math.abs math.clamp mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.axis red.sum |
| `suite/dev/l1_fused_kernel_3079c682.py` | dev | elementwise_reduce | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop math.abs mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.sum |
| `suite/dev/l1_fused_kernel_64a2cf40.py` | dev | elementwise_reduce | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset math.abs mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.sum |
| `suite/dev/l1_fused_opt_kernel_770afbaa.py` | dev | elementwise_reduce | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.sub cast.explicit cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise math.abs mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.sum |
| `suite/dev/l1_fused_row_kernel_c376727a.py` | dev | elementwise_reduce | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.loop index.multi_offset math.abs mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.axis red.sum select.where |
| `suite/dev/l1_norm_block_fused_kernel_c12b32af.py` | dev | norm | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.abs mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.axis red.sum |
| `suite/dev/l1_norm_fused_blockrows_kernel_d070b0d9.py` | dev | norm | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mul cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.abs mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.axis red.sum select.where |
| `suite/dev/l1_norm_fused_hyper_kernel_c1fb1344.py` | dev | norm | 2 | (128); (127) | float32 | arith.add arith.div arith.mul arith.neg arith.sub cast.explicit cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop logic.bitwise math.abs math.clamp mem.alignment_hint mem.cache_hint mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.sum |
| `suite/dev/l1_norm_fused_kernel_16977248.py` | dev | norm | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mul cmp.compare construct.arange flow.dynamic_range flow.if_pid flow.loop math.abs mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.axis red.sum |
| `suite/dev/l1_norm_fused_kernel_2cb0f555.py` | dev | norm | 2 | (128); (127) | float32 | arith.add arith.div arith.mul arith.neg arith.sub cast.explicit cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop logic.bitwise math.abs mem.alignment_hint mem.cache_hint mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.sum select.where |
| `suite/dev/l1_norm_fused_kernel_7f6ce49c.py` | dev | norm | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mul cmp.compare construct.arange construct.zeros flow.dynamic_range flow.if flow.loop index.multi_offset math.abs mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.axis red.sum |
| `suite/dev/l1_norm_fused_kernel_a430b801.py` | dev | norm | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange flow.dynamic_range flow.loop index.multi_offset math.abs mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.sum |
| `suite/dev/layer_norm_forward_row.py` | dev | norm | 6 | (3,16); (5,128) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 construct.arange flow.loop flow.tl_range math.sqrt_rsqrt mem.load mem.store pat.normalize pat.persistent_reduce pat.reduce_broadcast red.axis red.sum |
| `suite/dev/layer_norm_forward_tiled.py` | dev | norm | 6 | (3,17); (31,17) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.dynamic_range flow.loop flow.tl_range math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.normalize pat.persistent_reduce pat.reduce_broadcast red.sum select.where |
| `suite/dev/ldl_factor_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 flow.dynamic_range flow.loop mem.load mem.store |
| `suite/dev/ldl_init_info_kernel.py` | dev | elementwise_reduce | 1 | (17) | int32 | mem.store |
| `suite/dev/ldl_init_pivots_kernel.py` | dev | elementwise_reduce | 2 | (17); (97) | int32 | arith.add arith.div arith.mod arith.mul cmp.compare flow.if mem.store |
| `suite/dev/leaky_relu_kernel_strided.py` | dev | elementwise_reduce | 9 | (64,128); (33,65); (1,1) | float32, float16, bfloat16 | arith.mul cmp.compare mem.blockptr mem.boundary_check mem.load mem.padding mem.store pat.blockptr_boundary select.where |
| `suite/dev/linalg_cross_complex_contiguous_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cmp.compare construct.arange index.multi_offset mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both select.where shape.reshape shape.split_join |
| `suite/dev/linalg_cross_real_dim1_3d_kernel.py` | dev | elementwise_reduce | 6 | (17); (125) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.if logic.bool mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/linalg_cross_real_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.if logic.bool mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/linalg_cross_real_lastdim_broadcast_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mod arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.if logic.bool mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/linear_dropout_softmax_kernel.py` | dev | softmax_xent | 6 | (16,128,128); (5,100,100) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.sub cast.explicit cmp.compare construct.arange construct.full construct.zeros dtype.int dtype.uint flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise math.clamp math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store misc.rng pat.masked_both pat.persistent_reduce pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where |
| `suite/dev/linspace_kernel.py` | dev | elementwise_reduce | 6 | (17); (107) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cmp.compare construct.arange dtype.int mem.masked_store mem.store select.where |
| `suite/dev/local_ne_consecutive_kernel.py` | dev | elementwise_reduce | 2 | (17); (97) | int32 | arith.add arith.mul arith.sub cast.explicit cmp.compare construct.arange dtype.int flow.dynamic_range flow.loop mem.load mem.masked_load mem.masked_store mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.sum select.where |
| `suite/dev/local_ne_flat_impl.py` | dev | elementwise_reduce | 2 | (17); (97) | int32 | arith.add arith.mul arith.sub cmp.compare construct.arange mem.load mem.masked_load mem.masked_store mem.store pat.masked_both pat.reduce_broadcast red.sum select.where |
| `suite/dev/log_normal_kernel_impl.py` | dev | norm | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.sub cast.explicit cmp.compare construct.arange dtype.int dtype.uint flow.if index.multi_offset logic.bitwise logic.bool math.abs math.clamp math.round math.sqrt_rsqrt math.transcendental mem.cache_hint mem.masked_store mem.store misc.rng select.where |
| `suite/dev/logit_kernel.py` | dev | softmax_xent | 6 | (17); (109) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.if math.clamp math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/logit_kernel_2.py` | dev | softmax_xent | 6 | (17); (110) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.if math.clamp math.transcendental mem.load mem.masked_load mem.masked_store mem.store pat.masked_both |
| `suite/dev/logspace_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange dtype.int math.transcendental mem.masked_store mem.store |
| `suite/dev/logsumexp__logsumexp_kernel_non_inner.py` | dev | softmax_xent | 6 | (17); (104) | float32, float16, bfloat16 | arith.add arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise math.clamp math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.axis red.keep_dims red.maxmin red.sum select.where |
| `suite/dev/loop_sum.py` | dev | elementwise_reduce | 3 | (3,97) | float16, float32, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop mem.load mem.masked_load mem.other mem.store pat.persistent_reduce red.axis red.sum |
| `suite/dev/lu_factor_info_kernel.py` | dev | elementwise_reduce | 6 | (17); (4,5,5,5) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange dtype.int logic.bitwise mem.load mem.masked_load mem.other mem.store red.axis red.maxmin select.where |
| `suite/dev/lu_factor_swap_right_and_solve_kernel.py` | dev | elementwise_reduce | 6 | (17); (4,9) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.loop flow.tl_range index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.axis red.sum select.where |
| `suite/dev/masked_cumsum_kernel_db.py` | dev | select_scan_index | 9 | (128,128); (17,100); (1,1) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cmp.compare construct.arange dtype.int flow.dynamic_range flow.if flow.loop logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.scan red.sum |
| `suite/dev/masked_cumsum_vec_kernel.py` | dev | select_scan_index | 9 | (128,128); (17,100); (1,1) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cast.to_fp16 cast.to_fp32 cmp.compare construct.arange construct.zeros flow.dynamic_range flow.if flow.loop index.multi_offset mem.alignment_hint mem.cache_hint mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.axis red.scan red.sum select.where |
| `suite/dev/matmul_abt_kernel.py` | dev | matmul | 6 | (128,96,100); (40,24,100) | float16, bfloat16, float32 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cmp.compare construct.zeros dot.acc dot.matmul flow.if_pid flow.loop flow.static_range mem.blockptr mem.boundary_check mem.load mem.padding mem.store pat.blockptr_boundary pat.k_loop pat.matmul_epilogue |
| `suite/dev/matmul_at_b_kernel_043f2a05.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.clamp mem.cache_hint mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both pat.matmul_epilogue shape.trans |
| `suite/dev/matmul_at_b_kernel_db_551a9cda.py` | dev | matmul | 3 | (128) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset math.clamp mem.alignment_hint mem.cache_hint mem.load mem.store pat.k_loop pat.matmul_epilogue shape.trans |
| `suite/dev/matmul_at_b_kernel_opt_84f19043.py` | dev | matmul | 3 | (128) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset mem.load mem.store pat.k_loop |
| `suite/dev/matmul_at_kernel_optimized_8461cac3.py` | dev | matmul | 6 | (64); (128) | float32, float16, bfloat16 | arith.add arith.mul cmp.compare construct.arange construct.zeros dot.matmul flow.while index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/matmul_atb_optimized_kernel_2044087e.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dot.matmul flow.while index.multi_offset logic.bitwise mem.alignment_hint mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.matmul_epilogue shape.trans |
| `suite/dev/matmul_k32_fast_kernel_f2eeb00c.py` | dev | matmul | 3 | (128) | float32, float16, bfloat16 | arith.add arith.mul construct.arange construct.zeros dot.matmul index.multi_offset mem.load mem.store |
| `suite/dev/matmul_k32_grouped_nomask_kernel_72a8a8b9.py` | dev | matmul | 3 | (128) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub construct.arange construct.zeros dot.matmul index.multi_offset math.clamp mem.load mem.store pat.matmul_epilogue |
| `suite/dev/matmul_k32_no_loop_kernel_fd37acc3.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub construct.arange dot.matmul index.multi_offset math.clamp mem.alignment_hint mem.load mem.store pat.matmul_epilogue |
| `suite/dev/matmul_k32_persistent_adaptive_kernel_cf4bd5c4.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.mul cmp.compare construct.arange dot.matmul flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both |
| `suite/dev/matmul_k32_persistent_n_2stage_kernel_c11d9a2d.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.mul arith.sub construct.arange dot.matmul flow.dynamic_range flow.loop index.multi_offset mem.alignment_hint mem.load mem.store pat.k_loop |
| `suite/dev/matmul_k32_persistent_n_kernel_107194fe.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.mul construct.arange dot.matmul flow.dynamic_range flow.loop index.multi_offset mem.load mem.store pat.k_loop |
| `suite/dev/matmul_k32_splitn2_kernel_af4f712c.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub construct.arange dot.matmul index.multi_offset math.clamp mem.alignment_hint mem.load mem.store pat.matmul_epilogue |
| `suite/dev/matmul_k32_splitn4_paired_kernel_6f1c91c8.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit construct.arange dot.matmul dtype.int flow.dynamic_range flow.loop index.multi_offset math.clamp mem.alignment_hint mem.load mem.store pat.k_loop pat.matmul_epilogue |
| `suite/dev/matmul_k32_splitn8_kernel_7756e27e.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange dot.matmul flow.dynamic_range flow.if_pid flow.loop index.multi_offset math.clamp mem.alignment_hint mem.load mem.store pat.k_loop pat.matmul_epilogue |
| `suite/dev/matmul_k64_2d_unmasked_kernel_fc2c17b0.py` | dev | matmul | 3 | (128) | float32, float16, bfloat16 | arith.add arith.mul cmp.compare construct.arange dot.matmul hint.static_assert index.multi_offset mem.alignment_hint mem.load mem.store |
| `suite/dev/matmul_k64_fused_kernel_3d82b86f.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub construct.arange construct.zeros dot.matmul index.multi_offset mem.load mem.store |
| `suite/dev/matmul_k64_grouped_nomask_kernel_e5ed3959.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul construct.arange dot.matmul index.multi_offset mem.load mem.store |
| `suite/dev/matmul_k64_kernel_0ab65594.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange dot.matmul index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/matmul_k64_specialized_kernel_2e9d07eb.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub construct.arange dot.matmul index.multi_offset math.clamp mem.cache_hint mem.load mem.store pat.matmul_epilogue |
| `suite/dev/matmul_k64_swizzle_fast_v2_bbf654b4.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub construct.arange dot.matmul index.multi_offset mem.alignment_hint mem.load mem.store |
| `suite/dev/matmul_k64_swizzled_kernel_7eb7ffe7.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub construct.arange construct.zeros dot.matmul index.multi_offset mem.alignment_hint mem.cache_hint mem.load mem.store |
| `suite/dev/matmul_kernel.py` | dev | matmul | 6 | (128,128,128); (17,33,100) | float16, bfloat16, float32 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange construct.zeros dot.acc dot.matmul flow.if flow.loop flow.static_range index.multi_offset logic.bitwise logic.bool math.clamp mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both pat.matmul_epilogue |
| `suite/dev/matmul_kernel_08d476be.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both pat.matmul_epilogue |
| `suite/dev/matmul_kernel_0a4f4889.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both pat.matmul_epilogue |
| `suite/dev/matmul_kernel_0fdeffcb.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange construct.zeros dot.matmul flow.while index.multi_offset logic.bitwise math.clamp mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.matmul_epilogue |
| `suite/dev/matmul_kernel_10d5c480.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both pat.matmul_epilogue select.where |
| `suite/dev/matmul_kernel_1334dd27.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub construct.zeros dot.matmul flow.dynamic_range flow.loop mem.blockptr mem.boundary_check mem.load mem.padding mem.store pat.blockptr_boundary pat.k_loop |
| `suite/dev/matmul_kernel_283adb7c.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub construct.arange dot.matmul dot.out_dtype index.multi_offset mem.load mem.store |
| `suite/dev/matmul_kernel_2d_8e70c631.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cmp.compare construct.arange construct.zeros dot.matmul flow.while index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/matmul_kernel_2d_nomask_tc_5d3cdcfe.py` | dev | matmul | 3 | (128) | float32, float16, bfloat16 | arith.add arith.mul construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset mem.cache_hint mem.load mem.store pat.k_loop |
| `suite/dev/matmul_kernel_357aea12.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.clamp mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both pat.matmul_epilogue |
| `suite/dev/matmul_kernel_50ce05b6.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset logic.bitwise mem.alignment_hint mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both pat.matmul_epilogue |
| `suite/dev/matmul_kernel_551a94f2.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dot.matmul flow.while index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.matmul_epilogue |
| `suite/dev/matmul_kernel_5766d29c.py` | dev | elementwise_reduce | 4 | (128); (127) | float32, float16 | arith.add arith.mul cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/matmul_kernel_689cb6a4.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset math.clamp mem.load mem.store pat.k_loop pat.matmul_epilogue |
| `suite/dev/matmul_kernel_78ec979e.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul cmp.compare construct.arange construct.zeros dot.matmul flow.while index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/matmul_kernel_7e8de72a.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp16 cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both pat.matmul_epilogue |
| `suite/dev/matmul_kernel_82de0ce7.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset mem.alignment_hint mem.load mem.store pat.k_loop |
| `suite/dev/matmul_kernel_8d68babe.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange construct.zeros dot.matmul dot.out_dtype flow.dynamic_range flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both |
| `suite/dev/matmul_kernel_a7a69c6d.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset logic.bitwise mem.load mem.masked_store mem.store pat.k_loop |
| `suite/dev/matmul_kernel_dafb9e0e.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.mul cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset logic.bitwise mem.alignment_hint mem.cache_hint mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both |
| `suite/dev/matmul_ts_kernel_218043ea.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.if_pid flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both |
| `suite/dev/matrix_reduction.py` | dev | elementwise_reduce | 6 | (16,16); (8,8) | float32, float16, bfloat16 | arith.add construct.arange mem.blockptr mem.load mem.store red.axis red.maxmin |
| `suite/dev/matrix_transpose.py` | dev | elementwise_reduce | 6 | (16,16); (8,8) | float32, float16, bfloat16 | arith.add arith.mul construct.arange index.multi_offset mem.load mem.store |
| `suite/dev/max_kernel.py` | dev | elementwise_reduce | 6 | (17); (118) | float32, float16, bfloat16 | arith.add arith.mul arith.neg arith.pow arith.sub cast.explicit cmp.compare construct.arange construct.full construct.zeros dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bool mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.axis red.maxmin select.where |
| `suite/dev/max_reduction.py` | dev | elementwise_reduce | 6 | (128); (99) | float32, float16, bfloat16 | arith.add cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full flow.dynamic_range flow.loop math.clamp mem.load mem.masked_load mem.other mem.store pat.persistent_reduce red.axis red.maxmin tune.autotune |
| `suite/dev/maxpool1d.py` | dev | conv_pool | 6 | (3,19,3,2,1,1); (2,37,4,1,2,2) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full flow.dynamic_range flow.loop index.multi_offset index.rank2 logic.bitwise math.clamp mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both shape.reshape |
| `suite/dev/mean_dim_kernel_inner.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bool mem.load mem.masked_load mem.other mem.store pat.persistent_reduce red.axis red.sum |
| `suite/dev/mean_dim_kernel_non_inner.py` | dev | elementwise_reduce | 6 | (17); (120) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise logic.bool mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.axis red.keep_dims red.sum |
| `suite/dev/mean_dim_kernel_non_inner_vec.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset index.rank2 logic.bool mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/mean_kernel_1.py` | dev | elementwise_reduce | 6 | (17); (115) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange dtype.int flow.if logic.bool mem.load mem.masked_load mem.other mem.store red.sum |
| `suite/dev/mean_reduction.py` | dev | elementwise_reduce | 6 | (8,16); (8,32) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset logic.bitwise mem.load mem.other mem.store pat.persistent_reduce red.axis red.sum |
| `suite/dev/median_bool_count_kernel.py` | dev | select_scan_index | 2 | (17); (108) | bool | arith.add arith.mul cast.explicit cmp.compare construct.arange dtype.int logic.bitwise mem.load mem.masked_load mem.other mem.store red.axis red.sum |
| `suite/dev/median_bool_dim_count_chunks_kernel.py` | dev | linear_attention | 2 | (2,17,3); (4,97,7) | bool | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cmp.compare construct.arange dtype.int logic.bitwise mem.load mem.masked_load mem.other mem.store pat.reduce_broadcast red.axis red.maxmin red.sum select.where |
| `suite/dev/median_bool_dim_finish_kernel.py` | dev | select_scan_index | 2 | (3,5,17); (17,33,97) | int64 | arith.add arith.div arith.mul arith.sub cmp.compare construct.arange mem.load mem.masked_load mem.other mem.store pat.reduce_broadcast red.axis red.maxmin red.sum select.where |
| `suite/dev/median_bool_dim_reduce_chunks_kernel.py` | dev | linear_attention | 2 | (3,17); (15,17) | int64 | arith.add arith.mul cmp.compare construct.arange mem.load mem.masked_load mem.other mem.store red.axis red.maxmin red.sum |
| `suite/dev/median_bool_from_counts_kernel.py` | dev | select_scan_index | 2 | (17,3); (97,33) | int64 | arith.add arith.div arith.sub cmp.compare construct.arange mem.load mem.masked_load mem.other mem.store red.axis red.sum |
| `suite/dev/median_bool_reduce_counts_kernel.py` | dev | select_scan_index | 2 | (17); (109) | int64 | arith.add arith.mul cmp.compare construct.arange mem.load mem.masked_load mem.other mem.store red.axis red.sum |
| `suite/dev/median_f16_key_select_kernel.py` | dev | select_scan_index | 6 | (1,17); (3,33); (1,34) | float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.sub cast.explicit cmp.compare construct.arange construct.full dtype.int dtype.uint flow.loop flow.static_range logic.bitwise mem.load mem.masked_load mem.other mem.store pat.persistent_reduce pat.reduce_broadcast red.argmaxmin red.axis red.maxmin red.sum select.where |
| `suite/dev/median_fp32_strided_key_select_kernel.py` | dev | select_scan_index | 2 | (2,17,3); (4,65,7) | float32 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cmp.compare construct.arange construct.full dtype.int dtype.uint flow.loop flow.static_range index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.argmaxmin red.axis red.maxmin red.sum select.where |
| `suite/dev/median_int_lastdim_select_kernel.py` | dev | select_scan_index | 2 | (17); (97) | int32 | arith.add arith.div arith.mul arith.neg arith.pow arith.sub cast.explicit cmp.compare construct.arange dtype.int flow.if flow.loop flow.static_range logic.bitwise mem.load mem.masked_load mem.other mem.store pat.persistent_reduce pat.reduce_broadcast red.argmaxmin red.axis red.maxmin red.sum select.where |
| `suite/dev/medium__hardsigmoid_kernel.py` | dev | elementwise_reduce | 9 | (128); (100); (1) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cmp.compare construct.arange flow.loop flow.tl_range math.clamp mem.load mem.masked_load mem.masked_store mem.store pat.masked_both tune.loop_pragma |
| `suite/dev/min_kernel_2.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.pow arith.sub cmp.compare construct.arange flow.if mem.load mem.masked_load mem.other mem.store red.maxmin |
| `suite/dev/min_reduce_lastdim_partials_kernel.py` | dev | elementwise_reduce | 3 | (128,127); (17,100); (1,1) | float32 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange mem.atomic mem.load mem.masked_load mem.other red.axis red.maxmin |
| `suite/dev/mode_kernel.py` | dev | elementwise_reduce | 6 | (17); (114) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange construct.full dtype.int flow.dynamic_range flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.store pat.masked_both select.where shape.reshape |
| `suite/dev/mul_exponent_compensator.py` | dev | elementwise_reduce | 6 | (64); (128) | float32, float16, bfloat16 | arith.add arith.mul arith.pow arith.sub construct.arange mem.load mem.store |
| `suite/dev/mul_scalar_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cmp.compare construct.arange logic.bitwise mem.load mem.masked_load mem.masked_store mem.store pat.masked_both select.where |
| `suite/dev/multinomial_with_replacement.py` | dev | elementwise_reduce | 6 | (17); (5,5,8) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dtype.int dtype.uint flow.dynamic_range flow.if flow.loop logic.bitwise logic.bool math.transcendental mem.load mem.masked_load mem.masked_store mem.store misc.rng pat.masked_both select.where |
| `suite/dev/naive_attn_decoding_kernel.py` | dev | attention | 6 | (2,17,4,8,16,13); (3,33,6,12,32,65) | float16, float32, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full construct.zeros dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise math.clamp math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where |
| `suite/dev/nanmedian_ascend_byte_histogram_find_index_kernel.py` | dev | select_scan_index | 2 | (17); (97) | int32 | arith.add arith.mul arith.sub cast.explicit cmp.compare construct.arange construct.full dtype.int flow.if flow.loop flow.tl_range logic.bitwise mem.load mem.masked_load mem.other mem.store pat.persistent_reduce red.axis red.maxmin select.where |
| `suite/dev/nanmedian_ascend_byte_histogram_init_kernel.py` | dev | select_scan_index | 2 | (17); (38) | int64 | arith.add arith.div arith.mul cast.explicit dtype.int mem.store |
| `suite/dev/nanmedian_ascend_histogram_count_kernel.py` | dev | select_scan_index | 2 | (17); (108) | int8 | arith.add arith.mul arith.sub cast.explicit cmp.compare construct.arange construct.full dtype.int flow.if index.multi_offset logic.bitwise mem.load mem.masked_load mem.other mem.store pat.reduce_broadcast red.axis red.histogram red.sum select.where |
| `suite/dev/nanmedian_float_clean_count_kernel.py` | dev | select_scan_index | 4 | (17); (97) | float32, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full dtype.int flow.if flow.loop flow.tl_range logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.axis red.sum select.where |
| `suite/dev/nanmedian_select_kernel.py` | dev | select_scan_index | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.pow arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full dtype.int flow.if flow.loop flow.static_range logic.bitwise mem.load mem.masked_load mem.other mem.store pat.persistent_reduce pat.reduce_broadcast red.axis red.maxmin red.sum select.where |
| `suite/dev/nansum_dim_kernel_inner.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.axis red.sum select.where |
| `suite/dev/nansum_dim_kernel_non_inner.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.axis red.keep_dims red.sum select.where |
| `suite/dev/nansum_kernel_1.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange dtype.int flow.if mem.load mem.masked_load mem.other mem.store red.axis red.sum select.where |
| `suite/dev/nansum_kernel_2.py` | dev | elementwise_reduce | 6 | (17); (126) | float32, float16, bfloat16 | arith.add cast.explicit cmp.compare construct.arange construct.zeros flow.dynamic_range flow.if flow.loop mem.load mem.masked_load mem.other mem.store pat.persistent_reduce red.axis red.sum select.where |
| `suite/dev/nonzero_kernel.py` | dev | select_scan_index | 2 | (17); (735) | int32 | arith.add arith.mod arith.mul arith.neg arith.sub cast.explicit cmp.compare construct.arange dtype.int flow.dynamic_range flow.loop logic.bool mem.load mem.masked_load mem.masked_store mem.store pat.masked_both |
| `suite/dev/nonzero_static_count_kernel.py` | dev | select_scan_index | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange dtype.int flow.if logic.bitwise mem.load mem.masked_load mem.other mem.store red.axis red.sum |
| `suite/dev/nonzero_static_fill_tail_kernel.py` | dev | select_scan_index | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cmp.compare construct.arange construct.full math.clamp mem.load mem.masked_store mem.store |
| `suite/dev/norm__l1_norm_kernel_2.py` | dev | norm | 6 | (17); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange math.abs math.transcendental mem.load mem.masked_load mem.other mem.store red.sum |
| `suite/dev/norm__l2_norm_kernel.py` | dev | norm | 6 | (17); (106) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full construct.zeros dtype.int flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.abs math.clamp math.sqrt_rsqrt mem.load mem.other mem.store pat.persistent_reduce red.axis red.maxmin red.sum select.where |
| `suite/dev/norm__l2_norm_kernel_2.py` | dev | norm | 6 | (17); (127) | float32, float16, bfloat16 | arith.add cast.explicit cast.to_fp32 cmp.compare construct.arange math.sqrt_rsqrt mem.load mem.masked_load mem.other mem.store red.sum |
| `suite/dev/norm__l2_norm_kernel_d8a78ccfd6d73a54.py` | dev | norm | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.loop index.multi_offset logic.bool math.sqrt_rsqrt mem.load mem.other mem.store pat.persistent_reduce red.axis red.sum |
| `suite/dev/norm__max_norm_kernel_1.py` | dev | norm | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int math.abs mem.load mem.masked_load mem.other mem.store red.maxmin |
| `suite/dev/norm__max_norm_kernel_2.py` | dev | norm | 6 | (17); (97) | float32, float16, bfloat16 | arith.add cast.explicit cast.to_fp32 cmp.compare construct.arange mem.load mem.masked_load mem.other mem.store red.maxmin |
| `suite/dev/norm__min_norm_kernel.py` | dev | norm | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full dtype.int flow.dynamic_range flow.loop index.multi_offset logic.bool math.abs math.clamp mem.load mem.other mem.store pat.persistent_reduce red.axis red.maxmin |
| `suite/dev/norm__v_norm_kernel.py` | dev | norm | 6 | (17); (110) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.loop index.multi_offset logic.bool math.abs math.transcendental mem.load mem.other mem.store pat.persistent_reduce red.axis red.sum |
| `suite/dev/normalize_projection_kernel.py` | dev | norm | 6 | (17); (5,8,4) | float32, float16, bfloat16 | arith.add arith.div arith.mul cmp.compare construct.arange math.clamp mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/ones_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange dtype.int mem.masked_store mem.store |
| `suite/dev/output_counts_flat_kernel.py` | dev | elementwise_reduce | 2 | (17); (97) | int64 | arith.add arith.mul arith.sub cast.explicit cmp.compare construct.arange dtype.int flow.dynamic_range flow.loop mem.load mem.masked_load mem.masked_store mem.store pat.masked_both select.where |
| `suite/dev/pairwise_distance_general_kernel_1.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cmp.compare construct.arange math.abs math.transcendental mem.load mem.masked_load mem.other mem.store pat.reduce_broadcast red.sum select.where |
| `suite/dev/pairwise_distance_max_kernel_2.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.neg cmp.compare construct.arange mem.load mem.masked_load mem.other mem.store red.maxmin select.where |
| `suite/dev/pairwise_distance_min_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cmp.compare construct.arange construct.full flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.abs math.clamp mem.load mem.masked_load mem.other mem.store pat.persistent_reduce red.axis red.maxmin select.where |
| `suite/dev/pairwise_distance_min_kernel_1.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cmp.compare construct.arange math.abs mem.load mem.masked_load mem.other mem.store red.maxmin select.where |
| `suite/dev/pairwise_distance_p0_kernel_2.py` | dev | elementwise_reduce | 6 | (17); (127) | float32, float16, bfloat16 | arith.add arith.mul cmp.compare construct.arange mem.load mem.masked_load mem.other mem.store red.sum |
| `suite/dev/pairwise_distance_p2_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.abs math.sqrt_rsqrt mem.load mem.masked_load mem.other mem.store pat.persistent_reduce pat.reduce_broadcast red.axis red.sum select.where |
| `suite/dev/parallel_attn_fwd_kernel.py` | dev | attention | 6 | (2,17,2,4,7,9,8,9); (3,17,2,4,7,9,8,9) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full construct.zeros dot.matmul dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset index.rank2 logic.bitwise math.clamp math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.dot_reduce pat.k_loop pat.masked_both pat.matmul_epilogue pat.persistent_reduce pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where shape.reshape |
| `suite/dev/parallel_based_fwd_kernel.py` | dev | linear_attention | 6 | (4,17,7,9,8); (6,33,11,13,16) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dot.matmul dtype.int flow.dynamic_range flow.loop index.multi_offset index.rank2 logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store misc.barrier pat.dot_reduce pat.k_loop pat.masked_both pat.matmul_epilogue pat.persistent_reduce red.axis red.sum select.where shape.reshape |
| `suite/dev/parallel_path_fwd_kernel_prepare_k_cache.py` | dev | matmul | 6 | (17); (10,17,2,6) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dot.matmul dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset index.rank2 logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both pat.matmul_epilogue select.where shape.reshape shape.trans |
| `suite/dev/pdist__pdist_forward_general_kernel.py` | dev | elementwise_reduce | 6 | (17); (11,3) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int flow.if flow.if_pid flow.while logic.bool math.abs math.transcendental mem.load mem.masked_load mem.other mem.store pat.reduce_broadcast red.axis red.sum select.where |
| `suite/dev/pdist_forward__pdist_forward_inf_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full dtype.int flow.dynamic_range flow.loop math.abs math.clamp mem.load mem.masked_load mem.other mem.store pat.persistent_reduce red.maxmin select.where |
| `suite/dev/pdist_forward__pdist_forward_p2_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full dtype.int flow.dynamic_range flow.loop math.sqrt_rsqrt mem.load mem.masked_load mem.other mem.store pat.normalize pat.persistent_reduce pat.reduce_broadcast red.sum select.where |
| `suite/dev/pipelined_gemv.py` | dev | elementwise_reduce | 9 | (8,128); (17,97); (1,1) | float32, float16, bfloat16 | arith.add arith.mul cmp.compare construct.arange construct.zeros flow.loop flow.tl_range index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.axis red.sum tune.loop_pragma |
| `suite/dev/position_quantize.py` | dev | quant | 9 | (128); (114); (1) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full dtype.int index.multi_offset math.abs math.clamp math.round math.transcendental mem.load mem.other mem.store pat.reduce_broadcast red.axis red.keep_dims red.sum shape.expand |
| `suite/dev/pow_scalar_tensor.py` | dev | elementwise_reduce | 6 | (128); (99) | float32, float16, bfloat16 | arith.add arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare flow.dynamic_range flow.if flow.loop logic.bitwise math.abs math.round math.transcendental mem.blockptr mem.boundary_check mem.load mem.store pat.blockptr_boundary select.where |
| `suite/dev/prelu_kernel.py` | dev | elementwise_reduce | 6 | (17); (102) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul cmp.compare construct.arange flow.if mem.load mem.masked_load mem.masked_store mem.store pat.masked_both select.where |
| `suite/dev/prepare_wy_repr_fwd_kernel_safe.py` | dev | linear_attention | 6 | (2,33,3,16); (3,33,3,16) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp16 cmp.compare construct.arange construct.zeros dot.matmul dtype.int flow.if index.multi_offset mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.matmul_epilogue select.where |
| `suite/dev/qr.py` | dev | elementwise_reduce | 2 | (6,4); (12,8) | float32 | arith.add arith.div arith.mul arith.neg arith.sub cmp.compare construct.arange flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise math.clamp math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.normalize pat.persistent_reduce pat.reduce_broadcast red.axis red.sum select.where |
| `suite/dev/quant_transpose_kernel.py` | dev | quant | 6 | (128,128); (99,99) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int index.multi_offset logic.bitwise math.abs math.round mem.load mem.masked_load mem.masked_store mem.store pat.masked_both select.where tune.autotune |
| `suite/dev/randint__randint_kernel.py` | dev | elementwise_reduce | 2 | (17); (120) | int64 | arith.add arith.mod arith.mul cast.explicit cmp.compare construct.arange dtype.int dtype.uint index.multi_offset logic.bitwise mem.masked_store mem.store misc.rng |
| `suite/dev/randint_like__randint_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int dtype.uint flow.if index.multi_offset logic.bitwise logic.bool mem.cache_hint mem.masked_store mem.store misc.rng select.where |
| `suite/dev/rank1_svd_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full flow.dynamic_range flow.if flow.loop math.clamp math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.sum |
| `suite/dev/rank2_svals_tiny_kernel.py` | dev | elementwise_reduce | 6 | (17); (7,7,2) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.if index.multi_offset logic.bitwise math.clamp math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.normalize pat.reduce_broadcast red.axis red.sum select.where |
| `suite/dev/ranked_distribution_semantic.py` | dev | elementwise_reduce | 6 | (16); (64) | float32, float16, bfloat16 | arith.add arith.div arith.mod cast.explicit cmp.compare construct.arange dtype.int index.multi_offset logic.bitwise mem.load mem.store red.sort select.where |
| `suite/dev/reduce_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add cmp.compare construct.arange flow.if_pid mem.load mem.masked_load mem.other mem.store red.sum |
| `suite/dev/reduce_sum_kernel.py` | dev | elementwise_reduce | 6 | (17); (127) | float32, float16, bfloat16 | arith.add arith.div cast.explicit cast.to_fp32 cmp.compare construct.arange mem.load mem.masked_load mem.other mem.store red.axis red.sum |
| `suite/dev/relu_squared_forward_kernel.py` | dev | elementwise_reduce | 6 | (3,17); (36,17) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange dtype.int math.clamp mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/renorm_kernel.py` | dev | norm | 6 | (17); (117) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int math.abs math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both red.sum select.where |
| `suite/dev/renorm_kernel_norms.py` | dev | norm | 6 | (17); (123) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop logic.bool math.abs math.sqrt_rsqrt math.transcendental mem.load mem.masked_load mem.other mem.store pat.persistent_reduce red.sum |
| `suite/dev/renorm_kernel_scale.py` | dev | norm | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cmp.compare construct.arange dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bool mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/renorm_projection_update_s_kernel.py` | dev | norm | 6 | (17); (6,8,4) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange math.clamp math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both red.axis red.sum select.where |
| `suite/dev/repeat_interleave_tensor_kernel.py` | dev | elementwise_reduce | 2 | (17); (82) | int32 | arith.add arith.sub cast.explicit cmp.compare construct.arange dtype.int flow.dynamic_range flow.loop mem.load mem.masked_store mem.other mem.store |
| `suite/dev/resolve_conj_kernel_1d.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.neg cmp.compare construct.arange flow.if mem.load mem.masked_load mem.masked_store mem.store pat.masked_both |
| `suite/dev/reversed_cumsum.py` | dev | select_scan_index | 9 | (1,1,8,8); (2,2,9,9); (1,2,16,8) | float32, float16, bfloat16 | arith.add arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both tune.autotune |
| `suite/dev/rms_matmul_rbe.py` | dev | matmul | 6 | (1,64,64,64); (1,64,32,64) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.sqrt_rsqrt mem.load mem.masked_store mem.store pat.dot_reduce pat.k_loop pat.matmul_epilogue pat.persistent_reduce red.axis red.sum |
| `suite/dev/rmsnorm_fwd_loop_kernel.py` | dev | norm | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cmp.compare construct.arange construct.zeros flow.dynamic_range flow.if flow.loop index.multi_offset logic.bool math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.axis red.sum |
| `suite/dev/rng_dual_kernel.py` | dev | elementwise_reduce | 6 | (128); (1) | float32, float16, bfloat16 | arith.add arith.mod arith.mul cmp.compare construct.arange mem.load mem.masked_store mem.store misc.rng select.where |
| `suite/dev/rope_embedding.py` | dev | elementwise_reduce | 6 | (8,16); (8,32) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cast.to_fp32 construct.arange mem.load mem.store |
| `suite/dev/round_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.pow arith.sub cast.explicit cmp.compare construct.arange flow.if logic.bitwise math.abs math.round mem.load mem.masked_load mem.masked_store mem.store pat.masked_both select.where |
| `suite/dev/row_reduce_min_kernel.py` | dev | elementwise_reduce | 9 | (128,128); (17,128); (1,1) | float32, float16, bfloat16 | arith.add arith.mul construct.arange mem.load mem.store red.axis red.maxmin |
| `suite/dev/rowwise_quantization_triton.py` | dev | quant | 6 | (4,8); (7,11) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int logic.bitwise math.abs math.round mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both red.axis red.maxmin select.where tune.autotune |
| `suite/dev/scatter_atomic_kernel.py` | dev | select_scan_index | 9 | (128,4,128); (7,3,98); (1,1,1) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange mem.atomic mem.load mem.masked_load |
| `suite/dev/scatter_diag_kernel.py` | dev | select_scan_index | 6 | (17); (3,4,5) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange mem.load mem.masked_load mem.masked_store mem.store pat.masked_both select.where |
| `suite/dev/selu_kernel_supreme.py` | dev | elementwise_reduce | 2 | (393216); (4097) | float32 | arith.add arith.mod arith.mul arith.sub cmp.compare construct.arange flow.if flow.loop flow.static_range hint.static_assert math.clamp math.transcendental mem.alignment_hint mem.cache_hint mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.maxmin |
| `suite/dev/sgn_complex_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange flow.if logic.bitwise math.abs math.clamp math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both select.where |
| `suite/dev/sgn_real_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cmp.compare construct.arange flow.if mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/slice_scatter_kernel.py` | dev | select_scan_index | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange logic.bitwise mem.load mem.masked_load mem.masked_store mem.store pat.masked_both select.where |
| `suite/dev/small4_square_svd_kernel_cc0a90a31fcf1df1.py` | dev | elementwise_reduce | 1 | (17) | float32 | arith.add arith.div arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int flow.loop flow.static_range index.multi_offset logic.bitwise math.abs math.clamp math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.normalize pat.persistent_reduce pat.reduce_broadcast red.axis red.sum select.where |
| `suite/dev/small_n_log_softmax_kernel.py` | dev | softmax_xent | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.reduce_broadcast red.axis red.maxmin red.sum |
| `suite/dev/smooth_l1_loss_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.if math.abs mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both select.where |
| `suite/dev/smooth_l1_loss_partial_sum_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.if math.abs mem.load mem.masked_load mem.other mem.store pat.reduce_broadcast red.axis red.sum select.where |
| `suite/dev/soft_margin_loss_partial_sum_kernel.py` | dev | softmax_xent | 6 | (17); (118) | float32, float16, bfloat16 | arith.add arith.mul arith.neg cast.explicit cast.to_fp32 cmp.compare construct.arange math.abs math.clamp math.transcendental mem.load mem.masked_load mem.other mem.store red.axis red.sum select.where |
| `suite/dev/softmax_bias_scale_sigmoid_fused_nchw_inplace.py` | dev | softmax_xent | 6 | (2,64,128); (2,40,100) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.sub cast.explicit cast.to_fp16 cast.to_fp32 cmp.compare construct.arange construct.full construct.zeros dtype.int flow.if flow.loop flow.static_range index.multi_offset logic.bitwise math.abs math.clamp math.transcendental mem.cache_hint mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where |
| `suite/dev/softmax_kernel_inner.py` | dev | softmax_xent | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.full dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset math.clamp math.transcendental mem.cache_hint mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where |
| `suite/dev/softmax_multi_block_forward_kernel.py` | dev | softmax_xent | 6 | (1,17); (18,17) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cmp.compare construct.arange construct.full flow.loop flow.tl_range math.clamp math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum |
| `suite/dev/softmax_multi_block_forward_kernel_16feef5d77276b9f.py` | dev | softmax_xent | 6 | (3,97); (5,97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.sub cmp.compare construct.arange construct.full flow.loop flow.tl_range math.clamp math.transcendental mem.cache_hint mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum |
| `suite/dev/softmax_single_block_forward_kernel.py` | dev | softmax_xent | 6 | (1,17); (20,17) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cmp.compare construct.arange flow.loop flow.tl_range index.multi_offset logic.bitwise math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum |
| `suite/dev/softplus_kernel.py` | dev | elementwise_reduce | 1 | (128) | float32 | arith.add arith.mul cmp.compare construct.arange math.transcendental mem.load mem.store select.where |
| `suite/dev/softsign_kernel.py` | dev | elementwise_reduce | 6 | (128); (1) | float32, float16, bfloat16 | arith.add arith.div arith.mul construct.arange math.abs mem.load mem.store |
| `suite/dev/split_copy_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul cmp.compare construct.arange mem.load mem.masked_load mem.masked_store mem.store pat.masked_both |
| `suite/dev/splitk_gemv.py` | dev | elementwise_reduce | 4 | (17,64); (33,128) | float32, float16 | arith.add arith.mul cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.clamp mem.atomic mem.load mem.masked_load mem.other pat.persistent_reduce red.axis red.sum |
| `suite/dev/std_dim_kernel_inner.py` | dev | elementwise_reduce | 6 | (17); (114) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros flow.dynamic_range flow.if flow.loop index.multi_offset math.clamp math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.normalize pat.persistent_reduce pat.reduce_broadcast red.axis red.sum select.where |
| `suite/dev/std_map_kernel.py` | dev | elementwise_reduce | 6 | (17); (102) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange mem.load mem.masked_load mem.other mem.store red.axis red.sum |
| `suite/dev/std_reduce_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop math.clamp math.sqrt_rsqrt mem.load mem.masked_load mem.other mem.store pat.normalize pat.persistent_reduce pat.reduce_broadcast red.axis red.sum |
| `suite/dev/stochastic_ensemble.py` | dev | elementwise_reduce | 6 | (128); (32) | float32, float16, bfloat16 | arith.add arith.mod arith.mul cast.explicit cmp.compare construct.arange construct.full dtype.int dtype.uint logic.bitwise mem.load mem.store misc.rng select.where |
| `suite/dev/sum_kernel_2.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add cast.explicit cmp.compare construct.arange flow.if logic.bool mem.load mem.masked_load mem.other mem.store red.sum |
| `suite/dev/svd__rank2_svals_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.if math.clamp math.sqrt_rsqrt mem.load mem.masked_load mem.other mem.store pat.normalize pat.reduce_broadcast red.sum select.where |
| `suite/dev/swish_kernel.py` | dev | elementwise_reduce | 6 | (128); (100) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg cast.explicit cast.to_fp32 cmp.compare construct.arange flow.while math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both select.where |
| `suite/dev/sym_constrain_range_kernel.py` | dev | elementwise_reduce | 1 | (17) | int64 | cast.explicit cmp.compare dtype.int logic.bool mem.load mem.store |
| `suite/dev/synthesis_kernel.py` | dev | elementwise_reduce | 3 | (1,4,16,64) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros flow.dynamic_range flow.if flow.loop index.multi_offset math.abs math.clamp math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.axis red.sum select.where shape.expand |
| `suite/dev/thin_reorthogonalize_kernel.py` | dev | elementwise_reduce | 1 | (17) | float32 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.if flow.loop flow.static_range math.clamp math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store misc.barrier pat.masked_both pat.normalize pat.persistent_reduce pat.reduce_broadcast red.sum select.where |
| `suite/dev/tiled_argmin.py` | dev | select_scan_index | 6 | (2,37,5); (3,67,9) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange construct.full construct.zeros dtype.int flow.dynamic_range flow.if_pid flow.loop index.multi_offset logic.bitwise mem.cache_hint mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.argmaxmin red.axis red.maxmin select.where |
| `suite/dev/topk.py` | dev | select_scan_index | 6 | (4,16); (8,32) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange flow.dynamic_range flow.loop mem.load mem.masked_load mem.other mem.store pat.persistent_reduce red.argmaxmin red.axis red.maxmin select.where |
| `suite/dev/topk_stage1_kernel.py` | dev | select_scan_index | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int flow.dynamic_range flow.if flow.loop logic.bitwise mem.load mem.masked_load mem.other mem.store pat.persistent_reduce red.argmaxmin red.axis red.maxmin select.where |
| `suite/dev/transpose_2d_kernel_opt.py` | dev | elementwise_reduce | 6 | (128,128); (128,64) | float32, float16, bfloat16 | arith.add arith.mul construct.arange index.multi_offset mem.load mem.store shape.trans |
| `suite/dev/transposed_conv3d.py` | dev | conv_pool | 9 | (1,3,5,2,3,4,1,0); (1,3,10,2,3,4,1,0); (3,3,5,2,3,4,1,0) | float16, float32, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise logic.bool mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both shape.reshape shape.trans |
| `suite/dev/triangular_inverse_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.sub cast.explicit cmp.compare construct.zeros dtype.int flow.dynamic_range flow.if flow.loop logic.bool mem.load mem.store |
| `suite/dev/tril_exact_diag0_tile_kernel.py` | dev | elementwise_reduce | 6 | (2,8,8); (3,8,8) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cmp.compare construct.arange flow.if index.multi_offset mem.load mem.masked_load mem.other mem.store |
| `suite/dev/tril_inplace_zero_tile_kernel.py` | dev | elementwise_reduce | 6 | (2,8,8); (3,12,12) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cmp.compare construct.arange flow.if index.multi_offset logic.bitwise mem.masked_store mem.store |
| `suite/dev/tril_matmul_kernel_6d320d58.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise logic.bool math.clamp mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both pat.matmul_epilogue select.where |
| `suite/dev/tril_matmul_kernel_fccb62cc.py` | dev | matmul | 6 | (128); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.if_pid flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both |
| `suite/dev/tril_rows_kernel.py` | dev | elementwise_reduce | 6 | (2,8,8); (3,12,12) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cmp.compare construct.arange flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/tril_tile_kernel.py` | dev | elementwise_reduce | 6 | (2,8,8); (8,8,8) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cmp.compare construct.arange flow.if index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/triton_argmax.py` | dev | select_scan_index | 6 | (128); (127) | float32, float16, bfloat16 | arith.add cast.explicit cast.to_fp32 cmp.compare construct.arange mem.load mem.masked_load mem.other mem.store red.argmaxmin red.axis |
| `suite/dev/triton_conv2d_fwd.py` | dev | conv_pool | 6 | (1,2,6,6); (2,2,8,8) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare flow.dynamic_range flow.loop logic.bitwise mem.load mem.masked_load mem.other mem.store |
| `suite/dev/triu_batch_kernel.py` | dev | elementwise_reduce | 6 | (17); (120) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul cast.explicit cmp.compare construct.arange dtype.int index.multi_offset logic.bool mem.load mem.masked_store mem.other mem.store select.where |
| `suite/dev/triu_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange dtype.int flow.dynamic_range flow.loop index.multi_offset logic.bool mem.load mem.masked_store mem.other mem.store select.where |
| `suite/dev/tv_distance_kernel.py` | dev | elementwise_reduce | 6 | (1,17); (21,17) | float32, float16, bfloat16 | arith.add arith.mul arith.neg arith.sub cmp.compare construct.arange flow.dynamic_range flow.if flow.loop flow.tl_range math.abs mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.axis red.sum select.where |
| `suite/dev/unbind_copy_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul cmp.compare construct.arange mem.load mem.masked_load mem.masked_store mem.store pat.masked_both |
| `suite/dev/unfold_copy_kernel_3d_dim1.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mod arith.mul cmp.compare construct.arange mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/dev/unique_dim_inverse_kernel.py` | dev | select_scan_index | 2 | (17); (97) | int64 | arith.add arith.mul cast.explicit cmp.compare construct.arange dtype.int mem.load mem.masked_load mem.masked_store mem.store pat.masked_both |
| `suite/dev/unique_dim_row_chunk_diff_hash_kernel.py` | dev | linear_attention | 2 | (17); (97) | int32 | arith.add arith.mul arith.sub cast.explicit cmp.compare construct.arange construct.full dtype.int flow.if logic.bitwise mem.load mem.masked_load mem.store pat.reduce_broadcast red.axis red.sum select.where |
| `suite/dev/unique_dim_row_diff_reduce_kernel.py` | dev | select_scan_index | 2 | (17); (97) | int32 | arith.add arith.mul cast.explicit cmp.compare construct.arange dtype.int mem.load mem.masked_load mem.other mem.store red.axis red.sum |
| `suite/dev/unique_dim_row_single_chunk_first_kernel.py` | dev | linear_attention | 2 | (17); (104) | int32 | arith.add arith.mul arith.sub cast.explicit cmp.compare construct.arange construct.full dtype.int flow.if logic.bitwise mem.load mem.masked_load mem.store pat.reduce_broadcast red.axis red.sum |
| `suite/dev/var_kernel_1.py` | dev | elementwise_reduce | 6 | (17); (103) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int mem.load mem.other mem.store pat.reduce_broadcast red.sum |
| `suite/dev/var_kernel_2.py` | dev | elementwise_reduce | 6 | (17); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange math.clamp mem.load mem.other mem.store pat.reduce_broadcast red.axis red.sum |
| `suite/dev/var_len_copy.py` | dev | elementwise_reduce | 6 | (3); (4) | float32, float16, bfloat16 | arith.add cmp.compare construct.arange flow.dynamic_range flow.loop mem.load mem.masked_load mem.masked_store mem.store pat.masked_both |
| `suite/dev/var_mean_welford_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.loop index.multi_offset mem.load mem.other mem.store pat.persistent_reduce pat.reduce_broadcast red.sum select.where |
| `suite/dev/vdot__dot_kernel.py` | dev | elementwise_reduce | 6 | (17); (105) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop mem.load mem.masked_load mem.other mem.store pat.persistent_reduce red.sum |
| `suite/dev/vdot_kernel_complex.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul arith.neg arith.sub cmp.compare construct.arange construct.zeros flow.dynamic_range flow.if flow.loop logic.bool mem.load mem.masked_load mem.other mem.store pat.persistent_reduce pat.reduce_broadcast red.sum |
| `suite/dev/vecdot_kernel.py` | dev | elementwise_reduce | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop mem.load mem.masked_load mem.other mem.store pat.persistent_reduce red.axis red.sum |
| `suite/dev/vector_norm__l1_norm_kernel_1.py` | dev | norm | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange dtype.int flow.if math.abs math.transcendental mem.load mem.masked_load mem.other mem.store red.sum |
| `suite/dev/vector_norm__l1_norm_kernel_2.py` | dev | norm | 6 | (17); (127) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cmp.compare construct.arange flow.if math.transcendental mem.load mem.masked_load mem.other mem.store red.sum |
| `suite/dev/vector_norm__l2_norm_kernel.py` | dev | norm | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise math.sqrt_rsqrt mem.load mem.other mem.store pat.persistent_reduce red.axis red.sum |
| `suite/dev/vector_norm__max_norm_kernel.py` | dev | norm | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.mul cast.explicit cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise math.abs math.clamp mem.load mem.other mem.store pat.persistent_reduce red.axis red.maxmin |
| `suite/dev/vector_norm__max_norm_kernel_2.py` | dev | norm | 6 | (17); (97) | float32, float16, bfloat16 | arith.add cast.explicit cmp.compare construct.arange flow.if mem.load mem.masked_load mem.other mem.store red.maxmin |
| `suite/dev/vector_norm__v_norm_kernel.py` | dev | norm | 6 | (17); (97) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cmp.compare construct.arange construct.zeros dtype.int flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise math.abs math.transcendental mem.load mem.other mem.store pat.persistent_reduce red.axis red.sum |
| `suite/dev/vocab_parallel_ce_forward_kernel.py` | dev | elementwise_reduce | 6 | (7,17); (11,67) | float32, float16, bfloat16 | arith.add arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int flow.dynamic_range flow.if flow.loop logic.bitwise logic.bool math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.sum select.where |
| `suite/dev/weighted_scatter_add_kernel.py` | dev | select_scan_index | 9 | (8,64,128,128); (3,7,100,16); (1,1,1,1) | float32, float16, bfloat16 | arith.add arith.div arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange dtype.int flow.if mem.atomic mem.load mem.masked_load mem.other |
| `suite/perf/add_gelu.py` | perf | elementwise_reduce | 6 | (128); (99) | bfloat16, float32, float16 | arith.add arith.mul cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/add_mean.py` | perf | elementwise_reduce | 6 | (4,16); (4,97) | bfloat16, float32, float16 | arith.add arith.div arith.mul cmp.compare construct.arange mem.load mem.masked_load mem.other mem.store red.axis red.sum select.where |
| `suite/perf/add_value.py` | perf | elementwise_reduce | 6 | (4); (5) | bfloat16, float32, float16 | arith.add arith.mul cmp.compare construct.arange mem.load mem.masked_load mem.masked_store mem.store pat.masked_both |
| `suite/perf/argmax.py` | perf | select_scan_index | 6 | (4,16); (4,97) | bfloat16, float32, float16 | arith.add arith.mul arith.neg cmp.compare construct.arange flow.dynamic_range flow.loop logic.bitwise math.clamp mem.load mem.other mem.store pat.persistent_reduce red.axis red.maxmin select.where |
| `suite/perf/attention_forward_triton.py` | perf | attention | 9 | (2,2,16,32); (4,4,32,64); (1,1,8,16) | bfloat16, float32, float16 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange flow.if index.multi_offset math.transcendental mem.load mem.masked_load mem.other mem.store pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where |
| `suite/perf/attention_kernel.py` | perf | attention | 9 | (2,2,16,32); (4,4,32,64); (1,1,8,16) | bfloat16, float32, float16 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange flow.if index.multi_offset math.transcendental mem.load mem.masked_load mem.other mem.store pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where |
| `suite/perf/attn_fwd_causal.py` | perf | attention | 9 | (2,2,16,32); (4,4,32,64); (1,1,8,16) | bfloat16, float32, float16 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange flow.if index.multi_offset math.transcendental mem.load mem.masked_load mem.other mem.store pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where |
| `suite/perf/batched_vecmat_mult.py` | perf | matmul | 6 | (32,32,32); (33,33,33) | bfloat16, float32, float16 | arith.add arith.mul cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both shape.trans |
| `suite/perf/block_sparse_attn.py` | perf | attention | 3 | (2,2,32,32); (4,4,64,64); (1,1,16,16) | float32 | arith.add arith.div arith.mul arith.sub cmp.compare construct.arange construct.full construct.zeros dot.matmul flow.dynamic_range flow.if flow.loop index.multi_offset math.clamp math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.dot_reduce pat.k_loop pat.masked_both pat.matmul_epilogue pat.persistent_reduce pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where shape.trans |
| `suite/perf/chebyshev_polynomial_t.py` | perf | elementwise_reduce | 6 | (128); (99) | bfloat16, float32, float16 | arith.add arith.mul arith.sub cmp.compare construct.arange flow.dynamic_range flow.loop mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both select.where |
| `suite/perf/cholesky_solve.py` | perf | elementwise_reduce | 6 | (8); (9) | bfloat16, float32, float16 | arith.add arith.div arith.mul arith.neg arith.sub flow.dynamic_range flow.loop mem.load mem.store |
| `suite/perf/chunk_delta_rule.py` | perf | linear_attention | 9 | (2,2,16,32,32); (4,4,17,64,64); (1,1,8,16,16) | bfloat16, float32, float16 | arith.add arith.mul arith.sub construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset mem.load mem.store pat.persistent_reduce pat.reduce_broadcast red.axis red.sum |
| `suite/perf/chunk_retention.py` | perf | linear_attention | 9 | (2,2,16,32,32); (4,4,32,64,64); (1,1,8,16,16) | bfloat16, float32, float16 | arith.add arith.div arith.mod arith.mul construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset mem.load mem.store pat.persistent_reduce red.axis red.sum |
| `suite/perf/chunk_retention_ops.py` | perf | linear_attention | 9 | (2,2,16,32,32); (4,4,32,64,64); (1,1,8,16,16) | bfloat16, float32, float16 | arith.add arith.div arith.mod arith.mul construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset mem.load mem.store pat.persistent_reduce red.axis red.sum |
| `suite/perf/combined_activation.py` | perf | elementwise_reduce | 6 | (16,32); (17,33) | bfloat16, float32, float16 | arith.add arith.mul arith.sub cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.axis red.sum |
| `suite/perf/context_attn_fwd.py` | perf | attention | 9 | (2,2,16,32); (4,4,32,64); (1,1,8,16) | bfloat16, float32, float16 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange flow.if index.multi_offset math.transcendental mem.load mem.masked_load mem.other mem.store pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where |
| `suite/perf/conv2d_add.py` | perf | conv_pool | 6 | (8); (9) | bfloat16, float32, float16 | arith.add arith.div arith.mod arith.mul arith.sub flow.dynamic_range flow.loop mem.load mem.store |
| `suite/perf/cos_signbit.py` | perf | elementwise_reduce | 2 | (128); (99) | float32 | arith.add arith.mul cast.explicit cmp.compare construct.arange dtype.int math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/cosine_compute.py` | perf | elementwise_reduce | 6 | (128); (103) | bfloat16, float32, float16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.masked_store mem.store pat.masked_both |
| `suite/perf/dequantize_matmul.py` | perf | quant | 6 | (32,32); (33,33) | bfloat16, float32, float16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both tune.autotune |
| `suite/perf/dequantize_rowwise.py` | perf | quant | 6 | (4,8); (7,11) | bfloat16, float32, float16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange mem.load mem.masked_load mem.masked_store mem.store pat.masked_both |
| `suite/perf/det.py` | perf | elementwise_reduce | 6 | (8); (9) | bfloat16, float32, float16 | arith.add arith.div arith.mod arith.mul arith.neg arith.sub cmp.compare flow.dynamic_range flow.loop math.abs mem.load mem.store select.where |
| `suite/perf/elu_linear.py` | perf | elementwise_reduce | 6 | (16,32); (17,33) | bfloat16, float32, float16 | arith.add arith.mul arith.sub cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.axis red.sum select.where |
| `suite/perf/erf.py` | perf | elementwise_reduce | 2 | (128); (99) | float32 | arith.add arith.mul cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/exp_mean.py` | perf | elementwise_reduce | 2 | (4,16); (4,97) | float32 | arith.add arith.div arith.mul cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.other mem.store red.axis red.sum select.where |
| `suite/perf/exp_sqrt.py` | perf | elementwise_reduce | 2 | (128); (99) | float32 | arith.add arith.mul cmp.compare construct.arange math.sqrt_rsqrt math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/fast_ce_loss.py` | perf | elementwise_reduce | 6 | (4,32); (7,35) | bfloat16, float32, float16 | arith.add arith.div arith.mul arith.neg arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange flow.if math.transcendental mem.load mem.masked_load mem.other mem.store pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum |
| `suite/perf/fast_rms_layernorm.py` | perf | norm | 6 | (4,64); (7,67) | bfloat16, float32, float16 | arith.add arith.div arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both red.axis red.sum |
| `suite/perf/flash_decode.py` | perf | attention | 9 | (2,2,32,32); (4,4,64,64); (1,1,16,16) | bfloat16, float32, float16 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare construct.arange construct.full construct.zeros flow.dynamic_range flow.loop index.multi_offset math.clamp math.transcendental mem.load mem.masked_load mem.other mem.store pat.persistent_reduce pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where |
| `suite/perf/fused_add_mul_groupnorm.py` | perf | norm | 6 | (8,64); (9,65) | bfloat16, float32, float16 | arith.add arith.div arith.mul arith.sub cmp.compare construct.arange math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.normalize pat.reduce_broadcast red.axis red.sum select.where |
| `suite/perf/fused_cross_entropy_log_softmax.py` | perf | softmax_xent | 6 | (8,32); (11,35) | bfloat16, float32, float16 | arith.add arith.div arith.mul arith.sub cmp.compare construct.arange flow.dynamic_range flow.loop math.transcendental mem.load mem.masked_load mem.other mem.store pat.persistent_reduce pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where |
| `suite/perf/fused_embedding_add_tanh.py` | perf | elementwise_reduce | 2 | (16,32); (17,33) | float32 | arith.add arith.mul arith.sub cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/fused_hardsigmoid_batch_norm.py` | perf | norm | 2 | (4,64); (5,65) | float32 | arith.add arith.div arith.mul arith.sub cmp.compare construct.arange math.clamp math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/fused_hstack_div.py` | perf | elementwise_reduce | 6 | (8); (9) | bfloat16, float32, float16 | arith.add arith.div arith.mul arith.sub cmp.compare construct.arange logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both select.where |
| `suite/perf/fused_index_select_eq.py` | perf | select_scan_index | 6 | (4,16); (5,17) | bfloat16, float32, float16 | arith.add arith.mul cmp.compare construct.arange mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/fused_layer_norm_relu_linear.py` | perf | norm | 6 | (4,5); (5,6) | bfloat16, float32, float16 | arith.add arith.div arith.mul arith.sub cmp.compare construct.arange index.multi_offset logic.bitwise math.clamp math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.normalize pat.reduce_broadcast red.axis red.sum select.where |
| `suite/perf/fused_lu_solve.py` | perf | elementwise_reduce | 6 | (8); (9) | bfloat16, float32, float16 | arith.add arith.div arith.mul arith.neg arith.sub cmp.compare flow.dynamic_range flow.loop math.abs mem.load mem.store select.where |
| `suite/perf/fused_pairwise_distance_adaptive_avg_pool2d.py` | perf | conv_pool | 6 | (4,8); (5,9) | bfloat16, float32, float16 | arith.add arith.div arith.mul arith.sub flow.dynamic_range flow.loop math.sqrt_rsqrt mem.load mem.store |
| `suite/perf/fused_recurrent_hgrn.py` | perf | linear_attention | 9 | (2,16,32); (3,17,33); (1,32,32) | bfloat16, float32, float16 | arith.add arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/fused_recurrent_retention.py` | perf | linear_attention | 9 | (2,2,16,32,32); (4,4,32,64,64); (1,1,8,16,16) | bfloat16, float32, float16 | arith.add arith.div arith.mod arith.mul construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset mem.load mem.store pat.persistent_reduce red.axis red.sum |
| `suite/perf/fused_repeat_interleave_log_softmax.py` | perf | softmax_xent | 6 | (3,4); (4,5) | bfloat16, float32, float16 | arith.add arith.div arith.mul arith.sub cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where |
| `suite/perf/fused_tile_exp.py` | perf | elementwise_reduce | 2 | (16); (17) | float32 | arith.add arith.mod arith.mul cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/gammaln.py` | perf | elementwise_reduce | 2 | (128); (99) | float32 | arith.add arith.div arith.mul arith.neg arith.sub cmp.compare construct.arange flow.dynamic_range flow.loop math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both select.where |
| `suite/perf/gather_1d.py` | perf | select_scan_index | 18 | (128,128); (97,100); (1,1) | int8, int32, int64, bfloat16, float32, float16 | arith.add arith.mul cmp.compare construct.arange mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/geglu_tanh_triton.py` | perf | elementwise_reduce | 6 | (2,128); (5,99) | bfloat16, float32, float16 | arith.add arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/gelu.py` | perf | elementwise_reduce | 2 | (128); (99) | float32 | arith.add arith.mul cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/gelu_conv2d.py` | perf | conv_pool | 6 | (8); (9) | bfloat16, float32, float16 | arith.add arith.div arith.mod arith.mul arith.sub flow.dynamic_range flow.loop math.transcendental mem.load mem.store |
| `suite/perf/gelu_std.py` | perf | elementwise_reduce | 2 | (4,16); (4,97) | float32 | arith.add arith.div arith.mul arith.sub cast.explicit cmp.compare construct.arange flow.dynamic_range flow.loop math.abs math.clamp math.sqrt_rsqrt math.transcendental mem.load mem.other mem.store pat.normalize pat.persistent_reduce pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where |
| `suite/perf/ifftshift.py` | perf | elementwise_reduce | 6 | (17); (18) | bfloat16, float32, float16 | arith.add arith.div arith.mod arith.mul cmp.compare construct.arange mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/index_select_cat.py` | perf | select_scan_index | 6 | (4,8); (5,9) | bfloat16, float32, float16 | arith.add arith.mul cmp.compare construct.arange index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/kldiv_compute.py` | perf | elementwise_reduce | 6 | (128); (120) | bfloat16, float32, float16 | arith.add arith.div arith.mul cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.masked_store mem.store pat.masked_both |
| `suite/perf/kldiv_ops.py` | perf | elementwise_reduce | 6 | (4,32); (7,35) | bfloat16, float32, float16 | arith.add arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange math.clamp math.transcendental mem.load mem.masked_load mem.other mem.store pat.reduce_broadcast red.axis red.sum select.where |
| `suite/perf/kldiv_triton.py` | perf | elementwise_reduce | 6 | (4,32); (7,35) | bfloat16, float32, float16 | arith.add arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange math.clamp math.transcendental mem.load mem.masked_load mem.other mem.store pat.reduce_broadcast red.axis red.sum select.where |
| `suite/perf/l2_norm_triton1.py` | perf | norm | 6 | (4,8); (8,16) | bfloat16, float32, float16 | arith.add arith.div arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both red.axis red.sum select.where |
| `suite/perf/l2_norm_triton2.py` | perf | norm | 6 | (4,8); (7,11) | bfloat16, float32, float16 | arith.add arith.div arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both red.axis red.sum |
| `suite/perf/leaky_relu.py` | perf | elementwise_reduce | 6 | (128); (99) | bfloat16, float32, float16 | arith.add arith.mul cmp.compare construct.arange mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both select.where |
| `suite/perf/leaky_relu_conv2d.py` | perf | conv_pool | 6 | (8); (9) | bfloat16, float32, float16 | arith.add arith.div arith.mod arith.mul arith.sub cmp.compare flow.dynamic_range flow.loop mem.load mem.store select.where |
| `suite/perf/log_softmax_linear.py` | perf | softmax_xent | 6 | (16,32); (17,33) | bfloat16, float32, float16 | arith.add arith.mul arith.sub cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.axis red.maxmin red.sum select.where |
| `suite/perf/logit.py` | perf | softmax_xent | 6 | (128); (99) | bfloat16, float32, float16 | arith.add arith.div arith.mul arith.sub cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/logsumexp.py` | perf | softmax_xent | 6 | (4,16); (4,97) | bfloat16, float32, float16 | arith.add arith.mul arith.neg arith.sub cast.explicit cmp.compare construct.arange dtype.int flow.dynamic_range flow.loop logic.bitwise math.abs math.clamp math.transcendental mem.load mem.other mem.store pat.persistent_reduce pat.reduce_broadcast red.axis red.maxmin red.sum select.where |
| `suite/perf/matmul.py` | perf | matmul | 6 | (16,16,16); (8,32,24) | bfloat16, float32, float16 | arith.add arith.mul cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both |
| `suite/perf/matmul_triton2.py` | perf | matmul | 6 | (32,32,32); (33,33,33) | bfloat16, float32, float16 | arith.add arith.mul cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both pat.matmul_epilogue select.where tune.autotune |
| `suite/perf/matmul_triton_autotune.py` | perf | matmul | 6 | (32,32,32); (33,33,33) | bfloat16, float32, float16 | arith.add arith.mul cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.if flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both pat.matmul_epilogue select.where tune.autotune |
| `suite/perf/matrix_multiply_and_row_dot.py` | perf | elementwise_reduce | 6 | (16,24,32); (17,25,33) | bfloat16, float32, float16 | arith.add arith.mul cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset logic.bitwise mem.load mem.masked_load mem.other mem.store pat.persistent_reduce red.axis red.sum |
| `suite/perf/matrix_vector_multip.py` | perf | elementwise_reduce | 6 | (8,16); (11,19) | bfloat16, float32, float16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange mem.load mem.masked_load mem.other mem.store red.axis red.sum tune.autotune |
| `suite/perf/max.py` | perf | elementwise_reduce | 6 | (4,16); (4,97) | bfloat16, float32, float16 | arith.add arith.mul arith.neg cmp.compare construct.arange flow.dynamic_range flow.loop logic.bitwise math.clamp mem.load mem.other mem.store pat.persistent_reduce red.axis red.maxmin select.where |
| `suite/perf/mean.py` | perf | elementwise_reduce | 6 | (4,16); (4,97) | bfloat16, float32, float16 | arith.add arith.div arith.mul cmp.compare construct.arange mem.load mem.masked_load mem.other mem.store red.axis red.sum select.where |
| `suite/perf/min.py` | perf | elementwise_reduce | 6 | (4,16); (4,97) | bfloat16, float32, float16 | arith.add arith.mul cmp.compare construct.arange flow.dynamic_range flow.loop logic.bitwise math.clamp mem.load mem.other mem.store pat.persistent_reduce red.axis red.maxmin select.where |
| `suite/perf/mul_relu.py` | perf | elementwise_reduce | 6 | (128); (99) | bfloat16, float32, float16 | arith.add arith.mul cmp.compare construct.arange math.clamp mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/mul_sub.py` | perf | elementwise_reduce | 6 | (128); (99) | bfloat16, float32, float16 | arith.add arith.mul arith.sub cmp.compare construct.arange mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/normalized_cosine_similarity.py` | perf | norm | 2 | (8,64); (11,67) | float32 | arith.add arith.div arith.mul cmp.compare construct.arange math.clamp math.sqrt_rsqrt mem.load mem.masked_load mem.other mem.store red.axis red.sum |
| `suite/perf/parallel_retention_attention.py` | perf | attention | 9 | (2,2,16,32,32); (4,4,32,64,64); (1,1,8,16,16) | bfloat16, float32, float16 | arith.add arith.div arith.mod arith.mul construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset mem.load mem.store pat.persistent_reduce red.axis red.sum |
| `suite/perf/pow.py` | perf | elementwise_reduce | 2 | (128); (99) | float32 | arith.add arith.mul cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/relu_conv2d.py` | perf | conv_pool | 6 | (8); (9) | bfloat16, float32, float16 | arith.add arith.div arith.mod arith.mul arith.sub flow.dynamic_range flow.loop math.clamp mem.load mem.store |
| `suite/perf/relu_strided_buffer.py` | perf | elementwise_reduce | 6 | (16); (19) | bfloat16, float32, float16 | arith.add arith.mul cmp.compare construct.arange math.clamp mem.load mem.masked_load mem.masked_store mem.store pat.masked_both |
| `suite/perf/rsqrt.py` | perf | elementwise_reduce | 2 | (128); (99) | float32 | arith.add arith.div arith.mul cmp.compare construct.arange math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/scaled_add_dot.py` | perf | elementwise_reduce | 6 | (128); (99) | bfloat16, float32, float16 | arith.add arith.mul cmp.compare construct.arange flow.dynamic_range flow.loop mem.load mem.masked_load mem.other mem.store pat.persistent_reduce red.axis red.sum |
| `suite/perf/scaled_add_norm.py` | perf | norm | 6 | (128); (99) | bfloat16, float32, float16 | arith.add arith.mul cmp.compare construct.arange flow.dynamic_range flow.loop math.sqrt_rsqrt mem.load mem.masked_load mem.other mem.store pat.persistent_reduce red.axis red.sum |
| `suite/perf/selu.py` | perf | elementwise_reduce | 2 | (128); (99) | float32 | arith.add arith.mul arith.sub cmp.compare construct.arange math.clamp math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/sigmoid.py` | perf | elementwise_reduce | 2 | (128); (99) | float32 | arith.add arith.mul cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/sigmoid_adaptive_avg_pool2d.py` | perf | conv_pool | 6 | (4,64); (24,64) | bfloat16, float32, float16 | arith.add arith.div arith.mul cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.other mem.store red.axis red.sum |
| `suite/perf/sigmoid_argmax.py` | perf | select_scan_index | 2 | (4,16); (4,97) | float32 | arith.add arith.mul arith.neg cmp.compare construct.arange flow.dynamic_range flow.loop logic.bitwise math.clamp math.transcendental mem.load mem.other mem.store pat.persistent_reduce red.axis red.maxmin select.where |
| `suite/perf/sigmoid_batch_norm.py` | perf | norm | 2 | (4,64); (5,65) | float32 | arith.add arith.div arith.mul arith.sub cmp.compare construct.arange math.sqrt_rsqrt math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/signbit_bitwise_and.py` | perf | elementwise_reduce | 2 | (128); (99) | int32 | arith.add arith.mul cmp.compare construct.arange logic.bitwise mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/silu_batch_norm.py` | perf | norm | 2 | (4,64); (5,65) | float32 | arith.add arith.div arith.mul arith.sub cmp.compare construct.arange math.sqrt_rsqrt math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/sin_computation.py` | perf | elementwise_reduce | 2 | (16); (19) | float32 | arith.add arith.mul cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.masked_store mem.store pat.masked_both |
| `suite/perf/sin_kernel.py` | perf | elementwise_reduce | 2 | (16); (19) | float32 | arith.add arith.mul cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.masked_store mem.store pat.masked_both |
| `suite/perf/softmax.py` | perf | softmax_xent | 6 | (4,16); (4,97) | bfloat16, float32, float16 | arith.add arith.div arith.mul arith.sub cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where |
| `suite/perf/softmax_log.py` | perf | softmax_xent | 2 | (4,16); (4,97) | float32 | arith.add arith.div arith.mul arith.neg arith.sub cast.explicit cmp.compare construct.arange dtype.int flow.dynamic_range flow.loop logic.bitwise math.clamp math.transcendental mem.load mem.other mem.store pat.persistent_reduce pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where |
| `suite/perf/softmax_mul.py` | perf | softmax_xent | 6 | (4,16); (4,97) | bfloat16, float32, float16 | arith.add arith.div arith.mul arith.sub cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.reduce_broadcast pat.softmax red.axis red.maxmin red.sum select.where |
| `suite/perf/softplus_linear.py` | perf | elementwise_reduce | 6 | (16,32); (17,33) | bfloat16, float32, float16 | arith.add arith.div arith.mul cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce red.axis red.sum select.where |
| `suite/perf/sqrt.py` | perf | elementwise_reduce | 2 | (128); (99) | float32 | arith.add arith.mul cmp.compare construct.arange math.sqrt_rsqrt mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/sqrt_exp.py` | perf | elementwise_reduce | 2 | (128); (99) | float32 | arith.add arith.mul cmp.compare construct.arange math.sqrt_rsqrt math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/square_matrix.py` | perf | elementwise_reduce | 6 | (4,8); (5,9) | bfloat16, float32, float16 | arith.add arith.mul cmp.compare construct.arange mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/std.py` | perf | elementwise_reduce | 2 | (4,16); (4,97) | float32 | arith.add arith.div arith.mul arith.sub cast.explicit cmp.compare construct.arange flow.dynamic_range flow.loop math.abs math.clamp math.sqrt_rsqrt mem.load mem.other mem.store pat.normalize pat.persistent_reduce pat.reduce_broadcast red.axis red.maxmin red.sum select.where |
| `suite/perf/swiglu_fwd.py` | perf | elementwise_reduce | 6 | (4,64); (8,128) | bfloat16, float32, float16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both tune.autotune |
| `suite/perf/swiglu_triton.py` | perf | elementwise_reduce | 6 | (4,64); (7,67) | bfloat16, float32, float16 | arith.add arith.mul cast.explicit cast.to_fp32 cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/tanh.py` | perf | elementwise_reduce | 6 | (128); (97) | bfloat16, float32, float16 | arith.add arith.div arith.mul arith.sub cast.explicit cast.to_fp32 cmp.compare construct.arange math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both |
| `suite/perf/tanh_linear.py` | perf | elementwise_reduce | 6 | (16,32); (17,33) | bfloat16, float32, float16 | arith.add arith.mul arith.sub cmp.compare construct.arange construct.zeros flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.masked_both pat.persistent_reduce pat.reduce_broadcast red.axis red.sum |
| `suite/perf/triton_linear_activation.py` | perf | matmul | 6 | (32,32,32); (42,32,32) | bfloat16, float32, float16 | arith.add arith.mul cmp.compare construct.arange construct.zeros dot.matmul flow.dynamic_range flow.loop index.multi_offset logic.bitwise math.transcendental mem.load mem.masked_load mem.masked_store mem.other mem.store pat.k_loop pat.masked_both pat.matmul_epilogue tune.autotune |

## 6. Gaps, exclusions and notes for planning

1. **No in-subset language gaps**: the declared subset is closed over the
  kept operators (SUBSET.md principle 3); every construct the corpus calls
  is in the recorded api-spec. The refusal boundary is the exclusion table
  in §3.
2. **`tl.swizzle2d`** is declared in the subset but called by no shipped
  operator (`corpus_calls=0`): no corpus result exercises it.
3. **fp64 dead branches**: 16 operators contain `tl.float64` dtype-dispatch
  branches that never fire for the declared cases; the frontend must still
  fold the constexpr comparison.
4. **AGENT_GUIDE case-count drift**: `AGENT_GUIDE.md` §1 says 2893 cases
  (the v2 number); the corpus's own enumeration and SUITE_V3.md say 2734.
  The commands were run; 2734 is recorded.
5. **autotune**: 11 operators declare `@triton.autotune` spaces (the
  compiler must consume the config space itself; the reference devices'
  autotuner limitation is documented in AGENT_GUIDE §6).
6. **bf16 pointer duality** (host float32-cast vs host uint16-bitview) and
  **masked load without `other`** (undefined at disabled positions — never
  default to zero) are the two declared deep pitfalls (AGENT_GUIDE §7).
7. **Pointer tables**: `grouped_gemm_kernel` passes device addresses inside
  buffers (`pointer_table_relocations`); its host-address bytes differ per
  construction and are excluded from the golden cache.
8. **Value-level dtype introspection** is part of the surface even though it
  is not a `tl.*` call: 81 operators read `ptr.type.element_ty`, 60 read
  `x.dtype.element_ty`, and 15 branch on dtype predicates
  (`is_floating()`/`is_int_signed()`/`is_int_unsigned()`/`int_bitwidth`,
  e.g. `argmax_kernel_inner`) — the frontend must fold these constexpr
  comparisons during specialization. Pointer *increment* (`p += stride`)
  appears in 20 operators (descriptor-style advance producing a new pointer).

## 7. Reproduction

```bash
set -a; . ./.env; set +a
# operator set + scan (500 files, not the 42 harness files)
python3 -m compiler_agent --root . operator-set --glob 'suite/dev/*.py,suite/perf/*.py' --source 'ops/README.md ...'
python3 -m compiler_agent --root . ingest-ops
# corpus's own tier enumeration (numbers recorded above)
cd ops && python3 harness/compiler_api/run_cases.py --manifest suite/manifest.json --dry-run --group-order
cd ops && python3 harness/compiler_api/run_cases.py --manifest suite/manifest.json --dry-run --identities
# engine records
python3 -m compiler_agent --root . group-order --group suite/dev --group suite/perf --source 'ops/harness/compiler_api/run_cases.py'
python3 -m compiler_agent --root . record-case-totals --json '{"suite/dev": 2192, "suite/perf": 542}' --source '...'

# gate check
python3 -m compiler_agent --root . --json gates   # G2 PASS
```

Scanner's raw observed token sample (1068 tokens, including case-layer
numpy calls) is recorded in `PROJECT_STATE.json` → `workload.observed_sample`;
the language-relevant subset of that sample is the api-spec in §3, and the
semantic feature taxonomy is §4. The top language tokens observed:
`tl.constexpr` 1595, `tl.load` 1331, `tl.arange` 1052, `tl.float32` 883,
`tl.store` 791, `tl.where` 732, `tl.program_id` 592, `triton.jit` 500,
`tl.reshape` 377, `tl.sum` 351, `tl.dot` 305.
