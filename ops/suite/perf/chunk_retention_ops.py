"""chunk_retention_ops: fla(memory 类)。
bench 稳态配置见 bench/workload.json(声明 shape [2, 2, 16, 32, 32],验证 shape [8, 2, 16, 32, 32]);正确性 shape 见下方 SHAPES。
模式: creation.arange、creation.zeros、memory.load、memory.store、reduce.sum、control.for_range。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""

OPERATOR = {'name': 'bench/chunk_retention_ops', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'creation.zeros', 'memory.load', 'memory.store', 'reduce.sum', 'control.for_range', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/chunk_retention_ops.py', 'sha256': 'd16908d984947acc3eaf7f17ba5148eb2f255277bd9fb1d173db6f6f28cff1e5'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def chunk_retention_ops_kernel(
    q_ptr, k_ptr, v_ptr, g_ptr, o_ptr,
    B, H, T, scale,
    stride_qb, stride_qh, stride_qt, stride_qd,
    stride_kb, stride_kh, stride_kt, stride_kd,
    stride_vb, stride_vh, stride_vt, stride_vd,
    stride_gb, stride_gh, stride_gt,
    stride_ob, stride_oh, stride_ot, stride_od,
    HEAD_DIM: tl.constexpr, BLOCK_V: tl.constexpr,
):
    off_bh = tl.program_id(0)
    b = off_bh // H
    h = off_bh % H
    offs_d = tl.arange(0, HEAD_DIM)
    offs_v = tl.arange(0, BLOCK_V)
    state = tl.zeros([HEAD_DIM, BLOCK_V], dtype=tl.float32)
    for t in range(T):
        q = tl.load(q_ptr + b*stride_qb + h*stride_qh + t*stride_qt + offs_d*stride_qd)
        k = tl.load(k_ptr + b*stride_kb + h*stride_kh + t*stride_kt + offs_d*stride_kd)
        v = tl.load(v_ptr + b*stride_vb + h*stride_vh + t*stride_vt + offs_v*stride_vd)
        g = tl.load(g_ptr + b*stride_gb + h*stride_gh + t*stride_gt)
        state = state * g + k[:, None] * v[None, :]
        o = tl.sum(q[:, None] * state, axis=0) * scale
        tl.store(o_ptr + b*stride_ob + h*stride_oh + t*stride_ot + offs_v*stride_od, o)


# ------------------------------------------------------------------ ② case 层
DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((2, 2, 16, 32, 32), (4, 4, 32, 64, 64), (1, 1, 8, 16, 16))

def ref(args, meta):
    q = np.asarray(args["q_ptr"], dtype=np.float64)
    k = np.asarray(args["k_ptr"], dtype=np.float64)
    v = np.asarray(args["v_ptr"], dtype=np.float64)
    g = np.asarray(args["g_ptr"], dtype=np.float64)
    scale = float(args["scale"])
    b, h, t, d = q.shape
    dv = v.shape[-1]
    out = np.zeros((b, h, t, dv), dtype=np.float64)
    state = np.zeros((d, dv), dtype=np.float64)
    for i in range(t):
        state = state * g[:, :, i][:, :, None, None] + k[:, :, i, :, None] * v[:, :, i, None, :]
        out[:, :, i, :] = np.einsum("bhd,bhdv->bhv", q[:, :, i, :], state) * scale
    return {"o_ptr": out.astype(np.asarray(args["o_ptr"]).dtype)}

def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    b, h, t, d, dv = (int(x) for x in shape)
    from case_utils import fast_rng
    rng = fast_rng(seed)
    q = (rng.standard_normal((b, h, t, d)) * 0.5).astype(dtype)
    k = (rng.standard_normal((b, h, t, d)) * 0.5).astype(dtype)
    v = (rng.standard_normal((b, h, t, dv)) * 0.5).astype(dtype)
    g = (rng.uniform(0.5, 1.0, (b, h, t))).astype(dtype)
    args = {"q_ptr": q, "k_ptr": k, "v_ptr": v, "g_ptr": g,
            "o_ptr": np.zeros((b, h, t, dv), dtype=dtype),
            "B": np.int32(b), "H": np.int32(h), "T": np.int32(t),
            "scale": np.float32(1.0 / np.sqrt(d)),
            "stride_qb": np.int32(h*t*d), "stride_qh": np.int32(t*d),
            "stride_qt": np.int32(d), "stride_qd": np.int32(1),
            "stride_kb": np.int32(h*t*d), "stride_kh": np.int32(t*d),
            "stride_kt": np.int32(d), "stride_kd": np.int32(1),
            "stride_vb": np.int32(h*t*dv), "stride_vh": np.int32(t*dv),
            "stride_vt": np.int32(dv), "stride_vd": np.int32(1),
            "stride_gb": np.int32(h*t), "stride_gh": np.int32(t), "stride_gt": np.int32(1),
            "stride_ob": np.int32(h*t*dv), "stride_oh": np.int32(t*dv),
            "stride_ot": np.int32(dv), "stride_od": np.int32(1)}
    meta = {"HEAD_DIM": d, "BLOCK_V": dv}
    grid = (b * h,)
    return {"args": args, "meta": meta, "grid": grid,
            "outputs": ("o_ptr",), "expected": ref(args, meta)}

def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, chunk_retention_ops_kernel, DTYPES,
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
