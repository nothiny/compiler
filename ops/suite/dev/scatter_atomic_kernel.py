"""scatter_atomic_kernel: MoE 式的按位置原子累加 y[token] += src * weight。

模式: 2D grid(D 方向一块、行一块):先用 sorted_pos 这个排好序的位置表做间接
寻址取出 token_idx 与该位置的权重(weight 也是间接 load),再把 src 的一行乘以
权重后 tl.atomic_add 到 y 的对应行。间接寻址 + 原子累加,同一 token 会被多个
位置命中,所以必须用重复的 pos。

文件只有两层:
  ① scatter_atomic_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'medium/scatter_atomic_kernel', "group": 'medium', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'atomic.add', 'creation.arange', 'memory.load.masked', 'memory.indirect', 'memory.load']}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def scatter_atomic_kernel(y_ptr, src_ptr, sorted_pos_ptr, weights_ptr, stride_y_n, stride_y_d, stride_src_n, stride_src_d, K_val, N_total, D: tl.constexpr, BLOCK_SIZE: tl.constexpr):
    pid_d = tl.program_id(0)
    pid_n = tl.program_id(1)
    pos = tl.load(sorted_pos_ptr + pid_n)
    token_idx = pos // K_val
    weight = tl.load(weights_ptr + pos).to(tl.float32)
    offs = pid_d * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = offs < D
    src_ptr_off = src_ptr + pid_n * stride_src_n + offs * stride_src_d
    y_ptr_off = y_ptr + token_idx * stride_y_n + offs * stride_y_d
    val = tl.load(src_ptr_off, mask=mask).to(tl.float32)
    out = val * weight
    tl.atomic_add(y_ptr_off, out, mask=mask)

# ------------------------------------------------------------------ ② case 层
# 典型用法:MoE/attention 的 top-k 输出回散到 token 维:每个 (token, k) 位置有
# 一份 src,按权重累加到 token。原始版本形状很小;这里取 512 token x top-4 x
# 1024 维(与 LLM 的 hidden 量级一致,维度缩到 1024)。
#
# (N_total, K_val, D):
#   典型  (512, 4, 1024)  512 个 token、每个 4 个专家位置、1024 维
#   规模  (1024, 4, 1024)  典型规模 ×2:dim0 512->1024
#   规模  (512, 4, 2048)  典型规模 ×2:dim2 1024->2048
#   泛化  (7, 3, 130)     小规模:D 不整除 BLOCK,尾部被掩码
#         (1, 1, 1)       退化:单元素
SHAPES = ((128, 4, 128), (7, 3, 98), (1, 1, 1))
# 原始版本是 fp32(src/weights/y 都是);原子累加在 f32 里做。
DTYPES = ('float32', 'float16', 'bfloat16')
BLOCK_SIZE = 256


def ref(args, meta):
    """numpy 对照:按 pos 还原 token/weight 后累加(与加法顺序无关)。"""
    n_total, k_val, d = int(meta["N_total"]), int(meta["K_val"]), int(meta["D"])
    pos = np.asarray(args["sorted_pos_ptr"]).astype(np.int64)
    src = np.asarray(args["src_ptr"], dtype=np.float64).reshape(pos.size, d)
    w = np.asarray(args["weights_ptr"], dtype=np.float64)
    acc = np.zeros((n_total, d), dtype=np.float64)
    token = pos // k_val          # pos 决定 token
    weight = w[pos]               # 权重也按 pos 间接读取
    np.add.at(acc, token, src * weight[:, None])
    out = np.asarray(args["y_ptr"])
    return {"y_ptr": acc.reshape(-1).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n_total, k_val, d = (int(v) for v in shape)
    if min(n_total, k_val, d) <= 0:
        raise ValueError(f"shape must be positive (N_total, K_val, D), got {shape}")

    from case_utils import fast_rng
    rng = fast_rng(seed)
    n_rows = n_total * k_val
    # src 是 top-k 输出(1/16 网格,量级 1),weights 是 softmax 后的门控权重。
    src = (rng.integers(-16, 17, (n_rows, d), dtype=np.int16) / 16).astype(np.float32)
    weights = (rng.integers(1, 17, n_rows, dtype=np.int16) / 16).astype(np.float32)
    # pos 是 [0, n_rows) 的排列:每个位置恰好出现一次 => 每个 token 恰好被
    # K_val 个位置命中(重复索引必然出现,这是 atomic 的语义边界)。
    pos = rng.permutation(n_rows).astype(np.int32)

    args = {"y_ptr": np.zeros((n_total, d), np.float32), "src_ptr": src.reshape(-1),
            "sorted_pos_ptr": pos, "weights_ptr": weights,
            "stride_y_n": np.int32(d), "stride_y_d": np.int32(1),
            "stride_src_n": np.int32(d), "stride_src_d": np.int32(1),
            "K_val": np.int32(k_val), "N_total": np.int32(n_total)}
    meta = {"D": d, "BLOCK_SIZE": BLOCK_SIZE, "N_total": n_total, "K_val": k_val}
    grid = ((d + BLOCK_SIZE - 1) // BLOCK_SIZE, n_rows)
    case = {"args": args, "meta": meta, "grid": grid, "outputs": ("y_ptr",),
            "expected": ref(args, meta)}
    # 原子加的顺序随发射顺序变化:f32 下 K=4 个累加项的误差在 1e-6 量级。
    case["comparison"] = {"y_ptr": {"comparator": "allclose", "exact": False,
                                    "rtol": 1e-4, "atol": 1e-4, "equal_nan": True}}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, scatter_atomic_kernel, DTYPES,
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
