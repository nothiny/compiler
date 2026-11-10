#!/usr/bin/env python3
"""Collect guest dynamic instruction metrics for matmul-round cases.

For one (case, threads) configuration this tool:

1. stages the case exactly like the acceptance scan does
   (``a100_support.native_device`` + the project factory, golden inputs,
   same seed);
2. runs the staged executable under QEMU with the round's full
   instruction-count plugin twice: ``--repeats 1`` and
   ``--repeats 1+R`` -- the difference divided by R is the steady-state
   per-call profile (pool init, bundle open and loader work cancel out);
3. joins the per-pc dynamic counts with the compiler-side instruction
   manifest (``insn_manifest.py``): origins (spill/reload/vec-config/
   memory/const/...), the runtime region by symbol, spill/reload traffic
   (executions; bytes are model values), hot pcs with source locations.

Judge quantity: guest dynamic instruction executions.  QEMU wall time is
recorded only as auxiliary context.  The staged directory is a slim copy
of the artifact cache entry, so the manifest is loaded from
``a100c/cache/<key>/`` (key read from the staged artifact.json) after a
byte check that both executables agree.

Usage:
  python3 tools/profiling/collect_metrics.py \
      --operator suite/dev/matmul_kernel.py --shape 128,128,128 \
      --dtype float16 --threads 1 --steady-repeats 5 \
      --out docs/compiler-agent/optimizations/matmul/baseline/metrics/<name>
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLING = ROOT / "tools" / "profiling"
sys.path.insert(0, str(TOOLING))

from insn_manifest import Manifest  # noqa: E402


def load_env():
    for line in (ROOT / ".env").read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ[key.strip()] = value.strip()


def import_scan_driver():
    for path in (str(ROOT), str(ROOT / "ops" / "harness")):
        if path not in sys.path:
            sys.path.insert(0, path)
    spec = importlib.util.spec_from_file_location(
        "a100c_scan_driver", ROOT / "tools" / "run_scan.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_shape(raw: str):
    return [int(v) for v in raw.split(",") if v.strip()]


def find_row(scan, operator: str, shape, dtype: str):
    rows = list(scan.enumerated_rows(
        str(ROOT / "ops" / "suite" / "manifest.json"), None, [operator]))
    matches = [r for r in rows if r["shape"] == shape and r["dtype"] == dtype]
    if not matches:
        available = sorted({(tuple(r["shape"]), r["dtype"]) for r in rows})
        raise SystemExit(f"case not found: {operator} {shape} {dtype}; "
                         f"available: {available}")
    return matches[0]


def run_qemu(executable: Path, bundle: Path, threads: int, repeats: int,
             counts_out: Path):
    plugin = TOOLING / "full_instruction_counts.so"
    cmd = [os.environ["A100_QEMU"], "-L", os.environ["A100_SYSROOT"],
           "-cpu", os.environ.get("A100_QEMU_CPU",
                                  "max,vlen=1024,elen=64,vext_spec=v1.0"),
           "-plugin", f"{plugin},out={counts_out}",
           str(executable), "--bundle", str(bundle),
           "--threads", str(threads), "--repeats", str(repeats)]
    loader = os.environ.get("A100_QEMU_LOADER")
    if loader:
        cmd = [loader, "--library-path",
               os.environ["A100_QEMU_HOST_LIB"], *cmd]
    began = time.monotonic()
    result = subprocess.run(cmd, capture_output=True, text=True,
                            timeout=900)
    wall = time.monotonic() - began
    info = None
    for line in reversed((result.stdout or "").strip().splitlines()):
        try:
            info = json.loads(line)
            break
        except ValueError:
            continue
    return result, wall, info, " ".join(cmd)


def per_pc_map(counts: dict):
    return {row["pc"]: row for row in counts["instructions"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operator", required=True)
    parser.add_argument("--shape", required=True,
                        help="comma-separated, e.g. 128,128,128")
    parser.add_argument("--dtype", required=True)
    parser.add_argument("--threads", type=int, default=1,
                        choices=(1, 2, 4, 8))
    parser.add_argument("--steady-repeats", type=int, default=5)
    parser.add_argument("--seed", type=int, default=30,
                        help="same default as the scan driver")
    parser.add_argument("--out", required=True,
                        help="output directory for this run's evidence")
    args = parser.parse_args()

    load_env()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    shape = parse_shape(args.shape)

    scan = import_scan_driver()
    row = find_row(scan, args.operator, shape, args.dtype)
    case = scan.build_case(row, seed=args.seed)

    import a100_support.native_device as nd  # noqa: E402
    device = nd.make_device()
    device.threads = args.threads
    staged = device.stage_case(case)
    executable = Path(staged.artifact.executable)
    bundle = Path(staged.directory) / "bundle.bin"

    # the staged dir is a slim copy; the manifest lives in the cache entry
    staged_meta = json.loads((executable.parent / "artifact.json").read_text())
    entry = ROOT / "a100c" / "cache" / staged_meta["key"]
    if not entry.is_dir():
        raise SystemExit(f"cache entry missing: {entry}")
    if (entry / "operator_exec").read_bytes() != executable.read_bytes():
        raise SystemExit("staged executable differs from the cache entry; "
                         "refusing the join")

    manifest = Manifest(entry)
    pc_map, region, asm_diag = manifest.build_pc_map(
        executable, out / "asm")
    runtime_regions = Manifest.symbol_regions(executable)

    runs = {}
    problems = []
    for label, repeats in (("r1", 1), ("r2", 1 + args.steady_repeats)):
        counts_path = out / f"counts.{label}.json"
        result, wall, info, command = run_qemu(
            executable, bundle, args.threads, repeats, counts_path)
        entry_run = {"repeats": repeats, "exit_code": result.returncode,
                     "wall_s": round(wall, 3), "command": command,
                     "stdout_last_json": info,
                     "stderr_tail": result.stderr.strip()[-400:]}
        if result.returncode == 0 and counts_path.is_file():
            entry_run["counts"] = json.loads(counts_path.read_text())
        else:
            problems.append(f"{label}: exit {result.returncode}, counts "
                            f"present={counts_path.is_file()}")
        runs[label] = entry_run
    if problems:
        (out / "metrics.json").write_text(json.dumps(
            {"schema": "a100c-matmul-metrics/v1", "case": row["id"],
             "problems": problems, "runs": {k: {kk: vv for kk, vv in v.items()
                                                if kk != "counts"}
                                            for k, v in runs.items()}},
            indent=2) + "\n")
        for problem in problems:
            print(f"PROBLEM: {problem}")
        return 1

    r1, r2 = runs["r1"]["counts"], runs["r2"]["counts"]
    r1_pc, r2_pc = per_pc_map(r1), per_pc_map(r2)
    repeat_delta = args.steady_repeats

    # steady-state per-call profile (loader/pool/bundle init cancels)
    pc_call = {}
    indivisible = 0
    for pc, prow in r2_pc.items():
        before = r1_pc.get(pc, {}).get("executions", 0)
        delta = prow["executions"] - before
        if delta < 0:
            problems.append(f"pc {pc}: repeats=1 run executed MORE than "
                            f"repeats={1 + repeat_delta} (nondeterminism)")
            delta = 0
        if delta % repeat_delta:
            indivisible += 1
        pc_call[pc] = delta / repeat_delta
    total_call = (r2["total_dynamic_instructions"]
                  - r1["total_dynamic_instructions"]) / repeat_delta
    init_total = r1["total_dynamic_instructions"] - total_call

    def categories_of(counts):
        table = {}
        for prow in counts["instructions"]:
            table[prow["category"]] = (table.get(prow["category"], 0)
                                       + prow["executions"])
        return table

    cat_call = {}
    for pc, amount in pc_call.items():
        category = r2_pc[pc]["category"]
        cat_call[category] = cat_call.get(category, 0) + amount

    # program-region attribution (compiler-side origins)
    origin_call, opcode_call = {}, {}
    spill = {"spill_instructions": 0.0, "reload_instructions": 0.0,
             "spill_bytes_model": 0.0, "reload_bytes_model": 0.0,
             "bytes_model_note": "scalar=8B; vector=VLEN/8*lmul at vlmax"}
    for pc, record in pc_map.items():
        amount = pc_call.get(pc, 0.0)
        if amount == 0:
            continue
        origin_call[record["origin"]] = (origin_call.get(record["origin"], 0)
                                         + amount)
        opcode_call[record["opcode"] or "frame"] = (
            opcode_call.get(record["opcode"] or "frame", 0) + amount)
        if record["origin"] in ("spill", "reload"):
            key = ("spill" if record["origin"] == "spill"
                   else "reload") + "_instructions"
            spill[key] += amount
            width = Manifest.instruction_bytes(record["mnemonic"],
                                               record["vtype"])
            if width:
                spill[record["origin"] + "_bytes_model"] += amount * width

    # runtime/loader attribution
    runtime_call, unknown_call = {}, 0.0
    for pc, amount in pc_call.items():
        if pc in pc_map or amount == 0:
            continue
        symbol = Manifest.region_of(pc, runtime_regions)
        if symbol:
            runtime_call[symbol] = runtime_call.get(symbol, 0) + amount
        else:
            unknown_call += amount

    # vsetvli detail: static count by (sew, lmul) + dynamic executions
    vsetvli = {"static": {}, "dynamic_call": 0.0}
    for pc, record in pc_map.items():
        if record["opcode"] == "vsetvli":
            key = f"e{record['vtype'][0]},m{record['vtype'][1]}" \
                if record["vtype"] else "unknown"
            vsetvli["static"][key] = vsetvli["static"].get(key, 0) + 1
            vsetvli["dynamic_call"] += pc_call.get(pc, 0.0)

    hot = sorted(((amount, pc) for pc, amount in pc_call.items()),
                 reverse=True)[:40]
    hot_rows = []
    for amount, pc in hot:
        record = pc_map.get(pc)
        runtime = Manifest.region_of(pc, runtime_regions)
        hot_rows.append({
            "pc": pc, "per_call": round(amount, 3),
            "mnemonic": (r2_pc[pc]["mnemonic"]
                         if pc in r2_pc else "?"),
            "region": "program" if record else (runtime or "loader/unknown"),
            "origin": record["origin"] if record else None,
            "opcode": record["opcode"] if record else None,
            "loc": record["loc"] if record else None,
            "text": record["text"] if record else None,
        })

    emission = manifest.stats.get("emission", {})
    allocation = manifest.stats.get("allocation", {})
    metrics = {
        "schema": "a100c-matmul-metrics/v1",
        "case": row["id"],
        "threads": args.threads,
        "seed": args.seed,
        "steady_repeats": repeat_delta,
        "artifact": {"key": staged_meta["key"],
                     "sha256": staged.artifact_sha256,
                     "identity": manifest.identity,
                     "cache_entry": str(entry)},
        "environment": {
            "qemu": os.environ.get("A100_QEMU"),
            "qemu_version": subprocess.run(
                [os.environ["A100_QEMU"], "--version"],
                capture_output=True, text=True, timeout=60
            ).stdout.splitlines()[0],
            "cpu": os.environ.get("A100_QEMU_CPU"),
            "plugin": str(TOOLING / "full_instruction_counts.so"),
        },
        "asm_join": asm_diag,
        "runs": {label: {"repeats": run["repeats"],
                         "exit_code": run["exit_code"],
                         "wall_s": run["wall_s"],
                         "command": run["command"],
                         "stdout_last_json": run["stdout_last_json"],
                         "total": run["counts"]["total_dynamic_instructions"]
                         if "counts" in run else None,
                         "per_vcpu_totals": run["counts"]
                         ["per_vcpu_totals"] if "counts" in run else None,
                         "categories": categories_of(run["counts"])
                         if "counts" in run else None}
                  for label, run in runs.items()},
        "steady_state": {
            "per_call_total": total_call,
            "init_total": init_total,
            "per_call_categories": cat_call,
            "indivisible_pc_deltas": indivisible,
            "note": "per-call = (repeats=1+R minus repeats=1)/R; "
                    "indivisible deltas indicate run-to-run variation "
                    "(e.g. barrier spin) and are kept as fractions",
        },
        "program_region": {
            "origins_per_call": origin_call,
            "opcodes_per_call": opcode_call,
            "spill_traffic": spill,
            "vsetvli": vsetvli,
            "static": {
                "instructions": len(pc_map),
                "frame_bytes": emission.get("frame_bytes"),
                "saved_regs": emission.get("saved_regs"),
                "spill_slots": emission.get("spill_slots"),
                "spilled_values": allocation.get("spilled_values"),
                "gprs_used": allocation.get("gprs_used"),
                "vector_regs_used": allocation.get("vector_regs_used"),
                "vector_bytes_used": allocation.get("vector_bytes_used"),
            },
        },
        "runtime_region_per_call": runtime_call,
        "loader_unknown_per_call": unknown_call,
        "hot_pcs_per_call": hot_rows,
        "problems": problems,
    }
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps({
        "case": row["id"], "threads": args.threads,
        "per_call_total": total_call,
        "init_total": init_total,
        "categories": {k: round(v, 1) for k, v in
                       sorted(cat_call.items())},
        "top_origins": dict(sorted(origin_call.items(),
                                   key=lambda kv: -kv[1])[:6]),
        "spill": {k: round(v, 1) for k, v in spill.items()
                  if not k.endswith("note")},
        "runtime_top": dict(sorted(runtime_call.items(),
                                   key=lambda kv: -kv[1])[:4]),
    }, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
