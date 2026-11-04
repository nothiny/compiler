"""chunk_gated_delta_product_fwd_kernel_h_blockdim64: 从 ~/ops 仓库复制(core @ ops-pool),保留其已验证的 case 层。

模式: args.runtime_scalar、cast.to、control.for_range、control.if、control.loop_carried、creation.arange、creation.where、creation.zeros、dtype.float32、dtype.int64。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。循环上界来自运行时标量(不是 constexpr)。constexpr 参数: num_householder, H, K, V, BT, BTT, BV, USE_G, USE_INITIAL_STATE, STORE_FINAL_STATE, SAVE_NEW_VALUE, IS_VARLEN。

文件只有两层:
  ① chunk_gated_delta_product_fwd_kernel_h_blockdim64   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/chunk_gated_delta_product_fwd_kernel_h_blockdim64', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'cast.to', 'control.for_range', 'control.if', 'control.loop_carried', 'creation.arange', 'creation.where', 'creation.zeros', 'dtype.float32', 'dtype.int64', 'linalg.dot', 'math.cdiv', 'math.exp2', 'memory.load', 'memory.load.masked', 'memory.load.other', 'memory.store', 'memory.store.masked', 'reduce.min', 'shape.reshape', 'tile.2d', 'tile.3d']}
COPIED_FROM = {'repo': 'core @ ops-pool', 'note': 'validated case layer intact'}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit(do_not_specialize=['T'])
def chunk_gated_delta_product_fwd_kernel_h_blockdim64(k, v, w, v_new, g, h, h0, ht, cu_seqlens, chunk_offsets, T, num_householder: tl.constexpr, H: tl.constexpr, K: tl.constexpr, V: tl.constexpr, BT: tl.constexpr, BTT: tl.constexpr, BV: tl.constexpr, USE_G: tl.constexpr, USE_INITIAL_STATE: tl.constexpr, STORE_FINAL_STATE: tl.constexpr, SAVE_NEW_VALUE: tl.constexpr, IS_VARLEN: tl.constexpr):
    (i_v, i_nh) = (tl.program_id(0), tl.program_id(1).to(tl.int64))
    (i_n, i_h) = (i_nh // H, i_nh % H)
    if IS_VARLEN:
        (bos, eos) = (tl.load(cu_seqlens + i_n).to(tl.int64), tl.load(cu_seqlens + i_n + 1).to(tl.int64))
        T = eos - bos
        NT = tl.cdiv(T, BT)
        boh = tl.load(chunk_offsets + i_n).to(tl.int64)
    else:
        (bos, eos) = (i_n * T, i_n * T + T)
        NT = tl.cdiv(T, BT)
        boh = i_n * tl.cdiv(T // num_householder, BT)
    b_h1 = tl.zeros([64, BV], dtype=tl.float32)
    if K > 64:
        b_h2 = tl.zeros([64, BV], dtype=tl.float32)
    if K > 128:
        b_h3 = tl.zeros([64, BV], dtype=tl.float32)
    if K > 192:
        b_h4 = tl.zeros([64, BV], dtype=tl.float32)
    h += (boh * H + i_h) * K * V
    v += (bos * H + i_h) * V
    k += (bos * H + i_h) * K
    w += (bos * H + i_h) * K
    if SAVE_NEW_VALUE:
        v_new += (bos * H + i_h) * V
    stride_v = H * V
    stride_h = H * K * V
    stride_k = H * K
    if USE_INITIAL_STATE:
        h0 = h0 + i_nh * K * V
    if STORE_FINAL_STATE:
        ht = ht + i_nh * K * V
    o_k1 = tl.arange(0, 64)
    o_k2 = 64 + tl.arange(0, 64)
    o_k3 = 128 + tl.arange(0, 64)
    o_k4 = 192 + tl.arange(0, 64)
    o_v = i_v * BV + tl.arange(0, BV)
    m_v = o_v < V
    m_h1 = (o_k1[:, None] < K) & m_v[None, :]
    m_h2 = (o_k2[:, None] < K) & m_v[None, :]
    m_h3 = (o_k3[:, None] < K) & m_v[None, :]
    m_h4 = (o_k4[:, None] < K) & m_v[None, :]
    if USE_INITIAL_STATE:
        p_h0_1 = h0 + o_k1[:, None] * V + o_v[None, :]
        b_h1 += tl.load(p_h0_1, mask=m_h1, other=0.0).to(tl.float32)
        if K > 64:
            p_h0_2 = h0 + o_k2[:, None] * V + o_v[None, :]
            b_h2 += tl.load(p_h0_2, mask=m_h2, other=0.0).to(tl.float32)
        if K > 128:
            p_h0_3 = h0 + o_k3[:, None] * V + o_v[None, :]
            b_h3 += tl.load(p_h0_3, mask=m_h3, other=0.0).to(tl.float32)
        if K > 192:
            p_h0_4 = h0 + o_k4[:, None] * V + o_v[None, :]
            b_h4 += tl.load(p_h0_4, mask=m_h4, other=0.0).to(tl.float32)
    for i_t in range(NT):
        i_t_int64 = i_t.to(tl.int64)
        if i_t % num_householder == 0:
            i_t_true = i_t_int64 // num_householder
            p_h1 = h + i_t_true * stride_h + o_k1[:, None] * V + o_v[None, :]
            tl.store(p_h1, b_h1.to(p_h1.dtype.element_ty), mask=m_h1)
            if K > 64:
                p_h2 = h + i_t_true * stride_h + o_k2[:, None] * V + o_v[None, :]
                tl.store(p_h2, b_h2.to(p_h2.dtype.element_ty), mask=m_h2)
            if K > 128:
                p_h3 = h + i_t_true * stride_h + o_k3[:, None] * V + o_v[None, :]
                tl.store(p_h3, b_h3.to(p_h3.dtype.element_ty), mask=m_h3)
            if K > 192:
                p_h4 = h + i_t_true * stride_h + o_k4[:, None] * V + o_v[None, :]
                tl.store(p_h4, b_h4.to(p_h4.dtype.element_ty), mask=m_h4)
        o_t = i_t_int64 * BT + tl.arange(0, BTT)
        m_t = (o_t < T) & (o_t < (i_t + 1) * BT)
        m_vv = m_t[:, None] & m_v[None, :]
        p_v = v + o_t[:, None] * stride_v + o_v[None, :]
        p_v_new = v_new + o_t[:, None] * stride_v + o_v[None, :] if SAVE_NEW_VALUE else None
        b_v_new = tl.zeros([BTT, BV], dtype=tl.float32)
        p_w = w + o_t[:, None] * stride_k + o_k1[None, :]
        b_w = tl.load(p_w, mask=m_t[:, None] & (o_k1[None, :] < K), other=0.0)
        b_v_new += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_w.shape[1])[None, None, :] == 0, b_w[:, :, None], 0), (b_w.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_w.shape[1])[None, :, None] == 0, b_h1.to(b_w.dtype)[:, None, :], 0), (16, b_h1.to(b_w.dtype).shape[1])).to(tl.float32)) if b_w.shape[1] < 16 else tl.dot(b_w, b_h1.to(b_w.dtype))
        if K > 64:
            p_w = w + o_t[:, None] * stride_k + o_k2[None, :]
            b_w = tl.load(p_w, mask=m_t[:, None] & (o_k2[None, :] < K), other=0.0)
            b_v_new += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_w.shape[1])[None, None, :] == 0, b_w[:, :, None], 0), (b_w.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_w.shape[1])[None, :, None] == 0, b_h2.to(b_w.dtype)[:, None, :], 0), (16, b_h2.to(b_w.dtype).shape[1])).to(tl.float32)) if b_w.shape[1] < 16 else tl.dot(b_w, b_h2.to(b_w.dtype))
        if K > 128:
            p_w = w + o_t[:, None] * stride_k + o_k3[None, :]
            b_w = tl.load(p_w, mask=m_t[:, None] & (o_k3[None, :] < K), other=0.0)
            b_v_new += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_w.shape[1])[None, None, :] == 0, b_w[:, :, None], 0), (b_w.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_w.shape[1])[None, :, None] == 0, b_h3.to(b_w.dtype)[:, None, :], 0), (16, b_h3.to(b_w.dtype).shape[1])).to(tl.float32)) if b_w.shape[1] < 16 else tl.dot(b_w, b_h3.to(b_w.dtype))
        if K > 192:
            p_w = w + o_t[:, None] * stride_k + o_k4[None, :]
            b_w = tl.load(p_w, mask=m_t[:, None] & (o_k4[None, :] < K), other=0.0)
            b_v_new += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_w.shape[1])[None, None, :] == 0, b_w[:, :, None], 0), (b_w.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_w.shape[1])[None, :, None] == 0, b_h4.to(b_w.dtype)[:, None, :], 0), (16, b_h4.to(b_w.dtype).shape[1])).to(tl.float32)) if b_w.shape[1] < 16 else tl.dot(b_w, b_h4.to(b_w.dtype))
        b_v_new = -b_v_new + tl.load(p_v, mask=m_vv, other=0.0)
        if SAVE_NEW_VALUE:
            p_v_new = v_new + o_t[:, None] * stride_v + o_v[None, :]
            tl.store(p_v_new, b_v_new.to(p_v_new.dtype.element_ty), mask=m_vv)
        if USE_G:
            m_t = (i_t * BT + tl.arange(0, BTT) < T) & (tl.arange(0, BTT) < BT)
            last_idx = min((i_t + 1) * BT, T) - 1
            b_g_last = tl.load(g + bos * H + last_idx * H + i_h)
            p_g = g + bos * H + i_h + o_t * H
            b_g = tl.load(p_g, mask=m_t, other=0.0)
            _inl_1_exp2_x = b_g_last - b_g
            _inl_1_exp2_result = tl.exp2(_inl_1_exp2_x.to(tl.float32))
            b_v_new = b_v_new * tl.where(m_t, _inl_1_exp2_result, 0)[:, None]
            _inl_2_exp2_x = b_g_last
            _inl_2_exp2_result = tl.exp2(_inl_2_exp2_x.to(tl.float32))
            b_g_last = _inl_2_exp2_result
            b_h1 = b_h1 * b_g_last
            if K > 64:
                b_h2 = b_h2 * b_g_last
            if K > 128:
                b_h3 = b_h3 * b_g_last
            if K > 192:
                b_h4 = b_h4 * b_g_last
        b_v_new = b_v_new.to(k.dtype.element_ty)
        p_k = k + o_k1[:, None] + o_t[None, :] * stride_k
        b_k = tl.load(p_k, mask=(o_k1[:, None] < K) & m_t[None, :], other=0.0)
        b_h1 += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_k.shape[1])[None, None, :] == 0, b_k[:, :, None], 0), (b_k.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_k.shape[1])[None, :, None] == 0, b_v_new[:, None, :], 0), (16, b_v_new.shape[1])).to(tl.float32)) if b_k.shape[1] < 16 else tl.dot(b_k, b_v_new)
        if K > 64:
            p_k = k + o_k2[:, None] + o_t[None, :] * stride_k
            b_k = tl.load(p_k, mask=(o_k2[:, None] < K) & m_t[None, :], other=0.0)
            b_h2 += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_k.shape[1])[None, None, :] == 0, b_k[:, :, None], 0), (b_k.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_k.shape[1])[None, :, None] == 0, b_v_new[:, None, :], 0), (16, b_v_new.shape[1])).to(tl.float32)) if b_k.shape[1] < 16 else tl.dot(b_k, b_v_new)
        if K > 128:
            p_k = k + o_k3[:, None] + o_t[None, :] * stride_k
            b_k = tl.load(p_k, mask=(o_k3[:, None] < K) & m_t[None, :], other=0.0)
            b_h3 += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_k.shape[1])[None, None, :] == 0, b_k[:, :, None], 0), (b_k.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_k.shape[1])[None, :, None] == 0, b_v_new[:, None, :], 0), (16, b_v_new.shape[1])).to(tl.float32)) if b_k.shape[1] < 16 else tl.dot(b_k, b_v_new)
        if K > 192:
            p_k = k + o_k4[:, None] + o_t[None, :] * stride_k
            b_k = tl.load(p_k, mask=(o_k4[:, None] < K) & m_t[None, :], other=0.0)
            b_h4 += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_k.shape[1])[None, None, :] == 0, b_k[:, :, None], 0), (b_k.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_k.shape[1])[None, :, None] == 0, b_v_new[:, None, :], 0), (16, b_v_new.shape[1])).to(tl.float32)) if b_k.shape[1] < 16 else tl.dot(b_k, b_v_new)
    if STORE_FINAL_STATE:
        p_ht = ht + o_k1[:, None] * V + o_v[None, :]
        tl.store(p_ht, b_h1.to(p_ht.dtype.element_ty), mask=m_h1)
        if K > 64:
            p_ht = ht + o_k2[:, None] * V + o_v[None, :]
            tl.store(p_ht, b_h2.to(p_ht.dtype.element_ty), mask=m_h2)
        if K > 128:
            p_ht = ht + o_k3[:, None] * V + o_v[None, :]
            tl.store(p_ht, b_h3.to(p_ht.dtype.element_ty), mask=m_h3)
        if K > 192:
            p_ht = ht + o_k4[:, None] * V + o_v[None, :]
            tl.store(p_ht, b_h4.to(p_ht.dtype.element_ty), mask=m_h4)

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

SHAPES=((2, 2, 16, 7, 9, 4, 2), (4, 2, 16, 7, 9, 4, 2), (1, 3, 32, 11, 13, 8, 2));DTYPES=('float32', 'float16', 'bfloat16');FIXED_META={"USE_G":False,"USE_INITIAL_STATE":True,"STORE_FINAL_STATE":True,"SAVE_NEW_VALUE":True,"IS_VARLEN":False}
SHAPES=((2, 2, 16, 7, 9, 4, 2), (4, 2, 16, 7, 9, 4, 2), (1, 3, 32, 11, 13, 8, 2));DTYPES=('float32', 'float16', 'bfloat16');FIXED_META={"USE_G":False,"USE_INITIAL_STATE":True,"STORE_FINAL_STATE":True,"SAVE_NEW_VALUE":True,"IS_VARLEN":False}
SHAPES=((2, 2, 16, 7, 9, 4, 2), (4, 2, 16, 7, 9, 4, 2), (1, 3, 32, 11, 13, 8, 2));DTYPES=('float32', 'float16', 'bfloat16');FIXED_META={"USE_G":False,"USE_INITIAL_STATE":True,"STORE_FINAL_STATE":True,"SAVE_NEW_VALUE":True,"IS_VARLEN":False}
def ref(args,meta):
 import numpy as np
 B,T,H,K,V,BT,NH=args["cu_seqlens"].size-1,int(args["T"]),meta["H"],meta["K"],meta["V"],meta["BT"],meta["num_householder"];k=args["k"].reshape(B,T,H,K);v=args["v"].reshape(B,T,H,V);w=args["w"].reshape(B,T,H,K);state=args["h0"].reshape(B,H,K,V).copy();saved=np.zeros((B,(T//BT)//NH,H,K,V),np.float32);vn=np.zeros_like(v)
 for b in range(B):
  for h in range(H):
   for c,s in enumerate(range(0,T,BT)):
    e=s+BT
    if c%NH==0:saved[b,c//NH,h]=state[b,h]
    vn[b,s:e,h]=v[b,s:e,h]-w[b,s:e,h]@state[b,h];state[b,h]+=k[b,s:e,h].T@vn[b,s:e,h]
 return {"v_new":vn.reshape(-1),"h":saved.reshape(-1),"ht":state.reshape(-1)}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    del dtype
    import numpy as np
    (B, H, T, K, V, BT, NH) = (int(x) for x in shape)
    NT = T // BT
    NS = NT // NH
    from case_utils import fast_rng
    rng = fast_rng(seed)
    args = {'k': _aligned(rng.normal(0, 0.14, (B, T, H, K))), 'v': _aligned(rng.normal(0, 0.14, (B, T, H, V))), 'w': _aligned(rng.normal(0, 0.1, (B, T, H, K))), 'v_new': _aligned(np.full(B * T * H * V, -7.0)), 'g': _aligned(np.zeros((B, T, H))), 'h': _aligned(np.full(B * NS * H * K * V, -7.0)), 'h0': _aligned(rng.normal(0, 0.06, (B, H, K, V))), 'ht': _aligned(np.full(B * H * K * V, -7.0)), 'cu_seqlens': _aligned(np.arange(B + 1) * T, 'int32'), 'chunk_offsets': _aligned(np.arange(B + 1) * NS, 'int32'), 'T': T}
    meta = {**FIXED_META, 'num_householder': NH, 'H': H, 'K': K, 'V': V, 'BT': BT, 'BV': 1 << (int(V) - 1).bit_length()}
    grid = (1, B * H)
    outputs = ('v_new', 'h', 'ht')
    return _case(chunk_gated_delta_product_fwd_kernel_h_blockdim64, grid, args, meta, ('k', 'v', 'w', 'h0'), outputs, ref(args, meta), shape, 'float32', seed, {'grid_formula': '(ceil_div(V,BV),B*H)', 'stages': ('save-state', 'new-value', 'state-update')})
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
    case["meta"]["BTT"] = max(16, 1 << (int(case["meta"]["BT"]) - 1).bit_length())
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
