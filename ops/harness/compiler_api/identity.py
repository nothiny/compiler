"""Compilation identity: the unit a compiler actually emits code for.

A *case* is ``(operator, shape, dtype)``; a compiler does not compile a case,
it compiles an *identity* -- source + dtypes + constexpr ``meta`` + launch
config.  Shape and grid are **not** part of an identity: the same kernel with
``M=128`` and ``M=2048`` is one compilation if nothing else changed.

Why it matters: total gate time is ``compiles x cost-per-compile``, and the
corpus controls both knobs.  ``identities < cases`` means the corpus can reuse
artifacts; ``identities == cases`` means every shape change forces a new
compilation (that is the "shape-derived constexpr" smell).

Three tiers, from cheapest to most honest:

``dtype``
    only pointer element types.  This is the floor: a compiler that keyed on
    nothing but dtypes would compile this many times.
``triton``
    ``dtype`` + Triton's integer specialization (``==1`` / ``divisible-by-16``).
    This is what stock Triton 3.x keys on for scalar arguments.
``meta``
    ``triton`` + every constexpr in ``case["meta"]`` / ``case["launch_meta"]``.
    This is the count a "compile once per identity" rule can actually reach;
    it is what a backend that takes ``case["meta"]`` as constexpr must do.

Run ``run_cases.py --dry-run --identities`` for the census, or
``--dry-run --identities --schedule PATH`` to emit the driver work list.
"""
from __future__ import annotations

import hashlib
import json
from typing import Iterable, Mapping

TIERS = ("dtype", "triton", "meta")

#: Meta keys that are launch configuration rather than arithmetic structure;
#: they still belong to the identity because a different value means a
#: different binary.
LAUNCH_KEYS = ("num_warps", "num_stages", "num_ctas", "maxnreg")

#: Meta key prefixes whose value is derived from the grid/shape and therefore
#: never changes the emitted code (they feed address arithmetic only).
_SHAPE_DERIVED_PREFIXES = ("num_pid", "NUM_PID", "num_tiles", "NUM_TILES")


def _classify_int(value: int) -> str:
    """Triton's integer specialization: ``==1`` and ``div-16`` are distinct."""
    if value == 1:
        return "one"
    if value % 16 == 0:
        return "div16"
    return "other"


def _scalar_signature(value) -> tuple:
    """Signature of one runtime (non-constexpr) argument."""
    import numpy as np

    if isinstance(value, np.ndarray):
        return ("ptr", str(value.dtype))
    if isinstance(value, (bool, np.bool_)):
        return ("bool", bool(value))
    if isinstance(value, (int, np.integer)):
        return ("int", _classify_int(int(value)))
    if isinstance(value, (float, np.floating)):
        return ("float", str(np.dtype(type(value)).name))
    return ("object", type(value).__name__)


def pointer_signature(case: Mapping) -> tuple:
    """``bool``-free pointer element types, honouring ``pointer_dtypes``.

    ``bfloat16`` cases store host data as ``float32``; the *device* pointer is
    ``bfloat16`` and that is what the compiler sees, so the override wins.
    """
    overrides = case.get("pointer_dtypes") or {}
    items = []
    for name, value in case.get("args", {}).items():
        if not hasattr(value, "dtype") or getattr(value, "ndim", 0) == 0:
            continue
        dtype = overrides.get(name)
        items.append((name, str(dtype) if dtype else str(value.dtype)))
    return tuple(sorted(items))


def scalar_signature(case: Mapping) -> tuple:
    """Runtime (non-pointer) argument signatures."""
    items = []
    for name, value in case.get("args", {}).items():
        if hasattr(value, "ndim") and getattr(value, "ndim", 0) > 0:
            continue
        items.append((name, _scalar_signature(value)))
    return tuple(sorted(items))


def constexpr_signature(case: Mapping) -> tuple:
    """Every constexpr the compiler sees, ``meta`` first then ``launch_meta``."""
    items = []
    for table in ("meta", "launch_meta"):
        for key, value in (case.get(table) or {}).items():
            if isinstance(value, (list, tuple)):
                value = tuple(value)
            items.append((f"{table}.{key}", repr(value)))
    return tuple(sorted(items))


def _shape_derived_values(shape, case: Mapping) -> set:
    """Values a constexpr takes only because of the grid/shape.

    Covers the two idioms the corpus uses: a raw dimension
    (``NUM_K_BLOCKS``/``NTILES``), and a ceil-division of one (tile counts).
    """
    dims = {int(v) for v in (shape or []) if isinstance(v, (int, float))
            or (isinstance(v, str) and v.isdigit())}
    derived = set(dims)
    blocks = [int(v) for table in ("meta", "launch_meta")
              for v in (case.get(table) or {}).values()
              if isinstance(v, (int, float)) and 1 < int(v) <= 4096]
    for dim in dims:
        for block in blocks:
            derived.add(-(-dim // block))
    total = 1
    for dim in dims:
        total *= dim
    derived.add(total)
    return derived


def structural_drop_keys(entries: Iterable[Mapping]) -> set[str]:
    """Meta keys that are grid/shape-derived for one operator.

    Decided per *key per operator*, not per case: a key is dropped only when
    every case of that operator has a shape-derived value for it (otherwise
    dropping would invent distinctions instead of removing them).
    """
    drop: set[str] = set()
    flags: dict[str, list[bool]] = {}
    for entry in entries:
        case = entry["case"]
        derived = _shape_derived_values(entry.get("shape"), case)
        for table in ("meta", "launch_meta"):
            for key, value in (case.get(table) or {}).items():
                full = f"{table}.{key}"
                if any(key.startswith(p) for p in _SHAPE_DERIVED_PREFIXES):
                    drop.add(full)
                    continue
                shape_only = (isinstance(value, (int, float))
                              and not isinstance(value, bool)
                              and int(value) in derived)
                flags.setdefault(full, []).append(shape_only)
    for full, seen in flags.items():
        if seen and all(seen):
            drop.add(full)
    return drop


def structural_signature(case: Mapping, shape=None,
                         drop_keys: Iterable[str] = ()) -> tuple:
    """Like :func:`constexpr_signature` but drops grid/shape-derived entries.

    Shows how many identities would remain if the kernels took shapes as
    runtime scalars instead of constexprs (the "shape-derived meta" trap).
    This is a diagnostic, not an identity tier.
    """
    drop = set(drop_keys)
    items = []
    for table in ("meta", "launch_meta"):
        for key, value in (case.get(table) or {}).items():
            full = f"{table}.{key}"
            if full in drop or any(key.startswith(p) for p in _SHAPE_DERIVED_PREFIXES):
                continue
            if isinstance(value, (list, tuple)):
                value = tuple(value)
            items.append((full, repr(value)))
    return tuple(sorted(items))


def kernel_name(case: Mapping) -> str:
    """JIT function name (never ``str(JITFunction)`` -- that has an address)."""
    kernel = case.get("kernel")
    if kernel is None:
        return ""
    return getattr(kernel, "__name__", None) or str(kernel).split()[0]


def signature(source: str, case: Mapping, tier: str = "meta", shape=None,
              drop_keys: Iterable[str] = ()) -> tuple:
    """Everything that can change the emitted binary, for one identity tier."""
    if tier not in TIERS and tier != "structural":
        raise ValueError(f"unknown tier {tier!r}; expected one of {TIERS}")
    parts: list = [("source", str(source)),
                   ("kernel", kernel_name(case))]
    parts.append(("ptr", pointer_signature(case)))
    if tier != "dtype":
        parts.append(("scalar", scalar_signature(case)))
    if tier == "meta":
        parts.append(("constexpr", constexpr_signature(case)))
    elif tier == "structural":
        parts.append(("constexpr", structural_signature(case, shape, drop_keys)))
    return tuple(parts)


def case_identity(source: str, case: Mapping, tier: str = "meta",
                  shape=None, drop_keys: Iterable[str] = ()) -> str:
    """Stable 12-hex identity string (sha1 of the canonical signature)."""
    blob = json.dumps(signature(source, case, tier, shape, drop_keys),
                      sort_keys=True, default=str).encode()
    return hashlib.sha1(blob).hexdigest()[:12]


def identity_census(entries: Iterable[Mapping], tiers: Iterable[str] = TIERS) -> dict:
    """Census over ``[{operator, shape, dtype, case, kernel}, ...]``.

    Returns ``{tier: {identities, cases, ratio, per_operator, top}}`` plus the
    ``structural`` diagnostic tier.
    """
    entries = list(entries)
    cases = len(entries)
    report: dict = {"cases": cases, "tiers": {}}
    per_operator_cases: dict[str, int] = {}
    for entry in entries:
        per_operator_cases[entry["operator"]] = \
            per_operator_cases.get(entry["operator"], 0) + 1

    by_operator: dict[str, list] = {}
    for entry in entries:
        by_operator.setdefault(entry["operator"], []).append(entry)

    for tier in list(tiers) + ["structural"]:
        seen: dict[str, set] = {}
        per_operator: dict[str, set] = {}
        drop_by_operator = ({op: structural_drop_keys(group)
                             for op, group in by_operator.items()}
                            if tier == "structural" else {})
        for entry in entries:
            ident = case_identity(entry["operator"], entry["case"], tier,
                                  entry.get("shape"),
                                  drop_by_operator.get(entry["operator"], ()))
            seen.setdefault(ident, set()).add(
                (entry["operator"], tuple(entry.get("shape") or ()),
                 str(entry.get("dtype"))))
            per_operator.setdefault(entry["operator"], set()).add(ident)
        identities = len(seen)
        report["tiers"][tier] = {
            "identities": identities,
            "cases": cases,
            "ratio": round(cases / identities, 3) if identities else None,
            "reused": round(1 - identities / cases, 3) if cases else None,
            "per_operator": {op: len(v) for op, v in per_operator.items()},
            # operators where every case is its own compilation (no reuse)
            "no_reuse": sorted(op for op, v in per_operator.items()
                               if len(v) == per_operator_cases.get(op, 0)
                               and per_operator_cases.get(op, 0) > 1),
        }
    return report


def format_census(report: Mapping) -> str:
    """Human table for ``--dry-run --identities``."""
    cases = report["cases"]
    lines = [f"cases = {cases}"]
    lines.append(f"{'tier':<12}{'identities':>11}{'cases/id':>10}"
                 f"{'reuse':>8}   note")
    notes = {
        "dtype": "only pointer element types (floor)",
        "triton": "+ int ==1 / div-16 specialisation",
        "meta": "+ constexpr meta & launch cfg  <- what to target",
        "structural": "meta minus grid/shape-derived constexprs (diagnostic)",
    }
    for tier, data in report["tiers"].items():
        ratio = data["ratio"] if data["ratio"] is not None else 0.0
        reuse = (data["reused"] or 0.0) * 100
        lines.append(f"{tier:<12}{data['identities']:>11}{ratio:>10.2f}"
                     f"{reuse:>7.1f}%   {notes.get(tier, '')}")
    meta = report["tiers"].get("meta") or {}
    no_reuse = meta.get("no_reuse") or []
    if no_reuse:
        lines.append("")
        lines.append(f"operators where every case is a separate compilation "
                     f"({len(no_reuse)}, shape-derived constexpr suspected):")
        for op in no_reuse[:12]:
            lines.append(f"  {op}")
        if len(no_reuse) > 12:
            lines.append(f"  ... and {len(no_reuse) - 12} more")
    return "\n".join(lines)


def build_schedule(entries: Iterable[Mapping], tier: str = "meta") -> dict:
    """Driver work list: one item per identity, with the cases it covers.

    The parallel driver (16 processes) consumes this instead of the case list:
    compile one identity, then launch every case that maps onto it.
    """
    groups: dict[str, dict] = {}
    for entry in entries:
        ident = case_identity(entry["operator"], entry["case"], tier,
                              entry.get("shape"))
        item = groups.setdefault(ident, {
            "identity": ident,
            "operator": entry["operator"],
            "kernel": entry.get("kernel"),
            "cases": [],
            "cost_hint_s": entry.get("cost_hint_s"),
        })
        item["cases"].append({
            "shape": list(entry.get("shape") or []),
            "dtype": str(entry.get("dtype")),
        })
    items = list(groups.values())
    for item in items:
        item["cases"].sort(key=lambda c: (c["shape"], c["dtype"]))
    # Longest-processing-time-first: heavy identities start first so the
    # makespan is not set by a straggler that begins last.
    items.sort(key=lambda i: (-(i.get("cost_hint_s") or 0.0),
                             -len(i["cases"]), i["operator"]))
    return {"tier": tier, "identities": len(items),
            "cases": sum(len(i["cases"]) for i in items), "items": items}
