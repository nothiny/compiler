"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/chunk_abc_fwd_kernel_intra_K", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["fla"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit(do_not_specialize=['T'])
def chunk_abc_fwd_kernel_intra_K(v, z, o, A, T, V: tl.constexpr, BT: tl.constexpr, BC: tl.constexpr, BV: tl.constexpr, NC: tl.constexpr):
    (i_v, i_c, i_bh) = (tl.program_id(0), tl.program_id(1).to(tl.int64), tl.program_id(2).to(tl.int64))
    (i_t, i_i) = (i_c // NC, i_c % NC)
    o_r = i_t * BT + i_i * BC + tl.arange(0, BC)
    o_v = i_v * BV + tl.arange(0, BV)
    m_rv = (o_r[:, None] < T) & (o_v[None, :] < V)
    o_zn = (i_t * BT + i_i * BC) * V + o_v
    p_z = z + i_bh * T * V + o_r[:, None] * V + o_v[None, :]
    p_zn = z + i_bh * T * V + o_zn
    b_zn = tl.load(p_zn, mask=o_zn < T * V, other=0.0)
    b_o = tl.zeros([BC, BV], dtype=tl.float32)
    for i_j in range(0, i_i):
        o_vr = i_t * BT + i_j * BC + tl.arange(0, BC)
        o_Aj = i_j * BC + tl.arange(0, BC)
        m_vr = (o_vr[:, None] < T) & (o_v[None, :] < V)
        m_A = (o_r[:, None] < T) & (o_Aj[None, :] < BT)
        p_A = A + i_bh * T * BT + o_r[:, None] * BT + o_Aj[None, :]
        p_v = v + i_bh * T * V + o_vr[:, None] * V + o_v[None, :]
        b_v = tl.load(p_v, mask=m_vr, other=0.0)
        b_A = tl.load(p_A, mask=m_A, other=0.0)
        _inl_1_exp_x = b_v - b_zn[None, :]
        _inl_1_exp_result = tl.exp(_inl_1_exp_x.to(tl.float32))
        b_o += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_A.shape[1])[None, None, :] == 0, b_A[:, :, None], 0), (b_A.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_A.shape[1])[None, :, None] == 0, _inl_1_exp_result.to(b_v.dtype)[:, None, :], 0), (16, _inl_1_exp_result.to(b_v.dtype).shape[1])).to(tl.float32)) if b_A.shape[1] < 16 else tl.dot(b_A, _inl_1_exp_result.to(b_v.dtype))
    b_z = tl.load(p_z, mask=m_rv, other=0.0)
    _inl_2_exp_x = b_zn[None, :] - b_z
    _inl_2_exp_result = tl.exp(_inl_2_exp_x.to(tl.float32))
    b_o *= _inl_2_exp_result
    o_i = tl.arange(0, BC)
    o_A = i_bh * T * BT + (i_t * BT + i_i * BC + tl.arange(0, BC)) * BT + i_i * BC
    m_A = i_t * BT + i_i * BC + tl.arange(0, BC) < T
    for j in range(0, BC):
        o_vj = (i_t * BT + i_i * BC + j) * V + o_v
        p_vj = v + i_bh * T * V + o_vj
        b_A = tl.load(A + o_A + j, mask=m_A, other=0)
        b_v = tl.load(p_vj, mask=o_vj < T * V, other=0.0).to(tl.float32)
        m_i = o_i[:, None] >= j
        _inl_3_exp_x = b_v[None, :] - b_z
        _inl_3_exp_result = tl.exp(_inl_3_exp_x.to(tl.float32))
        b_o += tl.where(m_i, b_A[:, None] * _inl_3_exp_result, 0)
    p_o = o + i_bh * T * V + o_r[:, None] * V + o_v[None, :]
    tl.store(p_o, b_o.to(p_o.dtype.element_ty), mask=m_rv)
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
SHAPES = ((2, 2, 17, 9, 8, 4), (1, 3, 33, 13, 16, 4))
DTYPES = ('float32', 'float16', 'bfloat16')
FIXED_META = {"BV": 4}


def ref(args, meta):
    import numpy as np

    BH,T,V,BT,BC,NC=args["v"].shape[0],int(args["T"]),meta["V"],meta["BT"],meta["BC"],meta["NC"]; out=np.zeros((BH,T,V),np.float32)
    for n in range(BH):
        for chunk in range((T+BT-1)//BT):
            for sub in range(NC):
                start=chunk*BT+sub*BC
                for rr in range(BC):
                    row=start+rr
                    if row>=T: continue
                    zn=args["z"][n,start] if start<T else np.zeros(V,np.float32); value=np.zeros(V,np.float32)
                    for prior in range(sub):
                        ps=chunk*BT+prior*BC
                        for j in range(BC):
                            col=ps+j
                            if col<T: value += args["A"][n,row,prior*BC+j]*np.exp(args["v"][n,col]-zn)
                    value *= np.exp(zn-args["z"][n,row])
                    for j in range(rr+1):
                        col=start+j
                        if col<T: value += args["A"][n,row,sub*BC+j]*np.exp(args["v"][n,col]-args["z"][n,row])
                    out[n,row]=value
    return {"o":out.reshape(-1)}


def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
    del dtype
    import numpy as np

    B,H,T,V,BT,BC=(int(x) for x in shape); BH=B*H; NC=BT//BC; NT=(T+BT-1)//BT; rng=fast_rng(seed)
    args={"v":_aligned(rng.normal(0,.2,(BH,T,V))),"z":_aligned(rng.normal(0,.08,(BH,T,V))),"o":_aligned(np.full(BH*T*V,-7.0)),"A":_aligned(rng.normal(0,.1,(BH,T,BT))),"T":T}
    meta={**FIXED_META,"V":V,"BT":BT,"BC":BC,"NC":NC}; grid=((V+meta["BV"]-1)//meta["BV"],NT*NC,BH); outputs=("o",)
    return _case(chunk_abc_fwd_kernel_intra_K,grid,args,meta,("v","z","A"),outputs,ref(args,meta),shape,"torch.float32",seed,{"grid_formula":"(ceil_div(V,BV),NT*NC,B*H)","output":"o[B*H,T,V]"})

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
