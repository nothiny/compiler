#!/usr/bin/env python3
"""Executed full-register/state witnesses for backend spill emission.

The generated test programs compare all 128*LMUL bytes and both VL/VTYPE,
including AVL=0 and a live address scratch register. These are native ISA
regressions, separate from full corpus coverage.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap
ROOT = _bootstrap.bootstrap()

from a100c.backend import allocate, emit
from a100c.ir import mir
from a100c.target import DEFAULT_TARGET


def run_native(directory, name, body):
    source = directory / (name + ".S")
    obj = directory / (name + ".o")
    exe = directory / name
    source.write_text(body)
    prefix = os.environ["A100_CROSS_PREFIX"]
    commands = [
        [prefix + "as", "-march=rv64gcv", str(source), "-o", str(obj)],
        [prefix + "ld", "--no-relax", str(obj), "-o", str(exe)],
        [os.environ["A100_QEMU"], "-cpu", os.environ["A100_QEMU_CPU"],
         str(exe)],
    ]
    for command in commands[:2]:
        subprocess.run(command, check=True, capture_output=True, timeout=60)
    result = subprocess.run(commands[-1], capture_output=True, timeout=30)
    return {"name": name, "exit_code": result.returncode,
            "commands": commands,
            "artifact_sha256": hashlib.sha256(exe.read_bytes()).hexdigest()}


def spill_sequences(group):
    reg = mir.VReg(mir.VectorType(32, group, "int"), name="saved")
    module = mir.MModule("spill", "<native-probe>")
    allocation = allocate.Allocation(
        assignment={reg.rid: "v8", **{-(i + 1): name for i, name in
                    enumerate([f"t{n}" for n in range(7)]
                              + [f"a{n}" for n in range(1, 8)])}},
        slots=[4096, DEFAULT_TARGET.vlenb * group])
    emitter = emit._Emitter(module, {}, allocation, DEFAULT_TARGET, (0, 0), [])
    emitter._cur_region = (32, 1, None)  # Runtime AVL is deliberately unknown.
    attrs = {"slot": 1, "sew": 32, "lmul": group}
    emitter.emit_op(mir.MOp("vspill", [reg], [], attrs=attrs))
    store = "\n".join(emitter.lines)
    emitter.lines = []
    emitter.emit_op(mir.MOp("vreload", [], [reg], attrs=attrs))
    load = "\n".join(emitter.lines)
    assert emitter._cur_region == (32, 1, None)
    assert "vset" not in store + load
    assert f"vs{group}r.v" in store and f"vl{group}re8.v" in load
    return store, load, emitter.frame_bytes()


def spill_program(group, avl, store, load, frame):
    size = 128 * group
    pattern = ",".join(str((i * 37 + 11) % 256) for i in range(size))
    return f""".option norelax
.text
.globl _start
_start:
 li t2, {frame}
 sub sp, sp, t2
 la t0, input
 li t2, {size}
 vsetvli t3, t2, e8, m{group}, ta, ma
 vle8.v v8, (t0)
 li t2, {avl}
 vsetvli t3, t2, e64, m1, ta, ma
 csrr s0, vl
 csrr s1, vtype
 li t0, 1234567
{store}
 li t1, 1234567
 bne t0, t1, fail
 csrr t4, vl
 bne t4, s0, fail
 csrr t4, vtype
 bne t4, s1, fail
 li t2, {size}
 vsetvli t3, t2, e8, m{group}, ta, ma
 vmv.v.i v8, 0
 li t2, {avl}
 vsetvli t3, t2, e32, m1, ta, ma
 csrr s0, vl
 csrr s1, vtype
{load}
 li t1, 1234567
 bne t0, t1, fail
 csrr t4, vl
 bne t4, s0, fail
 csrr t4, vtype
 bne t4, s1, fail
 li t2, {size}
 vsetvli t3, t2, e8, m{group}, ta, ma
 la t1, restored
 vse8.v v8, (t1)
 la t0, input
 li t2, {size}
check:
 lbu t3, 0(t0)
 lbu t4, 0(t1)
 bne t3, t4, fail
 addi t0, t0, 1
 addi t1, t1, 1
 addi t2, t2, -1
 bnez t2, check
 li a0, 0
 j exit
fail:
 li a0, 1
exit:
 li a7, 93
 ecall
.data
.balign 16
input: .byte {pattern}
.bss
.balign 16
restored: .skip {size}
"""


def dynamic_avl_pressure():
    module = mir.MModule("pressure", "<native-probe>")
    fn = mir.MFunction("pressure", [])
    block = mir.Block("entry")
    fn.blocks.append(block)
    module.functions.append(fn)
    ptr = mir.VReg(mir.I64, name="base")
    avl = mir.VReg(mir.I32, name="runtime_avl")
    vl = mir.VReg(mir.I32, name="vl")
    block.ops.extend([
        mir.MOp("sconst", [], [ptr], attrs={"value": 4096}),
        mir.MOp("sload", [ptr], [avl],
                attrs={"width": 32, "ext": "sext", "offset": 0}),
        mir.MOp("vsetvli", [avl], [vl],
                attrs={"sew": 32, "lmul": 1, "policy": "ta,ma"}),
    ])
    regs = []
    for i in range(35):
        reg = mir.VReg(mir.VectorType(32, 1, "int"), name=f"p{i}")
        block.ops.append(mir.MOp("vid", [], [reg],
                                attrs={"sew": 32, "lmul": 1}))
        regs.append(reg)
    acc = regs[0]
    for reg in regs[1:]:
        result = mir.VReg(reg.type, name="sum")
        block.ops.append(mir.MOp("vbin", [acc, reg], [result],
                                attrs={"op": "add"}))
        acc = result
    block.ops.append(mir.MOp("ret", [], []))
    allocation = allocate.allocate(module, DEFAULT_TARGET)
    assert allocation.stats["spilled_values"] > 0
    assert not mir.verify_module(module), mir.verify_module(module)


def configuration_witness(directory, setter):
    lines = ["li t0, 16", "vsetvli t1, t0, e64, m1, ta,ma",
             *setter, "li t0, 16", "vsetvli t1, t0, e64, m1, ta,ma",
             "csrr t2, vtype", "li t3, 216", "bne t2, t3, fail"]
    rewritten = "\n".join(emit._peephole(lines))
    body = """.option norelax
.text
.globl _start
_start:
""" + rewritten + """
 li a0, 0
 j exit
fail:
 li a0, 1
exit:
 li a7, 93
 ecall
"""
    return run_native(directory, "state-" + setter[-1].split()[0], body)


def observable_vl_result(directory):
    lines = ["li t0, 16", "vsetvli t1, t0, e64, m1, ta,ma",
             "li t2, 77", "vsetvli t2, t0, e64, m1, ta,ma",
             "bne t2, t0, fail", "li t1, 99",
             "vsetvli t1, t0, e64, m1, ta,ma", "bne t1, t0, fail"]
    body = ".option norelax\n.text\n.globl _start\n_start:\n" + \
           "\n".join(emit._peephole(lines)) + """
 li a0, 0
 j exit
fail:
 li a0, 1
exit:
 li a7, 93
 ecall
"""
    return run_native(directory, "observable-vl-result", body)


def main():
    rows = []
    out = os.environ.get("A100C_BACKEND_EVIDENCE")
    with tempfile.TemporaryDirectory(prefix="a100c-whole-state-") as temp:
        directory = Path(out) if out else Path(temp)
        directory.mkdir(parents=True, exist_ok=True)
        for group in (1, 2, 4, 8):
            store, load, frame = spill_sequences(group)
            for avl in (0, 3, 13):
                rows.append(run_native(directory, f"m{group}-vl{avl}",
                    spill_program(group, avl, store, load, frame)))
        rows.append(configuration_witness(directory,
                    ["vsetivli t1, 16, e64, m2, ta,ma"]))
        rows.append(configuration_witness(directory,
                    ["li t2, 217", "vsetvl t1, t0, t2"]))
        rows.append(observable_vl_result(directory))
        dynamic_avl_pressure()
        summary = {"native_runs": rows, "dynamic_avl_pressure_allocates": True,
                   "all_pass": all(row["exit_code"] == 0 for row in rows)}
        if out:
            (directory / "summary.json").write_text(json.dumps(summary, indent=2))
        assert summary["all_pass"], rows
        print(f"test_backend_vector_state: {len(rows)} native checks PASS; "
              "runtime-AVL pressure allocates and verifies")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
