"""fast_rms_layernorm: norm(reduction 类)。
bench 稳态配置见 bench/workload.json(声明 shape [4, 64],验证 shape [64, 1024]);正确性 shape 见下方 SHAPES。
模式: creation.arange、math.rsqrt、memory.store、memory.store.masked、reduce.sum、memory.load.masked。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""

OPERATOR = {'name': 'bench/fast_rms_layernorm', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'math.rsqrt', 'memory.store', 'memory.store.masked', 'reduce.sum', 'memory.load.masked', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/fast_rms_layernorm.py', 'sha256': 'df23912d53644b550e42771c4b2a3afa55a598c30abe71742eee77fb489aed17'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def rms_layernorm_forward_kernel(
    Y, Y_row_stride,
    X, X_row_stride,
    W, W_row_stride,
    r, r_row_stride,
    n_cols, eps,
    BLOCK_SIZE: tl.constexpr,
):
    row_idx = tl.program_id(0)
    col_offsets = tl.arange(0, BLOCK_SIZE)
    mask = col_offsets < n_cols

    Y += row_idx * Y_row_stride
    X += row_idx * X_row_stride
    r += row_idx * r_row_stride

    X_row = tl.load(X + col_offsets, mask=mask, other=0.0).to(tl.float32)
    W_row = tl.load(W + col_offsets, mask=mask, other=0.0).to(tl.float32)

    row_var = tl.sum(X_row * X_row, axis=0) / n_cols
    inv_var = tl.rsqrt(row_var + eps)
    tl.store(r, inv_var)
    normed = X_row * inv_var
    output = normed * W_row
    tl.store(Y + col_offsets, output, mask=mask)


# ------------------------------------------------------------------ ② case 层
DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((4, 64), (7, 67))

def ref(args, meta):
    x = np.asarray(args["X"], dtype=np.float64)
    w = np.asarray(args["W"], dtype=np.float64)
    eps = float(args["eps"])
    n_rows, n_cols = x.shape
    var = (x * x).sum(axis=1, keepdims=True) / n_cols
    inv = 1.0 / np.sqrt(var + eps)
    y = (x * inv) * w[None, :]
    return {"Y": y.astype(np.asarray(args["Y"]).dtype),
            "r": inv.reshape(-1).astype(np.asarray(args["r"]).dtype)}

def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    shape = tuple(int(value) for value in shape)
    n_rows, n_cols = shape
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (rng.standard_normal((n_rows, n_cols)) * 0.5).astype(dtype)
    w = (rng.standard_normal(n_cols) * 0.5 + 1.0).astype(dtype)
    args = {"Y": np.zeros((n_rows, n_cols), dtype=dtype), "Y_row_stride": np.int32(n_cols),
            "X": x, "X_row_stride": np.int32(n_cols),
            "W": w, "W_row_stride": np.int32(1),
            "r": np.zeros(n_rows, dtype=dtype), "r_row_stride": np.int32(1),
            "n_cols": np.int32(n_cols), "eps": np.float32(1e-5)}
    meta = {"BLOCK_SIZE": triton.next_power_of_2(n_cols)}
    return {"args": args, "meta": meta, "grid": (n_rows,),
            "outputs": ("Y", "r"), "expected": ref(args, meta)}

def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, rms_layernorm_forward_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)

ORACLE_KIND = "numpy_reference"

INDEPENDENT_ORACLE = True

EXECUTION_KIND = "triton_kernel"

VERIFICATION_KIND = "correctness"

OPERATOR_NAME = "G/" + __file__.rsplit("/", 1)[-1]

OPERATOR_FILE = __file__


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
