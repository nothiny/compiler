"""median_f16_key_select_kernel: 从 ~/ops 仓库复制(smoke @ ops),保留其已验证的 case 层。

模式: args.runtime_scalar、cast.to、control.for_range、control.loop_carried、control.static_range、creation.arange、creation.full、creation.where、dtype.int16、dtype.int32。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。constexpr 参数: WIDTH, BLOCK。

文件只有两层:
  ① median_f16_key_select_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/median_f16_key_select_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'cast.to', 'control.for_range', 'control.loop_carried', 'control.static_range', 'creation.arange', 'creation.full', 'creation.where', 'dtype.int16', 'dtype.int32', 'dtype.int64', 'dtype.uint16', 'dtype.uint32', 'memory.load', 'memory.load.masked', 'memory.load.other', 'memory.store', 'reduce.argmax.axis0', 'reduce.max.axis0', 'reduce.min.axis0', 'reduce.sum.axis0']}
COPIED_FROM = {'repo': 'smoke @ ops', 'note': 'validated case layer intact'}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def median_f16_key_select_kernel(row_data, values, indices, WIDTH: tl.constexpr, BLOCK: tl.constexpr):
    row = tl.program_id(0)
    cols = tl.arange(0, BLOCK)
    valid = cols < WIDTH
    base = row_data + row * WIDTH
    data = tl.load(base + cols, mask=valid, other=0.0)
    nan_mask = valid & (data != data)
    nan_i32 = nan_mask.to(tl.int32)
    has_nan = tl.max(nan_i32, axis=0) != 0
    first_nan = tl.argmax(nan_i32, axis=0)
    nan_value = tl.load(base + first_nan, mask=has_nan, other=0.0)
    finite = valid & ~nan_mask
    neg_inf_mask = finite & (data == -float('inf'))
    pos_inf_mask = finite & (data == float('inf'))
    real_finite = finite & ~(neg_inf_mask | pos_inf_mask)
    neg_inf_count = tl.sum(neg_inf_mask.to(tl.int32), axis=0)
    real_finite_count = tl.sum(real_finite.to(tl.int32), axis=0)
    rank = (WIDTH - 1) // 2
    search_rank = rank - neg_inf_count
    take_neg_inf = rank < neg_inf_count
    take_pos_inf = search_rank >= real_finite_count
    key1_bits = data.to(tl.uint16, bitcast=True)
    key1_result = key1_bits ^ (tl.full((), 32768, dtype=tl.uint16) | (data.to(tl.int16, bitcast=True) >> 15).to(tl.uint16, bitcast=True))
    keys = key1_result.to(tl.uint32)
    key_min_fill = tl.full((), 65535, dtype=tl.uint32)
    key_max_fill = tl.full((), 0, dtype=tl.uint32)
    row_min = tl.min(tl.where(real_finite, keys, key_min_fill), axis=0)
    row_max = tl.max(tl.where(real_finite, keys, key_max_fill), axis=0)
    has_real_finite = real_finite_count != 0
    row_min = tl.where(has_real_finite, row_min, 0)
    row_max = tl.where(has_real_finite, row_max, 0)
    lo = row_min
    hi = row_max
    for _ in tl.static_range(0, 16):
        mid = lo + (hi - lo >> 1)
        le_count = tl.sum((real_finite & (keys <= mid)).to(tl.int32), axis=0)
        take_left = le_count > search_rank
        hi = tl.where(take_left, mid, hi)
        lo = tl.where(take_left, lo, mid + 1)
    selected_key = lo
    key_match = real_finite & (keys == selected_key)
    selected_key_first = tl.argmax(key_match.to(tl.int32), axis=0)
    selected_value = tl.load(base + selected_key_first)
    first_neg_inf = tl.argmax(neg_inf_mask.to(tl.int32), axis=0)
    neg_inf_value = tl.load(base + first_neg_inf, mask=take_neg_inf, other=0.0)
    first_pos_inf = tl.argmax(pos_inf_mask.to(tl.int32), axis=0)
    pos_inf_value = tl.load(base + first_pos_inf, mask=take_pos_inf, other=0.0)
    selected_value = tl.where(take_neg_inf, neg_inf_value, selected_value)
    selected_value = tl.where(take_pos_inf, pos_inf_value, selected_value)
    selected_key_first = tl.where(take_neg_inf, first_neg_inf, selected_key_first)
    selected_key_first = tl.where(take_pos_inf, first_pos_inf, selected_key_first)
    selected_value = tl.where(has_nan, nan_value, selected_value)
    first_match = tl.where(has_nan, first_nan, selected_key_first)
    tl.store(values + row, selected_value)
    tl.store(indices + row, first_match.to(tl.int64))

# ------------------------------------------------------------------ ② case 层
# (shape,) 的角色:第一个是典型用法,其余是泛化/尾块/退化用例。
#   (1, 17)
#   (3, 33)
#   (8, 65)
#   (16, 17)
# DTYPES: float16 —— 原始用途的 dtype 在前;非法域(例如本机 Triton 只吃 fp32 的exp/sqrt/erf/atomic)的算子只声明合法的那一种。

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

SHAPES = ((1, 17), (3, 33), (1, 34))
DTYPES = ('float16', 'bfloat16')
FIXED_META = {"WIDTH": 17, "BLOCK": 128}
LAUNCH_META = {"num_warps": 4, "num_stages": 1}
def ref(args, meta):
    import numpy as np
    x = np.asarray(args["row_data"]); rows, width = x.shape; values = np.empty(rows, dtype=x.dtype); indices = np.empty(rows, dtype=np.int64)
    for row_id in range(rows):
        row = x[row_id]; nan = np.flatnonzero(np.isnan(row))
        if nan.size: index = int(nan[0])
        else:
            # Match the kernel order: distinguish -0.0 from +0.0.
            bits = row.astype(np.float32).view(np.uint32)
            keys = np.where((bits >> 31) != 0, ~bits, bits ^ np.uint32(0x80000000))
            order = np.argsort(keys, kind="stable")
            selected_key = keys[order[(width - 1) // 2]]
            index = int(np.flatnonzero(keys == selected_key)[0])
        values[row_id] = row[index]; indices[row_id] = index
    return {"values": values, "indices": indices}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    import numpy as np
    dtype_name = str(dtype).rsplit('.', 1)[-1]
    (rows, width) = (int(value) for value in shape)
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = rng.uniform(-4.0, 4.0, rows * width).astype(np.dtype(dtype_name)).reshape(rows, width)
    x[0, min(2, width - 1)] = np.nan
    args = {'row_data': _aligned(x, dtype_name), 'values': _aligned(np.full(rows, -0.875), dtype_name), 'indices': _aligned(np.full(rows, -7), 'int64')}
    meta = {'WIDTH': width, 'BLOCK': 128}
    grid = (rows,)
    outputs = ('values', 'indices')
    return {'kernel': median_f16_key_select_kernel, 'grid': grid, 'args': args, 'meta': meta, 'launch_meta': dict(LAUNCH_META), 'inputs': ('row_data',), 'outputs': outputs, 'expected': ref(args, meta), 'comparison': _comparison(outputs, exact=True, dtype=str(dtype)), 'pointer_dtypes': {'row_data': dtype_name, 'values': dtype_name, 'indices': 'int64'}, 'buffer_extents': {'row_data': rows * width, 'values': rows, 'indices': rows}, 'buffer_layouts': _layouts(args), 'alignment': 64, 'aliases': {}, 'seed': int(seed), 'shape': tuple(shape), 'dtype': str(dtype), 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'coverage': {'complete_logical_output': True, 'grid_formula': '(rows,)', 'outputs': outputs}}
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
    # The fixture intentionally includes NaN; matching NaN positions are correct.
    case["comparison"]["values"]["equal_nan"] = True
    case.setdefault("outputs", tuple(case["expected"]))
    case.setdefault("launch_meta", {})
    return case


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float16'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float16': 'float16'}


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
