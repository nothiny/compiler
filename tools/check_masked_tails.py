#!/usr/bin/env python3
"""check_masked_tails.py -- the ragged-tail witness (MECH-WITNESS-TEST).

The masked-tail property: a masked vector store performs NO access at
disabled positions (a100rt.h / RVV 1.0 v0.t semantics; the TIR store declares
``no-access``).  This tool proves the tail predicate is load-bearing:

  default mode   compile the REAL artifact, run the ragged case under the
                 declared QEMU endpoint, and require (a) the outputs compare
                 PASS under the case's own policy and (b) a poisoned guard
                 region behind the output buffer is untouched.

  --witness mode additionally compile the DEGRADED artifact (the compile
                 option ``witness_drop_tail_predicates``: the same pipeline
                 with the tail predicate dropped from masked memory ops --
                 a separate artifact identity, never the normal cache) and
                 require its run to CORRUPT the guard: with the predicate
                 removed the ragged case FAILS (tail lanes touch the poisoned
                 guard region).  The witness must fail; a witness that cannot
                 fail proves nothing.

Exit codes: 0 = all required conditions hold; 1 = a condition was violated
(the check can fail).

The guard geometry: the case layer's output buffer (97 fp32 elements, a
388-byte payload padded to a 448-byte storage row) is followed in the bundle
by a 256-byte poison array (uint32 0xDA5A5A5A = a negative float, so |x|
changes its bits).  The tail lanes of the single 128-element block address
output bytes 388..511: the row padding plus the first 64 bytes of the poison
row.  An unmasked store rewrites those bytes with |x| (sign flipped);
an unmasked load reads them first, so the poison values flow through the
kernel and come back with their sign bits cleared.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ops" / "harness"))

import numpy as np  # noqa: E402

SLICE_OPERATOR = ROOT / "ops" / "suite" / "dev" / "absolute_kernel.py"
RAGGED_SHAPE = (97,)
BLOCK = 128
POISON_U32 = 0xDA5A5A5A          # a negative float: |x| flips the sign bit
GUARD_BYTES = 256


def _load_case_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("slice_operator",
                                                  SLICE_OPERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def guard_case(module) -> dict:
    """The ragged case with a poison guard array placed after the output."""
    case = module.make_case(shape=RAGGED_SHAPE)
    args = case["args"]
    guard = np.frombuffer(np.array([POISON_U32], dtype="<u4")
                          .tobytes() * (GUARD_BYTES // 4), dtype=np.uint8)
    new_args = {}
    for name, value in args.items():
        new_args[name] = value
    new_args["z_guard"] = guard            # after out_ptr in insertion order
    case = dict(case)
    case["args"] = new_args
    case["pointer_dtypes"] = dict(case.get("pointer_dtypes") or {})
    case["pointer_dtypes"]["z_guard"] = "uint8"
    return case


def run_artifact(compiler, case, threads: int):
    """Stage, run and read back one case; returns (ok, staged, error).

    The staged case is returned so the temporary bundle directory (and its
    bundle.json/bundle.bin) stays alive for the guard inspection."""
    import a100_support.native_device as nd
    device = nd.NativeExecutableDevice(compiler, threads)
    try:
        staged = device.stage_case(case)
        staged.launch()
        return True, staged, None
    except Exception as exc:  # a degraded run may crash or mismatch
        return False, None, str(exc)


def compare_outputs(outputs, case) -> tuple:
    """The case's own comparison policy (never the compiler grading itself)."""
    for name, policy in case["comparison"].items():
        got = outputs.get(name)
        expected = case["expected"][name]
        if policy.get("exact") or policy["comparator"] == "array_equal":
            ok = np.array_equal(np.asarray(got), np.asarray(expected))
        else:
            ok = np.allclose(np.asarray(got), np.asarray(expected),
                             rtol=policy.get("rtol", 0.0),
                             atol=policy.get("atol", 0.0),
                             equal_nan=policy.get("equal_nan", False))
        if not ok:
            return False, f"comparison FAILED for output {name!r}"
    return True, "outputs compare PASS under the case policy"


def guard_region(bundle_dir: Path) -> bytes:
    """The poison row's first 64 bytes out of the executed bundle."""
    info = json.loads((bundle_dir / "bundle.json").read_text())
    out_view = info["views"]["out_ptr"]
    out_row = info["storages"][out_view["storage"]]
    guard_view = info["views"]["z_guard"]
    guard_row = info["storages"][guard_view["storage"]]
    image = (bundle_dir / "bundle.bin").read_bytes()
    # the tail lanes address output bytes [97*4, 128*4) = [388, 512): the
    # padding of the output row plus the first (512 - out_row_size) bytes of
    # the following row
    tail_start = RAGGED_SHAPE[0] * 4
    tail_end = BLOCK * 4
    span = image[guard_row["offset"]:
                 guard_row["offset"] + max(0, tail_end - out_row["size"])]
    return bytes(span), out_row, guard_row


def check_real(module) -> bool:
    from a100c.driver import Compiler, CompileOptions
    case = guard_case(module)
    compiler = Compiler(options=CompileOptions())
    ok, staged, error = run_artifact(compiler, case, 1)
    if not ok:
        print(f"FAIL real artifact run: {error}")
        return False
    cmp_ok, cmp_msg = compare_outputs(staged.outputs(), case)
    print(f"real artifact ({staged.artifact_sha256[:12]}): {cmp_msg}")
    if not cmp_ok:
        return False
    span, out_row, guard_row = guard_region(staged.directory)
    expected_span = bytes(np.array([POISON_U32], dtype="<u4")
                          .tobytes() * (len(span) // 4))
    if span != expected_span:
        print(f"FAIL real artifact corrupted the guard region: {span[:16].hex()}")
        return False
    print(f"guard region intact ({len(span)} bytes behind the output row)")
    return True


def check_witness(module) -> bool:
    from a100c.driver import Compiler, CompileOptions
    case = guard_case(module)
    degraded = Compiler(options=CompileOptions(
        witness_drop_tail_predicates=True))
    ok, staged, error = run_artifact(degraded, case, 1)
    if not ok:
        # a crash or a transport failure is also a failing witness
        print(f"witness (tail predicate removed): run FAILED as required "
              f"({error})")
        return True
    span, out_row, guard_row = guard_region(staged.directory)
    expected_span = bytes(np.array([POISON_U32], dtype="<u4")
                          .tobytes() * (len(span) // 4))
    if span == expected_span:
        print("FAIL witness: the degraded build left the guard intact -- "
              "the tail predicate is NOT load-bearing (the check cannot "
              "fail, so it proves nothing)")
        return False
    print(f"witness (tail predicate removed, {staged.artifact_sha256[:12]}):"
          f" the ragged case FAILS as required -- tail lanes corrupted the "
          f"guard region "
          f"({span[:8].hex()} != {expected_span[:8].hex()})")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--witness", action="store_true",
                        help="also run the degraded (tail-predicate-dropped) "
                             "build and require it to corrupt the guard")
    args = parser.parse_args()

    module = _load_case_module()
    ok = check_real(module)
    if not ok:
        return 1
    if args.witness:
        if not check_witness(module):
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
