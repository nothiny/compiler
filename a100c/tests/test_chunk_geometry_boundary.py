#!/usr/bin/env python3
"""Regress chunk VL changes with original varlen-attention cases.

An extent-one scalar segment can open a chunk before the next pass picks
its own VL.  All six original shape/dtype cases must produce their original
reference outputs at 1/2/4/8 workers, with repeated native execution.
"""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap
ROOT = _bootstrap.bootstrap()
spec = importlib.util.spec_from_file_location("geometry_scan", ROOT / "tools/run_scan.py")
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)
from a100c.driver import CompileOptions
from a100c.factory import FactoryCompiler
from a100_support.native_device import NativeExecutableDevice
from opslib.compare import compare_case


def main():
    with tempfile.TemporaryDirectory(prefix="a100-chunk-geometry-") as tmp:
        compiler = FactoryCompiler(options=CompileOptions(cache_dir=tmp))
        rows = list(scan.enumerated_rows(str(ROOT / "ops/suite/manifest.json"), None,
                    ["suite/dev/naive_attn_decoding_kernel.py"]))
        assert len(rows) == 6
        for row in rows:
            case = scan.build_case(row, seed=30)
            for threads in (1, 2, 4, 8):
                staged = NativeExecutableDevice(compiler, threads).stage_case(case)
                proc = subprocess.run([
                    os.environ["A100_QEMU"], "-L", os.environ["A100_SYSROOT"],
                    "-cpu", os.environ["A100_QEMU_CPU"], str(staged.artifact.executable),
                    "--bundle", str(staged.directory / "bundle.bin"),
                    "--threads", str(threads), "--repeats", "3"],
                    capture_output=True, text=True, timeout=90)
                assert proc.returncode == 0, proc.stderr[-1200:]
                runtime = json.loads(proc.stdout.strip().splitlines()[-1])
                assert runtime["repeats_all_equal"]
                verdict = compare_case(case, staged.outputs())
                assert verdict["status"] == "PASS", (row["id"], threads, verdict)
                print("PASS", row["id"], "threads", threads, "repeats", 3, flush=True)
    print("PASS 24 chunk-geometry comparisons")


if __name__ == "__main__":
    main()
