"""transpose_2d_kernel_opt: 二维矩阵转置,BLOCK x BLOCK 的 tile 交换读写。

模式: 2D grid,每个 program 读 x 的一个 (BLOCK, BLOCK) tile(行跨 stride_xk、
列跨 stride_xm),tl.trans 之后按 y 的 stride 写回。load/store 都没有掩码,
所以 K 与 M 都必须整除 BLOCK —— 这是 kernel 的硬约束。

文件只有两层:
  ① transpose_2d_kernel_opt   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/transpose_2d_kernel_opt', "group": 'basic', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'creation.arange', 'memory.load', 'memory.store', 'shape.trans']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 27760, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "c7c4ac3b82507438fd2abd51b9fc3b3834f0ba028de81435110adf7a96def3d4"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def transpose_2d_kernel_opt(x_ptr, y_ptr, K, M, stride_xk, stride_xm, stride_ym, stride_yk, BLOCK: tl.constexpr):
    pid_m = tl.program_id(0)
    pid_k = tl.program_id(1)
    offs_m = pid_m * BLOCK + tl.arange(0, BLOCK)
    offs_k = pid_k * BLOCK + tl.arange(0, BLOCK)
    x_ptrs = x_ptr + offs_k[:, None] * stride_xk + offs_m[None, :] * stride_xm
    tile = tl.load(x_ptrs)
    y_ptrs = y_ptr + offs_m[:, None] * stride_ym + offs_k[None, :] * stride_yk
    tl.store(y_ptrs, tl.trans(tile))

# ------------------------------------------------------------------ ② case 层
# 典型用法:GEMM 前把 (K, M) 的操作数转置成 (M, K) 以配合 dot 的布局要求。
# 原始 (K, M) = (8192, 2048)(K >> M 是这类操作数的结构性特征);这里保持 K/M = 4
# 的比例、把两个维度按 1/4 缩小,单 case 的 make_case 控制在几十毫秒。
#
# (K, M):
#   典型  (2048, 512)   比例与原始一致(K/M = 4),K、M 都整除 BLOCK=16
#   规模  (4096, 512)  典型规模 ×2:dim0 2048->4096
#   规模  (2048, 1024)  典型规模 ×2:dim1 512->1024
#   泛化  (256, 64)     小 GEMM 的操作数,仍然整除
#         (16, 16)     退化:单个 tile(要求整除,无掩码)
SHAPES = ((128, 128), (128, 64))
# 转置只是搬数据,任何元素类型都合法;fp32 是 GEMM 的默认类型,排第一。
DTYPES = ("float32", "float16", "bfloat16")
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}
BLOCK = 16


def ref(args, meta):
    """numpy 对照:按 stride 视图转置后转回输出 dtype。"""
    k, m = int(args["K"]), int(args["M"])
    x = np.asarray(args["x_ptr"]).reshape(k, m)
    out = np.asarray(args["y_ptr"])
    return {"y_ptr": np.ascontiguousarray(x.T).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    k, m = (int(v) for v in shape)
    if k <= 0 or m <= 0 or k % BLOCK or m % BLOCK:
        raise ValueError(f"K and M must be positive multiples of BLOCK={BLOCK}, got {shape}")

    # GEMM 操作数是 ~N(0,1) 的权重/激活;取值落在 1/16 网格上,半精度精确可表示,
    # 转置不引入任何舍入。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (rng.integers(-128, 128, (k, m), dtype=np.int16) / 16).astype(_HOST_DTYPE[dtype])
    # 语义边界:首行/末行、首列/末列的取值不同,保证 tile 边界处不会错位读写。
    x[0, 0], x[0, -1], x[-1, 0], x[-1, -1] = 1.0, 2.0, 3.0, 4.0

    out_dtype = np_dtype = _HOST_DTYPE[dtype]
    args = {"x_ptr": x, "y_ptr": np.zeros((m, k), dtype=out_dtype),
            "K": np.int32(k), "M": np.int32(m),
            "stride_xk": np.int32(m), "stride_xm": np.int32(1),
            "stride_ym": np.int32(k), "stride_yk": np.int32(1)}
    meta = {"BLOCK": BLOCK}
    case = {"args": args, "meta": meta, "grid": (m // BLOCK, k // BLOCK),
            "outputs": ("y_ptr",), "expected": ref(args, meta)}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {"x_ptr": "bfloat16", "y_ptr": "bfloat16"}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;转置按位精确比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, transpose_2d_kernel_opt, DTYPES,
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
