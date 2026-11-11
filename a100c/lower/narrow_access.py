"""Runtime-proved contiguous segments for otherwise scalar narrow accesses.

The proof consumes actual i64 byte offsets, checks every active lane, and
never touches source/destination memory. A mismatch executes the original
scalar lowering. No source-operator identity or speculative address bound
is involved; statically proven unit/strided forms are selected earlier.
"""
from __future__ import annotations

from a100c.ir import mir, tir
from a100c.lower import addresses


class _Guard:
    segment = 16

    def __init__(self, lowering, ctx, loc):
        self.lowering, self.ctx, self.loc = lowering, ctx, loc

    def emit(self, code, operands, result_type, attrs=None, hint="ng"):
        return self.ctx.emit(mir.MOp(
            code, operands, [self.ctx.vreg(result_type, hint=hint, loc=self.loc)],
            attrs=attrs or {}, loc=self.loc))

    def region(self, ty, length=None):
        self.lowering._vregion(self.ctx, ty, self.loc,
                              self.segment if length is None else length)

    def splat(self, scalar, ty, length=None):
        self.region(ty, length)
        return self.emit("s2v", [scalar], ty)

    def slice(self, value, start):
        ty = value.type
        self.region(ty)
        if start == 0:
            return value
        index_type = mir.VectorType(ty.sew, ty.lmul, "int")
        ids = self.emit("vid", [], index_type)
        ids = self.emit("vbinx", [ids, self.ctx.const(
            start, mir.ScalarType(ty.sew), self.loc)], index_type, {"op": "add"})
        return self.emit("vrgather", [value, ids], ty)

    def active(self, mask01, start):
        if mask01 is None:
            return None
        value = self.slice(mask01, start)
        zero = self.splat(self.ctx.const(0, mir.I32, self.loc), value.type)
        return self.emit("vcmp", [value, zero], mir.MaskType(),
                         {"pred": "ne", "fp": False})

    def working_mask(self, active):
        return self.ctx.emit(mir.MOp(
            "vmovmask", [active], [self.ctx.vreg(
                mir.MaskType(), hint="ng0", loc=self.loc, fixed_phys="v0")],
            loc=self.loc))

    def plan(self, base, offsets, pointee, ty, mask):
        lowering, ctx, loc = self.lowering, self.ctx, self.loc
        mask01 = lowering._narrow_mask01(ctx, mask, ty, loc) \
            if mask is not None else None
        scaled, tree = addresses.materialize_address(
            ctx, base, offsets, pointee, loc, lowering._vl, (lowering._sew, 1))
        lowering.trees.append(tree)
        bad_sum = ctx.const(0, mir.I64, loc)
        segments = []
        for start in range(0, lowering._vl, self.segment):
            part = self.slice(scaled, start)
            self.region(part.type)
            first = self.emit("vextract", [part], mir.I64)
            ids = self.emit("vid", [], part.type)
            delta = self.emit("vbinx", [ids, ctx.const(
                ty.sew // 8, mir.I64, loc)], part.type, {"op": "mul"})
            expected = self.emit("vbinx", [delta, first], part.type, {"op": "add"})
            bad = self.emit("vcmp", [part, expected], mir.MaskType(),
                            {"pred": "ne", "fp": False})
            active = self.active(mask01, start)
            if active is not None:
                bad = self.emit("vmand", [bad, active], mir.MaskType())
            count = self.emit("vpopc", [bad], mir.I64)
            bad_sum = self.emit("sadd", [bad_sum, count], mir.I64)
            segments.append((start, self.emit("sadd", [base, first], mir.I64)))
        return mask01, bad_sum, segments


def _eligible(lowering, ty):
    # Bound guard pressure. Wider chunks have a separate pressure/cost
    # decision; the existing scalar fallback supports them unchanged.
    return (lowering.options.guarded_narrow_access
            and ty.sew in (8, 16) and ty.lmul == 1
            and lowering._vl in (16, 32))


def try_load(lowering, ctx, op, base, offsets, pointee, mask, other,
             default, loc, result_type, fallback):
    ty = lowering._vtype(result_type)
    if op.attrs.get("volatile") or not _eligible(lowering, ty):
        return None
    # Do not reinterpret unsigned/floating vector defaults solely because
    # their SEW matches: preserve the existing scalar low-bit behavior by
    # declining when a typed vector select cannot express that same type.
    oval = lowering._need(other, loc) \
        if other is not None or default == tir.MaskedDefault.VALUE else None
    if oval is not None and oval.is_vector() and oval.type != ty:
        return None
    guard = _Guard(lowering, ctx, loc)
    if oval is None:
        oval = guard.splat(ctx.const(0, mir.I32, loc), ty, lowering._vl)
    elif not oval.is_vector():
        oval = guard.splat(oval, ty, lowering._vl)
    mask01, bad_sum, segments = guard.plan(base, offsets, pointee, ty, mask)
    tname, ename, jname = lowering._guard_block_names("ngl")
    fast = ctx.add_block(tname, [], loc)
    slow = ctx.add_block(ename, [], loc)
    result = ctx.vreg(ty, hint="ng_join", loc=loc)
    join = ctx.add_block(jname, [result], loc)
    saved = dict(lowering.values)
    ctx.emit0(mir.MOp("brc", [bad_sum], [], attrs={
        "true_target": ename, "true_args": [],
        "false_target": tname, "false_args": []}, loc=loc))
    ctx.switch(fast)
    workspace = lowering._workspace_private_reg(ctx, loc)
    scratch = guard.emit("sadd", [workspace, ctx.const(
        lowering._narrow_ws_offset, mir.I64, loc)], mir.I64)
    for start, address in segments:
        active = guard.active(mask01, start)
        guard.region(ty)
        operands = [address]
        if active is not None:
            operands.append(guard.working_mask(active))
        value = guard.emit("vunit_load", operands, ty,
                           {"sew": ty.sew, "default": "undef"})
        if active is not None:
            default_part = guard.slice(oval, start)
            guard.region(ty)
            value = guard.emit("vsel", [guard.working_mask(active), value,
                                       default_part], ty)
        target = guard.emit("sadd", [scratch, ctx.const(
            start * ty.sew // 8, mir.I64, loc)], mir.I64)
        guard.region(ty)
        ctx.emit0(mir.MOp("vunit_store", [target, value], [],
                          attrs={"sew": ty.sew}, loc=loc))
    guard.region(ty, lowering._vl)
    value = guard.emit("vunit_load", [scratch], ty, {"sew": ty.sew})
    ctx.emit0(mir.MOp("br", [], [], attrs={"target": jname, "args": [value]}, loc=loc))
    lowering.values = dict(saved)
    ctx.switch(slow)
    value = fallback()
    ctx.emit0(mir.MOp("br", [], [], attrs={"target": jname, "args": [value]}, loc=loc))
    lowering.values = dict(saved)
    ctx.switch(join)
    lowering._vregion(ctx, ty, loc, lowering._vl)
    return result


def try_store(lowering, ctx, base, offsets, pointee, value, mask, loc,
              fallback, volatile=False):
    ty = value.type
    if not value.is_vector() or volatile or not _eligible(lowering, ty):
        return False
    guard = _Guard(lowering, ctx, loc)
    mask01, bad_sum, segments = guard.plan(base, offsets, pointee, ty, mask)
    tname, ename, jname = lowering._guard_block_names("ngs")
    fast = ctx.add_block(tname, [], loc)
    slow = ctx.add_block(ename, [], loc)
    join = ctx.add_block(jname, [], loc)
    saved = dict(lowering.values)
    ctx.emit0(mir.MOp("brc", [bad_sum], [], attrs={
        "true_target": ename, "true_args": [],
        "false_target": tname, "false_args": []}, loc=loc))
    ctx.switch(fast)
    for start, address in segments:
        part = guard.slice(value, start)
        active = guard.active(mask01, start)
        guard.region(ty)
        operands = [address, part]
        attrs = {"sew": ty.sew}
        if active is not None:
            operands.append(guard.working_mask(active))
            attrs["default"] = "no-access"
        ctx.emit0(mir.MOp("vunit_store", operands, [], attrs=attrs, loc=loc))
    ctx.emit0(mir.MOp("br", [], [], attrs={"target": jname, "args": []}, loc=loc))
    lowering.values = dict(saved)
    ctx.switch(slow)
    fallback()
    ctx.emit0(mir.MOp("br", [], [], attrs={"target": jname, "args": []}, loc=loc))
    lowering.values = dict(saved)
    ctx.switch(join)
    lowering._vregion(ctx, ty, loc, lowering._vl)
    return True
