"""Focused regression checks for the shared runner contract."""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pytest

HARNESS = Path(__file__).resolve().parents[1]     # <root>/harness
ROOT = HARNESS.parent                               # the corpus root
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from opslib import runner  # noqa: E402


def _case(value: np.ndarray, *, metadata: dict | None = None) -> dict:
    return {
        "args": {"out": value},
        "outputs": ("out",),
        "expected": {"out": value.copy()},
        "comparison": {"out": {"comparator": "array_equal", "exact": True}},
        **(metadata or {}),
    }


def test_executor_device_is_optional_and_propagated():
    case = _case(np.arange(3, dtype=np.float32))
    seen = []

    def executor(current, *, device):
        seen.append(device)
        return {"out": current["args"]["out"].copy()}

    result = runner.test(None, case=case, executor=executor, device="cuda:3")
    assert result["status"] == "PASS"
    assert seen == ["cuda:3"]


def test_one_argument_executor_remains_compatible():
    case = _case(np.arange(2, dtype=np.float32))
    result = runner.test(None, case=case,
                         executor=lambda current: {"out": current["args"]["out"].copy()})
    assert result["status"] == "PASS"


def test_declared_layout_and_aliases_are_checked():
    backing = np.arange(5, dtype=np.float32)
    view = backing[1:]
    other = np.zeros_like(backing)
    case = _case(view, metadata={
        "allocations": {"backing": backing, "other": other},
        "aliases": {"view": "other"},
        "buffer_layouts": {
            "view": {"shape": view.shape, "strides": (1,)},
            "backing": {"shape": backing.shape, "strides": (1,)},
            "other": {"shape": other.shape, "strides": (1,)},
        },
    })
    case["args"] = {"view": view, "out": view}
    case["expected"] = {"out": view.copy()}
    bad_layout = dict(case)
    bad_layout["buffer_layouts"] = dict(case["buffer_layouts"])
    bad_layout["buffer_layouts"]["view"] = {"shape": (99,), "strides": (1,)}
    with pytest.raises(AssertionError, match="declared shape"):
        runner.compare(bad_layout, {"out": view.copy()})
    with pytest.raises(AssertionError, match="declared aliased buffers"):
        runner.compare(case, {"out": view.copy()})


def test_returned_output_aliases_are_checked_when_both_are_declared():
    shared = np.arange(3, dtype=np.float32)
    case = {
        "args": {"left": shared, "right": shared},
        "outputs": ("left", "right"),
        "expected": {"left": shared.copy(), "right": shared.copy()},
        "comparison": {
            "left": {"comparator": "array_equal", "exact": True},
            "right": {"comparator": "array_equal", "exact": True},
        },
        "aliases": {"left": "right"},
    }
    with pytest.raises(AssertionError, match="returned outputs"):
        runner.compare(case, {"left": shared.copy(), "right": shared.copy()})


def test_sign_invariant_comparison_handles_svd_vector_signs():
    expected = np.asarray([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    actual = expected.copy()
    actual[:, 1] *= -1
    case = {
        "args": {"u": expected.reshape(-1)},
        "outputs": ("u",),
        "expected": {"u": expected.reshape(-1)},
        "comparison": {"u": {
            "comparator": "allclose_sign_invariant", "shape": (1, 2, 2),
            "axis": 2, "reduce_axes": (1,), "rtol": 0.0, "atol": 0.0,
        }},
    }
    assert runner.compare(case, {"u": actual.reshape(-1)})["status"] == "PASS"


@pytest.mark.skipif(
    not __import__("torch").cuda.is_available(), reason="requires a CUDA GPU"
)
def test_normalized_g_operator_uses_the_same_runner_contract():
    op = runner.load_operator(ROOT / "suite/dev/softsign_kernel.py")
    result = runner.test(op, shape=(1024,), dtype="float32", seed=7)
    assert result["status"] == "PASS"


# --------------------------------------------------------------- aliasing
try:
    import triton
    import triton.language as tl

    @triton.jit
    def _bump_kernel(a_ptr, b_ptr, n, BLOCK: tl.constexpr):
        off = tl.program_id(0) * BLOCK + tl.arange(0, BLOCK)
        m = off < n
        tl.store(b_ptr + off, tl.load(b_ptr + off, mask=m) + 1.0, mask=m)

    _HAVE_TRITON = True
except ImportError:  # pragma: no cover
    _HAVE_TRITON = False


class _AliasProbe:
    """Two argument names over ONE host storage: a write through b_ptr
    must be observable through a_ptr on the device, exactly as on host."""

    @staticmethod
    def make_case(n=64, seed=3):
        rng = np.random.default_rng(seed)
        shared = rng.standard_normal(n).astype(np.float32)
        args = {"a_ptr": shared, "b_ptr": shared, "n": n}
        return {
            "args": args, "meta": {"BLOCK": 64}, "grid": (1,),
            "outputs": ("a_ptr",),
            "expected": {"a_ptr": shared + np.float32(1.0)},
            "comparison": {"a_ptr": {"comparator": "allclose", "exact": False,
                                     "rtol": 0.0, "atol": 0.0}},
            "kernel": _bump_kernel,
        }

    @staticmethod
    def ref(args, meta):
        return {"a_ptr": args["a_ptr"] + np.float32(1.0)}


@pytest.mark.skipif(not _HAVE_TRITON or not __import__("torch").cuda.is_available(),
                    reason="requires triton and a CUDA GPU")
def test_aliased_host_buffers_share_one_device_allocation():
    """Regression: stage_case must not split host-aliased arrays into
    unrelated device buffers (writes through one name silently lost)."""
    case = _AliasProbe.make_case()
    result = runner.test(_AliasProbe, case=case, device="cuda")
    assert result["status"] == "PASS"
    assert result["max_abs_error"]["a_ptr"] == 0.0


@pytest.mark.skipif(not _HAVE_TRITON or not __import__("torch").cuda.is_available(),
                    reason="requires triton and a CUDA GPU")
def test_device_without_aliased_upload_fails_loudly():
    from opslib.device import stage_case
    from opslib.devices.cuda import CudaDevice
    case = _AliasProbe.make_case()
    with pytest.raises(RuntimeError, match="aliased host buffers"):
        stage_case(case, CudaDevice())


@pytest.mark.skipif(__import__("torch").cuda.device_count() < 2,
                    reason="needs a second CUDA device")
def test_runner_test_on_secondary_cuda_device():
    """runner.test(device="cuda:1") must execute on *that* device (launch,
    sync and read-back), not silently fall back to the current one."""
    op = runner.load_operator(ROOT / "suite" / "dev" / "softsign_kernel.py")
    result = runner.test(op, shape=(1024,), dtype="float32", seed=7,
                         device="cuda:1")
    assert result["status"] == "PASS"


def test_runner_pins_fp32_dot_to_ieee():
    """fp32 dot is IEEE by definition of the subset (principle 2)."""
    import os
    import subprocess
    import sys

    env = dict(os.environ, PYTHONPATH=str(HARNESS))
    env.pop("TRITON_F32_DEFAULT", None)
    code = "import opslib.device, os; print(os.environ.get('TRITON_F32_DEFAULT'))"
    got = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), env=env,
                         capture_output=True, text=True, timeout=120)
    assert got.returncode == 0, got.stdout + got.stderr
    assert got.stdout.strip() == "ieee"
    env["TRITON_F32_DEFAULT"] = "tf32"
    got = subprocess.run([sys.executable, "-c", code], cwd=str(ROOT), env=env,
                         capture_output=True, text=True, timeout=120)
    assert got.stdout.strip() == "tf32", "an explicit caller setting must win"
