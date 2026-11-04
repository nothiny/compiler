"""fast_ce_loss: loss(reduction 类)。
bench 稳态配置见 bench/workload.json(声明 shape [4, 32],验证 shape [64, 1024]);正确性 shape 见下方 SHAPES。
模式: creation.arange、memory.load、reduce.max、memory.store、math.log、memory.load.masked。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""

OPERATOR = {'name': 'bench/fast_ce_loss', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['creation.arange', 'memory.load', 'reduce.max', 'memory.store', 'math.log', 'memory.load.masked', 'reduce.sum', 'math.exp']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/fast_ce_loss.py', 'sha256': '7911068f573be46d90c65fb4af190e4827ccb601db30db26169fbde2710a6714'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def cross_entropy_forward_kernel(
    logits_ptr, logits_row_stride,
    loss_ptr,
    logsumexp_ptr,
    labels_ptr,
    VOCAB_SIZE: tl.constexpr,
    BLOCK_SIZE: tl.constexpr,
    DO_SOFTCAPPING: tl.constexpr,
    SOFTCAP: tl.constexpr,
    DO_LOGIT_SCALING: tl.constexpr,
    LOGIT_SCALE: tl.constexpr,
):
    row_idx = tl.program_id(0)
    logits_ptr += row_idx * logits_row_stride
    loss_ptr += row_idx
    logsumexp_ptr += row_idx
    labels_ptr += row_idx

    col_offsets = tl.arange(0, BLOCK_SIZE)
    mask = col_offsets < VOCAB_SIZE

    label_idx = tl.load(labels_ptr)
    logits = tl.load(logits_ptr + col_offsets, mask=mask, other=float("-inf")).to(tl.float32)

    if DO_LOGIT_SCALING:
        logits = LOGIT_SCALE * logits
    if DO_SOFTCAPPING:
        logits = SOFTCAP * (2.0 * tl.sigmoid(2.0 * (logits / SOFTCAP)) - 1.0)

    c = tl.max(logits, 0)
    logsumexp = c + tl.log(tl.sum(tl.exp(logits - c), 0))

    if label_idx != -100:
        x = tl.load(logits_ptr + label_idx).to(tl.float32)
        if DO_LOGIT_SCALING:
            x = LOGIT_SCALE * x
        if DO_SOFTCAPPING:
            x = SOFTCAP * (2.0 * tl.sigmoid(2.0 * (x / SOFTCAP)) - 1.0)
        loss = logsumexp - x
    else:
        loss = 0.0
    tl.store(logsumexp_ptr, logsumexp)
    tl.store(loss_ptr, loss)


# ------------------------------------------------------------------ ② case 层
DTYPES = ('bfloat16', 'float32', 'float16')

SHAPES = ((4, 32), (7, 35))

def ref(args, meta):
    logits = np.asarray(args["logits_ptr"], dtype=np.float64)
    labels = np.asarray(args["labels_ptr"], dtype=np.int64)
    n_rows, vocab = logits.shape
    c = logits.max(axis=1, keepdims=True)
    lse = c[:, 0] + np.log(np.exp(logits - c).sum(axis=1))
    rows = np.arange(n_rows)
    valid = labels != -100
    picked = logits[rows, np.clip(labels, 0, vocab - 1)]
    loss = np.where(valid, lse - np.where(valid, picked, 0.0), 0.0)
    return {"loss_ptr": loss.astype(np.asarray(args["loss_ptr"]).dtype),
            "logsumexp_ptr": lse.astype(np.asarray(args["logsumexp_ptr"]).dtype)}

def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    shape = tuple(int(value) for value in shape)
    n_rows, vocab = shape
    from case_utils import fast_rng
    rng = fast_rng(seed)
    logits = (rng.standard_normal((n_rows, vocab)) * 0.5).astype(dtype)
    labels = rng.integers(0, vocab, n_rows).astype(np.int32)
    args = {"logits_ptr": logits, "logits_row_stride": np.int32(vocab),
            "loss_ptr": np.zeros(n_rows, dtype=dtype),
            "logsumexp_ptr": np.zeros(n_rows, dtype=dtype),
            "labels_ptr": labels}
    meta = {"VOCAB_SIZE": vocab, "BLOCK_SIZE": triton.next_power_of_2(vocab),
            "DO_SOFTCAPPING": False, "SOFTCAP": 1.0,
            "DO_LOGIT_SCALING": False, "LOGIT_SCALE": 1.0}
    return {"args": args, "meta": meta, "grid": (n_rows,),
            "outputs": ("loss_ptr", "logsumexp_ptr"), "expected": ref(args, meta)}

def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, cross_entropy_forward_kernel, DTYPES,
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
