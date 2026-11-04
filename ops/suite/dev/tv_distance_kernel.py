"""One-JIT standalone Triton compiler test case."""

COPIED_FROM = {'repo': 'ops-pool/smoke', 'note': 'validated case layer intact; lottery 20261019'}
OPERATOR = {"name": "hidden/tv_distance_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def _tv_distance_kernel(p_ptr, p_stride, q_ptr, q_stride, loss_ptr, loss_stride, grads_ptr, grads_stride, label_ptr, ignore_index: tl.constexpr, n_cols, total_rows: tl.constexpr, BLOCK_SIZE: tl.constexpr, HAS_LABEL: tl.constexpr, reduction: tl.constexpr='batchmean'):
    thread_id = tl.program_id(0)
    num_threads = tl.num_programs(0)
    for pid in tl.range(thread_id, total_rows, num_threads):
        p_row_ptr = p_ptr + pid * p_stride
        q_row_ptr = q_ptr + pid * q_stride
        loss_row_ptr = loss_ptr + pid * loss_stride
        grads_row_ptr = grads_ptr + pid * grads_stride
        label_row_ptr = label_ptr + pid
        base_offsets = tl.arange(0, BLOCK_SIZE)
        should_skip = False
        if HAS_LABEL:
            label = tl.load(label_row_ptr)
            if label == ignore_index:
                should_skip = True
        if should_skip:
            for i in range(0, n_cols, BLOCK_SIZE):
                offsets = i + base_offsets
                mask = offsets < n_cols
                tl.store(grads_row_ptr + offsets, 0.0, mask=mask)
                if reduction == 'none':
                    tl.store(loss_row_ptr + offsets, 0.0, mask=mask)
        else:
            loss_sum = 0.0
            for i in range(0, n_cols, BLOCK_SIZE):
                offsets = i + base_offsets
                mask = offsets < n_cols
                p = tl.load(p_row_ptr + offsets, mask=mask, other=0.0)
                q = tl.load(q_row_ptr + offsets, mask=mask, other=0.0)
                tv_loss = 0.5 * tl.abs(p - q)
                grad_res = tl.where(p > q, 0.5, -0.5)
                tl.store(grads_row_ptr + offsets, grad_res, mask=mask)
                if reduction == 'none':
                    tl.store(loss_row_ptr + offsets, tv_loss, mask=mask)
                else:
                    loss_sum += tl.sum(tv_loss, axis=0)
            if reduction != 'none':
                tl.store(loss_row_ptr, loss_sum)
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
SHAPES = ((1, 17), (21, 17))

DTYPES = ('float32', 'float16', 'bfloat16')
FIXED_META = {"ignore_index": -100, "BLOCK_SIZE": 128, "HAS_LABEL": True, "reduction": "none"}
LAUNCH_META = {"num_warps": 4, "num_stages": 1}


def ref(args, meta):
    import numpy as np
    p = np.asarray(args["p_ptr"], dtype=np.float32); q = np.asarray(args["q_ptr"], dtype=np.float32); labels = np.asarray(args["label_ptr"]); loss = 0.5 * np.abs(p - q); grads = np.where(p > q, 0.5, -0.5).astype(np.float32); ignored = labels == int(meta["ignore_index"]); loss[ignored] = 0.0; grads[ignored] = 0.0; return {"loss_ptr": loss.astype(np.float32), "grads_ptr": grads}


def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    del dtype
    import numpy as np
    (rows, cols) = (int(value) for value in shape)
    rng = fast_rng(seed)
    p = rng.uniform(0.0, 1.0, (rows, cols)).astype(np.float32)
    q = rng.uniform(0.0, 1.0, (rows, cols)).astype(np.float32)
    p /= p.sum(axis=1, keepdims=True)
    q /= q.sum(axis=1, keepdims=True)
    labels = np.zeros(rows, dtype=np.int64)
    labels[-1] = -100 if rows > 1 else 0
    args = {'p_ptr': _aligned(p, 'float32'), 'p_stride': cols, 'q_ptr': _aligned(q, 'float32'), 'q_stride': cols, 'loss_ptr': _aligned(np.full((rows, cols), -0.875), 'float32'), 'loss_stride': cols, 'grads_ptr': _aligned(np.full((rows, cols), -0.875), 'float32'), 'grads_stride': cols, 'label_ptr': _aligned(labels, 'int64'), 'n_cols': cols}
    meta = {**FIXED_META, 'total_rows': rows}
    outputs = ('loss_ptr', 'grads_ptr')
    return {'kernel': _tv_distance_kernel, 'grid': (min(rows, 4),), 'args': args, 'meta': meta, 'launch_meta': dict(LAUNCH_META), 'inputs': ('p_ptr', 'q_ptr', 'label_ptr'), 'outputs': outputs, 'expected': ref(args, meta), 'comparison': _comparison(outputs, dtype='torch.float32'), 'pointer_dtypes': {'p_ptr': 'float32', 'q_ptr': 'float32', 'loss_ptr': 'float32', 'grads_ptr': 'float32', 'label_ptr': 'int64'}, 'buffer_extents': {'p_ptr': rows * cols, 'q_ptr': rows * cols, 'loss_ptr': rows * cols, 'grads_ptr': rows * cols, 'label_ptr': rows}, 'buffer_layouts': _layouts(args), 'alignment': 64, 'aliases': {}, 'seed': int(seed), 'shape': tuple(shape), 'dtype': 'torch.float32', 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'coverage': {'complete_logical_output': True, 'grid_formula': '(min(total_rows,4),) with strided row loop', 'outputs': outputs}}

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
