"""destindex_copy: layout(memory 类)bench 算子,自 tritonbench 收入 medium 组。
bench 稳态配置见 ~/ops/bench/workload.json(声明 shape [8, 16],验证 shape [16384, 16]);正确性 shape 见下方 SHAPES。
模式: creation.arange、memory.load、memory.store、args.runtime_scalar。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""

OPERATOR = {"name": "medium/destindex_copy", "group": "medium", "channel": "local", "execution": "triton_kernel", "verification": "correctness", "tags": ["creation.arange", "memory.load", "memory.store", "args.runtime_scalar"]}
COPIED_FROM = {"repo": "tritonbench @ ops", "path": "tritonbench/destindex_copy.py", "validated": True}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def destindex_copy_kernel(src, dest_loc, out, stride_src, stride_out, D: tl.constexpr):
    row = tl.program_id(0)
    offs = tl.arange(0, D)
    v = tl.load(src + row * stride_src + offs)
    d = tl.load(dest_loc + row)
    tl.store(out + d * stride_out + offs, v)


# ------------------------------------------------------------------ ② case 层
DTYPES = ('float32', 'float16', 'bfloat16')

SHAPES = ((8, 16), (4, 32))

def ref(args, meta):
    src = np.asarray(args["src"], dtype=np.float32)
    dest = np.asarray(args["dest_loc"], dtype=np.int64)
    out = np.array(args["out"], dtype=np.float32, copy=True)
    for i in range(src.shape[0]):
        out[dest[i]] = src[i]
    return {"out": out.astype(np.asarray(args["out"]).dtype)}

def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    n, d = (int(v) for v in shape)
    from case_utils import fast_rng
    rng = fast_rng(seed)
    dest = rng.permutation(n).astype(np.int32)
    args = {"src": rng.standard_normal((n, d)).astype(dtype), "dest_loc": dest,
            "out": np.zeros((n, d), dtype=dtype),
            "stride_src": np.int32(d), "stride_out": np.int32(d)}
    meta = {"D": d}
    return {"args": args, "meta": meta, "grid": (n,),
            "outputs": ("out",), "expected": ref(args, meta)}

def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, destindex_copy_kernel, DTYPES,
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
