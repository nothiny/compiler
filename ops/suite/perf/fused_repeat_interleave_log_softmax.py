"""fused_repeat_interleave_log_softmax: TritonBench 算子( 类)。
模式: creation.arange、memory.load.masked、reduce.max、creation.where、memory.store.masked、math.exp。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/fused_repeat_interleave_log_softmax', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'memory.load.masked', 'reduce.max', 'creation.where', 'memory.store.masked', 'math.exp', 'math.log', 'reduce.sum']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/fused_repeat_interleave_log_softmax.py', 'sha256': '13f1734657a2014cc88455d2ab8ec8cf644886412354d5d02a6e596ef1f113a3'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def fused_repeat_interleave_log_softmax_kernel(x_ptr, y_ptr, COLS, R, L,
                                               BE: tl.constexpr):
    row = tl.program_id(0)
    pos = tl.arange(0, BE)
    mask = pos < L
    cidx = pos // R
    x = tl.load(x_ptr + row * COLS + cidx, mask=mask, other=float('-inf'))
    m = tl.max(x, axis=0)
    e = tl.where(mask, tl.exp(x - m), 0.0)
    lse = m + tl.log(tl.sum(e, axis=0))
    tl.store(y_ptr + row * L + pos, x - lse, mask=mask)


# ------------------------------------------------------------------ ② case 层

DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((3, 4), (4, 5))

def _next_pow2(value):
    size = 1
    while size < value:
        size *= 2
    return size

def ref(args, meta):
    del meta
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    r = int(args["R"])
    rep = np.repeat(x, r, axis=1)
    m = rep.max(axis=1, keepdims=True)
    lse = m + np.log(np.exp(rep - m).sum(axis=1, keepdims=True))
    return {"y_ptr": (rep - lse).astype(np.float32)}

def make_case(shape=None, *, dtype="float32", seed=20261008):
    if dtype is None:
        dtype = "float32"
    if np.dtype(dtype).name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype!r}; choose from {DTYPES}")
    from case_utils import fast_rng
    rng = fast_rng(seed)
    actual = SHAPES[0] if shape is None else shape
    rows, cols = actual
    r = 2
    l = cols * r
    x = rng.standard_normal((rows, cols)) * 0.5
    args = {'x_ptr': x.astype(np.float32),
            'y_ptr': np.zeros((rows, l), dtype=np.float32),
            'COLS': cols, 'R': r, 'L': l}
    expected = ref(args, {})
    tolerance = {"comparator": "allclose", "exact": False, "rtol": 2e-3, "atol": 2e-3,
                 "equal_nan": True}
    comparison = {name: dict(tolerance) for name in expected}
    return {
        "args": args,
        "meta": {"BE": _next_pow2(l)},
        "grid": (rows,),
        "outputs": tuple(expected),
        "expected": expected,
        "comparison": comparison,
        "shape": actual,
        "dtype": "float32",
        "kernel": fused_repeat_interleave_log_softmax_kernel,
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
