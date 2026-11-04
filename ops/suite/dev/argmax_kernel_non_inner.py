"""argmax_kernel_non_inner: 非内层轴 argmax:3D 输入沿 N 轴取最大值下标(平铺 tile)。

模式: args.runtime_scalar, cast.to, control.for_range, control.if, creation.arange, creation.full, creation.where, memory.load.masked, memory.load.other, memory.store.masked, reduce.max。

文件只有两层:
  ① argmax_kernel_non_inner   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/argmax_kernel_non_inner", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "cast.to", "control.for_range", "control.if", "creation.arange", "creation.full", "creation.where", "memory.load.masked", "memory.load.other", "memory.store.masked", "reduce.max"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/argmax_kernel_non_inner.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def argmax_kernel_non_inner(inp, out_index, M, N, K, TILE_K: tl.constexpr, TILE_N: tl.constexpr, ONE_TILE_PER_CTA: tl.constexpr):
    pid_m = tl.program_id(0).to(tl.int64)
    pid_k = tl.program_id(1).to(tl.int64)
    k_offset = pid_k * TILE_K + tl.arange(0, TILE_K)
    if tl.constexpr(inp.dtype.element_ty == tl.float16) or tl.constexpr(inp.dtype.element_ty == tl.bfloat16):
        cdtype = tl.float32
    else:
        cdtype = inp.dtype.element_ty
    _inl_3_get_dtype_min_dtype = cdtype
    _inl_3_get_dtype_min_result = 0
    'get a value which is less that all other values of that dtype'
    _inl_3_get_dtype_min_dtype_ = _inl_3_get_dtype_min_dtype
    if _inl_3_get_dtype_min_dtype_.is_floating():
        _inl_3_get_dtype_min_value: tl.constexpr = float('-inf')
        _inl_3_get_dtype_min_result = _inl_3_get_dtype_min_value
    elif _inl_3_get_dtype_min_dtype_.is_int_signed():
        _inl_3_get_dtype_min_width: tl.constexpr = _inl_3_get_dtype_min_dtype_.int_bitwidth
        _inl_3_get_dtype_min_value: tl.constexpr = -1 * 2 ** (_inl_3_get_dtype_min_width - 1)
        _inl_3_get_dtype_min_result = _inl_3_get_dtype_min_value
    elif _inl_3_get_dtype_min_dtype_.is_int_unsigned():
        _inl_3_get_dtype_min_value: tl.constexpr = 0
        _inl_3_get_dtype_min_result = _inl_3_get_dtype_min_value
    min_value = _inl_3_get_dtype_min_result
    if ONE_TILE_PER_CTA:
        n_offset = tl.arange(0, TILE_N)
        offset = pid_m * N * K + n_offset[:, None] * K + k_offset
        mask = k_offset < K and n_offset[:, None] < N
        inp_ptrs = inp + offset
        inp_vals = tl.load(inp_ptrs, mask=mask, other=min_value)
        (local_max, local_argmax) = tl.max(inp_vals, 0, return_indices=True, return_indices_tie_break_left=True)
        offset_index = pid_m * K + k_offset
        out_index_ptrs = out_index + offset_index
        mask1 = k_offset < K
        tl.store(out_index_ptrs, local_argmax, mask=mask1)
    else:
        max_values = tl.full([TILE_K], dtype=cdtype, value=min_value)
        argmax_values = tl.full([TILE_K], dtype=tl.int64, value=0)
        for start_n in range(0, N, TILE_N):
            n_offset = start_n + tl.arange(0, TILE_N)
            offset = pid_m * N * K + n_offset[:, None] * K + k_offset
            mask = k_offset < K and n_offset[:, None] < N
            inp_ptrs = inp + offset
            inp_vals = tl.load(inp_ptrs, mask=mask, other=min_value)
            (local_max, local_argmax) = tl.max(inp_vals, 0, return_indices=True, return_indices_tie_break_left=True)
            update = local_max > max_values
            max_values = tl.where(update, local_max, max_values)
            argmax_values = tl.where(update, start_n + local_argmax, argmax_values)
        offset_index = pid_m * K + k_offset
        out_index_ptrs = out_index + offset_index
        mask1 = k_offset < K
        tl.store(out_index_ptrs, argmax_values, mask=mask1)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (1200,)  workload x2:dim0 600->1200
#   规模  (1800,)  workload x3:dim0 600->1800
SHAPES = ((17,), (120,))
DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 M=int(args["M"]);R=int(args["N"]);K=int(args["K"]);x=args["inp"].reshape(M,R,K);return {"out_index":np.argmax(x,axis=1).astype(np.int64).reshape(-1)}

def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=20260901):
 from case_utils import fast_rng
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 M=2;R=3;K=max(2,N//6);args={"inp":np.asarray(rng.normal(0,.8,M*R*K)),"out_index":np.asarray(np.full(M*K,-1),"int64"),"M":M,"N":R,"K":K};meta={"TILE_K":4,"TILE_N":128,"ONE_TILE_PER_CTA":False};grid=(M,(K+3)//4)
 outputs=('out_index',);return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0001, "atol": 0.0001, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, argmax_kernel_non_inner, DTYPES,
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
