"""mk_matmul_atb_optimized_kernel_2044087e: makora train 第 26852 行的 Triton 解:matmul_atb_optimized_kernel;ref 为 torch 参考实现的 numpy 移植。

模式: memory.load.masked、linalg.dot、args.program_id、creation.arange。

文件只有两层:
  ① matmul_atb_optimized_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
                     怎么分配、搬运、启动由 runner 的 Device 决定。
"""

OPERATOR = {"name": "hidden/matmul_atb_optimized_kernel_2044087e", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ['memory.load.masked', 'linalg.dot', 'args.program_id', 'creation.arange']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 26852,
          "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d",
          "original_sha256": "2044087ed3074be753735557ecde131abfc570a14b196d304e92d3fb13ddeaec"}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def matmul_atb_optimized_kernel(
    A_ptr,  # *fp32/16, A of shape (K, M)
    B_ptr,  # *fp32/16, B of shape (K, N)
    C_ptr,  # *fp32/16, C of shape (M, N)
    M,      # int32, rows of C
    N,      # int32, cols of C
    K,      # int32, reduction dim
    stride_a0, stride_a1,  # strides for A (K, M)
    stride_b0, stride_b1,  # strides for B (K, N)
    stride_c0, stride_c1,  # strides for C (M, N)
    BLOCK_M: tl.constexpr,
    BLOCK_N: tl.constexpr,
    BLOCK_K: tl.constexpr,
):
    # 2D program id
    pid_m = tl.program_id(0)
    pid_n = tl.program_id(1)

    # Offsets for this tile
    offs_m = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    offs_k = tl.arange(0, BLOCK_K)

    # Give compiler alignment hints to enable vectorization
    tl.multiple_of(offs_m, BLOCK_M)
    tl.multiple_of(offs_n, BLOCK_N)
    tl.multiple_of(offs_k, BLOCK_K)

    # Pointers for the first K-block
    # A is stored as (K, M). We load tiles as (BLOCK_K, BLOCK_M) (k, m)
    # and transpose in registers to get the logical (BLOCK_M, BLOCK_K).
    a_ptrs = A_ptr + offs_k[:, None] * stride_a0 + offs_m[None, :] * stride_a1
    # B is (K, N) and is consumed as (BLOCK_K, BLOCK_N) directly.
    b_ptrs = B_ptr + offs_k[:, None] * stride_b0 + offs_n[None, :] * stride_b1

    # Accumulator in FP32
    acc = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)

    k = 0
    while k < K:
        k_idx = k + offs_k

        a_mask = (k_idx[:, None] < K) & (offs_m[None, :] < M)
        b_mask = (k_idx[:, None] < K) & (offs_n[None, :] < N)

        a = tl.load(a_ptrs, mask=a_mask, other=0.0)
        b = tl.load(b_ptrs, mask=b_mask, other=0.0)

        # Compute in FP32; transpose A tile to match GEMM layout
        a = tl.trans(a.to(tl.float32))
        b = b.to(tl.float32)

        acc += tl.dot(a, b)

        # Advance to next K-block
        a_ptrs += BLOCK_K * stride_a0
        b_ptrs += BLOCK_K * stride_b0
        k += BLOCK_K

    # Write back result
    c_ptrs = C_ptr + offs_m[:, None] * stride_c0 + offs_n[None, :] * stride_c1
    c_mask = (offs_m[:, None] < M) & (offs_n[None, :] < N)
    tl.store(c_ptrs, acc, mask=c_mask)

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
    A = rng.standard_normal((b, 128,)).astype(np.float32)
    B = rng.standard_normal((b, 256,)).astype(np.float32)

    C = np.zeros((A.shape[1], B.shape[1],), dtype=np.float32)

    args = {'A_ptr': A, 'B_ptr': B, 'C_ptr': C, 'M': A.shape[1], 'N': B.shape[1], 'K': A.shape[0], 'stride_a0': int(A.strides[0] // A.itemsize), 'stride_a1': int(A.strides[1] // A.itemsize), 'stride_b0': int(B.strides[0] // B.itemsize), 'stride_b1': int(B.strides[1] // B.itemsize), 'stride_c0': int(C.strides[0] // C.itemsize), 'stride_c1': int(C.strides[1] // C.itemsize)}
    meta = {'BLOCK_M': 128, 'BLOCK_N': 128, 'BLOCK_K': 32}
    r = ref({'A': A, 'B': B}, meta)
    expected = {'C_ptr': r["_o0"].astype(C.dtype)}
    case = {"args": args, "meta": meta, "grid": (triton.cdiv(A.shape[1], (128)), triton.cdiv(B.shape[1], (128)),),
            "outputs": ('C_ptr',), "expected": expected}
    tol = 1e-2
    # fp32 dot 是 IEEE;低精度输入按 fp32 累加,按 expected 幅值自适应 atol
    case["comparison"] = {n: {"comparator": "allclose", "exact": False,
                              "rtol": tol,
                              "atol": max(4e-2, 2e-3 * float(np.abs(expected[n]).max())),
                              "equal_nan": True}
                              for n in case["outputs"]}
    case["launch_meta"] = {'num_stages': 4, 'num_warps': 8}

    return case


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, matmul_atb_optimized_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed)


def ref(args, meta):
    A = np.asarray(args['A'], dtype=np.float64)
    B = np.asarray(args['B'], dtype=np.float64)
    return {"_o0": np.matmul(A.T, B)}


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
