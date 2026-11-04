"""finalize_mean_tanh: 融合池化+hardtanh+空间均值之后的收尾,tanh 激活。

模式: 每个 program 处理一个 (n, c) 平面:读该平面的池化累加和,乘
inv_denom(= 1/(HP*WP)) 得均值,用 2*sigmoid(2x)-1 求 tanh(避免直接 tanh 的
数值问题)。它是 ConvTranspose+MaxPool+Hardtanh+mean+tanh 那条链的最后一级。

文件只有两层:
  ① _finalize_mean_tanh   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/finalize_mean_tanh', "group": 'basic', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'math.sigmoid', 'memory.load', 'memory.store']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 187795, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "730bbe724acd0535bb9147e8be4eb0d10d02320181b57f503e5554bf2d661282"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def _finalize_mean_tanh(sum_ptr, out_ptr, inv_denom):
    pid = tl.program_id(0)
    val = tl.load(sum_ptr + pid) * inv_denom
    out = 2.0 * tl.sigmoid(2.0 * val) - 1.0
    tl.store(out_ptr + pid, out)

# ------------------------------------------------------------------ ② case 层
# 典型用法:ConvTranspose2d+MaxPool2d(2,2)+Hardtanh+mean+tanh 的收尾段。
# 原始 (128, 64, 256, 256) fp32 -> 池化后 HP=WP=128,NC = 128*64 = 8192 个平面,
# inv_denom = 1/(HP*WP) = 1/16384。kernel 每个 program 处理一个平面,grid = NC。
#
# (NC,):
#   典型  (8192,)  原始 NC = batch 128 x channels 64;平面尺寸 128x128 体现在 inv_denom
#   规模  (16384,)  典型规模 ×2:dim0 8192->16384
#   规模  (24576,)  典型规模 ×3:dim0 8192->24576
#   泛化  (129,)   非 2 的幂的 program 数(尾部没有掩码问题,grid 就是 NC)
#         (1,)    退化:单平面
SHAPES = ((128,), (97,), (1,))
# tl.sigmoid 在本机 Triton 上只接受 fp32;池化累加缓冲区在原始程序里也是 f32。
DTYPES = ('float32', 'float16', 'bfloat16')
INV_DENOM = 1.0 / (128 * 128)   # 原始 HP = WP = 128


def ref(args, meta):
    """numpy 对照:float64 算均值与 tanh,再转回输出 dtype。"""
    s = np.asarray(args["sum_ptr"], dtype=np.float64)
    out = np.asarray(args["out_ptr"])
    mean = s * np.float64(args["inv_denom"])
    return {"out_ptr": np.tanh(mean).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    nc = int(shape[0])
    if nc <= 0:
        raise ValueError(f"NC must be positive, got {shape}")

    # 每个平面的累加和是 HP*WP 个 hardtanh 后(即 [-1,1])的池化值之和,量级落在
    # [-HP*WP, HP*WP];用 1/8 的网格造和,均值落在 [-2, 2] 附近,tanh 的两侧
    # 饱和区和线性区都覆盖到。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    window = float(1.0 / INV_DENOM)                 # HP*WP,即每个平面的元素数
    sums = (rng.integers(-16, 17, nc, dtype=np.int32) / 8.0) * window / 4.0
    # 语义边界: 均值 0(输出 0)、均值 1(线性区)、均值 -1(负半轴)。
    if nc > 0:
        sums[0] = 0.0
    if nc > 1:
        sums[1] = 1.0 * window
    if nc > 2:
        sums[2] = -1.0 * window
    args = {"sum_ptr": sums.astype(np.float32), "out_ptr": np.zeros(nc, dtype=np.float32),
            "inv_denom": float(INV_DENOM)}
    meta = {}
    return {"args": args, "meta": meta, "grid": (nc,), "outputs": ("out_ptr",),
            "expected": ref(args, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, _finalize_mean_tanh, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)


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
