"""makora_tiled_argmin_kernel: 取自 makora 数据集 train split 第 82459 行(上游 kernel argmin_kernel)。

模式: args.runtime_scalar、cast.to、control.for_range、control.if、control.loop_carried、creation.arange、creation.full、creation.where、creation.zeros、dtype.int64。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。循环上界来自运行时标量(不是 constexpr)。constexpr 参数: BLOCK_INNER, BLOCK_REDUCE。

文件只有两层:
  ① makora_tiled_argmin_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/tiled_argmin', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'cast.to', 'control.for_range', 'control.if', 'control.loop_carried', 'creation.arange', 'creation.full', 'creation.where', 'creation.zeros', 'dtype.int64', 'memory.load', 'memory.load.eviction_policy', 'memory.load.masked', 'memory.load.other', 'memory.store', 'memory.store.masked', 'reduce.argmin.axis1', 'reduce.min.axis1', 'tile.2d']}
SOURCE = {'dataset': 'makora-ai/triton-gpu-latency', 'revision': '3b30911350fa433e1cb97ec2a41bd8908dd35d5d', 'file': 'data/train.parquet', 'row': 82459, 'source_sha256': 'd9ffed26a8f61888aed83b787a9114546fdb7c69e470c5d745f34c38180f21a3', 'upstream_kernel': 'argmin_kernel', 'upstream_latency_label': 3.75064705133438, 'license': 'Apache-2.0', 'adaptations': ['rename JIT entry', 'replace torch host wrapper with independent NumPy case/ref', 'select explicit legal launch tile'], 'extraction_scope': 'original single JIT kernel stage, not the entire original PyTorch Model'}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def makora_tiled_argmin_kernel(x_ptr, y_ptr, stride_x_batch, stride_x_reduce, stride_x_inner, stride_y_batch, stride_y_inner, BatchSize, ReduceSize, InnerSize, BLOCK_INNER: tl.constexpr, BLOCK_REDUCE: tl.constexpr):
    pid_inner = tl.program_id(0)
    pid_batch = tl.program_id(1)
    offs_inner = pid_inner * BLOCK_INNER + tl.arange(0, BLOCK_INNER)
    mask_inner = offs_inner < InnerSize
    if pid_batch >= BatchSize:
        return
    x_base = x_ptr + pid_batch * stride_x_batch + offs_inner * stride_x_inner
    y_base = y_ptr + pid_batch * stride_y_batch + offs_inner * stride_y_inner
    min_val = tl.full([BLOCK_INNER], float('inf'), dtype=tl.float32)
    min_idx = tl.zeros([BLOCK_INNER], dtype=tl.int32)
    for r_start in range(0, ReduceSize, BLOCK_REDUCE):
        r_offs = r_start + tl.arange(0, BLOCK_REDUCE)
        r_mask = r_offs < ReduceSize
        ptr = x_base[:, None] + r_offs[None, :] * stride_x_reduce
        val = tl.load(ptr, mask=mask_inner[:, None] & r_mask[None, :], other=float('inf'), eviction_policy='evict_first')
        local_min = tl.min(val, axis=1)
        local_argmin = tl.argmin(val, axis=1)
        cond = local_min < min_val
        min_val = tl.where(cond, local_min, min_val)
        min_idx = tl.where(cond, r_start + local_argmin, min_idx)
    tl.store(y_base, min_idx.to(tl.int64), mask=mask_inner)

# ------------------------------------------------------------------ ② case 层
# 典型用法依据:数据集原始程序的常量(已按 sha256 核对原始文件):
#   batch_size = 128
#   dim = 1
# 下面 SHAPES 只缩小了这些配置里的批类维度,结构维度按原值保留。
# (shape,) 的角色:第一个是典型用法,其余是泛化/尾块/退化用例。
#   (2, 37, 5)
#   (3, 67, 9)
#   (4, 129, 16)
# DTYPES: float32 —— 原始用途的 dtype 在前;非法域(例如本机 Triton 只吃 fp32 的exp/sqrt/erf/atomic)的算子只声明合法的那一种。
#   规模    (4, 37, 5)  典型规模 ×2:dim0 2->4
#   规模    (2, 74, 5)  典型规模 ×2:dim1 37->74

SHAPES = ((2, 37, 5), (3, 67, 9))
DTYPES = ('float32', 'float16', 'bfloat16')
def ref(args, meta):
    return {'y_ptr':np.argmin(args['x_ptr'],axis=1).astype(np.int64)}
def make_case(shape=None, dtype=None, seed=0):
    shape = tuple(SHAPES[0] if shape is None else shape)
    dtype = DTYPES[0] if dtype is None else np.dtype(dtype).name
    if shape not in SHAPES or dtype not in DTYPES:
        raise ValueError((shape, dtype))
    from case_utils import fast_rng
    rng = fast_rng(seed)
    b,r,i=shape
    x=rng.normal(size=shape).astype(dtype)
    for batch in range(b):
        for inner in range(i):
            at = (batch * 11 + inner * 7 + 1) % r
            x[batch, at, inner] = -10
            if at + 32 < r:
                x[batch, at + 32, inner] = -10
    args={'x_ptr':x,'y_ptr':np.full((b,i),-1,np.int64),'stride_x_batch':r*i,'stride_x_reduce':i,'stride_x_inner':1,'stride_y_batch':i,'stride_y_inner':1,'BatchSize':b,'ReduceSize':r,'InnerSize':i}
    meta = {'BLOCK_INNER':8,'BLOCK_REDUCE':32}
    expected = ref(args, meta)
    return {"kernel": makora_tiled_argmin_kernel, "args": args, "meta": meta, "grid": (triton.cdiv(i,8),b), "outputs": ('y_ptr',), "expected": expected, "comparison": {k: {"exact": v.dtype.kind in "biu", "rtol": 0.0002, "atol": 2e-05} for k, v in expected.items()}}


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
