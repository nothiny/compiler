"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/topk_stage1_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["reduce"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def topk_stage1_kernel(y_ptr, index_ptr, x_ptr, k, N: tl.constexpr, CHUNK_SIZE: tl.constexpr, DESCENDING: tl.constexpr):
    cur_batch = tl.program_id(0).to(tl.int64)
    cur_chunk_idx = tl.program_id(1).to(tl.int64)
    _inl_3_num_programs_axis: tl.constexpr = 1
    _inl_3_num_programs_result = tl.num_programs(_inl_3_num_programs_axis).to(tl.int64)
    chunk_num = _inl_3_num_programs_result
    y_ptr += cur_batch * chunk_num * k + cur_chunk_idx * k
    index_ptr += cur_batch * chunk_num * k + cur_chunk_idx * k
    chunk_offset = cur_chunk_idx * CHUNK_SIZE
    x_ptr += cur_batch * N + chunk_offset
    cols = tl.arange(0, CHUNK_SIZE)
    mask = chunk_offset + cols < N
    mask_val = float('-inf') if DESCENDING else float('inf')
    x_val = tl.load(x_ptr + cols, mask=mask, other=mask_val).to(tl.float32)
    available = mask
    for k_idx in range(k):
        if DESCENDING:
            chunk_select_val = tl.max(x_val)
        else:
            chunk_select_val = tl.min(x_val)
        is_candidate = available & (x_val == chunk_select_val)
        candidate_indices = tl.where(is_candidate, cols, CHUNK_SIZE)
        chunk_select_idx = tl.argmin(candidate_indices, axis=0)
        tl.store(y_ptr + k_idx, chunk_select_val)
        tl.store(index_ptr + k_idx, chunk_select_idx + chunk_offset)
        if DESCENDING:
            x_val = tl.where(cols == chunk_select_idx, float('-inf'), x_val)
        else:
            x_val = tl.where(cols == chunk_select_idx, float('inf'), x_val)
        available = available & (cols != chunk_select_idx)
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
 B=args["x_ptr"].size//meta["N"];C=meta["N"];chunk=meta["CHUNK_SIZE"];k=int(args["k"]);x=args["x_ptr"].reshape(B,C);vals=[];inds=[]
 for row in x:
  for s in range(0,C,chunk):
   part=row[s:min(s+chunk,C)];order=np.argsort(-part,kind="stable")[:k];vals.extend(part[order]);inds.extend(s+order)
 return {"y_ptr":np.asarray(vals,np.float32),"index_ptr":np.asarray(inds,np.int64)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 B=3;C=max(4,N//B);chunk=128;k=3;chunks=(C+chunk-1)//chunk;args={"y_ptr":_aligned(np.full(B*chunks*k,-7.)),"index_ptr":_aligned(np.full(B*chunks*k,-1),"int64"),"x_ptr":_aligned(rng.normal(0,.8,B*C)),"k":k};meta={"N":C,"CHUNK_SIZE":chunk,"DESCENDING":True};grid=(B,chunks)
 outputs=('y_ptr', 'index_ptr');return _case(topk_stage1_kernel,grid,args,meta,('x_ptr',),outputs,ref(args,meta),shape,"torch.float32",seed,{"complete_launch_plan":True,"formula":'top-k candidates from every input chunk'})

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
