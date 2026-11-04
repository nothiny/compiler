"""hardsigmoid_kernel(2): hardsigmoid 的三种存储形态(int16 打包 fp16/bf16、fp32)。

模式: 一维带掩码 load,DTYPE_ID 是 constexpr 分支:0 表示输入就是 fp32;1/2 表示
输入是 int16 整数(先转 fp16 / bf16 再转 f32,数值转换),算
clamp(x+3, 0, 6)/6,最后把结果先舍入到 fp16/bf16、再 *数值* 转成 int16 写回
(输入侧把 int16 数值转成半精度再转 f32,输出侧把结果舍入到半精度再转回
int16;两侧都是数值转换,取值都落在半精度精确域内)。

文件只有两层:
  ① hardsigmoid_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/hardsigmoid_kernel_2', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'cast.to', 'control.if_constexpr', 'creation.arange', 'math.maximum', 'math.minimum', 'memory.load.masked', 'memory.store.masked']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 45069, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "c6cf6312ba867b6fb422ca2743bb49a7ad71bad5d10a06fd9b71f8ec2137ca53"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def hardsigmoid_kernel(x_ptr, out_ptr, n_elements, BLOCK_SIZE: tl.constexpr, DTYPE_ID: tl.constexpr):
    pid = tl.program_id(0)
    base_offset = pid * BLOCK_SIZE
    offsets = base_offset + tl.arange(0, BLOCK_SIZE)
    mask = offsets < n_elements
    if DTYPE_ID == 0:
        x = tl.load(x_ptr + offsets, mask=mask, other=0.0).to(tl.float32)
    elif DTYPE_ID == 1:
        x = tl.load(x_ptr + offsets, mask=mask, other=0).to(tl.int16).to(tl.float16).to(tl.float32)
    else:
        x = tl.load(x_ptr + offsets, mask=mask, other=0).to(tl.int16).to(tl.bfloat16).to(tl.float32)
    shifted = x + 3.0
    clamped = tl.maximum(tl.minimum(shifted, 6.0), 0.0)
    out_fp32 = clamped / 6.0
    if DTYPE_ID == 0:
        tl.store(out_ptr + offsets, out_fp32, mask=mask)
    else:
        if DTYPE_ID == 1:
            out_stored = out_fp32.to(tl.float16).to(tl.int16)
        else:
            out_stored = out_fp32.to(tl.bfloat16).to(tl.int16)
        tl.store(out_ptr + offsets, out_stored, mask=mask)

# ------------------------------------------------------------------ ② case 层
# 典型用法:量化激活在"半精度位打包成 int16"的存储上做 hardsigmoid(省一半带宽)。
# 原始 (4096, 393216) fp32 的激活;这里保留一整行宽度、batch 缩到 1。int16 形状
# 的奇偶用来选 DTYPE_ID=1(fp16 位)还是 2(bf16 位),两条 cast 分支都被覆盖。
#
# (n,):
#   典型  (393216,)  fp32 路径(DTYPE_ID=0)与 int16 打包路径都要跑
#   规模  (786432,)  典型规模 ×2:dim0 393216->786432
#   规模  (1179648,)  典型规模 ×3:dim0 393216->1179648
#   泛化  (1025,)    尾部不整除 BLOCK;奇数 n => int16 走 fp16 位
#         (1024,)    偶数 n => int16 走 bf16 位
SHAPES = ((128,), (97,))
# fp32 原始路径 + int16 位打包路径(对应 kernel 的三种 DTYPE_ID)。
DTYPES = ('int16', 'float32', 'float16', 'bfloat16')
_MAX = 6.0


def _dtype_id(dtype, n):
    if dtype == "float32":
        return 0
    return 1 if n % 2 else 2


def ref(args, meta):
    """numpy 对照:输入按 *数值* 解释(int16 -> fp16/bf16 -> f32),算完再舍入回 int16。"""
    did = int(meta["DTYPE_ID"])
    x = np.asarray(args["x_ptr"])
    # 输入侧是数值转换(int16 的整数值 -> 半精度 -> f32),不是位解释;取值都落在
    # 半精度可精确表示的整数区间,所以这一步无损。
    xf = x.astype(np.float32)
    # kernel 在 f32 里算 clamp(x+3,0,6)/6:ref 也按 f32 算(否则 f64 除法再舍入会
    # 和 f32 除法差 1 ULP,精确比较就会假失败)。
    y = np.clip(xf + np.float32(3.0), np.float32(0.0), np.float32(_MAX)) / np.float32(_MAX)
    out = np.asarray(args["out_ptr"])
    if did == 0:
        return {"out_ptr": y.astype(out.dtype)}
    if did == 1:
        return {"out_ptr": y.astype(np.float16).astype(np.int16)}
    bits = y.astype(np.float32).view(np.uint32)
    rounded = (bits + np.uint32(0x7FFF) + ((bits >> 16) & np.uint32(1))) & np.uint32(0xFFFF0000)
    bf = (rounded >> np.uint32(16)).astype(np.uint16)
    decoded = (bf.astype(np.uint32) << np.uint32(16)).view(np.float32)
    return {"out_ptr": decoded.astype(np.int16)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n = int(shape[0])
    if n <= 0:
        raise ValueError(f"n must be positive, got {shape}")
    did = _dtype_id(dtype, n)

    # 取值只从 {-8, -3, 0, 3, 8} 里选:clamp(x+3, 0, 6) 得到 0/3/6,再 /6 得到
    # 0/0.5/1 —— 商是精确的,所以 fp32 路径与 int16 路径都可以按位比较(否则
    # f32 除法 1 ULP 的差异会跨过舍入边界)。这些整数值在半精度里也精确。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    levels = np.array([-8, -3, 0, 3, 8], np.int16)
    xi = levels[rng.integers(0, levels.size, n)]
    x = xi.astype(np.float32) if did == 0 else xi

    args = {"x_ptr": x, "out_ptr": np.zeros(n, dtype=np.int16 if did else np.float32),
            "n_elements": np.int32(n)}
    meta = {"BLOCK_SIZE": 1024, "DTYPE_ID": did}
    return {"args": args, "meta": meta, "grid": ((n + 1023) // 1024,),
            "outputs": ("out_ptr",), "expected": ref(args, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;位打包输出按位精确比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, hardsigmoid_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=True)


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float32'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float32': 'float32', 'int16': 'int16'}


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
