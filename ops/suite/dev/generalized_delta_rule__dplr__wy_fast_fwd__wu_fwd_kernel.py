"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/generalized_delta_rule__dplr__wy_fast_fwd__wu_fwd_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit(do_not_specialize=['T'])
def wu_fwd_kernel(w, u, ag, v, A_ab_inv, A_ak, cu_seqlens, chunk_indices, T, H: tl.constexpr, K: tl.constexpr, V: tl.constexpr, BT: tl.constexpr, BK: tl.constexpr, BV: tl.constexpr, IS_VARLEN: tl.constexpr):
    (i_t, i_bh) = (tl.program_id(0).to(tl.int64), tl.program_id(1).to(tl.int64))
    (i_b, i_h) = (i_bh // H, i_bh % H)
    if IS_VARLEN:
        (i_n, i_t) = (tl.load(chunk_indices + i_t * 2).to(tl.int32), tl.load(chunk_indices + i_t * 2 + 1).to(tl.int64))
        (bos, eos) = (tl.load(cu_seqlens + i_n).to(tl.int64), tl.load(cu_seqlens + i_n + 1).to(tl.int64))
        T = eos - bos
    else:
        (bos, eos) = (i_b * T, i_b * T + T)
    o_s = tl.arange(0, BT)
    o_t = i_t * BT + o_s
    m_t = o_t < T
    m_A = m_t[:, None] & (o_s[None, :] < BT)
    p_A_ab_inv = A_ab_inv + (bos * H + i_h) * BT + o_t[:, None] * (H * BT) + o_s[None, :]
    p_A_ak = A_ak + (bos * H + i_h) * BT + o_t[:, None] * (H * BT) + o_s[None, :]
    b_Aab_inv = tl.load(p_A_ab_inv, mask=m_A, other=0.0)
    b_Aak = tl.load(p_A_ak, mask=m_A, other=0.0)
    b_Aab_inv = tl.where(o_s[:, None] >= o_s[None, :], b_Aab_inv, 0)
    b_Aak = tl.where(o_s[:, None] > o_s[None, :], b_Aak, 0)
    b_Aak = tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Aab_inv.shape[1])[None, None, :] == 0, b_Aab_inv[:, :, None], 0), (b_Aab_inv.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Aab_inv.shape[1])[None, :, None] == 0, b_Aak[:, None, :], 0), (16, b_Aak.shape[1])).to(tl.float32)) if b_Aab_inv.shape[1] < 16 else tl.dot(b_Aab_inv, b_Aak)
    b_Aak = b_Aak.to(v.dtype.element_ty, fp_downcast_rounding='rtne')
    b_Aab_inv = b_Aab_inv.to(ag.dtype.element_ty, fp_downcast_rounding='rtne')
    for i_k in range(tl.cdiv(K, BK)):
        o_k = i_k * BK + tl.arange(0, BK)
        m_k = m_t[:, None] & (o_k[None, :] < K)
        p_ag = ag + (bos * H + i_h) * K + o_t[:, None] * (H * K) + o_k[None, :]
        p_w = w + (bos * H + i_h) * K + o_t[:, None] * (H * K) + o_k[None, :]
        b_ag = tl.load(p_ag, mask=m_k, other=0.0)
        b_w = tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Aab_inv.shape[1])[None, None, :] == 0, b_Aab_inv[:, :, None], 0), (b_Aab_inv.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Aab_inv.shape[1])[None, :, None] == 0, b_ag[:, None, :], 0), (16, b_ag.shape[1])).to(tl.float32)) if b_Aab_inv.shape[1] < 16 else tl.dot(b_Aab_inv, b_ag)
        tl.store(p_w, b_w.to(p_w.dtype.element_ty, fp_downcast_rounding='rtne'), mask=m_k)
    for i_v in range(tl.cdiv(V, BV)):
        o_v = i_v * BV + tl.arange(0, BV)
        m_v = m_t[:, None] & (o_v[None, :] < V)
        p_v = v + (bos * H + i_h) * V + o_t[:, None] * (H * V) + o_v[None, :]
        p_u = u + (bos * H + i_h) * V + o_t[:, None] * (H * V) + o_v[None, :]
        b_v = tl.load(p_v, mask=m_v, other=0.0)
        b_u = tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Aak.shape[1])[None, None, :] == 0, b_Aak[:, :, None], 0), (b_Aak.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Aak.shape[1])[None, :, None] == 0, b_v[:, None, :], 0), (16, b_v.shape[1])).to(tl.float32)) if b_Aak.shape[1] < 16 else tl.dot(b_Aak, b_v)
        tl.store(p_u, b_u.to(p_u.dtype.element_ty, fp_downcast_rounding='rtne'), mask=m_v)
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
 T=int(args["T"]);H=int(meta["H"]);K=int(meta["K"]);V=int(meta["V"]);BT=int(meta["BT"]);ag=np.asarray(args["ag"],np.float32).reshape(-1,T,H,K);v=np.asarray(args["v"],np.float32).reshape(-1,T,H,V);aa=np.asarray(args["A_ab_inv"],np.float32).reshape(-1,T,H,BT);ak=np.asarray(args["A_ak"],np.float32).reshape(-1,T,H,BT);w=np.zeros_like(ag);u=np.zeros_like(v)
 for b in range(ag.shape[0]):
  for h in range(H):
   for start in range(0,T,BT):
    n=min(BT,T-start);A=np.tril(aa[b,start:start+n,h,:n]);Kmat=np.tril(ak[b,start:start+n,h,:n],-1);w[b,start:start+n,h]=A@ag[b,start:start+n,h];u[b,start:start+n,h]=(A@Kmat)@v[b,start:start+n,h]
 return {"w":w.reshape(-1),"u":u.reshape(-1)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 B=2;H=2;T=max(9,min(33,N|1));K=6;V=5;BT=8;aa=np.zeros((B,T,H,BT),np.float32);ak=np.zeros_like(aa)
 for start in range(0,T,BT):n=min(BT,T-start);aa[:,start:start+n,:,:n]=np.tril(rng.normal(0,.12,(B,n,H,n)))+np.eye(n)[None,:,None,:];ak[:,start:start+n,:,:n]=np.tril(rng.normal(0,.1,(B,n,H,n)),-1)
 args={"w":_aligned(np.full(B*T*H*K,-7),"float32"),"u":_aligned(np.full(B*T*H*V,-7),"float32"),"ag":_aligned(rng.normal(0,.2,(B,T,H,K)),"float32"),"v":_aligned(rng.normal(0,.2,(B,T,H,V)),"float32"),"A_ab_inv":_aligned(aa,"float32"),"A_ak":_aligned(ak,"float32"),"cu_seqlens":_aligned(np.asarray([0,T,2*T]),"int64"),"chunk_indices":_aligned(np.zeros(2,dtype=np.int64),"int64"),"T":T};meta={"H":H,"K":K,"V":V,"BT":BT,"BK":4,"BV":4,"IS_VARLEN":False};grid=((T+BT-1)//BT,B*H)
 outputs=('w', 'u');return _case(wu_fwd_kernel,grid,args,meta,('ag', 'v', 'A_ab_inv', 'A_ak'),outputs,ref(args,meta),shape,"torch.float32",seed,{"complete_launch_plan":True,"formula":'DPLR lower inverse times a-g and inverse-times-strict-lower-Aak times v'})

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
