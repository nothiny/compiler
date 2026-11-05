"""Copy propagation on TIR (T015).

An identity op -- one whose result is value-identical to one of its
operands -- has its uses rewired to that operand, so the copy becomes
dead (DCE removes it next).  The identity set:

* ``broadcast`` whose source shape equals the result shape (a no-op
  expansion);
* ``reshape`` with ``can_reorder=False`` whose source shape equals the
  result shape (reshape is metadata on the data path);
* ``select.where(c, x, x)`` -- both branches the same value;
* ``ptradd(p, 0)`` with a rank-0 constant zero offset (pointer
  semantics: the result is exactly ``p`` -- same pointee type, same
  extents; the unified base/offset shape of a rank-0 offset is the
  base's own shape).

Deliberately NOT identity: ``hint`` (the result carries the recorded
alignment promise -- rewriting would drop it; ignoring a hint is safe
but this pass does not pessimize the wide-access proofs) and ``realize``
(a flag-changing materialisation the verifier treats as a distinct
construct, never a copy).

Legality (dominance, joins, value identity): the identity source is an
operand of the copy, so it dominates the copy and every use the copy
dominates; name-based region joins resolve at DEFS, and a copy that is
a region-final binding is never removed -- only its uses move.  Uses
inside a loop body where the source or the copy is a carried init are
skipped (the lowering's head-parameter reinterpretation -- a fixed
outside value must never replace a per-iteration meaning).
"""
from __future__ import annotations

from a100c.ir import tir
from a100c.passes import rewrite
from a100c.passes.analyses import Dominance, LoopStructure, Pos, \
    _child_step

__all__ = ["CopyPropPass"]


def _const_value(v: tir.Value):
    if v.producer is not None and v.producer.op == "const":
        return v.producer.attrs.get("value")
    return None


def _identity_source(op: tir.Op):
    """The operand the op copies, or None.  The second element is the
    refusal reason for ops that LOOK like copies but are refused by
    policy (hint, realize); ordinary shape-changing ops are simply not
    candidates and carry no reason."""
    if op.op == "broadcast":
        if op.attrs.get("from_shape") == op.results[0].shape:
            return op.operands[0], None
        return None, None
    if op.op == "reshape":
        if op.attrs.get("from_shape") == op.results[0].shape \
                and not op.attrs.get("can_reorder"):
            return op.operands[0], None
        return None, None
    if op.op == "select.where":
        if op.operands[1] is op.operands[2]:
            return op.operands[1], None
        return None, None
    if op.op == "ptradd":
        offset = op.operands[1]
        if offset.rank == 0 and isinstance(_const_value(offset), int) \
                and _const_value(offset) == 0:
            base = op.operands[0]
            if base.shape == op.results[0].shape:
                return base, None
        return None, None
    if op.op == "hint":
        return None, "hint is a promise attached to the value identity " \
                     "(never rewritten: dropping it pessimizes the " \
                     "wide-access proofs)"
    if op.op == "realize":
        return None, "realize materialises broadcast extents as real " \
                     "(a distinct construct, never a copy)"
    return None, None


class CopyPropPass:
    name = "copyprop"
    ANALYSES_CONSUMED = ("dominance", "loops")
    ANALYSES_PRESERVED = ()
    ANALYSES_INVALIDATED = ("dominance", "liveness", "loops",
                            "memory_effects")

    def run(self, module: tir.Module, ctx) -> bool:
        dominance: Dominance = ctx.get("dominance")
        loops: LoopStructure = ctx.get("loops")
        trace = ctx.trace
        changed = False

        def walk_block(block: tir.Block, base: Pos, chain: tuple) -> None:
            nonlocal changed
            for i, st in enumerate(block.statements):
                here = base + (_child_step("op", i),)
                if isinstance(st, tir.If):
                    walk_block(st.then, here + (_child_step("then", 0),),
                               chain)
                    walk_block(st.els, here + (_child_step("else", 0),),
                               chain)
                    continue
                if isinstance(st, tir.Loop):
                    walk_block(st.body, here + (_child_step("body", 0),),
                               chain + (st,))
                    continue
                if not isinstance(st, tir.Op) or not st.results:
                    continue
                source, reason = _identity_source(st)
                if source is None:
                    if reason is not None and st.op in (
                            "broadcast", "reshape", "select.where",
                            "ptradd", "hint", "realize"):
                        trace.record_decline(reason)
                    continue
                # an identity whose operand is a carried init of an
                # enclosing loop is NOT a copy inside that loop: the
                # operand denotes the CURRENT iteration's value there
                # (the head-parameter override), so folding it away drops
                # a per-iteration term (T026: ``ptradd(p, j)`` with j the
                # while's channel lost its ``+ j`` inside the body).  The
                # enclosure is the walk's own loop-node chain -- copyprop
                # only rewires uses (no insertions or deletions), so the
                # chain is exact at every statement.
                carried_here = {init.vid
                                for loop in chain
                                for _n, init in loop.carried}
                if any(o.vid in carried_here for o in st.operands):
                    trace.record_decline(
                        "identity operand is loop-carried at this position "
                        "(the per-iteration meaning is not the copy)")
                    continue
                result = st.results[0]
                # the source must dominate the copy (an operand does, but
                # the dominance analysis is the authority -- a forced or
                # stale answer here changes the pass's behaviour)
                src_path = dominance.def_path.get(source.vid)
                if src_path is None or not dominance.dominates(src_path,
                                                                here):
                    trace.record_decline(
                        "the identity source does not dominate the copy")
                    continue
                n = rewrite.guarded_replace_uses(module, result, source,
                                                 loops)
                if n:
                    changed = True
                    rewrite.copy_aliases(result, source)
                    trace.record_fired(
                        f"copyprop {st.op}: {n} use(s) -> "
                        f"{source.name}")
                if result.vid in rewrite.protected_defs(module):
                    trace.record_decline(
                        "region-final binding kept (the join resolves the "
                        "name at the def; the copy itself stays for DCE)")

        for fn in module.functions:
            walk_block(fn.body, (), ())
        return changed
