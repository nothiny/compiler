"""repeat_interleave_tensor_kernel: repeat_interleave 的下标展开(按重复计数)。

模式: args.runtime_scalar, cast.to, control.for_range, creation.arange, memory.load.masked, memory.load.other, memory.store.masked。

文件只有两层:
  ① repeat_interleave_tensor_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/repeat_interleave_tensor_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "cast.to", "control.for_range", "creation.arange", "memory.load.masked", "memory.load.other", "memory.store.masked"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/repeat_interleave_tensor_kernel.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def repeat_interleave_tensor_kernel(repeats_ptr, cumsum_ptr, out_ptr, size, BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(0).to(tl.int64)
    mask = pid < size
    cumsum = tl.load(cumsum_ptr + pid, mask, other=0)
    repeats = tl.load(repeats_ptr + pid, mask, other=0)
    out_offset = cumsum - repeats
    out_ptr += out_offset
    for start_k in range(0, repeats, BLOCK_SIZE):
        offsets_k = start_k + tl.arange(0, BLOCK_SIZE)
        mask_k = offsets_k < repeats
        tl.store(out_ptr + offsets_k, pid, mask=mask_k)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (82,)  workload x2:dim0 41->82
#   规模  (123,)  workload x3:dim0 41->123
NORMAL_SHAPE = (41,)
SHAPES = ((17,), (82,))
DTYPES = ("int32",)

def ref(args,meta):
 import numpy as np
 return {"out_ptr":np.repeat(np.arange(int(args["size"]),dtype=np.int64),args["repeats_ptr"][:int(args["size"])])}

def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=20260901):
    from case_utils import fast_rng
    if tuple(shape) == NORMAL_SHAPE and tuple(shape) not in SHAPES:
        raise ValueError('unsupported explicit shape configuration')
    del dtype
    import numpy as np
    N = int(shape[0])
    rng = fast_rng(seed)
    K = int(shape[0]) if tuple(shape) == NORMAL_SHAPE else max(2, min(64, N))
    repeats = rng.integers(0, 4, K, dtype=np.int32)
    cumsum = np.cumsum(repeats, dtype=np.int64)
    args = {'repeats_ptr': np.asarray(repeats, 'int32'), 'cumsum_ptr': np.asarray(cumsum, 'int64'), 'out_ptr': np.asarray(np.full(int(cumsum[-1]), -1), 'int64'), 'size': K}
    meta = {'BLOCK_SIZE': 8}
    grid = (K,)
    outputs = ('out_ptr',)
    return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0002, "atol": 2e-05, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, repeat_interleave_tensor_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)
