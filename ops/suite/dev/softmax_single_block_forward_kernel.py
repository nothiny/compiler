"""One-JIT standalone Triton compiler test case."""

COPIED_FROM = {'repo': 'ops-pool/smoke', 'note': 'validated case layer intact; lottery 20261019'}
OPERATOR = {"name": "hidden/softmax_single_block_forward_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["norm"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def _softmax_single_block_forward_kernel(Y_ptr, Y_row_stride, X_ptr, X_row_stride, n_rows: tl.constexpr, n_cols: tl.constexpr, BLOCK_SIZE: tl.constexpr, ROWS_PER_BLOCK: tl.constexpr):
    """
    Single-block softmax forward kernel for small column sizes.

    Processes entire row in one block when n_cols <= BLOCK_SIZE.
    Uses 2D tensor to process multiple rows simultaneously for better UB utilization.

    Args:
        Y_ptr: Output tensor pointer
        Y_row_stride: Stride for output rows
        X_ptr: Input tensor pointer
        X_row_stride: Stride for input rows
        n_rows: Number of rows to process
        n_cols: Number of columns per row
        BLOCK_SIZE: Block size for column processing
        ROWS_PER_BLOCK: Number of rows to process simultaneously
    """
    row_block_start = tl.program_id(0) * ROWS_PER_BLOCK
    row_block_step = tl.num_programs(0) * ROWS_PER_BLOCK
    row_offsets = tl.arange(0, ROWS_PER_BLOCK)
    col_offsets = tl.arange(0, BLOCK_SIZE)
    for row_block_idx in tl.range(row_block_start, n_rows, row_block_step):
        row_idx = row_block_idx + row_offsets
        row_mask = row_idx < n_rows
        col_mask = col_offsets < n_cols
        mask = row_mask[:, None] & col_mask[None, :]
        offsets = row_idx[:, None] * X_row_stride + col_offsets[None, :]
        x = tl.load(X_ptr + offsets, mask=mask, other=float('-inf'))
        m = tl.max(x, axis=1)
        e = tl.exp(x - m[:, None])
        d = tl.sum(e, axis=1)
        y = e / d[:, None]
        offsets = row_idx[:, None] * Y_row_stride + col_offsets[None, :]
        tl.store(Y_ptr + offsets, y, mask=mask)
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
SHAPES = ((1, 17), (20, 17))

DTYPES = ('float32', 'float16', 'bfloat16')
FIXED_META = {"BLOCK_SIZE": 128}
LAUNCH_META = {"num_warps": 4, "num_stages": 1}


def ref(args, meta):
    del meta
    import numpy as np
    x = np.asarray(args["X_ptr"], dtype=np.float32)
    shifted = x - np.max(x, axis=1, keepdims=True)
    exp = np.exp(shifted, dtype=np.float32)
    return {"Y_ptr": (exp / np.sum(exp, axis=1, keepdims=True, dtype=np.float32)).astype(np.float32)}


def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    del dtype
    import numpy as np
    (rows, cols) = (int(value) for value in shape)
    rng = fast_rng(seed)
    x = _aligned(rng.uniform(-4.0, 4.0, rows * cols), 'float32').reshape(rows, cols)
    y = _aligned(np.full(rows * cols, -0.875), 'float32').reshape(rows, cols)
    args = {'Y_ptr': y, 'Y_row_stride': cols, 'X_ptr': x, 'X_row_stride': cols}
    meta = {'n_rows': rows, 'n_cols': cols, 'BLOCK_SIZE': max(128, 1 << max(0, (cols - 1).bit_length())), 'ROWS_PER_BLOCK': 4}
    grid = ((rows + meta['ROWS_PER_BLOCK'] - 1) // meta['ROWS_PER_BLOCK'],)
    outputs = ('Y_ptr',)
    return {'kernel': _softmax_single_block_forward_kernel, 'grid': grid, 'args': args, 'meta': meta, 'launch_meta': dict(LAUNCH_META), 'inputs': ('X_ptr',), 'outputs': outputs, 'expected': ref(args, meta), 'comparison': _comparison(outputs, rtol=0.0002, atol=2e-05, dtype='torch.float32'), 'pointer_dtypes': {'X_ptr': 'float32', 'Y_ptr': 'float32'}, 'buffer_extents': {'X_ptr': rows * cols, 'Y_ptr': rows * cols}, 'buffer_layouts': _layouts(args), 'alignment': 64, 'aliases': {}, 'seed': int(seed), 'shape': tuple(shape), 'dtype': 'torch.float32', 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'coverage': {'complete_logical_output': True, 'grid_formula': '(ceil_div(n_rows, ROWS_PER_BLOCK),)', 'output': 'outputs[rows,n_cols]'}}

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
