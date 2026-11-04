"""unique_dim_row_single_chunk_first_kernel: 每行"是否首次出现":与排序后的上一行逐元素比较。

模式: args.runtime_scalar, cast.to, control.if, creation.arange, creation.full, memory.load.masked, memory.store, reduce.sum。

文件只有两层:
  ① _unique_dim_row_single_chunk_first_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/unique_dim_row_single_chunk_first_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "cast.to", "control.if", "creation.arange", "creation.full", "memory.load.masked", "memory.store", "reduce.sum"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/unique_dim_row_single_chunk_first_kernel.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def _unique_dim_row_single_chunk_first_kernel(flat_ptr: tl.tensor, sorted_indices_ptr: tl.tensor, is_first_ptr: tl.tensor, num_rows: int, row_len: int, BLOCK_SIZE: tl.constexpr):
    row = tl.program_id(0).to(tl.int64)
    offsets = tl.arange(0, BLOCK_SIZE)
    mask = offsets < row_len
    out = tl.full((), True, dtype=tl.int1)
    if row != 0:
        cur_row = tl.load(sorted_indices_ptr + row)
        prev_row = tl.load(sorted_indices_ptr + row - 1)
        cur = tl.load(flat_ptr + cur_row * row_len + offsets, mask=mask)
        prev = tl.load(flat_ptr + prev_row * row_len + offsets, mask=mask)
        neq = (cur != prev) & mask
        out = tl.sum(neq.to(tl.int32), axis=0) != 0
    tl.store(is_first_ptr + row, out)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (1672,)  workload x2:dim0 836->1672
#   规模  (2508,)  workload x3:dim0 836->2508
SHAPES = ((17,), (104,))
DTYPES = ("int32",)

def ref(args,meta):
 import numpy as np
 R=int(args["num_rows"]);L=int(args["row_len"]);x=np.asarray(args["flat_ptr"]).reshape(R,L);order=np.asarray(args["sorted_indices_ptr"],np.int64);out=np.ones(R,np.bool_)
 for r in range(1,R):out[r]=np.any(x[order[r]]!=x[order[r-1]])
 return {"is_first_ptr":out}

def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=20260901):
 from case_utils import fast_rng
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 R=5;L=max(3,N);x=rng.integers(-9,10,(R,L),dtype=np.int32);x[1]=x[0];x[4]=x[3];order=np.arange(R,dtype=np.int64);B=1<<(L-1).bit_length();args={"flat_ptr":np.asarray(x,"int32"),"sorted_indices_ptr":np.asarray(order,"int64"),"is_first_ptr":np.asarray(np.full(R,False),"bool"),"num_rows":R,"row_len":L};meta={"BLOCK_SIZE":B};grid=(R,)
 outputs=('is_first_ptr',);return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0002, "atol": 2e-05, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, _unique_dim_row_single_chunk_first_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)
