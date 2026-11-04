"""softplus: 逐元素 log(1+exp(x)),阈值以上直接取 x,一维展平、无掩码。

模式: pid * BLOCK_SIZE 的连续访存,无掩码 load/store(要求元素数整除
BLOCK_SIZE),tl.where 做 THRESHOLD 分支(防止 exp 溢出),exp/log 各一次。
原始程序把 (batch, dim) 展平后按 BLOCK_SIZE=1024 切块,THRESHOLD=20.0。

文件只有两层:
  ① softplus_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/softplus_kernel', "group": 'basic', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'creation.arange', 'creation.where', 'math.exp', 'math.log', 'memory.load', 'memory.store']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 47965, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "121d6ece9f4291994ee0cdc0522d04abb81a5ecc6abd528d805000622d75bf81"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def softplus_kernel(x_ptr, out_ptr, n_elements, BLOCK_SIZE: tl.constexpr, THRESHOLD: tl.constexpr):
    pid = tl.program_id(0)
    offsets = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    x = tl.load(x_ptr + offsets)
    y = tl.where(x > THRESHOLD, x, tl.log(1.0 + tl.exp(x)))
    tl.store(out_ptr + offsets, y)

# ------------------------------------------------------------------ ② case 层
# 典型用法:激活层,输入 (batch, dim) 展平成 1D;原始 BLOCK_SIZE=1024、
# grid = n // BLOCK_SIZE,host 断言整除。kernel 无掩码,所以每个 shape 都整除。
#
# (n,):
#   典型  (393216,)  原始 (4096, 393216) fp32:保留 dim=393216,batch 缩到 1 行
#   规模  (786432,)  典型规模 ×2:dim0 393216->786432
#   规模  (1179648,)  典型规模 ×3:dim0 393216->1179648
#   泛化  (8192,)    小尺寸:8 个 block,整除
#         (1024,)    退化:单 block
SHAPES = ((128,),)
# tl.exp / tl.log 在本机 Triton 上只接受 fp32(半精度直接报不支持),所以这个
# kernel 的合法域只有 fp32;输入先 .to(tl.float32) 的变体不在本编译单元内。
DTYPES = ('float32',)


def ref(args, meta):
    """numpy 对照:float64 计算,阈值分支与 kernel 一致。"""
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    out = np.asarray(args["out_ptr"])
    with np.errstate(over="ignore"):
        y = np.where(x > 20.0, x, np.log(1.0 + np.exp(x)))
    return {"out_ptr": y.astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n = int(shape[0])
    if n <= 0:
        raise ValueError(f"shape must be a positive element count, got {shape}")

    # 原始输入是 [0,1) 的均匀分布;这里换成 [-16, 20) 的对称范围(标准差约 6),
    # 让 exp 的软饱和区和阈值分支两侧都被覆盖,取值落在 1/8 的网格上,与原始
    # 连续分布的形状相近但仍然精确可表示。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (rng.integers(-128, 160, n, dtype=np.int16) / 8).astype(np.float32)
    # 语义边界: 阈值以上的大正值(走 where 的直通分支)、0(得 ln2)、
    # 很负的值(结果 ~exp(x),接近 0)。
    x[0] = 25.0
    x[1] = 0.0
    x[2] = -20.0

    block = min(1024, n)
    args = {"x_ptr": x, "out_ptr": np.zeros(n, dtype=np.float32), "n_elements": np.int32(n)}
    meta = {"BLOCK_SIZE": block, "THRESHOLD": 20.0}
    return {"args": args, "meta": meta, "grid": (n // block,), "outputs": ("out_ptr",),
            "expected": ref(args, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, softplus_kernel, DTYPES,
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
