"""makora_deconv3d_leaky_pool_kernel: 取自 makora 数据集 test split 第 22715 行(上游 kernel deconv3d_fused_pool_kernel)。

模式: args.runtime_scalar、atomic.masked、atomic.max、control.for_range、control.loop_carried、creation.arange、creation.where、creation.zeros、memory.load、memory.load.masked。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。循环上界来自运行时标量(不是 constexpr)。constexpr 参数: BLOCK_M, BLOCK_OC。

文件只有两层:
  ① makora_deconv3d_leaky_pool_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/deconv3d_leaky_pool', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'atomic.masked', 'atomic.max', 'control.for_range', 'control.loop_carried', 'creation.arange', 'creation.where', 'creation.zeros', 'memory.load', 'memory.load.masked', 'memory.load.other', 'tile.2d']}
SOURCE = {'dataset': 'makora-ai/triton-gpu-latency', 'revision': '3b30911350fa433e1cb97ec2a41bd8908dd35d5d', 'file': 'data/test.parquet', 'row': 22715, 'source_sha256': '3da09ef84a1b947a028492a448e242c9852351eea08c98d7e30b160151e5d24a', 'upstream_kernel': 'deconv3d_fused_pool_kernel', 'upstream_latency_label': 77.3889390563965, 'license': 'Apache-2.0', 'adaptations': ['rename JIT entry', 'replace torch host wrapper with independent NumPy case/ref', 'select explicit legal launch tile'], 'extraction_scope': 'original single JIT kernel stage, not the entire original PyTorch Model'}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def makora_deconv3d_leaky_pool_kernel(x_ptr, w_ptr, b_ptr, mult_ptr, y_ptr, N, Ci, Co, Di, Hi, Wi, Do, Ho, Wo, kD, kH, kW, stride, pad, neg_slope, BLOCK_M: tl.constexpr, BLOCK_OC: tl.constexpr):
    pid_m = tl.program_id(0)
    pid_oc = tl.program_id(1)
    offs_m = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    offs_oc = pid_oc * BLOCK_OC + tl.arange(0, BLOCK_OC)
    total_M = N * Do * Ho * Wo
    mask_m = offs_m < total_M
    mask_oc = offs_oc < Co
    e = offs_m
    x_out = e % Wo
    e = e // Wo
    y_out = e % Ho
    e = e // Ho
    z_out = e % Do
    n = e // Do
    bias = tl.load(b_ptr + offs_oc, mask=mask_oc, other=0.0)
    out_acc = tl.zeros((BLOCK_M, BLOCK_OC), dtype=tl.float32) + bias[None, :]
    sN_x = Ci * Di * Hi * Wi
    sC_x = Di * Hi * Wi
    sD_x = Hi * Wi
    sH_x = Wi
    sW_x = 1
    sCi_w = Co * kD * kH * kW
    sCo_w = kD * kH * kW
    sKd_w = kH * kW
    sKh_w = kW
    sKw_w = 1
    for ic in range(0, Ci):
        for kd in range(0, kD):
            tZ = z_out + pad - kd
            mask_z = tZ % stride == 0
            z_in = tZ // stride
            mask_z &= (z_in >= 0) & (z_in < Di)
            for kh in range(0, kH):
                tY = y_out + pad - kh
                mask_y = tY % stride == 0
                y_in = tY // stride
                mask_y &= (y_in >= 0) & (y_in < Hi)
                for kw in range(0, kW):
                    tX = x_out + pad - kw
                    mask_x = tX % stride == 0
                    x_in = tX // stride
                    mask_x &= (x_in >= 0) & (x_in < Wi)
                    mask_xyz = mask_m & mask_z & mask_y & mask_x
                    inp_idx = n * sN_x + ic * sC_x + z_in * sD_x + y_in * sH_x + x_in * sW_x
                    inp_vals = tl.load(x_ptr + inp_idx, mask=mask_xyz, other=0.0)
                    w_offs = ic * sCi_w + offs_oc * sCo_w + kd * sKd_w + kh * sKh_w + kw * sKw_w
                    w_vec = tl.load(w_ptr + w_offs, mask=mask_oc, other=0.0)
                    out_acc += inp_vals[:, None] * w_vec[None, :]
    out_acc = tl.where(out_acc > 0, out_acc, out_acc * neg_slope)
    mult = tl.load(mult_ptr + offs_oc, mask=mask_oc, other=0.0)
    out_acc = out_acc * mult[None, :]
    out_acc = tl.where(out_acc > 0, out_acc, out_acc * neg_slope)
    Do2 = Do // 2
    Ho2 = Ho // 2
    Wo2 = Wo // 2
    sN_y = Co * Do2 * Ho2 * Wo2
    sC_y = Do2 * Ho2 * Wo2
    sD_y = Ho2 * Wo2
    sH_y = Wo2
    sW_y = 1
    z2 = z_out // 2
    y2 = y_out // 2
    x2 = x_out // 2
    out_base = n * sN_y + z2 * sD_y + y2 * sH_y + x2 * sW_y
    y_ptrs = y_ptr + out_base[:, None] + offs_oc[None, :] * sC_y
    tl.atomic_max(y_ptrs, out_acc, mask=mask_m[:, None] & mask_oc[None, :])

# ------------------------------------------------------------------ ② case 层
# 典型用法依据:数据集原始程序的常量(已按 sha256 核对原始文件):
#   batch_size = 16
#   in_channels = 16
#   out_channels = 32
#   kernel_size = 3
#   stride = 2
#   padding = 1
# 下面 SHAPES 只缩小了这些配置里的批类维度,结构维度按原值保留。
# (shape,) 的角色:第一个是典型用法,其余是泛化/尾块/退化用例。
#   (1, 2, 3, 2, 2, 2)
#   (1, 3, 5, 3, 2, 2)
#   (3, 2, 3, 2, 2, 2)
# DTYPES: float32 —— 原始用途的 dtype 在前;非法域(例如本机 Triton 只吃 fp32 的exp/sqrt/erf/atomic)的算子只声明合法的那一种。
#   规模    (2, 2, 3, 2, 2, 2)  典型规模 ×2:dim0 1->2
#   规模    (1, 2, 6, 2, 2, 2)  典型规模 ×2:dim2 3->6

SHAPES = ((1, 2, 3, 2, 2, 2), (2, 2, 3, 2, 2, 2), (1, 3, 5, 3, 2, 2))
DTYPES = ('float32',)
def ref(args, meta):
    x=args['x_ptr'].astype(np.float64);w=args['w_ptr'].astype(np.float64)
    b,ci,d,h,ww=x.shape;co=args['Co'];kd,kh,kw=args['kD'],args['kH'],args['kW'];st=args['stride'];pad=args['pad']
    y=np.zeros((b,co,args['Do'],args['Ho'],args['Wo']),np.float64)
    for iz in range(d):
        for iy in range(h):
            for ix in range(ww):
                for z in range(kd):
                    for yy in range(kh):
                        for xx in range(kw):
                            oz,oy,ox=iz*st-pad+z,iy*st-pad+yy,ix*st-pad+xx
                            if 0<=oz<y.shape[2] and 0<=oy<y.shape[3] and 0<=ox<y.shape[4]:
                                y[:,:,oz,oy,ox]+=x[:,:,iz,iy,ix]@w[:,:,z,yy,xx]
    y+=args['b_ptr'][None,:,None,None,None]
    y=np.where(y>0,y,y*args['neg_slope'])*args['mult_ptr'][None,:,None,None,None]
    y=np.where(y>0,y,y*args['neg_slope'])
    y=y.reshape(b,co,y.shape[2]//2,2,y.shape[3]//2,2,y.shape[4]//2,2).max(axis=(3,5,7))
    return {'y_ptr':y.astype(np.float32)}
def make_case(shape=None, dtype=None, seed=0):
    shape = tuple(SHAPES[0] if shape is None else shape)
    dtype = DTYPES[0] if dtype is None else np.dtype(dtype).name
    if shape not in SHAPES or dtype not in DTYPES:
        raise ValueError((shape, dtype))
    from case_utils import fast_rng
    rng = fast_rng(seed)
    b,ci,co,d,h,w=shape
    ks=2;st=2;pad=0;od,oh,ow=d*2,h*2,w*2
    args={'x_ptr':rng.normal(0,0.3,(b,ci,d,h,w)).astype(dtype),'w_ptr':rng.normal(0,0.3,(ci,co,ks,ks,ks)).astype(dtype),'b_ptr':rng.normal(0,0.2,co).astype(dtype),'mult_ptr':rng.uniform(-1.5,1.5,co).astype(dtype),'y_ptr':np.full((b,co,od//2,oh//2,ow//2),-np.inf,np.float32),'N':b,'Ci':ci,'Co':co,'Di':d,'Hi':h,'Wi':w,'Do':od,'Ho':oh,'Wo':ow,'kD':ks,'kH':ks,'kW':ks,'stride':st,'pad':pad,'neg_slope':0.2}
    meta = {'BLOCK_M':16,'BLOCK_OC':8}
    expected = ref(args, meta)
    return {"kernel": makora_deconv3d_leaky_pool_kernel, "args": args, "meta": meta, "grid": (triton.cdiv(b*od*oh*ow,16),triton.cdiv(co,8)), "outputs": ('y_ptr',), "expected": expected, "comparison": {k: {"exact": v.dtype.kind in "biu", "rtol": 0.0005, "atol": 5e-05} for k, v in expected.items()}}


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
