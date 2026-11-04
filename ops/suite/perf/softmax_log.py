"""softmax_log: norm(reduction 类)。
bench 稳态配置见 bench/workload.json(声明 shape [4, 16],验证 shape [64, 1024]);正确性 shape 见下方 SHAPES。
模式: creation.arange、creation.where、math.log、math.maximum、reduce.sum、memory.store。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/softmax_log', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'creation.where', 'math.log', 'math.maximum', 'reduce.sum', 'memory.store', 'memory.load', 'reduce.max']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/softmax_log.py', 'sha256': '2373dc38eb433d4410c5d56aa2b6eb6fe0573745a8c8c6c2686ef565872cdc4e'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def softmax_log_kernel(x_ptr,y_ptr,n_cols,BLOCK_N:tl.constexpr):
    row=tl.program_id(0)
    lane=tl.arange(0,BLOCK_N)
    maximum=-float('inf')
    has_nan=0
    for start in range(0,n_cols,BLOCK_N):
        cols=start+lane
        z=tl.log(tl.load(x_ptr+row*n_cols+cols,cols<n_cols,other=1.0))
        has_nan |= tl.sum(((cols<n_cols)&(z!=z)).to(tl.int32),0)>0
        maximum=tl.maximum(maximum,tl.max(tl.where((cols<n_cols)&(z==z),z,-float('inf')),0))
    maximum=tl.where(has_nan != 0,float('nan'),maximum)
    total=0.0
    for start in range(0,n_cols,BLOCK_N):
        cols=start+lane
        z=tl.log(tl.load(x_ptr+row*n_cols+cols,cols<n_cols,other=1.0))
        total+=tl.sum(tl.where(cols<n_cols,tl.exp(z-maximum),0.0),0)
    for start in range(0,n_cols,BLOCK_N):
        cols=start+lane
        z=tl.log(tl.load(x_ptr+row*n_cols+cols,cols<n_cols,other=1.0))
        tl.store(y_ptr+row*n_cols+cols,tl.exp(z-maximum)/total,cols<n_cols)


# ------------------------------------------------------------------ ② case 层

DTYPES = ('float32',)

SHAPES = ((4, 16), (4, 97))

def ref(args, meta):
    del meta
    x64 = np.asarray(args["x_ptr"], dtype=np.float64)
    z = np.log(x64)
    e = np.exp(z - z.max(-1, keepdims=True))
    result = e / e.sum(-1, keepdims=True)
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
    x = rng.uniform(0.1, 5.0, (rows, cols))
    args = {'x_ptr': x.astype(np.float32), 'y_ptr': np.zeros((rows, cols), dtype=np.float32), 'n_cols': cols}
    expected = ref(args, {})
    tolerance = {"comparator": "allclose", "exact": False, "rtol": 1e-4, "atol": 1e-7,
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
        "kernel": softmax_log_kernel,
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
