"""opslib.catalog: the operator index (explicit metadata, O(1) lookup)."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1]     # <root>/harness
ROOT = HARNESS.parent                               # the corpus root
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from opslib import catalog  # noqa: E402


def test_every_operator_file_declares_literal_metadata():
    index = catalog.load_index()
    index = catalog.load_index()
    import os
    expected = len([f for g in ("suite/dev", "suite/perf")
                      for f in (ROOT / g).glob("*.py")
      if f.name not in {"case_utils.py", "mathref.py", "operator_catalog.py",
                        "operator_entry.py", "runner.py", "run.py", "validate.py"}
      and ("def make_case" in f.read_text() or "def _make_case" in f.read_text())])
    assert len(index["operators"]) == expected
    for item in index["operators"]:
        assert item["channel"] in {"local", "T", "G"}, item["source"]
        assert item["execution"] == "triton_kernel", item["source"]
        assert item["verification"] == "correctness", item["source"]
        assert item["kernel"], item["source"]
        assert isinstance(item["tags"], list), item["source"]


def test_channels_match_the_corpus_split():
    counts = {"local": 0, "T": 0, "G": 0}
    for item in catalog.entries():
        counts[item["channel"]] += 1
    entries = list(catalog.entries())
    assert sum(counts.values()) == len(entries)
    summary = catalog.summary()
    assert summary["baseline"] == 0 and summary["reference_only"] == 0
    assert summary["total"] == len(entries)


def test_find_resolves_every_alias_shape():
    by_source = {item["source"]: item for item in catalog.entries()}
    for source, item in list(by_source.items())[:50]:
        found = catalog.find(source)
        assert found["source"] == source
        assert catalog.find(Path(found["path"]))["source"] == source
        assert catalog.find(item["name"])["source"] == source
    perf = sorted((ROOT / "suite" / "perf").glob("*.py"))[0]
    assert catalog.find(f"suite/perf/{perf.name}")["source"] == f"suite/perf/{perf.name}"
    assert catalog.find(f"suite/perf/{perf.name}")["group"] == "suite/perf"
    with pytest.raises(FileNotFoundError):
        catalog.find("no/such/operator.py")


def test_find_is_fast_after_index_load():
    catalog.find("suite/dev/argmin_tiled_kernel.py")      # warm the index
    start = time.perf_counter()
    for _ in range(100):
        catalog.find("suite/dev/argmin_tiled_kernel.py")
    per_call = (time.perf_counter() - start) / 100
    assert per_call < 0.010, f"{per_call*1000:.2f} ms per find"


def test_catalog_json_regenerates_identically(tmp_path):
    """catalog.json is a generated artifact: a fresh scan must reproduce it."""
    result = subprocess.run(
        [sys.executable, "-m", "opslib", "catalog", "--check"],
        cwd=HARNESS, capture_output=True, text=True, timeout=300)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "up to date" in result.stdout


def test_index_rebuilds_when_a_file_changes(tmp_path):
    index = catalog.load_index()
    item = next(i for i in index["operators"] if i["source"].endswith("add.py"))
    path = ROOT / item["source"]
    original = path.read_text()
    try:
        path.write_text(original + "\n# touched\n")
        fresh = catalog._Catalog(ROOT)
        assert fresh.find(item["source"])["sha256"] != item["sha256"]
    finally:
        path.write_text(original)
    fresh = catalog._Catalog(ROOT)
    assert fresh.find(item["source"])["sha256"] == item["sha256"]


def test_manifest_regenerates_identically():
    """manifest.json is derived state: regenerating it must not drift.

    Gated behind OPS_TEST_MANIFEST=1 because it builds a case for every
    operator (a few minutes even with a warm golden cache).
    """
    if not Path(ROOT / "manifest.json").is_file():
        pytest.skip("manifest.json not committed")
    import os
    if os.environ.get("OPS_TEST_MANIFEST") != "1":
        pytest.skip("set OPS_TEST_MANIFEST=1 to run the manifest drift check")
    from compiler_api import manifest
    rebuilt = manifest.build("all")
    committed = json.loads((ROOT / "manifest.json").read_text())
    # 'module' is repository-relative, so the comparison is exact
    assert rebuilt == committed
