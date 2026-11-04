"""fused_gemm_gn_min_kernel(2): GEMM + bias + 沿 N 分组的 norm + 行最小值(权重按 (N, K) 存)。

模式: 1D grid 的 GROUP_SIZE_M swizzle GEMM:x(BLOCK_M, BLOCK_K) 与 w(BLOCK_N, BLOCK_K)
取转置后 tl.dot,K 方向 for 循环累积 f32;加 bias 后把 N 方向 reshape 成
(N//CHANNELS_PER_GROUP, CHANNELS_PER_GROUP) 求组内 mean/var/rstd,affine 后两次
tl.min 得行最小值,再用 tl.atomic_min 归并到 min_ptr(跨 N tile 原子取最小)。
三个方向都有掩码。

文件只有两层:
  ① fused_gemm_gn_min_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/fused_gemm_gn_min_kernel_2', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'atomic.min', 'control.loop_runtime_bound', 'creation.arange', 'creation.zeros', 'linalg.dot', 'math.cdiv', 'math.minimum', 'math.rsqrt', 'memory.load.masked', 'reduce.max.axis1', 'reduce.sum.axis2', 'shape.reshape', 'shape.trans']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "test", "row": 24447, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "1e8171fc0f15e2ef95b3973314cc9c12a652e16894ee4e6da9d4892dd3c19df0"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def fused_gemm_gn_min_kernel(x_ptr, w_ptr, bias_ptr, gamma_ptr, beta_ptr, min_ptr, M, N, K, stride_xm, stride_xk, stride_wn, stride_wk, eps, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr, GROUP_SIZE_M: tl.constexpr, CHANNELS_PER_GROUP: tl.constexpr):
    pid = tl.program_id(axis=0)
    num_pid_m = tl.cdiv(M, BLOCK_M)
    num_pid_n = tl.cdiv(N, BLOCK_N)
    num_pid_in_group = GROUP_SIZE_M * num_pid_n
    group_id = pid // num_pid_in_group
    first_pid_m = group_id * GROUP_SIZE_M
    group_size = tl.minimum(num_pid_m - first_pid_m, GROUP_SIZE_M)
    pid_m = first_pid_m + pid % group_size
    pid_n = pid % num_pid_in_group // group_size
    offs_m = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    offs_k = tl.arange(0, BLOCK_K)
    x_ptrs = x_ptr + (offs_m[:, None] * stride_xm + offs_k[None, :] * stride_xk)
    w_ptrs = w_ptr + (offs_n[:, None] * stride_wn + offs_k[None, :] * stride_wk)
    acc = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)
    for k in range(0, K, BLOCK_K):
        x = tl.load(x_ptrs, mask=(offs_m[:, None] < M) & (k + offs_k[None, :] < K), other=0.0)
        w = tl.load(w_ptrs, mask=(offs_n[:, None] < N) & (k + offs_k[None, :] < K), other=0.0)
        acc += tl.dot(x, w.T)
        x_ptrs += BLOCK_K * stride_xk
        w_ptrs += BLOCK_K * stride_wk
    bias = tl.load(bias_ptr + offs_n, mask=offs_n < N, other=0.0)
    acc += bias[None, :]
    acc_r = tl.reshape(acc, (BLOCK_M, BLOCK_N // CHANNELS_PER_GROUP, CHANNELS_PER_GROUP))
    mean = tl.sum(acc_r, axis=2) / float(CHANNELS_PER_GROUP)
    mean_b = tl.broadcast_to(mean[:, :, None], (BLOCK_M, BLOCK_N // CHANNELS_PER_GROUP, CHANNELS_PER_GROUP))
    diff = acc_r - mean_b
    var = tl.sum(diff * diff, axis=2) / float(CHANNELS_PER_GROUP)
    rstd = tl.rsqrt(var + eps)
    rstd_b = tl.broadcast_to(rstd[:, :, None], (BLOCK_M, BLOCK_N // CHANNELS_PER_GROUP, CHANNELS_PER_GROUP))
    gamma = tl.load(gamma_ptr + offs_n, mask=offs_n < N, other=1.0)
    beta = tl.load(beta_ptr + offs_n, mask=offs_n < N, other=0.0)
    gamma_r = tl.reshape(gamma, (BLOCK_N // CHANNELS_PER_GROUP, CHANNELS_PER_GROUP))
    beta_r = tl.reshape(beta, (BLOCK_N // CHANNELS_PER_GROUP, CHANNELS_PER_GROUP))
    norm = diff * rstd_b * gamma_r[None, :, :] + beta_r[None, :, :]
    min_g = tl.min(norm, axis=2)
    min_b = tl.min(min_g, axis=1)
    min_ptrs = min_ptr + offs_m
    tl.atomic_min(min_ptrs, min_b, mask=offs_m < M)

# ------------------------------------------------------------------ ② case 层
# 典型用法:Transformer FFN 投影 + 沿特征维分组的 norm + 每行最小值(激活健康度)。
# 原始程序是 (tokens, hidden) 投影;这里取 M=64、N=256、K=512,
# BLOCK=(32,64,32)、CHANNELS_PER_GROUP=32。
#
# (M, N, K):
#   典型  (64, 256, 512)  三个方向都整除 BLOCK
#   规模  (128, 256, 512)  典型规模 ×2:dim0 64->128
#   规模  (64, 256, 1024)  典型规模 ×2:dim2 512->1024
#   泛化  (37, 192, 128)  M 不整除 BLOCK_M、N 不整除 BLOCK_N:两处掩码
#   约束:N 必须整除 CHANNELS_PER_GROUP(reshape 按整块 N 切组)。
#         (16, 32, 32)    退化:单个 tile
SHAPES = ((64, 128, 128), (37, 96, 128))
# dot 用例含 fp16/bf16(累加在 f32)。min_ptr 是 f32 缓冲区:tl.atomic_min 不支持半精度。
DTYPES = ('float32',)
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}
BLOCK_M, BLOCK_N, BLOCK_K, GROUP_SIZE_M, CHANNELS_PER_GROUP = 32, 64, 32, 8, 32
EPS = 1e-5


def ref(args, meta):
    """numpy 对照:float64 的 GEMM+bias、组内 norm、行最小值。"""
    m, n, k = int(args["M"]), int(args["N"]), int(args["K"])
    x = np.asarray(args["x_ptr"], dtype=np.float64).reshape(m, k)
    w = np.asarray(args["w_ptr"], dtype=np.float64).reshape(n, k)
    b = np.asarray(args["bias_ptr"], dtype=np.float64)
    g = np.asarray(args["gamma_ptr"], dtype=np.float64)
    bt = np.asarray(args["beta_ptr"], dtype=np.float64)
    acc = x @ w.T + b[None, :]
    cpg = int(meta["CHANNELS_PER_GROUP"])
    acc3 = acc.reshape(m, n // cpg, cpg)
    mean = acc3.mean(axis=2)
    var = acc3.var(axis=2)
    rstd = 1.0 / np.sqrt(var + np.float64(args["eps"]))
    out = (acc3 - mean[:, :, None]) * rstd[:, :, None] * g.reshape(n // cpg, cpg)[None]         + bt.reshape(n // cpg, cpg)[None]
    out_min = np.asarray(args["min_ptr"])
    return {"min_ptr": out.min(axis=(1, 2)).astype(out_min.dtype)}


def _make_case(shape=SHAPES[0], dtype="float16", seed=0):
    m, n, k = (int(v) for v in shape)
    if min(m, n, k) < 16:
        raise ValueError(f"shape must be >= 16 on all dims, got {shape}")
    if n % CHANNELS_PER_GROUP:
        raise ValueError(f"N must be divisible by {CHANNELS_PER_GROUP}, got {shape}")
    # BLOCK_N 必须整除 CHANNELS_PER_GROUP 的整数倍:reshape 按整块切组
    if BLOCK_N % CHANNELS_PER_GROUP:
        raise ValueError("BLOCK_N must be a multiple of CHANNELS_PER_GROUP")
    host = _HOST_DTYPE[dtype]

    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (rng.integers(-16, 16, (m, k), dtype=np.int16) / 16).astype(host)
    w = (rng.integers(-16, 16, (n, k), dtype=np.int16) / 16).astype(host)
    b = (rng.integers(-8, 9, n, dtype=np.int16) / 16).astype(host)
    gamma = (rng.integers(8, 24, n, dtype=np.int16) / 16).astype(host)
    beta = (rng.integers(-8, 9, n, dtype=np.int16) / 16).astype(host)
    # 语义边界:第 0 行 X 全 0(输出只由 bias 决定,组内方差可能为 0)。
    x[0, :] = 0.0
    b[:] = 0.0

    args = {"x_ptr": x.reshape(-1), "w_ptr": w.reshape(-1), "bias_ptr": b,
            "gamma_ptr": gamma, "beta_ptr": beta,
            "min_ptr": np.full(m, np.inf, np.float32),
            "M": np.int32(m), "N": np.int32(n), "K": np.int32(k),
            "stride_xm": np.int32(k), "stride_xk": np.int32(1),
            "stride_wn": np.int32(k), "stride_wk": np.int32(1), "eps": np.float32(EPS)}
    meta = {"BLOCK_M": BLOCK_M, "BLOCK_N": BLOCK_N, "BLOCK_K": BLOCK_K,
            "GROUP_SIZE_M": GROUP_SIZE_M, "CHANNELS_PER_GROUP": CHANNELS_PER_GROUP}
    grid = (((m + BLOCK_M - 1) // BLOCK_M) * ((n + BLOCK_N - 1) // BLOCK_N),)
    case = {"args": args, "meta": meta, "grid": grid, "outputs": ("min_ptr",),
            "expected": ref(args, meta)}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {name: "bfloat16" for name in
                                  ("x_ptr", "w_ptr", "bias_ptr", "gamma_ptr", "beta_ptr")}
    case["comparison"] = {"min_ptr": {"comparator": "allclose", "exact": False,
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
