"""loop_sum: 按行循环累加 —— 三层结构(样板见 add.py)。

① loop_sum_kernel   编译单元:@triton.jit,自研编译器只消费它的 AST。
② loop_sum(...)     执行单元:numpy in/out,grid lambda + kernel[grid] 原生调用,
                  设备搬运(staging)由编译器的 launcher 完成,本文件零 torch。
③ SHAPES / DTYPES / make_case / ref
                  验证层:runner 构造输入、启动 kernel、与 ref 对拍,纯 numpy。
"""

OPERATOR = {"name": "hidden/loop_sum", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import numpy as np
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def loop_sum_kernel(x_ptr, out_ptr, n_cols, BLOCK: tl.constexpr):
    row = tl.program_id(0)
    cols = tl.arange(0, BLOCK)
    acc = tl.zeros((BLOCK,), dtype=tl.float32)
    for start in range(0, n_cols, BLOCK):
        offsets = start + cols
        x = tl.load(x_ptr + row * n_cols + offsets, mask=offsets < n_cols, other=0.0).to(tl.float32)
        acc += x
    tl.store(out_ptr + row, tl.sum(acc, axis=0))


DTYPES = ('float16', 'float32', 'bfloat16')

SHAPES = ((3, 97),)


def ref(args, meta):
    import numpy as np

    return {'out_ptr': (np.sum(args['x_ptr'], axis=1, dtype=np.float64).astype(np.float32)).astype(np.asarray(args['out_ptr']).dtype)}


def _make_case(shape=(3, 257), seed=0, *, dtype="float32"):
    import numpy as np

    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")

    shape = tuple(int(v) for v in shape)
    if len(shape) != 2 or any(v <= 0 for v in shape):
        raise ValueError("invalid positive shape")
    rng = fast_rng(seed)
    rows, cols = shape
    x = rng.uniform(-1.0, 1.0, (rows, cols)).astype(np.float32)
    args = {'x_ptr': x, 'out_ptr': np.empty(rows, dtype=np.float32), 'n_cols': cols}
    meta = {'BLOCK': 128}
    for name, value in args.items():
        if isinstance(value, np.ndarray) and value.dtype.kind == "f":
            if name in ("out_ptr", "y_ptr"):
                args[name] = np.zeros(value.shape, dtype=dtype)
                continue
            args[name] = value.astype(dtype)
    return {"args": args, "meta": meta, "grid": (rows,), "outputs": ('out_ptr',), "expected": ref(args, meta)}


# ------------------------------------------------------------------ ② 执行单元
def loop_sum(x):
    """按行循环累加;numpy in/out(或 duck-typed 数组),设备搬运由编译器 launcher 完成。"""
    from case_utils import empty, empty_like, numel

    rows, cols = int(x.shape[0]), int(x.shape[1])
    out = empty((rows,), like=x)
    loop_sum_kernel[(rows,)](x, out, cols, BLOCK=128)
    return out


# ------------------------------------------------------------------ ③ 验证层公共包装


# ------------------------------------------------------------------ ② 执行单元
def loop_sum(x):
    """按行循环累加;numpy in/out(或 duck-typed 数组),设备搬运由编译器 launcher 完成。"""
    from case_utils import empty, empty_like, numel

    rows, cols = int(x.shape[0]), int(x.shape[1])
    out = empty((rows,), like=x)
    loop_sum_kernel[(rows,)](x, out, cols, BLOCK=128)
    return out


# ------------------------------------------------------------------ ③ 验证层公共包装
def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化 + 白名单校验,委托 _make_case;比较策略集中在 case_utils。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, loop_sum_kernel, DTYPES,
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
