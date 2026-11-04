"""makora_transposed_conv3d_kernel: 取自 makora 数据集 train split 第 116094 行(上游 kernel conv_transpose3d_kernel)。

模式: args.runtime_scalar、control.for_range、control.if、control.loop_carried、creation.arange、creation.zeros、linalg.dot、math.cdiv、memory.load、memory.load.masked。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。循环上界来自运行时标量(不是 constexpr)。constexpr 参数: BLOCK_H, BLOCK_W, BLOCK_CIN, BLOCK_COUT, HAS_BIAS。

文件只有两层:
  ① makora_transposed_conv3d_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/transposed_conv3d', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.for_range', 'control.if', 'control.loop_carried', 'creation.arange', 'creation.zeros', 'linalg.dot', 'math.cdiv', 'memory.load', 'memory.load.masked', 'memory.load.other', 'memory.store', 'memory.store.masked', 'shape.permute', 'shape.reshape', 'tile.2d', 'tile.3d']}
SOURCE = {'dataset': 'makora-ai/triton-gpu-latency', 'revision': '3b30911350fa433e1cb97ec2a41bd8908dd35d5d', 'file': 'data/train.parquet', 'row': 116094, 'source_sha256': '84c7d4e4ec3847045e66d35284d487d5414e41cc025dcaf53f403e42ee037636', 'upstream_kernel': 'conv_transpose3d_kernel', 'upstream_latency_label': 60.3787334060669, 'license': 'Apache-2.0', 'adaptations': ['rename JIT entry', 'replace torch host wrapper with independent NumPy case/ref', 'select explicit legal launch tile'], 'extraction_scope': 'original single JIT kernel stage, not the entire original PyTorch Model'}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def makora_transposed_conv3d_kernel(X, W, Bias, Out, stride_xn, stride_xc, stride_xd, stride_xh, stride_xw, stride_wk_k, stride_wk_cin, stride_wk_cout, stride_on, stride_oc, stride_od, stride_oh, stride_ow, Cin_per_group, Cout_per_group, Groups, Din, Hin, Win, Dout, Hout, Wout, K, Stride, Padding, BLOCK_H: tl.constexpr, BLOCK_W: tl.constexpr, BLOCK_CIN: tl.constexpr, BLOCK_COUT: tl.constexpr, HAS_BIAS: tl.constexpr):
    pid_spatial = tl.program_id(0)
    pid_cout = tl.program_id(1)
    pid_z = tl.program_id(2)
    rem_z = pid_z
    d_out = rem_z % Dout
    rem_z = rem_z // Dout
    group = rem_z % Groups
    batch = rem_z // Groups
    num_tiles_w = tl.cdiv(Wout, BLOCK_W)
    tile_y = pid_spatial // num_tiles_w
    tile_x = pid_spatial % num_tiles_w
    off_h = tile_y * BLOCK_H + tl.arange(0, BLOCK_H)
    off_w = tile_x * BLOCK_W + tl.arange(0, BLOCK_W)
    mask_h = off_h < Hout
    mask_w = off_w < Wout
    off_cout = pid_cout * BLOCK_COUT + tl.arange(0, BLOCK_COUT)
    mask_cout = off_cout < Cout_per_group
    global_cout = group * Cout_per_group + off_cout
    base_cin_group = group * Cin_per_group
    ptr_out = Out + batch * stride_on + global_cout[None, :, None] * stride_oc + d_out * stride_od + off_h[:, None, None] * stride_oh + off_w[None, None, :] * stride_ow
    acc = tl.zeros((BLOCK_H, BLOCK_W, BLOCK_COUT), dtype=tl.float32)
    val_d_base = d_out + Padding
    val_h_base = off_h + Padding
    val_w_base = off_w + Padding
    for kz in range(K):
        val_d = val_d_base - kz
        if val_d % Stride == 0:
            d_in = val_d // Stride
            if d_in >= 0 and d_in < Din:
                off_x_d = d_in * stride_xd
                for ky in range(K):
                    val_h = val_h_base - ky
                    mask_h_k = (val_h % Stride == 0) & (val_h >= 0)
                    h_in = val_h // Stride
                    mask_h_k = mask_h_k & (h_in < Hin) & mask_h
                    for kx in range(K):
                        val_w = val_w_base - kx
                        mask_w_k = (val_w % Stride == 0) & (val_w >= 0)
                        w_in = val_w // Stride
                        mask_w_k = mask_w_k & (w_in < Win) & mask_w
                        mask_sw = mask_h_k[:, None] & mask_w_k[None, :]
                        off_x_spatial = off_x_d + h_in[:, None] * stride_xh + w_in[None, :] * stride_xw
                        k_idx = kz * (K * K) + ky * K + kx
                        off_w_k = k_idx * stride_wk_k
                        for cin_blk in range(0, Cin_per_group, BLOCK_CIN):
                            off_cin = cin_blk + tl.arange(0, BLOCK_CIN)
                            mask_cin = off_cin < Cin_per_group
                            ptr_x = X + batch * stride_xn + (base_cin_group + off_cin)[None, None, :] * stride_xc + off_x_spatial[:, :, None]
                            mask_x_load = mask_sw[:, :, None] & mask_cin[None, None, :]
                            x_tile = tl.load(ptr_x, mask=mask_x_load, other=0.0)
                            ptr_w = W + off_w_k + off_cin[:, None] * stride_wk_cin + off_cout[None, :] * stride_wk_cout
                            mask_w_load = mask_cin[:, None] & mask_cout[None, :]
                            w_tile = tl.load(ptr_w, mask=mask_w_load, other=0.0)
                            x_flat = tl.reshape(x_tile, (BLOCK_H * BLOCK_W, BLOCK_CIN))
                            acc_flat = tl.dot(x_flat, w_tile)
                            acc += tl.reshape(acc_flat, (BLOCK_H, BLOCK_W, BLOCK_COUT))
    if HAS_BIAS:
        b_val = tl.load(Bias + global_cout, mask=mask_cout, other=0.0)
        acc += b_val[None, None, :]
    mask_store = mask_h[:, None, None] & mask_w[None, None, :] & mask_cout[None, :, None]
    acc_store = tl.permute(acc, (0, 2, 1))
    tl.store(ptr_out, acc_store, mask=mask_store)

# ------------------------------------------------------------------ ② case 层
# 典型用法依据:数据集原始程序的常量(已按 sha256 核对原始文件):
#   batch_size = 4
#   in_channels = 32
#   out_channels = 32
#   kernel_size = 3
#   depth = 32
#   height = 64
# 下面 SHAPES 只缩小了这些配置里的批类维度,结构维度按原值保留。
# (shape,) 的角色:第一个是典型用法,其余是泛化/尾块/退化用例。
#   (1, 3, 5, 2, 3, 4, 1, 0)
#   (1, 4, 7, 3, 2, 3, 2, 1)
#   (2, 3, 5, 2, 3, 4, 1, 0)
# DTYPES: float16 —— 原始用途的 dtype 在前;非法域(例如本机 Triton 只吃 fp32 的exp/sqrt/erf/atomic)的算子只声明合法的那一种。
#   规模    (1, 3, 10, 2, 3, 4, 1, 0)  典型规模 ×2:dim2 5->10
#   规模    (3, 3, 5, 2, 3, 4, 1, 0)  典型规模 ×3:dim0 1->3

SHAPES = ((1, 3, 5, 2, 3, 4, 1, 0), (1, 3, 10, 2, 3, 4, 1, 0), (3, 3, 5, 2, 3, 4, 1, 0))
DTYPES = ('float16', 'float32', 'bfloat16')
def ref(args, meta):
    x=args['X'].astype(np.float64);w=args['W'].astype(np.float64)
    b,ci,d,h,ww=x.shape;co=args['Cout_per_group'];ks=args['K'];st=args['Stride'];pad=args['Padding']
    y=np.zeros(args['Out'].shape,np.float64)
    weights=w.reshape(ks,ks,ks,ci,co)
    for iz in range(d):
        for iy in range(h):
            for ix in range(ww):
                for kz in range(ks):
                    for ky in range(ks):
                        for kx in range(ks):
                            oz,oy,ox=iz*st-pad+kz,iy*st-pad+ky,ix*st-pad+kx
                            if 0<=oz<y.shape[2] and 0<=oy<y.shape[3] and 0<=ox<y.shape[4]:
                                y[:,:,oz,oy,ox]+=x[:,:,iz,iy,ix]@weights[kz,ky,kx]
    y+=args['Bias'][None,:,None,None,None]
    return {'Out':y.astype(args['Out'].dtype)}
def make_case(shape=None, dtype=None, seed=0):
    shape = tuple(SHAPES[0] if shape is None else shape)
    dtype = DTYPES[0] if dtype is None else np.dtype(dtype).name
    if shape not in SHAPES or dtype not in DTYPES:
        raise ValueError((shape, dtype))
    from case_utils import fast_rng
    rng = fast_rng(seed)
    b,ci,co,d,h,w,st,pad=shape
    ks=2;od,oh,ow=(d-1)*st-2*pad+ks,(h-1)*st-2*pad+ks,(w-1)*st-2*pad+ks
    args={'X':rng.normal(0,0.3,(b,ci,d,h,w)).astype(dtype),'W':rng.normal(0,0.3,(ks**3,ci,co)).astype(dtype),'Bias':rng.normal(0,0.2,co).astype(dtype),'Out':np.zeros((b,co,od,oh,ow),dtype=dtype),'stride_xn':ci*d*h*w,'stride_xc':d*h*w,'stride_xd':h*w,'stride_xh':w,'stride_xw':1,'stride_wk_k':ci*co,'stride_wk_cin':co,'stride_wk_cout':1,'stride_on':co*od*oh*ow,'stride_oc':od*oh*ow,'stride_od':oh*ow,'stride_oh':ow,'stride_ow':1,'Cin_per_group':ci,'Cout_per_group':co,'Groups':1,'Din':d,'Hin':h,'Win':w,'Dout':od,'Hout':oh,'Wout':ow,'K':ks,'Stride':st,'Padding':pad}
    meta = {'BLOCK_H':4,'BLOCK_W':4,'BLOCK_CIN':16,'BLOCK_COUT':16,'HAS_BIAS':True}
    expected = ref(args, meta)
    return {"kernel": makora_transposed_conv3d_kernel, "args": args, "meta": meta, "grid": (triton.cdiv(ow,4)*triton.cdiv(oh,4),triton.cdiv(co,16),b*od), "outputs": ('Out',), "expected": expected, "comparison": {k: {"exact": v.dtype.kind in "biu", "rtol": 0.002, "atol": 0.0003} for k, v in expected.items()}}


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
