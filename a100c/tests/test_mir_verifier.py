#!/usr/bin/env python3
"""test_mir_verifier.py -- the MIR verifier (T007, acceptance[4]).

Rejects one hand-built malformed module per invariant class:

  - vsetvli-region inconsistency (a vector op whose width does not match
    the active region);
  - masked store without inactive semantics (and masked load without a
    declared default);
  - use before definition (dominance violation);
  - the structural classes: type mismatch, block structure, the v0
    working-mask constraint, unknown op.

And accepts the lowering's real output for the slice operator
(IR-WELLFORMED: the rejection path and the acceptance path are both
exercised -- a verifier that only ever rejects proves nothing).
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


def probe_module():
    fn = mir.MFunction("probe", [])
    entry = mir.Block("entry")
    fn.blocks.append(entry)
    module = mir.MModule("probe", "<probe>")
    module.functions.append(fn)
    return module, entry


def rejects(invariant: str, build) -> bool:
    module, entry = probe_module()
    build(entry)
    errors = mir.verify_module(module)
    got = [e for e in errors if e.invariant == invariant]
    other = [e for e in errors if e.invariant != invariant]
    return bool(got), str(got[0])[:90] if got else (f"other={other[:1]}")


def check_region_inconsistency():
    def build(entry):
        avl = mir.VReg(mir.I32, name="avl")
        entry.ops.append(mir.MOp("sconst", [], [avl], attrs={"value": 32}))
        entry.ops.append(mir.MOp("vsetvli", [avl],
                                 [mir.VReg(mir.I32, name="vl")],
                                 attrs={"sew": 32, "lmul": 1,
                                        "policy": "ta,ma"}))
        a = mir.VReg(mir.VectorType(64, 1, "int"), name="wide")   # e64 in e32
        b = mir.VReg(mir.VectorType(64, 1, "int"), name="wide2")
        entry.ops.append(mir.MOp("vbin", [a, b],
                                 [mir.VReg(mir.VectorType(64, 1, "int"),
                                           name="wout")],
                                 attrs={"op": "add"}))
        entry.ops.append(mir.MOp("ret", [], []))
    ok, detail = rejects(mir.Invariant.VSETVLI_REGION_INCONSISTENCY, build)
    check("rejects-vsetvli-region-inconsistency", ok, detail)


def check_region_missing():
    def build(entry):
        a = mir.VReg(mir.VectorType(32, 1, "int"), name="a")
        b = mir.VReg(mir.VectorType(32, 1, "int"), name="b")
        entry.ops.append(mir.MOp("vbin", [a, b],
                                 [mir.VReg(mir.VectorType(32, 1, "int"),
                                           name="c")],
                                 attrs={"op": "add"}))
        entry.ops.append(mir.MOp("ret", [], []))
    ok, detail = rejects(mir.Invariant.VSETVLI_REGION_INCONSISTENCY, build)
    check("rejects-vector-op-outside-any-region", ok, detail)


def check_masked_store_without_semantics():
    def build(entry):
        avl = mir.VReg(mir.I32, name="avl")
        entry.ops.append(mir.MOp("sconst", [], [avl], attrs={"value": 32}))
        entry.ops.append(mir.MOp("vsetvli", [avl],
                                 [mir.VReg(mir.I32, name="vl")],
                                 attrs={"sew": 32, "lmul": 1,
                                        "policy": "ta,ma"}))
        base = mir.VReg(mir.I64, name="base")
        idx = mir.VReg(mir.VectorType(64, 2, "int"), name="idx")
        val = mir.VReg(mir.VectorType(32, 1, "int"), name="val")
        v0 = mir.VReg(mir.MaskType(), name="v0", fixed_phys="v0")
        entry.ops.append(mir.MOp(
            "vstoreix", [base, idx, val, v0], [],
            attrs={"eew": 64, "sew": 32}))       # no default attr
        entry.ops.append(mir.MOp("ret", [], []))
    ok, detail = rejects(mir.Invariant.MASKED_WITHOUT_INACTIVE_SEMANTICS, build)
    check("rejects-masked-store-without-inactive-semantics", ok, detail)


def check_masked_store_wrong_semantics():
    def build(entry):
        avl = mir.VReg(mir.I32, name="avl")
        entry.ops.append(mir.MOp("sconst", [], [avl], attrs={"value": 32}))
        entry.ops.append(mir.MOp("vsetvli", [avl],
                                 [mir.VReg(mir.I32, name="vl")],
                                 attrs={"sew": 32, "lmul": 1,
                                        "policy": "ta,ma"}))
        base = mir.VReg(mir.I64, name="base")
        idx = mir.VReg(mir.VectorType(64, 2, "int"), name="idx")
        val = mir.VReg(mir.VectorType(32, 1, "int"), name="val")
        v0 = mir.VReg(mir.MaskType(), name="v0", fixed_phys="v0")
        entry.ops.append(mir.MOp(
            "vstoreix", [base, idx, val, v0], [],
            attrs={"eew": 64, "sew": 32, "default": "undef"}))
        entry.ops.append(mir.MOp("ret", [], []))
    ok, detail = rejects(mir.Invariant.MASKED_WITHOUT_INACTIVE_SEMANTICS, build)
    check("rejects-masked-store-declaring-undef", ok, detail)


def check_masked_load_without_semantics():
    def build(entry):
        avl = mir.VReg(mir.I32, name="avl")
        entry.ops.append(mir.MOp("sconst", [], [avl], attrs={"value": 32}))
        entry.ops.append(mir.MOp("vsetvli", [avl],
                                 [mir.VReg(mir.I32, name="vl")],
                                 attrs={"sew": 32, "lmul": 1,
                                        "policy": "ta,ma"}))
        base = mir.VReg(mir.I64, name="base")
        idx = mir.VReg(mir.VectorType(64, 2, "int"), name="idx")
        v0 = mir.VReg(mir.MaskType(), name="v0", fixed_phys="v0")
        entry.ops.append(mir.MOp(
            "vloadix", [base, idx, v0],
            [mir.VReg(mir.VectorType(32, 1, "int"), name="out")],
            attrs={"eew": 64, "sew": 32}))       # no default attr
        entry.ops.append(mir.MOp("ret", [], []))
    ok, detail = rejects(mir.Invariant.MASKED_WITHOUT_INACTIVE_SEMANTICS, build)
    check("rejects-masked-load-without-declared-default", ok, detail)


def check_use_before_definition():
    def build(entry):
        later = mir.VReg(mir.I64, name="later")
        a = mir.VReg(mir.I64, name="a")
        b = mir.VReg(mir.I64, name="b")
        entry.ops.append(mir.MOp("sadd", [a, later], [b]))   # later not defined
        entry.ops.append(mir.MOp("sconst", [], [later], attrs={"value": 1}))
        entry.ops.append(mir.MOp("ret", [], []))
    ok, detail = rejects(mir.Invariant.USE_BEFORE_DEFINITION, build)
    check("rejects-use-before-definition", ok, detail)


def check_cross_block_use_before_definition():
    module = mir.MModule("probe", "<probe>")
    fn = mir.MFunction("probe", [])
    entry = mir.Block("entry")
    other = mir.Block("other")
    fn.blocks += [entry, other]
    module.functions.append(fn)
    a = mir.VReg(mir.I64, name="a")
    b = mir.VReg(mir.I64, name="b")
    c = mir.VReg(mir.I64, name="c")
    entry.ops.append(mir.MOp("sconst", [], [a], attrs={"value": 1}))
    entry.ops.append(mir.MOp("br", [], [],
                             attrs={"target": "other", "args": []}))
    other.ops.append(mir.MOp("sadd", [a, b], [c]))   # b never defined
    other.ops.append(mir.MOp("ret", [], []))
    errors = mir.verify_module(module)
    got = [e for e in errors if e.invariant == mir.Invariant.USE_BEFORE_DEFINITION]
    check("rejects-cross-block-use-before-definition", bool(got),
          str(got[0])[:90] if got else str(errors[:1]))


def check_v0_constraint():
    def build(entry):
        avl = mir.VReg(mir.I32, name="avl")
        entry.ops.append(mir.MOp("sconst", [], [avl], attrs={"value": 32}))
        entry.ops.append(mir.MOp("vsetvli", [avl],
                                 [mir.VReg(mir.I32, name="vl")],
                                 attrs={"sew": 32, "lmul": 1,
                                        "policy": "ta,ma"}))
        a = mir.VReg(mir.VectorType(32, 1, "int"), name="a")
        b = mir.VReg(mir.VectorType(32, 1, "int"), name="b")
        entry.ops.append(mir.MOp("vid", [], [a]))
        entry.ops.append(mir.MOp("vid", [], [b]))
        loose = mir.VReg(mir.MaskType(), name="loose")    # NOT fixed to v0
        entry.ops.append(mir.MOp("vcmp", [a, b], [loose],
                                 attrs={"pred": "lt", "fp": False}))
        entry.ops.append(mir.MOp("vsel", [loose, a, b],
                                 [mir.VReg(mir.VectorType(32, 1, "int"),
                                           name="out")]))
        entry.ops.append(mir.MOp("ret", [], []))
    ok, detail = rejects(mir.Invariant.V0_MASK_CONSTRAINT, build)
    check("rejects-vsel-mask-not-in-v0", ok, detail)


def check_block_structure():
    module = mir.MModule("probe", "<probe>")
    fn = mir.MFunction("probe", [])
    entry = mir.Block("entry")
    fn.blocks.append(entry)
    module.functions.append(fn)
    entry.ops.append(mir.MOp("sconst", [],
                             [mir.VReg(mir.I64, name="a")],
                             attrs={"value": 1}))      # no terminator
    errors = mir.verify_module(module)
    check("rejects-missing-terminator",
          any(e.invariant == mir.Invariant.BLOCK_STRUCTURE for e in errors))
    # a branch to an unknown block
    entry.ops.append(mir.MOp("br", [], [],
                             attrs={"target": "nowhere", "args": []}))
    errors = mir.verify_module(module)
    check("rejects-branch-to-unknown-block",
          any("nowhere" in str(e) for e in errors))
    # wrong branch-arg arity
    other = mir.Block("other", [mir.VReg(mir.I64, name="p")])
    fn.blocks.append(other)
    other.ops.append(mir.MOp("ret", [], []))
    entry.ops[-1] = mir.MOp("br", [], [],
                            attrs={"target": "other", "args": []})
    errors = mir.verify_module(module)
    check("rejects-branch-arg-arity",
          any(e.invariant == mir.Invariant.BLOCK_STRUCTURE for e in errors))


def check_type_mismatch_and_unknown():
    def build(entry):
        a = mir.VReg(mir.I64, name="a")
        b = mir.VReg(mir.I32, name="b")
        entry.ops.append(mir.MOp("sconst", [], [a], attrs={"value": 1}))
        entry.ops.append(mir.MOp("sconst", [], [b], attrs={"value": 1}))
        entry.ops.append(mir.MOp("sadd", [a, b],
                                 [mir.VReg(mir.I64, name="c")]))
        entry.ops.append(mir.MOp("zzz", [], []))
        entry.ops.append(mir.MOp("ret", [], []))
    module, entry = probe_module()
    build(entry)
    errors = mir.verify_module(module)
    check("rejects-type-mismatch",
          any(e.invariant == mir.Invariant.TYPE_MISMATCH for e in errors))
    check("rejects-unknown-opcode",
          any(e.invariant == mir.Invariant.UNKNOWN_OP for e in errors))


def check_accepts_real_lowering():
    case = load_case()
    src = source.load_operator(str(SLICE))
    spec = specialize.specialize(src, case)
    tir_module = lower_tir.lower(src, spec)
    grid = grid_mod.extract_grid(src, case)
    layout = binding_mod.argument_layout(case, spec)
    module = vectorize.lower_to_mir(tir_module, part_mod.ExecutionPlan(),
                                    DEFAULT_TARGET, layout, grid)
    errors = mir.verify_module(module)
    check("accepts-the-lowerings-real-output", not errors,
          str(errors[0]) if errors else "")
    # and after legalisation (the post-legalize form also verifies)
    from a100c.backend import legalize
    legalize.legalize(module)
    errors = mir.verify_module(module)
    check("accepts-the-legalized-output", not errors,
          str(errors[0]) if errors else "")


MIXED_SEW_BODY = """
    i = tl.arange(0, BLOCK)
    m = i < n
    x = tl.load(x_ptr + i, mask=m, other=0.0).to(tl.float32)
    s = tl.sum(x, axis=0)
    tl.store(o_ptr, s / n)"""


def check_accepts_mixed_sew_lowering():
    """T028 acceptance[2]: the mixed-SEW lowering (fp16 data loaded in an
    e16 pass, converted to fp32 and reduced at e32 -- the multi-width
    reduce lane) verifies; the hand-built rejection control above still
    rejects inconsistent regions."""
    import textwrap
    import tempfile
    text = (
        '"""probe"""\n'
        'OPERATOR = {"name": "probe/mixedsew", "group": "probe", '
        '"channel": "local",\n'
        '            "execution": "triton_kernel", "verification": '
        '"correctness", "tags": []}\n'
        'import numpy as np\n'
        'import triton\n'
        'import triton.language as tl\n'
        '@triton.jit\n'
        'def mixedsew_kernel(x_ptr, o_ptr, n, BLOCK: tl.constexpr):\n'
        + textwrap.indent(textwrap.dedent(MIXED_SEW_BODY).strip("\n"),
                          "    ")
        + '\n\n'
        'def ref(args, meta):\n'
        '    import numpy as np\n'
        '    x = np.asarray(args["x_ptr"], np.float32)\n'
        '    return {"o_ptr": np.array([x.sum() / args["n"]], np.float32)}\n'
        '\n'
        'def _make_case(shape=(17,), dtype="float16", seed=0):\n'
        '    import numpy as np\n'
        '    rng = np.random.default_rng(seed)\n'
        '    x = rng.uniform(-2.0, 2.0, (17,)).astype(np.float16)\n'
        '    args = {"x_ptr": x, "o_ptr": np.zeros(4, np.float16),'
        ' "n": 17}\n'
        '    meta = {"BLOCK": 128}\n'
        '    expected = ref(args, meta)\n'
        '    return {"args": args, "meta": meta, "grid": (1,),'
        ' "shape": shape,\n'
        '            "kernel": mixedsew_kernel, "outputs": ("o_ptr",),\n'
        '            "expected": expected,\n'
        '            "comparison": {"o_ptr": {"comparator": "allclose",'
        ' "exact": False,\n'
        '                                    "rtol": 1e-2, "atol": 1e-2}}}\n'
    )
    d = tempfile.mkdtemp(prefix="a100c-mir-mixedsew-")
    p = Path(d) / "mixedsew.py"
    p.write_text(text)
    spec = importlib.util.spec_from_file_location("mixedsew", str(p))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    case = module._make_case()
    src = source.load_operator(str(p))
    specz = specialize.specialize(src, case)
    tir_module = lower_tir.lower(src, specz)
    grid = grid_mod.extract_grid(src, case)
    layout = binding_mod.argument_layout(case, specz)
    from a100c.passes import pipeline as passes_mod
    passes_mod.run(tir_module, passes_mod.PassConfig())
    mir_module = vectorize.lower_to_mir(tir_module, part_mod.ExecutionPlan(),
                                        DEFAULT_TARGET, layout, grid)
    errors = mir.verify_module(mir_module)
    sews = {op.attrs["sew"] for fn in mir_module.functions
            for b in fn.blocks for op in b.ops if op.opcode == "vsetvli"}
    check("accepts-the-mixed-sew-lowering", not errors,
          f"{str(errors[0])[:90] if errors else ''} "
          f"(sews seen: {sorted(sews)})")
    check("mixed-sew-lowering-mixes-regions", 16 in sews and 32 in sews,
          f"sews seen: {sorted(sews)}")


def main() -> int:
    check_region_inconsistency()
    check_region_missing()
    check_masked_store_without_semantics()
    check_masked_store_wrong_semantics()
    check_masked_load_without_semantics()
    check_use_before_definition()
    check_cross_block_use_before_definition()
    check_v0_constraint()
    check_block_structure()
    check_type_mismatch_and_unknown()
    check_accepts_real_lowering()
    check_accepts_mixed_sew_lowering()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_mir_verifier: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
