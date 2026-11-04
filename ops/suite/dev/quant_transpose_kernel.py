"""quant_transpose_kernel:global absmax 量化并转置写回 int8 —— 三层结构。

① quantize_global_transpose_kernel   编译单元:@triton.jit,编译器只消费它的 AST。
② quantize_global_transpose(...)     执行单元:numpy in/out,零 torch。
③ SHAPES / DTYPES / make_case / ref  验证层:纯 numpy。
"""

OPERATOR = {"name": "hidden/quant_transpose_kernel", "group": "hidden", "channel": "G",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["quant"]}
import numpy as np
import triton
import triton.language as tl
from case_utils import fast_rng


@triton.autotune(
    configs=[
        triton.Config({'BLOCK_M': 32, 'BLOCK_N': 32, 'GROUP_M': 8}, num_warps=4),
        triton.Config({'BLOCK_M': 64, 'BLOCK_N': 64, 'GROUP_M': 8}, num_warps=4),
    ],
    key=["M","N"],
)
@triton.jit
def quantize_global_transpose_kernel(
    A, absmax_inv_ptr, B,
    stride_am, stride_an, stride_bn, stride_bm,
    M, N,
    BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, GROUP_M: tl.constexpr,
):
    pid = tl.program_id(0)
    grid_m = (M + BLOCK_M - 1) // BLOCK_M
    grid_n = (N + BLOCK_N - 1) // BLOCK_N

    width = GROUP_M * grid_n
    group_id = pid // width
    group_size = min(grid_m - group_id * GROUP_M, GROUP_M)
    pid_m = group_id * GROUP_M + (pid % group_size)
    pid_n = (pid % width) // group_size

    rm = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    rn = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    A = A + (rm[:, None] * stride_am + rn[None, :] * stride_an)
    mask = (rm < M)[:, None] & (rn < N)[None, :]
    a = tl.load(A, mask=mask).to(tl.float32)
    absmax_inv = tl.load(absmax_inv_ptr).to(tl.float32)

    rm = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    rn = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    B = B + (rm[:, None] * stride_bm + rn[None, :] * stride_bn)
    mask = (rm < M)[:, None] & (rn < N)[None, :]

    _v = 127.0 * (a * absmax_inv)
    _r = tl.floor(_v)
    _d = _v - _r
    _odd = tl.abs(_r - 2.0 * tl.floor(_r * 0.5)) > 0.5
    output = tl.where((_d > 0.5) | ((_d == 0.5) & _odd), _r + 1.0, _r).to(tl.int8)
    tl.store(B, output, mask=mask)


DTYPES = ('float32', 'float16', 'bfloat16')
SHAPES = ((128, 128), (99, 99))


def _round_half_even(v):
    v = np.asarray(v, dtype=np.float32)
    r = np.floor(v).astype(np.float32)
    d = (v - r).astype(np.float32)
    odd = np.abs(r - (np.float32(2.0) * np.floor(
        (r * np.float32(0.5)).astype(np.float32))).astype(np.float32)) > np.float32(0.5)
    return np.where((d > np.float32(0.5)) | ((d == np.float32(0.5)) & odd),
                    (r + np.float32(1.0)).astype(np.float32), r)


def ref(args, meta):
    a = np.asarray(args["A"], dtype=np.float32)
    inv = np.asarray(args["absmax_inv_ptr"], dtype=np.float32).reshape(-1)[0]
    q = _round_half_even(np.float32(127.0) * (a * inv)).astype(args["B"].dtype)
    return {"B": np.ascontiguousarray(q.T)}


def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    shape = tuple(int(value) for value in shape)
    m, n = shape
    rng = fast_rng(seed)
    a = (rng.standard_normal((m, n)) * 0.5).astype(np.float32)
    absmax = np.float32(np.max(np.abs(a)))
    absmax_inv = np.array([np.float32(1.0) / absmax], dtype=np.float32)
    args = {"A": a, "absmax_inv_ptr": absmax_inv,
            "B": np.zeros((n, m), dtype=np.int8),
            "stride_am": n, "stride_an": 1, "stride_bn": m, "stride_bm": 1,
            "M": m, "N": n}
    meta = {}
    grid = (triton.cdiv(m, 64) * triton.cdiv(n, 64),)
    return {"args": args, "meta": meta, "grid": lambda meta: (triton.cdiv(m, meta["BLOCK_M"]) * triton.cdiv(n, meta["BLOCK_N"]),),
            "outputs": ("B",), "expected": ref(args, meta)}


def quantize_global_transpose(x):
    """global absmax 量化 + 转置写回;numpy in/out。"""
    from case_utils import empty

    xf = np.asarray(x, dtype=np.float32)
    m, n = int(xf.shape[0]), int(xf.shape[1])
    absmax = np.float32(np.max(np.abs(xf)))
    absmax_inv = np.array([np.float32(1.0) / absmax], dtype=np.float32)
    out = empty((n, m), like=xf, dtype="int8")
    grid = (triton.cdiv(m, 64) * triton.cdiv(n, 64),)
    quantize_global_transpose_kernel[grid](
        xf, absmax_inv, out, n, 1, m, 1, m, n,
        BLOCK_M=64, BLOCK_N=64, GROUP_M=8)
    return out


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, quantize_global_transpose_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=True)


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
