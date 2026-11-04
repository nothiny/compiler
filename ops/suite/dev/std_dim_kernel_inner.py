"""std_dim_kernel_inner: 沿 dim 的标准差:两遍均值/方差,带 correction。

模式: args.runtime_scalar, cast.to, control.for_range, control.if, creation.arange, creation.where, creation.zeros, math.maximum, math.sqrt, memory.load.masked, memory.load.other, memory.store, reduce.sum。

文件只有两层:
  ① _std_dim_kernel_inner   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/std_dim_kernel_inner", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "cast.to", "control.for_range", "control.if", "creation.arange", "creation.where", "creation.zeros", "math.maximum", "math.sqrt", "memory.load.masked", "memory.load.other", "memory.store", "reduce.sum"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/std_dim_kernel_inner.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit(do_not_specialize=['correction'])
def _std_dim_kernel_inner(Out, X, M, N, correction, TILE_N: tl.constexpr, ONE_TILE_PER_CTA: tl.constexpr):
    pid_m = tl.program_id(0)
    if ONE_TILE_PER_CTA:
        n_offsets = tl.arange(0, TILE_N)
        mask = n_offsets < N
        x = tl.load(X + pid_m * N + n_offsets, mask=mask, other=0.0).to(tl.float32)
        mean = tl.sum(x, axis=0) / N
    else:
        sum_acc = tl.zeros((TILE_N,), dtype=tl.float32)
        for start_n in range(0, N, TILE_N):
            n_offsets = start_n + tl.arange(0, TILE_N)
            mask = n_offsets < N
            x = tl.load(X + pid_m * N + n_offsets, mask=mask, other=0.0).to(tl.float32)
            sum_acc += x
        mean = tl.sum(sum_acc, axis=0) / N
    if ONE_TILE_PER_CTA:
        n_offsets = tl.arange(0, TILE_N)
        mask = n_offsets < N
        x = tl.load(X + pid_m * N + n_offsets, mask=mask, other=0.0).to(tl.float32)
        diff = x - mean
        sq_sum = tl.sum(tl.where(mask, diff * diff, 0.0), axis=0)
    else:
        sq_acc = tl.zeros((TILE_N,), dtype=tl.float32)
        for start_n in range(0, N, TILE_N):
            n_offsets = start_n + tl.arange(0, TILE_N)
            mask = n_offsets < N
            x = tl.load(X + pid_m * N + n_offsets, mask=mask, other=0.0).to(tl.float32)
            diff = x - mean
            sq_acc += tl.where(mask, diff * diff, 0.0)
        sq_sum = tl.sum(sq_acc, axis=0)
    denom = N - correction
    var = sq_sum / tl.maximum(denom, 1e-12)
    std_dev = tl.sqrt(tl.maximum(var, 0.0))
    tl.store(Out + pid_m, std_dev.to(Out.dtype.element_ty), mask=pid_m < M)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (1650,)  workload x2:dim0 825->1650
#   规模  (2475,)  workload x3:dim0 825->2475
SHAPES = ((17,), (114,))
DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 M=int(args["M"]);C=int(args["N"]);x=args["X"].reshape(M,C);return {"Out":np.std(x,axis=1,ddof=int(args["correction"])).astype(np.float32)}

def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=20260901):
 from case_utils import fast_rng
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 M=3;C=max(2,N//M);args={"Out":np.asarray(np.full(M,-7.)),"X":np.asarray(rng.normal(0,.8,M*C)),"M":M,"N":C,"correction":1};meta={"TILE_N":128,"ONE_TILE_PER_CTA":False};grid=(M,)
 outputs=('Out',);return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0001, "atol": 0.0001, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, _std_dim_kernel_inner, DTYPES,
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
