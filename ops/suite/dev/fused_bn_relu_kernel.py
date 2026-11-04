"""fused_bn_relu_kernel: BatchNorm(推理态)+ ReLU 融合,带向量化与尾块两条路径。

模式: 每个 program 处理 VEC_SIZE 个连续元素:把线性位置拆回 (n, c, hw) 三元组,
按通道 c 取 weight/bias/running_mean/running_var(向量 load,每个 lane 一个通道),
算 y = max((x - mean) / sqrt(var + eps) * w + b, 0)。总数不整除 VEC_SIZE 时,
最后一个 program 走带掩码的 BLOCK_SIZE 尾块路径(两条路径的数学一致)。

文件只有两层:
  ① fused_bn_relu_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'medium/fused_bn_relu_kernel', "group": 'medium', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.if_runtime', 'creation.arange',
                     'math.maximum', 'math.sqrt', 'memory.load', 'memory.load.masked',
                     'memory.store', 'memory.store.masked']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 439722, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "023d77422fc601f048992d3a1bd87db91b68649ace0639ad8fc5e263a625d598"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def fused_bn_relu_kernel(x_ptr, out_ptr, weight_ptr, bias_ptr, mean_ptr, var_ptr, B, C, HW, stride_x_b, stride_x_c, stride_x_hw, eps: tl.constexpr, BLOCK_SIZE: tl.constexpr, VEC_SIZE: tl.constexpr):
    """
    Fused BatchNorm + ReLU kernel optimized for high occupancy and memory throughput.
    Each program processes a contiguous block of VEC_SIZE elements at a time.
    """
    pid = tl.program_id(0)
    total_elements = B * C * HW
    num_vec_blocks = total_elements // VEC_SIZE
    remaining = total_elements % VEC_SIZE
    if pid < num_vec_blocks:
        vec_start = pid * VEC_SIZE
        n_start = vec_start // (C * HW)
        c_start = vec_start // HW % C
        hw_start = vec_start % HW
        vec_offsets = tl.arange(0, VEC_SIZE)
        linear_offsets = vec_start + vec_offsets
        n_idx = linear_offsets // (C * HW)
        c_idx = linear_offsets // HW % C
        hw_idx = linear_offsets % HW
        x_offsets = n_idx * stride_x_b + c_idx * stride_x_c + hw_idx * stride_x_hw
        # 修复记录:上游用 `c_idx[i]` 标量下标与 `tensor.at(i).set(...)` 逐元素装配,
        # 这两者在 Triton 3.8 都不存在(unsupported tensor index / no attribute 'at')。
        # 改成同语义的按 lane 向量 load/store:每个 lane 取的通道参数与逐元素版本一致。
        w_vec = tl.load(weight_ptr + c_idx).to(tl.float32)
        b_vec = tl.load(bias_ptr + c_idx).to(tl.float32)
        m_vec = tl.load(mean_ptr + c_idx).to(tl.float32)
        v_vec = tl.load(var_ptr + c_idx).to(tl.float32)
        x_vec = tl.load(x_ptr + x_offsets).to(tl.float32)
        inv_std_vec = 1.0 / tl.sqrt(v_vec + eps)
        y_vec = (x_vec - m_vec) * inv_std_vec * w_vec + b_vec
        y_vec = tl.maximum(y_vec, 0.0)
        out_offset = vec_start + vec_offsets
        tl.store(out_ptr + out_offset, y_vec)
    elif pid == num_vec_blocks and remaining > 0:
        vec_start = num_vec_blocks * VEC_SIZE
        offsets = vec_start + tl.arange(0, BLOCK_SIZE)
        mask = offsets < total_elements
        n_idx = offsets // (C * HW)
        c_idx = offsets // HW % C
        hw_idx = offsets % HW
        x_offsets = n_idx * stride_x_b + c_idx * stride_x_c + hw_idx * stride_x_hw
        w = tl.load(weight_ptr + c_idx, mask=mask, other=0.0)
        b = tl.load(bias_ptr + c_idx, mask=mask, other=0.0)
        m = tl.load(mean_ptr + c_idx, mask=mask, other=0.0)
        v = tl.load(var_ptr + c_idx, mask=mask, other=0.0)
        x = tl.load(x_ptr + x_offsets, mask=mask, other=0.0)
        inv_std = 1.0 / tl.sqrt(v + eps)
        y = (x - m) * inv_std * w + b
        y = tl.maximum(y, 0.0)
        tl.store(out_ptr + offsets, y, mask=mask)

# ------------------------------------------------------------------ ② case 层
# 典型用法:DenseNet 式网络的 BN+ReLU(推理态,用 running_mean/var)。原始
# (10, 64, 112, 112) fp32:C=64、HW=12544;这里把 batch 缩到 2。
# shape 里同时选 VEC_SIZE(BLOCK_SIZE 尾块的路径由 total % VEC_SIZE 决定)。
#
# (B, C, HW):
#   典型  (2, 64, 12544)  原始 (10, 64, 112x112);VEC_SIZE=4 快路径,整除无尾块
#   规模  (4, 64, 12544)  典型规模 ×2:dim0 2->4;VEC_SIZE=4 快路径
#   泛化  (2, 3, 7)       total=42:VEC_SIZE=4 => 10 个向量块 + 2 个元素走尾块路径
#         (3, 5, 11)      total=165:VEC_SIZE=2 => 走 tl.range 装配的通用路径 + 尾块
SHAPES = ((2, 3, 7), (3, 5, 11))
_VEC = {(2, 64, 12544): 4, (4, 64, 12544): 4, (2, 3, 7): 4, (3, 5, 11): 2}
# 原始程序是 fp32(running stats 与激活都是 f32);sqrt 也只吃 fp32。
DTYPES = ('float32',)
EPS = 1e-5
BLOCK_SIZE = 1024


def ref(args, meta):
    """numpy 对照:逐通道 BN(推理态)+ ReLU。"""
    b, c, hw = int(args["B"]), int(args["C"]), int(args["HW"])
    x = np.asarray(args["x_ptr"], dtype=np.float64).reshape(b, c, hw)
    w = np.asarray(args["weight_ptr"], dtype=np.float64)
    bias = np.asarray(args["bias_ptr"], dtype=np.float64)
    mean = np.asarray(args["mean_ptr"], dtype=np.float64)
    var = np.asarray(args["var_ptr"], dtype=np.float64)
    inv = 1.0 / np.sqrt(var + np.float64(meta["eps"]))
    y = (x - mean[None, :, None]) * inv[None, :, None] * w[None, :, None] + bias[None, :, None]
    out = np.asarray(args["out_ptr"])
    return {"out_ptr": np.maximum(y, 0.0).reshape(-1).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    b, c, hw = (int(v) for v in shape)
    if min(b, c, hw) <= 0:
        raise ValueError(f"shape must be positive (B, C, HW), got {shape}")

    from case_utils import fast_rng
    rng = fast_rng(seed)
    # 特征图是 ReLU 之后的非负值(1/16 网格);running stats 用 rand 输入训练得到的
    # 量级:mean≈0.3、var≈0.08;gamma/beta 是 BN 初始化后的 ~1 / ~0。
    x = (rng.integers(0, 65, (b, c, hw), dtype=np.int16) / 16).astype(np.float32)
    mean = (rng.integers(8, 24, c, dtype=np.int16) / 64).astype(np.float32)
    var = (rng.integers(16, 24, c, dtype=np.int16) / 128).astype(np.float32)
    w = (rng.integers(8, 24, c, dtype=np.int16) / 16).astype(np.float32)
    bias = (rng.integers(-16, 17, c, dtype=np.int16) / 16).astype(np.float32)
    # 语义边界:第 0 通道 var 恰为 0(只有 eps 撑住分母)、gamma 为 0(整通道输出
    # 退化成 relu(beta))。
    var[0] = 0.0
    if c > 1:
        w[1] = 0.0

    args = {"x_ptr": x.reshape(-1), "out_ptr": np.full(b * c * hw, -7.0, np.float32),
            "weight_ptr": w, "bias_ptr": bias, "mean_ptr": mean, "var_ptr": var,
            "B": np.int32(b), "C": np.int32(c), "HW": np.int32(hw),
            "stride_x_b": np.int32(c * hw), "stride_x_c": np.int32(hw),
            "stride_x_hw": np.int32(1)}
    vec = _VEC[(b, c, hw)]
    meta = {"eps": EPS, "BLOCK_SIZE": BLOCK_SIZE, "VEC_SIZE": vec}
    total = b * c * hw
    grid = (total // vec + (1 if total % vec else 0),)
    return {"args": args, "meta": meta, "grid": grid, "outputs": ("out_ptr",),
            "expected": ref(args, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, fused_bn_relu_kernel, DTYPES,
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
