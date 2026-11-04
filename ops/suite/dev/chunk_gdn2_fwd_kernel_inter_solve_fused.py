"""chunk_gdn2_fwd_kernel_inter_solve_fused: 从 ~/ops 仓库复制(fla @ ops),保留其已验证的 case 层。

模式: args.runtime_scalar、cast.to、control.for_range、control.if、control.loop_carried、creation.arange、creation.where、creation.zeros、dtype.float32、dtype.int32。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。循环上界来自运行时标量(不是 constexpr)。constexpr 参数: H, K, BT, BC, BK, IS_VARLEN, USE_SAFE_GATE。

文件只有两层:
  ① chunk_gdn2_fwd_kernel_inter_solve_fused   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/chunk_gdn2_fwd_kernel_inter_solve_fused', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'cast.to', 'control.for_range', 'control.if', 'control.loop_carried', 'creation.arange', 'creation.where', 'creation.zeros', 'dtype.float32', 'dtype.int32', 'dtype.int64', 'linalg.dot', 'math.cdiv', 'math.exp2', 'memory.load', 'memory.load.masked', 'memory.load.other', 'memory.store', 'memory.store.masked', 'reduce.min', 'reduce.sum.axis0', 'shape.reshape', 'shape.trans', 'tile.2d', 'tile.3d']}
COPIED_FROM = {'repo': 'fla @ ops', 'note': 'validated case layer intact'}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit(do_not_specialize=['T'])
def chunk_gdn2_fwd_kernel_inter_solve_fused(q, k, g, b, Aqk, Akkd, Akk, scale, cu_seqlens, chunk_indices, T, H: tl.constexpr, K: tl.constexpr, BT: tl.constexpr, BC: tl.constexpr, BK: tl.constexpr, IS_VARLEN: tl.constexpr, USE_SAFE_GATE: tl.constexpr):
    (i_t, i_bh) = (tl.program_id(0).to(tl.int64), tl.program_id(1).to(tl.int64))
    (i_b, i_h) = (i_bh // H, i_bh % H)
    if IS_VARLEN:
        (i_n, i_t) = (tl.load(chunk_indices + i_t * 2).to(tl.int32), tl.load(chunk_indices + i_t * 2 + 1).to(tl.int64))
        (bos, eos) = (tl.load(cu_seqlens + i_n).to(tl.int64), tl.load(cu_seqlens + i_n + 1).to(tl.int64))
        T = eos - bos
    else:
        (bos, eos) = (i_b * T, i_b * T + T)
    if i_t * BT >= T:
        return
    i_tc0 = i_t * BT
    i_tc1 = i_t * BT + BC
    i_tc2 = i_t * BT + 2 * BC
    i_tc3 = i_t * BT + 3 * BC
    q += (bos * H + i_h) * K
    k += (bos * H + i_h) * K
    g += (bos * H + i_h) * K
    b += (bos * H + i_h) * K
    Aqk += (bos * H + i_h) * BT
    Akk += (bos * H + i_h) * BT
    Akkd += (bos * H + i_h) * BC
    o_i = tl.arange(0, BC)
    m_tc0 = i_tc0 + o_i < T
    m_tc1 = i_tc1 + o_i < T
    m_tc2 = i_tc2 + o_i < T
    m_tc3 = i_tc3 + o_i < T
    b_Aqk10 = tl.zeros([BC, BC], dtype=tl.float32)
    b_Akk10 = tl.zeros([BC, BC], dtype=tl.float32)
    b_Aqk20 = tl.zeros([BC, BC], dtype=tl.float32)
    b_Akk20 = tl.zeros([BC, BC], dtype=tl.float32)
    b_Aqk21 = tl.zeros([BC, BC], dtype=tl.float32)
    b_Akk21 = tl.zeros([BC, BC], dtype=tl.float32)
    b_Aqk30 = tl.zeros([BC, BC], dtype=tl.float32)
    b_Akk30 = tl.zeros([BC, BC], dtype=tl.float32)
    b_Aqk31 = tl.zeros([BC, BC], dtype=tl.float32)
    b_Akk31 = tl.zeros([BC, BC], dtype=tl.float32)
    b_Aqk32 = tl.zeros([BC, BC], dtype=tl.float32)
    b_Akk32 = tl.zeros([BC, BC], dtype=tl.float32)
    for i_k in range(tl.cdiv(K, BK)):
        o_k = i_k * BK + tl.arange(0, BK)
        m_k = o_k < K
        p_k0 = k + (i_tc0 + o_i)[:, None] * (H * K) + o_k[None, :]
        p_g0 = g + (i_tc0 + o_i)[:, None] * (H * K) + o_k[None, :]
        b_k0 = tl.load(p_k0, mask=m_tc0[:, None] & m_k[None, :], other=0.0).to(tl.float32)
        b_g0 = tl.load(p_g0, mask=m_tc0[:, None] & m_k[None, :], other=0.0).to(tl.float32)
        if i_tc1 < T:
            p_q1 = q + (i_tc1 + o_i)[:, None] * (H * K) + o_k[None, :]
            p_k1 = k + (i_tc1 + o_i)[:, None] * (H * K) + o_k[None, :]
            p_g1 = g + (i_tc1 + o_i)[:, None] * (H * K) + o_k[None, :]
            p_b1 = b + (i_tc1 + o_i)[:, None] * (H * K) + o_k[None, :]
            b_q1 = tl.load(p_q1, mask=m_tc1[:, None] & m_k[None, :], other=0.0).to(tl.float32)
            b_k1 = tl.load(p_k1, mask=m_tc1[:, None] & m_k[None, :], other=0.0).to(tl.float32)
            b_g1 = tl.load(p_g1, mask=m_tc1[:, None] & m_k[None, :], other=0.0).to(tl.float32)
            b_b1 = tl.load(p_b1, mask=m_tc1[:, None] & m_k[None, :], other=0.0).to(tl.float32)
            b_gn1 = tl.load(g + i_tc1 * H * K + o_k, mask=m_k, other=0).to(tl.float32)
            _inl_1_exp2_x = b_g1 - b_gn1[None, :]
            _inl_1_exp2_result = tl.exp2(_inl_1_exp2_x.to(tl.float32))
            b_gqn = tl.where(m_tc1[:, None], _inl_1_exp2_result, 0)
            _inl_2_exp2_x = b_gn1[None, :] - b_g0
            _inl_2_exp2_result = tl.exp2(_inl_2_exp2_x.to(tl.float32))
            b_kgt = tl.trans(b_k0 * _inl_2_exp2_result)
            b_bk1 = b_b1 * b_k1
            b_Aqk10 += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // (b_q1 * b_gqn).shape[1])[None, None, :] == 0, (b_q1 * b_gqn)[:, :, None], 0), ((b_q1 * b_gqn).shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // (b_q1 * b_gqn).shape[1])[None, :, None] == 0, b_kgt[:, None, :], 0), (16, b_kgt.shape[1])).to(tl.float32)) if (b_q1 * b_gqn).shape[1] < 16 else tl.dot(b_q1 * b_gqn, b_kgt)
            b_Akk10 += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // (b_bk1 * b_gqn).shape[1])[None, None, :] == 0, (b_bk1 * b_gqn)[:, :, None], 0), ((b_bk1 * b_gqn).shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // (b_bk1 * b_gqn).shape[1])[None, :, None] == 0, b_kgt[:, None, :], 0), (16, b_kgt.shape[1])).to(tl.float32)) if (b_bk1 * b_gqn).shape[1] < 16 else tl.dot(b_bk1 * b_gqn, b_kgt)
            if i_tc2 < T:
                p_q2 = q + (i_tc2 + o_i)[:, None] * (H * K) + o_k[None, :]
                p_k2 = k + (i_tc2 + o_i)[:, None] * (H * K) + o_k[None, :]
                p_g2 = g + (i_tc2 + o_i)[:, None] * (H * K) + o_k[None, :]
                p_b2 = b + (i_tc2 + o_i)[:, None] * (H * K) + o_k[None, :]
                b_q2 = tl.load(p_q2, mask=m_tc2[:, None] & m_k[None, :], other=0.0).to(tl.float32)
                b_k2 = tl.load(p_k2, mask=m_tc2[:, None] & m_k[None, :], other=0.0).to(tl.float32)
                b_g2 = tl.load(p_g2, mask=m_tc2[:, None] & m_k[None, :], other=0.0).to(tl.float32)
                b_b2 = tl.load(p_b2, mask=m_tc2[:, None] & m_k[None, :], other=0.0).to(tl.float32)
                b_gn2 = tl.load(g + i_tc2 * H * K + o_k, mask=m_k, other=0).to(tl.float32)
                _inl_3_exp2_x = b_g2 - b_gn2[None, :]
                _inl_3_exp2_result = tl.exp2(_inl_3_exp2_x.to(tl.float32))
                b_gqn2 = tl.where(m_tc2[:, None], _inl_3_exp2_result, 0)
                b_qg2 = b_q2 * b_gqn2
                b_bkg2 = b_b2 * b_k2 * b_gqn2
                _inl_4_exp2_x = b_gn2[None, :] - b_g0
                _inl_4_exp2_result = tl.exp2(_inl_4_exp2_x.to(tl.float32))
                b_kgt = tl.trans(b_k0 * _inl_4_exp2_result)
                b_Aqk20 += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_qg2.shape[1])[None, None, :] == 0, b_qg2[:, :, None], 0), (b_qg2.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_qg2.shape[1])[None, :, None] == 0, b_kgt[:, None, :], 0), (16, b_kgt.shape[1])).to(tl.float32)) if b_qg2.shape[1] < 16 else tl.dot(b_qg2, b_kgt)
                b_Akk20 += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_bkg2.shape[1])[None, None, :] == 0, b_bkg2[:, :, None], 0), (b_bkg2.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_bkg2.shape[1])[None, :, None] == 0, b_kgt[:, None, :], 0), (16, b_kgt.shape[1])).to(tl.float32)) if b_bkg2.shape[1] < 16 else tl.dot(b_bkg2, b_kgt)
                _inl_5_exp2_x = b_gn2[None, :] - b_g1
                _inl_5_exp2_result = tl.exp2(_inl_5_exp2_x.to(tl.float32))
                b_kgt = tl.trans(b_k1 * _inl_5_exp2_result)
                b_Aqk21 += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_qg2.shape[1])[None, None, :] == 0, b_qg2[:, :, None], 0), (b_qg2.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_qg2.shape[1])[None, :, None] == 0, b_kgt[:, None, :], 0), (16, b_kgt.shape[1])).to(tl.float32)) if b_qg2.shape[1] < 16 else tl.dot(b_qg2, b_kgt)
                b_Akk21 += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_bkg2.shape[1])[None, None, :] == 0, b_bkg2[:, :, None], 0), (b_bkg2.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_bkg2.shape[1])[None, :, None] == 0, b_kgt[:, None, :], 0), (16, b_kgt.shape[1])).to(tl.float32)) if b_bkg2.shape[1] < 16 else tl.dot(b_bkg2, b_kgt)
                if i_tc3 < T:
                    p_q3 = q + (i_tc3 + o_i)[:, None] * (H * K) + o_k[None, :]
                    p_k3 = k + (i_tc3 + o_i)[:, None] * (H * K) + o_k[None, :]
                    p_g3 = g + (i_tc3 + o_i)[:, None] * (H * K) + o_k[None, :]
                    p_b3 = b + (i_tc3 + o_i)[:, None] * (H * K) + o_k[None, :]
                    b_q3 = tl.load(p_q3, mask=m_tc3[:, None] & m_k[None, :], other=0.0).to(tl.float32)
                    b_k3 = tl.load(p_k3, mask=m_tc3[:, None] & m_k[None, :], other=0.0).to(tl.float32)
                    b_g3 = tl.load(p_g3, mask=m_tc3[:, None] & m_k[None, :], other=0.0).to(tl.float32)
                    b_b3 = tl.load(p_b3, mask=m_tc3[:, None] & m_k[None, :], other=0.0).to(tl.float32)
                    b_gn3 = tl.load(g + i_tc3 * H * K + o_k, mask=m_k, other=0).to(tl.float32)
                    _inl_6_exp2_x = b_g3 - b_gn3[None, :]
                    _inl_6_exp2_result = tl.exp2(_inl_6_exp2_x.to(tl.float32))
                    b_gqn3 = tl.where(m_tc3[:, None], _inl_6_exp2_result, 0)
                    b_qg3 = b_q3 * b_gqn3
                    b_bkg3 = b_b3 * b_k3 * b_gqn3
                    _inl_7_exp2_x = b_gn3[None, :] - b_g0
                    _inl_7_exp2_result = tl.exp2(_inl_7_exp2_x.to(tl.float32))
                    b_kgt = tl.trans(b_k0 * _inl_7_exp2_result)
                    b_Aqk30 += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_qg3.shape[1])[None, None, :] == 0, b_qg3[:, :, None], 0), (b_qg3.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_qg3.shape[1])[None, :, None] == 0, b_kgt[:, None, :], 0), (16, b_kgt.shape[1])).to(tl.float32)) if b_qg3.shape[1] < 16 else tl.dot(b_qg3, b_kgt)
                    b_Akk30 += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_bkg3.shape[1])[None, None, :] == 0, b_bkg3[:, :, None], 0), (b_bkg3.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_bkg3.shape[1])[None, :, None] == 0, b_kgt[:, None, :], 0), (16, b_kgt.shape[1])).to(tl.float32)) if b_bkg3.shape[1] < 16 else tl.dot(b_bkg3, b_kgt)
                    _inl_8_exp2_x = b_gn3[None, :] - b_g1
                    _inl_8_exp2_result = tl.exp2(_inl_8_exp2_x.to(tl.float32))
                    b_kgt = tl.trans(b_k1 * _inl_8_exp2_result)
                    b_Aqk31 += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_qg3.shape[1])[None, None, :] == 0, b_qg3[:, :, None], 0), (b_qg3.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_qg3.shape[1])[None, :, None] == 0, b_kgt[:, None, :], 0), (16, b_kgt.shape[1])).to(tl.float32)) if b_qg3.shape[1] < 16 else tl.dot(b_qg3, b_kgt)
                    b_Akk31 += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_bkg3.shape[1])[None, None, :] == 0, b_bkg3[:, :, None], 0), (b_bkg3.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_bkg3.shape[1])[None, :, None] == 0, b_kgt[:, None, :], 0), (16, b_kgt.shape[1])).to(tl.float32)) if b_bkg3.shape[1] < 16 else tl.dot(b_bkg3, b_kgt)
                    _inl_9_exp2_x = b_gn3[None, :] - b_g2
                    _inl_9_exp2_result = tl.exp2(_inl_9_exp2_x.to(tl.float32))
                    b_kgt = tl.trans(b_k2 * _inl_9_exp2_result)
                    b_Aqk32 += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_qg3.shape[1])[None, None, :] == 0, b_qg3[:, :, None], 0), (b_qg3.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_qg3.shape[1])[None, :, None] == 0, b_kgt[:, None, :], 0), (16, b_kgt.shape[1])).to(tl.float32)) if b_qg3.shape[1] < 16 else tl.dot(b_qg3, b_kgt)
                    b_Akk32 += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_bkg3.shape[1])[None, None, :] == 0, b_bkg3[:, :, None], 0), (b_bkg3.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_bkg3.shape[1])[None, :, None] == 0, b_kgt[:, None, :], 0), (16, b_kgt.shape[1])).to(tl.float32)) if b_bkg3.shape[1] < 16 else tl.dot(b_bkg3, b_kgt)
    if i_tc1 < T:
        p_Aqk10 = Aqk + (i_tc1 + o_i)[:, None] * (H * BT) + o_i[None, :]
        tl.store(p_Aqk10, (b_Aqk10 * scale).to(Aqk.dtype.element_ty), mask=m_tc1[:, None] & (o_i[None, :] < BT))
    if i_tc2 < T:
        p_Aqk20 = Aqk + (i_tc2 + o_i)[:, None] * (H * BT) + o_i[None, :]
        p_Aqk21 = Aqk + (i_tc2 + o_i)[:, None] * (H * BT) + (BC + o_i)[None, :]
        tl.store(p_Aqk20, (b_Aqk20 * scale).to(Aqk.dtype.element_ty), mask=m_tc2[:, None] & (o_i[None, :] < BT))
        tl.store(p_Aqk21, (b_Aqk21 * scale).to(Aqk.dtype.element_ty), mask=m_tc2[:, None] & ((BC + o_i)[None, :] < BT))
    if i_tc3 < T:
        p_Aqk30 = Aqk + (i_tc3 + o_i)[:, None] * (H * BT) + o_i[None, :]
        p_Aqk31 = Aqk + (i_tc3 + o_i)[:, None] * (H * BT) + (BC + o_i)[None, :]
        p_Aqk32 = Aqk + (i_tc3 + o_i)[:, None] * (H * BT) + (2 * BC + o_i)[None, :]
        tl.store(p_Aqk30, (b_Aqk30 * scale).to(Aqk.dtype.element_ty), mask=m_tc3[:, None] & (o_i[None, :] < BT))
        tl.store(p_Aqk31, (b_Aqk31 * scale).to(Aqk.dtype.element_ty), mask=m_tc3[:, None] & ((BC + o_i)[None, :] < BT))
        tl.store(p_Aqk32, (b_Aqk32 * scale).to(Aqk.dtype.element_ty), mask=m_tc3[:, None] & ((2 * BC + o_i)[None, :] < BT))
    p_Akk00 = Akkd + (i_tc0 + o_i)[:, None] * (H * BC) + o_i[None, :]
    p_Akk11 = Akkd + (i_tc1 + o_i)[:, None] * (H * BC) + o_i[None, :]
    p_Akk22 = Akkd + (i_tc2 + o_i)[:, None] * (H * BC) + o_i[None, :]
    p_Akk33 = Akkd + (i_tc3 + o_i)[:, None] * (H * BC) + o_i[None, :]
    b_Ai00 = tl.load(p_Akk00, mask=m_tc0[:, None] & (o_i[None, :] < BC), other=0.0).to(tl.float32)
    b_Ai11 = tl.load(p_Akk11, mask=m_tc1[:, None] & (o_i[None, :] < BC), other=0.0).to(tl.float32)
    b_Ai22 = tl.load(p_Akk22, mask=m_tc2[:, None] & (o_i[None, :] < BC), other=0.0).to(tl.float32)
    b_Ai33 = tl.load(p_Akk33, mask=m_tc3[:, None] & (o_i[None, :] < BC), other=0.0).to(tl.float32)
    if not USE_SAFE_GATE:
        m_A = o_i[:, None] > o_i[None, :]
        m_I = o_i[:, None] == o_i[None, :]
        b_Ai00 = -tl.where(m_A, b_Ai00, 0)
        b_Ai11 = -tl.where(m_A, b_Ai11, 0)
        b_Ai22 = -tl.where(m_A, b_Ai22, 0)
        b_Ai33 = -tl.where(m_A, b_Ai33, 0)
        for i in range(2, min(BC, T - i_tc0)):
            b_a00 = -tl.load(Akkd + (i_tc0 + i) * H * BC + o_i)
            b_a00 = tl.where(o_i < i, b_a00, 0.0)
            b_a00 += tl.sum(b_a00[:, None] * b_Ai00, 0)
            b_Ai00 = tl.where((o_i == i)[:, None], b_a00, b_Ai00)
        for i in range(BC + 2, min(2 * BC, T - i_tc0)):
            b_a11 = -tl.load(Akkd + (i_tc0 + i) * H * BC + o_i)
            b_a11 = tl.where(o_i < i - BC, b_a11, 0.0)
            b_a11 += tl.sum(b_a11[:, None] * b_Ai11, 0)
            b_Ai11 = tl.where((o_i == i - BC)[:, None], b_a11, b_Ai11)
        for i in range(2 * BC + 2, min(3 * BC, T - i_tc0)):
            b_a22 = -tl.load(Akkd + (i_tc0 + i) * H * BC + o_i)
            b_a22 = tl.where(o_i < i - 2 * BC, b_a22, 0.0)
            b_a22 += tl.sum(b_a22[:, None] * b_Ai22, 0)
            b_Ai22 = tl.where((o_i == i - 2 * BC)[:, None], b_a22, b_Ai22)
        for i in range(3 * BC + 2, min(4 * BC, T - i_tc0)):
            b_a33 = -tl.load(Akkd + (i_tc0 + i) * H * BC + o_i)
            b_a33 = tl.where(o_i < i - 3 * BC, b_a33, 0.0)
            b_a33 += tl.sum(b_a33[:, None] * b_Ai33, 0)
            b_Ai33 = tl.where((o_i == i - 3 * BC)[:, None], b_a33, b_Ai33)
        b_Ai00 += m_I
        b_Ai11 += m_I
        b_Ai22 += m_I
        b_Ai33 += m_I
    b_Ai10 = -(tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai11.shape[1])[None, None, :] == 0, b_Ai11[:, :, None], 0), (b_Ai11.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai11.shape[1])[None, :, None] == 0, b_Akk10[:, None, :], 0), (16, b_Akk10.shape[1])).to(tl.float32)) if b_Ai11.shape[1] < 16 else tl.dot(b_Ai11, b_Akk10)).shape[1])[None, None, :] == 0, (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai11.shape[1])[None, None, :] == 0, b_Ai11[:, :, None], 0), (b_Ai11.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai11.shape[1])[None, :, None] == 0, b_Akk10[:, None, :], 0), (16, b_Akk10.shape[1])).to(tl.float32)) if b_Ai11.shape[1] < 16 else tl.dot(b_Ai11, b_Akk10))[:, :, None], 0), ((tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai11.shape[1])[None, None, :] == 0, b_Ai11[:, :, None], 0), (b_Ai11.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai11.shape[1])[None, :, None] == 0, b_Akk10[:, None, :], 0), (16, b_Akk10.shape[1])).to(tl.float32)) if b_Ai11.shape[1] < 16 else tl.dot(b_Ai11, b_Akk10)).shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai11.shape[1])[None, None, :] == 0, b_Ai11[:, :, None], 0), (b_Ai11.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai11.shape[1])[None, :, None] == 0, b_Akk10[:, None, :], 0), (16, b_Akk10.shape[1])).to(tl.float32)) if b_Ai11.shape[1] < 16 else tl.dot(b_Ai11, b_Akk10)).shape[1])[None, :, None] == 0, b_Ai00[:, None, :], 0), (16, b_Ai00.shape[1])).to(tl.float32)) if (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai11.shape[1])[None, None, :] == 0, b_Ai11[:, :, None], 0), (b_Ai11.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai11.shape[1])[None, :, None] == 0, b_Akk10[:, None, :], 0), (16, b_Akk10.shape[1])).to(tl.float32)) if b_Ai11.shape[1] < 16 else tl.dot(b_Ai11, b_Akk10)).shape[1] < 16 else tl.dot(tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai11.shape[1])[None, None, :] == 0, b_Ai11[:, :, None], 0), (b_Ai11.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai11.shape[1])[None, :, None] == 0, b_Akk10[:, None, :], 0), (16, b_Akk10.shape[1])).to(tl.float32)) if b_Ai11.shape[1] < 16 else tl.dot(b_Ai11, b_Akk10), b_Ai00))
    b_Ai21 = -(tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai22.shape[1])[None, None, :] == 0, b_Ai22[:, :, None], 0), (b_Ai22.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai22.shape[1])[None, :, None] == 0, b_Akk21[:, None, :], 0), (16, b_Akk21.shape[1])).to(tl.float32)) if b_Ai22.shape[1] < 16 else tl.dot(b_Ai22, b_Akk21)).shape[1])[None, None, :] == 0, (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai22.shape[1])[None, None, :] == 0, b_Ai22[:, :, None], 0), (b_Ai22.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai22.shape[1])[None, :, None] == 0, b_Akk21[:, None, :], 0), (16, b_Akk21.shape[1])).to(tl.float32)) if b_Ai22.shape[1] < 16 else tl.dot(b_Ai22, b_Akk21))[:, :, None], 0), ((tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai22.shape[1])[None, None, :] == 0, b_Ai22[:, :, None], 0), (b_Ai22.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai22.shape[1])[None, :, None] == 0, b_Akk21[:, None, :], 0), (16, b_Akk21.shape[1])).to(tl.float32)) if b_Ai22.shape[1] < 16 else tl.dot(b_Ai22, b_Akk21)).shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai22.shape[1])[None, None, :] == 0, b_Ai22[:, :, None], 0), (b_Ai22.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai22.shape[1])[None, :, None] == 0, b_Akk21[:, None, :], 0), (16, b_Akk21.shape[1])).to(tl.float32)) if b_Ai22.shape[1] < 16 else tl.dot(b_Ai22, b_Akk21)).shape[1])[None, :, None] == 0, b_Ai11[:, None, :], 0), (16, b_Ai11.shape[1])).to(tl.float32)) if (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai22.shape[1])[None, None, :] == 0, b_Ai22[:, :, None], 0), (b_Ai22.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai22.shape[1])[None, :, None] == 0, b_Akk21[:, None, :], 0), (16, b_Akk21.shape[1])).to(tl.float32)) if b_Ai22.shape[1] < 16 else tl.dot(b_Ai22, b_Akk21)).shape[1] < 16 else tl.dot(tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai22.shape[1])[None, None, :] == 0, b_Ai22[:, :, None], 0), (b_Ai22.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai22.shape[1])[None, :, None] == 0, b_Akk21[:, None, :], 0), (16, b_Akk21.shape[1])).to(tl.float32)) if b_Ai22.shape[1] < 16 else tl.dot(b_Ai22, b_Akk21), b_Ai11))
    b_Ai32 = -(tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai33.shape[1])[None, None, :] == 0, b_Ai33[:, :, None], 0), (b_Ai33.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai33.shape[1])[None, :, None] == 0, b_Akk32[:, None, :], 0), (16, b_Akk32.shape[1])).to(tl.float32)) if b_Ai33.shape[1] < 16 else tl.dot(b_Ai33, b_Akk32)).shape[1])[None, None, :] == 0, (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai33.shape[1])[None, None, :] == 0, b_Ai33[:, :, None], 0), (b_Ai33.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai33.shape[1])[None, :, None] == 0, b_Akk32[:, None, :], 0), (16, b_Akk32.shape[1])).to(tl.float32)) if b_Ai33.shape[1] < 16 else tl.dot(b_Ai33, b_Akk32))[:, :, None], 0), ((tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai33.shape[1])[None, None, :] == 0, b_Ai33[:, :, None], 0), (b_Ai33.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai33.shape[1])[None, :, None] == 0, b_Akk32[:, None, :], 0), (16, b_Akk32.shape[1])).to(tl.float32)) if b_Ai33.shape[1] < 16 else tl.dot(b_Ai33, b_Akk32)).shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai33.shape[1])[None, None, :] == 0, b_Ai33[:, :, None], 0), (b_Ai33.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai33.shape[1])[None, :, None] == 0, b_Akk32[:, None, :], 0), (16, b_Akk32.shape[1])).to(tl.float32)) if b_Ai33.shape[1] < 16 else tl.dot(b_Ai33, b_Akk32)).shape[1])[None, :, None] == 0, b_Ai22[:, None, :], 0), (16, b_Ai22.shape[1])).to(tl.float32)) if (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai33.shape[1])[None, None, :] == 0, b_Ai33[:, :, None], 0), (b_Ai33.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai33.shape[1])[None, :, None] == 0, b_Akk32[:, None, :], 0), (16, b_Akk32.shape[1])).to(tl.float32)) if b_Ai33.shape[1] < 16 else tl.dot(b_Ai33, b_Akk32)).shape[1] < 16 else tl.dot(tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai33.shape[1])[None, None, :] == 0, b_Ai33[:, :, None], 0), (b_Ai33.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai33.shape[1])[None, :, None] == 0, b_Akk32[:, None, :], 0), (16, b_Akk32.shape[1])).to(tl.float32)) if b_Ai33.shape[1] < 16 else tl.dot(b_Ai33, b_Akk32), b_Ai22))
    b_Ai20 = -(tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai22.shape[1])[None, None, :] == 0, b_Ai22[:, :, None], 0), (b_Ai22.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai22.shape[1])[None, :, None] == 0, ((tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk20.shape[1])[None, None, :] == 0, b_Akk20[:, :, None], 0), (b_Akk20.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk20.shape[1])[None, :, None] == 0, b_Ai00[:, None, :], 0), (16, b_Ai00.shape[1])).to(tl.float32)) if b_Akk20.shape[1] < 16 else tl.dot(b_Akk20, b_Ai00)) + (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk21.shape[1])[None, None, :] == 0, b_Akk21[:, :, None], 0), (b_Akk21.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk21.shape[1])[None, :, None] == 0, b_Ai10[:, None, :], 0), (16, b_Ai10.shape[1])).to(tl.float32)) if b_Akk21.shape[1] < 16 else tl.dot(b_Akk21, b_Ai10)))[:, None, :], 0), (16, ((tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk20.shape[1])[None, None, :] == 0, b_Akk20[:, :, None], 0), (b_Akk20.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk20.shape[1])[None, :, None] == 0, b_Ai00[:, None, :], 0), (16, b_Ai00.shape[1])).to(tl.float32)) if b_Akk20.shape[1] < 16 else tl.dot(b_Akk20, b_Ai00)) + (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk21.shape[1])[None, None, :] == 0, b_Akk21[:, :, None], 0), (b_Akk21.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk21.shape[1])[None, :, None] == 0, b_Ai10[:, None, :], 0), (16, b_Ai10.shape[1])).to(tl.float32)) if b_Akk21.shape[1] < 16 else tl.dot(b_Akk21, b_Ai10))).shape[1])).to(tl.float32)) if b_Ai22.shape[1] < 16 else tl.dot(b_Ai22, (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk20.shape[1])[None, None, :] == 0, b_Akk20[:, :, None], 0), (b_Akk20.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk20.shape[1])[None, :, None] == 0, b_Ai00[:, None, :], 0), (16, b_Ai00.shape[1])).to(tl.float32)) if b_Akk20.shape[1] < 16 else tl.dot(b_Akk20, b_Ai00)) + (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk21.shape[1])[None, None, :] == 0, b_Akk21[:, :, None], 0), (b_Akk21.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk21.shape[1])[None, :, None] == 0, b_Ai10[:, None, :], 0), (16, b_Ai10.shape[1])).to(tl.float32)) if b_Akk21.shape[1] < 16 else tl.dot(b_Akk21, b_Ai10))))
    b_Ai31 = -(tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai33.shape[1])[None, None, :] == 0, b_Ai33[:, :, None], 0), (b_Ai33.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai33.shape[1])[None, :, None] == 0, ((tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk31.shape[1])[None, None, :] == 0, b_Akk31[:, :, None], 0), (b_Akk31.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk31.shape[1])[None, :, None] == 0, b_Ai11[:, None, :], 0), (16, b_Ai11.shape[1])).to(tl.float32)) if b_Akk31.shape[1] < 16 else tl.dot(b_Akk31, b_Ai11)) + (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk32.shape[1])[None, None, :] == 0, b_Akk32[:, :, None], 0), (b_Akk32.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk32.shape[1])[None, :, None] == 0, b_Ai21[:, None, :], 0), (16, b_Ai21.shape[1])).to(tl.float32)) if b_Akk32.shape[1] < 16 else tl.dot(b_Akk32, b_Ai21)))[:, None, :], 0), (16, ((tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk31.shape[1])[None, None, :] == 0, b_Akk31[:, :, None], 0), (b_Akk31.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk31.shape[1])[None, :, None] == 0, b_Ai11[:, None, :], 0), (16, b_Ai11.shape[1])).to(tl.float32)) if b_Akk31.shape[1] < 16 else tl.dot(b_Akk31, b_Ai11)) + (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk32.shape[1])[None, None, :] == 0, b_Akk32[:, :, None], 0), (b_Akk32.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk32.shape[1])[None, :, None] == 0, b_Ai21[:, None, :], 0), (16, b_Ai21.shape[1])).to(tl.float32)) if b_Akk32.shape[1] < 16 else tl.dot(b_Akk32, b_Ai21))).shape[1])).to(tl.float32)) if b_Ai33.shape[1] < 16 else tl.dot(b_Ai33, (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk31.shape[1])[None, None, :] == 0, b_Akk31[:, :, None], 0), (b_Akk31.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk31.shape[1])[None, :, None] == 0, b_Ai11[:, None, :], 0), (16, b_Ai11.shape[1])).to(tl.float32)) if b_Akk31.shape[1] < 16 else tl.dot(b_Akk31, b_Ai11)) + (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk32.shape[1])[None, None, :] == 0, b_Akk32[:, :, None], 0), (b_Akk32.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk32.shape[1])[None, :, None] == 0, b_Ai21[:, None, :], 0), (16, b_Ai21.shape[1])).to(tl.float32)) if b_Akk32.shape[1] < 16 else tl.dot(b_Akk32, b_Ai21))))
    b_Ai30 = -(tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Ai33.shape[1])[None, None, :] == 0, b_Ai33[:, :, None], 0), (b_Ai33.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Ai33.shape[1])[None, :, None] == 0, ((tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk30.shape[1])[None, None, :] == 0, b_Akk30[:, :, None], 0), (b_Akk30.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk30.shape[1])[None, :, None] == 0, b_Ai00[:, None, :], 0), (16, b_Ai00.shape[1])).to(tl.float32)) if b_Akk30.shape[1] < 16 else tl.dot(b_Akk30, b_Ai00)) + (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk31.shape[1])[None, None, :] == 0, b_Akk31[:, :, None], 0), (b_Akk31.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk31.shape[1])[None, :, None] == 0, b_Ai10[:, None, :], 0), (16, b_Ai10.shape[1])).to(tl.float32)) if b_Akk31.shape[1] < 16 else tl.dot(b_Akk31, b_Ai10)) + (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk32.shape[1])[None, None, :] == 0, b_Akk32[:, :, None], 0), (b_Akk32.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk32.shape[1])[None, :, None] == 0, b_Ai20[:, None, :], 0), (16, b_Ai20.shape[1])).to(tl.float32)) if b_Akk32.shape[1] < 16 else tl.dot(b_Akk32, b_Ai20)))[:, None, :], 0), (16, ((tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk30.shape[1])[None, None, :] == 0, b_Akk30[:, :, None], 0), (b_Akk30.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk30.shape[1])[None, :, None] == 0, b_Ai00[:, None, :], 0), (16, b_Ai00.shape[1])).to(tl.float32)) if b_Akk30.shape[1] < 16 else tl.dot(b_Akk30, b_Ai00)) + (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk31.shape[1])[None, None, :] == 0, b_Akk31[:, :, None], 0), (b_Akk31.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk31.shape[1])[None, :, None] == 0, b_Ai10[:, None, :], 0), (16, b_Ai10.shape[1])).to(tl.float32)) if b_Akk31.shape[1] < 16 else tl.dot(b_Akk31, b_Ai10)) + (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk32.shape[1])[None, None, :] == 0, b_Akk32[:, :, None], 0), (b_Akk32.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk32.shape[1])[None, :, None] == 0, b_Ai20[:, None, :], 0), (16, b_Ai20.shape[1])).to(tl.float32)) if b_Akk32.shape[1] < 16 else tl.dot(b_Akk32, b_Ai20))).shape[1])).to(tl.float32)) if b_Ai33.shape[1] < 16 else tl.dot(b_Ai33, (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk30.shape[1])[None, None, :] == 0, b_Akk30[:, :, None], 0), (b_Akk30.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk30.shape[1])[None, :, None] == 0, b_Ai00[:, None, :], 0), (16, b_Ai00.shape[1])).to(tl.float32)) if b_Akk30.shape[1] < 16 else tl.dot(b_Akk30, b_Ai00)) + (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk31.shape[1])[None, None, :] == 0, b_Akk31[:, :, None], 0), (b_Akk31.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk31.shape[1])[None, :, None] == 0, b_Ai10[:, None, :], 0), (16, b_Ai10.shape[1])).to(tl.float32)) if b_Akk31.shape[1] < 16 else tl.dot(b_Akk31, b_Ai10)) + (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Akk32.shape[1])[None, None, :] == 0, b_Akk32[:, :, None], 0), (b_Akk32.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Akk32.shape[1])[None, :, None] == 0, b_Ai20[:, None, :], 0), (16, b_Ai20.shape[1])).to(tl.float32)) if b_Akk32.shape[1] < 16 else tl.dot(b_Akk32, b_Ai20))))
    p_Akk00 = Akk + (i_tc0 + o_i)[:, None] * (H * BT) + o_i[None, :]
    p_Akk10 = Akk + (i_tc1 + o_i)[:, None] * (H * BT) + o_i[None, :]
    p_Akk11 = Akk + (i_tc1 + o_i)[:, None] * (H * BT) + (BC + o_i)[None, :]
    p_Akk20 = Akk + (i_tc2 + o_i)[:, None] * (H * BT) + o_i[None, :]
    p_Akk21 = Akk + (i_tc2 + o_i)[:, None] * (H * BT) + (BC + o_i)[None, :]
    p_Akk22 = Akk + (i_tc2 + o_i)[:, None] * (H * BT) + (2 * BC + o_i)[None, :]
    p_Akk30 = Akk + (i_tc3 + o_i)[:, None] * (H * BT) + o_i[None, :]
    p_Akk31 = Akk + (i_tc3 + o_i)[:, None] * (H * BT) + (BC + o_i)[None, :]
    p_Akk32 = Akk + (i_tc3 + o_i)[:, None] * (H * BT) + (2 * BC + o_i)[None, :]
    p_Akk33 = Akk + (i_tc3 + o_i)[:, None] * (H * BT) + (3 * BC + o_i)[None, :]
    tl.store(p_Akk00, b_Ai00.to(Akk.dtype.element_ty), mask=m_tc0[:, None] & (o_i[None, :] < BT))
    tl.store(p_Akk10, b_Ai10.to(Akk.dtype.element_ty), mask=m_tc1[:, None] & (o_i[None, :] < BT))
    tl.store(p_Akk11, b_Ai11.to(Akk.dtype.element_ty), mask=m_tc1[:, None] & ((BC + o_i)[None, :] < BT))
    tl.store(p_Akk20, b_Ai20.to(Akk.dtype.element_ty), mask=m_tc2[:, None] & (o_i[None, :] < BT))
    tl.store(p_Akk21, b_Ai21.to(Akk.dtype.element_ty), mask=m_tc2[:, None] & ((BC + o_i)[None, :] < BT))
    tl.store(p_Akk22, b_Ai22.to(Akk.dtype.element_ty), mask=m_tc2[:, None] & ((2 * BC + o_i)[None, :] < BT))
    tl.store(p_Akk30, b_Ai30.to(Akk.dtype.element_ty), mask=m_tc3[:, None] & (o_i[None, :] < BT))
    tl.store(p_Akk31, b_Ai31.to(Akk.dtype.element_ty), mask=m_tc3[:, None] & ((BC + o_i)[None, :] < BT))
    tl.store(p_Akk32, b_Ai32.to(Akk.dtype.element_ty), mask=m_tc3[:, None] & ((2 * BC + o_i)[None, :] < BT))
    tl.store(p_Akk33, b_Ai33.to(Akk.dtype.element_ty), mask=m_tc3[:, None] & ((3 * BC + o_i)[None, :] < BT))

# ------------------------------------------------------------------ ② case 层

SUPPORT_STATUS = "supported"
VALIDATION_SCOPE = "full-launch-correctness"
SEED = 20260901
def _aligned(values, dtype="float32", alignment=64):
    import numpy as np

    values = np.asarray(values, dtype=np.dtype(dtype))
    raw = np.empty(values.size * values.dtype.itemsize + alignment, dtype=np.uint8)
    start = -raw.ctypes.data % alignment
    result = raw[start : start + values.size * values.dtype.itemsize].view(values.dtype)
    result[...] = values.reshape(-1)
    return result.reshape(values.shape)
def _case(kernel, grid, args, meta, inputs, outputs, expected, shape, dtype, seed, coverage, rtol=0.0002, atol=2e-05):
    import numpy as np
    _comparison_dtype_policy = str(dtype)
    if _comparison_dtype_policy == 'float32':
        (rtol, atol) = (0.0001, 0.0001)
    elif _comparison_dtype_policy == 'bfloat16':
        (rtol, atol) = (0.01, 0.01)
    comparison = {name: {'profile': 'numerical', 'comparator': 'allclose', 'exact': False, 'rtol': float(rtol), 'atol': float(atol), 'equal_nan': True} for name in outputs}
    arrays = {name: value for (name, value) in args.items() if isinstance(value, np.ndarray)}
    return {'kernel': kernel, 'grid': tuple((int(value) for value in grid)), 'args': args, 'meta': meta, 'launch_meta': {'num_warps': 4, 'num_stages': 1}, 'inputs': tuple(inputs), 'outputs': tuple(outputs), 'expected': expected, 'comparison': comparison, 'pointer_dtypes': {name: str(value.dtype) for (name, value) in arrays.items()}, 'buffer_extents': {name: int(value.size) for (name, value) in arrays.items()}, 'buffer_layouts': {name: {'shape': tuple((int(x) for x in value.shape)), 'strides': tuple((int(x // value.dtype.itemsize) for x in value.strides))} for (name, value) in arrays.items()}, 'alignment': 64, 'aliases': {}, 'seed': int(seed), 'shape': tuple(shape), 'dtype': str(dtype), 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'coverage': {'complete_logical_output': True, **coverage}}

SHAPES = ((17,), (3, 17, 2, 7));DTYPES = ('float32', 'float16', 'bfloat16')
SHAPES = ((17,), (3, 17, 2, 7));DTYPES = ('float32', 'float16', 'bfloat16')
def ref(args,meta):
 import numpy as np
 T=int(args["T"]);H=int(meta["H"]);K=int(meta["K"]);BT=int(meta["BT"]);BC=int(meta["BC"]);q=np.asarray(args["q"],np.float32).reshape(-1,T,H,K);k=np.asarray(args["k"],np.float32).reshape(-1,T,H,K);g=np.asarray(args["g"],np.float32).reshape(-1,T,H,K);b=np.asarray(args["b"],np.float32).reshape(-1,T,H,K);diag=np.asarray(args["Akkd"],np.float32).reshape(-1,T,H,BC);aq=np.array(args["Aqk"],copy=True).reshape(-1,T,H,BT);akk=np.array(args["Akk"],copy=True).reshape(-1,T,H,BT)
 for n in range(q.shape[0]):
  for h in range(H):
   for start in range(0,T,BT):
    count=min(BT,T-start);raw=np.zeros((count,count),np.float32)
    for r0 in range(0,count,BC):
     rn=min(BC,count-r0);raw[r0:r0+rn,r0:r0+rn]=np.tril(diag[n,start+r0:start+r0+rn,h,:rn],-1)
     for c0 in range(0,r0,BC):
      cn=min(BC,count-c0);gate=np.exp2(g[n,start+r0:start+r0+rn,h,None,:]-g[n,start+c0:start+c0+cn,h][None,:,:]);aq[n,start+r0:start+r0+rn,h,c0:c0+cn]=np.sum(q[n,start+r0:start+r0+rn,h,None,:]*k[n,start+c0:start+c0+cn,h][None,:,:]*gate,axis=2,dtype=np.float32)*np.float32(args["scale"]);raw[r0:r0+rn,c0:c0+cn]=np.sum((b[n,start+r0:start+r0+rn,h]*k[n,start+r0:start+r0+rn,h])[:,None,:]*k[n,start+c0:start+c0+cn,h][None,:,:]*gate,axis=2,dtype=np.float32)
    inv=np.eye(count,dtype=np.float32)
    for i in range(1,count):inv[i,:i]=-raw[i,:i]@inv[:i,:i]
    akk[n,start:start+count,h,:count]=inv
 return {"Aqk":aq.reshape(-1),"Akk":akk.reshape(-1)}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    if len(shape) > 1 and tuple(shape) not in SHAPES:
        raise ValueError('unsupported explicit shape configuration')
    del dtype
    import numpy as np
    N = int(shape[0])
    from case_utils import fast_rng
    rng = fast_rng(seed)
    B = int(shape[0]) if len(shape) > 1 else 2
    H = int(shape[2]) if len(shape) > 1 else 2
    T = int(shape[1]) if len(shape) > 1 else max(17, min(33, N | 1))
    K = int(shape[3]) if len(shape) > 1 else 7
    BC = 4
    BT = 4 * BC
    q = rng.normal(0, 0.15, (B, T, H, K)).astype(np.float32)
    k = rng.normal(0, 0.15, (B, T, H, K)).astype(np.float32)
    g = rng.normal(0, 0.05, (B, T, H, K)).astype(np.float32)
    bb = rng.normal(0, 0.08, (B, T, H, K)).astype(np.float32)
    aq = np.zeros((B, T, H, BT), np.float32)
    diag = np.zeros((B, T, H, BC), np.float32)
    for n in range(B):
        for h in range(H):
            for start in range(0, T, BT):
                count = min(BT, T - start)
                for sub in range(0, count, BC):
                    size = min(BC, count - sub)
                    gate = np.exp2(g[n, start + sub:start + sub + size, h, None, :] - g[n, start + sub:start + sub + size, h][None, :, :])
                    aq[n, start + sub:start + sub + size, h, sub:sub + size] = np.tril(np.sum(q[n, start + sub:start + sub + size, h, None, :] * k[n, start + sub:start + sub + size, h][None, :, :] * gate, axis=2, dtype=np.float32) * 0.7)
                    diag[n, start + sub:start + sub + size, h, :size] = np.tril(np.sum((bb[n, start + sub:start + sub + size, h] * k[n, start + sub:start + sub + size, h])[:, None, :] * k[n, start + sub:start + sub + size, h][None, :, :] * gate, axis=2, dtype=np.float32), -1)
    args = {'q': _aligned(q), 'k': _aligned(k), 'g': _aligned(g), 'b': _aligned(bb), 'Aqk': _aligned(aq), 'Akkd': _aligned(diag), 'Akk': _aligned(np.zeros(B * T * H * BT)), 'scale': 0.7, 'cu_seqlens': _aligned(np.arange(B + 1) * T, 'int64'), 'chunk_indices': _aligned(np.zeros(2, dtype=np.int64), 'int64'), 'T': T}
    meta = {'H': H, 'K': K, 'BT': BT, 'BC': BC, 'BK': 4, 'IS_VARLEN': False, 'USE_SAFE_GATE': False}
    grid = ((T + BT - 1) // BT, B * H)
    outputs = ('Aqk', 'Akk')
    return _case(chunk_gdn2_fwd_kernel_inter_solve_fused, grid, args, meta, ('q', 'k', 'g', 'b', 'Aqk', 'Akkd'), outputs, ref(args, meta), shape, 'float32', seed, {'complete_launch_plan': True, 'formula': 'GDN2 off-diagonal gated q-k and elementwise-b/key Gram blocks followed by full block-lower inversion'})
def make_case(shape=None, dtype=None, seed=None):
    """Create one host case; defaults and supported dtypes are operator-owned."""
    import numpy as np

    requested = None
    if dtype is not None:
        try:
            requested = np.dtype(dtype).name
        except TypeError:
            requested = str(dtype).rsplit(".", 1)[-1]
    choices = {str(value).rsplit(".", 1)[-1]: value for value in DTYPES}
    if requested is not None and requested not in choices:
        raise ValueError(f"unsupported dtype {dtype}; choose from {tuple(choices)}")
    options = {}
    if shape is not None:
        options["shape"] = tuple(shape)
    if requested is not None:
        options["dtype"] = choices[requested]
    if seed is not None:
        options["seed"] = seed
    case = _make_case(**options)
    case.setdefault("outputs", tuple(case["expected"]))
    case.setdefault("launch_meta", {})
    return case


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
