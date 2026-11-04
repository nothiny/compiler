"""triton_linear_activation: matmul(compute 类)。
bench 稳态配置见 bench/workload.json(声明 shape [32, 32, 32],验证 shape [256, 256, 256]);正确性 shape 见下方 SHAPES。
模式: creation.arange、creation.zeros、memory.load.masked、memory.store.masked、math.cdiv、linalg.dot。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""

OPERATOR = {'name': 'bench/triton_linear_activation', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'creation.zeros', 'memory.load.masked', 'memory.store.masked', 'math.cdiv', 'linalg.dot', 'math.erf', 'control.for_range']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/triton_linear_activation.py', 'sha256': '47939ad03e116a0724e8daff9f5be7d3c7c7b251a01628a85eb40fa5d21c1357'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.autotune(
    configs=[
        triton.Config({'BLOCK_M': 16, 'BLOCK_N': 16, 'BLOCK_K': 32}, num_warps=4),
        triton.Config({'BLOCK_M': 32, 'BLOCK_N': 32, 'BLOCK_K': 32}, num_warps=4),
        triton.Config({'BLOCK_M': 32, 'BLOCK_N': 64, 'BLOCK_K': 32}, num_warps=4),
    ],
    key=["M","N","K"],
)
@triton.jit
def linear_act_kernel(x_ptr, w_ptr, b_ptr, y_ptr, M, N, K,
                      stride_xm, stride_xk, stride_wk, stride_wn, stride_ym, stride_yn,
                      BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr):
    pid_m = tl.program_id(0)
    pid_n = tl.program_id(1)
    offs_m = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    offs_k = tl.arange(0, BLOCK_K)
    acc = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)
    for k in range(0, tl.cdiv(K, BLOCK_K)):
        kk = k * BLOCK_K + offs_k
        a = tl.load(x_ptr + offs_m[:, None] * stride_xm + kk[None, :] * stride_xk,
                    mask=(offs_m[:, None] < M) & (kk[None, :] < K), other=0.0)
        w = tl.load(w_ptr + kk[:, None] * stride_wk + offs_n[None, :] * stride_wn,
                    mask=(kk[:, None] < K) & (offs_n[None, :] < N), other=0.0)
        acc += tl.dot(a, w)
    b = tl.load(b_ptr + offs_n, mask=offs_n < N, other=0.0)
    acc = acc + b[None, :]
    acc = 0.5 * acc * (1.0 + tl.erf(acc * 0.7071067811865476))
    tl.store(y_ptr + offs_m[:, None] * stride_ym + offs_n[None, :] * stride_yn, acc,
             mask=(offs_m[:, None] < M) & (offs_n[None, :] < N))


# ------------------------------------------------------------------ ② case 层
DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((32, 32, 32), (42, 32, 32))

def ref(args, meta):
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    w = np.asarray(args["w_ptr"], dtype=np.float64)
    b = np.asarray(args["b_ptr"], dtype=np.float64)
    acc = x @ w + b[None, :]
    from mathref import erf
    y = 0.5 * acc * (1.0 + erf(acc * 0.7071067811865476))
    return {"y_ptr": y.astype(np.asarray(args["y_ptr"]).dtype)}

def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    m, n, k = (int(v) for v in shape)
    from case_utils import fast_rng
    rng = fast_rng(seed)
    args = {"x_ptr": rng.standard_normal((m, k)).astype(dtype),
            "w_ptr": rng.standard_normal((k, n)).astype(dtype),
            "b_ptr": rng.standard_normal(n).astype(dtype),
            "y_ptr": np.zeros((m, n), dtype=dtype),
            "M": np.int32(m), "N": np.int32(n), "K": np.int32(k),
            "stride_xm": np.int32(k), "stride_xk": np.int32(1),
            "stride_wk": np.int32(n), "stride_wn": np.int32(1),
            "stride_ym": np.int32(n), "stride_yn": np.int32(1)}
    meta = {}
    grid = (triton.cdiv(m, 32), triton.cdiv(n, 32))
    expected = ref(args, meta)
    tol = {"comparator": "allclose", "exact": False, "rtol": 1e-2, "atol": 1e-1, "equal_nan": True}
    return {"args": args, "meta": meta, "grid": lambda meta: (triton.cdiv(m, meta["BLOCK_M"]), triton.cdiv(n, meta["BLOCK_N"])),
            "outputs": ("y_ptr",), "expected": expected,
            "comparison": {name: dict(tol) for name in expected}}

def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, linear_act_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)

ORACLE_KIND = "numpy_reference"

INDEPENDENT_ORACLE = True

EXECUTION_KIND = "triton_kernel"

VERIFICATION_KIND = "correctness"

OPERATOR_NAME = "G/" + __file__.rsplit("/", 1)[-1]

OPERATOR_FILE = __file__


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
