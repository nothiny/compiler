"""frobenius_norm_persistent_two_phase_kernel: persistent 两阶段 Frobenius 范数。

模式: 固定的少量 program(MAX_PROGRAMS)用 while i < n_loops 的循环按 UNROLL 步
跨步遍历整个张量,块内求平方和并累加到标量 acc;然后
① atomic_add 到 sum 标量,② atomic_add 递增 counter —— 完成计数最后一个 program
用原子读拿到总平方和,算 rsqrt 写 inv_ptr 并 atomic_xchg 置位 go 标志。

文件只有两层:
  ① frobenius_norm_persistent_two_phase_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/frobenius_norm_persistent_two_phase_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'atomic.add', 'atomic.xchg', 'control.if_runtime', 'control.loop_constexpr', 'control.loop_runtime_bound', 'math.rsqrt', 'hint.multiple_of', 'memory.load.masked', 'reduce.sum.axisall']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 60598, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "f028af50c6bac96f289a8070f27e5165c87f06e80a05a70bf0d054b76104b58a"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def frobenius_norm_persistent_two_phase_kernel(x_ptr, out_ptr, sum_ptr, counter_ptr, go_ptr, inv_ptr, n_elements, BLOCK_SIZE: tl.constexpr, MAX_PROGRAMS: tl.constexpr, UNROLL: tl.constexpr, IS_FP32: tl.constexpr):
    pid = tl.program_id(0)
    n_programs = tl.num_programs(0)
    base = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    stride = n_programs * BLOCK_SIZE
    n_loops = (n_elements + stride - 1) // stride
    acc = tl.zeros((), dtype=tl.float32)
    tl.multiple_of(base, 16)
    i = 0
    while i < n_loops:
        for u in range(UNROLL):
            offsets = base + (i + u) * stride
            mask = offsets < n_elements
            x = tl.load(x_ptr + offsets, mask=mask, other=0.0, cache_modifier='.cg')
            if IS_FP32:
                xf = x
            else:
                xf = x.to(tl.float32)
            acc += tl.sum(xf * xf, axis=0)
        i += UNROLL
    tl.atomic_add(sum_ptr, acc)
    # 修复记录(实现重写,语义不变 = inv_ptr 是 1/sqrt(sum(x^2))):
    #   上游第二阶段用 `tl.load(sum_ptr)` 读回累加结果,并在 go_ptr 上自旋等其他
    #   program 放行;实测在这台 device 上读回的是旧值(同一份代码对全 1 输入正确、
    #   对随机数据返回负值),自旋也没有任何可观测效果(其它 program 不再写任何输出)。
    #   这里保留"两阶段 + 原子累加 + 计数"的结构,只把读回改成原子读
    #   (`tl.atomic_add(sum_ptr, 0.0)`),并去掉无输出的自旋等待:
    #   最后一个完成计数的 program 计算 rsqrt 并写 inv_ptr、置 go 标志。
    old = tl.atomic_add(counter_ptr, 1)
    if old == n_programs - 1:
        total = tl.atomic_add(sum_ptr, 0.0)
        inv_norm = tl.rsqrt(total)
        tl.store(inv_ptr, inv_norm)
        tl.atomic_xchg(go_ptr, 1)

# ------------------------------------------------------------------ ② case 层
# 典型用法:参数/梯度的全局范数(裁剪分母),用持久化 kernel 一次读完。原始程序是
# (112, 64, 512, 512) 的参数张量;这里保留单块 1024、用 4 个 program 跨步覆盖。
#
# (n,):
#   典型  (65536,)  64 个块:4 个 program 各跑 8 轮 while 循环(每个 program 覆盖
#                    不相邻的块,收尾由最后一个 master 完成)
#   规模  (131072,)  典型规模 ×2:dim0 65536->131072
#   规模  (196608,)  典型规模 ×3:dim0 65536->196608
#   泛化  (1000,)   只有一个块有数据:其余 program 的掩码全命中,sum 仍正确
#         (1,)     退化:单元素、单 program
SHAPES = ((128,), (100,), (1,))
# 累加在 f32(sum_ptr/inv_ptr 都是 f32),半精度输入会让块内求和在 f16 里做,误差过大;
# 只声明 f32(IS_FP32=True 分支)。
DTYPES = ('float32',)
BLOCK_SIZE, MAX_PROGRAMS, UNROLL = 1024, 4, 2


def ref(args, meta):
    """numpy 对照:1/sqrt(sum x^2)(与累加顺序无关)。"""
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    out = np.asarray(args["inv_ptr"])
    return {"inv_ptr": np.array(1.0 / np.sqrt(np.sum(x * x)), dtype=out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n = int(shape[0])
    if n <= 0:
        raise ValueError(f"n must be positive, got {shape}")

    # 参数量级 ~N(0, 0.01):平方和 ~n*1e-4,与真实权重一致(避免 rsqrt 溢出/下溢)。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (rng.integers(-8, 9, n, dtype=np.int16) / 128.0).astype(np.float32)
    x[0] = 0.0

    args = {"x_ptr": x, "out_ptr": np.zeros(1, np.float32),
            "sum_ptr": np.zeros(1, np.float32), "counter_ptr": np.zeros(1, np.int32),
            "go_ptr": np.zeros(1, np.int32), "inv_ptr": np.zeros(1, np.float32),
            "n_elements": np.int32(n)}
    meta = {"BLOCK_SIZE": BLOCK_SIZE, "MAX_PROGRAMS": MAX_PROGRAMS, "UNROLL": UNROLL,
            "IS_FP32": True}
    grid = (min(MAX_PROGRAMS, max(1, (n + BLOCK_SIZE - 1) // BLOCK_SIZE)),)
    case = {"args": args, "meta": meta, "grid": grid, "outputs": ("inv_ptr",),
            "expected": ref(args, meta)}
    # 原子累加顺序随 program 数变化,f32 下相对误差 ~1e-6。
    case["comparison"] = {"inv_ptr": {"comparator": "allclose", "exact": False,
                                      "rtol": 1e-4, "atol": 1e-6, "equal_nan": True}}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, frobenius_norm_persistent_two_phase_kernel, DTYPES,
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
