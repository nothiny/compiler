"""Shared bootstrap for a100c tests.

The tests are plain executables (python3 a100c/tests/test_<name>.py): the host
python has no pytest and none is needed.  This module puts the repository root
and the declared PYTHONPATH entries on sys.path and loads the project .env
(without overriding an already-exported environment), so the tests run the same
way with or without `set -a; . ./.env; set +a` in front.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def bootstrap() -> Path:
    # .env is the single source of truth for installed tool paths (F001);
    # values already exported by the caller win.
    env_path = ROOT / ".env"
    if env_path.is_file():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key, value.strip())
    # Import paths: the declared PYTHONPATH entries plus the repository root.
    for entry in os.environ.get("PYTHONPATH", "").split(os.pathsep):
        if entry and entry not in sys.path:
            sys.path.insert(0, entry)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    return ROOT


def load_build_module():
    """Import a100c/runtime/build.py without requiring a package __init__."""
    import importlib.util

    path = ROOT / "a100c" / "runtime" / "build.py"
    spec = importlib.util.spec_from_file_location("a100c_runtime_build", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
