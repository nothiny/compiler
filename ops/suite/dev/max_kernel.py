"""max_kernel: 行最大值 + 首个下标(块循环 + return_indices)。

模式: args.runtime_scalar, cast.to, control.for_range, control.if, creation.arange, creation.full, creation.where, creation.zeros, memory.load.masked, memory.load.other, memory.store.masked, reduce.max。

文件只有两层:
  ① max_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/max_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "cast.to", "control.for_range", "control.if", "creation.arange", "creation.full", "creation.where", "creation.zeros", "memory.load.masked", "memory.load.other", "memory.store.masked", "reduce.max"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/max_kernel.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def max_kernel(inp, out_value, out_index, M, N, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr):
    pid_m = tl.program_id(0).to(tl.int64)
    m_offset = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    dtype = inp.type.element_ty
    acc_type = tl.float32 if dtype is tl.bfloat16 else dtype
    _inl_2_get_dtype_min_dtype = dtype
    _inl_2_get_dtype_min_result = 0
    'get a value which is less that all other values of that dtype'
    _inl_2_get_dtype_min_dtype_ = _inl_2_get_dtype_min_dtype
    if _inl_2_get_dtype_min_dtype_.is_floating():
        _inl_2_get_dtype_min_value: tl.constexpr = float('-inf')
        _inl_2_get_dtype_min_result = _inl_2_get_dtype_min_value
    elif _inl_2_get_dtype_min_dtype_.is_int_signed():
        _inl_2_get_dtype_min_width: tl.constexpr = _inl_2_get_dtype_min_dtype_.int_bitwidth
        _inl_2_get_dtype_min_value: tl.constexpr = -1 * 2 ** (_inl_2_get_dtype_min_width - 1)
        _inl_2_get_dtype_min_result = _inl_2_get_dtype_min_value
    elif _inl_2_get_dtype_min_dtype_.is_int_unsigned():
        _inl_2_get_dtype_min_value: tl.constexpr = 0
        _inl_2_get_dtype_min_result = _inl_2_get_dtype_min_value
    min_value = _inl_2_get_dtype_min_result
    result_value = tl.full([BLOCK_M], value=min_value, dtype=acc_type)
    result_index = tl.zeros([BLOCK_M], dtype=tl.int64)
    for i in range(0, N, BLOCK_N):
        n_offset = i + tl.arange(0, BLOCK_N)
        offset = m_offset[:, None] * N + n_offset[None, :]
        mask = m_offset[:, None] < M and n_offset[None, :] < N
        inp_ptrs = inp + offset
        inp_vals = tl.load(inp_ptrs, mask=mask, other=min_value)
        (max_value, max_index) = tl.max(inp_vals, axis=1, return_indices=True)
        update_mask = max_value > result_value
        result_value = tl.where(update_mask, max_value, result_value)
        result_index = tl.where(update_mask, i + max_index, result_index)
    mask1 = m_offset < M
    offset_index = m_offset
    out_value_ptrs = out_value + offset_index
    out_index_ptrs = out_index + offset_index
    tl.store(out_value_ptrs, result_value, mask=mask1)
    tl.store(out_index_ptrs, result_index, mask=mask1)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (1398,)  workload x2:dim0 699->1398
#   规模  (2097,)  workload x3:dim0 699->2097
SHAPES = ((17,), (118,))
DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 x=args["inp"].reshape(int(args["M"]),int(args["N"]));idx=np.argmax(x,axis=1);return {"out_value":x[np.arange(x.shape[0]),idx],"out_index":idx.astype(np.int64)}

def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=20260901):
 from case_utils import fast_rng
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 M=3;C=max(2,N//M);args={"inp":np.asarray(rng.normal(0,.8,M*C)),"out_value":np.asarray(np.full(M,-7.)),"out_index":np.asarray(np.full(M,-1),"int64"),"M":M,"N":C};meta={"BLOCK_M":2,"BLOCK_N":128};grid=((M+1)//2,)
 outputs=('out_value', 'out_index');return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0001, "atol": 0.0001, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, max_kernel, DTYPES,
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
