"""IME matrix lowering: tl.dot to the A100 matrix extension (T010).

This module owns the matrix lane of the lowering
(ARCHITECTURE_CONSTRAINTS.json: "IME matrix lowering: tile mapping (vs1
row-major A, vs2 column-major B), accumulation typing, register grouping
constraints, MCPM-controlled format, BF16 gap handling via the vector FP32
path").  It consumes the dot tiling plan (``a100c/plan/tiles.py``) and the
bundle argument layout, and produces a complete program-level MIR module for
one dot kernel -- the same program shape the elementwise lane emits (entry
binding, worker-strided work loop, stats, ret), with the tile pipeline as
the body.

Lowered form of one 8x8 output tile (IME families, F030/F031/F033/F040):

  * staging: the A tile is materialised row-major (8 rows x tile_k elements)
    and the B tile column-major (8 columns x tile_k elements) in the
    worker-private workspace.  Every staging row/column is *fully written*
    each K step: valid positions come from memory through masked loads that
    perform no access at disabled lanes (the compiler never reads
    out-of-range memory to construct a nominally neutral term) and tail
    positions are written as zeros.  When the memory layout already provides
    the tile's contiguous direction (row-major A, column-major B), the
    staging copies are vector masked loads -- no software transpose (F031);
    otherwise the per-row/per-column pack runs as scalar loops (the
    ``smt.vpack`` interleave network is the declared vector alternative,
    F035, but its results require even-numbered m1 destinations the current
    allocator cannot express -- recorded as remaining work of the breadth
    lane).
  * the tile instruction: ``vmdot*``/``vfwmadot`` MIR ops whose selected
    repertoire rows emit ``smt.vmadot vd, vs1, vs2, i8`` (INT8 8x16x8 ->
    INT32; signedness variants none/u/us/su; 32-bit modular accumulation
    with a signed accumulator, F051) and ``smt.vfwmadot vd, vs1, vs2``
    (FP16 8x8x8 -> FP32, FP32 accumulation, F051).  Operand order follows
    the ISA: vs1 = the A tile, vs2 = the B tile (the geometric B^T
    statement -- no software transpose, F031).
  * accumulation: the MUL_C=2 accumulator is one m2 vector value (vd/vd+1
    the group); it chains through the K loop as a block parameter (the
    ``acc`` parameter of tl.dot) and is zero-initialised or loaded from C.
  * stores: the accumulator tile is written to a C staging tile, then each
    row is stored to C through an indexed masked store whose index vector
    carries the runtime column stride (strided C rows need no separate
    path); the store mask folds the M/N row guards, so disabled rows and
    columns perform no access.

Register grouping (F033/F040): the m2 accumulator allocation *is* the group
constraint -- the allocator's even-aligned m2 pairs give the even vd, and
its mixed-LMUL interference edges keep the destination group off vs1/vs2.
The tile forms additionally carry a defensive ``vsetvli x0, zero, e<sew>,
m1`` prefix: the ISA requires vtype LMUL=1 at every IME instruction, and
the prefix keeps that true even if an allocator-inserted vector reload
re-establishes an m2 region immediately before the tile op.

BF16 (F010/F034): the pinned emulator's BF16 IME format selection has not
passed; BF16 dot lowers to the ordinary RVV FMA path at e32 (BF16->FP32
widening is exact: zext + <<16 through an integer staging round trip, then
the float-typed reload), and no BF16 IME execution is claimed or inferable.

MIR extension (this module's contract with the backend):

  * new opcodes ``vmdot``/``vmdotu``/``vmdotus``/``vmdotsu``/``vfwmadot``
    (tile ops) and ``vuload8``/``vuload8m``/``vustore8``/``vuload16``/
    ``vuload16m``/``vustore16``/``vuload32``/``vustore32`` (unit-stride
    vector memory ops at region-governed width -- the gather forms cannot
    express a 128-byte tile load because their index groups would need lane
    counts the MIR's 32-lane ``vid`` cannot build);
  * their repertoire rows are registered into ``DEFAULT_REPERTOIRE`` as data
    (``Repertoire.add`` -- "adding an operation is a table edit"); importing
    this module is what arms the table for them;
  * ``verify_module`` is the IME-aware MIR verification: it runs
    ``a100c.ir.mir.verify_module`` for every general invariant (SSA,
    dominance, block structure, branch argument types, the regions of the
    generic vector ops -- these checks are opcode-agnostic and cover the new
    ops' operands too), sets aside the generic verifier's UNKNOWN_OP report
    for exactly these opcodes, and checks the IME contract in its place:
    family operand formats, LMUL=1 regions, even vd where MUL_C=2,
    destination/source group overlap, the v0 mask constraint of the masked
    loads, and the unit-stride regions.

Everything outside the declared slice is a located refusal
(MECH-DIAGNOSTIC-REFUSAL) through ``refuse_matrix`` -- the same entry point
``a100c/lower/vectorize.py`` calls for matrix-routed constructs, kept
verbatim so the elementwise lane's refusals are unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from a100c.backend.repertoire import DEFAULT_REPERTOIRE, InstructionEntry
from a100c.ir import mir
from a100c.lower import scalar as scalar_mod
from a100c.plan import tiles as tiles_mod
from a100c.plan.tiles import DotPlan
from a100c.target import TargetModel

__all__ = [
    "MatrixLoweringError", "refuse_matrix", "IME_OPERAND_CONTRACT",
    "MatrixOptions", "DotBinding", "dot_binding", "lower_dot",
    "verify_module", "verify", "IME_OPCODES", "ime_repertoire_rows",
    "IMEInvariant",
    # the composed pipeline's dot segment (T014)
    "ComposedDotSpec", "emit_composed_dot",
]


#: the sourced operand contract, recorded with every refusal (F030/F033/F040/F041)
IME_OPERAND_CONTRACT = (
    "IME LMUL=1 only; vs1 = A tile row-major; vs2 = B tile column-major; "
    "vd even-numbered when MUL_C=2; destination group must not overlap "
    "vs1/vs2; operand format per family; the pinned emulator's BF16 IME "
    "format selection is unverified (F010) so BF16 never reaches IME here"
)


class MatrixLoweringError(Exception):
    def __init__(self, loc, construct: str, message: str):
        super().__init__(f"matrix lowering: {construct}: {message}"
                         + (f" (at {loc})" if loc else ""))
        self.loc = loc
        self.construct = construct
        self.message = message


def refuse_matrix(loc, construct: str, message: str):
    """The single refusal path for every matrix-routed construct."""
    raise MatrixLoweringError(
        loc, construct,
        f"{message}; the IME tile path is not implemented by the vertical "
        f"slice (operand contract when implemented: {IME_OPERAND_CONTRACT})")


# ---------------------------------------------------------------------------
# The IME MIR opcodes: contract as data
# ---------------------------------------------------------------------------

#: tile op: opcode -> (family key, A element kind, B element kind); the
#: accumulator and result are (32, 2, family acc kind) for every family
#: (F030/F040: MUL_C=2, SEW=32)
_TILE_OPCODES: Dict[str, Tuple[str, str, str]] = {
    "vmdot": ("i8", "int", "int"),
    "vmdotu": ("i8", "uint", "uint"),
    "vmdotus": ("i8", "uint", "int"),
    "vmdotsu": ("i8", "int", "uint"),
    "vfwmadot": ("fp16", "float", "float"),
}

#: unit-stride vector memory op: opcode -> (sew, lmul, masked, is_store)
_MEM_OPCODES: Dict[str, Tuple[int, int, bool, bool]] = {
    "vuload8": (8, 1, False, False),
    "vuload8m": (8, 1, True, False),
    "vustore8": (8, 1, False, True),
    "vuload16": (16, 1, False, False),
    "vuload16m": (16, 1, True, False),
    "vustore16": (16, 1, False, True),
    "vuload32": (32, 2, False, False),
    "vustore32": (32, 2, False, True),
}

#: strided vector load: opcode -> (sew, lmul) -- the B-operand pack's
#: column gather (the matmul optimization round).  Probe-verified under
#: the pinned QEMU (docs/compiler-agent/optimizations/matmul/tooling/
#: probe-strided.S); the recorded indexed-form emulator defect (e64
#: index + sub-32-bit data SEGFAULT) does not cover strided forms.
_STRIDE_MEM_OPCODES: Dict[str, Tuple[int, int]] = {
    "vloads8": (8, 1),
    "vloads16": (16, 1),
}

IME_OPCODES = frozenset(_TILE_OPCODES) | frozenset(_MEM_OPCODES) | \
    frozenset(_STRIDE_MEM_OPCODES)

#: region (sew, lmul) each tile op requires (the ISA's LMUL=1 constraint)
_TILE_REGION = {"i8": (8, 1), "fp16": (16, 1)}


def ime_repertoire_rows() -> List[InstructionEntry]:
    """The IME rows of the repertoire, as data (TGT-INSTRUCTION-REPERTOIRE).

    Adding these is a table edit; the generic matcher needs no change.  The
    tile forms carry a defensive ``vsetvli x0, zero, e<sew>, m1`` prefix
    (rd=x0 with rs1=x0 leaves vl unchanged): the ISA requires vtype LMUL=1
    at every IME instruction and the prefix keeps that true regardless of
    the region an allocator-inserted reload re-established.
    """
    rows: List[InstructionEntry] = []
    ev = "F009/F034 (probed EXECUTED_AND_COMPARED_PASS under the pinned QEMU)"
    for opcode, (fam, _a, _b) in sorted(_TILE_OPCODES.items()):
        if fam == "i8":
            suffix = opcode[len("vmdot"):]
            rows.append(InstructionEntry(
                "smt.vmadot" + suffix, opcode, (),
                "vsetvli x0, zero, e8, m1, ta, ma\n"
                f"    smt.vmadot{suffix} {{vd}}, {{vs1}}, {{vs3}}, i8",
                evidence=ev,
                notes="INT8 8x16x8 -> INT32 tile (F030); vd is the MUL_C=2 "
                      "group; vs1 = A row-major, vs2 = B column-major "
                      "(F031); 32-bit modular accumulation, signed "
                      "accumulator (F051)"))
        else:
            rows.append(InstructionEntry(
                "smt.vfwmadot", opcode, (),
                "vsetvli x0, zero, e16, m1, ta, ma\n"
                "    smt.vfwmadot {vd}, {vs1}, {vs3}",
                evidence=ev + "; FP16 operands (MCPM.BF16=0 default, F011)",
                notes="FP16 8x8x8 -> FP32 tile (F030); FP32 accumulation "
                      "(F051); MCPM.BF16 is not userspace-accessible under "
                      "the pinned QEMU (F011) so only FP16 operands reach "
                      "this form -- the BF16 gap is recorded (F010/F034)"))
    mem_ev = "RVV 1.0 VLEN=1024 (F006/F026)"
    for opcode, (sew, lmul, masked, stores) in sorted(_MEM_OPCODES.items()):
        if stores:
            rows.append(InstructionEntry(
                f"vse{sew}.v", opcode, (),
                f"vse{sew}.v {{rs2}}, 0({{rs1}})", evidence=mem_ev,
                notes=("unit-stride store of the whole m2 group at the "
                       "region's vl (the C tile staging form)" if lmul == 2
                       else "unit-stride store of one staging row/column")))
        else:
            suffix = ", v0.t" if masked else ""
            rows.append(InstructionEntry(
                f"vle{sew}.v", opcode, (),
                f"vle{sew}.v {{vd}}, 0({{rs1}}){suffix}", evidence=mem_ev,
                notes=("unit-stride load of the whole m2 group at the vl"
                       if lmul == 2 else
                       "masked unit-stride load (no access at disabled "
                       "lanes; undisturbed lanes are merged by a vsel)"
                       if masked else
                       "unit-stride load of one full tile register")))
    for opcode, (sew, lmul) in sorted(_STRIDE_MEM_OPCODES.items()):
        rows.append(InstructionEntry(
            f"vlse{sew}.v", opcode, (),
            f"vlse{sew}.v {{vd}}, 0({{rs1}}), {{rs2}}",
            evidence="RVV 1.0 VLEN=1024; probe-verified under the pinned "
                     "QEMU (matmul round: docs/compiler-agent/optimizations"
                     "/matmul/tooling/probe-strided.S -- the pack shapes, "
                     "the region transition and avl 0)",
            notes="strided load of one staging column: lane l reads "
                  "rs1 + l*rs2 bytes; rs2 is the byte stride (N*esz), the "
                  "region's vl is the guarded element count"))
    return rows


def _register_repertoire_rows() -> None:
    """Register the IME rows into the default repertoire (a table edit).

    Additive only: no existing row shares these opcodes, so no selection
    that does not lower IME constructs can change (the generic matcher
    consults opcode + constraints; these are unique per opcode).
    """
    have = {e.opcode for e in DEFAULT_REPERTOIRE.entries}
    for row in ime_repertoire_rows():
        if row.opcode not in have:
            DEFAULT_REPERTOIRE.add(row)


_register_repertoire_rows()


# ---------------------------------------------------------------------------
# IME-aware MIR verification (the IME extension of the MIR verifier)
# ---------------------------------------------------------------------------


class IMEInvariant:
    """The IME contract's invariant classes (one rejection each)."""

    IME_FORMAT = "ime-operand-format-inconsistent-with-family"
    IME_LMUL = "ime-lmul-not-1"
    IME_PARITY = "ime-odd-destination-group"
    IME_OVERLAP = "ime-destination-overlaps-source"
    IME_MASK = "ime-mask-not-v0"
    IME_REGION = "ime-region-mismatch"
    IME_SHAPE = "ime-operand-shape"


def _phys_index(name: str) -> Optional[int]:
    if name and name.startswith("v") and name[1:].isdigit():
        return int(name[1:])
    return None


def _ime_op_errors(op: mir.MOp, region) -> List[mir.MirError]:
    """The IME contract of one op (types, region, register legality)."""
    errors: List[mir.MirError] = []
    code = op.opcode

    def err(invariant: str, msg: str) -> List[mir.MirError]:
        errors.append(mir.MirError(invariant, op.loc, msg))
        return errors

    if code in _TILE_OPCODES:
        fam, a_kind, b_kind = _TILE_OPCODES[code]
        family = tiles_mod.FAMILIES[fam]
        if len(op.operands) != 3 or len(op.results) != 1:
            return err(IMEInvariant.IME_SHAPE,
                       f"'{code}' takes (accumulator, A tile, B tile) and "
                       "produces the accumulator")
        acc, a, b = op.operands
        out = op.results[0]
        acc_ty = mir.VectorType(family.acc_sew, family.mul_c,
                                family.acc_kind)
        a_ty = mir.VectorType(family.in_width, 1, a_kind)
        b_ty = mir.VectorType(family.in_width, 1, b_kind)
        for what, got, want in (("accumulator", acc.type, acc_ty),
                                ("A tile", a.type, a_ty),
                                ("B tile", b.type, b_ty),
                                ("result", out.type, acc_ty)):
            if got != want:
                return err(IMEInvariant.IME_FORMAT,
                           f"'{code}' {what} must be {want!r} for the "
                           f"{family.key} family (F030/F031), got {got!r}")
        if region is None:
            return err(IMEInvariant.IME_REGION,
                       f"'{code}' executes outside any vsetvli region")
        sew, lmul = region
        want_sew, want_lmul = _TILE_REGION[fam]
        if lmul != want_lmul:
            return err(IMEInvariant.IME_LMUL,
                       f"'{code}' executes in region e{sew}m{lmul}; IME "
                       "instructions require vtype LMUL=1 (F033: every other "
                       "encoding is reserved and illegal)")
        if sew != want_sew:
            return err(IMEInvariant.IME_REGION,
                       f"'{code}' executes in region e{sew}m{lmul}; the "
                       f"{family.key} family's tiles run at e{want_sew}m1")
        if family.mul_c == 2:
            for what, reg in (("accumulator", acc), ("result", out)):
                if reg.fixed_phys is not None:
                    idx = _phys_index(reg.fixed_phys)
                    if idx is None or idx % 2 == 1:
                        return err(IMEInvariant.IME_PARITY,
                                   f"'{code}' {what} is fixed to "
                                   f"{reg.fixed_phys}; MUL_C=2 requires an "
                                   "even-numbered vd (vd and vd+1 the group)")
            group = {_phys_index(r.fixed_phys) for r in (acc, out)
                     if r.fixed_phys is not None}
            group.discard(None)
            for g in group:
                for src in (a, b):
                    if src.fixed_phys is not None:
                        s = _phys_index(src.fixed_phys)
                        if s is not None and s in (g, g + 1):
                            return err(
                                IMEInvariant.IME_OVERLAP,
                                f"'{code}' destination group v{g}/v{g + 1} "
                                f"overlaps source {src.name} at "
                                f"{src.fixed_phys} (F033/F040)")
        return errors

    if code in _MEM_OPCODES:
        sew, lmul, masked, stores = _MEM_OPCODES[code]
        if stores:
            if len(op.operands) != 2 or op.results:
                return err(IMEInvariant.IME_SHAPE,
                           f"'{code}' takes (base, value) and produces "
                           "nothing")
            base, val = op.operands
            if base.type != mir.I64:
                return err(IMEInvariant.IME_SHAPE,
                           f"'{code}' base must be i64, got {base.type!r}")
            if not val.is_vector() or (val.type.sew, val.type.lmul) != \
                    (sew, lmul):
                return err(IMEInvariant.IME_SHAPE,
                           f"'{code}' value must be (sew={sew}, lmul={lmul})"
                           f", got {val.type!r}")
        else:
            want = 2 if masked else 1
            if len(op.operands) != want or len(op.results) != 1:
                return err(IMEInvariant.IME_SHAPE,
                           f"'{code}' takes (base[, mask]) and produces the "
                           "loaded vector")
            base = op.operands[0]
            if base.type != mir.I64:
                return err(IMEInvariant.IME_SHAPE,
                           f"'{code}' base must be i64, got {base.type!r}")
            if masked:
                maskop = op.operands[1]
                if not maskop.is_mask():
                    return err(IMEInvariant.IME_SHAPE,
                               f"'{code}' mask operand must be a mask value")
                if maskop.fixed_phys != "v0":
                    return err(IMEInvariant.IME_MASK,
                               f"'{code}' reads its mask from hardware v0; "
                               f"operand {maskop.name} is not the fixed v0 "
                               "value (insert a vmovmask)")
            res = op.results[0]
            if not res.is_vector() or (res.type.sew, res.type.lmul) != \
                    (sew, lmul):
                return err(IMEInvariant.IME_SHAPE,
                           f"'{code}' result must be (sew={sew}, "
                           f"lmul={lmul}), got {res.type!r}")
        if region is None:
            return err(IMEInvariant.IME_REGION,
                       f"'{code}' executes outside any vsetvli region")
        if (region[0], region[1]) != (sew, lmul):
            return err(IMEInvariant.IME_REGION,
                       f"'{code}' executes in region e{region[0]}"
                       f"m{region[1]}; its value is (e{sew}, m{lmul})")
        return errors

    if code in _STRIDE_MEM_OPCODES:
        sew, lmul = _STRIDE_MEM_OPCODES[code]
        if len(op.operands) != 2 or len(op.results) != 1:
            return err(IMEInvariant.IME_SHAPE,
                       f"'{code}' takes (base, stride) and produces the "
                       "loaded vector")
        base, stride = op.operands
        if base.type != mir.I64:
            return err(IMEInvariant.IME_SHAPE,
                       f"'{code}' base must be i64, got {base.type!r}")
        if stride.type != mir.I64:
            return err(IMEInvariant.IME_SHAPE,
                       f"'{code}' stride must be i64 (bytes), got "
                       f"{stride.type!r}")
        res = op.results[0]
        if not res.is_vector() or (res.type.sew, res.type.lmul) != \
                (sew, lmul):
            return err(IMEInvariant.IME_SHAPE,
                       f"'{code}' result must be (sew={sew}, lmul={lmul}), "
                       f"got {res.type!r}")
        if region is None:
            return err(IMEInvariant.IME_REGION,
                       f"'{code}' executes outside any vsetvli region")
        if (region[0], region[1]) != (sew, lmul):
            return err(IMEInvariant.IME_REGION,
                       f"'{code}' executes in region e{region[0]}"
                       f"m{region[1]}; its value is (e{sew}, m{lmul})")
        return errors

    return errors


def _ime_contract_errors(module: mir.MModule) -> List[mir.MirError]:
    errors: List[mir.MirError] = []
    for fn in module.functions:
        for b in fn.blocks:
            region = None
            for op in b.ops:
                if op.opcode == "vsetvli":
                    region = (op.attrs["sew"], op.attrs["lmul"])
                elif op.opcode in IME_OPCODES:
                    errors.extend(_ime_op_errors(op, region))
    return errors


def verify_module(module: mir.MModule) -> List[mir.MirError]:
    """IME-aware MIR verification (mir/v1 + the IME contract).

    The generic verifier's opcode-agnostic checks (use-before-definition,
    double definitions, block structure, branch argument types, the regions
    of the generic vector ops) cover the new opcodes' operands like any
    other op; its UNKNOWN_OP report for exactly the IME opcodes is replaced
    here by the IME contract above (family formats, LMUL=1, parity, group
    overlap, v0 masks, unit-stride regions).
    """
    errors = list(mir.verify_module(module))
    out: List[mir.MirError] = []
    for e in errors:
        if e.invariant == mir.Invariant.UNKNOWN_OP:
            if any(e.message == f"unknown MIR opcode '{op}'"
                   for op in IME_OPCODES):
                continue          # checked below under the IME contract
        out.append(e)
    out.extend(_ime_contract_errors(module))
    return out


def verify(module: mir.MModule) -> None:
    """Verify a module; raise the first rejection found."""
    errors = verify_module(module)
    if errors:
        raise errors[0]


# ---------------------------------------------------------------------------
# Options and the argument binding
# ---------------------------------------------------------------------------


@dataclass
class MatrixOptions:
    """Lowering options; witness builds are recorded in the module meta."""

    #: witness-only degraded build: the staging loads lose their masks, so
    #: tail positions read out of range and the padding stops being zero --
    #: the tail case must FAIL under it (MECH-WITNESS-TEST: the padding is
    #: load-bearing).  Never set by the normal path.
    witness_drop_tile_padding: bool = False

    def identity_part(self) -> str:
        return ("witness-drop-tile-padding"
                if self.witness_drop_tile_padding else "default")


@dataclass(frozen=True)
class DotBinding:
    """The bundle binding of one dot kernel's three views (F046/F047).

    View indices follow the host packer's sorted-argument-name order (the
    same rule ``a100c/lower/binding.py`` derives for the elementwise lane).
    """

    a_index: int
    b_index: int
    c_index: int
    a_view: str = "a_ptr"
    b_view: str = "b_ptr"
    c_view: str = "c_ptr"

    def describe(self) -> dict:
        return {"a": [self.a_view, self.a_index],
                "b": [self.b_view, self.b_index],
                "c": [self.c_view, self.c_index]}


def dot_binding(names: Sequence[str]) -> DotBinding:
    """The binding for a case whose arrays are exactly ``names``."""
    order = sorted(names)
    if order != ["a_ptr", "b_ptr", "c_ptr"]:
        raise MatrixLoweringError(
            None, "binding",
            f"a dot case binds exactly the views a_ptr/b_ptr/c_ptr; "
            f"got {list(names)}")
    return DotBinding(a_index=0, b_index=1, c_index=2)


# ---------------------------------------------------------------------------
# The lowering
# ---------------------------------------------------------------------------


class _Ctx:
    """Emission helper: vreg creation, ordered op append, region tracking."""

    def __init__(self, module: mir.MModule, function: mir.MFunction):
        self.module = module
        self.function = function
        self.blocks: Dict[str, mir.Block] = {}
        self.cur: Optional[mir.Block] = None
        self._hints: Dict[str, int] = {}
        self._region: Optional[Tuple[int, int, int]] = None

    def add_block(self, name: str, params=(), loc=None) -> mir.Block:
        block = mir.Block(name, list(params), loc)
        self.function.blocks.append(block)
        self.blocks[name] = block
        return block

    def switch(self, block: mir.Block) -> None:
        self.cur = block
        self._region = None            # regions do not cross block boundaries

    def vreg(self, mtype, hint: str = "t", loc=None,
             fixed_phys: Optional[str] = None) -> mir.VReg:
        n = self._hints.get(hint, 0) + 1
        self._hints[hint] = n
        return mir.VReg(mtype, name=f"{hint}{n}", fixed_phys=fixed_phys,
                        loc=loc)

    def emit(self, op: mir.MOp) -> mir.VReg:
        self.cur.ops.append(op)
        assert len(op.results) == 1, op.opcode
        return op.results[0]

    def emit0(self, op: mir.MOp) -> None:
        self.cur.ops.append(op)

    def const(self, bits: int, mtype: mir.ScalarType, loc) -> mir.VReg:
        return self.emit(mir.MOp("sconst", [],
                                 [self.vreg(mtype, hint="k", loc=loc)],
                                 attrs={"value": int(bits)}, loc=loc))

    def region(self, sew: int, lmul: int, vl: int, loc) -> None:
        """Emit a vsetvli when the (sew, lmul, vl) changes (per block)."""
        if self._region == (sew, lmul, vl):
            return
        avl = self.const(vl, mir.I32, loc)
        self.emit0(mir.MOp("vsetvli", [avl],
                           [self.vreg(mir.I32, hint="rg", loc=loc)],
                           attrs={"sew": sew, "lmul": lmul,
                                  "policy": "ta,ma"}, loc=loc))
        self._region = (sew, lmul, vl)


def _tile_opcode_for(plan: DotPlan) -> str:
    if plan.path != "ime":
        raise MatrixLoweringError(
            None, "dot", "the vector-FP32 path emits no tile instruction")
    if plan.family.key == "fp16":
        return "vfwmadot"
    suffix = plan.family.suffix_for(plan.a_signed, plan.b_signed)
    return {"": "vmdot", "u": "vmdotu", "us": "vmdotus",
            "su": "vmdotsu"}[suffix]


class _DotLowering:
    """One (plan, binding, target, options) -> MIR lowering run."""

    def __init__(self, plan: DotPlan, binding: DotBinding,
                 target: TargetModel, options: MatrixOptions):
        self.plan = plan
        self.binding = binding
        self.target = target
        self.options = options
        self.loc = plan.source
        self.ime = plan.path == "ime"
        fam = plan.family
        if self.ime:
            self.in_sew = fam.in_width
            self.kstep = fam.tile_k
            self.row_lanes = fam.tile_k     # elements per staging row/column
            self.row_bytes = fam.tile_k * (fam.in_width // 8)   # 16 for both
            self.tile_lanes = target.vlenb // (fam.in_width // 8)
            self.in_type = mir.VectorType(
                fam.in_width, 1,
                "float" if fam.in_kind == "float"
                else ("uint" if not plan.a_signed else "int"))
            self.inb_type = mir.VectorType(
                fam.in_width, 1,
                "float" if fam.in_kind == "float"
                else ("uint" if not plan.b_signed else "int"))
            self.acc_type = mir.VectorType(fam.acc_sew, fam.mul_c,
                                           fam.acc_kind)
            self.acc_row_type = mir.VectorType(fam.acc_sew, 1,
                                               fam.acc_kind)
        else:
            self.in_sew = 16
            self.kstep = 1
            self.row_bytes = 32
        self.vt32m1 = mir.VectorType(32, 1, "int")
        self.vf32m1 = mir.VectorType(32, 1, "float")
        self.vu16m1 = mir.VectorType(16, 1, "uint")

    # -- scalar helpers -----------------------------------------------------
    def _k(self, ctx: _Ctx, value: int) -> mir.VReg:
        return ctx.const(value, mir.I64, self.loc)

    def _k32(self, ctx: _Ctx, value: int) -> mir.VReg:
        return ctx.const(value, mir.I32, self.loc)

    def _sbin(self, ctx: _Ctx, code: str, a: mir.VReg, b: mir.VReg,
              hint: str) -> mir.VReg:
        return ctx.emit(mir.MOp(code, [a, b],
                                [ctx.vreg(a.type, hint=hint, loc=self.loc)],
                                loc=self.loc))

    def _sadd(self, ctx, a, b, hint="sa"):
        return self._sbin(ctx, "sadd", a, b, hint)

    def _ssub(self, ctx, a, b, hint="ss"):
        return self._sbin(ctx, "ssub", a, b, hint)

    def _smul(self, ctx, a, b, hint="sm"):
        return self._sbin(ctx, "smul", a, b, hint)

    def _sand(self, ctx, a, b, hint="snd"):
        return self._sbin(ctx, "sand", a, b, hint)

    def _slt(self, ctx, a, b, hint="slt"):
        return ctx.emit(mir.MOp("slt", [a, b],
                                [ctx.vreg(mir.I64, hint=hint,
                                          loc=self.loc)], loc=self.loc))

    def _sltu(self, ctx, a, b, hint="sltu"):
        return ctx.emit(mir.MOp("sltu", [a, b],
                                [ctx.vreg(mir.I64, hint=hint,
                                          loc=self.loc)], loc=self.loc))

    def _sdivu(self, ctx, a, b, hint="sdv"):
        return self._sbin(ctx, "sdivu", a, b, hint)

    def _smin(self, ctx, a, b, hint="smn"):
        """min(a, b) = a + ((b - a) & -(a < b)) -- i64."""
        c = self._slt(ctx, a, b)
        zero = self._k(ctx, 0)
        mask = self._ssub(ctx, zero, c, hint="mnk")
        diff = self._ssub(ctx, b, a, hint="mnd")
        sel = self._sand(ctx, diff, mask, hint="mns")
        return self._sadd(ctx, a, sel, hint)

    def _guard(self, ctx, cond01: mir.VReg, raw: mir.VReg,
               hint: str) -> mir.VReg:
        """raw if cond01 else 0 (i64): raw & -cond."""
        zero = self._k(ctx, 0)
        mask = self._ssub(ctx, zero, cond01, hint=hint + "g")
        return self._sand(ctx, raw, mask, hint=hint)

    def _eq01(self, ctx, a: mir.VReg, value: int, hint: str) -> mir.VReg:
        """a == value as an i64 0/1."""
        diff = self._ssub(ctx, a, self._k(ctx, value), hint=hint + "d")
        one = self._k(ctx, 1)
        return self._sltu(ctx, diff, one, hint=hint + "e")

    def _narrow32(self, ctx, reg: mir.VReg, hint: str) -> mir.VReg:
        return ctx.emit(mir.MOp("strunc", [reg],
                                [ctx.vreg(mir.I32, hint=hint,
                                          loc=self.loc)], loc=self.loc))

    def _sload(self, ctx, base: mir.VReg, offset: int, width: int,
               ext: str, hint: str, wide64: bool = False) -> mir.VReg:
        """A scalar load; ``wide64`` holds a narrow load zero/sign-extended
        in an i64 register (the sload width only governs the memory
        access)."""
        mtype = mir.I64 if (width == 64 or wide64) else \
            mir.ScalarType(width, signed=(ext == "sext"))
        return ctx.emit(mir.MOp(
            "sload", [base],
            [ctx.vreg(mtype, hint=hint, loc=self.loc)],
            attrs={"width": width, "offset": offset, "ext": ext},
            loc=self.loc))

    # -- vector helpers -----------------------------------------------------
    def _splat(self, ctx, scalar: mir.VReg, vtype: mir.VectorType,
               hint: str) -> mir.VReg:
        return ctx.emit(mir.MOp("s2v", [scalar],
                                [ctx.vreg(vtype, hint=hint,
                                          loc=self.loc)], loc=self.loc))

    def _mask_lt(self, ctx, vid: mir.VReg, bound32: mir.VReg,
                 hint: str) -> mir.VReg:
        """lane < bound, as a mask value.

        The bound is splatted and compared vector-vs-vector: the emitter's
        ``vcmpx`` (vector-vs-scalar) path fills the scalar template slot
        from the vector operand, so the slice uses the well-emitted ``.vv``
        form (a pre-existing emission defect on an unexercised path,
        recorded for the backend owner).
        """
        splat = self._splat(ctx, bound32, self.vt32m1, hint + "s")
        return ctx.emit(mir.MOp(
            "vcmp", [vid, splat],
            [ctx.vreg(mir.MaskType(), hint=hint, loc=self.loc)],
            attrs={"pred": "lt"}, loc=self.loc))

    def _to_v0(self, ctx, mask: mir.VReg, hint: str) -> mir.VReg:
        return ctx.emit(mir.MOp(
            "vmovmask", [mask],
            [ctx.vreg(mir.MaskType(), hint=hint, loc=self.loc,
                      fixed_phys="v0")], loc=self.loc))

    def _vid(self, ctx, vl: int, hint: str) -> mir.VReg:
        return ctx.emit(mir.MOp("vid", [],
                                [ctx.vreg(self.vt32m1, hint=hint,
                                          loc=self.loc)], loc=self.loc))

    def _vmulx(self, ctx, vec: mir.VReg, scalar32: mir.VReg,
               hint: str) -> mir.VReg:
        return ctx.emit(mir.MOp(
            "vbinx", [vec, scalar32],
            [ctx.vreg(self.vt32m1, hint=hint, loc=self.loc)],
            attrs={"op": "mul"}, loc=self.loc))

    def _row_bound(self, ctx, r: Dict[str, mir.VReg], m0: mir.VReg, i: int,
                   raw: mir.VReg, hint: str) -> mir.VReg:
        """The staging/store mask bound of row i: raw if m0+i < M else 0."""
        mi = self._sadd(ctx, m0, self._k(ctx, i), hint=hint + "i")
        guard = self._slt(ctx, mi, r["M"], hint=hint + "g")
        bound = self._guard(ctx, guard, raw, hint=hint + "b")
        return self._narrow32(ctx, bound, hint + "32")

    # =====================================================================
    # The bundle entry (the same binding form the elementwise lane emits)
    # =====================================================================
    def _emit_entry(self, ctx: _Ctx) -> Dict[str, mir.VReg]:
        loc = self.loc
        launch = ctx.function.params[0]
        bundle = self._sload(ctx, launch, 0, 64, "sext", "bundle")
        views = self._sload(ctx, bundle, 0, 64, "sext", "views")
        worker_id = ctx.emit(mir.MOp(
            "sload", [launch],
            [ctx.vreg(mir.U32, hint="wid", loc=loc)],
            attrs={"width": 32, "offset": 40, "ext": "zext"}, loc=loc))
        worker_count = ctx.emit(mir.MOp(
            "sload", [launch],
            [ctx.vreg(mir.U32, hint="wcnt", loc=loc)],
            attrs={"width": 32, "offset": 44, "ext": "zext"}, loc=loc))

        def view(idx: int, hint: str) -> Dict[str, mir.VReg]:
            return {
                "data": self._sload(ctx, views, idx * 56, 64, "sext", hint),
                "shape": self._sload(ctx, views, idx * 56 + 8, 64, "sext",
                                     hint + "sh"),
                "strides": self._sload(ctx, views, idx * 56 + 16, 64, "sext",
                                       hint + "st"),
            }

        va = view(self.binding.a_index, "va")
        vb = view(self.binding.b_index, "vb")
        vc = view(self.binding.c_index, "vc")
        # the data pointers are re-loaded from the views pointer at their
        # use sites: one live GPR (views) instead of three (pressure)
        r: Dict[str, mir.VReg] = {
            "worker_id": worker_id,
            "worker_count": worker_count, "views": views,
            # extents: M/K from the A view, N from the C view (runtime,
            # never baked; the case layer guarantees the shapes agree)
            "M": self._sload(ctx, va["shape"], 0, 64, "sext", "M"),
            "K": self._sload(ctx, va["shape"], 8, 64, "sext", "K"),
            "N": self._sload(ctx, vc["shape"], 8, 64, "sext", "N"),
            "sA_m": self._sload(ctx, va["strides"], 0, 64, "sext", "sAm"),
            "sA_k": self._sload(ctx, va["strides"], 8, 64, "sext", "sAk"),
            "sB_k": self._sload(ctx, vb["strides"], 0, 64, "sext", "sBk"),
            "sB_n": self._sload(ctx, vb["strides"], 8, 64, "sext", "sBn"),
            "sC_m": self._sload(ctx, vc["strides"], 0, 64, "sext", "sCm"),
            "sC_n": self._sload(ctx, vc["strides"], 8, 64, "sext", "sCn"),
            "ws": self._sload(ctx, launch, 16, 64, "sext", "ws"),
        }
        r["wid64"] = ctx.emit(mir.MOp(
            "smove", [worker_id],
            [ctx.vreg(mir.I64, hint="wid64", loc=loc)], loc=loc))
        r["wcnt64"] = ctx.emit(mir.MOp(
            "smove", [worker_count],
            [ctx.vreg(mir.I64, hint="wcnt64", loc=loc)], loc=loc))
        return r

    # =====================================================================
    # The IME path
    # =====================================================================
    def lower_ime(self) -> mir.MModule:
        plan, loc = self.plan, self.loc
        module = mir.MModule(f"dot_{plan.family.key}", loc)
        launch = mir.VReg(mir.I64, name="launch")
        function = mir.MFunction("operator_entry", [launch], loc)
        module.functions.append(function)
        ctx = _Ctx(module, function)
        ctx.add_block("entry", [launch], loc)
        ctx.switch(ctx.blocks["entry"])
        r = self._emit_entry(ctx)

        a_stag = r["ws"]
        esz = plan.family.in_width // 8

        # loop-invariant vectors (hoisted to the entry; regions are per
        # block, so every block below re-opens its own).  The scalar live
        # set is kept deliberately small (register pressure): the staging
        # bases, the tile counts and the stats pointer are recomputed at
        # their use sites.
        ctx.region(32, 1, self.row_lanes, loc)
        vid_row = self._vid(ctx, self.row_lanes, "vidr")
        ctx.region(32, 1, 8, loc)
        vid8 = self._vid(ctx, 8, "vid8")
        idx_cstag = self._vmulx(ctx, vid8, self._k32(ctx, 4), "ixs")
        sC_n32 = self._narrow32(ctx, r["sC_n"], "sCn32")
        idx_cmemo = self._vmulx(ctx, vid8, sC_n32, "ixc")
        ctx.region(self.in_sew, 1, self.row_lanes, loc)
        zero_a = self._splat(ctx, self._k32(ctx, 0), self.in_type, "zina")
        zero_b = self._splat(ctx, self._k32(ctx, 0), self.inb_type, "zinb")

        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "tile_head",
                                 "args": [r["wid64"]]}, loc=loc))

        # -- tile_head(t): the worker-strided output-tile loop ----------------
        t_h = mir.VReg(mir.I64, name="t.head")
        head = ctx.add_block("tile_head", [t_h], loc)
        ctx.switch(head)
        tile_count = self._tile_count(ctx, r)
        go = self._slt(ctx, t_h, tile_count, hint="go")
        ctx.emit0(mir.MOp("brc", [go], [],
                          attrs={"true_target": "tile_body",
                                 "true_args": [t_h],
                                 "false_target": "tile_exit",
                                 "false_args": [t_h]}, loc=loc))

        # -- tile_body(t) ------------------------------------------------------
        t_b = mir.VReg(mir.I64, name="t.body")
        ctx.add_block("tile_body", [t_b], loc)
        ctx.switch(ctx.blocks["tile_body"])
        nt_count = self._nt_count(ctx, r)
        mt = self._sdivu(ctx, t_b, nt_count, hint="mt")
        nt = self._ssub(ctx, t_b, self._smul(ctx, mt, nt_count, hint="mtnt"),
                        hint="nt")
        m0 = self._smul(ctx, mt, self._k(ctx, 8), hint="m0")
        n0 = self._smul(ctx, nt, self._k(ctx, 8), hint="n0")

        if plan.acc_mode == "read_c":
            # the accumulator's initial value: the C tile, staged row by row
            # (masked loads; rows beyond M / columns beyond N are never
            # stored back, so their staged content is don't-care)
            nrem = self._ssub(ctx, r["N"], n0, hint="anrem")
            sC_m_a, sC_n_a = self._c_strides(ctx, r, "a")
            c_stag = self._sadd(ctx, r["ws"],
                                self._k(ctx, plan.c_stage_off), hint="acst")
            masks: List[mir.VReg] = [None] * 8      # type: ignore
            ctx.region(32, 1, 8, loc)
            for i in range(8):
                bound32 = self._row_bound(ctx, r, m0, i, nrem, "ab")
                masks[i] = self._mask_lt(ctx, vid8, bound32, "amk")
            row_base = self._sadd(
                ctx, self._sadd(ctx, self._data(ctx, r, "c", "acd"),
                                self._smul(ctx, m0, sC_m_a, hint="acm"),
                                hint="acb"),
                self._smul(ctx, n0, sC_n_a, hint="acn"), hint="acr")
            for i in range(8):
                if i:
                    row_base = self._sadd(ctx, row_base, sC_m_a,
                                          hint="acr")
                v0 = self._to_v0(ctx, masks[i], "av0")
                row = ctx.emit(mir.MOp(
                    "vloadix", [row_base, idx_cmemo, v0],
                    [ctx.vreg(self.acc_row_type, hint="arow", loc=loc)],
                    attrs={"eew": 32, "sew": 32, "default": "undef"},
                    loc=loc))
                stag_row = self._sadd(ctx, c_stag, self._k(ctx, i * 32),
                                      hint="asr")
                ctx.emit0(mir.MOp(
                    "vstoreix", [stag_row, idx_cstag, row], [],
                    attrs={"eew": 32, "sew": 32}, loc=loc))
            ctx.region(32, 2, 64, loc)
            acc = ctx.emit(mir.MOp(
                "vuload32", [c_stag],
                [ctx.vreg(self.acc_type, hint="acc0", loc=loc)], loc=loc))
        else:
            ctx.region(32, 2, 64, loc)
            acc = self._splat(ctx, self._k32(ctx, 0), self.acc_type, "acc0")
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "k_head",
                                 "args": [self._k(ctx, 0), acc]}, loc=loc))

        # -- k_head(k, acc): the K loop, accumulator carried ------------------
        k_h = mir.VReg(mir.I64, name="k.head")
        acc_h = mir.VReg(self.acc_type, name="acc.head")
        khead = ctx.add_block("k_head", [k_h, acc_h], loc)
        ctx.switch(khead)
        kgo = self._slt(ctx, k_h, r["K"], hint="kgo")
        ctx.emit0(mir.MOp("brc", [kgo], [],
                          attrs={"true_target": "k_body",
                                 "true_args": [k_h, acc_h],
                                 "false_target": "cstore",
                                 "false_args": [acc_h]}, loc=loc))

        # -- k_body(k, acc) ----------------------------------------------------
        k_b = mir.VReg(mir.I64, name="k.body")
        acc_b = mir.VReg(self.acc_type, name="acc.body")
        ctx.add_block("k_body", [k_b, acc_b], loc)
        ctx.switch(ctx.blocks["k_body"])
        krem = self._ssub(ctx, r["K"], k_b, hint="krem")
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "a_gate", "args": []}, loc=loc))

        # -- the A staging gate and paths ---------------------------------------
        ctx.add_block("a_gate", [], loc)
        ctx.switch(ctx.blocks["a_gate"])
        a_row0 = self._sadd(
            ctx, self._sadd(ctx, self._data(ctx, r, "a", "agd"),
                            self._smul(ctx, m0, r["sA_m"], hint="agm"),
                            hint="agb"),
            self._smul(ctx, k_b, r["sA_k"], hint="agk"), hint="agr")
        a_contig = self._eq01(ctx, r["sA_k"], esz, "actg")
        ctx.emit0(mir.MOp("brc", [a_contig], [],
                          attrs={"true_target": "a_vec", "true_args": [],
                                 "false_target": "a_sc_head",
                                 "false_args": [self._k(ctx, 0), a_row0,
                                                a_stag]}, loc=loc))
        self._emit_a_vec(ctx, r, vid_row, zero_a, m0, k_b, krem, a_stag)
        self._emit_pack_loops(ctx, r, "a", m0, r["M"], r["sA_m"], r["sA_k"],
                              krem, a_stag)

        # -- the B staging gate and paths ---------------------------------------
        ctx.add_block("b_gate", [], loc)
        ctx.switch(ctx.blocks["b_gate"])
        b_stag = self._sadd(ctx, r["ws"], self._k(ctx, plan.b_stage_off),
                            hint="bstg")
        b_col0 = self._sadd(
            ctx, self._sadd(ctx, self._data(ctx, r, "b", "bgd"),
                            self._smul(ctx, k_b, r["sB_k"], hint="bgk"),
                            hint="bgb"),
            self._smul(ctx, n0, r["sB_n"], hint="bgn"), hint="bgc")
        b_contig = self._eq01(ctx, r["sB_k"], esz, "bctg")
        ctx.emit0(mir.MOp("brc", [b_contig], [],
                          attrs={"true_target": "b_vec", "true_args": [],
                                 "false_target": "b_sc_head",
                                 "false_args": [self._k(ctx, 0), b_col0,
                                                b_stag]}, loc=loc))
        self._emit_b_vec(ctx, r, vid_row, zero_b, n0, k_b, krem, b_stag)
        self._emit_pack_loops(ctx, r, "b", n0, r["N"], r["sB_n"], r["sB_k"],
                              krem, b_stag)

        # -- the tile instruction -----------------------------------------------
        istep = ctx.add_block("ime_step", [], loc)
        ctx.switch(istep)
        ctx.region(self.in_sew, 1, self.tile_lanes, loc)
        vs1 = ctx.emit(mir.MOp(
            "vuload8" if self.in_sew == 8 else "vuload16", [a_stag],
            [ctx.vreg(self.in_type, hint="vs1", loc=loc)], loc=loc))
        vs2 = ctx.emit(mir.MOp(
            "vuload8" if self.in_sew == 8 else "vuload16", [b_stag],
            [ctx.vreg(self.inb_type, hint="vs2", loc=loc)], loc=loc))
        acc2 = ctx.emit(mir.MOp(
            _tile_opcode_for(plan), [acc_b, vs1, vs2],
            [ctx.vreg(self.acc_type, hint="acc2", loc=loc)], loc=loc))
        k2 = self._sadd(ctx, k_b, self._k(ctx, self.kstep), hint="k2")
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "k_head", "args": [k2, acc2]},
                          loc=loc))

        # -- cstore(acc): the C staging tile + masked strided row stores --------
        acc_c = mir.VReg(self.acc_type, name="acc.store")
        ctx.add_block("cstore", [acc_c], loc)
        ctx.switch(ctx.blocks["cstore"])
        nrem = self._ssub(ctx, r["N"], n0, hint="cnrem")
        sC_m_c, sC_n_c = self._c_strides(ctx, r, "c")
        c_stag = self._sadd(ctx, r["ws"], self._k(ctx, plan.c_stage_off),
                            hint="cstg")
        ctx.region(32, 2, 64, loc)
        ctx.emit0(mir.MOp("vustore32", [c_stag, acc_c], [], loc=loc))
        ctx.region(32, 1, 8, loc)
        cmasks: List[mir.VReg] = [None] * 8          # type: ignore
        for i in range(8):
            bound32 = self._row_bound(ctx, r, m0, i, nrem, "cb")
            cmasks[i] = self._mask_lt(ctx, vid8, bound32, "cmk")
        row_base = self._sadd(
            ctx, self._sadd(ctx, self._data(ctx, r, "c", "ccd"),
                            self._smul(ctx, m0, sC_m_c, hint="ccm"),
                            hint="ccb"),
            self._smul(ctx, n0, sC_n_c, hint="ccn"), hint="ccr")
        for i in range(8):
            if i:
                row_base = self._sadd(ctx, row_base, sC_m_c, hint="ccr")
            v0 = self._to_v0(ctx, cmasks[i], "cv0")
            stag_row = self._sadd(ctx, c_stag, self._k(ctx, i * 32),
                                  hint="csr")
            row = ctx.emit(mir.MOp(
                "vloadix", [stag_row, idx_cstag],
                [ctx.vreg(self.acc_row_type, hint="crow", loc=loc)],
                attrs={"eew": 32, "sew": 32}, loc=loc))
            ctx.emit0(mir.MOp(
                "vstoreix", [row_base, idx_cmemo, row, v0], [],
                attrs={"eew": 32, "sew": 32, "default": "no-access"},
                loc=loc))
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "tile_next",
                                 "args": [t_b]}, loc=loc))

        # -- tile_next / tile_exit ----------------------------------------------
        t_n = mir.VReg(mir.I64, name="t.next")
        ctx.add_block("tile_next", [t_n], loc)
        ctx.switch(ctx.blocks["tile_next"])
        launch = ctx.function.params[0]
        wcnt_n = ctx.emit(mir.MOp(
            "sload", [launch],
            [ctx.vreg(mir.U32, hint="nwcnt", loc=loc)],
            attrs={"width": 32, "offset": 44, "ext": "zext"}, loc=loc))
        wcnt64_n = ctx.emit(mir.MOp(
            "smove", [wcnt_n],
            [ctx.vreg(mir.I64, hint="nwcnt64", loc=loc)], loc=loc))
        t2 = self._sadd(ctx, t_n, wcnt64_n, hint="t2")
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "tile_head",
                                 "args": [t2]}, loc=loc))
        t_e = mir.VReg(mir.I64, name="t.exit")
        ctx.add_block("tile_exit", [t_e], loc)
        ctx.switch(ctx.blocks["tile_exit"])
        # the owned-tile count: t = wid + n*W at exit, so n = (t - wid)/W
        wid_e = ctx.emit(mir.MOp(
            "sload", [launch],
            [ctx.vreg(mir.U32, hint="xwid", loc=loc)],
            attrs={"width": 32, "offset": 40, "ext": "zext"}, loc=loc))
        wid64_e = ctx.emit(mir.MOp(
            "smove", [wid_e],
            [ctx.vreg(mir.I64, hint="xwid64", loc=loc)], loc=loc))
        wcnt_e = ctx.emit(mir.MOp(
            "sload", [launch],
            [ctx.vreg(mir.U32, hint="xwcnt", loc=loc)],
            attrs={"width": 32, "offset": 44, "ext": "zext"}, loc=loc))
        wcnt64_e = ctx.emit(mir.MOp(
            "smove", [wcnt_e],
            [ctx.vreg(mir.I64, hint="xwcnt64", loc=loc)], loc=loc))
        owned = self._sdivu(ctx, self._ssub(ctx, t_e, wid64_e, hint="exd"),
                            wcnt64_e, hint="exn")
        stats = self._sload(ctx, launch, 24, 64, "sext", "xst")
        ctx.emit0(mir.MOp("sstore", [stats, owned], [],
                          attrs={"width": 64, "offset": 0}, loc=loc))
        ctx.emit0(mir.MOp("ret", [], [], loc=loc))

        module.meta["ime"] = {
            "path": "ime", "family": plan.family.describe(),
            "mnemonic": plan.mnemonic,
            "tile_opcode": _tile_opcode_for(plan),
            "workspace_private": plan.workspace_private,
            "staging": {"a": plan.a_stage_off, "b": plan.b_stage_off,
                        "c": plan.c_stage_off},
            "witness": self.options.identity_part(),
            "binding": self.binding.describe(),
        }
        return module

    def _data(self, ctx: _Ctx, r: Dict[str, mir.VReg], which: str,
              hint: str) -> mir.VReg:
        """The view's element base, re-loaded at the use site (pressure)."""
        idx = {"a": self.binding.a_index, "b": self.binding.b_index,
               "c": self.binding.c_index}[which]
        return self._sload(ctx, r["views"], idx * 56, 64, "sext", hint)

    def _c_strides(self, ctx: _Ctx, r: Dict[str, mir.VReg],
                   tag: str) -> Tuple[mir.VReg, mir.VReg]:
        """Fresh C-stride loads at the use site (register pressure)."""
        sptr = self._sload(ctx, r["views"],
                           self.binding.c_index * 56 + 16, 64, "sext",
                           tag + "sp")
        return (self._sload(ctx, sptr, 0, 64, "sext", tag + "sm"),
                self._sload(ctx, sptr, 8, 64, "sext", tag + "sn"))

    def _tile_count(self, ctx: _Ctx, r: Dict[str, mir.VReg]) -> mir.VReg:
        seven = self._k(ctx, 7)
        mt = self._sdivu(ctx, self._sadd(ctx, r["M"], seven, hint="tc7"),
                         self._k(ctx, 8), hint="tcmt")
        nt = self._sdivu(ctx, self._sadd(ctx, r["N"], seven, hint="tcn7"),
                         self._k(ctx, 8), hint="tcnt")
        return self._smul(ctx, mt, nt, hint="tct")

    def _nt_count(self, ctx: _Ctx, r: Dict[str, mir.VReg]) -> mir.VReg:
        return self._sdivu(
            ctx, self._sadd(ctx, r["N"], self._k(ctx, 7), hint="ntc7"),
            self._k(ctx, 8), hint="ntcnt")


    # -- vector staging paths -------------------------------------------------
    def _emit_a_vec(self, ctx: _Ctx, r: Dict[str, mir.VReg],
                    vid_row: mir.VReg, zero_in: mir.VReg, m0: mir.VReg,
                    k_b: mir.VReg, krem: mir.VReg, a_stag: mir.VReg) -> None:
        """Vector A staging: 8 masked unit-stride row loads + zero merge.

        The masks are computed first (vector values are cheap in the
        31-register file); the row bases are chained transiently so at most
        one extra scalar is live at a time.
        """
        loc = self.loc
        ctx.add_block("a_vec", [], loc)
        ctx.switch(ctx.blocks["a_vec"])
        masks: List[mir.VReg] = []
        ctx.region(32, 1, self.row_lanes, loc)
        for i in range(8):
            bound32 = self._row_bound(ctx, r, m0, i, krem, "ab")
            masks.append(self._mask_lt(ctx, vid_row, bound32, "amk"))
        ctx.region(self.in_sew, 1, self.row_lanes, loc)
        row_base = self._sadd(
            ctx, self._sadd(ctx, self._data(ctx, r, "a", "avd"),
                            self._smul(ctx, m0, r["sA_m"], hint="avm"),
                            hint="avb"),
            self._smul(ctx, k_b, r["sA_k"], hint="avk"), hint="avr")
        self._emit_staged_rows(ctx, "a", masks, row_base, r["sA_m"], zero_in,
                               a_stag)
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "b_gate", "args": []}, loc=loc))

    def _emit_b_vec(self, ctx: _Ctx, r: Dict[str, mir.VReg],
                    vid_row: mir.VReg, zero_in: mir.VReg, n0: mir.VReg,
                    k_b: mir.VReg, krem: mir.VReg, b_stag: mir.VReg) -> None:
        """Vector B staging: 8 masked unit-stride column loads + zero merge."""
        loc = self.loc
        ctx.add_block("b_vec", [], loc)
        ctx.switch(ctx.blocks["b_vec"])
        masks: List[mir.VReg] = []
        ctx.region(32, 1, self.row_lanes, loc)
        for n in range(8):
            ni = self._sadd(ctx, n0, self._k(ctx, n), hint="bbni")
            guard = self._slt(ctx, ni, r["N"], hint="bbg")
            bound = self._guard(ctx, guard, krem, hint="bbb")
            bound32 = self._narrow32(ctx, bound, "bb32")
            masks.append(self._mask_lt(ctx, vid_row, bound32, "bmk"))
        ctx.region(self.in_sew, 1, self.row_lanes, loc)
        col_base = self._sadd(
            ctx, self._sadd(ctx, self._data(ctx, r, "b", "bvd"),
                            self._smul(ctx, k_b, r["sB_k"], hint="bvk"),
                            hint="bvbb"),
            self._smul(ctx, n0, r["sB_n"], hint="bvn"), hint="bvb")
        self._emit_staged_rows(ctx, "b", masks, col_base, r["sB_n"], zero_in,
                               b_stag)
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "ime_step", "args": []}, loc=loc))

    def _emit_staged_rows(self, ctx: _Ctx, which: str,
                          masks: List[mir.VReg], base0: mir.VReg,
                          stride: mir.VReg, zero_in: mir.VReg,
                          stag: mir.VReg) -> None:
        """The masked-load + zero-merge + unit-stride staging store loop.

        ``base0`` advances by ``stride`` per row/column; only the current
        base is live.  The witness build drops the masks (unmasked loads, no
        merge): tail positions then read out of range and the padding stops
        being zero.
        """
        loc = self.loc
        vtype = self.in_type if which == "a" else self.inb_type
        load_op = "vuload8m" if self.in_sew == 8 else "vuload16m"
        raw_load = "vuload8" if self.in_sew == 8 else "vuload16"
        store_op = "vustore8" if self.in_sew == 8 else "vustore16"
        base = base0
        for i in range(8):
            if i:
                base = self._sadd(ctx, base, stride, hint=f"{which}rb")
            stag_row = self._sadd(ctx, stag,
                                  self._k(ctx, i * self.row_bytes),
                                  hint=f"{which}vs")
            if self.options.witness_drop_tile_padding:
                row = ctx.emit(mir.MOp(
                    raw_load, [base],
                    [ctx.vreg(vtype, hint=f"{which}rw", loc=loc)], loc=loc))
                ctx.emit0(mir.MOp(store_op, [stag_row, row], [], loc=loc))
            else:
                v0 = self._to_v0(ctx, masks[i], f"{which}v0")
                row = ctx.emit(mir.MOp(
                    load_op, [base, v0],
                    [ctx.vreg(vtype, hint=f"{which}rw", loc=loc)], loc=loc))
                zrow = ctx.emit(mir.MOp(
                    "vsel", [v0, row, zero_in],
                    [ctx.vreg(vtype, hint=f"{which}zr", loc=loc)], loc=loc))
                ctx.emit0(mir.MOp(store_op, [stag_row, zrow], [], loc=loc))

    # -- scalar pack loops ------------------------------------------------------
    def _emit_pack_loops(self, ctx: _Ctx, r: Dict[str, mir.VReg],
                         which: str, base0: mir.VReg, limit: mir.VReg,
                         outer_stride: mir.VReg, inner_stride: mir.VReg,
                         krem: mir.VReg, stag: mir.VReg) -> None:
        """The scalar staging pack: zero each row/column, then copy the
        valid prefix.

        For the A operand the outer index runs over rows (guard m0+i < M,
        step sA_m) and the inner over the K prefix (step sA_k); for B the
        outer index runs over columns (guard n0+n < N, step sB_n) and the
        inner over the K prefix (step sB_k).  The loop entry arguments come
        from the operand's gate block.
        """
        loc = self.loc
        esz = self.plan.family.in_width // 8         # bytes per element
        ebits = self.plan.family.in_width            # sload/sstore width
        p = which                                    # block-name prefix
        ctx.add_block(f"{p}_sc_head",
                      [mir.VReg(mir.I64, name=f"{p}sc.i"),
                       mir.VReg(mir.I64, name=f"{p}sc.src"),
                       mir.VReg(mir.I64, name=f"{p}sc.dst")], loc)
        ctx.switch(ctx.blocks[f"{p}_sc_head"])
        i_h, src_h, dst_h = ctx.blocks[f"{p}_sc_head"].params
        cont = self._slt(ctx, i_h, self._k(ctx, 8), hint=f"{p}scc")
        ctx.emit0(mir.MOp("brc", [cont], [],
                          attrs={"true_target": f"{p}_sc_body",
                                 "true_args": [i_h, src_h, dst_h],
                                 "false_target":
                                     "b_gate" if p == "a" else "ime_step",
                                 "false_args": []}, loc=loc))

        ctx.add_block(f"{p}_sc_body",
                      [mir.VReg(mir.I64, name=f"{p}scb.i"),
                       mir.VReg(mir.I64, name=f"{p}scb.src"),
                       mir.VReg(mir.I64, name=f"{p}scb.dst")], loc)
        ctx.switch(ctx.blocks[f"{p}_sc_body"])
        i_b, src_b, dst_b = ctx.blocks[f"{p}_sc_body"].params
        ctx.region(self.in_sew, 1, self.row_lanes, loc)
        zero = self._splat(ctx, self._k32(ctx, 0),
                           self.in_type if p == "a" else self.inb_type,
                           f"{p}zn")
        ctx.emit0(mir.MOp(
            "vustore8" if self.in_sew == 8 else "vustore16",
            [dst_b, zero], [], loc=loc))
        bi = self._sadd(ctx, base0, i_b, hint=f"{p}sbi")
        guard = self._slt(ctx, bi, limit, hint=f"{p}sbg")
        kbound = self._smin(ctx, krem, self._k(ctx, self.kstep),
                            hint=f"{p}skb")
        rem = self._guard(ctx, guard, kbound, hint=f"{p}sbr")
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": f"{p}_sc_ihead",
                                 "args": [self._k(ctx, 0), src_b,
                                          dst_b]}, loc=loc))

        ctx.add_block(f"{p}_sc_ihead",
                      [mir.VReg(mir.I64, name=f"{p}si.q"),
                       mir.VReg(mir.I64, name=f"{p}si.s"),
                       mir.VReg(mir.I64, name=f"{p}si.d")], loc)
        ctx.switch(ctx.blocks[f"{p}_sc_ihead"])
        q_h2, s_h2, d_h2 = ctx.blocks[f"{p}_sc_ihead"].params
        qgo = self._slt(ctx, q_h2, rem, hint=f"{p}siq")
        ctx.emit0(mir.MOp("brc", [qgo], [],
                          attrs={"true_target": f"{p}_sc_ibody",
                                 "true_args": [q_h2, s_h2, d_h2],
                                 "false_target": f"{p}_sc_next",
                                 "false_args": [i_b, src_b,
                                                dst_b]}, loc=loc))

        ctx.add_block(f"{p}_sc_ibody",
                      [mir.VReg(mir.I64, name=f"{p}sib.q"),
                       mir.VReg(mir.I64, name=f"{p}sib.s"),
                       mir.VReg(mir.I64, name=f"{p}sib.d")], loc)
        ctx.switch(ctx.blocks[f"{p}_sc_ibody"])
        q_b2, s_b2, d_b2 = ctx.blocks[f"{p}_sc_ibody"].params
        val = self._sload(ctx, s_b2, 0, ebits, "zext", f"{p}sv")
        ctx.emit0(mir.MOp("sstore", [d_b2, val], [],
                          attrs={"width": ebits, "offset": 0}, loc=loc))
        q2 = self._sadd(ctx, q_b2, self._k(ctx, 1), hint=f"{p}sq2")
        s2 = self._sadd(ctx, s_b2, inner_stride, hint=f"{p}ss2")
        d2 = self._sadd(ctx, d_b2, self._k(ctx, esz), hint=f"{p}sd2")
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": f"{p}_sc_ihead",
                                 "args": [q2, s2, d2]}, loc=loc))

        ctx.add_block(f"{p}_sc_next",
                      [mir.VReg(mir.I64, name=f"{p}sn.i"),
                       mir.VReg(mir.I64, name=f"{p}sn.src"),
                       mir.VReg(mir.I64, name=f"{p}sn.dst")], loc)
        ctx.switch(ctx.blocks[f"{p}_sc_next"])
        i_n, src_n, dst_n = ctx.blocks[f"{p}_sc_next"].params
        i2 = self._sadd(ctx, i_n, self._k(ctx, 1), hint=f"{p}si2")
        src2 = self._sadd(ctx, src_n, outer_stride, hint=f"{p}ssrc")
        dst2 = self._sadd(ctx, dst_n, self._k(ctx, self.row_bytes),
                          hint=f"{p}sdst")
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": f"{p}_sc_head",
                                 "args": [i2, src2, dst2]}, loc=loc))

    # =====================================================================
    # The BF16 vector-FP32 path (the recorded emulator gap's declared route)
    # =====================================================================
    def lower_vector(self) -> mir.MModule:
        plan, loc = self.plan, self.loc
        if plan.path != "vector-fp32":
            raise MatrixLoweringError(None, "dot", "not a vector-FP32 plan")
        module = mir.MModule("dot_bf16_vector", loc)
        launch = mir.VReg(mir.I64, name="launch")
        function = mir.MFunction("operator_entry", [launch], loc)
        module.functions.append(function)
        ctx = _Ctx(module, function)
        ctx.add_block("entry", [launch], loc)
        ctx.switch(ctx.blocks["entry"])
        r = self._emit_entry(ctx)

        bconv = r["ws"]                      # 16 converted fp32 words
        braw_stag = self._sadd(ctx, r["ws"], self._k(ctx, 64),
                               hint="braw")  # 16 raw bf16 halfwords
        b_contig = self._eq01(ctx, r["sB_n"], 2, "bctg")
        chunk_count = self._sdivu(
            ctx, self._sadd(ctx, r["N"], self._k(ctx, 15), hint="n15"),
            self._k(ctx, 16), hint="cchunk")

        ctx.region(32, 1, 16, loc)
        vid16 = self._vid(ctx, 16, "vid16")
        idx_conv = self._vmulx(ctx, vid16, self._k32(ctx, 4), "ixv")
        sC_n32 = self._narrow32(ctx, r["sC_n"], "vCn32")
        idx_cmemo = self._vmulx(ctx, vid16, sC_n32, "ixc")
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "chunk_head",
                                 "args": [r["wid64"]]}, loc=loc))

        # chunk_head(c, items): worker-strided output column chunks
        c_h = mir.VReg(mir.I64, name="c.head")
        chead = ctx.add_block("chunk_head", [c_h], loc)
        ctx.switch(chead)
        cgo = self._slt(ctx, c_h, chunk_count, hint="cgo")
        ctx.emit0(mir.MOp("brc", [cgo], [],
                          attrs={"true_target": "chunk_body",
                                 "true_args": [c_h],
                                 "false_target": "chunk_exit",
                                 "false_args": [c_h]}, loc=loc))

        c_b = mir.VReg(mir.I64, name="c.body")
        ctx.add_block("chunk_body", [c_b], loc)
        ctx.switch(ctx.blocks["chunk_body"])
        n0 = self._smul(ctx, c_b, self._k(ctx, 16), hint="vn0")
        nrem = self._ssub(ctx, r["N"], n0, hint="vnrem")
        nrem32 = self._narrow32(ctx, nrem, "vnr32")
        ctx.region(32, 1, 16, loc)
        mask_n = self._mask_lt(ctx, vid16, nrem32, "vnk")
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "m_head",
                                 "args": [self._k(ctx, 0)]},
                          loc=loc))

        # m_head(m): the output rows
        m_h = mir.VReg(mir.I64, name="m.head")
        mhead = ctx.add_block("m_head", [m_h], loc)
        ctx.switch(mhead)
        mgo = self._slt(ctx, m_h, r["M"], hint="mgo")
        ctx.emit0(mir.MOp("brc", [mgo], [],
                          attrs={"true_target": "m_body",
                                 "true_args": [m_h],
                                 "false_target": "chunk_next",
                                 "false_args": [c_b]}, loc=loc))

        m_b = mir.VReg(mir.I64, name="m.body")
        ctx.add_block("m_body", [m_b], loc)
        ctx.switch(ctx.blocks["m_body"])
        ctx.region(32, 1, 16, loc)
        zero_f = self._splat(ctx, self._k32(ctx, 0), self.vf32m1, "zf")
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "kk_head",
                                 "args": [self._k(ctx, 0), zero_f]},
                          loc=loc))

        # kk_head(k, acc): the K loop of one output row
        k_h = mir.VReg(mir.I64, name="vk.head")
        acc_h = mir.VReg(self.vf32m1, name="vacc.head")
        khead = ctx.add_block("kk_head", [k_h, acc_h], loc)
        ctx.switch(khead)
        kgo = self._slt(ctx, k_h, r["K"], hint="vkgo")
        ctx.emit0(mir.MOp("brc", [kgo], [],
                          attrs={"true_target": "kk_body",
                                 "true_args": [k_h, acc_h],
                                 "false_target": "cstore_row",
                                 "false_args": [acc_h]}, loc=loc))

        k_b = mir.VReg(mir.I64, name="vk.body")
        acc_b = mir.VReg(self.vf32m1, name="vacc.body")
        ctx.add_block("kk_body", [k_b, acc_b], loc)
        ctx.switch(ctx.blocks["kk_body"])
        bbase = self._sadd(
            ctx, self._sadd(ctx, self._data(ctx, r, "b", "vbd"),
                            self._smul(ctx, k_b, r["sB_k"], hint="vbk"),
                            hint="vbbb"),
            self._smul(ctx, n0, r["sB_n"], hint="vbn"), hint="vbb")
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "bload_gate", "args": []}, loc=loc))

        # the B row gate: contiguous rows load directly (masked); strided
        # rows zero-fill the raw staging, copy the valid prefix into it,
        # then load it whole
        ctx.add_block("bload_gate", [], loc)
        ctx.switch(ctx.blocks["bload_gate"])
        kbound = self._smin(ctx, nrem, self._k(ctx, 16), hint="vbkb")
        ctx.emit0(mir.MOp("brc", [b_contig], [],
                          attrs={"true_target": "bload_vec", "true_args": [],
                                 "false_target": "bload_sc_zero",
                                 "false_args": []}, loc=loc))

        ctx.add_block("bload_vec", [], loc)
        ctx.switch(ctx.blocks["bload_vec"])
        ctx.region(16, 1, 16, loc)
        v0n = self._to_v0(ctx, mask_n, "vbv0")
        braw_v = ctx.emit(mir.MOp(
            "vuload16m", [bbase, v0n],
            [ctx.vreg(self.vu16m1, hint="vbraw", loc=loc)], loc=loc))
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "conv", "args": [braw_v]},
                          loc=loc))

        # the strided B row: zero-fill first, then the scalar copies
        ctx.add_block("bload_sc_zero", [], loc)
        ctx.switch(ctx.blocks["bload_sc_zero"])
        ctx.region(16, 1, 16, loc)
        zero16 = self._splat(ctx, self._k32(ctx, 0), self.vu16m1, "z16")
        ctx.emit0(mir.MOp("vustore16", [braw_stag, zero16], [], loc=loc))
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "bload_sc_head",
                                 "args": [self._k(ctx, 0), bbase,
                                          braw_stag]}, loc=loc))
        ctx.add_block("bload_sc_head",
                      [mir.VReg(mir.I64, name="vbs.q"),
                       mir.VReg(mir.I64, name="vbs.s"),
                       mir.VReg(mir.I64, name="vbs.d")], loc)
        ctx.switch(ctx.blocks["bload_sc_head"])
        q_h, s_h, d_h = ctx.blocks["bload_sc_head"].params
        qgo = self._slt(ctx, q_h, kbound, hint="vbsq")
        ctx.emit0(mir.MOp("brc", [qgo], [],
                          attrs={"true_target": "bload_sc_body",
                                 "true_args": [q_h, s_h, d_h],
                                 "false_target": "bload_sc_done",
                                 "false_args": []}, loc=loc))
        ctx.add_block("bload_sc_body",
                      [mir.VReg(mir.I64, name="vbsb.q"),
                       mir.VReg(mir.I64, name="vbsb.s"),
                       mir.VReg(mir.I64, name="vbsb.d")], loc)
        ctx.switch(ctx.blocks["bload_sc_body"])
        q_b2, s_b2, d_b2 = ctx.blocks["bload_sc_body"].params
        val = self._sload(ctx, s_b2, 0, 16, "zext", "vbsv")
        ctx.emit0(mir.MOp("sstore", [d_b2, val], [],
                          attrs={"width": 16, "offset": 0}, loc=loc))
        q2 = self._sadd(ctx, q_b2, self._k(ctx, 1), hint="vbsq2")
        s2 = self._sadd(ctx, s_b2, r["sB_n"], hint="vbss2")
        d2 = self._sadd(ctx, d_b2, self._k(ctx, 2), hint="vbsd2")
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "bload_sc_head",
                                 "args": [q2, s2, d2]}, loc=loc))
        ctx.add_block("bload_sc_done", [], loc)
        ctx.switch(ctx.blocks["bload_sc_done"])
        ctx.region(16, 1, 16, loc)
        braw_s = ctx.emit(mir.MOp(
            "vuload16", [braw_stag],
            [ctx.vreg(self.vu16m1, hint="vbrw", loc=loc)], loc=loc))
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "conv", "args": [braw_s]},
                          loc=loc))

        # conv(braw): widen bf16 -> fp32 bits, stage, reload as float
        braw_c = mir.VReg(self.vu16m1, name="braw.conv")
        ctx.add_block("conv", [braw_c], loc)
        ctx.switch(ctx.blocks["conv"])
        ctx.region(16, 1, 16, loc)
        bw = ctx.emit(mir.MOp(
            "vwaddx0", [braw_c],
            [ctx.vreg(mir.VectorType(32, 2, "int"), hint="vbw",
                      loc=loc)], attrs={"mode": "zext"}, loc=loc))
        ctx.region(32, 2, 16, loc)
        bws = ctx.emit(mir.MOp(
            "vbinx", [bw, self._k32(ctx, 65536)],
            [ctx.vreg(mir.VectorType(32, 2, "int"), hint="vbws",
                      loc=loc)], attrs={"op": "mul"}, loc=loc))
        ctx.emit0(mir.MOp("vustore32", [bconv, bws], [], loc=loc))
        ctx.region(32, 1, 16, loc)
        bf = ctx.emit(mir.MOp(
            "vloadix", [bconv, idx_conv],
            [ctx.vreg(self.vf32m1, hint="vbf", loc=loc)],
            attrs={"eew": 32, "sew": 32}, loc=loc))
        # the A element (scalar, any stride): bf16 bits << 16 as fp32 bits
        aaddr = self._sadd(
            ctx, self._sadd(ctx, self._data(ctx, r, "a", "vad"),
                            self._smul(ctx, m_b, r["sA_m"], hint="vam"),
                            hint="vab"),
            self._smul(ctx, k_b, r["sA_k"], hint="vak"), hint="vaa")
        a16 = self._sload(ctx, aaddr, 0, 16, "zext", "va16", wide64=True)
        a32 = self._sbin(ctx, "sshl", a16, self._k(ctx, 16), "va32")
        asplat = self._splat(ctx, a32, self.vf32m1, "vasp")
        prod = ctx.emit(mir.MOp(
            "vbin", [asplat, bf],
            [ctx.vreg(self.vf32m1, hint="vpr", loc=loc)],
            attrs={"op": "mul"}, loc=loc))
        acc2 = ctx.emit(mir.MOp(
            "vbin", [acc_b, prod],
            [ctx.vreg(self.vf32m1, hint="vac2", loc=loc)],
            attrs={"op": "add"}, loc=loc))
        k2 = self._sadd(ctx, k_b, self._k(ctx, 1), hint="vk2")
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "kk_head", "args": [k2, acc2]},
                          loc=loc))

        # cstore_row(acc): the masked strided row store
        acc_c = mir.VReg(self.vf32m1, name="vacc.store")
        ctx.add_block("cstore_row", [acc_c], loc)
        ctx.switch(ctx.blocks["cstore_row"])
        ctx.region(32, 1, 16, loc)
        v0n2 = self._to_v0(ctx, mask_n, "vcv0")
        cbase = self._sadd(
            ctx, self._sadd(ctx, self._data(ctx, r, "c", "vcd"),
                            self._smul(ctx, m_b, r["sC_m"], hint="vcm"),
                            hint="vcb2"),
            self._smul(ctx, n0, r["sC_n"], hint="vcn"), hint="vcb")
        ctx.emit0(mir.MOp(
            "vstoreix", [cbase, idx_cmemo, acc_c, v0n2], [],
            attrs={"eew": 32, "sew": 32, "default": "no-access"}, loc=loc))
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "m_next",
                                 "args": [m_b]}, loc=loc))

        m_n = mir.VReg(mir.I64, name="m.next")
        ctx.add_block("m_next", [m_n], loc)
        ctx.switch(ctx.blocks["m_next"])
        m2 = self._sadd(ctx, m_n, self._k(ctx, 1), hint="vm2")
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "m_head",
                                 "args": [m2]}, loc=loc))

        c_n = mir.VReg(mir.I64, name="c.next")
        ctx.add_block("chunk_next", [c_n], loc)
        ctx.switch(ctx.blocks["chunk_next"])
        launch = ctx.function.params[0]
        wcnt_v = ctx.emit(mir.MOp(
            "sload", [launch],
            [ctx.vreg(mir.U32, hint="nvwcnt", loc=loc)],
            attrs={"width": 32, "offset": 44, "ext": "zext"}, loc=loc))
        wcnt64_v = ctx.emit(mir.MOp(
            "smove", [wcnt_v],
            [ctx.vreg(mir.I64, hint="nvwcnt64", loc=loc)], loc=loc))
        c2 = self._sadd(ctx, c_n, wcnt64_v, hint="vc2")
        ctx.emit0(mir.MOp("br", [], [],
                          attrs={"target": "chunk_head",
                                 "args": [c2]}, loc=loc))

        c_e = mir.VReg(mir.I64, name="c.exit")
        ctx.add_block("chunk_exit", [c_e], loc)
        ctx.switch(ctx.blocks["chunk_exit"])
        # owned chunks = (c - wid)/W; rows computed = owned * M
        wid_v = ctx.emit(mir.MOp(
            "sload", [launch],
            [ctx.vreg(mir.U32, hint="xvwid", loc=loc)],
            attrs={"width": 32, "offset": 40, "ext": "zext"}, loc=loc))
        wid64_v = ctx.emit(mir.MOp(
            "smove", [wid_v],
            [ctx.vreg(mir.I64, hint="xvwid64", loc=loc)], loc=loc))
        wcnt_v2 = ctx.emit(mir.MOp(
            "sload", [launch],
            [ctx.vreg(mir.U32, hint="xvwcnt", loc=loc)],
            attrs={"width": 32, "offset": 44, "ext": "zext"}, loc=loc))
        wcnt64_v2 = ctx.emit(mir.MOp(
            "smove", [wcnt_v2],
            [ctx.vreg(mir.I64, hint="xvwcnt64", loc=loc)], loc=loc))
        owned = self._sdivu(ctx, self._ssub(ctx, c_e, wid64_v, hint="vxd"),
                            wcnt64_v2, hint="vxn")
        items = self._smul(ctx, owned, r["M"], hint="vxit")
        stats = self._sload(ctx, launch, 24, 64, "sext", "xvst")
        ctx.emit0(mir.MOp("sstore", [stats, items], [],
                          attrs={"width": 64, "offset": 0}, loc=loc))
        ctx.emit0(mir.MOp("ret", [], [], loc=loc))

        module.meta["ime"] = {
            "path": "vector-fp32",
            "bf16_gap": plan.bf16_gap,
            "acc_mode": plan.acc_mode,
            "workspace_private": plan.workspace_private,
            "vector_chunk": plan.vector_chunk,
            "witness": self.options.identity_part(),
            "binding": self.binding.describe(),
        }
        return module


def lower_dot(plan: DotPlan, binding: DotBinding, target: TargetModel,
              options: Optional[MatrixOptions] = None) -> mir.MModule:
    """Lower one planned dot kernel to a complete MIR program module."""
    options = options or MatrixOptions()
    low = _DotLowering(plan, binding, target, options)
    if plan.path == "ime":
        return low.lower_ime()
    if plan.path == "vector-fp32":
        return low.lower_vector()
    raise MatrixLoweringError(
        None, "dot", f"plan path {plan.path!r} is not a declared lowering "
        "path (ime | vector-fp32)")


# ---------------------------------------------------------------------------
# The composed pipeline's dot segment (T014: the matrix-breadth lane)
#
# One ``linalg.dot`` inside a kernel lowers as a SEGMENT between the
# vectorize passes: the operands arrive as staged block values (flat,
# compile-time-shaped regions in the worker-private workspace) and the
# result becomes a staged value the epilogue consumes.  Everything here
# reads the workspace through unit-stride or scalar forms at compiler-known
# addresses -- the narrow-data indexed forms the pinned QEMU crashes on
# (the probed e8/e16 + e64m2 constraint recorded in the staging analysis)
# never appear.
#
# The IME path reuses the slice's proven tile structure (staging rows with
# masked loads + zero merges, the column-major B pack, the m2 accumulator
# chaining through the K loop); the vector path is the budget-bounded FMA
# form (fp32 IEEE -- no tf32 anywhere on this input path, F052 -- and the
# BF16 widening, exact by construction).
# ---------------------------------------------------------------------------


from dataclasses import dataclass as _dataclass, field as _field

from a100c.plan.tiles import BreadthDotPlan


@_dataclass
class ComposedDotSpec:
    """The composed-path dot contract: the plan, the staged-region
    records (offset/extent/element-size/lane width) and the compile-time
    block extents."""

    plan: BreadthDotPlan
    a_rec: dict
    b_rec: dict
    acc_rec: Optional[dict]
    res_rec: dict
    block_m: int
    block_n: int
    block_k: int
    #: the transient staging area's byte offset in the private workspace
    #: (the dense A/B tiles and the C accumulator staging; 512B when any
    #: IME dot exists -- reserved by the lowering's workspace accounting)
    stage_off: Optional[int] = None
    loc: object = None


class _Composed:
    """One composed dot emission over the vectorize lowering's interface.

    The interface (constructed by ``a100c/lower/vectorize.py``) supplies
    the emission context, the private workspace base, region control, the
    scalar loop forms, unique block tags and the 16-bit float conversions
    -- the same services the slice's own ``_Ctx`` provides, so the tile
    pipeline below is the slice's structure against the composed
    program's address space.
    """

    def __init__(self, iface, spec: ComposedDotSpec):
        self.if_ = iface
        self.spec = spec
        self.plan = spec.plan
        fam = plan = self.plan
        self.ime = plan.path == "ime"
        # the composed lane honours the lowering switch (CompileOptions /
        # LowerOptions matrix_scalar_pack): True forces the scalar pack
        lowering_options = getattr(iface.sl, "options", None)
        self.pack_vector = not getattr(lowering_options,
                                       "matrix_scalar_pack", False)
        if self.ime:
            fam = plan.family
            self.tm, self.tn, self.tk = fam.tile_m, fam.tile_n, fam.tile_k
            self.mt = (spec.block_m + self.tm - 1) // self.tm
            self.nt = (spec.block_n + self.tn - 1) // self.tn
            self.in_sew = fam.in_width
            self.esz = fam.in_width // 8
            self.row_bytes = self.tk * self.esz      # 16 for both families
            self.tile_lanes = 128 // self.esz        # the m1 tile register
            self.in_type = mir.VectorType(
                fam.in_width, 1,
                "float" if fam.in_kind == "float"
                else ("uint" if not plan.a_signed else "int"))
            self.inb_type = mir.VectorType(
                fam.in_width, 1,
                "float" if fam.in_kind == "float"
                else ("uint" if not plan.b_signed else "int"))
            self.acc_type = mir.VectorType(fam.acc_sew, fam.mul_c,
                                           fam.acc_kind)
        self.M, self.N, self.K = spec.block_m, spec.block_n, spec.block_k
        self.vt32m1 = mir.VectorType(32, 1, "int")
        self._vlen_bits = iface.sl.target.vlen_bits
        #: per-block constant cache (T014: the GPR live-set stays flat)
        self._kcache: dict = {}

    # -- the interface's small helpers (the slice's forms) -----------------
    def _k(self, v: int):
        """An i64 constant, materialized once per BLOCK (the composed
        segment's bodies re-use a handful of distinct tile constants
        dozens of times; per-block reuse keeps the GPR live set flat --
        constants are pure, so a later block simply re-emits)."""
        key = ("k", v, id(self.if_.ctx.cur))
        reg = self._kcache.get(key)
        if reg is None:
            reg = self.if_.const(v, mir.I64, self.spec.loc)
            self._kcache[key] = reg
        return reg

    def _k32(self, v: int):
        key = ("k32", v, id(self.if_.ctx.cur))
        reg = self._kcache.get(key)
        if reg is None:
            reg = self.if_.const(v, mir.I32, self.spec.loc)
            self._kcache[key] = reg
        return reg

    def _sbin(self, code, a, b, hint):
        return self.if_.emit(mir.MOp(
            code, [a, b], [self.if_.vreg(a.type, hint=hint,
                                        loc=self.spec.loc)],
            loc=self.spec.loc))

    def _sadd(self, a, b, hint="sa"):
        return self._sbin("sadd", a, b, hint)

    def _ssub(self, a, b, hint="ss"):
        return self._sbin("ssub", a, b, hint)

    def _smul(self, a, b, hint="sm"):
        return self._sbin("smul", a, b, hint)

    def _sand(self, a, b, hint="snd"):
        return self._sbin("sand", a, b, hint)

    def _slt(self, a, b, hint="slt"):
        return self.if_.emit(mir.MOp(
            "slt", [a, b], [self.if_.vreg(mir.I64, hint=hint,
                                          loc=self.spec.loc)],
            loc=self.spec.loc))

    def _sltu(self, a, b, hint="sltu"):
        return self.if_.emit(mir.MOp(
            "sltu", [a, b], [self.if_.vreg(mir.I64, hint=hint,
                                           loc=self.spec.loc)],
            loc=self.spec.loc))

    def _sdivu(self, a, b, hint="sdv"):
        return self._sbin("sdivu", a, b, hint)

    def _smin(self, a, b, hint="smn"):
        """min(a, b) = a + ((b - a) & -(a < b)) -- i64."""
        c = self._slt(a, b)
        zero = self._k(0)
        mask = self._ssub(zero, c, "mnk")
        diff = self._ssub(b, a, "mnd")
        sel = self._sand(diff, mask, "mns")
        return self._sadd(a, sel, hint)

    def _guard(self, cond01, raw, hint="grd"):
        """raw if cond01 else 0 (i64): raw & -cond."""
        zero = self._k(0)
        mask = self._ssub(zero, cond01, hint + "g")
        return self._sand(raw, mask, hint + "b")

    def _narrow32(self, reg, hint):
        return self.if_.emit(mir.MOp(
            "strunc", [reg],
            [self.if_.vreg(mir.I32, hint=hint, loc=self.spec.loc)],
            loc=self.spec.loc))

    def _sload(self, base, offset, width, ext, hint):
        mtype = mir.I64 if width == 64 else \
            mir.ScalarType(width, signed=(ext == "sext"))
        return self.if_.emit(mir.MOp(
            "sload", [base], [self.if_.vreg(mtype, hint=hint,
                                            loc=self.spec.loc)],
            attrs={"width": width, "offset": offset, "ext": ext},
            loc=self.spec.loc))

    def _splat(self, scalar, vtype, hint):
        return self.if_.emit(mir.MOp(
            "s2v", [scalar], [self.if_.vreg(vtype, hint=hint,
                                            loc=self.spec.loc)],
            loc=self.spec.loc))

    def _lane_type(self, vl: int) -> mir.VectorType:
        """The e32 lane-id class covering ``vl`` lanes: the LMUL that
        holds the WHOLE chunk (T029: at m1 a vsetvli caps vl at
        vlmax(e32,m1)=32, so a 128-lane chunk's lane ids and N-tail mask
        would silently cover only the first 32 lanes -- the masked B-row
        load zero-filled and the masked result store skipped lanes 32+,
        the wrong-answer defect behind the removed LMUL-4 refusal)."""
        lmul = max(1, vl * 32 // self._vlen_bits)
        if lmul not in (1, 2, 4, 8):
            raise MatrixLoweringError(
                None, "dot",
                f"the {vl}-lane chunk needs an e32 lane class at LMUL "
                f"{lmul} (outside 1..8)")
        return mir.VectorType(32, lmul, "int")

    def _vid(self, vl, hint):
        vtype = self._lane_type(vl)
        self.if_.region(32, vtype.lmul, vl, self.spec.loc)
        return self.if_.emit(mir.MOp(
            "vid", [], [self.if_.vreg(vtype, hint=hint,
                                      loc=self.spec.loc)],
            loc=self.spec.loc))

    def _mask_lt(self, vid, bound32, hint, vl):
        """lane < bound as a mask value, at the lane class that covers
        all ``vl`` lanes (the lane ids and the bound splat share it)."""
        vtype = self._lane_type(vl)
        if vid.type != vtype:
            raise MatrixLoweringError(
                None, "dot",
                f"the lane ids ({vid.type!r}) do not match the "
                f"{vl}-lane mask class ({vtype!r})")
        self.if_.region(32, vtype.lmul, vl, self.spec.loc)
        splat = self._splat(bound32, vtype, hint + "s")
        return self.if_.emit(mir.MOp(
            "vcmp", [vid, splat],
            [self.if_.vreg(mir.MaskType(), hint=hint,
                           loc=self.spec.loc)],
            attrs={"pred": "lt"}, loc=self.spec.loc))

    def _to_v0(self, mask, hint):
        return self.if_.emit(mir.MOp(
            "vmovmask", [mask],
            [self.if_.vreg(mir.MaskType(), hint=hint, loc=self.spec.loc,
                           fixed_phys="v0")], loc=self.spec.loc))

    def _vload_unit(self, base, vtype, vl, v0=None, hint="ldu"):
        """A unit-stride load at a compiler-known scalar address (the
        safe form for every staged-region read: no index vector)."""
        self.if_.region(vtype.sew, vtype.lmul, vl, self.spec.loc)
        ops = [base]
        attrs = {"sew": vtype.sew}
        if v0 is not None:
            ops.append(v0)
            attrs["default"] = "undef"
        return self.if_.emit(mir.MOp(
            "vunit_load", ops,
            [self.if_.vreg(vtype, hint=hint, loc=self.spec.loc)],
            attrs=attrs, loc=self.spec.loc))

    def _vstore_unit(self, base, val, vl, v0=None):
        self.if_.region(val.type.sew, val.type.lmul, vl, self.spec.loc)
        ops = [base, val] + ([v0] if v0 is not None else [])
        self.if_.emit0(mir.MOp(
            "vunit_store", ops, [],
            attrs={"sew": val.type.sew,
                   **({"default": "no-access"} if v0 is not None else {})},
            loc=self.spec.loc))

    def _vsel(self, v0, a, b, hint):
        return self.if_.emit(mir.MOp(
            "vsel", [v0, a, b],
            [self.if_.vreg(a.type, hint=hint, loc=self.spec.loc)],
            loc=self.spec.loc))

    def _splat_const(self, value, vtype, hint):
        wide = self.if_.const(int(value), mir.ScalarType(vtype.sew,
                                                         True),
                              self.spec.loc)
        return self._splat(wide, vtype, hint)

    # =====================================================================
    # The IME path
    # =====================================================================
    def emit_ime(self) -> dict:
        if_ = self.if_
        spec, plan = self.spec, self.plan
        loc = spec.loc
        ws = if_.ws(loc)
        stage = self._sadd(ws, self._k(spec.stage_off), "mstg")
        a_stag = stage
        b_stag = self._sadd(stage, self._k(128), "bstg")
        c_stag = self._sadd(stage, self._k(256), "cstg")
        fam = plan.family
        res_rec, acc_rec = spec.res_rec, spec.acc_rec
        res_esz = res_rec["esz"]
        res_is16 = res_rec["type"].bitwidth() == 16

        # the segment's entry: hoist the lane ids and the zero splats
        vid_k = self._vid(self.tk, "mvid")       # the A-row lane ids
        vid8 = self._vid(8, "mvd8")              # the C-row lane ids
        self.if_.region(self.in_sew, 1, self.tile_lanes, loc)
        zero_a = self._splat(self._k32(0), self.in_type, "mza")
        zero_b = self._splat(self._k32(0), self.inb_type, "mzb")

        # -- the tile loop -------------------------------------------------
        tag = if_.tag("mtile")
        tframe = if_.loop(self._k(0), self._k(self.mt * self.nt), [], loc,
                          tag)
        t = tframe.params[0]
        nt_c = self._k(self.nt)
        mtq = self._sdivu(t, nt_c, "mmt")
        ntq = self._ssub(t, self._smul(mtq, nt_c, "mtn"), "mnt")
        m0 = self._smul(mtq, self._k(self.tm), "mm0")
        n0 = self._smul(ntq, self._k(self.tn), "mn0")

        # the accumulator init: the acc tile (chain) or zeros
        if plan.acc_mode == "chain":
            acc = self._load_acc_tile(c_stag, m0, n0, vid8, acc_rec)
        else:
            self.if_.region(32, fam.mul_c, 64, loc)
            acc = self._splat(self._k32(0), self.acc_type, "mz2")
        kframe = if_.loop(self._k(0), self._k(self.K), [acc], loc,
                          if_.tag("mk"))
        kb = kframe.params[0]

        # -- the A staging: 8 masked native row loads + zero merges -------
        krem = self._ssub(self._k(self.K), kb, "mkrem")
        self._stage_a_rows(ws, spec.a_rec, a_stag, m0, kb, krem, vid_k,
                           zero_a)
        # -- the B staging: the column-major scalar pack -------------------
        self._pack_b_columns(ws, spec.b_rec, b_stag, n0, kb, krem, zero_b)

        # -- the tile instruction -------------------------------------------
        self.if_.region(self.in_sew, 1, self.tile_lanes, loc)
        vs1 = self.if_.emit(mir.MOp(
            "vuload8" if self.in_sew == 8 else "vuload16", [a_stag],
            [self.if_.vreg(self.in_type, hint="mvs1", loc=loc)], loc=loc))
        vs2 = self.if_.emit(mir.MOp(
            "vuload8" if self.in_sew == 8 else "vuload16", [b_stag],
            [self.if_.vreg(self.inb_type, hint="mvs2", loc=loc)], loc=loc))
        acc2 = self.if_.emit(mir.MOp(
            _tile_opcode_for_plan_breadth(plan), [kframe.params[1], vs1, vs2],
            [self.if_.vreg(self.acc_type, hint="macc", loc=loc)], loc=loc))
        k2 = self._sadd(kb, self._k(self.tk), "mk2")
        if_.close(kframe, [k2, acc2], loc)

        # -- the C staging tile + the masked result-region stores ----------
        acc_c = kframe.exit.params[1]
        self.if_.region(32, fam.mul_c, 64, loc)
        self.if_.emit0(mir.MOp("vustore32", [c_stag, acc_c], [], loc=loc))
        self._store_result_rows(ws, res_rec, c_stag, m0, n0, vid8)
        t2 = self._sadd(t, self._k(1), "mt2")
        if_.close(tframe, [t2], loc)
        return {"path": "ime", "mnemonic": plan.mnemonic,
                "tiles": self.mt * self.nt,
                "k_steps": (self.K + self.tk - 1) // self.tk}

    def _load_acc_tile(self, c_stag, m0, n0, vid8, acc_rec):
        """The chain mode's accumulator tile: 8 masked rows from the acc
        region (the out dtype; 16-bit rows widen exactly), staged into the
        C staging tile then loaded as the m2 group."""
        loc = self.spec.loc
        ws = self.if_.ws(loc)
        esz = acc_rec["esz"]
        ty16 = acc_rec["type"]
        is16 = ty16.bitwidth() == 16
        rty = mir.VectorType(16, 1, "float") if is16 else \
            mir.VectorType(32, 1, ty16.kind if not ty16.is_float()
                           else "float")
        # the zero the masked rows select from opens its OWN region at the
        # row type (the tile loop's 16-bit loads leave their region active;
        # the e32 acc splat would run there -- the vsetvli-region
        # consistency invariant, matmul_kernel's fp16 form)
        self.if_.region(rty.sew, rty.lmul, 8, loc)
        zero = self._splat(self._k32(0), rty, "az")
        for i in range(self.tm):
            mi = self._sadd(m0, self._k(i), f"ami{i}")
            guard = self._slt(mi, self._k(self.M), f"amg{i}")
            nrem = self._ssub(self._k(self.N), n0, f"anr{i}")
            bound = self._guard(guard, nrem, f"ab{i}")
            bound32 = self._narrow32(bound, f"ab32{i}")
            mask = self._mask_lt(vid8, bound32, f"amk{i}", 8)
            v0 = self._to_v0(mask, f"av0{i}")
            base = self._sadd(ws, self._k(acc_rec["offset"]),
                              f"aab{i}")
            base = self._sadd(base, self._smul(mi, self._k(self.N * esz),
                                               f"aam{i}"), f"aar{i}")
            base = self._sadd(base, self._smul(n0, self._k(esz),
                                               f"aan{i}"), f"aac{i}")
            row = self._vload_unit(base, rty, 8, v0, f"arw{i}")
            row = self._vsel(v0, row, zero, f"azr{i}")
            if is16:
                row = self.if_.widen_f16(row, ty16)
            stag_row = self._sadd(c_stag, self._k(i * 32), f"asr{i}")
            self._vstore_unit(stag_row, row, 8)
        self.if_.region(32, self.plan.family.mul_c, 64, loc)
        return self.if_.emit(mir.MOp(
            "vuload32", [c_stag],
            [self.if_.vreg(self.acc_type, hint="macc0", loc=loc)], loc=loc))

    def _stage_a_rows(self, ws, a_rec, a_stag, m0, kb, krem, vid_k, zero_a):
        """The A tile: 8 rows of tk elements, masked (row guard + K tail),
        zero-merged, stored to the dense tile staging."""
        loc = self.spec.loc
        esz = a_rec["esz"]
        for i in range(self.tm):
            mi = self._sadd(m0, self._k(i), f"tmi{i}")
            guard = self._slt(mi, self._k(self.M), f"tmg{i}")
            kmin = self._smin(krem, self._k(self.tk), f"tkb{i}")
            bound = self._guard(guard, kmin, f"tb{i}")
            bound32 = self._narrow32(bound, f"tb32{i}")
            mask = self._mask_lt(vid_k, bound32, f"tmk{i}", self.tk)
            v0 = self._to_v0(mask, f"tv0{i}")
            base = self._sadd(
                ws, self._k(a_rec["offset"]), f"tab{i}")
            base = self._sadd(base, self._smul(mi, self._k(self.K * esz),
                                               f"tam{i}"), f"tar{i}")
            base = self._sadd(base, self._smul(kb, self._k(esz),
                                               f"tak{i}"), f"tac{i}")
            row = self._vload_unit(base, self.in_type, self.tk, v0,
                                   f"trw{i}")
            row = self._vsel(v0, row, zero_a, f"tzr{i}")
            stag_row = self._sadd(a_stag, self._k(i * self.row_bytes),
                                  f"tvs{i}")
            self.if_.region(self.in_sew, 1, self.tk, loc)
            self.if_.emit0(mir.MOp(
                "vustore8" if self.in_sew == 8 else "vustore16",
                [stag_row, row], [], loc=loc))

    def _pack_b_columns(self, ws, b_rec, b_stag, n0, kb, krem, zero_b):
        """The B tile: 8 columns of tk elements packed from the row-major
        (K, N) region.  The default packs each column with ONE strided
        vector load (vlse, byte stride N*esz, vl = the guarded count) and
        one unit store -- probe-verified under the pinned QEMU (the
        matmul round's tooling/probe-strided.S; the pinned QEMU's
        recorded indexed-form defect does not cover strided forms).  The
        guarded scalar per-element loops remain as the fallback: any
        other family width, or the lowering option matrix_scalar_pack
        (the on/off contrast and rollback path).

        W2-P1 (the unified optimization round): when every column is in
        bounds (n0 + tn <= N) and the whole K prefix is present (krem >=
        tk) -- the full-tile case, the dominant one on the perf shapes --
        a straight-line unguarded peel replaces the guarded loop: one
        constant-vl vsetvli, one strided load + one unit store per
        column, incrementing addresses, no zero fill (every lane is
        overwritten).  The hand-verified transform measured -28% on the
        128^3 fp16 flagship (/tmp/a100c-opt2's replay); the tail tiles
        keep the guarded path below."""
        loc = self.spec.loc
        if self.pack_vector and self.in_sew in (8, 16):
            # n0 + tn <= N  <=>  n0 + tn < N + 1;  krem >= tk  <=>
            # tk < krem + 1 (the slt forms; no sle/sge in the repertoire)
            n_end = self._sadd(n0, self._k(self.tn), "pfn")
            full_n = self._slt(n_end, self._k(self.N + 1), "pfl")
            full_k = self._slt(self._k(self.tk),
                               self._sadd(krem, self._k(1), "pfkr"), "pfk")
            both = self._sand(full_n, full_k, "pfa")
            tag = self.if_.tag("pbf")
            frame = scalar_mod.begin_if(self.if_.ctx, both, loc, tag)
            # -- the fast arm: the unguarded straight-line pack ----------
            self.if_.ctx.switch(frame.then_block)
            esz = b_rec["esz"]
            self.if_.region(self.in_sew, 1, self.tk, loc)
            stride = self._k(self.N * esz)
            src = self._sadd(ws, self._k(b_rec["offset"]), "pfs")
            src = self._sadd(src, self._smul(kb, stride, "pfkb"), "pfr")
            src = self._sadd(src, self._smul(n0, self._k(esz), "pfnz"),
                             "pfc")
            dst = b_stag
            for j in range(self.tn):
                gathered = self.if_.emit(mir.MOp(
                    f"vloads{self.in_sew}", [src, stride],
                    [self.if_.vreg(self.inb_type, hint=f"pfv{j}",
                                   loc=loc)], loc=loc))
                self.if_.emit0(mir.MOp(
                    "vustore8" if self.in_sew == 8 else "vustore16",
                    [dst, gathered], [], loc=loc))
                if j + 1 < self.tn:
                    src = self._sadd(src, self._k(esz), f"pfs{j}")
                    dst = self._sadd(dst, self._k(self.row_bytes),
                                     f"pfd{j}")
            scalar_mod.close_arm(self.if_.ctx, frame, f"{tag}.join", [])
            # -- the slow arm: the guarded pack (tails, ragged shapes) ---
            self.if_.ctx.switch(frame.else_block)
            self._pack_b_columns_guarded(ws, b_rec, b_stag, n0, kb, krem,
                                         zero_b)
            scalar_mod.close_arm(self.if_.ctx, frame, f"{tag}.join", [])
            scalar_mod.join_if(self.if_.ctx, frame, f"{tag}.join", [[], []],
                               loc)
            self.if_.ctx.switch(self.if_.ctx.blocks[f"{tag}.join"])
            return
        self._pack_b_columns_guarded(ws, b_rec, b_stag, n0, kb, krem, zero_b)

    def _pack_b_columns_guarded(self, ws, b_rec, b_stag, n0, kb, krem,
                                zero_b):
        """The guarded B pack: the zero fill plus the per-column guard /
        rem chain and the strided (or scalar) copy -- the tail-tile path
        and the rollback form."""
        loc = self.spec.loc
        esz = b_rec["esz"]
        ebits = self.in_sew
        # zero all 8 staging columns first
        self.if_.region(self.in_sew, 1, self.tk, loc)
        for j in range(self.tn):
            stag_col = self._sadd(b_stag, self._k(j * self.row_bytes),
                                  f"pzc{j}")
            self.if_.emit0(mir.MOp(
                "vustore8" if self.in_sew == 8 else "vustore16",
                [stag_col, zero_b], [], loc=loc))
        # the outer loop over columns j in [0, tn)
        jf = self.if_.loop(self._k(0), self._k(self.tn), [], loc,
                           self.if_.tag("pb"))
        j = jf.params[0]
        nj = self._sadd(n0, j, "pnj")
        guard = self._slt(nj, self._k(self.N), "png")
        kmin = self._smin(krem, self._k(self.tk), "pkb")
        rem = self._guard(guard, kmin, "pbr")
        src0 = self._sadd(ws, self._k(b_rec["offset"]), "psb")
        src0 = self._sadd(src0, self._smul(kb, self._k(self.N * esz),
                                           "psk"), "psr")
        src0 = self._sadd(src0, self._smul(nj, self._k(esz), "psn"),
                          "psc")
        dst0 = self._sadd(b_stag, self._smul(j, self._k(self.row_bytes),
                                             "pdj"), "pds")
        if self.pack_vector and self.in_sew in (8, 16):
            # one strided gather + one unit store per column.  rem <= tk
            # <= vlmax, so the runtime-AVL vsetvli sets vl = rem exactly;
            # rem == 0 (a guarded-out column) makes both no-ops
            # (probe-verified).  Lanes past rem keep the zero fill above
            # -- identical to the scalar prefix copy.
            rem32 = self._narrow32(rem, "pq32")
            self.if_.emit0(mir.MOp(
                "vsetvli", [rem32],
                [self.if_.vreg(mir.I32, hint="pqg", loc=loc)],
                attrs={"sew": self.in_sew, "lmul": 1,
                       "policy": "ta,ma"}, loc=loc))
            stride = self._k(self.N * esz)
            gathered = self.if_.emit(mir.MOp(
                f"vloads{self.in_sew}", [src0, stride],
                [self.if_.vreg(self.inb_type, hint="pqv", loc=loc)],
                loc=loc))
            self.if_.emit0(mir.MOp(
                "vustore8" if self.in_sew == 8 else "vustore16",
                [dst0, gathered], [], loc=loc))
        else:
            # the scalar fallback: the guarded per-element copy loop
            qf = self.if_.loop(self._k(0), rem, [], loc,
                               self.if_.tag("pq"))
            q = qf.params[0]
            src = self._sadd(src0, self._smul(q, self._k(self.N * esz),
                                               "pqw"), "pqs")
            dst = self._sadd(dst0, self._smul(q, self._k(esz), "pqs2"),
                             "pqd")
            val = self._sload(src, 0, ebits, "zext", "pv")
            self.if_.emit0(mir.MOp(
                "sstore", [dst, val], [],
                attrs={"width": ebits, "offset": 0}, loc=loc))
            q2 = self._sadd(q, self._k(1), "pq2")
            self.if_.close(qf, [q2], loc)
        j2 = self._sadd(j, self._k(1), "pj2")
        self.if_.close(jf, [j2], loc)

    def _store_result_rows(self, ws, res_rec, c_stag, m0, n0, vid8):
        """The C tile: the staged m2 accumulator stored row by row to the
        result region (masked: no access past the region's N tail or the
        M rows; a 16-bit out converts with one final rounding)."""
        loc = self.spec.loc
        esz = res_rec["esz"]
        ty = res_rec["type"]
        is16 = ty.bitwidth() == 16
        rty_in = mir.VectorType(32, 1, "float")
        for i in range(self.tm):
            mi = self._sadd(m0, self._k(i), f"cmi{i}")
            guard = self._slt(mi, self._k(self.M), f"cmg{i}")
            nrem = self._ssub(self._k(self.N), n0, f"cnr{i}")
            bound = self._guard(guard, nrem, f"cb{i}")
            bound32 = self._narrow32(bound, f"cb32{i}")
            mask = self._mask_lt(vid8, bound32, f"cmk{i}", 8)
            v0 = self._to_v0(mask, f"cv0{i}")
            stag_row = self._sadd(c_stag, self._k(i * 32), f"csr{i}")
            row = self._vload_unit(stag_row, rty_in, 8, hint=f"crw{i}")
            base = self._sadd(ws, self._k(res_rec["offset"]), f"cab{i}")
            base = self._sadd(base, self._smul(mi, self._k(self.N * esz),
                                               f"cam{i}"), f"car{i}")
            base = self._sadd(base, self._smul(n0, self._k(esz), f"can{i}"),
                              f"cac{i}")
            if is16:
                row = self.if_.narrow_f32(row, ty)
            self._vstore_unit(base, row, 8, v0)

    # =====================================================================
    # The vector-FP32 path (fp32 IEEE and bf16)
    # =====================================================================
    def emit_vector(self) -> dict:
        if_ = self.if_
        spec, plan = self.spec, self.plan
        loc = spec.loc
        ws = if_.ws(loc)
        chunk = min(plan.vector_chunk, spec.block_n)
        lmul = plan.vector_chunk_lmul
        while chunk * 32 > 1024 * lmul:      # the chunk fits the group
            lmul *= 2
        f32 = mir.VectorType(32, lmul, "float")
        a_rec, b_rec = spec.a_rec, spec.b_rec
        res_rec, acc_rec = spec.res_rec, spec.acc_rec
        M, N, K = self.M, self.N, self.K
        # the lane ids for the N-tail masks
        vid = self._vid(chunk, "vvid")
        self.if_.region(32, lmul, chunk, loc)
        zero = self._splat(self._k32(0), f32, "vz")

        # the row loop
        mf = if_.loop(self._k(0), self._k(M), [], loc, if_.tag("vm"))
        m = mf.params[0]
        # the chunk loop
        cf = if_.loop(self._k(0), self._k(N), [], loc, if_.tag("vc"))
        c = cf.params[0]
        nrem = self._ssub(self._k(N), c, "vnr")
        mask = self._mask_lt(vid, self._narrow32(nrem, "vnr32"), "vmk", chunk)
        v0 = self._to_v0(mask, "vv0")
        # the accumulator chunk: the acc region row (chain) or zeros
        if plan.acc_mode == "chain":
            base = self._sadd(ws, self._k(acc_rec["offset"]), "vab")
            base = self._sadd(base, self._smul(m, self._k(N * 4), "vam"),
                              "var")
            base = self._sadd(base, self._smul(c, self._k(4), "vac"),
                              "vao")
            acc = self._vload_unit(base, f32, chunk, v0, "val")
            acc = self._vsel(v0, acc, zero, "vaz")
        else:
            acc = zero
        # the K loop: acc += A[m, k] * B[k, c:c+chunk] (IEEE fp32 FMA;
        # the bf16 operands' regions hold their exact fp32 widening)
        kf = if_.loop(self._k(0), self._k(K), [acc], loc, if_.tag("vk"))
        k = kf.params[0]
        a_base = self._sadd(ws, self._k(a_rec["offset"]), "vkb")
        a_base = self._sadd(a_base, self._smul(m, self._k(K * 4), "vkm"),
                            "vkr")
        a_off = self._smul(k, self._k(4), "vko")
        a_addr = self._sadd(a_base, a_off, "vae")
        a_mk = self._sload(a_addr, 0, 32, "sext", "vka")
        b_base = self._sadd(ws, self._k(b_rec["offset"]), "vbb")
        b_base = self._sadd(b_base, self._smul(k, self._k(N * 4), "vbkr"),
                            "vbr")
        b_base = self._sadd(b_base, self._smul(c, self._k(4), "vbc"), "vbo")
        b_row = self._vload_unit(b_base, f32, chunk, v0, "vbl")
        b_row = self._vsel(v0, b_row, zero, "vbz")
        a_splat = self._splat(a_mk, f32, "vbs")
        acc2 = if_.emit(mir.MOp(
            "vfmacc", [b_row, a_splat, kf.params[1]],
            [self.if_.vreg(f32, hint="vfa", loc=loc)], loc=loc))
        k2 = self._sadd(k, self._k(1), "vk2")
        if_.close(kf, [k2, acc2], loc)
        # the result-region store (masked at the N tail)
        r_base = self._sadd(ws, self._k(res_rec["offset"]), "vrb")
        r_base = self._sadd(r_base, self._smul(m, self._k(N * 4), "vrm"),
                            "vrr")
        r_base = self._sadd(r_base, self._smul(c, self._k(4), "vrc"), "vro")
        self._vstore_unit(r_base, kf.exit.params[1], chunk, v0)
        c2 = self._sadd(c, self._k(chunk), "vc2")
        if_.close(cf, [c2], loc)
        m2 = self._sadd(m, self._k(1), "vm2")
        if_.close(mf, [m2], loc)
        return {"path": "vector-fp32", "vector_chunk": chunk,
                "ieee": plan.ieee,
                "bf16_gap": plan.bf16_gap}


def _tile_opcode_for_plan_breadth(plan) -> str:
    if plan.path != "ime":
        raise MatrixLoweringError(
            None, "dot", "the vector-FP32 path emits no tile instruction")
    if plan.family.key == "fp16":
        return "vfwmadot"
    suffix = plan.family.suffix_for(plan.a_signed, plan.b_signed)
    return {"": "vmdot", "u": "vmdotu", "us": "vmdotus",
            "su": "vmdotsu"}[suffix]


def emit_composed_dot(iface, spec: ComposedDotSpec) -> dict:
    """Emit one composed-path dot segment between the vectorize passes.

    Returns the segment's observability record (the plan's path, the
    mnemonic, the tile/chunk counts -- the counter the module meta
    carries)."""
    low = _Composed(iface, spec)
    if low.ime:
        if spec.stage_off is None:
            raise MatrixLoweringError(
                spec.loc, "dot",
                "the IME tile pipeline needs its staging area reserved in "
                "the private workspace (the lowering's accounting and the "
                "segment disagree)")
        return low.emit_ime()
    return low.emit_vector()
