"""flash_decode: attention(compute 类)。
bench 稳态配置见 bench/workload.json(声明 shape [2, 2, 32, 32],验证 shape [1, 8, 256, 64]);正确性 shape 见下方 SHAPES。
模式: creation.arange、memory.load、creation.full、creation.zeros、memory.store、memory.load.masked。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""

OPERATOR = {'name': 'bench/flash_decode', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'memory.load', 'creation.full', 'creation.zeros', 'memory.store', 'memory.load.masked', 'creation.where', 'math.maximum']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/flash_decode.py', 'sha256': 'd4b4005b2a67da2c8117f65b7423f2911e1e253609ef6d3d205e74bd270115af'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def flash_decode_kernel(Q, K, V, Out, stride_qh, stride_kh, stride_kn, stride_kk,
                        stride_vh, stride_vk, stride_vn, stride_oh,
                        H, N_CTX, scale, HEAD_DIM: tl.constexpr, BLOCK_N: tl.constexpr):
    off_hz = tl.program_id(0)
    off_z = off_hz // H
    off_h = off_hz % H
    offs_d = tl.arange(0, HEAD_DIM)
    offs_n = tl.arange(0, BLOCK_N)
    q = tl.load(Q + off_z * H * stride_qh + off_h * stride_qh + offs_d)
    kb = K + off_z * H * stride_kh + off_h * stride_kh
    vb = V + off_z * H * stride_vh + off_h * stride_vh
    m = tl.full([], float("-inf"), tl.float32)
    l = tl.zeros([], tl.float32)
    acc = tl.zeros([HEAD_DIM], tl.float32)
    for start_n in range(0, N_CTX, BLOCK_N):
        offs_nn = start_n + offs_n
        nmask = offs_nn < N_CTX
        k = tl.load(kb + offs_nn[:, None] * stride_kn + offs_d[None, :] * stride_kk,
                    mask=nmask[:, None], other=0.0)
        qk = tl.sum(q[None, :] * k, axis=1) * scale
        qk = tl.where(nmask, qk, float("-inf"))
        m_new = tl.maximum(m, tl.max(qk, axis=0))
        p = tl.exp(qk - m_new)
        alpha = tl.exp(m - m_new)
        l = l * alpha + tl.sum(p, axis=0)
        v = tl.load(vb + offs_nn[:, None] * stride_vk + offs_d[None, :] * stride_vn,
                    mask=nmask[:, None], other=0.0)
        acc = acc * alpha + tl.sum(p[:, None] * v, axis=0)
        m = m_new
    tl.store(Out + off_z * H * stride_oh + off_h * stride_oh + offs_d, acc / l)


# ------------------------------------------------------------------ ② case 层
DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((2, 2, 32, 32), (4, 4, 64, 64), (1, 1, 16, 16))

def ref(args, meta):
    q = np.asarray(args["Q"], dtype=np.float64)
    k = np.asarray(args["K"], dtype=np.float64)
    v = np.asarray(args["V"], dtype=np.float64)
    scale = float(args["scale"])
    z, h, n, d = k.shape
    out = np.zeros((z, h, d))
    for zz in range(z):
        for hh in range(h):
            s = (k[zz, hh] @ q[zz, hh]) * scale
            s = s - s.max()
            p = np.exp(s); p = p / p.sum()
            out[zz, hh] = p @ v[zz, hh]
    return {"Out": out.astype(np.asarray(args["Out"]).dtype)}

def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    z, h, n, d = (int(x) for x in shape)
    from case_utils import fast_rng
    rng = fast_rng(seed)
    args = {"Q": rng.standard_normal((z, h, d)).astype(dtype),
            "K": rng.standard_normal((z, h, n, d)).astype(dtype),
            "V": rng.standard_normal((z, h, n, d)).astype(dtype),
            "Out": np.zeros((z, h, d), dtype=dtype),
            "H": np.int32(h), "N_CTX": np.int32(n), "scale": np.float32(1.0 / np.sqrt(d)),
            "stride_qh": np.int32(d), "stride_kh": np.int32(n * d), "stride_kn": np.int32(d),
            "stride_kk": np.int32(1), "stride_vh": np.int32(n * d), "stride_vk": np.int32(d),
            "stride_vn": np.int32(1), "stride_oh": np.int32(d)}
    meta = {"HEAD_DIM": d, "BLOCK_N": 32}
    grid = (z * h,)
    expected = ref(args, meta)
    tol = {"comparator": "allclose", "exact": False, "rtol": 2e-2,
           "atol": 2e-2, "equal_nan": True}
    return {"args": args, "meta": meta, "grid": grid,
            "outputs": tuple(expected), "expected": expected,
            "comparison": {name: dict(tol) for name in expected}}

def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, flash_decode_kernel, DTYPES,
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
