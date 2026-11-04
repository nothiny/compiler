"""mk_matmul_at_b_kernel_043f2a05: makora train 第 26570 行的 Triton 解:matmul_at_b_kernel;ref 为 torch 参考实现的 numpy 移植。

模式: memory.load.masked、linalg.dot、args.program_id、creation.arange。

文件只有两层:
  ① matmul_at_b_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
                     怎么分配、搬运、启动由 runner 的 Device 决定。
"""

OPERATOR = {"name": "hidden/matmul_at_b_kernel_043f2a05", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ['memory.load.masked', 'linalg.dot', 'args.program_id', 'creation.arange']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 26570,
          "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d",
          "original_sha256": "043f2a052a4e377a42cbba030d2403422630bb0a3952b7480e06d7c8c406a672"}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def matmul_at_b_kernel(
    a_ptr, b_ptr, c_ptr,
    M, N, K,
    stride_ak, stride_am,
    stride_bk, stride_bn,
    stride_cm, stride_cn,
    BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr,
    GROUP_SIZE_M: tl.constexpr
):
    # -----------------------------------------------------------
    # Map Program ID to spatial location (Grouped GEMM Swizzling)
    # -----------------------------------------------------------
    # This grouping strategy maximizes L2 cache reuse of B tiles by processing 
    # a group of M blocks for each N block.
    pid = tl.program_id(axis=0)
    num_pid_m = tl.cdiv(M, BLOCK_M)
    num_pid_n = tl.cdiv(N, BLOCK_N)
    num_pid_in_group = GROUP_SIZE_M * num_pid_n
    group_id = pid // num_pid_in_group
    first_pid_m = group_id * GROUP_SIZE_M
    group_size_m = tl.minimum(num_pid_m - first_pid_m, GROUP_SIZE_M)
    pid_m = first_pid_m + (pid % group_size_m)
    pid_n = (pid % num_pid_in_group) // group_size_m

    # -----------------------------------------------------------
    # Pointer Arithmetics & Offsets
    # -----------------------------------------------------------
    offs_m = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    offs_k = tl.arange(0, BLOCK_K)

    # Pointers to A (K, M) and B (K, N)
    # A is loaded as (BLOCK_K, BLOCK_M) chunks - contiguous rows
    # B is loaded as (BLOCK_K, BLOCK_N) chunks - contiguous rows
    a_ptrs = a_ptr + (offs_k[:, None] * stride_ak + offs_m[None, :] * stride_am)
    b_ptrs = b_ptr + (offs_k[:, None] * stride_bk + offs_n[None, :] * stride_bn)

    # -----------------------------------------------------------
    # Main Computation Loop
    # -----------------------------------------------------------
    accumulator = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)

    for k in range(0, K, BLOCK_K):
        k_remaining = K - k
        
        # Create masks for the current block to handle arbitrary dimensions safeley
        mask_k = offs_k < k_remaining
        
        # Load A: (BLOCK_K, BLOCK_M)
        # 'evict_first' because A tiles change rapidly in the inner loop (streaming)
        a = tl.load(a_ptrs, mask=mask_k[:, None] & (offs_m[None, :] < M), other=0.0, eviction_policy='evict_first')
        
        # Load B: (BLOCK_K, BLOCK_N)
        # 'evict_last' because B tiles are reused across the swizzled group of M blocks
        b = tl.load(b_ptrs, mask=mask_k[:, None] & (offs_n[None, :] < N), other=0.0, eviction_policy='evict_last')
        
        # Compute C += A^T @ B
        # We loaded 'a' as (BLOCK_K, BLOCK_M), so transposing it in registers 
        # gives (BLOCK_M, BLOCK_K) efficiently without strided memory loads.
        accumulator += tl.dot(tl.trans(a), b)
        
        # Advance pointers
        a_ptrs += BLOCK_K * stride_ak
        b_ptrs += BLOCK_K * stride_bk

    # -----------------------------------------------------------
    # Store Result
    # -----------------------------------------------------------
    c_ptrs = c_ptr + (stride_cm * offs_m[:, None] + stride_cn * offs_n[None, :])
    c_mask = (offs_m[:, None] < M) & (offs_n[None, :] < N)
    tl.store(c_ptrs, accumulator, mask=c_mask)

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

    args = {'a_ptr': A, 'b_ptr': B, 'c_ptr': C, 'M': A.shape[1], 'N': B.shape[1], 'K': A.shape[0], 'stride_ak': int(A.strides[0] // A.itemsize), 'stride_am': int(A.strides[1] // A.itemsize), 'stride_bk': int(B.strides[0] // B.itemsize), 'stride_bn': int(B.strides[1] // B.itemsize), 'stride_cm': int(C.strides[0] // C.itemsize), 'stride_cn': int(C.strides[1] // C.itemsize)}
    meta = {'BLOCK_M': 128, 'BLOCK_N': 256, 'BLOCK_K': 32, 'GROUP_SIZE_M': 8}
    r = ref({'A': A, 'B': B}, meta)
    expected = {'c_ptr': r["_o0"].astype(C.dtype)}
    case = {"args": args, "meta": meta, "grid": ((triton.cdiv(A.shape[1], (128)) * triton.cdiv(B.shape[1], (256))),),
            "outputs": ('c_ptr',), "expected": expected}
    tol = 1e-2
    # fp32 dot 是 IEEE;低精度输入按 fp32 累加,按 expected 幅值自适应 atol
    case["comparison"] = {n: {"comparator": "allclose", "exact": False,
                              "rtol": tol,
                              "atol": max(4e-2, 2e-3 * float(np.abs(expected[n]).max())),
                              "equal_nan": True}
                              for n in case["outputs"]}
    case["launch_meta"] = {'num_stages': 3, 'num_warps': 8}

    return case


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, matmul_at_b_kernel, DTYPES,
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
