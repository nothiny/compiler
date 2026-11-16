"""MIR-CFG loop analysis and the mir-optimize stage's passes.

The WIRED pass (the declared mir-optimize stage, between lowering and
legalisation; OPT-IN -- ``A100C_MIRPASS_PRED=on``; the measured reason is
on the CompileOptions field):

* **mir-loop-predicate -- counted/while-loop rotation.**  The lowering's
   loop form is a head-test loop: ``head(i, carried...) { c = i < upper;
   brc c -> body, exit }`` with the body closing over ``br -> head``.
   Every iteration therefore executes the head's test/jump pair AND the
   body's unconditional back-edge jump.  The rotation rewrites it to the
   guarded do-while form: the preheader evaluates the condition on the
   initial values once (zero-trip safety preserved -- the body is never
   entered when the initial condition is false), the body's back edge
   becomes the conditional branch (the condition re-evaluated on the
   back-edge values, at the body's end), and the head block disappears.
   Per iteration, one unconditional jump and one block are removed; the
   emitter's compare+branch fusion (OPT-BRANCH-FUSE) applies to both new
   compare+branch pairs.  Legality is structural: a unique preheader, a
   single body block whose terminator is the single back edge, the
   head's ops exactly the condition computation (empty, or sconst
   materializations feeding one slt/sltu over head params and
   loop-invariant values), identity true-args, substitutable false-args,
   and matching exit arity.  The rotated condition reads exactly the
   values the original read at the same iteration boundaries (the
   single-back-edge form makes the head-entry values and the previous
   back-edge values the same sequence), so the evaluation sequence and
   every produced value are unchanged.

The UNWIRED machinery kept for the recorded follow-ups (see
docs/compiler-agent/optimizations/DESIGN-ISSUE-mir-optimize.md):

* mir-licm -- attempted and measured net negative (the register-pressure
  perturbation of blanket sconst hoisting outweighs the per-iteration
  li savings; unbounded hoisting overflows the allocator's spill/remat
  round budget).  Its implementation stays below, unwired, with the
  reusable natural-loop analysis this stage shares.
* mir-strength-reduction (induction -> pointer recursion) and
  mir-vsetvli-hoist (blocked by the regions-do-not-cross-blocks
  invariant until the region model carries per-point state) -- designed,
  not implemented.

Switch (the A100C_PASS_* pattern; recorded in the artifact identity
when disabled): A100C_MIRPASS_PRED=off.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple

from a100c.ir import mir

#: what mir-licm hoists (UNWIRED): ONLY the sconst rematerializations --
#: pressure-safe by construction (the allocator rematerializes constants
#: under pressure).  See the module docstring.
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
                # t plus everything that reaches b without passing t.
                # A SELF-EDGE (b == t) is exactly {t}: walking the
                # predecessors would swallow the loop's external entry
                # (a rotated loop's preheader -- the bug the rotation's
                # self-loops exposed)
                body = {t, b.name}
                stack = [] if b.name == t else [b.name]
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
# mir-loop-predicate: counted/while-loop rotation
# ---------------------------------------------------------------------------
def _def_block(function: mir.MFunction, rid: int) -> Optional[str]:
    """The block whose params or ops define the value ``rid`` (None when
    the definition is not in this function -- treated as not provably
    outside the loop, a decline).  Function parameters are defined at the
    entry block, which dominates every loop."""
    for p in function.params:
        if p.rid == rid:
            return function.blocks[0].name if function.blocks else None
    for b in function.blocks:
        for p in b.params:
            if p.rid == rid:
                return b.name
        for op in b.ops:
            for r in op.results:
                if r.rid == rid:
                    return b.name
    return None


def _rotate_one(function: mir.MFunction, head_name: str, body_set: Set[str],
                preds: Dict[str, List[str]], declines: Dict[str, int]) -> bool:
    """Rotate one natural loop in place; True when the rewrite fired.

    The matched form (the lowering's counted, while and chunk/staging
    loops): a unique preheader P ending in ``br INIT -> H``; a head H
    whose non-terminator ops are empty (the while form: the brc reads
    ``params[0]``) or a chain of sconst materializations feeding exactly
    one slt/sltu over head params and loop-invariant values (the counted
    form -- the bound constant is materialized inside the head); H's
    ``brc -> B/E`` passing the head params to B and a substitutable arg
    list (head params or loop-invariant values) to E; a single body
    block B whose terminator is the single back edge ``br V -> H``; the
    exit's arity equal to the false-arg count.

    Rotation is safe on the single-body-block loops as a DISJOINT family:
    no rotation targets another loop's head, body or preheader, so one
    sweep may rotate them all against one CFG snapshot.
    """
    def decline(reason: str) -> None:
        declines[reason] = declines.get(reason, 0) + 1

    blocks = {b.name: b for b in function.blocks}
    if head_name not in body_set or len(body_set) != 2:
        return False          # not the single-body-block form: not a candidate
    head = blocks[head_name]
    body_name = (body_set - {head_name}).pop()
    body = blocks[body_name]

    outside = [p for p in preds[head_name] if p not in body_set]
    if len(outside) != 1:
        decline("no-unique-preheader")
        return False
    pre = blocks[outside[0]]
    pterm = pre.terminator()
    if pterm is None or pterm.opcode != "br" \
            or pterm.attrs["target"] != head_name:
        decline("preheader-not-entry-br")
        return False
    init_args = list(pterm.attrs.get("args", ()))

    bterm = body.terminator()
    if bterm is None or bterm.opcode != "br" \
            or bterm.attrs["target"] != head_name:
        decline("body-not-single-back-edge")
        return False
    back_args = list(bterm.attrs.get("args", ()))
    if len(back_args) != len(head.params) or len(init_args) != len(head.params):
        decline("edge-arity")
        return False

    hterm = head.terminator()
    if hterm is None or hterm.opcode != "brc" \
            or hterm.attrs["true_target"] != body_name:
        decline("head-not-brc-to-body")
        return False
    exit_name = hterm.attrs["false_target"]
    if list(hterm.attrs.get("true_args", ())) != list(head.params):
        decline("true-args-not-identity")
        return False
    exit_block = blocks.get(exit_name)
    false_args = list(hterm.attrs.get("false_args", ()))
    if exit_block is None or len(exit_block.params) != len(false_args):
        decline("exit-arity")
        return False

    # every false arg must be substitutable: a head param (replaced by
    # the corresponding edge value at each rotation site) or a value
    # defined outside the loop (used as-is -- through the single entry
    # it dominates the preheader's end)
    false_pos: List[Optional[int]] = []
    for v in false_args:
        k = None
        for pi, p in enumerate(head.params):
            if p.rid == v.rid:
                k = pi
                break
        if k is None:
            defsite = _def_block(function, v.rid)
            if defsite is None or defsite in body_set:
                decline("false-arg-inside-loop")
                return False
        false_pos.append(k)

    # the head's condition computation: empty (while) or [sconst...]slt
    cond_val = hterm.operands[0] if hterm.operands else None
    cond_ops = head.ops[:-1]
    subst: Optional[Tuple[List[mir.MOp], mir.MOp, List[Optional[int]]]] = None
    if not cond_ops:
        # the while form: the brc reads the carried condition directly
        if cond_val is None or cond_val.rid != head.params[0].rid:
            decline("while-cond-not-param0")
            return False
    else:
        cmp_op = cond_ops[-1]
        const_ops = cond_ops[:-1]
        if cmp_op.opcode not in ("slt", "sltu") or not cmp_op.results \
                or len(cmp_op.operands) != 2 or cond_val is None \
                or cmp_op.results[0].rid != cond_val.rid:
            decline("cond-not-single-compare")
            return False
        used_by_cmp = {v.rid for v in cmp_op.operands}
        for op in const_ops:
            if op.opcode != "sconst" or not op.results \
                    or op.results[0].rid not in used_by_cmp:
                decline("head-carries-more")
                return False
        param_pos: List[Optional[int]] = []
        for v in cmp_op.operands:
            k = None
            for pi, p in enumerate(head.params):
                if p.rid == v.rid:
                    k = pi
                    break
            if k is None and not any(o.results and o.results[0].rid == v.rid
                                     for o in const_ops):
                # a loop-invariant operand: defined outside the loop
                defsite = _def_block(function, v.rid)
                if defsite is None or defsite in body_set:
                    decline("compare-operand-inside-loop")
                    return False
            param_pos.append(k)
        subst = (const_ops, cmp_op, param_pos)

    # ---- fire: the guarded do-while form --------------------------------
    def copy_condition(edge_args: List[mir.VReg],
                       into: mir.Block) -> mir.VReg:
        const_ops, cmp_op, param_pos = subst
        fresh: Dict[int, mir.VReg] = {}
        for op in const_ops:
            fresh[op.results[0].rid] = mir.VReg(op.results[0].type,
                                                loc=op.loc, hint="lp.k")
            into.ops.append(mir.MOp(op.opcode, [], [fresh[op.results[0].rid]],
                                    attrs=dict(op.attrs), loc=op.loc))
        operands = []
        for v, k in zip(cmp_op.operands, param_pos):
            if k is not None:
                operands.append(edge_args[k])
            elif v.rid in fresh:
                operands.append(fresh[v.rid])
            else:
                operands.append(v)
        result = mir.VReg(cmp_op.results[0].type, loc=cmp_op.loc, hint="lp")
        into.ops.append(mir.MOp(cmp_op.opcode, operands, [result],
                                loc=cmp_op.loc))
        return result

    def false_edge_args(edge_args: List[mir.VReg]) -> List[mir.VReg]:
        return [edge_args[k] if k is not None else v
                for v, k in zip(false_args, false_pos)]

    pre.ops.pop()                     # the entry br
    guard = init_args[0] if subst is None else copy_condition(init_args, pre)
    pre.ops.append(mir.MOp(
        "brc", [guard], [],
        attrs={"true_target": body_name, "true_args": list(init_args),
               "false_target": exit_name,
               "false_args": false_edge_args(init_args)},
        loc=head.loc))
    body.ops.pop()                    # the back-edge br
    back = back_args[0] if subst is None else copy_condition(back_args, body)
    body.ops.append(mir.MOp(
        "brc", [back], [],
        attrs={"true_target": body_name, "true_args": list(back_args),
               "false_target": exit_name,
               "false_args": false_edge_args(back_args)},
        loc=head.loc))
    # the head is unreachable now: its only referents were the two
    # rewritten branches
    function.blocks.remove(head)
    return True


def _loop_predicate_function(function: mir.MFunction
                             ) -> Tuple[int, Dict[str, int]]:
    """Rotate every eligible loop; (rotated, decline-reason histogram).

    The eligible single-body-block loops are a disjoint family (a
    single-block body cannot contain another loop), so one sweep rotates
    them all against one CFG snapshot; a second sweep confirms the fixpoint.
    """
    rotated = 0
    declines: Dict[str, int] = {}
    for _sweep in (0, 1):
        preds, succs = _build_graph(function)
        dom = _dominators(function, preds, succs)
        loops = _natural_loops(function, preds, dom)
        fired = 0
        for head_name, body_set in loops:
            if _rotate_one(function, head_name, body_set, preds, declines):
                rotated += 1
                fired += 1
        if not fired:
            break
    return rotated, declines


# ---------------------------------------------------------------------------
# the stage entry
# ---------------------------------------------------------------------------
def run(module: mir.MModule, options) -> mir.MModule:
    """Run the enabled mir-optimize passes over ``module`` (in place).

    ``options`` is the CompileOptions carrying the A100C_MIRPASS_PRED
    switch (opt-in; the pass is default-off -- see the CompileOptions
    field for the measured reason).  The pass's rewrite counts land in
    ``module.meta['mir_passes']``.
    """
    counts: Dict[str, Dict[str, int]] = {}
    if getattr(options, "mir_loop_predicate", False):
        n = 0
        declines: Dict[str, int] = {}
        for function in module.functions:
            r, d = _loop_predicate_function(function)
            n += r
            for k, v in d.items():
                declines[k] = declines.get(k, 0) + v
        counts["mir-loop-predicate"] = {"rotated": n, "declined": declines}
    else:
        counts["mir-loop-predicate"] = {"enabled": False}
    module.meta["mir_passes"] = counts
    module.renumber()
    return module
