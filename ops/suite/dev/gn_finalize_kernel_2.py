"""gn_finalize_kernel_2: GroupNorm 统计收尾,每组先累积 NUM_BLOCKS 个 partial。

模式: 每个 program 处理一组,用 tl.range(NUM_BLOCKS) 的运行时循环把该组的
sums/sumsq partial 累加(M 是每组元素数,运行时标量),再算 mean、var 与
rstd = 1/sqrt(var+eps)。循环上界来自运行时参数,不是 constexpr。

文件只有两层:
  ① gn_finalize_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/gn_finalize_kernel_2', "group": 'basic', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.loop_runtime_bound', 'math.sqrt', 'memory.load', 'memory.store']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 371996, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "84fb0c00ea942650cd554d93d7690ab38feda0a71f0b0d35505cc00ded7ffb25"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def gn_finalize_kernel(sums_ptr, sumsq_ptr, mean_ptr, rstd_ptr, M, eps, NUM_BLOCKS):
    pid = tl.program_id(0)
    s = 0.0
    s2 = 0.0
    base = pid * NUM_BLOCKS
    for i in tl.range(NUM_BLOCKS):
        s += tl.load(sums_ptr + base + i)
        s2 += tl.load(sumsq_ptr + base + i)
    mean = s / M
    var = s2 / M - mean * mean
    rstd = 1.0 / tl.sqrt(var + eps)
    tl.store(mean_ptr + pid, mean)
    tl.store(rstd_ptr + pid, rstd)

# ------------------------------------------------------------------ ② case 层
# 典型用法:GroupNorm(16 组)收尾。原始 (128, 64, 128, 128) fp32:NG = N*G =
# 128*16 = 2048 组,每组元素 M = (C/G)*H*W = 4*128*128 = 65536,按
# BLOCK_HW=1024 切成 NUM_BLOCKS = 16 个 partial。grid = (NG,)。
#
# (NG,):
#   典型  (2048,)  原始 NG = batch 128 x 16 组
#   规模  (4096,)  典型规模 ×2:dim0 2048->4096
#   规模  (6144,)  典型规模 ×3:dim0 2048->6144
#   泛化  (17,)    组数不是 2 的幂
#         (1,)     退化:单组
SHAPES = ((128,), (17,), (1,))
# tl.sqrt 在本机 Triton 上只接受 fp32;partial 缓冲区也是 f32。
DTYPES = ('float32', 'float16', 'bfloat16')
M = 4 * 128 * 128         # 每组元素数 = (C/G) * H * W
NUM_BLOCKS = 16           # HW=16384 按 BLOCK_HW=1024 切块
EPS = 1e-5


def ref(args, meta):
    """numpy 对照:按组累加 partial,再算 mean / var / rstd。"""
    s = np.asarray(args["sums_ptr"], dtype=np.float64).sum(axis=1)
    ss = np.asarray(args["sumsq_ptr"], dtype=np.float64).sum(axis=1)
    M = np.float64(args["M"])
    mean = s / M
    var = ss / M - mean * mean
    rstd = 1.0 / np.sqrt(var + np.float64(args["eps"]))
    out = np.asarray(args["mean_ptr"])
    return {"mean_ptr": mean.astype(out.dtype), "rstd_ptr": rstd.astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    ng = int(shape[0])
    if ng <= 0:
        raise ValueError(f"NG must be positive, got {shape}")

    # 原始输入是 rand 的 [0,1):每组均值 0.5、方差 1/12。直接按 (mean, var) 造
    # partial 的组内和,再均分到 NUM_BLOCKS 个 partial 上,量级与原程序一致。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    mean = (rng.integers(16, 49, ng, dtype=np.int32) / 64.0)
    var = (rng.integers(4, 33, ng, dtype=np.int32) / 256.0)
    # partial 布局是 (NG, NUM_BLOCKS):每组的和均分到 NUM_BLOCKS 个 partial 上。
    s = np.broadcast_to(((M * mean) / NUM_BLOCKS)[:, None], (ng, NUM_BLOCKS)).copy()
    ss = np.broadcast_to(((M * (var + mean * mean)) / NUM_BLOCKS)[:, None],
                         (ng, NUM_BLOCKS)).copy()
    # 语义边界:var 为 0 的组(全同值,rstd = 1/sqrt(eps));mean=0 的组。
    s[0], ss[0] = M * 0.5 / NUM_BLOCKS, M * 0.25 / NUM_BLOCKS
    if ng > 1:
        s[1], ss[1] = 0.0, M * (1.0 / 12.0) / NUM_BLOCKS

    args = {"sums_ptr": s.astype(np.float32), "sumsq_ptr": ss.astype(np.float32),
            "mean_ptr": np.zeros(ng, dtype=np.float32),
            "rstd_ptr": np.zeros(ng, dtype=np.float32),
            "M": np.float32(M), "eps": np.float32(EPS),
            "NUM_BLOCKS": np.int32(NUM_BLOCKS)}
    meta = {}
    return {"args": args, "meta": meta, "grid": (ng,), "outputs": ("mean_ptr", "rstd_ptr"),
            "expected": ref(args, meta)}


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
