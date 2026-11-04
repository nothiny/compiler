"""fused_layer_norm_relu_linear: matmul(compute 类)。
bench 稳态配置见 bench/workload.json(声明 shape [4, 5],验证 shape [256, 5]);正确性 shape 见下方 SHAPES。
模式: creation.arange、memory.load.masked、creation.where、memory.store.masked、reduce.sum、math.maximum。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/fused_layer_norm_relu_linear', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'memory.load.masked', 'creation.where', 'memory.store.masked', 'reduce.sum', 'math.maximum', 'math.sqrt', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/fused_layer_norm_relu_linear.py', 'sha256': '1a87db64b80a4702db28a4c9e1dad6e64333cf9c39e3093d841eb52cdee46f68'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def fused_layer_norm_relu_linear_kernel(x_ptr, w_ptr, b_ptr, y_ptr,
                                        IN, OUT, EPS,
                                        BI: tl.constexpr, BO: tl.constexpr):
    r = tl.program_id(0)
    cin = tl.arange(0, BI)
    cin_mask = cin < IN
    x = tl.load(x_ptr + r * IN + cin, mask=cin_mask, other=0.0)
    cout = tl.arange(0, BO)
    cout_mask = cout < OUT
    w = tl.load(w_ptr + cout[:, None] * IN + cin[None, :],
                mask=cout_mask[:, None] & cin_mask[None, :], other=0.0)
    b = tl.load(b_ptr + cout, mask=cout_mask, other=0.0)
    lin = tl.sum(w * x[None, :], axis=1) + b
    lin = tl.where(cout_mask, tl.maximum(lin, 0.0), 0.0)
    mean = tl.sum(lin, axis=0) / OUT
    dev = tl.where(cout_mask, lin - mean, 0.0)
    var = tl.sum(dev * dev, axis=0) / OUT
    z = (lin - mean) / tl.sqrt(var + EPS)
    tl.store(y_ptr + r * OUT + cout, z, mask=cout_mask)


# ------------------------------------------------------------------ ② case 层

DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((4, 5), (5, 6))

def ref(args, meta):
    del meta
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    w = np.asarray(args["w_ptr"], dtype=np.float64)
    b = np.asarray(args["b_ptr"], dtype=np.float64)
    eps = float(args["EPS"])
    lin = np.maximum(x @ w.T + b[None, :], 0.0)
    mean = lin.mean(axis=1, keepdims=True)
    var = lin.var(axis=1, keepdims=True)
    return {"y_ptr": ((lin - mean) / np.sqrt(var + eps)).astype(np.float32)}

def make_case(shape=None, *, dtype="float32", seed=20261008):
    if dtype is None:
        dtype = "float32"
    if np.dtype(dtype).name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype!r}; choose from {DTYPES}")
    from case_utils import fast_rng
    rng = fast_rng(seed)
    actual = SHAPES[0] if shape is None else shape
    rows, in_features = actual
    out_features = 3
    x = rng.standard_normal((rows, in_features)) * 0.5
    weight = rng.standard_normal((out_features, in_features)) * 0.5
    bias = rng.standard_normal(out_features) * 0.1
    eps = 1e-5
    args = {'x_ptr': x.astype(np.float32), 'w_ptr': weight.astype(np.float32),
            'b_ptr': bias.astype(np.float32),
            'y_ptr': np.zeros((rows, out_features), dtype=np.float32),
            'IN': in_features, 'OUT': out_features, 'EPS': eps}
    expected = ref(args, {})
    tolerance = {"comparator": "allclose", "exact": False, "rtol": 2e-3, "atol": 2e-3,
                 "equal_nan": True}
    comparison = {name: dict(tolerance) for name in expected}
    return {
        "args": args,
        "meta": {"BI": 32, "BO": 32},
        "grid": (rows,),
        "outputs": tuple(expected),
        "expected": expected,
        "comparison": comparison,
        "shape": actual,
        "dtype": "float32",
        "kernel": fused_layer_norm_relu_linear_kernel,
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
