"""any_kernel_2: 逻辑或 any 的收尾:partial 位或成全局标量。

模式: args.runtime_scalar, cast.to, creation.arange, memory.load.masked, memory.load.other, memory.store, reduce.max。

文件只有两层:
  ① any_kernel_2   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/any_kernel_2", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "cast.to", "creation.arange", "memory.load.masked", "memory.load.other", "memory.store", "reduce.max"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/any_kernel_2.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def any_kernel_2(mid, out, MID_SIZE, BLOCK_MID: tl.constexpr):
    offset = tl.arange(0, BLOCK_MID)
    mid_ptrs = mid + offset
    mask = offset < MID_SIZE
    mid_val = tl.load(mid_ptrs, mask=mask, other=0).to(tl.int1)
    any_val = tl.max(mid_val, axis=0)
    tl.store(out, any_val)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (2814,)  workload x2:dim0 1407->2814
#   规模  (4221,)  workload x3:dim0 1407->4221
SHAPES = ((17,), (126,))
DTYPES = ("bool",)

def ref(args,meta):
 import numpy as np
 return {"out":np.asarray([np.any(args["mid"][:int(args["MID_SIZE"])])],np.bool_)}

def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=20260901):
 from case_utils import fast_rng
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 K=max(1,(N+127)//128);args={"mid":np.asarray((np.arange(K)%3)==0,"bool"),"out":np.asarray(np.zeros(1),"bool"),"MID_SIZE":K};meta={"BLOCK_MID":1<<(K-1).bit_length()};grid=(1,)
 outputs=('out',);return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0002, "atol": 2e-05, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, any_kernel_2, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)
