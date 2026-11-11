#!/usr/bin/env python3
"""Run explicit standalone tests against a private final-source hard copy."""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

OUT = Path(__file__).resolve().parent
SNAPSHOT = json.loads((OUT / "SNAPSHOT.json").read_text())
ROOT = Path(SNAPSHOT["root"])
SCRIPTS = [
    "test_lower_vector.py", "test_lower_matrix.py", "test_matrix_breadth.py",
    "test_math_ops.py", "test_conversions.py", "test_memory_forms.py",
    "test_layout_ops.py", "test_reductions.py", "test_control_flow.py",
    "test_allocate.py", "test_select.py", "test_legalize.py", "test_emit.py",
    "test_build.py", "test_driver_cache.py", "test_backend_vector_state.py",
    "test_cache_dependencies.py", "test_guarded_narrow_access.py",
    "test_elementwise_width.py", "test_lowering_option_identity.py",
]
COMMANDS = [("a100c/tests/" + name, [], 0, False,
             900 if name == "test_matrix_breadth.py" else 600) for name in SCRIPTS]
for name in ("check_no_name_dispatch.py", "check_numeric_policy.py",
             "check_masked_tails.py", "check_stage_barriers.py"):
    COMMANDS.extend([
        ("tools/" + name, [], 0, name == "check_masked_tails.py", 360),
        ("tools/" + name, ["--witness"], 1,
         name in ("check_masked_tails.py", "check_stage_barriers.py"), 360),
    ])


def utc():
    return datetime.now(timezone.utc).isoformat()


def verify_sources():
    return [name for name, expected in SNAPSHOT["source_files"].items()
            if not (ROOT / name).is_file() or hashlib.sha256(
                (ROOT / name).read_bytes()).hexdigest() != expected]


def main():
    assert not verify_sources(), verify_sources()
    env = dict(os.environ)
    for name in list(env):
        if name.startswith("A100C_"):
            del env[name]
    for line in (ROOT / ".env").read_text().splitlines():
        key, sep, value = line.partition("=")
        if sep and not key.startswith("#"):
            env[key] = value
    env.update(PYTHONPATH=os.pathsep.join([
        str(ROOT), str(ROOT / "ops/harness"),
        "/home/i_yinzida/compiler-agent-workflow"]),
        PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
        XDG_CACHE_HOME=str(ROOT / "host-cache"),
        TRITON_CACHE_DIR=str(ROOT / "triton-cache"))
    wrapper = (
        "import pathlib,runpy,sys; import a100c.driver as d; "
        "root=pathlib.Path(sys.argv[1]).resolve(); "
        "assert pathlib.Path(d.__file__).resolve().is_relative_to(root), d.__file__; "
        "script=sys.argv[2];sys.argv=sys.argv[2:]; "
        "runpy.run_path(script,run_name='__main__')")
    results = []
    started = utc()
    for script, args, expected, advisory, timeout in COMMANDS:
        label = Path(script).stem + ("-witness" if args else "")
        log = OUT / (label + ".log")
        env["A100C_CACHE_DIR"] = str(ROOT / "suite-caches" / label)
        if label == "test_backend_vector_state":
            env["A100C_BACKEND_EVIDENCE"] = str(ROOT / "native-state-evidence")
        if label == "test_guarded_narrow_access":
            env["A100C_NARROW_GUARD_EVIDENCE"] = str(ROOT / "guard-evidence.json")
        if label == "test_lowering_option_identity":
            env["A100C_OPTION_IDENTITY_EVIDENCE"] = str(ROOT / "options-evidence.json")
        command = ["nice", "-n", "10", sys.executable, "-B", "-c", wrapper,
                   str(ROOT), str(ROOT / script), *args]
        beginning = time.monotonic()
        timed_out = False
        with log.open("w") as stream:
            process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=stream,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            try:
                code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                code = process.returncode
        text = log.read_text(errors="replace")
        lines = text.splitlines()
        row = {"label": label, "command": command, "expected_exit": expected,
               "actual_exit": code, "timeout": timed_out,
               "elapsed_seconds": round(time.monotonic() - beginning, 3),
               "advisory_protocol": advisory,
               "status": "PASS" if code == expected and not timed_out else
                         "ADVISORY_PROTOCOL_MISMATCH" if advisory and not timed_out else "FAIL",
               "pass_lines": sum(line.startswith("PASS ") for line in lines),
               "fail_lines": [line for line in lines if line.startswith("FAIL ")],
               "skip_lines": [line for line in lines if "SKIP" in line],
               "log": str(log),
               "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest(),
               "test_source_sha256": hashlib.sha256((ROOT / script).read_bytes()).hexdigest()}
        results.append(row)
        report = {"started_utc": started, "updated_utc": utc(),
                  "snapshot": SNAPSHOT["root"], "partial": True, "results": results}
        (OUT / "RESULTS.json").write_text(json.dumps(report, indent=2))
        print(json.dumps({key: row[key] for key in
              ("label", "actual_exit", "status", "pass_lines", "elapsed_seconds")}), flush=True)
    changes = verify_sources()
    report.update(partial=False, completed_utc=utc(), source_changes=changes,
                  all_required_pass=not changes and all(
                      row["status"] != "FAIL" for row in results))
    (OUT / "RESULTS.json").write_text(json.dumps(report, indent=2))
    return 0 if report["all_required_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
