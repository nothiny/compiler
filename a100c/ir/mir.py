"""MIR (mir/v1): virtual-register dataflow over target-shaped operations.

Carries, with a named owner for every check (IR-SEMANTIC-FIDELITY,
COMPILER_ARCHITECTURE.md 2.2):

======================  ============================================  ==========================
source property         carrier in MIR                                who checks
======================  ============================================  ==========================
element width (vector)  ``VectorType.sew`` on every value             MIR verifier; selection
register group size     ``VectorType.lmul``                           MIR verifier; allocation
mask + inactive-        ``mask`` operand plus declared ``default``    MIR verifier (a masked
position semantics      (undef/value on loads; no-access on stores)   op without it is malformed)
vsetvli regions         explicit ``vsetvli`` ops; every vector op      MIR verifier (region
                        executes inside a matching region            consistency invariant)
working-mask constraint ops that read a mask from hardware v0 take      MIR verifier; allocation
                        a vreg fixed to v0 (``vmovmask`` produces it) (fixed pre-coloring)
signedness              ``ScalarType.signed`` / VectorType kind       verifier; selection
addresses               ``vloadix``/``vstoreix`` index at EEW=64,     verifier (EEW/width match)
                        whole tree materialized in i64 (vwiden +
                        vmul + indexed base)
worker partition        explicit CFG: program loop with block params  verifier (block structure);
structure               (joins), strided worker stepping, barrier     plan produces it
======================  ============================================  ==========================

The verifier rejects one hand-built malformed module per invariant class
(vsetvli-region inconsistency, masked store without inactive semantics,
use-before-definition, plus the structural classes below) and accepts the
lowering's real output (IR-WELLFORMED).
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

__all__ = [
    "ScalarType", "VectorType", "MaskType", "VReg", "MOp", "Block",
    "MFunction", "MModule", "MirError", "Invariant", "verify_module",
    "verify", "dump_module", "I32", "I64", "U32", "U64",
    "VEC_OPS", "MEM_OPS", "MASK_READING_OPS",
]


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


class ScalarType:
    """A scalar machine type living in a GPR.

    i32 values are held sign-extended in 64-bit registers (the RV64 *w ops
    sign-extend); u32 values are held zero-extended and may only be compared
    unsigned or used where the value is known small.
    """

    __slots__ = ("width", "signed", "float")

    def __init__(self, width: int, signed: bool = True, float: bool = False):
        assert width in (1, 8, 16, 32, 64)
        self.width = width
        self.signed = signed
        self.float = float

    @property
    def bits(self) -> int:
        return self.width

    def __eq__(self, other):
        return (isinstance(other, ScalarType) and other.width == self.width
                and other.signed == self.signed and other.float == self.float)

    def __hash__(self):
        return hash(("s", self.width, self.signed, self.float))

    def __repr__(self):
        if self.float:
            return f"f{self.width}"
        return ("i" if self.signed else "u") + str(self.width)


I32 = ScalarType(32)
I64 = ScalarType(64)
U32 = ScalarType(32, signed=False)
U64 = ScalarType(64, signed=False)


class VectorType:
    """A vector value: SEW element width, LMUL register-group size, kind."""

    __slots__ = ("sew", "lmul", "kind")

    def __init__(self, sew: int, lmul: int = 1, kind: str = "int"):
        assert kind in ("int", "uint", "float")
        self.sew = sew
        self.lmul = lmul
        self.kind = kind

    @property
    def group_regs(self) -> int:
        return self.lmul

    def __eq__(self, other):
        return (isinstance(other, VectorType) and other.sew == self.sew
                and other.lmul == self.lmul and other.kind == self.kind)

    def __hash__(self):
        return hash(("v", self.sew, self.lmul, self.kind))

    def __repr__(self):
        kind = {"int": "i", "uint": "u", "float": "f"}[self.kind]
        return f"v{kind}{self.sew}m{self.lmul}"


class MaskType:
    """A mask value: one bit per lane, one vector register."""

    __slots__ = ()

    def __eq__(self, other):
        return isinstance(other, MaskType)

    def __hash__(self):
        return hash("mask")

    def __repr__(self):
        return "vm"


# ---------------------------------------------------------------------------
# Values
# ---------------------------------------------------------------------------

_NEXT_REG = [0]


class VReg:
    """A virtual register: type, name, optional fixed physical assignment.

    ``fixed_phys == 'v0'`` pins the value to vector register v0 (the working
    mask); the allocator pre-colors it and never assigns v0 itself.
    """

    __slots__ = ("rid", "name", "type", "fixed_phys", "loc", "hint")

    def __init__(self, mtype, name: Optional[str] = None,
                 fixed_phys: Optional[str] = None, loc=None, hint: str = ""):
        _NEXT_REG[0] += 1
        self.rid = _NEXT_REG[0]
        self.name = name or f"r{self.rid}"
        self.type = mtype
        self.fixed_phys = fixed_phys
        self.loc = loc
        self.hint = hint

    def is_scalar(self) -> bool:
        return isinstance(self.type, ScalarType)

    def is_vector(self) -> bool:
        return isinstance(self.type, VectorType)

    def is_mask(self) -> bool:
        return isinstance(self.type, MaskType)

    def __repr__(self):
        fixed = f"@{self.fixed_phys}" if self.fixed_phys else ""
        return f"{self.name}:{self.type!r}{fixed}"


# ---------------------------------------------------------------------------
# Ops
# ---------------------------------------------------------------------------

#: semantic op codes the *legaliser* rewrites (they have no direct repertoire
#: entry: no target instruction widens or narrows by itself)
LEGALIZE_ONLY_OPS = {"vwiden", "strunc"}

#: vector ops that execute inside a vsetvli region
VEC_OPS = {
    "vid", "s2v", "vbin", "vbinx", "vunary", "vcmp", "vcmpx", "vsel",
    "vwaddx0", "vwiden", "vloadix", "vstoreix",
}

#: memory ops with masks and declared inactive semantics
MEM_OPS = {"vloadix", "vstoreix"}

#: ops whose mask operand is read from hardware v0
MASK_READING_OPS = {"vsel", "vloadix", "vstoreix"}

#: scalar binary op codes (type from operands; i32 selects the *w forms)
SBIN_OPS = {"sadd", "ssub", "smul", "sdiv", "sdivu", "sand", "sor", "sxor",
            "sshl", "ssra", "slt", "sltu"}

#: vector binary op codes
VBIN_OPS = {"add", "sub", "mul", "and", "or", "xor", "fadd", "fsub", "fmul"}

#: vector x scalar op codes
VBINX_OPS = {"add", "mul"}

#: vector unary op codes
VUNARY_OPS = {"fneg", "not"}

#: comparison predicates (vector and scalar)
CMP_PREDS = {"lt", "le", "gt", "ge", "eq", "ne"}


class MOp:
    """One MIR operation: opcode, operands, results, attributes, location.

    ``loc`` carries the source position of the TIR op (or plan decision) that
    produced it -- source attribution survives to the emitted assembly
    (IR-OBSERVABILITY).
    """

    __slots__ = ("opcode", "operands", "results", "attrs", "loc", "index")

    def __init__(self, opcode: str, operands: Sequence[VReg],
                 results: Sequence[VReg], attrs: Optional[dict] = None,
                 loc=None):
        self.opcode = opcode
        self.operands = tuple(operands)
        self.results = tuple(results)
        self.attrs = dict(attrs or {})
        self.loc = loc
        self.index = -1

    def __repr__(self):
        res = ", ".join(r.name for r in self.results)
        ops = ", ".join(o.name for o in self.operands)
        head = f"{res} = " if res else ""
        return f"{head}{self.opcode}({ops})"


class Block:
    """A basic block: parameters (joins), ops, one terminator.

    Terminators are ``br`` (unconditional) and ``brc`` (conditional); both
    carry per-target block arguments.  ``ret`` ends the function.
    """

    __slots__ = ("name", "params", "ops", "loc")

    def __init__(self, name: str, params: Sequence[VReg] = (), loc=None):
        self.name = name
        self.params = list(params)
        self.ops: List[MOp] = []
        self.loc = loc

    def terminator(self) -> Optional[MOp]:
        return self.ops[-1] if self.ops and self.ops[-1].opcode in (
            "br", "brc", "ret") else None

    def successors(self) -> List[str]:
        term = self.terminator()
        if term is None or term.opcode == "ret":
            return []
        if term.opcode == "br":
            return [term.attrs["target"]]
        return [term.attrs["true_target"], term.attrs["false_target"]]

    def branch_args(self) -> Dict[str, List[VReg]]:
        term = self.terminator()
        if term is None or term.opcode == "ret":
            return {}
        if term.opcode == "br":
            return {term.attrs["target"]: list(term.attrs.get("args", ()))}
        return {term.attrs["true_target"]: list(term.attrs.get("true_args", ())),
                term.attrs["false_target"]: list(term.attrs.get("false_args", ()))}


class MFunction:
    def __init__(self, name: str, params: Sequence[VReg], loc=None):
        self.name = name
        self.params = list(params)
        self.loc = loc
        self.blocks: List[Block] = []

    def block(self, name: str) -> Block:
        for b in self.blocks:
            if b.name == name:
                return b
        raise KeyError(name)

    def block_index(self, name: str) -> int:
        for i, b in enumerate(self.blocks):
            if b.name == name:
                return i
        raise KeyError(name)


class MModule:
    """One MIR module: the lowering's output for one specialization."""

    def __init__(self, name: str, source_path: str):
        self.name = name
        self.source_path = source_path
        self.functions: List[MFunction] = []
        #: allocation/selection meta filled by later stages (dumps, budget)
        self.meta: Dict[str, object] = {}

    def renumber(self) -> None:
        """Deterministic op indices for dumps and diagnostics."""
        i = 0
        for fn in self.functions:
            for b in fn.blocks:
                for op in b.ops:
                    op.index = i
                    i += 1


# ---------------------------------------------------------------------------
# Verifier
# ---------------------------------------------------------------------------


class Invariant:
    """The verifier's invariant classes (one malformed module each)."""

    USE_BEFORE_DEFINITION = "use-before-definition"
    VSETVLI_REGION_INCONSISTENCY = "vsetvli-region-inconsistency"
    MASKED_WITHOUT_INACTIVE_SEMANTICS = "masked-op-without-inactive-semantics"
    TYPE_MISMATCH = "type-mismatch"
    BLOCK_STRUCTURE = "block-structure"
    V0_MASK_CONSTRAINT = "v0-mask-constraint"
    UNKNOWN_OP = "unknown-op"


class MirError(Exception):
    """A verifier/selection rejection: invariant class, location, message."""

    def __init__(self, invariant: str, loc, message: str):
        where = ""
        if loc is not None:
            where = f" (at {loc})"
        super().__init__(f"{invariant}: {message}{where}")
        self.invariant = invariant
        self.loc = loc
        self.message = message


def _loc_text(loc) -> str:
    return str(loc) if loc is not None else "<mir>"


def _check_terminators(fn: MFunction, errors: List[MirError]) -> None:
    names = {b.name for b in fn.blocks}
    if not fn.blocks:
        errors.append(MirError(Invariant.BLOCK_STRUCTURE, fn.loc,
                               f"function '{fn.name}' has no blocks"))
        return
    for b in fn.blocks:
        if not b.ops or b.ops[-1].opcode not in ("br", "brc", "ret"):
            errors.append(MirError(
                Invariant.BLOCK_STRUCTURE, b.loc or fn.loc,
                f"block '{b.name}' must end with br/brc/ret"))
            continue
        for op in b.ops[:-1]:
            if op.opcode in ("br", "brc", "ret"):
                errors.append(MirError(
                    Invariant.BLOCK_STRUCTURE, op.loc,
                    f"terminator '{op.opcode}' inside block '{b.name}'"))
        for target, args in b.branch_args().items():
            if target not in names:
                errors.append(MirError(
                    Invariant.BLOCK_STRUCTURE, b.ops[-1].loc,
                    f"block '{b.name}' branches to unknown block '{target}'"))
                continue
            params = fn.block(target).params
            if len(params) != len(args):
                errors.append(MirError(
                    Invariant.BLOCK_STRUCTURE, b.ops[-1].loc,
                    f"branch to '{target}' from '{b.name}' passes "
                    f"{len(args)} arg(s); target takes {len(params)}"))
                continue
            for p, a in zip(params, args):
                if p.type != a.type:
                    errors.append(MirError(
                        Invariant.TYPE_MISMATCH, b.ops[-1].loc,
                        f"branch arg {a.name}:{a.type!r} does not match "
                        f"param {p.name}:{p.type!r} of '{target}'"))


def _predecessors(fn: MFunction) -> Dict[str, set]:
    preds: Dict[str, set] = {b.name: set() for b in fn.blocks}
    for b in fn.blocks:
        for succ in b.successors():
            if succ in preds:
                preds[succ].add(b.name)
    return preds


def _dominators(fn: MFunction) -> Dict[str, set]:
    """Iterative dominator sets over the block order (entry = first block)."""
    names = [b.name for b in fn.blocks]
    entry = names[0]
    preds = _predecessors(fn)
    dom = {n: set(names) for n in names}
    dom[entry] = {entry}
    changed = True
    while changed:
        changed = False
        for n in names[1:]:
            new = set(names)
            if preds[n]:
                for p in preds[n]:
                    new &= dom[p]
            else:
                new = set()
            new.add(n)
            new |= {entry} if n == entry else set()
            if not preds[n] and n != entry:
                new = {n} | {entry}
            if new != dom[n]:
                dom[n] = new
                changed = True
    return dom


def _defined_before(op: MOp, value: VReg, fn: MFunction, block: Block,
                    dom: Dict[str, set], defs: Dict[int, Tuple[str, int]]) -> bool:
    """Is ``value`` defined before ``op`` (same block earlier, or dominating
    def, or a block param of a dominating block, or a function param)?"""
    if value.rid in {p.rid for p in fn.params}:
        return True
    if value.rid in {p.rid for p in block.params}:
        return True
    where = defs.get(value.rid)
    if where is None:
        return False
    dname, dindex = where
    if dname == block.name:
        return dindex < op.index
    return dname in dom[block.name]


def _type_check(op: MOp, errors: List[MirError]) -> None:
    """Per-opcode operand/result type rules (the type-mismatch class)."""

    def err(msg: str) -> None:
        errors.append(MirError(Invariant.TYPE_MISMATCH, op.loc, msg))

    code = op.opcode
    ops = op.operands
    res = op.results

    def S(i):
        return ops[i].type if i < len(ops) and isinstance(ops[i].type, ScalarType) else None

    def V(i):
        return ops[i].type if i < len(ops) and isinstance(ops[i].type, VectorType) else None

    if code == "sconst":
        if ops or len(res) != 1 or not res[0].is_scalar():
            return err("'sconst' takes no operands and one scalar result")
        if not isinstance(op.attrs.get("value"), int):
            return err("'sconst' value must be an integer (raw bits)")
    elif code == "sload":
        if len(ops) != 1 or not S(0):
            return err("'sload' takes one scalar base")
        if len(res) != 1 or not res[0].is_scalar():
            return err("'sload' produces one scalar")
        width = op.attrs.get("width")
        if width not in (8, 16, 32, 64):
            return err(f"'sload' width {width} not in 8/16/32/64")
        if not isinstance(op.attrs.get("offset"), int):
            return err("'sload' requires an integer offset")
        ext = op.attrs.get("ext")
        if ext not in ("sext", "zext"):
            return err("'sload' requires sext/zext extension")
    elif code == "sstore":
        if len(ops) != 2 or not S(0) or not S(1):
            return err("'sstore' takes a scalar base and value")
        if res:
            return err("'sstore' produces nothing")
        if op.attrs.get("width") not in (8, 16, 32, 64):
            return err("'sstore' width must be 8/16/32/64")
    elif code == "smove":
        if len(ops) != 1 or len(res) != 1 or not ops[0].is_scalar() \
                or not res[0].is_scalar():
            return err("'smove' moves one scalar to one scalar")
        if ops[0].type.width != res[0].type.width and not (
                ops[0].type.width == 32 and res[0].type.width == 64):
            return err("'smove' preserves width (32->64 only for values "
                       "already held extended in the register)")
    elif code == "strunc":
        if len(ops) != 1 or len(res) != 1 or ops[0].type != I64 \
                or res[0].type != I32:
            return err("'strunc' narrows one i64 to i32 (pre-legalisation "
                       "semantic op; no target instruction truncates)")
    elif code == "swext":
        if len(ops) != 1 or len(res) != 1 or ops[0].type != I64 \
                or res[0].type != I32:
            return err("'swext' re-sign-extends the low 32 bits of one i64 "
                       "into an i32 value")
    elif code in SBIN_OPS:
        if len(ops) != 2 or len(res) != 1:
            return err(f"'{code}' takes two operands and one result")
        a, b, r = S(0), S(1), res[0].type
        if not (a and b and res[0].is_scalar()):
            return err(f"'{code}' requires scalar operands")
        if a != b:
            return err(f"'{code}' operand types differ: {a!r} vs {b!r}")
        expect = I64 if code in ("slt", "sltu") else a
        if r != expect:
            return err(f"'{code}' result must be {expect!r}, got {r!r}")
    elif code == "s2v":
        if len(ops) != 1 or not S(0):
            return err("'s2v' splats one scalar")
        if len(res) != 1 or not res[0].is_vector():
            return err("'s2v' produces one vector")
        if res[0].type.sew > 64:
            return err("'s2v' destination SEW exceeds 64")
    elif code == "vid":
        if ops or len(res) != 1:
            return err("'vid' takes no operands and one result")
        if res[0].type != VectorType(32, 1, "int"):
            return err("'vid' produces vi32m1")
    elif code == "vsetvli":
        if len(ops) != 1 or not S(0) or ops[0].type.width != 32:
            return err("'vsetvli' takes one i32 AVL operand")
        if len(res) != 1 or res[0].type != I32:
            return err("'vsetvli' produces i32")
        if op.attrs.get("sew") not in (8, 16, 32, 64):
            return err("'vsetvli' SEW must be 8/16/32/64")
        if op.attrs.get("lmul") not in (1, 2, 4, 8):
            return err("'vsetvli' LMUL must be 1/2/4/8")
        if op.attrs.get("policy") not in ("ta,ma", "tu,ma", "ta,mu", "tu,mu"):
            return err("'vsetvli' policy must be e.g. ta,ma")
    elif code == "vbin":
        if len(ops) != 2 or len(res) != 1:
            return err("'vbin' takes two operands and one result")
        a, b, r = V(0), V(1), res[0].type
        if not (a and b and res[0].is_vector()):
            return err("'vbin' requires vector operands")
        if a != b or r != a:
            return err(f"'vbin' types must agree: {a!r}, {b!r} -> {r!r}")
        if op.attrs.get("op") not in VBIN_OPS:
            return err(f"'vbin' op {op.attrs.get('op')!r} unknown")
    elif code == "vbinx":
        if len(ops) != 2 or len(res) != 1:
            return err("'vbinx' takes a vector and a scalar")
        a, s, r = V(0), S(1), res[0].type
        if not a or not s or not res[0].is_vector():
            return err("'vbinx' requires vector and scalar operands")
        if a != r:
            return err(f"'vbinx' result {r!r} must equal the vector {a!r}")
        if s.width > a.sew:
            return err(f"'vbinx' scalar width {s.width} exceeds SEW {a.sew}")
        if op.attrs.get("op") not in VBINX_OPS:
            return err(f"'vbinx' op {op.attrs.get('op')!r} unknown")
    elif code == "vunary":
        if len(ops) != 1 or len(res) != 1 or not V(0) or not res[0].is_vector():
            return err("'vunary' takes one vector and produces one vector")
        if ops[0].type != res[0].type:
            return err("'vunary' must preserve the vector type")
        if op.attrs.get("op") not in VUNARY_OPS:
            return err(f"'vunary' op {op.attrs.get('op')!r} unknown")
    elif code in ("vcmp", "vcmpx"):
        if code == "vcmp" and len(ops) != 2:
            return err("'vcmp' takes two operands")
        if code == "vcmpx" and len(ops) != 2:
            return err("'vcmpx' takes a vector and a scalar")
        if len(res) != 1 or not res[0].is_mask():
            return err(f"'{code}' produces a mask")
        if op.attrs.get("pred") not in CMP_PREDS:
            return err(f"'{code}' predicate unknown")
        if code == "vcmp":
            a, b = V(0), V(1)
            if not (a and b) or a != b:
                return err("'vcmp' requires equal vector types")
        else:
            a, s = V(0), S(1)
            if not a or not s:
                return err("'vcmpx' requires a vector and a scalar")
            if a.kind == "float":
                return err("'vcmpx' (vector-vs-scalar) has no floating form "
                           "in the repertoire; splat the scalar first")
            if s.width > a.sew:
                return err("'vcmpx' scalar width exceeds SEW")
    elif code == "vsel":
        if len(ops) != 3 or len(res) != 1:
            return err("'vsel' takes a mask, a then-value and an else-value")
        m, t, e = ops[0].type, V(1), V(2)
        if not isinstance(m, MaskType):
            return err("'vsel' first operand must be a mask")
        if not (t and e) or t != e or res[0].type != t:
            return err("'vsel' branch types must agree with the result")
    elif code in ("vmovmask", "vpopc"):
        if len(ops) != 1 or not ops[0].is_mask():
            return err(f"'{code}' takes one mask")
        if code == "vmovmask":
            if len(res) != 1 or not res[0].is_mask():
                return err("'vmovmask' produces a mask")
            if res[0].fixed_phys != "v0":
                return err("'vmovmask' must produce the fixed v0 value")
        else:
            if len(res) != 1 or res[0].type != I64:
                return err("'vpopc' produces the i64 popcount")
    elif code == "vwiden":
        if len(ops) != 1 or len(res) != 1:
            return err("'vwiden' takes one operand and one result")
        a, r = V(0), res[0].type
        if not a or not res[0].is_vector():
            return err("'vwiden' is vector to vector")
        if op.attrs.get("mode") not in ("sext", "zext"):
            return err("'vwiden' mode must be sext/zext")
        if r != VectorType(a.sew * 2, a.lmul * 2, "int"):
            return err(f"'vwiden' result must double SEW and LMUL, got {r!r}")
    elif code == "vwaddx0":
        if len(ops) != 1 or len(res) != 1:
            return err("'vwaddx0' takes one operand and one result")
        a, r = V(0), res[0].type
        if not a or not res[0].is_vector():
            return err("'vwaddx0' is vector to vector")
        if op.attrs.get("mode") not in ("sext", "zext"):
            return err("'vwaddx0' mode must be sext/zext")
        if r != VectorType(a.sew * 2, a.lmul * 2, "int"):
            return err(f"'vwaddx0' result must double SEW and LMUL, got {r!r}")
    elif code == "vloadix":
        if len(ops) not in (2, 3):
            return err("'vloadix' takes a base, an index and an optional mask")
        base, idx = S(0), V(1)
        if not base or base != I64:
            return err("'vloadix' base must be i64")
        if not idx or idx.sew != op.attrs.get("eew"):
            return err(f"'vloadix' index SEW {getattr(idx, 'sew', None)} "
                       f"must equal the declared EEW {op.attrs.get('eew')}")
        if len(res) != 1 or not res[0].is_vector():
            return err("'vloadix' produces one vector")
        if res[0].type.sew != op.attrs.get("sew"):
            return err("'vloadix' result SEW must match the region")
    elif code == "vstoreix":
        if len(ops) not in (3, 4):
            return err("'vstoreix' takes base, index, value and a mask")
        if res:
            return err("'vstoreix' produces nothing")
        base, idx, val = S(0), V(1), V(2)
        if not base or base != I64:
            return err("'vstoreix' base must be i64")
        if not idx or idx.sew != op.attrs.get("eew"):
            return err("'vstoreix' index SEW must equal the declared EEW")
        if not val or val.sew != op.attrs.get("sew"):
            return err("'vstoreix' value SEW must match the region")
    elif code == "callbarrier":
        if len(ops) != 1 or ops[0].type != I64:
            return err("'callbarrier' takes the i64 launch pointer")
        if res:
            return err("'callbarrier' produces nothing")
    elif code in ("sspill", "sreload"):
        if code == "sspill" and (len(ops) != 1 or not ops[0].is_scalar()):
            return err("'sspill' takes one scalar")
        if code == "sreload" and (len(ops) != 0 or len(res) != 1
                                  or not res[0].is_scalar()):
            return err("'sreload' produces one scalar")
        if not isinstance(op.attrs.get("slot"), int):
            return err(f"'{code}' requires an integer slot")
    elif code in ("vspill", "vreload"):
        if code == "vspill" and (len(ops) != 1 or not ops[0].is_vector()):
            return err("'vspill' takes one vector")
        if code == "vreload" and (len(ops) != 0 or len(res) != 1
                                  or not res[0].is_vector()):
            return err("'vreload' produces one vector")
        if not isinstance(op.attrs.get("slot"), int):
            return err(f"'{code}' requires an integer slot")
    elif code in ("br", "brc", "ret"):
        pass                      # checked by the block-structure pass
    else:
        errors.append(MirError(Invariant.UNKNOWN_OP, op.loc,
                               f"unknown MIR opcode '{code}'"))


def _mask_semantics(op: MOp, errors: List[MirError]) -> None:
    """Masked memory ops must declare their inactive-position semantics."""
    if op.opcode not in MEM_OPS:
        return
    has_mask = (op.opcode == "vloadix" and len(op.operands) == 3) or \
               (op.opcode == "vstoreix" and len(op.operands) == 4)
    if not has_mask:
        return
    default = op.attrs.get("default")
    if default is None:
        errors.append(MirError(
            Invariant.MASKED_WITHOUT_INACTIVE_SEMANTICS, op.loc,
            f"masked '{op.opcode}' without a declared disabled-position "
            "default (undef/value on loads; no-access on stores)"))
        return
    if op.opcode == "vstoreix" and default != "no-access":
        errors.append(MirError(
            Invariant.MASKED_WITHOUT_INACTIVE_SEMANTICS, op.loc,
            f"masked store declares {default!r}; disabled positions must "
            "perform no access"))
    if op.opcode == "vloadix" and default not in ("undef", "value"):
        errors.append(MirError(
            Invariant.MASKED_WITHOUT_INACTIVE_SEMANTICS, op.loc,
            f"masked load declares {default!r}; disabled positions yield "
            "undef or a declared value, never zero-filled"))


def _region_and_v0(op: MOp, region, errors: List[MirError]) -> Optional[tuple]:
    """vsetvli region consistency and the v0 working-mask constraint.

    Returns the region after this op ((sew, lmul) or None).
    """
    if op.opcode == "vsetvli":
        return (op.attrs["sew"], op.attrs["lmul"])
    if op.opcode not in VEC_OPS:
        return region
    if region is None:
        errors.append(MirError(
            Invariant.VSETVLI_REGION_INCONSISTENCY, op.loc,
            f"vector op '{op.opcode}' executes outside any vsetvli region"))
        return region
    sew, lmul = region
    widths = set()
    for operand in op.operands:
        if isinstance(operand.type, VectorType):
            widths.add((operand.type.sew, operand.type.lmul))
    for result in op.results:
        if isinstance(result.type, VectorType):
            widths.add((result.type.sew, result.type.lmul))
    if op.opcode in ("vwiden", "vwaddx0"):
        # widening: source matches the region, destination doubles
        src = op.operands[0].type
        if (src.sew, src.lmul) != (sew, lmul):
            errors.append(MirError(
                Invariant.VSETVLI_REGION_INCONSISTENCY, op.loc,
                f"widening source {src!r} does not match region "
                f"e{sew}m{lmul}"))
        return region
    if op.opcode == "vloadix":
        dst = op.results[0].type
        if (dst.sew, dst.lmul) != (sew, lmul):
            errors.append(MirError(
                Invariant.VSETVLI_REGION_INCONSISTENCY, op.loc,
                f"'vloadix' result {dst!r} does not match region "
                f"e{sew}m{lmul}"))
        return region
    if op.opcode == "vstoreix":
        val = op.operands[2].type
        if (val.sew, val.lmul) != (sew, lmul):
            errors.append(MirError(
                Invariant.VSETVLI_REGION_INCONSISTENCY, op.loc,
                f"'vstoreix' value {val!r} does not match region "
                f"e{sew}m{lmul}"))
        return region
    for w, m in widths:
        if (w, m) != (sew, lmul):
            errors.append(MirError(
                Invariant.VSETVLI_REGION_INCONSISTENCY, op.loc,
                f"vector width v{w}m{m} does not match the active region "
                f"e{sew}m{lmul}"))
    # the working-mask constraint: masked mem ops and vmerge read hardware v0
    if op.opcode in MASK_READING_OPS:
        mask_operand = None
        if op.opcode == "vsel":
            mask_operand = op.operands[0]
        else:
            mask_operand = op.operands[-1]
        if mask_operand is not None and mask_operand.fixed_phys != "v0":
            errors.append(MirError(
                Invariant.V0_MASK_CONSTRAINT, op.loc,
                f"'{op.opcode}' reads its mask from hardware v0; operand "
                f"{mask_operand.name} is not the fixed v0 value (insert a "
                "vmovmask)"))
    return region


def verify_module(module: MModule) -> List[MirError]:
    """Verify a module; return the list of MirError (empty = valid)."""
    errors: List[MirError] = []
    module.renumber()
    for fn in module.functions:
        _check_terminators(fn, errors)
        dom = _dominators(fn)
        defs: Dict[int, Tuple[str, int]] = {}
        for b in fn.blocks:
            for op in b.ops:
                for r in op.results:
                    defs[r.rid] = (b.name, op.index)
        for b in fn.blocks:
            region = None
            for op in b.ops:
                # use-before-definition (operands here; branch args after)
                for i, operand in enumerate(op.operands):
                    if not _defined_before(op, operand, fn, b, dom, defs):
                        errors.append(MirError(
                            Invariant.USE_BEFORE_DEFINITION, op.loc,
                            f"op '{op.opcode}' operand {i} "
                            f"'{operand.name}' is used before its definition"))
                for i, r in enumerate(op.results):
                    if r.rid in defs and defs[r.rid] != (b.name, op.index):
                        errors.append(MirError(
                            Invariant.USE_BEFORE_DEFINITION, op.loc,
                            f"result {i} '{r.name}' of '{op.opcode}' is "
                            "defined twice"))
                _type_check(op, errors)
                _mask_semantics(op, errors)
                region = _region_and_v0(op, region, errors)
            # branch arguments are uses at the terminator
            term = b.terminator()
            if term is not None:
                for target, args in b.branch_args().items():
                    for a in args:
                        if not _defined_before(term, a, fn, b, dom, defs):
                            errors.append(MirError(
                                Invariant.USE_BEFORE_DEFINITION, term.loc,
                                f"branch argument '{a.name}' to '{target}' "
                                "is used before its definition"))
    return errors


def verify(module: MModule) -> None:
    """Verify a module; raise the first rejection found."""
    errors = verify_module(module)
    if errors:
        raise errors[0]


# ---------------------------------------------------------------------------
# Dump (source attribution survives every stage, IR-OBSERVABILITY)
# ---------------------------------------------------------------------------


def dump_op(op: MOp, indent: str = "  ") -> str:
    res = ", ".join(f"{r.name}:{r.type!r}" for r in op.results)
    ops = ", ".join(f"{o.name}:{o.type!r}" for o in op.operands)
    head = f"{indent}{res} = " if res else f"{indent}"
    attrs = ""
    if op.attrs:
        items = []
        for k in sorted(op.attrs):
            v = op.attrs[k]
            if isinstance(v, (list, tuple)):
                v = "[" + ", ".join(x.name if hasattr(x, "name") else str(x)
                                    for x in v) + "]"
            items.append(f"{k}={v}")
        attrs = " " + " ".join(items)
    loc = f"  ; {_loc_text(op.loc)}" if op.loc is not None else ""
    return f"{head}{op.opcode}({ops}){attrs}{loc}"


def dump_module(module: MModule) -> str:
    out = [f"// mir/v1 module {module.name} source={module.source_path}"]
    if module.meta:
        for key in sorted(module.meta):
            out.append(f"// {key}: {module.meta[key]}")
    for fn in module.functions:
        params = ", ".join(f"{p.name}:{p.type!r}" for p in fn.params)
        out.append(f"fn {fn.name}({params})")
        for b in fn.blocks:
            if b.params:
                p = ", ".join(f"{x.name}:{x.type!r}" for x in b.params)
                out.append(f"{b.name}({p}):")
            else:
                out.append(f"{b.name}:")
            for op in b.ops:
                out.append(dump_op(op))
    return "\n".join(out) + "\n"
