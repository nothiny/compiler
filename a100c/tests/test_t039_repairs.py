#!/usr/bin/env python3
"""test_t039_repairs.py -- the T039 pre-scan blocker repairs, each through
the real path (compile -> native execution -> comparison under the case's
own policy), with the controls that prove the checks are load-bearing.

  * the 4 genuinely untraceable grid refusals are REPAIRED inside the
    declared launch contract (the bundle keeps carrying views and
    scalars; the grid routine keeps evaluating natively -- no launch
    protocol change, no DESIGN_ISSUE needed):
      - gn_finalize's (n, g) axes are visible only as the view product
        n*g, but the kernel's whole program-id surface is the C-order
        linear index ``pid_n * num_programs(1) + pid_g`` -- the grid
        flattens to ONE axis over the product (the re-partition the
        recorded execution-model policy allows; the (pid_n, pid_g) ->
        linear bijection is the proof) and the TIR's linear expression
        rewrites to ``program_id(0)`` before the MIR lowering.  All
        three declared shapes execute and compare PASS at 1 and 4
        workers.
      - grouped_gemm's tile-count ``sum(cdiv(M+2g, BM) * cdiv(N+3g, BN)
        for g in range(groups))`` iterates an UNSIGNED case-shape axis
        whose single identity spans groups=3 and groups=4 -- but the
        count IS the bundle-visible ``group_size`` scalar, so the grid
        expression keeps a runtime SumLoop over the actual scalar read
        (neither count is unrolled into the structure).  Both declared
        shapes execute and compare PASS at 1 and 4 workers.  The repair
        also exposed and fixed the next blocker on that path: a 64-bit
        unsigned scalar load emitted a ``zext`` sload the repertoire has
        no row for (a 64-bit load's extension is vacuous -- ld loads all
        64 bits; the entry binding already carried that rule).
  * the deconv3d typical-case compute defect: the [1]-element staged
    records (``tl.full([1], ...)`` values like ``Oy_i64 * Ox_i64``) were
    stored and read with the raw ``(elem + lane)`` index -- one element
    is allocated, but each consumer pass wrote/ read ``vl`` lanes at the
    pass position, smashing the neighbouring staged regions (the [128]
    div/mod decomposition lanes corrupted at ``ow % 4 == 3``: the
    recomposition ``oz*(Oy*Ox)`` read the smashed product back as ``Ox``
    -- every corpus shape has Oy == Ox, so the wrong value coincided
    with a legal-looking factor).  Extent-1 records now stage element 0
    from every lane (the register is the value's splat -- the duplicate
    index writes the same element).  The minimized reproduction (the
    div/mod decomposition + the [16,1]+[1,128] broadcast store, with
    Oy != Ox so the wrong factor is distinguishable) executes and
    compares PASS; the degenerate and typical deconv3d shapes PASS at
    1 and 4 workers.
  * the gqa 1-worker CSE segfault: the ptradd lowering materialized a
    staged BASE block through ``_need(base)`` with no consumer shape --
    a staged [32, 1] base consumed by a [32, 32] ptradd read its region
    with the raw identity index while the [32, 32] consumer pass's
    element counter ran past the base's 32-element extent (T029 fixed
    the OFFSET side; the base side was missed).  The staged base read
    now maps through the result's shape exactly like the offsets.  gqa
    executes and compares PASS at 1, 2, 4 and 8 workers with the passes
    enabled AND with them off (the CSE merge that exposed the defect --
    the shared masked-load ``other`` broadcast -- is value-legal; the
    defect was the mis-shaped read, not the rewrite).
  * the fp64 tl.dot refusal's justification is verified recorded: the
    FRONTEND_COVERAGE tl.dot row carries the T038 dtype-surface boundary
    note naming the corpus declaration (CORPUS_LOCK.json's per-operator
    dtypes and the global declared set, no float64 anywhere), so the
    refusal reads as declared-unsupported with evidence.

Controls (MECH-WITNESS-TEST):
  * the flattening gate: a probe kernel whose program-id surface uses an
    axis OUTSIDE the linear expression keeps the located per-axis
    refusal (the flattening must not fire -- the axis factors cannot be
    reconstructed from the linear index);
  * the SumLoop gate: a probe whose sum iterates a range bound the
    model cannot read keeps the located refusal naming the bound;
  * the no-baking spot check: gn_finalize's two shapes of one identity
    share one artifact and the runtime program count follows the bundle
    (the flat axis reads the view extent: 1024 for (128, 8), 21 for
    (7, 3) -- a baked geometry would freeze one value).

Run: python3 a100c/tests/test_t039_repairs.py  (exit 0 = all checks PASS)
"""
from __future__ import annotations

import importlib.util
import json
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
from a100c.frontend import gridmodel  # noqa: E402
from a100c.frontend import lower_tir  # noqa: E402
from a100c.frontend import specialize as fe_spec  # noqa: E402
from a100c.passes import pipeline as passes_mod  # noqa: E402

OPS = ROOT / "ops"
WORK = Path(tempfile.mkdtemp(prefix="a100c-t039-"))


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_source(rel: str):
    return fe_source.load_operator(str(OPS / rel), corpus_root=str(OPS))


def _compiler(tag: str, pass_config=None) -> FactoryCompiler:
    return FactoryCompiler(
        options=CompileOptions(cache_dir=str(WORK / f"cache-{tag}")),
        pass_config=pass_config or passes_mod.PassConfig())


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


def _tir_of(rel: str, case: dict):
    src = _load_source(rel)
    spec = fe_spec.specialize(src, case)
    return lower_tir.lower(src, spec)


# ---------------------------------------------------------------------------
# acceptance[0]: the four untraceable grid refusals, repaired
# ---------------------------------------------------------------------------

def check_gn_finalize_flattening():
    """gn_finalize's (n, g) axes flatten to the view product: the model
    is one axis reading gsum_ptr[0], the self-check binds the modeled
    product to the declared grid's product, the TIR's linear pid
    expression rewrites to program_id(0), and every declared shape
    executes and compares PASS at 1 and 4 workers."""
    bad = []
    src = _load_source("suite/dev/gn_finalize_kernel.py")
    module = _load(OPS / "suite" / "dev" / "gn_finalize_kernel.py")
    for shape in ((128, 8), (7, 3), (1, 1)):
        case = module.make_case(shape=shape)
        tir = _tir_of("suite/dev/gn_finalize_kernel.py", case)
        model = gridmodel.extract_grid(src, case, tir_module=tir)
        if model.linear_ndim != 2 or model.ndim != 1:
            bad.append(f"{shape}: not a linear flattening "
                       f"(ndim={model.ndim}, linear={model.linear_ndim})")
        if repr(model.axes[0]) != "$bundle_view('gsum_ptr', 0)":
            bad.append(f"{shape}: axis is {model.axes[0]!r}")
        want = int(np.prod(case["grid"]))
        if model.self_check.get("declared_product") != want:
            bad.append(f"{shape}: self-check {model.self_check}")
        # the flattening rewrite: the linear expression is gone, exactly
        # one program_id(0) remains, and the TIR still verifies
        if not gridmodel.apply_linear_flattening(tir, 2):
            bad.append(f"{shape}: flattening did not apply")
        from a100c.ir import tir as tir_mod
        errors = tir_mod.verify_module(tir)
        if errors:
            bad.append(f"{shape}: verify after flatten {errors[0]}")
        pids = [op.attrs.get("axis") for op in _tir_ops(tir)
                if op.op == "program_id"]
        if pids != [0]:
            bad.append(f"{shape}: pid surface after rewrite {pids}")
        nps = [op.attrs.get("axis") for op in _tir_ops(tir)
               if op.op == "num_programs"]
        if nps:
            bad.append(f"{shape}: num_programs survived {nps}")
    c = _compiler("gn")
    for shape in ((128, 8), (7, 3), (1, 1)):
        for threads in (1, 4):
            ok, detail = _run_case(c, module, threads, shape=shape)
            if not ok:
                bad.append(f"{shape} t={threads}: {detail}")
    check("t039-gn-finalize-linear-flattening", not bad,
          "; ".join(bad[:2]) if bad else
          "(n,g)->n*g over the view extent; 3 shapes PASS at 1/4 workers")


def _tir_ops(module):
    from a100c.ir import tir as _tir
    out = []

    def walk(blk):
        for st in blk.statements:
            if isinstance(st, _tir.Op):
                out.append(st)
            elif isinstance(st, _tir.If):
                walk(st.then)
                walk(st.els)
            elif isinstance(st, _tir.Loop):
                walk(st.body)

    for fn in module.functions:
        walk(fn.body)
    return out


FLATTEN_GATE_TEXT = '''\
OPERATOR = {"name": "t039/flatten-gate", "group": "basic", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.program_id.nd"]}
import numpy as np
import triton
import triton.language as tl


@triton.jit
def gate_kernel(a_ptr, b_ptr):
    pid_n = tl.program_id(0)
    pid_g = tl.program_id(1)
    idx = pid_n * tl.num_programs(1) + pid_g
    # a use of pid_g OUTSIDE the linear expression: the flattening must
    # not fire (the axis factors cannot be reconstructed from the
    # linear index)
    v = tl.load(a_ptr + idx) + tl.load(b_ptr + pid_g)
    tl.store(b_ptr + idx, v)


def ref(args, meta):
    a = np.asarray(args["a_ptr"], dtype=np.float64)
    b = np.asarray(args["b_ptr"], dtype=np.float64)
    n, g = meta["shape"]
    out = np.zeros(n * g)
    for i in range(n * g):
        out[i] = a[i] + b[i % g]
    return {"b_ptr": out.astype(np.asarray(args["b_ptr"]).dtype)}


def _make_case(shape=(4, 3), dtype="float32", seed=0):
    n, g = (int(v) for v in shape)
    rng = np.random.default_rng(seed)
    args = {"a_ptr": rng.standard_normal(n * g).astype(np.float32),
            "b_ptr": np.zeros(n * g, np.float32)}
    meta = {"shape": (n, g)}
    return {"kernel": gate_kernel, "grid": (n, g), "args": args,
            "meta": meta, "outputs": ("b_ptr",), "shape": tuple(shape),
            "dtype": "float32", "expected": ref(args, meta),
            "comparison": {"b_ptr": {"comparator": "array_equal",
                                     "exact": True}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or (4, 3), dtype=dtype, seed=seed)
'''


def check_flattening_gate():
    """The control (MECH-WITNESS-TEST): a kernel whose program-id surface
    uses an axis outside the C-order linear expression keeps the located
    per-axis refusal -- the flattening must not fire."""
    bad = []
    workdir = WORK / "gate"
    workdir.mkdir(parents=True, exist_ok=True)
    path = workdir / "gate.py"
    path.write_text(FLATTEN_GATE_TEXT)
    spec = importlib.util.spec_from_file_location("gate", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    src = fe_source.load_operator(str(path))
    case = module.make_case()
    tir = _tir_of_case(src, case)
    try:
        gridmodel.extract_grid(src, case, tir_module=tir)
        bad.append("accepted (the flattening must not fire when an axis "
                   "is used outside the linear expression)")
    except gridmodel.GridError as exc:
        if "cannot be proven equal" not in str(exc) \
                or "only as a factor of a view extent" not in str(exc):
            bad.append(f"wrong refusal: {str(exc)[:110]}")
    # the same kernel without the outside use flattens and executes
    fixed = FLATTEN_GATE_TEXT.replace(
        "v = tl.load(a_ptr + idx) + tl.load(b_ptr + pid_g)",
        "v = tl.load(a_ptr + idx)")
    fpath = workdir / "gate_fixed.py"
    fpath.write_text(fixed)
    fspec = importlib.util.spec_from_file_location("gate_fixed", str(fpath))
    fmodule = importlib.util.module_from_spec(fspec)
    fspec.loader.exec_module(fmodule)
    fsrc = fe_source.load_operator(str(fpath))
    fcase = fmodule.make_case()
    ftir = _tir_of_case(fsrc, fcase)
    model = gridmodel.extract_grid(fsrc, fcase, tir_module=ftir)
    if model.linear_ndim != 2:
        bad.append(f"fixed probe did not flatten: {model.describe()}")
    check("t039-flattening-gate-pid-use-outside-linear", not bad,
          "; ".join(bad[:2]) if bad else
          "outside-use refuses located; pure-linear flattens")


def _tir_of_case(src, case: dict):
    spec = fe_spec.specialize(src, case)
    return lower_tir.lower(src, spec)


def check_grouped_gemm_sumloop():
    """grouped_gemm's tile-count sum lowers as a runtime SumLoop over the
    bundle-visible ``group_size`` scalar (one identity spans groups=3 and
    groups=4 -- neither count is unrolled), and both declared shapes
    execute and compare PASS at 1 and 4 workers."""
    bad = []
    src = _load_source("suite/dev/grouped_gemm_kernel.py")
    module = _load(OPS / "suite" / "dev" / "grouped_gemm_kernel.py")
    for shape, want in (((3, 17, 19, 13), 12), ((4, 33, 35, 21), 36)):
        case = module.make_case(shape=shape)
        model = gridmodel.extract_grid(src, case)
        axis = model.axes[0]
        if not isinstance(axis, gridmodel.SumLoop):
            bad.append(f"{shape}: axis is {axis!r}")
            continue
        if repr(axis.count) != "$bundle_scalar('group_size',)":
            bad.append(f"{shape}: count is {axis.count!r}")
        if model.self_check.get("modeled") != [want] \
                or model.self_check.get("declared") != [want]:
            bad.append(f"{shape}: self-check {model.self_check}")
    c = _compiler("gg")
    for shape in ((3, 17, 19, 13), (4, 33, 35, 21)):
        for threads in (1, 4):
            ok, detail = _run_case(c, module, threads, shape=shape)
            if not ok:
                bad.append(f"{shape} t={threads}: {detail}")
    check("t039-grouped-gemm-runtime-sumloop", not bad,
          "; ".join(bad[:2]) if bad else
          "sum(cdiv(M+2g,16)*cdiv(N+3g,16), g<group_size); "
          "both shapes PASS at 1/4 workers")


SUM_GATE_TEXT = '''\
OPERATOR = {"name": "t039/sum-gate", "group": "basic", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.program_id.0d"]}
import numpy as np
import triton
import triton.language as tl


@triton.jit
def sumgate_kernel(y_ptr):
    pid = tl.program_id(0)
    tl.store(y_ptr + pid, tl.full([1], 1, tl.float32))


def ref(args, meta):
    total = int(np.asarray(args["y_ptr"]).size)
    return {"y_ptr": np.ones(total, np.float32)}


def _make_case(shape=(3,), dtype="float32", seed=0):
    # the grid is a sum over an iterable the model cannot see (an
    # imported helper's call result -- no scalar argument and no view
    # extent carries it): the SumLoop must refuse, not guess
    from case_utils import fast_rng
    dims = fast_rng(seed).integers(2, 5, int(shape[0]))
    total = int(sum(int(x) for x in dims))
    args = {"y_ptr": np.zeros(total, np.float32)}
    meta = {}
    return {"kernel": sumgate_kernel, "grid": (total,), "args": args,
            "meta": meta, "outputs": ("y_ptr",), "shape": tuple(shape),
            "dtype": "float32", "expected": ref(args, meta),
            "comparison": {"y_ptr": {"comparator": "array_equal",
                                     "exact": True}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or (3,), dtype=dtype, seed=seed)
'''


def check_sumloop_gate():
    """The control (MECH-WITNESS-TEST): a grid whose sum iterates a bound
    the model cannot read (an opaque call's result, not a bundle-visible
    scalar) keeps the located refusal naming the bound -- the SumLoop
    must not guess a count."""
    bad = []
    workdir = WORK / "sumgate"
    workdir.mkdir(parents=True, exist_ok=True)
    path = workdir / "sumgate.py"
    path.write_text(SUM_GATE_TEXT)
    spec = importlib.util.spec_from_file_location("sumgate", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    src = fe_source.load_operator(str(path))
    case = module.make_case()
    try:
        gridmodel.extract_grid(src, case)
        bad.append("accepted (a sum over an unbound the model cannot see "
                   "must refuse)")
    except gridmodel.GridError as exc:
        if "not provenance-tracked" not in str(exc):
            bad.append(f"wrong refusal: {str(exc)[:110]}")
    check("t039-sumloop-gate-unreadable-bound", not bad,
          "; ".join(bad[:2]) if bad else "opaque bound refuses located")


def check_no_baking_flat():
    """The no-baking spot check: gn_finalize's (128, 8) and (7, 3) shapes
    share ONE specialization identity (count/eps classes agree), so the
    second compile is a cache hit on the same artifact, and the runtime
    program count follows the bundle's view extent (1024 vs 21 -- a
    baked geometry would freeze one value)."""
    import a100_support.native_device as nd
    bad = []
    module = _load(OPS / "suite" / "dev" / "gn_finalize_kernel.py")
    c = _compiler("gnbake")
    hits = {}
    for shape, want in (((128, 8), 1024), ((7, 3), 21)):
        case = module.make_case(shape=shape)
        payload = {k: v for k, v in case.items()
                   if k not in ("expected", "oracle_args")}
        art = c.compile_case(payload)
        hits[shape] = art
        device = nd.NativeExecutableDevice(c, 4)
        staged = device.stage_case(case)
        staged.launch()
        got = np.asarray(staged.outputs()["mean_ptr"])
        if not np.allclose(got, np.asarray(case["expected"]["mean_ptr"]),
                           rtol=1e-5, atol=1e-5):
            bad.append(f"{shape}: mean_ptr mismatch")
    if hits[(128, 8)].sha256 != hits[(7, 3)].sha256:
        bad.append("the two shapes produced different artifacts")
    if not hits[(7, 3)].cache_hit:
        bad.append("the second shape did not reuse the first shape's "
                   "artifact (they must share one identity)")
    check("t039-flat-grid-no-baking", not bad,
          "; ".join(bad[:2]) if bad else
          "one artifact for (128,8) and (7,3); both compare PASS -- the "
          "runtime grid reads the view extent (1024 vs 21)")


# ---------------------------------------------------------------------------
# acceptance[1]: the deconv3d typical-case compute defect
# ---------------------------------------------------------------------------

DECONV_REPRO_TEXT = '''\
OPERATOR = {"name": "t039/deconv-repro", "group": "basic", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["memory.store.masked"]}
import numpy as np
import triton
import triton.language as tl


@triton.jit
def repro_kernel(x_ptr, y_ptr, Cout, Oz, Oy, Ox,
                 BLOCK_OC: tl.constexpr, BLOCK_OW: tl.constexpr):
    pid_ow = tl.program_id(0)
    pid_oc = tl.program_id(1)
    oc_offsets = pid_oc * BLOCK_OC + tl.arange(0, BLOCK_OC)
    ow_offsets = pid_ow * BLOCK_OW + tl.arange(0, BLOCK_OW)
    mask_oc = oc_offsets < Cout
    mask_ow = ow_offsets < Oz * Oy * Ox
    ow_offsets_i64 = ow_offsets.to(tl.int64)
    Oy_i64 = tl.full([1], Oy, dtype=tl.int64)
    Ox_i64 = tl.full([1], Ox, dtype=tl.int64)
    oz = (ow_offsets_i64 // (Oy_i64 * Ox_i64)).to(tl.int32)
    rem = (ow_offsets_i64 % (Oy_i64 * Ox_i64)).to(tl.int32)
    oy = (rem // Ox).to(tl.int32)
    ox = (rem % Ox).to(tl.int32)
    base_y_oc_i64 = (oc_offsets * (Oz * Oy * Ox)).to(tl.int64)
    y_spatial_off_i64 = (oz.to(tl.int64) * (Oy_i64 * Ox_i64)
                         + oy.to(tl.int64) * Ox_i64 + ox.to(tl.int64))
    xv = y_spatial_off_i64.to(tl.float32)
    acc = tl.zeros((BLOCK_OC, BLOCK_OW), dtype=tl.float32) + xv[None, :]
    y_ptrs = y_ptr + (base_y_oc_i64[:, None] + y_spatial_off_i64[None, :])
    store_mask = mask_oc[:, None] & mask_ow[None, :]
    tl.store(y_ptrs, acc, mask=store_mask)


def ref(args, meta):
    cout, oz, oy, ox = args["Cout"], args["Oz"], args["Oy"], args["Ox"]
    total = oz * oy * ox
    y = np.zeros(cout * total)
    for c in range(cout):
        y[c * total:(c + 1) * total] = np.arange(total)
    return {"y_ptr": y.astype(np.asarray(args["y_ptr"]).dtype)}


def _make_case(shape=(1, 4, 8, 6, 10), dtype="float32", seed=0):
    n, cin, dz, dy, dx = shape
    Oz, Oy, Ox = (dz - 1) + 3, (dy - 1) + 5, (dx - 1) + 5
    cout = 8
    total = Oz * Oy * Ox
    args = {"x_ptr": np.zeros(total, np.float32),
            "y_ptr": np.zeros(cout * total, np.float32),
            "Cout": np.int32(cout), "Oz": np.int32(Oz),
            "Oy": np.int32(Oy), "Ox": np.int32(Ox)}
    meta = {"BLOCK_OC": 16, "BLOCK_OW": 128}
    return {"kernel": repro_kernel,
            "grid": ((total + 127) // 128, (cout + 15) // 16),
            "args": args, "meta": meta, "outputs": ("y_ptr",),
            "shape": tuple(shape), "dtype": "float32",
            "expected": ref(args, meta),
            "comparison": {"y_ptr": {"comparator": "array_equal",
                                     "exact": True}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or (1, 4, 8, 6, 10), dtype=dtype, seed=seed)
'''


def check_deconv_repro():
    """The minimized reproduction of the deconv3d typical-case defect:
    the div/mod decomposition of ``ow`` into (oz, oy, ox) recomposed
    through [1]-element products (``Oy_i64 * Ox_i64``), stored by the
    [16,1]+[1,128] broadcast address.  Oy != Ox (10 vs 14) so the wrong
    factor is distinguishable (every deconv3d corpus shape has
    Oy == Ox, which let the smashed product coincide with a legal-looking
    factor).  The recomposition must equal ``ow`` exactly."""
    bad = []
    workdir = WORK / "repro"
    workdir.mkdir(parents=True, exist_ok=True)
    path = workdir / "repro.py"
    path.write_text(DECONV_REPRO_TEXT)
    spec = importlib.util.spec_from_file_location("repro", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for tag, cfg in (("on", passes_mod.PassConfig()),
                     ("off", passes_mod.PassConfig().all_off())):
        c = _compiler(f"repro-{tag}", pass_config=cfg)
        for threads in (1, 4):
            ok, detail = _run_case(c, module, threads)
            if not ok:
                bad.append(f"{tag} t={threads}: {detail}")
    check("t039-deconv-repro-extent1-staging", not bad,
          "; ".join(bad[:2]) if bad else
          "y_spatial == ow at every lane, passes on and off, 1/4 workers")


def check_deconv3d_cases():
    """The deconv3d operator itself: the typical shape (1, 4, 8, 8, 8)
    -- pinned by T037 as 'compiles but computes wrong results' -- and the
    degenerate shape execute and compare PASS at 1 and 4 workers."""
    sys.path.insert(0, str(ROOT / "tools"))
    import run_scan as rs  # noqa: E402
    bad = []
    c = _compiler("deconv")
    op = "suite/dev/deconv3d_fwd_kernel.py"
    rows = [r for r in rs.enumerated_rows(
        "ops/suite/manifest.json", operators=[op])]
    ran = 0
    for row in rows:
        case = rs.build_case(row, 30, use_golden=True)
        payload = {k: v for k, v in case.items()
                   if k not in ("expected", "oracle_args")}
        try:
            c.compile_case(payload)
        except PipelineError as exc:
            bad.append(f"{tuple(row['shape'])} {row['dtype']}: refused at "
                       f"{exc.construct!r}")
            continue
        for threads in (1, 4):
            ok, detail = _run_case(c, type("M", (), {
                "make_case": staticmethod(
                    lambda **kw: rs.build_case(row, 30, use_golden=True))}),
                threads)
            if not ok:
                bad.append(f"{tuple(row['shape'])} {row['dtype']} "
                           f"t={threads}: {detail}")
        ran += 1
    check("t039-deconv3d-typical-case-passes", not bad and ran > 0,
          "; ".join(bad[:2]) if bad else f"{ran} case rows PASS at 1/4 "
          "workers (the T037 pin flips to a full comparison PASS)")


# ---------------------------------------------------------------------------
# acceptance[2]: the gqa 1-worker CSE segfault
# ---------------------------------------------------------------------------

def check_gqa_all_workers():
    """gqa executes and compares PASS at 1, 2, 4 and 8 workers with the
    passes enabled (the T030-pinned 1-worker segfault is gone) and with
    the passes off (the general path stays green)."""
    bad = []
    module = _load(OPS / "suite" / "dev" / "gqa.py")
    for tag, cfg in (("on", passes_mod.PassConfig()),
                     ("off", passes_mod.PassConfig().all_off())):
        c = _compiler(f"gqa-{tag}", pass_config=cfg)
        for threads in (1, 2, 4, 8):
            ok, detail = _run_case(c, module, threads,
                                   shape=(2, 4, 2, 32, 32))
            if not ok:
                bad.append(f"{tag} t={threads}: {detail}")
    check("t039-gqa-passes-enabled-all-workers", not bad,
          "; ".join(bad[:2]) if bad else
          "passes on and off, 1/2/4/8 workers, all PASS")


PTRADD_BASE_TEXT = '''\
OPERATOR = {"name": "t039/ptradd-base", "group": "basic", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["memory.store.masked"]}
import numpy as np
import triton
import triton.language as tl


@triton.jit
def pbase_kernel(q_ptr, k_ptr, o_ptr, N_CTX, scale,
                 BLOCK: tl.constexpr):
    # the gqa defect shape: a [BLOCK, 1] staged ptradd BASE consumed by
    # a [BLOCK, BLOCK] store -- the base's staged read must map through
    # the result's broadcast axes (T029 covered the offset side only)
    pid = tl.program_id(0)
    offs = pid * BLOCK + tl.arange(0, BLOCK)
    mask = offs < N_CTX
    q = tl.load(q_ptr + offs, mask=mask, other=0.0)
    k = tl.load(k_ptr + offs, mask=mask, other=0.0)
    # a shared masked-load default the CSE pass merges across the loop
    acc = tl.zeros((BLOCK, BLOCK), dtype=tl.float32)
    for s in range(0, 2):
        a = tl.load(q_ptr + offs, mask=mask, other=0.0)
        b = tl.load(k_ptr + offs, mask=mask, other=0.0)
        acc += (a[:, None] + b[None, :]) * scale
    base = o_ptr + (offs[:, None] * N_CTX)
    tl.store(base + tl.arange(0, BLOCK)[None, :],
             acc + q[:, None] + k[None, :], mask=mask[:, None])


def ref(args, meta):
    n = int(args["N_CTX"])
    q = np.asarray(args["q_ptr"], dtype=np.float64)
    k = np.asarray(args["k_ptr"], dtype=np.float64)
    scale = float(args["scale"])
    out = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            out[i, j] = 2.0 * (q[i] + k[j]) * scale + q[i] + k[j]
    return {"o_ptr": out.reshape(-1).astype(
        np.asarray(args["o_ptr"]).dtype)}


def _make_case(shape=(32,), dtype="float32", seed=0):
    # n == BLOCK: one program covers every row and the store's column
    # block spans the full row (the probe exercises the staged-base
    # read, not tail masking)
    n = int(shape[0])
    rng = np.random.default_rng(seed)
    args = {"q_ptr": rng.standard_normal(n).astype(np.float32),
            "k_ptr": rng.standard_normal(n).astype(np.float32),
            "o_ptr": np.zeros(n * n, np.float32),
            "N_CTX": np.int32(n), "scale": np.float32(0.25)}
    meta = {"BLOCK": 32}
    return {"kernel": pbase_kernel, "grid": ((n + 31) // 32,), "args": args,
            "meta": meta, "outputs": ("o_ptr",), "shape": tuple(shape),
            "dtype": "float32", "expected": ref(args, meta),
            "comparison": {"o_ptr": {"comparator": "allclose",
                                     "exact": False, "rtol": 1e-5,
                                     "atol": 1e-5, "equal_nan": False}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or (32,), dtype=dtype, seed=seed)
'''


def check_ptradd_base_probe():
    """The structural regression: a staged [N, 1] ptradd base consumed by
    an [N, N] store, with CSE merging the loop's shared masked-load
    defaults -- the shape that exposed the unmapped base read (the gqa
    1-worker segfault).  The store's rows must be exact."""
    bad = []
    workdir = WORK / "pbase"
    workdir.mkdir(parents=True, exist_ok=True)
    path = workdir / "pbase.py"
    path.write_text(PTRADD_BASE_TEXT)
    spec = importlib.util.spec_from_file_location("pbase", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for tag, cfg in (("on", passes_mod.PassConfig()),
                     ("off", passes_mod.PassConfig().all_off())):
        c = _compiler(f"pbase-{tag}", pass_config=cfg)
        for threads in (1, 4):
            ok, detail = _run_case(c, module, threads)
            if not ok:
                bad.append(f"{tag} t={threads}: {detail}")
    check("t039-ptradd-staged-base-consumer-shape", not bad,
          "; ".join(bad[:2]) if bad else
          "the staged [N,1] base maps through the [N,N] result shape")


# ---------------------------------------------------------------------------
# acceptance[3]: the fp64 tl.dot refusal's recorded justification
# ---------------------------------------------------------------------------

def check_fp64_records():
    """The fp64 tl.dot refusal reads as declared-unsupported with
    evidence: the FRONTEND_COVERAGE tl.dot row carries the dtype-surface
    boundary note naming the corpus declaration (CORPUS_LOCK.json), the
    global declared dtype set has no float64, and the refusing
    operator's own declaration excludes it."""
    bad = []
    fc = json.loads((ROOT / "FRONTEND_COVERAGE.json").read_text())
    row = next((r for r in fc["rows"] if r["item"] == "tl.dot"), None)
    if row is None:
        bad.append("no tl.dot row")
    else:
        note = row.get("note") or ""
        if "T038 dtype-surface boundary" not in note:
            bad.append("the boundary note is missing from the tl.dot row")
        if "CORPUS_LOCK.json" not in note:
            bad.append("the note does not name the corpus declaration")
    lock = json.loads(
        (ROOT / "docs" / "compiler-agent" / "CORPUS_LOCK.json").read_text())
    global_dtypes = set()
    for op in lock["operators"]:
        global_dtypes.update(op.get("dtypes", []))
        if "iplr_delta_rule_fwd_kernel_o" in json.dumps(op):
            if "float64" in op.get("dtypes", []):
                bad.append("the refusing operator declares float64")
    if "float64" in global_dtypes:
        bad.append("the declared surface contains float64")
    check("t039-fp64-dot-refusal-justification-recorded", not bad,
          "; ".join(bad[:2]) if bad else
          "FRONTEND_COVERAGE tl.dot note names CORPUS_LOCK.json; "
          f"declared dtypes {sorted(global_dtypes)}")


# ---------------------------------------------------------------------------

def main():
    check_gn_finalize_flattening()
    check_flattening_gate()
    check_grouped_gemm_sumloop()
    check_sumloop_gate()
    check_no_baking_flat()
    check_deconv_repro()
    check_deconv3d_cases()
    check_gqa_all_workers()
    check_ptradd_base_probe()
    check_fp64_records()
    if FAILURES:
        print(f"\nFAILED: {len(FAILURES)} check(s): {FAILURES}")
        return 1
    print("\ntest_t039_repairs: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
