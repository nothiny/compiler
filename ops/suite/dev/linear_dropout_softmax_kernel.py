"""linear_dropout_softmax_kernel: Y = softmax(dropout(X @ W^T + bias)) 一趟算完。

模式: 1D grid(行号),每行三趟列循环:第一趟沿 N 分块、块内沿 K 分块做
tl.dot 的点积累加(+bias),再用 tl.rand(seed, row*N+col) 的 Philox 随机数做
dropout(keep 的乘 1/(1-p)、其余写 0),把 keep 以 uint8 写进 MASK 并累积行 max;
第二趟求 exp(x-row_max) 的和;第三趟写归一化结果。

文件只有两层:
  ① linear_dropout_softmax_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/linear_dropout_softmax_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.if_runtime', 'control.loop_runtime_bound', 'creation.arange', 'creation.zeros', 'creation.full', 'linalg.dot', 'memory.load.masked', 'memory.store.masked', 'random.rand', 'reduce.max.axis0', 'reduce.sum.axis0']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "test", "row": 20057, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "d7c70688d52fff19dcace64d70418f0cba8b74b42a2cbe1356d0eb74c5c2d04b"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def linear_dropout_softmax_kernel(X_ptr, W_ptr, BIAS_ptr, OUT_ptr, MASK_ptr, M, N, K, stride_xm, stride_xk, stride_wk, stride_wn, stride_om, stride_on, dropout_p: tl.constexpr, seed: tl.int32, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr):
    """
    Fused kernel that computes: Y = softmax(dropout((X @ W^T + bias)))
    over the feature dimension (N), row by row.
    We process one row (m) per program and loop over N and K.
    This is optimized for very large N (=16384) typical for this model.
    """
    m = tl.program_id(0)
    if m >= M:
        return
    X_row_ptr = X_ptr + m * stride_xm
    OUT_row_ptr = OUT_ptr + m * stride_om
    MASK_row_ptr = MASK_ptr + m * stride_om
    rnd_seed = seed
    rnd_offset = m * N
    row_max = -float('inf')
    keep_prob = 1.0 - dropout_p
    scale = 1.0 / keep_prob if keep_prob > 0 else 0.0
    for n_start in range(0, N, BLOCK_N):
        offs_n = n_start + tl.arange(0, BLOCK_N)
        mask_n = offs_n < N
        acc = tl.zeros((BLOCK_N,), dtype=tl.float32)
        for k_start in range(0, K, BLOCK_K):
            offs_k = k_start + tl.arange(0, BLOCK_K)
            mask_k = offs_k < K
            x_ptrs = X_row_ptr + offs_k * stride_xk
            x = tl.load(x_ptrs, mask=mask_k, other=0.0)
            w_ptrs = W_ptr + (offs_k[:, None] * stride_wk + offs_n[None, :] * stride_wn)
            w = tl.load(w_ptrs, mask=mask_k[:, None] & mask_n[None, :], other=0.0)
            acc += tl.sum(w * x[:, None], axis=0)
        if BIAS_ptr is not None:
            bias = tl.load(BIAS_ptr + offs_n, mask=mask_n, other=0.0)
            acc += bias
        rnd = tl.rand(tl.full((BLOCK_N,), rnd_seed, tl.int32), rnd_offset + offs_n)
        keep = rnd > dropout_p
        keep = keep & mask_n
        acc = tl.where(keep, acc * scale, 0.0)
        out_ptrs = OUT_row_ptr + offs_n * stride_on
        tl.store(out_ptrs, acc, mask=mask_n)
        tile_max = tl.max(acc, axis=0)
        row_max = tl.maximum(row_max, tile_max)
        tl.store(MASK_row_ptr + offs_n * stride_on, keep.to(tl.uint8), mask=mask_n)
    denom = 0.0
    for n_start in range(0, N, BLOCK_N):
        offs_n = n_start + tl.arange(0, BLOCK_N)
        mask_n = offs_n < N
        out_ptrs = OUT_row_ptr + offs_n * stride_on
        acc = tl.load(out_ptrs, mask=mask_n, other=-float('inf'))
        num = tl.exp(acc - row_max)
        denom += tl.sum(num, axis=0)
    inv_denom = 1.0 / denom
    for n_start in range(0, N, BLOCK_N):
        offs_n = n_start + tl.arange(0, BLOCK_N)
        mask_n = offs_n < N
        out_ptrs = OUT_row_ptr + offs_n * stride_on
        acc = tl.load(out_ptrs, mask=mask_n, other=-float('inf'))
        y = tl.exp(acc - row_max) * inv_denom
        tl.store(out_ptrs, y, mask=mask_n)

# ------------------------------------------------------------------ ② case 层
def _philox(seed, n, c1=0, base=0):
    """Bit-exact NumPy reproduction of Triton's philox4_32 (counter = base+i, c1, 0, 0)."""
    mask = np.uint64(0xffffffff)
    c = [np.arange(base, base + n, dtype=np.uint64), np.full(n, c1, np.uint64),
         np.zeros(n, np.uint64), np.zeros(n, np.uint64)]
    k0 = seed & 0xffffffff; k1 = (seed >> 32) & 0xffffffff
    for _ in range(10):
        p0 = c[0] * np.uint64(0xd2511f53); p2 = c[2] * np.uint64(0xcd9e8d57)
        c = [((p2 >> np.uint64(32)) ^ c[1] ^ np.uint64(k0)) & mask, p2 & mask,
             ((p0 >> np.uint64(32)) ^ c[3] ^ np.uint64(k1)) & mask, p0 & mask]
        k0 = (k0 + 0x9e3779b9) & 0xffffffff; k1 = (k1 + 0xbb67ae85) & 0xffffffff
    return [x.astype(np.uint32) for x in c]


def _uniform(bits):
    """Philox 输出 -> [0,1) 的 f32 均匀分布(与 tl.rand 相同)。"""
    x = bits.view(np.int32)
    return np.where(x < 0, ~x, x).astype(np.float32) * np.float32(4.6566127342e-10)

# 典型用法:小 batch、大输出的 Linear + dropout + softmax(原始注释里 N=16384 是
# 这个模型的真实维度)。这里取 M=16 行、N=4096、K=1024,并把 N 缩小以控制耗时。
#
# (M, N, K):
#   典型  (16, 4096, 1024)  N=4096(远大于 M),K=1024 是 hidden
#   规模  (32, 4096, 1024)  典型规模 ×2:dim0 16->32
#   规模  (16, 8192, 1024)  典型规模 ×2:dim1 4096->8192
#   泛化  (5, 300, 100)     M/N/K 都不整除 BLOCK:三处掩码都走
#         (1, 1, 1)        退化:单元素
SHAPES = ((16, 128, 128), (5, 100, 100))
# 原始程序是 fp32(dot 与 softmax 都在 f32);tl.rand 也只产生 fp32。
DTYPES = ('float32', 'float16', 'bfloat16')
BLOCK_M, BLOCK_N, BLOCK_K = 16, 128, 64
DROP_P = 0.1
RNG_SEED = 20240503


def ref(args, meta):
    """numpy 对照:GEMM+bias -> 位精确 Philox dropout -> softmax(float64)。"""
    m, n, k = int(args["M"]), int(args["N"]), int(args["K"])
    x = np.asarray(args["X_ptr"], dtype=np.float64).reshape(m, k)
    wgt = np.asarray(args["W_ptr"], dtype=np.float64).reshape(n, k)
    b = np.asarray(args["BIAS_ptr"], dtype=np.float64)
    logits = x @ wgt.T + b[None, :]
    p = np.float32(meta["dropout_p"])
    scale = np.float32(1.0) / (np.float32(1.0) - p)
    keep = np.zeros((m, n), np.uint8)
    d = np.empty((m, n), np.float64)
    for row in range(m):
        r = _uniform(_philox(RNG_SEED, n, base=row * n)[0])
        kk = np.asarray(r > p)
        keep[row] = kk.astype(np.uint8)
        d[row] = np.where(kk, logits[row] * float(scale), 0.0)
    mx = d.max(axis=1, keepdims=True)
    l = np.exp(d - mx).sum(axis=1, keepdims=True)
    out = np.asarray(args["OUT_ptr"])
    return {"OUT_ptr": (np.exp(d - mx) / l).reshape(-1).astype(out.dtype),
            "MASK_ptr": keep.reshape(-1)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    m, n, k = (int(v) for v in shape)
    if min(m, n, k) <= 0:
        raise ValueError(f"shape must be positive (M, N, K), got {shape}")

    # 权重/激活取 1/16 网格的 [-1, 1):dot 的 f32 累加误差最小;第 0 行 X 全 0
    # (logits 只由 bias 决定),第 0 列 W 全 1(该列 logits 等于 X 的行和)。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (rng.integers(-16, 16, (m, k), dtype=np.int16) / 16).astype(np.float32)
    wgt = (rng.integers(-16, 16, (n, k), dtype=np.int16) / 16).astype(np.float32)
    b = (rng.integers(-16, 17, n, dtype=np.int16) / 16).astype(np.float32)
    x[0, :] = 0.0
    wgt[0, :] = 1.0

    args = {"X_ptr": x.reshape(-1), "W_ptr": wgt.reshape(-1), "BIAS_ptr": b,
            "OUT_ptr": np.full(m * n, -7.0, np.float32),
            "MASK_ptr": np.full(m * n, 255, np.uint8),
            "M": np.int32(m), "N": np.int32(n), "K": np.int32(k),
            "stride_xm": np.int32(k), "stride_xk": np.int32(1),
            "stride_wk": np.int32(1), "stride_wn": np.int32(k),
            "stride_om": np.int32(n), "stride_on": np.int32(1),
            "seed": np.int32(RNG_SEED)}
    meta = {"dropout_p": DROP_P, "BLOCK_M": BLOCK_M, "BLOCK_N": BLOCK_N,
            "BLOCK_K": BLOCK_K}
    case = {"args": args, "meta": meta, "grid": (m,),
            "outputs": ("OUT_ptr", "MASK_ptr"), "expected": ref(args, meta)}
    case["comparison"] = {"OUT_ptr": {"comparator": "allclose", "exact": False,
                                      "rtol": 1e-4, "atol": 1e-6, "equal_nan": True},
                          "MASK_ptr": {"comparator": "array_equal", "exact": True}}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;keep 掩码按位精确比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, linear_dropout_softmax_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)


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
