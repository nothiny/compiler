"""One-JIT standalone Triton compiler test case."""

COPIED_FROM = {'repo': 'ops-pool/core', 'note': 'validated case layer intact; lottery 20261019'}
OPERATOR = {"name": "hidden/chunk_gdn2_fwd_kernel_intra_token_parallel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["fla"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit(do_not_specialize=['T', 'N'])
def chunk_gdn2_fwd_kernel_intra_token_parallel(q, k, g, b, Aqk, Akk, scale, cu_seqlens, N, T, H: tl.constexpr, K: tl.constexpr, BK: tl.constexpr, BT: tl.constexpr, BC: tl.constexpr, BH: tl.constexpr, IS_VARLEN: tl.constexpr):
    (i_tg, i_hg) = (tl.program_id(0).to(tl.int64), tl.program_id(1))
    if IS_VARLEN:
        i_n = 0
        (left, right) = (0, N)
        for _ in range(20):
            if left < right:
                mid = (left + right) // 2
                if i_tg < tl.load(cu_seqlens + mid + 1).to(tl.int32):
                    right = mid
                else:
                    left = mid + 1
        i_n = left
        (bos, eos) = (tl.load(cu_seqlens + i_n).to(tl.int64), tl.load(cu_seqlens + i_n + 1).to(tl.int64))
        T = eos - bos
        i_t = i_tg - bos
    else:
        bos = i_tg // T * T
        i_t = i_tg % T
    if i_t >= T:
        return
    i_c = i_t // BT
    i_s = i_t % BT // BC
    i_tc = i_c * BT
    i_ts = i_tc + i_s * BC
    q += bos * H * K
    k += bos * H * K
    g += bos * H * K
    b += bos * H * K
    Aqk += bos * H * BT
    Akk += bos * H * BC
    o_h = tl.arange(0, BH)
    o_k = tl.arange(0, BK)
    m_h = i_hg * BH + o_h < H
    m_k = o_k < K
    p_q = q + i_t * H * K + (i_hg * BH + o_h)[:, None] * K + o_k[None, :]
    p_k = k + i_t * H * K + (i_hg * BH + o_h)[:, None] * K + o_k[None, :]
    p_g = g + i_t * H * K + (i_hg * BH + o_h)[:, None] * K + o_k[None, :]
    p_b = b + i_t * H * K + (i_hg * BH + o_h)[:, None] * K + o_k[None, :]
    b_q = tl.load(p_q, mask=m_h[:, None] & m_k[None, :], other=0.0).to(tl.float32)
    b_k = tl.load(p_k, mask=m_h[:, None] & m_k[None, :], other=0.0).to(tl.float32)
    b_g = tl.load(p_g, mask=m_h[:, None] & m_k[None, :], other=0.0).to(tl.float32)
    b_b = tl.load(p_b, mask=m_h[:, None] & m_k[None, :], other=0.0).to(tl.float32)
    b_k = b_k * b_b
    for j in range(i_ts, min(i_t + 1, min(T, i_ts + BC))):
        p_kj = k + j * H * K + (i_hg * BH + o_h)[:, None] * K + o_k[None, :]
        p_gj = g + j * H * K + (i_hg * BH + o_h)[:, None] * K + o_k[None, :]
        b_kj = tl.load(p_kj, mask=m_h[:, None] & m_k[None, :], other=0.0).to(tl.float32)
        b_gj = tl.load(p_gj, mask=m_h[:, None] & m_k[None, :], other=0.0).to(tl.float32)
        _inl_1_exp2_x = b_g - b_gj
        _inl_1_exp2_result = tl.exp2(_inl_1_exp2_x.to(tl.float32))
        b_kgj = b_kj * _inl_1_exp2_result
        b_kgj = tl.where(m_k[None, :], b_kgj, 0.0)
        b_Aqk = tl.sum(b_q * b_kgj, axis=1) * scale
        b_Akk = tl.sum(b_k * b_kgj, axis=1) * tl.where(j < i_t, 1.0, 0.0)
        tl.store(Aqk + i_t * H * BT + (i_hg * BH + o_h) * BT + j % BT, b_Aqk.to(Aqk.dtype.element_ty), mask=m_h)
        tl.store(Akk + i_t * H * BC + (i_hg * BH + o_h) * BC + j - i_ts, b_Akk.to(Akk.dtype.element_ty), mask=m_h)
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
SHAPES=((2, 17, 5, 7, 8, 4), (3, 17, 5, 7, 8, 4));DTYPES=('float32', 'float16', 'bfloat16');FIXED_META={"IS_VARLEN":False}

def ref(args,meta):
 import numpy as np
 N,T,H,K,BT,BC=int(args["N"]),int(args["T"]),meta["H"],meta["K"],meta["BT"],meta["BC"];q=args["q"].reshape(N,T,H,K);k=args["k"].reshape(N,T,H,K);g=args["g"].reshape(N,T,H,K);bb=args["b"].reshape(N,T,H,K);aq=args["Aqk"].copy().reshape(N,T,H,BT);ak=args["Akk"].copy().reshape(N,T,H,BC)
 for n in range(N):
  for t in range(T):
   start=(t//BT)*BT+(t%BT//BC)*BC
   for j in range(start,t+1):dec=np.exp2(g[n,t]-g[n,j]);aq[n,t,:,j%BT]=np.sum(q[n,t]*k[n,j]*dec,axis=1)*np.float32(args["scale"]);ak[n,t,:,j-start]=np.sum((bb[n,t]*k[n,t])*k[n,j]*dec,axis=1)*(j<t)
 return {"Aqk":aq.reshape(-1),"Akk":ak.reshape(-1)}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    del dtype
    import numpy as np
    (N, T, H, K, BT, BC) = (int(x) for x in shape)
    rng = fast_rng(seed)
    args = {n: _aligned(rng.normal(0, 0.2, (N, T, H, K))) for n in ('q', 'k', 'b')}
    args.update({'g': _aligned(rng.normal(0, 0.1, (N, T, H, K))), 'Aqk': _aligned(np.full(N * T * H * BT, -7.0)), 'Akk': _aligned(np.full(N * T * H * BC, -7.0)), 'scale': K ** (-0.5), 'cu_seqlens': _aligned(np.arange(N + 1) * T, 'int32'), 'N': N, 'T': T})
    meta = {**FIXED_META, 'H': H, 'K': K, 'BK': 1 << (int(K) - 1).bit_length(), 'BT': BT, 'BC': BC, 'BH': 4}
    grid = (N * T, (H + 3) // 4)
    outputs = ('Aqk', 'Akk')
    return _case(chunk_gdn2_fwd_kernel_intra_token_parallel, grid, args, meta, ('q', 'k', 'g', 'b'), outputs, ref(args, meta), shape, 'torch.float32', seed, {'grid_formula': '(N*T,ceil_div(H,BH))', 'outputs': outputs})

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
