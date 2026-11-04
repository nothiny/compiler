"""gelu_std: TritonBench 算子( 类)。
模式: creation.arange、creation.where、memory.load、memory.store、math.maximum、reduce.sum。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/gelu_std', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'creation.where', 'memory.load', 'memory.store', 'math.maximum', 'reduce.sum', 'math.sqrt', 'reduce.max']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/gelu_std.py', 'sha256': '7feec56d15b80a908ae571362258b315ed875124e07d32cfae10e7cc94e2580b'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def gelu_std_kernel(x_ptr,y_ptr,n_cols,BLOCK_N:tl.constexpr):
    row=tl.program_id(0)
    lane=tl.arange(0,BLOCK_N)
    scale=0.0
    for start in range(0,n_cols,BLOCK_N):
        cols=start+lane
        x=tl.load(x_ptr+row*n_cols+cols,cols<n_cols,other=0.0)
        value = 0.5 * x * (1.0 + tl.erf(x * 0.7071067811865476))
        scale=tl.maximum(scale,tl.max(tl.where(cols<n_cols,tl.abs(value),0.0),0))
    scale=tl.where(scale>0.0,scale,1.0)
    first_x=tl.load(x_ptr+row*n_cols)
    # Keep the origin in input units until after subtraction.
    origin=0.5 * first_x * (1.0 + tl.erf(first_x * 0.7071067811865476))
    delta=0.0
    for start in range(0,n_cols,BLOCK_N):
        cols=start+lane
        x=tl.load(x_ptr+row*n_cols+cols,cols<n_cols,other=0.0)
        value = 0.5 * x * (1.0 + tl.erf(x * 0.7071067811865476))
        shifted = tl.where((value >= 0.0) == (origin >= 0.0), tl.div_rn(value-origin,scale), tl.div_rn(value,scale)-tl.div_rn(origin,scale))
        delta+=tl.sum(tl.where(cols<n_cols,tl.div_rn(shifted,tl.cast(n_cols,tl.float32)),0.0),0)
    mean=delta
    squares=0.0
    for start in range(0,n_cols,BLOCK_N):
        cols=start+lane
        x=tl.load(x_ptr+row*n_cols+cols,cols<n_cols,other=0.0)
        value = 0.5 * x * (1.0 + tl.erf(x * 0.7071067811865476))
        shifted = tl.where((value >= 0.0) == (origin >= 0.0), tl.div_rn(value-origin,scale), tl.div_rn(value,scale)-tl.div_rn(origin,scale))
        diff=shifted-mean
        squares+=tl.sum(tl.where(cols<n_cols,diff*diff,0.0),0)
    result=scale*tl.sqrt(squares/tl.maximum(n_cols-1,1))
    tl.store(y_ptr+row,tl.where(n_cols>1,result,float('nan')))


# ------------------------------------------------------------------ ② case 层

import math

DTYPES = ('float32',)

SHAPES = ((4, 16), (4, 97))

def _verf(x):
    from mathref import erf
    return erf(x)

def ref(args, meta):
    del meta
    x64 = np.asarray(args["x_ptr"], dtype=np.float64)
    g = 0.5 * x64 * (1.0 + _verf(x64 / np.sqrt(2.0)))
    result = g.std(-1, ddof=1)
    return {"y_ptr": np.asarray(result).astype(np.float32)}

def make_case(shape=None, *, dtype="float32", seed=20261008):
    if dtype is None:
        dtype = "float32"
    if np.dtype(dtype).name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype!r}; choose from {DTYPES}")
    actual = SHAPES[0] if shape is None else tuple(int(v) for v in shape)
    rows, cols = (actual if len(actual) == 2 else (1, actual[0]))
    if len(actual) not in (1,2) or rows <= 0 or cols <= 0:
        raise ValueError("expected a nonempty row or positive 2D shape")
    n = int(np.prod(actual, dtype=np.int64))
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = rng.standard_normal((rows, cols)) * 3.0
    args = {'x_ptr': x.astype(np.float32), 'y_ptr': np.zeros(rows, dtype=np.float32), 'n_cols': cols}
    expected = ref(args, {})
    tolerance = {"comparator": "allclose", "exact": False, "rtol": 3e-5, "atol": 3e-6,
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
        "kernel": gelu_std_kernel,
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
