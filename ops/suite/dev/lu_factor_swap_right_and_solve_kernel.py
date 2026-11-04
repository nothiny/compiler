"""One-JIT standalone Triton compiler test case."""

COPIED_FROM = {'repo': 'ops-pool/flaggems', 'note': 'validated case layer intact; lottery 20261019'}
OPERATOR = {"name": "hidden/lu_factor_swap_right_and_solve_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["linalg"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def _lu_factor_swap_right_and_solve_kernel(LU, PIVOTS, K0: tl.constexpr, M: tl.constexpr, N: tl.constexpr, K: tl.constexpr, PANEL: tl.constexpr, BLOCK_B: tl.constexpr, BLOCK_N: tl.constexpr):
    """Apply panel pivots to trailing columns and solve for U rows in one pass."""
    pid_n = tl.program_id(0)
    pid_b = tl.program_id(1)
    brows = tl.arange(0, BLOCK_B)
    cols = K0 + PANEL + pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    rows = K0 + brows
    offsets = pid_b * M * N + rows[:, None] * N + cols[None, :]
    mask = (brows[:, None] < PANEL) & (cols[None, :] < N)
    vals = tl.load(LU + offsets, mask=mask, other=0.0).to(tl.float32)
    col_mask = cols[None, :] < N
    for jj in tl.range(0, PANEL):
        j = K0 + jj
        pivot_row = tl.load(PIVOTS + pid_b * K + j) - 1
        row_j = tl.sum(tl.where(brows[:, None] == jj, vals, 0.0), axis=0)
        row_p_offsets = pid_b * M * N + pivot_row * N + cols
        row_p = tl.load(LU + row_p_offsets, mask=cols < N, other=0.0).to(tl.float32)
        vals = tl.where((brows[:, None] == jj) & col_mask, row_p[None, :], vals)
        rel_pivot = pivot_row - K0
        vals = tl.where((brows[:, None] == rel_pivot) & col_mask, row_j[None, :], vals)
        tl.store(LU + row_p_offsets, row_j, mask=cols < N)
    for jj in tl.range(0, PANEL):
        row_j = tl.sum(tl.where(brows[:, None] == jj, vals, 0.0), axis=0)
        l_col_offsets = pid_b * M * N + (K0 + brows) * N + (K0 + jj)
        l_col = tl.load(LU + l_col_offsets, mask=brows < PANEL, other=0.0).to(tl.float32)
        l_col = tl.where(brows <= jj, 0.0, l_col)
        vals = tl.where(brows[:, None] > jj, vals - l_col[:, None] * row_j[None, :], vals)
    tl.store(LU + offsets, vals, mask=mask)
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
SHAPES = ((17,), (4, 9));DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 B=args["LU"].size//(int(meta["M"])*int(meta["N"]));M=int(meta["M"]);D=int(meta["N"]);K0=int(meta["K0"]);P=int(meta["PANEL"]);K=int(meta["K"]);out=np.array(args["LU"],copy=True).reshape(B,M,D);piv=np.asarray(args["PIVOTS"],np.int32).reshape(B,K);start=K0+P
 for b in range(B):
  vals=out[b,K0:K0+P,start:D].copy()
  for jj in range(P):
   p=int(piv[b,K0+jj])-1;row=vals[jj].copy();pval=out[b,p,start:D].copy();vals[jj]=pval;rel=p-K0
   if 0<=rel<P:vals[rel]=row
   out[b,p,start:D]=row
  for jj in range(P):
   row=vals[jj].copy()
   for i in range(jj+1,P):vals[i]-=out[b,K0+i,K0+jj]*row
  out[b,K0:K0+P,start:D]=vals
 return {"LU":out.reshape(-1)}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    if len(shape) > 1 and tuple(shape) not in SHAPES:
        raise ValueError('unsupported explicit shape configuration')
    del dtype
    import numpy as np
    N = int(shape[0])
    rng = fast_rng(seed)
    B = int(shape[0]) if len(shape) > 1 else 2
    D = int(shape[1]) if len(shape) > 1 else 9
    K0 = 1
    P = 3
    K = min(D, D)
    x = rng.normal(0, 0.5, (B, D, D)).astype(np.float32)
    piv = np.tile(np.arange(1, K + 1, dtype=np.int32), (B, 1))
    piv[:, K0] = K0 + 2
    for b in range(B):
        for i in range(P):
            x[b, K0 + i, K0 + i] = 1
            x[b, K0 + i, K0:K0 + i] = rng.normal(0, 0.2, i)
    args = {'LU': _aligned(x, 'float32'), 'PIVOTS': _aligned(piv, 'int32')}
    meta = {'K0': K0, 'M': D, 'N': D, 'K': K, 'PANEL': P, 'BLOCK_B': 4, 'BLOCK_N': 4}
    grid = ((D - K0 - P + 3) // 4, B)
    outputs = ('LU',)
    return _case(_lu_factor_swap_right_and_solve_kernel, grid, args, meta, ('LU', 'PIVOTS'), outputs, ref(args, meta), shape, 'torch.float32', seed, {'complete_launch_plan': True, 'formula': 'apply panel pivots to all trailing columns, then forward-solve the panel rows'})

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
