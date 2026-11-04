"""Fast case construction: ``fast_rng`` and the split oracle.

Both exist because building a benchmark-sized case (hundreds of MiB per
tensor) used to cost seconds of single-threaded numpy per entry -- far more
than running the kernel.  Their contracts:

* ``fast_rng(seed)`` gives *exactly* ``np.random.default_rng(seed)``'s values
  for draws below the parallel threshold (every correctness case), and for
  larger draws values that depend on the seed alone, not on the thread count;
* ``split_ref`` may only be used where it reproduces the whole-array oracle
  bit for bit, and ``split_ref_is_exact`` must say no for an oracle that
  reduces across rows.
"""
from __future__ import annotations

import os
import sys
import types
from pathlib import Path

import numpy as np
import pytest

HARNESS = Path(__file__).resolve().parents[1]     # <root>/harness
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from opslib import case as C  # noqa: E402

LARGE = C._PARALLEL_MIN * 2 + 12345


@pytest.mark.parametrize("seed", [0, 7, 30, 20261008])
def test_small_draws_match_default_rng_exactly(seed):
    plain, fast = np.random.default_rng(seed), C.fast_rng(seed)
    assert np.array_equal(plain.standard_normal((64, 1000)), fast.standard_normal((64, 1000)))
    assert np.array_equal(plain.normal(0, 0.5, (33, 65)), fast.normal(0, 0.5, (33, 65)))
    assert np.array_equal(plain.integers(-127, 128, (32, 32)), fast.integers(-127, 128, (32, 32)))
    assert np.array_equal(plain.uniform(-1, 1, 1000), fast.uniform(-1, 1, 1000))
    assert np.array_equal(plain.random(77, dtype=np.float32), fast.random(77, dtype=np.float32))
    assert np.array_equal(plain.permutation(50), fast.permutation(50))
    # the stream stays in step after a mix of draws
    assert np.array_equal(plain.standard_normal(10), fast.standard_normal(10))


def test_large_draws_depend_on_the_seed_not_the_thread_count(monkeypatch):
    monkeypatch.setenv("OPS_DATAGEN_THREADS", "1")
    one = C.fast_rng(3).standard_normal(LARGE, dtype=np.float32)
    monkeypatch.setenv("OPS_DATAGEN_THREADS", "5")
    five = C.fast_rng(3).standard_normal(LARGE, dtype=np.float32)
    assert np.array_equal(one, five)
    assert not np.array_equal(one, C.fast_rng(4).standard_normal(LARGE, dtype=np.float32))
    # a shaped request is the same stream, reshaped
    shaped = C.fast_rng(3).standard_normal((LARGE,), dtype=np.float32)
    assert np.array_equal(one, shaped)


def test_large_draws_have_the_requested_distribution():
    rng = C.fast_rng(11)
    x = rng.normal(2.0, 0.5, LARGE)
    assert abs(x.mean() - 2.0) < 1e-3 and abs(x.std() - 0.5) < 1e-3
    u = rng.uniform(-3.0, 1.0, LARGE)
    assert u.min() >= -3.0 and u.max() < 1.0 and abs(u.mean() + 1.0) < 1e-2
    k = rng.integers(0, 10, LARGE, dtype=np.int32)
    assert k.dtype == np.int32 and k.min() == 0 and k.max() == 9
    # a later draw on the same generator is deterministic too
    assert np.array_equal(C.fast_rng(11).normal(2.0, 0.5, LARGE), x)


def _module(ref, make_shape=(64, 32)):
    """A minimal operator module: ``make_case`` calls the module-level ``ref``."""
    module = types.ModuleType("fake_op")

    def make_case(shape=None, dtype=None, seed=None):
        rows, cols = shape or make_shape
        x = np.random.default_rng(seed).standard_normal((rows, cols))
        args = {"x_ptr": x, "y_ptr": np.zeros_like(x), "n_cols": cols}
        return {"args": args, "meta": {}, "expected": module.ref(args, {})}
    module.ref = ref
    module.make_case = make_case
    return module


def test_split_is_exact_for_a_row_independent_oracle():
    module = _module(lambda a, m: {"y_ptr": np.exp(a["x_ptr"]) * a["n_cols"]})
    assert C.split_ref_is_exact(module, (64, 32), "float32")
    whole = module.make_case((5000, 1000), seed=1)["expected"]["y_ptr"]
    parted = C.make_case_split(module, (5000, 1000), seed=1)["expected"]["y_ptr"]
    assert np.array_equal(whole, parted)
    assert module.ref.__name__ == "<lambda>"          # restored after the scope


def test_split_is_refused_for_an_oracle_that_reduces_across_rows():
    # counter-example: a column statistic depends on every row
    module = _module(lambda a, m: {"y_ptr": a["x_ptr"] - a["x_ptr"].mean(axis=0)})
    assert not C.split_ref_is_exact(module, (64, 32), "float32")
    # and one whose output is not row-aligned at all
    module = _module(lambda a, m: {"y_ptr": a["x_ptr"].sum(axis=0)})
    assert not C.split_ref_is_exact(module, (64, 32), "float32")


def test_operator_files_build_rng_through_fast_rng():
    root = HARNESS.parent
    offenders = [str(p.relative_to(root))
                 for g in ("suite/dev", "suite/perf")
                 for p in sorted((root / g).glob("*.py"))
                 if "np.random.default_rng(" in p.read_text()]
    assert not offenders, f"use case_utils.fast_rng instead: {offenders[:5]}"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
