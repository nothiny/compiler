"""_matmul_abt_kernel: C = A @ B^T,block pointer + 全 constexpr 形状。

模式: 1D grid(tile 展平),GROUP_M 分组后 pid_m/pid_n 解出;两个操作数都用
make_block_ptr(boundary_check 处理不足一块的边界,零填充),K 方向
tl.static_range(NUM_K_BLOCKS) 静态展开并 advance 指针,tl.dot 累积到 f32,
最后以 OUT_DTYPE 存回 C 的 block pointer。pid_m 越界时早退(分组会多算)。

文件只有两层:
  ① _matmul_abt_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'hard/matmul_abt_kernel', "group": 'hard', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'control.if_runtime', 'control.loop_constexpr', 'linalg.dot', 'linalg.dot.acc', 'memory.block_pointer', 'blockptr.advance', 'blockptr.make', 'memory.load.masked', 'memory.store.masked']}
SOURCE = {"dataset": "makora-ai/triton-gpu-latency", "split": "train", "row": 28840, "license": "Apache-2.0", "revision": "3b30911350fa433e1cb97ec2a41bd8908dd35d5d", "original_sha256": "4471cad1492365c7e71206e74945c76a25c6d26de0651fb44053b07e7f0eb599"}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def _matmul_abt_kernel(A_ptr, B_ptr, C_ptr, M: tl.constexpr, N: tl.constexpr, K: tl.constexpr, stride_am: tl.constexpr, stride_ak: tl.constexpr, stride_bn: tl.constexpr, stride_bk: tl.constexpr, stride_cm: tl.constexpr, stride_cn: tl.constexpr, OUT_DTYPE: tl.constexpr, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr, GROUP_M: tl.constexpr, NUM_K_BLOCKS: tl.constexpr):
    pid = tl.program_id(0)
    grid_m = tl.cdiv(M, BLOCK_M)
    grid_n = tl.cdiv(N, BLOCK_N)
    num_pid_in_group = GROUP_M * grid_n
    group_id = pid // num_pid_in_group
    first_pid_m = group_id * GROUP_M
    pid_in_group = pid - group_id * num_pid_in_group
    pid_m = first_pid_m + pid_in_group % GROUP_M
    pid_n = pid_in_group // GROUP_M
    if pid_m >= grid_m:
        return
    a_bp = tl.make_block_ptr(base=A_ptr, shape=(M, K), strides=(stride_am, stride_ak), offsets=(pid_m * BLOCK_M, 0), block_shape=(BLOCK_M, BLOCK_K), order=(1, 0))
    b_bp = tl.make_block_ptr(base=B_ptr, shape=(K, N), strides=(stride_bk, stride_bn), offsets=(0, pid_n * BLOCK_N), block_shape=(BLOCK_K, BLOCK_N), order=(0, 1))
    acc = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)
    for _ in tl.static_range(0, NUM_K_BLOCKS):
        a = tl.load(a_bp, boundary_check=(0, 1), padding_option='zero')
        b = tl.load(b_bp, boundary_check=(0, 1), padding_option='zero')
        acc = tl.dot(a, b, acc=acc)
        a_bp = tl.advance(a_bp, (0, BLOCK_K))
        b_bp = tl.advance(b_bp, (BLOCK_K, 0))
    c_bp = tl.make_block_ptr(base=C_ptr, shape=(M, N), strides=(stride_cm, stride_cn), offsets=(pid_m * BLOCK_M, pid_n * BLOCK_N), block_shape=(BLOCK_M, BLOCK_N), order=(1, 0))
    tl.store(c_bp, acc.to(OUT_DTYPE), boundary_check=(0, 1))

# ------------------------------------------------------------------ ② case 层
# 典型用法:attention/Linear 里"权重以 (N, K) 存放"的 GEMM(所以是 A@B^T)。
# 原始程序是 A(1024xK) 与 W(NxK) 的乘;这里取 M=256、N=512、K=2048。
#
# (M, N, K):
#   典型  (256, 512, 2048)  K >> M、N,三者都整除 BLOCK
#   规模  (512, 512, 2048)  典型规模 ×2:dim0 256->512
#   规模  (768, 512, 2048)  典型规模 ×3:dim0 256->768
#   泛化  (40, 24, 100)     都不整除 BOOT/block:boundary_check 与 pid_m 早退都走到
#         (16, 16, 16)      退化:单 tile
SHAPES = ((128, 96, 100), (40, 24, 100))
# dot 用例含 fp16/bf16;OUT_DTYPE 跟随输入 dtype。
DTYPES = ("float16", "bfloat16", "float32")
_HOST_DTYPE = {"float32": np.float32, "float16": np.float16, "bfloat16": np.float32}
BLOCK_M, BLOCK_N, BLOCK_K, GROUP_M = 32, 32, 32, 4


def _tl_kind(dtype):
    import triton.language as tl
    return {"float32": tl.float32, "float16": tl.float16, "bfloat16": tl.bfloat16}[dtype]


def ref(args, meta):
    """numpy 对照:float64 的 A @ B^T(B 以 (N, K) 存放)。"""
    m, n, k = int(meta["M"]), int(meta["N"]), int(meta["K"])
    a = np.asarray(args["A_ptr"], dtype=np.float64).reshape(m, k)
    b = np.asarray(args["B_ptr"], dtype=np.float64).reshape(n, k)
    out = np.asarray(args["C_ptr"])
    return {"C_ptr": (a @ b.T).reshape(-1).astype(out.dtype)}


def _make_case(shape=SHAPES[0], dtype="float16", seed=0):
    m, n, k = (int(v) for v in shape)
    if min(m, n, k) < 16:
        raise ValueError(f"shape must be >= 16 on all dims, got {shape}")
    host = _HOST_DTYPE[dtype]

    from case_utils import fast_rng
    rng = fast_rng(seed)
    a = (rng.integers(-16, 16, (m, k), dtype=np.int16) / 16).astype(host)
    b = (rng.integers(-16, 16, (n, k), dtype=np.int16) / 16).astype(host)
    # 语义边界:第 0 行 A 全 0;B 的第 0 行全 1(输出第 0 列等于 A 的行和)。
    a[0, :] = 0.0
    b[0, :] = 1.0

    out_dtype = np.float32 if dtype == "bfloat16" else np.dtype(dtype)
    args = {"A_ptr": a.reshape(-1), "B_ptr": b.reshape(-1),
            "C_ptr": np.zeros((m, n), dtype=out_dtype)}
    meta = {"M": m, "N": n, "K": k, "stride_am": k, "stride_ak": 1,
            "stride_bn": k, "stride_bk": 1, "stride_cm": n, "stride_cn": 1,
            "OUT_DTYPE": _tl_kind(dtype), "BLOCK_M": BLOCK_M, "BLOCK_N": BLOCK_N,
            "BLOCK_K": BLOCK_K, "GROUP_M": GROUP_M,
            "NUM_K_BLOCKS": (k + BLOCK_K - 1) // BLOCK_K}
    grid = (((m + BLOCK_M - 1) // BLOCK_M) * ((n + BLOCK_N - 1) // BLOCK_N),)
    case = {"args": args, "meta": meta, "grid": grid, "outputs": ("C_ptr",),
            "expected": ref(args, meta)}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {"A_ptr": "bfloat16", "B_ptr": "bfloat16",
                                  "C_ptr": "bfloat16"}
    case["comparison"] = {"C_ptr": {"comparator": "allclose", "exact": False,
                                    "rtol": 5e-3, "atol": 5e-3, "equal_nan": True}}
    return case


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;浮点输出按容差比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, _matmul_abt_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float32'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float16': 'float16', 'bfloat16': 'bfloat16', 'float32': 'float32'}


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
