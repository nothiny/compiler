"""row_reduce_min_kernel: 每组对已分块求过的 partial min 再做一次组内归约。

模式: 每个 program 处理一行/一组,off = n*G + arange(BLOCK_SIZE),
tl.min(axis=0) 后写一个标量。无掩码,BLOCK_SIZE 必须等于 G。

文件只有两层:
  ① row_reduce_min_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/row_reduce_min_kernel', "group": 'basic', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'creation.arange', 'memory.load', 'memory.store', 'reduce.min']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "test", "row": 24169, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "551371d7a33836d2e0ea9109d3449f358973d212c20346c2f4b2fbed75a2adca"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def row_reduce_min_kernel(gmin_ptr, out_ptr, N, G, BLOCK_SIZE: tl.constexpr):
    n = tl.program_id(0)
    g_offsets = n * G + tl.arange(0, BLOCK_SIZE)
    data = tl.load(gmin_ptr + g_offsets)
    m = tl.min(data, axis=0)
    tl.store(out_ptr + n, m)

# ------------------------------------------------------------------ ② case 层
# 典型用法:分组归一化后的组内最小 partial 归约。原始 (1024, 8192) 输入分成
# num_groups=512 组 => 每行每组的 partial 数 G = 8192/512 = 16,grid = (N,)。
#
# (N, G):
#   典型  (1024, 512)  原始 batch 1024,行内 512 个组的 partial
#   规模  (2048, 512)  典型规模 ×2:dim0 1024->2048
#   规模  (1024, 1024)  典型规模 ×2:dim1 512->1024
#   泛化  (17, 128)    行数不是 2 的幂;BLOCK_SIZE 必须是 2 的幂(arange 的要求)
#         (1, 1)       退化:单值
SHAPES = ((128, 128), (17, 128), (1, 1))
# tl.min 只是比较+选择,半精度合法;原始 partial 缓冲区是 f32,排第一。
DTYPES = ("float32", "float16", "bfloat16")
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}


def ref(args, meta):
    """numpy 对照:按行取最小值。"""
    x = np.asarray(args["gmin_ptr"])
    return {"out_ptr": x.min(axis=1)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n, g = (int(v) for v in shape)
    if n <= 0 or g <= 0:
        raise ValueError(f"shape must be (N > 0, G > 0), got {shape}")

    # 原始 partial min 是归一化后数据的组内最小值,集中在 0 附近。用 1/16 网格上
    # 的正态值(标准差 2),fp16/bf16 都能精确表示。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (np.clip(np.rint(rng.standard_normal((n, g), dtype=np.float32) * 32),
                 -128, 127) / 16).astype(_HOST_DTYPE[dtype])
    # 语义边界:第 0 行整行相同(全是并列最小值);第 1 行的最小值放在最后一列。
    x[0, :] = 2.0
    if n > 1:
        x[1, :] = 0.0
        x[1, -1] = -8.0

    args = {"gmin_ptr": x, "out_ptr": np.zeros(n, dtype=x.dtype), "N": np.int32(n),
            "G": np.int32(g)}
    meta = {"BLOCK_SIZE": g}
    case = {"args": args, "meta": meta, "grid": (n,), "outputs": ("out_ptr",),
            "expected": ref(args, meta)}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {"gmin_ptr": "bfloat16"}
        case["comparison"] = {"out_ptr": {"comparator": "allclose", "exact": False,
                                          "rtol": 5e-3, "atol": 5e-3, "equal_nan": True}}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, row_reduce_min_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float32'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float32': 'float32', 'float16': 'float16', 'bfloat16': 'bfloat16'}


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
