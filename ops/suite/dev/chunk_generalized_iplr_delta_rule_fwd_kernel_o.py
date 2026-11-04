"""chunk_generalized_iplr_delta_rule_fwd_kernel_o: 广义 IPLR delta rule 前向 o:IPLR q 状态投影 + 因果 q-k/value 与 q-b/u 局部贡献。

模式: args.runtime_scalar, cast.to, control.for_range, control.if, creation.arange, creation.where, creation.zeros, linalg.dot, memory.load.masked, memory.load.other, memory.store, shape.reshape。

文件只有两层:
  ① chunk_generalized_iplr_delta_rule_fwd_kernel_o   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/chunk_generalized_iplr_delta_rule_fwd_kernel_o", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "cast.to", "control.for_range", "control.if", "creation.arange", "creation.where", "creation.zeros", "linalg.dot", "memory.load.masked", "memory.load.other", "memory.store", "shape.reshape"]}
COPIED_FROM = {"repo": "fla @ ~/ops", "path": "operators/chunk_generalized_iplr_delta_rule_fwd_kernel_o.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit(do_not_specialize=['T'])
def chunk_generalized_iplr_delta_rule_fwd_kernel_o(q, k, v, u, b, h, o, cu_seqlens, chunk_indices, scale, T, H: tl.constexpr, K: tl.constexpr, V: tl.constexpr, BT: tl.constexpr, BK: tl.constexpr, BV: tl.constexpr, IS_VARLEN: tl.constexpr):
    (i_v, i_t, i_bh) = (tl.program_id(0), tl.program_id(1).to(tl.int64), tl.program_id(2).to(tl.int64))
    (i_b, i_h) = (i_bh // H, i_bh % H)
    if IS_VARLEN:
        i_tg = i_t
        (i_n, i_t) = (tl.load(chunk_indices + i_t * 2).to(tl.int32), tl.load(chunk_indices + i_t * 2 + 1).to(tl.int64))
        (bos, eos) = (tl.load(cu_seqlens + i_n).to(tl.int64), tl.load(cu_seqlens + i_n + 1).to(tl.int64))
        T = eos - bos
        NT = tl.cdiv(T, BT)
    else:
        NT = tl.cdiv(T, BT)
        i_tg = i_b * NT + i_t
        (bos, eos) = (i_b * T, i_b * T + T)
    q += (bos * H + i_h) * K
    k += (bos * H + i_h) * K
    b += (bos * H + i_h) * K
    v += (bos * H + i_h) * V
    u += (bos * H + i_h) * V
    o += (bos * H + i_h) * V
    h += (i_tg * H + i_h) * K * V
    stride_qk = H * K
    stride_vo = H * V
    b_o = tl.zeros([BT, BV], dtype=tl.float32)
    b_Aqk = tl.zeros([BT, BT], dtype=tl.float32)
    b_Aqb = tl.zeros([BT, BT], dtype=tl.float32)
    o_t = i_t * BT + tl.arange(0, BT)
    o_v = i_v * BV + tl.arange(0, BV)
    m_t = o_t < T
    for i_k in range(tl.cdiv(K, BK)):
        o_k = i_k * BK + tl.arange(0, BK)
        m_q = m_t[:, None] & (o_k[None, :] < K)
        m_k = (o_k[:, None] < K) & m_t[None, :]
        m_h = (o_k[:, None] < K) & (o_v[None, :] < V)
        p_q = q + o_t[:, None] * stride_qk + o_k[None, :]
        p_k = k + o_k[:, None] + o_t[None, :] * stride_qk
        p_h = h + o_k[:, None] * V + o_v[None, :]
        p_b = b + o_k[:, None] + o_t[None, :] * stride_qk
        b_q = tl.load(p_q, mask=m_q, other=0.0)
        b_k = tl.load(p_k, mask=m_k, other=0.0)
        b_b = tl.load(p_b, mask=m_k, other=0.0)
        b_h = tl.load(p_h, mask=m_h, other=0.0)
        b_o += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_q.shape[1])[None, None, :] == 0, b_q[:, :, None], 0), (b_q.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_q.shape[1])[None, :, None] == 0, b_h[:, None, :], 0), (16, b_h.shape[1])).to(tl.float32)) if b_q.shape[1] < 16 else tl.dot(b_q, b_h)
        b_Aqk += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_q.shape[1])[None, None, :] == 0, b_q[:, :, None], 0), (b_q.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_q.shape[1])[None, :, None] == 0, b_k[:, None, :], 0), (16, b_k.shape[1])).to(tl.float32)) if b_q.shape[1] < 16 else tl.dot(b_q, b_k)
        b_Aqb += tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_q.shape[1])[None, None, :] == 0, b_q[:, :, None], 0), (b_q.shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_q.shape[1])[None, :, None] == 0, b_b[:, None, :], 0), (16, b_b.shape[1])).to(tl.float32)) if b_q.shape[1] < 16 else tl.dot(b_q, b_b)
    o_i = tl.arange(0, BT)
    m_A = o_i[:, None] >= o_i[None, :]
    b_Aqk = tl.where(m_A, b_Aqk, 0)
    b_Aqb = tl.where(m_A, b_Aqb, 0)
    m_v = m_t[:, None] & (o_v[None, :] < V)
    p_v = v + o_t[:, None] * stride_vo + o_v[None, :]
    p_u = u + o_t[:, None] * stride_vo + o_v[None, :]
    p_o = o + o_t[:, None] * stride_vo + o_v[None, :]
    b_v = tl.load(p_v, mask=m_v, other=0.0)
    b_u = tl.load(p_u, mask=m_v, other=0.0)
    b_o = (b_o + (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Aqk.to(b_v.dtype).shape[1])[None, None, :] == 0, b_Aqk.to(b_v.dtype)[:, :, None], 0), (b_Aqk.to(b_v.dtype).shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Aqk.to(b_v.dtype).shape[1])[None, :, None] == 0, b_v[:, None, :], 0), (16, b_v.shape[1])).to(tl.float32)) if b_Aqk.to(b_v.dtype).shape[1] < 16 else tl.dot(b_Aqk.to(b_v.dtype), b_v)) + (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_Aqb.to(b_u.dtype).shape[1])[None, None, :] == 0, b_Aqb.to(b_u.dtype)[:, :, None], 0), (b_Aqb.to(b_u.dtype).shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_Aqb.to(b_u.dtype).shape[1])[None, :, None] == 0, b_u[:, None, :], 0), (16, b_u.shape[1])).to(tl.float32)) if b_Aqb.to(b_u.dtype).shape[1] < 16 else tl.dot(b_Aqb.to(b_u.dtype), b_u))) * scale
    tl.store(p_o, b_o.to(p_o.dtype.element_ty), mask=m_v)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 fla 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (6, 17, 2, 7, 6)  workload x2:dim0 3->6
#   规模  (3, 34, 2, 7, 6)  workload x2:dim1 17->34
SHAPES = ((17,), (6, 17, 2, 7, 6))
DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 T=int(args["T"]);H=int(meta["H"]);K=int(meta["K"]);V=int(meta["V"]);BT=int(meta["BT"]);NT=(T+BT-1)//BT;q=np.asarray(args["q"],np.float32).reshape(-1,T,H,K);k=np.asarray(args["k"],np.float32).reshape(-1,T,H,K);b=np.asarray(args["b"],np.float32).reshape(-1,T,H,K);v=np.asarray(args["v"],np.float32).reshape(-1,T,H,V);u=np.asarray(args["u"],np.float32).reshape(-1,T,H,V);state=np.asarray(args["h"],np.float32).reshape(-1,NT,H,K,V);out=np.zeros_like(v)
 for n in range(q.shape[0]):
  for h in range(H):
   for c,start in enumerate(range(0,T,BT)):
    count=min(BT,T-start);qq=q[n,start:start+count,h];Aqk=np.tril(qq@k[n,start:start+count,h].T);Aqb=np.tril(qq@b[n,start:start+count,h].T);out[n,start:start+count,h]=(qq@state[n,c,h]+Aqk@v[n,start:start+count,h]+Aqb@u[n,start:start+count,h])*np.float32(args["scale"])
 return {"o":out.reshape(-1)}

def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=20260901):
    from case_utils import fast_rng
    if len(shape) > 1 and tuple(shape) not in SHAPES:
        raise ValueError('unsupported explicit shape configuration')
    del dtype
    import numpy as np
    N = int(shape[0])
    rng = fast_rng(seed)
    B = int(shape[0]) if len(shape) > 1 else 2
    H = int(shape[2]) if len(shape) > 1 else 2
    T = int(shape[1]) if len(shape) > 1 else max(9, min(33, N | 1))
    K = int(shape[3]) if len(shape) > 1 else 7
    V = int(shape[4]) if len(shape) > 1 else 6
    BT = 8
    NT = (T + BT - 1) // BT
    args = {'q': np.asarray(rng.normal(0, 0.2, (B, T, H, K))), 'k': np.asarray(rng.normal(0, 0.2, (B, T, H, K))), 'v': np.asarray(rng.normal(0, 0.2, (B, T, H, V))), 'u': np.asarray(rng.normal(0, 0.2, (B, T, H, V))), 'b': np.asarray(rng.normal(0, 0.2, (B, T, H, K))), 'h': np.asarray(rng.normal(0, 0.15, (B, NT, H, K, V))), 'o': np.asarray(np.full(B * T * H * V, -7.0)), 'cu_seqlens': np.asarray(np.arange(B + 1) * T, 'int64'), 'chunk_indices': np.asarray(np.zeros(2, dtype=np.int64), 'int64'), 'scale': 0.7, 'T': T}
    meta = {'H': H, 'K': K, 'V': V, 'BT': BT, 'BK': 4, 'BV': 4, 'IS_VARLEN': False}
    grid = ((V + 3) // 4, NT, B * H)
    outputs = ('o',)
    return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0001, "atol": 0.0001, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, chunk_generalized_iplr_delta_rule_fwd_kernel_o, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)


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
