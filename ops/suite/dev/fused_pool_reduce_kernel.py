"""fused_pool_reduce_kernel: 2x2 最大池化 + bias + hardtanh + 全局均值 + tanh,每通道一个 program。

模式: 1D grid(N*C),每个 program 处理一个 (n, c) 平面:双层块循环
(for h / for w over 池化后的网格),把每个池化窗的 4 个输入装进
(BLOCK_H, 2, BLOCK_W, 2) 再两次 tl.max,然后加 per-channel bias、hardtanh 夹取、
累加;最后除以 P(池化后元素数)并用 2*sigmoid(-2*mean)-1 求 tanh。
池化网格的尾块由两次 reshape 出来的 mask 处理。

文件只有两层:
  ① fused_pool_reduce_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/fused_pool_reduce_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.loop_runtime_bound', 'creation.arange', 'math.maximum', 'math.minimum', 'math.sigmoid', 'memory.load.masked', 'memory.store', 'shape.reshape', 'reduce.max.axis1', 'reduce.sum.axisall']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 184305, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "30279f99de2bca9dcf21933a9c240b3e1f0717ec5d8b0df1f6aeb2c9d0942b8a"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def fused_pool_reduce_kernel(x_ptr, bias_ptr, out_ptr, N, C, H, W, H_pool, W_pool, P, hard_min, hard_max, BLOCK_H: tl.constexpr, BLOCK_W: tl.constexpr):
    pid = tl.program_id(0)
    c = pid % C
    n = pid // C
    b_val = tl.load(bias_ptr + c)
    base_offset = (n * C + c) * H * W
    x_base = x_ptr + base_offset
    acc = 0.0
    for h_start in range(0, H_pool, BLOCK_H):
        for w_start in range(0, W_pool, BLOCK_W):
            offs_h_p = h_start + tl.arange(0, BLOCK_H)
            mask_h_p = offs_h_p < H_pool
            offs_w_p = w_start + tl.arange(0, BLOCK_W)
            mask_w_p = offs_w_p < W_pool
            h_in_base = offs_h_p[:, None] * 2
            h_offsets = h_in_base + tl.arange(0, 2)[None, :]
            offs_h_in = tl.reshape(h_offsets, (BLOCK_H * 2,))
            w_in_base = offs_w_p[:, None] * 2
            w_offsets = w_in_base + tl.arange(0, 2)[None, :]
            offs_w_in = tl.reshape(w_offsets, (BLOCK_W * 2,))
            ptr_grid = x_base + offs_h_in[:, None] * W + offs_w_in[None, :]
            m_h_exp = tl.reshape(mask_h_p[:, None] + tl.zeros((1, 2), dtype=tl.int1), (BLOCK_H * 2,))
            m_w_exp = tl.reshape(mask_w_p[:, None] + tl.zeros((1, 2), dtype=tl.int1), (BLOCK_W * 2,))
            load_mask = m_h_exp[:, None] & m_w_exp[None, :]
            tile = tl.load(ptr_grid, mask=load_mask, other=float('-inf'))
            tile_r = tl.reshape(tile, (BLOCK_H, 2, BLOCK_W, 2))
            max1 = tl.max(tile_r, axis=3)
            pool_val = tl.max(max1, axis=1)
            pool_val = pool_val + b_val
            pool_val = tl.minimum(tl.maximum(pool_val, hard_min), hard_max)
            valid_mask = mask_h_p[:, None] & mask_w_p[None, :]
            pool_val = tl.where(valid_mask, pool_val, 0.0)
            acc += tl.sum(pool_val)
    mean_val = acc / P
    z = -2.0 * mean_val
    sig = 1.0 / (1.0 + tl.exp(z))
    out_val = 2.0 * sig - 1.0
    tl.store(out_ptr + pid, out_val)

# ------------------------------------------------------------------ ② case 层
# 典型用法:卷积塔的"MaxPool2d(2,2) -> +bias -> Hardtanh -> 全局均值 -> tanh"。
# 原始程序是 (N, C, H, W) 的特征图;这里取 N=8、C=16、H=W=64 => 池化后 32x32。
#
# (N, C, H, W):
#   典型  (8, 16, 64, 64)  64x64 -> 32x32 池化网格,整除 BLOCK
#   规模  (16, 16, 64, 64)  典型规模 ×2:dim0 8->16
#   规模  (8, 16, 128, 64)  典型规模 ×2:dim2 64->128
#   泛化  (2, 3, 30, 34)   池化网格 15x17 不整除 BLOCK_H/BLOCK_W:两块都有尾块
#         (1, 1, 6, 8)     退化:单个 3x4 池化网格
SHAPES = ((8, 16, 64, 64), (2, 3, 30, 34))
# 原始程序是 fp32;收尾的 sigmoid 也用 exp,只声明 f32。
DTYPES = ('float32', 'float16', 'bfloat16')
HT_MIN, HT_MAX = -1.0, 1.0
BLOCK_H, BLOCK_W = 16, 16


def ref(args, meta):
    """numpy 对照:2x2 maxpool(越界填 -inf)-> +bias -> clamp -> 均值 -> tanh。"""
    n, c, h, w = (int(args[k]) for k in ("N", "C", "H", "W"))
    hp, wp = int(args["H_pool"]), int(args["W_pool"])
    x = np.asarray(args["x_ptr"], dtype=np.float64).reshape(n * c, h, w)
    bias = np.asarray(args["bias_ptr"], dtype=np.float64)
    out = np.asarray(args["out_ptr"])
    padded = np.full((n * c, hp * 2, wp * 2), -np.inf)
    padded[:, :h, :w] = x
    pooled = padded.reshape(n * c, hp, 2, wp, 2).max(axis=(2, 4))
    pooled = pooled + bias.reshape(n * c)[:, None, None]
    pooled = np.clip(pooled, np.float64(args["hard_min"]), np.float64(args["hard_max"]))
    mean = pooled.sum(axis=(1, 2)) / np.float64(args["P"])
    # kernel: z = -2*mean, sig = 1/(1+e^z), out = 2*sig-1 == tanh(mean)
    return {"out_ptr": np.tanh(mean).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n, c, h, w = (int(v) for v in shape)
    if min(n, c, h, w) <= 0:
        raise ValueError(f"shape must be positive (N, C, H, W), got {shape}")
    hp, wp = (h + 1) // 2, (w + 1) // 2

    # 特征图取 1/16 网格上的 [-4, 4);bias 是 per-channel 的 1/16 网格值。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (rng.integers(-64, 65, (n * c, h, w), dtype=np.int16) / 16).astype(np.float32)
    bias = (rng.integers(-8, 9, c, dtype=np.int16) / 16).astype(np.float32)
    # 语义边界:第 0 个平面全为 +4(hardtanh 上饱和 -> 均值 = 上界)。
    x[0, :, :] = 4.0
    bias[0] = 0.0

    args = {"x_ptr": x.reshape(-1), "bias_ptr": np.resize(bias, n * c),
            "out_ptr": np.full(n * c, -7.0, np.float32),
            "N": np.int32(n), "C": np.int32(c), "H": np.int32(h), "W": np.int32(w),
            "H_pool": np.int32(hp), "W_pool": np.int32(wp),
            "P": np.int32(hp * wp), "hard_min": np.float32(HT_MIN),
            "hard_max": np.float32(HT_MAX)}
    meta = {"BLOCK_H": BLOCK_H, "BLOCK_W": BLOCK_W}
    return {"args": args, "meta": meta, "grid": (n * c,), "outputs": ("out_ptr",),
            "expected": ref(args, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, fused_pool_reduce_kernel, DTYPES,
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
