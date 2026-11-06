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

from a100c.ir import mir

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
    ("vector transcendental instructions (exp/log/sin/cos/erf/floor/ceil)",
     "RVV 1.0 has no vector transcendental forms; the math-ops lane calls "
     "the declared sysroot's libm per element through the vmath expansion "
     "(a negative target fact that fixes the lowering, not folklore)"),
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
    # sign-extended; the w forms re-establish that invariant).  and/or/xor
    # have NO *w forms in RV64 -- and none are needed: the bitwise ops on
    # sign-extended i32 operands produce sign-extended exact i32 results
    # in the plain 64-bit form
    for width, sfx in ((64, ""), (32, "w")):
        for op, m in (("sadd", "add"), ("ssub", "sub"), ("smul", "mul"),
                      ("sdivu", "divu"), ("sshl", "sll"), ("ssra", "sra"),
                      ("srl", "srl")):
            rows.append(_E(m + sfx, op, (("width", width),),
                           f"{m}{sfx} {{rd}}, {{rs1}}, {{rs2}}",
                           evidence="RV64IMAFDC (F002)"))
        for op, m in (("sand", "and"), ("sor", "or"), ("sxor", "xor")):
            rows.append(_E(m, op, (("width", width),),
                           f"{m} {{rd}}, {{rs1}}, {{rs2}}",
                           notes="no andw/orw/xorw exists; the plain form "
                                 "is exact on sign-extended i32 operands",
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
                  ("and", "vand"), ("or", "vor"), ("xor", "vxor"),
                  ("srl", "vsrl"), ("sra", "vsra"), ("sll", "vsll"),
                  # T012: the layout lane's index maps / tl.swizzle2d
                  ("sdiv", "vdiv"), ("udiv", "vdivu"),
                  ("srem", "vrem"), ("urem", "vremu")):
        rows.append(_E(m + ".vv", "vbin", (("op", op), ("fp", False)),
                       f"{m}.vv {{vd}}, {{vs2}}, {{vs1}}",
                       evidence="RVV 1.0 (F006/F026)"))
    # floating forms: the MIR arith code is the same (arith.mul on fp
    # operands); the row is selected by the operand kind
    for code, m in (("add", "vfadd"), ("sub", "vfsub"), ("mul", "vfmul"),
                    ("fdiv", "vfdiv")):
        rows.append(_E(m + ".vv", "vbin", (("op", code), ("fp", True)),
                       f"{m}.vv {{vd}}, {{vs2}}, {{vs1}}",
                       evidence="RVV 1.0 (F006/F026)"))
    for op, m in (("add", "vadd"), ("mul", "vmul")):
        rows.append(_E(m + ".vx", "vbinx", (("op", op), ("fp", False)),
                       f"{m}.vx {{vd}}, {{vs2}}, {{rs1}}",
                       evidence="RVV 1.0 (F006/F026)"))
    # floating vector-vs-scalar forms (no scalar float compare exists in
    # the scalar core: splat-and-.vv is the alternative)
    for op, m in (("add", "vfadd"), ("mul", "vfmul")):
        rows.append(_E(m + ".vx", "vbinx", (("op", op), ("fp", True)),
                       f"{m}.vx {{vd}}, {{vs2}}, {{rs1}}",
                       evidence="RVV 1.0 (F006/F026)"))
    # T013: the math-ops lane's binary forms -- the philox umulhi (the
    # unsigned high half of the 2x-SEW product), the integer maximum /
    # minimum families (signed and unsigned -- the op code carries the
    # signedness) and the float maximum/minimum building blocks (the NaN
    # policies are lowering compositions over these, never this bare form)
    rows.append(_E("vmulhu.vv", "vbin", (("op", "umulhi"), ("fp", False)),
                   "vmulhu.vv {vd}, {vs2}, {vs1}",
                   notes="unsigned high multiply (philox's umulhi at the "
                         "counter width)",
                   evidence="RVV 1.0 (F006/F026)"))
    for op, m in (("max", "vmax"), ("min", "vmin"),
                  ("maxu", "vmaxu"), ("minu", "vminu")):
        rows.append(_E(m + ".vv", "vbin", (("op", op), ("fp", False)),
                       f"{m}.vv {{vd}}, {{vs2}}, {{vs1}}",
                       notes="integer maximum/minimum (the MIR op code "
                             "carries the signedness)",
                       evidence="RVV 1.0 (F006/F026)"))
    for op, m in (("fmax", "vfmax"), ("fmin", "vfmin")):
        rows.append(_E(m + ".vv", "vbin", (("op", op), ("fp", True)),
                       f"{m}.vv {{vd}}, {{vs2}}, {{vs1}}",
                       notes="float maximum/minimum building block; the "
                             "maxnum/maximum NaN policies are lowering "
                             "compositions over this form",
                       evidence="RVV 1.0 (F006/F026)"))
    rows.append(_E("vfmacc.vv", "vfmacc", (),
                   "vfmacc.vv {vd}, {vs1}, {vs2}",
                   notes="vd = +(vs1 * vs2) + vd, one rounding (tl.fma; "
                         "the third operand is pre-copied into vd)",
                   evidence="RVV 1.0 (F006/F026)"))
    rows.append(_E("vmor.mm", "vmor", (), "vmor.mm {vd}, {vs2}, {vs1}",
                   notes="mask OR (the any-NaN disjunction of the "
                         "propagate_nan compositions)",
                   evidence="RVV 1.0 (F006)"))
    # the libm-backed transcendentals: one scalar libm call per element at
    # the region's lane count; the emitter expands the sequence (buffer
    # spill, element loop, reload) and the form below is the selection
    # record (the call itself carries [opN] attribution)
    for fn in sorted(mir.MATH_LIBM_FNS):
        rows.append(_E(f"call {fn}", "vmath", (("fn", fn),),
                       f"call {fn}",
                       notes="libm-backed elementwise math (the emitter's "
                             "buffer/loop expansion; -lm links the "
                             "declared sysroot's libm)",
                       evidence="sysroot libm probed under the pinned QEMU "
                                "(exit 0, correct values)"))
    rows.append(_E("vfsgnjn.vv", "vunary", (("op", "fneg"),),
                   "vfsgnjn.vv {vd}, {vs2}, {vs2}",
                   notes="the real form behind the vfneg.vv pseudo",
                   evidence="RVV 1.0 (F006)"))
    # T013: the math-ops lane's direct vector forms -- the exactly-rounded
    # sqrt and the float abs (sign-bit xor with itself)
    rows.append(_E("vfsqrt.v", "vunary", (("op", "fsqrt"),),
                   "vfsqrt.v {vd}, {vs2}",
                   notes="IEEE round-to-nearest square root (math.sqrt and "
                         "math.sqrt_rn; the approximable and precise forms "
                         "coincide on this target)",
                   evidence="RVV 1.0 (F006)"))
    rows.append(_E("vfsgnjx.vv", "vunary", (("op", "fabs"),),
                   "vfsgnjx.vv {vd}, {vs2}, {vs2}",
                   notes="float absolute value (sign bits xor themselves)",
                   evidence="RVV 1.0 (F006)"))
    rows.append(_E("vnot.v", "vunary", (("op", "not"),),
                   "vnot.v {vd}, {vs2}",
                   notes="one's complement (vxor.vi -1); the uint_to_"
                         "uniform_float negation path's ~x on int blocks",
                   evidence="RVV 1.0 (F006)"))
    rows.append(_E("vfcvt.f.x.v", "vunary", (("op", "fcvt"),),
                   "vfcvt.f.x.v {vd}, {vs2}",
                   notes="signed integer to float at the same SEW",
                   evidence="RVV 1.0 (F006)"))
    # T012: the conversion matrix's same-width and widening/narrowing forms
    # (each probed under the pinned QEMU endpoint: vfcvt.x.f.v,
    # vfcvt.rtz.x.f.v, vfcvt.f.xu.v, vfcvt.rtz.xu.f.v, vfwcvt.f.f.v,
    # vfwcvt.f.x.v, vfncvt.f.f.w, vfncvt.x.f.w all executed, exit 42)
    rows.append(_E("vfcvt.rtz.x.f.v", "vunary", (("op", "fcvt.xf"),),
                   "vfcvt.rtz.x.f.v {vd}, {vs2}",
                   notes="float to signed int truncating toward zero (the "
                         "pinned fptosi semantics)",
                   evidence="probed under the pinned QEMU (exit 42)"))
    rows.append(_E("vfcvt.f.xu.v", "vunary", (("op", "fcvt.fxu"),),
                   "vfcvt.f.xu.v {vd}, {vs2}",
                   notes="unsigned integer to float at the same SEW",
                   evidence="probed under the pinned QEMU (exit 42)"))
    rows.append(_E("vfcvt.rtz.xu.f.v", "vunary", (("op", "fcvt.xuf"),),
                   "vfcvt.rtz.xu.f.v {vd}, {vs2}",
                   notes="float to unsigned int truncating toward zero",
                   evidence="probed under the pinned QEMU (exit 42)"))
    rows.append(_E("vfwcvt.f.f.v", "vfwcvt", (("op", "ff"),),
                   "vfwcvt.f.f.v {vd}, {vs2}",
                   notes="f16 -> f32 widening (exact)",
                   evidence="probed under the pinned QEMU (exit 42)"))
    rows.append(_E("vfwcvt.f.x.v", "vfwcvt", (("op", "fx"),),
                   "vfwcvt.f.x.v {vd}, {vs2}",
                   notes="i16 -> f32 widening",
                   evidence="probed under the pinned QEMU (exit 42)"))
    rows.append(_E("vfwcvt.f.xu.v", "vfwcvt", (("op", "fxu"),),
                   "vfwcvt.f.xu.v {vd}, {vs2}",
                   notes="u16 -> f32 widening",
                   evidence="RVV 1.0 (F006)"))
    rows.append(_E("vfncvt.f.f.w", "vfncvt", (("op", "ff"),),
                   "vfncvt.f.f.w {vd}, {vs2}",
                   notes="f32 -> f16 narrowing (round to nearest even, the "
                         "pinned default downcast rounding)",
                   evidence="probed under the pinned QEMU (exit 42)"))
    rows.append(_E("vfncvt.rtz.f.f.w", "vfncvt", (("op", "ffrtz"),),
                   "vfncvt.rtz.f.f.w {vd}, {vs2}",
                   notes="f32 -> f16 narrowing, round toward zero (the "
                         "fp_downcast_rounding='rtz' form)",
                   evidence="RVV 1.0 (F006)"))
    rows.append(_E("vfncvt.rtz.x.f.w", "vfncvt", (("op", "xf"),),
                   "vfncvt.rtz.x.f.w {vd}, {vs2}",
                   notes="f32 -> i16 narrowing, truncating toward zero",
                   evidence="probed under the pinned QEMU (vfncvt.x.f.w "
                            "family, exit 42)"))
    rows.append(_E("vfncvt.rtz.xu.f.w", "vfncvt", (("op", "xuf"),),
                   "vfncvt.rtz.xu.f.w {vd}, {vs2}",
                   notes="f32 -> u16 narrowing, truncating toward zero",
                   evidence="RVV 1.0 (F006)"))
    rows.append(_E("vmv.v.v", "vmovv", (),
                   "vmv.v.v {vd}, {vs2}",
                   notes="the bit-level reinterpretation move (the same "
                         "SEW/LMUL, the element kind changes)",
                   evidence="RVV 1.0 (F006)"))
    # vector reductions: vd[0] = vs1[0] combine vs2's active lanes; only
    # lane 0 of vd is consumed (the merge accumulator convention)
    for (kind, fp), m in sorted(mir.VRED_KINDS.items()):
        if kind == "sum" and not fp:
            rows.append(_E("vredsum.vs", "vred",
                           (("kind", kind), ("fp", False)),
                           "vredsum.vs {vd}, {vs2}, {vs1}",
                           evidence="RVV 1.0 (F006/F026)"))
            continue
        if fp:
            rows.append(_E(f"{m}.vs", "vred",
                           (("kind", kind), ("fp", True)),
                           f"{m}.vs {{vd}}, {{vs2}}, {{vs1}}",
                           notes="floating reduction; the unordered-sum "
                                 "form regroups within the case tolerance",
                           evidence="RVV 1.0 (F006/F026)"))
            continue
        # both signednesses exist for the integer min/max reductions
        # (the index lane compares block indices: signed at non-negative
        # ranges, unsigned for the full-range forms)
        rows.append(_E(f"{m}.vs", "vred",
                       (("kind", kind), ("fp", False),
                        ("unsigned", False)),
                       f"{m}.vs {{vd}}, {{vs2}}, {{vs1}}",
                       evidence="RVV 1.0 (F006/F026)"))
        rows.append(_E(f"{m}u.vs", "vred",
                       (("kind", kind), ("fp", False),
                        ("unsigned", True)),
                       f"{m}u.vs {{vd}}, {{vs2}}, {{vs1}}",
                       evidence="RVV 1.0 (F006/F026)"))
    rows.append(_E("vmv.x.s", "vextract", (),
                   "vmv.x.s {rd}, {vs2}",
                   notes="extract lane 0 to a GPR (raw bits for floats)",
                   evidence="RVV 1.0 (F006)"))
    rows.append(_E("vmand.mm", "vmand", (),
                   "vmand.mm {vd}, {vs2}, {vs1}",
                   notes="mask AND (the arg-merge tie condition); the .mm "
                         "form is the mask-mask assembly suffix of RVV 1.0",
                   evidence="RVV 1.0 (F006)"))
    rows.append(_E("vmxor.mm", "vmxor", (),
                   "vmxor.mm {vd}, {vs2}, {vs1}",
                   notes="mask XOR (the boolean block's i1 arithmetic, "
                         "T033: arith.add on two int1 block tensors is "
                         "addition mod 2 -- exactly lane xor -- the "
                         "fused_pool_reduce broadcast idiom; cmp.ne over "
                         "masks is the same form)",
                   evidence="RVV 1.0 (F006); as -march=rv64gcv probe: "
                            "vmxor.mm accepted"))
    rows.append(_E("vmnand.mm", "vmnot", (),
                   "vmnand.mm {vd}, {vs2}, {vs2}",
                   notes="mask complement (the boolean block's ~m: "
                         "logical.not / bit.invert on an i1 block, T024); "
                         "the pinned toolchain's binutils has no vmnot.mm "
                         "pseudo (probed: unrecognized opcode), so the "
                         "complement is vmnand(m, m) = ~(m & m) -- exact "
                         "for the 0/1 mask lanes",
                   evidence="RVV 1.0 (F006); as -march=rv64gcv probe: "
                            "vmnand.mm accepted, vmnot.mm unrecognized"))
    # integer vector compares (vv): vd = vs2 <pred> vs1.  The ORDERED
    # signed rows constrain unsigned=False (T013: a uint-kind operand must
    # select the unsigned form -- before the constraint the matcher saw
    # both rows and the randint offsets' uint64 compares hit the
    # ambiguity); eq/ne are sign-agnostic and stay unconstrained
    for pred, m, swap in (("lt", "vmslt", False), ("le", "vmsle", False),
                          ("gt", "vmslt", True), ("ge", "vmsle", True)):
        rows.append(_E(m + ".vv", "vcmp",
                       (("pred", pred), ("fp", False), ("unsigned", False)),
                       f"{m}.vv {{vd}}, {{vs2}}, {{vs1}}", swap_operands=swap,
                       evidence="RVV 1.0 (F006/F026)"))
    for pred, m in (("eq", "vmseq"), ("ne", "vmsne")):
        rows.append(_E(m + ".vv", "vcmp", (("pred", pred), ("fp", False)),
                       f"{m}.vv {{vd}}, {{vs2}}, {{vs1}}",
                       notes="sign-agnostic equality",
                       evidence="RVV 1.0 (F006/F026)"))
    for pred, m, swap in (("lt", "vmsltu", False), ("le", "vmsleu", False),
                          ("gt", "vmsltu", True), ("ge", "vmsleu", True)):
        rows.append(_E(m + ".vv", "vcmp",
                       (("pred", pred), ("fp", False), ("unsigned", True)),
                       f"{m}.vv {{vd}}, {{vs2}}, {{vs1}}", swap_operands=swap,
                       evidence="RVV 1.0 (F006/F026)"))
    # floating compares (vv): only eq/ne/lt/le exist (no gt/ge forms);
    # gt/ge realize by swapping the operands (gt(a,b) == lt(b,a))
    for pred, m in (("lt", "vmflt"), ("le", "vmfle"),
                    ("eq", "vmfeq"), ("ne", "vmfne")):
        rows.append(_E(m + ".vv", "vcmp", (("pred", pred), ("fp", True)),
                       f"{m}.vv {{vd}}, {{vs2}}, {{vs1}}",
                       evidence="RVV 1.0 (F006/F026)"))
    for pred, m, swap in (("gt", "vmflt", True), ("ge", "vmfle", True)):
        rows.append(_E(m + ".vv", "vcmp", (("pred", pred), ("fp", True)),
                       f"{m}.vv {{vd}}, {{vs2}}, {{vs1}}",
                       swap_operands=swap,
                       notes="no floating gt/ge form exists (see "
                             "ABSENT_FORMS); the swapped-operand lt/le "
                             "realizes it",
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
