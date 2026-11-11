#!/usr/bin/env python3
"""Source discovery and actual runtime-header cache invalidation witnesses."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap
ROOT = _bootstrap.bootstrap()

from a100c import driver


def check_revision_sources(temp):
    original = driver.ROOT
    package = temp / "a100c"
    affected = ("factory.py", "passes/cse.py", "passes/pipeline.py",
                "plan/tiles.py", "plan/stages.py", "runtime/a100rt.h")
    try:
        driver.ROOT = temp
        for name in affected:
            path = package / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("original\n")
        baseline = driver.compiler_revision()
        for name in affected:
            path = package / name
            path.write_text("modified\n")
            assert driver.compiler_revision() != baseline, name
            path.write_text("original\n")
            assert driver.compiler_revision() == baseline
        for name in ("cache/entry/generated.py", "tests/test_new.py",
                     "runtime/build/generated.py"):
            path = package / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("unrelated\n")
        assert driver.compiler_revision() == baseline
        path = package / "passes/new_transform.py"
        path.write_text("new production dependency\n")
        assert driver.compiler_revision() != baseline
    finally:
        driver.ROOT = original
    return {"previously_omitted_files_checked": list(affected),
            "new_module_changes_revision": True,
            "tests_and_generated_outputs_excluded": True}


def check_runtime_header(temp):
    build = _bootstrap.load_build_module()
    copied = temp / "runtime"
    shutil.copytree(ROOT / "a100c/runtime", copied,
                    ignore=shutil.ignore_patterns("build", "__pycache__"))
    build.RUNTIME_DIR = copied
    project = temp / "project"
    (project / "a100_support").mkdir(parents=True)
    lock = project / "a100_support/lock.json"
    shutil.copy2(ROOT / "a100_support/lock.json", lock)
    build.PROJECT_ROOT = project
    build.CFLAGS = tuple(str(copied) if x == str(ROOT / "a100c/runtime") else x
                         for x in build.CFLAGS)
    first = build.build_operator_stub(temp / "objects")
    first_exe = temp / "old_exec"
    shutil.copy2(first["executable"], first_exe)
    old_objects = [str(p) for p in first["runtime_objects"]]
    warm = build.build_operator_stub(temp / "objects")
    assert warm["compiled"] == 0 and warm["assembled"] == 0
    header = copied / "a100rt.h"
    header.write_text(header.read_text().replace(
        "#define A100RT_EXIT_USAGE 2", "#define A100RT_EXIT_USAGE 42"))
    changed = build.build_operator_stub(temp / "objects")
    assert changed["compiled"] == len(build.RUNTIME_SOURCES)
    assert old_objects != [str(p) for p in changed["runtime_objects"]]
    fresh = build.build_operator_stub(temp / "fresh-objects")
    assert changed["executable"].read_bytes() == fresh["executable"].read_bytes()
    command = [os.environ["A100_QEMU"], "-L", os.environ["A100_SYSROOT"],
               "-cpu", os.environ["A100_QEMU_CPU"]]
    exits = [subprocess.run([*command, str(path)], capture_output=True,
                           timeout=30).returncode
             for path in (first_exe, changed["executable"], fresh["executable"])]
    assert exits == [2, 42, 42], exits
    old_identity = build.build_identity()
    old_objects = [str(p) for p in changed["runtime_objects"]]
    lock.write_text(lock.read_text() + "\n")
    sdk_changed = build.build_operator_stub(temp / "objects")
    assert sdk_changed["compiled"] == len(build.RUNTIME_SOURCES)
    assert old_objects != [str(p) for p in sdk_changed["runtime_objects"]]
    assert build.build_identity() != old_identity
    original_identity = build.build_identity()
    build.LINKFLAGS = (*build.LINKFLAGS, "-Wl,--no-relax")
    assert build.build_identity() != original_identity
    return {"old_cached_changed_fresh_exit_codes": exits,
            "unchanged_compiles": warm["compiled"],
            "header_changed_compiles": changed["compiled"],
            "sdk_lock_changed_compiles": sdk_changed["compiled"],
            "cached_and_clean_new_elf_sha256": hashlib.sha256(
                changed["executable"].read_bytes()).hexdigest(),
            "link_flags_affect_build_identity": True}


def main():
    with tempfile.TemporaryDirectory(prefix="a100c-cache-deps-") as path:
        temp = Path(path)
        result = {"revision": check_revision_sources(temp / "revision"),
                  "runtime_header": check_runtime_header(temp / "native")}
    out = os.environ.get("A100C_CACHE_DEPENDENCY_EVIDENCE")
    if out:
        Path(out).write_text(json.dumps(result, indent=2))
    print("test_cache_dependencies: source discovery, native header mutation "
          "and build identity checks PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
