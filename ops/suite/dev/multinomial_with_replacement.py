"""multinomial_with_replacement: 从 ~/ops 仓库复制(flaggems @ ops-pool),保留其已验证的 case 层。

模式: args.runtime_scalar、cast.to、control.for_range、control.if、control.loop_carried、creation.arange、creation.where、creation.zeros、dtype.float32、dtype.int32。load/store 带掩码,越界的 lane 由 other/padding 处理,所以 SHAPES 里既有整除尺寸也有非整除的尾块。循环上界来自运行时标量(不是 constexpr)。constexpr 参数: NBLOCK。

文件只有两层:
  ① multinomial_with_replacement   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/multinomial_with_replacement', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'cast.to', 'control.for_range', 'control.if', 'control.loop_carried', 'creation.arange', 'creation.where', 'creation.zeros', 'dtype.float32', 'dtype.int32', 'dtype.int64', 'dtype.uint32', 'math.log2', 'memory.load', 'memory.load.masked', 'memory.store', 'memory.store.masked', 'random.philox']}
COPIED_FROM = {'repo': 'flaggems @ ops-pool', 'note': 'validated case layer intact', 'lines': 197}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit(do_not_specialize=['K', 'N', 'philox_seed', 'philox_offset'])
def multinomial_with_replacement(cdf_ptr, out_ptr, K, N, philox_seed, philox_offset, NBLOCK: tl.constexpr=128):
    y_off = tl.program_id(1) * N
    n = tl.program_id(0) * NBLOCK + tl.arange(0, NBLOCK)
    _inl_1_uniform_seed = philox_seed
    _inl_1_uniform_philox_offset = philox_offset
    _inl_1_uniform_offset = y_off + n
    _inl_1_uniform_seed = _inl_1_uniform_seed.to(tl.int64)
    _inl_1_uniform_philox_offset = _inl_1_uniform_philox_offset.to(tl.int64)
    _inl_1_uniform_c0 = (_inl_1_uniform_philox_offset & 4294967295).to(tl.uint32)
    _inl_1_uniform_c1 = (_inl_1_uniform_philox_offset >> 32 & 4294967295).to(tl.uint32)
    _inl_1_uniform_i4 = _inl_1_uniform_offset
    _inl_1_uniform_c0 += _inl_1_uniform_i4
    _inl_1_uniform__O = _inl_1_uniform_c0 * 0
    (_inl_1_uniform_r0, _inl_1_uniform_r1, _inl_1_uniform_r2, _inl_1_uniform_r3) = tl.philox(_inl_1_uniform_seed, _inl_1_uniform_c0, _inl_1_uniform_c1, _inl_1_uniform__O, _inl_1_uniform__O)
    _inl_2_uint_to_uniform_float_x = _inl_1_uniform_r0
    '\n        Numerically stable function to convert a random uint into a random float uniformly sampled in [0, 1).\n        '
    if tl.constexpr(_inl_2_uint_to_uniform_float_x.dtype == tl.uint32) or tl.constexpr(_inl_2_uint_to_uniform_float_x.dtype == tl.int32):
        _inl_2_uint_to_uniform_float_x = _inl_2_uint_to_uniform_float_x.to(tl.int32, bitcast=True)
        _inl_2_uint_to_uniform_float_scale = 4.6566127342e-10
    else:
        _inl_2_uint_to_uniform_float_x = _inl_2_uint_to_uniform_float_x.to(tl.int64, bitcast=True)
        _inl_2_uint_to_uniform_float_scale = 1.0842020432385337e-19
    _inl_2_uint_to_uniform_float_x = tl.where(_inl_2_uint_to_uniform_float_x < 0, -_inl_2_uint_to_uniform_float_x - 1, _inl_2_uint_to_uniform_float_x)
    _inl_2_uint_to_uniform_float_result = _inl_2_uint_to_uniform_float_x * _inl_2_uint_to_uniform_float_scale
    _inl_1_uniform_r0 = _inl_2_uint_to_uniform_float_result
    _inl_3_uint_to_uniform_float_x = _inl_1_uniform_r1
    '\n        Numerically stable function to convert a random uint into a random float uniformly sampled in [0, 1).\n        '
    if tl.constexpr(_inl_3_uint_to_uniform_float_x.dtype == tl.uint32) or tl.constexpr(_inl_3_uint_to_uniform_float_x.dtype == tl.int32):
        _inl_3_uint_to_uniform_float_x = _inl_3_uint_to_uniform_float_x.to(tl.int32, bitcast=True)
        _inl_3_uint_to_uniform_float_scale = 4.6566127342e-10
    else:
        _inl_3_uint_to_uniform_float_x = _inl_3_uint_to_uniform_float_x.to(tl.int64, bitcast=True)
        _inl_3_uint_to_uniform_float_scale = 1.0842020432385337e-19
    _inl_3_uint_to_uniform_float_x = tl.where(_inl_3_uint_to_uniform_float_x < 0, -_inl_3_uint_to_uniform_float_x - 1, _inl_3_uint_to_uniform_float_x)
    _inl_3_uint_to_uniform_float_result = _inl_3_uint_to_uniform_float_x * _inl_3_uint_to_uniform_float_scale
    _inl_1_uniform_r1 = _inl_3_uint_to_uniform_float_result
    _inl_4_uint_to_uniform_float_x = _inl_1_uniform_r2
    '\n        Numerically stable function to convert a random uint into a random float uniformly sampled in [0, 1).\n        '
    if tl.constexpr(_inl_4_uint_to_uniform_float_x.dtype == tl.uint32) or tl.constexpr(_inl_4_uint_to_uniform_float_x.dtype == tl.int32):
        _inl_4_uint_to_uniform_float_x = _inl_4_uint_to_uniform_float_x.to(tl.int32, bitcast=True)
        _inl_4_uint_to_uniform_float_scale = 4.6566127342e-10
    else:
        _inl_4_uint_to_uniform_float_x = _inl_4_uint_to_uniform_float_x.to(tl.int64, bitcast=True)
        _inl_4_uint_to_uniform_float_scale = 1.0842020432385337e-19
    _inl_4_uint_to_uniform_float_x = tl.where(_inl_4_uint_to_uniform_float_x < 0, -_inl_4_uint_to_uniform_float_x - 1, _inl_4_uint_to_uniform_float_x)
    _inl_4_uint_to_uniform_float_result = _inl_4_uint_to_uniform_float_x * _inl_4_uint_to_uniform_float_scale
    _inl_1_uniform_r2 = _inl_4_uint_to_uniform_float_result
    _inl_5_uint_to_uniform_float_x = _inl_1_uniform_r3
    '\n        Numerically stable function to convert a random uint into a random float uniformly sampled in [0, 1).\n        '
    if tl.constexpr(_inl_5_uint_to_uniform_float_x.dtype == tl.uint32) or tl.constexpr(_inl_5_uint_to_uniform_float_x.dtype == tl.int32):
        _inl_5_uint_to_uniform_float_x = _inl_5_uint_to_uniform_float_x.to(tl.int32, bitcast=True)
        _inl_5_uint_to_uniform_float_scale = 4.6566127342e-10
    else:
        _inl_5_uint_to_uniform_float_x = _inl_5_uint_to_uniform_float_x.to(tl.int64, bitcast=True)
        _inl_5_uint_to_uniform_float_scale = 1.0842020432385337e-19
    _inl_5_uint_to_uniform_float_x = tl.where(_inl_5_uint_to_uniform_float_x < 0, -_inl_5_uint_to_uniform_float_x - 1, _inl_5_uint_to_uniform_float_x)
    _inl_5_uint_to_uniform_float_result = _inl_5_uint_to_uniform_float_x * _inl_5_uint_to_uniform_float_scale
    _inl_1_uniform_r3 = _inl_5_uint_to_uniform_float_result
    _inl_1_uniform_result = (_inl_1_uniform_r0, _inl_1_uniform_r1, _inl_1_uniform_r2, _inl_1_uniform_r3)
    (rv, _, _, _) = _inl_1_uniform_result
    cdf_ptr += tl.program_id(1) * K
    start = tl.zeros((NBLOCK,), dtype=tl.int32)
    end = tl.zeros((NBLOCK,), dtype=tl.int32) + K - 1
    steps = tl.log2(K.to(tl.float32)).to(tl.int32) + 1
    for _ in range(steps):
        mid = start + (end - start) // 2
        x = tl.load(cdf_ptr + mid, mask=n < N)
        start = tl.where(x <= rv, mid + 1, start)
        end = tl.where(x <= rv, end, mid)
    start = tl.where(start >= K, K - 1, start)
    tl.store(out_ptr + y_off + n, start, mask=n < N)

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

SHAPES=((17,), (5, 5, 8));DTYPES=('float32', 'float16', 'bfloat16')
SHAPES=((17,), (5, 5, 8));DTYPES=('float32', 'float16', 'bfloat16')
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
 K=int(args["K"]);S=int(args["N"]);cdf=args["cdf_ptr"].reshape(-1);rows=cdf.size//K;out=[]
 for row in range(rows):
  raw=_philox(row*S+np.arange(S),int(args["philox_seed"]),int(args["philox_offset"]))[0];u=_to_uniform(raw);out.extend(np.searchsorted(cdf[row*K:(row+1)*K],u,side="right").clip(max=K-1))
 return {"out_ptr":np.asarray(out,np.int64)}
def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    if len(shape) > 1 and tuple(shape) not in SHAPES:
        raise ValueError('unsupported explicit shape configuration')
    del dtype
    import numpy as np
    N = int(shape[0])
    from case_utils import fast_rng
    rng = fast_rng(seed)
    R = int(shape[0]) if len(shape) > 1 else 2
    K = int(shape[1]) if len(shape) > 1 else 5
    S = int(shape[2]) if len(shape) > 1 else max(2, N // R)
    prob = rng.uniform(0.1, 1, (R, K))
    cdf = np.cumsum(prob / prob.sum(1, keepdims=True), axis=1)
    args = {'cdf_ptr': _aligned(cdf), 'out_ptr': _aligned(np.full(R * S, -1), 'int64'), 'K': K, 'N': S, 'philox_seed': 81985529216486895, 'philox_offset': 37}
    meta = {'NBLOCK': 128}
    grid = ((S + 127) // 128, R)
    outputs = ('out_ptr',)
    return _case(multinomial_with_replacement, grid, args, meta, ('cdf_ptr',), outputs, ref(args, meta), shape, 'float32', seed, {'complete_launch_plan': True, 'formula': 'multinomial samples by Philox uniforms and CDF search'})
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
