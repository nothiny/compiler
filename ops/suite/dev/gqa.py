"""gqa: attention(compute 类)bench 算子,自 tritonbench 收入 hard 组。
bench 稳态配置见 ~/ops/bench/workload.json(声明 shape [2, 4, 2, 32, 32],验证 shape [2, 4, 2, 256, 64]);正确性 shape 见下方 SHAPES。
模式: creation.arange、memory.load.masked、creation.full、creation.zeros、memory.store.masked、creation.where。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""

OPERATOR = {"name": "hard/gqa", "group": "hard", "channel": "local", "execution": "triton_kernel", "verification": "correctness", "tags": ["creation.arange", "memory.load.masked", "creation.full", "creation.zeros", "memory.store.masked", "creation.where", "math.maximum", "math.exp"]}
COPIED_FROM = {"repo": "tritonbench @ ops", "path": "tritonbench/gqa.py", "validated": True}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def gqa_kernel(Q, K, V, Out,
               stride_qh, stride_qm, stride_qk, stride_kh, stride_kn, stride_kk,
               stride_vh, stride_vk, stride_vn, stride_oh, stride_om, stride_on,
               H_Q, H_KV, N_CTX, scale, GROUP: tl.constexpr,
               HEAD_DIM: tl.constexpr, BLOCK_N: tl.constexpr):
    pid_m = tl.program_id(0)
    off_hz = tl.program_id(1)
    off_z = off_hz // H_Q
    off_h = off_hz % H_Q
    off_hkv = off_h // GROUP
    qb = Q + off_z * H_Q * stride_qh + off_h * stride_qh
    kb = K + off_z * H_KV * stride_kh + off_hkv * stride_kh
    vb = V + off_z * H_KV * stride_vh + off_hkv * stride_vh
    ob = Out + off_z * H_Q * stride_oh + off_h * stride_oh
    offs_m = pid_m * BLOCK_N + tl.arange(0, BLOCK_N)
    offs_n = tl.arange(0, BLOCK_N)
    offs_d = tl.arange(0, HEAD_DIM)
    mmask = offs_m < N_CTX
    q = tl.load(qb + offs_m[:, None] * stride_qm + offs_d[None, :] * stride_qk,
                mask=mmask[:, None], other=0.0)
    m_i = tl.full([BLOCK_N], float("-inf"), tl.float32)
    l_i = tl.zeros([BLOCK_N], tl.float32)
    acc = tl.zeros([BLOCK_N, HEAD_DIM], tl.float32)
    for start_n in range(0, N_CTX, BLOCK_N):
        offs_nn = start_n + offs_n
        nmask = offs_nn < N_CTX
        k = tl.load(kb + offs_nn[:, None] * stride_kn + offs_d[None, :] * stride_kk,
                    mask=nmask[:, None], other=0.0)
        qk = tl.dot(q, tl.trans(k)) * scale
        qk = tl.where(nmask[None, :], qk, float("-inf"))
        m_ij = tl.maximum(m_i, tl.max(qk, axis=1))
        p = tl.exp(qk - m_ij[:, None])
        alpha = tl.exp(m_i - m_ij)
        l_i = l_i * alpha + tl.sum(p, axis=1)
        acc = acc * alpha[:, None]
        v = tl.load(vb + offs_nn[:, None] * stride_vk + offs_d[None, :] * stride_vn,
                    mask=nmask[:, None], other=0.0)
        acc += tl.dot(p, v)
        m_i = m_ij
    acc = acc / l_i[:, None]
    tl.store(ob + offs_m[:, None] * stride_om + offs_d[None, :] * stride_on, acc,
             mask=mmask[:, None])


# ------------------------------------------------------------------ ② case 层
DTYPES = ('float32',)

SHAPES = ((2, 4, 2, 32, 32), (2, 4, 2, 64, 32), (1, 4, 2, 64, 32))

def ref(args, meta):
    q = np.asarray(args["Q"], dtype=np.float64)
    k = np.asarray(args["K"], dtype=np.float64)
    v = np.asarray(args["V"], dtype=np.float64)
    scale = float(args["scale"])
    g = meta["GROUP"]
    z, hq, n, d = q.shape
    out = np.zeros_like(q)
    for zz in range(z):
        for hh in range(hq):
            kvh = hh // g
            s = np.einsum("id,jd->ij", q[zz, hh], k[zz, kvh]) * scale
            s = s - s.max(axis=-1, keepdims=True)
            p = np.exp(s)
            p = p / p.sum(axis=-1, keepdims=True)
            out[zz, hh] = p @ v[zz, kvh]
    return {"Out": out.astype(np.asarray(args["Out"]).dtype)}

def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    z, hq, hkv, n, d = (int(x) for x in shape)
    g = hq // hkv
    from case_utils import fast_rng
    rng = fast_rng(seed)
    args = {"Q": rng.standard_normal((z, hq, n, d)).astype(dtype),
            "K": rng.standard_normal((z, hkv, n, d)).astype(dtype),
            "V": rng.standard_normal((z, hkv, n, d)).astype(dtype),
            "Out": np.zeros((z, hq, n, d), dtype=dtype),
            "H_Q": np.int32(hq), "H_KV": np.int32(hkv), "N_CTX": np.int32(n),
            "scale": np.float32(1.0 / np.sqrt(d)),
            "stride_qh": np.int32(n * d), "stride_qm": np.int32(d), "stride_qk": np.int32(1),
            "stride_kh": np.int32(n * d), "stride_kn": np.int32(d), "stride_kk": np.int32(1),
            "stride_vh": np.int32(n * d), "stride_vk": np.int32(d), "stride_vn": np.int32(1),
            "stride_oh": np.int32(n * d), "stride_om": np.int32(d), "stride_on": np.int32(1)}
    meta = {"GROUP": g, "HEAD_DIM": d, "BLOCK_N": 32}
    grid = (triton.cdiv(n, 32), z * hq)
    expected = ref(args, meta)
    tol = {"comparator": "allclose", "exact": False, "rtol": 2e-2,
           "atol": 2e-2, "equal_nan": True}
    return {"args": args, "meta": meta, "grid": grid,
            "outputs": tuple(expected), "expected": expected,
            "comparison": {name: dict(tol) for name in expected}}

def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, gqa_kernel, DTYPES,
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
