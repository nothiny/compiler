"""parallel_attn_fwd_kernel: 从 ~/ops 仓库复制(core @ ops),保留其已验证的 case 层。

模式: args.runtime_scalar、cast.to、control.for_range、control.if、control.loop_carried、creation.arange、creation.full、creation.where、creation.zeros、dtype.float32。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。循环上界来自运行时标量(不是 constexpr)。constexpr 参数: W, B, H, HQ, G, K, V, BT, BS, BK, BV, USE_G, USE_SINK_BIAS, USE_WINDOW, IS_VARLEN。

文件只有两层:
  ① parallel_attn_fwd_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/parallel_attn_fwd_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'cast.to', 'control.for_range', 'control.if', 'control.loop_carried', 'creation.arange', 'creation.full', 'creation.where', 'creation.zeros', 'dtype.float32', 'dtype.int32', 'dtype.int64', 'linalg.dot', 'math.exp2', 'math.log2', 'math.maximum', 'memory.load', 'memory.load.masked', 'memory.load.other', 'memory.store', 'memory.store.masked', 'reduce.max.axis1', 'reduce.min', 'reduce.sum.axis1', 'shape.reshape', 'tile.2d', 'tile.3d']}
COPIED_FROM = {'repo': 'core @ ops', 'note': 'validated case layer intact', 'lines': 216}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def parallel_attn_fwd_kernel(q, k, v, o, g_cumsum, sink_bias, lse, scale, cu_seqlens, chunk_indices, T, W: tl.constexpr, B: tl.constexpr, H: tl.constexpr, HQ: tl.constexpr, G: tl.constexpr, K: tl.constexpr, V: tl.constexpr, BT: tl.constexpr, BS: tl.constexpr, BK: tl.constexpr, BV: tl.constexpr, USE_G: tl.constexpr, USE_SINK_BIAS: tl.constexpr, USE_WINDOW: tl.constexpr, IS_VARLEN: tl.constexpr):
    (i_v, i_t, i_bh) = (tl.program_id(0), tl.program_id(1).to(tl.int64), tl.program_id(2).to(tl.int64))
    (i_b, i_hq) = (i_bh // HQ, i_bh % HQ)
    i_h = i_hq // G
    if IS_VARLEN:
        (i_n, i_t) = (tl.load(chunk_indices + i_t * 2).to(tl.int32), tl.load(chunk_indices + i_t * 2 + 1).to(tl.int64))
        (bos, eos) = (tl.load(cu_seqlens + i_n).to(tl.int64), tl.load(cu_seqlens + i_n + 1).to(tl.int64))
        T = (eos - bos).to(tl.int32)
    else:
        i_n = i_b
        (bos, eos) = ((i_n * T).to(tl.int64), (i_n * T + T).to(tl.int64))
    RCP_LN2: tl.constexpr = 1.4426950216
    o_q = i_t * BT + tl.arange(0, BT)
    o_d = tl.arange(0, BK)
    o_v = i_v * BV + tl.arange(0, BV)
    m_q = o_q < T
    p_q = q + (bos * HQ + i_hq) * K + o_q[:, None] * (HQ * K) + o_d[None, :]
    p_o = o + (bos * HQ + i_hq) * V + o_q[:, None] * (HQ * V) + o_v[None, :]
    p_lse = lse + bos * HQ + i_hq + o_q * HQ
    b_q = tl.load(p_q, mask=m_q[:, None] & (o_d[None, :] < K), other=0.0)
    b_o = tl.zeros([BT, BV], dtype=tl.float32)
    b_m = tl.full([BT], float('-inf'), dtype=tl.float32)
    b_acc = tl.zeros([BT], dtype=tl.float32)
    if USE_G:
        p_g = g_cumsum + bos * HQ + i_hq + o_q * HQ
        b_gq = tl.load(p_g, mask=m_q, other=0.0).to(tl.float32)
    else:
        b_gq = None
    if USE_SINK_BIAS:
        b_sink_bias = tl.load(sink_bias + i_hq).to(tl.float32)
    else:
        b_sink_bias = None
    i_start = tl.maximum((i_t * BT - W + 1) // BS * BS, 0) if USE_WINDOW else 0
    for i_s in range(i_start, i_t * BT, BS):
        o_k = i_s + tl.arange(0, BS)
        m_k = o_k < T
        p_k = k + (bos * H + i_h) * K + o_d[:, None] + o_k[None, :] * (H * K)
        p_v = v + (bos * H + i_h) * V + o_k[:, None] * (H * V) + o_v[None, :]
        b_k = tl.load(p_k, mask=(o_d[:, None] < K) & m_k[None, :], other=0.0)
        b_v = tl.load(p_v, mask=m_k[:, None] & (o_v[None, :] < V), other=0.0)
        b_s = (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_q.shape[1])[None, None, :] == 0, b_q[:, :, None], 0), (b_q.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_q.shape[1])[None, :, None] == 0, b_k[:, None, :], 0), (16, b_k.shape[1])).to(tl.float32)) if b_q.shape[1] < 16 else tl.dot(b_q, b_k)) * scale * RCP_LN2
        if USE_G:
            b_gk = tl.load(g_cumsum + (bos + o_k) * HQ + i_hq, mask=m_k, other=0).to(tl.float32)
            b_s += b_gq[:, None] - b_gk[None, :]
        if USE_WINDOW:
            b_s = tl.where((o_q[:, None] - o_k[None, :] < W) & m_k[None, :], b_s, float('-inf'))
        (b_m, b_mp) = (tl.maximum(b_m, tl.max(b_s, 1)), b_m)
        b_mw = tl.where(b_m == float('-inf'), 0.0, b_m)
        _inl_1_exp2_x = b_mp - b_mw
        _inl_1_exp2_result = tl.exp2(_inl_1_exp2_x.to(tl.float32))
        b_r = _inl_1_exp2_result
        _inl_2_exp2_x = b_s - b_mw[:, None]
        _inl_2_exp2_result = tl.exp2(_inl_2_exp2_x.to(tl.float32))
        b_p = _inl_2_exp2_result
        b_acc = b_acc * b_r + tl.sum(b_p, 1)
        b_o = b_o * b_r[:, None] + (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_p.to(b_q.dtype).shape[1])[None, None, :] == 0, b_p.to(b_q.dtype)[:, :, None], 0), (b_p.to(b_q.dtype).shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_p.to(b_q.dtype).shape[1])[None, :, None] == 0, b_v[:, None, :], 0), (16, b_v.shape[1])).to(tl.float32)) if b_p.to(b_q.dtype).shape[1] < 16 else tl.dot(b_p.to(b_q.dtype), b_v))
        b_mp = b_m
    for i_s in range(i_t * BT, min((i_t + 1) * BT, T), BS):
        o_k = i_s + tl.arange(0, BS)
        m_k = o_k < T
        p_k = k + (bos * H + i_h) * K + o_d[:, None] + o_k[None, :] * (H * K)
        p_v = v + (bos * H + i_h) * V + o_k[:, None] * (H * V) + o_v[None, :]
        b_k = tl.load(p_k, mask=(o_d[:, None] < K) & m_k[None, :], other=0.0)
        b_v = tl.load(p_v, mask=m_k[:, None] & (o_v[None, :] < V), other=0.0)
        b_s = (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_q.shape[1])[None, None, :] == 0, b_q[:, :, None], 0), (b_q.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_q.shape[1])[None, :, None] == 0, b_k[:, None, :], 0), (16, b_k.shape[1])).to(tl.float32)) if b_q.shape[1] < 16 else tl.dot(b_q, b_k)) * scale * RCP_LN2
        if USE_G:
            b_gk = tl.load(g_cumsum + (bos + o_k) * HQ + i_hq, mask=m_k, other=0).to(tl.float32)
            b_s += b_gq[:, None] - b_gk[None, :]
        m_s = (o_q[:, None] >= o_k[None, :]) & m_k[None, :]
        if USE_WINDOW:
            m_s = m_s & (o_q[:, None] - o_k[None, :] < W)
        b_s = tl.where(m_s, b_s, float('-inf'))
        (b_m, b_mp) = (tl.maximum(b_m, tl.max(b_s, 1)), b_m)
        b_mw = tl.where(b_m == float('-inf'), 0.0, b_m)
        _inl_3_exp2_x = b_mp - b_mw
        _inl_3_exp2_result = tl.exp2(_inl_3_exp2_x.to(tl.float32))
        b_r = _inl_3_exp2_result
        _inl_4_exp2_x = b_s - b_mw[:, None]
        _inl_4_exp2_result = tl.exp2(_inl_4_exp2_x.to(tl.float32))
        b_p = _inl_4_exp2_result
        b_acc = b_acc * b_r + tl.sum(b_p, 1)
        b_o = b_o * b_r[:, None] + (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_p.to(b_q.dtype).shape[1])[None, None, :] == 0, b_p.to(b_q.dtype)[:, :, None], 0), (b_p.to(b_q.dtype).shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_p.to(b_q.dtype).shape[1])[None, :, None] == 0, b_v[:, None, :], 0), (16, b_v.shape[1])).to(tl.float32)) if b_p.to(b_q.dtype).shape[1] < 16 else tl.dot(b_p.to(b_q.dtype), b_v))
        b_mp = b_m
    if USE_SINK_BIAS:
        b_m = tl.where(b_m == float('-inf'), 0.0, b_m)
        _inl_5_exp2_x = b_sink_bias - b_m
        _inl_5_exp2_result = tl.exp2(_inl_5_exp2_x.to(tl.float32))
        b_acc += _inl_5_exp2_result
    b_o = b_o / b_acc[:, None]
    _inl_6_log2_x = b_acc
    _inl_6_log2_result = tl.log2(_inl_6_log2_x.to(tl.float32))
    b_m += _inl_6_log2_result
    tl.store(p_o, b_o.to(p_o.dtype.element_ty), mask=m_q[:, None] & (o_v[None, :] < V))
    if i_v == 0:
        tl.store(p_lse, b_m.to(p_lse.dtype.element_ty), mask=m_q)

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
def _attention(q, k, v, gate, scale, window, sink_bias=None):
    import numpy as np

    B, T, HQ, K = q.shape; H = k.shape[2]; G = HQ // H; V = v.shape[3]
    output = np.zeros((B, T, HQ, V), dtype=np.float32)
    lse = np.zeros((B, T, HQ), dtype=np.float32)
    probabilities = np.zeros((B, HQ, T, T), dtype=np.float32)
    log2e = np.float32(1.4426950216)
    for b in range(B):
        for hq in range(HQ):
            h = hq // G
            logits = (q[b, :, hq] @ k[b, :, h].T) * np.float32(scale) * log2e
            logits += gate[b, :, hq, None] - gate[b, None, :, hq]
            for row in range(T):
                first = max(0, row - int(window) + 1)
                valid = logits[row, first : row + 1]
                maximum = max(float(np.max(valid)), float(sink_bias[hq]) if sink_bias is not None else -np.inf)
                weights = np.exp2(valid - maximum)
                denominator = float(np.sum(weights))
                if sink_bias is not None:
                    denominator += float(np.exp2(np.float32(sink_bias[hq]) - maximum))
                probabilities[b, hq, row, first : row + 1] = weights / denominator
                output[b, row, hq] = probabilities[b, hq, row] @ v[b, :, h]
                lse[b, row, hq] = maximum + np.log2(denominator)
    return output, lse, probabilities

SHAPES=((2, 17, 2, 4, 7, 9, 8, 9), (3, 17, 2, 4, 7, 9, 8, 9));DTYPES=('float32', 'float16', 'bfloat16');FIXED_META={"BS":4,"USE_G":True,"USE_SINK_BIAS":True,"USE_WINDOW":True,"IS_VARLEN":False}
SHAPES=((2, 17, 2, 4, 7, 9, 8, 9), (3, 17, 2, 4, 7, 9, 8, 9));DTYPES=('float32', 'float16', 'bfloat16');FIXED_META={"BS":4,"USE_G":True,"USE_SINK_BIAS":True,"USE_WINDOW":True,"IS_VARLEN":False}
SHAPES=((2, 17, 2, 4, 7, 9, 8, 9), (3, 17, 2, 4, 7, 9, 8, 9));DTYPES=('float32', 'float16', 'bfloat16');FIXED_META={"BS":4,"USE_G":True,"USE_SINK_BIAS":True,"USE_WINDOW":True,"IS_VARLEN":False}
def ref(args,meta):
    q=args["q"].reshape(meta["B"],int(args["T"]),meta["HQ"],meta["K"]);k=args["k"].reshape(meta["B"],int(args["T"]),meta["H"],meta["K"]);v=args["v"].reshape(meta["B"],int(args["T"]),meta["H"],meta["V"]);g=args["g_cumsum"].reshape(meta["B"],int(args["T"]),meta["HQ"]);o,lse,_=_attention(q,k,v,g,args["scale"],meta["W"],args["sink_bias"]);return {"o":o.reshape(-1),"lse":lse.reshape(-1)}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    del dtype
    import numpy as np
    (B, T, H, HQ, K, V, BT, W) = (int(x) for x in shape)
    G = HQ // H
    NT = (T + BT - 1) // BT
    from case_utils import fast_rng
    rng = fast_rng(seed)
    args = {'q': _aligned(rng.normal(0, 0.25, (B, T, HQ, K))), 'k': _aligned(rng.normal(0, 0.25, (B, T, H, K))), 'v': _aligned(rng.normal(0, 0.25, (B, T, H, V))), 'o': _aligned(np.full(B * T * HQ * V, -7.0)), 'g_cumsum': _aligned(np.cumsum(rng.normal(-0.03, 0.02, (B, T, HQ)), axis=1)), 'sink_bias': _aligned(rng.normal(-1, 0.2, HQ)), 'lse': _aligned(np.full(B * T * HQ, -7.0)), 'scale': K ** (-0.5), 'cu_seqlens': _aligned(np.arange(B + 1) * T, 'int32'), 'chunk_indices': _aligned(np.zeros(2 * B * NT), 'int32'), 'T': T}
    meta = {**FIXED_META, 'W': W, 'B': B, 'H': H, 'HQ': HQ, 'G': G, 'K': K, 'V': V, 'BT': BT, 'BK': 1 << (int(K) - 1).bit_length(), 'BV': 1 << (int(V) - 1).bit_length()}
    grid = (1, NT, B * HQ)
    outputs = ('o', 'lse')
    return _case(parallel_attn_fwd_kernel, grid, args, meta, ('q', 'k', 'v', 'g_cumsum', 'sink_bias'), outputs, ref(args, meta), shape, 'float32', seed, {'grid_formula': '(ceil_div(V,BV),ceil_div(T,BT),B*HQ)', 'outputs': outputs})
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
