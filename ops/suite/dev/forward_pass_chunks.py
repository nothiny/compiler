"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/forward_pass_chunks", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit(do_not_specialize=['T'])
def _forward_pass_chunks(a, sa, ac, h0, cu_seqlens, B: tl.constexpr, T, H: tl.constexpr, D: tl.constexpr, CHUNK_LEN: tl.constexpr, a_stride_b, a_stride_c, a_stride_h, a_stride_d, sa_stride_b, sa_stride_c, sa_stride_h, ac_stride_b, ac_stride_c, ac_stride_h, ac_stride_d, BK: tl.constexpr, USE_INITIAL_STATE: tl.constexpr, IS_VARLEN: tl.constexpr):
    i_nh = tl.program_id(0).to(tl.int64)
    if IS_VARLEN:
        i_n = i_nh // H
        h = i_nh % H
        bos = tl.load(cu_seqlens + i_n).to(tl.int32)
        eos = tl.load(cu_seqlens + i_n + 1).to(tl.int32)
        T = eos - bos
        b = i_n.to(tl.int64)
    else:
        b = i_nh // H
        h = i_nh % H
        if b >= B:
            return
    if h >= H:
        return
    N_chunks = tl.cdiv(T, CHUNK_LEN)
    for i_k in range(tl.cdiv(D, BK)):
        d_offset = i_k * BK
        D_range = d_offset + tl.arange(0, BK)
        D_mask = D_range < D
        sa_ptr = sa + b * sa_stride_b + h * sa_stride_h
        a_ptr = a + b * a_stride_b + h * a_stride_h + D_range * a_stride_d
        ac_ptr = ac + b * ac_stride_b + h * ac_stride_h + D_range * ac_stride_d
        if USE_INITIAL_STATE:
            ac_val = tl.load(h0 + i_nh * D + D_range, mask=D_mask, other=0).to(tl.float32)
        else:
            ac_val = tl.zeros([BK], dtype=tl.float32)
        for chunk_id in tl.range(N_chunks):
            a_val = tl.load(a_ptr, D_mask).to(tl.float32)
            sa_val = tl.load(sa_ptr).to(tl.float32)
            ac_val = tl.exp(sa_val) * ac_val + a_val
            tl.store(ac_ptr, ac_val, mask=D_mask)
            sa_ptr += sa_stride_c
            a_ptr += a_stride_c
            ac_ptr += ac_stride_c
CASE_SCHEMA = 3
SUPPORT_STATUS = "supported"
VALIDATION_SCOPE = "full-launch-correctness"
SEED = 20260826


def _aligned(values, dtype, alignment=64):
    import numpy as np

    values = np.asarray(values, dtype=np.dtype(dtype))
    raw = np.empty(values.size * values.dtype.itemsize + alignment, dtype=np.uint8)
    start = -raw.ctypes.data % alignment
    result = raw[start : start + values.size * values.dtype.itemsize].view(values.dtype)
    result[...] = values.reshape(-1)
    return result.reshape(values.shape)


def _comparison(outputs, exact=False, rtol=0.0001, atol=0.0001, dtype=None):
    if not exact:
        _comparison_dtype_policy = str(dtype)
        if _comparison_dtype_policy == 'torch.float32':
            (rtol, atol) = (0.0001, 0.0001)
        elif _comparison_dtype_policy == 'torch.bfloat16':
            (rtol, atol) = (0.01, 0.01)
    return {name: {'profile': 'exact' if exact else 'elementwise-strict', 'comparator': 'array_equal' if exact else 'allclose', 'exact': bool(exact), 'rtol': 0.0 if exact else float(rtol), 'atol': 0.0 if exact else float(atol), 'equal_nan': not exact} for name in outputs}


def _layouts(args):
    import numpy as np

    return {
        name: {
            "shape": tuple(int(value) for value in np.asarray(array).shape),
            "strides": tuple(int(value // np.asarray(array).dtype.itemsize) for value in np.asarray(array).strides),
        }
        for name, array in args.items()
        if isinstance(array, np.ndarray)
    }
SHAPES = ((2, 17, 3, 13), (4, 65, 5, 61))
DTYPES = ('float32', 'float16', 'bfloat16')
FIXED_META = {"CHUNK_LEN":8,"USE_INITIAL_STATE":True,"IS_VARLEN":False}
LAUNCH_META = {"num_warps":4,"num_stages":1}


def ref(args,meta):
    import numpy as np
    batches,heads,dim=int(meta["B"]),int(meta["H"]),int(meta["D"]); chunks=(int(args["T"])+int(meta["CHUNK_LEN"])-1)//int(meta["CHUNK_LEN"]); a=np.asarray(args["a"],dtype=np.float32).reshape(batches,chunks,heads,dim); sa=np.asarray(args["sa"],dtype=np.float32).reshape(batches,chunks,heads); state=np.asarray(args["h0"],dtype=np.float32).reshape(batches,heads,dim).copy(); out=np.empty((batches,chunks,heads,dim),dtype=np.float32)
    for chunk in range(chunks): state=np.exp(sa[:,chunk,:,None])*state+a[:,chunk]; out[:,chunk]=state
    return {"ac":out.reshape(-1)}


def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    import numpy as np
    (batches, time, heads, dim) = (int(value) for value in shape)
    del dtype
    chunk_len = FIXED_META['CHUNK_LEN']
    chunks = (time + chunk_len - 1) // chunk_len
    rng = fast_rng(seed)
    args = {'a': _aligned(rng.normal(0, 0.1, batches * chunks * heads * dim), 'float32'), 'sa': _aligned(rng.uniform(-0.5, -0.05, batches * chunks * heads), 'float32'), 'ac': _aligned(np.full(batches * chunks * heads * dim, -0.875), 'float32'), 'h0': _aligned(rng.normal(0, 0.1, batches * heads * dim), 'float32'), 'cu_seqlens': _aligned(np.arange(batches + 1, dtype=np.int32) * time, 'int32'), 'T': time, 'a_stride_b': chunks * heads * dim, 'a_stride_c': heads * dim, 'a_stride_h': dim, 'a_stride_d': 1, 'sa_stride_b': chunks * heads, 'sa_stride_c': heads, 'sa_stride_h': 1, 'ac_stride_b': chunks * heads * dim, 'ac_stride_c': heads * dim, 'ac_stride_h': dim, 'ac_stride_d': 1}
    meta = {**FIXED_META, 'B': batches, 'H': heads, 'D': dim, 'BK': 1 << (dim - 1).bit_length()}
    grid = (batches * heads,)
    outputs = ('ac',)
    return {'kernel': _forward_pass_chunks, 'grid': grid, 'args': args, 'meta': meta, 'launch_meta': dict(LAUNCH_META), 'inputs': ('a', 'sa', 'h0'), 'outputs': outputs, 'expected': ref(args, meta), 'comparison': _comparison(outputs, rtol=0.0002, atol=2e-05, dtype='torch.float32'), 'pointer_dtypes': {'a': 'float32', 'sa': 'float32', 'ac': 'float32', 'h0': 'float32', 'cu_seqlens': 'int32'}, 'buffer_extents': {name: int(value.size) for (name, value) in args.items() if isinstance(value, np.ndarray)}, 'buffer_layouts': _layouts(args), 'alignment': 64, 'aliases': {}, 'seed': int(seed), 'shape': tuple(shape), 'dtype': 'torch.float32', 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'coverage': {'complete_logical_output': True, 'grid_formula': '(B*H,)', 'stage': 'sequential state pass across every chunk'}}

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
