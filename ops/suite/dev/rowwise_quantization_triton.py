"""rowwise_quantization_triton:按行 int8 量化(半偶舍入) —— 三层结构。

① quantize_rowwise_kernel   编译单元:@triton.jit,编译器只消费它的 AST。
② 执行单元:numpy in/out,零 torch。
③ SHAPES / DTYPES / make_case / ref  验证层:纯 numpy。
"""

OPERATOR = {"name": "hidden/rowwise_quantization_triton", "group": "hidden", "channel": "G",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["quant"]}
import numpy as np
import triton
import triton.language as tl
from case_utils import fast_rng


@triton.autotune(
    configs=[
        triton.Config({'BLOCK': 128}, num_warps=4),
        triton.Config({'BLOCK': 256}, num_warps=4),
        triton.Config({'BLOCK': 512}, num_warps=4),
        triton.Config({'BLOCK': 1024}, num_warps=4),
    ],
    key=["n_cols"],
)
@triton.jit
def quantize_rowwise_kernel(x_ptr, output_ptr, output_maxs, n_cols, BLOCK: tl.constexpr):
    row = tl.program_id(0)
    offs = tl.arange(0, BLOCK)
    mask = offs < n_cols
    x = tl.load(x_ptr + row * n_cols + offs, mask=mask, other=0.0).to(tl.float32)
    max_val = tl.max(tl.where(mask, tl.abs(x), 0.0), axis=0)
    v = 127.0 * (x / max_val)
    r = tl.floor(v)
    d = v - r
    odd = tl.abs(r - 2.0 * tl.floor(r * 0.5)) > 0.5
    q = tl.where((d > 0.5) | ((d == 0.5) & odd), r + 1.0, r).to(tl.int8)
    tl.store(output_ptr + row * n_cols + offs, q, mask=mask)
    tl.store(output_maxs + row, max_val)


DTYPES = ('float32', 'float16', 'bfloat16')
SHAPES = ((4, 8), (7, 11))


def ref(args, meta):
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    max_val = np.abs(x).max(axis=1)
    v = (127.0 * (x / max_val[:, None])).astype(np.float32)
    r = np.floor(v).astype(np.float32)
    d = (v - r).astype(np.float32)
    odd = np.abs(r - (np.float32(2.0) * np.floor((r * np.float32(0.5)).astype(np.float32))).astype(np.float32)) > np.float32(0.5)
    q = np.where((d > np.float32(0.5)) | ((d == np.float32(0.5)) & odd), (r + np.float32(1.0)).astype(np.float32), r)
    return {"output_ptr": q.astype(np.asarray(args["output_ptr"]).dtype),
            "output_maxs": max_val.astype(np.asarray(args["output_maxs"]).dtype)}


def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    r, c = (int(v) for v in shape)
    rng = fast_rng(seed)
    args = {"x_ptr": rng.standard_normal((r, c)).astype(dtype),
            "output_ptr": np.zeros((r, c), dtype=np.int8),
            "output_maxs": np.zeros(r, dtype=dtype), "n_cols": np.int32(c)}
    meta = {}
    return {"args": args, "meta": meta, "grid": (r,),
            "outputs": ("output_ptr", "output_maxs"), "expected": ref(args, meta)}


def quantize_rowwise(x):
    from case_utils import empty

    xf = np.asarray(x, dtype=np.float32)
    r, c = xf.shape
    q = empty((r, c), like=x, dtype="int8")
    m = empty((r,), like=x)
    quantize_rowwise_kernel[(r,)](xf, q, m, c, BLOCK=triton.next_power_of_2(c))
    return q, m


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, quantize_rowwise_kernel, DTYPES,
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
