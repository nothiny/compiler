"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/local_ne_flat_impl", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def local_ne_flat_impl(global_pid, sorted_data_ptr: tl.tensor, ne_result_ptr: tl.tensor, tile_sum_ptr: tl.tensor, global_ctas_num: int, num_tasks: int, tile_size: tl.constexpr):
    r = tl.arange(0, tile_size)
    i0 = global_pid * tile_size + r
    mask = i0 < num_tasks
    i0_prev = tl.where(i0 > 0, i0 - 1, 0)
    a = tl.load(sorted_data_ptr + i0, mask=mask)
    b = tl.load(sorted_data_ptr + i0_prev, mask=mask)
    ne_result = tl.where(i0 > 0, a != b, 0)
    tl.store(ne_result_ptr + i0, ne_result, mask=mask)
    tile_sum = tl.sum(ne_result)
    tile_sum_mask = global_pid < global_ctas_num
    tl.store(tile_sum_ptr + global_pid, tile_sum, mask=tile_sum_mask)
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
SHAPES=((17,), (97,));DTYPES=('torch.int32',)
def ref(args,meta):
 import numpy as np
 x=np.asarray(args["sorted_data_ptr"])[:int(args["num_tasks"])];ne=np.empty(x.size,np.int32);ne[0]=0;ne[1:]=(x[1:]!=x[:-1]).astype(np.int32);tile=int(meta["tile_size"]);sums=np.asarray([ne[s:min(s+tile,ne.size)].sum() for s in range(0,ne.size,tile)],np.int64);return {"ne_result_ptr":ne,"tile_sum_ptr":sums}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 T=max(3,N);tile=1<<(T-1).bit_length();x=np.sort(rng.integers(0,max(3,T//4),T,dtype=np.int32));args={"global_pid":0,"sorted_data_ptr":_aligned(x,"int32"),"ne_result_ptr":_aligned(np.full(T,-1),"int32"),"tile_sum_ptr":_aligned(np.full(1,-1),"int64"),"global_ctas_num":1,"num_tasks":T};meta={"tile_size":tile};grid=(1,)
 outputs=('ne_result_ptr', 'tile_sum_ptr');return _case(local_ne_flat_impl,grid,args,meta,('sorted_data_ptr',),outputs,ref(args,meta),shape,"torch.float32",seed,{"complete_launch_plan":True,"formula":'one explicit unique-flat tile: adjacent-change markers (first marker zero) and tile sum'})

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
