#!/usr/bin/env python3
"""One infrastructure retry plus final MIR/spill and baseline-witness checks."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

OUT = Path(__file__).resolve().parent
snapshot = json.loads((OUT / "SNAPSHOT.json").read_text())
final = Path(snapshot["root"])
baseline = Path((OUT / "BARRIER_BASELINE_ROOT.txt").read_text().strip())
commands = [
    ("matrix_breadth-fixture-retry", final, "a100c/tests/test_matrix_breadth.py", [], 900),
    ("mir_verifier-final", final, "a100c/tests/test_mir_verifier.py", [], 300),
    ("t029_spill-final", final, "a100c/tests/test_t029_repairs.py", [], 600),
    ("stage-barrier-baseline", baseline, "tools/check_stage_barriers.py", ["--witness"], 360),
]
saved = OUT / "SUPPLEMENTAL_RESULTS.json"
rows = json.loads(saved.read_text())["results"] if saved.is_file() else []
for label, root, script, args, timeout in commands:
    if any(row["label"] == label for row in rows):
        continue  # Preserve already executed, source-bound results on resume.
    env = {k: v for k, v in os.environ.items() if not k.startswith("A100C_")}
    for line in (root / ".env").read_text().splitlines():
        key, sep, value = line.partition("=")
        if sep and not key.startswith("#"):
            env[key] = value
    env.update(PYTHONPATH=os.pathsep.join([str(root), str(root / "ops/harness"),
        "/home/i_yinzida/compiler-agent-workflow"]), PYTHONDONTWRITEBYTECODE="1",
        OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1",
        A100C_CACHE_DIR=str(root / "supplemental-caches" / label))
    wrapper = ("import pathlib,runpy,sys;import a100c.driver as d;"
        "root=pathlib.Path(sys.argv[1]).resolve();"
        "assert pathlib.Path(d.__file__).resolve().is_relative_to(root),d.__file__;"
        "print('actual_driver='+str(d.__file__),flush=True);"
        "script=sys.argv[2];sys.argv=sys.argv[2:];runpy.run_path(script,run_name='__main__')")
    command = ["nice", "-n", "10", sys.executable, "-B", "-c", wrapper,
               str(root), str(root / script), *args]
    log = OUT / (label + ".log")
    start = time.monotonic()
    timed_out = False
    with log.open("w") as stream:
        process = subprocess.Popen(command, cwd=root, env=env, stdout=stream,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        try:
            code = process.wait(timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            code = process.returncode
    text = log.read_text(errors="replace")
    for line in text.splitlines():
        if line.startswith("# evidence: "):
            source = Path(line.split(": ", 1)[1])
            if source.is_file():
                shutil.copy2(source, OUT / (label + "-native-evidence.json"))
    row = {"label": label, "root": str(root), "command": command,
           "actual_exit": code, "timeout": timed_out,
           "elapsed_seconds": round(time.monotonic() - start, 3),
           "log": str(log), "log_sha256": hashlib.sha256(log.read_bytes()).hexdigest(),
           "test_source_sha256": hashlib.sha256((root / script).read_bytes()).hexdigest(),
           "pass_lines": sum(s.startswith("PASS ") for s in text.splitlines()),
           "fail_lines": [s for s in text.splitlines() if s.startswith("FAIL ")]}
    rows.append(row)
    (OUT / "SUPPLEMENTAL_RESULTS.json").write_text(json.dumps({
        "updated_utc": datetime.now(timezone.utc).isoformat(), "partial": True,
        "results": rows}, indent=2))
    print(json.dumps(row), flush=True)
changes = [p for p, h in snapshot["source_files"].items()
           if hashlib.sha256((final / p).read_bytes()).hexdigest() != h]
(OUT / "SUPPLEMENTAL_RESULTS.json").write_text(json.dumps({
    "completed_utc": datetime.now(timezone.utc).isoformat(), "partial": False,
    "source_changes": changes, "results": rows}, indent=2))
