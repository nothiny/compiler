#!/usr/bin/env python3
"""test_select.py -- one generic matcher over the repertoire table (T007).

Every MIR op must map to exactly one repertoire row by (opcode, features);
a construct with no row is refused with a located diagnostic naming it --
never matched to a nearby form.  The table is data: adding a row selects a
new construct with no matcher edit; removing rows makes selection refuse
(MECH-TARGET-DESCRIPTION-AS-DATA, TGT-INSTRUCTION-REPERTOIRE).

Run: python3 a100c/tests/test_select.py   (exit 0 = all checks PASS)
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
from a100c.backend.repertoire import (ABSENT_FORMS, InstructionEntry,  # noqa: E402
                                       Repertoire, DEFAULT_REPERTOIRE)
from a100c.frontend import lower_tir, source, specialize  # noqa: E402
from a100c.ir import mir  # noqa: E402
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


def legalized_mir():
    case = load_case()
    src = source.load_operator(str(SLICE))
    spec = specialize.specialize(src, case)
    tir_module = lower_tir.lower(src, spec)
    grid = grid_mod.extract_grid(src, case)
    layout = binding_mod.argument_layout(case, spec)
    module = vectorize.lower_to_mir(tir_module, part_mod.ExecutionPlan(),
                                    DEFAULT_TARGET, layout, grid)
    legal_mod.legalize(module)
    return module


def check_slice_selection():
    module = legalized_mir()
    try:
        selection = select_mod.select(module)
    except select_mod.SelectionError as exc:
        check("slice-selects-fully", False, str(exc)[:100])
        return
    mnemonics = {s.mnemonic for s in selection.values()}
    # T011's wide-access selection: this kernel's structurally proven
    # contiguous accesses select the unit-stride forms (vle32.v/vse32.v)
    # instead of the indexed vluxei64/vsuxei64, and the address
    # widening/scaling ops (vwadd.vx, vmul.vx) disappear with them
    expected = {"vsetvli", "vid.v", "vmv.v.x", "vadd.vv", "vadd.vx",
                "vmslt.vv", "vmflt.vv", "vfmul.vv", "vfsgnjn.vv",
                "vmerge.vvm", "vmv1r.v", "vle32.v", "vse32.v",
                "vcpop.m", "li", "ld", "lwu",
                "add", "addw", "sub", "mulw", "divu", "slt",
                "mv", "addiw", "sd", "j", "bne", "ret"}
    missing = expected - mnemonics
    check("slice-selection-mnemonics", not missing,
          f"missing {sorted(missing)}" if missing else
          f"{len(mnemonics)} distinct mnemonics")
    check("selection-recorded-in-meta",
          module.meta["selection"]["ops"] == len(selection))


def check_refusals():
    # a feature combination with no row (vector frem: vfdiv gained a row
    # when the reduction families' mean kernels needed it -- T009) is
    # refused, located
    module = legalized_mir()
    fn = module.functions[0]
    block = fn.blocks[-1]
    a = mir.VReg(mir.VectorType(32, 1, "float"), name="fa")
    bad = mir.MOp("vbin", [a, mir.VReg(mir.VectorType(32, 1, "float"),
                                       name="fb")],
                  [mir.VReg(mir.VectorType(32, 1, "float"), name="fd")],
                  attrs={"op": "frem"}, loc=None)
    block.ops.insert(0, bad)
    try:
        select_mod.select(module)
        check("no-row-refused", False, "selection accepted frem")
    except select_mod.SelectionError as exc:
        check("no-row-refused", "frem" in str(exc) and "vbin" in str(exc),
              str(exc)[:90])
    # the repertoire itself reports the miss
    check("repertoire-find-miss",
          DEFAULT_REPERTOIRE.find("vbin", {"op": "frem", "fp": True}) is None)
    # vfdiv is implemented now (the mean kernels' normalize division)
    check("repertoire-find-vfdiv",
          (DEFAULT_REPERTOIRE.find("vbin", {"op": "fdiv", "fp": True}) or
           InstructionEntry("", "", (), "")).mnemonic == "vfdiv.vv")
    check("repertoire-find-hit",
          (DEFAULT_REPERTOIRE.find("vbin", {"op": "mul", "fp": True}) or
           InstructionEntry("", "", (), "")).mnemonic == "vfmul.vv")
    check("fp-and-int-mul-are-distinct-rows",
          DEFAULT_REPERTOIRE.find("vbin", {"op": "mul",
                                           "fp": False}).mnemonic == "vmul.vv")


def check_table_is_data():
    """Adding a row selects a new construct with no matcher edit; a subset
    table refuses what it lacks."""
    rep = Repertoire(list(DEFAULT_REPERTOIRE.entries))
    features = {"op": "fdiv"}
    check("absent-before-add", rep.find("vbin", features) is None)
    rep.add(InstructionEntry("vfdiv.vv", "vbin", (("op", "fdiv"),),
                             "vfdiv.vv {vd}, {vs2}, {vs1}"))
    entry = rep.find("vbin", features)
    check("present-after-add", entry is not None and entry.mnemonic == "vfdiv.vv")

    # a table without the merge row refuses the slice's selects
    subset = Repertoire([e for e in DEFAULT_REPERTOIRE.entries
                         if e.opcode != "vsel"])
    module = legalized_mir()
    try:
        select_mod.select(module, subset)
        check("subset-table-refuses", False, "selection matched without a row")
    except select_mod.SelectionError as exc:
        check("subset-table-refuses", "vsel" in str(exc), str(exc)[:80])

    # the declared absences are recorded as data
    check("absent-forms-recorded",
          len(ABSENT_FORMS) >= 5
          and any("v0" in form for form, _ in ABSENT_FORMS)
          and any("EEW=128" in form for form, _ in ABSENT_FORMS),
          f"{len(ABSENT_FORMS)} declared absences")


def main() -> int:
    check_slice_selection()
    check_refusals()
    check_table_is_data()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_select: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
