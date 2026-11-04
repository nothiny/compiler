"""One-JIT standalone Triton compiler test case."""

COPIED_FROM = {'repo': 'ops-pool/core', 'note': 'validated case layer intact; lottery 20261019'}
OPERATOR = {"name": "hidden/prepare_wy_repr_fwd_kernel_chunk32", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["fla"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit(do_not_specialize=['T'])
def prepare_wy_repr_fwd_kernel_chunk32(A_ab, A_ab_inv, cu_seqlens, chunk_indices, T, H: tl.constexpr, BT: tl.constexpr, BC: tl.constexpr, IS_VARLEN: tl.constexpr):
    (i_t, i_bh) = (tl.program_id(0).to(tl.int64), tl.program_id(1).to(tl.int64))
    (i_b, i_h) = (i_bh // H, i_bh % H)
    if IS_VARLEN:
        (i_n, i_t) = (tl.load(chunk_indices + i_t * 2).to(tl.int32), tl.load(chunk_indices + i_t * 2 + 1).to(tl.int64))
        (bos, eos) = (tl.load(cu_seqlens + i_n).to(tl.int64), tl.load(cu_seqlens + i_n + 1).to(tl.int64))
        T = eos - bos
    else:
        (bos, eos) = (i_b * T, i_b * T + T)
    o_t = i_t * BT + tl.arange(0, BT)
    o_A = tl.arange(0, BT)
    m_t = o_t < T
    m_A = m_t[:, None] & (o_A[None, :] < BT)
    p_Aab = A_ab + (bos * H + i_h) * BT + o_t[:, None] * (H * BT) + o_A[None, :]
    p_Aab_inv = A_ab_inv + (bos * H + i_h) * BT + o_t[:, None] * (H * BT) + o_A[None, :]
    b_A_ab = tl.load(p_Aab, mask=m_A, other=0.0)
    b_A_ab = tl.where(tl.arange(0, BT)[:, None] > tl.arange(0, BT)[None, :], b_A_ab, 0)
    for i in range(1, BT):
        mask = tl.arange(0, BT) == i
        b_a = tl.sum(tl.where(mask[:, None], b_A_ab, 0), 0)
        b_a = b_a + tl.sum(b_a[:, None] * b_A_ab, 0) * (tl.arange(0, BT) < i)
        b_A_ab = tl.where(mask[:, None], b_a, b_A_ab)
    b_A_ab += tl.arange(0, BT)[:, None] == tl.arange(0, BT)[None, :]
    tl.store(p_Aab_inv, b_A_ab.to(p_Aab_inv.dtype.element_ty), mask=m_A)
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
SHAPES=((2, 33, 3, 32), (3, 33, 3, 32));DTYPES=('float32', 'float16');FIXED_META={"BC":16,"IS_VARLEN":False}

def ref(args,meta):
    import numpy as np
    B,T,H,BT=int(args["cu_seqlens"].size-1),int(args["T"]),meta["H"],meta["BT"];A=args["A_ab"].reshape(B,T,H,BT);out=np.zeros_like(A)
    for b in range(B):
      for h in range(H):
       for s in range(0,T,BT):
        e=min(s+BT,T);L=np.tril(A[b,s:e,h,:e-s],-1);R=L.copy()
        for i in range(1,e-s):R[i,:i]=R[i,:i]+R[i]@R[:,:i]
        out[b,s:e,h,:e-s]=R+np.eye(e-s,dtype=np.float32)
    return {"A_ab_inv":out.reshape(-1)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
    del dtype
    import numpy as np
    B,T,H,BT=(int(x) for x in shape);NT=(T+BT-1)//BT;rng=fast_rng(seed);args={"A_ab":_aligned(rng.normal(0,.03,(B,T,H,BT))),"A_ab_inv":_aligned(np.full(B*T*H*BT,-7.)),"cu_seqlens":_aligned(np.arange(B+1)*T,"int32"),"chunk_indices":_aligned(np.zeros(2*B*NT),"int32"),"T":T};meta={**FIXED_META,"H":H,"BT":BT};grid=(NT,B*H);outputs=("A_ab_inv",)
    return _case(prepare_wy_repr_fwd_kernel_chunk32,grid,args,meta,("A_ab",),outputs,ref(args,meta),shape,"torch.float32",seed,{"grid_formula":"(ceil_div(T,BT),B*H)","output":"A_ab_inv[B,T,H,BT]"})

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
