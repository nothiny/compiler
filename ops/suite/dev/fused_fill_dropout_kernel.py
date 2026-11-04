"""fused_fill_dropout_kernel: 融合填充与 dropout —— 用 Philox 随机数决定每个位置写值还是写 0。

模式: 带掩码的连续 store,随机数由 tl.rand(seed, offs) 生成(Triton 的 Philox),与
阈值 p 比较决定保留/丢弃,保留时写 value*scale(dropout 的 inverted 缩放)。
oracle 在 numpy 里位精确复现同一条 Philox 流,所以输出可以逐位比较。

文件只有两层:
  ① fused_fill_dropout_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/fused_fill_dropout_kernel', "group": 'basic', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'creation.arange', 'creation.where', 'memory.store.masked', 'random.rand']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 353869, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "30981115cc1cfd5e1392164faa56a6e246153dfe436dc0d53d4e2f07121613aa"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def fused_fill_dropout_kernel(out_ptr, n_elements, value, p, scale, seed, BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(0)
    offsets = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = offsets < n_elements
    r = tl.rand(seed, offsets)
    keep = r > p
    out = tl.where(keep, value * scale, 0.0)
    tl.store(out_ptr + offsets, out, mask=mask)

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
# 典型用法:训练时的一次 dropout(inverted dropout:保留的元素乘 1/(1-p))+ 填充。
# 原始程序是 (batch, dim) 展平后按 1024 分块;这里取一条 64K 元素的激活。
#
# (n,):
#   典型  (65536,)  一条 64K 元素的激活,64 个块
#   规模  (131072,)  典型规模 ×2:dim0 65536->131072
#   规模  (196608,)  典型规模 ×3:dim0 65536->196608
#   泛化  (5000,)   尾部:5000 = 4*1024 + 904,最后一个块被掩码
#         (1,)     退化:单元素
SHAPES = ((128,), (1,))
# tl.rand 只产生 fp32 随机数,输出也按 fp32 写。
DTYPES = ('float32', 'float16', 'bfloat16')
P = 0.4                  # 丢弃概率(0 到 1 之间的真实值)
VALUE = 3.0              # 被填充的常数
SCALE = 1.0 / (1.0 - P)  # inverted dropout 的缩放
RNG_SEED = 12345         # 交给 kernel 的 Philox seed
_COMPARISON = {"out_ptr": {"comparator": "array_equal", "exact": True}}


def ref(args, meta):
    """numpy 对照:位精确复现 tl.rand(seed, offs) 后按同一规则写值。"""
    n = int(args["n_elements"])
    seed = int(args["seed"])
    r = _uniform(_philox(seed, n)[0])
    keep = r > np.float32(args["p"])
    out = np.where(keep, np.float32(args["value"]) * np.float32(args["scale"]),
                   np.float32(0.0))
    return {"out_ptr": out.astype(np.asarray(args["out_ptr"]).dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n = int(shape[0])
    if n <= 0:
        raise ValueError(f"n must be positive, got {shape}")

    # 初值用 -7:被丢弃的位置写 0、保留的位置写 value*scale,都不可能是 -7,
    # 所以"没有任何 lane 漏写"也能被检查出来(掩码边界最容易在这里出错)。
    args = {"out_ptr": np.full(n, -7.0, np.float32), "n_elements": np.int32(n),
            "value": np.float32(VALUE), "p": np.float32(P),
            "scale": np.float32(SCALE), "seed": np.int32(RNG_SEED)}
    meta = {"BLOCK_SIZE": min(1024, n)}
    return {"args": args, "meta": meta, "grid": (((n + meta["BLOCK_SIZE"] - 1)
                                                 // meta["BLOCK_SIZE"]),),
            "outputs": ("out_ptr",), "expected": ref(args, meta),
            "comparison": _COMPARISON}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;随机输出按位精确比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, fused_fill_dropout_kernel, DTYPES,
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
