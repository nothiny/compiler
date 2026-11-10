#!/usr/bin/env python3
"""test_lower_matrix.py -- the IME matrix lowering (T010): plan, MIR,
verification, selection, allocation, refusals.

The vertical slice's matrix lane lowers a planned dot kernel to a complete
MIR program through the real backend interfaces:

  * the tile plan (a100c/plan/tiles.py): the IME families as data (INT8
    8x16x8 -> INT32, FP16 8x8x8 -> FP32, F030), the signedness variants
    (none/u/us/su, F031), the slot mapping (vs1 = A row-major, vs2 = B
    column-major, F031), the staging layout and the declared refusals
    (int4/sparse/scale/fp8/mixed/out-dtype narrowing, F037);
  * the MIR extension (a100c/lower/matrix.py): the tile and unit-stride
    memory opcodes, the IME-aware MIR verification (family formats, LMUL=1
    regions, even vd where MUL_C=2, destination/source group overlap, v0
    masks -- F033/F040/F041), the repertoire rows registered as data, and
    the lowering's real output accepted (IR-WELLFORMED);
  * the allocator: an over-constrained function must yield a legal
    allocation (even m2 groups, no destination/source overlap) or a
    diagnosed refusal (acceptance[2]);
  * the constructed illegal forms: LMUL not 1, odd vd, group overlap,
    operand format inconsistent with the family -- each rejected with its
    invariant class (acceptance[2]);
  * the source-level int4 dot refusal (acceptance[3]) and the kept
    refuse_matrix contract the elementwise lane calls.

Execution and instruction-count evidence live in test_ime_evidence.py.

Run: python3 a100c/tests/test_lower_matrix.py   (exit 0 = all checks PASS)
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


from a100c.backend import allocate as alloc_mod  # noqa: E402
from a100c.backend import legalize as legal_mod  # noqa: E402
from a100c.backend import select as select_mod  # noqa: E402
from a100c.backend.repertoire import DEFAULT_REPERTOIRE  # noqa: E402
from a100c.ir import mir  # noqa: E402
from a100c.lower import matrix as matrix_mod  # noqa: E402
from a100c.plan import tiles as tiles_mod  # noqa: E402
from a100c.target import DEFAULT_TARGET  # noqa: E402

BINDING = matrix_mod.dot_binding(["a_ptr", "b_ptr", "c_ptr"])


def lower(ad, bd, od, acc="zero", witness=False):
    plan = tiles_mod.plan_dot(tiles_mod.DotDescription(
        a_dtype=ad, b_dtype=bd, out_dtype=od, acc_mode=acc))
    opts = matrix_mod.MatrixOptions(witness_drop_tile_padding=witness)
    return plan, matrix_mod.lower_dot(plan, BINDING, DEFAULT_TARGET, opts)


def check_plan_families():
    i8 = tiles_mod.FAMILIES["i8"]
    fp16 = tiles_mod.FAMILIES["fp16"]
    check("i8-family-tile-8x16x8",
          (i8.tile_m, i8.tile_n, i8.tile_k) == (8, 8, 16)
          and i8.acc_sew == 32 and i8.mul_c == 2 and i8.lambda_ == 4,
          f"{(i8.tile_m, i8.tile_n, i8.tile_k)} acc={i8.acc_sew} "
          f"mul_c={i8.mul_c} lambda={i8.lambda_}")
    check("fp16-family-tile-8x8x8",
          (fp16.tile_m, fp16.tile_n, fp16.tile_k) == (8, 8, 8)
          and fp16.acc_sew == 32 and fp16.mul_c == 2,
          f"{(fp16.tile_m, fp16.tile_n, fp16.tile_k)} acc={fp16.acc_sew}")
    variants = {(True, True): "smt.vmadot", (False, False): "smt.vmadotu",
                (False, True): "smt.vmadotus", (True, False): "smt.vmadotsu"}
    for (a_s, b_s), want in variants.items():
        got = i8.mnemonic_for(a_s, b_s)
        check(f"i8-signedness-variant-{want.split('.')[-1]}", got == want,
              got)
    plan = lower("int8", "int8", "int32")[0]
    check("int8-plan-mnemonic-suffix-empty", plan.mnemonic == "smt.vmadot",
          plan.mnemonic)
    plan_u = lower("uint8", "uint8", "int32")[0]
    check("uint8-plan-mnemonic-u", plan_u.mnemonic == "smt.vmadotu",
          plan_u.mnemonic)
    plan_us = lower("uint8", "int8", "int32")[0]
    check("uint8-x-int8-plan-mnemonic-us", plan_us.mnemonic == "smt.vmadotus",
          plan_us.mnemonic)
    plan_su = lower("int8", "uint8", "int32")[0]
    check("int8-x-uint8-plan-mnemonic-su", plan_su.mnemonic == "smt.vmadotsu",
          plan_su.mnemonic)
    plan_f = lower("float16", "float16", "float32")[0]
    check("fp16-plan-mnemonic-vfwmadot", plan_f.mnemonic == "smt.vfwmadot",
          plan_f.mnemonic)
    # the slot mapping is recorded with the plan (F031)
    check("slot-map-vs1-a-row-major",
          "row-major" in plan.slot_map["vs1"], str(plan.slot_map["vs1"]))
    check("slot-map-vs2-b-column-major",
          "column-major" in plan.slot_map["vs2"], str(plan.slot_map["vs2"]))
    check("slot-map-vd-mul-c-2-group",
          "MUL_C=2" in plan.slot_map["vd"], str(plan.slot_map["vd"]))
    # the pure models the execution test predicts counts with
    check("tile-grid-model", tiles_mod.tile_grid(24, 20) == (3, 3)
          and tiles_mod.tile_grid(9, 13) == (2, 2)
          and tiles_mod.tile_grid(1, 1) == (1, 1))
    check("k-steps-model", tiles_mod.k_steps(32, 16) == 2
          and tiles_mod.k_steps(17, 16) == 2 and tiles_mod.k_steps(8, 8) == 1)
    check("expected-tile-ops-24x20x32",
          tiles_mod.expected_tile_ops(24, 20, 32, plan) == 18,
          str(tiles_mod.expected_tile_ops(24, 20, 32, plan)))


def check_plan_refusals():
    # int4 is outside the declared surface (acceptance[3])
    try:
        tiles_mod.plan_dot(tiles_mod.DotDescription(
            a_dtype="int4", b_dtype="int4", out_dtype="int32"))
        check("int4-dot-refused", False, "no refusal raised")
    except tiles_mod.TilePlanError as exc:
        check("int4-dot-refused",
              "outside the declared surface" in str(exc)
              and "F037" in str(exc), str(exc)[:90])
    for ad, name in ((("float8e4nv"), "fp8"), (("int16"), "int16"),
                     (("float32"), "fp32-ieee")):
        try:
            tiles_mod.plan_dot(tiles_mod.DotDescription(
                a_dtype=ad, b_dtype=ad, out_dtype="int32"))
            check(f"{name}-dot-refused", False, "no refusal raised")
        except tiles_mod.TilePlanError as exc:
            check(f"{name}-dot-refused", True, str(exc)[:70])
    try:
        tiles_mod.plan_dot(tiles_mod.DotDescription(
            a_dtype="float16", b_dtype="bfloat16", out_dtype="float32"))
        check("mixed-fp16-bf16-refused", False, "no refusal raised")
    except tiles_mod.TilePlanError as exc:
        check("mixed-fp16-bf16-refused", "mixed" in str(exc), str(exc)[:70])
    try:
        tiles_mod.plan_dot(tiles_mod.DotDescription(
            a_dtype="int8", b_dtype="int8", out_dtype="float32"))
        check("out-dtype-narrow-refused", False, "no refusal raised")
    except tiles_mod.TilePlanError as exc:
        check("out-dtype-narrow-refused", "out_dtype" in str(exc),
              str(exc)[:70])
    # BF16 plans the vector path and carries the recorded gap (F010/F034)
    plan = lower("bfloat16", "bfloat16", "float32")[0]
    check("bf16-plans-vector-fp32-path", plan.path == "vector-fp32",
          plan.path)
    check("bf16-gap-recorded",
          plan.bf16_gap is not None and "F010" in plan.bf16_gap
          and "not claimable" in plan.bf16_gap,
          (plan.bf16_gap or "")[:80])


def check_lowering_and_verify():
    for ad, acc in (("int8", "zero"), ("int8", "read_c"),
                    ("uint8", "zero"), ("float16", "zero"),
                    ("float16", "read_c"), ("bfloat16", "zero"),
                    ("bfloat16", "read_c")):
        od = "int32" if ad in ("int8", "uint8") else "float32"
        plan, mod = lower(ad, ad, od, acc)
        errs = matrix_mod.verify_module(mod)
        check(f"{ad}-{acc}-lowering-verifies", not errs,
              str(errs[:1]) if errs else
              f"{sum(len(b.ops) for b in mod.functions[0].blocks)} ops")
    # the generic verifier alone reports the IME opcodes as unknown: the
    # composed verification is the contract (documented boundary)
    plan, mod = lower("int8", "int8", "int32")
    generic = mir.verify_module(mod)
    unknown = [e for e in generic
               if e.invariant == mir.Invariant.UNKNOWN_OP
               and any(e.message == f"unknown MIR opcode '{op}'"
                       for op in matrix_mod.IME_OPCODES)]
    other = [e for e in generic if e not in unknown]
    check("generic-verifier-flags-ime-opcodes-only",
          len(unknown) > 0 and not other,
          f"{len(unknown)} ime UNKNOWN_OP, {len(other)} other")
    # structure: the tile op, the k loop with the accumulator as a block
    # parameter, staging stores, masked strided C stores, the strided tile
    # loop, and the stats store
    text = mir.dump_module(mod)
    check("mir-has-tile-op", "vmdot" in text)
    khead = mod.functions[0].block("k_head")
    check("k-loop-carries-m2-accumulator",
          len(khead.params) == 2 and khead.params[1].type ==
          mir.VectorType(32, 2, "int"),
          str([str(p.type) for p in khead.params]))
    check("mir-has-staging-stores", "vustore8" in text)
    check("mir-has-masked-strided-c-stores",
          text.count("vstoreix") >= 8 and "no-access" in text)
    thead = mod.functions[0].block("tile_head")
    check("tile-loop-is-worker-strided", len(thead.params) == 1,
          "the tile id is the only carried scalar")
    check("mir-dump-carries-source-attribution", "ime-slice" in text)
    # the witness build records itself and drops the staging masks
    _, wmod = lower("int8", "int8", "int32", witness=True)
    wtext = mir.dump_module(wmod)
    stage_blocks = {b.name for b in wmod.functions[0].blocks
                    if b.name in ("a_vec", "b_vec")}
    wloads = [op for b in wmod.functions[0].blocks if b.name in stage_blocks
              for op in b.ops if op.opcode in ("vuload8", "vuload16")]
    nloads = [op for b in wmod.functions[0].blocks if b.name in stage_blocks
              for op in b.ops if op.opcode in ("vuload8m", "vuload16m")]
    check("witness-drops-staging-masks",
          len(wloads) == 16 and len(nloads) == 0,
          f"{len(wloads)} unmasked staging loads, {len(nloads)} masked")
    check("witness-recorded-in-meta",
          wmod.meta["ime"]["witness"] == "witness-drop-tile-padding")


def check_ime_illegal_forms():
    """acceptance[2]: constructed illegal IME forms are rejected."""
    def tile_op(opcode, acc, a, b, out, **kw):
        return mir.MOp(opcode, [acc, a, b], [out], loc="probe", **kw)

    def build(op, params=()):
        fn = mir.MFunction("f", list(params))
        entry = mir.Block("entry")
        fn.blocks.append(entry)
        mod = mir.MModule("probe", "<probe>")
        mod.functions.append(fn)
        entry.ops.append(op)
        entry.ops.append(mir.MOp("ret", [], [], loc="probe"))
        return mod

    acc_ty = mir.VectorType(32, 2, "int")
    a_ty = mir.VectorType(8, 1, "int")
    b_ty = mir.VectorType(8, 1, "int")

    def fresh():
        # the operands are function parameters (always defined); the tile
        # op's result is the only definition under test
        return (mir.VReg(acc_ty, name="acc"), mir.VReg(a_ty, name="a"),
                mir.VReg(b_ty, name="b"), mir.VReg(acc_ty, name="out"))

    def region(mod, sew, lmul, vl=None):
        target = DEFAULT_TARGET
        vl = vl if vl is not None else target.vlmax(sew, lmul)
        avl = mir.VReg(mir.I32, name="avl")
        mod.functions[0].blocks[0].ops.insert(0, mir.MOp(
            "vsetvli", [avl], [mir.VReg(mir.I32, name="vl")],
            attrs={"sew": sew, "lmul": lmul, "policy": "ta,ma"},
            loc="probe"))
        mod.functions[0].blocks[0].ops.insert(0, mir.MOp(
            "sconst", [], [avl], attrs={"value": vl}, loc="probe"))

    # LMUL not 1: the tile op executes in an m2 region
    acc, a, b, out = fresh()
    mod = build(tile_op("vmdot", acc, a, b, out),
                    (acc, a, b))
    region(mod, 8, 2)
    errs = matrix_mod.verify_module(mod)
    check("illegal-lmul-not-1-rejected",
          len(errs) == 1 and errs[0].invariant ==
          matrix_mod.IMEInvariant.IME_LMUL, str(errs[:1]))
    # odd vd where MUL_C=2
    acc, a, b, out = fresh()
    out.fixed_phys = "v3"
    mod = build(tile_op("vmdot", acc, a, b, out),
                    (acc, a, b))
    region(mod, 8, 1)
    errs = matrix_mod.verify_module(mod)
    check("illegal-odd-vd-rejected",
          len(errs) == 1 and errs[0].invariant ==
          matrix_mod.IMEInvariant.IME_PARITY, str(errs[:1]))
    # destination group overlapping vs1
    acc, a, b, out = fresh()
    acc.fixed_phys = "v4"
    out.fixed_phys = "v4"
    a.fixed_phys = "v5"
    mod = build(tile_op("vmdot", acc, a, b, out),
                    (acc, a, b))
    region(mod, 8, 1)
    errs = matrix_mod.verify_module(mod)
    check("illegal-destination-overlap-rejected",
          len(errs) == 1 and errs[0].invariant ==
          matrix_mod.IMEInvariant.IME_OVERLAP, str(errs[:1]))
    # operand format inconsistent with the family: float tiles on the
    # integer family, and integer tiles on the floating family
    acc, a, b, out = fresh()
    af = mir.VReg(mir.VectorType(16, 1, "float"), name="af")
    bf = mir.VReg(mir.VectorType(16, 1, "float"), name="bf")
    mod = build(tile_op("vmdot", acc, af, bf, out), (acc, af, bf))
    region(mod, 8, 1)
    errs = matrix_mod.verify_module(mod)
    check("illegal-family-format-rejected",
          len(errs) == 1 and errs[0].invariant ==
          matrix_mod.IMEInvariant.IME_FORMAT, str(errs[:1]))
    accf = mir.VReg(mir.VectorType(32, 2, "float"), name="accf")
    outf = mir.VReg(mir.VectorType(32, 2, "float"), name="outf")
    ai = mir.VReg(mir.VectorType(8, 1, "int"), name="ai")
    bi = mir.VReg(mir.VectorType(8, 1, "int"), name="bi")
    mod = build(tile_op("vfwmadot", accf, ai, bi, outf), (accf, ai, bi))
    region(mod, 16, 1)
    errs = matrix_mod.verify_module(mod)
    check("illegal-vfwmadot-int-tiles-rejected",
          len(errs) == 1 and errs[0].invariant ==
          matrix_mod.IMEInvariant.IME_FORMAT, str(errs[:1]))
    # the signedness variants type-check against their operand kinds
    for opcode, ka, kb in (("vmdot", "int", "int"), ("vmdotu", "uint", "uint"),
                           ("vmdotus", "uint", "int"),
                           ("vmdotsu", "int", "uint")):
        acc, a, b, out = fresh()
        av = mir.VReg(mir.VectorType(8, 1, ka), name="a")
        bv = mir.VReg(mir.VectorType(8, 1, kb), name="b")
        mod = build(tile_op(opcode, acc, av, bv, out), (acc, av, bv))
        region(mod, 8, 1)
        errs = matrix_mod.verify_module(mod)
        check(f"{opcode}-legal-form-verifies", not errs,
              str(errs[:1]) if errs else "")
    # a masked unit-stride load whose mask is not the fixed v0 value
    base = mir.VReg(mir.I64, name="base")
    mask = mir.VReg(mir.MaskType(), name="m")
    mod = build(mir.MOp("vuload8m", [base, mask],
                        [mir.VReg(mir.VectorType(8, 1, "int"), name="v")],
                        loc="probe"), (base, mask))
    region(mod, 8, 1)
    errs = matrix_mod.verify_module(mod)
    check("illegal-mask-not-v0-rejected",
          len(errs) == 1 and errs[0].invariant ==
          matrix_mod.IMEInvariant.IME_MASK, str(errs[:1]))


def _tile_chain_module(n_acc: int):
    """A function with n_acc simultaneously live m2 accumulators chained
    through tile ops (all live at the final stores): the register-pressure
    construct for the allocator checks."""
    fn = mir.MFunction(f"over{n_acc}", [])
    entry = mir.Block("entry")
    fn.blocks.append(entry)
    mod = mir.MModule(f"over{n_acc}", "<probe>")
    mod.functions.append(fn)
    avl = mir.VReg(mir.I32, name="avl")
    entry.ops.append(mir.MOp("sconst", [], [avl],
                             attrs={"value": 64}, loc="probe"))
    entry.ops.append(mir.MOp("vsetvli", [avl],
                             [mir.VReg(mir.I32, name="vl")],
                             attrs={"sew": 32, "lmul": 2, "policy": "ta,ma"},
                             loc="probe"))
    a = mir.VReg(mir.VectorType(8, 1, "int"), name="ta")
    b = mir.VReg(mir.VectorType(8, 1, "int"), name="tb")
    base = mir.VReg(mir.I64, name="base")
    # entry-block parameters (the form the allocator colors; function
    # parameters alone are not in its value set)
    entry.params.extend([a, b, base])
    zero = mir.VReg(mir.I32, name="z")
    entry.ops.append(mir.MOp("sconst", [], [zero],
                             attrs={"value": 0}, loc="probe"))
    prev = mir.VReg(mir.VectorType(32, 2, "int"), name="acc0")
    entry.ops.append(mir.MOp("s2v", [zero], [prev], loc="probe"))
    # the tile chain runs at e8m1 (the ISA's LMUL=1 requirement)
    avl8 = mir.VReg(mir.I32, name="avl8")
    entry.ops.append(mir.MOp("sconst", [], [avl8],
                             attrs={"value": 128}, loc="probe"))
    entry.ops.append(mir.MOp("vsetvli", [avl8],
                             [mir.VReg(mir.I32, name="vl8")],
                             attrs={"sew": 8, "lmul": 1, "policy": "ta,ma"},
                             loc="probe"))
    accs = [prev]
    for i in range(n_acc - 1):
        nxt = mir.VReg(mir.VectorType(32, 2, "int"), name=f"acc{i+1}")
        entry.ops.append(mir.MOp("vmdot", [prev, a, b], [nxt], loc="probe"))
        accs.append(nxt)
        prev = nxt
    # the stores return to the accumulator's (32,2) region
    avl2 = mir.VReg(mir.I32, name="avl2")
    entry.ops.append(mir.MOp("sconst", [], [avl2],
                             attrs={"value": 64}, loc="probe"))
    entry.ops.append(mir.MOp("vsetvli", [avl2],
                             [mir.VReg(mir.I32, name="vl2")],
                             attrs={"sew": 32, "lmul": 2, "policy": "ta,ma"},
                             loc="probe"))
    # every accumulator is used at the end (all live simultaneously)
    for acc in accs:
        entry.ops.append(mir.MOp("vustore32", [base, acc], [], loc="probe"))
    entry.ops.append(mir.MOp("ret", [], [], loc="probe"))
    return mod, accs, a, b


def check_allocator():
    """acceptance[2]: the allocator honors parity/group constraints.

    A pressured function (12 simultaneously live m2 accumulators + the two
    m1 tiles: 26 of the 31 allocatable vector registers) must allocate
    legally: every m2 base even-numbered (MUL_C=2 parity) and no
    destination group overlapping a source tile.  An over-constrained
    function (16 groups + tiles: 34 > 31) must yield a legal allocation or
    a diagnosed refusal -- never a silent violation.
    """
    # the pressured-but-fitting case: a legal allocation whose parity and
    # group disjointness are asserted on the assignment itself
    mod, accs, a, b = _tile_chain_module(12)
    errs = matrix_mod.verify_module(mod)
    check("pressured-module-verifies", not errs,
          str(errs[:1]) if errs else "")
    try:
        alloc = alloc_mod.allocate(mod, DEFAULT_TARGET)
        bases = {alloc.assignment[r.rid] for r in accs}
        even = all(int(n[1:]) % 2 == 0 for n in bases if n.startswith("v"))
        groups = {f"v{int(alloc.assignment[r.rid][1:])}"
                  for r in accs}
        tile_regs = {alloc.assignment[a.rid], alloc.assignment[b.rid]}
        disjoint = not any(
            tr in {g, f"v{int(g[1:]) + 1}"} for tr in tile_regs
            for g in groups)
        check("pressured-allocation-honors-parity-and-groups",
              even and disjoint,
              f"m2 bases {sorted(bases)} tiles {sorted(tile_regs)} "
              f"spills={alloc.stats['spilled_values']}")
    except alloc_mod.AllocationError as exc:
        check("pressured-allocation-honors-parity-and-groups", False,
              f"unexpected refusal: {str(exc)[:90]}")
    # the over-constrained case: 16 groups + tiles = 34 > 31 registers
    mod, accs, a, b = _tile_chain_module(16)
    errs = matrix_mod.verify_module(mod)
    check("overconstrained-module-verifies", not errs,
          str(errs[:1]) if errs else "")
    try:
        alloc = alloc_mod.allocate(mod, DEFAULT_TARGET)
        bases = {alloc.assignment[r.rid] for r in accs}
        even = all(int(n[1:]) % 2 == 0 for n in bases if n.startswith("v"))
        check("overconstrained-allocates-legally-or-refuses", even,
              f"legal allocation with spills="
              f"{alloc.stats['spilled_values']}")
    except alloc_mod.AllocationError as exc:
        check("overconstrained-allocates-legally-or-refuses", True,
              f"diagnosed refusal: {str(exc)[:80]}")


def check_selection():
    plan, mod = lower("int8", "int8", "int32")
    legal_mod.legalize(mod)
    selection = select_mod.select(mod)
    mnemonics = {s.mnemonic for s in selection.values()}
    check("int8-selection-includes-smt-vmadot", "smt.vmadot" in mnemonics,
          str(sorted(m for m in mnemonics if m.startswith("smt"))))
    plan_f, mod_f = lower("float16", "float16", "float32")
    legal_mod.legalize(mod_f)
    sel_f = select_mod.select(mod_f)
    check("fp16-selection-includes-smt-vfwmadot",
          "smt.vfwmadot" in {s.mnemonic for s in sel_f.values()})
    plan_b, mod_b = lower("bfloat16", "bfloat16", "float32")
    legal_mod.legalize(mod_b)
    sel_b = select_mod.select(mod_b)
    check("bf16-selection-has-no-ime-instruction",
          not any(m.startswith("smt.") for m in
                  {s.mnemonic for s in sel_b.values()}),
          "the vector-FP32 path emits no IME instruction (F010/F034)")
    # the repertoire rows are registered as data (table edit)
    opcodes = {e.opcode for e in DEFAULT_REPERTOIRE.entries}
    check("repertoire-rows-registered",
          matrix_mod.IME_OPCODES <= opcodes,
          f"{len(matrix_mod.IME_OPCODES)} ime opcodes in the table")
    rows = {r.mnemonic for r in matrix_mod.ime_repertoire_rows()}
    for m in ("smt.vmadot", "smt.vmadotu", "smt.vmadotus", "smt.vmadotsu",
              "smt.vfwmadot"):
        check(f"repertoire-row-{m}", m in rows)


def check_refuse_matrix_kept():
    """The elementwise lane's refusal entry point keeps its contract."""
    try:
        matrix_mod.refuse_matrix(None, "tl.dot", "probe")
        check("matrix-refusal-contract-kept", False, "no refusal raised")
    except matrix_mod.MatrixLoweringError as exc:
        check("matrix-refusal-contract-kept",
              "IME" in str(exc) and "LMUL=1" in str(exc), str(exc)[:80])


def check_strided_pack():
    """The strided staging-pack opcodes (the matmul optimization round):
    the repertoire rows as data, selection finds the vlse form, and the
    IME contract accepts the pack's own shape while rejecting a wrong
    region, a non-i64 stride and a wrong result width."""
    rows = {r.mnemonic: r for r in matrix_mod.ime_repertoire_rows()}
    for m in ("vlse8.v", "vlse16.v"):
        check(f"strided-row-{m}",
              m in rows and "{rs2}" in rows[m].form and "{rs1}" in
              rows[m].form,
              rows[m].form if m in rows else "missing")
    check("strided-opcodes-in-ime-set",
          {"vloads8", "vloads16"} <= matrix_mod.IME_OPCODES)

    def build(op, params=()):
        fn = mir.MFunction("f", list(params))
        entry = mir.Block("entry")
        fn.blocks.append(entry)
        mod = mir.MModule("probe", "<probe>")
        mod.functions.append(fn)
        entry.ops.append(op)
        entry.ops.append(mir.MOp("ret", [], [], loc="probe"))
        return mod

    def with_region(mod, sew, lmul):
        avl = mir.VReg(mir.I32, name="avl")
        mod.functions[0].blocks[0].ops.insert(0, mir.MOp(
            "vsetvli", [avl], [mir.VReg(mir.I32, name="vl")],
            attrs={"sew": sew, "lmul": lmul, "policy": "ta,ma"},
            loc="probe"))
        mod.functions[0].blocks[0].ops.insert(0, mir.MOp(
            "sconst", [], [avl], attrs={"value": 8}, loc="probe"))

    base = mir.VReg(mir.I64, name="base")
    stride = mir.VReg(mir.I64, name="stride")
    out16 = mir.VReg(mir.VectorType(16, 1, "float"), name="v")

    mod = build(mir.MOp("vloads16", [base, stride], [out16], loc="probe"),
                (base, stride, out16))
    with_region(mod, 16, 1)
    errs = matrix_mod.verify_module(mod)
    check("strided-pack-accepted", not errs, str(errs[:1]))
    legal_mod.legalize(mod)
    selection = select_mod.select(mod)
    check("strided-pack-selected-vlse16",
          "vlse16.v" in {s.mnemonic for s in selection.values()})

    mod = build(mir.MOp("vloads16", [base, stride], [out16], loc="probe"),
                (base, stride, out16))
    with_region(mod, 32, 1)
    errs = matrix_mod.verify_module(mod)
    check("strided-wrong-region-rejected",
          len(errs) == 1 and errs[0].invariant ==
          matrix_mod.IMEInvariant.IME_REGION, str(errs[:1]))

    stride32 = mir.VReg(mir.I32, name="stride32")
    mod = build(mir.MOp("vloads16", [base, stride32], [out16],
                        loc="probe"), (base, stride32, out16))
    with_region(mod, 16, 1)
    errs = matrix_mod.verify_module(mod)
    check("strided-non-i64-stride-rejected",
          len(errs) == 1 and errs[0].invariant ==
          matrix_mod.IMEInvariant.IME_SHAPE, str(errs[:1]))

    out8 = mir.VReg(mir.VectorType(8, 1, "uint"), name="v8")
    mod = build(mir.MOp("vloads16", [base, stride], [out8], loc="probe"),
                (base, stride, out8))
    with_region(mod, 16, 1)
    errs = matrix_mod.verify_module(mod)
    check("strided-wrong-result-width-rejected",
          len(errs) == 1 and errs[0].invariant ==
          matrix_mod.IMEInvariant.IME_SHAPE, str(errs[:1]))


def main() -> int:
    check_plan_families()
    check_plan_refusals()
    check_lowering_and_verify()
    check_ime_illegal_forms()
    check_allocator()
    check_selection()
    check_strided_pack()
    check_refuse_matrix_kept()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_lower_matrix: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
