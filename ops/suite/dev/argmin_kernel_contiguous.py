"""argmin_kernel_contiguous: 沿中间维(arg=1)取最小值下标,分块 + 跨块合并。

模式: pid 拆成 (前置维、后置维) 两个索引,行内用 for start_n in range(0, S_dim,
BLOCK_SIZE_N) 的分块循环:每块求局部 min 与 argmin,再用 tl.where 与已记录的
best_val/best_idx 比较合并(严格的 < 保证并列取最左)。stride_n 由调用方给出,
支持沿中间维跨步读取。

文件只有两层:
  ① argmin_kernel_contiguous   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'medium/argmin_kernel_contiguous', "group": 'medium', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.loop_runtime_bound', 'creation.arange', 'memory.load.masked', 'reduce.min.axis0', 'reduce.argmin']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 83486, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "1e339dfd482a6cc7c85d1573526652f821d17912aa4013b35fab9c7ef0f50228"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def argmin_kernel_contiguous(x_ptr, out_ptr, S_dim, S_post, stride_n, BLOCK_SIZE_N: tl.constexpr):
    pid = tl.program_id(0)
    idx_pre = pid // S_post
    idx_post = pid % S_post
    offset_base = idx_pre * (S_dim * S_post) + idx_post
    best_val = float('inf')
    best_idx = 0
    for start_n in range(0, S_dim, BLOCK_SIZE_N):
        offsets = start_n + tl.arange(0, BLOCK_SIZE_N)
        mask = offsets < S_dim
        val_offsets = offset_base + offsets * stride_n
        vals = tl.load(x_ptr + val_offsets, mask=mask, other=float('inf'))
        local_min = tl.min(vals, axis=0)
        local_argmin = tl.argmin(vals, axis=0)
        cond = local_min < best_val
        best_val = tl.where(cond, local_min, best_val)
        best_idx = tl.where(cond, start_n + local_argmin, best_idx)
    tl.store(out_ptr + pid, best_idx)

# ------------------------------------------------------------------ ② case 层
# 典型用法:三维张量沿中间维求最小值下标。原始 (128, 4096, 4095) fp32:
# 保留被归约维 S_dim=4096 与短的后置维,把后置维与前置维都缩小。
#
# (S_dim, S_post, N_pre):
#   典型  (4096, 128, 2)  S_dim = 4096(原始值),后置维缩到 128,前置维 2
#   规模  (8192, 128, 2)  典型规模 ×2:dim0 4096->8192
#   规模  (4096, 256, 2)  典型规模 ×2:dim1 128->256
#   泛化  (1000, 7, 3)    S_dim 不整除 BLOCK,分块循环的尾块被掩码
#         (1, 1, 1)      退化:单元素
SHAPES = ((128, 128, 2), (100, 7, 3), (1, 1, 1))
# 原始数据是 fp32;tl.min/argmin 只是比较+选择,半精度合法。
DTYPES = ("float32", "float16", "bfloat16")
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}
BLOCK_SIZE_N = 256


def ref(args, meta):
    """numpy 对照:沿 axis=1 取 argmin(首个最小值)。"""
    s_dim, s_post, n_pre = int(args["S_dim"]), int(args["S_post"]), int(args["N_pre"])
    x = np.asarray(args["x_ptr"]).reshape(n_pre, s_dim, s_post)
    return {"out_ptr": np.argmin(x, axis=1).reshape(-1).astype(np.int32)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    s_dim, s_post, n_pre = (int(v) for v in shape)
    if min(s_dim, s_post, n_pre) <= 0:
        raise ValueError(f"shape must be positive, got {shape}")

    # 1/16 网格上的正态值:最小值位置在半精度下同样精确。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (np.clip(np.rint(rng.standard_normal((n_pre, s_dim, s_post), dtype=np.float32) * 32),
                 -128, 127) / 16).astype(_HOST_DTYPE[dtype])
    # 语义边界:第 0 行的最小值放在被归约维的最后一个位置(分块循环的尾块)、
    # 第 1 行整行并列(取最左)。
    x[0, -1, :] = -8.0
    if n_pre > 1:
        x[1, :, :] = 1.0
    if n_pre > 2:
        x[2, :, 0] = 0.0

    args = {"x_ptr": x.reshape(-1), "out_ptr": np.zeros(n_pre * s_post, np.int32),
            "S_dim": np.int32(s_dim), "S_post": np.int32(s_post),
            "stride_n": np.int32(s_post), "N_pre": n_pre}
    meta = {"BLOCK_SIZE_N": BLOCK_SIZE_N}
    case = {"args": args, "meta": meta, "grid": (n_pre * s_post,),
            "outputs": ("out_ptr",), "expected": ref(args, meta)}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {"x_ptr": "bfloat16"}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;下标输出按位精确比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, argmin_kernel_contiguous, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=True)


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
