"""dropout_softmax_fwd_kernel: dropout + online softmax 合一的单趟前向。

模式: 1D grid(行号),每行用 tl.static_range(NUM_BLOCKS) 静态展开列块:
training 分支里用 tl.rand(seed, row*N+col) 生成 Philox 随机数,keep = r >= p,
保留的乘 1/(1-p)、其余置 -inf;然后做 online softmax 的 max/sum 递推
(m_new = max(m_i, x_max), l_i = l_i*exp(m_i-m_new)+sum(exp(x-m_new))),
最后写归一化结果。p/training 是 constexpr。

文件只有两层:
  ① dropout_softmax_fwd_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/dropout_softmax_fwd_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.if_constexpr', 'control.loop_constexpr', 'creation.full', 'memory.load.masked', 'memory.store.masked', 'reduce.max.axis0', 'reduce.sum.axis0', 'random.rand', 'math.exp', 'math.maximum']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "test", "row": 20285, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "8168f1040884e000fbc5c4eaa8d5a09b676b78c836fc057a2d7b243697b36505"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def dropout_softmax_fwd_kernel(x_ptr, y_ptr, seed_ptr, stride_xm: tl.constexpr, stride_xn: tl.constexpr, stride_ym: tl.constexpr, stride_yn: tl.constexpr, M: tl.constexpr, N: tl.constexpr, p: tl.constexpr, training: tl.constexpr, BLOCK_N: tl.constexpr, NUM_BLOCKS: tl.constexpr):
    row = tl.program_id(0)
    if row >= M:
        return
    x_row_ptr = x_ptr + row * stride_xm
    y_row_ptr = y_ptr + row * stride_ym
    seed = tl.load(seed_ptr).to(tl.uint64)
    m_i = tl.full((), -float('inf'), tl.float32)
    l_i = tl.full((), 0.0, tl.float32)
    scale = 1.0 / (1.0 - p)
    for bid in tl.static_range(0, NUM_BLOCKS):
        col_offsets = bid * BLOCK_N + tl.arange(0, BLOCK_N)
        mask = col_offsets < N
        x = tl.load(x_row_ptr + col_offsets * stride_xn, mask=mask, other=-float('inf')).to(tl.float32)
        if training:
            ctr = (row * N + col_offsets).to(tl.uint32)
            r = tl.rand(seed, ctr)
            keep = r >= p
            x = tl.where(keep, x * scale, -float('inf'))
        x_max = tl.max(x, axis=0)
        m_new = tl.maximum(m_i, x_max)
        l_i = l_i * tl.exp(m_i - m_new)
        l_i += tl.sum(tl.exp(x - m_new), axis=0)
        m_i = m_new
    l_safe = tl.where(l_i > 0.0, l_i, 1.0)
    for bid in tl.static_range(0, NUM_BLOCKS):
        col_offsets = bid * BLOCK_N + tl.arange(0, BLOCK_N)
        mask = col_offsets < N
        x = tl.load(x_row_ptr + col_offsets * stride_xn, mask=mask, other=-float('inf')).to(tl.float32)
        if training:
            ctr = (row * N + col_offsets).to(tl.uint32)
            r = tl.rand(seed, ctr)
            keep = r >= p
            x = tl.where(keep, x * scale, -float('inf'))
        y = tl.exp(x - m_i) / l_safe
        if training:
            y = tl.where(l_i > 0.0, y, 0.0)
        tl.store(y_row_ptr + col_offsets * stride_yn, y, mask=mask)

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

# 典型用法:训练时的 dropout + softmax(推理时 training=False 跳过 dropout)。
# 原始程序是 (batch, dim) 的大词表/大特征 logits;这里取 (256, 4096)。
# 两个 shape 分别选 training=True / False,把 constexpr 分支两侧都覆盖。
#
# (rows, N):
#   典型  (256, 4096)  training=True:Philox dropout + online softmax
#   规模  (512, 4096)  典型规模 ×2:dim0 256->512;training=True 在更大 batch 上
#   泛化  (33, 1000)   training=False(纯 softmax);N 不整除 BLOCK_N
#         (1, 1)      退化:单元素
SHAPES = ((33, 100), (1, 1))
_TRAINING = {(64, 256): True, (128, 256): True, (33, 100): False, (1, 1): False}
# 原始程序是 fp32;tl.rand/exp 也只产生/接受 fp32。
DTYPES = ('float32', 'float16', 'bfloat16')
BLOCK_N = 1024
DROP_P = 0.1
RNG_SEED = 20240501


def ref(args, meta):
    """numpy 对照:位精确复现 tl.rand,再做 dropout 与两趟 softmax。"""
    rows = int(args["ROWS"])
    n = int(meta["N"])
    p = np.float32(meta["p"])
    scale = np.float32(1.0) / (np.float32(1.0) - p)
    x = np.asarray(args["x_ptr"], dtype=np.float64).reshape(rows, n)
    if meta["training"]:
        r = np.empty((rows, n), np.float32)
        for row in range(rows):
            r[row] = _uniform(_philox(RNG_SEED, n, base=row * n)[0])
        keep = np.asarray(r >= p)
        xd = np.where(keep, x * float(scale), -np.inf)
    else:
        xd = x
    m = xd.max(axis=1, keepdims=True)
    l = np.exp(xd - m).sum(axis=1, keepdims=True)
    out = np.asarray(args["y_ptr"])
    return {"y_ptr": (np.exp(xd - m) / l).reshape(-1).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    rows, n = (int(v) for v in shape)
    if min(rows, n) <= 0:
        raise ValueError(f"shape must be positive (rows, N), got {shape}")
    training = _TRAINING[(rows, n)]

    # logits ~N(0, 2^2),1/16 网格;第 0 行全 0(softmax 均匀,测试 l 的边界)。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (np.clip(np.rint(rng.standard_normal((rows, n), dtype=np.float32) * 32),
                 -128, 127) / 16).astype(np.float32)
    x[0, :] = 0.0

    args = {"x_ptr": x.reshape(-1), "y_ptr": np.full(rows * n, -7.0, np.float32),
            "seed_ptr": np.array([RNG_SEED], np.int32), "ROWS": np.int32(rows)}
    meta = {"N": n, "p": DROP_P, "training": training, "BLOCK_N": BLOCK_N,
            "NUM_BLOCKS": (n + BLOCK_N - 1) // BLOCK_N,
            "stride_xm": n, "stride_xn": 1, "stride_ym": n, "stride_yn": 1,
            "M": rows}
    case = {"args": args, "meta": meta, "grid": (rows,), "outputs": ("y_ptr",),
            "expected": ref(args, meta)}
    # dropout 的 keep 掩码是逐位复现的,但 exp/求和顺序不同会有 1 ULP 级差异。
    case["comparison"] = {"y_ptr": {"comparator": "allclose", "exact": False,
                                    "rtol": 1e-4, "atol": 1e-6, "equal_nan": True}}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, dropout_softmax_fwd_kernel, DTYPES,
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
