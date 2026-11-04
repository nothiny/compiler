"""tanh: element-wise Tanh —— 三层结构(样板见 add.py)。

① tanh_kernel   编译单元:@triton.jit,自研编译器只消费它的 AST。
② tanh(...)     执行单元:numpy in/out,grid lambda + kernel[grid] 原生调用,
                  设备搬运(staging)由编译器的 launcher 完成,本文件零 torch。
③ SHAPES / DTYPES / make_case / ref
                  验证层:runner 构造输入、启动 kernel、与 ref 对拍,纯 numpy。
"""

OPERATOR = {"name": "hidden/tanh", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import numpy as np
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def tanh_kernel(x_ptr, y_ptr, n, BLOCK: tl.constexpr):
    pid = tl.program_id(0)
    cols = tl.arange(0, BLOCK)
    offsets = pid * BLOCK + cols
    mask = offsets < n
    x = tl.load(x_ptr + offsets, mask=mask, other=0.0).to(tl.float32)
    e2x = tl.exp(x + x)
    y = 1.0 - 2.0 / (e2x + 1.0)
    tl.store(y_ptr + offsets, y, mask=mask)


DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((128,), (97,))


def ref(args, meta):
    import numpy as np

    x = np.asarray(args['x_ptr'], dtype=np.float32)
    return {'y_ptr': (np.tanh(x.astype(np.float64)).astype(np.float32)).astype(np.asarray(args['y_ptr']).dtype)}


def _make_case(shape=SHAPES[0], *, dtype="float32", seed=2):
    import numpy as np

    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    shape = tuple((int(value) for value in shape))
    if not shape or any((value <= 0 for value in shape)):
        raise ValueError('shape dimensions must be positive')
    rng = fast_rng(seed)
    n = int(np.prod(shape))
    x = (rng.standard_normal(n) * 3.0).astype(np.float32)
    y = np.zeros_like(x)
    args = {'x_ptr': x, 'y_ptr': y, 'n': np.int32(n)}
    BLOCK = 1024
    grid = (int(np.ceil(n / BLOCK)),)
    meta = {'BLOCK': 1024}
    for name, value in args.items():
        if isinstance(value, np.ndarray) and value.dtype.kind == "f":
            if name in ("out_ptr", "y_ptr"):
                args[name] = np.zeros(value.shape, dtype=dtype)
                continue
            args[name] = value.astype(dtype)
    return {'args': args, 'meta': meta, 'grid': grid, 'outputs': ('y_ptr',), 'expected': ref(args, meta)}


# ------------------------------------------------------------------ ② 执行单元
def tanh(x):
    """element-wise Tanh;numpy in/out(或 duck-typed 数组),设备搬运由编译器 launcher 完成。"""
    from case_utils import empty, empty_like, numel

    y = empty_like(x)
    n = numel(y)
    grid = lambda meta: (triton.cdiv(n, meta["BLOCK"]),)
    tanh_kernel[grid](x, y, n, BLOCK=1024)
    return y


# ------------------------------------------------------------------ ③ 验证层公共包装


# ------------------------------------------------------------------ ② 执行单元
def tanh(x):
    """element-wise Tanh;numpy in/out(或 duck-typed 数组),设备搬运由编译器 launcher 完成。"""
    from case_utils import empty, empty_like, numel

    y = empty_like(x)
    n = numel(y)
    grid = lambda meta: (triton.cdiv(n, meta["BLOCK"]),)
    tanh_kernel[grid](x, y, n, BLOCK=1024)
    return y


# ------------------------------------------------------------------ ③ 验证层公共包装
def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化 + 白名单校验,委托 _make_case;比较策略集中在 case_utils。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, tanh_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float32'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float16': 'float16', 'float32': 'float32'}


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
