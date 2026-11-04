"""triton_argmax:数组全局 argmax(单 program)—— 三层结构。

① argmax_kernel   编译单元:@triton.jit,编译器只消费它的 AST。
② argmax(...)     执行单元:numpy in/out,零 torch。
③ SHAPES / DTYPES / make_case / ref  验证层:纯 numpy。
"""

OPERATOR = {"name": "hidden/triton_argmax", "group": "hidden", "channel": "G",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["reduce"]}
import numpy as np
import triton
import triton.language as tl
from case_utils import fast_rng


@triton.jit
def argmax_kernel(inp, out, M, BLOCK_SIZE: tl.constexpr):
    idx = tl.arange(0, BLOCK_SIZE)
    v = tl.load(inp + idx, mask=idx < M, other=float("-inf")).to(tl.float32)
    i = tl.argmax(v, axis=0, tie_break_left=True)
    tl.store(out, i)


DTYPES = ('float32', 'float16', 'bfloat16')
SHAPES = ((128,), (127,))


def ref(args, meta):
    x = np.asarray(args["inp"], dtype=np.float32)
    return {"out": np.array([np.argmax(x)], dtype=np.asarray(args["out"]).dtype)}


def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    n = int(np.prod(shape))
    rng = fast_rng(seed)
    args = {"inp": rng.standard_normal(n).astype(dtype), "out": np.zeros(1, dtype=np.int32),
            "M": np.int32(n)}
    meta = {"BLOCK_SIZE": triton.next_power_of_2(n)}
    return {"args": args, "meta": meta, "grid": (1,),
            "outputs": ("out",), "expected": ref(args, meta)}


def argmax(x):
    from case_utils import empty, numel

    xf = np.asarray(x, dtype=np.float32)
    n = numel(xf)
    out = empty((1,), like=x, dtype="int32")
    argmax_kernel[(1,)](xf, out, n, BLOCK_SIZE=triton.next_power_of_2(n))
    return out


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, argmax_kernel, DTYPES,
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
