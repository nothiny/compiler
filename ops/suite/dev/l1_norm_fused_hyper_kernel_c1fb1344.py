"""mk_l1_norm_fused_hyper_kernel_c1fb1344: makora train 第 62586 行的 Triton 解:l1_norm_fused_hyper_kernel;ref 为 torch 参考实现的 numpy 移植。

模式: memory.load.masked、reduce.sum、args.program_id、creation.arange。

文件只有两层:
  ① l1_norm_fused_hyper_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
                     怎么分配、搬运、启动由 runner 的 Device 决定。
"""

OPERATOR = {"name": "hidden/l1_norm_fused_hyper_kernel_c1fb1344", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ['memory.load.masked', 'reduce.sum', 'args.program_id', 'creation.arange']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 62586,
          "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d",
          "original_sha256": "c1fb1344b977aec201c5ac9ebe1372ab44a68c5f42c38be86c9dd46852d4b9ff"}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def l1_norm_fused_hyper_kernel(
    x_ptr,
    y_ptr,
    N_COLS: tl.constexpr,
    BLOCK_SIZE: tl.constexpr,
):
    # One program per row
    row_idx = tl.program_id(0).to(tl.int64)

    # With contiguous layout, stride == N_COLS; use constexpr to simplify index math
    row_off = row_idx * N_COLS
    x_row_ptr = x_ptr + row_off
    y_row_ptr = y_ptr + row_off

    # Align main-loop accesses to 128B (32 floats) for coalesced traffic
    shift = ((-row_off) & 31).to(tl.int32)

    offs = tl.arange(0, BLOCK_SIZE)

    # Vector accumulator across lanes, final reduction done once
    acc_vec = tl.zeros((BLOCK_SIZE,), dtype=tl.float32)

    # Register caches to avoid reloads in pass 2
    last_block_v = tl.zeros((BLOCK_SIZE,), dtype=tl.float32)
    penult_block_v = tl.zeros((BLOCK_SIZE,), dtype=tl.float32)
    tail_v = tl.zeros((BLOCK_SIZE,), dtype=tl.float32)

    # --- Pass 1: Reduction ---
    # Prologue for alignment
    if shift > 0:
        m = offs < tl.minimum(shift, N_COLS)
        v = tl.load(x_row_ptr + offs, mask=m, other=0.0, eviction_policy='evict_last')
        acc_vec += tl.abs(v)

    main_start = shift
    tl.multiple_of(main_start, 32)  # alignment hint for compiler

    # Compute number of full tiles and the aligned end of main loop
    num_full = (N_COLS - main_start) // BLOCK_SIZE
    main_end = main_start + num_full * BLOCK_SIZE

    if num_full > 0:
        if num_full >= 3:
            # Accumulate all but the last two blocks
            for k in range(0, num_full - 2):
                v = tl.load(x_row_ptr + main_start + k * BLOCK_SIZE + offs, eviction_policy='evict_last')
                acc_vec += tl.abs(v)
            # Keep last two blocks in registers for reuse in Pass 2
            penult_block_v = tl.load(x_row_ptr + main_start + (num_full - 2) * BLOCK_SIZE + offs, eviction_policy='evict_last')
            acc_vec += tl.abs(penult_block_v)
            last_block_v = tl.load(x_row_ptr + main_start + (num_full - 1) * BLOCK_SIZE + offs, eviction_policy='evict_last')
            acc_vec += tl.abs(last_block_v)
        elif num_full == 2:
            penult_block_v = tl.load(x_row_ptr + main_start + offs, eviction_policy='evict_last')
            acc_vec += tl.abs(penult_block_v)
            last_block_v = tl.load(x_row_ptr + main_start + BLOCK_SIZE + offs, eviction_policy='evict_last')
            acc_vec += tl.abs(last_block_v)
        else:  # num_full == 1
            last_block_v = tl.load(x_row_ptr + main_start + offs, eviction_policy='evict_last')
            acc_vec += tl.abs(last_block_v)

    # Tail accumulation and cache for reuse
    if main_end < N_COLS:
        tail_offs = main_end + offs
        m = tail_offs < N_COLS
        tail_v = tl.load(x_row_ptr + tail_offs, mask=m, other=0.0, eviction_policy='evict_last')
        acc_vec += tl.abs(tail_v)

    # Final reduction and compute scaling factor: y = x * (N / sum(|x|))
    l1_sum = tl.sum(acc_vec)
    scale = N_COLS / l1_sum

    # --- Pass 2: Normalize & Store ---
    # Prologue store for alignment region
    if shift > 0:
        m = offs < tl.minimum(shift, N_COLS)
        v = tl.load(x_row_ptr + offs, mask=m, other=0.0)
        tl.store(y_row_ptr + offs, v * scale, mask=m)

    # Main full blocks store with software pipelining and register reuse
    if num_full > 0:
        if num_full == 1:
            tl.store(y_row_ptr + main_start + offs, last_block_v * scale)
        elif num_full == 2:
            tl.store(y_row_ptr + main_start + offs, penult_block_v * scale)
            tl.store(y_row_ptr + main_start + BLOCK_SIZE + offs, last_block_v * scale)
        else:
            # Reload early blocks with pipelining; last two are already cached
            curr = tl.load(x_row_ptr + main_start + offs)
            for k in range(1, num_full - 2):
                nxt = tl.load(x_row_ptr + main_start + k * BLOCK_SIZE + offs)
                tl.store(y_row_ptr + main_start + (k - 1) * BLOCK_SIZE + offs, curr * scale)
                curr = nxt
            # Store the (num_full-3)-th block
            tl.store(y_row_ptr + main_start + (num_full - 3) * BLOCK_SIZE + offs, curr * scale)
            # Store the final two cached blocks
            tl.store(y_row_ptr + main_start + (num_full - 2) * BLOCK_SIZE + offs, penult_block_v * scale)
            tl.store(y_row_ptr + main_start + (num_full - 1) * BLOCK_SIZE + offs, last_block_v * scale)

    # Tail store from cached tail registers
    if main_end < N_COLS:
        tail_offs = main_end + offs
        m = tail_offs < N_COLS
        tl.store(y_row_ptr + tail_offs, tail_v * scale, mask=m)

# ------------------------------------------------------------------ ② case 层
# 典型用法:makora 行的 Triton 解,ref 为其 torch 参考实现的 numpy 移植;
# 输入按原 get_inputs 的构造种类复现(randn/zeros/randint...),权重两模型共用。
SHAPES = ((128,), (127,))
DTYPES = ('float32',)
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

    args = {'x_ptr': x, 'y_ptr': y}
    meta = {'N_COLS': x.shape[1], 'BLOCK_SIZE': 8192}
    r = ref({'x': x}, meta)
    expected = {'y_ptr': r["_o0"].astype(y.dtype)}
    case = {"args": args, "meta": meta, "grid": (x.shape[0],),
            "outputs": ('y_ptr',), "expected": expected}
    tol = 1e-4
    # fp32 dot 是 IEEE;低精度输入按 fp32 累加,按 expected 幅值自适应 atol
    case["comparison"] = {n: {"comparator": "allclose", "exact": False,
                              "rtol": tol,
                              "atol": max(1e-4, 2e-3 * float(np.abs(expected[n]).max())),
                              "equal_nan": True}
                              for n in case["outputs"]}
    case["launch_meta"] = {'num_stages': 5, 'num_warps': 8}

    return case


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, l1_norm_fused_hyper_kernel, DTYPES,
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
