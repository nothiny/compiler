"""chunk_gdn2_fwd_kernel_intra_sub_chunk: 从 ~/ops 仓库复制(core @ ops-pool),保留其已验证的 case 层。

模式: args.runtime_scalar、cast.to、control.for_range、control.if、control.loop_carried、creation.arange、creation.full、creation.where、dtype.float32、dtype.int32。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。循环上界来自运行时标量(不是 constexpr)。constexpr 参数: H, K, BT, BC, BK, IS_VARLEN, USE_GATHER。

文件只有两层:
  ① chunk_gdn2_fwd_kernel_intra_sub_chunk   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/chunk_gdn2_fwd_kernel_intra_sub_chunk', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'cast.to', 'control.for_range', 'control.if', 'control.loop_carried', 'creation.arange', 'creation.full', 'creation.where', 'dtype.float32', 'dtype.int32', 'dtype.int64', 'linalg.dot', 'math.exp2', 'memory.load', 'memory.load.masked', 'memory.load.other', 'memory.store', 'memory.store.masked', 'reduce.min', 'reduce.sum.axis0', 'shape.reshape', 'shape.trans', 'tile.2d', 'tile.3d']}
COPIED_FROM = {'repo': 'core @ ops-pool', 'note': 'validated case layer intact'}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit(do_not_specialize=['T'])
def chunk_gdn2_fwd_kernel_intra_sub_chunk(q, k, g, b, Aqk, Akk, scale, cu_seqlens, chunk_indices, T, H: tl.constexpr, K: tl.constexpr, BT: tl.constexpr, BC: tl.constexpr, BK: tl.constexpr, IS_VARLEN: tl.constexpr, USE_GATHER: tl.constexpr):
    (i_t, i_i, i_bh) = (tl.program_id(0).to(tl.int64), tl.program_id(1), tl.program_id(2).to(tl.int64))
    (i_b, i_h) = (i_bh // H, i_bh % H)
    if IS_VARLEN:
        (i_n, i_t) = (tl.load(chunk_indices + i_t * 2).to(tl.int32), tl.load(chunk_indices + i_t * 2 + 1).to(tl.int64))
        (bos, eos) = (tl.load(cu_seqlens + i_n).to(tl.int64), tl.load(cu_seqlens + i_n + 1).to(tl.int64))
        T = eos - bos
    else:
        (bos, eos) = (i_b * T, i_b * T + T)
    i_ti = i_t * BT + i_i * BC
    if i_ti >= T:
        return
    o_c = i_ti + tl.arange(0, BC)
    m_c = o_c < T
    q = q + (bos * H + i_h) * K
    k = k + (bos * H + i_h) * K
    g = g + (bos * H + i_h) * K
    b = b + (bos * H + i_h) * K
    Aqk = Aqk + (bos * H + i_h) * BT
    Akk = Akk + (bos * H + i_h) * BC
    o_k = tl.arange(0, BK)
    m_kc = m_c[:, None] & (o_k[None, :] < K)
    p_q = q + o_c[:, None] * (H * K) + o_k[None, :]
    p_k = k + o_c[:, None] * (H * K) + o_k[None, :]
    p_g = g + o_c[:, None] * (H * K) + o_k[None, :]
    p_b = b + o_c[:, None] * (H * K) + o_k[None, :]
    b_q = tl.load(p_q, mask=m_kc, other=0.0)
    b_k = tl.load(p_k, mask=m_kc, other=0.0)
    b_g = tl.load(p_g, mask=m_kc, other=0.0)
    b_b = tl.load(p_b, mask=m_kc, other=0.0)
    if USE_GATHER:
        _inl_1_gather_src = b_g
        _inl_1_gather_index = tl.full([1, BK], min(BC // 2, T - i_ti - 1), dtype=tl.int16)
        _inl_1_gather_axis: tl.constexpr = 0
        _inl_1_gather__builder: tl.constexpr = None
        '\n        Gather operation that works when tl.gather is not supported.\n        This is a fallback implementation that returns None.\n        Just to make triton compiler happy.\n        '
        _inl_1_gather_result = None
        b_gn = _inl_1_gather_result
    else:
        p_gn = g + (i_ti + min(BC // 2, T - i_ti - 1)) * H * K + tl.arange(0, BK)
        b_gn = tl.load(p_gn, mask=tl.arange(0, BK) < K, other=0.0)
        b_gn = b_gn[None, :]
    b_gm = (b_g - b_gn).to(tl.float32)
    _inl_2_exp2_x = b_gm
    _inl_2_exp2_result = tl.exp2(_inl_2_exp2_x.to(tl.float32))
    b_gq = tl.where(m_c[:, None], _inl_2_exp2_result, 0.0)
    _inl_3_exp2_x = -b_gm
    _inl_3_exp2_result = tl.exp2(_inl_3_exp2_x.to(tl.float32))
    b_gk = tl.where(m_c[:, None], _inl_3_exp2_result, 0.0)
    b_kgt = tl.trans(b_k * b_gk)
    b_bk = (b_b.to(tl.float32) * b_k.to(tl.float32)).to(b_k.dtype)
    b_Aqk = (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // (b_q * b_gq).shape[1])[None, None, :] == 0, (b_q * b_gq)[:, :, None], 0), ((b_q * b_gq).shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // (b_q * b_gq).shape[1])[None, :, None] == 0, b_kgt[:, None, :], 0), (16, b_kgt.shape[1])).to(tl.float32)) if (b_q * b_gq).shape[1] < 16 else tl.dot(b_q * b_gq, b_kgt)) * scale
    b_Akk = tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // (b_bk * b_gq).shape[1])[None, None, :] == 0, (b_bk * b_gq)[:, :, None], 0), ((b_bk * b_gq).shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // (b_bk * b_gq).shape[1])[None, :, None] == 0, b_kgt[:, None, :], 0), (16, b_kgt.shape[1])).to(tl.float32)) if (b_bk * b_gq).shape[1] < 16 else tl.dot(b_bk * b_gq, b_kgt)
    o_i = tl.arange(0, BC)
    m_Aqk = o_i[:, None] >= o_i[None, :]
    m_Akk = o_i[:, None] > o_i[None, :]
    m_I = o_i[:, None] == o_i[None, :]
    b_Aqk = tl.where(m_Aqk, b_Aqk, 0.0)
    b_Akk = tl.where(m_Akk, b_Akk, 0.0)
    m_Aqk = m_c[:, None] & ((i_i * BC + o_i)[None, :] < BT)
    m_Akk = m_c[:, None] & (o_i[None, :] < BC)
    p_Aqk = Aqk + o_c[:, None] * (H * BT) + (i_i * BC + o_i)[None, :]
    p_Akk = Akk + o_c[:, None] * (H * BC) + o_i[None, :]
    tl.store(p_Aqk, b_Aqk.to(Aqk.dtype.element_ty), mask=m_Aqk)
    tl.store(p_Akk, b_Akk.to(Akk.dtype.element_ty), mask=m_Akk)
    tl.debug_barrier()
    b_Ai = -b_Akk
    for i in range(2, min(BC, T - i_ti)):
        b_a = -tl.load(Akk + (i_ti + i) * H * BC + o_i)
        b_a = tl.where(o_i < i, b_a, 0.0)
        b_a += tl.sum(b_a[:, None] * b_Ai, 0)
        b_Ai = tl.where((o_i == i)[:, None], b_a, b_Ai)
    b_Ai += m_I
    tl.store(p_Akk, b_Ai.to(Akk.dtype.element_ty), mask=m_Akk)

# ------------------------------------------------------------------ ② case 层

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
    if _comparison_dtype_policy == 'float32':
        (rtol, atol) = (0.0001, 0.0001)
    elif _comparison_dtype_policy == 'bfloat16':
        (rtol, atol) = (0.01, 0.01)
    comparison = {name: {'profile': 'numerical', 'comparator': 'allclose', 'exact': False, 'rtol': float(rtol), 'atol': float(atol), 'equal_nan': True} for name in outputs}
    arrays = {name: value for (name, value) in args.items() if isinstance(value, np.ndarray)}
    return {'kernel': kernel, 'grid': tuple((int(value) for value in grid)), 'args': args, 'meta': meta, 'launch_meta': {'num_warps': 4, 'num_stages': 1}, 'inputs': tuple(inputs), 'outputs': tuple(outputs), 'expected': expected, 'comparison': comparison, 'pointer_dtypes': {name: str(value.dtype) for (name, value) in arrays.items()}, 'buffer_extents': {name: int(value.size) for (name, value) in arrays.items()}, 'buffer_layouts': {name: {'shape': tuple((int(x) for x in value.shape)), 'strides': tuple((int(x // value.dtype.itemsize) for x in value.strides))} for (name, value) in arrays.items()}, 'alignment': 64, 'aliases': {}, 'seed': int(seed), 'shape': tuple(shape), 'dtype': str(dtype), 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'coverage': {'complete_logical_output': True, **coverage}}

SHAPES=((2, 17, 3, 7, 8, 4), (3, 17, 3, 7, 8, 4));DTYPES=('float32', 'float16', 'bfloat16');FIXED_META={"IS_VARLEN":False,"USE_GATHER":False}
SHAPES=((2, 17, 3, 7, 8, 4), (3, 17, 3, 7, 8, 4));DTYPES=('float32', 'float16', 'bfloat16');FIXED_META={"IS_VARLEN":False,"USE_GATHER":False}
SHAPES=((2, 17, 3, 7, 8, 4), (3, 17, 3, 7, 8, 4));DTYPES=('float32', 'float16', 'bfloat16');FIXED_META={"IS_VARLEN":False,"USE_GATHER":False}
def ref(args,meta):
 import numpy as np
 B,T,H,K,BT,BC=args["cu_seqlens"].size-1,int(args["T"]),meta["H"],meta["K"],meta["BT"],meta["BC"];q=args["q"].reshape(B,T,H,K);k=args["k"].reshape(B,T,H,K);g=args["g"].reshape(B,T,H,K);bb=args["b"].reshape(B,T,H,K);aq=args["Aqk"].copy().reshape(B,T,H,BT);ak=args["Akk"].copy().reshape(B,T,H,BC)
 for n in range(B):
  for h in range(H):
   for s in range(0,T,BT):
    for sub in range(BT//BC):
     a=s+sub*BC;e=min(a+BC,T)
     if a>=T:continue
     aq[n,a:e,h,sub*BC:(sub+1)*BC]=0;ak[n,a:e,h,:]=0
     pivot=min(a+BC//2,T-1);Gq=np.exp2(g[n,a:e,h]-g[n,pivot,h]);Gk=1/Gq;rawq=(q[n,a:e,h]*Gq)@(k[n,a:e,h]*Gk).T*np.float32(args["scale"]);rawk=(bb[n,a:e,h]*k[n,a:e,h]*Gq)@(k[n,a:e,h]*Gk).T;aq[n,a:e,h,sub*BC:sub*BC+e-a]=np.tril(rawq);L=np.tril(rawk,-1);R=-L.copy()
     for i in range(2,e-a):R[i,:i]=-L[i,:i]+(-L[i])@R[:,:i]
     ak[n,a:e,h,:e-a]=R+np.eye(e-a,dtype=np.float32)
 return {"Aqk":aq.reshape(-1),"Akk":ak.reshape(-1)}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    del dtype
    import numpy as np
    (B, T, H, K, BT, BC) = (int(x) for x in shape)
    NT = (T + BT - 1) // BT
    from case_utils import fast_rng
    rng = fast_rng(seed)
    args = {n: _aligned(rng.normal(0, 0.2, (B, T, H, K))) for n in ('q', 'k', 'b')}
    args.update({'g': _aligned(rng.normal(0, 0.1, (B, T, H, K))), 'Aqk': _aligned(np.full(B * T * H * BT, -7.0)), 'Akk': _aligned(np.full(B * T * H * BC, -7.0)), 'scale': K ** (-0.5), 'cu_seqlens': _aligned(np.arange(B + 1) * T, 'int32'), 'chunk_indices': _aligned(np.zeros(2 * B * NT), 'int32'), 'T': T})
    meta = {**FIXED_META, 'H': H, 'K': K, 'BT': BT, 'BC': BC, 'BK': 1 << (int(K) - 1).bit_length()}
    grid = (NT, BT // BC, B * H)
    outputs = ('Aqk', 'Akk')
    return _case(chunk_gdn2_fwd_kernel_intra_sub_chunk, grid, args, meta, ('q', 'k', 'g', 'b'), outputs, ref(args, meta), shape, 'float32', seed, {'grid_formula': '(ceil_div(T,BT),BT/BC,B*H)', 'outputs': outputs})
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


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float32'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float32': 'float32'}


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
