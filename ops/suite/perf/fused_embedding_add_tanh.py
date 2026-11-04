"""fused_embedding_add_tanh: TritonBench 算子( 类)。
模式: creation.arange、memory.load、memory.load.masked、memory.store.masked、math.sigmoid、args.runtime_scalar。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/fused_embedding_add_tanh', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'memory.load', 'memory.load.masked', 'memory.store.masked', 'math.sigmoid', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/fused_embedding_add_tanh.py', 'sha256': '1deaa3da6c9cb3e43045ee5b881342972af6c9aaf03df5abe8d7c8ff230a5928'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def fused_embedding_add_tanh_kernel(idx_ptr, w_ptr, o_ptr, y_ptr, dim, BLOCK: tl.constexpr):
    row = tl.program_id(0)
    cols = tl.arange(0, BLOCK)
    mask = cols < dim
    src = tl.load(idx_ptr + row)
    w = tl.load(w_ptr + src * dim + cols, mask=mask, other=0.0)
    o = tl.load(o_ptr + row * dim + cols, mask=mask, other=0.0)
    z = w + o
    y = 2.0 * tl.sigmoid(2.0 * z) - 1.0
    tl.store(y_ptr + row * dim + cols, y, mask=mask)


# ------------------------------------------------------------------ ② case 层

DTYPES = ('float32',)

SHAPES = ((16, 32), (17, 33))

def ref(args, meta):
    del meta
    idx = np.asarray(args["idx_ptr"], dtype=np.int64)
    w = np.asarray(args["w_ptr"], dtype=np.float64)
    o = np.asarray(args["o_ptr"], dtype=np.float64)
    return {"y_ptr": np.tanh(w[idx] + o).astype(np.float32)}

def make_case(shape=None, *, dtype="float32", seed=20261008):
    if dtype is None:
        dtype = "float32"
    if np.dtype(dtype).name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype!r}; choose from {DTYPES}")
    from case_utils import fast_rng
    rng = fast_rng(seed)
    actual = SHAPES[0] if shape is None else shape
    n_sel, dim = actual
    vocab = 128
    idx = rng.integers(0, vocab, n_sel).astype(np.int32)
    w = rng.standard_normal((vocab, dim)) * 0.5
    o = rng.standard_normal((n_sel, dim)) * 0.5
    args = {'idx_ptr': idx, 'w_ptr': w.astype(np.float32), 'o_ptr': o.astype(np.float32), 'y_ptr': np.zeros((n_sel, dim), dtype=np.float32), 'dim': dim}
    expected = ref(args, {})
    tolerance = {"comparator": "allclose", "exact": False, "rtol": 2e-3, "atol": 2e-3,
                   "equal_nan": True}
    comparison = {name: ({"comparator": "array_equal", "exact": True}
                    if np.asarray(value).dtype == np.bool_ else dict(tolerance))
                  for name, value in expected.items()}
    return {
        "args": args,
        "meta": {"BLOCK": 1024},
        "grid": (n_sel,),
        "outputs": tuple(expected),
        "expected": expected,
        "comparison": comparison,
        "shape": actual,
        "dtype": "float32",
        "kernel": fused_embedding_add_tanh_kernel,
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
