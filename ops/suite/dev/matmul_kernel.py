"""matmul_kernel: 标准分块 GEMM,GROUP_M 做 L2 友好的 tile swizzle。

模式: 1D grid(所有 (m, n) tile 展平),pid 先按 GROUP_M 分组、组内再蛇形顺序
取 tile;K 方向用 tl.static_range(0, K, BLOCK_K) 静态展开(所以 K 是 constexpr),
每轮 tl.dot 累积到 f32。EVEN_M/EVEN_N/EVEN_K 三个 constexpr 开关决定对应的 load
是否带掩码(全整除时走无掩码路径);fp32 dot 是 IEEE。

文件只有两层:
  ① matmul_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/matmul_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.loop_constexpr', 'control.if_constexpr', 'linalg.dot', 'linalg.dot.acc', 'math.cdiv', 'math.minimum', 'memory.load', 'memory.load.masked', 'memory.store', 'memory.store.masked']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 2931, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "e5ae748203651e5b15803b051351b7369b9573ea86a397471ff84b1174e1b6a2"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def matmul_kernel(A_ptr, B_ptr, C_ptr, M, N, stride_am, stride_ak, stride_bk, stride_bn, stride_cm, stride_cn, K: tl.constexpr, EVEN_M: tl.constexpr, EVEN_N: tl.constexpr, EVEN_K: tl.constexpr, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr, GROUP_M: tl.constexpr):
    pid = tl.program_id(0)
    grid_m = tl.cdiv(M, BLOCK_M)
    grid_n = tl.cdiv(N, BLOCK_N)
    pid_group = pid // (GROUP_M * grid_n)
    first_pid_m = pid_group * GROUP_M
    group_size_m = tl.minimum(grid_m - first_pid_m, GROUP_M)
    pid_in_group = pid - pid_group * (GROUP_M * grid_n)
    pid_m = first_pid_m + pid_in_group % group_size_m
    pid_n = pid_in_group // group_size_m
    offs_m = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    offs_k = tl.arange(0, BLOCK_K)
    acc = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)
    if EVEN_M:
        m_mask = None
    else:
        m_mask = offs_m < M
    if EVEN_N:
        n_mask = None
    else:
        n_mask = offs_n < N
    for k0 in tl.static_range(0, K, BLOCK_K):
        k_ids = k0 + offs_k
        if EVEN_K:
            k_mask = None
        else:
            k_mask = k_ids < K
        a_ptrs = A_ptr + (offs_m[:, None] * stride_am + k_ids[None, :] * stride_ak)
        b_ptrs = B_ptr + (k_ids[:, None] * stride_bk + offs_n[None, :] * stride_bn)
        if m_mask is None and k_mask is None:
            a = tl.load(a_ptrs)
        elif k_mask is None:
            a = tl.load(a_ptrs, mask=m_mask[:, None], other=0.0)
        elif m_mask is None:
            a = tl.load(a_ptrs, mask=k_mask[None, :], other=0.0)
        else:
            a = tl.load(a_ptrs, mask=m_mask[:, None] & k_mask[None, :], other=0.0)
        if k_mask is None and n_mask is None:
            b = tl.load(b_ptrs)
        elif n_mask is None:
            b = tl.load(b_ptrs, mask=k_mask[:, None], other=0.0)
        elif k_mask is None:
            b = tl.load(b_ptrs, mask=n_mask[None, :], other=0.0)
        else:
            b = tl.load(b_ptrs, mask=k_mask[:, None] & n_mask[None, :], other=0.0)
        acc = tl.dot(a, b, acc=acc)
    c_ptrs = C_ptr + (offs_m[:, None] * stride_cm + offs_n[None, :] * stride_cn)
    if m_mask is None and n_mask is None:
        tl.store(c_ptrs, acc)
    elif n_mask is None:
        tl.store(c_ptrs, acc, mask=m_mask[:, None])
    elif m_mask is None:
        tl.store(c_ptrs, acc, mask=n_mask[None, :])
    else:
        tl.store(c_ptrs, acc, mask=m_mask[:, None] & n_mask[None, :])

# ------------------------------------------------------------------ ② case 层
# 典型用法:GEMM(K 远大于 M、N 是这类算子的结构性特征;M/N/K 全对齐 16 与都不对齐
# 各要一例)。原始程序是 Linear/attn 投影的 GEMM;这里取 M=256、N=512、K=2048,
# BLOCK=64/64/32。
#
# (M, N, K):
#   典型  (256, 512, 2048)  K >> M、N;三者都整除 BLOCK => EVEN_* 全真(无掩码)
#   规模  (512, 512, 2048)  典型规模 ×2:dim0 256->512
#   规模  (768, 512, 2048)  典型规模 ×3:dim0 256->768
#   泛化  (17, 33, 1000)    都不整除 BLOCK => 三个 EVEN_* 全假,三条掩码路径都走
#         (64, 64, 32)      退化:单个 tile,EVEN_K 真、M/N 整除
SHAPES = ((128, 128, 128), (17, 33, 100))
# fp32 dot is IEEE (the subset has no precision knob).
DTYPES = ("float16", "bfloat16", "float32")
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}
BLOCK_M, BLOCK_N, BLOCK_K, GROUP_M = 64, 64, 32, 8


def ref(args, meta):
    """numpy 对照:float64 的 A @ B。"""
    m, n, k = int(args["M"]), int(args["N"]), int(meta["K"])
    a = np.asarray(args["A_ptr"], dtype=np.float64).reshape(m, k)
    b = np.asarray(args["B_ptr"], dtype=np.float64).reshape(k, n)
    out = np.asarray(args["C_ptr"])
    return {"C_ptr": (a @ b).reshape(-1).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float16", seed=0):
    m, n, k = (int(v) for v in shape)
    if min(m, n, k) < 16:
        raise ValueError(f"shape must be >= 16 on all dims, got {shape}")
    host = _HOST_DTYPE[dtype]

    # 取 1/16 网格上的 [-1, 1):fp16/bf16 里精确,乘积与 K 维 f32 累加的误差最小。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    a = (rng.integers(-16, 16, (m, k), dtype=np.int16) / 16).astype(host)
    b = (rng.integers(-16, 16, (k, n), dtype=np.int16) / 16).astype(host)
    # 语义边界:第 0 行 A 全 0(整行为 0);B 的第 0 列全 1(输出等于 A 的行和)。
    a[0, :] = 0.0
    b[:, 0] = 1.0

    out_dtype = np.float32 if dtype == "bfloat16" else np.dtype(dtype)
    args = {"A_ptr": a.reshape(-1), "B_ptr": b.reshape(-1),
            "C_ptr": np.zeros((m, n), dtype=out_dtype),
            "M": np.int32(m), "N": np.int32(n),
            "stride_am": np.int32(k), "stride_ak": np.int32(1),
            "stride_bk": np.int32(n), "stride_bn": np.int32(1),
            "stride_cm": np.int32(n), "stride_cn": np.int32(1)}
    meta = {"K": k, "BLOCK_M": BLOCK_M,
            "BLOCK_N": BLOCK_N, "BLOCK_K": BLOCK_K, "GROUP_M": GROUP_M,
            "EVEN_M": m % BLOCK_M == 0, "EVEN_N": n % BLOCK_N == 0,
            "EVEN_K": k % BLOCK_K == 0}
    grid = ((m + BLOCK_M - 1) // BLOCK_M * ((n + BLOCK_N - 1) // BLOCK_N),)
    case = {"args": args, "meta": meta, "grid": grid, "outputs": ("C_ptr",),
            "expected": ref(args, meta)}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {"A_ptr": "bfloat16", "B_ptr": "bfloat16",
                                  "C_ptr": "bfloat16"}
    case["comparison"] = {"C_ptr": {"comparator": "allclose", "exact": False,
                                    "rtol": 5e-3, "atol": 5e-3, "equal_nan": True}}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, matmul_kernel, DTYPES,
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
