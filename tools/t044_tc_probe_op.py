"""T044 probe operator: minimized transposed_conv3d (makora_transposed_conv3d_kernel).

Same structure -- pid decomposition, per-tap runtime loops, masked loads,
tl.dot, carried acc, permute, channel-last-ish store -- with a switch that
removes the runtime ``if val_d % Stride == 0`` guard by folding it into the
load masks (semantics-preserving: the guarded acc update becomes a masked
contribution of zero).  For the failing shape Stride=1 makes the guard
always true, so both forms compute the same function; a divergence between
them isolates the runtime-if + IME-dot interaction.

Diagnostic helper for the repair task; not part of the delivered program.
"""

OPERATOR = {"name": 'probe/t044_tc_probe', "group": 'dev', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.for_range', 'control.if',
                     'control.loop_carried', 'creation.arange', 'creation.zeros',
                     'linalg.dot', 'memory.load.masked', 'memory.store.masked',
                     'shape.permute', 'shape.reshape', 'tile.2d', 'tile.3d']}

import numpy as np
import triton
import triton.language as tl


@triton.jit
def t044_tc_probe(X, W, Bias, Out, stride_xn, stride_xc, stride_xd, stride_xh, stride_xw, stride_wk_k, stride_wk_cin, stride_wk_cout, stride_on, stride_oc, stride_od, stride_oh, stride_ow, Cin_per_group, Cout_per_group, Groups, Din, Hin, Win, Dout, Hout, Wout, K, Stride, Padding, USE_IF: tl.constexpr, BLOCK_H: tl.constexpr, BLOCK_W: tl.constexpr, BLOCK_CIN: tl.constexpr, BLOCK_COUT: tl.constexpr, HAS_BIAS: tl.constexpr):
    pid_spatial = tl.program_id(0)
    pid_cout = tl.program_id(1)
    pid_z = tl.program_id(2)
    rem_z = pid_z
    d_out = rem_z % Dout
    rem_z = rem_z // Dout
    group = rem_z % Groups
    batch = rem_z // Groups
    num_tiles_w = tl.cdiv(Wout, BLOCK_W)
    tile_y = pid_spatial // num_tiles_w
    tile_x = pid_spatial % num_tiles_w
    off_h = tile_y * BLOCK_H + tl.arange(0, BLOCK_H)
    off_w = tile_x * BLOCK_W + tl.arange(0, BLOCK_W)
    mask_h = off_h < Hout
    mask_w = off_w < Wout
    off_cout = pid_cout * BLOCK_COUT + tl.arange(0, BLOCK_COUT)
    mask_cout = off_cout < Cout_per_group
    global_cout = group * Cout_per_group + off_cout
    base_cin_group = group * Cin_per_group
    ptr_out = Out + batch * stride_on + global_cout[None, :, None] * stride_oc + d_out * stride_od + off_h[:, None, None] * stride_oh + off_w[None, None, :] * stride_ow
    acc = tl.zeros((BLOCK_H, BLOCK_W, BLOCK_COUT), dtype=tl.float32)
    val_d_base = d_out + Padding
    val_h_base = off_h + Padding
    val_w_base = off_w + Padding
    for kz in range(K):
        val_d = val_d_base - kz
        if USE_IF:
            if val_d % Stride == 0:
                d_in = val_d // Stride
                if d_in >= 0 and d_in < Din:
                    off_x_d = d_in * stride_xd
                    for ky in range(K):
                        val_h = val_h_base - ky
                        mask_h_k = (val_h % Stride == 0) & (val_h >= 0)
                        h_in = val_h // Stride
                        mask_h_k = mask_h_k & (h_in < Hin) & mask_h
                        for kx in range(K):
                            val_w = val_w_base - kx
                            mask_w_k = (val_w % Stride == 0) & (val_w >= 0)
                            w_in = val_w // Stride
                            mask_w_k = mask_w_k & (w_in < Win) & mask_w
                            mask_sw = mask_h_k[:, None] & mask_w_k[None, :]
                            off_x_spatial = off_x_d + h_in[:, None] * stride_xh + w_in[None, :] * stride_xw
                            k_idx = kz * (K * K) + ky * K + kx
                            off_w_k = k_idx * stride_wk_k
                            for cin_blk in range(0, Cin_per_group, BLOCK_CIN):
                                off_cin = cin_blk + tl.arange(0, BLOCK_CIN)
                                mask_cin = off_cin < Cin_per_group
                                ptr_x = X + batch * stride_xn + (base_cin_group + off_cin)[None, None, :] * stride_xc + off_x_spatial[:, :, None]
                                mask_x_load = mask_sw[:, :, None] & mask_cin[None, None, :]
                                x_tile = tl.load(ptr_x, mask=mask_x_load, other=0.0)
                                ptr_w = W + off_w_k + off_cin[:, None] * stride_wk_cin + off_cout[None, :] * stride_wk_cout
                                mask_w_load = mask_cin[:, None] & mask_cout[None, :]
                                w_tile = tl.load(ptr_w, mask=mask_w_load, other=0.0)
                                x_flat = tl.reshape(x_tile, (BLOCK_H * BLOCK_W, BLOCK_CIN))
                                acc_flat = tl.dot(x_flat, w_tile)
                                acc += tl.reshape(acc_flat, (BLOCK_H, BLOCK_W, BLOCK_COUT))
        else:
            d_in = val_d // Stride
            mask_d_k = (val_d % Stride == 0) & (d_in >= 0) & (d_in < Din)
            off_x_d = d_in * stride_xd
            for ky in range(K):
                val_h = val_h_base - ky
                mask_h_k = (val_h % Stride == 0) & (val_h >= 0)
                h_in = val_h // Stride
                mask_h_k = mask_h_k & (h_in < Hin) & mask_h
                for kx in range(K):
                    val_w = val_w_base - kx
                    mask_w_k = (val_w % Stride == 0) & (val_w >= 0)
                    w_in = val_w // Stride
                    mask_w_k = mask_w_k & (w_in < Win) & mask_w
                    mask_sw = mask_h_k[:, None] & mask_w_k[None, :] & mask_d_k
                    off_x_spatial = off_x_d + h_in[:, None] * stride_xh + w_in[None, :] * stride_xw
                    k_idx = kz * (K * K) + ky * K + kx
                    off_w_k = k_idx * stride_wk_k
                    for cin_blk in range(0, Cin_per_group, BLOCK_CIN):
                        off_cin = cin_blk + tl.arange(0, BLOCK_CIN)
                        mask_cin = off_cin < Cin_per_group
                        ptr_x = X + batch * stride_xn + (base_cin_group + off_cin)[None, None, :] * stride_xc + off_x_spatial[:, :, None]
                        mask_x_load = mask_sw[:, :, None] & mask_cin[None, None, :]
                        x_tile = tl.load(ptr_x, mask=mask_x_load, other=0.0)
                        ptr_w = W + off_w_k + off_cin[:, None] * stride_wk_cin + off_cout[None, :] * stride_wk_cout
                        mask_w_load = mask_cin[:, None] & mask_cout[None, :]
                        w_tile = tl.load(ptr_w, mask=mask_w_load, other=0.0)
                        x_flat = tl.reshape(x_tile, (BLOCK_H * BLOCK_W, BLOCK_CIN))
                        acc_flat = tl.dot(x_flat, w_tile)
                        acc += tl.reshape(acc_flat, (BLOCK_H, BLOCK_W, BLOCK_COUT))
    if HAS_BIAS:
        b_val = tl.load(Bias + global_cout, mask=mask_cout, other=0.0)
        acc += b_val[None, None, :]
    mask_store = mask_h[:, None, None] & mask_w[None, None, :] & mask_cout[None, :, None]
    acc_store = tl.permute(acc, (0, 2, 1))
    tl.store(ptr_out, acc_store, mask=mask_store)


SHAPES = ((1, 3, 5, 2, 3, 4, 1, 0),)
DTYPES = ('float16',)


def _make_case(shape=SHAPES[0], dtype="float16", seed=0, use_if=True):
    b, ci, co, d, h, w, st, pad = (int(v) for v in shape)
    ks = 2
    od, oh, ow = (d - 1) * st - 2 * pad + ks, (h - 1) * st - 2 * pad + ks, \
        (w - 1) * st - 2 * pad + ks
    rng = np.random.default_rng(seed)
    x = rng.normal(0, 0.3, (b, ci, d, h, w)).astype(dtype)
    wt = rng.normal(0, 0.3, (ks ** 3, ci, co)).astype(dtype)
    bias = rng.normal(0, 0.2, co).astype(dtype)
    args = {'X': x, 'W': wt, 'Bias': bias,
            'Out': np.zeros((b, co, od, oh, ow), dtype=dtype),
            'stride_xn': ci * d * h * w, 'stride_xc': d * h * w,
            'stride_xd': h * w, 'stride_xh': w, 'stride_xw': 1,
            'stride_wk_k': ci * co, 'stride_wk_cin': co, 'stride_wk_cout': 1,
            'stride_on': co * od * oh * ow, 'stride_oc': od * oh * ow,
            'stride_od': oh * ow, 'stride_oh': ow, 'stride_ow': 1,
            'Cin_per_group': ci, 'Cout_per_group': co, 'Groups': 1,
            'Din': d, 'Hin': h, 'Win': w, 'Dout': od, 'Hout': oh, 'Wout': ow,
            'K': ks, 'Stride': st, 'Padding': pad}
    meta = {'USE_IF': use_if, 'BLOCK_H': 4, 'BLOCK_W': 4, 'BLOCK_CIN': 16,
            'BLOCK_COUT': 16, 'HAS_BIAS': True}
    grid = (triton.cdiv(ow, 4) * triton.cdiv(oh, 4), triton.cdiv(co, 16), b * od)
    return {"kernel": t044_tc_probe, "args": args, "meta": meta, "grid": grid,
            "outputs": ('Out',), "expected": {"Out": np.zeros((b, co, od, oh, ow), dtype=dtype)}}


def make_case(shape=None, dtype=None, seed=None):
    shape = tuple(SHAPES[0] if shape is None else shape)
    dtype = DTYPES[0] if dtype is None else np.dtype(dtype).name
    if shape not in SHAPES or dtype not in DTYPES:
        raise ValueError((shape, dtype))
    return _make_case(shape=shape, dtype=dtype, seed=seed)
