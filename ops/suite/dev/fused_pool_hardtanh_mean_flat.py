"""fused_pool_hardtanh_mean_flat: 2x2 最大池化 + hardtanh + 全局均值,每个 (n, c) 平面一个 program。

模式: 1D grid(N*C),x_base 指到该平面;按 HP 分块,一次 load 2*BLOCK_HP 行 x
2*BLOCK_WP 列(正好是 BLOCK_HP x BLOCK_WP 个 2x2 池化窗),tl.reshape 成
(BLOCK_HP, 2, BLOCK_WP, 2) 后两次 tl.max 得到池化值,再做 hardtanh 夹取、
tl.sum 累加,最后乘 inv_area(1/(HP*WP))写一个标量。

文件只有两层:
  ① fused_pool_hardtanh_mean_flat   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/fused_pool_hardtanh_mean_flat', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.loop_runtime_bound', 'creation.arange', 'math.maximum', 'math.minimum', 'memory.load', 'memory.store', 'shape.reshape', 'reduce.max.axis1', 'reduce.sum.axisall']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 184496, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "aeea965e02800f5cffea649ab13f0d53060bbfddac0b3b770a1d026698fc5ddb"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def fused_pool_hardtanh_mean_flat(x_ptr, out_ptr, N, C, H, W, HP, WP, ht_min, ht_max, inv_area, BLOCK_HP: tl.constexpr, BLOCK_WP: tl.constexpr):
    pid = tl.program_id(0)
    offset_x = pid * H * W
    x_base = x_ptr + offset_x
    acc = 0.0
    offs_w = tl.arange(0, 2 * BLOCK_WP)
    offs_h_input = tl.arange(0, 2 * BLOCK_HP)
    for h in range(0, HP, BLOCK_HP):
        row_start = 2 * h
        ptrs = x_base + (row_start + offs_h_input)[:, None] * W + offs_w[None, :]
        val = tl.load(ptrs)
        val_reshaped = tl.reshape(val, (BLOCK_HP, 2, BLOCK_WP, 2))
        m_w = tl.max(val_reshaped, axis=3)
        pooled = tl.max(m_w, axis=1)
        activated = tl.minimum(tl.maximum(pooled, ht_min), ht_max)
        acc += tl.sum(activated)
    tl.store(out_ptr + pid, acc * inv_area)

# ------------------------------------------------------------------ ② case 层
# 典型用法:卷积/池化塔里的"MaxPool2d(2,2) -> Hardtanh -> 全局均值"。原始程序是
# (N, C, H, W) 的特征图;这里取 N=8、C=16、H=W=64(2x2 池化后 32x32)。
# kernel 里 load 没有列偏移也不要掩码:W 必须恰好等于 2*BLOCK_WP、H = 2*HP、
# 且 HP 是 BLOCK_HP 的整数倍 —— 这是调用方要满足的约束,见下面的注释。
#
# (N, C, H, W):
#   典型  (8, 16, 64, 64)  2x2 池化 => HP=WP=32;整除所有块约束
#   规模  (16, 16, 64, 64) 典型规模 ×2:dim0 8->16;块宽同典型
#   泛化  (2, 3, 32, 32)   更小的特征图(HP=WP=16),换一组块宽
#         (1, 1, 16, 16)   退化:单平面、8x8 池化后
SHAPES = ((8, 16, 64, 64), (2, 3, 32, 32), (1, 1, 16, 16))
_BLOCKS = {(8, 16, 64, 64): (8, 32), (16, 16, 64, 64): (8, 32),
           (2, 3, 32, 32): (16, 16), (1, 1, 16, 16): (4, 8)}
# 原始程序是 fp32;池化+夹取+求和都在 f32 里做。
DTYPES = ('float32', 'float16', 'bfloat16')
HT_MIN, HT_MAX = -1.0, 1.0


def ref(args, meta):
    """numpy 对照:2x2 maxpool -> hardtanh -> 均值(float64)。"""
    n, c, h, w = (int(args[k]) for k in ("N", "C", "H", "W"))
    x = np.asarray(args["x_ptr"], dtype=np.float64).reshape(n * c, h, w)
    hp, wp = h // 2, w // 2
    pooled = x.reshape(n * c, hp, 2, wp, 2).max(axis=(2, 4))
    act = np.clip(pooled, np.float64(args["ht_min"]), np.float64(args["ht_max"]))
    out = np.asarray(args["out_ptr"])
    return {"out_ptr": (act.mean(axis=(1, 2)) * np.float64(args["inv_area"]) * (hp * wp)
                        ).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n, c, h, w = (int(v) for v in shape)
    if min(n, c, h, w) <= 0 or h % 2 or w % 2:
        raise ValueError(f"shape must have even H/W, got {shape}")
    hp, wp = h // 2, w // 2
    block_hp, block_wp = _BLOCKS[(n, c, h, w)]
    if w != 2 * block_wp or hp % block_hp:
        raise ValueError("block sizes are inconsistent with the shape")

    # 特征图是 ReLU 之后的非负值(1/16 网格);第 0 个平面全 0(池化/hardtanh 后
    # 仍为 0),最后一个平面全 4(hardtanh 上界饱和)。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (rng.integers(0, 65, (n * c, h, w), dtype=np.int16) / 16).astype(np.float32)
    x[0, :, :] = 0.0
    x[-1, :, :] = 4.0

    args = {"x_ptr": x.reshape(-1), "out_ptr": np.full(n * c, -7.0, np.float32),
            "N": np.int32(n), "C": np.int32(c), "H": np.int32(h), "W": np.int32(w),
            "HP": np.int32(hp), "WP": np.int32(wp),
            "ht_min": np.float32(HT_MIN), "ht_max": np.float32(HT_MAX),
            "inv_area": np.float32(1.0 / (hp * wp))}
    meta = {"BLOCK_HP": block_hp, "BLOCK_WP": block_wp}
    return {"args": args, "meta": meta, "grid": (n * c,), "outputs": ("out_ptr",),
            "expected": ref(args, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, fused_pool_hardtanh_mean_flat, DTYPES,
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
