"""cumprod_dim1_kernel_log2exp2_early: 对数域前缀积,遇到 0 提前退出。

模式: 1D grid(行号),行内 for start in range(0, N, BLOCK) 分块:块内
log2 -> tl.cumsum -> 加跨块的 acc_l2 -> exp2 写回,并用 tl.sum 更新 acc_l2;
块末检查最后一个值是否为 0,是则把 finished 置位,后续块整块写 0(提前退出)。

文件只有两层:
  ① cumprod_dim1_kernel_log2exp2_early   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/cumprod_dim1_kernel_log2exp2_early', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.if_runtime', 'control.loop_carried', 'control.loop_runtime_bound', 'creation.arange', 'math.exp2', 'math.log2', 'memory.load.masked', 'memory.store.masked', 'reduce.cumprod', 'reduce.cumsum']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "test", "row": 13675, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "f1f46be991e1aa18469070fb62cdb42fe0880610127c24a0cd22473aece5ef1c"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def cumprod_dim1_kernel_log2exp2_early(x_ptr, y_ptr, N, BLOCK: tl.constexpr):
    pid = tl.program_id(0)
    row_start = pid * N
    acc_l2 = 0.0
    finished = tl.zeros((), dtype=tl.int1)
    for start in range(0, N, BLOCK):
        offs = start + tl.arange(0, BLOCK)
        mask = offs < N
        if finished == 0:
            x = tl.load(x_ptr + row_start + offs, mask=mask, other=1.0)
            lx2 = tl.log2(x)
            pref_l2 = tl.cumsum(lx2, axis=0) + acc_l2
            y = tl.exp2(pref_l2)
            tl.store(y_ptr + row_start + offs, y, mask=mask)
            acc_l2 += tl.sum(lx2, axis=0)
            last_col = tl.minimum(N - 1, start + BLOCK - 1)
            last_val = tl.load(y_ptr + row_start + last_col)
            finished = finished | (last_val == 0.0)
        else:
            tl.store(y_ptr + row_start + offs, 0.0, mask=mask)

# ------------------------------------------------------------------ ② case 层
# 典型用法:对数域前缀积(概率连乘/累积缩放),0 之后整行为 0 —— kernel 用
# finished 标志提前退出,所以数据里必须既有含 0 的行也有不含 0 的行。
#
# (rows, N):
#   典型  (64, 256)   含 0 的行(第 0 行第一个元素为 0)触发早退
#   规模  (128, 256)  典型规模 ×2:dim0 64->128
#   规模  (64, 512)  典型规模 ×2:dim1 256->512
#   泛化  (17, 300)   N 不整除 BLOCK,最后一块被掩码
#         (1, 1)      退化:单元素
SHAPES = ((64, 128), (17, 100), (1, 1))
# tl.log2/exp2 在本机 Triton 上只接受 fp32。
DTYPES = ('float32',)
BLOCK = 128


def ref(args, meta):
    """numpy 对照:按 kernel 的 log2/exp2 形式算(数学上等价于前缀积)。"""
    rows, n = int(args["N_ROWS"]), int(args["N"])
    x = np.asarray(args["x_ptr"], dtype=np.float64).reshape(rows, n)
    out = np.asarray(args["y_ptr"])
    y = np.exp2(np.cumsum(np.log2(x), axis=1))
    return {"y_ptr": y.reshape(-1).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    rows, n = (int(v) for v in shape)
    if min(rows, n) <= 0:
        raise ValueError(f"shape must be positive (rows, N), got {shape}")

    # 连乘因子取 1/256 网格上的 [1, 1.05):log2 域里不溢出;第 0 行第 0 个元素
    # 为 0(log2(-inf) -> exp2 得 0),之后整行应为 0(早退分支);第 1 行全 1
    # (前缀积恒为 1,不触发早退)。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (1.0 + rng.integers(0, 13, (rows, n), dtype=np.int16) / 256.0).astype(np.float32)
    x[0, 0] = 0.0
    if n > 1:
        x[0, 1:] = 1.0
    if rows > 1:
        x[1, :] = 1.0

    args = {"x_ptr": x.reshape(-1), "y_ptr": np.full(rows * n, -7.0, np.float32),
            "N": np.int32(n), "N_ROWS": rows}
    meta = {"BLOCK": BLOCK}
    case = {"args": args, "meta": meta, "grid": (rows,), "outputs": ("y_ptr",),
            "expected": ref(args, meta)}
    # log2/exp2 往返误差在 f32 的 1e-6 量级;前缀和越长误差越大,给 1e-4。
    case["comparison"] = {"y_ptr": {"comparator": "allclose", "exact": False,
                                    "rtol": 1e-4, "atol": 1e-4, "equal_nan": True}}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, cumprod_dim1_kernel_log2exp2_early, DTYPES,
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
