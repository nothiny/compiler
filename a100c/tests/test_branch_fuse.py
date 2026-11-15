#!/usr/bin/env python3
"""test_branch_fuse.py -- the branch-fuse round's contracts, through the
real compilation path plus unit-level rule checks on crafted streams.

The candidate (A100C_BRANCH_FUSE, default on), two provable rewrites at the
emission stage:

* bare-stub elimination -- a brc taken edge whose argument-move sequence is
  empty routes through a stub holding exactly one ``j``; the branch is
  retargeted to the destination directly (guarding the CB-format ±4 KiB
  range conservatively and requiring the stub label unreferenced
  elsewhere);
* compare+branch fusion -- a ``slt/sltu`` immediately before its brc whose
  result vreg is read nowhere else in the module (exact MIR def-use over
  operands and edge args) folds into ``blt/bltu``; applied only when the
  emitted stream still shows the pair intact.

Checks (each must hold for exit 0):

  * bf-unit-stub-eliminated / bf-unit-fusion-fired: the unit rewrites on
    crafted streams produce exactly the specified forms with counters;
  * bf-unit-refusals: stubs with moves, out-of-range targets and
    multiply-referenced labels decline; a fusion candidate whose stream has
    an instruction between the pair declines (the textual verification is
    load-bearing -- without it the fused branch could read clobbered
    sources);
  * bf-round-fires: a real loop-bearing case fires both rules (artifact
    counters >= 1 each) and the emitted loop head is the direct form
    (``blt`` to the body, the false-edge ``j``, the body label next);
  * bf-off-control: A100C_BRANCH_FUSE=off emits the pre-round forms (no
    annotations, no fused branches, empty counters) under a distinct cache
    key;
  * bf-execution-match: the same case executes and compares PASS under its
    original policy at 1 and 4 workers on BOTH the on and off builds.

Run: python3 a100c/tests/test_branch_fuse.py   (exit 0 = PASS)
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap
ROOT = _bootstrap.bootstrap()
sys.path.insert(0, str(ROOT / "ops/harness"))

from a100c.backend.emit import _peephole_branch   # noqa: E402
from a100c.driver import CompileOptions           # noqa: E402
from a100c.factory import FactoryCompiler         # noqa: E402
from a100_support.native_device import NativeExecutableDevice  # noqa: E402
from opslib.compare import compare_case           # noqa: E402
import importlib.util                              # noqa: E402

SOFTMAX = ROOT / "ops" / "suite" / "dev" / \
    "softmax_single_block_forward_kernel.py"

_FAILURES = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (" | " + detail if detail else ""),
          flush=True)
    if not ok:
        _FAILURES.append(name)


def load_case(path, **kw):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.make_case(**kw)


# ---------------------------------------------------------------------------
# unit-level rule checks on crafted streams
# ---------------------------------------------------------------------------
def unit_checks():
    # a bare stub: eliminated, branch retargeted
    lines = [
        "    slt t1, t0, s9  # [op1] k.py:1:1",
        "    bne t1, zero, .Lbrc7_true  # [op2] k.py:1:1",
        "    j .Lexit1  # [op2] k.py:1:1",
        ".Lbrc7_true:  # [op2] k.py:1:1",
        "    j .Lbody1  # [op2] k.py:1:1",
        ".Lbody1:  # block body1",
        "    addi t0, t0, 1  # [op3] k.py:1:1",
        "    j .Lhead1  # [op4] k.py:1:1",
    ]
    out, counts = _peephole_branch(list(lines))
    check("bf-unit-stub-eliminated",
          counts["stubs_removed"] == 1
          and any("bne t1, zero, .Lbody1" in l for l in out)
          and not any(l.strip() == "j .Lbody1" for l in out),
          str(counts))

    # fusion: a candidate pair with the dead compare
    out, counts = _peephole_branch(
        list(lines),
        candidates=[{"slt": 0, "bne": 1, "rd": "t1", "a": "t0", "b": "s9",
                     "unsigned": False}])
    check("bf-unit-fusion-fired",
          counts["cmp_fused"] == 1 and counts["stubs_removed"] == 1
          and any(l.strip().startswith("blt t0, s9, .Lbody1") for l in out)
          and any("[peephole-cmpfuse]" in l for l in out),
          str(counts))

    # refusal: an instruction between the pair (the scheduler moved
    # something in) -- the textual verification must decline
    lines_between = [
        "    slt t1, t0, s9  # [op1] k.py:1:1",
        "    add t2, t0, t0  # [opX] k.py:1:1",
        "    bne t1, zero, .Lbrc7_true  # [op2] k.py:1:1",
        "    j .Lexit1  # [op2] k.py:1:1",
        ".Lbrc7_true:  # [op2] k.py:1:1",
        "    j .Lbody1  # [op2] k.py:1:1",
        ".Lbody1:  # block body1",
    ]
    out, counts = _peephole_branch(
        list(lines_between),
        candidates=[{"slt": 0, "bne": 2, "rd": "t1", "a": "t0", "b": "s9",
                     "unsigned": False}])
    check("bf-unit-refusal-instruction-between",
          counts["cmp_fused"] == 0 and counts["cmp_declined"] == 1
          and any(l.strip().startswith("slt t1, t0, s9") for l in out),
          str(counts))

    # refusal: a stub carrying argument moves
    lines_moves = [
        "    bne t1, zero, .Lbrc8_true  # [op2] k.py:1:1",
        "    j .Lexit1  # [op2] k.py:1:1",
        ".Lbrc8_true:  # [op2] k.py:1:1",
        "    mv t2, t3  # [op2] k.py:1:1",
        "    j .Lbody1  # [op2] k.py:1:1",
        ".Lbody1:  # block body1",
    ]
    out, counts = _peephole_branch(list(lines_moves))
    check("bf-unit-refusal-stub-with-moves",
          counts["stubs_removed"] == 0 and counts["stubs_declined"] == 1
          and any(l.split("#", 1)[0].strip() == "j .Lbody1" for l in out),
          str(counts))

    # refusal: out-of-range target (the CB-format displacement guard)
    far = ["    bne t1, zero, .Lbrc9_true  # [op2] k.py:1:1",
           "    j .Lexit1  # [op2] k.py:1:1",
           ".Lbrc9_true:  # [op2] k.py:1:1"]
    far += [f"    # filler comment {i}" for i in range(1200)]
    far += ["    j .Lbody1  # [op2] k.py:1:1", ".Lbody1:  # block body1"]
    out, counts = _peephole_branch(far)
    check("bf-unit-refusal-out-of-range",
          counts["stubs_removed"] == 0 and counts["stubs_declined"] == 1,
          str(counts))

    # refusal: the stub label referenced by a second branch
    lines_multiref = [
        "    bne t1, zero, .LbrcA_true  # [op2] k.py:1:1",
        "    beq t4, zero, .LbrcA_true  # [op5] k.py:1:1",
        "    j .Lexit1  # [op2] k.py:1:1",
        ".LbrcA_true:  # [op2] k.py:1:1",
        "    j .Lbody1  # [op2] k.py:1:1",
        ".Lbody1:  # block body1",
    ]
    out, counts = _peephole_branch(list(lines_multiref))
    check("bf-unit-refusal-multiref-label",
          counts["stubs_removed"] == 0 and counts["stubs_declined"] >= 1,
          str(counts))


# ---------------------------------------------------------------------------
# through the real compilation path
# ---------------------------------------------------------------------------
def round_checks():
    case = load_case(SOFTMAX, shape=(20, 17), dtype="float16", seed=30)

    with tempfile.TemporaryDirectory(prefix="a100c-branch-fuse-") as temp:
        # ON build (the default pipeline)
        on = FactoryCompiler(options=CompileOptions(cache_dir=temp))
        staged_on = NativeExecutableDevice(on, threads=1).stage_case(case)
        entry_on = Path(staged_on.artifact.executable).parent
        art_on = json.load(open(entry_on / "artifact.json"))
        stats = art_on["stages"]["emission"].get("peephole_branch", {})
        text = (entry_on / "program.S").read_text()
        check("bf-round-fires",
              stats.get("stubs_removed", 0) >= 1
              and stats.get("cmp_fused", 0) >= 1,
              str(stats))
        # the direct loop-head form: a fused branch straight to a block
        # (not to a surviving stub), the false-edge jump, then the block
        # label right after (no stub between)
        direct = None
        for fm in re.finditer(r'^\s*(blt|bltu) (\w+), (\w+), (\S+)',
                              text, re.M):
            if not fm.group(4).endswith('_true'):
                direct = fm
                break
        check("bf-round-direct-form", direct is not None,
              direct.group(0) if direct else "no direct fused branch")
        if direct:
            # the branch reaches its block directly: the target label
            # exists and no stub trampoline label lies between
            target = direct.group(4)
            tpos = text.find("\n" + target + ":")
            seg = text[direct.end():tpos if tpos > 0 else len(text)]
            check("bf-round-no-stub-between",
                  tpos > 0
                  and not re.search(r'^\.Lbrc\d+_true:$', seg, re.M),
                  f"target {target} at +{tpos - direct.end()} chars")
        check("bf-round-annotations",
              "[peephole-stub]" in text and "[peephole-cmpfuse]" in text)
        remaining_stubs = len(
            re.findall(r'^\.Lbrc\d+_true:', text, re.M))
        check("bf-round-remaining-stubs-match-declines",
              remaining_stubs == stats.get("stubs_declined", 0),
              f"{remaining_stubs} labels vs {stats.get('stubs_declined')} declines")

        # OFF build (the control): pre-round forms, distinct key
        off = FactoryCompiler(options=CompileOptions(
            cache_dir=temp, branch_fuse=False))
        staged_off = NativeExecutableDevice(off, threads=1).stage_case(case)
        entry_off = Path(staged_off.artifact.executable).parent
        art_off = json.load(open(entry_off / "artifact.json"))
        stats_off = art_off["stages"]["emission"].get("peephole_branch", {})
        text_off = (entry_off / "program.S").read_text()
        check("bf-off-control",
              stats_off == {}
              and "[peephole-stub]" not in text_off
              and "[peephole-cmpfuse]" not in text_off
              and re.search(r'^\s*bne \w+, zero, \.Lbrc\d+_true',
                            text_off, re.M) is not None
              and entry_off.name != entry_on.name
              and art_off["sha256"] != art_on["sha256"],
              f"key separation on={entry_on.name[:8]} off={entry_off.name[:8]}")

        # execution + comparison under the original policy, both builds,
        # 1 and 4 workers
        for label, staged in (("on", staged_on), ("off", staged_off)):
            dev = NativeExecutableDevice(
                FactoryCompiler(options=CompileOptions(
                    cache_dir=temp,
                    branch_fuse=(label == "on"))), threads=4)
            staged4 = dev.stage_case(case)
            staged4.launch()
            verdict4 = compare_case(case, staged4.outputs())
            staged.launch()
            verdict1 = compare_case(case, staged.outputs())
            check(f"bf-execution-match-{label}",
                  verdict1["status"] == "PASS" and verdict4["status"] == "PASS",
                  f"t1={verdict1['status']} t4={verdict4['status']}")


def main() -> int:
    unit_checks()
    round_checks()
    if _FAILURES:
        print(f"test_branch_fuse: {len(_FAILURES)} check(s) FAILED: "
              f"{_FAILURES}", file=sys.stderr)
        return 1
    print("test_branch_fuse: all checks PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
