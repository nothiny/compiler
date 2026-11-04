"""nanmedian_ascend_histogram_count_kernel: nanmedian 的直方图计数段(升序键分桶统计)。

模式: args.runtime_scalar, cast.to, control.if, creation.arange, creation.full, creation.where, memory.load.masked, memory.load.other, memory.store, reduce.sum。

文件只有两层:
  ① nanmedian_ascend_histogram_count_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/nanmedian_ascend_histogram_count_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "cast.to", "control.if", "creation.arange", "creation.full", "creation.where", "memory.load.masked", "memory.load.other", "memory.store", "reduce.sum"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/nanmedian_ascend_histogram_count_kernel.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def nanmedian_ascend_histogram_count_kernel(inp, partial_counts, M, N: tl.constexpr, BLOCK_N: tl.constexpr, NUM_CHUNKS: tl.constexpr, HISTOGRAM_BINS: tl.constexpr):
    pid_m = tl.program_id(0).to(tl.int64)
    pid_chunk = tl.program_id(1).to(tl.int64)
    offsets = pid_chunk * BLOCK_N + tl.arange(0, BLOCK_N)
    bins = tl.arange(0, HISTOGRAM_BINS)
    mask = offsets < N
    vals = tl.load(inp + pid_m * N + offsets, mask=mask, other=0)
    _inl_3_to_order_key_vals = vals
    _inl_3_to_order_key_valid = mask
    _inl_3_to_order_key_dtype = _inl_3_to_order_key_vals.dtype
    _inl_3_to_order_key_nbits: tl.constexpr = _inl_3_to_order_key_dtype.primitive_bitwidth
    _inl_3_to_order_key_utype = tl.dtype(f'uint{_inl_3_to_order_key_nbits}')
    _inl_3_to_order_key_top_mask: tl.constexpr = 1 << _inl_3_to_order_key_nbits - 1
    _inl_3_to_order_key_full_mask: tl.constexpr = (1 << _inl_3_to_order_key_nbits) - 1
    _inl_3_to_order_key_full = tl.full(_inl_3_to_order_key_vals.shape, _inl_3_to_order_key_full_mask, dtype=_inl_3_to_order_key_utype)
    if _inl_3_to_order_key_dtype.is_floating():
        _inl_3_to_order_key_bits = _inl_3_to_order_key_vals.to(_inl_3_to_order_key_utype, bitcast=True)
        _inl_3_to_order_key_sign_mask = tl.where(_inl_3_to_order_key_bits & _inl_3_to_order_key_top_mask != 0, _inl_3_to_order_key_full_mask, _inl_3_to_order_key_top_mask)
        _inl_3_to_order_key_key = _inl_3_to_order_key_bits ^ _inl_3_to_order_key_sign_mask
    elif _inl_3_to_order_key_dtype.is_int_signed():
        _inl_3_to_order_key_bits = _inl_3_to_order_key_vals.to(_inl_3_to_order_key_utype, bitcast=True)
        _inl_3_to_order_key_key = _inl_3_to_order_key_bits ^ _inl_3_to_order_key_top_mask
    else:
        _inl_3_to_order_key_key = _inl_3_to_order_key_vals.to(_inl_3_to_order_key_utype)
    _inl_3_to_order_key_result = tl.where(_inl_3_to_order_key_valid, _inl_3_to_order_key_key, _inl_3_to_order_key_full)
    keys = _inl_3_to_order_key_result.to(tl.int32)
    keys = tl.where(mask, keys, 0)
    counts = tl.histogram(keys, HISTOGRAM_BINS).to(tl.int32)
    invalid_count = tl.sum((~mask).to(tl.int32), axis=0)
    counts = counts - tl.where(bins == 0, invalid_count, 0)
    count_offsets = (pid_m * NUM_CHUNKS + pid_chunk) * HISTOGRAM_BINS + bins
    tl.store(partial_counts + count_offsets, counts)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (1420,)  workload x2:dim0 710->1420
#   规模  (2130,)  workload x3:dim0 710->2130
SHAPES = ((17,), (108,))
DTYPES = ("int8",)

def ref(args,meta):
 import numpy as np
 M=int(args["M"]);C=int(meta["N"]);B=int(meta["BLOCK_N"]);chunks=int(meta["NUM_CHUNKS"]);bins=int(meta["HISTOGRAM_BINS"]);x=np.asarray(args["inp"],np.int8).reshape(M,C);keys=x.view(np.uint8)^np.uint8(0x80);out=np.zeros((M,chunks,bins),np.int32)
 for r in range(M):
  for c in range(chunks):out[r,c]=np.bincount(keys[r,c*B:min((c+1)*B,C)].astype(np.int64),minlength=bins)
 return {"partial_counts":out.reshape(-1)}

def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=20260901):
 from case_utils import fast_rng
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 M=3;C=max(3,N);B=128;chunks=(C+B-1)//B;bins=256;x=rng.integers(-128,128,(M,C),dtype=np.int16).astype(np.int8);args={"inp":np.asarray(x,"int8"),"partial_counts":np.asarray(np.full(M*chunks*bins,-1),"int32"),"M":M};meta={"N":C,"BLOCK_N":B,"NUM_CHUNKS":chunks,"HISTOGRAM_BINS":bins};grid=(M,chunks)
 outputs=('partial_counts',);return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0002, "atol": 2e-05, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, nanmedian_ascend_histogram_count_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)
