"""matmul: matmul(compute 类)。
bench 稳态配置见 bench/workload.json(声明 shape [16, 16, 16],验证 shape [256, 256, 256]);正确性 shape 见下方 SHAPES。
模式: creation.arange、creation.zeros、memory.store.masked、memory.load.masked、linalg.dot、。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/matmul', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'creation.zeros', 'memory.store.masked', 'memory.load.masked', 'linalg.dot', 'control.for_range', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/matmul.py', 'sha256': 'c3b16af04e3c2cc74fa734ad7ffa07c7bd927413f14ad6f978627b87cac2a874'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def matmul_kernel(a_ptr, b_ptr, y_ptr, M, N, K):

    pid_m = tl.program_id(0)
    pid_n = tl.program_id(1)
    offs_m = pid_m * 16 + tl.arange(0, 16)
    offs_n = pid_n * 16 + tl.arange(0, 16)
    offs_k = tl.arange(0, 32)
    acc = tl.zeros((16, 16), tl.float32)
    for k0 in range(0, K, 32):
        kk = k0 + offs_k
        a = tl.load(a_ptr + offs_m[:, None] * K + kk[None, :],
                    mask=(offs_m[:, None] < M) & (kk[None, :] < K), other=0.0)
        b = tl.load(b_ptr + kk[:, None] * N + offs_n[None, :],
                    mask=(kk[:, None] < K) & (offs_n[None, :] < N), other=0.0)
        acc = tl.dot(a, b, acc)
    tl.store(y_ptr + offs_m[:, None] * N + offs_n[None, :], acc,
             mask=(offs_m[:, None] < M) & (offs_n[None, :] < N))


# ------------------------------------------------------------------ ② case 层

DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((16, 16, 16), (8, 32, 24))

def ref(args, meta):
    del meta
    a = np.asarray(args["a_ptr"], dtype=np.float64)
    b = np.asarray(args["b_ptr"], dtype=np.float64)
    return {"y_ptr": (a @ b).astype(np.float32)}

def make_case(shape=None, *, dtype="float32", seed=20261008):
    if dtype is None:
        dtype = "float32"
    if np.dtype(dtype).name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype!r}; choose from {DTYPES}")
    from case_utils import fast_rng
    rng = fast_rng(seed)
    actual = SHAPES[0] if shape is None else shape
    m, n, k = actual
    a = rng.standard_normal((m, k)) * 0.5
    b = rng.standard_normal((k, n)) * 0.5
    args = {'a_ptr': a.astype(np.float32), 'b_ptr': b.astype(np.float32), 'y_ptr': np.zeros((m, n), dtype=np.float32), 'M': m, 'N': n, 'K': k}
    expected = ref(args, {})
    tolerance = {"comparator": "allclose", "exact": False, "rtol": 2e-3, "atol": 2e-3,
                   "equal_nan": True}
    comparison = {name: ({"comparator": "array_equal", "exact": True}
                    if np.asarray(value).dtype == np.bool_ else dict(tolerance))
                  for name, value in expected.items()}
    return {
        "args": args,
        "meta": {},
        "grid": ((m + 15) // 16, (n + 15) // 16),
        "outputs": tuple(expected),
        "expected": expected,
        "comparison": comparison,
        "shape": actual,
        "dtype": "float32",
        "kernel": matmul_kernel,
    }


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
