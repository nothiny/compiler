"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/median_fp32_strided_key_select_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def median_fp32_strided_key_select_kernel(inp, values, indices, total_outputs, reduction_size, inner_size, BLOCK: tl.constexpr, BLOCK_OUT: tl.constexpr):
    out_offsets = tl.program_id(0) * BLOCK_OUT + tl.arange(0, BLOCK_OUT)
    out_mask = out_offsets < total_outputs
    inner_offsets = out_offsets % inner_size
    outer_offsets = out_offsets // inner_size
    cols = tl.arange(0, BLOCK)
    valid = (cols[None, :] < reduction_size) & out_mask[:, None]
    ptrs = inp + outer_offsets[:, None] * reduction_size * inner_size + cols[None, :] * inner_size + inner_offsets[:, None]
    data = tl.load(ptrs, mask=valid, other=0.0)
    nan_mask = valid & (data != data)
    nan_i32 = nan_mask.to(tl.int32)
    has_nan = tl.max(nan_i32, axis=1) != 0
    first_nan = tl.argmax(nan_i32, axis=1)
    nan_value = tl.load(inp + outer_offsets * reduction_size * inner_size + first_nan * inner_size + inner_offsets, mask=out_mask, other=0.0)
    key1_bits = data.to(tl.uint32, bitcast=True)
    keys = key1_bits ^ (tl.full((), 2147483648, dtype=tl.uint32) | (data.to(tl.int32, bitcast=True) >> 31).to(tl.uint32, bitcast=True))
    finite = valid & ~nan_mask
    key_min_fill = tl.full((), 4294967295, dtype=tl.uint32)
    key_max_fill = tl.full((), 0, dtype=tl.uint32)
    row_min = tl.min(tl.where(finite, keys, key_min_fill), axis=1)
    row_max = tl.max(tl.where(finite, keys, key_max_fill), axis=1)
    lo = row_min
    hi = row_max
    rank = (reduction_size - 1) // 2
    for _ in tl.static_range(0, 32):
        mid = lo + (hi - lo >> 1)
        le_count = tl.sum((finite & (keys <= mid[:, None])).to(tl.int32), axis=1)
        take_left = le_count > rank
        hi = tl.where(take_left, mid, hi)
        lo = tl.where(take_left, lo, mid + 1)
    selected_key = lo
    key_match = finite & (keys == selected_key[:, None])
    selected_key_first = tl.argmax(key_match.to(tl.int32), axis=1)
    selected_value = tl.load(inp + outer_offsets * reduction_size * inner_size + selected_key_first * inner_size + inner_offsets, mask=out_mask, other=0.0)
    selected_value = tl.where(has_nan, nan_value, selected_value)
    first_match = tl.where(has_nan, first_nan, selected_key_first)
    tl.store(values + out_offsets, selected_value, mask=out_mask)
    tl.store(indices + out_offsets, first_match.to(tl.int64), mask=out_mask)
CASE_SCHEMA = 3
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
        if _comparison_dtype_policy == 'torch.float32':
            (rtol, atol) = (0.0001, 0.0001)
        elif _comparison_dtype_policy == 'torch.bfloat16':
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
SHAPES = ((2, 17, 3), (4, 65, 7))
DTYPES = ('float32',)
FIXED_META = {"BLOCK": 128, "BLOCK_OUT": 4}
LAUNCH_META = {"num_warps": 4, "num_stages": 1}


def ref(args, meta):
    del meta
    import numpy as np
    x = np.asarray(args["inp"]); outer, reduction, inner = x.shape; values = np.empty((outer, inner), dtype=x.dtype); indices = np.empty((outer, inner), dtype=np.int64)
    for o in range(outer):
        for i in range(inner):
            row = x[o, :, i]; nan = np.flatnonzero(np.isnan(row))
            if nan.size: index = int(nan[0])
            else:
                # Match the kernel order: distinguish -0.0 from +0.0.
                bits = row.astype(np.float32).view(np.uint32)
                keys = np.where((bits >> 31) != 0, ~bits, bits ^ np.uint32(0x80000000))
                order = np.argsort(keys, kind="stable")
                selected_key = keys[order[(reduction - 1) // 2]]
                index = int(np.flatnonzero(keys == selected_key)[0])
            values[o, i] = row[index]; indices[o, i] = index
    return {"values": values.reshape(-1), "indices": indices.reshape(-1)}


def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    import numpy as np
    dtype_name = str(dtype).rsplit('.', 1)[-1]
    (outer, reduction, inner) = (int(value) for value in shape)
    total = outer * inner
    rng = fast_rng(seed)
    x = rng.uniform(-4.0, 4.0, outer * reduction * inner).astype(np.dtype(dtype_name)).reshape(outer, reduction, inner)
    x[0, min(2, reduction - 1), 0] = np.nan
    args = {'inp': _aligned(x, dtype_name), 'values': _aligned(np.full(total, -0.875), dtype_name), 'indices': _aligned(np.full(total, -7), 'int64'), 'total_outputs': total, 'reduction_size': reduction, 'inner_size': inner}
    meta = dict(FIXED_META)
    grid = ((total + meta['BLOCK_OUT'] - 1) // meta['BLOCK_OUT'],)
    outputs = ('values', 'indices')
    return {'kernel': median_fp32_strided_key_select_kernel, 'grid': grid, 'args': args, 'meta': meta, 'launch_meta': dict(LAUNCH_META), 'inputs': ('inp',), 'outputs': outputs, 'expected': ref(args, meta), 'comparison': _comparison(outputs, exact=True, dtype=str(dtype)), 'pointer_dtypes': {'inp': dtype_name, 'values': dtype_name, 'indices': 'int64'}, 'buffer_extents': {'inp': outer * reduction * inner, 'values': total, 'indices': total}, 'buffer_layouts': _layouts(args), 'alignment': 64, 'aliases': {}, 'seed': int(seed), 'shape': tuple(shape), 'dtype': str(dtype), 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'coverage': {'complete_logical_output': True, 'grid_formula': '(ceil_div(total_outputs, BLOCK_OUT),)', 'outputs': outputs}}

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
