"""One-JIT standalone Triton compiler test case."""

COPIED_FROM = {'repo': 'ops-pool/flaggems', 'note': 'validated case layer intact; lottery 20261019'}
OPERATOR = {"name": "hidden/complex_svd_project_u_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def _complex_svd_project_u_kernel(A_RI, V_RI, S, U_RI, M: tl.constexpr, N: tl.constexpr, K: tl.constexpr, BLOCK_SIZE: tl.constexpr):
    batch = tl.program_id(0)
    offsets = tl.arange(0, BLOCK_SIZE)
    mask = offsets < M * K
    row = offsets // K
    col = offsets % K
    acc_r = tl.zeros((BLOCK_SIZE,), dtype=tl.float32)
    acc_i = tl.zeros((BLOCK_SIZE,), dtype=tl.float32)
    for j in tl.static_range(0, N):
        a_base = A_RI + batch * M * N * 2 + (row * N + j) * 2
        v_base = V_RI + batch * N * K * 2 + (j * K + col) * 2
        ar = tl.load(a_base, mask=mask, other=0.0)
        ai = tl.load(a_base + 1, mask=mask, other=0.0)
        vr = tl.load(v_base, mask=mask, other=0.0)
        vi = tl.load(v_base + 1, mask=mask, other=0.0)
        acc_r += ar * vr - ai * vi
        acc_i += ar * vi + ai * vr
    s = tl.load(S + batch * K + col, mask=mask, other=1.0)
    inv_s = tl.where(s > 1e-20, 1.0 / s, 0.0)
    out_base = U_RI + batch * M * K * 2 + offsets * 2
    tl.store(out_base, acc_r * inv_s, mask=mask)
    tl.store(out_base + 1, acc_i * inv_s, mask=mask)
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
SHAPES = ((17,), (4, 6, 5, 4));DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 M=int(meta["M"]);N=int(meta["N"]);K=int(meta["K"]);a0=np.asarray(args["A_RI"],np.float32).reshape(-1,M,N,2);v0=np.asarray(args["V_RI"],np.float32).reshape(-1,N,K,2);s=np.asarray(args["S"],np.float32).reshape(-1,K);a=a0[...,0]+1j*a0[...,1];v=v0[...,0]+1j*v0[...,1];inv=np.zeros_like(s);np.divide(1,s,out=inv,where=s>1e-20);u=(a@v)*inv[:,None,:];return {"U_RI":np.stack((u.real,u.imag),axis=-1).astype(np.float32).reshape(-1)}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    if len(shape) > 1 and tuple(shape) not in SHAPES:
        raise ValueError('unsupported explicit shape configuration')
    del dtype
    import numpy as np
    N = int(shape[0])
    rng = fast_rng(seed)
    B = int(shape[0]) if len(shape) > 1 else 3
    M = int(shape[1]) if len(shape) > 1 else 6
    C = int(shape[2]) if len(shape) > 1 else 5
    K = int(shape[3]) if len(shape) > 1 else 4
    a = rng.normal(0, 0.3, (B, M, C, 2)).astype(np.float32)
    v = rng.normal(0, 0.3, (B, C, K, 2)).astype(np.float32)
    s = np.abs(rng.normal(1, 0.3, (B, K))).astype(np.float32)
    s[:, 1] = 0
    args = {'A_RI': _aligned(a, 'float32'), 'V_RI': _aligned(v, 'float32'), 'S': _aligned(s, 'float32'), 'U_RI': _aligned(np.full(B * M * K * 2, -7), 'float32')}
    meta = {'M': M, 'N': C, 'K': K, 'BLOCK_SIZE': 32}
    grid = (B,)
    outputs = ('U_RI',)
    return _case(_complex_svd_project_u_kernel, grid, args, meta, ('A_RI', 'V_RI', 'S'), outputs, ref(args, meta), shape, 'torch.float32', seed, {'complete_launch_plan': True, 'formula': 'complex A-times-V projection divided by singular values with zero-sigma columns cleared'})

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
