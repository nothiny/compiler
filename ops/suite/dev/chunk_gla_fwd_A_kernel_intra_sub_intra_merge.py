"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/chunk_gla_fwd_A_kernel_intra_sub_intra_merge", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["fla"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit(do_not_specialize=['T'])
def chunk_gla_fwd_A_kernel_intra_sub_intra_merge(A, A2, cu_seqlens, chunk_indices, T, B: tl.constexpr, H: tl.constexpr, BT: tl.constexpr, BC: tl.constexpr, NK: tl.constexpr, IS_VARLEN: tl.constexpr):
    (i_t, i_c, i_bh) = (tl.program_id(0).to(tl.int64), tl.program_id(1), tl.program_id(2).to(tl.int64))
    (i_b, i_h) = (i_bh // H, i_bh % H)
    if IS_VARLEN:
        (i_n, i_t) = (tl.load(chunk_indices + i_t * 2).to(tl.int32), tl.load(chunk_indices + i_t * 2 + 1).to(tl.int64))
        (bos, eos) = (tl.load(cu_seqlens + i_n).to(tl.int64), tl.load(cu_seqlens + i_n + 1).to(tl.int64))
        all = T
        T = eos - bos
    else:
        (bos, eos) = (i_b * T, i_b * T + T)
        all = B * T
    if i_t * BT + i_c * BC >= T:
        return
    b_A = tl.zeros([BC, BC], dtype=tl.float32)
    o_c = i_t * BT + i_c * BC + tl.arange(0, BC)
    o_i = tl.arange(0, BC)
    m_c = o_c < T
    m_A = m_c[:, None] & (o_i[None, :] < BC)
    m_A2 = m_c[:, None] & ((i_c * BC + o_i)[None, :] < BT)
    for i_k in range(0, NK):
        p_A = A + (i_k * all + bos) * H * BC + i_h * BC + o_c[:, None] * (H * BC) + o_i[None, :]
        b_A += tl.load(p_A, mask=m_A, other=0.0)
    p_A2 = A2 + (bos * H + i_h) * BT + o_c[:, None] * (H * BT) + (i_c * BC + o_i)[None, :]
    tl.store(p_A2, b_A.to(A2.dtype.element_ty), mask=m_A2)
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
SHAPES=((2,17,3,8,4,3),(3,33,5,16,4,5));DTYPES=('float32', 'float16', 'bfloat16');FIXED_META={"IS_VARLEN":False}
def ref(args, meta):
    import numpy as np
    B, H, BT, BC, NK = (meta[k] for k in ('B', 'H', 'BT', 'BC', 'NK'))
    T = int(args['T'])
    values = args['A'].reshape(NK, B, T, H, BC).sum(axis=0)
    out = args['A2'].reshape(B, T, H, BT).copy()
    for t in range(T):
        col = ((t % BT) // BC) * BC
        out[:, t, :, col:col + BC] = values[:, t]
    return {'A2': out.reshape(-1)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 B,T,H,BT,BC,NK=(int(x) for x in shape);NT=(T+BT-1)//BT;rng=fast_rng(seed);args={"A":_aligned(rng.normal(0,.1,(NK,B,T,H,BC))),"A2":_aligned(np.full(B*T*H*BT,-7.)),"cu_seqlens":_aligned(np.arange(B+1)*T,"int32"),"chunk_indices":_aligned(np.zeros(2*B*NT),"int32"),"T":T};meta={**FIXED_META,"B":B,"H":H,"BT":BT,"BC":BC,"NK":NK};grid=(NT,BT//BC,B*H);outputs=("A2",)
 return _case(chunk_gla_fwd_A_kernel_intra_sub_intra_merge,grid,args,meta,("A",),outputs,ref(args,meta),shape,"torch.float32",seed,{"grid_formula":"(ceil_div(T,BT),BT/BC,B*H)","output":"A2[B,T,H,BT]"})

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
