"""fused_conv3d_kernel_2: im2col 视角的 3D 卷积 + LeakyReLU + bias/sum + clamp + GELU。

模式: 1D grid 的 GROUP_SIZE_M swizzle GEMM:把输出位置 (n, d, h, w) 摊平成 M、
把 (Cin, KD, KH, KW) 摊平成 K,沿 K 分块用位运算拆出 (ic, kd, kh, kw) 算输入偏移,
权重按 (Cout, Cin*KD*KH*KW) 存,tl.dot(val_x, trans(val_w)) 累积(USE_MMA 决定
是否用带 acc 的 dot 形式,USE_FP16_ACCUM 决定累加器精度);epilogue 是
+bias、LeakyReLU(0.2)、+sum 缓冲、clamp[-1,1]、erf 形式 GELU,按通道最内层布局写出。

文件只有两层:
  ① fused_conv3d_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/fused_conv3d_kernel_2', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.if_constexpr', 'control.loop_runtime_bound', 'creation.arange', 'creation.zeros', 'creation.where', 'math.clamp', 'math.erf', 'memory.load.masked', 'memory.store.masked', 'reduce.sum.axis1', 'shape.trans']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 364290, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "b99df146a4fc88919acc8bc24569fab19728588f961e7d47771b9121d492ade8"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def fused_conv3d_kernel(x_ptr, w_ptr, b_ptr, s_ptr, out_ptr, stride_xn, stride_xc, stride_xd, stride_xh, stride_xw, stride_on, stride_oc, stride_od, stride_oh, stride_ow, N, Cin, Din, Hin, Win, Cout, KD, KH, KW, Dout, Hout, Wout, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr, GROUP_SIZE_M: tl.constexpr, USE_MMA: tl.constexpr, USE_FP16_ACCUM: tl.constexpr):
    """Fused 3D convolution with LeakyReLU, sum addition, clamp, and GELU.
    Optimized for high arithmetic intensity and memory efficiency.
    """
    pid = tl.program_id(0)
    M = N * Dout * Hout * Wout
    K_total = Cin * KD * KH * KW
    num_pid_m = tl.cdiv(M, BLOCK_M)
    num_pid_n = tl.cdiv(Cout, BLOCK_N)
    num_pid_in_group = GROUP_SIZE_M * num_pid_n
    group_id = pid // num_pid_in_group
    first_pid_m = group_id * GROUP_SIZE_M
    group_size_m = min(num_pid_m - first_pid_m, GROUP_SIZE_M)
    pid_m = first_pid_m + pid % group_size_m
    pid_n = pid % num_pid_in_group // group_size_m
    offs_m = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    mask_m = offs_m < M
    mask_n = offs_n < Cout
    dim_hw = Hout * Wout
    dim_dhw = Dout * dim_hw
    n_idx = offs_m // dim_dhw
    rem_n = offs_m % dim_dhw
    d_idx = rem_n // dim_hw
    rem_d = rem_n % dim_hw
    h_idx = rem_d // Wout
    w_idx = rem_d % Wout
    x_base = n_idx * stride_xn + d_idx * stride_xd + h_idx * stride_xh + w_idx * stride_xw
    if USE_FP16_ACCUM:
        acc = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float16)
    else:
        acc = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)
    stride_w_oc = K_total
    stride_w_k = 1
    for k in range(0, K_total, BLOCK_K):
        offs_k = k + tl.arange(0, BLOCK_K)
        mask_k = offs_k < K_total
        kw = offs_k % KW
        rem_kw = offs_k // KW
        kh = rem_kw % KH
        rem_kh = rem_kw // KH
        kd = rem_kh % KD
        ic = rem_kh // KD
        x_k_off = ic * stride_xc + kd * stride_xd + kh * stride_xh + kw * stride_xw
        ptr_x = x_ptr + (x_base[:, None] + x_k_off[None, :])
        val_x = tl.load(ptr_x, mask=mask_m[:, None] & mask_k[None, :], other=0.0)
        ptr_w = w_ptr + (offs_n[:, None] * stride_w_oc + offs_k[None, :] * stride_w_k)
        val_w = tl.load(ptr_w, mask=mask_n[:, None] & mask_k[None, :], other=0.0)
        if USE_MMA:
            acc = tl.dot(val_x, tl.trans(val_w), acc, out_dtype=tl.float32)
        else:
            acc += tl.dot(val_x, tl.trans(val_w))
    if USE_FP16_ACCUM:
        acc = acc.to(tl.float32)
    val_b = tl.load(b_ptr + offs_n, mask=mask_n, other=0.0)
    acc += val_b[None, :]
    acc = tl.where(acc >= 0.0, acc, acc * 0.2)
    val_s = tl.load(s_ptr + offs_n, mask=mask_n, other=0.0)
    acc += val_s[None, :]
    acc = tl.clamp(acc, -1.0, 1.0)
    acc = 0.5 * acc * (1.0 + tl.erf(acc * 0.70710678))
    out_base = n_idx * stride_on + d_idx * stride_od + h_idx * stride_oh + w_idx * stride_ow
    ptr_out = out_ptr + (out_base[:, None] + offs_n[None, :] * stride_oc)
    tl.store(ptr_out, acc, mask=mask_m[:, None] & mask_n[None, :])

# ------------------------------------------------------------------ ② case 层
# 典型用法:体数据卷积 + 激活的 im2col GEMM 实现。原始程序是 (N, Cin, D, H, W) 的
# 体数据;这里取 N=1、Cin=8、8x8x8、Cout=16、核 3x3x3 => 输出 6x6x6(valide)。
#
# (N, Cin, Din, Hin, Win, Cout, KD, KH, KW):
#   典型  (1, 8, 8, 8, 8, 16, 3, 3, 3)   USE_MMA=True、f32 累加
#   规模  (2, 8, 8, 8, 8, 16, 3, 3, 3)   典型规模 ×2:dim0 1->2;USE_MMA=True
#   泛化  (2, 4, 7, 6, 5, 6, 2, 2, 2)   Cout / 位置数都不整除 BLOCK:两处掩码
#         (1, 2, 3, 3, 3, 8, 1, 1, 1)   退化:1x1x1 核,USE_MMA=False 的 dot 分支
SHAPES = ((1, 8, 8, 8, 8, 16, 3, 3, 3), (2, 4, 7, 6, 5, 6, 2, 2, 2), (1, 2, 3, 3, 3, 8, 1, 1, 1))
_USE_MMA = {(1, 8, 8, 8, 8, 16, 3, 3, 3): True, (2, 8, 8, 8, 8, 16, 3, 3, 3): True,
            (2, 4, 7, 6, 5, 6, 2, 2, 2): True,
            (1, 2, 3, 3, 3, 8, 1, 1, 1): False}
# tl.erf 在本机 Triton 上只接受 fp32,所以 GELU 段决定合法域只有 fp32。
DTYPES = ('float32', 'float16', 'bfloat16')
BLOCK_M, BLOCK_N, BLOCK_K, GROUP_SIZE_M = 64, 16, 32, 8


def _dims(shape):
    n, ci, d, h, w, co, kd, kh, kw = (int(v) for v in shape)
    return n, ci, d, h, w, co, kd, kh, kw, d - kd + 1, h - kh + 1, w - kw + 1


def ref(args, meta):
    """numpy 对照:valide conv3d -> leaky(0.2) -> +sum -> clamp -> GELU。"""
    from mathref import erf

    n, ci, d, h, w, co, kd, kh, kw, od, oh, ow = _dims(meta["shape"])
    x = np.asarray(args["x_ptr"], dtype=np.float64).reshape(n, ci, d, h, w)
    wt = np.asarray(args["w_ptr"], dtype=np.float64).reshape(
        co, ci * kd * kh * kw)          # 按 (ic, kd, kh, kw) 摊平
    wt = wt.reshape(co, ci, kd, kh, kw)
    b = np.asarray(args["b_ptr"], dtype=np.float64)
    s = np.asarray(args["s_ptr"], dtype=np.float64)
    acc = np.zeros((n, od, oh, ow, co), dtype=np.float64)
    for kz in range(kd):
        for ky in range(kh):
            for kx in range(kw):
                patch = x[:, :, kz:kz + od, ky:ky + oh, kx:kx + ow]
                acc += np.tensordot(patch, wt[:, :, kz, ky, kx], axes=([1], [1]))
    acc = acc + b[None, None, None, None, :]
    acc = np.where(acc >= 0, acc, acc * 0.2)
    acc = acc + s[None, None, None, None, :]
    acc = np.clip(acc, -1.0, 1.0)
    acc = 0.5 * acc * (1.0 + erf(acc * 0.70710678))
    out = np.asarray(args["out_ptr"])
    return {"out_ptr": acc.reshape(-1).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n, ci, d, h, w, co, kd, kh, kw, od, oh, ow = _dims(shape)
    if min(n, ci, d, h, w, co, kd, kh, kw) <= 0 or min(od, oh, ow) <= 0:
        raise ValueError(f"invalid valide conv3d geometry {shape}")

    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (rng.integers(-16, 16, (n, ci, d, h, w), dtype=np.int16) / 16).astype(np.float32)
    wt = (rng.integers(-8, 9, (co, ci, kd, kh, kw), dtype=np.int16) / 16).astype(np.float32)
    b = (rng.integers(-8, 9, co, dtype=np.int16) / 16).astype(np.float32)
    s = (rng.integers(-8, 9, co, dtype=np.int16) / 16).astype(np.float32)
    # 语义边界:第 0 个样本输入全 0(输出只由 bias + sum 决定)。
    x[0] = 0.0

    m_total = n * od * oh * ow
    args = {"x_ptr": x.reshape(-1), "w_ptr": wt.reshape(co, -1), "b_ptr": b, "s_ptr": s,
            "out_ptr": np.full(m_total * co, -7.0, np.float32),
            "stride_xn": np.int32(ci * d * h * w), "stride_xc": np.int32(d * h * w),
            "stride_xd": np.int32(h * w), "stride_xh": np.int32(w), "stride_xw": np.int32(1),
            "stride_on": np.int32(od * oh * ow * co), "stride_oc": np.int32(1),
            "stride_od": np.int32(oh * ow * co), "stride_oh": np.int32(ow * co),
            "stride_ow": np.int32(co),
            "N": np.int32(n), "Cin": np.int32(ci), "Din": np.int32(d),
            "Hin": np.int32(h), "Win": np.int32(w), "Cout": np.int32(co),
            "KD": np.int32(kd), "KH": np.int32(kh), "KW": np.int32(kw),
            "Dout": np.int32(od), "Hout": np.int32(oh), "Wout": np.int32(ow)}
    meta = {"shape": shape, "BLOCK_M": BLOCK_M, "BLOCK_N": BLOCK_N, "BLOCK_K": BLOCK_K,
            "GROUP_SIZE_M": GROUP_SIZE_M, "USE_MMA": _USE_MMA[shape],
            "USE_FP16_ACCUM": False}
    grid = (((m_total + BLOCK_M - 1) // BLOCK_M) * ((co + BLOCK_N - 1) // BLOCK_N),)
    return {"args": args, "meta": meta, "grid": grid, "outputs": ("out_ptr",),
            "expected": ref(args, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, fused_conv3d_kernel, DTYPES,
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
