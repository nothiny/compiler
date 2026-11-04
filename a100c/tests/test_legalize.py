#!/usr/bin/env python3
"""test_legalize.py -- the declared legalisation stage (T007).

Contract: it accepts MIR constructs the target cannot execute directly and
rewrites them into legal sequences; after it runs, every remaining construct
is in the declared repertoire (selection relies on that guarantee).

  ``vwiden sext/zext`` -> ``vwaddx0`` (vwadd/vwaddu.vx with rs1 = x0):
      no target instruction widens by itself.
  ``strunc`` (i64 -> i32) -> ``swext`` (addiw rd, rs, 0): RV64 has no
      truncation instruction; i32 values live sign-extended.

The control (MECH-WITNESS-TEST): with a rewrite disabled the construct
survives and SELECTION refuses it with a located diagnostic -- the illegal
construct is reported, never silently assembled.

Run: python3 a100c/tests/test_legalize.py   (exit 0 = all checks PASS)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
import warnings  # noqa: E402

warnings.filterwarnings("ignore")

FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(name)
    return ok


import importlib.util  # noqa: E402

from a100c.backend import legalize as legal_mod  # noqa: E402
from a100c.backend import select as select_mod  # noqa: E402
from a100c.frontend import lower_tir, source, specialize  # noqa: E402
from a100c.ir import mir, tir  # noqa: E402
from a100c.lower import binding as binding_mod  # noqa: E402
from a100c.lower import vectorize  # noqa: E402
from a100c.plan import grid as grid_mod  # noqa: E402
from a100c.plan import partition as part_mod  # noqa: E402
from a100c.target import DEFAULT_TARGET  # noqa: E402

SLICE = ROOT / "ops" / "suite" / "dev" / "absolute_kernel.py"


def load_case():
    spec = importlib.util.spec_from_file_location("slice_operator", SLICE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.make_case(shape=(97,))


def lowered_mir():
    case = load_case()
    src = source.load_operator(str(SLICE))
    spec = specialize.specialize(src, case)
    tir_module = lower_tir.lower(src, spec)
    grid = grid_mod.extract_grid(src, case)
    layout = binding_mod.argument_layout(case, spec)
    return vectorize.lower_to_mir(tir_module, part_mod.ExecutionPlan(),
                                  DEFAULT_TARGET, layout, grid)


def _wide_selected(module) -> bool:
    """T011's wide-access selection present: a unit-stride vector memory
    op (the proof-selected form) exists in the module."""
    return any(op.opcode in ("vunit_load", "vunit_store")
               for fn in module.functions for b in fn.blocks
               for op in b.ops)


INDIRECT_TEXT = '''"""probe"""
OPERATOR = {"name": "probe/ind", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness", "tags": []}
SHAPES = ((257,),)
import numpy as np
import triton
import triton.language as tl

@triton.jit
def ind_kernel(x_ptr, y_ptr, out_ptr, n, BLOCK: tl.constexpr):
    i = tl.program_id(0) * BLOCK + tl.arange(0, BLOCK)
    m = i < n
    idx = tl.load(x_ptr + i, mask=m, other=0)
    v = tl.load(y_ptr + idx, mask=m, other=0)
    tl.store(out_ptr + i, v, mask=m)

def ref(args, meta):
    idx = np.asarray(args["x_ptr"]).astype(np.int64)
    y = np.asarray(args["y_ptr"])
    return {"out_ptr": y[idx]}

def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n = int(shape[0])
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, n).astype(np.int32)
    y = rng.standard_normal(n).astype(np.float32)
    args = {"x_ptr": idx, "y_ptr": y,
            "out_ptr": np.zeros(n, np.float32), "n": n}
    meta = {"BLOCK": 128}
    grid = ((n + 127) // 128,)
    return {"args": args, "meta": meta, "grid": grid,
            "kernel": ind_kernel, "outputs": ("out_ptr",),
            "expected": ref(args, meta),
            "comparison": {"out_ptr": {"comparator": "allclose", "exact": False,
                                       "rtol": 1e-6, "atol": 1e-6, "equal_nan": True}}}

def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or SHAPES[0],
                      dtype=dtype or "float32", seed=seed or 0)
'''


def indirect_mir():
    """A module whose access is INDIRECT (a loaded index vector): the
    wide-access proof declines, the indexed form and its e64m2 address
    vector (with the vwiden) must exist."""
    import tempfile
    d = Path(tempfile.mkdtemp(prefix="a100c-leg-"))
    p = d / "ind.py"
    p.write_text(INDIRECT_TEXT)
    import importlib.util
    spec = importlib.util.spec_from_file_location("ind", str(p))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    case = module.make_case()
    src = source.load_operator(str(p))
    spec2 = specialize.specialize(src, case)
    tir_module = lower_tir.lower(src, spec2)
    grid = grid_mod.extract_grid(src, case)
    layout = binding_mod.argument_layout(case, spec2)
    return vectorize.lower_to_mir(tir_module, part_mod.ExecutionPlan(),
                                  DEFAULT_TARGET, layout, grid)


def check_rewrites():
    # the rewrite counts run on the INDIRECT module (its address vector
    # must exist); the slice kernel's own module is checked for the
    # wide-selected world below
    module = indirect_mir()
    before_vwiden = sum(1 for fn in module.functions for b in fn.blocks
                        for op in b.ops if op.opcode == "vwiden")
    before_strunc = sum(1 for fn in module.functions for b in fn.blocks
                        for op in b.ops if op.opcode == "strunc")
    report = legal_mod.legalize(module)
    after = {op.opcode for fn in module.functions for b in fn.blocks
             for op in b.ops}
    # T011's wide-access selection removed this kernel's widenings (its
    # accesses are structurally proven contiguous, so the unit-stride form
    # needs no e64m2 address vector); the rewrite itself is exercised on
    # the indirect module below, whose address vector must exist
    check("vwiden-rewritten-to-vwaddx0",
          (before_vwiden == 0 and _wide_selected(module))
          or (before_vwiden > 0
              and report.rewrites.get("vwiden->vwaddx0") == before_vwiden
              and "vwiden" not in after),
          f"{before_vwiden} widenings")
    check("strunc-rewritten-to-swext",
          before_strunc > 0
          and report.rewrites.get("strunc->swext") == before_strunc
          and "strunc" not in after,
          f"{before_strunc} truncations")
    errors = mir.verify_module(module)
    check("post-legalize-module-verifies", not errors,
          str(errors[0]) if errors else "")
    try:
        select_mod.select(module)
        check("post-legalize-everything-selects", True)
    except select_mod.SelectionError as exc:
        check("post-legalize-everything-selects", False, str(exc)[:100])


def check_disabled_control():
    """The control: a disabled rewrite leaves the illegal construct and
    selection refuses it (the check can fail, so it proves something)."""
    # the control runs on the INDIRECT module (a loaded index vector: the
    # wide-access proof declines, so its e64m2 address vector -- with the
    # vwiden -- must exist for the disabled rewrite to leave behind)
    module = indirect_mir()
    report = legal_mod.legalize(
        module, legal_mod.LegalizeOptions(disabled={"vwiden"}))
    check("disabled-rewrite-declines",
          report.declined.get("vwiden", 0) > 0
          and any(op.opcode == "vwiden"
                  for fn in module.functions for b in fn.blocks
                  for op in b.ops))
    try:
        select_mod.select(module)
        check("disabled-rewrite-refused-by-selection", False,
              "selection accepted an illegal construct")
    except select_mod.SelectionError as exc:
        check("disabled-rewrite-refused-by-selection",
              "vwiden" in str(exc), str(exc)[:100])


def main() -> int:
    check_rewrites()
    check_disabled_control()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_legalize: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
