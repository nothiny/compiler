"""avg_pool1d_kernel_optimized: 1D 平均池化,(B, C, L) -> (B, C, L_out)。

模式: 2D grid(batch*channel 一组、输出长度方向一组),块内用 (BLOCK_SIZE,
VECTOR_SIZE) 展平的向量走访存,核窗口用 for k in range(kernel_size) 逐点累加,
越界位置(左边界 padding、右边界尾部)都由 load_mask 屏蔽成 0,再除以
kernel_size。stride/padding/kernel_size 都是运行时标量。

文件只有两层:
  ① avg_pool1d_kernel_optimized   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'medium/avg_pool1d_kernel_optimized', "group": 'medium', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.loop_runtime_bound', 'creation.arange', 'memory.load.masked', 'memory.store.masked', 'reduce.sum.axisall']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 71535, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "9c2f8c9fc3e24624d4cdcffd75f687bd2fc3a02ac49123607751eecd8cba0fb4"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def avg_pool1d_kernel_optimized(x_ptr, out_ptr, stride_b, stride_c, stride_l, out_stride_b, out_stride_c, out_stride_l, batch_size, in_channels, input_length, output_length, kernel_size, stride, padding, BLOCK_SIZE: tl.constexpr, VECTOR_SIZE: tl.constexpr=4):
    pid_bc = tl.program_id(0)
    pid_l = tl.program_id(1)
    batch_idx = pid_bc // in_channels
    channel_idx = pid_bc % in_channels
    x_ptr_bc = x_ptr + batch_idx * stride_b + channel_idx * stride_c
    out_ptr_bc = out_ptr + batch_idx * out_stride_b + channel_idx * out_stride_c
    block_start = pid_l * BLOCK_SIZE * VECTOR_SIZE
    thread_ids = tl.arange(0, BLOCK_SIZE)[:, None]
    vec_offs = tl.arange(0, VECTOR_SIZE)[None, :]
    offs = block_start + thread_ids * VECTOR_SIZE + vec_offs
    offs = tl.ravel(offs)
    mask = offs < output_length
    acc = tl.zeros((BLOCK_SIZE * VECTOR_SIZE,), dtype=tl.float32)
    for k in range(kernel_size):
        in_pos = offs * stride - padding + k
        load_mask = (in_pos >= 0) & (in_pos < input_length) & mask
        val = tl.load(x_ptr_bc + in_pos * stride_l, mask=load_mask, other=0.0)
        acc += val
    result = acc / tl.cast(kernel_size, tl.float32)
    tl.store(out_ptr_bc + offs * out_stride_l, result, mask=mask)

# ------------------------------------------------------------------ ② case 层
# 典型用法:序列模型下采样前的池化。原始 (64, 128, 65536) fp32,kernel=8、
# stride=8、padding=0 => L_out = 8192。保留 L 的量级、把 batch 缩到 2。
# kernel 有掩码,所以泛化 shape 的输出长度故意不整除 BLOCK*VECTOR。
#
# (B, C, L):
#   典型  (2, 32, 4096)   kernel=8,stride=8 => L_out=512,BLOCK*VEC=512 恰好整除
#   规模  (4, 32, 4096)   典型规模 ×2:dim0 2->4;kernel=8、stride=8 同典型
#   泛化  (1, 3, 1031)    L_out=129,尾部被 mask;padding=2 让左侧也越界
#         (1, 1, 8)       退化:一个窗口、一个输出
SHAPES = ((1, 1, 8),)
# 原始程序用 fp32;池化只有加法与除法,半精度合法,补 fp16/bf16。
DTYPES = ("float32", "float16", "bfloat16")
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}
BLOCK_SIZE, VECTOR_SIZE = 64, 8
# shape -> (kernel_size, stride, padding)
_POOL = {(2, 32, 4096): (8, 8, 0), (4, 32, 4096): (8, 8, 0), (1, 3, 1031): (4, 8, 2), (1, 1, 8): (8, 8, 0)}


def ref(args, meta):
    """numpy 对照:零填充后按窗口求平均(float64)。"""
    b, c, l = (int(args[k]) for k in ("batch_size", "in_channels", "input_length"))
    k, s, p = (int(args[k]) for k in ("kernel_size", "stride", "padding"))
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    out = np.asarray(args["out_ptr"])
    l_out = (l + 2 * p - k) // s + 1
    padded = np.zeros((b, c, l + 2 * p), dtype=np.float64)
    padded[:, :, p:p + l] = x
    idx = np.arange(l_out)[:, None] * s + np.arange(k)[None, :]
    y = padded[:, :, idx].mean(axis=-1)
    return {"out_ptr": y.astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    b, c, l = (int(v) for v in shape)
    kernel, stride, padding = _POOL[(b, c, l)]
    l_out = (l + 2 * padding - kernel) // stride + 1

    # 原始输入是 [0,1) 的均匀分布;改成 [-1,1) 让均值可能在 0 附近(检验不丢符号),
    # 取值落在 1/8 网格上,半精度精确可表示。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (rng.integers(-8, 8, (b, c, l), dtype=np.int16) / 8.0).astype(_HOST_DTYPE[dtype])
    # 语义边界:第一个窗口全为 -1(均值 -1)、最后一个窗口全为 1(均值 1);
    # 第一条通道全 0(均值 0,且 padding 的零填充不会被误算进来)。
    x[:, 0, :] = 0.0
    x[0, 0 if c == 1 else 1, :kernel] = -1.0
    x[0, 0 if c == 1 else 1, -kernel:] = 1.0

    args = {"x_ptr": x, "out_ptr": np.zeros((b, c, l_out), dtype=np_dtype_of(dtype)),
            "stride_b": np.int32(c * l), "stride_c": np.int32(l), "stride_l": np.int32(1),
            "out_stride_b": np.int32(c * l_out), "out_stride_c": np.int32(l_out),
            "out_stride_l": np.int32(1), "batch_size": np.int32(b),
            "in_channels": np.int32(c), "input_length": np.int32(l),
            "output_length": np.int32(l_out), "kernel_size": np.int32(kernel),
            "stride": np.int32(stride), "padding": np.int32(padding)}
    meta = {"BLOCK_SIZE": BLOCK_SIZE, "VECTOR_SIZE": VECTOR_SIZE}
    grid = (b * c, (l_out + BLOCK_SIZE * VECTOR_SIZE - 1) // (BLOCK_SIZE * VECTOR_SIZE))
    case = {"args": args, "meta": meta, "grid": grid, "outputs": ("out_ptr",),
            "expected": ref(args, meta)}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {"x_ptr": "bfloat16", "out_ptr": "bfloat16"}
        case["comparison"] = {"out_ptr": {"comparator": "allclose", "exact": False,
                                          "rtol": 5e-3, "atol": 5e-3, "equal_nan": True}}
    return case


def np_dtype_of(dtype):
    return np.float32 if dtype == "bfloat16" else np.dtype(dtype)


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, avg_pool1d_kernel_optimized, DTYPES,
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
