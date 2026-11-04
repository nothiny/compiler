"""mk__matmul_at_kernel_optimized_8461cac3: makora train 第 26803 行的 Triton 解:_matmul_at_kernel_optimized;ref 为 torch 参考实现的 numpy 移植。

模式: memory.load.masked、linalg.dot、args.program_id、creation.arange。

文件只有两层:
  ① _matmul_at_kernel_optimized   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
                     怎么分配、搬运、启动由 runner 的 Device 决定。
"""

OPERATOR = {"name": "hidden/matmul_at_kernel_optimized_8461cac3", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ['memory.load.masked', 'linalg.dot', 'args.program_id', 'creation.arange']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 26803,
          "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d",
          "original_sha256": "8461cac378b3f9a434c650589b3dccaf083066b722abb3026ffa3260d5d37b8e"}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def _matmul_at_kernel_optimized(
    A_ptr,  # pointer to A (shape K x M in memory)
    B_ptr,  # pointer to B (shape K x N in memory)
    C_ptr,  # pointer to output C (shape M x N in memory)
    M, N, K,
    stride_Ak, stride_Am,
    stride_Bk, stride_Bn,
    stride_Cm, stride_Cn,
    BLOCK_M: tl.constexpr,
    BLOCK_N: tl.constexpr,
    BLOCK_K: tl.constexpr,
    NUM_WARPS: tl.constexpr,
    NUM_STAGES: tl.constexpr,
):
    # 2D grid: program_id(0) -> block row (over M), program_id(1) -> block col (over N)
    row_block = tl.program_id(0)
    col_block = tl.program_id(1)

    row_start = row_block * BLOCK_M
    col_start = col_block * BLOCK_N

    # row/col indices for this program
    rm = row_start + tl.arange(0, BLOCK_M)   # shape (BLOCK_M,)
    cn = col_start + tl.arange(0, BLOCK_N)   # shape (BLOCK_N,)

    # accumulator for the block (BLOCK_M x BLOCK_N), keep in float32
    acc = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)

    # Precompute a reusable small range for K-block offsets
    k_base = tl.arange(0, BLOCK_K)

    # Load first K block (k in [0, BLOCK_K))
    k = 0
    a_ptrs = A_ptr + rm[:, None] * stride_Am + k_base[None, :] * stride_Ak
    mask_a = (rm[:, None] < M) & (k_base[None, :] < K)
    a = tl.load(a_ptrs, mask=mask_a, other=0.0)            # shape (BLOCK_M, BLOCK_K)

    b_ptrs = B_ptr + k_base[:, None] * stride_Bk + cn[None, :] * stride_Bn
    mask_b = (k_base[:, None] < K) & (cn[None, :] < N)
    b = tl.load(b_ptrs, mask=mask_b, other=0.0)            # shape (BLOCK_K, BLOCK_N)

    k += BLOCK_K

    # Main loop with prefetch (double-buffer): load next block while computing on current
    while k < K:
        k_off = k_base + k

        a_next_ptrs = A_ptr + rm[:, None] * stride_Am + k_off[None, :] * stride_Ak
        mask_a_next = (rm[:, None] < M) & (k_off[None, :] < K)
        a_next = tl.load(a_next_ptrs, mask=mask_a_next, other=0.0)

        b_next_ptrs = B_ptr + k_off[:, None] * stride_Bk + cn[None, :] * stride_Bn
        mask_b_next = (k_off[:, None] < K) & (cn[None, :] < N)
        b_next = tl.load(b_next_ptrs, mask=mask_b_next, other=0.0)

        # compute on the current set while the next is already being fetched
        acc += tl.dot(a, b)

        # advance windows
        a = a_next
        b = b_next
        k += BLOCK_K

    # final block
    acc += tl.dot(a, b)

    # Write back the accumulator to C
    c_ptrs = C_ptr + rm[:, None] * stride_Cm + cn[None, :] * stride_Cn
    mask_c = (rm[:, None] < M) & (cn[None, :] < N)
    tl.store(c_ptrs, acc, mask=mask_c)

# ------------------------------------------------------------------ ② case 层
# 典型用法:makora 行的 Triton 解,ref 为其 torch 参考实现的 numpy 移植;
# 输入按原 get_inputs 的构造种类复现(randn/zeros/randint...),权重两模型共用。
SHAPES = ((64,), (128,))
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

    args = {'A_ptr': A, 'B_ptr': B, 'C_ptr': C, 'M': A.shape[1], 'N': B.shape[1], 'K': A.shape[0], 'stride_Ak': int(A.strides[0] // A.itemsize), 'stride_Am': int(A.strides[1] // A.itemsize), 'stride_Bk': int(B.strides[0] // B.itemsize), 'stride_Bn': int(B.strides[1] // B.itemsize), 'stride_Cm': int(C.strides[0] // C.itemsize), 'stride_Cn': int(C.strides[1] // C.itemsize)}
    meta = {'BLOCK_M': 64, 'BLOCK_N': 64, 'BLOCK_K': 32, 'NUM_WARPS': 8, 'NUM_STAGES': 2}
    r = ref({'A': A, 'B': B}, meta)
    expected = {'C_ptr': r["_o0"].astype(C.dtype)}
    case = {"args": args, "meta": meta, "grid": ((((A.shape[1] + 64) - 1) // 64), (((B.shape[1] + 64) - 1) // 64),),
            "outputs": ('C_ptr',), "expected": expected}
    tol = 1e-2
    # fp32 dot 是 IEEE;低精度输入按 fp32 累加,按 expected 幅值自适应 atol
    case["comparison"] = {n: {"comparator": "allclose", "exact": False,
                              "rtol": tol,
                              "atol": max(4e-2, 2e-3 * float(np.abs(expected[n]).max())),
                              "equal_nan": True}
                              for n in case["outputs"]}

    return case


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, _matmul_at_kernel_optimized, DTYPES,
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
