"""batched_vecmat_mult: matmul(compute 类)。
bench 稳态配置见 bench/workload.json(声明 shape [32, 32, 32],验证 shape [256, 256, 256]);正确性 shape 见下方 SHAPES。
模式: creation.zeros、memory.store.masked、creation.arange、math.cdiv、memory.load.masked、linalg.dot。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""

OPERATOR = {'name': 'bench/batched_vecmat_mult', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.zeros', 'memory.store.masked', 'creation.arange', 'math.cdiv', 'memory.load.masked', 'linalg.dot', 'shape.trans', 'control.for_range']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/batched_vecmat_mult.py', 'sha256': 'c534f63db1bce7cac3f06fd487c6ce916b6f968a593e6b3f6dd7200896c213e0'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def batched_vecmat_kernel(A, B, out, M, N, K,
                          BM: tl.constexpr, BN: tl.constexpr, BK: tl.constexpr):
    pid_m = tl.program_id(0)
    pid_n = tl.program_id(1)
    offs_m = pid_m * BM + tl.arange(0, BM)
    offs_n = pid_n * BN + tl.arange(0, BN)
    acc = tl.zeros((BM, BN), dtype=tl.float32)
    for k in range(0, tl.cdiv(K, BK)):
        kk = k * BK + tl.arange(0, BK)
        a = tl.load(A + kk[:, None] * M + offs_m[None, :],
                    mask=(kk[:, None] < K) & (offs_m[None, :] < M), other=0.0)
        b = tl.load(B + kk[:, None] * N + offs_n[None, :],
                    mask=(kk[:, None] < K) & (offs_n[None, :] < N), other=0.0)
        acc += tl.dot(tl.trans(a), b)
    tl.store(out + offs_m[:, None] * N + offs_n[None, :], acc,
             mask=(offs_m[:, None] < M) & (offs_n[None, :] < N))


# ------------------------------------------------------------------ ② case 层
DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((32, 32, 32), (33, 33, 33))

def ref(args, meta):
    a = np.asarray(args["A"], dtype=np.float64)
    b = np.asarray(args["B"], dtype=np.float64)
    return {"out": (a.T @ b).astype(np.asarray(args["out"]).dtype)}

def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    m, n, k = (int(v) for v in shape)
    from case_utils import fast_rng
    rng = fast_rng(seed)
    args = {"A": rng.standard_normal((k, m)).astype(dtype),
            "B": rng.standard_normal((k, n)).astype(dtype),
            "out": np.zeros((m, n), dtype=dtype), "M": np.int32(m), "N": np.int32(n), "K": np.int32(k)}
    meta = {"BM": 32, "BN": 32, "BK": 32}
    grid = (triton.cdiv(m, 32), triton.cdiv(n, 32))
    expected = ref(args, meta)
    tol = {"comparator": "allclose", "exact": False, "rtol": 1e-2, "atol": 1e-1, "equal_nan": True}
    return {"args": args, "meta": meta, "grid": grid,
            "outputs": ("out",), "expected": expected,
            "comparison": {name: dict(tol) for name in expected}}

def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, batched_vecmat_kernel, DTYPES,
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
