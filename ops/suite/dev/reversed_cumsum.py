"""reversed_cumsum:沿 T 的逆序累积和 —— 三层结构。

① reversed_cumsum_kernel   编译单元:@triton.jit,编译器只消费它的 AST。
② reversed_cumsum(...)     执行单元:numpy in/out,零 torch。
③ SHAPES / DTYPES / make_case / ref  验证层:纯 numpy。
"""

OPERATOR = {"name": "hidden/reversed_cumsum", "group": "hidden", "channel": "G",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["reduce"]}
import numpy as np
import triton
import triton.language as tl
from case_utils import fast_rng


@triton.autotune(
    configs=[
        triton.Config({'BS': 16}, num_warps=4),
        triton.Config({'BS': 32}, num_warps=4),
        triton.Config({'BS': 64}, num_warps=4),
    ],
    key=["T","S"],
)
@triton.jit
def reversed_cumsum_kernel(s, z, s_s_h, s_s_t, s_s_d, T, S, BS: tl.constexpr):
    i_s = tl.program_id(0)
    i_bh = tl.program_id(1)
    offs = i_s * BS + tl.arange(0, BS)
    mask = offs < S
    acc = tl.zeros([BS], dtype=tl.float32)
    base = i_bh * s_s_h + offs * s_s_d
    for t in range(T - 1, -1, -1):
        acc += tl.load(s + base + t * s_s_t, mask=mask, other=0.0).to(tl.float32)
        tl.store(z + base + t * s_s_t, acc, mask=mask)


DTYPES = ('float32', 'float16', 'bfloat16')
SHAPES = ((1, 1, 8, 8), (2, 2, 9, 9), (1, 2, 16, 8))


def ref(args, meta):
    s = np.asarray(args["s"], dtype=np.float64)
    rev = np.cumsum(s[:, :, ::-1, :], axis=2)[:, :, ::-1, :]
    return {"z": rev.astype(np.asarray(args["z"]).dtype)}


def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    b, h, t, s = (int(v) for v in shape)
    rng = fast_rng(seed)
    args = {"s": rng.standard_normal((b, h, t, s)).astype(dtype),
            "z": np.zeros((b, h, t, s), dtype=dtype),
            "s_s_h": np.int32(t * s), "s_s_t": np.int32(s), "s_s_d": np.int32(1),
            "T": np.int32(t), "S": np.int32(s)}
    meta = {}
    return {"args": args, "meta": meta, "grid": lambda meta: (triton.cdiv(s, meta["BS"]), b * h),
            "outputs": ("z",), "expected": ref(args, meta)}


def reversed_cumsum(s):
    from case_utils import empty

    sf = np.asarray(s, dtype=np.float32)
    b, h, t, dim = sf.shape
    z = empty((b, h, t, dim), like=s)
    reversed_cumsum_kernel[(1, b * h)](
        sf, z, t * dim, dim, 1, t, dim, BS=dim)
    return z


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, reversed_cumsum_kernel, DTYPES,
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
