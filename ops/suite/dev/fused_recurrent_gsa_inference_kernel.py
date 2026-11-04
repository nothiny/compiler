"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/fused_recurrent_gsa_inference_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["fla"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def fused_recurrent_gsa_inference_kernel(q, k, v, s, g, o, hk0, hv0, hkt, hvt, scale, K: tl.constexpr, V: tl.constexpr, M: tl.constexpr, BK: tl.constexpr, BV: tl.constexpr, NG: tl.constexpr, PAD_M: tl.constexpr):
    i_bh = tl.program_id(0).to(tl.int64)
    i_bg = i_bh // NG
    b_s = tl.load(s + i_bg * M + tl.arange(0, PAD_M), mask=tl.arange(0, PAD_M) < M, other=0.0).to(tl.float32)
    b_g = tl.load(g + i_bg * M + tl.arange(0, PAD_M), mask=tl.arange(0, PAD_M) < M, other=0.0).to(tl.float32)
    _inl_1_exp_x = b_g
    _inl_1_exp_result = tl.exp(_inl_1_exp_x.to(tl.float32))
    b_g = _inl_1_exp_result
    b_ok = tl.zeros([PAD_M], dtype=tl.float32)
    for i_k in range(tl.cdiv(K, BK)):
        o_k = i_k * BK + tl.arange(0, BK)
        p_hk0 = hk0 + i_bg * K * M + o_k[None, :] * M + tl.arange(0, PAD_M)[:, None]
        mask_k = o_k < K
        mask_hk = (tl.arange(0, PAD_M) < M)[:, None] & mask_k[None, :]
        b_hk = tl.load(p_hk0, mask=mask_hk, other=0.0).to(tl.float32)
        b_q = tl.load(q + i_bh * K + o_k, mask=mask_k, other=0.0).to(tl.float32) * scale
        b_k = tl.load(k + i_bg * K + o_k, mask=mask_k, other=0.0).to(tl.float32)
        b_hk = b_hk * b_g[:, None] + b_k[None, :] * b_s[:, None]
        b_ok += tl.sum(b_hk * b_q[None, :], axis=1)
        if i_bh % NG == 0:
            p_hkt = hkt + i_bg * K * M + o_k[None, :] * M + tl.arange(0, PAD_M)[:, None]
            tl.store(p_hkt, b_hk.to(p_hkt.dtype.element_ty), mask=mask_hk)
    b_q = tl.where(tl.arange(0, PAD_M) < M, b_ok, float('-inf'))
    _m = tl.max(b_q, 0)
    _e = tl.exp(b_q - _m)
    b_qv = _e / tl.sum(_e, 0)
    for i_v in range(tl.cdiv(V, BV)):
        o_v = i_v * BV + tl.arange(0, BV)
        p_hv0 = hv0 + i_bg * M * V + tl.arange(0, PAD_M)[None, :] * V + o_v[:, None]
        mask_v = o_v < V
        mask_hv = mask_v[:, None] & (tl.arange(0, PAD_M) < M)[None, :]
        b_hv = tl.load(p_hv0, mask=mask_hv, other=0).to(tl.float32)
        b_v = tl.load(v + i_bg * V + o_v, mask=mask_v, other=0).to(tl.float32)
        b_hv = b_hv * b_g[None, :] + b_s[None, :] * b_v[:, None]
        b_ov = tl.sum(b_hv * b_qv[None, :], axis=1)
        tl.store(o + i_bh * V + o_v, b_ov.to(o.dtype.element_ty), mask=mask_v)
        if i_bh % NG == 0:
            p_hvt = hvt + i_bg * M * V + tl.arange(0, PAD_M)[None, :] * V + o_v[:, None]
            tl.store(p_hvt, b_hv.to(p_hvt.dtype.element_ty), mask=mask_hv)
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
SHAPES=((4,3,7,9,5),(6,4,11,13,7));DTYPES=('float32', 'float16', 'bfloat16')
def ref(args,meta):
 import numpy as np
 BG,NG,K,V,M=args["k"].shape[0],meta["NG"],meta["K"],meta["V"],meta["M"];gate=np.exp(args["g"]);hk=args["hk0"].reshape(BG,K,M)*gate[:,None,:]+args["k"][:,:,None]*args["s"][:,None,:];hv=args["hv0"].reshape(BG,M,V)*gate[:,:,None]+args["s"][:,:,None]*args["v"][:,None,:];out=np.zeros((BG*NG,V),np.float32)
 for i in range(BG*NG):
  bg=i//NG;logits=(args["q"][i]*np.float32(args["scale"]))@hk[bg];prob=np.exp(logits-np.max(logits));prob/=np.sum(prob);out[i]=prob@hv[bg]
 return {"o":out.reshape(-1),"hkt":hk.reshape(-1),"hvt":hv.reshape(-1)}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    del dtype
    import numpy as np
    (BG, NG, K, V, M) = (int(x) for x in shape)
    rng = fast_rng(seed)
    args = {'q': _aligned(rng.normal(0, 0.2, (BG * NG, K))), 'k': _aligned(rng.normal(0, 0.2, (BG, K))), 'v': _aligned(rng.normal(0, 0.2, (BG, V))), 's': _aligned(rng.normal(0, 0.2, (BG, M))), 'g': _aligned(rng.uniform(-0.3, -0.02, (BG, M))), 'o': _aligned(np.full(BG * NG * V, -7.0)), 'hk0': _aligned(rng.normal(0, 0.1, (BG, K, M))), 'hv0': _aligned(rng.normal(0, 0.1, (BG, M, V))), 'hkt': _aligned(np.full(BG * K * M, -7.0)), 'hvt': _aligned(np.full(BG * M * V, -7.0)), 'scale': K ** (-0.5)}
    meta = {'K': K, 'V': V, 'M': M, 'BK': 1 << (int(1 << (int(K) - 1).bit_length()) - 1).bit_length(), 'BV': 1 << (int(1 << (int(V) - 1).bit_length()) - 1).bit_length(), 'NG': NG}
    grid = (BG * NG,)
    outputs = ('o', 'hkt', 'hvt')
    return _case(fused_recurrent_gsa_inference_kernel, grid, args, meta, ('q', 'k', 'v', 's', 'g', 'hk0', 'hv0'), outputs, ref(args, meta), shape, 'torch.float32', seed, {'grid_formula': '(BG*NG,)', 'outputs': outputs})

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
    case["meta"]["PAD_M"] = 1 << (int(case["meta"]["M"]) - 1).bit_length()
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
