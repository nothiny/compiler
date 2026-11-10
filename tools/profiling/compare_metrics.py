#!/usr/bin/env python3
"""Before/after comparison table for the matmul round's metric sweeps.

Reads two metrics roots (baseline and candidate), matches by run-directory
name, and prints/writes the per-case table: per-call total, category
shares, pack-class share (from blocks.json when present), spill traffic
and the relative change of the total.

Usage: python3 tools/profiling/compare_metrics.py <baseline-root> \
           <candidate-root> [--out <json-path>]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def load(root: Path):
    runs = {}
    for f in sorted(root.glob("*/metrics.json")):
        m = json.loads(f.read_text())
        runs[f.parent.name] = m
    return runs


def blocks_of(run_dir: Path):
    f = run_dir / "blocks.json"
    if not f.is_file():
        return None
    return json.loads(f.read_text())


def pack_share(blocks):
    if blocks is None:
        return None
    pct = blocks.get("by_class_pct", {})
    return pct.get("pack-q(inner element copy)", 0) + \
        pct.get("pack-b(column outer)", 0)


def main() -> int:
    baseline_root, candidate_root = (Path(sys.argv[1]), Path(sys.argv[2]))
    out_json = None
    if "--out" in sys.argv:
        out_json = Path(sys.argv[sys.argv.index("--out") + 1])
    base, cand = load(baseline_root), load(candidate_root)
    names = sorted(set(base) & set(cand))
    rows = []
    for name in names:
        b, c = base[name], cand[name]
        if b.get("problems") or c.get("problems"):
            rows.append({"run": name, "note": "problems present",
                         "base_problems": b.get("problems"),
                         "cand_problems": c.get("problems")})
            continue
        bt = b["steady_state"]["per_call_total"]
        ct = c["steady_state"]["per_call_total"]
        bb = blocks_of(baseline_root / name)
        cb = blocks_of(candidate_root / name)
        rows.append({
            "run": name,
            "base_total": bt,
            "cand_total": ct,
            "total_change": (ct - bt) / bt if bt else None,
            "base_pack_pct": pack_share(bb),
            "cand_pack_pct": pack_share(cb),
            "base_reload": b["program_region"]["spill_traffic"]
            ["reload_instructions"],
            "cand_reload": c["program_region"]["spill_traffic"]
            ["reload_instructions"],
            "base_categories": b["steady_state"]["per_call_categories"],
            "cand_categories": c["steady_state"]["per_call_categories"],
        })
    print(f"{'run':<24} {'base':>10} {'cand':>10} {'change':>8} "
          f"{'pack% b->c':>14} {'reload b->c':>18}")
    for r in rows:
        if "note" in r:
            print(f"{r['run']:<24} PROBLEMS: {r.get('base_problems') or ''}"
                  f"{r.get('cand_problems') or ''}")
            continue
        print(f"{r['run']:<24} {r['base_total']/1e6:9.2f}M "
              f"{r['cand_total']/1e6:9.2f}M "
              f"{r['total_change']*100:7.1f}% "
              f"{(r['base_pack_pct'] or 0):6.1f}->{(r['cand_pack_pct'] or 0):5.1f}"
              f" {r['base_reload']/1e3:7.1f}K->{r['cand_reload']/1e3:7.1f}K")
    if out_json:
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(
            {"schema": "a100c-matmul-comparison/v1",
             "baseline_root": str(baseline_root),
             "candidate_root": str(candidate_root),
             "rows": rows}, indent=2) + "\n")
        print(f"-> {out_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
