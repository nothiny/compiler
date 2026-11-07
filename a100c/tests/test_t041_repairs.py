#!/usr/bin/env python3
"""test_t041_repairs.py -- the T041 identity-stable grid folding and the
comma-safe resource-evidence path, through the real compilation path
(grid-model extraction -> specialization -> TIR -> native compile ->
execution -> comparison under the case's own policy), with the controls
that prove the checks are load-bearing.

The repaired defects (both recorded by T040 as pre-existing, both proven
fold-independent there):

  * GRID-MODEL BAKING.  chunk_gdn2_fwd_kernel_inter_solve_fused bakes a
    case-tier launch geometry into a shape-independent cache key: the
    ``[17]`` float32 case folds grid axis 1 to the constant 4 (the 1-D
    builder's literals ``B = ... if len(shape) > 1 else 2``,
    ``H = ... else 2``), while the same identity's ``[3,17,2,7]`` case
    correctly ties the axis to the Akkd view extents -- both compiles
    share cache key 020c5b09... but produced different executables, and
    the ``[17]``-compiled artifact leaves (b,h)-blocks >= 4 uncomputed at
    the larger shape (Akk output 0.0 vs reference 1.0).  The general fix
    (a100c/frontend/gridmodel.py): a grid axis may fold to a compile-time
    constant only when the constant is identity-stable -- derived
    exclusively from identity-keyed values (source literals, module
    constants, meta constexprs, dtype folds the pointer dtypes sign);
    never from case-tier data that varies across the SHAPES table of one
    identity.  ``len(shape)`` stays symbolic whenever the operator's own
    SHAPES table mixes arities (24 corpus operators), so the branch it
    selects becomes a hole the ties fill from bundle-visible quantities
    (a scalar argument, a view extent, an identity-tier meta constant) --
    or a located refusal, never a silent fold.  The seed never carries a
    concrete value (the identity signs no seed).

  * HARNESS COMMA PATH.  tools/run_scan.py passed a counts.json path
    containing the case id (shape lists with commas) through QEMU's
    ``-plugin file,out=PATH``, which QEMU splits on commas -- a truncated
    file ``...#[2`` was created and the resource-flagged multi-dim-shape
    cases recorded LAUNCH_FAIL.  The evidence directory name is now
    comma-free (injective over the corpus's case ids).

Checks (each must hold for exit 0):

  * t041-gdn2-model-identity-stable: both shapes of the gdn2 identity
    extract the SAME grid model (identical axes and ties -- runtime reads
    of the T scalar and the Akkd view extents, no literal axis), both
    self-checks pass, and the two shapes share one corpus identity;
  * t041-gdn2-separate-processes: the two shapes compiled in separate
    fresh processes (fresh caches) agree -- one shared key with ONE
    byte-identical artifact (the correct shared artifact), or distinct
    keys; never one key with divergent executables;
  * t041-gdn2-both-compile-orders: the [3,17,2,7] case executes and
    compares PASS when its artifact was compiled from the [17] case first
    (cache-hit reuse) and when compiled cold from its own payload; the
    [17] case also passes on the cold-order cache;
  * t041-control-refusal: a mixed-arity probe whose 1-D builder literal
    has NO bundle-visible tie refuses with a located diagnostic for both
    shapes (never a silent fold); the witness control: with the stability
    rule disabled, the [17] model folds the literal axis again -- the
    pre-fix defect -- so the refusal is load-bearing;
  * t041-comma-unit: the evidence directory name is comma-free and
    injective, and the QEMU plugin argument carries no comma for a
    comma-containing case id;
  * t041-comma-qemu-roundtrip: the instruction-count plugin really writes
    counts.json at the sanitized comma-id path under the pinned QEMU
    (a real RISC-V binary), and the negative control holds: the
    unsanitized comma path is NOT created (QEMU split it there before the
    fix);
  * t041-chunk-abc-resource-evidence: the resource-flagged
    chunk_abc [2,2,17,9,8,4]#float16 case, through the scan driver
    itself: no LAUNCH_FAIL, the instrumented execution runs, the case's
    own comparison passes, and the evidence (execution log with
    instruction counts and multi-worker observation, binding, listing) is
    recorded at the comma-free path; the pre-existing IME-witness
    condition (this case's dot is the fp32 reshape form, so no IME family
    applies to it) is asserted to be recorded honestly, never fabricated.

Run: python3 a100c/tests/test_t041_repairs.py  (exit 0 = all checks PASS)
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
for _p in (str(ROOT / "ops" / "harness"), str(ROOT / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

warnings.filterwarnings("ignore")

FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}", flush=True)
    if not ok:
        FAILURES.append(name)
    return ok


import numpy as np  # noqa: E402

import run_scan as rs                                        # noqa: E402
from a100c.driver import CompileOptions, PipelineError       # noqa: E402
from a100c.factory import FactoryCompiler                    # noqa: E402
from a100c.frontend import source as fe_source               # noqa: E402
from a100c.frontend import gridmodel                         # noqa: E402
from a100c.passes import pipeline as passes_mod              # noqa: E402
from compiler_api import identity as identity_lib            # noqa: E402

GDN2 = "suite/dev/chunk_gdn2_fwd_kernel_inter_solve_fused.py"
CHUNK_ABC = "suite/dev/chunk_abc_fwd_kernel_intra_K.py"
WORK = Path(tempfile.mkdtemp(prefix="a100c-t041-"))


def _rows(operator: str):
    return list(rs.enumerated_rows(rs.DEFAULT_MANIFEST, None, [operator]))


def _case(operator: str, shape, dtype: str):
    rows = _rows(operator)
    row = next(r for r in rows
               if tuple(r["shape"]) == tuple(shape) and r["dtype"] == dtype)
    return rs.build_case(row, 30, use_golden=True), row


def _source(operator: str):
    path = ROOT / "ops" / "suite" / operator.split("/", 1)[1] \
        if not operator.startswith("ops/") else ROOT / operator
    return fe_source.load_operator(str(path))


def _payload(case: dict) -> dict:
    return {k: v for k, v in case.items()
            if k not in ("expected", "oracle_args")}


def _compiler(cache: str) -> FactoryCompiler:
    return FactoryCompiler(options=CompileOptions(cache_dir=cache),
                           pass_config=passes_mod.PassConfig())


# ---------------------------------------------------------------------------
# the one-case worker: runs in its OWN process against one cache dir
# ---------------------------------------------------------------------------

WORKER = r'''\
import argparse
import json
import sys
from pathlib import Path

ROOT = Path({root!r})
for p in (str(ROOT), str(ROOT / "ops" / "harness"), str(ROOT / "tools")):
    if p not in sys.path:
        sys.path.insert(0, p)

import run_scan as rs  # noqa: E402  (loads .env, harness paths)
from a100c.driver import CompileOptions  # noqa: E402
from a100c.factory import FactoryCompiler  # noqa: E402
from a100c.passes import pipeline as passes_mod  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--operator", required=True)
    ap.add_argument("--shape", required=True)
    ap.add_argument("--dtype", default="float32")
    ap.add_argument("--cache", required=True)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--threads", type=int, default=1)
    a = ap.parse_args()
    shape = tuple(json.loads(a.shape))
    rows = list(rs.enumerated_rows(rs.DEFAULT_MANIFEST, None, [a.operator]))
    row = next(r for r in rows
               if tuple(r["shape"]) == shape and r["dtype"] == a.dtype)
    case = rs.build_case(row, 30, use_golden=True)
    compiler = FactoryCompiler(
        options=CompileOptions(cache_dir=a.cache),
        pass_config=passes_mod.PassConfig())
    out = {{}}
    if a.execute:
        import a100_support.native_device as nd
        device = nd.NativeExecutableDevice(compiler, a.threads)
        staged = device.stage_case(case)
        out["key"] = str(staged.artifact.executable.parent.name)
        out["sha256"] = staged.artifact_sha256
        out["cache_hit"] = bool(staged.artifact.cache_hit)
        staged.launch()
        outputs = staged.outputs()
        try:
            verdict = rs.compare_outputs(case, outputs)
            out["compare"] = "PASS"
            out["max_abs_error"] = rs._jsonable(
                verdict.get("max_abs_error", {{}}))
        except Exception as exc:                              # noqa: BLE001
            out["compare"] = "FAIL"
            out["detail"] = f"{{type(exc).__name__}}: {{exc}}".splitlines()[0][:300]
        print(json.dumps(out))
        return 0 if out["compare"] == "PASS" else 1
    artifact = compiler.compile_case(
        {{k: v for k, v in case.items()
          if k not in ("expected", "oracle_args")}})
    out.update(key=str(artifact.executable.parent.name),
               sha256=artifact.sha256,
               cache_hit=bool(artifact.cache_hit),
               identity=artifact.identity)
    print(json.dumps(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def _worker_path() -> Path:
    path = WORK / "t041_worker.py"
    path.write_text(WORKER.format(root=str(ROOT)))
    return path


def _run_worker(operator: str, shape, dtype: str, cache: str,
                execute: bool = False, threads: int = 1, timeout: float = 900):
    command = [sys.executable, str(_worker_path()),
               "--operator", operator, "--shape", json.dumps(list(shape)),
               "--dtype", dtype, "--cache", cache]
    if execute:
        command += ["--execute", "--threads", str(threads)]
    result = subprocess.run(command, capture_output=True, text=True,
                            timeout=timeout, cwd=str(ROOT))
    if result.returncode != 0:
        raise RuntimeError(f"worker failed ({result.returncode}): "
                           f"{result.stdout[-400:]} {result.stderr[-400:]}")
    lines = [line for line in result.stdout.strip().splitlines() if line]
    return json.loads(lines[-1])


# ---------------------------------------------------------------------------
# acceptance[0]: the gdn2 baking defect
# ---------------------------------------------------------------------------

def check_gdn2_model_identity_stable():
    """Both shapes of the gdn2 identity extract the SAME grid model: every
    axis is a runtime read (the T scalar, the Akkd view extents), no axis
    is a baked literal, both self-checks pass, and the shapes share one
    corpus identity (so one artifact must serve both)."""
    src = _source(GDN2)
    models = {}
    identities = {}
    for shape in ([17], [3, 17, 2, 7]):
        case, row = _case(GDN2, shape, "float32")
        model = gridmodel.extract_grid(src, case)
        models[tuple(shape)] = model
        identities[tuple(shape)] = identity_lib.case_identity(
            row["operator"], case, tier="meta")
        literal_axis = any(isinstance(a, gridmodel.Lit)
                           for a in model.axes)
        if literal_axis:
            check("t041-gdn2-model-identity-stable", False,
                  f"axis folded to a literal for shape {shape}")
            return
    same_identity = identities[(17,)] == identities[(3, 17, 2, 7)]
    same_axes = (repr(models[(17,)].axes) == repr(models[(3, 17, 2, 7)].axes))
    same_ties = models[(17,)].ties == models[(3, 17, 2, 7)].ties
    reads = all(
        leaf.kind in ("bundle_scalar", "bundle_view")
        for axis in models[(17,)].axes
        for leaf in gridmodel._grid_leafs(axis))
    check("t041-gdn2-model-identity-stable",
          same_identity and same_axes and same_ties and reads,
          f"axes={models[(17,)].axes!r} ties={models[(17,)].ties} "
          f"shared-identity={same_identity} all-runtime-reads={reads}")


def check_gdn2_separate_processes():
    """The two shapes compiled in separate fresh processes (each with its
    own cold cache) agree: one shared key whose artifact is byte-identical
    (the shared artifact is correct at both shapes), or distinct keys.
    The pre-fix defect was one shared key with DIFFERENT executables."""
    r17 = _run_worker(GDN2, [17], "float32", str(WORK / "cache-p17"))
    r47 = _run_worker(GDN2, [3, 17, 2, 7], "float32", str(WORK / "cache-p47"))
    shared_key = r17["key"] == r47["key"]
    identical = r17["sha256"] == r47["sha256"]
    ok = (shared_key and identical) or (not shared_key)
    check("t041-gdn2-separate-processes", ok,
          f"[17]: key={r17['key'][:12]} sha={r17['sha256'][:12]} "
          f"cache_hit={r17['cache_hit']}; [3,17,2,7]: "
          f"key={r47['key'][:12]} sha={r47['sha256'][:12]} "
          f"cache_hit={r47['cache_hit']}; shared-key={shared_key} "
          f"byte-identical={identical}")


def check_gdn2_both_compile_orders():
    """The [3,17,2,7] case compares PASS under BOTH compile orders:
    order A compiles the [17] case first and the [3,17,2,7] execution
    reuses that artifact through the cache; order B compiles [3,17,2,7]
    cold from its own payload.  The [17] case also passes on order B's
    cache (the shared artifact serves both shapes)."""
    # order A: [17] first, then execute [3,17,2,7] as a cache hit
    cache_a = str(WORK / "cache-order-a")
    _run_worker(GDN2, [17], "float32", cache_a)
    a47 = _run_worker(GDN2, [3, 17, 2, 7], "float32", cache_a, execute=True)
    # order B: [3,17,2,7] cold, then [17] as a cache hit
    cache_b = str(WORK / "cache-order-b")
    b47 = _run_worker(GDN2, [3, 17, 2, 7], "float32", cache_b, execute=True)
    b17 = _run_worker(GDN2, [17], "float32", cache_b, execute=True)
    ok = (a47["compare"] == "PASS" and a47["cache_hit"]
          and b47["compare"] == "PASS" and not b47["cache_hit"]
          and b17["compare"] == "PASS" and b17["cache_hit"])
    check("t041-gdn2-both-compile-orders", ok,
          f"order-A [3,17,2,7]: {a47['compare']} cache_hit={a47['cache_hit']}"
          f" max_err={a47.get('max_abs_error')}; "
          f"order-B [3,17,2,7]: {b47['compare']} "
          f"cache_hit={b47['cache_hit']}; "
          f"order-B [17]: {b17['compare']} cache_hit={b17['cache_hit']}")


# ---------------------------------------------------------------------------
# acceptance[0], the control: a non-identity-stable literal axis with no tie
# ---------------------------------------------------------------------------

BAKE_PROBE_TEXT = '''\
"""t041/bake-probe: a mixed-arity SHAPES table whose 1-D builder's grid
literal has no bundle-visible tie -- the control: a located refusal, never
a silent fold."""
OPERATOR = {"name": "t041/bake-probe", "group": "basic", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar"]}
import numpy as np
import triton
import triton.language as tl

SHAPES = ((17,), (3, 17, 2, 7))
DTYPES = ("float32",)


@triton.jit
def bake_probe(x_ptr, y_ptr, N):
    pid = tl.program_id(0)
    offs = pid * 64 + tl.arange(0, 64)
    mask = offs < N
    tl.store(y_ptr + offs, tl.load(x_ptr + offs, mask=mask), mask=mask)


def ref(args, meta):
    x = np.asarray(args["x_ptr"])
    return {"y_ptr": x.copy()}


def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=0):
    del dtype, seed
    import numpy as np
    N = int(shape[0])
    # B varies across the SHAPES table (2 for the 1-D builder, 3 for the
    # 4-D one) and NOTHING bundle-visible carries it: x/y are shaped by N,
    # the only scalar is N, meta is empty -- the grid axis cannot tie
    B = int(shape[0]) if len(shape) > 1 else 2
    x = np.arange(N, dtype=np.float32)
    args = {"x_ptr": x, "y_ptr": np.zeros(N, np.float32), "N": N}
    meta = {}
    grid = (B,)
    return {"kernel": bake_probe, "grid": grid, "args": args, "meta": meta,
            "launch_meta": {}, "outputs": ("y_ptr",),
            "shape": tuple(shape), "dtype": "float32",
            "expected": ref(args, meta),
            "comparison": {"y_ptr": {"comparator": "array_equal",
                                     "exact": True}}}


def make_case(shape=None, dtype=None, seed=None):
    options = {}
    if shape is not None:
        options["shape"] = tuple(shape)
    case = _make_case(**options)
    case.setdefault("outputs", tuple(case["expected"]))
    return case
'''


def _bake_probe_paths():
    path = WORK / "bake_probe.py"
    if not path.is_file():
        path.write_text(BAKE_PROBE_TEXT)
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, fe_source.load_operator(str(path))


def check_control_refusal():
    """The bake-probe's untied case-tier literal refuses, located, for both
    shapes of its mixed-arity family; with the stability rule disabled the
    [17] model folds the literal axis again (the pre-fix silent fold), so
    the refusal is load-bearing (MECH-WITNESS-TEST)."""
    module, src = _bake_probe_paths()
    cache = str(WORK / "cache-bake-probe")
    refused = {}
    for shape in ([17], [3, 17, 2, 7]):
        case = module.make_case(shape=shape)
        try:
            model = gridmodel.extract_grid(src, case)
            refused[tuple(shape)] = f"extracted {model.axes!r}"
        except gridmodel.GridError as exc:
            refused[tuple(shape)] = f"{exc.path}:{exc.line}:{exc.col}: " \
                                    f"{exc.construct}: {exc.message}"
        try:
            _compiler(cache).compile_case(_payload(case))
            compiled = "compiled"
        except PipelineError as exc:
            compiled = f"refused: {exc}"
        except Exception as exc:                               # noqa: BLE001
            compiled = f"crash: {type(exc).__name__}: {exc}"
        if not (refused[tuple(shape)].startswith(str(WORK))
                and compiled.startswith("refused: ")):
            check("t041-control-refusal", False,
                  f"shape {shape}: model={refused[tuple(shape)]} "
                  f"compile={compiled[:200]}")
            return
    # the witness control: the stability rule disabled -> the [17] model
    # folds the literal axis again (the pre-fix defect)
    case17 = module.make_case(shape=[17])
    real = gridmodel._shape_arity_stable
    gridmodel._shape_arity_stable = lambda source: True
    try:
        model = gridmodel.extract_grid(src, case17)
        folded = any(isinstance(a, gridmodel.Lit) and a.value == 2
                     for a in model.axes)
        folded_detail = repr(model.axes)
    except gridmodel.GridError as exc:
        folded, folded_detail = False, f"still refuses: {exc}"
    finally:
        gridmodel._shape_arity_stable = real
    check("t041-control-refusal", folded,
          "both shapes refuse located ("
          f"[17]: {refused[(17,)].split(': ', 1)[-1][:120]}); "
          f"stability-rule-disabled control folds axis 2: {folded_detail}")


# ---------------------------------------------------------------------------
# acceptance[1]: the comma-safe resource-evidence path
# ---------------------------------------------------------------------------

COMMA_ID = ("suite/dev/chunk_abc_fwd_kernel_intra_K.py#"
            + json.dumps([2, 2, 17, 9, 8, 4]) + "#float16")


def check_comma_unit():
    """The evidence directory name is comma-free and injective over
    comma-containing case ids, and the QEMU plugin argument built from it
    carries no comma (the pre-fix argument was split at the shape list).
    Injectivity is over the id grammar the scan can produce (operator path,
    a json.dumps int-list shape, a dtype name): the shape list contains no
    underscore, so the comma -> _ mapping cannot collide."""
    samples = [
        COMMA_ID,
        "suite/dev/chunk_abc_fwd_kernel_intra_K.py#[2,2,17,9,8,4]#bfloat16",
        "suite/dev/chunk_abc_fwd_kernel_intra_K.py#[1,3,33,13,16,4]#float16",
        "suite/dev/copy_last_chunk_kernel.py#[3,17,1,6,5]#float32",
        "suite/dev/jagged_to_padded_dense_forward_kernel.py"
        "#[8,16,11,9,8,7,13,10,15,12]#float16",
    ]
    names = [rs.evidence_dir_name(s) for s in samples]
    injective = len(set(names)) == len(names)
    grammar = all("_" not in s.split("#")[1] and "," not in s.split("#")[2]
                  for s in samples)
    raw = rs.evidence_dir_name(COMMA_ID)
    work = WORK / "comma-unit" / raw
    work.mkdir(parents=True, exist_ok=True)
    command = rs._instrumented_command(
        Path("/tmp/fake-exec"), Path("/tmp/fake-bundle"), 4,
        Path("/tmp/fake-plugin.so"), work / "counts.json")
    plugin_arg = command[command.index("-plugin") + 1]
    comma_free = "," not in plugin_arg.split("out=", 1)[1]
    check("t041-comma-unit",
          "," not in raw and comma_free and injective and grammar,
          f"dir={raw} plugin-arg-out={plugin_arg.split('out=', 1)[1]} "
          f"injective={injective} grammar={grammar}")


def check_comma_qemu_roundtrip():
    """A REAL round-trip through the pinned QEMU: the instruction-count
    plugin writes counts.json at the sanitized comma-id path; the negative
    control (the pre-fix unsanitized path) is NOT created because QEMU
    splits the argument at the comma."""
    qemu = os.environ.get("A100_QEMU")
    cpu = os.environ.get("A100_QEMU_CPU",
                         "max,vlen=1024,elen=64,vext_spec=v1.0")
    sysroot = os.environ.get("A100_SYSROOT")
    probe = ROOT / "a100_support" / "build" / "matrix_probe"
    plugin = ROOT / "a100_support" / "build" / "instruction_counts.so"
    if not (qemu and sysroot and probe.is_file() and plugin.is_file()):
        check("t041-comma-qemu-roundtrip", False,
              "missing QEMU/plugin/probe in the declared environment")
        return
    good_dir = WORK / "qemu-roundtrip" / rs.evidence_dir_name(COMMA_ID)
    good_dir.mkdir(parents=True, exist_ok=True)
    good_counts = good_dir / "counts.json"
    result = subprocess.run(
        [qemu, "-L", sysroot, "-cpu", cpu,
         "-plugin", f"{plugin},out={good_counts}",
         str(probe), "int8"],
        capture_output=True, text=True, timeout=120)
    wrote = good_counts.is_file()
    parsed = False
    if wrote:
        try:
            data = json.loads(good_counts.read_text())
            parsed = "instructions" in data
        except ValueError:
            parsed = False
    # the negative control: the pre-fix path (the raw comma id) is split
    bad_dir = WORK / "qemu-roundtrip" / COMMA_ID.replace("/", "__")
    bad_dir.mkdir(parents=True, exist_ok=True)
    bad_counts = bad_dir / "counts.json"
    subprocess.run(
        [qemu, "-L", sysroot, "-cpu", cpu,
         "-plugin", f"{plugin},out={bad_counts}",
         str(probe), "int8"],
        capture_output=True, text=True, timeout=120)
    split_evidence = not bad_counts.is_file()
    check("t041-comma-qemu-roundtrip",
          result.returncode == 0 and wrote and parsed and split_evidence,
          f"qemu exit {result.returncode}, counts at the sanitized path: "
          f"{wrote} (parsed={parsed}); unsanitized comma path created: "
          f"{not split_evidence} (the pre-fix split)")


def check_chunk_abc_resource_evidence():
    """The resource-flagged chunk_abc [2,2,17,9,8,4]#float16 case, through
    the scan driver itself: the comma-containing case id no longer breaks
    the instrumented launch (the pre-fix LAUNCH_FAIL) -- the case executes,
    its comparison passes, and its evidence is recorded (execution log with
    instruction counts and multi-worker observation, binding, listing) at
    the comma-free path.

    The row's final status can still be EVIDENCE_FAIL on the declared IME
    instruction witnesses (smt.vmadot AND smt.vfwmadot in this artifact):
    that condition is PRE-EXISTING and independent of the comma path --
    this case's source-level dot is the fp32 reshape form (K < 16, so no
    IME family applies), and even the perf representative carries only
    smt.vfwmadot.  The check asserts that unmet condition is recorded
    honestly (never a fabricated pass) and reports it in the detail; the
    harness defect this task repairs is the LAUNCH_FAIL."""
    report = WORK / "chunk-abc-report.json"
    command = [sys.executable, str(ROOT / "tools" / "run_scan.py"), "run",
               "--operator", CHUNK_ABC, "--threads", "1",
               "--flag-resource", COMMA_ID,
               "--report", str(report)]
    result = subprocess.run(command, capture_output=True, text=True,
                            timeout=1800, cwd=str(ROOT))
    if result.returncode != 0:
        check("t041-chunk-abc-resource-evidence", False,
              f"run_scan exit {result.returncode}: "
              f"{result.stdout[-500:]} {result.stderr[-300:]}")
        return
    data = json.loads(report.read_text())
    row = next((r for r in data["cases"] if r["id"] == COMMA_ID), None)
    if row is None:
        check("t041-chunk-abc-resource-evidence", False,
              f"case {COMMA_ID} missing from the report")
        return
    observations = row.get("resource_observations") or {}
    workers = observations.get("workers") or []
    active = [w for w in workers if w.get("completed_units", 0) > 0]
    units = {w.get("unit") for w in active}
    evidence_root = report.parent / "resource-evidence"
    evidence_dir = evidence_root / rs.evidence_dir_name(COMMA_ID)
    log_path = evidence_dir / "execution_log.json"
    binding_path = evidence_dir / "binding.json"
    listing_path = evidence_dir / "listing.S"
    log = json.loads(log_path.read_text()) if log_path.is_file() else {}
    comma_free = "," not in str(evidence_dir)
    no_launch_fail = row["status"] != "LAUNCH_FAIL"
    executed = bool(row.get("executed")) and observations.get("exit_code") == 0
    compared_pass = (row.get("compared") and row["status"] in
                     ("PASS", "EVIDENCE_FAIL"))
    evidence_recorded = (log_path.is_file() and binding_path.is_file()
                         and listing_path.is_file()
                         and log.get("instruction_counts") is not None
                         and log.get("case_id") == COMMA_ID)
    multi_worker = len(active) >= 2 and len(units) >= 2
    witness_gap_recorded = ("instruction witness" in (row.get("detail") or "")) \
        if row["status"] == "EVIDENCE_FAIL" else True
    ok = (no_launch_fail and executed and compared_pass and evidence_recorded
          and multi_worker and comma_free and witness_gap_recorded)
    detail = (f"status={row['status']} executed={executed} "
              f"compared-pass={compared_pass} evidence-files="
              f"{evidence_recorded} active-workers={len(active)} "
              f"distinct-units={len(units)} comma-free-dir={comma_free} "
              f"detail={row.get('detail', '')[:90]}")
    check("t041-chunk-abc-resource-evidence", ok, detail)


# ---------------------------------------------------------------------------

def main() -> int:
    check_gdn2_model_identity_stable()
    check_gdn2_separate_processes()
    check_gdn2_both_compile_orders()
    check_control_refusal()
    check_comma_unit()
    check_comma_qemu_roundtrip()
    check_chunk_abc_resource_evidence()
    if FAILURES:
        print(f"\n{len(FAILURES)} check(s) failed: {FAILURES}",
              file=sys.stderr)
        return 1
    print("\nall t041 checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
