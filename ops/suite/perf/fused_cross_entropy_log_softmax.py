"""fused_cross_entropy_log_softmax: TritonBench 算子( 类)。
模式: creation.arange、memory.store、memory.load.masked、reduce.max、creation.where、memory.load。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/fused_cross_entropy_log_softmax', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'memory.store', 'memory.load.masked', 'reduce.max', 'creation.where', 'memory.load', 'math.exp', 'math.log']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/fused_cross_entropy_log_softmax.py', 'sha256': '27639bd0681b0cffa847f5e1fdb54e8046282836dd73c468eb02e58730386770'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def fused_cross_entropy_log_softmax_kernel(x_ptr, t_ptr, y_ptr, n_rows, n_cols,
                                           BLOCK: tl.constexpr):
    cols = tl.arange(0, BLOCK)
    cmask = cols < n_cols
    acc = 0.0
    for r in range(0, n_rows):
        x = tl.load(x_ptr + r * n_cols + cols, mask=cmask, other=float('-inf'))
        m = tl.max(x, axis=0)
        e = tl.where(cmask, tl.exp(x - m), 0.0)
        lse = m + tl.log(tl.sum(e, axis=0))
        t = tl.load(t_ptr + r)
        xt = tl.load(x_ptr + r * n_cols + t)
        acc = acc + (lse - xt)
    tl.store(y_ptr, acc / n_rows)


# ------------------------------------------------------------------ ② case 层

import math

DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((8, 32), (11, 35))

def ref(args, meta):
    del meta
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    t = np.asarray(args["t_ptr"], dtype=np.int64)
    m = x.max(-1, keepdims=True)
    lse = m[:, 0] + np.log(np.exp(x - m).sum(-1))
    return {"y_ptr": np.array([float((lse - x[np.arange(len(t)), t]).mean())],
                              dtype=np.float32)}

def make_case(shape=None, *, dtype="float32", seed=20261008):
    if dtype is None:
        dtype = "float32"
    if np.dtype(dtype).name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype!r}; choose from {DTYPES}")
    from case_utils import fast_rng
    rng = fast_rng(seed)
    actual = SHAPES[0] if shape is None else shape
    rows, cols = actual
    x = rng.standard_normal((rows, cols))
    t = rng.integers(0, cols, rows).astype(np.int64)
    args = {'x_ptr': x.astype(np.float32), 't_ptr': t, 'y_ptr': np.zeros(1, dtype=np.float32), 'n_rows': rows, 'n_cols': cols}
    expected = ref(args, {})
    tolerance = {"comparator": "allclose", "exact": False, "rtol": 2e-3, "atol": 2e-3,
                   "equal_nan": True}
    comparison = {name: dict(tolerance) for name in expected}
    return {
        "args": args,
        "meta": {"BLOCK": 1024},
        "grid": (1,),
        "outputs": tuple(expected),
        "expected": expected,
        "comparison": comparison,
        "shape": actual,
        "dtype": "float32",
        "kernel": fused_cross_entropy_log_softmax_kernel,
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
