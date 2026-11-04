"""det: TritonBench 算子( 类)。
模式: creation.where、memory.store、memory.load、math.abs、control.for_range、args.runtime_scalar。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/det', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.where', 'memory.store', 'memory.load', 'math.abs', 'control.for_range', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/det.py', 'sha256': 'a52c9f83f357f1ad3d1c327e5bbb7d73dd2c7d6812bb72d023acf3eabd8e31a4'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def det_kernel(a_ptr, y_ptr, w_ptr, ptmp_ptr, n):
    for i in range(0, n):
        for j in range(0, n):
            tl.store(w_ptr + i * n + j, tl.load(a_ptr + i * n + j))
    swaps = 0

    for i in range(0, n):
        tl.store(ptmp_ptr + i, i)
    for k in range(0, n):
        best = 0.0
        best_i = k
        for i in range(k, n):
            v = tl.abs(tl.load(w_ptr + i * n + k))
            take = v > best
            best = tl.where(take, v, best)
            best_i = tl.where(take, i, best_i)
        for j in range(0, n):
            a = tl.load(w_ptr + k * n + j)
            b = tl.load(w_ptr + best_i * n + j)
            tl.store(w_ptr + k * n + j, b)
            tl.store(w_ptr + best_i * n + j, a)
        swaps = swaps + tl.where(best_i == k, 0, 1)
        pa = tl.load(ptmp_ptr + k)
        pb = tl.load(ptmp_ptr + best_i)
        tl.store(ptmp_ptr + k, pb)
        tl.store(ptmp_ptr + best_i, pa)
        piv = tl.load(w_ptr + k * n + k)
        for i in range(k + 1, n):
            f = tl.load(w_ptr + i * n + k) / piv
            tl.store(w_ptr + i * n + k, f)
            for j in range(k + 1, n):
                tl.store(w_ptr + i * n + j,
                         tl.load(w_ptr + i * n + j) - f * tl.load(w_ptr + k * n + j))

    sign = tl.where(swaps % 2 == 0, 1.0, -1.0)
    d = sign
    for k in range(0, n):
        d = d * tl.load(w_ptr + k * n + k)
    tl.store(y_ptr, d)


# ------------------------------------------------------------------ ② case 层

DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((8,), (9,))

def ref(args, meta):
    del meta
    a = np.asarray(args["a_ptr"], dtype=np.float64)
    return {"y_ptr": np.array([float(np.linalg.det(a))], dtype=np.float32)}

def make_case(shape=None, *, dtype="float32", seed=20261008):
    if dtype is None:
        dtype = "float32"
    if np.dtype(dtype).name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype!r}; choose from {DTYPES}")
    from case_utils import fast_rng
    rng = fast_rng(seed)
    actual = SHAPES[0] if shape is None else shape
    n = actual[0]
    # A well-conditioned matrix whose determinant stays finite at the
    # benchmark size (n=128 timing shape; the case also constructs at
    # n=256): a random N(0,1) matrix has |det| ~ exp(n), which overflows
    # float32.  ``I + 0.001*N`` keeps the determinant near 1 while still
    # exercising pivoting and elimination.
    a = np.eye(n) + 0.001 * rng.standard_normal((n, n))
    # Keep the diagonal exactly 1: bf16 rounds a diagonal near 1 coarsely
    # (spacing 2^-7), which would move a determinant of a near-identity
    # matrix by several percent.  The off-diagonal perturbation still
    # exercises pivoting and elimination.
    np.fill_diagonal(a, 1.0)
    args = {'a_ptr': a.astype(np.float32), 'y_ptr': np.zeros(1, dtype=np.float32), 'w_ptr': np.zeros((n, n), dtype=np.float32), 'ptmp_ptr': np.arange(n, dtype=np.int32), 'n': n}
    expected = ref(args, {})
    tolerance = {"comparator": "allclose", "exact": False, "rtol": 2e-3, "atol": 2e-3,
                   "equal_nan": True}
    comparison = {name: ({"comparator": "array_equal", "exact": True}
                    if np.asarray(value).dtype == np.bool_ else dict(tolerance))
                  for name, value in expected.items()}
    return {
        "args": args,
        "meta": {},
        "grid": (1,),
        "outputs": tuple(expected),
        "expected": expected,
        "comparison": comparison,
        "shape": actual,
        "dtype": "float32",
        "kernel": det_kernel,
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
