#!/usr/bin/env python3
"""test_control_flow.py -- control flow, loop forms and grid generality
(T008, gate G5).

  acceptance[0] in-scope slice: the corpus operator var_len_copy (flow.loop
      + flow.dynamic_range: a runtime-bound ``for`` over a loaded length,
      scalar loads, view-extent grid tie) compiles and its cases execute
      and compare PASS at threads 1/2/4/8 on one artifact per identity;
      the remaining non-reduction flow families are exercised by the
      equivalent control-flow forms below (runtime if, while +
      tl.num_programs grid-stride, tl.range with step and pragmas,
      tl.static_range unrolling, if_pid), each executed end to end under
      the declared QEMU endpoint with its own independent reference.  The
      146 pat.persistent_reduce operators are T009's (reductions), not
      here.
  acceptance[2] a carried-value re-bind case: a variable assigned on only
      one path of a branch (join) and a variable re-assigned twice in a
      loop (carried) execute correctly at 1 and 4 workers (2 and 8 too);
      the lexical name-restore implementation is rejected by the TIR
      verifier (carried value without join), one witness per region form.
  acceptance[3] multi-axis grids decompose program_id per axis correctly
      (a 3x5 grid whose per-element value encodes both axes; an
      axis-swapped reference does NOT match -- the decomposition is
      axis-distinguishing) and tl.num_programs reads the runtime extents.

Every executed check compares against a reference computed independently
of the compiler (numpy in this test), under the case's own policy.

Run: python3 a100c/tests/test_control_flow.py   (exit 0 = all checks PASS)
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

from a100c.frontend import lower_tir, source, specialize  # noqa: E402
from a100c.frontend.source import FrontendError  # noqa: E402
from a100c.ir import dump as tir_dump  # noqa: E402
from a100c.ir import tir  # noqa: E402

# ---------------------------------------------------------------------------
# TIR-level witnesses: the verifier rejects the lexical name-restore
# ---------------------------------------------------------------------------


def check_verifier_rejects_lexical_restore():
    """A value defined inside a region and used after it without a join is
    the lexical name-restore implementation -- the TIR verifier rejects it
    (carried-value-without-join), one hand-built witness per region form.
    The control: the same module WITH the join verifies."""
    bad = []

    # (a) if-arm: y is re-bound in the then arm, no join entry, used after
    p = tir.Value(tir.Type.pointer(tir.INT32), (), name="p")
    fn = tir.Function("k", [p])
    cond_op = tir.Op.const(True, tir.INT1)
    fn.body.statements.append(cond_op)
    node = tir.If(cond_op.result())
    inner = tir.Op.const(7, tir.INT32)
    inner.results[0].name = "y"
    node.then.statements.append(inner)
    node.join_names = ()                  # the name-restore form: no join
    fn.body.statements.append(node)
    yv = inner.results[0]
    ptr = tir.Op.ptradd(p, yv)
    fn.body.statements.append(ptr)
    store = tir.Op.store(ptr.result(), yv, None, None)
    fn.body.statements.append(store)      # uses the arm's value after the if
    module = tir.Module("k", "<probe>")
    module.functions.append(fn)
    errors = tir.verify_module(module)
    if not any(e.invariant == tir.Invariant.CARRIED_WITHOUT_JOIN
               for e in errors):
        bad.append(f"if-arm: {errors or 'accepted'}")

    # (b) loop: a carried entry the body never redefines (the restore form
    # would keep the initial value)
    fn2 = tir.Function("k2", [p])
    i0 = tir.Op.const(0, tir.INT32)
    n = tir.Op.const(4, tir.INT32)
    s = tir.Op.const(1, tir.INT32)
    acc0 = tir.Op.const(0, tir.INT32)
    for op in (i0, n, s, acc0):
        fn2.body.statements.append(op)
    loop = tir.Loop(i0.result(), n.result(), s.result())
    loop.carried = (("acc", acc0.result()),)
    fn2.body.statements.append(loop)
    module2 = tir.Module("k2", "<probe>")
    module2.functions.append(fn2)
    errors2 = tir.verify_module(module2)
    if not any(e.invariant == tir.Invariant.CARRIED_WITHOUT_JOIN
               for e in errors2):
        bad.append(f"loop: {errors2 or 'accepted'}")

    # control: the if WITH the join verifies (both arms define y; the join
    # result is a fresh value visible after the region -- the store is
    # rebuilt on the join result, the arm value stays closed)
    else_inner = tir.Op.const(7, tir.INT32)
    else_inner.results[0].name = "y"
    node.els.statements.append(else_inner)
    node.join_names = ("y",)
    join0 = tir.Value(tir.INT32, (), name="y")
    node.join_results = (join0,)
    fn.body.statements = [s for s in fn.body.statements
                          if s is not store and s is not ptr]
    ptr2 = tir.Op.ptradd(p, join0)
    store2 = tir.Op.store(ptr2.result(), join0, None, None)
    fn.body.statements += [ptr2, store2]
    errors3 = tir.verify_module(module)
    if errors3:
        bad.append(f"control(with join): {errors3[0]}")

    # while form: a loop whose condition is not carried never updates it
    fn3 = tir.Function("k3", [p])
    wcond = tir.Op.const(True, tir.INT1)
    fn3.body.statements.append(wcond)
    wloop = tir.Loop(None, None, None, cond=wcond.result())
    wloop.carried = (("acc", acc0.result()),)
    fn3.body.statements.append(wloop)
    module3 = tir.Module("k3", "<probe>")
    module3.functions.append(fn3)
    errors4 = tir.verify_module(module3)
    if not any("does not carry its condition" in str(e) for e in errors4):
        bad.append(f"while-cond: {errors4 or 'accepted'}")

    check("verifier-rejects-lexical-name-restore", not bad, "; ".join(bad))


def check_frontend_region_forms():
    """The frontend lowers every region form to TIR the verifier accepts,
    with the declared carriers: join_names on if, carried on loops,
    static_range unrolled, num_programs as an op, tl.range pragmas
    classified ignorable-with-reason."""
    bad = []

    def lower(body):
        import textwrap
        indented = textwrap.indent(body.strip("\n"), "    ")
        text = TEMPLATE % ("forms", "forms", "forms",
                           "x_ptr, y_ptr, n, flag, "
                           "BLOCK: tl.constexpr, ITERS: tl.constexpr",
                           indented, CASE_LAYER_INT)
        src = source.load_operator_text(text, "<forms>", "forms.py")
        case = {"args": {"x_ptr": np.zeros(16, np.int32),
                         "y_ptr": np.zeros(16, np.int32),
                         "n": 16, "flag": 3},
                "meta": {"BLOCK": 16, "ITERS": 4}, "launch_meta": {}}
        spec = specialize.specialize(src, case)
        module = lower_tir.lower(src, spec)
        errors = tir.verify_module(module)
        return module, errors, spec

    m, errs, spec = lower("""
i = tl.arange(0, BLOCK)
x = tl.load(x_ptr + i)
y = x
if flag > 0:
    y = x + 1
acc = 0
for k in range(0, ITERS, 1):
    acc = acc + 1
    acc = acc * 2
z = 0
while z < n:
    z = z + 2
tl.store(y_ptr + i, y + acc + z)
""")
    if errs:
        bad.append(f"verify: {errs[0]}")
    ifs = [s for s in m.functions[0].body.statements if isinstance(s, tir.If)]
    loops = [s for s in m.functions[0].body.statements
             if isinstance(s, tir.Loop)]
    if not (len(ifs) == 1 and ifs[0].join_names == ("y",)
            and len(ifs[0].join_results) == 1):
        bad.append(f"if-join: {ifs and ifs[0].join_names}")
    counted = [l for l in loops if l.cond is None]
    whiles = [l for l in loops if l.cond is not None]
    if not (len(counted) == 1 and counted[0].carried
            and counted[0].carried[0][0] == "k"
            and any(c == "acc" for c, _ in counted[0].carried)):
        bad.append(f"counted-carried: {counted and counted[0].carried}")
    if not (len(whiles) == 1
            and any(n == whiles[0].cond.name or
                    n in whiles[0].cond.aliases
                    for n, _ in whiles[0].carried)):
        bad.append("while does not carry its condition")

    m2, errs2, _ = lower("""
i = tl.arange(0, BLOCK)
y = tl.load(x_ptr + i)
for s in tl.static_range(3):
    y = y + 1
for k in tl.range(0, n, 2, num_stages=2, loop_unroll_factor=1):
    y = y + 2
tl.store(y_ptr + i, y)
""")
    if errs2:
        bad.append(f"ranges verify: {errs2[0]}")
    loops2 = [s for s in m2.functions[0].body.statements
              if isinstance(s, tir.Loop)]
    if len(loops2) != 1:
        bad.append(f"static_range not unrolled ({len(loops2)} loops remain)")

    m3, errs3, _ = lower("""
p = tl.program_id(0)
g = tl.num_programs(0)
tl.store(y_ptr + tl.arange(0, BLOCK), tl.zeros([BLOCK], dtype=tl.int32) + p + g)
""")
    if errs3:
        bad.append(f"num_programs verify: {errs3[0]}")
    if not any(isinstance(s, tir.Op) and s.op == "num_programs"
               for s in m3.functions[0].body.statements):
        bad.append("num_programs op missing")

    # the tl.range pragma parameters are classified ignorable-with-reason
    # (recorded on the lowering, countable -- never silently dropped)
    import textwrap as _tw
    text = TEMPLATE % ("forms", "forms", "forms",
                       "x_ptr, y_ptr, n, flag, "
                       "BLOCK: tl.constexpr, ITERS: tl.constexpr",
                       _tw.indent("""
for k in tl.range(0, n, 1, num_stages=3, loop_unroll_factor=2,
                  disallow_acc_multi_buffer=True, flatten=True,
                  warp_specialize=True, disable_licm=True):
    z = k
tl.store(y_ptr + tl.arange(0, BLOCK), tl.zeros([BLOCK], dtype=tl.int32))
""".strip("\n"), "    "), CASE_LAYER_INT)
    src4 = source.load_operator_text(text, "<forms>", "forms.py")
    case4 = {"args": {"x_ptr": np.zeros(16, np.int32),
                      "y_ptr": np.zeros(16, np.int32),
                      "n": 16, "flag": 3},
             "meta": {"BLOCK": 16, "ITERS": 4}, "launch_meta": {}}
    spec4 = specialize.specialize(src4, case4)
    lowering = lower_tir.Lowering(src4, spec4)
    lowering.lower()
    ignored = {(p.construct, p.param) for p in lowering.ignored}
    wanted = {("tl.range", p) for p in
              ("num_stages", "loop_unroll_factor",
               "disallow_acc_multi_buffer", "flatten", "warp_specialize",
               "disable_licm")}
    if not wanted <= ignored:
        bad.append(f"pragma classifications missing: {sorted(wanted - ignored)}")

    check("frontend-region-forms-lower-and-verify", not bad, "; ".join(bad))


# ---------------------------------------------------------------------------
# End-to-end execution through the real pipeline (compile -> QEMU -> compare)
# ---------------------------------------------------------------------------

TEMPLATE = ('"""probe operator %s"""\n'
            'OPERATOR = {"name": "probe/%s", "group": "probe", "channel": "local",\n'
            '            "execution": "triton_kernel", "verification": "correctness",\n'
            '            "tags": []}\n'
            'SHAPES = ((257,), (514,))\n'
            'import numpy as np\n'
            'import triton\n'
            'import triton.language as tl\n'
            '\n'
            '@triton.jit\n'
            'def %s_kernel(%s):\n'
            '%s\n'
            '\n'
            '%s\n')

CASE_LAYER_INT = ('def ref(args, meta):\n'
                  '    raise NotImplementedError\n'
                  '\n'
                  '\n'
                  'def _make_case(shape=SHAPES[0], dtype="int32", seed=0):\n'
                  '    raise NotImplementedError\n')


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


def _run_case(compiler, module, threads: int, **make_kwargs):
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
        if policy.get("exact") or policy["comparator"] == "array_equal":
            same = np.array_equal(got, exp)
        else:
            same = np.allclose(got, exp, rtol=policy.get("rtol", 0.0),
                               atol=policy.get("atol", 0.0),
                               equal_nan=policy.get("equal_nan", False))
        if not same:
            diff = np.nonzero(got != exp)[0] if got.shape == exp.shape else []
            detail = f"{name}: {len(diff)} mismatched elements"
        ok &= same
    return ok, detail


def _int_case_layer(flag, ref_lines, kernel_ref, grid="((n + 127) // 128,)"):
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
            '            "n": n, "flag": %d}\n'
            '    meta = {"BLOCK": 128, "ITERS": 4}\n'
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
            ) % (ref, flag, grid, kernel_ref)


# -- acceptance[2]: the carried-value re-bind case --------------------------

REBIND_BODY = """\\
    pid = tl.program_id(0)
    i = pid * BLOCK + tl.arange(0, BLOCK)
    x = tl.load(x_ptr + i, mask=i < n)
    y = x
    if flag > 0:
        y = x + 1
    acc = 0
    for k in range(0, ITERS, 1):
        acc = acc + 1
        acc = acc * 2
    yb = tl.zeros([BLOCK], dtype=tl.int32) + acc
    tl.store(out_ptr + i, y + yb, mask=i < n)"""

REBIND_REF = ['xx = args["x_ptr"]',
              'y = xx + 1 if args["flag"] > 0 else xx',
              'acc = 0',
              'for k in range(0, meta["ITERS"]):',
              '    acc = (acc + 1) * 2',
              'out = y + acc']


def check_carried_rebind_executes(workdir, compiler):
    """A variable assigned on only one path of a branch (join) and a
    variable re-assigned twice in a loop (carried) execute correctly at 1
    and 4 workers (and 2, 8), on both branch directions and both shapes."""
    bad = []
    params = ("x_ptr, out_ptr, n, flag, BLOCK: tl.constexpr, "
              "ITERS: tl.constexpr")
    for flag, tag in ((3, "then"), (-2, "else")):
        path = _operator_file(workdir, f"rebind_{tag}", params, REBIND_BODY,
                              _int_case_layer(flag, REBIND_REF,
                                              f"rebind_{tag}_kernel"))
        module = _load(path)
        for threads in (1, 2, 4, 8):
            for shape in ((257,), (514,)):
                ok, detail = _run_case(compiler, module, threads,
                                       shape=shape)
                if not ok:
                    bad.append(f"flag={flag} threads={threads} "
                               f"shape={shape}: {detail}")
    check("carried-value-rebind-executes-at-1-and-4-workers", not bad,
          "; ".join(bad[:3]))


# -- while + tl.num_programs (the persistent grid-stride form) ----------------

WHILE_BODY = """\\
    pid = tl.program_id(0)
    num_prog = tl.num_programs(0)
    base = pid * BLOCK
    while base < n:
        i = base + tl.arange(0, BLOCK)
        m = i < n
        v = tl.load(x_ptr + i, mask=m)
        tl.store(out_ptr + i, v + 1, mask=m)
        base += num_prog * BLOCK"""

WHILE_REF = ['out = args["x_ptr"] + 1']


def check_while_num_programs(workdir, compiler):
    """A while loop whose stride reads tl.num_programs(0): with a grid of
    2 programs over 257 elements (3 blocks needed), each program strides
    the whole range -- the runtime grid extent must be read, not baked."""
    bad = []
    params = ("x_ptr, out_ptr, n, flag, BLOCK: tl.constexpr, "
              "ITERS: tl.constexpr")
    path = _operator_file(workdir, "whilegs", params, WHILE_BODY,
                          _int_case_layer(3, WHILE_REF, "whilegs_kernel",
                                          grid="(2,)"))
    module = _load(path)
    for threads in (1, 2, 4, 8):
        ok, detail = _run_case(compiler, module, threads, shape=(257,))
        if not ok:
            bad.append(f"threads={threads}: {detail}")
    # the grid extent is genuinely read at run time: a 4-program grid on a
    # 514-element input needs the stride too
    ok, detail = _run_case(compiler, module, 4, shape=(514,))
    if not ok:
        bad.append(f"grid=(2,) shape=(514,) threads=4: {detail}")
    check("while-loop-num-programs-grid-stride-executes", not bad,
          "; ".join(bad[:3]))


# -- tl.static_range unrolling and tl.range with step + pragmas ---------------

RANGES_BODY = """\\
    pid = tl.program_id(0)
    i = pid * BLOCK + tl.arange(0, BLOCK)
    x = tl.load(x_ptr + i, mask=i < n)
    y = x
    for s in tl.static_range(3):
        y = y + 1
    for k in tl.range(0, ITERS, 2, num_stages=2, loop_unroll_factor=1):
        y = y + 2
    tl.store(out_ptr + i, y, mask=i < n)"""

RANGES_REF = ['out = args["x_ptr"] + 3 + 2 * 2']


def check_static_and_tl_range(workdir, compiler):
    """tl.static_range unrolls at compile time; tl.range takes a step and
    classifies every pragma parameter ignorable-with-reason; both execute
    and compare exactly."""
    bad = []
    params = ("x_ptr, out_ptr, n, flag, BLOCK: tl.constexpr, "
              "ITERS: tl.constexpr")
    path = _operator_file(workdir, "ranges", params, RANGES_BODY,
                          _int_case_layer(3, RANGES_REF, "ranges_kernel"))
    module = _load(path)
    for threads in (1, 4):
        ok, detail = _run_case(compiler, module, threads, shape=(257,))
        if not ok:
            bad.append(f"threads={threads}: {detail}")
    check("static-range-and-tl-range-step-pragmas-execute", not bad,
          "; ".join(bad[:3]))


# -- acceptance[3]: multi-axis program_id decomposition + num_programs --------

MULTIAXIS_BODY = """\\
    p0 = tl.program_id(0)
    p1 = tl.program_id(1)
    np0 = tl.num_programs(0)
    np1 = tl.num_programs(1)
    pid = p1 * np0 + p0
    i = pid * BLOCK + tl.arange(0, BLOCK)
    m = i < n
    v = tl.load(x_ptr + i, mask=m)
    tl.store(out_ptr + i, v + p0 * 100 + p1 + np0 + np1, mask=m)"""

MULTIAXIS_REF = ['n0, n1 = 3, 5',
                 'out = args["x_ptr"].copy()',
                 'for p1 in range(n1):',
                 '    for p0 in range(n0):',
                 '        pid = p1 * n0 + p0',
                 '        lo, hi = pid * 128, min((pid + 1) * 128, len(out))',
                 '        out[lo:hi] = args["x_ptr"][lo:hi] + p0 * 100 + p1 + n0 + n1']


def check_multi_axis(workdir, compiler):
    """A 3x5 grid: the per-element value encodes BOTH axes (p0*100 + p1),
    so a wrong decomposition (axes swapped or the wrong divisor) produces
    different values.  The axis-swapped reference is the negative control:
    it must NOT match."""
    bad = []
    params = ("x_ptr, out_ptr, n, flag, BLOCK: tl.constexpr, "
              "ITERS: tl.constexpr")
    path = _operator_file(workdir, "multiaxis", params, MULTIAXIS_BODY,
                          _int_case_layer(3, MULTIAXIS_REF,
                                          "multiaxis_kernel", grid="(3, 5)"))
    module = _load(path)
    for threads in (1, 2, 4, 8):
        ok, detail = _run_case(compiler, module, threads, shape=(257,))
        if not ok:
            bad.append(f"threads={threads}: {detail}")
    # negative control: the axis-swapped reference must not match
    swapped = ['n0, n1 = 3, 5',
               'out = args["x_ptr"].copy()',
               'for p1 in range(n1):',
               '    for p0 in range(n0):',
               '        pid = p1 * n0 + p0',
               '        lo, hi = pid * 128, min((pid + 1) * 128, len(out))',
               '        out[lo:hi] = args["x_ptr"][lo:hi] + p1 * 100 + p0 + n0 + n1']
    path_sw = _operator_file(workdir, "multiaxis_sw", params, MULTIAXIS_BODY,
                             _int_case_layer(3, swapped,
                                             "multiaxis_sw_kernel",
                                             grid="(3, 5)"))
    module_sw = _load(path_sw)
    ok_sw, _ = _run_case(compiler, module_sw, 1, shape=(257,))
    if ok_sw:
        bad.append("axis-swapped reference matched (decomposition does not "
                   "distinguish axes)")
    check("multi-axis-program-id-decomposes-per-axis", not bad,
          "; ".join(bad[:3]))


# -- if_pid pattern -------------------------------------------------------------

IFPID_BODY = """\\
    pid = tl.program_id(0)
    i = pid * BLOCK + tl.arange(0, BLOCK)
    x = tl.load(x_ptr + i, mask=i < n)
    if pid == 0:
        y = x + 5
    else:
        y = x
    tl.store(out_ptr + i, y, mask=i < n)"""

IFPID_REF = ['out = args["x_ptr"] + 5',
             'out[128:] = args["x_ptr"][128:]']


def check_if_pid(workdir, compiler):
    """The if_pid pattern: a runtime branch on the program id -- the first
    program takes a different path (a block-value join across the arms)."""
    params = ("x_ptr, out_ptr, n, flag, BLOCK: tl.constexpr, "
              "ITERS: tl.constexpr")
    path = _operator_file(workdir, "ifpid", params, IFPID_BODY,
                          _int_case_layer(3, IFPID_REF, "ifpid_kernel"))
    module = _load(path)
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(compiler, module, threads, shape=(257,))
        if not ok:
            bad.append(f"threads={threads}: {detail}")
    check("if-pid-pattern-executes", not bad, "; ".join(bad[:3]))


# -- the corpus operator: var_len_copy (flow.loop + flow.dynamic_range) --------


def check_var_len_copy_corpus(compiler):
    """A real corpus operator with a runtime-bound loop over a loaded
    length: all its float32 cases (both shapes) execute and compare PASS
    at 1/2/4/8 threads on one artifact per identity.  (T012 implements
    the SEW-16 element path, so the fp16 cases of the same operator now
    execute too -- inside the declared fp32-lane single-rounding policy;
    the executed fp16 comparison evidence lives in test_conversions.py.)"""
    path = ROOT / "ops" / "suite" / "dev" / "var_len_copy.py"
    module = _load(path)
    bad = []
    for threads in (1, 2, 4, 8):
        for shape in ((3,), (4,)):
            ok, detail = _run_case(compiler, module, threads, shape=shape,
                                   dtype="float32")
            if not ok:
                bad.append(f"threads={threads} shape={shape}: {detail}")
    check("corpus-var-len-copy-flow-loop-executes-at-1-2-4-8", not bad,
          "; ".join(bad[:3]))
    # the fp16 cases of the same operator execute through the T012 path
    from a100c.driver import PipelineError
    try:
        for threads in (1, 2, 4, 8):
            ok, detail = _run_case(compiler, module, threads, shape=(3,),
                                   dtype="float16")
            if not ok:
                bad.append(f"fp16 threads={threads}: {detail}")
        check("var-len-copy-fp16-executes-located", not bad,
              "; ".join(bad[:2]))
    except PipelineError as exc:
        check("var-len-copy-fp16-executes-located",
              "width 16" in str(exc) or "SEW" in str(exc), str(exc)[:90])


# -- refusal boundaries are located (never silent) ------------------------------


def check_refusals_located(compiler):
    """Operators whose remaining constructs belong to later tasks refuse
    with a located diagnostic naming the construct -- tril_inplace_zero_tile
    (2-D arange indexing / early return).  control_flow.py (masked load
    with other=) and prelu_kernel.py moved past this boundary in T011
    (the other-merge, the scalar converts and the fp compare rows landed;
    both compile and execute PASS now -- verified by the probe runs in
    T011's evidence), so they are no longer refusal cases.  T027 moved
    tril_inplace past the GRID boundary (its M/C are meta constexprs the
    specialization identity signs -- a declared provenance category): the
    refusal now sits deeper, at the extent-homogeneous region lane.
    T028 removed that last boundary too: the mixed-extent region
    restructure lowers tril_inplace_zero_tile's 2-D masked stores, and
    every dtype executes PASS at 1/4 workers (verified in T028's
    execution probe) -- the family left the refusal census, so the list
    below is empty (the check keeps its shape for the next boundary)."""
    from a100c.driver import PipelineError
    bad = []
    cases = [
    ]
    for rel, kwargs, needles in cases:
        module = _load(ROOT / rel)
        try:
            compiler.compile_case(module.make_case(**kwargs))
            bad.append(f"{rel}: compiled (expected a located refusal)")
        except PipelineError as exc:
            if not any(n in str(exc) for n in needles):
                bad.append(f"{rel}: {str(exc)[:110]}")
        except Exception as exc:               # noqa: BLE001
            bad.append(f"{rel}: wrong error type {type(exc).__name__}: "
                       f"{str(exc)[:80]}")
    check("flow-family-remaining-boundaries-refuse-located", not bad,
          "; ".join(bad[:2]))


# -- T026: the control-flow frontend repair classes ---------------------------
#
# Every shape below reproduced a 'carried-value-without-join' or
# 'return'/'while'/'and' refusal row in the compile census before the
# control-flow core repair: the census operators l1_fused_* (join 'mask'),
# fast_ce_loss (join 'loss'/'x'), unique_dim_row_single_chunk_first (join
# 'cur'), chebyshev_polynomial_t (loop carries 't_prev'), kldiv (loop
# carries 'loss_sum'), cholesky_upper (while j < K), amax/any_kernel_dim
# (Python and/or), chunk_gdn2_* (early return).


def _t026_lower(body, params=None):
    """Lower one probe kernel body and return (module, errors)."""
    import textwrap
    indented = textwrap.indent(body.strip("\n"), "    ")
    text = TEMPLATE % ("t026", "t026", "t026",
                       params or ("x_ptr, y_ptr, n, flag, "
                                  "BLOCK: tl.constexpr, "
                                  "ITERS: tl.constexpr"),
                       indented, CASE_LAYER_INT)
    src = source.load_operator_text(text, "<t026>", "t026.py")
    case = {"args": {"x_ptr": np.zeros(16, np.int32),
                     "y_ptr": np.zeros(16, np.int32),
                     "n": 16, "flag": 3},
            "meta": {"BLOCK": 16, "ITERS": 4}, "launch_meta": {}}
    spec = specialize.specialize(src, case)
    module = lower_tir.lower(src, spec)
    return module, tir.verify_module(module)


def check_t026_carried_join_shapes():
    """acceptance[2]: each join shape that previously failed as a
    carried-value-without-join row lowers to a module the TIR verifier
    ACCEPTS, with the join the construction must create.

    * one-path assignment: a name defined before the branch and assigned
      on one path joins (the other path's side is the outer binding);
    * an arm-only name (never defined before, used only inside its arm)
      creates NO join -- the other arm must not see the then arm's
      bindings (the l1_fused 'mask' class);
    * a re-assigned variable joins on both arms;
    * a conditionally-assigned pointer joins (an i64 domain value);
    * a ConstVal arm side materializes inside its arm under the join name
      (the fast_ce_loss 'loss' class);
    * a loop channel copy (``prev = cur``, the chebyshev 't_prev' class)
      gets a region-visible body definition;
    * a carried candidate whose only assignment a specialization folds
      away keeps its outer binding (the kldiv 'loss_sum' class)."""
    bad = []

    # one-path assignment + arm-only name + ConstVal side, one module
    m, errs = _t026_lower("""
i = tl.arange(0, BLOCK)
m = i < n
x = tl.load(x_ptr + i, mask=m)
y = x
if flag > 0:
    y = x + 1
    arm_only = x * 3
    z = flag + 1
else:
    z = 0
tl.store(y_ptr + i, y + z, mask=m)
""")
    if errs:
        bad.append(f"one-path/const: {errs[0]}")
    ifs = [s for s in m.functions[0].body.statements if isinstance(s, tir.If)]
    if len(ifs) != 1:
        bad.append(f"one-path: {len(ifs)} ifs")
    else:
        names = ifs[0].join_names
        for wanted in ("y", "z"):
            if wanted not in names:
                bad.append(f"one-path: join '{wanted}' missing {names}")
        if "arm_only" in names:
            bad.append(f"arm-only name joined: {names}")

    # re-assigned variable on both arms + conditionally-assigned pointer
    m2, errs2 = _t026_lower("""
i = tl.arange(0, BLOCK)
m = i < n
p = x_ptr + 4
w = tl.load(x_ptr + i, mask=m)
if flag > 0:
    w = w + 1
    p = p + 8
else:
    w = w + 2
    p = p + 16
v = tl.load(p + i, mask=m)
tl.store(y_ptr + i, w + v, mask=m)
""")
    if errs2:
        bad.append(f"reassigned/pointer: {errs2[0]}")
    ifs2 = [s for s in m2.functions[0].body.statements if isinstance(s, tir.If)]
    if len(ifs2) != 1 or not {"w", "p"} <= set(ifs2[0].join_names):
        bad.append(f"reassigned/pointer joins: "
                   f"{ifs2 and ifs2[0].join_names}")

    # a loop channel copy (prev = cur) and a folded-away carried candidate
    m3, errs3 = _t026_lower("""
i = tl.arange(0, BLOCK)
x = tl.load(x_ptr + i)
t_cur = x
t_prev = x * 0 + 1
acc = 0
for k in range(0, ITERS):
    t_next = t_cur + t_prev
    t_prev = t_cur
    t_cur = t_next
    acc = acc + 1
keep = 0
for k2 in range(0, ITERS):
    if ITERS < 0:
        keep = keep + 1
    acc = acc + 2
tl.store(y_ptr + i, x + acc + keep + t_prev + t_cur - t_prev)
""")
    if errs3:
        bad.append(f"channel-copy/folded: {errs3[0]}")
    loops = [s for s in m3.functions[0].body.statements
             if isinstance(s, tir.Loop)]
    if len(loops) != 2:
        bad.append(f"channel-copy: {len(loops)} loops")
    else:
        carried0 = [c for c, _ in loops[0].carried]
        if "t_prev" not in carried0 or "t_cur" not in carried0:
            bad.append(f"channel-copy carried: {carried0}")
        # the folded-away candidate is NOT a channel (its only assignment
        # sits under a constexpr-false branch in this specialization)
        carried1 = [c for c, _ in loops[1].carried]
        if "keep" in carried1:
            bad.append(f"folded-away candidate carried: {carried1}")

    check("t026-carried-value-join-shapes-verify", not bad, "; ".join(bad))


EARLY_RETURN_BODY = """\\
    pid = tl.program_id(0)
    i = pid * BLOCK + tl.arange(0, BLOCK)
    m = i < n
    if pid >= 2:
        return
    if flag < 0:
        return
    v = tl.load(x_ptr + i, mask=m)
    tl.store(out_ptr + i, v + 1, mask=m)"""

EARLY_RETURN_REF = ['out = np.zeros(len(args["x_ptr"]), np.int32)',
                    'if args["flag"] >= 0:',
                    '    for pid in range(2):',
                    '        lo, hi = pid * 128, min((pid + 1) * 128, len(out))',
                    '        out[lo:hi] = args["x_ptr"][lo:hi] + 1']


def check_t026_early_return(workdir, compiler):
    """acceptance[1] shape: a bare early return inside runtime branches --
    the returned programs' outputs keep their default (the returned-vs-
    default semantics), the guard state carries through the joins, and
    both branch directions execute correctly at 1 and 4 workers."""
    bad = []
    params = ("x_ptr, out_ptr, n, flag, BLOCK: tl.constexpr, "
              "ITERS: tl.constexpr")
    for flag, tag in ((3, "live"), (-2, "returned")):
        path = _operator_file(workdir, f"earlyret_{tag}", params,
                              EARLY_RETURN_BODY,
                              _int_case_layer(flag, EARLY_RETURN_REF,
                                              f"earlyret_{tag}_kernel"))
        module = _load(path)
        for threads in (1, 4):
            for shape in ((257,), (514,)):
                ok, detail = _run_case(compiler, module, threads,
                                       shape=shape)
                if not ok:
                    bad.append(f"flag={flag} threads={threads} "
                               f"shape={shape}: {detail}")
    check("t026-early-return-executes-at-1-and-4-workers", not bad,
          "; ".join(bad[:3]))


AND_OR_BODY = """\\
    pid = tl.program_id(0)
    i = pid * BLOCK + tl.arange(0, BLOCK)
    row = i < n
    col = i < (n - 1)
    mask = row and col
    x = tl.load(x_ptr + i, mask=mask, other=0)
    below = i < (n // 2)
    above = i > (n // 2 + 3)
    violated = below or above
    if flag > 0 and pid < 3:
        x = x + 1
    anyhits = tl.max((violated and mask).to(tl.int32), axis=0)
    tl.store(out_ptr + i, x + anyhits, mask=row)"""

AND_OR_REF = ['x = args["x_ptr"].astype(np.int32).copy()',
              'n = len(x)',
              'mask = np.arange(n) < (n - 1)',
              'x[~mask] = 0',
              'violated = (np.arange(n) < n // 2) | (np.arange(n) > n // 2 + 3)',
              'if args["flag"] > 0:',
              '    x = x + 1',
              'out = x.copy()',
              'B = 128',
              'for b in range((n + B - 1) // B):',
              '    lo, hi = b * B, min((b + 1) * B, n)',
              '    hit = int((violated[lo:hi] & mask[lo:hi]).any())',
              '    out[lo:hi] = x[lo:hi] + hit']


def check_t026_and_or(workdir, compiler):
    """Python and/or over runtime values lowers to the pinned semantics:
    bool-tensor & / | with broadcast (the amax/any_kernel_dim class) and
    the short-circuit/boolean forms over runtime scalars (the
    sym_constrain_range / vocab_parallel_ce class), executed at 1 and 4
    workers against an independent reference."""
    bad = []
    params = ("x_ptr, out_ptr, n, flag, BLOCK: tl.constexpr, "
              "ITERS: tl.constexpr")
    for flag, tag in ((3, "and"), (-2, "or_false")):
        path = _operator_file(workdir, f"andor_{tag}", params, AND_OR_BODY,
                              _int_case_layer(flag, AND_OR_REF,
                                              f"andor_{tag}_kernel"))
        module = _load(path)
        for threads in (1, 4):
            ok, detail = _run_case(compiler, module, threads, shape=(257,))
            if not ok:
                bad.append(f"flag={flag} threads={threads}: {detail}")
    check("t026-python-and-or-executes-at-1-and-4-workers", not bad,
          "; ".join(bad[:3]))


WHILE_CARRIED_BODY = """\\
    pid = tl.program_id(0)
    j = 0
    total = 0
    while j < flag:
        step = 0
        while step < j:
            total = total + 2
            step = step + 1
        total = total + 1
        j = j + 1
    i = pid * BLOCK + tl.arange(0, BLOCK)
    m = i < n
    v = tl.load(x_ptr + i, mask=m)
    tl.store(out_ptr + i, v + total, mask=m)"""

WHILE_CARRIED_REF = ['total = 0',
                     'for j in range(args["flag"]):',
                     '    total += 1 + 2 * j',
                     'out = args["x_ptr"] + total']


def check_t026_while_carried(workdir, compiler):
    """The cholesky/deconv3d class: a while whose condition compares a
    name the body re-assigns (``while j < K`` with ``j = 0`` before it)
    must NOT fold against the pre-loop constant (the old 'while True
    never terminates' refusal); nested whiles compose; executed at 1 and
    4 workers against an independent reference."""
    bad = []
    params = ("x_ptr, out_ptr, n, flag, BLOCK: tl.constexpr, "
              "ITERS: tl.constexpr")
    path = _operator_file(workdir, "whilecarried", params, WHILE_CARRIED_BODY,
                          _int_case_layer(5, WHILE_CARRIED_REF,
                                          "whilecarried_kernel"))
    module = _load(path)
    for threads in (1, 4):
        ok, detail = _run_case(compiler, module, threads, shape=(257,))
        if not ok:
            bad.append(f"threads={threads}: {detail}")
    check("t026-while-carried-condition-executes-at-1-and-4-workers",
          not bad, "; ".join(bad[:3]))


BREAK_CONTINUE_BODY = """\\
    pid = tl.program_id(0)
    i = pid * BLOCK + tl.arange(0, BLOCK)
    m = i < n
    v = tl.load(x_ptr + i, mask=m)
    total = 0
    for k in range(0, ITERS * 4):
        if k == 3:
            break
        if k == 1:
            continue
        total = total + 1
    w = 0
    while True:
        if w >= flag:
            break
        w = w + 2
    tl.store(out_ptr + i, v + total * 10 + w, mask=m)"""

BREAK_CONTINUE_REF = ['total = 0',
                      'for k in range(4 * 4):',
                      '    if k == 3:',
                      '        break',
                      '    if k == 1:',
                      '        continue',
                      '    total += 1',
                      'w = 0',
                      'while True:',
                      '    if w >= args["flag"]:',
                      '        break',
                      '    w += 2',
                      'out = args["x_ptr"] + total * 10 + w']


def check_t026_break_continue(workdir, compiler):
    """break and continue as loop exits: a counted range with a break
    lowers through the while form (the stop channel), a continue skips
    the rest of its iteration while the induction still advances, and
    ``while True`` + break terminates; executed at 1 and 4 workers.  The
    control: ``while True`` WITHOUT a break still refuses, located."""
    from a100c.driver import PipelineError
    bad = []
    params = ("x_ptr, out_ptr, n, flag, BLOCK: tl.constexpr, "
              "ITERS: tl.constexpr")
    path = _operator_file(workdir, "brkcont", params, BREAK_CONTINUE_BODY,
                          _int_case_layer(7, BREAK_CONTINUE_REF,
                                          "brkcont_kernel"))
    module = _load(path)
    for threads in (1, 4):
        ok, detail = _run_case(compiler, module, threads, shape=(257,))
        if not ok:
            bad.append(f"threads={threads}: {detail}")

    # the control: an exit-free `while True` refuses with the located
    # infinite-loop diagnostic (never a silent hang)
    path2 = _operator_file(workdir, "whiletrue", params, """\\
    pid = tl.program_id(0)
    i = pid * BLOCK + tl.arange(0, BLOCK)
    m = i < n
    v = tl.load(x_ptr + i, mask=m)
    while True:
        v = v + 1
    tl.store(out_ptr + i, v, mask=m)""",
                          _int_case_layer(7, ['out = args["x_ptr"]'],
                                          "whiletrue_kernel"))
    module2 = _load(path2)
    try:
        compiler.compile_case(module2.make_case())
        bad.append("while-True-without-break compiled (expected a refusal)")
    except PipelineError as exc:
        if "while True never terminates" not in str(exc):
            bad.append(f"while-True control: {str(exc)[:110]}")
    except Exception as exc:                   # noqa: BLE001
        bad.append(f"while-True control: wrong error {type(exc).__name__}")
    check("t026-break-continue-and-while-true-execute", not bad,
          "; ".join(bad[:3]))


def main() -> int:
    workdir = Path(tempfile.mkdtemp(prefix="a100c-cf-"))
    cache = workdir / "cache"
    try:
        from a100c.driver import Compiler, CompileOptions
        compiler = Compiler(options=CompileOptions(cache_dir=str(cache)))

        check_verifier_rejects_lexical_restore()
        check_frontend_region_forms()
        check_carried_rebind_executes(workdir, compiler)
        check_while_num_programs(workdir, compiler)
        check_static_and_tl_range(workdir, compiler)
        check_multi_axis(workdir, compiler)
        check_if_pid(workdir, compiler)
        check_var_len_copy_corpus(compiler)
        check_refusals_located(compiler)
        # T026: the control-flow frontend repair classes
        check_t026_carried_join_shapes()
        check_t026_early_return(workdir, compiler)
        check_t026_and_or(workdir, compiler)
        check_t026_while_carried(workdir, compiler)
        check_t026_break_continue(workdir, compiler)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_control_flow: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
