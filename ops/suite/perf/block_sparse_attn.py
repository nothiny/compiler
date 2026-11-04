"""block_sparse_attn: attention(compute 类)。
bench 稳态配置见 bench/workload.json(声明 shape [2, 2, 32, 32],验证 shape [1, 8, 256, 64]);正确性 shape 见下方 SHAPES。
模式: creation.arange、memory.load.masked、creation.full、creation.zeros、memory.store.masked、memory.load。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""

OPERATOR = {'name': 'bench/block_sparse_attn', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'memory.load.masked', 'creation.full', 'creation.zeros', 'memory.store.masked', 'memory.load', 'creation.where', 'math.maximum']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/block_sparse_attn.py', 'sha256': '3981fafc5a6cb6a2aef0096960d57753cf9d5f253ffed638e372cfa6e37b18b4'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def block_sparse_kernel(Q, K, V, Out, BM_ptr,
                        stride_qm, stride_qk, stride_kn, stride_kk, stride_vk, stride_vn,
                        stride_om, stride_on,
                        N_CTX, scale, NBLK_N: tl.constexpr,
                        HEAD_DIM: tl.constexpr, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr):
    pid_m = tl.program_id(0)
    pid_bh = tl.program_id(1)
    offs_m = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    offs_d = tl.arange(0, HEAD_DIM)
    q_base = Q + pid_bh * N_CTX * stride_qm
    v_base = V + pid_bh * N_CTX * stride_vk
    q = tl.load(q_base + offs_m[:, None] * stride_qm + offs_d[None, :] * stride_qk,
                mask=(offs_m[:, None] < N_CTX), other=0.0)
    m_i = tl.full([BLOCK_M], float("-inf"), tl.float32)
    l_i = tl.zeros([BLOCK_M], tl.float32)
    acc = tl.zeros([BLOCK_M, HEAD_DIM], tl.float32)
    for nb in range(0, NBLK_N):
        keep = tl.load(BM_ptr + pid_m * NBLK_N + nb)
        if keep != 0:
            offs_n = nb * BLOCK_N + tl.arange(0, BLOCK_N)
            k = tl.load(K + pid_bh * N_CTX * stride_kn + offs_n[:, None] * stride_kn + offs_d[None, :] * stride_kk,
                        mask=(offs_n[:, None] < N_CTX), other=0.0)
            qk = tl.dot(q, tl.trans(k)) * scale
            qk = tl.where(offs_n[None, :] < N_CTX, qk, float("-inf"))
            m_ij = tl.maximum(m_i, tl.max(qk, axis=1))
            p = tl.exp(qk - m_ij[:, None])
            alpha = tl.exp(m_i - m_ij)
            l_i = l_i * alpha + tl.sum(p, axis=1)
            acc = acc * alpha[:, None]
            v = tl.load(v_base + offs_n[:, None] * stride_vk + offs_d[None, :] * stride_vn,
                        mask=(offs_n[:, None] < N_CTX), other=0.0)
            acc += tl.dot(p, v)
            m_i = m_ij
    acc = acc / l_i[:, None]
    tl.store(Out + pid_bh * N_CTX * stride_om + offs_m[:, None] * stride_om + offs_d[None, :] * stride_on,
             acc, mask=(offs_m[:, None] < N_CTX))


# ------------------------------------------------------------------ ② case 层
DTYPES = ('float32',)

SHAPES = ((2, 2, 32, 32), (4, 4, 64, 64), (1, 1, 16, 16))

def ref(args, meta):
    q = np.asarray(args["Q"], dtype=np.float64)
    k = np.asarray(args["K"], dtype=np.float64)
    v = np.asarray(args["V"], dtype=np.float64)
    bm = np.asarray(args["BM_ptr"])
    scale = float(args["scale"])
    z, h, n, d = q.shape
    nb = meta["NBLK_N"]
    bn = meta["BLOCK_N"]
    s = np.einsum("zhid,zhjd->zhij", q, k) * scale
    # apply block mask
    for i in range(0, n, meta["BLOCK_M"]):
        for j in range(nb):
            if bm[i // meta["BLOCK_M"], j] == 0:
                s[:, :, i:i + meta["BLOCK_M"], j * bn:(j + 1) * bn] = -np.inf
    s = s - s.max(axis=-1, keepdims=True)
    p = np.exp(s)
    p = p / p.sum(axis=-1, keepdims=True)
    out = np.einsum("zhij,zhjd->zhid", p, v)
    return {"Out": out.astype(np.asarray(args["Out"]).dtype)}

def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    z, h, n, d = (int(x) for x in shape)
    from case_utils import fast_rng
    rng = fast_rng(seed)
    bm_m, bm_n = triton.cdiv(n, 32), triton.cdiv(n, 32)
    block_mask = (rng.random((bm_m, bm_n)) < 0.6).astype(np.int32)
    # ensure at least the diagonal block is kept so every row is valid
    for i in range(bm_m):
        block_mask[i, i] = 1
    args = {"Q": rng.standard_normal((z, h, n, d)).astype(dtype),
            "K": rng.standard_normal((z, h, n, d)).astype(dtype),
            "V": rng.standard_normal((z, h, n, d)).astype(dtype),
            "Out": np.zeros((z, h, n, d), dtype=dtype), "BM_ptr": block_mask,
            "N_CTX": np.int32(n), "scale": np.float32(1.0 / np.sqrt(d)),
            "stride_qm": np.int32(d), "stride_qk": np.int32(1),
            "stride_kn": np.int32(d), "stride_kk": np.int32(1),
            "stride_vk": np.int32(d), "stride_vn": np.int32(1),
            "stride_om": np.int32(d), "stride_on": np.int32(1)}
    meta = {"NBLK_N": bm_n, "HEAD_DIM": d, "BLOCK_M": 32, "BLOCK_N": 32}
    grid = (bm_m, z * h)
    expected = ref(args, meta)
    tol = {"comparator": "allclose", "exact": False, "rtol": 2e-2,
           "atol": 2e-2, "equal_nan": True}
    return {"args": args, "meta": meta, "grid": grid,
            "outputs": tuple(expected), "expected": expected,
            "comparison": {name: dict(tol) for name in expected}}

def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, block_sparse_kernel, DTYPES,
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
