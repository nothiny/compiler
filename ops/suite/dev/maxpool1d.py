"""makora_maxpool1d_kernel: 取自 makora 数据集 train split 第 65335 行(上游 kernel max_pool1d_kernel)。

模式: args.runtime_scalar、cast.to、control.for_range、control.loop_carried、creation.arange、creation.full、dtype.float32、math.maximum、memory.load、memory.load.masked。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。循环上界来自运行时标量(不是 constexpr)。constexpr 参数: BLOCK_SIZE, VEC。

文件只有两层:
  ① makora_maxpool1d_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/maxpool1d', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'cast.to', 'control.for_range', 'control.loop_carried', 'creation.arange', 'creation.full', 'dtype.float32', 'math.maximum', 'memory.load', 'memory.load.masked', 'memory.load.other', 'memory.store', 'memory.store.masked', 'shape.ravel', 'tile.2d']}
SOURCE = {'dataset': 'makora-ai/triton-gpu-latency', 'revision': '3b30911350fa433e1cb97ec2a41bd8908dd35d5d', 'file': 'data/train.parquet', 'row': 65335, 'source_sha256': 'b942f30a17c79574a7087528044a52cee03ef782a571fe530c051b21fed1660c', 'upstream_kernel': 'max_pool1d_kernel', 'upstream_latency_label': 3.12980096101761, 'license': 'Apache-2.0', 'adaptations': ['rename JIT entry', 'replace torch host wrapper with independent NumPy case/ref', 'select explicit legal launch tile', 'remove host autotune decorator'], 'extraction_scope': 'original single JIT kernel stage, not the entire original PyTorch Model'}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def makora_maxpool1d_kernel(input_ptr, output_ptr, batch_channels, input_len, output_len, kernel_size, stride, padding, dilation, BLOCK_SIZE: tl.constexpr, VEC: tl.constexpr):
    TOTAL_ELEMS: tl.constexpr = BLOCK_SIZE * VEC
    pid_bc = tl.program_id(0)
    pid_block = tl.program_id(1)
    base_in = pid_bc * input_len
    base_out = pid_bc * output_len
    block_start = pid_block * TOTAL_ELEMS
    offs_2d = tl.arange(0, BLOCK_SIZE)[:, None] * VEC + tl.arange(0, VEC)[None, :]
    offs = block_start + tl.ravel(offs_2d)
    mask = offs < output_len
    max_vals = tl.full((TOTAL_ELEMS,), float('-inf'), dtype=tl.float32)
    for k in range(kernel_size):
        in_pos = offs * stride - padding + k * dilation
        in_mask = (in_pos >= 0) & (in_pos < input_len) & mask
        vals = tl.load(input_ptr + base_in + in_pos, mask=in_mask, other=float('-inf'))
        max_vals = tl.maximum(max_vals, vals.to(tl.float32))
    tl.store(output_ptr + base_out + offs, max_vals.to(input_ptr.dtype.element_ty), mask=mask)

# ------------------------------------------------------------------ ② case 层
# 典型用法依据:数据集原始程序的常量(已按 sha256 核对原始文件):
#   batch_size = 64
#   kernel_size = 8
#   stride      = 1
#   padding     = 4
# 下面 SHAPES 只缩小了这些配置里的批类维度,结构维度按原值保留。
# (shape,) 的角色:第一个是典型用法,其余是泛化/尾块/退化用例。
#   (3, 19, 3, 2, 1, 1)
#   (2, 37, 4, 1, 2, 2)
#   (4, 19, 3, 2, 1, 1)
# DTYPES: float32 —— 原始用途的 dtype 在前;非法域(例如本机 Triton 只吃 fp32 的exp/sqrt/erf/atomic)的算子只声明合法的那一种。
#   规模    (6, 19, 3, 2, 1, 1)  典型规模 ×2:dim0 3->6
#   规模    (3, 38, 3, 2, 1, 1)  典型规模 ×2:dim1 19->38

SHAPES = ((3, 19, 3, 2, 1, 1), (2, 37, 4, 1, 2, 2))
DTYPES = ('float32', 'float16', 'bfloat16')
def ref(args, meta):
    x=args['input_ptr'];nc,l=x.shape
    lo=args['output_len'];y=np.full((nc,lo),-np.inf,np.float64)
    for i in range(lo):
        for k in range(args['kernel_size']):
            at=i*args['stride']-args['padding']+k*args['dilation']
            if 0<=at<l:y[:,i]=np.maximum(y[:,i],x[:,at])
    return {'output_ptr':y.astype(args['output_ptr'].dtype)}
def make_case(shape=None, dtype=None, seed=0):
    shape = tuple(SHAPES[0] if shape is None else shape)
    dtype = DTYPES[0] if dtype is None else np.dtype(dtype).name
    if shape not in SHAPES or dtype not in DTYPES:
        raise ValueError((shape, dtype))
    from case_utils import fast_rng
    rng = fast_rng(seed)
    nc,l,ks,st,pad,dil=shape
    lo=(l+2*pad-dil*(ks-1)-1)//st+1
    x=rng.normal(size=(nc,l)).astype(dtype)
    args={'input_ptr':x,'output_ptr':np.zeros((nc,lo),dtype=dtype),'batch_channels':nc,'input_len':l,'output_len':lo,'kernel_size':ks,'stride':st,'padding':pad,'dilation':dil}
    meta = {'BLOCK_SIZE':8,'VEC':2}
    expected = ref(args, meta)
    return {"kernel": makora_maxpool1d_kernel, "args": args, "meta": meta, "grid": (nc,triton.cdiv(lo,16)), "outputs": ('output_ptr',), "expected": expected, "comparison": {k: {"exact": v.dtype.kind in "biu", "rtol": 0.0002, "atol": 2e-05} for k, v in expected.items()}}


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
