"""Golden cache: hit/miss, invalidation on file change, concurrency, fidelity."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HARNESS = Path(__file__).resolve().parents[1]     # <root>/harness
ROOT = HARNESS.parent                               # the corpus root
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from opslib import runner  # noqa: E402
from opslib import golden  # noqa: E402

ADD = ROOT / "suite" / "dev" / "softsign_kernel.py"
GELU = ROOT / "suite" / "dev" / "gelu_min.py"              # oracle through mathref.erf
CUMSUM = ROOT / "suite" / "perf" / "swiglu_fwd.py"          # callable grid


def _cases_equal(left, right):
    assert set(left) == set(right)
    for key, value in left.items():
        if key == "kernel":
            assert golden._kernel_name(value) == golden._kernel_name(right[key])
            continue
        mine = value
        theirs = right[key]
        if isinstance(mine, dict) and isinstance(theirs, dict):
            assert set(mine) == set(theirs), key
            for name in mine:
                a, b = mine[name], theirs[name]
                if isinstance(a, np.ndarray):
                    assert b.dtype == a.dtype and b.shape == a.shape, (key, name)
                    assert np.array_equal(a, b, equal_nan=True), (key, name)
                else:
                    assert (a == b) or (a != a and b != b), (key, name)
        elif isinstance(mine, tuple) and isinstance(theirs, (tuple, list)):
            assert list(mine) == list(theirs), key
        else:
            assert mine == theirs or (mine != mine and theirs != theirs), key


def test_miss_then_hit_roundtrip(tmp_path):
    op = runner.load_operator(ADD)
    stats = {}
    fresh = golden.load_or_build(op, ADD, shape=(4097,), dtype="float32",
                                 seed=30, cache=tmp_path, stats=stats)
    assert stats == {"miss": 1}
    _cases_equal(fresh, op.make_case(shape=(4097,), dtype="float32", seed=30))

    stats = {}
    cached = golden.load_or_build(op, ADD, shape=(4097,), dtype="float32",
                                  seed=30, cache=tmp_path, stats=stats)
    assert stats == {"hit": 1}
    _cases_equal(cached, fresh)

    # different seed/shape/dtype are different entries
    stats = {}
    golden.load_or_build(op, ADD, shape=(4097,), dtype="float16",
                         seed=30, cache=tmp_path, stats=stats)
    golden.load_or_build(op, ADD, shape=(1024,), dtype="float32",
                         seed=30, cache=tmp_path, stats=stats)
    golden.load_or_build(op, ADD, shape=(4097,), dtype="float32",
                         seed=31, cache=tmp_path, stats=stats)
    assert stats == {"miss": 3}


def test_zero_output_buffers_are_recreated_not_persisted(tmp_path):
    op = runner.load_operator(ADD)
    golden.load_or_build(op, ADD, shape=(128,), dtype="float32", seed=30,
                         cache=tmp_path)
    cached = golden.load_or_build(op, ADD, shape=(128,), dtype="float32",
                                  seed=30, cache=tmp_path)
    y = cached["args"]["out_ptr"]
    assert isinstance(y, np.ndarray) and not isinstance(y, np.memmap)
    assert not y.any() and y.dtype == np.float32
    # the entry directory holds only the input arrays + expected
    entry = next((tmp_path / golden.entry_key(ADD, (128,), "float32", 30)[:2])
                 .iterdir())
    names = {p.name for p in entry.iterdir()}
    assert "args.x_ptr.npy" in names and "args.out_ptr.npy" not in names


def test_file_change_invalidates(tmp_path):
    original = ADD.read_text()
    copy = tmp_path / "add_modified.py"
    try:
        # any byte-level change must produce a different cache key; a trailing
        # comment is semantics-preserving and survives operator rewrites
        copy.write_text(original + "\n# golden-invalidation probe\n")
        op_a = runner.load_operator(ADD)
        op_b = runner.load_operator(copy)
        stats = {}
        golden.load_or_build(op_a, ADD, shape=(128,), dtype="float32",
                             seed=30, cache=tmp_path, stats=stats)
        golden.load_or_build(op_b, copy, shape=(128,), dtype="float32",
                             seed=30, cache=tmp_path, stats=stats)
        assert stats["miss"] == 2          # different file bytes -> different keys
        stats = {}
        golden.load_or_build(op_a, ADD, shape=(128,), dtype="float32",
                             seed=30, cache=tmp_path, stats=stats)
        assert stats == {"hit": 1}
    finally:
        copy.unlink(missing_ok=True)


def test_callable_grid_is_not_cached(tmp_path):
    op = runner.load_operator(CUMSUM)
    assert callable(op.make_case()["grid"])
    stats = {}
    case = golden.load_or_build(op, CUMSUM, shape=None, dtype=None, seed=30,
                                cache=tmp_path, stats=stats)
    assert stats == {"skip": 1}
    assert callable(case["grid"])
    assert not list(tmp_path.rglob("meta.json"))


def test_use_cache_false_and_env_override(tmp_path, monkeypatch):
    op = runner.load_operator(ADD)
    stats = {}
    golden.load_or_build(op, ADD, shape=(128,), dtype="float32", seed=30,
                         cache=tmp_path, use_cache=False, stats=stats)
    assert stats == {"skip": 1}
    assert not list(tmp_path.rglob("meta.json"))
    monkeypatch.setenv("OPS_GOLDEN", "0")
    assert golden.cache_enabled() is False
    stats = {}
    golden.load_or_build(op, ADD, shape=(128,), dtype="float32", seed=30,
                         cache=tmp_path, stats=stats)
    assert stats == {"skip": 1}
    monkeypatch.delenv("OPS_GOLDEN")
    assert golden.cache_enabled() is True


def test_corrupt_entry_falls_back_to_make_case(tmp_path):
    op = runner.load_operator(ADD)
    golden.load_or_build(op, ADD, shape=(128,), dtype="float32", seed=30,
                         cache=tmp_path)
    entry = next((tmp_path / golden.entry_key(ADD, (128,), "float32", 30)[:2])
                 .iterdir())
    (entry / "meta.json").write_text("{ not json")
    stats = {}
    case = golden.load_or_build(op, ADD, shape=(128,), dtype="float32",
                                seed=30, cache=tmp_path, stats=stats)
    assert stats == {"miss": 1}            # rebuilt and overwritten
    assert isinstance(case["args"]["x_ptr"], np.ndarray)


def test_concurrent_writers_produce_one_valid_entry(tmp_path):
    script = f"""
import sys
sys.path.insert(0, {str(HARNESS)!r})
from opslib import runner
from opslib import golden
op = runner.load_operator({str(ADD)!r})
for _ in range(3):
    case = golden.load_or_build(op, {str(ADD)!r}, shape=(256,), dtype="float32",
                                seed=30, cache={str(tmp_path)!r})
    reference = op.make_case(shape=(256,), dtype="float32", seed=30)
    assert {{k: v for k, v in case.items() if k != "kernel"}}.keys() == \\
           {{k: v for k, v in reference.items() if k != "kernel"}}.keys()
    import numpy as np
    assert np.array_equal(case["args"]["x_ptr"], reference["args"]["x_ptr"])
    assert np.array_equal(case["expected"]["out_ptr"], reference["expected"]["out_ptr"])
"""
    processes = [subprocess.Popen([sys.executable, "-c", script],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  text=True)
                 for _ in range(4)]
    for process in processes:
        out, err = process.communicate(timeout=120)
        assert process.returncode == 0, err
    entries = list(tmp_path.rglob("meta.json"))
    assert len(entries) == 1               # exactly one entry, no temp leftovers
    assert not [p for p in tmp_path.rglob(".tmp-*")]


def test_prune_removes_changed_operators(tmp_path):
    op = runner.load_operator(ADD)
    golden.load_or_build(op, ADD, shape=(128,), dtype="float32", seed=30,
                         cache=tmp_path)
    # forge an entry whose operator sha matches nothing on disk
    digest = "ff" * 32
    directory = tmp_path / digest[:2] / digest
    directory.mkdir(parents=True)
    (directory / "meta.json").write_text(json.dumps(
        {"format": 1, "operator": "gone.py", "operator_sha256": "0" * 64}))
    (directory / "args.x.npy").write_bytes(b"")
    result = golden.prune(tmp_path)
    assert result["removed"] == 1 and result["kept"] == 1
    assert not directory.exists()
    kept = list(tmp_path.rglob("meta.json"))
    assert len(kept) == 1


def test_gelu_roundtrip_through_mathref(tmp_path):
    op = runner.load_operator(GELU)
    fresh = golden.load_or_build(op, GELU, shape=(1025,), dtype="float32",
                                 seed=20261008, cache=tmp_path)
    cached = golden.load_or_build(op, GELU, shape=(1025,), dtype="float32",
                                  seed=20261008, cache=tmp_path)
    np.testing.assert_array_equal(fresh["expected"]["y_ptr"],
                                  cached["expected"]["y_ptr"])


def test_memory_sharing_and_aliases_are_not_cached(tmp_path):
    """Aliased cases must never enter the cache: independent .npy files
    would read back as unrelated buffers and silently change semantics
    (writes through one name lost for the other)."""
    shared = np.zeros(8, dtype=np.float32)
    policy = {"comparator": "allclose", "exact": False, "rtol": 0, "atol": 0}

    def case_with(**extra):
        return {"args": {"x_ptr": shared, "b_ptr": shared, "n": 8},
                "meta": {}, "grid": (1,), "outputs": ("b_ptr",),
                "expected": {"b_ptr": shared + np.float32(1)},
                "comparison": {"b_ptr": policy}, "kernel": None, **extra}

    assert golden._payload_from_case(case_with()) is None          # shares
    split = {"args": {"x_ptr": np.zeros(8, np.float32),
                      "b_ptr": np.zeros(8, np.float32), "n": 8},
             "meta": {}, "grid": (1,), "outputs": ("b_ptr",),
             "expected": {"b_ptr": np.ones(8, np.float32)},
             "comparison": {"b_ptr": policy}, "kernel": None}
    assert golden._payload_from_case(split) is not None            # clean
    assert golden._payload_from_case({**split, "aliases": {"x_ptr": "b_ptr"}}) is None

    # end to end: an aliased case is rebuilt every time and keeps sharing
    class Probe:
        @staticmethod
        def make_case(shape=None, dtype=None, seed=None):
            return case_with()
    stats = {}
    first = golden.load_or_build(Probe, ADD, shape=(8,), dtype="float32",
                                 seed=1, cache=tmp_path, stats=stats)
    second = golden.load_or_build(Probe, ADD, shape=(8,), dtype="float32",
                                  seed=1, cache=tmp_path, stats=stats)
    assert stats["skip"] == 2 and "hit" not in stats and "miss" not in stats
    for case in (first, second):
        assert np.shares_memory(case["args"]["x_ptr"], case["args"]["b_ptr"])
    assert not list(tmp_path.rglob("meta.json"))
