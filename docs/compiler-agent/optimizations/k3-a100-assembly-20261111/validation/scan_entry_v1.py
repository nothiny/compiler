#!/usr/bin/env python3
"""Run an unchanged frozen scan module with import-root assertions.

The logical runner argv is preserved in its own report. The sharding plan also
records this diagnostic launcher's actual argv and digest. Assertions change no
kernel, case, comparator, reference, emitted instruction or cache semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--binding", type=Path, required=True)
    parser.add_argument("runner_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    root = args.root.resolve()
    scan_path = root / "tools/run_scan.py"
    if scan_path.is_symlink() or scan_path.resolve().parent != root / "tools":
        raise SystemExit("The frozen scan runner must be a real copied file")
    sys.path[:0] = [str(root), str(root / "ops/harness"), str(root / "tools")]
    spec = importlib.util.spec_from_file_location("k3_bound_scan", scan_path)
    scan = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = scan
    spec.loader.exec_module(scan)
    if scan.ROOT.resolve() != root:
        raise SystemExit("Imported scan ROOT differs from the frozen root")
    observations = {}

    def check_imports():
        for name, module in list(sys.modules.items()):
            if not (name == "a100c" or name.startswith("a100c.")
                    or name == "a100_support" or name.startswith("a100_support.")):
                continue
            raw = getattr(module, "__file__", None)
            if raw is None:
                continue
            path = Path(raw).resolve()
            if not path.is_relative_to(root):
                raise RuntimeError(f"{name} imported outside frozen root: {path}")
            observations[name] = {"path": str(path),
                                  "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}

    check_imports()
    from a100c.factory import FactoryCompiler
    original = FactoryCompiler.compile_case

    def checked_compile(self, *positional, **keywords):
        result = original(self, *positional, **keywords)
        check_imports()  # Includes lazily imported lowering helpers.
        return result

    FactoryCompiler.compile_case = checked_compile
    runner_args = args.runner_args[1:] if args.runner_args[:1] == ["--"] else args.runner_args
    sys.argv = [str(scan_path), *runner_args]
    try:
        return scan.main()
    finally:
        FactoryCompiler.compile_case = original
        check_imports()
        args.binding.parent.mkdir(parents=True, exist_ok=True)
        args.binding.write_text(json.dumps({
            "root": str(root), "scan_file": str(scan_path),
            "scan_sha256": hashlib.sha256(scan_path.read_bytes()).hexdigest(),
            "assertions_passed": True, "observed_modules": observations,
            "logical_scan_argv": sys.argv,
            "diagnostic_note": "Unchanged runner main; read-only module-file assertions after compilation",
        }, indent=2) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
