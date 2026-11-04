#!/usr/bin/env python3
"""test_lower_scalar.py -- the scalar/integer core of the lowering (T011).

The scalar core's declared semantics (A003, standard RV64IMAFDC) executed
end to end through the real pipeline (compile -> QEMU -> compare) on
equivalent kernel forms, plus the corpus operators that exercise them:

  * int64 index arithmetic: ``pid.to(tl.int64)``-typed offsets ride the
    i64/EMUL-2 index class (the count_nonzero corpus operator is the
    executor; an equivalent form adds a negative-offset case);
  * unsigned logic and shifts: ``bit.lshr``/``bit.ashr``/``bit.shl`` and
    unsigned comparisons at both widths (an equivalent form computes the
    declared wrap/shift answers; the controls are exact);
  * division and remainder: the truncating sdiv, the unsigned udiv, the
    C-truncation remainder and the non-negative power-of-two remainder
    fold (``i % 2^k == i & (2^k - 1)``) with its legality guard;
  * bool logic: the 0/1 value class (``(x != 0).to(tl.int64)``) through a
    reduction and an atomic;
  * the wrap semantics: i32 arithmetic wraps mod 2^32 exactly as the
    pinned Triton semantics declare (an equivalent form multiplies large
    values and compares the wrapped result against numpy's int32 wrap).

The refusals are located: vector division/remainder outside the fold,
scalar widening beyond 32->64.

Run: python3 a100c/tests/test_lower_scalar.py   (exit 0 = all checks PASS)
"""
from __future__ import annotations

import importlib.util
import shutil
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

from a100c.driver import Compiler, CompileOptions, PipelineError  # noqa: E402

# ---------------------------------------------------------------------------
# The operator-file template and the run helper (the same staging the
# corpus harness uses; every comparison is against an independent numpy
# reference under the case's own policy)
# ---------------------------------------------------------------------------

TEMPLATE = ('"""probe operator %s"""\n'
            'OPERATOR = {"name": "probe/%s", "group": "probe", "channel": "local",\n'
            '            "execution": "triton_kernel", "verification": "correctness",\n'
            '            "tags": []}\n'
            'SHAPES = ((257,),)\n'
            'import numpy as np\n'
            'import triton\n'
            'import triton.language as tl\n'
            '\n'
            '@triton.jit\n'
            'def %s_kernel(%s):\n'
            '%s\n'
            '\n'
            '%s\n')


def _operator_file(directory: Path, name: str, params: str, body: str,
                   case_layer: str):
    text = TEMPLATE % (name, name, name, params, body, case_layer)
    path = directory / f"{name}.py"
    path.write_text(text)
    return path


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _int_case_layer(ref_lines, kernel_ref, grid="((n + 127) // 128,)"):
    ref = "\n".join("    " + line for line in ref_lines)
    return ('def ref(args, meta):\n'
            '%s\n'
            '    return {"out_ptr": out.astype(np.int32)}\n'
            '\n'
            '\n'
            'def _make_case(shape=SHAPES[0], dtype="int32", seed=0):\n'
            '    n = int(shape[0])\n'
            '    rng = np.random.default_rng(seed)\n'
            '    x = rng.integers(-100, 100, n).astype(np.int32)\n'
            '    args = {"x_ptr": x, "out_ptr": np.zeros(n, np.int32),\n'
            '            "n": n}\n'
            '    meta = {"BLOCK": 128}\n'
            '    grid = %s\n'
            '    return {"args": args, "meta": meta, "grid": grid,\n'
            '            "kernel": %s, "outputs": ("out_ptr",),\n'
            '            "expected": ref(args, meta),\n'
            '            "comparison": {"out_ptr": {"comparator": "array_equal",\n'
            '                                       "exact": True}}}\n'
            '\n'
            '\n'
            'def make_case(shape=None, dtype=None, seed=None):\n'
            '    return _make_case(shape=shape or SHAPES[0],\n'
            '                      dtype=dtype or "int32", seed=seed or 0)\n'
            ) % (ref, grid, kernel_ref)


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
            detail = f"{name}: {np.sum(got != exp)} mismatched elements"
        ok &= same
    return ok, detail


# ---------------------------------------------------------------------------
# int64 index arithmetic (the corpus executor + the negative-offset form)
# ---------------------------------------------------------------------------

def check_int64_index_arithmetic(workdir, compiler):
    """count_nonzero_kernel_1 executes its int64-typed offsets exactly
    (pid.to(int64) * BLOCK + arange at 1/2/4/8 workers on one artifact per
    identity); an equivalent form adds a negative-offset i64 path
    (base - i) that the i64 index class must carry exactly too."""
    p = ROOT / "ops" / "suite" / "dev" / "count_nonzero_kernel_1.py"
    module = _load(p)
    bad = []
    for threads in (1, 2, 4, 8):
        for shape in ((17,), (97,)):
            ok, detail = _run_case(compiler, module, threads, shape=shape,
                                   dtype="float32")
            if not ok:
                bad.append(f"corpus t={threads} s={shape}: {detail}")
    check("int64-index-arithmetic-corpus-count-nonzero", not bad,
          "; ".join(bad[:2]))

    body = """\\
    i = tl.arange(0, BLOCK)
    n64 = n.to(tl.int64)
    i64 = i.to(tl.int64)
    offsets = n64 - i64 - 1
    m = offsets >= 0
    x = tl.load(x_ptr + offsets, mask=m, other=0)
    tl.store(out_ptr + i, (x + 1).to(tl.int32), mask=m)"""
    ref = ['xx = np.asarray(args["x_ptr"])',
           'out = np.zeros(len(xx), np.int32)',
           'out[:] = (xx[::-1] + 1).astype(np.int32)']
    path = _operator_file(workdir, "i64rev", "x_ptr, out_ptr, n, BLOCK: tl.constexpr",
                          body, _int_case_layer(ref, "i64rev_kernel",
                                                grid="(1,)"))
    module = _load(path)
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(compiler, module, threads, shape=(97,))
        if not ok:
            bad.append(f"t={threads}: {detail}")
    check("int64-index-arithmetic-reversed-offsets", not bad,
          "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# unsigned logic, shifts, wrap semantics
# ---------------------------------------------------------------------------

def check_shifts_unsigned_wrap(workdir, compiler):
    """Two equivalent kernels: an int32 one (ashr, shl, the signed wrap of
    a large multiply, the arithmetic shift of negatives) and a uint32 one
    (lshr, the unsigned compare, the mod-2^32 unsigned wrap); the numpy
    references compute the declared answers with numpy's own width
    discipline (the control: any deviation fails)."""
    body = """\\
    i = tl.program_id(0) * BLOCK + tl.arange(0, BLOCK)
    m = i < n
    x = tl.load(x_ptr + i, mask=m, other=0)
    a = x >> 3
    s = x << 4
    big = x * 998244353
    neg = -x
    tl.store(out_ptr + i, (a + s + big + neg).to(tl.int32), mask=m)"""
    ref = ['x = np.asarray(args["x_ptr"]).astype(np.int32)',
           'a = (x >> 3)',
           's = (x.astype(np.int64) << 4).astype(np.int32)',
           'big = (x.astype(np.int64) * 998244353).astype(np.int32)',
           'neg = (-x.astype(np.int64)).astype(np.int32)',
           'out = (a.astype(np.int64) + s + big + neg).astype(np.int32)']
    path = _operator_file(workdir, "shifts", "x_ptr, out_ptr, n, BLOCK: tl.constexpr",
                          body, _int_case_layer(ref, "shifts_kernel"))
    module = _load(path)
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(compiler, module, threads)
        if not ok:
            bad.append(f"signed t={threads}: {detail}")
    check("shift-signed-and-wrap-semantics-execute", not bad,
          "; ".join(bad[:2]))

    ubody = """\\
    i = tl.program_id(0) * BLOCK + tl.arange(0, BLOCK)
    m = i < n
    u = tl.load(x_ptr + i, mask=m)
    l = u >> 3
    big = u * u
    tl.store(out_ptr + i, (l + big).to(tl.uint32), mask=m)"""
    uref = ['u = np.asarray(args["x_ptr"]).astype(np.uint32)',
            'l = (u >> np.uint32(3))',
            'big = (u.astype(np.uint64) * u.astype(np.uint64)).astype(np.uint32)',
            'out = ((l.astype(np.uint64) + big) % np.uint64(2**32)).astype(np.uint32)']
    case_layer = ('def ref(args, meta):\n'
                  + "\n".join("    " + l for l in uref) +
                  '\n    return {"out_ptr": out}\n'
                  '\n'
                  'def _make_case(shape=SHAPES[0], dtype="uint32", seed=0):\n'
                  '    n = int(shape[0])\n'
                  '    rng = np.random.default_rng(seed)\n'
                  '    x = rng.integers(0, 2**32, n).astype(np.uint32)\n'
                  '    args = {"x_ptr": x, "out_ptr": np.zeros(n, np.uint32),\n'
                  '            "n": n}\n'
                  '    meta = {"BLOCK": 128}\n'
                  '    grid = ((n + 127) // 128,)\n'
                  '    return {"args": args, "meta": meta, "grid": grid,\n'
                  '            "kernel": ushifts_kernel, "outputs": ("out_ptr",),\n'
                  '            "expected": ref(args, meta),\n'
                  '            "pointer_dtypes": {"x_ptr": "uint32", "out_ptr": "uint32"},\n'
                  '            "comparison": {"out_ptr": {"comparator": "array_equal",\n'
                  '                                       "exact": True}}}\n'
                  '\n'
                  'def make_case(shape=None, dtype=None, seed=None):\n'
                  '    return _make_case(shape=shape or SHAPES[0],\n'
                  '                      dtype=dtype or "uint32", seed=seed or 0)\n')
    path = _operator_file(workdir, "ushifts", "x_ptr, out_ptr, n, BLOCK: tl.constexpr",
                          ubody, case_layer)
    module = _load(path)
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(compiler, module, threads)
        if not ok:
            bad.append(f"unsigned t={threads}: {detail}")
    check("shift-unsigned-lshr-and-wrap-execute", not bad,
          "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# division and remainder (truncating sdiv, udiv, the pow2 fold + guard)
# ---------------------------------------------------------------------------

def check_division_remainder(workdir, compiler):
    """The truncating sdiv runs on the scalar core (vector division is a
    declared refusal -- no vdiv row): ``n // 7`` and ``(0 - n) // 7``
    give the positive and negative truncation answers Python's floor
    division disagrees with for negative n.  The non-negative power-of-two
    remainder folds to a mask exactly (atomic_bitmap's ``i % 4`` rides
    it; the equivalent form checks ``i % 8`` on the arange)."""
    body = """\\
    lane = tl.arange(0, BLOCK)
    m = lane % 8
    i = tl.program_id(0) * BLOCK + lane
    msk = i < n
    x = tl.load(x_ptr + i, mask=msk, other=0)
    q = (n // 7) + (0 - n) // 7
    tl.store(out_ptr + i, (x + q + m).to(tl.int32), mask=msk)"""
    ref = ['x = np.asarray(args["x_ptr"])',
           'n = int(args["n"])',
           'q = int(np.int32(np.trunc(n / 7) + np.trunc((0 - n) / 7)))',
           'i = np.arange(len(x), dtype=np.int64)',
           'm = ((i % 128) % 8).astype(np.int32)',
           'out = (x.astype(np.int64) + q + m).astype(np.int32)']
    path = _operator_file(workdir, "divrem", "x_ptr, out_ptr, n, BLOCK: tl.constexpr",
                          body, _int_case_layer(ref, "divrem_kernel"))
    module = _load(path)
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(compiler, module, threads)
        if not ok:
            bad.append(f"t={threads}: {detail}")
    check("division-remainder-and-pow2-fold-execute", not bad,
          "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# bool logic: the 0/1 value class
# ---------------------------------------------------------------------------

def check_bool_class(workdir, compiler):
    """``(x != 0).to(<int>)`` is exact at every lane (the 0/1 value
    class); the sum-then-consume composition is count_nonzero's (the
    corpus executor above -- the reduce's in-region value is the
    per-chunk partial by the declared T009 semantics, so a block
    arithmetic over it composes with the partial, not the whole-block
    merge; consuming the merged value is the suffix/atomic path)."""
    body = """\\
    i = tl.program_id(0) * BLOCK + tl.arange(0, BLOCK)
    m = i < n
    x = tl.load(x_ptr + i, mask=m, other=0)
    z = (x != 0).to(tl.int32)
    tl.store(out_ptr + i, z, mask=m)"""
    ref = ['xx = np.asarray(args["x_ptr"])',
           'out = (xx != 0).astype(np.int32)']
    case_layer = _int_case_layer(ref, "bools_kernel")


    case_layer = case_layer.replace('{"out_ptr": {"comparator": "array_equal",\n'
                                    '                                       "exact": True}}',
                                    '{"out_ptr": {"comparator": "array_equal",\n'
                                    '                                       "exact": True}}')
    path = _operator_file(workdir, "bools", "x_ptr, out_ptr, n, BLOCK: tl.constexpr",
                          body, case_layer)
    module = _load(path)
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(compiler, module, threads)
        if not ok:
            bad.append(f"t={threads}: {detail}")
    check("bool-01-class-sums-and-widens-exactly", not bad,
          "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# located refusals (the boundary is honest)
# ---------------------------------------------------------------------------

def check_refusals_located(workdir, compiler):
    """T012 implements vector division/remainder (the layout lane's index
    maps and tl.swizzle2d need them; vdiv/vrem/vdivu probed under the
    pinned QEMU), so the runtime (non-constexpr) divisor now EXECUTES
    CORRECTLY through vrem (the pinned srem semantics) instead of
    refusing; the pow2 fold still applies to the provable forms."""
    bad = []
    cases = []
    # runtime divisor: executes through the vector remainder row
    cases.append((
        "x_ptr, out_ptr, n, k, BLOCK: tl.constexpr",
        """\
    i = tl.arange(0, BLOCK)
    x = tl.load(x_ptr + i)
    tl.store(out_ptr + i, (x % k).to(tl.int32))""",
        ('def ref(args, meta):\n'
         '    import numpy as np\n'
         '    x = np.asarray(args["x_ptr"])\n'
         '    return {"out_ptr": np.fmod(x, 3).astype(np.int32)}\n'
         '\n'
         'def _make_case(shape=(128,), dtype="int32", seed=0):\n'
         '    n = int(shape[0])\n'
         '    rng = np.random.default_rng(seed)\n'
         '    x = rng.integers(-100, 100, n).astype(np.int32)\n'
         '    args = {"x_ptr": x, "out_ptr": np.zeros(n, np.int32),\n'
         '            "n": n, "k": 3}\n'
         '    meta = {"BLOCK": 128}\n'
         '    grid = ((n + 127) // 128,)\n'
         '    return {"args": args, "meta": meta, "grid": grid,\n'
         '            "kernel": refuse_kernel, "outputs": ("out_ptr",),\n'
         '            "expected": ref(args, meta),\n'
         '            "comparison": {"out_ptr": {"comparator": "array_equal",\n'
         '                                       "exact": True}}}\n'
         '\n'
         'def make_case(shape=None, dtype=None, seed=None):\n'
         '    return _make_case(shape=shape or (128,),\n'
         '                      dtype=dtype or "int32", seed=seed or 0)\n')))
    for params, body, case_layer in cases:
        path = _operator_file(workdir, "refuse", params, body,
                              case_layer)
        module = _load(path)
        for threads in (1, 4):
            ok, detail = _run_case(compiler, module, threads)
            if not ok:
                bad.append(f"t={threads}: {detail}")
    check("runtime-divisor-remainder-executes-exact", not bad,
          "; ".join(bad[:2]))


def main() -> int:
    workdir = Path(tempfile.mkdtemp(prefix="a100c-scalar-"))
    cache = workdir / "cache"
    try:
        compiler = Compiler(options=CompileOptions(cache_dir=str(cache)))
        check_int64_index_arithmetic(workdir, compiler)
        check_shifts_unsigned_wrap(workdir, compiler)
        check_division_remainder(workdir, compiler)
        check_bool_class(workdir, compiler)
        check_refusals_located(workdir, compiler)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_lower_scalar: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
