"""selu_kernel_supreme: SELU,按块内符号分布选三条分支。

模式: 每个 program 用 tl.static_range(VEC) 展开 VEC 个块;每块先看 tl.min(x):
全部非负就整块 scale*x,否则看 tl.max(x):全部非正就整块 scale_alpha*(exp(x)-1),
正负混合才走逐元素 tl.where。core 是 tl.multiple_of / max_contiguous 的向量化提示
与 cache_modifier='.cg' 的缓存提示。

文件只有两层:
  ① selu_kernel_supreme   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/selu_kernel_supreme', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'hint.max_contiguous', 'hint.multiple_of', 'math.exp', 'memory.load.masked', 'memory.store.masked', 'control.if_runtime', 'control.loop_constexpr']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 44215, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "2ddadd161791bfdf6560325853cf75c212ee96c2b08696df1eacd1dd058b2e60"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def selu_kernel_supreme(x_ptr, y_ptr, n_elements, SCALE: tl.constexpr, ALPHA: tl.constexpr, SCALE_ALPHA: tl.constexpr, BLOCK_SIZE: tl.constexpr, VEC: tl.constexpr):
    tl.static_assert(BLOCK_SIZE % 128 == 0)
    pid = tl.program_id(0)
    ar = tl.arange(0, BLOCK_SIZE)
    base = pid * BLOCK_SIZE * VEC
    offs_hint = base + ar
    tl.multiple_of(offs_hint, 128)
    tl.max_contiguous(offs_hint, 128)
    for i in tl.static_range(VEC):
        offsets = base + i * BLOCK_SIZE + ar
        mask = offsets < n_elements
        x = tl.load(x_ptr + offsets, mask=mask, other=0.0, cache_modifier='.cg')
        xmin = tl.min(x)
        if xmin >= 0.0:
            y = SCALE * x
        else:
            xmax = tl.max(x)
            if xmax <= 0.0:
                y = SCALE_ALPHA * (tl.exp(x) - 1.0)
            else:
                n = tl.minimum(x, 0.0)
                y = SCALE * x + SCALE_ALPHA * (tl.exp(n) - 1.0) - SCALE * n
        tl.store(y_ptr + offsets, y, mask=mask)

# ------------------------------------------------------------------ ② case 层
# 典型用法:激活层 SELU。原始 (4096, 393216) fp32;这里保留一整行宽度、batch 缩到
# 1。三个 shape 分别覆盖三条分支(全正 / 全负 / 正负混合),因为它们由块内
# tl.min/tl.max 决定,必须用不同的数据分布才能都走到。
#
# (n,):
#   典型  (393216,)  全正数据  -> 整块 scale*x 分支
#   规模  (786432,)  典型规模 ×2:dim0 393216->786432;正负混合 -> where 分支
#   泛化  (4096,)    全负数据  -> 整块 scale_alpha*(exp(x)-1) 分支
#         (4097,)    正负混合  -> 逐元素 where 分支(且不整除 BLOCK)
SHAPES = ((393216,), (4097,))
# 原始程序是 fp32;tl.exp 在本机 Triton 上只接受 fp32,合法域只有 fp32。
DTYPES = ('float32',)
_SCALE = 1.0507009873554805
_ALPHA = 1.6732632423543772
_REGIME = {393216: "pos", 786432: "mixed", 4096: "neg", 4097: "mixed"}   # shape -> 数据符号分布


def ref(args, meta):
    """numpy 对照:float64 的 SELU(pos 分支与 neg 分支在数学上等价于 where)。"""
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    out = np.asarray(args["y_ptr"])
    y = np.where(x > 0, _SCALE * x, _SCALE * _ALPHA * (np.exp(x) - 1.0))
    return {"y_ptr": y.astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n = int(shape[0])
    if n <= 0:
        raise ValueError(f"n must be positive, got {shape}")
    regime = _REGIME[n]

    from case_utils import fast_rng
    rng = fast_rng(seed)
    # 取值落在 1/8 网格上,量级 [-8, 8);按 regime 决定符号:全正、全负、或正负混合。
    raw = (rng.integers(1, 65, n, dtype=np.int16) / 8.0).astype(np.float32)
    x = raw if regime == "pos" else (-raw if regime == "neg" else
                                     np.where(np.arange(n) % 2 == 0, raw, -raw).astype(np.float32))
    # 语义边界(x 恰为 0:走负分支,输出 0)。
    x[0] = 0.0

    args = {"x_ptr": x, "y_ptr": np.full(n, -7.0, np.float32), "n_elements": np.int32(n)}
    meta = {"SCALE": _SCALE, "ALPHA": _ALPHA, "SCALE_ALPHA": _SCALE * _ALPHA,
            "BLOCK_SIZE": 1024, "VEC": 2}
    return {"args": args, "meta": meta, "grid": ((n + 1024 * 2 - 1) // (1024 * 2),),
            "outputs": ("y_ptr",), "expected": ref(args, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, selu_kernel_supreme, DTYPES,
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
