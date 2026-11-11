"""T044 probe operator: minimized fused_conv3d_kernel (no epilogue).

Same structure as ops/suite/dev/fused_conv3d_kernel.py's compile unit --
2D grid (output-channel blocks x output-position blocks), the multi-axis
output-coordinate decomposition (ow/oh/od/n from off_n), the runtime Cin
loop with fully unrolled (kz, ky, kx) taps, the loop-carried weight
pointer advancing by Cout per tap, the outer-product w_v * x_v
accumulation and the channel-major store -- minus the bias/LeakyReLU/
clamp/GELU epilogue, so a probe input (x = element-index ramp, w = one-hot
tap) makes the stored value decode the exact x element each tap read.

Diagnostic helper for the repair task; not part of the delivered program.
"""

OPERATOR = {"name": 'probe/t044_conv3d_probe', "group": 'dev', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.loop_runtime_bound',
                     'control.loop_constexpr', 'creation.arange',
                     'creation.zeros', 'memory.load.masked',
                     'memory.store.masked', 'shape.view']}

import numpy as np
import triton
import triton.language as tl


@triton.jit
def t044_conv3d_probe(x_ptr, wT_ptr, y_ptr, stride_xn, stride_xc, stride_xd, stride_xh, stride_xw, stride_yn, stride_yc, stride_yd, stride_yh, stride_yw, Cin, Cout, OD, OH, OW, N_total, KD: tl.constexpr, KH: tl.constexpr, KW: tl.constexpr, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr):
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
    y_spatial_off = n * stride_yn + od * stride_yd + oh * stride_yh + ow * stride_yw
    y_ptrs = y_ptr + off_m[:, None] * stride_yc + y_spatial_off[None, :]
    tl.store(y_ptrs, acc, mask=mask_m[:, None] & mask_n[None, :])


# shape (N, Cin, D, H, W, Cout, KD, KH, KW) of the failing case
SHAPES = ((2, 4, 7, 6, 5, 6, 2, 2, 2),)
DTYPES = ('float32',)
BLOCK_M, BLOCK_N = 16, 64


def _dims(shape):
    n, ci, d, h, w, co, kd, kh, kw = (int(v) for v in shape)
    return n, ci, d, h, w, co, kd, kh, kw, d - kd + 1, h - kh + 1, w - kw + 1


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n, ci, d, h, w, co, kd, kh, kw, od, oh, ow = _dims(shape)
    x = np.zeros(n * ci * d * h * w, dtype=np.float32)
    wt = np.zeros(ci * kd * kh * kw * co, dtype=np.float32)
    args = {"x_ptr": x, "wT_ptr": wt,
            "y_ptr": np.zeros(co * n * od * oh * ow, np.float32),
            "stride_xn": np.int32(ci * d * h * w), "stride_xc": np.int32(d * h * w),
            "stride_xd": np.int32(h * w), "stride_xh": np.int32(w), "stride_xw": np.int32(1),
            "stride_yn": np.int32(od * oh * ow), "stride_yc": np.int32(n * od * oh * ow),
            "stride_yd": np.int32(oh * ow), "stride_yh": np.int32(ow), "stride_yw": np.int32(1),
            "Cin": np.int32(ci), "Cout": np.int32(co), "OD": np.int32(od),
            "OH": np.int32(oh), "OW": np.int32(ow), "N_total": np.int32(n * od * oh * ow)}
    meta = {"KD": kd, "KH": kh, "KW": kw, "BLOCK_M": BLOCK_M, "BLOCK_N": BLOCK_N}
    grid = ((co + BLOCK_M - 1) // BLOCK_M,
            (n * od * oh * ow + BLOCK_N - 1) // BLOCK_N)
    return {"kernel": t044_conv3d_probe, "args": args, "meta": meta, "grid": grid,
            "outputs": ("y_ptr",), "expected": {"y_ptr": np.zeros(
                co * n * od * oh * ow, np.float32)}}


def make_case(shape=None, dtype=None, seed=None):
    shape = tuple(SHAPES[0] if shape is None else shape)
    dtype = DTYPES[0] if dtype is None else np.dtype(dtype).name
    if shape not in SHAPES or dtype not in DTYPES:
        raise ValueError((shape, dtype))
    return _make_case(shape=shape, dtype=dtype, seed=seed)


def probe_case(w_onehot_flat_index=None, x_ramp=True):
    """One probe payload: x is the element-index ramp (or zeros), w is the
    one-hot at ``w_onehot_flat_index`` (or zeros).  With w one-hot at tap
    (ic, kz, ky, kx)'s base the stored value is exactly the x element
    index that tap read for that lane."""
    case = _make_case()
    n, ci, d, h, w, co, kd, kh, kw, od, oh, ow = _dims(SHAPES[0])
    if x_ramp:
        idx = np.arange(1, n * ci * d * h * w + 1, dtype=np.int64)
        case["args"]["x_ptr"] = (idx * idx).astype(np.float32)
    if w_onehot_flat_index is not None:
        case["args"]["wT_ptr"][int(w_onehot_flat_index)] = 1.0
    return case
