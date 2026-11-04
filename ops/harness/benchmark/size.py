"""Resolve a benchmark entry's steady-state shape.

A ``workload.json`` entry carries a *scale rule*, not a fixed shape, so the same
workload is valid on any target: the working set is sized from the **execution
device's last-level cache** (``--llc-bytes``), never from the corpus's tiny
correctness shapes.

Only the **kernel time** is compared; there is no FLOP or byte model.

    python3 bench/size.py --llc-bytes 134217728          # print resolved shapes
    python3 bench/size.py --llc-bytes 62914560 --check    # validate each shape
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]     # <root>/harness
ROOT = HARNESS.parent                               # the corpus root
sys.path.insert(0, str(HARNESS))

DEFAULT_LLC = 128 * 1024 * 1024        # GPU L2 of the reference device
MULTIPLE = 8                            # working set >= 8x LLC


def _prod(values) -> int:
    out = 1
    for v in values:
        out *= int(v)
    return out


def itemsize(dtype: str) -> int:
    """Bytes per element of a workload dtype name (``bfloat16`` included)."""
    return {"float64": 8, "int64": 8, "float32": 4, "int32": 4, "float16": 2,
            "bfloat16": 2, "int16": 2, "int8": 1, "uint8": 1}.get(str(dtype), 4)


def resolve_shape(entry: dict, llc_bytes: int = DEFAULT_LLC, multiple: int = MULTIPLE,
                  dtype: str = "float32") -> list[int]:
    """Return the steady-state shape for one entry.

    Bandwidth-bound entries are sized from the execution device's last-level
    cache; compute-bound entries use a fixed, latency-dominant size (a 2048^3
    GEMM, a 2048-token attention) because they are not launch-bound there.
    """
    target_bytes = llc_bytes * multiple
    rule, model, declared = entry["scale"], entry["bytes_model"], entry["declared_shape"]
    kind = rule["kind"]
    width = itemsize(entry.get("dtype", dtype))
    if kind == "fixed":                              # compute-bound: an explicit shape
        return [int(v) for v in rule["shape"]]
    if kind == "matmul":
        size = int(rule["size"])
        return [size, size, size]
    if kind == "batched_matmul":
        size = int(rule["size"])
        return [int(rule["batch"]), size, size, size]
    if kind == "linear":
        k = int(rule["k"])
        rows = max(1, int(target_bytes // (width * 3)) // max(1, k))
        return [rows, k]
    if kind == "attention":
        return [1, int(rule["heads"]), int(rule["seq"]), int(rule["dim"])]
    if kind == "attention_score":                    # [Z, H, N, NKV, D]
        return [int(rule["z"]), int(rule["h"]), int(rule["n"]), int(rule["nkv"]), int(rule["d"])]
    if kind == "gqa":                                # [Z, HQ, HKV, N, D]
        return [int(rule["z"]), int(rule["hq"]), int(rule["hkv"]),
                int(rule["seq"]), int(rule["d"])]
    if kind == "paged":                              # [S, H, HKV, NB, BS, D]
        return [int(rule["s"]), int(rule["h"]), int(rule["hkv"]),
                int(rule["nb"]), int(rule["bs"]), int(rule["d"])]
    if kind == "lightning":                          # [B, H, T, D, DV]
        return [int(rule["b"]), int(rule["h"]), int(rule["seq"]),
                int(rule["d"]), int(rule["dv"])]
    if kind == "linalg":
        return [int(rule["n"])]
    if kind == "reduce":
        cols = int(rule["cols"])
        full = int(model.get("full", 1))
        rows = max(1, int(target_bytes // (width * max(1, full) * cols)))
        return [rows, cols]
    # first_dim: keep the declared trailing dims, scale dim 0 to the LLC target
    elems = int(target_bytes // (width * max(1, model.get("full", 2))))
    if rule.get("quadratic"):
        n0 = max(1, min(int(rule.get("max", 1 << 15)), int(math.isqrt(elems))))
        return [n0] + list(declared[1:])
    base = _prod(declared[1:]) if len(declared) > 1 else 1
    n0 = max(1, elems // max(1, base))
    step = int(rule.get("multiple_of", 1))      # keep dim 0's divisibility
    n0 = max(step, n0 // step * step)
    return [n0] + list(declared[1:])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workload", default=str(ROOT / "bench" / "workload.json"))
    parser.add_argument("--llc-bytes", type=int, default=DEFAULT_LLC)
    parser.add_argument("--multiple", type=int, default=MULTIPLE)
    parser.add_argument("--group", default=None, help="filter by class: memory|reduction|compute")
    parser.add_argument("--check", action="store_true", help="validate each rule with make_case")
    args = parser.parse_args()

    workload = json.loads(Path(args.workload).read_text())
    op_cache: dict = {}
    for entry in workload["entries"]:
        if args.group and entry["class"] != args.group:
            continue
        shape = resolve_shape(entry, args.llc_bytes, args.multiple, workload["dtype"])
        note = ""
        if args.check:
            from opslib.runner import load_operator
            op = op_cache.setdefault(entry["operator"], load_operator(ROOT / entry["operator"]))
            try:
                op.make_case(shape=tuple(entry["validated_shape"]), dtype=entry.get("dtype", workload["dtype"]), seed=7)
            except Exception as exc:  # noqa: BLE001
                note = f"  FAIL {type(exc).__name__}: {exc}"[:110]
        print(f"{entry['class']:9s} {entry['id']:34s} {entry.get('dtype', workload['dtype']):9s} {str(shape):30s}{note}")


if __name__ == "__main__":
    main()
