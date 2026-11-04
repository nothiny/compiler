"""fht_kernel_1d_native: 长度 16 的快速 Walsh-Hadamard 变换(带缩放)。

模式: args.runtime_scalar, control.if, creation.arange, memory.load, memory.store, shape.reshape。

文件只有两层:
  ① _fht_kernel_1d_native   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/fht_kernel_1d_native", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "control.if", "creation.arange", "memory.load", "memory.store", "shape.reshape"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/fht_kernel_1d_native.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def _fht_kernel_1d_native(X_ptr, OUT_ptr, stride_x_row, stride_out_row, DIM: tl.constexpr, LOG_N: tl.constexpr, BLOCK_SIZE: tl.constexpr, SCALE: tl.constexpr):
    """FHT butterfly — 1D single-row, native fp16/bf16, reversed stage order."""
    pid = tl.program_id(0)
    col_offs = tl.arange(0, BLOCK_SIZE)
    x = tl.load(X_ptr + pid * stride_x_row + col_offs)
    for s_rev in tl.static_range(LOG_N):
        _inl_1_butterfly_stage_1d_x = x
        pass
        pass
        _inl_1_butterfly_stage_1d_result = 0
        'One butterfly stage on a 1D vector.'
        pass
        if 1 << LOG_N - 1 - s_rev == 1:
            _inl_1_butterfly_stage_1d_x2 = tl.reshape(_inl_1_butterfly_stage_1d_x, (BLOCK_SIZE // (2 * (1 << LOG_N - 1 - s_rev)), 2))
            (_inl_1_butterfly_stage_1d_a, _inl_1_butterfly_stage_1d_b) = tl.split(_inl_1_butterfly_stage_1d_x2)
            _inl_1_butterfly_stage_1d_result = tl.reshape(tl.join(_inl_1_butterfly_stage_1d_a + _inl_1_butterfly_stage_1d_b, _inl_1_butterfly_stage_1d_a - _inl_1_butterfly_stage_1d_b), (BLOCK_SIZE,))
        else:
            _inl_1_butterfly_stage_1d_x3 = tl.reshape(_inl_1_butterfly_stage_1d_x, (BLOCK_SIZE // (2 * (1 << LOG_N - 1 - s_rev)), 2, 1 << LOG_N - 1 - s_rev))
            _inl_1_butterfly_stage_1d_x3 = tl.permute(_inl_1_butterfly_stage_1d_x3, (0, 2, 1))
            (_inl_1_butterfly_stage_1d_a, _inl_1_butterfly_stage_1d_b) = tl.split(_inl_1_butterfly_stage_1d_x3)
            _inl_1_butterfly_stage_1d_x3 = tl.join(_inl_1_butterfly_stage_1d_a + _inl_1_butterfly_stage_1d_b, _inl_1_butterfly_stage_1d_a - _inl_1_butterfly_stage_1d_b)
            _inl_1_butterfly_stage_1d_x3 = tl.permute(_inl_1_butterfly_stage_1d_x3, (0, 2, 1))
            _inl_1_butterfly_stage_1d_result = tl.reshape(_inl_1_butterfly_stage_1d_x3, (BLOCK_SIZE,))
        x = _inl_1_butterfly_stage_1d_result
    x = x * SCALE
    tl.store(OUT_ptr + pid * stride_out_row + col_offs, x, eviction_policy='evict_first')


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (34, 16)  workload x2:dim0 17->34
#   规模  (51, 16)  workload x3:dim0 17->51
SHAPES = ((17,), (51, 16))
DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 x=args["X_ptr"].reshape(-1,int(meta.get("DIM",args["stride_x_row"])));y=np.array(x,copy=True)
 h=1
 while h<y.shape[1]:
  for s in range(0,y.shape[1],2*h):
   a=y[:,s:s+h].copy();b=y[:,s+h:s+2*h].copy();y[:,s:s+h]=a+b;y[:,s+h:s+2*h]=a-b
  h*=2
 y*=np.float32(meta["SCALE"])
 return {"OUT_ptr":y.reshape(-1)}

def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=20260901):
    from case_utils import fast_rng
    if len(shape) > 1 and tuple(shape) not in SHAPES:
        raise ValueError('unsupported explicit shape configuration')
    del dtype
    import numpy as np
    N = int(shape[0])
    rng = fast_rng(seed)
    R = int(shape[0]) if len(shape) > 1 else 3
    D = int(shape[1]) if len(shape) > 1 else 16
    T = R * D
    args = {'X_ptr': np.asarray(rng.normal(0, 0.8, T)), 'OUT_ptr': np.asarray(np.full(T, -7.0)), 'stride_x_row': D, 'stride_out_row': D}
    meta = {'DIM': D, 'LOG_N': 4, 'BLOCK_SIZE': D, 'SCALE': 0.25}
    grid = (R,)
    outputs = ('OUT_ptr',)
    return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0001, "atol": 0.0001, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, _fht_kernel_1d_native, DTYPES,
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
