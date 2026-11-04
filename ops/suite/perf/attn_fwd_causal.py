"""attn_fwd_causal: attention(compute 类)。
bench 稳态配置见 bench/workload.json(声明 shape [2, 2, 16, 32],验证 shape [1, 8, 256, 64]);正确性 shape 见下方 SHAPES。
模式: creation.arange、memory.load、memory.load.masked、creation.where、reduce.max、math.exp。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""

OPERATOR = {'name': 'bench/attn_fwd_causal', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'memory.load', 'memory.load.masked', 'creation.where', 'reduce.max', 'math.exp', 'reduce.sum', 'memory.store']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/attn_fwd_causal.py', 'sha256': 'a094145a4b387245f537be8dedceceae9eb4d9d22ba91250f4edc7c9cb63aad4'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def attn_fwd_causal_kernel(
    q_ptr, k_ptr, v_ptr, out_ptr,
    Z, H, N_CTX, scale,
    stride_qz, stride_qh, stride_qm, stride_qk,
    stride_kz, stride_kh, stride_kn, stride_kk,
    stride_vz, stride_vh, stride_vk, stride_vn,
    stride_oz, stride_oh, stride_om, stride_on,
    HEAD_DIM: tl.constexpr, BLOCK_N: tl.constexpr, CAUSAL: tl.constexpr,
):
    pid_m = tl.program_id(0)
    off_hz = tl.program_id(1)
    off_z = off_hz // H
    off_h = off_hz % H

    offs_d = tl.arange(0, HEAD_DIM)
    offs_n = tl.arange(0, BLOCK_N)
    q_base = q_ptr + off_z * stride_qz + off_h * stride_qh
    k_base = k_ptr + off_z * stride_kz + off_h * stride_kh
    v_base = v_ptr + off_z * stride_vz + off_h * stride_vh

    q = tl.load(q_base + pid_m * stride_qm + offs_d * stride_qk)
    nmask = offs_n < N_CTX
    k = tl.load(k_base + offs_n[:, None] * stride_kn + offs_d[None, :] * stride_kk,
                mask=nmask[:, None], other=0.0)
    qk = tl.sum(q[None, :] * k, axis=1) * scale
    qk = tl.where(nmask, qk, float("-inf"))
    if CAUSAL:
        qk = tl.where(offs_n <= pid_m, qk, float("-inf"))
    m = tl.max(qk, axis=0)
    p = tl.exp(qk - m)
    p = p / tl.sum(p, axis=0)
    v = tl.load(v_base + offs_n[:, None] * stride_vk + offs_d[None, :] * stride_vn,
                mask=nmask[:, None], other=0.0)
    out = tl.sum(p[:, None] * v, axis=0)
    tl.store(out_ptr + off_z * stride_oz + off_h * stride_oh + pid_m * stride_om
             + offs_d * stride_on, out)


# ------------------------------------------------------------------ ② case 层
DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((2, 2, 16, 32), (4, 4, 32, 64), (1, 1, 8, 16))

def ref(args, meta):
    q = np.asarray(args["q_ptr"], dtype=np.float64)
    k = np.asarray(args["k_ptr"], dtype=np.float64)
    v = np.asarray(args["v_ptr"], dtype=np.float64)
    scale = float(args["scale"])
    z, h, n, d = q.shape
    scores = np.einsum("zhid,zhjd->zhij", q, k) * scale
    mask = np.tril(np.ones((n, n), dtype=bool)) if meta["CAUSAL"] else np.ones((n, n), dtype=bool)
    scores = np.where(mask[None, None], scores, -np.inf)
    scores = scores - scores.max(axis=-1, keepdims=True)
    p = np.exp(scores)
    p = p / p.sum(axis=-1, keepdims=True)
    out = np.einsum("zhij,zhjd->zhid", p, v)
    return {"out_ptr": out.astype(np.asarray(args["out_ptr"]).dtype)}

def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    z, h, n, d = (int(v) for v in shape)
    from case_utils import fast_rng
    rng = fast_rng(seed)
    q = (rng.standard_normal((z, h, n, d)) * 0.5).astype(dtype)
    k = (rng.standard_normal((z, h, n, d)) * 0.5).astype(dtype)
    v = (rng.standard_normal((z, h, n, d)) * 0.5).astype(dtype)
    args = {"q_ptr": q, "k_ptr": k, "v_ptr": v,
            "out_ptr": np.zeros((z, h, n, d), dtype=dtype),
            "Z": np.int32(z), "H": np.int32(h), "N_CTX": np.int32(n),
            "scale": np.float32(1.0 / np.sqrt(d)),
            "stride_qz": np.int32(h * n * d), "stride_qh": np.int32(n * d),
            "stride_qm": np.int32(d), "stride_qk": np.int32(1),
            "stride_kz": np.int32(h * n * d), "stride_kh": np.int32(n * d),
            "stride_kn": np.int32(d), "stride_kk": np.int32(1),
            "stride_vz": np.int32(h * n * d), "stride_vh": np.int32(n * d),
            "stride_vk": np.int32(d), "stride_vn": np.int32(1),
            "stride_oz": np.int32(h * n * d), "stride_oh": np.int32(n * d),
            "stride_om": np.int32(d), "stride_on": np.int32(1)}
    meta = {"HEAD_DIM": d, "BLOCK_N": triton.next_power_of_2(n), "CAUSAL": True}
    grid = (n, z * h)
    return {"args": args, "meta": meta, "grid": grid,
            "outputs": ("out_ptr",), "expected": ref(args, meta)}

def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, attn_fwd_causal_kernel, DTYPES,
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
