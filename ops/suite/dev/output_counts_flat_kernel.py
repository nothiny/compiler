"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/output_counts_flat_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def output_counts_flat_kernel(idx_ptr: tl.tensor, origin_num_tasks: int, counts_ptr: tl.tensor, num_tasks: int, tiles_per_cta: int, tile_size: tl.constexpr):
    pid = tl.program_id(0).to(tl.int64)
    _inl_2_num_programs_axis: tl.constexpr = 0
    _inl_2_num_programs_result = tl.num_programs(_inl_2_num_programs_axis).to(tl.int64)
    ctas_num = _inl_2_num_programs_result
    for j in range(0, tiles_per_cta):
        global_pid = pid + j * ctas_num
        _inl_3_output_counts_flat_impl_global_pid = global_pid
        _inl_3_output_counts_flat_impl_idx_ptr = idx_ptr
        _inl_3_output_counts_flat_impl_origin_num_tasks = origin_num_tasks
        _inl_3_output_counts_flat_impl_counts_ptr = counts_ptr
        _inl_3_output_counts_flat_impl_num_tasks = num_tasks
        _inl_3_output_counts_flat_impl_tile_size: tl.constexpr = tile_size
        _inl_3_output_counts_flat_impl_r = tl.arange(0, _inl_3_output_counts_flat_impl_tile_size)
        _inl_3_output_counts_flat_impl_i0 = _inl_3_output_counts_flat_impl_global_pid * _inl_3_output_counts_flat_impl_tile_size + _inl_3_output_counts_flat_impl_r
        _inl_3_output_counts_flat_impl_mask = _inl_3_output_counts_flat_impl_i0 < _inl_3_output_counts_flat_impl_num_tasks
        _inl_3_output_counts_flat_impl_idx = tl.load(_inl_3_output_counts_flat_impl_idx_ptr + _inl_3_output_counts_flat_impl_i0, mask=_inl_3_output_counts_flat_impl_mask)
        _inl_3_output_counts_flat_impl_i0_next = _inl_3_output_counts_flat_impl_i0 + 1
        _inl_3_output_counts_flat_impl_next_mask = _inl_3_output_counts_flat_impl_i0_next < _inl_3_output_counts_flat_impl_num_tasks
        _inl_3_output_counts_flat_impl_idx_next = tl.load(_inl_3_output_counts_flat_impl_idx_ptr + _inl_3_output_counts_flat_impl_i0_next, mask=_inl_3_output_counts_flat_impl_next_mask)
        _inl_3_output_counts_flat_impl_counts = tl.where(_inl_3_output_counts_flat_impl_i0_next < _inl_3_output_counts_flat_impl_num_tasks, _inl_3_output_counts_flat_impl_idx_next - _inl_3_output_counts_flat_impl_idx, _inl_3_output_counts_flat_impl_origin_num_tasks - _inl_3_output_counts_flat_impl_idx)
        tl.store(_inl_3_output_counts_flat_impl_counts_ptr + _inl_3_output_counts_flat_impl_i0, _inl_3_output_counts_flat_impl_counts, mask=_inl_3_output_counts_flat_impl_mask)
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
SHAPES=((17,), (97,));DTYPES=('torch.int64',)
def ref(args,meta):
 import numpy as np
 idx=np.asarray(args["idx_ptr"],np.int64)[:int(args["num_tasks"])];tail=np.asarray([int(args["origin_num_tasks"])],np.int64);return {"counts_ptr":np.diff(np.concatenate((idx,tail))).astype(np.int64)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 origin=max(5,N);idx=np.arange(0,origin,3,dtype=np.int64);M=idx.size;tile=128;tiles=(M+tile-1)//tile;per=2;ctas=(tiles+per-1)//per;args={"idx_ptr":_aligned(idx,"int64"),"origin_num_tasks":origin,"counts_ptr":_aligned(np.full(M,-1),"int64"),"num_tasks":M,"tiles_per_cta":per};meta={"tile_size":tile};grid=(ctas,)
 outputs=('counts_ptr',);return _case(output_counts_flat_kernel,grid,args,meta,('idx_ptr',),outputs,ref(args,meta),shape,"torch.float32",seed,{"complete_launch_plan":True,"formula":'run lengths from successive unique-start indices'})

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
