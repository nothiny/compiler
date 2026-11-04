"""linalg_cross_complex_contiguous_kernel: 连续布局复数向量的叉积(头 4 列 + 尾 2 列)。

模式: args.runtime_scalar, creation.arange, creation.where, memory.load.masked, memory.load.other, memory.store.masked, shape.reshape。

文件只有两层:
  ① _linalg_cross_complex_contiguous_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/linalg_cross_complex_contiguous_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "creation.arange", "creation.where", "memory.load.masked", "memory.load.other", "memory.store.masked", "shape.reshape"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/linalg_cross_complex_contiguous_kernel.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def _linalg_cross_complex_contiguous_kernel(input_ptr, other_ptr, output_ptr, num_vectors, BLOCK_SIZE: tl.constexpr):
    """Use coalesced transactions for interleaved contiguous complex data."""
    vector_offsets = tl.program_id(0) * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    head_columns = tl.arange(0, 4)
    tail_columns = tl.arange(0, 2)
    vector_mask = vector_offsets < num_vectors
    vector_base = vector_offsets[:, None] * 6
    head_offsets = vector_base + head_columns[None, :]
    tail_offsets = vector_base + 4 + tail_columns[None, :]
    mask = vector_mask[:, None]
    input_head = tl.load(input_ptr + head_offsets, mask=mask, other=0.0)
    input_tail = tl.load(input_ptr + tail_offsets, mask=mask, other=0.0)
    other_head = tl.load(other_ptr + head_offsets, mask=mask, other=0.0)
    other_tail = tl.load(other_ptr + tail_offsets, mask=mask, other=0.0)
    (input_head_real, input_head_imag) = tl.split(tl.reshape(input_head, (BLOCK_SIZE * 2, 2)))
    (input_0_real, input_1_real) = tl.split(tl.reshape(input_head_real, (BLOCK_SIZE, 2)))
    (input_0_imag, input_1_imag) = tl.split(tl.reshape(input_head_imag, (BLOCK_SIZE, 2)))
    (input_2_real, input_2_imag) = tl.split(input_tail)
    (other_head_real, other_head_imag) = tl.split(tl.reshape(other_head, (BLOCK_SIZE * 2, 2)))
    (other_0_real, other_1_real) = tl.split(tl.reshape(other_head_real, (BLOCK_SIZE, 2)))
    (other_0_imag, other_1_imag) = tl.split(tl.reshape(other_head_imag, (BLOCK_SIZE, 2)))
    (other_2_real, other_2_imag) = tl.split(other_tail)
    out_0_real = input_1_real * other_2_real - input_1_imag * other_2_imag - input_2_real * other_1_real + input_2_imag * other_1_imag
    out_0_imag = input_1_real * other_2_imag + input_1_imag * other_2_real - input_2_real * other_1_imag - input_2_imag * other_1_real
    out_1_real = input_2_real * other_0_real - input_2_imag * other_0_imag - input_0_real * other_2_real + input_0_imag * other_2_imag
    out_1_imag = input_2_real * other_0_imag + input_2_imag * other_0_real - input_0_real * other_2_imag - input_0_imag * other_2_real
    out_2_real = input_0_real * other_1_real - input_0_imag * other_1_imag - input_1_real * other_0_real + input_1_imag * other_0_imag
    out_2_imag = input_0_real * other_1_imag + input_0_imag * other_1_real - input_1_real * other_0_imag - input_1_imag * other_0_real
    output_head = tl.where(head_columns[None, :] == 0, out_0_real[:, None], tl.where(head_columns[None, :] == 1, out_0_imag[:, None], tl.where(head_columns[None, :] == 2, out_1_real[:, None], out_1_imag[:, None])))
    output_tail = tl.where(tail_columns[None, :] == 0, out_2_real[:, None], out_2_imag[:, None])
    tl.store(output_ptr + head_offsets, output_head, mask=mask)
    tl.store(output_ptr + tail_offsets, output_tail, mask=mask)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (1344,)  workload x2:dim0 672->1344
#   规模  (2016,)  workload x3:dim0 672->2016
SHAPES = ((17,), (97,))
DTYPES = ('float32', 'float16', 'bfloat16')

def ref(args,meta):
 import numpy as np
 a=args["input_ptr"].reshape(-1,3,2);b=args["other_ptr"].reshape(-1,3,2);za=a[...,0]+1j*a[...,1];zb=b[...,0]+1j*b[...,1];z=np.cross(za,zb);return {"output_ptr":np.stack((z.real,z.imag),axis=-1).astype(np.float32).reshape(-1)}

def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=20260901):
 from case_utils import fast_rng
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 V=max(1,N//6);T=V*6;args={"input_ptr":np.asarray(rng.normal(0,.8,T)),"other_ptr":np.asarray(rng.normal(0,.8,T)),"output_ptr":np.asarray(np.full(T,-7.)),"num_vectors":V};meta={"BLOCK_SIZE":128};grid=((V+127)//128,)
 outputs=('output_ptr',);return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0001, "atol": 0.0001, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, _linalg_cross_complex_contiguous_kernel, DTYPES,
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
