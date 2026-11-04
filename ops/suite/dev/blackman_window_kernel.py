"""blackman_window_kernel: 对称 Blackman 窗:0.42 - 0.5cos + 0.08cos。

模式: args.runtime_scalar, cast.to, control.if, creation.arange, math.cos, memory.store.masked。

文件只有两层:
  ① blackman_window_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/blackman_window_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "cast.to", "control.if", "creation.arange", "math.cos", "memory.store.masked"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/blackman_window_kernel.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def blackman_window_kernel(out_ptr, window_length, scale, LOW_PRECISION: tl.constexpr, BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(0).to(tl.int64)
    idx = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = idx < window_length
    dtype = out_ptr.dtype.element_ty
    if LOW_PRECISION:
        n = idx.to(dtype).to(tl.float32)
        x = (n * scale).to(dtype).to(tl.float32)
        c2 = tl.cos((x * 2.0).to(dtype).to(tl.float32)).to(dtype).to(tl.float32)
        c4 = tl.cos((x * 4.0).to(dtype).to(tl.float32)).to(dtype).to(tl.float32)
        t4 = (c4 * 0.08).to(dtype).to(tl.float32)
        t2 = (c2 * 0.5).to(dtype).to(tl.float32)
        term = (t4 - t2).to(dtype).to(tl.float32)
        val = (term + 0.42).to(dtype)
    else:
        n = idx.to(dtype)
        x = n * scale
        val = 0.08 * tl.cos(x * 4.0) - 0.5 * tl.cos(x * 2.0) + 0.42
        val = val.to(dtype)
    tl.store(out_ptr + idx, val, mask=mask)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (1210,)  workload x2:dim0 605->1210
#   规模  (1815,)  workload x3:dim0 605->1815
SHAPES = ((17,), (122,))
DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 L=int(args["window_length"]);n=np.arange(L,dtype=np.float32);return {"out_ptr":(0.42-0.5*np.cos(2*np.pi*n/(L-1))+0.08*np.cos(4*np.pi*n/(L-1))).astype(np.float32)}

def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=20260901):
 from case_utils import fast_rng
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 L=max(2,N);args={"out_ptr":np.asarray(np.full(L,-7.)),"window_length":L,"scale":np.pi/(L-1)};meta={"LOW_PRECISION":False,"BLOCK_SIZE":128};grid=((L+127)//128,)
 outputs=('out_ptr',);return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0001, "atol": 0.0001, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, blackman_window_kernel, DTYPES,
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
