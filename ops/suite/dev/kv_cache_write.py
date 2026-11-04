"""kv_cache_write:分页 KV cache 按 slot 写入 —— 三层结构。

① kv_cache_write_kernel   编译单元:@triton.jit,编译器只消费它的 AST。
② 执行单元:numpy in/out,零 torch。
③ SHAPES / DTYPES / make_case / ref  验证层:纯 numpy。
"""

OPERATOR = {"name": "hidden/kv_cache_write", "group": "hidden", "channel": "G",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["elementwise"]}
import numpy as np
import triton
import triton.language as tl
from case_utils import fast_rng


@triton.jit
def kv_cache_write_kernel(new_ptr, slot_ptr, cache_ptr, HDIM: tl.constexpr, BLOCK_SIZE: tl.constexpr):
    tok = tl.program_id(0)
    slot = tl.load(slot_ptr + tok)
    block = slot // BLOCK_SIZE
    offset = slot % BLOCK_SIZE
    offs = tl.arange(0, HDIM)
    v = tl.load(new_ptr + tok * HDIM + offs)
    tl.store(cache_ptr + (block * BLOCK_SIZE + offset) * HDIM + offs, v)


DTYPES = ('float32', 'float16', 'bfloat16')
SHAPES = ((6, 4, 2, 8), (12, 8, 4, 16), (3, 2, 1, 4))


def ref(args, meta):
    new = np.asarray(args["new_ptr"], dtype=np.float32)
    slot = np.asarray(args["slot_ptr"], dtype=np.int64)
    cache = np.array(args["cache_ptr"], dtype=np.float32, copy=True)
    bs = meta["BLOCK_SIZE"]
    for t in range(new.shape[0]):
        block = slot[t] // bs
        offset = slot[t] % bs
        cache[block, offset] = new[t]
    return {"cache_ptr": cache.astype(np.asarray(args["cache_ptr"]).dtype)}


def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    ntok, hdim, nb, bs = (int(x) for x in shape)
    rng = fast_rng(seed)
    slot = rng.permutation(nb * bs)[:ntok].astype(np.int32)
    args = {"new_ptr": rng.standard_normal((ntok, hdim)).astype(dtype),
            "slot_ptr": slot, "cache_ptr": np.zeros((nb, bs, hdim), dtype=dtype)}
    meta = {"HDIM": hdim, "BLOCK_SIZE": bs}
    return {"args": args, "meta": meta, "grid": (ntok,),
            "outputs": ("cache_ptr",), "expected": ref(args, meta)}


def kv_cache_write(new, slot, cache):
    kv_cache_write_kernel[(new.shape[0],)](new, slot, cache, HDIM=new.shape[1],
                                           BLOCK_SIZE=cache.shape[1])
    return cache


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, kv_cache_write_kernel, DTYPES,
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
