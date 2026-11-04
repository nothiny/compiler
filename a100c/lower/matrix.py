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
from a100c.plan import tiles as tiles_mod
from a100c.plan.tiles import DotPlan
from a100c.target import TargetModel

__all__ = [
    "MatrixLoweringError", "refuse_matrix", "IME_OPERAND_CONTRACT",
    "MatrixOptions", "DotBinding", "dot_binding", "lower_dot",
    "verify_module", "verify", "IME_OPCODES", "ime_repertoire_rows",
    "IMEInvariant",
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

IME_OPCODES = frozenset(_TILE_OPCODES) | frozenset(_MEM_OPCODES)

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
