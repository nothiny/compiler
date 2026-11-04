"""control_flow: 运行时分支 + constexpr 分支 + 静态循环的组合。

模式: 带掩码 load,`if flag > 0` 是运行时标量分支(取 x 或 -x),`if SQUARE` 是
constexpr 分支,y = y*y,随后 tl.static_range(STEPS) 的静态展开循环加
(step+1),最后带掩码 store。三种控制流形状各自对应一个 case。

文件只有两层:
  ① control_flow_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/control_flow', "group": 'basic', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.if_runtime', 'control.loop_constexpr', 'memory.load.masked', 'memory.store.masked', 'creation.arange']}
COPIED_FROM = {'repo': '~/ops (basic)', 'note': 'base operator; semantic boundary cases merged into its case layer (no protected-dir constraint here)', 'validated': True}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit(do_not_specialize=["flag"])
def control_flow_kernel(x_ptr, out_ptr, n, flag, SQUARE: tl.constexpr, STEPS: tl.constexpr, BLOCK: tl.constexpr):
    i = tl.program_id(0) * BLOCK + tl.arange(0, BLOCK)
    x = tl.load(x_ptr + i, mask=i < n, other=0.0).to(tl.float32)
    if flag > 0:
        y = x
    else:
        y = -x
    if SQUARE:
        y = y * y
    for step in tl.static_range(STEPS):
        y = y + (step + 1)
    tl.store(out_ptr + i, y, mask=i < n)

# ------------------------------------------------------------------ ② case 层
# 典型用法:带门控的逐元素算子(gating 常以标量或开关传入)。三个 shape 分别
# 覆盖:直通分支 + 静态循环多次、取负分支 + 平方分支、循环不进入。
#
# (n,):
#   典型  (257,)     flag>0 直通、SQUARE=0、STEPS=3:尾部 1 个 lane 被掩码
#   规模  (514,)     典型规模 ×2:dim0 257->514;flag>0、SQUARE=1、STEPS=3(此前未覆盖的组合)
#   泛化  (522,)     flag<0 取负、SQUARE=1(常量分支的另一侧)、STEPS=2
#         (128,)     STEPS=0:静态循环不进入,长度恰好整除 BLOCK
SHAPES = ((128,),)
# kernel 内部先转 f32,半精度输入合法;fp16 是第一轮的真实用法。
DTYPES = ("float32", "float16", "bfloat16")
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}
BLOCK = 128
# 每个 shape 对应的控制流配置(flag 是运行时标量,SQUARE/STEPS 是 constexpr)。
_CONTROL = {(257,): (1, 0, 3), (514,): (1, 1, 3), (522,): (-1, 1, 2), (128,): (1, 0, 0)}


def ref(args, meta):
    """numpy 对照:按同一份 flag/SQUARE/STEPS 配置算。"""
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    n = int(args["n"])
    x = x[:n]
    y = x if int(args["flag"]) > 0 else -x
    if int(meta["SQUARE"]):
        y = y * y
    for step in range(int(meta["STEPS"])):
        y = y + (step + 1)
    out = np.asarray(args["out_ptr"])
    return {"out_ptr": y.astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n = int(shape[0])
    if n <= 0:
        raise ValueError(f"n must be positive, got {shape}")
    flag, square, steps = _CONTROL[(n,)]

    # 原始输入是 [-1,1) 的均匀分布;取 1/8 网格以覆盖正负号,并在 fp16/bf16 里
    # 精确可表示(平方与加常数都在整数网格上,不会引入舍入差)。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (rng.integers(-8, 8, n, dtype=np.int16) / 8.0).astype(_HOST_DTYPE[dtype])
    # 语义边界:0(取负与平方都退化)、-1(取负/平方后变成 +1)、1。
    x[0] = 0.0
    if n > 1:
        x[1] = -1.0
    if n > 2:
        x[2] = 1.0

    args = {"x_ptr": x, "out_ptr": np.zeros(n, dtype=np_dtype_of(dtype)),
            "n": np.int32(n), "flag": np.int32(flag)}
    meta = {"SQUARE": square, "STEPS": steps, "BLOCK": BLOCK}
    case = {"args": args, "meta": meta, "grid": ((n + BLOCK - 1) // BLOCK,),
            "outputs": ("out_ptr",), "expected": ref(args, meta)}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {"x_ptr": "bfloat16", "out_ptr": "bfloat16"}
        case["comparison"] = {"out_ptr": {"comparator": "allclose", "exact": False,
                                          "rtol": 5e-3, "atol": 5e-3, "equal_nan": True}}
    return case


def np_dtype_of(dtype):
    return np.float32 if dtype == "bfloat16" else np.dtype(dtype)


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, control_flow_kernel, DTYPES,
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
