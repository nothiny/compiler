"""rms_matmul_rbe:RMSNorm prologue + matmul —— 三层结构。

① rms_matmul_rbe_kernel   编译单元:@triton.jit,编译器只消费它的 AST。
② rms_matmul_rbe(...)     执行单元:numpy in/out,零 torch。
③ SHAPES / DTYPES / make_case / ref  验证层:纯 numpy。
"""

OPERATOR = {"name": "hidden/rms_matmul_rbe", "group": "hidden", "channel": "G",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["matmul"]}
import numpy as np
import triton
import triton.language as tl
from case_utils import fast_rng


@triton.jit
def rms_matmul_rbe_kernel(
    x_ptr, w_ptr, rms_w_ptr, out_ptr,
    M, N, K,
    stride_x_batch, stride_x_m, stride_x_k,
    stride_w_k, stride_w_n,
    stride_rms_w,
    stride_out_batch, stride_out_m, stride_out_n,
    start_token_position,
    USE_FP8: tl.constexpr, RBE_EPILOGUE: tl.constexpr, THETA: tl.constexpr,
    EPS: tl.constexpr,
    BLOCK_SIZE_M: tl.constexpr, BLOCK_SIZE_N: tl.constexpr, BLOCK_SIZE_K: tl.constexpr,
):
    pid_batch = tl.program_id(axis=0)
    pid = tl.program_id(axis=1)
    pid_m = pid // tl.cdiv(N, BLOCK_SIZE_N)
    pid_n = pid % tl.cdiv(N, BLOCK_SIZE_N)

    offs_m = (pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M)) % M
    offs_n = (pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N)) % N
    offs_k = tl.arange(0, BLOCK_SIZE_K)
    x_ptrs = x_ptr + (pid_batch * stride_x_batch + offs_m[:, None] * stride_x_m
                      + offs_k[None, :] * stride_x_k)
    w_ptrs = w_ptr + (offs_k[:, None] * stride_w_k + offs_n[None, :] * stride_w_n)
    accumulator = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=tl.float32)
    rms_w_ptrs = rms_w_ptr + tl.arange(0, BLOCK_SIZE_K)[None, :] * stride_rms_w
    x_sum = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_K), dtype=tl.float32)
    for _ in range(0, tl.cdiv(K, BLOCK_SIZE_K)):
        x = tl.load(x_ptrs)
        x_sum += x.to(tl.float32) * x.to(tl.float32)
        rms_w = tl.load(rms_w_ptrs)
        x = x * rms_w
        w = tl.load(w_ptrs)
        accumulator += tl.dot(x, w)
        x_ptrs += BLOCK_SIZE_K * stride_x_k
        w_ptrs += BLOCK_SIZE_K * stride_w_k
        rms_w_ptrs += BLOCK_SIZE_K * stride_rms_w
    x_mean = tl.sum(x_sum, axis=1) / K + EPS
    x_norm = tl.rsqrt(x_mean)
    accumulator = accumulator * x_norm[:, None]

    offs_m = pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M)
    offs_n = pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N)
    out_ptrs = out_ptr + (pid_batch * stride_out_batch
                          + offs_m[:, None] * stride_out_m + offs_n[None, :] * stride_out_n)
    out_mask = (offs_m[:, None] < M) & (offs_n[None, :] < N)
    tl.store(out_ptrs, accumulator, mask=out_mask)


DTYPES = ('float32', 'float16', 'bfloat16')
SHAPES = ((1, 64, 64, 64), (1, 64, 32, 64))


def ref(args, meta):
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    w = np.asarray(args["w_ptr"], dtype=np.float64)
    rw = np.asarray(args["rms_w_ptr"], dtype=np.float64)
    eps = float(args["EPS"])
    k = x.shape[-1]
    a = x * rw[None, None, :]
    acc = a @ w
    norm = 1.0 / np.sqrt((x * x).sum(axis=-1, keepdims=True) / k + eps)
    out = acc * norm
    return {"out_ptr": out.astype(np.asarray(args["out_ptr"]).dtype)}


def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    batch, m, n, k = (int(v) for v in shape)
    rng = fast_rng(seed)
    x = (rng.standard_normal((batch, m, k)) * 0.5).astype(dtype)
    w = (rng.standard_normal((k, n)) * 0.5).astype(dtype)
    rw = (rng.standard_normal(k) * 0.2 + 1.0).astype(dtype)
    args = {"x_ptr": x, "w_ptr": w, "rms_w_ptr": rw,
            "out_ptr": np.zeros((batch, m, n), dtype=dtype),
            "M": np.int32(m), "N": np.int32(n), "K": np.int32(k),
            "stride_x_batch": np.int32(m * k), "stride_x_m": np.int32(k), "stride_x_k": np.int32(1),
            "stride_w_k": np.int32(n), "stride_w_n": np.int32(1), "stride_rms_w": np.int32(1),
            "stride_out_batch": np.int32(m * n), "stride_out_m": np.int32(n), "stride_out_n": np.int32(1),
            "start_token_position": np.int32(0), "EPS": np.float32(1e-5)}
    meta = {"USE_FP8": False, "RBE_EPILOGUE": False, "THETA": 10000.0, "EPS": 1e-5,
            "BLOCK_SIZE_M": 32, "BLOCK_SIZE_N": 32, "BLOCK_SIZE_K": 32}
    grid = (batch, triton.cdiv(m, 32) * triton.cdiv(n, 32))
    expected = ref(args, meta)
    tol = {"comparator": "allclose", "exact": False, "rtol": 1e-2,
           "atol": 1e-2, "equal_nan": True}
    return {"args": args, "meta": meta, "grid": grid,
            "outputs": ("out_ptr",), "expected": expected,
            "comparison": {name: dict(tol) for name in expected}}


def rms_matmul_rbe(x, w, rms_w):
    """RMSNorm(x) @ w;numpy in/out。"""
    from case_utils import empty

    xf = np.asarray(x, dtype=np.float32)
    batch, m, k = xf.shape
    n = int(np.asarray(w).shape[1])
    out = empty((batch, m, n), like=x)
    grid = (batch, triton.cdiv(m, 32) * triton.cdiv(n, 32))
    rms_matmul_rbe_kernel[grid](
        xf, w, rms_w, out, m, n, k, m * k, k, 1, n, 1, 1, m * n, n, 1, 0,
        USE_FP8=False, RBE_EPILOGUE=False, THETA=10000.0, EPS=1e-5,
        BLOCK_SIZE_M=32, BLOCK_SIZE_N=32, BLOCK_SIZE_K=32)
    return out


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, rms_matmul_rbe_kernel, DTYPES,
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
