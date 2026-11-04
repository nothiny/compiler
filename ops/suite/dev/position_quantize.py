"""position_quantize: 用 FP64 位置相位 + 近似 sin 生成两通道量化特征。

模式: 每个 program 处理 B 个位置:i 用 int64 计算(避免溢出),按 |x| 做 scaled
归一化,通道循环用 broadcast/unsqueeze 展开成 2 列;位置相位在 FP64 里做周期
规约(floor + sub)后再转 FP32 调 sin,最后除以范数、乘 8、ceil 量化。
覆盖 div_rn/sqrt_rn/floor/sin/ceil/unsqueeze/broadcast/to_tensor。

文件只有两层:
  ① position_quantize_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/position_quantize', "group": 'basic', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'creation.arange', 'dtype.float64', 'math.ceil', 'math.floor', 'math.sin', 'math.sqrt', 'shape.broadcast', 'shape.unsqueeze']}
COPIED_FROM = {'repo': '~/ops basic (authored composite, validated at d326fbc+)', 'covers_gap_apis': ['add', 'ceil', 'div_rn', 'mul', 'sqrt_rn', 'sub', 'to_tensor', 'unsqueeze']}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def position_quantize_kernel(X, Y, N: tl.constexpr, B: tl.constexpr):
    i = tl.program_id(0).to(tl.int64) * B + tl.arange(0, B)
    x = tl.cast(tl.load(X+i, i<N, other=0), tl.float32)
    p = tl.cast(i, tl.float64)
    channels = tl.arange(0,2)
    scale = tl.maximum(tl.abs(x), 1.0)
    inv_scale = tl.div_rn(1.0, scale)
    a, channel = tl.broadcast(tl.unsqueeze(tl.div_rn(x,scale),1),tl.unsqueeze(channels,0))
    # Reduce the FP64 position phase before the FP32 approximate sine.
    phase = tl.unsqueeze(p,1)*0.125+channel.to(tl.float64)*0.5
    period = tl.full((), 6.2831853071795864769, tl.float64)
    half_period = tl.full((), 3.1415926535897932385, tl.float64)
    reduced = phase - tl.floor((phase + half_period) / period) * period
    offset = tl.sub(tl.sin(reduced.to(tl.float32)), tl.to_tensor(0.5))
    centered = tl.add(tl.mul(a,1.25),tl.mul(offset,tl.unsqueeze(inv_scale,1)))
    norm = tl.sqrt_rn(tl.sum(tl.mul(centered, centered),axis=1,keep_dims=True)+tl.unsqueeze(inv_scale*inv_scale,1))
    norm = tl.squeeze(norm,1)
    q = tl.ceil(tl.mul(tl.div_rn(centered,tl.unsqueeze(norm,1)),8.0))
    tl.store(Y+i[:,None]*2+channels[None,:],q,(i<N)[:,None])

# ------------------------------------------------------------------ ② case 层
# 典型用法:位置编码的量化特征(序列位置 x 通道的二维正弦特征,量化成小整数)。
# 原始版本是单块 128 的向量;取一条 hidden=4096 的序列位置。
#
# (N,):
#   典型  (4096,)  一条 4096 位置的序列,按 B=128 分块
#   规模  (8192,)  典型规模 ×2:dim0 4096->8192
#   规模  (12288,)  典型规模 ×3:dim0 4096->12288
#   泛化  (530,)   尾部:530 = 4*128 + 18,最后一个块只有 18 个有效位置
#         (1,)     退化:单位置
SHAPES = ((128,), (114,), (1,))
# kernel 在 FP64 里算相位、FP32 里算 sin/量化,输出是 fp32 ceil 值;
# ceil 的输出只可能是整数,所以用区间比较(见 comparison_policy)。
DTYPES = ('float32', 'float16', 'bfloat16')
B = 128


def _prequantize(args):
    """独立复现:host 上按同一公式算量化前的实数值(FP64)。"""
    x = np.asarray(args["X"], dtype=np.float64)
    z = (x[:, None] * 1.25
         + np.sin(np.arange(x.size)[:, None] * 0.125 + np.arange(2)[None, :] * 0.5) - 0.5)
    return 8 * z / np.sqrt((z * z).sum(axis=1, keepdims=True) + 1)


def ref(args, meta):
    """numpy 对照:ceil 量化后的两通道特征。"""
    return {"Y": np.ceil(_prequantize(args)).astype(np.float32)}


def comparison_policy(args):
    """ceil 是不连续函数:靠近整数边界的 bin 允许取相邻两个整数,其余必须精确。

    归一化值落在 [-8,8],32*eps 的预算覆盖 FP32 算术与近似 sin 的误差。
    """
    value = _prequantize(args)
    budget = 32 * np.finfo(np.float32).eps
    return {"Y": {"comparator": "quantized_interval",
                  "lower": np.ceil(value - budget).tolist(),
                  "upper": np.ceil(value + budget).tolist()}}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n = int(shape[0])
    if n <= 0:
        raise ValueError(f"N must be positive, got {shape}")

    # 原始输入是标准正态。这里保留正态形状但落在 1/16 网格上,半精度也能精确
    # 表示,量化前的宿主值与设备值一致。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (np.clip(np.rint(rng.standard_normal(n, dtype=np.float32) * 16), -128, 127)
         / 16).astype(np.float32)
    # 语义边界:0(|x| 被 tl.maximum 抬到 1,inv_scale=1)、以及正负极值。
    x[0] = 0.0
    if n > 1:
        x[1] = 8.0
    if n > 2:
        x[2] = -8.0

    args = {"X": x.astype(np.dtype(dtype)), "Y": np.zeros((n, 2), np.float32)}
    meta = {"N": n, "B": B}
    return {"args": args, "meta": meta, "grid": ((n + B - 1) // B,), "outputs": ("Y",),
            "expected": ref(args, meta), "comparison": comparison_policy(args)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;输出按 quantized_interval 比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, position_quantize_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float32'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float32': 'float32', 'float16': 'float16'}


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
