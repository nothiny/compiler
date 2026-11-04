"""swiglu_fwd: bench 算子(原始 tritonbench 实现),自 tritonbench 收入 medium 组。
模式: memory.store.masked、creation.arange、memory.load.masked、math.sigmoid、args.runtime_scalar。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""

OPERATOR = {"name": "medium/swiglu_fwd", "group": "medium", "channel": "local", "execution": "triton_kernel", "verification": "correctness", "tags": ["memory.store.masked", "creation.arange", "memory.load.masked", "math.sigmoid", "args.runtime_scalar"]}
COPIED_FROM = {"repo": "tritonbench @ ops", "path": "tritonbench/swiglu_fwd.py", "validated": True}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.autotune(
    configs=[
        triton.Config({'BLOCK_N': 32}, num_warps=4),
        triton.Config({'BLOCK_N': 64}, num_warps=4),
        triton.Config({'BLOCK_N': 128}, num_warps=4),
    ],
    key=["ncols"],
)
@triton.jit
def swiglu_fwd_kernel(X, Y, OUT, stride_x_row, stride_y_row, stride_out_row, ncols,
                      BLOCK_N: tl.constexpr):
    row = tl.program_id(0)
    start_col = tl.program_id(1) * BLOCK_N
    cols = start_col + tl.arange(0, BLOCK_N)
    mask = cols < ncols
    x = tl.load(X + row * stride_x_row + cols, mask=mask, other=0.0).to(tl.float32)
    y = tl.load(Y + row * stride_y_row + cols, mask=mask, other=0.0).to(tl.float32)
    tl.store(OUT + row * stride_out_row + cols, x * tl.sigmoid(x) * y, mask=mask)


# ------------------------------------------------------------------ ② case 层
DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((4, 64), (8, 128))

def ref(args, meta):
    x = np.asarray(args["X"], dtype=np.float64)
    y = np.asarray(args["Y"], dtype=np.float64)
    silu = x / (1.0 + np.exp(-x))
    return {"OUT": (silu * y).astype(np.asarray(args["OUT"]).dtype)}

def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    r, c = (int(v) for v in shape)
    from case_utils import fast_rng
    rng = fast_rng(seed)
    args = {"X": rng.standard_normal((r, c)).astype(dtype),
            "Y": rng.standard_normal((r, c)).astype(dtype),
            "OUT": np.zeros((r, c), dtype=dtype),
            "stride_x_row": np.int32(c), "stride_y_row": np.int32(c),
            "stride_out_row": np.int32(c), "ncols": np.int32(c)}
    meta = {}
    return {"args": args, "meta": meta, "grid": lambda meta: (r, triton.cdiv(c, meta["BLOCK_N"])),
            "outputs": ("OUT",), "expected": ref(args, meta)}

def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, swiglu_fwd_kernel, DTYPES,
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
