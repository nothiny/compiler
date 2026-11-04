"""Compare kernel times against the Triton baseline, provenance-aware.

Reads a compiler report and a Triton baseline produced by ``bench/run.py``
and, per entry, reports ``speedup = triton_kernel_s / compiler_kernel_s``
(> 1 means the compiler is faster).  Grouped by class and overall (geomean).

Entries pair only when their ``operator_sha256`` **and** resolved shape
match: a changed operator file or a differently-sized run is reported in a
"stale baseline" section and never enters the geomean -- an old baseline
can no longer be silently compared against a changed kernel.  A compiler
record that was not verified against the oracle (``verified: false``, i.e.
run with ``--no-verify``) is never scored either: speed without correctness
does not count.

    python3 bench/report.py --report results/<compiler>/BENCH_REPORT.json \
                            --triton results/<triton>/BENCH_TRITON.json
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]         # the corpus root


def _geomean(values):
    values = [v for v in values if v and v > 0]
    return math.exp(sum(math.log(v) for v in values) / len(values)) if values else None


def _pair(compiler, triton):
    """Pair entries by id; returns (paired, stale) with provenance checks."""
    paired, stale = [], []
    for eid, base in triton.items():
        mine = compiler.get(eid)
        if not (base.get("status") == "PASS" and mine
                and mine.get("status") == "PASS"):
            continue
        if mine.get("verified") is False:
            stale.append((eid, "compiler record not verified (rerun without --no-verify)"))
            continue
        base_sha = base.get("operator_sha256")
        mine_sha = mine.get("operator_sha256")
        if not base_sha or not mine_sha:
            # legacy records (e.g. results/reference/) carry no provenance;
            # pairing them would silently skip the staleness check entirely
            stale.append((eid, "missing operator_sha256 (legacy record)"))
            continue
        if base_sha != mine_sha:
            stale.append((eid, "operator file changed"))
            continue
        if list(base.get("shape", ())) != list(mine.get("shape", ())):
            stale.append((eid, f"shape {base.get('shape')} vs {mine.get('shape')}"))
            continue
        paired.append({"id": eid, "class": base["class"], "shape": base["shape"],
                       "triton_kernel_s": base["kernel_s"],
                       "compiler_kernel_s": mine["kernel_s"],
                       "speedup": base["kernel_s"] / mine["kernel_s"]})
    return paired, stale


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default=None,
                        help="compiler report (default: newest <results-dir>/*/BENCH_REPORT.json)")
    parser.add_argument("--triton", default=None,
                        help="triton baseline (default: newest <results-dir>/*/BENCH_TRITON.json)")
    parser.add_argument("--results-dir", default=str(ROOT / "results"),
                        help="where to look for the newest reports (the --out-dir "
                             "given to bench/run.py)")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    def newest(pattern):
        candidates = sorted(
            (p for p in Path(args.results_dir).glob(f"*/{pattern}")
             if p.parent.name != "reference"),
            key=lambda p: p.stat().st_mtime)
        if not candidates:
            raise SystemExit(f"no {args.results_dir}/*/{pattern} found; pass "
                             "--results-dir, --report or --triton")
        return candidates[-1]

    report_path = Path(args.report) if args.report else newest("BENCH_REPORT.json")
    triton_path = Path(args.triton) if args.triton else newest("BENCH_TRITON.json")

    compiler = {r["id"]: r for r in json.loads(report_path.read_text())["entries"]}
    triton = {r["id"]: r for r in json.loads(triton_path.read_text())["entries"]}

    rows, stale = _pair(compiler, triton)

    print(f"compiler: {report_path}")
    print(f"triton:   {triton_path}")
    print(f"entries compared: {len(rows)}")
    for cls in ("memory", "reduction", "compute"):
        vals = [r["speedup"] for r in rows if r["class"] == cls]
        if not vals:
            continue
        print(f"  {cls:9s} n={len(vals):3d} geomean={_geomean(vals):.3f}x "
              f"min={min(vals):.3f}x max={max(vals):.3f}x")
    allv = [r["speedup"] for r in rows]
    if allv:
        print(f"  {'overall':9s} n={len(allv):3d} geomean={_geomean(allv):.3f}x")

    if stale:
        print(f"\nstale baselines (excluded from the geomean): {len(stale)}")
        for eid, why in stale[:10]:
            print(f"  {eid}: {why}")

    print("\nworst entries (compiler slower):")
    for r in sorted(rows, key=lambda r: r["speedup"])[:10]:
        print(f"  {r['speedup']:6.3f}x {r['class']:9s} {r['id']:28s} "
              f"triton={r['triton_kernel_s']*1e3:9.4f}ms compiler={r['compiler_kernel_s']*1e3:9.4f}ms")

    if args.out:
        Path(args.out).write_text(json.dumps(
            {"schema": "tritonbench-bench-summary/2", "metric": "kernel_time_s",
             "entries": rows, "stale": [{"id": e, "reason": w} for e, w in stale]},
            indent=2) + "\n")
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
