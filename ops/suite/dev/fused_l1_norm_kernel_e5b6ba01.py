"""mk_fused_l1_norm_kernel_e5b6ba01: makora train 第 62489 行的 Triton 解:fused_l1_norm_kernel;ref 为 torch 参考实现的 numpy 移植。

模式: memory.load.masked、reduce.sum、args.program_id、creation.arange。

文件只有两层:
  ① fused_l1_norm_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
                     怎么分配、搬运、启动由 runner 的 Device 决定。
"""

OPERATOR = {"name": "hidden/fused_l1_norm_kernel_e5b6ba01", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ['memory.load.masked', 'reduce.sum', 'args.program_id', 'creation.arange']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 62489,
          "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d",
          "original_sha256": "e5b6ba01c0f1cb1c73b00ce2732ebfe3397bb361ad2df8ea91c884d85171238c"}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def fused_l1_norm_kernel(
    x_ptr,
    out_ptr,
    row_size,
    BLOCK_SIZE: tl.constexpr,
):
    """
    Fused L1 normalization kernel with optimized memory access pattern.
    
    Optimization features:
    1. Fused computation: eliminates intermediate tensor and extra global memory transactions
    2. Vectorized loads/stores: BLOCK_SIZE is multiple of 16 for automatic vectorization
    3. Optimized loop pipelining: num_stages=2 for memory-bound operations
    4. Tuned launch parameters: adaptive BLOCK_SIZE and num_warps based on problem size
    """
    row_idx = tl.program_id(0)
    row_start = row_idx * row_size
    
    # Use float32 accumulator to maintain precision
    sum_abs = 0.0
    
    # First pass: compute sum of absolute values
    # tl.range with num_stages enables software pipelining for better performance
    for block_start in tl.range(0, row_size, BLOCK_SIZE, num_stages=2):
        # Create block offsets with contiguous access pattern
        offsets = row_start + block_start + tl.arange(0, BLOCK_SIZE)
        mask = offsets < row_start + row_size
        
        # Load data - Triton automatically generates vectorized instructions
        # when BLOCK_SIZE is multiple of 16 and data is aligned
        x = tl.load(x_ptr + offsets, mask=mask, other=0.0)
        
        # Fused abs + sum reduction
        sum_abs += tl.sum(tl.abs(x))
    
    # Compute mean (divide by row_size)
    mean = sum_abs / row_size
    
    # Second pass: normalize and store
    for block_start in tl.range(0, row_size, BLOCK_SIZE, num_stages=2):
        offsets = row_start + block_start + tl.arange(0, BLOCK_SIZE)
        mask = offsets < row_start + row_size
        
        x = tl.load(x_ptr + offsets, mask=mask, other=0.0)
        out = x / mean
        
        # Vectorized store
        tl.store(out_ptr + offsets, out, mask=mask)

# ------------------------------------------------------------------ ② case 层
# 典型用法:makora 行的 Triton 解,ref 为其 torch 参考实现的 numpy 移植;
# 输入按原 get_inputs 的构造种类复现(randn/zeros/randint...),权重两模型共用。
SHAPES = ((16,), (32,))
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

    out = np.zeros_like(x)

    args = {'x_ptr': x, 'out_ptr': out, 'row_size': x.shape[1]}
    meta = {'BLOCK_SIZE': 16}
    r = ref({'x': x}, meta)
    expected = {'out_ptr': r["_o0"].astype(out.dtype)}
    case = {"args": args, "meta": meta, "grid": (x.shape[0],),
            "outputs": ('out_ptr',), "expected": expected}
    tol = 1e-4
    # fp32 dot 是 IEEE;低精度输入按 fp32 累加,按 expected 幅值自适应 atol
    case["comparison"] = {n: {"comparator": "allclose", "exact": False,
                              "rtol": tol,
                              "atol": max(1e-4, 2e-3 * float(np.abs(expected[n]).max())),
                              "equal_nan": True}
                              for n in case["outputs"]}
    case["launch_meta"] = {'num_warps': 4}

    return case


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, fused_l1_norm_kernel, DTYPES,
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
