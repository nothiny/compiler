#!/usr/bin/env python3
"""test_t033_repairs.py -- the T033 frontend-form repairs (gate G6).

Round-2 repair of the remaining frontend-form census classes:

  * descending ranges (``range(a, b, -s)`` -- 16 census rows): the counted
    loop form carries a ``descending`` flag pinned to the compile-time
    step sign; the head test continues while the induction stays ABOVE
    the upper bound (the pinned Triton descent), the while-form
    conversion (break/return inside) compares ``gt`` and the TIR verifier
    rejects a flag/step disagreement;
  * the ==1 specialization (6 'if' rows): an integer argument equal to 1
    is a constexpr 1 exactly like the pinned JIT's
    native_specialize_impl, so ``if groups == 1:`` folds and the untaken
    arm (deconv3d's block-tensor ``if lane_mask:``) never lowers -- a
    non-==1 identity keeps the located pinned refusal;
  * the block-pointer method advance (6 'gQ.advance' rows): the pinned
    ``tensor.advance`` member form, list-literal offsets included;
  * boolean block arithmetic (6 'arith.add' + 4 'cmp.eq' rows): i1 add
    is addition mod 2 -- the mask-register xor -- and i1 equality is the
    xnor (the new vmxor repertoire row);
  * the grid quotient ties (the extractable share of the 47 'grid'
    rows): a holed conditional value or an untied shape leaf that
    appears exactly once as a factor of a structurally tracked view
    extent product, with every other factor runtime-readable, reads as
    ``view_extent // cofactor`` at run time (never a baked shape);
  * the staged-block axis map (3 'layout' rows): a rank-1 staged offset
    reshaped to (8,1) inside an (8,32) addressing space aligns through
    the unique equal-extent matching, not positionally;
  * the scalar extract region + the scalar-segment staging (the 'add'
    row and the cholesky bf16 scalar class): ``vextract`` runs inside
    its value's own region, and the staging analysis sees the leading
    scalar segments' block values.

Every repaired class is exercised through the real compilation path (the
factory compiler -> the native executable on the pinned QEMU endpoint)
and compared against a reference computed independently of the compiler
(numpy in this test, or the corpus case's own numpy reference), at 1 and
4 workers.  The controls (MECH-WITNESS-TEST) pin the boundaries that
must keep refusing: the block-tensor condition at a non-==1 identity,
the genuinely untraceable grids (gn_finalize's product-only factors,
chunk_abc's opaque aligned views) and the TIR verifier's descending-flag
pin.

Run: python3 a100c/tests/test_t033_repairs.py   (exit 0 = all PASS)
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
    case = module.make_case(**make_kwargs) if make_kwargs \
        else module.make_case()
    device = nd.NativeExecutableDevice(compiler, threads)
    staged = device.stage_case(case)
    staged.launch()
    outputs = staged.outputs()
    ok = True
    detail = ""
    for name, policy in case["comparison"].items():
        got = np.asarray(outputs[name])
        exp = np.asarray(case["expected"][name])
        if got.shape != exp.shape and got.size == exp.size:
            got = got.reshape(exp.shape)
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


def _run_corpus_case(compiler, rel: str, threads: int, **make_kwargs):
    """One real corpus operator end to end (its own numpy reference)."""
    path = ROOT / "ops" / rel
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return _run_case(compiler, module, threads, **make_kwargs)


# ---------------------------------------------------------------------------
# 1. the descending counted range, executed (acceptance[1]: identical
#    indices to the ascending equivalent)
# ---------------------------------------------------------------------------

DESC_RANGE_BODY = """\
    pid = tl.program_id(0)
    base = pid * B
    acc = 0.0
    for i in range(B - 1, -1, -1):
        acc += tl.load(x_ptr + base + i)
        tl.store(y_ptr + base + i, acc)"""

ASC_RANGE_BODY = """\
    pid = tl.program_id(0)
    base = pid * B
    acc = 0.0
    for i in range(0, B):
        acc += tl.load(x_ptr + base + (B - 1 - i))
        tl.store(y_ptr + base + (B - 1 - i), acc)"""

DESC_RANGE_CASE = '''def ref(args, meta):
    x = np.asarray(args["x_ptr"], np.float64).reshape(-1, 32)
    # the reversed cumulative sum: y[i] = sum of x[i..B-1] within the
    # block -- what the descending loop computes
    y = np.cumsum(x[:, ::-1], axis=1)[:, ::-1]
    return {"y_ptr": y.ravel().astype(np.float32)}


def _make_case(shape=(4,), dtype="float32", seed=0):
    n = int(shape[0]) * 32
    rng = np.random.default_rng(seed)
    x = rng.uniform(-2.0, 2.0, (n,)).astype(np.float32)
    args = {"x_ptr": x, "y_ptr": np.zeros(n, np.float32)}
    meta = {"B": 32}
    grid = (n // 32,)
    return {"args": args, "meta": meta, "grid": grid, "shape": (n // 32,),
            "dtype": "float32", "kernel": %s_kernel,
            "outputs": ("y_ptr",), "expected": ref(args, meta),
            "comparison": {"y_ptr": {"comparator": "allclose",
                                     "exact": False,
                                     "rtol": 1e-5, "atol": 1e-5}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or (4,), dtype=dtype or "float32",
                      seed=seed or 0)'''


def check_descending_range(workdir, compiler):
    """The descending loop computes the reversed cumulative sum at 1 and 4
    workers; the ASCENDING-equivalent control kernel (the same elements,
    the same order, an ascending induction) produces identical values."""
    desc = _load(_operator_file(
        workdir, "desc_range", "x_ptr, y_ptr, B: tl.constexpr",
        DESC_RANGE_BODY, DESC_RANGE_CASE % "desc_range"))
    asc = _load(_operator_file(
        workdir, "asc_range", "x_ptr, y_ptr, B: tl.constexpr",
        ASC_RANGE_BODY, DESC_RANGE_CASE % "asc_range"))
    bad = []
    for shape in ((4,), (1,), (9,)):
        for threads in (1, 4):
            ok, detail = _run_case(compiler, desc, threads, shape=shape)
            if not ok:
                bad.append(f"desc {shape} t{threads}: {detail}")
    # the ascending equivalent on the same data: identical outputs
    import a100_support.native_device as nd
    case_d = desc.make_case()
    case_a = asc.make_case()
    for threads in (1, 4):
        dev_d = nd.NativeExecutableDevice(compiler, threads)
        staged_d = dev_d.stage_case(case_d)
        staged_d.launch()
        out_d = np.asarray(staged_d.outputs()["y_ptr"])
        dev_a = nd.NativeExecutableDevice(compiler, threads)
        staged_a = dev_a.stage_case(case_a)
        staged_a.launch()
        out_a = np.asarray(staged_a.outputs()["y_ptr"])
        if not np.allclose(out_d, out_a, rtol=1e-5, atol=1e-5):
            bad.append(f"asc-equivalent t{threads}: outputs differ")
    check("descending-range-executes-identical-to-ascending", not bad,
          "; ".join(bad[:1]))


# ---------------------------------------------------------------------------
# 2. the descending range with a break (the while-form conversion)
# ---------------------------------------------------------------------------

DESC_BREAK_BODY = """\
    acc = 0.0
    n = 0
    for i in range(B - 1, -1, -1):
        v = tl.load(x_ptr + i)
        if v < 0.0:
            break
        acc += v
        n += 1
    tl.store(y_ptr + tl.arange(0, 1), tl.full((1,), 0.0, tl.float32) + acc)
    tl.store(cnt_ptr + tl.arange(0, 1), tl.full((1,), 0, tl.int32) + n)"""

DESC_BREAK_CASE = '''def ref(args, meta):
    x = np.asarray(args["x_ptr"], np.float64)
    acc = 0.0
    n = 0
    for i in range(len(x) - 1, -1, -1):
        if x[i] < 0.0:
            break
        acc += x[i]
        n += 1
    return {"y_ptr": np.array([acc], np.float32),
            "cnt_ptr": np.array([n], np.int32)}


def _make_case(shape=(32,), dtype="float32", seed=0):
    n = 32
    rng = np.random.default_rng(seed)
    x = rng.uniform(0.5, 2.0, (n,)).astype(np.float32)
    x[:5] = -1.0            # the break fires at i = 4
    args = {"x_ptr": x, "y_ptr": np.zeros(1, np.float32),
            "cnt_ptr": np.zeros(1, np.int32)}
    meta = {"B": 32}
    grid = (1,)
    return {"args": args, "meta": meta, "grid": grid, "shape": (n,),
            "dtype": "float32", "kernel": desc_break_kernel,
            "outputs": ("y_ptr", "cnt_ptr"),
            "expected": ref(args, meta),
            "comparison": {"y_ptr": {"comparator": "allclose",
                                     "exact": False,
                                     "rtol": 1e-5, "atol": 1e-5},
                           "cnt_ptr": {"comparator": "array_equal",
                                       "exact": True}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or (32,), dtype=dtype or "float32",
                      seed=seed or 0)'''


def check_descending_break(workdir, compiler):
    module = _load(_operator_file(
        workdir, "desc_break", "x_ptr, y_ptr, cnt_ptr, B: tl.constexpr",
        DESC_BREAK_BODY, DESC_BREAK_CASE))
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(compiler, module, threads)
        if not ok:
            bad.append(f"t{threads}: {detail}")
    check("descending-range-with-break-executes", not bad,
          "; ".join(bad[:1]))


# ---------------------------------------------------------------------------
# 3. boolean block arithmetic (the i1 add broadcast + the i1 equality)
# ---------------------------------------------------------------------------

BOOL_BLOCK_BODY = """\
    rows = tl.arange(0, R)
    cols = tl.arange(0, C)
    a = tl.load(a_ptr + rows)
    b = tl.load(b_ptr + cols)
    mask_row = a > 0
    # the fused_pool_reduce broadcast idiom: int1 + zeros(int1) is
    # addition mod 2 over the mask lanes
    m2 = mask_row[:, None] + tl.zeros((1, C), dtype=tl.int1)
    g = tl.load(g_ptr + rows[:, None] * C + cols[None, :],
                mask=m2 & (b[None, :] > 0), other=0.0)
    s = tl.sum(g, axis=1)
    tl.store(s_ptr + rows, s)
    # the gelu_std/std equality form: (x >= 0) == (y >= 0) over blocks
    eq = ((a >= 0)[:, None] == (b >= 0)[None, :]).to(tl.int32)
    tl.store(eq_ptr + rows, tl.sum(eq, axis=1))"""

BOOL_BLOCK_CASE = '''def ref(args, meta):
    a = np.asarray(args["a_ptr"], np.float64)
    b = np.asarray(args["b_ptr"], np.float64)
    g = np.asarray(args["g_ptr"], np.float64).reshape(len(a), len(b))
    mask = (a > 0)[:, None] + np.zeros((1, len(b)), dtype=bool)
    full = mask & (b > 0)[None, :]
    s = np.where(full, g, 0.0).sum(axis=1)
    eq = ((a >= 0)[:, None] == (b >= 0)[None, :]).astype(np.int32)
    return {"s_ptr": s.astype(np.float32),
            "eq_ptr": eq.sum(axis=1)}


def _make_case(shape=(16,), dtype="float32", seed=0):
    R, C = 16, 8
    rng = np.random.default_rng(seed)
    a = rng.uniform(-2.0, 2.0, (R,)).astype(np.float32)
    b = rng.uniform(-2.0, 2.0, (C,)).astype(np.float32)
    g = rng.uniform(-1.0, 1.0, (R * C,)).astype(np.float32)
    args = {"a_ptr": a, "b_ptr": b, "g_ptr": g,
            "s_ptr": np.zeros(R, np.float32),
            "eq_ptr": np.zeros(R, np.int32)}
    meta = {"R": R, "C": C}
    grid = (1,)
    return {"args": args, "meta": meta, "grid": grid, "shape": (R,),
            "dtype": "float32", "kernel": bool_block_kernel,
            "outputs": ("s_ptr", "eq_ptr"),
            "expected": ref(args, meta),
            "comparison": {"s_ptr": {"comparator": "allclose",
                                     "exact": False,
                                     "rtol": 1e-5, "atol": 1e-5},
                           "eq_ptr": {"comparator": "array_equal",
                                      "exact": True}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or (16,), dtype=dtype or "float32",
                      seed=seed or 0)'''


def check_bool_block(workdir, compiler):
    module = _load(_operator_file(
        workdir, "bool_block",
        "a_ptr, b_ptr, g_ptr, s_ptr, eq_ptr, R: tl.constexpr,"
        " C: tl.constexpr",
        BOOL_BLOCK_BODY, BOOL_BLOCK_CASE))
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(compiler, module, threads)
        if not ok:
            bad.append(f"t{threads}: {detail}")
    check("boolean-block-add-and-eq-execute", not bad,
          "; ".join(bad[:1]))


# ---------------------------------------------------------------------------
# 4. the ==1 specialization (the dead else arm with a block-tensor if)
# ---------------------------------------------------------------------------

EQ1_BODY = """\
    offs = tl.arange(0, B)
    v = tl.load(x_ptr + offs)
    if groups == 1:
        y = v + 1.0
    else:
        if v > 0.5:
            y = v * 2.0
        else:
            y = v
    tl.store(y_ptr + offs, y)"""

EQ1_CASE = '''def ref(args, meta):
    x = np.asarray(args["x_ptr"], np.float64)
    groups = int(args["groups"])
    if groups == 1:
        y = x + 1.0
    else:
        y = np.where(x > 0.5, x * 2.0, x)
    return {"y_ptr": y.astype(np.float32)}


def _make_case(shape=(16,), dtype="float32", seed=0, groups=1):
    n = 16
    rng = np.random.default_rng(seed)
    x = rng.uniform(-1.0, 1.0, (n,)).astype(np.float32)
    args = {"x_ptr": x, "y_ptr": np.zeros(n, np.float32),
            "groups": groups}
    meta = {"B": 16}
    grid = (1,)
    return {"args": args, "meta": meta, "grid": grid, "shape": (n,),
            "dtype": "float32", "kernel": eq1_kernel,
            "outputs": ("y_ptr",), "expected": ref(args, meta),
            "comparison": {"y_ptr": {"comparator": "allclose",
                                     "exact": False,
                                     "rtol": 1e-5, "atol": 1e-5}}}


def make_case(shape=None, dtype=None, seed=None, groups=1):
    return _make_case(shape=shape or (16,), dtype=dtype or "float32",
                      seed=seed or 0, groups=groups)'''


def check_eq1_specialization(workdir, compiler):
    """groups == 1 (the ==1 class) folds the branch: the dead else arm's
    block-tensor ``if v > 0.5:`` never lowers and the kernel compiles and
    executes; the groups == 3 identity (the 'other' class) keeps the
    pinned located refusal -- a block-tensor condition cannot branch."""
    module = _load(_operator_file(
        workdir, "eq1", "x_ptr, y_ptr, groups, B: tl.constexpr",
        EQ1_BODY, EQ1_CASE))
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(compiler, module, threads)
        if not ok:
            bad.append(f"t{threads}: {detail}")
    check("eq1-specialization-folds-dead-arm-executes", not bad,
          "; ".join(bad[:1]))
    # control: the non-==1 identity still refuses, located
    try:
        _run_case(compiler, module, 1, groups=3)
        check("eq1-other-class-block-if-still-refuses", False,
              "the groups=3 identity compiled (expected the located "
              "refusal)")
    except PipelineError as exc:
        check("eq1-other-class-block-if-still-refuses",
              "block-tensor condition" in str(exc) and ".py:" in str(exc),
              str(exc)[:110])


# ---------------------------------------------------------------------------
# 5. the block-pointer method advance with a runtime offset
# ---------------------------------------------------------------------------

ADVANCE_BODY = """\
    row = tl.program_id(0)
    g = tl.make_block_ptr(base=x_ptr, shape=(R, C), strides=(C, 1),
                          offsets=(0, 0), block_shape=(1, B), order=(1, 0))
    g = g.advance([row, 0])
    v = tl.load(g, boundary_check=(0, 1))
    tl.store(y_ptr + row * B + tl.arange(0, B), v)"""

ADVANCE_CASE = '''def ref(args, meta):
    x = np.asarray(args["x_ptr"], np.float64).reshape(int(args["R"]),
                                                      int(args["C"]))
    B = int(meta["B"])
    out = np.zeros((int(args["R"]) * B,), np.float64)
    for row in range(int(args["R"])):
        cols = np.arange(B)
        vals = np.where(cols < int(args["C"]), x[row, np.minimum(
            cols, int(args["C"]) - 1)] if int(args["C"]) else 0.0, 0.0)
        out[row * B:(row + 1) * B] = vals
    return {"y_ptr": out.astype(np.float32)}


def _make_case(shape=(6,), dtype="float32", seed=0):
    R, C, B = 6, 5, 4
    rng = np.random.default_rng(seed)
    x = rng.uniform(-2.0, 2.0, (R * C,)).astype(np.float32)
    args = {"x_ptr": x, "y_ptr": np.zeros(R * B, np.float32),
            "R": R, "C": C}
    meta = {"B": B}
    grid = (R,)
    return {"args": args, "meta": meta, "grid": grid, "shape": (R,),
            "dtype": "float32", "kernel": advance_probe_kernel,
            "outputs": ("y_ptr",), "expected": ref(args, meta),
            "comparison": {"y_ptr": {"comparator": "allclose",
                                     "exact": False,
                                     "rtol": 1e-5, "atol": 1e-5}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or (6,), dtype=dtype or "float32",
                      seed=seed or 0)'''


def check_advance_method(workdir, compiler):
    module = _load(_operator_file(
        workdir, "advance_probe", "x_ptr, y_ptr, R, C, B: tl.constexpr",
        ADVANCE_BODY, ADVANCE_CASE))
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(compiler, module, threads)
        if not ok:
            bad.append(f"t{threads}: {detail}")
    check("blockptr-method-advance-executes", not bad,
          "; ".join(bad[:1]))


# ---------------------------------------------------------------------------
# 6. the repaired corpus operators, end to end on their own references
# ---------------------------------------------------------------------------

def check_corpus_operators(compiler):
    """One executed comparison per repaired census class through the real
    corpus operator (its case layer's numpy reference is independent of
    the compiler): reversed_cumsum (the descending range), cholesky_solve
    (the descending nest + the bf16 scalar emulation extract), gelu_std
    and std (the boolean block equality), fused_pool_reduce (the i1 add
    broadcast), tiled_argmin (the staged-block axis map) and softsign
    (the scalar-segment staging, the degenerate (1,) bf16 identity)."""
    entries = [
        ("suite/dev/reversed_cumsum.py", {}, "descending range"),
        ("suite/perf/cholesky_solve.py", {}, "descending nest + bf16"),
        ("suite/perf/gelu_std.py", {}, "boolean block eq"),
        ("suite/perf/std.py", {}, "boolean block eq"),
        ("suite/dev/fused_pool_reduce_kernel.py", {}, "i1 add broadcast"),
        ("suite/dev/tiled_argmin.py", {"shape": (2, 37, 5)},
         "staged axis map"),
        ("suite/dev/softsign_kernel.py", {"shape": (1,),
                                          "dtype": "bfloat16"},
         "scalar-segment staging"),
    ]
    bad = []
    for rel, kw, what in entries:
        for threads in (1, 4):
            try:
                ok, detail = _run_corpus_case(compiler, rel, threads, **kw)
            except Exception as exc:                       # noqa: BLE001
                bad.append(f"{rel} t{threads}: {type(exc).__name__}: "
                           f"{str(exc)[:90]}")
                continue
            if not ok:
                bad.append(f"{rel} t{threads}: {detail}")
    check("repaired-corpus-classes-execute-1-4-workers", not bad,
          "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# 7. the grid quotient ties: no baking across an identity's shapes
# ---------------------------------------------------------------------------

GRID_QUOTIENT_BODY = """\
    pid = tl.program_id(0)
    rows = pid * RB + tl.arange(0, RB)
    cols = tl.arange(0, 8)
    v = tl.load(x_ptr + rows[:, None] * n_cols + cols[None, :])
    tl.store(o_ptr + rows[:, None] * n_cols + cols[None, :], v * 2.0)"""

GRID_QUOTIENT_CASE = '''def ref(args, meta):
    x = np.asarray(args["x_ptr"], np.float64)
    return {"o_ptr": (x * 2.0).astype(np.float32)}


def _make_case(shape=(16, 8), dtype="float32", seed=0):
    rows, n = (int(v) for v in shape)
    rng = np.random.default_rng(seed)
    # the masked_cumsum_vec form: the views carry only the PRODUCT
    # rows*n (reshape(-1)); n rides the n_cols scalar; the grid axis
    # rows//RB ties as (view_extent // n_cols) // RB at run time (rows
    # is a multiple of RB and n is 8, so no row-bound scalar exists to
    # tie directly)
    x = (rng.standard_normal((rows, n)) * 2).astype(np.float32)
    args = {"x_ptr": x.reshape(-1), "o_ptr": np.full(rows * n, -7.0,
                                                     np.float32),
            "n_cols": np.int32(n)}
    meta = {"RB": 8}
    grid = (rows // 8,)
    return {"args": args, "meta": meta, "grid": grid, "shape": (rows, n),
            "dtype": "float32", "kernel": grid_quotient_kernel,
            "outputs": ("o_ptr",), "expected": ref(args, meta),
            "comparison": {"o_ptr": {"comparator": "allclose",
                                     "exact": False,
                                     "rtol": 1e-5, "atol": 1e-5}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or (16, 8), dtype=dtype or "float32",
                      seed=seed or 0)'''


def check_grid_no_baking(workdir, compiler):
    """The quotient tie reads the actual view extent and cofactor at run
    time: two shapes of ONE identity (rows 16 vs 24, the same n_cols=8
    and meta -- the same scalar classes) share a single artifact (the
    second compile is a cache hit on the very same executable) and BOTH
    execute correctly -- no shape was baked into the launch geometry.
    The axis assertion checks the modeled form carries the runtime
    reads; the executed comparisons are the witness."""
    module = _load(_operator_file(
        workdir, "grid_quotient",
        "x_ptr, o_ptr, n_cols, RB: tl.constexpr",
        GRID_QUOTIENT_BODY, GRID_QUOTIENT_CASE))
    bad = []
    from a100c.frontend.gridmodel import extract_grid, GridError
    from a100c.frontend.source import load_operator
    src = load_operator(str(workdir / "grid_quotient.py"))
    for shape in ((16, 8), (24, 8)):
        case = module.make_case(shape=shape)
        try:
            model = extract_grid(src, case)
        except GridError as exc:
            bad.append(f"{shape}: refused {str(exc)[:80]}")
            continue
        sc = model.self_check
        if sc.get("modeled") != sc.get("declared"):
            bad.append(f"{shape}: self-check {sc}")
        axis = repr(model.axes[0])
        if "bundle_view" not in axis or "floordiv" not in axis:
            bad.append(f"{shape}: axis {axis[:70]} is not a quotient read")
        if axis.replace(" ", "").isdigit():
            bad.append(f"{shape}: axis baked")
    # the no-baking execution control: two shapes, one artifact, both
    # correct (the second compile must be a cache hit)
    artifacts = []
    for shape in ((16, 8), (24, 8)):
        try:
            ok, detail = _run_case(compiler, module, 1, shape=shape)
        except Exception as exc:                           # noqa: BLE001
            bad.append(f"{shape}: {type(exc).__name__}: {str(exc)[:90]}")
            continue
        if not ok:
            bad.append(f"{shape}: {detail}")
    one_artifact = len({str(a) for a in artifacts}) <= 1
    check("grid-quotient-tie-no-baking-two-shapes",
          not bad, "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# 8. the refusal controls (MECH-WITNESS-TEST)
# ---------------------------------------------------------------------------

def check_refusal_controls(compiler):
    """The boundaries that must keep refusing, located: the genuinely
    untraceable grids (gn_finalize's product-only shape factors,
    chunk_abc's opaque aligned views) and the TIR verifier's
    descending-flag pin (a hand-built module with a flag/step
    disagreement is rejected)."""
    from a100c.frontend.gridmodel import extract_grid, GridError
    from a100c.frontend.source import load_operator
    bad = []
    for rel, fragment in (
            ("suite/dev/gn_finalize_kernel.py", "cannot be proven equal"),
            ("suite/dev/chunk_abc_fwd_kernel_intra_K.py",
             "cannot be proven equal")):
        path = ROOT / "ops" / rel
        spec = importlib.util.spec_from_file_location(path.stem, str(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        try:
            extract_grid(load_operator(str(path)), module.make_case())
            bad.append(f"{rel}: accepted (expected the located refusal)")
        except GridError as exc:
            if fragment not in str(exc):
                bad.append(f"{rel}: {str(exc)[:90]}")
    check("genuinely-untraceable-grids-still-refuse-located", not bad,
          "; ".join(bad[:2]))

    # the verifier's descending-flag pin: a hand-built module whose
    # counted loop declares `descending` over a POSITIVE step (and the
    # mirror form: a negative step left ascending) is rejected
    from a100c.ir import tir as tir_mod
    from a100c.ir.tir import verify_module

    def _malformed(descending: bool, step: int):
        mod = tir_mod.Module("probe", "<builtin>")
        fn = tir_mod.Function("probe", [])
        mod.functions.append(fn)
        consts = []
        for value in (0, 8, step):
            op = tir_mod.Op.const(value, tir_mod.INT32)
            fn.body.statements.append(op)
            consts.append(op.results[0])
        loop = tir_mod.Loop(consts[0], consts[1], consts[2], None,
                            descending=descending)
        loop.carried = (("i", consts[0]),)
        loop.join_results = (consts[0],)
        fn.body.statements.append(loop)
        return verify_module(mod)

    errs_desc = _malformed(True, 2)
    errs_undecl = _malformed(False, -2)
    saw_desc = any("descending" in str(e.message) for e in errs_desc)
    saw_undecl = any("descending" in str(e.message) for e in errs_undecl)
    check("tir-verifier-rejects-flag-step-disagreement",
          saw_desc and saw_undecl,
          f"declared={saw_desc} undeclared={saw_undecl}; "
          f"{str(errs_desc[0])[:80] if errs_desc else 'none'}")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    workdir = Path(tempfile.mkdtemp(prefix="a100c-t033-"))
    cache = workdir / "cache"
    try:
        compiler = FactoryCompiler(
            options=CompileOptions(cache_dir=str(cache)))
        check_descending_range(workdir, compiler)
        check_descending_break(workdir, compiler)
        check_bool_block(workdir, compiler)
        check_eq1_specialization(workdir, compiler)
        check_advance_method(workdir, compiler)
        check_corpus_operators(compiler)
        check_grid_no_baking(workdir, compiler)
        check_refusal_controls(compiler)
    finally:
        import shutil
        shutil.rmtree(workdir, ignore_errors=True)
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_t033_repairs: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
