"""Loop-invariant code motion on TIR (T015).

Hoists INVARIANT PURE EXPRESSIONS out of loop bodies to the position
before the loop.  Legality:

* pure and non-trapping only -- a memory access (masked or not) is
  never hoisted: a hoisted read would touch memory the source may never
  read (zero-trip safety), and a masked load's disabled positions
  perform no access by contract while a hoisted one would read them;
  divisions/remainders and float-to-int converts are refused as the
  trapping/undefined classes even when their operands are invariant;
* every operand must be defined OUTSIDE the loop and not be one of the
  loop's carried inits (inside the body an init use denotes the CURRENT
  iteration's value -- the MIR head-parameter override; hoisting such an
  operation would freeze the initial value, the classic
  loop-invariant-hoisting miscompile).  Cascading hoists arrive with
  the pipeline's next round (the analysis is recomputed after every
  mutation);
* no result of the hoisted operation may have a scope name that the loop
  body (re)binds -- TIR scoping is NAME-BASED (the verifier's lexical
  rule: a use is legal while one of the value's names still maps to it).
  A body-defined value that shadows one of the result's names sits ABOVE
  the remaining in-body uses once the definition moves to the preheader,
  and those uses resolve against the shadow -- use-before-definition
  (implicit_conv2d's reshape ``rs`` vs the source variable ``rs`` riding
  the srem's alias, the T024 census class).  A result whose name the body
  rebinds is declined this round; the fixpoint may still hoist it later
  once the shadowing def itself leaves the body;
* a statement that is a region-final name binding (an if-arm join name
  or a carried name's body-end definition) is never moved: the join
  resolves the name at the def and the lowering's carried
  classification reads the body's final binding;
* the hoist is zero-trip safe by purity: the loop may run zero times
  and the hoisted expression simply computes an unused value.

Decisions are made on one analysis snapshot and applied afterwards, so
the positions the decisions read stay consistent.  Within one loop no
two hoisted ops depend on each other (an operand defined in the body
declines the op this round), so the insertion order is free; body order
is used because it is deterministic.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from a100c.ir import tir
from a100c.passes import rewrite
from a100c.passes.analyses import Dominance, LoopStructure

__all__ = ["LICMPass"]

#: op codes refused as the trapping/undefined class even when invariant
_TRAPPING = {"arith.sdiv", "arith.udiv", "arith.srem", "arith.urem",
             "arith.fdiv", "arith.frem", "arith.div_rn"}

#: memory / ordering effects -- never hoisted
_NEVER = {"load", "store", "atomic_rmw", "atomic_cas", "debug_barrier"}


def _hoistable(op: tir.Op) -> Tuple[bool, Optional[str]]:
    if op.op in _NEVER:
        return False, (f"memory access '{op.op}' is never hoisted "
                       "(masked or not: zero-trip safety -- a hoisted "
                       "read touches memory the source may never read)")
    if op.op in _TRAPPING:
        return False, (f"'{op.op}' is the trapping class (division or "
                       "remainder): a hoisted one would trap where the "
                       "source never executed it")
    if op.op == "convert":
        src = op.operands[0].type
        dst = op.results[0].type
        if src.is_float() and dst.is_int():
            return False, ("float-to-int convert of NaN/out-of-range is "
                           "undefined at the source level (refused)")
    if op.op == "hint":
        return False, ("hint is a promise attached to the value identity "
                       "(hoisting it away from its use pessimizes the "
                       "wide-access proofs)")
    return True, None


def _body_name_owners(body: tir.Block) -> Dict[str, Set[int]]:
    """name -> vids of the values the loop body binds it to.

    Everything that can shadow a name inside the body counts: op results
    (under every scope name), if/loop join results, and each nested
    loop's CARRIED names (a carried entry rebinds its name at the body's
    entry -- the verifier defines ``body_scope[name] = init`` -- so a
    hoisted result aliased to a carried name would be shadowed from the
    very first body statement)."""
    owners: Dict[str, Set[int]] = {}

    def add(name: str, vid: int) -> None:
        owners.setdefault(name, set()).add(vid)

    def walk(block: tir.Block) -> None:
        for st in block.statements:
            if isinstance(st, tir.Op):
                for r in st.results:
                    for n in r.scope_names():
                        add(n, r.vid)
            elif isinstance(st, tir.If):
                walk(st.then)
                walk(st.els)
                for name, jv in zip(st.join_names, st.join_results):
                    add(name, jv.vid)
                    for n in jv.scope_names():
                        add(n, jv.vid)
            elif isinstance(st, tir.Loop):
                for name, init in st.carried:
                    add(name, init.vid)
                walk(st.body)
                for name, jv in zip([n for n, _ in st.carried],
                                    st.join_results):
                    add(name, jv.vid)
                    for n in jv.scope_names():
                        add(n, jv.vid)

    walk(body)
    return owners


def _result_name_rebound(op: tir.Op, owners: Dict[str, Set[int]]) -> bool:
    """Does the body bind one of ``op``'s result names to another value?"""
    own = {r.vid for r in op.results}
    for r in op.results:
        for name in r.scope_names():
            for vid in owners.get(name, ()):
                if vid not in own:
                    return True
    return False


class LICMPass:
    name = "licm"
    ANALYSES_CONSUMED = ("dominance", "loops")
    ANALYSES_PRESERVED = ()
    ANALYSES_INVALIDATED = ("dominance", "liveness", "loops",
                            "memory_effects")

    def run(self, module: tir.Module, ctx) -> bool:
        dominance: Dominance = ctx.get("dominance")
        loops: LoopStructure = ctx.get("loops")
        trace = ctx.trace
        hoists: List[Tuple[tir.Loop, tir.Op]] = []

        def loop_invariant(op: tir.Op, info) -> bool:
            for operand in op.operands:
                if operand.vid in info.carried_inits:
                    trace.record_decline(
                        "loop-carried operand: the operation is "
                        "per-iteration inside the body (never hoisted)")
                    return False
                if operand.vid in info.body_defined:
                    return False         # defined inside: not this round
                # the operand's definition must dominate the loop (the
                # verifier's use-before-def rule says it does, but the
                # dominance analysis is the authority here -- a forced
                # or stale answer changes this pass's behaviour)
                dpath = dominance.def_path.get(operand.vid)
                if dpath is None or not dominance.dominates(
                        dpath, info.path):
                    trace.record_decline(
                        "operand does not dominate the loop (invariance "
                        "unproven)")
                    return False
            return True

        def collect(block: tir.Block, info, owners: Dict[str, Set[int]]) -> None:
            for st in block.statements:
                if isinstance(st, tir.If):
                    collect(st.then, info, owners)
                    collect(st.els, info, owners)
                    continue
                if isinstance(st, tir.Loop):
                    continue            # nested loops: their own entries
                if not isinstance(st, tir.Op) or not st.results:
                    continue
                ok, reason = _hoistable(st)
                if not ok:
                    trace.record_decline(reason)
                    continue
                if any(r.vid in rewrite.protected_defs(module)
                       for r in st.results):
                    trace.record_decline(
                        "region-final binding: the join resolves the name "
                        "at the def (never moved)")
                    continue
                if _result_name_rebound(st, owners):
                    # the name-based scope rule: a body binding of one of
                    # this result's names would sit between the preheader
                    # and the remaining in-body uses (use-before-definition
                    # -- the verifier is the control, never a weakened one)
                    trace.record_decline(
                        "result name re-bound inside the loop body (the "
                        "name-based scope rule: the remaining in-body uses "
                        "would resolve against the body's binding)")
                    continue
                if loop_invariant(st, info):
                    hoists.append((info.node, st))

        # decide on one snapshot, innermost loops first (a hoist out of
        # an inner loop can enable the outer one next round)
        for info in sorted(loops.loops, key=lambda li: -len(li.path)):
            collect(info.node.body, info, _body_name_owners(info.node.body))
        if not hoists:
            return False

        changed = False
        for node, op in hoists:
            if rewrite.remove_statement(module, op):
                changed = True
                trace.record_fired(f"licm {op.op} -> loop preheader")
        if not changed:
            return False
        pending: Dict[int, List[tir.Op]] = {}
        for node, op in hoists:
            pending.setdefault(id(node), []).append(op)
        for fn in module.functions:
            self._insert_before(fn.body, pending)
        rewrite.drop_protected_cache(module)
        return True

    @staticmethod
    def _insert_before(block: tir.Block, pending: Dict[int, List[tir.Op]]) \
            -> None:
        i = 0
        while i < len(block.statements):
            st = block.statements[i]
            if isinstance(st, tir.If):
                LICMPass._insert_before(st.then, pending)
                LICMPass._insert_before(st.els, pending)
            elif isinstance(st, tir.Loop):
                LICMPass._insert_before(st.body, pending)
                mine = pending.pop(id(st), None)
                if mine:
                    block.statements[i:i] = mine
                    i += len(mine)
            i += 1
