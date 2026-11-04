#!/usr/bin/env python3
"""check_stage_barriers.py -- the cross-worker visibility witness
(MECH-WITNESS-TEST; T009, acceptance[3]).

The stage-barrier property: a two-phase cross-worker reduction is correct
only with the declared stage barrier.  The split writes each worker's
partial into its OWNED workspace slot, the barrier (a100rt_stage_barrier,
pthread-based: F054/A006 -- explicit synchronization, no assumed coherence)
establishes visibility, and the merge owner (worker 0) combines the
partials under the source's own merge rule.  Without the barrier the merge
reads slots no barrier has published: the race becomes a WRONG result
(sum-merges read stale zeroed slots and lose other workers' work).

  default mode   compile the REAL artifact for a persistent grid-stride
                 reduction (single program, many chunks: each worker owns
                 a strided share) and require, at every worker count
                 1/2/4/8 and over repeated executions in one process, the
                 outputs compare PASS under the case's own policy.

  --witness mode additionally compile the DEGRADED artifact (the compile
                 option ``witness_drop_stage_barrier``: the same pipeline
                 with the stage barrier call removed from the split path
                 -- a separate artifact identity, never the normal cache)
                 and require its execution to FAIL: with --repeats the
                 race must flip at least one repeat (the runtime's own
                 repeat-mismatch detection exits nonzero, or the outputs
                 compare FAIL).  The witness must fail; a witness that
                 cannot fail proves nothing.

Exit codes: 0 = all required conditions hold; 1 = a condition was violated
(the check can fail).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ops" / "harness"))

import numpy as np  # noqa: E402

import a100_support.native_device as nd  # noqa: E402

#: the two-phase specimen: a persistent grid-stride reduction over one
#: program (grid=(1,)) with enough chunks that every worker owns real
#: work.  All-positive data: a stale (zeroed) partial slot observably
#: shrinks the sum, so the race cannot hide.
SPECIMEN = ROOT / "ops" / "suite" / "dev" / "vdot_kernel_complex.py"

#: repeated executions of the degraded artifact: each repeat is an
#: independent race (the runtime re-zeroes the workspace and restores the
#: inputs per repeat)
REPEATS = 16


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def compare_outputs(outputs, case) -> tuple:
    """The case's own comparison policy (never the compiler grading
    itself)."""
    for name, policy in case["comparison"].items():
        got = np.asarray(outputs[name])
        exp = np.asarray(case["expected"][name])
        if policy.get("exact") or policy["comparator"] == "array_equal":
            ok = np.array_equal(got, exp)
        else:
            ok = np.allclose(got, exp, rtol=policy.get("rtol", 0.0),
                             atol=policy.get("atol", 0.0),
                             equal_nan=policy.get("equal_nan", False))
        if not ok:
            return False, (f"{name}: got {np.ravel(got)[:4]} "
                           f"expected {np.ravel(exp)[:4]}")
    return True, "outputs compare PASS under the case policy"


def run_with_repeats(staged, repeats: int) -> tuple:
    """Run the staged artifact once with --repeats k; returns (ok, detail).

    A nonzero process exit (the runtime's own repeat-mismatch or usage
    contract) or a comparison failure is a failing run."""
    command = [
        str(ROOT / "a100_support" / "run-riscv.sh"),
        str(staged.artifact.executable),
        "--bundle", str(staged.directory / "bundle.bin"),
        "--threads", str(staged.threads),
        "--repeats", str(repeats),
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                timeout=240)
    except subprocess.TimeoutExpired:
        return False, "process did not return (timeout)"
    if result.returncode:
        return False, f"native process exit {result.returncode}: " \
                      f"{result.stderr[-200:]}"
    outputs = staged.outputs()
    return compare_outputs(outputs, staged.case)


def check_real(compiler, module) -> bool:
    """The real artifact: correct at every worker count, with repeats (the
    barrier publishes every partial before the merge reads it, so every
    repeat is identical and PASS)."""
    bad = []
    for threads in (1, 2, 4, 8):
        case = module.make_case(shape=(97,), dtype="float32")
        device = nd.NativeExecutableDevice(compiler, threads)
        staged = device.stage_case(case)
        staged.case = case
        ok, detail = run_with_repeats(staged, REPEATS)
        print(f"real artifact threads={threads} repeats={REPEATS}: "
              f"{'PASS' if ok else 'FAIL'} ({detail})")
        if not ok:
            bad.append(f"threads={threads}: {detail}")
    if bad:
        print("FAIL real artifact: " + "; ".join(bad[:2]))
        return False
    return True


def check_witness(compiler, module) -> bool:
    """The degraded artifact (barrier removed): its execution must FAIL --
    removing the declared synchronization changes the result of the
    cross-worker two-phase case."""
    from a100c.driver import CompileOptions
    degraded = compiler.__class__(options=CompileOptions(
        cache_dir=compiler.cache_dir,
        witness_drop_stage_barrier=True))
    case = module.make_case(shape=(97,), dtype="float32")
    device = nd.NativeExecutableDevice(degraded, 4)
    staged = device.stage_case(case)
    staged.case = case
    ok, detail = run_with_repeats(staged, REPEATS)
    if ok:
        print("FAIL witness: the degraded build (stage barrier removed) "
              "produced correct results across all repeats -- the "
              "synchronization is NOT load-bearing (the check cannot "
              "fail, so it proves nothing)")
        return False
    print(f"witness (stage barrier removed, threads=4, repeats={REPEATS}): "
          f"the two-phase case FAILS as required -- {detail}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--witness", action="store_true",
                        help="also run the degraded (barrier-removed) build "
                             "and require its execution to fail")
    args = parser.parse_args()

    import tempfile
    from a100c.driver import Compiler, CompileOptions
    module = _load(SPECIMEN)
    with tempfile.TemporaryDirectory(prefix="a100c-barrier-") as td:
        compiler = Compiler(options=CompileOptions(cache_dir=str(td)))
        if not check_real(compiler, module):
            return 1
        if args.witness:
            if not check_witness(compiler, module):
                return 1
    print("check_stage_barriers: all required conditions hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
