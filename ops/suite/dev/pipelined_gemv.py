"""pipelined_gemv: GEMV = A(M, K) @ b(K),K 方向用 tl.range(num_stages=2) 流水。

模式: 每个 program 处理 BLOCK_SIZE_M 行,内层按 BLOCK_SIZE_K 切 K 维,
load 一个 (BLOCK_SIZE_M, BLOCK_SIZE_K) 的 A 块与 b 块,累加 f32 点积。
行掩码(row_idx < M)与 K 掩码(k_idx < K)同时存在,支持任意 M/K。

文件只有两层:
  ① makora_pipelined_gemv_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/pipelined_gemv', "group": 'basic', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.loop_runtime_bound', 'creation.arange', 'memory.load.masked', 'memory.store.masked', 'reduce.sum.axis1']}
SOURCE = {'dataset': 'makora-ai/triton-gpu-latency', 'revision': '3b30911350fa433e1cb97ec2a41bd8908dd35d5d', 'file': 'data/test.parquet', 'row': 60, 'source_sha256': 'c79e8d8ff9c597790c7d1949b0eaeba3a56e20170564e3e63e7dbd71d5e4353b', 'upstream_kernel': 'gemv_optimized_kernel_v2', 'upstream_latency_label': 111.329274139404, 'license': 'Apache-2.0', 'adaptations': ['rename JIT entry', 'replace torch host wrapper with independent NumPy case/ref', 'select explicit legal launch tile'], 'extraction_scope': 'original single JIT kernel stage, not the entire original PyTorch Model'}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def makora_pipelined_gemv_kernel(A_ptr, B_ptr, out_ptr, M: int, K: int, stride_am: int, stride_ak: int, stride_bk: int, stride_out_m: int, BLOCK_SIZE_M: tl.constexpr, BLOCK_SIZE_K: tl.constexpr):
    """
    Optimized GEMV kernel with improved memory efficiency and parallelism.
    Uses software pipelining and optimal block sizes for better occupancy.
    """
    pid = tl.program_id(0)
    row_start = pid * BLOCK_SIZE_M
    rows = tl.arange(0, BLOCK_SIZE_M)
    row_idx = row_start + rows
    row_mask = row_idx < M
    acc = tl.zeros([BLOCK_SIZE_M], dtype=tl.float32)
    for k_start in tl.range(0, K, BLOCK_SIZE_K, num_stages=2):
        ks = tl.arange(0, BLOCK_SIZE_K)
        k_idx = k_start + ks
        k_mask = k_idx < K
        b_vals = tl.load(B_ptr + k_idx * stride_bk, mask=k_mask, other=0.0)
        a_ptrs = A_ptr + row_idx[:, None] * stride_am + k_idx[None, :] * stride_ak
        a_mask = row_mask[:, None] & k_mask[None, :]
        a_vals = tl.load(a_ptrs, mask=a_mask, other=0.0)
        acc += tl.sum(a_vals * b_vals[None, :], axis=1)
    tl.store(out_ptr + row_idx * stride_out_m, acc, mask=row_mask)

# ------------------------------------------------------------------ ② case 层
# 典型用法:decode 阶段的线性层 = 单 token(或很少几个 token)乘一个 (K,) 权重:
# K 是 hidden(4096),M 是 token 数(decode 时为 1~8)。K 远大于 M 是这个 kernel
# 的结构性特征(每行一次完整的 K 维点积)。
#
# (M, K):
#   典型  (8, 4096)   decode:8 个 token x hidden 4096(原始 softplus_linear 一类)
#   规模  (16, 4096)  典型规模 ×2:dim0 8->16
#   规模  (8, 8192)  典型规模 ×2:dim1 4096->8192
#   泛化  (17, 129)   M、K 都不是 BLOCK 的整数倍:行尾与 K 尾都被掩码
#         (1, 1)     退化:单元素点积
SHAPES = ((8, 128), (17, 97), (1, 1))
# 原始 workload 是 fp32;fp16 有 11 位尾数,乘积舍入 0.05%,K 维求和后仍在对拍
# 容差内。bf16 只有 8 位尾数,乘积在 bf16 里舍入后 K=4096 项相加的相对误差可达
# 3%,没有对拍意义,故不列入合法域。
DTYPES = ('float32', 'float16', 'bfloat16')
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}
BLOCK_M = 16
BLOCK_K = 64


def ref(args, meta):
    """numpy 对照:float64 的矩阵向量积。"""
    a = np.asarray(args["A_ptr"], dtype=np.float64)
    b = np.asarray(args["B_ptr"], dtype=np.float64)
    out = np.asarray(args["out_ptr"])
    return {"out_ptr": (a @ b).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    m, k = (int(v) for v in shape)
    if m <= 0 or k <= 0:
        raise ValueError(f"shape must be positive (M, K), got {shape}")

    # 权重与激活都取 1/16 网格上的 [-1, 1):乘积是 1/256 的倍数,半精度里精确,
    # K 维的 f32 累加误差可以忽略,所以半精度 case 也能用严格的 5e-3。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    host = _HOST_DTYPE[dtype]
    a = (rng.integers(-16, 16, (m, k), dtype=np.int16) / 16).astype(host)
    b = (rng.integers(-16, 16, k, dtype=np.int16) / 16).astype(host)
    # 语义边界:第 0 行 A 全 0(输出恰为 0);b 的第一个元素为 -1,最后一个
    # 元素为 1,保证 K 维的首尾都被读到。
    a[0, :] = 0.0
    b[0] = -1.0
    if k > 1:
        b[-1] = 1.0

    out_dtype = np.float32 if dtype == "bfloat16" else np.dtype(dtype)
    args = {"A_ptr": a, "B_ptr": b, "out_ptr": np.zeros(m, dtype=out_dtype),
            "M": np.int32(m), "K": np.int32(k), "stride_am": np.int32(k),
            "stride_ak": np.int32(1), "stride_bk": np.int32(1),
            "stride_out_m": np.int32(1)}
    meta = {"BLOCK_SIZE_M": BLOCK_M, "BLOCK_SIZE_K": BLOCK_K}
    case = {"args": args, "meta": meta, "grid": ((m + BLOCK_M - 1) // BLOCK_M,),
            "outputs": ("out_ptr",), "expected": ref(args, meta)}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, makora_pipelined_gemv_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float32'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float32': 'float32', 'float16': 'float16'}


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
