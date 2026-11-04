"""chebyshev_polynomial_t: TritonBench 算子( 类)。
模式: memory.load.masked、creation.where、memory.store.masked、creation.arange、control.for_range、args.runtime_scalar。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/chebyshev_polynomial_t', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['memory.load.masked', 'creation.where', 'memory.store.masked', 'creation.arange', 'control.for_range', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/chebyshev_polynomial_t.py', 'sha256': 'ea4e887262cb3ec57edb75991380d496f1ae0e86f67f0f39c4359db09034ec98'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def chebyshev_polynomial_t_kernel(x_ptr, y_ptr, order, n_elements, BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(0)
    offsets = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = offsets < n_elements
    x = tl.load(x_ptr + offsets, mask=mask, other=0.0)
    t_prev = x * 0.0 + 1.0
    t_cur = x
    for _ in range(1, order):
        t_next = 2.0 * x * t_cur - t_prev
        t_prev = t_cur
        t_cur = t_next
    y = tl.where(order == 0, x * 0.0 + 1.0, t_cur)
    tl.store(y_ptr + offsets, y, mask=mask)


# ------------------------------------------------------------------ ② case 层

DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((128,), (99,))

def ref(args, meta):
    del meta
    x64 = np.asarray(args["x_ptr"], dtype=np.float64)
    order = int(args["order"])
    return {"y_ptr": (np.cos(order * np.arccos(x64))).astype(np.float32)}

def make_case(shape=None, *, dtype="float32", seed=20261008):
    if dtype is None:
        dtype = "float32"
    if np.dtype(dtype).name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype!r}; choose from {DTYPES}")
    actual_shape = tuple(SHAPES[0] if shape is None else (int(v) for v in shape))
    if not actual_shape or any(v <= 0 for v in actual_shape):
        raise ValueError("shape dimensions must be positive")
    from case_utils import fast_rng
    rng = fast_rng(seed)
    n = int(np.prod(actual_shape, dtype=np.int64))
    x = rng.uniform(-1.0, 1.0, n)
    args = {'x_ptr': x.astype(np.float32), 'order': 3, 'y_ptr': np.zeros(n, dtype=np.float32), 'n_elements': n}
    expected = ref(args, {})
    tolerance = {"comparator": "allclose", "exact": False, "rtol": 2e-3, "atol": 2e-3,
                   "equal_nan": True}
    comparison = {name: ({"comparator": "array_equal", "exact": True}
                    if np.asarray(value).dtype == np.bool_ else dict(tolerance))
                  for name, value in expected.items()}
    return {
        "args": args,
        "meta": {"BLOCK_SIZE": 1024},
        "grid": (int((n + 1023) // 1024),),
        "outputs": tuple(expected),
        "expected": expected,
        "comparison": comparison,
        "shape": actual_shape,
        "dtype": "float32",
        "kernel": chebyshev_polynomial_t_kernel,
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
