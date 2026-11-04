"""min_reduce_lastdim_partials_kernel: 最后一维分块求最小,用 atomic_min 归并。

模式: 2D grid(行、N 方向的分块),块内 load(M 维用 stride_m 定位)后被
tl.min(axis=0) 归约成标量,再用 tl.atomic_min 与其它块合并到该行的一个标量。
N 是 constexpr,块宽 BLOCK_N 覆盖尾部掩码(other=+inf)。

文件只有两层:
  ① _min_reduce_lastdim_partials_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'medium/min_reduce_lastdim_partials_kernel', "group": 'medium', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'creation.arange', 'memory.load.masked', 'atomic.min', 'reduce.min.axis0']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 85086, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "377b40e7bd11a3286256f4e244d1f5b3415591f794828b77d01f398db2666aec"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def _min_reduce_lastdim_partials_kernel(x_ptr, out_ptr, M: tl.constexpr, N: tl.constexpr, stride_m: tl.constexpr, BLOCK_N: tl.constexpr):
    pid_m = tl.program_id(0)
    pid_b = tl.program_id(1)
    row = pid_m
    block_start = pid_b * BLOCK_N
    offs = block_start + tl.arange(0, BLOCK_N)
    base = row * stride_m
    x = tl.load(x_ptr + base + offs, mask=offs < N, other=float('inf')).to(tl.float32)
    v = tl.min(x, axis=0)
    tl.atomic_min(out_ptr + row, v)

# ------------------------------------------------------------------ ② case 层
# 典型用法:逐行(最后一维 = 特征维)的最小值归约,分块是为了放下大特征维。
# 原始 (128, 4096, 4095) fp32 => M = 128*4096 行、N = 4095;这里把 M 缩到 1024,
# 保留 N = 4095(不是 2 的幂,正好走尾部掩码)。
#
# (M, N):
#   典型  (1024, 4095)  N 与原始一致,行数缩到 1024
#   规模  (2048, 4095)  典型规模 ×2:dim0 1024->2048
#   规模  (1024, 8190)  典型规模 ×2:dim1 4095->8190
#   泛化  (17, 1000)    两个维度都不是 2 的幂
#         (1, 1)       退化:单元素
SHAPES = ((128, 127), (17, 100), (1, 1))
# tl.atomic_min 在本机 Triton 上不接受半精度指针(原始 partial 缓冲区也是 f32),
# 所以合法域只有 fp32。
DTYPES = ('float32',)
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}
BLOCK_N = 1024


def ref(args, meta):
    """numpy 对照:按行取最小值(原子归并与顺序无关)。"""
    m, n = int(meta["M"]), int(meta["N"])
    x = np.asarray(args["x_ptr"]).reshape(m, n)
    out = np.asarray(args["out_ptr"])
    return {"out_ptr": x.min(axis=1).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    m, n = (int(v) for v in shape)
    if m <= 0 or n <= 0:
        raise ValueError(f"shape must be positive (M, N), got {shape}")
    host = _HOST_DTYPE[dtype]

    # 数据是标准化后的特征(1/16 网格上的正态值),最小值集中在 -1~-4。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (np.clip(np.rint(rng.standard_normal((m, n), dtype=np.float32) * 32),
                 -128, 127) / 16).astype(host)
    # 语义边界:第 0 行整行并列(全 2)、第 1 行的最小值放在最后一列(块尾 + 尾部掩码边界)。
    x[0, :] = 2.0
    if m > 1:
        x[1, :] = 0.0
        x[1, -1] = -8.0

    # out_ptr 必须从 +inf 起:atomic_min 只能往下合并,用 0 初始化会让所有正的
    # 行最小值错成 0。
    out_dtype = np.float32 if dtype == "bfloat16" else np.dtype(dtype)
    args = {"x_ptr": x.reshape(-1), "out_ptr": np.full(m, np.inf, dtype=out_dtype),
            "stride_m": np.int32(n)}
    meta = {"M": m, "N": n, "BLOCK_N": BLOCK_N}
    return {"args": args, "meta": meta,
            "grid": (m, (n + BLOCK_N - 1) // BLOCK_N), "outputs": ("out_ptr",),
            "expected": ref(args, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, _min_reduce_lastdim_partials_kernel, DTYPES,
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
