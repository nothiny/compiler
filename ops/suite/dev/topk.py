"""topk: reduce(reduction 类)bench 算子,自 tritonbench 收入 medium 组。
bench 稳态配置见 ~/ops/bench/workload.json(声明 shape [4, 16],验证 shape [64, 1024]);正确性 shape 见下方 SHAPES。
模式: creation.arange、reduce.argmax、reduce.max、memory.store、creation.where、memory.load.masked。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""

OPERATOR = {"name": "medium/topk", "group": "medium", "channel": "local", "execution": "triton_kernel", "verification": "correctness", "tags": ["creation.arange", "reduce.argmax", "reduce.max", "memory.store", "creation.where", "memory.load.masked", "control.for_range", "args.runtime_scalar"]}
COPIED_FROM = {"repo": "tritonbench @ ops", "path": "tritonbench/topk.py", "validated": True}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def topk_kernel(x_ptr, vals_ptr, idx_ptr, n_cols, K: tl.constexpr, BLOCK: tl.constexpr):
    row = tl.program_id(0)
    cols = tl.arange(0, BLOCK)
    x = tl.load(x_ptr + row * n_cols + cols, mask=cols < n_cols, other=float("-inf")).to(tl.float32)
    for k in range(K):
        i = tl.argmax(x, axis=0, tie_break_left=True)
        v = tl.max(x, axis=0)
        tl.store(vals_ptr + row * K + k, v)
        tl.store(idx_ptr + row * K + k, i)
        x = tl.where(cols == i, float("-inf"), x)


# ------------------------------------------------------------------ ② case 层
DTYPES = ('float32', 'float16', 'bfloat16')

SHAPES = ((4, 16), (8, 32))

def ref(args, meta):
    x = np.asarray(args["x_ptr"], dtype=np.float32)
    k = meta["K"]
    order = np.argsort(-x, axis=1, kind="stable")[:, :k]
    vals = np.take_along_axis(x, order, axis=1)
    return {"vals_ptr": vals.astype(np.asarray(args["vals_ptr"]).dtype),
            "idx_ptr": order.astype(np.asarray(args["idx_ptr"]).dtype)}

def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    r, c = (int(x) for x in shape)
    k = 3
    from case_utils import fast_rng
    rng = fast_rng(seed)
    args = {"x_ptr": rng.standard_normal((r, c)).astype(dtype),
            "vals_ptr": np.zeros((r, k), dtype=dtype), "idx_ptr": np.zeros((r, k), dtype=np.int32),
            "n_cols": np.int32(c)}
    meta = {"K": k, "BLOCK": triton.next_power_of_2(c)}
    return {"args": args, "meta": meta, "grid": (r,),
            "outputs": ("vals_ptr", "idx_ptr"), "expected": ref(args, meta)}

def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, topk_kernel, DTYPES,
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
