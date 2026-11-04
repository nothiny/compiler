#!/usr/bin/env python3
"""test_tir_verifier.py -- the TIR structural verifier (T006, acceptance[2]).

The verifier rejects one hand-built malformed module per invariant class
(use-before-definition, type contradiction, masked operation without
declared default, broadcast extent consumed as real extent, carried value
without join) and accepts the real frontend's output for valid elementwise
kernels (IR-WELLFORMED).  The control: delete a definition whose use
remains and the verifier must reject (the witness that the checks are
load-bearing, not vacuous).

Run: python3 a100c/tests/test_tir_verifier.py   (exit 0 = all checks PASS)
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
OPS = ROOT / "ops"

warnings.filterwarnings("ignore")

FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(name)
    return ok


import os  # noqa: E402

sys.path.insert(0, str(OPS / "harness"))
os.chdir(str(OPS))

from a100c.frontend import lower_tir, source, specialize  # noqa: E402
from a100c.ir import tir  # noqa: E402

LOC = tir.SrcLoc("handbuilt.py", 1, 1)


def new_module(params=()):
    fn = tir.Function("k", list(params), LOC)
    mod = tir.Module("k", "handbuilt.py")
    mod.functions.append(fn)
    return mod, fn


def ptr_param(name, pointee=tir.FLOAT32):
    return tir.Value(tir.Type.pointer(pointee), (), LOC, name=name)


def i32_param(name):
    return tir.Value(tir.INT32, (), LOC, name=name)


def has_invariant(errors, invariant):
    return any(e.invariant == invariant for e in errors)


def only_invariant(errors, invariant):
    return errors and all(e.invariant == invariant for e in errors)


# ---------------------------------------------------------------------------
# One hand-built malformed module per invariant class
# ---------------------------------------------------------------------------

def malformed_use_before_definition():
    mod, fn = new_module([ptr_param("p"), i32_param("n")])
    offs = tir.Op.arange(0, 8, LOC)
    # the mask uses `offs` before it is defined (statement order swapped)
    nb = tir.Op.broadcast(fn.params[1], (tir.Extent(8, True),), LOC)
    mask = tir.Op.cmp("cmp.lt", offs.result(), nb.result(), LOC)
    fn.body.statements.append(mask)
    fn.body.statements.append(offs)
    return tir.verify_module(mod)


def malformed_type_contradiction():
    mod, fn = new_module([ptr_param("p"), i32_param("n")])
    offs = tir.Op.arange(0, 8, LOC)
    fn.body.statements.append(offs)
    fconst = tir.Op.const(1.0, tir.FLOAT32, LOC)
    fn.body.statements.append(fconst)
    # arith.add on i32 and fp32 without an explicit convert
    bad = tir.Op.binop("arith.add", offs.result(), fconst.result(), LOC)
    fn.body.statements.append(bad)
    return tir.verify_module(mod)


def malformed_masked_without_default():
    mod, fn = new_module([ptr_param("p"), i32_param("n")])
    offs = tir.Op.arange(0, 8, LOC)
    fn.body.statements.append(offs)
    nb = tir.Op.broadcast(fn.params[1], (tir.Extent(8, True),), LOC)
    fn.body.statements.append(nb)
    mask = tir.Op.cmp("cmp.lt", offs.result(), nb.result(), LOC)
    fn.body.statements.append(mask)
    padd = tir.Op.ptradd(fn.params[0], offs.result(), LOC)
    fn.body.statements.append(padd)
    # masked load whose masked_default attribute is missing entirely
    ld = tir.Op("load", (padd.result(), mask.result()), LOC,
                tir.FLOAT32, padd.result().shape, attrs={})
    fn.body.statements.append(ld)
    return tir.verify_module(mod)


def malformed_broadcast_as_real():
    mod, fn = new_module([ptr_param("p"), i32_param("n")])
    offs = tir.Op.arange(0, 8, LOC)
    fn.body.statements.append(offs)
    nb = tir.Op.broadcast(fn.params[1], (tir.Extent(8, True),), LOC)
    fn.body.statements.append(nb)
    mask = tir.Op.cmp("cmp.lt", offs.result(), nb.result(), LOC)
    fn.body.statements.append(mask)
    padd = tir.Op.ptradd(fn.params[0], offs.result(), LOC)
    fn.body.statements.append(padd)
    zero = tir.Op.const(0.0, tir.FLOAT32, LOC)
    fn.body.statements.append(zero)
    # the store value keeps its broadcast extent: consumed as real
    zbad = tir.Op.broadcast(zero.result(), (tir.Extent(8, True),), LOC)
    fn.body.statements.append(zbad)
    st = tir.Op.store(padd.result(), zbad.result(), mask.result(),
                      tir.MaskedDefault.NO_ACCESS, LOC)
    fn.body.statements.append(st)
    return tir.verify_module(mod)


def malformed_carried_without_join():
    mod, fn = new_module([i32_param("n")])
    cond = tir.Op.cmp("cmp.lt", fn.params[0], fn.params[0], LOC)
    fn.body.statements.append(cond)
    # then-arm defines a value that is used after the if without a join
    iff = tir.If(cond.result(), LOC)
    arm_val = tir.Op.const(1, tir.INT32, LOC)
    iff.then.statements.append(arm_val)
    other = tir.Op.const(2, tir.INT32, LOC)
    iff.els.statements.append(other)
    iff.join_names = ()                 # no join declared
    fn.body.statements.append(iff)
    after = tir.Op.binop("arith.add", arm_val.result(), arm_val.result(),
                         LOC)
    fn.body.statements.append(after)
    return tir.verify_module(mod)


def malformed_loop_carried_without_join():
    mod, fn = new_module([i32_param("n")])
    loop = tir.Loop(None, fn.params[0], None, LOC)
    loop.carried = (("acc", fn.params[0]),)
    # the body never redefines the carried value: no join
    dummy = tir.Op.const(0, tir.INT32, LOC)
    loop.body.statements.append(dummy)
    fn.body.statements.append(loop)
    return tir.verify_module(mod)


# ---------------------------------------------------------------------------
# Controls (MECH-WITNESS-TEST: a check that cannot fail is not a check)
# ---------------------------------------------------------------------------

def control_deleted_definition():
    """A valid module with one definition deleted: the verifier must reject
    (use-before-definition), proving the checks are live."""
    mod, fn = new_module([ptr_param("p"), i32_param("n")])
    offs = tir.Op.arange(0, 8, LOC)
    nb = tir.Op.broadcast(fn.params[1], (tir.Extent(8, True),), LOC)
    mask = tir.Op.cmp("cmp.lt", offs.result(), nb.result(), LOC)
    padd = tir.Op.ptradd(fn.params[0], offs.result(), LOC)
    ld = tir.Op.load(padd.result(), mask.result(), tir.MaskedDefault.UNDEF,
                     None, LOC)
    st = tir.Op.store(padd.result(), ld.result(), mask.result(),
                      tir.MaskedDefault.NO_ACCESS, LOC)
    for op in (offs, nb, mask, padd, ld, st):
        fn.body.statements.append(op)
    errors = tir.verify_module(mod)
    if errors:
        return errors, "pristine module was already invalid"
    # delete the arange definition: every user becomes use-before-def
    fn.body.statements.remove(offs)
    return tir.verify_module(mod), None


# ---------------------------------------------------------------------------
# The real frontend's output for valid elementwise kernels
# ---------------------------------------------------------------------------

def lower_real(rel, shape, dtype):
    from opslib.runner import load_operator
    src = source.load_operator(str(OPS / rel), corpus_root=str(OPS))
    module = load_operator(str(OPS / rel))
    case = module.make_case(shape=shape, dtype=dtype)
    spec = specialize.specialize(src, case)
    return lower_tir.lower(src, spec), spec


REAL_KERNELS = [
    ("suite/dev/absolute_kernel.py", (17,), "float32"),
    ("suite/perf/leaky_relu.py", (99,), "bfloat16"),
    ("suite/perf/signbit_bitwise_and.py", (99,), "int32"),
    ("suite/dev/slice_scatter_kernel.py", (17,), "float32"),
    ("suite/perf/fused_index_select_eq.py", (5, 17), "bfloat16"),
    ("suite/dev/mul_scalar_kernel.py", (17,), "float32"),
    ("suite/dev/kv_cache_write.py", (6, 4, 2, 8), "float32"),
    ("suite/perf/square_matrix.py", (4, 4), "float32"),
]


def main() -> int:
    check("malformed-use-before-definition",
          has_invariant(malformed_use_before_definition(),
                        tir.Invariant.USE_BEFORE_DEFINITION)
          and only_invariant(malformed_use_before_definition(),
                             tir.Invariant.USE_BEFORE_DEFINITION))
    check("malformed-type-contradiction",
          only_invariant(malformed_type_contradiction(),
                         tir.Invariant.TYPE_CONTRADICTION))
    errs = malformed_masked_without_default()
    check("malformed-masked-without-default",
          has_invariant(errs, tir.Invariant.MASKED_WITHOUT_DEFAULT),
          str(errs[:1]))
    errs = malformed_broadcast_as_real()
    check("malformed-broadcast-as-real",
          has_invariant(errs, tir.Invariant.BROADCAST_AS_REAL), str(errs[:1]))
    errs = malformed_carried_without_join()
    check("malformed-carried-without-join",
          has_invariant(errs, tir.Invariant.CARRIED_WITHOUT_JOIN),
          str(errs[:1]))
    check("malformed-loop-carried-without-join",
          has_invariant(malformed_loop_carried_without_join(),
                        tir.Invariant.CARRIED_WITHOUT_JOIN))

    # a masked store without declared no-access semantics is also malformed
    mod, fn = new_module([ptr_param("p"), i32_param("n")])
    offs = tir.Op.arange(0, 8, LOC)
    fn.body.statements.append(offs)
    nb = tir.Op.broadcast(fn.params[1], (tir.Extent(8, True),), LOC)
    fn.body.statements.append(nb)
    mask = tir.Op.cmp("cmp.lt", offs.result(), nb.result(), LOC)
    fn.body.statements.append(mask)
    padd = tir.Op.ptradd(fn.params[0], offs.result(), LOC)
    fn.body.statements.append(padd)
    ld = tir.Op.load(padd.result(), mask.result(), tir.MaskedDefault.UNDEF,
                     None, LOC)
    fn.body.statements.append(ld)
    st = tir.Op("store", (padd.result(), ld.result(), mask.result()), LOC,
                None, None, attrs={"masked_default": "value"}, results=0)
    fn.body.statements.append(st)
    errs = tir.verify_module(mod)
    check("masked-store-must-declare-no-access",
          has_invariant(errs, tir.Invariant.TYPE_CONTRADICTION)
          and not has_invariant(errs, tir.Invariant.MASKED_WITHOUT_DEFAULT),
          str(errs[:1]))

    errors, pre = control_deleted_definition()
    check("control-deleted-definition-rejected",
          pre is None
          and has_invariant(errors, tir.Invariant.USE_BEFORE_DEFINITION),
          pre or str(errors[:1]))

    # the real frontend's output verifies for valid elementwise kernels
    for rel, shape, dtype in REAL_KERNELS:
        try:
            mod, spec = lower_real(rel, shape, dtype)
            errs = tir.verify_module(mod)
            stmts = len(mod.functions[0].body.statements)
            check(f"frontend-output-verified:{Path(rel).stem}",
                  not errs, f"{stmts} statements" +
                  (f"; errors: {errs[:1]}" if errs else ""))
        except Exception as exc:  # noqa: BLE001
            check(f"frontend-output-verified:{Path(rel).stem}", False,
                  f"{type(exc).__name__}: {exc}")

    if FAILURES:
        print(f"test_tir_verifier: {len(FAILURES)} check(s) FAILED: "
              f"{FAILURES}")
        return 1
    print("test_tir_verifier: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
