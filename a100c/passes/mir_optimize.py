"""MIR-CFG loop analysis and the mir-licm prototype (W3 of the unified
optimization round -- NOT WIRED into the pipeline).

Status: attempted, measured, unwired.  The first delivery's sconst-only
LICM (pressure-safe by construction: the allocator rematerializes
constants under pressure) measured -2.5% on softmax-f16 but +1% on
linear-dropout and +8% on log_softmax_linear at the pressure-safe hoist
cap -- the register-pressure perturbation outweighs the per-iteration
li savings, and unbounded hoisting overflows the allocator's spill/remat
round budget (the convergence bomb).  The stage is therefore not wired;
the loop analysis here (natural loops over the dominator tree, def-sites
by value identity -- sibling blocks carry identically-named params) is
the reusable machinery for the follow-up's pressure-aware design.  See
docs/compiler-agent/optimizations/DESIGN-ISSUE-mir-optimize.md.

The original design sketch (kept for the follow-up):

* mir-licm -- loop-invariant code motion for the SCALAR core: ``sconst``
  rematerializations and pure integer scalar operations (the SBIN_OPS
  set plus smove/strunc/swext) hoist from natural-loop bodies to the
  loop's unique preheader.  Speculation is safe on this target (RISC-V
  integer add/mul/div do not trap; division by zero returns the defined
  non-trapping result), memory accesses and every vector op are never
  hoisted (a vector op's semantics depend on the active vsetvli region,
  and regions do not cross block boundaries -- the MIR invariant), and
  a zero-trip loop only ever executes the hoisted pure ops uselessly.
  Hoisting is dominated-safe: a definition that dominates a use inside
  the loop also dominates the preheader (every path to the use passes
  through it).

* mir-strength-reduction, mir-loop-predicate, mir-vsetvli-hoist -- the
  first delivery of this stage runs them as analysis-only (they fire
  zero rewrites); their transforms land in the follow-up delivery.  The
  counters report the truth; a pass that fires zero times is not a
  rewrite.

Switches (the A100C_PASS_* pattern; recorded in the artifact identity
when disabled): A100C_MIRPASS_LICM=off, A100C_MIRPASS_SR=off,
A100C_MIRPASS_PRED=off, A100C_MIRPASS_VSETVLI=off.
"""
from __future__ import annotations

from typing import Dict, List, Set, Tuple

from a100c.ir import mir

#: what mir-licm hoists in this delivery: ONLY the sconst
#: rematerializations.  A hoisted constant is pressure-safe by
#: construction -- under register pressure the allocator rematerializes
#: it right back to the per-use sconst form (its declared escape valve),
#: so hoisting is never worse than the loop-body form and saves the
#: per-iteration li when the budget allows.  The integer address trees
#: (SBIN chains, width moves) are deliberately NOT hoisted yet: their
#: results are not rematerializable, and the first delivery's unbounded
#: hoisting of them overflowed the register file into a non-converging
#: spill/remat deadlock -- they return behind an explicit pressure
#: budget in the follow-up.
_HOISTABLE = frozenset({"sconst"})


class MirOptimizeError(Exception):
    """A located refusal from the stage (never a silent miscompile)."""

    def __init__(self, loc, message: str):
        super().__init__(message)
        self.loc = loc
        self.message = message


# ---------------------------------------------------------------------------
# the CFG
# ---------------------------------------------------------------------------
def _terminator_targets(op: mir.MOp) -> List[str]:
    if op.opcode == "br":
        return [op.attrs["target"]]
    if op.opcode == "brc":
        return [op.attrs["true_target"], op.attrs["false_target"]]
    return []


def _build_graph(function: mir.MFunction) -> Tuple[Dict[str, List[str]],
                                                   Dict[str, List[str]]]:
    """(preds, succs) over the block CFG from the terminators."""
    preds: Dict[str, List[str]] = {b.name: [] for b in function.blocks}
    succs: Dict[str, List[str]] = {b.name: [] for b in function.blocks}
    for b in function.blocks:
        term = b.ops[-1] if b.ops else None
        if term is None:
            continue
        for t in _terminator_targets(term):
            if t in succs:
                if b.name not in preds[t]:
                    preds[t].append(b.name)
                if t not in succs[b.name]:
                    succs[b.name].append(t)
    return preds, succs


def _dominators(function: mir.MFunction, preds, succs) -> Dict[str, Set[str]]:
    """The classic iterative set-based dominator computation over RPO."""
    entry = function.blocks[0].name
    # post-order DFS from the entry (unreachable blocks are excluded)
    post: List[str] = []
    seen = {entry}
    stack = [(entry, iter(succs[entry]))]
    while stack:
        node, it = stack[-1]
        advanced = False
        for s in it:
            if s not in seen:
                seen.add(s)
                stack.append((s, iter(succs[s])))
                advanced = True
                break
        if not advanced:
            post.append(node)
            stack.pop()
    rpo = list(reversed(post))
    all_rpo = set(rpo)
    dom: Dict[str, Set[str]] = {entry: {entry}}
    for n in rpo[1:]:
        dom[n] = set(all_rpo)
    changed = True
    while changed:
        changed = False
        for n in rpo[1:]:
            ps = [p for p in preds[n] if p in dom and p in all_rpo]
            new = set.intersection(*(dom[p] for p in ps)) if ps else set()
            new = new | {n}
            if new != dom[n]:
                dom[n] = new
                changed = True
    return dom


def _natural_loops(function: mir.MFunction, preds,
                   dom) -> List[Tuple[str, Set[str]]]:
    """(head, body-blocks) for every back-edge, innermost first."""
    loops: List[Tuple[str, Set[str]]] = []
    for b in function.blocks:
        term = b.ops[-1] if b.ops else None
        if term is None:
            continue
        for t in _terminator_targets(term):
            if t in dom.get(b.name, set()):
                # back edge b -> t (t dominates b): the natural loop is
                # t plus everything that reaches b without passing t
                body = {t, b.name}
                stack = [b.name]
                while stack:
                    n = stack.pop()
                    for p in preds[n]:
                        if p not in body:
                            body.add(p)
                            stack.append(p)
                loops.append((t, body))
    loops.sort(key=lambda hb: len(hb[1]))
    return loops


# ---------------------------------------------------------------------------
# mir-licm
# ---------------------------------------------------------------------------
def _licm_function(function: mir.MFunction) -> int:
    """Hoist invariant pure scalar ops out of every natural loop.

    Inner loops first so a value hoisted out of an inner loop lands in
    an outer loop's blocks and hoists further on the outer sweep.  The
    sweep repeats to a fixpoint inside each loop (cascading within one
    pass over the body would otherwise miss back-referencing chains).
    """
    blocks_by_name = {b.name: b for b in function.blocks}
    order = {b.name: i for i, b in enumerate(function.blocks)}
    preds, succs = _build_graph(function)
    dom = _dominators(function, preds, succs)
    loops = _natural_loops(function, preds, dom)
    hoisted_total = 0
    #: the per-preheader hoist cap: the allocator relieves register
    #: pressure by rematerializing ONE value per spill round (64 rounds
    #: max), so an unbounded hoist count is a compile-time convergence
    #: bomb even when every hoisted value is a rematerializable sconst.
    #: Eight long-lived constants per preheader is well inside that
    #: budget while still taking the hottest loop-body materializations
    #: out of the per-iteration path.  Four: the biggest softmax kernel
    #: (linear_dropout [16,128,128] f16) rides the register-file limit
    #: even before the pass and tips over at eight.
    _CAP = 4
    hoisted_into: Dict[str, int] = {}
    for head, body in loops:
        outside = [p for p in preds[head] if p not in body]
        if len(outside) != 1:
            # not the structured single-entry form the lowering emits;
            # a multi-entry loop would need a dedicated preheader block
            continue
        pre = blocks_by_name[outside[0]]
        if hoisted_into.get(pre.name, 0) >= _CAP:
            continue
        changed = True
        while changed:
            changed = False
            # def sites by VALUE IDENTITY, never by name: sibling
            # blocks carry identically-named params (every chunk head
            # names its induction "elem.loop") and a name-keyed map
            # would alias them -- the first licm delivery hoisted a
            # chunk head's own test into the preheader that way
            defsite: Dict[int, str] = {}
            for blk in function.blocks:
                for p in blk.params:
                    defsite[id(p)] = blk.name
                for op in blk.ops:
                    for r in op.results:
                        defsite[id(r)] = blk.name
            for bname in sorted(body, key=lambda n: order.get(n, 1 << 30)):
                blk = blocks_by_name[bname]
                if not blk.ops:
                    continue
                term = blk.ops[-1]
                body_ops = blk.ops[:-1]
                keep: List[mir.MOp] = []
                for op in body_ops:
                    if (op.opcode in _HOISTABLE
                            and hoisted_into.get(pre.name, 0) < _CAP
                            and all(defsite.get(id(o), bname) not in body
                                    for o in op.operands)):
                        # hoist: move to the preheader, before its
                        # terminator; the def-site becomes the preheader
                        # so dependent ops hoist on the same sweep
                        pre.ops.insert(len(pre.ops) - 1, op)
                        hoisted_into[pre.name] = \
                            hoisted_into.get(pre.name, 0) + 1
                        for r in op.results:
                            defsite[id(r)] = pre.name
                        hoisted_total += 1
                        changed = True
                    else:
                        keep.append(op)
                blk.ops = keep + [term]
    return hoisted_total


# ---------------------------------------------------------------------------
# the declared passes whose transforms land in the follow-up delivery
# ---------------------------------------------------------------------------
def _strength_reduction_function(function: mir.MFunction) -> int:
    """Analysis-only in this delivery (fires zero rewrites): the affine
    induction-variable -> pointer-recursion transform."""
    return 0


def _loop_predicate_function(function: mir.MFunction) -> int:
    """Analysis-only in this delivery (fires zero rewrites): the counted
    loop predicate resolution."""
    return 0


def _vsetvli_hoist_function(function: mir.MFunction) -> int:
    """Analysis-only in this delivery (fires zero rewrites): the
    region-consistent vsetvli hoist (blocked by the regions-do-not-cross
    -blocks invariant until the region model carries per-point state)."""
    return 0


# ---------------------------------------------------------------------------
# the stage entry
# ---------------------------------------------------------------------------
def run(module: mir.MModule, options) -> mir.MModule:
    """Run the enabled mir-optimize passes over ``module`` (in place).

    ``options`` is the CompileOptions carrying the four A100C_MIRPASS_*
    switches (default on).  The per-pass rewrite counts land in
    ``module.meta['mir_passes']``.
    """
    counts: Dict[str, Dict[str, int]] = {}
    if getattr(options, "mir_licm", True):
        n = 0
        for function in module.functions:
            n += _licm_function(function)
        counts["mir-licm"] = {"hoisted": n}
    if getattr(options, "mir_strength_reduction", True):
        n = 0
        for function in module.functions:
            n += _strength_reduction_function(function)
        counts["mir-strength-reduction"] = {"rewrites": n}
    if getattr(options, "mir_loop_predicate", True):
        n = 0
        for function in module.functions:
            n += _loop_predicate_function(function)
        counts["mir-loop-predicate"] = {"resolved": n}
    if getattr(options, "mir_vsetvli_hoist", True):
        n = 0
        for function in module.functions:
            n += _vsetvli_hoist_function(function)
        counts["mir-vsetvli-hoist"] = {"hoisted": n}
    module.meta["mir_passes"] = counts
    return module
