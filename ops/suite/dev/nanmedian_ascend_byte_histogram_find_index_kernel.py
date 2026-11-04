"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/nanmedian_ascend_byte_histogram_find_index_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def nanmedian_ascend_byte_histogram_find_index_kernel(inp, state, out_values, out_indices, M, N: tl.constexpr, BLOCK_N: tl.constexpr):
    pid = tl.program_id(0).to(tl.int64)
    offsets = tl.arange(0, BLOCK_N)
    dtype = inp.dtype.element_ty
    nbits: tl.constexpr = dtype.primitive_bitwidth
    utype = tl.dtype(f'uint{nbits}')
    desired = tl.load(state + pid * 3 + 0).to(utype)
    result_idx = tl.full((), N, dtype=tl.int32)
    for start in tl.range(0, N, BLOCK_N):
        cols = start + offsets
        mask = cols < N
        vals = tl.load(inp + pid * N + cols, mask=mask, other=0)
        _inl_2_to_order_key_vals = vals
        _inl_2_to_order_key_valid = mask
        _inl_2_to_order_key_dtype = _inl_2_to_order_key_vals.dtype
        _inl_2_to_order_key_nbits: tl.constexpr = _inl_2_to_order_key_dtype.primitive_bitwidth
        _inl_2_to_order_key_utype = tl.dtype(f'uint{_inl_2_to_order_key_nbits}')
        _inl_2_to_order_key_top_mask: tl.constexpr = 1 << _inl_2_to_order_key_nbits - 1
        _inl_2_to_order_key_full_mask: tl.constexpr = (1 << _inl_2_to_order_key_nbits) - 1
        _inl_2_to_order_key_full = tl.full(_inl_2_to_order_key_vals.shape, _inl_2_to_order_key_full_mask, dtype=_inl_2_to_order_key_utype)
        if _inl_2_to_order_key_dtype.is_floating():
            _inl_2_to_order_key_bits = _inl_2_to_order_key_vals.to(_inl_2_to_order_key_utype, bitcast=True)
            _inl_2_to_order_key_sign_mask = tl.where(_inl_2_to_order_key_bits & _inl_2_to_order_key_top_mask != 0, _inl_2_to_order_key_full_mask, _inl_2_to_order_key_top_mask)
            _inl_2_to_order_key_key = _inl_2_to_order_key_bits ^ _inl_2_to_order_key_sign_mask
        elif _inl_2_to_order_key_dtype.is_int_signed():
            _inl_2_to_order_key_bits = _inl_2_to_order_key_vals.to(_inl_2_to_order_key_utype, bitcast=True)
            _inl_2_to_order_key_key = _inl_2_to_order_key_bits ^ _inl_2_to_order_key_top_mask
        else:
            _inl_2_to_order_key_key = _inl_2_to_order_key_vals.to(_inl_2_to_order_key_utype)
        _inl_2_to_order_key_result = tl.where(_inl_2_to_order_key_valid, _inl_2_to_order_key_key, _inl_2_to_order_key_full)
        keys = _inl_2_to_order_key_result
        local_idx = tl.min(tl.where(mask & (keys == desired), cols, N), axis=0)
        result_idx = tl.where(local_idx < result_idx, local_idx, result_idx)
    result_val = tl.load(inp + pid * N + result_idx)
    tl.store(out_values + pid, result_val)
    tl.store(out_indices + pid, result_idx)
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
 M=int(args["M"]);C=int(meta["N"]);x=np.asarray(args["inp"],np.int32).reshape(M,C);keys=x.view(np.uint32)^np.uint32(0x80000000);desired=np.asarray(args["state"],np.int64).reshape(M,3)[:,0].astype(np.uint32);idx=np.asarray([np.flatnonzero(keys[r]==desired[r])[0] for r in range(M)],np.int32);return {"out_values":x[np.arange(M),idx],"out_indices":idx}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 M=3;C=max(3,N);x=rng.integers(-1000,1001,(M,C),dtype=np.int32);rank=(C-1)//2;vals=np.sort(x,axis=1,kind="stable")[:,rank];keys=x.view(np.uint32)^np.uint32(0x80000000);idx=np.asarray([np.flatnonzero(x[r]==vals[r])[0] for r in range(M)]);state=np.zeros((M,3),np.int64);state[:,0]=keys[np.arange(M),idx].astype(np.int64);args={"inp":_aligned(x,"int32"),"state":_aligned(state,"int64"),"out_values":_aligned(np.full(M,-1),"int32"),"out_indices":_aligned(np.full(M,-1),"int32"),"M":M};meta={"N":C,"BLOCK_N":128};grid=(M,)
 outputs=('out_values', 'out_indices');return _case(nanmedian_ascend_byte_histogram_find_index_kernel,grid,args,meta,('inp', 'state'),outputs,ref(args,meta),shape,"torch.float32",seed,{"complete_launch_plan":True,"formula":'first source index and value matching each fully selected order key'})

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
