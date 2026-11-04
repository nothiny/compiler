"""rope_embedding: bench 算子(原始 tritonbench 实现),自 tritonbench 收入 medium 组。
模式: creation.arange、memory.store、memory.load、args.runtime_scalar。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""

OPERATOR = {"name": "medium/rope_embedding", "group": "medium", "channel": "local", "execution": "triton_kernel", "verification": "correctness", "tags": ["creation.arange", "memory.store", "memory.load", "args.runtime_scalar"]}
COPIED_FROM = {"repo": "tritonbench @ ops", "path": "tritonbench/rope_embedding.py", "validated": True}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def rope_kernel(x_ptr, cos_ptr, sin_ptr, out_ptr, T, D: tl.constexpr, HALF: tl.constexpr):
    row = tl.program_id(0)
    half = tl.arange(0, HALF)
    x1 = tl.load(x_ptr + row * D + 2 * half).to(tl.float32)
    x2 = tl.load(x_ptr + row * D + 2 * half + 1).to(tl.float32)
    c = tl.load(cos_ptr + row * HALF + half).to(tl.float32)
    s = tl.load(sin_ptr + row * HALF + half).to(tl.float32)
    tl.store(out_ptr + row * D + 2 * half, x1 * c - x2 * s)
    tl.store(out_ptr + row * D + 2 * half + 1, x1 * s + x2 * c)


# ------------------------------------------------------------------ ② case 层
DTYPES = ('float32', 'float16', 'bfloat16')

SHAPES = ((8, 16), (8, 32))

def ref(args, meta):
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    c = np.asarray(args["cos_ptr"], dtype=np.float64)
    s = np.asarray(args["sin_ptr"], dtype=np.float64)
    x1 = x[:, 0::2]
    x2 = x[:, 1::2]
    out = np.empty_like(x)
    out[:, 0::2] = x1 * c - x2 * s
    out[:, 1::2] = x1 * s + x2 * c
    return {"out_ptr": out.astype(np.asarray(args["out_ptr"]).dtype)}

def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    t, d = (int(x) for x in shape)
    from case_utils import fast_rng
    rng = fast_rng(seed)
    half = d // 2
    ang = rng.standard_normal((t, half)).astype(np.float32)
    args = {"x_ptr": rng.standard_normal((t, d)).astype(dtype),
            "cos_ptr": np.cos(ang).astype(dtype), "sin_ptr": np.sin(ang).astype(dtype),
            "out_ptr": np.zeros((t, d), dtype=dtype), "T": np.int32(t)}
    meta = {"D": d, "HALF": half}
    return {"args": args, "meta": meta, "grid": (t,),
            "outputs": ("out_ptr",), "expected": ref(args, meta)}

def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, rope_kernel, DTYPES,
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
