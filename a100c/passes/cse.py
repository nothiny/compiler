"""Common subexpression elimination on TIR (T015).

Availability with scoped visibility: an earlier pure op is available to
a later identical op when the earlier one dominates it -- which in the
structured region tree means the walk's scope discipline:

* entries created inside an If arm die at the arm's end (both arms
  start from the parent's available entries);
* entries created inside a loop body die at the body's end, and the
  parent's entries that REFERENCE a carried-init value of the loop (as
  an operand -- directly or through a load's mask/other -- or as their
  own result) are NOT visible inside the body: inside the body a use of
  a carried init denotes the CURRENT iteration's value (the MIR
  head-parameter override), so an outside computation that consumed the
  init computed a different thing than an inside candidate would.

Loads are pure values but memory-dependent: a load is reused only with
an effect/alias proof -- no barrier and no write at all in the tree
interval between the available load and the candidate, or every write
in that interval proven disjoint from the load's address (the same base
parameter with constant offsets and non-overlapping flat extents;
different kernel arguments never prove disjointness -- in-place
operators pass one buffer as two).  A masked load keeps its declared
disabled-position semantics (`other`/undef are part of the identity);
volatile loads are never reused.

program_id / num_programs participate as pure values (the same axis is
the same value).  Every replacement rewires uses through the shared
guard (a reinterpreted use site is never rewired).  Statements are
removed in one sweep AFTER the walk, so the positions the interval
proof reads stay valid throughout; a candidate that is a region-final
name binding keeps its definition (the join resolves the name at the
def).
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from a100c.ir import tir
from a100c.passes import rewrite
from a100c.passes.analyses import LoopStructure, MemoryEffects, Pos, \
    _child_step
from a100c.passes.rewrite import op_key

__all__ = ["CSEPass"]


class _Scope:
    """The available entries of one walk scope (key -> (op, path))."""

    def __init__(self, parent: "Optional[_Scope]" = None):
        self.parent = parent
        self.entries: Dict[tuple, Tuple[tir.Op, Pos]] = {}
        if parent is not None:
            self.entries.update(parent.entries)

    def add(self, key: tuple, op: tir.Op, path: Pos) -> None:
        self.entries[key] = (op, path)

    def lookup(self, key: tuple) -> Optional[Tuple[tir.Op, Pos]]:
        return self.entries.get(key)


def _load_key(op: tir.Op) -> Optional[tuple]:
    if op.attrs.get("volatile"):
        return None
    return ("load", op.operands[0].vid,
            op.operands[1].vid if len(op.operands) > 1 else None,
            op.operands[2].vid if len(op.operands) > 2 else None,
            op.attrs.get("masked_default"))


def _key_vids(key: tuple) -> Tuple[int, ...]:
    """The value vids a key's meaning depends on."""
    if key[0] == "load":
        return tuple(v for v in key[1:4] if v is not None)
    return tuple(key[1])


class CSEPass:
    name = "cse"
    ANALYSES_CONSUMED = ("loops", "memory_effects")
    ANALYSES_PRESERVED = ()
    ANALYSES_INVALIDATED = ("dominance", "liveness", "loops",
                            "memory_effects")

    def run(self, module: tir.Module, ctx) -> bool:
        loops: LoopStructure = ctx.get("loops")
        effects: MemoryEffects = ctx.get("memory_effects")
        trace = ctx.trace
        changed = [False]
        doomed: List[tir.Op] = []

        def load_reusable(earlier: tir.Op, earlier_path: Pos,
                          candidate: tir.Op, candidate_path: Pos) -> bool:
            """The effect/alias proof for reusing an available load.

            Two classes of intervening effect can change the memory the
            candidate reads: the effects in the tree interval between
            the two positions, AND -- when the availability crossed a
            loop boundary (the available load sits outside a loop whose
            body contains the candidate) -- every effect anywhere in
            that loop's body: the candidate runs each iteration, so the
            body's writes from PREVIOUS iterations precede it even when
            they sit after it in body order."""
            interval = list(effects.effects_between(earlier_path,
                                                    candidate_path))
            seen = {id(op) for op in interval}
            for info in loops.loops:
                body = loops.body_path(info)
                inside_candidate = candidate_path[:len(body)] == body
                inside_earlier = earlier_path[:len(body)] == body
                if inside_candidate and not inside_earlier:
                    for path, op in effects.effects:
                        if id(op) not in seen \
                                and path[:len(body)] == body:
                            interval.append(op)
                            seen.add(id(op))
            if not interval:
                return True
            ptr = candidate.operands[0]
            for effect in interval:
                if effect.op == "debug_barrier":
                    trace.record_decline(
                        "load reuse across a barrier refused (ordering)")
                    return False
                if effect.op in ("store", "atomic_rmw", "atomic_cas"):
                    writer = effect.operands[0]
                    if effects.provably_disjoint(ptr, writer):
                        continue
                    trace.record_decline(
                        "load reuse across an intervening write refused "
                        "without an alias proof (the write may alias the "
                        "load's address)")
                    return False
                if effect.op == "load" and effect.attrs.get("volatile"):
                    trace.record_decline(
                        "load reuse across a volatile access refused")
                    return False
            return True

        def try_replace(st: tir.Op, avail: tir.Op, what: str) -> None:
            for j, result in enumerate(st.results):
                survivor = avail.results[j]
                n = rewrite.guarded_replace_uses(module, result, survivor,
                                                 loops)
                if n:
                    changed[0] = True
                    rewrite.copy_aliases(result, survivor)
                    trace.record_fired(
                        f"{what}: {n} use(s) -> {survivor.name}")
            if any(r.vid in rewrite.protected_defs(module)
                   for r in st.results):
                trace.record_decline(
                    "region-final binding kept: the join resolves the "
                    "name at the def (the computation stays)")
                return
            if any(rewrite.count_uses(module, r) for r in st.results):
                # sites the guard skipped (reinterpreted loop-carried
                # meanings) still reference the candidate: its def stays
                trace.record_decline(
                    "uses remain at loop-carried sites: the candidate's "
                    "def stays (the rewrite is value-identical)")
                return
            doomed.append(st)

        def walk_block(block: tir.Block, base: Pos, scope: _Scope) -> None:
            i = 0
            while i < len(block.statements):
                st = block.statements[i]
                here = base + (_child_step("op", i),)
                if isinstance(st, tir.If):
                    walk_block(st.then, here + (_child_step("then", 0),),
                               _Scope(scope))
                    walk_block(st.els, here + (_child_step("else", 0),),
                               _Scope(scope))
                    i += 1
                    continue
                if isinstance(st, tir.Loop):
                    # entries referencing a carried init (as an operand,
                    # a load's mask/other, or as their own result) are
                    # not visible inside the body: their meaning there is
                    # per-iteration
                    inits = {init.vid for _, init in st.carried}
                    inner = _Scope(scope)
                    drop = [key for key, (op, _p) in inner.entries.items()
                            if any(v in inits for v in _key_vids(key))
                            or any(r.vid in inits for r in op.results)]
                    for key in drop:
                        del inner.entries[key]
                    walk_block(st.body, here + (_child_step("body", 0),),
                               inner)
                    i += 1
                    continue
                if not isinstance(st, tir.Op) or not st.results:
                    i += 1
                    continue
                key = _load_key(st) if st.op == "load" else op_key(st)
                if key is not None:
                    found = scope.lookup(key)
                    if found is not None:
                        avail, avail_path = found
                        if st.op != "load" or load_reusable(
                                avail, avail_path, st, here):
                            try_replace(st, avail, f"cse {st.op}")
                            i += 1
                            continue
                    scope.add(key, st, here)
                i += 1

        for fn in module.functions:
            walk_block(fn.body, (), _Scope())
        for op in doomed:
            rewrite.remove_statement(module, op)
        if doomed:
            changed[0] = True
        return changed[0]
