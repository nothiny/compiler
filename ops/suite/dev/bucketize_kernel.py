"""bucketize_kernel: bucketize:对每个输入在有序边界里二分找桶号(right 语义可切)。

模式: args.runtime_scalar, cast.to, control.for_range, control.if, creation.arange, creation.full, creation.where, creation.zeros, math.minimum, memory.load.masked, memory.load.other, memory.store.masked。

文件只有两层:
  ① bucketize_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/bucketize_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "cast.to", "control.for_range", "control.if", "creation.arange", "creation.full", "creation.where", "creation.zeros", "math.minimum", "memory.load.masked", "memory.load.other", "memory.store.masked"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/bucketize_kernel.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def bucketize_kernel(inp_ptr, boundaries_ptr, out_ptr, n_elements, n_boundaries, right: tl.constexpr, N_BOUNDARY_ITERS: tl.constexpr, BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(0).to(tl.int64)
    block_start = pid * BLOCK_SIZE
    offsets = block_start + tl.arange(0, BLOCK_SIZE)
    mask = offsets < n_elements
    inp_val = tl.load(inp_ptr + offsets, mask=mask, other=0.0)
    n_boundaries_i32 = tl.full([BLOCK_SIZE], n_boundaries, dtype=tl.int32)
    zero = tl.zeros([BLOCK_SIZE], dtype=tl.int32)
    lo = zero
    hi = n_boundaries_i32
    if right:
        for _ in range(N_BOUNDARY_ITERS):
            mid = tl.minimum((lo + hi) // 2, n_boundaries_i32 - 1)
            mid_val = tl.load(boundaries_ptr + mid)
            cond = mid_val <= inp_val
            lo = tl.where(cond, mid + 1, lo)
            hi = tl.where(cond, hi, mid)
        result = lo
    else:
        for _ in range(N_BOUNDARY_ITERS):
            mid = tl.minimum((lo + hi) // 2, n_boundaries_i32 - 1)
            mid_val = tl.load(boundaries_ptr + mid)
            cond = mid_val < inp_val
            lo = tl.where(cond, mid + 1, lo)
            hi = tl.where(cond, hi, mid)
        result = lo
    tl.store(out_ptr + offsets, result, mask=mask)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (1214,)  workload x2:dim0 607->1214
#   规模  (1821,)  workload x3:dim0 607->1821
SHAPES = ((17,), (126,))
DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 return {"out_ptr":np.searchsorted(args["boundaries_ptr"][:int(args["n_boundaries"])],args["inp_ptr"][:int(args["n_elements"])],side="right" if meta["right"] else "left").astype(np.int64)}

def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=20260901):
 from case_utils import fast_rng
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 B=max(4,min(64,N//2));bounds=np.sort(rng.normal(0,1,B)).astype(np.float32);args={"inp_ptr":np.asarray(rng.normal(0,1,N)),"boundaries_ptr":np.asarray(bounds),"out_ptr":np.asarray(np.full(N,-1),"int64"),"n_elements":N,"n_boundaries":B};meta={"right":True,"N_BOUNDARY_ITERS":B.bit_length(),"BLOCK_SIZE":128};grid=((N+127)//128,)
 outputs=('out_ptr',);return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0001, "atol": 0.0001, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, bucketize_kernel, DTYPES,
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
