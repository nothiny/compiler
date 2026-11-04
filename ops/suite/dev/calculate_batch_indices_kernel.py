"""One-JIT standalone Triton compiler test case."""

COPIED_FROM = {'repo': 'ops-pool/flaggems', 'note': 'validated case layer intact; lottery 20261019'}
OPERATOR = {"name": "hidden/calculate_batch_indices_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def calculate_batch_indices_kernel(batch_indices_ptr, a_batch0: tl.int64, a_batch1: tl.int64, b_batch0: tl.int64, b_batch1: tl.int64, out_batch0: tl.int64, out_batch1: tl.int64, BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(axis=0)
    offset = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    out_indice1 = offset % out_batch1
    remaining = offset // out_batch1
    out_indice0 = remaining % out_batch0
    a_idx = out_indice0 // b_batch0
    a_idx = a_idx * a_batch1 + out_indice1 // b_batch1
    b_idx = out_indice0 % b_batch0
    b_idx = b_idx * b_batch1 + out_indice1 % b_batch1
    a_store_offset = 2 * offset
    b_store_offset = 2 * offset + 1
    tl.store(batch_indices_ptr + a_store_offset, a_idx, mask=offset < out_batch0 * out_batch1)
    tl.store(batch_indices_ptr + b_store_offset, b_idx, mask=offset < out_batch0 * out_batch1)
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
SHAPES = ((17,), (5, 3, 2, 2));DTYPES = ('torch.int64',)

def ref(args,meta):
 import numpy as np
 total=int(args["out_batch0"])*int(args["out_batch1"]);o=np.arange(total);o1=o%int(args["out_batch1"]);o0=(o//int(args["out_batch1"]))%int(args["out_batch0"]);a=(o0//int(args["b_batch0"]))*int(args["a_batch1"])+o1//int(args["b_batch1"]);b=(o0%int(args["b_batch0"]))*int(args["b_batch1"])+o1%int(args["b_batch1"]);return {"batch_indices_ptr":np.stack((a,b),axis=1).astype(np.int64).reshape(-1)}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    if len(shape) > 1 and tuple(shape) not in SHAPES:
        raise ValueError('unsupported explicit shape configuration')
    del dtype
    import numpy as np
    N = int(shape[0])
    rng = fast_rng(seed)
    a0 = int(shape[0]) if len(shape) > 1 else 2
    a1 = int(shape[1]) if len(shape) > 1 else 3
    b0 = int(shape[2]) if len(shape) > 1 else 2
    b1 = int(shape[3]) if len(shape) > 1 else 2
    o0 = a0 * b0
    o1 = a1 * b1
    T = o0 * o1
    args = {'batch_indices_ptr': _aligned(np.full(T * 2, -1), 'int64'), 'a_batch0': a0, 'a_batch1': a1, 'b_batch0': b0, 'b_batch1': b1, 'out_batch0': o0, 'out_batch1': o1}
    meta = {'BLOCK_SIZE': 128}
    grid = ((T + 127) // 128,)
    outputs = ('batch_indices_ptr',)
    return _case(calculate_batch_indices_kernel, grid, args, meta, (), outputs, ref(args, meta), shape, 'torch.int64', seed, {'complete_launch_plan': True, 'formula': 'Kronecker broadcast batch-index pairs'})

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
