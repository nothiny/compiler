"""pow_scalar_tensor:逐元素 x ** exponent(标量指数)—— 三层结构。

① pow_func_scalar_tensor_kernel_rank_1   编译单元:@triton.jit,只消费它的 AST。
② pow_scalar_tensor(...)                 执行单元:numpy in/out,零 torch。
③ SHAPES / DTYPES / make_case / ref      验证层:纯 numpy。
"""

OPERATOR = {"name": "hidden/pow_scalar_tensor", "group": "hidden", "channel": "G",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import numpy as np
import triton
import triton.language as tl
from case_utils import fast_rng


@triton.jit(do_not_specialize=['val0'])
def pow_func_scalar_tensor_kernel_rank_1(
    val0,
    in0_ptr: tl.tensor,
    out0_ptr: tl.tensor,
    in0_stride0: int,
    in0_stride_order0: tl.constexpr,
    out0_stride0: int,
    out0_stride_order0: tl.constexpr,
    s0: int,
    num_tasks: int,
    tiles_per_cta: int,
    tile_size0: tl.constexpr,
    one_tile_per_cta: tl.constexpr,
):
    pid = tl.program_id(0)
    if one_tile_per_cta:
        tile_id0 = pid
        offset0 = tile_id0 * tile_size0
        in0_bptr = tl.make_block_ptr(in0_ptr, (s0,), (in0_stride0,), (offset0,),
                                     (tile_size0,), order=(in0_stride_order0,))
        in0 = tl.load(in0_bptr, boundary_check=(in0_stride_order0,)).to(in0_ptr.type.element_ty)
        _xf = in0.to(tl.float32)
        _ax = tl.abs(_xf)
        _safe = tl.where(_ax > 0.0, _ax, 1.0)
        _mag = tl.exp2(val0 * tl.log2(_safe))
        _is_int = val0 == tl.floor(val0)
        _odd = (val0 * 0.5 - tl.floor(val0 * 0.5)) > 0.25
        _sign = tl.where((_xf < 0.0) & _is_int & _odd, -1.0, 1.0)
        _zero = tl.where(val0 > 0.0, 0.0, tl.where(val0 == 0.0, 1.0, float('inf')))
        out0 = tl.where(_ax == 0.0, _zero, _sign * _mag)
        out0 = tl.where((_xf < 0.0) & (~_is_int), float('nan'), out0)
        out0_bptr = tl.make_block_ptr(out0_ptr, (s0,), (out0_stride0,), (offset0,),
                                      (tile_size0,), order=(out0_stride_order0,))
        tl.store(out0_bptr, out0.to(out0_ptr.type.element_ty),
                 boundary_check=(out0_stride_order0,))
    else:
        num_ctas = tl.num_programs(0)
        for j in range(0, tiles_per_cta):
            tile_id0 = pid + j * num_ctas
            offset0 = tile_id0 * tile_size0
            in0_bptr = tl.make_block_ptr(in0_ptr, (s0,), (in0_stride0,), (offset0,),
                                         (tile_size0,), order=(in0_stride_order0,))
            in0 = tl.load(in0_bptr, boundary_check=(in0_stride_order0,)).to(in0_ptr.type.element_ty)
            _xf = in0.to(tl.float32)
            _ax = tl.abs(_xf)
            _safe = tl.where(_ax > 0.0, _ax, 1.0)
            _mag = tl.exp2(val0 * tl.log2(_safe))
            _is_int = val0 == tl.floor(val0)
            _odd = (val0 * 0.5 - tl.floor(val0 * 0.5)) > 0.25
            _sign = tl.where((_xf < 0.0) & _is_int & _odd, -1.0, 1.0)
            _zero = tl.where(val0 > 0.0, 0.0, tl.where(val0 == 0.0, 1.0, float('inf')))
            out0 = tl.where(_ax == 0.0, _zero, _sign * _mag)
            out0 = tl.where((_xf < 0.0) & (~_is_int), float('nan'), out0)
            out0_bptr = tl.make_block_ptr(out0_ptr, (s0,), (out0_stride0,), (offset0,),
                                          (tile_size0,), order=(out0_stride_order0,))
            tl.store(out0_bptr, out0.to(out0_ptr.type.element_ty),
                     boundary_check=(out0_stride_order0,))


DTYPES = ('float32', 'float16', 'bfloat16')
SHAPES = ((128,), (99,))


def _pow_ref(x, exponent):
    xf = np.asarray(x, dtype=np.float32)
    e = np.float32(exponent)
    ax = np.abs(xf)
    safe = np.where(ax > 0, ax, np.float32(1.0)).astype(np.float32)
    mag = np.exp2(e * np.log2(safe)).astype(np.float32)
    is_int = bool(e == np.floor(e))
    odd = bool((e * np.float32(0.5) - np.floor(e * np.float32(0.5))) > np.float32(0.25))
    sign = np.where((xf < 0) & is_int & odd, np.float32(-1.0), np.float32(1.0)).astype(np.float32)
    if e > 0:
        zero = np.float32(0.0)
    elif e == 0:
        zero = np.float32(1.0)
    else:
        zero = np.float32(np.inf)
    result = np.where(ax == 0, zero, sign * mag).astype(np.float32)
    if not is_int:
        result = np.where(xf < 0, np.float32(np.nan), result).astype(np.float32)
    return result


def ref(args, meta):
    x = np.asarray(args["in0_ptr"], dtype=np.float32).reshape(-1)
    return {"out0_ptr": _pow_ref(x, float(args["val0"])).astype(
        np.asarray(args["out0_ptr"]).dtype)}


def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    shape = tuple(int(value) for value in shape)
    n = int(shape[0])
    rng = fast_rng(seed)
    x = (rng.standard_normal(n) * 1.5).astype(dtype)
    x[0] = np.float32(0.0)
    exponent = 2.0
    blk = triton.next_power_of_2(n)
    tiles = triton.cdiv(n, blk)
    args = {"val0": exponent, "in0_ptr": x,
            "out0_ptr": np.zeros(n, dtype=dtype),
            "in0_stride0": np.int32(1), "out0_stride0": np.int32(1),
            "s0": np.int32(n), "num_tasks": np.int32(tiles),
            "tiles_per_cta": np.int32(tiles)}
    meta = {"in0_stride_order0": 0, "out0_stride_order0": 0,
            "tile_size0": blk, "one_tile_per_cta": (tiles == 1)}
    return {"args": args, "meta": meta, "grid": (tiles,),
            "outputs": ("out0_ptr",), "expected": ref(args, meta)}


def pow_scalar_tensor(x, exponent):
    """逐元素 x ** exponent(标量);numpy in/out。"""
    from case_utils import empty, numel

    xf = np.asarray(x, dtype=np.float32).reshape(-1)
    n = numel(xf)
    out = empty((n,), like=x)
    blk = triton.next_power_of_2(n)
    tiles = triton.cdiv(n, blk)
    pow_func_scalar_tensor_kernel_rank_1[(tiles,)](
        float(exponent), xf, out, 1, 0, 1, 0, n, tiles, tiles,
        tile_size0=blk, one_tile_per_cta=(tiles == 1))
    return out


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, pow_func_scalar_tensor_kernel_rank_1, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)


ORACLE_KIND = "numpy_reference"
INDEPENDENT_ORACLE = True
EXECUTION_KIND = "triton_kernel"
VERIFICATION_KIND = "correctness"
OPERATOR_NAME = "G/" + __file__.rsplit("/", 1)[-1]
OPERATOR_FILE = __file__


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
