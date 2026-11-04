"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/small4_square_svd_kernel_cc0a90a31fcf1df1", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def _small4_square_svd_kernel(A, U, S, V, BATCH: tl.constexpr, BLOCK_B: tl.constexpr, SWEEPS: tl.constexpr):
    pid = tl.program_id(0)
    b = pid * BLOCK_B + tl.arange(0, BLOCK_B)
    r = tl.arange(0, 4)
    bb = b[:, None]
    rr = r[None, :]
    mask = b < BATCH
    full_mask = (bb < BATCH) & (rr < 4)
    base = A + bb * 16 + rr * 4
    c0 = tl.load(base, mask=full_mask, other=0.0).to(tl.float32)
    c1 = tl.load(base + 1, mask=full_mask, other=0.0).to(tl.float32)
    c2 = tl.load(base + 2, mask=full_mask, other=0.0).to(tl.float32)
    c3 = tl.load(base + 3, mask=full_mask, other=0.0).to(tl.float32)
    v0 = tl.where(rr == 0, 1.0, 0.0)
    v1 = tl.where(rr == 1, 1.0, 0.0)
    v2 = tl.where(rr == 2, 1.0, 0.0)
    v3 = tl.where(rr == 3, 1.0, 0.0)
    for _ in tl.static_range(0, SWEEPS):
        _inl_1_rotate_pair_4_ap = c0
        _inl_1_rotate_pair_4_aq = c1
        _inl_1_rotate_pair_4_vp = v0
        _inl_1_rotate_pair_4_vq = v1
        _inl_1_rotate_pair_4_eps = 1e-20
        _inl_1_rotate_pair_4_alpha = tl.sum(_inl_1_rotate_pair_4_ap * _inl_1_rotate_pair_4_ap, axis=1)
        _inl_1_rotate_pair_4_beta = tl.sum(_inl_1_rotate_pair_4_aq * _inl_1_rotate_pair_4_aq, axis=1)
        _inl_1_rotate_pair_4_gamma = tl.sum(_inl_1_rotate_pair_4_ap * _inl_1_rotate_pair_4_aq, axis=1)
        _inl_1_rotate_pair_4_abs_gamma = tl.abs(_inl_1_rotate_pair_4_gamma)
        _inl_1_rotate_pair_4_threshold = 1e-07 * tl.sqrt(_inl_1_rotate_pair_4_alpha * _inl_1_rotate_pair_4_beta + _inl_1_rotate_pair_4_eps)
        _inl_1_rotate_pair_4_active = _inl_1_rotate_pair_4_abs_gamma > _inl_1_rotate_pair_4_threshold
        _inl_1_rotate_pair_4_safe_gamma = tl.where(_inl_1_rotate_pair_4_active, _inl_1_rotate_pair_4_gamma, 1.0)
        _inl_1_rotate_pair_4_tau = (_inl_1_rotate_pair_4_beta - _inl_1_rotate_pair_4_alpha) / (2.0 * _inl_1_rotate_pair_4_safe_gamma)
        _inl_1_rotate_pair_4_sign_tau = tl.where(_inl_1_rotate_pair_4_tau >= 0.0, 1.0, -1.0)
        _inl_1_rotate_pair_4_t = _inl_1_rotate_pair_4_sign_tau / (tl.abs(_inl_1_rotate_pair_4_tau) + tl.sqrt(1.0 + _inl_1_rotate_pair_4_tau * _inl_1_rotate_pair_4_tau))
        _inl_1_rotate_pair_4_c = tl.rsqrt(1.0 + _inl_1_rotate_pair_4_t * _inl_1_rotate_pair_4_t)
        _inl_1_rotate_pair_4_s_rot = _inl_1_rotate_pair_4_t * _inl_1_rotate_pair_4_c
        _inl_1_rotate_pair_4_c = tl.where(_inl_1_rotate_pair_4_active, _inl_1_rotate_pair_4_c, 1.0)
        _inl_1_rotate_pair_4_s_rot = tl.where(_inl_1_rotate_pair_4_active, _inl_1_rotate_pair_4_s_rot, 0.0)
        _inl_1_rotate_pair_4_new_ap = _inl_1_rotate_pair_4_c[:, None] * _inl_1_rotate_pair_4_ap - _inl_1_rotate_pair_4_s_rot[:, None] * _inl_1_rotate_pair_4_aq
        _inl_1_rotate_pair_4_new_aq = _inl_1_rotate_pair_4_s_rot[:, None] * _inl_1_rotate_pair_4_ap + _inl_1_rotate_pair_4_c[:, None] * _inl_1_rotate_pair_4_aq
        _inl_1_rotate_pair_4_new_vp = _inl_1_rotate_pair_4_c[:, None] * _inl_1_rotate_pair_4_vp - _inl_1_rotate_pair_4_s_rot[:, None] * _inl_1_rotate_pair_4_vq
        _inl_1_rotate_pair_4_new_vq = _inl_1_rotate_pair_4_s_rot[:, None] * _inl_1_rotate_pair_4_vp + _inl_1_rotate_pair_4_c[:, None] * _inl_1_rotate_pair_4_vq
        _inl_1_rotate_pair_4_result = (_inl_1_rotate_pair_4_new_ap, _inl_1_rotate_pair_4_new_aq, _inl_1_rotate_pair_4_new_vp, _inl_1_rotate_pair_4_new_vq)
        (c0, c1, v0, v1) = _inl_1_rotate_pair_4_result
        _inl_2_rotate_pair_4_ap = c0
        _inl_2_rotate_pair_4_aq = c2
        _inl_2_rotate_pair_4_vp = v0
        _inl_2_rotate_pair_4_vq = v2
        _inl_2_rotate_pair_4_eps = 1e-20
        _inl_2_rotate_pair_4_alpha = tl.sum(_inl_2_rotate_pair_4_ap * _inl_2_rotate_pair_4_ap, axis=1)
        _inl_2_rotate_pair_4_beta = tl.sum(_inl_2_rotate_pair_4_aq * _inl_2_rotate_pair_4_aq, axis=1)
        _inl_2_rotate_pair_4_gamma = tl.sum(_inl_2_rotate_pair_4_ap * _inl_2_rotate_pair_4_aq, axis=1)
        _inl_2_rotate_pair_4_abs_gamma = tl.abs(_inl_2_rotate_pair_4_gamma)
        _inl_2_rotate_pair_4_threshold = 1e-07 * tl.sqrt(_inl_2_rotate_pair_4_alpha * _inl_2_rotate_pair_4_beta + _inl_2_rotate_pair_4_eps)
        _inl_2_rotate_pair_4_active = _inl_2_rotate_pair_4_abs_gamma > _inl_2_rotate_pair_4_threshold
        _inl_2_rotate_pair_4_safe_gamma = tl.where(_inl_2_rotate_pair_4_active, _inl_2_rotate_pair_4_gamma, 1.0)
        _inl_2_rotate_pair_4_tau = (_inl_2_rotate_pair_4_beta - _inl_2_rotate_pair_4_alpha) / (2.0 * _inl_2_rotate_pair_4_safe_gamma)
        _inl_2_rotate_pair_4_sign_tau = tl.where(_inl_2_rotate_pair_4_tau >= 0.0, 1.0, -1.0)
        _inl_2_rotate_pair_4_t = _inl_2_rotate_pair_4_sign_tau / (tl.abs(_inl_2_rotate_pair_4_tau) + tl.sqrt(1.0 + _inl_2_rotate_pair_4_tau * _inl_2_rotate_pair_4_tau))
        _inl_2_rotate_pair_4_c = tl.rsqrt(1.0 + _inl_2_rotate_pair_4_t * _inl_2_rotate_pair_4_t)
        _inl_2_rotate_pair_4_s_rot = _inl_2_rotate_pair_4_t * _inl_2_rotate_pair_4_c
        _inl_2_rotate_pair_4_c = tl.where(_inl_2_rotate_pair_4_active, _inl_2_rotate_pair_4_c, 1.0)
        _inl_2_rotate_pair_4_s_rot = tl.where(_inl_2_rotate_pair_4_active, _inl_2_rotate_pair_4_s_rot, 0.0)
        _inl_2_rotate_pair_4_new_ap = _inl_2_rotate_pair_4_c[:, None] * _inl_2_rotate_pair_4_ap - _inl_2_rotate_pair_4_s_rot[:, None] * _inl_2_rotate_pair_4_aq
        _inl_2_rotate_pair_4_new_aq = _inl_2_rotate_pair_4_s_rot[:, None] * _inl_2_rotate_pair_4_ap + _inl_2_rotate_pair_4_c[:, None] * _inl_2_rotate_pair_4_aq
        _inl_2_rotate_pair_4_new_vp = _inl_2_rotate_pair_4_c[:, None] * _inl_2_rotate_pair_4_vp - _inl_2_rotate_pair_4_s_rot[:, None] * _inl_2_rotate_pair_4_vq
        _inl_2_rotate_pair_4_new_vq = _inl_2_rotate_pair_4_s_rot[:, None] * _inl_2_rotate_pair_4_vp + _inl_2_rotate_pair_4_c[:, None] * _inl_2_rotate_pair_4_vq
        _inl_2_rotate_pair_4_result = (_inl_2_rotate_pair_4_new_ap, _inl_2_rotate_pair_4_new_aq, _inl_2_rotate_pair_4_new_vp, _inl_2_rotate_pair_4_new_vq)
        (c0, c2, v0, v2) = _inl_2_rotate_pair_4_result
        _inl_3_rotate_pair_4_ap = c0
        _inl_3_rotate_pair_4_aq = c3
        _inl_3_rotate_pair_4_vp = v0
        _inl_3_rotate_pair_4_vq = v3
        _inl_3_rotate_pair_4_eps = 1e-20
        _inl_3_rotate_pair_4_alpha = tl.sum(_inl_3_rotate_pair_4_ap * _inl_3_rotate_pair_4_ap, axis=1)
        _inl_3_rotate_pair_4_beta = tl.sum(_inl_3_rotate_pair_4_aq * _inl_3_rotate_pair_4_aq, axis=1)
        _inl_3_rotate_pair_4_gamma = tl.sum(_inl_3_rotate_pair_4_ap * _inl_3_rotate_pair_4_aq, axis=1)
        _inl_3_rotate_pair_4_abs_gamma = tl.abs(_inl_3_rotate_pair_4_gamma)
        _inl_3_rotate_pair_4_threshold = 1e-07 * tl.sqrt(_inl_3_rotate_pair_4_alpha * _inl_3_rotate_pair_4_beta + _inl_3_rotate_pair_4_eps)
        _inl_3_rotate_pair_4_active = _inl_3_rotate_pair_4_abs_gamma > _inl_3_rotate_pair_4_threshold
        _inl_3_rotate_pair_4_safe_gamma = tl.where(_inl_3_rotate_pair_4_active, _inl_3_rotate_pair_4_gamma, 1.0)
        _inl_3_rotate_pair_4_tau = (_inl_3_rotate_pair_4_beta - _inl_3_rotate_pair_4_alpha) / (2.0 * _inl_3_rotate_pair_4_safe_gamma)
        _inl_3_rotate_pair_4_sign_tau = tl.where(_inl_3_rotate_pair_4_tau >= 0.0, 1.0, -1.0)
        _inl_3_rotate_pair_4_t = _inl_3_rotate_pair_4_sign_tau / (tl.abs(_inl_3_rotate_pair_4_tau) + tl.sqrt(1.0 + _inl_3_rotate_pair_4_tau * _inl_3_rotate_pair_4_tau))
        _inl_3_rotate_pair_4_c = tl.rsqrt(1.0 + _inl_3_rotate_pair_4_t * _inl_3_rotate_pair_4_t)
        _inl_3_rotate_pair_4_s_rot = _inl_3_rotate_pair_4_t * _inl_3_rotate_pair_4_c
        _inl_3_rotate_pair_4_c = tl.where(_inl_3_rotate_pair_4_active, _inl_3_rotate_pair_4_c, 1.0)
        _inl_3_rotate_pair_4_s_rot = tl.where(_inl_3_rotate_pair_4_active, _inl_3_rotate_pair_4_s_rot, 0.0)
        _inl_3_rotate_pair_4_new_ap = _inl_3_rotate_pair_4_c[:, None] * _inl_3_rotate_pair_4_ap - _inl_3_rotate_pair_4_s_rot[:, None] * _inl_3_rotate_pair_4_aq
        _inl_3_rotate_pair_4_new_aq = _inl_3_rotate_pair_4_s_rot[:, None] * _inl_3_rotate_pair_4_ap + _inl_3_rotate_pair_4_c[:, None] * _inl_3_rotate_pair_4_aq
        _inl_3_rotate_pair_4_new_vp = _inl_3_rotate_pair_4_c[:, None] * _inl_3_rotate_pair_4_vp - _inl_3_rotate_pair_4_s_rot[:, None] * _inl_3_rotate_pair_4_vq
        _inl_3_rotate_pair_4_new_vq = _inl_3_rotate_pair_4_s_rot[:, None] * _inl_3_rotate_pair_4_vp + _inl_3_rotate_pair_4_c[:, None] * _inl_3_rotate_pair_4_vq
        _inl_3_rotate_pair_4_result = (_inl_3_rotate_pair_4_new_ap, _inl_3_rotate_pair_4_new_aq, _inl_3_rotate_pair_4_new_vp, _inl_3_rotate_pair_4_new_vq)
        (c0, c3, v0, v3) = _inl_3_rotate_pair_4_result
        _inl_4_rotate_pair_4_ap = c1
        _inl_4_rotate_pair_4_aq = c2
        _inl_4_rotate_pair_4_vp = v1
        _inl_4_rotate_pair_4_vq = v2
        _inl_4_rotate_pair_4_eps = 1e-20
        _inl_4_rotate_pair_4_alpha = tl.sum(_inl_4_rotate_pair_4_ap * _inl_4_rotate_pair_4_ap, axis=1)
        _inl_4_rotate_pair_4_beta = tl.sum(_inl_4_rotate_pair_4_aq * _inl_4_rotate_pair_4_aq, axis=1)
        _inl_4_rotate_pair_4_gamma = tl.sum(_inl_4_rotate_pair_4_ap * _inl_4_rotate_pair_4_aq, axis=1)
        _inl_4_rotate_pair_4_abs_gamma = tl.abs(_inl_4_rotate_pair_4_gamma)
        _inl_4_rotate_pair_4_threshold = 1e-07 * tl.sqrt(_inl_4_rotate_pair_4_alpha * _inl_4_rotate_pair_4_beta + _inl_4_rotate_pair_4_eps)
        _inl_4_rotate_pair_4_active = _inl_4_rotate_pair_4_abs_gamma > _inl_4_rotate_pair_4_threshold
        _inl_4_rotate_pair_4_safe_gamma = tl.where(_inl_4_rotate_pair_4_active, _inl_4_rotate_pair_4_gamma, 1.0)
        _inl_4_rotate_pair_4_tau = (_inl_4_rotate_pair_4_beta - _inl_4_rotate_pair_4_alpha) / (2.0 * _inl_4_rotate_pair_4_safe_gamma)
        _inl_4_rotate_pair_4_sign_tau = tl.where(_inl_4_rotate_pair_4_tau >= 0.0, 1.0, -1.0)
        _inl_4_rotate_pair_4_t = _inl_4_rotate_pair_4_sign_tau / (tl.abs(_inl_4_rotate_pair_4_tau) + tl.sqrt(1.0 + _inl_4_rotate_pair_4_tau * _inl_4_rotate_pair_4_tau))
        _inl_4_rotate_pair_4_c = tl.rsqrt(1.0 + _inl_4_rotate_pair_4_t * _inl_4_rotate_pair_4_t)
        _inl_4_rotate_pair_4_s_rot = _inl_4_rotate_pair_4_t * _inl_4_rotate_pair_4_c
        _inl_4_rotate_pair_4_c = tl.where(_inl_4_rotate_pair_4_active, _inl_4_rotate_pair_4_c, 1.0)
        _inl_4_rotate_pair_4_s_rot = tl.where(_inl_4_rotate_pair_4_active, _inl_4_rotate_pair_4_s_rot, 0.0)
        _inl_4_rotate_pair_4_new_ap = _inl_4_rotate_pair_4_c[:, None] * _inl_4_rotate_pair_4_ap - _inl_4_rotate_pair_4_s_rot[:, None] * _inl_4_rotate_pair_4_aq
        _inl_4_rotate_pair_4_new_aq = _inl_4_rotate_pair_4_s_rot[:, None] * _inl_4_rotate_pair_4_ap + _inl_4_rotate_pair_4_c[:, None] * _inl_4_rotate_pair_4_aq
        _inl_4_rotate_pair_4_new_vp = _inl_4_rotate_pair_4_c[:, None] * _inl_4_rotate_pair_4_vp - _inl_4_rotate_pair_4_s_rot[:, None] * _inl_4_rotate_pair_4_vq
        _inl_4_rotate_pair_4_new_vq = _inl_4_rotate_pair_4_s_rot[:, None] * _inl_4_rotate_pair_4_vp + _inl_4_rotate_pair_4_c[:, None] * _inl_4_rotate_pair_4_vq
        _inl_4_rotate_pair_4_result = (_inl_4_rotate_pair_4_new_ap, _inl_4_rotate_pair_4_new_aq, _inl_4_rotate_pair_4_new_vp, _inl_4_rotate_pair_4_new_vq)
        (c1, c2, v1, v2) = _inl_4_rotate_pair_4_result
        _inl_5_rotate_pair_4_ap = c1
        _inl_5_rotate_pair_4_aq = c3
        _inl_5_rotate_pair_4_vp = v1
        _inl_5_rotate_pair_4_vq = v3
        _inl_5_rotate_pair_4_eps = 1e-20
        _inl_5_rotate_pair_4_alpha = tl.sum(_inl_5_rotate_pair_4_ap * _inl_5_rotate_pair_4_ap, axis=1)
        _inl_5_rotate_pair_4_beta = tl.sum(_inl_5_rotate_pair_4_aq * _inl_5_rotate_pair_4_aq, axis=1)
        _inl_5_rotate_pair_4_gamma = tl.sum(_inl_5_rotate_pair_4_ap * _inl_5_rotate_pair_4_aq, axis=1)
        _inl_5_rotate_pair_4_abs_gamma = tl.abs(_inl_5_rotate_pair_4_gamma)
        _inl_5_rotate_pair_4_threshold = 1e-07 * tl.sqrt(_inl_5_rotate_pair_4_alpha * _inl_5_rotate_pair_4_beta + _inl_5_rotate_pair_4_eps)
        _inl_5_rotate_pair_4_active = _inl_5_rotate_pair_4_abs_gamma > _inl_5_rotate_pair_4_threshold
        _inl_5_rotate_pair_4_safe_gamma = tl.where(_inl_5_rotate_pair_4_active, _inl_5_rotate_pair_4_gamma, 1.0)
        _inl_5_rotate_pair_4_tau = (_inl_5_rotate_pair_4_beta - _inl_5_rotate_pair_4_alpha) / (2.0 * _inl_5_rotate_pair_4_safe_gamma)
        _inl_5_rotate_pair_4_sign_tau = tl.where(_inl_5_rotate_pair_4_tau >= 0.0, 1.0, -1.0)
        _inl_5_rotate_pair_4_t = _inl_5_rotate_pair_4_sign_tau / (tl.abs(_inl_5_rotate_pair_4_tau) + tl.sqrt(1.0 + _inl_5_rotate_pair_4_tau * _inl_5_rotate_pair_4_tau))
        _inl_5_rotate_pair_4_c = tl.rsqrt(1.0 + _inl_5_rotate_pair_4_t * _inl_5_rotate_pair_4_t)
        _inl_5_rotate_pair_4_s_rot = _inl_5_rotate_pair_4_t * _inl_5_rotate_pair_4_c
        _inl_5_rotate_pair_4_c = tl.where(_inl_5_rotate_pair_4_active, _inl_5_rotate_pair_4_c, 1.0)
        _inl_5_rotate_pair_4_s_rot = tl.where(_inl_5_rotate_pair_4_active, _inl_5_rotate_pair_4_s_rot, 0.0)
        _inl_5_rotate_pair_4_new_ap = _inl_5_rotate_pair_4_c[:, None] * _inl_5_rotate_pair_4_ap - _inl_5_rotate_pair_4_s_rot[:, None] * _inl_5_rotate_pair_4_aq
        _inl_5_rotate_pair_4_new_aq = _inl_5_rotate_pair_4_s_rot[:, None] * _inl_5_rotate_pair_4_ap + _inl_5_rotate_pair_4_c[:, None] * _inl_5_rotate_pair_4_aq
        _inl_5_rotate_pair_4_new_vp = _inl_5_rotate_pair_4_c[:, None] * _inl_5_rotate_pair_4_vp - _inl_5_rotate_pair_4_s_rot[:, None] * _inl_5_rotate_pair_4_vq
        _inl_5_rotate_pair_4_new_vq = _inl_5_rotate_pair_4_s_rot[:, None] * _inl_5_rotate_pair_4_vp + _inl_5_rotate_pair_4_c[:, None] * _inl_5_rotate_pair_4_vq
        _inl_5_rotate_pair_4_result = (_inl_5_rotate_pair_4_new_ap, _inl_5_rotate_pair_4_new_aq, _inl_5_rotate_pair_4_new_vp, _inl_5_rotate_pair_4_new_vq)
        (c1, c3, v1, v3) = _inl_5_rotate_pair_4_result
        _inl_6_rotate_pair_4_ap = c2
        _inl_6_rotate_pair_4_aq = c3
        _inl_6_rotate_pair_4_vp = v2
        _inl_6_rotate_pair_4_vq = v3
        _inl_6_rotate_pair_4_eps = 1e-20
        _inl_6_rotate_pair_4_alpha = tl.sum(_inl_6_rotate_pair_4_ap * _inl_6_rotate_pair_4_ap, axis=1)
        _inl_6_rotate_pair_4_beta = tl.sum(_inl_6_rotate_pair_4_aq * _inl_6_rotate_pair_4_aq, axis=1)
        _inl_6_rotate_pair_4_gamma = tl.sum(_inl_6_rotate_pair_4_ap * _inl_6_rotate_pair_4_aq, axis=1)
        _inl_6_rotate_pair_4_abs_gamma = tl.abs(_inl_6_rotate_pair_4_gamma)
        _inl_6_rotate_pair_4_threshold = 1e-07 * tl.sqrt(_inl_6_rotate_pair_4_alpha * _inl_6_rotate_pair_4_beta + _inl_6_rotate_pair_4_eps)
        _inl_6_rotate_pair_4_active = _inl_6_rotate_pair_4_abs_gamma > _inl_6_rotate_pair_4_threshold
        _inl_6_rotate_pair_4_safe_gamma = tl.where(_inl_6_rotate_pair_4_active, _inl_6_rotate_pair_4_gamma, 1.0)
        _inl_6_rotate_pair_4_tau = (_inl_6_rotate_pair_4_beta - _inl_6_rotate_pair_4_alpha) / (2.0 * _inl_6_rotate_pair_4_safe_gamma)
        _inl_6_rotate_pair_4_sign_tau = tl.where(_inl_6_rotate_pair_4_tau >= 0.0, 1.0, -1.0)
        _inl_6_rotate_pair_4_t = _inl_6_rotate_pair_4_sign_tau / (tl.abs(_inl_6_rotate_pair_4_tau) + tl.sqrt(1.0 + _inl_6_rotate_pair_4_tau * _inl_6_rotate_pair_4_tau))
        _inl_6_rotate_pair_4_c = tl.rsqrt(1.0 + _inl_6_rotate_pair_4_t * _inl_6_rotate_pair_4_t)
        _inl_6_rotate_pair_4_s_rot = _inl_6_rotate_pair_4_t * _inl_6_rotate_pair_4_c
        _inl_6_rotate_pair_4_c = tl.where(_inl_6_rotate_pair_4_active, _inl_6_rotate_pair_4_c, 1.0)
        _inl_6_rotate_pair_4_s_rot = tl.where(_inl_6_rotate_pair_4_active, _inl_6_rotate_pair_4_s_rot, 0.0)
        _inl_6_rotate_pair_4_new_ap = _inl_6_rotate_pair_4_c[:, None] * _inl_6_rotate_pair_4_ap - _inl_6_rotate_pair_4_s_rot[:, None] * _inl_6_rotate_pair_4_aq
        _inl_6_rotate_pair_4_new_aq = _inl_6_rotate_pair_4_s_rot[:, None] * _inl_6_rotate_pair_4_ap + _inl_6_rotate_pair_4_c[:, None] * _inl_6_rotate_pair_4_aq
        _inl_6_rotate_pair_4_new_vp = _inl_6_rotate_pair_4_c[:, None] * _inl_6_rotate_pair_4_vp - _inl_6_rotate_pair_4_s_rot[:, None] * _inl_6_rotate_pair_4_vq
        _inl_6_rotate_pair_4_new_vq = _inl_6_rotate_pair_4_s_rot[:, None] * _inl_6_rotate_pair_4_vp + _inl_6_rotate_pair_4_c[:, None] * _inl_6_rotate_pair_4_vq
        _inl_6_rotate_pair_4_result = (_inl_6_rotate_pair_4_new_ap, _inl_6_rotate_pair_4_new_aq, _inl_6_rotate_pair_4_new_vp, _inl_6_rotate_pair_4_new_vq)
        (c2, c3, v2, v3) = _inl_6_rotate_pair_4_result
    s0 = tl.sqrt(tl.sum(c0 * c0, axis=1))
    s1 = tl.sqrt(tl.sum(c1 * c1, axis=1))
    s2 = tl.sqrt(tl.sum(c2 * c2, axis=1))
    s3 = tl.sqrt(tl.sum(c3 * c3, axis=1))
    r0 = (s1 > s0).to(tl.int32) + (s2 > s0).to(tl.int32) + (s3 > s0).to(tl.int32)
    r1 = (s0 >= s1).to(tl.int32) + (s2 > s1).to(tl.int32) + (s3 > s1).to(tl.int32)
    r2 = (s0 >= s2).to(tl.int32) + (s1 >= s2).to(tl.int32) + (s3 > s2).to(tl.int32)
    r3 = (s0 >= s3).to(tl.int32) + (s1 >= s3).to(tl.int32) + (s2 >= s3).to(tl.int32)
    eps = 1e-20
    tl.store(S + b * 4 + r0, s0, mask=mask)
    tl.store(S + b * 4 + r1, s1, mask=mask)
    tl.store(S + b * 4 + r2, s2, mask=mask)
    tl.store(S + b * 4 + r3, s3, mask=mask)
    tl.store(U + bb * 16 + rr * 4 + r0[:, None], c0 / tl.maximum(s0[:, None], eps), mask=full_mask)
    tl.store(U + bb * 16 + rr * 4 + r1[:, None], c1 / tl.maximum(s1[:, None], eps), mask=full_mask)
    tl.store(U + bb * 16 + rr * 4 + r2[:, None], c2 / tl.maximum(s2[:, None], eps), mask=full_mask)
    tl.store(U + bb * 16 + rr * 4 + r3[:, None], c3 / tl.maximum(s3[:, None], eps), mask=full_mask)
    tl.store(V + bb * 16 + rr * 4 + r0[:, None], v0, mask=full_mask)
    tl.store(V + bb * 16 + rr * 4 + r1[:, None], v1, mask=full_mask)
    tl.store(V + bb * 16 + rr * 4 + r2[:, None], v2, mask=full_mask)
    tl.store(V + bb * 16 + rr * 4 + r3[:, None], v3, mask=full_mask)
CASE_SCHEMA = 3
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
    if _comparison_dtype_policy == 'torch.float32':
        (rtol, atol) = (0.0001, 0.0001)
    elif _comparison_dtype_policy == 'torch.bfloat16':
        (rtol, atol) = (0.01, 0.01)
    comparison = {name: {'profile': 'numerical', 'comparator': 'allclose', 'exact': False, 'rtol': float(rtol), 'atol': float(atol), 'equal_nan': True} for name in outputs}
    arrays = {name: value for (name, value) in args.items() if isinstance(value, np.ndarray)}
    return {'kernel': kernel, 'grid': tuple((int(value) for value in grid)), 'args': args, 'meta': meta, 'launch_meta': {'num_warps': 4, 'num_stages': 1}, 'inputs': tuple(inputs), 'outputs': tuple(outputs), 'expected': expected, 'comparison': comparison, 'pointer_dtypes': {name: str(value.dtype) for (name, value) in arrays.items()}, 'buffer_extents': {name: int(value.size) for (name, value) in arrays.items()}, 'buffer_layouts': {name: {'shape': tuple((int(x) for x in value.shape)), 'strides': tuple((int(x // value.dtype.itemsize) for x in value.strides))} for (name, value) in arrays.items()}, 'alignment': 64, 'aliases': {}, 'seed': int(seed), 'shape': tuple(shape), 'dtype': str(dtype), 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'coverage': {'complete_logical_output': True, **coverage}}
SHAPES = ((17,),);DTYPES = ('float32',)
def ref(args,meta):
 import numpy as np
 B=int(meta["BATCH"]);sweeps=int(meta["SWEEPS"]);a=np.asarray(args["A"],np.float32).reshape(B,4,4);cols=np.transpose(a,(0,2,1)).copy();v=np.tile(np.eye(4,dtype=np.float32),(B,1,1));pairs=((0,1),(0,2),(0,3),(1,2),(1,3),(2,3))
 for _ in range(sweeps):
  for p,q in pairs:
   for b in range(B):
    ap=cols[b,p].copy();aq=cols[b,q].copy();alpha=np.sum(ap*ap,dtype=np.float32);beta=np.sum(aq*aq,dtype=np.float32);gamma=np.sum(ap*aq,dtype=np.float32);active=abs(gamma)>1e-7*np.sqrt(alpha*beta+1e-20)
    if active:tau=(beta-alpha)/(2*gamma);t=(1 if tau>=0 else -1)/(abs(tau)+np.sqrt(1+tau*tau));c=np.float32(1/np.sqrt(1+t*t));s=np.float32(t*c)
    else:c=np.float32(1);s=np.float32(0)
    vp=v[b,:,p].copy();vq=v[b,:,q].copy();cols[b,p]=c*ap-s*aq;cols[b,q]=s*ap+c*aq;v[b,:,p]=c*vp-s*vq;v[b,:,q]=s*vp+c*vq
 norms=np.sqrt(np.sum(cols*cols,axis=2,dtype=np.float32)).astype(np.float32);u=np.empty((B,4,4),np.float32);vo=np.empty_like(u);sv=np.empty((B,4),np.float32)
 for b in range(B):
  order=np.argsort(-norms[b],kind="stable")
  for rank,c in enumerate(order):sv[b,rank]=norms[b,c];u[b,:,rank]=cols[b,c]/max(norms[b,c],1e-20);vo[b,:,rank]=v[b,:,c]
 return {"U":u.reshape(-1),"S":sv.reshape(-1),"V":vo.reshape(-1)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 B=5;block=2;sweeps=8;x=rng.normal(0,.4,(B,4,4)).astype(np.float32);x[1,:,3]=x[1,:,2];args={"A":_aligned(x,"float32"),"U":_aligned(np.full(B*16,-7),"float32"),"S":_aligned(np.full(B*4,-7),"float32"),"V":_aligned(np.full(B*16,-7),"float32")};meta={"BATCH":B,"BLOCK_B":block,"SWEEPS":sweeps};grid=((B+block-1)//block,)
 outputs=('U', 'S', 'V');return _case(_small4_square_svd_kernel,grid,args,meta,('A',),outputs,ref(args,meta),shape,"torch.float32",seed,{"complete_launch_plan":True,"formula":'six-pair one-sided Jacobi sweeps for 4x4 matrices with stable descending column-norm ranking'})

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


# ------------------------------------------------------------------ ② 执行单元(case 驱动)
def run(shape=None, dtype=None, seed=None, to_array=None):
    """直接执行:make_case 构造输入 → kernel[grid] 启动 → 返回输出。

    to_array=None 时数组参数按 numpy 原样传给 launcher(自研编译器的 staging
    语义);传入数组转换器(如 numpy→torch.cuda)即可在真实 Triton 上执行。
    """
    import sys

    from case_utils import run_case

    return run_case(sys.modules[__name__], shape=shape, dtype=dtype,
                    seed=seed, to_array=to_array)


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float32'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float32': 'torch.float32'}


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
