"""cumprod_dim1_grouped_mixed_kernel: 分组行前缀积,两种模式(直接乘 / 对数域)。

模式: 1D grid(行组),每个 program 处理 GROUP_ROWS 行、按 BLOCK_COLS 列块推进。
use_log 是运行时开关:use_log == 0 时用 tl.cumprod 直接连乘,并在 running == 0 时
把该行标记 not alive(之后整行写 0,零传播提前退出);use_log == 1 时改走
y = exp(cumsum(log(clamp(x, eps, inf)))) 的对数域扫描,避免上溢/下溢。

文件只有两层:
  ① cumprod_dim1_grouped_mixed_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/cumprod_dim1_grouped_mixed_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.if_runtime', 'control.loop_runtime_bound', 'creation.arange', 'creation.full', 'math.exp', 'math.log', 'math.maximum', 'memory.load.masked', 'memory.store.masked', 'reduce.cumprod', 'reduce.cumsum']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "test", "row": 13709, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "3b382f9888f57d905febf2d60b9b3cc0fd941080d9633f593dd7875756af0e6f"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def cumprod_dim1_grouped_mixed_kernel(x_ptr, y_ptr, batch_size, length, epsilon, use_log, BLOCK_COLS: tl.constexpr, GROUP_ROWS: tl.constexpr):
    """
    GROUP_ROWS-row cumulative product along dim=1 for [batch_size, length].

    Two execution modes (selected per-launch via use_log):
      - use_log == 0: direct product using tl.cumprod with per-row early-out when running == 0
      - use_log == 1: log-space scan y = exp(cumsum(log(clamp(x, eps, inf)))) for better stability.

    Each program instance handles GROUP_ROWS rows and walks columns in BLOCK_COLS tiles;
    memory accesses are fully coalesced in row-major order.
    """
    pid = tl.program_id(0)
    row_start = pid * GROUP_ROWS
    rows = row_start + tl.arange(0, GROUP_ROWS)
    row_mask = rows < batch_size
    if use_log == 0:
        running = tl.full((GROUP_ROWS,), 1.0, tl.float32)
        alive = tl.full((GROUP_ROWS,), 1, tl.int1)
        for offset in range(0, length, BLOCK_COLS):
            cols = offset + tl.arange(0, BLOCK_COLS)
            col_mask = cols < length
            full_mask = row_mask[:, None] & col_mask[None, :]
            active_mask = alive[:, None] & full_mask
            x_block = tl.load(x_ptr + rows[:, None] * length + cols[None, :], mask=active_mask, other=1.0)
            block_cum = tl.cumprod(x_block, axis=1) * running[:, None]
            out_block = tl.where(active_mask, block_cum, 0.0)
            tl.store(y_ptr + rows[:, None] * length + cols[None, :], out_block, mask=full_mask)
            last_idx = BLOCK_COLS - 1
            last_col = offset + last_idx
            has_last = last_col < length
            last_vals = tl.load(y_ptr + rows * length + last_col, mask=row_mask & has_last & alive, other=running)
            running = tl.where(row_mask & has_last & alive, last_vals, running)
            alive = alive & (running != 0.0)
    else:
        eps = epsilon
        running_log = tl.full((GROUP_ROWS,), 0.0, tl.float32)
        for offset in range(0, length, BLOCK_COLS):
            cols = offset + tl.arange(0, BLOCK_COLS)
            col_mask = cols < length
            full_mask = row_mask[:, None] & col_mask[None, :]
            x_block = tl.load(x_ptr + rows[:, None] * length + cols[None, :], mask=full_mask, other=1.0)
            x_clamped = tl.maximum(x_block, eps)
            log_block = tl.log(x_clamped)
            log_cumsum = tl.cumsum(log_block, axis=1) + running_log[:, None]
            y_block = tl.exp(log_cumsum)
            tl.store(y_ptr + rows[:, None] * length + cols[None, :], y_block, mask=full_mask)
            last_idx = BLOCK_COLS - 1
            last_col = offset + last_idx
            has_last = last_col < length
            last_vals = tl.load(y_ptr + rows * length + last_col, mask=row_mask & has_last, other=1.0)
            running_log = tl.where(row_mask & has_last, tl.log(tl.maximum(last_vals, eps)), running_log)

# ------------------------------------------------------------------ ② case 层
# 典型用法:同一算子的两种数值策略(稳定优先时走对数域)。原始程序是 2D
# (batch, length) 行式扫描;length 取 256(连乘不溢出),两个 shape 分别选
# use_log=0 与 use_log=1,把两条运行时分支都覆盖。
#
# (batch, length):
#   典型  (64, 256)   use_log=0:直接连乘 + 零传播早退
#   规模  (128, 256)  典型规模 ×2:dim0 64->128;use_log=1 的对数域扫描放到更大 batch 上
#   泛化  (33, 300)   use_log=1:对数域扫描(f32 除法精度,容差放宽到 1e-4)
#         (1, 1)      退化:单元素(use_log=0)
SHAPES = ((1, 1),)
_USE_LOG = {(64, 256): 0, (128, 256): 1, (33, 300): 1, (1, 1): 0}
# 原始程序是 fp32;对数域版依赖 tl.log/exp(fp32 only),所以只声明 f32。
DTYPES = ('float32', 'float16', 'bfloat16')
GROUP_ROWS, BLOCK_COLS = 4, 128
EPS = 1e-6


def ref(args, meta):
    """numpy 对照:float64 连乘;对数域版按 exp(cumsum(log(clamp(x)))) 算。"""
    rows, length = int(args["batch_size"]), int(args["length"])
    x = np.asarray(args["x_ptr"], dtype=np.float64).reshape(rows, length)
    out = np.asarray(args["y_ptr"])
    if int(args["use_log"]):
        y = np.exp(np.cumsum(np.log(np.maximum(x, np.float64(args["epsilon"]))), axis=1))
    else:
        y = np.cumprod(x, axis=1)
    return {"y_ptr": y.reshape(-1).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    rows, length = (int(v) for v in shape)
    if min(rows, length) <= 0:
        raise ValueError(f"shape must be positive (batch, length), got {shape}")
    use_log = _USE_LOG[(rows, length)]

    # 连乘因子取 1/256 网格上的 [1, 1.05):不溢出;第 0 行的第二个元素取 0
    # (直接模式下的零传播 + 早退分支)。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (1.0 + rng.integers(0, 13, (rows, length), dtype=np.int16) / 256.0).astype(np.float32)
    x[0, 0] = 0.0
    if length > 1:
        x[0, 1:] = 1.0

    args = {"x_ptr": x.reshape(-1), "y_ptr": np.full(rows * length, -7.0, np.float32),
            "batch_size": np.int32(rows), "length": np.int32(length),
            "epsilon": np.float32(EPS), "use_log": np.int32(use_log)}
    meta = {"BLOCK_COLS": BLOCK_COLS, "GROUP_ROWS": GROUP_ROWS}
    grid = ((rows + GROUP_ROWS - 1) // GROUP_ROWS,)
    case = {"args": args, "meta": meta, "grid": grid, "outputs": ("y_ptr",),
            "expected": ref(args, meta)}
    # 对数域版多了一次 log/exp 往返,按 1e-4 比较(仍在 f32 的有效位数内)。
    tol = 1e-4 if use_log else 1e-5
    case["comparison"] = {"y_ptr": {"comparator": "allclose", "exact": False,
                                    "rtol": tol, "atol": tol, "equal_nan": True}}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, cumprod_dim1_grouped_mixed_kernel, DTYPES,
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
