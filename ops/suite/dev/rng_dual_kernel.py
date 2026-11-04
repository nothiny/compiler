"""rng_dual_kernel: 一个 grid 同时给两个张量(如 RNN 的 h0 与 c0)填随机初值。

模式: grid 是 "2 x 每张量块数",program_id 落在后半段时 is_c0 为真,目标指针换成
c0,并用 global_offsets 偏移 n_elements 让第二张量取到 Philox 流的另一段
(两个张量不共享随机数)。运行时分派 + 间接指针选择 + 带掩码 store。
oracle 在 numpy 里位精确复现 tl.randn 的两段输出。

文件只有两层:
  ① rng_dual_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/rng_dual_kernel', "group": 'basic', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'creation.arange', 'control.loop_runtime_bound', 'memory.store.masked', 'random.randn', 'memory.indirect']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 481736, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "b9e5f404c86b47a297f6b257739e36190f56f0ab86d69d642e1f82a6f0045c5c"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def rng_dual_kernel(h0_ptr, c0_ptr, seed_ptr, n_elements, BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(0)
    num_blocks_per_tensor = tl.cdiv(n_elements, BLOCK_SIZE)
    is_c0 = pid >= num_blocks_per_tensor
    block_idx = pid % num_blocks_per_tensor
    block_start = block_idx * BLOCK_SIZE
    offsets = block_start + tl.arange(0, BLOCK_SIZE)
    mask = offsets < n_elements
    seed = tl.load(seed_ptr)
    global_offsets = offsets + (n_elements if is_c0 else 0)
    rnd = tl.randn(seed, global_offsets)
    target_ptr = c0_ptr if is_c0 else h0_ptr
    tl.store(target_ptr + offsets, rnd, mask=mask)

def _philox(seed, n, c1=0, base=0):
    """Bit-exact NumPy reproduction of Triton's philox4_32 (counter = base+i, c1, 0, 0)."""
    import numpy as np

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
    import numpy as np

    x = bits.view(np.int32)
    return np.where(x < 0, ~x, x).astype(np.float32) * np.float32(4.6566127342e-10)
def _normals(words):
    import numpy as np

    u = [_uniform(w).astype(np.float64) for w in words]
    out = []
    for a, b in ((u[0], u[1]), (u[2], u[3])):
        radius = np.sqrt(-2 * np.log(np.maximum(1e-7, a))); theta = 2 * np.pi * b
        out.extend((radius * np.cos(theta), radius * np.sin(theta)))
    return out

# ------------------------------------------------------------------ ② case 层
# 典型用法:LSTM/GRU 的 h0、c0 用同一 kernel 一起初始化(layers x hidden 展平)。
# 原始版本是 (batch, dim) 展平后按 1024 分块;这里取一条 16K 元素的状态向量,
# 两个张量各一份,于是 grid = 2 * 16。
#
# (n,):
#   典型  (16384,)  一个 16K 元素的状态向量(两个张量各 16K)
#   规模  (32768,)  典型规模 ×2:dim0 16384->32768
#   规模  (49152,)  典型规模 ×3:dim0 16384->49152
#   泛化  (4100,)   尾部:4100 的最后一个块被掩码(掩码在两条分支上都要生效)
#         (1,)     退化:单元素,两个张量各 1 个随机数
SHAPES = ((128,), (1,))
# tl.randn 只产生 fp32 随机数,输出按 fp32 写。
DTYPES = ('float32', 'float16', 'bfloat16')
RNG_SEED = 987654321
_COMPARISON = {name: {"comparator": "allclose", "exact": False, "rtol": 1e-4,
                      "atol": 1e-5, "equal_nan": True}
               for name in ("h0_ptr", "c0_ptr")}


def ref(args, meta):
    """numpy 对照:位精确复现两段 tl.randn(seed, offs) 与 tl.randn(seed, offs+n)。"""
    n = int(args["n_elements"])
    seed = int(np.asarray(args["seed_ptr"])[0])
    h0 = _normals(_philox(seed, n, base=0))[0]
    c0 = _normals(_philox(seed, n, base=n))[0]
    return {"h0_ptr": h0.astype(np.asarray(args["h0_ptr"]).dtype),
            "c0_ptr": c0.astype(np.asarray(args["c0_ptr"]).dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n = int(shape[0])
    if n <= 0:
        raise ValueError(f"n must be positive, got {shape}")

    block = min(1024, n)
    # 初值取 -5:正常写入的是 ~N(0,1) 的随机数,若某个 lane 漏写就能看到 -5。
    args = {"h0_ptr": np.full(n, -5.0, np.float32),
            "c0_ptr": np.full(n, -5.0, np.float32),
            "seed_ptr": np.array([RNG_SEED], np.int32), "n_elements": np.int32(n)}
    meta = {"BLOCK_SIZE": block}
    grid = (2 * ((n + block - 1) // block),)
    return {"args": args, "meta": meta, "grid": grid,
            "outputs": ("h0_ptr", "c0_ptr"), "expected": ref(args, meta),
            "comparison": _COMPARISON}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;随机输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, rng_dual_kernel, DTYPES,
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
