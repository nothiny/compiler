#!/usr/bin/env python3
"""run_scan.py -- the input scan driver (T017).

Enumerates the corpus's cases with the corpus's own harness
(``run_cases.py --manifest ops/suite/manifest.json``: manifest paths ->
``manifest_specs`` -> ``golden.load_or_build_spec``, i.e.
``opslib.runner.load_operator`` + ``make_case`` exactly as the harness runs
them), groups them by compile identity (the corpus's declared meta tier:
compile once per identity, run every case), stages, executes and compares
each case through the native device protocol
(``a100_support.native_device`` with ``A100_COMPILER_FACTORY``), under a
per-case bound (``A100_EXECUTION_TIMEOUT``): a case that does not return is a
recorded failure, never a wait, and one faulting case never poisons the next.

Comparison uses each case's declared per-output policy -- comparator,
rtol/atol, equal_nan, quantized_interval, allclose_sign_invariant; integer,
index and boolean outputs are exact -- with the tolerance and the reference
read from the case and never widened (F052, IR-NUMERIC-POLICY).

Modes:

  manifest   write the input-regression/v1 case manifest the engine's
             ``regression-prepare`` seals (every case, both tiers, per-case
             comparison policies, resource_evidence flags on representative
             rows) plus the identity census.

  run        execute the scan.  Writes input-regression/v1 report rows for
             ``regression-record`` (``--report``), an append-only journal for
             kill-safe resume (``--journal`` / ``--resume``: a resumed run
             never recompiles what it skips), and the acceptance summary
             (compile count vs identity census <= 1.25x, cache-hit speed).

The driver and the compiler import no torch and no reference device: the
reference service never substitutes for candidate execution (F049/F052).
The only reference-device module on this path is the prepared transport's
dtype converter (``a100_support/native_io.py`` uses
``TritonCpuReferenceDevice.__new__`` for host bf16 representation only --
the reference device itself, its backend and torch are never constructed;
``tools/check_no_name_dispatch.py`` asserts this by import inspection).

Exit codes: 0 = the requested mode completed (individual case failures are
recorded rows, not exit failures); 1 = driver-level error; 2 = usage.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS_ROOT = ROOT / "ops" / "harness"


def _load_project_env() -> None:
    """The declared tool paths from .env (caller exports win)."""
    env_path = ROOT / ".env"
    if env_path.is_file():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key, value.strip())


_load_project_env()

for entry in (str(ROOT), str(HARNESS_ROOT), str(ROOT / "tools")):
    if entry not in sys.path:
        sys.path.insert(0, entry)

# The corpus's own harness: enumeration, case building, comparison and the
# identity tier.  Importing it also installs the torch meta-path blocker
# (run_cases refuses torch on this path), which is exactly the discipline the
# scan wants.
from compiler_api import identity as identity_lib  # noqa: E402
from compiler_api.run_cases import cases_from_manifest, enumerate_cases, \
    manifest_specs  # noqa: E402
from opslib import compare as compare_lib  # noqa: E402
from opslib import golden  # noqa: E402

import a100_support.native_device as nd  # noqa: E402
from a100c.driver import PipelineError  # noqa: E402

SCHEMA = "input-regression/v1"
SUMMARY_SCHEMA = "a100-scan-summary/v1"
GROUPS = ("suite/dev", "suite/perf")
DEFAULT_MANIFEST = "ops/suite/manifest.json"
#: the corpus's declared economics (OPERATOR_INVENTORY §1 / SUITE_V3.md §0);
#: the run's own census is recomputed and both are reported
DECLARED_CENSUS = {"cases": 2734, "identities": 2161}
#: dtypes whose IME execution is verified under the pinned endpoint (F034)
IME_VERIFIED_DTYPES = ("float16", "int8")
#: the corpus tag that marks dot-carrying operators (manifest metadata, not
#: an operator name)
DOT_TAG = "dot.matmul"

STATUS_PASS = "PASS"
STATUS_CASE_FAIL = "CASE_FAIL"
STATUS_COMPILE_REFUSED = "COMPILE_REFUSED"
STATUS_LAUNCH_FAIL = "LAUNCH_FAIL"
STATUS_TIMEOUT = "TIMEOUT"
STATUS_MISMATCH = "MISMATCH"
STATUS_EVIDENCE_FAIL = "EVIDENCE_FAIL"


# ---------------------------------------------------------------------------
# enumeration -- exactly the harness's own path
# ---------------------------------------------------------------------------

def resolve_operator_path(raw: str) -> str:
    """A user-given operator path -> the corpus-root-relative source key.

    Accepts project-relative (``ops/suite/dev/x.py``), corpus-relative
    (``suite/dev/x.py``) and absolute paths.
    """
    corpus = HARNESS_ROOT.parent
    path = Path(raw)
    if path.is_absolute():
        candidates = [path]
    else:
        candidates = [ROOT / path, corpus / path,
                      corpus / path.relative_to("ops") if raw.startswith("ops/")
                      else None]
    for candidate in candidates:
        if candidate is None:
            continue
        if candidate.is_file():
            return str(candidate.resolve().relative_to(corpus.resolve()))
    raise FileNotFoundError(f"operator file not found: {raw}")


def case_id(source: str, shape, dtype) -> str:
    """Stable unique case identifier: operator + shape + dtype."""
    return f"{source}#{json.dumps([int(v) for v in shape])}#{dtype}"


def enumerated_rows(manifest_path: str, group=None, operators=None):
    """Every (operator, shape, dtype) case, harness order, with its spec."""
    paths = cases_from_manifest(manifest_path)
    operator_keys = {resolve_operator_path(op) for op in operators} \
        if operators else None
    for spec, shape, dtype in enumerate_cases(None, group, operator_keys,
                                              paths):
        yield {"id": case_id(spec.source, shape, dtype),
               "group": spec.entry["group"], "operator": spec.source,
               "shape": [int(v) for v in shape], "dtype": str(dtype),
               "spec": spec}


def build_case(row, seed: int, use_golden: bool = True) -> dict:
    """The case payload, built exactly as the harness builds it."""
    return golden.load_or_build_spec(row["spec"], shape=row["shape"],
                                     dtype=row["dtype"], seed=seed,
                                     use_cache=use_golden)


def _jsonable(value):
    """Case payloads contain numpy scalars/arrays; the report is JSON."""
    import numpy as np
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    return value


# ---------------------------------------------------------------------------
# representative resource-evidence rows (from the corpus's own metadata)
# ---------------------------------------------------------------------------

def _corpus_manifest(manifest_path: str) -> dict:
    return json.loads((ROOT / manifest_path).read_text())


def representative_resource_cases(manifest_path: str) -> dict:
    """The deterministic representative rule for resource_evidence flags.

    One dot-carrying case per tier (the corpus ``dot.matmul`` tag), the
    smallest shape of an IME-verified dtype when the operator declares one.
    Selection is by the corpus's own declared metadata (family tags, shapes,
    dtypes) -- never by an operator, kernel or benchmark name, and never by
    peeking at compiler output.  The flagged rows are executed at
    ``--resource-threads`` under the QEMU instruction-count plugin so their
    report rows can bind instruction counts and multi-worker observation to
    the same run, case and artifact (A100-VALIDATION).
    """
    data = _corpus_manifest(manifest_path)
    chosen = {}
    for operator in data.get("operators", []):
        tags = operator.get("tags") or []
        if DOT_TAG not in tags:
            continue
        lane = operator.get("lane")
        if lane not in ("dev", "perf") or lane in chosen:
            continue
        dtypes = operator.get("dtype_names") or []
        dtype = next((d for d in IME_VERIFIED_DTYPES if d in dtypes),
                     dtypes[0] if dtypes else None)
        if dtype is None:
            continue
        shapes = operator.get("shape_list") or []
        shape = min(shapes, key=lambda s: (len(s), sum(s))) if shapes else []
        chosen[lane] = case_id(operator["path"], shape, dtype)
    return chosen


# ---------------------------------------------------------------------------
# per-case bound (never a wait)
# ---------------------------------------------------------------------------

class CaseDeadline(Exception):
    """One case exceeded its overall wall-clock budget (SIGALRM)."""


def _raise_deadline(signum, frame):
    raise CaseDeadline("case budget exceeded")


class _deadline:
    """SIGALRM bound around one case's build/stage/launch/compare."""

    def __init__(self, seconds):
        self.seconds = float(seconds) if seconds else None

    def __enter__(self):
        if not self.seconds:
            return self
        self._previous = signal.signal(signal.SIGALRM, _raise_deadline)
        signal.setitimer(signal.ITIMER_REAL, self.seconds)
        return self

    def __exit__(self, *exc):
        if self.seconds:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, self._previous)
        return False


# ---------------------------------------------------------------------------
# the comparison entry (tolerance and reference are the case's own)
# ---------------------------------------------------------------------------

def compare_outputs(case, actual, expected=None):
    """The scan's single comparison entry point.

    The comparator, tolerances and reference are read from the case
    (``case['comparison']`` / ``case['expected']``); this driver never passes
    an rtol/atol override and never substitutes a reference.  Integer, index
    and boolean outputs are exact (opslib.compare enforces the dtype rule).
    """
    return compare_lib.compare_case(case, actual, expected)


# ---------------------------------------------------------------------------
# resource-evidence capture (QEMU instruction-count plugin + worker view)
# ---------------------------------------------------------------------------

def _plugin_path(work_dir: Path) -> Path:
    """The compiled instruction-count plugin (F008/F048), built if missing."""
    built = ROOT / "a100_support" / "build" / "instruction_counts.so"
    if built.is_file():
        return built
    out = work_dir / "instruction_counts.so"
    if out.is_file():
        return out
    prefix = os.environ.get("A100_PREFIX", "")
    include = [f"-I{prefix}/jdsk-qemu-10.0.2/include",
               f"-I{prefix}/host-runtime-bookworm/include/glib-2.0",
               f"-I{prefix}/host-runtime-bookworm/lib/glib-2.0/include"]
    subprocess.run(["gcc", "-O2", "-Wall", "-Wextra", "-shared", "-fPIC",
                    "-pthread", *include,
                    str(ROOT / "a100_support" / "probes"
                        / "instruction_counts.c"),
                    "-o", str(out)], check=True, timeout=120)
    return out


def _instrumented_command(executable, bundle, threads, plugin, counts_out):
    """The native launch with the instruction-count plugin loaded -- the same
    QEMU endpoint and argument ABI ``a100_support/run-riscv.sh`` uses."""
    qemu = os.environ["A100_QEMU"]
    cpu = os.environ.get("A100_QEMU_CPU",
                         "max,vlen=1024,elen=64,vext_spec=v1.0")
    sysroot = os.environ["A100_SYSROOT"]
    command = [qemu, "-L", sysroot, "-cpu", cpu,
               "-plugin", f"{plugin},out={counts_out}",
               str(executable), "--bundle", str(bundle),
               "--threads", str(threads)]
    loader = os.environ.get("A100_QEMU_LOADER")
    if loader:
        command = [loader, "--library-path",
                   os.environ["A100_QEMU_HOST_LIB"], *command]
    return command


def _pattern_executions(counts: dict, pattern: str) -> int:
    """Executed instructions of one declared pattern: the exact mnemonic or
    its family suffixes (``smt.vmadot`` counts ``smt.vmadot.sp`` too)."""
    total = 0
    for row in counts.get("instructions", []):
        mnemonic = row.get("mnemonic", "")
        if mnemonic == pattern or mnemonic.startswith(pattern + "."):
            total += int(row.get("executions", 0))
    return total


def _rel(path: Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(Path(path).resolve())


def _sha256(path: Path) -> str:
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def capture_resource_evidence(staged, case_id_text, run_id, threads,
                              requirements, work_dir, case_timeout):
    """Run one flagged case under the instruction-count plugin and bind the
    observation to this run, case and artifact.

    Returns ``(ran_ok, contract_ok, detail, binding_ref, observations)``:
    ``ran_ok`` says the instrumented execution itself succeeded (exit 0,
    observation read back); ``contract_ok`` says the declared resource
    contract (instruction witnesses, executed counts, multi-worker
    observation) is satisfied by what was actually observed.
    ``binding_ref`` is the report row's ``resource_evidence`` value when the
    capture satisfies the declared contract, else None -- the capture files
    are still written: what was observed is evidence even when it does not
    satisfy the requirement, and the row records exactly which condition
    was unmet (never a fabricated pass).
    """
    work_dir.mkdir(parents=True, exist_ok=True)
    counts_path = work_dir / "counts.json"
    command = _instrumented_command(staged.artifact.executable,
                                    staged.directory / "bundle.bin", threads,
                                    _plugin_path(work_dir), counts_path)
    began = time.monotonic()
    result = subprocess.run(command, capture_output=True, text=True,
                            timeout=float(case_timeout))
    ended = time.monotonic()
    info = None
    for line in reversed((result.stdout or "").strip().splitlines()):
        try:
            info = json.loads(line)
            break
        except ValueError:
            continue
    observations = {"exit_code": result.returncode,
                    "command": " ".join(str(p) for p in command),
                    "interval_s": [began, ended]}
    if result.returncode or info is None:
        return False, False, \
            f"instrumented run failed (exit {result.returncode})", None, \
            observations
    counts = json.loads(counts_path.read_text())
    patterns = requirements.get("instruction_patterns") or []
    units = requirements.get("allowed_units") or []
    minimum = int(requirements.get("minimum_workers") or 2)
    # the listing: the emitted program of this exact artifact
    listing = staged.artifact.executable.parent / "program.S"
    if not listing.is_file():
        return True, False, "listing unavailable for the artifact", None, \
            observations
    listing_copy = work_dir / "listing.S"
    shutil.copyfile(listing, listing_copy)
    instruction_counts = {pattern: _pattern_executions(counts, pattern)
                          for pattern in patterns}
    workers = []
    for worker in info.get("workers", []):
        index = int(worker.get("id", 0))
        unit = f"a100-compute-worker-slot-{index}" if index < len(units) \
            else None
        if unit is None or unit not in units:
            return True, False, (f"worker {index} ran outside the declared "
                                 f"resource set"), None, observations
        workers.append({"worker": f"worker-{index}", "unit": unit,
                        "observed_units": [unit],
                        "completed_units": int(worker.get("items", 0)),
                        "start": began, "end": ended})
    variant = f"threads-{threads}"
    execution_log = {"run_id": run_id, "case_id": case_id_text,
                     "artifact_sha256": staged.artifact_sha256,
                     "variant": variant,
                     "instruction_counts": instruction_counts,
                     "workers": workers,
                     "guest_tids": [int(w.get("guest_tid", 0))
                                    for w in info.get("workers", [])],
                     "command": observations["command"]}
    log_path = work_dir / "execution_log.json"
    log_path.write_text(json.dumps(execution_log, indent=2) + "\n")
    binding = {"requirements_sha256": _sha256(ROOT / "EXECUTION_RESOURCES.json"),
               "artifact": {"path": _rel(staged.artifact.executable),
                            "sha256": staged.artifact_sha256},
               "listing": {"path": _rel(listing_copy),
                           "sha256": _sha256(listing_copy)},
               "execution_log": {"path": _rel(log_path),
                                 "sha256": _sha256(log_path)},
               "variant": variant}
    binding_path = work_dir / "binding.json"
    binding_path.write_text(json.dumps(binding, indent=2) + "\n")
    # the declared contract, checked locally so an unmet condition is a
    # visible row failure -- never a fabricated pass
    unmet = []
    for pattern in patterns:
        if not re.search(r"(?<![\w.])" + re.escape(pattern) + r"(?![\w.])",
                         listing_copy.read_text()):
            unmet.append(f"instruction witness missing: {pattern}")
        elif instruction_counts.get(pattern, 0) < 1:
            unmet.append(f"executed instruction count zero: {pattern}")
    active = [w for w in workers if w["completed_units"] > 0]
    distinct_units = {w["unit"] for w in active}
    if len(active) < minimum or len(distinct_units) < minimum:
        unmet.append(f"insufficient multi-worker observation: "
                     f"{len(active)} active workers over "
                     f"{len(distinct_units)} units (minimum {minimum})")
    observations.update({"instruction_counts": instruction_counts,
                         "workers": workers})
    binding_ref = {"path": _rel(binding_path), "sha256": _sha256(binding_path)}
    if unmet:
        return True, False, "; ".join(unmet), binding_ref, observations
    return True, True, "", binding_ref, observations


# ---------------------------------------------------------------------------
# the scan
# ---------------------------------------------------------------------------

class ScanDriver:
    def __init__(self, args):
        self.args = args
        self.device = nd.make_device()      # A100_COMPILER_FACTORY from .env
        if args.threads is not None:
            if args.threads not in (1, 2, 4, 8):
                raise SystemExit("--threads must be one of 1, 2, 4, 8")
            self.device.threads = args.threads
        self.compiler = self.device.compiler
        self.case_timeout = float(args.case_timeout
                                  or os.environ.get("A100_EXECUTION_TIMEOUT",
                                                    "120"))
        # the overall per-case bound sits above the launch bound so a hanging
        # launch is cut by the subprocess bound first (its own message)
        self.case_budget = self.case_timeout * 1.5 + 5.0
        self.compile_calls = []
        self._instrument_compiles()
        self._resource_ids = set()
        self.requirements = {}
        resources = ROOT / "EXECUTION_RESOURCES.json"
        if resources.is_file():
            self.requirements = json.loads(resources.read_text())

    def _instrument_compiles(self):
        """Time every compile_case call (cold vs cache hit)."""
        inner = self.compiler.compile_case

        def compile_case(case):
            began = time.perf_counter()
            artifact = inner(case)
            self.compile_calls.append({
                "ms": round((time.perf_counter() - began) * 1000, 3),
                "cache_hit": bool(getattr(artifact, "cache_hit", False)),
                "key": Path(artifact.executable).parent.name})
            return artifact

        self.compiler.compile_case = compile_case

    # -- one case ------------------------------------------------------------
    def run_case(self, row, evidence_root=None, fault=None) -> dict:
        """One case end to end; every failure is a recorded row."""
        began = time.perf_counter()
        result = self._run_case_inner(row, evidence_root, fault)
        result["seconds"] = round(time.perf_counter() - began, 3)
        return result

    def _run_case_inner(self, row, evidence_root, fault) -> dict:
        args = self.args
        result = {"id": row["id"], "group": row["group"],
                  "operator": row["operator"], "shape": row["shape"],
                  "dtype": row["dtype"],
                  "compiled": False, "executed": False, "compared": False,
                  "passed": False, "status": STATUS_CASE_FAIL, "detail": "",
                  "threads": self.device.threads}
        try:
            with _deadline(self.case_budget):
                case = build_case(row, args.seed,
                                  use_golden=not args.no_golden)
            result["identity"] = identity_lib.case_identity(
                row["operator"], case, tier="meta")
        except CaseDeadline as exc:
            result.update(status=STATUS_TIMEOUT,
                          detail=f"case build: {exc}")
            return result
        except Exception as exc:  # noqa: BLE001 - a broken case is data
            result.update(status=STATUS_CASE_FAIL,
                          detail=f"{type(exc).__name__}: {exc}"[:400])
            return result
        try:
            with _deadline(self.case_budget):
                staged = self.device.stage_case(case)
        except PipelineError as exc:
            # a located compile refusal: a recorded finding for repair,
            # never a silently narrowed corpus
            result.update(status=STATUS_COMPILE_REFUSED,
                          detail=str(exc)[:400])
            return result
        except CaseDeadline as exc:
            result.update(status=STATUS_TIMEOUT, detail=f"stage: {exc}")
            return result
        except Exception as exc:  # noqa: BLE001
            result.update(status=STATUS_LAUNCH_FAIL,
                          detail=f"stage: {type(exc).__name__}: {exc}"[:400])
            return result
        artifact = staged.artifact
        result["compiled"] = True
        result["artifact_sha256"] = staged.artifact_sha256
        result["artifact_key"] = Path(artifact.executable).parent.name
        result["cache_hit"] = bool(getattr(artifact, "cache_hit", False))
        resource = row["id"] in self._resource_ids
        launch_began = time.perf_counter()
        try:
            if resource:
                ran_ok, contract_ok, detail, binding, observations = \
                    capture_resource_evidence(
                        staged, row["id"], args.run_id,
                        args.resource_threads, self.requirements,
                        (evidence_root / row["id"].replace("/", "__"))
                        if evidence_root else Path(tempfile.mkdtemp(
                            prefix="a100-resource-")),
                        self.case_timeout)
                result["resource_observations"] = _jsonable(observations)
                result["threads"] = args.resource_threads
                executed = ran_ok
                evidence = binding if contract_ok else None
                evidence_detail = "" if contract_ok else detail
                if not ran_ok:
                    raise RuntimeError(detail)
            else:
                if fault == "crash":
                    # the fault-isolation witness: a real bundle fault the
                    # native process hits (the next case is unaffected)
                    bundle = staged.directory / "bundle.bin"
                    with open(bundle, "r+b") as handle:
                        handle.truncate(16)
                if fault == "timeout":
                    # a case that does not return within its bound: the
                    # launch is cut at --fault-timeout and recorded, never
                    # waited on
                    previous = os.environ.get("A100_EXECUTION_TIMEOUT")
                    os.environ["A100_EXECUTION_TIMEOUT"] = \
                        str(args.fault_timeout)
                    try:
                        with _deadline(self.case_budget):
                            staged.launch()
                    finally:
                        if previous is None:
                            os.environ.pop("A100_EXECUTION_TIMEOUT", None)
                        else:
                            os.environ["A100_EXECUTION_TIMEOUT"] = previous
                else:
                    with _deadline(self.case_budget):
                        staged.launch()
                executed, evidence, evidence_detail = True, None, ""
        except subprocess.TimeoutExpired as exc:
            result.update(status=STATUS_TIMEOUT, executed=False,
                          launch_seconds=round(time.perf_counter()
                                               - launch_began, 3),
                          detail=(f"launch exceeded its bound "
                                  f"{exc.timeout:g}s "
                                  f"(A100_EXECUTION_TIMEOUT)"))
            return result
        except CaseDeadline as exc:
            result.update(status=STATUS_TIMEOUT, executed=False,
                          detail=f"case budget: {exc}")
            return result
        except Exception as exc:  # noqa: BLE001
            result.update(status=STATUS_LAUNCH_FAIL, executed=False,
                          launch_seconds=round(time.perf_counter()
                                               - launch_began, 3),
                          detail=f"launch: {type(exc).__name__}: "
                                 f"{exc}"[:400])
            return result
        result["executed"] = executed
        result["launch_seconds"] = round(time.perf_counter() - launch_began,
                                         3)
        if not executed:
            result["status"] = STATUS_LAUNCH_FAIL
            result["detail"] = evidence_detail or "instrumented run failed"
            return result
        try:
            with _deadline(self.case_budget):
                verdict = compare_outputs(case, staged.outputs())
        except CaseDeadline as exc:
            result.update(status=STATUS_TIMEOUT, detail=f"compare: {exc}")
            return result
        except Exception as exc:  # noqa: BLE001 - the comparison verdict
            result["compared"] = True
            result.update(status=STATUS_MISMATCH,
                          detail=str(exc).splitlines()[0][:400])
            return result
        result["compared"] = True
        result["max_abs_error"] = _jsonable(verdict.get("max_abs_error", {}))
        if evidence is not None:
            result["resource_evidence"] = evidence
        if evidence_detail:
            result.update(status=STATUS_EVIDENCE_FAIL, passed=False,
                          detail=evidence_detail[:400])
        else:
            result.update(status=STATUS_PASS, passed=True)
        return result

    # -- the whole run --------------------------------------------------------
    def run(self):
        args = self.args
        rows = list(enumerated_rows(args.manifest_path, args.group,
                                    args.operator))
        representatives = representative_resource_cases(args.manifest_path)
        self._resource_ids = set(representatives.values())
        self._resource_ids.update(args.flag_resource or ())
        journal_rows = {}
        if args.journal and Path(args.journal).is_file():
            for line in Path(args.journal).read_text(
                    errors="replace").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                    journal_rows[row["id"]] = row   # last write wins
                except Exception:                   # noqa: BLE001 - torn line
                    continue
        resume_keys = set()
        if args.resume:
            resume_keys = {key for key, row in journal_rows.items()
                           if not args.retry_failed
                           or row.get("status") != STATUS_PASS}
        evidence_root = None
        if args.report:
            evidence_root = Path(args.report).resolve().parent \
                / "resource-evidence"
        run_rows, identities = [], {}
        resumed = 0
        executed_here = 0
        for row in rows:
            if row["id"] in resume_keys:
                resumed += 1
                previous = journal_rows.get(row["id"])
                if previous is not None:
                    run_rows.append(previous)
                    if previous.get("identity"):
                        identity = previous["identity"]
                        identities[identity] = identities.get(identity, 0) + 1
                continue
            if args.limit is not None and executed_here >= args.limit:
                break
            executed_here += 1
            fault = None
            for injection in args.fault_inject or ():
                name, _, kind = injection.partition(":")
                if name == row["id"]:
                    fault = kind or "crash"
            result = self.run_case(row, evidence_root=evidence_root,
                                   fault=fault)
            if "identity" in result:
                identities[result["identity"]] = \
                    identities.get(result["identity"], 0) + 1
            run_rows.append(result)
            print(f"[{len(run_rows)}/{len(rows)}] {result['status']:16s} "
                  f"{result['operator']} {result['shape']} "
                  f"{result['dtype']}"
                  + (f" :: {result['detail'][:120]}"
                     if result["detail"] else ""), flush=True)
            if args.journal:
                Path(args.journal).parent.mkdir(parents=True, exist_ok=True)
                with open(args.journal, "a", encoding="utf-8") as stream:
                    stream.write(json.dumps(result, ensure_ascii=False)
                                 + "\n")
        # the report: this run's rows plus the journal's rows for skipped
        # cases, in enumeration order (a partial run is marked as such)
        by_id = {row["id"]: row for row in run_rows}
        report_rows = []
        missing = []
        for row in rows:
            if row["id"] in by_id:
                report_rows.append(by_id[row["id"]])
            elif row["id"] in journal_rows:
                report_rows.append(journal_rows[row["id"]])
            else:
                missing.append(row["id"])
        summary = self.summarize(rows, report_rows, identities, resumed,
                                 executed_here, missing)
        if args.report:
            report = {"schema": SCHEMA, "run_id": args.run_id,
                      "command": " ".join(sys.argv),
                      "partial": bool(missing),
                      "missing_case_ids": missing[:20],
                      "cases": _jsonable(report_rows)}
            Path(args.report).parent.mkdir(parents=True, exist_ok=True)
            Path(args.report).write_text(
                json.dumps(report, indent=2, ensure_ascii=False) + "\n")
            Path(args.report).with_suffix(
                Path(args.report).suffix + ".summary.json").write_text(
                json.dumps(summary, indent=2) + "\n")
            print(f"report -> {args.report} "
                  f"({len(report_rows)} rows, summary beside it)")
        print(json.dumps(summary, indent=2))
        return 0

    def summarize(self, rows, report_rows, identities, resumed,
                  executed_here, missing):
        from statistics import median
        cold = [call["ms"] for call in self.compile_calls
                if not call["cache_hit"]]
        warm = [call["ms"] for call in self.compile_calls
                if call["cache_hit"]]
        artifact_identities = {call["key"] for call in self.compile_calls}
        compile_count = self.compiler.compile_count
        cache_hits = self.compiler.cache_hits
        distinct = len(identities)
        statuses = {}
        for row in report_rows:
            statuses[row["status"]] = statuses.get(row["status"], 0) + 1
        cold_median = median(cold) if cold else None
        warm_median = median(warm) if warm else None
        cache_hit_fast = (warm_median is not None and warm_median < 500.0
                          and (not cold or warm_median < cold_median / 4))
        return {
            "schema": SUMMARY_SCHEMA,
            "run": {"cases_enumerated": len(rows),
                    "rows_reported": len(report_rows),
                    "run_this_process": executed_here,
                    "resumed": resumed, "missing": len(missing),
                    "threads": self.device.threads,
                    "resource_threads": self.args.resource_threads,
                    "case_timeout_s": self.case_timeout,
                    "representative_resource_cases":
                        sorted(self._resource_ids)},
            "census": {"cases": len(rows), "identities": distinct,
                       "declared_full_corpus": DECLARED_CENSUS},
            "compile": {"count": compile_count, "cache_hits": cache_hits,
                        "artifact_identities": len(artifact_identities),
                        "cold_ms_median": cold_median,
                        "cache_hit_ms_median": warm_median,
                        "cold_ms": cold[:64], "cache_hit_ms": warm[:64]},
            "statuses": statuses,
            "checks": {
                "compile_count_le_identity_census_1_25x":
                    bool(distinct and compile_count <= 1.25 * distinct),
                "artifact_identities_le_identity_census_1_25x":
                    bool(distinct
                         and len(artifact_identities) <= 1.25 * distinct),
                "compile_count_equals_artifact_identities":
                    compile_count == len(artifact_identities),
                "cache_hit_is_fast": cache_hit_fast,
                "report_complete": not missing,
            },
        }


# ---------------------------------------------------------------------------
# the manifest builder (input-regression/v1, for regression-prepare)
# ---------------------------------------------------------------------------

def build_manifest(args) -> int:
    rows = list(enumerated_rows(args.manifest_path, args.group,
                                args.operator))
    representatives = representative_resource_cases(args.manifest_path)
    cases, identities = [], {}
    for row in rows:
        case = build_case(row, args.seed, use_golden=not args.no_golden)
        identity = identity_lib.case_identity(row["operator"], case,
                                              tier="meta")
        identities[identity] = identities.get(identity, 0) + 1
        cases.append({
            "id": row["id"], "group": row["group"],
            "operator": row["operator"], "shape": row["shape"],
            "dtype": row["dtype"],
            "kernel": identity_lib.kernel_name(case),
            "identity": identity,
            "comparison": _jsonable(case.get("comparison") or {}),
            "resource_evidence": row["id"] in set(
                representatives.values()),
        })
        print(f"[{len(cases)}/{len(rows)}] {row['operator']} "
              f"{row['shape']} {row['dtype']}", flush=True)
    manifest = {
        "schema": SCHEMA,
        "generator": "tools/run_scan.py manifest",
        "identity_tier": "meta",
        "seed": args.seed,
        "census": {"cases": len(cases), "identities": len(identities),
                   "declared_full_corpus": DECLARED_CENSUS},
        "representative_rule": (
            "one dot-carrying case per tier (corpus tag 'dot.matmul', "
            "smallest shape of an IME-verified dtype: float16, int8), "
            "selected from the corpus's own declared metadata"),
        "representative_resource_cases": representatives,
        "cases": cases,
    }
    totals = {}
    for case in cases:
        totals[case["group"]] = totals.get(case["group"], 0) + 1
    manifest["group_totals"] = totals
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(manifest, indent=2,
                                         ensure_ascii=False) + "\n")
    print(f"manifest -> {args.out} ({len(cases)} cases, "
          f"{len(identities)} identities, totals {totals})")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="the input scan driver (enumerate, compile once per "
                    "identity, execute, compare, report)")
    parser.add_argument("--manifest-path", default=DEFAULT_MANIFEST,
                        help="the corpus suite manifest "
                             "(default ops/suite/manifest.json)")
    parser.add_argument("--seed", type=int, default=30)
    parser.add_argument("--no-golden", action="store_true",
                        help="rebuild every case with make_case (no cache)")
    sub = parser.add_subparsers(dest="mode", required=True)

    p_manifest = sub.add_parser(
        "manifest", help="write the input-regression/v1 manifest")
    p_manifest.add_argument("--out", required=True)
    p_manifest.add_argument("--group", choices=GROUPS)
    p_manifest.add_argument("--operator", action="append")

    p_run = sub.add_parser("run", help="execute the scan")
    p_run.add_argument("--report",
                       help="write the input-regression/v1 report rows "
                            "(project-relative keeps evidence bindings "
                            "resolvable)")
    p_run.add_argument("--run-id",
                       help="the prepared regression run id the report and "
                            "its evidence bind to")
    p_run.add_argument("--journal", help="append one JSON line per case")
    p_run.add_argument("--resume", action="store_true",
                       help="skip cases already recorded in --journal")
    p_run.add_argument("--retry-failed", action="store_true",
                       help="with --resume: re-run non-PASS cases too")
    p_run.add_argument("--limit", type=int,
                       help="run at most N cases this process")
    p_run.add_argument("--group", choices=GROUPS)
    p_run.add_argument("--operator", action="append",
                       help="restrict to operator files (repeatable)")
    p_run.add_argument("--threads", type=int, choices=(1, 2, 4, 8),
                       help="compute threads (default A100_COMPUTE_THREADS "
                            "or 1)")
    p_run.add_argument("--resource-threads", type=int, default=4,
                       choices=(2, 4, 8),
                       help="threads for resource-evidence rows (default 4)")
    p_run.add_argument("--case-timeout", type=float,
                       help="per-case bound in seconds (default "
                            "A100_EXECUTION_TIMEOUT or 120)")
    p_run.add_argument("--fault-inject", action="append", metavar="ID[:KIND]",
                       help="fault-isolation witness: corrupt this case's "
                            "bundle (crash) or cut its launch at "
                            "--fault-timeout (timeout)")
    p_run.add_argument("--fault-timeout", type=float, default=2.0,
                       help="the bound used by ID:timeout (default 2s)")
    p_run.add_argument("--flag-resource", action="append", default=[],
                       metavar="ID",
                       help="add a case id to the resource-evidence set")
    args = parser.parse_args(argv)

    if args.mode == "manifest":
        return build_manifest(args)

    if args.resume and not args.journal:
        parser.error("--resume needs --journal")
    if args.run_id and not args.report:
        parser.error("--run-id needs --report")
    try:
        driver = ScanDriver(args)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return driver.run()


if __name__ == "__main__":
    sys.exit(main())
