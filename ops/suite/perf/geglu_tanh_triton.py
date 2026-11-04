"""geglu_tanh_triton: TritonBench 算子( 类)。
模式: creation.arange、memory.store.masked、memory.load.masked、math.sigmoid、args.runtime_scalar。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""

OPERATOR = {'name': 'bench/geglu_tanh_triton', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'memory.store.masked', 'memory.load.masked', 'math.sigmoid', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/geglu_tanh_triton.py', 'sha256': 'ccc46b61a9df933f2a2ac0682e8ead26a499daf2ab1005a7b1303add8b7ab654'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def geglu_tanh_forward_kernel(a_ptr, b_ptr, c_ptr, stride, n_cols: tl.constexpr,
                              BLOCK_SIZE: tl.constexpr):
    program_id = tl.program_id(0)
    a_ptr += program_id * stride
    b_ptr += program_id * stride
    c_ptr += program_id * stride

    col_offsets = tl.arange(0, BLOCK_SIZE)
    mask = col_offsets < n_cols
    a_row = tl.load(a_ptr + col_offsets, mask=mask, other=0.0).to(tl.float32)
    b_row = tl.load(b_ptr + col_offsets, mask=mask, other=0.0).to(tl.float32)

    a_cubed = a_row * a_row * a_row
    tanh_arg = 0.7978845608028654 * (a_row + 0.044715 * a_cubed)
    tanh_result = 2.0 * tl.sigmoid(2.0 * tanh_arg) - 1.0
    geglu_a = 0.5 * a_row * (1.0 + tanh_result)
    c_row = geglu_a * b_row
    tl.store(c_ptr + col_offsets, c_row, mask=mask)


# ------------------------------------------------------------------ ② case 层
DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((2, 128), (5, 99))

def ref(args, meta):
    a = np.asarray(args["a_ptr"], dtype=np.float64)
    b = np.asarray(args["b_ptr"], dtype=np.float64)
    z = 0.7978845608028654 * (a + 0.044715 * a * a * a)
    c = 0.5 * a * (1.0 + np.tanh(z)) * b
    return {"c_ptr": c.astype(np.asarray(args["c_ptr"]).dtype)}

def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    shape = tuple(int(value) for value in shape)
    n_rows, n_cols = shape
    from case_utils import fast_rng
    rng = fast_rng(seed)
    a = (rng.standard_normal((n_rows, n_cols)) * 0.5).astype(dtype)
    b = (rng.standard_normal((n_rows, n_cols)) * 0.5).astype(dtype)
    c = np.zeros((n_rows, n_cols), dtype=dtype)
    args = {"a_ptr": a, "b_ptr": b, "c_ptr": c, "stride": np.int32(n_cols)}
    meta = {"n_cols": n_cols, "BLOCK_SIZE": max(128, triton.next_power_of_2(n_cols))}
    return {"args": args, "meta": meta, "grid": (n_rows,),
            "outputs": ("c_ptr",), "expected": ref(args, meta)}

def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, geglu_tanh_forward_kernel, DTYPES,
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
