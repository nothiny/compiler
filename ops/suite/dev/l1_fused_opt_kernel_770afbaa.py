"""mk_l1_fused_opt_kernel_770afbaa: makora train 第 61973 行的 Triton 解:l1_fused_opt_kernel;ref 为 torch 参考实现的 numpy 移植。

模式: memory.load.masked、reduce.sum、control.loop_runtime_bound、args.program_id、creation.arange。

文件只有两层:
  ① l1_fused_opt_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
                     怎么分配、搬运、启动由 runner 的 Device 决定。
"""

OPERATOR = {"name": "hidden/l1_fused_opt_kernel_770afbaa", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ['memory.load.masked', 'reduce.sum', 'control.loop_runtime_bound', 'args.program_id', 'creation.arange']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 61973,
          "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d",
          "original_sha256": "770afbaa19eeacdff78e79b44f35af6471d6bf42f0ce2041bc0d68013df2d3a1"}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def l1_fused_opt_kernel(
    x_ptr,
    y_ptr,
    stride_row,
    n_cols,
    BLOCK_SIZE: tl.constexpr,
    UNROLL: tl.constexpr
):
    # Map row to program
    row_idx = tl.program_id(0).to(tl.int64)
    row_start_offset = row_idx * stride_row
    
    # Pointers
    x_row_ptr = x_ptr + row_start_offset
    y_row_ptr = y_ptr + row_start_offset
    
    # 1. Alignment Prologue
    # Calculate shift to align accesses to 32-element (128-byte) boundaries
    # We want (row_start_offset + shift) % 32 == 0. 
    # This ensures coalesced accesses for the main loop.
    shift = ((-row_start_offset) & 31).to(tl.int32)
    
    # Accumulator: Vector of BLOCK_SIZE to avoid inner-loop reduction
    accum = tl.zeros((BLOCK_SIZE,), dtype=tl.float32)
    
    # Handle prologue
    if shift > 0:
        offs = tl.arange(0, BLOCK_SIZE)
        mask = offs < shift
        # Safety check for very small n_cols
        mask = mask & (offs < n_cols)
        val = tl.load(x_row_ptr + offs, mask=mask, other=0.0)
        accum += tl.abs(val)
        
    # Main loop setup
    aligned_start = shift
    chunk_size = BLOCK_SIZE * UNROLL
    
    # Calculate where the aligned main loop ends
    aligned_end = aligned_start + ((n_cols - aligned_start) // chunk_size) * chunk_size
    
    offs_base = tl.arange(0, BLOCK_SIZE)
    
    # 2. Main Loop (Unrolled)
    # Iterating with a large step (UNROLL * BLOCK_SIZE) reduces loop overhead
    for off in range(aligned_start, aligned_end, chunk_size):
        for u in range(UNROLL):
            u_off = off + u * BLOCK_SIZE
            val = tl.load(x_row_ptr + u_off + offs_base)
            accum += tl.abs(val)
            
    # 3. Semi-Epilogue: Handle remaining full blocks
    tail_start = aligned_end
    tail_end = aligned_start + ((n_cols - aligned_start) // BLOCK_SIZE) * BLOCK_SIZE
    
    for off in range(tail_start, tail_end, BLOCK_SIZE):
        val = tl.load(x_row_ptr + off + offs_base)
        accum += tl.abs(val)
        
    # 4. Final Epilogue: Masked tail
    if tail_end < n_cols:
        off = tail_end
        mask = (off + offs_base) < n_cols
        val = tl.load(x_row_ptr + off + offs_base, mask=mask, other=0.0)
        accum += tl.abs(val)
        
    # Final Reduction: Sum across the block once per row
    sum_val = tl.sum(accum)
    scale = n_cols / sum_val
    
    # -----------------------------------------------------------------------
    # PASS 2: Scale and Write
    # -----------------------------------------------------------------------
    # We mirror the access pattern to maximize L2 cache hits. 
    # We explicitly avoided 'evict_last' in Pass 1 to keep data in L2.
    
    # 1. Prologue
    if shift > 0:
        offs = tl.arange(0, BLOCK_SIZE)
        mask = offs < shift
        mask = mask & (offs < n_cols)
        val = tl.load(x_row_ptr + offs, mask=mask, other=0.0)
        tl.store(y_row_ptr + offs, val * scale, mask=mask)
        
    # 2. Main Loop
    for off in range(aligned_start, aligned_end, chunk_size):
        for u in range(UNROLL):
            u_off = off + u * BLOCK_SIZE
            val = tl.load(x_row_ptr + u_off + offs_base)
            tl.store(y_row_ptr + u_off + offs_base, val * scale)
            
    # 3. Semi-Epilogue
    for off in range(tail_start, tail_end, BLOCK_SIZE):
        val = tl.load(x_row_ptr + off + offs_base)
        tl.store(y_row_ptr + off + offs_base, val * scale)
        
    # 4. Final Epilogue
    if tail_end < n_cols:
        off = tail_end
        mask = (off + offs_base) < n_cols
        val = tl.load(x_row_ptr + off + offs_base, mask=mask, other=0.0)
        tl.store(y_row_ptr + off + offs_base, val * scale, mask=mask)

# ------------------------------------------------------------------ ② case 层
# 典型用法:makora 行的 Triton 解,ref 为其 torch 参考实现的 numpy 移植;
# 输入按原 get_inputs 的构造种类复现(randn/zeros/randint...),权重两模型共用。
SHAPES = ((128,), (127,))
DTYPES = ('float32', 'float16', 'bfloat16')
_HOST_DTYPE = {"float32": np.float32}

def _sigmoid(v):
    return 1.0 / (1.0 + np.exp(-v))


def _silu(v):
    return v / (1.0 + np.exp(-v))


def _relu(v):
    return np.maximum(v, 0.0)


def _rsqrt(v):
    return 1.0 / np.sqrt(v)


def _erf(v):
    """Abramowitz-Stegun 7.1.26,|误差| < 1.5e-7(numpy 无 erf,不引 scipy)。"""
    s = np.sign(v)
    a = np.abs(np.asarray(v, dtype=np.float64))
    t = 1.0 / (1.0 + 0.3275911 * a)
    y = 1.0 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t
                - 0.284496736) * t + 0.254829592) * t * np.exp(-a * a)
    return s * y


def _softmax(v, axis):
    m = v.max(axis=axis, keepdims=True)
    e = np.exp(v - m)
    return e / e.sum(axis=axis, keepdims=True)


def _layer_norm(v, w, b, eps):
    mu = v.mean(axis=-1, keepdims=True)
    var = ((v - mu) ** 2).mean(axis=-1, keepdims=True)
    return (v - mu) / np.sqrt(var + eps) * w + b



def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    from case_utils import fast_rng
    rng = fast_rng(seed)
    b = int(shape[0])
    x = rng.standard_normal((b, 8193,)).astype(np.float32)

    y = np.zeros_like(x)

    args = {'x_ptr': x, 'y_ptr': y, 'stride_row': int(x.strides[0] // x.itemsize), 'n_cols': x.shape[1]}
    meta = {'BLOCK_SIZE': 4096, 'UNROLL': 4}
    r = ref({'x': x}, meta)
    expected = {'y_ptr': r["_o0"].astype(y.dtype)}
    case = {"args": args, "meta": meta, "grid": (x.shape[0],),
            "outputs": ('y_ptr',), "expected": expected}
    tol = 1e-4
    # fp32 dot 是 IEEE;低精度输入按 fp32 累加,按 expected 幅值自适应 atol
    case["comparison"] = {n: {"comparator": "allclose", "exact": False,
                              "rtol": tol,
                              "atol": max(1e-4, 2e-3 * float(np.abs(expected[n]).max())),
                              "equal_nan": True}
                              for n in case["outputs"]}
    case["launch_meta"] = {'num_warps': 8}

    return case


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, l1_fused_opt_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed)


def ref(args, meta):
    x = np.asarray(args['x'], dtype=np.float64)
    return {"_o0": (x / np.mean(np.abs(x), axis=1, keepdims=True))}


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float32'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float32': 'float32'}


def make_case(shape=None, dtype=None, seed=None):
    """Enriched case builder: dtype-generic, one shared tolerance table.

    The original case layer built one float case.  For fp16/bf16 we build that
    same case, temporarily wrap the module ``ref`` so the expected outputs are
    computed from the low-precision inputs, then re-express the buffers in the
    requested dtype (``case_utils.dtype_case``).  Integer / bool requests go
    through the original builder unchanged.
    """
    from case_utils import convert_float_arrays, dtype_case, dtype_name

    requested = dtype_name(dtype) or DTYPES[0]
    if requested in _ENRICH_ORIGINAL_DTYPES:
        # declared before enrichment: the operator's own case builder and tolerances
        return _ENRICH_ORIGINAL_MAKE_CASE(shape=shape, dtype=_ENRICH_ORIGINAL_DTYPES[requested], seed=seed)
    if requested not in _ENRICH_TARGETS:
        return _ENRICH_ORIGINAL_MAKE_CASE(shape=shape, dtype=dtype, seed=seed)
    if requested == _ENRICH_BASE:
        case = _ENRICH_ORIGINAL_MAKE_CASE(shape=shape, dtype=requested, seed=seed)
        case["dtype"] = requested
        if _ENRICH_APPLY_FOR_BASE:
            case = dtype_case(case, requested, ref=None)
        return case
    original_ref = ref

    def enriched_ref(args, meta):
        return original_ref(convert_float_arrays(args, requested), meta)

    globals()["ref"] = enriched_ref
    try:
        case = _ENRICH_ORIGINAL_MAKE_CASE(shape=shape, dtype=_ENRICH_BASE, seed=seed)
    finally:
        globals()["ref"] = original_ref
    return dtype_case(case, requested, ref=None)
