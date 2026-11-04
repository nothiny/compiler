"""compare_case (opslib) vs runner.compare (legacy): identical verdicts.

The new single-pass comparison must accept and reject exactly what the old
three-pass implementation accepted and rejected, on adversarial data: NaN,
inf, -0.0, subnormals, tolerance-boundary values, bf16 bit patterns, wide
integers, and sign-invariant policies.  The informational max_abs_error must
match too.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

HARNESS = Path(__file__).resolve().parents[1]     # <root>/harness
ROOT = HARNESS.parent                               # the corpus root
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from opslib import runner  # noqa: E402
from opslib import compare as compare_lib  # noqa: E402


def _run_both(case, actual):
    """(old_outcome, new_outcome): ('PASS', record) or (ExcType, message)."""
    outcomes = []
    for compare in (runner.compare, compare_lib.compare_case):
        try:
            outcomes.append(("PASS", compare(case, actual)))
        except Exception as exc:  # noqa: BLE001
            outcomes.append((type(exc).__name__, str(exc)))
    return outcomes


def _assert_agree(case, actual):
    (old_kind, old), (new_kind, new) = _run_both(case, actual)
    assert old_kind == new_kind, f"{old_kind} != {new_kind}: {old} | {new}"
    if old_kind == "PASS":
        assert old["status"] == new["status"] == "PASS"
        for name, error in old["max_abs_error"].items():
            assert new["max_abs_error"][name] == error, name


def _case(output_storage, expected, policy, *, pointer_dtypes=None):
    name = "out"
    return {
        "args": {name: output_storage},
        "outputs": (name,),
        "expected": {name: expected},
        "comparison": {name: policy},
        **({"pointer_dtypes": {name: pointer_dtypes}} if pointer_dtypes else {}),
    }


ALLCLOSE = {"comparator": "allclose", "exact": False, "rtol": 1e-4,
            "atol": 1e-4, "equal_nan": True}
ALLCLOSE_NO_NAN = {**ALLCLOSE, "equal_nan": False}


def test_random_arrays_agree_across_tolerances():
    rng = np.random.default_rng(1234)
    for trial in range(60):
        n = 512
        reference = rng.standard_normal(n).astype(np.float32)
        scale = [0.0, 1e-5, 1e-4, 1e-3, 1e-1][trial % 5]
        output = reference + (rng.standard_normal(n) * scale).astype(np.float32)
        for policy in (ALLCLOSE, ALLCLOSE_NO_NAN,
                       {**ALLCLOSE, "rtol": 0.0, "atol": 0.0}):
            _assert_agree(_case(reference.copy(), expected=reference.copy(),
                                policy=policy),
                          {name: output.copy() for name in ["out"]})


def test_nan_inf_and_special_values_agree():
    reference = np.array([1.0, np.nan, 2.0, np.inf, -np.inf, 0.0, -0.0,
                          1e-38, 5e-324, -5e-324], dtype=np.float32)
    outputs = [
        reference.copy(),
        reference + 1.0,
        np.where(np.isnan(reference), np.nan, reference),
        np.where(np.isnan(reference), 0.0, reference),
        np.where(np.isinf(reference), 0.0, reference),
    ]
    for output in outputs:
        for policy in (ALLCLOSE, ALLCLOSE_NO_NAN):
            _assert_agree(_case(reference.copy(), expected=reference.copy(),
                                policy=policy),
                          {"out": output.copy()})


def test_tolerance_boundary_values_agree():
    # values engineered to sit exactly at |a-b| == atol + rtol*|b|
    atol = rtol = 1e-3
    reference = np.array([0.0, 1.0, -1.0, 1e3, 1e-3, 123.456], dtype=np.float32)
    output = reference.astype(np.float64)
    output = (output + atol + rtol * np.abs(output)).astype(np.float32)
    output2 = (np.float64(output) + np.spacing(np.float32(atol))).astype(np.float32)
    for candidate in (output, output2, reference + np.float32(1e-4)):
        _assert_agree(_case(reference.copy(), expected=reference.copy(),
                            policy={**ALLCLOSE, "rtol": rtol, "atol": atol}),
                      {"out": candidate.copy()})


def test_float16_and_float64_agree():
    rng = np.random.default_rng(9)
    for dtype in (np.float16, np.float64):
        reference = (rng.standard_normal(1024) * 3).astype(dtype)
        output = (reference.astype(np.float64)
                  + rng.standard_normal(1024) * 2e-4).astype(dtype)
        _assert_agree(_case(reference.copy(), expected=reference.copy(),
                            policy=ALLCLOSE), {"out": output.copy()})


def test_integer_exactness_agree_including_wide_unsigned():
    storage = np.array([1, 2, 3], dtype=np.uint64)
    expected = np.array([1, 2, 3], dtype=np.uint64)
    policy = {"comparator": "allclose", "exact": False, "rtol": 1e-4,
              "atol": 1e-4}  # integer dtype forces exact comparison
    for actual_value in ([1, 2, 3], [1, 2, 4],
                         [1, 2, 3 + (1 << 59)],   # > 2**53: float64 trap
                         [np.iinfo(np.uint64).max, 2, 3]):
        output = np.array(actual_value, dtype=np.uint64)
        _assert_agree(_case(storage.copy(), expected=expected.copy(),
                            policy=policy), {"out": output})


def test_bool_and_signed_outputs_agree():
    policy = {"comparator": "array_equal", "exact": True}
    _assert_agree(_case(np.array([True, False]), expected=np.array([True, False]),
                        policy=policy), {"out": np.array([True, False])})
    _assert_agree(_case(np.array([True, False]), expected=np.array([True, False]),
                        policy=policy), {"out": np.array([True, True])})
    signed = {"comparator": "array_equal", "exact": True}
    _assert_agree(_case(np.array([-2**63, 2**63 - 1], dtype=np.int64),
                        expected=np.array([-2**63, 2**63 - 1], dtype=np.int64),
                        policy=signed),
                  {"out": np.array([-2**63, 2**63 - 1], dtype=np.int64)})
    _assert_agree(_case(np.array([-2**63, 2**63 - 1], dtype=np.int64),
                        expected=np.array([-2**63, 2**63 - 1], dtype=np.int64),
                        policy=signed),
                  {"out": np.array([-2**63, -(2**63 - 1)], dtype=np.int64)})


def test_exact_float_with_equal_nan_agree():
    policy = {"comparator": "array_equal", "exact": True, "equal_nan": True}
    values = np.array([1.0, np.nan, 3.0], dtype=np.float32)
    for output in (values.copy(),
                   np.array([1.0, np.nan, 3.5], dtype=np.float32),
                   np.array([1.0, 0.0, 3.0], dtype=np.float32)):
        _assert_agree(_case(values.copy(), expected=values.copy(), policy=policy),
                      {"out": output.copy()})


def test_bf16_bit_patterns_agree():
    rng = np.random.default_rng(4)
    bits = rng.integers(0, 1 << 16, size=1024, dtype=np.uint16)
    policy = {"comparator": "allclose", "exact": False, "rtol": 1e-2,
              "atol": 1e-2, "equal_nan": True}
    for output_bits in (bits.copy(),
                        bits ^ np.uint16(1),              # 1-ulp flip
                        bits + np.uint16(0x100)):
        _assert_agree(_case(bits.copy(), expected=bits.copy(), policy=policy,
                            pointer_dtypes="bfloat16"),
                      {"out": output_bits.copy()})


def test_sign_invariant_agree():
    rng = np.random.default_rng(5)
    expected = rng.standard_normal((4, 3, 8)).astype(np.float32)
    output = expected.copy()
    for i in range(4):
        if i % 2:
            output[i] *= -1.0                 # flip whole 3x8 blocks
    policy = {"comparator": "allclose_sign_invariant", "shape": (4, 3, 8),
              "axis": 2, "rtol": 0.0, "atol": 1e-5}
    _assert_agree(_case(expected.reshape(-1), expected=expected.reshape(-1),
                        policy=policy), {"out": output.reshape(-1)})
    slightly_off = output + np.float32(1e-2)
    _assert_agree(_case(expected.reshape(-1), expected=expected.reshape(-1),
                        policy=policy), {"out": slightly_off.reshape(-1)})


def test_shape_and_dtype_mismatches_agree():
    reference = np.ones((4, 4), dtype=np.float32)
    case = _case(reference.copy(), expected=reference.copy(), policy=ALLCLOSE)
    _assert_agree(case, {"out": np.ones((4, 4), dtype=np.float32)})
    _assert_agree(case, {"out": np.ones((2, 8), dtype=np.float32)})     # shape
    _assert_agree(case, {"out": np.ones((4, 4), dtype=np.float64)})     # dtype
    _assert_agree(case, {"out": np.ones((4, 4), dtype=np.float32),
                         "extra": np.ones((4, 4), dtype=np.float32)})   # names
    _assert_agree(case, {})                                             # missing


def test_flat_reference_reshapes_like_legacy():
    storage = np.ones((4, 4), dtype=np.float32)
    flat_expected = storage.reshape(-1) * 2.0
    case = _case(storage.copy(), expected=flat_expected.copy(), policy=ALLCLOSE)
    _assert_agree(case, {"out": (storage * 2).copy()})
    _assert_agree(case, {"out": storage.copy()})


def test_rtol_atol_overrides_agree():
    reference = np.linspace(0.0, 10.0, 64).astype(np.float32)
    output = reference + np.float32(0.5)
    case = _case(reference.copy(), expected=reference.copy(), policy=ALLCLOSE)
    for override in ({"rtol": 0.2, "atol": 0.0}, {"rtol": 0.0, "atol": 0.6},
                     {"rtol": 0.0, "atol": 1e-6}):
        old = new = None
        try:
            old = ("PASS", runner.compare(case, {"out": output.copy()},
                                          **override))
        except Exception as exc:  # noqa: BLE001
            old = (type(exc).__name__,)
        try:
            new = ("PASS", compare_lib.compare_case(case, {"out": output.copy()},
                                                    **override))
        except Exception as exc:  # noqa: BLE001
            new = (type(exc).__name__,)
        assert old[0] == new[0]


@pytest.mark.parametrize("n", [1, 2, 17, 16_000_001])   # spans the chunk boundary
def test_chunking_does_not_change_verdicts(n):
    rng = np.random.default_rng(n)
    reference = rng.standard_normal(n).astype(np.float32)
    output = reference + np.float32(1e-3)
    _assert_agree(_case(reference.copy(), expected=reference.copy(), policy=ALLCLOSE),
                  {"out": output.copy()})
    output[n // 2] = 1e9                              # one clear violation
    _assert_agree(_case(reference.copy(), expected=reference.copy(), policy=ALLCLOSE),
                  {"out": output.copy()})
