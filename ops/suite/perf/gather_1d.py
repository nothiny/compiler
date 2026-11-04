"""gather_1d: 一维按索引收集 out[i] = x[idx[i]]。

模式: 带掩码的连续 load(索引数组 + 被收集数据两次 load),第二次 load 的下标是
从索引数组里读出来的(间接寻址),再带掩码 store。数据 dtype 与索引 dtype 分开。

文件只有两层:
  ① gather_1d_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/gather_1d', "group": 'basic', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'memory.load', 'memory.load.masked', 'memory.store', 'memory.indirect', 'creation.arange']}
COPIED_FROM = {'repo': '~/ops (basic)', 'note': 'base operator; semantic boundary cases merged into its case layer (no protected-dir constraint here)', 'validated': True}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def gather_1d_kernel(index_ptr, x_ptr, out_ptr, n_elements, BLOCK_SIZE: tl.constexpr):
    pid = tl.program_id(0)
    offsets = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    mask = offsets < n_elements
    idx = tl.load(index_ptr + offsets, mask=mask, other=0)
    vals = tl.load(x_ptr + idx, mask=mask, other=0.0)
    tl.store(out_ptr + offsets, vals, mask=mask)

# ------------------------------------------------------------------ ② case 层
# 典型用法:embedding / index_select 的行拷贝:一次从表里按索引取出 n_out 个元素。
# 常见的 1D 用法是对一条激活做置换(permutation)或按 token id 取表行。
# 索引必须落在 [0, n_src) 内,并且覆盖整个合法范围(含 0 和 n_src-1)。
#
# (n_out, n_src):
#   典型  (4096, 4096)  置换一条 4096 元素的特征向量(索引是 [0,n_src) 的排列)
#   规模  (8192, 4096)  典型规模 ×2:dim0 4096->8192
#   规模  (4096, 8192)  典型规模 ×2:dim1 4096->8192
#   泛化  (257, 1000)   n_out 不整除 BLOCK,尾部掩码;索引重复、未覆盖全表
#         (1, 1)       退化:单元素
SHAPES = ((128, 128), (97, 100), (1, 1))
# 原始 ops 版本用 int32 索引;数据侧给出推理/训练都常见的几种 dtype。
DTYPES = ('int8', 'int32', 'int64', 'bfloat16', 'float32', 'float16')
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}
INDEX_DTYPE = np.int32


def ref(args, meta):
    """numpy 对照:x[idx],整数数据同样适用。"""
    idx = np.asarray(args["index_ptr"])
    x = np.asarray(args["x_ptr"])
    out = np.asarray(args["out_ptr"])
    return {"out_ptr": x[idx].astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n_out, n_src = (int(v) for v in shape)
    if n_out <= 0 or n_src <= 0:
        raise ValueError(f"shape must be (n_out > 0, n_src > 0), got {shape}")
    np_dtype = np.dtype(_HOST_DTYPE.get(dtype, dtype))

    from case_utils import fast_rng
    rng = fast_rng(seed)
    # 索引覆盖整个合法范围:前 n_src 个位置是 [0, n_src) 的排列,其余随机,
    # 于是 0 和 n_src-1 一定出现,重复也一定出现。
    order = rng.permutation(n_src)
    if n_out <= n_src:
        idx = order[:n_out]
    else:
        idx = np.concatenate([order, rng.integers(0, n_src, n_out - n_src, dtype=INDEX_DTYPE)])
    # 语义边界:第一个位置取 0、最后一个位置取 n_src-1(表尾),中间允许重复。
    if n_out > 0:
        idx[0] = 0
    if n_out > 1:
        idx[-1] = n_src - 1

    if np_dtype.kind in "iu":
        x = rng.integers(-120, 121, n_src).astype(np_dtype)
    else:
        # 取值落在 1/16 网格上:bf16/fp16 精确可表示,收集不会引入误差。
        x = (rng.integers(-128, 128, n_src, dtype=np.int16) / 16).astype(np_dtype)

    args = {"index_ptr": idx.astype(INDEX_DTYPE), "x_ptr": x,
            "out_ptr": np.zeros(n_out, dtype=np_dtype), "n_elements": np.int32(n_out)}
    meta = {"BLOCK_SIZE": 256}
    case = {"args": args, "meta": meta, "grid": ((n_out + 255) // 256,),
            "outputs": ("out_ptr",), "expected": ref(args, meta)}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {"x_ptr": "bfloat16", "out_ptr": "bfloat16"}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;整数/拷移动子按位精确比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, gather_1d_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float32'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float32': 'float32', 'float16': 'float16', 'bfloat16': 'bfloat16', 'int8': 'int8', 'int32': 'int32', 'int64': 'int64'}


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
