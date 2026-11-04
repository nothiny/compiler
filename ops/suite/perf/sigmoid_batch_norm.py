"""sigmoid_batch_norm: norm(reduction 类)。
bench 稳态配置见 bench/workload.json(声明 shape [4, 64],验证 shape [64, 1024]);正确性 shape 见下方 SHAPES。
模式: creation.arange、memory.load.masked、math.sigmoid、memory.store.masked、math.sqrt、args.runtime_scalar。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/sigmoid_batch_norm', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'memory.load.masked', 'math.sigmoid', 'memory.store.masked', 'math.sqrt', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/sigmoid_batch_norm.py', 'sha256': 'bee4d2759aee122e9f4b930f076345a71ce5415205da76f918722af3ea33dae4'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def sigmoid_batch_norm_kernel(x_ptr, rm_ptr, rv_ptr, w_ptr, b_ptr, y_ptr, n_cols, BLOCK: tl.constexpr):
    row = tl.program_id(0)
    cols = tl.arange(0, BLOCK)
    mask = cols < n_cols
    x = tl.load(x_ptr + row * n_cols + cols, mask=mask, other=0.0)
    rm = tl.load(rm_ptr + cols, mask=mask, other=0.0)
    rv = tl.load(rv_ptr + cols, mask=mask, other=0.0)
    w = tl.load(w_ptr + cols, mask=mask, other=0.0)
    b = tl.load(b_ptr + cols, mask=mask, other=0.0)
    y = (x - rm) / tl.sqrt(rv + 1e-5) * w + b
    y = tl.sigmoid(y)
    tl.store(y_ptr + row * n_cols + cols, y, mask=mask)


# ------------------------------------------------------------------ ② case 层

DTYPES = ('float32',)

SHAPES = ((4, 64), (5, 65))

def ref(args, meta):
    del meta
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    rm = np.asarray(args["rm_ptr"], dtype=np.float64)
    rv = np.asarray(args["rv_ptr"], dtype=np.float64)
    w = np.asarray(args["w_ptr"], dtype=np.float64)
    b = np.asarray(args["b_ptr"], dtype=np.float64)
    bn = (x - rm[None, :]) / np.sqrt(rv[None, :] + 1e-5) * w[None, :] + b[None, :]
    return {"y_ptr": (1.0 / (1.0 + np.exp(-bn))).astype(np.float32)}

def make_case(shape=None, *, dtype="float32", seed=20261008):
    if dtype is None:
        dtype = "float32"
    if np.dtype(dtype).name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype!r}; choose from {DTYPES}")
    from case_utils import fast_rng
    rng = fast_rng(seed)
    actual = SHAPES[0] if shape is None else shape
    rows, cols = actual
    x = rng.standard_normal((rows, cols)) * 2.0
    rm = rng.standard_normal(cols) * 0.1
    rv = rng.uniform(0.5, 2.0, cols)
    w = rng.standard_normal(cols) * 0.5 + 1.0
    b = rng.standard_normal(cols) * 0.1
    args = {'x_ptr': x.astype(np.float32), 'rm_ptr': rm.astype(np.float32), 'rv_ptr': rv.astype(np.float32), 'w_ptr': w.astype(np.float32), 'b_ptr': b.astype(np.float32), 'y_ptr': np.zeros((rows, cols), dtype=np.float32), 'n_cols': cols}
    expected = ref(args, {})
    tolerance = {"comparator": "allclose", "exact": False, "rtol": 2e-3, "atol": 2e-3,
                   "equal_nan": True}
    comparison = {name: dict(tolerance) for name in expected}
    return {
        "args": args,
        "meta": {"BLOCK": 1024},
        "grid": (rows,),
        "outputs": tuple(expected),
        "expected": expected,
        "comparison": comparison,
        "shape": actual,
        "dtype": "float32",
        "kernel": sigmoid_batch_norm_kernel,
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
