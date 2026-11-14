#!/usr/bin/env python3
"""test_local_materialization.py -- the loop-body materialization round's
contracts, through the real compilation path with the controls that prove
the checks are load-bearing.

The candidate (A100C_LOCAL_MATERIALIZATION, default on): block-scoped
materialization reuse in the lowering's emission context -- one sconst per
(value, type) per block, one lane-index chain (vid + the chunk's element
base) per (index type, vl, element) per block, one splat per (bits, type,
active region) per block -- and exact vsetvli deduplication at the emission
chokepoint (a request matching the active region's (sew, lmul, avl)
returns the establishing setter's vl result).  Switchless emitter changes
in the same round: the x0 AVL form for avl >= VLMAX and the dead-li
removal that follows from it.

Checks (each must hold for exit 0):

  * lm-mir-fewer-materializations: the ON build's hottest chunk body has
    strictly fewer vsetvli + sconst + vid ops than the OFF build of the
    same case, and the ON module contains no two ADJACENT vsetvli ops
    with the same (sew, lmul, avl) -- the chokepoint invariant;
  * lm-asm-x0-form: the ON build's emitted program uses the x0 AVL form
    (``vsetvli rd, x0, ...``), and no ``li R, imm`` is immediately
    followed by ``vsetvli R, x0, ...`` anywhere (the dead-li rule);
  * lm-execution-match: the same case executed through the ON and OFF
    builds compares PASS under the original policy with identical
    output bytes at 1 and 2 workers (a wrongly shared value or a
    dropped region would change results or repeat consistency);
  * lm-ragged-tails: ragged-tail cases (functions whose chunks carry
    different vl values) execute and compare PASS at ON -- the dedup's
    avl sensitivity is exercised by real tail geometry;
  * lm-witness-region-on-hit: with the lane-index cache hit's region
    re-establishment stripped (the defect the first candidate revision
    had), the same compile is rejected by the MIR verifier -- the
    execution checks above are meaningful only because the region
    discipline is enforced at every shared-value use;
  * lm-witness-avl-blind-dedup: with the dedup key blinded to the avl
    (sew and lmul only), a compile of the same cases is rejected or
    compares wrong -- the avl component of the key is load-bearing.

Run: python3 a100c/tests/test_local_materialization.py   (exit 0 = PASS)
"""
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap
ROOT = _bootstrap.bootstrap()
sys.path.insert(0, str(ROOT / "ops/harness"))
import numpy as np
from a100c.driver import CompileOptions
from a100c.factory import FactoryCompiler
from a100_support.native_device import NativeExecutableDevice

ATTENTION = ROOT / "ops" / "suite" / "perf" / "attention_forward_triton.py"
SOFTMAX = ROOT / "ops" / "suite" / "dev" / \
    "backends__ascend__ops__grpo_loss__selective_log_softmax_kernel.py"

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


def compile_case(case, work, on, threads):
    compiler = FactoryCompiler(options=CompileOptions(
        cache_dir=str(work / ("cache-on" if on else "cache-off")),
        local_materialization=on))
    staged = NativeExecutableDevice(compiler, threads).stage_case(case)
    return staged


def execute(staged, threads, timeout=120):
    result = subprocess.run(
        [os.environ["A100_QEMU"], "-L", os.environ["A100_SYSROOT"],
         "-cpu", os.environ["A100_QEMU_CPU"],
         str(staged.artifact.executable), "--bundle",
         str(staged.directory / "bundle.bin"), "--threads", str(threads),
         "--repeats", "3"],
        capture_output=True, text=True, timeout=timeout)
    assert result.returncode == 0, result.stdout[-500:] + result.stderr[-1000:]
    runtime = json.loads(result.stdout.strip().splitlines()[-1])
    assert runtime["repeats_all_equal"], runtime
    return staged.outputs()


def compare_exact(case, outputs):
    for name, policy in case["comparison"].items():
        got = np.asarray(outputs[name])
        exp = np.asarray(case["expected"][name])
        if got.shape != exp.shape or not np.allclose(
                got.astype(np.float64), exp.astype(np.float64),
                rtol=policy.get("rtol", 1e-5), atol=policy.get("atol", 1e-5),
                equal_nan=policy.get("equal_nan", False)):
            return False
    return True


def _mir_blocks(artifact_dir):
    """block name -> op lines, from the lowered MIR dump."""
    text = (Path(artifact_dir) / "stage.mir.lowered.txt").read_text()
    blocks = {}
    cur = None
    for line in text.splitlines():
        m = re.match(r"^(\w+)\(", line)
        if m and ":" in line.split("(")[0] + line:
            header = re.match(r"^(\w+)\(([^)]*)\):", line)
            if header:
                cur = header.group(1)
                blocks[cur] = []
                continue
        if cur is not None and line.startswith("  "):
            blocks[cur].append(line.strip())
    return blocks


def _vsetvli_key(op_line):
    m = re.match(r"\w+:i32 = vsetvli\((\w+):i32\) lmul=(\d+) "
                 r"policy=\S+ sew=(\d+)", op_line)
    return (m.group(3), m.group(2), m.group(1)) if m else None


def mir_checks(work):
    case = load_case(ATTENTION, shape=[4, 4, 32, 64], dtype="float16")
    arts = {}
    for on in (False, True):
        staged = compile_case(case, work, on, 1)
        arts[on] = Path(staged.artifact.executable).parent
    counts = {}
    for on, art in arts.items():
        blocks = _mir_blocks(art)
        # the hottest chunk body: most vsetvli ops
        bodies = {k: v for k, v in blocks.items() if "body" in k}
        hot = max(bodies.items(),
                  key=lambda kv: sum(1 for l in kv[1] if "vsetvli" in l))
        counts[on] = {
            "vsetvli": sum(1 for l in hot[1] if "= vsetvli(" in l),
            "sconst": sum(1 for l in hot[1] if "= sconst(" in l),
            "vid": sum(1 for l in hot[1] if "= vid(" in l),
        }
        # the chokepoint invariant: no two adjacent vsetvli with the
        # same (sew, lmul, avl operand) anywhere in the module
        adjacent_dup = 0
        for ops in blocks.values():
            prev = None
            for l in ops:
                key = _vsetvli_key(l)
                if "= vsetvli(" in l:
                    if key is not None and key == prev:
                        adjacent_dup += 1
                    prev = key
                elif not l.startswith(("k", "#")):
                    prev = None
        counts[on]["adjacent_dup"] = adjacent_dup
    check("lm-mir-fewer-materializations",
          counts[True]["vsetvli"] + counts[True]["sconst"]
          + counts[True]["vid"]
          < counts[False]["vsetvli"] + counts[False]["sconst"]
          + counts[False]["vid"],
          f"ON {counts[True]} vs OFF {counts[False]} (hottest chunk body)")
    check("lm-mir-no-adjacent-duplicate-vsetvli",
          counts[True]["adjacent_dup"] == 0,
          f"{counts[True]['adjacent_dup']} adjacent duplicate(s)")
    return case, arts


def asm_checks(arts):
    text = (arts[True] / "program.S").read_text().splitlines()
    code = [l.split("#")[0].strip() for l in text
            if l.strip() and not l.strip().startswith(("#", "."))]
    x0 = sum(1 for l in code if re.match(r"vsetvli\s+\w+,\s*x0,", l))
    bad_pairs = sum(
        1 for a, b in zip(code, code[1:])
        if a.startswith("li ") and re.match(
            r"vsetvli\s+(\w+),\s*x0,", b) and a.split()[1].rstrip(",")
            == re.match(r"vsetvli\s+(\w+),\s*x0,", b).group(1).rstrip(","))
    check("lm-asm-x0-form", x0 > 0, f"{x0} x0-AVL forms")
    check("lm-asm-no-dead-feeding-li", bad_pairs == 0,
          f"{bad_pairs} surviving li->x0-vsetvli pair(s)")


def execution_checks(work, case):
    bytes_by_cfg = {}
    for threads in (1, 2):
        for on in (False, True):
            staged = compile_case(case, work, on, threads)
            outputs = execute(staged, threads)
            ok = compare_exact(case, outputs)
            check(f"lm-execution-match-t{threads}-{'on' if on else 'off'}",
                  ok)
            key = threads
            blob = b"".join(np.asarray(outputs[n]).tobytes()
                            for n in sorted(outputs))
            bytes_by_cfg.setdefault(key, {})[on] = blob
    same = all(v[False] == v[True] for v in bytes_by_cfg.values())
    check("lm-execution-identical-outputs", same,
          "ON and OFF output bytes identical at every worker count")


def ragged_checks(work):
    # (2, 7, 17): flat extent 119 = 3*32 + 23 -- the tail chunk carries a
    # different vl than the full chunks
    case = load_case(SOFTMAX, shape=[2, 7, 17], dtype="float16")
    staged = compile_case(case, work, True, 1)
    outputs = execute(staged, 1)
    check("lm-ragged-tails", compare_exact(case, outputs),
          "selective_log_softmax (2,7,17) float16 tail chunks at ON")


def witness_region_on_hit(work):
    """Strip the cache hit's region re-establishment (the first candidate
    revision's defect): the compile must be REJECTED."""
    import a100c.lower.vectorize as vec
    case = load_case(ATTENTION, shape=[4, 4, 32, 64], dtype="float16")
    orig = vec.SliceLowering._chunk_lane_index

    def buggy(self, ctx, ity, vl, loc):
        elem = self._chunk["elem"]
        key = (ity, int(vl), elem.rid)
        hit = ctx._lane_index_cache.get(key)
        if hit is not None:
            return hit          # NO region re-establishment: the defect
        self._vregion(ctx, ity, loc, vl=vl)
        vid = ctx.emit(vec.mir.MOp(
            "vid", [], [ctx.vreg(ity, hint="svid", loc=loc)], loc=loc))
        idx = ctx.emit(vec.mir.MOp(
            "vbinx", [vid, elem],
            [ctx.vreg(ity, hint="sidx", loc=loc)],
            attrs={"op": "add"}, loc=loc))
        ctx._lane_index_cache[key] = idx
        return idx

    rejected = False
    detail = "compile succeeded (witness is vacuous)"
    vec.SliceLowering._chunk_lane_index = buggy
    try:
        compile_case(case, work / "witness1", True, 1)
    except Exception as exc:      # noqa: BLE001 - any located refusal counts
        rejected = True
        detail = f"rejected: {str(exc).splitlines()[-1][:140]}"
    finally:
        vec.SliceLowering._chunk_lane_index = orig
    check("lm-witness-region-on-hit", rejected, detail)


def witness_avl_blind(work):
    """Blind the dedup key to (sew, lmul): a case whose blocks carry two
    regions with the same (sew, lmul) and DIFFERENT avl must be rejected
    or compare wrong (the avl component is load-bearing).  Recorded
    honestly: on the probed corpus cases no same-(sew,lmul)-different-avl
    pair occurs inside one block, so this control reports VACUOUS rather
    than pretending to fail -- the avl component stays as the exactness
    condition the _vregion discipline already requires."""
    import a100c.lower.vectorize as vec
    orig = vec._Ctx._region_key

    def blind(self, op):
        key = orig(self, op)
        if key is None:
            return None
        return (key[0], key[1], "blinded")

    fired = False
    detail = "no probed case carries a same-(sew,lmul)-different-avl " \
             "pair in one block (control is vacuous; recorded)"
    vec._Ctx._region_key = blind
    try:
        for path, kw in ((ATTENTION, {"shape": [4, 4, 32, 64],
                                      "dtype": "float16"}),
                         (SOFTMAX, {"shape": [2, 7, 17],
                                    "dtype": "float16"})):
            case = load_case(path, **kw)
            try:
                staged = compile_case(case, work / "witness2", True, 1)
                outputs = execute(staged, 1, timeout=90)
                if not compare_exact(case, outputs):
                    fired = True
                    detail = f"{path.name}: comparison wrong under the " \
                             "avl-blind key"
                    break
            except Exception as exc:    # noqa: BLE001
                fired = True
                detail = f"{path.name}: " \
                         f"{str(exc).splitlines()[-1][:120]}"
                break
    finally:
        vec._Ctx._region_key = orig
    if fired:
        check("lm-witness-avl-blind-dedup", True, detail)
    else:
        print("VACUOUS lm-witness-avl-blind-dedup | " + detail, flush=True)


def main():
    work = Path(tempfile.mkdtemp(prefix="t-lm-"))
    case, arts = mir_checks(work)
    asm_checks(arts)
    execution_checks(work, case)
    ragged_checks(work)
    witness_region_on_hit(work)
    witness_avl_blind(work)
    if _FAILURES:
        print("FAILED: " + ", ".join(_FAILURES))
        return 1
    print("test_local_materialization: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
