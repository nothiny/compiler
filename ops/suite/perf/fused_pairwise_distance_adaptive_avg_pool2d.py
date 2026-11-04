"""fused_pairwise_distance_adaptive_avg_pool2d: TritonBench 算子( 类)。
模式: memory.store、math.sqrt、memory.load、control.for_range、args.runtime_scalar。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/fused_pairwise_distance_adaptive_avg_pool2d', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['memory.store', 'math.sqrt', 'memory.load', 'control.for_range', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/fused_pairwise_distance_adaptive_avg_pool2d.py', 'sha256': '0f9d84bff4805f6c6955f9b22383b90c82ce50ad6f021dfd8c666f9ac92cb83b'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def fused_pairwise_distance_adaptive_avg_pool2d_kernel(x1_ptr, x2_ptr, y_ptr,
                                                       C, HW, eps):
    n_idx = tl.program_id(0)
    acc = 0.0
    for c in range(0, C):
        m1 = 0.0
        m2 = 0.0
        for q in range(0, HW):
            m1 = m1 + tl.load(x1_ptr + n_idx * C * HW + c * HW + q)
            m2 = m2 + tl.load(x2_ptr + n_idx * C * HW + c * HW + q)
        d = m1 / HW - m2 / HW
        acc = acc + d * d
    tl.store(y_ptr + n_idx, tl.sqrt(acc) + eps)


# ------------------------------------------------------------------ ② case 层

import math

DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((4, 8), (5, 9))

def ref(args, meta):
    del meta
    x1 = np.asarray(args["x1_ptr"], dtype=np.float64).reshape(args["x1_ptr"].shape[0], -1)
    x2 = np.asarray(args["x2_ptr"], dtype=np.float64).reshape(args["x2_ptr"].shape[0], -1)
    n, c_hw = x1.shape
    c = int(args["C"])
    m1 = x1.reshape(n, c, c_hw // c).mean(-1)
    m2 = x2.reshape(n, c, c_hw // c).mean(-1)
    d = np.sqrt(((m1 - m2) ** 2).sum(-1)) + 1e-6
    return {"y_ptr": d.astype(np.float32)}

def make_case(shape=None, *, dtype="float32", seed=20261008):
    if dtype is None:
        dtype = "float32"
    if np.dtype(dtype).name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype!r}; choose from {DTYPES}")
    from case_utils import fast_rng
    rng = fast_rng(seed)
    actual = SHAPES[0] if shape is None else shape
    n, side = actual
    c = 2
    x1 = rng.standard_normal((n, c, side, side)) * 0.5
    x2 = rng.standard_normal((n, c, side, side)) * 0.5
    args = {'x1_ptr': x1.astype(np.float32), 'x2_ptr': x2.astype(np.float32), 'y_ptr': np.zeros(n, dtype=np.float32), 'C': c, 'HW': side * side, 'eps': 1e-6}
    expected = ref(args, {})
    tolerance = {"comparator": "allclose", "exact": False, "rtol": 2e-3, "atol": 2e-3,
                   "equal_nan": True}
    comparison = {name: dict(tolerance) for name in expected}
    return {
        "args": args,
        "meta": {},
        "grid": (n,),
        "outputs": tuple(expected),
        "expected": expected,
        "comparison": comparison,
        "shape": actual,
        "dtype": "float32",
        "kernel": fused_pairwise_distance_adaptive_avg_pool2d_kernel,
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
