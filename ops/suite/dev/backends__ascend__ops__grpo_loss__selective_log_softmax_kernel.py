"""One-JIT standalone Triton compiler test case."""

COPIED_FROM = {'repo': 'ops-pool/liger', 'note': 'validated case layer intact; lottery 20261019'}
OPERATOR = {"name": "hidden/backends__ascend__ops__grpo_loss__selective_log_softmax_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["norm"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def _selective_log_softmax_kernel(LOGITS, INPUT_IDS, LOG_P, MASK, TEMPERATURE, stride_input_ids_b, L: tl.constexpr, N: tl.constexpr, BLOCK_N: tl.constexpr=4096):
    pid_b = tl.program_id(0)
    pid_l = tl.program_id(1)
    num_progs_l = tl.num_programs(1)
    batch_start = pid_b * L
    batch_end = batch_start + L
    start_token = batch_start + pid_l
    stride = num_progs_l
    inv_temp = 1.0 / TEMPERATURE
    for token_idx in tl.range(start_token, batch_end, stride):
        off_b = token_idx // L
        off_l = token_idx % L
        should_process = 1
        if MASK is not None:
            MASK_local = MASK + off_b * stride_input_ids_b + off_l
            not_skip = tl.load(MASK_local)
            should_process = not_skip
        if should_process != 0:
            LOGITS_local = LOGITS + off_b * (L + 1) * N + off_l * N
            INPUT_IDS_local = INPUT_IDS + off_b * stride_input_ids_b + off_l
            LOG_P_local = LOG_P + token_idx
            m_i = float('-inf')
            l_i = 0.0
            for start in tl.static_range(0, N, BLOCK_N):
                cols = start + tl.arange(0, BLOCK_N)
                cols_mask = cols < N
                logits = tl.load(LOGITS_local + cols, mask=cols_mask, other=float('-inf')).to(tl.float32) * inv_temp
                new_m_i = tl.maximum(m_i, tl.max(logits))
                alpha = tl.exp(m_i - new_m_i)
                l_i = l_i * alpha + tl.sum(tl.exp(logits - new_m_i))
                m_i = new_m_i
            lse = m_i + tl.log(l_i)
            ids = tl.load(INPUT_IDS_local)
            x = tl.load(LOGITS_local + ids).to(tl.float32) * inv_temp
            logp = x - lse
            tl.store(LOG_P_local, logp)
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
SHAPES=((2, 7, 17), (3, 7, 17));DTYPES=('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 B,L,N=args["INPUT_IDS"].shape[0],meta["L"],meta["N"];x=args["LOGITS"].reshape(B,L+1,N)[:,:L]/np.float32(args["TEMPERATURE"]);ids=args["INPUT_IDS"].reshape(B,L);mask=args["MASK"].reshape(B,L);mx=np.max(x,2);lse=mx+np.log(np.sum(np.exp(x-mx[:,:,None]),2));out=args["LOG_P"].reshape(B,L).copy();value=x[np.arange(B)[:,None],np.arange(L)[None,:],ids]-lse;out[mask!=0]=value[mask!=0];return {"LOG_P":out.reshape(-1)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 B,L,N=map(int,shape);rng=fast_rng(seed);args={"LOGITS":_aligned(rng.normal(0,.8,(B,L+1,N))),"INPUT_IDS":_aligned(rng.integers(0,N,(B,L)),"int32"),"LOG_P":_aligned(np.full(B*L,-7.)),"MASK":_aligned((np.arange(B*L).reshape(B,L)%4)!=0,"bool"),"TEMPERATURE":.8,"stride_input_ids_b":L};meta={"L":L,"N":N,"BLOCK_N":64};return _case(_selective_log_softmax_kernel,(B,L),args,meta,("LOGITS","INPUT_IDS","MASK"),("LOG_P",),ref(args,meta),shape,"torch.float32",seed,{"grid_formula":"(B,L)","formula":"grid-stride masked selected log-softmax"})

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
