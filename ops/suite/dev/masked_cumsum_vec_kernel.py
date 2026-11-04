"""masked_cumsum_vec_kernel: 向量化网格上的带掩码前缀和(两级 cumsum)。

模式: 1D grid(行号),列方向按 (BLOCK_COLS, VEC) 的二维块推进:先在 VEC 这一维
用 tl.cumsum(axis=1) 求块内前缀,再对每行 group_sum 沿 BLOCK_COLS 求
tl.cumsum(axis=0) 得到组间偏移,两者相加并加上跨块 running 得到全局前缀和。
掩码为 0 的 lane 不参与。T_KIND/ACC_KIND 是 constexpr 的指针/累加 dtype,
stride 都有 tl.multiple_of 提示(要求 16 的整数倍)。

文件只有两层:
  ① masked_cumsum_vec_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/masked_cumsum_vec_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.loop_runtime_bound', 'cast.to', 'creation.arange', 'hint.multiple_of', 'memory.load.masked', 'memory.store.masked', 'reduce.cumsum', 'reduce.sum.axis1', 'tile.2d']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 143296, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "8b172491b5cb3fc9e8080633f3f4c277053f9762c9154060b88305c914513463"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def masked_cumsum_vec_kernel(x_ptr, m_ptr, o_ptr, stride_x_row: tl.int32, stride_m_row: tl.int32, stride_o_row: tl.int32, n_cols: tl.int32, T_KIND: tl.constexpr, ACC_KIND: tl.constexpr, BLOCK_COLS: tl.constexpr, VEC: tl.constexpr):
    row = tl.program_id(0)
    x_row = x_ptr + row * stride_x_row
    m_row = m_ptr + row * stride_m_row
    o_row = o_ptr + row * stride_o_row
    tl.multiple_of(stride_x_row, 16)
    tl.multiple_of(stride_m_row, 16)
    tl.multiple_of(stride_o_row, 16)
    running = tl.zeros((), dtype=ACC_KIND)
    for start in range(0, n_cols, BLOCK_COLS * VEC):
        grp = tl.arange(0, BLOCK_COLS)[:, None]
        lane = tl.arange(0, VEC)[None, :]
        idx = start + grp * VEC + lane
        in_bounds = idx < n_cols
        x_vals = tl.load(x_row + idx, mask=in_bounds, other=0, cache_modifier='.cg')
        m_vals = tl.load(m_row + idx, mask=in_bounds, other=0, cache_modifier='.cg')
        x_acc = tl.cast(x_vals, ACC_KIND) if T_KIND is not ACC_KIND else x_vals
        y = tl.where(m_vals, x_acc, tl.zeros_like(x_acc))
        local_pref = tl.cumsum(y, axis=1)
        group_sum = tl.sum(y, axis=1)
        group_pref_incl = tl.cumsum(group_sum, axis=0)
        group_offset_excl = running + (group_pref_incl - group_sum)
        pref = local_pref + group_offset_excl[:, None]
        if T_KIND is tl.float16:
            tl.store(o_row + idx, pref.to(tl.float16), mask=in_bounds)
        elif T_KIND is tl.bfloat16:
            tl.store(o_row + idx, pref.to(tl.bfloat16), mask=in_bounds)
        elif T_KIND is tl.float64:
            tl.store(o_row + idx, pref.to(tl.float64), mask=in_bounds)
        else:
            tl.store(o_row + idx, pref.to(tl.float32), mask=in_bounds)
        running += tl.sum(group_sum, axis=0)

# ------------------------------------------------------------------ ② case 层
# 典型用法:attention/linear-attention 的掩码前缀和(比逐块标量版少一半的串行
# 依赖)。原始程序是 2D (rows, n_cols) 行式扫描;这里取 (256, 4096)。
#
# (rows, n_cols):
#   典型  (256, 4096)  256 行 x 4096 列,列方向 128 组 x VEC=4 的二维块
#   规模  (512, 4096)  典型规模 ×2:dim0 256->512
#   规模  (256, 8192)  典型规模 ×2:dim1 4096->8192
#   泛化  (17, 1000)   n_cols 不整除 BLOCK_COLS*VEC,尾块被掩码
#         (1, 1)      退化:单元素
SHAPES = ((128, 128), (17, 100), (1, 1))
# 原始程序是 fp32;kernel 的 store 分支按 T_KIND 选择,这里同时覆盖 fp32 与 fp16
# (fp16 输入 + fp32 累加,与真实 attention 的混合精度一致)。
DTYPES = ("float32", "float16", "bfloat16")
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}
BLOCK_COLS, VEC = 128, 4


def _tl_kind(dtype):
    import triton.language as tl
    return {"float32": tl.float32, "float16": tl.float16, "bfloat16": tl.bfloat16}[dtype]


def ref(args, meta):
    """numpy 对照:where(m, x, 0) 的行内前缀和,在 float64 里算再转回。"""
    rows, n = int(args["N_ROWS"]), int(args["n_cols"])
    x = np.asarray(args["x_ptr"], dtype=np.float64).reshape(rows, n)
    m = np.asarray(args["m_ptr"]).reshape(rows, n).astype(bool)
    out = np.asarray(args["o_ptr"])
    return {"o_ptr": np.cumsum(np.where(m, x, 0.0), axis=1).reshape(-1).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    rows, n = (int(v) for v in shape)
    if min(rows, n) <= 0:
        raise ValueError(f"shape must be positive (rows, n_cols), got {shape}")
    host = _HOST_DTYPE[dtype]

    # 1/16 网格上的 [-4, 4);掩码为下三角 + 随机抖动(因果 + 稀疏两种模式都有)。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (rng.integers(-64, 64, (rows, n), dtype=np.int16) / 16).astype(host)
    m = (np.arange(n)[None, :] <= (np.arange(rows)[:, None] * n // max(rows, 1))).astype(np.int8)
    m |= rng.integers(0, 2, (rows, n), dtype=np.int8)
    m[0, :] = 0
    if rows > 1:
        m[1, :] = 1

    out_dtype = np.float32 if dtype == "bfloat16" else np.dtype(dtype)
    args = {"x_ptr": x.reshape(-1), "m_ptr": m.reshape(-1),
            "o_ptr": np.full(rows * n, -7.0, dtype=out_dtype),
            "stride_x_row": np.int32(n), "stride_m_row": np.int32(n),
            "stride_o_row": np.int32(n), "n_cols": np.int32(n), "N_ROWS": rows}
    meta = {"T_KIND": _tl_kind(dtype), "ACC_KIND": _tl_kind("float32"),
            "BLOCK_COLS": BLOCK_COLS, "VEC": VEC}
    case = {"args": args, "meta": meta, "grid": (rows,), "outputs": ("o_ptr",),
            "expected": ref(args, meta)}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {"x_ptr": "bfloat16", "o_ptr": "bfloat16"}
        case["comparison"] = {"o_ptr": {"comparator": "allclose", "exact": False,
                                        "rtol": 5e-3, "atol": 5e-3, "equal_nan": True}}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, masked_cumsum_vec_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float32'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float32': 'float32', 'float16': 'float16', 'bfloat16': 'bfloat16'}


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
