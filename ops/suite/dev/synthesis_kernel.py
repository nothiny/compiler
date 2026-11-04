"""synthesis_kernel: S4/S4D 滤波器合成 —— 由 (a, theta, q, q_init, dt) 生成 f 与 y_init。

模式: 2D grid(C*H, L 方向块),每个 program 负责一个 (c, h) 的一段序列位置:
先按 learn_dt 决定 dt(exp(log_dt[h]) 或 1/(L-1)),再用 for d in 块的 D 循环
按 D 分块读参数,算 base = 2*dt*exp(-|a|*zk)*cos(theta*zk)(is_disc 时用
exp(zk*log|a|)),与 q / q_init 相乘后沿 D 归约累加到 f 与 y_init。三个开关
learn_dt/use_initial/is_disc 都是 constexpr。

文件只有两层:
  ① synthesis_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/synthesis_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.if_constexpr', 'control.loop_runtime_bound', 'creation.arange', 'creation.zeros', 'math.abs', 'math.cos', 'math.exp', 'math.log', 'math.maximum', 'math.expand_dims', 'memory.load.masked', 'memory.store.masked', 'reduce.sum.axis1']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "test", "row": 42456, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "1b4b952b3040d7f1063232c31e81ea0b6a500e34db83121d007ea137ef00e114"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def synthesis_kernel(a_ptr, theta_ptr, q_ptr, q_init_ptr, log_dt_ptr, f_ptr, y_init_ptr, C, H, D, L, learn_dt: tl.constexpr, use_initial: tl.constexpr, is_disc: tl.constexpr, BLOCK_SIZE_D: tl.constexpr, BLOCK_SIZE_L: tl.constexpr):
    """
    Compute filter f and initial term y_init for each (C, H, L).
    Grid: (C*H, ceil(L/BLOCK_SIZE_L))
    Each program handles a block of BLOCK_SIZE_L sequence positions for a specific (C,H).
    """
    pid_ch = tl.program_id(0)
    pid_l_block = tl.program_id(1)
    c_idx = pid_ch // H
    h_idx = pid_ch % H
    if learn_dt:
        dt = tl.exp(tl.load(log_dt_ptr + h_idx))
    else:
        dt = 1.0 / (L - 1.0)
    l_offsets = pid_l_block * BLOCK_SIZE_L + tl.arange(0, BLOCK_SIZE_L)
    l_mask = l_offsets < L
    zk = l_offsets.to(tl.float32) * dt
    acc_f = tl.zeros([BLOCK_SIZE_L], dtype=tl.float32)
    acc_init = tl.zeros([BLOCK_SIZE_L], dtype=tl.float32)
    for d_block_start in range(0, D, BLOCK_SIZE_D):
        d_offsets = d_block_start + tl.arange(0, BLOCK_SIZE_D)
        d_mask = d_offsets < D
        param_base = (c_idx * H + h_idx) * D
        a = tl.load(a_ptr + param_base + d_offsets, mask=d_mask, other=0.0)
        theta = tl.load(theta_ptr + param_base + d_offsets, mask=d_mask, other=0.0)
        q = tl.load(q_ptr + param_base + d_offsets, mask=d_mask, other=0.0)
        q_init = tl.load(q_init_ptr + param_base + d_offsets, mask=d_mask, other=0.0)
        zk_expanded = tl.expand_dims(zk, 1)
        theta_expanded = tl.expand_dims(theta, 0)
        a_expanded = tl.expand_dims(a, 0)
        if is_disc:
            a_abs = tl.abs(a_expanded)
            log_a = tl.log(tl.maximum(a_abs, 1e-12))
            exp_term = tl.exp(zk_expanded * log_a)
        else:
            exp_term = tl.exp(-tl.abs(a_expanded) * zk_expanded)
        cos_term = tl.cos(theta_expanded * zk_expanded)
        base = 2.0 * dt * exp_term * cos_term
        q_expanded = tl.expand_dims(q, 0)
        q_init_expanded = tl.expand_dims(q_init, 0)
        masked_base = tl.where(d_mask[None, :], base, 0.0)
        acc_f += tl.sum(masked_base * q_expanded, axis=1)
        if use_initial:
            acc_init += tl.sum(masked_base * q_init_expanded, axis=1)
    out_base = pid_ch * L
    tl.store(f_ptr + out_base + l_offsets, acc_f, mask=l_mask)
    if use_initial:
        tl.store(y_init_ptr + out_base + l_offsets, acc_init, mask=l_mask)

# ------------------------------------------------------------------ ② case 层
# 典型用法:S4 层在 forward 前把 (a, theta, q) 合成卷积核 f(与 y_init)。原始
# 程序是 (C, H, D, L) 的参数化作;这里取 C=1、H=16、D=64、L=256,并按 shape 选择
# learn_dt / use_initial / is_disc 三个 constexpr 分支。
#
# (C, H, D, L):
#   典型  (1, 16, 64, 256)  learn_dt=0、use_initial=1、is_disc=0(连续时间的指数衰减)
#   规模  (2, 16, 64, 256)  典型规模 ×2:dim0 1->2;learn_dt=1、use_initial=1、is_disc=1(三分支全开)
#   泛化  (2, 8, 48, 300)   learn_dt=1、use_initial=0;L 不整除 BLOCK_SIZE_L
#         (1, 4, 16, 64)    is_disc=1(离散化参数化:exp(zk*log|a|))
SHAPES = ((1, 4, 16, 64),)
_FLAGS = {(1, 16, 64, 256): (False, True, False), (2, 16, 64, 256): (True, True, True),
          (2, 8, 48, 300): (True, False, False),
          (1, 4, 16, 64): (False, True, True)}
# kernel 里全在 f32 上算(exp/log/cos 只吃 fp32)。
DTYPES = ('float32', 'float16', 'bfloat16')
BLOCK_SIZE_D, BLOCK_SIZE_L = 32, 64


def ref(args, meta):
    """numpy 对照:base = 2*dt*exp_term*cos(theta*zk),沿 D 求和。"""
    c, h, d, l = (int(args[k]) for k in ("C", "H", "D", "L"))
    learn_dt, use_initial, is_disc = meta["learn_dt"], meta["use_initial"], meta["is_disc"]
    a = np.asarray(args["a_ptr"], dtype=np.float64).reshape(c, h, d)
    theta = np.asarray(args["theta_ptr"], dtype=np.float64).reshape(c, h, d)
    q = np.asarray(args["q_ptr"], dtype=np.float64).reshape(c, h, d)
    q_init = np.asarray(args["q_init_ptr"], dtype=np.float64).reshape(c, h, d)
    log_dt = np.asarray(args["log_dt_ptr"], dtype=np.float64).reshape(h)
    k = np.arange(l, dtype=np.float64)[None, None, :]          # (1, 1, L)
    if learn_dt:
        dt = np.exp(log_dt)[None, :, None]                     # (1, H, 1)
    else:
        dt = np.full((1, 1, 1), 1.0 / (l - 1.0))
    zk = (k * dt)[:, :, None, :]                               # (1, H, 1, L)
    dt4 = dt[:, :, None, :]                                    # (1, H, 1, 1)
    if is_disc:
        exp_term = np.exp(zk * np.log(np.maximum(np.abs(a), 1e-12))[:, :, :, None])
    else:
        exp_term = np.exp(-np.abs(a)[:, :, :, None] * zk)
    base = 2.0 * dt4 * exp_term * np.cos(theta[:, :, :, None] * zk)   # (C, H, D, L)
    f = (base * q[:, :, :, None]).sum(axis=2)
    y_init = ((base * q_init[:, :, :, None]).sum(axis=2) if use_initial
              else np.full_like(f, -7.0))
    out_f = np.asarray(args["f_ptr"])
    out_y = np.asarray(args["y_init_ptr"])
    return {"f_ptr": f.reshape(-1).astype(out_f.dtype),
            "y_init_ptr": y_init.reshape(-1).astype(out_y.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    c, h, d, l = (int(v) for v in shape)
    if min(c, h, d, l) <= 0 or l < 2:
        raise ValueError(f"shape must be > 1 on all dims, got {shape}")
    learn_dt, use_initial, is_disc = _FLAGS[(c, h, d, l)]

    # 参数按 S4D 的初始化量级:a 与 theta 在 (0, 1] 的 1/64 网格上,而 log_dt 取
    # log(1e-3 .. 1e-1) 之间的值;q/q_init 是 ~N(0,1) 的 1/16 网格值。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    size = (c, h, d)
    a = (rng.integers(1, 65, size, dtype=np.int16) / 64.0).astype(np.float32)
    theta = (rng.integers(1, 65, size, dtype=np.int16) / 16.0).astype(np.float32)
    q = (rng.integers(-16, 16, size, dtype=np.int16) / 16.0).astype(np.float32)
    q_init = (rng.integers(-16, 16, size, dtype=np.int16) / 16.0).astype(np.float32)
    log_dt = np.linspace(np.log(1e-3), np.log(1e-1), h).astype(np.float32)
    # 语义边界:第 0 个 (c,h) 的 theta 为 0(cos 恒为 1,只剩衰减)。
    theta[0, 0, :] = 0.0

    args = {"a_ptr": a.reshape(-1), "theta_ptr": theta.reshape(-1), "q_ptr": q.reshape(-1),
            "q_init_ptr": q_init.reshape(-1), "log_dt_ptr": log_dt,
            "f_ptr": np.full(c * h * l, -7.0, np.float32),
            "y_init_ptr": np.full(c * h * l, -7.0, np.float32),
            "C": np.int32(c), "H": np.int32(h), "D": np.int32(d), "L": np.int32(l)}
    meta = {"learn_dt": learn_dt, "use_initial": use_initial, "is_disc": is_disc,
            "BLOCK_SIZE_D": BLOCK_SIZE_D, "BLOCK_SIZE_L": BLOCK_SIZE_L}
    grid = (c * h, (l + BLOCK_SIZE_L - 1) // BLOCK_SIZE_L)
    return {"args": args, "meta": meta, "grid": grid,
            "outputs": ("f_ptr", "y_init_ptr"), "expected": ref(args, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, synthesis_kernel, DTYPES,
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
