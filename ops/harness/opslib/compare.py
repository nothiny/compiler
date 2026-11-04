"""Single-pass output comparison (and the optional device-side fast path).

``runner.compare`` validates a case's outputs against its oracle in *three*
full passes over data of benchmark size: ``np.testing.assert_allclose`` (its
own temporaries), then a float64 ``delta`` recomputation, then the equality
mask.  At 1 GiB outputs that is several seconds per entry and a handful of
full-size temporaries.

``compare_case`` here produces **identical verdicts and identical error
metrics** while touching the data once, in ~16M-element chunks:

  - the pass/fail predicate is ``np.isclose`` itself (what
    ``assert_allclose`` calls internally), so the tolerance arithmetic stays
    in the arrays' dtype exactly as before;
  - the informational ``max_abs_error`` keeps the old definition
    (``max |a-b|`` in float64 over elements that are not exactly equal);
  - on failure the first violating flat indices are reported.

``compare_case_on_device`` asks the ``Device`` to run the same comparison on
the device buffers (uploading only the expected values, reading back only
scalars); it returns ``None`` whenever the device or the policy does not
support it, and the caller falls back to the host path.  bf16 bit patterns
and ``allclose_sign_invariant`` always use the host path.
"""
from __future__ import annotations

import numpy as np

_CHUNK = 16 * 1024 * 1024   # elements per chunk (~64 MiB of float64)
_MAX_REPORT = 8             # violating indices reported on failure


# ------------------------------------------------------------- case checks
def _alias_pairs(aliases):
    """Normalize the supported alias metadata forms into two-item pairs."""
    pairs = []
    if isinstance(aliases, dict):
        for name, targets in aliases.items():
            if isinstance(targets, (list, tuple, set, frozenset)):
                pairs.extend((name, target) for target in targets)
            else:
                pairs.append((name, targets))
    elif isinstance(aliases, (list, tuple, set, frozenset)):
        pairs.extend(aliases)
    else:
        raise TypeError("aliases must be a mapping or a sequence of pairs")
    normalized = []
    for pair in pairs:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise TypeError(f"alias entries must be two-item pairs, got {pair!r}")
        normalized.append((pair[0], pair[1]))
    return normalized


def _validate_case_buffers(case):
    """Validate the host-side storage contract declared by a case."""
    buffers = {**case.get("allocations", {}), **case.get("args", {})}
    layouts = case.get("buffer_layouts", {}) or {}
    if not isinstance(layouts, dict):
        raise TypeError("buffer_layouts must be a mapping")
    for name, layout in layouts.items():
        if name not in buffers:
            raise AssertionError(f"buffer_layouts names unknown buffer {name!r}")
        array = buffers[name]
        if not isinstance(array, np.ndarray):
            raise AssertionError(f"buffer_layouts[{name!r}] requires a NumPy ndarray")
        if not isinstance(layout, dict):
            raise TypeError(f"buffer_layouts[{name!r}] must be a mapping")
        if "shape" in layout and tuple(int(value) for value in layout["shape"]) != array.shape:
            raise AssertionError(
                f"{name}: declared shape {tuple(layout['shape'])} does not match {array.shape}"
            )
        if "strides" in layout:
            itemsize = int(array.dtype.itemsize)
            if itemsize <= 0 or any(int(stride) % itemsize for stride in array.strides):
                raise AssertionError(f"{name}: strides are not representable in elements")
            actual = tuple(int(stride) // itemsize for stride in array.strides)
            declared = tuple(int(value) for value in layout["strides"])
            if declared != actual:
                raise AssertionError(f"{name}: declared strides {declared} do not match {actual}")

    aliases = case.get("aliases", {}) or {}
    pairs = _alias_pairs(aliases)
    for left, right in pairs:
        # Corpus cases may use a descriptive value such as ``input-output``
        # to document in-place mutation.  It is not the name of a second
        # buffer, so there is no storage pair for the runner to validate.
        if (right not in buffers and isinstance(right, str)
                and right in {"input-output", "input", "output", "in-place", "inplace"}):
            continue
        if left not in buffers or right not in buffers:
            raise AssertionError(f"alias references unknown buffers {left!r}, {right!r}")
        first, second = buffers[left], buffers[right]
        if not isinstance(first, np.ndarray) or not isinstance(second, np.ndarray):
            raise AssertionError("aliased buffers must be NumPy ndarrays")
        shares = np.shares_memory(first, second)
        # NumPy cannot prove sharing for some empty views because there are no
        # addressed elements.  Same-pointer empty views are still a valid
        # declaration and need no special device allocation.
        if not shares and first.size == 0 and second.size == 0:
            shares = first.ctypes.data == second.ctypes.data
        if not shares:
            raise AssertionError(f"declared aliased buffers {left!r} and {right!r} do not share storage")


# ----------------------------------------------------------- chunked compare
def _allclose_pass(output, reference, rtol, atol, equal_nan, name):
    """One data pass: allclose verdict + the old error metric.

    ``np.isclose`` is exactly what ``np.testing.assert_allclose`` evaluates,
    so verdicts are identical; chunking only bounds the temporaries.
    """
    flat_output = output.reshape(-1)
    flat_reference = reference.reshape(-1)
    total = flat_output.size
    violations = []
    max_error = 0.0
    for start in range(0, total, _CHUNK):
        a = flat_output[start:start + _CHUNK]
        b = flat_reference[start:start + _CHUNK]
        close = np.isclose(a, b, rtol=rtol, atol=atol, equal_nan=equal_nan)
        if not close.all():
            bad = np.flatnonzero(~close)
            violations.extend(int(index) + start for index in bad[:_MAX_REPORT])
            # keep scanning: max_abs_error still needs the full sweep
        with np.errstate(invalid="ignore", over="ignore"):
            delta = np.abs(a.astype(np.float64) - b.astype(np.float64))
            equal = a == b
            if equal_nan:
                equal = equal | (np.isnan(a) & np.isnan(b))
            error = float(np.where(equal, 0.0, delta).max(initial=0.0))
        if error > max_error:
            max_error = error
    if violations:
        first = violations[0]
        raise AssertionError(
            f"{name}: not close to tolerance rtol={rtol:g}, atol={atol:g}; "
            f"first bad flat indices {violations[:_MAX_REPORT]}, e.g. "
            f"output={flat_output[first]!r} vs reference={flat_reference[first]!r}")
    return max_error


# ---------------------------------------------------------------- main entry
def compare_case(case, actual, expected=None, *, rtol=None, atol=None):
    """Validate output contracts and apply per-output NumPy comparison
    policies.  Same contract and verdicts as ``runner.compare``."""
    _validate_case_buffers(case)
    expected = case["expected"] if expected is None else expected
    if set(expected) != set(case["outputs"]):
        raise AssertionError("Oracle output names do not match case outputs")
    if set(actual) != set(expected):
        raise AssertionError(f"output names differ: {set(actual)} != {set(expected)}")
    # If an alias declaration covers two returned outputs, retain that
    # observable part of the storage contract.
    for left, right in _alias_pairs(case.get("aliases", {}) or {}):
        if left not in actual or right not in actual:
            continue
        first, second = np.asarray(actual[left]), np.asarray(actual[right])
        if first.size == 0 and second.size == 0:
            # Empty outputs have no observable storage relationship.
            continue
        shares = np.shares_memory(first, second)
        if not shares:
            raise AssertionError(f"returned outputs {left!r} and {right!r} violate alias declaration")
    buffers = {**case.get("allocations", {}), **case["args"]}
    errors = {}
    for name, reference in expected.items():
        reference = np.asarray(reference)
        output = np.asarray(actual[name])
        storage = np.asarray(buffers[name])
        kind = str(case.get("pointer_dtypes", {}).get(name, storage.dtype)).rsplit(".", 1)[-1]
        expected_dtype = storage.dtype if kind == "bfloat16" else np.dtype(kind)
        if output.shape != storage.shape or output.dtype != expected_dtype:
            raise AssertionError(f"{name}: got {output.shape}/{output.dtype}, expected {storage.shape}/{expected_dtype}")
        if reference.shape != storage.shape:
            # A flat oracle represents the same complete row-major output buffer.
            if reference.size != storage.size or (reference.ndim != 1 and storage.ndim != 1):
                raise AssertionError(f"{name}: incompatible reference shape {reference.shape} for buffer {storage.shape}")
            reference = reference.reshape(storage.shape)
        policy = case["comparison"][name]
        if policy.get("comparator") == "quantized_interval":
            # Discontinuous rounding needs an input-derived interval, not a
            # blanket tolerance of one output bin. Away from a threshold the
            # independently computed bounds are identical and equality is exact.
            lower = np.asarray(policy["lower"], dtype=reference.dtype)
            upper = np.asarray(policy["upper"], dtype=reference.dtype)
            if lower.shape != reference.shape or upper.shape != reference.shape:
                raise AssertionError(f"{name}: quantization bounds must match the reference shape")
            finite = np.isfinite(reference)
            if (not np.isfinite(lower[finite]).all() or not np.isfinite(upper[finite]).all()
                    or np.any(lower[finite] > upper[finite])
                    or np.any(upper[finite] - lower[finite] > 1)
                    or np.any(reference[finite] < lower[finite])
                    or np.any(reference[finite] > upper[finite])
                    or np.any(lower[finite] != np.ceil(lower[finite]))
                    or np.any(upper[finite] != np.ceil(upper[finite]))):
                raise AssertionError(f"{name}: invalid quantization interval")
            good = finite & (output >= lower) & (output <= upper) & (output == np.ceil(output))
            good |= np.isnan(output) & np.isnan(reference)
            if not good.all():
                raise AssertionError(f"{name}: outside the independently computed quantization interval")
            errors[name] = float(np.max(np.abs(output[finite] - reference[finite]), initial=0))
            continue
        # bf16 lives on the host as uint16 bit patterns: decode both sides to
        # float32 before comparing, so a declared tolerance compares values,
        # not bits (the decode is injective, so an exact policy keeps its
        # meaning), and the integer-exactness rule below no longer mistakes
        # the bit storage for an integer output.
        semantic = str(case.get("pointer_dtypes", {}).get(
            name, case.get("dtype", storage.dtype))).rsplit(".", 1)[-1]
        if (semantic == "bfloat16" and output.dtype == np.dtype("uint16")
                and reference.dtype == np.dtype("uint16")):
            output = (output.astype(np.uint32) << np.uint32(16)).view(np.float32)
            reference = (reference.astype(np.uint32) << np.uint32(16)).view(np.float32)
        comparator = policy.get("comparator", "array_equal" if policy.get("exact") else "allclose")
        if comparator not in ("array_equal", "allclose", "allclose_sign_invariant"):
            raise ValueError(f"unsupported comparator: {comparator}")
        exact = comparator == "array_equal" or policy.get("exact", False) or output.dtype.kind in "biu"
        equal_nan = policy.get("equal_nan", False)
        compared_output, compared_reference = output, reference
        if comparator == "allclose_sign_invariant":
            if exact or output.dtype.kind in "biu":
                raise ValueError(f"{name}: sign-invariant comparison requires floating output")
            view_shape = tuple(int(value) for value in policy.get("shape", ()))
            axis = int(policy.get("axis", -1))
            if not view_shape or np.prod(view_shape, dtype=np.int64) != output.size:
                raise ValueError(f"{name}: sign-invariant shape must cover the complete output")
            if axis < 0:
                axis += len(view_shape)
            if axis < 0 or axis >= len(view_shape):
                raise ValueError(f"{name}: sign-invariant axis is out of range")
            output_view = output.reshape(view_shape)
            reference_view = reference.reshape(view_shape)
            reduce_axes = tuple(int(index) for index in policy.get(
                "reduce_axes", tuple(index for index in range(len(view_shape)) if index != axis)))
            if any(index < 0 or index >= len(view_shape) for index in reduce_axes) or axis in reduce_axes:
                raise ValueError(f"{name}: invalid sign-invariant reduction axes")
            dot = np.sum(output_view * reference_view, axis=reduce_axes, keepdims=True)
            signs = np.where(dot < 0, -1.0, 1.0)
            compared_output = (output_view * signs).reshape(output.shape)
            compared_reference = reference_view.reshape(reference.shape)
        if exact:
            # Keep integer precision: never convert to float64 before equality.
            if output.dtype.kind in "biu":
                # Python int/float equality avoids NumPy promoting uint64 to float64.
                matches = np.array_equal(output.astype(object), np.asarray(reference).astype(object))
            else:
                matches = np.array_equal(output, reference, equal_nan=equal_nan)
            if not matches:
                raise AssertionError(f"{name}: exact comparison failed")
            # Every element is exactly equal, so the old error metric is 0.
            errors[name] = 0.0
        else:
            relative = policy["rtol"] if rtol is None else rtol
            absolute = policy["atol"] if atol is None else atol
            if not (np.isfinite(relative) and np.isfinite(absolute) and relative >= 0 and absolute >= 0):
                raise ValueError(f"{name}: tolerances must be finite and nonnegative")
            errors[name] = _allclose_pass(compared_output, compared_reference,
                                          relative, absolute, equal_nan, name)
    return {"status": "PASS", "max_abs_error": errors}


# ---------------------------------------------------------- device fast path
def _device_comparable(case, name, policy, expected):
    """A policy the generic device comparison can evaluate exactly."""
    if policy.get("comparator", "allclose") != "allclose" or policy.get("exact", False):
        return False
    value = expected.get(name)
    if not isinstance(value, np.ndarray) or value.dtype.kind != "f":
        return False
    semantic = str(case.get("pointer_dtypes", {}).get(
        name, case.get("dtype", value.dtype))).rsplit(".", 1)[-1]
    return semantic != "bfloat16"


def compare_case_on_device(staged, case, device, expected=None, *,
                           rtol=None, atol=None):
    """Compare a staged case's outputs on the device, when it supports that.

    Returns the ``{"status": "PASS", ...}`` record, or ``None`` when the
    device (or a policy) does not support on-device comparison and the
    caller should download and use ``compare_case``.  Only engages when the
    outcome is provably identical to the host path: plain float allclose
    policies, expected arrays already shaped like their storage buffers, no
    alias declarations (the host path validates those against the
    downloaded arrays).
    """
    if getattr(device, "compare", None) is None:
        return None
    expected = case["expected"] if expected is None else expected
    if set(expected) != set(case["outputs"]):
        raise AssertionError("Oracle output names do not match case outputs")
    if case.get("aliases"):
        return None
    buffers = {**case.get("allocations", {}), **case.get("args", {})}
    for name in case["outputs"]:
        policy = case["comparison"][name]
        if not _device_comparable(case, name, policy, expected):
            return None
        reference = np.asarray(expected[name])
        storage = np.asarray(buffers[name])
        if reference.shape != storage.shape or reference.dtype != storage.dtype:
            return None            # flat oracle / mixed dtype: host path
    errors = {}
    for name in case["outputs"]:
        policy = case["comparison"][name]
        relative = policy["rtol"] if rtol is None else rtol
        absolute = policy["atol"] if atol is None else atol
        if not (np.isfinite(relative) and np.isfinite(absolute)
                and relative >= 0 and absolute >= 0):
            raise ValueError(f"{name}: tolerances must be finite and nonnegative")
        result = device.compare(staged.buffer(name), expected[name],
                                {"rtol": relative, "atol": absolute,
                                 "equal_nan": policy.get("equal_nan", False)})
        if result is None:
            return None
        ok, error = result
        if not ok:
            raise AssertionError(
                f"{name}: device comparison failed (max_abs_error={error:.3e})")
        errors[name] = float(error)
    return {"status": "PASS", "max_abs_error": errors}
