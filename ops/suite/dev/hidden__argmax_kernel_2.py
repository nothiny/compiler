"""argmax_kernel_2: 两段 argmax 的收尾:partial (值, 下标) 对里选全局最大。

模式: args.runtime_scalar, control.if, creation.arange, memory.load.masked, memory.load.other, memory.store, reduce.argmax。

文件只有两层:
  ① argmax_kernel_2   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/argmax_kernel_2", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "control.if", "creation.arange", "memory.load.masked", "memory.load.other", "memory.store", "reduce.argmax"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/argmax_kernel_2.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def argmax_kernel_2(mid_value, mid_index, out, mid_size, BLOCK_MID: tl.constexpr):
    offset = tl.arange(0, BLOCK_MID)
    mid_ptrs = mid_value + offset
    mask = offset < mid_size
    _inl_1_get_dtype_min_dtype = mid_value.type.element_ty
    _inl_1_get_dtype_min_result = 0
    'get a value which is less that all other values of that dtype'
    _inl_1_get_dtype_min_dtype_ = _inl_1_get_dtype_min_dtype
    if _inl_1_get_dtype_min_dtype_.is_floating():
        _inl_1_get_dtype_min_value: tl.constexpr = float('-inf')
        _inl_1_get_dtype_min_result = _inl_1_get_dtype_min_value
    elif _inl_1_get_dtype_min_dtype_.is_int_signed():
        _inl_1_get_dtype_min_width: tl.constexpr = _inl_1_get_dtype_min_dtype_.int_bitwidth
        _inl_1_get_dtype_min_value: tl.constexpr = -1 * 2 ** (_inl_1_get_dtype_min_width - 1)
        _inl_1_get_dtype_min_result = _inl_1_get_dtype_min_value
    elif _inl_1_get_dtype_min_dtype_.is_int_unsigned():
        _inl_1_get_dtype_min_value: tl.constexpr = 0
        _inl_1_get_dtype_min_result = _inl_1_get_dtype_min_value
    min_value = _inl_1_get_dtype_min_result
    mid_val = tl.load(mid_ptrs, mask=mask, other=min_value)
    index_val = tl.argmax(mid_val, axis=0)
    mid_index_ptrs = mid_index + index_val
    out_val = tl.load(mid_index_ptrs)
    tl.store(out, out_val)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (3070,)  workload x2:dim0 1535->3070
#   规模  (4605,)  workload x3:dim0 1535->4605
SHAPES = ((17,), (126,))
DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 k=int(args["mid_size"]);j=int(np.argmax(args["mid_value"][:k]));return {"out":np.asarray([args["mid_index"][j]],np.int64)}

def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=20260901):
 from case_utils import fast_rng
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 K=max(1,(N+127)//128);args={"mid_value":np.asarray(rng.normal(0,.8,K)),"mid_index":np.asarray(np.arange(K)*128,"int64"),"out":np.asarray(np.full(1,-1),"int64"),"mid_size":K};meta={"BLOCK_MID":1<<(K-1).bit_length()};grid=(1,)
 outputs=('out',);return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0001, "atol": 0.0001, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, argmax_kernel_2, DTYPES,
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
