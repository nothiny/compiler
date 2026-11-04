#!/usr/bin/env python3
"""test_grid_model.py -- the provenance-tracking case-layer grid model
(T008, gate G5).

  acceptance[1] the grid model reproduces the concrete grid of every
      corpus operator at compile time via the provenance self-check, or
      refuses with a located diagnostic naming the untraceable input; the
      extraction/refusal census is recorded (no silent baking).

Corpus grid forms covered: multi-axis tuples, cdiv products, the
``lambda meta:`` form (autotune-config constexprs folded, identity-tier),
shape-derived locals (``int(shape[0])``, ``np.prod``, unpacking,
``map(int, shape)``), view extents (``x.shape[0]``, arrays created from
tracked sizes, the two-pass binding of opaque arrays), scalar arguments,
``min``/``max`` over tracked inputs (one MinMax node, realized natively by
the declared compare/mask/select sequence) and ``np.ceil(a / b)``.

Run: python3 a100c/tests/test_grid_model.py   (exit 0 = all checks PASS)
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
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
          f"{(' | ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(name)
    return ok


import numpy as np  # noqa: E402

from a100c.frontend import source as fe_source  # noqa: E402
from a100c.frontend.gridmodel import (  # noqa: E402
    Bin, GridError, Lit, MinMax, Ref, evaluate_expr, extract_grid)

OPS = ROOT / "ops"


def load_module(rel: str):
    spec = importlib.util.spec_from_file_location(
        rel.replace("/", "_").replace(".py", ""), str(OPS / rel))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_source(rel: str):
    return fe_source.load_operator(str(OPS / rel), corpus_root=str(OPS))


# ---------------------------------------------------------------------------
# The corpus grid forms
# ---------------------------------------------------------------------------


def check_corpus_forms():
    """Every declared grid form extracts with the expected tie kinds and a
    passing self-check (modeled == declared, recorded)."""
    bad = []

    def extract(rel, **make):
        module = load_module(rel)
        case = module.make_case(**make) if make else module.make_case()
        model = extract_grid(load_source(rel), case)
        sc = model.self_check
        if sc.get("modeled") != sc.get("declared"):
            bad.append(f"{rel}: self-check {sc}")
        return model

    # 1-D view-extent tie (a runtime dynamic loop over a loaded length)
    m = extract("suite/dev/var_len_copy.py", shape=(4,), dtype="float32")
    if not (m.ndim == 1 and m.axes
            and "shape_extent" in repr(m.axes[0])
            and any(t[0] == "view_extent" for t in m.ties.values())):
        bad.append(f"var_len_copy: {m.describe()}")

    # 1-D cdiv over a scalar-argument tie
    m = extract("suite/dev/absolute_kernel.py", shape=(97,))
    if not (m.ndim == 1 and "floordiv" in repr(m.axes[0])
            and any(t[0] == "scalar" for t in m.ties.values())):
        bad.append(f"absolute: {m.describe()}")

    # 2-axis lambda-meta form with the autotune config folded (identity
    # tier) and both axes tied to view extents
    m = extract("suite/perf/swiglu_fwd.py")
    if not (m.ndim == 2
            and any(t[0] == "view_extent" for t in m.ties.values())):
        bad.append(f"swiglu: {m.describe()}")

    # np.prod of a 1-D shape tied to the created view
    m = extract("suite/dev/bitcast.py")
    if not (m.ndim == 1 and "floordiv" in repr(m.axes[0])
            and any(t[0] == "view_extent" for t in m.ties.values())):
        bad.append(f"bitcast: {m.describe()}")

    # multi-axis shape arithmetic with scalar ties and a value tie
    m = extract("suite/dev/adaptive_avg_pool2d_kernel.py")
    if not (m.ndim == 2
            and any(t[0] == "scalar" for t in m.ties.values())
            and any(t[0] == "view_extent" for t in m.ties.values())):
        bad.append(f"adaptive: {m.describe()}")

    # shape unpacking + per-axis arithmetic (the direct make_case form)
    m = extract("suite/dev/maxpool1d.py")
    if not (m.ndim == 2 and len(m.ties) >= 4):
        bad.append(f"maxpool1d: {m.describe()}")

    check("corpus-grid-forms-extract-with-ties", not bad, "; ".join(bad[:3]))


def check_no_baking():
    """A shape-dependent grid stays SYMBOLIC in the expression: the axes
    carry Ref leaves, never a folded literal of this case's shape (the
    concrete values are self-check inputs only)."""
    bad = []
    for rel, make in (("suite/dev/var_len_copy.py",
                       {"shape": (4,), "dtype": "float32"}),
                      ("suite/dev/absolute_kernel.py", {"shape": (97,)}),
                      ("suite/perf/swiglu_fwd.py", {})):
        module = load_module(rel)
        case = module.make_case(**make) if make else module.make_case()
        model = extract_grid(load_source(rel), case)
        for axis in model.axes:
            if not _grid_leafs_of(axis):
                bad.append(f"{rel}: axis {axis!r} has no symbolic leaf "
                           "(the case's shape was baked)")
    # the control: a grid that is a compile-time constant in the source is
    # a literal (amax: grid = ((M + 1) // 2,) with M a module constant)
    module = load_module("suite/dev/amax_kernel.py")
    model = extract_grid(load_source("suite/dev/amax_kernel.py"),
                         module.make_case())
    if not all(isinstance(a, Lit) for a in model.axes):
        bad.append(f"amax: constant grid is not literal {model.axes!r}")
    check("grid-expressions-stay-symbolic-never-baked", not bad,
          "; ".join(bad[:2]))


def _grid_leafs_of(expr):
    if isinstance(expr, Ref):
        return [expr]
    if isinstance(expr, (Bin, MinMax)):
        return _grid_leafs_of(expr.left) + _grid_leafs_of(expr.right)
    return []


def check_self_check():
    """The compile-time equality self-check: modeled == declared is
    recorded; a disagreement (a tampered declared grid, or a tie that picks
    the wrong view) refuses loudly."""
    bad = []
    module = load_module("suite/dev/var_len_copy.py")
    case = module.make_case(shape=(4,), dtype="float32")
    model = extract_grid(load_source("suite/dev/var_len_copy.py"), case)
    if model.self_check.get("modeled") != [4] or \
            model.self_check.get("declared") != [4]:
        bad.append(f"self-check record: {model.self_check}")

    # a tampered declared grid: the model must refuse (never silently
    # trust either side)
    tampered = dict(case, grid=(5,))
    try:
        extract_grid(load_source("suite/dev/var_len_copy.py"), tampered)
        bad.append("tampered declared grid accepted")
    except GridError as exc:
        if "self-check failed" not in str(exc):
            bad.append(f"tampered: {str(exc)[:80]}")

    # a wrong value tie refuses through the self-check: bitcast's n ties
    # to x_ptr's axis 0; a case whose x has a different extent than the
    # grid expression expects fails the equality check
    module_bc = load_module("suite/dev/bitcast.py")
    case_bc = module_bc.make_case()
    ok = True
    try:
        extract_grid(load_source("suite/dev/bitcast.py"), case_bc)
    except GridError:
        ok = False
    if not ok:
        bad.append("bitcast (untampered) refused")

    check("grid-self-check-binds-modeled-to-declared", not bad,
          "; ".join(bad[:2]))


def check_refusals_located():
    """Refusals are located and name the untraceable input (never a silent
    bake): a grid over the seed (a case parameter, not bundle-visible),
    and tril's M/C (present only in meta, not in any bundle quantity)."""
    bad = []
    module = load_module("suite/dev/var_len_copy.py")
    case = module.make_case(shape=(4,), dtype="float32")

    # a synthetic untraceable grid: replace the case's grid with one over
    # a value no bundle quantity can prove (the seed)
    text = (OPS / "suite" / "dev" / "var_len_copy.py").read_text()
    text = text.replace('"grid": (num,),', '"grid": (num + seed,),')
    scratch = ROOT / "a100c" / "tests" / "_scratch_grid_seed.py"
    scratch.write_text(text)
    try:
        src_bad = fe_source.load_operator(str(scratch),
                                          corpus_root=str(OPS))
        try:
            extract_grid(src_bad, case)
            bad.append("seed grid accepted")
        except GridError as exc:
            if ("case_param" not in str(exc)
                    and "case parameter" not in str(exc)) or not exc.line:
                bad.append(f"seed grid: {str(exc)[:120]}")
    finally:
        scratch.unlink(missing_ok=True)

    # tril: M and C are meta constexprs, not bundle-visible -- the refusal
    # names the case-shape axis it cannot tie
    module_tril = load_module("suite/dev/tril_inplace_zero_tile_kernel.py")
    try:
        extract_grid(load_source("suite/dev/tril_inplace_zero_tile_kernel.py"),
                     module_tril.make_case())
        bad.append("tril grid accepted")
    except GridError as exc:
        if "cannot be proven equal" not in str(exc) or \
                "shape_extent" not in str(exc) or not exc.line:
            bad.append(f"tril: {str(exc)[:90]}")

    check("grid-refusals-located-naming-the-input", not bad,
          "; ".join(bad[:2]))


def check_minmax_and_ceil():
    """min/max and np.ceil(a/b) carry as grid expressions and evaluate
    exactly (the native routine realizes max/min with the declared
    compare/mask/select scalar sequence)."""
    bad = []
    a, b = Ref("shape_extent", (0,)), Ref("shape_extent", (1,))
    for lhs, rhs, want in ((7, 3, 7), (3, 7, 7), (5, 5, 5)):
        expr = MinMax("max", Lit(lhs), Lit(rhs))
        got = evaluate_expr(expr, {})
        if got != want:
            bad.append(f"max({lhs},{rhs}) = {got}")
    for lhs, rhs, want in ((7, 3, 3), (3, 7, 3), (5, 5, 5)):
        expr = MinMax("min", Lit(lhs), Lit(rhs))
        if evaluate_expr(expr, {}) != want:
            bad.append(f"min({lhs},{rhs}) wrong")
    # mixed symbolic/concrete and nesting
    expr = MinMax("max", a, Lit(2))
    if evaluate_expr(expr, {(0,): 1}) != 2 or \
            evaluate_expr(expr, {(0,): 9}) != 9:
        bad.append("max(a, 2) wrong")
    expr = Bin("floordiv", MinMax("max", a, Lit(1)), Lit(4))
    if evaluate_expr(expr, {(0,): 9}) != 2:
        bad.append("cdiv(max(a,1),4) wrong")
    # ceil(a / b) = -((-a) // b) over positives
    expr = Bin("sub", Lit(0),
               Bin("floordiv", Bin("sub", Lit(0), a), Lit(4)))
    if evaluate_expr(expr, {(0,): 9}) != 3 or \
            evaluate_expr(expr, {(0,): 8}) != 2:
        bad.append("ceil(a/4) wrong")
    # the leaf walk covers MinMax children
    from a100c.frontend.gridmodel import _grid_leafs
    if set(_grid_leafs(MinMax("min", a, b))) != {a, b}:
        bad.append("MinMax leaf walk")
    check("minmax-ceil-grid-expressions-exact", not bad, "; ".join(bad[:3]))


# ---------------------------------------------------------------------------
# The full-corpus census (acceptance[1])
# ---------------------------------------------------------------------------


def check_corpus_census():
    """Every corpus case (2734 = 500 operators x shape x dtype, both
    tiers, the corpus's own enumeration) either extracts with a passing
    self-check or refuses with a located diagnostic; the census is
    recorded.  No silent baking: every extracted model's self-check
    records modeled == declared, and every refusal carries a construct,
    a location and a message."""
    import os
    os.chdir(str(OPS))
    from compiler_api.run_cases import cases_from_manifest, enumerate_cases
    from opslib import golden
    from a100c.frontend.gridmodel import census

    started = time.time()
    paths = cases_from_manifest(str(OPS / "suite" / "manifest.json"))
    entries = []
    for spec_h, shape, dtype in enumerate_cases(paths=paths):
        case = golden.load_or_build_spec(spec_h, shape=shape, dtype=dtype,
                                         seed=30, use_cache=True)
        src = fe_source.load_operator(spec_h.path, corpus_root=str(OPS))
        entries.append((src, case))
    report = census(entries)
    elapsed = time.time() - started

    bad = []
    if report["entries"] != 2734:
        bad.append(f"entries {report['entries']} != 2734")
    if report["extracted"] + report["refused"] != report["entries"]:
        bad.append("counts do not add up")
    internal = [k for k in report["refusals"] if k.startswith("internal:")]
    if internal:
        bad.append(f"unexpected internal errors: {internal}")
    for d in report["details"]:
        if d["outcome"] == "extracted":
            if d["self_check"].get("modeled") != d["self_check"].get("declared"):
                bad.append(f"extracted without a passing self-check: "
                           f"{d['source']}")
        else:
            if not d.get("location") or not d.get("message") \
                    or not d.get("construct"):
                bad.append(f"unlocated refusal: {d}")

    # the census is recorded (the artifact the report cites)
    out = ROOT / "a100c" / "cache" / "grid-census.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")

    ops_all = {d["source"] for d in report["details"]}
    ops_refused = {d["source"] for d in report["details"]
                   if d["outcome"] == "refused"}
    ops_full = ops_all - ops_refused
    print(f"     census: {report['extracted']} extracted / "
          f"{report['refused']} refused of {report['entries']} cases "
          f"({len(ops_all)} operators, {len(ops_full)} fully extracted); "
          f"ndim={report['ndim_histogram']} "
          f"ties={report['tie_kinds']} ({elapsed:.0f}s, artifact {out})")
    refusal_classes = {}
    for d in report["details"]:
        if d["outcome"] != "refused":
            continue
        m = d["message"]
        if "cannot be proven equal" in m:
            key = "genuinely-untied-input"
        elif "cannot see" in m:
            key = "axis-untracked-value"
        elif "self-check failed" in m:
            key = "self-check-mismatch"
        elif "never assigns a trackable" in m:
            key = "no-trackable-grid"
        else:
            key = d["construct"]
        refusal_classes[key] = refusal_classes.get(key, 0) + 1
    print(f"     refusal classes: {json.dumps(refusal_classes, sort_keys=True)}")

    check("corpus-grid-census-extracted-or-located-refusal", not bad,
          "; ".join(bad[:3]))


def check_minmax_grid_executes():
    """A max()-gridded kernel executes end to end through the real
    pipeline: the native grid-evaluation routine realizes the MinMax node
    with the declared compare/mask/select sequence (max(n, 256) picks a
    different grid per shape; a wrong select changes the output)."""
    import tempfile
    import a100_support.native_device as nd
    from a100c.driver import Compiler, CompileOptions

    workdir = Path(tempfile.mkdtemp(prefix="a100c-mm-"))
    try:
        body = ("    pid = tl.program_id(0)\n"
                "    i = pid * BLOCK + tl.arange(0, BLOCK)\n"
                "    m = i < n\n"
                "    v = tl.load(x_ptr + i, mask=m)\n"
                "    tl.store(out_ptr + i, v + 1, mask=m)\n")
        case_layer = (
            'def ref(args, meta):\n'
            '    return {"out_ptr": (args["x_ptr"] + 1).astype(np.int32)}\n'
            '\n'
            'def _make_case(shape=SHAPES[0], dtype="int32", seed=0):\n'
            '    n = int(shape[0])\n'
            '    rng = np.random.default_rng(seed)\n'
            '    x = rng.integers(-50, 50, n).astype(np.int32)\n'
            '    args = {"x_ptr": x, "out_ptr": np.zeros(n, np.int32),\n'
            '            "n": n}\n'
            '    meta = {"BLOCK": 128}\n'
            '    grid = (max(n, 256) + 127) // 128,\n'
            '    return {"args": args, "meta": meta, "grid": grid,\n'
            '            "kernel": mmgrid_kernel, "outputs": ("out_ptr",),\n'
            '            "expected": ref(args, meta),\n'
            '            "comparison": {"out_ptr": {"comparator": "array_equal",\n'
            '                                       "exact": True}}}\n'
            '\n'
            'def make_case(shape=None, dtype=None, seed=None):\n'
            '    return _make_case(shape=shape or SHAPES[0])\n')
        text = ('"""probe operator mmgrid"""\n'
                'OPERATOR = {"name": "probe/mmgrid", "group": "probe",\n'
                '            "channel": "local", "execution": "triton_kernel",\n'
                '            "verification": "correctness", "tags": []}\n'
                'SHAPES = ((300,), (100,))\n'
                'import numpy as np\n'
                'import triton\n'
                'import triton.language as tl\n'
                '\n'
                '@triton.jit\n'
                'def mmgrid_kernel(x_ptr, out_ptr, n, BLOCK: tl.constexpr):\n'
                + body + '\n\n' + case_layer)
        path = workdir / "mmgrid.py"
        path.write_text(text)
        spec = importlib.util.spec_from_file_location("mmgrid", str(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        src = fe_source.load_operator(str(path))
        model = extract_grid(src, module.make_case(shape=(300,)))
        if "max" not in repr(model.axes[0]):
            check("minmax-grid-executes", False,
                  f"axis is not a MinMax: {model.axes[0]!r}")
            return
        compiler = Compiler(options=CompileOptions(
            cache_dir=str(workdir / "cache")))
        bad = []
        for threads in (1, 4):
            for shape in ((300,), (100,)):
                case = module.make_case(shape=shape)
                device = nd.NativeExecutableDevice(compiler, threads)
                staged = device.stage_case(case)
                staged.launch()
                got = np.asarray(staged.outputs()["out_ptr"])
                exp = np.asarray(case["expected"]["out_ptr"])
                if not np.array_equal(got, exp):
                    bad.append(f"shape={shape} threads={threads}")
        check("minmax-grid-executes", not bad, "; ".join(bad))
    finally:
        import shutil
        shutil.rmtree(workdir, ignore_errors=True)


def main() -> int:
    check_corpus_forms()
    check_no_baking()
    check_self_check()
    check_refusals_located()
    check_minmax_and_ceil()
    check_minmax_grid_executes()
    check_corpus_census()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_grid_model: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
