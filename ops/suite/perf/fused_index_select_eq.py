"""fused_index_select_eq: layout(memory 类)。
bench 稳态配置见 bench/workload.json(声明 shape [4, 16],验证 shape [16384, 16]);正确性 shape 见下方 SHAPES。
模式: creation.arange、memory.load、memory.load.masked、memory.store.masked、args.runtime_scalar。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/fused_index_select_eq', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'memory.load', 'memory.load.masked', 'memory.store.masked', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/fused_index_select_eq.py', 'sha256': '13a1fab078acf7d9d43c0509aa9e1185e5f1c0e54fd788453317dc78771d7535'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def fused_index_select_eq_kernel(x_ptr, index_ptr, other_ptr, y_ptr, n_cols,
                                 BLOCK: tl.constexpr):
    row = tl.program_id(0)
    cols = tl.arange(0, BLOCK)
    mask = cols < n_cols
    src = tl.load(index_ptr + row)
    x = tl.load(x_ptr + src * n_cols + cols, mask=mask, other=0.0)
    o = tl.load(other_ptr + row * n_cols + cols, mask=mask, other=0.0)
    tl.store(y_ptr + row * n_cols + cols, x == o, mask=mask)


# ------------------------------------------------------------------ ② case 层

DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((4, 16), (5, 17))

def ref(args, meta):
    del meta
    x = np.asarray(args["x_ptr"])
    index = np.asarray(args["index_ptr"], dtype=np.int64)
    other = np.asarray(args["other_ptr"])
    return {"y_ptr": (x[index] == other).astype(np.bool_)}

def make_case(shape=None, *, dtype="float32", seed=20261008):
    if dtype is None:
        dtype = "float32"
    if np.dtype(dtype).name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype!r}; choose from {DTYPES}")
    from case_utils import fast_rng
    rng = fast_rng(seed)
    actual = SHAPES[0] if shape is None else shape
    rows, cols = actual
    n_sel = rows
    x = rng.integers(-3, 4, (rows, cols)).astype(np.float32)
    index = rng.integers(0, rows, n_sel).astype(np.int32)
    other = rng.integers(-3, 4, (n_sel, cols)).astype(np.float32)
    args = {'x_ptr': x, 'index_ptr': index, 'other_ptr': other, 'y_ptr': np.zeros((n_sel, cols), dtype=np.bool_), 'n_cols': cols}
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
        "kernel": fused_index_select_eq_kernel,
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
