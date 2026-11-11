#!/usr/bin/env python3
"""Pair original-case checks with stable native-program PC instruction counts.

The program assembly is independently reassembled and byte-checked against
the shipped ELF.  Only its non-PIE PC interval is differenced; ASLR library
PCs and MIR operation ordinals never enter the metric.  Two independent
repeats-1/repeats-3 pairs must agree exactly.  Raw bundles/counts stay in a
fresh /tmp directory, with paths and SHA256s retained in the JSON evidence.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument("--project", required=True)
parser.add_argument("--operator", required=True)
parser.add_argument("--shape", required=True)
parser.add_argument("--dtype", required=True)
parser.add_argument("--threads", type=int, default=1)
parser.add_argument("--off", action="store_true")
parser.add_argument("--out", required=True)
args = parser.parse_args()
root = Path(args.project).resolve()
for line in (root / ".env").read_text().splitlines():
    key, sep, value = line.partition("=")
    if sep and not key.startswith("#"):
        os.environ[key] = value
os.environ.update(PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
sys.path[:0] = [str(root), str(root / "ops/harness")]
spec = importlib.util.spec_from_file_location("k3_scan", root / "tools/run_scan.py")
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)
from a100c.driver import CompileOptions, compiler_revision
from a100c.factory import FactoryCompiler
from a100_support.native_device import NativeExecutableDevice
from a100_support.native_io import unpack_outputs
from opslib.compare import compare_case

out = Path(args.out).resolve()
out.mkdir(parents=True, exist_ok=True)
raw = Path(tempfile.mkdtemp(prefix="a100-k3-pc-profile-"))
shape = [int(x) for x in args.shape.split(",")]
rows = list(scan.enumerated_rows(str(root / "ops/suite/manifest.json"), None, [args.operator]))
row = next(r for r in rows if r["dtype"] == args.dtype)
row = dict(row, shape=shape)
case = scan.build_case(row, seed=30, use_golden=any(r["shape"] == shape and r["dtype"] == args.dtype for r in rows))
fields = {"cache_dir": str(root / "metric-cache")}
for field in ("kept_axis_reduction", "neutral_reduction_trim", "matrix_row_reuse"):
    if field in CompileOptions.__dataclass_fields__:
        fields[field] = not args.off
options = CompileOptions(**fields)
compiler = FactoryCompiler(options=options)
revision = compiler_revision()
staged = NativeExecutableDevice(compiler, args.threads).stage_case(case)
assert compiler_revision() == revision, "source changed while compiling; freeze it first"
executable = Path(staged.artifact.executable)
entry = executable.parent
shutil.copytree(staged.directory, raw / "pristine")
shutil.copy2(entry / "program.S", out / "program.S")
prefix = os.environ["A100_CROSS_PREFIX"]
subprocess.run([prefix + "as", "-march=rv64gcv", "-o", str(raw / "program.o"), str(entry / "program.S")], check=True)
for source, dest in ((raw / "program.o", raw / "object.text"), (executable, raw / "executable.text")):
    subprocess.run([prefix + "objcopy", "--only-section=.text", "-O", "binary", str(source), str(dest)], check=True)
nm = subprocess.check_output([prefix + "nm", "-S", "--defined-only", str(executable)], text=True)
symbols = {}
for line in nm.splitlines():
    parts = line.split()
    if len(parts) == 4:
        symbols[parts[3]] = (int(parts[0], 16), int(parts[1], 16))
start = symbols["operator_workspace_private"][0]
end = sum(symbols["operator_entry"])
sections = subprocess.check_output([prefix + "objdump", "-h", str(executable)], text=True)
text_base = next(int(line.split()[3], 16) for line in sections.splitlines()
                 if len(line.split()) > 3 and line.split()[1] == ".text")
object_bytes = (raw / "object.text").read_bytes()
elf_bytes = (raw / "executable.text").read_bytes()
assert elf_bytes[start-text_base:end-text_base] == object_bytes, "assembly/ELF bytes disagree"
plugin = root / "tools/profiling/full_instruction_counts.so"
assert plugin.exists()
evidence = {"project": str(root), "revision": revision, "mode": "off" if args.off else "on",
            "operator": args.operator, "shape": shape, "dtype": args.dtype, "threads": args.threads,
            "original_case_shape": any(r["shape"] == shape for r in rows),
            "options": options.identity_part(), "artifact_sha256": sha(executable),
            "artifact_key": entry.name, "assembly_sha256": sha(entry / "program.S"),
            "program_pc_interval": [start, end], "assembly_bytes_verified": True,
            "plugin_sha256": sha(plugin), "raw_directory": str(raw), "runs": [], "pairs": [],
            "unit": "guest program instructions per complete native launch, all workers summed"}
for pair in range(2):
    maps = []
    for repeats in (1, 3):
        directory = raw / f"pair-{pair}-r{repeats}"
        shutil.copytree(raw / "pristine", directory)
        counts = directory / "counts.json"
        command = [os.environ["A100_QEMU"], "-L", os.environ["A100_SYSROOT"], "-cpu", os.environ["A100_QEMU_CPU"],
                   "-plugin", f"{plugin},out={counts}", str(executable), "--bundle", str(directory / "bundle.bin"),
                   "--threads", str(args.threads), "--repeats", str(repeats)]
        proc = subprocess.run(command, capture_output=True, text=True, timeout=240)
        (directory / "stdout.log").write_text(proc.stdout)
        (directory / "stderr.log").write_text(proc.stderr)
        assert proc.returncode == 0, proc.stderr[-1000:]
        runtime = json.loads(proc.stdout.strip().splitlines()[-1])
        assert runtime["repeats_all_equal"]
        verdict = compare_case(case, unpack_outputs(directory))
        assert verdict["status"] == "PASS", verdict
        data = json.loads(counts.read_text())
        current = {int(r["pc"]): int(r["executions"]) for r in data["instructions"] if start <= int(r["pc"]) < end}
        maps.append(current)
        evidence["runs"].append({"pair": pair, "repeats": repeats, "command": command,
                                  "comparison": verdict, "runtime": runtime,
                                  "counts_path": str(counts), "counts_sha256": sha(counts)})
    deltas = {pc: maps[1].get(pc, 0) - maps[0].get(pc, 0) for pc in maps[0].keys() | maps[1].keys()}
    assert all(v >= 0 and v % 2 == 0 for v in deltas.values()), "unstable program PC differences"
    evidence["pairs"].append(sum(deltas.values()) // 2)
assert evidence["pairs"][0] == evidence["pairs"][1], "repeat pairs disagree"
evidence["instructions_per_launch"] = evidence["pairs"][0]
assert compiler_revision() == revision, "source changed during run"
(out / "profile.json").write_text(json.dumps(evidence, indent=2) + "\n")
print(json.dumps({k: evidence[k] for k in ("mode", "operator", "shape", "dtype", "threads", "instructions_per_launch")}))
