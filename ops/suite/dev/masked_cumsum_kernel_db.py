"""masked_cumsum_kernel_db: 带掩码的行内前缀和(attention 的 causal 前缀和)。

模式: 1D grid(行号),每行先用 n_full = N // BLOCK_N 做整块循环:块内
load(mask=m) 后 tl.cumsum(axis=0) 加上跨块标量 running,再推进 running;
剩下的 N % BLOCK_N 个列用 carry=1 的尾块单独处理(尾块的 running 也要接着用)。
掩码以外的元素按 0 参与前缀和。

文件只有两层:
  ① masked_cumsum_kernel_db   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/masked_cumsum_kernel_db', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.if_runtime', 'control.loop_runtime_bound', 'creation.arange', 'memory.load.masked', 'memory.store.masked', 'reduce.cumsum', 'reduce.sum.axis0']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 142685, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "3b8b28d86aa15d2968c86f9c4027cb88dd0012b08c01fa8d6b35ad44e96983d0"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def masked_cumsum_kernel_db(x_ptr, m_ptr, o_ptr, M, N, BLOCK_N: tl.constexpr):
    row = tl.program_id(0)
    base_x = x_ptr + row * N
    base_m = m_ptr + row * N
    base_o = o_ptr + row * N
    running = 0.0
    offs = tl.arange(0, BLOCK_N)
    n_full = N // BLOCK_N
    if n_full > 0:
        m0 = tl.load(base_m + offs)
        m0 = m0.to(tl.int1)
        x0 = tl.load(base_x + offs, mask=m0, other=0.0)
        for i in range(n_full - 1):
            next_off = (i + 1) * BLOCK_N
            m1 = tl.load(base_m + next_off + offs)
            m1 = m1.to(tl.int1)
            x1 = tl.load(base_x + next_off + offs, mask=m1, other=0.0)
            scan0 = tl.cumsum(x0, axis=0) + running
            tl.store(base_o + i * BLOCK_N + offs, scan0)
            running += tl.sum(x0)
            x0 = x1
        scan_last = tl.cumsum(x0, axis=0) + running
        tl.store(base_o + (n_full - 1) * BLOCK_N + offs, scan_last)
        running += tl.sum(x0)
    rem = N - n_full * BLOCK_N
    if rem:
        in_bounds = offs < rem
        m = tl.load(base_m + n_full * BLOCK_N + offs, mask=in_bounds, other=0)
        m = m.to(tl.int1)
        x = tl.load(base_x + n_full * BLOCK_N + offs, mask=in_bounds & m, other=0.0)
        scan = tl.cumsum(x, axis=0) + running
        tl.store(base_o + n_full * BLOCK_N + offs, scan, mask=in_bounds)

# ------------------------------------------------------------------ ② case 层
# 典型用法:causal attention 的 softmax 前缀和/累积 mask 权重。原始程序是 2D
# (rows, N) 的行式扫描;这里取 (128, 2048)(一个块数较少、能覆盖跨块 carry 的配置)。
#
# (rows, N):
#   典型  (128, 2048)  128 行 x 2048 列:8 个整块,跨块 carry 被反复使用
#   规模  (256, 2048)  典型规模 ×2:dim0 128->256
#   规模  (128, 4096)  典型规模 ×2:dim1 2048->4096
#   泛化  (17, 1000)   N 不整除 BLOCK_N:走完整块后还剩 232 列的尾块分支
#         (1, 1)      退化:单元素(尾块分支,且没有整块)
SHAPES = ((128, 128), (17, 100), (1, 1))
# 原始程序是 fp32(cumsum 在 f32 里累加)。
DTYPES = ('float32', 'float16', 'bfloat16')
BLOCK_N = 256


def ref(args, meta):
    """numpy 对照:where(m, x, 0) 的行内前缀和(float64)。"""
    rows, n = int(args["M"]), int(args["N"])
    x = np.asarray(args["x_ptr"], dtype=np.float64).reshape(rows, n)
    m = np.asarray(args["m_ptr"]).reshape(rows, n).astype(bool)
    out = np.asarray(args["o_ptr"])
    return {"o_ptr": np.cumsum(np.where(m, x, 0.0), axis=1).reshape(-1).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    rows, n = (int(v) for v in shape)
    if min(rows, n) <= 0:
        raise ValueError(f"shape must be positive (rows, N), got {shape}")

    # 值取 1/16 网格上的 [-4, 4);掩码是下三角(因果)再掺一点随机:
    # 于是每行既有被屏蔽的前缀也有全开的行,前缀和的"跳跃"边界都被覆盖。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (rng.integers(-64, 64, (rows, n), dtype=np.int16) / 16).astype(np.float32)
    m = (np.arange(n)[None, :] <= (np.arange(rows)[:, None] * n // max(rows, 1))).astype(np.int8)
    m |= rng.integers(0, 2, (rows, n), dtype=np.int8)
    # 语义边界:第 0 行全屏蔽(前缀和恒为 0);第 1 行全开(退化成普通 cumsum)。
    m[0, :] = 0
    if rows > 1:
        m[1, :] = 1

    args = {"x_ptr": x.reshape(-1), "m_ptr": m.reshape(-1),
            "o_ptr": np.full(rows * n, -7.0, np.float32), "M": np.int32(rows), "N": np.int32(n)}
    meta = {"BLOCK_N": BLOCK_N}
    return {"args": args, "meta": meta, "grid": (rows,), "outputs": ("o_ptr",),
            "expected": ref(args, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, masked_cumsum_kernel_db, DTYPES,
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
