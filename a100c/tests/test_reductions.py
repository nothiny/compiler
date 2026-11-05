#!/usr/bin/env python3
"""test_reductions.py -- reductions, scans and cross-worker merge
semantics (T009, gate G5).

  acceptance[0]: the reduction families' corpus operators that are inside
      the implemented surface execute and compare PASS at 1/2/4/8 threads
      -- mean (red.sum, axis selection + the accumulate-typing divide),
      reduce_kernel and pairwise_distance_max (single-program grids: the
      two-phase cross-worker split runs at 2/4/8), row_reduce_min
      (red.maxmin, multi-program strided partition), vdot_kernel_complex
      (pat.persistent_reduce: the persistent grid-stride loop with scalar
      accumulation).  The remaining family members need constructs owned
      by later lanes (see check_remaining_boundaries_refuse_located).
      Every reduction and scan construct itself is validated through
      equivalent executed forms with independent numpy references.

  acceptance[1]: empty-extent and single-element reductions are exact;
      argmax/argmin tie-break-left returns the declared (leftmost) index;
      integer and boolean reductions are exact (no tolerance).

  The stage-barrier witness (acceptance[2]/[3]) is
  tools/check_stage_barriers.py; the workspace ownership rejection is
  test_stage_plan.py.

Every executed check compares against a reference computed independently
of the compiler (numpy in this test), under the case's own policy.

Run: python3 a100c/tests/test_reductions.py   (exit 0 = all checks PASS)
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import textwrap
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
sys.path.insert(0, str(ROOT / "ops" / "harness"))

warnings.filterwarnings("ignore")

import numpy as np  # noqa: E402

from a100c.frontend import lower_tir, source, specialize  # noqa: E402
from a100c.frontend.source import FrontendError  # noqa: E402
from a100c.ir import tir  # noqa: E402

FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}", flush=True)
    if not ok:
        FAILURES.append(name)
    return ok


# ---------------------------------------------------------------------------
# TIR-level: the reduction contract carriers and the verifier's rejections
# ---------------------------------------------------------------------------


def check_tir_reduction_forms():
    """The frontend lowers every reduction construct to the TIR op that
    carries the contract: kind, axes, keep_dims, the per-op-and-dtype
    identity and the declared tie-break."""
    from a100c.plan import stages

    def lower(body):
        indented = textwrap.indent(body, "    ")
        text = PROBE % ("red", "red", "red", indented)
        src = source.load_operator_text(text, "<red>", "red.py")
        case = {"args": {"x_ptr": np.zeros(16, np.float32),
                         "o_ptr": np.zeros(16, np.float32), "n": 16},
                "meta": {"BLOCK": 16}, "grid": (1,), "outputs": ("o_ptr",)}
        spec = specialize.specialize(src, case)
        module = lower_tir.lower(src, spec)
        return module, tir.verify_module(module)

    m, errs = lower("""
        i = tl.arange(0, BLOCK)
        x = tl.load(x_ptr + i, mask=i < n, other=0.0)
        s = tl.sum(x, axis=0)
        mx = tl.max(x)
        mn = tl.min(x, axis=0)
        am = tl.argmax(x, 0, tie_break_left=True)
        an = tl.argmin(x, 0)
        v, ix = tl.min(x, 0, return_indices=True)
        xs = tl.xor_sum((x > 0).to(tl.int32), axis=0)
        ro = tl.reduce_or((x > 0).to(tl.int32), axis=0)
        cs = tl.cumsum(x, axis=0)
        cp = tl.cumprod(x, axis=0)
        tl.store(o_ptr, s + mx + mn + am + an + v + ix + xs + ro)
        tl.store(o_ptr + i, cs + cp)
    """)
    check("all-reduction-constructs-lower-and-verify", not errs,
          str(errs[:1]))
    ops = {}
    for st in m.functions[0].body.statements:
        if isinstance(st, tir.Op):
            ops.setdefault(st.op, []).append(st)
    reduces = ops.get("reduce", [])
    scans = ops.get("scan", [])
    ok = len(reduces) == 8 and len(scans) == 2
    check("tir-carries-eight-reduces-and-two-scans", ok,
          f"reduce={len(reduces)} scan={len(scans)}")
    kinds = [r.attrs["kind"] for r in reduces]
    want = {"sum", "max", "min", "argmax", "argmin", "xor_sum", "reduce_or"}
    check("reduce-kinds-carried", want <= set(kinds), str(kinds))
    for r in reduces:
        if r.attrs["kind"] in ("argmax", "argmin"):
            if not r.attrs.get("tie_break_left"):
                check("index-forms-carry-tie-break", False,
                      r.attrs["kind"])
        ident = r.attrs["identity"]
        ty = r.attrs.get("accumulate_type") or r.operands[0].type
        if ident != stages.identity_for(r.attrs["kind"], ty) and \
                r.attrs["kind"] not in ("argmax", "argmin"):
            check("identities-carried-from-the-table", False,
                  f"{r.attrs['kind']}: {ident}")
    check("identities-carried-from-the-table", True)
    # the return_indices form produces (value, index) with an i32 index
    ri = [r for r in reduces if r.attrs.get("return_indices")]
    ok = len(ri) == 1 and len(ri[0].results) == 2 and \
        ri[0].results[1].type == tir.INT32
    check("return-indices-pair-carried", ok)

    # softmax lowers as the declared SOFTMAX_COMPOSITE now that the
    # math-ops lane (T013) implemented exp: the composition is max-
    # subtract / exp / sum / divide -- the reduction structure with the
    # elementwise exp dependency (the T009 stub refused naming that
    # dependency; T013 completed it)
    try:
        m3, errs3 = lower("""
            i = tl.arange(0, BLOCK)
            x = tl.load(x_ptr + i)
            p = tl.softmax(x, dim=0)
            tl.store(o_ptr + i, p)
        """)
        ops3 = [st.op for fn in m3.functions
                for st in fn.body.statements if isinstance(st, tir.Op)]
        check("softmax-composes-exp", not errs3 and "math.exp" in ops3
              and "reduce" in ops3 and "arith.fdiv" in ops3,
              f"ops={sorted(set(ops3))[:6]}")
    except FrontendError as exc:
        check("softmax-composes-exp", False, str(exc)[:80])

    # sort / topk / histogram emit their TIR ops (the semantics are
    # declared; the whole-block reorder path refuses at the lowering)
    m2, errs2 = lower("""
        i = tl.arange(0, BLOCK)
        x = tl.load(x_ptr + i)
        s = tl.sort(x, descending=False)
        tl.store(o_ptr + i, s)
    """)
    ok = not errs2 and any(isinstance(st, tir.Op) and st.op == "sort"
                           for st in m2.functions[0].body.statements)
    check("sort-emits-tir-op", ok)

    # T016: topk and histogram emit their TIR ops too (the declared-
    # surface coverage evidence for the two reorder-family constructs
    # that had no emitting check)
    m4, errs4 = lower("""
        i = tl.arange(0, BLOCK)
        x = tl.load(x_ptr + i)
        t = tl.topk(x, 4)
        tl.store(o_ptr + tl.arange(0, 4), t)
    """)
    ok4 = not errs4 and any(isinstance(st, tir.Op) and st.op == "topk"
                            for st in m4.functions[0].body.statements)
    check("topk-emits-tir-op", ok4)

    m5, errs5 = lower("""
        i = tl.arange(0, BLOCK)
        x = tl.load(x_ptr + i)
        h = tl.histogram(tl.cast(x, tl.int32), num_bins=16)
        tl.store(o_ptr + tl.arange(0, 16), tl.cast(h, tl.float32))
    """)
    ok5 = not errs5 and any(isinstance(st, tir.Op) and st.op == "histogram"
                            for st in m5.functions[0].body.statements)
    check("histogram-emits-tir-op", ok5)


def check_tir_verifier_rejects_malformed():
    """Hand-built malformed reductions are rejected by the TIR verifier
    (one per invariant class: axis outside the rank, the wrong identity
    for the dtype's signedness, the wrong result shape, an index form
    without an index type)."""
    from a100c.plan import stages
    bad = []

    def verify(op):
        x = tir.Value(tir.FLOAT32, tir.real_shape([8]), name="x")
        fn = tir.Function("k", [])
        fn.body.statements.append(op)
        module = tir.Module("k", "<probe>")
        module.functions.append(fn)
        return tir.verify_module(module)

    # axis outside the rank
    r = tir.Op.reduce(tir.Value(tir.FLOAT32, tir.real_shape([8]),
                                name="x"), "sum", (1,), False,
                      stages.identity_for("sum", tir.FLOAT32))
    if not verify(r):
        bad.append("axis-not-rejected")
    # the wrong identity for the dtype (a signed min identity at fp32)
    r2 = tir.Op.reduce(tir.Value(tir.FLOAT32, tir.real_shape([8]),
                                 name="x"), "min", (0,), False, 0.0)
    if not verify(r2):
        bad.append("identity-not-rejected")
    # the wrong result shape
    x3 = tir.Value(tir.FLOAT32, tir.real_shape([8]), name="x")
    r3 = tir.Op.reduce(x3, "sum", (0,), False,
                       stages.identity_for("sum", tir.FLOAT32))
    r3.results[0].shape = tir.real_shape([4])
    if not verify(r3):
        bad.append("shape-not-rejected")
    # an index form producing a float
    x4 = tir.Value(tir.FLOAT32, tir.real_shape([8]), name="x")
    r4 = tir.Op.reduce(x4, "argmin", (0,), False,
                       stages.identity_for("argmin", tir.INT32))
    r4.results[0].type = tir.FLOAT32
    if not verify(r4):
        bad.append("index-type-not-rejected")
    # a scan with the wrong carry identity
    x5 = tir.Value(tir.INT32, tir.real_shape([8]), name="x")
    s5 = tir.Op.scan(x5, "cumprod", 0, False, 0)
    if not verify(s5):
        bad.append("scan-identity-not-rejected")
    check("tir-verifier-rejects-malformed-reductions", not bad,
          "; ".join(bad))
    # the control: the well-formed forms verify
    x6 = tir.Value(tir.INT32, tir.real_shape([8]), name="x")
    s6 = tir.Op.scan(x6, "cumprod", 0, False, 1)
    check("well-formed-scan-verifies", not verify(s6))


# ---------------------------------------------------------------------------
# End-to-end execution through the real pipeline (compile -> QEMU -> compare)
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
            'def %s_kernel(x_ptr, o_ptr, n, BLOCK: tl.constexpr):\n'
            '%s\n'
            '\n'
            'def ref(args, meta):\n'
            '    return {"o_ptr": np.zeros(4, np.float32)}\n'
            '\n'
            'def _make_case(shape=(257,), dtype="float32", seed=0):\n'
            '    return {"args": {"x_ptr": np.zeros(4, np.float32),\n'
            '                     "o_ptr": np.zeros(4, np.float32), "n": 16},\n'
            '            "meta": {"BLOCK": 128}, "grid": (1,)}\n')

PROBE = TEMPLATE


def _operator_file(directory: Path, name: str, body: str, ref_body: str,
                   args_decl: str = "x_ptr, o_ptr, n, BLOCK: tl.constexpr",
                   make_case: str = ""):
    """One probe operator: the kernel body plus a case layer whose numpy
    reference is written independently of the compiler."""
    ref_lines = "\n".join("    " + line for line in
                           textwrap.dedent(ref_body).strip("\n").splitlines())
    make_lines = "\n".join("    " + line for line in
                            textwrap.dedent(make_case).strip("\n").splitlines())
    text = (
        '"""probe operator"""\n'
        f'OPERATOR = {{"name": "probe/{name}", "group": "probe", "channel": "local",\n'
        '            "execution": "triton_kernel", "verification": "correctness",\n'
        '            "tags": []}\n'
        'SHAPES = ((257,), (4, 97))\n'
        'import numpy as np\n'
        'import triton\n'
        'import triton.language as tl\n'
        '\n'
        '@triton.jit\n'
        f'def {name}_kernel({args_decl}):\n'
        + textwrap.indent(textwrap.dedent(body).strip("\n"), "    ") + '\n\n'
        'def ref(args, meta):\n'
        '    import numpy as np\n'
        f'{ref_lines}\n'
        '\n'
        'def _make_case(shape=(257,), dtype="float32", seed=0):\n'
        '    import numpy as np\n'
        '    rng = np.random.default_rng(seed)\n'
        f'{make_lines}\n'
        '\n'
        'def make_case(shape=None, dtype=None, seed=None):\n'
        '    return _make_case(shape=shape or (257,),\n'
        '                      dtype=dtype or "float32", seed=seed or 0)\n')
    text = text.replace("_KERNEL_REF_", f"{name}_kernel")
    path = directory / f"{name}.py"
    path.write_text(text)
    return path


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_case(compiler, module, threads: int, **make_kwargs):
    import a100_support.native_device as nd
    case = module.make_case(**make_kwargs)
    device = nd.NativeExecutableDevice(compiler, threads)
    staged = device.stage_case(case)
    staged.launch()
    outputs = staged.outputs()
    ok, detail = True, ""
    for name, policy in case["comparison"].items():
        got = np.asarray(outputs[name])
        exp = np.asarray(case["expected"][name])
        if policy.get("exact") or policy["comparator"] == "array_equal":
            same = np.array_equal(got, exp)
        else:
            same = np.allclose(got, exp, rtol=policy.get("rtol", 0.0),
                               atol=policy.get("atol", 0.0),
                               equal_nan=policy.get("equal_nan", False))
        if not same:
            ok = False
            detail = f"{name}: got {np.ravel(got)[:4]} " \
                     f"expected {np.ravel(exp)[:4]}"
    return ok, detail


STD_MAKE = textwrap.dedent("""
    n = int(shape[0])
    x = rng.uniform(-2.0, 2.0, (n,)).astype(np.float32)
    args = {"x_ptr": x, "o_ptr": np.zeros(8, np.float32), "n": n}
    meta = {"BLOCK": 128}
    expected = ref(args, meta)
    e = np.asarray(expected["o_ptr"], np.float32).ravel()
    out = np.zeros(8, np.float32)
    out[:len(e)] = e
    expected["o_ptr"] = out
    return {"args": args, "meta": meta, "grid": (1,),
            "kernel": _KERNEL_REF_,
            "outputs": ("o_ptr",), "expected": expected,
            "comparison": {"o_ptr": {"comparator": "allclose",
                                     "exact": False,
                                     "rtol": 1e-5, "atol": 1e-5}}}
""")

#: scalar-output forms: STD_MAKE (a small o_ptr, the expected padded)
SCALAR_MAKE = STD_MAKE

#: tie-heavy inputs: many duplicated extrema (a half-integer grid), so
#: the argmax/argmin tie-break is exercised on nearly every case
TIE_MAKE = textwrap.dedent("""
    n = int(shape[0])
    x = (np.round(rng.uniform(-2.0, 2.0, (n,)) * 2) / 2).astype(np.float32)
    args = {"x_ptr": x, "o_ptr": np.zeros(8, np.float32), "n": n}
    meta = {"BLOCK": 128}
    expected = ref(args, meta)
    e = np.asarray(expected["o_ptr"], np.float32).ravel()
    out = np.zeros(8, np.float32)
    out[:len(e)] = e
    expected["o_ptr"] = out
    return {"args": args, "meta": meta, "grid": (1,),
            "kernel": _KERNEL_REF_,
            "outputs": ("o_ptr",), "expected": expected,
            "comparison": {"o_ptr": {"comparator": "allclose",
                                     "exact": False,
                                     "rtol": 1e-5, "atol": 1e-5}}}
""")

#: integer forms: exact comparison (no tolerance)
INT_MAKE = textwrap.dedent("""
    n = int(shape[0])
    x = rng.integers(-100000, 100000, (n,)).astype(np.int32)
    args = {"x_ptr": x, "o_ptr": np.zeros(8, np.int32), "n": n}
    meta = {"BLOCK": 128}
    expected = ref(args, meta)
    e = np.asarray(expected["o_ptr"], np.int32).ravel()
    out = np.zeros(8, np.int32)
    out[:len(e)] = e
    expected["o_ptr"] = out
    return {"args": args, "meta": meta, "grid": (1,),
            "kernel": _KERNEL_REF_,
            "outputs": ("o_ptr",), "expected": expected,
            "comparison": {"o_ptr": {"comparator": "array_equal",
                                     "exact": True}}}
""")

#: block-output forms (scans): the output is the block itself
BLOCK_MAKE = textwrap.dedent("""
    n = int(shape[0])
    x = rng.uniform(-2.0, 2.0, (n,)).astype(np.float32)
    args = {"x_ptr": x, "o_ptr": np.zeros(n, np.float32), "n": n}
    meta = {"BLOCK": 128}
    expected = ref(args, meta)
    return {"args": args, "meta": meta, "grid": (1,),
            "kernel": _KERNEL_REF_,
            "outputs": ("o_ptr",), "expected": expected,
            "comparison": {"o_ptr": {"comparator": "allclose",
                                     "exact": False,
                                     "rtol": 1e-5, "atol": 1e-5}}}
""")


def check_executed_reduction_forms(workdir, compiler):
    """Every reduction and scan construct executes end to end under QEMU
    and compares PASS against an independent numpy reference -- at one
    worker and at four (the two-phase split for the single-program
    forms).  The shapes stay within one block (a single program covers
    BLOCK lanes; the persistent form loops past it)."""
    forms = []

    forms.append(("red_sum", """
        i = tl.arange(0, BLOCK)
        x = tl.load(x_ptr + i, mask=i < n, other=0.0)
        tl.store(o_ptr, tl.sum(x, axis=0))
    """, """
        x = np.asarray(args["x_ptr"], np.float64)
        return {"o_ptr": np.array([x.sum()], np.float32)}
    """, SCALAR_MAKE))

    forms.append(("red_max", """
        i = tl.arange(0, BLOCK)
        x = tl.load(x_ptr + i, mask=i < n, other=-1e30)
        tl.store(o_ptr, tl.max(x, axis=0))
    """, """
        x = np.asarray(args["x_ptr"], np.float64)
        return {"o_ptr": np.array([x.max()], np.float32)}
    """, SCALAR_MAKE))

    forms.append(("red_min_where", """
        i = tl.arange(0, BLOCK)
        x = tl.load(x_ptr + i, mask=i < n, other=0.0)
        y = tl.where(i < n, x, 1e30)
        tl.store(o_ptr, tl.min(y, axis=0))
    """, """
        x = np.asarray(args["x_ptr"], np.float64)
        return {"o_ptr": np.array([x.min()], np.float32)}
    """, SCALAR_MAKE))

    forms.append(("red_argmax_tie_left", """
        i = tl.arange(0, BLOCK)
        x = tl.load(x_ptr + i, mask=i < n, other=-1e30)
        tl.store(o_ptr, tl.argmax(x, 0, tie_break_left=True))
    """, """
        x = np.asarray(args["x_ptr"])
        return {"o_ptr": np.array([int(np.argmax(x))], np.float32)}
    """, TIE_MAKE))

    forms.append(("red_argmin_tie_left", """
        i = tl.arange(0, BLOCK)
        x = tl.load(x_ptr + i, mask=i < n, other=1e30)
        tl.store(o_ptr, tl.argmin(x, 0))
    """, """
        x = np.asarray(args["x_ptr"])
        return {"o_ptr": np.array([int(np.argmin(x))], np.float32)}
    """, TIE_MAKE))

    forms.append(("red_return_indices", """
        i = tl.arange(0, BLOCK)
        x = tl.load(x_ptr + i, mask=i < n, other=-1e30)
        v, ix = tl.max(x, 0, return_indices=True,
                       return_indices_tie_break_left=True)
        tl.store(o_ptr, v)
        tl.store(o_ptr + 1, ix)
    """, """
        x = np.asarray(args["x_ptr"])
        return {"o_ptr": np.array([x.max(), float(np.argmax(x))],
                                  np.float32)}
    """, TIE_MAKE))

    forms.append(("red_sum_int_exact", """
        i = tl.arange(0, BLOCK)
        x = tl.load(x_ptr + i, mask=i < n, other=0)
        tl.store(o_ptr, tl.sum(x, axis=0))
    """, """
        x = np.asarray(args["x_ptr"], np.int64)
        return {"o_ptr": np.array([int(x.sum())], np.int32)}
    """, INT_MAKE))

    forms.append(("red_xor_or_exact", """
        i = tl.arange(0, BLOCK)
        x = tl.load(x_ptr + i, mask=i < n, other=0)
        a = tl.xor_sum(x, axis=0)
        b = tl.reduce_or(x, axis=0)
        tl.store(o_ptr, a)
        tl.store(o_ptr + 1, b)
    """, """
        x = np.asarray(args["x_ptr"], np.int64)
        return {"o_ptr": np.array([int(np.bitwise_xor.reduce(x)),
                                   int(np.bitwise_or.reduce(x))],
                                  np.int32)}
    """, INT_MAKE))

    forms.append(("red_cumsum", """
        i = tl.arange(0, BLOCK)
        x = tl.load(x_ptr + i, mask=i < n, other=0.0)
        tl.store(o_ptr + i, tl.cumsum(x, axis=0), mask=i < n)
    """, """
        x = np.asarray(args["x_ptr"], np.float32)
        out = np.zeros(len(x), np.float32)
        out[:len(x)] = np.cumsum(x)
        return {"o_ptr": out}
    """, BLOCK_MAKE))

    forms.append(("red_cumprod", """
        i = tl.arange(0, BLOCK)
        x = tl.load(x_ptr + i, mask=i < n, other=1.0)
        tl.store(o_ptr + i, tl.cumprod(x, axis=0), mask=i < n)
    """, """
        x = np.asarray(args["x_ptr"], np.float32)
        out = np.zeros(len(x), np.float32)
        out[:len(x)] = np.cumprod(x)
        return {"o_ptr": out}
    """, BLOCK_MAKE))

    # the persistent two-phase form: one program, chunks looped inside it
    forms.append(("red_persistent_two_phase", """
        acc = tl.zeros([], dtype=tl.float32)
        for start in range(0, n, BLOCK):
            i = start + tl.arange(0, BLOCK)
            x = tl.load(x_ptr + i, mask=i < n, other=0.0)
            acc += tl.sum(x, axis=0)
        tl.store(o_ptr, acc)
    """, """
        x = np.asarray(args["x_ptr"], np.float64)
        return {"o_ptr": np.array([x.sum()], np.float32)}
    """, SCALAR_MAKE))

    bad = []
    for name, body, ref_body, make in forms:
        path = _operator_file(workdir, name, body, ref_body, make_case=make)
        module = _load(path)
        for threads in (1, 4):
            for shape in ((97,), (33,), (1,), (257,)):
                if shape[0] > 128 and name != "red_persistent_two_phase":
                    continue   # one program covers BLOCK lanes only
                try:
                    ok, detail = _run_case(compiler, module, threads,
                                           shape=shape)
                except Exception as exc:  # noqa: BLE001
                    ok, detail = False, f"{type(exc).__name__}: " \
                                        f"{str(exc)[:120]}"
                if not ok:
                    bad.append(f"{name} t={threads} s={shape}: {detail}")
        status = "bad" if any(b.startswith(name + " ") for b in bad) \
            else "ok "
        print(f"  {status} {name}", flush=True)
    check("reduction-and-scan-forms-execute-and-compare", not bad,
          "; ".join(bad[:3]))


def check_empty_and_single_element(workdir, compiler):
    """acceptance[1]: empty-extent (all lanes masked off -> the identity
    path) and single-element reductions are exact; the tie-break index is
    the declared leftmost."""
    # single element: n=1 -> one active lane, everything else masked
    body = """
        i = tl.arange(0, BLOCK)
        xs = tl.load(x_ptr + i, mask=i < n, other=0.0)
        xm = tl.load(x_ptr + i, mask=i < n, other=-1e30)
        xn = tl.load(x_ptr + i, mask=i < n, other=1e30)
        s = tl.sum(xs, axis=0)
        m = tl.max(xm, axis=0)
        a = tl.argmin(xn, 0)
        tl.store(o_ptr, s)
        tl.store(o_ptr + 1, m)
        tl.store(o_ptr + 2, a)
    """
    ref = """
        x = np.asarray(args["x_ptr"], np.float64)
        return {"o_ptr": np.array([x.sum(), x.max(),
                                   float(np.argmin(x))], np.float32)}
    """
    make = textwrap.dedent("""
        n = int(shape[0])
        x = rng.uniform(-3.0, 3.0, (n,)).astype(np.float32)
        args = {"x_ptr": x, "o_ptr": np.zeros(8, np.float32), "n": n}
        meta = {"BLOCK": 128}
        expected = ref(args, meta)
        e = np.asarray(expected["o_ptr"], np.float32).ravel()
        out = np.zeros(8, np.float32)
        out[:len(e)] = e
        expected["o_ptr"] = out
        return {"args": args, "meta": meta, "grid": (1,),
                "kernel": _KERNEL_REF_,
                "outputs": ("o_ptr",), "expected": expected,
                "comparison": {"o_ptr": {"comparator": "allclose",
                                         "exact": False,
                                         "rtol": 1e-6, "atol": 1e-6}}}
    """)
    path = _operator_file(workdir, "red_single", body, ref, make_case=make)
    module = _load(path)
    bad = []
    for threads in (1, 4):
        for shape in ((1,), (2,)):
            ok, detail = _run_case(compiler, module, threads, shape=shape)
            if not ok:
                bad.append(f"t={threads} s={shape}: {detail}")
    check("single-element-reduction-exact", not bad, "; ".join(bad[:2]))

    # empty extent: n=0 -> every lane masked; the sum is the exact
    # identity 0, the max over other-filled zeros is 0.0 (the declared
    # disabled-position value participates)
    body2 = """
        i = tl.arange(0, BLOCK)
        x = tl.load(x_ptr + i, mask=i < n, other=0.0)
        tl.store(o_ptr, tl.sum(x, axis=0))
    """
    ref2 = """
        return {"o_ptr": np.array([0.0], np.float32)}
    """
    make2 = textwrap.dedent("""
        n = 0
        x = np.zeros(1, np.float32)
        args = {"x_ptr": x, "o_ptr": np.zeros(4, np.float32), "n": 0}
        meta = {"BLOCK": 128}
        expected = ref(args, meta)
        e = np.asarray(expected["o_ptr"], np.float32).ravel()
        out = np.zeros(4, np.float32)
        out[:len(e)] = e
        expected["o_ptr"] = out
        return {"args": args, "meta": meta, "grid": (1,),
                "kernel": _KERNEL_REF_,
                "outputs": ("o_ptr",), "expected": expected,
                "comparison": {"o_ptr": {"comparator": "array_equal",
                                         "exact": True}}}
    """)
    path2 = _operator_file(workdir, "red_empty", body2, ref2,
                           make_case=make2)
    module2 = _load(path2)
    bad2 = []
    for threads in (1, 4):
        try:
            ok, detail = _run_case(compiler, module2, threads, shape=(1,))
            if not ok:
                bad2.append(f"t={threads}: {detail}")
        except Exception as exc:  # noqa: BLE001
            bad2.append(f"t={threads}: {str(exc)[:100]}")
    check("empty-extent-reduction-exact-identity", not bad2,
          "; ".join(bad2[:2]))


def check_corpus_reduction_operators(compiler):
    """acceptance[0]: the reduction families' corpus operators inside the
    implemented surface execute and compare PASS at 1/2/4/8 threads (the
    single-program grids run the two-phase cross-worker split at
    2/4/8)."""
    ops = [
        ("ops/suite/perf/mean.py", {"shape": (4, 97),
                                    "dtype": "float32"}, "red.sum"),
        ("ops/suite/dev/reduce_kernel.py", {"shape": (97,),
                                            "dtype": "float32"},
         "red.sum+if_pid"),
        ("ops/suite/dev/pairwise_distance_max_kernel_2.py",
         {"shape": (97,), "dtype": "float32"}, "red.maxmin"),
        ("ops/suite/dev/row_reduce_min_kernel.py",
         {"shape": (17, 128), "dtype": "float32"}, "red.maxmin+axis"),
        ("ops/suite/dev/vdot_kernel_complex.py",
         {"shape": (97,), "dtype": "float32"}, "pat.persistent_reduce"),
    ]
    bad = []
    for rel, kwargs, tag in ops:
        module = _load(ROOT / rel)
        for threads in (1, 2, 4, 8):
            try:
                ok, detail = _run_case(compiler, module, threads, **kwargs)
            except Exception as exc:  # noqa: BLE001
                ok, detail = False, f"{type(exc).__name__}: " \
                                    f"{str(exc)[:120]}"
            if not ok:
                bad.append(f"{tag} t={threads}: {detail}")
        print(f"  {'ok ' if not any(b.startswith(tag + ' ') for b in bad) else 'bad'} {tag} {rel}", flush=True)
    check("corpus-reduction-operators-execute-1-2-4-8", not bad,
          "; ".join(bad[:3]))


def check_remaining_boundaries_refuse_located(compiler):
    """The remaining family members need constructs owned by later lanes;
    they refuse with located diagnostics naming the missing construct
    (never a silent miscompile), and the fp16/int64 cases refuse on the
    element-width boundary."""
    from a100c.driver import PipelineError
    bad = []
    cases = [
        # argmin_kernel_contiguous: T027 tied its grid (the n_pre*s_post
        # subtree reads the out_ptr view extent at run time), so the
        # float32 case compiles and executes PASS now (verified in
        # T027's execution probe); the fp16 case refuses deeper, at the
        # multi-width reduction lane
        ("ops/suite/dev/argmin_kernel_contiguous.py",
         {"shape": (128, 128, 2), "dtype": "float16"},
         ("SEW", "multi-width", "reduce")),
        # loop_sum: the identity .to(float32) folds, but the int64
        # median family refuses on the element width
        # T012 widened the conversion matrix, so the int64 element path
        # now reaches the scalar bool store boundary instead of the
        # element-width refusal -- both are located refusals naming the
        # construct that is out of the lane
        ("ops/suite/dev/median_bool_from_counts_kernel.py",
         {"shape": (17, 3)},
         ("width 64", "SEW", "scalar bool stores", "scalar core")),
        # cumsum family: T016 closed the meta-carried dtype-object
        # boundary (tl.zeros((), dtype=ACC_KIND) with the live tl.float32
        # constant in the case meta now folds), so the refusal moved to
        # the partial-axis multi-block reduction (the T018 compile-sweep
        # class) -- still a located refusal naming the missing construct
        ("ops/suite/dev/masked_cumsum_vec_kernel.py",
         {"shape": (17, 257), "dtype": "float32"},
         ("multi-axis", "partial axis", "rank 1")),
        # sort family: T012 implements flip, so the file's refusal boundary
        # moved past it -- it now refuses on tl.softmax's exp (the
        # math-ops lane owns that construct)
        ("ops/suite/dev/ranked_distribution_semantic.py",
         {"shape": (16,), "dtype": "float32"},
         ("softmax", "exp", "math-ops", "flip", "gather", "cast")),
    ]
    for rel, kwargs, needles in cases:
        module = _load(ROOT / rel)
        try:
            compiler.compile_case(module.make_case(**kwargs))
            bad.append(f"{rel}: compiled (expected a located refusal)")
        except PipelineError as exc:
            if not any(n in str(exc) for n in needles):
                bad.append(f"{rel}: {str(exc)[:110]}")
        except Exception as exc:  # noqa: BLE001
            bad.append(f"{rel}: wrong error type {type(exc).__name__}: "
                       f"{str(exc)[:80]}")
    check("remaining-family-boundaries-refuse-located", not bad,
          "; ".join(bad[:2]))


def main() -> int:
    workdir = Path(tempfile.mkdtemp(prefix="a100c-red-"))
    cache = workdir / "cache"
    try:
        from a100c.driver import Compiler, CompileOptions
        compiler = Compiler(options=CompileOptions(cache_dir=str(cache)))

        check_tir_reduction_forms()
        check_tir_verifier_rejects_malformed()
        check_executed_reduction_forms(workdir, compiler)
        check_empty_and_single_element(workdir, compiler)
        check_corpus_reduction_operators(compiler)
        check_remaining_boundaries_refuse_located(compiler)
    finally:
        import shutil
        shutil.rmtree(workdir, ignore_errors=True)
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_reductions: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
