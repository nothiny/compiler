"""leaky_relu: TritonBench 算子( 类)。
模式: memory.load.masked、creation.where、memory.store.masked、creation.arange、args.runtime_scalar。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/leaky_relu', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['memory.load.masked', 'creation.where', 'memory.store.masked', 'creation.arange', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/leaky_relu.py', 'sha256': 'bed5c909de9f79cde4cd6325c0c54113d11aa7e7453048c286b44c701c8a7379'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def leaky_relu_kernel(x_ptr, y_ptr, slope, n_elements, BLOCK: tl.constexpr):
    pid = tl.program_id(0)
    offs = pid * BLOCK + tl.arange(0, BLOCK)
    mask = offs < n_elements
    x = tl.load(x_ptr + offs, mask=mask, other=0.0)
    y = tl.where(x >= 0.0, x, slope * x)
    tl.store(y_ptr + offs, y, mask=mask)


# ------------------------------------------------------------------ ② case 层

DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((128,), (99,))

def ref(args, meta):
    del meta
    x64 = np.asarray(args["x_ptr"], dtype=np.float64)
    slope = float(args["slope"])
    return {"y_ptr": np.where(x64 >= 0, x64, slope * x64).astype(np.float32)}

def make_case(shape=None, *, dtype="float32", seed=20261008):
    if dtype is None:
        dtype = "float32"
    if np.dtype(dtype).name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype!r}; choose from {DTYPES}")
    from case_utils import fast_rng
    rng = fast_rng(seed)
    actual = SHAPES[0] if shape is None else shape
    n = int(np.prod(actual))
    x = rng.standard_normal(n) * 3.0
    args = {'x_ptr': x.astype(np.float32), 'y_ptr': np.zeros(n, dtype=np.float32), 'n_elements': n, 'slope': 0.1}
    expected = ref(args, {})
    tolerance = {"comparator": "allclose", "exact": False, "rtol": 2e-3, "atol": 2e-3,
                   "equal_nan": True}
    comparison = {name: dict(tolerance) for name in expected}
    return {
        "args": args,
        "meta": {"BLOCK": 1024},
        "grid": ((n + 1023) // 1024,),
        "outputs": tuple(expected),
        "expected": expected,
        "comparison": comparison,
        "shape": actual,
        "dtype": "float32",
        "kernel": leaky_relu_kernel,
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
