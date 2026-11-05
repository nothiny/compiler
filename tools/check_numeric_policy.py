#!/usr/bin/env python3
"""check_numeric_policy.py -- the numeric-policy check (T017).

Property under test (IR-NUMERIC-POLICY, F052): the scan's comparison harness
reads the comparator, the tolerance and the reference from the CASE -- never
from the compiler, never widened, never substituted.  Integer, index and
boolean outputs are exact; floating outputs obey the case's declared
rtol/atol/equal_nan/quantized_interval/allclose_sign_invariant policy.

Probes (each can fail):

  static    tools/run_scan.py passes no rtol/atol override anywhere (the
            driver has no business naming a tolerance) and its comparison
            entry passes exactly (case, actual, expected).

  tolerance a float output inside the declared tolerance compares PASS; the
            same output outside it (but inside a 1e6-widened tolerance)
            FAILS.

  exactness an int output off by one FAILS even under a declared loose
            float tolerance (a float-tolerant reading would pass it).

  reference the correct output FAILS against a tampered reference (the
            reference drives the verdict; the harness never recomputes or
            replaces it), and PASSES against the case's own reference.

  comparator the case's comparator is applied: a whole-column sign flip
            PASSES under a declared allclose_sign_invariant policy (a plain
            allclose reading would reject it) and a non-sign perturbation
            still FAILS; a quantized_interval output inside its interval
            PASSES, a non-integral value inside the interval FAILS and a
            value outside FAILS; NaN-vs-NaN follows the declared equal_nan.

  manifest  the input-regression manifest rows carry each case's own
            comparison policy verbatim (per-case policies are recorded, not
            a global default).

  --witness widens a tolerance in a scratch copy of the comparison harness
            and requires the out-of-policy output to be REJECTED: the
            scratch comparison accepts it, the probe observes the
            acceptance and the witness exits nonzero (the widening is
            caught).  Exit 0 from the witness means the check is vacuous --
            the alarm, not the pass.

Exit codes: 0 = every probe holds (default) / the widened scratch copy
still rejected the out-of-policy output (--witness: vacuous); 1 = a probe
was violated (default) / the widened tolerance was caught (--witness, the
healthy outcome); 2 = witness setup error.
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for entry in (str(ROOT), str(ROOT / "ops" / "harness"), str(ROOT / "tools")):
    if entry not in sys.path:
        sys.path.insert(0, entry)

import numpy as np

import run_scan  # noqa: E402 - the driver under test


# ---------------------------------------------------------------------------
# synthetic cases (the case contract opslib.compare validates)
# ---------------------------------------------------------------------------

def _case(args, outputs, expected, comparison):
    return {"args": args, "outputs": tuple(outputs),
            "expected": expected, "comparison": comparison}


def float_case():
    reference = np.arange(8, dtype=np.float32) * 1.0
    return _case({"out": np.zeros(8, np.float32)}, ("out",),
                 {"out": reference},
                 {"out": {"comparator": "allclose", "rtol": 1e-4,
                          "atol": 1e-4, "equal_nan": False}})


def int_case():
    reference = np.arange(4, dtype=np.int32)
    return _case({"idx": np.zeros(4, np.int32)}, ("idx",),
                 {"idx": reference},
                 {"idx": {"comparator": "allclose", "rtol": 1.0,
                          "atol": 1.0}})


def sign_invariant_case():
    reference = np.array([[1.0, 2.0], [3.0, 4.0]], np.float32)
    return _case({"out": np.zeros((2, 2), np.float32)}, ("out",),
                 {"out": reference},
                 {"out": {"comparator": "allclose_sign_invariant",
                          "shape": [2, 2], "axis": 1, "rtol": 1e-6,
                          "atol": 1e-6, "equal_nan": False}})


def quantized_case():
    reference = np.array([1.0, 2.0], np.float32)
    return _case({"out": np.zeros(2, np.float32)}, ("out",),
                 {"out": reference},
                 {"out": {"comparator": "quantized_interval",
                          "lower": [1.0, 2.0], "upper": [1.0, 2.0]}})


def nan_case(equal_nan):
    reference = np.array([np.nan], np.float32)
    return _case({"out": np.zeros(1, np.float32)}, ("out",),
                 {"out": reference},
                 {"out": {"comparator": "allclose", "rtol": 1e-4,
                          "atol": 1e-4, "equal_nan": equal_nan}})


def _accepts(compare, case, actual):
    """True when the comparison PASSES (no exception)."""
    try:
        compare(case, {name: value for name, value in actual.items()})
        return True
    except Exception:  # noqa: BLE001 - the verdict is the exception
        return False


# ---------------------------------------------------------------------------
# probes
# ---------------------------------------------------------------------------

def probe_static(compare=None) -> tuple:
    """run_scan.py names no tolerance and overrides nothing."""
    source = (ROOT / "tools" / "run_scan.py").read_text()
    tree = ast.parse(source)
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for keyword in node.keywords:
                if keyword.arg in ("rtol", "atol"):
                    findings.append(f"line {node.lineno}: passes "
                                    f"{keyword.arg}= to a call")
    # the comparison entry must forward exactly (case, actual, expected)
    pattern = "return compare_lib.compare_case(case, actual, expected)"
    if pattern not in source:
        findings.append("the comparison entry no longer forwards exactly "
                        "(case, actual, expected) to compare_case")
    return (not findings, "; ".join(findings)
            or "no rtol/atol override anywhere; comparison forwards "
               "(case, actual, expected)")


def probe_tolerance(compare) -> tuple:
    case = float_case()
    reference = case["expected"]["out"]
    inside = reference + np.float32(5e-5)          # within 1e-4
    outside = reference + np.float32(1e-2)         # 100x the declared atol
    ok_in = _accepts(compare, case, {"out": inside})
    ok_out = _accepts(compare, case, {"out": outside})
    # sanity: the widened tolerance really would accept the outside value
    widened_would_accept = bool(np.allclose(
        outside, reference, rtol=1e6, atol=1e6))
    ok = ok_in and not ok_out and widened_would_accept
    note = (" (a 1e6-widened tolerance would accept the outside value, so "
            "the probe discriminates)" if widened_would_accept else "")
    return ok, (f"inside -> {'PASS' if ok_in else 'FAIL'}; "
                f"outside -> {'FAIL' if not ok_out else 'PASS'}{note}")


def probe_exactness(compare) -> tuple:
    case = int_case()
    reference = case["expected"]["idx"]
    off_by_one = reference + np.int32(1)
    float_would_accept = bool(np.allclose(
        off_by_one.astype(np.float64), reference.astype(np.float64),
        rtol=1.0, atol=1.0))
    accepted = _accepts(compare, case, {"idx": off_by_one})
    ok = (not accepted) and float_would_accept
    return ok, (f"int off-by-one -> {'FAIL' if not accepted else 'PASS'} "
                f"(a float reading under the declared rtol=atol=1 would "
                f"{'accept' if float_would_accept else 'reject'} it)")


def probe_reference(compare) -> tuple:
    case = float_case()
    correct = case["expected"]["out"].copy()
    tampered = dict(case)
    tampered["expected"] = {
        "out": case["expected"]["out"]
        + np.float32([5.0, 0, 0, 0, 0, 0, 0, 0])}
    ok_correct = _accepts(compare, case, {"out": correct})
    ok_tampered = _accepts(compare, tampered, {"out": correct})
    ok = ok_correct and not ok_tampered
    return ok, (f"correct output vs the case's reference -> "
                f"{'PASS' if ok_correct else 'FAIL'}; vs a tampered "
                f"reference -> {'FAIL' if not ok_tampered else 'PASS'} "
                f"(the reference drives the verdict)")


def probe_comparator(compare) -> tuple:
    notes, ok = [], True
    # allclose_sign_invariant: a whole-row sign flip passes only under the
    # declared comparator (axis=1: the dot is taken over the non-axis axes)
    case = sign_invariant_case()
    reference = case["expected"]["out"]
    flipped = -reference
    plain_allclose_rejects = not np.allclose(flipped, reference,
                                             rtol=1e-6, atol=1e-6)
    flipped_accepted = _accepts(compare, case, {"out": flipped})
    perturbed = reference + np.float32(10.0)
    perturbed_accepted = _accepts(compare, case, {"out": perturbed})
    if not (plain_allclose_rejects and flipped_accepted
            and not perturbed_accepted):
        ok = False
    notes.append(f"sign_invariant: flip -> "
                 f"{'PASS' if flipped_accepted else 'FAIL'} under the case's "
                 f"comparator (plain allclose would "
                 f"{'reject' if plain_allclose_rejects else 'accept'}); "
                 f"perturbation -> "
                 f"{'FAIL' if not perturbed_accepted else 'PASS'}")
    # quantized_interval
    case = quantized_case()
    inside = _accepts(compare, case, {"out": np.array([1.0, 2.0],
                                                      np.float32)})
    fractional = _accepts(compare, case, {"out": np.array([1.5, 2.0],
                                                          np.float32)})
    outside = _accepts(compare, case, {"out": np.array([1.0, 3.0],
                                                       np.float32)})
    if not (inside and not fractional and not outside):
        ok = False
    notes.append(f"quantized_interval: inside -> "
                 f"{'PASS' if inside else 'FAIL'}; fractional-in-interval -> "
                 f"{'FAIL' if not fractional else 'PASS'}; outside -> "
                 f"{'FAIL' if not outside else 'PASS'}")
    # equal_nan
    for declared, expected_ok in ((False, False), (True, True)):
        case = nan_case(declared)
        accepted = _accepts(compare, case, {"out": np.array([np.nan],
                                                            np.float32)})
        if accepted != expected_ok:
            ok = False
        notes.append(f"equal_nan={declared}: NaN-vs-NaN -> "
                     f"{'PASS' if accepted else 'FAIL'}")
    return ok, "; ".join(notes)


def probe_manifest() -> tuple:
    """The manifest rows carry each case's own comparison policy."""
    import contextlib
    import io
    from opslib.runner import load_operator
    work = Path(tempfile.mkdtemp(prefix="a100-policy-manifest-"))
    try:
        out = work / "manifest.json"
        with contextlib.redirect_stdout(io.StringIO()):
            code = run_scan.main(["--manifest-path",
                                  "ops/suite/manifest.json",
                                  "manifest", "--out", str(out),
                                  "--operator",
                                  "suite/dev/absolute_kernel.py",
                                  "--operator",
                                  "suite/dev/position_quantize.py"])
        if code != 0:
            return False, "the manifest builder failed"
        manifest = json.loads(out.read_text())
        rows = manifest["cases"]
        if not rows:
            return False, "the manifest has no rows"
        # the case's own policy, read back from a freshly built case
        module = load_operator(
            ROOT / "ops" / "suite" / "dev" / "absolute_kernel.py")
        case = module.make_case(shape=rows[0]["shape"],
                                dtype=rows[0]["dtype"], seed=30)
        policy = run_scan._jsonable(case["comparison"])
        if rows[0]["comparison"] != policy:
            return False, (f"manifest policy {rows[0]['comparison']} != "
                           f"the case's policy {policy}")
        comparators = {row["comparison"][name].get("comparator")
                       for row in rows
                       for name in row["comparison"]}
        return True, (f"{len(rows)} rows carry the case's own policy "
                      f"(comparators seen: {sorted(comparators)})")
    finally:
        shutil.rmtree(work, ignore_errors=True)


PROBES = (("static", probe_static),
          ("tolerance", lambda c: probe_tolerance(c)),
          ("exactness", lambda c: probe_exactness(c)),
          ("reference", lambda c: probe_reference(c)),
          ("comparator", lambda c: probe_comparator(c)))


# ---------------------------------------------------------------------------
# the witness
# ---------------------------------------------------------------------------

WIDEN_TARGET = "return compare_lib.compare_case(case, actual, expected)"
WIDENED = ("return compare_lib.compare_case(case, actual, expected, "
           "rtol=1.0e6, atol=1.0e6)")


def _load_scratch_run_scan(scratch: Path):
    spec = importlib.util.spec_from_file_location("run_scan_witness",
                                                  str(scratch))
    module = importlib.util.module_from_spec(spec)
    sys.modules["run_scan_witness"] = module
    spec.loader.exec_module(module)
    return module


def run_witness() -> int:
    work = Path(tempfile.mkdtemp(prefix="a100-policy-witness-"))
    try:
        source = (ROOT / "tools" / "run_scan.py").read_text()
        if source.count(WIDEN_TARGET) != 1:
            print("witness setup error: the comparison entry point is not "
                  "uniquely identifiable (the harness changed?)",
                  file=sys.stderr)
            return 2
        scratch = work / "run_scan.py"
        scratch.write_text(source.replace(WIDEN_TARGET, WIDENED))
        module = _load_scratch_run_scan(scratch)
        case = float_case()
        outside = case["expected"]["out"] + np.float32(1e-2)
        accepted = _accepts(module.compare_outputs, case, {"out": outside})
        if accepted:
            print("witness: the widened tolerance in the scratch copy let "
                  "an out-of-policy output compare PASS -- CAUGHT")
            print("the check can fail; a clean harness result is meaningful")
            return 1                      # nonzero: the widening was caught
        print("FAIL: the widened scratch copy still rejected the "
              "out-of-policy output -- the witness is vacuous")
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="the comparison harness reads tolerance and reference "
                    "from the case, never widening either")
    parser.add_argument("--witness", action="store_true",
                        help="widen a tolerance in a scratch copy of the "
                             "harness and require the out-of-policy output "
                             "to be rejected (the witness exits nonzero "
                             "when the widening is caught)")
    args = parser.parse_args()

    if args.witness:
        return run_witness()

    failures = 0
    for name, probe in PROBES:
        ok, detail = probe(run_scan.compare_outputs)
        print(f"{'PASS' if ok else 'FAIL'} {name}: {detail}")
        failures += 0 if ok else 1
    ok, detail = probe_manifest()
    print(f"{'PASS' if ok else 'FAIL'} manifest: {detail}")
    failures += 0 if ok else 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
