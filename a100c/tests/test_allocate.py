#!/usr/bin/env python3
"""test_allocate.py -- interference-based allocation with spill/split (T007).

Every live value gets a location: 32 GPRs (minus the reserved ABI registers)
and the 32 x 128 B vector register file.  Interference comes from the real
liveness analysis over the real CFG; the allocation of the actual slice MIR
must be interference-free and inside the file budget; exceeding the vector
file is a compiler-owned spill/split (the synthetic high-pressure case must
spill and still verify); mask exhaustion is a bounded, located refusal
(F041: the vector file has no architectural spill).

Run: python3 a100c/tests/test_allocate.py   (exit 0 = all checks PASS)
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

from a100c.backend import allocate as alloc_mod  # noqa: E402
from a100c.backend import legalize as legal_mod  # noqa: E402
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


def check_slice_allocation():
    module = legalized_mir()
    try:
        allocation = alloc_mod.allocate(module, DEFAULT_TARGET)
    except alloc_mod.AllocationError as exc:
        check("slice-allocates", False, str(exc)[:100])
        return
    values = [v for fn in module.functions for b in fn.blocks
              for v in b.params] + \
             [r for fn in module.functions for b in fn.blocks
              for op in b.ops for r in op.results]
    missing = [v.name for v in values
               if v.rid not in allocation.assignment]
    check("every-value-has-a-location", not missing, str(missing[:4]))
    # interference-free: no two simultaneously-live values share a register
    fn = module.functions[0]
    graph, _ = alloc_mod._interference(fn)
    conflicts = []
    for rid, neighbors in graph.items():
        name = allocation.assignment.get(rid)
        for n in neighbors:
            if allocation.assignment.get(n) == name:
                conflicts.append((rid, n, name))
    check("no-interfering-pair-shares-a-register", not conflicts,
          str(conflicts[:3]))
    # the fixed working masks are all v0
    fixed = [v for fn in module.functions for b in fn.blocks
             for op in b.ops for v in op.results if v.fixed_phys == "v0"]
    check("working-masks-pinned-to-v0",
          fixed and all(allocation.assignment[v.rid] == "v0" for v in fixed))
    # v0 is never allocated to a free value
    check("v0-never-allocated",
          not [rid for rid, name in allocation.assignment.items()
               if name == "v0" and rid not in {v.rid for v in fixed}])
    stats = allocation.stats
    check("vector-file-within-budget",
          stats["vector_regs_used"] <= 32
          and stats["vector_bytes_used"] <= DEFAULT_TARGET.vector_file_bytes,
          f"{stats['vector_regs_used']} regs, {stats['vector_bytes_used']} B "
          f"of {DEFAULT_TARGET.vector_file_bytes} B")
    check("slice-does-not-spill", stats["spilled_values"] == 0,
          str(stats))
    # m2 groups are even-aligned pairs
    bad_m2 = []
    for fn in module.functions:
        for b in fn.blocks:
            for op in b.ops:
                for r in op.results:
                    if r.is_vector() and r.type.lmul == 2:
                        name = allocation.assignment.get(r.rid, "")
                        if name.startswith("v") and int(name[1:]) % 2:
                            bad_m2.append(name)
    check("m2-groups-even-aligned", not bad_m2, str(bad_m2))


def _high_pressure_function(count: int, mtype=None):
    """count simultaneously-live vector values + one use of each."""
    mtype = mtype or mir.VectorType(32, 1, "int")
    fn = mir.MFunction("pressure", [])
    entry = mir.Block("entry")
    fn.blocks.append(entry)
    regs = []
    for i in range(count):
        reg = mir.VReg(mtype, name=f"p{i}")
        entry.ops.append(mir.MOp("vid", [], [reg],
                                 attrs={"sew": 32, "lmul": 1}))
        regs.append(reg)
    # consume them all at the end (a single vbin chain)
    acc = regs[0]
    for r in regs[1:]:
        nxt = mir.VReg(mtype, name=f"s{r.name}")
        entry.ops.append(mir.MOp("vbin", [acc, r], [nxt], attrs={"op": "add"}))
        acc = nxt
    entry.ops.append(mir.MOp("ret", [], []))
    module = mir.MModule("pressure", "<probe>")
    module.functions.append(fn)
    return module


def check_vector_spill():
    """35 simultaneously-live m1 vector values exceed the 31 usable
    registers: the allocator must spill/split, and the result must still
    verify (full-vl regions make the vector spill legal)."""
    module = _high_pressure_function(35)
    # the region: vl must equal vlmax for the spill to be legal
    avl = mir.VReg(mir.I32, name="avl")
    module.functions[0].blocks[0].ops.insert(
        0, mir.MOp("sconst", [], [avl], attrs={"value": 32}))
    module.functions[0].blocks[0].ops.insert(
        1, mir.MOp("vsetvli", [avl], [mir.VReg(mir.I32, name="vlr")],
                   attrs={"sew": 32, "lmul": 1, "policy": "ta,ma"}))
    try:
        allocation = alloc_mod.allocate(module, DEFAULT_TARGET)
    except alloc_mod.AllocationError as exc:
        check("vector-spill-fires", False, str(exc)[:120])
        return
    stats = allocation.stats
    check("vector-spill-fires",
          stats["spilled_values"] > 0 and stats["spill_slots"] > 0,
          str(stats))
    ops = {op.opcode for fn in module.functions for b in fn.blocks
           for op in b.ops}
    check("spill-ops-inserted",
          ("vspill" in ops and "vreload" in ops)
          or ("sspill" in ops and "sreload" in ops), str(sorted(ops)))
    errors = mir.verify_module(module)
    check("post-spill-module-verifies", not errors,
          str(errors[0]) if errors else "")
    check("spill-slots-sized-by-value-class",
          all(size in (DEFAULT_TARGET.vlenb, 8) for size in allocation.slots),
          str(allocation.slots))


def check_scalar_spill():
    """More simultaneously-live scalars than allocatable GPRs: spill/split
    through the stack."""
    module = _high_pressure_function(40, mtype=mir.I64)
    # retype: the pressure builder used vid (vector); build scalar pressure
    fn = mir.MFunction("gpr_pressure", [])
    entry = mir.Block("entry")
    fn.blocks.append(entry)
    regs = []
    for i in range(40):
        reg = mir.VReg(mir.I64, name=f"g{i}")
        entry.ops.append(mir.MOp("sconst", [], [reg], attrs={"value": i}))
        regs.append(reg)
    acc = regs[0]
    for r in regs[1:]:
        nxt = mir.VReg(mir.I64, name=f"a{r.name}")
        entry.ops.append(mir.MOp("sadd", [acc, r], [nxt]))
        acc = nxt
    entry.ops.append(mir.MOp("ret", [], []))
    module = mir.MModule("gpr_pressure", "<probe>")
    module.functions.append(fn)
    try:
        allocation = alloc_mod.allocate(module, DEFAULT_TARGET)
    except alloc_mod.AllocationError as exc:
        check("scalar-spill-fires", False, str(exc)[:120])
        return
    ops = {op.opcode for fn in module.functions for b in fn.blocks
           for op in b.ops}
    check("scalar-spill-fires",
          allocation.stats["spilled_values"] > 0 and "sspill" in ops
          and "sreload" in ops, str(allocation.stats))
    errors = mir.verify_module(module)
    check("post-scalar-spill-verifies", not errors,
          str(errors[0]) if errors else "")


def check_mask_refusal():
    """Mask exhaustion is a bounded, located refusal (mask spill is not
    implemented; a silent misallocation would be the defect)."""
    fn = mir.MFunction("mask_pressure", [])
    entry = mir.Block("entry")
    fn.blocks.append(entry)
    avl = mir.VReg(mir.I32, name="avl")
    entry.ops.append(mir.MOp("sconst", [], [avl], attrs={"value": 32}))
    entry.ops.append(mir.MOp("vsetvli", [avl], [mir.VReg(mir.I32, name="vl")],
                             attrs={"sew": 32, "lmul": 1, "policy": "ta,ma"}))
    src = mir.VReg(mir.VectorType(32, 1, "int"), name="src")
    entry.ops.append(mir.MOp("vid", [], [src]))
    zero = mir.VReg(mir.I32, name="zero")
    entry.ops.append(mir.MOp("sconst", [], [zero], attrs={"value": 0}))
    masks = []
    for i in range(40):
        m = mir.VReg(mir.MaskType(), name=f"m{i}")
        entry.ops.append(mir.MOp("vcmpx", [src, zero], [m],
                                 attrs={"pred": "lt"}))
        masks.append(m)
    # consume all masks
    acc = masks[0]
    for m in masks[1:]:
        v0 = mir.VReg(mir.MaskType(), name=f"w{m.name}", fixed_phys="v0")
        entry.ops.append(mir.MOp("vmovmask", [acc], [v0]))
        acc = m
    entry.ops.append(mir.MOp("vmovmask", [acc],
                             [mir.VReg(mir.MaskType(), name="wend",
                                       fixed_phys="v0")]))
    entry.ops.append(mir.MOp("ret", [], []))
    module = mir.MModule("mask_pressure", "<probe>")
    module.functions.append(fn)
    try:
        alloc_mod.allocate(module, DEFAULT_TARGET)
        check("mask-exhaustion-refuses", False,
              "allocation succeeded past the mask file")
    except alloc_mod.AllocationError as exc:
        check("mask-exhaustion-refuses",
              "mask" in str(exc) or "spill" in str(exc), str(exc)[:100])


def main() -> int:
    check_slice_allocation()
    check_vector_spill()
    check_scalar_spill()
    check_mask_refusal()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_allocate: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
