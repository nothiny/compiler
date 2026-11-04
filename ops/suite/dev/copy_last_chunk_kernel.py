"""One-JIT standalone Triton compiler test case."""

COPIED_FROM = {'repo': 'ops-pool/fla', 'note': 'validated case layer intact; lottery 20261019'}
OPERATOR = {"name": "hidden/copy_last_chunk_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit(do_not_specialize=['T'])
def copy_last_chunk_kernel(q, k, v, g, level_scales, cu_seqlens, q_prev, k_prev, v_prev, g_prev, level_scales_prev, offsets, T, H: tl.constexpr, K: tl.constexpr, V: tl.constexpr, L: tl.constexpr, BT: tl.constexpr, IS_VARLEN: tl.constexpr, PAD_K: tl.constexpr, PAD_V: tl.constexpr):
    i_nh = tl.program_id(0).to(tl.int64)
    (i_n, i_h) = (i_nh // H, i_nh % H)
    if IS_VARLEN:
        (bos, eos) = (tl.load(cu_seqlens + i_n).to(tl.int64), tl.load(cu_seqlens + i_n + 1).to(tl.int64))
        T = (eos - bos).to(tl.int32)
    else:
        (bos, eos) = ((i_n * T).to(tl.int64), (i_n * T + T).to(tl.int64))
    seq_offset = T // BT * BT
    o_k = tl.arange(0, PAD_K)
    o_v = tl.arange(0, PAD_V)
    o_i = tl.arange(0, BT)
    o_t = seq_offset.to(tl.int64) + o_i
    m_t = o_t < T
    m_tk = m_t[:, None] & (o_k[None, :] < K)
    m_tv = m_t[:, None] & (o_v[None, :] < V)
    m_ik = (o_i[:, None] < BT) & (o_k[None, :] < K)
    m_iv = (o_i[:, None] < BT) & (o_v[None, :] < V)
    p_g = g + bos * H + i_h + o_t * H
    p_q = q + bos * K + o_t[:, None] * K + o_k[None, :]
    p_k = k + bos * K + o_t[:, None] * K + o_k[None, :]
    p_v = v + (bos * H + i_h) * V + o_t[:, None] * (H * V) + o_v[None, :]
    p_g_prev = g_prev + i_n * BT * H + i_h + o_i * H
    p_q_prev = q_prev + i_n * BT * K + o_i[:, None] * K + o_k[None, :]
    p_k_prev = k_prev + i_n * BT * K + o_i[:, None] * K + o_k[None, :]
    p_v_prev = v_prev + (i_n * BT * H + i_h) * V + o_i[:, None] * (H * V) + o_v[None, :]
    tl.store(p_g_prev, tl.load(p_g, mask=m_t, other=0.0), mask=o_i < BT)
    tl.store(p_q_prev, tl.load(p_q, mask=m_tk, other=0.0), mask=m_ik)
    tl.store(p_k_prev, tl.load(p_k, mask=m_tk, other=0.0), mask=m_ik)
    tl.store(p_v_prev, tl.load(p_v, mask=m_tv, other=0.0), mask=m_iv)
    for i in range(L):
        p_l = level_scales + (bos * H + i_h) * L + o_t[:, None] * (H * L) + i
        p_l_prev = level_scales_prev + (i_n * BT * H + i_h) * L + o_i[:, None] * (H * L) + i
        tl.store(p_l_prev, tl.load(p_l, mask=m_t[:, None], other=0.0), mask=o_i[:, None] < BT)
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
SHAPES = ((17,), (97,), (3, 17, 1, 6, 5));DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 T=int(args["T"]);H=int(meta["H"]);K=int(meta["K"]);V=int(meta["V"]);L=int(meta["L"]);BT=int(meta["BT"]);B=np.asarray(args["v"]).size//(T*H*V);start=(T//BT)*BT;n=T-start;q=np.zeros((B,BT,K),np.float32);kout=np.zeros_like(q);vout=np.zeros((B,BT,H,V),np.float32);gout=np.zeros((B,BT,H),np.float32);lout=np.zeros((B,BT,H,L),np.float32)
 if n:
  q[:,:n]=np.asarray(args["q"],np.float32).reshape(B,T,K)[:,start:];kout[:,:n]=np.asarray(args["k"],np.float32).reshape(B,T,K)[:,start:];vout[:,:n]=np.asarray(args["v"],np.float32).reshape(B,T,H,V)[:,start:];gout[:,:n]=np.asarray(args["g"],np.float32).reshape(B,T,H)[:,start:];lout[:,:n]=np.asarray(args["level_scales"],np.float32).reshape(B,T,H,L)[:,start:]
 return {"q_prev":q.reshape(-1),"k_prev":kout.reshape(-1),"v_prev":vout.reshape(-1),"g_prev":gout.reshape(-1),"level_scales_prev":lout.reshape(-1)}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    if len(shape) > 1 and tuple(shape) not in SHAPES:
        raise ValueError('unsupported explicit shape configuration')
    del dtype
    import numpy as np
    N = int(shape[0])
    rng = fast_rng(seed)
    B = int(shape[0]) if len(shape) > 1 else 2
    H = int(shape[2]) if len(shape) > 1 else 1
    T = int(shape[1]) if len(shape) > 1 else max(9, min(65, N | 1))
    K = int(shape[3]) if len(shape) > 1 else 6
    V = int(shape[4]) if len(shape) > 1 else 5
    L = 3
    BT = 8
    args = {'q': _aligned(rng.normal(0, 0.3, (B, T, K)), 'float32'), 'k': _aligned(rng.normal(0, 0.3, (B, T, K)), 'float32'), 'v': _aligned(rng.normal(0, 0.3, (B, T, H, V)), 'float32'), 'g': _aligned(rng.normal(0, 0.1, (B, T, H)), 'float32'), 'level_scales': _aligned(rng.normal(0, 0.2, (B, T, H, L)), 'float32'), 'cu_seqlens': _aligned(np.arange(B + 1) * T, 'int64'), 'q_prev': _aligned(np.full(B * BT * K, -7), 'float32'), 'k_prev': _aligned(np.full(B * BT * K, -7), 'float32'), 'v_prev': _aligned(np.full(B * BT * H * V, -7), 'float32'), 'g_prev': _aligned(np.full(B * BT * H, -7), 'float32'), 'level_scales_prev': _aligned(np.full(B * BT * H * L, -7), 'float32'), 'offsets': _aligned(np.zeros(B, dtype=np.int64), 'int64'), 'T': T}
    meta = {'H': H, 'K': K, 'V': V, 'L': L, 'BT': BT, 'IS_VARLEN': False}
    grid = (B * H,)
    outputs = ('q_prev', 'k_prev', 'v_prev', 'g_prev', 'level_scales_prev')
    return _case(copy_last_chunk_kernel, grid, args, meta, ('q', 'k', 'v', 'g', 'level_scales'), outputs, ref(args, meta), shape, 'torch.float32', seed, {'complete_launch_plan': True, 'formula': 'copy the final incomplete chunk into fixed BT buffers with zero padding'})

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
    case["meta"]["PAD_K"] = 1 << (int(case["meta"]["K"]) - 1).bit_length()
    case["meta"]["PAD_V"] = 1 << (int(case["meta"]["V"]) - 1).bit_length()
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
