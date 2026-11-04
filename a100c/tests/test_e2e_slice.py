#!/usr/bin/env python3
"""test_e2e_slice.py -- the end-to-end vertical slice (T007, gate G4).

One small elementwise operator (absolute_kernel, suite/dev) compiled,
built, executed on the declared QEMU endpoint through the a100_support
native device protocol (the factory shim) and independently compared
against the case's expected outputs with the case's own comparison policy:

  acceptance[0] the declared case kinds -- aligned extent (128), ragged
                tails not a multiple of the block extent (97, 17), the
                size-one edge (1) -- at threads 1/2/4/8 on ONE artifact
                per compile identity (identical sha256 across thread
                counts; the program computes its partition from
                --threads);
  acceptance[1] two cases of one compile identity compile once (the
                second is a cache lookup); the artifact is an ELF64
                little-endian RISC-V executable that runs without Python;
  acceptance[2] per-stage dumps with source attribution; identical inputs
                reproduce identical artifact bytes.

Run: python3 a100c/tests/test_e2e_slice.py   (exit 0 = all checks PASS)
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
import warnings  # noqa: E402

warnings.filterwarnings("ignore")

FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(name)
    return ok


import importlib.util  # noqa: E402
import numpy as np  # noqa: E402

SLICE = ROOT / "ops" / "suite" / "dev" / "absolute_kernel.py"
CACHE = Path(tempfile.mkdtemp(prefix="a100c-e2e-"))

# the factory shim: a100_support.native_device.make_device() reads
# A100_COMPILER_FACTORY (F047: it refuses until the factory is set)
os.environ["A100_COMPILER_FACTORY"] = "a100c.driver:make_compiler"

import a100_support.native_device as nd  # noqa: E402
from a100c.driver import Compiler, CompileOptions  # noqa: E402


def load_module():
    spec = importlib.util.spec_from_file_location("slice_operator", SLICE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compare(case, outputs) -> tuple:
    for name, policy in case["comparison"].items():
        got = np.asarray(outputs[name])
        expected = np.asarray(case["expected"][name])
        if policy.get("exact") or policy["comparator"] == "array_equal":
            if not np.array_equal(got, expected):
                return False, f"{name}: array_equal failed"
        else:
            if not np.allclose(got, expected, rtol=policy.get("rtol", 0.0),
                               atol=policy.get("atol", 0.0),
                               equal_nan=policy.get("equal_nan", False)):
                return False, f"{name}: allclose failed (max err " \
                              f"{np.max(np.abs(got - expected))})"
    return True, "compares PASS under the case policy"


def run_json(staged, threads) -> dict:
    subs = {"bundle": str(staged.directory / "bundle.bin"),
            "threads": str(threads)}
    args = [p.format(**subs) for p in staged.artifact.arguments]
    result = subprocess.run(
        [str(ROOT / "a100_support" / "run-riscv.sh"),
         str(staged.artifact.executable), *args],
        capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise RuntimeError(f"native process exit {result.returncode}: "
                           f"{result.stderr[-300:]}")
    return json.loads(result.stdout.strip().splitlines()[-1])


def check_matrix(module):
    operator = module
    compiler = Compiler(options=CompileOptions(cache_dir=str(CACHE)))
    shas = {}
    all_ok = True
    for shape in ((128,), (97,), (17,), (1,)):
        for threads in (1, 2, 4, 8):
            case = operator.make_case(shape=shape)
            device = nd.NativeExecutableDevice(compiler, threads)
            staged = device.stage_case(case)
            staged.launch()
            ok, why = compare(case, staged.outputs())
            all_ok &= ok
            shas.setdefault(shape, set()).add(staged.artifact_sha256)
            if not ok:
                print(f"   shape={shape} threads={threads}: {why}")
    check("declared-cases-pass-at-1-2-4-8-threads", all_ok)
    check("one-artifact-per-identity-across-thread-counts",
          all(len(s) == 1 for s in shas.values()),
          str({k: len(v) for k, v in shas.items()}))


def check_worker_distribution(module):
    """The program computes its partition from --threads: the per-worker
    item counts match the strided model and sum to n."""
    from a100c.plan.partition import strided_range
    compiler = Compiler(options=CompileOptions(cache_dir=str(CACHE)))
    case = module.make_case(shape=(4097,))
    ok = True
    for threads in (1, 2, 4, 8):
        device = nd.NativeExecutableDevice(compiler, threads)
        staged = device.stage_case(case)
        info = run_json(staged, threads)
        items = [w["items"] for w in info["workers"]]
        if sum(items) != 4097 or len(items) != threads \
                or info["pool_initializations"] != 1:
            ok = False
        # the strided model: worker w owns ceil-range programs; the item
        # count is the sum of active elements of the owned programs
        n, block = 4097, 128
        programs = (n + block - 1) // block
        for w in range(threads):
            owned = strided_range(w, threads, programs)
            expect = sum(min(block, max(0, n - p * block)) for p in owned)
            if items[w] != expect:
                ok = False
    check("partition-matches-strided-model-and-covers-all-work", ok)


def check_compile_once(module):
    """acceptance[1]: two cases of one compile identity compile once."""
    fresh = Path(tempfile.mkdtemp(prefix="a100c-e2e-identity-"))
    compiler = Compiler(options=CompileOptions(cache_dir=str(fresh)))
    first = compiler.compile_case(module.make_case(shape=(97,)))
    second = compiler.compile_case(module.make_case(shape=(4097,)))
    check("two-cases-one-identity-compile-once",
          compiler.compile_count == 1 and compiler.cache_hits == 1
          and second.cache_hit and first.sha256 == second.sha256,
          f"compiles={compiler.compile_count} hits={compiler.cache_hits}")
    elf = Path(first.executable).read_bytes()
    check("artifact-is-elf64-little-riscv",
          elf[:6] == b"\x7fELF\x02\x01" and elf[18:20] == b"\xf3\x00")
    # the artifact runs under the declared QEMU endpoint without Python
    # (the guest process is the ELF itself; run-riscv.sh execs QEMU only)
    case = module.make_case(shape=(97,))
    device = nd.NativeExecutableDevice(compiler, 1)
    staged = device.stage_case(case)
    staged.launch()
    ok, why = compare(case, staged.outputs())
    check("artifact-runs-without-python", ok, why)
    shutil.rmtree(fresh, ignore_errors=True)


def check_dumps_and_determinism(module):
    fresh = Path(tempfile.mkdtemp(prefix="a100c-e2e-det-"))
    compiler = Compiler(options=CompileOptions(cache_dir=str(fresh)))
    art = compiler.compile_case(module.make_case(shape=(97,)))
    entry = Path(art.executable).parent
    dumps = sorted(p.name for p in entry.iterdir())
    expected = ["artifact.json", "operator_exec", "program.S",
                "stage.mir.allocated.txt", "stage.mir.legalized.txt",
                "stage.mir.lowered.txt", "stage.plan.txt",
                "stage.selection.txt", "stage.tir.txt"]
    check("per-stage-dumps-produced",
          all(name in dumps for name in expected), str(dumps))
    tir_text = (entry / "stage.tir.txt").read_text()
    mir_text = (entry / "stage.mir.lowered.txt").read_text()
    asm_text = (entry / "program.S").read_text()
    check("dumps-carry-source-attribution",
          "absolute_kernel.py:" in tir_text
          and "absolute_kernel.py:" in mir_text
          and "[op" in asm_text and "absolute_kernel.py:" in asm_text)
    # determinism: a second fresh cache produces identical artifact bytes
    fresh2 = Path(tempfile.mkdtemp(prefix="a100c-e2e-det2-"))
    compiler2 = Compiler(options=CompileOptions(cache_dir=str(fresh2)))
    art2 = compiler2.compile_case(module.make_case(shape=(97,)))
    check("same-input-reproduces-identical-artifact-bytes",
          art.sha256 == art2.sha256, f"{art.sha256[:12]} vs {art2.sha256[:12]}")
    shutil.rmtree(fresh, ignore_errors=True)
    shutil.rmtree(fresh2, ignore_errors=True)


def check_factory_route(module):
    """The a100_support factory shim constructs the native device."""
    os.environ["A100_COMPUTE_THREADS"] = "2"
    device = nd.make_device()
    check("factory-shim-constructs-native-device",
          device.name == "a100-native-executable-qemu"
          and device.threads == 2)
    case = module.make_case(shape=(97,))
    staged = device.stage_case(case)
    staged.launch()
    ok, why = compare(case, staged.outputs())
    check("factory-route-executes-and-compares", ok, why)


def main() -> int:
    try:
        module = load_module()
        check_matrix(module)
        check_worker_distribution(module)
        check_compile_once(module)
        check_dumps_and_determinism(module)
        check_factory_route(module)
    finally:
        shutil.rmtree(CACHE, ignore_errors=True)
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_e2e_slice: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
