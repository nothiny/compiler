"""csr_value_index_kernel: 把 CSR 的非零元映射回稠密矩阵的值下标。

模式: args.runtime_scalar, cast.to, control.for_range, creation.arange, memory.load.masked, memory.load.other, memory.store。

文件只有两层:
  ① _csr_value_index_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/csr_value_index_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "cast.to", "control.for_range", "creation.arange", "memory.load.masked", "memory.load.other", "memory.store"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/csr_value_index_kernel.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def _csr_value_index_kernel(crow_ptr, col_ptr, idx_ptr, M, N, nnz_per_batch, BLOCK: tl.constexpr):
    pid = tl.program_id(0).to(tl.int64)
    b = pid // M
    r = pid % M
    crow_base = crow_ptr + b.to(tl.int64) * (M + 1)
    row_start = tl.load(crow_base + r).to(tl.int64)
    row_end = tl.load(crow_base + r + 1).to(tl.int64)
    col_base = col_ptr + b.to(tl.int64) * nnz_per_batch
    out_base = idx_ptr + b.to(tl.int64) * M * N + r.to(tl.int64) * N
    for start in range(row_start, row_end, BLOCK):
        e = start + tl.arange(0, BLOCK)
        mask = e < row_end
        c = tl.load(col_base + e, mask=mask, other=0)
        tl.store(out_base + c, e.to(tl.int32), mask=mask)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (6, 3, 4)  workload x2:dim0 3->6
#   规模  (3, 3, 8)  workload x2:dim2 4->8
SHAPES = ((17,), (3, 3, 8))
DTYPES = ("int64",)

def ref(args,meta):
 import numpy as np
 B=args["crow_ptr"].size//(int(args["M"])+1);M=int(args["M"]);C=int(args["N"]);out=np.array(args["idx_ptr"],copy=True).reshape(B,M,C);crow=args["crow_ptr"].reshape(B,M+1);cols=args["col_ptr"].reshape(B,int(args["nnz_per_batch"]))
 for b in range(B):
  for r in range(M):
   for e in range(int(crow[b,r]),int(crow[b,r+1])):out[b,r,int(cols[b,e])]=e
 return {"idx_ptr":out.reshape(-1)}

def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=20260901):
    from case_utils import fast_rng
    if len(shape) > 1 and tuple(shape) not in SHAPES:
        raise ValueError('unsupported explicit shape configuration')
    del dtype
    import numpy as np
    N = int(shape[0])
    rng = fast_rng(seed)
    B = int(shape[0]) if len(shape) > 1 else 2
    M = int(shape[1]) if len(shape) > 1 else 3
    C = int(shape[2]) if len(shape) > 1 else 4
    crow = np.tile(np.asarray([0, 2, 3, 5]), (B, 1))
    cols = np.tile(np.asarray([0, 2, 1, 0, 3]), (B, 1))
    args = {'crow_ptr': np.asarray(crow, 'int64'), 'col_ptr': np.asarray(cols, 'int64'), 'idx_ptr': np.asarray(np.full(B * M * C, -1), 'int32'), 'M': M, 'N': C, 'nnz_per_batch': 5}
    meta = {'BLOCK': 128}
    grid = (B * M,)
    outputs = ('idx_ptr',)
    return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0002, "atol": 2e-05, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, _csr_value_index_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)
