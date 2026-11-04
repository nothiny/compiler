"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/chunk_hgrn_fwd_kernel_h", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["fla"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit(do_not_specialize=['T'])
def chunk_hgrn_fwd_kernel_h(x, g, gc, o, h0, T, D: tl.constexpr, BT: tl.constexpr, BD: tl.constexpr, USE_INITIAL_STATE: tl.constexpr):
    (i_d, i_t, i_b) = (tl.program_id(0), tl.program_id(1), tl.program_id(2).to(tl.int64))
    o_d = i_d * BD + tl.arange(0, BD)
    mask = o_d < D
    p_x = x + i_b * T * D + i_t * BT * D + o_d
    p_g = g + i_b * T * D + i_t * BT * D + o_d
    p_gc = gc + i_b * T * D + i_t * BT * D + o_d
    p_o = o + i_b * T * D + i_t * BT * D + o_d
    b_h = tl.zeros([BD], dtype=tl.float32)
    b_gc = tl.zeros([BD], dtype=tl.float32)
    if USE_INITIAL_STATE:
        if i_t == 0:
            b_h += tl.load(h0 + i_b * D + o_d, mask=mask, other=0).to(tl.float32)
    for i in range(0, BT):
        mask_t = mask & (i_t * BT + i < T)
        b_x = tl.load(p_x, mask=mask_t, other=0).to(tl.float32)
        b_g = tl.load(p_g, mask=mask_t, other=0).to(tl.float32)
        _inl_1_exp_x = b_g
        _inl_1_exp_result = tl.exp(_inl_1_exp_x.to(tl.float32))
        b_h = _inl_1_exp_result * b_h + b_x
        b_gc = b_gc + b_g
        tl.store(p_gc, b_gc.to(p_o.dtype.element_ty), mask=mask_t)
        tl.store(p_o, b_h.to(p_o.dtype.element_ty), mask=mask_t)
        p_x += D
        p_g += D
        p_gc += D
        p_o += D
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
SHAPES=((2,17,13,8),(3,33,29,16));DTYPES=('float32', 'float16', 'bfloat16');FIXED_META={"BD":16,"USE_INITIAL_STATE":True}


def ref(args,meta):
    import numpy as np
    B,T,D,BT=args["h0"].shape[0],int(args["T"]),meta["D"],meta["BT"];x=args["x"].reshape(B,T,D);g=args["g"].reshape(B,T,D);o=np.zeros_like(x);gc=np.zeros_like(g)
    for b in range(B):
        for start in range(0,T,BT):
            state=args["h0"][b].copy() if start==0 else np.zeros(D,np.float32);cs=np.zeros(D,np.float32)
            for t in range(start,min(start+BT,T)): state=np.exp(g[b,t])*state+x[b,t];cs+=g[b,t];o[b,t]=state;gc[b,t]=cs
    return {"gc":gc.reshape(-1),"o":o.reshape(-1)}


def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
    del dtype
    import numpy as np
    B,T,D,BT=(int(x) for x in shape);rng=fast_rng(seed);args={"x":_aligned(rng.normal(0,.2,B*T*D)),"g":_aligned(rng.uniform(-.4,-.05,B*T*D)),"gc":_aligned(np.full(B*T*D,-7.0)),"o":_aligned(np.full(B*T*D,-7.0)),"h0":_aligned(rng.normal(0,.1,(B,D))),"T":T};meta={**FIXED_META,"D":D,"BT":BT};grid=((D+meta["BD"]-1)//meta["BD"],(T+BT-1)//BT,B);outputs=("gc","o")
    return _case(chunk_hgrn_fwd_kernel_h,grid,args,meta,("x","g","h0"),outputs,ref(args,meta),shape,"torch.float32",seed,{"grid_formula":"(ceil_div(D,BD),ceil_div(T,BT),B)","outputs":outputs})

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
