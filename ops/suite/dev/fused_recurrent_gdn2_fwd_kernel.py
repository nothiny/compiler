"""fused_recurrent_gdn2_fwd_kernel: 从 ~/ops 仓库复制(core @ ops),保留其已验证的 case 层。

模式: args.runtime_scalar、cast.to、control.for_range、control.if、control.loop_carried、control.range_num_stages、creation.arange、creation.where、creation.zeros、dtype.float32。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。循环上界来自运行时标量(不是 constexpr)。constexpr 参数: scale, H, HV, K, V, BK, BV, stride_init_state_token, stride_final_state_token, stride_indices_seq, stride_indices_tok, USE_INITIAL_STATE, INPLACE_FINAL_STATE, USE_QK_L2NORM_IN_KERNEL, IS_VARLEN, IS_CONTINUOUS_BATCHING, IS_SPEC_DECODING, STORE_FINAL_STATE, HAS_A, HAS_BIAS, USE_GATE_IN_KERNEL, USE_LOWER_BOUND, STATE_V_FIRST, PIPELINE_STAGES。

文件只有两层:
  ① fused_recurrent_gdn2_fwd_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/fused_recurrent_gdn2_fwd_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'cast.to', 'control.for_range', 'control.if', 'control.loop_carried', 'control.range_num_stages', 'creation.arange', 'creation.where', 'creation.zeros', 'dtype.float32', 'dtype.int64', 'math.cdiv', 'math.exp', 'math.log', 'math.sigmoid', 'math.sqrt', 'memory.load', 'memory.load.eviction_policy', 'memory.load.masked', 'memory.load.other', 'memory.store', 'memory.store.masked', 'reduce.sum', 'reduce.sum.axis0', 'reduce.sum.axis1', 'tile.2d']}
COPIED_FROM = {'repo': 'core @ ops', 'note': 'validated case layer intact'}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit(do_not_specialize=['N', 'T'])
def fused_recurrent_gdn2_fwd_kernel(q, k, v, g, b, w, A_log, dt_bias, o, h0, ht, cu_seqlens, ssm_state_indices, num_accepted_tokens, lower_bound, scale: tl.constexpr, N: tl.int64, T: tl.int64, H: tl.constexpr, HV: tl.constexpr, K: tl.constexpr, V: tl.constexpr, BK: tl.constexpr, BV: tl.constexpr, stride_init_state_token: tl.constexpr, stride_final_state_token: tl.constexpr, stride_indices_seq: tl.constexpr, stride_indices_tok: tl.constexpr, USE_INITIAL_STATE: tl.constexpr, INPLACE_FINAL_STATE: tl.constexpr, USE_QK_L2NORM_IN_KERNEL: tl.constexpr, IS_VARLEN: tl.constexpr, IS_CONTINUOUS_BATCHING: tl.constexpr, IS_SPEC_DECODING: tl.constexpr, STORE_FINAL_STATE: tl.constexpr, HAS_A: tl.constexpr, HAS_BIAS: tl.constexpr, USE_GATE_IN_KERNEL: tl.constexpr, USE_LOWER_BOUND: tl.constexpr, STATE_V_FIRST: tl.constexpr, PIPELINE_STAGES: tl.constexpr):
    pid = tl.program_id(0).to(tl.int64)
    NV = tl.cdiv(V, BV)
    NK = tl.cdiv(K, BK)
    i_k = pid % NK
    pid_rest = pid // NK
    i_v = pid_rest % NV
    i_nh = pid_rest // NV
    (i_n, i_hv) = (i_nh // HV, i_nh % HV)
    i_h = i_hv // (HV // H)
    if IS_VARLEN:
        (bos, eos) = (tl.load(cu_seqlens + i_n).to(tl.int64), tl.load(cu_seqlens + i_n + 1).to(tl.int64))
        T = eos - bos
    else:
        (bos, eos) = (i_n * T, i_n * T + T)
    if T == 0:
        return
    o_k = i_k * BK + tl.arange(0, BK)
    o_v = i_v * BV + tl.arange(0, BV)
    p_q = q + (bos * H + i_h) * K + o_k
    p_k = k + (bos * H + i_h) * K + o_k
    p_v = v + (bos * HV + i_hv) * V + o_v
    p_b = b + (bos * HV + i_hv) * K + o_k
    p_w = w + (bos * HV + i_hv) * V + o_v
    p_g = g + (bos * HV + i_hv) * K + o_k
    p_o = o + (bos * HV + i_hv) * V + o_v
    mask_k = o_k < K
    mask_v = o_v < V
    if STATE_V_FIRST:
        mask_h = mask_v[:, None] & mask_k[None, :]
    else:
        mask_h = mask_k[:, None] & mask_v[None, :]
    if STATE_V_FIRST:
        b_h = tl.zeros([BV, BK], dtype=tl.float32)
    else:
        b_h = tl.zeros([BK, BV], dtype=tl.float32)
    if USE_INITIAL_STATE:
        if IS_CONTINUOUS_BATCHING:
            if IS_SPEC_DECODING:
                i_t = tl.load(num_accepted_tokens + i_n).to(tl.int64) - 1
            else:
                i_t = 0
            p_h0 = h0 + tl.load(ssm_state_indices + i_n * stride_indices_seq + i_t).to(tl.int64) * stride_init_state_token
            if STATE_V_FIRST:
                p_h0 = p_h0 + i_hv * K * V + o_v[:, None] * K + o_k[None, :]
            else:
                p_h0 = p_h0 + i_hv * K * V + o_k[:, None] * V + o_v[None, :]
        elif STATE_V_FIRST:
            p_h0 = h0 + (i_n * HV + i_hv) * K * V + o_v[:, None] * K + o_k[None, :]
        else:
            p_h0 = h0 + (i_n * HV + i_hv) * K * V + o_k[:, None] * V + o_v[None, :]
        b_h += tl.load(p_h0, mask=mask_h, other=0).to(tl.float32)
    for i_t in tl.range(0, T, num_stages=PIPELINE_STAGES):
        b_q = tl.load(p_q, mask=mask_k, other=0, eviction_policy='evict_last').to(tl.float32)
        b_k = tl.load(p_k, mask=mask_k, other=0, eviction_policy='evict_last').to(tl.float32)
        b_v = tl.load(p_v, mask=mask_v, other=0, eviction_policy='evict_first').to(tl.float32)
        if USE_QK_L2NORM_IN_KERNEL:
            b_q = b_q / tl.sqrt(tl.sum(b_q * b_q) + 1e-06)
            b_k = b_k / tl.sqrt(tl.sum(b_k * b_k) + 1e-06)
        b_q = b_q * scale
        b_g = tl.load(p_g, mask=mask_k, other=0, eviction_policy='evict_last').to(tl.float32)
        if USE_GATE_IN_KERNEL:
            b_A = tl.load(A_log + i_hv).to(tl.float32) if HAS_A else 1.0
            if HAS_BIAS:
                b_bias = tl.load(dt_bias + i_hv * K + o_k, mask=mask_k, other=0).to(tl.float32)
                b_g = b_g + b_bias
            if USE_LOWER_BOUND:
                _inl_1_exp_x = b_A
                _inl_1_exp_result = tl.exp(_inl_1_exp_x.to(tl.float32))
                b_gk = lower_bound * tl.sigmoid((_inl_1_exp_result if HAS_A else b_A) * b_g)
            else:
                _inl_2_exp_x = b_A
                _inl_2_exp_result = tl.exp(_inl_2_exp_x.to(tl.float32))
                _inl_3_softplus_triton_x = b_g
                _inl_3_softplus_triton_result = tl.where(_inl_3_softplus_triton_x < 20.0, tl.log(1 + tl.exp(_inl_3_softplus_triton_x)), _inl_3_softplus_triton_x)
                b_gk = -_inl_2_exp_result * _inl_3_softplus_triton_result
        else:
            b_gk = b_g
        if STATE_V_FIRST:
            _inl_4_exp_x = b_gk[None, :]
            _inl_4_exp_result = tl.exp(_inl_4_exp_x.to(tl.float32))
            b_h *= _inl_4_exp_result
        else:
            _inl_5_exp_x = b_gk[:, None]
            _inl_5_exp_result = tl.exp(_inl_5_exp_x.to(tl.float32))
            b_h *= _inl_5_exp_result
        b_b = tl.load(p_b, mask=mask_k, other=0, eviction_policy='evict_last').to(tl.float32)
        b_bk = b_b * b_k
        if STATE_V_FIRST:
            erase_d = tl.sum(b_h * b_bk[None, :], 1)
        else:
            erase_d = tl.sum(b_h * b_bk[:, None], 0)
        b_w = tl.load(p_w, mask=mask_v, other=0, eviction_policy='evict_first').to(tl.float32)
        b_v_new = b_w * b_v - erase_d
        if STATE_V_FIRST:
            b_h += b_v_new[:, None] * b_k[None, :]
            b_o = tl.sum(b_h * b_q[None, :], 1)
        else:
            b_h += b_k[:, None] * b_v_new[None, :]
            b_o = tl.sum(b_h * b_q[:, None], 0)
        tl.store(p_o, b_o.to(p_o.dtype.element_ty), mask=mask_v, eviction_policy='evict_first')
        if IS_CONTINUOUS_BATCHING:
            if INPLACE_FINAL_STATE:
                p_ht = ht + tl.load(ssm_state_indices + i_n * stride_indices_seq + i_t).to(tl.int64) * stride_final_state_token
            else:
                p_ht = ht + (bos + i_t) * stride_final_state_token
            if STATE_V_FIRST:
                p_ht = p_ht + i_hv * K * V + o_v[:, None] * K + o_k[None, :]
            else:
                p_ht = p_ht + i_hv * K * V + o_k[:, None] * V + o_v[None, :]
            tl.store(p_ht, b_h.to(p_ht.dtype.element_ty), mask=mask_h)
        p_q += H * K
        p_k += H * K
        p_o += HV * V
        p_v += HV * V
        p_g += HV * K
        p_b += HV * K
        p_w += HV * V
    if not IS_CONTINUOUS_BATCHING:
        if STORE_FINAL_STATE:
            if STATE_V_FIRST:
                p_ht = ht + (i_n * HV + i_hv) * K * V + o_v[:, None] * K + o_k[None, :]
            else:
                p_ht = ht + (i_n * HV + i_hv) * K * V + o_k[:, None] * V + o_v[None, :]
            tl.store(p_ht, b_h.to(p_ht.dtype.element_ty), mask=mask_h)

# ------------------------------------------------------------------ ② case 层
# (shape,) 的角色:第一个是典型用法,其余是泛化/尾块/退化用例。
#   (2, 9, 2, 4, 5, 7)
#   (1, 17, 3, 6, 8, 9)
#   (3, 9, 2, 4, 5, 7)
# DTYPES: float32 —— 原始用途的 dtype 在前;非法域(例如本机 Triton 只吃 fp32 的exp/sqrt/erf/atomic)的算子只声明合法的那一种。

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

SHAPES = ((2, 9, 2, 4, 5, 7), (2, 18, 2, 4, 5, 7), (1, 17, 3, 6, 8, 9))
DTYPES = ('float32', 'float16', 'bfloat16')
FIXED_META = {"USE_INITIAL_STATE":True,"INPLACE_FINAL_STATE":False,"USE_QK_L2NORM_IN_KERNEL":True,"IS_VARLEN":False,"IS_CONTINUOUS_BATCHING":False,"IS_SPEC_DECODING":False,"STORE_FINAL_STATE":True,"HAS_A":False,"HAS_BIAS":False,"USE_GATE_IN_KERNEL":False,"USE_LOWER_BOUND":False,"STATE_V_FIRST":False,"PIPELINE_STAGES":1}
def ref(args,meta):
    import numpy as np

    N,T,H,HV,K,V=int(args["N"]),int(args["T"]),meta["H"],meta["HV"],meta["K"],meta["V"]
    q=args["q"].reshape(N,T,H,K); k=args["k"].reshape(N,T,H,K); v=args["v"].reshape(N,T,HV,V); g=args["g"].reshape(N,T,HV,K); bb=args["b"].reshape(N,T,HV,K); w=args["w"].reshape(N,T,HV,V)
    state=args["h0"].reshape(N,HV,K,V).copy(); out=np.zeros((N,T,HV,V),np.float32); ratio=HV//H
    for n in range(N):
        for hv in range(HV):
            h=hv//ratio
            for t in range(T):
                qq=q[n,t,h]/np.sqrt(np.sum(q[n,t,h]**2)+1e-6); kk=k[n,t,h]/np.sqrt(np.sum(k[n,t,h]**2)+1e-6)
                state[n,hv] *= np.exp(g[n,t,hv])[:,None]
                erase=(bb[n,t,hv]*kk)@state[n,hv]; v_new=w[n,t,hv]*v[n,t,hv]-erase
                state[n,hv] += np.outer(kk,v_new); out[n,t,hv]=(qq*np.float32(meta["scale"]))@state[n,hv]
    return {"o":out.reshape(-1),"ht":state.reshape(-1)}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    del dtype
    import numpy as np
    (N, T, H, HV, K, V) = (int(x) for x in shape)
    from case_utils import fast_rng
    rng = fast_rng(seed)
    args = {'q': _aligned(rng.normal(0, 0.18, (N, T, H, K))), 'k': _aligned(rng.normal(0, 0.18, (N, T, H, K))), 'v': _aligned(rng.normal(0, 0.18, (N, T, HV, V))), 'g': _aligned(rng.uniform(-0.3, -0.02, (N, T, HV, K))), 'b': _aligned(rng.uniform(0.05, 0.4, (N, T, HV, K))), 'w': _aligned(rng.uniform(0.2, 0.9, (N, T, HV, V))), 'A_log': _aligned(np.zeros(HV)), 'dt_bias': _aligned(np.zeros((HV, K))), 'o': _aligned(np.full(N * T * HV * V, -7.0)), 'h0': _aligned(rng.normal(0, 0.08, (N, HV, K, V))), 'ht': _aligned(np.full(N * HV * K * V, -7.0)), 'cu_seqlens': _aligned(np.arange(N + 1) * T, 'int32'), 'ssm_state_indices': _aligned(np.arange(N), 'int64'), 'num_accepted_tokens': _aligned(np.ones(N), 'int32'), 'lower_bound': 0, 'N': N, 'T': T}
    meta = {**FIXED_META, 'scale': K ** (-0.5), 'H': H, 'HV': HV, 'K': K, 'V': V, 'BK': 1 << (int(K) - 1).bit_length(), 'BV': 1 << (int(V) - 1).bit_length(), 'stride_init_state_token': HV * K * V, 'stride_final_state_token': HV * K * V, 'stride_indices_seq': 1, 'stride_indices_tok': 1}
    grid = (N * HV,)
    outputs = ('o', 'ht')
    return _case(fused_recurrent_gdn2_fwd_kernel, grid, args, meta, ('q', 'k', 'v', 'g', 'b', 'w', 'h0'), outputs, ref(args, meta), shape, 'float32', seed, {'grid_formula': '(N*HV*ceil_div(V,BV)*ceil_div(K,BK),)', 'stages': ('normalize', 'decay', 'erase', 'rank-one-update', 'output')})
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
