"""weighted_scatter_add_kernel: MoE 输出回散 —— (val+bias)*weight 按 token 原子累加。

模式: 2D grid(位置, D 方向一块)。先用 mask 做 control.if 的早退(无效位置直接
return),再从 indices 间接取出 token_id、从 weights 取门控权重,bias 按专家
e_idx = idx // M 取,最后 tl.atomic_add 到 out[token] 的 D 维一段。
间接寻址 + 早退分支 + 原子累加三件套。

文件只有两层:
  ① weighted_scatter_add_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'medium/weighted_scatter_add_kernel', "group": 'medium', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'atomic.add', 'atomic.masked', 'control.if_runtime', 'creation.arange', 'memory.load', 'memory.load.masked', 'memory.indirect']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "test", "row": 49307, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "64632034057515b8a691da010bee89685f5545814424f6b6b7c42f07819937b8"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def weighted_scatter_add_kernel(out_ptr, val_ptr, b_ptr, weights_ptr, indices_ptr, mask_ptr, E, M, D, BLOCK_SIZE: tl.constexpr):
    idx = tl.program_id(0)
    d_block = tl.program_id(1)
    is_valid = tl.load(mask_ptr + idx).to(tl.int16)
    if is_valid == 0:
        return
    token_id = tl.load(indices_ptr + idx)
    weight = tl.load(weights_ptr + idx).to(tl.float32)
    e_idx = idx // M
    offs = d_block * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = offs < D
    v = tl.load(val_ptr + idx * D + offs, mask=mask, other=0.0).to(tl.float32)
    b = tl.load(b_ptr + e_idx * D + offs, mask=mask, other=0.0).to(tl.float32)
    res = (v + b) * weight
    tl.atomic_add(out_ptr + token_id * D + offs, res, mask=mask)

# ------------------------------------------------------------------ ② case 层
# 典型用法:DeepSeek-MoE 式的专家输出回散:每个 (专家, 槽位) 的输出按门控权重
# 加回 token。原始 dim=2048、n_activated_experts=6、每专家最多 max_c 个 token;
# 这里取 E=8 个在用专家 x 64 槽位 x 2048 维(约 1M 个元素),前缀维按 shape 缩。
#
# (E, M, D, N_tokens):
#   典型  (8, 64, 2048, 512)  8 个在用专家、每专家 64 槽、2048 维、512 个 token
#   规模  (16, 64, 2048, 512)  典型规模 ×2:dim0 8->16
#   规模  (8, 64, 4096, 512)  典型规模 ×2:dim2 2048->4096
#   泛化  (3, 7, 300, 16)     D 不整除 BLOCK,尾块被掩码;小配置
#         (1, 1, 1, 1)        退化:单元素(且该位置被 mask 掉,走早退分支)
SHAPES = ((8, 64, 128, 128), (3, 7, 100, 16), (1, 1, 1, 1))
# 原始程序全程 f32(专家输出与门控权重都是 f32),原子累加也在 f32 里做。
DTYPES = ('float32', 'float16', 'bfloat16')
BLOCK_SIZE = 256


def ref(args, meta):
    """numpy 对照:跳过 mask=0 的位置,其余按 token 累加(与加法顺序无关)。"""
    e, m, d, n_tok = (int(meta[k]) for k in ("E", "M", "D", "N_tokens"))
    val = np.asarray(args["val_ptr"], dtype=np.float64).reshape(e * m, d)
    bias = np.asarray(args["b_ptr"], dtype=np.float64).reshape(e, d)
    weight = np.asarray(args["weights_ptr"], dtype=np.float64)
    mask = np.asarray(args["mask_ptr"]).astype(bool)
    token = np.asarray(args["indices_ptr"]).astype(np.int64)
    acc = np.zeros((n_tok, d), dtype=np.float64)
    e_idx = np.arange(e * m) // m
    contrib = (val + bias[e_idx]) * weight[:, None]
    np.add.at(acc, token[mask], contrib[mask])
    out = np.asarray(args["out_ptr"])
    return {"out_ptr": acc.reshape(-1).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    e, m, d, n_tok = (int(v) for v in shape)
    if min(e, m, d, n_tok) <= 0:
        raise ValueError(f"shape must be positive (E, M, D, N_tokens), got {shape}")

    from case_utils import fast_rng
    rng = fast_rng(seed)
    rows = e * m
    # 专家输出是 1/16 网格的 ~N(0,1);门控权重是 softmax 后的正数;bias 是 ~0。
    val = (rng.integers(-32, 32, (rows, d), dtype=np.int16) / 16).astype(np.float32)
    bias = (rng.integers(-8, 9, (e, d), dtype=np.int16) / 16).astype(np.float32)
    weight = (rng.integers(1, 33, rows, dtype=np.int16) / 32).astype(np.float32)
    # token 下标有重复(不同专家/槽位落到同一 token)——这正是 atomic 的语义边界。
    token = rng.integers(0, n_tok, rows, dtype=np.int32)
    # 前一半位置有效、后一半被 mask 掉:早退分支与正常分支都被走到。
    mask = np.ones(rows, dtype=np.int8)
    mask[rows // 2:] = 0
    if rows == 1:
        mask[:] = 0

    args = {"out_ptr": np.zeros((n_tok, d), np.float32), "val_ptr": val.reshape(-1),
            "b_ptr": bias.reshape(-1), "weights_ptr": weight, "indices_ptr": token,
            "mask_ptr": mask, "E": np.int32(e), "M": np.int32(m), "D": np.int32(d)}
    meta = {"BLOCK_SIZE": BLOCK_SIZE, "E": e, "M": m, "D": d, "N_tokens": n_tok}
    grid = (rows, (d + BLOCK_SIZE - 1) // BLOCK_SIZE)
    case = {"args": args, "meta": meta, "grid": grid, "outputs": ("out_ptr",),
            "expected": ref(args, meta)}
    case["comparison"] = {"out_ptr": {"comparator": "allclose", "exact": False,
                                      "rtol": 1e-4, "atol": 1e-4, "equal_nan": True}}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, weighted_scatter_add_kernel, DTYPES,
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
