"""ranked_distribution_kernel: 从 ~/ops 仓库复制(extra @ ops),保留其已验证的 case 层。

模式: args.runtime_scalar、cast.to、creation.arange、creation.where、dtype.int32、memory.load、memory.store、reduce.reduce_or.axis0、reduce.xor_sum.axis0、selection.gather。load/store 没有掩码,SHAPES 全部满足整除约束。constexpr 参数: N。

文件只有两层:
  ① ranked_distribution_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/ranked_distribution_semantic', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'cast.to', 'creation.arange', 'creation.where', 'dtype.int32', 'memory.load', 'memory.store', 'reduce.reduce_or.axis0', 'reduce.xor_sum.axis0', 'selection.gather', 'selection.sort', 'selection.topk', 'shape.flip']}
SOURCE = {"operator": "basic/ranked_distribution.py", "case_family": "ranked_selection"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def ranked_distribution_kernel(X,Y,Flags,Ranked,N:tl.constexpr):
    i=tl.arange(0,N)
    x=tl.load(X+i)
    ordered=tl.sort(x,descending=False)
    ranked=tl.flip(ordered,0)
    # A cyclic permutation retains all scores but changes their positions.
    rotated=tl.gather(ranked,(i+3)%N,axis=0)
    tl.store(Ranked+i,rotated)
    top=tl.topk(rotated,N//2)
    prob=tl.softmax(top,dim=0)
    tl.store(Y+tl.arange(0,N//2),prob)
    bits=tl.where(x>0,1 << (i%16),0).to(tl.int32)
    tl.store(Flags,tl.reduce_or(bits,0))
    tl.store(Flags+1,tl.xor_sum(bits,0))

# ------------------------------------------------------------------ ② case 层
# (shape,) 的角色:第一个是典型用法,其余是泛化/尾块/退化用例。
#   (16,)
#   (64,)
# DTYPES: float32 —— 原始用途的 dtype 在前;非法域(例如本机 Triton 只吃 fp32 的exp/sqrt/erf/atomic)的算子只声明合法的那一种。

SHAPES = [(16,), (64,)]
DTYPES = ('float32', 'float16', 'bfloat16')
PINNED_VALUES = {
    16: lambda n: np.array([2.0] * (n // 2) + [-.25 * (i + 1) for i in range(n // 2)], np.float32),
    64: lambda n: np.array([(i * i) * .0025 - 2 for i in range(n)], np.float32),
}
def ref(args, meta):
    x = args['X']; n = x.size
    top = np.sort(x.astype(np.float64))[::-1][:n // 2]
    p = np.exp(top - top.max()); p /= p.sum()
    bits = np.where(x > 0, 1 << (np.arange(n) % 16), 0).astype(np.int32)
    return {'Y': p.astype(np.float32), 'Ranked': np.roll(np.sort(x)[::-1], -3).copy(),
            'Flags': np.array([np.bitwise_or.reduce(bits), np.bitwise_xor.reduce(bits)], np.int32)}
def _make_case(shape=None, dtype=None, seed=0):
    shape = tuple(SHAPES[0] if shape is None else shape)
    dtype = DTYPES[0] if dtype is None else np.dtype(dtype).name
    if dtype not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype}; choose from {DTYPES}")
    if not (len(shape) == 1 and shape[0] >= 2 and shape[0] & (shape[0] - 1) == 0):
        raise ValueError(f"invalid shape {shape} for ranked_distribution_semantic")
    n = shape[0]
    if n not in PINNED_VALUES:
        raise ValueError(f"no pinned semantic distribution for {shape}")
    values = PINNED_VALUES[n](n)
    x = np.asarray(values, np.float32)[(np.arange(n) * 5 + 3) % n]
    args = {'X': x, 'Y': np.zeros(n // 2, np.float32), 'Flags': np.zeros(2, np.int32),
            'Ranked': np.zeros(n, np.float32)}
    return {'kernel': ranked_distribution_kernel, 'args': args, 'meta': {'N': n}, 'grid': (1,),
            'outputs': ('Y', 'Flags', 'Ranked'), 'expected': ref(args, {}),
            'comparison': {'Y': {'rtol': 2e-5, 'atol': 2e-6}, 'Flags': {'exact': True}, 'Ranked': {'exact': True}}}
def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化 + 白名单校验,委托 _make_case;比较策略集中在 case_utils。"""
    return _make_case(shape=shape, dtype=dtype, seed=seed)


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
