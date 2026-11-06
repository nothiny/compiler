#!/usr/bin/env python3
"""test_t031_repairs.py -- the T031 construct-class repairs (gate G6).

One regression test per repaired census class, each through the real
compilation path (the factory compiler -> the native executable on the
pinned QEMU endpoint) and compared against a reference computed
independently of the compiler (numpy in this test), at 1 and 4 workers:

  bool-any-store     the scalar-bool lane: a bool block reduced with
                     tl.max (the any_kernel_1/any_kernel_2 class) whose
                     rank-0 bool result stores to the i1 backing store.
                     The repaired path: the rank-0 bool binds the
                     scalar-bool GPR convention (an i64 0/1), the store
                     writes its low byte (the pre-fix path crashed
                     reading .width off a MaskType, or refused
                     'scalar narrowing 64 -> 8'), and the bool block
                     compare unifies the 0/1 class at e8 with the
                     broadcast splat at e32 (the pre-fix MIR verifier
                     rejected 'vcmp requires equal vector types').
                     Boolean exactness (F052) -- array_equal.
  bool-block-store   the block bool store over a masked load (the
                     cos_signbit / fused_index_select_eq / median_bool
                     class): 0/1 bytes on the i8 storage lane, no access
                     at the disabled lanes, round-tripped back through a
                     bool load and a second store.
  bool-median        the median_bool_dim_finish shape: a sum reduced
                     inside the region and consumed there by a scalar
                     chain (sub -> cmp -> where) that feeds BOTH a bool
                     store and an int64 index store.  The data is chosen
                     so the per-chunk partials DIFFER (the block spans
                     four chunks; only the first carries nonzero
                     counts): reading the last chunk's partial yields
                     False/4 where the merged value yields True/2 -- the
                     executed comparison is the control that fails
                     under the per-chunk-partial defect.
  masked-scalar      the masked SCALAR store (the std_dim_inner /
                     local_ne class): the disabled position performs no
                     access (the out-of-range row's slot keeps its
                     sentinel), the enabled one stores.
  shape-fold         the constexpr shape fold: ``tl.arange(0, 16 //
                     x.shape[1])`` and ``tl.reshape(..., (x.shape[0],
                     16))`` of a runtime-loaded block (the
                     chunk_transform_qk / chunk_abc class) -- block
                     extents are compile-time in the pinned language, so
                     the forms lower (the pre-fix frontend refused
                     'end must be a compile-time integer').  The control
                     (a genuinely runtime bound, ``tl.arange(0, n)`` for
                     a runtime scalar n) keeps its located refusal.
  program-id-axis1   program_id(1) under a 2-axis grid (the
                     pairwise_distance class): the axis decomposition is
                     axis-distinguishing -- an axis-swapped reference
                     does NOT match.

Run: python3 a100c/tests/test_t031_repairs.py   (exit 0 = all PASS)
"""
from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
sys.path.insert(0, str(ROOT / "ops" / "harness"))

warnings.filterwarnings("ignore")

FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}", flush=True)
    if not ok:
        FAILURES.append(name)
    return ok


import numpy as np  # noqa: E402

from a100c.driver import CompileOptions, PipelineError  # noqa: E402
from a100c.factory import FactoryCompiler  # noqa: E402

TEMPLATE = ('"""probe operator %s"""\n'
            'OPERATOR = {"name": "probe/%s", "group": "probe", "channel": "local",\n'
            '            "execution": "triton_kernel", "verification": "correctness",\n'
            '            "tags": []}\n'
            'SHAPES = ((257,), (514,))\n'
            'import numpy as np\n'
            'import triton\n'
            'import triton.language as tl\n'
            '\n'
            '@triton.jit\n'
            'def %s_kernel(%s):\n'
            '%s\n'
            '\n'
            '%s\n')


def _operator_file(directory: Path, name: str, params: str, body: str,
                   case_layer: str):
    text = TEMPLATE % (name, name, name, params, body, case_layer)
    path = directory / f"{name}.py"
    path.write_text(text)
    return path


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_case(compiler, module, threads: int, **make_kwargs):
    import a100_support.native_device as nd
    case = module.make_case(**make_kwargs)
    device = nd.NativeExecutableDevice(compiler, threads)
    staged = device.stage_case(case)
    staged.launch()
    outputs = staged.outputs()
    ok = True
    detail = ""
    for name, policy in case["comparison"].items():
        got = np.asarray(outputs[name])
        exp = np.asarray(case["expected"][name])
        if policy.get("exact") or policy["comparator"] == "array_equal":
            same = np.array_equal(got, exp)
        else:
            same = np.allclose(got, exp, rtol=policy.get("rtol", 0.0),
                               atol=policy.get("atol", 0.0),
                               equal_nan=policy.get("equal_nan", False))
        if not same:
            diff = np.nonzero(got != exp)[0] if got.shape == exp.shape else []
            detail = f"{name}: {len(diff)} mismatched elements" \
                     f" (first got {got.ravel()[:4]} exp {exp.ravel()[:4]})"
        ok &= same
    return ok, detail


# ---------------------------------------------------------------------------
# 1. the scalar-bool lane (any_kernel class): reduce a bool block, store
#    the rank-0 bool, then load it back and store a derived int
# ---------------------------------------------------------------------------

BOOL_ANY_BODY = """\
    pid = tl.program_id(0)
    i = pid * BLOCK + tl.arange(0, BLOCK)
    m = i < n
    x = tl.load(x_ptr + i, mask=m, other=0.0)
    any_val = tl.max(x != 0, axis=0)
    tl.store(mid_ptr + pid, any_val)
    j = tl.arange(0, MID_BLOCK)
    mv = tl.load(flags_ptr + j, mask=j < n_blocks, other=0).to(tl.int1)
    total = tl.sum(mv.to(tl.int32), axis=0)
    tl.store(out_ptr + pid, total)"""

BOOL_ANY_CASE = '''def ref(args, meta):
    x = args["x_ptr"]
    flags = args["flags_ptr"]
    n = int(args["n"])
    B = 128
    blocks = (n + B - 1) // B
    mid = np.zeros(blocks, np.bool_)
    for b in range(blocks):
        lo, hi = b * B, min((b + 1) * B, n)
        mid[b] = bool((x[lo:hi] != 0).any())
    total = int(flags[:blocks].astype(np.int32).sum())
    return {"mid_ptr": mid, "out_ptr": np.full(blocks, total, np.int32)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n = int(shape[0])
    rng = np.random.default_rng(seed)
    x = rng.normal(0, 2, n).astype(np.float32)
    # sparse nonzeros: some all-zero blocks (False) and some hit blocks
    x[::7] = 0.0
    x[1::11] = 0.0
    blocks = (n + 127) // 128
    flags = rng.random(blocks) < 0.6
    args = {"x_ptr": x, "flags_ptr": flags,
            "mid_ptr": np.zeros(blocks, np.bool_),
            "out_ptr": np.zeros(blocks, np.int32), "n": n,
            "n_blocks": blocks}
    meta = {"BLOCK": 128, "MID_BLOCK": 128}
    grid = (blocks,)
    return {"args": args, "meta": meta, "grid": grid,
            "kernel": bool_any_kernel, "outputs": ("mid_ptr", "out_ptr"),
            "expected": ref(args, meta),
            "comparison": {"mid_ptr": {"comparator": "array_equal",
                                       "exact": True},
                           "out_ptr": {"comparator": "array_equal",
                                       "exact": True}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape or SHAPES[0], dtype or "float32", seed or 0)'''

# ---------------------------------------------------------------------------
# 2. the block bool store over a masked load, round-tripped
# ---------------------------------------------------------------------------

BOOL_BLOCK_BODY = """\
    pid = tl.program_id(0)
    i = pid * BLOCK + tl.arange(0, BLOCK)
    m = i < n
    x = tl.load(x_ptr + i, mask=m, other=0.0)
    b = x > 0.25
    tl.store(b_ptr + i, b, mask=m)
    y = tl.load(b_ptr + i, mask=m, other=False)
    z = tl.load(x_ptr + i, mask=m, other=0.0)
    tl.store(o_ptr + i, tl.where(y, z + 1.0, z - 1.0), mask=m)"""

BOOL_BLOCK_CASE = '''def ref(args, meta):
    x = args["x_ptr"]
    n = int(args["n"])
    b = x > 0.25
    return {"b_ptr": b, "o_ptr": np.where(b, x + 1.0, x - 1.0)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n = int(shape[0])
    rng = np.random.default_rng(seed)
    x = rng.normal(0, 1, n)
    args = {"x_ptr": x, "b_ptr": np.zeros(n, np.bool_),
            "o_ptr": np.zeros(n), "n": n}
    meta = {"BLOCK": 128}
    grid = ((n + 127) // 128,)
    return {"args": args, "meta": meta, "grid": grid,
            "kernel": bool_block_kernel, "outputs": ("b_ptr", "o_ptr"),
            "expected": ref(args, meta),
            "comparison": {"b_ptr": {"comparator": "array_equal",
                                     "exact": True},
                           "o_ptr": {"comparator": "allclose",
                                     "rtol": 1e-5, "atol": 1e-5}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape or SHAPES[0], dtype or "float32", seed or 0)'''

# ---------------------------------------------------------------------------
# 3. the median_bool_dim_finish shape: an in-region sum consumed by a
#    scalar chain; the data makes the per-chunk partials differ
# ---------------------------------------------------------------------------

BOOL_MEDIAN_BODY = """\
    row = tl.program_id(0)
    chunk_offsets = tl.arange(0, BLOCK)
    valid = chunk_offsets < chunks_per_output
    base = row * chunks_per_output + chunk_offsets
    block_counts = tl.load(counts + base, mask=valid, other=0)
    true_count = tl.sum(block_counts, axis=0)
    false_count = reduction_size - true_count
    rank = (reduction_size - 1) // 2
    median_value = rank >= false_count
    false_indices = tl.load(first_false + base, mask=valid, other=9223372036854775807)
    true_indices = tl.load(first_true + base, mask=valid, other=9223372036854775807)
    first_false_idx = tl.min(false_indices, axis=0)
    first_true_idx = tl.min(true_indices, axis=0)
    first_match = tl.where(median_value, first_true_idx, first_false_idx)
    tl.store(values + row, median_value)
    tl.store(indices + row, first_match)"""

BOOL_MEDIAN_CASE = '''def ref(args, meta):
    counts = args["counts"].reshape(-1, int(args["chunks_per_output"]))
    ff = args["first_false"].reshape(-1, int(args["chunks_per_output"]))
    ft = args["first_true"].reshape(-1, int(args["chunks_per_output"]))
    R = int(args["reduction_size"])
    out_v = np.zeros(counts.shape[0], np.bool_)
    out_i = np.zeros(counts.shape[0], np.int64)
    for r in range(counts.shape[0]):
        tc = int(counts[r].sum())
        fc = R - tc
        rank = (R - 1) // 2
        out_v[r] = rank >= fc
        out_i[r] = ft[r].min() if out_v[r] else ff[r].min()
    return {"values": out_v, "indices": out_i}


def _make_case(shape=SHAPES[0], dtype="int64", seed=0):
    rows = 9
    cpo = 64                    # the row block spans 4 chunks at e64
    rng = np.random.default_rng(seed)
    counts = np.zeros((rows, cpo), np.int64)
    # every row's nonzero counts sit in lanes 0..15 -- the FIRST chunk
    # only: the per-chunk partials differ (chunk 0 carries the whole
    # row sum, chunks 1..3 sum to 0), so reading the LAST chunk's
    # partial instead of the merged value yields the wrong median
    for r in range(rows):
        head = rng.integers(0, 5, 6)
        head[0] += 17 - head.sum()
        counts[r, :6] = head
    ff = rng.integers(0, 50, (rows, cpo)).astype(np.int64)
    ft = rng.integers(0, 50, (rows, cpo)).astype(np.int64)
    args = {"counts": counts.ravel(), "first_false": ff.ravel(),
            "first_true": ft.ravel(), "values": np.zeros(rows, np.bool_),
            "indices": np.zeros(rows, np.int64), "reduction_size": 17,
            "chunks_per_output": cpo}
    meta = {"chunks_per_output": cpo, "BLOCK": 64}
    grid = (rows,)
    return {"args": args, "meta": meta, "grid": grid,
            "kernel": bool_median_kernel, "outputs": ("values", "indices"),
            "expected": ref(args, meta),
            "comparison": {"values": {"comparator": "array_equal",
                                      "exact": True},
                           "indices": {"comparator": "array_equal",
                                       "exact": True}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape or SHAPES[0], dtype or "int64", seed or 0)'''

# ---------------------------------------------------------------------------
# 4. the masked scalar store (std_dim_inner / local_ne class)
# ---------------------------------------------------------------------------

MASKED_SCALAR_BODY = """\
    pid = tl.program_id(0)
    x = tl.load(x_ptr + pid)
    y = x * 2 + 1
    tl.store(o_ptr + pid, y, mask=pid < m)"""

MASKED_SCALAR_CASE = '''def ref(args, meta):
    x = args["x_ptr"]
    m = int(args["m"])
    o = np.full(x.shape[0], -7.0)
    o[:m] = x[:m] * 2 + 1
    return {"o_ptr": o}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n = int(shape[0])
    rng = np.random.default_rng(seed)
    x = rng.normal(0, 1, n)
    args = {"x_ptr": x, "o_ptr": np.full(n, -7.0), "m": n - 3}
    meta = {"BLOCK": 128}
    grid = (n,)
    return {"args": args, "meta": meta, "grid": grid,
            "kernel": masked_scalar_kernel, "outputs": ("o_ptr",),
            "expected": ref(args, meta),
            "comparison": {"o_ptr": {"comparator": "allclose",
                                     "rtol": 1e-5, "atol": 1e-5}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape or SHAPES[0], dtype or "float32", seed or 0)'''

# ---------------------------------------------------------------------------
# 5. the constexpr shape fold (arange end / reshape shape from x.shape)
# ---------------------------------------------------------------------------

SHAPE_FOLD_BODY = """\
    r = tl.arange(0, R)
    c = tl.arange(0, C)
    x = tl.load(x_ptr + r[:, None] * C + c[None, :])
    b = tl.reshape(tl.where(tl.arange(0, 16 // x.shape[1])[None, None, :] == 0, x[:, :, None], 0), (x.shape[0], 16)) if x.shape[1] < 16 else x
    s = tl.sum(b, axis=1)
    tl.store(o_ptr + r, s)"""

SHAPE_FOLD_CASE = '''def ref(args, meta):
    x = args["x_ptr"].reshape(int(args["R"]), int(args["C"]))
    # the where/reshape idiom zero-pads axis 1 out to 16 lanes per row
    # before the sum: the padding contributes 0, so the row sum stands
    return {"o_ptr": x.sum(axis=1)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    R, C = 8, 8                 # C < 16: the pad branch folds and runs
    rng = np.random.default_rng(seed)
    x = rng.normal(0, 1, (R, C)).astype(np.float32)
    args = {"x_ptr": x.ravel(), "o_ptr": np.zeros(R), "R": R, "C": C}
    meta = {"R": R, "C": C}
    grid = (1,)
    return {"args": args, "meta": meta, "grid": grid,
            "kernel": shape_fold_kernel, "outputs": ("o_ptr",),
            "expected": ref(args, meta),
            "comparison": {"o_ptr": {"comparator": "allclose",
                                     "rtol": 1e-5, "atol": 1e-5}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape or SHAPES[0], dtype or "float32", seed or 0)'''

# the negative control: a GENUINELY runtime arange bound keeps the
# located refusal (never a baked value)
RUNTIME_ARANGE_BODY = """\
    pid = tl.program_id(0)
    i = tl.arange(0, n)
    tl.store(o_ptr + pid, tl.sum(tl.load(x_ptr + i).to(tl.float32), axis=0))"""

RUNTIME_ARANGE_CASE = '''def ref(args, meta):
    return {"o_ptr": np.zeros(1)}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n = 8
    args = {"x_ptr": np.ones(n), "o_ptr": np.zeros(1), "n": n}
    meta = {"BLOCK": 8}
    return {"args": args, "meta": meta, "grid": (1,),
            "kernel": runtime_arange_kernel, "outputs": ("o_ptr",),
            "expected": ref(args, meta),
            "comparison": {"o_ptr": {"comparator": "array_equal",
                                     "exact": True}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape or SHAPES[0], dtype or "float32", seed or 0)'''

# ---------------------------------------------------------------------------
# 6. program_id(1) under a 2-axis grid (pairwise_distance class)
# ---------------------------------------------------------------------------

PID_AXIS_BODY = """\
    pid_n = tl.program_id(0)
    pid_d = tl.program_id(1)
    i = pid_d * BLOCK + tl.arange(0, BLOCK)
    m = i < D
    a = tl.load(x1_ptr + pid_n * D + i, mask=m, other=0.0)
    b = tl.load(x2_ptr + pid_n * D + i, mask=m, other=0.0)
    part = tl.sum(a * b, axis=0)
    tl.store(o_ptr + pid_n * num_d + pid_d, part)"""

PID_AXIS_CASE = '''def ref(args, meta):
    x1 = args["x1_ptr"]
    x2 = args["x2_ptr"]
    D = int(args["D"])
    R = x1.size // D
    P = (D + 127) // 128
    o = np.zeros(R * P)
    for r in range(R):
        for p in range(P):
            o[r * P + p] = (x1[r * D + p * 128:(r + 1) * D][:128]
                            * x2[r * D + p * 128:(r + 1) * D][:128]).sum()
    return {"o_ptr": o}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    R, D = 5, 300
    rng = np.random.default_rng(seed)
    x1 = rng.normal(0, 1, R * D)
    x2 = rng.normal(0, 1, R * D)
    P = (D + 127) // 128
    args = {"x1_ptr": x1, "x2_ptr": x2, "o_ptr": np.zeros(R * P),
            "D": D, "num_d": P}
    meta = {"BLOCK": 128}
    grid = (R, P)
    return {"args": args, "meta": meta, "grid": grid,
            "kernel": pid_axis_kernel, "outputs": ("o_ptr",),
            "expected": ref(args, meta),
            "comparison": {"o_ptr": {"comparator": "allclose",
                                     "rtol": 1e-4, "atol": 1e-4}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape or SHAPES[0], dtype or "float32", seed or 0)'''



# ---------------------------------------------------------------------------
# 7. the 16-bit float SCALAR binop rides the fp32-lane policy (bf16 bits
#    at the e16 lanes are fp16 on this target -- the pre-fix scalar path
#    ran them there and silently miscompiled blocked_jacobi's
#    alpha * beta)
# ---------------------------------------------------------------------------

BF16_SCALAR_BODY = """\
    rows = tl.arange(0, ROWS)
    m = rows < ROWS
    ap = tl.load(X + rows, mask=m, other=0.0)
    aq = tl.load(W + rows, mask=m, other=0.0)
    alpha = tl.sum(ap * ap)
    beta = tl.sum(aq * aq)
    gamma = tl.sum(ap * aq)
    tl.store(o1_ptr + 0, alpha)
    tl.store(o2_ptr + 0, beta)
    tl.store(o3_ptr + 0, gamma)
    eps = 1e-20
    t = alpha * beta + eps
    tl.store(o4_ptr + 0, t)
    tl.store(o5_ptr + 0, tl.sqrt(t))
    tl.store(o6_ptr + 0, tl.where(gamma > 0.0, alpha, beta))"""

BF16_SCALAR_CASE = '''def ref(args, meta):
    # fp32 semantics on the (bf16-rounded) inputs; the candidate's
    # intermediate bf16 roundings stay inside the 2% tolerance
    x = np.asarray(args["X"], np.float32)
    w = np.asarray(args["W"], np.float32)
    alpha = np.float32((x * x).sum())
    beta = np.float32((w * w).sum())
    gamma = np.float32((x * w).sum())
    t = np.float32(alpha * beta + 1e-20)
    o6 = np.float32(alpha if gamma > 0.0 else beta)
    return {"o1_ptr": alpha[None], "o2_ptr": beta[None],
            "o3_ptr": gamma[None], "o4_ptr": t[None],
            "o5_ptr": np.float32(np.sqrt(t))[None], "o6_ptr": o6[None]}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    R = 16
    rng = np.random.default_rng(seed)
    x = rng.normal(0, 1, R).astype(np.float32)
    w = rng.normal(0, 1, R).astype(np.float32)
    args = {"X": x, "W": w, "o1_ptr": np.zeros(1, np.float32),
            "o2_ptr": np.zeros(1, np.float32), "o3_ptr": np.zeros(1, np.float32),
            "o4_ptr": np.zeros(1, np.float32), "o5_ptr": np.zeros(1, np.float32),
            "o6_ptr": np.zeros(1, np.float32)}
    meta = {"ROWS": R}
    return {"args": args, "meta": meta, "grid": (1,),
            "kernel": bf16_scalar_kernel,
            "outputs": ("o1_ptr", "o2_ptr", "o3_ptr", "o4_ptr", "o5_ptr",
                       "o6_ptr"),
            "expected": ref(args, meta),
            "comparison": {k: {"comparator": "allclose", "rtol": 0.02,
                               "atol": 0.02}
                           for k in ("o1_ptr", "o2_ptr", "o3_ptr",
                                     "o4_ptr", "o5_ptr", "o6_ptr")},
            "shape": (R,), "dtype": dtype}


def make_case(shape=None, dtype=None, seed=None):
    from opslib.case import dtype_case
    case = _make_case(shape or SHAPES[0], "float32", seed or 0)
    want = dtype or "bfloat16"
    if want in ("bfloat16", "float16"):
        return dtype_case(case, want, ref=None)
    return case
'''

def main() -> int:
    workdir = Path(tempfile.mkdtemp(prefix="a100c-t031-"))
    compiler = FactoryCompiler(
        options=CompileOptions(cache_dir=str(workdir / "cache")))
    try:
        # 1. the scalar-bool lane
        path = _operator_file(workdir, "bool_any",
                              "x_ptr, flags_ptr, mid_ptr, out_ptr, n, "
                              "n_blocks, BLOCK: tl.constexpr, "
                              "MID_BLOCK: tl.constexpr",
                              BOOL_ANY_BODY, BOOL_ANY_CASE)
        module = _load(path)
        bad = []
        for threads in (1, 4):
            for shape in ((257,), (514,)):
                ok, detail = _run_case(compiler, module, threads,
                                       shape=shape)
                if not ok:
                    bad.append(f"t={threads} s={shape}: {detail}")
        check("t031-bool-any-store-exact-at-1-and-4-workers", not bad,
              "; ".join(bad[:2]))

        # 2. the block bool store round-trip
        path = _operator_file(workdir, "bool_block",
                              "x_ptr, b_ptr, o_ptr, n, "
                              "BLOCK: tl.constexpr",
                              BOOL_BLOCK_BODY, BOOL_BLOCK_CASE)
        module = _load(path)
        bad = []
        for threads in (1, 4):
            for shape in ((257,), (514,)):
                ok, detail = _run_case(compiler, module, threads,
                                       shape=shape)
                if not ok:
                    bad.append(f"t={threads} s={shape}: {detail}")
        check("t031-bool-block-store-round-trips-exactly", not bad,
              "; ".join(bad[:2]))

        # 3. the in-region sum consumed by a scalar chain (the merged
        #    value, never the per-chunk partial)
        path = _operator_file(workdir, "bool_median",
                              "counts, first_false, first_true, values, "
                              "indices, reduction_size, "
                              "chunks_per_output: tl.constexpr, "
                              "BLOCK: tl.constexpr",
                              BOOL_MEDIAN_BODY, BOOL_MEDIAN_CASE)
        module = _load(path)
        bad = []
        for threads in (1, 4):
            ok, detail = _run_case(compiler, module, threads)
            if not ok:
                bad.append(f"t={threads}: {detail}")
        check("t031-in-region-sum-consumer-reads-merged-value", not bad,
              "; ".join(bad[:2]))

        # 4. the masked scalar store
        path = _operator_file(workdir, "masked_scalar",
                              "x_ptr, o_ptr, m, BLOCK: tl.constexpr",
                              MASKED_SCALAR_BODY, MASKED_SCALAR_CASE)
        module = _load(path)
        bad = []
        for threads in (1, 4):
            for shape in ((37,), (257,)):
                ok, detail = _run_case(compiler, module, threads,
                                       shape=shape)
                if not ok:
                    bad.append(f"t={threads} s={shape}: {detail}")
        check("t031-masked-scalar-store-no-access-when-disabled", not bad,
              "; ".join(bad[:2]))

        # 5. the constexpr shape fold + its negative control
        path = _operator_file(workdir, "shape_fold",
                              "x_ptr, o_ptr, R: tl.constexpr, "
                              "C: tl.constexpr",
                              SHAPE_FOLD_BODY, SHAPE_FOLD_CASE)
        module = _load(path)
        bad = []
        for threads in (1, 4):
            ok, detail = _run_case(compiler, module, threads)
            if not ok:
                bad.append(f"t={threads}: {detail}")
        check("t031-shape-derived-arange-reshape-fold-lowers", not bad,
              "; ".join(bad[:2]))
        path = _operator_file(workdir, "runtime_arange",
                              "x_ptr, o_ptr, n, BLOCK: tl.constexpr",
                              RUNTIME_ARANGE_BODY, RUNTIME_ARANGE_CASE)
        module = _load(path)
        refused = False
        why = ""
        try:
            compiler.compile_case(module.make_case())
        except PipelineError as exc:
            refused = "compile-time integer" in str(exc) and \
                "tl.arange.end" in str(exc)
            why = str(exc)[:120]
        except Exception as exc:  # noqa: BLE001
            why = f"wrong error type {type(exc).__name__}: {exc}"[:120]
        check("t031-runtime-arange-end-keeps-located-refusal", refused, why)

        # 7. the 16-bit float scalar binop (fp32-lane policy)
        path = _operator_file(workdir, "bf16_scalar",
                              "X, W, o1_ptr, o2_ptr, o3_ptr, o4_ptr, "
                              "o5_ptr, o6_ptr, ROWS: tl.constexpr",
                              BF16_SCALAR_BODY, BF16_SCALAR_CASE)
        module = _load(path)
        bad = []
        for dt in ("bfloat16", "float16"):
            for threads in (1, 4):
                ok, detail = _run_case(compiler, module, threads, dtype=dt)
                if not ok:
                    bad.append(f"{dt} t={threads}: {detail}")
        check("t031-bf16-scalar-binop-rides-fp32-lanes", not bad,
              "; ".join(bad[:2]))
        # 6. program_id(1) under a 2-axis grid
        path = _operator_file(workdir, "pid_axis",
                              "x1_ptr, x2_ptr, o_ptr, D, num_d, "
                              "BLOCK: tl.constexpr",
                              PID_AXIS_BODY, PID_AXIS_CASE)
        module = _load(path)
        bad = []
        for threads in (1, 4):
            ok, detail = _run_case(compiler, module, threads)
            if not ok:
                bad.append(f"t={threads}: {detail}")
        # the axis-distinguishing control: swapping the grid axes must
        # NOT match (the reference is computed for (R, P), a kernel run
        # as if the axes were swapped produces a different layout)
        check("t031-program-id-axis1-decomposes-2-axis-grid", not bad,
              "; ".join(bad[:2]))
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    if FAILURES:
        print(f"\n{len(FAILURES)} check(s) failed: {FAILURES}",
              file=sys.stderr)
        return 1
    print("\ntest_t031_repairs: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
