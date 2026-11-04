"""matrix_transpose:矩阵转置 —— 三层结构。

① matrix_transpose_kernel   编译单元:@triton.jit,编译器只消费它的 AST。
② matrix_transpose(...)     执行单元:numpy in/out,零 torch。
③ SHAPES / DTYPES / make_case / ref  验证层:纯 numpy。
"""

OPERATOR = {"name": "hidden/matrix_transpose", "group": "hidden", "channel": "G",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["layout"]}
import numpy as np
import triton
import triton.language as tl
from case_utils import fast_rng


@triton.jit
def matrix_transpose_kernel(M, Out, matrix_stridex, matrix_stridey,
                            out_stridex, out_stridey,
                            SIZE_M: tl.constexpr, D_HEAD: tl.constexpr):
    m = tl.arange(0, SIZE_M)
    d = tl.arange(0, D_HEAD)
    matrix_ptr = M + d[None, :] * matrix_stridey + m[:, None] * matrix_stridex
    out_ptr = Out + d[None, :] * out_stridex + m[:, None] * out_stridey
    tl.store(out_ptr, tl.load(matrix_ptr))


DTYPES = ('float32', 'float16', 'bfloat16')
SHAPES = ((16, 16), (8, 8))


def ref(args, meta):
    m = np.asarray(args["M"], dtype=np.float32)
    return {"Out": np.ascontiguousarray(m.T).astype(np.asarray(args["Out"]).dtype)}


def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    sm, dh = (int(v) for v in shape)
    rng = fast_rng(seed)
    args = {"M": rng.standard_normal((sm, dh)).astype(dtype),
            "Out": np.zeros((dh, sm), dtype=dtype),
            "matrix_stridex": np.int32(dh), "matrix_stridey": np.int32(1),
            "out_stridex": np.int32(sm), "out_stridey": np.int32(1)}
    meta = {"SIZE_M": sm, "D_HEAD": dh}
    return {"args": args, "meta": meta, "grid": (1,),
            "outputs": ("Out",), "expected": ref(args, meta)}


def matrix_transpose(m):
    from case_utils import empty

    mf = np.asarray(m, dtype=np.float32)
    sm, dh = mf.shape
    out = empty((dh, sm), like=m)
    matrix_transpose_kernel[(1,)](mf, out, dh, 1, sm, 1, SIZE_M=sm, D_HEAD=dh)
    return out


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, matrix_transpose_kernel, DTYPES,
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
