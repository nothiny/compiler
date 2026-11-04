"""argmin_tiled_kernel: (B, M, N) 沿 M 取 argmin,按 (BLOCK_M, BLOCK_N) tile 累加。

模式: 2D grid(N 方向一块、B 一块),每个 program 处理一行 B 的一列切片:
for m_start in range(0, M, BLOCK_M) 按 M 分块 load tile,tl.min/tl.argmin(axis=0)
得列内极值,再与 (BLOCK_N,) 的 best_val/best_idx 用 tl.where 合并;N 方向有掩码。

文件只有两层:
  ① argmin_tiled_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/argmin_tiled_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.loop_runtime_bound', 'creation.arange', 'creation.full', 'hint.multiple_of', 'memory.load.masked', 'reduce.argmin']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 83493, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "b4b186e08a12421d309b4a2e2760926947e86bf95fb6f729e97d586077b9b4b6"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def argmin_tiled_kernel(x_ptr, out_ptr, stride_x_b, stride_x_m, stride_x_n, stride_out_b, stride_out_n, M, N, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr):
    pid_n = tl.program_id(0)
    pid_b = tl.program_id(1)
    offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    mask_n = offs_n < N
    tl.multiple_of(offs_n, BLOCK_N)
    base_ptr = x_ptr + pid_b * stride_x_b + offs_n * stride_x_n
    best_val = tl.full((BLOCK_N,), float('inf'), dtype=tl.float32)
    best_idx = tl.zeros((BLOCK_N,), dtype=tl.int32)
    for m_start in range(0, M, BLOCK_M):
        offs_m = m_start + tl.arange(0, BLOCK_M)
        mask_m = offs_m < M
        tile_ptr = base_ptr[None, :] + offs_m[:, None] * stride_x_m
        tile = tl.load(tile_ptr, mask=mask_m[:, None] & mask_n[None, :], other=float('inf'), eviction_policy='evict_first')
        local_min = tl.min(tile, axis=0)
        local_argmin = tl.argmin(tile, axis=0)
        is_better = local_min < best_val
        best_val = tl.where(is_better, local_min, best_val)
        best_idx = tl.where(is_better, (m_start + local_argmin).to(tl.int32), best_idx)
    out_ptrs = out_ptr + pid_b * stride_out_b + offs_n * stride_out_n
    tl.store(out_ptrs, best_idx.to(tl.int64), mask=mask_n)

# ------------------------------------------------------------------ ② case 层
# 典型用法:(B, M, N) 沿 M 取 argmin。原始程序是 3D 中间轴归约;这里保留
# N=1024 的宽、缩小 B 与 M(BLOCK_M 的整数倍/非整数倍各一例)。
#
# (B, M, N):
#   典型  (4, 128, 1024)  M 整除 BLOCK_M=32
#   规模  (8, 128, 1024)  典型规模 ×2:dim0 4->8
#   规模  (4, 128, 2048)  典型规模 ×2:dim2 1024->2048
#   泛化  (3, 17, 1000)   M、N 都不整除块宽:两个方向都有尾块
#         (1, 1, 1)       退化:单元素
SHAPES = ((4, 128, 128), (3, 17, 100), (1, 1, 1))
# 原始数据是 fp32;argmin 只是比较+选择,半精度合法。
DTYPES = ("float32", "float16", "bfloat16")
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}
BLOCK_M, BLOCK_N = 32, 64


def ref(args, meta):
    """numpy 对照:沿 axis=1 取首个最小值下标,输出 int32(与 kernel 一致)。"""
    b, m, n = int(args["M_B"]), int(args["M"]), int(args["N"])
    x = np.asarray(args["x_ptr"]).reshape(b, m, n)
    return {"out_ptr": np.argmin(x, axis=1).astype(np.int32)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    b, m, n = (int(v) for v in shape)
    if min(b, m, n) <= 0:
        raise ValueError(f"shape must be positive (B, M, N), got {shape}")

    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (np.clip(np.rint(rng.standard_normal((b, m, n), dtype=np.float32) * 32),
                 -128, 127) / 16).astype(_HOST_DTYPE[dtype])
    # 语义边界:第 0 个 batch 的第 0 列整条并列(取 0);第 1 列的最小值放在 M 的
    # 最后一个元素(分块循环的尾块)。
    x[0, :, 0] = 1.0
    if n > 1:
        x[0, :, 1] = 0.0
        x[0, -1, 1] = -8.0

    args = {"x_ptr": x.reshape(-1), "out_ptr": np.zeros((b, n), np.int32),
            "stride_x_b": np.int32(m * n), "stride_x_m": np.int32(n),
            "stride_x_n": np.int32(1), "stride_out_b": np.int32(n),
            "stride_out_n": np.int32(1), "M": np.int32(m), "N": np.int32(n),
            "M_B": np.int32(b)}
    meta = {"BLOCK_M": BLOCK_M, "BLOCK_N": BLOCK_N}
    grid = ((n + BLOCK_N - 1) // BLOCK_N, b)
    case = {"args": args, "meta": meta, "grid": grid, "outputs": ("out_ptr",),
            "expected": ref(args, meta)}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {"x_ptr": "bfloat16"}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;下标输出按位精确比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, argmin_tiled_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=True)


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float32'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float32': 'float32', 'float16': 'float16', 'bfloat16': 'bfloat16'}


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
