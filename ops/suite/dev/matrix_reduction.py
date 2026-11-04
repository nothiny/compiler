"""matrix_reduction:每行取最大值 —— 三层结构。

① load_reduce_kernel   编译单元:@triton.jit,编译器只消费它的 AST。
② load_reduce(...)     执行单元:numpy in/out,零 torch。
③ SHAPES / DTYPES / make_case / ref  验证层:纯 numpy。
"""

OPERATOR = {"name": "hidden/matrix_reduction", "group": "hidden", "channel": "G",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["reduce"]}
import numpy as np
import triton
import triton.language as tl
from case_utils import fast_rng


@triton.jit
def load_reduce_kernel(x_ptr, y_ptr, stride_xm, stride_xn, stride_y,
                       BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr):
    x_ptr = tl.make_block_ptr(base=x_ptr, shape=(BLOCK_M, BLOCK_N),
                              strides=(stride_xm, stride_xn), offsets=(0, 0),
                              block_shape=(BLOCK_M, BLOCK_N), order=(1, 0))
    x = tl.load(x_ptr)
    y = tl.max(x, axis=1)
    tl.store(y_ptr + tl.arange(0, BLOCK_M), y)


DTYPES = ('float32', 'float16', 'bfloat16')
SHAPES = ((16, 16), (8, 8))


def ref(args, meta):
    x = np.asarray(args["x_ptr"], dtype=np.float32)
    return {"y_ptr": x.max(axis=1).astype(np.asarray(args["y_ptr"]).dtype)}


def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    bm, bn = (int(v) for v in shape)
    rng = fast_rng(seed)
    args = {"x_ptr": rng.standard_normal((bm, bn)).astype(dtype),
            "y_ptr": np.zeros(bm, dtype=dtype),
            "stride_xm": np.int32(bn), "stride_xn": np.int32(1), "stride_y": np.int32(1)}
    meta = {"BLOCK_M": bm, "BLOCK_N": bn}
    return {"args": args, "meta": meta, "grid": (1,),
            "outputs": ("y_ptr",), "expected": ref(args, meta)}


def load_reduce(x):
    from case_utils import empty

    xf = np.asarray(x, dtype=np.float32)
    bm, bn = xf.shape
    y = empty((bm,), like=x)
    load_reduce_kernel[(1,)](xf, y, bn, 1, 1, BLOCK_M=bm, BLOCK_N=bn)
    return y


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, load_reduce_kernel, DTYPES,
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
