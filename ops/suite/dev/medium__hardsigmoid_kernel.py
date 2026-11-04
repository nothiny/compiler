"""hardsigmoid_kernel: hardsigmoid = clamp(x/6 + 0.5, 0, 1),带 grid-stride 循环。

模式: 每个 program 用 for tile_id in tl.range(pid, num_tiles, num_programs) 的
grid-stride 循环处理多个块(循环上界与步长都来自运行时值),块内带掩码 load/store,
再做一次缩放与双向 clamp。

文件只有两层:
  ① hardsigmoid_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'medium/hardsigmoid_kernel', "group": 'medium', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.loop_runtime_bound', 'creation.arange', 'math.maximum', 'math.minimum', 'memory.load.masked', 'memory.store.masked']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 45287, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "72910f04f96718b26c62c2f38d452ea64bd846828a8c113cfe515c990ec6d483"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def hardsigmoid_kernel(x_ptr, out_ptr, n_elements, BLOCK_SIZE: tl.constexpr):
    """
    Optimized HardSigmoid kernel with grid-stride looping for sustained H100 occupancy.
    Implements: clamp(x / 6.0 + 0.5, 0.0, 1.0)
    """
    pid = tl.program_id(0)
    num_programs = tl.num_programs(0)
    num_tiles = (n_elements + BLOCK_SIZE - 1) // BLOCK_SIZE
    for tile_id in tl.range(pid, num_tiles, num_programs, num_stages=1):
        start = tile_id * BLOCK_SIZE
        offsets = start + tl.arange(0, BLOCK_SIZE)
        mask = offsets < n_elements
        x = tl.load(x_ptr + offsets, mask=mask)
        scaled = x / 6.0 + 0.5
        out = tl.maximum(0.0, tl.minimum(1.0, scaled))
        tl.store(out_ptr + offsets, out, mask=mask)

# ------------------------------------------------------------------ ② case 层
# 典型用法:激活层,输入 (batch, dim) 展平成一维后按块处理。原始 (4096, 393216)
# fp32;保留一整行的宽度、batch 缩到 1。
#
# (n,):
#   典型  (393216,)  原始单行 dim=393216:384 个块,grid-stride 循环跑多轮
#   规模  (786432,)  典型规模 ×2:dim0 393216->786432
#   规模  (1179648,)  典型规模 ×3:dim0 393216->1179648
#   泛化  (5000,)    尾部:5000 不整除 BLOCK,最后一块被掩码
#         (1,)      退化:单元素
SHAPES = ((128,), (100,), (1,))
# 原始程序是 fp32;hardsigmoid 只有除/加/clamp,半精度合法。
DTYPES = ("float32", "float16", "bfloat16")
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}
BLOCK = 1024
NUM_PROGRAMS = 128        # grid 比块数小,让 grid-stride 循环至少跑两轮


def ref(args, meta):
    """numpy 对照:clamp(x/6+0.5, 0, 1)。"""
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    out = np.asarray(args["out_ptr"])
    return {"out_ptr": np.clip(x / 6.0 + 0.5, 0.0, 1.0).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n = int(shape[0])
    if n <= 0:
        raise ValueError(f"n must be positive, got {shape}")

    # 原始输入是 [0,1);这里用 [-8, 8) 的对称网格覆盖 clamp 的两侧饱和区与线性区,
    # 1/8 的步长在半精度里精确可表示。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (rng.integers(-64, 64, n, dtype=np.int16) / 8.0).astype(_HOST_DTYPE[dtype])
    # 语义边界: -8(下饱和)、0(输出恰 0.5)、8(上饱和)。
    x[0] = -8.0
    if n > 1:
        x[1] = 0.0
    if n > 2:
        x[2] = 8.0

    out_dtype = np.float32 if dtype == "bfloat16" else np.dtype(dtype)
    args = {"x_ptr": x, "out_ptr": np.zeros(n, dtype=out_dtype), "n_elements": np.int32(n)}
    meta = {"BLOCK_SIZE": BLOCK}
    grid = (min(NUM_PROGRAMS, (n + BLOCK - 1) // BLOCK),)
    case = {"args": args, "meta": meta, "grid": grid, "outputs": ("out_ptr",),
            "expected": ref(args, meta)}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {"x_ptr": "bfloat16", "out_ptr": "bfloat16"}
        case["comparison"] = {"out_ptr": {"comparator": "allclose", "exact": False,
                                          "rtol": 5e-3, "atol": 5e-3, "equal_nan": True}}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, hardsigmoid_kernel, DTYPES,
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
