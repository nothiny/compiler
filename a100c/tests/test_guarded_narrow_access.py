#!/usr/bin/env python3
"""Native exact guard/fallback/default/poisoned-lane checks for narrow memory."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import sys
import tempfile
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap
ROOT = _bootstrap.bootstrap()
resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

import numpy as np
from a100c.driver import CompileOptions
from a100c.factory import FactoryCompiler
from a100c.lower import narrow_access
from a100_support.native_device import NativeExecutableDevice
from opslib.compare import compare_case


def check_declines_before_emission():
    from a100c.ir import mir, tir
    result_type = mir.VectorType(8, 1, "uint")
    signed_other = mir.VReg(mir.VectorType(8, 1, "int"))
    lowering = SimpleNamespace(
        options=SimpleNamespace(guarded_narrow_access=True), _vl=16,
        _vtype=lambda unused: result_type, _need=lambda *unused: signed_other)
    # ctx/base/offsets are deliberately unavailable: rejecting the typed
    # mismatch and volatile forms must not emit a guard or memory access.
    assert narrow_access.try_load(lowering, None, SimpleNamespace(attrs={}),
        None, None, None, None, object(), tir.MaskedDefault.VALUE,
        None, None, lambda: None) is None
    assert narrow_access.try_load(lowering, None,
        SimpleNamespace(attrs={"volatile": True}), None, None, None, None,
        None, tir.MaskedDefault.UNDEF, None, None, lambda: None) is None


def module_at(directory, store=False, unsigned=False, volatile=False):
    name = "probe_" + str(int(store)) + str(int(unsigned)) + str(int(volatile))
    source = directory / (name + ".py")
    expression = ("value=tl.load(data+i)\n    tl.store(output+index,value,mask=flag!=0)"
                  if store else "other=" + ("i.to(tl.int8)" if unsigned else
                    "(i.to(tl.float32)*0.25+0.5).to(tl.float16)") +
                    "\n    value=tl.load(data+index,mask=flag!=0,other=other,volatile=" +
                    str(volatile) + ")\n    tl.store(output+i,value)")
    source.write_text("""OPERATOR={'name':'narrow_guard_probe','group':'private','channel':'local','execution':'triton_kernel','verification':'correctness','tags':[]}
import triton
import triton.language as tl
@triton.jit
def probe(data,indices,active,output,B:tl.constexpr):
    i=tl.arange(0,B)
    index=tl.load(indices+i)
    flag=tl.load(active+i)
    """ + expression + """
def _make_case(shape=None,dtype='float16',seed=30):
    return {'grid':(1,)}
""")
    spec = importlib.util.spec_from_file_location(name, source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class WitnessCompiler(FactoryCompiler):
    def _identity(self, case):
        result = super()._identity(case)
        result["key"] = hashlib.sha256(
            (result["key"] + "test-only-guard-disabled-witness").encode()).hexdigest()
        return result


def main():
    check_declines_before_emission()
    rows = []
    original_plan = narrow_access._Guard.plan
    def wrong_plan(self, *args):
        mask, bad, segments = original_plan(self, *args)
        from a100c.ir import mir
        return mask, self.ctx.const(0, mir.I64, self.loc), segments
    i = np.arange(32, dtype=np.int64)
    rng = np.random.default_rng(42)
    patterns = {"contiguous": i + 64, "segments": (i // 16) * 32 + i % 16,
                "reverse": 511 - i, "random": rng.permutation(480)[:32],
                "duplicates": (i // 16) * 32 + i % 4}
    with tempfile.TemporaryDirectory(prefix="a100c-narrow-guard-") as temp:
        directory = Path(temp)
        for store, unsigned, volatile in ((False, False, False),
                                           (True, False, False),
                                           (False, True, False),
                                           (False, False, True)):
            module = module_at(directory, store, unsigned, volatile)
            for mode in ("off", "on", "witness"):
                if mode == "witness" and (unsigned or volatile):
                    continue
                narrow_access._Guard.plan = wrong_plan if mode == "witness" else original_plan
                compiler_type = WitnessCompiler if mode == "witness" else FactoryCompiler
                compiler = compiler_type(options=CompileOptions(
                    cache_dir=str(directory / mode), guarded_narrow_access=mode != "off"))
                for name, index_values in patterns.items():
                    if (unsigned or volatile) and name not in ("contiguous", "random"):
                        continue
                    for mask_name, active in (("all", np.ones(32, np.int32)),
                            ("none", np.zeros(32, np.int32)),
                            ("alternating", (i % 2 == 0).astype(np.int32)),
                            ("first-inactive", (i % 2 == 1).astype(np.int32))):
                        indices = index_values.copy()
                        indices[active == 0] = np.where(i[active == 0] % 2, 2**40, -2**40)
                        dtype = np.uint8 if unsigned else np.float16
                        data = np.full(32 if store else 512, 1.25, dtype=dtype) if store \
                            else np.arange(512, dtype=dtype)
                        output = np.full(512 if store else 32, 13, dtype=dtype)
                        if store:
                            expected = output.copy()
                            expected[indices[active != 0]] = data[active != 0]
                        else:
                            expected = i.astype(np.int8).astype(np.uint8) if unsigned else \
                                (i.astype(np.float32) * .25 + .5).astype(np.float16)
                            expected[active != 0] = data[indices[active != 0]]
                        case = {"kernel": module.probe,
                            "args": {"data": data, "indices": indices,
                                     "active": active, "output": output},
                            "meta": {"B": 32}, "grid": (1,), "outputs": ("output",),
                            "expected": {"output": expected},
                            "comparison": {"output": {"comparator": "array_equal", "exact": True}}}
                        try:
                            staged = NativeExecutableDevice(compiler, 1).stage_case(case)
                            staged.artifact.arguments = (*staged.artifact.arguments, "--repeats", "3")
                            staged.launch()
                            verdict = compare_case(case, staged.outputs())
                            passed = verdict["status"] == "PASS" and \
                                staged.outputs()["output"].tobytes() == expected.tobytes()
                            row = {"mode": mode, "store": store, "unsigned": unsigned,
                                   "volatile": volatile, "pattern": name, "mask": mask_name,
                                   "passed": passed, "artifact_sha256": staged.artifact_sha256}
                        except Exception as exc:
                            row = {"mode": mode, "store": store, "unsigned": unsigned,
                                   "volatile": volatile, "pattern": name, "mask": mask_name,
                                   "passed": False, "error": repr(exc)}
                        rows.append(row)
                        print(json.dumps(row), flush=True)
                        if mode != "witness":
                            assert row["passed"], row
        narrow_access._Guard.plan = original_plan
    summary = {"rows": rows, "normal_checks": sum(x["mode"] != "witness" for x in rows),
               "all_normal_pass": all(x["passed"] for x in rows if x["mode"] != "witness"),
               "witness_fails_load_and_store": all(any(not x["passed"] for x in rows
                    if x["mode"] == "witness" and x["store"] == store) for store in (False, True)),
               "scope": "additional semantic probes, not original corpus coverage"}
    assert summary["witness_fails_load_and_store"]
    out = os.environ.get("A100C_NARROW_GUARD_EVIDENCE")
    if out:
        Path(out).write_text(json.dumps(summary, indent=2))
    print("test_guarded_narrow_access: normal exact cases PASS; both guard-removal witnesses fail")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
