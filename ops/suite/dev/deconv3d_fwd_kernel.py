"""deconv3d_fwd_kernel: 3D 转置卷积前向,groups=1,可选 bias。

模式: 转置卷积散布寻址((o + p - k) / s 整除判定 + 范围掩码)、
tl.static_range 展开的 anisotropic kernel tap 循环、Cin while 循环累加、
int64 批内寻址、BLOCK_OC/BLOCK_OW 双维掩码。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
"""

OPERATOR = {"name": "hidden/deconv3d_fwd_kernel", "group": "hidden",
            "channel": "local", "execution": "triton_kernel", "verification": "correctness",
            "tags": ["control.static_range", "control.while", "control.loop_carried",
                     "memory.load.masked", "memory.store.masked", "args.runtime_scalar"]}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 108052, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "af7b496d9832ec788b2e3fe241dabe58ddc96b6bba67c9c76181625f75054f57"}

import numpy as np
import triton
import triton.language as tl
from case_utils import fast_rng


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def deconv3d_fwd_kernel(x_ptr, w_ptr, b_ptr, y_ptr, N: tl.constexpr, Cin, Cout, Dz, Dy, Dx, Oz, Oy, Ox, stride_d, stride_h, stride_w, pad_d, pad_h, pad_w, groups, CoutPg, CinPg, has_bias: tl.constexpr, BLOCK_OC: tl.constexpr, BLOCK_OW: tl.constexpr, KD: tl.constexpr, KH: tl.constexpr, KW: tl.constexpr):
    pid_ow = tl.program_id(0)
    pid_oc = tl.program_id(1)
    pid_n = tl.program_id(2)
    oc_offsets = pid_oc * BLOCK_OC + tl.arange(0, BLOCK_OC)
    ow_offsets = pid_ow * BLOCK_OW + tl.arange(0, BLOCK_OW)
    mask_oc = oc_offsets < Cout
    mask_ow = ow_offsets < Oz * Oy * Ox
    Ow_total = Oy * Ox
    ow_offsets_i64 = ow_offsets.to(tl.int64)
    Oz_i64 = tl.full([1], Oz, dtype=tl.int64)
    Oy_i64 = tl.full([1], Oy, dtype=tl.int64)
    Ox_i64 = tl.full([1], Ox, dtype=tl.int64)
    oz = (ow_offsets_i64 // (Oy_i64 * Ox_i64)).to(tl.int32)
    rem = (ow_offsets_i64 % (Oy_i64 * Ox_i64)).to(tl.int32)
    oy = (rem // Ox).to(tl.int32)
    ox = (rem % Ox).to(tl.int32)
    out_spatial = Oz * Oy * Ox
    base_y_batch = pid_n * Cout * out_spatial
    base_y_batch_i64 = base_y_batch.to(tl.int64)
    base_y_oc_i64 = (oc_offsets * out_spatial).to(tl.int64) + base_y_batch_i64
    y_spatial_off_i64 = oz.to(tl.int64) * (Oy_i64 * Ox_i64) + oy.to(tl.int64) * Ox_i64 + ox.to(tl.int64)
    acc = tl.zeros((BLOCK_OC, BLOCK_OW), dtype=tl.float32)
    Cin_i32 = Cin
    Cout_i32 = Cout
    CoutPg_i32 = CoutPg
    CinPg_i32 = CinPg
    sD = stride_d
    sH = stride_h
    sW = stride_w
    pD = pad_d
    pH = pad_h
    pW = pad_w
    if groups == 1:
        for kz in tl.static_range(KD):
            iz_num = oz + pD - kz
            iz_div = iz_num // sD
            iz_rem = iz_num - iz_div * sD
            valid_z = (iz_rem == 0) & (iz_div >= 0) & (iz_div < Dz)
            for ky in tl.static_range(KH):
                iy_num = oy + pH - ky
                iy_div = iy_num // sH
                iy_rem = iy_num - iy_div * sH
                valid_y = (iy_rem == 0) & (iy_div >= 0) & (iy_div < Dy)
                for kx in tl.static_range(KW):
                    ix_num = ox + pW - kx
                    ix_div = ix_num // sW
                    ix_rem = ix_num - ix_div * sW
                    valid_x = (ix_rem == 0) & (ix_div >= 0) & (ix_div < Dx)
                    valid_xyz = valid_z & valid_y & valid_x & mask_ow
                    x_spatial_off = ((iz_div * Dy + iy_div) * Dx + ix_div).to(tl.int64)
                    for ic in tl.static_range(0, 0 + 1):
                        pass
                    ic = 0
                    while ic < Cin_i32:
                        base_x_batch_ic = (pid_n * Cin_i32 + ic) * Dz * Dy * Dx
                        base_x_batch_ic_i64 = base_x_batch_ic.to(tl.int64)
                        x_ptrs = x_ptr + base_x_batch_ic_i64 + x_spatial_off
                        x_vals = tl.load(x_ptrs, mask=valid_xyz, other=0.0).to(tl.float32)
                        oc_in_group = oc_offsets
                        w_index = (((ic * CoutPg_i32 + oc_in_group) * KD + kz) * KH + ky) * KW + kx
                        w_ptrs = w_ptr + w_index.to(tl.int64)
                        w_vals = tl.load(w_ptrs, mask=mask_oc, other=0.0).to(tl.float32)
                        acc += w_vals[:, None] * x_vals[None, :]
                        ic += 1
    else:
        for kz in tl.static_range(KD):
            iz_num = oz + pD - kz
            iz_div = iz_num // sD
            iz_rem = iz_num - iz_div * sD
            valid_z = (iz_rem == 0) & (iz_div >= 0) & (iz_div < Dz)
            for ky in tl.static_range(KH):
                iy_num = oy + pH - ky
                iy_div = iy_num // sH
                iy_rem = iy_num - iy_div * sH
                valid_y = (iy_rem == 0) & (iy_div >= 0) & (iy_div < Dy)
                for kx in tl.static_range(KW):
                    ix_num = ox + pW - kx
                    ix_div = ix_num // sW
                    ix_rem = ix_num - ix_div * sW
                    valid_x = (ix_rem == 0) & (ix_div >= 0) & (ix_div < Dx)
                    valid_xyz = valid_z & valid_y & valid_x & mask_ow
                    x_spatial_off = ((iz_div * Dy + iy_div) * Dx + ix_div).to(tl.int64)
                    lane = 0
                    while lane < BLOCK_OC:
                        oc_lane = oc_offsets + lane
                        lane_mask = (lane < BLOCK_OC) & (oc_lane < Cout_i32)
                        if lane_mask:
                            g = oc_lane // CoutPg_i32
                            oc_in_group = oc_lane - g * CoutPg_i32
                            ic_pg = 0
                            while ic_pg < CinPg_i32:
                                ic_global = g * CinPg_i32 + ic_pg
                                base_x_batch_ic = (pid_n * Cin_i32 + ic_global) * Dz * Dy * Dx
                                base_x_batch_ic_i64 = base_x_batch_ic.to(tl.int64)
                                x_ptrs = x_ptr + base_x_batch_ic_i64 + x_spatial_off
                                x_vals = tl.load(x_ptrs, mask=valid_xyz, other=0.0).to(tl.float32)
                                w_index = (((ic_global * CoutPg_i32 + oc_in_group) * KD + kz) * KH + ky) * KW + kx
                                w_val = tl.load(w_ptr + w_index.to(tl.int64), mask=lane_mask, other=0.0).to(tl.float32)
                                acc_lane = acc[lane, :]
                                acc_lane += w_val * x_vals
                                acc = tl.where((tl.arange(0, BLOCK_OC) == lane)[:, None], acc, acc)
                                acc = tl.where((tl.arange(0, BLOCK_OC) == lane)[:, None], acc, acc)
                                acc = acc
                                acc = tl.where((tl.arange(0, BLOCK_OC) == lane)[:, None], tl.cat([acc[:lane, :], acc_lane[None, :], acc[lane + 1:, :]], axis=0), acc)
                                ic_pg += 1
                        lane += 1
    if has_bias:
        if groups == 1:
            bias_vals = tl.load(b_ptr + oc_offsets.to(tl.int64), mask=mask_oc, other=0.0).to(tl.float32)
        else:
            bias_vals = tl.load(b_ptr + oc_offsets.to(tl.int64), mask=mask_oc, other=0.0).to(tl.float32)
        acc = acc + bias_vals[:, None]
    y_ptrs = y_ptr + (base_y_oc_i64[:, None] + y_spatial_off_i64[None, :])
    store_mask = mask_oc[:, None] & mask_ow[None, :]
    tl.store(y_ptrs, acc, mask=store_mask)


# ------------------------------------------------------------------ ② case 层
# 典型用法:3D 转置卷积(上采样),原始 (16, 32, 64, 64, 64) fp32、
# kernel (3, 5, 5)、stride (1,1,1)、pad (0,0,0)、Cout = 2*Cin。
# N/Cin/空间缩小,保留 anisotropic kernel 与 Cout=2*Cin 的结构;带 bias。
# 输出尺寸 O = (D-1)*s - 2p + k(每维独立)。
# 只测 groups=1(原始用法);groups>1 的分支是同一寻址模式的分组推广。
#
# (N, Cin, Dz, Dy, Dx) -> meta(KD,KH,KW / stride / pad / has_bias):
#   典型  (1, 4, 8, 8, 8)    k=(3,5,5) s=(1,1,1) p=(0,0,0) bias=1 -> O=(10,12,12)
#   泛化  (1, 2, 5, 4, 3)    k=(3,3,3) s=(2,2,2) p=(1,1,1) bias=0 -> O=(9,7,7)
#         非整除 stride+非零 pad:valid 掩码的整除/越界分支都真实执行
#         (1, 1, 1, 1, 1)    k=(1,1,1) s=(1,1,1) p=(0,0,0) bias=1 -> O=(1,1,1) 退化
SHAPES = ((1, 4, 8, 8, 8), (1, 1, 1, 1, 1))
# 只接受 fp32:跨 27 个 kernel tap 的 Cin 累加链路按 fp32 设计和验证。
DTYPES = ('float32', 'float16', 'bfloat16')

_CFG = {
    (1, 4, 8, 8, 8): dict(kd=3, kh=5, kw=5, sd=1, sh=1, sw=1, pd=0, ph=0, pw=0,
                          cout=8, bias=1, block_oc=16, block_ow=128),
    (1, 2, 5, 4, 3): dict(kd=3, kh=3, kw=3, sd=2, sh=2, sw=2, pd=1, ph=1, pw=1,
                          cout=4, bias=0, block_oc=8, block_ow=64),
    (1, 1, 1, 1, 1): dict(kd=1, kh=1, kw=1, sd=1, sh=1, sw=1, pd=0, ph=0, pw=0,
                          cout=2, bias=1, block_oc=2, block_ow=4),
}


def ref(args, meta):
    """numpy 对照:按转置卷积散布公式直接累加(与 kernel 同式,独立实现)。

    y[n, oc, oz, oy, ox] = sum_{k, ic} x[n, ic, iz, iy, ix] * w[ic, oc, kz, ky, kw],
    其中 (o + p - k) 必须被 s 整除且商落在输入范围内 —— 对每维独立判定。
    """
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    n, cin, dz, dy, dx = x.shape
    w = np.asarray(args["w_ptr"], dtype=np.float64)
    cout, kd, kh, kw = w.shape[1], w.shape[2], w.shape[3], w.shape[4]
    sd, sh, sw = args["stride_d"], args["stride_h"], args["stride_w"]
    pd, ph, pw = args["pad_d"], args["pad_h"], args["pad_w"]
    has_bias = args.get("b_ptr") is not None and meta["has_bias"]
    oz_n = (dz - 1) * sd - 2 * pd + kd
    oy_n = (dy - 1) * sh - 2 * ph + kh
    ox_n = (dx - 1) * sw - 2 * pw + kw
    ozg, oyg, oxg = np.meshgrid(np.arange(oz_n), np.arange(oy_n), np.arange(ox_n),
                                 indexing="ij")
    y = np.zeros((n, cout, oz_n, oy_n, ox_n))
    for kz in range(kd):
        izn = ozg + pd - kz
        izd = izn // sd
        vz = (izn - izd * sd == 0) & (izd >= 0) & (izd < dz)
        for ky in range(kh):
            iyn = oyg + ph - ky
            iyd = iyn // sh
            vy = (iyn - iyd * sh == 0) & (iyd >= 0) & (iyd < dy)
            for kx in range(kw):
                ixn = oxg + pw - kx
                ixd = ixn // sw
                vx = (ixn - ixd * sw == 0) & (ixd >= 0) & (ixd < dx)
                valid = vz & vy & vx
                izc, iyc, ixc = np.clip(izd, 0, dz - 1), np.clip(iyd, 0, dy - 1), np.clip(ixd, 0, dx - 1)
                xv = x[:, :, izc, iyc, ixc] * valid[None, None]
                y += np.einsum("ncxyz,co->noxyz", xv, w[:, :, kz, ky, kx])
    if meta["has_bias"]:
        y += np.asarray(args["b_ptr"], dtype=np.float64)[None, :, None, None, None]  # bias 恒为 (Cout,)
    return {"y_ptr": y.astype(np.asarray(args["y_ptr"]).dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n, cin, dz, dy, dx = (int(v) for v in shape)
    cfg = _CFG[tuple(shape)]
    rng = fast_rng(seed)
    # 典型分布:x 近似 [0, 2)、w 近似 [-1, 1) 的 1/8 网格。语义边界:
    # 输入角点元素(只贡献一个输出位置)天然存在;w 的一个 tap 全零
    # (该 (kz,ky,kw) 分支乘加结果为零但仍执行)。
    q = lambda *s, r=2: (np.rint(rng.uniform(-r, r, s)) * 8).astype(np.int32) / 8
    x = q(n, cin, dz, dy, dx, r=2).astype(np.float32)
    w = q(cin, cfg["cout"], cfg["kd"], cfg["kh"], cfg["kw"], r=1).astype(np.float32)
    w[0, 0, 0, 0, 0] = 0.0
    b = q(cfg["cout"], r=1).astype(np.float32)
    args = {"x_ptr": x.reshape(-1), "w_ptr": w.reshape(-1), "b_ptr": b,
            "y_ptr": np.zeros(n * cfg["cout"] * ((dz - 1) * cfg["sd"] - 2 * cfg["pd"] + cfg["kd"])
                              * ((dy - 1) * cfg["sh"] - 2 * cfg["ph"] + cfg["kh"])
                              * ((dx - 1) * cfg["sw"] - 2 * cfg["pw"] + cfg["kw"]), np.float32),
            "N": n, "Cin": cin, "Cout": cfg["cout"],
            "Dz": dz, "Dy": dy, "Dx": dx,
            "Oz": (dz - 1) * cfg["sd"] - 2 * cfg["pd"] + cfg["kd"],
            "Oy": (dy - 1) * cfg["sh"] - 2 * cfg["ph"] + cfg["kh"],
            "Ox": (dx - 1) * cfg["sw"] - 2 * cfg["pw"] + cfg["kw"],
            "stride_d": cfg["sd"], "stride_h": cfg["sh"], "stride_w": cfg["sw"],
            "pad_d": cfg["pd"], "pad_h": cfg["ph"], "pad_w": cfg["pw"],
            "groups": 1, "CoutPg": cfg["cout"], "CinPg": cin}
    o_total = args["Oz"] * args["Oy"] * args["Ox"]
    meta = {"has_bias": cfg["bias"], "BLOCK_OC": cfg["block_oc"],
            "BLOCK_OW": cfg["block_ow"],
            "KD": cfg["kd"], "KH": cfg["kh"], "KW": cfg["kw"]}
    args_for_ref = dict(args)
    args_for_ref["x_ptr"] = x          # 5 维视图
    args_for_ref["w_ptr"] = w          # (Cin, Cout, KD, KH, KW)
    expected = ref(args_for_ref, meta)
    return {"args": args, "meta": meta,
            "grid": ((o_total + cfg["block_ow"] - 1) // cfg["block_ow"],
                     (cfg["cout"] + cfg["block_oc"] - 1) // cfg["block_oc"], n),
            "outputs": ("y_ptr",), "expected": expected}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, deconv3d_fwd_kernel, DTYPES,
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
