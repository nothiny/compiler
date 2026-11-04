"""sum_dim1_grouped_kernel: 取自 makora 数据集 test split 第 7373 行(上游 kernel sum_dim1_grouped_kernel)。

模式: 单个 @triton.jit 计算单元。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。constexpr 参数: BLOCK_M, BLOCK_N, GROUP_B。

文件只有两层:
  ① sum_dim1_grouped_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/grouped_strided_sum', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": []}
SOURCE = {'dataset': 'makora-ai/triton-gpu-latency', 'revision': '3b30911350fa433e1cb97ec2a41bd8908dd35d5d', 'file': 'data/test.parquet', 'row': 7373, 'source_sha256': '91367266827f44bf13aae94c7c70fc3c58c4f754f7e11bb4381b0eaeeceaf903', 'upstream_kernel': 'sum_dim1_grouped_kernel', 'license': 'Apache-2.0', 'adaptations': ['extract single JIT without executing original Torch model', 'replace autotune selection with explicit small legal tiles in scoped fixtures; JIT body unchanged', 'disable reduction-length M specialization for observable runtime zero/one/many loop configurations'], 'scope': 'local proposal only; not default corpus or claimed full original workload'}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit(do_not_specialize=['M'])
def sum_dim1_grouped_kernel(x_ptr, out_ptr, B, M, N, stride_b, stride_m, stride_n, out_stride_b, out_stride_m, out_stride_n, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, GROUP_B: tl.constexpr):
    pid_n = tl.program_id(0)
    pid_bg = tl.program_id(1)
    offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    n_mask = offs_n < N
    offs_b = pid_bg * GROUP_B + tl.arange(0, GROUP_B)
    b_mask = offs_b < B
    acc = tl.zeros((GROUP_B, BLOCK_N), dtype=tl.float32)
    m_range = tl.arange(0, BLOCK_M)
    m_start = 0
    while m_start < M:
        m_idx = m_start + m_range
        m_mask = m_idx < M
        ptrs = offs_b[:, None, None] * stride_b + m_idx[None, :, None] * stride_m + offs_n[None, None, :] * stride_n
        mask = b_mask[:, None, None] & m_mask[None, :, None] & n_mask[None, None, :]
        x_tile = tl.load(x_ptr + ptrs, mask=mask, other=0.0).to(tl.float32)
        acc += tl.sum(x_tile, axis=1)
        m_start += BLOCK_M
    out_ptrs = offs_b[:, None] * out_stride_b + 0 * out_stride_m + offs_n[None, :] * out_stride_n
    tl.store(out_ptr + out_ptrs, acc, mask=b_mask[:, None] & n_mask[None, :])

# ------------------------------------------------------------------ ② case 层
# 典型用法依据:数据集原始程序的常量(已按 sha256 核对原始文件):
#   batch_size = 128
# 下面 SHAPES 只缩小了这些配置里的批类维度,结构维度按原值保留。
# (shape,) 的角色:第一个是典型用法,其余是泛化/尾块/退化用例。
#   (3, 0, 5)
#   (3, 1, 5)
#   (4, 16, 8)
#   (3, 17, 5)
# DTYPES: float32 —— 原始用途的 dtype 在前;非法域(例如本机 Triton 只吃 fp32 的exp/sqrt/erf/atomic)的算子只声明合法的那一种。
#   规模    (6, 0, 5)  典型规模 ×2:dim0 3->6
#   规模    (3, 0, 10)  典型规模 ×2:dim2 5->10

SHAPES = ((3, 0, 5), (6, 0, 5), (3, 0, 10))
DTYPES = ('float32', 'float16', 'bfloat16')
FIXED_META = {"BLOCK_M": 8, "BLOCK_N": 4, "GROUP_B": 2}
LAUNCH_META = {"num_warps": 4}
SUPPORT_STATUS = "supported"
COMPARISON_PROFILE = "reduction"
CASE_SCHEMA = 3
VALIDATION_SCOPE = "full-launch-correctness"
def ref(args, meta):
    """Independent NumPy oracle over the strided physical buffers."""
    import numpy as np

    x = np.asarray(args["x_ptr"])
    out = np.asarray(args["out_ptr"])
    b, m, n = int(args["B"]), int(args["M"]), int(args["N"])
    sb, sm, sn = int(args["stride_b"]), int(args["stride_m"]), int(args["stride_n"])
    ob, on = int(args["out_stride_b"]), int(args["out_stride_n"])
    result = out.astype(np.float32).copy()
    for batch in range(b):
        for col in range(n):
            total = np.float32(0)
            for r in range(m):
                total += np.float32(x[batch * sb + r * sm + col * sn])
            result[batch * ob + col * on] = total
    return {"out_ptr": result.astype(out.dtype, copy=False).copy()}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=20261019):
    """Build one complete launch and correctness case.

    The physical buffers are padded and strided: the reduction axis (M) is the
    middle axis with a non-unit stride, and the output keeps its own padded
    layout with unwritten gaps preserved. Exactly representable integer-valued
    payloads make the scoped oracle exact.
    """
    import numpy as np

    shape = tuple(int(value) for value in shape)
    if len(shape) != 3 or any(value < 0 for value in shape):
        raise ValueError("grouped_strided_sum shape must be a (B, M, N) triple with M >= 0")
    dtype_text = str(dtype)
    if dtype_text not in DTYPES:
        raise ValueError(f"unsupported grouped_strided_sum dtype: {dtype_text}")
    b, m, n = shape
    sb, sm, sn = m * (2 * n + 3) + 7, 2 * n + 3, 2
    ob, on = 2 * n + 5, 2

    x = np.full(b * sb, 97, np.float32)
    out = np.full(b * ob, 777, np.float32)
    for batch in range(b):
        for r in range(m):
            for col in range(n):
                x[batch * sb + r * sm + col * sn] = 100 * batch + 10 * r + col + 1
    args = {"x_ptr": x, "out_ptr": out, "B": np.int32(b), "M": np.int32(m), "N": np.int32(n),
            "stride_b": np.int64(sb), "stride_m": np.int64(sm), "stride_n": np.int64(sn),
            "out_stride_b": np.int64(ob), "out_stride_m": np.int64(0), "out_stride_n": np.int64(on)}
    meta = dict(FIXED_META)
    launch_meta = dict(LAUNCH_META)
    grid = ((n + meta["BLOCK_N"] - 1) // meta["BLOCK_N"], (b + meta["GROUP_B"] - 1) // meta["GROUP_B"])

    expected = ref(args, meta)
    arrays = {name: value for name, value in args.items() if isinstance(value, np.ndarray)}
    return {"kernel": sum_dim1_grouped_kernel, "grid": grid, "args": args, "meta": meta,
            "launch_meta": launch_meta, "inputs": ("x_ptr",), "outputs": ("out_ptr",),
            "expected": expected,
            "comparison": {"out_ptr": {"profile": COMPARISON_PROFILE, "comparator": "array_equal",
                                       "exact": True}},
            "pointer_dtypes": {name: str(value.dtype) for name, value in arrays.items()},
            "buffer_extents": {name: int(value.size) for name, value in arrays.items()},
            "buffer_layouts": {name: {"shape": tuple(int(v) for v in value.shape),
                                      "strides": tuple(int(s // value.dtype.itemsize) for s in value.strides)}
                               for name, value in arrays.items()},
            "alignment": 0, "aliases": {}, "seed": int(seed), "shape": shape, "dtype": dtype_text,
            "support_status": SUPPORT_STATUS, "validation_scope": VALIDATION_SCOPE,
            "coverage": {"complete_logical_output": True,
                         "logical_output": "out[b*ob + c*on] for 0<=b<B, 0<=c<N",
                         "preserved_physical_padding": True,
                         "dynamic_loop_trips": (m + meta["BLOCK_M"] - 1) // meta["BLOCK_M"]}}
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
