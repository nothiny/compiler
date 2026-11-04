"""finalize_stats_kernel: GroupNorm 的统计收尾,由 sum/sumsq 求 mean 与 invstd。

模式: 每个 program 处理一个 (n, c) 平面:读 stage-1 累加的 sum 与平方和,
S 是每平面元素数(运行时标量),用 f32 算 mean 与 var = ss/S - mean^2,
var 用 tl.maximum 夹到非负(抵消 f32 抵消误差),再算 invstd = 1/sqrt(var+eps)。

文件只有两层:
  ① _finalize_stats_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/finalize_stats_kernel', "group": 'basic', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'creation.full', 'math.maximum', 'math.sqrt', 'memory.load', 'memory.store']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 56322, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "a70db896486ad603cc97e50cfd7981ec51b89ea7a83f37415a73bc6dc77cb50d"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def _finalize_stats_kernel(sum_ptr, sumsq_ptr, mean_ptr, invstd_ptr, S, eps, NC):
    pid_nc = tl.program_id(0)
    s = tl.load(sum_ptr + pid_nc)
    ss = tl.load(sumsq_ptr + pid_nc)
    S_f = tl.full([], S, tl.float32)
    mean = s / S_f
    var = tl.maximum(ss / S_f - mean * mean, 0.0)
    invstd = 1.0 / tl.sqrt(var + eps)
    tl.store(mean_ptr + pid_nc, mean)
    tl.store(invstd_ptr + pid_nc, invstd)

# ------------------------------------------------------------------ ② case 层
# 典型用法:GroupNorm 三级 kernel 的第二级。原始 (112, 64, 512, 512) fp32,
# NC = N*C = 112*64 = 7168 个平面,S = H*W = 512*512 = 262144。
# grid = (NC,),每个 program 处理一个平面。
#
# (NC,):
#   典型  (7168,)   原始 NC = batch 112 x channels 64;S = 262144 由 meta 传入
#   规模  (14336,)  典型规模 ×2:dim0 7168->14336
#   规模  (21504,)  典型规模 ×3:dim0 7168->21504
#   泛化  (129,)    program 数不是 2 的幂(grid 与 block 无关)
#         (1,)     退化:单平面
SHAPES = ((128,), (97,), (1,))
# tl.sqrt 在本机 Triton 上只接受 fp32;stage-1 的 sum/sumsq 缓冲区也是 f32。
DTYPES = ('float32', 'bfloat16')
S = 512 * 512            # 原始每平面元素数 H*W
EPS = 1e-5


def ref(args, meta):
    """numpy 对照:float64 复现 mean/var/invstd,含 var 的非负夹取。"""
    s = np.asarray(args["sum_ptr"], dtype=np.float64)
    ss = np.asarray(args["sumsq_ptr"], dtype=np.float64)
    S = np.float64(args["S"])
    mean = s / S
    var = np.maximum(ss / S - mean * mean, 0.0)
    invstd = 1.0 / np.sqrt(var + np.float64(args["eps"]))
    out = np.asarray(args["mean_ptr"])
    return {"mean_ptr": mean.astype(out.dtype), "invstd_ptr": invstd.astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    nc = int(shape[0])
    if nc <= 0:
        raise ValueError(f"NC must be positive, got {shape}")

    # 原始输入是 rand 的 [0,1):均值 0.5、方差 1/12。这里直接按 (mean, var) 造
    # sum/sumsq,取值落在 1/64 的网格上,host 与 device 看到的是同一份 f32 值。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    mean = (rng.integers(16, 49, nc, dtype=np.int32) / 64.0)      # [0.25, 0.75)
    var = (rng.integers(4, 33, nc, dtype=np.int32) / 256.0)       # [0.015, 0.125)
    s = S * mean
    ss = S * (var + mean * mean)
    # 语义边界:var 恰好为 0(全同值平面)、raw var 明显为负(tl.maximum 的夹取
    # 分支),以及 mean=0 的平面(invstd = 1/sqrt(eps))。
    s[0], ss[0] = S * 0.5, S * 0.25
    if nc > 1:
        s[1], ss[1] = S * 0.5, S * 0.25 - 0.5 * S      # raw var = -0.5 -> 夹到 0
    if nc > 2:
        s[2], ss[2] = 0.0, S * (1.0 / 12.0)
    args = {"sum_ptr": s.astype(np.float32), "sumsq_ptr": ss.astype(np.float32),
            "mean_ptr": np.zeros(nc, dtype=np.float32),
            "invstd_ptr": np.zeros(nc, dtype=np.float32),
            "S": np.int32(S), "eps": np.float32(EPS), "NC": np.int32(nc)}
    meta = {}
    return {"args": args, "meta": meta, "grid": (nc,), "outputs": ("mean_ptr", "invstd_ptr"),
            "expected": ref(args, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, _finalize_stats_kernel, DTYPES,
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
