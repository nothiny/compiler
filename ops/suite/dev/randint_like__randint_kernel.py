"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/randint_like__randint_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import triton
import triton.language as tl
from case_utils import fast_rng

@triton.jit(do_not_specialize=['philox_seed', 'philox_offset'])
def randint_kernel(out_ptr, N, high, philox_seed, philox_offset, BLOCK: tl.constexpr):
    philox_seed = philox_seed.to(tl.int64)
    philox_offset = philox_offset.to(tl.int64)
    c0 = (philox_offset & 4294967295).to(tl.uint32)
    c1 = (philox_offset >> 32 & 4294967295).to(tl.uint32)
    i4 = tl.program_id(0) * BLOCK + tl.arange(0, BLOCK)
    c0 += i4
    _O = c0 * 0
    (r0, r1, r2, r3) = tl.philox(philox_seed, c0, c1, _O, _O)
    _inl_1_uint_to_uniform_float_x = r0
    '\n        Numerically stable function to convert a random uint into a random float uniformly sampled in [0, 1).\n        '
    if tl.constexpr(_inl_1_uint_to_uniform_float_x.dtype == tl.uint32) or tl.constexpr(_inl_1_uint_to_uniform_float_x.dtype == tl.int32):
        _inl_1_uint_to_uniform_float_x = _inl_1_uint_to_uniform_float_x.to(tl.int32, bitcast=True)
        _inl_1_uint_to_uniform_float_scale = 4.6566127342e-10
    else:
        _inl_1_uint_to_uniform_float_x = _inl_1_uint_to_uniform_float_x.to(tl.int64, bitcast=True)
        _inl_1_uint_to_uniform_float_scale = 1.0842020432385337e-19
    _inl_1_uint_to_uniform_float_x = tl.where(_inl_1_uint_to_uniform_float_x < 0, -_inl_1_uint_to_uniform_float_x - 1, _inl_1_uint_to_uniform_float_x)
    _inl_1_uint_to_uniform_float_result = _inl_1_uint_to_uniform_float_x * _inl_1_uint_to_uniform_float_scale
    u0 = _inl_1_uint_to_uniform_float_result
    _inl_2_uint_to_uniform_float_x = r1
    '\n        Numerically stable function to convert a random uint into a random float uniformly sampled in [0, 1).\n        '
    if tl.constexpr(_inl_2_uint_to_uniform_float_x.dtype == tl.uint32) or tl.constexpr(_inl_2_uint_to_uniform_float_x.dtype == tl.int32):
        _inl_2_uint_to_uniform_float_x = _inl_2_uint_to_uniform_float_x.to(tl.int32, bitcast=True)
        _inl_2_uint_to_uniform_float_scale = 4.6566127342e-10
    else:
        _inl_2_uint_to_uniform_float_x = _inl_2_uint_to_uniform_float_x.to(tl.int64, bitcast=True)
        _inl_2_uint_to_uniform_float_scale = 1.0842020432385337e-19
    _inl_2_uint_to_uniform_float_x = tl.where(_inl_2_uint_to_uniform_float_x < 0, -_inl_2_uint_to_uniform_float_x - 1, _inl_2_uint_to_uniform_float_x)
    _inl_2_uint_to_uniform_float_result = _inl_2_uint_to_uniform_float_x * _inl_2_uint_to_uniform_float_scale
    u1 = _inl_2_uint_to_uniform_float_result
    _inl_3_uint_to_uniform_float_x = r2
    '\n        Numerically stable function to convert a random uint into a random float uniformly sampled in [0, 1).\n        '
    if tl.constexpr(_inl_3_uint_to_uniform_float_x.dtype == tl.uint32) or tl.constexpr(_inl_3_uint_to_uniform_float_x.dtype == tl.int32):
        _inl_3_uint_to_uniform_float_x = _inl_3_uint_to_uniform_float_x.to(tl.int32, bitcast=True)
        _inl_3_uint_to_uniform_float_scale = 4.6566127342e-10
    else:
        _inl_3_uint_to_uniform_float_x = _inl_3_uint_to_uniform_float_x.to(tl.int64, bitcast=True)
        _inl_3_uint_to_uniform_float_scale = 1.0842020432385337e-19
    _inl_3_uint_to_uniform_float_x = tl.where(_inl_3_uint_to_uniform_float_x < 0, -_inl_3_uint_to_uniform_float_x - 1, _inl_3_uint_to_uniform_float_x)
    _inl_3_uint_to_uniform_float_result = _inl_3_uint_to_uniform_float_x * _inl_3_uint_to_uniform_float_scale
    u2 = _inl_3_uint_to_uniform_float_result
    _inl_4_uint_to_uniform_float_x = r3
    '\n        Numerically stable function to convert a random uint into a random float uniformly sampled in [0, 1).\n        '
    if tl.constexpr(_inl_4_uint_to_uniform_float_x.dtype == tl.uint32) or tl.constexpr(_inl_4_uint_to_uniform_float_x.dtype == tl.int32):
        _inl_4_uint_to_uniform_float_x = _inl_4_uint_to_uniform_float_x.to(tl.int32, bitcast=True)
        _inl_4_uint_to_uniform_float_scale = 4.6566127342e-10
    else:
        _inl_4_uint_to_uniform_float_x = _inl_4_uint_to_uniform_float_x.to(tl.int64, bitcast=True)
        _inl_4_uint_to_uniform_float_scale = 1.0842020432385337e-19
    _inl_4_uint_to_uniform_float_x = tl.where(_inl_4_uint_to_uniform_float_x < 0, -_inl_4_uint_to_uniform_float_x - 1, _inl_4_uint_to_uniform_float_x)
    _inl_4_uint_to_uniform_float_result = _inl_4_uint_to_uniform_float_x * _inl_4_uint_to_uniform_float_scale
    u3 = _inl_4_uint_to_uniform_float_result
    high_f = high.to(tl.float32)
    i0 = (u0 * high_f).to(tl.int32)
    i1 = (u1 * high_f).to(tl.int32)
    i2 = (u2 * high_f).to(tl.int32)
    i3 = (u3 * high_f).to(tl.int32)
    off_0 = tl.program_id(0) * BLOCK * 4 + tl.arange(0, BLOCK)
    off_1 = off_0 + BLOCK
    off_2 = off_1 + BLOCK
    off_3 = off_2 + BLOCK
    tl.store(out_ptr + off_0, i0, mask=off_0 < N, eviction_policy='evict_first')
    tl.store(out_ptr + off_1, i1, mask=off_1 < N, eviction_policy='evict_first')
    tl.store(out_ptr + off_2, i2, mask=off_2 < N, eviction_policy='evict_first')
    tl.store(out_ptr + off_3, i3, mask=off_3 < N, eviction_policy='evict_first')
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
SHAPES=((17,), (97,));DTYPES=('float32', 'float16', 'bfloat16')
def ref(args,meta):
 import numpy as np
 def _philox(c0,seed,offset):
  mask=np.uint64(0xffffffff);c0=(np.asarray(c0,dtype=np.uint64)+np.uint64(offset&0xffffffff))&mask;c1=np.full(c0.shape,(offset>>32)&0xffffffff,np.uint64);c2=np.zeros_like(c0);c3=np.zeros_like(c0);k0=np.uint64(seed&0xffffffff);k1=np.uint64((seed>>32)&0xffffffff)
  for _ in range(10):
   p0=np.uint64(0xD2511F53)*c0;p1=np.uint64(0xCD9E8D57)*c2;hi0=p0>>np.uint64(32);lo0=p0&mask;hi1=p1>>np.uint64(32);lo1=p1&mask;c0,c1,c2,c3=(hi1^c1^k0)&mask,lo1,(hi0^c3^k1)&mask,lo0;k0=(k0+np.uint64(0x9E3779B9))&mask;k1=(k1+np.uint64(0xBB67AE85))&mask
  return tuple(v.astype(np.uint32) for v in (c0,c1,c2,c3))
 def _to_uniform(raw):
  signed=raw.view(np.int32).astype(np.int64);return (np.where(signed<0,-signed-1,signed).astype(np.float32)*np.float32(4.6566127342e-10)).astype(np.float32)
 def _random_words(n,seed,offset,block):
  out=np.empty(n,np.uint32);programs=(n+4*block-1)//(4*block)
  for pid in range(programs):
   r=_philox(pid*block+np.arange(block),seed,offset);base=pid*4*block
   for q in range(4):
    idx=base+q*block+np.arange(block);valid=idx<n;out[idx[valid]]=r[q][valid]
  return out
 def _uniform(n,seed,offset,block):return _to_uniform(_random_words(n,seed,offset,block))
 def _normal(n,seed,offset,block):
  out=np.empty(n,np.float32);programs=(n+4*block-1)//(4*block)
  for pid in range(programs):
   raw=_philox(pid*block+np.arange(block),seed,offset);u=[_to_uniform(v) for v in raw];r0=np.sqrt(-2*np.log(np.maximum(u[0],1e-7)));t0=2*np.pi*u[1];r1=np.sqrt(-2*np.log(np.maximum(u[2],1e-7)));t1=2*np.pi*u[3];vals=(r0*np.cos(t0),r0*np.sin(t0),r1*np.cos(t1),r1*np.sin(t1));base=pid*4*block
   for q in range(4):
    idx=base+q*block+np.arange(block);valid=idx<n;out[idx[valid]]=vals[q][valid]
  return out
 u=_uniform(int(args["N"]),int(args["philox_seed"]),int(args["philox_offset"]),meta["BLOCK"]);return {"out_ptr":(u*np.float32(args["high"])).astype(np.int32)}
def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=SEED):
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 B=64;args={"out_ptr":_aligned(np.full(N,-1),"int32"),"N":N,"philox_seed":0x123456789ABCDEF,"philox_offset":37,"high":17};meta={"BLOCK":B};grid=((N+4*B-1)//(4*B),)
 outputs=('out_ptr',);return _case(randint_kernel,grid,args,meta,(),outputs,ref(args,meta),shape,"torch.float32",seed,{"complete_launch_plan":True,"formula":'integer Philox samples by scaled uniform'})

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


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float32'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float32': 'torch.float32'}


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
