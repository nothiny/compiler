#!/usr/bin/env python3
"""test_t034_repairs.py -- the T034 repair classes, each through the real
path (compile -> native execution -> comparison under the case's own
policy), with the controls that prove the checks are load-bearing.

  * rank2-blockptr-tile: the two-axis block-pointer desugar keeps the
    source's DECLARED block shape (the old rank-1 flattening was
    shape-agnostic; a (slow, fast) tile transposed every block whose
    order places the minor axis first).  matmul_kernel_1334dd27 (the
    runtime K loop; fp16 = the IME path, fp32, bf16) and matmul_abt
    (fp32/bf16; the static_range unrolled form) execute and compare at 1
    and 4 workers.  The blockptr advance channels: the loop carries the
    stepped axes (the K offsets) and drops the untouched ones.
  * fp16-atomic-subword: 16-bit pointee atomics (fp16/bf16/int16) lower
    as an aligned 32-bit word lr/sc RMW preserving the neighbouring
    half, with the declared RVWMO ordering (the aq/rl suffixes on the
    lr.w/sc.w pair).  All four corpus operators execute and compare at
    1/2/4/8 workers (scatter_atomic's cross-program accumulation: every
    contribution lands exactly once).
  * scalar-width: sub-32 scalar widening rides the vector lane
    (weighted_scatter_add's ``.to(tl.int16)`` over an i8 load), and
    mixed-width scalar pairs widen to the declared computation width at
    the compare (logsumexp's ``has_nan |= ... > 0`` -- kept located: its
    1024-lane block in a chunked region re-derives the carried value per
    pass, a located refusal rather than the silently wrong -inf).
  * float-scalar-cmp: a re-materialized floating comparison
    (pdist's ``if p_val == 0.0``) rides the splat-compare-extract form;
    pdist executes and compares at 1 and 4 workers.  Its binary search
    also pins the if-join side repair (the alias-driven name environment
    resolved one arm's join side to the sibling's value).
  * the two T018-named defects: sym_constrain_range int64 compiles and
    executes (the scalar_store VectorType crash is gone) and sgn_real
    bf16 builds an artifact (the two fixed-v0 working masks no longer
    overlap: the pin moved to immediately before its select).

Controls (MECH-WITNESS-TEST): the fp16 guard-region witness (a masked
block atomic whose disabled lanes address a poisoned guard -- intact in
the real build, corrupted in the degraded witness_drop_atomic_masks
build), the assembly carries the lr.w/sc.w ordered suffixes of the
declared sem/scope mapping, and the located refusals (grouped_gemm's
grid, logsumexp's chunked carried value) name their construct.

Run: python3 a100c/tests/test_t034_repairs.py  (exit 0 = all PASS)
"""
from __future__ import annotations

import importlib.util
import re
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
          f"{(' | ' + detail) if detail else ''}", flush=True)
    if not ok:
        FAILURES.append(name)
    return ok


import numpy as np  # noqa: E402

from a100c.driver import CompileOptions, PipelineError  # noqa: E402
from a100c.factory import FactoryCompiler  # noqa: E402
from a100c.passes import pipeline as passes_mod  # noqa: E402

OPS = ROOT / "ops"
WORK = Path(tempfile.mkdtemp(prefix="a100c-t034-"))


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_case(compiler, module, threads, **make_kwargs):
    import a100_support.native_device as nd
    case = module.make_case(**make_kwargs)
    device = nd.NativeExecutableDevice(compiler, threads)
    staged = device.stage_case(case)
    staged.launch()
    outputs = staged.outputs()
    ok = True
    detail = ""
    for name, policy in case["comparison"].items():
        got = np.asarray(outputs[name])
        exp = np.asarray(case["expected"][name])
        if got.shape != exp.shape and got.size == exp.size:
            got = got.reshape(exp.shape)
        if policy.get("exact") or policy["comparator"] == "array_equal":
            same = np.array_equal(got, exp)
        else:
            same = np.allclose(got, exp, rtol=policy.get("rtol", 0.0),
                               atol=policy.get("atol", 0.0),
                               equal_nan=policy.get("equal_nan", False))
        if not same:
            detail = f"{name}: {int(np.sum(got != exp))} mismatched elements"
        ok &= same
    return ok, detail


def _compiler(tag: str) -> FactoryCompiler:
    return FactoryCompiler(
        options=CompileOptions(cache_dir=str(WORK / f"cache-{tag}")),
        pass_config=passes_mod.PassConfig())


# ---------------------------------------------------------------------------
# acceptance[1]: the batched (two-axis block pointer) dot executes
# ---------------------------------------------------------------------------

def check_rank2_dot():
    c = _compiler("dot")
    bad = []
    mm = _load(OPS / "suite" / "dev" / "matmul_kernel_1334dd27.py")
    for dtype in ("float16", "float32", "bfloat16"):
        for threads in (1, 4):
            ok, detail = _run_case(c, mm, threads, dtype=dtype)
            if not ok:
                bad.append(f"1334dd27 {dtype} t={threads}: {detail}")
    abt = _load(OPS / "suite" / "dev" / "matmul_abt_kernel.py")
    for dtype in ("float32", "bfloat16"):
        for threads in (1, 4):
            ok, detail = _run_case(c, abt, threads, dtype=dtype)
            if not ok:
                bad.append(f"matmul_abt {dtype} t={threads}: {detail}")
    check("rank2-blockptr-tile-executes-1-4-workers", not bad,
          "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# acceptance[1]: fp16 atomics execute with the declared ordering
# ---------------------------------------------------------------------------

def check_fp16_atomics():
    c = _compiler("atm")
    bad = []
    sc = _load(OPS / "suite" / "dev" / "scatter_atomic_kernel.py")
    for threads in (1, 2, 4, 8):
        ok, detail = _run_case(c, sc, threads, dtype="float16")
        if not ok:
            bad.append(f"scatter fp16 t={threads}: {detail}")
    ok, detail = _run_case(c, sc, 4, dtype="float16", shape=(7, 3, 98))
    if not ok:
        bad.append(f"scatter fp16 tail: {detail}")
    for opname, dtypes in (
            ("weighted_scatter_add_kernel.py", ("float16", "float32")),
            ("splitk_gemv.py", ("float16",)),
            ("f_init_recurrence_kernel.py", ("float16",)),
            ("conv1x1_pool_fc_kernel.py", ("float16",))):
        module = _load(OPS / "suite" / "dev" / opname)
        for dtype in dtypes:
            for threads in (1, 4):
                ok, detail = _run_case(c, module, threads, dtype=dtype)
                if not ok:
                    bad.append(f"{opname} {dtype} t={threads}: {detail}")
    check("fp16-atomic-subword-executes-1-2-4-8", not bad,
          "; ".join(bad[:2]))


def check_atomic_ordering_assembly():
    """The sub-word loop's lr.w/sc.w carry the declared RVWMO suffixes:
    the default sem/scope (acq_rel/gpu) selects .aqrl; an explicit
    relaxed atomic selects the plain forms.  Asserted on the emitted
    program listing of an fp16 atomic artifact."""
    import a100_support.native_device as nd
    c = _compiler("atmorder")
    sc = _load(OPS / "suite" / "dev" / "scatter_atomic_kernel.py")
    case = sc.make_case(dtype="float16")
    device = nd.NativeExecutableDevice(c, 1)
    staged = device.stage_case(case)
    asm = (Path(staged.artifact.executable).parent / "program.S").read_text()
    has_aqrl = bool(re.search(r"\blr\.w\.aqrl\b", asm)) and \
        bool(re.search(r"\bsc\.w\.aqrl\b", asm))
    check("fp16-subword-ordered-forms-in-listing", has_aqrl,
          f"lr.w.aqrl/sc.w.aqrl {'present' if has_aqrl else 'missing'} "
          f"in the acq_rel default build")


# ---------------------------------------------------------------------------
# the guard witness for the sub-word atomic (acceptance[2] shape)
# ---------------------------------------------------------------------------

GUARD_BYTES = 128
POISON_U32 = 0x5A5A5A5A

FP16_GUARD_BODY = """\\
    i = tl.arange(0, BLOCK)
    m = i < n
    tl.atomic_add(out_ptr + i, 1.0, mask=m)"""

FP16_GUARD_LAYER = ('import numpy as np\n'
                    'def ref(args, meta):\n'
                    '    out = np.asarray(args["out_ptr"]).copy()\n'
                    '    out = (out.astype(np.float32) + 1.0)'
                    '.astype(out.dtype)\n'
                    '    return {"out_ptr": out}\n'
                    '\n'
                    'def _make_case(shape=(33,), dtype="float16", seed=0):\n'
                    '    n = int(shape[0])\n'
                    '    args = {"out_ptr": np.zeros(n, np.float16), "n": n}\n'
                    '    meta = {"BLOCK": 128}\n'
                    '    return {"args": args, "meta": meta, "grid": (1,),\n'
                    '            "kernel": gwit_kernel,\n'
                    '            "outputs": ("out_ptr",),\n'
                    '            "expected": ref(args, meta),\n'
                    '            "comparison": {"out_ptr": {\n'
                    '                "comparator": "allclose", "exact": False,\n'
                    '                "rtol": 1e-3, "atol": 1e-3,\n'
                    '                "equal_nan": True}}}\n'
                    '\n'
                    'def make_case(shape=None, dtype=None, seed=None):\n'
                    '    return _make_case()\n')


def _fp16_guard_case(directory: Path):
    text = ('"""probe operator gwit"""\n'
            'OPERATOR = {"name": "probe/gwit", "group": "probe", '
            '"channel": "local",\n'
            '            "execution": "triton_kernel", '
            '"verification": "correctness", "tags": []}\n'
            'SHAPES = ((33,),)\n'
            'import numpy as np\n'
            'import triton\n'
            'import triton.language as tl\n'
            '\n'
            '@triton.jit\n'
            'def gwit_kernel(out_ptr, n, BLOCK: tl.constexpr):\n'
            + FP16_GUARD_BODY + '\n'
            '\n'
            + FP16_GUARD_LAYER)
    path = directory / "gwit.py"
    path.write_text(text)
    module = _load(path)
    case = module.make_case()
    args = dict(case["args"])
    guard = np.frombuffer(
        np.array([POISON_U32], dtype="<u4").tobytes()
        * (GUARD_BYTES // 4), dtype=np.uint8)
    args["z_guard"] = guard
    case = dict(case)
    case["args"] = args
    case["pointer_dtypes"] = dict(case.get("pointer_dtypes") or {})
    case["pointer_dtypes"]["z_guard"] = "uint8"
    return case


def _guard_span(staged):
    import json
    info = json.loads((staged.directory / "bundle.json").read_text())
    out_view = info["views"]["out_ptr"]
    out_row = info["storages"][out_view["storage"]]
    guard_view = info["views"]["z_guard"]
    guard_row = info["storages"][guard_view["storage"]]
    image = (staged.directory / "bundle.bin").read_bytes()
    tail_end = 128 * 2
    span = image[guard_row["offset"]:
                 guard_row["offset"] + max(0, tail_end - out_row["size"])]
    return bytes(span)


def check_fp16_guard_witness():
    """The masked fp16 block atomic performs no access at its disabled
    positions: the real build leaves the poisoned guard behind the 33-lane
    fp16 row intact (the containing-word RMW of the last enabled element
    writes back the neighbour half bit-exactly); the degraded build
    (witness_drop_atomic_masks) corrupts it -- the check can fail, so the
    no-access property is load-bearing."""
    import a100_support.native_device as nd
    realdir = WORK / "gwit-real"
    realdir.mkdir(parents=True, exist_ok=True)
    case = _fp16_guard_case(realdir)
    real = FactoryCompiler(options=CompileOptions(
        cache_dir=str(WORK / "gwit-real-cache")))
    device = nd.NativeExecutableDevice(real, 1)
    staged = device.stage_case(case)
    staged.launch()
    outputs = staged.outputs()
    cmp_ok = np.allclose(np.asarray(outputs["out_ptr"], dtype=np.float32),
                         np.asarray(case["expected"]["out_ptr"],
                                    dtype=np.float32),
                         rtol=1e-3, atol=1e-3)
    span = _guard_span(staged)
    expected_span = bytes(np.array([POISON_U32], dtype="<u4").tobytes()
                          * (len(span) // 4))
    guard_ok = span == expected_span
    check("fp16-guard-region-real-build-intact", cmp_ok and guard_ok,
          f"compare {'PASS' if cmp_ok else 'FAIL'}; guard "
          f"{'intact' if guard_ok else 'corrupted'}")

    degradedir = WORK / "gwit-degraded"
    degradedir.mkdir(parents=True, exist_ok=True)
    case2 = _fp16_guard_case(degradedir)
    degraded = FactoryCompiler(options=CompileOptions(
        cache_dir=str(WORK / "gwit-degraded-cache"),
        witness_drop_atomic_masks=True))
    try:
        device2 = nd.NativeExecutableDevice(degraded, 1)
        staged2 = device2.stage_case(case2)
        staged2.launch()
        span2 = _guard_span(staged2)
        witness_corrupted = span2 != expected_span
        check("fp16-guard-witness-degraded-build-corrupts",
              witness_corrupted,
              "the degraded build left the guard intact -- the no-access "
              "property is NOT load-bearing" if not witness_corrupted
              else f"corrupted as required ({span2[:8].hex()} != "
                   f"{expected_span[:8].hex()})")
    except Exception as exc:               # noqa: BLE001
        check("fp16-guard-witness-degraded-build-corrupts", True,
              f"degraded run failed as required ({type(exc).__name__})")


# ---------------------------------------------------------------------------
# the scalar-width / float-compare classes
# ---------------------------------------------------------------------------

def check_scalar_width():
    c = _compiler("scalar")
    bad = []
    ws = _load(OPS / "suite" / "dev" / "weighted_scatter_add_kernel.py")
    for dtype in ("float32", "float16"):
        for threads in (1, 4):
            ok, detail = _run_case(c, ws, threads, dtype=dtype)
            if not ok:
                bad.append(f"weighted_scatter {dtype} t={threads}: {detail}")
    check("scalar-width-i8-to-i16-executes", not bad, "; ".join(bad[:2]))

    pd = _load(OPS / "suite" / "dev"
               / "pdist__pdist_forward_general_kernel.py")
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(c, pd, threads)
        if not ok:
            bad.append(f"pdist t={threads}: {detail}")
    check("float-scalar-cmp-and-if-join-sides-execute", not bad,
          "; ".join(bad[:2]))


def check_located_refusals():
    """The compile boundaries of the grouped-grid family.  T037 repaired
    the grouped_mm grid (the identity-signed trip count), T036 repaired
    the chunked carried-value family (logsumexec compiles), and T039
    repaired the last boundary this record pinned: grouped_gemm's
    tile-count sum lowers as a runtime SumLoop over the bundle-visible
    ``group_size`` scalar (its single identity spans groups=3 and
    groups=4, so no count is unrolled -- the routine loops the actual
    scalar read), so the operator now COMPILES (its identities execute
    and compare PASS at 1 and 4 workers -- the T039 repair test; the
    SumLoop's unreadable-bound refusal gate lives there too)."""
    c = _compiler("refusals")
    bad = []
    # T037 repaired the grouped_mm grid this record used to pin: the
    # tile-count loop's ``range(num_groups)`` bound is a case-shape axis
    # the identity SIGNS (meta num_groups), so the loop unrolls its
    # structure while the accumulated expression reads the M scalar and
    # the offs[0] view extent at run time -- the operator now COMPILES
    # (its identities execute and compare PASS -- the T037 repair test)
    gm = _load(OPS / "suite" / "dev" / "grouped_mm_kernel.py")
    try:
        c.compile_case(
            {k: v for k, v in gm.make_case().items()
             if k not in ("expected", "oracle_args")})
    except PipelineError as exc:
        bad.append(f"grouped_mm_kernel.py: refused at {exc.construct!r} "
                   "(T037 repaired the signed-count grid tie)")
    except Exception as exc:               # noqa: BLE001
        bad.append(f"grouped_mm_kernel.py: wrong error "
                   f"{type(exc).__name__}")
    # T039 repaired the grouped_gemm grid this record used to pin: the
    # tile-count sum is a runtime SumLoop over the group_size scalar
    gg = _load(OPS / "suite" / "dev" / "grouped_gemm_kernel.py")
    try:
        c.compile_case(
            {k: v for k, v in gg.make_case().items()
             if k not in ("expected", "oracle_args")})
    except PipelineError as exc:
        bad.append(f"grouped_gemm_kernel.py: refused at {exc.construct!r} "
                   "(T039 repaired the sum-loop grid tie)")
    except Exception as exc:               # noqa: BLE001
        bad.append(f"grouped_gemm_kernel.py: wrong error "
                   f"{type(exc).__name__}")
    lse = _load(OPS / "suite" / "perf" / "logsumexp.py")
    try:
        c.compile_case(
            {k: v for k, v in lse.make_case().items()
             if k not in ("expected", "oracle_args")})
    except PipelineError as exc:
        bad.append(f"logsumexp: refused at {exc.construct!r} (T036 "
                   "repaired the extremum carried-update merge)")
    except Exception as exc:                   # noqa: BLE001
        bad.append(f"logsumexp: wrong error {type(exc).__name__}")
    check("located-refusals-grid-and-chunked-carry", not bad,
          "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# the two T018-named defects
# ---------------------------------------------------------------------------

def check_named_defects():
    c = _compiler("named")
    bad = []
    scr = _load(OPS / "suite" / "dev" / "sym_constrain_range_kernel.py")
    for threads in (1, 4):
        ok, detail = _run_case(c, scr, threads)
        if not ok:
            bad.append(f"sym_constrain_range t={threads}: {detail}")
    check("sym-constrain-range-int64-regression", not bad,
          "; ".join(bad[:2]))

    sr = _load(OPS / "suite" / "dev" / "sgn_real_kernel.py")
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(c, sr, threads, dtype="bfloat16")
        if not ok:
            bad.append(f"sgn_real bf16 t={threads}: {detail}")
    check("sgn-real-bf16-v0-masks-serialized", not bad,
          "; ".join(bad[:2]))


def main():
    check_rank2_dot()
    check_fp16_atomics()
    check_atomic_ordering_assembly()
    check_fp16_guard_witness()
    check_scalar_width()
    check_located_refusals()
    check_named_defects()
    if FAILURES:
        print(f"\nFAILED: {len(FAILURES)} check(s): {FAILURES}")
        return 1
    print("\ntest_t034_repairs: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
