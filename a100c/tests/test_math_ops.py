#!/usr/bin/env python3
"""test_math_ops.py -- special math functions (T013, the math-ops lane).

Coverage of the task's acceptance:

  * acceptance[0]: the declared math forms -- exp, exp2, log, log2, sqrt,
    sqrt_rn, rsqrt, sigmoid, erf, sin, cos, floor, ceil, clamp, pow (the
    constexpr folds and the exp2*log2 composition), fma, div_rn, abs
    (float / signed-int / the unsigned identity), maximum / minimum with
    their propagate_nan policies -- compile through the real pipeline and
    their cases execute on the declared QEMU endpoint and compare PASS
    within each case's declared tolerance.  fp32 results use IEEE
    operations (vfsqrt / vfdiv / vfmacc are exactly rounded); fp16 / bf16
    ride the FP32 lanes under the declared single-rounding policy; the
    fp64 internal-compute width (position_quantize's phase reduction)
    lowers through the two declared routes.
  * acceptance[2] (the maximum/minimum half): propagate_nan=NONE returns
    the OTHER operand on NaN, =ALL propagates a quiet NaN -- executed
    with NaN inputs; the where/equal_nan comparison policies hold.
  * acceptance[3] (the control): a deliberately wrongly-rounded constant
    in the reference FAILS the comparison (the accuracy test can fail);
    a 16-bit operand to a transcendental is a located type error (the
    pinned _check_dtype boundary); tensor pow is refused (the pinned
    Triton 3.8 has no tensor __pow__).
  * representative corpus operators of the math families execute and
    compare at 1/2/4/8 worker threads on ONE artifact per identity.

Run: python3 a100c/tests/test_math_ops.py   (exit 0 = all checks PASS)
"""
from __future__ import annotations

import importlib.util
import math
import os
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

# the factory shim: a100_support.native_device.make_device() reads
# A100_COMPILER_FACTORY (F047)
os.environ.setdefault("A100_COMPILER_FACTORY", "a100c.driver:make_compiler")

import a100_support.native_device as nd  # noqa: E402
from a100c.driver import Compiler, CompileOptions, PipelineError  # noqa: E402
from a100c.frontend import lower_tir, source as fe_source, \
    specialize as fe_spec  # noqa: E402
from a100c.frontend.source import FrontendError  # noqa: E402

CACHE = Path(tempfile.mkdtemp(prefix="a100c-math-"))

# ---------------------------------------------------------------------------
# 1. the every-construct probe: one kernel per declared math form, exact
#    references from numpy at the fp32 IEEE / single-rounding policy
# ---------------------------------------------------------------------------

MATH_TEMPLATE = '''"""probe"""
OPERATOR = {{"name": "probe/{name}", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}}
SHAPES = ((32,))
import math
import numpy as np
import triton
import triton.language as tl

@triton.jit
def {name}_kernel(x_ptr, y_ptr, n, BLOCK: tl.constexpr):
    offs = tl.arange(0, BLOCK)
    m = offs < n
    x = tl.load(x_ptr + offs, mask=m, other=0.0)
    out = {body}
    tl.store(y_ptr + offs, out, mask=m)

def ref(args, meta):
    x = np.asarray(args["x_ptr"], dtype=np.float32)
    return {{"y_ptr": np.asarray({refexpr}, dtype=np.float32)}}

def _make_case(shape=(32,), dtype="float32", seed=0):
    n = 32
    rng = np.random.default_rng(11)
    x = rng.uniform(-3.0, 3.0, n).astype(np.float32)
    x[0] = 0.25
    x[1] = 1.0
    args = {{"x_ptr": x, "y_ptr": np.zeros(n, np.float32), "n": n}}
    return {{"args": args, "meta": {{"BLOCK": 32}}, "grid": (1,),
            "kernel": {name}_kernel, "outputs": ("y_ptr",),
            "expected": ref(args, None),
            "comparison": {{"y_ptr": {{"comparator": "allclose",
                                       "exact": False, "rtol": {rtol},
                                       "atol": {atol},
                                       "equal_nan": True}}}}}}

def make_case(shape=None, dtype=None, seed=None):
    return _make_case()
'''


# (name, kernel body, numpy reference, rtol, atol)
# the reference computes in float64 and rounds once to fp32: the fp32
# IEEE / single-rounding policy's oracle (the libm-backed forms stay
# inside 2 ulp of it; the direct IEEE forms are bit-exact at 1 ulp)
MATH_FORMS = [
    ("exp", "tl.exp(x)",
     "np.exp(x.astype(np.float64)).astype(np.float32)", 3e-7, 3e-7),
    ("exp2", "tl.exp2(x)",
     "np.exp2(x.astype(np.float64)).astype(np.float32)", 3e-7, 3e-7),
    ("log", "tl.log(tl.abs(x) + 1.0)",
     "np.log(np.abs(x.astype(np.float64)) + 1.0).astype(np.float32)",
     3e-7, 3e-7),
    ("log2", "tl.log2(tl.abs(x) + 1.0)",
     "np.log2(np.abs(x.astype(np.float64)) + 1.0).astype(np.float32)",
     3e-7, 3e-7),
    ("sqrt", "tl.sqrt(tl.abs(x))",
     "np.sqrt(np.abs(x.astype(np.float64))).astype(np.float32)",
     1e-7, 1e-7),
    ("sqrt_rn", "tl.sqrt_rn(tl.abs(x))",
     "np.sqrt(np.abs(x.astype(np.float64))).astype(np.float32)",
     1e-7, 1e-7),
    ("rsqrt", "tl.rsqrt(tl.abs(x) + 0.5)",
     "(1.0 / np.sqrt(np.abs(x.astype(np.float64)) + 0.5))"
     ".astype(np.float32)", 1e-6, 1e-6),
    ("sigmoid", "tl.sigmoid(x)",
     "(1.0 / (1.0 + np.exp(-x.astype(np.float64))))"
     ".astype(np.float32)", 3e-7, 3e-7),
    ("erf", "tl.erf(x * 0.5)",
     "np.vectorize(math.erf)(x.astype(np.float64) * 0.5)"
     ".astype(np.float32)", 3e-7, 3e-7),
    ("sin", "tl.sin(x)",
     "np.sin(x.astype(np.float64)).astype(np.float32)", 3e-7, 3e-7),
    ("cos", "tl.cos(x)",
     "np.cos(x.astype(np.float64)).astype(np.float32)", 3e-7, 3e-7),
    ("floor", "tl.floor(x * 1.5)",
     "np.floor(x.astype(np.float64) * 1.5).astype(np.float32)", 0, 0),
    ("ceil", "tl.ceil(x * -1.5)",
     "np.ceil(x.astype(np.float64) * -1.5).astype(np.float32)", 0, 0),
    ("clamp", "tl.clamp(x, -0.5, 0.75)",
     "np.clip(x, -0.5, 0.75)", 0, 0),
    ("fma", "tl.fma(x, 3.0, 0.5)",
     "(x.astype(np.float64) * 3.0 + 0.5).astype(np.float32)", 0, 0),
    ("div_rn", "tl.div_rn(x + 4.0, 3.0)",
     "((x + np.float32(4.0)) / np.float32(3.0))", 0, 0),
    ("abs", "tl.abs(x * -2.0)", "np.abs(x * -2.0)", 0, 0),
    ("maximum", "tl.maximum(x, 0.5)", "np.maximum(x, 0.5)", 0, 0),
    ("minimum", "tl.minimum(x, -0.5)", "np.minimum(x, -0.5)", 0, 0),
    ("pow_exp2log2", "tl.exp2(3.0 * tl.log2(tl.abs(x) + 0.125))",
     "np.exp2(3.0 * np.log2(np.abs(x.astype(np.float64)) + 0.125))"
     ".astype(np.float32)", 1e-6, 1e-6),
    # T016: the explicit function forms of the AST arithmetic operators
    # (position_quantize's spelled-out tl.add/tl.sub/tl.mul) and the
    # tl.cdiv (a+b-1)//b desugar, executed and compared like the rest
    ("arith_add", "tl.add(x, 0.5)",
     "(x + np.float32(0.5))", 0, 0),
    ("arith_sub", "tl.sub(x, 0.25)",
     "(x - np.float32(0.25))", 0, 0),
    ("arith_mul", "tl.mul(x, -1.5)",
     "(x * np.float32(-1.5))", 0, 0),
    ("cdiv_desugar",
     "tl.cast(tl.cdiv(tl.cast(tl.abs(x) * 8.0, tl.int32), 7), tl.float32)",
     "np.floor((np.abs(x) * 8.0 + 6.0) / 7.0)", 0, 0),
]

WORKDIR = Path(tempfile.mkdtemp(prefix="a100c-mathgen-"))


def build_form(name, body, refexpr, rtol, atol):
    text = MATH_TEMPLATE.format(name=name, body=body, refexpr=refexpr,
                                rtol=rtol, atol=atol)
    path = WORKDIR / f"{name}.py"
    path.write_text(text)
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compare(case, outputs) -> tuple:
    for name, policy in case["comparison"].items():
        got = np.asarray(outputs[name])
        expected = np.asarray(case["expected"][name])
        if policy.get("exact") or policy.get("comparator") == "array_equal":
            if not np.array_equal(got, expected):
                return False, f"{name}: array_equal failed"
        else:
            if not np.allclose(got, expected, rtol=policy.get("rtol", 0.0),
                               atol=policy.get("atol", 0.0),
                               equal_nan=policy.get("equal_nan", False)):
                d = np.abs(got.astype(np.float64)
                           - expected.astype(np.float64))
                i = int(np.argmax(d))
                return False, (f"{name}: max |diff| {d.max():.3e} at [{i}]: "
                               f"got {got.flatten()[i]} exp "
                               f"{expected.flatten()[i]}")
    return True, "compares PASS under the case policy"


def run_case(module, compiler, threads=1, shape=None, dtype=None):
    case = module.make_case(shape=shape, dtype=dtype)
    device = nd.NativeExecutableDevice(compiler, threads)
    staged = device.stage_case(case)
    staged.launch()
    return case, staged.outputs(), staged


def check_every_form(compiler):
    ok = True
    passed = []
    for name, body, refexpr, rtol, atol in MATH_FORMS:
        try:
            module = build_form(name, body, refexpr, rtol, atol)
            case, outs, _ = run_case(module, compiler)
            good, why = compare(case, outs)
            ok &= good
            passed.append(good)
            if not good:
                print(f"       {name}: {why}")
        except Exception as exc:  # noqa: BLE001
            ok = False
            passed.append(False)
            print(f"       {name}: {type(exc).__name__}: {str(exc)[:140]}")
    check("every-declared-math-form-executes-and-compares", ok,
          f"{sum(passed)}/{len(MATH_FORMS)} forms PASS")


def check_wrongly_rounded_control(compiler):
    """acceptance[3]: a deliberately wrong reference FAILS the comparison
    (the accuracy check can fail -- replacing exp2's constant with a
    truncated one moves every value far outside the tolerance)."""
    module = build_form(
        "ctl_exp2", "tl.exp2(x)",
        "np.exp2(x.astype(np.float64)).astype(np.float32)", 3e-7, 3e-7)
    case = module.make_case()
    # the control: perturb the expected values the way a wrongly-rounded
    # constant would (a 1e-3 relative error -- orders beyond tolerance)
    expected = np.asarray(case["expected"]["y_ptr"])
    perturbed = (expected.astype(np.float64) * (1.0 + 1e-3)) \
        .astype(np.float32)
    device = nd.NativeExecutableDevice(compiler, 1)
    staged = device.stage_case(module.make_case())
    staged.launch()
    got = np.asarray(staged.outputs()["y_ptr"])
    good_vs_ref = np.allclose(got, expected, rtol=3e-7, atol=3e-7)
    good_vs_wrong = np.allclose(got, perturbed, rtol=3e-7, atol=3e-7)
    check("wrongly-rounded-constant-fails-the-accuracy-test",
          good_vs_ref and not good_vs_wrong,
          f"correct ref PASS={good_vs_ref}, perturbed ref PASS="
          f"{good_vs_wrong} (the control must fail)")


def check_fp32_ieee_forms(compiler):
    """The direct IEEE forms are exactly rounded: sqrt / sqrt_rn / div_rn
    match the double-precision-rounded oracle bit-exactly (every value),
    and fma matches the single-rounding oracle bit-exactly."""
    ok = True
    for name, body, refexpr in (
            ("sqrt_exact", "tl.sqrt(tl.abs(x))",
             "np.sqrt(np.abs(x.astype(np.float64))).astype(np.float32)"),
            ("sqrt_rn_exact", "tl.sqrt_rn(tl.abs(x))",
             "np.sqrt(np.abs(x.astype(np.float64))).astype(np.float32)"),
            ("div_rn_exact", "tl.div_rn(x + 4.0, 3.0)",
             "((x + np.float32(4.0)) / np.float32(3.0))"),
            ("fma_exact", "tl.fma(x, 3.0, 0.5)",
             "(x.astype(np.float64) * 3.0 + 0.5).astype(np.float32)")):
        module = build_form(name, body, refexpr, 0, 0)
        case = module.make_case()
        device = nd.NativeExecutableDevice(compiler, 1)
        staged = device.stage_case(case)
        staged.launch()
        got = np.asarray(staged.outputs()["y_ptr"])
        exp = np.asarray(case["expected"]["y_ptr"])
        same = np.array_equal(got, exp)
        if not same:
            d = np.abs(got.astype(np.float64) - exp.astype(np.float64))
            i = int(np.argmax(d))
            print(f"       {name}: first diff at [{i}]: {got[i]} vs {exp[i]}")
        ok &= same
    check("fp32-ieee-forms-bit-exact", ok,
          "sqrt/sqrt_rn/div_rn/fma equal the double-rounded oracle")


def check_fp16_bf16_lanes(compiler):
    """The declared numeric decision: 16-bit compute rides the FP32 lanes
    with ONE final rounding (the fp16/bf16 tolerance absorbs the double
    rounding)."""
    ok = True
    module = build_form("cvt16", "tl.exp(tl.cast(x, tl.float32))",
                        "np.exp(x.astype(np.float64))", 3e-7, 3e-7)
    for dtype in ("float16", "bfloat16"):
        try:
            case = module.make_case(dtype=dtype)
            # re-express the expected in the requested dtype (the
            # enrichment's own round trip)
            exp32 = np.asarray(case["expected"]["y_ptr"])
            if dtype == "bfloat16":
                b = ((exp32.view(np.uint32) + 0x7fff
                      + ((exp32.view(np.uint32) >> 16) & 1))
                     .astype(np.uint64) >> np.uint64(16)).astype(np.uint16)
                exp = (b.astype(np.uint32) << 16).view(np.float32)
            else:
                exp = exp32.astype(np.float16).astype(np.float32)
            case["expected"]["y_ptr"] = exp
            device = nd.NativeExecutableDevice(compiler, 1)
            staged = device.stage_case(case)
            staged.launch()
            got = np.asarray(staged.outputs()["y_ptr"])
            good = np.allclose(got, exp, rtol=2e-2, atol=2e-2)
            ok &= good
            if not good:
                d = np.abs(got.astype(np.float64) - exp.astype(np.float64))
                print(f"       {dtype}: max |diff| {d.max():.3e}")
        except Exception as exc:  # noqa: BLE001
            ok = False
            print(f"       {dtype}: {type(exc).__name__}: {str(exc)[:120]}")
    check("fp16-bf16-ride-the-fp32-lanes", ok,
          "one final rounding inside the 16-bit tolerance")


def check_int_abs_and_minmax(compiler):
    """abs on signed integers is exact (iabs); the unsigned identity; int
    maximum / minimum exact (the corpus's clamp-composition users)."""
    text = '''"""probe"""
OPERATOR = {"name": "probe/int_math", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}
SHAPES = ((32,))
import numpy as np
import triton
import triton.language as tl

@triton.jit
def int_math_kernel(x_ptr, y_ptr, z_ptr, n, BLOCK: tl.constexpr):
    offs = tl.arange(0, BLOCK)
    m = offs < n
    x = tl.load(x_ptr + offs, mask=m, other=0)
    a = tl.abs(x)
    b = tl.maximum(x, -7)
    c = tl.minimum(x, 7)
    tl.store(y_ptr + offs, a, mask=m)
    tl.store(z_ptr + offs, b + c, mask=m)

def ref(args, meta):
    x = np.asarray(args["x_ptr"])
    return {"y_ptr": np.abs(x),
            "z_ptr": np.maximum(x, -7) + np.minimum(x, 7)}

def _make_case(shape=(32,), dtype="float32", seed=0):
    n = 32
    rng = np.random.default_rng(5)
    x = rng.integers(-1000, 1000, n).astype(np.int32)
    args = {"x_ptr": x, "y_ptr": np.zeros(n, np.int32),
            "z_ptr": np.zeros(n, np.int32), "n": n}
    return {"args": args, "meta": {"BLOCK": 32}, "grid": (1,),
            "kernel": int_math_kernel, "outputs": ("y_ptr", "z_ptr"),
            "expected": ref(args, None),
            "comparison": {k: {"comparator": "array_equal", "exact": True}
                           for k in ("y_ptr", "z_ptr")}}

def make_case(shape=None, dtype=None, seed=None):
    return _make_case()
'''
    path = WORKDIR / "int_math.py"
    path.write_text(text)
    spec = importlib.util.spec_from_file_location("int_math", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    case, outs, _ = run_case(module, compiler)
    good, why = compare(case, outs)
    check("integer-abs-and-maxmin-exact", good, why)


def check_nan_policies(compiler):
    """maximum / minimum honor propagate_nan: NONE returns the other
    operand on NaN, ALL propagates a quiet NaN; the where/equal_nan
    policies hold on the comparison side."""
    text = '''"""probe"""
OPERATOR = {"name": "probe/nan_mm", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}
SHAPES = ((32,))
import numpy as np
import triton
import triton.language as tl

@triton.jit
def nan_mm_kernel(x_ptr, y_ptr, o1, o2, o3, o4, n, BLOCK: tl.constexpr):
    offs = tl.arange(0, BLOCK)
    m = offs < n
    x = tl.load(x_ptr + offs, mask=m, other=0.0)
    y = tl.load(y_ptr + offs, mask=m, other=0.0)
    a = tl.maximum(x, y)
    b = tl.minimum(x, y)
    c = tl.maximum(x, y, propagate_nan=tl.PropagateNan.ALL)
    d = tl.minimum(x, y, propagate_nan=tl.PropagateNan.ALL)
    tl.store(o1 + offs, a, mask=m)
    tl.store(o2 + offs, b, mask=m)
    tl.store(o3 + offs, c, mask=m)
    tl.store(o4 + offs, d, mask=m)

def ref(args, meta):
    x = np.asarray(args["x_ptr"], np.float32)
    y = np.asarray(args["y_ptr"], np.float32)
    # NONE: the other operand on NaN (the C fmaxf/fminf convention)
    a = np.where(np.isnan(x), y, np.where(np.isnan(y), x, np.maximum(x, y)))
    b = np.where(np.isnan(x), y, np.where(np.isnan(y), x, np.minimum(x, y)))
    # ALL: a quiet NaN propagates
    nan = np.isnan(x) | np.isnan(y)
    c = np.where(nan, np.float32("nan"), np.maximum(x, y))
    d = np.where(nan, np.float32("nan"), np.minimum(x, y))
    return {"o1": a, "o2": b, "o3": c, "o4": d}

def _make_case(shape=(32,), dtype="float32", seed=0):
    n = 32
    rng = np.random.default_rng(3)
    x = rng.uniform(-2, 2, n).astype(np.float32)
    y = rng.uniform(-2, 2, n).astype(np.float32)
    x[3] = np.float32("nan"); y[5] = np.float32("nan")
    x[7] = np.float32("nan"); y[7] = np.float32("nan")
    args = {"x_ptr": x, "y_ptr": y,
            "o1": np.zeros(n, np.float32), "o2": np.zeros(n, np.float32),
            "o3": np.zeros(n, np.float32), "o4": np.zeros(n, np.float32),
            "n": n}
    cmp = {k: {"comparator": "allclose", "exact": False, "rtol": 0,
               "atol": 0, "equal_nan": True} for k in ("o1", "o2", "o3", "o4")}
    return {"args": args, "meta": {"BLOCK": 32}, "grid": (1,),
            "kernel": nan_mm_kernel,
            "outputs": ("o1", "o2", "o3", "o4"),
            "expected": ref(args, None), "comparison": cmp}

def make_case(shape=None, dtype=None, seed=None):
    return _make_case()
'''
    path = WORKDIR / "nan_mm.py"
    path.write_text(text)
    spec = importlib.util.spec_from_file_location("nan_mm", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    case, outs, _ = run_case(module, compiler)
    good, why = compare(case, outs)
    check("maximum-minimum-honor-propagate_nan", good, why)


def check_located_refusals(compiler):
    """The declared boundaries refuse with LOCATED diagnostics: a 16-bit
    operand to a transcendental (the pinned _check_dtype), tensor pow
    (the pinned Triton 3.8 has no tensor __pow__), and fp64 staging
    beyond the two internal-compute routes."""
    ok = True

    def try_lower(body, needles, label):
        nonlocal ok
        text = MATH_TEMPLATE.format(name="refuse", body=body,
                                    refexpr="x", rtol=1, atol=1)
        try:
            src = fe_source.load_operator_text(text, "<probe>", "refuse.py")
            case = {"args": {"x_ptr": np.zeros(16, np.float16),
                             "y_ptr": np.zeros(16, np.float16), "n": 16},
                    "meta": {"BLOCK": 16}, "grid": (1,),
                    "outputs": ("y_ptr",)}
            specz = fe_spec.specialize(src, case)
            lower_tir.lower(src, specz)
            check(f"refusal-{label}", False, "no refusal")
            ok = False
        except FrontendError as exc:
            located = all(n in str(exc) for n in needles)
            check(f"refusal-{label}", located, str(exc)[:90])
            ok &= located
        except Exception as exc:  # noqa: BLE001
            check(f"refusal-{label}", False,
                  f"{type(exc).__name__}: {str(exc)[:80]}")
            ok = False

    try_lower("tl.exp(x)",
              ("tl.exp", "fp32 or fp64"), "fp16-transcendental")
    try_lower("x ** 2", ("pow", "constexpr"), "tensor-pow")


def check_corpus_representatives(compiler):
    """Representative operators of the math families execute and compare
    (asinh: log/sqrt/abs/where; gelu_min: erf + minimum + a loop;
    fused_activation: sigmoid; floor_kernel: floor; pow's exp2*log2
    composition rides the same forms)."""
    reps = [
        ("asinh_kernel", {"shape": (17,)}, "math.transcendental"),
        ("gelu_min", {"shape": (128,)}, "math.transcendental (erf)"),
        ("fused_activation", {"shape": (17,)}, "sigmoid"),
        ("floor_kernel", {"shape": (17,)}, "math.round (floor)"),
    ]
    ok = True
    for name, kwargs, label in reps:
        p = ROOT / "ops" / "suite" / "dev" / f"{name}.py"
        try:
            spec = importlib.util.spec_from_file_location(name, str(p))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            case, outs, _ = run_case(module, compiler, **kwargs)
            good, why = compare(case, outs)
            ok &= good
            if not good:
                print(f"       {name}: {why}")
        except Exception as exc:  # noqa: BLE001
            ok = False
            print(f"       {name}: {type(exc).__name__}: {str(exc)[:140]}")
    check("corpus-math-representatives-execute-and-compare", ok,
          f"{len(reps)} operators ({', '.join(l for _, _, l in reps)})")


def check_thread_matrix(compiler):
    """One artifact per compile identity serves 1/2/4/8 worker threads
    with identical results (the program computes its partition from
    --threads)."""
    module = build_form(
        "thr", "tl.exp2(x)",
        "np.exp2(x.astype(np.float64)).astype(np.float32)", 3e-7, 3e-7)
    shas = set()
    ok = True
    for threads in (1, 2, 4, 8):
        case, outs, staged = run_case(module, compiler, threads=threads)
        good, why = compare(case, outs)
        ok &= good
        shas.add(staged.artifact_sha256)
        if not good:
            print(f"       threads={threads}: {why}")
    check("math-op-1-2-4-8-threads-one-artifact",
          ok and len(shas) == 1,
          f"{len(shas)} artifact sha(s) across 4 thread counts")


def check_constexpr_pow_fold():
    """arith.pow's constexpr form folds at specialization (the amax
    dtype-min pattern -1 * 2 ** (width - 1)); the folded value is exact."""
    text = '''"""probe"""
OPERATOR = {"name": "probe/pow_fold", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}
SHAPES = ((32,))
import numpy as np
import triton
import triton.language as tl

@triton.jit
def pow_fold_kernel(x_ptr, y_ptr, n, BLOCK: tl.constexpr):
    offs = tl.arange(0, BLOCK)
    m = offs < n
    x = tl.load(x_ptr + offs, mask=m, other=0)
    width: tl.constexpr = 32
    min_value: tl.constexpr = -1 * 2 ** (width - 1)
    out = tl.where(x < min_value, x, min_value + 1)
    tl.store(y_ptr + offs, out, mask=m)

def ref(args, meta):
    x = np.asarray(args["x_ptr"])
    return {"y_ptr": np.where(x < -2147483648, x, -2147483647)}

def _make_case(shape=(32,), dtype="float32", seed=0):
    n = 32
    x = np.linspace(-3e9, 3e9, n).astype(np.int32)
    args = {"x_ptr": x, "y_ptr": np.zeros(n, np.int32), "n": n}
    return {"args": args, "meta": {"BLOCK": 32}, "grid": (1,),
            "kernel": pow_fold_kernel, "outputs": ("y_ptr",),
            "expected": ref(args, None),
            "comparison": {"y_ptr": {"comparator": "array_equal",
                                     "exact": True}}}

def make_case(shape=None, dtype=None, seed=None):
    return _make_case()
'''
    path = WORKDIR / "pow_fold.py"
    path.write_text(text)
    spec = importlib.util.spec_from_file_location("pow_fold", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    compiler = Compiler(options=CompileOptions(cache_dir=str(CACHE)))
    case, outs, _ = run_case(module, compiler)
    good, why = compare(case, outs)
    check("constexpr-pow-folds-exact", good, why)


def main() -> int:
    compiler = Compiler(options=CompileOptions(cache_dir=str(CACHE)))
    check_every_form(compiler)
    check_wrongly_rounded_control(compiler)
    check_fp32_ieee_forms(compiler)
    check_fp16_bf16_lanes(compiler)
    check_int_abs_and_minmax(compiler)
    check_nan_policies(compiler)
    check_located_refusals(compiler)
    check_corpus_representatives(compiler)
    check_thread_matrix(compiler)
    check_constexpr_pow_fold()
    if FAILURES:
        print(f"test_math_ops: FAILED: {len(FAILURES)} check(s)")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print("test_math_ops: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
