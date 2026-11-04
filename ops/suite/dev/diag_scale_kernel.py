"""diag_scale_kernel: C = diag(a) @ B,按行缩放,不物化对角矩阵。

模式: 每个 program 处理一行:a 的一个标量乘以 B 的一整行。行内用 block pointer
沿 M 方向 for 循环 advance,boundary_check 处理 M 尾块(零填充/丢弃),所以
M 不必整除 BLOCK_SIZE_M;N 由 grid 覆盖。覆盖 block pointer 的 advance 与
boundary check。

文件只有两层:
  ① diag_scale_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'medium/diag_scale_kernel', "group": 'medium', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.loop_runtime_bound', 'memory.load.masked', 'memory.store.masked', 'memory.block_pointer']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 21920, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "76abb6dc8b437d3b11c310785ff101fba4f6900ab90238135c8785483e4dd1ea"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def diag_scale_kernel(A_ptr, B_ptr, C_ptr, N, M, stride_a_n, stride_b_n, stride_b_m, stride_c_n, stride_c_m, BLOCK_SIZE_M: tl.constexpr):
    """
    Triton kernel for C = diag(A) @ B, optimized as row-wise scaling.
    This kernel avoids materializing the NxN diagonal matrix. It uses a 1D launch
    grid where each program computes one full row of the output matrix C. This
    design maximizes parallelism, ensures perfect data reuse for the scaling
    factors from A, and achieves fully coalesced memory accesses for B and C.
    """
    row_idx = tl.program_id(0)
    a_val = tl.load(A_ptr + row_idx * stride_a_n)
    b_block_ptr = tl.make_block_ptr(base=B_ptr, shape=(N, M), strides=(stride_b_n, stride_b_m), offsets=(row_idx, 0), block_shape=(1, BLOCK_SIZE_M), order=(1, 0))
    c_block_ptr = tl.make_block_ptr(base=C_ptr, shape=(N, M), strides=(stride_c_n, stride_c_m), offsets=(row_idx, 0), block_shape=(1, BLOCK_SIZE_M), order=(1, 0))
    for _ in range(0, tl.cdiv(M, BLOCK_SIZE_M)):
        b_vals = tl.load(b_block_ptr, boundary_check=(1,), padding_option='zero')
        c_vals = a_val * b_vals
        tl.store(c_block_ptr, c_vals, boundary_check=(1,))
        b_block_ptr = tl.advance(b_block_ptr, (0, BLOCK_SIZE_M))
        c_block_ptr = tl.advance(c_block_ptr, (0, BLOCK_SIZE_M))

# ------------------------------------------------------------------ ② case 层
# 典型用法:逐元素缩放里的"按行缩放"(把对角矩阵乘法退化成一次广播乘),常见于
# 优化器/归一化的重标定步骤。原始是随机 (N, M) 矩阵,这里取 4096 x 1024。
#
# (N, M):
#   典型  (4096, 1024)  N 行各一个缩放因子;M 整除 BLOCK_SIZE_M
#   规模  (8192, 1024)  典型规模 ×2:dim0 4096->8192
#   规模  (4096, 2048)  典型规模 ×2:dim1 1024->2048
#   泛化  (129, 1000)   M 不整除 BLOCK:最后一块走 boundary_check;N 也不是 2 的幂
#         (1, 1)      退化:单元素
SHAPES = ((128, 128), (97, 100), (1, 1))
# 只有一次乘法,半精度合法;原始矩阵是 fp32。
DTYPES = ("float32", "float16", "bfloat16")
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}
BLOCK_SIZE_M = 128


def ref(args, meta):
    """numpy 对照:a[:, None] * B。"""
    n, m = int(args["N"]), int(args["M"])
    a = np.asarray(args["A_ptr"], dtype=np.float64)
    b = np.asarray(args["B_ptr"], dtype=np.float64).reshape(n, m)
    out = np.asarray(args["C_ptr"])
    return {"C_ptr": (a[:, None] * b).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n, m = (int(v) for v in shape)
    if n <= 0 or m <= 0:
        raise ValueError(f"shape must be positive (N, M), got {shape}")
    host = _HOST_DTYPE[dtype]

    # 缩放因子与矩阵都取 1/16 网格上的 [-2, 2),乘积仍在半精度精确域内。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    a = (rng.integers(-32, 32, n, dtype=np.int16) / 16).astype(host)
    b = (rng.integers(-32, 32, (n, m), dtype=np.int16) / 16).astype(host)
    # 语义边界:第 0 行缩放因子为 0(整行为 0)、第 1 行缩放因子为 1(恒等),
    # 第 2 行缩放因子为 -1(只翻转符号)。
    a[0] = 0.0
    if n > 1:
        a[1] = 1.0
    if n > 2:
        a[2] = -1.0

    out_dtype = np.float32 if dtype == "bfloat16" else np.dtype(dtype)
    args = {"A_ptr": a, "B_ptr": b, "C_ptr": np.zeros((n, m), dtype=out_dtype),
            "N": np.int32(n), "M": np.int32(m), "stride_a_n": np.int32(1),
            "stride_b_n": np.int32(m), "stride_b_m": np.int32(1),
            "stride_c_n": np.int32(m), "stride_c_m": np.int32(1)}
    meta = {"BLOCK_SIZE_M": BLOCK_SIZE_M}
    case = {"args": args, "meta": meta, "grid": (n,), "outputs": ("C_ptr",),
            "expected": ref(args, meta)}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {"A_ptr": "bfloat16", "B_ptr": "bfloat16",
                                  "C_ptr": "bfloat16"}
        case["comparison"] = {"C_ptr": {"comparator": "allclose", "exact": False,
                                        "rtol": 5e-3, "atol": 5e-3, "equal_nan": True}}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;乘性输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, diag_scale_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)


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
