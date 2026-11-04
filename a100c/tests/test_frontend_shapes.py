#!/usr/bin/env python3
"""test_frontend_shapes.py -- rank/extent inference with broadcast extents
distinguished from real extents (T006, FE-SHAPE-AND-BROADCAST).

Shapes align from the right (the pinned Triton 3.8 ``broadcast_impl_value``
prepends singleton axes); an axis expands only from extent 1; a
disagreement the rules do not permit is a diagnostic, never a silent
stretch.  Broadcast extents stay flagged through the pipeline and must be
realized before a memory op consumes them as real extents.

Run: python3 a100c/tests/test_frontend_shapes.py   (exit 0 = all PASS)
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
from a100c.frontend import shapes as fshapes  # noqa: E402
from a100c.frontend.source import FrontendError  # noqa: E402
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


def lower(body, args, meta=None):
    text = TEMPLATE.format(
        params="x_ptr, y_ptr, n, BLOCK: tl.constexpr",
        body="\n".join("    " + line for line in body.splitlines()))
    src = source.load_operator_text(text, "<probe>", "probe.py")
    case = {"args": args, "meta": meta or {"BLOCK": 8}, "launch_meta": {}}
    spec = specialize.specialize(src, case)
    return lower_tir.lower(src, spec), spec, src


def ops_of(module):
    return [st for st in module.functions[0].body.statements
            if isinstance(st, tir.Op)]


def E(v, b=False):
    return tir.Extent(v, b)


def check_unify_pair():
    bad = []
    # (8,1) + (1,16) -> (8,16): each operand expands along one axis and the
    # expanded operand carries the target extent flagged broadcast
    target, a, b = fshapes.unify_pair((E(8), E(1)), (E(1), E(16)))
    if (target, a, b) != ((E(8), E(16)), (E(8), E(16, True)),
                          (E(8, True), E(16))):
        bad.append(f"2d: {target} {a} {b}")
    # rank alignment is from the right (pinned broadcast_impl_value):
    # (16,) aligns to (1,16) and its padded axis expands against (8,16)
    target, a, b = fshapes.unify_pair((E(16),), (E(8), E(16)))
    if (target, a, b) != ((E(8), E(16)), (E(8, True), E(16)),
                          (E(8), E(16))):
        bad.append(f"rank-align: {target} {a} {b}")
    # scalar splat: () + (8,) -> (8,) with the scalar fully broadcast
    target, a, b = fshapes.unify_pair((), (E(8),))
    if (target, a, b) != ((E(8),), (E(8, True),), (E(8),)):
        bad.append(f"scalar: {target} {a} {b}")
    # equal shapes stay untouched
    target, a, b = fshapes.unify_pair((E(8),), (E(8),))
    if (target, a, b) != ((E(8),), (E(8),), (E(8),)):
        bad.append(f"equal: {target} {a} {b}")
    check("unify-pair-pinned-rules", not bad, "; ".join(bad))


def check_disagreement_is_diagnostic():
    bad = []
    for a, b in (((E(8),), (E(16),)), ((E(8), E(3)), (E(8), E(4))),
                 ((E(8),), (E(8), E(16)))):
        try:
            fshapes.unify_pair(a, b)
            bad.append(f"{a}+{b} unified")
        except fshapes.ShapeError as exc:
            if "cannot unify" not in str(exc):
                bad.append(f"{a}+{b}: {exc}")
    # end to end: two aranges of different extents disagree at the add
    try:
        lower("""
a = tl.arange(0, BLOCK)
b = tl.arange(0, 16)
c = a + b
tl.store(y_ptr + a, c)
""", {"x_ptr": np.zeros(8, np.float32), "y_ptr": np.zeros(8, np.float32),
      "n": 3}, {"BLOCK": 8})
        bad.append("8+16 arange add lowered")
    except FrontendError as exc:
        if "cannot unify" not in str(exc) or not exc.line:
            bad.append(f"end-to-end: {exc}")
    check("shape-disagreement-is-a-diagnostic", not bad, "; ".join(bad[:3]))


def check_subscript_refused():
    """T012: the ``[:, None]`` expand_dims subscript lowers (a reshape);
    an integer index still refuses (the pinned __getitem__ refuses it)."""
    try:
        mod, _, _ = lower("""
rows = tl.arange(0, BLOCK)[:, None]
""", {"x_ptr": np.zeros(8, np.float32), "y_ptr": np.zeros(8, np.float32),
      "n": 3}, {"BLOCK": 8})
        rows = [v for fn in mod.functions for v in ()]
        ok = True
        for fn in mod.functions:
            for st in fn.body.statements:
                if isinstance(st, __import__("a100c.ir.tir",
                                             fromlist=["tir"]).Op) \
                        and st.op == "reshape":
                    want = __import__("a100c.ir.tir",
                                      fromlist=["tir"]).real_shape([8, 1])
                    ok &= st.results[0].shape == want
        check("subscript-none-lowers-to-reshape", ok,
              "the [:, None] subscript expands the axis")
    except FrontendError as exc:
        check("subscript-none-lowers-to-reshape", False, f"line {exc.line}")
    try:
        lower("""
rows = tl.arange(0, BLOCK)[0]
""", {"x_ptr": np.zeros(8, np.float32), "y_ptr": np.zeros(8, np.float32),
      "n": 3}, {"BLOCK": 8})
        check("subscript-index-not-in-core-refused", False, "lowered")
    except FrontendError as exc:
        check("subscript-index-not-in-core-refused",
              "subscript" in str(exc) and exc.line == 11, f"line {exc.line}")


def check_scalar_store_realizes():
    """A scalar (zero-dim) store value is broadcast (flagged) and then
    realized: the store consumes real extents only."""
    mod, _, _ = lower("""
v = tl.load(x_ptr + tl.arange(0, BLOCK))
tl.store(y_ptr + tl.arange(0, BLOCK), 2.0)
""", {"x_ptr": np.zeros(8, np.float32), "y_ptr": np.zeros(8, np.float32),
      "n": 3}, {"BLOCK": 8})
    ops = ops_of(mod)
    st = [o for o in ops if o.op == "store"][0]
    value = st.operands[1]
    ok = value.producer is not None and value.producer.op == "realize"
    ok &= all(not e.broadcast for e in value.shape)
    rz = value.producer
    ok &= rz.operands[0].producer.op == "broadcast"
    ok &= all(e.broadcast for e in rz.operands[0].shape)
    ok &= tir.verify_module(mod) == []
    check("scalar-store-value-realized-before-store", ok)


def check_where_broadcast():
    """tl.where unifies the branch shapes: a scalar branch broadcasts to
    the condition's block shape."""
    mod, _, _ = lower("""
offs = tl.arange(0, BLOCK)
v = tl.load(x_ptr + offs)
w = tl.where(v > 0.0, v, 0.0)
tl.store(y_ptr + offs, w)
""", {"x_ptr": np.zeros(8, np.float32), "y_ptr": np.zeros(8, np.float32),
      "n": 3}, {"BLOCK": 8})
    ops = ops_of(mod)
    sel = [o for o in ops if o.op == "select.where"][0]
    ok = all(o.rank == 1 for o in sel.operands)
    ok &= sel.results[0].shape == (E(8),)
    # the scalar 0.0 branch was broadcast (flagged) into the block
    bcs = [o for o in ops if o.op == "broadcast"
           and o.results[0].type == tir.FLOAT32]
    ok &= any(all(e.broadcast for e in o.results[0].shape) for o in bcs)
    ok &= tir.verify_module(mod) == []
    check("where-unifies-branch-shapes", ok)


def check_runtime_symbolic_extents():
    """Shapes, grid values and scalar values stay runtime-symbolic: the
    specialization identity does not contain the shape, and a masked load
    against a runtime bound keeps the bound as a value, never a constant."""
    mod, spec, _ = lower("""
offs = tl.arange(0, BLOCK)
m = offs < n
v = tl.load(x_ptr + offs, mask=m, other=0.0)
tl.store(y_ptr + offs, v, mask=m)
""", {"x_ptr": np.zeros(8, np.float32), "y_ptr": np.zeros(8, np.float32),
      "n": 17}, {"BLOCK": 8})
    mod2, spec2, _ = lower("""
offs = tl.arange(0, BLOCK)
m = offs < n
v = tl.load(x_ptr + offs, mask=m, other=0.0)
tl.store(y_ptr + offs, v, mask=m)
""", {"x_ptr": np.zeros(8, np.float32), "y_ptr": np.zeros(8, np.float32),
      "n": 4097}, {"BLOCK": 8})
    ops = ops_of(mod)
    cmps = [o for o in ops if o.op == "cmp.lt"]

    def root(v):
        while v.producer is not None and v.producer.op in ("broadcast",
                                                           "realize",
                                                           "convert"):
            v = v.producer.operands[0]
        return v

    ok = cmps and root(cmps[0].operands[1]).producer is None  # runtime n
    ok &= not any(o.op == "const" and o.attrs.get("value") in (17, 4097)
                  for o in ops)
    ok &= spec.identity == spec2.identity      # never baked into the key
    ok &= tir.verify_module(mod) == []
    # the grid never appears in the specialization at all
    ok &= all("grid" not in k for k, _ in spec.constexpr_values.items())
    check("shapes-and-scalars-stay-runtime-symbolic", ok)


def main() -> int:
    check_unify_pair()
    check_disagreement_is_diagnostic()
    check_subscript_refused()
    check_scalar_store_realizes()
    check_where_broadcast()
    check_runtime_symbolic_extents()
    if FAILURES:
        print(f"test_frontend_shapes: {len(FAILURES)} check(s) FAILED: "
              f"{FAILURES}")
        return 1
    print("test_frontend_shapes: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
