"""triu_batch_kernel: 批量上三角化:保留对角线以上,其余置 0。

模式: args.runtime_scalar, cast.to, creation.arange, creation.where, memory.load.masked, memory.load.other, memory.store.masked。

文件只有两层:
  ① triu_batch_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/triu_batch_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "cast.to", "creation.arange", "creation.where", "memory.load.masked", "memory.load.other", "memory.store.masked"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/triu_batch_kernel.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit(do_not_specialize=['diagonal'])
def triu_batch_kernel(X, Y, batch, MN, N, diagonal, BATCH_BLOCK_SIZE: tl.constexpr, MN_BLOCK_SIZE: tl.constexpr):
    batch_id = tl.program_id(0).to(tl.int64)
    mn_id = tl.program_id(1).to(tl.int64)
    row = batch_id * BATCH_BLOCK_SIZE + tl.arange(0, BATCH_BLOCK_SIZE)[:, None]
    batch_mask = row < batch
    X += row * MN
    Y += row * MN
    cols = mn_id * MN_BLOCK_SIZE + tl.arange(0, MN_BLOCK_SIZE)[None, :]
    mn_mask = cols < MN
    mask = batch_mask and mn_mask
    x = tl.load(X + cols, mask, other=0.0)
    m = cols // N
    n = cols % N
    y = tl.where(m + diagonal <= n, x, 0.0)
    tl.store(Y + cols, y, mask=mask)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (1648,)  workload x2:dim0 824->1648
#   规模  (2472,)  workload x3:dim0 824->2472
SHAPES = ((17,), (120,))
DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 B=int(args["batch"]);C=int(args["N"]);M=int(args["MN"])//C;x=args["X"].reshape(B,M,C);return {"Y":np.asarray([np.triu(a,k=int(args["diagonal"])) for a in x]).reshape(-1)}

def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=20260901):
 from case_utils import fast_rng
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 B=2;M=4;C=max(3,N//8);T=B*M*C;args={"X":np.asarray(rng.normal(0,.8,T)),"Y":np.asarray(np.full(T,-7.)),"batch":B,"MN":M*C,"N":C,"diagonal":-1};meta={"BATCH_BLOCK_SIZE":1,"MN_BLOCK_SIZE":128};grid=(B,(M*C+127)//128)
 outputs=('Y',);return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0001, "atol": 0.0001, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, triu_batch_kernel, DTYPES,
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
