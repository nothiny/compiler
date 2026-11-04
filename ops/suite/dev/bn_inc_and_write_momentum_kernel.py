"""bn_inc_and_write_momentum_kernel: BatchNorm 的 num_batches_tracked 自增与 momentum 计算。

模式: 单个 program 的标量 kernel:atomic_add 把 num_batches_tracked 加一并取回旧值,
HAS_MOMENTUM 是 constexpr 分支 —— 有 momentum 就直接写它,没有就用
1/max(new, 1)(PyTorch 的 cumulative moving average 规则)。

文件只有两层:
  ① _bn_inc_and_write_momentum_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'medium/bn_inc_and_write_momentum_kernel', "group": 'medium', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'atomic.add', 'control.if_constexpr', 'math.maximum', 'memory.store']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 329275, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "417da621aa7ac38ba79daabab9095504b6ddce5c1327bfdf28c1aa6dbb218844"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def _bn_inc_and_write_momentum_kernel(num_batches_tracked_ptr, mom_out_ptr, momentum, HAS_MOMENTUM: tl.constexpr):
    old = tl.atomic_add(num_batches_tracked_ptr, 1)
    new = old + 1
    if HAS_MOMENTUM:
        mom = momentum
    else:
        mom = 1.0 / tl.maximum(new.to(tl.float32), 1.0)
    tl.store(mom_out_ptr + 0, mom.to(tl.float32))

# ------------------------------------------------------------------ ② case 层
# 典型用法:BN 前向的第一步(每个 step 只跑一次)。没有形状,shape 里唯一的数
# 是 num_batches_tracked 的初值,同时用它选 HAS_MOMENTUM 分支:
#   (0,) -> HAS_MOMENTUM=1(预置 momentum=0.1 的常规训练)
#   (5,) -> HAS_MOMENTUM=0(没有 momentum,按 1/new 衰减)
SHAPES = ((0,), (5,))
# 计数器是 int64、momentum 是 f32(PyTorch 的 BN buffer dtype),各一种。
DTYPES = ('float32', 'float16', 'bfloat16')
MOMENTUM = 0.1


def ref(args, meta):
    """numpy 对照:new = old + 1;有 momentum 用它,否则 1/max(new, 1)。"""
    old = int(np.asarray(args["num_batches_tracked_ptr"])[0])
    new = old + 1
    mom = (float(args["momentum"]) if meta["HAS_MOMENTUM"]
           else 1.0 / float(max(new, 1)))
    out = np.asarray(args["mom_out_ptr"])
    return {"mom_out_ptr": np.array(mom, dtype=out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    counter = int(shape[0])
    if counter < 0:
        raise ValueError(f"num_batches_tracked must be >= 0, got {shape}")

    args = {"num_batches_tracked_ptr": np.array([counter], np.int64),
            "mom_out_ptr": np.zeros(1, np.float32),
            "momentum": np.float32(MOMENTUM)}
    meta = {"HAS_MOMENTUM": counter > 0}
    return {"args": args, "meta": meta, "grid": (1,), "outputs": ("mom_out_ptr",),
            "expected": ref(args, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, _bn_inc_and_write_momentum_kernel, DTYPES,
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
