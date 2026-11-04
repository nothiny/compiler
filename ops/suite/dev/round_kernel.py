"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/round_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def round_kernel(x_ptr, out_ptr, n_elements, decimals: tl.constexpr, BLOCK_SIZE: tl.constexpr, IS_FP32: tl.constexpr, IS_FP16: tl.constexpr, IS_BF16: tl.constexpr):
    pid = tl.program_id(axis=0)
    block_start = pid * BLOCK_SIZE
    offsets = block_start + tl.arange(0, BLOCK_SIZE)
    mask = offsets < n_elements
    x = tl.load(x_ptr + offsets, mask=mask)
    if decimals == 0:
        out = x
        if IS_FP32:
            _inl_1_round_half_to_even_impl_x = x
            'Round to nearest with ties to even (round half to even).\n    x must be fp32.'
            _inl_1_round_half_to_even_impl_r = tl.floor(_inl_1_round_half_to_even_impl_x)
            _inl_1_round_half_to_even_impl_d = _inl_1_round_half_to_even_impl_x - _inl_1_round_half_to_even_impl_r
            _inl_1_round_half_to_even_impl_is_odd = tl.abs(_inl_1_round_half_to_even_impl_r - 2.0 * tl.floor(_inl_1_round_half_to_even_impl_r / 2.0)) > 0.5
            _inl_1_round_half_to_even_impl_result = tl.where((_inl_1_round_half_to_even_impl_d > 0.5) | (tl.abs(_inl_1_round_half_to_even_impl_d - 0.5) < 1e-10) & _inl_1_round_half_to_even_impl_is_odd, _inl_1_round_half_to_even_impl_r + 1.0, _inl_1_round_half_to_even_impl_r)
            out = _inl_1_round_half_to_even_impl_result
        elif IS_FP16:
            x_fp32 = tl.cast(x, tl.float32)
            _inl_2_round_half_to_even_impl_x = x_fp32
            'Round to nearest with ties to even (round half to even).\n    x must be fp32.'
            _inl_2_round_half_to_even_impl_r = tl.floor(_inl_2_round_half_to_even_impl_x)
            _inl_2_round_half_to_even_impl_d = _inl_2_round_half_to_even_impl_x - _inl_2_round_half_to_even_impl_r
            _inl_2_round_half_to_even_impl_is_odd = tl.abs(_inl_2_round_half_to_even_impl_r - 2.0 * tl.floor(_inl_2_round_half_to_even_impl_r / 2.0)) > 0.5
            _inl_2_round_half_to_even_impl_result = tl.where((_inl_2_round_half_to_even_impl_d > 0.5) | (tl.abs(_inl_2_round_half_to_even_impl_d - 0.5) < 1e-10) & _inl_2_round_half_to_even_impl_is_odd, _inl_2_round_half_to_even_impl_r + 1.0, _inl_2_round_half_to_even_impl_r)
            out = tl.cast(_inl_2_round_half_to_even_impl_result, tl.float16)
        elif IS_BF16:
            x_fp32 = tl.cast(x, tl.float32)
            _inl_3_round_half_to_even_impl_x = x_fp32
            'Round to nearest with ties to even (round half to even).\n    x must be fp32.'
            _inl_3_round_half_to_even_impl_r = tl.floor(_inl_3_round_half_to_even_impl_x)
            _inl_3_round_half_to_even_impl_d = _inl_3_round_half_to_even_impl_x - _inl_3_round_half_to_even_impl_r
            _inl_3_round_half_to_even_impl_is_odd = tl.abs(_inl_3_round_half_to_even_impl_r - 2.0 * tl.floor(_inl_3_round_half_to_even_impl_r / 2.0)) > 0.5
            _inl_3_round_half_to_even_impl_result = tl.where((_inl_3_round_half_to_even_impl_d > 0.5) | (tl.abs(_inl_3_round_half_to_even_impl_d - 0.5) < 1e-10) & _inl_3_round_half_to_even_impl_is_odd, _inl_3_round_half_to_even_impl_r + 1.0, _inl_3_round_half_to_even_impl_r)
            out = tl.cast(_inl_3_round_half_to_even_impl_result, tl.bfloat16)
    else:
        scale = 10.0 ** decimals
        if IS_FP32:
            x_scaled = x * scale
            _inl_4_round_half_to_even_impl_x = x_scaled
            'Round to nearest with ties to even (round half to even).\n    x must be fp32.'
            _inl_4_round_half_to_even_impl_r = tl.floor(_inl_4_round_half_to_even_impl_x)
            _inl_4_round_half_to_even_impl_d = _inl_4_round_half_to_even_impl_x - _inl_4_round_half_to_even_impl_r
            _inl_4_round_half_to_even_impl_is_odd = tl.abs(_inl_4_round_half_to_even_impl_r - 2.0 * tl.floor(_inl_4_round_half_to_even_impl_r / 2.0)) > 0.5
            _inl_4_round_half_to_even_impl_result = tl.where((_inl_4_round_half_to_even_impl_d > 0.5) | (tl.abs(_inl_4_round_half_to_even_impl_d - 0.5) < 1e-10) & _inl_4_round_half_to_even_impl_is_odd, _inl_4_round_half_to_even_impl_r + 1.0, _inl_4_round_half_to_even_impl_r)
            out = _inl_4_round_half_to_even_impl_result / scale
        elif IS_FP16:
            x_fp32 = tl.cast(x, tl.float32)
            x_scaled = x_fp32 * scale
            _inl_5_round_half_to_even_impl_x = x_scaled
            'Round to nearest with ties to even (round half to even).\n    x must be fp32.'
            _inl_5_round_half_to_even_impl_r = tl.floor(_inl_5_round_half_to_even_impl_x)
            _inl_5_round_half_to_even_impl_d = _inl_5_round_half_to_even_impl_x - _inl_5_round_half_to_even_impl_r
            _inl_5_round_half_to_even_impl_is_odd = tl.abs(_inl_5_round_half_to_even_impl_r - 2.0 * tl.floor(_inl_5_round_half_to_even_impl_r / 2.0)) > 0.5
            _inl_5_round_half_to_even_impl_result = tl.where((_inl_5_round_half_to_even_impl_d > 0.5) | (tl.abs(_inl_5_round_half_to_even_impl_d - 0.5) < 1e-10) & _inl_5_round_half_to_even_impl_is_odd, _inl_5_round_half_to_even_impl_r + 1.0, _inl_5_round_half_to_even_impl_r)
            out = tl.cast(_inl_5_round_half_to_even_impl_result / scale, tl.float16)
        elif IS_BF16:
            x_fp32 = tl.cast(x, tl.float32)
            x_scaled = x_fp32 * scale
            _inl_6_round_half_to_even_impl_x = x_scaled
            'Round to nearest with ties to even (round half to even).\n    x must be fp32.'
            _inl_6_round_half_to_even_impl_r = tl.floor(_inl_6_round_half_to_even_impl_x)
            _inl_6_round_half_to_even_impl_d = _inl_6_round_half_to_even_impl_x - _inl_6_round_half_to_even_impl_r
            _inl_6_round_half_to_even_impl_is_odd = tl.abs(_inl_6_round_half_to_even_impl_r - 2.0 * tl.floor(_inl_6_round_half_to_even_impl_r / 2.0)) > 0.5
            _inl_6_round_half_to_even_impl_result = tl.where((_inl_6_round_half_to_even_impl_d > 0.5) | (tl.abs(_inl_6_round_half_to_even_impl_d - 0.5) < 1e-10) & _inl_6_round_half_to_even_impl_is_odd, _inl_6_round_half_to_even_impl_r + 1.0, _inl_6_round_half_to_even_impl_r)
            out = tl.cast(_inl_6_round_half_to_even_impl_result / scale, tl.bfloat16)
        else:
            out = x
    tl.store(out_ptr + offsets, out, mask=mask)
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
SHAPES=((17,), (97,));DTYPES=('float32', 'float16', 'bfloat16')
def ref(args,meta):
 import numpy as np
 scale=np.float32(10**meta["decimals"]);return {"out_ptr":(np.round(args["x_ptr"]*scale)/scale).astype(np.float32)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 args={"x_ptr":_aligned(rng.normal(0,.8,N)),"out_ptr":_aligned(np.full(N,-7.)),"n_elements":N};meta={"decimals":2,"BLOCK_SIZE":128,"IS_FP32":True,"IS_FP16":False,"IS_BF16":False};grid=((N+127)//128,)
 outputs=('out_ptr',);return _case(round_kernel,grid,args,meta,('x_ptr',),outputs,ref(args,meta),shape,"torch.float32",seed,{"complete_launch_plan":True,"formula":'round to two decimal places'})

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
