#!/usr/bin/env python3
"""test_frontend_types.py -- the pinned Triton 3.8 type rules (T006).

Literal typing, promotion/unification and result types per the pinned
triton 3.8.0 semantics (the reference environment pins
``triton.__version__ == 3.8.0``, F013/F049; the rules mirror
``triton/language/semantic.py`` of that source), value conversion distinct
from bitcast, zero-dimensional values, and the end-to-end behavior of those
rules through the lowering (int/int true division is fp32; store values
convert to the pointee type; bool lanes store through i1 pointers).

Run: python3 a100c/tests/test_frontend_types.py   (exit 0 = all PASS)
"""
from __future__ import annotations

import sys
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()

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
from a100c.frontend import types as ft  # noqa: E402
from a100c.frontend.types import TypeRuleError  # noqa: E402
from a100c.ir import tir  # noqa: E402

TEMPLATE = '''\
"""probe operator"""
OPERATOR = {{"name": "probe", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}}
import triton
import triton.language as tl

@triton.jit
def probe_kernel({params}):
{body}
'''


def lower(body, args, meta=None, pdt=None):
    text = TEMPLATE.format(
        params="x_ptr, y_ptr, n, BLOCK: tl.constexpr",
        body="\n".join("    " + line for line in body.splitlines()))
    src = source.load_operator_text(text, "<probe>", "probe.py")
    case = {"args": args, "meta": meta or {"BLOCK": 8}, "launch_meta": {}}
    if pdt:
        case["pointer_dtypes"] = pdt
    spec = specialize.specialize(src, case)
    return lower_tir.lower(src, spec), spec


def ops_of(module):
    return [st for st in module.functions[0].body.statements
            if isinstance(st, tir.Op)]


def check_literal_typing():
    """Pinned to_tensor_type: bool -> i1, int by magnitude, float by fp32
    representability."""
    cases = [
        (True, tir.INT1), (False, tir.INT1),
        (0, tir.INT32), (17, tir.INT32), (-17, tir.INT32),
        (2**31 - 1, tir.INT32), (2**31, tir.UINT32), (2**32 - 1, tir.UINT32),
        (2**32, tir.INT64), (-2**63, tir.INT64),
        (2**63, tir.UINT64), (2**64 - 1, tir.UINT64),
        (0.0, tir.FLOAT32), (1.5, tir.FLOAT32), (-1e30, tir.FLOAT32),
        (1e-40, tir.FLOAT64), (1e40, tir.FLOAT64), (float("inf"),
                                                    tir.FLOAT32),
        (float("nan"), tir.FLOAT32), (2**-126, tir.FLOAT32),
    ]
    bad = []
    for value, want in cases:
        try:
            got = ft.literal_type(value)
        except TypeRuleError:
            got = None
        if got != want:
            bad.append(f"{value!r}->{got!r} (want {want!r})")
    try:
        ft.literal_type(2**64)
        bad.append("2**64 accepted")
    except TypeRuleError:
        pass
    check("literal-typing-pinned", not bad, "; ".join(bad[:4]))


def check_integer_promote():
    cases = [
        (tir.INT32, tir.INT32, tir.INT32),
        (tir.INT32, tir.INT64, tir.INT64),
        (tir.UINT16, tir.INT32, tir.INT32),
        (tir.UINT32, tir.INT32, tir.UINT32),      # equal width: unsigned
        (tir.UINT8, tir.INT64, tir.INT64),
        (tir.INT1, tir.INT1, tir.INT1),           # bool & bool -> i1
        (tir.INT1, tir.INT32, tir.INT32),         # bool joins integers
        (tir.INT1, tir.INT8, tir.INT8),           # 1-bit vs 8-bit signed
    ]
    bad = [f"{a!r},{b!r}->{ft.integer_promote(a, b)!r} (want {w!r})"
           for a, b, w in cases if ft.integer_promote(a, b) != w]
    check("integer-promote-usual-arithmetic-conversions", not bad,
          "; ".join(bad[:3]))


def check_computation_type():
    T, F = ft.computation_type, True
    cases = [
        # literal of a lower-or-equal kind does not participate (pinned 0)
        (tir.INT32, True, tir.FLOAT16, False, False, tir.FLOAT16),
        (tir.INT32, True, tir.BFLOAT16, False, False, tir.BFLOAT16),
        # the / % exception for fp16/bf16
        (tir.INT32, True, tir.FLOAT16, False, True, tir.FLOAT32),
        (tir.INT32, True, tir.BFLOAT16, False, True, tir.FLOAT32),
        # a float literal with an int tensor participates (pinned rule 2)
        (tir.FLOAT32, True, tir.INT32, False, False, tir.FLOAT32),
        # fp hierarchy
        (tir.FLOAT16, False, tir.FLOAT32, False, False, tir.FLOAT32),
        (tir.FLOAT16, False, tir.FLOAT16, False, False, tir.FLOAT16),
        (tir.FLOAT16, False, tir.FLOAT16, False, True, tir.FLOAT32),
        (tir.BFLOAT16, False, tir.BFLOAT16, False, False, tir.BFLOAT16),
        (tir.BFLOAT16, False, tir.BFLOAT16, False, True, tir.FLOAT32),
        (tir.BFLOAT16, False, tir.FLOAT16, False, False, tir.FLOAT16),  # pinned rule 3
        (tir.FLOAT64, False, tir.FLOAT16, False, False, tir.FLOAT64),
        # integers
        (tir.INT32, False, tir.INT64, False, False, tir.INT64),
        (tir.UINT8, False, tir.INT16, False, False, tir.INT16),
        # bool as a 1-bit signed integer
        (tir.INT1, False, tir.INT1, False, False, tir.INT1),
    ]
    bad = []
    for a, al, b, bl, dm, want in cases:
        got = T(a, al, b, bl, dm)
        if got != want:
            bad.append(f"{a!r}x{al},{b!r}x{bl},div={dm}->{got!r}")
    # mixed signedness division is an error (pinned)
    for a, b in ((tir.UINT32, tir.INT32), (tir.INT64, tir.UINT32)):
        try:
            T(a, False, b, False, True)
            bad.append(f"mixed-signedness div {a!r},{b!r} accepted")
        except TypeRuleError:
            pass
    check("computation-type-pinned-matrix", not bad, "; ".join(bad[:4]))


def check_literal_guards():
    bad = []
    # a negative literal with an unsigned result is an error (pinned)
    try:
        ft.binop_unify(tir.INT32, True, -1, tir.UINT32, False, None)
        bad.append("negative literal with unsigned accepted")
    except TypeRuleError:
        pass
    # a literal out of the computation type's range is an error (pinned)
    try:
        ft.binop_unify(tir.INT32, True, 300, tir.INT8, False, None)
        bad.append("out-of-range literal accepted")
    except TypeRuleError:
        pass
    check("literal-guards-pinned", not bad)


def check_convert_vs_bitcast():
    ok = ft.convert_ok(tir.INT32, tir.FLOAT32)
    ok &= ft.convert_ok(tir.FLOAT32, tir.FLOAT16)
    ok &= ft.convert_ok(tir.BOOL if hasattr(tir, "BOOL") else tir.INT1,
                        tir.INT32)
    ok &= not ft.convert_ok(tir.Type.pointer(tir.FLOAT32), tir.FLOAT32)
    ok &= not ft.convert_ok(tir.FLOAT32, tir.FLOAT32)      # identity: no
    ok &= ft.bitcast_ok(tir.FLOAT32, tir.UINT32)
    ok &= ft.bitcast_ok(tir.FLOAT16, tir.UINT16)
    ok &= not ft.bitcast_ok(tir.FLOAT32, tir.UINT16)       # width change
    ok &= not ft.bitcast_ok(tir.FLOAT32, tir.FLOAT32)      # identity: no
    ok &= not ft.bitcast_ok(tir.Type.pointer(tir.FLOAT32), tir.UINT64)
    check("convert-vs-bitcast-distinct", ok)


def check_scalar_arg_and_class():
    bad = []
    cases = [
        (True, tir.INT1), (5, tir.INT32), (5, tir.INT32),
        (2**40, tir.INT64), (np.int32(3), tir.INT32),
        (np.int64(3), tir.INT64), (np.uint8(3), tir.UINT8),
        (0.5, tir.FLOAT32), (np.float32(0.5), tir.FLOAT32),
        (np.float16(0.5), tir.FLOAT16),
    ]
    for value, want in cases:
        got = ft.scalar_arg_type(value)
        if got != want:
            bad.append(f"{value!r}->{got!r}")
    # specialization classes mirror the corpus meta tier (identity.py)
    cls = [
        (1, ("int", "one")), (16, ("int", "div16")), (32, ("int", "div16")),
        (17, ("int", "other")), (np.int32(16), ("int", "div16")),
        (True, ("bool", True)), (False, ("bool", False)),
        (0.5, ("float", "float64")), (np.float32(0.5), ("float", "float32")),
    ]
    for value, want in cls:
        got = ft.scalar_class(value)
        if got != want:
            bad.append(f"class {value!r}->{got!r}")
    check("scalar-arg-types-and-classes", not bad, "; ".join(bad[:4]))


def check_zero_dim_and_end_to_end():
    # zero-dimensional values: scalars broadcast (flagged) into blocks
    mod, _ = lower("""
v = tl.load(x_ptr + tl.arange(0, BLOCK))
w = v + n
tl.store(y_ptr + tl.arange(0, BLOCK), w)
""", {"x_ptr": np.zeros(8, np.float32), "y_ptr": np.zeros(8, np.float32),
      "n": 3})
    ops = ops_of(mod)
    bcs = [o for o in ops if o.op == "broadcast" and
           all(e.broadcast for e in o.results[0].shape)]
    add = [o for o in ops if o.op == "arith.add"]
    ok = len(bcs) >= 1 and len(add) == 1
    ok &= add[0].operands[0].rank == 1 and add[0].operands[1].rank == 1
    ok &= tir.verify_module(mod) == []
    check("zero-dim-scalar-broadcasts-into-block", ok)

    # int / int true division computes in fp32 (pinned div: both to fp32)
    mod, _ = lower("""
a = tl.load(x_ptr + tl.arange(0, BLOCK))
b = tl.load(y_ptr + tl.arange(0, BLOCK))
c = a / b
tl.store(y_ptr + tl.arange(0, BLOCK), c)
""", {"x_ptr": np.zeros(8, np.int32), "y_ptr": np.zeros(8, np.int32),
      "n": 3})
    ops = ops_of(mod)
    fdiv = [o for o in ops if o.op == "arith.fdiv"]
    ok = len(fdiv) == 1 and fdiv[0].results[0].type == tir.FLOAT32
    ok &= all(o.type == tir.FLOAT32 for o in fdiv[0].operands)
    ok &= all(o.producer.op == "convert"
              and o.producer.results[0].type == tir.FLOAT32
              for o in fdiv[0].operands)
    ok &= tir.verify_module(mod) == []
    check("int-true-division-is-fp32", ok)

    # the store value converts to the pointee type (fp32 tensor -> fp16 ptr)
    mod, _ = lower("""
v = tl.load(x_ptr + tl.arange(0, BLOCK))
tl.store(y_ptr + tl.arange(0, BLOCK), v)
""", {"x_ptr": np.zeros(8, np.float32), "y_ptr": np.zeros(8, np.float16),
      "n": 3})
    ops = ops_of(mod)
    cvts = [o for o in ops if o.op == "convert"]
    st = [o for o in ops if o.op == "store"][0]
    ok = any(c.results[0].type == tir.FLOAT16 and
             c.attrs.get("from") == tir.FLOAT32 for c in cvts)
    ok &= st.operands[1].type == tir.FLOAT16
    ok &= tir.verify_module(mod) == []
    check("store-value-converts-to-pointee", ok)

    # mixed fp16/bf16 unification computes in fp32 (pinned rule 4)
    mod, _ = lower("""
a = tl.load(x_ptr + tl.arange(0, BLOCK))
b = tl.load(y_ptr + tl.arange(0, BLOCK))
c = a + b
tl.store(y_ptr + tl.arange(0, BLOCK), c)
""", {"x_ptr": np.zeros(8, np.float16), "y_ptr": np.zeros(8, np.float32),
      "n": 3})
    ops = ops_of(mod)
    add = [o for o in ops if o.op == "arith.add"][0]
    ok = add.results[0].type == tir.FLOAT32
    ok &= any(o.op == "convert" and o.results[0].type == tir.FLOAT32
              and o.attrs.get("from") == tir.FLOAT16 for o in ops)
    ok &= tir.verify_module(mod) == []
    check("fp16-fp32-promotion-computes-fp32", ok)

    # a bf16 pointer override types the load bf16 while the host is fp32
    mod, _ = lower("""
v = tl.load(x_ptr + tl.arange(0, BLOCK))
tl.store(y_ptr + tl.arange(0, BLOCK), v)
""", {"x_ptr": np.zeros(8, np.float32), "y_ptr": np.zeros(8, np.float32),
      "n": 3}, pdt={"x_ptr": "bfloat16", "y_ptr": "bfloat16"})
    ld = [o for o in ops_of(mod) if o.op == "load"]
    st = [o for o in ops_of(mod) if o.op == "store"]
    ok = ld and ld[0].results[0].type == tir.BFLOAT16
    ok &= st and st[0].operands[1].type == tir.BFLOAT16
    ok &= tir.verify_module(mod) == []
    check("bf16-pointer-override-types-loads", ok)

    # int lanes stored through an i1 pointer keep i1 semantics (pinned:
    # pointer<int1> storage is a backend concern, the TIR types stay i1)
    mod, _ = lower("""
v = tl.load(x_ptr + tl.arange(0, BLOCK))
tl.store(y_ptr + tl.arange(0, BLOCK), v & v)
""", {"x_ptr": np.zeros(8, np.bool_), "y_ptr": np.zeros(8, np.bool_),
      "n": 3})
    ops = ops_of(mod)
    ok = any(o.op == "bit.and" and o.results[0].type == tir.INT1
             for o in ops)
    ok &= tir.verify_module(mod) == []
    check("bool-lanes-stay-i1", ok)


def main() -> int:
    check_literal_typing()
    check_integer_promote()
    check_computation_type()
    check_literal_guards()
    check_convert_vs_bitcast()
    check_scalar_arg_and_class()
    check_zero_dim_and_end_to_end()
    if FAILURES:
        print(f"test_frontend_types: {len(FAILURES)} check(s) FAILED: "
              f"{FAILURES}")
        return 1
    print("test_frontend_types: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
