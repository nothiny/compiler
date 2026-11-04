"""fused_recurrent_rwkv6: bench 算子(原始 tritonbench 实现),自 tritonbench 收入 hard 组。
模式: creation.arange、creation.zeros、memory.load、math.exp、memory.store、reduce.sum。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""

OPERATOR = {"name": "hard/fused_recurrent_rwkv6", "group": "hard", "channel": "local", "execution": "triton_kernel", "verification": "correctness", "tags": ["creation.arange", "creation.zeros", "memory.load", "math.exp", "memory.store", "reduce.sum", "control.for_range", "args.runtime_scalar"]}
COPIED_FROM = {"repo": "tritonbench @ ops", "path": "tritonbench/fused_recurrent_rwkv6.py", "validated": True}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def rwkv6_kernel(r_ptr, k_ptr, v_ptr, w_ptr, u_ptr, o_ptr, T, scale,
                 HEAD_DIM: tl.constexpr, BLOCK_V: tl.constexpr):
    off_bh = tl.program_id(0)
    offs_d = tl.arange(0, HEAD_DIM)
    offs_v = tl.arange(0, BLOCK_V)
    state = tl.zeros([HEAD_DIM, BLOCK_V], dtype=tl.float32)
    for t in range(T):
        base = (off_bh * T + t)
        r = tl.load(r_ptr + base * HEAD_DIM + offs_d)
        k = tl.load(k_ptr + base * HEAD_DIM + offs_d)
        v = tl.load(v_ptr + base * BLOCK_V + offs_v)
        w = tl.load(w_ptr + base * HEAD_DIM + offs_d)
        u = tl.load(u_ptr + base * HEAD_DIM + offs_d)
        decay = tl.exp(-tl.exp(w))
        o = tl.sum(r[:, None] * state, axis=0) + tl.sum(r * k * u, axis=0) * v
        state = state * decay[:, None] + k[:, None] * v[None, :]
        tl.store(o_ptr + base * BLOCK_V + offs_v, o * scale)


# ------------------------------------------------------------------ ② case 层
DTYPES = ('float32',)

SHAPES = ((2, 2, 16, 32, 32), (2, 2, 16, 64, 32), (1, 2, 32, 32, 32))

def ref(args, meta):
    r = np.asarray(args["r_ptr"], dtype=np.float64)
    k = np.asarray(args["k_ptr"], dtype=np.float64)
    v = np.asarray(args["v_ptr"], dtype=np.float64)
    w = np.asarray(args["w_ptr"], dtype=np.float64)
    u = np.asarray(args["u_ptr"], dtype=np.float64)
    scale = float(args["scale"])
    b, h, t, d = r.shape
    dv = v.shape[-1]
    out = np.zeros((b, h, t, dv))
    state = np.zeros((b, h, d, dv))
    for i in range(t):
        decay = np.exp(-np.exp(w[:, :, i]))
        o = np.einsum("bhd,bhdv->bhv", r[:, :, i], state)
        bonus = np.einsum("bhd,bhd,bhd->bh", r[:, :, i], k[:, :, i], u[:, :, i])[:, :, None] * v[:, :, i]
        out[:, :, i] = (o + bonus) * scale
        state = state * decay[:, :, :, None] + k[:, :, i, :, None] * v[:, :, i, None, :]
    return {"o_ptr": out.astype(np.asarray(args["o_ptr"]).dtype)}

def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    b, h, t, d, dv = (int(x) for x in shape)
    from case_utils import fast_rng
    rng = fast_rng(seed)
    args = {"r_ptr": rng.standard_normal((b, h, t, d)).astype(dtype),
            "k_ptr": rng.standard_normal((b, h, t, d)).astype(dtype),
            "v_ptr": rng.standard_normal((b, h, t, dv)).astype(dtype),
            "w_ptr": rng.standard_normal((b, h, t, d)).astype(dtype),
            "u_ptr": rng.standard_normal((b, h, t, d)).astype(dtype),
            "o_ptr": np.zeros((b, h, t, dv), dtype=dtype), "T": np.int32(t),
            "scale": np.float32(1.0 / np.sqrt(d))}
    meta = {"HEAD_DIM": d, "BLOCK_V": dv}
    return {"args": args, "meta": meta, "grid": (b * h,),
            "outputs": ("o_ptr",), "expected": ref(args, meta)}

def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, rwkv6_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)

ORACLE_KIND = "numpy_reference"

INDEPENDENT_ORACLE = True

EXECUTION_KIND = "triton_kernel"

VERIFICATION_KIND = "correctness"

OPERATOR_NAME = "G/" + __file__.rsplit("/", 1)[-1]

OPERATOR_FILE = __file__


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float32'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float32': 'float32'}


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
