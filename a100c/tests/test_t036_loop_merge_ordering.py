#!/usr/bin/env python3
"""test_t036_loop_merge_ordering.py -- the T036 (WTI038) round-3 repair
classes: the generic loop-carried merge and the lowering-ordering family,
each through the real path (compile -> native execution -> comparison
under the case's own policy), with the controls that prove the checks
are load-bearing.

The repaired census classes (the final 109-row census):

  * the 31 'region value <name> escapes without a merge rule (its loop
    update is not a recognized reduction form)' rows -- loop-carried
    values updated through NON-plain-reduction forms must merge across
    the loop back edge through the generic carried-value join
    machinery.  The stage plan now recognizes three more update forms
    (a100c/plan/stages.py): the extremum binops
    (``acc = tl.maximum(acc, term)`` / tl.minimum, either operand
    order -- arith.maxnumf/minnumf/maximumf/minimumf/maxsi/minsi/
    maxui/minui), and the guarded extremum select
    (``acc = tl.where(term < acc, term, acc)`` with its operand/
    direction variants, the carried value on one side).  The (value,
    index) arg-select pair under a compound condition keeps its own
    machinery; a rebinding that drops the carried value is NOT an
    extremum fold (last-wins, no rule).
  * the 3 'merge: a partial has no lowered value at the chunk back
    edge' rows -- the chunk a SCALAR segment's block statement opens
    (the extent-1 splat sources) rode the unfiltered kernel-level frame
    list; its close refused before the restructured region ever
    lowered.  The scalar branch now filters its frames to the ones its
    own statements define (none in practice: reduces and loops are
    pass or matrix segments), and the no-pass fallback vl is the block
    extent's own chunk plan -- the scalar-opened chunk ran 32 lanes
    over extent-1 staged slots and its stores overflowed them (the
    executed 0.0-for-0.787 nansum defect, reproduced and fixed here).
  * the ~20 mir-verifier use-before-definition rows -- values defined
    inside a chunk body or a sibling if-arm consumed after the close:
    the region close now drops the stale chunk-body bindings (pure
    trees re-materialize; merged partials and liveouts rebind at the
    exit) and clears the chunk so suffix-level ifs stop threading
    per-chunk candidates (reduce_kernel's if2.join arg); each if-arm
    starts from the PRE-IF merge-slot state (masked_cumsum's else arm
    branched to the join with the THEN arm's scan carry); a
    restructured if's arm-close join values are nested-liveout uses of
    the arm's passes (cross_entropy's loop induction ``i``); and a
    16-bit float scan's carry computes at fp32 (the target's e16 float
    lanes are fp16 -- a bf16 scan's adds through them silently
    reinterpreted the bits; masked_cumsum bf16's executed garbage).

Run: python3 a100c/tests/test_t036_loop_merge_ordering.py
     (exit 0 = all PASS)
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
from a100c.passes import pipeline as passes_mod  # noqa: E402
from a100c.plan import stages as stages_mod  # noqa: E402
from a100c.frontend import source as fe_source  # noqa: E402
from a100c.frontend import lower_tir, specialize as fe_spec  # noqa: E402
from a100c.ir import tir  # noqa: E402
from a100c.lower.vectorize import (  # noqa: E402
    SliceLowering, LowerOptions)
from a100c.plan.partition import ExecutionPlan  # noqa: E402
from a100c.target import DEFAULT_TARGET  # noqa: E402
from a100c.lower.binding import argument_layout  # noqa: E402
from a100c.frontend.gridmodel import extract_grid  # noqa: E402
from a100c.lower import matrix as matrix_verify  # noqa: E402

OPS = ROOT / "ops"
WORK = Path(tempfile.mkdtemp(prefix="a100c-t036lmo-"))

_scan_spec = importlib.util.spec_from_file_location(
    "run_scan_for_t036lmo", str(ROOT / "tools" / "run_scan.py"))
_rs = importlib.util.module_from_spec(_scan_spec)
_scan_spec.loader.exec_module(_rs)


# ---------------------------------------------------------------------------
# shared harness
# ---------------------------------------------------------------------------

def _compiler(tag: str) -> FactoryCompiler:
    return FactoryCompiler(
        options=CompileOptions(cache_dir=str(WORK / f"cache-{tag}")),
        pass_config=passes_mod.PassConfig())


def _harness_case(op_rel: str, shape, dtype):
    op = _rs.resolve_operator_path(op_rel)
    row = next(r for r in _rs.enumerated_rows(
            str(ROOT / "ops" / "suite" / "manifest.json"))
               if r["operator"] == op and tuple(r["shape"]) == tuple(shape)
               and r["dtype"] == dtype)
    return _rs.build_case(row, 30, use_golden=True)


def _run_harness_case(compiler, op_rel, shape, dtype, threads):
    import a100_support.native_device as nd
    case = _harness_case(op_rel, shape, dtype)
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
            same = np.array_equal(
                got, exp, equal_nan=policy.get("equal_nan", False))
        else:
            same = np.allclose(got, exp, rtol=policy.get("rtol", 0.0),
                               atol=policy.get("atol", 0.0),
                               equal_nan=policy.get("equal_nan", False))
        if not same:
            detail = f"{name}: {int(np.sum(got != exp))} mismatched " \
                     f"(first got {got.ravel()[:3]} exp {exp.ravel()[:3]})"
        ok &= same
    return ok, detail


TEMPLATE = ('"""probe operator %s"""\n'
            'OPERATOR = {"name": "probe/%s", "group": "probe", "channel": '
            '"local",\n'
            '            "execution": "triton_kernel", "verification": '
            '"correctness", "tags": []}\n'
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


def _operator_file(name: str, params: str, body: str, case_layer: str):
    text = TEMPLATE % (name, name, name, params, body, case_layer)
    path = WORK / f"{name}.py"
    path.write_text(text)
    return path


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_probe_case(compiler, module, threads: int, **make_kwargs):
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
            detail = f"{name}: first got {got.ravel()[:4]} " \
                     f"exp {exp.ravel()[:4]}"
        ok &= same
    return ok, detail


def _lower_probe(name, params, body, case_layer, case):
    """The real compile path up to MIR: source -> specialization -> TIR
    (+ passes + TIR verify) -> MIR (+ MIR verify).  Returns the modules
    and the verifier error lists."""
    path = _operator_file(name, params, body, case_layer)
    src = fe_source.load_operator(str(path))
    specz = fe_spec.specialize(src, case)
    tm = lower_tir.lower(src, specz)
    tir_errors_pre = tir.verify_module(tm)
    passes_mod.run(tm, passes_mod.PassConfig())
    tir_errors = tir.verify_module(tm) or tir_errors_pre
    grid = extract_grid(src, case)
    layout = argument_layout(case, specz)
    lv = SliceLowering(tm, ExecutionPlan(), DEFAULT_TARGET, layout, grid,
                       LowerOptions())
    mir_module = lv.lower()
    mir_errors = matrix_verify.verify_module(mir_module)
    return tm, mir_module, tir_errors, mir_errors


# ---------------------------------------------------------------------------
# 1. the plan classification: the non-reduction carried-update forms
# ---------------------------------------------------------------------------

PLAN_TEMPLATE = ('"""probe operator %s"""\n'
                 'OPERATOR = {"name": "probe/%s", "group": "probe", '
                 '"channel": "local",\n'
                 '            "execution": "triton_kernel", "verification": '
                 '"correctness", "tags": []}\n'
                 'SHAPES = ((257,),)\n'
                 'import numpy as np\n'
                 'import triton\n'
                 'import triton.language as tl\n'
                 '\n'
                 '@triton.jit\n'
                 'def %s_kernel(x_ptr, o_ptr, v_ptr, n, BLOCK: tl.constexpr):\n'
                 '%s\n'
                 '\n'
                 'def _make_case(shape=(257,), dtype="float32", seed=0):\n'
                 '    return {"args": {"x_ptr": np.zeros(257, np.float32),\n'
                 '                     "o_ptr": np.zeros(4, np.float32),\n'
                 '                     "v_ptr": np.zeros(4, np.int32),\n'
                 '                     "n": 257},\n'
                 '            "meta": {"BLOCK": 128}, "grid": (1,),\n'
                 '            "outputs": ("o_ptr",)}\n')


def _plan_of(name: str, body: str):
    text = PLAN_TEMPLATE % (name, name, name, body)
    path = WORK / f"{name}.py"
    path.write_text(text)
    src = fe_source.load_operator(str(path))
    case = {"args": {"x_ptr": np.zeros(257, np.float32),
                     "o_ptr": np.zeros(4, np.float32),
                     "v_ptr": np.zeros(4, np.int32), "n": 257},
            "meta": {"BLOCK": 128}, "grid": (1,), "outputs": ("o_ptr",)}
    specz = fe_spec.specialize(src, case)
    tm = lower_tir.lower(src, specz)
    passes_mod.run(tm, passes_mod.PassConfig())
    return stages_mod.build_stage_plan(tm), tm


def check_plan_forms():
    """The (b) classification recognizes the extremum binop, the guarded
    extremum select and the index-tracking min; a compound-condition
    select keeps the arg-select PAIR form; a rebinding that drops the
    carried value and a subtract accumulate stay unrecognized (the
    located-refusal boundary -- the control that the recognition is not
    over-broad)."""
    # the where-guarded maximum binop (logsumexp's form)
    plan, _ = _plan_of("plan_extremum_binop", """
    lo = float('-inf')
    for start in range(0, n, BLOCK):
        i = start + tl.arange(0, BLOCK)
        x = tl.load(x_ptr + i, mask=i < n, other=float('-inf'))
        lo = tl.maximum(lo, tl.max(x, axis=0))
    tl.store(o_ptr, lo)
""")
    check("plan-extremum-binop-max-merge",
          any(p.name == "lo" and p.merge == stages_mod.MERGE_MAX
              for p in plan.partials),
          str([(p.name, p.merge) for p in plan.partials]))

    # the guarded extremum SELECT with index tracking (nanmedian's form)
    plan, _ = _plan_of("plan_guarded_select", """
    worst = tl.full((), 257, dtype=tl.int32)
    for start in range(0, n, BLOCK):
        i = start + tl.arange(0, BLOCK)
        m = i < n
        x = tl.load(x_ptr + i, mask=m, other=0.0)
        local = tl.min(tl.where(m, i, 257), axis=0)
        worst = tl.where(local < worst, local, worst)
    tl.store(v_ptr, worst)
""")
    check("plan-guarded-select-min-merge",
          any(p.name == "worst" and p.merge == stages_mod.MERGE_MIN
              for p in plan.partials),
          str([(p.name, p.merge) for p in plan.partials]))

    # the compound-condition (value, index) pair keeps the pair form
    plan, _ = _plan_of("plan_pair_select", """
    best = float('-inf')
    idx = 2147483647
    for start in range(0, n, BLOCK):
        i = start + tl.arange(0, BLOCK)
        m = i < n
        x = tl.load(x_ptr + i, mask=m, other=float('-inf'))
        cand = tl.max(x, axis=0)
        cand_idx = tl.min(tl.where(m, i, 2147483647), axis=0)
        take = (cand > best) | ((cand == best) & (cand_idx < idx))
        best = tl.where(take, cand, best)
        idx = tl.where(take, cand_idx, idx)
    tl.store(o_ptr, best)
""")
    check("plan-pair-select-keeps-pair-merge",
          any(p.merge in (stages_mod.MERGE_MAX_INDEX,
                          stages_mod.MERGE_MIN_INDEX)
              and p.pair_value_id is not None for p in plan.partials),
          str([(p.name, p.merge) for p in plan.partials]))

    # the CONTROL: an unrecognized update still refuses located
    plan, _ = _plan_of("plan_subtract_form", """
    acc = tl.zeros((), dtype=tl.float32)
    for start in range(0, n, BLOCK):
        i = start + tl.arange(0, BLOCK)
        x = tl.load(x_ptr + i, mask=i < n, other=0.0)
        acc = acc - tl.sum(x, axis=0)
    tl.store(o_ptr, acc)
""")
    check("plan-unrecognized-update-still-refuses",
          (not plan.eligible) and "without a merge rule" in plan.reason,
          plan.reason[:90])

    # the CONTROL: a rebinding select whose condition does not compare
    # the select's own two values is not an extremum fold (a conditional
    # accumulate keeps the located-refusal boundary)
    plan, _ = _plan_of("plan_rebinding_select", """
    acc = tl.zeros((), dtype=tl.float32)
    for start in range(0, n, BLOCK):
        i = start + tl.arange(0, BLOCK)
        x = tl.load(x_ptr + i, mask=i < n, other=0.0)
        s = tl.sum(x, axis=0)
        acc = tl.where(s > 0.0, s, acc)
    tl.store(o_ptr, acc)
""")
    check("plan-rebinding-select-not-an-extremum",
          not any(p.merge in (stages_mod.MERGE_MIN, stages_mod.MERGE_MAX)
                  and p.name == "acc" for p in plan.partials),
          str([(p.name, p.merge) for p in plan.partials]))


# ---------------------------------------------------------------------------
# 2. the carried-update shape, executed (the 31-row loop class)
# ---------------------------------------------------------------------------

CARRIED_CASE_LAYER = '''
def ref(args, meta):
    x = np.asarray(args["x_ptr"], dtype=np.float64)
    m = np.asarray(args["m_ptr"]) != 0
    n = int(args["n"])
    best = -np.inf
    idx = 2147483647
    worst = 2147483647
    for start in range(0, n, 128):
        cols = start + np.arange(128)
        valid = cols < n
        clip = np.minimum(cols, n - 1)
        mm = valid & m[clip]
        xc = x[clip]
        v = np.where(mm & (xc == xc), xc, -np.inf)
        cand = v.max()
        cand_idx = np.where(v == cand, cols, 2147483647).min()
        take = (cand > best) | ((cand == best) & (cand_idx < idx))
        best = float(np.where(take, cand, best))
        idx = int(np.where(take, cand_idx, idx))
        isn = mm & (xc != xc)
        worst = min(worst, int(np.where(isn, cols, 2147483647).min()))
    return {"o_ptr": np.array([best], np.float32),
            "v_ptr": np.array([idx], np.int32),
            "w_ptr": np.array([worst], np.int32)}


def make_case(shape=None, dtype="float32", seed=7):
    rng = np.random.default_rng(seed)
    n = 300
    # quarter-quantized values: exactly representable in fp32 (and in
    # the fp64 reference), so a value tie is EXACT and both sides pick
    # the same leftmost index (a near-tie would differ between the fp32
    # lanes and the fp64 reference)
    x = (np.round(rng.standard_normal(n) * 4) / 4).astype(np.float32)
    x[5] = np.nan
    x[299] = np.nan
    m = (rng.random(n) > 0.25).astype(np.int32)
    args = {"x_ptr": x, "m_ptr": m, "o_ptr": np.zeros(1, np.float32),
            "v_ptr": np.zeros(1, np.int32), "w_ptr": np.zeros(1, np.int32),
            "n": n}
    exp = ref(args, {})
    return {"args": args, "meta": {"BLOCK": 128}, "grid": (1,),
            "outputs": tuple(exp), "expected": exp,
            "kernel": carried_probe_kernel,
            "comparison": {"o_ptr": {"comparator": "allclose", "exact":
                                     False, "rtol": 1e-6, "atol": 1e-6,
                                     "equal_nan": True},
                           "v_ptr": {"comparator": "array_equal",
                                     "exact": True},
                           "w_ptr": {"comparator": "array_equal",
                                     "exact": True}}}
'''


def check_carried_update_executes():
    """The non-reduction carried-update shape through the REAL path: a
    128-lane block over a 300-element row (3 source iterations, 4
    32-lane chunks per block) carrying a where-guarded maximum, its
    paired index tracking, and a guarded minimum for the first NaN
    index.  Executed at 1 and 4 workers; the integer/index outputs are
    exact (the tie-break-left pair semantics), the float output within
    its declared tolerance.  Pre-fix this shape refused at 'loop'
    (nan_index/maximum/best escape without a merge rule)."""
    body = """
    lane = tl.arange(0, BLOCK)
    best = -float('inf')
    idx = 2147483647
    worst = 2147483647
    for start in range(0, n, BLOCK):
        cols = start + lane
        valid = cols < n
        mrow = tl.load(m_ptr + cols, mask=valid, other=0) != 0
        x = tl.load(x_ptr + cols, mask=valid & mrow,
                    other=-float('inf'))
        isn = valid & mrow & (x != x)
        worst = tl.minimum(worst,
                           tl.min(tl.where(isn, cols, 2147483647), axis=0))
        safe = tl.where(valid & mrow & (x == x), x, -float('inf'))
        cand = tl.max(safe, axis=0)
        cand_idx = tl.min(tl.where(valid & mrow & (safe == cand),
                                   cols, 2147483647), axis=0)
        take = (cand > best) | ((cand == best) & (cand_idx < idx))
        best = tl.where(take, cand, best)
        idx = tl.where(take, cand_idx, idx)
    tl.store(o_ptr, best)
    tl.store(v_ptr, idx)
    tl.store(w_ptr, worst)
"""
    path = _operator_file("carried_probe",
                          "x_ptr, m_ptr, o_ptr, v_ptr, w_ptr, n, "
                          "BLOCK: tl.constexpr", body, CARRIED_CASE_LAYER)
    module = _load(path)
    c = _compiler("carried")
    bad = []
    for threads in (1, 4):
        ok, detail = _run_probe_case(c, module, threads)
        if not ok:
            bad.append(f"t={threads}: {detail}")
    check("carried-update-executes-1-4-workers", not bad,
          "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# 3. the scalar-opened chunk's staging (the 3-row merge class)
# ---------------------------------------------------------------------------

NANSUM_CASE_LAYER = '''
def ref(args, meta):
    import numpy as np
    x = np.asarray(args["mid"], dtype=np.float64)
    n = int(args["mid_size"])
    return {"out": np.array([np.sum(x[:n])], np.float32)}


def make_case(shape=None, dtype="float32", seed=11):
    import numpy as np
    rng = np.random.default_rng(seed)
    n = 17
    x = rng.normal(0.0, 1.0, n)
    args = {"mid": x, "out": np.full(1, -7.0), "mid_size": n}
    exp = ref(args, {})
    return {"args": args, "meta": {"BLOCK_SIZE": 1}, "grid": (1,),
            "outputs": tuple(exp), "expected": exp,
            "kernel": nansum_probe_kernel,
            "comparison": {"out": {"comparator": "allclose", "exact":
                                   False, "rtol": 1e-5, "atol": 1e-6,
                                   "equal_nan": True}}}
'''


def check_scalar_chunk_staging():
    """The scalar-opened chunk's frames and fallback vl: an all-matrix
    region kernel (no pass segments) whose extent-1 splat sources open
    the chunk.  Pre-fix (a) the compile refused 'a partial has no
    lowered value at the chunk back edge' and (b) with only the frame
    filter fixed the executed sum came out 0.0 (the scalar-opened
    chunk ran 32 lanes and its staged stores overflowed the 1-element
    slots -- the mask reload read the start-splat's zeros)."""
    body = """
    _sum = tl.zeros((), dtype=tl.float32)
    for start in range(0, mid_size, BLOCK_SIZE):
        idx = start + tl.arange(0, BLOCK_SIZE)
        mask = idx < mid_size
        val = tl.load(mid + idx, mask=mask, other=0.0).to(tl.float32)
        val = tl.where(val != val, 0.0, val)
        _sum += tl.sum(val, axis=0)
    tl.store(out, _sum)
"""
    path = _operator_file("nansum_probe",
                          "mid, out, mid_size, BLOCK_SIZE: tl.constexpr",
                          body, NANSUM_CASE_LAYER)
    module = _load(path)
    c = _compiler("nansum")
    bad = []
    for threads in (1, 4):
        ok, detail = _run_probe_case(c, module, threads)
        if not ok:
            bad.append(f"t={threads}: {detail}")
    check("scalar-chunk-staging-executes-1-4-workers", not bad,
          "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# 4. the join-ordering failure mode (the mir-verifier rows)
# ---------------------------------------------------------------------------

def check_join_ordering_verifiers():
    """The five use-before-definition shapes compile through the REAL
    driver (whose stage 6 runs the MIR verifier) AND lower explicitly
    with both the TIR and MIR verifiers accepting the built module.
    Pre-fix the MIR verifier rejected each with 'use-before-definition'
    (branch arguments to joins / a vpopc operand defined inside the
    chunk body)."""
    cases = [
        ("suite/dev/cross_entropy_kernel.py", (1, 17), "float32"),
        ("suite/dev/cumprod_dim1_kernel_log2exp2_early.py", (17, 100),
         "float32"),
        ("suite/dev/masked_cumsum_kernel_db.py", (17, 100), "float32"),
        ("suite/dev/reduce_kernel.py", (17,), "bfloat16"),
        ("suite/dev/renorm_kernel_norms.py", (17,), "float32"),
    ]
    c = _compiler("ordering")
    bad = []
    for op, shape, dtype in cases:
        try:
            case = _harness_case(op, shape, dtype)
        except SystemExit:
            bad.append(f"{op}: no case")
            continue
        payload = {k: v for k, v in case.items()
                   if k not in ("expected", "oracle_args")}
        # the real driver: specialization -> TIR (+verify) -> passes
        # (+verify) -> MIR (+ the mir-verifier) -> legalise -> select
        # -> allocate -> emit -> ELF
        try:
            c.compile_case(payload)
        except PipelineError as exc:
            bad.append(f"{op.split('/')[-1]}: refused at {exc.construct}")
            continue
        except Exception as exc:                   # noqa: BLE001
            bad.append(f"{op.split('/')[-1]}: {type(exc).__name__}")
            continue
        # the explicit verifier assertion on a freshly built module
        kern = payload["kernel"]
        fn0 = kern
        path = None
        for _ in range(8):
            code = getattr(fn0, "__code__", None)
            if code is not None and code.co_filename:
                path = code.co_filename
                break
            nxt = getattr(fn0, "fn", None)
            if nxt is None or nxt is fn0:
                break
            fn0 = nxt
        src = fe_source.load_operator(path)
        specz = fe_spec.specialize(src, payload)
        tm = lower_tir.lower(src, specz)
        if tir.verify_module(tm):
            bad.append(f"{op.split('/')[-1]}: TIR verifier rejected")
            continue
        passes_mod.run(tm, passes_mod.PassConfig())
        if tir.verify_module(tm):
            bad.append(f"{op.split('/')[-1]}: TIR verifier post-passes")
            continue
        grid = extract_grid(src, payload)
        layout = argument_layout(payload, specz)
        lv = SliceLowering(tm, ExecutionPlan(), DEFAULT_TARGET, layout,
                           grid, LowerOptions())
        m = lv.lower()
        errs = matrix_verify.verify_module(m)
        if errs:
            bad.append(f"{op.split('/')[-1]}: MIR verifier: "
                       f"{str(errs[0])[:70]}")
    check("join-ordering-verifiers-accept", not bad, "; ".join(bad[:3]))


# ---------------------------------------------------------------------------
# 5. the scan's fp32-lane policy (the bf16 miscompile the first
#    executions of the repaired class exposed)
# ---------------------------------------------------------------------------

def check_bf16_scan_policy():
    """A bf16 scan's carry computes at fp32: the target's e16 float
    lanes are fp16 and bf16 has no native vector arithmetic.  Pre-fix
    the scan's inner adds ran at e16 and the executed cumsum was
    garbage from row 1 (the first row's chunks left the carry at the
    fp16-read bits)."""
    body = """
    row = tl.program_id(0)
    base = x_ptr + row * N
    obase = o_ptr + row * N
    offs = tl.arange(0, BLOCK_N)
    m = tl.load(mm_ptr + row * N + offs, mask=offs < N, other=0) != 0
    x = tl.load(base + offs, mask=(offs < N) & m, other=0.0)
    scan = tl.cumsum(x, axis=0)
    tl.store(obase + offs, scan, mask=offs < N)
"""
    case_layer = '''
def ref(args, meta):
    import numpy as np
    x = np.asarray(args["x_ptr"], dtype=np.float32)
    m = np.asarray(args["mm_ptr"]) != 0
    out = np.where(m, x, 0.0).cumsum(axis=1).astype(np.float32)
    return {"o_ptr": out}


def make_case(shape=None, dtype="bfloat16", seed=3):
    import numpy as np
    rng = np.random.default_rng(seed)
    M, N = 4, 100
    x = (rng.standard_normal((M, N)) * 3.0).astype(np.float32)
    m = (rng.random((M, N)) > 0.3).astype(np.int32)
    args = {"x_ptr": x, "mm_ptr": m,
            "o_ptr": np.zeros((M, N), np.float32), "N": N}
    exp = ref(args, {})
    return {"args": args, "meta": {"BLOCK_N": 256}, "grid": (M,),
            "outputs": tuple(exp), "expected": exp,
            "kernel": bf16_scan_probe_kernel,
            "comparison": {"o_ptr": {"comparator": "allclose", "exact":
                                     False, "rtol": 1e-2, "atol": 1e-2,
                                     "equal_nan": True}}}
'''
    path = _operator_file("bf16_scan_probe",
                          "x_ptr, mm_ptr, o_ptr, N, BLOCK_N: tl.constexpr",
                          body, case_layer)
    module = _load(path)
    c = _compiler("bf16scan")
    bad = []
    for threads in (1, 4):
        ok, detail = _run_probe_case(c, module, threads)
        if not ok:
            bad.append(f"t={threads}: {detail}")
    check("bf16-scan-fp32-policy-executes-1-4", not bad,
          "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# 6. the owned corpus operators, executed (acceptance[1])
# ---------------------------------------------------------------------------

OWNED = [
    # the argmax/max/min/logsumexp families the acceptance names, every
    # census shape and dtype
    ("suite/perf/argmax.py", (4, 16), "float32"),
    ("suite/perf/argmax.py", (4, 16), "float16"),
    ("suite/perf/argmax.py", (4, 16), "bfloat16"),
    ("suite/perf/argmax.py", (4, 97), "float32"),
    ("suite/perf/argmax.py", (4, 97), "float16"),
    ("suite/perf/argmax.py", (4, 97), "bfloat16"),
    ("suite/perf/max.py", (4, 16), "float32"),
    ("suite/perf/max.py", (4, 16), "float16"),
    ("suite/perf/max.py", (4, 16), "bfloat16"),
    ("suite/perf/max.py", (4, 97), "float32"),
    ("suite/perf/max.py", (4, 97), "float16"),
    ("suite/perf/max.py", (4, 97), "bfloat16"),
    ("suite/perf/min.py", (4, 16), "float32"),
    ("suite/perf/min.py", (4, 16), "float16"),
    ("suite/perf/min.py", (4, 16), "bfloat16"),
    ("suite/perf/min.py", (4, 97), "float32"),
    ("suite/perf/min.py", (4, 97), "float16"),
    ("suite/perf/min.py", (4, 97), "bfloat16"),
    ("suite/perf/logsumexp.py", (4, 16), "float32"),
    ("suite/perf/logsumexp.py", (4, 16), "float16"),
    ("suite/perf/logsumexp.py", (4, 16), "bfloat16"),
    ("suite/perf/logsumexp.py", (4, 97), "float32"),
    ("suite/perf/logsumexp.py", (4, 97), "float16"),
    ("suite/perf/logsumexp.py", (4, 97), "bfloat16"),
    # every other owned identity of the three census classes
    ("suite/perf/sigmoid_argmax.py", (4, 16), "float32"),
    ("suite/perf/sigmoid_argmax.py", (4, 97), "float32"),
    ("suite/dev/pdist_forward__pdist_forward_inf_kernel.py", (17,),
     "float32"),
    ("suite/dev/pdist_forward__pdist_forward_inf_kernel.py", (17,),
     "float16"),
    ("suite/dev/pdist_forward__pdist_forward_inf_kernel.py", (17,),
     "bfloat16"),
    ("suite/dev/nanmedian_ascend_byte_histogram_find_index_kernel.py",
     (17,), "torch.int32"),
    ("suite/dev/nanmedian_ascend_byte_histogram_find_index_kernel.py",
     (97,), "torch.int32"),
    ("suite/dev/nansum_kernel_2.py", (17,), "float32"),
    ("suite/dev/nansum_kernel_2.py", (17,), "float16"),
    ("suite/dev/nansum_kernel_2.py", (17,), "bfloat16"),
    ("suite/dev/cross_entropy_kernel.py", (1, 17), "float32"),
    ("suite/dev/cross_entropy_kernel.py", (1, 17), "float16"),
    ("suite/dev/cross_entropy_kernel.py", (1, 17), "bfloat16"),
    ("suite/dev/cross_entropy_kernel.py", (17, 97), "float32"),
    ("suite/dev/cross_entropy_kernel.py", (17, 97), "float16"),
    ("suite/dev/cross_entropy_kernel.py", (17, 97), "bfloat16"),
    ("suite/dev/cumprod_dim1_kernel_log2exp2_early.py", (1, 1), "float32"),
    ("suite/dev/cumprod_dim1_kernel_log2exp2_early.py", (17, 100),
     "float32"),
    ("suite/dev/cumprod_dim1_kernel_log2exp2_early.py", (64, 128),
     "float32"),
    ("suite/dev/masked_cumsum_kernel_db.py", (17, 100), "float32"),
    ("suite/dev/masked_cumsum_kernel_db.py", (17, 100), "float16"),
    ("suite/dev/masked_cumsum_kernel_db.py", (17, 100), "bfloat16"),
    ("suite/dev/masked_cumsum_kernel_db.py", (128, 128), "float32"),
    ("suite/dev/masked_cumsum_kernel_db.py", (128, 128), "float16"),
    ("suite/dev/masked_cumsum_kernel_db.py", (128, 128), "bfloat16"),
    ("suite/dev/reduce_kernel.py", (17,), "bfloat16"),
    ("suite/dev/reduce_kernel.py", (17,), "float16"),
    ("suite/dev/renorm_kernel_norms.py", (17,), "float32"),
    ("suite/dev/renorm_kernel_norms.py", (17,), "float16"),
    ("suite/dev/renorm_kernel_norms.py", (17,), "bfloat16"),
]


def check_owned_operators_execute():
    """Every owned identity of the three census classes executes and
    compares PASS at 1 and 4 workers under its own declared policy
    (integer/index outputs exact; the argmax tie-break-left pair
    semantics preserved -- the pair merges with tie-break-left and the
    guarded minimum tracks the first NaN index exactly)."""
    c = _compiler("owned")
    bad = []
    for op, shape, dtype in OWNED:
        for threads in (1, 4):
            try:
                ok, detail = _run_harness_case(c, op, shape, dtype, threads)
            except Exception as exc:                 # noqa: BLE001
                ok, detail = False, f"{type(exc).__name__}: {str(exc)[:80]}"
            if not ok:
                bad.append(f"{op.split('/')[-1]} {shape} {dtype} "
                           f"t={threads}: {detail}")
    check("owned-operators-execute-1-4-workers", not bad,
          "; ".join(bad[:2]))


def main() -> int:
    check_plan_forms()
    check_carried_update_executes()
    check_scalar_chunk_staging()
    check_join_ordering_verifiers()
    check_bf16_scan_policy()
    check_owned_operators_execute()
    if FAILURES:
        print(f"\nFAILED: {len(FAILURES)} check(s): {FAILURES}",
              file=sys.stderr)
        return 1
    print("\nall T036 loop-merge/ordering checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
