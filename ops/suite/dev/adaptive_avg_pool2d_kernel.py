"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/adaptive_avg_pool2d_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["conv_pool"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def adaptive_avg_pool2d_kernel(input_ptr, output_ptr, in_stride_n, in_stride_c, in_stride_h, in_stride_w, in_c, in_h, in_w, out_h, out_w, BLOCK_H: tl.constexpr, BLOCK_W: tl.constexpr):
    pid_nc = tl.program_id(0)
    pid_hw = tl.program_id(1)
    num_w_blocks = tl.cdiv(out_w, BLOCK_W)
    h_block_idx = pid_hw // num_w_blocks
    w_block_idx = pid_hw % num_w_blocks
    n_idx = pid_nc // in_c
    c_idx = pid_nc % in_c
    h_out_offsets = h_block_idx * BLOCK_H + tl.arange(0, BLOCK_H)
    w_out_offsets = w_block_idx * BLOCK_W + tl.arange(0, BLOCK_W)
    h_start = h_out_offsets[:, None] * in_h // out_h
    h_end = 1 + ((h_out_offsets[:, None] + 1) * in_h - 1) // out_h
    w_start = w_out_offsets[None, :] * in_w // out_w
    w_end = 1 + ((w_out_offsets[None, :] + 1) * in_w - 1) // out_w
    window_size = (h_end - h_start) * (w_end - w_start)
    window_size = tl.maximum(window_size, 1)
    h_start = tl.maximum(h_start, 0)
    w_start = tl.maximum(w_start, 0)
    sum_acc = tl.zeros((BLOCK_H, BLOCK_W), dtype=tl.float32)
    input_base_ptr = input_ptr + n_idx * in_stride_n + c_idx * in_stride_c
    max_win_h = (in_h + out_h - 1) // out_h + 1
    max_win_w = (in_w + out_w - 1) // out_w + 1
    for kh in range(max_win_h):
        h_in = h_start + kh
        h_valid = (h_in >= 0) & (h_in < h_end) & (h_in < in_h)
        h_valid_kw = kh < max_win_h
        for kw in range(max_win_w):
            w_in = w_start + kw
            w_valid = (w_in >= 0) & (w_in < w_end) & (w_in < in_w)
            w_valid_kw = kw < max_win_w
            h_valid_2d = h_valid & h_valid_kw
            w_valid_2d = w_valid & w_valid_kw
            in_mask = h_valid_2d & w_valid_2d
            h_in_2d = tl.reshape(h_in, (BLOCK_H, 1))
            w_in_2d = tl.reshape(w_in, (1, BLOCK_W))
            input_offset = h_in_2d * in_stride_h + w_in_2d * in_stride_w
            current_val = tl.load(input_base_ptr + input_offset, mask=in_mask, other=0.0)
            sum_val = tl.where(in_mask, current_val, 0.0)
            sum_acc = sum_acc + tl.reshape(sum_val, (BLOCK_H, BLOCK_W))
    output_vals = sum_acc / window_size.to(tl.float32)
    out_base_ptr = output_ptr + pid_nc * out_h * out_w
    out_h_offsets = h_block_idx * BLOCK_H + tl.arange(0, BLOCK_H)
    out_w_offsets = w_block_idx * BLOCK_W + tl.arange(0, BLOCK_W)
    output_block_ptr = out_base_ptr + out_h_offsets[:, None] * out_w + out_w_offsets[None, :]
    out_mask = (out_h_offsets[:, None] < out_h) & (w_out_offsets[None, :] < out_w)
    tl.store(output_block_ptr, output_vals.to(output_ptr.type.element_ty), mask=out_mask)
CASE_SCHEMA = 3
SUPPORT_STATUS = "supported"
VALIDATION_SCOPE = "full-launch-correctness"
SEED = 20260826


def _aligned(values, dtype, alignment=64):
    import numpy as np

    values = np.asarray(values, dtype=np.dtype(dtype))
    raw = np.empty(values.size * values.dtype.itemsize + alignment, dtype=np.uint8)
    start = -raw.ctypes.data % alignment
    result = raw[start : start + values.size * values.dtype.itemsize].view(values.dtype)
    result[...] = values.reshape(-1)
    return result.reshape(values.shape)


def _comparison(outputs, exact=False, rtol=0.0001, atol=0.0001, dtype=None):
    if not exact:
        _comparison_dtype_policy = str(dtype)
        if _comparison_dtype_policy == 'torch.float32':
            (rtol, atol) = (0.0001, 0.0001)
        elif _comparison_dtype_policy == 'torch.bfloat16':
            (rtol, atol) = (0.01, 0.01)
    return {name: {'profile': 'exact' if exact else 'elementwise-strict', 'comparator': 'array_equal' if exact else 'allclose', 'exact': bool(exact), 'rtol': 0.0 if exact else float(rtol), 'atol': 0.0 if exact else float(atol), 'equal_nan': not exact} for name in outputs}


def _layouts(args):
    import numpy as np

    return {
        name: {
            "shape": tuple(int(value) for value in np.asarray(array).shape),
            "strides": tuple(int(value // np.asarray(array).dtype.itemsize) for value in np.asarray(array).strides),
        }
        for name, array in args.items()
        if isinstance(array, np.ndarray)
    }
SHAPES = ((1, 2, 5, 7, 3, 4), (2, 3, 8, 9, 4, 5))
DTYPES = ('float16', 'float32', 'bfloat16')
FIXED_META = {"BLOCK_H": 2, "BLOCK_W": 2}
LAUNCH_META = {"num_warps": 4, "num_stages": 1}


def ref(args, meta):
    del meta
    import numpy as np
    x = np.asarray(args["input_ptr"])
    n, c, in_h, in_w = x.shape
    out_h, out_w = int(args["out_h"]), int(args["out_w"])
    out = np.empty((n, c, out_h, out_w), dtype=x.dtype)
    for oh in range(out_h):
        hs, he = oh * in_h // out_h, ((oh + 1) * in_h + out_h - 1) // out_h
        for ow in range(out_w):
            ws, we = ow * in_w // out_w, ((ow + 1) * in_w + out_w - 1) // out_w
            out[:, :, oh, ow] = x[:, :, hs:he, ws:we].astype(np.float32).mean(axis=(2, 3)).astype(x.dtype)
    return {"output_ptr": out}


def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    import numpy as np
    (n, c, in_h, in_w, out_h, out_w) = (int(value) for value in shape)
    dtype_name = str(dtype).rsplit('.', 1)[-1]
    rng = fast_rng(seed)
    x = _aligned(rng.uniform(-1.0, 1.0, n * c * in_h * in_w), dtype_name).reshape(n, c, in_h, in_w)
    out = _aligned(np.full(n * c * out_h * out_w, -0.875), dtype_name).reshape(n, c, out_h, out_w)
    args = {'input_ptr': x, 'output_ptr': out, 'in_stride_n': c * in_h * in_w, 'in_stride_c': in_h * in_w, 'in_stride_h': in_w, 'in_stride_w': 1, 'in_c': c, 'in_h': in_h, 'in_w': in_w, 'out_h': out_h, 'out_w': out_w}
    meta = dict(FIXED_META)
    grid = (n * c, (out_h + meta['BLOCK_H'] - 1) // meta['BLOCK_H'] * ((out_w + meta['BLOCK_W'] - 1) // meta['BLOCK_W']))
    outputs = ('output_ptr',)
    return {'kernel': adaptive_avg_pool2d_kernel, 'grid': grid, 'args': args, 'meta': meta, 'launch_meta': dict(LAUNCH_META), 'inputs': ('input_ptr',), 'outputs': outputs, 'expected': ref(args, meta), 'comparison': _comparison(outputs, rtol=0.02 if dtype_name == 'float16' else 1e-4, atol=0.02 if dtype_name == 'float16' else 1e-4, dtype=str(dtype)), 'pointer_dtypes': {'input_ptr': dtype_name, 'output_ptr': dtype_name}, 'buffer_extents': {'input_ptr': x.size, 'output_ptr': out.size}, 'buffer_layouts': _layouts(args), 'alignment': 64, 'aliases': {}, 'seed': int(seed), 'shape': tuple(shape), 'dtype': str(dtype), 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'coverage': {'complete_logical_output': True, 'grid_formula': '(N*C, ceil_div(out_h,BLOCK_H)*ceil_div(out_w,BLOCK_W))', 'output': 'output_ptr[N,C,out_h,out_w]'}}

def make_case(shape=None, dtype=None, seed=None):
    """Create one host case; defaults and supported dtypes are operator-owned."""
    import numpy as np

    requested = None
    if dtype is not None:
        try:
            requested = np.dtype(dtype).name
        except TypeError:
            requested = str(dtype).rsplit(".", 1)[-1]
    choices = {str(value).rsplit(".", 1)[-1]: value for value in DTYPES}
    if requested is not None and requested not in choices:
        raise ValueError(f"unsupported dtype {dtype}; choose from {tuple(choices)}")
    options = {}
    if shape is not None:
        options["shape"] = tuple(shape)
    if requested is not None:
        options["dtype"] = choices[requested]
    if seed is not None:
        options["seed"] = seed
    case = _make_case(**options)
    case.setdefault("outputs", tuple(case["expected"]))
    case.setdefault("launch_meta", {})
    return case


# ------------------------------------------------------------------ ② 执行单元(case 驱动)
def run(shape=None, dtype=None, seed=None, to_array=None):
    """直接执行:make_case 构造输入 → kernel[grid] 启动 → 返回输出。

    to_array=None 时数组参数按 numpy 原样传给 launcher(自研编译器的 staging
    语义);传入数组转换器(如 numpy→torch.cuda)即可在真实 Triton 上执行。
    """
    import sys

    from case_utils import run_case

    return run_case(sys.modules[__name__], shape=shape, dtype=dtype,
                    seed=seed, to_array=to_array)


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float32'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float16': 'torch.float16', 'float32': 'torch.float32'}


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
