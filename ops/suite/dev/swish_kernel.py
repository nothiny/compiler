"""swish_kernel: 手写组合。

模式: args.runtime_scalar、cast.to、control.while、creation.arange、creation.where、dtype.float32、math.exp、memory.load、memory.load.masked、memory.load.other。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。constexpr 参数: BLOCK_SIZE。

文件只有两层:
  ① swish_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/swish_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'cast.to', 'control.while', 'creation.arange', 'creation.where', 'dtype.float32', 'math.exp', 'memory.load', 'memory.load.masked', 'memory.load.other', 'memory.store', 'memory.store.masked']}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def swish_kernel(x_ptr, out_ptr, n_elements, BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(0)
    num_prog = tl.num_programs(0)
    block_start = pid * BLOCK_SIZE
    while block_start < n_elements:
        offsets = block_start + tl.arange(0, BLOCK_SIZE)
        mask = offsets < n_elements
        x = tl.load(x_ptr + offsets, mask=mask, other=0.0)
        xf = x.to(tl.float32)
        pos = xf >= 0.0
        e = tl.where(pos, tl.exp(-xf), tl.exp(xf))
        denom = 1.0 + e
        sig = tl.where(pos, 1.0 / denom, e / denom)
        y = (xf * sig).to(x.dtype)
        tl.store(out_ptr + offsets, y, mask=mask)
        block_start += num_prog * BLOCK_SIZE

# ------------------------------------------------------------------ ② case 层
# (shape,) 的角色:第一个是典型用法,其余是泛化/尾块/退化用例。
#   (1024,)
#   (5000,)
# DTYPES: float32 —— 原始用途的 dtype 在前;非法域(例如本机 Triton 只吃 fp32 的exp/sqrt/erf/atomic)的算子只声明合法的那一种。
#   规模    (2048,)  典型规模 ×2:dim0 1024->2048
#   规模    (3072,)  典型规模 ×3:dim0 1024->3072

SHAPES = ((128,), (100,))
DTYPES = ('float32', 'float16', 'bfloat16')
def ref(args, meta):
        import numpy as np

        x = np.asarray(args['x_ptr'], dtype=np.float64)
        sig = 1.0 / (1.0 + np.exp(-x))
        return {'out_ptr': (x * sig).astype(np.asarray(args['out_ptr']).dtype)}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=20261019):
        import numpy as np

        n = int(shape[0])
        from case_utils import fast_rng
        rng = fast_rng(seed)
        x = rng.uniform(-30.0, 30.0, n).astype(np.float32)
        args = {'x_ptr': x, 'out_ptr': np.zeros(n, np.float32), 'n_elements': np.int32(n)}
        meta = {'BLOCK_SIZE': 1024}
        grid = (3,)   # 3 个 program 而非 cdiv(n,B):强制 while 网格跨步多轮执行
        return {"args": args, "meta": meta, "grid": grid, "outputs": ('out_ptr',), "expected": ref(args, meta)}
def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化 + 白名单校验,委托 _make_case;比较策略集中在 case_utils。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, swish_kernel, DTYPES,
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
