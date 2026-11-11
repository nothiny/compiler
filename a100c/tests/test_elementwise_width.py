#!/usr/bin/env python3
"""Execute width/tail/alias contracts through the production factory.

All expected values are computed before execution from independent input
snapshots.  Dynamic aliases never enter the artifact identity.  Positive
shift overlap is tested inside one original 32-lane chunk; cross-chunk
forward dependencies in the old lowering are not claimed to be repaired.
"""
import ast
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
sys.path.insert(0, str(ROOT / "ops/harness"))
import numpy as np
from a100c.driver import CompileOptions
from a100c.factory import FactoryCompiler
from a100_support.native_device import NativeExecutableDevice
from opslib.compare import compare_case


def execute(case, compiler, threads):
    staged = NativeExecutableDevice(compiler, threads).stage_case(case)
    result = subprocess.run([
        os.environ["A100_QEMU"], "-L", os.environ["A100_SYSROOT"], "-cpu", os.environ["A100_QEMU_CPU"],
        str(staged.artifact.executable), "--bundle", str(staged.directory / "bundle.bin"),
        "--threads", str(threads), "--repeats", "3"], capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stderr[-1000:]
    runtime = json.loads(result.stdout.strip().splitlines()[-1])
    assert runtime["repeats_all_equal"]
    got = staged.outputs()
    verdict = compare_case(case, got)
    assert verdict["status"] == "PASS", verdict
    dump = (Path(staged.artifact.executable).parent / "stage.mir.lowered.txt").read_text()
    line = next(s for s in dump.splitlines() if s.startswith("// elementwise_width:"))
    report = ast.literal_eval(line.partition(":")[2].strip())
    return got, Path(staged.artifact.executable).parent.name, report


def probe(work):
    path = work / "width_probe.py"
    path.write_text('''OPERATOR={'name':'width_probe','group':'probe','channel':'local','execution':'triton_kernel','verification':'correctness','tags':[]}
import triton
import triton.language as tl
@triton.jit
def kernel(X,Y,n,B:tl.constexpr,FORM:tl.constexpr):
    i=tl.arange(0,B)
    mask=i<n
    x=tl.load(X+i,mask=mask,other=0)
    if FORM == 0:
        out=x*1.25+2.0
    elif FORM == 1:
        out=x.to(tl.int32,bitcast=True)
    else:
        out=x*7+11
    tl.store(Y+i,out,mask=mask)
def _make_case(shape=None,dtype='float32',seed=30):
    return {'grid':(1,)}
''')
    spec = importlib.util.spec_from_file_location("width_probe", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.kernel


def make_case(kernel, x, y, n, form):
    before = x.copy()
    expected = y.copy()
    with np.errstate(invalid="ignore", over="ignore"):
        if form == 0:
            expected[:n] = np.float32(np.float32(before[:n]*np.float32(1.25)) + np.float32(2))
        elif form == 1:
            expected[:n] = before[:n].view(np.int32)
        else:
            expected[:n] = (before[:n].astype(np.int64)*7 + 11).astype(np.int32)
    policy = {"comparator": "array_equal", "exact": True} if form else \
             {"comparator": "allclose", "exact": False, "rtol": 0, "atol": 0, "equal_nan": True}
    return {"kernel": kernel, "args": {"X": x, "Y": y, "n": np.int32(n)},
            "meta": {"B": 512, "FORM": form}, "grid": (1,), "outputs": ("Y",),
            "expected": {"Y": expected}, "comparison": {"Y": policy}}


def tails_and_bits(work):
    kernel = probe(work)
    compilers = {on: FactoryCompiler(options=CompileOptions(
        cache_dir=str(work / "cache"), elementwise_width=on, guarded_narrow_access=False))
        for on in (False, True)}
    for form in (0, 1, 2):
        for n in (0, 1, 17, 97, 257):
            if form == 2:
                x = np.resize(np.array([0, -1, 0x7fffffff, -0x80000000, 1234567], np.int32), 512)
            else:
                x = np.resize(np.array([0, 0x80000000, 0x3f800000, 0xbf800000,
                                      0x7f800000, 0xff800000, 0x7fc12345, 1], np.uint32), 512).view(np.float32)
            y = np.full(512, -123, np.int32 if form else np.float32)
            case = make_case(kernel, x, y, n, form)
            results = []
            for on in (False, True):
                got, key, report = execute(case, compilers[on], 8 if on else 1)
                results.append(got["Y"].tobytes())
                if on and n not in (0, 1):
                    assert report["factor"] > 1, report
                if not on:
                    assert report["factor"] == 1
            assert results[0] == results[1]
            print("PASS width edge", form, n, flush=True)


def aliases(work):
    kernel = probe(work)
    compilers = {on: FactoryCompiler(options=CompileOptions(
        cache_dir=str(work / "alias-cache"), elementwise_width=on, guarded_narrow_access=False))
        for on in (False, True)}
    keys = {False: set(), True: set()}
    for label, n in (("disjoint", 97), ("in-place", 97), ("positive-shift", 17), ("negative-shift", 97)):
        base = (np.arange(1024, dtype=np.float32) - 512) / np.float32(16)
        if label == "disjoint":
            x, y = base[:512].copy(), base[512:].copy()
        elif label == "in-place":
            x = y = base[:512]
        elif label == "positive-shift":
            x, y = base[:512], base[1:513]
        else:
            x, y = base[1:513], base[:512]
        case = make_case(kernel, x, y, n, 0)
        results = []
        for on in (False, True):
            got, key, report = execute(case, compilers[on], 1)
            keys[on].add(key)
            results.append(got["Y"].tobytes())
            if on:
                assert report["runtime_storage_pairs"], report
        assert results[0] == results[1]
        print("PASS alias", label, n, flush=True)
    assert len(keys[True]) == len(keys[False]) == 1, keys
    print("PASS same artifact for runtime aliases", flush=True)


def size_reuse(work):
    spec = importlib.util.spec_from_file_location("width_scan", ROOT / "tools/run_scan.py")
    scan = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scan)
    row = next(iter(scan.enumerated_rows(str(ROOT / "ops/suite/manifest.json"), None, ["suite/perf/gelu.py"])))
    keys = {False: [], True: []}
    results = {False: [], True: []}
    for on in (False, True):
        compiler = FactoryCompiler(options=CompileOptions(cache_dir=str(work / "reuse-cache"),
                                   elementwise_width=on, guarded_narrow_access=False))
        for n in (128, 262144, 128):
            case = scan.build_case(dict(row, shape=[n], dtype="float32"), seed=30, use_golden=False)
            got, key, report = execute(case, compiler, 8 if on else 1)
            keys[on].append(key)
            results[on].append(got[case["outputs"][0]].tobytes())
            if on:
                assert report["factor"] == 2, report
                assert report["attempts"][0]["factor"] == 4 and report["attempts"][0]["status"] == "declined"
            print("PASS GELU size reuse", on, n, flush=True)
        assert compiler.compile_count == 1 and compiler.cache_hits == 2
    assert len(set(keys[True])) == len(set(keys[False])) == 1 and keys[True][0] != keys[False][0]
    assert results[True] == results[False]


def main():
    with tempfile.TemporaryDirectory(prefix="a100-width-contract-") as tmp:
        work = Path(tmp)
        tails_and_bits(work)
        aliases(work)
        size_reuse(work)
    print("PASS 44 native width checks, including same-ELF runtime aliases and N reuse")


if __name__ == "__main__":
    main()
