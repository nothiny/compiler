"""fused_lstm_layer_kernel: 单层 LSTM 前向,一个 program 跑完整个序列。

模式: grid = (batch,),每个 program 用 scratch 缓冲区在 HIDDEN_SIZE 个 lane 间
广播 h_{t-1}:for t in range(SEQ_LEN) 内层 for k in range(HIDDEN_SIZE) 读
h_scratch[k] 与 Whh[k, :, gate] 累加 4 个门(门在最后一维连续排布,i/f/g/o = +0..3),
再用 sigmoid 与 tanh(2*sigmoid(2x)-1)算 c_t、h_t;两次 tl.debug_barrier 保证
scratch 的读写顺序。SAVE_SEQUENCE 是 constexpr 分支,决定是否保存整条序列。

文件只有两层:
  ① fused_lstm_layer_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'medium/fused_lstm_layer_kernel', "group": 'medium', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.loop_runtime_bound', 'control.if_constexpr', 'math.sigmoid', 'memory.load', 'memory.store']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 484313, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "b03c10c95ebdcfe24d3631a52fa46a34fa0ef14a78ca1ab13a6648205c6ccb73"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def fused_lstm_layer_kernel(GatesIH_ptr, Whh_ptr, H0_ptr, C0_ptr, H_scratch_ptr, H_out_ptr, H_final_ptr, SEQ_LEN: tl.constexpr, HIDDEN_SIZE: tl.constexpr, SAVE_SEQUENCE: tl.constexpr, stride_g_b, stride_g_s, stride_g_h, stride_w_row, stride_w_col, stride_h0_b, stride_h0_h, stride_c0_b, stride_c0_h, stride_hs_b, stride_hs_h, stride_hout_b, stride_hout_s, stride_hout_h, stride_hfin_b, stride_hfin_h):
    pid = tl.program_id(0)
    tid = tl.arange(0, HIDDEN_SIZE)
    c = tl.load(C0_ptr + pid * stride_c0_b + tid * stride_c0_h)
    h = tl.load(H0_ptr + pid * stride_h0_b + tid * stride_h0_h)
    scratch_base = H_scratch_ptr + pid * stride_hs_b
    tl.store(scratch_base + tid, h)
    gates_base = GatesIH_ptr + pid * stride_g_b
    for t in range(SEQ_LEN):
        tl.debug_barrier()
        g_ptr = gates_base + t * stride_g_s + tid * stride_g_h
        acc_i = tl.load(g_ptr + 0)
        acc_f = tl.load(g_ptr + 1)
        acc_g = tl.load(g_ptr + 2)
        acc_o = tl.load(g_ptr + 3)
        for k in range(HIDDEN_SIZE):
            h_val = tl.load(scratch_base + k)
            w_ptr = Whh_ptr + k * stride_w_row + tid * stride_w_col
            w_i = tl.load(w_ptr + 0)
            w_f = tl.load(w_ptr + 1)
            w_g = tl.load(w_ptr + 2)
            w_o = tl.load(w_ptr + 3)
            acc_i += h_val * w_i
            acc_f += h_val * w_f
            acc_g += h_val * w_g
            acc_o += h_val * w_o
        i_val = tl.sigmoid(acc_i)
        f_val = tl.sigmoid(acc_f)
        g_val = 2.0 * tl.sigmoid(2.0 * acc_g) - 1.0
        o_val = tl.sigmoid(acc_o)
        c = f_val * c + i_val * g_val
        tanh_c = 2.0 * tl.sigmoid(2.0 * c) - 1.0
        h = o_val * tanh_c
        tl.debug_barrier()
        tl.store(scratch_base + tid, h)
        if SAVE_SEQUENCE:
            out_loc = H_out_ptr + pid * stride_hout_b + t * stride_hout_s + tid * stride_hout_h
            tl.store(out_loc, h)
    tl.store(H_final_ptr + pid * stride_hfin_b + tid * stride_hfin_h, h)

# ------------------------------------------------------------------ ② case 层
# 典型用法:推理时的单层 LSTM(输入投影 gates_ih 已提前算好)。原始
# batch=10、seq_len=512、hidden=256;这个 kernel 每个 program 顺序跑完
# SEQ_LEN x HIDDEN_SIZE 次内积,512x256 的真实尺寸在验证里太慢,这里按比例
# 缩到 seq=8、hidden=32(结构与门排布不变),batch=2。
#
# (B, S, H):
#   典型  (2, 8, 32)   两个 batch,8 个时间步,hidden=32;SAVE_SEQUENCE=True
#   规模  (4, 8, 32)   典型规模 ×2:dim0 2->4;SAVE_SEQUENCE=True
#   泛化  (1, 4, 16)   小配置;SAVE_SEQUENCE=False(不写序列输出)
#         (1, 1, 8)    退化:单时间步(只走一轮门计算)
SHAPES = ((2, 8, 32), (4, 8, 32), (1, 1, 8))
_SAVE = {(2, 8, 32): True, (4, 8, 32): True, (1, 4, 16): False, (1, 1, 8): True}
# kernel 里 sigmoid/tanh 都在 f32 上算,tl.sigmoid 只吃 fp32,合法域只有 fp32。
DTYPES = ('float32',)
UNWRITTEN = -7.0          # SAVE_SEQUENCE=False 时 H_out 的初值,应该原样保留


def ref(args, meta):
    """numpy 对照:标准 LSTM 递推,门在最后一维按 i,f,g,o 排布。"""
    b, s, h = int(meta["SEQ_LEN"]), int(meta["SEQ_LEN"]), int(meta["HIDDEN_SIZE"])
    b = int(args["B"])
    gates = np.asarray(args["GatesIH_ptr"], dtype=np.float64).reshape(b, s, h, 4)
    whh = np.asarray(args["Whh_ptr"], dtype=np.float64).reshape(h, h, 4)
    h_t = np.asarray(args["H0_ptr"], dtype=np.float64).reshape(b, h).copy()
    c_t = np.asarray(args["C0_ptr"], dtype=np.float64).reshape(b, h).copy()
    sigmoid = lambda v: 1.0 / (1.0 + np.exp(-v))
    seq = np.zeros((b, s, h), dtype=np.float64)
    for t in range(s):
        acc = gates[:, t, :, :] + np.einsum("bh,hg->bg", h_t, whh.reshape(h, -1)).reshape(b, h, 4)
        i = sigmoid(acc[:, :, 0])
        f = sigmoid(acc[:, :, 1])
        g = np.tanh(acc[:, :, 2])
        o = sigmoid(acc[:, :, 3])
        c_t = f * c_t + i * g
        h_t = o * np.tanh(c_t)
        seq[:, t, :] = h_t
    out = np.asarray(args["H_out_ptr"])
    h_final = np.asarray(args["H_final_ptr"])
    saved = seq if meta["SAVE_SEQUENCE"] else np.full_like(seq, UNWRITTEN)
    return {"H_out_ptr": saved.reshape(-1).astype(out.dtype),
            "H_final_ptr": h_t.reshape(-1).astype(h_final.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    b, s, h = (int(v) for v in shape)
    if min(b, s, h) <= 0:
        raise ValueError(f"shape must be positive (B, S, H), got {shape}")
    save = _SAVE[(b, s, h)]

    from case_utils import fast_rng
    rng = fast_rng(seed)
    # 输入投影 gates_ih 是 x@W_ih^T 的结果,量级 ~N(0, sqrt(input_size)*0.1);
    # Whh 是正交初始化后的 ~N(0, 1/sqrt(hidden))。门值太大会让 sigmoid 饱和,
    # 所以用 1/8 网格把量级压在 [-2, 2)。
    gates = (rng.integers(-16, 16, (b, s, h, 4), dtype=np.int16) / 8).astype(np.float32)
    whh = (rng.integers(-4, 5, (h, h, 4), dtype=np.int16) / 16).astype(np.float32)
    h0 = (rng.integers(-8, 9, (b, h), dtype=np.int16) / 16).astype(np.float32)
    c0 = (rng.integers(-8, 9, (b, h), dtype=np.int16) / 16).astype(np.float32)
    # 语义边界:第 0 个 batch 的 h0/c0 全 0(第一个时间步的递归项为零,
    # 输出完全由 gates_ih 决定)。
    h0[0] = 0.0
    c0[0] = 0.0

    args = {"GatesIH_ptr": gates.reshape(-1), "Whh_ptr": whh.reshape(-1),
            "H0_ptr": h0.reshape(-1), "C0_ptr": c0.reshape(-1),
            "H_scratch_ptr": np.zeros((b, h), np.float32),
            "H_out_ptr": np.full(b * s * h, UNWRITTEN, np.float32),
            "H_final_ptr": np.zeros((b, h), np.float32),
            "stride_g_b": np.int32(s * h * 4), "stride_g_s": np.int32(h * 4),
            "stride_g_h": np.int32(4), "stride_w_row": np.int32(h * 4),
            "stride_w_col": np.int32(4), "stride_h0_b": np.int32(h),
            "stride_h0_h": np.int32(1), "stride_c0_b": np.int32(h),
            "stride_c0_h": np.int32(1), "stride_hs_b": np.int32(h),
            "stride_hs_h": np.int32(1), "stride_hout_b": np.int32(s * h),
            "stride_hout_s": np.int32(h), "stride_hout_h": np.int32(1),
            "stride_hfin_b": np.int32(h), "stride_hfin_h": np.int32(1),
            "B": np.int32(b)}
    meta = {"SEQ_LEN": s, "HIDDEN_SIZE": h, "SAVE_SEQUENCE": save}
    return {"args": args, "meta": meta, "grid": (b,),
            "outputs": ("H_out_ptr", "H_final_ptr"), "expected": ref(args, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, fused_lstm_layer_kernel, DTYPES,
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
