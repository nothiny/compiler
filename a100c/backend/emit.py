"""Emission (BE-EMISSION): the complete program-level RISC-V assembly.

Mechanical and traceable: every emitted construct traces to a selected MIR
op (each instruction line carries the op index and the source location of
the TIR construct that produced it -- IR-OBSERVABILITY through the last
stage).  The artifact is checked against MIR invariants before the external
assembler sees it (the driver verifies the module first), so a rejection
from as/ld is reported with the originating construct.

Program shape (a100rt.h, F046/F043):
  - ``operator_workspace_private/shared`` -- the workspace queries;
  - ``operator_entry(launch)`` -- prologue (ra + the allocated callee-saved
    registers, frame for spill slots), the launch pointer moved from a0,
    one label per MIR block, the epilogue.
Branch arguments become explicit parallel moves before the jump (cycle
breaking through a stack scratch slot); calls move the launch pointer into
a0 and clobber the caller-saved registers (the allocator's avoid-sets
guarantee no live value sits in them).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from a100c.backend.allocate import Allocation, CALLER_SAVED, GPR_NAMES
from a100c.backend.select import Selected, select
from a100c.ir import mir
from a100c.target import TargetModel

__all__ = ["EmissionError", "EmittedProgram", "emit_assembly"]


class EmissionError(Exception):
    def __init__(self, loc, construct: str, message: str):
        super().__init__(f"emission: {construct}: {message}"
                         + (f" (at {loc})" if loc else ""))
        self.loc = loc
        self.construct = construct
        self.message = message


@dataclass
class EmittedProgram:
    text: str
    frame_bytes: int
    saved_regs: List[str] = field(default_factory=list)
    stats: Dict[str, object] = field(default_factory=dict)


def _fmt(template: str, values: Dict[str, str]) -> str:
    out = template
    for key, value in values.items():
        out = out.replace("{" + key + "}", value)
    return out


class _Emitter:
    def __init__(self, module: mir.MModule, selection: Dict[int, Selected],
                 allocation: Allocation, target: TargetModel,
                 workspace: Tuple[int, int], header: List[str]):
        self.module = module
        self.selection = selection
        self.alloc = allocation
        self.target = target
        self.workspace = workspace
        self.header = header
        self.lines: List[str] = []
        self.label_of = {b.name: f".L{b.name}" for fn in module.functions
                         for b in fn.blocks}
        # frame layout
        self.slot_offsets, self.scratch_offset = self._layout()
        self.saved_regs = self._saved()
        #: the region state at the current emission position:
        #: (sew, lmul, avl) -- updated at every vsetvli whose avl operand
        #: is a materialized constant (the lowering's own discipline), so
        #: the allocator's spill/reload vtype switches can restore it
        #: (T014: a spill's vsetvli x0,x0 left the block's region at the
        #: spilled value's vtype -- the following ops ran at the WRONG
        #: SEW/LMUL, a pressure-dependent silent corruption)
        self._cur_region = None
        self._const_of = {}
        for fn in module.functions:
            for b in fn.blocks:
                for mop in b.ops:
                    if mop.opcode == "sconst":
                        for r in mop.results:
                            self._const_of[r.rid] = int(
                                mop.attrs["value"])

    # -- frame ------------------------------------------------------------
    def _layout(self) -> Tuple[Dict[int, int], Optional[int]]:
        """The frame layout (offsets from the adjusted sp).

        T029: the small, always-accessed items (saved registers, the
        move scratch, the 8-byte scalar slots, the spill/reload address
        scratch, the libm slots) sit at LOW offsets; only the vector
        spill slots -- up to 1024 B per m8 group -- may push past the
        12-bit immediate boundary of the sp-relative forms, and every
        access that can reach them goes through the offset-safe
        address materialization (:meth:`_sp_addr`), so a frame of any
        size the allocator builds still assembles.
        """
        # [ra + saved registers] at the bottom
        self._saved_base = 0
        offset = 8 * (1 + len(self._saved()))
        # [the parallel-move GPR scratch slot]
        scratch = None
        if self._needs_scratch():
            scratch = offset
            offset += 8
        # T014: the spill/reload address scratch -- a dedicated 8-byte
        # slot so a fully-allocated GPR file can still spill (any
        # caller-saved register saves there, serves as the address, and
        # restores)
        self._spill_addr_slot = offset
        offset += 8
        # T013: the libm element loops' buffer and pointer/counter slots.
        # The buffer holds one vector of the widest vmath element (the
        # operand spills there, the scalar loop rewrites it in place --
        # every libm function in the set is pure in its single argument --
        # and the result reloads from it).
        self._math_slots: Dict[str, int] = {}
        buf = self._math_buffer_bytes()
        if buf:
            self._math_slots["buf"] = offset
            offset += buf
            self._math_slots["ptr"] = offset
            offset += 8
            self._math_slots["cnt"] = offset
            offset += 8
        # [the 8-byte scalar spill slots]
        offsets: Dict[int, int] = {}
        for slot, size in enumerate(self.alloc.slots):
            if size == 8:
                offsets[slot] = offset
                offset += 8
        # [the vector spill slots] -- 128..1024 B each, may cross the
        # 12-bit immediate boundary
        for slot, size in enumerate(self.alloc.slots):
            if size != 8:
                offsets[slot] = offset
                offset += size
        self._frame_end = offset
        return offsets, scratch

    def _sp_addr(self, off: int, scratch: str, op: mir.MOp) -> None:
        """Materialize ``sp + off`` in ``scratch``, 12-bit safe: the plain
        addi while the offset fits its immediate, else li + add (T029:
        vector spill slots of m4/m8 groups push frames past 2047)."""
        if -2048 <= off <= 2047:
            self.emit(f"addi {scratch}, sp, {off}", op)
        else:
            self.emit(f"li {scratch}, {off}", op)
            self.emit(f"add {scratch}, {scratch}, sp", op)

    def _math_buffer_bytes(self) -> int:
        """The widest vmath operand in bytes (vl * esz), 16-byte aligned."""
        worst = 0
        for fn in self.module.functions:
            for b in fn.blocks:
                for op in b.ops:
                    if op.opcode == "vmath":
                        worst = max(worst, op.attrs["vl"]
                                    * op.attrs["sew"] // 8)
        return (worst + 15) & ~15

    def _needs_scratch(self) -> bool:
        for fn in self.module.functions:
            for b in fn.blocks:
                if b.branch_args():
                    return True
        return False

    def _saved(self) -> List[str]:
        used = {name for name in self.alloc.assignment.values()
                if not name.startswith("v")}
        return sorted((n for n in used if n not in CALLER_SAVED),
                      key=GPR_NAMES.index)

    def frame_bytes(self) -> int:
        return (self._frame_end + 15) & ~15

    # -- phys helpers -------------------------------------------------------
    def phys(self, reg: mir.VReg) -> str:
        return self.alloc.phys(reg)

    def comment(self, op: mir.MOp) -> str:
        if op.loc is None:
            return f"  # [op{op.index}]"
        return f"  # [op{op.index}] {op.loc}"

    def emit(self, text: str, op: Optional[mir.MOp] = None, note: str = "") -> None:
        suffix = ""
        if op is not None:
            suffix = self.comment(op)
        elif note:
            suffix = f"  # {note}"
        self.lines.append(text + suffix)

    # -- parallel moves -------------------------------------------------------
    def parallel_move(self, pairs: List[Tuple[mir.VReg, mir.VReg]], op: mir.MOp) -> None:
        """Move arg values into the target params' registers.

        Cycles are broken through the stack scratch slot (GPRs only; a
        vector/mask cycle is a located refusal -- the slice's branch args
        are scalars by construction).
        """
        pending: List[List] = [[self.phys(dst), self.phys(src), dst]
                               for dst, src in pairs
                               if self.phys(dst) != self.phys(src)]
        guard = 0
        while pending:
            guard += 1
            if guard > 256:
                raise EmissionError(op.loc, "branch",
                                    "parallel move did not terminate")
            moved = False
            for i, (dst, src, dstv) in enumerate(pending):
                others = {p[1] for j, p in enumerate(pending) if j != i}
                if dst not in others:
                    if src == "@scratch":
                        self.emit(f"ld {dst}, {self.scratch_offset}(sp)", op)
                    else:
                        self._emit_move(dst, src, dstv, op)
                    pending.pop(i)
                    moved = True
                    break
            if moved:
                continue
            dst, src, dstv = pending[0]
            if dstv.is_scalar():
                if self.scratch_offset is None:
                    raise EmissionError(
                        op.loc, "branch",
                        "a cyclic parallel move needs the GPR scratch slot; "
                        f"the value at {dst} cannot be cycled (located "
                        "refusal)")
                self.emit(f"sd {dst}, {self.scratch_offset}(sp)", op)
                self._emit_move(dst, src, dstv, op)
                for p in pending[1:]:
                    if p[1] == dst:
                        p[1] = "@scratch"
                pending.pop(0)
                continue
            # a vector cycle: save the destination group through a
            # register the allocation does not own, perform the move,
            # and let later readers of the saved value take it from the
            # temp (the GPR scratch-slot algorithm, vector form)
            temp = self._free_vector_reg(dstv)
            if temp is None:
                raise EmissionError(
                    op.loc, "branch",
                    "a cyclic vector move needs a free scratch register; "
                    f"the value at {dst} cannot be cycled (located "
                    "refusal)")
            self._emit_move(temp, dst, dstv, op)
            self._emit_move(dst, src, dstv, op)
            for p in pending[1:]:
                if p[1] == dst:
                    p[1] = temp
            pending.pop(0)

    def _free_vector_reg(self, dstv: mir.VReg) -> Optional[str]:
        """A vector register no allocated value owns (cycle scratch)."""
        used = set(self.alloc.assignment.values())
        span = dstv.type.lmul if dstv.is_vector() else 1
        for i in range(1, 32 - span + 1):
            group = [f"v{i + k}" for k in range(span)]
            if not any(r in used for r in group) and "v0" not in group:
                return f"v{i}"
        return None

    def _free_gpr(self) -> Optional[str]:
        """A CALLER-SAVED GPR no allocated value owns and no ABI role
        reserves.

        Only caller-saved registers qualify (t0-t6, a1-a7): a callee-saved
        register the allocation does not own still belongs to the RUNTIME
        caller (pool.c's worker loop holds live values across
        operator_entry), and using it without saving corrupts that state
        -- the probe-found hang of the first vmath emission.  a0 carries
        call arguments, so it never serves as a scratch either."""
        regs = self._free_gprs(1)
        return regs[0] if regs else None

    def _free_gprs(self, count: int) -> Optional[List[str]]:
        """``count`` distinct caller-saved GPRs no allocated value owns
        (the same rule as :meth:`_free_gpr`; None when fewer exist)."""
        used = set(self.alloc.assignment.values())
        order = [f"t{i}" for i in range(7)] + [f"a{i}" for i in range(1, 8)]
        free = [name for name in order if name not in used]
        return free[:count] if len(free) >= count else None

    def _emit_move(self, dst: str, src: str, dstv: mir.VReg, op: mir.MOp) -> None:
        if dstv.is_scalar():
            self.emit(f"mv {dst}, {src}", op)
        elif dstv.is_mask():
            self.emit(f"vmv1r.v {dst}, {src}", op)
        elif dstv.type.lmul == 1:
            self.emit(f"vmv.v.v {dst}, {src}", op)
        elif dstv.type.lmul in (2, 4, 8):
            # whole-register-group moves (T029: the allocator's m4/m8
            # groups -- the fp32 dot's 128-lane chunk class)
            self.emit(f"vmv{dstv.type.lmul}r.v {dst}, {src}", op)
        else:  # pragma: no cover - the verifier restricts LMUL to 1..8
            raise EmissionError(op.loc, "branch",
                                f"vector move at LMUL {dstv.type.lmul} "
                                "not emitted")

    # -- per-op emission --------------------------------------------------------
    def op_text(self, op: mir.MOp) -> List[str]:
        selected = self.selection.get(op.index)
        if selected is None:
            raise EmissionError(op.loc, op.opcode,
                                "op was never selected (selection must run "
                                "before emission)")
        entry = selected.entry
        ops = op.operands
        res = op.results
        values: Dict[str, str] = {}
        if res:
            values["rd"] = self.phys(res[0])
            values["vd"] = self.phys(res[0])
        if ops:
            values["rs1"] = self.phys(ops[0])
            values["vs2"] = self.phys(ops[0])
        if len(ops) > 1:
            values["rs2"] = self.phys(ops[1])
            values["vs1"] = self.phys(ops[1])
        if len(ops) > 2:
            values["vs3"] = self.phys(ops[2])
        if op.opcode == "sconst":
            values["imm"] = str(op.attrs["value"])
        elif op.opcode in ("sload", "sstore"):
            values["imm"] = str(op.attrs["offset"])
        elif op.opcode == "vsetvli":
            values["sew"] = str(op.attrs["sew"])
            values["lmul"] = str(op.attrs["lmul"])
            values["policy"] = op.attrs["policy"]
            avl = self._const_of.get(op.operands[0].rid) \
                if op.operands else None
            self._cur_region = (op.attrs["sew"], op.attrs["lmul"], avl)
        elif op.opcode in ("sspill", "sreload", "vspill", "vreload"):
            values["slot"] = str(self.slot_offsets[op.attrs["slot"]])
        text = _fmt(entry.form, values)
        if entry.swap_operands:
            # pred gt/ge implemented by swapping the compare operands
            text = _fmt(entry.form, {**values, "vs2": values.get("vs1", ""),
                                     "vs1": values.get("vs2", ""),
                                     "rs2": values.get("rs1", ""),
                                     "rs1": values.get("rs2", "")})
        return [text]

    def emit_op(self, op: mir.MOp) -> None:
        code = op.opcode
        if code == "sstore":
            # operands: base, value -> rs1 = base, rs2 = value
            selected = self.selection[op.index]
            values = {"rs1": self.phys(op.operands[0]),
                      "rs2": self.phys(op.operands[1]),
                      "imm": str(op.attrs["offset"])}
            self.emit(_fmt(selected.entry.form, values), op)
            return
        if code == "vstoreix":
            selected = self.selection[op.index]
            values = {"rs1": self.phys(op.operands[0]),
                      "vs2": self.phys(op.operands[1]),
                      "vs3": self.phys(op.operands[2])}
            text = _fmt(selected.entry.form, values)
            if len(op.operands) == 4:
                text += ", v0.t"
            self.emit(text, op)
            return
        if code == "vloadix":
            selected = self.selection[op.index]
            values = {"rs1": self.phys(op.operands[0]),
                      "vs2": self.phys(op.operands[1]),
                      "vd": self.phys(op.results[0])}
            text = _fmt(selected.entry.form, values)
            if len(op.operands) == 3:
                text += ", v0.t"
            self.emit(text, op)
            return
        if code == "vsel":
            selected = self.selection[op.index]
            values = {"vd": self.phys(op.results[0]),
                      "vs1": self.phys(op.operands[1]),   # then
                      "vs2": self.phys(op.operands[2])}   # else
            self.emit(_fmt(selected.entry.form, values), op)
            return
        if code == "vmovmask":
            selected = self.selection[op.index]
            values = {"vs2": self.phys(op.operands[0])}
            self.emit(_fmt(selected.entry.form, values), op)
            return
        if code == "vcmp" or code == "vcmpx":
            selected = self.selection[op.index]
            swap = selected.entry.swap_operands
            if code == "vcmp":
                a, b = self.phys(op.operands[0]), self.phys(op.operands[1])
            else:
                a, b = self.phys(op.operands[0]), self.phys(op.operands[1])
            values = {"vd": self.phys(op.results[0]),
                      "vs2": b if swap else a, "vs1": a if swap else b,
                      "rs1": b if swap else a}
            self.emit(_fmt(selected.entry.form, values), op)
            return
        if code == "vwaddx0":
            selected = self.selection[op.index]
            values = {"vd": self.phys(op.results[0]),
                      "vs2": self.phys(op.operands[0])}
            self.emit(_fmt(selected.entry.form, values), op)
            return
        if code == "vpopc":
            selected = self.selection[op.index]
            values = {"rd": self.phys(op.results[0]),
                      "vs2": self.phys(op.operands[0])}
            self.emit(_fmt(selected.entry.form, values), op)
            return
        if code == "vbinx":
            selected = self.selection[op.index]
            values = {"vd": self.phys(op.results[0]),
                      "vs2": self.phys(op.operands[0]),
                      "rs1": self.phys(op.operands[1])}
            self.emit(_fmt(selected.entry.form, values), op)
            return
        if code in ("vunit_load", "vunit_store"):
            # unit-stride vector memory at the region's SEW; the masked
            # forms append v0.t (inactive lanes perform no access)
            selected = self.selection[op.index]
            values = {"rs1": self.phys(op.operands[0])}
            if code == "vunit_load":
                values["vd"] = self.phys(op.results[0])
            else:
                values["rs2"] = self.phys(op.operands[1])
            text = _fmt(selected.entry.form, values)
            masked = len(op.operands) == (2 if code == "vunit_load" else 3)
            if masked:
                text += ", v0.t"
            self.emit(text, op)
            return
        if code == "sfence":
            selected = self.selection[op.index]
            values = {"pred": op.attrs["pred"],
                      "succ": op.attrs["succ"]}
            self.emit(_fmt(selected.entry.form, values), op)
            return
        if code == "vunary":
            selected = self.selection[op.index]
            values = {"vd": self.phys(op.results[0]),
                      "vs2": self.phys(op.operands[0])}
            self.emit(_fmt(selected.entry.form, values), op)
            return
        if code == "callbarrier":
            launch = self.phys(op.operands[0])
            if launch != "a0":
                self.emit(f"mv a0, {launch}", op)
            self.emit("call a100rt_stage_barrier", op)
            return
        if code == "vmath":
            self._emit_vmath(op)
            return
        if code == "vfmacc":
            # vd = z pre-copied, then vd += x * y (one rounding; the
            # third operand legitimately shares vd's register)
            vd = self.phys(op.results[0])
            z = self.phys(op.operands[2])
            x = self.phys(op.operands[0])
            y = self.phys(op.operands[1])
            if vd != z:
                lmul = op.results[0].type.lmul
                if lmul == 1:
                    self.emit(f"vmv.v.v {vd}, {z}", op)
                elif lmul in (2, 4, 8):
                    # whole-register-group copies (T029: the m4/m8 chunk
                    # classes copy as groups)
                    self.emit(f"vmv{lmul}r.v {vd}, {z}", op)
                else:  # pragma: no cover - verifier restricts LMUL
                    raise EmissionError(op.loc, "vfmacc",
                                        f"vfmacc pre-copy at LMUL {lmul} "
                                        "not emitted")
            self.emit(f"vfmacc.vv {vd}, {x}, {y}", op)
            return
        if code == "br":
            args = list(op.attrs.get("args", ()))
            self.parallel_move(list(zip(self._params(op.attrs["target"]),
                                        args)), op)
            self.emit(f"j {self.label_of[op.attrs['target']]}", op)
            return
        if code == "brc":
            true_args = list(op.attrs.get("true_args", ()))
            false_args = list(op.attrs.get("false_args", ()))
            tt = op.attrs["true_target"]
            ft = op.attrs["false_target"]
            stub = f".Lbrc{op.index}_true"
            # The condition is read first; each edge's argument moves run
            # only on that edge (a shared move sequence before the branch
            # would let one edge's cycle-breaking clobber the other edge's
            # sources -- probe-found on the multi-program grid case).
            self.emit(f"bne {self.phys(op.operands[0])}, zero, {stub}", op)
            self.parallel_move(list(zip(self._params(ft), false_args)), op)
            self.emit(f"j {self.label_of[ft]}", op)
            self.emit(f"{stub}:", op)
            self.parallel_move(list(zip(self._params(tt), true_args)), op)
            self.emit(f"j {self.label_of[tt]}", op)
            return
        if code == "ret":
            self.emit_epilogue(op)
            return
        if code == "sspill":
            # allocator-inserted (never selected: selection runs before
            # allocation); the form is the allocator's own, matching
            # the repertoire row.  T029: a slot past the 12-bit
            # immediate addresses through the spill-address scratch
            off = self.slot_offsets[op.attrs["slot"]]
            if off <= 2047:
                values = {"rs2": self.phys(op.operands[0]),
                          "slot": str(off)}
                self.emit(_fmt("sd {rs2}, {slot}(sp)", values), op)
            else:
                scratch, epilogue = self._spill_addr_gpr(op)
                if epilogue:
                    self.emit(f"sd {scratch}, "
                              f"{self._spill_addr_slot}(sp)", op)
                self._sp_addr(off, scratch, op)
                self.emit(f"sd {self.phys(op.operands[0])}, "
                          f"0({scratch})", op)
                for line in epilogue:
                    self.emit(line, op)
            return
        if code == "sreload":
            off = self.slot_offsets[op.attrs["slot"]]
            if off <= 2047:
                values = {"rd": self.phys(op.results[0]),
                          "slot": str(off)}
                self.emit(_fmt("ld {rd}, {slot}(sp)", values), op)
            else:
                scratch, epilogue = self._spill_addr_gpr(op)
                if epilogue:
                    self.emit(f"sd {scratch}, "
                              f"{self._spill_addr_slot}(sp)", op)
                self._sp_addr(off, scratch, op)
                self.emit(f"ld {self.phys(op.results[0])}, "
                          f"0({scratch})", op)
                for line in epilogue:
                    self.emit(line, op)
            return
        if code == "sconst" and op.index not in self.selection:
            # allocator-inserted rematerialization (T029: never selected
            # -- selection runs before allocation); the repertoire's own
            # li form
            values = {"rd": self.phys(op.results[0]),
                      "imm": str(op.attrs["value"])}
            self.emit(_fmt("li {rd}, {imm}", values), op)
            return
        if code == "vspill":
            sew, lmul = op.attrs["sew"], op.attrs["lmul"]
            off = self.slot_offsets[op.attrs["slot"]]
            saved_region = self._cur_region
            self.emit(f"vsetvli x0, x0, e{sew}, m{lmul}, ta, ma", op)
            # vector unit-stride accesses take a bare base register (no
            # immediate offset form exists): materialize sp+off in a
            # scratch GPR (a free one, or any caller-saved one saved to
            # the dedicated slot first -- T014: a fully-allocated GPR
            # file must still spill; T029: the offset-safe form -- the
            # m4/m8 group slots push frames past the 12-bit immediate)
            scratch, epilogue = self._spill_addr_gpr(op)
            if epilogue:
                self.emit(f"sd {scratch}, {self._spill_addr_slot}(sp)", op)
            self._sp_addr(off, scratch, op)
            self.emit(f"vse{sew}.v {self.phys(op.operands[0])}, "
                      f"({scratch})", op)
            for line in epilogue:
                self.emit(line, op)
            self._restore_region(saved_region, op)
            return
        if code == "vreload":
            sew, lmul = op.attrs["sew"], op.attrs["lmul"]
            off = self.slot_offsets[op.attrs["slot"]]
            saved_region = self._cur_region
            self.emit(f"vsetvli x0, x0, e{sew}, m{lmul}, ta, ma", op)
            scratch, epilogue = self._spill_addr_gpr(op)
            if epilogue:
                self.emit(f"sd {scratch}, {self._spill_addr_slot}(sp)", op)
            self._sp_addr(off, scratch, op)
            self.emit(f"vle{sew}.v {self.phys(op.results[0])}, "
                      f"({scratch})", op)
            for line in epilogue:
                self.emit(line, op)
            self._restore_region(saved_region, op)
            return
        # generic template path (sconst, sload, smove, swext, sbin, s2v, vid,
        # vsetvli, vbin, vbinx)
        for text in self.op_text(op):
            self.emit(text, op)

    def _spill_addr_gpr(self, op: mir.MOp) -> Tuple[str, List[str]]:
        """A GPR usable as a spill/reload address: a free caller-saved
        one when it exists, else any caller-saved one saved to the
        dedicated slot first (and restored by the returned epilogue)."""
        free = self._free_gpr()
        if free is not None:
            return free, []
        order = [f"t{i}" for i in range(7)] + [f"a{i}" for i in range(1, 8)]
        reg = order[0]
        return reg, [f"ld {reg}, {self._spill_addr_slot}(sp)"]

    def _restore_region(self, region, op: mir.MOp) -> None:
        """Re-establish the region a spill/reload vtype switch displaced
        (T014): ``vsetivli x0, <avl>, e<sew>, m<lmul>`` restores both the
        vtype and the vl.  A region whose avl is not a materialized
        constant cannot be restored -- a located refusal (never a silent
        wrong region)."""
        if region is None:
            return
        sew, lmul, avl = region
        if avl is None:
            raise EmissionError(op.loc, "vspill",
                                "the displaced region's vl is not a "
                                "materialized constant; the spill cannot "
                                "restore it (a located refusal)")
        if 0 <= int(avl) <= 31:
            self.emit(f"vsetivli x0, {int(avl)}, e{int(sew)}, "
                      f"m{int(lmul)}, ta, ma", op)
        else:
            # the CSR-immediate form's avl is 5 bits: a wider vl restores
            # through the register form (li scratch, avl; vsetvli x0,
            # scratch) -- the address scratch GPR serves (it is dead at
            # this point: the spill's own address use has completed)
            scratch, epilogue = self._spill_addr_gpr(op)
            if epilogue:
                self.emit(f"sd {scratch}, {self._spill_addr_slot}(sp)",
                          op)
            self.emit(f"li {scratch}, {int(avl)}", op)
            self.emit(f"vsetvli x0, {scratch}, e{int(sew)}, "
                      f"m{int(lmul)}, ta, ma", op)
            for line in epilogue:
                self.emit(line, op)
        self._cur_region = region

    def _params(self, block_name: str) -> List[mir.VReg]:
        for fn in self.module.functions:
            for b in fn.blocks:
                if b.name == block_name:
                    return list(b.params)
        raise EmissionError(None, "branch", f"unknown block {block_name}")

    # -- T013: the libm element loop ---------------------------------------
    def _emit_vmath(self, op: mir.MOp) -> None:
        """One libm-backed elementwise math op: the operand spills to the
        frame buffer, a scalar loop applies the function per element (the
        argument in fa0, exactly the psABI float/double convention) and
        the result reloads as a vector at the same region.

        No register lives across the call: the element pointer and the
        remaining-element count live in frame slots and reload into free
        GPRs after every call (the call clobbers every caller-saved GPR;
        the allocator's avoid-sets keep live values out of them).  The
        libm functions are pure in their single argument, so the loop
        rewrites the buffer in place.
        """
        fn = op.attrs["fn"]
        sew = op.attrs["sew"]
        vl = op.attrs["vl"]
        esz = sew // 8
        load = {4: "flw", 8: "fld"}[esz]
        store = {4: "fsw", 8: "fsd"}[esz]
        regs = self._free_gprs(2)
        if regs is None:
            raise EmissionError(op.loc, "vmath",
                                "no free caller-saved GPR pair for the "
                                "libm loop (a located refusal)")
        scratch, second = regs
        buf = self._math_slots["buf"]
        ptr = self._math_slots["ptr"]
        cnt = self._math_slots["cnt"]
        vs = self.phys(op.operands[0])
        vd = self.phys(op.results[0])
        loop = f".Lvmath{op.index}_loop"
        done = f".Lvmath{op.index}_done"
        self.emit(f"addi {scratch}, sp, {buf}", op)
        self.emit(f"vse{sew}.v {vs}, ({scratch})", op)
        self.emit(f"sd {scratch}, {ptr}(sp)", op)
        self.emit(f"li {second}, {vl}", op)
        self.emit(f"sd {second}, {cnt}(sp)", op)
        self.emit(f"{loop}:", op)
        self.emit(f"ld {second}, {cnt}(sp)", op)
        self.emit(f"beq {second}, zero, {done}", op)
        self.emit(f"ld {scratch}, {ptr}(sp)", op)
        self.emit(f"{load} fa0, 0({scratch})", op)
        self.emit(f"call {fn}", op)
        # the call (and its PLT stub) clobbers every caller-saved GPR:
        # the element pointer reloads from its slot BEFORE the store --
        # probe-found: the PLT stub's own auipc/ld scratch registers
        # turned the stale pointer into a wild store (guest SIGSEGV)
        self.emit(f"ld {scratch}, {ptr}(sp)", op)
        self.emit(f"{store} fa0, 0({scratch})", op)
        self.emit(f"addi {scratch}, {scratch}, {esz}", op)
        self.emit(f"sd {scratch}, {ptr}(sp)", op)
        self.emit(f"ld {second}, {cnt}(sp)", op)
        self.emit(f"addi {second}, {second}, -1", op)
        self.emit(f"sd {second}, {cnt}(sp)", op)
        self.emit(f"j {loop}", op)
        self.emit(f"{done}:", op)
        self.emit(f"addi {scratch}, sp, {buf}", op)
        self.emit(f"vle{sew}.v {vd}, ({scratch})", op)

    # -- function ------------------------------------------------------------
    def emit_function(self, fn: mir.MFunction) -> None:
        frame = self.frame_bytes()
        self.emit(f"operator_entry:", note=f"fn {fn.name}")
        if frame <= 2047:
            self.emit(f"addi sp, sp, -{frame}")
        else:
            # T029: a frame past the 12-bit immediate adjusts through a
            # caller-saved scratch (t0 is dead at entry: the launch
            # pointer arrives in a0 and moves to its own register after)
            self.emit(f"li t0, {frame}")
            self.emit("sub sp, sp, t0")
        self.emit(f"sd ra, {self._saved_base}(sp)")
        offset = self._saved_base + 8
        for name in self.saved_regs:
            self.emit(f"sd {name}, {offset}(sp)")
            offset += 8
        launch_phys = self.phys(fn.params[0])
        if launch_phys != "a0":
            self.emit(f"mv {launch_phys}, a0")
        for b in fn.blocks:
            self.emit(f"{self.label_of[b.name]}:", note=f"block {b.name}")
            for op in b.ops:
                self.emit_op(op)

    def emit_epilogue(self, op: mir.MOp) -> None:
        frame = self.frame_bytes()
        self.emit(f"ld ra, {self._saved_base}(sp)", op)
        offset = self._saved_base + 8
        for name in self.saved_regs:
            self.emit(f"ld {name}, {offset}(sp)", op)
            offset += 8
        if frame <= 2047:
            self.emit(f"addi sp, sp, {frame}", op)
        else:
            # t0 is caller-saved and nothing is live at the return
            self.emit(f"li t0, {frame}", op)
            self.emit("add sp, sp, t0", op)
        self.emit("ret", op)

    # -- whole program ----------------------------------------------------------
    def render(self) -> EmittedProgram:
        out: List[str] = []
        out.extend(self.header)
        out.append("    .text")
        private, shared = self.workspace
        out.append("    .globl operator_workspace_private")
        out.append("    .type operator_workspace_private, @function")
        out.append("operator_workspace_private:")
        out.append(f"    li a0, {private}")
        out.append("    ret")
        out.append("    .size operator_workspace_private, "
                   ".-operator_workspace_private")
        out.append("    .globl operator_workspace_shared")
        out.append("    .type operator_workspace_shared, @function")
        out.append("operator_workspace_shared:")
        out.append(f"    li a0, {shared}")
        out.append("    ret")
        out.append("    .size operator_workspace_shared, "
                   ".-operator_workspace_shared")
        out.append("    .globl operator_entry")
        out.append("    .type operator_entry, @function")
        out.extend(self.lines)
        out.append("    .size operator_entry, .-operator_entry")
        out.append('    .section .note.GNU-stack,"",@progbits')
        stats = {
            "frame_bytes": self.frame_bytes(),
            "saved_regs": list(self.saved_regs),
            "emitted_lines": len([line for line in out
                                  if line.startswith("    ")
                                  and not line.strip().endswith(":")]),
        }
        return EmittedProgram(text="\n".join(out) + "\n",
                              frame_bytes=self.frame_bytes(),
                              saved_regs=list(self.saved_regs), stats=stats)


def emit_assembly(module: mir.MModule, allocation: Allocation,
                  target: TargetModel, workspace: Tuple[int, int] = (0, 0),
                  selection: Optional[Dict[int, Selected]] = None,
                  header: Optional[List[str]] = None) -> EmittedProgram:
    """Emit the complete program-level assembly for one allocated module."""
    if selection is None:
        selection = select(module)
    if header is None:
        header = [f"# a100c emitted program: {module.name}",
                  f"# source: {module.source_path}"]
    emitter = _Emitter(module, selection, allocation, target, workspace, header)
    for fn in module.functions:
        emitter.emit_function(fn)
    return emitter.render()
