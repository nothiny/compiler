"""grouped_gemm_kernel: 从 ~/ops 仓库复制(smoke @ ops),保留其已验证的 case 层。

模式: args.runtime_scalar、blockptr.advance、blockptr.make、cast.to、control.for_range、control.loop_carried、creation.zeros、linalg.dot、linalg.dot.acc。load/store 没有掩码,SHAPES 全部满足整除约束。循环上界来自运行时标量(不是 constexpr)。constexpr 参数: BLOCK_M, BLOCK_N, BLOCK_K, GROUP_M, alpha, beta。

文件只有两层:
  ① grouped_gemm_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/grouped_gemm_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'blockptr.advance', 'blockptr.make', 'cast.to', 'control.for_range', 'control.loop_carried', 'creation.zeros', 'linalg.dot', 'linalg.dot.acc', 'math.cdiv', 'math.minimum', 'memory.load', 'memory.store']}
COPIED_FROM = {'repo': 'smoke @ ops', 'note': 'validated case layer intact', 'lines': 203}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def grouped_gemm_kernel(M, N, K, group_a_ptrs, group_b_ptrs, group_c_ptrs, group_out_ptrs, group_gemm_sizes, g_lds, group_size, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr, GROUP_M: tl.constexpr, alpha: tl.constexpr, beta: tl.constexpr):
    tile_idx = tl.program_id(0)
    total_grid = tl.num_programs(0)
    last_problem_end = 0
    for g in range(group_size):
        gm = tl.load(group_gemm_sizes + g * 3)
        gn = tl.load(group_gemm_sizes + g * 3 + 1)
        gk = tl.load(group_gemm_sizes + g * 3 + 2)
        num_m_tiles = tl.cdiv(gm, BLOCK_M)
        num_n_tiles = tl.cdiv(gn, BLOCK_N)
        num_tiles = num_m_tiles * num_n_tiles
        current_problem_end = last_problem_end + num_tiles
        if tile_idx >= last_problem_end and tile_idx < current_problem_end:
            lda = tl.load(g_lds + g * 3)
            ldb = tl.load(g_lds + g * 3 + 1)
            ldc = tl.load(g_lds + g * 3 + 2)
            a_ptr = tl.load(group_a_ptrs + g).to(tl.pointer_type(tl.bfloat16))
            b_ptr = tl.load(group_b_ptrs + g).to(tl.pointer_type(tl.bfloat16))
            c_ptr = tl.load(group_c_ptrs + g).to(tl.pointer_type(tl.bfloat16))
            out_ptr = tl.load(group_out_ptrs + g).to(tl.pointer_type(tl.bfloat16))
            loop_count = (current_problem_end - tile_idx + total_grid - 1) // total_grid
            for _ in tl.range(loop_count):
                tile_idx_in_gemm = tile_idx - last_problem_end
                group1_grid_m = tl.cdiv(gm, BLOCK_M)
                group1_width = GROUP_M * tl.cdiv(gn, BLOCK_N)
                group1_group_id = tile_idx_in_gemm // group1_width
                group1_group_size = tl.minimum(group1_grid_m - group1_group_id * GROUP_M, GROUP_M)
                (tile_m_idx, tile_n_idx) = (group1_group_id * GROUP_M + tile_idx_in_gemm % group1_group_size, tile_idx_in_gemm % group1_width // group1_group_size)
                offs_am = tile_m_idx * BLOCK_M
                offs_bn = tile_n_idx * BLOCK_N
                a_ptrs = tl.make_block_ptr(base=a_ptr, shape=(gm, gk), strides=(lda, 1), offsets=(offs_am, 0), block_shape=(BLOCK_M, BLOCK_K), order=(1, 0))
                b_ptrs = tl.make_block_ptr(base=b_ptr, shape=(gk, gn), strides=(ldb, 1), offsets=(0, offs_bn), block_shape=(BLOCK_K, BLOCK_N), order=(1, 0))
                accumulator = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)
                for kk in range(0, tl.cdiv(gk, BLOCK_K)):
                    a = tl.load(a_ptrs, boundary_check=(0, 1))
                    b = tl.load(b_ptrs, boundary_check=(0, 1))
                    accumulator = tl.dot(a, b, acc=accumulator)
                    a_ptrs = tl.advance(a_ptrs, (0, BLOCK_K))
                    b_ptrs = tl.advance(b_ptrs, (BLOCK_K, 0))
                offs_cm = tile_m_idx * BLOCK_M
                offs_cn = tile_n_idx * BLOCK_N
                c_ptrs = tl.make_block_ptr(base=c_ptr, shape=(gm, gn), strides=(ldc, 1), offsets=(offs_cm, offs_cn), block_shape=(BLOCK_M, BLOCK_N), order=(1, 0))
                out_ptrs = tl.make_block_ptr(base=out_ptr, shape=(gm, gn), strides=(ldc, 1), offsets=(offs_cm, offs_cn), block_shape=(BLOCK_M, BLOCK_N), order=(1, 0))
                ori_c = tl.load(c_ptrs, boundary_check=(0, 1))
                accumulator = ori_c * beta + accumulator * alpha
                c = accumulator.to(c_ptrs.dtype.element_ty)
                tl.store(out_ptrs, c, boundary_check=(0, 1))
                tile_idx += total_grid
        last_problem_end = current_problem_end

# ------------------------------------------------------------------ ② case 层
# (shape,) 的角色:第一个是典型用法,其余是泛化/尾块/退化用例。
#   (3, 17, 19, 13)
#   (4, 33, 35, 21)
#   (5, 65, 67, 29)
#   (4, 17, 19, 13)
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

SHAPES = ((3, 17, 19, 13), (4, 33, 35, 21))
DTYPES = ('bfloat16', 'float32', 'float16')
FIXED_META = {"BLOCK_M": 16, "BLOCK_N": 16, "BLOCK_K": 16, "GROUP_M": 4, "alpha": 1.25, "beta": -0.5}
LAUNCH_META = {"num_warps": 4, "num_stages": 1}
def _bf16_bits(values):
    import numpy as np
    words = np.asarray(values, dtype=np.float32).view(np.uint32)
    rounded = words + np.uint32(0x7FFF) + ((words >> np.uint32(16)) & np.uint32(1))
    return (rounded >> np.uint32(16)).astype(np.uint16)
def _bf16_values(bits):
    import numpy as np
    return (np.asarray(bits, dtype=np.uint16).astype(np.uint32) << np.uint32(16)).view(np.float32)
def ref(args, meta):
    import numpy as np

    sizes = np.asarray(args["group_gemm_sizes"], dtype=np.int32).reshape(-1, 3)
    results = {}
    for group, (m, n, k) in enumerate(sizes):
        a_raw = np.asarray(args[f"a_{group}"], dtype=np.uint16)
        b_raw = np.asarray(args[f"b_{group}"], dtype=np.uint16)
        c_raw = np.asarray(args[f"c_{group}"], dtype=np.uint16)
        a = _bf16_values(a_raw).reshape(int(m), int(k))
        b = _bf16_values(b_raw).reshape(int(k), int(n))
        c = _bf16_values(c_raw).reshape(int(m), int(n))
        value = float(meta["alpha"]) * (a @ b) + float(meta["beta"]) * c
        results[f"out_{group}"] = _bf16_bits(value).reshape(-1)
    return results
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    del dtype
    import numpy as np
    (groups, base_m, base_n, base_k) = (int(value) for value in shape)
    if min(groups, base_m, base_n, base_k) <= 0:
        raise ValueError('shape must be (positive groups, M, N, K)')
    from case_utils import fast_rng
    rng = fast_rng(seed)
    dimensions = [(base_m + 2 * g, base_n + 3 * g, base_k + g) for g in range(groups)]
    a_buffers = [_aligned(_bf16_bits(rng.uniform(-0.5, 0.5, m * k)), 'uint16') for (m, n, k) in dimensions]
    b_buffers = [_aligned(_bf16_bits(rng.uniform(-0.5, 0.5, k * n)), 'uint16') for (m, n, k) in dimensions]
    c_buffers = [_aligned(_bf16_bits(rng.uniform(-0.5, 0.5, m * n)), 'uint16') for (m, n, k) in dimensions]
    out_buffers = [_aligned(np.zeros(m * n), 'uint16') for (m, n, k) in dimensions]
    pointer_tables = {'group_a_ptrs': _aligned([array.ctypes.data for array in a_buffers], 'uint64'), 'group_b_ptrs': _aligned([array.ctypes.data for array in b_buffers], 'uint64'), 'group_c_ptrs': _aligned([array.ctypes.data for array in c_buffers], 'uint64'), 'group_out_ptrs': _aligned([array.ctypes.data for array in out_buffers], 'uint64')}
    sizes = _aligned(np.asarray(dimensions, dtype=np.int32).reshape(-1), 'int32')
    leading_dimensions = _aligned(np.asarray([(k, n, n) for (m, n, k) in dimensions], dtype=np.int32).reshape(-1), 'int32')
    args = {'M': base_m, 'N': base_n, 'K': base_k, **pointer_tables, 'group_gemm_sizes': sizes, 'g_lds': leading_dimensions, 'group_size': groups}
    meta = dict(FIXED_META)
    total_tiles = sum(((m + meta['BLOCK_M'] - 1) // meta['BLOCK_M'] * ((n + meta['BLOCK_N'] - 1) // meta['BLOCK_N']) for (m, n, k) in dimensions))
    allocations = {}
    relocations = []
    for (group, buffers) in enumerate(zip(a_buffers, b_buffers, c_buffers, out_buffers)):
        for (role, buffer) in zip(('a', 'b', 'c', 'out'), buffers):
            name = f'{role}_{group}'
            allocations[name] = buffer
            relocations.append({'table': f"group_{(role if role != 'out' else 'out')}_ptrs", 'entry': group, 'allocation': name, 'byte_offset': 0})
    inputs = ('group_a_ptrs', 'group_b_ptrs', 'group_c_ptrs', 'group_gemm_sizes', 'g_lds', *(f'{role}_{group}' for group in range(groups) for role in ('a', 'b', 'c')))
    outputs = tuple((f'out_{group}' for group in range(groups)))
    return {'kernel': grouped_gemm_kernel, 'grid': (total_tiles,), 'args': args, 'meta': meta, 'launch_meta': dict(LAUNCH_META), 'inputs': inputs, 'outputs': outputs, 'expected': ref({**args, **allocations}, meta), 'comparison': _comparison(outputs, exact=False, dtype='bfloat16'), 'pointer_dtypes': {'group_a_ptrs': 'uint64', 'group_b_ptrs': 'uint64', 'group_c_ptrs': 'uint64', 'group_out_ptrs': 'uint64', 'group_gemm_sizes': 'int32', 'g_lds': 'int32'}, 'buffer_extents': {**{name: int(value.size) for (name, value) in pointer_tables.items()}, 'group_gemm_sizes': 3 * groups, 'g_lds': 3 * groups, **{name: int(value.size) for (name, value) in allocations.items()}}, 'buffer_layouts': _layouts({**args, **allocations}), 'alignment': 64, 'aliases': {}, 'seed': int(seed), 'shape': tuple(shape), 'dtype': 'bfloat16', 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'allocations': allocations, 'oracle_args': dict(allocations), 'pointer_table_relocations': relocations, 'kernel_arg_order': ('M', 'N', 'K', 'group_a_ptrs', 'group_b_ptrs', 'group_c_ptrs', 'group_out_ptrs', 'group_gemm_sizes', 'g_lds', 'group_size'), 'coverage': {'complete_logical_output': True, 'grid_formula': '(sum_g ceil_div(M_g,BLOCK_M)*ceil_div(N_g,BLOCK_N),)', 'pointer_tables_relocated': True}}
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
