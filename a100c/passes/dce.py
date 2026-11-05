"""Dead code elimination on TIR (T015).

Removes statements whose results no live use ever reaches, iterating to
a fixpoint (removing one dead op can make its operands' defs dead).
Liveness -- the shared analysis -- carries every value's use sites, and
a use site is live when its statement survives; the fixpoint closes
over both.

Roots -- the observable effects and the structural lookups -- are
preserved exactly:

* stores, atomics and ``debug_barrier`` (synchronization and stage
  effects), and volatile loads (the not-elidable carrier);
* the region-final name bindings: both arms' final binding of every If
  join name and every loop body's final binding of every carried name
  (the verifier's joins and the lowering's back-edge/classification
  machinery resolve those names at the defs);
* region conditions, loop bounds and carried initialisers (they always
  evaluate), and everything transitively used by a surviving statement.

A dead op in the trapping class -- a division or remainder whose
divisor is not a nonzero constant -- is RETAINED with the unmet
condition recorded (removing an executed division could change trapping
behaviour); every other dead op (pure arithmetic, unused non-volatile
loads, layout/metadata producers) is removed.  After every removal
round the pass refreshes its analysis view: the suite's digest check
forces recomputation, never a stale read.
"""
from __future__ import annotations

from typing import List, Set

from a100c.ir import tir
from a100c.passes import rewrite
from a100c.passes.analyses import Liveness

__all__ = ["DCEPass"]

_EFFECT_OPS = ("store", "atomic_rmw", "atomic_cas", "debug_barrier")


def _may_trap(op: tir.Op) -> bool:
    if op.op not in ("arith.sdiv", "arith.udiv", "arith.srem",
                     "arith.urem"):
        return False
    divisor = op.operands[1]
    if divisor.producer is not None and divisor.producer.op == "const":
        value = divisor.producer.attrs.get("value")
        if isinstance(value, int) and value != 0:
            return False
    return True


def _is_effect(op: tir.Op) -> bool:
    return op.op in _EFFECT_OPS or bool(op.attrs.get("volatile"))


class DCEPass:
    name = "dce"
    ANALYSES_CONSUMED = ("liveness",)
    ANALYSES_PRESERVED = ()
    ANALYSES_INVALIDATED = ("dominance", "liveness", "loops",
                            "memory_effects")

    def run(self, module: tir.Module, ctx) -> bool:
        trace = ctx.trace
        changed = False
        for _round in range(64):
            liveness: Liveness = ctx.get("liveness")
            live = self._live_values(module, liveness)
            doomed: List[tir.Op] = []

            def walk(block: tir.Block) -> None:
                for st in block.statements:
                    if isinstance(st, tir.If):
                        walk(st.then)
                        walk(st.els)
                        continue
                    if isinstance(st, tir.Loop):
                        walk(st.body)
                        continue
                    if not isinstance(st, tir.Op) or not st.results:
                        continue
                    if _is_effect(st):
                        continue          # an observable-effect root
                    if any(r.vid in live for r in st.results):
                        continue          # a live result keeps the def
                    if _may_trap(st):
                        trace.record_decline(
                            "dead division/remainder retained (the "
                            "divisor is not a nonzero constant: removal "
                            "could change trapping behaviour)")
                        continue
                    doomed.append(st)

            for fn in module.functions:
                walk(fn.body)
            if not doomed:
                break
            for op in doomed:
                if rewrite.remove_statement(module, op):
                    changed = True
                    trace.record_fired(f"dce {op.op}")
            # the module mutated: refresh the view so the next round's
            # liveness is recomputed (the digest check enforces it)
            ctx.refresh()
        return changed

    @staticmethod
    def _live_values(module: tir.Module, liveness: Liveness) -> Set[int]:
        """The values whose definitions must survive: the region-final
        roots, plus every value with a use site whose statement survives
        (an effect statement, a region read, or a statement with a live
        result) -- closed to a fixpoint."""
        live: Set[int] = set(rewrite.protected_defs(module))

        def site_live(site) -> bool:
            op = site.op
            if isinstance(op, (tir.If, tir.Loop)):
                return True               # conditions/bounds/carried read
            if _is_effect(op):
                return True
            return any(r.vid in live for r in op.results)

        vids = sorted(liveness.uses.keys())
        for _ in range(4096):
            grew = False
            for vid in vids:
                if vid in live:
                    continue
                if any(site_live(s) for s in liveness.uses[vid]):
                    live.add(vid)
                    grew = True
            if not grew:
                break
        return live
