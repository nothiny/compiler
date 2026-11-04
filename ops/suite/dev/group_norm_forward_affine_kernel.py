"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/group_norm_forward_affine_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["norm"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def _group_norm_forward_affine_kernel(Y_ptr, X_ptr, Mean_ptr, RSTD_ptr, W_ptr, B_ptr, batch_size, num_groups, hidden_size: tl.constexpr, channels_per_group: tl.constexpr, channel_blocks, BLOCK_SIZE_H: tl.constexpr, BLOCK_SIZE_CH: tl.constexpr, BLOCK_BATCH: tl.constexpr):
    hidden_size_per_channel: tl.constexpr = hidden_size // channels_per_group
    pid_tile = tl.program_id(0)
    pid_batch_block = tl.program_id(1)
    pid_group = pid_tile // channel_blocks
    pid_channel_block = pid_tile - pid_group * channel_blocks
    batch_offsets = pid_batch_block * BLOCK_BATCH + tl.arange(0, BLOCK_BATCH)
    batch_mask = batch_offsets < batch_size
    task_offsets = batch_offsets * num_groups + pid_group
    mean = tl.load(Mean_ptr + task_offsets, mask=batch_mask, other=0.0).to(tl.float32)
    rstd = tl.load(RSTD_ptr + task_offsets, mask=batch_mask, other=0.0).to(tl.float32)
    ch_offsets = pid_channel_block * BLOCK_SIZE_CH + tl.arange(0, BLOCK_SIZE_CH)
    ch_mask = ch_offsets < channels_per_group
    group_ch_offsets = pid_group * channels_per_group + ch_offsets
    W_vals = tl.load(W_ptr + group_ch_offsets, mask=ch_mask, other=1.0).to(tl.float32)
    B_vals = tl.load(B_ptr + group_ch_offsets, mask=ch_mask, other=0.0).to(tl.float32)
    h_offsets = tl.arange(0, BLOCK_SIZE_H)
    for start in tl.range(0, hidden_size_per_channel, BLOCK_SIZE_H):
        idx = start + h_offsets
        h_mask = idx < hidden_size_per_channel
        mask = batch_mask[:, None, None] & ch_mask[None, :, None] & h_mask[None, None, :]
        ptrs = task_offsets[:, None, None] * hidden_size + ch_offsets[None, :, None] * hidden_size_per_channel + idx[None, None, :]
        X_vals = tl.load(X_ptr + ptrs, mask=mask, other=0.0).to(tl.float32)
        Y_vals = (X_vals - mean[:, None, None]) * rstd[:, None, None]
        Y_vals = Y_vals * W_vals[None, :, None] + B_vals[None, :, None]
        tl.store(Y_ptr + ptrs, Y_vals.to(Y_ptr.dtype.element_ty), mask=mask)
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
SHAPES=((3,2,4,5),(5,3,2,7));DTYPES=('float32', 'float16', 'bfloat16')
def ref(args,meta):
 import numpy as np
 B,G=int(args["batch_size"]),int(args["num_groups"]);C=meta["channels_per_group"];S=meta["hidden_size"]//C;x=args["X_ptr"].reshape(B,G,C,S);m=args["Mean_ptr"].reshape(B,G);r=args["RSTD_ptr"].reshape(B,G);w=args["W_ptr"].reshape(G,C);bb=args["B_ptr"].reshape(G,C);return {"Y_ptr":(((x-m[:,:,None,None])*r[:,:,None,None])*w[None,:,:,None]+bb[None,:,:,None]).reshape(-1)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 B,G,C,S=map(int,shape);D=C*S;rng=fast_rng(seed);x=rng.normal(0,.7,(B,G,C,S)).astype(np.float32);m=x.reshape(B,G,D).mean(2);r=1/np.sqrt(x.reshape(B,G,D).var(2)+1e-5);args={"Y_ptr":_aligned(np.full(B*G*D,-7.)),"X_ptr":_aligned(x),"Mean_ptr":_aligned(m),"RSTD_ptr":_aligned(r),"W_ptr":_aligned(rng.uniform(.7,1.3,(G,C))),"B_ptr":_aligned(rng.normal(0,.1,(G,C))),"batch_size":B,"num_groups":G,"channel_blocks":(C+1)//2};meta={"hidden_size":D,"channels_per_group":C,"BLOCK_SIZE_H":8,"BLOCK_SIZE_CH":2,"BLOCK_BATCH":2};grid=(G*args["channel_blocks"],(B+1)//2);return _case(_group_norm_forward_affine_kernel,grid,args,meta,("X_ptr","Mean_ptr","RSTD_ptr","W_ptr","B_ptr"),("Y_ptr",),ref(args,meta),shape,"torch.float32",seed,{"grid_formula":"(groups*channel_blocks,ceil_div(batch,BLOCK_BATCH))","formula":"group normalization affine stage"})

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
