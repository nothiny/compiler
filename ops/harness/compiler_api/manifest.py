"""Generate a machine-readable manifest for the whole operator corpus.

The compiler agent consumes ``manifest.json`` instead of parsing each
operator's Python AST: every entry lists the single ``@triton.jit`` kernel,
its parameters (pointer / scalar / constexpr), the launch grid description,
the declared SHAPES x DTYPES, and the output names.

Usage:
    python3 compiler_api/manifest.py                       # full corpus -> ./manifest.json
    python3 compiler_api/manifest.py --group basic --out /tmp/m.json   # subsets need --out

``module`` is the operator file's path **relative to the repository root**
(the same value as ``operator``), so the manifest is valid in any checkout.
A subset (``--group`` / a non-``all`` ``--channel``) is never written over the
repository's full ``manifest.json``: pass ``--out`` (or ``--out -`` for stdout).
"""
from __future__ import annotations

import argparse
import inspect
import json
import sys
from pathlib import Path

import numpy as np

HARNESS = Path(__file__).resolve().parents[1]     # <root>/harness
ROOT = HARNESS.parent                               # the corpus root
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from opslib import catalog  # noqa: E402


def _kernel_target(kernel):
    """Unwrap Autotuner/Heuristics/JITFunction down to the Python function."""
    target = kernel
    for _ in range(8):
        if inspect.isfunction(target):
            return target
        nested = getattr(target, "fn", None)
        if nested is None or nested is target:
            return target
        target = nested
    return target


def _signature(kernel, case):
    """Parameter list with kind inferred from the case (reliable) and the
    annotation (fallback)."""
    args = case.get("args", {}) or {}
    meta = case.get("meta", {}) or {}
    try:
        parameters = inspect.signature(_kernel_target(kernel)).parameters
    except (TypeError, ValueError):
        return []
    result = []
    for name, param in parameters.items():
        if name in meta:
            kind = "constexpr"
        elif isinstance(args.get(name), np.ndarray):
            kind = "pointer"
        elif "constexpr" in str(param.annotation):
            kind = "constexpr"
        else:
            kind = "scalar"
        result.append({"name": name, "kind": kind})
    return result


def _autotune(kernel):
    configs = getattr(kernel, "configs", None)
    if not configs:
        return None
    return {
        "key": list(getattr(kernel, "key", []) or []),
        "configs": [{"kwargs": dict(getattr(c, "kwargs", {}) or {}),
                     "num_warps": getattr(c, "num_warps", None),
                     "num_stages": getattr(c, "num_stages", None)}
                    for c in configs],
    }


def _grid(kernel, case):
    grid = case.get("grid")
    if callable(grid):
        return {"kind": "callable", "note": "grid depends on the autotune config"}
    if grid is None:
        return None
    if isinstance(grid, (tuple, list)):
        return [int(g) for g in grid]
    return str(grid)


def _to_list(value):
    if isinstance(value, (list, tuple)):
        return [_to_list(item) for item in value]
    return int(value)


def build(channel: str = "all", group: str | None = None) -> dict:
    from opslib.catalog import summary

    operators = []
    counts = {"total": 0, "supported": 0, "unsupported": 0, "triton_kernel": 0,
              "torch_reference": 0, "cases": 0, "cases_constructible": 0}
    for spec in catalog.specs(channel):
        if group not in (None, "all") and spec.entry["group"] != group:
            continue
        counts["total"] += 1
        supported = spec.supported
        if not supported:
            counts["unsupported"] += 1
            continue
        counts["supported"] += 1
        counts["triton_kernel" if spec.execution == "triton_kernel"
               else "torch_reference"] += 1
        module = spec.load()
        raw_shapes = list(getattr(module, "SHAPES", []))
        shapes = [_to_list(s) for s in raw_shapes]
        dtypes = [str(d).rsplit(".", 1)[-1] for d in getattr(module, "DTYPES", [])]
        declared = len(shapes) * len(dtypes)
        counts["cases"] += declared
        constructible = 0
        case_errors = []
        for shape in raw_shapes:
            for dtype in dtypes:
                try:
                    spec.make_case(shape=shape, dtype=dtype, seed=30)
                    constructible += 1
                except Exception as exc:  # noqa: BLE001 - diagnostics
                    case_errors.append({"shape": _to_list(shape), "dtype": str(dtype),
                                        "error": f"{type(exc).__name__}: {exc}"[:160]})
        counts["cases_constructible"] = counts.get("cases_constructible", 0) + constructible
        entry = {
            "operator": spec.source,
            "name": spec.name,
            "group": spec.entry["group"],
            "channel": spec.channel,
            "execution": spec.execution,
            "verification": spec.verification,
            "module": spec.source,
            "shapes": shapes,
            "dtypes": dtypes,
            "case_count": declared,
            "cases_declared": declared,
            "cases_constructible": constructible,
        }
        if case_errors:
            entry["case_errors"] = case_errors
        try:
            first_shape = raw_shapes[0] if raw_shapes else None
            first_dtype = dtypes[0] if dtypes else None
            case = spec.make_case(shape=first_shape, dtype=first_dtype, seed=30)
            kernel = case.get("kernel")
            if kernel is None:
                entry["error"] = "case has no kernel"
                operators.append(entry)
                continue
            entry["kernel"] = getattr(_kernel_target(kernel), "__name__", None)
            entry["parameters"] = _signature(kernel, case)
            entry["constexpr_values"] = {k: _jsonable(v)
                                         for k, v in (case.get("meta") or {}).items()}
            entry["launch_meta"] = {k: _jsonable(v)
                                    for k, v in (case.get("launch_meta") or {}).items()}
            entry["autotune"] = _autotune(kernel)
            entry["grid"] = _grid(kernel, case)
            entry["outputs"] = list(case.get("outputs") or [])
            entry["output_dtypes"] = {
                name: str(value.dtype) for name, value in (case.get("expected") or {}).items()}
        except Exception as exc:  # pragma: no cover - diagnostics only
            entry["error"] = f"{type(exc).__name__}: {exc}"
        operators.append(entry)
    return {"schema_version": 1, "channel": channel, "counts": counts,
            "catalog": summary(channel), "operators": operators}


def _jsonable(value):
    if isinstance(value, (int, float, bool, str)) or value is None:
        return value
    return str(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", default="all",
                        choices=("all", "both", "local", "T", "G"))
    parser.add_argument("--group", default=None,
                        help="one directory: basic|medium|hard|bench")
    parser.add_argument("--out", default=None,
                        help="output path, or - for stdout (default: ./manifest.json, "
                             "full corpus only; a subset requires --out)")
    args = parser.parse_args()
    subset = args.group is not None or args.channel != "all"
    full_path = ROOT / "manifest.json"
    if args.out is None:
        if subset:
            parser.error("a subset manifest (--group/--channel) needs --out: refusing "
                         f"to overwrite the full corpus manifest {full_path}")
        out = full_path
    else:
        out = None if args.out == "-" else Path(args.out)
        if out is not None and subset and out.resolve() == full_path.resolve():
            parser.error(f"refusing to write a subset manifest over {full_path}")
    manifest = build(args.channel, args.group)
    text = json.dumps(manifest, indent=2) + "\n"
    if out is None:
        sys.stdout.write(text)
        return
    out.write_text(text)
    print(json.dumps(manifest["counts"], indent=2))
    print("wrote", out)


if __name__ == "__main__":
    main()
