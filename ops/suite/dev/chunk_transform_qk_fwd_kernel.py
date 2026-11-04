"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/chunk_transform_qk_fwd_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["fla"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit(do_not_specialize=['T'])
def chunk_transform_qk_fwd_kernel(q, k, v, beta, o, A, q_new, k_new, A_local, scale, T, K: tl.constexpr, V: tl.constexpr, BK: tl.constexpr, BV: tl.constexpr, BT: tl.constexpr, OUTPUT_ATTENTIONS: tl.constexpr):
    (i_t, i_bh) = (tl.program_id(0).to(tl.int64), tl.program_id(1).to(tl.int64))
    o_t = i_t * BT + tl.arange(0, BT)
    o_k = tl.arange(0, BK)
    o_v = tl.arange(0, BV)
    o_T = tl.arange(0, BT)
    m_b = o_t < T
    m_qk = m_b[:, None] & (o_k[None, :] < K)
    m_v = m_b[:, None] & (o_v[None, :] < V)
    m_T = m_b[:, None] & (o_T[None, :] < BT)
    p_q = q + i_bh * T * K + o_t[:, None] * K + o_k[None, :]
    p_k = k + i_bh * T * K + o_t[:, None] * K + o_k[None, :]
    p_v = v + i_bh * T * V + o_t[:, None] * V + o_v[None, :]
    b_q = (tl.load(p_q, mask=m_qk, other=0.0) * scale).to(p_q.dtype.element_ty)
    b_k = tl.load(p_k, mask=m_qk, other=0.0)
    b_v = tl.load(p_v, mask=m_v, other=0.0)
    p_T = A + i_bh * T * BT + o_t[:, None] * BT + o_T[None, :]
    b_T = tl.load(p_T, mask=m_T, other=0.0)
    o_i = tl.arange(0, BT)
    m_t = o_i[:, None] >= o_i[None, :]
    b_qk = tl.where(m_t, tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_q.shape[1])[None, None, :] == 0, b_q[:, :, None], 0), (b_q.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_q.shape[1])[None, :, None] == 0, tl.trans(b_k)[:, None, :], 0), (16, tl.trans(b_k).shape[1])).to(tl.float32)) if b_q.shape[1] < 16 else tl.dot(b_q, tl.trans(b_k)), 0).to(b_q.dtype)
    m_t = o_i[:, None] > o_i[None, :]
    b_kk = tl.where(m_t, tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_k.shape[1])[None, None, :] == 0, b_k[:, :, None], 0), (b_k.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_k.shape[1])[None, :, None] == 0, tl.trans(b_k)[:, None, :], 0), (16, tl.trans(b_k).shape[1])).to(tl.float32)) if b_k.shape[1] < 16 else tl.dot(b_k, tl.trans(b_k)), 0).to(b_k.dtype)
    p_beta = beta + i_bh * T + o_t
    b_beta = tl.load(p_beta, mask=m_b, other=0.0)
    b_k_beta = (b_k * b_beta[:, None]).to(b_k.dtype)
    b_qkT = (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_qk.shape[1])[None, None, :] == 0, b_qk[:, :, None], 0), (b_qk.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_qk.shape[1])[None, :, None] == 0, b_T[:, None, :], 0), (16, b_T.shape[1])).to(tl.float32)) if b_qk.shape[1] < 16 else tl.dot(b_qk, b_T)).to(b_k.dtype)
    if OUTPUT_ATTENTIONS:
        p_a = A_local + i_bh * T * BT + o_t[:, None] * BT + o_T[None, :]
        tl.store(p_a, b_qkT.to(p_a.dtype.element_ty), mask=m_T)
    b_kkT = (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_kk.shape[1])[None, None, :] == 0, b_kk[:, :, None], 0), (b_kk.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_kk.shape[1])[None, :, None] == 0, b_T[:, None, :], 0), (16, b_T.shape[1])).to(tl.float32)) if b_kk.shape[1] < 16 else tl.dot(b_kk, b_T)).to(b_k.dtype)
    p_o = o + i_bh * T * V + o_t[:, None] * V + o_v[None, :]
    tl.store(p_o, (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_qkT.shape[1])[None, None, :] == 0, b_qkT[:, :, None], 0), (b_qkT.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_qkT.shape[1])[None, :, None] == 0, b_v[:, None, :], 0), (16, b_v.shape[1])).to(tl.float32)) if b_qkT.shape[1] < 16 else tl.dot(b_qkT, b_v)).to(p_o.dtype.element_ty), mask=m_v)
    p_q_new = q_new + i_bh * T * K + o_t[:, None] * K + o_k[None, :]
    tl.store(p_q_new, (b_q - (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_qkT.shape[1])[None, None, :] == 0, b_qkT[:, :, None], 0), (b_qkT.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_qkT.shape[1])[None, :, None] == 0, b_k_beta[:, None, :], 0), (16, b_k_beta.shape[1])).to(tl.float32)) if b_qkT.shape[1] < 16 else tl.dot(b_qkT, b_k_beta))).to(p_q_new.dtype.element_ty), mask=m_qk)
    p_k_new = k_new + i_bh * T * K + o_t[:, None] * K + o_k[None, :]
    b_k_new = b_k - (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // tl.trans(b_kkT).shape[1])[None, None, :] == 0, tl.trans(b_kkT)[:, :, None], 0), (tl.trans(b_kkT).shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // tl.trans(b_kkT).shape[1])[None, :, None] == 0, b_k_beta[:, None, :], 0), (16, b_k_beta.shape[1])).to(tl.float32)) if tl.trans(b_kkT).shape[1] < 16 else tl.dot(tl.trans(b_kkT), b_k_beta))
    tl.store(p_k_new, b_k_new.to(p_k_new.dtype.element_ty), mask=m_qk)
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
SHAPES=((4,17,7,9,8),(6,33,11,13,16));DTYPES=('float32', 'float16', 'bfloat16');FIXED_META={"OUTPUT_ATTENTIONS":True}
def ref(args,meta):
    import numpy as np
    BH,T,K,V,BT=args["q"].shape[0],int(args["T"]),meta["K"],meta["V"],meta["BT"];q=args["q"]*np.float32(args["scale"]);k=args["k"];v=args["v"];beta=args["beta"];A=args["A"];out=np.zeros((BH,T,V),np.float32);qn=np.zeros_like(q);kn=np.zeros_like(k);local=np.zeros((BH,T,BT),np.float32)
    for n in range(BH):
      for s in range(0,T,BT):
       e=min(s+BT,T);qq=q[n,s:e];kk=k[n,s:e];vv=v[n,s:e];M=A[n,s:e,:e-s];qk=np.tril(qq@kk.T);kkt=np.tril(kk@kk.T,-1);qkT=qk@M;kkT=kkt@M;local[n,s:e,:]=qk@A[n,s:e,:];out[n,s:e]=qkT@vv;qn[n,s:e]=qq-qkT@(kk*beta[n,s:e,None]);kn[n,s:e]=kk-kkT.T@(kk*beta[n,s:e,None])
    return {"o":out.reshape(-1),"q_new":qn.reshape(-1),"k_new":kn.reshape(-1),"A_local":local.reshape(-1)}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    del dtype
    import numpy as np
    (BH, T, K, V, BT) = (int(x) for x in shape)
    NT = (T + BT - 1) // BT
    rng = fast_rng(seed)
    args = {'q': _aligned(rng.normal(0, 0.2, (BH, T, K))), 'k': _aligned(rng.normal(0, 0.2, (BH, T, K))), 'v': _aligned(rng.normal(0, 0.2, (BH, T, V))), 'beta': _aligned(rng.uniform(0.1, 0.9, (BH, T))), 'o': _aligned(np.full(BH * T * V, -7.0)), 'A': _aligned(rng.normal(0, 0.1, (BH, T, BT))), 'q_new': _aligned(np.full(BH * T * K, -7.0)), 'k_new': _aligned(np.full(BH * T * K, -7.0)), 'A_local': _aligned(np.full(BH * T * BT, -7.0)), 'scale': 0.7, 'T': T}
    meta = {**FIXED_META, 'K': K, 'V': V, 'BK': 1 << (int(K) - 1).bit_length(), 'BV': 1 << (int(V) - 1).bit_length(), 'BT': BT}
    grid = (NT, BH)
    outputs = ('o', 'q_new', 'k_new', 'A_local')
    return _case(chunk_transform_qk_fwd_kernel, grid, args, meta, ('q', 'k', 'v', 'beta', 'A'), outputs, ref(args, meta), shape, 'torch.float32', seed, {'grid_formula': '(ceil_div(T,BT),B*H)', 'outputs': outputs})

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
