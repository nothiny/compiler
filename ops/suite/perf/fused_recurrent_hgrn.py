"""fused_recurrent_hgrn: fla(memory 类)。
bench 稳态配置见 bench/workload.json(声明 shape [2, 16, 32],验证 shape [512, 16, 32]);正确性 shape 见下方 SHAPES。
模式: creation.arange、creation.zeros、memory.store.masked、memory.load.masked、control.for_range、args.runtime_scalar。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""

OPERATOR = {'name': 'bench/fused_recurrent_hgrn', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'creation.zeros', 'memory.store.masked', 'memory.load.masked', 'control.for_range', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/fused_recurrent_hgrn.py', 'sha256': 'fead4715989d676a5f4c130f1c2c68f22cc341fc99dc7ada49aa8a454aa9064d'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def hgrn_kernel(i_ptr, g_ptr, o_ptr, B, T, D, stride_ib, stride_it, stride_id,
                BLOCK_D: tl.constexpr):
    off_b = tl.program_id(0)
    offs = tl.arange(0, BLOCK_D)
    mask = offs < D
    h = tl.zeros([BLOCK_D], dtype=tl.float32)
    for t in range(T):
        i = tl.load(i_ptr + off_b * stride_ib + t * stride_it + offs * stride_id, mask=mask, other=0.0).to(tl.float32)
        g = tl.load(g_ptr + off_b * stride_ib + t * stride_it + offs * stride_id, mask=mask, other=0.0).to(tl.float32)
        h = (1.0 - g) * h + g * i
        tl.store(o_ptr + off_b * stride_ib + t * stride_it + offs * stride_id, h, mask=mask)


# ------------------------------------------------------------------ ② case 层
DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((2, 16, 32), (3, 17, 33), (1, 32, 32))

def ref(args, meta):
    i = np.asarray(args["i_ptr"], dtype=np.float64)
    g = np.asarray(args["g_ptr"], dtype=np.float64)
    b, t, d = i.shape
    o = np.zeros((b, t, d))
    h = np.zeros((b, d))
    for k in range(t):
        h = (1.0 - g[:, k]) * h + g[:, k] * i[:, k]
        o[:, k] = h
    return {"o_ptr": o.astype(np.asarray(args["o_ptr"]).dtype)}

def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    b, t, d = (int(x) for x in shape)
    from case_utils import fast_rng
    rng = fast_rng(seed)
    args = {"i_ptr": rng.standard_normal((b, t, d)).astype(dtype),
            "g_ptr": rng.uniform(0.0, 1.0, (b, t, d)).astype(dtype),
            "o_ptr": np.zeros((b, t, d), dtype=dtype),
            "B": np.int32(b), "T": np.int32(t), "D": np.int32(d),
            "stride_ib": np.int32(t * d), "stride_it": np.int32(d), "stride_id": np.int32(1)}
    meta = {"BLOCK_D": triton.next_power_of_2(d)}
    return {"args": args, "meta": meta, "grid": (b,),
            "outputs": ("o_ptr",), "expected": ref(args, meta)}

def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, hgrn_kernel, DTYPES,
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
