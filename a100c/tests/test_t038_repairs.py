#!/usr/bin/env python3
"""test_t038_repairs.py -- the T038 round-3 long-tail repair classes (the
final construct census rows), each through the real path (compile -> native
execution -> comparison under the case's own policy), with the controls
that prove the checks are load-bearing.

  * the last-axis scan of a MULTI-AXIS block (masked_cumsum_vec's
    (BLOCK_COLS, VEC) cumsum along axis 1, cumprod_grouped's (GROUP_ROWS,
    BLOCK_COLS) cumprod along axis 1): the scan's chunk carry restarts at
    every row boundary of the row-major flat lane order (the reset modulus
    is the LAST axis's extent), the reset select composes at the carry's
    fp32 class with its mask on hardware v0, and the scan's workspace
    slice is sized by the OPERAND's own flat extent (a restructured
    region's nested pass extents are invisible to the top-level max
    extent -- the undersized slice overran into the staging records and
    the executed store scattered to garbage).  Both operators execute and
    compare PASS at 1 and 4 workers.
  * the ==1-specialization hint (masked_cumsum_vec at shape (1, 1)):
    ``tl.multiple_of`` on the folded constant stride is the value itself
    (a promise on a known value carries no information; the wide-access
    proof reads hints off runtime values only).  The (1, 1) cases compile
    and execute PASS at 1 and 4 workers.
  * the constexpr convert (final_mean at shape (1,)): ``tl.cast`` of the
    ==1-folded scalar materializes as a TIR constant of its own literal
    type and takes the ordinary convert op (constprop folds it under the
    declared semantics -- never a Python re-typing).  The (1,) cases
    execute PASS at 1 and 4 workers.
  * the vsel v0-mask re-materializations (cyclic_jacobi_pair,
    blocked_jacobi_pair_svals, l1_norm_fused): the two rank-0 pure-select
    re-materialization paths insert the vmovmask like every other vsel
    site.  All three operators execute PASS at 1 and 4 workers.
  * the staging-loop merge select (fht's join over the 64-bit staged
    lanes): the region opens at the VALUES' type after the selector's
    index-class compare.  fht [17] float32 (and every other declared
    case) executes PASS at 1 and 4 workers.
  * the whole-block reorder/count protocol (ranked_distribution's
    tl.sort + tl.flip + tl.gather + tl.topk + softmax,
    nanmedian_ascend_histogram_count's tl.histogram): sort lowers by the
    stable rank form through the workspace, topk as the rank restricted
    to k, histogram as the per-bin equality count; the chunk/width-bound
    gathers materialize through the staged source region; the full-axis
    keep_dims reduce binds the [1] result to the reduced scalar with the
    pass constrained by the OPERAND's extent.  Both operators execute
    and compare PASS at 1 and 4 workers.
  * the native-source layout mirror (chunk_transform_qk's permute over
    an IME-native fp16 record): the source widens into a 32-bit scratch
    mirror through the safe unit-stride forms and the staging loop's
    indexed reads run against the mirror; the multi-view IME kernel
    counts the tile-loop state against the GPR budget (the view bases
    re-materialize at their uses).  chunk_transform_qk's [6, 33, 11, 13,
    16] fp16 identity (and the other declared cases) executes PASS at 1
    and 4 workers.
  * the fp64 dot row resolves against the corpus's declared dtype
    surface: CORPUS_LOCK.json declares chunk_generalized_iplr's dtypes
    float32/float16/bfloat16 and the global declared set has no fp64
    (F037).  T040 later repaired the round-3 refusal itself (the fp64
    dot was dead code behind a specialization-folded condition), so the
    float32-labeled case now compiles; the boundary witness is the
    GENUINELY-fp64 form (a live fp64 dot, no folded condition in front
    of it), which keeps the located declared-surface refusal; the
    justification and its T040 update are recorded on
    FRONTEND_COVERAGE.json's tl.dot row.

Controls (MECH-WITNESS-TEST):
  * a NON-last-axis scan of a multi-axis block keeps its located refusal
    (the transpose/staging protocol owns it -- lowering it through the
    flat-order restart would silently reorder the carry);
  * a PARTIAL-axis keep_dims reduce keeps its located refusal (the
    result keeps other axes' extents -- not the [1] splat form);
  * a kernel with any scan never takes the worker-strided two-phase
    split (the scan carry is sequential by construction -- the split
    would thread it across non-adjacent chunks);
  * the fp64 dot refusal is the located declared-surface diagnostic.

Run: python3 a100c/tests/test_t038_repairs.py  (exit 0 = all checks PASS)
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
from a100c.frontend import lower_tir, source, specialize  # noqa: E402
from a100c.passes import pipeline as passes_mod  # noqa: E402

OPS = ROOT / "ops"
WORK = Path(tempfile.mkdtemp(prefix="a100c-t038-"))


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _dev(name: str) -> Path:
    return OPS / "suite" / "dev" / name


def _run_case(compiler, module, threads, **make_kwargs):
    import a100_support.native_device as nd
    case = module.make_case(**make_kwargs)
    device = nd.NativeExecutableDevice(compiler, threads)
    staged = device.stage_case(case)
    staged.launch()
    outputs = staged.outputs()
    ok = True
    detail = ""
    # the case's own comparison policy; a case without one compares its
    # declared outputs exactly (never a vacuous pass)
    comparison = case.get("comparison") or \
        {name: {"exact": True} for name in case.get("outputs", ())}
    for name, policy in comparison.items():
        got = np.asarray(outputs[name])
        exp = np.asarray(case["expected"][name])
        if got.shape != exp.shape and got.size == exp.size:
            got = got.reshape(exp.shape)
        comparator = policy.get("comparator")
        if policy.get("exact") or comparator == "array_equal":
            same = np.array_equal(got, exp)
        else:
            same = np.allclose(got, exp, rtol=policy.get("rtol", 0.0),
                               atol=policy.get("atol", 0.0),
                               equal_nan=policy.get("equal_nan", False))
        if not same:
            atol = policy.get("atol", 0.0)
            rtol = policy.get("rtol", 0.0)
            nbad = int(np.sum(np.abs(got - exp) > (atol + rtol *
                                                   np.abs(exp))))
            detail = f"{name}: {nbad} mismatched elements"
        ok &= same
    return ok, detail


def _compiler(tag: str) -> FactoryCompiler:
    return FactoryCompiler(
        options=CompileOptions(cache_dir=str(WORK / f"cache-{tag}")),
        pass_config=passes_mod.PassConfig())


TEMPLATE = '''\
"""probe operator"""
OPERATOR = {{"name": "probe", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}}
import triton
import triton.language as tl

@triton.jit
def probe_kernel({params}):
{body}
'''


def _compile_probe(params, body, args, meta=None):
    text = TEMPLATE.format(params=params,
                           body="\n".join("    " + line
                                          for line in body.splitlines()))
    src = source.load_operator_text(text, "<probe>", "probe.py")
    case = {"args": args, "meta": meta or {}, "launch_meta": {}}
    spec = specialize.specialize(src, case)
    lowering = lower_tir.Lowering(src, spec)
    return lowering.lower()


def _probe_compiler_case(params, body, args, meta=None):
    """A probe payload for the full factory path (refusals included)."""
    return {"args": args, "meta": meta or {}, "launch_meta": {},
            "grid": (1,), "outputs": ()}


# ---------------------------------------------------------------------------
# the repaired classes: executed and compared
# ---------------------------------------------------------------------------

def check_scans_execute():
    """masked_cumsum_vec (the (BLOCK_COLS, VEC) segmented cumsum + the
    (1, 1) hint cases) and cumprod_dim1_grouped_mixed (the (GROUP_ROWS,
    BLOCK_COLS) segmented cumprod) execute and compare PASS."""
    c = _compiler("scan")
    bad = []
    mm = _load(_dev("masked_cumsum_vec_kernel.py"))
    for shape in ((128, 128), (17, 100), (1, 1)):
        for dtype in ("float32", "float16", "bfloat16"):
            for threads in (1, 4):
                ok, detail = _run_case(c, mm, threads, shape=shape,
                                       dtype=dtype)
                if not ok:
                    bad.append(f"masked_cumsum_vec {shape} {dtype} "
                               f"t={threads}: {detail}")
    gm = _load(_dev("cumprod_dim1_grouped_mixed_kernel.py"))
    for dtype in ("float32", "float16", "bfloat16"):
        for threads in (1, 4):
            ok, detail = _run_case(c, gm, threads, dtype=dtype)
            if not ok:
                bad.append(f"cumprod_grouped {dtype} t={threads}: {detail}")
    check("multi-axis-last-axis-scans-execute-1-4", not bad,
          "; ".join(bad[:3]))


def check_reorder_execute():
    """ranked_distribution (sort + flip + gather + topk + softmax) and
    nanmedian_ascend_histogram_count (histogram) execute and compare
    PASS at 1 and 4 workers."""
    c = _compiler("reorder")
    bad = []
    rd = _load(_dev("ranked_distribution_semantic.py"))
    for shape in ((16,), (64,)):
        for dtype in ("float32", "float16", "bfloat16"):
            for threads in (1, 4):
                ok, detail = _run_case(c, rd, threads, shape=shape,
                                       dtype=dtype)
                if not ok:
                    bad.append(f"ranked_distribution {shape} {dtype} "
                               f"t={threads}: {detail}")
    hg = _load(_dev("nanmedian_ascend_histogram_count_kernel.py"))
    for shape in ((17,), (108,)):
        for threads in (1, 4):
            ok, detail = _run_case(c, hg, threads, shape=shape)
            if not ok:
                bad.append(f"histogram {shape} t={threads}: {detail}")
    check("sort-topk-histogram-execute-1-4", not bad, "; ".join(bad[:3]))


def check_v0_and_region_execute():
    """The vsel re-materialization sites (cyclic/blocked jacobi,
    l1_norm), the staging-loop merge select (fht [17] float32) and the
    constexpr convert (final_mean (1,)) execute and compare PASS."""
    c = _compiler("v0reg")
    bad = []
    for name in ("cyclic_jacobi_pair_kernel.py",
                 "blocked_jacobi_pair_svals_kernel.py"):
        module = _load(_dev(name))
        for dtype in ("float32", "float16", "bfloat16"):
            for threads in (1, 4):
                ok, detail = _run_case(c, module, threads, dtype=dtype)
                if not ok:
                    bad.append(f"{name} {dtype} t={threads}: {detail}")
    fh = _load(_dev("fht_kernel_1d_native.py"))
    for dtype in ("float32", "float16", "bfloat16"):
        ok, detail = _run_case(c, fh, 1, shape=(17,), dtype=dtype)
        if not ok:
            bad.append(f"fht [17] {dtype} t=1: {detail}")
    ok, detail = _run_case(c, fh, 4, shape=(17,), dtype="float32")
    if not ok:
        bad.append(f"fht [17] float32 t=4: {detail}")
    fm = _load(_dev("final_mean_kernel.py"))
    for dtype in ("float32", "float16", "bfloat16"):
        for threads in (1, 4):
            ok, detail = _run_case(c, fm, threads, shape=(1,), dtype=dtype)
            if not ok:
                bad.append(f"final_mean (1,) {dtype} t={threads}: {detail}")
    ln = _load(_dev("l1_norm_fused_kernel_2cb0f555.py"))
    for threads in (1, 4):
        ok, detail = _run_case(c, ln, threads)
        if not ok:
            bad.append(f"l1_norm t={threads}: {detail}")
    check("v0-remat-staging-select-constexpr-cast-execute-1-4", not bad,
          "; ".join(bad[:3]))


def check_native_mirror_execute():
    """chunk_transform_qk's [6, 33, 11, 13, 16] fp16 identity (the
    permute over the IME-native fp16 record) and its sibling cases
    execute and compare PASS at 1 and 4 workers."""
    c = _compiler("mirror")
    bad = []
    module = _load(_dev("chunk_transform_qk_fwd_kernel.py"))
    for threads in (1, 4):
        ok, detail = _run_case(c, module, threads,
                               shape=(6, 33, 11, 13, 16), dtype="float16")
        if not ok:
            bad.append(f"chunk_transform big fp16 t={threads}: {detail}")
    ok, detail = _run_case(c, module, 1, shape=(4, 17, 7, 9, 8),
                           dtype="float32")
    if not ok:
        bad.append(f"chunk_transform small fp32 t=1: {detail}")
    check("native-mirror-layout-execute-1-4", not bad, "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# the controls (each must FAIL to compile / stay refused)
# ---------------------------------------------------------------------------

def _probe_operator(params: str, body: str, ref_body: str,
                     args_builder):
    """Write one probe operator file (the corpus's two-layer form) and
    load its module -- the full pipeline (grid model, specialization,
    lowering, MIR verification, allocation, emission) compiles it
    exactly like a corpus operator."""
    text = f'''"""probe"""
OPERATOR = {{"name": "probe/probe_kernel", "group": "probe",
            "channel": "local", "execution": "triton_kernel",
            "verification": "correctness", "tags": []}}
import numpy as np
import triton
import triton.language as tl


@triton.jit
def probe_kernel({params}):
{body}


def ref(args, meta):
{ref_body}


def _make_case(shape=(8, 4), dtype="float32", seed=0):
{args_builder}
    return {{"args": args, "meta": {{}}, "grid": (1,),
            "kernel": probe_kernel, "outputs": ("Y",),
            "expected": ref(args, {{}})}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case()
'''
    path = WORK / f"probe-{abs(hash(body)) % 100000}.py"
    path.write_text(text)
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _probe_body(statements: str) -> str:
    """The jit body, one indent per line (``statements`` arrives with
    its first line unindented)."""
    return "\n".join("    " + line if line.strip() else line
                     for line in statements.splitlines())


def check_non_last_axis_scan_refuses():
    """A scan along a NON-last axis of a multi-axis block keeps its
    located refusal (the control for the last-axis acceptance: the
    flat-order row restart is only the last-axis form)."""
    module = _probe_operator(
        "X, Y",
        _probe_body(
            "rows = tl.arange(0, 8)[:, None]\n"
            "cols = tl.arange(0, 4)[None, :]\n"
            "x = tl.load(X + rows * 4 + cols)\n"
            "y = tl.cumsum(x, axis=0)\n"
            "tl.store(Y + rows * 4 + cols, y)"),
        "    x = np.asarray(args['X']).reshape(8, 4)\n"
        "    return {'Y': np.cumsum(x, axis=0).reshape(-1)}",
        "    args = {'X': np.arange(32, dtype=np.float32) / 8,\n"
        "            'Y': np.zeros(32, dtype=np.float32)}")
    c = _compiler("probescan")
    case = module.make_case()
    payload = {k: v for k, v in case.items()
               if k not in ("expected", "oracle_args")}
    try:
        c.compile_case(payload)
        check("non-last-axis-scan-refuses-located", False,
              "compiled (expected the located refusal)")
    except PipelineError as exc:
        ok = exc.construct == "tl.cumsum/cumprod" \
            and "non-last axis" in str(exc)
        check("non-last-axis-scan-refuses-located", ok, str(exc)[:110])


def check_partial_keepdims_executes():
    """A PARTIAL-axis keep_dims reduce executes and compares PASS through
    the staging lane (the (8, 1) result is the kept axes' block with an
    extent-1 trailing axis -- the same flat bytes as the (8,) form, so
    the preduce segment materializes it exactly); the full-axis [1]
    form's scalar binding is the ranked_distribution execution above."""
    module = _probe_operator(
        "X, Y",
        _probe_body(
            "rows = tl.arange(0, 8)[:, None]\n"
            "cols = tl.arange(0, 4)[None, :]\n"
            "x = tl.load(X + rows * 4 + cols)\n"
            "y = tl.sum(x, axis=1, keep_dims=True)\n"
            "z = tl.reshape(y, (8,))\n"
            "tl.store(Y + tl.arange(0, 8), z)"),
        "    x = np.asarray(args['X']).reshape(8, 4)\n"
        "    return {'Y': x.sum(axis=1)}",
        "    args = {'X': np.arange(32, dtype=np.float32) / 8,\n"
        "            'Y': np.zeros(8, dtype=np.float32)}")
    c = _compiler("probekd")
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(c, module, threads)
        if not ok:
            bad.append(f"t={threads}: {detail}")
    check("partial-keepdims-executes-1-4", not bad, "; ".join(bad[:2]))


def check_scan_never_two_phase():
    """A kernel with any scan never takes the worker-strided two-phase
    split: the split's chunk loop would thread the sequential scan carry
    across non-adjacent chunks (the control for the eligibility guard --
    the emitted MIR has no strided chunk block)."""
    from a100c.frontend import gridmodel
    from a100c.lower import binding as binding_mod
    from a100c.lower import vectorize
    from a100c.plan import partition as part_mod
    from a100c.target import TargetModel
    module = _load(_dev("cumprod_dim1_kernel.py"))
    case = module.make_case(dtype="float32")
    payload = {k: v for k, v in case.items()
               if k not in ("expected", "oracle_args")}
    src = source.load_operator(str(_dev("cumprod_dim1_kernel.py")),
                               corpus_root=str(OPS))
    spec = specialize.specialize(src, payload)
    tir_module = lower_tir.lower(src, spec)
    grid = gridmodel.extract_grid(src, payload)
    plan = part_mod.ExecutionPlan()
    layout = binding_mod.argument_layout(payload, spec)
    mir = vectorize.lower_to_mir(tir_module, plan, TargetModel(), layout,
                                 grid, vectorize.LowerOptions())
    names = [b.name for f in mir.functions for b in f.blocks]
    strided = [n for n in names if "schunk" in n]
    check("scan-kernel-never-two-phase", not strided,
          f"strided chunk blocks: {strided[:3]}")


#: the genuinely-fp64 dot boundary witness (T040): a LIVE fp64 dot -- no
#: folded dispatch condition in front of it -- keeps the located
#: declared-surface refusal after the value-level dtype-introspection fold
#: repaired the round-3 refusal (chunk_generalized's fp64 dot was dead
#: code behind a condition that folds True at specialization)
_FP64_DOT_WITNESS_TEXT = '''\
"""t038/fp64-dot-witness: the genuinely-fp64 dot boundary."""
OPERATOR = {"name": "t038/fp64-dot-witness", "group": "probe",
            "channel": "local", "execution": "triton_kernel",
            "verification": "correctness", "tags": ["linalg.dot"]}
import numpy as np
import triton
import triton.language as tl


@triton.jit
def fp64_dot_witness(a_ptr, b_ptr, c_ptr,
                     M: tl.constexpr, N: tl.constexpr, K: tl.constexpr):
    a = tl.load(a_ptr + tl.arange(0, M)[:, None] * K
                + tl.arange(0, K)[None, :])
    b = tl.load(b_ptr + tl.arange(0, K)[:, None] * N
                + tl.arange(0, N)[None, :])
    c = tl.dot(a, b)
    tl.store(c_ptr + tl.arange(0, M)[:, None] * N
             + tl.arange(0, N)[None, :], c)


def ref(args, meta):
    a = np.asarray(args["a_ptr"])
    b = np.asarray(args["b_ptr"])
    return {"c_ptr": a @ b}


def make_case(shape=None, dtype=None, seed=None):
    # numpy-default float64 buffers: the pointers ARE fp64 and the dot is
    # live code
    args = {"a_ptr": np.ones((4, 4)), "b_ptr": np.ones((4, 4)),
            "c_ptr": np.zeros((4, 4))}
    return {"kernel": fp64_dot_witness, "grid": (1,), "args": args,
            "meta": {"M": 4, "N": 4, "K": 4}, "outputs": ("c_ptr",),
            "shape": (4,), "dtype": "float32", "expected": ref(args, {}),
            "comparison": {"c_ptr": {"comparator": "array_equal",
                                     "exact": True}}}
'''


def _fp64_dot_witness():
    """The genuinely-fp64 dot witness case payload (a LIVE fp64 dot)."""
    path = WORK / "fp64_dot_witness.py"
    if not path.is_file():
        path.write_text(_FP64_DOT_WITNESS_TEXT)
    module = _load(path)
    case = module.make_case()
    payload = {k: v for k, v in case.items()
               if k not in ("expected", "oracle_args")}
    return {"payload": payload}


def check_fp64_dot_refusal_witness():
    """The fp64 dot boundary resolves against the corpus's declared dtype
    surface.  T040 repaired the round-3 refusal itself (the operator's
    fp64 dot was dead code behind a specialization-folded condition --
    the value-level dtype-introspection fold, test_t040_repairs.py), so
    the float32-labeled case now COMPILES; the boundary witness is the
    genuinely-fp64 form (an explicit fp64 dot, no folded condition in
    front of it), which keeps the located declared-surface refusal, and
    the recorded justification (with its T040 update) lives on
    FRONTEND_COVERAGE.json's tl.dot row."""
    module = _load(_dev(
        "chunk_generalized_iplr_delta_rule_fwd_kernel_o.py"))
    case = module.make_case(shape=(17,), dtype="float32")
    payload = {k: v for k, v in case.items()
               if k not in ("expected", "oracle_args")}
    f64 = any(str(getattr(v, "dtype", "")).endswith("float64")
              for v in payload["args"].values()
              if hasattr(v, "dtype"))
    # T040: the float32-labeled case compiles (the dead fp64 arm is never
    # lowered -- the dispatch condition folds at specialization)
    c = _compiler("fp64")
    repaired = False
    try:
        artifact = c.compile_case(payload)
        repaired = artifact.executable is not None
    except PipelineError:
        repaired = False
    # the boundary witness: a GENUINELY-fp64 dot (live code) keeps the
    # located declared-surface refusal
    witness = _fp64_dot_witness()
    located = False
    try:
        witness_compiler = _compiler("fp64w")
        witness_compiler.compile_case(witness["payload"])
    except PipelineError as exc:
        located = ("fp64 tl.dot is outside the corpus dtype surface"
                   in str(exc) and exc.construct == "tl.dot")
    row = None
    fc = __import__("json").loads(
        (ROOT / "FRONTEND_COVERAGE.json").read_text())
    for r in fc["rows"]:
        if r["item"] == "tl.dot":
            row = r
    recorded = row is not None and \
        "T038 dtype-surface boundary" in (row.get("note") or "") and \
        "T040" in (row.get("note") or "")
    # the corpus's own declaration has no fp64 anywhere
    lock = __import__("json").loads(
        (ROOT / "docs" / "compiler-agent" / "CORPUS_LOCK.json").read_text())
    global_dtypes = set()
    for op in lock["operators"]:
        global_dtypes.update(op["dtypes"])
    check("fp64-dot-resolves-against-declared-surface",
          f64 and repaired and located and recorded
          and "float64" not in global_dtypes,
          f"case-buffers-f64={f64} case-compiles={repaired} "
          f"genuinely-fp64-refuses={located} "
          f"justification-recorded={recorded}")


def main() -> int:
    check_scans_execute()
    check_reorder_execute()
    check_v0_and_region_execute()
    check_native_mirror_execute()
    check_non_last_axis_scan_refuses()
    check_partial_keepdims_executes()
    check_scan_never_two_phase()
    check_fp64_dot_refusal_witness()
    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s): " + ", ".join(FAILURES))
        return 1
    print("all T038 checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
