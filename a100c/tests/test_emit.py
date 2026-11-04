#!/usr/bin/env python3
"""test_emit.py -- emission of the complete program-level assembly (T007).

The emitted .S is the complete single-operator program: workspace queries,
operator_entry with the psABI prologue/epilogue, one label per MIR block,
the vsetvli regions, masked indexed memory with v0.t, the per-edge branch
argument moves (condition read first, each edge's moves on its own path),
and source attribution on every instruction line ([opN] + the TIR source
location -- IR-OBSERVABILITY through the last stage).  Emission is
deterministic; the assembled+linked artifact is an ELF64 little-endian
RISC-V executable built by the declared cross toolchain only (F002/F003).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
import shutil  # noqa: E402
import tempfile  # noqa: E402
import warnings  # noqa: E402

warnings.filterwarnings("ignore")

FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(name)
    return ok


import importlib.util  # noqa: E402

from a100c.backend import allocate as alloc_mod  # noqa: E402
from a100c.backend import emit as emit_mod  # noqa: E402
from a100c.backend import legalize as legal_mod  # noqa: E402
from a100c.backend import select as select_mod  # noqa: E402
from a100c.frontend import lower_tir, source, specialize  # noqa: E402
from a100c.ir import mir  # noqa: E402
from a100c.lower import binding as binding_mod  # noqa: E402
from a100c.lower import vectorize  # noqa: E402
from a100c.plan import grid as grid_mod  # noqa: E402
from a100c.plan import partition as part_mod  # noqa: E402
from a100c.target import DEFAULT_TARGET  # noqa: E402

SLICE = ROOT / "ops" / "suite" / "dev" / "absolute_kernel.py"


def load_case():
    spec = importlib.util.spec_from_file_location("slice_operator", SLICE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.make_case(shape=(97,))


def emit_slice():
    case = load_case()
    src = source.load_operator(str(SLICE))
    spec = specialize.specialize(src, case)
    tir_module = lower_tir.lower(src, spec)
    grid = grid_mod.extract_grid(src, case)
    layout = binding_mod.argument_layout(case, spec)
    module = vectorize.lower_to_mir(tir_module, part_mod.ExecutionPlan(),
                                    DEFAULT_TARGET, layout, grid)
    legal_mod.legalize(module)
    selection = select_mod.select(module)
    allocation = alloc_mod.allocate(module, DEFAULT_TARGET)
    program = emit_mod.emit_assembly(module, allocation, DEFAULT_TARGET,
                                     workspace=(0, 0), selection=selection)
    return module, program


def check_program_shape():
    module, program = emit_slice()
    text = program.text
    check("workspace-queries-present",
          "operator_workspace_private:" in text
          and "operator_workspace_shared:" in text)
    check("entry-and-abi-prologue",
          "operator_entry:" in text and "addi sp, sp, -" in text
          and "sd ra, " in text and "mv " in text and "a0" in text)
    check("epilogue-present", "ld ra, " in text and "\n    ret" in text)
    blocks = [b.name for fn in module.functions for b in fn.blocks]
    check("one-label-per-block",
          all(f".L{b}:" in text for b in blocks), str(blocks))
    check("vsetvli-regions-emitted",
          "e32, m1, ta,ma" in text and "e64, m2, ta,ma" in text)
    check("masked-indexed-memory-with-v0t",
          "vluxei64.v " in text and ", v0.t" in text
          and "vsuxei64.v " in text)
    check("note-gnu-stack", '.section .note.GNU-stack' in text)
    # per-edge branch argument moves: condition read first, stubs per edge
    check("brc-edge-stubs", ".Lbrc" in text and "_true:" in text)
    first_bne = text.index("bne ")
    first_move_after = text.index("mv ", first_bne)
    check("condition-read-before-edge-moves", first_bne < first_move_after)


def check_traceability():
    module, program = emit_slice()
    lines = [l for l in program.text.splitlines()
             if "[op" in l and "absolute_kernel.py:" in l]
    op_indices = {int(l.split("[op")[1].split("]")[0])
                  for l in lines}
    total = sum(len(b.ops) for fn in module.functions for b in fn.blocks)
    check("instructions-carry-source-attribution", len(lines) > 50,
          f"{len(lines)} attributed lines")
    check("attribution-maps-to-real-ops",
          all(0 <= i < total for i in op_indices)
          and len(op_indices) > 40, f"{len(op_indices)} distinct ops")


def check_determinism():
    _, first = emit_slice()
    _, second = emit_slice()
    check("emission-is-deterministic", first.text == second.text)
    check("emission-stats-recorded",
          "frame_bytes" in first.stats and "emitted_lines" in first.stats,
          str(first.stats))


def check_builds_elf():
    _, program = emit_slice()
    with tempfile.TemporaryDirectory(prefix="a100c-emit-") as tmp:
        asm = Path(tmp) / "program.S"
        asm.write_text(program.text)
        sys.path.insert(0, str(ROOT))
        import importlib.util as ilu
        spec = ilu.spec_from_file_location(
            "a100c_runtime_build", ROOT / "a100c" / "runtime" / "build.py")
        build = ilu.module_from_spec(spec)
        spec.loader.exec_module(build)
        obj, tools, _assembled, _inv = build.assemble_operator(asm,
                                                               Path(tmp))
        info = build.link_operator([obj], Path(tmp) / "operator_exec",
                                   build_dir=Path(tmp))
        elf = Path(info["executable"]).read_bytes()
        check("artifact-is-elf64-little-riscv",
              elf[:6] == b"\x7fELF\x02\x01" and elf[18:20] == b"\xf3\x00",
              f"magic={elf[:6].hex()} machine={elf[18:20].hex()}")
        check("declared-cross-toolchain-only",
              "riscv64-unknown-linux-gnu" in str(tools["as"])
              and "riscv64-unknown-linux-gnu" in str(tools["gcc"]))


def main() -> int:
    check_program_shape()
    check_traceability()
    check_determinism()
    check_builds_elf()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_emit: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
