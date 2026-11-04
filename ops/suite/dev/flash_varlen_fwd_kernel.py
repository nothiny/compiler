"""flash_varlen_fwd_kernel: 从 ~/ops 仓库复制(~/ops (smoke)),保留其已验证的 case 层。

模式: args.runtime_scalar、blockptr.make、cast.to、control.for_range、control.if、control.loop_carried、control.static_range、creation.arange、creation.full、creation.where。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。循环上界来自运行时标量(不是 constexpr)。constexpr 参数: is_cu_seqlens_q, is_cu_seqlens_k, is_seqused_k, h, hk, h_hk_ratio, d, d_rounded, is_softcap, softcap, scale_softmax, scale_softmax_log2, is_dropout, p_dropout, rp_dropout, p_dropout_in_uint8_t, return_softmax, is_causal, is_local, window_size_left, window_size_right, seqlenq_ngroups_swapped, is_paged, is_alibi, alibi_slopes_batch_stride, page_table_batch_stride, block_size, BLOCK_M, BLOCK_N, BLOCK_K, KERNEL_NUM_WARPS, PIPELINE_STAGES。

文件只有两层:
  ① flash_varlen_fwd_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/flash_varlen_fwd_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'blockptr.make', 'cast.to', 'control.for_range', 'control.if', 'control.loop_carried', 'control.static_range', 'creation.arange', 'creation.full', 'creation.where', 'creation.zeros', 'dtype.float32', 'dtype.int32', 'dtype.int64', 'dtype.uint32', 'dtype.uint64', 'linalg.dot', 'linalg.dot.out_dtype', 'math.abs', 'math.cdiv', 'math.exp', 'math.exp2', 'math.log', 'math.maximum', 'memory.load', 'memory.load.masked', 'memory.load.other', 'memory.store', 'memory.store.masked', 'reduce.max', 'reduce.max.axis1', 'reduce.min', 'reduce.sum.axis1', 'shape.join', 'shape.trans', 'tile.2d']}
COPIED_FROM = {'repo': '~/ops (smoke)', 'note': 'pattern witness: masked-GEMM/splitK/attention-varlen/layernorm/rmsnorm/embedding-int64/int8-dot', 'validated': True}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit(do_not_specialize=['q_batch_stride', 'k_batch_stride', 'v_batch_stride', 'o_batch_stride', 'b', 'bk', 'seqlen_q', 'seqlen_k', 'seqlen_q_rounded', 'seqlen_k_rounded', 'total_q'])
def flash_varlen_fwd_kernel(q_ptr, k_ptr, v_ptr, o_ptr, p_ptr, softmax_lse_ptr, q_row_stride, k_row_stride, v_row_stride, q_head_stride, k_head_stride, v_head_stride, o_row_stride, o_head_stride, q_batch_stride, k_batch_stride, v_batch_stride, o_batch_stride, is_cu_seqlens_q: tl.constexpr, cu_seqlens_q_ptr, is_cu_seqlens_k: tl.constexpr, cu_seqlens_k_ptr, is_seqused_k: tl.constexpr, seqused_k_ptr, b, bk, h: tl.constexpr, hk: tl.constexpr, h_hk_ratio: tl.constexpr, seqlen_q, seqlen_k, seqlen_q_rounded, seqlen_k_rounded, d: tl.constexpr, d_rounded: tl.constexpr, is_softcap: tl.constexpr, softcap: tl.constexpr, scale_softmax: tl.constexpr, scale_softmax_log2: tl.constexpr, is_dropout: tl.constexpr, p_dropout: tl.constexpr, rp_dropout: tl.constexpr, p_dropout_in_uint8_t: tl.constexpr, philox_args, return_softmax: tl.constexpr, is_causal: tl.constexpr, is_local: tl.constexpr, window_size_left: tl.constexpr, window_size_right: tl.constexpr, seqlenq_ngroups_swapped: tl.constexpr, is_paged: tl.constexpr, is_alibi: tl.constexpr, alibi_slopes_ptr, alibi_slopes_batch_stride: tl.constexpr, total_q, page_table_ptr, page_table_batch_stride: tl.constexpr, block_size: tl.constexpr, k_page_stride, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr, KERNEL_NUM_WARPS: tl.constexpr, PIPELINE_STAGES: tl.constexpr):
    m_block = tl.program_id(0)
    bid = tl.program_id(1)
    hid = tl.program_id(2)
    if is_cu_seqlens_q:
        q_eos = tl.load(cu_seqlens_q_ptr + bid + 1).to(tl.int32)
        q_bos = tl.load(cu_seqlens_q_ptr + bid).to(tl.int32)
        q_len = q_eos - q_bos
        q_offset = q_bos * q_row_stride
        o_offset = q_bos * o_row_stride
        lse_offset = q_bos * 1
    else:
        q_len = seqlen_q
        q_offset = bid * q_batch_stride
        o_offset = bid * o_batch_stride
        lse_offset = bid * seqlen_q
    if is_cu_seqlens_k:
        k_eos = tl.load(cu_seqlens_k_ptr + bid + 1).to(tl.int32)
        k_bos = tl.load(cu_seqlens_k_ptr + bid).to(tl.int32)
        k_len_cache = k_eos - k_bos
        k_offset = k_bos * k_row_stride
        v_offset = k_bos * v_row_stride
    else:
        k_len_cache = seqlen_k
        k_offset = bid * k_batch_stride
        v_offset = bid * v_batch_stride
    if is_seqused_k:
        k_len = tl.load(seqused_k_ptr + bid).to(tl.int32)
    else:
        k_len = k_len_cache
    if m_block * BLOCK_M > q_len:
        return
    is_even_mn: tl.constexpr = False
    if is_local:
        n_block_min = max(0, (m_block * BLOCK_M + k_len - q_len - window_size_left) // BLOCK_N)
    else:
        n_block_min = 0
    n_block_max = tl.cdiv(k_len, BLOCK_N)
    if is_causal or is_local:
        n_block_max = min(n_block_max, tl.cdiv((m_block + 1) * BLOCK_M + k_len - q_len + window_size_right, BLOCK_N))
    if is_dropout:
        philox_seed = tl.load(philox_args).to(tl.uint64)
        philox_offset = tl.load(philox_args + 1).to(tl.uint64)
    if is_paged:
        page_table_ptr += bid * page_table_batch_stride
    q_row_offset = hid * q_head_stride
    k_row_offset = hid // h_hk_ratio * k_head_stride
    k_ptr_base = k_ptr + k_row_offset
    v_ptr_base = v_ptr + hid // h_hk_ratio * v_head_stride
    gQ = tl.make_block_ptr(base=q_ptr + q_offset + q_row_offset, shape=(q_len, d), strides=(q_row_stride, 1), offsets=(0, 0), block_shape=(BLOCK_M, BLOCK_K), order=(1, 0))
    bQ = tl.load(gQ.advance([m_block * BLOCK_M, 0]), boundary_check=(0, 1))
    acc_ = tl.zeros((BLOCK_M, BLOCK_K), dtype=tl.float32)
    rowmax_ = tl.full([BLOCK_M], float('-inf'), dtype=tl.float32)
    rowsum_ = tl.zeros([BLOCK_M], dtype=tl.float32)
    if is_alibi:
        alibi_offset = bid * alibi_slopes_batch_stride + hid
        alibi_slope = tl.load(alibi_slopes_ptr + alibi_offset)
        alibi_slope /= scale_softmax
    else:
        alibi_slope = 0.0
    if not is_causal and (not is_local):
        n_masking_steps = 1
    elif is_even_mn:
        n_masking_steps = tl.cdiv(BLOCK_M, BLOCK_N)
    else:
        n_masking_steps = tl.cdiv(BLOCK_M, BLOCK_N) + 1
    n_masking_steps = min(n_block_max - n_block_min, n_masking_steps)
    row_idx = m_block * BLOCK_M + tl.arange(0, BLOCK_M)
    n_block = n_block_max - 1
    for step in tl.range(0, n_masking_steps):
        col_idx = n_block * BLOCK_N + tl.arange(0, BLOCK_N)
        if is_paged:
            page2_virtual_page_index = col_idx // block_size
            page2_page_offset = col_idx % block_size
            page2_page_block_index = tl.load(page_table_ptr + page2_virtual_page_index, mask=col_idx < k_len, other=0).to(tl.int64)
            cache1_cache_offset = page2_page_block_index * k_page_stride + page2_page_offset * k_row_stride
            cache1_k_offset = tl.arange(0, BLOCK_K)[:, None] + cache1_cache_offset[None, :]
            cache1_v_offset = tl.arange(0, BLOCK_K)[None, :] + cache1_cache_offset[:, None]
            if d == BLOCK_K:
                cache1_bK_mask = col_idx[None, :] < k_len
                cache1_bV_mask = col_idx[:, None] < k_len
                cache1_bK = tl.load(k_ptr_base + cache1_k_offset, mask=cache1_bK_mask, other=0.0)
                cache1_bV = tl.load(v_ptr_base + cache1_v_offset, mask=cache1_bV_mask, other=0.0)
            else:
                cache1_bK_mask = (tl.arange(0, BLOCK_K)[:, None] < d) & (col_idx[None, :] < k_len)
                cache1_bV_mask = (tl.arange(0, BLOCK_K)[None, :] < d) & (col_idx[:, None] < k_len)
                cache1_bK = tl.load(k_ptr_base + cache1_k_offset, mask=cache1_bK_mask, other=0.0)
                cache1_bV = tl.load(v_ptr_base + cache1_v_offset, mask=cache1_bV_mask, other=0.0)
            (bK, bV) = (cache1_bK, cache1_bV)
        else:
            start_n = n_block * BLOCK_N
            k_ptr_seq = k_ptr_base + k_offset
            v_ptr_seq = v_ptr_base + v_offset
            gK = tl.make_block_ptr(base=k_ptr_seq, shape=(k_len, d), strides=(k_row_stride, 1), offsets=(start_n, 0), block_shape=(BLOCK_N, BLOCK_K), order=(0, 1))
            gV = tl.make_block_ptr(base=v_ptr_seq, shape=(k_len, d), strides=(v_row_stride, 1), offsets=(start_n, 0), block_shape=(BLOCK_N, BLOCK_K), order=(0, 1))
            bK = tl.load(gK, boundary_check=(0, 1))
            bK = tl.trans(bK)
            bV = tl.load(gV, boundary_check=(0, 1))
        S = tl.dot(bQ, bK, out_dtype=tl.float32)
        softcap3_S = S
        if is_softcap:
            softcap3_S = 2.0 / (1.0 + tl.exp(-(2.0 * (softcap3_S * softcap)))) - 1.0
        S = softcap3_S
        local4_apply_alibi_S = S
        if is_alibi:
            if is_causal:
                local4_apply_alibi_bias = alibi_slope * (-k_len + 1 + col_idx[None, :]).to(tl.float32)
                local4_apply_alibi_S += local4_apply_alibi_bias
            else:
                local4_apply_alibi_bias = -alibi_slope * tl.abs(col_idx[None, :] - k_len + q_len - row_idx[:, None]).to(tl.float32)
                local4_apply_alibi_S += local4_apply_alibi_bias
        S = local4_apply_alibi_S
        mask5_S = S
        mask5_need_mask = is_causal | is_local | (not is_even_mn)
        if mask5_need_mask:
            mask5_col_lb = max(0, row_idx + k_len - q_len - window_size_left)
            mask5_col_rb = min(k_len - 1, row_idx + k_len - q_len + window_size_right)
            if is_causal:
                mask5_S = tl.where(col_idx[None, :] > mask5_col_rb[:, None], float('-inf'), mask5_S)
            if is_local:
                mask5_S = tl.where((col_idx[None, :] > mask5_col_rb[:, None]) | (col_idx[None, :] < mask5_col_lb[:, None]), float('-inf'), mask5_S)
            if (not is_local) & (not is_causal) & (not is_even_mn):
                mask5_S = tl.where(col_idx[None, :] >= k_len, float('-inf'), mask5_S)
        S = mask5_S
        softmax6_O_acc = acc_
        softmax6_row_max = rowmax_
        softmax6_row_sum = rowsum_
        softmax6_prev_max = softmax6_row_max
        softmax6_row_max = tl.maximum(softmax6_row_max, tl.max(S, 1))
        softmax6_cur_max = tl.where(softmax6_row_max == float('-inf'), 0, softmax6_row_max)
        softmax6_p_scale = tl.exp2((softmax6_prev_max - softmax6_cur_max) * scale_softmax_log2)
        softmax6_row_sum *= softmax6_p_scale
        softmax6_O_acc *= softmax6_p_scale[:, None]
        softmax6_max_scaled = tl.where(softmax6_row_max == float('-inf'), 0, softmax6_row_max * scale_softmax_log2)
        softmax6_P = tl.exp2(S * scale_softmax_log2 - softmax6_max_scaled[:, None])
        softmax6_row_sum = softmax6_row_sum + tl.sum(softmax6_P, 1)
        (acc_, P, rowmax_, rowsum_) = (softmax6_O_acc, softmax6_P, softmax6_row_max, softmax6_row_sum)
        P = P.to(v_ptr.type.element_ty)
        if is_dropout:
            dropout7_P = P
            dropout7_row_start = n_block * BLOCK_N
            dropout7_col_start = m_block * BLOCK_M
            if is_dropout:
                dropout7_row_start = tl.multiple_of(dropout7_row_start, BLOCK_M)
                dropout7_col_start = tl.multiple_of(dropout7_col_start, BLOCK_N)
                dropout7_row = dropout7_row_start + tl.arange(0, BLOCK_M)[:, None]
                dropout7_col = dropout7_col_start // 4 + tl.arange(0, BLOCK_N // 4)[None, :]
                dropout7_subsequence = dropout7_row.to(tl.uint64) * k_len + dropout7_col.to(tl.uint64)
                dropout7_offset = philox_offset + bid * h + hid
                dropout7_offset += dropout7_subsequence * 0
                split9_x = philox_seed.to(tl.uint64)
                (rng8_k0, rng8_k1) = ((split9_x >> 32).to(tl.uint32), (split9_x & 4294967295).to(tl.uint32))
                split10_x = dropout7_offset.to(tl.uint64)
                (rng8_c0, rng8_c1) = ((split10_x >> 32).to(tl.uint32), (split10_x & 4294967295).to(tl.uint32))
                split11_x = dropout7_subsequence.to(tl.uint64)
                (rng8_c2, rng8_c3) = ((split11_x >> 32).to(tl.uint32), (split11_x & 4294967295).to(tl.uint32))
                for rng8__ in tl.static_range(6):
                    rng8_res0 = 3528531795 * rng8_c0.to(tl.uint64)
                    rng8_res1 = 3449720151 * rng8_c2.to(tl.uint64)
                    (rng8_res0_x, rng8_res0_y) = ((rng8_res0 >> 32).to(tl.uint32), (rng8_res0 & 4294967295).to(tl.uint32))
                    (rng8_res1_x, rng8_res1_y) = ((rng8_res1 >> 32).to(tl.uint32), (rng8_res1 & 4294967295).to(tl.uint32))
                    (rng8_c0, rng8_c1, rng8_c2, rng8_c3) = (rng8_res1_y ^ rng8_c1 ^ rng8_k0, rng8_res1_x, rng8_res0_y ^ rng8_c3 ^ rng8_k1, rng8_res0_x)
                    rng8_k0 += 2654435769
                    rng8_k1 += 3144134277
                rng8_res0 = 3528531795 * rng8_c0.to(tl.uint64)
                rng8_res1 = 3449720151 * rng8_c2.to(tl.uint64)
                (rng8_res0_x, rng8_res0_y) = ((rng8_res0 >> 32).to(tl.uint32), (rng8_res0 & 4294967295).to(tl.uint32))
                (rng8_res1_x, rng8_res1_y) = ((rng8_res1 >> 32).to(tl.uint32), (rng8_res1 & 4294967295).to(tl.uint32))
                (rng8_c0, rng8_c1, rng8_c2, rng8_c3) = (rng8_res1_y ^ rng8_c1 ^ rng8_k0, rng8_res1_x, rng8_res0_y ^ rng8_c3 ^ rng8_k1, rng8_res0_x)
                (dropout7_r0, dropout7_r1, dropout7_r2, dropout7_r3) = (rng8_c0, rng8_c1, rng8_c2, rng8_c3)
                dropout7_r = tl.join(tl.join(dropout7_r0, dropout7_r1), tl.join(dropout7_r2, dropout7_r3)).reshape(BLOCK_M, BLOCK_N)
                dropout7_mask = dropout7_r & 255 >= p_dropout_in_uint8_t
                dropmask16_P = dropout7_P
                dropmask16_P = tl.where(dropout7_mask, (dropmask16_P * 0).to(dropmask16_P.dtype), dropmask16_P)
                dropout7_P = dropmask16_P
            P = dropout7_P
        acc_ = tl.dot(P, bV, acc_)
        n_block -= 1
    for n_block in tl.range(n_block_max - n_masking_steps - 1, n_block_min - 1, step=-1):
        col_idx = n_block * BLOCK_N + tl.arange(0, BLOCK_N)
        if is_paged:
            page18_virtual_page_index = col_idx // block_size
            page18_page_offset = col_idx % block_size
            page18_page_block_index = tl.load(page_table_ptr + page18_virtual_page_index).to(tl.int64)
            cache17_cache_offset = page18_page_block_index * k_page_stride + page18_page_offset * k_row_stride
            cache17_k_offset = tl.arange(0, BLOCK_K)[:, None] + cache17_cache_offset[None, :]
            cache17_v_offset = tl.arange(0, BLOCK_K)[None, :] + cache17_cache_offset[:, None]
            if d == BLOCK_K:
                cache17_bK_mask = col_idx[None, :] < k_len
                cache17_bV_mask = col_idx[:, None] < k_len
                cache17_bK = tl.load(k_ptr_base + cache17_k_offset, mask=cache17_bK_mask, other=0.0)
                cache17_bV = tl.load(v_ptr_base + cache17_v_offset, mask=cache17_bV_mask, other=0.0)
            else:
                cache17_bK_mask = (tl.arange(0, BLOCK_K)[:, None] < d) & (col_idx[None, :] < k_len)
                cache17_bV_mask = (tl.arange(0, BLOCK_K)[None, :] < d) & (col_idx[:, None] < k_len)
                cache17_bK = tl.load(k_ptr_base + cache17_k_offset, mask=cache17_bK_mask, other=0.0)
                cache17_bV = tl.load(v_ptr_base + cache17_v_offset, mask=cache17_bV_mask, other=0.0)
            (bK, bV) = (cache17_bK, cache17_bV)
        else:
            start_n = n_block * BLOCK_N
            k_ptr_seq = k_ptr_base + k_offset
            v_ptr_seq = v_ptr_base + v_offset
            gK = tl.make_block_ptr(base=k_ptr_seq, shape=(k_len, d), strides=(k_row_stride, 1), offsets=(start_n, 0), block_shape=(BLOCK_N, BLOCK_K), order=(0, 1))
            gV = tl.make_block_ptr(base=v_ptr_seq, shape=(k_len, d), strides=(v_row_stride, 1), offsets=(start_n, 0), block_shape=(BLOCK_N, BLOCK_K), order=(0, 1))
            bK = tl.load(gK)
            bK = tl.trans(bK)
            bV = tl.load(gV)
        S = tl.dot(bQ, bK, out_dtype=tl.float32)
        softcap19_S = S
        if is_softcap:
            softcap19_S = 2.0 / (1.0 + tl.exp(-(2.0 * (softcap19_S * softcap)))) - 1.0
        S = softcap19_S
        local20_apply_alibi_S = S
        if is_alibi:
            if is_causal:
                local20_apply_alibi_bias = alibi_slope * (-k_len + 1 + col_idx[None, :]).to(tl.float32)
                local20_apply_alibi_S += local20_apply_alibi_bias
            else:
                local20_apply_alibi_bias = -alibi_slope * tl.abs(col_idx[None, :] - k_len + q_len - row_idx[:, None]).to(tl.float32)
                local20_apply_alibi_S += local20_apply_alibi_bias
        S = local20_apply_alibi_S
        mask21_S = S
        mask21_need_mask = False | is_local | (not True)
        if mask21_need_mask:
            mask21_col_lb = max(0, row_idx + k_len - q_len - window_size_left)
            mask21_col_rb = min(k_len - 1, row_idx + k_len - q_len + window_size_right)
            if is_local:
                mask21_S = tl.where((col_idx[None, :] > mask21_col_rb[:, None]) | (col_idx[None, :] < mask21_col_lb[:, None]), float('-inf'), mask21_S)
            if (not is_local) & (not False) & (not True):
                mask21_S = tl.where(col_idx[None, :] >= k_len, float('-inf'), mask21_S)
        S = mask21_S
        softmax22_O_acc = acc_
        softmax22_row_max = rowmax_
        softmax22_row_sum = rowsum_
        softmax22_prev_max = softmax22_row_max
        softmax22_row_max = tl.maximum(softmax22_row_max, tl.max(S, 1))
        if is_local:
            softmax22_cur_max = tl.where(softmax22_row_max == float('-inf'), 0, softmax22_row_max)
        else:
            softmax22_cur_max = softmax22_row_max
        softmax22_p_scale = tl.exp2((softmax22_prev_max - softmax22_cur_max) * scale_softmax_log2)
        softmax22_row_sum *= softmax22_p_scale
        softmax22_O_acc *= softmax22_p_scale[:, None]
        softmax22_max_scaled = tl.where(softmax22_row_max == float('-inf'), 0, softmax22_row_max * scale_softmax_log2)
        softmax22_P = tl.exp2(S * scale_softmax_log2 - softmax22_max_scaled[:, None])
        softmax22_row_sum = softmax22_row_sum + tl.sum(softmax22_P, 1)
        (acc_, P, rowmax_, rowsum_) = (softmax22_O_acc, softmax22_P, softmax22_row_max, softmax22_row_sum)
        P = P.to(v_ptr.type.element_ty)
        if is_dropout:
            dropout23_P = P
            dropout23_row_start = m_block * BLOCK_M
            dropout23_col_start = n_block * BLOCK_N
            if is_dropout:
                dropout23_row_start = tl.multiple_of(dropout23_row_start, BLOCK_M)
                dropout23_col_start = tl.multiple_of(dropout23_col_start, BLOCK_N)
                dropout23_row = dropout23_row_start + tl.arange(0, BLOCK_M)[:, None]
                dropout23_col = dropout23_col_start // 4 + tl.arange(0, BLOCK_N // 4)[None, :]
                dropout23_subsequence = dropout23_row.to(tl.uint64) * k_len + dropout23_col.to(tl.uint64)
                dropout23_offset = philox_offset + bid * h + hid
                dropout23_offset += dropout23_subsequence * 0
                split25_x = philox_seed.to(tl.uint64)
                (rng24_k0, rng24_k1) = ((split25_x >> 32).to(tl.uint32), (split25_x & 4294967295).to(tl.uint32))
                split26_x = dropout23_offset.to(tl.uint64)
                (rng24_c0, rng24_c1) = ((split26_x >> 32).to(tl.uint32), (split26_x & 4294967295).to(tl.uint32))
                split27_x = dropout23_subsequence.to(tl.uint64)
                (rng24_c2, rng24_c3) = ((split27_x >> 32).to(tl.uint32), (split27_x & 4294967295).to(tl.uint32))
                for rng24__ in tl.static_range(6):
                    rng24_res0 = 3528531795 * rng24_c0.to(tl.uint64)
                    rng24_res1 = 3449720151 * rng24_c2.to(tl.uint64)
                    (rng24_res0_x, rng24_res0_y) = ((rng24_res0 >> 32).to(tl.uint32), (rng24_res0 & 4294967295).to(tl.uint32))
                    (rng24_res1_x, rng24_res1_y) = ((rng24_res1 >> 32).to(tl.uint32), (rng24_res1 & 4294967295).to(tl.uint32))
                    (rng24_c0, rng24_c1, rng24_c2, rng24_c3) = (rng24_res1_y ^ rng24_c1 ^ rng24_k0, rng24_res1_x, rng24_res0_y ^ rng24_c3 ^ rng24_k1, rng24_res0_x)
                    rng24_k0 += 2654435769
                    rng24_k1 += 3144134277
                rng24_res0 = 3528531795 * rng24_c0.to(tl.uint64)
                rng24_res1 = 3449720151 * rng24_c2.to(tl.uint64)
                (rng24_res0_x, rng24_res0_y) = ((rng24_res0 >> 32).to(tl.uint32), (rng24_res0 & 4294967295).to(tl.uint32))
                (rng24_res1_x, rng24_res1_y) = ((rng24_res1 >> 32).to(tl.uint32), (rng24_res1 & 4294967295).to(tl.uint32))
                (rng24_c0, rng24_c1, rng24_c2, rng24_c3) = (rng24_res1_y ^ rng24_c1 ^ rng24_k0, rng24_res1_x, rng24_res0_y ^ rng24_c3 ^ rng24_k1, rng24_res0_x)
                (dropout23_r0, dropout23_r1, dropout23_r2, dropout23_r3) = (rng24_c0, rng24_c1, rng24_c2, rng24_c3)
                dropout23_r = tl.join(tl.join(dropout23_r0, dropout23_r1), tl.join(dropout23_r2, dropout23_r3)).reshape(BLOCK_M, BLOCK_N)
                dropout23_mask = dropout23_r & 255 >= p_dropout_in_uint8_t
                dropmask32_P = dropout23_P
                dropmask32_P = tl.where(dropout23_mask, (dropmask32_P * 0).to(dropmask32_P.dtype), dropmask32_P)
                dropout23_P = dropmask32_P
            P = dropout23_P
        acc_ = tl.dot(P, bV, acc_)
    lse = tl.where(rowsum_ == 0 | (rowsum_ != rowsum_), float('inf'), rowmax_ * scale_softmax + tl.log(rowsum_))
    inv_sum = tl.where(rowsum_ == 0 | (rowsum_ != rowsum_), 1.0, 1.0 / rowsum_)
    acc_ *= inv_sum[:, None]
    if is_dropout:
        acc_ *= rp_dropout
    out = acc_.to(o_ptr.type.element_ty)
    o_row_offset = hid * o_head_stride
    gO = tl.make_block_ptr(base=o_ptr + o_offset + o_row_offset, shape=(q_len, d), strides=(o_row_stride, 1), offsets=(0, 0), block_shape=(BLOCK_M, BLOCK_K), order=(1, 0))
    tl.store(gO.advance([m_block * BLOCK_M, 0]), out, boundary_check=(0, 1))
    softmax_lse_ptr += hid * total_q
    lse_row_offset = lse_offset + m_block * BLOCK_M + tl.arange(0, BLOCK_M)
    tl.store(softmax_lse_ptr + lse_row_offset, lse, mask=lse_row_offset < lse_offset + q_len)

# ------------------------------------------------------------------ ② case 层
# (shape,) 的角色:第一个是典型用法,其余是泛化/尾块/退化用例。
#   (2, 17, 19, 4, 2, 16)
#   (3, 33, 35, 6, 2, 32)
#   (4, 65, 67, 8, 4, 64)
#   (2, 17, 35, 4, 2, 16, 0, 0, 1)
#   (2, 17, 35, 4, 2, 16, 1, 1, 1)
#   (2, 17, 35, 4, 2, 16, 1, 0, 1)
#   (2, 17, 35, 4, 2, 16, 0, 1, 1)
#   (3, 17, 19, 4, 2, 16)
# DTYPES: float16, bfloat16 —— 原始用途的 dtype 在前;非法域(例如本机 Triton 只吃 fp32 的exp/sqrt/erf/atomic)的算子只声明合法的那一种。

SUPPORT_STATUS = "supported"
VALIDATION_SCOPE = "full-launch-correctness"
SEED = 20260826
def _aligned(values, dtype, alignment=64):
    import numpy as np

    values = np.asarray(values, dtype=np.dtype(dtype))
    raw = np.empty(values.size * values.dtype.itemsize + alignment, dtype=np.uint8)
    start = -raw.ctypes.data % alignment
    result = raw[start : start + values.size * values.dtype.itemsize].view(values.dtype)
    result[...] = values.reshape(-1)
    return result.reshape(values.shape)
def _comparison(outputs, exact=False, rtol=0.0001, atol=0.0001, dtype=None):
    if not exact:
        _comparison_dtype_policy = str(dtype)
        if _comparison_dtype_policy == 'float32':
            (rtol, atol) = (0.0001, 0.0001)
        elif _comparison_dtype_policy == 'bfloat16':
            (rtol, atol) = (0.01, 0.01)
    return {name: {'profile': 'exact' if exact else 'elementwise-strict', 'comparator': 'array_equal' if exact else 'allclose', 'exact': bool(exact), 'rtol': 0.0 if exact else float(rtol), 'atol': 0.0 if exact else float(atol), 'equal_nan': not exact} for name in outputs}
def _layouts(args):
    import numpy as np

    return {
        name: {
            "shape": tuple(int(value) for value in np.asarray(array).shape),
            "strides": tuple(int(value // np.asarray(array).dtype.itemsize) for value in np.asarray(array).strides),
        }
        for name, array in args.items()
        if isinstance(array, np.ndarray)
    }

SHAPES = ((2, 17, 19, 4, 2, 16), (3, 17, 19, 6, 2, 32))
DTYPES = ('float16', 'bfloat16', 'float32')
FIXED_META = {"is_softcap": False, "softcap": 0.0, "is_dropout": False, "p_dropout": 1.0, "rp_dropout": 1.0, "p_dropout_in_uint8_t": 255, "return_softmax": False, "is_causal": False, "is_local": False, "window_size_left": -1, "window_size_right": -1, "seqlenq_ngroups_swapped": False, "is_paged": False, "is_alibi": False, "alibi_slopes_batch_stride": 0, "page_table_batch_stride": 0, "block_size": 1, "BLOCK_M": 16, "BLOCK_N": 16, "KERNEL_NUM_WARPS": 4, "PIPELINE_STAGES": 1}
LAUNCH_META = {"num_warps": 4, "num_stages": 1}
def ref(args, meta):
    import numpy as np

    if meta["is_paged"] or any(meta[name] for name in
            ("is_dropout", "is_alibi", "is_causal", "is_local", "is_softcap")):
        raise ValueError("reference covers dense unmasked attention only")
    h, d, ratio = (int(meta[name]) for name in ("h", "d", "h_hk_ratio"))
    output = np.asarray(args["o_ptr"]).copy()
    lse = np.asarray(args["softmax_lse_ptr"]).copy()
    for batch in range(int(args["b"])):
        offsets = {}
        lengths = {}
        for name in ("q", "k"):
            if meta["is_cu_seqlens_" + name]:
                ends = args["cu_seqlens_" + name + "_ptr"]
                start, stop = int(ends[batch]), int(ends[batch + 1])
                lengths[name] = stop - start
                offsets[name] = start * args[name + "_row_stride"]
            else:
                start = batch * args["seqlen_" + name]
                lengths[name] = args["seqlen_" + name]
                offsets[name] = batch * args[name + "_batch_stride"]
            if name == "q":
                q_start = start
                offsets["o"] = (start * args["o_row_stride"] if meta["is_cu_seqlens_q"]
                                else batch * args["o_batch_stride"])
            else:
                offsets["v"] = (start * args["v_row_stride"] if meta["is_cu_seqlens_k"]
                                else batch * args["v_batch_stride"])
        if meta["is_seqused_k"]:
            lengths["k"] = int(args["seqused_k_ptr"][batch])
        for head in range(h):
            tiles = {}
            indices = {}
            for name in ("q", "k", "v", "o"):
                count = lengths["q" if name in ("q", "o") else "k"]
                tile_head = head if name in ("q", "o") else head // ratio
                idx = (offsets[name] + tile_head * args[name + "_head_stride"]
                       + np.arange(count)[:, None] * args[name + "_row_stride"]
                       + np.arange(d)[None, :])
                indices[name] = idx
                tiles[name] = np.asarray(args[name + "_ptr"])[idx].astype(np.float32)
            scores = (tiles["q"] @ tiles["k"].T) * np.float32(meta["scale_softmax"])
            maximum = scores.max(axis=1, keepdims=True)
            weights = np.exp(scores - maximum)
            denominator = weights.sum(axis=1, keepdims=True)
            output[indices["o"]] = (weights / denominator) @ tiles["v"]
            lse[head * args["total_q"] + q_start + np.arange(lengths["q"])] = (
                maximum[:, 0] + np.log(denominator[:, 0]))
    return {"o_ptr": output, "softmax_lse_ptr": lse}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    import math
    import numpy as np
    (batches, max_q, max_k, h, hk, d) = (int(value) for value in shape[:6])
    var_q, var_k, strided = (True, True, False) if len(shape) == 6 else map(bool, shape[6:])
    if min(batches, max_q, max_k, h, hk, d) <= 0 or h % hk:
        raise ValueError('shape must be positive (B,maxQ,maxK,H,Hk,D) with H divisible by Hk')
    if d & d - 1:
        raise ValueError('this fixture requires a power-of-two head dimension')
    dtype_name = str(dtype).rsplit('.', 1)[-1]
    storage_dtype = 'float16' if dtype_name == 'float16' else 'float32'
    q_lengths = np.asarray([max_q - 2 * batch for batch in range(batches)], dtype=np.int32)
    k_lengths = np.asarray([max_k - 3 * batch for batch in range(batches)], dtype=np.int32)
    if not var_q:
        q_lengths[:] = max_q
    if not var_k:
        k_lengths[:] = max_k
    if q_lengths.min() <= 0 or k_lengths.min() <= 0:
        raise ValueError('batch count is too large for the supplied maximum lengths')
    cu_q = np.concatenate((np.asarray([0], dtype=np.int32), np.cumsum(q_lengths, dtype=np.int32)))
    cu_k = np.concatenate((np.asarray([0], dtype=np.int32), np.cumsum(k_lengths, dtype=np.int32)))
    (total_q, total_k) = (int(cu_q[-1]), int(cu_k[-1]))
    from case_utils import fast_rng
    rng = fast_rng(seed)
    args = {'q_ptr': _aligned(rng.normal(0.0, 0.25, total_q * h * d), storage_dtype), 'k_ptr': _aligned(rng.normal(0.0, 0.25, total_k * hk * d), storage_dtype), 'v_ptr': _aligned(rng.normal(0.0, 0.25, total_k * hk * d), storage_dtype), 'o_ptr': _aligned(np.full(total_q * h * d, -0.875), storage_dtype), 'p_ptr': _aligned(np.zeros(1), 'float32'), 'softmax_lse_ptr': _aligned(np.full(h * total_q, -np.inf), 'float32'), 'q_row_stride': h * d, 'k_row_stride': hk * d, 'v_row_stride': hk * d, 'q_head_stride': d, 'k_head_stride': d, 'v_head_stride': d, 'o_row_stride': h * d, 'o_head_stride': d, 'q_batch_stride': 0, 'k_batch_stride': 0, 'v_batch_stride': 0, 'o_batch_stride': 0, 'cu_seqlens_q_ptr': _aligned(cu_q, 'int32'), 'cu_seqlens_k_ptr': _aligned(cu_k, 'int32'), 'seqused_k_ptr': _aligned(k_lengths, 'int32'), 'b': batches, 'bk': batches, 'seqlen_q': max_q, 'seqlen_k': max_k, 'seqlen_q_rounded': (max_q + 127) // 128 * 128, 'seqlen_k_rounded': (max_k + 31) // 32 * 32, 'philox_args': _aligned([seed, 0], 'uint64'), 'alibi_slopes_ptr': _aligned(np.zeros(1), 'float32'), 'total_q': total_q, 'page_table_ptr': _aligned(np.zeros(1), 'int32'), 'k_page_stride': total_k * hk * d}
    args["q_batch_stride"] = max_q * h * d
    args["o_batch_stride"] = max_q * h * d
    args["k_batch_stride"] = max_k * hk * d
    args["v_batch_stride"] = max_k * hk * d
    if strided:
        for name, head_pad, row_pad, batch_pad in (("k", 3, 5, 7), ("v", 7, 11, 13)):
            logical = args[name + "_ptr"].reshape(total_k, hk, d).copy()
            head_stride = d + head_pad
            row_stride = hk * head_stride + row_pad
            batch_stride = max_k * row_stride + batch_pad
            extent = total_k * row_stride if var_k else batches * batch_stride
            packed = np.full(extent, -3.0, dtype=logical.dtype)
            for batch in range(batches):
                start, stop = int(cu_k[batch]), int(cu_k[batch + 1])
                base = start * row_stride if var_k else batch * batch_stride
                idx = (base + np.arange(stop - start)[:, None, None] * row_stride
                       + np.arange(hk)[None, :, None] * head_stride
                       + np.arange(d)[None, None, :])
                packed[idx] = logical[start:stop]
            args[name + "_ptr"] = _aligned(packed, storage_dtype)
            args[name + "_head_stride"] = head_stride
            args[name + "_row_stride"] = row_stride
            args[name + "_batch_stride"] = batch_stride
    scale = 1.0 / math.sqrt(d)
    meta = {**FIXED_META, 'is_cu_seqlens_q': var_q, 'is_cu_seqlens_k': var_k, 'is_seqused_k': False, 'h': h, 'hk': hk, 'h_hk_ratio': h // hk, 'd': d, 'd_rounded': d, 'scale_softmax': scale, 'scale_softmax_log2': scale * math.log2(math.e), 'BLOCK_K': d}
    grid = ((max_q + meta['BLOCK_M'] - 1) // meta['BLOCK_M'], batches, h)
    outputs = ('o_ptr', 'softmax_lse_ptr')
    pointer_dtypes = {'q_ptr': dtype_name, 'k_ptr': dtype_name, 'v_ptr': dtype_name, 'o_ptr': dtype_name, 'p_ptr': 'float32', 'softmax_lse_ptr': 'float32', 'cu_seqlens_q_ptr': 'int32', 'cu_seqlens_k_ptr': 'int32', 'seqused_k_ptr': 'int32', 'philox_args': 'uint64', 'alibi_slopes_ptr': 'float32', 'page_table_ptr': 'int32'}
    return {'kernel': flash_varlen_fwd_kernel, 'grid': grid, 'args': args, 'meta': meta, 'launch_meta': dict(LAUNCH_META), 'inputs': ('q_ptr', 'k_ptr', 'v_ptr', 'cu_seqlens_q_ptr', 'cu_seqlens_k_ptr'), 'outputs': outputs, 'expected': ref(args, meta), 'comparison': _comparison(outputs, rtol=0.03, atol=0.03, dtype=str(dtype)), 'pointer_dtypes': pointer_dtypes, 'buffer_extents': {name: int(value.size) for (name, value) in args.items() if isinstance(value, np.ndarray)}, 'buffer_layouts': _layouts(args), 'alignment': 64, 'aliases': {}, 'seed': int(seed), 'shape': tuple(shape), 'dtype': str(dtype), 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'coverage': {'complete_logical_output': True, 'grid_formula': '(ceil_div(max_seqlen_q,BLOCK_M), batch, heads)', 'variable_lengths': {'q': tuple((int(x) for x in q_lengths)), 'k': tuple((int(x) for x in k_lengths))}, 'specialization': 'dense-no-dropout-no-paging-no-alibi', 'variable_q': var_q, 'variable_k': var_k, 'independent_kv_strides': strided}}
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
_ENRICH_BASE = 'float16'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float16': 'float16', 'bfloat16': 'bfloat16'}


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
