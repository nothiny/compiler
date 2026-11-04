"""sigmoid_adaptive_avg_pool2d: TritonBench 算子( 类)。
模式: creation.arange、memory.load.masked、math.sigmoid、memory.store、reduce.sum、args.runtime_scalar。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/sigmoid_adaptive_avg_pool2d', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'memory.load.masked', 'math.sigmoid', 'memory.store', 'reduce.sum', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/sigmoid_adaptive_avg_pool2d.py', 'sha256': '5632ed64d11b255dd4a1e2528888f29c08152f251f25fed00bc50dfd604bce45'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def sigmoid_adaptive_avg_pool2d_kernel(x_ptr, y_ptr, n_cols, BLOCK: tl.constexpr):
    row = tl.program_id(0)
    cols = tl.arange(0, BLOCK)
    mask = cols < n_cols
    x = tl.load(x_ptr + row * n_cols + cols, mask=mask, other=0.0)
    y = tl.sum(x, axis=0) / n_cols
    y = tl.sigmoid(y)
    tl.store(y_ptr + row, y)


# ------------------------------------------------------------------ ② case 层

DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((4, 64), (24, 64))

def ref(args, meta):
    del meta
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    m = x.reshape(x.shape[0], -1).mean(-1)
    return {"y_ptr": (1.0 / (1.0 + np.exp(-m))).astype(np.float32)}

def make_case(shape=None, *, dtype="float32", seed=20261008):
    if dtype is None:
        dtype = "float32"
    if np.dtype(dtype).name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype!r}; choose from {DTYPES}")
    from case_utils import fast_rng
    rng = fast_rng(seed)
    actual = SHAPES[0] if shape is None else shape
    c, hw = actual
    side = int(round(np.sqrt(hw)))
    x = rng.standard_normal((c, side, side))
    args = {'x_ptr': x.astype(np.float32), 'y_ptr': np.zeros(c, dtype=np.float32), 'n_cols': hw}
    expected = ref(args, {})
    tolerance = {"comparator": "allclose", "exact": False, "rtol": 2e-3, "atol": 2e-3,
                   "equal_nan": True}
    comparison = {name: dict(tolerance) for name in expected}
    return {
        "args": args,
        "meta": {"BLOCK": 1024},
        "grid": (c,),
        "outputs": tuple(expected),
        "expected": expected,
        "comparison": comparison,
        "shape": actual,
        "dtype": "float32",
        "kernel": sigmoid_adaptive_avg_pool2d_kernel,
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
