"""argmin_split_K_kernel_merged: split-K argmin:M x N x K 沿 N 归约最小值下标(split 合并)。

模式: args.runtime_scalar, cast.to, control.for_range, control.if, creation.arange, creation.full, creation.where, memory.load.masked, memory.load.other, memory.store.masked, reduce.min。

文件只有两层:
  ① argmin_split_K_kernel_merged   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/argmin_split_K_kernel_merged", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "cast.to", "control.for_range", "control.if", "creation.arange", "creation.full", "creation.where", "memory.load.masked", "memory.load.other", "memory.store.masked", "reduce.min"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/argmin_split_K_kernel_merged.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def argmin_split_K_kernel_merged(inp, out_index, M: tl.constexpr, N: tl.constexpr, K: tl.constexpr, dtype: tl.constexpr, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr):
    pid_m = tl.program_id(0).to(tl.int64)
    pid_k = tl.program_id(1).to(tl.int64)
    m = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)[:, None]
    k = pid_k * BLOCK_K + tl.arange(0, BLOCK_K)[None, :]
    m_mask = m < M
    k_mask = k < K
    mk_mask = m_mask & k_mask
    compute_dtype = tl.float32 if dtype == tl.bfloat16 else dtype
    _inl_3_get_dtype_max_dtype = compute_dtype
    _inl_3_get_dtype_max_result = 0
    'get a value which is greater that all other values of that dtype'
    _inl_3_get_dtype_max_dtype_ = _inl_3_get_dtype_max_dtype
    if _inl_3_get_dtype_max_dtype_.is_floating():
        _inl_3_get_dtype_max_value: tl.constexpr = float('inf')
        _inl_3_get_dtype_max_result = _inl_3_get_dtype_max_value
    elif _inl_3_get_dtype_max_dtype_.is_int_signed():
        _inl_3_get_dtype_max_width: tl.constexpr = _inl_3_get_dtype_max_dtype_.int_bitwidth
        _inl_3_get_dtype_max_value: tl.constexpr = 2 ** (_inl_3_get_dtype_max_width - 1) - 1
        _inl_3_get_dtype_max_result = _inl_3_get_dtype_max_value
    elif _inl_3_get_dtype_max_dtype_.is_int_unsigned():
        _inl_3_get_dtype_max_width: tl.constexpr = _inl_3_get_dtype_max_dtype_.int_bitwidth
        _inl_3_get_dtype_max_value: tl.constexpr = 2 ** _inl_3_get_dtype_max_width - 1
        _inl_3_get_dtype_max_result = _inl_3_get_dtype_max_value
    max_val = _inl_3_get_dtype_max_result
    global_min = tl.full((BLOCK_M, BLOCK_K), max_val, dtype=compute_dtype)
    global_argmin = tl.full((BLOCK_M, BLOCK_K), 0, dtype=tl.int64)
    for start_n in range(0, N, BLOCK_N):
        n = start_n + tl.arange(0, BLOCK_N)
        n_mask = n < N
        offset = m.to(tl.int64) * N * K + n[:, None, None].to(tl.int64) * K + k.to(tl.int64)
        inp_vals = tl.load(inp + offset, mask=m_mask & n_mask[:, None, None] & k_mask[None, :, :], other=max_val)
        inp_vals = inp_vals.to(compute_dtype)
        (local_min, local_argmin) = tl.min(inp_vals, 0, return_indices=True, return_indices_tie_break_left=True)
        local_argmin += start_n
        mask = local_min < global_min
        global_min = tl.where(mask, local_min, global_min)
        global_argmin = tl.where(mask, local_argmin, global_argmin)
    out_offset = m.to(tl.int64) * K + k.to(tl.int64)
    tl.store(out_index + out_offset, global_argmin, mask=mk_mask)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (1224,)  workload x2:dim0 612->1224
#   规模  (1836,)  workload x3:dim0 612->1836
SHAPES = ((17,), (104,))
DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 M=int(meta["M"]);R=int(meta["N"]);K=int(meta["K"]);x=args["inp"].reshape(M,R,K);return {"out_index":np.argmin(x,axis=1).astype(np.int64).reshape(-1)}

def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=20260901):
 from case_utils import fast_rng
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 M=2;R=3;K=max(2,N//6);args={"inp":np.asarray(rng.normal(0,.8,M*R*K)),"out_index":np.asarray(np.full(M*K,-1),"int64")};meta={"M":M,"N":R,"K":K,"dtype":tl.float32,"BLOCK_M":2,"BLOCK_N":128,"BLOCK_K":4};grid=((M+1)//2,(K+3)//4)
 outputs=('out_index',);return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0001, "atol": 0.0001, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, argmin_split_K_kernel_merged, DTYPES,
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
