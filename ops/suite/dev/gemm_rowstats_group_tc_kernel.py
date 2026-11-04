"""gemm_rowstats_group_tc_kernel: GEMM + bias,顺带算每行的 sum 与 max。

模式: 2D grid(M 方向一块、N 方向一组 GROUP_N 个 tile),每个 program 在自己的
GROUP_N 个 N tile 上:块内沿 K 分块 tl.dot(USE_TC 时把 a/w 先转 fp16 走 TensorCore,
否则 fp32),加 bias 后按行求 sum 与 max 并累加;组间用 tl.atomic_add /
tl.atomic_max 把每行的 sum/max 归并到 SUM/MAX。

文件只有两层:
  ① gemm_rowstats_group_tc_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/gemm_rowstats_group_tc_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'atomic.add', 'atomic.max', 'control.if_constexpr', 'control.loop_runtime_bound', 'creation.arange', 'creation.full', 'linalg.dot', 'memory.load.masked', 'reduce.max.axis1', 'reduce.sum.axis1']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 348281, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "0d1b9853d0cd645b5a0e7cd01a3579f68ba324f691b9b1b3a3a239eebfa13fe5"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def gemm_rowstats_group_tc_kernel(A_ptr, W_ptr, B_ptr, SUM_ptr, MAX_ptr, M, N, K, NTILES, stride_am, stride_ak, stride_wn, stride_wk, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr, GROUP_N: tl.constexpr, USE_TC: tl.constexpr):
    pid_m = tl.program_id(0)
    pid_ng = tl.program_id(1)
    offs_m = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    offs_k = tl.arange(0, BLOCK_K)
    row_sum_acc = tl.zeros((BLOCK_M,), dtype=tl.float32)
    row_max_acc = tl.full((BLOCK_M,), -float('inf'), dtype=tl.float32)
    for g in range(0, GROUP_N):
        tile_n = pid_ng * GROUP_N + g
        offs_n = tile_n * BLOCK_N + tl.arange(0, BLOCK_N)
        n_mask = offs_n < N
        acc = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)
        a_ptrs = A_ptr + (offs_m[:, None] * stride_am + offs_k[None, :] * stride_ak)
        w_ptrs = W_ptr + (offs_n[None, :] * stride_wn + offs_k[:, None] * stride_wk)
        for k0 in range(0, K, BLOCK_K):
            a = tl.load(a_ptrs, mask=(offs_m[:, None] < M) & (k0 + offs_k[None, :] < K), other=0.0)
            w = tl.load(w_ptrs, mask=(offs_n[None, :] < N) & (k0 + offs_k[:, None] < K), other=0.0)
            if USE_TC:
                acc += tl.dot(a.to(tl.float16), w.to(tl.float16))
            else:
                acc += tl.dot(a, w)
            a_ptrs += BLOCK_K * stride_ak
            w_ptrs += BLOCK_K * stride_wk
        bias = tl.load(B_ptr + offs_n, mask=n_mask, other=0.0)
        acc += bias[None, :]
        acc_for_sum = tl.where(n_mask[None, :], acc, 0.0)
        acc_for_max = tl.where(n_mask[None, :], acc, -float('inf'))
        row_sum_tile = tl.sum(acc_for_sum, axis=1)
        row_max_tile = tl.max(acc_for_max, axis=1)
        row_sum_acc += row_sum_tile
        row_max_acc = tl.maximum(row_max_acc, row_max_tile)
    m_mask = offs_m < M
    tl.atomic_add(SUM_ptr + offs_m, row_sum_acc, mask=m_mask)
    tl.atomic_max(MAX_ptr + offs_m, row_max_acc, mask=m_mask)

# ------------------------------------------------------------------ ② case 层
# 典型用法:GEMM 之后要行的 sum/max(softmax 分母、BN 统计等),用 TensorCore 版
# 做累加。原始程序是 (tokens, hidden) 的投影;这里取 M=64、N=512、K=256。
#
# (M, N, K):
#   典型  (64, 512, 256)  USE_TC=True:fp16 输入的 TensorCore dot
#   规模  (128, 512, 256) 典型规模 ×2:dim0 64->128;USE_TC=True
#   泛化  (37, 200, 100)  M/N/K 都不整除 BLOCK:三处掩码
#         (16, 32, 32)    退化:单 tile,USE_TC=False 的 fp32 分支
SHAPES = ((64, 128, 128), (128, 128, 128))
_USE_TC = {(64, 128, 128): True, (128, 128, 128): True, (37, 200, 100): True, (16, 32, 32): False}
# dot 用例含 fp16/bf16;fp32 输入走 USE_TC=False 的 fp32 dot 分支。SUM/MAX 是
# f32 缓冲区(tl.atomic_add/atomic_max 在本机 Triton 上不支持半精度指针)。
DTYPES = ('float32',)
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}
BLOCK_M, BLOCK_N, BLOCK_K, GROUP_N = 32, 32, 32, 4


def ref(args, meta):
    """numpy 对照:float64 的 GEMM+bias,再按行求 sum/max。"""
    m, n, k = int(args["M"]), int(args["N"]), int(args["K"])
    a = np.asarray(args["A_ptr"], dtype=np.float64).reshape(m, k)
    w = np.asarray(args["W_ptr"], dtype=np.float64).reshape(n, k)
    b = np.asarray(args["B_ptr"], dtype=np.float64)
    acc = a @ w.T + b[None, :]
    out_s = np.asarray(args["SUM_ptr"])
    out_m = np.asarray(args["MAX_ptr"])
    return {"SUM_ptr": acc.sum(axis=1).astype(out_s.dtype),
            "MAX_ptr": acc.max(axis=1).astype(out_m.dtype)}


def _make_case(shape=SHAPES[0], dtype="float16", seed=0):
    m, n, k = (int(v) for v in shape)
    if min(m, n, k) < 16:
        raise ValueError(f"shape must be >= 16 on all dims, got {shape}")
    host = _HOST_DTYPE[dtype]
    use_tc = _USE_TC[(m, n, k)] and dtype != "float32"

    from case_utils import fast_rng
    rng = fast_rng(seed)
    a = (rng.integers(-16, 16, (m, k), dtype=np.int16) / 16).astype(host)
    w = (rng.integers(-16, 16, (n, k), dtype=np.int16) / 16).astype(host)
    b = (rng.integers(-8, 9, n, dtype=np.int16) / 16).astype(host)
    # 语义边界:第 0 行 A 全 0(该行输出 = bias,sum/max 都只由 bias 决定)。
    a[0, :] = 0.0
    b[:] = 0.0

    # 行统计的输出缓冲永远是 f32,与输入精度无关。
    out_dtype = np.float32
    args = {"A_ptr": a.reshape(-1), "W_ptr": w.reshape(-1), "B_ptr": b,
            "SUM_ptr": np.zeros(m, dtype=out_dtype),
            "MAX_ptr": np.full(m, -np.inf, dtype=out_dtype),
            "M": np.int32(m), "N": np.int32(n), "K": np.int32(k),
            "NTILES": np.int32((n + BLOCK_N - 1) // BLOCK_N),
            "stride_am": np.int32(k), "stride_ak": np.int32(1),
            "stride_wn": np.int32(k), "stride_wk": np.int32(1)}
    meta = {"BLOCK_M": BLOCK_M, "BLOCK_N": BLOCK_N, "BLOCK_K": BLOCK_K,
            "GROUP_N": GROUP_N, "USE_TC": use_tc}
    grid = ((m + BLOCK_M - 1) // BLOCK_M,
            ((n + BLOCK_N - 1) // BLOCK_N + GROUP_N - 1) // GROUP_N)
    case = {"args": args, "meta": meta, "grid": grid,
            "outputs": ("SUM_ptr", "MAX_ptr"), "expected": ref(args, meta)}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {name: "bfloat16" for name in
                                  ("A_ptr", "W_ptr", "B_ptr")}
    case["comparison"] = {name: {"comparator": "allclose", "exact": False,
                                 "rtol": 5e-3, "atol": 5e-3, "equal_nan": True}
                          for name in ("SUM_ptr", "MAX_ptr")}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, gemm_rowstats_group_tc_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float32'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float16': 'float16', 'bfloat16': 'bfloat16', 'float32': 'float32'}


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
