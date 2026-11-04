"""One-JIT standalone Triton compiler test case."""

COPIED_FROM = {'repo': 'ops-pool/smoke', 'note': 'validated case layer intact; lottery 20261019'}
OPERATOR = {"name": "hidden/cross_entropy_forward_kernel_plain", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["loss"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def liger_cross_entropy_forward_kernel_plain(X_ptr, X_stride, Y_ptr, loss_ptr, n_cols, n_rows, ce_stats_ptr, ignore_index, reduction: tl.constexpr, BLOCK_SIZE: tl.constexpr):
    """
    Plain CE forward fast path (no weight/softcap/smoothing/z-loss/metrics).
    1 program processes 1 row to maximize parallelism (unlike the generic kernel
    which chunks rows per program for flexibility).
    Writes per-row loss to ``loss_ptr`` (float32 recommended).
    """
    row = tl.program_id(0)
    if row >= n_rows:
        return
    row_i64 = row.to(tl.int64)
    y = tl.load(Y_ptr + row_i64)
    inv_n = tl.load(ce_stats_ptr + 0).cast(tl.float32)
    if y == ignore_index:
        tl.store(loss_ptr + row_i64, 0.0)
        return
    logits_row_ptr = X_ptr + row_i64 * X_stride
    m = float('-inf')
    d = 0.0
    x_y = tl.load(logits_row_ptr + y).cast(tl.float32)
    for i in range(0, n_cols, BLOCK_SIZE):
        offs = i + tl.arange(0, BLOCK_SIZE)
        x = tl.load(logits_row_ptr + offs, mask=offs < n_cols, other=float('-inf')).cast(tl.float32)
        block_max = tl.max(x)
        m_new = tl.maximum(m, block_max)
        d = d * tl.exp(m - m_new) + tl.sum(tl.exp(x - m_new))
        m = m_new
    lse = m + tl.log(d)
    loss = lse - x_y
    if reduction == 'mean':
        loss = loss * inv_n
    tl.store(loss_ptr + row_i64, loss)
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
SHAPES = ((1, 17), (13, 17))

DTYPES = ('float32', 'float16', 'bfloat16')
LAUNCH_META = {"num_warps": 4, "num_stages": 1}

FIXED_META = {"reduction": "mean", "BLOCK_SIZE": 128}


def ref(args, meta):
    """Row-wise mathematical reference; preserve buffers the kernel does not write."""
    import numpy as np

    x_buffer = np.asarray(args["X_ptr"])
    labels = np.asarray(args["Y_ptr"]).reshape(-1)
    cols = int(args["n_cols"])
    rows = int(args.get("n_rows", x_buffer.shape[0]))
    x = x_buffer.reshape(-1)
    result = {name: np.asarray(args[name]).copy() for name in ('loss_ptr',)}
    flat = {name: value.reshape(-1) for name, value in result.items()}
    mean = meta["reduction"] == "mean"
    stats = np.asarray(args["ce_stats_ptr"]).reshape(-1)
    inv_n = float(stats[0])
    inv_weight = float(stats[1])
    weight_sum = float(stats[2])
    for row in range(rows):
        target = int(labels[row * int(args.get("Y_stride", 1))])
        xi = row * int(args["X_stride"]) + np.arange(cols)
        oi = row * int(args.get("loss_stride", 1))
        if target == int(args["ignore_index"]):
            flat["loss_ptr"][oi] = 0.0
            continue
        if not 0 <= target < cols:
            raise ValueError("target is outside the class range")
        logits = x[xi].astype(np.float64)
        maximum = logits.max()
        lse = maximum + np.log(np.exp(logits - maximum).sum())
        flat["loss_ptr"][oi] = (lse - logits[target]) * (inv_n if mean else 1.0)
    return result


def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    del dtype
    import numpy as np
    (rows, cols) = (int(value) for value in shape)
    rng = fast_rng(seed)
    x = _aligned(rng.uniform(-4.0, 4.0, rows * cols), 'float32').reshape(rows, cols)
    y = _aligned(rng.integers(0, cols, rows), 'int64')
    args = {'X_ptr': x, 'X_stride': cols, 'Y_ptr': y, 'loss_ptr': _aligned(np.full(rows, -0.875), 'float32'), 'n_cols': cols, 'n_rows': rows, 'ce_stats_ptr': _aligned([1.0 / rows, 1.0, float(cols)], 'float32'), 'ignore_index': -100}
    meta = dict(FIXED_META)
    outputs = ('loss_ptr',)
    return {'kernel': liger_cross_entropy_forward_kernel_plain, 'grid': (rows,), 'args': args, 'meta': meta, 'launch_meta': dict(LAUNCH_META), 'inputs': ('X_ptr', 'Y_ptr', 'ce_stats_ptr'), 'outputs': outputs, 'expected': ref(args, meta), 'comparison': _comparison(outputs, rtol=0.0002, atol=2e-05, dtype='torch.float32'), 'pointer_dtypes': {'X_ptr': 'float32', 'Y_ptr': 'int64', 'loss_ptr': 'float32', 'ce_stats_ptr': 'float32'}, 'buffer_extents': {'X_ptr': rows * cols, 'Y_ptr': rows, 'loss_ptr': rows, 'ce_stats_ptr': 3}, 'buffer_layouts': _layouts(args), 'alignment': 64, 'aliases': {}, 'seed': int(seed), 'shape': tuple(shape), 'dtype': 'torch.float32', 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'coverage': {'complete_logical_output': True, 'grid_formula': '(n_rows,)', 'output': 'loss_ptr[0:n_rows]'}}

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
