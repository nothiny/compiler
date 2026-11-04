"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/fused_recurrent_hgrn_fwd_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["fla"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit(do_not_specialize=['T'])
def fused_recurrent_hgrn_fwd_kernel(x, g, o, h0, ht, cu_seqlens, T, D: tl.constexpr, BD: tl.constexpr, USE_INITIAL_STATE: tl.constexpr, STORE_FINAL_STATE: tl.constexpr, IS_VARLEN: tl.constexpr):
    pid = tl.program_id(0)
    ND = tl.cdiv(D, BD)
    (i_d, i_n) = (pid % ND, (pid // ND).to(tl.int64))
    if IS_VARLEN:
        (bos, eos) = (tl.load(cu_seqlens + i_n).to(tl.int64), tl.load(cu_seqlens + i_n + 1).to(tl.int64))
        T = eos - bos
    else:
        (bos, eos) = (i_n * T, i_n * T + T)
    o_d = i_d * BD + tl.arange(0, BD)
    mask = o_d < D
    p_x = x + bos * D + o_d
    p_g = g + bos * D + o_d
    p_o = o + bos * D + o_d
    b_h = tl.zeros([BD], dtype=tl.float32)
    if USE_INITIAL_STATE:
        p_h0 = h0 + i_n * D + o_d
        b_h += tl.load(p_h0, mask=mask, other=0).to(tl.float32)
    for _ in range(0, T):
        b_x = tl.load(p_x, mask=mask, other=0).to(tl.float32)
        b_g = tl.load(p_g, mask=mask, other=0).to(tl.float32)
        _inl_1_exp_x = b_g
        _inl_1_exp_result = tl.exp(_inl_1_exp_x.to(tl.float32))
        b_h = _inl_1_exp_result * b_h + b_x
        tl.store(p_o, b_h.to(p_o.dtype.element_ty), mask=mask)
        p_x += D
        p_g += D
        p_o += D
    if STORE_FINAL_STATE:
        p_ht = ht + i_n * D + o_d
        tl.store(p_ht, b_h.to(p_ht.dtype.element_ty), mask=mask)
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
SHAPES=((3,17,13),(2,33,29)); DTYPES=('float32', 'float16', 'bfloat16'); FIXED_META={"BD":16,"USE_INITIAL_STATE":True,"STORE_FINAL_STATE":True,"IS_VARLEN":False}


def ref(args,meta):
    import numpy as np
    B=args["h0"].shape[0]; T=int(args["T"]); D=meta["D"]; x=args["x"].reshape(B,T,D); g=args["g"].reshape(B,T,D); state=args["h0"].copy(); out=np.empty_like(x)
    for t in range(T): state=np.exp(g[:,t])*state+x[:,t]; out[:,t]=state
    return {"o":out.reshape(-1),"ht":state.reshape(-1)}


def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
    del dtype
    import numpy as np
    B,T,D=(int(x) for x in shape); rng=fast_rng(seed); args={"x":_aligned(rng.normal(0,.2,B*T*D)),"g":_aligned(rng.uniform(-.4,-.05,B*T*D)),"o":_aligned(np.full(B*T*D,-7.0)),"h0":_aligned(rng.normal(0,.1,(B,D))),"ht":_aligned(np.full(B*D,-7.0)),"cu_seqlens":_aligned(np.arange(B+1)*T,"int32"),"T":T}; meta={**FIXED_META,"D":D}; grid=(B*((D+meta["BD"]-1)//meta["BD"]),); outputs=("o","ht")
    return _case(fused_recurrent_hgrn_fwd_kernel,grid,args,meta,("x","g","h0"),outputs,ref(args,meta),shape,"torch.float32",seed,{"grid_formula":"(B*ceil_div(D,BD),)","outputs":outputs})

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
