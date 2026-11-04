"""logsumexp__logsumexp_kernel_non_inner: 非内层轴 logsumexp(在线 max 稳定化)。

模式: args.runtime_scalar, cast.to, control.for_range, control.if, creation.arange, creation.full, creation.where, math.exp, math.log, math.maximum, memory.load.masked, memory.load.other, memory.store.masked, reduce.max, reduce.sum。

文件只有两层:
  ① logsumexp_kernel_non_inner   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/logsumexp__logsumexp_kernel_non_inner", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "cast.to", "control.for_range", "control.if", "creation.arange", "creation.full", "creation.where", "math.exp", "math.log", "math.maximum", "memory.load.masked", "memory.load.other", "memory.store.masked", "reduce.max", "reduce.sum"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/logsumexp__logsumexp_kernel_non_inner.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def logsumexp_kernel_non_inner(output_ptr, input_ptr, M, N, K, TILE_N: tl.constexpr, TILE_K: tl.constexpr, ONE_TILE_PER_CTA: tl.constexpr):
    """Kernel for logsumexp when reduction dimension is not the innermost."""
    pid_m = tl.program_id(0).to(tl.int64)
    pid_k = tl.program_id(1).to(tl.int64)
    k_offsets = pid_k * TILE_K + tl.arange(0, TILE_K)[None, :]
    if ONE_TILE_PER_CTA:
        n_offsets = tl.arange(0, TILE_N)[:, None]
        inp_offset = pid_m * N * K + n_offsets * K + k_offsets
        mask = (n_offsets < N) & (k_offsets < K)
        input_ptrs = input_ptr + inp_offset
        inp = tl.load(input_ptrs, mask=mask, other=-float('inf')).to(tl.float32)
        m = tl.max(inp, axis=0, keep_dims=True)
        safe_m = tl.where(m == float('-inf'), tl.zeros_like(m), m)
        e = tl.exp(inp - safe_m)
        z = tl.sum(e, axis=0, keep_dims=True)
        out = safe_m + tl.log(z)
        out = tl.where(m == float('-inf'), m, out)
        out_offset = pid_m * K + k_offsets
        output_ptrs = output_ptr + out_offset
        tl.store(output_ptrs, out, mask=k_offsets < K)
    else:
        m = tl.full([TILE_N, TILE_K], value=float('-inf'), dtype=tl.float32)
        z = tl.full([TILE_N, TILE_K], value=0.0, dtype=tl.float32)
        for start_n in range(0, N, TILE_N):
            n_offsets = start_n + tl.arange(0, TILE_N)[:, None]
            inp_offsets = pid_m * N * K + n_offsets * K + k_offsets
            mask = (n_offsets < N) & (k_offsets < K)
            inp = tl.load(input_ptr + inp_offsets, mask=mask, other=-float('inf')).to(tl.float32)
            m_new = tl.maximum(m, inp)
            all_neg_inf = m_new == float('-inf')
            z = tl.where(all_neg_inf, z, z * tl.exp(m - m_new) + tl.exp(inp - m_new))
            m = m_new
        m_reduced = tl.max(m, axis=0, keep_dims=True)
        z = tl.sum(z * tl.exp(m - m_reduced), axis=0, keep_dims=True)
        m = m_reduced
        out = tl.where(m == float('-inf'), m, m + tl.log(z))
        out_offset = pid_m * K + k_offsets
        output_ptrs = output_ptr + out_offset
        tl.store(output_ptrs, out, mask=k_offsets < K)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (1416,)  workload x2:dim0 708->1416
#   规模  (2124,)  workload x3:dim0 708->2124
SHAPES = ((17,), (104,))
DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 M=int(args["M"]);R=int(args["N"]);K=int(args["K"]);x=args["input_ptr"].reshape(M,R,K);m=np.max(x,axis=1);return {"output_ptr":(m+np.log(np.sum(np.exp(x-m[:,None,:]),axis=1))).reshape(-1)}

def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=20260901):
 from case_utils import fast_rng
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 M=2;R=3;K=max(2,N//6);T=M*R*K;args={"output_ptr":np.asarray(np.full(M*K,-7.)),"input_ptr":np.asarray(rng.normal(0,.8,T)),"M":M,"N":R,"K":K};meta={"TILE_N":128,"TILE_K":4,"ONE_TILE_PER_CTA":False};grid=(M,(K+3)//4)
 outputs=('output_ptr',);return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0001, "atol": 0.0001, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, logsumexp_kernel_non_inner, DTYPES,
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
