"""Shared TIR rewriting mechanics for the basic passes (T015).

Everything the passes change goes through here so the two structural
invariants of this IR survive every rewrite:

1. **The carried-value reinterpretation rule.**  Inside a loop body a use
   of one of that loop's carried INIT values denotes the CURRENT
   iteration's value (the MIR head parameter overrides it).  A use site
   that is reinterpreted this way must never be rewired to a fixed
   outside value, and an outside value that is itself a carried init
   must never be wired into a body use site.  ``guarded_replace_uses``
   skips exactly those sites, and never touches a loop's carried-init
   slots at all (rewiring an init retroactively changes the meaning of
   every body use of the old value).

2. **The name-based joins.**  Region joins and loop carries resolve by
   SOURCE NAME at the region end (the verifier's lexical scoping).  A
   def that is the final binding of a join/carried name is a protected
   def: it is never removed, and when a value is replaced by a
   value-identical survivor the survivor inherits the replaced value's
   source-name aliases so the joins still resolve (to the same value).
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Set, Tuple

from a100c.ir import tir
from a100c.passes.analyses import LoopStructure, Pos, _child_step

__all__ = ["protected_defs", "guarded_replace_uses", "remove_statement",
           "copy_aliases", "splat_const", "op_key"]


def _final_bindings(module: tir.Module) -> Set[int]:
    """Vids of the region-final name bindings: for every If, both arms'
    final binding of every join name; for every Loop, the body's final
    binding of every carried name.  Those defs must survive every pass
    (the verifier's join lookups and the lowering's back-edge and
    classification machinery read them)."""
    out: Set[int] = set()

    def bind_into(scope: Dict[str, tir.Value], v: tir.Value) -> None:
        for key in v.scope_names():
            scope[key] = v

    def walk(block: tir.Block, scope: Dict[str, tir.Value]) -> None:
        for st in block.statements:
            if isinstance(st, tir.Op):
                for r in st.results:
                    bind_into(scope, r)
            elif isinstance(st, tir.If):
                for arm in (st.then, st.els):
                    arm_scope = dict(scope)
                    walk(arm, arm_scope)
                    for name in st.join_names:
                        v = arm_scope.get(name)
                        if v is not None:
                            out.add(v.vid)
                for jv in st.join_results:
                    bind_into(scope, jv)
            elif isinstance(st, tir.Loop):
                body_scope = dict(scope)
                for _name, init in st.carried:
                    bind_into(body_scope, init)
                walk(st.body, body_scope)
                for name, _ in st.carried:
                    v = body_scope.get(name)
                    if v is not None:
                        out.add(v.vid)
                for jv in st.join_results:
                    bind_into(scope, jv)

    for fn in module.functions:
        root: Dict[str, tir.Value] = {}
        for p in fn.params:
            bind_into(root, p)
        walk(fn.body, root)
    return out


_CACHE_KEY = "_passes_protected_defs"


def protected_defs(module: tir.Module) -> Set[int]:
    """Cached per module object (the pipeline recomputes after each
    mutating pass; the cache key is the module's identity)."""
    cached = getattr(module, _CACHE_KEY, None)
    if cached is not None:
        return cached
    cached = _final_bindings(module)
    try:
        setattr(module, _CACHE_KEY, cached)
    except AttributeError:  # pragma: no cover - plain class
        pass
    return cached


def drop_protected_cache(module: tir.Module) -> None:
    try:
        delattr(module, _CACHE_KEY)
    except AttributeError:
        pass


def copy_aliases(removed: tir.Value, survivor: tir.Value) -> None:
    """The survivor inherits the removed value's source-name aliases so
    name-based region joins still resolve (to the same value: the
    replacement is value-identical by construction)."""
    for name in removed.scope_names():
        if name != survivor.name and name not in survivor.aliases:
            survivor.add_alias(name)


def _iter_use_sites(module: tir.Module):
    """(container, attribute | None, index | None, path, enclosing) over
    every value use site: op operands, if conditions, loop bounds and
    carried inits.  Carried-init slots are yielded with the ``carried``
    marker so the rewriter can skip them.  ``enclosing`` is the chain of
    structured loops the site sits inside -- the position-free enclosure
    the reinterpretation guard reads (statement indices shift under the
    passes' own insertions; the node chain never lies)."""
    def walk(block: tir.Block, base: Pos, chain: tuple):
        for i, st in enumerate(block.statements):
            here = base + (_child_step("op", i),)
            if isinstance(st, tir.Op):
                for j in range(len(st.operands)):
                    yield (st, "operands", j, here, chain)
            elif isinstance(st, tir.If):
                yield (st, "cond", None, here, chain)
                yield from walk(st.then, here + (_child_step("then", 0),),
                                chain)
                yield from walk(st.els, here + (_child_step("else", 0),),
                                chain)
            elif isinstance(st, tir.Loop):
                for slot in ("lower", "upper", "step", "cond"):
                    if getattr(st, slot) is not None:
                        yield (st, slot, None, here, chain)
                for j, (_name, _init) in enumerate(st.carried):
                    yield (st, "carried", j, here, chain)
                yield from walk(st.body, here + (_child_step("body", 0),),
                                chain + (st,))
    for fn in module.functions:
        yield from walk(fn.body, (), ())


def _site_reinterpreted(enclosing: tuple) -> set:
    """The carried-init vids whose meaning at a site enclosed by
    ``enclosing`` is the CURRENT iteration's value (the head-parameter
    override): every enclosing loop's carried inits."""
    out: set = set()
    for loop in enclosing:
        for _name, init in loop.carried:
            out.add(init.vid)
    return out


def count_uses(module: tir.Module, value: tir.Value) -> int:
    """Every remaining reference to ``value``: op operands, region
    conditions, loop bounds and carried-init slots (a value some
    reinterpreted site still references is NOT dead -- its def must
    stay)."""
    if value.producer is None:
        return 1                        # a parameter: always referenced
    n = 0
    for holder, attr, index, _path, _enclosing in _iter_use_sites(module):
        if attr == "operands":
            if holder.operands[index] is value:
                n += 1
        elif attr == "cond":
            if holder.cond is value:
                n += 1
        elif attr in ("lower", "upper", "step"):
            if getattr(holder, attr) is value:
                n += 1
        elif attr == "carried":
            if holder.carried[index][1] is value:
                n += 1
    return n


def guarded_replace_uses(module: tir.Module, old: tir.Value,
                         new: tir.Value, loops: LoopStructure) -> int:
    """Rewire every use of ``old`` to ``new`` EXCEPT:

    * carried-init slots (rewiring an init changes the meaning of every
      body use of the old value retroactively);
    * use sites inside a loop body where ``old`` or ``new`` is a
      carried init of an enclosing loop (the site denotes the current
      iteration's value, not the fixed outside value).

    The enclosure is read from the site's own loop-node chain, never
    from the ``loops`` analysis's recorded positions: the passes mutate
    the module between the analysis and this rewrite (their own
    insertions shift statement indices), and a position-based answer
    silently unguards the reinterpretation (the T026 cholesky_upper
    miscompile).  ``loops`` is kept for signature compatibility.

    Returns the number of sites rewired."""
    if old is new or old.vid == new.vid:
        return 0
    n = 0
    for holder, attr, index, _path, enclosing in _iter_use_sites(module):
        if attr == "operands":
            value = holder.operands[index]
        elif attr == "cond":
            value = holder.cond
        elif attr in ("lower", "upper", "step"):
            value = getattr(holder, attr)
        elif attr == "carried":
            continue                    # never rewire a carried-init slot
        else:                            # pragma: no cover
            continue
        if value is not old:
            continue
        reinterpreted = _site_reinterpreted(enclosing)
        if old.vid in reinterpreted or new.vid in reinterpreted:
            continue
        if attr == "operands":
            ops = list(holder.operands)
            ops[index] = new
            holder.operands = tuple(ops)
        elif attr == "cond":
            holder.cond = new
        else:
            setattr(holder, attr, new)
        n += 1
    return n


def remove_statement(module: tir.Module, target) -> bool:
    """Remove one Op statement from its containing block (region
    statements are never passed here)."""
    def walk(block: tir.Block) -> bool:
        for i, st in enumerate(block.statements):
            if st is target:
                del block.statements[i]
                return True
            if isinstance(st, tir.If):
                if walk(st.then) or walk(st.els):
                    return True
            elif isinstance(st, tir.Loop):
                if walk(st.body):
                    return True
        return False

    for fn in module.functions:
        if walk(fn.body):
            drop_protected_cache(module)
            return True
    return False


def splat_const(value, type_: tir.Type, ref_shape: tir.Shape,
                loc: Optional[tir.SrcLoc]) -> tir.Value:
    """A constant usable as the RHS of a binop against an operand of
    ``ref_shape``: a rank-0 const, broadcast to the operand's extent
    values with all-broadcast flags (exactly the frontend's own
    constant-block materialisation; a rank-0 reference needs no
    broadcast)."""
    c = tir.Op.const(value, type_, loc)
    if not ref_shape:
        return c.result()
    shape = tuple(tir.Extent(e.value, True) for e in ref_shape)
    bc = tir.Op.broadcast(c.result(), shape, loc)
    return bc.result()


def op_key(op: tir.Op) -> Optional[tuple]:
    """The semantic identity of a pure single-def op: two ops with the
    same key compute the same value at the same iteration scope.  None
    for ops that are not pure-value candidates (effects, loads)."""
    if not op.results:
        return None
    if op.op in ("store", "atomic_rmw", "atomic_cas", "debug_barrier"):
        return None
    if op.attrs.get("volatile"):
        return None
    if op.op == "load":
        return None                    # handled by the CSE load proof
    return (
        op.op,
        tuple(o.vid for o in op.operands),
        tuple(sorted((k, repr(v)) for k, v in op.attrs.items())),
        tuple((r.type.kind, r.type.width, r.type.name,
               tuple((e.value, e.broadcast) for e in r.shape))
              for r in op.results),
    )
