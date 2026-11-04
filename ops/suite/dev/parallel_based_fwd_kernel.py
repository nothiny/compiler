"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/parallel_based_fwd_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["fla"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit(do_not_specialize=['T'])
def parallel_based_fwd_kernel(q, k, v, o, z, scale, T, B: tl.constexpr, H: tl.constexpr, K: tl.constexpr, V: tl.constexpr, BTL: tl.constexpr, BTS: tl.constexpr, BK: tl.constexpr, BV: tl.constexpr):
    (i_kv, i_c, i_bh) = (tl.program_id(0), tl.program_id(1).to(tl.int64), tl.program_id(2).to(tl.int64))
    NV = tl.cdiv(V, BV)
    i_k = i_kv // NV
    i_v = i_kv % NV
    o_t = i_c * BTL + tl.arange(0, BTL)
    o_kk = i_k * BK + tl.arange(0, BK)
    o_vv = i_v * BV + tl.arange(0, BV)
    m_t = o_t < T
    m_q = m_t[:, None] & (o_kk[None, :] < K)
    m_o = m_t[:, None] & (o_vv[None, :] < V)
    p_q = q + i_bh * T * K + o_t[:, None] * K + o_kk[None, :]
    b_q = tl.load(p_q, mask=m_q, other=0.0)
    b_q = (b_q * scale).to(b_q.dtype)
    b_o = tl.zeros([BTL, BV], dtype=tl.float32)
    b_z = tl.zeros([BTL], dtype=tl.float32)
    for i_s in range(0, i_c * BTL, BTS):
        o_s = i_s + tl.arange(0, BTS)
        m_k = (o_kk[:, None] < K) & (o_s[None, :] < T)
        m_v = (o_s[:, None] < T) & (o_vv[None, :] < V)
        p_k = k + i_bh * T * K + o_kk[:, None] + o_s[None, :] * K
        p_v = v + i_bh * T * V + o_s[:, None] * V + o_vv[None, :]
        b_k = tl.load(p_k, mask=m_k, other=0.0)
        b_v = tl.load(p_v, mask=m_v, other=0.0)
        b_s = tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_q.shape[1])[None, None, :] == 0, b_q[:, :, None], 0), (b_q.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_q.shape[1])[None, :, None] == 0, b_k[:, None, :], 0), (16, b_k.shape[1])).to(tl.float32)) if b_q.shape[1] < 16 else tl.dot(b_q, b_k)
        b_s = 1 + b_s + 0.5 * b_s * b_s
        b_z += tl.sum(b_s, axis=1)
        b_o = b_o + (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_s.to(b_v.dtype).shape[1])[None, None, :] == 0, b_s.to(b_v.dtype)[:, :, None], 0), (b_s.to(b_v.dtype).shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_s.to(b_v.dtype).shape[1])[None, :, None] == 0, b_v[:, None, :], 0), (16, b_v.shape[1])).to(tl.float32)) if b_s.to(b_v.dtype).shape[1] < 16 else tl.dot(b_s.to(b_v.dtype), b_v))
    tl.debug_barrier()
    o_q = tl.arange(0, BTL)
    o_k = tl.arange(0, BTS)
    for i_s in range(i_c * BTL, (i_c + 1) * BTL, BTS):
        o_s = i_s + tl.arange(0, BTS)
        m_k = (o_kk[:, None] < K) & (o_s[None, :] < T)
        m_v = (o_s[:, None] < T) & (o_vv[None, :] < V)
        p_k = k + i_bh * T * K + o_kk[:, None] + o_s[None, :] * K
        p_v = v + i_bh * T * V + o_s[:, None] * V + o_vv[None, :]
        b_k = tl.load(p_k, mask=m_k, other=0.0)
        b_v = tl.load(p_v, mask=m_v, other=0.0)
        m_s = o_q[:, None] >= o_k[None, :]
        b_s = tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_q.shape[1])[None, None, :] == 0, b_q[:, :, None], 0), (b_q.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_q.shape[1])[None, :, None] == 0, b_k[:, None, :], 0), (16, b_k.shape[1])).to(tl.float32)) if b_q.shape[1] < 16 else tl.dot(b_q, b_k)
        b_s = 1 + b_s + 0.5 * b_s * b_s
        b_s = tl.where(m_s, b_s, 0)
        b_z += tl.sum(b_s, axis=1)
        b_o += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_s.to(b_q.dtype).shape[1])[None, None, :] == 0, b_s.to(b_q.dtype)[:, :, None], 0), (b_s.to(b_q.dtype).shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_s.to(b_q.dtype).shape[1])[None, :, None] == 0, b_v[:, None, :], 0), (16, b_v.shape[1])).to(tl.float32)) if b_s.to(b_q.dtype).shape[1] < 16 else tl.dot(b_s.to(b_q.dtype), b_v)
        o_k += BTS
    p_o = o + (i_bh + B * H * i_k) * T * V + o_t[:, None] * V + o_vv[None, :]
    p_z = z + (i_bh + B * H * i_k) * T + i_c * BTL + tl.arange(0, BTL)
    tl.store(p_o, b_o.to(p_o.dtype.element_ty), mask=m_o)
    tl.store(p_z, b_z.to(p_z.dtype.element_ty), mask=i_c * BTL + tl.arange(0, BTL) < T)
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
def _based_forward(q,k,v,scale):
    import numpy as np
    BH,T,K=q.shape;out=np.zeros((BH,T,v.shape[2]),np.float32);normalizer=np.zeros((BH,T),np.float32)
    for n in range(BH):
        scores=(q[n]*np.float32(scale))@k[n].T;weights=1+scores+np.float32(.5)*scores*scores;weights=np.tril(weights);out[n]=weights@v[n];normalizer[n]=np.sum(weights,axis=1)
    return out,normalizer


def _based_backward(q,k,v,do,dz,scale):
    import numpy as np
    BH,T,K=q.shape;dq=np.zeros_like(q);dk=np.zeros_like(k);dv=np.zeros_like(v)
    for n in range(BH):
        scores=(q[n]*np.float32(scale))@k[n].T;mask=np.tri(T,dtype=np.float32);weights=(1+scores+np.float32(.5)*scores*scores)*mask;dweight=(do[n]@v[n].T+dz[n,:,None])*mask;ds=dweight*(1+scores);dq[n]=(ds@k[n])*np.float32(scale);dk[n]=(ds.T@q[n])*np.float32(scale);dv[n]=weights.T@do[n]
    return dq,dk,dv

SHAPES=((4,17,7,9,8),(6,33,11,13,16));DTYPES=('float32', 'float16', 'bfloat16')
def ref(args,meta):
    o,z=_based_forward(args["q"],args["k"],args["v"],args["scale"]);return {"o":o.reshape(-1),"z":z.reshape(-1)}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    del dtype
    import numpy as np
    (BH, T, K, V, BTL) = (int(x) for x in shape)
    rng = fast_rng(seed)
    args = {'q': _aligned(rng.normal(0, 0.2, (BH, T, K))), 'k': _aligned(rng.normal(0, 0.2, (BH, T, K))), 'v': _aligned(rng.normal(0, 0.2, (BH, T, V))), 'o': _aligned(np.full(BH * T * V, -7.0)), 'z': _aligned(np.full(BH * T, -7.0)), 'scale': K ** (-0.5), 'T': T}
    meta = {'B': 2, 'H': BH // 2, 'K': K, 'V': V, 'BTL': BTL, 'BTS': 4, 'BK': 1 << (int(K) - 1).bit_length(), 'BV': 1 << (int(V) - 1).bit_length()}
    grid = (1, (T + BTL - 1) // BTL, BH)
    outputs = ('o', 'z')
    return _case(parallel_based_fwd_kernel, grid, args, meta, ('q', 'k', 'v'), outputs, ref(args, meta), shape, 'torch.float32', seed, {'grid_formula': '(ceil_div(K,BK)*ceil_div(V,BV),ceil_div(T,BTL),B*H)', 'outputs': outputs})

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
