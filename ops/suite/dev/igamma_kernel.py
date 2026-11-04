"""igamma_kernel: 正则化下不完全伽马 P(a,x):Lanczos log-gamma + 级数/连分式。

模式: args.runtime_scalar, cast.to, control.for_range, creation.arange, creation.where, math.abs, math.exp, math.log, math.maximum, math.minimum, math.sin, memory.load.masked, memory.store.masked。

文件只有两层:
  ① igamma_kernel_   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/igamma_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "cast.to", "control.for_range", "creation.arange", "creation.where", "math.abs", "math.exp", "math.log", "math.maximum", "math.minimum", "math.sin", "memory.load.masked", "memory.store.masked"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/igamma_kernel.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def igamma_kernel_(a_ptr, x_ptr, out_ptr, n_elements, BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(axis=0)
    block_start = pid * BLOCK_SIZE
    offsets = block_start + tl.arange(0, BLOCK_SIZE)
    mask = offsets < n_elements
    a = tl.load(a_ptr + offsets, mask=mask)
    x = tl.load(x_ptr + offsets, mask=mask)
    a_f32 = a.to(tl.float32)
    x_f32 = x.to(tl.float32)
    result_zero = x_f32 == 0.0
    pi = 3.141592653589793
    lanczos_g = 7.0
    reflect_mask = a_f32 < 0.5
    x_refl = tl.where(reflect_mask, 1.0 - a_f32, a_f32)
    z = x_refl - 1.0
    p = 0.9999999999998099 + 676.5203681218851 / (z + 1.0) + -1259.1392167224028 / (z + 2.0) + 771.3234287776531 / (z + 3.0) + -176.6150291621406 / (z + 4.0) + 12.507343278686905 / (z + 5.0) + -0.13857109526572012 / (z + 6.0) + 9.984369578019572e-06 / (z + 7.0) + 1.5056327351493116e-07 / (z + 8.0)
    sqrt_2pi = 2.5066282746310007
    t = z + lanczos_g + 0.5
    log_gamma_a = (z + 0.5) * tl.log(t) - t + tl.log(sqrt_2pi * p)
    log_gamma_a = tl.where(reflect_mask, tl.log(pi) - tl.log(tl.abs(tl.sin(pi * a_f32))) - log_gamma_a, log_gamma_a)
    log_ax = a_f32 * tl.log(x_f32) - x_f32 - log_gamma_a
    ax = tl.exp(log_ax)
    small_x = x_f32 < a_f32 + 1.0
    series_result = 1.0 / a_f32
    series_term = 1.0 / a_f32
    ap = a_f32
    for i in range(60):
        ap = ap + 1.0
        series_term = series_term * x_f32 / ap
        series_result = series_result + series_term
    series_res = ax * series_result
    fpmin = 1e-30
    b = x_f32 + 1.0 - a_f32
    c = b * 0.0 + 1e+30
    d = 1.0 / b
    h = d
    n = 1.0
    for i in range(60):
        an = -n * (n - a_f32)
        b = b + 2.0
        d = an * d + b
        d = tl.where(tl.abs(d) < fpmin, fpmin, d)
        c = b + an / c
        c = tl.where(tl.abs(c) < fpmin, fpmin, c)
        d = 1.0 / d
        delta = c * d
        h = h * delta
        n = n + 1.0
    cf_res = 1.0 - ax * h
    result = tl.where(result_zero, 0.0, tl.where(small_x, series_res, cf_res))
    result = tl.minimum(result, 1.0)
    result = tl.maximum(result, 0.0)
    result = result.to(a.dtype)
    tl.store(out_ptr + offsets, result, mask=mask)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (1302,)  workload x2:dim0 651->1302
#   规模  (1953,)  workload x3:dim0 651->1953
SHAPES = ((17,), (118,))
DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 import math
 a=args["a_ptr"].astype(np.float64);x=args["x_ptr"].astype(np.float64);term=1/a;s=term.copy()
 for k in range(1,100):term*=x/(a+k);s+=term
 from mathref import lgamma;y=np.exp(-x+a*np.log(x)-lgamma(a))*s;return {"out_ptr":y.astype(np.float32)}

def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=20260901):
 from case_utils import fast_rng
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 args={"a_ptr":np.asarray(rng.uniform(1,4,N)),"x_ptr":np.asarray(rng.uniform(.05,2,N)),"out_ptr":np.asarray(np.full(N,-7.)),"n_elements":N};meta={"BLOCK_SIZE":128};grid=((N+127)//128,)
 outputs=('out_ptr',);return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0001, "atol": 0.0001, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, igamma_kernel_, DTYPES,
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
