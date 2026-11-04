"""fused_conv3d_kernel: 3D 卷积(valide,无 padding)+ LeakyReLU + 通道 bias + clamp + GELU。

模式: 2D grid(输出通道块、输出位置块),用外积写法:每个 (输出通道, 输出位置)
一条 lane,沿输入通道和 (kz, ky, kx) 全部静态展开的 tap 逐个把
w[ic,kz,ky,kx,oc] 与 x[n,ic,od+kz,oh+ky,ow+kx] 相乘累加(权重是通道最内层布局,
指针按 Cout 递进);之后加 bias、LeakyReLU、再加 per-channel 的 sum 缓冲、
clamp 到 [-1, 1],最后用 erf 形式算 GELU 并按通道主序写回。

文件只有两层:
  ① fused_conv3d_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/fused_conv3d_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.loop_runtime_bound', 'control.loop_constexpr', 'creation.arange', 'creation.zeros', 'math.erf', 'math.maximum', 'math.minimum', 'memory.load.masked', 'memory.store.masked', 'shape.view']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "test", "row": 24716, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "c05eea65cfdc324870e9f89b1c8bc5f31eab77ea21b50c3f240cacfd356f642b"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def fused_conv3d_kernel(x_ptr, wT_ptr, b_ptr, sum_ptr, y_ptr, stride_xn, stride_xc, stride_xd, stride_xh, stride_xw, stride_yn, stride_yc, stride_yd, stride_yh, stride_yw, Cin, Cout, OD, OH, OW, N_total, KD: tl.constexpr, KH: tl.constexpr, KW: tl.constexpr, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, NEG_SLOPE: tl.constexpr):
    pid_m = tl.program_id(0)
    pid_n = tl.program_id(1)
    off_m = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    mask_m = off_m < Cout
    off_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    mask_n = off_n < N_total
    ow = off_n % OW
    tmp1 = off_n // OW
    oh = tmp1 % OH
    tmp2 = tmp1 // OH
    od = tmp2 % OD
    n = tmp2 // OD
    base_x_ptrs = x_ptr + (n * stride_xn + od * stride_xd + oh * stride_xh + ow * stride_xw)
    acc = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)
    curr_w_ptr = wT_ptr + off_m[None, :]
    w_step = Cout
    for ic in range(Cin):
        ic_off = ic * stride_xc
        for kz in tl.static_range(KD):
            kz_off = kz * stride_xd
            for ky in tl.static_range(KH):
                ky_off = ky * stride_xh
                x_row_ptrs = base_x_ptrs + (ic_off + kz_off + ky_off)
                for kx in tl.static_range(KW):
                    w_val = tl.load(curr_w_ptr, mask=mask_m[None, :], other=0.0)
                    x_val = tl.load(x_row_ptrs + kx * stride_xw, mask=mask_n, other=0.0)
                    w_v = tl.view(w_val, (BLOCK_M, 1))
                    x_v = tl.view(x_val, (1, BLOCK_N))
                    acc += w_v * x_v
                    curr_w_ptr += w_step
    b_val = tl.load(b_ptr + off_m, mask=mask_m, other=0.0)
    acc += b_val[:, None]
    acc = tl.where(acc > 0, acc, acc * NEG_SLOPE)
    s_val = tl.load(sum_ptr + off_m, mask=mask_m, other=0.0)
    acc += s_val[:, None]
    acc = tl.maximum(tl.minimum(acc, 1.0), -1.0)
    inv_sqrt2 = 0.7071067811865476
    acc = 0.5 * acc * (1.0 + tl.erf(acc * inv_sqrt2))
    y_spatial_off = n * stride_yn + od * stride_yd + oh * stride_yh + ow * stride_yw
    y_ptrs = y_ptr + off_m[:, None] * stride_yc + y_spatial_off[None, :]
    tl.store(y_ptrs, acc, mask=mask_m[:, None] & mask_n[None, :])

# ------------------------------------------------------------------ ② case 层
# 典型用法:体数据卷积 + 激活的融合 kernel。原始程序是 (N, Cin, D, H, W) 的体数据;
# 这里取 N=1、Cin=8、8x8x8、Cout=16、核 3x3x3 => 输出 6x6x6(valide 卷积)。
#
# (N, Cin, D, H, W, Cout, KD, KH, KW):
#   典型  (1, 8, 8, 8, 8, 16, 3, 3, 3)  典型 valide 3x3x3
#   规模  (2, 8, 8, 8, 8, 16, 3, 3, 3)  典型规模 ×2:dim0 1->2
#   规模  (1, 8, 8, 8, 8, 32, 3, 3, 3)  典型规模 ×2:dim5 16->32
#   泛化  (2, 4, 7, 6, 5, 6, 2, 2, 2)   Cout 不整除 BLOCK_M、位置数不整除 BLOCK_N
#         (1, 2, 3, 3, 3, 8, 1, 1, 1)   退化:1x1x1 核
SHAPES = ((1, 8, 8, 8, 8, 16, 3, 3, 3), (2, 4, 7, 6, 5, 6, 2, 2, 2), (1, 4, 8, 8, 8, 32, 3, 3, 3))
# tl.erf 在本机 Triton 上只接受 fp32,所以 GELU 段决定了合法域只有 fp32。
DTYPES = ('float32', 'float16', 'bfloat16')
NEG_SLOPE = 0.1
BLOCK_M, BLOCK_N = 16, 64


def _dims(shape):
    n, ci, d, h, w, co, kd, kh, kw = (int(v) for v in shape)
    return n, ci, d, h, w, co, kd, kh, kw, d - kd + 1, h - kh + 1, w - kw + 1


def ref(args, meta):
    """numpy 对照:float64 的 valide conv3d -> leaky -> +sum -> clamp -> GELU。"""
    from mathref import erf

    n, ci, d, h, w, co, kd, kh, kw, od, oh, ow = _dims(meta["shape"])
    x = np.asarray(args["x_ptr"], dtype=np.float64).reshape(n, ci, d, h, w)
    wt = np.asarray(args["wT_ptr"], dtype=np.float64).reshape(ci, kd, kh, kw, co)
    b = np.asarray(args["b_ptr"], dtype=np.float64)
    s = np.asarray(args["sum_ptr"], dtype=np.float64)
    acc = np.zeros((n, co, od, oh, ow), dtype=np.float64)
    for kz in range(kd):
        for ky in range(kh):
            for kx in range(kw):
                patch = x[:, :, kz:kz + od, ky:ky + oh, kx:kx + ow]
                acc += np.einsum("ncdhw,co->nodhw", patch, wt[:, kz, ky, kx, :])
    acc = acc + b[None, :, None, None, None]
    acc = np.where(acc > 0, acc, acc * np.float64(meta["NEG_SLOPE"]))
    acc = acc + s[None, :, None, None, None]
    acc = np.clip(acc, -1.0, 1.0)
    acc = 0.5 * acc * (1.0 + erf(acc * 0.7071067811865476))
    out = np.asarray(args["y_ptr"])
    # 输出是"通道主序":y[oc][n][od][oh][ow](stride_yc 覆盖整幅图像),
    # 与 numpy 里 (n, oc, ...) 的自然顺序不同,所以先转置再展平。
    return {"y_ptr": acc.transpose(1, 0, 2, 3, 4).reshape(-1).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n, ci, d, h, w, co, kd, kh, kw, od, oh, ow = _dims(shape)
    if min(n, ci, d, h, w, co, kd, kh, kw) <= 0 or min(od, oh, ow) <= 0:
        raise ValueError(f"invalid valide conv3d geometry {shape}")

    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (rng.integers(-16, 16, (n, ci, d, h, w), dtype=np.int16) / 16).astype(np.float32)
    wt = (rng.integers(-8, 9, (ci, kd, kh, kw, co), dtype=np.int16) / 16).astype(np.float32)
    b = (rng.integers(-8, 9, co, dtype=np.int16) / 16).astype(np.float32)
    s = (rng.integers(-8, 9, co, dtype=np.int16) / 16).astype(np.float32)
    # 语义边界:第 0 个样本输入全 0(输出只由 bias + sum 决定,clamp 的负侧也覆盖)。
    x[0] = 0.0

    args = {"x_ptr": x.reshape(-1), "wT_ptr": wt.reshape(-1), "b_ptr": b, "sum_ptr": s,
            "y_ptr": np.full(co * n * od * oh * ow, -7.0, np.float32),
            "stride_xn": np.int32(ci * d * h * w), "stride_xc": np.int32(d * h * w),
            "stride_xd": np.int32(h * w), "stride_xh": np.int32(w), "stride_xw": np.int32(1),
            "stride_yn": np.int32(od * oh * ow), "stride_yc": np.int32(n * od * oh * ow),
            "stride_yd": np.int32(oh * ow), "stride_yh": np.int32(ow), "stride_yw": np.int32(1),
            "Cin": np.int32(ci), "Cout": np.int32(co), "OD": np.int32(od),
            "OH": np.int32(oh), "OW": np.int32(ow), "N_total": np.int32(n * od * oh * ow)}
    meta = {"shape": shape, "KD": kd, "KH": kh, "KW": kw, "BLOCK_M": BLOCK_M,
            "BLOCK_N": BLOCK_N, "NEG_SLOPE": NEG_SLOPE}
    grid = ((co + BLOCK_M - 1) // BLOCK_M, (n * od * oh * ow + BLOCK_N - 1) // BLOCK_N)
    return {"args": args, "meta": meta, "grid": grid, "outputs": ("y_ptr",),
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
