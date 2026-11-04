"""makora_splitk_gemv_kernel: 取自 makora 数据集 test split 第 166 行(上游 kernel matvec_kernel)。

模式: args.runtime_scalar、atomic.add、atomic.masked、control.for_range、control.loop_carried、creation.arange、creation.zeros、math.cdiv、math.minimum、memory.load。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。循环上界来自运行时标量(不是 constexpr)。constexpr 参数: BLOCK_M, BLOCK_K。

文件只有两层:
  ① makora_splitk_gemv_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/splitk_gemv', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'atomic.add', 'atomic.masked', 'control.for_range', 'control.loop_carried', 'creation.arange', 'creation.zeros', 'math.cdiv', 'math.minimum', 'memory.load', 'memory.load.masked', 'memory.load.other', 'reduce.sum.axis1', 'tile.2d']}
SOURCE = {'dataset': 'makora-ai/triton-gpu-latency', 'revision': '3b30911350fa433e1cb97ec2a41bd8908dd35d5d', 'file': 'data/test.parquet', 'row': 166, 'source_sha256': '5c6073f59bb5e6db240b3bf9678b57183c864b7001b47ca5d66cf5489c117023', 'upstream_kernel': 'matvec_kernel', 'upstream_latency_label': 173.317522583008, 'license': 'Apache-2.0', 'adaptations': ['rename JIT entry', 'replace torch host wrapper with independent NumPy case/ref', 'select explicit legal launch tile'], 'extraction_scope': 'original single JIT kernel stage, not the entire original PyTorch Model', 'local_semantic_fix': 'basic/provenance/local-kernel-fixes.json'}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def makora_splitk_gemv_kernel(A_ptr, B_ptr, C_ptr, M, K, stride_am, stride_ak, stride_bk, stride_bn, stride_cm, stride_cn, BLOCK_M: tl.constexpr, BLOCK_K: tl.constexpr):
    pid_m = tl.program_id(0)
    pid_k = tl.program_id(1)
    offs_m = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    mask_m = offs_m < M
    split_k = tl.num_programs(1)
    k_chunk = tl.cdiv(K, split_k)
    k_start = pid_k * k_chunk
    k_end = tl.minimum(k_start + k_chunk, K)
    acc = tl.zeros((BLOCK_M,), dtype=tl.float32)
    for k0 in range(k_start, k_end, BLOCK_K):
        offs_k = k0 + tl.arange(0, BLOCK_K)
        k_mask = (offs_k < K) & (offs_k < k_end)
        A_tile = tl.load(A_ptr + (offs_m[:, None] * stride_am + offs_k[None, :] * stride_ak), mask=mask_m[:, None] & k_mask[None, :], other=0.0)
        B_vec = tl.load(B_ptr + offs_k * stride_bk, mask=k_mask, other=0.0)
        acc += tl.sum(A_tile * B_vec[None, :], axis=1)
    tl.atomic_add(C_ptr + offs_m * stride_cm, acc, mask=mask_m)

# ------------------------------------------------------------------ ② case 层
# (shape,) 的角色:第一个是典型用法,其余是泛化/尾块/退化用例。
#   (17, 64)
#   (33, 128)
#   (9, 67)
#   (48, 257)
# DTYPES: float32 —— 原始用途的 dtype 在前;非法域(例如本机 Triton 只吃 fp32 的exp/sqrt/erf/atomic)的算子只声明合法的那一种。
#   规模    (34, 64)  典型规模 ×2:dim0 17->34
#   规模    (17, 128)  典型规模 ×2:dim1 64->128

SHAPES = ((17, 64), (33, 128))
DTYPES = ('float32', 'float16')
def ref(args, meta):
    a = args['A_ptr'].astype(np.float64)
    b = args['B_ptr'].astype(np.float64)
    return {'C_ptr': (a @ b).astype(np.float32)}
def make_case(shape=None, dtype=None, seed=0):
    shape = tuple(SHAPES[0] if shape is None else shape)
    dtype = DTYPES[0] if dtype is None else np.dtype(dtype).name
    if shape not in SHAPES or dtype not in DTYPES:
        raise ValueError((shape, dtype))
    from case_utils import fast_rng
    rng = fast_rng(seed)
    m,k = shape
    a = rng.normal(size=(m,k)).astype(dtype)
    b = rng.normal(size=(k,1)).astype(dtype)
    args = {'A_ptr':a, 'B_ptr':b, 'C_ptr':np.zeros((m,1),np.float32), 'M':m,'K':k,'stride_am':k,'stride_ak':1,'stride_bk':1,'stride_bn':1,'stride_cm':1,'stride_cn':1}
    splits = 2
    meta = {'BLOCK_M': 16, 'BLOCK_K': 16}
    expected = ref(args, meta)
    return {"kernel": makora_splitk_gemv_kernel, "args": args, "meta": meta, "grid": (triton.cdiv(m,16),splits), "outputs": ('C_ptr',), "expected": expected, "comparison": {k: {"exact": v.dtype.kind in "biu", "rtol": 0.0003, "atol": 3e-05} for k, v in expected.items()}}


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
