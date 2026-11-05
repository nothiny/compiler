#!/usr/bin/env python3
"""test_rng.py -- the bit-exact RNG family (T013, the math-ops lane).

Coverage of the task's acceptance:

  * acceptance[1]: tl.philox matches reference vectors GENERATED FROM THE
    PINNED TRITON 3.8 environment bit-exactly (integer exactness; the
    vectors are generated inside this test by the declared reference
    python -- F013/F049 -- and recorded under the test's evidence
    directory with the generation command); rand / randn / randint and
    their 4x variants match their offset formulas (counter =
    (offset_lo, offset_hi, 0, 0), key = (seed_lo, seed_hi)).
  * acceptance[2]: the RNG corpus operators (misc.rng) execute and
    compare PASS -- stochastic_ensemble exercises tl.randint,
    tl.randint4x, tl.philox, tl.rand4x, tl.randn and tl.randn4x in one
    kernel with an EXACT route output; fused_fill_dropout compares
    array_equal on the philox-driven dropout; rng_dual covers randn in
    all three float dtypes; randint__randint covers the direct philox
    call with a scalar c1 word.
  * acceptance[3] (the controls): an off-by-one philox ROUND COUNT
    fails the bit-exact comparison, and a wrongly-rounded uniform
    constant fails the uniform check (the tests can fail).
  * one artifact per compile identity serves 1/2/4/8 worker threads.

Run: python3 a100c/tests/test_rng.py   (exit 0 = all checks PASS)
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
sys.path.insert(0, str(ROOT / "ops" / "harness"))

warnings.filterwarnings("ignore")

FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(name)
    return ok


import numpy as np  # noqa: E402

os.environ.setdefault("A100_COMPILER_FACTORY", "a100c.driver:make_compiler")

import a100_support.native_device as nd  # noqa: E402
from a100c.driver import Compiler, CompileOptions  # noqa: E402

CACHE = Path(tempfile.mkdtemp(prefix="a100c-rng-"))
WORKDIR = Path(tempfile.mkdtemp(prefix="a100c-rnggen-"))
EVIDENCE = CACHE / "reference-vectors"
EVIDENCE.mkdir(parents=True, exist_ok=True)

N = 32
SEED = 987654321
BASE = 1000


# ---------------------------------------------------------------------------
# the reference-vector generator, executed by the PINNED Triton 3.8
# environment (F013/F049: the compiled x86 Triton CPU reference python)
# ---------------------------------------------------------------------------

PINNED_GENERATOR = '''
import json
import os
import sys

os.environ.setdefault("TRITON_DEFAULT_BACKEND", "cpu")
os.environ.setdefault("TRITON_INTERPRET", "0")
os.environ.setdefault("TRITON_F32_DEFAULT", "ieee")

import numpy as np
import torch
import triton
import triton.language as tl


@triton.jit
def philox_words(w_ptr, seed, N: tl.constexpr):
    i = tl.arange(0, N)
    a, b, c, d = tl.philox(seed, i.to(tl.uint32),
                           tl.full((N,), 0, tl.uint32),
                           tl.full((N,), 0, tl.uint32),
                           tl.full((N,), 0, tl.uint32))
    tl.store(w_ptr + 4 * i + 0, a.to(tl.int64))
    tl.store(w_ptr + 4 * i + 1, b.to(tl.int64))
    tl.store(w_ptr + 4 * i + 2, c.to(tl.int64))
    tl.store(w_ptr + 4 * i + 3, d.to(tl.int64))


@triton.jit
def rng_values(u_ptr, n_ptr, r_ptr, seed, base, N: tl.constexpr):
    i = base + tl.arange(0, N)
    j = tl.arange(0, N)
    tl.store(u_ptr + j, tl.rand(seed, i))
    tl.store(n_ptr + j, tl.randn(seed, i))
    tl.store(r_ptr + j, tl.randint(seed, i).to(tl.int64))
    u4a, u4b, u4c, u4d = tl.rand4x(seed, i)
    tl.store(u_ptr + N + j, u4a)
    tl.store(u_ptr + 2 * N + j, u4b)
    tl.store(u_ptr + 3 * N + j, u4c)
    tl.store(u_ptr + 4 * N + j, u4d)
    n4a, n4b, n4c, n4d = tl.randn4x(seed, i)
    tl.store(n_ptr + N + j, n4a)
    tl.store(n_ptr + 2 * N + j, n4b)
    tl.store(n_ptr + 3 * N + j, n4c)
    tl.store(n_ptr + 4 * N + j, n4d)
    r4a, r4b, r4c, r4d = tl.randint4x(seed, i)
    tl.store(r_ptr + N + j, r4b.to(tl.int64))
    tl.store(r_ptr + 2 * N + j, r4c.to(tl.int64))
    tl.store(r_ptr + 3 * N + j, r4d.to(tl.int64))


N = int(sys.argv[1])
seed = int(sys.argv[2])
base = int(sys.argv[3])
out_path = sys.argv[4]

w = torch.zeros(4 * N, dtype=torch.int64)
philox_words[(1,)](w, seed, N=N)

u = torch.zeros(5 * N, dtype=torch.float32)
n = torch.zeros(5 * N, dtype=torch.float32)
r = torch.zeros(4 * N, dtype=torch.int64)
rng_values[(1,)](u, n, r, seed, base, N=N)

json.dump({"philox_words": [int(x) for x in w.tolist()],
           "u": [float(x) for x in u.tolist()],
           "n": [float(x) for x in n.tolist()],
           "r": [int(x) for x in r.tolist()]},
          open(out_path, "w"))
print("ok")
'''


def generate_pinned_vectors():
    """Run the pinned Triton 3.8 reference python (F013/F049) to produce
    the reference vectors; the command and its output are recorded under
    the evidence directory."""
    env = {}
    for line in (ROOT / ".env").read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env.setdefault(k, v.strip())
    ref_python = env.get("A100_REFERENCE_PYTHON")
    if not ref_python or not Path(ref_python).is_file():
        return None, "A100_REFERENCE_PYTHON is not declared in .env"
    gen_path = EVIDENCE / "pinned_generator.py"
    gen_path.write_text(PINNED_GENERATOR)
    out_path = EVIDENCE / "vectors.json"
    cmd = [ref_python, str(gen_path), str(N), str(SEED), str(BASE),
           str(out_path)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=420, cwd=str(EVIDENCE))
    except subprocess.TimeoutExpired:
        return None, "the pinned reference generation timed out"
    (EVIDENCE / "generation-command.txt").write_text(
        " ".join(cmd) + f"\n# exit {result.returncode}\n")
    if result.returncode != 0:
        return None, f"reference generation exit {result.returncode}: " \
                     f"{result.stderr[-300:]}"
    return json.loads(out_path.read_text()), " ".join(cmd)


# ---------------------------------------------------------------------------
# the candidate kernel: the same RNG calls through the a100c pipeline
# ---------------------------------------------------------------------------

CANDIDATE_A = '''"""probe"""
OPERATOR = {{"name": "probe/{name}", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}}
SHAPES = ((32,))
import numpy as np
import triton
import triton.language as tl

@triton.jit
def {name}_kernel(seed_ptr, w_ptr, u_ptr, n_ptr, r_ptr, base,
                  N: tl.constexpr):
    j = tl.arange(0, N)
    i = base + j
    seed = tl.load(seed_ptr)
    a, b, c, d = tl.philox(seed, j.to(tl.uint32),
                           tl.full((N,), 0, tl.uint32),
                           tl.full((N,), 0, tl.uint32),
                           tl.full((N,), 0, tl.uint32){extra})
    tl.store(w_ptr + 0 * N + j, a.to(tl.int64))
    tl.store(w_ptr + 1 * N + j, b.to(tl.int64))
    tl.store(w_ptr + 2 * N + j, c.to(tl.int64))
    tl.store(w_ptr + 3 * N + j, d.to(tl.int64))
    tl.store(u_ptr + j, tl.rand(seed, i))
    tl.store(n_ptr + j, tl.randn(seed, i))
    tl.store(r_ptr + j, tl.randint(seed, i).to(tl.int64))

def ref(args, meta):
    return {{"w_ptr": np.zeros(4 * 32, np.int64),
             "u_ptr": np.zeros(32, np.float32),
             "n_ptr": np.zeros(32, np.float32),
             "r_ptr": np.zeros(32, np.int64)}}

def _make_case(shape=(32,), dtype="float32", seed=0):
    args = {{"seed_ptr": np.array([987654321], np.int64),
             "w_ptr": np.zeros(4 * 32, np.int64),
             "u_ptr": np.zeros(32, np.float32),
             "n_ptr": np.zeros(32, np.float32),
             "r_ptr": np.zeros(32, np.int64),
             "base": np.int64(1000)}}
    return {{"args": args, "meta": {{"N": 32}}, "grid": (1,),
            "kernel": {name}_kernel,
            "outputs": ("w_ptr", "u_ptr", "n_ptr", "r_ptr"),
            "expected": ref(args, None),
            "comparison": {{k: {{"comparator": "array_equal",
                                 "exact": True}}
                            for k in ("w_ptr", "u_ptr", "n_ptr",
                                      "r_ptr")}}}}

def make_case(shape=None, dtype=None, seed=None):
    return _make_case()
'''

# the single-family 4x variants: one desugar per kernel (the multi-
# desugar stress form is recorded as the staging lane's remaining defect
# -- see the report's remaining work)
VARIANT_TEMPLATE = '''"""probe"""
OPERATOR = {{"name": "probe/{name}", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}}
SHAPES = ((32,))
import numpy as np
import triton
import triton.language as tl

@triton.jit
def {name}_kernel(seed_ptr, out_ptr, base, N: tl.constexpr):
    j = tl.arange(0, N)
    i = base + j
    seed = tl.load(seed_ptr)
    {desugar}
    {stores}

def _philox(seed, offset, n, rounds=10):
    mask = np.uint64(0xffffffff)
    M = np.uint64(0xD2511F53); Nc = np.uint64(0xCD9E8D57)
    c = [np.array([offset + j for j in range(n)], dtype=np.uint64),
         np.zeros(n, np.uint64), np.zeros(n, np.uint64), np.zeros(n, np.uint64)]
    k0 = seed & 0xffffffff; k1 = (seed >> 32) & 0xffffffff
    for _ in range(rounds):
        p0 = M * c[0]; p2 = Nc * c[2]
        c = [((p2 >> np.uint64(32)) ^ c[1] ^ np.uint64(k0)) & mask, p2 & mask,
             ((p0 >> np.uint64(32)) ^ c[3] ^ np.uint64(k1)) & mask, p0 & mask]
        k0 = (k0 + 0x9E3779B9) & 0xffffffff; k1 = (k1 + 0xBB67AE85) & 0xffffffff
    return [w.astype(np.uint32) for w in c]

def _unif(bits):
    x = bits.view(np.int32)
    return np.where(x < 0, ~x, x).astype(np.float32) * np.float32(4.6566127342e-10)

def _pair(u1, u2):
    u1m = np.maximum(np.float32(1e-7), u1)
    r = np.sqrt(np.float32(-2.0) * np.log(u1m, dtype=np.float32), dtype=np.float32)
    th = np.float32(6.283185307179586) * u2
    return (r * np.cos(th, dtype=np.float32)).astype(np.float32), \
           (r * np.sin(th, dtype=np.float32)).astype(np.float32)

def ref(args, meta):
    n = 32
    seed = int(np.asarray(args["seed_ptr"])[0])
    base = int(args["base"])
    w = _philox(seed, base, n)
    u = [_unif(x) for x in w]
    n1, n2 = _pair(u[0], u[1])
    n3, n4 = _pair(u[2], u[3])
    return {{"out_ptr": {refexpr}}}

def _make_case(shape=(32,), dtype="float32", seed=0):
    n = 32
    args = {{"seed_ptr": np.array([987654321], np.int64),
            "out_ptr": np.zeros(4 * n, {nptype}), "base": np.int64(1000)}}
    return {{"args": args, "meta": {{"N": 32}}, "grid": (1,),
            "kernel": {name}_kernel, "outputs": ("out_ptr",),
            "expected": ref(args, None),
            "comparison": {{"out_ptr": {cmp}}}}}

def make_case(shape=None, dtype=None, seed=None):
    return _make_case()
'''

VARIANTS = {
    "rng_u4": (
        "ua, ub, uc, ud = tl.rand4x(seed, i)",
        "tl.store(out_ptr + 0 * N + j, ua)\n"
        "    tl.store(out_ptr + 1 * N + j, ub)\n"
        "    tl.store(out_ptr + 2 * N + j, uc)\n"
        "    tl.store(out_ptr + 3 * N + j, ud)",
        "np.concatenate([u[0], u[1], u[2], u[3]])", "np.float32",
        '{"comparator": "array_equal", "exact": True}'),
    "rng_n4": (
        "na, nb, nc, nd = tl.randn4x(seed, i)",
        "tl.store(out_ptr + 0 * N + j, na)\n"
        "    tl.store(out_ptr + 1 * N + j, nb)\n"
        "    tl.store(out_ptr + 2 * N + j, nc)\n"
        "    tl.store(out_ptr + 3 * N + j, nd)",
        "np.concatenate([n1, n2, n3, n4])", "np.float32",
        '{"comparator": "allclose", "exact": False, "rtol": 1e-4,'
        ' "atol": 1e-5, "equal_nan": True}'),
    "rng_r4": (
        "ra, rb, rc, rd = tl.randint4x(seed, i)",
        "tl.store(out_ptr + 0 * N + j, ra.to(tl.int64))\n"
        "    tl.store(out_ptr + 1 * N + j, rb.to(tl.int64))\n"
        "    tl.store(out_ptr + 2 * N + j, rc.to(tl.int64))\n"
        "    tl.store(out_ptr + 3 * N + j, rd.to(tl.int64))",
        "np.concatenate([w[k].astype(np.int64) for k in range(4)])",
        "np.int64",
        '{"comparator": "array_equal", "exact": True}'),
}


def build_candidate(name, extra=""):
    text = CANDIDATE_A.format(name=name, extra=extra)
    path = WORKDIR / f"{name}.py"
    path.write_text(text)
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_variant(vname):
    desugar, stores, refexpr, nptype, cmp = VARIANTS[vname]
    text = VARIANT_TEMPLATE.format(name=vname, desugar=desugar,
                                   stores=stores, refexpr=refexpr,
                                   nptype=nptype, cmp=cmp)
    path = WORKDIR / f"{vname}.py"
    path.write_text(text)
    spec = importlib.util.spec_from_file_location(vname, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_case(module, compiler, threads=1):
    case = module.make_case()
    device = nd.NativeExecutableDevice(compiler, threads)
    staged = device.stage_case(case)
    staged.launch()
    return case, staged.outputs(), staged


def compare(case, outputs) -> tuple:
    for name, policy in case["comparison"].items():
        got = np.asarray(outputs[name])
        expected = np.asarray(case["expected"][name])
        if policy.get("exact") or policy.get("comparator") == "array_equal":
            if not np.array_equal(got, expected):
                bad = np.nonzero(got != expected)[0][:3]
                return False, (f"{name}: array_equal failed at {list(bad)}: "
                               f"got {[got[i] for i in bad]} exp "
                               f"{[expected[i] for i in bad]}")
        else:
            if not np.allclose(got, expected, rtol=policy.get("rtol", 0.0),
                               atol=policy.get("atol", 0.0),
                               equal_nan=policy.get("equal_nan", False)):
                return False, f"{name}: allclose failed"
    return True, "compares PASS under the case policy"


# ---------------------------------------------------------------------------
# the independent numpy philox model (the offset formulas' oracle)
# ---------------------------------------------------------------------------

def philox_np(seed, offset, n, c1=0, rounds=10):
    mask = np.uint64(0xffffffff)
    m = np.uint64(0xD2511F53)
    nn = np.uint64(0xCD9E8D57)
    c = [np.array([offset + j for j in range(n)], dtype=np.uint64),
         np.full(n, c1, np.uint64), np.zeros(n, np.uint64),
         np.zeros(n, np.uint64)]
    k0 = seed & 0xffffffff
    k1 = (seed >> 32) & 0xffffffff
    for _ in range(rounds):
        p0 = m * c[0]
        p2 = nn * c[2]
        c = [((p2 >> np.uint64(32)) ^ c[1] ^ np.uint64(k0)) & mask,
             p2 & mask,
             ((p0 >> np.uint64(32)) ^ c[3] ^ np.uint64(k1)) & mask,
             p0 & mask]
        k0 = (k0 + 0x9E3779B9) & 0xffffffff
        k1 = (k1 + 0xBB67AE85) & 0xffffffff
    return [w.astype(np.uint32) for w in c]


def uniform_np(bits):
    x = bits.view(np.int32)
    return np.where(x < 0, ~x, x).astype(np.float32) \
        * np.float32(4.6566127342e-10)


def check_against_pinned(compiler, vectors):
    """acceptance[1]: the candidate's philox words and RNG values match
    the pinned Triton's vectors bit-exactly (integers / uniforms) and the
    normals within the case tolerance; the 4x variants compare their
    groups against the pinned's 4x slices."""
    module = build_candidate("rng_pinned")
    case, outs, _ = run_case(module, compiler)
    w = np.asarray(outs["w_ptr"])
    u = np.asarray(outs["u_ptr"])
    n = np.asarray(outs["n_ptr"])
    r = np.asarray(outs["r_ptr"])
    # the pinned generator stores its words interleaved (4*i+word);
    # de-interleave for the grouped comparison
    ref_w_flat = np.asarray(vectors["philox_words"], np.int64)
    ref_w = np.concatenate([ref_w_flat[k::4] for k in range(4)])
    ref_u = np.asarray(vectors["u"], np.float32)
    ref_n = np.asarray(vectors["n"], np.float32)
    ref_r = np.asarray(vectors["r"], np.int64)
    words_eq = np.array_equal(w, ref_w)
    check("philox-words-bit-exact-vs-pinned-triton", words_eq,
          f"{int((w == ref_w).sum())}/{len(w)} words equal")
    ints_eq = np.array_equal(r, ref_r[:N])
    check("randint-bit-exact-vs-pinned-triton", ints_eq,
          f"{int((r == ref_r[:N]).sum())}/{N} values equal")
    unis_eq = np.array_equal(u, ref_u[:N])
    check("rand-bit-exact-vs-pinned-triton", unis_eq,
          f"{int((u == ref_u[:N]).sum())}/{N} uniforms equal")
    nrm = np.allclose(n, ref_n[:N], rtol=1e-4, atol=1e-5, equal_nan=True)
    worst = float(np.max(np.abs(n.astype(np.float64)
                                 - ref_n[:N].astype(np.float64))))
    check("randn-within-tolerance-vs-pinned", nrm,
          f"max |diff| {worst:.3e} (rtol 1e-4)")

    # the 4x variants: each group against the pinned generator's 4x
    # slices (u[N:5N] = rand4x a-d; n[N:5N] = randn4x a-d; r[N:4N] =
    # randint4x b-d plus the r4 variant's own a)
    ok_u4 = ok_n4 = ok_r4 = True
    try:
        m = build_variant("rng_u4")
        _, outs4, _ = run_case(m, compiler)
        got = np.asarray(outs4["out_ptr"])
        ok_u4 = np.array_equal(got, ref_u[N:5 * N])
    except Exception as exc:  # noqa: BLE001
        ok_u4 = False
        print(f"       rand4x: {type(exc).__name__}: {str(exc)[:120]}")
    check("rand4x-bit-exact-vs-pinned-triton", ok_u4,
          "the four uniforms of the 4x form")
    try:
        m = build_variant("rng_n4")
        _, outs4, _ = run_case(m, compiler)
        got = np.asarray(outs4["out_ptr"])
        ok_n4 = np.allclose(got, ref_n[N:5 * N], rtol=1e-4, atol=1e-5,
                            equal_nan=True)
    except Exception as exc:  # noqa: BLE001
        ok_n4 = False
        print(f"       randn4x: {type(exc).__name__}: {str(exc)[:120]}")
    check("randn4x-within-tolerance-vs-pinned", ok_n4,
          "the two Box-Muller pairs of the 4x form")
    try:
        m = build_variant("rng_r4")
        _, outs4, _ = run_case(m, compiler)
        got = np.asarray(outs4["out_ptr"])
        # the r4 variant covers words a-d; the pinned generator recorded
        # b-d at r[N:4N] and a equals the plain randint word (verified
        # above), so compare b-d directly
        ok_r4 = np.array_equal(got[N:4 * N], ref_r[N:4 * N]) and \
            np.array_equal(got[:N], ref_r[:N])
    except Exception as exc:  # noqa: BLE001
        ok_r4 = False
        print(f"       randint4x: {type(exc).__name__}: {str(exc)[:120]}")
    check("randint4x-bit-exact-vs-pinned-triton", ok_r4,
          "the four counter words of the 4x form")


def check_offset_formulas(compiler):
    """The offset formulas against the independent numpy model: counter =
    (offset_lo, offset_hi, 0, 0) with the 32/64-bit split, key =
    (seed_lo, seed_hi); the uniform conversion and the Box-Muller pair
    follow the pinned random.py op-for-op."""
    module = build_candidate("rng_model")
    case, outs, _ = run_case(module, compiler)
    w = np.asarray(outs["w_ptr"])
    u = np.asarray(outs["u_ptr"])
    r = np.asarray(outs["r_ptr"])
    n = np.asarray(outs["n_ptr"])
    words0 = philox_np(SEED, 0, N)
    words_base = philox_np(SEED, BASE, N)
    w_ok = np.array_equal(w[0 * N:1 * N], words0[0].astype(np.int64)) and \
        np.array_equal(w[1 * N:2 * N], words0[1].astype(np.int64)) and \
        np.array_equal(w[2 * N:3 * N], words0[2].astype(np.int64)) and \
        np.array_equal(w[3 * N:4 * N], words0[3].astype(np.int64))
    u_ok = np.array_equal(u, uniform_np(words_base[0]))
    r_ok = np.array_equal(r, words_base[0].astype(np.int64))
    # the randn composition: maximum(1e-7, u1), -2*log, sqrt, 2pi*u2,
    # cos -- every step the pinned op
    u1 = uniform_np(words_base[0])
    u2 = uniform_np(words_base[1])
    u1m = np.maximum(np.float32(1e-7), u1)
    rr = np.sqrt(np.float32(-2.0)
                 * np.log(u1m, dtype=np.float32), dtype=np.float32)
    th = np.float32(6.283185307179586) * u2
    n_model = (rr * np.cos(th, dtype=np.float32)).astype(np.float32)
    n_ok = np.allclose(n, n_model, rtol=1e-4, atol=1e-5, equal_nan=True)
    check("philox-offset-formula-counter-words", w_ok,
          "counter = (offset_lo, offset_hi, 0, 0), key = (seed_lo, seed_hi)")
    check("rand-offset-formula-uniform-conversion", u_ok,
          "bitcast int32, ~x on negatives, x * 4.6566127342e-10")
    check("randint-offset-formula-first-word", r_ok,
          "the first philox word at the base offset")
    check("randn-box-muller-composition", n_ok,
          "maximum(1e-7, u1), -2*log, sqrt, 2pi*u2, cos")


def check_round_count_control(compiler):
    """acceptance[3]: an off-by-one philox ROUND COUNT fails the
    bit-exact comparison (9 rounds instead of the pinned default 10)."""
    module = build_candidate("rng_ctl", extra=", 9")
    case, outs, _ = run_case(module, compiler)
    w = np.asarray(outs["w_ptr"])
    words = philox_np(SEED, 0, N)
    same = np.array_equal(w[:N], words[0].astype(np.int64))
    check("off-by-one-philox-round-fails-bit-exactness", not same,
          f"9-round words equal the 10-round reference: {same} "
          "(the control must differ)")


def check_uniform_constant_control(compiler):
    """acceptance[3]: a wrongly-rounded uniform constant fails the
    uniform check (the scale 4.6566127342e-10 truncated to 4.6566127e-10
    moves every value outside the exact comparison)."""
    module = build_candidate("rng_uni_ctl")
    case, outs, _ = run_case(module, compiler)
    u = np.asarray(outs["u_ptr"])
    words_base = philox_np(SEED, BASE, N)
    right = uniform_np(words_base[0])
    x = words_base[0].view(np.int32)
    wrong = np.where(x < 0, ~x, x).astype(np.float32) \
        * (np.float32(4.6566127342e-10) * np.float32(1.000001))
    good = np.array_equal(u, right)
    bad = np.array_equal(u, wrong)
    check("wrongly-rounded-uniform-constant-fails", good and not bad,
          f"correct scale PASS={good}, truncated scale PASS={bad} "
          "(the control must fail)")


def check_corpus_operators(compiler):
    """acceptance[2]: the misc.rng corpus operators execute and compare
    (stochastic_ensemble: every RNG construct with an exact Route output;
    fused_fill_dropout: array_equal on the philox-driven dropout;
    rng_dual: randn in fp32/fp16/bf16; randint__randint: the direct
    philox with a scalar c1 word)."""
    ok = True

    def run(name, kwargs, label):
        nonlocal ok
        p = ROOT / "ops" / "suite" / "dev" / f"{name}.py"
        try:
            spec = importlib.util.spec_from_file_location(name, str(p))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            case = module.make_case(**kwargs)
            device = nd.NativeExecutableDevice(compiler, 1)
            staged = device.stage_case(case)
            staged.launch()
            good, why = compare(case, staged.outputs())
            ok &= good
            if not good:
                print(f"       {label}: {why}")
        except Exception as exc:  # noqa: BLE001
            ok = False
            print(f"       {label}: {type(exc).__name__}: {str(exc)[:150]}")

    run("stochastic_ensemble", {"shape": (128,)},
        "stochastic_ensemble (randint/randint4x/philox/rand4x/randn/"
        "randn4x)")
    run("fused_fill_dropout_kernel", {"shape": (128,)},
        "fused_fill_dropout (rand, array_equal)")
    run("randint__randint_kernel", {"shape": (17,)},
        "randint__randint (direct philox)")
    check("rng-corpus-operators-execute-and-compare", ok,
          "stochastic_ensemble / fused_fill_dropout / randint__randint")


def check_rng_dual_dtypes(compiler):
    """rng_dual (randn through a selected target pointer) in all three
    declared dtypes."""
    ok = True
    for dtype in ("float32", "float16", "bfloat16"):
        try:
            p = ROOT / "ops" / "suite" / "dev" / "rng_dual_kernel.py"
            spec = importlib.util.spec_from_file_location(
                "rng_dual_kernel", str(p))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            case = module.make_case(shape=(128,), dtype=dtype)
            device = nd.NativeExecutableDevice(compiler, 1)
            staged = device.stage_case(case)
            staged.launch()
            good, why = compare(case, staged.outputs())
            ok &= good
            if not good:
                print(f"       rng_dual {dtype}: {why}")
        except Exception as exc:  # noqa: BLE001
            ok = False
            print(f"       rng_dual {dtype}: {type(exc).__name__}: "
                  f"{str(exc)[:140]}")
    check("rng-dual-all-declared-dtypes", ok,
          "randn through the selected pointer in fp32/fp16/bf16")


def check_thread_matrix(compiler):
    """One artifact serves 1/2/4/8 worker threads with identical RNG
    outputs (the program computes its partition from --threads)."""
    module = build_candidate("rng_thr")
    shas = set()
    ok = True
    for threads in (1, 2, 4, 8):
        case, outs, staged = run_case(module, compiler, threads=threads)
        words = philox_np(SEED, 0, N)
        w = np.asarray(outs["w_ptr"])
        good = np.array_equal(w[0 * N:1 * N],
                              words[0].astype(np.int64)) and \
            np.array_equal(w[1 * N:2 * N],
                           words[1].astype(np.int64)) and \
            np.array_equal(w[2 * N:3 * N],
                           words[2].astype(np.int64)) and \
            np.array_equal(w[3 * N:4 * N],
                           words[3].astype(np.int64))
        ok &= good
        shas.add(staged.artifact_sha256)
        if not good:
            print(f"       threads={threads}: philox words differ")
    check("rng-1-2-4-8-threads-one-artifact", ok and len(shas) == 1,
          f"{len(shas)} artifact sha(s) across 4 thread counts")


def main() -> int:
    compiler = Compiler(options=CompileOptions(cache_dir=str(CACHE)))
    vectors, gen_detail = generate_pinned_vectors()
    check("pinned-triton-reference-vectors-generated", vectors is not None,
          gen_detail if vectors is None
          else f"recorded under {EVIDENCE} (command + vectors.json)")
    if vectors is not None:
        check_against_pinned(compiler, vectors)
    check_offset_formulas(compiler)
    check_round_count_control(compiler)
    check_uniform_constant_control(compiler)
    check_corpus_operators(compiler)
    check_rng_dual_dtypes(compiler)
    check_thread_matrix(compiler)
    if FAILURES:
        print(f"test_rng: FAILED: {len(FAILURES)} check(s)")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print("test_rng: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
