"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/rms_norm_loop_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["norm"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit(do_not_specialize=['eps'])
def rms_norm_loop_kernel(out_ptr, INV_RMS, in_ptr, w_ptr, N, eps, TILE_N: tl.constexpr):
    if tl.constexpr(in_ptr.dtype.element_ty == tl.float16) or tl.constexpr(in_ptr.dtype.element_ty == tl.bfloat16):
        cdtype = tl.float32
    else:
        cdtype = in_ptr.dtype.element_ty
    pid = tl.program_id(0).to(tl.int64)
    acc = tl.zeros((TILE_N,), dtype=tl.float32)
    num_steps = tl.cdiv(N, TILE_N)
    for step in range(0, num_steps - 1):
        start_n = step * TILE_N
        n_offsets = start_n + tl.arange(0, TILE_N)
        x = tl.load(in_ptr + pid * N + n_offsets).to(tl.float32)
        acc += x * x
    start_n = (num_steps - 1) * TILE_N
    n_offsets = start_n + tl.arange(0, TILE_N)
    mask = n_offsets < N
    x = tl.load(in_ptr + pid * N + n_offsets, mask=mask, other=0.0).to(tl.float32)
    acc += x * x
    var = tl.sum(acc) / N
    rrms = 1 / tl.sqrt(var + eps)
    tl.store(INV_RMS + pid, rrms)
    _inl_2_prev_multiple_of_a = N
    _inl_2_prev_multiple_of_b = TILE_N
    _inl_2_prev_multiple_of_result = tl.cdiv(_inl_2_prev_multiple_of_a, _inl_2_prev_multiple_of_b) * _inl_2_prev_multiple_of_b - _inl_2_prev_multiple_of_b
    prev_multiple = _inl_2_prev_multiple_of_result
    for start_n in range(0, TILE_N, TILE_N):
        n_offsets = prev_multiple - start_n + tl.arange(0, TILE_N)
        mask = n_offsets < N
        x = tl.load(in_ptr + pid * N + n_offsets, mask=mask, other=0.0, eviction_policy='evict_first').to(cdtype)
        w = tl.load(w_ptr + n_offsets, mask=mask, other=0.0)
        x_normed = (x * rrms).to(in_ptr.dtype.element_ty)
        y = x_normed * w
        tl.store(out_ptr + pid * N + n_offsets, y, mask=mask)
    for start_n in range(TILE_N, N, TILE_N):
        n_offsets = prev_multiple - start_n + tl.arange(0, TILE_N)
        x = tl.load(in_ptr + pid * N + n_offsets, eviction_policy='evict_first').to(cdtype)
        w = tl.load(w_ptr + n_offsets)
        x_normed = (x * rrms).to(in_ptr.dtype.element_ty)
        y = x_normed * w
        tl.store(out_ptr + pid * N + n_offsets, y)
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
SHAPES=((17,), (97,));DTYPES=('float32', 'float16', 'bfloat16')
def ref(args,meta):
 import numpy as np
 C=int(args["N"]);x=args["in_ptr"].reshape(-1,C);rr=1/np.sqrt(np.mean(x*x,axis=1)+np.float32(args["eps"]));return {"out_ptr":(x*rr[:,None]*args["w_ptr"][:C]).reshape(-1),"INV_RMS":rr.astype(np.float32)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 R=3;C=max(2,N//R);T=R*C;args={"out_ptr":_aligned(np.full(T,-7.)),"INV_RMS":_aligned(np.full(R,-7.)),"in_ptr":_aligned(rng.normal(0,.8,T)),"w_ptr":_aligned(rng.uniform(.5,1.5,C)),"N":C,"eps":1e-5};meta={"TILE_N":128};grid=(R,)
 outputs=('out_ptr', 'INV_RMS');return _case(rms_norm_loop_kernel,grid,args,meta,('in_ptr', 'w_ptr'),outputs,ref(args,meta),shape,"torch.float32",seed,{"complete_launch_plan":True,"formula":'RMS normalization and inverse-RMS output'})

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
