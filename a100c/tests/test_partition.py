#!/usr/bin/env python3
"""test_partition.py -- worker range partition over program instances (T007).

The strided round-robin default: worker w of W executes programs w, w+W,
w+2W, ... below the runtime program count.  Every configuration must cover
each program exactly once ("tails owned": the ragged tail program is owned
like any other), never duplicate, and keep the strided order.  The chunk
plan splits a block extent into exact-vl pieces at the target's (SEW, LMUL).

Run: python3 a100c/tests/test_partition.py   (exit 0 = all checks PASS)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()

FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(name)
    return ok


from a100c.plan.partition import (ExecutionPlan, PartitionPolicy,  # noqa: E402
                                  check_partition, partition_table,
                                  strided_range)
from a100c.target import DEFAULT_TARGET  # noqa: E402


def check_strided_properties():
    bad = []
    for workers in (1, 2, 4, 8):
        for programs in (0, 1, 2, 3, 5, 8, 17, 33, 128):
            ok, why = check_partition(workers, programs)
            if not ok:
                bad.append(f"W={workers} P={programs}: {why}")
            table = partition_table(workers, programs)
            flat = [p for row in table for p in row]
            if sorted(flat) != list(range(programs)):
                bad.append(f"W={workers} P={programs}: not exactly-once")
    check("strided-partition-covers-exactly-once", not bad, "; ".join(bad[:3]))


def check_tail_ownership():
    # the ragged tail program is owned exactly once at every worker count
    ok = True
    for workers in (1, 2, 4, 8):
        for programs in (1, 3, 33, 127):
            last = programs - 1
            owners = [w for w in range(workers)
                      if last in strided_range(w, workers, programs)]
            if len(owners) != 1:
                ok = False
    check("ragged-tail-program-owned-exactly-once", ok)


def check_invalid_counts():
    ok = True
    for workers in (0, 3, 5, 6, 7, 9, 16):
        try:
            strided_range(0, workers, 10)
            ok = False
        except ValueError:
            pass
    try:
        strided_range(2, 2, 10)                 # id outside 0..W-1
        ok = False
    except ValueError:
        pass
    try:
        strided_range(0, 2, -1)                 # negative program count
        ok = False
    except ValueError:
        pass
    check("invalid-worker-configurations-refused", ok)


def check_chunk_plan():
    target = DEFAULT_TARGET
    bad = []
    # VLEN=1024, SEW=32 -> vlmax 32
    cases = {128: [32] * 4, 32: [32], 16: [16], 4096: [32] * 128, 1: [1]}
    for block, expected in cases.items():
        chunks = target.chunk_plan(block, 32, 1)
        vls = [vl for vl, _ in chunks]
        if vls != expected:
            bad.append(f"block {block}: {vls} != {expected}")
        total = sum(vls)
        if total != block:
            bad.append(f"block {block}: chunks cover {total} != {block}")
    check("exact-vl-chunk-plan", not bad, "; ".join(bad[:3]))


def check_plan_shape():
    plan = ExecutionPlan()
    plan.chunks = DEFAULT_TARGET.chunk_plan(128, 32, 1)
    plan.block_extent = 128
    desc = plan.describe()
    check("execution-plan-describe",
          desc["block_extent"] == 128 and desc["chunks"] == [[32, 1]] * 4
          and desc["partition"] == "strided"
          and desc["workers"] == [1, 2, 4, 8],
          str(desc["chunks"][:2]))
    policy = PartitionPolicy()
    check("policy-range-model",
          policy.range_of(3, 8, 10) == [3] and policy.range_of(0, 4, 9) ==
          [0, 4, 8])


def main() -> int:
    check_strided_properties()
    check_tail_ownership()
    check_invalid_counts()
    check_chunk_plan()
    check_plan_shape()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_partition: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
