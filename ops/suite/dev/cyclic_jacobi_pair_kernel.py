"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/cyclic_jacobi_pair_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["linalg"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def _cyclic_jacobi_pair_kernel(A_WORK, V_WORK, STEP, K: tl.constexpr, ROUND: tl.constexpr, ROWS: tl.constexpr, BLOCK_R: tl.constexpr, BLOCK_K: tl.constexpr):
    batch = tl.program_id(0)
    pair = tl.program_id(1)
    rows = tl.arange(0, BLOCK_R)
    cols = tl.arange(0, BLOCK_K)
    ring = ROUND - 1
    pos_p = pair
    pos_q = ROUND - 1 - pair
    p = tl.where(pos_p == 0, 0, (pos_p + ring - STEP - 1) % ring + 1)
    q = tl.where(pos_q == 0, 0, (pos_q + ring - STEP - 1) % ring + 1)
    valid_pair = (p < K) & (q < K)
    swap = p > q
    p2 = tl.where(swap, q, p)
    q2 = tl.where(swap, p, q)
    row_mask = (rows < ROWS) & valid_pair
    col_mask = (cols < K) & valid_pair
    aw_base = A_WORK + batch * K * ROWS
    vw_base = V_WORK + batch * K * K
    ap = tl.load(aw_base + p2 * ROWS + rows, mask=row_mask, other=0.0)
    aq = tl.load(aw_base + q2 * ROWS + rows, mask=row_mask, other=0.0)
    alpha = tl.sum(ap * ap)
    beta = tl.sum(aq * aq)
    gamma = tl.sum(ap * aq)
    eps = 1e-20
    abs_gamma = tl.abs(gamma)
    threshold = 1e-07 * tl.sqrt(alpha * beta + eps)
    active = abs_gamma > threshold
    safe_gamma = tl.where(active, gamma, 1.0)
    tau = (beta - alpha) / (2.0 * safe_gamma)
    sign_tau = tl.where(tau >= 0.0, 1.0, -1.0)
    t = sign_tau / (tl.abs(tau) + tl.sqrt(1.0 + tau * tau))
    c = tl.rsqrt(1.0 + t * t)
    s_rot = t * c
    c = tl.where(active, c, 1.0)
    s_rot = tl.where(active, s_rot, 0.0)
    new_ap = c * ap - s_rot * aq
    new_aq = s_rot * ap + c * aq
    tl.store(aw_base + p2 * ROWS + rows, new_ap, mask=row_mask)
    tl.store(aw_base + q2 * ROWS + rows, new_aq, mask=row_mask)
    vp = tl.load(vw_base + p2 * K + cols, mask=col_mask, other=0.0)
    vq = tl.load(vw_base + q2 * K + cols, mask=col_mask, other=0.0)
    new_vp = c * vp - s_rot * vq
    new_vq = s_rot * vp + c * vq
    tl.store(vw_base + p2 * K + cols, new_vp, mask=col_mask)
    tl.store(vw_base + q2 * K + cols, new_vq, mask=col_mask)
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
SHAPES = ((17,),);DTYPES = ('float32', 'float16', 'bfloat16')
def ref(args,meta):
 import numpy as np
 K=int(meta["K"]);R=int(meta["ROWS"]);round_=int(meta["ROUND"]);step=int(args["STEP"]);a=np.array(args["A_WORK"],copy=True).reshape(-1,K,R);v=np.array(args["V_WORK"],copy=True).reshape(-1,K,K)
 def pair_indices(pair):
  ring=round_-1;pp=pair;qq=round_-1-pair;p=0 if pp==0 else (pp+ring-step-1)%ring+1;q=0 if qq==0 else (qq+ring-step-1)%ring+1;return (min(p,q),max(p,q),p<K and q<K)

 def rotation(ap,aq):
  alpha=np.sum(ap*ap,dtype=np.float32);beta=np.sum(aq*aq,dtype=np.float32);gamma=np.sum(ap*aq,dtype=np.float32);active=abs(gamma)>1e-7*np.sqrt(alpha*beta+1e-20)
  if not active:return (np.float32(1),np.float32(0))
  tau=(beta-alpha)/(2*gamma);t=(1 if tau>=0 else -1)/(abs(tau)+np.sqrt(1+tau*tau));c=np.float32(1/np.sqrt(1+t*t));return (c,np.float32(t*c))
 for b in range(a.shape[0]):
  for pair in range(round_//2):
   p,q,valid=pair_indices(pair)
   if valid:
    ap=a[b,p].copy();aq=a[b,q].copy();vp=v[b,p].copy();vq=v[b,q].copy();c,s=rotation(ap,aq);a[b,p]=c*ap-s*aq;a[b,q]=s*ap+c*aq;v[b,p]=c*vp-s*vq;v[b,q]=s*vp+c*vq
 return {"A_WORK":a.reshape(-1),"V_WORK":v.reshape(-1)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 B=3;K=6;R=9;round_=6;step=2;pairs=round_//2;a=rng.normal(0,.4,(B,K,R)).astype(np.float32);v=np.tile(np.eye(K,dtype=np.float32),(B,1,1));args={"A_WORK":_aligned(a,"float32"),"V_WORK":_aligned(v,"float32"),"STEP":step};meta={"K":K,"ROUND":round_,"ROWS":R,"BLOCK_R":16,"BLOCK_K":8};grid=(B,pairs)
 outputs=('A_WORK', 'V_WORK');return _case(_cyclic_jacobi_pair_kernel,grid,args,meta,('A_WORK', 'V_WORK'),outputs,ref(args,meta),shape,"torch.float32",seed,{"complete_launch_plan":True,"formula":'apply each scheduled one-sided Jacobi rotation to both A-work and V-work'})

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
