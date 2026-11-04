"""parallel_path_fwd_kernel_prepare_k_cache: 从 ~/ops 仓库复制(fla @ ops-pool),保留其已验证的 case 层。

模式: args.runtime_scalar、cast.to、control.for_range、control.if、control.loop_carried、creation.arange、creation.where、creation.zeros、dtype.float32、dtype.int32。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。循环上界来自运行时标量(不是 constexpr)。constexpr 参数: H, K, BT, BK, IS_VARLEN。

文件只有两层:
  ① parallel_path_fwd_kernel_prepare_k_cache   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/parallel_path_fwd_kernel_prepare_k_cache', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'cast.to', 'control.for_range', 'control.if', 'control.loop_carried', 'creation.arange', 'creation.where', 'creation.zeros', 'dtype.float32', 'dtype.int32', 'dtype.int64', 'linalg.dot', 'math.cdiv', 'memory.load', 'memory.load.masked', 'memory.load.other', 'memory.store', 'memory.store.masked', 'shape.reshape', 'shape.trans', 'tile.2d', 'tile.3d']}
COPIED_FROM = {'repo': 'fla @ ops-pool', 'note': 'validated case layer intact'}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit(do_not_specialize=['T'])
def parallel_path_fwd_kernel_prepare_k_cache(k, k_new, w1, w2, offsets, indices, T, H: tl.constexpr, K: tl.constexpr, BT: tl.constexpr, BK: tl.constexpr, IS_VARLEN: tl.constexpr):
    (i_t, i_bh) = (tl.program_id(0).to(tl.int64), tl.program_id(1))
    (i_b, i_h) = (i_bh // H, i_bh % H)
    if IS_VARLEN:
        (i_n, i_t) = (tl.load(indices + i_t * 2).to(tl.int32), tl.load(indices + i_t * 2 + 1).to(tl.int64))
        (bos, eos) = (tl.load(offsets + i_n).to(tl.int64), tl.load(offsets + i_n + 1).to(tl.int64))
        T = (eos - bos).to(tl.int32)
    else:
        i_n = i_b
        (bos, eos) = ((i_n * T).to(tl.int64), (i_n * T + T).to(tl.int64))
    k += (bos * H + i_h) * K
    k_new += (bos * H + i_h) * K
    w1 += (bos * H + i_h) * K
    w2 += (bos * H + i_h) * K
    o_k = i_t * BT + tl.arange(0, BT)
    o_d = tl.arange(0, BK)
    m_k = (o_k[:, None] < T) & (o_d[None, :] < K)
    p_k = k + o_k[:, None] * (H * K) + o_d[None, :]
    b_k = tl.zeros([BT, BK], dtype=tl.float32)
    b_k += tl.load(p_k, mask=m_k, other=0.0)
    for k_block_idx in range(i_t + 1, tl.cdiv(T, BT)):
        o_w = k_block_idx * BT + tl.arange(0, BT)
        m_w = (o_w[:, None] < T) & (o_d[None, :] < K)
        p_w1 = w1 + o_w[:, None] * (H * K) + o_d[None, :]
        p_w2 = w2 + o_w[:, None] * (H * K) + o_d[None, :]
        b_w1 = tl.load(p_w1, mask=m_w, other=0.0)
        b_w2 = tl.load(p_w2, mask=m_w, other=0.0)
        b_A = tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_k.to(b_w2.dtype).shape[1])[None, None, :] == 0, b_k.to(b_w2.dtype)[:, :, None], 0), (b_k.to(b_w2.dtype).shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_k.to(b_w2.dtype).shape[1])[None, :, None] == 0, tl.trans(b_w2)[:, None, :], 0), (16, tl.trans(b_w2).shape[1])).to(tl.float32)) if b_k.to(b_w2.dtype).shape[1] < 16 else tl.dot(b_k.to(b_w2.dtype), tl.trans(b_w2))
        b_k = b_k - (tl.dot(tl.reshape(tl.where(tl.arange(0, 16 // b_A.to(b_w1.dtype).shape[1])[None, None, :] == 0, b_A.to(b_w1.dtype)[:, :, None], 0), (b_A.to(b_w1.dtype).shape[0], 16)).to(tl.float32), tl.reshape(tl.where(tl.arange(0, 16 // b_A.to(b_w1.dtype).shape[1])[None, :, None] == 0, b_w1[:, None, :], 0), (16, b_w1.shape[1])).to(tl.float32)) if b_A.to(b_w1.dtype).shape[1] < 16 else tl.dot(b_A.to(b_w1.dtype), b_w1))
    p_k_new = k_new + o_k[:, None] * (H * K) + o_d[None, :]
    tl.store(p_k_new, b_k.to(p_k_new.dtype.element_ty), mask=m_k)

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

SHAPES = ((17,), (10, 17, 2, 6));DTYPES = ('float32', 'float16', 'bfloat16')
SHAPES = ((17,), (10, 17, 2, 6));DTYPES = ('float32', 'float16', 'bfloat16')
def ref(args,meta):
 import numpy as np
 T=int(args["T"]);H=int(meta["H"]);K=int(meta["K"]);BT=int(meta["BT"]);x=np.asarray(args["k"],np.float32).reshape(-1,T,H,K);w1=np.asarray(args["w1"],np.float32).reshape(-1,T,H,K);w2=np.asarray(args["w2"],np.float32).reshape(-1,T,H,K);out=np.zeros_like(x)
 for b in range(x.shape[0]):
  for h in range(H):
   for start in range(0,T,BT):
    stop=min(start+BT,T);cur=np.zeros((BT,K),np.float32);cur[:stop-start]=x[b,start:stop,h]
    for future in range(start+BT,T,BT):
     end=min(future+BT,T);one=np.zeros((BT,K),np.float32);two=np.zeros((BT,K),np.float32);one[:end-future]=w1[b,future:end,h];two[:end-future]=w2[b,future:end,h];cur-=cur@two.T@one
    out[b,start:stop,h]=cur[:stop-start]
 return {"k_new":out.reshape(-1)}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    if len(shape) > 1 and tuple(shape) not in SHAPES:
        raise ValueError('unsupported explicit shape configuration')
    del dtype
    import numpy as np
    N = int(shape[0])
    from case_utils import fast_rng
    rng = fast_rng(seed)
    B = int(shape[0]) if len(shape) > 1 else 2
    H = int(shape[2]) if len(shape) > 1 else 2
    T = int(shape[1]) if len(shape) > 1 else max(17, min(65, N | 1))
    K = int(shape[3]) if len(shape) > 1 else 6
    BT = 8
    shape = (B, T, H, K)
    args = {'k': _aligned(rng.normal(0, 0.25, shape), 'float32'), 'k_new': _aligned(np.full(B * T * H * K, -7), 'float32'), 'w1': _aligned(rng.normal(0, 0.08, shape), 'float32'), 'w2': _aligned(rng.normal(0, 0.08, shape), 'float32'), 'offsets': _aligned(np.arange(B + 1) * T, 'int64'), 'indices': _aligned(np.zeros(2, dtype=np.int64), 'int64'), 'T': T}
    meta = {'H': H, 'K': K, 'BT': BT, 'BK': 8, 'IS_VARLEN': False}
    grid = ((T + BT - 1) // BT, B * H)
    outputs = ('k_new',)
    return _case(parallel_path_fwd_kernel_prepare_k_cache, grid, args, meta, ('k', 'w1', 'w2'), outputs, ref(args, meta), shape, 'float32', seed, {'complete_launch_plan': True, 'formula': 'apply all future path Householder-like cache corrections to each complete current key chunk'})
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
