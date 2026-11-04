"""One-JIT standalone Triton compiler test case."""

COPIED_FROM = {'repo': 'ops-pool/flaggems', 'note': 'validated case layer intact; lottery 20261019'}
OPERATOR = {"name": "hidden/fht_kernel_256_4row_native", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def _fht_kernel_256_4row_native(X_ptr, OUT_ptr, stride_x_row, stride_out_row, N_ROWS, SCALE: tl.constexpr):
    """FHT for dim=256, 4-row ILP: four independent 1D butterflies per program."""
    pid = tl.program_id(0)
    col_offs = tl.arange(0, 256)
    row0 = pid * 4
    row1 = row0 + 1
    row2 = row0 + 2
    row3 = row0 + 3
    x0 = tl.load(X_ptr + row0 * stride_x_row + col_offs)
    x1 = tl.load(X_ptr + row1 * stride_x_row + col_offs, mask=row1 < N_ROWS, other=0.0)
    x2 = tl.load(X_ptr + row2 * stride_x_row + col_offs, mask=row2 < N_ROWS, other=0.0)
    x3 = tl.load(X_ptr + row3 * stride_x_row + col_offs, mask=row3 < N_ROWS, other=0.0)
    _inl_1_butterfly_stage_1d_x = x0
    pass
    pass
    _inl_1_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    pass
    if 128 == 1:
        _inl_1_butterfly_stage_1d_x2 = tl.reshape(_inl_1_butterfly_stage_1d_x, (256 // (2 * 128), 2))
        (_inl_1_butterfly_stage_1d_a, _inl_1_butterfly_stage_1d_b) = tl.split(_inl_1_butterfly_stage_1d_x2)
        _inl_1_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_1_butterfly_stage_1d_a + _inl_1_butterfly_stage_1d_b, _inl_1_butterfly_stage_1d_a - _inl_1_butterfly_stage_1d_b), (256,))
    else:
        _inl_1_butterfly_stage_1d_x3 = tl.reshape(_inl_1_butterfly_stage_1d_x, (256 // (2 * 128), 2, 128))
        _inl_1_butterfly_stage_1d_x3 = tl.permute(_inl_1_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_1_butterfly_stage_1d_a, _inl_1_butterfly_stage_1d_b) = tl.split(_inl_1_butterfly_stage_1d_x3)
        _inl_1_butterfly_stage_1d_x3 = tl.join(_inl_1_butterfly_stage_1d_a + _inl_1_butterfly_stage_1d_b, _inl_1_butterfly_stage_1d_a - _inl_1_butterfly_stage_1d_b)
        _inl_1_butterfly_stage_1d_x3 = tl.permute(_inl_1_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_1_butterfly_stage_1d_result = tl.reshape(_inl_1_butterfly_stage_1d_x3, (256,))
    x0 = _inl_1_butterfly_stage_1d_result
    _inl_2_butterfly_stage_1d_x = x1
    pass
    pass
    _inl_2_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    pass
    if 128 == 1:
        _inl_2_butterfly_stage_1d_x2 = tl.reshape(_inl_2_butterfly_stage_1d_x, (256 // (2 * 128), 2))
        (_inl_2_butterfly_stage_1d_a, _inl_2_butterfly_stage_1d_b) = tl.split(_inl_2_butterfly_stage_1d_x2)
        _inl_2_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_2_butterfly_stage_1d_a + _inl_2_butterfly_stage_1d_b, _inl_2_butterfly_stage_1d_a - _inl_2_butterfly_stage_1d_b), (256,))
    else:
        _inl_2_butterfly_stage_1d_x3 = tl.reshape(_inl_2_butterfly_stage_1d_x, (256 // (2 * 128), 2, 128))
        _inl_2_butterfly_stage_1d_x3 = tl.permute(_inl_2_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_2_butterfly_stage_1d_a, _inl_2_butterfly_stage_1d_b) = tl.split(_inl_2_butterfly_stage_1d_x3)
        _inl_2_butterfly_stage_1d_x3 = tl.join(_inl_2_butterfly_stage_1d_a + _inl_2_butterfly_stage_1d_b, _inl_2_butterfly_stage_1d_a - _inl_2_butterfly_stage_1d_b)
        _inl_2_butterfly_stage_1d_x3 = tl.permute(_inl_2_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_2_butterfly_stage_1d_result = tl.reshape(_inl_2_butterfly_stage_1d_x3, (256,))
    x1 = _inl_2_butterfly_stage_1d_result
    _inl_3_butterfly_stage_1d_x = x2
    _inl_3_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_3_butterfly_stage_1d_STRIDE: tl.constexpr = 128
    _inl_3_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_3_butterfly_stage_1d_GRP: tl.constexpr = _inl_3_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_3_butterfly_stage_1d_STRIDE)
    if _inl_3_butterfly_stage_1d_STRIDE == 1:
        _inl_3_butterfly_stage_1d_x2 = tl.reshape(_inl_3_butterfly_stage_1d_x, (_inl_3_butterfly_stage_1d_GRP, 2))
        (_inl_3_butterfly_stage_1d_a, _inl_3_butterfly_stage_1d_b) = tl.split(_inl_3_butterfly_stage_1d_x2)
        _inl_3_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_3_butterfly_stage_1d_a + _inl_3_butterfly_stage_1d_b, _inl_3_butterfly_stage_1d_a - _inl_3_butterfly_stage_1d_b), (_inl_3_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_3_butterfly_stage_1d_x3 = tl.reshape(_inl_3_butterfly_stage_1d_x, (_inl_3_butterfly_stage_1d_GRP, 2, _inl_3_butterfly_stage_1d_STRIDE))
        _inl_3_butterfly_stage_1d_x3 = tl.permute(_inl_3_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_3_butterfly_stage_1d_a, _inl_3_butterfly_stage_1d_b) = tl.split(_inl_3_butterfly_stage_1d_x3)
        _inl_3_butterfly_stage_1d_x3 = tl.join(_inl_3_butterfly_stage_1d_a + _inl_3_butterfly_stage_1d_b, _inl_3_butterfly_stage_1d_a - _inl_3_butterfly_stage_1d_b)
        _inl_3_butterfly_stage_1d_x3 = tl.permute(_inl_3_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_3_butterfly_stage_1d_result = tl.reshape(_inl_3_butterfly_stage_1d_x3, (_inl_3_butterfly_stage_1d_BLOCK_SIZE,))
    x2 = _inl_3_butterfly_stage_1d_result
    _inl_4_butterfly_stage_1d_x = x3
    _inl_4_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_4_butterfly_stage_1d_STRIDE: tl.constexpr = 128
    _inl_4_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_4_butterfly_stage_1d_GRP: tl.constexpr = _inl_4_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_4_butterfly_stage_1d_STRIDE)
    if _inl_4_butterfly_stage_1d_STRIDE == 1:
        _inl_4_butterfly_stage_1d_x2 = tl.reshape(_inl_4_butterfly_stage_1d_x, (_inl_4_butterfly_stage_1d_GRP, 2))
        (_inl_4_butterfly_stage_1d_a, _inl_4_butterfly_stage_1d_b) = tl.split(_inl_4_butterfly_stage_1d_x2)
        _inl_4_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_4_butterfly_stage_1d_a + _inl_4_butterfly_stage_1d_b, _inl_4_butterfly_stage_1d_a - _inl_4_butterfly_stage_1d_b), (_inl_4_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_4_butterfly_stage_1d_x3 = tl.reshape(_inl_4_butterfly_stage_1d_x, (_inl_4_butterfly_stage_1d_GRP, 2, _inl_4_butterfly_stage_1d_STRIDE))
        _inl_4_butterfly_stage_1d_x3 = tl.permute(_inl_4_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_4_butterfly_stage_1d_a, _inl_4_butterfly_stage_1d_b) = tl.split(_inl_4_butterfly_stage_1d_x3)
        _inl_4_butterfly_stage_1d_x3 = tl.join(_inl_4_butterfly_stage_1d_a + _inl_4_butterfly_stage_1d_b, _inl_4_butterfly_stage_1d_a - _inl_4_butterfly_stage_1d_b)
        _inl_4_butterfly_stage_1d_x3 = tl.permute(_inl_4_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_4_butterfly_stage_1d_result = tl.reshape(_inl_4_butterfly_stage_1d_x3, (_inl_4_butterfly_stage_1d_BLOCK_SIZE,))
    x3 = _inl_4_butterfly_stage_1d_result
    _inl_5_butterfly_stage_1d_x = x0
    _inl_5_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_5_butterfly_stage_1d_STRIDE: tl.constexpr = 64
    _inl_5_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_5_butterfly_stage_1d_GRP: tl.constexpr = _inl_5_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_5_butterfly_stage_1d_STRIDE)
    if _inl_5_butterfly_stage_1d_STRIDE == 1:
        _inl_5_butterfly_stage_1d_x2 = tl.reshape(_inl_5_butterfly_stage_1d_x, (_inl_5_butterfly_stage_1d_GRP, 2))
        (_inl_5_butterfly_stage_1d_a, _inl_5_butterfly_stage_1d_b) = tl.split(_inl_5_butterfly_stage_1d_x2)
        _inl_5_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_5_butterfly_stage_1d_a + _inl_5_butterfly_stage_1d_b, _inl_5_butterfly_stage_1d_a - _inl_5_butterfly_stage_1d_b), (_inl_5_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_5_butterfly_stage_1d_x3 = tl.reshape(_inl_5_butterfly_stage_1d_x, (_inl_5_butterfly_stage_1d_GRP, 2, _inl_5_butterfly_stage_1d_STRIDE))
        _inl_5_butterfly_stage_1d_x3 = tl.permute(_inl_5_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_5_butterfly_stage_1d_a, _inl_5_butterfly_stage_1d_b) = tl.split(_inl_5_butterfly_stage_1d_x3)
        _inl_5_butterfly_stage_1d_x3 = tl.join(_inl_5_butterfly_stage_1d_a + _inl_5_butterfly_stage_1d_b, _inl_5_butterfly_stage_1d_a - _inl_5_butterfly_stage_1d_b)
        _inl_5_butterfly_stage_1d_x3 = tl.permute(_inl_5_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_5_butterfly_stage_1d_result = tl.reshape(_inl_5_butterfly_stage_1d_x3, (_inl_5_butterfly_stage_1d_BLOCK_SIZE,))
    x0 = _inl_5_butterfly_stage_1d_result
    _inl_6_butterfly_stage_1d_x = x1
    _inl_6_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_6_butterfly_stage_1d_STRIDE: tl.constexpr = 64
    _inl_6_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_6_butterfly_stage_1d_GRP: tl.constexpr = _inl_6_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_6_butterfly_stage_1d_STRIDE)
    if _inl_6_butterfly_stage_1d_STRIDE == 1:
        _inl_6_butterfly_stage_1d_x2 = tl.reshape(_inl_6_butterfly_stage_1d_x, (_inl_6_butterfly_stage_1d_GRP, 2))
        (_inl_6_butterfly_stage_1d_a, _inl_6_butterfly_stage_1d_b) = tl.split(_inl_6_butterfly_stage_1d_x2)
        _inl_6_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_6_butterfly_stage_1d_a + _inl_6_butterfly_stage_1d_b, _inl_6_butterfly_stage_1d_a - _inl_6_butterfly_stage_1d_b), (_inl_6_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_6_butterfly_stage_1d_x3 = tl.reshape(_inl_6_butterfly_stage_1d_x, (_inl_6_butterfly_stage_1d_GRP, 2, _inl_6_butterfly_stage_1d_STRIDE))
        _inl_6_butterfly_stage_1d_x3 = tl.permute(_inl_6_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_6_butterfly_stage_1d_a, _inl_6_butterfly_stage_1d_b) = tl.split(_inl_6_butterfly_stage_1d_x3)
        _inl_6_butterfly_stage_1d_x3 = tl.join(_inl_6_butterfly_stage_1d_a + _inl_6_butterfly_stage_1d_b, _inl_6_butterfly_stage_1d_a - _inl_6_butterfly_stage_1d_b)
        _inl_6_butterfly_stage_1d_x3 = tl.permute(_inl_6_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_6_butterfly_stage_1d_result = tl.reshape(_inl_6_butterfly_stage_1d_x3, (_inl_6_butterfly_stage_1d_BLOCK_SIZE,))
    x1 = _inl_6_butterfly_stage_1d_result
    _inl_7_butterfly_stage_1d_x = x2
    _inl_7_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_7_butterfly_stage_1d_STRIDE: tl.constexpr = 64
    _inl_7_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_7_butterfly_stage_1d_GRP: tl.constexpr = _inl_7_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_7_butterfly_stage_1d_STRIDE)
    if _inl_7_butterfly_stage_1d_STRIDE == 1:
        _inl_7_butterfly_stage_1d_x2 = tl.reshape(_inl_7_butterfly_stage_1d_x, (_inl_7_butterfly_stage_1d_GRP, 2))
        (_inl_7_butterfly_stage_1d_a, _inl_7_butterfly_stage_1d_b) = tl.split(_inl_7_butterfly_stage_1d_x2)
        _inl_7_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_7_butterfly_stage_1d_a + _inl_7_butterfly_stage_1d_b, _inl_7_butterfly_stage_1d_a - _inl_7_butterfly_stage_1d_b), (_inl_7_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_7_butterfly_stage_1d_x3 = tl.reshape(_inl_7_butterfly_stage_1d_x, (_inl_7_butterfly_stage_1d_GRP, 2, _inl_7_butterfly_stage_1d_STRIDE))
        _inl_7_butterfly_stage_1d_x3 = tl.permute(_inl_7_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_7_butterfly_stage_1d_a, _inl_7_butterfly_stage_1d_b) = tl.split(_inl_7_butterfly_stage_1d_x3)
        _inl_7_butterfly_stage_1d_x3 = tl.join(_inl_7_butterfly_stage_1d_a + _inl_7_butterfly_stage_1d_b, _inl_7_butterfly_stage_1d_a - _inl_7_butterfly_stage_1d_b)
        _inl_7_butterfly_stage_1d_x3 = tl.permute(_inl_7_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_7_butterfly_stage_1d_result = tl.reshape(_inl_7_butterfly_stage_1d_x3, (_inl_7_butterfly_stage_1d_BLOCK_SIZE,))
    x2 = _inl_7_butterfly_stage_1d_result
    _inl_8_butterfly_stage_1d_x = x3
    _inl_8_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_8_butterfly_stage_1d_STRIDE: tl.constexpr = 64
    _inl_8_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_8_butterfly_stage_1d_GRP: tl.constexpr = _inl_8_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_8_butterfly_stage_1d_STRIDE)
    if _inl_8_butterfly_stage_1d_STRIDE == 1:
        _inl_8_butterfly_stage_1d_x2 = tl.reshape(_inl_8_butterfly_stage_1d_x, (_inl_8_butterfly_stage_1d_GRP, 2))
        (_inl_8_butterfly_stage_1d_a, _inl_8_butterfly_stage_1d_b) = tl.split(_inl_8_butterfly_stage_1d_x2)
        _inl_8_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_8_butterfly_stage_1d_a + _inl_8_butterfly_stage_1d_b, _inl_8_butterfly_stage_1d_a - _inl_8_butterfly_stage_1d_b), (_inl_8_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_8_butterfly_stage_1d_x3 = tl.reshape(_inl_8_butterfly_stage_1d_x, (_inl_8_butterfly_stage_1d_GRP, 2, _inl_8_butterfly_stage_1d_STRIDE))
        _inl_8_butterfly_stage_1d_x3 = tl.permute(_inl_8_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_8_butterfly_stage_1d_a, _inl_8_butterfly_stage_1d_b) = tl.split(_inl_8_butterfly_stage_1d_x3)
        _inl_8_butterfly_stage_1d_x3 = tl.join(_inl_8_butterfly_stage_1d_a + _inl_8_butterfly_stage_1d_b, _inl_8_butterfly_stage_1d_a - _inl_8_butterfly_stage_1d_b)
        _inl_8_butterfly_stage_1d_x3 = tl.permute(_inl_8_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_8_butterfly_stage_1d_result = tl.reshape(_inl_8_butterfly_stage_1d_x3, (_inl_8_butterfly_stage_1d_BLOCK_SIZE,))
    x3 = _inl_8_butterfly_stage_1d_result
    _inl_9_butterfly_stage_1d_x = x0
    _inl_9_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_9_butterfly_stage_1d_STRIDE: tl.constexpr = 32
    _inl_9_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_9_butterfly_stage_1d_GRP: tl.constexpr = _inl_9_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_9_butterfly_stage_1d_STRIDE)
    if _inl_9_butterfly_stage_1d_STRIDE == 1:
        _inl_9_butterfly_stage_1d_x2 = tl.reshape(_inl_9_butterfly_stage_1d_x, (_inl_9_butterfly_stage_1d_GRP, 2))
        (_inl_9_butterfly_stage_1d_a, _inl_9_butterfly_stage_1d_b) = tl.split(_inl_9_butterfly_stage_1d_x2)
        _inl_9_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_9_butterfly_stage_1d_a + _inl_9_butterfly_stage_1d_b, _inl_9_butterfly_stage_1d_a - _inl_9_butterfly_stage_1d_b), (_inl_9_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_9_butterfly_stage_1d_x3 = tl.reshape(_inl_9_butterfly_stage_1d_x, (_inl_9_butterfly_stage_1d_GRP, 2, _inl_9_butterfly_stage_1d_STRIDE))
        _inl_9_butterfly_stage_1d_x3 = tl.permute(_inl_9_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_9_butterfly_stage_1d_a, _inl_9_butterfly_stage_1d_b) = tl.split(_inl_9_butterfly_stage_1d_x3)
        _inl_9_butterfly_stage_1d_x3 = tl.join(_inl_9_butterfly_stage_1d_a + _inl_9_butterfly_stage_1d_b, _inl_9_butterfly_stage_1d_a - _inl_9_butterfly_stage_1d_b)
        _inl_9_butterfly_stage_1d_x3 = tl.permute(_inl_9_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_9_butterfly_stage_1d_result = tl.reshape(_inl_9_butterfly_stage_1d_x3, (_inl_9_butterfly_stage_1d_BLOCK_SIZE,))
    x0 = _inl_9_butterfly_stage_1d_result
    _inl_10_butterfly_stage_1d_x = x1
    _inl_10_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_10_butterfly_stage_1d_STRIDE: tl.constexpr = 32
    _inl_10_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_10_butterfly_stage_1d_GRP: tl.constexpr = _inl_10_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_10_butterfly_stage_1d_STRIDE)
    if _inl_10_butterfly_stage_1d_STRIDE == 1:
        _inl_10_butterfly_stage_1d_x2 = tl.reshape(_inl_10_butterfly_stage_1d_x, (_inl_10_butterfly_stage_1d_GRP, 2))
        (_inl_10_butterfly_stage_1d_a, _inl_10_butterfly_stage_1d_b) = tl.split(_inl_10_butterfly_stage_1d_x2)
        _inl_10_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_10_butterfly_stage_1d_a + _inl_10_butterfly_stage_1d_b, _inl_10_butterfly_stage_1d_a - _inl_10_butterfly_stage_1d_b), (_inl_10_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_10_butterfly_stage_1d_x3 = tl.reshape(_inl_10_butterfly_stage_1d_x, (_inl_10_butterfly_stage_1d_GRP, 2, _inl_10_butterfly_stage_1d_STRIDE))
        _inl_10_butterfly_stage_1d_x3 = tl.permute(_inl_10_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_10_butterfly_stage_1d_a, _inl_10_butterfly_stage_1d_b) = tl.split(_inl_10_butterfly_stage_1d_x3)
        _inl_10_butterfly_stage_1d_x3 = tl.join(_inl_10_butterfly_stage_1d_a + _inl_10_butterfly_stage_1d_b, _inl_10_butterfly_stage_1d_a - _inl_10_butterfly_stage_1d_b)
        _inl_10_butterfly_stage_1d_x3 = tl.permute(_inl_10_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_10_butterfly_stage_1d_result = tl.reshape(_inl_10_butterfly_stage_1d_x3, (_inl_10_butterfly_stage_1d_BLOCK_SIZE,))
    x1 = _inl_10_butterfly_stage_1d_result
    _inl_11_butterfly_stage_1d_x = x2
    _inl_11_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_11_butterfly_stage_1d_STRIDE: tl.constexpr = 32
    _inl_11_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_11_butterfly_stage_1d_GRP: tl.constexpr = _inl_11_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_11_butterfly_stage_1d_STRIDE)
    if _inl_11_butterfly_stage_1d_STRIDE == 1:
        _inl_11_butterfly_stage_1d_x2 = tl.reshape(_inl_11_butterfly_stage_1d_x, (_inl_11_butterfly_stage_1d_GRP, 2))
        (_inl_11_butterfly_stage_1d_a, _inl_11_butterfly_stage_1d_b) = tl.split(_inl_11_butterfly_stage_1d_x2)
        _inl_11_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_11_butterfly_stage_1d_a + _inl_11_butterfly_stage_1d_b, _inl_11_butterfly_stage_1d_a - _inl_11_butterfly_stage_1d_b), (_inl_11_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_11_butterfly_stage_1d_x3 = tl.reshape(_inl_11_butterfly_stage_1d_x, (_inl_11_butterfly_stage_1d_GRP, 2, _inl_11_butterfly_stage_1d_STRIDE))
        _inl_11_butterfly_stage_1d_x3 = tl.permute(_inl_11_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_11_butterfly_stage_1d_a, _inl_11_butterfly_stage_1d_b) = tl.split(_inl_11_butterfly_stage_1d_x3)
        _inl_11_butterfly_stage_1d_x3 = tl.join(_inl_11_butterfly_stage_1d_a + _inl_11_butterfly_stage_1d_b, _inl_11_butterfly_stage_1d_a - _inl_11_butterfly_stage_1d_b)
        _inl_11_butterfly_stage_1d_x3 = tl.permute(_inl_11_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_11_butterfly_stage_1d_result = tl.reshape(_inl_11_butterfly_stage_1d_x3, (_inl_11_butterfly_stage_1d_BLOCK_SIZE,))
    x2 = _inl_11_butterfly_stage_1d_result
    _inl_12_butterfly_stage_1d_x = x3
    _inl_12_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_12_butterfly_stage_1d_STRIDE: tl.constexpr = 32
    _inl_12_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_12_butterfly_stage_1d_GRP: tl.constexpr = _inl_12_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_12_butterfly_stage_1d_STRIDE)
    if _inl_12_butterfly_stage_1d_STRIDE == 1:
        _inl_12_butterfly_stage_1d_x2 = tl.reshape(_inl_12_butterfly_stage_1d_x, (_inl_12_butterfly_stage_1d_GRP, 2))
        (_inl_12_butterfly_stage_1d_a, _inl_12_butterfly_stage_1d_b) = tl.split(_inl_12_butterfly_stage_1d_x2)
        _inl_12_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_12_butterfly_stage_1d_a + _inl_12_butterfly_stage_1d_b, _inl_12_butterfly_stage_1d_a - _inl_12_butterfly_stage_1d_b), (_inl_12_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_12_butterfly_stage_1d_x3 = tl.reshape(_inl_12_butterfly_stage_1d_x, (_inl_12_butterfly_stage_1d_GRP, 2, _inl_12_butterfly_stage_1d_STRIDE))
        _inl_12_butterfly_stage_1d_x3 = tl.permute(_inl_12_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_12_butterfly_stage_1d_a, _inl_12_butterfly_stage_1d_b) = tl.split(_inl_12_butterfly_stage_1d_x3)
        _inl_12_butterfly_stage_1d_x3 = tl.join(_inl_12_butterfly_stage_1d_a + _inl_12_butterfly_stage_1d_b, _inl_12_butterfly_stage_1d_a - _inl_12_butterfly_stage_1d_b)
        _inl_12_butterfly_stage_1d_x3 = tl.permute(_inl_12_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_12_butterfly_stage_1d_result = tl.reshape(_inl_12_butterfly_stage_1d_x3, (_inl_12_butterfly_stage_1d_BLOCK_SIZE,))
    x3 = _inl_12_butterfly_stage_1d_result
    _inl_13_butterfly_stage_1d_x = x0
    _inl_13_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_13_butterfly_stage_1d_STRIDE: tl.constexpr = 16
    _inl_13_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_13_butterfly_stage_1d_GRP: tl.constexpr = _inl_13_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_13_butterfly_stage_1d_STRIDE)
    if _inl_13_butterfly_stage_1d_STRIDE == 1:
        _inl_13_butterfly_stage_1d_x2 = tl.reshape(_inl_13_butterfly_stage_1d_x, (_inl_13_butterfly_stage_1d_GRP, 2))
        (_inl_13_butterfly_stage_1d_a, _inl_13_butterfly_stage_1d_b) = tl.split(_inl_13_butterfly_stage_1d_x2)
        _inl_13_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_13_butterfly_stage_1d_a + _inl_13_butterfly_stage_1d_b, _inl_13_butterfly_stage_1d_a - _inl_13_butterfly_stage_1d_b), (_inl_13_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_13_butterfly_stage_1d_x3 = tl.reshape(_inl_13_butterfly_stage_1d_x, (_inl_13_butterfly_stage_1d_GRP, 2, _inl_13_butterfly_stage_1d_STRIDE))
        _inl_13_butterfly_stage_1d_x3 = tl.permute(_inl_13_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_13_butterfly_stage_1d_a, _inl_13_butterfly_stage_1d_b) = tl.split(_inl_13_butterfly_stage_1d_x3)
        _inl_13_butterfly_stage_1d_x3 = tl.join(_inl_13_butterfly_stage_1d_a + _inl_13_butterfly_stage_1d_b, _inl_13_butterfly_stage_1d_a - _inl_13_butterfly_stage_1d_b)
        _inl_13_butterfly_stage_1d_x3 = tl.permute(_inl_13_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_13_butterfly_stage_1d_result = tl.reshape(_inl_13_butterfly_stage_1d_x3, (_inl_13_butterfly_stage_1d_BLOCK_SIZE,))
    x0 = _inl_13_butterfly_stage_1d_result
    _inl_14_butterfly_stage_1d_x = x1
    _inl_14_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_14_butterfly_stage_1d_STRIDE: tl.constexpr = 16
    _inl_14_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_14_butterfly_stage_1d_GRP: tl.constexpr = _inl_14_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_14_butterfly_stage_1d_STRIDE)
    if _inl_14_butterfly_stage_1d_STRIDE == 1:
        _inl_14_butterfly_stage_1d_x2 = tl.reshape(_inl_14_butterfly_stage_1d_x, (_inl_14_butterfly_stage_1d_GRP, 2))
        (_inl_14_butterfly_stage_1d_a, _inl_14_butterfly_stage_1d_b) = tl.split(_inl_14_butterfly_stage_1d_x2)
        _inl_14_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_14_butterfly_stage_1d_a + _inl_14_butterfly_stage_1d_b, _inl_14_butterfly_stage_1d_a - _inl_14_butterfly_stage_1d_b), (_inl_14_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_14_butterfly_stage_1d_x3 = tl.reshape(_inl_14_butterfly_stage_1d_x, (_inl_14_butterfly_stage_1d_GRP, 2, _inl_14_butterfly_stage_1d_STRIDE))
        _inl_14_butterfly_stage_1d_x3 = tl.permute(_inl_14_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_14_butterfly_stage_1d_a, _inl_14_butterfly_stage_1d_b) = tl.split(_inl_14_butterfly_stage_1d_x3)
        _inl_14_butterfly_stage_1d_x3 = tl.join(_inl_14_butterfly_stage_1d_a + _inl_14_butterfly_stage_1d_b, _inl_14_butterfly_stage_1d_a - _inl_14_butterfly_stage_1d_b)
        _inl_14_butterfly_stage_1d_x3 = tl.permute(_inl_14_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_14_butterfly_stage_1d_result = tl.reshape(_inl_14_butterfly_stage_1d_x3, (_inl_14_butterfly_stage_1d_BLOCK_SIZE,))
    x1 = _inl_14_butterfly_stage_1d_result
    _inl_15_butterfly_stage_1d_x = x2
    _inl_15_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_15_butterfly_stage_1d_STRIDE: tl.constexpr = 16
    _inl_15_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_15_butterfly_stage_1d_GRP: tl.constexpr = _inl_15_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_15_butterfly_stage_1d_STRIDE)
    if _inl_15_butterfly_stage_1d_STRIDE == 1:
        _inl_15_butterfly_stage_1d_x2 = tl.reshape(_inl_15_butterfly_stage_1d_x, (_inl_15_butterfly_stage_1d_GRP, 2))
        (_inl_15_butterfly_stage_1d_a, _inl_15_butterfly_stage_1d_b) = tl.split(_inl_15_butterfly_stage_1d_x2)
        _inl_15_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_15_butterfly_stage_1d_a + _inl_15_butterfly_stage_1d_b, _inl_15_butterfly_stage_1d_a - _inl_15_butterfly_stage_1d_b), (_inl_15_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_15_butterfly_stage_1d_x3 = tl.reshape(_inl_15_butterfly_stage_1d_x, (_inl_15_butterfly_stage_1d_GRP, 2, _inl_15_butterfly_stage_1d_STRIDE))
        _inl_15_butterfly_stage_1d_x3 = tl.permute(_inl_15_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_15_butterfly_stage_1d_a, _inl_15_butterfly_stage_1d_b) = tl.split(_inl_15_butterfly_stage_1d_x3)
        _inl_15_butterfly_stage_1d_x3 = tl.join(_inl_15_butterfly_stage_1d_a + _inl_15_butterfly_stage_1d_b, _inl_15_butterfly_stage_1d_a - _inl_15_butterfly_stage_1d_b)
        _inl_15_butterfly_stage_1d_x3 = tl.permute(_inl_15_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_15_butterfly_stage_1d_result = tl.reshape(_inl_15_butterfly_stage_1d_x3, (_inl_15_butterfly_stage_1d_BLOCK_SIZE,))
    x2 = _inl_15_butterfly_stage_1d_result
    _inl_16_butterfly_stage_1d_x = x3
    _inl_16_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_16_butterfly_stage_1d_STRIDE: tl.constexpr = 16
    _inl_16_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_16_butterfly_stage_1d_GRP: tl.constexpr = _inl_16_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_16_butterfly_stage_1d_STRIDE)
    if _inl_16_butterfly_stage_1d_STRIDE == 1:
        _inl_16_butterfly_stage_1d_x2 = tl.reshape(_inl_16_butterfly_stage_1d_x, (_inl_16_butterfly_stage_1d_GRP, 2))
        (_inl_16_butterfly_stage_1d_a, _inl_16_butterfly_stage_1d_b) = tl.split(_inl_16_butterfly_stage_1d_x2)
        _inl_16_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_16_butterfly_stage_1d_a + _inl_16_butterfly_stage_1d_b, _inl_16_butterfly_stage_1d_a - _inl_16_butterfly_stage_1d_b), (_inl_16_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_16_butterfly_stage_1d_x3 = tl.reshape(_inl_16_butterfly_stage_1d_x, (_inl_16_butterfly_stage_1d_GRP, 2, _inl_16_butterfly_stage_1d_STRIDE))
        _inl_16_butterfly_stage_1d_x3 = tl.permute(_inl_16_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_16_butterfly_stage_1d_a, _inl_16_butterfly_stage_1d_b) = tl.split(_inl_16_butterfly_stage_1d_x3)
        _inl_16_butterfly_stage_1d_x3 = tl.join(_inl_16_butterfly_stage_1d_a + _inl_16_butterfly_stage_1d_b, _inl_16_butterfly_stage_1d_a - _inl_16_butterfly_stage_1d_b)
        _inl_16_butterfly_stage_1d_x3 = tl.permute(_inl_16_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_16_butterfly_stage_1d_result = tl.reshape(_inl_16_butterfly_stage_1d_x3, (_inl_16_butterfly_stage_1d_BLOCK_SIZE,))
    x3 = _inl_16_butterfly_stage_1d_result
    _inl_17_butterfly_stage_1d_x = x0
    _inl_17_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_17_butterfly_stage_1d_STRIDE: tl.constexpr = 8
    _inl_17_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_17_butterfly_stage_1d_GRP: tl.constexpr = _inl_17_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_17_butterfly_stage_1d_STRIDE)
    if _inl_17_butterfly_stage_1d_STRIDE == 1:
        _inl_17_butterfly_stage_1d_x2 = tl.reshape(_inl_17_butterfly_stage_1d_x, (_inl_17_butterfly_stage_1d_GRP, 2))
        (_inl_17_butterfly_stage_1d_a, _inl_17_butterfly_stage_1d_b) = tl.split(_inl_17_butterfly_stage_1d_x2)
        _inl_17_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_17_butterfly_stage_1d_a + _inl_17_butterfly_stage_1d_b, _inl_17_butterfly_stage_1d_a - _inl_17_butterfly_stage_1d_b), (_inl_17_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_17_butterfly_stage_1d_x3 = tl.reshape(_inl_17_butterfly_stage_1d_x, (_inl_17_butterfly_stage_1d_GRP, 2, _inl_17_butterfly_stage_1d_STRIDE))
        _inl_17_butterfly_stage_1d_x3 = tl.permute(_inl_17_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_17_butterfly_stage_1d_a, _inl_17_butterfly_stage_1d_b) = tl.split(_inl_17_butterfly_stage_1d_x3)
        _inl_17_butterfly_stage_1d_x3 = tl.join(_inl_17_butterfly_stage_1d_a + _inl_17_butterfly_stage_1d_b, _inl_17_butterfly_stage_1d_a - _inl_17_butterfly_stage_1d_b)
        _inl_17_butterfly_stage_1d_x3 = tl.permute(_inl_17_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_17_butterfly_stage_1d_result = tl.reshape(_inl_17_butterfly_stage_1d_x3, (_inl_17_butterfly_stage_1d_BLOCK_SIZE,))
    x0 = _inl_17_butterfly_stage_1d_result
    _inl_18_butterfly_stage_1d_x = x1
    _inl_18_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_18_butterfly_stage_1d_STRIDE: tl.constexpr = 8
    _inl_18_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_18_butterfly_stage_1d_GRP: tl.constexpr = _inl_18_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_18_butterfly_stage_1d_STRIDE)
    if _inl_18_butterfly_stage_1d_STRIDE == 1:
        _inl_18_butterfly_stage_1d_x2 = tl.reshape(_inl_18_butterfly_stage_1d_x, (_inl_18_butterfly_stage_1d_GRP, 2))
        (_inl_18_butterfly_stage_1d_a, _inl_18_butterfly_stage_1d_b) = tl.split(_inl_18_butterfly_stage_1d_x2)
        _inl_18_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_18_butterfly_stage_1d_a + _inl_18_butterfly_stage_1d_b, _inl_18_butterfly_stage_1d_a - _inl_18_butterfly_stage_1d_b), (_inl_18_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_18_butterfly_stage_1d_x3 = tl.reshape(_inl_18_butterfly_stage_1d_x, (_inl_18_butterfly_stage_1d_GRP, 2, _inl_18_butterfly_stage_1d_STRIDE))
        _inl_18_butterfly_stage_1d_x3 = tl.permute(_inl_18_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_18_butterfly_stage_1d_a, _inl_18_butterfly_stage_1d_b) = tl.split(_inl_18_butterfly_stage_1d_x3)
        _inl_18_butterfly_stage_1d_x3 = tl.join(_inl_18_butterfly_stage_1d_a + _inl_18_butterfly_stage_1d_b, _inl_18_butterfly_stage_1d_a - _inl_18_butterfly_stage_1d_b)
        _inl_18_butterfly_stage_1d_x3 = tl.permute(_inl_18_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_18_butterfly_stage_1d_result = tl.reshape(_inl_18_butterfly_stage_1d_x3, (_inl_18_butterfly_stage_1d_BLOCK_SIZE,))
    x1 = _inl_18_butterfly_stage_1d_result
    _inl_19_butterfly_stage_1d_x = x2
    _inl_19_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_19_butterfly_stage_1d_STRIDE: tl.constexpr = 8
    _inl_19_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_19_butterfly_stage_1d_GRP: tl.constexpr = _inl_19_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_19_butterfly_stage_1d_STRIDE)
    if _inl_19_butterfly_stage_1d_STRIDE == 1:
        _inl_19_butterfly_stage_1d_x2 = tl.reshape(_inl_19_butterfly_stage_1d_x, (_inl_19_butterfly_stage_1d_GRP, 2))
        (_inl_19_butterfly_stage_1d_a, _inl_19_butterfly_stage_1d_b) = tl.split(_inl_19_butterfly_stage_1d_x2)
        _inl_19_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_19_butterfly_stage_1d_a + _inl_19_butterfly_stage_1d_b, _inl_19_butterfly_stage_1d_a - _inl_19_butterfly_stage_1d_b), (_inl_19_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_19_butterfly_stage_1d_x3 = tl.reshape(_inl_19_butterfly_stage_1d_x, (_inl_19_butterfly_stage_1d_GRP, 2, _inl_19_butterfly_stage_1d_STRIDE))
        _inl_19_butterfly_stage_1d_x3 = tl.permute(_inl_19_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_19_butterfly_stage_1d_a, _inl_19_butterfly_stage_1d_b) = tl.split(_inl_19_butterfly_stage_1d_x3)
        _inl_19_butterfly_stage_1d_x3 = tl.join(_inl_19_butterfly_stage_1d_a + _inl_19_butterfly_stage_1d_b, _inl_19_butterfly_stage_1d_a - _inl_19_butterfly_stage_1d_b)
        _inl_19_butterfly_stage_1d_x3 = tl.permute(_inl_19_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_19_butterfly_stage_1d_result = tl.reshape(_inl_19_butterfly_stage_1d_x3, (_inl_19_butterfly_stage_1d_BLOCK_SIZE,))
    x2 = _inl_19_butterfly_stage_1d_result
    _inl_20_butterfly_stage_1d_x = x3
    _inl_20_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_20_butterfly_stage_1d_STRIDE: tl.constexpr = 8
    _inl_20_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_20_butterfly_stage_1d_GRP: tl.constexpr = _inl_20_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_20_butterfly_stage_1d_STRIDE)
    if _inl_20_butterfly_stage_1d_STRIDE == 1:
        _inl_20_butterfly_stage_1d_x2 = tl.reshape(_inl_20_butterfly_stage_1d_x, (_inl_20_butterfly_stage_1d_GRP, 2))
        (_inl_20_butterfly_stage_1d_a, _inl_20_butterfly_stage_1d_b) = tl.split(_inl_20_butterfly_stage_1d_x2)
        _inl_20_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_20_butterfly_stage_1d_a + _inl_20_butterfly_stage_1d_b, _inl_20_butterfly_stage_1d_a - _inl_20_butterfly_stage_1d_b), (_inl_20_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_20_butterfly_stage_1d_x3 = tl.reshape(_inl_20_butterfly_stage_1d_x, (_inl_20_butterfly_stage_1d_GRP, 2, _inl_20_butterfly_stage_1d_STRIDE))
        _inl_20_butterfly_stage_1d_x3 = tl.permute(_inl_20_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_20_butterfly_stage_1d_a, _inl_20_butterfly_stage_1d_b) = tl.split(_inl_20_butterfly_stage_1d_x3)
        _inl_20_butterfly_stage_1d_x3 = tl.join(_inl_20_butterfly_stage_1d_a + _inl_20_butterfly_stage_1d_b, _inl_20_butterfly_stage_1d_a - _inl_20_butterfly_stage_1d_b)
        _inl_20_butterfly_stage_1d_x3 = tl.permute(_inl_20_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_20_butterfly_stage_1d_result = tl.reshape(_inl_20_butterfly_stage_1d_x3, (_inl_20_butterfly_stage_1d_BLOCK_SIZE,))
    x3 = _inl_20_butterfly_stage_1d_result
    _inl_21_butterfly_stage_1d_x = x0
    _inl_21_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_21_butterfly_stage_1d_STRIDE: tl.constexpr = 4
    _inl_21_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_21_butterfly_stage_1d_GRP: tl.constexpr = _inl_21_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_21_butterfly_stage_1d_STRIDE)
    if _inl_21_butterfly_stage_1d_STRIDE == 1:
        _inl_21_butterfly_stage_1d_x2 = tl.reshape(_inl_21_butterfly_stage_1d_x, (_inl_21_butterfly_stage_1d_GRP, 2))
        (_inl_21_butterfly_stage_1d_a, _inl_21_butterfly_stage_1d_b) = tl.split(_inl_21_butterfly_stage_1d_x2)
        _inl_21_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_21_butterfly_stage_1d_a + _inl_21_butterfly_stage_1d_b, _inl_21_butterfly_stage_1d_a - _inl_21_butterfly_stage_1d_b), (_inl_21_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_21_butterfly_stage_1d_x3 = tl.reshape(_inl_21_butterfly_stage_1d_x, (_inl_21_butterfly_stage_1d_GRP, 2, _inl_21_butterfly_stage_1d_STRIDE))
        _inl_21_butterfly_stage_1d_x3 = tl.permute(_inl_21_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_21_butterfly_stage_1d_a, _inl_21_butterfly_stage_1d_b) = tl.split(_inl_21_butterfly_stage_1d_x3)
        _inl_21_butterfly_stage_1d_x3 = tl.join(_inl_21_butterfly_stage_1d_a + _inl_21_butterfly_stage_1d_b, _inl_21_butterfly_stage_1d_a - _inl_21_butterfly_stage_1d_b)
        _inl_21_butterfly_stage_1d_x3 = tl.permute(_inl_21_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_21_butterfly_stage_1d_result = tl.reshape(_inl_21_butterfly_stage_1d_x3, (_inl_21_butterfly_stage_1d_BLOCK_SIZE,))
    x0 = _inl_21_butterfly_stage_1d_result
    _inl_22_butterfly_stage_1d_x = x1
    _inl_22_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_22_butterfly_stage_1d_STRIDE: tl.constexpr = 4
    _inl_22_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_22_butterfly_stage_1d_GRP: tl.constexpr = _inl_22_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_22_butterfly_stage_1d_STRIDE)
    if _inl_22_butterfly_stage_1d_STRIDE == 1:
        _inl_22_butterfly_stage_1d_x2 = tl.reshape(_inl_22_butterfly_stage_1d_x, (_inl_22_butterfly_stage_1d_GRP, 2))
        (_inl_22_butterfly_stage_1d_a, _inl_22_butterfly_stage_1d_b) = tl.split(_inl_22_butterfly_stage_1d_x2)
        _inl_22_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_22_butterfly_stage_1d_a + _inl_22_butterfly_stage_1d_b, _inl_22_butterfly_stage_1d_a - _inl_22_butterfly_stage_1d_b), (_inl_22_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_22_butterfly_stage_1d_x3 = tl.reshape(_inl_22_butterfly_stage_1d_x, (_inl_22_butterfly_stage_1d_GRP, 2, _inl_22_butterfly_stage_1d_STRIDE))
        _inl_22_butterfly_stage_1d_x3 = tl.permute(_inl_22_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_22_butterfly_stage_1d_a, _inl_22_butterfly_stage_1d_b) = tl.split(_inl_22_butterfly_stage_1d_x3)
        _inl_22_butterfly_stage_1d_x3 = tl.join(_inl_22_butterfly_stage_1d_a + _inl_22_butterfly_stage_1d_b, _inl_22_butterfly_stage_1d_a - _inl_22_butterfly_stage_1d_b)
        _inl_22_butterfly_stage_1d_x3 = tl.permute(_inl_22_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_22_butterfly_stage_1d_result = tl.reshape(_inl_22_butterfly_stage_1d_x3, (_inl_22_butterfly_stage_1d_BLOCK_SIZE,))
    x1 = _inl_22_butterfly_stage_1d_result
    _inl_23_butterfly_stage_1d_x = x2
    _inl_23_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_23_butterfly_stage_1d_STRIDE: tl.constexpr = 4
    _inl_23_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_23_butterfly_stage_1d_GRP: tl.constexpr = _inl_23_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_23_butterfly_stage_1d_STRIDE)
    if _inl_23_butterfly_stage_1d_STRIDE == 1:
        _inl_23_butterfly_stage_1d_x2 = tl.reshape(_inl_23_butterfly_stage_1d_x, (_inl_23_butterfly_stage_1d_GRP, 2))
        (_inl_23_butterfly_stage_1d_a, _inl_23_butterfly_stage_1d_b) = tl.split(_inl_23_butterfly_stage_1d_x2)
        _inl_23_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_23_butterfly_stage_1d_a + _inl_23_butterfly_stage_1d_b, _inl_23_butterfly_stage_1d_a - _inl_23_butterfly_stage_1d_b), (_inl_23_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_23_butterfly_stage_1d_x3 = tl.reshape(_inl_23_butterfly_stage_1d_x, (_inl_23_butterfly_stage_1d_GRP, 2, _inl_23_butterfly_stage_1d_STRIDE))
        _inl_23_butterfly_stage_1d_x3 = tl.permute(_inl_23_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_23_butterfly_stage_1d_a, _inl_23_butterfly_stage_1d_b) = tl.split(_inl_23_butterfly_stage_1d_x3)
        _inl_23_butterfly_stage_1d_x3 = tl.join(_inl_23_butterfly_stage_1d_a + _inl_23_butterfly_stage_1d_b, _inl_23_butterfly_stage_1d_a - _inl_23_butterfly_stage_1d_b)
        _inl_23_butterfly_stage_1d_x3 = tl.permute(_inl_23_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_23_butterfly_stage_1d_result = tl.reshape(_inl_23_butterfly_stage_1d_x3, (_inl_23_butterfly_stage_1d_BLOCK_SIZE,))
    x2 = _inl_23_butterfly_stage_1d_result
    _inl_24_butterfly_stage_1d_x = x3
    _inl_24_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_24_butterfly_stage_1d_STRIDE: tl.constexpr = 4
    _inl_24_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_24_butterfly_stage_1d_GRP: tl.constexpr = _inl_24_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_24_butterfly_stage_1d_STRIDE)
    if _inl_24_butterfly_stage_1d_STRIDE == 1:
        _inl_24_butterfly_stage_1d_x2 = tl.reshape(_inl_24_butterfly_stage_1d_x, (_inl_24_butterfly_stage_1d_GRP, 2))
        (_inl_24_butterfly_stage_1d_a, _inl_24_butterfly_stage_1d_b) = tl.split(_inl_24_butterfly_stage_1d_x2)
        _inl_24_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_24_butterfly_stage_1d_a + _inl_24_butterfly_stage_1d_b, _inl_24_butterfly_stage_1d_a - _inl_24_butterfly_stage_1d_b), (_inl_24_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_24_butterfly_stage_1d_x3 = tl.reshape(_inl_24_butterfly_stage_1d_x, (_inl_24_butterfly_stage_1d_GRP, 2, _inl_24_butterfly_stage_1d_STRIDE))
        _inl_24_butterfly_stage_1d_x3 = tl.permute(_inl_24_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_24_butterfly_stage_1d_a, _inl_24_butterfly_stage_1d_b) = tl.split(_inl_24_butterfly_stage_1d_x3)
        _inl_24_butterfly_stage_1d_x3 = tl.join(_inl_24_butterfly_stage_1d_a + _inl_24_butterfly_stage_1d_b, _inl_24_butterfly_stage_1d_a - _inl_24_butterfly_stage_1d_b)
        _inl_24_butterfly_stage_1d_x3 = tl.permute(_inl_24_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_24_butterfly_stage_1d_result = tl.reshape(_inl_24_butterfly_stage_1d_x3, (_inl_24_butterfly_stage_1d_BLOCK_SIZE,))
    x3 = _inl_24_butterfly_stage_1d_result
    _inl_25_butterfly_stage_1d_x = x0
    _inl_25_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_25_butterfly_stage_1d_STRIDE: tl.constexpr = 2
    _inl_25_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_25_butterfly_stage_1d_GRP: tl.constexpr = _inl_25_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_25_butterfly_stage_1d_STRIDE)
    if _inl_25_butterfly_stage_1d_STRIDE == 1:
        _inl_25_butterfly_stage_1d_x2 = tl.reshape(_inl_25_butterfly_stage_1d_x, (_inl_25_butterfly_stage_1d_GRP, 2))
        (_inl_25_butterfly_stage_1d_a, _inl_25_butterfly_stage_1d_b) = tl.split(_inl_25_butterfly_stage_1d_x2)
        _inl_25_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_25_butterfly_stage_1d_a + _inl_25_butterfly_stage_1d_b, _inl_25_butterfly_stage_1d_a - _inl_25_butterfly_stage_1d_b), (_inl_25_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_25_butterfly_stage_1d_x3 = tl.reshape(_inl_25_butterfly_stage_1d_x, (_inl_25_butterfly_stage_1d_GRP, 2, _inl_25_butterfly_stage_1d_STRIDE))
        _inl_25_butterfly_stage_1d_x3 = tl.permute(_inl_25_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_25_butterfly_stage_1d_a, _inl_25_butterfly_stage_1d_b) = tl.split(_inl_25_butterfly_stage_1d_x3)
        _inl_25_butterfly_stage_1d_x3 = tl.join(_inl_25_butterfly_stage_1d_a + _inl_25_butterfly_stage_1d_b, _inl_25_butterfly_stage_1d_a - _inl_25_butterfly_stage_1d_b)
        _inl_25_butterfly_stage_1d_x3 = tl.permute(_inl_25_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_25_butterfly_stage_1d_result = tl.reshape(_inl_25_butterfly_stage_1d_x3, (_inl_25_butterfly_stage_1d_BLOCK_SIZE,))
    x0 = _inl_25_butterfly_stage_1d_result
    _inl_26_butterfly_stage_1d_x = x1
    _inl_26_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_26_butterfly_stage_1d_STRIDE: tl.constexpr = 2
    _inl_26_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_26_butterfly_stage_1d_GRP: tl.constexpr = _inl_26_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_26_butterfly_stage_1d_STRIDE)
    if _inl_26_butterfly_stage_1d_STRIDE == 1:
        _inl_26_butterfly_stage_1d_x2 = tl.reshape(_inl_26_butterfly_stage_1d_x, (_inl_26_butterfly_stage_1d_GRP, 2))
        (_inl_26_butterfly_stage_1d_a, _inl_26_butterfly_stage_1d_b) = tl.split(_inl_26_butterfly_stage_1d_x2)
        _inl_26_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_26_butterfly_stage_1d_a + _inl_26_butterfly_stage_1d_b, _inl_26_butterfly_stage_1d_a - _inl_26_butterfly_stage_1d_b), (_inl_26_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_26_butterfly_stage_1d_x3 = tl.reshape(_inl_26_butterfly_stage_1d_x, (_inl_26_butterfly_stage_1d_GRP, 2, _inl_26_butterfly_stage_1d_STRIDE))
        _inl_26_butterfly_stage_1d_x3 = tl.permute(_inl_26_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_26_butterfly_stage_1d_a, _inl_26_butterfly_stage_1d_b) = tl.split(_inl_26_butterfly_stage_1d_x3)
        _inl_26_butterfly_stage_1d_x3 = tl.join(_inl_26_butterfly_stage_1d_a + _inl_26_butterfly_stage_1d_b, _inl_26_butterfly_stage_1d_a - _inl_26_butterfly_stage_1d_b)
        _inl_26_butterfly_stage_1d_x3 = tl.permute(_inl_26_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_26_butterfly_stage_1d_result = tl.reshape(_inl_26_butterfly_stage_1d_x3, (_inl_26_butterfly_stage_1d_BLOCK_SIZE,))
    x1 = _inl_26_butterfly_stage_1d_result
    _inl_27_butterfly_stage_1d_x = x2
    _inl_27_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_27_butterfly_stage_1d_STRIDE: tl.constexpr = 2
    _inl_27_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_27_butterfly_stage_1d_GRP: tl.constexpr = _inl_27_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_27_butterfly_stage_1d_STRIDE)
    if _inl_27_butterfly_stage_1d_STRIDE == 1:
        _inl_27_butterfly_stage_1d_x2 = tl.reshape(_inl_27_butterfly_stage_1d_x, (_inl_27_butterfly_stage_1d_GRP, 2))
        (_inl_27_butterfly_stage_1d_a, _inl_27_butterfly_stage_1d_b) = tl.split(_inl_27_butterfly_stage_1d_x2)
        _inl_27_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_27_butterfly_stage_1d_a + _inl_27_butterfly_stage_1d_b, _inl_27_butterfly_stage_1d_a - _inl_27_butterfly_stage_1d_b), (_inl_27_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_27_butterfly_stage_1d_x3 = tl.reshape(_inl_27_butterfly_stage_1d_x, (_inl_27_butterfly_stage_1d_GRP, 2, _inl_27_butterfly_stage_1d_STRIDE))
        _inl_27_butterfly_stage_1d_x3 = tl.permute(_inl_27_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_27_butterfly_stage_1d_a, _inl_27_butterfly_stage_1d_b) = tl.split(_inl_27_butterfly_stage_1d_x3)
        _inl_27_butterfly_stage_1d_x3 = tl.join(_inl_27_butterfly_stage_1d_a + _inl_27_butterfly_stage_1d_b, _inl_27_butterfly_stage_1d_a - _inl_27_butterfly_stage_1d_b)
        _inl_27_butterfly_stage_1d_x3 = tl.permute(_inl_27_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_27_butterfly_stage_1d_result = tl.reshape(_inl_27_butterfly_stage_1d_x3, (_inl_27_butterfly_stage_1d_BLOCK_SIZE,))
    x2 = _inl_27_butterfly_stage_1d_result
    _inl_28_butterfly_stage_1d_x = x3
    _inl_28_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_28_butterfly_stage_1d_STRIDE: tl.constexpr = 2
    _inl_28_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_28_butterfly_stage_1d_GRP: tl.constexpr = _inl_28_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_28_butterfly_stage_1d_STRIDE)
    if _inl_28_butterfly_stage_1d_STRIDE == 1:
        _inl_28_butterfly_stage_1d_x2 = tl.reshape(_inl_28_butterfly_stage_1d_x, (_inl_28_butterfly_stage_1d_GRP, 2))
        (_inl_28_butterfly_stage_1d_a, _inl_28_butterfly_stage_1d_b) = tl.split(_inl_28_butterfly_stage_1d_x2)
        _inl_28_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_28_butterfly_stage_1d_a + _inl_28_butterfly_stage_1d_b, _inl_28_butterfly_stage_1d_a - _inl_28_butterfly_stage_1d_b), (_inl_28_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_28_butterfly_stage_1d_x3 = tl.reshape(_inl_28_butterfly_stage_1d_x, (_inl_28_butterfly_stage_1d_GRP, 2, _inl_28_butterfly_stage_1d_STRIDE))
        _inl_28_butterfly_stage_1d_x3 = tl.permute(_inl_28_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_28_butterfly_stage_1d_a, _inl_28_butterfly_stage_1d_b) = tl.split(_inl_28_butterfly_stage_1d_x3)
        _inl_28_butterfly_stage_1d_x3 = tl.join(_inl_28_butterfly_stage_1d_a + _inl_28_butterfly_stage_1d_b, _inl_28_butterfly_stage_1d_a - _inl_28_butterfly_stage_1d_b)
        _inl_28_butterfly_stage_1d_x3 = tl.permute(_inl_28_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_28_butterfly_stage_1d_result = tl.reshape(_inl_28_butterfly_stage_1d_x3, (_inl_28_butterfly_stage_1d_BLOCK_SIZE,))
    x3 = _inl_28_butterfly_stage_1d_result
    _inl_29_butterfly_stage_1d_x = x0
    _inl_29_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_29_butterfly_stage_1d_STRIDE: tl.constexpr = 1
    _inl_29_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_29_butterfly_stage_1d_GRP: tl.constexpr = _inl_29_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_29_butterfly_stage_1d_STRIDE)
    if _inl_29_butterfly_stage_1d_STRIDE == 1:
        _inl_29_butterfly_stage_1d_x2 = tl.reshape(_inl_29_butterfly_stage_1d_x, (_inl_29_butterfly_stage_1d_GRP, 2))
        (_inl_29_butterfly_stage_1d_a, _inl_29_butterfly_stage_1d_b) = tl.split(_inl_29_butterfly_stage_1d_x2)
        _inl_29_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_29_butterfly_stage_1d_a + _inl_29_butterfly_stage_1d_b, _inl_29_butterfly_stage_1d_a - _inl_29_butterfly_stage_1d_b), (_inl_29_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_29_butterfly_stage_1d_x3 = tl.reshape(_inl_29_butterfly_stage_1d_x, (_inl_29_butterfly_stage_1d_GRP, 2, _inl_29_butterfly_stage_1d_STRIDE))
        _inl_29_butterfly_stage_1d_x3 = tl.permute(_inl_29_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_29_butterfly_stage_1d_a, _inl_29_butterfly_stage_1d_b) = tl.split(_inl_29_butterfly_stage_1d_x3)
        _inl_29_butterfly_stage_1d_x3 = tl.join(_inl_29_butterfly_stage_1d_a + _inl_29_butterfly_stage_1d_b, _inl_29_butterfly_stage_1d_a - _inl_29_butterfly_stage_1d_b)
        _inl_29_butterfly_stage_1d_x3 = tl.permute(_inl_29_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_29_butterfly_stage_1d_result = tl.reshape(_inl_29_butterfly_stage_1d_x3, (_inl_29_butterfly_stage_1d_BLOCK_SIZE,))
    x0 = _inl_29_butterfly_stage_1d_result
    _inl_30_butterfly_stage_1d_x = x1
    _inl_30_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_30_butterfly_stage_1d_STRIDE: tl.constexpr = 1
    _inl_30_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_30_butterfly_stage_1d_GRP: tl.constexpr = _inl_30_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_30_butterfly_stage_1d_STRIDE)
    if _inl_30_butterfly_stage_1d_STRIDE == 1:
        _inl_30_butterfly_stage_1d_x2 = tl.reshape(_inl_30_butterfly_stage_1d_x, (_inl_30_butterfly_stage_1d_GRP, 2))
        (_inl_30_butterfly_stage_1d_a, _inl_30_butterfly_stage_1d_b) = tl.split(_inl_30_butterfly_stage_1d_x2)
        _inl_30_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_30_butterfly_stage_1d_a + _inl_30_butterfly_stage_1d_b, _inl_30_butterfly_stage_1d_a - _inl_30_butterfly_stage_1d_b), (_inl_30_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_30_butterfly_stage_1d_x3 = tl.reshape(_inl_30_butterfly_stage_1d_x, (_inl_30_butterfly_stage_1d_GRP, 2, _inl_30_butterfly_stage_1d_STRIDE))
        _inl_30_butterfly_stage_1d_x3 = tl.permute(_inl_30_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_30_butterfly_stage_1d_a, _inl_30_butterfly_stage_1d_b) = tl.split(_inl_30_butterfly_stage_1d_x3)
        _inl_30_butterfly_stage_1d_x3 = tl.join(_inl_30_butterfly_stage_1d_a + _inl_30_butterfly_stage_1d_b, _inl_30_butterfly_stage_1d_a - _inl_30_butterfly_stage_1d_b)
        _inl_30_butterfly_stage_1d_x3 = tl.permute(_inl_30_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_30_butterfly_stage_1d_result = tl.reshape(_inl_30_butterfly_stage_1d_x3, (_inl_30_butterfly_stage_1d_BLOCK_SIZE,))
    x1 = _inl_30_butterfly_stage_1d_result
    _inl_31_butterfly_stage_1d_x = x2
    _inl_31_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_31_butterfly_stage_1d_STRIDE: tl.constexpr = 1
    _inl_31_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_31_butterfly_stage_1d_GRP: tl.constexpr = _inl_31_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_31_butterfly_stage_1d_STRIDE)
    if _inl_31_butterfly_stage_1d_STRIDE == 1:
        _inl_31_butterfly_stage_1d_x2 = tl.reshape(_inl_31_butterfly_stage_1d_x, (_inl_31_butterfly_stage_1d_GRP, 2))
        (_inl_31_butterfly_stage_1d_a, _inl_31_butterfly_stage_1d_b) = tl.split(_inl_31_butterfly_stage_1d_x2)
        _inl_31_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_31_butterfly_stage_1d_a + _inl_31_butterfly_stage_1d_b, _inl_31_butterfly_stage_1d_a - _inl_31_butterfly_stage_1d_b), (_inl_31_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_31_butterfly_stage_1d_x3 = tl.reshape(_inl_31_butterfly_stage_1d_x, (_inl_31_butterfly_stage_1d_GRP, 2, _inl_31_butterfly_stage_1d_STRIDE))
        _inl_31_butterfly_stage_1d_x3 = tl.permute(_inl_31_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_31_butterfly_stage_1d_a, _inl_31_butterfly_stage_1d_b) = tl.split(_inl_31_butterfly_stage_1d_x3)
        _inl_31_butterfly_stage_1d_x3 = tl.join(_inl_31_butterfly_stage_1d_a + _inl_31_butterfly_stage_1d_b, _inl_31_butterfly_stage_1d_a - _inl_31_butterfly_stage_1d_b)
        _inl_31_butterfly_stage_1d_x3 = tl.permute(_inl_31_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_31_butterfly_stage_1d_result = tl.reshape(_inl_31_butterfly_stage_1d_x3, (_inl_31_butterfly_stage_1d_BLOCK_SIZE,))
    x2 = _inl_31_butterfly_stage_1d_result
    _inl_32_butterfly_stage_1d_x = x3
    _inl_32_butterfly_stage_1d_BLOCK_SIZE: tl.constexpr = 256
    _inl_32_butterfly_stage_1d_STRIDE: tl.constexpr = 1
    _inl_32_butterfly_stage_1d_result = 0
    'One butterfly stage on a 1D vector.'
    _inl_32_butterfly_stage_1d_GRP: tl.constexpr = _inl_32_butterfly_stage_1d_BLOCK_SIZE // (2 * _inl_32_butterfly_stage_1d_STRIDE)
    if _inl_32_butterfly_stage_1d_STRIDE == 1:
        _inl_32_butterfly_stage_1d_x2 = tl.reshape(_inl_32_butterfly_stage_1d_x, (_inl_32_butterfly_stage_1d_GRP, 2))
        (_inl_32_butterfly_stage_1d_a, _inl_32_butterfly_stage_1d_b) = tl.split(_inl_32_butterfly_stage_1d_x2)
        _inl_32_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_32_butterfly_stage_1d_a + _inl_32_butterfly_stage_1d_b, _inl_32_butterfly_stage_1d_a - _inl_32_butterfly_stage_1d_b), (_inl_32_butterfly_stage_1d_BLOCK_SIZE,))
    else:
        _inl_32_butterfly_stage_1d_x3 = tl.reshape(_inl_32_butterfly_stage_1d_x, (_inl_32_butterfly_stage_1d_GRP, 2, _inl_32_butterfly_stage_1d_STRIDE))
        _inl_32_butterfly_stage_1d_x3 = tl.permute(_inl_32_butterfly_stage_1d_x3, (0, 2, 1))
        (_inl_32_butterfly_stage_1d_a, _inl_32_butterfly_stage_1d_b) = tl.split(_inl_32_butterfly_stage_1d_x3)
        _inl_32_butterfly_stage_1d_x3 = tl.join(_inl_32_butterfly_stage_1d_a + _inl_32_butterfly_stage_1d_b, _inl_32_butterfly_stage_1d_a - _inl_32_butterfly_stage_1d_b)
        _inl_32_butterfly_stage_1d_x3 = tl.permute(_inl_32_butterfly_stage_1d_x3, (0, 2, 1))
        _inl_32_butterfly_stage_1d_result = tl.reshape(_inl_32_butterfly_stage_1d_x3, (_inl_32_butterfly_stage_1d_BLOCK_SIZE,))
    x3 = _inl_32_butterfly_stage_1d_result
    x0 = x0 * SCALE
    x1 = x1 * SCALE
    x2 = x2 * SCALE
    x3 = x3 * SCALE
    tl.store(OUT_ptr + row0 * stride_out_row + col_offs, x0, eviction_policy='evict_first')
    tl.store(OUT_ptr + row1 * stride_out_row + col_offs, x1, mask=row1 < N_ROWS, eviction_policy='evict_first')
    tl.store(OUT_ptr + row2 * stride_out_row + col_offs, x2, mask=row2 < N_ROWS, eviction_policy='evict_first')
    tl.store(OUT_ptr + row3 * stride_out_row + col_offs, x3, mask=row3 < N_ROWS, eviction_policy='evict_first')
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
SHAPES = ((17,),);DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 x=args["X_ptr"].reshape(-1,int(meta.get("DIM",args["stride_x_row"])));y=np.array(x,copy=True)
 h=1
 while h<y.shape[1]:
  for s in range(0,y.shape[1],2*h):
   a=y[:,s:s+h].copy();b=y[:,s+h:s+2*h].copy();y[:,s:s+h]=a+b;y[:,s+h:s+2*h]=a-b
  h*=2
 y*=np.float32(meta["SCALE"])
 return {"OUT_ptr":y.reshape(-1)}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    if len(shape) > 1 and tuple(shape) not in SHAPES:
        raise ValueError('unsupported explicit shape configuration')
    del dtype
    import numpy as np
    N = int(shape[0])
    rng = fast_rng(seed)
    R = int(shape[0]) if len(shape) > 1 else 4
    D = int(shape[1]) if len(shape) > 1 else 256
    T = R * D
    ROWS_PER_PROGRAM = 4
    args = {'X_ptr': _aligned(rng.normal(0, 0.8, T)), 'OUT_ptr': _aligned(np.full(T, -7.0)), 'stride_x_row': D, 'stride_out_row': D, 'N_ROWS': R}
    meta = {'SCALE': 0.0625}
    grid = ((R + ROWS_PER_PROGRAM - 1) // ROWS_PER_PROGRAM,)
    outputs = ('OUT_ptr',)
    return _case(_fht_kernel_256_4row_native, grid, args, meta, ('X_ptr',), outputs, ref(args, meta), shape, 'torch.float32', seed, {'complete_launch_plan': True, 'formula': 'scaled length-256 fast Walsh-Hadamard transform'})

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
