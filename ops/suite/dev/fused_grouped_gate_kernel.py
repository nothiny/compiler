"""fused_grouped_gate_kernel: MoE 的分组门控(top-k 组 -> 组内 top-k 专家)。

模式: 1D grid(一个 token 一行),整行专家分数装进一个块:
USE_SOFTMAX 决定按 softmax 还是 sigmoid 归一(USE_BIAS 时组分数用 top1+top2,
否则组内取 max),再逐轮 tl.argmax 选出 topk_groups 个组(选过的置 -inf),
在被选组的范围里逐轮 tl.argmax 选 topk_experts 个专家,把下标与权重写到
indices/weights;最后按 ROUTE_SCALE(sigmoid 模式下再除以权重和)缩放。
USE_BIAS/USE_SOFTMAX 是 constexpr,topk 选择是运行时 for 循环。

文件只有两层:
  ① fused_grouped_gate_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/fused_grouped_gate_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.if_constexpr', 'control.loop_runtime_bound', 'creation.arange', 'creation.zeros', 'math.exp', 'math.maximum', 'math.minimum', 'memory.load.masked', 'memory.store', 'reduce.argmax', 'reduce.max.axis1', 'shape.reshape']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "test", "row": 51575, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "e9f69e50db9d8e1f2cb7419aca8c493d439461586b8e66c07cab8b4b605c23c0"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def fused_grouped_gate_kernel(scores_ptr, bias_ptr, weights_out_ptr, indices_out_ptr, stride_scores_b, stride_scores_e, stride_weights_b, stride_weights_e, stride_indices_b, stride_indices_e, n_experts: tl.constexpr, n_groups: tl.constexpr, topk_groups: tl.constexpr, topk_experts: tl.constexpr, USE_BIAS: tl.constexpr, USE_SOFTMAX: tl.constexpr, ROUTE_SCALE: tl.constexpr, BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(0)
    offs = tl.arange(0, BLOCK_SIZE)
    mask = offs < n_experts
    scores_ptr_row = scores_ptr + pid * stride_scores_b + offs * stride_scores_e
    scores = tl.load(scores_ptr_row, mask=mask, other=-float('inf'))
    if USE_SOFTMAX:
        m = tl.max(scores, axis=0)
        e = tl.exp(scores - m)
        s = tl.sum(e, axis=0)
        act_scores = e / s
    else:
        act_scores = 1.0 / (1.0 + tl.exp(-scores))
    routing_scores = act_scores
    if USE_BIAS:
        bias = tl.load(bias_ptr + offs, mask=mask, other=0.0)
        routing_scores = routing_scores + bias
    epg_padded: tl.constexpr = BLOCK_SIZE // n_groups
    rs_reshaped = tl.reshape(routing_scores, (n_groups, epg_padded))
    if not USE_BIAS:
        g_scores = tl.max(rs_reshaped, axis=1)
    else:
        top1 = tl.max(rs_reshaped, axis=1)
        idx1 = tl.argmax(rs_reshaped, axis=1)
        cols = tl.arange(0, epg_padded)
        mask_top1 = cols[None, :] == idx1[:, None]
        rem = tl.where(mask_top1, -float('inf'), rs_reshaped)
        top2 = tl.max(rem, axis=1)
        g_scores = top1 + top2
    group_mask = tl.zeros((n_groups,), dtype=tl.int1)
    temp_g_scores = g_scores
    for k in range(topk_groups):
        idx = tl.argmax(temp_g_scores, axis=0)
        current_mask = tl.arange(0, n_groups) == idx
        group_mask = group_mask | current_mask
        temp_g_scores = tl.where(current_mask, -float('inf'), temp_g_scores)
    mask_expanded = tl.broadcast_to(group_mask[:, None], (n_groups, epg_padded))
    mask_flattened = tl.reshape(mask_expanded, (BLOCK_SIZE,))
    curr_scores = tl.where(mask_flattened, routing_scores, -float('inf'))
    w_out_row = weights_out_ptr + pid * stride_weights_b
    i_out_row = indices_out_ptr + pid * stride_indices_b
    sum_weights = 0.0
    for k in range(topk_experts):
        idx = tl.argmax(curr_scores, axis=0)
        tl.store(i_out_row + k * stride_indices_e, idx)
        weight_val = tl.sum(tl.where(offs == idx, act_scores, 0.0))
        tl.store(w_out_row + k * stride_weights_e, weight_val)
        if not USE_SOFTMAX:
            sum_weights += weight_val
        mask_sel = offs == idx
        curr_scores = tl.where(mask_sel, -float('inf'), curr_scores)
    final_scale = ROUTE_SCALE
    if not USE_SOFTMAX:
        final_scale = ROUTE_SCALE / (sum_weights + 1e-20)
    for k in range(topk_experts):
        ptr = w_out_row + k * stride_weights_e
        val = tl.load(ptr)
        tl.store(ptr, val * final_scale)

# ------------------------------------------------------------------ ② case 层
# 典型用法:DeepSeek 式分组路由(64 个专家分成 8 组、选 2 组、组内选 3 个专家)。
# 原始程序是 (tokens, 64) 的专家分数;这里 batch 取 32 个 token,专家数 64。
#
# (tokens, n_experts):
#   典型  (32, 64)    原始配置:n_experts=64(8 组 x 8)、topk_groups=2、topk_experts=3
#   规模  (64, 64)  典型规模 ×2:dim0 32->64
#   规模  (96, 64)  典型规模 ×3:dim0 32->96
#   泛化  (17, 32)    专家数减半(4 组 x 8),token 数不是 2 的幂
#         (1, 8)      退化:单 token、单组
# 约束:n_experts 必须是 2 的幂(kernel 用 BLOCK_SIZE // n_groups 切组,而
# BLOCK_SIZE 由 meta 传成 n_experts)。
SHAPES = ((32, 64), (17, 32))
_CFG = {64: (8, 2, 3), 32: (4, 2, 3), 8: (1, 1, 2)}   # n_experts -> (n_groups, topk_groups, topk_experts)
# 原始程序是 fp32(scores 与权重都是 f32)。
DTYPES = ('float32', 'float16', 'bfloat16')
ROUTE_SCALE = 2.5


def ref(args, meta):
    """numpy 对照:按 kernel 的选择顺序(稳定 argmax = 首个最大值)复现。"""
    import numpy as _np
    tokens = int(args["TOKENS"])
    ne, ng = int(meta["n_experts"]), int(meta["n_groups"])
    tg, te = int(meta["topk_groups"]), int(meta["topk_experts"])
    scores = _np.asarray(args["scores_ptr"], dtype=_np.float64).reshape(tokens, ne)
    bias = _np.asarray(args["bias_ptr"], dtype=_np.float64)
    epg = ne // ng
    weights = _np.zeros((tokens, te), _np.float64)
    indices = _np.zeros((tokens, te), _np.int32)
    for row in range(tokens):
        s = scores[row]
        act = _np.exp(s - s.max()) / _np.exp(s - s.max()).sum() if meta["USE_SOFTMAX"]             else 1.0 / (1.0 + _np.exp(-s))
        routing = act + (bias if meta["USE_BIAS"] else 0.0)
        rs = routing.reshape(ng, epg)
        if not meta["USE_BIAS"]:
            g = rs.max(axis=1)
        else:
            order = _np.argsort(-rs, axis=1, kind="stable")
            g = rs[_np.arange(ng), order[:, 0]] + rs[_np.arange(ng), order[:, 1]]
        # 选 top-k 组:每轮取首个最大(与 tl.argmax 一致),选过的置 -inf
        temp = g.copy()
        chosen = _np.zeros(ng, bool)
        for _ in range(tg):
            i = int(_np.argmax(temp))
            chosen[i] = True
            temp[i] = -_np.inf
        mask = _np.broadcast_to(chosen[:, None], (ng, epg)).reshape(ne)
        curr = _np.where(mask, routing, -_np.inf)
        total = 0.0
        for k in range(te):
            i = int(_np.argmax(curr))
            indices[row, k] = i
            weights[row, k] = act[i]
            if not meta["USE_SOFTMAX"]:
                total += act[i]
            curr[i] = -_np.inf
        scale = ROUTE_SCALE if meta["USE_SOFTMAX"] else ROUTE_SCALE / (total + 1e-20)
        weights[row] *= scale
    out_w = np.asarray(args["weights_out_ptr"])
    out_i = np.asarray(args["indices_out_ptr"])
    return {"weights_out_ptr": weights.reshape(-1).astype(out_w.dtype),
            "indices_out_ptr": indices.reshape(-1).astype(out_i.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    tokens, ne = (int(v) for v in shape)
    if tokens <= 0 or ne <= 0:
        raise ValueError(f"shape must be positive (tokens, n_experts), got {shape}")
    ng, tg, te = _CFG[ne]
    # kernel 用 BLOCK_SIZE // n_groups 来切组,所以 BLOCK_SIZE 必须恰好等于
    # n_experts(否则高位补出来的 -inf 槽会把组边界错开)。n_experts 取 2 的幂。
    block = ne
    if ne % ng or block & (block - 1):
        raise ValueError(f"n_experts must be a power of 2 divisible by n_groups, got {shape}")

    # 专家分数是 1/16 网格上的 ~N(0,1);bias 是 per-expert 的小偏移(1/64 网格)。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    scores = (np.clip(np.rint(rng.standard_normal((tokens, ne), dtype=np.float32) * 16),
                      -128, 127) / 16).astype(np.float32)
    bias = (rng.integers(-4, 5, ne, dtype=np.int16) / 64).astype(np.float32)
    # 语义边界:第 0 个 token 的所有专家分数相同(并列,argmax 取最左)。
    scores[0, :] = 0.0
    bias[:] = 0.0

    args = {"scores_ptr": scores.reshape(-1), "bias_ptr": bias,
            "weights_out_ptr": np.full(tokens * te, -7.0, np.float32),
            "indices_out_ptr": np.full(tokens * te, -1, np.int32),
            "stride_scores_b": np.int32(ne), "stride_scores_e": np.int32(1),
            "stride_weights_b": np.int32(te), "stride_weights_e": np.int32(1),
            "stride_indices_b": np.int32(te), "stride_indices_e": np.int32(1),
            "TOKENS": tokens}
    meta = {"n_experts": ne, "n_groups": ng, "topk_groups": tg, "topk_experts": te,
            "USE_BIAS": False, "USE_SOFTMAX": True, "ROUTE_SCALE": ROUTE_SCALE,
            "BLOCK_SIZE": block}
    return {"args": args, "meta": meta, "grid": (tokens,),
            "outputs": ("weights_out_ptr", "indices_out_ptr"),
            "expected": ref(args, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;下标精确、权重按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, fused_grouped_gate_kernel, DTYPES,
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
