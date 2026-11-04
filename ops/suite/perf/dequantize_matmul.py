"""dequantize_matmul: matmul(compute 类)。
bench 稳态配置见 bench/workload.json(声明 shape [32, 32],验证 shape [256, 32]);正确性 shape 见下方 SHAPES。
模式: memory.store.masked、creation.arange、memory.load.masked、args.runtime_scalar。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""

OPERATOR = {'name': 'bench/dequantize_matmul', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['memory.store.masked', 'creation.arange', 'memory.load.masked', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/dequantize_matmul.py', 'sha256': 'aa6065f86a125e9d92a28b57141ad37a5b77b4cb7c18521aa2f4fe4453676c85'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.autotune(
    configs=[
        triton.Config({'BLOCK_K': 16, 'BLOCK_N': 32}, num_warps=4),
        triton.Config({'BLOCK_K': 32, 'BLOCK_N': 32}, num_warps=4),
        triton.Config({'BLOCK_K': 32, 'BLOCK_N': 64}, num_warps=4),
        triton.Config({'BLOCK_K': 64, 'BLOCK_N': 64}, num_warps=4),
    ],
    key=["K","N"],
)
@triton.jit
def dequantize_kernel(b_ptr, b_scale_ptr, fpb_ptr, K, N,
                      stride_bk, stride_bn, stride_fpbk, stride_fpbn,
                      BLOCK_K: tl.constexpr, BLOCK_N: tl.constexpr):
    pid_k = tl.program_id(0)
    pid_n = tl.program_id(1)
    offs_k = pid_k * BLOCK_K + tl.arange(0, BLOCK_K)
    offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    mask = (offs_k[:, None] < K) & (offs_n[None, :] < N)
    b = tl.load(b_ptr + offs_k[:, None] * stride_bk + offs_n[None, :] * stride_bn,
                mask=mask, other=0).to(tl.float32)
    s = tl.load(b_scale_ptr + offs_n, mask=offs_n < N, other=0.0).to(tl.float32)
    tl.store(fpb_ptr + offs_k[:, None] * stride_fpbk + offs_n[None, :] * stride_fpbn,
             b * s[None, :], mask=mask)


# ------------------------------------------------------------------ ② case 层
DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((32, 32), (33, 33))

def ref(args, meta):
    b = np.asarray(args["b_ptr"], dtype=np.float64)
    s = np.asarray(args["b_scale_ptr"], dtype=np.float64)
    return {"fpb_ptr": (b * s[None, :]).astype(np.asarray(args["fpb_ptr"]).dtype)}

def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    k, n = (int(v) for v in shape)
    from case_utils import fast_rng
    rng = fast_rng(seed)
    args = {"b_ptr": rng.integers(-127, 128, (k, n)).astype(np.int8),
            "b_scale_ptr": rng.random(n).astype(dtype),
            "fpb_ptr": np.zeros((k, n), dtype=dtype),
            "K": np.int32(k), "N": np.int32(n),
            "stride_bk": np.int32(n), "stride_bn": np.int32(1),
            "stride_fpbk": np.int32(n), "stride_fpbn": np.int32(1)}
    meta = {}
    grid = (triton.cdiv(k, 32), triton.cdiv(n, 32))
    return {"args": args, "meta": meta, "grid": lambda meta: (triton.cdiv(k, meta["BLOCK_K"]), triton.cdiv(n, meta["BLOCK_N"])),
            "outputs": ("fpb_ptr",), "expected": ref(args, meta)}

def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, dequantize_kernel, DTYPES,
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
