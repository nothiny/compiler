"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/thin_reorthogonalize_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def _thin_reorthogonalize_kernel(Q, ROWS: tl.constexpr, K: tl.constexpr, BLOCK_R: tl.constexpr):
    batch = tl.program_id(0)
    rows = tl.arange(0, BLOCK_R)
    row_mask = rows < ROWS
    base = Q + batch * ROWS * K
    eps = 1e-20
    for j in tl.static_range(0, K):
        vec = tl.load(base + rows * K + j, mask=row_mask, other=0.0).to(tl.float32)
        original_norm = tl.sqrt(tl.sum(vec * vec))
        for prev in tl.static_range(0, K):
            if prev < j:
                q_prev = tl.load(base + rows * K + prev, mask=row_mask, other=0.0).to(tl.float32)
                coeff = tl.sum(vec * q_prev)
                vec = vec - coeff * q_prev
        for prev in tl.static_range(0, K):
            if prev < j:
                q_prev = tl.load(base + rows * K + prev, mask=row_mask, other=0.0).to(tl.float32)
                coeff = tl.sum(vec * q_prev)
                vec = vec - coeff * q_prev
        norm = tl.sqrt(tl.sum(vec * vec))
        basis = tl.where(rows == j, 1.0, 0.0)
        vec = tl.where(norm > tl.maximum(eps, original_norm * 1e-06), vec, basis)
        for prev in tl.static_range(0, K):
            if prev < j:
                q_prev = tl.load(base + rows * K + prev, mask=row_mask, other=0.0).to(tl.float32)
                coeff = tl.sum(vec * q_prev)
                vec = vec - coeff * q_prev
        norm = tl.sqrt(tl.sum(vec * vec))
        vec = vec / tl.maximum(norm, eps)
        tl.store(base + rows * K + j, vec, mask=row_mask)
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
SHAPES = ((17,),);DTYPES = ('float32',)
def ref(args,meta):
 import numpy as np
 R=int(meta["ROWS"]);K=int(meta["K"]);q=np.asarray(args["Q"],np.float32).reshape(-1,R,K);out=np.empty_like(q)
 for b in range(q.shape[0]):
  for j in range(K):
   v=q[b,:,j].copy(); original_norm=np.linalg.norm(v)
   for _ in range(2):
    for p in range(j):v-=out[b,:,p]*np.sum(v*out[b,:,p],dtype=np.float32)
   if np.sqrt(np.sum(v*v,dtype=np.float32))<=max(1e-20, original_norm*1e-6):v=(np.arange(R)==j).astype(np.float32)
   for p in range(j):v-=out[b,:,p]*np.sum(v*out[b,:,p],dtype=np.float32)
   v/=max(np.sqrt(np.sum(v*v,dtype=np.float32)),1e-20);out[b,:,j]=v
 return {"Q":out.reshape(-1)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 B=3;R=8;K=4;q=rng.normal(0,.4,(B,R,K)).astype(np.float32);q[:,:,1]=q[:,:,0];q[:,:,3]=0;args={"Q":_aligned(q,"float32")};meta={"ROWS":R,"K":K,"BLOCK_R":8};grid=(B,)
 outputs=('Q',);return _case(_thin_reorthogonalize_kernel,grid,args,meta,('Q',),outputs,ref(args,meta),shape,"torch.float32",seed,{"complete_launch_plan":True,"formula":'two-pass modified Gram-Schmidt, coordinate fallback, final projection, and normalization'})

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
