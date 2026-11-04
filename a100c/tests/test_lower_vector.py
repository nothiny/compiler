#!/usr/bin/env python3
"""test_lower_vector.py -- RVV vectorization, grid model, refusals (T007).

The vector slice lowers the elementwise core to MIR with vsetvli regions,
exact vl, masked tails (declared inactive semantics), whole-tree i64
addresses (base + sext(i32 index) * pointee size), the strided worker loop
and the native grid-evaluation form.  Everything outside the slice is a
located refusal (control flow, non-32-bit elements, masked loads with
other=, conversions, matrix-routed constructs) -- never a silent
approximation.

Run: python3 a100c/tests/test_lower_vector.py   (exit 0 = all checks PASS)
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

from a100c.frontend import lower_tir, source, specialize  # noqa: E402
from a100c.ir import mir, tir  # noqa: E402
from a100c.lower import binding as binding_mod  # noqa: E402
from a100c.lower import matrix as matrix_mod  # noqa: E402
from a100c.lower import scalar as scalar_mod  # noqa: E402
from a100c.lower import vectorize  # noqa: E402
from a100c.lower.addresses import check_address_model  # noqa: E402
from a100c.plan import grid as grid_mod  # noqa: E402
from a100c.plan import partition as part_mod  # noqa: E402
from a100c.target import DEFAULT_TARGET  # noqa: E402

SLICE = ROOT / "ops" / "suite" / "dev" / "absolute_kernel.py"


def load_case(shape=(97,)):
    spec = importlib.util.spec_from_file_location("slice_operator", SLICE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.make_case(shape=shape)


def lower_slice(shape=(97,), options=None):
    case = load_case(shape)
    src = source.load_operator(str(SLICE))
    spec = specialize.specialize(src, case)
    tir_module = lower_tir.lower(src, spec)
    errors = tir.verify_module(tir_module)
    assert not errors, errors
    grid = grid_mod.extract_grid(src, case)
    layout = binding_mod.argument_layout(case, spec)
    plan = part_mod.ExecutionPlan()
    mir_module = vectorize.lower_to_mir(tir_module, plan, DEFAULT_TARGET,
                                        layout, grid, options)
    return case, src, spec, tir_module, grid, layout, plan, mir_module


def check_slice_mir():
    case, src, spec, tir_module, grid, layout, plan, mir_module = lower_slice()
    errors = mir.verify_module(mir_module)
    check("slice-mir-verifies", not errors,
          str(errors[0]) if errors else "")
    text = mir.dump_module(mir_module)

    # exact vl + region structure: the e32m1 data region always; the
    # e64m2 address region only when an access kept its indexed form (the
    # structurally proven contiguous accesses of this kernel select the
    # unit-stride wide-access form since T011, which needs no address
    # region at all)
    vsetvlis = [op for fn in mir_module.functions for b in fn.blocks
                for op in b.ops if op.opcode == "vsetvli"]
    forms = {(op.attrs["sew"], op.attrs["lmul"]) for op in vsetvlis}
    check("vsetvli-regions-present",
          (32, 1) in forms and forms <= {(32, 1), (64, 2)},
          str(sorted(forms)))
    avls = {op.operands[0].name: op for op in vsetvlis}
    # the data region's AVL is the constant 32 (exact vl)
    data_region = [op for op in vsetvlis
                   if (op.attrs["sew"], op.attrs["lmul"]) == (32, 1)][0]
    avl_def = data_region.operands[0]
    exact = any(op.opcode == "sconst" and op.results[0].rid == avl_def.rid
                and op.attrs["value"] == 32
                for fn in mir_module.functions for b in fn.blocks
                for op in b.ops)
    check("exact-vl-is-32", exact)

    # masked memory ops with declared inactive semantics (the indexed
    # forms vloadix/vstoreix and, for proven-contiguous accesses, the
    # unit-stride forms vunit_load/vunit_store -- T011's wide-access
    # selection)
    def mem_ops(codes):
        return [op for fn in mir_module.functions for b in fn.blocks
                for op in b.ops if op.opcode in codes]
    loads = mem_ops(("vloadix", "vunit_load"))
    stores = mem_ops(("vstoreix", "vunit_store"))
    check("masked-load-declares-undef",
          loads and all(
              (op.opcode == "vloadix" and len(op.operands) == 3
               and op.attrs["default"] == "undef")
              or (op.opcode == "vunit_load" and len(op.operands) == 2
                  and op.attrs["default"] == "undef")
              for op in loads))
    check("masked-store-declares-no-access",
          stores and all(
              (op.opcode == "vstoreix" and len(op.operands) == 4
               and op.attrs["default"] == "no-access")
              or (op.opcode == "vunit_store" and len(op.operands) == 3
                  and op.attrs["default"] == "no-access")
              for op in stores))
    indexed = [op for op in loads + stores if op.opcode.endswith("ix")]
    check("memory-index-at-eew64",
          all(op.attrs["eew"] == 64 and op.operands[1].type.sew == 64
              for op in indexed))

    # whole-tree address form + independent model check
    trees = mir_module.meta["address_trees"]
    # whole-tree address records: an indexed access records its tree; a
    # kernel whose every access selected the unit-stride form records
    # none (the wide-selection entries in the module meta carry those)
    wide = mir_module.meta.get("wide_selections") or []
    check("address-trees-recorded",
          any("+ sext(vi32" in t and "* 4" in t for t in trees)
          or (not trees and wide),
          f"trees={trees} wide={len(wide)}")
    base = 0x11000
    lanes = list(range(0, 128))
    expected = [base + i * 4 for i in lanes]
    from a100c.lower.addresses import AddressTree
    tree = AddressTree(base="b", index="i", index_sew=32, esz=4)
    got = check_address_model(tree, base, lanes, expected)
    check("address-model-independent-check", got == expected)

    # the strided worker loop and the native grid evaluation
    check("worker-loop-and-grid-present",
          "prog_head" in text and "prog_next" in text
          and "sdivu" in text and "chunk_head" in text)
    # the grid tie reads the bundle scalar n_elements
    check("grid-tied-to-scalar",
          grid.ties and list(grid.ties.values()) == [("scalar", "n_elements")],
          str(grid.ties))
    check("grid-self-check-recorded",
          grid.self_check.get("modeled") == grid.self_check.get("declared")
          and grid.self_check.get("modeled") == [1],
          str(grid.self_check))
    return mir_module


def check_witness_option():
    _, _, _, _, _, _, _, mir_module = lower_slice(
        options=vectorize.LowerOptions(witness_drop_tail_predicates=True))
    # the predicate-dropped memory ops carry NO mask operand: the indexed
    # forms (vloadix 2 / vstoreix 3 operands) and the unit-stride forms
    # (vunit_load 1 / vunit_store 2 -- T011's wide-access selection)
    unmasked_widths = {"vloadix": 2, "vstoreix": 3,
                       "vunit_load": 1, "vunit_store": 2}
    loads = [op for fn in mir_module.functions for b in fn.blocks
             for op in b.ops if op.opcode in unmasked_widths]
    check("witness-drops-tail-predicates",
          loads and all(len(op.operands) == unmasked_widths[op.opcode]
                        for op in loads)
          and mir_module.meta["witness"] == "witness-drop-tail-predicates")


def check_refusals():
    case = load_case()

    def lower_with(src, spec, case, grid=None):
        layout = binding_mod.argument_layout(case, spec)
        plan = part_mod.ExecutionPlan()
        return vectorize.lower_to_mir(lower_tir.lower(src, spec), plan,
                                      DEFAULT_TARGET, layout,
                                      grid or grid_mod.extract_grid(src, case))

    # fp16 pointers: element width 16 is outside the slice (located refusal)
    src = source.load_operator(str(SLICE))
    spec16 = specialize.specialize(src, dict(case, args={
        **case["args"],
        "x_ptr": case["args"]["x_ptr"].astype("float16"),
        "out_ptr": case["args"]["out_ptr"].astype("float16")},
        pointer_dtypes={"x_ptr": "float16", "out_ptr": "float16"}))
    try:
        lower_with(src, spec16, dict(case, args={
            **case["args"],
            "x_ptr": case["args"]["x_ptr"].astype("float16"),
            "out_ptr": case["args"]["out_ptr"].astype("float16")},
            pointer_dtypes={"x_ptr": "float16", "out_ptr": "float16"}))
        check("fp16-element-refused", False, "no refusal raised")
    except vectorize.VectorizeError as exc:
        check("fp16-element-refused", "width 16" in str(exc)
              or "SEW" in str(exc), str(exc)[:90])

    # a grid the model cannot tie to a bundle-visible quantity is refused
    import pathlib
    bad = pathlib.Path(str(SLICE)).read_text()
    bad = bad.replace(
        "grid = ((n + meta['BLOCK_SIZE'] - 1) // meta['BLOCK_SIZE'],)",
        "grid = ((n + seed - 1) // meta['BLOCK_SIZE'],)")
    path = ROOT / "a100c" / "tests" / "_scratch_bad_grid.py"
    path.write_text(bad)
    try:
        bad_src = source.load_operator(str(path))
        grid_mod.extract_grid(bad_src, case)
        check("untied-grid-refused", False, "no refusal raised")
    except grid_mod.GridError as exc:
        # the refusal is located either at tracking (the classic form) or
        # at the tie stage (T011 lets integer literals ride the grid
        # expression, so an unbundle-visible leaf like a case parameter
        # refuses when its tie is attempted -- same discipline, later gate)
        check("untied-grid-refused",
              "not provenance-tracked" in str(exc)
              or "not bundle-visible" in str(exc)
              or "cannot be proven" in str(exc), str(exc)[:90])
    finally:
        path.unlink(missing_ok=True)

    # matrix-routed constructs are refused by the stub with the contract
    try:
        matrix_mod.refuse_matrix(None, "tl.dot", "probe")
        check("matrix-stub-refuses", False, "no refusal raised")
    except matrix_mod.MatrixLoweringError as exc:
        check("matrix-stub-refuses", "IME" in str(exc)
              and "LMUL=1" in str(exc), str(exc)[:80])

    # the scalar core refuses what it does not implement
    try:
        scalar_mod.refuse(None, "arith.frem", "probe")
        check("scalar-stub-refuses", False, "no refusal raised")
    except scalar_mod.ScalarLoweringError:
        check("scalar-stub-refuses", True)

    # malformed control flow is refused (T008 lowers well-formed regions;
    # a hand-built module bypassing the TIR verifier still gets a located
    # refusal from the lowering itself)
    fn = tir.Function("k", [tir.Value(tir.Type.pointer(tir.FLOAT32), (),
                                     name="p")])
    fn.body.statements.append(tir.Op.arange(0, 128))
    loop = tir.Loop(None, None, None)
    fn.body.statements.append(loop)
    module = tir.Module("k", "<probe>")
    module.functions.append(fn)
    from a100c.plan.grid import GridModel, Lit as GLit
    trivial = GridModel(axes=(GLit(1),), ties={}, ndim=1, path="<probe>")
    try:
        vectorize.SliceLowering(module, part_mod.ExecutionPlan(),
                                DEFAULT_TARGET,
                                binding_mod.ArgumentLayout([], [], [], [], "d"),
                                trivial).lower()
        check("control-flow-refused", False, "no refusal raised")
    except vectorize.VectorizeError as exc:
        check("control-flow-refused", "control flow" in str(exc), str(exc)[:80])


def check_grid_view_extent_tie():
    """The view-extent tie mechanism: a hand-built model reading a view shape
    lowers to a load of view.shape[axis] from the bundle."""
    from a100c.plan.grid import Bin, Lit, Ref
    model = grid_mod.GridModel(
        axes=(Bin("floordiv", Ref("view_extent", ("out_ptr", 0)), Lit(128)),),
        ties={("out_ptr", 0): ("view_extent", "out_ptr", 0)},
        ndim=1, path="<probe>")
    case = load_case()
    src = source.load_operator(str(SLICE))
    spec = specialize.specialize(src, case)
    layout = binding_mod.argument_layout(case, spec)
    tir_module = lower_tir.lower(src, spec)
    plan = part_mod.ExecutionPlan()
    try:
        mir_module = vectorize.lower_to_mir(tir_module, plan, DEFAULT_TARGET,
                                            layout, model)
        text = mir.dump_module(mir_module)
        # the grid reads view.shape[0]: a load at view offset +8 (the shape
        # pointer) then +0 (axis 0)
        check("view-extent-tie-lowers-to-shape-load",
              "vshape" in text and "vext" in text, text[:0])
    except vectorize.VectorizeError as exc:
        check("view-extent-tie-lowers-to-shape-load", False, str(exc)[:100])


def main() -> int:
    check_slice_mir()
    check_witness_option()
    check_refusals()
    check_grid_view_extent_tie()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_lower_vector: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
