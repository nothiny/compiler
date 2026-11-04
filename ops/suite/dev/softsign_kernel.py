"""softsign: 逐元素 x/(1+|x|),一维展平、无掩码。

模式: pid * BLOCK_SIZE 的连续访存,无掩码 load/store(要求元素数整除
BLOCK_SIZE),逐元素 abs + div。原始程序把 (batch, dim) 一整块展平后处理,
grid = n // BLOCK_SIZE,host 端断言整除。

文件只有两层:
  ① softsign_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/softsign_kernel', "group": 'basic', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'creation.arange', 'math.abs', 'memory.load', 'memory.store']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 48866, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "2fb22b1b88dee8b38d34ecf205a93a78d5cd976163b108f773b000395c7a5b8c"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def softsign_kernel(x_ptr, out_ptr, BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(0)
    offsets = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    x = tl.load(x_ptr + offsets)
    y = x / (1.0 + tl.abs(x))
    tl.store(out_ptr + offsets, y)

# ------------------------------------------------------------------ ② case 层
# 典型用法:activation 层前的逐元素处理,(batch, dim) 展平成 1D,BLOCK_SIZE=1024,
# grid = n // BLOCK_SIZE。kernel 无掩码,所以每个 shape 都必须整除 BLOCK_SIZE。
#
# (n,):
#   典型  (393216,)  原始 (4096, 393216) fp32:保留 dim=393216,batch 缩到 1 行
#   规模  (786432,)  典型规模 ×2:dim0 393216->786432
#   规模  (1179648,)  典型规模 ×3:dim0 393216->1179648
#   泛化  (4096,)    小尺寸:4 个 block,整除
#         (1,)      退化:单元素,BLOCK_SIZE=1
SHAPES = ((128,), (1,))
# 原始程序是 fp32(rand 输入);softsign 只有 abs/div,半精度是合法域,补 fp16/bf16。
DTYPES = ("float32", "float16", "bfloat16")
# bf16 在 host 上用 float32 存值,上传时由 Device 转成 bf16(见 pointer_dtypes)。
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}


def ref(args, meta):
    """numpy 对照:float64 计算后转回输出 dtype。"""
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    out = np.asarray(args["out_ptr"])
    return {"out_ptr": (x / (1.0 + np.abs(x))).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n = int(shape[0])
    if n <= 0:
        raise ValueError(f"shape must be a positive element count, got {shape}")

    # 原始输入是 [0,1) 的均匀分布;这里改用对称的 [-8, 8)、1/16 的倍数,
    # 这样正负两条分支都走到,而且取值在 fp16/bf16 里都精确,上传舍入不会
    # 改变 expected(host 上用同一份值算)。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (rng.integers(-128, 128, n, dtype=np.int16) / 16).astype(_HOST_DTYPE[dtype])
    # 语义边界: 0(分母为 1)、最小的负值、网格上的最大正值。
    x[0] = 0.0
    x[-1] = 8.0
    if n > 2:
        x[1] = -8.0

    block = min(1024, n)
    args = {"x_ptr": x, "out_ptr": np.zeros(n, dtype=x.dtype)}
    meta = {"BLOCK_SIZE": block}
    case = {"args": args, "meta": meta, "grid": (n // block,), "outputs": ("out_ptr",),
            "expected": ref(args, meta)}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {"x_ptr": "bfloat16"}
        # host 侧输出仍是 fp32,但 kernel 在 bf16 里算,按半精度容差比较。
        tol = 5e-3
        case["comparison"] = {"out_ptr": {"comparator": "allclose", "exact": False,
                                          "rtol": tol, "atol": tol, "equal_nan": True}}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, softsign_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float32'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float32': 'float32', 'float16': 'float16', 'bfloat16': 'bfloat16'}


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
