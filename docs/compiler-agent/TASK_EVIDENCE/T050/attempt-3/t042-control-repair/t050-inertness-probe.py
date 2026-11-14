#!/usr/bin/env python3
"""Differential probe: does the T050 override lookup change the amax MIR
that test_t042_repairs' constraint-off coloring control depends on?

Builds the amax_kernel_1 [17] float16 legalized MIR twice -- once with the
current _materialize_scalar_tree (T050 fix in) and once with the pre-fix
form (const producer re-emits its constant without consulting the
enclosing regions' carried bindings, the same strip as test_t050_repairs'
control) -- then runs the T042 control logic (mask-compare-group constraint
disabled, _try_color) on both and reports the violations found.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path("/home/i_yinzida/compiler-a100-experiment-001")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ops" / "harness"))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(str(ROOT))

import run_scan as rs                                    # noqa: E402
from a100c.backend import allocate as alloc_mod          # noqa: E402
from a100c.backend import legalize as legal_mod          # noqa: E402
from a100c.frontend import lower_tir, source, specialize  # noqa: E402
from a100c.lower import binding as binding_mod           # noqa: E402
from a100c.lower import vectorize                        # noqa: E402
from a100c.plan import grid as grid_mod                  # noqa: E402
from a100c.plan import partition as part_mod             # noqa: E402
from a100c.target import DEFAULT_TARGET                  # noqa: E402

AMAX = "suite/dev/amax_kernel_1.py"


def build_mir(strip: bool):
    rows = list(rs.enumerated_rows(rs.DEFAULT_MANIFEST, None, [AMAX]))
    row = next(r for r in rows if r["shape"] == [17] and r["dtype"] == "float16")
    case = rs.build_case(row, 30, use_golden=True)
    path = ROOT / "ops" / "suite" / AMAX.split("/", 1)[1]
    src = source.load_operator(str(path))
    spec = specialize.specialize(src, case)
    tir_module = lower_tir.lower(src, spec)
    grid = grid_mod.extract_grid(src, case)
    layout = binding_mod.argument_layout(case, spec)
    if strip:
        original = vectorize.SliceLowering._materialize_scalar_tree

        def stripped(self, ctx, v, loc, allow_bound_leaves=False):
            prod = v.producer
            if prod is not None and prod.op == "const":
                from a100c.lower import scalar as scalar_mod
                return scalar_mod.lower_const(
                    ctx, prod.attrs["value"], v.type, loc)
            return original(self, ctx, v, loc,
                            allow_bound_leaves=allow_bound_leaves)

        vectorize.SliceLowering._materialize_scalar_tree = stripped
        try:
            module = vectorize.lower_to_mir(
                tir_module, part_mod.ExecutionPlan(), DEFAULT_TARGET,
                layout, grid)
        finally:
            vectorize.SliceLowering._materialize_scalar_tree = original
    else:
        module = vectorize.lower_to_mir(
            tir_module, part_mod.ExecutionPlan(), DEFAULT_TARGET,
            layout, grid)
    legal_mod.legalize(module)
    return module


def mir_fingerprint(module):
    """A structural digest: op counts by opcode + total ops."""
    counts = {}
    total = 0
    for fn in module.functions:
        for b in fn.blocks:
            for op in b.ops:
                counts[op.opcode] = counts.get(op.opcode, 0) + 1
                total += 1
    return total, counts


def control_violations(module):
    """The T042 control: constraint-off coloring must reproduce a
    mask-inside-source-group placement."""
    fn = module.functions[0]
    fixed = {}
    for b in fn.blocks:
        for op in b.ops:
            for r in op.results:
                if r.fixed_phys == "v0":
                    fixed[r.rid] = "v0"
    original = alloc_mod._mask_compare_groups
    try:
        alloc_mod._mask_compare_groups = lambda fn_: ({}, {})
        assignment, failed = alloc_mod._try_color(fn, DEFAULT_TARGET, fixed)
    finally:
        alloc_mod._mask_compare_groups = original
    if assignment is None:
        return None, "coloring FAILED (no assignment)"
    # the T042 violation predicate
    implied = alloc_mod._index_implied_groups(fn)
    out = []
    for b in fn.blocks:
        for op in b.ops:
            if op.opcode not in ("vcmp", "vcmpx"):
                continue
            if not op.results or not op.results[0].is_mask():
                continue
            dst = assignment.get(op.results[0].rid)
            if not dst or not dst.startswith("v"):
                continue
            d = int(dst[1:])
            for o in op.operands:
                if not o.is_vector():
                    continue
                nm = assignment.get(o.rid)
                if not nm or not nm.startswith("v"):
                    continue
                base = int(nm[1:])
                span = max(o.type.lmul if o.is_vector() else 1,
                           implied.get(o.rid, 1))
                if base < d < base + span:
                    out.append((op.results[0].name, dst, o.name, nm, span))
    return assignment, out


for strip in (False, True):
    tag = "PRE-FIX (stripped)" if strip else "CURRENT (T050 fix in)"
    module = build_mir(strip)
    total, counts = mir_fingerprint(module)
    assignment, violations = control_violations(module)
    print(f"== {tag}: {total} ops; ssub={counts.get('ssub')} vcmp={counts.get('vcmp')} "
          f"vmseq={counts.get('vmseq')} ld={counts.get('ld')}")
    if assignment is None:
        print("   constraint-off coloring: FAILED")
    else:
        print(f"   constraint-off coloring violations: {len(violations)}")
        for v in violations[:4]:
            print(f"     {v}")
