"""int8_quantization:按块 int8 量化 —— 三层结构。

① q_kernel_per_block_int8   编译单元:@triton.jit,编译器只消费它的 AST。
② 执行单元:numpy in/out,零 torch。
③ SHAPES / DTYPES / make_case / ref  验证层:纯 numpy。
"""

OPERATOR = {"name": "hidden/int8_quantization", "group": "hidden", "channel": "G",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["quant"]}
import numpy as np
import triton
import triton.language as tl
from case_utils import fast_rng


@triton.jit
def q_kernel_per_block_int8(X, X_int8, Scale, L, C: tl.constexpr,
                            BLOCK: tl.constexpr):
    off_blk = tl.program_id(0)
    offs_m = off_blk * BLOCK + tl.arange(0, BLOCK)
    offs_k = tl.arange(0, C)
    mask = offs_m[:, None] < L
    x = tl.load(X + offs_m[:, None] * C + offs_k[None, :], mask=mask, other=0.0).to(tl.float32)
    x = x * (C ** -0.5 * 1.44269504)
    scale = tl.max(tl.abs(x)) / 127.0
    q = tl.where(x >= 0, x / scale + 0.5, x / scale - 0.5)
    tl.store(X_int8 + offs_m[:, None] * C + offs_k[None, :], q.to(tl.int8), mask=mask)
    tl.store(Scale + off_blk, scale)


DTYPES = ('float32', 'float16', 'bfloat16')
SHAPES = ((8, 16), (4, 8))


def ref(args, meta):
    x = np.asarray(args["X"], dtype=np.float64)
    c = x.shape[1]
    x = x * (c ** -0.5 * 1.44269504)
    scale = np.abs(x).max() / 127.0
    q = np.where(x / scale >= 0, x / scale + 0.5, x / scale - 0.5)
    return {"X_int8": q.astype(np.asarray(args["X_int8"]).dtype),
            "Scale": np.array([scale], dtype=np.asarray(args["Scale"]).dtype)}


def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    l, c = (int(v) for v in shape)
    rng = fast_rng(seed)
    args = {"X": rng.standard_normal((l, c)).astype(dtype),
            "X_int8": np.zeros((l, c), dtype=np.int8), "Scale": np.zeros(1, dtype=dtype),
            "L": np.int32(l), "C": np.int32(c)}
    meta = {"BLOCK": triton.next_power_of_2(l)}
    return {"args": args, "meta": meta, "grid": (1,),
            "outputs": ("X_int8", "Scale"), "expected": ref(args, meta)}


def quantize_block(x):
    from case_utils import empty

    xf = np.asarray(x, dtype=np.float32)
    l, c = xf.shape
    q = empty((l, c), like=x, dtype="int8")
    s = empty((1,), like=x)
    q_kernel_per_block_int8[(1,)](xf, q, s, l, c, BLOCK=triton.next_power_of_2(l))
    return q, s


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, q_kernel_per_block_int8, DTYPES,
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
