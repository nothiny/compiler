"""norm__l2_norm_kernel: 向量 L2 范数:尺度稳定的两遍平方和。

模式: args.runtime_scalar, cast.to, control.for_range, creation.arange, creation.full, creation.where, creation.zeros, math.abs, math.maximum, math.sqrt, memory.load.masked, memory.store.masked, reduce.max, reduce.sum。

文件只有两层:
  ① l2_norm_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/norm__l2_norm_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "cast.to", "control.for_range", "creation.arange", "creation.full", "creation.where", "creation.zeros", "math.abs", "math.maximum", "math.sqrt", "memory.load.masked", "memory.store.masked", "reduce.max", "reduce.sum"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/norm__l2_norm_kernel.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def l2_norm_kernel(X, Out, M, N, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr):
    _inl_1_program_id_result = tl.program_id(0).to(tl.int64)
    pid = _inl_1_program_id_result.to(tl.int64) * BLOCK_M + tl.arange(0, BLOCK_M)[:, None]
    X = X + pid * N
    Out = Out + pid
    row_mask = pid < M
    scale = tl.full((BLOCK_M,), 0.0, tl.float32)
    has_nan = tl.full((BLOCK_M,), 0, tl.int32)
    for off in range(0, N, BLOCK_N):
        cols = off + tl.arange(0, BLOCK_N)[None, :]
        a = tl.load(X + cols, row_mask & (cols < N), other=0.0).to(tl.float32)
        scale = tl.maximum(scale, tl.max(tl.abs(a), 1))
        has_nan |= tl.sum((a != a).to(tl.int32), 1) > 0
    safe_scale = tl.where(scale > 0.0, scale, 1.0)
    squares = tl.zeros([BLOCK_M, BLOCK_N], dtype=tl.float32)
    for off in range(0, N, BLOCK_N):
        cols = off + tl.arange(0, BLOCK_N)[None, :]
        a = tl.load(X + cols, row_mask & (cols < N), other=0.0).to(tl.float32)
        scaled = tl.div_rn(a, safe_scale[:, None])
        squares += scaled * scaled
    out = scale * tl.sqrt(tl.sum(squares, axis=1))
    out = tl.where(scale == float('inf'), scale, out)
    out = tl.where(has_nan != 0, float('nan'), out)
    tl.store(Out, out[:, None], row_mask)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (1482,)  workload x2:dim0 741->1482
#   规模  (2223,)  workload x3:dim0 741->2223
SHAPES = ((17,), (106,))
DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 x=args["X"].astype(np.float64).reshape(int(args["M"]),int(args["N"]));return {"Out":np.sqrt(np.sum(x*x,axis=1)).astype(args["Out"].dtype)}

def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=20260901):
 from case_utils import fast_rng
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 M=3;C=max(2,N//M);args={"X":np.asarray(rng.normal(0,.8,M*C)),"Out":np.asarray(np.full(M,-7.)),"M":M,"N":C};meta={"BLOCK_M":2,"BLOCK_N":128};grid=((M+1)//2,)
 outputs=('Out',);return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0001, "atol": 0.0001, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, l2_norm_kernel, DTYPES,
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
