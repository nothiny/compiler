#!/usr/bin/env python3
"""test_mir_passes.py -- the mir-optimize stage's contracts (the
loop-predicate round): the mir-loop-predicate rotation at the MIR level
and, through the real pipeline, the stage's opt-in switch, the
edge-reload deferral it composes with, and executed equivalence.

The pass (A100C_MIRPASS_PRED=on, DEFAULT OFF -- the CompileOptions field
records the measured reason): head-test loops become guarded do-while
loops -- the preheader evaluates the condition on the initial values
once (zero-trip safety preserved), the body's back edge becomes the
conditional branch, the head block disappears.

Checks (each must hold for exit 0):

  * mp-counted-rotated / mp-while-rotated / mp-chunk-rotated: the three
    lowered loop forms (counted with an in-head sconst bound, while with
    the carried condition, chunk with substitutable false args) rotate
    to the guarded form and the rotated modules pass the MIR verifier;
  * mp-declines: the structural refusals (multi-block body, a head
    carrying more than the condition computation, a while head whose
    brc does not read params[0]) keep the original form, counted;
  * mp-witness-broken-rotation: a rotation with a dropped edge arg is
    rejected by the MIR verifier -- the structural check is load-bearing;
  * mp-stage-opt-in: through the real pipeline the stage is off by
    default (stats {"enabled": False}, no stage dump) and rotates when
    enabled, under a distinct cache key;
  * mp-execution-match: a loop-bearing case executes and compares PASS
    under its original policy at 1 and 4 workers in BOTH configurations;
  * mp-edge-reload-deferred: with the deferral on, a tail reload feeding
    only edge args is emitted inside the edge (after the branch), and
    A100C_EDGE_RELOAD=off restores the before-branch placement.

Run: python3 a100c/tests/test_mir_passes.py   (exit 0 = PASS)
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap
ROOT = _bootstrap.bootstrap()
sys.path.insert(0, str(ROOT / "ops/harness"))

from a100c.ir import mir                                   # noqa: E402
from a100c.lower import matrix as matrix_verify            # noqa: E402
from a100c.passes import mir_optimize                      # noqa: E402
from a100c.driver import CompileOptions                    # noqa: E402
from a100c.factory import FactoryCompiler                  # noqa: E402
from a100_support.native_device import NativeExecutableDevice  # noqa: E402
from opslib.compare import compare_case                    # noqa: E402

ATTENTION = ROOT / "ops" / "suite" / "perf" / "attention_forward_triton.py"

_FAILURES = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (" | " + detail if detail else ""),
          flush=True)
    if not ok:
        _FAILURES.append(name)


# ---------------------------------------------------------------------------
# MIR-level fixtures
# ---------------------------------------------------------------------------
def _mk(op, operands=(), results=(), attrs=None, loc=None):
    return mir.MOp(op, list(operands), list(results), attrs=attrs, loc=loc)


def _counted_module(with_sconst_bound=True):
    """pre -> head(i) { [k=sconst(64);] c=slt(i,k); brc c -> body(i), exit(i) }
       body(i) { i2=sadd(i,one); br i2 -> head }  exit(i) { ret }"""
    m = mir.MModule("counted", "test.py")
    fn = mir.MFunction("f", [mir.VReg(mir.I64, name="arg")])
    m.functions.append(fn)
    i0 = mir.VReg(mir.I64, name="i.init")
    ih = mir.VReg(mir.I64, name="i.head")
    pre = mir.Block("pre")
    pre.ops.append(_mk("smove", [fn.params[0]], [i0]))
    head = mir.Block("loop.head", [ih])
    body = mir.Block("loop.body", [ih])
    exit_ = mir.Block("loop.exit", [ih])
    cond = mir.VReg(mir.I64, name="c")
    if with_sconst_bound:
        k = mir.VReg(mir.I64, name="k.bound")
        head.ops.append(_mk("sconst", [], [k], {"value": 64}))
        head.ops.append(_mk("slt", [ih, k], [cond]))
    else:
        head.ops.append(_mk("slt", [ih, fn.params[0]], [cond]))
    head.ops.append(_mk("brc", [cond], [], {
        "true_target": "loop.body", "true_args": [ih],
        "false_target": "loop.exit", "false_args": [ih]}))
    one = mir.VReg(mir.I64, name="one")
    i2 = mir.VReg(mir.I64, name="i.next")
    body.ops.append(_mk("sconst", [], [one], {"value": 1}))
    body.ops.append(_mk("sadd", [ih, one], [i2]))
    body.ops.append(_mk("br", [], [], {"target": "loop.head", "args": [i2]}))
    exit_.ops.append(_mk("ret", [], []))
    pre.ops.append(_mk("br", [], [], {"target": "loop.head", "args": [i0]}))
    fn.blocks = [pre, head, body, exit_]
    m.renumber()
    return m


def _while_module():
    """pre -> head(c) { brc c -> body(c), exit(c) }; body(c) { c2=sconst(0);
    br c2 -> head } -- the condition is carried, not computed in the head."""
    m = mir.MModule("while", "test.py")
    fn = mir.MFunction("f", [mir.VReg(mir.I64, name="arg")])
    m.functions.append(fn)
    c0 = mir.VReg(mir.I64, name="c.init")
    ch = mir.VReg(mir.I64, name="c.head")
    pre = mir.Block("pre")
    pre.ops.append(_mk("smove", [fn.params[0]], [c0]))
    head = mir.Block("loop.head", [ch])
    body = mir.Block("loop.body", [ch])
    exit_ = mir.Block("loop.exit", [ch])
    head.ops.append(_mk("brc", [ch], [], {
        "true_target": "loop.body", "true_args": [ch],
        "false_target": "loop.exit", "false_args": [ch]}))
    c2 = mir.VReg(mir.I64, name="c.next")
    body.ops.append(_mk("sconst", [], [c2], {"value": 0}))
    body.ops.append(_mk("br", [], [], {"target": "loop.head", "args": [c2]}))
    exit_.ops.append(_mk("ret", [], []))
    pre.ops.append(_mk("br", [], [], {"target": "loop.head", "args": [c0]}))
    fn.blocks = [pre, head, body, exit_]
    m.renumber()
    return m


def _chunk_module():
    """The chunk form: head(elem, items) { k=sconst; c=slt(elem,k);
    brc c -> body(elem,items), exit(pid,items) } -- the false args are a
    loop-invariant value and a head param (both substitutable)."""
    m = mir.MModule("chunk", "test.py")
    fn = mir.MFunction("f", [mir.VReg(mir.I64, name="pid")])
    m.functions.append(fn)
    pid = fn.params[0]
    e0 = mir.VReg(mir.I64, name="elem.init")
    n0 = mir.VReg(mir.I64, name="items.init")
    eh = mir.VReg(mir.I64, name="elem.head")
    nh = mir.VReg(mir.I64, name="items.head")
    pre = mir.Block("pre")
    pre.ops.append(_mk("smove", [pid], [e0]))
    pre.ops.append(_mk("smove", [pid], [n0]))
    head = mir.Block("loop.head", [eh, nh])
    body = mir.Block("loop.body", [eh, nh])
    exit_ = mir.Block("loop.exit", [mir.VReg(mir.I64, name="pid.x"),
                                    mir.VReg(mir.I64, name="items.x")])
    k = mir.VReg(mir.I64, name="k.bound")
    cond = mir.VReg(mir.I64, name="c")
    head.ops.append(_mk("sconst", [], [k], {"value": 64}))
    head.ops.append(_mk("slt", [eh, k], [cond]))
    head.ops.append(_mk("brc", [cond], [], {
        "true_target": "loop.body", "true_args": [eh, nh],
        "false_target": "loop.exit", "false_args": [pid, nh]}))
    step = mir.VReg(mir.I64, name="step")
    e2 = mir.VReg(mir.I64, name="elem.next")
    n2 = mir.VReg(mir.I64, name="items.next")
    body.ops.append(_mk("sconst", [], [step], {"value": 32}))
    body.ops.append(_mk("sadd", [eh, step], [e2]))
    body.ops.append(_mk("sadd", [nh, step], [n2]))
    body.ops.append(_mk("br", [], [], {"target": "loop.head",
                                       "args": [e2, n2]}))
    exit_.ops.append(_mk("ret", [], []))
    pre.ops.append(_mk("br", [], [], {"target": "loop.head",
                                      "args": [e0, n0]}))
    fn.blocks = [pre, head, body, exit_]
    m.renumber()
    return m


def _names(m):
    return [b.name for fn in m.functions for b in fn.blocks]


def unit_checks():
    from a100c.passes.mir_optimize import _loop_predicate_function

    for label, mod in (("counted", _counted_module()),
                       ("counted-no-const", _counted_module(False)),
                       ("while", _while_module()),
                       ("chunk", _chunk_module())):
        fn = mod.functions[0]
        n, declines = _loop_predicate_function(fn)
        errs = matrix_verify.verify_module(mod)
        rotated = n >= 1 and "loop.head" not in _names(mod)
        check(f"mp-{label}-rotated", rotated and not errs,
              f"rotated={n} declines={declines} errs={errs[:1]}")
        if rotated:
            body = next(b for b in fn.blocks if b.name == "loop.body")
            term = body.terminator()
            guard = next(b for b in fn.blocks
                         if b.name != "loop.body").terminator()
            check(f"mp-{label}-guarded-do-while",
                  term is not None and term.opcode == "brc"
                  and term.attrs["true_target"] == "loop.body"
                  and term.attrs["false_target"] == "loop.exit"
                  and guard is not None and guard.opcode == "brc"
                  and guard.attrs["true_target"] == "loop.body",
                  f"body term -> {term.attrs.get('true_target')}")

    # declines: a head carrying more than the condition computation
    m = _counted_module()
    fn = m.functions[0]
    head = fn.block("loop.head")
    extra = mir.VReg(mir.I64, name="extra")
    head.ops.insert(1, _mk("sadd", [head.params[0], head.params[0]],
                           [extra]))
    n, declines = _loop_predicate_function(fn)
    check("mp-decline-head-carries-more",
          n == 0 and "head-carries-more" in declines
          and "loop.head" in _names(m), str(declines))

    # declines: a while head whose brc reads a non-param value
    m = _while_module()
    fn = m.functions[0]
    head = fn.block("loop.head")
    other = mir.VReg(mir.I64, name="other")
    head.ops.insert(0, _mk("sconst", [], [other], {"value": 1}))
    head.terminator().operands = (other,)
    n, declines = _loop_predicate_function(fn)
    check("mp-decline-while-cond-not-param0",
          n == 0 and declines.get("cond-not-single-compare", 0) >= 1,
          str(declines))

    # witness: a rotation that drops an edge arg is verifier-rejected
    m = _chunk_module()
    fn = m.functions[0]
    n, _ = _loop_predicate_function(fn)
    body = fn.block("loop.body")
    term = body.terminator()
    term.attrs["true_args"] = term.attrs["true_args"][:1]   # drop one arg
    errs = matrix_verify.verify_module(m)
    check("mp-witness-broken-rotation", bool(errs),
          f"rotated={n}, verifier errors={errs[:1]}")


# ---------------------------------------------------------------------------
# through the real pipeline
# ---------------------------------------------------------------------------
def pipeline_checks():
    spec = importlib.util.spec_from_file_location("op", str(ATTENTION))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    case = module.make_case(shape=(4, 4, 32, 64), dtype="float16", seed=30)

    with tempfile.TemporaryDirectory(prefix="a100c-mir-passes-") as temp:
        results = {}
        for label, opts in (("off", CompileOptions(cache_dir=temp)),
                            ("on", CompileOptions(
                                cache_dir=temp, mir_loop_predicate=True))):
            comp = FactoryCompiler(options=opts)
            staged = NativeExecutableDevice(comp, threads=1).stage_case(case)
            entry = Path(staged.artifact.executable).parent
            art = json.load(open(entry / "artifact.json"))
            stats = art["stages"].get("mir-optimize", {})
            text = (entry / "program.S").read_text()
            heads = len(re.findall(r"^\.L\S+\.head:", text, re.M))
            results[label] = (entry, stats, heads, art, staged)
        off_entry, off_stats, off_heads, off_art, off_staged = results["off"]
        on_entry, on_stats, on_heads, on_art, on_staged = results["on"]
        check("mp-stage-off-by-default",
              off_stats == {"mir-loop-predicate": {"enabled": False}}
              and not (off_entry / "stage.mir.optimized.txt").exists(),
              str(off_stats))
        check("mp-stage-opt-in-rotates",
              on_stats.get("mir-loop-predicate", {}).get("rotated", 0) >= 20
              and on_heads < off_heads
              and (on_entry / "stage.mir.optimized.txt").exists(),
              f"on stats={on_stats} heads {off_heads}->{on_heads}")
        check("mp-distinct-cache-keys",
              on_entry.name != off_entry.name
              and on_art["sha256"] != off_art["sha256"])

        # execution under the original policy, both configurations,
        # 1 and 4 workers
        for label in ("off", "on"):
            staged = results[label][4]
            staged.launch()
            v1 = compare_case(case, staged.outputs())
            opts = CompileOptions(cache_dir=temp,
                                  mir_loop_predicate=(label == "on"))
            dev = NativeExecutableDevice(
                FactoryCompiler(options=opts), threads=4)
            staged4 = dev.stage_case(case)
            staged4.launch()
            v4 = compare_case(case, staged4.outputs())
            check(f"mp-execution-match-{label}",
                  v1["status"] == "PASS" and v4["status"] == "PASS",
                  f"t1={v1['status']} t4={v4['status']}")

        # the edge-reload deferral: a tail reload feeding only edge args
        # moves inside the edge (after the branch -- fused or stub form
        # alike); A100C_EDGE_RELOAD=off restores the before-branch
        # placement
        defer_text = (off_entry / "program.S").read_text()
        moved = re.search(
            r"^(?:bne \w+, zero|blt\w* \w+, \w+), \S+"
            r"(?:(?!^(?:bne|blt|beq|bge)\b).)*?^ld \w+, \d+\(sp\)",
            defer_text, re.M | re.S)
        check("mp-edge-reload-deferred-inside-edge", moved is not None,
              "a reload follows the branch inside an edge")
        comp = FactoryCompiler(options=CompileOptions(
            cache_dir=temp, edge_reload_defer=False))
        staged = NativeExecutableDevice(comp, threads=1).stage_case(case)
        plain = Path(staged.artifact.executable).parent
        nodefer_text = (plain / "program.S").read_text()
        before = re.search(
            r"^ld \w+, \d+\(sp\)"
            r"(?:(?!^ld \w+, \d+\(sp\)).)*?^bne \w+, zero, \S+",
            nodefer_text, re.M | re.S)
        check("mp-edge-reload-off-restores-placement",
              before is not None
              and "no-edge-reload-defer" in nodefer_text,
              "the off build reloads before the branch")


def main() -> int:
    unit_checks()
    pipeline_checks()
    if _FAILURES:
        print(f"test_mir_passes: {len(_FAILURES)} check(s) FAILED: "
              f"{_FAILURES}", file=sys.stderr)
        return 1
    print("test_mir_passes: all checks PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
