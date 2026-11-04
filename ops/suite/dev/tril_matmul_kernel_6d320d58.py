"""mk__tril_matmul_kernel_6d320d58: makora train 第 25567 行的 Triton 解:_tril_matmul_kernel;ref 为 torch 参考实现的 numpy 移植。

模式: memory.load.masked、control.where、linalg.dot、args.program_id、creation.arange。

文件只有两层:
  ① _tril_matmul_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
                     怎么分配、搬运、启动由 runner 的 Device 决定。
"""

OPERATOR = {"name": "hidden/tril_matmul_kernel_6d320d58", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ['memory.load.masked', 'control.where', 'linalg.dot', 'args.program_id', 'creation.arange']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 25567,
          "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d",
          "original_sha256": "6d320d5857acef965cc5c62d9a48518a62340ff6b32f8aa6e563b84b1f2d8ddd"}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def _tril_matmul_kernel(
    A_ptr,  # *fp32
    B_ptr,  # *fp32
    C_ptr,  # *fp32
    N,      # int32, matrix dimension (N x N)
    stride_Am,
    stride_Ak,
    stride_Bk,
    stride_Bn,
    stride_Cm,
    stride_Cn,
    BLOCK_M: tl.constexpr,
    BLOCK_N: tl.constexpr,
    BLOCK_K: tl.constexpr,
):
    """Compute C = tril(A @ B) for square matrices A, B, C of size N x N.

    The kernel tiles the output matrix and avoids any computation for tiles that
    are fully above the main diagonal (i < j). Tiles strictly below the
    diagonal are computed as a dense matmul. Tiles intersecting the diagonal
    are computed as dense tiles and then masked with a lower-triangular mask.
    """

    pid_m = tl.program_id(0)
    pid_n = tl.program_id(1)

    # Tile start indices
    tile_m_start = pid_m * BLOCK_M
    tile_n_start = pid_n * BLOCK_N
    tile_m_end = tile_m_start + BLOCK_M - 1
    tile_n_end = tile_n_start + BLOCK_N - 1

    N_i32 = N

    # Offsets within the tile
    offs_m = tile_m_start + tl.arange(0, BLOCK_M)
    offs_n = tile_n_start + tl.arange(0, BLOCK_N)

    # Masks for in-bounds rows/cols
    mask_m = offs_m < N_i32
    mask_n = offs_n < N_i32

    # Determine if this tile is fully above or fully below the diagonal
    # using only the region that lies inside [0, N).
    N_minus_1 = N_i32 - 1
    max_valid_i = tl.minimum(tile_m_end, N_minus_1)
    max_valid_j = tl.minimum(tile_n_end, N_minus_1)

    # Tile has some valid elements iff tile_m_start < N and tile_n_start < N
    has_valid = (tile_m_start < N_i32) & (tile_n_start < N_i32)

    # Fully above diagonal: max_i < min_j (min_j = tile_n_start)
    is_above = has_valid & (max_valid_i < tile_n_start)

    # Fully below diagonal: min_i >= max_j (min_i = tile_m_start)
    is_below = has_valid & (tile_m_start >= max_valid_j)

    # Accumulator for this tile (float32)
    acc = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)

    # If the tile is not fully above the diagonal, compute its (dense) matmul
    if not is_above:
        for k0 in range(0, N_i32, BLOCK_K):
            offs_k = k0 + tl.arange(0, BLOCK_K)
            k_mask = offs_k < N_i32

            # Pointers for A and B tiles
            a_ptrs = A_ptr + (offs_m[:, None] * stride_Am + offs_k[None, :] * stride_Ak)
            b_ptrs = B_ptr + (offs_k[:, None] * stride_Bk + offs_n[None, :] * stride_Bn)

            a = tl.load(a_ptrs, mask=mask_m[:, None] & k_mask[None, :], other=0.0)
            b = tl.load(b_ptrs, mask=k_mask[:, None] & mask_n[None, :], other=0.0)

            acc += tl.dot(a, b)

        # Apply lower-triangular masking for tiles that intersect the diagonal
        if is_below:
            c_tile = acc
        else:
            # Diagonal-intersecting tile: zero out i < j
            i_idx = offs_m[:, None]
            j_idx = offs_n[None, :]
            tri_mask = i_idx >= j_idx
            c_tile = tl.where(tri_mask, acc, 0.0)
    else:
        # Fully above diagonal: output is all zeros
        c_tile = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)

    # Store the result
    c_ptrs = C_ptr + (offs_m[:, None] * stride_Cm + offs_n[None, :] * stride_Cn)
    mask_c = mask_m[:, None] & mask_n[None, :]
    tl.store(c_ptrs, c_tile, mask=mask_c)

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
    A = rng.standard_normal((b, b,)).astype(np.float32)
    B = rng.standard_normal((b, b,)).astype(np.float32)

    C = np.zeros_like(A)

    args = {'A_ptr': A, 'B_ptr': B, 'C_ptr': C, 'N': A.shape[0], 'stride_Am': int(A.strides[0] // A.itemsize), 'stride_Ak': int(A.strides[1] // A.itemsize), 'stride_Bk': int(B.strides[0] // B.itemsize), 'stride_Bn': int(B.strides[1] // B.itemsize), 'stride_Cm': int(C.strides[0] // C.itemsize), 'stride_Cn': int(C.strides[1] // C.itemsize)}
    meta = {'BLOCK_M': 128, 'BLOCK_N': 128, 'BLOCK_K': 32}
    r = ref({'A': A, 'B': B}, meta)
    expected = {'C_ptr': r["_o0"].astype(C.dtype)}
    case = {"args": args, "meta": meta, "grid": (triton.cdiv(A.shape[0], (128)), triton.cdiv(A.shape[0], (128)),),
            "outputs": ('C_ptr',), "expected": expected}
    tol = 1e-2
    # fp32 dot 是 IEEE;低精度输入按 fp32 累加,按 expected 幅值自适应 atol
    case["comparison"] = {n: {"comparator": "allclose", "exact": False,
                              "rtol": tol,
                              "atol": max(4e-2, 2e-3 * float(np.abs(expected[n]).max())),
                              "equal_nan": True}
                              for n in case["outputs"]}
    case["launch_meta"] = {'num_stages': 3, 'num_warps': 4}

    return case


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, _tril_matmul_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed)


def ref(args, meta):
    A = np.asarray(args['A'], dtype=np.float64)
    B = np.asarray(args['B'], dtype=np.float64)
    return {"_o0": np.tril(np.matmul(A, B))}


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
