"""fused_stage1_kernel: dropout + bias 之后做分块 online-softmax 的第一阶段。

模式: 1D grid(M * N 方向块数),pid 拆成 (row, 列块)。块内 = x + bias,用
tl.rand(seed, row*N+col) 的 Philox 随机数做 dropout(keep 的乘 1/(1-p)、其余置 0),
把 keep 以 int8 写回(第二段复用),再把被掩码的 lane 置 -inf 后算块内 max 与
sum(exp(x-max)),两者分别写到 per-block 的 max_out/sum_out。

文件只有两层:
  ① fused_stage1_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/fused_stage1_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'creation.arange', 'creation.where', 'math.cdiv', 'math.maximum', 'memory.load.masked', 'memory.store.masked', 'random.rand', 'reduce.max.axis0', 'reduce.sum.axis0']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "test", "row": 20386, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "10bef44c9bb2bc5e93da79141452901d33f43339218b74118ab7afd40a11fdb9"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def fused_stage1_kernel(x_ptr, b_ptr, mask_out_ptr, max_out_ptr, sum_out_ptr, M, N, p, scale, seed, BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(0)
    num_blocks_n = tl.cdiv(N, BLOCK_SIZE)
    pid_m = pid // num_blocks_n
    pid_n = pid % num_blocks_n
    offs_n = pid_n * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask_bounds = offs_n < N
    x_offset = pid_m * N + offs_n
    x = tl.load(x_ptr + x_offset, mask=mask_bounds, other=-float('inf'))
    b = tl.load(b_ptr + offs_n, mask=mask_bounds, other=0.0)
    val = x + b
    rng_offset = pid_m * N + offs_n
    r = tl.rand(seed, rng_offset)
    keep = r < 1.0 - p
    real_val = tl.where(keep, val * scale, 0.0)
    val_reduced = tl.where(mask_bounds, real_val, -float('inf'))
    tl.store(mask_out_ptr + x_offset, keep.to(tl.int8), mask=mask_bounds)
    local_max = tl.max(val_reduced, axis=0)
    local_sum = tl.sum(tl.exp(val_reduced - local_max), axis=0)
    out_idx = pid_m * num_blocks_n + pid_n
    tl.store(max_out_ptr + out_idx, local_max)
    tl.store(sum_out_ptr + out_idx, local_sum)

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

# 典型用法:大词表 logits 的 dropout+softmax 第一段(第二阶段读 max_out/sum_out)。
# 原始程序是 (batch, dim) = (4096, 393216) 的 logits;这里保留 dim 的量级、
# batch 缩到 32。
#
# (M, N):
#   典型  (32, 65536)  32 行 x 64K 列(64 个列块)
#   规模  (64, 65536)  典型规模 ×2:dim0 32->64
#   规模  (32, 131072)  典型规模 ×2:dim1 65536->131072
#   泛化  (17, 1000)   N 不整除 BLOCK_SIZE,最后一个列块被掩码
#         (1, 1)      退化:单元素
SHAPES = ((32, 128), (17, 100), (1, 1))
# 原始程序是 fp32;tl.rand 也只产生 fp32。
DTYPES = ('float32', 'float16', 'bfloat16')
BLOCK_SIZE = 1024
DROP_P = 0.2
RNG_SEED = 20240502


def ref(args, meta):
    """numpy 对照:位精确复现 tl.rand 的 dropout,再算块内 max/sum。"""
    m, n = int(args["M"]), int(args["N"])
    p, scale = np.float32(args["p"]), np.float32(args["scale"])
    blocks = (n + BLOCK_SIZE - 1) // BLOCK_SIZE
    x = np.asarray(args["x_ptr"], dtype=np.float64).reshape(m, n)
    b = np.asarray(args["b_ptr"], dtype=np.float64)
    keep = np.zeros((m, n), np.int8)
    val = np.empty((m, n), np.float64)
    for row in range(m):
        r = _uniform(_philox(RNG_SEED, n, base=row * n)[0])
        k = np.asarray(r < (np.float32(1.0) - p))
        keep[row] = k.astype(np.int8)
        val[row] = np.where(k, (x[row] + b) * float(scale), 0.0)
    padded = np.full((m, blocks * BLOCK_SIZE), -np.inf)
    padded[:, :n] = val
    v = padded.reshape(m, blocks, BLOCK_SIZE)
    mx = v.max(axis=2)
    sm = np.exp(v - mx[:, :, None]).sum(axis=2)
    out_max = np.asarray(args["max_out_ptr"])
    out_sum = np.asarray(args["sum_out_ptr"])
    return {"mask_out_ptr": keep.reshape(-1),
            "max_out_ptr": mx.reshape(-1).astype(out_max.dtype),
            "sum_out_ptr": sm.reshape(-1).astype(out_sum.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    m, n = (int(v) for v in shape)
    if min(m, n) <= 0:
        raise ValueError(f"shape must be positive (M, N), got {shape}")
    blocks = (n + BLOCK_SIZE - 1) // BLOCK_SIZE

    # logits 是 1/16 网格上的 ~N(0,2),bias 是 1/16 网格的 per-column 偏移。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (np.clip(np.rint(rng.standard_normal((m, n), dtype=np.float32) * 32),
                 -128, 127) / 16).astype(np.float32)
    b = (rng.integers(-16, 17, n, dtype=np.int16) / 16).astype(np.float32)
    # 语义边界:第 0 行 logits 与 bias 全 0(块内 max 恰为 0)。
    x[0, :] = 0.0
    b[:] = 0.0

    args = {"x_ptr": x.reshape(-1), "b_ptr": b,
            "mask_out_ptr": np.full(m * n, -1, np.int8),
            "max_out_ptr": np.full(m * blocks, -7.0, np.float32),
            "sum_out_ptr": np.full(m * blocks, -7.0, np.float32),
            "M": np.int32(m), "N": np.int32(n), "p": np.float32(DROP_P),
            "scale": np.float32(1.0 / (1.0 - DROP_P)), "seed": np.int32(RNG_SEED)}
    meta = {"BLOCK_SIZE": BLOCK_SIZE, "p": DROP_P}
    grid = (m * blocks,)
    return {"args": args, "meta": meta, "grid": grid,
            "outputs": ("mask_out_ptr", "max_out_ptr", "sum_out_ptr"),
            "expected": ref(args, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;keep 掩码按位精确比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, fused_stage1_kernel, DTYPES,
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
