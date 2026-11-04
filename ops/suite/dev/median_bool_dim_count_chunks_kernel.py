"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/median_bool_dim_count_chunks_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def median_bool_dim_count_chunks_kernel(inp, counts, first_false, first_true, total_outputs, reduction_size, inner_size, chunks_per_output: tl.constexpr, BLOCK: tl.constexpr):
    pid = tl.program_id(0)
    out_offset = pid // chunks_per_output
    chunk_id = pid - out_offset * chunks_per_output
    out_mask = out_offset < total_outputs
    inner_offset = out_offset % inner_size
    outer_offset = out_offset // inner_size
    cols = chunk_id * BLOCK + tl.arange(0, BLOCK)
    valid = (cols < reduction_size) & out_mask
    ptrs = inp + outer_offset * reduction_size * inner_size + cols * inner_size + inner_offset
    data = tl.load(ptrs, mask=valid, other=False)
    true_mask = valid & data
    false_mask = valid & ~data
    true_count = tl.sum(true_mask.to(tl.int64), axis=0)
    first_false_idx = tl.min(tl.where(false_mask, cols, reduction_size), axis=0)
    first_true_idx = tl.min(tl.where(true_mask, cols, reduction_size), axis=0)
    tl.store(counts + pid, true_count)
    tl.store(first_false + pid, first_false_idx.to(tl.int64))
    tl.store(first_true + pid, first_true_idx.to(tl.int64))
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
SHAPES = ((2, 17, 3), (4, 97, 7))
DTYPES = ("torch.bool",)
FIXED_META = {"BLOCK": 128}
LAUNCH_META = {"num_warps": 4, "num_stages": 1}


def ref(args, meta):
    import numpy as np
    x = np.asarray(args["inp"], dtype=np.bool_); outer, reduction, inner = x.shape; chunks = int(meta["chunks_per_output"]); block = int(meta["BLOCK"]); counts = np.zeros((outer * inner, chunks), dtype=np.int64); first_false = np.full_like(counts, reduction); first_true = np.full_like(counts, reduction)
    for o in range(outer):
        for i in range(inner):
            row_id = o * inner + i
            for chunk in range(chunks):
                start, stop = chunk * block, min(reduction, (chunk + 1) * block); values = x[o, start:stop, i]; counts[row_id, chunk] = np.count_nonzero(values); f = np.flatnonzero(~values); t = np.flatnonzero(values); first_false[row_id, chunk] = reduction if not f.size else start + int(f[0]); first_true[row_id, chunk] = reduction if not t.size else start + int(t[0])
    return {"counts": counts.reshape(-1), "first_false": first_false.reshape(-1), "first_true": first_true.reshape(-1)}


def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    del dtype
    import numpy as np
    (outer, reduction, inner) = (int(value) for value in shape)
    rng = fast_rng(seed)
    meta = dict(FIXED_META)
    chunks = (reduction + meta['BLOCK'] - 1) // meta['BLOCK']
    total = outer * inner
    x = rng.integers(0, 2, outer * reduction * inner).astype(np.bool_).reshape(outer, reduction, inner)
    args = {'inp': _aligned(x, 'bool'), 'counts': _aligned(np.full(total * chunks, -7), 'int64'), 'first_false': _aligned(np.full(total * chunks, -7), 'int64'), 'first_true': _aligned(np.full(total * chunks, -7), 'int64'), 'total_outputs': total, 'reduction_size': reduction, 'inner_size': inner}
    meta['chunks_per_output'] = chunks
    outputs = ('counts', 'first_false', 'first_true')
    return {'kernel': median_bool_dim_count_chunks_kernel, 'grid': (total * chunks,), 'args': args, 'meta': meta, 'launch_meta': dict(LAUNCH_META), 'inputs': ('inp',), 'outputs': outputs, 'expected': ref(args, meta), 'comparison': _comparison(outputs, exact=True, dtype='torch.bool'), 'pointer_dtypes': {'inp': 'bool', 'counts': 'int64', 'first_false': 'int64', 'first_true': 'int64'}, 'buffer_extents': {'inp': outer * reduction * inner, 'counts': total * chunks, 'first_false': total * chunks, 'first_true': total * chunks}, 'buffer_layouts': _layouts(args), 'alignment': 64, 'aliases': {}, 'seed': int(seed), 'shape': tuple(shape), 'dtype': 'torch.bool', 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'coverage': {'complete_logical_output': True, 'grid_formula': '(total_outputs*chunks_per_output,)', 'outputs': outputs}}

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
