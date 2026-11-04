"""Legalisation (BE-LEGALIZATION): one declared stage with a contract.

Accepts MIR constructs the target cannot execute directly and rewrites them
into legal sequences; after it runs, every remaining construct is in the
declared repertoire -- that guarantee is what selection relies on.

Implemented rewrites (each has no direct repertoire entry):

  ``vwiden sext/zext`` (vi32 -> vi64)  ->  ``vwaddx0`` (vwadd/vwaddu.vx with
      rs1 = x0): no target instruction widens by itself; the widening add
      with a zero scalar realizes the extension.
  ``strunc`` (i64 -> i32)  ->  ``swext`` (addiw rd, rs, 0): RV64 has no
      truncation instruction; i32 values live sign-extended in registers and
      the re-extension realizes the narrowing view.

The control (MECH-WITNESS-TEST): with a rewrite disabled, the stage leaves
the construct in place and the MIR verifier / selector reports it -- the
illegal construct is never silently assembled.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from a100c.ir import mir

__all__ = ["LegalizeOptions", "legalize", "LegalizeReport"]


@dataclass
class LegalizeOptions:
    #: rewrite toggles (the witness control): name -> enabled
    disabled: Set[str] = None  # type: ignore[assignment]

    def __post_init__(self):
        if self.disabled is None:
            self.disabled = set()

    def enabled(self, name: str) -> bool:
        return name not in self.disabled


@dataclass
class LegalizeReport:
    rewrites: Dict[str, int]
    declined: Dict[str, int]

    def describe(self) -> dict:
        return {"rewrites": dict(self.rewrites), "declined": dict(self.declined)}


def legalize(module: mir.MModule,
             options: Optional[LegalizeOptions] = None) -> LegalizeReport:
    """Rewrite illegal-but-expressible constructs into legal sequences."""
    options = options or LegalizeOptions()
    rewrites: Dict[str, int] = {}
    declined: Dict[str, int] = {}
    for fn in module.functions:
        for block in fn.blocks:
            new_ops: List[mir.MOp] = []
            for op in block.ops:
                if op.opcode == "vwiden":
                    if options.enabled("vwiden"):
                        new = mir.MOp("vwaddx0", op.operands, op.results,
                                      attrs={"mode": op.attrs["mode"]},
                                      loc=op.loc)
                        new.index = op.index
                        new_ops.append(new)
                        rewrites["vwiden->vwaddx0"] = \
                            rewrites.get("vwiden->vwaddx0", 0) + 1
                    else:
                        new_ops.append(op)
                        declined["vwiden"] = declined.get("vwiden", 0) + 1
                    continue
                if op.opcode == "strunc":
                    if options.enabled("strunc"):
                        new = mir.MOp("swext", op.operands, op.results,
                                      loc=op.loc)
                        new.index = op.index
                        new_ops.append(new)
                        rewrites["strunc->swext"] = \
                            rewrites.get("strunc->swext", 0) + 1
                    else:
                        new_ops.append(op)
                        declined["strunc"] = declined.get("strunc", 0) + 1
                    continue
                new_ops.append(op)
            block.ops = new_ops
    module.meta["legalize"] = {"rewrites": dict(rewrites),
                               "declined": dict(declined)}
    return LegalizeReport(rewrites=rewrites, declined=declined)
