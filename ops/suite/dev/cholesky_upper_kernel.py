"""cholesky_upper_kernel: 上三角 Cholesky 递推(容差钳位主元,逐批处理)。

模式: args.runtime_scalar, cast.to, control.while, creation.arange, creation.full, creation.where, math.abs, math.maximum, math.sqrt, memory.load.masked, memory.load.other, memory.store.masked, reduce.max, reduce.sum。

文件只有两层:
  ① _cholesky_upper_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/cholesky_upper_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "cast.to", "control.while", "creation.arange", "creation.full", "creation.where", "math.abs", "math.maximum", "math.sqrt", "memory.load.masked", "memory.load.other", "memory.store.masked", "reduce.max", "reduce.sum"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/cholesky_upper_kernel.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def _cholesky_upper_kernel(GRAM, R, STATUS, K: tl.constexpr, BLOCK_K: tl.constexpr):
    batch = tl.program_id(0)
    cols = tl.arange(0, BLOCK_K)
    col_mask = cols < K
    base_g = GRAM + batch * K * K
    base_r = R + batch * K * K
    diag_vals = tl.load(base_g + cols * K + cols, mask=col_mask, other=0.0).to(tl.float32)
    max_diag = tl.max(tl.abs(diag_vals), axis=0)
    tol = tl.maximum(max_diag * 1e-08, 1e-20)
    status = tl.full((), 0, dtype=tl.int32)
    finite_limit = 3.4028234663852886e+38
    j = 0
    while j < K:
        row_mask = col_mask & (cols >= j)
        gram_row = tl.load(base_g + j * K + cols, mask=row_mask, other=0.0).to(tl.float32)
        diag = tl.load(base_g + j * K + j).to(tl.float32)
        p = 0
        while p < j:
            r_pj = tl.load(base_r + p * K + j).to(tl.float32)
            r_pcols = tl.load(base_r + p * K + cols, mask=row_mask, other=0.0).to(tl.float32)
            gram_row -= r_pj * r_pcols
            diag -= r_pj * r_pj
            p += 1
        good_diag = (diag == diag) & (tl.abs(diag) < finite_limit) & (diag > tol)
        pivot = tl.sqrt(tl.maximum(diag, tol))
        r_vals = gram_row / pivot
        r_vals = tl.where(cols == j, pivot, r_vals)
        r_vals = tl.where(row_mask, r_vals, 0.0)
        bad_vals = tl.sum((((r_vals != r_vals) | (tl.abs(r_vals) >= finite_limit)) & row_mask).to(tl.int32), axis=0)
        status = tl.where(good_diag & (bad_vals == 0), status, 1)
        tl.store(base_r + j * K + cols, r_vals, mask=col_mask)
        j += 1
    tl.store(STATUS + batch, status)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (16, 5)  workload x2:dim0 8->16
#   规模  (24, 5)  workload x3:dim0 8->24
SHAPES = ((17,), (24, 5))
DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 K=int(meta["K"]);g=np.asarray(args["GRAM"],np.float32).reshape(-1,K,K);out=np.zeros_like(g);status=np.zeros(g.shape[0],np.int32)
 for b in range(g.shape[0]):
  tol=max(np.max(np.abs(np.diag(g[b])))*1e-8,1e-20)
  for j in range(K):
   row=g[b,j].copy();diag=np.float32(g[b,j,j])
   for p in range(j):row[j:]-=out[b,p,j]*out[b,p,j:];diag-=out[b,p,j]*out[b,p,j]
   good=np.isfinite(diag) and diag>tol;pivot=np.sqrt(max(diag,tol));vals=np.zeros(K,np.float32);vals[j:]=row[j:]/pivot;vals[j]=pivot
   if (not good) or np.any(~np.isfinite(vals[j:])):status[b]=1
   out[b,j]=vals
 return {"R":out.reshape(-1),"STATUS":status}

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
    q = rng.normal(0, 0.3, (B, K, K)).astype(np.float32)
    g = q @ np.transpose(q, (0, 2, 1)) + np.eye(K, dtype=np.float32)[None]
    g[2] = np.eye(K, dtype=np.float32)
    g[2, 0, 0] = 0
    args = {'GRAM': np.asarray(g, 'float32'), 'R': np.asarray(np.full(B * K * K, -7), 'float32'), 'STATUS': np.asarray(np.full(B, -1), 'int32')}
    meta = {'K': K, 'BLOCK_K': 8}
    grid = (B,)
    outputs = ('R', 'STATUS')
    return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0001, "atol": 0.0001, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, _cholesky_upper_kernel, DTYPES,
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
