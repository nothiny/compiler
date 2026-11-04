"""_softmax_bias_scale_sigmoid_fused_nchw_inplace: NCHW 上的两趟 softmax + bias/scale + sigmoid(in-place)。

模式: 2D grid(batch、S 方向一块)。第一趟用 tl.static_range(0, C, BLOCK_C) 沿
通道分块做 online softmax 的 max/sum 递推;第二趟再走一遍通道块,算
sm = exp(x-m)/l,再 z = sm*scale + bias*scale,最后用数值稳定的 sigmoid
(按符号选 1/(1+e^-|z|) 或 e^-|z|/(1+e^-|z|))写回同一缓冲区。
C/S/SCALE 与输出精度分支都是 constexpr。

文件只有两层:
  ① _softmax_bias_scale_sigmoid_fused_nchw_inplace   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/softmax_bias_scale_sigmoid_fused_nchw_inplace', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.if_constexpr', 'control.loop_constexpr', 'creation.full', 'math.abs', 'math.exp', 'math.maximum', 'math.fma', 'memory.load.masked', 'memory.store.masked', 'reduce.max.axis0', 'reduce.sum.axis0']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 368441, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "51a04d36102f6a1141b499f4eda0ddc91c10a9ef5cb85696a15f43a4d9016ffe"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def _softmax_bias_scale_sigmoid_fused_nchw_inplace(x_ptr, b_ptr, C: tl.constexpr, S: tl.constexpr, SCALE: tl.constexpr, BLOCK_S: tl.constexpr, BLOCK_C: tl.constexpr, OUT_FP16: tl.constexpr, OUT_BF16: tl.constexpr):
    pid_n = tl.program_id(0)
    pid_s = tl.program_id(1)
    s = pid_s * BLOCK_S + tl.arange(0, BLOCK_S)
    s_mask = s < S
    base = pid_n.to(tl.int64) * (C * S)
    s64 = s.to(tl.int64)
    m = tl.full([BLOCK_S], -float('inf'), tl.float32)
    l = tl.zeros([BLOCK_S], tl.float32)
    for c0 in tl.static_range(0, C, BLOCK_C):
        c = c0 + tl.arange(0, BLOCK_C)
        c_mask = c < C
        c64 = c.to(tl.int64)
        ptrs = x_ptr + base + c64[:, None] * S + s64[None, :]
        x = tl.load(ptrs, mask=c_mask[:, None] & s_mask[None, :], other=-float('inf'), eviction_policy='evict_first').to(tl.float32)
        x_max = tl.max(x, axis=0)
        x_max = tl.where(s_mask, x_max, 0.0)
        ex = tl.exp(x - x_max[None, :])
        ex = tl.where(c_mask[:, None] & s_mask[None, :], ex, 0.0)
        l2 = tl.sum(ex, axis=0)
        m_new = tl.maximum(m, x_max)
        l = l * tl.exp(m - m_new) + l2 * tl.exp(x_max - m_new)
        m = m_new
    m = tl.where(s_mask, m, 0.0)
    l = tl.where(s_mask, l, 1.0)
    scale_f = tl.full([], SCALE, tl.float32)
    for c0 in tl.static_range(0, C, BLOCK_C):
        c = c0 + tl.arange(0, BLOCK_C)
        c_mask = c < C
        c64 = c.to(tl.int64)
        ptrs = x_ptr + base + c64[:, None] * S + s64[None, :]
        x = tl.load(ptrs, mask=c_mask[:, None] & s_mask[None, :], other=-float('inf'), eviction_policy='evict_first').to(tl.float32)
        num = tl.exp(x - m[None, :])
        sm = num / l[None, :]
        b = tl.load(b_ptr + c64, mask=c_mask, other=0.0, eviction_policy='evict_last').to(tl.float32)
        z = tl.fma(sm, scale_f, b[:, None] * scale_f)
        is_pos = z >= 0
        ez = tl.exp(-tl.abs(z))
        y = tl.where(is_pos, 1.0 / (1.0 + ez), ez / (1.0 + ez))
        if OUT_FP16:
            y = y.to(tl.float16)
        elif OUT_BF16:
            y = y.to(tl.bfloat16)
        else:
            y = y.to(tl.float32)
        tl.store(ptrs, y, mask=c_mask[:, None] & s_mask[None, :])

# ------------------------------------------------------------------ ② case 层
# 典型用法:attention 之后的 softmax + 门控(scale + per-channel bias + sigmoid),
# 原地覆盖输入以省一次 HBM 往返。原始程序是 attention 的 (4, 64, 4096) 输出;
# 这里保留 S=4096、减小 batch 与 C。
#
# (N, C, S):
#   典型  (2, 64, 4096)  C=64、S=4096(softmax 沿 C)
#   规模  (4, 64, 4096)  典型规模 ×2:dim0 2->4
#   规模  (2, 64, 8192)  典型规模 ×2:dim2 4096->8192
#   泛化  (2, 40, 1000)  C、S 都不整除块宽
#         (1, 1, 1)     退化:单元素(C=1 时 softmax 恒为 1)
SHAPES = ((2, 64, 128), (2, 40, 100))
# 原始程序是 fp32;OUT_FP16/OUT_BF16 分支覆盖半精度写回(计算仍在 f32)。
DTYPES = ("float32", "float16", "bfloat16")
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}
BLOCK_S, BLOCK_C, SCALE = 64, 32, 1.25


def ref(args, meta):
    """numpy 对照:沿 C 的 softmax,再 (sm*SCALE + bias*SCALE) 过 sigmoid,float64。"""
    n, c, s = int(args["N"]), int(meta["C"]), int(meta["S"])
    x = np.asarray(args["x_ptr"], dtype=np.float64).reshape(n, c, s)
    b = np.asarray(args["b_ptr"], dtype=np.float64)
    m = x.max(axis=1, keepdims=True)
    l = np.exp(x - m).sum(axis=1, keepdims=True)
    sm = np.exp(x - m) / l
    z = sm * np.float64(meta["SCALE"]) + b[None, :, None] * np.float64(meta["SCALE"])
    y = 1.0 / (1.0 + np.exp(-z))
    out = np.asarray(args["x_ptr"])
    return {"x_ptr": y.reshape(-1).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n, c, s = (int(v) for v in shape)
    if min(n, c, s) <= 0:
        raise ValueError(f"shape must be positive (N, C, S), got {shape}")
    host = _HOST_DTYPE[dtype]

    # attention 输出(softmax 前)是 1/16 网格上的 ~N(0,2);bias 是 per-channel 的
    # 偏置(1/16 网格)。第 0 个通道 bias 取 0,第一个 batch 的 logits 全相同
    # (softmax 均匀),把 m/l 的边界钉住。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (np.clip(np.rint(rng.standard_normal((n, c, s), dtype=np.float32) * 32),
                 -128, 127) / 16).astype(host)
    b = (rng.integers(-16, 17, c, dtype=np.int16) / 16).astype(host)
    b[0] = 0.0
    x[0, :, :] = 0.0

    out_dtype = np.float32 if dtype == "bfloat16" else np.dtype(dtype)
    args = {"x_ptr": x.reshape(-1).astype(out_dtype), "b_ptr": b, "N": np.int32(n)}
    meta = {"C": c, "S": s, "SCALE": SCALE, "BLOCK_S": BLOCK_S, "BLOCK_C": BLOCK_C,
            "OUT_FP16": dtype == "float16", "OUT_BF16": dtype == "bfloat16"}
    grid = (n, (s + BLOCK_S - 1) // BLOCK_S)
    case = {"args": args, "meta": meta, "grid": grid, "outputs": ("x_ptr",),
            "expected": ref(args, meta)}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {"x_ptr": "bfloat16", "b_ptr": "bfloat16"}
    case["comparison"] = {"x_ptr": {"comparator": "allclose", "exact": False,
                                    "rtol": 5e-3, "atol": 5e-3, "equal_nan": True}}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, _softmax_bias_scale_sigmoid_fused_nchw_inplace, DTYPES,
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
