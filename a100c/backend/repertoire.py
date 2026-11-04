"""The target's instruction repertoire as data (TGT-INSTRUCTION-REPERTOIRE,
MECH-TARGET-DESCRIPTION-AS-DATA).

The table is the data the selector consults: one row per implementable MIR
form with its constraints and emitted template.  Adding an operation is a
table edit, never a matcher edit; a construct with no entry is refused with
a located diagnostic, never approximated by a nearby operation.

Negative facts are recorded as data too (ABSENT_FORMS): the forms the target
does not have, with the reason -- they change the lowering and belong to the
declared surface, not to folklore.

Operand templates use {rd} {rs1} {rs2} {vs1} {vs2} {vs3} {imm} {label}
{slot}; the emitter fills them from the allocation.  ``mask_suffix`` marks
the form's dependence on the hardware working mask v0.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

__all__ = ["InstructionEntry", "Repertoire", "DEFAULT_REPERTOIRE",
           "ABSENT_FORMS"]


@dataclass(frozen=True)
class InstructionEntry:
    mnemonic: str
    opcode: str                    # the MIR opcode this row implements
    constraints: Tuple[Tuple[str, object], ...]   # must all match the op
    form: str                      # emitted template
    swap_operands: bool = False    # implement pred by swapping vs2/vs1
    mask_suffix: bool = False      # the form reads the working mask v0
    evidence: str = ""
    notes: str = ""

    def matches(self, features: Dict[str, object]) -> bool:
        for key, value in self.constraints:
            if features.get(key) != value:
                return False
        return True

    def describe(self) -> dict:
        return {"mnemonic": self.mnemonic, "opcode": self.opcode,
                "constraints": dict(self.constraints), "form": self.form,
                "swap": self.swap_operands, "mask": self.mask_suffix,
                "evidence": self.evidence, "notes": self.notes}


#: declared absences (negative facts; F026/F032/F041 and RVV 1.0)
ABSENT_FORMS: List[Tuple[str, str]] = [
    ("vmerge.vvm with a mask register other than v0",
     "the mask operand of vmerge/vmasked memory ops is architecturally v0 "
     "only (RVV 1.0); the lowering materializes the working mask with "
     "vmovmask"),
    ("vmflt.vx / vfcompare-vs-scalar",
     "no floating vector-vs-scalar compare in RVV 1.0; splat the scalar and "
     "use the .vv form"),
    ("vfneg.vv as a distinct instruction",
     "pseudo-instruction of vfsgnjn.vv vd, vs, vs; the repertoire stores the "
     "real form"),
    ("vector narrowing (i64 -> i32) arithmetic",
     "no narrowing op is needed by the slice; a narrowing form would be a "
     "new table row with its own legality, never an implicit reinterpret"),
    ("Zvvmtls (vector load/store whole-register with mask)",
     "extension absent from the target (F026); mask whole-register moves are "
     "not used"),
    ("EEW=128 vector accesses",
     "EEW range is 8..64 (F026)"),
    ("smt.* matrix instructions in the slice's selection path",
     "IME forms exist on the target (F009/F034) but no MIR matrix op is "
     "lowered by the vertical slice; matrix.py refuses the construct first"),
    ("spilled mask values (vsm/vlm stack round-trip)",
     "mask spill is not implemented; the allocator refuses when the mask "
     "file is exhausted (a bounded, located refusal)"),
]

_E = InstructionEntry


def _scalar_rows() -> List[InstructionEntry]:
    rows: List[InstructionEntry] = []
    rows.append(_E("li", "sconst", (), "li {rd}, {imm}",
                   evidence="RV64IMAFDC (F002)"))
    rows.append(_E("mv", "smove", (), "mv {rd}, {rs1}",
                   evidence="RV64IMAFDC (F002)"))
    rows.append(_E("addiw", "swext", (), "addiw {rd}, {rs1}, 0",
                   notes="re-sign-extend the low 32 bits (the strunc "
                         "legalisation)", evidence="RV64IMAFDC (F002)"))
    # loads: (width, ext) -> mnemonic
    for width, mnemonics in {64: ("ld", None), 32: ("lw", "lwu"),
                             16: ("lh", "lhu"), 8: ("lb", "lbu")}.items():
        sext, zext = mnemonics
        if sext:
            rows.append(_E(sext, "sload", (("width", width), ("ext", "sext")),
                           f"{sext} {{rd}}, {{imm}}({{rs1}})",
                           evidence="RV64IMAFDC (F002)"))
        if zext:
            rows.append(_E(zext, "sload", (("width", width), ("ext", "zext")),
                           f"{zext} {{rd}}, {{imm}}({{rs1}})",
                           evidence="RV64IMAFDC (F002)"))
    for width, m in {64: "sd", 32: "sw", 16: "sh", 8: "sb"}.items():
        rows.append(_E(m, "sstore", (("width", width),),
                       f"{m} {{rs2}}, {{imm}}({{rs1}})",
                       evidence="RV64IMAFDC (F002)"))
    # integer arithmetic: i64 plain, i32 *w forms (i32 values are held
    # sign-extended; the w forms re-establish that invariant)
    for width, sfx in ((64, ""), (32, "w")):
        for op, m in (("sadd", "add"), ("ssub", "sub"), ("smul", "mul"),
                      ("sdivu", "divu"), ("sand", "and"), ("sor", "or"),
                      ("sxor", "xor"), ("sshl", "sll"), ("ssra", "sra")):
            rows.append(_E(m + sfx, op, (("width", width),),
                           f"{m}{sfx} {{rd}}, {{rs1}}, {{rs2}}",
                           evidence="RV64IMAFDC (F002)"))
        rows.append(_E("sdiv", "sdiv", (("width", width),),
                       f"div{sfx} {{rd}}, {{rs1}}, {{rs2}}",
                       evidence="RV64IMAFDC (F002)"))
    for op, m in (("slt", "slt"), ("sltu", "sltu")):
        rows.append(_E(m, op, (), f"{m} {{rd}}, {{rs1}}, {{rs2}}",
                      notes="compares the full 64-bit registers; i32 values "
                            "are held sign-extended so this is the signed "
                            "32-bit compare",
                      evidence="RV64IMAFDC (F002)"))
    return rows


def _vector_rows() -> List[InstructionEntry]:
    rows: List[InstructionEntry] = []
    rows.append(_E("vmv.v.x", "s2v", (), "vmv.v.x {vd}, {rs1}",
                   evidence="RVV 1.0 VLEN=1024 (F006/F026)"))
    rows.append(_E("vid.v", "vid", (), "vid.v {vd}",
                   evidence="RVV 1.0 (F006)"))
    rows.append(_E("vsetvli", "vsetvli", (),
                   "vsetvli {rd}, {rs1}, e{sew}, m{lmul}, {policy}",
                   evidence="RVV 1.0 (F006)"))
    # integer forms (op names are the MIR arith codes; fp operands carry
    # fp=True in the features and select the vf* rows below)
    for op, m in (("add", "vadd"), ("sub", "vsub"), ("mul", "vmul"),
                  ("and", "vand"), ("or", "vor"), ("xor", "vxor")):
        rows.append(_E(m + ".vv", "vbin", (("op", op), ("fp", False)),
                       f"{m}.vv {{vd}}, {{vs2}}, {{vs1}}",
                       evidence="RVV 1.0 (F006/F026)"))
    # floating forms: the MIR arith code is the same (arith.mul on fp
    # operands); the row is selected by the operand kind
    for code, m in (("add", "vfadd"), ("sub", "vfsub"), ("mul", "vfmul")):
        rows.append(_E(m + ".vv", "vbin", (("op", code), ("fp", True)),
                       f"{m}.vv {{vd}}, {{vs2}}, {{vs1}}",
                       evidence="RVV 1.0 (F006/F026)"))
    for op, m in (("add", "vadd"), ("mul", "vmul")):
        rows.append(_E(m + ".vx", "vbinx", (("op", op),),
                       f"{m}.vx {{vd}}, {{vs2}}, {{rs1}}",
                       evidence="RVV 1.0 (F006/F026)"))
    rows.append(_E("vfsgnjn.vv", "vunary", (("op", "fneg"),),
                   "vfsgnjn.vv {vd}, {vs2}, {vs2}",
                   notes="the real form behind the vfneg.vv pseudo",
                   evidence="RVV 1.0 (F006)"))
    # integer vector compares (vv): vd = vs2 <pred> vs1
    for pred, m, swap in (("lt", "vmslt", False), ("le", "vmsle", False),
                          ("eq", "vmseq", False), ("ne", "vmsne", False),
                          ("gt", "vmslt", True), ("ge", "vmsle", True)):
        rows.append(_E(m + ".vv", "vcmp", (("pred", pred), ("fp", False)),
                       f"{m}.vv {{vd}}, {{vs2}}, {{vs1}}", swap_operands=swap,
                       evidence="RVV 1.0 (F006/F026)"))
    for pred, m, swap in (("lt", "vmsltu", False), ("le", "vmsleu", False),
                          ("gt", "vmsltu", True), ("ge", "vmsleu", True)):
        rows.append(_E(m + ".vv", "vcmp",
                       (("pred", pred), ("fp", False), ("unsigned", True)),
                       f"{m}.vv {{vd}}, {{vs2}}, {{vs1}}", swap_operands=swap,
                       evidence="RVV 1.0 (F006/F026)"))
    # floating compares (vv): only eq/ne/lt/le exist (no gt/ge forms)
    for pred, m in (("lt", "vmflt"), ("le", "vmfle"),
                    ("eq", "vmfeq"), ("ne", "vmfne")):
        rows.append(_E(m + ".vv", "vcmp", (("pred", pred), ("fp", True)),
                       f"{m}.vv {{vd}}, {{vs2}}, {{vs1}}",
                       evidence="RVV 1.0 (F006/F026)"))
    for pred, m, swap in (("lt", "vmslt", False), ("le", "vmsle", False),
                          ("eq", "vmseq", False), ("ne", "vmsne", False),
                          ("gt", "vmslt", True), ("ge", "vmsle", True)):
        rows.append(_E(m + ".vx", "vcmpx", (("pred", pred),),
                       f"{m}.vx {{vd}}, {{vs2}}, {{rs1}}", swap_operands=swap,
                       notes="integer only: no floating vector-vs-scalar "
                             "compare exists (see ABSENT_FORMS)",
                       evidence="RVV 1.0 (F006/F026)"))
    rows.append(_E("vmerge.vvm", "vsel", (),
                   "vmerge.vvm {vd}, {vs2}, {vs1}, v0",
                   mask_suffix=True,
                   notes="probe-verified: mask-set lanes take vs1 (the "
                         "then-value), mask-clear take vs2",
                   evidence="RVV 1.0 under the pinned QEMU (probe, T007)"))
    rows.append(_E("vmv1r.v", "vmovmask", (), "vmv1r.v v0, {vs2}",
                   notes="materializes the working mask into the "
                         "architectural v0", evidence="RVV 1.0 (F006)"))
    rows.append(_E("vwadd.vx", "vwaddx0", (("mode", "sext"),),
                   "vwadd.vx {vd}, {vs2}, x0",
                   notes="signed widening: vd = sext(vs2) + 0",
                   evidence="RVV 1.0 (probe: vwcvt.x.x.v)"))
    rows.append(_E("vwaddu.vx", "vwaddx0", (("mode", "zext"),),
                   "vwaddu.vx {vd}, {vs2}, x0",
                   notes="unsigned widening: vd = zext(vs2) + 0",
                   evidence="RVV 1.0 (F006)"))
    for eew in (64, 32, 16, 8):
        rows.append(_E(f"vluxei{eew}.v", "vloadix", (("eew", eew),),
                       f"vluxei{eew}.v {{vd}}, ({{rs1}}), {{vs2}}",
                       notes="unmasked form; the masked form appends v0.t "
                             "(inactive lanes perform no access and yield "
                             "the declared default)",
                       evidence="RVV 1.0 (probe, T007)"))
        rows.append(_E(f"vsuxei{eew}.v", "vstoreix", (("eew", eew),),
                       f"vsuxei{eew}.v {{vs3}}, ({{rs1}}), {{vs2}}",
                       notes="unmasked form; the masked form appends v0.t "
                             "(inactive lanes perform no access)",
                       evidence="RVV 1.0 (probe, T007)"))
    rows.append(_E("vcpop.m", "vpopc", (), "vcpop.m {rd}, {vs2}",
                   notes="probe-verified popcount of set mask bits",
                   evidence="RVV 1.0 (probe, T007)"))
    return rows


def _control_rows() -> List[InstructionEntry]:
    rows: List[InstructionEntry] = []
    rows.append(_E("call", "callbarrier", (), "call a100rt_stage_barrier",
                   notes="a0 must hold the launch pointer; clobbers every "
                         "caller-saved GPR (psABI, F045)",
                   evidence="a100rt.h (F046)"))
    rows.append(_E("j", "br", (), "j {label}", evidence="RV64 (F002)"))
    rows.append(_E("bne", "brc", (), "bne {rs1}, zero, {label}",
                   evidence="RV64 (F002)"))
    rows.append(_E("ret", "ret", (), "ret", evidence="RV64 (F002)"))
    rows.append(_E("sd", "sspill", (), "sd {rs2}, {slot}(sp)",
                   notes="allocator-inserted scalar spill",
                   evidence="RV64 (F002)"))
    rows.append(_E("ld", "sreload", (), "ld {rd}, {slot}(sp)",
                   notes="allocator-inserted scalar reload",
                   evidence="RV64 (F002)"))
    return rows


class Repertoire:
    """The declared operation set: rows consulted by one generic matcher."""

    def __init__(self, entries: List[InstructionEntry]):
        self.entries = list(entries)

    def find(self, opcode: str, features: Dict[str, object]) -> Optional[InstructionEntry]:
        """The generic match: constraints must be a subset of the features.

        Returns the unique matching entry, or None (a located refusal --
        never a nearest-neighbour guess).
        """
        found = [e for e in self.entries
                 if e.opcode == opcode and e.matches(features)]
        if len(found) > 1:
            raise RuntimeError(
                f"repertoire ambiguity for {opcode} {features}: "
                f"{[e.mnemonic for e in found]}")
        return found[0] if found else None

    def add(self, entry: InstructionEntry) -> None:
        """Adding an operation is a table edit (MECH-TARGET-DESCRIPTION-AS-DATA)."""
        self.entries.append(entry)

    def describe(self) -> dict:
        return {"entries": [e.describe() for e in self.entries],
                "absent": [{"form": f, "reason": r} for f, r in ABSENT_FORMS]}


DEFAULT_REPERTOIRE = Repertoire(_scalar_rows() + _vector_rows()
                                + _control_rows())
