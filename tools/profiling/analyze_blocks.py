#!/usr/bin/env python3
"""Per-loop-nest attribution of dynamic instructions for one metrics run.

Reads a collect_metrics.py output directory (counts.r1/r2.json + the
artifact cache entry recorded in metrics.json), rebuilds the pc map
(insn_manifest), attaches the enclosing block label to every program pc
(the label preceding it in program.S order), and aggregates the
steady-state per-call counts by block class:

  pack-b   pb*     the IME B-operand column-major scalar pack outer loops
  pack-q   pq*     the pack's inner per-element copy loops
  pack-sc  *_sc_*  the alternative IME staging scalar loops (_emit_pack_loops)
  k-loop   mk*     the dot K-loop
  tile     mtile*  the output tile loop
  chunk    chunk*  the vectorizer's chunk loops
  other    <rest>  everything else in the program region
  runtime  -       outside the program region (pool/barrier/...)

Usage: python3 tools/profiling/analyze_blocks.py <metrics-dir> [--top N]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "profiling"))

from insn_manifest import Manifest, parse_program_s  # noqa: E402


def block_class(label: str) -> str:
    name = label.strip()
    if name.startswith(".L"):
        name = name[2:]          # the emitter's .L{block} prefix
    name = name.rstrip(":")
    if name.startswith("pq"):
        return "pack-q(inner element copy)"
    if name.startswith("pb"):
        return "pack-b(column outer)"
    if "_sc_" in name or name.endswith("_sc_head"):
        return "pack-sc(staging scalar)"
    if name.startswith("mk"):
        return "k-loop"
    if name.startswith("mtile"):
        return "tile-loop"
    if name.startswith("chunk"):
        return "chunk-loop"
    return "other"


def main() -> int:
    metrics_dir = Path(sys.argv[1])
    top = 12
    if "--top" in sys.argv:
        top = int(sys.argv[sys.argv.index("--top") + 1])
    metrics = json.loads((metrics_dir / "metrics.json").read_text())
    entry = Path(metrics["artifact"]["cache_entry"])
    executable = Path(json.loads(
        (entry / "artifact.json").read_text()).get("executable")
        or entry / "operator_exec")
    if not executable.is_file():
        executable = entry / "operator_exec"

    manifest = Manifest(entry)
    pc_map, region, diag = manifest.build_pc_map(executable,
                                                 metrics_dir / "asm")
    lines = parse_program_s((entry / "program.S").read_text())

    # pc -> enclosing block label (the last label at or before the line)
    line_label = {}
    current = None
    for rec in lines:
        if rec["kind"] == "label":
            current = rec["text"].strip()
        line_label[rec["line"]] = current
    pc_label = {}
    for pc, record in pc_map.items():
        pc_label[pc] = line_label.get(record["line"]) or "<none>"

    r1 = json.loads((metrics_dir / "counts.r1.json").read_text())
    r2 = json.loads((metrics_dir / "counts.r2.json").read_text())
    r1_pc = {row["pc"]: row["executions"] for row in r1["instructions"]}
    repeats = metrics["steady_repeats"]
    pc_call = {}
    for row in r2["instructions"]:
        delta = row["executions"] - r1_pc.get(row["pc"], 0)
        pc_call[row["pc"]] = max(delta, 0) / repeats
    total = sum(pc_call.values())

    by_class, by_label, by_origin_class = {}, {}, {}
    for pc, amount in pc_call.items():
        record = pc_map.get(pc)
        if record is None:
            cls = "runtime/loader"
        else:
            cls = block_class(pc_label[pc])
            by_origin_class[(cls, record["origin"])] = \
                by_origin_class.get((cls, record["origin"]), 0) + amount
        by_class[cls] = by_class.get(cls, 0) + amount
        if record is not None:
            label = pc_label[pc]
            by_label[label] = by_label.get(label, 0) + amount

    result = {
        "case": metrics["case"],
        "threads": metrics["threads"],
        "per_call_total": total,
        "by_class": {k: round(v) for k, v in
                     sorted(by_class.items(), key=lambda kv: -kv[1])},
        "by_class_pct": {k: round(v / total * 100, 1) for k, v in
                         sorted(by_class.items(), key=lambda kv: -kv[1])},
        "top_labels": [{"label": k, "per_call": round(v),
                        "pct": round(v / total * 100, 2)}
                       for k, v in sorted(by_label.items(),
                                          key=lambda kv: -kv[1])[:top]],
        "class_x_origin": {f"{c}|{o}": round(v) for (c, o), v in
                           sorted(by_origin_class.items(),
                                  key=lambda kv: -kv[1])[:top * 2]},
        "asm_join": diag,
    }
    out = metrics_dir / "blocks.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"{metrics['case']} t{metrics['threads']} total={total/1e6:.2f}M")
    for cls, pct in result["by_class_pct"].items():
        print(f"  {cls:<28} {pct:5.1f}%")
    print(f"  -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
