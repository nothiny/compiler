"""Allocation (BE-ALLOCATION-CORRECTNESS): every live value gets a location.

32 GPRs (minus the reserved ABI registers) and the 32 x 128 B vector
register file (F023/F028/F039/F041).  Interference comes from a real
liveness analysis over the real CFG (backward dataflow to a fixpoint, so
values live across back edges keep their whole-loop live ranges -- the
AM0128 prior), never from a linear scan of instruction order.

Register classes share the physical files they occupy:
  - GPR scalars        -> t0-t6, a1-a7, s1-s11 (a0/ra/sp/gp/tp/zero reserved;
    a0 carries the launch pointer at entry and call arguments);
  - vector m1 / masks  -> v1..v31 (v0 is the fixed working mask, never
    allocated; fixed v0 values are pre-colored);
  - vector m2 groups   -> even-aligned pairs (v2, v4, ..., v30).

Interference is recorded at definition points (a def interferes with
everything live after it), at block entries (block parameters interfere
with each other and with everything live-in), and across calls
(a100rt_stage_barrier clobbers every caller-saved GPR, psABI F045, so
values live across a call avoid those registers).

Exceeding a file is a compiler-owned spill/split decision (the vector file
has no architectural spill, F041): the live range is split -- the value is
stored to a stack slot after each definition (block parameters included,
stored at block entry) and reloaded into a fresh short-range value before
each use -- and coloring restarts (bounded rounds).  Vector spill is only
legal in full-vl regions (the spill sequence re-establishes vlmax at the
value's (SEW, LMUL)); elsewhere, and for masks, the allocator refuses with
a located diagnostic (a bounded, declared refusal, see ABSENT_FORMS).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from a100c.ir import mir
from a100c.target import TargetModel

__all__ = ["AllocationError", "Allocation", "allocate", "GPR_NAMES",
           "ALLOCATABLE_GPRS", "CALLER_SAVED"]

#: ABI register names by index (RISC-V psABI, lp64d; F045)
GPR_NAMES = ["zero", "ra", "sp", "gp", "tp",
             "t0", "t1", "t2", "s0", "s1",
             "a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7",
             "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11",
             "t3", "t4", "t5", "t6"]

#: allocatable GPR indices (a0 carries launch/args; ra/sp/gp/tp/zero reserved)
ALLOCATABLE_GPRS = [5, 6, 7, 9, 11, 12, 13, 14, 15, 16, 17,
                    18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
                    28, 29, 30, 31]

#: clobbered by every call (t0-t6, a0-a7)
CALLER_SAVED = {GPR_NAMES[i] for i in
                [5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17, 28, 29, 30, 31]}


class AllocationError(Exception):
    def __init__(self, loc, message: str):
        super().__init__(f"allocation: {message}"
                         + (f" (at {loc})" if loc else ""))
        self.loc = loc
        self.message = message


@dataclass
class Allocation:
    """The allocation result: every vreg has a physical location."""

    #: vreg rid -> physical name ('t0', 's3', 'v5', 'v0')
    assignment: Dict[int, str] = field(default_factory=dict)
    #: vreg rid -> (kind, span) for budget accounting
    shapes: Dict[int, Tuple[str, int]] = field(default_factory=dict)
    #: vreg rid -> spill slot index (spilled values only)
    spilled: Dict[int, int] = field(default_factory=dict)
    #: slot -> byte size
    slots: List[int] = field(default_factory=list)
    #: statistics reported against the budget (TGT-RESOURCE-BUDGET)
    stats: Dict[str, object] = field(default_factory=dict)

    def phys(self, reg: mir.VReg) -> str:
        got = self.assignment.get(reg.rid)
        if got is None:
            raise AllocationError(reg.loc,
                                  f"vreg {reg.name} has no physical location")
        return got

    def frame_bytes(self) -> int:
        return (sum(self.slots) + 15 + 16) & ~15

    def describe(self) -> dict:
        return {"assignment": dict(self.assignment),
                "spilled": dict(self.spilled),
                "slots": list(self.slots),
                "stats": dict(self.stats)}


# ---------------------------------------------------------------------------
# Liveness over the real CFG
# ---------------------------------------------------------------------------


def _block_uses_defs(fn: mir.MFunction):
    """Per-block use/def sets; branch arguments are uses of the terminator."""
    uses: Dict[str, Set[int]] = {b.name: set() for b in fn.blocks}
    defs: Dict[str, Set[int]] = {b.name: set() for b in fn.blocks}
    for b in fn.blocks:
        for p in b.params:
            defs[b.name].add(p.rid)
        for op in b.ops:
            for o in op.operands:
                if o.rid not in defs[b.name]:
                    uses[b.name].add(o.rid)
            for r in op.results:
                defs[b.name].add(r.rid)
        for _target, args in b.branch_args().items():
            for a in args:
                if a.rid not in defs[b.name]:
                    uses[b.name].add(a.rid)
    return uses, defs


def _live_in(fn: mir.MFunction) -> Dict[str, Set[int]]:
    """live-in per block, iterated to a fixpoint (back edges included)."""
    uses, defs = _block_uses_defs(fn)
    succs = {b.name: b.successors() for b in fn.blocks}
    live_in: Dict[str, Set[int]] = {b.name: set() for b in fn.blocks}
    changed = True
    while changed:
        changed = False
        for b in reversed(fn.blocks):
            out: Set[int] = set()
            for s in succs[b.name]:
                out |= live_in[s]
            live = (out | uses[b.name]) - defs[b.name]
            if live != live_in[b.name]:
                live_in[b.name] = live
                changed = True
    return live_in


def _live_before(fn: mir.MFunction) -> Dict[str, List[Set[int]]]:
    """Per-block list ``before[i]`` = the live set immediately before op i,
    plus ``before[N]`` = the block-exit (live-out) set."""
    live_in = _live_in(fn)
    succs = {b.name: b.successors() for b in fn.blocks}
    result: Dict[str, List[Set[int]]] = {}
    for b in fn.blocks:
        out: Set[int] = set()
        for s in succs[b.name]:
            out |= live_in[s]
        live = set(out)
        befores: List[Set[int]] = [set(live)]          # before op N (exit)
        for op in reversed(b.ops):
            for r in op.results:
                live.discard(r.rid)
            for o in op.operands:
                live.add(o.rid)
            if op is b.ops[-1]:
                for _target, args in b.branch_args().items():
                    for a in args:
                        live.add(a.rid)
            befores.append(set(live))
        befores.reverse()                              # before[i] for op i
        result[b.name] = befores
    return result


def _failure_live_set(fn: mir.MFunction, failed: Optional[mir.VReg]) -> Set[int]:
    """The rids live at the failing value's definition (the pressure
    source the non-convergence refusal names; empty when the value has
    no resolvable definition)."""
    if failed is None:
        return set()
    befores = _live_before(fn)
    for b in fn.blocks:
        for p in b.params:
            if p.rid == failed.rid:
                return set(befores[b.name][0])
        for i, op in enumerate(b.ops):
            if any(r.rid == failed.rid for r in op.results):
                after = befores[b.name][i + 1] if i + 1 <= len(b.ops) \
                    else befores[b.name][-1]
                return set(after)
    return set()


# ---------------------------------------------------------------------------
# Interference
# ---------------------------------------------------------------------------


def _loop_depths(fn: mir.MFunction) -> Dict[str, int]:
    index = {b.name: i for i, b in enumerate(fn.blocks)}
    headers = {s for b in fn.blocks for s in b.successors()
               if s in index and index[s] <= index[b.name]}
    depth = {b.name: 0 for b in fn.blocks}
    for h in headers:
        stack = [h]
        while stack:
            n = stack.pop()
            for b in fn.blocks:
                if n in b.successors() and depth[b.name] == 0:
                    depth[b.name] = 1
                    stack.append(b.name)
    return depth


def _interference(fn: mir.MFunction) -> Tuple[Dict[int, Set[int]], Dict[int, Set[str]]]:
    """The interference graph and the per-value physical avoid-sets."""
    befores = _live_before(fn)
    graph: Dict[int, Set[int]] = {}
    avoid: Dict[int, Set[str]] = {}

    def touch(r: mir.VReg) -> None:
        graph.setdefault(r.rid, set())
        avoid.setdefault(r.rid, set())

    def edge(a: int, b: int) -> None:
        if a != b:
            graph.setdefault(a, set()).add(b)
            graph.setdefault(b, set()).add(a)

    for b in fn.blocks:
        n = len(b.ops)
        # block-entry: params interfere with each other and with live-in
        entry_live = befores[b.name][0] if n else befores[b.name][0]
        for p in b.params:
            touch(p)
            for other in b.params:
                edge(p.rid, other.rid)
            for rid in entry_live:
                edge(p.rid, rid)
        for i, op in enumerate(b.ops):
            after = befores[b.name][i + 1] if i + 1 <= n else befores[b.name][-1]
            for r in op.results:
                touch(r)
                for rid in after:
                    edge(r.rid, rid)
                # mixed-LMUL vector ops (the widening address form: an m1
                # source feeding an m2 destination; an m2 index feeding an
                # m1 load result): the destination group must not overlap
                # ANY source group, even a dying one -- the hardware reads
                # the whole source group while writing the destination
                # group (a probe-found illegal-instruction form)
                for o in op.operands:
                    if o.is_vector() and r.is_vector() \
                            and r.type.lmul != o.type.lmul:
                        edge(r.rid, o.rid)
            for o in op.operands:
                touch(o)
            if op.opcode in ("callbarrier", "vmath"):
                # a100rt_stage_barrier and the libm calls behind vmath
                # clobber every caller-saved GPR (psABI, F045), so values
                # live across them avoid those registers
                for rid in after:
                    avoid.setdefault(rid, set()).update(CALLER_SAVED)
            if op.opcode == "vloadix":
                # T014: the indexed load reads its index vector while
                # writing the destination -- vd == vs2 is a broken form
                # under the pinned QEMU (probed: SIGILL; the mixed-LMUL
                # case is already covered above, the same-LMUL narrow
                # index class needed the explicit edge)
                idx = op.operands[1] if len(op.operands) >= 2 else None
                if idx is not None and idx.is_vector():
                    for r in op.results:
                        if r.is_vector():
                            edge(r.rid, idx.rid)
            if op.opcode == "vrgather":
                # RVV vrgather: the destination must not overlap either
                # source (the index is read while the destination is
                # written -- vd == vs1 is an illegal form the hardware
                # traps on)
                for o in op.operands:
                    for r in op.results:
                        edge(r.rid, o.rid)
            if op.opcode == "vfmacc":
                # T013: vfmacc reads vs1/vs2 while accumulating into vd --
                # the destination group must not overlap either source
                # (the third operand z legitimately shares vd: the emitter
                # pre-copies it there)
                for o in op.operands[:2]:
                    for r in op.results:
                        edge(r.rid, o.rid)
            if op.opcode in ("vfncvt", "vfwcvt", "vmovv"):
                # T012: the widening/narrowing converts and the register
                # move read their source group while writing the
                # destination -- vd overlapping vs2 is an illegal form on
                # this target (probed: SIGILL)
                for o in op.operands:
                    for r in op.results:
                        edge(r.rid, o.rid)
        for _target, args in b.branch_args().items():
            for a in args:
                touch(a)
            for i, a in enumerate(args):
                for c in args[i + 1:]:
                    edge(a.rid, c.rid)
    return graph, avoid


def _file_of(reg: mir.VReg) -> str:
    return "gpr" if reg.is_scalar() else "vec"


def _candidates(reg: mir.VReg, target: TargetModel) -> List[int]:
    if reg.is_scalar():
        return list(ALLOCATABLE_GPRS)
    if reg.is_mask() or reg.type.lmul == 1:
        return list(range(1, target.vector_registers))
    # T029: LMUL > 1 groups allocate as naturally aligned register
    # groups (vN with N % lmul == 0; RVV requires group bases aligned to
    # the group size), v0 reserved as the working mask.  m4 groups cover
    # v4..v28 (7 slots), m8 v8..v24 (3 slots) -- the whole legal LMUL
    # range fits the 32 x 128 B file and the interference coloring owns
    # the budget (the plan's chunk decision already bounded its demand
    # to the same file)
    lmul = reg.type.lmul
    if lmul not in (2, 4, 8):
        raise AllocationError(reg.loc,
                              f"vector LMUL {lmul} is not a legal register "
                              "group (1/2/4/8)")
    return list(range(lmul, target.vector_registers, lmul))


def _phys_name(reg: mir.VReg, index: int) -> str:
    return GPR_NAMES[index] if reg.is_scalar() else f"v{index}"


def _all_values(fn: mir.MFunction) -> List[mir.VReg]:
    out: List[mir.VReg] = []
    seen: Set[int] = set()
    for b in fn.blocks:
        for p in b.params:
            if p.rid not in seen:
                seen.add(p.rid)
                out.append(p)
        for op in b.ops:
            for r in op.results:
                if r.rid not in seen:
                    seen.add(r.rid)
                    out.append(r)
    return out


def _try_color(fn: mir.MFunction, target: TargetModel,
               fixed: Dict[int, str]) -> Tuple[Optional[Dict[int, str]],
                                               Optional[mir.VReg]]:
    """Greedy graph coloring by spill weight.

    Returns (assignment, None) on success or (None, failing_value) when a
    value cannot be colored -- the failing value is the spill victim the
    caller splits (targeting the actual pressure, not a guess)."""
    graph, avoid = _interference(fn)
    use_counts: Dict[int, int] = {}
    for b in fn.blocks:
        for op in b.ops:
            for o in op.operands:
                use_counts[o.rid] = use_counts.get(o.rid, 0) + 1
        for _target, args in b.branch_args().items():
            for a in args:
                use_counts[a.rid] = use_counts.get(a.rid, 0) + 1
    depth = _loop_depths(fn)
    values = _all_values(fn)
    # MECH-COMPILE-COST-LINEAR: every value's defining block as one
    # indexed map (a full _def_block scan per value made the weight
    # build quadratic; the big unrolled bodies -- complex_svd's
    # static_range nest -- spent the whole compile budget inside it,
    # and _try_color re-runs it per spill round)
    def_block: Dict[int, str] = {}
    for b in fn.blocks:
        for p in b.params:
            def_block.setdefault(p.rid, b.name)
        for op in b.ops:
            for r in op.results:
                def_block.setdefault(r.rid, b.name)
    weights = {v.rid: (use_counts.get(v.rid, 0) + 1)
               * (10.0 ** depth.get(def_block.get(v.rid, ""), 0))
               for v in values}

    assignment: Dict[int, str] = {}
    for v in values:
        if v.rid in fixed:
            assignment[v.rid] = fixed[v.rid]

    # the full physical span of every already-assigned value (an m2 value
    # at v2 occupies v2 and v3: a span-1 neighbour must not land on v3 --
    # the interference graph records the base name only)
    spans: Dict[int, int] = {v.rid: (v.type.lmul if v.is_vector() else 1)
                             for v in values}

    def _group_names(name: str, span: int) -> List[str]:
        if span <= 1 or not name.startswith("v"):
            return [name]
        try:
            base = int(name[1:])
        except ValueError:
            return [name]
        return [f"v{base + k}" for k in range(span)]

    for reg in sorted(values, key=lambda v: (-weights[v.rid], v.rid)):
        if reg.rid in fixed:
            continue
        taken: Set[str] = set()
        for n in graph.get(reg.rid, ()):
            name = assignment.get(n)
            if name is not None:
                taken.update(_group_names(name, spans.get(n, 1)))
        blocked = avoid.get(reg.rid, set())
        span = reg.type.lmul if reg.is_vector() else 1
        chosen = None
        for idx in _candidates(reg, target):
            names = ([_phys_name(reg, idx)] if span == 1
                     else [f"v{idx + k}" for k in range(span)])
            if any(nm in taken or nm in blocked for nm in names):
                continue
            chosen = names[0]
            break
        if chosen is None:
            return None, reg
        assignment[reg.rid] = chosen
    return assignment, None


def _def_block(fn: mir.MFunction, reg: mir.VReg) -> str:
    for b in fn.blocks:
        if any(p.rid == reg.rid for p in b.params):
            return b.name
        for op in b.ops:
            if any(r.rid == reg.rid for r in op.results):
                return b.name
    return ""


# ---------------------------------------------------------------------------
# Spill / split
# ---------------------------------------------------------------------------


def _const_full_regions(fn: mir.MFunction, target: TargetModel) -> Set[Tuple[int, int]]:
    """(sew, lmul) regions whose vsetvli AVL is a constant equal to vlmax
    (the only regions where a vector spill is legal in this slice)."""
    consts: Dict[int, int] = {}
    for b in fn.blocks:
        for op in b.ops:
            if op.opcode == "sconst":
                consts[op.results[0].rid] = op.attrs["value"]
    full: Set[Tuple[int, int]] = set()
    for b in fn.blocks:
        for op in b.ops:
            if op.opcode == "vsetvli":
                avl = op.operands[0]
                if avl.rid in consts and consts[avl.rid] == \
                        target.vlmax(op.attrs["sew"], op.attrs["lmul"]):
                    full.add((op.attrs["sew"], op.attrs["lmul"]))
    return full


def _spill_attrs(reg: mir.VReg, slot: int) -> dict:
    if reg.is_vector():
        return {"slot": slot, "sew": reg.type.sew, "lmul": reg.type.lmul}
    return {"slot": slot}


def _split_value(fn: mir.MFunction, reg: mir.VReg, slot: int) -> bool:
    """Split one live range: store after every definition (block parameters
    get a store at block entry), reload before every use.  Returns False
    when the split is not implementable."""
    if reg.is_mask():
        return False
    if reg.is_vector() and reg.type.lmul not in (1, 2, 4, 8):
        return False
    fresh = [0]
    for b in fn.blocks:
        new_ops: List[mir.MOp] = []
        for p in b.params:
            if p.rid == reg.rid:
                new_ops.append(mir.MOp(
                    "vspill" if reg.is_vector() else "sspill", [p], [],
                    attrs=_spill_attrs(reg, slot), loc=p.loc))
        for i, op in enumerate(b.ops):
            is_term = op is b.ops[-1]
            uses_it = any(o.rid == reg.rid for o in op.operands)
            if is_term:
                uses_it = uses_it or any(
                    a.rid == reg.rid
                    for args in b.branch_args().values() for a in args)
            if uses_it:
                fresh[0] += 1
                value = mir.VReg(reg.type, name=f"{reg.name}.r{fresh[0]}",
                                 loc=reg.loc)
                new_ops.append(mir.MOp(
                    "vreload" if reg.is_vector() else "sreload", [], [value],
                    attrs=_spill_attrs(reg, slot), loc=op.loc))
                op.operands = tuple(value if o.rid == reg.rid else o
                                    for o in op.operands)
                if is_term:
                    op.attrs = dict(op.attrs)
                    for key in ("args", "true_args", "false_args"):
                        if key in op.attrs:
                            op.attrs[key] = [
                                value if a.rid == reg.rid else a
                                for a in op.attrs[key]]
            new_ops.append(op)
            for r in op.results:
                if r.rid == reg.rid:
                    new_ops.append(mir.MOp(
                        "vspill" if reg.is_vector() else "sspill", [r], [],
                        attrs=_spill_attrs(reg, slot), loc=r.loc))
        b.ops = new_ops
    return True


def _reload_defs(fn: mir.MFunction) -> Set[int]:
    """rids defined by a spill reload (values whose live range is already
    minimal: the reload sits immediately before its single use)."""
    out: Set[int] = set()
    for b in fn.blocks:
        for op in b.ops:
            if op.opcode in ("sreload", "vreload"):
                out.update(r.rid for r in op.results)
    return out


def _const_values(fn: mir.MFunction) -> Dict[int, int]:
    """rid -> value for scalar constants: every def is an ``sconst``
    carrying the same value and the value is not a block parameter (a
    rematerializable constant -- T029's measured pressure source: the
    matrix lane hoists ~10 such constants, live across whole loop bodies
    with up to 27 uses each)."""
    def_values: Dict[int, List[int]] = {}
    params = {p.rid for b in fn.blocks for p in b.params}
    for b in fn.blocks:
        for op in b.ops:
            if op.opcode != "sconst":
                continue
            for r in op.results:
                if not r.is_scalar() or r.rid in params:
                    continue
                value = op.attrs.get("value")
                if not isinstance(value, int):
                    continue
                def_values.setdefault(r.rid, []).append(value)
    return {rid: values[0] for rid, values in def_values.items()
            if len(set(values)) == 1}


def _remat_constant(fn: mir.MFunction, reg: mir.VReg,
                    value: int) -> Set[int]:
    """Rematerialize one scalar constant at each of its uses (T029's
    convergence repair): every use is rewritten to a fresh ``sconst``
    materialized immediately before it -- the classic remat alternative
    to spill/split.  No stack slot, no store: the constant is pure, so
    the whole long live range dissolves into per-use one-op ranges.  The
    original definition stays (dead, one op long; the vsetvli-AVL
    constant tracking reads it unchanged).  Returns the fresh rids (the
    remat products -- never victims again)."""
    fresh = [0]
    products: Set[int] = set()
    for b in fn.blocks:
        new_ops: List[mir.MOp] = []
        for i, op in enumerate(b.ops):
            is_term = op is b.ops[-1]
            uses_it = any(o.rid == reg.rid for o in op.operands)
            if is_term:
                uses_it = uses_it or any(
                    a.rid == reg.rid
                    for args in b.branch_args().values() for a in args)
            if uses_it:
                fresh[0] += 1
                cv = mir.VReg(reg.type, name=f"{reg.name}.c{fresh[0]}",
                              loc=reg.loc)
                products.add(cv.rid)
                new_ops.append(mir.MOp("sconst", [], [cv],
                                       attrs={"value": value}, loc=op.loc))
                op.operands = tuple(cv if o.rid == reg.rid else o
                                    for o in op.operands)
                if is_term:
                    op.attrs = dict(op.attrs)
                    for key in ("args", "true_args", "false_args"):
                        if key in op.attrs:
                            op.attrs[key] = [
                                cv if a.rid == reg.rid else a
                                for a in op.attrs[key]]
            new_ops.append(op)
        b.ops = new_ops
    return products


def _pick_victim(fn: mir.MFunction, fixed: Dict[int, str],
                 exclude: Set[int],
                 failed: Optional[mir.VReg] = None,
                 graph: Optional[Dict[int, set]] = None,
                 consts: Optional[Dict[int, int]] = None,
                 rematted: Optional[Set[int]] = None
                 ) -> Optional[mir.VReg]:
    """The fallback spill/remat candidate.

    When the failing value is known, prefer one of its interference
    neighbours: a neighbour's range covers the failure point by
    definition, so rematerializing or spilling it relieves the actual
    pressure (the globally least-used value may live nowhere near the
    failure and split uselessly).  Among the neighbours, a
    rematerializable constant comes first (the whole range dissolves
    with no stack traffic), then the least-used spillable one.  Masks,
    reload values and non-m1/m2/m4/m8 vectors are not spillable in this
    slice.
    """
    use_counts: Dict[int, int] = {}
    regs: Dict[int, mir.VReg] = {}
    reload_defs: Set[int] = set()
    for b in fn.blocks:
        for p in b.params:
            regs[p.rid] = p
        for op in b.ops:
            if op.opcode in ("sreload", "vreload"):
                reload_defs.update(r.rid for r in op.results)
            for o in op.operands:
                use_counts[o.rid] = use_counts.get(o.rid, 0) + 1
            for r in op.results:
                regs[r.rid] = r

    def rematable(reg: mir.VReg) -> bool:
        # ``exclude`` carries the consumed set (split, rematted AND the
        # remat products): re-rematerializing a product is a no-op that
        # relieves nothing
        return consts is not None and reg.rid in consts \
            and reg.rid not in exclude \
            and (rematted is None or reg.rid not in rematted) \
            and reg.rid not in reload_defs

    def spillable(reg: mir.VReg) -> bool:
        if reg.rid in fixed or reg.rid in exclude or reg.is_mask():
            return False
        if reg.rid in reload_defs:
            return False                  # already a short-range reload
        if reg.is_vector() and reg.type.lmul not in (1, 2, 4, 8):
            return False
        return True

    if failed is not None and graph is not None:
        neighbours = [regs[n] for n in graph.get(failed.rid, ())
                      if n in regs and (spillable(regs[n])
                                        or rematable(regs[n]))]
        for reg in sorted((r for r in neighbours if rematable(r)),
                          key=lambda r: (use_counts.get(r.rid, 0), r.rid)):
            return reg
        for reg in sorted((r for r in neighbours if spillable(r)),
                          key=lambda r: (use_counts.get(r.rid, 0), r.rid)):
            return reg
    for reg in sorted(regs.values(), key=lambda r: (use_counts.get(r.rid, 0),
                                                    r.rid)):
        if rematable(reg):
            return reg
        if spillable(reg):
            return reg
    return None


def _allocate_function(module: mir.MModule, fn: mir.MFunction,
                       target: TargetModel, alloc: Allocation) -> None:
    fixed: Dict[int, str] = {}
    for b in fn.blocks:
        for op in b.ops:
            for r in op.results:
                if r.fixed_phys == "v0":
                    fixed[r.rid] = "v0"
    graph, _ = _interference(fn)
    fixed_ids = list(fixed)
    for i, a in enumerate(fixed_ids):
        for c in fixed_ids[i + 1:]:
            if c in graph.get(a, ()):
                raise AllocationError(
                    None, "two fixed v0 working masks are simultaneously "
                    "live; the lowering must serialize their uses")

    rounds = 0
    split_once: Set[int] = set()
    rematted: Set[int] = set()
    #: remat products (the fresh per-use sconsts): re-rematerializing one
    #: is a no-op that adds ops without relieving any pressure, so they
    #: are never victims again (T029's convergence repair)
    remat_products: Set[int] = set()
    while True:
        assignment, failed = _try_color(fn, target, fixed)
        if assignment is not None:
            alloc.assignment.update(assignment)
            for v in _all_values(fn):
                span = v.type.lmul if v.is_vector() else 1
                alloc.shapes[v.rid] = ("mask" if v.is_mask() else
                                       "vec" if v.is_vector() else "gpr", span)
            return
        rounds += 1
        if rounds > 64:
            # the located refusal names the pressure source (T029): the
            # failing value, its position, and the simultaneous liveness
            # that exceeds the file at that point
            live_at = _failure_live_set(fn, failed)
            raise AllocationError(
                failed.loc,
                f"allocation did not converge for '{fn.name}' after "
                f"{rounds} spill rounds (each round rematerializes or "
                f"splits one value); the pressure source is value "
                f"'{failed.name}' ({failed.type!r}) at "
                f"{failed.loc or 'an unlocated position'} with "
                f"{len(live_at)} values simultaneously live against "
                f"{len(ALLOCATABLE_GPRS)} allocatable GPRs and "
                f"{target.vector_registers - len(target.reserved_vector_regs)}"
                f" vector registers -- a register-pressure pattern the "
                "splitter cannot resolve (a bounded, located refusal)")
        consts = _const_values(fn)
        reloads = _reload_defs(fn)
        consumed = split_once | rematted | remat_products
        # T029: a reload value's range is already minimal (its def sits
        # immediately before its use) -- splitting it again only adds
        # ops, never relieves pressure; it is never the victim.  The
        # failing value itself is the victim only on its first
        # intervention
        victim = None
        if failed is not None and failed.rid not in consumed \
                and failed.rid not in reloads:
            victim = failed
        if victim is None:
            # the failed value may be a fresh reload or remat product
            # absent from the round-start graph (a stale graph leaves it
            # neighbourless and the global fallback split uselessly --
            # the measured non-convergence): recompute the interference
            # so the neighbour preference targets the CURRENT pressure
            graph_now, _ = _interference(fn)
            victim = _pick_victim(fn, fixed, consumed, failed, graph_now,
                                  consts=consts, rematted=rematted)
        if victim is None:
            raise AllocationError(
                None, f"register pressure in '{fn.name}' exceeds the "
                "allocatable files and no spillable value remains (mask "
                "spill is not implemented; a bounded refusal)")
        if victim.rid in consts and victim.rid not in rematted:
            # rematerialization: no slot, no store -- every use gets a
            # fresh sconst immediately before it
            products = _remat_constant(fn, victim, consts[victim.rid])
            rematted.add(victim.rid)
            remat_products.update(products)
            continue
        if victim.is_mask():
            raise AllocationError(
                victim.loc,
                f"mask value '{victim.name}' cannot be spilled: the mask "
                "file is exhausted and mask spill is not implemented (a "
                "bounded, located refusal -- see ABSENT_FORMS)")
        if victim.is_vector():
            full_vl = _const_full_regions(fn, target)
            if (victim.type.sew, victim.type.lmul) not in full_vl:
                raise AllocationError(
                    victim.loc,
                    f"vector value '{victim.name}' must spill outside a "
                    "full-vl region; vector spill in partial-vl regions is "
                    "not implemented (located refusal)")
        slot = len(alloc.slots)
        alloc.slots.append(target.vlenb * victim.type.lmul
                           if victim.is_vector() else 8)
        split_once.add(victim.rid)
        if not _split_value(fn, victim, slot):
            raise AllocationError(
                victim.loc,
                f"value '{victim.name}' cannot be spilled (a bounded "
                "refusal, not a silent misallocation)")
        alloc.spilled[victim.rid] = slot


def _check_group_overlap(fn: mir.MFunction, alloc: "Allocation") -> None:
    """Post-allocation invariant: in a mixed-LMUL vector op the destination
    group must not overlap any source group (a hardware illegal-instruction
    form the allocator prevents by construction and asserts here)."""
    def indices(reg: mir.VReg) -> Set[int]:
        name = alloc.assignment.get(reg.rid)
        if name is None or not name.startswith("v"):
            return set()
        base = int(name[1:])
        span = alloc.shapes.get(reg.rid, ("vec", 1))[1]
        return set(range(base, base + span))

    for b in fn.blocks:
        for op in b.ops:
            for r in op.results:
                if not r.is_vector():
                    continue
                dst = indices(r)
                for o in op.operands:
                    if not o.is_vector():
                        continue
                    if o.type.lmul == r.type.lmul and \
                            op.opcode not in ("vfncvt", "vfwcvt", "vmovv",
                                              "vfmacc"):
                        continue
                    if op.opcode == "vfmacc" and o is op.operands[2]:
                        continue      # z legitimately pre-copied into vd
                    overlap = dst & indices(o)
                    if overlap:
                        raise AllocationError(
                            op.loc,
                            f"allocation gives '{r.name}' ({alloc.assignment.get(r.rid)}) "
                            f"a destination group overlapping source "
                            f"'{o.name}' ({alloc.assignment.get(o.rid)}) in "
                            f"'{op.opcode}' -- an overlap the "
                            "hardware rejects (illegal instruction)")


def allocate(module: mir.MModule, target: TargetModel) -> Allocation:
    """Allocate every function in the module; returns the Allocation."""
    alloc = Allocation()
    for fn in module.functions:
        _allocate_function(module, fn, target, alloc)
        _check_group_overlap(fn, alloc)
    vec_indices: Set[int] = set()
    for rid, name in alloc.assignment.items():
        if name.startswith("v"):
            base = int(name[1:])
            span = alloc.shapes.get(rid, ("vec", 1))[1]
            vec_indices.update(range(base, base + span))
    gpr_names = {n for n in alloc.assignment.values() if not n.startswith("v")}
    stats = {
        "gprs_used": len(gpr_names),
        "vector_regs_used": len(vec_indices),
        "vector_bytes_used": len(vec_indices) * target.vlenb,
        "vector_file_bytes": target.vector_file_bytes,
        "spill_slots": len(alloc.slots),
        "spilled_values": len(alloc.spilled),
        "frame_bytes": alloc.frame_bytes(),
        "spill_rounds_bound": 64,
    }
    alloc.stats = stats
    module.meta["allocation"] = stats
    return alloc
