"""kldiv_ops: loss(reduction 类)。
bench 稳态配置见 bench/workload.json(声明 shape [4, 32],验证 shape [64, 1024]);正确性 shape 见下方 SHAPES。
模式: creation.arange、reduce.sum、memory.store、creation.where、memory.load.masked、math.log。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""

OPERATOR = {'name': 'bench/kldiv_ops', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'reduce.sum', 'memory.store', 'creation.where', 'memory.load.masked', 'math.log', 'math.maximum', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/kldiv_ops.py', 'sha256': '2202f60acd34a6f6169e06eea5296856e7d8518d345530ce82f5710ff4d1066c'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def kldiv_kernel(y_ptr, gt_ptr, loss_ptr, n_cols, BLOCK: tl.constexpr):
    row = tl.program_id(0)
    cols = tl.arange(0, BLOCK)
    mask = cols < n_cols
    y = tl.load(y_ptr + row * n_cols + cols, mask=mask, other=0.0).to(tl.float32)
    gt = tl.load(gt_ptr + row * n_cols + cols, mask=mask, other=0.0).to(tl.float32)
    loss = tl.sum(tl.where(mask, gt * (tl.log(tl.maximum(gt, 1e-12)) - y), 0.0), axis=0)
    tl.store(loss_ptr + row, loss)


# ------------------------------------------------------------------ ② case 层
DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((4, 32), (7, 35))

def ref(args, meta):
    y = np.asarray(args["y_ptr"], dtype=np.float64)
    gt = np.asarray(args["gt_ptr"], dtype=np.float64)
    loss = (gt * (np.log(np.maximum(gt, 1e-12)) - y)).sum(axis=1)
    return {"loss_ptr": loss.astype(np.asarray(args["loss_ptr"]).dtype)}

def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    r, c = (int(v) for v in shape)
    from case_utils import fast_rng
    rng = fast_rng(seed)
    gt = rng.random((r, c)) + 0.01
    gt /= gt.sum(axis=1, keepdims=True)
    prediction = rng.random((r, c)) + 0.01
    prediction /= prediction.sum(axis=1, keepdims=True)
    args = {"y_ptr": np.log(prediction).astype(dtype), "gt_ptr": gt.astype(dtype),
            "loss_ptr": np.zeros(r, dtype=dtype), "n_cols": np.int32(c)}
    meta = {"BLOCK": triton.next_power_of_2(c)}
    return {"args": args, "meta": meta, "grid": (r,),
            "outputs": ("loss_ptr",), "expected": ref(args, meta)}

def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, kldiv_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)

ORACLE_KIND = "numpy_reference"

INDEPENDENT_ORACLE = True

EXECUTION_KIND = "triton_kernel"

VERIFICATION_KIND = "correctness"

OPERATOR_NAME = "G/" + __file__.rsplit("/", 1)[-1]

OPERATOR_FILE = __file__


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
