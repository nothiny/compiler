"""gn_finalize_kernel: GroupNorm 的统计收尾,二维 grid (N, G)。

模式: program_id(0)=n、program_id(1)=g,idx = n*num_programs(1)+g 定位该组的
sum/sumsq,count 是每组元素数(运行时标量),算 mean 与 var,再用 tl.rsqrt 求
rstd。它是"BN+tanh+pool+GN"复合模型里 GN 段的第二级。

文件只有两层:
  ① gn_finalize_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/gn_finalize_kernel', "group": 'basic', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'math.rsqrt', 'memory.load', 'memory.store', 'args.program_id.nd']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 189147, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "1ba510767779f526988e8a9f56e05939740335ea3358cdee1d889272fe8fcc8d"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def gn_finalize_kernel(gsum_ptr, gsumsq_ptr, mean_ptr, rstd_ptr, count, eps):
    pid_n = tl.program_id(0)
    pid_g = tl.program_id(1)
    idx = pid_n * tl.num_programs(1) + pid_g
    s = tl.load(gsum_ptr + idx)
    ss = tl.load(gsumsq_ptr + idx)
    mean = s / count
    var = ss / count - mean * mean
    rstd = tl.rsqrt(var + eps)
    tl.store(mean_ptr + idx, mean)
    tl.store(rstd_ptr + idx, rstd)

# ------------------------------------------------------------------ ② case 层
# 典型用法:GroupNorm 收尾。原始 (512, 64, 32, 32) fp32,G = 8 组,N = batch 512
# => grid = (512, 8),每组 count = (64/8)*32*32 = 8192。
#
# (N, G):
#   典型  (512, 8)   原始 batch 512 x 8 组;count 由 meta 传入
#   规模  (1024, 8)  典型规模 ×2:dim0 512->1024
#   规模  (512, 16)  典型规模 ×2:dim1 8->16
#   泛化  (7, 3)     两个维度都不是 2 的幂(2D grid 的行优先布局)
#         (1, 1)     退化:单组
SHAPES = ((128, 8), (7, 3), (1, 1))
# tl.rsqrt 在本机 Triton 上只接受 fp32;stage-1 的 sum/sumsq 也是 f32。
DTYPES = ('float32', 'float16', 'bfloat16')
COUNT = 8192             # 每组元素数 = (C/G) * H * W = 8 * 32 * 32
EPS = 1e-5


def ref(args, meta):
    """numpy 对照:float64 复现 mean / var / rstd。"""
    s = np.asarray(args["gsum_ptr"], dtype=np.float64)
    ss = np.asarray(args["gsumsq_ptr"], dtype=np.float64)
    count = np.float64(args["count"])
    mean = s / count
    var = ss / count - mean * mean
    rstd = 1.0 / np.sqrt(var + np.float64(args["eps"]))
    out = np.asarray(args["mean_ptr"])
    return {"mean_ptr": mean.astype(out.dtype), "rstd_ptr": rstd.astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n, g = (int(v) for v in shape)
    if n <= 0 or g <= 0:
        raise ValueError(f"shape must be (N > 0, G > 0), got {shape}")

    # 原始输入是 rand 的 [0,1):均值 0.5、方差 1/12。按 (mean, var) 直接造
    # sum/sumsq,mean 落在 1/64 网格上,var 取 [0.015, 0.125),与真实数据同量级。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    total = n * g
    mean = (rng.integers(16, 49, total, dtype=np.int32) / 64.0)
    var = (rng.integers(4, 33, total, dtype=np.int32) / 256.0)
    s = COUNT * mean
    ss = COUNT * (var + mean * mean)
    # 语义边界:var 为 0 的组(rstd = 1/sqrt(eps)),以及 mean=0 的组。
    s[0], ss[0] = COUNT * 0.5, COUNT * 0.25
    if total > 1:
        s[1], ss[1] = 0.0, COUNT * (1.0 / 12.0)

    args = {"gsum_ptr": s.astype(np.float32), "gsumsq_ptr": ss.astype(np.float32),
            "mean_ptr": np.zeros(total, dtype=np.float32),
            "rstd_ptr": np.zeros(total, dtype=np.float32),
            "count": np.float32(COUNT), "eps": np.float32(EPS)}
    meta = {}
    return {"args": args, "meta": meta, "grid": (n, g),
            "outputs": ("mean_ptr", "rstd_ptr"), "expected": ref(args, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, gn_finalize_kernel, DTYPES,
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
