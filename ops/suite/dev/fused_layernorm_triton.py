"""fused_layernorm_triton:逐行 LayerNorm —— 三层结构。

① layernorm_kernel   编译单元:@triton.jit,编译器只消费它的 AST。
② 执行单元:numpy in/out,零 torch。
③ SHAPES / DTYPES / make_case / ref  验证层:纯 numpy。
"""

OPERATOR = {"name": "hidden/fused_layernorm_triton", "group": "hidden", "channel": "G",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["norm"]}
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
    key=["N"],
)
@triton.jit
def layernorm_kernel(X, Y, W, B, Mean, Rstd, stride, N, eps, BLOCK: tl.constexpr):
    row = tl.program_id(0)
    X += row * stride
    Y += row * stride
    cols = tl.arange(0, BLOCK)
    mask = cols < N
    x = tl.load(X + cols, mask=mask, other=0.0).to(tl.float32)
    mean = tl.sum(x, axis=0) / N
    xc = tl.where(mask, x - mean, 0.0)
    var = tl.sum(xc * xc, axis=0) / N
    rstd = 1.0 / tl.sqrt(var + eps)
    tl.store(Mean + row, mean)
    tl.store(Rstd + row, rstd)
    w = tl.load(W + cols, mask=mask, other=0.0).to(tl.float32)
    b = tl.load(B + cols, mask=mask, other=0.0).to(tl.float32)
    tl.store(Y + cols, xc * rstd * w + b, mask=mask)


DTYPES = ('float32', 'float16', 'bfloat16')
SHAPES = ((4, 64), (7, 67))


def ref(args, meta):
    x = np.asarray(args["X"], dtype=np.float64)
    w = np.asarray(args["W"], dtype=np.float64)
    b = np.asarray(args["B"], dtype=np.float64)
    eps = float(args["eps"])
    mean = x.mean(axis=1)
    var = x.var(axis=1)
    rstd = 1.0 / np.sqrt(var + eps)
    y = (x - mean[:, None]) * rstd[:, None] * w[None, :] + b[None, :]
    return {"Y": y.astype(np.asarray(args["Y"]).dtype),
            "Mean": mean.astype(np.asarray(args["Mean"]).dtype),
            "Rstd": rstd.astype(np.asarray(args["Rstd"]).dtype)}


def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    r, c = (int(v) for v in shape)
    rng = fast_rng(seed)
    args = {"X": rng.standard_normal((r, c)).astype(dtype),
            "Y": np.zeros((r, c), dtype=dtype),
            "W": (rng.standard_normal(c) * 0.5 + 1.0).astype(dtype),
            "B": (rng.standard_normal(c) * 0.1).astype(dtype),
            "Mean": np.zeros(r, dtype=dtype), "Rstd": np.zeros(r, dtype=dtype),
            "stride": np.int32(c), "N": np.int32(c), "eps": np.float32(1e-5)}
    meta = {}
    return {"args": args, "meta": meta, "grid": (r,),
            "outputs": ("Y", "Mean", "Rstd"), "expected": ref(args, meta)}


def layernorm(x, weight, bias, eps=1e-5):
    from case_utils import empty_like, empty

    xf = np.asarray(x, dtype=np.float32)
    r, c = xf.shape
    y = empty_like(x)
    mean = empty((r,), like=x)
    rstd = empty((r,), like=x)
    layernorm_kernel[(r,)](xf, y, weight, bias, mean, rstd, c, c, float(eps),
                           BLOCK=triton.next_power_of_2(c))
    return y


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, layernorm_kernel, DTYPES,
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
