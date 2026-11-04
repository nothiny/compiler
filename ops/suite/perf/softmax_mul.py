"""softmax_mul: norm(reduction 类)。
bench 稳态配置见 bench/workload.json(声明 shape [4, 16],验证 shape [64, 1024]);正确性 shape 见下方 SHAPES。
模式: creation.arange、memory.load.masked、reduce.max、creation.where、memory.store.masked、math.exp。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/softmax_mul', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'memory.load.masked', 'reduce.max', 'creation.where', 'memory.store.masked', 'math.exp', 'reduce.sum', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/softmax_mul.py', 'sha256': '3122585adabb8f699db3babbcc05f2ced8450e8d7617b4a773fe9cd3833add83'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def softmax_mul_kernel(x_ptr, o_ptr, y_ptr, n_cols, BLOCK_N: tl.constexpr):
    row = tl.program_id(0)
    cols = tl.arange(0, BLOCK_N)
    mask = cols < n_cols
    x = tl.load(x_ptr + row * n_cols + cols, mask=mask, other=1.0)
    z = x
    o = tl.load(o_ptr + row * n_cols + cols, mask=mask, other=0.0)
    m = tl.max(tl.where(mask, z, float('-inf')), axis=0)
    e = tl.where(mask, tl.exp(z - m), 0.0)
    y = e / tl.sum(e, axis=0)
    y = y * o
    tl.store(y_ptr + row * n_cols + cols, y, mask=mask)


# ------------------------------------------------------------------ ② case 层

DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((4, 16), (4, 97))

def ref(args, meta):
    del meta
    x64 = np.asarray(args["x_ptr"], dtype=np.float64)
    o64 = np.asarray(args['o_ptr'], dtype=np.float64)
    e = np.exp(x64 - x64.max(-1, keepdims=True))
    sm = e / e.sum(-1, keepdims=True)
    result = sm * o64
    return {"y_ptr": np.asarray(result).astype(np.float32)}

def make_case(shape=None, *, dtype="float32", seed=20261008):
    if dtype is None:
        dtype = "float32"
    if np.dtype(dtype).name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype!r}; choose from {DTYPES}")
    actual = SHAPES[0] if shape is None else tuple(int(v) for v in shape)
    rows, cols = (actual if len(actual) == 2 else (1, actual[0]))
    n = int(np.prod(actual, dtype=np.int64))
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = rng.standard_normal((rows, cols)) * 3.0
    o = rng.uniform(0.5, 2.0, (rows, cols))
    args = {'x_ptr': x.astype(np.float32), 'o_ptr': o.astype(np.float32), 'y_ptr': np.zeros((rows, cols), dtype=np.float32), 'n_cols': cols}
    expected = ref(args, {})
    tolerance = {"comparator": "allclose", "exact": False, "rtol": 2e-3, "atol": 2e-3,
                   "equal_nan": True}
    comparison = {name: dict(tolerance) for name in expected}
    return {
        "args": args,
        "meta": {"BLOCK_N": 1024},
        "grid": (rows,),
        "outputs": tuple(expected),
        "expected": expected,
        "comparison": comparison,
        "shape": (rows, cols),
        "dtype": "float32",
        "kernel": softmax_mul_kernel,
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
