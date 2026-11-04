"""max_reduction: reduce(reduction 类)bench 算子,自 tritonbench 收入 medium 组。
bench 稳态配置见 ~/ops/bench/workload.json(声明 shape [256],验证 shape [262144]);正确性 shape 见下方 SHAPES。
模式: creation.full、memory.store、math.maximum、reduce.max、creation.arange、memory.load.masked。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""

OPERATOR = {"name": "medium/max_reduction", "group": "medium", "channel": "local", "execution": "triton_kernel", "verification": "correctness", "tags": ["creation.full", "memory.store", "math.maximum", "reduce.max", "creation.arange", "memory.load.masked", "control.for_range", "args.runtime_scalar"]}
COPIED_FROM = {"repo": "tritonbench @ ops", "path": "tritonbench/max_reduction.py", "validated": True}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.autotune(
    configs=[
        triton.Config({'BLOCK_SIZE': 64}, num_warps=4),
        triton.Config({'BLOCK_SIZE': 128}, num_warps=4),
        triton.Config({'BLOCK_SIZE': 256}, num_warps=4),
    ],
    key=["M"],
)
@triton.jit
def max_reduction_kernel(inp, out, M, BLOCK_SIZE: tl.constexpr):
    acc = tl.full([BLOCK_SIZE], float("-inf"), tl.float32)
    for off in range(0, M, BLOCK_SIZE):
        idx = off + tl.arange(0, BLOCK_SIZE)
        v = tl.load(inp + idx, mask=idx < M, other=float("-inf")).to(tl.float32)
        acc = tl.maximum(acc, v)
    tl.store(out, tl.max(acc, axis=0))


# ------------------------------------------------------------------ ② case 层
DTYPES = ('float32', 'float16', 'bfloat16')

SHAPES = ((128,), (99,))

def ref(args, meta):
    x = np.asarray(args["inp"], dtype=np.float32)
    return {"out": np.array([x.max()], dtype=np.asarray(args["out"]).dtype)}

def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    n = int(np.prod(shape))
    from case_utils import fast_rng
    rng = fast_rng(seed)
    args = {"inp": rng.standard_normal(n).astype(dtype), "out": np.zeros(1, dtype=dtype),
            "M": np.int32(n)}
    meta = {}
    return {"args": args, "meta": meta, "grid": (1,),
            "outputs": ("out",), "expected": ref(args, meta)}

def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, max_reduction_kernel, DTYPES,
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
