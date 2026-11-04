#!/usr/bin/env python3
"""test_build.py -- build-path acceptance for the a100c native runtime (T005).

Covers acceptance[3]: the runtime and the hand-written assembly stub are built
exclusively by the declared cross gcc/as/ld with the declared sysroot
(F002/F003/F004), no tool outside the declared build path appears (F044), and
the built executable contains no Python symbol or dependency (F043).  Also
checks the ELF identity, rebuild determinism and the precompiled-object reuse
of the runtime.

Run: python3 a100c/tests/test_build.py   (exit 0 = all checks PASS)
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()

FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}{(' | ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(name)
    return ok


def objdump(tool: Path, flags, target: Path) -> str:
    result = subprocess.run([str(tool), *flags, str(target)], capture_output=True,
                            text=True, timeout=300)
    if result.returncode != 0:
        raise RuntimeError(f"objdump failed: {result.stderr[-1000:]}")
    return result.stdout


def main() -> int:
    import shutil
    import tempfile

    build = _bootstrap.load_build_module()
    # Fresh build directory: the full build path is exercised (3 C compiles,
    # 1 assembly, 1 link), independent of any cached objects.
    fresh = Path(tempfile.mkdtemp(prefix="a100rt-build-test-"))
    try:
        return checks(build, fresh)
    finally:
        shutil.rmtree(fresh, ignore_errors=True)


def checks(build, fresh: Path) -> int:
    info = build.build_operator_stub(fresh / "build")
    exe = info["executable"]
    tools = info["tools"]

    check("executable-produced", exe.is_file(), str(exe))

    # ELF identity: ELF64, little-endian, RISC-V machine (the transport checks
    # exactly these bytes before executing an artifact).
    elf = exe.read_bytes()
    check("elf-identity",
          elf[:6] == b"\x7fELF\x02\x01" and elf[18:20] == b"\xf3\x00",
          f"{len(elf)} bytes")

    # Declared-tool-only build path: every invocation names a cross tool from
    # the declared toolchain directory (gcc/as/ld) and passes the declared
    # sysroot explicitly on every gcc call.
    tool_names = {"gcc", "as", "ld"}
    ok_tools = True
    details = []
    for command in info["invocations"]:
        argv = [str(part) for part in command]
        tool = Path(argv[0])
        if tool.parent != tools["gcc"].parent or tool.stem.rsplit("-", 1)[-1] not in tool_names:
            ok_tools = False
            details.append(argv[0])
        if tool.stem.endswith("gcc"):
            if "--sysroot" not in argv or argv[argv.index("--sysroot") + 1] != str(tools["sysroot"]):
                ok_tools = False
                details.append(f"sysroot missing in {argv[0]}")
    check("declared-cross-tools-only",
          ok_tools and len(info["invocations"]) >= 5,
          "; ".join(details) if details else f"{len(info['invocations'])} invocations")

    # No Python symbol in the static symbol table...
    symbols = objdump(tools["objdump"], ["-t"], exe)
    check("no-python-symbols", "python" not in symbols.lower(),
          f"{len(symbols.splitlines())} symbol lines")
    # ...and no Python dynamic dependency.
    dynamic = objdump(tools["objdump"], ["-p"], exe)
    needed = [parts[1] for parts in (line.split() for line in dynamic.splitlines())
              if parts and parts[0] == "NEEDED"]
    check("no-python-dependency",
          bool(needed) and not any("python" in name.lower() for name in needed),
          "NEEDED " + ",".join(needed))

    # Rebuild determinism: the project build directory (reusing the
    # precompiled runtime objects) must produce a byte-identical executable,
    # compiling and assembling nothing.
    project = build.build_operator_stub()
    check("rebuild-byte-identical",
          hashlib.sha256(exe.read_bytes()).hexdigest()
          == hashlib.sha256(project["executable"].read_bytes()).hexdigest(),
          str(project["executable"]))
    check("runtime-objects-reused",
          project["compiled"] == 0 and project["assembled"] == 0,
          f"compiled={project['compiled']} assembled={project['assembled']}")

    if FAILURES:
        print(f"test_build: {len(FAILURES)} check(s) FAILED: {FAILURES}")
        return 1
    print("test_build: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
