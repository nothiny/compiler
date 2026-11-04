"""naive_attn_decoding_kernel: 从 ~/ops 仓库复制(smoke @ ops),保留其已验证的 case 层。

模式: args.runtime_scalar、cast.to、control.for_range、control.if、control.loop_carried、creation.arange、creation.full、creation.where、creation.zeros、dtype.float32。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。循环上界来自运行时标量(不是 constexpr)。constexpr 参数: B, H, HQ, G, K, V, BS, BK, BV, USE_G, USE_SINK_BIAS。

文件只有两层:
  ① naive_attn_decoding_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/naive_attn_decoding_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'cast.to', 'control.for_range', 'control.if', 'control.loop_carried', 'creation.arange', 'creation.full', 'creation.where', 'creation.zeros', 'dtype.float32', 'dtype.int64', 'math.cdiv', 'math.exp', 'math.maximum', 'memory.load', 'memory.load.masked', 'memory.load.other', 'memory.store', 'memory.store.masked', 'reduce.max', 'reduce.sum.axis0', 'reduce.sum.axis1', 'tile.2d']}
COPIED_FROM = {'repo': 'smoke @ ops', 'note': 'validated case layer intact'}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def naive_attn_decoding_kernel(q, k, v, o, g_cumsum, sink_bias, scale, cu_seqlens, T, B: tl.constexpr, H: tl.constexpr, HQ: tl.constexpr, G: tl.constexpr, K: tl.constexpr, V: tl.constexpr, BS: tl.constexpr, BK: tl.constexpr, BV: tl.constexpr, USE_G: tl.constexpr, USE_SINK_BIAS: tl.constexpr):
    pid = tl.program_id(0)
    NV = tl.cdiv(V, BV)
    (i_v, i_bh) = (pid % NV, (pid // NV).to(tl.int64))
    (i_b, i_hq) = (i_bh // HQ, i_bh % HQ)
    i_h = i_hq // G
    (bos, eos) = (tl.load(cu_seqlens + i_b).to(tl.int64), tl.load(cu_seqlens + i_b + 1).to(tl.int64))
    T = eos - bos
    o_d = tl.arange(0, BK)
    o_v = i_v * BV + tl.arange(0, BV)
    p_q = q + i_bh * K + o_d
    p_o = o + i_bh * V + o_v
    b_q = tl.load(p_q, mask=o_d < K, other=0.0)
    b_q = (b_q * scale).to(b_q.dtype)
    b_o = tl.zeros([BV], dtype=tl.float32)
    b_m = tl.full([1], float('-inf'), dtype=tl.float32)
    b_acc = tl.zeros([1], dtype=tl.float32)
    if USE_G:
        p_g = g_cumsum + bos * HQ + i_hq + (T - 1) * HQ
        b_gq = tl.load(p_g, mask=T - 1 < T, other=0.0).to(tl.float32)
    else:
        b_gq = None
    if USE_SINK_BIAS:
        b_sink_bias = tl.load(sink_bias + i_hq).to(tl.float32)
    else:
        b_sink_bias = None
    for i_s in range(0, T, BS):
        o_k = (i_s + tl.arange(0, BS)).to(tl.int64)
        m_k = o_k < T
        p_k = k + (bos * H + i_h) * K + o_k[:, None] * (H * K) + o_d[None, :]
        p_v = v + (bos * H + i_h) * V + o_k[:, None] * (H * V) + o_v[None, :]
        b_k = tl.load(p_k, mask=m_k[:, None] & (o_d[None, :] < K), other=0.0)
        b_v = tl.load(p_v, mask=m_k[:, None] & (o_v[None, :] < V), other=0.0)
        b_s = tl.sum(b_q[None, :] * b_k, 1)
        b_s = tl.where(m_k, b_s, float('-inf'))
        if USE_G:
            p_gk = g_cumsum + bos * HQ + i_hq + o_k * HQ
            b_gk = tl.load(p_gk, mask=m_k, other=0.0).to(tl.float32)
            b_s += b_gq - b_gk
        (b_m, b_mp) = (tl.maximum(b_m, tl.max(b_s)), b_m)
        b_r = tl.exp((b_mp - b_m).to(tl.float32))
        b_p = tl.exp((b_s - b_m).to(tl.float32))
        b_acc = b_acc * b_r + tl.sum(b_p, 0)
        b_o = b_o * b_r + tl.sum(b_p[:, None] * b_v, 0)
        b_mp = b_m
    if USE_SINK_BIAS:
        b_m = tl.where(b_m == float('-inf'), 0.0, b_m)
        b_acc += tl.exp((b_sink_bias - b_m).to(tl.float32))
    b_o = b_o / b_acc
    tl.store(p_o, b_o.to(p_o.dtype.element_ty), mask=o_v < V)

# ------------------------------------------------------------------ ② case 层
# (shape,) 的角色:第一个是典型用法,其余是泛化/尾块/退化用例。
#   (2, 17, 4, 8, 16, 13)
#   (3, 33, 6, 12, 32, 65)
#   (4, 65, 8, 16, 64, 129)
#   (4, 17, 4, 8, 16, 13)
# DTYPES: float16, float32 —— 原始用途的 dtype 在前;非法域(例如本机 Triton 只吃 fp32 的exp/sqrt/erf/atomic)的算子只声明合法的那一种。

SUPPORT_STATUS = "supported"
VALIDATION_SCOPE = "full-launch-correctness"
SEED = 20260826
def _aligned(values, dtype, alignment=64):
    import numpy as np

    values = np.asarray(values, dtype=np.dtype(dtype))
    raw = np.empty(values.size * values.dtype.itemsize + alignment, dtype=np.uint8)
    start = -raw.ctypes.data % alignment
    result = raw[start : start + values.size * values.dtype.itemsize].view(values.dtype)
    result[...] = values.reshape(-1)
    return result.reshape(values.shape)
def _comparison(outputs, exact=False, rtol=0.0001, atol=0.0001, dtype=None):
    if not exact:
        _comparison_dtype_policy = str(dtype)
        if _comparison_dtype_policy == 'float32':
            (rtol, atol) = (0.0001, 0.0001)
        elif _comparison_dtype_policy == 'bfloat16':
            (rtol, atol) = (0.01, 0.01)
    return {name: {'profile': 'exact' if exact else 'elementwise-strict', 'comparator': 'array_equal' if exact else 'allclose', 'exact': bool(exact), 'rtol': 0.0 if exact else float(rtol), 'atol': 0.0 if exact else float(atol), 'equal_nan': not exact} for name in outputs}
def _layouts(args):
    import numpy as np

    return {
        name: {
            "shape": tuple(int(value) for value in np.asarray(array).shape),
            "strides": tuple(int(value // np.asarray(array).dtype.itemsize) for value in np.asarray(array).strides),
        }
        for name, array in args.items()
        if isinstance(array, np.ndarray)
    }

SHAPES = ((2, 17, 4, 8, 16, 13), (3, 33, 6, 12, 32, 65))
DTYPES = ('float16', 'float32', 'bfloat16')
FIXED_META = {"BS": 16, "BV": 32, "USE_G": True, "USE_SINK_BIAS": True}
LAUNCH_META = {"num_warps": 4, "num_stages": 1}
def ref(args, meta):
    import numpy as np
    batches, h, hq, kdim, vdim = int(meta["B"]), int(meta["H"]), int(meta["HQ"]), int(meta["K"]), int(meta["V"]); groups = int(meta["G"])
    ends = np.asarray(args["cu_seqlens"], dtype=np.int64); q = np.asarray(args["q"], dtype=np.float32).reshape(batches, hq, kdim)
    keys = np.asarray(args["k"], dtype=np.float32).reshape(int(ends[-1]), h, kdim); values = np.asarray(args["v"], dtype=np.float32).reshape(int(ends[-1]), h, vdim)
    gates = np.asarray(args["g_cumsum"], dtype=np.float32).reshape(int(ends[-1]), hq); sink = np.asarray(args["sink_bias"], dtype=np.float32); out = np.empty((batches, hq, vdim), dtype=np.float32)
    for batch in range(batches):
        start, end = int(ends[batch]), int(ends[batch + 1])
        for head_q in range(hq):
            scores = (keys[start:end, head_q // groups] @ (q[batch, head_q] * float(args["scale"]))) + gates[end - 1, head_q] - gates[start:end, head_q]
            maximum = max(float(scores.max()), float(sink[head_q])); weights = np.exp(scores - maximum)
            denominator = weights.sum() + np.exp(float(sink[head_q]) - maximum)
            out[batch, head_q] = weights @ values[start:end, head_q // groups] / denominator
    return {"o": out.reshape(-1).astype(np.asarray(args["o"]).dtype)}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    import numpy as np
    (batches, max_t, h, hq, kdim, vdim) = (int(value) for value in shape)
    dtype_name = str(dtype).rsplit('.', 1)[-1]
    if hq % h:
        raise ValueError('HQ must be divisible by H')
    lengths = np.asarray([max_t - 2 * batch for batch in range(batches)], dtype=np.int32)
    cu = np.concatenate(([0], np.cumsum(lengths))).astype(np.int32)
    total = int(cu[-1])
    from case_utils import fast_rng
    rng = fast_rng(seed)
    args = {'q': _aligned(rng.normal(0, 0.25, batches * hq * kdim), dtype_name), 'k': _aligned(rng.normal(0, 0.25, total * h * kdim), dtype_name), 'v': _aligned(rng.normal(0, 0.25, total * h * vdim), dtype_name), 'o': _aligned(np.full(batches * hq * vdim, -0.875), dtype_name), 'g_cumsum': _aligned(np.cumsum(rng.uniform(-0.1, 0.0, (total, hq)), axis=0), 'float32'), 'sink_bias': _aligned(rng.uniform(-0.5, 0.5, hq), 'float32'), 'scale': np.float32(kdim ** (-0.5)), 'cu_seqlens': _aligned(cu, 'int32'), 'T': total}
    meta = {**FIXED_META, 'B': batches, 'H': h, 'HQ': hq, 'G': hq // h, 'K': kdim, 'V': vdim, 'BK': 1 << (kdim - 1).bit_length()}
    grid = ((vdim + meta['BV'] - 1) // meta['BV'] * batches * hq,)
    outputs = ('o',)
    return {'kernel': naive_attn_decoding_kernel, 'grid': grid, 'args': args, 'meta': meta, 'launch_meta': dict(LAUNCH_META), 'inputs': ('q', 'k', 'v', 'g_cumsum', 'sink_bias', 'cu_seqlens'), 'outputs': outputs, 'expected': ref(args, meta), 'comparison': _comparison(outputs, rtol=0.03, atol=0.03, dtype=str(dtype)), 'pointer_dtypes': {'q': dtype_name, 'k': dtype_name, 'v': dtype_name, 'o': dtype_name, 'g_cumsum': 'float32', 'sink_bias': 'float32', 'cu_seqlens': 'int32'}, 'buffer_extents': {name: int(value.size) for (name, value) in args.items() if isinstance(value, np.ndarray)}, 'buffer_layouts': _layouts(args), 'alignment': 64, 'aliases': {}, 'seed': int(seed), 'shape': tuple(shape), 'dtype': str(dtype), 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'coverage': {'complete_logical_output': True, 'grid_formula': '(ceil_div(V,BV)*B*HQ,)', 'variable_lengths': tuple((int(x) for x in lengths)), 'features': ('gate', 'sink_bias', 'GQA')}}
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


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float32'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float16': 'float16', 'float32': 'float32'}


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
