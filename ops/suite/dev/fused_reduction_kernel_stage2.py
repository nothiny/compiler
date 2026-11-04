"""fused_reduction_kernel_stage2: 两段归约的第二段 —— 按行求和、取均值、夹取。

模式: 每个 program 处理一行 partial(宽度 BLOCK_SIZE,无掩码),tl.sum 归约成标量,
乘 inv_total_elements 得均值,再用 tl.clamp 夹到 [clamp_min, clamp_max]。它是
ConvTranspose3d+MaxPool3d+bias+scale+全局均值+clamp 复合链的收尾段。

文件只有两层:
  ① fused_reduction_kernel_stage2   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/fused_reduction_kernel_stage2', "group": 'basic', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'creation.arange', 'math.clamp', 'memory.load', 'memory.store', 'reduce.sum.axis0']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 385782, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "15bd898129254da8cbd2753170b8cfeed96c55fcf1f340a8203eb538f27a7f21"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def fused_reduction_kernel_stage2(partial_ptr, out_ptr, inv_total_elements, clamp_min, clamp_max, BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(0)
    offs = tl.arange(0, BLOCK_SIZE)
    vals = tl.load(partial_ptr + pid * BLOCK_SIZE + offs)
    total = tl.sum(vals)
    res = tl.clamp(total * inv_total_elements, clamp_min, clamp_max)
    tl.store(out_ptr + pid, res)

# ------------------------------------------------------------------ ② case 层
# 典型用法:全局平均池化 + clamp 的收尾。原始 (128, 16, 16, 32, 32) fp32,
# ConvTranspose 后 C=16、池化后 D_p*H_p*W_p = 8*16*16 = 2048,total_pool =
# 16*2048 = 32768 => inv_total = 1/32768;stage-1 每个 (n, c) 平面写 BLOCK=1024
# 个 partial,所以 grid = N*C = 2048。无掩码:BLOCK_SIZE 就是 partial 宽度。
#
# (P, BLOCK_SIZE):
#   典型  (2048, 1024)  原始 N*C = 128*16 = 2048 行,每行 1024 个 partial
#   规模  (4096, 1024)  典型规模 ×2:dim0 2048->4096
#   规模  (2048, 2048)  典型规模 ×2:dim1 1024->2048
#   泛化  (2048, 128)   小配置:BLOCK_SIZE 换 128(仍无掩码)
#         (1, 1)        退化:单个 partial
SHAPES = ((128, 128), (1, 1))
# partial 缓冲区在原始程序里是 f32,均值和 clamp 也都在 f32 里做。
DTYPES = ('float32', 'float16', 'bfloat16')
TOTAL_POOL = 32768       # = C * D_p * H_p * W_p = 16 * 8 * 16 * 16
CLAMP_MIN, CLAMP_MAX = 0.0, 1.0


def ref(args, meta):
    """numpy 对照:按行求和(与顺序无关)后取均值并夹取。"""
    p = np.asarray(args["partial_ptr"], dtype=np.float64)
    total = p.sum(axis=1) * np.float64(args["inv_total_elements"])
    total = np.clip(total, np.float64(args["clamp_min"]), np.float64(args["clamp_max"]))
    out = np.asarray(args["out_ptr"])
    return {"out_ptr": total.astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    rows, block = (int(v) for v in shape)
    if rows <= 0 or block <= 0:
        raise ValueError(f"shape must be positive (P, BLOCK_SIZE), got {shape}")

    # stage-1 的 partial 是 pool 后(rand 的 [0,1))值的局部和,所以在 1/8 网格上
    # 的正值;均值落在 0.5 附近,与 clamp 的 [0,1] 边界贴合处最有意义。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    partial = (rng.integers(0, 32, (rows, block), dtype=np.int32) / 8.0).astype(np.float32)
    # 语义边界:第 0 行均值明显大于 1(夹到上界)、第 1 行为全 0(夹到下界)。
    partial[0, :] = 3.0
    if rows > 1:
        partial[1, :] = 0.0

    args = {"partial_ptr": partial, "out_ptr": np.zeros(rows, np.float32),
            "inv_total_elements": np.float32(1.0 / TOTAL_POOL),
            "clamp_min": np.float32(CLAMP_MIN), "clamp_max": np.float32(CLAMP_MAX)}
    meta = {"BLOCK_SIZE": block}
    return {"args": args, "meta": meta, "grid": (rows,), "outputs": ("out_ptr",),
            "expected": ref(args, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, fused_reduction_kernel_stage2, DTYPES,
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
