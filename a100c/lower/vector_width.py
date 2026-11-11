"""Choose a bounded SIMD width for simple lane-independent lowered loops.

This is an internal lowering choice over the existing MIR, before its
normal verifier/selection/allocation consumers.  It creates no persistent
IR or optimization stage.  The original module is retained unless a
structurally legal candidate passes the register-pressure budget.
"""
from __future__ import annotations

import copy

from a100c.ir import mir, tir
from a100c.backend.allocate import register_pressure
from a100c.passes import mir_optimize


_PURE = frozenset(mir.SBIN_OPS) | frozenset((
    "sconst", "smove", "swext", "strunc", "vid", "s2v", "vbin",
    "vbinx", "vunary", "vcmp", "vcmpx", "vsel", "vwaddx0", "vwiden",
    "vfwcvt", "vfncvt", "vmovv", "vfmacc", "vmand", "vmor", "vmnot", "vmxor",
))
_VECTOR = _PURE | frozenset(("vsetvli", "vmovmask", "vunit_load", "vunit_store",
                             "vloadix", "vuload32", "vustore32"))

# Native ABI v1: a100c/runtime/a100rt.h has matching offsetof/sizeof
# static_asserts for a100rt_view.storage and the complete view record.
_VIEW_RECORD_BYTES = 56
_VIEW_STORAGE_OFFSET = 48


def _alias_pairs(tir_module, layout):
    """Bind actual memory roots, never pointer-table container storage."""
    if tir_module is None or layout is None or len(tir_module.functions) != 1:
        return None
    fn = tir_module.functions[0]
    parameters = {p.vid: layout.view_of(p.name) for p in fn.params if p.type.is_pointer()}

    def root(value):
        if value.vid in parameters:
            binding = parameters[value.vid]
            return binding.view_index if binding is not None else None
        prod = value.producer
        if prod is not None and prod.op in ("ptradd", "broadcast", "realize", "hint"):
            return root(prod.operands[0])
        return None

    reads, writes = [], []
    for op in fn.body.statements:
        if not isinstance(op, tir.Op):
            return None
        if op.op in ("load", "store"):
            index = root(op.operands[0])
            if index is None or op.attrs.get("volatile"):
                return None
            (reads if op.op == "load" else writes).append(index)
    if not writes:
        return None
    pairs = {(read, write) for read in reads for write in writes}
    pairs.update((first, second) for i, first in enumerate(writes) for second in writes[i+1:])
    # A statically identical read/write root never has a profitable wider
    # path under this conservative guard.  Unknown runtime aliases are
    # checked in native code instead of entering compilation identity.
    if any(a == b for a, b in pairs):
        return None
    return sorted(pairs)


def _runtime_width(module, views_rid, pairs, factor):
    """Select old or new chunk geometry using native backing-storage IDs."""
    fn = module.functions[0]
    regs = {r.rid: r for block in fn.blocks for r in block.params}
    regs.update({r.rid: r for block in fn.blocks for op in block.ops for r in (*op.operands, *op.results)})
    views = regs[views_rid]
    prelude = []

    def emit(code, operands, ty=mir.I64, attrs=None):
        reg = mir.VReg(ty, name="width.guard")
        prelude.append(mir.MOp(code, operands, [reg], attrs=attrs or {}))
        return reg

    def constant(n, ty=mir.I64):
        return emit("sconst", [], ty, {"value": n})

    storage = {}
    disjoint = constant(1)
    for a, b in pairs:
        for index in (a, b):
            if index not in storage:
                storage[index] = emit("sload", [views], attrs={"width": 64,
                    "offset": index*_VIEW_RECORD_BYTES + _VIEW_STORAGE_OFFSET, "ext": "sext"})
        different = emit("sor", [emit("sltu", [storage[a], storage[b]]),
                                   emit("sltu", [storage[b], storage[a]])])
        disjoint = emit("sand", [disjoint, different])
    wide_delta = emit("smul", [disjoint, constant(32*factor - 32)])
    width64 = emit("sadd", [constant(32), wide_delta])
    width32 = emit("strunc", [width64], mir.I32)
    # The launch's views pointer was defined in entry.  Native guard
    # loads occur once per worker entry, before every program/chunk loop.
    entry = fn.blocks[0]
    entry.ops[-1:-1] = prelude
    return width32, width64


def _dead_temporaries(fn):
    """Remove unused pure lowering temporaries, preserving all effects.

    Unknown operations, state changes, memory accesses and fixed-register
    copies remain roots.  This runs only on an eligible private candidate,
    and the untouched input module is returned if no width is selected.
    """
    definitions = {r.rid: op for b in fn.blocks for op in b.ops for r in op.results}
    needed, pending = set(), []
    for block in fn.blocks:
        for op in block.ops:
            if op.opcode not in _PURE or not op.results or any(r.fixed_phys for r in op.results):
                needed.add(id(op))
                pending.extend(op.operands)
                for key in ("args", "true_args", "false_args"):
                    pending.extend(op.attrs.get(key, ()))
    while pending:
        reg = pending.pop()
        producer = definitions.get(reg.rid)
        if producer is None or id(producer) in needed:
            continue
        needed.add(id(producer))
        pending.extend(producer.operands)
    count = 0
    for block in fn.blocks:
        kept = [op for op in block.ops if id(op) in needed]
        count += len(block.ops) - len(kept)
        block.ops = kept
    return count


def _loops(module, factor):
    """Return matched chunk back-edge updates, or a conservative reason."""
    if len(module.functions) != 1 or module.meta.get("matrix_segments"):
        return None, "requires one non-matrix function"
    fn = module.functions[0]
    ops = [op for block in fn.blocks for op in block.ops]
    for op in ops:
        if op.opcode in mir.VEC_OPS and op.opcode not in _VECTOR:
            return None, "cross-lane or unsupported vector operation"
        if op.opcode in ("satomic", "slr", "ssc", "sfence", "callbarrier", "vmath"):
            return None, "ordered operation or scalar math service"
        if op.opcode in ("sload", "sstore") and op.attrs.get("width", 64) < 32:
            return None, "narrow scalar memory fallback"
        if op.opcode in ("vloadix", "vstoreix") and op.attrs.get("sew", 0) < 32:
            return None, "narrow indexed memory"
        if op.opcode == "vmovv" and op.operands[0].type.sew != op.results[0].type.sew:
            return None, "packed register reinterpretation"
    constants = {r.rid: op.attrs["value"] for op in ops if op.opcode == "sconst" for r in op.results}
    definitions = {r.rid: op for op in ops for r in op.results}
    regions = [op for op in ops if op.opcode == "vsetvli"]
    if not regions or any(constants.get(op.operands[0].rid) != 32 for op in regions):
        return None, "requires fixed 32-lane vector regions"

    def upper_bound(reg):
        if reg.rid in constants:
            return constants[reg.rid]
        add = definitions.get(reg.rid)
        if add is None or add.opcode != "sadd":
            return None
        # P1's exact signed min(live, BLOCK) idiom; BLOCK is static,
        # live remains runtime symbolic, never specialized from the case.
        for bound, select in (add.operands, tuple(reversed(add.operands))):
            extent = constants.get(bound.rid)
            band = definitions.get(select.rid)
            if extent is None or band is None or band.opcode != "sand":
                continue
            for delta, neg in (band.operands, tuple(reversed(band.operands))):
                diff, minus = definitions.get(delta.rid), definitions.get(neg.rid)
                if diff is None or diff.opcode != "ssub" or \
                        constants.get(diff.operands[1].rid) != extent or \
                        minus is None or minus.opcode != "ssub" or \
                        constants.get(minus.operands[0].rid) != 0:
                    continue
                pred = definitions.get(minus.operands[1].rid)
                if pred is not None and pred.opcode in ("strunc", "swext"):
                    pred = definitions.get(pred.operands[0].rid)
                if pred is not None and pred.opcode == "slt" and \
                        pred.operands[0] is diff.operands[0] and \
                        constants.get(pred.operands[1].rid) == extent:
                    return extent
        return None

    preds, succs = mir_optimize._build_graph(fn)
    dom = mir_optimize._dominators(fn, preds, succs)
    loops = mir_optimize._natural_loops(fn, preds, dom)
    blocks = {b.name: b for b in fn.blocks}
    chunks = [(head, body) for head, body in loops if len(body) == 2 and
              any(op.opcode in mir.VEC_OPS for name in body for op in blocks[name].ops)]
    if not chunks or len(loops) != len(chunks) + 1:
        return None, "requires simple vector loops inside one program loop"
    updates = []
    for head_name, body_names in chunks:
        head = blocks[head_name]
        body = next(blocks[name] for name in body_names if name != head_name)
        term = body.ops[-1]
        if term.opcode != "br" or term.attrs.get("target") != head_name:
            return None, "unexpected vector-loop back edge"
        if len(head.params) != 2 or any(op.opcode in ("sload", "sstore") for op in body.ops):
            return None, "chunk has scalar state or memory effects"
        found = None
        for slot, param in enumerate(head.params):
            if not param.is_scalar() or param.type.width != 32:
                continue
            tests = []
            for op in head.ops:
                if op.opcode != "slt":
                    continue
                lhs = op.operands[0]
                producer = definitions.get(lhs.rid)
                if producer is not None and producer.opcode == "smove" and \
                        producer.operands[0].type.width == 32:
                    lhs = producer.operands[0]
                if lhs is param and upper_bound(op.operands[1]) is not None:
                    tests.append(op)
            if len(tests) != 1:
                continue
            extent = upper_bound(tests[0].operands[1])
            if extent <= 0 or extent % (32 * factor):
                continue
            argument = term.attrs["args"][slot]
            advance = [op for op in body.ops if op.opcode == "sadd" and
                       argument in op.results and param in op.operands]
            if len(advance) != 1:
                continue
            step = next((reg for reg in advance[0].operands if reg is not param), None)
            if step is not None and constants.get(step.rid) == 32:
                found = (advance[0], step, extent)
                break
        if found is None:
            return None, "no exact divisible 32-lane chunk induction"
        updates.append(found)
        # Unmasked stores count chunk work with an explicit VL constant.
        # Masked stores use vpopc, whose active VL follows the same guard.
        item_arg = term.attrs["args"][1]
        item_update = definitions.get(item_arg.rid)
        if item_arg is head.params[1]:
            continue
        if item_update is None or item_update.opcode != "sadd" or \
                head.params[1] not in item_update.operands:
            return None, "unknown chunk item counter"
        amount = next(r for r in item_update.operands if r is not head.params[1])
        counter = definitions.get(amount.rid)
        if constants.get(amount.rid) == 32:
            updates.append((item_update, amount, extent))
        elif counter is None or counter.opcode != "vpopc":
            return None, "unknown chunk work increment"
    return (updates, constants), None


def _widen(module, factor, match, views_rid, pairs):
    updates, constants = match
    fn = module.functions[0]
    regs = {r.rid: r for block in fn.blocks for r in block.params}
    regs.update({r.rid: r for block in fn.blocks for op in block.ops for r in (*op.operands, *op.results)})
    if any(r.is_vector() and r.type.lmul * factor > 8 for r in regs.values()):
        return False
    width32, width64 = _runtime_width(module, views_rid, pairs, factor)
    advance = {id(op): step for op, step, _ in updates}
    for block in fn.blocks:
        changed = []
        for op in block.ops:
            if id(op) in advance:
                old = advance[id(op)]
                step = width32 if old.type.width == 32 else width64
                op.operands = tuple(step if r is old else r for r in op.operands)
            if op.opcode == "vsetvli":
                op.attrs["lmul"] *= factor
                op.operands = (width32,)
            changed.append(op)
        block.ops = changed
    for reg in regs.values():
        if reg.is_vector():
            ty = reg.type
            reg.type = mir.VectorType(ty.sew, ty.lmul*factor, ty.kind)
    return True


def choose(module, enabled=True, tir_module=None, layout=None, views_reg=None):
    report = {"enabled": enabled, "factor": 1, "attempts": [], "vector_budget": 28}
    module.meta["elementwise_width"] = report
    if not enabled:
        return module
    pairs = _alias_pairs(tir_module, layout)
    if pairs is None or views_reg is None:
        report["reason"] = "memory roots or alias safety not established"
        return module
    report["runtime_storage_pairs"] = [list(pair) for pair in pairs]
    # Check applicability before copying or computing CFG pressure.
    match, reason = _loops(module, 2)
    if match is None:
        report["reason"] = reason
        return module
    baseline = register_pressure(module.functions[0])
    for factor in (4, 2):
        candidate = copy.deepcopy(module)
        match, reason = _loops(candidate, factor)
        if match is None or not _widen(candidate, factor, match, views_reg.rid, pairs):
            report["attempts"].append({"factor": factor, "status": "not-applicable", "reason": reason})
            continue
        dead = _dead_temporaries(candidate.functions[0])
        errors = mir.verify_module(candidate)
        demand = register_pressure(candidate.functions[0])
        accepted = not errors and demand["vector_registers"] <= 28 and demand["gpr"] <= max(25, baseline["gpr"])
        report["attempts"].append({"factor": factor, "status": "selected" if accepted else "declined",
                                   "pressure": demand, "removed_temporaries": dead,
                                   "errors": [str(e) for e in errors[:2]]})
        if accepted:
            report["factor"] = factor
            candidate.meta["elementwise_width"] = report
            return candidate
    return module
