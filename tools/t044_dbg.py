#!/usr/bin/env python3
"""T044 debug: dump runtime state around one emitted x load.

Patches the emitted program.S of the probe kernel: after the base-pointer
load and after the x load itself, store the base register, the views
entries, the byte-offset vector and the loaded vector into the y output
buffer, then run and decode.  Diagnostic only.
"""
import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "ops" / "harness"), str(ROOT / "tools")):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np  # noqa: E402

import t044_probe_op as POP  # noqa: E402
from a100c.factory import FactoryCompiler  # noqa: E402
from a100c.driver import CompileOptions  # noqa: E402
from a100c.passes import pipeline as passes_mod  # noqa: E402
from a100_support.native_io import pack_case, unpack_outputs  # noqa: E402


def main() -> int:
    work = Path(tempfile.mkdtemp(prefix="a100c-t044-dbg-"))
    compiler = FactoryCompiler(
        options=CompileOptions(cache_dir=str(work / "cache")),
        pass_config=passes_mod.PassConfig())
    case = POP.probe_case(w_onehot_flat_index=0)
    cc = {k: v for k, v in case.items() if k != "expected"}
    artifact = compiler.compile_case(cc)
    entry = Path(artifact.executable).parent
    lines = (entry / "program.S").read_text().splitlines()

    site = None
    for i, l in enumerate(lines):
        if "vluxei64.v v4, (s8), v2, v0.t" in l and i > 4900:
            site = i
            break
    assert site, "x load site not found"
    ldline = None
    for k in range(site - 6, site):
        if "ld s8, 144(sp)" in lines[k]:
            ldline = k
    assert ldline is not None, "base load not found"

    out = []
    for i, l in enumerate(lines):
        out.append(l)
        if i == ldline:
            # t4/t5 are scratch here (dbg2/dbg3 clobbered them safely)
            out += ["ld t4, 120(sp)",
                    "ld t5, 112(t4)",
                    "sd s8, 1024(t5)",     # y word 256: the base register
                    "ld t4, 120(sp)",
                    "ld t4, 56(t4)",
                    "sd t4, 1032(t5)",     # y word 258: views[56]
                    "ld t4, 120(sp)",
                    "ld t4, 0(t4)",
                    "sd t4, 1040(t5)",     # y word 260: views[0]
                    ]
        if i == site - 1:
            # dump the byte-offset vector v2 (e64 m2 vl=32 state is active)
            out += ["ld t4, 120(sp)",
                    "ld t5, 112(t4)",
                    "vse64.v v2, (t5)"]    # y words 0..63: byte offsets
        if i == site:
            # dump the loaded vector v4 (e32 m1 vl=32 active at the load)
            out += ["ld t4, 120(sp)",
                    "ld t5, 112(t4)",
                    "addi t5, t5, 1056",
                    "vse32.v v4, (t5)"]    # y words 264..295: loaded values
    src = entry / "program_dbg.S"
    src.write_text("\n".join(out) + "\n")

    spec = importlib.util.spec_from_file_location(
        "a100c_runtime_build", ROOT / "a100c" / "runtime" / "build.py")
    bm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bm)
    obj, tools, assembled, invocations = bm.assemble_operator(
        src, build_dir=work / "build")
    bm.link_operator([obj], entry / "operator_exec_dbg",
                     build_dir=work / "build", extra_invocations=invocations)

    stage = Path(tempfile.mkdtemp(prefix="a100c-t044-dbgcase-"))
    pack_case(case, stage)
    qemu = os.environ["A100_QEMU"]
    cpu = os.environ["A100_QEMU_CPU"]
    sysroot = os.environ["A100_SYSROOT"]
    cmd = [qemu, "-L", sysroot, "-cpu", cpu,
           str(entry / "operator_exec_dbg"), "--bundle", str(stage / "bundle.bin"),
           "--threads", "1"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    print("exit:", r.returncode)
    if r.returncode:
        print(r.stderr[-500:])
        return 1
    y = np.asarray(unpack_outputs(stage)["y_ptr"]).reshape(-1)
    yi = y.view(np.int32)
    offs = y[:32].view(np.int64)
    print("byte offsets v2 (first 8):", offs[:8].tolist())
    print("element offsets (v2/4):", (offs[:8] // 4).tolist())
    base_reg = int(y[256:258].view(np.uint64)[0])
    views56 = int(y[258:260].view(np.uint64)[0])
    views0 = int(y[260:262].view(np.uint64)[0])
    print("base reg s8      =", hex(base_reg))
    print("views[56]        =", hex(views56))
    print("views[0]         =", hex(views0))
    loaded = y[264:276]
    print("loaded v4 (float):", [round(float(v), 3) for v in loaded[:8]])
    print("x ramp nearby: x[1661]=1662 ... (x[i]=i+1)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
