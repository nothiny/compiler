"""final_mean_kernel: 归约收尾,把 f64 部分和按 f32 精度折算成均值。

模式: 单 program 标量 kernel:n_elements 以 int64 传入,和先 cast 成 f32,
除法也在 f32 里做,最后按 constexpr OUT_DTYPE 存出。与 finalize_mean 的区别
是这里显式固定了 f32 中间精度(混合精度收尾的写法)。

文件只有两层:
  ① final_mean_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/final_mean_kernel', "group": 'basic', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'memory.load', 'memory.store']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 144718, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "a40f46c441b88ff07ee9cf42a34b5f7ef5ef73c2090a3fc75d7907f48e5cc520"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def _final_mean_kernel(sum_ptr, out_ptr, n_elements: tl.int64, OUT_DTYPE: tl.constexpr):
    s = tl.load(sum_ptr)
    s = tl.cast(s, tl.float32)
    n = tl.cast(n_elements, tl.float32)
    mean = s / n
    tl.store(out_ptr, tl.cast(mean, OUT_DTYPE))

# ------------------------------------------------------------------ ② case 层
# 典型用法:同 finalize_mean,MSE 类 loss 的收尾段。原始输入 (32768, 32768)
# fp32,n_elements = 32768*32768 = 1073741824,int64 下标。
#
# (n_elements,):
#   典型  (1073741824,)  原始总元素数:batch 32768 行 x 32768 列
#   规模  (2147483648,)  典型规模 ×2:dim0 1073741824->2147483648
#   规模  (3221225472,)  典型规模 ×3:dim0 1073741824->3221225472
#   泛化  (32768,)       单行:只缩小"批"维度
#         (1,)           退化:n=1
SHAPES = ((128,), (1,))
# kernel 内部固定 f32 中间精度(s = cast(f32), mean = s / cast(f32)),再用
# OUT_DTYPE 存出;声明 f64 输出只会把 f32 的结果装进 f64,测不出精度,故只声明 f32。
DTYPES = ('float32', 'float16', 'bfloat16')


def ref(args, meta):
    """numpy 对照:遵循 kernel 的 f32 中间精度,再按 OUT_DTYPE 存出。"""
    s = np.float32(args["sum_ptr"][0])
    n = np.float32(np.int64(args["n_elements"]))
    out = np.asarray(args["out_ptr"])
    return {"out_ptr": np.float32(s / n).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n = int(shape[0])
    if n <= 0:
        raise ValueError(f"n_elements must be positive, got {shape}")

    from case_utils import fast_rng
    rng = fast_rng(seed)
    sums = (rng.uniform(0.25, 0.4, 1) * float(n)).astype(np.float32)
    if n == 1:
        sums[:] = 1.5
    args = {"sum_ptr": sums.astype(np.float64), "out_ptr": np.zeros(1, dtype=np.float32),
            "n_elements": np.int64(n)}
    meta = {"OUT_DTYPE": tl.float32}
    return {"args": args, "meta": meta, "grid": (1,), "outputs": ("out_ptr",),
            "expected": ref(args, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, _final_mean_kernel, DTYPES,
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
