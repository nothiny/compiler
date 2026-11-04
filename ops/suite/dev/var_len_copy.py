"""var_len_copy:变长数组段拷贝 —— 三层结构。

① var_len_copy_kernel   编译单元:@triton.jit,编译器只消费它的 AST。
② 执行单元:numpy in/out,零 torch。
③ SHAPES / DTYPES / make_case / ref  验证层:纯 numpy。
"""

OPERATOR = {"name": "hidden/var_len_copy", "group": "hidden", "channel": "G",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import numpy as np
import triton
import triton.language as tl
from case_utils import fast_rng


@triton.jit
def var_len_copy_kernel(old_a_start, old_a_len, old_a_location, new_a_start, new_a_location,
                        BLOCK_SIZE: tl.constexpr):
    a_id = tl.program_id(0)
    length = tl.load(old_a_len + a_id)
    old_start = tl.load(old_a_start + a_id)
    new_start = tl.load(new_a_start + a_id)
    off = tl.arange(0, BLOCK_SIZE)
    for i in range(0, length, BLOCK_SIZE):
        v = tl.load(old_a_location + old_start + i + off, mask=off < length)
        tl.store(new_a_location + new_start + i + off, v, mask=off < length)


DTYPES = ('float32', 'float16', 'bfloat16')
SHAPES = [(3,), (4,)]


def ref(args, meta):
    starts = np.asarray(args["old_a_start"], dtype=np.int64)
    lens = np.asarray(args["old_a_len"], dtype=np.int64)
    nstarts = np.asarray(args["new_a_start"], dtype=np.int64)
    old = np.asarray(args["old_a_location"], dtype=np.float32)
    out = np.array(args["new_a_location"], dtype=np.float32, copy=True)
    for i in range(len(starts)):
        out[nstarts[i]:nstarts[i] + lens[i]] = old[starts[i]:starts[i] + lens[i]]
    return {"new_a_location": out.astype(np.asarray(args["new_a_location"]).dtype)}


def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    num = int(shape[0])
    rng = fast_rng(seed)
    starts = rng.integers(0, 100, num).astype(np.int32)
    lens = rng.integers(10, 50, num).astype(np.int32)
    nstarts = np.concatenate([[0], np.cumsum(lens)[:-1]]).astype(np.int32)
    args = {"old_a_start": starts, "old_a_len": lens,
            "old_a_location": rng.standard_normal(512).astype(dtype),
            "new_a_start": nstarts,
            "new_a_location": np.zeros(int(lens.sum()), dtype=dtype)}
    meta = {"BLOCK_SIZE": 256}
    return {"args": args, "meta": meta, "grid": (num,),
            "outputs": ("new_a_location",), "expected": ref(args, meta)}


def var_len_copy(old_a_start, old_a_len, old_location, new_a_start, new_a_location):
    var_len_copy_kernel[(len(old_a_start),)](
        old_a_start, old_a_len, old_location, new_a_start, new_a_location, BLOCK_SIZE=256)
    return new_a_location


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, var_len_copy_kernel, DTYPES,
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
