#!/usr/bin/env python3
"""Both compile entry points forward switches and execute distinct artifacts."""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap
ROOT = _bootstrap.bootstrap()

from a100c import driver
from a100c.factory import FactoryCompiler
from a100c.lower import vectorize
from a100_support.native_device import NativeExecutableDevice
from opslib.compare import compare_case
from opslib.runner import load_operator


def main():
    fields = ("kept_axis_reduction", "neutral_reduction_trim", "matrix_row_reuse")
    env_names = ("A100C_KEPT_AXIS_REDUCTION", "A100C_NEUTRAL_REDUCTION_TRIM",
                 "A100C_MATRIX_ROW_REUSE")
    saved = {name: os.environ.pop(name, None) for name in env_names}
    original_lower = vectorize.lower_to_mir
    seen = []

    def lower(*args, **kwargs):
        options = args[5] if len(args) > 5 else kwargs["options"]
        seen.append(tuple(getattr(options, field) for field in fields))
        return original_lower(*args, **kwargs)

    vectorize.lower_to_mir = lower
    rows = []
    try:
        module = load_operator(ROOT / "ops/suite/dev/absolute_kernel.py")
        case = module.make_case(shape=[97], dtype="float32", seed=30)
        with tempfile.TemporaryDirectory(prefix="a100c-option-identity-") as temp:
            for cls in (driver.Compiler, FactoryCompiler):
                keys = []
                for disabled in (None, *fields):
                    options = driver.CompileOptions(cache_dir=temp,
                        **({disabled: False} if disabled else {}))
                    expected = tuple(field != disabled for field in fields)
                    compiler = cls(options=options)
                    for threads in (1, 8):
                        staged = NativeExecutableDevice(compiler, threads).stage_case(case)
                        artifact = staged.artifact
                        staged.launch()
                        verdict = compare_case(case, staged.outputs())
                        assert verdict["status"] == "PASS", verdict
                        if threads == 1:
                            assert seen[-1] == expected, (seen[-1], expected)
                            keys.append(artifact.executable.parent.name)
                            header = (artifact.executable.parent / "program.S").read_text()
                            if disabled:
                                assert "no-" + disabled.replace("_", "-") in header
                        else:
                            assert artifact.cache_hit
                        rows.append({"entry": cls.__name__, "disabled": disabled,
                                     "threads": threads, "comparison": verdict,
                                     "specialization_identity": artifact.identity,
                                     "cache_key": artifact.executable.parent.name})
                assert len(set(keys)) == 4
            for field, env_name in zip(fields, env_names):
                os.environ[env_name] = "off"
                option = driver.CompileOptions()
                assert getattr(option, field) is False
                assert "no-" + field.replace("_", "-") in option.identity_part()
                del os.environ[env_name]
    finally:
        vectorize.lower_to_mir = original_lower
        for name, value in saved.items():
            if value is not None:
                os.environ[name] = value
    out = os.environ.get("A100C_OPTION_IDENTITY_EVIDENCE")
    if out:
        Path(out).write_text(json.dumps({"rows": rows, "all_pass": True}, indent=2))
    print("test_lowering_option_identity: 8 distinct compiled artifacts, "
          "16 native original comparisons, both entry points PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
