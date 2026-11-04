"""makora_implicit_conv2d_kernel: 取自 makora 数据集 test split 第 8739 行(上游 kernel conv2d_implicit_gemm_kernel)。

模式: args.runtime_scalar、control.for_range、control.loop_carried、creation.arange、creation.zeros、linalg.dot、memory.load、memory.load.masked、memory.load.other、memory.store。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。循环上界来自运行时标量(不是 constexpr)。constexpr 参数: BLOCK_M, BLOCK_N, BLOCK_K。

文件只有两层:
  ① makora_implicit_conv2d_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/implicit_conv2d', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.for_range', 'control.loop_carried', 'creation.arange', 'creation.zeros', 'linalg.dot', 'memory.load', 'memory.load.masked', 'memory.load.other', 'memory.store', 'memory.store.masked', 'shape.broadcast_to', 'tile.2d']}
SOURCE = {'dataset': 'makora-ai/triton-gpu-latency', 'revision': '3b30911350fa433e1cb97ec2a41bd8908dd35d5d', 'file': 'data/test.parquet', 'row': 8739, 'source_sha256': '2968330849da7e75a63846bcae0fa406fd576cb66735774752cf4eaa576371b5', 'upstream_kernel': 'conv2d_implicit_gemm_kernel', 'upstream_latency_label': 30.5384137535095, 'license': 'Apache-2.0', 'adaptations': ['rename JIT entry', 'replace torch host wrapper with independent NumPy case/ref', 'select explicit legal launch tile'], 'extraction_scope': 'original single JIT kernel stage, not the entire original PyTorch Model'}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def makora_implicit_conv2d_kernel(x_ptr, wmat_ptr, y_ptr, N, C, H, W, OC, KH, KW, H_OUT, W_OUT, K, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr):
    pid_m = tl.program_id(0)
    pid_n = tl.program_id(1)
    M = N * H_OUT * W_OUT
    offs_m = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    mask_m = offs_m < M
    mask_n = offs_n < OC
    hw_out = H_OUT * W_OUT
    n_idx = offs_m // hw_out
    rem = offs_m % hw_out
    h_out_idx = rem // W_OUT
    w_out_idx = rem % W_OUT
    in_batch_stride = C * H * W
    in_ch_stride = H * W
    in_h_stride = W
    base_in = n_idx * in_batch_stride + h_out_idx * in_h_stride + w_out_idx
    acc = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)
    for k0 in range(0, K, BLOCK_K):
        k_idx = k0 + tl.arange(0, BLOCK_K)
        khw = KH * KW
        c_idx = k_idx // khw
        rs = k_idx % khw
        r_idx = rs // KW
        s_idx = rs % KW
        a_offsets = base_in[:, None] + c_idx[None, :] * in_ch_stride + r_idx[None, :] * in_h_stride + s_idx[None, :]
        a = tl.load(x_ptr + a_offsets, mask=mask_m[:, None], other=0.0)
        b_offsets = k_idx[:, None] * OC + offs_n[None, :]
        b = tl.load(wmat_ptr + b_offsets, mask=tl.broadcast_to(mask_n[None, :], (BLOCK_K, BLOCK_N)), other=0.0)
        acc += tl.dot(a, b)
    out_batch_stride = OC * H_OUT * W_OUT
    out_c_stride = H_OUT * W_OUT
    out_h_stride = W_OUT
    out_offsets = n_idx[:, None] * out_batch_stride + offs_n[None, :] * out_c_stride + h_out_idx[:, None] * out_h_stride + w_out_idx[:, None]
    tl.store(y_ptr + out_offsets, acc, mask=mask_m[:, None] & mask_n[None, :])

# ------------------------------------------------------------------ ② case 层
# 典型用法依据:数据集原始程序的常量(已按 sha256 核对原始文件):
#   batch_size = 8
#   height = 512
#   width = 1024
#   in_channels = 64  # increased channels
#   out_channels = 128
#   kernel_size = 3
# 下面 SHAPES 只缩小了这些配置里的批类维度,结构维度按原值保留。
# (shape,) 的角色:第一个是典型用法,其余是泛化/尾块/退化用例。
#   (1, 4, 5, 7, 7)
#   (2, 8, 6, 5, 19)
#   (3, 8, 12, 12, 32)
# DTYPES: float16 —— 原始用途的 dtype 在前;非法域(例如本机 Triton 只吃 fp32 的exp/sqrt/erf/atomic)的算子只声明合法的那一种。
#   规模    (2, 4, 5, 7, 7)  典型规模 ×2:dim0 1->2
#   规模    (1, 4, 5, 14, 7)  典型规模 ×2:dim3 7->14

SHAPES = ((1, 4, 5, 7, 7), (2, 8, 6, 5, 19), (1, 4, 5, 14, 7))
DTYPES = ('float16', 'float32', 'bfloat16')
def ref(args, meta):
    x=args['x_ptr'].astype(np.float64)
    n,c,h,w=x.shape
    oc,kh,kw=args['OC'],args['KH'],args['KW']
    weights=args['wmat_ptr'].astype(np.float64).reshape(c,kh,kw,oc)
    y=np.zeros(args['y_ptr'].shape,np.float64)
    for i in range(args['H_OUT']):
        for j in range(args['W_OUT']):
            y[:,:,i,j]=np.tensordot(x[:,:,i:i+kh,j:j+kw],weights,axes=((1,2,3),(0,1,2)))
    return {'y_ptr':y.astype(args['y_ptr'].dtype)}
def make_case(shape=None, dtype=None, seed=0):
    shape = tuple(SHAPES[0] if shape is None else shape)
    dtype = DTYPES[0] if dtype is None else np.dtype(dtype).name
    if shape not in SHAPES or dtype not in DTYPES:
        raise ValueError((shape, dtype))
    from case_utils import fast_rng
    rng = fast_rng(seed)
    b,c,h,w,oc=shape
    kh=kw=2
    ho,wo=h-1,w-1
    k=c*kh*kw
    args={'x_ptr':rng.normal(0,0.3,(b,c,h,w)).astype(dtype),'wmat_ptr':rng.normal(0,0.3,(k,oc)).astype(dtype),'y_ptr':np.zeros((b,oc,ho,wo),dtype=dtype),'N':b,'C':c,'H':h,'W':w,'OC':oc,'KH':kh,'KW':kw,'H_OUT':ho,'W_OUT':wo,'K':k}
    meta = {'BLOCK_M':16,'BLOCK_N':16,'BLOCK_K':16}
    expected = ref(args, meta)
    return {"kernel": makora_implicit_conv2d_kernel, "args": args, "meta": meta, "grid": (triton.cdiv(b*ho*wo,16),triton.cdiv(oc,16)), "outputs": ('y_ptr',), "expected": expected, "comparison": {k: {"exact": v.dtype.kind in "biu", "rtol": 0.002, "atol": 0.0003} for k, v in expected.items()}}


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float16'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float16': 'float16'}


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
