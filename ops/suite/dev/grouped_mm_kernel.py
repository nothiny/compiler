"""grouped_mm_kernel: 从 ~/ops 仓库复制(smoke @ ops),保留其已验证的 case 层。

模式: args.runtime_scalar、blockptr.advance、blockptr.make、cast.to、control.for_range、control.loop_carried、creation.arange、creation.zeros、dtype.int32、linalg.dot。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。循环上界来自运行时标量(不是 constexpr)。constexpr 参数: num_groups, N, K, stride_am, stride_ak, stride_bk, stride_bn, stride_cm, stride_cn, BLOCK_M, BLOCK_N, BLOCK_K, GROUP_M。

文件只有两层:
  ① grouped_mm_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/grouped_mm_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'blockptr.advance', 'blockptr.make', 'cast.to', 'control.for_range', 'control.loop_carried', 'creation.arange', 'creation.zeros', 'dtype.int32', 'linalg.dot', 'linalg.dot.acc', 'math.cdiv', 'math.minimum', 'memory.load', 'memory.store', 'memory.store.masked', 'tile.2d']}
COPIED_FROM = {'repo': 'smoke @ ops', 'note': 'validated case layer intact', 'lines': 177}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def grouped_mm_kernel(A, B, C, offs, num_groups: tl.constexpr, M, N: tl.constexpr, K: tl.constexpr, stride_am: tl.constexpr, stride_ak: tl.constexpr, stride_bk: tl.constexpr, stride_bn: tl.constexpr, stride_cm: tl.constexpr, stride_cn: tl.constexpr, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr, GROUP_M: tl.constexpr):
    total_grid = tl.num_programs(axis=0)
    tile_idx = tl.program_id(axis=0)
    num_n_tiles = tl.cdiv(N, BLOCK_N)
    last_problem_end = 0
    group_start = 0
    group_end = 0
    for group_idx in tl.range(num_groups):
        group_end = tl.load(offs + group_idx).to(tl.int32)
        m = group_end - group_start
        num_m_tiles = tl.cdiv(m, BLOCK_M)
        num_tiles = num_m_tiles * num_n_tiles
        current_problem_end = last_problem_end + num_tiles
        if tile_idx >= last_problem_end and tile_idx < current_problem_end:
            loop_count = (current_problem_end - tile_idx + total_grid - 1) // total_grid
            for _ in tl.range(loop_count):
                tile_idx_in_gemm = tile_idx - last_problem_end
                group1_grid_m = tl.cdiv(m, BLOCK_M)
                group1_width = GROUP_M * tl.cdiv(N, BLOCK_N)
                group1_group_id = tile_idx_in_gemm // group1_width
                group1_group_size = tl.minimum(group1_grid_m - group1_group_id * GROUP_M, GROUP_M)
                (tile_m_idx, tile_n_idx) = (group1_group_id * GROUP_M + tile_idx_in_gemm % group1_group_size, tile_idx_in_gemm % group1_width // group1_group_size)
                offs_am = group_start + tile_m_idx * BLOCK_M
                offs_bn = tile_n_idx * BLOCK_N
                offs_bk = group_idx * K
                a_block_ptr = tl.make_block_ptr(base=A, shape=(M, K), strides=(stride_am, stride_ak), offsets=(offs_am, 0), block_shape=(BLOCK_M, BLOCK_K), order=(1, 0))
                b_block_ptr = tl.make_block_ptr(base=B, shape=(num_groups * K, N), strides=(stride_bk, stride_bn), offsets=(offs_bk, offs_bn), block_shape=(BLOCK_K, BLOCK_N), order=(1, 0))
                accumulator = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)
                for k in tl.range(0, tl.cdiv(K, BLOCK_K)):
                    a = tl.load(a_block_ptr, boundary_check=(0, 1))
                    b = tl.load(b_block_ptr, boundary_check=(0, 1))
                    accumulator = tl.dot(a, b, acc=accumulator)
                    a_block_ptr = tl.advance(a_block_ptr, (0, BLOCK_K))
                    b_block_ptr = tl.advance(b_block_ptr, (BLOCK_K, 0))
                c = accumulator.to(C.dtype.element_ty)
                c_block_ptr = tl.make_block_ptr(base=C, shape=(M, N), strides=(stride_cm, stride_cn), offsets=(offs_am, offs_bn), block_shape=(BLOCK_M, BLOCK_N), order=(1, 0))
                if offs_am + BLOCK_M <= group_end:
                    tl.store(c_block_ptr, c, boundary_check=(0, 1))
                else:
                    offs_cm = offs_am + tl.arange(0, BLOCK_M)
                    offs_cn = offs_bn + tl.arange(0, BLOCK_N)
                    c_ptrs = C + stride_cm * offs_cm[:, None] + stride_cn * offs_cn[None, :]
                    c_mask = (offs_cm[:, None] < group_end) & (offs_cn[None, :] < N)
                    tl.store(c_ptrs, c, mask=c_mask)
                tile_idx += total_grid
        last_problem_end = current_problem_end
        group_start = group_end

# ------------------------------------------------------------------ ② case 层
# (shape,) 的角色:第一个是典型用法,其余是泛化/尾块/退化用例。
#   (3, 23, 19, 17)
#   (4, 67, 35, 29)
#   (5, 129, 65, 33)
#   (4, 23, 19, 17)
# DTYPES: bfloat16 —— 原始用途的 dtype 在前;非法域(例如本机 Triton 只吃 fp32 的exp/sqrt/erf/atomic)的算子只声明合法的那一种。

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
        if _comparison_dtype_policy == 'float32':
            (rtol, atol) = (0.0001, 0.0001)
        elif _comparison_dtype_policy == 'bfloat16':
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

SHAPES = ((3, 23, 19, 17), (4, 67, 35, 29))
DTYPES = ('bfloat16', 'float32', 'float16')
FIXED_META = {"BLOCK_M": 16, "BLOCK_N": 16, "BLOCK_K": 16, "GROUP_M": 4}
LAUNCH_META = {"num_warps": 4, "num_stages": 1}
def ref(args, meta):
    import numpy as np

    a = np.asarray(args["A"], dtype=np.float32).reshape(int(args["M"]), int(meta["K"]))
    b = np.asarray(args["B"], dtype=np.float32).reshape(int(meta["num_groups"]), int(meta["K"]), int(meta["N"]))
    ends = np.asarray(args["offs"], dtype=np.int64)
    result = np.empty((int(args["M"]), int(meta["N"])), dtype=np.float32)
    start = 0
    for group, end in enumerate(ends):
        result[start:end] = a[start:end] @ b[group]
        start = int(end)
    return {"C": result.reshape(-1)}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    import numpy as np
    (num_groups, m, n, k) = (int(value) for value in shape)
    if num_groups <= 0 or m < num_groups or n <= 0 or (k <= 0):
        raise ValueError('shape must be (groups, M>=groups, positive N, positive K)')
    dtype_name = str(dtype).rsplit('.', 1)[-1]
    from case_utils import fast_rng
    rng = fast_rng(seed)
    ends = np.asarray([m * (group + 1) // num_groups for group in range(num_groups)], dtype=np.int32)
    args = {'A': _aligned(rng.uniform(-0.5, 0.5, m * k), 'float32'), 'B': _aligned(rng.uniform(-0.5, 0.5, num_groups * k * n), 'float32'), 'C': _aligned(np.full(m * n, -0.875), 'float32'), 'offs': _aligned(ends, 'int32'), 'M': m}
    meta = {'num_groups': num_groups, 'N': n, 'K': k, 'stride_am': k, 'stride_ak': 1, 'stride_bk': n, 'stride_bn': 1, 'stride_cm': n, 'stride_cn': 1, **FIXED_META}
    start = 0
    total_tiles = 0
    for end in ends:
        rows = int(end) - start
        total_tiles += (rows + meta['BLOCK_M'] - 1) // meta['BLOCK_M'] * ((n + meta['BLOCK_N'] - 1) // meta['BLOCK_N'])
        start = int(end)
    grid = (total_tiles,)
    outputs = ('C',)
    return {'kernel': grouped_mm_kernel, 'grid': grid, 'args': args, 'meta': meta, 'launch_meta': dict(LAUNCH_META), 'inputs': ('A', 'B', 'offs'), 'outputs': outputs, 'expected': ref(args, meta), 'comparison': _comparison(outputs, rtol=0.03, atol=0.03, dtype=str(dtype)), 'pointer_dtypes': {'A': dtype_name, 'B': dtype_name, 'C': dtype_name, 'offs': 'int32'}, 'buffer_extents': {'A': m * k, 'B': num_groups * k * n, 'C': m * n, 'offs': num_groups}, 'buffer_layouts': _layouts(args), 'alignment': 64, 'aliases': {}, 'seed': int(seed), 'shape': tuple(shape), 'dtype': str(dtype), 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'coverage': {'complete_logical_output': True, 'grid_formula': '(sum_g ceil_div(rows_g,BLOCK_M)*ceil_div(N,BLOCK_N),)', 'groups': num_groups}}
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


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'bfloat16'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'bfloat16': 'bfloat16'}


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
