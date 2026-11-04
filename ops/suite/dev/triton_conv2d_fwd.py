"""triton_conv2d_fwd:2D 卷积 forward —— 三层结构。

① conv2d_fwd_kernel   编译单元:@triton.jit,编译器只消费它的 AST。
② 执行单元:numpy in/out,零 torch。
③ SHAPES / DTYPES / make_case / ref  验证层:纯 numpy。
"""

OPERATOR = {"name": "hidden/triton_conv2d_fwd", "group": "hidden", "channel": "G",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["conv_pool"]}
import numpy as np
import triton
import triton.language as tl
from case_utils import fast_rng


@triton.jit
def conv2d_fwd_kernel(x_ptr, w_ptr, y_ptr, N, C, H, W, O, OH, OW,
                      KH: tl.constexpr, KW: tl.constexpr, SH: tl.constexpr, SW: tl.constexpr,
                      PH: tl.constexpr, PW: tl.constexpr):
    idx = tl.program_id(0)
    ow = idx % OW
    t = idx // OW
    oh = t % OH
    t = t // OH
    o = t % O
    n = t // O
    acc = 0.0
    for c in range(0, C):
        for i in range(0, KH):
            for j in range(0, KW):
                ih = oh * SH - PH + i
                iw = ow * SW - PW + j
                ok = (ih >= 0) & (ih < H) & (iw >= 0) & (iw < W)
                xv = tl.load(x_ptr + ((n * C + c) * H + ih) * W + iw, mask=ok, other=0.0)
                wv = tl.load(w_ptr + ((o * C + c) * KH + i) * KW + j)
                acc = acc + xv * wv
    tl.store(y_ptr + ((n * O + o) * OH + oh) * OW + ow, acc)


DTYPES = ('float32', 'float16', 'bfloat16')
SHAPES = [(1, 2, 6, 6), (2, 2, 8, 8)]


def ref(args, meta):
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    w = np.asarray(args["w_ptr"], dtype=np.float64)
    kh, kw = meta["KH"], meta["KW"]
    sh, sw = meta["SH"], meta["SW"]
    ph, pw = meta["PH"], meta["PW"]
    n, c, h, wd = x.shape
    o, _, _, _ = w.shape
    oh = (h + 2 * ph - kh) // sh + 1
    owd = (wd + 2 * pw - kw) // sw + 1
    y = np.zeros((n, o, oh, owd))
    for nn in range(n):
        for oo in range(o):
            for i in range(oh):
                for j in range(owd):
                    acc = 0.0
                    for cc in range(c):
                        for ki in range(kh):
                            for kj in range(kw):
                                ih = i * sh - ph + ki
                                iw = j * sw - pw + kj
                                if 0 <= ih < h and 0 <= iw < wd:
                                    acc += x[nn, cc, ih, iw] * w[oo, cc, ki, kj]
                    y[nn, oo, i, j] = acc
    return {"y_ptr": y.astype(np.asarray(args["y_ptr"]).dtype)}


def _make_case(shape=SHAPES[0], *, dtype="float32", seed=30):
    dtype = np.dtype(dtype)
    if dtype.name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype.name}; choose from {DTYPES}")
    n, c, h, wd = (int(v) for v in shape)
    o, kh, kw = 3, 3, 3
    sh, sw, ph, pw = 1, 1, 1, 1
    rng = fast_rng(seed)
    x = rng.standard_normal((n, c, h, wd)).astype(dtype)
    w = rng.standard_normal((o, c, kh, kw)).astype(dtype)
    oh = (h + 2 * ph - kh) // sh + 1
    owd = (wd + 2 * pw - kw) // sw + 1
    args = {"x_ptr": x, "w_ptr": w, "y_ptr": np.zeros((n, o, oh, owd), dtype=dtype),
            "N": np.int32(n), "C": np.int32(c), "H": np.int32(h), "W": np.int32(wd),
            "O": np.int32(o), "OH": np.int32(oh), "OW": np.int32(owd)}
    meta = {"KH": kh, "KW": kw, "SH": sh, "SW": sw, "PH": ph, "PW": pw}
    return {"args": args, "meta": meta, "grid": (n * o * oh * owd,),
            "outputs": ("y_ptr",), "expected": ref(args, meta)}


def conv2d_fwd(x, weight):
    from case_utils import empty

    xf = np.asarray(x, dtype=np.float32)
    n, c, h, wd = xf.shape
    o, _, kh, kw = np.asarray(weight).shape
    oh = (h + 2 - kh) + 1
    owd = (wd + 2 - kw) + 1
    y = empty((n, o, oh, owd), like=x)
    conv2d_fwd_kernel[(n * o * oh * owd,)](xf, weight, y, n, c, h, wd, o, oh, owd,
                                           KH=kh, KW=kw, SH=1, SW=1, PH=1, PW=1)
    return y


def make_case(shape=None, dtype=None, seed=None):
    from case_utils import public_make_case

    return public_make_case(_make_case, conv2d_fwd_kernel, DTYPES,
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
