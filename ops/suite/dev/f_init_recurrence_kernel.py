"""_f_init_recurrence_kernel: S4D 式复指数递归,生成卷积核 f 与初始化项 init。

模式: 2D grid(时间块, c*h*d)。每个 program 先算一次 r=exp(-|a|dt)、phi=theta*dt,
再用 tl.static_range(BLOCK_L) 的静态展开推进递推(Ak *= r、cosk/sink 由旋转
公式更新),每个 k 用 k < L 的运行时判断做尾部裁剪,并把
q*2*dt*Ak*cosk 原子累加进 f(USE_INIT 时再累加 2*c*x0*base 进 init)。
覆盖 atomic.add、static_range、runtime 分支与循环携带变量。

文件只有两层:
  ① _f_init_recurrence_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'medium/f_init_recurrence_kernel', "group": 'medium', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'atomic.add', 'control.if_runtime', 'control.loop_constexpr', 'control.loop_carried', 'math.abs', 'math.cos', 'math.exp', 'math.sin', 'memory.load']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 522351, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "ea36ebe79b1c0bad44eb55ebd26415a8ccc72b2dad36ed41a2a04b0f0e506176"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def _f_init_recurrence_kernel(a_ptr, theta_ptr, b_ptr, c_ptr, x0_ptr, f_ptr, init_ptr, H, D, L, C, dt, BLOCK_L: tl.constexpr, USE_INIT: tl.constexpr):
    pid_t = tl.program_id(0)
    pid_chd = tl.program_id(1)
    d = pid_chd % D
    tmp = pid_chd // D
    h = tmp % H
    c = tmp // H
    k0 = pid_t * BLOCK_L
    base_chd = (c * H + h) * D + d
    a_val = tl.load(a_ptr + base_chd)
    th_val = tl.load(theta_ptr + base_chd)
    b_val = tl.load(b_ptr + base_chd)
    c_val = tl.load(c_ptr + base_chd)
    x0_val = tl.load(x0_ptr + base_chd)
    a_neg = -tl.abs(a_val)
    r = tl.exp(a_neg * dt)
    phi = th_val * dt
    cos_phi = tl.cos(phi)
    sin_phi = tl.sin(phi)
    Ak = tl.exp(a_neg * dt * k0)
    cosk = tl.cos(phi * k0)
    sink = tl.sin(phi * k0)
    q_val = b_val * c_val
    two_dt = 2.0 * dt
    two_cx0 = 2.0 * (c_val * x0_val)
    for j in tl.static_range(BLOCK_L):
        k = k0 + j
        if k < L:
            base = two_dt * Ak * cosk
            out_off = (c * H + h) * L + k
            tl.atomic_add(f_ptr + out_off, q_val * base)
            if USE_INIT:
                tl.atomic_add(init_ptr + out_off, two_cx0 * base)
        new_cosk = cosk * cos_phi - sink * sin_phi
        new_sink = sink * cos_phi + cosk * sin_phi
        cosk = new_cosk
        sink = new_sink
        Ak = Ak * r

# ------------------------------------------------------------------ ② case 层
# 典型用法:S4/S4D 状态空间层在 forward 之前预计算卷积核。原始
# (C=1, H=16, D=1, L=256) fp16/fp32 的 u=(B,H,L) 输入,dt = 1/(L-1),
# BLOCK_L=128 => 2 个时间块 grid = (2, C*H*D) = (2, 16)。
# shape 里的 D 同时选择 USE_INIT 分支(D=1 走累加 init 的分支,D>1 只算 f)。
#
# (C, H, D, L):
#   典型  (1, 16, 1, 256)  原始 S4D 配置:L=256、16 个 hippo、单通道
#   规模  (2, 16, 1, 256)  典型规模 ×2:dim0 1->2
#   规模  (1, 16, 1, 512)  典型规模 ×2:dim3 256->512
#   泛化  (1, 16, 1, 300)  L 不整除 BLOCK_L:最后一个时间块的 `if k < L` 才生效
#         (2, 4, 2, 128)   D>1(USE_INIT=False 分支)+ 多通道多 hippo 的批
SHAPES = ((1, 16, 1, 128), (1, 16, 1, 100))
# kernel 全程 f32 计算(exp/cos/sin 只吃 fp32),输出缓冲也是 f32。
DTYPES = ('float32', 'float16', 'bfloat16')
BLOCK_L = 128


def ref(args, meta):
    """numpy 对照:f[k] = q*2*dt*exp(-|a|dt*k)*cos(theta*dt*k),init 同源乘 2*c*x0。"""
    c, h, d, l = (int(v) for k, v in meta.items() if k in ("C", "H", "D", "L"))
    a = np.asarray(args["a_ptr"], dtype=np.float64).reshape(c * h * d)
    th = np.asarray(args["theta_ptr"], dtype=np.float64).reshape(c * h * d)
    b = np.asarray(args["b_ptr"], dtype=np.float64).reshape(c * h * d)
    cc = np.asarray(args["c_ptr"], dtype=np.float64).reshape(c * h * d)
    x0 = np.asarray(args["x0_ptr"], dtype=np.float64).reshape(c * h * d)
    dt = np.float64(args["dt"])
    k = np.arange(l, dtype=np.float64)
    base = 2.0 * dt * np.exp(-np.abs(a)[:, None] * dt * k[None, :]) * np.cos(th[:, None] * dt * k[None, :])
    f = (b * cc)[:, None] * base
    init = 2.0 * (cc * x0)[:, None] * base
    out_f = np.asarray(args["f_ptr"])
    out_i = np.asarray(args["init_ptr"])
    # (C,H,D) -> 输出按 (c*H+h)*L+k 展平;D 方向对同一 (c,h,k) 累加。
    f = f.reshape(c, h, d, l).sum(axis=2)
    init = init.reshape(c, h, d, l).sum(axis=2)
    if not meta["USE_INIT"]:
        init = np.zeros_like(init)          # USE_INIT=False 时 kernel 完全不碰 init
    return {"f_ptr": f.reshape(-1).astype(out_f.dtype),
            "init_ptr": init.reshape(-1).astype(out_i.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    c, h, d, l = (int(v) for v in shape)
    if min(c, h, d) <= 0 or l < 2:
        raise ValueError(f"shape must be (C, H, D, L >= 2), got {shape}")

    from case_utils import fast_rng
    rng = fast_rng(seed)
    # S4D 的参数化:a = -exp(uniform(log(dt_min), log(dt_max)))、theta = 角度采样、
    # b/c/x0 是初始化后的 ~N(0,1)。这里用 1/64 网格的 [-2, 2) 取值,量级一致。
    size = c * h * d
    grid_val = lambda: (rng.integers(-128, 128, size, dtype=np.int16) / 64.0).astype(np.float32)
    a = -(rng.integers(8, 65, size, dtype=np.int16) / 1024.0).astype(np.float32)  # 负的 ~0.01
    theta = (rng.integers(1, 64, size, dtype=np.int16) / 16.0).astype(np.float32)
    b, cc, x0 = grid_val(), grid_val(), grid_val()
    args = {"a_ptr": a, "theta_ptr": theta, "b_ptr": b, "c_ptr": cc, "x0_ptr": x0,
            "f_ptr": np.zeros(c * h * l, np.float32),
            "init_ptr": np.zeros(c * h * l, np.float32),
            "H": np.int32(h), "D": np.int32(d), "L": np.int32(l), "C": np.int32(c),
            "dt": np.float32(1.0 / (l - 1))}
    meta = {"BLOCK_L": BLOCK_L, "USE_INIT": d == 1, "C": c, "H": h, "D": d, "L": l}
    grid = ((l + BLOCK_L - 1) // BLOCK_L, c * h * d)
    case = {"args": args, "meta": meta, "grid": grid, "outputs": ("f_ptr", "init_ptr"),
            "expected": ref(args, meta)}
    # 时间是"每个 k 只由一个 program 写",但 kernel 用的是 atomic_add:f32 下一次
    # 加法就是精确的期望值,按 1e-5 相对容差比较即可。
    case["comparison"] = {name: {"comparator": "allclose", "exact": False, "rtol": 1e-5,
                                 "atol": 1e-6, "equal_nan": True}
                          for name in ("f_ptr", "init_ptr")}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, _f_init_recurrence_kernel, DTYPES,
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
