#!/usr/bin/env python3
"""test_t042_repairs.py -- the T042 fp16/bf16 reduction SIGILL class,
through the real compilation path (frontend -> TIR -> MIR -> legalize ->
allocation -> native compile -> execution -> comparison under the case's
own policy), with the controls that prove the checks are load-bearing.

The repaired defect (24 LAUNCH_FAIL cases; native process exit -4 /
SIGILL at native launch, also at threads 2): reductions over fp16/bf16
data (amax, count_nonzero, mean, nansum, norm__max_norm,
vector_norm__l1_norm) widened their i64 offset domain to e64,m2 and the
allocator placed a compare's MASK DESTINATION strictly inside an m2
source register group -- the emitted ``vmslt.vv v5, v2, v4`` runs at
SEW=64, LMUL=2 with vs2 occupying v4-v5, so vd=v5 sits inside the group.
Probed on the pinned QEMU endpoint (the declared target, F005/F042) at
e64,m2 vl=32 VLEN=1024:

  vd=v5 over vs2 group v4-v5  -> SIGILL   (the failing form)
  vd=v4 (== vs2 group base)   -> ok       (the fp32 artifacts' form)
  vd=v6 (disjoint)            -> ok
  vd=v3 over vs1 group v2-v3  -> SIGILL
  vd=v2 (== vs1 group base)   -> ok
  the same vd=v5 at m1        -> ok       (no group to overlap)

The general fix (a100c/backend/allocate.py, the shared allocation path,
no per-operator branch): a mask-destination compare's vd must not fall
strictly inside an LMUL>1 source register group.  The constraint is
instruction-local, not a global interference edge -- an edge would also
forbid the legal exact-base form the fp32 artifacts already use -- so
the coloring checks the pair's actual placement in BOTH directions (the
mask against already-assigned operand groups, and an operand group
against an already-assigned mask it would strictly contain), and
``_check_group_overlap`` asserts the invariant after every successful
coloring so a regression fails at compile time instead of launching an
illegal instruction.

Checks (each must hold for exit 0):

  * t042-allocation-legal-mask-placement: the real amax fp16 MIR
    allocates with no compare mask strictly inside any LMUL>1/implied
    source group, and the MIR really carries the class (compares over m2
    operands with mask results);
  * t042-control-prefix-coloring-reproduces: with the constraint
    disabled (the pre-fix allocator), the SAME MIR colors the compare
    mask strictly inside a source group (the pre-fix defect, reproduced)
    and the post-allocation assert refuses it with a located diagnostic
    naming the mask, the source and the registers -- the constraint and
    the safety net are load-bearing, not decorative;
  * t042-safety-net-rejects-handbuilt: a hand-built allocation that puts
    a compare mask strictly inside a source group is rejected by
    _check_group_overlap (the malformed-form control);
  * t042-emitted-legal-form: through the real compiler, the emitted
    program.S of every failing-class operator (six operators, fp16)
    contains no mask-destination compare whose vd sits strictly inside a
    source register group at the active LMUL>1, and each program still
    executes its compares at m2 (the class is exercised, not avoided);
  * t042-end-to-end-pass: the previously LAUNCH_FAIL cases execute and
    compare PASS under their own policies (amax fp16/bfloat16 [17] at
    one thread, mean bfloat16 [17] at two threads -- the worker-count
    finding class); the pre-fix artifacts died with exit -4 before
    producing any output.

Run: python3 a100c/tests/test_t042_repairs.py  (exit 0 = all checks PASS)
"""
from __future__ import annotations

import re
import sys
import tempfile
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
for _p in (str(ROOT / "ops" / "harness"), str(ROOT / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

warnings.filterwarnings("ignore")

FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}", flush=True)
    if not ok:
        FAILURES.append(name)
    return ok


import run_scan as rs                                        # noqa: E402
import a100_support.native_device as nd                      # noqa: E402
from a100c.backend import allocate as alloc_mod              # noqa: E402
from a100c.backend import legalize as legal_mod              # noqa: E402
from a100c.driver import CompileOptions                      # noqa: E402
from a100c.factory import FactoryCompiler                    # noqa: E402
from a100c.frontend import lower_tir, source, specialize     # noqa: E402
from a100c.ir import mir                                     # noqa: E402
from a100c.lower import binding as binding_mod               # noqa: E402
from a100c.lower import vectorize                            # noqa: E402
from a100c.passes import pipeline as passes_mod              # noqa: E402
from a100c.plan import grid as grid_mod                      # noqa: E402
from a100c.plan import partition as part_mod                 # noqa: E402
from a100c.target import DEFAULT_TARGET                      # noqa: E402

AMAX = "suite/dev/amax_kernel_1.py"
MEAN = "suite/dev/mean_kernel_1.py"
CLASS_OPERATORS = (
    "suite/dev/amax_kernel_1.py",
    "suite/dev/count_nonzero_kernel_1.py",
    "suite/dev/mean_kernel_1.py",
    "suite/dev/nansum_kernel_1.py",
    "suite/dev/norm__max_norm_kernel_1.py",
    "suite/dev/vector_norm__l1_norm_kernel_1.py",
)
WORK = Path(tempfile.mkdtemp(prefix="a100c-t042-"))


# ---------------------------------------------------------------------------
# the shared invariant: no compare mask strictly inside a source group
# ---------------------------------------------------------------------------

def _operand_span(o: mir.VReg, implied: dict) -> int:
    return max(o.type.lmul if o.is_vector() else 1, implied.get(o.rid, 1))


def _mask_in_group_violations(fn: mir.MFunction, assignment: dict,
                              shapes=None) -> list:
    """Every (mask, its register, source, its register, span) where a
    mask-destination compare's vd sits strictly inside an LMUL>1 source
    register group -- the probed illegal-instruction form."""
    implied = alloc_mod._index_implied_groups(fn)
    out = []
    for b in fn.blocks:
        for op in b.ops:
            if op.opcode not in ("vcmp", "vcmpx"):
                continue
            if not op.results or not op.results[0].is_mask():
                continue
            dst = assignment.get(op.results[0].rid)
            if not dst or not dst.startswith("v"):
                continue
            d = int(dst[1:])
            for o in op.operands:
                if not o.is_vector():
                    continue
                nm = assignment.get(o.rid)
                if not nm or not nm.startswith("v"):
                    continue
                base = int(nm[1:])
                span = (_operand_span(o, implied) if shapes is None
                        else shapes.get(o.rid, ("vec", 1))[1])
                if base < d < base + span:
                    out.append((op.results[0].name, dst, o.name, nm, span))
    return out


def _compare_group_class_count(fn: mir.MFunction) -> int:
    """How many compares in this MIR read an LMUL>1 vector operand into a
    mask destination -- the failing opcode class's MIR shape."""
    count = 0
    for b in fn.blocks:
        for op in b.ops:
            if op.opcode not in ("vcmp", "vcmpx"):
                continue
            if not op.results or not op.results[0].is_mask():
                continue
            if any(o.is_vector() and o.type.lmul > 1 for o in op.operands):
                count += 1
    return count


def _build_mir(operator: str, shape, dtype: str):
    """The real frontend path to the legalized MIR of one case."""
    rows = list(rs.enumerated_rows(rs.DEFAULT_MANIFEST, None, [operator]))
    row = next(r for r in rows
               if r["shape"] == list(shape) and r["dtype"] == dtype)
    case = rs.build_case(row, 30, use_golden=True)
    path = ROOT / "ops" / "suite" / operator.split("/", 1)[1]
    src = source.load_operator(str(path))
    spec = specialize.specialize(src, case)
    tir_module = lower_tir.lower(src, spec)
    grid = grid_mod.extract_grid(src, case)
    layout = binding_mod.argument_layout(case, spec)
    module = vectorize.lower_to_mir(tir_module, part_mod.ExecutionPlan(),
                                    DEFAULT_TARGET, layout, grid)
    legal_mod.legalize(module)
    return module, case


# ---------------------------------------------------------------------------
# unit level: the allocation invariant, on the real failing MIR
# ---------------------------------------------------------------------------

def check_allocation_legal_mask_placement():
    module, _ = _build_mir(AMAX, (17,), "float16")
    fn = module.functions[0]
    try:
        alloc = alloc_mod.allocate(module, DEFAULT_TARGET)
    except alloc_mod.AllocationError as exc:
        check("t042-allocation-legal-mask-placement", False, str(exc)[:120])
        return
    violations = _mask_in_group_violations(fn, alloc.assignment, alloc.shapes)
    class_count = _compare_group_class_count(fn)
    check("t042-allocation-legal-mask-placement", not violations,
          f"{len(violations)} violation(s)"
          + (f" e.g. {violations[0]}" if violations else ""))
    # the class is really exercised in this MIR: compares over m2 groups
    check("t042-mir-carries-the-class", class_count >= 1,
          f"{class_count} compare(s) over LMUL>1 operands with mask results")


def check_control_prefix_coloring():
    """The pre-fix allocator, reproduced by disabling the constraint:
    the coloring itself must place a compare mask strictly inside a
    source group, and the safety net must refuse it."""
    module, _ = _build_mir(AMAX, (17,), "float16")
    fn = module.functions[0]
    fixed = {}
    for b in fn.blocks:
        for op in b.ops:
            for r in op.results:
                if r.fixed_phys == "v0":
                    fixed[r.rid] = "v0"
    original = alloc_mod._mask_compare_groups
    try:
        alloc_mod._mask_compare_groups = lambda fn_: ({}, {})
        assignment, failed = alloc_mod._try_color(fn, DEFAULT_TARGET, fixed)
        reproduced = []
        if assignment is not None:
            reproduced = _mask_in_group_violations(fn, assignment)
        check("t042-control-prefix-coloring-reproduces",
              assignment is not None and bool(reproduced),
              "constraint-off coloring: "
              + (f"{len(reproduced)} mask-in-group placement(s), e.g. "
                 f"{reproduced[0]}" if reproduced
                 else "no violation reproduced (control is vacuous)"))
        # the full path with the constraint disabled must be refused by
        # the post-allocation assert, naming the illegal form
        module2, _ = _build_mir(AMAX, (17,), "float16")
        refused = False
        detail = ""
        try:
            alloc_mod.allocate(module2, DEFAULT_TARGET)
            detail = "allocate succeeded past the illegal form"
        except alloc_mod.AllocationError as exc:
            refused = True
            detail = str(exc)[:160]
        check("t042-control-safety-net-refuses", refused, detail)
    finally:
        alloc_mod._mask_compare_groups = original


def check_safety_net_rejects_handbuilt():
    """A hand-built allocation with the mask strictly inside a source
    group is rejected (the malformed-form control: the assert can fire)."""
    module, _ = _build_mir(AMAX, (17,), "float16")
    fn = module.functions[0]
    alloc = alloc_mod.allocate(module, DEFAULT_TARGET)
    # find one compare over an m2 operand and force its mask inside the
    # operand's group
    target_op = None
    for b in fn.blocks:
        for op in b.ops:
            if op.opcode not in ("vcmp", "vcmpx"):
                continue
            if not op.results or not op.results[0].is_mask():
                continue
            for o in op.operands:
                if o.is_vector() and o.type.lmul > 1:
                    src = alloc.assignment.get(o.rid, "")
                    if src.startswith("v"):
                        target_op = (op, o)
                        break
            if target_op:
                break
        if target_op:
            break
    if target_op is None:
        check("t042-safety-net-rejects-handbuilt", False,
              "no compare over an m2 operand in the MIR (control setup "
              "failed)")
        return
    op, operand = target_op
    base = int(alloc.assignment[operand.rid][1:])
    span = alloc.shapes.get(operand.rid, ("vec", 1))[1]
    if span < 2:                                        # implied-group case
        span = 2
    inside = f"v{base + 1}"
    alloc.assignment[op.results[0].rid] = inside
    refused = False
    detail = ""
    try:
        alloc_mod._check_group_overlap(fn, alloc)
        detail = "the assert accepted the hand-built illegal form"
    except alloc_mod.AllocationError as exc:
        refused = True
        detail = str(exc)[:160]
    check("t042-safety-net-rejects-handbuilt", refused, detail)


# ---------------------------------------------------------------------------
# the emitted legal form, through the real compiler
# ---------------------------------------------------------------------------

#: the compare mnemonics that write a mask destination (repertoire rows
#: for vcmp; the .vx forms read a GPR scalar, no register group)
_COMPARE_VV = re.compile(
    r"^\s*(vmslt|vmsle|vmsltu|vmsleu|vmseq|vmsne|vmflt|vmfle|vmfeq|vmfne)"
    r"\.vv\s+v(\d+),\s*v(\d+),\s*v(\d+)")
_VSETVLI = re.compile(r"^\s*vsetvli\s+\w+,\s*\w+,\s*"
                      r"e(\d+),\s*m(\d+),\s*ta,ma")


def _scan_emitted_compares(text: str):
    """(illegal, m2_compares) over one emitted program: every
    mask-destination compare is checked against the LMUL active at its
    position (the region discipline: vsetvli establishes the state)."""
    illegal = []
    m2_compares = 0
    lmul = 1
    for line in text.splitlines():
        state = _VSETVLI.match(line)
        if state:
            lmul = int(state.group(2))
            continue
        m = _COMPARE_VV.match(line)
        if not m:
            continue
        vd, vs1, vs2 = (int(m.group(k)) for k in (2, 3, 4))
        if lmul > 1:
            m2_compares += 1
            for src in (vs1, vs2):
                if src < vd < src + lmul:
                    illegal.append((line.strip(), f"vd=v{vd} inside "
                                   f"v{src}-v{src + lmul - 1}"))
    return illegal, m2_compares


def check_emitted_legal_form():
    cache = WORK / "cache"
    compiler = FactoryCompiler(
        options=CompileOptions(cache_dir=str(cache)),
        pass_config=passes_mod.PassConfig())
    all_ok = True
    details = []
    for operator in CLASS_OPERATORS:
        rows = list(rs.enumerated_rows(rs.DEFAULT_MANIFEST, None, [operator]))
        row = next(r for r in rows
                   if r["dtype"] == "float16")   # the failing dtype
        case = rs.build_case(row, 30, use_golden=True)
        payload = {k: v for k, v in case.items()
                   if k not in ("expected", "oracle_args")}
        artifact = compiler.compile_case(payload)
        program = Path(artifact.executable).parent / "program.S"
        illegal, m2 = _scan_emitted_compares(program.read_text())
        ok = not illegal and m2 >= 1
        all_ok = all_ok and ok
        details.append(f"{operator.split('/')[-1]}: "
                       f"{m2} m2-compare(s), {len(illegal)} illegal")
        if illegal:
            details.append(f"  e.g. {illegal[0]}")
    check("t042-emitted-legal-form", all_ok, "; ".join(details))


# ---------------------------------------------------------------------------
# end to end: the previously LAUNCH_FAIL cases execute and compare
# ---------------------------------------------------------------------------

def _run_case(operator: str, shape, dtype: str, threads: int):
    rows = list(rs.enumerated_rows(rs.DEFAULT_MANIFEST, None, [operator]))
    row = next(r for r in rows
               if r["shape"] == list(shape) and r["dtype"] == dtype)
    case = rs.build_case(row, 30, use_golden=True)
    compiler = FactoryCompiler(
        options=CompileOptions(cache_dir=str(WORK / "cache")),
        pass_config=passes_mod.PassConfig())
    staged = nd.NativeStagedCase(case, compiler, threads)
    staged.launch()                       # raises on non-zero native exit
    verdict = rs.compare_outputs(case, staged.outputs())
    return verdict.get("status")


def check_end_to_end_pass():
    runs = [
        (AMAX, (17,), "float16", 1),
        (AMAX, (17,), "bfloat16", 1),
        (MEAN, (17,), "bfloat16", 2),     # the worker-count finding class
    ]
    all_ok = True
    details = []
    for operator, shape, dtype, threads in runs:
        try:
            status = _run_case(operator, shape, dtype, threads)
            ok = status == "PASS"
            detail = (f"{operator.split('/')[-1]} {dtype} {list(shape)} "
                      f"@{threads}T -> {status}")
        except Exception as exc:                    # noqa: BLE001
            ok = False
            detail = (f"{operator.split('/')[-1]} {dtype} {list(shape)} "
                      f"@{threads}T -> {type(exc).__name__}: "
                      f"{str(exc)[:90]}")
        all_ok = all_ok and ok
        details.append(detail)
    check("t042-end-to-end-pass", all_ok, "; ".join(details))


def main() -> int:
    check_allocation_legal_mask_placement()
    check_control_prefix_coloring()
    check_safety_net_rejects_handbuilt()
    check_emitted_legal_form()
    check_end_to_end_pass()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_t042_repairs: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
