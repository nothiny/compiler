"""relu_conv2d: TritonBench 算子( 类)。
模式: math.maximum、memory.store、memory.load、control.for_range、args.runtime_scalar。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/relu_conv2d', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['math.maximum', 'memory.store', 'memory.load', 'control.for_range', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/relu_conv2d.py', 'sha256': 'c4308e369b61d2c56a9fecb29cb15a147d94d391da9182649b09ca8d0d0fa209'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def relu_conv2d_kernel(x_ptr, w_ptr, b_ptr, y_ptr, C, H, W, O, KH, KW):
    q = tl.program_id(0)
    ho = q // (W - KW + 1)
    wo = q % (W - KW + 1)
    o = tl.program_id(1)
    acc = 0.0
    for c in range(0, C):
        for i in range(0, KH):
            for j in range(0, KW):
                xv = tl.load(x_ptr + c * H * W + (ho + i) * W + (wo + j))
                wv = tl.load(w_ptr + o * C * KH * KW + c * KH * KW + i * KW + j)
                acc = acc + xv * wv
    acc = acc + tl.load(b_ptr + o)
    acc = tl.maximum(acc, 0.0)
    tl.store(y_ptr + o * (H - KH + 1) * (W - KW + 1) + q, acc)


# ------------------------------------------------------------------ ② case 层

DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((8,), (9,))

def ref(args, meta):
    del meta
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    w = np.asarray(args["w_ptr"], dtype=np.float64)
    b = np.asarray(args["b_ptr"], dtype=np.float64)
    o, c, kh, kw = w.shape
    _, h, wd = x.shape
    ho, wo = h - kh + 1, wd - kw + 1
    cv = np.zeros((o, ho, wo))
    for oo in range(o):
        for cc in range(c):
            for i in range(kh):
                for j in range(kw):
                    cv[oo] += x[cc, i:i + ho, j:j + wo] * w[oo, cc, i, j]
    return {"y_ptr": (np.maximum(cv + b[:, None, None], 0)).astype(np.float32)}

def make_case(shape=None, *, dtype="float32", seed=20261008):
    if dtype is None:
        dtype = "float32"
    if np.dtype(dtype).name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype!r}; choose from {DTYPES}")
    from case_utils import fast_rng
    rng = fast_rng(seed)
    actual = SHAPES[0] if shape is None else shape
    side = actual[0]
    c, o, k = 2, 3, 3
    x = rng.standard_normal((c, side, side)) * 0.5
    w = rng.standard_normal((o, c, k, k)) * 0.5
    b = rng.standard_normal(o) * 0.1
    args = {'x_ptr': x.astype(np.float32), 'w_ptr': w.astype(np.float32), 'b_ptr': b.astype(np.float32), 'y_ptr': np.zeros((3, side - 2, side - 2), dtype=np.float32), 'C': c, 'H': side, 'W': side, 'O': o, 'KH': k, 'KW': k}
    expected = ref(args, {})
    tolerance = {"comparator": "allclose", "exact": False, "rtol": 2e-3, "atol": 2e-3,
                   "equal_nan": True}
    comparison = {name: dict(tolerance) for name in expected}
    return {
        "args": args,
        "meta": {},
        "grid": ((side - 2) * (side - 2), 3),
        "outputs": tuple(expected),
        "expected": expected,
        "comparison": comparison,
        "shape": actual,
        "dtype": "float32",
        "kernel": relu_conv2d_kernel,
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
