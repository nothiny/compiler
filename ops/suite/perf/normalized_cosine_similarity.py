"""normalized_cosine_similarity: TritonBench 算子( 类)。
模式: creation.arange、memory.load.masked、math.sqrt、reduce.sum、math.maximum、memory.store。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/normalized_cosine_similarity', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'memory.load.masked', 'math.sqrt', 'reduce.sum', 'math.maximum', 'memory.store', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/normalized_cosine_similarity.py', 'sha256': '8798a4abcea9fb718b6539947943a154707af45a6218149bc94c5ba39cd387e1'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def normalized_cosine_similarity_kernel(x1_ptr, x2_ptr, y_ptr, n_cols, BLOCK: tl.constexpr):
    row = tl.program_id(0)
    cols = tl.arange(0, BLOCK)
    mask = cols < n_cols
    x1 = tl.load(x1_ptr + row * n_cols + cols, mask=mask, other=0.0)
    x2 = tl.load(x2_ptr + row * n_cols + cols, mask=mask, other=0.0)
    n1 = tl.sqrt(tl.sum(x1 * x1, axis=0))
    n2 = tl.sqrt(tl.sum(x2 * x2, axis=0))
    u1 = x1 / tl.maximum(n1, 1e-12)
    u2 = x2 / tl.maximum(n2, 1e-12)
    d = tl.sum(u1 * u2, axis=0)
    denom = tl.maximum(tl.sqrt(tl.sum(u1 * u1, axis=0) * tl.sum(u2 * u2, axis=0)), 1e-8)
    tl.store(y_ptr + row, d / denom)


# ------------------------------------------------------------------ ② case 层

DTYPES = ('float32',)

SHAPES = ((8, 64), (11, 67))

def ref(args, meta):
    del meta
    x1 = np.asarray(args["x1_ptr"], dtype=np.float64)
    x2 = np.asarray(args["x2_ptr"], dtype=np.float64)
    u1 = x1 / np.maximum(np.linalg.norm(x1, axis=-1, keepdims=True), 1e-12)
    u2 = x2 / np.maximum(np.linalg.norm(x2, axis=-1, keepdims=True), 1e-12)
    d = (u1 * u2).sum(-1)
    denom = np.maximum(np.linalg.norm(u1, axis=-1) * np.linalg.norm(u2, axis=-1), 1e-8)
    return {"y_ptr": (d / denom).astype(np.float32)}

def make_case(shape=None, *, dtype="float32", seed=20261008):
    if dtype is None:
        dtype = "float32"
    if np.dtype(dtype).name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype!r}; choose from {DTYPES}")
    from case_utils import fast_rng
    rng = fast_rng(seed)
    actual = SHAPES[0] if shape is None else shape
    rows, cols = actual
    x1 = rng.standard_normal((rows, cols))
    x2 = rng.standard_normal((rows, cols))
    args = {'x1_ptr': x1.astype(np.float32), 'x2_ptr': x2.astype(np.float32), 'y_ptr': np.zeros(rows, dtype=np.float32), 'n_cols': cols}
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
        "kernel": normalized_cosine_similarity_kernel,
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
