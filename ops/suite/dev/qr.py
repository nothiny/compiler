"""qr: bench 算子(原始 tritonbench 实现),自 tritonbench 收入 hard 组。
模式: creation.arange、memory.load.masked、creation.where、math.minimum、memory.store.masked、reduce.sum。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {"name": "hard/qr", "group": "hard", "channel": "local", "execution": "triton_kernel", "verification": "correctness", "tags": ["creation.arange", "memory.load.masked", "creation.where", "math.minimum", "memory.store.masked", "reduce.sum", "math.sqrt", "control.for_range"]}
COPIED_FROM = {"repo": "tritonbench @ ops", "path": "tritonbench/qr.py", "validated": True}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def qr_kernel(a_ptr, q_ptr, r_ptr, M, N, BLOCK: tl.constexpr):
    rows = tl.arange(0, BLOCK)
    cols = tl.arange(0, BLOCK)
    rmask = (rows[:, None] < M) & (cols[None, :] < N)
    R = tl.load(a_ptr + rows[:, None] * N + cols[None, :], mask=rmask, other=0.0)
    Q = tl.where(rows[:, None] == cols[None, :], 1.0, 0.0)
    mn = tl.minimum(M, N)
    for k in range(0, mn):
        if (M - k) > 1:
            colk = tl.sum(tl.where(cols[None, :] == k, R, 0.0), axis=1)
            xk = tl.where(rows >= k, colk, 0.0)
            nrm = tl.sqrt(tl.sum(xk * xk, axis=0))
            x0 = tl.sum(tl.where(rows == k, colk, 0.0), axis=0)
            s = tl.where(x0 > 0, 1.0, tl.where(x0 < 0, -1.0, 1.0))
            alpha = -s * nrm
            v = tl.where(rows == k, xk - alpha, xk)
            vn2 = tl.sum(v * v, axis=0)
            vn2 = tl.where(vn2 > 1e-30, vn2, 1.0)
            proj = tl.sum(v[:, None] * R, axis=0)
            R = R - 2.0 * v[:, None] * proj[None, :] / vn2
            qv = tl.sum(Q * v[None, :], axis=1)
            Q = Q - 2.0 * qv[:, None] * v[None, :] / vn2
    tl.store(q_ptr + rows[:, None] * N + cols[None, :], Q,
             mask=(rows[:, None] < M) & (cols[None, :] < N))
    tl.store(r_ptr + rows[:, None] * N + cols[None, :], R,
             mask=(rows[:, None] < N) & (cols[None, :] < N))


# ------------------------------------------------------------------ ② case 层

DTYPES = ('float32',)

SHAPES = ((6, 4), (12, 8))

def ref(args, meta):
    del meta
    a = np.asarray(args["a_ptr"], dtype=np.float64)
    q, r = np.linalg.qr(a, mode="reduced")
    return {"q_ptr": q.astype(np.float32), "r_ptr": r.astype(np.float32)}

def make_case(shape=None, *, dtype="float32", seed=20261008):
    if dtype is None:
        dtype = "float32"
    if np.dtype(dtype).name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype!r}; choose from {DTYPES}")
    from case_utils import fast_rng
    rng = fast_rng(seed)
    actual = SHAPES[0] if shape is None else shape
    m, n = actual
    if m < n:
        raise ValueError("qr reduced case requires m >= n")
    a = rng.standard_normal((m, n)) * 0.5
    args = {'a_ptr': a.astype(np.float32), 'q_ptr': np.zeros((m, n), dtype=np.float32),
            'r_ptr': np.zeros((n, n), dtype=np.float32), 'M': m, 'N': n}
    expected = ref(args, {})
    tolerance = {"comparator": "allclose", "exact": False, "rtol": 2e-3, "atol": 2e-3,
                 "equal_nan": True}
    comparison = {name: dict(tolerance) for name in expected}
    return {
        "args": args,
        "meta": {"BLOCK": 16},
        "grid": (1,),
        "outputs": tuple(expected),
        "expected": expected,
        "comparison": comparison,
        "shape": actual,
        "dtype": "float32",
        "kernel": qr_kernel,
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
