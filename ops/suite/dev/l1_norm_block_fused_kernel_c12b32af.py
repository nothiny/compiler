"""mk_l1_norm_block_fused_kernel_c12b32af: makora train 第 61878 行的 Triton 解:l1_norm_block_fused_kernel;ref 为 torch 参考实现的 numpy 移植。

模式: memory.load.masked、reduce.sum、args.program_id、creation.arange。

文件只有两层:
  ① l1_norm_block_fused_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
                     怎么分配、搬运、启动由 runner 的 Device 决定。
"""

OPERATOR = {"name": "hidden/l1_norm_block_fused_kernel_c12b32af", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ['memory.load.masked', 'reduce.sum', 'args.program_id', 'creation.arange']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 61878,
          "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d",
          "original_sha256": "c12b32afeb79d29b51b65f1f9a3be302a3e4bcb7da3beaefdeca2b53eb5f0c46"}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def l1_norm_block_fused_kernel(
    x_ptr,           # *f32 / *f16: [B, D], contiguous
    y_ptr,           # *same: [B, D], contiguous
    B,               # int32: batch size (rows)
    D,               # int32: feature dim (cols)
    BLOCK_ROWS: tl.constexpr,
    BLOCK_D: tl.constexpr,
):
    """
    Fused L1 normalization kernel with multi-row, wide-column tiling.
    For each block of rows, it:
      1) streams across all columns to compute per-row L1 sums,
      2) computes inv-mean(|x|) per row,
      3) streams again to write x * inv_mean(|x|) into y.
    """
    pid = tl.program_id(0)

    # Rows handled by this program
    row_start = pid * BLOCK_ROWS
    rows = row_start + tl.arange(0, BLOCK_ROWS)
    mask_rows = rows < B

    # ---------- First pass: compute per-row L1 sums ----------
    abs_sum = tl.zeros([BLOCK_ROWS], dtype=tl.float32)

    cols_block = tl.arange(0, BLOCK_D)
    for col_start in range(0, D, BLOCK_D):
        cols = col_start + cols_block
        mask_cols = cols < D

        # Compute 2D offsets for [BLOCK_ROWS, BLOCK_D] tile
        row_offsets = rows.to(tl.int64) * D
        offs = row_offsets[:, None] + cols[None, :].to(tl.int64)
        mask = mask_rows[:, None] & mask_cols[None, :]

        x = tl.load(x_ptr + offs, mask=mask, other=0.0)
        # accumulate sum of abs along columns in fp32
        abs_sum += tl.sum(tl.abs(x.to(tl.float32)), axis=1)

    # Compute inv mean(|x|) per row: inv_mean = D / sum(|x|)
    inv_mean = D / abs_sum  # [BLOCK_ROWS], fp32

    # ---------- Second pass: scale and store ----------
    for col_start in range(0, D, BLOCK_D):
        cols = col_start + cols_block
        mask_cols = cols < D

        row_offsets = rows.to(tl.int64) * D
        offs = row_offsets[:, None] + cols[None, :].to(tl.int64)
        mask = mask_rows[:, None] & mask_cols[None, :]

        x = tl.load(x_ptr + offs, mask=mask, other=0.0)
        x_f32 = x.to(tl.float32)
        y = x_f32 * inv_mean[:, None]
        y = y.to(x.dtype)
        tl.store(y_ptr + offs, y, mask=mask)

# ------------------------------------------------------------------ ② case 层
# 典型用法:makora 行的 Triton 解,ref 为其 torch 参考实现的 numpy 移植;
# 输入按原 get_inputs 的构造种类复现(randn/zeros/randint...),权重两模型共用。
SHAPES = ((128,), (127,))
DTYPES = ('float32', 'float16', 'bfloat16')
_HOST_DTYPE = {"float32": np.float32}

def _sigmoid(v):
    return 1.0 / (1.0 + np.exp(-v))


def _silu(v):
    return v / (1.0 + np.exp(-v))


def _relu(v):
    return np.maximum(v, 0.0)


def _rsqrt(v):
    return 1.0 / np.sqrt(v)


def _erf(v):
    """Abramowitz-Stegun 7.1.26,|误差| < 1.5e-7(numpy 无 erf,不引 scipy)。"""
    s = np.sign(v)
    a = np.abs(np.asarray(v, dtype=np.float64))
    t = 1.0 / (1.0 + 0.3275911 * a)
    y = 1.0 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t
                - 0.284496736) * t + 0.254829592) * t * np.exp(-a * a)
    return s * y


def _softmax(v, axis):
    m = v.max(axis=axis, keepdims=True)
    e = np.exp(v - m)
    return e / e.sum(axis=axis, keepdims=True)


def _layer_norm(v, w, b, eps):
    mu = v.mean(axis=-1, keepdims=True)
    var = ((v - mu) ** 2).mean(axis=-1, keepdims=True)
    return (v - mu) / np.sqrt(var + eps) * w + b



def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    from case_utils import fast_rng
    rng = fast_rng(seed)
    b = int(shape[0])
    x = rng.standard_normal((b, 8193,)).astype(np.float32)

    y = np.zeros_like(x)

    args = {'x_ptr': x, 'y_ptr': y, 'B': x.shape[0], 'D': x.shape[1]}
    meta = {'BLOCK_ROWS': 4, 'BLOCK_D': 4096}
    r = ref({'x': x}, meta)
    expected = {'y_ptr': r["_o0"].astype(y.dtype)}
    case = {"args": args, "meta": meta, "grid": (triton.cdiv(x.shape[0], 4),),
            "outputs": ('y_ptr',), "expected": expected}
    tol = 1e-4
    # fp32 dot 是 IEEE;低精度输入按 fp32 累加,按 expected 幅值自适应 atol
    case["comparison"] = {n: {"comparator": "allclose", "exact": False,
                              "rtol": tol,
                              "atol": max(1e-4, 2e-3 * float(np.abs(expected[n]).max())),
                              "equal_nan": True}
                              for n in case["outputs"]}
    case["launch_meta"] = {'num_stages': 4, 'num_warps': 8}

    return case


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, l1_norm_block_fused_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed)


def ref(args, meta):
    x = np.asarray(args['x'], dtype=np.float64)
    return {"_o0": (x / np.mean(np.abs(x), axis=1, keepdims=True))}


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
