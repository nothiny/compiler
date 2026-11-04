"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/unique_dim_row_chunk_diff_hash_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit
def _unique_dim_row_chunk_diff_hash_kernel(flat_ptr: tl.tensor, sorted_indices_ptr: tl.tensor, row_hash_ptr: tl.tensor, row_chunk_diff_ptr: tl.tensor, num_rows: int, row_len: int, num_chunks: int, BLOCK_SIZE: tl.constexpr):
    row = tl.program_id(0).to(tl.int64)
    chunk = tl.program_id(1).to(tl.int64)
    offsets = chunk * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = offsets < row_len
    out = tl.full((), 0, dtype=tl.int32)
    if row == 0:
        out = tl.where(chunk == 0, 1, 0)
    else:
        cur_row = tl.load(sorted_indices_ptr + row)
        prev_row = tl.load(sorted_indices_ptr + row - 1)
        cur_hash = tl.load(row_hash_ptr + cur_row)
        prev_hash = tl.load(row_hash_ptr + prev_row)
        if cur_hash != prev_hash:
            out = tl.where(chunk == 0, 1, 0)
        else:
            cur = tl.load(flat_ptr + cur_row * row_len + offsets, mask=mask)
            prev = tl.load(flat_ptr + prev_row * row_len + offsets, mask=mask)
            neq = (cur != prev) & mask
            has_diff = tl.sum(neq.to(tl.int32), axis=0) != 0
            out = has_diff.to(tl.int32)
    tl.store(row_chunk_diff_ptr + row * num_chunks + chunk, out)
CASE_SCHEMA = 3
SUPPORT_STATUS = "supported"
VALIDATION_SCOPE = "full-launch-correctness"
SEED = 20260901


def _aligned(values, dtype="float32", alignment=64):
    import numpy as np

    values = np.asarray(values, dtype=np.dtype(dtype))
    raw = np.empty(values.size * values.dtype.itemsize + alignment, dtype=np.uint8)
    start = -raw.ctypes.data % alignment
    result = raw[start : start + values.size * values.dtype.itemsize].view(values.dtype)
    result[...] = values.reshape(-1)
    return result.reshape(values.shape)


def _case(kernel, grid, args, meta, inputs, outputs, expected, shape, dtype, seed, coverage, rtol=0.0002, atol=2e-05):
    import numpy as np
    _comparison_dtype_policy = str(dtype)
    if _comparison_dtype_policy == 'torch.float32':
        (rtol, atol) = (0.0001, 0.0001)
    elif _comparison_dtype_policy == 'torch.bfloat16':
        (rtol, atol) = (0.01, 0.01)
    comparison = {name: {'profile': 'numerical', 'comparator': 'allclose', 'exact': False, 'rtol': float(rtol), 'atol': float(atol), 'equal_nan': True} for name in outputs}
    arrays = {name: value for (name, value) in args.items() if isinstance(value, np.ndarray)}
    return {'kernel': kernel, 'grid': tuple((int(value) for value in grid)), 'args': args, 'meta': meta, 'launch_meta': {'num_warps': 4, 'num_stages': 1}, 'inputs': tuple(inputs), 'outputs': tuple(outputs), 'expected': expected, 'comparison': comparison, 'pointer_dtypes': {name: str(value.dtype) for (name, value) in arrays.items()}, 'buffer_extents': {name: int(value.size) for (name, value) in arrays.items()}, 'buffer_layouts': {name: {'shape': tuple((int(x) for x in value.shape)), 'strides': tuple((int(x // value.dtype.itemsize) for x in value.strides))} for (name, value) in arrays.items()}, 'alignment': 64, 'aliases': {}, 'seed': int(seed), 'shape': tuple(shape), 'dtype': str(dtype), 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'coverage': {'complete_logical_output': True, **coverage}}
SHAPES=((17,), (97,));DTYPES=('torch.int32',)
def ref(args,meta):
 import numpy as np
 R=int(args["num_rows"]);L=int(args["row_len"]);C=int(args["num_chunks"]);B=int(meta["BLOCK_SIZE"]);x=np.asarray(args["flat_ptr"]).reshape(R,L);order=np.asarray(args["sorted_indices_ptr"],np.int64);h=np.asarray(args["row_hash_ptr"],np.int64);out=np.zeros((R,C),np.int32);out[0,0]=1
 for r in range(1,R):
  cur=order[r];prev=order[r-1]
  if h[cur]!=h[prev]:out[r,0]=1
  else:
   for c in range(C):
    s=c*B;e=min(s+B,L);out[r,c]=int(np.any(x[cur,s:e]!=x[prev,s:e]))
 return {"row_chunk_diff_ptr":out.reshape(-1)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 R=5;L=max(3,N);C=(L+127)//128;x=rng.integers(-9,10,(R,L),dtype=np.int32);x[1]=x[0];x[2]=x[0];x[2,-1]+=1;x[4]=x[3];order=np.arange(R,dtype=np.int64);off=np.arange(L,dtype=np.int64);h=np.sum((x.astype(np.int64)+(off+1)*1009+9176)*131071,axis=1,dtype=np.int64);h[2]=h[1];args={"flat_ptr":_aligned(x,"int32"),"sorted_indices_ptr":_aligned(order,"int64"),"row_hash_ptr":_aligned(h,"int64"),"row_chunk_diff_ptr":_aligned(np.full(R*C,-1),"int32"),"num_rows":R,"row_len":L,"num_chunks":C};meta={"BLOCK_SIZE":128};grid=(R,C)
 outputs=('row_chunk_diff_ptr',);return _case(_unique_dim_row_chunk_diff_hash_kernel,grid,args,meta,('flat_ptr', 'sorted_indices_ptr', 'row_hash_ptr'),outputs,ref(args,meta),shape,"torch.float32",seed,{"complete_launch_plan":True,"formula":'hash-prefiltered per-chunk adjacent-row differences, including an exercised hash collision'})

def make_case(shape=None, dtype=None, seed=None):
    """Create one host case; defaults and supported dtypes are operator-owned."""
    import numpy as np

    requested = None
    if dtype is not None:
        try:
            requested = np.dtype(dtype).name
        except TypeError:
            requested = str(dtype).rsplit(".", 1)[-1]
    choices = {str(value).rsplit(".", 1)[-1]: value for value in DTYPES}
    if requested is not None and requested not in choices:
        raise ValueError(f"unsupported dtype {dtype}; choose from {tuple(choices)}")
    options = {}
    if shape is not None:
        options["shape"] = tuple(shape)
    if requested is not None:
        options["dtype"] = choices[requested]
    if seed is not None:
        options["seed"] = seed
    case = _make_case(**options)
    case.setdefault("outputs", tuple(case["expected"]))
    case.setdefault("launch_meta", {})
    return case


# ------------------------------------------------------------------ ② 执行单元(case 驱动)
def run(shape=None, dtype=None, seed=None, to_array=None):
    """直接执行:make_case 构造输入 → kernel[grid] 启动 → 返回输出。

    to_array=None 时数组参数按 numpy 原样传给 launcher(自研编译器的 staging
    语义);传入数组转换器(如 numpy→torch.cuda)即可在真实 Triton 上执行。
    """
    import sys

    from case_utils import run_case

    return run_case(sys.modules[__name__], shape=shape, dtype=dtype,
                    seed=seed, to_array=to_array)
