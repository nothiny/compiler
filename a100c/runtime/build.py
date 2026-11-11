"""Build orchestration for the a100c native runtime and operator programs.

The reusable precompiled C runtime (bundle.c, pool.c, main.c) is compiled once
per content digest into a100c/runtime/build/ and linked with any operator
program object; a100c/runtime/operator_stub.S is the hand-written assembly
operator that proves the boundary today, and the emitter's output will take the
same route later.  Only the declared cross toolchain is invoked (F002/F003/
F004): cross gcc compiles C and links, cross as assembles; the declared sysroot
is passed explicitly on every gcc invocation.  Nothing from the unusable
SpacemiT LLVM package (F012/F044) and no host compiler appears on the build
path; the built executable neither starts, embeds nor calls Python (F043).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = RUNTIME_DIR.parents[1]

RUNTIME_SOURCES = ("bundle.c", "pool.c", "main.c")
OPERATOR_STUB = "operator_stub.S"

CFLAGS = ("-O2", "-Wall", "-Wextra", "-march=rv64gcv", "-mabi=lp64d", "-pthread",
          "-fno-ident", "-I", str(RUNTIME_DIR))
ASFLAGS = ("-march=rv64gcv",)
# -lm: the math-ops lane's elementwise transcendentals call the declared
# sysroot's libm (expf/logf/sinf/cosf/erff/floorf/ceilf and their double
# forms -- probed under the pinned QEMU endpoint, exit 0 with correct
# values); the runtime itself has no other libm dependency
LINKFLAGS = ("-march=rv64gcv", "-mabi=lp64d", "-pthread", "-Wl,--build-id=none",
             "-lm")

_TOOL_DIGESTS = {}


def _tool_digest(path: Path) -> str:
    """Content identity of a declared tool, memoized at its file identity."""
    path = path.resolve()
    stat = path.stat()
    key = (str(path), stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)
    if key not in _TOOL_DIGESTS:
        _TOOL_DIGESTS[key] = hashlib.sha256(path.read_bytes()).hexdigest()
    return _TOOL_DIGESTS[key]


def _sdk_lock_digest() -> str:
    lock = PROJECT_ROOT / "a100_support" / "lock.json"
    return hashlib.sha256(lock.read_bytes()).hexdigest() if lock.is_file() else ""


def build_identity() -> str:
    """Bound native build settings and the pinned SDK installation.

    The lock names the installed SDK archive. Its sysroot is assumed not
    externally modified; local compiler/runtime inputs are hashed by the
    driver and runtime-object cache independently.
    """
    tools = tool_paths()
    material = {
        "tools": {name: {"path": str(tools[name].resolve()),
                         "sha256": _tool_digest(tools[name])}
                  for name in ("gcc", "as", "ld")},
        "sysroot": str(tools["sysroot"]),
        "cflags": CFLAGS, "asflags": ASFLAGS, "linkflags": LINKFLAGS,
        "sdk_lock": _sdk_lock_digest(),
    }
    return hashlib.sha256(json.dumps(material, sort_keys=True).encode()).hexdigest()


def _project_env() -> dict:
    """Declared tool paths from the environment, falling back to .env."""
    env = {}
    env_path = PROJECT_ROOT / ".env"
    if env_path.is_file():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env.setdefault(key, value.strip())
    return env


def tool_paths() -> dict:
    declared = _project_env()

    def resolve(name, default=""):
        return Path(os.environ.get(name, declared.get(name, default)))

    prefix = resolve("A100_CROSS_PREFIX")
    sysroot = resolve("A100_SYSROOT")
    if not str(prefix) or not sysroot.is_dir():
        raise RuntimeError("A100_CROSS_PREFIX and A100_SYSROOT must be declared in .env")
    tools = {
        "gcc": Path(str(prefix) + "gcc"),
        "as": Path(str(prefix) + "as"),
        "ld": Path(str(prefix) + "ld"),
        "objdump": Path(str(prefix) + "objdump"),
        "sysroot": sysroot.resolve(),
    }
    missing = [name for name in ("gcc", "as", "ld", "objdump") if not tools[name].is_file()]
    if missing:
        raise RuntimeError(f"declared cross tools missing: {missing}")
    return tools


def _run(command) -> str:
    argv = [str(part) for part in command]
    result = subprocess.run(argv, capture_output=True, text=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(
            f"build command failed (exit {result.returncode}): {' '.join(argv)}\n"
            f"{result.stderr[-4000:]}")
    return result.stderr


def _digest(*parts: bytes) -> str:
    return hashlib.sha256(b"\0".join(parts)).hexdigest()[:16]


def default_build_dir() -> Path:
    return RUNTIME_DIR / "build"


def _runtime_header_identity() -> bytes:
    """The local runtime include closure, shared by all C object stamps.

    The runtime has a small common ABI header; hashing all local headers
    also covers future nested includes and newly added headers without a
    second hand-maintained dependency list. System headers/toolchain stay
    pinned by the declared tool installation and sysroot.
    """
    digest = hashlib.sha256()
    for path in sorted(RUNTIME_DIR.rglob("*.h")):
        if "build" in path.relative_to(RUNTIME_DIR).parts:
            continue
        digest.update(path.relative_to(RUNTIME_DIR).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.digest()


def runtime_objects(build_dir: Path | None = None):
    """Compile (or reuse) the precompiled runtime objects; returns
    (objects, tools, invocations, compiled_count)."""
    build_dir = Path(build_dir) if build_dir else default_build_dir()
    build_dir.mkdir(parents=True, exist_ok=True)
    tools = tool_paths()
    objects: list[Path] = []
    invocations = []
    compiled = 0
    headers = _runtime_header_identity()
    for name in RUNTIME_SOURCES:
        source = RUNTIME_DIR / name
        stamp = _digest(source.read_bytes(), headers, repr(CFLAGS).encode(),
                        str(tools["gcc"]).encode(),
                        _tool_digest(tools["gcc"]).encode(),
                        str(tools["sysroot"]).encode(),
                        _sdk_lock_digest().encode())
        obj = build_dir / f"{source.stem}-{stamp}.o"
        if not obj.is_file():
            command = [tools["gcc"], *CFLAGS, "--sysroot", tools["sysroot"],
                       "-c", source, "-o", obj]
            _run(command)
            invocations.append(command)
            compiled += 1
        objects.append(obj)
    return objects, tools, invocations, compiled


def assemble_operator(source: Path, build_dir: Path | None = None):
    """Assemble one operator program (.S) with the declared cross as.
    Returns (object, tools, assembled_count, invocations)."""
    build_dir = Path(build_dir) if build_dir else default_build_dir()
    build_dir.mkdir(parents=True, exist_ok=True)
    tools = tool_paths()
    stamp = _digest(Path(source).read_bytes(), repr(ASFLAGS).encode(),
                    str(tools["as"]).encode(), _tool_digest(tools["as"]).encode())
    obj = build_dir / f"{Path(source).stem}-{stamp}.o"
    assembled = 0
    invocations = []
    if not obj.is_file():
        command = [tools["as"], *ASFLAGS, source, "-o", obj]
        _run(command)
        invocations.append(command)
        assembled = 1
    return obj, tools, assembled, invocations


def link_operator(operator_objects, out: Path, build_dir: Path | None = None,
                  extra_invocations=()):
    """Link operator program objects with the precompiled runtime into a
    standalone ELF64 RISC-V executable (declared cross gcc + sysroot)."""
    build_dir = Path(build_dir) if build_dir else default_build_dir()
    objects, tools, invocations, compiled = runtime_objects(build_dir)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    command = [tools["gcc"], *LINKFLAGS, "--sysroot", tools["sysroot"],
               *[Path(o) for o in operator_objects], *objects, "-o", out]
    _run(command)
    invocations = [*extra_invocations, *invocations, command]
    return {"executable": out, "runtime_objects": objects, "tools": tools,
            "invocations": invocations, "compiled": compiled}


def build_operator_stub(build_dir: Path | None = None):
    """Build the hand-written assembly operator stub against the runtime."""
    obj, tools, assembled, invocations = assemble_operator(RUNTIME_DIR / OPERATOR_STUB, build_dir)
    build_dir = Path(build_dir) if build_dir else default_build_dir()
    info = link_operator([obj], build_dir / "operator_exec", build_dir,
                         extra_invocations=invocations)
    info["operator_objects"] = [obj]
    info["assembled"] = assembled
    return info


def main() -> int:
    info = build_operator_stub()
    summary = {
        "executable": str(info["executable"]),
        "operator_objects": [str(p) for p in info["operator_objects"]],
        "runtime_objects": [str(p) for p in info["runtime_objects"]],
        "tools": {name: str(path) for name, path in info["tools"].items()},
        "invocations": [" ".join(str(part) for part in cmd) for cmd in info["invocations"]],
        "compiled": info["compiled"],
        "assembled": info["assembled"],
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
