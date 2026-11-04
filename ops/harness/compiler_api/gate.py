"""Single-process compile gate: is this corpus affordable to compile?

The gate answers one question per round: *can this corpus be compiled and
verified inside the budget?*  It runs every case through a ``Device`` (the
reference CUDA device, or a compiler adapter that follows
``COMPILE_CONTRACT.md``), then reports the numbers that decide whether a
1000-operator experiment is feasible:

* ``cases`` / ``identities`` -- how much of the corpus is actually new work
  (an identity is one compilation; see ``identity.py``);
* per-identity compile cost -- the *first* launch of an identity is its
  compile, every later case on that identity is a cache hit;
* the tail (p50/p90/p99/max) -- gate time is set by the tail, not the mean;
* failures by class, with ``COMPILE_BUDGET_EXCEEDED`` counted as a compiler
  defect (never as a corpus defect: an operator that needs 90 s to compile is
  a compiler problem, and hiding it by deleting the case is how a corpus rots).

    # reference device (stock Triton, torch-free): measures the corpus itself
    python3 harness/compiler_api/gate.py --device cuda

    # a compiler adapter, with the production ceilings
    python3 harness/compiler_api/gate.py --device mycompiler:Device \
        --compile-budget 10 --max-wall 900 --report gate.json

Exit code is 0 when every threshold holds, 1 otherwise, so CI can gate on it.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]
ROOT = HARNESS.parent
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from compiler_api import identity as identity_lib          # noqa: E402
from compiler_api.run_cases import (                      # noqa: E402
    GROUP_ORDER,
    cases_from_manifest,
    enumerate_cases,
    run_all,
    summarize,
)
from opslib.device import make_device                     # noqa: E402

#: Statuses that are a compiler defect rather than a corpus defect.
COMPILER_DEFECTS = ("COMPILE_BUDGET_EXCEEDED", "LAUNCH_FAIL")


def _percentile(values, q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round(q * (len(ordered) - 1))))
    return ordered[index]


def identity_costs(rows) -> dict:
    """Per-identity compile cost: the first row of an identity pays for it.

    Returns ``{identity: {seconds, operator, shape, dtype}}`` so a report can
    name the offender instead of printing a hash.
    """
    costs: dict[str, dict] = {}
    for row in rows:
        ident = row.get("identity")
        if not ident or ident in costs or row.get("launch_seconds") is None:
            continue
        costs[ident] = {"seconds": float(row["launch_seconds"]),
                        "operator": row["operator"],
                        "shape": row["shape"],
                        "dtype": row["dtype"]}
    return costs


def evaluate(rows, *, wall_seconds: float, min_ratio: float,
             max_p99: float | None, max_wall: float | None,
             compile_budget: float | None) -> dict:
    """Turn rows into a verdict.  Pure function, so it is easy to test."""
    cases = len(rows)
    identities = {r["identity"] for r in rows if r.get("identity")}
    costs = identity_costs(rows)
    cost_values = [item["seconds"] for item in costs.values()]
    statuses = summarize(rows)
    failures = {s: n for s, n in statuses.items() if s != "PASS"}

    compile_total = sum(cost_values)
    report = {
        "cases": cases,
        "identities": len(identities),
        "cases_per_identity": round(cases / len(identities), 3) if identities else None,
        "statuses": statuses,
        "failures": failures,
        "compiler_defects": {s: n for s, n in failures.items()
                             if s in COMPILER_DEFECTS},
        "compile": {
            "identities_measured": len(cost_values),
            "total_s": round(compile_total, 2),
            "p50_s": round(statistics.median(cost_values), 3) if cost_values else None,
            "p90_s": round(_percentile(cost_values, 0.9), 3) if cost_values else None,
            "p99_s": round(_percentile(cost_values, 0.99), 3) if cost_values else None,
            "max_s": round(max(cost_values), 3) if cost_values else None,
            "over_budget": sum(1 for c in cost_values
                               if compile_budget is not None and c > compile_budget),
        },
        "wall_seconds": round(wall_seconds, 2),
        "top_offenders": [
            {"identity": ident, "seconds": round(item["seconds"], 2),
             "operator": item["operator"], "shape": item["shape"],
             "dtype": item["dtype"]}
            for ident, item in sorted(costs.items(),
                                      key=lambda kv: -kv[1]["seconds"])[:10]
        ],
    }
    checks = {
        "no_failures": not failures,
        "dedupe": (report["cases_per_identity"] or 0) >= min_ratio,
        "p99": max_p99 is None or (report["compile"]["p99_s"] or 0) <= max_p99,
        "wall": max_wall is None or wall_seconds <= max_wall,
        "budget": compile_budget is None or report["compile"]["over_budget"] == 0,
    }
    report["checks"] = checks
    report["passed"] = all(checks.values())
    return report


def format_report(report) -> str:
    compile_ = report["compile"]
    lines = [
        f"cases        {report['cases']}",
        f"identities   {report['identities']}   "
        f"({report['cases_per_identity']} cases/identity)",
        f"statuses     {report['statuses']}",
        f"compile      total {compile_['total_s']}s   p50 {compile_['p50_s']}s   "
        f"p90 {compile_['p90_s']}s   p99 {compile_['p99_s']}s   max {compile_['max_s']}s",
        f"wall         {report['wall_seconds']}s",
    ]
    if report["top_offenders"]:
        lines.append("slowest identities (compile):")
        for item in report["top_offenders"]:
            if item["seconds"] >= 1.0:
                lines.append(f"  {item['seconds']:8.2f}s  {item['operator']} "
                             f"{item['shape']} {item['dtype']}  ({item['identity']})")
    lines.append("checks       " + "  ".join(
        f"{name}={'ok' if ok else 'FAIL'}" for name, ok in report["checks"].items()))
    lines.append("verdict      " + ("PASS" if report["passed"] else "FAIL"))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--device", default="cuda",
                        help="reference device (cpu/cuda/torch-*) or adapter "
                             "('module:attr') following COMPILE_CONTRACT.md")
    parser.add_argument("--group", default=None, choices=list(GROUP_ORDER) + [None])
    parser.add_argument("--operator", action="append", default=None)
    parser.add_argument("--manifest", default=None, metavar="PATH",
                        help="run exactly the operators listed in a suite manifest "
                             "(suite/manifest.json)")
    parser.add_argument("--seed", type=int, default=30)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--compile-budget", type=float, default=None, metavar="SEC",
                        help="per-identity compile ceiling; overruns become "
                             "COMPILE_BUDGET_EXCEEDED failures")
    parser.add_argument("--max-p99", type=float, default=10.0, metavar="SEC",
                        help="fail when the identity p99 exceeds this (default 10)")
    parser.add_argument("--max-wall", type=float, default=900.0, metavar="SEC",
                        help="fail when the whole run exceeds this (default 900)")
    parser.add_argument("--min-cases-per-identity", type=float, default=1.25,
                        help="fail when the corpus compiles more than ~1/1.25 "
                             "times per identity (default 1.25)")
    parser.add_argument("--journal", default=None)
    parser.add_argument("--report", default=None, metavar="PATH",
                        help="write the JSON verdict here")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    operators = None
    if args.operator:
        operators = set()
        for raw in args.operator:
            path = Path(raw) if Path(raw).is_absolute() else ROOT / raw
            try:
                operators.add(str(path.resolve().relative_to(ROOT)))
            except ValueError:
                operators.add(str(raw))

    paths = cases_from_manifest(args.manifest) if args.manifest else None
    device = make_device(args.device)
    began = time.perf_counter()
    rows = run_all(device, channel="all", seed=args.seed, group=args.group,
                   use_golden=True, operators=operators, paths=paths,
                   compile_budget=args.compile_budget, journal=args.journal,
                   limit=args.limit)
    wall = time.perf_counter() - began

    report = evaluate(rows, wall_seconds=wall,
                      min_ratio=args.min_cases_per_identity,
                      max_p99=args.max_p99, max_wall=args.max_wall,
                      compile_budget=args.compile_budget)
    report["device"] = args.device
    report["group"] = args.group or "all"
    report["operator_cases"] = dict(sorted(
        Counter(r["operator"] for r in rows).items()))
    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report).write_text(json.dumps(report, indent=2) + "\n")
    if not args.quiet:
        print(format_report(report))
        for row in rows:
            if row["status"] != "PASS":
                print(f"{row['status']:24s} {row['operator']} {row['shape']} "
                      f"{row['dtype']} :: {row['detail']}")
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
