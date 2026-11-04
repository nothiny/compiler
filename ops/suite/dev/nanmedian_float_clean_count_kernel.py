"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/nanmedian_float_clean_count_kernel", "group": "hidden", "channel": "local",
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
def nanmedian_float_clean_count_kernel(inp, cleaned, valid_counts, N: tl.constexpr, BLOCK_N: tl.constexpr):
    pid = tl.program_id(0).to(tl.int64)
    offsets = tl.arange(0, BLOCK_N)
    dtype = inp.dtype.element_ty
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
    count = tl.full((), 0, dtype=tl.int32)
    for start in tl.range(0, N, BLOCK_N):
        cols = start + offsets
        mask = cols < N
        vals = tl.load(inp + pid * N + cols, mask=mask, other=max_value)
        _inl_3_is_not_nan_vals = vals
        _inl_3_is_not_nan_USE_ISNAN: tl.constexpr = False
        _inl_3_is_not_nan_vals_fp32 = _inl_3_is_not_nan_vals.to(tl.float32)
        _inl_3_is_not_nan_result = _inl_3_is_not_nan_vals_fp32 == _inl_3_is_not_nan_vals_fp32
        valid = mask & _inl_3_is_not_nan_result
        cleaned_vals = tl.where(valid, vals, max_value)
        tl.store(cleaned + pid * N + cols, cleaned_vals, mask=mask)
        count += tl.sum(valid.to(tl.int32), axis=0)
    tl.store(valid_counts + pid, count)
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
SHAPES=((17,), (97,));DTYPES=('float32', 'bfloat16')
def ref(args,meta):
 import numpy as np
 C=int(meta["N"]);x=np.asarray(args["inp"],np.float32).reshape(-1,C);valid=~np.isnan(x);clean=np.where(valid,x,np.finfo(np.float32).max).astype(np.float32);return {"cleaned":clean.reshape(-1),"valid_counts":np.sum(valid,axis=1,dtype=np.int64).astype(np.int32)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 M=4;C=max(3,N);x=rng.normal(0,.8,(M,C)).astype(np.float32);x[0,::3]=np.nan;x[1,:]=np.nan;args={"inp":_aligned(x,"float32"),"cleaned":_aligned(np.full(M*C,-7),"float32"),"valid_counts":_aligned(np.full(M,-1),"int32")};meta={"N":C,"BLOCK_N":128};grid=(M,)
 outputs=('cleaned', 'valid_counts');return _case(nanmedian_float_clean_count_kernel,grid,args,meta,('inp',),outputs,ref(args,meta),shape,"torch.float32",seed,{"complete_launch_plan":True,"formula":'replace NaNs with float32 maximum and count valid elements in every row'})

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
