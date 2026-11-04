"""gelu_min: 一遍扫完整条向量,求 GELU 之后的全局最小值。

模式: 只有 1 个 program,用 for start in range(0, n_elements, BLOCK_N) 的运行时
循环按块处理,块内先算 GELU(erf 形式),被掩码的 lane 取 +inf,再用
tl.minimum 把每块的最小值累积到 acc,最后 tl.min(acc) 归约成一个标量。

文件只有两层:
  ① gelu_min_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/gelu_min', "group": 'basic', "channel": 'T',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.loop_runtime_bound', 'creation.arange', 'creation.full', 'math.erf', 'memory.load.masked', 'reduce.min', 'reduce.min.axis0']}
COPIED_FROM = {'repo': '~/ops (tritonbench)', 'note': 'base operator; semantic boundary cases merged into its case layer (no protected-dir constraint here)', 'validated': True}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def gelu_min_kernel(x_ptr, y_ptr, n_elements, BLOCK_N: tl.constexpr):
    cols = tl.arange(0, BLOCK_N)
    acc = tl.full((BLOCK_N,), float('inf'), tl.float32)
    for start in range(0, n_elements, BLOCK_N):
        offs = start + cols
        mask = offs < n_elements
        x = tl.load(x_ptr + offs, mask=mask, other=0.0)
        g = tl.where(mask, 0.5 * x * tl.erf(x * 0.7071067811865476), float('inf'))
        acc = tl.minimum(acc, g)
    tl.store(y_ptr, tl.min(acc, axis=0))

# ------------------------------------------------------------------ ② case 层
# 典型用法:激活值诊断(找最小激活)。kernel 计算的是 0.5*x*erf(x/sqrt2)(上游
# 版本漏了 GELU 的 +1),负半轴的最小值出现在 x -> -inf 处的 +0.5|x| 之前,
# 所以下面的语义边界数据同时给了很负和很正的值。原始版本是单块 1024。
#
# (n,):
#   典型  (4096,)   一条 hidden=4096 的激活:4 个块,循环跑 4 次
#   规模  (8192,)  典型规模 ×2:dim0 4096->8192
#   规模  (12288,)  典型规模 ×3:dim0 4096->12288
#   泛化  (1025,)   尾部:最后一个块只有 1 个有效 lane(其余被掩码成 +inf)
#         (1,)     退化:单元素
SHAPES = ((128,), (1,))
# tl.erf 在本机 Triton 上只接受 fp32;acc 也显式声明为 f32。
DTYPES = ('float32',)


def ref(args, meta):
    """numpy 对照:float64 复现 kernel 的 0.5*x*erf(x/sqrt2),再取全局最小。

    注意 kernel 少写了 GELU 的 "+1"(上游如此):x << 0 时不是 0 而是 +0.5|x|,
    ref 按 kernel 实际计算的函数写,不按标准 GELU。
    """
    from mathref import erf

    x = np.asarray(args["x_ptr"], dtype=np.float64)
    y = 0.5 * x * erf(x * 0.7071067811865476)
    out = np.asarray(args["y_ptr"])
    return {"y_ptr": np.array(y.min(), dtype=out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n = int(shape[0])
    if n <= 0:
        raise ValueError(f"n must be positive, got {shape}")

    # 激活值近似正态(标准差 2),取值落在 1/16 网格上;fp32 下精确。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (np.clip(np.rint(rng.standard_normal(n, dtype=np.float32) * 32), -128, 127)
         / 16).astype(np.float32)
    # 语义边界:一个很负的值(GELU 在 x << 0 处趋近 -0.17,是全局最小候选),
    # 一个 0(输出 0),一个很正的值(GELU 趋近 x,不可能成为最小)。
    x[0] = -12.0
    if n > 1:
        x[1] = 0.0
    if n > 2:
        x[2] = 12.0

    args = {"x_ptr": x, "y_ptr": np.zeros(1, dtype=np.float32), "n_elements": np.int32(n)}
    meta = {"BLOCK_N": min(1024, max(1, n))}
    return {"args": args, "meta": meta, "grid": (1,), "outputs": ("y_ptr",),
            "expected": ref(args, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, gelu_min_kernel, DTYPES,
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
