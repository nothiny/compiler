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


def check_rewrites():
    module = lowered_mir()
    before_vwiden = sum(1 for fn in module.functions for b in fn.blocks
                        for op in b.ops if op.opcode == "vwiden")
    before_strunc = sum(1 for fn in module.functions for b in fn.blocks
                        for op in b.ops if op.opcode == "strunc")
    report = legal_mod.legalize(module)
    after = {op.opcode for fn in module.functions for b in fn.blocks
             for op in b.ops}
    check("vwiden-rewritten-to-vwaddx0",
          before_vwiden > 0
          and report.rewrites.get("vwiden->vwaddx0") == before_vwiden
          and "vwiden" not in after,
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
    module = lowered_mir()
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
