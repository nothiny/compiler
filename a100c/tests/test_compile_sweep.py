#!/usr/bin/env python3
"""test_compile_sweep.py -- the full compile sweep, gate G6 (T018).

One cold sweep over the whole corpus through the enabled pipeline (the
factory compiler with every basic pass on, the normal ``passes=default``
configuration): every one of the 500 operators / 2734 cases / 2161-declared
compile identities is compiled exactly once per identity, and the census is
recorded as the driver output this task validates.

What the sweep does (single pass, the scan driver's own enumeration order --
``tools/run_scan.py`` is this task's declared input, so the sweep enumerates
cases exactly as ``run`` does: ``run_cases.py`` manifest paths ->
``manifest_specs`` -> ``golden.load_or_build_spec``, i.e. ``load_operator`` +
``make_case`` exactly as the harness runs them):

  * for every case: build the payload with the corpus's own harness and
    compute the corpus's declared compile identity (``compiler_api.identity``,
    tier ``meta``: source + kernel + pointer dtypes + scalar specialization
    classes + every constexpr in ``meta``/``launch_meta`` -- never shapes,
    grids or values);
  * the first case of each identity is compiled through
    ``a100c.factory.FactoryCompiler`` (``compile_case`` on the payload the
    native device hands over: the case minus ``expected``/``oracle_args``)
    under a per-identity wall budget (SIGALRM, default 600s -- a safety
    valve above the corpus's current compile-cost envelope, whose heaviest
    identities legitimately compile in ~4 minutes): an artifact, a located
    refusal (``PipelineError``) or an over-budget record -- never a silent
    retry and never a wait;
  * every later case of an identity that produced an artifact is compiled
    again as the no-baking control: it must be a cache hit on the very same
    executable (two cases of one identity share one artifact; no shape, grid
    or scalar value is baked into the key).

The census (artifacts, refusals, identities, compile times, refusal
classification) is written to ``docs/compiler-agent/COMPILE_CENSUS.json``
(``--census-out`` overrides) -- refusals are recorded findings for the
repair loop (classified by construct and operator), never a pass and never a
silently narrowed corpus.

The compile economics are measured cold: the sweep runs against an isolated
temporary artifact cache (``--cache-root`` overrides), so ``compile_count``
counts exactly the compilations this sweep performed.

Checks (each must hold for exit 0):

  census-covers-every-case          every enumerated case built and classified
  census-covers-all-operators       the census spans every manifest operator
  partition-sums-to-identity-census artifacts + refusals == identities, with
                                    zero over-budget, zero crashes (every
                                    identity has an ELF artifact or a located
                                    refusal)
  artifacts-are-riscv64-elf         every built artifact is ELF64-little-RISC-V
  compile-count-within-economics    compile_count <= 1.25 x the corpus's
                                    declared identity census (2161 for the
                                    2734 cases)
  repeat-cases-reuse-one-artifact   every recompiled repeat case is a cache
                                    hit on the same executable (no baking)
  refusals-located-and-countable    every refusal names its construct and a
                                    ``file:line:col`` source location, and the
                                    by-construct classification sums to the
                                    refusal count
  compile-budget-respected          the per-identity bound is enforced (every
                                    completed compile inside it, over-budget
                                    identities recorded, one attempt per
                                    identity -- never a silent retry)
  enabled-pipeline-passes-on        every artifact was produced with the six
                                    basic passes enabled (``passes=default``)
                                    and at least one rewrite fired somewhere

Run: python3 a100c/tests/test_compile_sweep.py [--limit N] [--operator PATH]...
     (exit 0 = every check PASS; the full corpus is the default)
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import signal
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
import warnings  # noqa: E402

warnings.filterwarnings("ignore")

# The scan driver (this task's declared input): importing it keeps one
# enumeration path -- the sweep sees exactly the cases ``tools/run_scan.py
# run`` sees, built exactly as the harness builds them.
_RUN_SCAN_PATH = ROOT / "tools" / "run_scan.py"
_spec = importlib.util.spec_from_file_location("run_scan_for_sweep",
                                               _RUN_SCAN_PATH)
rs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rs)                                    # noqa: E402

from compiler_api import identity as identity_lib              # noqa: E402
from a100c.driver import CompileOptions, PipelineError, compiler_revision  # noqa: E402
from a100c.factory import FactoryCompiler                      # noqa: E402
from a100c.passes import pipeline as passes_mod                # noqa: E402

FAILURES = []

#: the corpus's own declared economics (OPERATOR_INVENTORY section 1 /
#: SUITE_V3.md section 0; the sweep recomputes its census and reports both)
DECLARED_CENSUS = rs.DECLARED_CENSUS            # {"cases": 2734, "identities": 2161}
CENSUS_SCHEMA = "a100-compile-census/v1"
DEFAULT_CENSUS_OUT = ROOT / "docs" / "compiler-agent" / "COMPILE_CENSUS.json"
#: ``path:line:col`` -- what a located diagnostic must carry (MECH-
#: DIAGNOSTIC-REFUSAL), in PipelineError.loc or inside the rendered message
LOCATION_RE = re.compile(r"[\w./+-]+\.py:\d+:\d+")

STATUS_ARTIFACT = "artifact"
STATUS_REFUSED = "refused"
STATUS_OVER_BUDGET = "over-budget"
STATUS_CRASH = "crash"


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}", flush=True)
    if not ok:
        FAILURES.append(name)
    return ok


# ---------------------------------------------------------------------------
# the per-identity compile bound (never a wait, never a silent retry)
# ---------------------------------------------------------------------------

class CompileDeadline(Exception):
    """One identity's compile exceeded its wall budget (SIGALRM)."""


def _raise_deadline(signum, frame):
    raise CompileDeadline("compile budget exceeded")


class deadline:
    """SIGALRM bound around one compile_case call."""

    def __init__(self, seconds):
        self.seconds = float(seconds) if seconds else None

    def __enter__(self):
        if not self.seconds:
            return self
        self._previous = signal.signal(signal.SIGALRM, _raise_deadline)
        signal.setitimer(signal.ITIMER_REAL, self.seconds)
        return self

    def __exit__(self, *exc):
        if self.seconds:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, self._previous)
        return False


def is_riscv64_elf(path: Path) -> bool:
    """ELF64-little with e_machine == EM_RISCV (243)."""
    try:
        head = path.read_bytes()[:20]
    except OSError:
        return False
    return head[:6] == b"\x7fELF\x02\x01" and head[18:20] == b"\xf3\x00"


# ---------------------------------------------------------------------------
# the sweep
# ---------------------------------------------------------------------------

class CompileSweep:
    def __init__(self, args):
        self.args = args
        self.cache_root = Path(args.cache_root) if args.cache_root \
            else Path(tempfile.mkdtemp(prefix="a100-compile-sweep-"))
        self.owns_cache = not args.cache_root
        # the enabled pipeline: the normal configuration with every basic
        # pass on (an env switch that disables one would silently change what
        # this sweep measures, so the config is pinned and recorded)
        self.pass_config = passes_mod.PassConfig()
        self.compiler = FactoryCompiler(
            options=CompileOptions(cache_dir=str(self.cache_root), dumps=True),
            pass_config=self.pass_config)
        # The default bound sits above the corpus's current legitimate
        # compile-cost envelope: after the T030/T031 cost repairs the
        # heaviest identities (complex_svd, the restructured dot-in-loop
        # families) compile in ~175-243s, so a 600s bound lets every
        # identity reach an artifact-or-located-refusal classification
        # while still bounding the sweep.  An identity that exceeds it is
        # recorded as over-budget and never retried, and every identity's
        # cold compile time is recorded in the census, so compile-cost
        # findings stay visible instead of being hidden by the bound.
        self.budget = float(args.budget
                            or os.environ.get("A100_SWEEP_COMPILE_BUDGET",
                                              "600"))
        #: a generous bound on one case *build* (reference computation with
        #: the corpus's own harness; the compile budget is separate)
        self.build_budget = max(600.0, self.budget * 5.0)
        self.identities = {}        # corpus identity -> row
        self.case_rows = []         # every case, classified
        self.repeat_checks = []     # artifact-reuse controls
        self.compile_attempts = 0   # one per identity, by construction
        self.t_build = 0.0
        self.t_compile = 0.0
        self.refusal_prints = 0

    # -- one case ------------------------------------------------------------
    def sweep_case(self, row) -> None:
        began = time.perf_counter()
        try:
            with deadline(self.build_budget):
                case = rs.build_case(row, self.args.seed,
                                     use_golden=not self.args.no_golden)
        except Exception as exc:                                # noqa: BLE001
            self.t_build += time.perf_counter() - began
            self.case_rows.append({"id": row["id"], "operator": row["operator"],
                                   "status": "case-build-failed",
                                   "detail": f"{type(exc).__name__}: {exc}"[:300]})
            return
        self.t_build += time.perf_counter() - began
        identity = identity_lib.case_identity(row["operator"], case,
                                              tier="meta")
        payload = {k: v for k, v in case.items()
                   if k not in ("expected", "oracle_args")}
        entry = self.identities.get(identity)
        if entry is None:
            entry = self._new_identity(identity, row)
            self._compile_identity_first(entry, payload, row)
            self.case_rows.append({"id": row["id"],
                                   "operator": row["operator"],
                                   "identity": identity,
                                   "status": entry["status"]})
            return
        entry["cases"] += 1
        self.case_rows.append({"id": row["id"], "operator": row["operator"],
                               "identity": identity,
                               "status": entry["status"]})
        if entry["status"] == STATUS_ARTIFACT:
            # the no-baking control: this case (same identity, different
            # shape/grid/values) must reuse the very same artifact through
            # the cache -- a second cold compile here would mean something
            # case-specific entered the artifact key
            began = time.perf_counter()
            try:
                with deadline(self.budget):
                    artifact = self.compiler.compile_case(payload)
                reuse_ok = bool(artifact.cache_hit) and \
                    str(artifact.executable) == entry["artifact"]
                self.repeat_checks.append(
                    {"identity": identity, "case": row["id"],
                     "cache_hit": bool(artifact.cache_hit),
                     "same_artifact": str(artifact.executable)
                     == entry["artifact"],
                     "ok": reuse_ok})
            except Exception as exc:                            # noqa: BLE001
                self.repeat_checks.append(
                    {"identity": identity, "case": row["id"],
                     "cache_hit": False, "same_artifact": False, "ok": False,
                     "error": f"{type(exc).__name__}: {exc}"[:200]})
            self.t_compile += time.perf_counter() - began
        # refused / over-budget / crash identities are never retried: the
        # refusal is a property of the identity, recorded once (its cases are
        # all bound to it through the identity grouping above)

    def _new_identity(self, identity, row):
        entry = {"identity": identity, "operator": row["operator"],
                 "group": row["group"], "first_case": {"shape": row["shape"],
                                                       "dtype": row["dtype"]},
                 "cases": 1, "status": None, "attempts": 0}
        self.identities[identity] = entry
        return entry

    def _compile_identity_first(self, entry, payload, row) -> None:
        entry["attempts"] += 1
        self.compile_attempts += 1
        began = time.perf_counter()
        try:
            with deadline(self.budget):
                artifact = self.compiler.compile_case(payload)
        except CompileDeadline as exc:
            self.t_compile += time.perf_counter() - began
            entry["status"] = STATUS_OVER_BUDGET
            entry["detail"] = (f"compile exceeded its {self.budget:g}s "
                               f"budget; recorded, not retried")
            self._print_refusal(entry)
            return
        except PipelineError as exc:
            # a located compile refusal: a recorded finding for repair,
            # never a pass and never a silently narrowed corpus
            self.t_compile += time.perf_counter() - began
            entry["status"] = STATUS_REFUSED
            entry["construct"] = exc.construct
            entry["location"] = str(exc.loc) if exc.loc else None
            entry["detail"] = f"{exc.construct}: {exc.message}"[:400]
            self._print_refusal(entry)
            return
        except Exception as exc:                                # noqa: BLE001
            # a non-PipelineError failure is neither an artifact nor a
            # located refusal -- a census defect, recorded as a crash
            self.t_compile += time.perf_counter() - began
            entry["status"] = STATUS_CRASH
            entry["detail"] = f"{type(exc).__name__}: {exc}"[:400]
            self._print_refusal(entry)
            return
        self.t_compile += time.perf_counter() - began
        entry["status"] = STATUS_ARTIFACT
        entry["artifact"] = str(artifact.executable)
        entry["artifact_key"] = Path(artifact.executable).parent.name
        entry["sha256"] = artifact.sha256
        entry["cache_hit_first"] = bool(artifact.cache_hit)
        entry["compile_ms"] = round((time.perf_counter() - began) * 1000, 1)

    def _print_refusal(self, entry) -> None:
        if self.refusal_prints < 20:
            print(f"    {entry['status']:12s} {entry['operator']} "
                  f"[{entry['first_case']['shape']} "
                  f"{entry['first_case']['dtype']}] :: "
                  f"{entry.get('detail', '')[:110]}", flush=True)
        self.refusal_prints += 1

    # -- the whole sweep -------------------------------------------------------
    def run(self):
        args = self.args
        rows = list(rs.enumerated_rows(args.manifest_path, args.group,
                                        args.operator))
        if args.limit is not None:
            rows = rows[:args.limit]
        began = time.perf_counter()
        for index, row in enumerate(rows):
            self.sweep_case(row)
            if (index + 1) % 25 == 0 or index + 1 == len(rows):
                print(f"[{index + 1}/{len(rows)}] identities "
                      f"{len(self.identities)} build {self.t_build:.0f}s "
                      f"compile {self.t_compile:.0f}s "
                      f"({time.perf_counter() - began:.0f}s elapsed)",
                      flush=True)
        self.wall_s = time.perf_counter() - began
        return self.census_document(rows)

    # -- the census ------------------------------------------------------------
    def census_document(self, rows) -> dict:
        identities = list(self.identities.values())
        by_status = {}
        for entry in identities:
            by_status[entry["status"]] = by_status.get(entry["status"], 0) + 1
        refusals = [e for e in identities if e["status"] == STATUS_REFUSED]
        by_construct = {}
        for entry in refusals:
            by_construct[entry["construct"]] = \
                by_construct.get(entry["construct"], 0) + 1
        by_operator_refused = {}
        for entry in refusals:
            by_operator_refused[entry["operator"]] = \
                by_operator_refused.get(entry["operator"], 0) + 1
        operators_seen = {e["operator"] for e in identities}
        cold_ms = sorted(e["compile_ms"] for e in identities
                         if e["status"] == STATUS_ARTIFACT
                         and not e["cache_hit_first"])
        # pass evidence from the artifacts' own markers: the configuration
        # every artifact was built with, and the rewrites that fired (one
        # marker per distinct artifact key -- merged identities share one)
        pass_totals = {name: 0 for name in passes_mod.PASS_ORDER}
        markers_all_default = 0
        markers_read = 0
        marker_keys = set()
        for entry in identities:
            if entry["status"] != STATUS_ARTIFACT:
                continue
            if entry["artifact_key"] in marker_keys:
                continue
            marker_keys.add(entry["artifact_key"])
            marker_path = Path(self.cache_root) / entry["artifact_key"] \
                / "artifact.json"
            try:
                marker = json.loads(marker_path.read_text())
                stages = marker.get("stages") or {}
                passes = (stages.get("passes") or {})
                markers_read += 1
                if passes.get("identity") == self.pass_config.identity_part():
                    markers_all_default += 1
                for name, trace in (passes.get("passes") or {}).items():
                    fired = trace.get("fired")
                    if isinstance(fired, int):
                        pass_totals[name] = pass_totals.get(name, 0) + fired
            except (OSError, ValueError):
                continue
        build_failures = [r for r in self.case_rows
                          if r["status"] == "case-build-failed"]
        repeat_bad = [r for r in self.repeat_checks if not r["ok"]]
        crashes = [e for e in identities if e["status"] == STATUS_CRASH]
        crash_by_class = {}
        for entry in crashes:
            klass = entry["detail"].split(":", 1)[0]
            crash_by_class[klass] = crash_by_class.get(klass, 0) + 1
        census = {
            "schema": CENSUS_SCHEMA,
            "generator": "a100c/tests/test_compile_sweep.py",
            "command": " ".join(sys.argv),
            "seed": self.args.seed,
            "manifest": self.args.manifest_path,
            "compiler_revision": compiler_revision(),
            "pass_config": self.pass_config.identity_part(),
            "restricted": bool(self.args.operator or self.args.group
                               or self.args.limit is not None),
            "cache": {"root": str(self.cache_root),
                      "isolated_temporary": self.owns_cache},
            "budget_s_per_identity": self.budget,
            "census": {
                "operators": len(operators_seen),
                "cases": len(rows),
                "cases_classified": len(self.case_rows),
                "identities": len(identities),
                "cases_per_identity": (round(len(rows) / len(identities), 3)
                                       if identities else None),
                "declared_full_corpus": DECLARED_CENSUS,
                "identities_with_multiple_cases":
                    sum(1 for e in identities if e["cases"] > 1),
            },
            "partition": {
                "artifacts": by_status.get(STATUS_ARTIFACT, 0),
                "refused": by_status.get(STATUS_REFUSED, 0),
                "over_budget": by_status.get(STATUS_OVER_BUDGET, 0),
                "crash": by_status.get(STATUS_CRASH, 0),
                "case_build_failures": len(build_failures),
                "sums_to_identity_census":
                    by_status.get(STATUS_ARTIFACT, 0)
                    + by_status.get(STATUS_REFUSED, 0)
                    + by_status.get(STATUS_OVER_BUDGET, 0)
                    + by_status.get(STATUS_CRASH, 0) == len(identities),
            },
            "compile": {
                "count": self.compiler.compile_count,
                "cache_hits": self.compiler.cache_hits,
                "attempts_one_per_identity": self.compile_attempts,
                "cold_ms": cold_ms,
                "cold_ms_median": (cold_ms[len(cold_ms) // 2]
                                   if cold_ms else None),
                "cold_ms_max": cold_ms[-1] if cold_ms else None,
                "declared_identity_bound_1_25x":
                    int(1.25 * DECLARED_CENSUS["identities"]),
                "within_declared_economics":
                    self.compiler.compile_count
                    <= 1.25 * DECLARED_CENSUS["identities"],
            },
            "artifact_reuse": {
                "repeat_case_checks": len(self.repeat_checks),
                "all_reused_one_artifact": not repeat_bad,
                "violations": repeat_bad[:20],
            },
            "passes": {"totals_fired": pass_totals,
                       "markers_read": markers_read,
                       "markers_with_enabled_config": markers_all_default},
            "refusals": {
                "count": len(refusals),
                "by_construct": dict(sorted(by_construct.items(),
                                            key=lambda kv: -kv[1])),
                "by_operator": dict(sorted(by_operator_refused.items(),
                                           key=lambda kv: -kv[1])),
                "rows": [{"identity": e["identity"], "operator": e["operator"],
                          "cases": e["cases"],
                          "first_case": e["first_case"],
                          "construct": e["construct"],
                          "location": e["location"], "detail": e["detail"]}
                         for e in refusals],
            },
            "over_budget_rows": [
                {"identity": e["identity"], "operator": e["operator"],
                 "first_case": e["first_case"], "detail": e["detail"]}
                for e in identities if e["status"] == STATUS_OVER_BUDGET],
            "crash_rows": [
                {"identity": e["identity"], "operator": e["operator"],
                 "first_case": e["first_case"], "detail": e["detail"]}
                for e in crashes],
            "crashes": {"count": len(crashes),
                        "by_exception_class": dict(sorted(
                            crash_by_class.items(), key=lambda kv: -kv[1]))},
            "case_build_failures": build_failures[:50],
            "wall": {"total_s": round(self.wall_s, 1),
                     "build_s": round(self.t_build, 1),
                     "compile_s": round(self.t_compile, 1)},
            "identities": [
                {"identity": e["identity"], "operator": e["operator"],
                 "cases": e["cases"], "status": e["status"],
                 "artifact_key": e.get("artifact_key"),
                 "sha256": e.get("sha256"),
                 "compile_ms": e.get("compile_ms"),
                 "cache_hit_first": e.get("cache_hit_first"),
                 "construct": e.get("construct"),
                 "location": e.get("location")}
                for e in identities],
        }
        return census


# ---------------------------------------------------------------------------
# the acceptance checks
# ---------------------------------------------------------------------------

def validate(census: dict, expected_operators: set) -> None:
    part = census["partition"]
    cnt = census["census"]
    comp = census["compile"]
    reuse = census["artifact_reuse"]

    check("census-covers-every-case",
          cnt["cases_classified"] == cnt["cases"]
          and part["case_build_failures"] == 0,
          f"{cnt['cases_classified']}/{cnt['cases']} cases classified, "
          f"{part['case_build_failures']} build failures")

    operators_seen = {e["operator"] for e in census["identities"]}
    check("census-covers-all-operators",
          operators_seen == expected_operators,
          f"{len(operators_seen)}/{len(expected_operators)} operators; "
          + (f"missing: {sorted(expected_operators - operators_seen)[:3]}"
             if operators_seen != expected_operators else ""))

    check("partition-sums-to-identity-census",
          part["artifacts"] + part["refused"] == cnt["identities"]
          and part["sums_to_identity_census"]
          and part["over_budget"] == 0 and part["crash"] == 0,
          f"{part['artifacts']} artifacts + {part['refused']} refusals "
          f"= {cnt['identities']} identities "
          f"(over-budget {part['over_budget']}, crash {part['crash']})")

    bad_elf = []
    for entry in census["identities"]:
        if entry["status"] != STATUS_ARTIFACT:
            continue
        executable = Path(census["cache"]["root"]) / entry["artifact_key"] \
            / "operator_exec"
        if not is_riscv64_elf(executable):
            bad_elf.append(entry["identity"])
    check("artifacts-are-riscv64-elf",
          part["artifacts"] > 0 and not bad_elf,
          f"{part['artifacts']} artifacts checked"
          + (f"; non-ELF: {bad_elf[:3]}" if bad_elf else ""))

    check("compile-count-within-economics",
          comp["count"] <= comp["declared_identity_bound_1_25x"]
          and comp["count"] <= cnt["identities"],
          f"{comp['count']} compiles <= 1.25 x "
          f"{DECLARED_CENSUS['identities']} = "
          f"{comp['declared_identity_bound_1_25x']} "
          f"(run census {cnt['identities']} identities, "
          f"{comp['cache_hits']} cache hits)")

    check("repeat-cases-reuse-one-artifact",
          reuse["repeat_case_checks"] > 0 and reuse["all_reused_one_artifact"],
          f"{reuse['repeat_case_checks']} repeat cases recompiled, "
          f"{len(reuse['violations'])} violations"
          + (f"; first: {reuse['violations'][:1]}" if reuse["violations"]
             else ""))

    refusals = census["refusals"]
    unlocated = [r for r in refusals["rows"]
                 if not r["construct"]
                 or not LOCATION_RE.search(f"{r['location'] or ''} "
                                           f"{r['detail'] or ''}")]
    classified = sum(refusals["by_construct"].values())
    check("refusals-located-and-countable",
          classified == refusals["count"] and not unlocated
          and all(r["construct"] for r in refusals["rows"]),
          f"{refusals['count']} refusals, "
          f"{len(refusals['by_construct'])} constructs "
          f"(top: {list(refusals['by_construct'].items())[:3]})"
          + (f"; unlocated: {unlocated[:2]}" if unlocated else ""))

    over = census["over_budget_rows"]
    attempts = comp["attempts_one_per_identity"]
    max_ms = comp["cold_ms_max"] or 0.0
    # acceptance[3]: the sweep runs within a bounded wall time per identity --
    # the bound is enforced (every completed compile inside it), over-budget
    # identities are recorded (never silently retried: exactly one attempt
    # per identity).  An over-budget identity still breaks the census
    # partition, which is acceptance[0]'s check, not this one.
    check("compile-budget-respected",
          attempts == cnt["identities"]
          and len(over) == part["over_budget"]
          and max_ms < census["budget_s_per_identity"] * 1000,
          f"budget {census['budget_s_per_identity']:g}s/identity, "
          f"{attempts} attempts for {cnt['identities']} identities (one per "
          f"identity, no retries), slowest completed cold compile "
          f"{max_ms:.0f}ms, {len(over)} over-budget (recorded, not retried)")

    fired = census["passes"]["totals_fired"]
    markers = census["passes"]["markers_read"]
    enabled = census["passes"]["markers_with_enabled_config"]
    check("enabled-pipeline-passes-on",
          markers > 0 and markers == enabled
          and sum(fired.values()) > 0,
          f"config {census['pass_config']}: {enabled}/{markers} markers, "
          f"rewrites fired {fired}")


def _expected_operators(args) -> set:
    """The operator set a sweep restricted by ``args`` must cover."""
    if args.limit is not None:
        return None                     # a prefix: coverage is not meaningful
    operators = rs.cases_from_manifest(args.manifest_path)
    if args.operator:
        return {rs.resolve_operator_path(p) for p in args.operator}
    expected = {rs.resolve_operator_path(p) for p in operators}
    if args.group:
        return {op for op in expected if op.startswith(args.group + "/")}
    return expected

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="the full compile sweep (gate G6): compile every corpus "
                    "identity once through the enabled pipeline and record "
                    "the census")
    parser.add_argument("--manifest-path", default=rs.DEFAULT_MANIFEST)
    parser.add_argument("--seed", type=int, default=30)
    parser.add_argument("--no-golden", action="store_true")
    parser.add_argument("--group", choices=rs.GROUPS)
    parser.add_argument("--operator", action="append",
                        help="restrict to operator files (repeatable; the "
                             "full corpus is the default)")
    parser.add_argument("--limit", type=int,
                        help="sweep at most N cases (calibration only)")
    parser.add_argument("--budget", type=float,
                        help="per-identity compile bound in seconds "
                             "(default A100_SWEEP_COMPILE_BUDGET or 600; "
                             "the bound is a safety valve above the corpus's "
                             "current compile-cost envelope -- over-budget "
                             "identities are recorded, never retried)")
    parser.add_argument("--cache-root",
                        help="artifact cache root (default: an isolated "
                             "temporary directory, so compile counting is "
                             "cold and the shared cache is untouched)")
    parser.add_argument("--census-out", default=str(DEFAULT_CENSUS_OUT),
                        help="where the compile census is written")
    args = parser.parse_args(argv)

    sweep = CompileSweep(args)
    try:
        census = sweep.run()
        expected_operators = _expected_operators(args)
        if expected_operators is None:
            # a --limit prefix: coverage is against what the prefix reached
            expected_operators = {e["operator"] for e in census["identities"]}
        census["expected_operators"] = sorted(expected_operators)
        validate(census, expected_operators)

        census_out = Path(args.census_out)
        census_out.parent.mkdir(parents=True, exist_ok=True)
        census_out.write_text(json.dumps(census, indent=2,
                                         ensure_ascii=False) + "\n")
        print(f"census -> {census_out} "
              f"({census['census']['identities']} identities, "
              f"{census['partition']['artifacts']} artifacts, "
              f"{census['partition']['refused']} refusals)")
        summary = {k: dict(census[k]) for k in
                   ("census", "partition", "artifact_reuse", "wall",
                    "crashes")}
        compile_summary = dict(census["compile"])
        compile_summary.pop("cold_ms", None)     # full list lives in the file
        summary["compile"] = compile_summary
        print(json.dumps(summary, indent=2))
    finally:
        if sweep.owns_cache:
            import shutil
            shutil.rmtree(sweep.cache_root, ignore_errors=True)
    if FAILURES:
        print(f"\n{len(FAILURES)} check(s) failed: {FAILURES}",
              file=sys.stderr)
        return 1
    print("\nall compile-sweep checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
