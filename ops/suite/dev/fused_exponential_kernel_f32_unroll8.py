"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/fused_exponential_kernel_f32_unroll8", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["layout"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit(do_not_specialize=['philox_seed', 'philox_offset', 'N'])
def fused_exponential_kernel_f32_unroll8(out_ptr, N, inv_lambd, eps_minus, philox_seed, philox_offset, BLOCK: tl.constexpr):
    philox_seed = philox_seed.to(tl.int64)
    philox_offset = philox_offset.to(tl.int64)
    c0 = (philox_offset & 4294967295).to(tl.uint32)
    c1 = (philox_offset >> 32 & 4294967295).to(tl.uint32)
    pid = tl.program_id(0)
    block_start = pid * BLOCK * 2
    offsets = block_start + tl.arange(0, BLOCK)
    c0_first = c0 + offsets * 4
    c0_second = c0_first + BLOCK * 4
    z = c0_first * 0
    (r0_0, r1_0, r2_0, r3_0) = tl.philox(philox_seed, c0_first, c1, z, z)
    (r0_1, r1_1, r2_1, r3_1) = tl.philox(philox_seed, c0_second, c1, z, z)
    _inl_1_uint_to_uniform_float_x = r0_0
    '\n        Numerically stable function to convert a random uint into a random float uniformly sampled in [0, 1).\n        '
    if tl.constexpr(_inl_1_uint_to_uniform_float_x.dtype == tl.uint32) or tl.constexpr(_inl_1_uint_to_uniform_float_x.dtype == tl.int32):
        _inl_1_uint_to_uniform_float_x = _inl_1_uint_to_uniform_float_x.to(tl.int32, bitcast=True)
        _inl_1_uint_to_uniform_float_scale: tl.constexpr = 4.6566127342e-10
    else:
        _inl_1_uint_to_uniform_float_x = _inl_1_uint_to_uniform_float_x.to(tl.int64, bitcast=True)
        _inl_1_uint_to_uniform_float_scale: tl.constexpr = 1.0842020432385337e-19
    _inl_1_uint_to_uniform_float_x = tl.where(_inl_1_uint_to_uniform_float_x < 0, -_inl_1_uint_to_uniform_float_x - 1, _inl_1_uint_to_uniform_float_x)
    _inl_1_uint_to_uniform_float_result = _inl_1_uint_to_uniform_float_x * _inl_1_uint_to_uniform_float_scale
    _inl_2_transform_exponential_f32_fast_u = _inl_1_uint_to_uniform_float_result
    _inl_2_transform_exponential_f32_fast_inv_lambd = inv_lambd
    _inl_2_transform_exponential_f32_fast_eps_minus = eps_minus
    _inl_3_safe_fast_log_f32_x = _inl_2_transform_exponential_f32_fast_u
    _inl_3_safe_fast_log_f32_min_normal = (_inl_3_safe_fast_log_f32_x * 0.0 + tl.full((), 1.17549435e-38, tl.float32)).to(tl.float32)
    _inl_3_safe_fast_log_f32_max_u = _inl_3_safe_fast_log_f32_x * 0.0 + 0.99999994
    _inl_3_safe_fast_log_f32_x = tl.minimum(tl.maximum(_inl_3_safe_fast_log_f32_x, _inl_3_safe_fast_log_f32_min_normal), _inl_3_safe_fast_log_f32_max_u)
    _inl_3_safe_fast_log_f32_bits = _inl_3_safe_fast_log_f32_x.to(tl.int32, bitcast=True)
    _inl_3_safe_fast_log_f32_exponent = (_inl_3_safe_fast_log_f32_bits >> 23) - 127
    _inl_3_safe_fast_log_f32_mantissa = (_inl_3_safe_fast_log_f32_bits & 8388607).to(tl.float32) * (1.0 / 8388608.0) + 1.0
    _inl_3_safe_fast_log_f32_m1 = _inl_3_safe_fast_log_f32_mantissa - 1.0
    _inl_3_safe_fast_log_f32_result = tl.log(_inl_3_safe_fast_log_f32_x)
    _inl_2_transform_exponential_f32_fast_log = tl.where(_inl_2_transform_exponential_f32_fast_u >= 1.0 + _inl_2_transform_exponential_f32_fast_eps_minus, _inl_2_transform_exponential_f32_fast_eps_minus, _inl_3_safe_fast_log_f32_result)
    _inl_2_transform_exponential_f32_fast_result = -_inl_2_transform_exponential_f32_fast_inv_lambd * _inl_2_transform_exponential_f32_fast_log
    y0_0 = _inl_2_transform_exponential_f32_fast_result
    _inl_4_uint_to_uniform_float_x = r1_0
    '\n        Numerically stable function to convert a random uint into a random float uniformly sampled in [0, 1).\n        '
    if tl.constexpr(_inl_4_uint_to_uniform_float_x.dtype == tl.uint32) or tl.constexpr(_inl_4_uint_to_uniform_float_x.dtype == tl.int32):
        _inl_4_uint_to_uniform_float_x = _inl_4_uint_to_uniform_float_x.to(tl.int32, bitcast=True)
        _inl_4_uint_to_uniform_float_scale: tl.constexpr = 4.6566127342e-10
    else:
        _inl_4_uint_to_uniform_float_x = _inl_4_uint_to_uniform_float_x.to(tl.int64, bitcast=True)
        _inl_4_uint_to_uniform_float_scale: tl.constexpr = 1.0842020432385337e-19
    _inl_4_uint_to_uniform_float_x = tl.where(_inl_4_uint_to_uniform_float_x < 0, -_inl_4_uint_to_uniform_float_x - 1, _inl_4_uint_to_uniform_float_x)
    _inl_4_uint_to_uniform_float_result = _inl_4_uint_to_uniform_float_x * _inl_4_uint_to_uniform_float_scale
    _inl_5_transform_exponential_f32_fast_u = _inl_4_uint_to_uniform_float_result
    _inl_5_transform_exponential_f32_fast_inv_lambd = inv_lambd
    _inl_5_transform_exponential_f32_fast_eps_minus = eps_minus
    _inl_6_safe_fast_log_f32_x = _inl_5_transform_exponential_f32_fast_u
    _inl_6_safe_fast_log_f32_min_normal = (_inl_6_safe_fast_log_f32_x * 0.0 + tl.full((), 1.17549435e-38, tl.float32)).to(tl.float32)
    _inl_6_safe_fast_log_f32_max_u = _inl_6_safe_fast_log_f32_x * 0.0 + 0.99999994
    _inl_6_safe_fast_log_f32_x = tl.minimum(tl.maximum(_inl_6_safe_fast_log_f32_x, _inl_6_safe_fast_log_f32_min_normal), _inl_6_safe_fast_log_f32_max_u)
    _inl_6_safe_fast_log_f32_bits = _inl_6_safe_fast_log_f32_x.to(tl.int32, bitcast=True)
    _inl_6_safe_fast_log_f32_exponent = (_inl_6_safe_fast_log_f32_bits >> 23) - 127
    _inl_6_safe_fast_log_f32_mantissa = (_inl_6_safe_fast_log_f32_bits & 8388607).to(tl.float32) * (1.0 / 8388608.0) + 1.0
    _inl_6_safe_fast_log_f32_m1 = _inl_6_safe_fast_log_f32_mantissa - 1.0
    _inl_6_safe_fast_log_f32_result = tl.log(_inl_6_safe_fast_log_f32_x)
    _inl_5_transform_exponential_f32_fast_log = tl.where(_inl_5_transform_exponential_f32_fast_u >= 1.0 + _inl_5_transform_exponential_f32_fast_eps_minus, _inl_5_transform_exponential_f32_fast_eps_minus, _inl_6_safe_fast_log_f32_result)
    _inl_5_transform_exponential_f32_fast_result = -_inl_5_transform_exponential_f32_fast_inv_lambd * _inl_5_transform_exponential_f32_fast_log
    y1_0 = _inl_5_transform_exponential_f32_fast_result
    _inl_7_uint_to_uniform_float_x = r2_0
    '\n        Numerically stable function to convert a random uint into a random float uniformly sampled in [0, 1).\n        '
    if tl.constexpr(_inl_7_uint_to_uniform_float_x.dtype == tl.uint32) or tl.constexpr(_inl_7_uint_to_uniform_float_x.dtype == tl.int32):
        _inl_7_uint_to_uniform_float_x = _inl_7_uint_to_uniform_float_x.to(tl.int32, bitcast=True)
        _inl_7_uint_to_uniform_float_scale: tl.constexpr = 4.6566127342e-10
    else:
        _inl_7_uint_to_uniform_float_x = _inl_7_uint_to_uniform_float_x.to(tl.int64, bitcast=True)
        _inl_7_uint_to_uniform_float_scale: tl.constexpr = 1.0842020432385337e-19
    _inl_7_uint_to_uniform_float_x = tl.where(_inl_7_uint_to_uniform_float_x < 0, -_inl_7_uint_to_uniform_float_x - 1, _inl_7_uint_to_uniform_float_x)
    _inl_7_uint_to_uniform_float_result = _inl_7_uint_to_uniform_float_x * _inl_7_uint_to_uniform_float_scale
    _inl_8_transform_exponential_f32_fast_u = _inl_7_uint_to_uniform_float_result
    _inl_8_transform_exponential_f32_fast_inv_lambd = inv_lambd
    _inl_8_transform_exponential_f32_fast_eps_minus = eps_minus
    _inl_9_safe_fast_log_f32_x = _inl_8_transform_exponential_f32_fast_u
    _inl_9_safe_fast_log_f32_min_normal = (_inl_9_safe_fast_log_f32_x * 0.0 + tl.full((), 1.17549435e-38, tl.float32)).to(tl.float32)
    _inl_9_safe_fast_log_f32_max_u = _inl_9_safe_fast_log_f32_x * 0.0 + 0.99999994
    _inl_9_safe_fast_log_f32_x = tl.minimum(tl.maximum(_inl_9_safe_fast_log_f32_x, _inl_9_safe_fast_log_f32_min_normal), _inl_9_safe_fast_log_f32_max_u)
    _inl_9_safe_fast_log_f32_bits = _inl_9_safe_fast_log_f32_x.to(tl.int32, bitcast=True)
    _inl_9_safe_fast_log_f32_exponent = (_inl_9_safe_fast_log_f32_bits >> 23) - 127
    _inl_9_safe_fast_log_f32_mantissa = (_inl_9_safe_fast_log_f32_bits & 8388607).to(tl.float32) * (1.0 / 8388608.0) + 1.0
    _inl_9_safe_fast_log_f32_m1 = _inl_9_safe_fast_log_f32_mantissa - 1.0
    _inl_9_safe_fast_log_f32_result = tl.log(_inl_9_safe_fast_log_f32_x)
    _inl_8_transform_exponential_f32_fast_log = tl.where(_inl_8_transform_exponential_f32_fast_u >= 1.0 + _inl_8_transform_exponential_f32_fast_eps_minus, _inl_8_transform_exponential_f32_fast_eps_minus, _inl_9_safe_fast_log_f32_result)
    _inl_8_transform_exponential_f32_fast_result = -_inl_8_transform_exponential_f32_fast_inv_lambd * _inl_8_transform_exponential_f32_fast_log
    y2_0 = _inl_8_transform_exponential_f32_fast_result
    _inl_10_uint_to_uniform_float_x = r3_0
    '\n        Numerically stable function to convert a random uint into a random float uniformly sampled in [0, 1).\n        '
    if tl.constexpr(_inl_10_uint_to_uniform_float_x.dtype == tl.uint32) or tl.constexpr(_inl_10_uint_to_uniform_float_x.dtype == tl.int32):
        _inl_10_uint_to_uniform_float_x = _inl_10_uint_to_uniform_float_x.to(tl.int32, bitcast=True)
        _inl_10_uint_to_uniform_float_scale: tl.constexpr = 4.6566127342e-10
    else:
        _inl_10_uint_to_uniform_float_x = _inl_10_uint_to_uniform_float_x.to(tl.int64, bitcast=True)
        _inl_10_uint_to_uniform_float_scale: tl.constexpr = 1.0842020432385337e-19
    _inl_10_uint_to_uniform_float_x = tl.where(_inl_10_uint_to_uniform_float_x < 0, -_inl_10_uint_to_uniform_float_x - 1, _inl_10_uint_to_uniform_float_x)
    _inl_10_uint_to_uniform_float_result = _inl_10_uint_to_uniform_float_x * _inl_10_uint_to_uniform_float_scale
    _inl_11_transform_exponential_f32_fast_u = _inl_10_uint_to_uniform_float_result
    _inl_11_transform_exponential_f32_fast_inv_lambd = inv_lambd
    _inl_11_transform_exponential_f32_fast_eps_minus = eps_minus
    _inl_12_safe_fast_log_f32_x = _inl_11_transform_exponential_f32_fast_u
    _inl_12_safe_fast_log_f32_min_normal = (_inl_12_safe_fast_log_f32_x * 0.0 + tl.full((), 1.17549435e-38, tl.float32)).to(tl.float32)
    _inl_12_safe_fast_log_f32_max_u = _inl_12_safe_fast_log_f32_x * 0.0 + 0.99999994
    _inl_12_safe_fast_log_f32_x = tl.minimum(tl.maximum(_inl_12_safe_fast_log_f32_x, _inl_12_safe_fast_log_f32_min_normal), _inl_12_safe_fast_log_f32_max_u)
    _inl_12_safe_fast_log_f32_bits = _inl_12_safe_fast_log_f32_x.to(tl.int32, bitcast=True)
    _inl_12_safe_fast_log_f32_exponent = (_inl_12_safe_fast_log_f32_bits >> 23) - 127
    _inl_12_safe_fast_log_f32_mantissa = (_inl_12_safe_fast_log_f32_bits & 8388607).to(tl.float32) * (1.0 / 8388608.0) + 1.0
    _inl_12_safe_fast_log_f32_m1 = _inl_12_safe_fast_log_f32_mantissa - 1.0
    _inl_12_safe_fast_log_f32_result = tl.log(_inl_12_safe_fast_log_f32_x)
    _inl_11_transform_exponential_f32_fast_log = tl.where(_inl_11_transform_exponential_f32_fast_u >= 1.0 + _inl_11_transform_exponential_f32_fast_eps_minus, _inl_11_transform_exponential_f32_fast_eps_minus, _inl_12_safe_fast_log_f32_result)
    _inl_11_transform_exponential_f32_fast_result = -_inl_11_transform_exponential_f32_fast_inv_lambd * _inl_11_transform_exponential_f32_fast_log
    y3_0 = _inl_11_transform_exponential_f32_fast_result
    _inl_13_uint_to_uniform_float_x = r0_1
    '\n        Numerically stable function to convert a random uint into a random float uniformly sampled in [0, 1).\n        '
    if tl.constexpr(_inl_13_uint_to_uniform_float_x.dtype == tl.uint32) or tl.constexpr(_inl_13_uint_to_uniform_float_x.dtype == tl.int32):
        _inl_13_uint_to_uniform_float_x = _inl_13_uint_to_uniform_float_x.to(tl.int32, bitcast=True)
        _inl_13_uint_to_uniform_float_scale: tl.constexpr = 4.6566127342e-10
    else:
        _inl_13_uint_to_uniform_float_x = _inl_13_uint_to_uniform_float_x.to(tl.int64, bitcast=True)
        _inl_13_uint_to_uniform_float_scale: tl.constexpr = 1.0842020432385337e-19
    _inl_13_uint_to_uniform_float_x = tl.where(_inl_13_uint_to_uniform_float_x < 0, -_inl_13_uint_to_uniform_float_x - 1, _inl_13_uint_to_uniform_float_x)
    _inl_13_uint_to_uniform_float_result = _inl_13_uint_to_uniform_float_x * _inl_13_uint_to_uniform_float_scale
    _inl_14_transform_exponential_f32_fast_u = _inl_13_uint_to_uniform_float_result
    _inl_14_transform_exponential_f32_fast_inv_lambd = inv_lambd
    _inl_14_transform_exponential_f32_fast_eps_minus = eps_minus
    _inl_15_safe_fast_log_f32_x = _inl_14_transform_exponential_f32_fast_u
    _inl_15_safe_fast_log_f32_min_normal = (_inl_15_safe_fast_log_f32_x * 0.0 + tl.full((), 1.17549435e-38, tl.float32)).to(tl.float32)
    _inl_15_safe_fast_log_f32_max_u = _inl_15_safe_fast_log_f32_x * 0.0 + 0.99999994
    _inl_15_safe_fast_log_f32_x = tl.minimum(tl.maximum(_inl_15_safe_fast_log_f32_x, _inl_15_safe_fast_log_f32_min_normal), _inl_15_safe_fast_log_f32_max_u)
    _inl_15_safe_fast_log_f32_bits = _inl_15_safe_fast_log_f32_x.to(tl.int32, bitcast=True)
    _inl_15_safe_fast_log_f32_exponent = (_inl_15_safe_fast_log_f32_bits >> 23) - 127
    _inl_15_safe_fast_log_f32_mantissa = (_inl_15_safe_fast_log_f32_bits & 8388607).to(tl.float32) * (1.0 / 8388608.0) + 1.0
    _inl_15_safe_fast_log_f32_m1 = _inl_15_safe_fast_log_f32_mantissa - 1.0
    _inl_15_safe_fast_log_f32_result = tl.log(_inl_15_safe_fast_log_f32_x)
    _inl_14_transform_exponential_f32_fast_log = tl.where(_inl_14_transform_exponential_f32_fast_u >= 1.0 + _inl_14_transform_exponential_f32_fast_eps_minus, _inl_14_transform_exponential_f32_fast_eps_minus, _inl_15_safe_fast_log_f32_result)
    _inl_14_transform_exponential_f32_fast_result = -_inl_14_transform_exponential_f32_fast_inv_lambd * _inl_14_transform_exponential_f32_fast_log
    y0_1 = _inl_14_transform_exponential_f32_fast_result
    _inl_16_uint_to_uniform_float_x = r1_1
    '\n        Numerically stable function to convert a random uint into a random float uniformly sampled in [0, 1).\n        '
    if tl.constexpr(_inl_16_uint_to_uniform_float_x.dtype == tl.uint32) or tl.constexpr(_inl_16_uint_to_uniform_float_x.dtype == tl.int32):
        _inl_16_uint_to_uniform_float_x = _inl_16_uint_to_uniform_float_x.to(tl.int32, bitcast=True)
        _inl_16_uint_to_uniform_float_scale: tl.constexpr = 4.6566127342e-10
    else:
        _inl_16_uint_to_uniform_float_x = _inl_16_uint_to_uniform_float_x.to(tl.int64, bitcast=True)
        _inl_16_uint_to_uniform_float_scale: tl.constexpr = 1.0842020432385337e-19
    _inl_16_uint_to_uniform_float_x = tl.where(_inl_16_uint_to_uniform_float_x < 0, -_inl_16_uint_to_uniform_float_x - 1, _inl_16_uint_to_uniform_float_x)
    _inl_16_uint_to_uniform_float_result = _inl_16_uint_to_uniform_float_x * _inl_16_uint_to_uniform_float_scale
    _inl_17_transform_exponential_f32_fast_u = _inl_16_uint_to_uniform_float_result
    _inl_17_transform_exponential_f32_fast_inv_lambd = inv_lambd
    _inl_17_transform_exponential_f32_fast_eps_minus = eps_minus
    _inl_18_safe_fast_log_f32_x = _inl_17_transform_exponential_f32_fast_u
    _inl_18_safe_fast_log_f32_min_normal = (_inl_18_safe_fast_log_f32_x * 0.0 + tl.full((), 1.17549435e-38, tl.float32)).to(tl.float32)
    _inl_18_safe_fast_log_f32_max_u = _inl_18_safe_fast_log_f32_x * 0.0 + 0.99999994
    _inl_18_safe_fast_log_f32_x = tl.minimum(tl.maximum(_inl_18_safe_fast_log_f32_x, _inl_18_safe_fast_log_f32_min_normal), _inl_18_safe_fast_log_f32_max_u)
    _inl_18_safe_fast_log_f32_bits = _inl_18_safe_fast_log_f32_x.to(tl.int32, bitcast=True)
    _inl_18_safe_fast_log_f32_exponent = (_inl_18_safe_fast_log_f32_bits >> 23) - 127
    _inl_18_safe_fast_log_f32_mantissa = (_inl_18_safe_fast_log_f32_bits & 8388607).to(tl.float32) * (1.0 / 8388608.0) + 1.0
    _inl_18_safe_fast_log_f32_m1 = _inl_18_safe_fast_log_f32_mantissa - 1.0
    _inl_18_safe_fast_log_f32_result = tl.log(_inl_18_safe_fast_log_f32_x)
    _inl_17_transform_exponential_f32_fast_log = tl.where(_inl_17_transform_exponential_f32_fast_u >= 1.0 + _inl_17_transform_exponential_f32_fast_eps_minus, _inl_17_transform_exponential_f32_fast_eps_minus, _inl_18_safe_fast_log_f32_result)
    _inl_17_transform_exponential_f32_fast_result = -_inl_17_transform_exponential_f32_fast_inv_lambd * _inl_17_transform_exponential_f32_fast_log
    y1_1 = _inl_17_transform_exponential_f32_fast_result
    _inl_19_uint_to_uniform_float_x = r2_1
    '\n        Numerically stable function to convert a random uint into a random float uniformly sampled in [0, 1).\n        '
    if tl.constexpr(_inl_19_uint_to_uniform_float_x.dtype == tl.uint32) or tl.constexpr(_inl_19_uint_to_uniform_float_x.dtype == tl.int32):
        _inl_19_uint_to_uniform_float_x = _inl_19_uint_to_uniform_float_x.to(tl.int32, bitcast=True)
        _inl_19_uint_to_uniform_float_scale: tl.constexpr = 4.6566127342e-10
    else:
        _inl_19_uint_to_uniform_float_x = _inl_19_uint_to_uniform_float_x.to(tl.int64, bitcast=True)
        _inl_19_uint_to_uniform_float_scale: tl.constexpr = 1.0842020432385337e-19
    _inl_19_uint_to_uniform_float_x = tl.where(_inl_19_uint_to_uniform_float_x < 0, -_inl_19_uint_to_uniform_float_x - 1, _inl_19_uint_to_uniform_float_x)
    _inl_19_uint_to_uniform_float_result = _inl_19_uint_to_uniform_float_x * _inl_19_uint_to_uniform_float_scale
    _inl_20_transform_exponential_f32_fast_u = _inl_19_uint_to_uniform_float_result
    _inl_20_transform_exponential_f32_fast_inv_lambd = inv_lambd
    _inl_20_transform_exponential_f32_fast_eps_minus = eps_minus
    _inl_21_safe_fast_log_f32_x = _inl_20_transform_exponential_f32_fast_u
    _inl_21_safe_fast_log_f32_min_normal = (_inl_21_safe_fast_log_f32_x * 0.0 + tl.full((), 1.17549435e-38, tl.float32)).to(tl.float32)
    _inl_21_safe_fast_log_f32_max_u = _inl_21_safe_fast_log_f32_x * 0.0 + 0.99999994
    _inl_21_safe_fast_log_f32_x = tl.minimum(tl.maximum(_inl_21_safe_fast_log_f32_x, _inl_21_safe_fast_log_f32_min_normal), _inl_21_safe_fast_log_f32_max_u)
    _inl_21_safe_fast_log_f32_bits = _inl_21_safe_fast_log_f32_x.to(tl.int32, bitcast=True)
    _inl_21_safe_fast_log_f32_exponent = (_inl_21_safe_fast_log_f32_bits >> 23) - 127
    _inl_21_safe_fast_log_f32_mantissa = (_inl_21_safe_fast_log_f32_bits & 8388607).to(tl.float32) * (1.0 / 8388608.0) + 1.0
    _inl_21_safe_fast_log_f32_m1 = _inl_21_safe_fast_log_f32_mantissa - 1.0
    _inl_21_safe_fast_log_f32_result = tl.log(_inl_21_safe_fast_log_f32_x)
    _inl_20_transform_exponential_f32_fast_log = tl.where(_inl_20_transform_exponential_f32_fast_u >= 1.0 + _inl_20_transform_exponential_f32_fast_eps_minus, _inl_20_transform_exponential_f32_fast_eps_minus, _inl_21_safe_fast_log_f32_result)
    _inl_20_transform_exponential_f32_fast_result = -_inl_20_transform_exponential_f32_fast_inv_lambd * _inl_20_transform_exponential_f32_fast_log
    y2_1 = _inl_20_transform_exponential_f32_fast_result
    _inl_22_uint_to_uniform_float_x = r3_1
    '\n        Numerically stable function to convert a random uint into a random float uniformly sampled in [0, 1).\n        '
    if tl.constexpr(_inl_22_uint_to_uniform_float_x.dtype == tl.uint32) or tl.constexpr(_inl_22_uint_to_uniform_float_x.dtype == tl.int32):
        _inl_22_uint_to_uniform_float_x = _inl_22_uint_to_uniform_float_x.to(tl.int32, bitcast=True)
        _inl_22_uint_to_uniform_float_scale: tl.constexpr = 4.6566127342e-10
    else:
        _inl_22_uint_to_uniform_float_x = _inl_22_uint_to_uniform_float_x.to(tl.int64, bitcast=True)
        _inl_22_uint_to_uniform_float_scale: tl.constexpr = 1.0842020432385337e-19
    _inl_22_uint_to_uniform_float_x = tl.where(_inl_22_uint_to_uniform_float_x < 0, -_inl_22_uint_to_uniform_float_x - 1, _inl_22_uint_to_uniform_float_x)
    _inl_22_uint_to_uniform_float_result = _inl_22_uint_to_uniform_float_x * _inl_22_uint_to_uniform_float_scale
    _inl_23_transform_exponential_f32_fast_u = _inl_22_uint_to_uniform_float_result
    _inl_23_transform_exponential_f32_fast_inv_lambd = inv_lambd
    _inl_23_transform_exponential_f32_fast_eps_minus = eps_minus
    _inl_24_safe_fast_log_f32_x = _inl_23_transform_exponential_f32_fast_u
    _inl_24_safe_fast_log_f32_min_normal = (_inl_24_safe_fast_log_f32_x * 0.0 + tl.full((), 1.17549435e-38, tl.float32)).to(tl.float32)
    _inl_24_safe_fast_log_f32_max_u = _inl_24_safe_fast_log_f32_x * 0.0 + 0.99999994
    _inl_24_safe_fast_log_f32_x = tl.minimum(tl.maximum(_inl_24_safe_fast_log_f32_x, _inl_24_safe_fast_log_f32_min_normal), _inl_24_safe_fast_log_f32_max_u)
    _inl_24_safe_fast_log_f32_bits = _inl_24_safe_fast_log_f32_x.to(tl.int32, bitcast=True)
    _inl_24_safe_fast_log_f32_exponent = (_inl_24_safe_fast_log_f32_bits >> 23) - 127
    _inl_24_safe_fast_log_f32_mantissa = (_inl_24_safe_fast_log_f32_bits & 8388607).to(tl.float32) * (1.0 / 8388608.0) + 1.0
    _inl_24_safe_fast_log_f32_m1 = _inl_24_safe_fast_log_f32_mantissa - 1.0
    _inl_24_safe_fast_log_f32_result = tl.log(_inl_24_safe_fast_log_f32_x)
    _inl_23_transform_exponential_f32_fast_log = tl.where(_inl_23_transform_exponential_f32_fast_u >= 1.0 + _inl_23_transform_exponential_f32_fast_eps_minus, _inl_23_transform_exponential_f32_fast_eps_minus, _inl_24_safe_fast_log_f32_result)
    _inl_23_transform_exponential_f32_fast_result = -_inl_23_transform_exponential_f32_fast_inv_lambd * _inl_23_transform_exponential_f32_fast_log
    y3_1 = _inl_23_transform_exponential_f32_fast_result
    base_off = pid.to(tl.uint64) * BLOCK * 8
    off0 = base_off + tl.arange(0, BLOCK)
    off1 = off0 + BLOCK
    off2 = off1 + BLOCK
    off3 = off2 + BLOCK
    off4 = off3 + BLOCK
    off5 = off4 + BLOCK
    off6 = off5 + BLOCK
    off7 = off6 + BLOCK
    tl.store(out_ptr + off0, y0_0, mask=off0 < N)
    tl.store(out_ptr + off1, y1_0, mask=off1 < N)
    tl.store(out_ptr + off2, y2_0, mask=off2 < N)
    tl.store(out_ptr + off3, y3_0, mask=off3 < N)
    tl.store(out_ptr + off4, y0_1, mask=off4 < N)
    tl.store(out_ptr + off5, y1_1, mask=off5 < N)
    tl.store(out_ptr + off6, y2_1, mask=off6 < N)
    tl.store(out_ptr + off7, y3_1, mask=off7 < N)
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
SHAPES=((17,), (97,));DTYPES=('float32', 'float16', 'bfloat16')
def ref(args,meta):
 import numpy as np
 def _philox(c0,seed,offset):
  mask=np.uint64(0xffffffff);c0=(np.asarray(c0,dtype=np.uint64)+np.uint64(offset&0xffffffff))&mask;c1=np.full(c0.shape,(offset>>32)&0xffffffff,np.uint64);c2=np.zeros_like(c0);c3=np.zeros_like(c0);k0=np.uint64(seed&0xffffffff);k1=np.uint64((seed>>32)&0xffffffff)
  for _ in range(10):
   p0=np.uint64(0xD2511F53)*c0;p1=np.uint64(0xCD9E8D57)*c2;hi0=p0>>np.uint64(32);lo0=p0&mask;hi1=p1>>np.uint64(32);lo1=p1&mask;c0,c1,c2,c3=(hi1^c1^k0)&mask,lo1,(hi0^c3^k1)&mask,lo0;k0=(k0+np.uint64(0x9E3779B9))&mask;k1=(k1+np.uint64(0xBB67AE85))&mask
  return tuple(v.astype(np.uint32) for v in (c0,c1,c2,c3))
 def _to_uniform(raw):
  signed=raw.view(np.int32).astype(np.int64);return (np.where(signed<0,-signed-1,signed).astype(np.float32)*np.float32(4.6566127342e-10)).astype(np.float32)
 def _random_words(n,seed,offset,block):
  out=np.empty(n,np.uint32)
  for pid in range((n+8*block-1)//(8*block)):
   for half in range(2):
    counters=(pid*2*block+half*block+np.arange(block))*4
    words=_philox(counters,seed,offset)
    for q in range(4):
     idx=pid*8*block+(half*4+q)*block+np.arange(block); valid=idx<n;out[idx[valid]]=words[q][valid]
  return out
 def _uniform(n,seed,offset,block):return _to_uniform(_random_words(n,seed,offset,block))
 def _normal(n,seed,offset,block):
  out=np.empty(n,np.float32);programs=(n+4*block-1)//(4*block)
  for pid in range(programs):
   raw=_philox(pid*block+np.arange(block),seed,offset);u=[_to_uniform(v) for v in raw];r0=np.sqrt(-2*np.log(np.maximum(u[0],1e-7)));t0=2*np.pi*u[1];r1=np.sqrt(-2*np.log(np.maximum(u[2],1e-7)));t1=2*np.pi*u[3];vals=(r0*np.cos(t0),r0*np.sin(t0),r1*np.cos(t1),r1*np.sin(t1));base=pid*4*block
   for q in range(4):
    idx=base+q*block+np.arange(block);valid=idx<n;out[idx[valid]]=vals[q][valid]
  return out
 u=_uniform(int(args["N"]),int(args["philox_seed"]),int(args["philox_offset"]),meta["BLOCK"]).astype(np.float64);u=np.clip(u,np.finfo(np.float32).tiny,1+np.float64(args["eps_minus"]));return {"out_ptr":(-np.float64(args["inv_lambd"])*np.log(u)).astype(args["out_ptr"].dtype)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 B=64;args={"out_ptr":_aligned(np.full(N,-7.),"float32"),"N":N,"philox_seed":0x123456789ABCDEF,"philox_offset":37,"inv_lambd":.8,"eps_minus":-5.960464477539063e-8};meta={"BLOCK":B};grid=((N+8*B-1)//(8*B),)
 outputs=('out_ptr',);return _case(fused_exponential_kernel_f32_unroll8,grid,args,meta,(),outputs,ref(args,meta),shape,"torch.float32",seed,{"complete_launch_plan":True,"formula":'float32 exponential transform of Philox uniforms'})

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
