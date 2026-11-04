"""One-JIT standalone Triton compiler test case."""

COPIED_FROM = {'repo': 'ops-pool/liger', 'note': 'validated case layer intact; lottery 20261019'}
OPERATOR = {"name": "hidden/layer_norm_forward_tiled", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["norm"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def _layer_norm_forward_tiled(Y_ptr, Y_row_stride, X_ptr, X_row_stride, W_ptr, B_ptr, Mean_ptr, Mean_row_stride, RSTD_ptr, RSTD_row_stride, n_rows: tl.constexpr, n_cols: tl.constexpr, eps: tl.constexpr, BLOCK_SIZE: tl.constexpr):
    """Fallback forward kernel that tiles columns when a full row does not fit UB."""
    pid = tl.program_id(0)
    num_progs = tl.num_programs(0)
    num_col_blocks = tl.cdiv(n_cols, BLOCK_SIZE)
    offsets = tl.arange(0, BLOCK_SIZE)
    n_cols_inv = 1.0 / n_cols
    for row_idx in tl.range(pid, n_rows, num_progs):
        X_row_ptr = X_ptr + row_idx * X_row_stride
        Y_row_ptr = Y_ptr + row_idx * Y_row_stride
        Mean_row_ptr = Mean_ptr + row_idx * Mean_row_stride
        RSTD_row_ptr = RSTD_ptr + row_idx * RSTD_row_stride
        row_sum = 0.0
        for col_block_idx in range(num_col_blocks):
            col_offsets = col_block_idx * BLOCK_SIZE + offsets
            mask = col_offsets < n_cols
            X_block = tl.load(X_row_ptr + col_offsets, mask=mask, other=0.0).to(tl.float32)
            row_sum += tl.sum(X_block)
        mean = row_sum * n_cols_inv
        var_sum = 0.0
        for col_block_idx in range(num_col_blocks):
            col_offsets = col_block_idx * BLOCK_SIZE + offsets
            mask = col_offsets < n_cols
            X_block = tl.load(X_row_ptr + col_offsets, mask=mask, other=0.0).to(tl.float32)
            x_hat = X_block - mean
            var_sum += tl.sum(tl.where(mask, x_hat * x_hat, 0.0))
        rstd = tl.rsqrt(var_sum * n_cols_inv + eps)
        tl.store(Mean_row_ptr, mean)
        tl.store(RSTD_row_ptr, rstd)
        for col_block_idx in range(num_col_blocks):
            col_offsets = col_block_idx * BLOCK_SIZE + offsets
            mask = col_offsets < n_cols
            X_block = tl.load(X_row_ptr + col_offsets, mask=mask, other=0.0).to(tl.float32)
            W_block = tl.load(W_ptr + col_offsets, mask=mask, other=0.0).to(tl.float32)
            B_block = tl.load(B_ptr + col_offsets, mask=mask, other=0.0).to(tl.float32)
            Y_f32 = (X_block - mean) * rstd * W_block + B_block
            tl.store(Y_row_ptr + col_offsets, Y_f32.to(X_block.dtype), mask=mask)
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
SHAPES=((3, 17), (31, 17));DTYPES=('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 R,C=meta["n_rows"],meta["n_cols"];x=args["X_ptr"].astype(np.float64).reshape(R,C);mean=x.mean(1);rstd=1/np.sqrt(np.mean((x-mean[:,None])**2,1)+meta["eps"]);y=(x-mean[:,None])*rstd[:,None]*args["W_ptr"]+args["B_ptr"];return {"Y_ptr":y.reshape(-1).astype(args["Y_ptr"].dtype),"Mean_ptr":mean.astype(args["Mean_ptr"].dtype),"RSTD_ptr":rstd.astype(args["RSTD_ptr"].dtype)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 R,C=map(int,shape);rng=fast_rng(seed);args={"Y_ptr":_aligned(np.full(R*C,-7.)),"Y_row_stride":C,"X_ptr":_aligned(rng.normal(0,.7,(R,C))),"X_row_stride":C,"W_ptr":_aligned(rng.uniform(.7,1.3,C)),"B_ptr":_aligned(rng.normal(0,.1,C)),"Mean_ptr":_aligned(np.full(R,-7.)),"Mean_row_stride":1,"RSTD_ptr":_aligned(np.full(R,-7.)),"RSTD_row_stride":1};meta={"n_rows":R,"n_cols":C,"eps":1e-5,"BLOCK_SIZE":64};return _case(_layer_norm_forward_tiled,(R,),args,meta,("X_ptr","W_ptr","B_ptr"),("Y_ptr","Mean_ptr","RSTD_ptr"),ref(args,meta),shape,"torch.float32",seed,{"grid_formula":"(rows,)","formula":"layer-norm affine, tiled columns"})

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
