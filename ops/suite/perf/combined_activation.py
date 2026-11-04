"""combined_activation: TritonBench 算子( 类)。
模式: creation.arange、creation.zeros、math.sigmoid、memory.load.masked、memory.store.masked、reduce.sum。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/combined_activation', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'creation.zeros', 'math.sigmoid', 'memory.load.masked', 'memory.store.masked', 'reduce.sum', 'control.for_range', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/combined_activation.py', 'sha256': '3ae99c04d3efa11d0a761280960c181df441af956b9f876de833d3e893aef5a5'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def combined_activation_kernel(x_ptr, w1_ptr, w2_ptr, b_ptr, y_ptr, K, N):
    row = tl.program_id(0)
    offs_n = tl.arange(0, 64)
    nmask = offs_n < N
    acc = tl.zeros((64,), tl.float32)
    for k0 in range(0, K, 32):
        offs_k = k0 + tl.arange(0, 32)
        kmask = offs_k < K
        x = tl.load(x_ptr + row * K + offs_k, mask=kmask, other=0.0)
        w1 = tl.load(w1_ptr + offs_k[:, None] * N + offs_n[None, :],
                     mask=kmask[:, None] & nmask[None, :], other=0.0)
        acc = acc + tl.sum(w1 * x[:, None], axis=0)
    s = tl.sigmoid(acc)
    t = 2.0 * tl.sigmoid(2.0 * s) - 1.0
    w2 = tl.load(w2_ptr + row * N + offs_n, mask=nmask, other=0.0)
    bias = tl.load(b_ptr + row * N + offs_n, mask=nmask, other=0.0)
    y = t * w2 + bias
    tl.store(y_ptr + row * N + offs_n, y, mask=nmask)


# ------------------------------------------------------------------ ② case 层

DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((16, 32), (17, 33))

def ref(args, meta):
    del meta
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    w1 = np.asarray(args["w1_ptr"], dtype=np.float64)
    w2 = np.asarray(args["w2_ptr"], dtype=np.float64)
    b = np.asarray(args["b_ptr"], dtype=np.float64)
    s = 1.0 / (1.0 + np.exp(-(x @ w1)))
    t = np.tanh(s)
    return {"y_ptr": (t * w2 + b).astype(np.float32)}

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
    w1 = rng.standard_normal((k, n)) * 0.5
    w2 = rng.standard_normal((rows, n)) * 0.5
    b = rng.standard_normal((rows, n)) * 0.5
    args = {'x_ptr': x.astype(np.float32), 'w1_ptr': w1.astype(np.float32), 'w2_ptr': w2.astype(np.float32), 'b_ptr': b.astype(np.float32), 'y_ptr': np.zeros((rows, n), dtype=np.float32), 'K': k, 'N': n}
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
        "kernel": combined_activation_kernel,
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
