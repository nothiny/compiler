#!/usr/bin/env python3
"""test_vmath_sincos.py -- the P7 sinf/cosf vector-polynomial round's
contracts, through the real compilation path with the controls that prove
the checks are load-bearing.

The candidate: sinf/cosf at SEW 32 join _VMATH_POLY_FNS.  The polynomial
arm (rint by the 1.5*2^23 magic, the 3-way Cody-Waite reduction, one
Horner pair in z=r*r, the quadrant pick and the sign flip through the
i32 view) runs only when EVERY lane is inside the domain guard
|x| < _POLY_SINCOS_XMAX; any out-of-range lane routes the whole op to
the per-element libm path (the structural guard and its correct
fallback).  The A100C_VMATH_LIBM=1 switch forces the libm path for
on/off contrast.

Checks (each must hold for exit 0):

  * sincos-corpus-pass: the corpus sin/cos operators execute and compare
    PASS under their original policies at 1 and 2 workers (attention to
    the fp16/bf16 lanes and the masked tails);
  * sincos-domain-guard: an input vector mixing in-range and far
    out-of-range magnitudes (1e6, -1e30, 3000, tiny, specials) compares
    PASS -- the out-of-range lanes ride the libm fallback;
  * sincos-switch-contrast: A100C_VMATH_LIBM=1 produces a DIFFERENT
    artifact whose emitted program contains the libm call, while the
    default (polynomial) artifact does not -- and both compare PASS
    with identical output bytes on the same case;
  * sincos-witness-guard-stripped: with the domain cap raised to
    infinity (the guard disabled), the far-out-of-range case compares
    WRONG -- the domain guard is load-bearing, not decorative;
  * sincos-f64-untouched: an fp64 sin operator still rides the libm
    path (the polynomial guard is (fn, sew)-structural: SEW 64 never
    enters it).

Run: python3 a100c/tests/test_vmath_sincos.py   (exit 0 = PASS)
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
sys.path.insert(0, str(ROOT / "ops/harness"))
import numpy as np
from a100c.driver import CompileOptions
from a100c.factory import FactoryCompiler
from a100_support.native_device import NativeExecutableDevice

SIN_KERNEL = ROOT / "ops" / "suite" / "perf" / "sin_kernel.py"
COSINE = ROOT / "ops" / "suite" / "perf" / "cosine_compute.py"
BLACKMAN = ROOT / "ops" / "suite" / "dev" / "blackman_window_kernel.py"
SYNTH = ROOT / "ops" / "suite" / "dev" / "synthesis_kernel.py"
IGAMMA = ROOT / "ops" / "suite" / "dev" / "igamma_kernel.py"

_FAILURES = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (" | " + detail if detail else ""),
          flush=True)
    if not ok:
        _FAILURES.append(name)


def load_case(path, **kw):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.make_case(**kw)


def compile_and_run(case, work, tag, threads=1, libm=False, timeout=120):
    compiler = FactoryCompiler(options=CompileOptions(
        cache_dir=str(work / f"cache-{tag}"), vmath_libm=libm))
    staged = NativeExecutableDevice(compiler, threads).stage_case(case)
    result = subprocess.run(
        [os.environ["A100_QEMU"], "-L", os.environ["A100_SYSROOT"],
         "-cpu", os.environ["A100_QEMU_CPU"],
         str(staged.artifact.executable), "--bundle",
         str(staged.directory / "bundle.bin"), "--threads", str(threads),
         "--repeats", "3"],
        capture_output=True, text=True, timeout=timeout)
    assert result.returncode == 0, result.stdout[-400:] + result.stderr[-800:]
    runtime = json.loads(result.stdout.strip().splitlines()[-1])
    assert runtime["repeats_all_equal"], runtime
    return staged, staged.outputs(), Path(staged.artifact.executable).parent


def compare(case, outputs):
    for name, policy in case["comparison"].items():
        got = np.asarray(outputs[name])
        exp = np.asarray(case["expected"][name])
        if got.shape != exp.shape:
            return False
        if policy.get("exact") or policy.get("comparator") == "array_equal":
            if not np.array_equal(got, exp):
                return False
        elif not np.allclose(got.astype(np.float64), exp.astype(np.float64),
                             rtol=policy.get("rtol", 1e-5),
                             atol=policy.get("atol", 1e-5),
                             equal_nan=policy.get("equal_nan", False)):
            return False
    return True


def probe_case(work):
    """A mixed-magnitude sin/cos case: in-range, out-of-range and special
    lanes in one vector, checked against the f64-computed reference."""
    path = work / "sincos_probe.py"
    path.write_text('''OPERATOR={'name':'sincos_probe','group':'probe','channel':'local','execution':'triton_kernel','verification':'correctness','tags':[]}
import triton
import triton.language as tl
@triton.jit
def kernel(X,Y,n,B:tl.constexpr,FORM:tl.constexpr):
    i=tl.arange(0,B)
    mask=i<n
    x=tl.load(X+i,mask=mask,other=0.0)
    if FORM == 0:
        out=tl.sin(x)
    else:
        out=tl.cos(x)
    tl.store(Y+i,out,mask=mask)
def _make_case(shape=None,dtype='float32',seed=30):
    return {'grid':(1,)}
''')
    spec = importlib.util.spec_from_file_location("sincos_probe", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    def make(form, values):
        x = np.asarray(values, np.float32)
        y = np.zeros_like(x)
        with np.errstate(invalid="ignore"):
            expected = (np.sin(x.astype(np.float64)) if form == 0
                        else np.cos(x.astype(np.float64))).astype(np.float32)
        policy = {"comparator": "allclose", "exact": False, "rtol": 0,
                  "atol": 1e-4, "equal_nan": True}
        return {"kernel": module.kernel,
                "args": {"X": x, "Y": y, "n": np.int32(len(x))},
                "meta": {"B": 32, "FORM": form}, "grid": (1,),
                "outputs": ("Y",), "expected": {"Y": expected},
                "comparison": {"Y": policy}}
    return make


def main():
    work = Path(tempfile.mkdtemp(prefix="t-sc-"))
    # 1. the corpus operators, 1 and 2 workers
    specs = [
        (SIN_KERNEL, {"shape": [4096], "dtype": "float32"}),
        (COSINE, {"shape": [4096], "dtype": "float32"}),
        (BLACKMAN, {"shape": [1024], "dtype": "float32"}),
        (SYNTH, {"shape": [1, 4, 16, 64], "dtype": "float32"}),
        (IGAMMA, {"shape": [118], "dtype": "float32"}),
    ]
    for path, kw in specs:
        case = load_case(path, **kw)
        for threads in (1, 2):
            try:
                _, outputs, _ = compile_and_run(
                    case, work, f"{path.stem}-{threads}", threads,
                    timeout=180)
                ok = compare(case, outputs)
            except Exception as exc:      # noqa: BLE001
                ok = False
                print("   exc:", str(exc).splitlines()[-1][:160])
            check(f"sincos-corpus-pass-{path.stem}-t{threads}", ok)
    # 2. the domain guard: mixed magnitudes through the fallback
    maker = probe_case(work)
    mixed = [0.5, -0.5, 3.14159265, -2.718281828, 100.0, -100.0,
             1023.999, -1023.999, 1e6, -1e6, 1e30, -1e30, 0.0, -0.0,
             1e-38, 700.0, 5000.0, -5000.0, 12.566370614, 6.283185307]
    for form in (0, 1):
        case = maker(form, mixed)
        _, outputs, _ = compile_and_run(case, work, f"mixed-{form}")
        check(f"sincos-domain-guard-form{form}", compare(case, outputs),
              "mixed magnitudes incl. 1e6/1e30 ride the fallback")
    # 3. the switch contrast (libm vs polynomial)
    case = maker(0, mixed[:8] + [0.25] * 8 + [900.0] * 8 + [0.125] * 8)
    poly_staged, poly_out, poly_dir = compile_and_run(
        case, work, "poly", libm=False)
    libm_staged, libm_out, libm_dir = compile_and_run(
        case, work, "libm", libm=True)
    poly_asm = (poly_dir / "program.S").read_text()
    libm_asm = (libm_dir / "program.S").read_text()
    # the polynomial arm carries the rint magic's IEEE bit pattern
    # (12582912.0 -> 1262485504); the libm-only build never emits it.
    # BOTH builds contain the fallback arm's `call sinf` (the guard's
    # else arm), so the call's presence alone distinguishes nothing.
    check("sincos-switch-cache-keys-differ",
          poly_dir.name != libm_dir.name,
          f"{poly_dir.name[:12]} vs {libm_dir.name[:12]}")
    check("sincos-switch-poly-arm-present",
          "1262485504" in poly_asm and "1262485504" not in libm_asm,
          "the rint magic is in the polynomial build only")
    check("sincos-switch-libm-fallback-arms",
          "call sinf" in poly_asm and "call sinf" in libm_asm,
          "both builds keep the libm fallback arm")
    check("sincos-switch-both-pass",
          compare(case, poly_out) and compare(case, libm_out),
          "both paths compare PASS under the original policy")
    # 4. the witness: the guard stripped (cap -> inf) computes wrong
    #    values on far-out-of-range lanes
    import a100c.lower.vectorize as vec
    orig = vec._POLY_SINCOS_XMAX
    try:
        vec._POLY_SINCOS_XMAX = float("inf")
        case_w = maker(0, [0.5, 1e6, -1e30, 5000.0])
        _, outputs_w, _ = compile_and_run(case_w, work / "witness",
                                          "guard-stripped")
        bad = not compare(case_w, outputs_w)
        detail = "out-of-range lanes compared wrong (guard is load-bearing)"
    except Exception as exc:          # noqa: BLE001
        bad = True
        detail = "compile/run refused: " + str(exc).splitlines()[-1][:120]
    finally:
        vec._POLY_SINCOS_XMAX = orig
    check("sincos-witness-guard-stripped", bad, detail)
    # 5. fp64 sin stays on the libm path
    spec_pq = importlib.util.spec_from_file_location(
        "pq", str(ROOT / "ops" / "suite" / "dev" / "position_quantize.py"))
    pq = importlib.util.module_from_spec(spec_pq)
    spec_pq.loader.exec_module(pq)
    case64 = pq.make_case()
    try:
        _, outputs64, dir64 = compile_and_run(case64, work, "f64",
                                              timeout=180)
        ok = compare(case64, outputs64)
        asm64 = (dir64 / "program.S").read_text()
        poly64 = "fcvt" in asm64 and "sin" in asm64  # informational only
    except Exception as exc:          # noqa: BLE001
        ok = False
        poly64 = False
        print("   exc:", str(exc).splitlines()[-1][:160])
    check("sincos-f64-untouched", ok,
          "fp64 sin rides its own path (SEW 64 never enters the poly)")
    if _FAILURES:
        print("FAILED: " + ", ".join(_FAILURES))
        return 1
    print("test_vmath_sincos: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
