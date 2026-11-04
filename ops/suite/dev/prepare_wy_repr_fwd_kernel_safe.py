"""prepare_wy_repr_fwd_kernel_safe: 从 ~/ops 仓库复制(core @ ops),保留其已验证的 case 层。

模式: args.runtime_scalar、cast.to、control.if、creation.arange、creation.where、creation.zeros、dtype.float16、dtype.int32、dtype.int64、linalg.dot。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。constexpr 参数: H, BT, BC, IS_VARLEN。

文件只有两层:
  ① prepare_wy_repr_fwd_kernel_safe   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/prepare_wy_repr_fwd_kernel_safe', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'cast.to', 'control.if', 'creation.arange', 'creation.where', 'creation.zeros', 'dtype.float16', 'dtype.int32', 'dtype.int64', 'linalg.dot', 'memory.load', 'memory.load.masked', 'memory.load.other', 'memory.store', 'memory.store.masked', 'tile.2d']}
COPIED_FROM = {'repo': 'core @ ops', 'note': 'validated case layer intact', 'lines': 207}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit(do_not_specialize=['T'])
def prepare_wy_repr_fwd_kernel_safe(A_ab, A_ab_inv, cu_seqlens, chunk_indices, T, H: tl.constexpr, BT: tl.constexpr, BC: tl.constexpr, IS_VARLEN: tl.constexpr):
    (i_t, i_bh) = (tl.program_id(0).to(tl.int64), tl.program_id(1).to(tl.int64))
    (i_b, i_h) = (i_bh // H, i_bh % H)
    if IS_VARLEN:
        (i_n, i_t) = (tl.load(chunk_indices + i_t * 2).to(tl.int32), tl.load(chunk_indices + i_t * 2 + 1).to(tl.int64))
        (bos, eos) = (tl.load(cu_seqlens + i_n).to(tl.int64), tl.load(cu_seqlens + i_n + 1).to(tl.int64))
        T = eos - bos
    else:
        bos = i_b * T
    NB: tl.constexpr = 16
    NS: tl.constexpr = BT // NB
    o_i = tl.arange(0, NB)
    o_c1 = NB + o_i
    m_lo = o_i[:, None] > o_i[None, :]
    b_zero = tl.zeros([NB, NB], dtype=tl.float32)
    r_0 = i_t * BT + o_i
    m_r0 = r_0 < T
    o_A0 = A_ab + (bos * H + i_h) * BT + r_0[:, None] * (H * BT)
    o_I0 = A_ab_inv + (bos * H + i_h) * BT + r_0[:, None] * (H * BT)
    b_L00 = tl.where(m_lo, tl.load(o_A0 + o_i[None, :], mask=m_r0[:, None], other=0.0), 0.0).to(tl.float16)
    _inl_1_inv_diag16_b_L = b_L00
    _inl_1_inv_diag16_o_i = tl.arange(0, 16)
    _inl_1_inv_diag16_b_I = (_inl_1_inv_diag16_o_i[:, None] == _inl_1_inv_diag16_o_i[None, :]).to(tl.float16)
    _inl_1_inv_diag16_b_L2 = tl.dot(_inl_1_inv_diag16_b_L, _inl_1_inv_diag16_b_L).to(tl.float16)
    _inl_1_inv_diag16_b_L4 = tl.dot(_inl_1_inv_diag16_b_L2, _inl_1_inv_diag16_b_L2).to(tl.float16)
    _inl_1_inv_diag16_b_L8 = tl.dot(_inl_1_inv_diag16_b_L4, _inl_1_inv_diag16_b_L4).to(tl.float16)
    _inl_1_inv_diag16_b_T = tl.dot(_inl_1_inv_diag16_b_I + _inl_1_inv_diag16_b_L, _inl_1_inv_diag16_b_I + _inl_1_inv_diag16_b_L2)
    _inl_1_inv_diag16_b_T = tl.dot(_inl_1_inv_diag16_b_T.to(tl.float16), _inl_1_inv_diag16_b_I + _inl_1_inv_diag16_b_L4)
    _inl_1_inv_diag16_b_T = tl.dot(_inl_1_inv_diag16_b_T.to(tl.float16), _inl_1_inv_diag16_b_I + _inl_1_inv_diag16_b_L8)
    _inl_1_inv_diag16_result = _inl_1_inv_diag16_b_T
    b_T00 = _inl_1_inv_diag16_result
    tl.store(o_I0 + o_i[None, :], b_T00, mask=m_r0[:, None])
    if NS >= 2:
        r_1 = i_t * BT + NB + o_i
        m_r1 = r_1 < T
        o_A1 = A_ab + (bos * H + i_h) * BT + r_1[:, None] * (H * BT)
        o_I1 = A_ab_inv + (bos * H + i_h) * BT + r_1[:, None] * (H * BT)
        b_L11 = tl.where(m_lo, tl.load(o_A1 + o_c1[None, :], mask=m_r1[:, None], other=0.0), 0.0).to(tl.float16)
        b_L10 = tl.load(o_A1 + o_i[None, :], mask=m_r1[:, None], other=0.0).to(tl.float16)
        _inl_2_inv_diag16_b_L = b_L11
        _inl_2_inv_diag16_o_i = tl.arange(0, 16)
        _inl_2_inv_diag16_b_I = (_inl_2_inv_diag16_o_i[:, None] == _inl_2_inv_diag16_o_i[None, :]).to(tl.float16)
        _inl_2_inv_diag16_b_L2 = tl.dot(_inl_2_inv_diag16_b_L, _inl_2_inv_diag16_b_L).to(tl.float16)
        _inl_2_inv_diag16_b_L4 = tl.dot(_inl_2_inv_diag16_b_L2, _inl_2_inv_diag16_b_L2).to(tl.float16)
        _inl_2_inv_diag16_b_L8 = tl.dot(_inl_2_inv_diag16_b_L4, _inl_2_inv_diag16_b_L4).to(tl.float16)
        _inl_2_inv_diag16_b_T = tl.dot(_inl_2_inv_diag16_b_I + _inl_2_inv_diag16_b_L, _inl_2_inv_diag16_b_I + _inl_2_inv_diag16_b_L2)
        _inl_2_inv_diag16_b_T = tl.dot(_inl_2_inv_diag16_b_T.to(tl.float16), _inl_2_inv_diag16_b_I + _inl_2_inv_diag16_b_L4)
        _inl_2_inv_diag16_b_T = tl.dot(_inl_2_inv_diag16_b_T.to(tl.float16), _inl_2_inv_diag16_b_I + _inl_2_inv_diag16_b_L8)
        _inl_2_inv_diag16_result = _inl_2_inv_diag16_b_T
        b_T11 = _inl_2_inv_diag16_result
        b_T10 = tl.dot(b_T11.to(tl.float16), tl.dot(b_L10, b_T00.to(tl.float16)).to(tl.float16))
        tl.store(o_I1 + o_i[None, :], b_T10, mask=m_r1[:, None])
        tl.store(o_I1 + o_c1[None, :], b_T11, mask=m_r1[:, None])
        tl.store(o_I0 + o_c1[None, :], b_zero, mask=m_r0[:, None])
        if NS == 4:
            o_c2 = 2 * NB + o_i
            o_c3 = 3 * NB + o_i
            r_2 = i_t * BT + 2 * NB + o_i
            r_3 = i_t * BT + 3 * NB + o_i
            m_r2 = r_2 < T
            m_r3 = r_3 < T
            o_A2 = A_ab + (bos * H + i_h) * BT + r_2[:, None] * (H * BT)
            o_A3 = A_ab + (bos * H + i_h) * BT + r_3[:, None] * (H * BT)
            o_I2 = A_ab_inv + (bos * H + i_h) * BT + r_2[:, None] * (H * BT)
            o_I3 = A_ab_inv + (bos * H + i_h) * BT + r_3[:, None] * (H * BT)
            b_L22 = tl.where(m_lo, tl.load(o_A2 + o_c2[None, :], mask=m_r2[:, None], other=0.0), 0.0).to(tl.float16)
            b_L33 = tl.where(m_lo, tl.load(o_A3 + o_c3[None, :], mask=m_r3[:, None], other=0.0), 0.0).to(tl.float16)
            b_L20 = tl.load(o_A2 + o_i[None, :], mask=m_r2[:, None], other=0.0).to(tl.float16)
            b_L21 = tl.load(o_A2 + o_c1[None, :], mask=m_r2[:, None], other=0.0).to(tl.float16)
            b_L30 = tl.load(o_A3 + o_i[None, :], mask=m_r3[:, None], other=0.0).to(tl.float16)
            b_L31 = tl.load(o_A3 + o_c1[None, :], mask=m_r3[:, None], other=0.0).to(tl.float16)
            b_L32 = tl.load(o_A3 + o_c2[None, :], mask=m_r3[:, None], other=0.0).to(tl.float16)
            _inl_3_inv_diag16_b_L = b_L22
            _inl_3_inv_diag16_o_i = tl.arange(0, 16)
            _inl_3_inv_diag16_b_I = (_inl_3_inv_diag16_o_i[:, None] == _inl_3_inv_diag16_o_i[None, :]).to(tl.float16)
            _inl_3_inv_diag16_b_L2 = tl.dot(_inl_3_inv_diag16_b_L, _inl_3_inv_diag16_b_L).to(tl.float16)
            _inl_3_inv_diag16_b_L4 = tl.dot(_inl_3_inv_diag16_b_L2, _inl_3_inv_diag16_b_L2).to(tl.float16)
            _inl_3_inv_diag16_b_L8 = tl.dot(_inl_3_inv_diag16_b_L4, _inl_3_inv_diag16_b_L4).to(tl.float16)
            _inl_3_inv_diag16_b_T = tl.dot(_inl_3_inv_diag16_b_I + _inl_3_inv_diag16_b_L, _inl_3_inv_diag16_b_I + _inl_3_inv_diag16_b_L2)
            _inl_3_inv_diag16_b_T = tl.dot(_inl_3_inv_diag16_b_T.to(tl.float16), _inl_3_inv_diag16_b_I + _inl_3_inv_diag16_b_L4)
            _inl_3_inv_diag16_b_T = tl.dot(_inl_3_inv_diag16_b_T.to(tl.float16), _inl_3_inv_diag16_b_I + _inl_3_inv_diag16_b_L8)
            _inl_3_inv_diag16_result = _inl_3_inv_diag16_b_T
            b_T22 = _inl_3_inv_diag16_result
            _inl_4_inv_diag16_b_L = b_L33
            _inl_4_inv_diag16_o_i = tl.arange(0, 16)
            _inl_4_inv_diag16_b_I = (_inl_4_inv_diag16_o_i[:, None] == _inl_4_inv_diag16_o_i[None, :]).to(tl.float16)
            _inl_4_inv_diag16_b_L2 = tl.dot(_inl_4_inv_diag16_b_L, _inl_4_inv_diag16_b_L).to(tl.float16)
            _inl_4_inv_diag16_b_L4 = tl.dot(_inl_4_inv_diag16_b_L2, _inl_4_inv_diag16_b_L2).to(tl.float16)
            _inl_4_inv_diag16_b_L8 = tl.dot(_inl_4_inv_diag16_b_L4, _inl_4_inv_diag16_b_L4).to(tl.float16)
            _inl_4_inv_diag16_b_T = tl.dot(_inl_4_inv_diag16_b_I + _inl_4_inv_diag16_b_L, _inl_4_inv_diag16_b_I + _inl_4_inv_diag16_b_L2)
            _inl_4_inv_diag16_b_T = tl.dot(_inl_4_inv_diag16_b_T.to(tl.float16), _inl_4_inv_diag16_b_I + _inl_4_inv_diag16_b_L4)
            _inl_4_inv_diag16_b_T = tl.dot(_inl_4_inv_diag16_b_T.to(tl.float16), _inl_4_inv_diag16_b_I + _inl_4_inv_diag16_b_L8)
            _inl_4_inv_diag16_result = _inl_4_inv_diag16_b_T
            b_T33 = _inl_4_inv_diag16_result
            b_T32 = tl.dot(b_T33.to(tl.float16), tl.dot(b_L32, b_T22.to(tl.float16)).to(tl.float16))
            b_P1 = tl.dot(b_L20, b_T00.to(tl.float16)) + tl.dot(b_L21, b_T10.to(tl.float16))
            b_P2 = tl.dot(b_L30, b_T00.to(tl.float16)) + tl.dot(b_L31, b_T10.to(tl.float16))
            b_T20 = tl.dot(b_T22.to(tl.float16), b_P1.to(tl.float16))
            b_T21 = tl.dot(b_T22.to(tl.float16), tl.dot(b_L21, b_T11.to(tl.float16)).to(tl.float16))
            b_T30 = tl.dot(b_T32.to(tl.float16), b_P1.to(tl.float16)) + tl.dot(b_T33.to(tl.float16), b_P2.to(tl.float16))
            b_T31 = tl.dot(b_T32.to(tl.float16), tl.dot(b_L21, b_T11.to(tl.float16)).to(tl.float16)) + tl.dot(b_T33.to(tl.float16), tl.dot(b_L31, b_T11.to(tl.float16)).to(tl.float16))
            tl.store(o_I0 + o_c2[None, :], b_zero, mask=m_r0[:, None])
            tl.store(o_I0 + o_c3[None, :], b_zero, mask=m_r0[:, None])
            tl.store(o_I1 + o_c2[None, :], b_zero, mask=m_r1[:, None])
            tl.store(o_I1 + o_c3[None, :], b_zero, mask=m_r1[:, None])
            tl.store(o_I2 + o_i[None, :], b_T20, mask=m_r2[:, None])
            tl.store(o_I2 + o_c1[None, :], b_T21, mask=m_r2[:, None])
            tl.store(o_I2 + o_c2[None, :], b_T22, mask=m_r2[:, None])
            tl.store(o_I2 + o_c3[None, :], b_zero, mask=m_r2[:, None])
            tl.store(o_I3 + o_i[None, :], b_T30, mask=m_r3[:, None])
            tl.store(o_I3 + o_c1[None, :], b_T31, mask=m_r3[:, None])
            tl.store(o_I3 + o_c2[None, :], b_T32, mask=m_r3[:, None])
            tl.store(o_I3 + o_c3[None, :], b_T33, mask=m_r3[:, None])

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

SHAPES=((2, 33, 3, 16), (3, 33, 3, 16));DTYPES=('float32', 'float16', 'bfloat16');FIXED_META={"BC":16,"IS_VARLEN":False}
SHAPES=((2, 33, 3, 16), (3, 33, 3, 16));DTYPES=('float32', 'float16', 'bfloat16');FIXED_META={"BC":16,"IS_VARLEN":False}
SHAPES=((2, 33, 3, 16), (3, 33, 3, 16));DTYPES=('float32', 'float16', 'bfloat16');FIXED_META={"BC":16,"IS_VARLEN":False}
def ref(args,meta):
    import numpy as np
    B,T,H,BT=int(args["cu_seqlens"].size-1),int(args["T"]),meta["H"],meta["BT"];A=args["A_ab"].reshape(B,T,H,BT);out=np.zeros_like(A);I=np.eye(16,dtype=np.float16)
    for b in range(B):
      for h in range(H):
       for s in range(0,T,BT):
        e=min(s+BT,T);L=np.zeros((16,16),np.float16);L[:e-s,:e-s]=np.tril(A[b,s:e,h,:e-s],-1).astype(np.float16);L2=(L@L).astype(np.float16);L4=(L2@L2).astype(np.float16);L8=(L4@L4).astype(np.float16);R=((I+L)@(I+L2)).astype(np.float16);R=(R@(I+L4)).astype(np.float16);R=(R@(I+L8)).astype(np.float16);out[b,s:e,h,:e-s]=R[:e-s,:e-s]
    return {"A_ab_inv":out.reshape(-1)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
    del dtype
    import numpy as np
    from case_utils import fast_rng
    B,T,H,BT=(int(x) for x in shape);NT=(T+BT-1)//BT;rng=fast_rng(seed);args={"A_ab":_aligned(rng.normal(0,.02,(B,T,H,BT))),"A_ab_inv":_aligned(np.full(B*T*H*BT,-7.)),"cu_seqlens":_aligned(np.arange(B+1)*T,"int32"),"chunk_indices":_aligned(np.zeros(2*B*NT),"int32"),"T":T};meta={**FIXED_META,"H":H,"BT":BT};grid=(NT,B*H);outputs=("A_ab_inv",)
    return _case(prepare_wy_repr_fwd_kernel_safe,grid,args,meta,("A_ab",),outputs,ref(args,meta),shape,'float32',seed,{"grid_formula":"(ceil_div(T,BT),B*H)","output":"A_ab_inv[B,T,H,BT]"},rtol=2e-3,atol=2e-3)
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
