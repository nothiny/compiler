#!/usr/bin/env python3
"""test_scan_report.py -- the full input scan report validation (T019, G7).

The scan (tools/run_scan.py, T017) executed the whole declared corpus --
2734 cases, suite/dev 2192 + suite/perf 542, in the corpus's own declared
order -- on the declared QEMU endpoint, compared every case against its own
reference under its own comparison policy, and bound the run to a prepared
input-regression invocation.  This test validates the produced evidence
against the task's acceptance refs:

  acceptance[0] the report covers all 2734 declared cases with per-case rows
                (compiled, executed, compared, passed, artifact identity);
                no case is skipped or substituted (ids re-enumerated through
                the corpus's own harness; per-row operator/shape/dtype match
                the sealed manifest; one artifact per compile identity -- no
                shape/grid/value baking);
  acceptance[1] every feature class (the corpus manifest's operator family)
                is validated at each of 1, 2, 4 and 8 workers somewhere in
                the scan; the representative resource-evidence rows are
                executed at all four counts (with repetition) and identified;
                F018's aspects (coverage, tails, ownership, visibility,
                repeated execution) are present at every count;
  acceptance[2] failures are classified by feature class and first incorrect
                stage; the census totals reconcile (classes sum to failures,
                stages sum to failures, unclassified bounded with a recorded
                reason); worker-count-only findings are recorded;
  acceptance[3] the report is an input-regression/v1 report acceptable by
                regression-record when bound to a prepared run: schema
                conformance is re-verified here against the sealed run
                (compiler_agent.regression.check_report), the engine's
                recorded binding (report_sha256) matches the report bytes,
                and negative controls prove the conformance check can fail.

Evidence layout (docs/compiler-agent/SCAN_T019/):
  manifest.json                      the sealed input-regression/v1 manifest
  run/report.json                    the primary scan report (recorded)
  run/report.json.summary.json       the driver's acceptance summary
  run/resource-evidence/<case>/      representative captures (primary run)
  workers/manifest-nodot.json        corpus manifest copy with the two rep
                                     operators' dot.matmul tag removed, so
                                     the representative cases can execute as
                                     plain rows at the one-worker baseline
                                     through the same driver path
  workers/threads-{2,4,8}/           stratified class subsets per count
  workers/reps-threads-{1a,1b,2a,2b,4a,4b,8a,8b}/
                                     representative rows at each count,
                                     repeated (a and b)
  workers/coverage.json              consolidated worker-count evidence
  census.json                        the classified failure census

Run: python3 a100c/tests/test_scan_report.py   (exit 0 = all checks PASS)

Controls (MECH-WITNESS-TEST): the schema checks are exercised against
deliberately corrupted in-memory reports (partial, duplicated, unknown id,
inconsistent booleans, wrong run) and must be refused; the census
reconciliation is exercised against a census with an extra unaccounted row
and must fail; the comparison entry is exercised against a corrupted output
(must fail under the case's own tolerance) and a widened scratch tolerance
(must then pass) -- the tolerance is read from the case, never from the
compiler (IR-NUMERIC-POLICY).
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
import warnings  # noqa: E402

warnings.filterwarnings("ignore")

import numpy as np  # noqa: E402

FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}", flush=True)
    if not ok:
        FAILURES.append(name)
    return ok


# ---------------------------------------------------------------------------
# the scan driver module (the same code path that executed the scan)
# ---------------------------------------------------------------------------

_spec = importlib.util.spec_from_file_location("run_scan_for_report",
                                               ROOT / "tools" / "run_scan.py")
rs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rs)                                    # noqa: E402

SCAN = ROOT / "docs" / "compiler-agent" / "SCAN_T019"
CORPUS_MANIFEST = str(ROOT / "ops" / "suite" / "manifest.json")
COUNTS = (1, 2, 4, 8)
WORKER_COUNTS = (2, 4, 8)
#: cross-worker merge / stage structures (F018 visibility): operators whose
#: kernels split work across workers and merge it back
VIS_TAGS = frozenset(("pat.persistent_reduce", "pat.k_loop", "red.axis",
                      "dot.matmul"))
#: the two anchors executed at every count so the F018 aspect set is
#: deterministic: ragged-tail elementwise (absolute_kernel: extents 17/97,
#: masked load+store) and a persistent reduction (fused_l1_norm: 128/127)
ANCHORS = ("suite/dev/absolute_kernel.py",
           "suite/dev/fused_l1_norm_kernel_76761630.py")
REP_OPERATORS = ("suite/dev/chunk_abc_fwd_kernel_intra_K.py",
                 "suite/perf/batched_vecmat_mult.py")
#: powers of two up to the corpus's largest extent: an extent outside this
#: set cannot be a multiple of a power-of-two block extent, so the case
#: exercises vector tails (A100-VECTOR: small, ragged and large inputs)
_POW2 = {1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024}

STATUS_VOCAB = frozenset(("PASS", "CASE_FAIL", "COMPILE_REFUSED", "LAUNCH_FAIL",
                          "TIMEOUT", "MISMATCH", "EVIDENCE_FAIL"))
#: the declared stage vocabulary of the census, by status (acceptance[2])
STAGE_BY_STATUS = {
    "CASE_FAIL": {"case-build"},
    "COMPILE_REFUSED": {"compile-refused"},
    "LAUNCH_FAIL": {"native-staging", "native-launch"},
    "TIMEOUT": {"case-build", "native-staging", "native-launch", "compare"},
    "MISMATCH": {"execution-mismatch"},
    "EVIDENCE_FAIL": {"resource-evidence"},
}
HEX64 = set("0123456789abcdef")


def is_sha256(text) -> bool:
    return (isinstance(text, str) and len(text) == 64
            and all(c in HEX64 for c in text))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text())


def nonpow2_extent(shape) -> bool:
    return any(int(v) not in _POW2 for v in shape)


def project_relative(reference) -> bool:
    """An evidence path the engine can resolve: relative, inside the root."""
    if not isinstance(reference, str) or not reference or reference.startswith("/"):
        return False
    parts = Path(reference).parts
    return ".." not in parts


# ---------------------------------------------------------------------------
# the corpus's own metadata (feature classes / tags -- never a compiler
# artifact): operator -> family, operator -> tags
# ---------------------------------------------------------------------------

corpus_manifest = load_json(ROOT / "ops" / "suite" / "manifest.json")
OPERATOR_FAMILY = {}
OPERATOR_TAGS = {}
for entry in corpus_manifest["operators"]:
    OPERATOR_FAMILY[entry["path"]] = entry["family"]
    OPERATOR_TAGS[entry["path"]] = frozenset(entry.get("tags") or ())
FAMILIES = sorted(set(OPERATOR_FAMILY.values()))


def stratified_stratum(threads: int):
    """The deterministic stratified class subset for one worker count.

    Per family, the operators sorted by path, positions [i::3] (i = count
    index 0/1/2 for 2/4/8), first two picks; plus the anchors; the
    representative operators are excluded from the picks (their cases are
    executed by the dedicated representative runs at every count).
    """
    index = WORKER_COUNTS.index(threads)
    by_family = {}
    for path, family in OPERATOR_FAMILY.items():
        if path in REP_OPERATORS or path in ANCHORS:
            continue
        by_family.setdefault(family, []).append(path)
    picks = list(ANCHORS)
    for family in FAMILIES:
        operators = sorted(by_family.get(family, []))
        picks.extend(operators[index::3][:2])
    return picks


# ---------------------------------------------------------------------------
# 1. the sealed manifest (acceptance[0]: every declared case, no substitution)
# ---------------------------------------------------------------------------

manifest = load_json(SCAN / "manifest.json")
mcases = manifest["cases"]
mrows = {case["id"]: case for case in mcases}

check("manifest-schema", manifest.get("schema") == rs.SCHEMA,
      f"schema={manifest.get('schema')}")
check("manifest-covers-2734", len(mcases) == 2734, f"cases={len(mcases)}")
check("manifest-ids-unique", len(mrows) == len(mcases))
totals = {}
for case in mcases:
    totals[case["group"]] = totals.get(case["group"], 0) + 1
check("manifest-group-totals", totals == {"suite/dev": 2192, "suite/perf": 542},
      str(totals))
check("manifest-comparison-policies",
      all(isinstance(c.get("comparison"), dict) and c["comparison"]
          for c in mcases),
      "every case retains its declared per-output comparison policy")
check("manifest-resource-flags-bool",
      all(type(c.get("resource_evidence")) is bool for c in mcases))
declared_identities = {c["identity"] for c in mcases}
check("manifest-identity-census",
      manifest["census"]["cases"] == len(mcases)
      and manifest["census"]["identities"] == len(declared_identities),
      f"identities={len(declared_identities)} (recomputed from the rows)")

# no substitution: re-enumerate through the corpus's own harness (~2 s) and
# require the exact id sequence of the sealed manifest
enumerated = [row["id"] for row in rs.enumerated_rows(CORPUS_MANIFEST)]
check("manifest-equals-harness-enumeration",
      enumerated == [c["id"] for c in mcases],
      f"{len(enumerated)} harness rows, order preserved")

# the representative rows are the run's own recorded rule output: the
# manifest seals them at prepare time.  Recomputing today's rule here
# would demand a historical run match a rule that may have evolved since
# (the per-family representative rule, IME_PATTERN_DTYPES); what this
# report proves is the RUN's self-consistency -- the sealed manifest's
# representatives are exactly the rows the run flagged, and the rule
# that produced them is recorded alongside them
reps_expected = manifest["representative_resource_cases"]
check("representatives-recorded-by-the-run",
      isinstance(reps_expected, dict) and bool(reps_expected)
      and isinstance(manifest.get("representative_rule"), str)
      and bool(manifest["representative_rule"].strip()),
      str(reps_expected))
flagged = sorted(c["id"] for c in mcases if c["resource_evidence"])
check("representatives-flagged",
      flagged == sorted(reps_expected.values()), str(flagged))

# ---------------------------------------------------------------------------
# 2. the primary report (acceptance[0])
# ---------------------------------------------------------------------------

report_path = SCAN / "run" / "report.json"
report = load_json(report_path)
rows = report["cases"]
by_id = {row["id"]: row for row in rows}

check("report-schema", report.get("schema") == rs.SCHEMA)
check("report-run-id", bool(report.get("run_id")), report.get("run_id"))
check("report-command-recorded",
      isinstance(report.get("command"), str) and bool(report["command"].strip()))
check("report-complete", report.get("partial") is False
      and not report.get("missing_case_ids"),
      f"partial={report.get('partial')}")
check("report-covers-2734", len(rows) == 2734, f"rows={len(rows)}")
check("report-ids-unique", len(by_id) == len(rows))
check("report-ids-equal-manifest",
      [r["id"] for r in rows] == [c["id"] for c in mcases],
      "same ids, same declared order (no case skipped or substituted)")

# per-case rows: the four booleans, the identity fields, no substitution of
# operator/shape/dtype/group
shape_ok = status_ok = bool_ok = artifact_ok = True
for row in rows:
    mcase = mrows[row["id"]]
    if (row["group"] != mcase["group"] or row["operator"] != mcase["operator"]
            or row["shape"] != mcase["shape"] or row["dtype"] != mcase["dtype"]):
        shape_ok = False
    if row["status"] not in STATUS_VOCAB:
        status_ok = False
    if not all(type(row.get(k)) is bool
               for k in ("compiled", "executed", "compared", "passed")):
        bool_ok = False
    if row["passed"] and not (row["compiled"] and row["executed"]
                              and row["compared"]):
        bool_ok = False
    if row["compared"] and not row["executed"]:
        bool_ok = False
    if row["compiled"] and not (is_sha256(row.get("artifact_sha256"))
                                and isinstance(row.get("artifact_key"), str)
                                and row["artifact_key"]
                                and isinstance(row.get("identity"), str)
                                and row["identity"]):
        artifact_ok = False
check("rows-match-manifest-case-identity", shape_ok)
check("rows-status-vocabulary", status_ok)
check("rows-boolean-contract", bool_ok,
      "passed => compiled&executed&compared; compared => executed")
check("rows-artifact-identity", artifact_ok,
      "every compiled row records artifact sha256 + cache key + compile identity")

# no shape/grid/value baking: every case of one artifact key executes the
# SAME executable bytes (the T041 gdn2 defect class: one key, two programs).
# The reverse direction is NOT an invariant: one corpus meta identity may
# legitimately map to several artifact keys when its cases carry different
# argument signatures (verified against the case payloads below).
sha_by_key = {}
bake_violations = []
for row in rows:
    if not row.get("compiled"):
        continue
    previous = sha_by_key.setdefault(row["artifact_key"], row["artifact_sha256"])
    if previous != row["artifact_sha256"]:
        bake_violations.append(row["id"])
check("no-key-baking", not bake_violations,
      f"{len(sha_by_key)} artifact keys; violations={bake_violations[:3]}")
key_by_identity = {}
for row in rows:
    if row.get("compiled"):
        key_by_identity.setdefault(row["identity"], set()).add(row["artifact_key"])
identity_key_splits = {identity: sorted(keys)
                       for identity, keys in key_by_identity.items()
                       if len(keys) > 1}

statuses = {}
for row in rows:
    statuses[row["status"]] = statuses.get(row["status"], 0) + 1
check("statuses-sum-to-cases", sum(statuses.values()) == 2734, str(statuses))

summary = load_json(SCAN / "run" / "report.json.summary.json")
check("summary-consistent",
      summary["run"]["cases_enumerated"] == 2734
      and summary["run"]["rows_reported"] == 2734
      and summary["checks"]["report_complete"] is True
      and summary["census"]["cases"] == 2734
      and summary["run"]["threads"] == 1
      and summary["run"]["resource_threads"] == 4,
      f"threads={summary['run']['threads']} "
      f"resource_threads={summary['run']['resource_threads']}")
check("summary-compile-economics",
      summary["checks"]["compile_count_le_identity_census_1_25x"] is True,
      f"compile count {summary['compile']['count']} vs identities "
      f"{summary['census']['identities']} (<= 1.25x)")

# ---------------------------------------------------------------------------
# 3. engine binding: acceptable by regression-record (acceptance[3])
# ---------------------------------------------------------------------------

from compiler_agent import regression as engine_regression  # noqa: E402
from compiler_agent import resource_evidence as engine_resources  # noqa: E402

state = load_json(ROOT / "docs" / "compiler-agent" / "PROJECT_STATE.json")
run_id = report["run_id"]
run_ref = (state.get("regression_runs") or {}).get(run_id)
check("prepared-run-registered", bool(run_ref), run_id)
run = load_json(ROOT / run_ref["path"]) if run_ref else {}
check("prepared-run-seals-this-manifest",
      run.get("manifest_sha256")
      == engine_regression.digest(sorted(mcases, key=lambda c: c["id"]))
      and [c["id"] for c in run.get("cases", [])] == sorted(mrows),
      "the sealed run enumerates exactly the manifest's cases")

# the report satisfies regression-record's own conformance check
try:
    recorded_failures = engine_regression.check_report(run, report)
    conformance = "ok"
except ValueError as exc:
    conformance = f"refused: {exc}"
    recorded_failures = []
check("regression-record-conformance", conformance == "ok", conformance)
check("regression-record-failures-are-the-report-failures",
      sorted(f["id"] for f in recorded_failures)
      == sorted(r["id"] for r in rows if not r["passed"]),
      f"{len(recorded_failures)} failing rows")

# the engine accepted and bound this exact report (regression-record was run)
check("regression-record-binding",
      bool(run_ref.get("report_sha256"))
      and run_ref["report_sha256"] == sha256_file(report_path),
      "report_sha256 binding matches the report bytes")

# resource rows that pass must carry inspectable evidence; resource rows
# that fail must record the unmet condition honestly (never a fabricated pass)
resource_rows_ok = True
resource_details = []
for case_id in sorted(reps_expected.values()):
    row = by_id[case_id]
    binding = row.get("resource_evidence")
    observations = row.get("resource_observations") or {}
    if row["passed"]:
        result = engine_resources.inspect(
            ROOT, binding["path"], run_id=run_id, case_id=case_id,
            artifact_sha256=row.get("artifact_sha256"), require_execution=True)
        if not result["ok"]:
            resource_rows_ok = False
            resource_details.append(f"{case_id}: {result['errors'][:2]}")
    else:
        # an unmet condition is named, and the observation is still bound to
        # this run/case/artifact on disk
        if not (isinstance(row.get("detail"), str) and row["detail"].strip()
                and isinstance(observations.get("instruction_counts"), dict)
                and isinstance(observations.get("workers"), list)):
            resource_rows_ok = False
            resource_details.append(f"{case_id}: missing honest failure record")
check("resource-rows-honest", resource_rows_ok,
      "; ".join(resource_details[:3]) if resource_details
      else "no passing resource rows to inspect; failing rows record their "
           "unmet condition")


# negative controls: the conformance check must refuse corrupted reports
def refuses(mutate, expected_fragment: str) -> bool:
    mutated = copy.deepcopy(report)
    mutate(mutated)
    try:
        engine_regression.check_report(run, mutated)
    except ValueError as exc:
        return expected_fragment in str(exc)
    return False


check("control-partial-report-refused",
      refuses(lambda r: r.__setitem__("cases", r["cases"][:-1]), "partial"),
      "dropping the last row must be refused")
check("control-duplicate-row-refused",
      refuses(lambda r: r["cases"].append(r["cases"][0]), "duplicate"))
check("control-unknown-case-refused",
      refuses(lambda r: r["cases"][0].__setitem__(
          "id", "suite/dev/nope.py#[1]#float32"), "unknown"))
_first_passing = next((i for i, r in enumerate(rows) if r["passed"]), 0)
check("control-inconsistent-booleans-refused",
      refuses(lambda r: r["cases"][_first_passing].update(
          {"compiled": False}), "must have been compiled"),
      "a passing row with compiled=false must be refused")
check("control-wrong-run-refused",
      refuses(lambda r: r.__setitem__("run_id", "0" * 32), "another regression"))

# ---------------------------------------------------------------------------
# 4. comparison policy preservation (IR-NUMERIC-POLICY control)
# ---------------------------------------------------------------------------

# a deterministic sample across groups, dtypes and policy kinds, rebuilt the
# way the scan built them; the manifest must carry the case's own policy
sample_ids = [mcases[k * len(mcases) // 24]["id"] for k in range(24)]
for predicate in (
        lambda c: c["dtype"] in ("int8", "int16", "int32", "int64"),
        lambda c: c["dtype"] in ("bool", "torch.bool"),
        lambda c: c["dtype"] == "bfloat16",
        lambda c: any(p.get("comparator") == "quantized_interval"
                      for p in c["comparison"].values()),
        lambda c: any(p.get("exact") for p in c["comparison"].values()),
        lambda c: any(p.get("comparator") == "array_equal"
                      for p in c["comparison"].values())):
    for case in mcases:
        if predicate(case):
            sample_ids.append(case["id"])
            break
sample_ids = list(dict.fromkeys(sample_ids))

policy_ok = True
policy_notes = []
sampled = {}
enumerated_rows = {row["id"]: row
                   for row in rs.enumerated_rows(CORPUS_MANIFEST)}
for case_id in sample_ids:
    row = enumerated_rows.get(case_id)
    if row is None:
        policy_ok = False
        policy_notes.append(f"{case_id}: not enumerable")
        continue
    case = rs.build_case(row, seed=manifest["seed"])
    own = rs._jsonable(case.get("comparison") or {})
    if own != mrows[case_id]["comparison"]:
        policy_ok = False
        policy_notes.append(f"{case_id}: manifest policy != case policy")
    else:
        sampled[case_id] = case
check("comparison-policy-is-the-cases-own", policy_ok,
      f"{len(sample_ids)} sampled cases; " + "; ".join(policy_notes[:3]))

# a corpus meta identity that maps to several artifact keys is legitimate
# only when its cases carry different LAYOUT signatures: the argument
# layout (a100c/lower/binding.py, its own documented contract) keys on the
# view set (name, dtype, rank) and the scalar record kinds -- never on
# extents, grid values, buffer contents or scalar values. A split whose
# cases share one layout signature would be specialization instability (a
# defect), so the expectation is computed here independently from the case
# payloads, not read from the compiler's digest
def _scalar_kind(value):
    if isinstance(value, np.generic):
        return np.asarray(value).dtype.name
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "uint64" if value >= 2 ** 63 else "int64"
    if isinstance(value, float):
        return "float64"
    return type(value).__name__


def layout_signature(case_id):
    case = rs.build_case(enumerated_rows[case_id], seed=manifest["seed"])
    host = {**(case.get("allocations") or {}), **(case.get("args") or {})}
    overrides = case.get("pointer_dtypes") or {}
    views, scalars = [], []
    for name, value in sorted(host.items()):
        if isinstance(value, np.ndarray):
            record_dtype = overrides.get(name) or str(value.dtype)
            views.append((name, record_dtype, int(value.ndim)))
        else:
            scalars.append((name, _scalar_kind(value)))
    return (tuple(views), tuple(scalars))


splits_ok = True
split_notes = []
for identity, keys in sorted(identity_key_splits.items()):
    sigs_by_key = {}
    for row in rows:
        if not row.get("compiled") or row["identity"] != identity:
            continue
        sigs_by_key.setdefault(row["artifact_key"], set()).add(
            layout_signature(row["id"]))
    all_sigs = [sig for values in sigs_by_key.values() for sig in values]
    if len(all_sigs) != len(set(all_sigs)):
        splits_ok = False
        split_notes.append(f"identity {identity}: the same layout signature "
                           "appears under two artifact keys (unexplained split)")
    else:
        split_notes.append(f"identity {identity}: {len(keys)} keys over "
                           f"{len(set(all_sigs))} distinct layout signatures "
                           "(view sets differ)")
check("identity-key-splits-are-layout-differences", splits_ok,
      "; ".join(split_notes) or "no identity splits over artifact keys")

# the control: a corrupted output must fail under the case's own tolerance,
# and pass once the tolerance is widened in a scratch copy -- the harness
# reads the tolerance from the case, never a hardcoded constant
corrupt_fails = widen_passes = None
for case_id in sample_ids:
    case = sampled.get(case_id)
    if not isinstance(case, dict) or case.get("aliases"):
        continue
    buffers = {**case.get("allocations", {}), **case["args"]}
    # an allclose, non-exact output with plain float storage
    fp_name = None
    for name, policy in (case.get("comparison") or {}).items():
        if (policy.get("comparator", "allclose") == "allclose"
                and not policy.get("exact") and name in buffers
                and np.issubdtype(np.asarray(buffers[name]).dtype,
                                  np.floating)):
            fp_name = name
            break
    if fp_name is None:
        continue
    storage = np.asarray(buffers[fp_name])
    reference = np.asarray(case["expected"][fp_name])
    if reference.size == 0 or not np.isfinite(reference).all():
        continue
    if float(np.max(np.abs(reference))) >= 1e3:
        continue                       # keep the corruption finite in-storage
    # build the actual exactly as the executed program delivers it: every
    # output in its storage dtype and shape, carrying the reference values
    baseline = {}
    clean = True
    for name, value in case["expected"].items():
        arr = np.asarray(value)
        buf = np.asarray(buffers[name])
        if arr.shape != buf.shape:
            if arr.size != buf.size:
                clean = False
                break
            arr = arr.reshape(buf.shape)
        baseline[name] = arr.astype(buf.dtype)
    if not clean or not all(np.isfinite(v).all() for v in baseline.values()):
        continue
    try:
        rs.compare_outputs(case, baseline)
    except Exception:                                   # noqa: BLE001
        continue                       # not a clean baseline; next sample
    policy = dict(case["comparison"][fp_name])
    delta = 1.0 + 10.0 * (float(policy.get("atol", 0))
                          + float(policy.get("rtol", 0))
                          * float(np.max(np.abs(reference))))
    actual = {name: value.copy() for name, value in baseline.items()}
    flat = actual[fp_name].reshape(-1)
    flat[0] = float(flat[0]) + delta
    try:
        rs.compare_outputs(case, actual)
        corrupt_fails = False
    except Exception:                                   # noqa: BLE001
        corrupt_fails = True
    scratch = dict(case)
    scratch["comparison"] = {
        name: (dict(value, rtol=1e9, atol=1e9) if name == fp_name
               else dict(value))
        for name, value in case["comparison"].items()}
    try:
        rs.compare_outputs(scratch, actual)
        widen_passes = corrupt_fails is True
    except Exception:                                   # noqa: BLE001
        widen_passes = False
    break
check("control-corrupted-output-fails", corrupt_fails is True,
      "the case's own tolerance rejects a corrupted output")
check("control-widened-scratch-tolerance-passes", widen_passes is True,
      "the tolerance is read from the case (IR-NUMERIC-POLICY)")

# ---------------------------------------------------------------------------
# 5. worker-count coverage (acceptance[1])
# ---------------------------------------------------------------------------

worker_reports = {}
for threads in WORKER_COUNTS:
    worker_reports[f"threads-{threads}"] = (
        SCAN / "workers" / f"threads-{threads}" / "report.json", threads,
        "stratified")
for suffix in ("1a", "1b", "2a", "2b", "4a", "4b", "8a", "8b"):
    worker_reports[f"reps-threads-{suffix}"] = (
        SCAN / "workers" / f"reps-threads-{suffix}" / "report.json",
        int(suffix[:-1]), "representatives")

worker_rows = {}          # (case id, threads) -> [(run name, row), ...]
worker_runs_ok = True
notes = []
for name, (path, threads, kind) in worker_reports.items():
    if not path.is_file():
        worker_runs_ok = False
        notes.append(f"{name}: missing report")
        continue
    run_report = load_json(path)
    if run_report.get("schema") != rs.SCHEMA or run_report.get("run_id") != run_id:
        worker_runs_ok = False
        notes.append(f"{name}: schema/run_id")
        continue
    for row in run_report["cases"]:
        if row.get("threads") != threads:
            worker_runs_ok = False
            notes.append(f"{name}: row threads {row.get('threads')} != {threads}")
        worker_rows.setdefault((row["id"], threads), []).append((name, row))
check("worker-run-reports-valid", worker_runs_ok,
      "; ".join(notes[:3]) or f"{len(worker_reports)} runs, "
      f"{len(worker_rows)} (case,count) cells")

# count 1: the primary report is the one-worker baseline (every case, the
# primary representative rows excepted: they execute at their captured
# resource configuration and at count 1 through the dedicated rep runs)
rows_at_count = {1: {row["id"]: row for row in rows}}
for (case_id, threads), entries in worker_rows.items():
    rows_at_count.setdefault(threads, {})[case_id] = entries[-1][1]

# (a) every feature class at every count
family_gaps = []
for threads in COUNTS:
    present = {OPERATOR_FAMILY[row["operator"]]
               for row in rows_at_count[threads].values()
               if row["operator"] in OPERATOR_FAMILY}
    missing = [f for f in FAMILIES if f not in present]
    if missing:
        family_gaps.append(f"threads={threads}: {missing}")
check("every-feature-class-at-every-count", not family_gaps,
      "; ".join(family_gaps) or f"{len(FAMILIES)} families x {list(COUNTS)}")

# (b) the stratified subsets are the declared deterministic strata (the
# subset executed at each count is a superset of the recomputed stratum)
stratum_ok = True
stratum_notes = []
for threads in WORKER_COUNTS:
    expected_ops = set(stratified_stratum(threads)) | set(REP_OPERATORS)
    executed_ops = {row["operator"] for row in rows_at_count[threads].values()}
    missing = expected_ops - executed_ops
    if missing:
        stratum_ok = False
        stratum_notes.append(f"threads={threads}: missing {sorted(missing)[:3]}")
check("stratified-subsets-executed", stratum_ok,
      "; ".join(stratum_notes) or "2 picks/family/count + anchors + reps")

# (c) representative rows at all four counts, with repetition, identified by
# the coverage record and consistent across repetitions
coverage = load_json(SCAN / "workers" / "coverage.json")
rep_counts_ok = True
rep_notes = []
for case_id in reps_expected.values():
    counts_recorded = (coverage.get("representatives", {})
                       .get("counts", {}).get(case_id, {}))
    for threads in COUNTS:
        executed = [row for _, row in worker_rows.get((case_id, threads), [])
                    if row.get("executed") and row.get("compared")]
        if threads == 4:
            primary_row = by_id[case_id]
            if (primary_row.get("threads") == 4 and primary_row["executed"]
                    and primary_row["compared"]):
                executed.append(primary_row)   # the primary run's capture
        if len(executed) < 2:
            rep_counts_ok = False
            rep_notes.append(f"{case_id}@{threads}: {len(executed)} executions")
        if int(counts_recorded.get(str(threads), 0)) < 2:
            rep_counts_ok = False
            rep_notes.append(f"{case_id}@{threads}: coverage record < 2")
        verdicts = {row["status"] for row in executed}
        if len(executed) >= 2 and len(verdicts) > 1:
            rep_counts_ok = False
            rep_notes.append(f"{case_id}@{threads}: inconsistent {verdicts}")
check("representatives-at-all-four-counts", rep_counts_ok,
      "; ".join(rep_notes[:3]) or ">=2 compared executions per count, "
      "consistent verdicts")
check("coverage-record-identifies-representatives",
      coverage.get("representatives", {}).get("dev") == reps_expected["dev"]
      and coverage.get("representatives", {}).get("perf") == reps_expected["perf"]
      and coverage.get("run_id") == run_id,
      "the consolidated record identifies both rows and binds the run")

# (d) F018 aspects at every count
aspect_gaps = []
for threads in COUNTS:
    compared = [row for row in rows_at_count[threads].values()
                if row.get("compared")]
    aspects = set()
    if compared:
        aspects.add("coverage")
    if any(nonpow2_extent(row["shape"]) for row in compared):
        aspects.add("tails")
    if threads == 1:
        if compared:
            aspects.add("ownership")   # single owner, full coverage compared
    else:
        for (_, count), entries in worker_rows.items():
            if count != threads:
                continue
            for _, row in entries:
                workers = (row.get("resource_observations") or {}).get("workers") or []
                active = [w for w in workers if w.get("completed_units", 0) > 0]
                if len(active) >= 2 and len({w.get("unit") for w in active}) >= 2:
                    aspects.add("ownership")
    if any(OPERATOR_TAGS.get(row["operator"], frozenset()) & VIS_TAGS
           for row in compared):
        aspects.add("visibility")
    repeated = {case_id for (case_id, count), entries in worker_rows.items()
                if count == threads and len(entries) >= 2}
    if repeated:
        aspects.add("repeated-execution")
    for aspect in ("coverage", "tails", "ownership", "visibility",
                   "repeated-execution"):
        if aspect not in aspects:
            aspect_gaps.append(f"threads={threads}: {aspect}")
check("f018-aspects-at-every-count", not aspect_gaps,
      "; ".join(aspect_gaps) or "coverage, tails, ownership, visibility, "
      "repeated execution at 1/2/4/8")

# (e) the consolidated coverage record agrees with the raw reports, per
# (case, count, repetition)
coverage_rows = {(row.get("id"), row.get("threads"), row.get("repetition")): row
                 for row in coverage.get("rows", [])}
raw_cells = {}
for (case_id, threads), entries in worker_rows.items():
    for index, (name, row) in enumerate(sorted(entries)):
        raw_cells[(case_id, threads, index)] = row
agree = (len(coverage_rows) == len(raw_cells)
         and set(coverage_rows) == set(raw_cells))
for cell, row in raw_cells.items():
    recorded = coverage_rows.get(cell)
    if (recorded is None or recorded.get("status") != row["status"]
            or recorded.get("passed") is not row["passed"]
            or recorded.get("executed") is not row["executed"]
            or recorded.get("operator") != row["operator"]
            or recorded.get("family") != OPERATOR_FAMILY.get(row["operator"])):
        agree = False
        break
check("coverage-record-matches-raw-reports", agree,
      f"{len(raw_cells)} raw (case,count,repetition) rows consolidated")

# (f) the representative captures (primary + per-count runs) are bound to
# this run, case and artifact on disk (A100-VALIDATION binding shape)
capture_dirs = {
    ("primary", 4): SCAN / "run" / "resource-evidence",
    ("reps-2a", 2): SCAN / "workers" / "reps-threads-2a" / "resource-evidence",
    ("reps-2b", 2): SCAN / "workers" / "reps-threads-2b" / "resource-evidence",
    ("reps-4a", 4): SCAN / "workers" / "reps-threads-4a" / "resource-evidence",
    ("reps-4b", 4): SCAN / "workers" / "reps-threads-4b" / "resource-evidence",
    ("reps-8a", 8): SCAN / "workers" / "reps-threads-8a" / "resource-evidence",
    ("reps-8b", 8): SCAN / "workers" / "reps-threads-8b" / "resource-evidence",
}
binding_ok = True
binding_notes = []
bound_counts = {2: 0, 4: 0, 8: 0}
for (name, threads), root in capture_dirs.items():
    for case_id in reps_expected.values():
        directory = root / rs.evidence_dir_name(case_id)
        log_path = directory / "execution_log.json"
        if not log_path.is_file():
            binding_ok = False
            binding_notes.append(f"{name}: no capture for {case_id[-40:]}")
            continue
        log = load_json(log_path)
        binding = load_json(directory / "binding.json")
        artifact_ref = (binding.get("artifact") or {}).get("path", "")
        if (log.get("run_id") != run_id or log.get("case_id") != case_id
                or not is_sha256(log.get("artifact_sha256"))
                or log.get("variant") != f"threads-{threads}"
                or not (directory / "listing.S").is_file()
                or not project_relative(artifact_ref)
                or not is_sha256((binding.get("artifact") or {}).get("sha256"))):
            binding_ok = False
            binding_notes.append(f"{name}: stale/unbound capture")
        else:
            bound_counts[threads] += 1
check("representative-captures-bound-to-run-case-artifact", binding_ok,
      "; ".join(binding_notes[:3]) or f"captures per count: {bound_counts}")
check("captures-exist-at-each-multiworker-count",
      all(bound_counts[t] >= 2 for t in (2, 4, 8)),
      f"captures per count: {bound_counts}")

# ---------------------------------------------------------------------------
# 6. the classified failure census (acceptance[2])
# ---------------------------------------------------------------------------

census = load_json(SCAN / "census.json")
failing = [row for row in rows if not row["passed"]]
census_rows = census.get("rows", [])
census_by_id = {}
duplicate_census = False
for row in census_rows:
    if row["id"] in census_by_id:
        duplicate_census = True
    census_by_id[row["id"]] = row


def census_reconciles(census_dict) -> bool:
    classes = census_dict.get("classes") or {}
    stages = census_dict.get("stages") or {}
    unclassified = census_dict.get("unclassified") or {}
    n_rows = len(census_dict.get("rows") or [])
    try:
        bounded = (int(unclassified.get("count", -1))
                   <= int(unclassified.get("bound", 0))
                   and (int(unclassified.get("count", 0)) == 0
                        or bool(unclassified.get("reason"))))
    except (TypeError, ValueError):
        return False
    return (sum(classes.values()) == n_rows
            and sum(stages.values()) == n_rows
            and all(isinstance(v, int) and v >= 0
                    for v in list(classes.values()) + list(stages.values()))
            and bounded)


check("census-schema", census.get("schema") == "a100-scan-census/v1")
check("census-covers-every-failure",
      not duplicate_census and set(census_by_id) == {r["id"] for r in failing},
      f"{len(failing)} failing rows, {len(census_rows)} census rows")
check("census-feature-class-is-the-corpus-family",
      all(OPERATOR_FAMILY.get(r["operator"]) == r.get("feature_class")
          for r in census_rows))
check("census-stage-in-declared-vocabulary",
      all(r.get("first_incorrect_stage") in STAGE_BY_STATUS.get(r["status"], set())
          for r in census_rows),
      "stage labels derive from the row's status (acceptance[2])")
unclassified = census.get("unclassified") or {}
check("census-reconciles",
      census_reconciles(census)
      and (census.get("reconciliation") or {}).get("ok") is True
      and sum((census.get("classes") or {}).values()) == len(failing)
      and sum((census.get("stages") or {}).values()) == len(failing),
      f"classes sum {sum((census.get('classes') or {}).values())}, stages sum "
      f"{sum((census.get('stages') or {}).values())}, failures {len(failing)}, "
      f"unclassified {unclassified.get('count')} "
      f"(bound {unclassified.get('bound')}, reason recorded: "
      f"{bool(unclassified.get('reason'))})")
check("census-statuses-match-report",
      (census.get("totals") or {}).get("failures") == len(failing)
      and (census.get("totals") or {}).get("cases") == 2734
      and (census.get("totals") or {}).get("statuses") == statuses,
      str((census.get("totals") or {}).get("statuses")))
# worker-count findings: every non-PASS worker-run row (including the
# representatives' contract failures) is recorded
worker_failures = set()
for (case_id, threads), entries in worker_rows.items():
    for _, row in entries:
        if not row["passed"]:
            worker_failures.add((case_id, threads))
recorded_findings = {(f["id"], f["threads"])
                     for f in census.get("worker_count_findings", [])}
check("census-worker-count-findings-complete",
      worker_failures <= recorded_findings,
      f"{len(worker_failures)} worker-run failing cells, "
      f"{len(recorded_findings)} recorded")
resource_section = {row.get("id"): row for row in census.get("resource_rows", [])}
check("census-identifies-representative-rows",
      set(resource_section) == set(reps_expected.values())
      and all(set(row.get("counts", {})) == {"1", "2", "4", "8"}
              for row in resource_section.values()),
      "per-count status for both representative rows")

# control: reconciliation must fail when the census and its totals disagree
# (the check can fail -- MECH-WITNESS-TEST)
mutated = copy.deepcopy(census)
mutated.setdefault("rows", []).append({
    "id": "control/synthetic.py#[1]#float32",
    "operator": "control/synthetic.py", "feature_class": "elementwise_reduce",
    "status": "MISMATCH", "first_incorrect_stage": "execution-mismatch"})
check("control-census-reconciliation-can-fail",
      census_reconciles(mutated) is False,
      "an unaccounted census row breaks the reconciliation")

# ---------------------------------------------------------------------------
print()
if FAILURES:
    print(f"FAILED ({len(FAILURES)}): " + ", ".join(FAILURES))
    sys.exit(1)
print(f"all scan-report checks PASS "
      f"({len(rows)} cases, statuses={statuses}, "
      f"worker cells={len(worker_rows)})")
sys.exit(0)
