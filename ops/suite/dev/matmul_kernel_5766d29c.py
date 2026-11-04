"""mk__matmul_kernel_5766d29c: makora train 第 11827 行的 Triton 解:_matmul_kernel;ref 为 torch 参考实现的 numpy 移植。

模式: memory.load.masked、args.program_id、creation.arange。

文件只有两层:
  ① _matmul_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
                     怎么分配、搬运、启动由 runner 的 Device 决定。
"""

OPERATOR = {"name": "hidden/matmul_kernel_5766d29c", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ['memory.load.masked', 'args.program_id', 'creation.arange']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 11827,
          "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d",
          "original_sha256": "5766d29c6425c27ab5c09d8b740a00388651eca4c6b17d504bdd6a96b5a42de6"}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def _matmul_kernel(
    a_ptr,  # pointer to A (M, K)
    b_ptr,  # pointer to B (K, N)
    c_ptr,  # pointer to C (M, N)
    M, N, K,
    stride_am, stride_ak,  # A strides: (stride_row, stride_col)
    stride_bk, stride_bn,  # B strides: (stride_row, stride_col)
    stride_cm, stride_cn,  # C strides: (stride_row, stride_col)
    BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr,
):
    # tile indices
    pid_m = tl.program_id(0)
    pid_n = tl.program_id(1)

    m_start = pid_m * BLOCK_M
    n_start = pid_n * BLOCK_N

    rm = m_start + tl.arange(0, BLOCK_M)
    rn = n_start + tl.arange(0, BLOCK_N)

    # accumulator
    acc = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)

    # loop over K in small blocks; BLOCK_K is constexpr so inner loop unrolls
    for k_start in range(0, K, BLOCK_K):
        # iterate over each k in the K-block and load a column/row directly
        for kk in range(0, BLOCK_K):
            k = k_start + kk
            # masks for valid loads
            a_mask = (rm < M) & (k < K)
            b_mask = (rn < N) & (k < K)

            # compute offsets for loads
            a_off = rm * stride_am + k * stride_ak
            b_off = k * stride_bk + rn * stride_bn

            # load a column of A and a row of B
            a_col = tl.load(a_ptr + a_off, mask=a_mask, other=0.0)  # [BLOCK_M]
            b_row = tl.load(b_ptr + b_off, mask=b_mask, other=0.0)  # [BLOCK_N]

            # outer product and accumulate
            acc += a_col[:, None] * b_row[None, :]

    # write back
    c_mask = (rm[:, None] < M) & (rn[None, :] < N)
    c_off = rm[:, None] * stride_cm + rn[None, :] * stride_cn
    tl.store(c_ptr + c_off, acc, mask=c_mask)

# ------------------------------------------------------------------ ② case 层
# 典型用法:makora 行的 Triton 解,ref 为其 torch 参考实现的 numpy 移植;
# 输入按原 get_inputs 的构造种类复现(randn/zeros/randint...),权重两模型共用。
SHAPES = ((128,), (127,))
DTYPES = ('float32', 'float16')
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
    A = rng.standard_normal((b, 64,)).astype(np.float32)
    B = rng.standard_normal((64, 512,)).astype(np.float32)

    C = np.zeros((A.shape[0], B.shape[1],), dtype=np.float32)

    args = {'a_ptr': A, 'b_ptr': B, 'c_ptr': C, 'M': A.shape[0], 'N': B.shape[1], 'K': A.shape[1], 'stride_am': int(A.strides[0] // A.itemsize), 'stride_ak': int(A.strides[1] // A.itemsize), 'stride_bk': int(B.strides[0] // B.itemsize), 'stride_bn': int(B.strides[1] // B.itemsize), 'stride_cm': int(C.strides[0] // C.itemsize), 'stride_cn': int(C.strides[1] // C.itemsize)}
    meta = {'BLOCK_M': 128, 'BLOCK_N': 128, 'BLOCK_K': 32}
    r = ref({'A': A, 'B': B}, meta)
    expected = {'c_ptr': r["_o0"].astype(C.dtype)}
    case = {"args": args, "meta": meta, "grid": ((((A.shape[0] + (128)) - 1) // (128)), (((B.shape[1] + (128)) - 1) // (128)),),
            "outputs": ('c_ptr',), "expected": expected}
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

    return public_make_case(_make_case, _matmul_kernel, DTYPES,
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
