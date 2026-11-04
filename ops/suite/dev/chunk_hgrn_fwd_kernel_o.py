"""One-JIT standalone Triton compiler test case."""

COPIED_FROM = {'repo': 'ops-pool/core', 'note': 'validated case layer intact; lottery 20261019'}
OPERATOR = {"name": "hidden/chunk_hgrn_fwd_kernel_o", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["fla"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit(do_not_specialize=['T'])
def chunk_hgrn_fwd_kernel_o(gc, o, s_b, s_t, s_d, T, D: tl.constexpr, BT: tl.constexpr, BD: tl.constexpr):
    (i_d, i_b) = (tl.program_id(0), tl.program_id(1).to(tl.int64))
    o_d = i_d * BD + tl.arange(0, BD)
    mask = o_d < D
    for i_t in range(1, tl.cdiv(T, BT)):
        o_t = (i_t * BT).to(tl.int64) + tl.arange(0, BT)
        m_g = (o_t[:, None] < T) & mask[None, :]
        p_gc = gc + i_b * s_b + o_t[:, None] * s_t + o_d[None, :] * s_d
        p_o = o + i_b * s_b + o_t[:, None] * s_t + o_d[None, :] * s_d
        b_h0 = tl.load(o + i_b * T * D + i_t * BT * D - D + o_d, mask=mask, other=0).to(tl.float32)
        b_gc = tl.load(p_gc, mask=m_g, other=0.0).to(tl.float32)
        b_o = tl.load(p_o, mask=m_g, other=0.0).to(tl.float32)
        _inl_1_exp_x = b_gc
        _inl_1_exp_result = tl.exp(_inl_1_exp_x.to(tl.float32))
        b_o = b_o + _inl_1_exp_result * b_h0[None, :]
        tl.store(p_o, b_o.to(p_o.dtype.element_ty), mask=m_g)
        # The next iteration's b_h0 load reads the last row this store wrote —
        # possibly by a different thread of the same CTA. A global-memory
        # load after another thread's store needs a barrier to be ordered;
        # without it the load can read the stale pre-store value when the
        # store has not drained (observed: 2/8 runs wrong under 8-way GPU
        # contention, correct in isolation).
        tl.debug_barrier()
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
SHAPES=((2, 17, 13, 8), (6, 17, 13, 8));DTYPES=('float32', 'float16', 'bfloat16');FIXED_META={"BD":16}



def _local(g,x,BT):
    import numpy as np
    B,T,D=g.shape;o=np.zeros_like(x);gc=np.zeros_like(g)
    for b in range(B):
        for s in range(0,T,BT):
            h=np.zeros(D,np.float32);c=np.zeros(D,np.float32)
            for t in range(s,min(s+BT,T)):h=np.exp(g[b,t])*h+x[b,t];c+=g[b,t];o[b,t]=h;gc[b,t]=c
    return gc,o


def ref(args,meta):
    import numpy as np
    B=args["gc"].shape[0];T=int(args["T"]);D=meta["D"];BT=meta["BT"];gc=args["gc"].reshape(B,T,D);out=args["o"].reshape(B,T,D).copy()
    for s in range(BT,T,BT):out[:,s:min(s+BT,T)]+=np.exp(gc[:,s:min(s+BT,T)])*out[:,s-1:s]
    return {"o":out.reshape(-1)}


def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
    del dtype
    import numpy as np
    B,T,D,BT=(int(x) for x in shape);rng=fast_rng(seed);g=_aligned(rng.uniform(-.4,-.05,(B,T,D)));x=_aligned(rng.normal(0,.2,(B,T,D)));gc,o=_local(g,x,BT);args={"gc":_aligned(gc),"o":_aligned(o),"s_b":T*D,"s_t":D,"s_d":1,"T":T};meta={**FIXED_META,"D":D,"BT":BT};grid=((D+meta["BD"]-1)//meta["BD"],B);outputs=("o",)
    return _case(chunk_hgrn_fwd_kernel_o,grid,args,meta,("gc","o"),outputs,ref(args,meta),shape,"torch.float32",seed,{"grid_formula":"(ceil_div(D,BD),B)","output":"o[B,T,D]"})

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
