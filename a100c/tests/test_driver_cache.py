#!/usr/bin/env python3
"""test_driver_cache.py -- the driver, artifact cache and factory (T017).

Covers the task's acceptance refs against the real compile/execute path:

  * the factory: ``a100c.factory.make_compiler()`` returns the
    ``compile_case(case) -> artifact`` protocol ``a100_support`` consumes
    (arguments ``('--bundle','{bundle}','--threads','{threads}')``, an
    ELF64-little-RISC-V executable, provenance, ``A100C_CACHE_DIR`` honored);
    the artifact identity excludes shape and grid (two cases of one identity
    share one artifact; a dtype change is a new identity) and the pass
    configuration is part of the key (MECH-PASS-ATTRIBUTION);

  * the scan driver (``tools/run_scan.py``), each scenario in a fresh
    process over a small corpus group that compiles, executes and compares
    end to end today:
      - cold run: compile count == distinct compile identities in the run
        set (== the corpus meta-tier census of that set, never the case
        count); every case compiled, executed and compared with its
        declared policy;
      - warm run over the same set: zero compilations, cache hits only,
        cache-hit staging is fast;
      - resume: a journaled partial run resumes without recompiling, and
        the report is complete;
      - fault isolation: an injected fault in the middle of the run (a
        corrupted bundle -- crash; a launch cut at a tiny bound -- timeout)
        is recorded as that case's failure and leaves every other case's
        result unchanged;

  * import inspection: compiling through the factory loads neither torch
    nor the reference device (F049/F052).

Run: python3 a100c/tests/test_driver_cache.py   (exit 0 = all checks PASS)
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
import warnings  # noqa: E402

warnings.filterwarnings("ignore")

FAILURES = []
EVIDENCE: dict = {"scenarios": []}


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}", flush=True)
    if not ok:
        FAILURES.append(name)
    return ok


def record(**fields):
    EVIDENCE["scenarios"].append(fields)


WORK = Path(tempfile.mkdtemp(prefix="a100c-driver-cache-"))

#: a small corpus group that compiles, executes and compares PASS today
#: (elementwise + atomics + bit-level reinterpretation + index arithmetic)
OPERATORS = ("suite/dev/absolute_kernel.py",
             "suite/dev/bincount_kernel.py",
             "suite/dev/bitcast.py",
             "suite/dev/calculate_batch_indices_kernel.py")

RUN_SCAN = str(ROOT / "tools" / "run_scan.py")


def scan(cache: Path, *extra, expect_exit=0):
    """One scan subprocess with an isolated artifact cache."""
    env = dict(os.environ)
    env["A100C_CACHE_DIR"] = str(cache)
    command = [sys.executable, RUN_SCAN, "run",
               *sum([["--operator", op] for op in OPERATORS], []),
               *extra]
    proc = subprocess.run(command, capture_output=True, text=True,
                          timeout=540, cwd=str(ROOT), env=env)
    if proc.returncode != expect_exit:
        print(proc.stdout[-2000:], file=sys.stderr)
        print(proc.stderr[-2000:], file=sys.stderr)
    return proc, command


def load(path):
    return json.loads(Path(path).read_text())


# ---------------------------------------------------------------------------
# the factory and the artifact cache
# ---------------------------------------------------------------------------

def check_factory() -> None:
    cache = WORK / "factory-cache"
    os.environ["A100C_CACHE_DIR"] = str(cache)
    from a100c.factory import FactoryCompiler, make_compiler
    from opslib.runner import load_operator

    module = load_operator(ROOT / "ops" / "suite" / "dev" / "absolute_kernel.py")
    case = module.make_case(shape=[97], dtype="float32")
    payload = {k: v for k, v in case.items()
               if k not in ("expected", "oracle_args")}
    compiler = make_compiler()
    check("factory-returns-compile-case-protocol",
          callable(getattr(compiler, "compile_case", None)),
          f"{type(compiler).__name__} from a100c.factory:make_compiler")
    artifact = compiler.compile_case(payload)
    check("factory-artifact-arguments-protocol",
          tuple(artifact.arguments) ==
          ("--bundle", "{bundle}", "--threads", "{threads}"),
          f"arguments={artifact.arguments}")
    elf = Path(artifact.executable).read_bytes()
    check("factory-artifact-is-riscv-elf",
          elf[:6] == b"\x7fELF\x02\x01" and elf[18:20] == b"\xf3\x00",
          f"{artifact.executable.name}, {len(elf)} bytes")
    check("factory-artifact-provenance",
          bool(artifact.provenance) and "a100c" in artifact.provenance,
          artifact.provenance)
    check("factory-cache-root-honored",
          cache in Path(artifact.executable).parents,
          str(Path(artifact.executable).parent))
    cold_count = compiler.compile_count

    # shape and grid are runtime: another case of the same identity (same
    # dtypes, different shape) must be a cache hit on the same artifact
    other = module.make_case(shape=[4097], dtype="float32")
    payload_other = {k: v for k, v in other.items()
                     if k not in ("expected", "oracle_args")}
    artifact_other = compiler.compile_case(payload_other)
    check("identity-excludes-shape",
          Path(artifact_other.executable) == Path(artifact.executable)
          and artifact_other.cache_hit and compiler.compile_count == cold_count,
          "one artifact for both shapes; the second call is a cache hit")

    # a dtype change is a different identity
    third = module.make_case(shape=[97], dtype="float16")
    payload_third = {k: v for k, v in third.items()
                     if k not in ("expected", "oracle_args")}
    artifact_third = compiler.compile_case(payload_third)
    check("identity-includes-pointer-dtype",
          Path(artifact_third.executable) != Path(artifact.executable)
          and compiler.compile_count == cold_count + 1,
          "float16 compiles a distinct artifact")

    # the pass configuration is part of the key: all-off is a different
    # entry whose bytes match the plain driver's (the general path intact)
    from a100c.driver import Compiler, CompileOptions
    from a100c.passes import pipeline as passes_mod
    plain = Compiler(options=CompileOptions(
        cache_dir=str(WORK / "plain-driver"), dumps=False))
    plain_artifact = plain.compile_case(payload)
    off = FactoryCompiler(
        pass_config=passes_mod.PassConfig().all_off(),
        options=CompileOptions(cache_dir=str(WORK / "all-off"), dumps=False))
    off_artifact = off.compile_case(payload)
    on = FactoryCompiler(
        pass_config=passes_mod.PassConfig(),
        options=CompileOptions(cache_dir=str(WORK / "passes-on"), dumps=False))
    on_artifact = on.compile_case(payload)
    plain_sha = hashlib.sha256(
        Path(plain_artifact.executable).read_bytes()).hexdigest()
    off_sha = hashlib.sha256(
        Path(off_artifact.executable).read_bytes()).hexdigest()
    on_sha = hashlib.sha256(
        Path(on_artifact.executable).read_bytes()).hexdigest()
    check("pass-config-in-cache-key-and-general-path-intact",
          Path(off_artifact.executable) != Path(on_artifact.executable)
          and off_sha == plain_sha,
          "all-off is a distinct cache entry, byte-identical to the plain "
          f"driver ({off_sha[:12]}); passes-on differs ({on_sha[:12]})")
    marker = json.loads((Path(on_artifact.executable).parent
                         / "artifact.json").read_text())
    fired = {name: trace.get("fired")
             for name, trace in marker["stages"]["passes"]["passes"].items()}
    check("pass-trace-recorded-in-marker",
          marker["stages"]["passes"]["identity"] == "passes=default"
          and all(v is not None for v in fired.values()),
          f"fired={fired}")
    record(scenario="factory", cold_count=compiler.compile_count,
           pass_trace=fired, all_off_equals_plain=off_sha == plain_sha)
    del os.environ["A100C_CACHE_DIR"]


# ---------------------------------------------------------------------------
# the scan scenarios
# ---------------------------------------------------------------------------

def check_cold_and_warm() -> dict:
    cache = WORK / "scan-cache"
    proc, command = scan(cache, "--report", str(WORK / "cold.json"))
    check("cold-run-exits-0", proc.returncode == 0,
          f"exit {proc.returncode}")
    cold = load(WORK / "cold.json")
    cold_summary = load(WORK / "cold.json.summary.json")
    cases = cold_summary["census"]["cases"]
    identities = cold_summary["census"]["identities"]
    compiles = cold_summary["compile"]["count"]
    artifacts = cold_summary["compile"]["artifact_identities"]
    check("cold-compile-count-equals-distinct-identities",
          compiles == identities == artifacts and compiles < cases,
          f"{compiles} compiles == {identities} identities == "
          f"{artifacts} artifacts (< {cases} cases)")
    check("cold-run-every-case-compiled-executed-compared",
          all(row["compiled"] and row["executed"] and row["compared"]
              and row["passed"] for row in cold["cases"]),
          f"statuses={cold_summary['statuses']}")
    check("cold-run-report-complete",
          cold_summary["checks"]["report_complete"]
          and cold["schema"] == "input-regression/v1",
          f"{len(cold['cases'])} rows, schema {cold['schema']}")
    record(scenario="cold", cases=cases, identities=identities,
           compiles=compiles, statuses=cold_summary["statuses"])

    proc, _ = scan(cache, "--report", str(WORK / "warm.json"))
    warm = load(WORK / "warm.json")
    warm_summary = load(WORK / "warm.json.summary.json")
    check("warm-run-zero-compilations",
          proc.returncode == 0
          and warm_summary["compile"]["count"] == 0
          and warm_summary["compile"]["cache_hits"] == cases,
          f"compiles={warm_summary['compile']['count']}, "
          f"cache_hits={warm_summary['compile']['cache_hits']} over "
          f"{cases} cases")
    check("warm-run-cache-hits-are-fast",
          warm_summary["checks"]["cache_hit_is_fast"],
          f"cache-hit p50 "
          f"{warm_summary['compile']['cache_hit_ms_median']} ms vs cold p50 "
          f"{cold_summary['compile']['cold_ms_median']} ms")
    check("warm-run-results-identical",
          [(r["id"], r["status"], r.get("artifact_sha256"))
           for r in warm["cases"]]
          == [(r["id"], r["status"], r.get("artifact_sha256"))
              for r in cold["cases"]],
          "every row reproduces its cold-run verdict and artifact")
    record(scenario="warm", compiles=warm_summary["compile"]["count"],
           cache_hits=warm_summary["compile"]["cache_hits"],
           cache_hit_ms_median=warm_summary["compile"]["cache_hit_ms_median"])
    return {"cold": cold, "cold_summary": cold_summary}


def check_resume() -> None:
    cache = WORK / "scan-cache"            # warm from the previous scenario
    journal = WORK / "resume.jl"
    proc, _ = scan(cache, "--journal", str(journal), "--limit", "4",
                   "--report", str(WORK / "resume-partial.json"))
    check("resume-partial-run-exits-0", proc.returncode == 0,
          f"exit {proc.returncode}")
    proc, _ = scan(cache, "--journal", str(journal), "--resume",
                   "--report", str(WORK / "resume-complete.json"))
    check("resume-run-exits-0", proc.returncode == 0,
          f"exit {proc.returncode}")
    summary = load(WORK / "resume-complete.json.summary.json")
    report = load(WORK / "resume-complete.json")
    check("resume-skips-journaled-cases-without-recompiling",
          summary["run"]["resumed"] == 4
          and summary["compile"]["count"] == 0
          and summary["run"]["missing"] == 0,
          f"resumed={summary['run']['resumed']}, "
          f"compiles={summary['compile']['count']}, "
          f"run_this_process={summary['run']['run_this_process']}")
    check("resume-report-is-complete",
          summary["checks"]["report_complete"]
          and all(row["compiled"] and row["executed"] and row["compared"]
                  and row["passed"] for row in report["cases"]),
          f"{len(report['cases'])} rows, every case compiled, executed "
          f"and compared")
    journal_rows = [json.loads(line) for line in
                    journal.read_text().splitlines() if line.strip()]
    resumed_rows = {row["id"]: row for row in journal_rows}
    check("resume-rows-come-from-the-journal",
          all(report_row == resumed_rows.get(report_row["id"])
              for report_row in report["cases"]
              if report_row["id"] in resumed_rows),
          f"{len(resumed_rows)} journaled rows reproduced verbatim")
    record(scenario="resume", resumed=summary["run"]["resumed"],
           compiles=summary["compile"]["count"])


def check_fault_isolation(baseline: dict) -> None:
    cache = WORK / "scan-cache"
    rows = baseline["cold"]["cases"]
    middle = rows[len(rows) // 2]["id"]
    target = max(rows, key=lambda r: r.get("launch_seconds") or 0.0)
    crash_id = middle
    timeout_id = target["id"]
    launch_seconds = target.get("launch_seconds") or 0.0
    bound = max(0.01, launch_seconds / 3.0)
    proc, _ = scan(cache, "--report", str(WORK / "faulted.json"),
                   "--fault-inject", f"{crash_id}:crash",
                   "--fault-inject", f"{timeout_id}:timeout",
                   "--fault-timeout", str(bound))
    check("faulted-run-exits-0", proc.returncode == 0,
          f"exit {proc.returncode} (the fault is a recorded row, never a "
          f"scan failure)")
    faulted = {row["id"]: row for row in load(WORK / "faulted.json")["cases"]}
    crash_row = faulted[crash_id]
    timeout_row = faulted[timeout_id]
    check("crash-fault-recorded-as-failure",
          crash_row["status"] == "LAUNCH_FAIL"
          and not crash_row["passed"] and not crash_row["executed"]
          and "native process exit" in crash_row["detail"],
          f"{crash_id} -> {crash_row['status']}: "
          f"{crash_row['detail'][:80]}")
    check("timeout-fault-recorded-with-its-bound",
          timeout_row["status"] == "TIMEOUT"
          and not timeout_row["passed"] and not timeout_row["executed"]
          and "exceeded its bound" in timeout_row["detail"],
          f"{timeout_id} -> {timeout_row['status']}: "
          f"{timeout_row['detail'][:80]}")
    unchanged = []
    for row in baseline["cold"]["cases"]:
        if row["id"] in (crash_id, timeout_id):
            continue
        other = faulted[row["id"]]
        if (row["status"], row.get("detail"), row.get("artifact_sha256"),
                row["passed"]) != (other["status"], other.get("detail"),
                                   other.get("artifact_sha256"),
                                   other["passed"]):
            unchanged.append(row["id"])
    check("fault-isolation-other-cases-unchanged",
          not unchanged,
          f"{len(rows) - 2} other cases reproduce their clean-run results"
          + (f"; changed: {unchanged[:3]}" if unchanged else ""))
    record(scenario="fault-isolation", crash=crash_id,
           crash_status=crash_row["status"], timeout=timeout_id,
           timeout_status=timeout_row["status"], bound_s=bound,
           other_cases_unchanged=not unchanged)


def check_import_inspection() -> None:
    probe = WORK / "import-probe.py"
    probe.write_text(f"""
import json, sys
sys.path.insert(0, {str(ROOT)!r})
sys.path.insert(0, {str(ROOT / 'ops' / 'harness')!r})
import a100c.factory as factory
compiler = factory.make_compiler()
from opslib.runner import load_operator
module = load_operator({str(ROOT / 'ops' / 'suite' / 'dev' / 'absolute_kernel.py')!r})
case = module.make_case(shape=[97], dtype='float32')
payload = {{k: v for k, v in case.items()
           if k not in ('expected', 'oracle_args')}}
artifact = compiler.compile_case(payload)
assert artifact.executable.is_file()
bad = [m for m in ('torch', 'a100_support.reference_device',
                   'a100_support.reference_backend') if m in sys.modules]
print(json.dumps(bad))
sys.exit(1 if bad else 0)
""")
    env = dict(os.environ)
    env["A100C_CACHE_DIR"] = str(WORK / "import-cache")
    proc = subprocess.run([sys.executable, str(probe)], capture_output=True,
                          text=True, timeout=300, env=env)
    check("compiler-and-factory-import-no-torch-no-reference-device",
          proc.returncode == 0,
          f"modules loaded during a real compile: "
          f"{proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else proc.stderr[-200:]}")


def main() -> int:
    try:
        check_factory()
        baseline = check_cold_and_warm()
        check_resume()
        check_fault_isolation(baseline)
        check_import_inspection()
    finally:
        shutil.rmtree(WORK, ignore_errors=True)
    if FAILURES:
        print(f"\n{len(FAILURES)} check(s) failed: {FAILURES}", file=sys.stderr)
        return 1
    print("\nall driver/cache/factory checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
