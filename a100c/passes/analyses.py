"""The shared analysis owner for the basic passes (T015).

One owner computes and caches every derived fact the passes consume --
dominance, liveness, loop structure and memory effects -- over ONE TIR
module, under a declared invalidation contract (MECH-SHARED-ANALYSIS-
BUNDLE, IR-ANALYSIS-VALIDITY):

* ``AnalysisSuite.get(name)`` NEVER returns a stale result: every cached
  result carries the structural digest of the module it was computed at,
  and a digest mismatch forces recomputation.  A module mutated behind
  the suite's back is still caught (the digest covers ops, operands,
  attributes, results and region structure).
* ``AnalysisSuite.freeze()`` binds results to the current digest: a
  ``FrozenAnalyses`` view raises ``StaleAnalysisError`` once the module
  moves on, so a pass holding a frozen view refuses to run rather than
  reading it (the pass-refusal half of the contract).
* ``AnalysisSuite.invalidate(*names)`` is the declared invalidation
  point: passes declare which analyses their mutations invalidate and
  the pipeline drops them; the digest check remains the enforcement.

The suite is also the single place that knows the lowering's carried-
value reinterpretation rule: inside a loop body, a use of one of that
loop's carried INIT values denotes the CURRENT iteration's value (the
MIR head parameter overrides it -- vectorize.py ``_lower_loop``).  Every
consumer that reasons about values must treat those vids as varying
inside the body; ``reinterpret_inits`` answers exactly that question.

Positions: a statement's position is a tuple of steps -- ``("op", i)``
for the i-th statement of a block, ``("then", i)``/``("else", i)`` for
If arms and ``("body", i)`` for loop bodies, nested outward-in.  In this
structured representation dominance is the path-prefix relation: p
dominates q iff p is a prefix of q (a statement before a region
dominates its interior; an arm's statements dominate nothing outside
the arm; a loop body's statements dominate nothing after the loop --
the body may run zero times).
"""
from __future__ import annotations

import hashlib
from typing import Dict, List, Optional, Set, Tuple

from a100c.ir import tir

__all__ = [
    "AnalysisSuite", "FrozenAnalyses", "StaleAnalysisError",
    "ANALYSIS_NAMES", "Dominance", "Liveness", "LoopStructure", "LoopInfo",
    "MemoryEffects", "Pos", "steps_block",
]

ANALYSIS_NAMES = ("dominance", "liveness", "loops", "memory_effects")

Pos = Tuple[Tuple[str, int], ...]


class StaleAnalysisError(Exception):
    """A frozen analysis view no longer matches the module: the consumer
    must refuse to run on it (never read a stale result)."""

    def __init__(self, name: str, message: str = ""):
        super().__init__(
            f"stale analysis '{name}': the module changed after the "
            f"result was computed{(' ' + message) if message else ''}")
        self.name = name


def _child_step(kind: str, index: int) -> Tuple[str, int]:
    return (kind, index)


# ---------------------------------------------------------------------------
# the analyses
# ============================================================================

class Dominance:
    """Path-prefix dominance over the structured region tree, plus each
    value's defining position (parameters define at the function root)."""

    def __init__(self, module: tir.Module):
        self.def_path: Dict[int, Pos] = {}
        self._roots: List[Pos] = []
        for fn in module.functions:
            root: Pos = ()
            for p in fn.params:
                self.def_path.setdefault(p.vid, root)
            self._walk(fn.body, root)

    def _walk(self, block: tir.Block, base: Pos) -> None:
        for i, st in enumerate(block.statements):
            here = base + (_child_step("op", i),)
            if isinstance(st, tir.Op):
                for r in st.results:
                    self.def_path[r.vid] = here
            elif isinstance(st, tir.If):
                if st.cond.producer is not None:
                    self.def_path.setdefault(st.cond.vid, base)
                self._walk(st.then, here + (_child_step("then", 0),))
                self._walk(st.els, here + (_child_step("else", 0),))
                for jv in st.join_results:
                    self.def_path[jv.vid] = here
            elif isinstance(st, tir.Loop):
                for bound in (st.lower, st.upper, st.step, st.cond):
                    if bound is not None and bound.producer is not None:
                        self.def_path.setdefault(bound.vid, base)
                for _, init in st.carried:
                    if init.producer is not None:
                        self.def_path.setdefault(init.vid, base)
                self._walk(st.body, here + (_child_step("body", 0),))
                for jv in st.join_results:
                    self.def_path[jv.vid] = here

    def dominates(self, p: Pos, q: Pos) -> bool:
        """Does position p dominate position q?

        Two cases in the structured tree: p is a prefix of q (p is the
        region statement containing q, or p == q) -- a region statement
        dominates its whole interior; or p and q are two statements of
        the SAME block (they agree on every step but the last, both
        ``("op", i)``) and p's index is smaller -- an earlier statement
        dominates a later one.  Everything else (an arm's statements vs
        the other arm or the code after the region; a loop body's
        statements vs the code after the loop -- zero-trip) does not
        dominate."""
        if p == q:
            return True
        if len(p) < len(q) and q[:len(p)] == p:
            return True
        if len(p) == len(q) and len(p) > 0:
            k = len(p) - 1
            if p[:k] == q[:k] and p[k][0] == "op" and q[k][0] == "op" \
                    and p[k][1] < q[k][1]:
                return True
        return False

    def value_dominates(self, a: tir.Value, b: tir.Value) -> bool:
        pa = self.def_path.get(a.vid)
        pb = self.def_path.get(b.vid)
        if pa is None or pb is None:
            return False
        return self.dominates(pa, pb)


class _UseSite:
    __slots__ = ("path", "op", "slot")

    def __init__(self, path: Pos, op, slot: str):
        self.path = path
        self.op = op
        self.slot = slot


class Liveness:
    """Every value's use sites (operands, region conditions, loop bounds,
    carried initialisers) and the region-final name bindings the TIR
    verifier's name-based joins resolve (the lowering's own scoping rule
    simulated on TIR -- the DCE root set)."""

    def __init__(self, module: tir.Module):
        self.uses: Dict[int, List[_UseSite]] = {}
        # name -> value at each block end, mirroring the verifier's
        # lexical scoping (arms get copies; joins bind in the parent)
        self.arm_final: Dict[Pos, Dict[str, tir.Value]] = {}
        self.loop_final: Dict[Pos, Dict[str, tir.Value]] = {}
        for fn in module.functions:
            scope: Dict[str, tir.Value] = {p.name: p for p in fn.params}
            for p in fn.params:
                for key in p.scope_names():
                    scope[key] = p
            self._walk(fn.body, (), scope)

    def _bind(self, scope: Dict[str, tir.Value], value: tir.Value) -> None:
        for key in value.scope_names():
            scope[key] = value

    def _use(self, v: tir.Value, path: Pos, op, slot: str) -> None:
        self.uses.setdefault(v.vid, []).append(_UseSite(path, op, slot))

    def _walk(self, block: tir.Block, base: Pos,
              scope: Dict[str, tir.Value]) -> None:
        for i, st in enumerate(block.statements):
            here = base + (_child_step("op", i),)
            if isinstance(st, tir.Op):
                for j, o in enumerate(st.operands):
                    self._use(o, here, st, f"operand{j}")
                for r in st.results:
                    self._bind(scope, r)
            elif isinstance(st, tir.If):
                self._use(st.cond, here, st, "cond")
                then_scope = dict(scope)
                else_scope = dict(scope)
                self._walk(st.then, here + (_child_step("then", 0),),
                           then_scope)
                self._walk(st.els, here + (_child_step("else", 0),),
                           else_scope)
                self.arm_final[here + (_child_step("then", 0),)] = then_scope
                self.arm_final[here + (_child_step("else", 0),)] = else_scope
                for name, jv in zip(st.join_names, st.join_results):
                    scope[name] = jv
                    self._bind(scope, jv)
            elif isinstance(st, tir.Loop):
                for slot, bound in (("lower", st.lower), ("upper", st.upper),
                                    ("step", st.step), ("cond", st.cond)):
                    if bound is not None:
                        self._use(bound, here, st, slot)
                for name, init in st.carried:
                    self._use(init, here, st, "carried")
                    scope[name] = init
                    self._bind(scope, init)
                body_scope = dict(scope)
                self._walk(st.body, here + (_child_step("body", 0),),
                           body_scope)
                self.loop_final[here + (_child_step("body", 0),)] = body_scope
                for name, jv in zip(
                        [n for n, _ in st.carried], st.join_results):
                    scope[name] = jv
                    self._bind(scope, jv)

    def has_uses(self, value: tir.Value) -> bool:
        return bool(self.uses.get(value.vid))

    def use_count(self, value: tir.Value) -> int:
        return len(self.uses.get(value.vid, ()))


class LoopInfo:
    """One structured loop: its position, carried initialisers, the values
    defined inside its body (nested regions included) and its memory
    effects (never hoisted -- recorded for the decline reasons)."""

    __slots__ = ("node", "path", "carried_inits", "body_defined",
                 "is_while", "index")

    def __init__(self, node: tir.Loop, path: Pos, index: int):
        self.node = node
        self.path = path
        self.index = index
        self.carried_inits: Set[int] = {init.vid for _, init in node.carried}
        self.body_defined: Set[int] = set()
        self.is_while = node.cond is not None


class LoopStructure:
    """Every loop with its body-defined values; answers the
    reinterpretation question (``invariant_at``) and enclosure."""

    def __init__(self, module: tir.Module):
        self.loops: List[LoopInfo] = []
        self._by_path: Dict[Pos, LoopInfo] = {}
        for fn in module.functions:
            self._walk(fn.body, ())

    def _walk(self, block: tir.Block, base: Pos) -> None:
        for i, st in enumerate(block.statements):
            here = base + (_child_step("op", i),)
            if isinstance(st, tir.Op):
                continue
            if isinstance(st, tir.If):
                self._walk(st.then, here + (_child_step("then", 0),))
                self._walk(st.els, here + (_child_step("else", 0),))
            elif isinstance(st, tir.Loop):
                info = LoopInfo(st, here, len(self.loops))
                self.loops.append(info)
                self._by_path[here] = info
                self._collect(st.body, info.body_defined)
                self._walk(st.body, here + (_child_step("body", 0),))

    def _collect(self, block: tir.Block, out: Set[int]) -> None:
        for st in block.statements:
            if isinstance(st, tir.Op):
                for r in st.results:
                    out.add(r.vid)
            elif isinstance(st, tir.If):
                self._collect(st.then, out)
                self._collect(st.els, out)
                for jv in st.join_results:
                    out.add(jv.vid)
            elif isinstance(st, tir.Loop):
                self._collect(st.body, out)
                for jv in st.join_results:
                    out.add(jv.vid)

    def enclosing(self, path: Pos) -> List[LoopInfo]:
        """Loops whose body contains ``path`` (innermost last)."""
        out = []
        for info in self.loops:
            body_base = info.path + (_child_step("body", 0),)
            if path[:len(body_base)] == body_base:
                out.append(info)
        return out

    def body_path(self, info: LoopInfo) -> Pos:
        return info.path + (_child_step("body", 0),)

    def reinterpret_inits(self, path: Pos) -> Set[int]:
        """The carried-init vids whose meaning at ``path`` is the CURRENT
        iteration's value (uses inside the body are reinterpreted by the
        lowering's head-parameter override)."""
        out: Set[int] = set()
        for info in self.enclosing(path):
            out |= info.carried_inits
        return out

    def inits_of(self, path: Pos) -> Set[int]:
        """The carried-init vids of the innermost loop whose body contains
        ``path`` (for CSE's availability scoping)."""
        inner = self.enclosing(path)
        return inner[-1].carried_inits if inner else set()


#: op codes that read or write memory or order it (never CSE-reusable,
#: never hoisted); loads are handled separately by the CSE proof
_EFFECT_OPS = {"store", "atomic_rmw", "atomic_cas", "debug_barrier"}


class MemoryEffects:
    """Every memory effect with its position, plus the constant-offset
    alias proof (the ``effect/alias proof`` half of CSE's load reuse)."""

    def __init__(self, module: tir.Module):
        #: (path, op) for every store/atomic/barrier/volatile-load, in
        #: a deterministic walk order
        self.effects: List[Tuple[Pos, tir.Op]] = []
        self._effect_paths: Dict[Pos, tir.Op] = {}
        for fn in module.functions:
            self._walk(fn.body, ())

    def _walk(self, block: tir.Block, base: Pos) -> None:
        for i, st in enumerate(block.statements):
            here = base + (_child_step("op", i),)
            if isinstance(st, tir.Op):
                if st.op in _EFFECT_OPS or st.attrs.get("volatile"):
                    self.effects.append((here, st))
                    self._effect_paths[here] = st
            elif isinstance(st, tir.If):
                self._walk(st.then, here + (_child_step("then", 0),))
                self._walk(st.els, here + (_child_step("else", 0),))
            elif isinstance(st, tir.Loop):
                self._walk(st.body, here + (_child_step("body", 0),))

    # -- the tree-interval query ------------------------------------------

    def effects_between(self, earlier: Pos, later: Pos) -> List[tir.Op]:
        """Effects that execute strictly between two positions in the
        structured order.  Positions are statement paths; plain tuple
        order is execution order in this representation (a statement
        precedes its subtree, statements in a block order by index), so
        an effect inside any region lying between the two statements
        counts: a write in an intervening if-arm may execute, a write in
        an intervening loop body executes on every iteration between
        them."""
        return [op for path, op in self.effects if earlier < path < later]

    # -- the constant-offset alias proof ----------------------------------

    @staticmethod
    def _decompose(ptr: tir.Value) -> Optional[Tuple[int, int]]:
        """(base parameter vid, constant element offset) of a pointer
        whose address is a rank-0 constant offset over one base, else
        None (unprovable -- including block offsets, where different
        lanes address different elements)."""
        if ptr.producer is None:
            return (ptr.vid, 0)
        if ptr.producer.op == "ptradd":
            base = MemoryEffects._decompose(ptr.producer.operands[0])
            if base is None:
                return None
            off = ptr.producer.operands[1]
            if off.rank != 0 or off.producer is None \
                    or off.producer.op != "const" \
                    or not isinstance(off.producer.attrs.get("value"), int):
                return None
            return (base[0], base[1] + off.producer.attrs["value"])
        return None

    @staticmethod
    def provably_disjoint(a: tir.Value, b: tir.Value) -> bool:
        """Two pointer operands address disjoint element ranges: the same
        base parameter with constant offsets and non-overlapping flat
        extents.  Different bases never prove disjointness (distinct
        kernel arguments may alias -- in-place operators pass the same
        buffer twice); non-constant offsets never prove it either."""
        da = MemoryEffects._decompose(a)
        db = MemoryEffects._decompose(b)
        if da is None or db is None or da[0] != db[0]:
            return False
        na = tir.flat_extent(a.shape)
        nb = tir.flat_extent(b.shape)
        if na is None or nb is None:
            return False
        return da[1] + na <= db[1] or db[1] + nb <= da[1]


# ---------------------------------------------------------------------------
# the suite
# ============================================================================

def _digest_op(digest, st) -> None:
    if isinstance(st, tir.Op):
        digest.update(f"op|{st.op}|".encode())
        digest.update(",".join(str(o.vid) for o in st.operands).encode())
        digest.update("|".join(f"{k}={v!r}" for k, v in sorted(
            st.attrs.items(), key=lambda kv: kv[0])).encode())
        digest.update("|".join(
            f"{r.vid}:{r.type.kind}{r.type.width}{r.type.name}"
            f"{''.join(f'{e.value}b' if e.broadcast else str(e.value) for e in r.shape)}"
            for r in st.results).encode())
        return
    if isinstance(st, tir.If):
        digest.update(f"if|{st.cond.vid}|".encode())
        digest.update(",".join(st.join_names).encode())
        digest.update(",".join(str(v.vid) for v in st.join_results).encode())
        for arm in (st.then, st.els):
            for s in arm.statements:
                _digest_op(digest, s)
        return
    if isinstance(st, tir.Loop):
        tag = "while" if st.cond is not None else "range"
        bounds = [b.vid for b in (st.lower, st.upper, st.step, st.cond)
                  if b is not None]
        digest.update(f"loop|{tag}|".encode())
        digest.update(",".join(str(v) for v in bounds).encode())
        digest.update("|".join(f"{n}:{i.vid}" for n, i in st.carried).encode())
        digest.update(",".join(str(v.vid) for v in st.join_results).encode())
        for s in st.body.statements:
            _digest_op(digest, s)


def module_digest(module: tir.Module) -> str:
    """A structural digest of the module: every statement, operand vid,
    attribute, result identity and region join.  Any mutation the passes
    perform (statement insertion/removal/reordering, operand rewiring,
    attribute changes, region rewrites) changes it."""
    digest = hashlib.sha256()
    for fn in module.functions:
        digest.update(f"fn|{fn.name}|".encode())
        digest.update(",".join(f"{p.vid}:{p.type.name}" for p in fn.params)
                      .encode())
        for st in fn.body.statements:
            _digest_op(digest, st)
    return digest.hexdigest()


_COMPUTERS = {
    "dominance": Dominance,
    "liveness": Liveness,
    "loops": LoopStructure,
    "memory_effects": MemoryEffects,
}


class FrozenAnalyses:
    """A digest-bound view: served through the suite (which never
    returns a stale result) but REFUSED -- never silently re-served --
    once the module changed after the freeze."""

    def __init__(self, suite: "AnalysisSuite", digest: str):
        self._suite = suite
        self._digest = digest

    def get(self, name: str):
        if name not in _COMPUTERS:
            raise KeyError(f"unknown analysis '{name}'")
        if self._suite.module_digest() != self._digest:
            raise StaleAnalysisError(
                name, "(the frozen view predates the mutation)")
        return self._suite.get(name)

    @property
    def digest(self) -> str:
        return self._digest


class AnalysisSuite:
    """The single owner of every derived analysis over one TIR module."""

    def __init__(self, module: tir.Module):
        self.module = module
        self._cache: Dict[str, object] = {}
        self._digests: Dict[str, str] = {}
        self._current: Optional[str] = None
        self.invalidate()

    # -- the contract ------------------------------------------------------

    def module_digest(self) -> str:
        fresh = module_digest(self.module)
        if self._current is None or fresh != self._current:
            self._current = fresh
        return fresh

    def get(self, name: str):
        """Never stale: recompute when the module digest moved (or the
        analysis was explicitly invalidated)."""
        if name not in _COMPUTERS:
            raise KeyError(f"unknown analysis '{name}'")
        digest = self.module_digest()
        cached = self._cache.get(name)
        if cached is None or self._digests.get(name) != digest:
            cached = _COMPUTERS[name](self.module)
            self._cache[name] = cached
            self._digests[name] = digest
        return cached

    def freeze(self) -> FrozenAnalyses:
        """Bind a view to the current digest (results compute lazily
        through the suite; the view refuses once the module moves)."""
        return FrozenAnalyses(self, self.module_digest())

    def invalidate(self, *names: str) -> None:
        """The declared invalidation point: drop the named analyses (all
        of them when no names are given)."""
        if not names:
            names = tuple(ANALYSIS_NAMES)  # type: ignore[assignment]
        for name in names:
            self._cache.pop(name, None)
            self._digests.pop(name, None)

    def force_result(self, name: str, result) -> None:
        """Plant a result bound to the CURRENT digest (the IR-ANALYSIS-
        VALIDITY control: a deliberately wrong-but-fresh answer, used by
        tests to prove a dependent pass actually consumes the analysis).
        Production code never calls this."""
        if name not in _COMPUTERS:
            raise KeyError(f"unknown analysis '{name}'")
        self._cache[name] = result
        self._digests[name] = self.module_digest()
