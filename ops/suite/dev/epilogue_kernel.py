"""epilogue_kernel: GEMM 之后的融合 epilogue —— bias 广播、缩放、hardtanh、GELU。

模式: 一维连续访存(n_elements = rows*n_cols),bias 用 offs % n_cols 按列广播,
再逐元素 y = clamp((x+b)*scale, ht_min, ht_max),最后 GELU(erf 形式)。
load/store 都没有掩码,所以元素数必须整除 BLOCK_SIZE。

文件只有两层:
  ① epilogue_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/epilogue_kernel', "group": 'basic', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'creation.arange', 'math.erf', 'math.maximum', 'math.minimum', 'memory.load', 'memory.store']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "test", "row": 19040, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "0a8250b6d85139ff722720d5e563d8620688e4e6e914221ba15884a792c3da60"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def epilogue_kernel(out_ptr, bias_ptr, n_elements, n_cols, scale, ht_min, ht_max, BLOCK_SIZE: tl.constexpr):
    offs = tl.program_id(0) * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
    x = tl.load(out_ptr + offs)
    b = tl.load(bias_ptr + offs % n_cols)
    y = (x + b) * scale
    y = tl.minimum(tl.maximum(y, ht_min), ht_max)
    inv_sqrt2 = 0.7071067811865476
    y = 0.5 * y * (1.0 + tl.erf(y * inv_sqrt2))
    tl.store(out_ptr + offs, y)

# ------------------------------------------------------------------ ② case 层
# 典型用法:nn.Linear(in=8192, out=8192) 之后的 epilogue。原始 (2048, 8192) fp32:
# scale=0.5、hardtanh [-2, 2],bias 按 out_features 广播。kernel 无掩码,
# 所以 rows*cols 必须整除 BLOCK_SIZE。
#
# (rows, cols):
#   典型  (64, 8192)   原始 (2048, 8192):保留 out_features=8192,batch 缩到 64
#   规模  (128, 8192)  典型规模 ×2:dim0 64->128
#   规模  (64, 16384)  典型规模 ×2:dim1 8192->16384
#   泛化  (16, 1024)   小 GEMM 的 epilogue,整除 BLOCK_SIZE=1024
#         (1, 4096)   单行:偏置广播退化成整行一个窗口
SHAPES = ((64, 128), (128, 128))
# tl.erf 在本机 Triton 上只接受 fp32,epilogue 又紧跟 f32 累加的 GEMM,
# 所以合法域只有 fp32。
DTYPES = ('float32', 'float16', 'bfloat16')
SCALE = 0.5              # 原始 scaling_factor
HT_MIN, HT_MAX = -2.0, 2.0   # 原始 hardtanh 边界


def ref(args, meta):
    """numpy 对照:float64 复现 bias 广播、缩放、hardtanh 与 GELU(erf 形式)。"""
    from mathref import erf          # 向量化 erf,避免逐元素 loop

    x = np.asarray(args["out_ptr"], dtype=np.float64)
    b = np.asarray(args["bias_ptr"], dtype=np.float64)
    ncols = int(args["n_cols"])
    rows = x.size // ncols
    y = (x.reshape(rows, ncols) + b[None, :]) * np.float64(args["scale"])
    y = np.minimum(np.maximum(y, np.float64(args["ht_min"])), np.float64(args["ht_max"]))
    y = 0.5 * y * (1.0 + erf(y / np.sqrt(2.0)))
    return {"out_ptr": y.reshape(-1).astype(np.asarray(args["out_ptr"]).dtype)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    rows, cols = (int(v) for v in shape)
    n = rows * cols
    if n % 1024:
        raise ValueError(f"rows*cols must be divisible by BLOCK_SIZE=1024, got {shape}")

    # GEMM 输出是 ~N(0, sqrt(in_features)) 的和:用标准差 4 的正态值,乘 scale=0.5
    # 后大量落在 hardtanh 的 [-2,2] 之外,夹取分支被覆盖。取值落在 1/16 网格上。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (np.clip(np.rint(rng.standard_normal(n, dtype=np.float32) * 64), -1024, 1023)
         / 16).astype(np.float32)
    bias = (rng.integers(-64, 65, cols, dtype=np.int32) / 16).astype(np.float32)
    # 语义边界:第 0 行 y 恰好等于硬夹取边界、第 1 行全负(走 GELU 的负饱和),
    # 第 2 行的 bias 让 y 落在 0 附近(GELU 的拐点)。
    x[:cols] = 4.0                       # (4+0)*0.5 = 2 = HT_MAX
    bias[0] = 0.0
    if rows > 1:
        x[cols:2 * cols] = -8.0
    if rows > 2:
        x[2 * cols:3 * cols] = 0.0

    args = {"out_ptr": x, "bias_ptr": bias, "n_elements": np.int32(n),
            "n_cols": np.int32(cols), "scale": np.float32(SCALE),
            "ht_min": np.float32(HT_MIN), "ht_max": np.float32(HT_MAX)}
    # out_ptr 是原地更新的输入输出缓冲区:expected 用同一份 host 值算。
    meta = {"BLOCK_SIZE": min(1024, n)}
    return {"args": args, "meta": meta, "grid": (n // min(1024, n),),
            "outputs": ("out_ptr",), "oracle_args": {"out_ptr": x.copy()},
            "expected": ref({**args, "out_ptr": x.copy()}, meta)}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, epilogue_kernel, DTYPES,
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
