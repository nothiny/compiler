"""index_select_cat: layout(memory 类)。
bench 稳态配置见 bench/workload.json(声明 shape [4, 8],验证 shape [32768, 8]);正确性 shape 见下方 SHAPES。
模式: memory.load.masked、memory.store.masked、creation.arange、args.runtime_scalar。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""

OPERATOR = {'name': 'bench/index_select_cat', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['memory.load.masked', 'memory.store.masked', 'creation.arange', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/index_select_cat.py', 'sha256': '2ff76cd7051c838e0fb1a6918bc672084a8322268db353fed414dc15b05c0ac9'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def index_select_cat_kernel(output_ptr, source_ptr, index_ptr, num_indices, num_cols,
                            stride0, stride1, BLOCK_I: tl.constexpr, BLOCK_C: tl.constexpr):
    pid0 = tl.program_id(0)
    pid1 = tl.program_id(1)
    idx = pid0 * BLOCK_I + tl.arange(0, BLOCK_I)
    cols = pid1 * BLOCK_C + tl.arange(0, BLOCK_C)
    m = (idx[:, None] < num_indices) & (cols[None, :] < num_cols)
    row = tl.load(index_ptr + idx, mask=idx < num_indices, other=0)
    v = tl.load(source_ptr + row[:, None] * stride0 + cols[None, :] * stride1, mask=m, other=0.0)
    tl.store(output_ptr + idx[:, None] * stride0 + cols[None, :] * stride1, v, mask=m)


# ------------------------------------------------------------------ ② case 层
DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((4, 8), (5, 9))

def ref(args, meta):
    src = np.asarray(args["source_ptr"], dtype=np.float32)
    idx = np.asarray(args["index_ptr"], dtype=np.int64)
    return {"output_ptr": src[idx].astype(np.asarray(args["output_ptr"]).dtype)}

def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    n_idx, n_cols = (int(v) for v in shape)
    n_rows = n_idx + 2
    from case_utils import fast_rng
    rng = fast_rng(seed)
    args = {"output_ptr": np.zeros((n_idx, n_cols), dtype=dtype),
            "source_ptr": rng.standard_normal((n_rows, n_cols)).astype(dtype),
            "index_ptr": rng.integers(0, n_rows, n_idx).astype(np.int32),
            "num_indices": np.int32(n_idx), "num_cols": np.int32(n_cols),
            "stride0": np.int32(n_cols), "stride1": np.int32(1)}
    meta = {"BLOCK_I": 8, "BLOCK_C": triton.next_power_of_2(n_cols)}
    grid = (triton.cdiv(n_idx, 8), triton.cdiv(n_cols, triton.next_power_of_2(n_cols)))
    return {"args": args, "meta": meta, "grid": grid,
            "outputs": ("output_ptr",), "expected": ref(args, meta)}

def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, index_select_cat_kernel, DTYPES,
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
