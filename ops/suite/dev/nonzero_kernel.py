"""nonzero_kernel: 从 ~/ops 仓库复制(flaggems @ ops),保留其已验证的 case 层。

模式: args.runtime_scalar、cast.to、control.for_range、control.loop_carried、creation.arange、dtype.int1、dtype.int64、memory.load、memory.load.masked、memory.store。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。循环上界来自运行时标量(不是 constexpr)。constexpr 参数: ndim, BLOCK_SIZE。

文件只有两层:
  ① nonzero_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/nonzero_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'cast.to', 'control.for_range', 'control.loop_carried', 'creation.arange', 'dtype.int1', 'dtype.int64', 'memory.load', 'memory.load.masked', 'memory.store', 'memory.store.masked']}
COPIED_FROM = {'repo': 'flaggems @ ops', 'note': 'validated case layer intact', 'lines': 103}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def nonzero_kernel(inp, prefix_sum, out, n_elements, shape, ndim: tl.constexpr, BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(0).to(tl.int64)
    offset = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = offset < n_elements
    inp_vals = tl.load(inp + offset, mask=mask).to(tl.int1)
    out_offset = tl.load(prefix_sum + offset, mask=mask) - 1
    nonzero_mask = mask and inp_vals
    idx_flat = offset
    for dim in range(ndim - 1, -1, -1):
        dim_size = tl.load(shape + dim)
        remainder = idx_flat % dim_size
        idx_flat //= dim_size
        tl.store(out + out_offset * ndim + dim, remainder, mask=nonzero_mask)

# ------------------------------------------------------------------ ② case 层

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
    if _comparison_dtype_policy == 'float32':
        (rtol, atol) = (0.0001, 0.0001)
    elif _comparison_dtype_policy == 'bfloat16':
        (rtol, atol) = (0.01, 0.01)
    comparison = {name: {'profile': 'numerical', 'comparator': 'allclose', 'exact': False, 'rtol': float(rtol), 'atol': float(atol), 'equal_nan': True} for name in outputs}
    arrays = {name: value for (name, value) in args.items() if isinstance(value, np.ndarray)}
    return {'kernel': kernel, 'grid': tuple((int(value) for value in grid)), 'args': args, 'meta': meta, 'launch_meta': {'num_warps': 4, 'num_stages': 1}, 'inputs': tuple(inputs), 'outputs': tuple(outputs), 'expected': expected, 'comparison': comparison, 'pointer_dtypes': {name: str(value.dtype) for (name, value) in arrays.items()}, 'buffer_extents': {name: int(value.size) for (name, value) in arrays.items()}, 'buffer_layouts': {name: {'shape': tuple((int(x) for x in value.shape)), 'strides': tuple((int(x // value.dtype.itemsize) for x in value.strides))} for (name, value) in arrays.items()}, 'alignment': 64, 'aliases': {}, 'seed': int(seed), 'shape': tuple(shape), 'dtype': str(dtype), 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'coverage': {'complete_logical_output': True, **coverage}}

SHAPES=((17,), (735,));DTYPES=('int32',)
SHAPES=((17,), (735,));DTYPES=('int32',)
def ref(args,meta):
 import numpy as np
 shape=tuple(int(v) for v in args["shape"][:meta["ndim"]]);return {"out":np.argwhere(args["inp"].reshape(shape)!=0).astype(np.int64).reshape(-1)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 from case_utils import fast_rng
 N=int(shape[0]);rng=fast_rng(seed)
 R=3;C=max(2,N//R);x=rng.integers(-1,2,R*C,dtype=np.int32);nz=np.count_nonzero(x);prefix=np.cumsum(x!=0,dtype=np.int64);args={"inp":_aligned(x,"int32"),"prefix_sum":_aligned(prefix,"int64"),"out":_aligned(np.full(nz*2,-1),"int64"),"n_elements":R*C,"shape":_aligned(np.asarray([R,C]),"int64")};meta={"ndim":2,"BLOCK_SIZE":128};grid=((R*C+127)//128,)
 outputs=('out',);return _case(nonzero_kernel,grid,args,meta,('inp', 'prefix_sum', 'shape'),outputs,ref(args,meta),shape,'int32',seed,{"complete_launch_plan":True,"formula":'coordinates of all nonzero elements'})
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
