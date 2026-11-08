#!/usr/bin/env python3
"""test_t043_repairs.py -- the T043 triangular-mask mismatch class, through
the real compilation path (frontend -> TIR -> verify -> MIR -> legalize ->
native compile -> execution -> comparison under the case's own policy),
with the controls that prove the checks are load-bearing.

The repaired defect (12 MISMATCH cases: tril_matmul_kernel_6d320d58 at
[127]/[128] x fp32/fp16/bf16, triu_batch_kernel at [17]/[120] x
fp32/fp16/bf16) was two shared-path defects behind one symptom class:

1. tril -- the FRONTEND constexpr evaluator folded ``not <runtime scalar>``
   to a constant False: ``RuntimeValue`` defines no ``__bool__``, so
   ``_unaryop(ast.Not, v)`` evaluated the OBJECT's truthiness (True) and
   ``not v`` baked False.  ``if not is_above:`` (is_above a runtime scalar)
   then took the all-zeros else arm at compile time: the dot, the k-loop
   and the triangular ``tl.where`` never lowered, and C came out zero at
   every kept (i >= j) position.  The T016 fix covered the same leak for
   ``and``/``or`` (BoolOp); the UnaryOp(Not) arm did not decline
   RuntimeValue operands.  The fix (a100c/frontend/specialize.py): the
   UnaryOp arm declines a RuntimeValue operand exactly like the BoolOp
   arm; ``if not <runtime>:`` then routes to the runtime-if path and
   lowers ``logical.not``.

2. triu -- the LOWERING materialized every ``tl.arange`` as the raw chunk
   positions ``vid + elem`` regardless of the arange's own start/extent.
   An extent-1 arange (``tl.arange(0, BATCH_BLOCK_SIZE)`` with
   BATCH_BLOCK_SIZE=1) is a splat source that joins any open pass; the
   T039 extent-1 staging store writes element 0 from EVERY lane (the
   register is assumed to be the value's splat), so the staged slot held
   the last lane's raw position (elem + vl - 1) instead of the arange's
   element 0 (= start).  triu's row mask then compared
   ``pid + (elem + 15) < batch`` -- false for every chunk -- and the
   store was fully masked off: Y kept its -7 fill value everywhere.  The
   fix (a100c/lower/vectorize.py): the arange materialization emits the
   arange's OWN values -- a splat of ``start`` when the extent is 1, and
   ``start + (vid + elem)`` when ``start != 0`` (the start==0 corpus
   majority keeps its exact previous codegen).

Two enabling repairs the corrected tril form then needed (the same
stage-bisect walk, each with its own control below):

3. the TIR VERIFIER's join scope tracking: an arm that assigns a join
   name to an already-defined value (``c_tile = acc``, acc a loop join)
   encodes the binding as an ALIAS on that value.  Op results define all
   their scope names at their definition point (pdist's ``hi = mid``),
   but loop/if joins defined only the join name -- the alias stayed
   invisible and the both-arms rule rejected the sound outer-value side
   ("join 'c_tile' ... is not defined by both arms").  The fix
   (a100c/ir/tir.py): joins define the join value's scope names
   (aliases included), exactly like op results.

4. the scalar-tree re-materialization rung (a100c/lower/vectorize.py):
   a mid-pass scalar unary (the ``logical.not`` of the runtime if's
   condition) binds inside the pass that hosts its operands and its
   register drops at the pass close; the re-materialization whitelist
   (BIN_ARITH/BIN_BITWISE/CMP_PREDS/MAXMIN_OPS) had no unary rung, so
   the matrix-if's condition read refused with "not lowered before its
   use".  UNARY_OPS joined the whitelist and _materialize_scalar_tree
   lowers the scalar-core unary set.

Checks (each must hold for exit 0):

  * t043-not-runtime-declines-fold: ``not <RuntimeValue>`` evaluates to
    NOT_CONSTEXPR; the differential control (the pre-fix arm without the
    guard) reproduces the silent False fold, and ``not <constexpr bool>``
    still folds -- the guard is load-bearing and the legitimate fold is
    intact;
  * t043-tril-lowers-runtime-branch: the real tril frontend output
    verifies, carries ``logical.not`` feeding a two-arm runtime if, and
    contains the ``linalg.dot`` and the diagonal ``tl.where`` (before the
    fix the TIR held only the all-zeros else arm);
  * t043-verifier-join-alias-side: a hand-built module whose if binds a
    join name to a loop-join value by alias verifies (before the fix:
    carried-value-without-join), and the malformed control (a join name
    defined by no arm at all) is still rejected;
  * t043-arange-own-values: the real triu MIR materializes the extent-1
    arange as a splat of its start (no ``vid`` at the extent-1 arange's
    source line; exactly one ``vid``, the block arange's) and still
    carries the row-compare class;
  * t043-end-to-end-pass: the previously MISMATCH cases execute and
    compare PASS under their own policies -- tril [128] fp32 at one
    thread, tril [127] bfloat16 at four threads (the ragged tail, low
    precision, multi-worker), triu [17] fp32 at one thread and triu
    [120] float16 at four threads.

Run: python3 a100c/tests/test_t043_repairs.py  (exit 0 = all checks PASS)
"""
from __future__ import annotations

import ast
import sys
import tempfile
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
OPS = ROOT / "ops"

warnings.filterwarnings("ignore")

FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}", flush=True)
    if not ok:
        FAILURES.append(name)
    return ok


import os  # noqa: E402

sys.path.insert(0, str(OPS / "harness"))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(str(ROOT))

import run_scan as rs                                        # noqa: E402
import a100_support.native_device as nd                      # noqa: E402
from a100c.backend import legalize as legal_mod              # noqa: E402
from a100c.driver import CompileOptions                      # noqa: E402
from a100c.factory import FactoryCompiler                    # noqa: E402
from a100c.frontend import lower_tir, source, specialize     # noqa: E402
from a100c.frontend.specialize import NOT_CONSTEXPR, \
    RuntimeValue                                             # noqa: E402
from a100c.ir import mir, tir                               # noqa: E402
from a100c.lower import binding as binding_mod               # noqa: E402
from a100c.lower import vectorize                            # noqa: E402
from a100c.passes import pipeline as passes_mod              # noqa: E402
from a100c.plan import grid as grid_mod                      # noqa: E402
from a100c.plan import partition as part_mod                 # noqa: E402
from a100c.target import DEFAULT_TARGET                      # noqa: E402

TRIL = "suite/dev/tril_matmul_kernel_6d320d58.py"
TRIU = "suite/dev/triu_batch_kernel.py"
WORK = Path(tempfile.mkdtemp(prefix="a100c-t043-"))

#: the source lines of tril's extent-1-relevant and block aranges (triu)
TRIU_EXTENT1_ARANGE_LINE = 25     # tl.arange(0, BATCH_BLOCK_SIZE)[:, None]
TRIU_BLOCK_ARANGE_LINE = 29       # tl.arange(0, MN_BLOCK_SIZE)[None, :]
TRIL_NOT_IF_LINE = 86             # if not is_above:


# ---------------------------------------------------------------------------
# shared helpers (the real path pieces)
# ---------------------------------------------------------------------------

def _case_of(operator: str, shape, dtype: str):
    rows = list(rs.enumerated_rows(rs.DEFAULT_MANIFEST, None, [operator]))
    row = next(r for r in rows
               if r["shape"] == list(shape) and r["dtype"] == dtype)
    return rs.build_case(row, 30, use_golden=True)


def _frontend_tir(operator: str, shape, dtype: str):
    """The real frontend output (source -> specialize -> TIR)."""
    case = _case_of(operator, shape, dtype)
    path = ROOT / "ops" / "suite" / operator.split("/", 1)[1]
    src = source.load_operator(str(path))
    spec = specialize.specialize(src, case)
    return lower_tir.lower(src, spec), case


def _build_mir(operator: str, shape, dtype: str):
    """The real path to the legalized MIR of one case."""
    case = _case_of(operator, shape, dtype)
    path = ROOT / "ops" / "suite" / operator.split("/", 1)[1]
    src = source.load_operator(str(path))
    spec = specialize.specialize(src, case)
    tir_module = lower_tir.lower(src, spec)
    grid = grid_mod.extract_grid(src, case)
    layout = binding_mod.argument_layout(case, spec)
    module = vectorize.lower_to_mir(tir_module, part_mod.ExecutionPlan(),
                                    DEFAULT_TARGET, layout, grid)
    legal_mod.legalize(module)
    return module


def _run_case(operator: str, shape, dtype: str, threads: int):
    case = _case_of(operator, shape, dtype)
    compiler = FactoryCompiler(
        options=CompileOptions(cache_dir=str(WORK / "cache")),
        pass_config=passes_mod.PassConfig())
    staged = nd.NativeStagedCase(case, compiler, threads)
    staged.launch()                       # raises on non-zero native exit
    verdict = rs.compare_outputs(case, staged.outputs())
    return verdict.get("status")


# ---------------------------------------------------------------------------
# 1. the frontend constexpr evaluator declines `not <runtime>`
# ---------------------------------------------------------------------------

def check_not_runtime_declines_fold():
    env = specialize.ConstexprEnv()
    rt = RuntimeValue("is_above", tir.INT1, ())
    env.values["is_above"] = rt
    node = ast.parse("not is_above", mode="eval").body
    got = env.evaluate(node)
    ok = got is NOT_CONSTEXPR
    # the differential control: the pre-fix arm (no RuntimeValue guard)
    # reproduced the silent constant fold -- the object's truthiness
    leak = env._unaryop(ast.Not(), rt)
    control_ok = (leak is False)
    # the legitimate fold is intact: `not <constexpr bool>` still folds
    env.values["flag"] = True
    folded = env.evaluate(ast.parse("not flag", mode="eval").body)
    fold_ok = folded is False
    check("t043-not-runtime-declines-fold",
          ok and control_ok and fold_ok,
          f"runtime -> {got!r} (pre-fix leak {leak!r}); "
          f"constexpr not True -> {folded!r}")


# ---------------------------------------------------------------------------
# 2. the real tril frontend lowers the runtime branch
# ---------------------------------------------------------------------------

def _walk_tir_ops(block: tir.Block):
    for stmt in block.statements:
        if isinstance(stmt, tir.Op):
            yield stmt
        elif isinstance(stmt, tir.If):
            yield from _walk_tir_ops(stmt.then)
            yield from _walk_tir_ops(stmt.els)
        elif isinstance(stmt, tir.Loop):
            yield from _walk_tir_ops(stmt.body)


def check_tril_lowers_runtime_branch():
    tir_module, _ = _frontend_tir(TRIL, (128,), "float32")
    errors = tir.verify_module(tir_module)
    verify_ok = not errors
    ops = list(_walk_tir_ops(tir_module.functions[0].body))
    nots = [o for o in ops if o.op == "logical.not"]
    dots = [o for o in ops if o.op == "linalg.dot"]
    # the where and the zeros of the two inner arms
    text = tir_text(tir_module)
    has_where = "select.where" in text
    has_zeros_else = "zeros()" in text
    # the outer runtime if consumes the logical.not
    ifs = [st for st in tir_module.functions[0].body.statements
           if isinstance(st, tir.If)]
    outer = [i for i in ifs
             if i.cond.producer is not None
             and i.cond.producer.op == "logical.not"]
    outer_ok = bool(outer) and all(i.then.statements or i.els.statements
                                   for i in outer)
    ok = (verify_ok and len(nots) == 1 and len(dots) == 1 and has_where
          and has_zeros_else and outer_ok)
    check("t043-tril-lowers-runtime-branch", ok,
          f"verify={len(errors)} err; logical.not={len(nots)}; "
          f"dot={len(dots)}; where={has_where}; zeros={has_zeros_else}; "
          f"runtime-if-on-not={bool(outer)}")


def tir_text(module) -> str:
    from a100c.ir import dump as tir_dump
    return tir_dump.dump_module(module)


# ---------------------------------------------------------------------------
# 3. the verifier accepts an alias-bound join side; rejects the malformed
# ---------------------------------------------------------------------------

LOC = tir.SrcLoc("handbuilt.py", 1, 1)


def _join_alias_module(with_ghost: bool):
    """A loop carrying 'acc', then an if whose then-arm binds the join
    name to the loop's join value BY ALIAS (no statement) and whose
    else-arm defines it by an op -- the tril ``c_tile = acc`` shape."""
    n = tir.Value(tir.INT32, (), LOC, name="n")
    fn = tir.Function("k", [n], LOC)
    mod = tir.Module("k", "handbuilt.py")
    mod.functions.append(fn)

    zero = tir.Op.const(0, tir.INT32, LOC)
    fn.body.statements.append(zero)
    one = tir.Op.const(1, tir.INT32, LOC)
    fn.body.statements.append(one)
    loop = tir.Loop(zero.result(), n, one.result(), LOC)
    loop.carried = (("acc", zero.result()),)
    acc_param = tir.Value(tir.INT32, (), LOC, name="acc")
    inc = tir.Op.binop("arith.add", acc_param, one.result(), LOC)
    inc.result().add_alias("acc")         # the body rebinds the carried name
    loop.body.statements.append(inc)
    acc_join = tir.Value(tir.INT32, (), LOC, name="acc")
    acc_join.add_alias("acc")
    loop.join_results = (acc_join,)
    fn.body.statements.append(loop)

    cond = tir.Op.cmp("cmp.lt", n, n, LOC)
    fn.body.statements.append(cond)
    iff = tir.If(cond.result(), LOC)
    # the then arm stays EMPTY: it binds c_tile to the loop's join value
    # by ALIAS only (exactly what the frontend does for ``c_tile = acc``)
    acc_join.add_alias("c_tile")
    other = tir.Op.const(2, tir.INT32, LOC)
    other.result().add_alias("c_tile")
    iff.els.statements.append(other)
    names = ("c_tile", "ghost") if with_ghost else ("c_tile",)
    iff.join_names = names
    fn.body.statements.append(iff)
    return mod


def check_verifier_join_alias_side():
    errors = tir.verify_module(_join_alias_module(False))
    ok = not errors
    # the malformed control: a join name no arm (and no alias) defines
    ghost_errors = tir.verify_module(_join_alias_module(True))
    control_ok = any(e.invariant == tir.Invariant.CARRIED_WITHOUT_JOIN
                     for e in ghost_errors)
    check("t043-verifier-join-alias-side", ok and control_ok,
          f"alias-side module: {len(errors)} error(s); "
          f"ghost-name control rejected: {control_ok}")


# ---------------------------------------------------------------------------
# 4. the arange materialization emits the arange's own values
# ---------------------------------------------------------------------------

def check_arange_own_values():
    module = _build_mir(TRIU, (17,), "float32")
    text = mir.dump_module(module)
    lines = text.splitlines()

    def src_line(line: str):
        marker = "triu_batch_kernel.py:"
        if marker not in line:
            return 0
        tail = line.split(marker, 1)[1]
        try:
            return int(tail.split(":")[0])
        except (IndexError, ValueError):
            return 0

    vids = [src_line(l) for l in lines if "= vid()" in l]
    # the extent-1 arange site: the materialization is a SPLAT of the
    # arange's start (s2v of a const-0), never vid + elem
    start_splats = 0
    for line in lines:
        if src_line(line) != TRIU_EXTENT1_ARANGE_LINE:
            continue
        for name in _s2v_operands(line):
            for other in lines:
                if other.startswith(f"  {name}:i32 = sconst()") \
                        and "value=0" in other:
                    start_splats += 1
                    break
    ok = (len(vids) == 1 and vids[0] == TRIU_BLOCK_ARANGE_LINE
          and start_splats >= 1)
    check("t043-arange-own-values", ok,
          f"vid ops at lines {vids} (want exactly [{TRIU_BLOCK_ARANGE_LINE}"
          f"]); start-splats at the extent-1 site: {start_splats}")


def _s2v_operands(line: str):
    """The operand names of every ``s2v(...)`` on this dumped MIR line."""
    import re
    out = []
    for match in re.finditer(r"s2v\((\w+):", line):
        out.append(match.group(1))
    return out


# ---------------------------------------------------------------------------
# 5. end to end: the previously MISMATCH cases execute and compare
# ---------------------------------------------------------------------------

def check_end_to_end_pass():
    runs = [
        (TRIL, (128,), "float32", 1),     # the aligned shape
        (TRIL, (127,), "bfloat16", 4),    # the ragged tail, multi-worker
        (TRIU, (17,), "float32", 1),      # the smallest reproduction
        (TRIU, (120,), "float16", 4),     # the batch shape, multi-worker
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
    check("t043-end-to-end-pass", all_ok, "; ".join(details))


def main() -> int:
    check_not_runtime_declines_fold()
    check_tril_lowers_runtime_branch()
    check_verifier_join_alias_side()
    check_arange_own_values()
    check_end_to_end_pass()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_t043_repairs: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
