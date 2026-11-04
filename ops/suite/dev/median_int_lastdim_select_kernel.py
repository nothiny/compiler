"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/median_int_lastdim_select_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def median_int_lastdim_select_kernel(row_data, values, indices, WIDTH: tl.constexpr, BLOCK: tl.constexpr, SEARCH_STEPS: tl.constexpr):
    row = tl.program_id(0)
    cols = tl.arange(0, BLOCK)
    valid = cols < WIDTH
    base = row_data + row * WIDTH
    data = tl.load(base + cols, mask=valid, other=0)
    dtype = row_data.dtype.element_ty
    _inl_1_get_iinfo_val_dtype = dtype
    _inl_1_get_iinfo_val_return_max: tl.constexpr = True
    _inl_1_get_iinfo_val_result = 0
    if _inl_1_get_iinfo_val_return_max:
        _inl_2_get_dtype_max_dtype = _inl_1_get_iinfo_val_dtype
        _inl_2_get_dtype_max_result = 0
        'get a value which is greater that all other values of that dtype'
        _inl_2_get_dtype_max_dtype_ = _inl_2_get_dtype_max_dtype
        if _inl_2_get_dtype_max_dtype_.is_floating():
            _inl_2_get_dtype_max_value: tl.constexpr = float('inf')
            _inl_2_get_dtype_max_result = _inl_2_get_dtype_max_value
        elif _inl_2_get_dtype_max_dtype_.is_int_signed():
            _inl_2_get_dtype_max_width: tl.constexpr = _inl_2_get_dtype_max_dtype_.int_bitwidth
            _inl_2_get_dtype_max_value: tl.constexpr = 2 ** (_inl_2_get_dtype_max_width - 1) - 1
            _inl_2_get_dtype_max_result = _inl_2_get_dtype_max_value
        elif _inl_2_get_dtype_max_dtype_.is_int_unsigned():
            _inl_2_get_dtype_max_width: tl.constexpr = _inl_2_get_dtype_max_dtype_.int_bitwidth
            _inl_2_get_dtype_max_value: tl.constexpr = 2 ** _inl_2_get_dtype_max_width - 1
            _inl_2_get_dtype_max_result = _inl_2_get_dtype_max_value
        _inl_1_get_iinfo_val_result = _inl_2_get_dtype_max_result
    else:
        _inl_3_get_dtype_min_dtype = _inl_1_get_iinfo_val_dtype
        _inl_3_get_dtype_min_result = 0
        'get a value which is less that all other values of that dtype'
        _inl_3_get_dtype_min_dtype_ = _inl_3_get_dtype_min_dtype
        if _inl_3_get_dtype_min_dtype_.is_floating():
            _inl_3_get_dtype_min_value: tl.constexpr = float('-inf')
            _inl_3_get_dtype_min_result = _inl_3_get_dtype_min_value
        elif _inl_3_get_dtype_min_dtype_.is_int_signed():
            _inl_3_get_dtype_min_width: tl.constexpr = _inl_3_get_dtype_min_dtype_.int_bitwidth
            _inl_3_get_dtype_min_value: tl.constexpr = -1 * 2 ** (_inl_3_get_dtype_min_width - 1)
            _inl_3_get_dtype_min_result = _inl_3_get_dtype_min_value
        elif _inl_3_get_dtype_min_dtype_.is_int_unsigned():
            _inl_3_get_dtype_min_value: tl.constexpr = 0
            _inl_3_get_dtype_min_result = _inl_3_get_dtype_min_value
        _inl_1_get_iinfo_val_result = _inl_3_get_dtype_min_result
    high = _inl_1_get_iinfo_val_result
    _inl_4_get_iinfo_val_dtype = dtype
    _inl_4_get_iinfo_val_return_max: tl.constexpr = False
    _inl_4_get_iinfo_val_result = 0
    if _inl_4_get_iinfo_val_return_max:
        _inl_5_get_dtype_max_dtype = _inl_4_get_iinfo_val_dtype
        _inl_5_get_dtype_max_result = 0
        'get a value which is greater that all other values of that dtype'
        _inl_5_get_dtype_max_dtype_ = _inl_5_get_dtype_max_dtype
        if _inl_5_get_dtype_max_dtype_.is_floating():
            _inl_5_get_dtype_max_value: tl.constexpr = float('inf')
            _inl_5_get_dtype_max_result = _inl_5_get_dtype_max_value
        elif _inl_5_get_dtype_max_dtype_.is_int_signed():
            _inl_5_get_dtype_max_width: tl.constexpr = _inl_5_get_dtype_max_dtype_.int_bitwidth
            _inl_5_get_dtype_max_value: tl.constexpr = 2 ** (_inl_5_get_dtype_max_width - 1) - 1
            _inl_5_get_dtype_max_result = _inl_5_get_dtype_max_value
        elif _inl_5_get_dtype_max_dtype_.is_int_unsigned():
            _inl_5_get_dtype_max_width: tl.constexpr = _inl_5_get_dtype_max_dtype_.int_bitwidth
            _inl_5_get_dtype_max_value: tl.constexpr = 2 ** _inl_5_get_dtype_max_width - 1
            _inl_5_get_dtype_max_result = _inl_5_get_dtype_max_value
        _inl_4_get_iinfo_val_result = _inl_5_get_dtype_max_result
    else:
        _inl_6_get_dtype_min_dtype = _inl_4_get_iinfo_val_dtype
        _inl_6_get_dtype_min_result = 0
        'get a value which is less that all other values of that dtype'
        _inl_6_get_dtype_min_dtype_ = _inl_6_get_dtype_min_dtype
        if _inl_6_get_dtype_min_dtype_.is_floating():
            _inl_6_get_dtype_min_value: tl.constexpr = float('-inf')
            _inl_6_get_dtype_min_result = _inl_6_get_dtype_min_value
        elif _inl_6_get_dtype_min_dtype_.is_int_signed():
            _inl_6_get_dtype_min_width: tl.constexpr = _inl_6_get_dtype_min_dtype_.int_bitwidth
            _inl_6_get_dtype_min_value: tl.constexpr = -1 * 2 ** (_inl_6_get_dtype_min_width - 1)
            _inl_6_get_dtype_min_result = _inl_6_get_dtype_min_value
        elif _inl_6_get_dtype_min_dtype_.is_int_unsigned():
            _inl_6_get_dtype_min_value: tl.constexpr = 0
            _inl_6_get_dtype_min_result = _inl_6_get_dtype_min_value
        _inl_4_get_iinfo_val_result = _inl_6_get_dtype_min_result
    low = _inl_4_get_iinfo_val_result
    row_min = tl.min(tl.where(valid, data, high), axis=0).to(tl.int64)
    row_max = tl.max(tl.where(valid, data, low), axis=0).to(tl.int64)
    lo = row_min
    hi = row_max
    rank = (WIDTH - 1) // 2
    for _ in tl.static_range(0, SEARCH_STEPS):
        mid = lo + (hi - lo) // 2
        le_count = tl.sum((valid & (data <= mid.to(dtype))).to(tl.int32), axis=0)
        take_left = le_count > rank
        hi = tl.where(take_left, mid, hi)
        lo = tl.where(take_left, lo, mid + 1)
    median_value = lo.to(dtype)
    first_match = tl.argmax((valid & (data == median_value)).to(tl.int32), axis=0)
    tl.store(values + row, median_value)
    tl.store(indices + row, first_match.to(tl.int64))
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
 x=np.asarray(args["row_data"]).reshape(-1,int(meta["WIDTH"]));vals=[];inds=[]
 for row in x:
  nan=np.flatnonzero(np.isnan(row)) if row.dtype.kind=="f" else np.empty(0,np.int64)
  if nan.size:j=int(nan[0])
  else:
   value=np.sort(row,kind="stable")[(row.size-1)//2];j=int(np.flatnonzero(row==value)[0])
  vals.append(row[j]);inds.append(j)
 return {"values":np.asarray(vals,dtype=x.dtype),"indices":np.asarray(inds,np.int64)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 R=3;W=max(3,N);B=1<<(W-1).bit_length();x=rng.normal(0,.8,(R,W)).astype(np.dtype("int32"))
 if x.dtype.kind in "iu":x=rng.integers(-19,20,(R,W),dtype=x.dtype)
 else:x[0,1]=np.nan;x[1,0]=x[1,-1]
 args={"row_data":_aligned(x,"int32"),"values":_aligned(np.full(R,-7),"int32"),"indices":_aligned(np.full(R,-1),"int64")};meta={"WIDTH":W,"BLOCK":B,"SEARCH_STEPS":32};grid=(R,)
 outputs=('values', 'indices');return _case(median_int_lastdim_select_kernel,grid,args,meta,('row_data',),outputs,ref(args,meta),shape,"torch.float32",seed,{"complete_launch_plan":True,"formula":'row-wise lower median for int32 and first source index'})

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
