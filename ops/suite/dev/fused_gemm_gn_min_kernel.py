"""fused_gemm_gn_min_kernel: GEMM + bias + GroupNorm(沿 N 分组) + 行内最小值。

模式: 1D grid 的 GROUP_M swizzle GEMM(K 方向 for 循环 + tl.dot 累积 f32),加 bias
后把 N 方向 reshape 成 (N//GROUP_SIZE, GROUP_SIZE) 做组内 mean/var/rstd
(GROUP_SIZE 是 constexpr),再乘 gamma/beta,最后两次 tl.min 求每行最小值,
用 tl.atomic_min 归约到 Mins(跨 N tile 原子取最小)。

文件只有两层:
  ① fused_gemm_gn_min_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/fused_gemm_gn_min_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'atomic.min', 'control.loop_runtime_bound', 'creation.arange', 'creation.zeros', 'linalg.dot', 'math.cdiv', 'math.minimum', 'math.rsqrt', 'memory.load.masked', 'reduce.max.axis1', 'reduce.sum.axis2']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "test", "row": 23209, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "19e7894246d21e327b507f8ddca8d35058c67ac8c8d13c229db0b5aec999b3f5"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def fused_gemm_gn_min_kernel(X_ptr, W_ptr, B_ptr, Gamma_ptr, Beta_ptr, Mins_ptr, M, N, K, stride_xm, stride_xk, stride_wn, stride_wk, eps, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr, GROUP_SIZE: tl.constexpr, GROUP_M: tl.constexpr):
    pid = tl.program_id(axis=0)
    num_pid_m = tl.cdiv(M, BLOCK_M)
    num_pid_n = tl.cdiv(N, BLOCK_N)
    num_pid_in_group = GROUP_M * num_pid_n
    group_id = pid // num_pid_in_group
    first_pid_m = group_id * GROUP_M
    group_size_m = min(num_pid_m - first_pid_m, GROUP_M)
    pid_m = first_pid_m + pid % group_size_m
    pid_n = pid % num_pid_in_group // group_size_m
    offs_m = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    offs_k = tl.arange(0, BLOCK_K)
    x_ptrs = X_ptr + (offs_m[:, None] * stride_xm + offs_k[None, :] * stride_xk)
    w_ptrs = W_ptr + (offs_k[:, None] * stride_wk + offs_n[None, :] * stride_wn)
    acc = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)
    for k in range(0, K, BLOCK_K):
        x = tl.load(x_ptrs, mask=offs_m[:, None] < M)
        w = tl.load(w_ptrs, mask=offs_n[None, :] < N)
        acc += tl.dot(x, w)
        x_ptrs += BLOCK_K * stride_xk
        w_ptrs += BLOCK_K * stride_wk
    b = tl.load(B_ptr + offs_n, mask=offs_n < N)
    acc += b[None, :]
    tl.static_assert(BLOCK_N % GROUP_SIZE == 0)
    acc_3d = tl.reshape(acc, (BLOCK_M, BLOCK_N // GROUP_SIZE, GROUP_SIZE))
    mean = tl.sum(acc_3d, axis=2) / GROUP_SIZE
    diff = acc_3d - mean[:, :, None]
    var = tl.sum(diff * diff, axis=2) / GROUP_SIZE
    rstd = tl.rsqrt(var + eps)
    gamma = tl.load(Gamma_ptr + offs_n, mask=offs_n < N)
    beta = tl.load(Beta_ptr + offs_n, mask=offs_n < N)
    gamma_3d = tl.reshape(gamma, (1, BLOCK_N // GROUP_SIZE, GROUP_SIZE))
    beta_3d = tl.reshape(beta, (1, BLOCK_N // GROUP_SIZE, GROUP_SIZE))
    out = diff * rstd[:, :, None]
    out = out * gamma_3d + beta_3d
    min_g = tl.min(out, axis=2)
    min_row = tl.min(min_g, axis=1)
    tl.atomic_min(Mins_ptr + offs_m, min_row, mask=offs_m < M)

# ------------------------------------------------------------------ ② case 层
# 典型用法:Transformer 的 FFN 投影 + GroupNorm(沿特征维分组)+ 每行最小值
# (激活健康度指标)。原始程序是 (tokens, hidden) 的投影;这里取 M=64 行、
# N=256(hidden)、K=512,BLOCK/GROUP_SIZE 取 32/32。
#
# (M, N, K):
#   典型  (64, 256, 512)   N 整除 GROUP_SIZE,BLOCK_N=64
#   规模  (128, 256, 512)  典型规模 ×2:dim0 64->128
#   规模  (64, 256, 1024)  典型规模 ×2:dim2 512->1024
#   泛化  (37, 192, 96)    M 不整除 BLOCK_M(37);N、K 仍按块对齐
# 约束(kernel 如此):dot 的 load 没有 K 掩码、reshape 覆盖整块 N,所以
# K % BLOCK_K == 0、N % GROUP_SIZE == 0;只有 M 可以任意(store 有掩码)。
#         (16, 64, 32)     退化:最小对齐配置(单个 N tile)
SHAPES = ((64, 128, 128), (128, 128, 128))
# dot 用例含 fp16/bf16(累加在 f32);原始程序是 fp32。Mins 必须是 f32 缓冲区:
# tl.atomic_min 在本机 Triton 上不支持半精度指针,所以这里是"半精度输入 + f32 累加器"。
DTYPES = ('float32',)
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}
BLOCK_M, BLOCK_N, BLOCK_K, GROUP_SIZE, GROUP_M = 32, 64, 32, 32, 8
EPS = 1e-5


def ref(args, meta):
    """numpy 对照:float64 的 GEMM+bias、组内 norm、行最小值。"""
    m, n, k = int(args["M"]), int(args["N"]), int(args["K"])
    x = np.asarray(args["X_ptr"], dtype=np.float64).reshape(m, k)
    w = np.asarray(args["W_ptr"], dtype=np.float64).reshape(k, n)
    b = np.asarray(args["B_ptr"], dtype=np.float64)
    g = np.asarray(args["Gamma_ptr"], dtype=np.float64)
    bt = np.asarray(args["Beta_ptr"], dtype=np.float64)
    acc = x @ w + b[None, :]
    gs = int(meta["GROUP_SIZE"])
    acc3 = acc.reshape(m, n // gs, gs)
    mean = acc3.mean(axis=2)
    var = acc3.var(axis=2)
    rstd = 1.0 / np.sqrt(var + np.float64(args["eps"]))
    out = (acc3 - mean[:, :, None]) * rstd[:, :, None] * g.reshape(n // gs, gs)[None]         + bt.reshape(n // gs, gs)[None]
    mins = out.min(axis=(1, 2))
    out_min = np.asarray(args["Mins_ptr"])
    return {"Mins_ptr": mins.astype(out_min.dtype)}


def _make_case(shape=SHAPES[0], dtype="float16", seed=0):
    m, n, k = (int(v) for v in shape)
    if min(m, n, k) < 16:
        raise ValueError(f"shape must be >= 16 on all dims, got {shape}")
    if n % GROUP_SIZE or n % BLOCK_N or k % BLOCK_K:
        raise ValueError(f"need N % {BLOCK_N} == 0 and K % {BLOCK_K} == 0, got {shape}")
    host = _HOST_DTYPE[dtype]

    # X/W 取 1/16 网格上的 [-1, 1)(dot 误差最小);bias 小偏移,gamma ~1,beta ~0。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (rng.integers(-16, 16, (m, k), dtype=np.int16) / 16).astype(host)
    w = (rng.integers(-16, 16, (k, n), dtype=np.int16) / 16).astype(host)
    b = (rng.integers(-8, 9, n, dtype=np.int16) / 16).astype(host)
    gamma = (rng.integers(8, 24, n, dtype=np.int16) / 16).astype(host)
    beta = (rng.integers(-8, 9, n, dtype=np.int16) / 16).astype(host)
    # 语义边界:第 0 行 X 全 0(该行输出只由 bias 决定,组内方差可能为 0)。
    x[0, :] = 0.0
    b[:] = 0.0

    # 输出(原子累加的 Mins)永远是 f32,与输入精度无关。
    out_dtype = np.float32
    args = {"X_ptr": x.reshape(-1), "W_ptr": w.reshape(-1), "B_ptr": b,
            "Gamma_ptr": gamma, "Beta_ptr": beta,
            "Mins_ptr": np.full(m, np.inf, dtype=out_dtype),
            "M": np.int32(m), "N": np.int32(n), "K": np.int32(k),
            "stride_xm": np.int32(k), "stride_xk": np.int32(1),
            "stride_wn": np.int32(1), "stride_wk": np.int32(n), "eps": np.float32(EPS)}
    meta = {"BLOCK_M": BLOCK_M, "BLOCK_N": BLOCK_N, "BLOCK_K": BLOCK_K,
            "GROUP_SIZE": GROUP_SIZE, "GROUP_M": GROUP_M}
    grid = (((m + BLOCK_M - 1) // BLOCK_M) * ((n + BLOCK_N - 1) // BLOCK_N),)
    case = {"args": args, "meta": meta, "grid": grid, "outputs": ("Mins_ptr",),
            "expected": ref(args, meta)}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {name: "bfloat16" for name in
                                  ("X_ptr", "W_ptr", "B_ptr", "Gamma_ptr", "Beta_ptr")}
    case["comparison"] = {"Mins_ptr": {"comparator": "allclose", "exact": False,
                                       "rtol": 5e-3, "atol": 5e-3, "equal_nan": True}}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, fused_gemm_gn_min_kernel, DTYPES,
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
