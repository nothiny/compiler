#!/usr/bin/env python3
"""T043 minimal reproduction: dump actual vs expected for a triu/tril case.

Walks the real path (harness case build -> compile -> native launch -> readback)
and prints the mismatch pattern so the first incorrect stage can be bisected.
Read-only helper for the repair task; not part of the delivered program.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "ops" / "harness"
for p in (str(ROOT), str(HARNESS), str(ROOT / "tools")):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np  # noqa: E402

from compiler_api.run_cases import enumerate_cases  # noqa: E402
from opslib import golden  # noqa: E402
import a100_support.native_device as nd  # noqa: E402


def main() -> int:
    operator = sys.argv[1]
    shape = [int(v) for v in sys.argv[2].split(",")]
    dtype = sys.argv[3]
    threads = int(sys.argv[4]) if len(sys.argv) > 4 else 1

    device = nd.make_device()
    device.threads = threads
    found = None
    key = operator
    if key.startswith("ops/"):
        key = key[4:]
    for spec, cshape, cdtype in enumerate_cases(
            None, None, {key}, [key]):
        if [int(v) for v in cshape] == shape and str(cdtype) == dtype:
            found = (spec, cshape, cdtype)
            break
    assert found, "case not found"
    spec, cshape, cdtype = found
    case = golden.load_or_build_spec(spec, shape=cshape, dtype=cdtype, seed=30,
                                     use_cache=True)
    staged = device.stage_case(case)
    staged.launch()
    actual = staged.outputs()
    print("case:", spec.source, cshape, cdtype, "threads:", threads)
    for name in case["outputs"]:
        exp = np.asarray(case["expected"][name])
        act = np.asarray(actual[name])
        flat_act = act.reshape(-1)
        flat_exp = exp.reshape(-1)
        bad = np.flatnonzero(
            ~np.isclose(flat_act.astype(np.float64),
                        flat_exp.astype(np.float64), rtol=1e-3, atol=1e-3))
        print(f"output {name}: shape {act.shape} bad={bad.size}/{flat_act.size}")
        print("first bad idx:", bad[:16].tolist())
        limit = min(48, flat_act.size)
        print("idx | actual | expected")
        for i in range(limit):
            mark = "  BAD" if i in set(bad[:limit].tolist()) else ""
            print(f"{i:4d} | {flat_act[i]!s:24s} | {flat_exp[i]!s:24s}{mark}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
