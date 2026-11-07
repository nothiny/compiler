#!/usr/bin/env python3
"""test_t037_repairs.py -- the T037 grid-tie repair classes (the final 22
census residual rows), each through the real path (compile -> native
execution -> comparison under the case's own policy), with the controls
that prove the checks are load-bearing.

  * aligned-copy extents (chunk_abc, 6 identities): ``_aligned``'s
    ``return result.reshape(values.shape)`` over an opaque base now yields
    the argument's extents, so the views the case builds from the shape
    carry their per-axis provenance -- the B*H grid axis becomes ONE
    runtime view read (A[0]) instead of an untied shape leaf.  Both
    declared shapes execute and compare PASS at 1 and 4 workers.
  * lambda value-massaging + config-read memoization (deconv3d, 6
    identities): ``q = lambda *s, r=2: ...`` keeps its extents through
    the rng/rint/astype chain, and the repeated ``cfg[...]`` reads are
    one value, so the quotient solve reads the n factor as
    ``x_ptr[0] // (Cin*Dz*Dy*Dx)`` over bundle scalars.  The degenerate
    shape (1, 1, 1, 1, 1) executes and compares PASS at 1 and 4 workers;
    the typical shape (1, 4, 8, 8, 8) now COMPILES and its first
    execution exposes a NEW post-grid compute defect (pinned below as
    the next repair round's input -- not a grid defect: the tile tail is
    intact and the self-check binds modeled == declared).
  * the identity-signed trip count (grouped_mm, 6 identities): the
    tile-count loop's ``range(num_groups)`` bound is a case-shape axis
    the identity SIGNS (meta num_groups), so the loop unrolls its
    structure while the accumulated expression reads the M scalar and
    the offs[0] view extent at run time.  Both declared shapes execute
    and compare PASS at 1 and 4 workers.
  * the genuinely untraceable keep located refusals that NAME the
    untraceable input: gn_finalize's (n, g) axes (only their product is
    view-visible -- the refusal names the axis and the product), and
    grouped_gemm's runtime-length tile-count sum (its single identity
    spans groups=3 and groups=4 cases, so the trip count is per-case
    data; the refusal names the unsigned case-shape axis).
  * the recorded NEW defect: deconv3d's typical case compiles through
    the repaired grid and its execution mismatch (per-lane ox == 3 mod
    4, worker-count-dependent) is pinned with the control that
    attributes it away from the grid (the tile tail intact, the
    degenerate shape PASS) -- the input of the next repair round.

Controls (MECH-WITNESS-TEST):
  * the signed-count gate: a probe operator whose loop bound is an
    UNSIGNED case-shape axis never unrolls (a located refusal naming the
    axis -- unrolling it would bake one case's loop shape), while the
    same loop over a SIGNED axis extracts and executes;
  * the no-baking spot check (acceptance[1]): the probe's two shapes
    share ONE identity and differ only in the runtime m the grid routine
    reads (one artifact computes grid 3 for m=40 and 6 for m=70 -- a
    baked m would fail the pinned program-count comparison), and
    add_base_max's two shapes cold-compile to bit-identical artifacts
    (the grid is a pure view read);
  * the self-check control: a tampered declared grid refuses loudly;
  * the model-level Lit audit: no axis literal carries a shape value the
    identity does not sign.

Run: python3 a100c/tests/test_t037_repairs.py  (exit 0 = all checks PASS)
"""
from __future__ import annotations

import importlib.util
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
from a100c.frontend import source as fe_source  # noqa: E402
from a100c.frontend.gridmodel import (  # noqa: E402
    Bin, GridError, Lit, MinMax, extract_grid)
from a100c.passes import pipeline as passes_mod  # noqa: E402

OPS = ROOT / "ops"
WORK = Path(tempfile.mkdtemp(prefix="a100c-t037-"))


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_source(rel: str):
    return fe_source.load_operator(str(OPS / rel), corpus_root=str(OPS))


def _run_case(compiler, module, threads, **make_kwargs):
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
        if got.shape != exp.shape and got.size == exp.size:
            got = got.reshape(exp.shape)
        if policy.get("exact") or policy["comparator"] == "array_equal":
            same = np.array_equal(got, exp)
        else:
            same = np.allclose(got, exp, rtol=policy.get("rtol", 0.0),
                               atol=policy.get("atol", 0.0),
                               equal_nan=policy.get("equal_nan", False))
        if not same:
            detail = f"{name}: {int(np.sum(got != exp))} mismatched elements"
        ok &= same
    return ok, detail


def _compiler(tag: str) -> FactoryCompiler:
    return FactoryCompiler(
        options=CompileOptions(cache_dir=str(WORK / f"cache-{tag}")),
        pass_config=passes_mod.PassConfig())


def _lits(expr, out):
    if isinstance(expr, Lit):
        out.append(expr.value)
    elif isinstance(expr, (Bin, MinMax)):
        _lits(expr.left, out)
        _lits(expr.right, out)
    return out


def _signed_values(case) -> set:
    out = set()
    for table in ("meta", "launch_meta"):
        for value in (case.get(table) or {}).values():
            if isinstance(value, int) and not isinstance(value, bool):
                out.add(value)
    return out


# ---------------------------------------------------------------------------
# the repaired extraction classes
# ---------------------------------------------------------------------------

def check_t037_grid_ties():
    """chunk_abc / deconv3d / grouped_mm extract at every declared
    (shape, dtype) with a passing self-check, and every axis is a runtime
    bundle read (never a baked shape value)."""
    bad = []

    # chunk_abc: the aligned views carry extents; the B*H axis is ONE view
    # read and every other axis reads bundle quantities
    module = _load(OPS / "suite" / "dev" / "chunk_abc_fwd_kernel_intra_K.py")
    for shape in ((2, 2, 17, 9, 8, 4), (1, 3, 33, 13, 16, 4)):
        for dtype in ("float32", "float16", "bfloat16"):
            case = module.make_case(shape=shape, dtype=dtype)
            try:
                model = extract_grid(_load_source(
                    "suite/dev/chunk_abc_fwd_kernel_intra_K.py"), case)
            except GridError as exc:
                bad.append(f"chunk_abc {shape} {dtype}: {str(exc)[:90]}")
                continue
            if model.self_check.get("modeled") != \
                    model.self_check.get("declared"):
                bad.append(f"chunk_abc {shape} {dtype}: self-check")
            if repr(model.axes[2]) != "$bundle_view('A', 0)":
                bad.append(f"chunk_abc {shape} {dtype}: axis 2 is "
                           f"{model.axes[2]!r}, not the A[0] view read")

    # deconv3d: the lambda-massaged x carries its extents; the n axis is
    # the quotient view read over the Cin/Dz/Dy/Dx bundle scalars
    module = _load(OPS / "suite" / "dev" / "deconv3d_fwd_kernel.py")
    for shape in ((1, 4, 8, 8, 8), (1, 1, 1, 1, 1)):
        for dtype in ("float32", "float16", "bfloat16"):
            case = module.make_case(shape=shape, dtype=dtype)
            try:
                model = extract_grid(_load_source(
                    "suite/dev/deconv3d_fwd_kernel.py"), case)
            except GridError as exc:
                bad.append(f"deconv3d {shape} {dtype}: {str(exc)[:90]}")
                continue
            if model.self_check.get("modeled") != \
                    model.self_check.get("declared"):
                bad.append(f"deconv3d {shape} {dtype}: self-check")
            axis2 = repr(model.axes[2])
            if "bundle_view('x_ptr', 0)" not in axis2 or \
                    "floordiv" not in axis2 or \
                    "bundle_scalar('Cin'" not in axis2:
                bad.append(f"deconv3d {shape} {dtype}: axis 2 is "
                           f"{axis2[:80]}, not the x_ptr[0] quotient over "
                           "the Cin/Dz/Dy/Dx scalars")

    # grouped_mm: the identity-signed trip count unrolls the tile-count
    # loop; the accumulated chain reads the M scalar per group term and
    # the offs[0] view extent (the term count equals meta num_groups)
    module = _load(OPS / "suite" / "dev" / "grouped_mm_kernel.py")
    for shape in ((3, 23, 19, 17), (4, 67, 35, 29)):
        for dtype in ("bfloat16", "float32", "float16"):
            case = module.make_case(shape=shape, dtype=dtype)
            try:
                model = extract_grid(_load_source(
                    "suite/dev/grouped_mm_kernel.py"), case)
            except GridError as exc:
                bad.append(f"grouped_mm {shape} {dtype}: {str(exc)[:90]}")
                continue
            if model.self_check.get("modeled") != \
                    model.self_check.get("declared"):
                bad.append(f"grouped_mm {shape} {dtype}: self-check")
            axis = repr(model.axes[0])
            groups = int(case["meta"]["num_groups"])
            # one M read in the first term (start = 0), two in each later
            # term (end_g - end_{g-1}): 2*groups - 1 runtime M reads
            if axis.count("$bundle_scalar('M',)") != 2 * groups - 1:
                bad.append(f"grouped_mm {shape} {dtype}: the axis does not "
                           f"carry {2 * groups - 1} per-group M reads")
            if model.ties.get((0,)) != ("view_extent", "offs", 0):
                bad.append(f"grouped_mm {shape} {dtype}: the shape axis "
                           f"does not tie to the offs[0] view extent "
                           f"(ties={model.ties})")
            # no baking: no axis literal carries a shape value the
            # identity does not sign (m is unsigned; num_groups/N/K are
            # meta-signed)
            signed = _signed_values(case)
            unsigned = {v for v in shape if v not in signed}
            lits = _lits(model.axes[0], [])
            baked = [v for v in unsigned if v in lits]
            if baked:
                bad.append(f"grouped_mm {shape} {dtype}: axis literal "
                           f"carries the unsigned shape value {baked}")
    check("t037-grid-ties-extract-with-runtime-reads", not bad,
          "; ".join(bad[:3]))


# ---------------------------------------------------------------------------
# the genuinely untraceable keep located refusals naming the input
# ---------------------------------------------------------------------------

def check_t037_located_refusals():
    bad = []
    module = _load(OPS / "suite" / "dev" / "gn_finalize_kernel.py")
    try:
        extract_grid(_load_source("suite/dev/gn_finalize_kernel.py"),
                     module.make_case())
        bad.append("gn_finalize accepted")
    except GridError as exc:
        if "cannot be proven equal" not in str(exc) \
                or "shape_extent" not in str(exc) \
                or "only as a factor of a view extent" not in str(exc) \
                or not exc.line:
            bad.append(f"gn_finalize: {str(exc)[:110]}")
    module = _load(OPS / "suite" / "dev" / "grouped_gemm_kernel.py")
    try:
        extract_grid(_load_source("suite/dev/grouped_gemm_kernel.py"),
                     module.make_case())
        bad.append("grouped_gemm accepted")
    except GridError as exc:
        if "not provenance-tracked" not in str(exc) \
                or "no identity-signed count" not in str(exc) \
                or "shape_extent" not in str(exc) or not exc.line:
            bad.append(f"grouped_gemm: {str(exc)[:110]}")
    # the pipeline surfaces the same refusals located (the compile-time
    # boundary)
    c = _compiler("refusals")
    for opname, needle in (("gn_finalize_kernel.py",
                            "only as a factor of a view extent"),
                           ("grouped_gemm_kernel.py",
                            "no identity-signed count")):
        module = _load(OPS / "suite" / "dev" / opname)
        try:
            c.compile_case(
                {k: v for k, v in module.make_case().items()
                 if k not in ("expected", "oracle_args")})
            bad.append(f"{opname}: compiled (expected a located refusal)")
        except PipelineError as exc:
            if exc.construct != "grid" or needle not in str(exc):
                bad.append(f"{opname}: {str(exc)[:110]}")
        except Exception as exc:               # noqa: BLE001
            bad.append(f"{opname}: wrong error {type(exc).__name__}")
    check("t037-untraceable-refuse-located-naming-input", not bad,
          "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# executed comparison through the real pipeline
# ---------------------------------------------------------------------------

def check_t037_execute_compare():
    c = _compiler("exec")
    bad = []
    plan = [
        ("suite/dev/chunk_abc_fwd_kernel_intra_K.py",
         (2, 2, 17, 9, 8, 4), "float32"),
        ("suite/dev/chunk_abc_fwd_kernel_intra_K.py",
         (1, 3, 33, 13, 16, 4), "float32"),
        ("suite/dev/chunk_abc_fwd_kernel_intra_K.py",
         (2, 2, 17, 9, 8, 4), "float16"),
        ("suite/dev/deconv3d_fwd_kernel.py", (1, 1, 1, 1, 1), "float32"),
        ("suite/dev/grouped_mm_kernel.py", (3, 23, 19, 17), "float32"),
        ("suite/dev/grouped_mm_kernel.py", (4, 67, 35, 29), "float32"),
    ]
    for rel, shape, dtype in plan:
        module = _load(OPS / rel)
        for threads in (1, 4):
            ok, detail = _run_case(c, module, threads, shape=shape,
                                   dtype=dtype)
            if not ok:
                bad.append(f"{rel.split('/')[-1]} {shape} {dtype} "
                           f"t={threads}: {detail}")
    check("t037-repaired-grids-execute-and-compare", not bad,
          "; ".join(bad[:2]))


def check_t037_deconv3d_new_defect_recorded():
    """deconv3d's typical case (1, 4, 8, 8, 8): the T037 grid repair
    unblocked it through the grid model (it extracts, self-checked, and
    compiles to an artifact), and the FIRST execution through the rest of
    the pipeline exposes a NEW compute defect this pins for the next
    repair round: a deterministic per-lane mismatch (every ox == 3 mod 4
    across all cout/oz/oy, ~435 of 11520 elements at 1 worker, count
    varying with the worker count).  The control attributes it AWAY from
    the grid: the grid axis-0 tile tail ([1408, 1440) of the 1440-wide
    flattened (oz, oy, ox) space) is NOT fully mismatched -- a missing or
    wrong grid tile would leave that whole region unwritten -- and the
    degenerate shape (1, 1, 1, 1, 1) with the same tie structure
    executes and compares PASS.  When the deeper defect is repaired this
    pin flips to a full comparison PASS."""
    import a100_support.native_device as nd
    import sys as _sys
    _sys.path.insert(0, str(ROOT / "tools"))
    import run_scan as rs  # noqa: E402
    bad = []
    c = _compiler("deconv-heavy")
    op = "suite/dev/deconv3d_fwd_kernel.py"
    rows = [r for r in rs.enumerated_rows(
        "ops/suite/manifest.json", operators=[op])
        if tuple(r["shape"]) == (1, 4, 8, 8, 8) and r["dtype"] == "float32"]
    case = rs.build_case(rows[0], 30, use_golden=True)
    payload = {k: v for k, v in case.items()
               if k not in ("expected", "oracle_args")}
    try:
        art = c.compile_case(payload)
    except PipelineError as exc:
        check("t037-deconv3d-typical-case-new-defect-recorded", False,
              f"compile refused at {exc.construct!r}: {str(exc)[:90]}")
        return
    counts = {}
    for threads in (1, 4):
        device = nd.NativeExecutableDevice(c, threads)
        staged = device.stage_case(case)
        staged.launch()
        got = np.asarray(staged.outputs()["y_ptr"])
        exp = np.asarray(case["expected"]["y_ptr"])
        mm = (got.reshape(exp.shape) != exp.reshape(exp.shape))
        counts[threads] = int(mm.sum())
        # the control: NOT a grid-tile miss (the flattened (oz,oy,ox)
        # tail tile [1408, 1440) must not be fully unwritten)
        y = got.reshape(1, 8, 10, 12, 12)
        e = exp.reshape(1, 8, 10, 12, 12)
        flat = (y != e)[0].sum(axis=0).reshape(-1)
        tail = flat[1408:1440]
        if (tail > 0).all():
            bad.append(f"t={threads}: the tail tile is fully mismatched "
                       "(a grid-tile miss -- the grid model is implicated)")
        if counts[threads] == 0:
            bad.append(f"t={threads}: comparison PASS -- the recorded "
                       "compute defect is gone; update this pin to a full "
                       "comparison PASS")
    check("t037-deconv3d-typical-case-new-defect-recorded",
          not bad and all(v > 0 for v in counts.values()),
          f"artifact {Path(art.executable).name}; mismatches "
          f"t=1: {counts.get(1)}, t=4: {counts.get(4)} of 11520 "
          "(per-lane ox==3 mod 4; the grid tile tail is intact)")


# ---------------------------------------------------------------------------
# the no-baking spot check (acceptance[1]) and its controls
# ---------------------------------------------------------------------------

PROBE_TEXT = '''"""probe operator t037probe (T037: the identity-signed trip count)"""
OPERATOR = {"name": "probe/t037probe", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}
SHAPES = ((3, 40), (3, 70))
import numpy as np
import triton
import triton.language as tl


@triton.jit
def t037probe_kernel(x_ptr, out_ptr, nprog_ptr, m, BLOCK: tl.constexpr):
    pid = tl.program_id(0)
    if pid == 0:
        tl.store(nprog_ptr, tl.num_programs(0).to(tl.int32))
    i = pid * BLOCK + tl.arange(0, BLOCK)
    mask = i < m
    v = tl.load(x_ptr + i, mask=mask, other=0)
    tl.store(out_ptr + i, v + 1, mask=mask)


def _aligned(values, dtype="int32", alignment=64):
    import numpy as np

    values = np.asarray(values, dtype=np.dtype(dtype))
    raw = np.empty(values.size * values.dtype.itemsize + alignment, dtype=np.uint8)
    start = -raw.ctypes.data % alignment
    result = raw[start : start + values.size * values.dtype.itemsize].view(values.dtype)
    result[...] = values.reshape(-1)
    return result.reshape(values.shape)


def ref(args, meta):
    return {"out_ptr": (args["x_ptr"] + 1).astype(np.int32),
            "nprog_ptr": np.array([args["grid"][0]], np.int32)}


def _make_case(shape=SHAPES[0], dtype="int32", seed=0):
    groups, m = (int(v) for v in shape)
    rng = np.random.default_rng(seed)
    q = lambda *s: rng.integers(1, 100, s).astype(np.int32)
    x = _aligned(q(m))
    ends = np.asarray([m * (group + 1) // groups for group in range(groups)],
                      dtype=np.int32)
    total = 0
    start = 0
    for end in ends:
        rows = int(end) - start
        total += (rows + 15) // 16
        start = int(end)
    args = {"x_ptr": x, "out_ptr": _aligned(np.zeros(m, np.int32)),
            "nprog_ptr": _aligned(np.zeros(1, np.int32)), "m": m}
    meta = {"BLOCK": 16, "groups": groups}
    grid = (total,)
    return {"kernel": t037probe_kernel, "args": args, "meta": meta,
            "grid": grid,
            "outputs": ("out_ptr", "nprog_ptr"),
            "expected": ref({"x_ptr": np.asarray(x).reshape(-1),
                              "grid": grid}, meta),
            "comparison": {"out_ptr": {"comparator": "array_equal",
                                        "exact": True},
                            "nprog_ptr": {"comparator": "array_equal",
                                          "exact": True}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or SHAPES[0])
'''


def check_t037_no_baking():
    """acceptance[1]: no grid value is baked.  The probe's two shapes
    (3, 40) and (3, 70) share ONE identity (the meta and the scalar
    classes agree); the second compile is a cache hit on the very same
    artifact, and the pinned program-count comparison (nprog_ptr) holds
    3 for m=40 and 6 for m=70 -- the grid differs across the two runs
    only through the runtime bundle reads.  add_base_max's two shapes
    cold-compile (isolated caches) to bit-identical artifacts (the grid
    is a pure view read).  The control: the same loop over an UNSIGNED
    case-shape axis refuses located (never unrolled, nothing baked)."""
    import shutil
    workdir = WORK / "probe"
    workdir.mkdir(parents=True, exist_ok=True)
    bad = []
    try:
        path = workdir / "t037probe.py"
        path.write_text(PROBE_TEXT)
        spec = importlib.util.spec_from_file_location("t037probe", str(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        src = fe_source.load_operator(str(path))

        # both shapes extract; the axis reads the runtime m per term and
        # the term count is the meta-signed groups (3) -- identical across
        # the two shapes of one identity
        for shape in ((3, 40), (3, 70)):
            case = module.make_case(shape=shape)
            model = extract_grid(src, case)
            if model.self_check.get("modeled") != \
                    model.self_check.get("declared"):
                bad.append(f"probe {shape}: self-check {model.self_check}")
            if repr(model.axes[0]).count("$bundle_scalar('m',)") != 5:
                bad.append(f"probe {shape}: the axis does not carry 5 "
                           "per-term m reads (2*groups-1)")

        # one identity, two shapes: the second compile is a cache hit on
        # the same artifact, and both runs compare PASS (the runtime grid
        # follows the bundle: 3 for m=40, 6 for m=70)
        import a100_support.native_device as nd
        c = _compiler("probe")
        expected_grids = {(3, 40): 3, (3, 70): 6}
        hits = {}
        for shape, want in expected_grids.items():
            case = module.make_case(shape=shape)
            art = c.compile_case(
                {k: v for k, v in case.items()
                 if k not in ("expected", "oracle_args")})
            hits[shape] = art
            device = nd.NativeExecutableDevice(c, 4)
            staged = device.stage_case(case)
            staged.launch()
            outputs = staged.outputs()
            got = int(np.asarray(outputs["nprog_ptr"]).reshape(-1)[0])
            if got != want:
                bad.append(f"probe {shape}: runtime program count {got} "
                           f"!= {want} (a baked m would freeze one value)")
            if not np.array_equal(np.asarray(outputs["out_ptr"]),
                                  np.asarray(case["expected"]["out_ptr"])):
                bad.append(f"probe {shape}: out_ptr mismatch")
        if not hits[(3, 70)].cache_hit:
            bad.append("probe: the second shape did not reuse the first "
                       "shape's artifact (they must share one identity)")
        if hits[(3, 40)].sha256 != hits[(3, 70)].sha256:
            bad.append("probe: the two shapes produced different artifacts")

        # the control (MECH-WITNESS-TEST): the same loop over an UNSIGNED
        # case-shape axis (meta does not sign it) refuses located, naming
        # the axis -- the unroll is gated on the identity signature
        control = PROBE_TEXT.replace(
            'meta = {"BLOCK": 16, "groups": groups}',
            'meta = {"BLOCK": 16}')
        cpath = workdir / "t037probe_unsigned.py"
        cpath.write_text(control)
        cspec = importlib.util.spec_from_file_location(
            "t037probe_unsigned", str(cpath))
        cmodule = importlib.util.module_from_spec(cspec)
        cspec.loader.exec_module(cmodule)
        csrc = fe_source.load_operator(str(cpath))
        try:
            extract_grid(csrc, cmodule.make_case(shape=(3, 40)))
            bad.append("unsigned control: accepted (the unroll must be "
                       "gated on the identity-signed count)")
        except GridError as exc:
            if "no identity-signed count" not in str(exc) \
                    or "shape_extent" not in str(exc):
                bad.append(f"unsigned control: {str(exc)[:110]}")

        # the self-check control: a tampered declared grid refuses loudly
        case = module.make_case(shape=(3, 40))
        tampered = dict(case, grid=(7,))
        try:
            extract_grid(src, tampered)
            bad.append("tampered declared grid accepted")
        except GridError as exc:
            if "self-check failed" not in str(exc):
                bad.append(f"tampered: {str(exc)[:90]}")
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    # add_base_max: two shapes of ONE identity cold-compile (isolated
    # caches) to bit-identical artifacts -- the grid is a pure view read,
    # so the two shapes' runs differ only in the bundle each reads
    module = _load(OPS / "suite" / "dev" / "add_base_max_kernel.py")
    shas = []
    for shape in ((17,), (97,)):
        cc = FactoryCompiler(
            options=CompileOptions(cache_dir=str(
                WORK / f"cold-{shape[0]}")),
            pass_config=passes_mod.PassConfig())
        case = module.make_case(shape=shape)
        art = cc.compile_case(
            {k: v for k, v in case.items()
             if k not in ("expected", "oracle_args")})
        shas.append(art.sha256)
    if shas[0] != shas[1]:
        bad.append(f"add_base_max: cold artifacts differ {shas}")
    c = _compiler("abm")
    for shape in ((17,), (97,)):
        for threads in (1, 4):
            ok, detail = _run_case(c, module, threads, shape=shape)
            if not ok:
                bad.append(f"add_base_max {shape} t={threads}: {detail}")
    check("t037-no-baking-two-shapes-one-identity", not bad,
          "; ".join(bad[:2]))


def main():
    check_t037_grid_ties()
    check_t037_located_refusals()
    check_t037_execute_compare()
    check_t037_deconv3d_new_defect_recorded()
    check_t037_no_baking()
    if FAILURES:
        print(f"\nFAILED: {len(FAILURES)} check(s): {FAILURES}")
        return 1
    print("\ntest_t037_repairs: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
