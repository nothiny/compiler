"""One-JIT standalone Triton compiler test case."""

COPIED_FROM = {'repo': 'ops-pool/smoke', 'note': 'validated case layer intact; lottery 20261019'}
OPERATOR = {"name": "hidden/median_bool_reduce_counts_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["reduce"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def median_bool_reduce_counts_kernel(counts_in, counts_out, WIDTH: tl.constexpr, BLOCK: tl.constexpr):
    block_id = tl.program_id(0)
    offsets = block_id * BLOCK + tl.arange(0, BLOCK)
    valid = offsets < WIDTH
    block_counts = tl.load(counts_in + offsets, mask=valid, other=0)
    count = tl.sum(block_counts, axis=0)
    tl.store(counts_out + block_id, count)
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
SHAPES = ((17,), (109,))

DTYPES = ("torch.int64",)
FIXED_META = {"BLOCK": 128}
LAUNCH_META = {"num_warps": 4, "num_stages": 1}


def ref(args, meta):
    import numpy as np
    values = np.asarray(args["counts_in"], dtype=np.int64); block = int(meta["BLOCK"]); return {"counts_out": np.asarray([np.sum(values[start : start + block], dtype=np.int64) for start in range(0, values.size, block)], dtype=np.int64)}


def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    del dtype
    import numpy as np
    width = int(tuple(shape)[0])
    rng = fast_rng(seed)
    meta = dict(FIXED_META)
    blocks = (width + meta['BLOCK'] - 1) // meta['BLOCK']
    args = {'counts_in': _aligned(rng.integers(0, 128, width), 'int64'), 'counts_out': _aligned(np.full(blocks, -7), 'int64')}
    meta['WIDTH'] = width
    outputs = ('counts_out',)
    return {'kernel': median_bool_reduce_counts_kernel, 'grid': (blocks,), 'args': args, 'meta': meta, 'launch_meta': dict(LAUNCH_META), 'inputs': ('counts_in',), 'outputs': outputs, 'expected': ref(args, meta), 'comparison': _comparison(outputs, exact=True, dtype='torch.int64'), 'pointer_dtypes': {'counts_in': 'int64', 'counts_out': 'int64'}, 'buffer_extents': {'counts_in': width, 'counts_out': blocks}, 'buffer_layouts': _layouts(args), 'alignment': 64, 'aliases': {}, 'seed': int(seed), 'shape': (width,), 'dtype': 'torch.int64', 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'coverage': {'complete_logical_output': True, 'grid_formula': '(ceil_div(WIDTH,BLOCK),)', 'output': 'counts_out[0:grid0]'}}

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
