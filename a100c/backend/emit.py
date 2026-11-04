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

    # -- frame ------------------------------------------------------------
    def _layout(self) -> Tuple[Dict[int, int], Optional[int]]:
        offset = 0
        offsets: Dict[int, int] = {}
        for slot, size in enumerate(self.alloc.slots):
            offsets[slot] = offset
            offset += size
        scratch = None
        if self._needs_scratch():
            scratch = offset
            offset += 8
        return offsets, scratch

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
        body = max(sum(self.alloc.slots), 0) + (8 if self.scratch_offset is not None else 0)
        return (body + 8 * len(self.saved_regs) + 8 + 15) & ~15

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
            if self.scratch_offset is None or not dstv.is_scalar():
                raise EmissionError(
                    op.loc, "branch",
                    "a cyclic parallel move needs the GPR scratch slot; the "
                    f"value at {dst} cannot be cycled (located refusal)")
            self.emit(f"sd {dst}, {self.scratch_offset}(sp)", op)
            self._emit_move(dst, src, dstv, op)
            for p in pending[1:]:
                if p[1] == dst:
                    p[1] = "@scratch"
            pending.pop(0)

    def _emit_move(self, dst: str, src: str, dstv: mir.VReg, op: mir.MOp) -> None:
        if dstv.is_scalar():
            self.emit(f"mv {dst}, {src}", op)
        elif dstv.is_mask():
            self.emit(f"vmv1r.v {dst}, {src}", op)
        elif dstv.type.lmul == 1:
            self.emit(f"vmv.v.v {dst}, {src}", op)
        elif dstv.type.lmul == 2:
            self.emit(f"vmv2r.v {dst}, {src}", op)
        else:  # pragma: no cover - allocator refuses m>2
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
            selected = self.selection[op.index]
            values = {"rs2": self.phys(op.operands[0]),
                      "slot": str(self.slot_offsets[op.attrs["slot"]])}
            self.emit(_fmt(selected.entry.form, values), op)
            return
        if code == "sreload":
            selected = self.selection[op.index]
            values = {"rd": self.phys(op.results[0]),
                      "slot": str(self.slot_offsets[op.attrs["slot"]])}
            self.emit(_fmt(selected.entry.form, values), op)
            return
        if code == "vspill":
            sew, lmul = op.attrs["sew"], op.attrs["lmul"]
            self.emit(f"vsetvli x0, x0, e{sew}, m{lmul}, ta, ma", op)
            self.emit(f"vse{sew}.v {self.phys(op.operands[0])}, "
                      f"{self.slot_offsets[op.attrs['slot']]}(sp)", op)
            return
        if code == "vreload":
            sew, lmul = op.attrs["sew"], op.attrs["lmul"]
            self.emit(f"vsetvli x0, x0, e{sew}, m{lmul}, ta, ma", op)
            self.emit(f"vle{sew}.v {self.phys(op.results[0])}, "
                      f"{self.slot_offsets[op.attrs['slot']]}(sp)", op)
            return
        # generic template path (sconst, sload, smove, swext, sbin, s2v, vid,
        # vsetvli, vbin, vbinx)
        for text in self.op_text(op):
            self.emit(text, op)

    def _params(self, block_name: str) -> List[mir.VReg]:
        for fn in self.module.functions:
            for b in fn.blocks:
                if b.name == block_name:
                    return list(b.params)
        raise EmissionError(None, "branch", f"unknown block {block_name}")

    # -- function ------------------------------------------------------------
    def emit_function(self, fn: mir.MFunction) -> None:
        frame = self.frame_bytes()
        self.emit(f"operator_entry:", note=f"fn {fn.name}")
        self.emit(f"addi sp, sp, -{frame}")
        self.emit(f"sd ra, {frame - 8}(sp)")
        offset = frame - 16
        for name in self.saved_regs:
            self.emit(f"sd {name}, {offset}(sp)")
            offset -= 8
        launch_phys = self.phys(fn.params[0])
        if launch_phys != "a0":
            self.emit(f"mv {launch_phys}, a0")
        for b in fn.blocks:
            self.emit(f"{self.label_of[b.name]}:", note=f"block {b.name}")
            for op in b.ops:
                self.emit_op(op)

    def emit_epilogue(self, op: mir.MOp) -> None:
        frame = self.frame_bytes()
        self.emit(f"ld ra, {frame - 8}(sp)", op)
        offset = frame - 16
        for name in self.saved_regs:
            self.emit(f"ld {name}, {offset}(sp)", op)
            offset -= 8
        self.emit(f"addi sp, sp, {frame}", op)
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
