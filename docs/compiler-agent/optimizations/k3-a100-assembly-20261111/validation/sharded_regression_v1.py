#!/usr/bin/env python3
"""Use the unchanged scan runner in complete-operator shards, then audit IDs.

This is human-guided validation evidence, not an engine regression/gate claim.
No corpus or harness code is changed. Each shard owns its artifact/build cache.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def source_hashes(root):
    paths = [p for p in (root / "a100c").rglob("*")
             if p.is_file() and p.suffix in (".py", ".c", ".h", ".S")
             and not any(x in p.relative_to(root).parts
                         for x in ("cache", "build", "__pycache__", "annotated-cache",
                                   "host-cache", "triton-cache"))]
    paths += [root / "tools/run_scan.py", root / ".env",
              root / "ops/suite/manifest.json"]
    paths.extend(root / name for name in ("chip.md", "EXECUTION_RESOURCES.json",
                                         "EXECUTION_MODEL.json", "ARCHITECTURE_CONSTRAINTS.json")
                 if (root / name).exists())
    # Bind the actual external comparator, transport and operator sources,
    # not just the compiler files and the manifest's file-name list.
    for tree in (root / "a100_support", root / "ops/harness", root / "ops/suite"):
        paths.extend(p for p in tree.rglob("*")
                     if p.is_file() and p.suffix in (".py", ".sh", ".json")
                     and "__pycache__" not in p.relative_to(tree).parts)
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(paths))}


def prepare(args):
    root, out = args.root.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if (out / "plan.json").exists():
        raise SystemExit("Plan already exists; use a fresh output directory")
    sys.path[:0] = [str(root), str(root / "ops/harness"), str(root / "tools")]
    spec = importlib.util.spec_from_file_location("k3_scan", root / "tools/run_scan.py")
    scan = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scan)
    if scan.ROOT.resolve() != root or (root / "tools/run_scan.py").is_symlink():
        raise SystemExit("The frozen scan runner must be a real copied file")
    for name, module in list(sys.modules.items()):
        if name == "a100c" or name.startswith("a100c."):
            raw = getattr(module, "__file__", None)
            if raw and not Path(raw).resolve().is_relative_to(root):
                raise SystemExit("Compiler import outside frozen source: " + name)
    rows = [{k: r[k] for k in ("id", "operator", "shape", "dtype", "group")}
            for r in scan.enumerated_rows(str(root / "ops/suite/manifest.json"), None, None)]
    ids = [r["id"] for r in rows]
    if len(ids) != len(set(ids)) or len(ids) != 2734:
        raise SystemExit("Original full corpus is not the expected unique 2734 cases")
    historical = json.loads(args.historical_report.read_text())
    weights = defaultdict(float)
    for row in historical["cases"]:
        weights[row["operator"]] += row.get("seconds", 1.0)
    by_operator = defaultdict(list)
    for row in rows:
        by_operator[row["operator"]].append(row)
    partitions = [dict(operators=[], estimated_baseline_case_seconds=0.0, case_ids=[])
                  for _ in range(args.shards)]
    for op in sorted(by_operator, key=lambda x: (-weights[x], x)):
        part = min(partitions, key=lambda p: p["estimated_baseline_case_seconds"])
        part["operators"].append(op)
        part["case_ids"].extend(r["id"] for r in by_operator[op])
        part["estimated_baseline_case_seconds"] += max(weights[op], 0.01)
    scratch = Path(tempfile.mkdtemp(prefix="a100-k3-full-regression-caches-"))
    for index, part in enumerate(partitions):
        directory = out / f"shard-{index}"
        directory.mkdir()
        part.update(index=index, directory=str(directory),
                    cache=str(scratch / f"shard-{index}"))
        part["command"] = [sys.executable, "-B", str(root / "tools/run_scan.py"), "run",
                           "--threads", "1", "--resource-threads", "4",
                           "--case-timeout", str(args.case_timeout),
                           "--report", str(directory / "report.json"),
                           "--journal", str(directory / "journal.jsonl")]
        for op in sorted(part["operators"]):
            part["command"].extend(["--operator", op])
        part["logical_runner_command"] = part["command"]
        part["command"] = [sys.executable, "-B", str(Path(__file__).with_name("scan_entry_v1.py")),
                           "--root", str(root), "--binding", str(directory / "import-binding.json"),
                           "--", *part["logical_runner_command"][3:]]
    plan = dict(schema="a100-manual-sharded-regression/v1", root=str(root),
                created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                scope="Original full corpus; runner concurrency is not single-operator multi-core evidence; no engine state/gate mutation",
                cases=rows, source_hashes=source_hashes(root), partitions=partitions,
                original_comparison_policy="Unchanged run_scan.py builds each original case and calls the corpus comparator",
                no_resume=True, case_timeout=args.case_timeout,
                validation_entry_sha256=hashlib.sha256(
                    Path(__file__).with_name("scan_entry_v1.py").read_bytes()).hexdigest())
    dump(out / "plan.json", plan)
    print(json.dumps(dict(plan=str(out / "plan.json"), cases=len(rows),
                         shards=[dict(index=p["index"], operators=len(p["operators"]),
                                      cases=len(p["case_ids"]),
                                      estimated_seconds=round(p["estimated_baseline_case_seconds"], 1))
                                 for p in partitions]), indent=2))


def run(args):
    plan = json.loads(args.plan.read_text())
    root = Path(plan["root"])
    if source_hashes(root) != plan["source_hashes"]:
        raise SystemExit("Frozen source changed before execution")
    if hashlib.sha256(Path(__file__).with_name("scan_entry_v1.py").read_bytes()).hexdigest() != plan["validation_entry_sha256"]:
        raise SystemExit("Validation import-check launcher changed after preparation")
    started = time.monotonic()
    active = []
    try:
        for part in plan["partitions"]:
            directory = Path(part["directory"])
            if (directory / "report.json").exists() or (directory / "journal.jsonl").exists():
                raise SystemExit("Fresh run required; existing report/journal would mix executions")
            env = dict(os.environ, A100C_CACHE_DIR=part["cache"],
                       A100_EXECUTION_TIMEOUT=str(plan["case_timeout"]),
                       PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="1",
                       OMP_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
            env["PYTHONPATH"] = os.pathsep.join([str(root), str(root / "ops/harness"),
                                                  "/home/i_yinzida/compiler-agent-workflow"])
            log = (directory / "execution.log").open("w")
            process = subprocess.Popen(["nice", "-n", "10", *part["command"]],
                                       cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT,
                                       start_new_session=True)
            active.append((part, process, log))
        while any(p.poll() is None for _, p, _ in active):
            if time.monotonic() - started > args.max_wall:
                raise TimeoutError("Whole validation campaign reached its recorded wall budget")
            time.sleep(10)
    finally:
        status = []
        for part, process, log in active:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=10)
            log.close()
            status.append(dict(index=part["index"], exit_code=process.returncode))
        dump(args.plan.parent / "process-status.json",
             dict(seconds=round(time.monotonic() - started, 3), shards=status,
                  frozen_source_unchanged=source_hashes(root) == plan["source_hashes"]))
    if any(r["exit_code"] != 0 for r in status):
        raise SystemExit("At least one shard did not finish; inspect retained raw evidence")


def merge(args):
    plan = json.loads(args.plan.read_text())
    root = Path(plan["root"])
    if source_hashes(root) != plan["source_hashes"]:
        raise SystemExit("Frozen source changed during campaign")
    by_id, raw = {}, []
    for part in plan["partitions"]:
        path = Path(part["directory"]) / "report.json"
        report = json.loads(path.read_text())
        binding = json.loads((path.parent / "import-binding.json").read_text())
        if not binding.get("assertions_passed") or Path(binding["root"]) != root:
            raise SystemExit(f"Invalid or missing real import binding: {path}")
        if report.get("partial") or report.get("missing_case_ids"):
            raise SystemExit(f"Incomplete shard: {path}")
        if {r["id"] for r in report["cases"]} != set(part["case_ids"]):
            raise SystemExit(f"Shard case identity set differs: {path}")
        for row in report["cases"]:
            if row["id"] in by_id:
                raise SystemExit("Duplicate original case: " + row["id"])
            if row.get("passed") and (row.get("status") != "PASS" or
                    not all(row.get(k) for k in ("compiled", "executed", "compared"))):
                raise SystemExit("PASS row lacks actual compile/execute/compare: " + row["id"])
            by_id[row["id"]] = row
        raw.append(dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    originals = {r["id"]: r for r in plan["cases"]}
    if set(by_id) != set(originals):
        raise SystemExit("Full original manifest differs: missing/extra cases")
    for key, source in originals.items():
        row = by_id[key]
        for field in ("operator", "shape", "dtype", "group"):
            if row.get(field) != source.get(field):
                raise SystemExit("Original case metadata changed: " + key + ":" + field)
    rows = [by_id[r["id"]] for r in plan["cases"]]
    merged = dict(schema="input-regression/v1", run_id=None,
                  command="unchanged run_scan.py in complete-operator shards; exact argv in plan.json",
                  partial=False, missing_case_ids=[], cases=rows)
    status = Counter(r["status"] for r in rows)
    summary = dict(schema="a100-manual-sharded-regression-summary/v1", cases=len(rows),
                   unique_case_ids=len(by_id), statuses=dict(status), raw_reports=raw,
                   source_unchanged=True,
                   every_pass_compiled_executed_compared=True,
                   all_original_cases_pass=status == {"PASS": len(rows)},
                   per_group={g: dict(Counter(r["status"] for r in rows if r["group"] == g))
                              for g in sorted({r["group"] for r in rows})},
                   failures=[r for r in rows if r["status"] != "PASS"],
                   scope="Independent human-guided full-input evidence, not engine G8/G9 acceptance",
                   resource_rows=[r for r in rows if r.get("resource_evidence")])
    dump(args.plan.parent / "report.json", merged)
    dump(args.plan.parent / "summary.json", summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in ("resource_rows", "failures")}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--historical-report", type=Path, required=True)
    p.add_argument("--shards", type=int, choices=(1, 2, 4), default=4)
    p.add_argument("--case-timeout", type=int, default=600)
    p.set_defaults(handler=prepare)
    p = sub.add_parser("run")
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--max-wall", type=int, default=10800)
    p.set_defaults(handler=run)
    p = sub.add_parser("merge")
    p.add_argument("--plan", type=Path, required=True)
    p.set_defaults(handler=merge)
    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
