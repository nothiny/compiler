"""One-JIT standalone Triton compiler test case."""

COPIED_FROM = {'repo': 'ops-pool/liger', 'note': 'validated case layer intact; lottery 20261019'}
OPERATOR = {"name": "hidden/group_norm_forward_stats_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["norm"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def _group_norm_forward_stats_kernel(X_ptr, Mean_ptr, RSTD_ptr, batch_size, num_groups, hidden_size: tl.constexpr, eps, BLOCK_SIZE_H: tl.constexpr, BLOCK_BATCH: tl.constexpr):
    pid_group = tl.program_id(0)
    pid_batch_block = tl.program_id(1)
    batch_offsets = pid_batch_block * BLOCK_BATCH + tl.arange(0, BLOCK_BATCH)
    batch_mask = batch_offsets < batch_size
    task_offsets = batch_offsets * num_groups + pid_group
    inv_hidden_size = 1.0 / hidden_size
    sum_acc = tl.zeros([BLOCK_BATCH], dtype=tl.float32)
    sum_sq_acc = tl.zeros([BLOCK_BATCH], dtype=tl.float32)
    h_offsets = tl.arange(0, BLOCK_SIZE_H)
    for start in tl.range(0, hidden_size, BLOCK_SIZE_H):
        idx = start + h_offsets
        h_mask = idx < hidden_size
        mask = batch_mask[:, None] & h_mask[None, :]
        ptrs = task_offsets[:, None] * hidden_size + idx[None, :]
        X_vals = tl.load(X_ptr + ptrs, mask=mask, other=0.0).to(tl.float32)
        sum_acc += tl.sum(X_vals, axis=1)
        sum_sq_acc += tl.sum(X_vals * X_vals, axis=1)
    mean = sum_acc * inv_hidden_size
    variance = tl.maximum(sum_sq_acc * inv_hidden_size - mean * mean, 0.0)
    rstd = tl.rsqrt(variance + eps)
    tl.store(Mean_ptr + task_offsets, mean, mask=batch_mask)
    tl.store(RSTD_ptr + task_offsets, rstd, mask=batch_mask)
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
SHAPES=((3, 2, 4, 5), (7, 2, 4, 5));DTYPES=('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 B,G=int(args["batch_size"]),int(args["num_groups"]);x=args["X_ptr"].reshape(B,G,meta["hidden_size"]);mean=x.mean(2);rstd=1/np.sqrt(np.maximum((x*x).mean(2)-mean*mean,0)+np.float32(args["eps"]));return {"Mean_ptr":mean.reshape(-1),"RSTD_ptr":rstd.reshape(-1)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 B,G,C,S=map(int,shape);D=C*S;rng=fast_rng(seed);args={"X_ptr":_aligned(rng.normal(0,.7,(B,G,D))),"Mean_ptr":_aligned(np.full(B*G,-7.)),"RSTD_ptr":_aligned(np.full(B*G,-7.)),"batch_size":B,"num_groups":G,"eps":1e-5};meta={"hidden_size":D,"BLOCK_SIZE_H":16,"BLOCK_BATCH":2};return _case(_group_norm_forward_stats_kernel,(G,(B+1)//2),args,meta,("X_ptr",),("Mean_ptr","RSTD_ptr"),ref(args,meta),shape,"torch.float32",seed,{"grid_formula":"(num_groups,ceil_div(batch,BLOCK_BATCH))","formula":"group mean and reciprocal std"})

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
