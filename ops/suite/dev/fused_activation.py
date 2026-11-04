"""fused_activation:multiplier*in + x + bias 后接激活(sigmoid/relu)—— 三层结构。

① fused_activation_kernel   编译单元:@triton.jit,编译器只消费它的 AST。
② fused_activation(...)     执行单元:numpy in/out,零 torch。
③ SHAPES / DTYPES / make_case / ref  验证层:纯 numpy。
"""

OPERATOR = {"name": "hidden/fused_activation", "group": "hidden", "channel": "G",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import numpy as np
import triton
import triton.language as tl
from case_utils import fast_rng


@triton.jit
def fused_activation_kernel(x_ptr, bias_ptr, in_ptr,
                            num_weights: tl.constexpr, xnumel: tl.constexpr,
                            multiplier: tl.constexpr, activation: tl.constexpr,
                            BLOCK_SIZE: tl.constexpr):
    xoffset = tl.program_id(0) * BLOCK_SIZE
    index = xoffset + tl.arange(0, BLOCK_SIZE)[:]
    mask = index < xnumel
    bias_index = index % num_weights
    tmp0 = tl.load(x_ptr + index, mask)
    tmp1 = tl.load(bias_ptr + bias_index, mask, eviction_policy="evict_last")
    tmp3 = tl.load(in_ptr + index, mask)
    activ_input = multiplier * tmp3 + tmp0 + tmp1
    if activation == "sigmoid":
        ma_result = tl.sigmoid(activ_input)
    else:
        ma_result = tl.maximum(0, activ_input)
    tl.store(x_ptr + index, ma_result, mask)


DTYPES = ('float32',)
SHAPES = ((128,), (99,))


def ref(args, meta):
    x = np.asarray(args["x_ptr"], dtype=np.float32)
    bias = np.asarray(args["bias_ptr"], dtype=np.float32)
    inp = np.asarray(args["in_ptr"], dtype=np.float32)
    m = float(meta["multiplier"])
    act = meta["activation"]
    v = m * inp + x + bias[np.arange(x.size) % bias.size]
    r = 1.0 / (1.0 + np.exp(-v)) if act == "sigmoid" else np.maximum(v, 0.0)
    return {"x_ptr": r.astype(np.asarray(args["x_ptr"]).dtype)}


def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    n = int(np.prod(shape))
    rng = fast_rng(seed)
    w = 8
    args = {"x_ptr": rng.standard_normal(n).astype(dtype),
            "bias_ptr": rng.standard_normal(w).astype(dtype),
            "in_ptr": rng.standard_normal(n).astype(dtype)}
    meta = {"num_weights": w, "xnumel": n, "multiplier": 0.5,
            "activation": "sigmoid", "BLOCK_SIZE": 2048}
    return {"args": args, "meta": meta, "grid": (triton.cdiv(n, 2048),),
            "outputs": ("x_ptr",), "expected": ref(args, meta)}


def fused_activation(x, bias, inp):
    from case_utils import numel

    n = numel(x)
    bs = min(2048, n)
    fused_activation_kernel[(triton.cdiv(n, bs),)](
        x, bias, inp, numel(bias), n, 0.5, "sigmoid", BLOCK_SIZE=bs)
    return x


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, fused_activation_kernel, DTYPES,
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
