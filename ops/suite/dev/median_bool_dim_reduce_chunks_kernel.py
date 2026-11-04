"""One-JIT standalone Triton compiler test case."""

COPIED_FROM = {'repo': 'ops-pool/smoke', 'note': 'validated case layer intact; lottery 20261019'}
OPERATOR = {"name": "hidden/median_bool_dim_reduce_chunks_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["reduce"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def median_bool_dim_reduce_chunks_kernel(counts_in, first_false_in, first_true_in, counts_out, first_false_out, first_true_out, input_chunks: tl.constexpr, output_chunks: tl.constexpr, BLOCK: tl.constexpr):
    row = tl.program_id(0)
    out_chunk = tl.program_id(1)
    chunk_offsets = out_chunk * BLOCK + tl.arange(0, BLOCK)
    valid = chunk_offsets < input_chunks
    in_base = row * input_chunks + chunk_offsets
    counts = tl.load(counts_in + in_base, mask=valid, other=0)
    first_false = tl.load(first_false_in + in_base, mask=valid, other=9223372036854775807)
    first_true = tl.load(first_true_in + in_base, mask=valid, other=9223372036854775807)
    true_count = tl.sum(counts, axis=0)
    first_false_idx = tl.min(first_false, axis=0)
    first_true_idx = tl.min(first_true, axis=0)
    out_base = row * output_chunks + out_chunk
    tl.store(counts_out + out_base, true_count)
    tl.store(first_false_out + out_base, first_false_idx)
    tl.store(first_true_out + out_base, first_true_idx)
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
SHAPES = ((3, 17), (15, 17))

DTYPES = ("torch.int64",)
FIXED_META = {"BLOCK": 128}
LAUNCH_META = {"num_warps": 4, "num_stages": 1}


def ref(args, meta):
    import numpy as np
    counts = np.asarray(args["counts_in"], dtype=np.int64); ff = np.asarray(args["first_false_in"], dtype=np.int64); ft = np.asarray(args["first_true_in"], dtype=np.int64); rows, input_chunks = counts.shape; block = int(meta["BLOCK"]); output_chunks = int(meta["output_chunks"]); co = np.empty((rows, output_chunks), dtype=np.int64); fo = np.empty_like(co); to = np.empty_like(co)
    for out_chunk in range(output_chunks):
        sl = slice(out_chunk * block, min(input_chunks, (out_chunk + 1) * block)); co[:, out_chunk] = counts[:, sl].sum(axis=1, dtype=np.int64); fo[:, out_chunk] = ff[:, sl].min(axis=1); to[:, out_chunk] = ft[:, sl].min(axis=1)
    return {"counts_out": co, "first_false_out": fo, "first_true_out": to}


def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    del dtype
    import numpy as np
    (rows, input_chunks) = (int(value) for value in shape)
    rng = fast_rng(seed)
    meta = dict(FIXED_META)
    output_chunks = (input_chunks + meta['BLOCK'] - 1) // meta['BLOCK']
    counts = rng.integers(0, 128, (rows, input_chunks), dtype=np.int64)
    ff = rng.integers(0, 4096, (rows, input_chunks), dtype=np.int64)
    ft = rng.integers(0, 4096, (rows, input_chunks), dtype=np.int64)
    args = {'counts_in': _aligned(counts, 'int64'), 'first_false_in': _aligned(ff, 'int64'), 'first_true_in': _aligned(ft, 'int64'), 'counts_out': _aligned(np.full((rows, output_chunks), -7), 'int64'), 'first_false_out': _aligned(np.full((rows, output_chunks), -7), 'int64'), 'first_true_out': _aligned(np.full((rows, output_chunks), -7), 'int64')}
    meta.update({'input_chunks': input_chunks, 'output_chunks': output_chunks})
    outputs = ('counts_out', 'first_false_out', 'first_true_out')
    return {'kernel': median_bool_dim_reduce_chunks_kernel, 'grid': (rows, output_chunks), 'args': args, 'meta': meta, 'launch_meta': dict(LAUNCH_META), 'inputs': ('counts_in', 'first_false_in', 'first_true_in'), 'outputs': outputs, 'expected': ref(args, meta), 'comparison': _comparison(outputs, exact=True, dtype='torch.int64'), 'pointer_dtypes': {name: 'int64' for name in args}, 'buffer_extents': {name: int(value.size) for (name, value) in args.items()}, 'buffer_layouts': _layouts(args), 'alignment': 64, 'aliases': {}, 'seed': int(seed), 'shape': tuple(shape), 'dtype': 'torch.int64', 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'coverage': {'complete_logical_output': True, 'grid_formula': '(rows,ceil_div(input_chunks,BLOCK))', 'outputs': outputs}}

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
