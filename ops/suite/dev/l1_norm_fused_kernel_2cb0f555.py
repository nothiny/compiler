"""mk_l1_norm_fused_kernel_2cb0f555: makora train 第 63069 行的 Triton 解:l1_norm_fused_kernel;ref 为 torch 参考实现的 numpy 移植。

模式: memory.load.masked、reduce.sum、args.program_id、creation.arange。

文件只有两层:
  ① l1_norm_fused_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
                     怎么分配、搬运、启动由 runner 的 Device 决定。
"""

OPERATOR = {"name": "hidden/l1_norm_fused_kernel_2cb0f555", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ['memory.load.masked', 'reduce.sum', 'args.program_id', 'creation.arange']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 63069,
          "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d",
          "original_sha256": "2cb0f555e02ca5979f37b959ea449a1510daf88d26e99680035af6c1905ceaf2"}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def l1_norm_fused_kernel(
    x_ptr,
    y_ptr,
    stride_row,
    n_cols,
    BLOCK_SIZE: tl.constexpr,
):
    # Program ID corresponds to one row
    row_idx = tl.program_id(0).to(tl.int64)
    row_off = row_idx * stride_row
    
    # Base pointers for this row
    x_row = x_ptr + row_off
    y_row = y_ptr + row_off

    # 1. Alignment Prologue
    # Calculate shift to align the main loop loads to 128-byte (32 float) boundaries
    # (base + shift) % 32 == 0. This ensures maximum memory bandwidth.
    shift = ((-row_off) & 31).to(tl.int32)
    
    # Offsets [0, BLOCK_SIZE)
    offs = tl.arange(0, BLOCK_SIZE)
    
    # Accumulator for L1 norm (Scalar to save registers vs vector accumulator)
    acc = 0.0
    
    # --- Pass 1: Reduction (Sum of Abs) ---
    
    # Handle Unaligned Head
    if shift > 0:
        mask = offs < shift
        mask = mask & (offs < n_cols)
        # evict_last: unlikely to be reused immediately but keeps in cache longer
        val = tl.load(x_row + offs, mask=mask, other=0.0, eviction_policy='evict_last')
        acc += tl.sum(tl.abs(val))

    # Main Loop Setup
    main_start = shift
    # Hint to compiler that x_row + main_start is aligned
    tl.multiple_of(main_start, 32)
    
    remaining = n_cols - main_start
    if remaining < 0:
        remaining = 0
        
    num_full = remaining // BLOCK_SIZE
    main_end = main_start + num_full * BLOCK_SIZE
    
    # Register Caching Strategy:
    # Cache up to 4 full blocks in registers to avoid reloading them from DRAM in Pass 2.
    # This reduces global memory reads by up to ~50% in the second pass for fit rows.
    CACHE_COUNT = 4
    num_cached = num_full if num_full < CACHE_COUNT else CACHE_COUNT
    num_reload = num_full - num_cached
    
    # Allocate registers for cached blocks explicitly
    c1 = tl.zeros((BLOCK_SIZE,), dtype=tl.float32)
    c2 = tl.zeros((BLOCK_SIZE,), dtype=tl.float32)
    c3 = tl.zeros((BLOCK_SIZE,), dtype=tl.float32)
    c4 = tl.zeros((BLOCK_SIZE,), dtype=tl.float32)
    c_tail = tl.zeros((BLOCK_SIZE,), dtype=tl.float32)
    
    cur_off = main_start
    
    # A. Reloadable Blocks (Stream through L1/L2, accumulate, do not cache in registers)
    if num_reload > 0:
        # Software pipelining: load next block while processing current
        curr = tl.load(x_row + cur_off + offs, eviction_policy='evict_last')
        for _ in range(num_reload - 1):
            acc += tl.sum(tl.abs(curr))
            cur_off += BLOCK_SIZE
            curr = tl.load(x_row + cur_off + offs, eviction_policy='evict_last')
        acc += tl.sum(tl.abs(curr))
        cur_off += BLOCK_SIZE
        
    # B. Cached Blocks (Load and keep in registers)
    # Use evict_first as we hold data in registers and don't need L1/L2 persistence
    if num_cached == 4:
        c1 = tl.load(x_row + cur_off + offs, eviction_policy='evict_first')
        acc += tl.sum(tl.abs(c1))
        cur_off += BLOCK_SIZE
        c2 = tl.load(x_row + cur_off + offs, eviction_policy='evict_first')
        acc += tl.sum(tl.abs(c2))
        cur_off += BLOCK_SIZE
        c3 = tl.load(x_row + cur_off + offs, eviction_policy='evict_first')
        acc += tl.sum(tl.abs(c3))
        cur_off += BLOCK_SIZE
        c4 = tl.load(x_row + cur_off + offs, eviction_policy='evict_first')
        acc += tl.sum(tl.abs(c4))
        cur_off += BLOCK_SIZE
    elif num_cached == 3:
        c1 = tl.load(x_row + cur_off + offs, eviction_policy='evict_first')
        acc += tl.sum(tl.abs(c1))
        cur_off += BLOCK_SIZE
        c2 = tl.load(x_row + cur_off + offs, eviction_policy='evict_first')
        acc += tl.sum(tl.abs(c2))
        cur_off += BLOCK_SIZE
        c3 = tl.load(x_row + cur_off + offs, eviction_policy='evict_first')
        acc += tl.sum(tl.abs(c3))
        cur_off += BLOCK_SIZE
    elif num_cached == 2:
        c1 = tl.load(x_row + cur_off + offs, eviction_policy='evict_first')
        acc += tl.sum(tl.abs(c1))
        cur_off += BLOCK_SIZE
        c2 = tl.load(x_row + cur_off + offs, eviction_policy='evict_first')
        acc += tl.sum(tl.abs(c2))
        cur_off += BLOCK_SIZE
    elif num_cached == 1:
        c1 = tl.load(x_row + cur_off + offs, eviction_policy='evict_first')
        acc += tl.sum(tl.abs(c1))
        cur_off += BLOCK_SIZE
        
    # Tail Loading (Cache in registers)
    if main_end < n_cols:
        tail_off = main_end + offs
        mask = tail_off < n_cols
        c_tail = tl.load(x_row + tail_off, mask=mask, other=0.0, eviction_policy='evict_first')
        acc += tl.sum(tl.abs(c_tail))
        
    # --- Calculation ---
    # mean = acc / n_cols. y = x / mean = x * (n_cols / acc)
    scale = n_cols / acc
    
    # --- Pass 2: Normalization & Store ---
    
    # 1. Store Unaligned Head (Reload needed)
    if shift > 0:
        mask = offs < shift
        mask = mask & (offs < n_cols)
        val = tl.load(x_row + offs, mask=mask, other=0.0, eviction_policy='evict_first')
        tl.store(y_row + offs, val * scale, mask=mask)
        
    cur_off = main_start
    
    # 2. Reload and Store Non-Cached Blocks (Software Pipeline)
    if num_reload > 0:
        curr = tl.load(x_row + cur_off + offs, eviction_policy='evict_first')
        for _ in range(num_reload - 1):
            tl.store(y_row + cur_off + offs, curr * scale)
            cur_off += BLOCK_SIZE
            curr = tl.load(x_row + cur_off + offs, eviction_policy='evict_first')
        tl.store(y_row + cur_off + offs, curr * scale)
        cur_off += BLOCK_SIZE
        
    # 3. Store Cached Blocks (Direct from Registers, No Load)
    if num_cached == 4:
        tl.store(y_row + cur_off + offs, c1 * scale)
        cur_off += BLOCK_SIZE
        tl.store(y_row + cur_off + offs, c2 * scale)
        cur_off += BLOCK_SIZE
        tl.store(y_row + cur_off + offs, c3 * scale)
        cur_off += BLOCK_SIZE
        tl.store(y_row + cur_off + offs, c4 * scale)
    elif num_cached == 3:
        tl.store(y_row + cur_off + offs, c1 * scale)
        cur_off += BLOCK_SIZE
        tl.store(y_row + cur_off + offs, c2 * scale)
        cur_off += BLOCK_SIZE
        tl.store(y_row + cur_off + offs, c3 * scale)
    elif num_cached == 2:
        tl.store(y_row + cur_off + offs, c1 * scale)
        cur_off += BLOCK_SIZE
        tl.store(y_row + cur_off + offs, c2 * scale)
    elif num_cached == 1:
        tl.store(y_row + cur_off + offs, c1 * scale)
        
    # 4. Store Tail
    if main_end < n_cols:
        tail_off = main_end + offs
        mask = tail_off < n_cols
        tl.store(y_row + tail_off, c_tail * scale, mask=mask)

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

    args = {'x_ptr': x, 'y_ptr': y, 'stride_row': int(x.strides[0] // x.itemsize), 'n_cols': x.shape[1]}
    meta = {'BLOCK_SIZE': 8192}
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
    case["launch_meta"] = {'num_stages': 4, 'num_warps': 8}

    return case


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, l1_norm_fused_kernel, DTYPES,
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
