#!/usr/bin/env python3
"""Phase-A validation of tools/profiling/full_instruction_counts.so.

Builds the plugin, assembles analytically-known freestanding RISC-V
programs with the declared cross toolchain, runs them under the declared
QEMU with the plugin, and asserts the guest dynamic instruction counts
match hand-computed expectations EXACTLY (per category, per pc and per
vcpu).  Raw evidence is written under
docs/compiler-agent/optimizations/matmul/tooling/phase-a/.

The judge quantity of the round is guest dynamic instruction executions
(per-insn exec callbacks); this script is the counting-calibration the
round's methodology requires.  Static listings (objdump) are used only as
a cross-check that the hand-computed tables describe the actual binary.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLING = ROOT / "tools" / "profiling"
EVID = ROOT / "docs/compiler-agent/optimizations/matmul/tooling/phase-a"

ALL_CATEGORIES = ["ime", "vec-config", "vec-mem", "vec-arith",
                  "scalar-load", "scalar-store", "atomic",
                  "scalar-arith", "branch", "system"]

# hand-computed expectations (see the .S files; one machine instruction
# per source line, verified against the objdump listing at run time)
EXPECT = {
    "straight": {
        "total": 12,
        "static": 12,
        "categories": {"scalar-arith": 6, "scalar-load": 1,
                       "scalar-store": 1, "vec-config": 1,
                       "vec-arith": 1, "branch": 1, "system": 1},
        "per_pc": "all-once",
    },
    "loop": {
        "total": 8006,               # 4*1 + 8*1000 + 2*1
        "static": 14,
        "categories": {"scalar-arith": 3005,     # 4 + 3*1000 + 1
                       "scalar-load": 1000,
                       "scalar-store": 1000,
                       "vec-config": 1000,
                       "vec-arith": 1000,
                       "branch": 1000,
                       "system": 1},
        "per_pc": {1000: 8, 1: 6},   # value: number of pcs
    },
    "vendor": {
        "total": 14,
        "static": 14,
        "categories": {"scalar-arith": 5, "vec-config": 3,
                       "vec-arith": 1, "vec-mem": 3,
                       "ime": 1, "system": 1},
        "per_pc": "all-once",
    },
}


def load_env():
    for line in (ROOT / ".env").read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ[key.strip()] = value.strip()


def sh(cmd, timeout=180, check=True):
    result = subprocess.run([str(c) for c in cmd], capture_output=True,
                            text=True, timeout=timeout)
    if check and result.returncode:
        sys.exit(f"command failed ({result.returncode}): "
                 f"{' '.join(str(c) for c in cmd)}\n"
                 f"{result.stdout}\n{result.stderr}")
    return result


def build_plugin():
    sh(["bash", str(TOOLING / "build_plugin.sh")])


def asm_program(name):
    prefix = os.environ["A100_CROSS_PREFIX"]
    obj = EVID / f"{name}.o"
    exe = EVID / name
    # the same march the project's own native build uses (a100c/runtime/
    # build.py ASFLAGS); the default assembler ISA has no V extension
    sh([f"{prefix}as", "-march=rv64gcv",
        str(TOOLING / "validate" / f"{name}.S"), "-o", str(obj)])
    sh([f"{prefix}ld", str(obj), "-o", str(exe)])
    return exe


def objdump_pcs(exe):
    prefix = os.environ["A100_CROSS_PREFIX"]
    result = sh([f"{prefix}objdump", "-d", "--no-show-raw-insn", str(exe)])
    pcs = []
    for line in result.stdout.splitlines():
        match = re.match(r"^\s*([0-9a-f]+):\s+(\S+)", line)
        if match:
            pcs.append((int(match.group(1), 16), match.group(2)))
    return pcs


def run_qemu(exe, out_json):
    cmd = [os.environ["A100_QEMU"], "-L", os.environ["A100_SYSROOT"],
           "-cpu", os.environ.get("A100_QEMU_CPU",
                                  "max,vlen=1024,elen=64,vext_spec=v1.0"),
           "-plugin", f"{TOOLING / 'full_instruction_counts.so'},"
                      f"out={out_json}",
           str(exe)]
    return sh(cmd, timeout=120, check=False), " ".join(cmd)


def normalize(categories):
    base = {name: 0 for name in ALL_CATEGORIES}
    base.update(categories)
    return base


def check_program(name, exe, listing, evidence):
    expect = EXPECT[name]
    problems = []
    runs = []
    command = None
    for attempt in (1, 2):  # determinism: two identical runs
        out_json = EVID / f"{name}.counts{attempt}.json"
        result, command = run_qemu(exe, out_json)
        runs.append({"attempt": attempt,
                     "returncode": result.returncode,
                     "stderr_tail": result.stderr.strip()[-400:],
                     "stdout_tail": result.stdout.strip()[-400:]})
        if result.returncode != 0 or not out_json.is_file():
            problems.append(f"run {attempt}: exit {result.returncode}, "
                            f"counts file present={out_json.is_file()}")
            evidence[name] = {"runs": runs, "command": command,
                              "problems": problems, "verdict": "FAIL"}
            return problems
        runs[-1]["counts"] = json.loads(out_json.read_text())
    first, second = runs[0]["counts"], runs[1]["counts"]
    if first != second:
        problems.append("determinism: the two runs' counts JSON differ")

    static_pcs = {pc for pc, _ in listing}
    if len(listing) != expect["static"]:
        problems.append(f"objdump static count {len(listing)} != "
                        f"hand count {expect['static']} (listing: "
                        f"{listing})")
    rows = first["instructions"]
    executed_pcs = {row["pc"] for row in rows}
    if executed_pcs != static_pcs:
        problems.append(f"executed pc set != static pc set "
                        f"(missing={sorted(static_pcs - executed_pcs)}, "
                        f"extra={sorted(executed_pcs - static_pcs)})")

    actual_total = first["total_dynamic_instructions"]
    if actual_total != expect["total"]:
        problems.append(f"total {actual_total} != expected "
                        f"{expect['total']}")
    sum_rows = sum(row["executions"] for row in rows)
    if sum_rows != actual_total:
        problems.append(f"sum of rows {sum_rows} != stated total "
                        f"{actual_total}")
    vcpu = first["per_vcpu_totals"]
    if vcpu[0] != actual_total or any(vcpu[1:]):
        problems.append(f"per-vcpu totals {vcpu} do not concentrate on "
                        f"vcpu 0 for a single-threaded program")

    actual_cat = {}
    for row in rows:
        actual_cat[row["category"]] = (actual_cat.get(row["category"], 0)
                                       + row["executions"])
    actual_cat = normalize(actual_cat)
    wanted_cat = normalize(expect["categories"])
    if actual_cat != wanted_cat:
        problems.append(f"categories {actual_cat} != expected "
                        f"{wanted_cat}")

    per_pc = {row["pc"]: row["executions"] for row in rows}
    if expect["per_pc"] == "all-once":
        if any(count != 1 for count in per_pc.values()):
            problems.append(f"not every pc executed exactly once: "
                            f"{sorted(per_pc.items())}")
    else:
        wanted = expect["per_pc"]
        actual = {}
        for count in per_pc.values():
            actual[count] = actual.get(count, 0) + 1
        if actual != wanted:
            problems.append(f"per-pc count multiset {actual} != expected "
                            f"{wanted}")
    for row in rows:
        if row["size"] not in (2, 4):
            problems.append(f"pc {row['pc']}: odd size {row['size']}")

    if name == "vendor":
        ime_rows = [row for row in rows if row["category"] == "ime"]
        if not ime_rows or ime_rows[0]["mnemonic"] != "smt.vmadot" or \
                ime_rows[0]["format"] != "i8" or \
                ime_rows[0]["executions"] != 1:
            problems.append(f"vendor decode row unexpected: {ime_rows}")

    evidence[name] = {
        "command": command,
        "runs": [{k: v for k, v in run.items() if k != "counts"}
                 for run in runs],
        "static_listing": [[pc, mn] for pc, mn in listing],
        "actual_total": actual_total,
        "actual_categories": actual_cat,
        "expected_total": expect["total"],
        "expected_categories": wanted_cat,
        "problems": problems,
        "verdict": "PASS" if not problems else "FAIL",
    }
    return problems


def main():
    EVID.mkdir(parents=True, exist_ok=True)
    load_env()
    build_plugin()
    evidence = {
        "schema": "a100c-profiling-phase-a-validation/v1",
        "qemu": os.environ.get("A100_QEMU"),
        "qemu_version": sh([os.environ["A100_QEMU"], "--version"],
                           timeout=60).stdout.splitlines()[0],
        "cross_prefix": os.environ.get("A100_CROSS_PREFIX"),
        "cpu": os.environ.get("A100_QEMU_CPU"),
        "note": "counts are guest dynamic instruction executions "
                "(per-insn exec callbacks); expectations hand-computed "
                "from the sources and cross-checked against objdump",
    }
    all_problems = []
    for name in ("straight", "loop", "vendor"):
        exe = asm_program(name)
        listing = objdump_pcs(exe)
        problems = check_program(name, exe, listing, evidence)
        all_problems.extend(f"{name}: {p}" for p in problems)
        print(f"[{name}] "
              f"{'PASS' if not problems else 'FAIL'} "
              f"(static={len(listing)})")
        for problem in problems:
            print(f"    - {problem}")
    evidence["verdict"] = "PASS" if not all_problems else "FAIL"
    (EVID / "validation.json").write_text(
        json.dumps(evidence, indent=2) + "\n")
    print(f"evidence -> {EVID / 'validation.json'}")
    return 0 if not all_problems else 1


if __name__ == "__main__":
    sys.exit(main())
