#!/usr/bin/env python3
"""Executed semantic checks for layout-aware reduction and matrix lowering.

The references state scalar addition/FMA order independently.  Every case
runs through the production factory, native bundle ABI and generated RISC-V
program.  Switch-off runs exercise the retained paths and artifact identity.
"""
from __future__ import annotations

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


def module(directory, name, text):
    path = directory / (name + ".py")
    path.write_text(
        "OPERATOR={'name':'probe','group':'probe','channel':'local',"
        "'execution':'triton_kernel','verification':'correctness','tags':[]}\n"
        "import triton\nimport triton.language as tl\n" + text +
        "\ndef _make_case(shape=None,dtype='float32',seed=30):\n"
        "    return {'grid':(1,)}\n")
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def execute(case, options, threads):
    staged = NativeExecutableDevice(FactoryCompiler(options=options), threads).stage_case(case)
    command = [os.environ["A100_QEMU"], "-L", os.environ["A100_SYSROOT"],
               "-cpu", os.environ["A100_QEMU_CPU"], str(staged.artifact.executable),
               "--bundle", str(staged.directory / "bundle.bin"),
               "--threads", str(threads), "--repeats", "3"]
    proc = subprocess.run(command, capture_output=True, text=True, timeout=90)
    assert proc.returncode == 0, proc.stderr[-1200:]
    runtime = json.loads(proc.stdout.strip().splitlines()[-1])
    assert runtime["repeats_all_equal"], runtime
    got = staged.outputs()
    verdict = compare_case(case, got)
    assert verdict["status"] == "PASS", verdict
    dump = (Path(staged.artifact.executable).parent / "stage.mir.lowered.txt").read_text()
    return got, dump, Path(staged.artifact.executable).parent.name


def case_for(kernel, args, meta, expected):
    return {"kernel": kernel, "args": args, "meta": meta, "grid": (1,),
            "outputs": ("Y",), "expected": {"Y": expected},
            "comparison": {"Y": {"comparator": "array_equal", "exact": True}}}


def reductions(work, cache):
    mod = module(work, "kept_probe", '''
@triton.jit
def probe(X,Y,B:tl.constexpr,SHAPE:tl.constexpr,AX:tl.constexpr,OUT:tl.constexpr):
    i=tl.arange(0,B)
    x=tl.load(X+i).to(tl.float32)
    x=tl.reshape(x,SHAPE)
    result=tl.sum(x,axis=AX)
    j=tl.arange(0,OUT)
    tl.store(Y+j,tl.reshape(result,(OUT,)))
''')
    shapes = [((2, 4, 16), (1,), True), ((2, 4, 2, 16), (1, 2), True),
              ((2, 4, 16), (0, 2), False), ((2, 4, 1), (1,), False)]
    for shape, axes, eligible in shapes:
        keep = [a for a in range(len(shape)) if a not in axes]
        kept_shape = tuple(shape[a] for a in keep)
        for dtype in (np.float32, np.float16):
            x = ((np.arange(np.prod(shape)) % 19) - 9).astype(dtype).reshape(shape)
            if dtype == np.float32:
                # Cancellation distinguishes sequential sums from regrouping.
                x.flat[::7], x.flat[1::7] = 1e20, -1e20
            expected = np.zeros(kept_shape, np.float32)
            for ks in np.ndindex(kept_shape):
                total = np.float32(0)
                for rs in np.ndindex(tuple(shape[a] for a in axes)):
                    at = [0] * len(shape)
                    for a, v in zip(keep, ks): at[a] = v
                    for a, v in zip(axes, rs): at[a] = v
                    total = np.float32(total + np.float32(x[tuple(at)]))
                expected[ks] = total
            case = case_for(mod.probe, {"X": x, "Y": np.zeros(expected.size, np.float32)},
                            {"B": x.size, "SHAPE": shape, "AX": axes[0] if len(axes) == 1 else axes,
                             "OUT": expected.size}, expected.ravel())
            identities = []
            for on in (False, True):
                got, dump, ident = execute(case, CompileOptions(cache_dir=str(cache),
                                           kept_axis_reduction=on), 8 if on else 1)
                fired = "// kept_axis_reductions: []" not in dump
                assert fired == (on and eligible), (shape, axes, on)
                identities.append(ident)
            assert identities[0] != identities[1]
            print("PASS kept", shape, axes, np.dtype(dtype).name, flush=True)


def neutral_padding(work, cache):
    mod = module(work, "neutral_probe", '''
@triton.jit
def probe(X,Y,n,B:tl.constexpr,GOOD:tl.constexpr):
    i=tl.arange(0,B)
    mask=i<n
    x=tl.load(X+i,mask=mask,other=7.0).to(tl.float32)
    if GOOD:
        x=tl.where(mask,x,0.0)
    total=tl.sum(x,axis=0)
    tl.store(Y+i,total,mask=mask)
''')
    for good in (False, True):
        for n in (0, 1, 17, 97):
            data = (np.arange(128) % 17).astype(np.float32)
            expected = np.zeros(128, np.float32)
            expected[:n] = np.sum(data[:n], dtype=np.float64) + (0 if good else (128-n)*7)
            case = case_for(mod.probe, {"X": data, "Y": np.zeros(128, np.float32), "n": np.int32(n)},
                            {"B": 128, "GOOD": good}, expected)
            for on in (False, True):
                got, dump, _ = execute(case, CompileOptions(cache_dir=str(cache),
                                      neutral_reduction_trim=on), 8 if on else 1)
                fired = "// neutral_reduction_trims: []" not in dump
                # Scalar 1 specializes and can fold the prefix predicate
                # outside this proof's recognized shape.  Declining is
                # legal; non-neutral padding must never be trimmed.
                assert not fired or (on and good), (good, n, on)
                if on and good and n == 97:
                    assert fired
            print("PASS padding", good, n, flush=True)


def matrices(work, cache):
    mod = module(work, "row_probe", '''
@triton.jit
def probe(A,B,Y,M:tl.constexpr,N:tl.constexpr,K:tl.constexpr,CHAIN:tl.constexpr):
    m=tl.arange(0,M)
    n=tl.arange(0,N)
    k=tl.arange(0,K)
    a=tl.load(A+m[:,None]*K+k[None,:])
    b=tl.load(B+k[:,None]*N+n[None,:])
    if CHAIN:
        c=tl.full((M,N),1.0,tl.float32)
        out=tl.dot(a,b,c)
    else:
        out=tl.dot(a,b)
    tl.store(Y+m[:,None]*N+n[None,:],out)
''')
    for m in (1, 2):
        for chain in (False, True):
            a = ((np.arange(m*8) % 7) - 3).astype(np.float32).reshape(m, 8)
            b = ((np.arange(8*32) % 11) - 5).astype(np.float32).reshape(8, 32)
            expected = (a.astype(np.float64) @ b.astype(np.float64) + int(chain)).astype(np.float32)
            case = case_for(mod.probe, {"A": a, "B": b, "Y": np.zeros((m,32), np.float32)},
                            {"M": m, "N": 32, "K": 8, "CHAIN": chain}, expected)
            results = []
            for on in (False, True):
                got, dump, _ = execute(case, CompileOptions(cache_dir=str(cache), matrix_row_reuse=on),
                                      8 if on else 1)
                assert ("'row_block': 2" in dump) == (on and m == 2), (m, chain, on)
                results.append(got["Y"].tobytes())
            assert results[0] == results[1]
            print("PASS matrix", m, chain, flush=True)


def safety_edges(work, cache):
    mod = module(work, "edge_probe", '''
@triton.jit
def probe(X,Y,n,B:tl.constexpr,MODE:tl.constexpr):
    i=tl.arange(0,B)
    mask=i<n
    x=tl.load(X+i,mask=mask,other=7.0)
    x=tl.where(mask,x,0.0)
    if MODE == 2:
        result=tl.argmax(x,axis=0)
    else:
        result=tl.sum(x,axis=0)
        if MODE == 1:
            result=result.to(tl.int32,bitcast=True)
    tl.store(Y+i,result,mask=mask)
''')
    for value in (-0.0, float("inf"), float("-inf"), float("nan")):
        for mode in (0, 1):
            n = 17
            data = np.full(128, value, np.float32)
            total = np.float32(0)
            for x in data[:n]:
                total = np.float32(total + x)
            # RISC-V scalar/vector float operations canonicalize NaNs.
            if np.isnan(total):
                total = np.array([0x7fc00000], np.uint32).view(np.float32)[0]
            dtype = np.int32 if mode else np.float32
            expected = np.zeros(128, dtype)
            expected[:n] = np.asarray(total).view(np.int32) if mode else total
            case = case_for(mod.probe, {"X": data, "Y": np.zeros(128, dtype), "n": np.int32(n)},
                            {"B": 128, "MODE": mode}, expected)
            if mode == 0:
                case["comparison"] = {"Y": {"comparator": "allclose", "exact": False,
                                            "rtol": 0, "atol": 0, "equal_nan": True}}
            results = []
            for on in (False, True):
                got, dump, _ = execute(case, CompileOptions(cache_dir=str(cache),
                                      neutral_reduction_trim=on), 8 if on else 1)
                if mode:
                    assert "// neutral_reduction_trims: []" in dump
                results.append(got["Y"].tobytes())
            assert results[0] == results[1]
            print("PASS edge", value, "bitcast", bool(mode), flush=True)
    # Padding zero is greater than every active value.  It is observable
    # to argmax and must remain in the index reduction domain.
    data = np.full(128, -1, np.float32)
    expected = np.zeros(128, np.int32)
    expected[:17] = 17
    case = case_for(mod.probe, {"X": data, "Y": np.zeros(128, np.int32), "n": np.int32(17)},
                    {"B": 128, "MODE": 2}, expected)
    for on in (False, True):
        _, dump, _ = execute(case, CompileOptions(cache_dir=str(cache), neutral_reduction_trim=on), 8)
        assert "// neutral_reduction_trims: []" in dump
    print("PASS index-padding-observable", flush=True)


def rejection_guards(work, cache):
    mod = module(work, "guard_probe", '''
@triton.jit
def probe(X,Y,n,shift,B:tl.constexpr,VOLATILE:tl.constexpr):
    i=tl.arange(0,B)
    mask=(i+shift)<n
    x=tl.load(X+i,mask=mask,other=7.0,volatile=VOLATILE)
    x=tl.where(mask,x,0.0)
    total=tl.sum(x,axis=0)
    tl.store(Y+i,total,mask=mask)
''')
    for label, n, shift, volatile in (
            ("unsigned-high-bit", np.uint32(0x80000001), np.uint32(0), False),
            ("offset-prefix", np.int32(25), np.int32(8), False),
            ("volatile", np.int32(17), np.int32(0), True)):
        data = ((np.arange(128) % 17) - 8).astype(np.float32)
        active = (np.arange(128, dtype=np.int64) + int(shift)) < int(n)
        total = np.float32(np.sum(data[active], dtype=np.float64))
        expected = np.zeros(128, np.float32)
        expected[active] = total
        case = case_for(mod.probe, {"X": data, "Y": np.zeros(128, np.float32),
                                   "n": n, "shift": shift},
                        {"B": 128, "VOLATILE": volatile}, expected)
        for on in (False, True):
            _, dump, _ = execute(case, CompileOptions(cache_dir=str(cache),
                                 neutral_reduction_trim=on), 8 if on else 1)
            assert "// neutral_reduction_trims: []" in dump
        print("PASS declined", label, flush=True)


def main():
    with tempfile.TemporaryDirectory(prefix="a100-k3-lowering-tests-") as tmp:
        work = Path(tmp)
        cache = work / "cache"
        reductions(work, cache)
        neutral_padding(work, cache)
        matrices(work, cache)
        safety_edges(work, cache)
        rejection_guards(work, cache)
    print("PASS all K3 lowering checks")


if __name__ == "__main__":
    main()
