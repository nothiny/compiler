"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/kda_gate_fwd_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["fla"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit(do_not_specialize=['T'])
def kda_gate_fwd_kernel(g, A_log, dt_bias, beta, yg, yb, lower_bound, T, H: tl.constexpr, D: tl.constexpr, BT: tl.constexpr, BD: tl.constexpr, HAS_A: tl.constexpr, HAS_BIAS: tl.constexpr, HAS_BETA: tl.constexpr, USE_LOWER_BOUND: tl.constexpr):
    (i_t, i_h) = (tl.program_id(0).to(tl.int64), tl.program_id(1))
    b_A = tl.load(A_log + i_h).to(tl.float32) if HAS_A else 1.0
    o_t = i_t * BT + tl.arange(0, BT)
    o_d = tl.arange(0, BD)
    m_t = o_t < T
    m_g = m_t[:, None] & (o_d[None, :] < D)
    p_g = g + i_h * D + o_t[:, None] * (H * D) + o_d[None, :]
    p_yg = yg + i_h * D + o_t[:, None] * (H * D) + o_d[None, :]
    b_g = tl.load(p_g, mask=m_g, other=0.0).to(tl.float32)
    if HAS_BIAS:
        o_b = i_h * D + tl.arange(0, BD)
        b_g = b_g + tl.load(dt_bias + o_b, mask=o_b < H * D, other=0.0).to(tl.float32)
    if not USE_LOWER_BOUND:
        _inl_1_exp_x = b_A
        _inl_1_exp_result = tl.exp(_inl_1_exp_x.to(tl.float32))
        _inl_2_softplus_triton_x = b_g
        _inl_2_softplus_triton_result = tl.where(_inl_2_softplus_triton_x < 20.0, tl.log(1 + tl.exp(_inl_2_softplus_triton_x)), _inl_2_softplus_triton_x)
        b_yg = -_inl_1_exp_result * _inl_2_softplus_triton_result
    else:
        _inl_3_exp_x = b_A
        _inl_3_exp_result = tl.exp(_inl_3_exp_x.to(tl.float32))
        b_yg = lower_bound * tl.sigmoid((_inl_3_exp_result if HAS_A else b_A) * b_g)
    tl.store(p_yg, b_yg.to(p_yg.dtype.element_ty), mask=m_g)
    if HAS_BETA:
        p_b = beta + i_h + o_t * H
        p_yb = yb + i_h + o_t * H
        b_yb = tl.sigmoid(tl.load(p_b, mask=m_t, other=0.0).to(tl.float32))
        tl.store(p_yb, b_yb.to(p_yb.dtype.element_ty), mask=m_t)
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
 T=int(args["T"]);H=int(meta["H"]);D=int(meta["D"]);x=np.asarray(args["g"],np.float32).reshape(T,H,D);z=x+np.asarray(args["dt_bias"],np.float32).reshape(H,D)[None];a=np.asarray(args["A_log"],np.float32).reshape(H);soft=np.where(z<20,np.log1p(np.exp(z)),z);yg=-np.exp(a)[None,:,None]*soft;yb=1/(1+np.exp(-np.asarray(args["beta"],np.float32).reshape(T,H)));return {"yg":yg.astype(np.float32).reshape(-1),"yb":yb.astype(np.float32).reshape(-1)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 T=max(9,min(65,N|1));H=3;D=7;BT=8;args={"g":_aligned(rng.normal(0,.7,(T,H,D)),"float32"),"A_log":_aligned(rng.normal(-.3,.2,H),"float32"),"dt_bias":_aligned(rng.normal(0,.2,(H,D)),"float32"),"beta":_aligned(rng.normal(0,.7,(T,H)),"float32"),"yg":_aligned(np.full(T*H*D,-7),"float32"),"yb":_aligned(np.full(T*H,-7),"float32"),"lower_bound":-.1,"T":T};meta={"H":H,"D":D,"BT":BT,"BD":8,"HAS_A":True,"HAS_BIAS":True,"HAS_BETA":True,"USE_LOWER_BOUND":False};grid=((T+BT-1)//BT,H)
 outputs=('yg', 'yb');return _case(kda_gate_fwd_kernel,grid,args,meta,('g', 'A_log', 'dt_bias', 'beta'),outputs,ref(args,meta),shape,"torch.float32",seed,{"complete_launch_plan":True,"formula":'negative exp(A-log) times biased softplus gate and sigmoid beta gate'})

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
