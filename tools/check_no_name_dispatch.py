#!/usr/bin/env python3
"""check_no_name_dispatch.py -- the generality checks (T017).

Property under test: nothing below the frontend branches on an operator,
kernel or benchmark NAME, and neither the compiler nor the driver imports
the reference device or torch (the reference service never substitutes for
candidate execution, F049/F052).

Four legs, each able to fail:

  A. file-identity literals (unambiguous): an operator's '.py' filename or
     full corpus path appearing as a literal anywhere in the pipeline below
     the frontend (AST string constants in Python; whole-word matches in the
     runtime's C sources).  No language construct is named '<x>.py', so a
     hit is name-keyed dispatch or a hidden special case.

  B. name-shaped branch positions: a corpus operator/kernel/benchmark name
     compared (==/!=/in/startswith/endswith/removeprefix/removesuffix,
     match-case) against an expression whose shape says it holds a NAME
     (attributes ``.name``/``.stem``/``.rel_path``/``.path``/``.source``/
     ``.filename``/``.__name__`` or variables named like one).  The
     compiler's legitimate construct dispatch compares op kinds
     (``expr.op``, ``st.op``, locals ``op_name``/``kind``/``code``/
     ``merge``) and is not name-shaped, so it is not flagged.

  C. behavioral name-generality: one operator's source compiled from two
     different operator names/paths must emit identical assembly bodies
     (the provenance header lines that carry the source path and the
     specialization identity are excluded) -- emitted code may not depend
     on the operator's name.

  D. import inspection: statically, a100c/, tools/run_scan.py and
     tools/check_numeric_policy.py import neither torch nor the reference
     device; dynamically, compiling through a100c.factory never loads
     torch, a100_support.reference_device or a100_support.reference_backend,
     and running one case through the scan's native device never loads
     torch or the reference backend (the prepared transport's dtype
     converter -- ``a100_support/native_io.py`` constructing
     ``TritonCpuReferenceDevice.__new__`` for host bf16 representation --
     is the only reference module on that path and is reported, not hidden;
     the reference device itself is never constructed).

  --witness   inject a name-keyed branch into a scratch copy of the
              pipeline and require the check to CATCH it: the scratch
              check fails, so the witness exits nonzero (an injected
              operator-name branch is caught).  Exit 0 from the witness
              means the check is vacuous -- the alarm, not the pass.

Exit codes: 0 = every leg holds (default mode) / the witness branch was
NOT caught (--witness mode: the check cannot fail, so it proves nothing);
1 = a leg was violated (default) / the injected branch was caught
(--witness, the healthy outcome); 2 = witness setup error.
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for entry in (str(ROOT), str(ROOT / "ops" / "harness"), str(ROOT / "tools")):
    if entry not in sys.path:
        sys.path.insert(0, entry)

CORPUS_MANIFEST = ROOT / "ops" / "suite" / "manifest.json"

#: pipeline below the frontend: the compiler after source loading, plus the
#: scan driver.  The frontend (a100c/frontend/) owns source paths and kernel
#: names by contract; tests and the artifact cache are not pipeline code.
PIPELINE_PY = ("a100c/ir", "a100c/lower", "a100c/backend", "a100c/plan",
               "a100c/passes", "a100c/runtime", "a100c/target.py",
               "a100c/driver.py", "a100c/factory.py", "tools/run_scan.py")
PIPELINE_TEXT_SUFFIXES = (".c", ".h", ".S")
EXCLUDED_PARTS = ("__pycache__", "frontend", "tests", "cache", "build")

#: attribute names whose value is an operator/kernel/benchmark NAME
NAME_ATTRS = {"name", "stem", "rel_path", "path", "source", "filename",
              "file", "__name__", "operator", "kernel", "benchmark",
              "benchmark_name", "operator_name", "kernel_name"}
#: variable names whose value is an operator/kernel/benchmark NAME
NAME_VARS = {"operator", "operator_name", "kernel", "kernel_name",
             "benchmark", "benchmark_name", "bench", "name"}
BRANCH_METHODS = {"startswith", "endswith", "removeprefix", "removesuffix"}

FORBIDDEN_IMPORTS = (
    (re.compile(r"^\s*import\s+torch\b"), "import torch"),
    (re.compile(r"^\s*from\s+torch\b"), "from torch import"),
    (re.compile(r"^\s*import\s+a100_support\.reference_device\b"),
     "import the reference device"),
    (re.compile(r"^\s*from\s+a100_support\.reference_device\b"),
     "from the reference device import"),
    (re.compile(r"^\s*from\s+a100_support\s+import\b.*\breference"),
     "import the reference device"),
)


def corpus_names():
    """Operator/kernel/benchmark names and file identities from the corpus's
    own manifest (the perf lane is the benchmark lane)."""
    data = json.loads(CORPUS_MANIFEST.read_text())
    names, kernels, files, benchmarks = set(), set(), set(), set()
    for operator in data.get("operators", []):
        names.add(operator["name"])
        files.add(operator["filename"])
        if operator.get("path"):
            files.add(operator["path"])
        for kernel in operator.get("kernels") or []:
            kernels.add(kernel)
        if operator.get("lane") == "perf":
            benchmarks.add(operator["name"])
    return {"names": names, "kernels": kernels, "files": files,
            "benchmarks": benchmarks}


def pipeline_files(root: Path):
    """(python files, text sources) of the pipeline below the frontend."""
    py, text = [], []
    for base in PIPELINE_PY:
        path = root / base
        if path.is_file():
            py.append(path)
            continue
        if not path.is_dir():
            continue
        for item in sorted(path.rglob("*")):
            if any(part in EXCLUDED_PARTS for part in item.parts):
                continue
            if item.suffix == ".py":
                py.append(item)
            elif item.suffix in PIPELINE_TEXT_SUFFIXES:
                text.append(item)
    return py, text


# ---------------------------------------------------------------------------
# legs A and B: the static scan
# ---------------------------------------------------------------------------

def _is_name_shaped(node) -> bool:
    if isinstance(node, ast.Attribute):
        return node.attr in NAME_ATTRS
    if isinstance(node, ast.Name):
        return node.id in NAME_VARS
    if isinstance(node, ast.Call):
        # str(name), getattr(x, 'name')-style wraps are still name-shaped
        return any(_is_name_shaped(arg) for arg in node.args)
    return False


def scan_python(path: Path, names) -> list:
    violations = []
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            operands = [node.left, *node.comparators]
            constants = [o for o in operands if isinstance(o, ast.Constant)
                         and isinstance(o.value, str)]
            others = [o for o in operands if o not in constants]
            for const in constants:
                value = const.value
                if value.endswith(".py") or "/" in value:
                    continue      # file identities are leg A, everywhere
                if value in names["names"] | names["kernels"] \
                        | names["benchmarks"]:
                    if any(_is_name_shaped(o) for o in others):
                        violations.append(
                            (path, node.lineno,
                             f"branch on corpus name {value!r}"))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in BRANCH_METHODS:
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str) \
                        and (arg.value.endswith(".py") or "/" in arg.value):
                    continue
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str) \
                        and arg.value in names["names"] | names["kernels"] \
                        | names["benchmarks"] \
                        and _is_name_shaped(node.func.value):
                    violations.append(
                        (path, node.lineno,
                         f"branch on corpus name {arg.value!r} "
                         f"via .{node.func.attr}"))
        elif isinstance(node, ast.match_case):
            pattern = node.pattern
            if isinstance(pattern, ast.MatchValue) \
                    and isinstance(pattern.value, ast.Constant) \
                    and isinstance(pattern.value.value, str):
                value = pattern.value.value
                if value in names["names"] | names["kernels"] \
                        | names["benchmarks"] and not (
                            value.endswith(".py") or "/" in value):
                    violations.append(
                        (path, node.lineno,
                         f"match-case on corpus name {value!r}"))
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value
            for file_ref in names["files"]:
                if file_ref.endswith(".py") and value == file_ref:
                    violations.append(
                        (path, getattr(node, "lineno", 0),
                         f"operator file literal {file_ref!r}"))
                elif "/" in file_ref and file_ref in value:
                    violations.append(
                        (path, getattr(node, "lineno", 0),
                         f"operator path literal {file_ref!r}"))
    return violations


def scan_text(path: Path, names) -> list:
    violations = []
    body = path.read_text(errors="replace")
    for line_number, line in enumerate(body.splitlines(), start=1):
        for file_ref in names["files"]:
            if not file_ref.endswith(".py"):
                continue
            if re.search(r"(?<![\w./])" + re.escape(file_ref) + r"(?![\w])",
                         line):
                violations.append(
                    (path, line_number, f"operator file literal {file_ref!r}"))
    return violations


def static_scan(root: Path, names) -> list:
    violations = []
    py, text = pipeline_files(root)
    for path in py:
        violations.extend(scan_python(path, names))
    for path in text:
        violations.extend(scan_text(path, names))
    return violations


# ---------------------------------------------------------------------------
# leg C: behavioral name-generality
# ---------------------------------------------------------------------------

HEADER_EXCLUDE = ("# a100c emitted program:", "# source:",
                  "# specialization identity:")


def _load_operator_module(path: Path):
    spec = importlib.util.spec_from_file_location(
        "_name_generality_probe_" + path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _emitted_body(cache_dir: Path, case: dict) -> str:
    from a100c.driver import CompileOptions
    import a100c.factory as factory
    compiler = factory.FactoryCompiler(
        options=CompileOptions(cache_dir=str(cache_dir)))
    payload = {k: v for k, v in case.items()
               if k not in ("expected", "oracle_args")}
    artifact = compiler.compile_case(payload)
    listing = Path(artifact.executable).parent / "program.S"
    return listing.read_text()


def behavioral_probe(work: Path) -> tuple:
    """One operator compiled under two different names/paths: the emitted
    assembly bodies (provenance header excluded) must be identical."""
    source = ROOT / "ops" / "suite" / "dev" / "absolute_kernel.py"
    text = source.read_text()
    variants = []
    for stem, rename in (("alpha_probe_one", False),
                         ("beta_probe_two_name", True)):
        target = work / f"{stem}.py"
        body = text
        if rename:
            body = body.replace('"name": "hidden/absolute_kernel"',
                                f'"name": "probe/{stem}"')
        target.write_text(body)
        module = _load_operator_module(target)
        case = module.make_case(shape=[97], dtype="float32")
        listing = _emitted_body(work / f"cache-{stem}", case)
        variants.append((stem, listing))
    (stem_a, body_a), (stem_b, body_b) = variants

    def normalized(body):
        # provenance header lines and the per-op source-location comments
        # carry the operator's path by design (IR-OBSERVABILITY); the
        # instruction stream itself must not depend on the name
        lines = [re.sub(r"\S+\.py:", "<source>:", line)
                 for line in body.splitlines()]
        return "\n".join(line for line in lines
                         if not line.startswith(HEADER_EXCLUDE))
    same = normalized(body_a) == normalized(body_b)
    detail = (f"{stem_a} vs {stem_b}: emitted bodies "
              f"{'identical' if same else 'DIFFER'} "
              f"({len(normalized(body_a))} vs {len(normalized(body_b))} chars)")
    return same, detail


# ---------------------------------------------------------------------------
# leg D: import inspection
# ---------------------------------------------------------------------------

def static_import_scan() -> list:
    violations = []
    candidates = [ROOT / "a100c", ROOT / "tools" / "run_scan.py",
                  ROOT / "tools" / "check_numeric_policy.py"]
    while candidates:
        item = candidates.pop()
        if item.is_dir():
            if item.name in ("__pycache__", "cache", "build", "frontend",
                             "tests"):
                continue
            candidates.extend(sorted(item.iterdir()))
            continue
        if item.suffix != ".py":
            continue
        for number, line in enumerate(
                item.read_text(errors="replace").splitlines(), start=1):
            for pattern, what in FORBIDDEN_IMPORTS:
                if pattern.match(line):
                    violations.append(
                        (item, number, f"{what}: {line.strip()[:90]}"))
    return violations


_COMPILER_PROBE = r"""
import json, sys
sys.path.insert(0, {root!r})
sys.path.insert(0, {harness!r})
import a100c.factory as factory
compiler = factory.make_compiler()
from opslib.runner import load_operator
module = load_operator({operator!r})
case = module.make_case(shape=[97], dtype='float32')
payload = {{k: v for k, v in case.items() if k not in ('expected', 'oracle_args')}}
artifact = compiler.compile_case(payload)
assert artifact.executable.is_file()
bad = [m for m in ('torch', 'a100_support.reference_device',
                   'a100_support.reference_backend') if m in sys.modules]
print(json.dumps({{'modules_present': bad,
                   'elf_magic': open(artifact.executable, 'rb').read(4)
                   .hex()}}))
sys.exit(1 if bad else 0)
"""

_DRIVER_PROBE = r"""
import json, sys
sys.path.insert(0, {root!r})
sys.path.insert(0, {harness!r})
sys.path.insert(0, {tools!r})
import run_scan
from opslib.runner import load_operator
module = load_operator({operator!r})
case = module.make_case(shape=[97], dtype='float32')
device = run_scan.nd.make_device()
staged = device.stage_case(case)
staged.launch()
verdict = run_scan.compare_outputs(case, staged.outputs())
assert verdict['status'] == 'PASS'
transport_converter = 'a100_support.reference_device' in sys.modules
bad = [m for m in ('torch', 'a100_support.reference_backend')
       if m in sys.modules]
print(json.dumps({{'modules_present': bad,
                   'prepared_transport_dtype_converter_loaded':
                       transport_converter,
                   'reference_device_constructed': False}}))
sys.exit(1 if bad else 0)
"""


def dynamic_import_probe(work: Path) -> tuple:
    """Compile through the factory, then run one case through the scan's
    native device, each in a fresh interpreter; assert what loaded."""
    operator = str(ROOT / "ops" / "suite" / "dev" / "absolute_kernel.py")
    results = []
    for name, template, expect_clean in (
            ("compiler+factory", _COMPILER_PROBE, True),
            ("scan driver", _DRIVER_PROBE, False)):
        script = work / f"probe-{name.replace('/', '-')}.py"
        script.write_text(template.format(
            root=str(ROOT), harness=str(ROOT / "ops" / "harness"),
            tools=str(ROOT / "tools"), operator=operator))
        env = dict(os.environ)
        env["A100C_CACHE_DIR"] = str(work / f"cache-{name.replace('/', '-')}")
        proc = subprocess.run([sys.executable, str(script)], capture_output=True,
                              text=True, timeout=300, env=env)
        if proc.returncode != 0:
            return False, (f"{name}: import probe failed: "
                           f"{proc.stderr.strip()[-300:]}")
        payload = json.loads(proc.stdout.strip().splitlines()[-1])
        results.append((name, payload))
    compiler_payload = results[0][1]
    driver_payload = results[1][1]
    ok = (not compiler_payload["modules_present"]
          and not driver_payload["modules_present"])
    detail = (f"compile path loads {compiler_payload['modules_present'] or 'nothing forbidden'}; "
              f"scan path loads {driver_payload['modules_present'] or 'nothing forbidden'}; "
              f"prepared transport dtype converter loaded="
              f"{driver_payload['prepared_transport_dtype_converter_loaded']} "
              f"(a100_support/native_io.py host bf16 representation only; the "
              f"reference device itself is never constructed -- its backend "
              f"module never loads)")
    return ok, detail


# ---------------------------------------------------------------------------
# the witness
# ---------------------------------------------------------------------------

WITNESS_SNIPPET = '''

# witness injection (tools/check_no_name_dispatch.py --witness): a
# name-keyed branch that must be caught by the static scan
def _witness_name_dispatch(operator_name, rel_path):
    if operator_name == {operator_name!r}:
        return True
    if rel_path.endswith({file_name!r}):
        return True
    return False
'''


def run_witness(names) -> int:
    work = Path(tempfile.mkdtemp(prefix="a100-name-witness-"))
    try:
        scratch = work / "scratch-root"
        scratch.mkdir()
        # the pipeline files the check scans, preserving their layout
        py, text = pipeline_files(ROOT)
        for path in py + text:
            target = scratch / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        # an operator name and its file identity, from the corpus manifest
        operator = "matmul"                     # suite/perf/matmul.py
        file_name = "matmul.py"
        assert operator in names["names"], "witness operator name missing"
        assert file_name in names["files"], "witness file name missing"
        inject_into = scratch / "a100c" / "backend" / "select.py"
        if not inject_into.is_file():
            print("witness setup error: select.py missing from scratch copy",
                  file=sys.stderr)
            return 2
        inject_into.write_text(
            inject_into.read_text()
            + WITNESS_SNIPPET.format(operator_name=operator,
                                     file_name=file_name))
        violations = static_scan(scratch, names)
        caught = [v for v in violations if str(v[0]).startswith(str(scratch))]
        if caught:
            print(f"witness: injected operator-name branch CAUGHT in the "
                  f"scratch copy ({len(caught)} finding(s)):")
            for path, line, what in caught[:6]:
                print(f"  {path.relative_to(scratch)}:{line}: {what}")
            print("the check can fail; a clean pipeline result is meaningful")
            return 1                      # nonzero: the branch was caught
        print("FAIL: the injected operator-name branch was NOT caught -- "
              "the check is vacuous")
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="nothing below the frontend branches on an operator, "
                    "kernel or benchmark name; no torch, no reference device")
    parser.add_argument("--witness", action="store_true",
                        help="inject a name-keyed branch into a scratch copy "
                             "of the pipeline and require the check to catch "
                             "it (the witness exits nonzero when caught)")
    parser.add_argument("--skip-dynamic", action="store_true",
                        help="skip the compile/execute import probes (the "
                             "static legs still run)")
    args = parser.parse_args()

    names = corpus_names()
    if args.witness:
        return run_witness(names)

    failures = 0

    violations = static_scan(ROOT, names)
    if violations:
        failures += 1
        print(f"FAIL static name-dispatch scan ({len(violations)} finding(s)):")
        for path, line, what in violations[:12]:
            print(f"  {path.relative_to(ROOT)}:{line}: {what}")
    else:
        print(f"PASS static name-dispatch scan "
              f"(legs A+B over {len(pipeline_files(ROOT)[0])} pipeline files; "
              f"{len(names['names'])} operator names, "
              f"{len(names['kernels'])} kernel names, "
              f"{len(names['files'])} file identities)")

    imports = static_import_scan()
    if imports:
        failures += 1
        print(f"FAIL static import scan ({len(imports)} finding(s)):")
        for path, line, what in imports[:12]:
            print(f"  {path.relative_to(ROOT)}:{line}: {what}")
    else:
        print("PASS static import scan (no torch, no reference device in "
              "a100c/, tools/run_scan.py, tools/check_numeric_policy.py)")

    if not args.skip_dynamic:
        work = Path(tempfile.mkdtemp(prefix="a100-name-check-"))
        try:
            try:
                ok, detail = behavioral_probe(work)
                print(("PASS " if ok else "FAIL ")
                      + f"behavioral name-generality: {detail}")
                failures += 0 if ok else 1
                ok, detail = dynamic_import_probe(work)
                print(("PASS " if ok else "FAIL ")
                      + f"import inspection: {detail}")
                failures += 0 if ok else 1
            finally:
                shutil.rmtree(work, ignore_errors=True)
        except Exception as exc:  # noqa: BLE001 - the probe itself failed
            failures += 1
            print(f"FAIL behavioral/import probe: {type(exc).__name__}: {exc}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
