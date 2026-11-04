"""log_softmax_linear: matmul(compute 类)。
bench 稳态配置见 bench/workload.json(声明 shape [16, 32],验证 shape [256, 32]);正确性 shape 见下方 SHAPES。
模式: creation.arange、creation.zeros、reduce.max、creation.where、memory.store.masked、memory.load.masked。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/log_softmax_linear', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'creation.zeros', 'reduce.max', 'creation.where', 'memory.store.masked', 'memory.load.masked', 'math.exp', 'math.log']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/log_softmax_linear.py', 'sha256': 'cdfccb5ab477d5af274fc50938855056e0e40889cfad2825040964ee2153b537'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def log_softmax_linear_kernel(x_ptr, w_ptr, y_ptr, K, N):
    row = tl.program_id(0)
    offs_n = tl.arange(0, 64)
    nmask = offs_n < N
    acc = tl.zeros((64,), tl.float32)
    for k0 in range(0, K, 32):
        offs_k = k0 + tl.arange(0, 32)
        kmask = offs_k < K
        x = tl.load(x_ptr + row * K + offs_k, mask=kmask, other=0.0)
        w = tl.load(w_ptr + offs_n[:, None] * K + offs_k[None, :],
                    mask=nmask[:, None] & kmask[None, :], other=0.0)
        acc = acc + tl.sum(w * x[None, :], axis=1)
    m = tl.max(tl.where(nmask, acc, float('-inf')), axis=0)
    e = tl.where(nmask, tl.exp(acc - m), 0.0)
    y = acc - m - tl.log(tl.sum(e, axis=0))
    tl.store(y_ptr + row * N + offs_n, y, mask=nmask)


# ------------------------------------------------------------------ ② case 层

DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((16, 32), (17, 33))

def ref(args, meta):
    del meta
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    w = np.asarray(args["w_ptr"], dtype=np.float64)
    z = x @ w.T
    m = z.max(-1, keepdims=True)
    return {"y_ptr": (z - m - np.log(np.exp(z - m).sum(-1, keepdims=True))).astype(np.float32)}

def make_case(shape=None, *, dtype="float32", seed=20261008):
    if dtype is None:
        dtype = "float32"
    if np.dtype(dtype).name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype!r}; choose from {DTYPES}")
    from case_utils import fast_rng
    rng = fast_rng(seed)
    actual = SHAPES[0] if shape is None else shape
    rows, k = actual
    n = 24
    x = rng.standard_normal((rows, k)) * 0.5
    w = rng.standard_normal((n, k)) * 0.5
    args = {'x_ptr': x.astype(np.float32), 'w_ptr': w.astype(np.float32), 'y_ptr': np.zeros((rows, n), dtype=np.float32), 'K': k, 'N': n}
    expected = ref(args, {})
    tolerance = {"comparator": "allclose", "exact": False, "rtol": 2e-3, "atol": 2e-3,
                   "equal_nan": True}
    comparison = {name: ({"comparator": "array_equal", "exact": True}
                    if np.asarray(value).dtype == np.bool_ else dict(tolerance))
                  for name, value in expected.items()}
    return {
        "args": args,
        "meta": {},
        "grid": (rows,),
        "outputs": tuple(expected),
        "expected": expected,
        "comparison": comparison,
        "shape": actual,
        "dtype": "float32",
        "kernel": log_softmax_linear_kernel,
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
