"""matrix_multiply_and_row_dot: TritonBench 算子( 类)。
模式: creation.arange、creation.zeros、memory.store、memory.load.masked、reduce.sum、control.for_range。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/matrix_multiply_and_row_dot', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'creation.zeros', 'memory.store', 'memory.load.masked', 'reduce.sum', 'control.for_range', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/matrix_multiply_and_row_dot.py', 'sha256': 'd92fc7548a21631954b6daf494a502ea73470c5a8f7a4fa02e2da5fc6bd92ee4'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def matrix_multiply_and_row_dot_kernel(a_ptr, b_ptr, cin_ptr, out_ptr, N, K, alpha, beta):
    offs_n = tl.arange(0, 64)
    nmask = offs_n < N
    acc0 = tl.zeros((64,), tl.float32)
    acc1 = tl.zeros((64,), tl.float32)
    for k0 in range(0, K, 32):
        offs_k = k0 + tl.arange(0, 32)
        kmask = offs_k < K
        a0 = tl.load(a_ptr + 0 * K + offs_k, mask=kmask, other=0.0)
        a1 = tl.load(a_ptr + 1 * K + offs_k, mask=kmask, other=0.0)
        b = tl.load(b_ptr + offs_k[:, None] * N + offs_n[None, :],
                    mask=kmask[:, None] & nmask[None, :], other=0.0)
        acc0 = acc0 + tl.sum(b * a0[:, None], axis=0)
        acc1 = acc1 + tl.sum(b * a1[:, None], axis=0)
    c0 = alpha * acc0 + beta * tl.load(cin_ptr + 0 * N + offs_n, mask=nmask, other=0.0)
    c1 = alpha * acc1 + beta * tl.load(cin_ptr + 1 * N + offs_n, mask=nmask, other=0.0)
    tl.store(out_ptr, tl.sum(c0 * c1, axis=0))


# ------------------------------------------------------------------ ② case 层

DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((16, 24, 32), (17, 25, 33))

def ref(args, meta):
    del meta
    a = np.asarray(args["a_ptr"], dtype=np.float64)
    b = np.asarray(args["b_ptr"], dtype=np.float64)
    c = np.asarray(args["cin_ptr"], dtype=np.float64)
    alpha, beta = float(args["alpha"]), float(args["beta"])
    cc = alpha * (a @ b) + beta * c
    return {"out_ptr": np.array([float(cc[0] @ cc[1])], dtype=np.float32)}

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
    c = rng.standard_normal((m, n))
    args = {'a_ptr': a.astype(np.float32), 'b_ptr': b.astype(np.float32), 'cin_ptr': c.astype(np.float32), 'out_ptr': np.zeros(1, dtype=np.float32), 'N': n, 'K': k, 'alpha': 1.25, 'beta': 0.75}
    expected = ref(args, {})
    tolerance = {"comparator": "allclose", "exact": False, "rtol": 2e-3, "atol": 2e-3,
                   "equal_nan": True}
    comparison = {name: ({"comparator": "array_equal", "exact": True}
                    if np.asarray(value).dtype == np.bool_ else dict(tolerance))
                  for name, value in expected.items()}
    return {
        "args": args,
        "meta": {},
        "grid": (1,),
        "outputs": tuple(expected),
        "expected": expected,
        "comparison": comparison,
        "shape": actual,
        "dtype": "float32",
        "kernel": matrix_multiply_and_row_dot_kernel,
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
