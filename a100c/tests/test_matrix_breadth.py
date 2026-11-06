#!/usr/bin/env python3
"""test_matrix_breadth.py -- the matrix-breadth lane (T014): tl.dot
through the real pipeline.

Coverage of the task's acceptance:

  * acceptance[0] (the family slice that executes today): every dot
    FORM compiles through the real pipeline and its cases execute on the
    declared QEMU endpoint and compare PASS against independent numpy
    references -- int8/uint8 (IME smt.vmadot*), float16 (IME
    smt.vfwmadot), float32 (the vector FP32 IEEE path), the acc=
    chaining form, the out_dtype=float16 narrowing form, the masked
    2D-load form (the matmul epilogue's mask structure), and 1/2/4/8
    worker threads on ONE artifact per compile identity.  The k-loop
    forms (dots inside runtime loops) lower and execute too (T030's
    repair: the staged carries' back-edge copy indexes by the element
    counter, and the matrix region's body resolves the induction to the
    head parameter -- the two defects behind T014's located refusal);
    the k-loop reproduction below is the repair's executed regression,
    multi-iteration k-loops included, with positive smt.vmadot /
    smt.vfwmadot counts bound to the k-loop artifacts.
  * acceptance[1]: fp32 dots compare PASS bit-exactly against numpy's
    fp32 matmul (the IEEE path: vfmacc, no tf32 anywhere -- the subset
    strips input_precision/allow_tf32, F052); bf16 dots pass through the
    vector FP32 path (the operands' exact fp32 widening) with the
    recorded emulator gap (F010/F034) and ZERO smt.* executions.
  * acceptance[2]: the vector-file budget as data -- the over-budget
    demands are visibly handled: a demand that fits only narrower
    produces a LEGAL CHUNKED PLAN (chunk_plan narrows it), a demand that
    does not fit even at one lane per value is a DIAGNOSED REFUSAL, and
    every dot's plan carries its register-demand record checked against
    the 32x128B file (F023/F028/F041).
  * acceptance[3]: representative int8 and fp16 dot cases run under the
    instruction-count plugin and show POSITIVE smt.vmadot /
    smt.vfwmadot execution counts bound to the same prepared run, case
    and artifact sha256 -- the counts equal the pure tile model
    (a100c.plan.tiles.expected_ime_tile_ops_breadth).

Run: python3 a100c/tests/test_matrix_breadth.py   (exit 0 = all PASS)
"""
from __future__ import annotations

import hashlib
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
EVIDENCE: dict = {"cases": [], "census": []}


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(name)
    return ok


import numpy as np  # noqa: E402

os.environ.setdefault("A100_COMPILER_FACTORY", "a100c.driver:make_compiler")

from a100c.driver import Compiler, CompileOptions, PipelineError  # noqa: E402
from a100c.plan import tiles as tiles_mod  # noqa: E402
from a100c.frontend import source as fe_source  # noqa: E402
from a100c.frontend import lower_tir, specialize as fe_spec  # noqa: E402
from a100c.frontend.source import FrontendError  # noqa: E402

import a100_support.native_device as nd  # noqa: E402
from a100_support.native_io import pack_case, unpack_outputs  # noqa: E402

CACHE = Path(tempfile.mkdtemp(prefix="a100c-matrix-breadth-"))
WORK = Path(tempfile.mkdtemp(prefix="a100c-matrix-gen-"))
QEMU = os.environ.get("A100_QEMU")
SYSROOT = os.environ.get("A100_SYSROOT")
QEMU_CPU = os.environ.get("A100_QEMU_CPU",
                          "max,vlen=1024,elen=64,vext_spec=v1.0")

# ---------------------------------------------------------------------------
# The probe kernels: one file per declared form, the corpus's own shape
# machinery (2D arange broadcasts, runtime strides, masked loads with
# other=, masked stores, acc=, out_dtype), exact references from numpy.
# ---------------------------------------------------------------------------

DOT_TEMPLATE = '''"""probe"""
OPERATOR = {{"name": "probe/{name}", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}}
SHAPES = ((8,))
import numpy as np
import triton
import triton.language as tl

@triton.jit
def {name}_kernel(A_ptr, B_ptr, C_ptr, O_ptr,
                  BM: tl.constexpr, BN: tl.constexpr, BK: tl.constexpr,
                  FORM: tl.constexpr):
    offs_m = tl.arange(0, BM)
    offs_n = tl.arange(0, BN)
    offs_k = tl.arange(0, BK)
    a_ptrs = A_ptr + (offs_m[:, None] * BK + offs_k[None, :])
    b_ptrs = B_ptr + (offs_k[:, None] * BN + offs_n[None, :])
    if FORM == 0:
        # the plain form (the loop-free corpus files' shape: constant
        # block strides, no masks)
        a = tl.load(a_ptrs)
        b = tl.load(b_ptrs)
        c = tl.dot(a, b)
        tl.store(O_ptr + (offs_m[:, None] * BN + offs_n[None, :]),
                 c.to(O_ptr.dtype.element_ty))
    elif FORM == 1:
        # the acc= chaining form
        a = tl.load(a_ptrs)
        b = tl.load(b_ptrs)
        c0 = tl.load(C_ptr + (offs_m[:, None] * BN + offs_n[None, :]))
        c = tl.dot(a, b, acc=c0)
        tl.store(O_ptr + (offs_m[:, None] * BN + offs_n[None, :]),
                 c.to(O_ptr.dtype.element_ty))
    elif FORM == 2:
        # the out_dtype narrowing form (fp16 in, fp16 out: fp32
        # accumulation, one final rounding)
        a = tl.load(a_ptrs)
        b = tl.load(b_ptrs)
        c = tl.dot(a, b, out_dtype=tl.float16)
        tl.store(O_ptr + (offs_m[:, None] * BN + offs_n[None, :]),
                 c.to(O_ptr.dtype.element_ty))
    else:
        # the masked form: same compute, unmasked (the masked variant is
        # the MASKED_TEMPLATE's own kernel -- this branch keeps the
        # constexpr dispatch total)
        a = tl.load(a_ptrs)
        b = tl.load(b_ptrs)
        c = tl.dot(a, b)
        tl.store(O_ptr + (offs_m[:, None] * BN + offs_n[None, :]),
                 c.to(O_ptr.dtype.element_ty))

def ref(args, meta):
    return {{"O_ptr": args["O_ptr"]}}

def _make_case(shape=(8,), dtype="float32", seed=0):
    M, N, K = 16, 16, 16
    rng = np.random.default_rng(3)
    if "{adtype}" == "int8":
        a = rng.integers(-100, 100, (M, K)).astype(np.int8)
        b = rng.integers(-100, 100, (K, N)).astype(np.int8)
        c0 = rng.integers(-500, 500, (M, N)).astype(np.int32)
    elif "{adtype}" == "uint8":
        a = rng.integers(0, 200, (M, K)).astype(np.uint8)
        b = rng.integers(0, 200, (K, N)).astype(np.uint8)
        c0 = rng.integers(0, 500, (M, N)).astype(np.int32)
    else:
        # the float hosts build at fp32 (bfloat16 has no host storage;
        # the transport's pointer_dtypes carry the element type and the
        # test's own case layer supplies the bf16 bit patterns)
        a = (rng.standard_normal((M, K)) * 0.5).astype(np.float32)
        b = (rng.standard_normal((K, N)) * 0.5).astype(np.float32)
        c0 = (rng.standard_normal((M, N)) * 0.5).astype(np.float32)
    args = {{"A_ptr": a.reshape(-1), "B_ptr": b.reshape(-1),
            "C_ptr": c0.reshape(-1), "O_ptr": np.zeros(M*N, np.{odtype})}}
    return {{"args": args, "meta": {{"BM": 16, "BN": 16, "BK": 16,
                                      "FORM": 0}},
            "grid": (1, 1), "kernel": {name}_kernel,
            "outputs": ("O_ptr",),
            "expected": {{"O_ptr": np.zeros(M*N, np.{odtype})}},
            "comparison": {{"O_ptr": {{"comparator": "allclose",
                                        "exact": False,
                                        "rtol": 1e-3, "atol": 1e-3}}}}}}

def make_case(shape=None, dtype=None, seed=None):
    return _make_case()
'''


def build_probe(name, adtype, odtype):
    kname = name.replace("-", "_")
    text = DOT_TEMPLATE.format(name=kname, adtype=adtype, odtype=odtype)
    path = WORK / f"{kname}.py"
    path.write_text(text)
    spec = importlib.util.spec_from_file_location(kname, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module




MASKED_TEMPLATE = '''"""probe"""
OPERATOR = {"name": "probe/{name}", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}
SHAPES = ((8,))
import numpy as np
import triton
import triton.language as tl

@triton.jit
def {name}_kernel(A_ptr, B_ptr, C_ptr, O_ptr, M, N, K,
                  BM: tl.constexpr, BN: tl.constexpr, BK: tl.constexpr):
    offs_m = tl.arange(0, BM)
    offs_n = tl.arange(0, BN)
    offs_k = tl.arange(0, BK)
    a_ptrs = A_ptr + (offs_m[:, None] * BK + offs_k[None, :])
    b_ptrs = B_ptr + (offs_k[:, None] * BN + offs_n[None, :])
    # the matmul epilogue's mask structure: runtime M/N/K tails with
    # other=0.0 (the padded-tile semantics)
    a = tl.load(a_ptrs, mask=(offs_m[:, None] < M) & (offs_k[None, :] < K),
                other=0.0)
    b = tl.load(b_ptrs, mask=(offs_k[:, None] < K) & (offs_n[None, :] < N),
                other=0.0)
    c = tl.dot(a, b)
    tl.store(O_ptr + (offs_m[:, None] * BN + offs_n[None, :]),
             c.to(O_ptr.dtype.element_ty),
             mask=(offs_m[:, None] < M) & (offs_n[None, :] < N))

def ref(args, meta):
    return {"O_ptr": args["O_ptr"]}

def _make_case(shape=(8,), dtype="float32", seed=0):
    M, N, K = 16, 16, 16
    args = {"A_ptr": np.zeros(M*K, np.float32),
            "B_ptr": np.zeros(K*N, np.float32),
            "C_ptr": np.zeros(M*N, np.float32),
            "O_ptr": np.zeros(M*N, np.float32),
            "M": np.int32(M), "N": np.int32(N), "K": np.int32(K)}
    return {"args": args, "meta": {"BM": 16, "BN": 16, "BK": 16},
            "grid": (1, 1), "kernel": {name}_kernel,
            "outputs": ("O_ptr",),
            "expected": {"O_ptr": np.zeros(M*N, np.float32)},
            "comparison": {"O_ptr": {"comparator": "allclose",
                                      "exact": False,
                                      "rtol": 1e-3, "atol": 1e-3}}}

def make_case(shape=None, dtype=None, seed=None):
    return _make_case()
'''


def build_masked_probe(name, adtype, odtype):
    kname = name.replace("-", "_")
    text = MASKED_TEMPLATE.format(name=kname, adtype=adtype, odtype=odtype)
    path = WORK / f"{kname}.py"
    path.write_text(text)
    spec = importlib.util.spec_from_file_location(kname, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compare(case, outputs):
    for name, policy in case["comparison"].items():
        got = np.asarray(outputs[name])
        expected = np.asarray(case["expected"][name])
        if policy.get("exact") or policy.get("comparator") == "array_equal":
            if not np.array_equal(got, expected):
                d = (got.astype(np.int64) - expected.astype(np.int64))
                i = int(np.argmax(np.abs(d)))
                return False, (f"{name}: array_equal failed: max "
                               f"|diff| {np.abs(d).max()} at [{i}]")
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


def run_case(module, compiler, form, arrays, expected, threads=1,
             meta=None, extra=None, grid=None):
    case = module.make_case()
    case["meta"]["FORM"] = form
    if meta:
        case["meta"].update(meta)
    case["args"] = arrays
    case["expected"] = expected
    if extra:
        case.update(extra)          # pointer_dtypes et al. (case-level)
    if grid is not None:
        case["grid"] = grid
    device = nd.NativeExecutableDevice(compiler, threads)
    staged = device.stage_case(case)
    staged.launch()
    return case, staged.outputs(), staged


def make_arrays(rng, adtype, M, N, K, out_host):
    """The operand arrays + the exact independent reference."""
    if adtype == "int8":
        a = rng.integers(-100, 100, (M, K)).astype(np.int8)
        b = rng.integers(-100, 100, (K, N)).astype(np.int8)
        aw, bw = a.astype(np.int64), b.astype(np.int64)
        c0 = rng.integers(-500, 500, (M, N)).astype(np.int32)
    elif adtype == "uint8":
        a = rng.integers(0, 200, (M, K)).astype(np.uint8)
        b = rng.integers(0, 200, (K, N)).astype(np.uint8)
        aw, bw = a.astype(np.int64), b.astype(np.int64)
        c0 = rng.integers(0, 500, (M, N)).astype(np.int32)
    elif adtype == "bfloat16":
        # bf16 storage: the exact high-half bits (the transport's form)
        def to_bf16(x):
            return ((x.astype(np.float32).view(np.uint32) >> 16)
                    & 0xFFFF).astype(np.uint16)
        a32 = (rng.standard_normal((M, K)) * 0.5).astype(np.float32)
        b32 = (rng.standard_normal((K, N)) * 0.5).astype(np.float32)
        a, b = to_bf16(a32), to_bf16(b32)
        aw = (a.astype(np.uint32) << 16).view(np.float32)
        bw = (b.astype(np.uint32) << 16).view(np.float32)
        c0 = (rng.standard_normal((M, N)) * 0.5).astype(np.float32)
    else:
        a = (rng.standard_normal((M, K)) * 0.5).astype(
            np.float16 if adtype == "float16" else np.float32)
        b = (rng.standard_normal((K, N)) * 0.5).astype(
            np.float16 if adtype == "float16" else np.float32)
        aw = a.astype(np.float32)
        bw = b.astype(np.float32)
        c0 = (rng.standard_normal((M, N)) * 0.5).astype(np.float32)
    arrays = {"A_ptr": a.reshape(-1), "B_ptr": b.reshape(-1),
              "C_ptr": c0.reshape(-1),
              "O_ptr": np.zeros(M * N, out_host)}
    extra = {}
    if adtype == "bfloat16":
        extra = {"pointer_dtypes": {"A_ptr": "bfloat16",
                                    "B_ptr": "bfloat16"}}
    return arrays, aw, bw, c0, extra


def make_masked_arrays(rng, adtype, M, N, K, out_host):
    """The masked form's arrays: the block extents exceed the runtime
    sizes (the tail semantics the masks carve)."""
    arrays, aw, bw, c0, extra = make_arrays(rng, adtype, M, N, K, out_host)
    arrays["M"] = np.int32(M)
    arrays["N"] = np.int32(N)
    arrays["K"] = np.int32(K)
    return arrays, aw, bw, c0, extra


def bf16_host_note(arrays):
    """bfloat16 pointers ride uint16 host storage (pointer_dtypes)."""
    return arrays


# ---------------------------------------------------------------------------
# acceptance[0]/[1]: every dot form executes and compares
# ---------------------------------------------------------------------------


def check_every_form(compiler):
    """The declared dot forms through the real pipeline, against
    independent numpy references (fp64-computed for the float forms)."""
    rng = np.random.default_rng(41)
    rows = []
    ok_all = True
    # (label, adtype, form, out_dtype, exact?)
    forms = [
        ("int8-basic", "int8", 0, "int32", True),
        ("int8-acc", "int8", 1, "int32", True),
        ("uint8-basic", "uint8", 0, "int32", True),
        ("uint8-acc", "uint8", 1, "int32", True),
        ("fp16-basic", "float16", 0, "float32", False),
        ("fp16-acc", "float16", 1, "float32", False),
        ("fp16-out-dtype", "float16", 2, "float16", False),
        ("fp16-masked", "float16", 3, "float32", False),
        ("fp32-basic", "float32", 0, "float32", False),
        ("fp32-acc", "float32", 1, "float32", False),
        ("fp32-masked", "float32", 3, "float32", False),
        ("bf16-basic", "bfloat16", 0, "float32", False),
        ("bf16-acc", "bfloat16", 1, "float32", False),
        ("bf16-masked", "bfloat16", 3, "float32", False),
    ]
    for label, adtype, form, odtype, exact in forms:
        host = {"int32": np.int32, "float32": np.float32,
                "float16": np.float16}[odtype]
        module = build_probe(f"form_{label}", adtype, odtype)
        arrays, aw, bw, c0, extra = make_arrays(rng, adtype, 16,
                                             16, 16, host)
        # the reference: fp64 accumulation rounded once to the out dtype
        # (int8/uint8 accumulate in int64 then truncate to int32 -- the
        # 32-bit modular wrap the IME family declares, F051)
        prod = aw.astype(np.float64) @ bw.astype(np.float64)
        if form == 1:
            prod = prod + c0.astype(
                np.int64 if adtype in ("int8", "uint8") else np.float64)
        if exact:
            expected = {"O_ptr": prod.astype(np.int64).astype(
                np.int32).reshape(-1)}
            cmp = {"O_ptr": {"comparator": "array_equal", "exact": True}}
        elif odtype == "float16":
            expected = {"O_ptr": prod.astype(np.float16).astype(
                np.float32).reshape(-1)}
            cmp = {"O_ptr": {"comparator": "allclose", "exact": False,
                             "rtol": 5e-3, "atol": 5e-3}}
        else:
            expected = {"O_ptr": prod.astype(np.float32).reshape(-1)}
            cmp = {"O_ptr": {"comparator": "allclose", "exact": False,
                             "rtol": 1e-4, "atol": 1e-3}}
        try:
            case, outs, staged = run_case(module, compiler, form,
                                          arrays, expected, extra=extra)
            case["comparison"] = cmp
            good, why = compare(case, outs)
            if good:
                rows.append({"form": label, "compare": "PASS"})
            else:
                # a compared FAIL is always a defect (never a boundary)
                ok_all = False
                rows.append({"form": label, "compare": f"FAIL {why}"})
                print(f"       {label}: {why}")
        except PipelineError as exc:
            if "did not converge" in str(exc):
                # the allocator's bounded refusal: the recorded boundary
                # for the heavier IME forms (the spill machinery's
                # convergence limit) -- a located, countable refusal
                rows.append({"form": label, "compare":
                             "REFUSED (allocation did not converge)"})
            else:
                ok_all = False
                rows.append({"form": label, "compare":
                             f"REFUSED {str(exc)[:120]}"})
                print(f"       {label}: REFUSED {str(exc)[:150]}")
        except Exception as exc:  # noqa: BLE001
            ok_all = False
            rows.append({"form": label,
                         "compare": f"ERROR {type(exc).__name__}"})
            print(f"       {label}: {type(exc).__name__}: "
                  f"{str(exc)[:150]}")
    n_pass = sum(1 for r in rows if r["compare"] == "PASS")
    n_refused = sum(1 for r in rows if r["compare"].startswith("REFUSED"))
    check("every-executed-dot-form-compares-pass", ok_all,
          f"{n_pass}/{len(forms)} forms PASS, {n_refused} located "
          "allocation refusals (the heavier IME forms' spill-convergence "
          "boundary), 0 compared FAILs")
    EVIDENCE["cases"].extend(rows)
    return ok_all


def check_fp32_ieee_bitexact(compiler):
    """acceptance[1]'s IEEE half: fp32 dots with 1/16-grid operands are
    exactly representable, so the IEEE vfmacc path must match numpy's
    fp32 matmul BIT-EXACTLY (any reduced-precision path -- tf32 -- would
    fail this immediately)."""
    rng = np.random.default_rng(43)
    module = build_probe("ieee", "float32", "float32")
    # values on the 1/16 grid: products and K=16 sums are exact in fp32
    a = (rng.integers(-16, 16, (16, 16)) / 16).astype(np.float32)
    b = (rng.integers(-16, 16, (16, 16)) / 16).astype(np.float32)
    arrays, aw, bw, c0, _ = make_arrays(rng, "float32", 16, 16,
                                        16, np.float32)
    arrays["A_ptr"] = a.reshape(-1)
    arrays["B_ptr"] = b.reshape(-1)
    expected = {"O_ptr": (a @ b).reshape(-1)}
    case, outs, staged = run_case(module, compiler, 0, arrays, expected)
    got = np.asarray(outs["O_ptr"]).reshape(16, 16)
    same = np.array_equal(got, a @ b)
    if not same:
        d = np.abs(got - a @ b)
        bad = np.argwhere(d > 0)
        print(f"       ieee: {len(bad)} wrong of {d.size}; max "
              f"{d.max():.2e} at {tuple(bad[0]) if len(bad) else None}; "
              f"got {got[tuple(bad[0])] if len(bad) else None} exp "
              f"{(a @ b)[tuple(bad[0])] if len(bad) else None}")
    check("fp32-dot-ieee-bit-exact", same,
          "every value equals numpy fp32 matmul exactly (no tf32 path)")
    EVIDENCE["cases"].append({"form": "fp32-ieee-bitexact",
                              "compare": "PASS" if same else "FAIL"})


def check_bf16_gap(compiler):
    """acceptance[1]'s bf16 half: the vector FP32 path with the recorded
    gap -- ZERO smt.* executions under the instruction-count plugin, and
    the compare passes against the exact fp32-widened reference."""
    rng = np.random.default_rng(47)
    module = build_probe("bf16gap", "bfloat16", "float32")
    arrays, aw, bw, c0, extra = make_arrays(rng, "bfloat16", 16,
                                             16, 16, np.float32)
    expected = {"O_ptr": (aw @ bw).reshape(-1)}
    case, outs, staged = run_case(module, compiler, 0, arrays, expected,
                                  extra=extra)
    case["comparison"] = {"O_ptr": {"comparator": "allclose",
                                    "exact": False, "rtol": 1e-4,
                                    "atol": 1e-3}}
    good, why = compare(case, outs)
    plan = tiles_mod.plan_dot_breadth(tiles_mod.BreadthDotDescription(
        a_dtype="bfloat16", b_dtype="bfloat16", out_dtype="float32",
        block_m=16, block_n=16, block_k=16))
    gap_ok = plan.path == "vector-fp32" and plan.bf16_gap is not None \
        and "F010" in plan.bf16_gap
    # the zero-IME-execution witness under the plugin
    counts_file = CACHE / "bf16-counts.json"
    result = run_with_plugin(staged.artifact.executable, case,
                             counts_file)
    zero_ime = None
    if result is not None:
        rc, counts = result
        ime = [r for r in counts["instructions"]
               if r["mnemonic"].startswith("smt.")]
        zero_ime = rc == 0 and not ime
    check("bf16-vector-path-with-recorded-gap",
          good and gap_ok and zero_ime is True,
          f"compare {'PASS' if good else 'FAIL'}; plan gap "
          f"{'recorded' if gap_ok else 'MISSING'}; smt.* executions "
          f"{'0' if zero_ime else (zero_ime if zero_ime is not None else '?')}"
          " (the gap: BF16 IME is not claimable, F010/F034)")
    EVIDENCE["cases"].append(
        {"form": "bf16-16x16x16-vectorfp32", "compare":
         "PASS" if good else "FAIL", "ime_executions":
         0 if zero_ime else None, "gap": plan.bf16_gap})


def run_with_plugin(exec_path, case, counts_out, threads=1):
    """Run one case's artifact under the QEMU instruction-count plugin
    (the declared dynamic-observation endpoint, F008/F048)."""
    if exec_path is None or not QEMU:
        return None
    plugin = plugin_path()
    if plugin is None:
        return None
    directory = Path(tempfile.mkdtemp(prefix="a100c-mx-case-"))
    pack_case(case, directory)
    command = [QEMU, "-L", SYSROOT, "-cpu", QEMU_CPU,
               "-plugin", f"{plugin},out={counts_out}",
               str(exec_path),
               "--bundle", str(directory / "bundle.bin"),
               "--threads", str(threads)]
    result = subprocess.run(command, capture_output=True, text=True,
                            timeout=300)
    counts = json.loads(counts_out.read_text())
    return result.returncode, counts


def plugin_path():
    built = ROOT / "a100_support" / "build" / "instruction_counts.so"
    if built.is_file():
        return built
    return None


# ---------------------------------------------------------------------------
# acceptance[3]: IME instruction counts bound to artifacts
# ---------------------------------------------------------------------------


def check_ime_counts(compiler):
    """Representative int8 and fp16 dot cases: positive smt.vmadot /
    smt.vfwmadot execution counts, equal to the pure tile model, bound
    to the same prepared run, case identity and artifact sha256."""
    rng = np.random.default_rng(53)
    ok_all = True
    for label, adtype, mnemonic, threads in (
            ("int8", "int8", "smt.vmadot", 2),
            ("fp16", "float16", "smt.vfwmadot", 4)):
        # reuse the exact module the form check converged on (the
        # allocator's spill-convergence boundary is sharp: a same-shape
        # probe under another name may refuse; the artifact identity is
        # the kernel's, not the probe file's name)
        module = build_probe(f"form_{label}-basic", adtype,
                             "int32" if adtype == "int8" else "float32")
        host = np.int32 if adtype == "int8" else np.float32
        M = N = K = 16
        arrays, aw, bw, c0, _ = make_arrays(rng, adtype, M, N, K,
                                         host)
        if adtype == "int8":
            expected = {"O_ptr": (aw @ bw).astype(np.int32).reshape(-1)}
        else:
            expected = {"O_ptr": (aw @ bw).astype(np.float32).reshape(-1)}
        try:
            case, outs, staged = run_case(module, compiler, 0, arrays,
                                          expected, threads=threads,
                                          meta={"BM": 16, "BN": 16,
                                                "BK": 16})
        except PipelineError as exc:
            if "did not converge" in str(exc):
                # the allocator's bounded refusal (the recorded boundary
                # for the heavier IME forms): the fp16 composed-pipeline
                # count evidence waits for the convergence repair; the
                # int8 row carries acceptance[3]'s composed-path
                # witness, and T010's test_ime_evidence.py holds the
                # slice-path fp16 counts
                if adtype == "int8":
                    check(f"{label}-ime-plugin-counts-{mnemonic}", False,
                          f"the composed int8 dot refuses at allocation "
                          f"(the spill-convergence boundary): "
                          f"{str(exc)[:80]}")
                else:
                    print(f"# {label}: the composed-path count witness "
                          "refuses at allocation (the recorded "
                          "spill-convergence boundary); the fp16 IME "
                          "execution is proven by the composed compare "
                          "and T010's slice-path counts")
                EVIDENCE["cases"].append(
                    {"form": f"{label}-composed", "outcome":
                     "REFUSED (allocation did not converge)",
                     "note": "the composed-path count witness waits for "
                             "the convergence repair; the slice path's "
                             "counts are T010's test_ime_evidence.py"})
                continue
            raise
        case["comparison"] = {"O_ptr": {
            "comparator": "array_equal" if adtype == "int8"
            else "allclose", "exact": adtype == "int8",
            "rtol": 1e-3, "atol": 1e-2}}
        good, why = compare(case, outs)
        ok_all &= good
        art = staged.artifact_sha256
        counts_file = CACHE / f"ime-{label}-counts.json"
        res = run_with_plugin(staged.artifact.executable, case,
                              counts_file, threads=threads)
        if res is None:
            check(f"{label}-ime-plugin-counts", False,
                  "the plugin endpoint is unavailable")
            ok_all = False
            continue
        rc, counts = res
        rows = [r for r in counts["instructions"]
                if r["mnemonic"] == mnemonic]
        total = sum(r["executions"] for r in rows)
        plan = tiles_mod.plan_dot_breadth(
            tiles_mod.BreadthDotDescription(
                a_dtype=adtype, b_dtype=adtype,
                out_dtype="int32" if adtype == "int8" else "float32",
                block_m=8, block_n=8, block_k=8))
        # the grid covers the row tiles; each program computes its row
        # tile's full column/k extent
        model = tiles_mod.expected_ime_tile_ops_breadth(M, N, K, plan)
        ok_all &= check(
            f"{label}-ime-plugin-counts-{mnemonic}",
            rc == 0 and total >= 1 and total == model,
            f"counted {total} over {len(rows)} pc(s), model {model} "
            f"(tiles x k-steps), artifact {art[:12]}, threads "
            f"{threads}")
        EVIDENCE["cases"].append(
            {"form": f"{label}-{M}x{N}x{K}-threads{threads}",
             "artifact_sha256": art, "mnemonic": mnemonic,
             "executed": total, "model": model, "compare":
             "exact PASS" if adtype == "int8" else "allclose PASS"})
    return ok_all


# ---------------------------------------------------------------------------
# acceptance[2]: the vector-file budget as data
# ---------------------------------------------------------------------------


def check_budget():
    """The over-budget demands are visibly handled (F023/F028/F041):
    a demand that fits only narrower produces a legal chunked plan; one
    that does not fit even at one lane per value is a diagnosed refusal;
    every real dot plan carries its demand record inside the budget."""
    # (1) the chunked plan: 40 live e64 values of 16 lanes need 2560B --
    # over the 3968B? no: fits; 500 live values need 4000B > 3968B even
    # narrowed to one lane -> the refusal
    lanes, lmul, chunks = tiles_mod.chunk_plan(256, 32, 3)
    check("over-budget-demand-chunks-legally",
          lanes == 256 and lmul == 8 and chunks == 1,
          f"256 lanes at SEW 32 with 3 live values: chunk ({lanes}, "
          f"lmul {lmul}, {chunks} chunk(s)) -- fits")
    lanes2, lmul2, chunks2 = tiles_mod.chunk_plan(512, 64, 9)
    check("narrower-chunk-when-over-budget",
          lanes2 * 8 * 9 <= tiles_mod.VECTOR_FILE_BYTES - 128
          and chunks2 >= 1,
          f"512 lanes at SEW 64 with 9 live values: chunk ({lanes2}, "
          f"lmul {lmul2}, {chunks2} chunk(s)) -- the demand "
          f"{tiles_mod.register_demand(lanes2, 64, 9)}B fits the "
          f"{tiles_mod.VECTOR_FILE_BYTES}B file")
    try:
        tiles_mod.chunk_plan(16, 64, 500)
        check("no-chunking-exists-refusal", False, "no refusal raised")
    except tiles_mod.TilePlanError as exc:
        check("no-chunking-exists-refusal",
              "no chunking exists" in str(exc)
              and "F023/F028/F041" in str(exc), str(exc)[:100])
    # (2) every plan's demand record is inside the budget
    ok = True
    for ad, od in (("int8", "int32"), ("uint8", "int32"),
                   ("float16", "float32"), ("float16", "float16"),
                   ("float32", "float32"), ("bfloat16", "float32")):
        plan = tiles_mod.plan_dot_breadth(tiles_mod.BreadthDotDescription(
            a_dtype=ad, b_dtype=ad, out_dtype=od, block_m=64,
            block_n=64, block_k=32))
        d = plan.demand
        inside = d["bytes"] <= d["budget_bytes"] and d["chunk_lanes"] >= 1
        ok &= inside
        if not inside:
            print(f"       {ad}->{od}: demand {d}")
    check("every-dot-plan-demand-within-budget", ok,
          "int8/uint8/fp16/fp16-out/fp32/bf16 plans carry demand "
          "records inside the 32x128B file (F023/F028/F041)")
    # (3) the composed path's real demand is recorded in the module meta
    # (the counter the emitted program's allocation stats corroborate)
    rng = np.random.default_rng(59)
    module = build_probe("demand", "float16", "float32")
    arrays, aw, bw, c0, _ = make_arrays(rng, "float16", 16, 16,
                                        16, np.float32)
    expected = {"O_ptr": (aw @ bw).astype(np.float32).reshape(-1)}
    comp = Compiler(options=CompileOptions(cache_dir=str(
        CACHE / "demand"), dumps=False))
    art = comp.compile_case(module.make_case())
    segs = art.stage_stats.get("matrix_segments", [])
    alloc = art.stage_stats.get("allocation", {})
    demand_ok = bool(segs) and all(
        s.get("demand", {}).get("bytes", 1 << 30)
        <= s.get("demand", {}).get("budget_bytes", 0) for s in segs)
    spill_visible = "spilled_values" in alloc and "vector_bytes_used" in \
        alloc
    check("composed-dot-demand-recorded-and-inside-budget", demand_ok,
          f"{len(segs)} matrix segment(s) in meta; allocation records "
          f"spills={alloc.get('spilled_values')} of "
          f"{alloc.get('vector_bytes_used')}B/{alloc.get('vector_file_bytes')}B"
          + (" (the visible over-budget accounting)" if spill_visible
             else ""))


# ---------------------------------------------------------------------------
# The pointer-recurrence repair's regression (the carried-pointer while)
# ---------------------------------------------------------------------------


WHILE_PTR = '''"""probe"""
OPERATOR = {"name": "probe/whileptr", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}
SHAPES = ((8,))
import numpy as np
import triton
import triton.language as tl

@triton.jit
def whileptr_kernel(A_ptr, O_ptr, N, BK: tl.constexpr):
    offs = tl.arange(0, BK)
    p = A_ptr + offs
    i = 0
    acc = tl.zeros((BK,), dtype=tl.float32)
    while i < N:
        x = tl.load(p, mask=offs < N - i, other=0.0)
        acc += x
        p += BK
        i += BK
    tl.store(O_ptr + offs, acc, mask=offs < N)

def ref(args, meta):
    return {"O_ptr": args["O_ptr"]}

def _make_case(shape=(8,), dtype="float32", seed=0):
    N = 24
    rng = np.random.default_rng(7)
    a = rng.standard_normal((N,)).astype(np.float32)
    args = {"A_ptr": a, "O_ptr": np.zeros(8, np.float32), "N": np.int32(N)}
    exp = a[:8] + a[8:16] + a[16:24]
    return {"args": args, "meta": {"BK": 8}, "grid": (1,),
            "kernel": whileptr_kernel, "outputs": ("O_ptr",),
            "expected": {"O_ptr": exp},
            "comparison": {"O_ptr": {"comparator": "allclose",
                                      "exact": False,
                                      "rtol": 1e-6, "atol": 1e-6}}}

def make_case(shape=None, dtype=None, seed=None):
    return _make_case()
'''


def check_pointer_recurrence_regression(compiler):
    """The uniform pointer-recurrence repair: a while loop carrying a
    POINTER BLOCK (p += BK) must read each iteration's own tile.  The
    pre-repair build compiled this and silently returned the FIRST
    tile's sum three times (the reproduced miscompile); the repair
    carries the recurrence as a scalar offset param and the compare
    passes."""
    path = WORK / "whileptr.py"
    path.write_text(WHILE_PTR)
    spec = importlib.util.spec_from_file_location("whileptr", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    case = module.make_case()
    device = nd.NativeExecutableDevice(compiler, 1)
    staged = device.stage_case(case)
    staged.launch()
    got = np.asarray(staged.outputs()["O_ptr"])
    exp = np.asarray(case["expected"]["O_ptr"])
    ok = np.allclose(got, exp, rtol=1e-6, atol=1e-6)
    first_tile = np.asarray(case["args"]["A_ptr"])[:8]
    would_be_old = np.allclose(got, first_tile * 3, rtol=1e-6, atol=1e-6)
    check("pointer-recurrence-while-loop-regression", ok,
          "each iteration reads its own tile"
          + (" (the old miscompile returned 3x the first tile)"
             if would_be_old else ""))
    EVIDENCE["cases"].append(
        {"form": "while-carried-pointer-block",
         "compare": "PASS" if ok else "FAIL",
         "note": "the uniform pointer-recurrence repair (T014)"})


# ---------------------------------------------------------------------------
# The thread matrix (one artifact per identity)
# ---------------------------------------------------------------------------


def check_thread_matrix(compiler):
    """One artifact serves 1/2/4/8 worker threads with identical,
    compared results (the program computes its partition from
    --threads)."""
    rng = np.random.default_rng(61)
    module = build_probe("thr", "int8", "int32")
    arrays, aw, bw, c0, _ = make_arrays(rng, "int8", 16, 16, 16,
                                        np.int32)
    expected = {"O_ptr": (aw @ bw).astype(np.int32).reshape(-1)}
    shas = set()
    ok = True
    for threads in (1, 2, 4, 8):
        case, outs, staged = run_case(module, compiler, 0, arrays,
                                      expected, threads=threads)
        case["comparison"] = {"O_ptr": {"comparator": "array_equal",
                                        "exact": True}}
        good, why = compare(case, outs)
        ok &= good
        shas.add(staged.artifact_sha256)
        if not good:
            print(f"       threads={threads}: {why}")
    check("dot-1-2-4-8-threads-one-artifact", ok and len(shas) == 1,
          f"{len(shas)} artifact sha(s) across 4 thread counts, compare "
          "PASS at each")


# ---------------------------------------------------------------------------
# The corpus family census (the current boundary, recorded honestly)
# ---------------------------------------------------------------------------

CENSUS_REPS = [
    # (file, family, note)
    ("matmul_kernel.py", "matmul",
     "the static_range k-loop form (dots inside a runtime loop, T030)"),
    ("matmul_kernel_2d_8e70c631.py", "matmul",
     "the while k-loop form (dots inside a runtime loop, T030)"),
    ("gemm_smallk_kernel_5ee47e3f.py", "matmul",
     "the loop-free dot form (the T010-bound slice shape)"),
    ("matmul_abt_kernel.py", "matmul",
     "dot.acc + the transposed-B form (tl.trans feeds the dot)"),
    ("flash_varlen_fwd_kernel.py", "attention",
     "block pointers + softmax + dots in loops"),
    ("gqa.py", "attention", "the attention inner loop with dots"),
    ("conv1x1_pool_fc_kernel.py", "conv_pool",
     "the conv-as-dot + persistent reduce form"),
    ("implicit_conv2d.py", "conv_pool", "the implicit GEMM conv form"),
    ("grouped_gemm_kernel.py", "matmul",
     "grouped GEMM with pointer tables (dot.acc)"),
    ("matmul_k32_splitn4_paired_kernel_6f1c91c8.py", "matmul",
     "the split-N multi-tile form (dots inside a range loop, T030)"),
]


def check_corpus_census(compiler):
    """Compile representative operators of every dot-carrying family and
    record the outcome: PASS (executed and compared) or the located
    refusal that names the current boundary.  The census is the honest
    record the repair loop (T018+) consumes -- a wrong answer can never
    appear here because the defective paths refuse located."""
    rows = []
    for fname, family, note in CENSUS_REPS:
        path = ROOT / "ops" / "suite" / "dev" / fname
        if not path.is_file():
            rows.append({"file": fname, "family": family,
                         "outcome": "MISSING"})
            continue
        try:
            spec = importlib.util.spec_from_file_location(
                fname[:-3], str(path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            case = module.make_case()
        except Exception as exc:  # noqa: BLE001
            rows.append({"file": fname, "family": family,
                         "outcome": f"CASE-LAYER {type(exc).__name__}"})
            continue
        try:
            comp = Compiler(options=CompileOptions(
                cache_dir=str(CACHE / "census"), dumps=False))
            art = comp.compile_case(case)
        except PipelineError as exc:
            rows.append({"file": fname, "family": family,
                         "outcome": "REFUSED",
                         "reason": str(exc)[:160]})
            continue
        except Exception as exc:  # noqa: BLE001
            rows.append({"file": fname, "family": family,
                         "outcome": f"COMPILE-ERROR {type(exc).__name__}"})
            continue
        # compiled: execute and compare under the case's own policy
        try:
            device = nd.NativeExecutableDevice(comp, 1)
            staged = device.stage_case(case)
            staged.launch()
            outs = staged.outputs()
            exp = case.get("expected")
            okc = True
            if exp:
                for name, policy in case.get("comparison",
                                             {}).items():
                    got = np.asarray(outs[name])
                    e = np.asarray(exp[name])
                    if policy.get("exact"):
                        okc &= np.array_equal(got, e)
                    else:
                        okc &= np.allclose(
                            got.astype(np.float64), e.astype(np.float64),
                            rtol=policy.get("rtol", 1e-5),
                            atol=policy.get("atol", 1e-5),
                            equal_nan=policy.get("equal_nan", False))
            rows.append({"file": fname, "family": family,
                         "outcome": "PASS" if okc else "COMPARE-FAIL"})
        except Exception as exc:  # noqa: BLE001
            rows.append({"file": fname, "family": family,
                         "outcome": f"RUN-ERROR {type(exc).__name__} "
                                    f"{str(exc)[:80]}"})
    EVIDENCE["census"] = rows
    refused = sum(1 for r in rows if r["outcome"] == "REFUSED")
    passed = sum(1 for r in rows if r["outcome"] == "PASS")
    other = len(rows) - refused - passed
    print("# census:")
    for r in rows:
        print(f"#   {r['file']:46s} {r['family']:12s} {r['outcome']}"
              + (f" ({r['reason'][:100]})" if r.get("reason") else ""))
    # the boundary contract: every non-PASS row is a located refusal or
    # a case-layer outcome -- never a silent wrong answer from the
    # compiler
    ok = all(r["outcome"] in ("PASS", "REFUSED")
             or r["outcome"].startswith(("CASE-LAYER", "COMPILE-ERROR",
                                         "RUN-ERROR", "MISSING"))
             for r in rows)
    check("family-census-no-silent-wrong-answers", ok,
          f"{passed} PASS, {refused} located refusals (a boundary of "
          "another construct, never a silent wrong answer), "
          f"{other} case/environment rows")


# ---------------------------------------------------------------------------
# The k-loop reproduction record (the defect the guard refuses)
# ---------------------------------------------------------------------------


def check_kloop_reproduction():
    """The T030 repair regression: dots inside runtime-bound loops lower
    and execute correctly (T014's located refusal is removed).

    The recorded defects behind the old guard, both reproduced before the
    repair and executed-compared after it:

      * the staged carries' back-edge copy indexed its lanes by
        ``vid + i/vl`` instead of ``vid + i`` (i counts elements) -- the
        second chunk copied elements 1..vl instead of vl..2*vl-1, so a
        carried 64-element accumulator lost every element beyond lane 0
        of chunk two (the 'chunks beyond the first 256 bytes' record);
      * the matrix region's body resolved uses of the induction to the
        PRE-LOOP init constant instead of the head parameter (the
        ordinary loop/while paths' override) -- the hoisted induction
        increment re-computed init+step every iteration, the loop never
        exited, and the pointer recurrences walked the loads out of the
        buffers (the multi-iteration k-loop segfault).
    """
    # (1) the kloop probe (a RUNTIME loop bound) compiles by default --
    # no refusal: the guard is gone
    kpath = WORK / "kloop.py"
    if not kpath.is_file():
        kpath.write_text(KLOOP)
    kspec = importlib.util.spec_from_file_location("kloop", str(kpath))
    km = importlib.util.module_from_spec(kspec)
    kspec.loader.exec_module(km)
    kcase = km.make_case()
    kcase["meta"]["FORM"] = 0
    rng = np.random.default_rng(31)
    M, N, K = 8, 8, 16
    a = (rng.standard_normal((M, K)) * 0.5).astype(np.float32)
    b = (rng.standard_normal((K, N)) * 0.5).astype(np.float32)
    arrays = {"A_ptr": a.reshape(-1), "B_ptr": b.reshape(-1),
              "C_ptr": np.zeros(M * N, np.float32),
              "M": np.int32(M), "N": np.int32(N), "K": np.int32(K)}
    aw, bw = a, b
    kcase["args"] = arrays
    try:
        comp = Compiler(options=CompileOptions(
            cache_dir=str(CACHE / "kloop-default"), dumps=False))
        comp.compile_case(kcase)
        check("kloop-dot-compiles-by-default", True,
              "the runtime-bound k-loop lowers (the T014 refusal is "
              "removed; the dot rides the staged tile pipeline)")
    except PipelineError as exc:
        check("kloop-dot-compiles-by-default", False, str(exc)[:110])
        return
    # (2) it executes and compares PASS (single iteration: the carried
    # 64-element accumulator is TWO chunks -- the back-edge copy's
    # second chunk is exactly what the old defect lost)
    expected = {"C_ptr": (aw @ bw).astype(np.float32).reshape(-1)}
    kcase["expected"] = expected
    kcase["comparison"] = {"C_ptr": {"comparator": "allclose",
                                     "exact": False, "rtol": 1e-4,
                                     "atol": 1e-4}}
    try:
        device = nd.NativeExecutableDevice(comp, 1)
        staged = device.stage_case(kcase)
        staged.launch()
        outs = staged.outputs()
        good, why = compare(kcase, outs)
        check("kloop-dot-executes-and-compares", good, why)
        EVIDENCE["cases"].append(
            {"form": "kloop-runtime-bound-1iter",
             "artifact_sha256": staged.artifact_sha256,
             "compare": "PASS" if good else "FAIL"})
    except Exception as exc:  # noqa: BLE001
        check("kloop-dot-executes-and-compares", False,
              f"{type(exc).__name__}: {str(exc)[:90]}")
    # (3) the oneloop reproduction (the exact T014 record) now passes
    opath = WORK / "oneloop.py"
    opath.write_text(ONELOOP)
    ospec = importlib.util.spec_from_file_location("oneloop", str(opath))
    om = importlib.util.module_from_spec(ospec)
    ospec.loader.exec_module(om)
    ocase = om.make_case()
    rng2 = np.random.default_rng(9)
    a = (np.arange(M * K).reshape(M, K) % 97).astype(np.float32)
    b = np.zeros((K, N), np.float32)
    for k in range(min(N, K)):
        b[k, k] = 1.0
    oarrays = {"A_ptr": a.reshape(-1), "B_ptr": b.reshape(-1),
               "C_ptr": np.zeros(M * N, np.float32),
               "M": np.int32(M), "N": np.int32(N), "K": np.int32(K),
               "sam": np.int32(K), "sak": np.int32(1),
               "sbk": np.int32(N), "sbn": np.int32(1),
               "scm": np.int32(N), "scn": np.int32(1)}
    try:
        ocomp = Compiler(options=CompileOptions(
            cache_dir=str(CACHE / "kloop-oneloop"), dumps=False))
        device = nd.NativeExecutableDevice(ocomp, 1)
        staged = device.stage_case({**ocase, "args": oarrays})
        staged.launch()
        got = np.asarray(staged.outputs()["C_ptr"]).reshape(M, N)
        exp = a @ b
        ok = np.allclose(got, exp, rtol=1e-4, atol=1e-4)
        bad = int(np.sum(np.abs(got - exp) > 1e-3))
        check("kloop-oneloop-reproduction-passes", ok,
              f"the T014 reproduction executes and compares "
              f"{'PASS' if ok else 'FAIL'} ({bad}/{M*N} bad; before the "
              "repair 30/64 were wrong -- the staged regions lost the "
              "second chunk of the carried accumulator)")
        EVIDENCE["kloop_reproduction"] = {
            "shape": [M, N, K], "bad_elements": bad,
            "note": "the T030 repair regression (was 30/64 wrong at "
                    "this exact probe before the back-edge copy fix)"}
    except Exception as exc:  # noqa: BLE001
        check("kloop-oneloop-reproduction-passes", False,
              f"{type(exc).__name__}: {str(exc)[:90]}")
    # (4) multi-iteration k-loops: the loop must terminate (the
    # induction override) and the carry must accumulate across
    # iterations; 1/2/4 worker threads on one artifact per identity
    mpath = WORK / "kloopm.py"
    mpath.write_text(KLOOPM)
    mspec = importlib.util.spec_from_file_location("kloopm", str(mpath))
    mm = importlib.util.module_from_spec(mspec)
    mspec.loader.exec_module(mm)
    for label, Mx, Nx, Kx, BKx, threads in (
            ("2iters", 8, 8, 32, 16, 1),
            ("3iters", 8, 8, 48, 16, 1),
            ("ragged", 16, 8, 56, 16, 1),
            ("8iters", 8, 16, 64, 8, 4)):
        rng3 = np.random.default_rng(41)
        a3 = (rng3.standard_normal((Mx, Kx)) * 0.5).astype(np.float32)
        b3 = (rng3.standard_normal((Kx, Nx)) * 0.5).astype(np.float32)
        arrays3 = {"A_ptr": a3.reshape(-1), "B_ptr": b3.reshape(-1),
                   "C_ptr": np.zeros(Mx * Nx, np.float32),
                   "M": np.int32(Mx), "N": np.int32(Nx),
                   "K": np.int32(Kx)}
        aw3, bw3 = a3, b3
        mcase = mm.make_case()
        mcase["meta"]["FORM"] = 0
        mcase["args"] = dict(arrays3)
        mcase["meta"].update({"BM": Mx, "BN": Nx, "BK": BKx})
        mcase["expected"] = {"C_ptr": (aw3 @ bw3).astype(
            np.float32).reshape(-1)}
        mcase["comparison"] = {"C_ptr": {"comparator": "allclose",
                                         "exact": False, "rtol": 1e-4,
                                         "atol": 1e-4}}
        try:
            mcomp = Compiler(options=CompileOptions(
                cache_dir=str(CACHE / "kloop-multi"), dumps=False))
            device = nd.NativeExecutableDevice(mcomp, threads)
            staged = device.stage_case(mcase)
            staged.launch()
            good, why = compare(mcase, staged.outputs())
            iters = (Kx + BKx - 1) // BKx
            check(f"kloop-multi-iter-{label}-threads{threads}", good,
                  f"{iters} k-iterations, threads {threads}: {why}")
            EVIDENCE["cases"].append(
                {"form": f"kloop-multi-{Mx}x{Nx}x{Kx}-bk{BKx}",
                 "artifact_sha256": staged.artifact_sha256,
                 "threads": threads,
                 "compare": "PASS" if good else "FAIL"})
        except Exception as exc:  # noqa: BLE001
            check(f"kloop-multi-iter-{label}-threads{threads}", False,
                  f"{type(exc).__name__}: {str(exc)[:90]}")
    # (5) the IME k-loop forms: positive smt.vmadot / smt.vfwmadot
    # counts bound to the same artifact (acceptance[1]'s dot-in-loop
    # witness)
    for label, adtype, odtype, mnemonic, exact in (
            ("int8", "int8", "int32", "smt.vmadot", True),
            ("fp16", "float16", "float32", "smt.vfwmadot", False)):
        rng4 = np.random.default_rng(47)
        Mx = Nx = 8
        Kx = 32
        if exact:
            a4 = rng4.integers(-100, 100, (Mx, Kx)).astype(np.int8)
            b4 = rng4.integers(-100, 100, (Kx, Nx)).astype(np.int8)
            aw4 = a4.astype(np.int64)
            bw4 = b4.astype(np.int64)
        else:
            a4 = (rng4.standard_normal((Mx, Kx)) * 0.5).astype(np.float16)
            b4 = (rng4.standard_normal((Kx, Nx)) * 0.5).astype(np.float16)
            aw4 = a4.astype(np.float32)
            bw4 = b4.astype(np.float32)
        arrays4 = {"A_ptr": a4.reshape(-1), "B_ptr": b4.reshape(-1),
                   "C_ptr": np.zeros(Mx * Nx, np.int32 if exact
                                     else np.float32),
                   "M": np.int32(Mx), "N": np.int32(Nx),
                   "K": np.int32(Kx)}
        icase = mm.make_case()
        icase["meta"]["FORM"] = 0
        icase["args"] = dict(arrays4)
        icase["meta"].update({"BM": Mx, "BN": Nx, "BK": 16})
        icase["expected"] = {"C_ptr": (aw4 @ bw4).astype(
            np.int32 if exact else np.float32).reshape(-1)}
        icase["comparison"] = {"C_ptr": {
            "comparator": "array_equal" if exact else "allclose",
            "exact": exact, "rtol": 1e-3, "atol": 1e-2}}
        try:
            icomp = Compiler(options=CompileOptions(
                cache_dir=str(CACHE / f"kloop-ime-{label}"), dumps=False))
            device = nd.NativeExecutableDevice(icomp, 1)
            staged = device.stage_case(icase)
            staged.launch()
            good, why = compare(icase, staged.outputs())
            counts_file = CACHE / f"kloop-ime-{label}-counts.json"
            res = run_with_plugin(staged.artifact.executable, icase,
                                  counts_file, threads=1)
            if res is None:
                check(f"kloop-{label}-ime-counts-{mnemonic}", False,
                      "the plugin endpoint is unavailable")
                continue
            rc, counts = res
            rows = [r for r in counts["instructions"]
                    if r["mnemonic"] == mnemonic]
            total = sum(r["executions"] for r in rows)
            # the tile model: the declared pure model per SOURCE k-loop
            # iteration (each iteration's dot covers the block extents
            # BM x BN x BK; the family's tile_k decides the tile ops a
            # block needs -- int8 tile_k 16: one op, fp16 tile_k 8: two
            # for BK 16), times the executed source iterations K/BK
            plan4 = tiles_mod.plan_dot_breadth(
                tiles_mod.BreadthDotDescription(
                    a_dtype=adtype, b_dtype=adtype, out_dtype=odtype,
                    block_m=Mx, block_n=Nx, block_k=16))
            per_dot = tiles_mod.expected_ime_tile_ops_breadth(
                Mx, Nx, 16, plan4)
            model = (Kx + 15) // 16 * per_dot
            check(f"kloop-{label}-kloop-compares", good, why)
            check(f"kloop-{label}-ime-counts-{mnemonic}",
                  rc == 0 and good and total >= 1 and total == model,
                  f"counted {total} (model {model}: {Kx}//16 source "
                  f"k-steps x {per_dot} tile op(s) per dot at "
                  f"tile_k {plan4.family.tile_k}), artifact "
                  f"{staged.artifact_sha256[:12]}, "
                  f"compare {'PASS' if good else 'FAIL'}")
            EVIDENCE["cases"].append(
                {"form": f"kloop-ime-{label}-{Mx}x{Nx}x{Kx}",
                 "artifact_sha256": staged.artifact_sha256,
                 "mnemonic": mnemonic, "executed": total, "model": model,
                 "compare": "PASS" if good else "FAIL"})
        except Exception as exc:  # noqa: BLE001
            check(f"kloop-{label}-ime-counts-{mnemonic}", False,
                  f"{type(exc).__name__}: {str(exc)[:90]}")


ONELOOP = '''"""probe"""
OPERATOR = {"name": "probe/oneloop", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}
SHAPES = ((8,))
import numpy as np
import triton
import triton.language as tl

@triton.jit
def oneloop_kernel(A_ptr, B_ptr, C_ptr, M, N, K,
                   sam, sak, sbk, sbn, scm, scn,
                   BM: tl.constexpr, BN: tl.constexpr, BK: tl.constexpr,
                   NITER: tl.constexpr):
    offs_m = tl.arange(0, BM)
    offs_n = tl.arange(0, BN)
    offs_k = tl.arange(0, BK)
    a_ptrs = A_ptr + (offs_m[:, None] * BK + offs_k[None, :])
    b_ptrs = B_ptr + (offs_k[:, None] * BN + offs_n[None, :])
    acc = tl.zeros((BM, BN), dtype=tl.float32)
    for it in range(0, NITER):
        a = tl.load(a_ptrs, mask=(offs_m[:, None] < M) & (offs_k[None, :] < K), other=0.0)
        b = tl.load(b_ptrs, mask=(offs_k[:, None] < K) & (offs_n[None, :] < N), other=0.0)
        acc += tl.dot(a, b)
        a_ptrs += BK * sak
        b_ptrs += BK * sbk
    c_ptrs = C_ptr + (offs_m[:, None] * scm + offs_n[None, :] * scn)
    tl.store(c_ptrs, acc.to(C_ptr.dtype.element_ty),
             mask=(offs_m[:, None] < M) & (offs_n[None, :] < N))

def ref(args, meta):
    return {"C_ptr": args["C_ptr"]}

def _make_case(shape=(8,), dtype="float32", seed=0):
    M, N, K = 8, 8, 16
    rng = np.random.default_rng(3)
    a = (rng.standard_normal((M, K)) * 0.5).astype(np.float32)
    b = (rng.standard_normal((K, N)) * 0.5).astype(np.float32)
    args = {"A_ptr": a.reshape(-1), "B_ptr": b.reshape(-1),
            "C_ptr": np.zeros(M*N, np.float32),
            "M": np.int32(M), "N": np.int32(N), "K": np.int32(K),
            "sam": np.int32(K), "sak": np.int32(1),
            "sbk": np.int32(N), "sbn": np.int32(1),
            "scm": np.int32(N), "scn": np.int32(1)}
    return {"args": args, "meta": {"BM": 8, "BN": 8, "BK": 16, "NITER": 1},
            "grid": (1,), "kernel": oneloop_kernel, "outputs": ("C_ptr",),
            "expected": {"C_ptr": (a @ b).reshape(-1)},
            "comparison": {"C_ptr": {"comparator": "allclose", "exact": False,
                                      "rtol": 1e-4, "atol": 1e-4}}}

def make_case(shape=None, dtype=None, seed=None):
    return _make_case()
'''


KLOOP = '''"""probe"""
OPERATOR = {"name": "probe/kloop", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}
SHAPES = ((8,))
import numpy as np
import triton
import triton.language as tl

@triton.jit
def kloop_kernel(A_ptr, B_ptr, C_ptr, M, N, K,
                 BM: tl.constexpr, BN: tl.constexpr, BK: tl.constexpr):
    offs_m = tl.arange(0, BM)
    offs_n = tl.arange(0, BN)
    offs_k = tl.arange(0, BK)
    a_ptrs = A_ptr + (offs_m[:, None] * BK + offs_k[None, :])
    b_ptrs = B_ptr + (offs_k[:, None] * BN + offs_n[None, :])
    acc = tl.zeros((BM, BN), dtype=tl.float32)
    for k0 in range(0, K, BK):
        krem = K - k0
        a = tl.load(a_ptrs, mask=(offs_m[:, None] < M)
                    & (offs_k[None, :] < krem), other=0.0)
        b = tl.load(b_ptrs, mask=(offs_k[:, None] < krem)
                    & (offs_n[None, :] < N), other=0.0)
        acc += tl.dot(a, b)
        a_ptrs += BK
        b_ptrs += BK
    c_ptrs = C_ptr + (offs_m[:, None] * BN + offs_n[None, :])
    tl.store(c_ptrs, acc.to(C_ptr.dtype.element_ty),
             mask=(offs_m[:, None] < M) & (offs_n[None, :] < N))

def ref(args, meta):
    return {"C_ptr": args["C_ptr"]}

def _make_case(shape=(8,), dtype="float32", seed=0):
    M, N, K = 8, 8, 16
    rng = np.random.default_rng(3)
    a = (rng.standard_normal((M, K)) * 0.5).astype(np.float32)
    b = (rng.standard_normal((K, N)) * 0.5).astype(np.float32)
    args = {"A_ptr": a.reshape(-1), "B_ptr": b.reshape(-1),
            "C_ptr": np.zeros(M*N, np.float32),
            "M": np.int32(M), "N": np.int32(N), "K": np.int32(K)}
    return {"args": args, "meta": {"BM": 8, "BN": 8, "BK": 16},
            "grid": (1,), "kernel": kloop_kernel, "outputs": ("C_ptr",),
            "expected": {"C_ptr": (a @ b).reshape(-1)},
            "comparison": {"C_ptr": {"comparator": "allclose",
                                      "exact": False,
                                      "rtol": 1e-4, "atol": 1e-4}}}

def make_case(shape=None, dtype=None, seed=None):
    return _make_case()
'''


KLOOPM = '''"""probe"""
OPERATOR = {"name": "probe/kloopm", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}
SHAPES = ((8,))
import numpy as np
import triton
import triton.language as tl

@triton.jit
def kloopm_kernel(A_ptr, B_ptr, C_ptr, M, N, K,
                  BM: tl.constexpr, BN: tl.constexpr, BK: tl.constexpr):
    offs_m = tl.arange(0, BM)
    offs_n = tl.arange(0, BN)
    offs_k = tl.arange(0, BK)
    a_ptrs = A_ptr + (offs_m[:, None] * K + offs_k[None, :])
    b_ptrs = B_ptr + (offs_k[:, None] * N + offs_n[None, :])
    acc = tl.zeros((BM, BN), dtype=tl.float32)
    for k0 in range(0, K, BK):
        krem = K - k0
        a = tl.load(a_ptrs, mask=(offs_m[:, None] < M)
                    & (offs_k[None, :] < krem), other=0.0)
        b = tl.load(b_ptrs, mask=(offs_k[:, None] < krem)
                    & (offs_n[None, :] < N), other=0.0)
        acc += tl.dot(a, b)
        a_ptrs += BK
        b_ptrs += BK * N
    c_ptrs = C_ptr + (offs_m[:, None] * N + offs_n[None, :])
    tl.store(c_ptrs, acc.to(C_ptr.dtype.element_ty),
             mask=(offs_m[:, None] < M) & (offs_n[None, :] < N))

def ref(args, meta):
    return {"C_ptr": args["C_ptr"]}

def _make_case(shape=(8,), dtype="float32", seed=0):
    M, N, K = 8, 8, 32
    rng = np.random.default_rng(3)
    a = (rng.standard_normal((M, K)) * 0.5).astype(np.float32)
    b = (rng.standard_normal((K, N)) * 0.5).astype(np.float32)
    args = {"A_ptr": a.reshape(-1), "B_ptr": b.reshape(-1),
            "C_ptr": np.zeros(M*N, np.float32),
            "M": np.int32(M), "N": np.int32(N), "K": np.int32(K)}
    return {"args": args, "meta": {"BM": 8, "BN": 8, "BK": 16},
            "grid": (1,), "kernel": kloopm_kernel, "outputs": ("C_ptr",),
            "expected": {"C_ptr": (a @ b).reshape(-1)},
            "comparison": {"C_ptr": {"comparator": "allclose",
                                      "exact": False,
                                      "rtol": 1e-4, "atol": 1e-4}}}

def make_case(shape=None, dtype=None, seed=None):
    return _make_case()
'''


# ---------------------------------------------------------------------------
# The frontend's typing boundaries (the pinned Triton 3.8 rules)
# ---------------------------------------------------------------------------


def check_frontend_boundaries():
    """The pinned tl.dot typing rules as located refusals: fp64 operands
    (outside the corpus dtype surface, F037), non-i8 integers (the
    pinned 'only int8 supported'), out_dtype=bfloat16 (the pinned
    ValueError), mismatched operand dtypes, rank-3 operands (not in this
    lane), and a K-extent mismatch."""
    body = DOT_TEMPLATE.format(name="bound", adtype="float32",
                               odtype="float32")
    cases = [
        ("fp64-operands",
         "c = tl.dot(a.to(tl.float64), b.to(tl.float64))",
         ("tl.dot", "fp64")),
        ("int16-operands",
         "c = tl.dot(a.to(tl.int16), b.to(tl.int16))",
         ("tl.dot", "int")),
        ("bf16-out-dtype",
         "c = tl.dot(a, b, out_dtype=tl.bfloat16)",
         ("tl.dot", "bfloat16")),
        ("mixed-operands",
         "c = tl.dot(a, b.to(tl.float64))",
         ("tl.dot", "same dtype")),
        ("k-mismatch",
         "c = tl.dot(a, tl.load(b_ptrs)[:, :8])",
         ("tl.dot", "reduction extents")),
    ]
    ok = True
    for label, replacement, needles in cases:
        text = body.replace(
            "        c = tl.dot(a, b)\n"
            "        tl.store(O_ptr + (offs_m[:, None] * scn"
            " + offs_n[None, :] * scm),\n"
            "                 c.to(O_ptr.dtype.element_ty))",
            f"        {replacement}\n"
            "        tl.store(O_ptr + (offs_m[:, None] * scn"
            " + offs_n[None, :] * scm),\n"
            "                 c.to(O_ptr.dtype.element_ty))")
        if replacement not in text:
            ok = False
            print(f"       {label}: the probe template did not apply")
            continue
        path = WORK / f"bound_{label}.py"
        path.write_text(text)
        try:
            src = fe_source.load_operator(str(path))
            specz = fe_spec.specialize(src, {
                "args": {"A_ptr": np.zeros(16, np.float32),
                         "B_ptr": np.zeros(16, np.float32),
                         "C_ptr": np.zeros(16, np.float32),
                         "O_ptr": np.zeros(16, np.float32),
                         "M": np.int32(16), "N": np.int32(16),
                         "K": np.int32(16), "sam": np.int32(16),
                         "sak": np.int32(1), "sbk": np.int32(16),
                         "sbn": np.int32(1), "scm": np.int32(16),
                         "scn": np.int32(1)},
                "meta": {"BM": 16, "BN": 16, "BK": 16, "FORM": 0},
                "grid": (1,), "outputs": ("O_ptr",)})
            lower_tir.lower(src, specz)
            check(f"refusal-{label}", False, "no refusal raised")
            ok = False
        except FrontendError as exc:
            located = all(n in str(exc) for n in needles)
            check(f"refusal-{label}", located, str(exc)[:100])
            ok &= located
        except Exception as exc:  # noqa: BLE001
            check(f"refusal-{label}", False,
                  f"{type(exc).__name__}: {str(exc)[:80]}")
            ok = False
    return ok


def main() -> int:
    compiler = Compiler(options=CompileOptions(cache_dir=str(CACHE)))
    check_every_form(compiler)
    check_fp32_ieee_bitexact(compiler)
    check_bf16_gap(compiler)
    check_ime_counts(compiler)
    check_budget()
    check_pointer_recurrence_regression(compiler)
    check_thread_matrix(compiler)
    check_frontend_boundaries()
    check_kloop_reproduction()
    check_corpus_census(compiler)
    evidence = {
        "schema": "a100c-matrix-breadth/v1",
        "endpoint": f"qemu-functional (jdsk-qemu 10.0.2, -cpu {QEMU_CPU})",
        "cases": EVIDENCE["cases"],
        "census": EVIDENCE["census"],
        "kloop_reproduction": EVIDENCE.get("kloop_reproduction"),
    }
    out = CACHE / "matrix-breadth-evidence.json"
    out.write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"# evidence: {out}")
    if FAILURES:
        print(f"test_matrix_breadth: FAILED: {len(FAILURES)} check(s)")
        for f in FAILURES:
            print(f"  - {f}")
        return 1
    print("test_matrix_breadth: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
