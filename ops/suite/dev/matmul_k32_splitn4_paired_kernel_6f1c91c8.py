"""mk_matmul_k32_splitn4_paired_kernel_6f1c91c8: makora train 第 15553 行的 Triton 解:matmul_k32_splitn4_paired_kernel;ref 为 torch 参考实现的 numpy 移植。

模式: linalg.dot、args.program_id、creation.arange。

文件只有两层:
  ① matmul_k32_splitn4_paired_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
                     怎么分配、搬运、启动由 runner 的 Device 决定。
"""

OPERATOR = {"name": "hidden/matmul_k32_splitn4_paired_kernel_6f1c91c8", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ['linalg.dot', 'args.program_id', 'creation.arange']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 15553,
          "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d",
          "original_sha256": "6f1c91c83ce55287b9eaf14b76bf17e3bb0dee151f68e76c07eb43d514e6c483"}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def matmul_k32_splitn4_paired_kernel(
    A_ptr, B_ptr, C_ptr,
    M, N, K,                      # A[M, K], B[K, N], C[M, N] with K == 32
    stride_am, stride_ak,
    stride_bk, stride_bn,
    stride_cm, stride_cn,
    BLOCK_M: tl.constexpr,        # 128
    BLOCK_N: tl.constexpr,        # 64  (two tiles per pair -> effective 128)
    BLOCK_K: tl.constexpr,        # 32 (matches K exactly)
    GROUP_M: tl.constexpr,        # 8
    SPLIT_PAIRS: tl.constexpr     # 2 pairs -> 4 N-tiles per program
):
    # 1D grouped swizzle to improve L2 locality when sweeping M and reusing B tiles
    pid = tl.program_id(0)
    num_pid_m = tl.cdiv(M, BLOCK_M)
    num_pid_n_total = tl.cdiv(N, BLOCK_N)
    SPLIT_N_TOTAL = 2 * SPLIT_PAIRS  # each pair handles 2 adjacent N-tiles
    num_pid_n_assigned = tl.cdiv(num_pid_n_total, SPLIT_N_TOTAL)

    num_pid_in_group = GROUP_M * num_pid_n_assigned
    group_id = pid // num_pid_in_group
    first_pid_m = group_id * GROUP_M
    group_size_m = tl.minimum(num_pid_m - first_pid_m, GROUP_M)
    pid_m = first_pid_m + (pid % group_size_m)
    pid_n_assigned = (pid % num_pid_in_group) // group_size_m
    base_pid_n = pid_n_assigned * SPLIT_N_TOTAL  # base N-tile index for this program

    # Tile ranges
    offs_m = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    offs_k = tl.arange(0, BLOCK_K)  # K==BLOCK_K==32

    # Alignment hints for better vectorization
    tl.multiple_of(offs_m, BLOCK_M)
    tl.multiple_of(offs_k, BLOCK_K)

    # Base pointer for A tile (single K-slice -> no loop)
    a_ptrs = A_ptr + (offs_m[:, None].to(tl.int64) * stride_am + offs_k[None, :].to(tl.int64) * stride_ak)
    A_tile = tl.load(a_ptrs)  # (BLOCK_M, BLOCK_K)

    # Process SPLIT_PAIRS pairs; each pair computes two adjacent N-tiles concurrently
    for pair in range(SPLIT_PAIRS):
        tile_n0 = (base_pid_n + (2 * pair)) * BLOCK_N
        tile_n1 = tile_n0 + BLOCK_N

        offs_n0 = tile_n0 + tl.arange(0, BLOCK_N)
        offs_n1 = tile_n1 + tl.arange(0, BLOCK_N)

        tl.multiple_of(offs_n0, BLOCK_N)
        tl.multiple_of(offs_n1, BLOCK_N)

        # B pointers for both N-tiles
        b0_ptrs = B_ptr + (offs_k[:, None].to(tl.int64) * stride_bk + offs_n0[None, :].to(tl.int64) * stride_bn)
        b1_ptrs = B_ptr + (offs_k[:, None].to(tl.int64) * stride_bk + offs_n1[None, :].to(tl.int64) * stride_bn)

        # Load tiles (no masks: dimensions are multiples of block sizes)
        B0_tile = tl.load(b0_ptrs)
        B1_tile = tl.load(b1_ptrs)

        # Accumulate results in fp32
        acc0 = tl.dot(A_tile, B0_tile)
        acc1 = tl.dot(A_tile, B1_tile)

        # Store back
        c0_ptrs = C_ptr + (offs_m[:, None].to(tl.int64) * stride_cm + offs_n0[None, :].to(tl.int64) * stride_cn)
        c1_ptrs = C_ptr + (offs_m[:, None].to(tl.int64) * stride_cm + offs_n1[None, :].to(tl.int64) * stride_cn)
        tl.store(c0_ptrs, acc0)
        tl.store(c1_ptrs, acc1)

# ------------------------------------------------------------------ ② case 层
# 典型用法:makora 行的 Triton 解,ref 为其 torch 参考实现的 numpy 移植;
# 输入按原 get_inputs 的构造种类复现(randn/zeros/randint...),权重两模型共用。
SHAPES = ((128,), (256,))
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
    A = rng.standard_normal((b, 32,)).astype(np.float32)
    B = rng.standard_normal((32, 512,)).astype(np.float32)

    C = np.zeros((A.shape[0], B.shape[1],), dtype=np.float32)

    args = {'A_ptr': A, 'B_ptr': B, 'C_ptr': C, 'M': A.shape[0], 'N': B.shape[1], 'K': A.shape[1], 'stride_am': int(A.strides[0] // A.itemsize), 'stride_ak': int(A.strides[1] // A.itemsize), 'stride_bk': int(B.strides[0] // B.itemsize), 'stride_bn': int(B.strides[1] // B.itemsize), 'stride_cm': int(C.strides[0] // C.itemsize), 'stride_cn': int(C.strides[1] // C.itemsize)}
    meta = {'BLOCK_M': 128, 'BLOCK_N': 64, 'BLOCK_K': 32, 'GROUP_M': 8, 'SPLIT_PAIRS': 2}
    r = ref({'A': A, 'B': B}, meta)
    expected = {'C_ptr': r["_o0"].astype(C.dtype)}
    case = {"args": args, "meta": meta, "grid": ((triton.cdiv(A.shape[0], 128) * triton.cdiv(triton.cdiv(B.shape[1], 64), (2 * 2))),),
            "outputs": ('C_ptr',), "expected": expected}
    tol = 1e-2
    # fp32 dot 是 IEEE;低精度输入按 fp32 累加,按 expected 幅值自适应 atol
    case["comparison"] = {n: {"comparator": "allclose", "exact": False,
                              "rtol": tol,
                              "atol": max(4e-2, 2e-3 * float(np.abs(expected[n]).max())),
                              "equal_nan": True}
                              for n in case["outputs"]}
    case["launch_meta"] = {'num_stages': 2, 'num_warps': 8}

    return case


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, matmul_k32_splitn4_paired_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed)


def ref(args, meta):
    A = np.asarray(args['A'], dtype=np.float64)
    B = np.asarray(args['B'], dtype=np.float64)
    return {"_o0": np.matmul(A, B)}


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
