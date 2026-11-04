"""complex_pack: 把交织的 (real, im) 对拆开,输出 plan 特征与复数平方。

模式: 一个 program 处理整个向量(N 是 constexpr):load 2N 个交织值,reshape 成
(N, 2) 后用 tl.split 拆出 real/im;一路 join(re+im, re-im) 再转置成平面布局,
另一路算复平方 (re^2-im^2, 2re*im) 再 interleave;最后 tl.cat 成 4N 长输出。

文件只有两层:
  ① complex_pack_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/complex_pack', "group": 'basic', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'creation.arange', 'memory.load', 'memory.store', 'shape.reshape', 'shape.split', 'shape.join', 'shape.interleave', 'shape.trans', 'shape.cat']}
COPIED_FROM = {'repo': '~/ops basic (authored composite, validated at d326fbc+)', 'covers_gap_apis': ['interleave']}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def complex_pack_kernel(X, Y, N: tl.constexpr):
    i=tl.arange(0,N)
    packed=tl.load(X+tl.arange(0,2*N)).to(tl.float32)
    re, im=tl.split(tl.reshape(packed,(N,2)))
    pair=tl.join(re+im,re-im)
    planar=tl.trans(pair)
    # Real/imaginary decomposition of pairwise complex squaring.
    real=re*re-im*im
    imag=2*re*im
    squared=tl.interleave(real,imag)
    features=tl.cat(tl.reshape(planar,(2*N,)),squared,can_reorder=False)
    tl.store(Y+tl.arange(0,4*N),features)

# ------------------------------------------------------------------ ② case 层
# 典型用法:复数特征工程(音频/雷达前端把 I/Q 交织数据展开成 [re+im, re-im] 和
# 复平方两段特征)。N 是 constexpr(signature 固定),向量长度按 N 取。
#
# (N,):
#   典型  (1024,)  一次处理 1024 个复数(2 KiB 输入 / 16 KiB 输出,fp32)
#   规模  (2048,)  典型规模 ×2:dim0 1024->2048
#   规模  (4096,)  典型规模 ×4:dim0 1024->4096
#   泛化  (16,)    小向量:split/join/interleave 都在一个 warp 内做完
#         (1,)     退化:单个复数
SHAPES = ((128,), (1,))
# kernel 内部先转 f32 再算,输出 dtype 可以是半精度;原始版本用 fp16/fp32。
DTYPES = ("float32", "float16", "bfloat16")
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}


def ref(args, meta):
    """numpy 对照:按 kernel 的两段布局逐段拼出 4N 输出。"""
    n = int(meta["N"])
    packed = np.asarray(args["X"]).astype(np.float64).reshape(n, 2)
    re, im = packed[:, 0], packed[:, 1]
    out = np.asarray(args["Y"])
    planar = np.stack([re + im, re - im], axis=0).reshape(2 * n)
    squared = np.stack([re * re - im * im, 2.0 * re * im], axis=1).reshape(2 * n)
    return {"Y": np.concatenate([planar, squared]).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n = int(shape[0])
    if n <= 0:
        raise ValueError(f"N must be positive, got {shape}")

    # 原始输入是零均值正态的 I/Q 采样,标准差约 1。取值落在 1/8 网格 [-8, 8),
    # 半精度精确可表示;re*re-im*im 等中间量最多到 64,仍在 fp16 的整数精度内。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (rng.integers(-64, 64, 2 * n, dtype=np.int16) / 8).astype(_HOST_DTYPE[dtype])
    # 语义边界:第一个复数 = 0(平方为 0、planar 两项相同),第二个是纯实数,
    # 第三个是纯虚数,保证 re/im 的角色不会互换。
    x[0] = 0.0
    if n > 1:
        x[2], x[3] = 0.0, 0.5
    if n > 2:
        x[4], x[5] = -0.5, 0.0

    args = {"X": x, "Y": np.zeros(4 * n, dtype=np_dtype_of(dtype))}
    meta = {"N": n}
    case = {"args": args, "meta": meta, "grid": (1,), "outputs": ("Y",),
            "expected": ref(args, meta)}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {"X": "bfloat16", "Y": "bfloat16"}
        case["comparison"] = {"Y": {"comparator": "allclose", "exact": False,
                                    "rtol": 5e-3, "atol": 5e-3, "equal_nan": True}}
    return case


def np_dtype_of(dtype):
    return np.float32 if dtype == "bfloat16" else np.dtype(dtype)


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, complex_pack_kernel, DTYPES,
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
