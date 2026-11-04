"""mode_kernel: 排序输入的众数:最长游程的值与首个下标。

模式: args.runtime_scalar, cast.to, control.for_range, creation.arange, creation.full, creation.where, memory.load.masked, memory.store.masked。

文件只有两层:
  ① mode_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/mode_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "cast.to", "control.for_range", "creation.arange", "creation.full", "creation.where", "memory.load.masked", "memory.store.masked"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/mode_kernel.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def mode_kernel(sorted_inp, sorted_indices, out_value, out_index, M, N, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr):
    pid_m = tl.program_id(0).to(tl.int64)
    m_offset = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    mask_m = m_offset < M
    n0 = tl.arange(0, 1)
    offset0 = m_offset[:, None] * N + n0[None, :]
    mask0 = mask_m[:, None] & (n0[None, :] < N)
    val0 = tl.load(sorted_inp + offset0, mask=mask0)
    idx0 = tl.load(sorted_indices + offset0, mask=mask0)
    cur_value = val0.reshape([BLOCK_M])
    cur_index = idx0.reshape([BLOCK_M])
    cur_count = tl.full([BLOCK_M], 1, dtype=tl.int64)
    best_value = cur_value
    best_index = cur_index
    best_count = tl.full([BLOCK_M], 1, dtype=tl.int64)
    for i in range(1, N):
        ni = tl.full([1], i, dtype=tl.int32)
        offset_i = m_offset[:, None] * N + ni[None, :]
        mask_i = mask_m[:, None] & (ni[None, :] < N)
        val_i = tl.load(sorted_inp + offset_i, mask=mask_i).reshape([BLOCK_M])
        idx_i = tl.load(sorted_indices + offset_i, mask=mask_i).reshape([BLOCK_M])
        same = val_i == cur_value
        cur_count = tl.where(same, cur_count + 1, tl.full([BLOCK_M], 1, dtype=tl.int64))
        cur_value = tl.where(same, cur_value, val_i)
        cur_index = idx_i
        better = cur_count > best_count
        best_count = tl.where(better, cur_count, best_count)
        best_value = tl.where(better, cur_value, best_value)
        best_index = tl.where(better, cur_index, best_index)
    tl.store(out_value + m_offset, best_value, mask=mask_m)
    tl.store(out_index + m_offset, best_index, mask=mask_m)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (1394,)  workload x2:dim0 697->1394
#   规模  (2091,)  workload x3:dim0 697->2091
SHAPES = ((17,), (114,))
DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 M=int(args["M"]);C=int(args["N"]);x=args["sorted_inp"].reshape(M,C);idx=args["sorted_indices"].reshape(M,C);vals=[];inds=[]
 for row,ir in zip(x,idx):
  u,start,count=np.unique(row,return_index=True,return_counts=True);j=int(np.argmax(count));end=start[j]+count[j]-1;vals.append(u[j]);inds.append(ir[end])
 return {"out_value":np.asarray(vals,np.float32),"out_index":np.asarray(inds,np.int64)}

def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=20260901):
 from case_utils import fast_rng
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 M=3;C=max(3,N//M);raw=rng.integers(0,5,(M,C));order=np.argsort(raw,axis=1,kind="stable");x=np.take_along_axis(raw,order,axis=1);args={"sorted_inp":np.asarray(x),"sorted_indices":np.asarray(order,"int64"),"out_value":np.asarray(np.full(M,-7.)),"out_index":np.asarray(np.full(M,-1),"int64"),"M":M,"N":C};meta={"BLOCK_M":2,"BLOCK_N":1<<(C-1).bit_length()};grid=((M+1)//2,)
 outputs=('out_value', 'out_index');return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0001, "atol": 0.0001, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, mode_kernel, DTYPES,
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
