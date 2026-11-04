"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/median_bool_dim_finish_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def median_bool_dim_finish_kernel(counts, first_false, first_true, values, indices, reduction_size, chunks_per_output: tl.constexpr, BLOCK: tl.constexpr):
    row = tl.program_id(0)
    chunk_offsets = tl.arange(0, BLOCK)
    valid = chunk_offsets < chunks_per_output
    base = row * chunks_per_output + chunk_offsets
    block_counts = tl.load(counts + base, mask=valid, other=0)
    true_count = tl.sum(block_counts, axis=0)
    false_count = reduction_size - true_count
    rank = (reduction_size - 1) // 2
    median_value = rank >= false_count
    false_indices = tl.load(first_false + base, mask=valid, other=9223372036854775807)
    true_indices = tl.load(first_true + base, mask=valid, other=9223372036854775807)
    first_false_idx = tl.min(false_indices, axis=0)
    first_true_idx = tl.min(true_indices, axis=0)
    first_match = tl.where(median_value, first_true_idx, first_false_idx)
    tl.store(values + row, median_value)
    tl.store(indices + row, first_match)
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
SHAPES = ((3, 5, 17), (17, 33, 97))
DTYPES = ("torch.int64",)
FIXED_META = {"BLOCK": 64}
LAUNCH_META = {"num_warps": 4, "num_stages": 1}


def ref(args, meta):
    import numpy as np
    counts = np.asarray(args["counts"]); ff = np.asarray(args["first_false"]); ft = np.asarray(args["first_true"]); reduction = int(args["reduction_size"]); true_count = counts.sum(axis=1, dtype=np.int64); median = (reduction - 1) // 2 >= reduction - true_count; index = np.where(median, ft.min(axis=1), ff.min(axis=1)); return {"values": median.astype(np.bool_), "indices": index.astype(np.int64)}


def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    del dtype
    import numpy as np
    (rows, chunks, reduction) = (int(value) for value in shape)
    rng = fast_rng(seed)
    counts = rng.multinomial(reduction, np.full(chunks, 1.0 / chunks), size=rows).astype(np.int64)
    ff = rng.integers(0, reduction, (rows, chunks), dtype=np.int64)
    ft = rng.integers(0, reduction, (rows, chunks), dtype=np.int64)
    args = {'counts': _aligned(counts, 'int64'), 'first_false': _aligned(ff, 'int64'), 'first_true': _aligned(ft, 'int64'), 'values': _aligned(np.zeros(rows), 'bool'), 'indices': _aligned(np.full(rows, -7), 'int64'), 'reduction_size': reduction}
    meta = {'chunks_per_output': chunks, **FIXED_META}
    outputs = ('values', 'indices')
    return {'kernel': median_bool_dim_finish_kernel, 'grid': (rows,), 'args': args, 'meta': meta, 'launch_meta': dict(LAUNCH_META), 'inputs': ('counts', 'first_false', 'first_true'), 'outputs': outputs, 'expected': ref(args, meta), 'comparison': _comparison(outputs, exact=True, dtype='torch.int64'), 'pointer_dtypes': {'counts': 'int64', 'first_false': 'int64', 'first_true': 'int64', 'values': 'bool', 'indices': 'int64'}, 'buffer_extents': {name: int(value.size) for (name, value) in args.items() if hasattr(value, 'size')}, 'buffer_layouts': _layouts(args), 'alignment': 64, 'aliases': {}, 'seed': int(seed), 'shape': tuple(shape), 'dtype': 'torch.int64', 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'coverage': {'complete_logical_output': True, 'grid_formula': '(rows,)', 'outputs': outputs}}

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
