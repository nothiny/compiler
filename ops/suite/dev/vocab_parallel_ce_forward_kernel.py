"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/vocab_parallel_ce_forward_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def liger_vocab_parallel_ce_forward_kernel(X_ptr, X_stride, EXP_ptr, EXP_stride, logits_max_ptr, Y_ptr, pred_ptr, sum_exp_ptr, vocab_start, n_cols, ignore_index, BLOCK_SIZE: tl.constexpr):
    """Per-token forward stats. One program per row.

    All per-token bookkeeping (off-rank check, ignore-index check, shift by global
    max) happens here so the Python wrapper doesn't have to allocate a target_mask
    tensor or a shifted-logits buffer.
    """
    program_id = tl.program_id(0).to(tl.int64)
    X_ptr += program_id * X_stride
    EXP_ptr += program_id * EXP_stride
    y_global = tl.load(Y_ptr + program_id)
    m = tl.load(logits_max_ptr + program_id).cast(tl.float32)
    is_ignored = y_global == ignore_index
    target_off_rank = (y_global < vocab_start) | (y_global >= vocab_start + n_cols)
    y_local = y_global - vocab_start
    if is_ignored or target_off_rank:
        pred_local = 0.0
    else:
        pred_local = tl.load(X_ptr + y_local).cast(tl.float32) - m
    sum_exp = 0.0
    for i in range(0, n_cols, BLOCK_SIZE):
        X_offsets = i + tl.arange(0, BLOCK_SIZE)
        col_mask = X_offsets < n_cols
        X_block = tl.load(X_ptr + X_offsets, mask=col_mask, other=0.0).cast(tl.float32)
        exp_block = tl.exp(X_block - m)
        exp_block = tl.where(col_mask, exp_block, 0.0)
        sum_exp += tl.sum(exp_block)
        tl.store(EXP_ptr + X_offsets, exp_block, mask=col_mask)
    tl.store(pred_ptr + program_id, pred_local)
    tl.store(sum_exp_ptr + program_id, sum_exp)
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
SHAPES=((7,17),(11,67));DTYPES=('float32', 'float16', 'bfloat16')
def ref(args,meta):
 import numpy as np
 R,C=args["Y_ptr"].size,int(args["n_cols"]);x=args["X_ptr"].reshape(R,C);m=args["logits_max_ptr"];ex=np.exp(x-m[:,None]);y=args["Y_ptr"].astype(np.int64);local=y-int(args["vocab_start"]);valid=(y!=int(args["ignore_index"]))&(local>=0)&(local<C);pred=np.zeros(R,np.float32);pred[valid]=x[np.arange(R)[valid],local[valid]]-m[valid];return {"EXP_ptr":ex.reshape(-1),"pred_ptr":pred,"sum_exp_ptr":ex.sum(1)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 R,C=map(int,shape);rng=fast_rng(seed);x=rng.normal(0,.8,(R,C)).astype(np.float32);start=10;y=start+(np.arange(R)%C);y[0]=-100
 if R>2:y[1]=start+C+3
 args={"X_ptr":_aligned(x),"X_stride":C,"EXP_ptr":_aligned(np.full(R*C,-7.)),"EXP_stride":C,"logits_max_ptr":_aligned(x.max(1)),"Y_ptr":_aligned(y,"int64"),"pred_ptr":_aligned(np.full(R,-7.)),"sum_exp_ptr":_aligned(np.full(R,-7.)),"vocab_start":start,"n_cols":C,"ignore_index":-100};meta={"BLOCK_SIZE":64};outputs=("EXP_ptr","pred_ptr","sum_exp_ptr");return _case(liger_vocab_parallel_ce_forward_kernel,(R,),args,meta,("X_ptr","logits_max_ptr","Y_ptr"),outputs,ref(args,meta),shape,"torch.float32",seed,{"grid_formula":"(rows,)","formula":"local-vocab exp, selected shifted logit, exp sum"})

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
