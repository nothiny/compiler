"""leaky_relu_kernel_strided: 二维 leaky ReLU,用 block pointer + stride 访问。

模式: 2D grid,每个 program 用 make_block_ptr 取 (BLOCK_M, BLOCK_N) tile,
两个方向的 boundary_check 处理尾部(M/N 不必整除),tl.where 按符号选择
x 或 negative_slope*x,再按 out 的 stride 存回。stride 由调用方给出。

文件只有两层:
  ① leaky_relu_kernel_strided   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'medium/leaky_relu_kernel_strided', "group": 'medium', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'creation.arange', 'memory.load.masked', 'memory.store.masked', 'memory.block_pointer']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 34044, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "ebbd7f5ffc391a5447e6c89bd51b01f71302fb009949e6ff3435ed1df72c2367"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def leaky_relu_kernel_strided(x_ptr, out_ptr, stride_x_m, stride_x_n, stride_out_m, stride_out_n, M, N, negative_slope: tl.float32, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr):
    pid_m = tl.program_id(0)
    pid_n = tl.program_id(1)
    x_block_ptr = tl.make_block_ptr(base=x_ptr, shape=(M, N), strides=(stride_x_m, stride_x_n), offsets=(pid_m * BLOCK_M, pid_n * BLOCK_N), block_shape=(BLOCK_M, BLOCK_N), order=(1, 0))
    out_block_ptr = tl.make_block_ptr(base=out_ptr, shape=(M, N), strides=(stride_out_m, stride_out_n), offsets=(pid_m * BLOCK_M, pid_n * BLOCK_N), block_shape=(BLOCK_M, BLOCK_N), order=(1, 0))
    x = tl.load(x_block_ptr, boundary_check=(0, 1), padding_option='zero')
    zero = tl.zeros_like(x)
    out = tl.where(x > zero, x, negative_slope * x)
    tl.store(out_block_ptr, out, boundary_check=(0, 1))

# ------------------------------------------------------------------ ② case 层
# 典型用法:二维激活(Linear/Conv 之后的 (batch, features) 或 (H, W) 特征图)。
# 原始 (4096, 393216) fp32 展平处理;这里保留特征维 8192、batch 缩到 64。
#
# (M, N):
#   典型  (64, 8192)   原始 (4096, 393216):保留 N=8192 的一段特征,batch 缩到 64
#   规模  (128, 8192)  典型规模 ×2:dim0 64->128
#   规模  (64, 16384)  典型规模 ×2:dim1 8192->16384
#   泛化  (33, 65)     M、N 都不整除 BLOCK,两个方向都走 boundary_check
#         (1, 1)      退化:单元素
SHAPES = ((64, 128), (33, 65), (1, 1))
# 原始程序是 fp32;只有乘法与选择,半精度合法。
DTYPES = ("float32", "float16", "bfloat16")
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}
BLOCK_M, BLOCK_N = 32, 128
NEGATIVE_SLOPE = 0.01


def ref(args, meta):
    """numpy 对照:where(x > 0, x, slope*x)。"""
    m, n = int(args["M"]), int(args["N"])
    x = np.asarray(args["x_ptr"], dtype=np.float64).reshape(m, n)
    out = np.asarray(args["out_ptr"])
    y = np.where(x > 0, x, np.float64(args["negative_slope"]) * x)
    return {"out_ptr": y.reshape(-1).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    m, n = (int(v) for v in shape)
    if m <= 0 or n <= 0:
        raise ValueError(f"shape must be positive (M, N), got {shape}")
    host = _HOST_DTYPE[dtype]

    # 激活值 ~N(0,1):取 1/16 网格,半精度精确;正负两侧各占一半,leaky 分支
    # 一定会被走到。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (np.clip(np.rint(rng.standard_normal((m, n), dtype=np.float32) * 16),
                 -128, 127) / 16).astype(host)
    # 语义边界:0(比较的等号侧,走 where 的第二支)、一个很负的值(被缩放)。
    x[0, 0] = 0.0
    x[0, -1] = -8.0

    out_dtype = np.float32 if dtype == "bfloat16" else np.dtype(dtype)
    args = {"x_ptr": x.reshape(-1), "out_ptr": np.zeros(m * n, dtype=out_dtype),
            "stride_x_m": np.int32(n), "stride_x_n": np.int32(1),
            "stride_out_m": np.int32(n), "stride_out_n": np.int32(1),
            "M": np.int32(m), "N": np.int32(n),
            "negative_slope": np.float32(NEGATIVE_SLOPE)}
    meta = {"BLOCK_M": BLOCK_M, "BLOCK_N": BLOCK_N}
    grid = ((m + BLOCK_M - 1) // BLOCK_M, (n + BLOCK_N - 1) // BLOCK_N)
    case = {"args": args, "meta": meta, "grid": grid, "outputs": ("out_ptr",),
            "expected": ref(args, meta)}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {"x_ptr": "bfloat16", "out_ptr": "bfloat16"}
        case["comparison"] = {"out_ptr": {"comparator": "allclose", "exact": False,
                                          "rtol": 5e-3, "atol": 5e-3, "equal_nan": True}}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, leaky_relu_kernel_strided, DTYPES,
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
