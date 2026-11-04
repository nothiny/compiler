"""Selection: one generic matcher over the repertoire table (BE-SELECTION).

For every MIR op, computes the op's feature dictionary (opcode, operand
widths, attributes) and consults the repertoire data; the matched row's
mnemonic and template are recorded on the op (selection results travel with
the module to emission).  An op with no matching row is refused with a
located diagnostic naming the construct -- never matched to a nearby form
and never silently approximated (MECH-DIAGNOSTIC-REFUSAL).
"""
from __future__ import annotations

from typing import Dict, Optional

from a100c.backend.repertoire import DEFAULT_REPERTOIRE, InstructionEntry, Repertoire
from a100c.ir import mir

__all__ = ["SelectionError", "Selected", "select"]


class SelectionError(Exception):
    def __init__(self, loc, construct: str, message: str):
        super().__init__(f"selection: {construct}: {message}"
                         + (f" (at {loc})" if loc else ""))
        self.loc = loc
        self.construct = construct
        self.message = message


class Selected:
    """The selection result attached to one MIR op."""

    __slots__ = ("entry", "features")

    def __init__(self, entry: InstructionEntry, features: Dict[str, object]):
        self.entry = entry
        self.features = features

    @property
    def mnemonic(self) -> str:
        return self.entry.mnemonic


def _features(op: mir.MOp) -> Dict[str, object]:
    features: Dict[str, object] = {"opcode": op.opcode}
    ops = op.operands
    if op.opcode in ("sload", "sstore"):
        features["width"] = op.attrs["width"]
        if op.opcode == "sload":
            features["ext"] = op.attrs["ext"]
    elif op.opcode in mir.SBIN_OPS and ops:
        features["width"] = ops[0].type.width
    elif op.opcode == "vbin":
        features["op"] = op.attrs["op"]
        features["fp"] = bool(ops and ops[0].type.kind == "float")
    elif op.opcode == "vbinx":
        features["op"] = op.attrs["op"]
        features["fp"] = bool(ops and ops[0].type.kind == "float")
    elif op.opcode == "vunary":
        features["op"] = op.attrs["op"]
    elif op.opcode == "vred":
        features["kind"] = op.attrs["kind"]
        features["fp"] = bool(ops and ops[0].type.kind == "float")
        features["unsigned"] = bool(ops and ops[0].type.kind == "uint")
    elif op.opcode == "vcmp":
        features["pred"] = op.attrs["pred"]
        features["fp"] = bool(op.attrs.get("fp", False))
        features["unsigned"] = bool(ops and ops[0].type.kind == "uint")
    elif op.opcode == "vcmpx":
        features["pred"] = op.attrs["pred"]
    elif op.opcode == "vwaddx0":
        features["mode"] = op.attrs["mode"]
    elif op.opcode in ("vloadix", "vstoreix"):
        features["eew"] = op.attrs["eew"]
    elif op.opcode == "vsetvli":
        features["sew"] = op.attrs["sew"]
        features["lmul"] = op.attrs["lmul"]
        features["policy"] = op.attrs["policy"]
    return features


def select(module: mir.MModule,
           repertoire: Optional[Repertoire] = None) -> Dict[int, Selected]:
    """Select every op in the module; returns {op index: Selected}.

    Refuses (SelectionError, located) on any op with no repertoire row.
    """
    if repertoire is None:
        repertoire = DEFAULT_REPERTOIRE
    module.renumber()
    results: Dict[int, Selected] = {}
    for fn in module.functions:
        for block in fn.blocks:
            for op in block.ops:
                features = _features(op)
                entry = repertoire.find(op.opcode, features)
                if entry is None:
                    raise SelectionError(
                        op.loc, op.opcode,
                        f"no repertoire entry for {op.opcode} with features "
                        f"{ {k: v for k, v in features.items() if k != 'opcode'} }"
                        "; the construct is refused (MECH-DIAGNOSTIC-REFUSAL)")
                results[op.index] = Selected(entry, features)
    module.meta["selection"] = {
        "ops": len(results),
        "mnemonics": sorted({s.mnemonic for s in results.values()}),
    }
    return results
