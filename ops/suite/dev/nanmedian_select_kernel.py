"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/nanmedian_select_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng
_MAX_BFLOAT16_VAL = tl.constexpr(3.3895313892515355e+38)
_MAX_FLOAT16_VAL = tl.constexpr(65504.0)
_MAX_FLOAT32_VAL = tl.constexpr(3.4028234663852886e+38)
_MIN_BFLOAT16_VAL = tl.constexpr(-3.3895313892515355e+38)
_MIN_FLOAT16_VAL = tl.constexpr(-65504.0)
_MIN_FLOAT32_VAL = tl.constexpr(-3.4028234663852886e+38)

@triton.jit
def nanmedian_select_kernel(inp, out_values, out_indices, M, N: tl.constexpr, BLOCK_N: tl.constexpr, USE_ISNAN: tl.constexpr):
    pid = tl.program_id(0).to(tl.int64)
    offsets = tl.arange(0, BLOCK_N)
    mask = offsets < N
    dtype = inp.dtype.element_ty
    if dtype.is_floating():
        _inl_2_get_finfo_val_dtype = dtype
        _inl_2_get_finfo_val_return_max: tl.constexpr = True
        _inl_2_get_finfo_val_result = 0
        if _inl_2_get_finfo_val_dtype is tl.float32:
            if _inl_2_get_finfo_val_return_max:
                _inl_2_get_finfo_val_result = _MAX_FLOAT32_VAL
            else:
                _inl_2_get_finfo_val_result = _MIN_FLOAT32_VAL
        elif _inl_2_get_finfo_val_dtype is tl.float16:
            if _inl_2_get_finfo_val_return_max:
                _inl_2_get_finfo_val_result = _MAX_FLOAT16_VAL
            else:
                _inl_2_get_finfo_val_result = _MIN_FLOAT16_VAL
        elif _inl_2_get_finfo_val_dtype is tl.bfloat16:
            if _inl_2_get_finfo_val_return_max:
                _inl_2_get_finfo_val_result = _MAX_BFLOAT16_VAL
            else:
                _inl_2_get_finfo_val_result = _MIN_BFLOAT16_VAL
        max_value = _inl_2_get_finfo_val_result
        _inl_3_get_finfo_val_dtype = dtype
        _inl_3_get_finfo_val_return_max: tl.constexpr = False
        _inl_3_get_finfo_val_result = 0
        if _inl_3_get_finfo_val_dtype is tl.float32:
            if _inl_3_get_finfo_val_return_max:
                _inl_3_get_finfo_val_result = _MAX_FLOAT32_VAL
            else:
                _inl_3_get_finfo_val_result = _MIN_FLOAT32_VAL
        elif _inl_3_get_finfo_val_dtype is tl.float16:
            if _inl_3_get_finfo_val_return_max:
                _inl_3_get_finfo_val_result = _MAX_FLOAT16_VAL
            else:
                _inl_3_get_finfo_val_result = _MIN_FLOAT16_VAL
        elif _inl_3_get_finfo_val_dtype is tl.bfloat16:
            if _inl_3_get_finfo_val_return_max:
                _inl_3_get_finfo_val_result = _MAX_BFLOAT16_VAL
            else:
                _inl_3_get_finfo_val_result = _MIN_BFLOAT16_VAL
        fallback_value = _inl_3_get_finfo_val_result
    else:
        _inl_4_get_dtype_max_dtype = dtype
        _inl_4_get_dtype_max_result = 0
        'get a value which is greater that all other values of that dtype'
        _inl_4_get_dtype_max_dtype_ = _inl_4_get_dtype_max_dtype.value
        if _inl_4_get_dtype_max_dtype_.is_floating():
            _inl_4_get_dtype_max_value: tl.constexpr = float('inf')
            _inl_4_get_dtype_max_result = _inl_4_get_dtype_max_value
        elif _inl_4_get_dtype_max_dtype_.is_int_signed():
            _inl_4_get_dtype_max_width: tl.constexpr = _inl_4_get_dtype_max_dtype_.int_bitwidth
            _inl_4_get_dtype_max_value: tl.constexpr = 2 ** (_inl_4_get_dtype_max_width - 1) - 1
            _inl_4_get_dtype_max_result = _inl_4_get_dtype_max_value
        elif _inl_4_get_dtype_max_dtype_.is_int_unsigned():
            _inl_4_get_dtype_max_width: tl.constexpr = _inl_4_get_dtype_max_dtype_.int_bitwidth
            _inl_4_get_dtype_max_value: tl.constexpr = 2 ** _inl_4_get_dtype_max_width - 1
            _inl_4_get_dtype_max_result = _inl_4_get_dtype_max_value
        max_value = _inl_4_get_dtype_max_result
        _inl_5_get_dtype_min_dtype = dtype
        _inl_5_get_dtype_min_result = 0
        'get a value which is less that all other values of that dtype'
        _inl_5_get_dtype_min_dtype_ = _inl_5_get_dtype_min_dtype.value
        if _inl_5_get_dtype_min_dtype_.is_floating():
            _inl_5_get_dtype_min_value: tl.constexpr = float('-inf')
            _inl_5_get_dtype_min_result = _inl_5_get_dtype_min_value
        elif _inl_5_get_dtype_min_dtype_.is_int_signed():
            _inl_5_get_dtype_min_width: tl.constexpr = _inl_5_get_dtype_min_dtype_.int_bitwidth
            _inl_5_get_dtype_min_value: tl.constexpr = -1 * 2 ** (_inl_5_get_dtype_min_width - 1)
            _inl_5_get_dtype_min_result = _inl_5_get_dtype_min_value
        elif _inl_5_get_dtype_min_dtype_.is_int_unsigned():
            _inl_5_get_dtype_min_value: tl.constexpr = 0
            _inl_5_get_dtype_min_result = _inl_5_get_dtype_min_value
        fallback_value = _inl_5_get_dtype_min_result
    vals = tl.load(inp + pid * N + offsets, mask=mask, other=max_value)
    if dtype.is_floating():
        _inl_6_is_not_nan_vals = vals
        _inl_6_is_not_nan_USE_ISNAN: tl.constexpr = USE_ISNAN
        _inl_6_is_not_nan_vals_fp32 = _inl_6_is_not_nan_vals.to(tl.float32)
        _inl_6_is_not_nan_result = _inl_6_is_not_nan_vals_fp32 == _inl_6_is_not_nan_vals_fp32
        valid = mask & _inl_6_is_not_nan_result
    else:
        valid = mask
    valid_count = tl.sum(valid.to(tl.int32), axis=0)
    median_rank = (valid_count - 1) // 2
    active = valid
    median_val = tl.full((), fallback_value, dtype=vals.dtype)
    median_idx = tl.full((), 0, dtype=tl.int32)
    for select_iter in tl.static_range(0, BLOCK_N):
        select_vals = tl.where(active, vals, max_value)
        cur_val = tl.min(select_vals, axis=0)
        cur_idx = tl.min(tl.where(active & (vals == cur_val), offsets, BLOCK_N), axis=0)
        take = select_iter == median_rank
        median_val = tl.where(take, cur_val, median_val)
        median_idx = tl.where(take, cur_idx, median_idx)
        active = active & (offsets != cur_idx)
    if dtype.is_floating():
        all_nan = valid_count == 0
        median_val = tl.where(all_nan, float('nan'), median_val)
        median_idx = tl.where(all_nan, 0, median_idx)
    tl.store(out_values + pid, median_val)
    tl.store(out_indices + pid, median_idx)
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
SHAPES = ((17,), (97,));DTYPES = ('float32', 'float16', 'bfloat16')
def ref(args,meta):
 import numpy as np
 M=int(args["M"]);C=int(meta["N"]);x=np.asarray(args["inp"],np.float32).reshape(M,C);vals=[];inds=[]
 for row in x:
  valid=np.flatnonzero(~np.isnan(row))
  if valid.size==0:vals.append(np.nan);inds.append(0)
  else:
   order=valid[np.argsort(row[valid],kind="stable")];j=int(order[(valid.size-1)//2]);vals.append(row[j]);inds.append(j)
 return {"out_values":np.asarray(vals,np.float32),"out_indices":np.asarray(inds,np.int32)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 M=4;C=max(3,min(N,257));B=1<<(C-1).bit_length();x=rng.normal(0,.8,(M,C)).astype(np.float32);x[0,::3]=np.nan;x[1,:]=np.nan;x[2,1]=x[2,-1];args={"inp":_aligned(x,"float32"),"out_values":_aligned(np.full(M,-7),"float32"),"out_indices":_aligned(np.full(M,-1),"int32"),"M":M};meta={"N":C,"BLOCK_N":B,"USE_ISNAN":True};grid=(M,)
 outputs=('out_values', 'out_indices');return _case(nanmedian_select_kernel,grid,args,meta,('inp',),outputs,ref(args,meta),shape,"torch.float32",seed,{"complete_launch_plan":True,"formula":'complete repeated-min nanmedian with stable duplicate occurrence and all-NaN fallback'})

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
