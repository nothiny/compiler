"""gram_jacobi_sym_kernel: 对称 Gram 矩阵的 Jacobi 扫描(产出未排序对角特征值)。

模式: args.runtime_scalar, cast.to, control.while, creation.arange, creation.where, math.abs, math.rsqrt, math.sqrt, memory.load.masked, memory.load.other, memory.store.masked, reduce.sum。

文件只有两层:
  ① _gram_jacobi_sym_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/gram_jacobi_sym_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "cast.to", "control.while", "creation.arange", "creation.where", "math.abs", "math.rsqrt", "math.sqrt", "memory.load.masked", "memory.load.other", "memory.store.masked", "reduce.sum"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/gram_jacobi_sym_kernel.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def _gram_jacobi_sym_kernel(GRAM, EVECS, EVALS, K, SWEEPS, BLOCK_K: tl.constexpr):
    batch = tl.program_id(0)
    r = tl.arange(0, BLOCK_K)
    cidx = tl.arange(0, BLOCK_K)
    rr = r[:, None]
    cc = cidx[None, :]
    mask = (rr < K) & (cc < K)
    base = GRAM + batch * K * K
    g = tl.load(base + rr * K + cc, mask=mask, other=0.0).to(tl.float32)
    v = tl.where((rr == cc) & mask, 1.0, 0.0)
    eps = 1e-20
    sweep = 0
    while sweep < SWEEPS:
        p = 0
        while p < K - 1:
            q = p + 1
            while q < K:
                diag_p = tl.sum(tl.where((rr == p) & (cc == p), g, 0.0))
                diag_q = tl.sum(tl.where((rr == q) & (cc == q), g, 0.0))
                off = tl.sum(tl.where((rr == p) & (cc == q), g, 0.0))
                abs_off = tl.abs(off)
                threshold = 1e-07 * tl.sqrt(tl.abs(diag_p * diag_q) + eps)
                active = abs_off > threshold
                safe_off = tl.where(active, off, 1.0)
                tau = (diag_q - diag_p) / (2.0 * safe_off)
                sign_tau = tl.where(tau >= 0.0, 1.0, -1.0)
                t = sign_tau / (tl.abs(tau) + tl.sqrt(1.0 + tau * tau))
                crot = tl.rsqrt(1.0 + t * t)
                srot = t * crot
                crot = tl.where(active, crot, 1.0)
                srot = tl.where(active, srot, 0.0)
                col_p = tl.sum(tl.where(cc == p, g, 0.0), axis=1)
                col_q = tl.sum(tl.where(cc == q, g, 0.0), axis=1)
                row_p = tl.sum(tl.where(rr == p, g, 0.0), axis=0)
                row_q = tl.sum(tl.where(rr == q, g, 0.0), axis=0)
                new_col_p = crot * col_p - srot * col_q
                new_col_q = srot * col_p + crot * col_q
                new_row_p = crot * row_p - srot * row_q
                new_row_q = srot * row_p + crot * row_q
                g = tl.where(cc == p, new_col_p[:, None], g)
                g = tl.where(cc == q, new_col_q[:, None], g)
                g = tl.where(rr == p, new_row_p[None, :], g)
                g = tl.where(rr == q, new_row_q[None, :], g)
                new_pp = crot * crot * diag_p - 2.0 * crot * srot * off + srot * srot * diag_q
                new_qq = srot * srot * diag_p + 2.0 * crot * srot * off + crot * crot * diag_q
                g = tl.where((rr == p) & (cc == p), new_pp, g)
                g = tl.where((rr == q) & (cc == q), new_qq, g)
                g = tl.where((rr == p) & (cc == q) | (rr == q) & (cc == p), 0.0, g)
                vec_p = tl.sum(tl.where(cc == p, v, 0.0), axis=1)
                vec_q = tl.sum(tl.where(cc == q, v, 0.0), axis=1)
                new_vec_p = crot * vec_p - srot * vec_q
                new_vec_q = srot * vec_p + crot * vec_q
                v = tl.where(cc == p, new_vec_p[:, None], v)
                v = tl.where(cc == q, new_vec_q[:, None], v)
                q += 1
            p += 1
        sweep += 1
    diag = tl.sum(tl.where(rr == cc, g, 0.0), axis=1)
    tl.store(EVALS + batch * K + r, diag, mask=r < K)
    tl.store(EVECS + batch * K * K + rr * K + cc, v, mask=mask)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (20, 5)  workload x2:dim0 10->20
#   规模  (30, 5)  workload x3:dim0 10->30
SHAPES = ((17,), (30, 5))
DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 K=int(args["K"]);sweeps=int(args["SWEEPS"]);grams=np.asarray(args["GRAM"],np.float32).reshape(-1,K,K);evals=np.empty((grams.shape[0],K),np.float32);evecs=np.empty_like(grams)
 for b in range(grams.shape[0]):
  g=grams[b].copy();v=np.eye(K,dtype=np.float32)
  for _ in range(sweeps):
   for p in range(K-1):
    for q in range(p+1,K):
     dp=np.float32(g[p,p]);dq=np.float32(g[q,q]);off=np.float32(g[p,q]);active=abs(off)>1e-7*np.sqrt(abs(dp*dq)+1e-20)
     if active:tau=(dq-dp)/(2*off);t=(1 if tau>=0 else -1)/(abs(tau)+np.sqrt(1+tau*tau));c=np.float32(1/np.sqrt(1+t*t));s=np.float32(t*c)
     else:c=np.float32(1);s=np.float32(0)
     cp=g[:,p].copy();cq=g[:,q].copy();rp=g[p].copy();rq=g[q].copy();g[:,p]=c*cp-s*cq;g[:,q]=s*cp+c*cq;g[p]=c*rp-s*rq;g[q]=s*rp+c*rq;g[p,p]=c*c*dp-2*c*s*off+s*s*dq;g[q,q]=s*s*dp+2*c*s*off+c*c*dq;g[p,q]=0;g[q,p]=0;vp=v[:,p].copy();vq=v[:,q].copy();v[:,p]=c*vp-s*vq;v[:,q]=s*vp+c*vq
  evals[b]=np.diag(g);evecs[b]=v
 return {"EVECS":evecs.reshape(-1),"EVALS":evals.reshape(-1)}

def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=20260901):
    from case_utils import fast_rng
    if len(shape) > 1 and tuple(shape) not in SHAPES:
        raise ValueError('unsupported explicit shape configuration')
    del dtype
    import numpy as np
    N = int(shape[0])
    rng = fast_rng(seed)
    B = int(shape[0]) if len(shape) > 1 else 3
    K = int(shape[1]) if len(shape) > 1 else 5
    sweeps = 6
    q = rng.normal(0, 0.4, (B, K, K)).astype(np.float32)
    g = (q + np.transpose(q, (0, 2, 1))) / 2
    args = {'GRAM': np.asarray(g, 'float32'), 'EVECS': np.asarray(np.full(B * K * K, -7), 'float32'), 'EVALS': np.asarray(np.full(B * K, -7), 'float32'), 'K': K, 'SWEEPS': sweeps}
    meta = {'BLOCK_K': 8}
    grid = (B,)
    outputs = ('EVECS', 'EVALS')
    return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0001, "atol": 0.0001, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, _gram_jacobi_sym_kernel, DTYPES,
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
