"""Enumerate every (operator, shape, dtype) case and run it through a Device.

This is the single test loop for the whole corpus: it walks the catalog,
builds each case, stages it through the supplied ``Device``, and compares
against the NumPy oracle.  It is torch-free: unless the device itself is a
torch device, a meta-path blocker keeps ``torch`` out of the process so a
self-built compiler never meets it (``--allow-torch`` disables the blocker,
``OPS_BLOCK_TORCH=1`` forces it on for any device).

    # enumerate only (no device needed)
    python3 harness/compiler_api/run_cases.py --dry-run
    python3 harness/compiler_api/run_cases.py --dry-run --group basic
    python3 harness/compiler_api/run_cases.py --dry-run --group-order

    # run through the reference CPU device
    python3 harness/compiler_api/run_cases.py --device cpu --group basic
    python3 harness/compiler_api/run_cases.py --device cpu --group-order

    # run through your own compiler device
    from compiler_api.run_cases import run_all
    rows = run_all(my_device, channel="all", group="medium")

    # specific operator files only (paths relative to the corpus root)
    python3 harness/compiler_api/run_cases.py --device cuda --operator suite/dev/argmax.py

    # N concurrent subprocesses, one shard each, merged report; --gpus
    # pins shard i to GPU gpus[i % len(gpus)]
    python3 harness/compiler_api/run_cases.py --device cuda --jobs 4 --gpus 0,1,2,3

    # kill-safe long run: one JSON line per finished case, heartbeat file for
    # a watchdog, per-case deadline; a killed run resumes where it stopped
    python3 harness/compiler_api/run_cases.py --device mydev:device \
        --journal runs/local.jsonl --heartbeat runs/local.status.json \
        --resume --case-timeout 120 --progress-every 25 --report runs/local.json

    # resource caps for one case: an RSS ceiling (a huge PTX / runaway IR
    # allocation dies as one OOM row instead of OOM-killing the sweep) and
    # kernel-enforced CPU seconds (the SIGALRM deadline above cannot fire
    # while a single C call runs).  RLIMIT_AS is opt-in: a CUDA context maps
    # tens of GiB of *virtual* space, so an address-space cap cannot tell a
    # real leak from the driver's reservations.
    python3 harness/compiler_api/run_cases.py --device mydev:device \
        --case-memory-mb 16384 --case-cpu-seconds 300 --journal runs/local.jsonl
"""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import signal
import subprocess
import threading
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]     # <root>/harness
ROOT = HARNESS.parent                               # the corpus root
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

TORCH_DEVICES = ("torch-gpu", "torch-cpu")


class _TorchBlocker:
    """Meta-path finder that refuses ``torch`` / ``torch.*`` imports.

    Raising ``ImportError`` (rather than installing ``sys.modules['torch'] =
    None``) is deliberate: stock Triton's AMD-backend probe catches the
    ImportError and falls back, while its binding code would crash on a None
    module.  Must be inserted before anything imports triton.
    """

    def find_spec(self, fullname, path=None, target=None):
        if fullname == "torch" or fullname.startswith("torch."):
            raise ImportError(
                "torch is blocked on this path (run_cases --block-torch)")
        return None


def _argv_device():
    """Best-effort --device value from raw argv (before argparse runs)."""
    argv = sys.argv
    for i, arg in enumerate(argv[1:], start=1):
        if arg.startswith("--device="):
            return arg.split("=", 1)[1]
        if arg == "--device" and i + 1 < len(argv):
            return argv[i + 1]
    return None


def _install_blocker():
    sys.meta_path.insert(0, _TorchBlocker())
    return True


def _install_default_blocker():
    """Block torch unless the requested device is a torch device."""
    if "--allow-torch" in sys.argv:
        return False
    device = _argv_device()
    if device is not None and any(device.startswith(t) for t in TORCH_DEVICES):
        return False
    return _install_blocker()


_TORCH_BLOCKED = _install_default_blocker()

from opslib import catalog  # noqa: E402
from opslib import compare as compare_lib  # noqa: E402
from opslib import golden  # noqa: E402
from opslib.device import make_device, run_case, stage_case  # noqa: E402

from compiler_api import identity as identity_lib  # noqa: E402

# The two input directories, in the order the corpus declares them.
GROUP_ORDER = ("suite/dev", "suite/perf")   # upstream pool: --group basic ...


def _to_list(value):
    if isinstance(value, (list, tuple)):
        return [_to_list(item) for item in value]
    return int(value)


def _resolve_operator_paths(paths):
    """User-given operator paths -> catalog source keys (repo-relative)."""
    out = set()
    for raw in paths:
        p = Path(raw)
        p = p if p.is_absolute() else ROOT / p
        try:
            out.add(str(p.resolve().relative_to(ROOT)))
        except ValueError:
            out.add(str(p))
    return out


def manifest_specs(paths):
    """``OperatorSpec``-shaped objects for explicit files (e.g. a suite manifest).

    The catalog only indexes the four input directories, so a selected suite
    that pulls operators from a pool directory (``hidden/``) cannot be
    enumerated through it.  These specs are duck-typed: ``source``,
    ``entry["group"]``, ``supported`` and ``load()`` are all the runner needs.
    """
    from opslib.runner import load_operator

    for rel in paths:
        path = ROOT / rel
        if not path.is_file():
            raise FileNotFoundError(f"manifest lists a missing operator: {rel}")
        # group = the directory that holds the file, relative to the corpus root
        try:
            group = path.resolve().parent.relative_to(ROOT.resolve()).as_posix()
        except ValueError:
            group = Path(rel).parent.as_posix()
        entry = {"channel": "local", "group": group,
                 "name": path.stem, "source": rel, "path": str(path),
                 "execution": "triton", "verification": "numpy", "oracle": "numpy",
                 "kernel": None, "sha256": None}
        spec = catalog.OperatorSpec(entry)
        spec.load()                       # fail early on a broken file
        yield spec


def cases_from_manifest(manifest_path: str):
    """Operator paths listed in a suite manifest (``suite/manifest.json``)."""
    data = json.loads(Path(manifest_path).read_text())
    operators = data.get("operators") or []
    paths = [op["path"] if isinstance(op, dict) else str(op) for op in operators]
    if not paths:
        raise SystemExit(f"{manifest_path}: no operators listed")
    return paths


def enumerate_cases(channel: str = "all", group: str | None = None,
                    operators: set[str] | None = None,
                    paths: list[str] | None = None):
    """Yield ``(spec, shape, dtype)`` for every supported operator case.

    ``group`` restricts to one directory (``basic`` ... ``bench``);
    ``None``/``"all"`` yields every group.  ``operators`` restricts to the
    given repo-relative operator source paths.  ``paths`` bypasses the catalog
    and enumerates exactly those files (a selected suite manifest).
    """
    if paths is None and group not in (None, "all"):
        # a single group is enumerated by directory, so the dev suite
        # (`suite/dev`) and the upstream pool (`basic` ...) both work whether or
        # not the catalog indexes them
        directory = ROOT / group
        if directory.is_dir() and any(directory.glob("*.py")):
            paths = sorted(str(p) for p in directory.glob("*.py"))
    specs = manifest_specs(paths) if paths is not None else catalog.specs(channel)
    for spec in specs:
        if not spec.supported:
            continue
        if group not in (None, "all") and spec.entry["group"] != group:
            continue
        if operators is not None and spec.source not in operators:
            continue
        module = spec.load()
        shapes = getattr(module, "SHAPES", [])
        dtypes = getattr(module, "DTYPES", [])
        for shape in shapes:
            for dtype in dtypes:
                yield spec, _to_list(shape), dtype


class CaseMemoryLimit(Exception):
    """One case's resident set exceeded ``--case-memory-mb``.  Raised from the
    watchdog thread through SIGUSR1 (the same "interrupt at the next bytecode
    boundary" trick as the deadline), recorded as status OOM."""


def _rss_bytes() -> int | None:
    """Current resident set size of this process (bytes), or None."""
    try:
        with open("/proc/self/statm", "r", encoding="ascii") as fh:
            fields = fh.read().split()
        return int(fields[1]) * os.sysconf("SC_PAGE_SIZE")
    except (OSError, ValueError, IndexError):
        return None


class _MemoryWatchdog:
    """Polls this process's RSS and trips the case when it crosses the cap.

    A polling watchdog (not an rlimit) is what works next to a GPU driver: the
    CUDA context reserves tens of GiB of address space, so RLIMIT_AS cannot
    distinguish that reservation from a runaway allocation, while RSS is what
    the OOM killer actually looks at.  The poll interval bounds the overshoot
    to roughly (interval x allocation rate) and the breach interrupts the
    main thread at its next bytecode boundary.
    """

    def __init__(self, interval: float = 0.02):
        self.interval = interval
        self.limit: int | None = None
        self.peak = 0
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, name="rss-watchdog",
                                        daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while not self._stop.is_set():
            limit = self.limit
            if limit:
                rss = _rss_bytes()
                if rss is not None:
                    self.peak = max(self.peak, rss)
                    if rss > limit:
                        self.limit = None            # trip once per case
                        try:
                            signal.pthread_kill(threading.main_thread().ident,
                                                signal.SIGUSR1)
                        except (AttributeError, OSError, ValueError):
                            pass
            time.sleep(self.interval)


_WATCHDOG = _MemoryWatchdog()
_RSS_LIMIT_MB: float | None = None


def _raise_memory(signum, frame):
    raise CaseMemoryLimit("resident set exceeded the case cap")


class CaseTimeout(Exception):
    """A single case exceeded its wall-clock budget (SIGALRM from
    ``--case-timeout``).  Recorded as status TIMEOUT so a slow case cannot
    hold the whole sweep hostage."""


@contextlib.contextmanager
def _case_deadline(seconds: float | None):
    """Per-case watchdog.  SIGALRM only works in the main thread, which is
    where ``run_all`` runs (``--jobs`` fans out into subprocesses)."""
    if not seconds:
        yield
        return
    previous = signal.signal(signal.SIGALRM, _raise_timeout)
    signal.setitimer(signal.ITIMER_REAL, float(seconds))
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def _raise_timeout(signum, frame):
    raise CaseTimeout(f"exceeded {signal.getitimer(signal.ITIMER_REAL)[0]:.1f}s")


def _proc_status_kb(field: str) -> float | None:
    """One ``/proc/self/status`` size field in KiB (None when unavailable)."""
    try:
        with open("/proc/self/status", "r", encoding="ascii", errors="replace") as fh:
            for line in fh:
                if line.startswith(field + ":"):
                    return float(line.split()[1])
    except OSError:
        pass
    return None


def _peak_rss_mb() -> float | None:
    """Peak RSS of this process so far (monotone; KiB on Linux)."""
    try:
        import resource
        return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)
    except (ImportError, OSError, ValueError):
        return None


_MEM_CAP_WARNED = False
_MEM_CAP_MB: float | None = None


class CaseResourceScope:
    """Per-case resource caps.

    Two independent mechanisms, because they fail differently:

    - ``memory_mb`` — an **RSS ceiling** enforced by a polling watchdog thread.
      This is the one that works next to a GPU driver: a CUDA context maps tens
      of GiB of *virtual* space, so ``RLIMIT_AS`` cannot tell the driver's
      reservation from a runaway allocation, while RSS is what the kernel's OOM
      killer actually watches.  A breach interrupts the main thread (SIGUSR1)
      and becomes one OOM row.
    - ``cpu_seconds`` — ``RLIMIT_CPU``, kernel enforced.  The backstop for
      ``--case-timeout``, whose SIGALRM cannot fire while one C call runs.
    - ``address_space_mb`` — ``RLIMIT_AS``, opt-in, for pure-CPU workers with no
      GPU context (it is the only mechanism that also caps mmap'd bookkeeping).

    Only soft limits are lowered, and they are restored after the case, so the
    process gets its headroom back.
    """

    SLACK_BYTES = 256 << 20

    def __init__(self, memory_mb: float | None = None,
                 cpu_seconds: float | None = None,
                 address_space_mb: float | None = None):
        self.memory_mb = memory_mb
        self.cpu_seconds = cpu_seconds
        self.address_space_mb = address_space_mb
        self.memory_bytes: int | None = None
        self._saved: list[tuple[int, tuple[float, float]]] = []
        self._previous_sigusr1 = None

    # -- enter/exit ---------------------------------------------------------

    def __enter__(self) -> "CaseResourceScope":
        global _MEM_CAP_MB, _RSS_LIMIT_MB
        if self.memory_mb:
            _WATCHDOG.start()
            _RSS_LIMIT_MB = float(self.memory_mb)
            self._previous_sigusr1 = signal.signal(signal.SIGUSR1, _raise_memory)
            _MEM_CAP_MB = round(float(self.memory_mb), 1)
            _WATCHDOG.limit = int(self.memory_mb * (1 << 20))
        if self.address_space_mb:
            self._enter_address_space()
        if self.cpu_seconds:
            self._enter_cpu()
        return self

    def __exit__(self, *exc) -> None:
        import resource
        global _MEM_CAP_MB, _RSS_LIMIT_MB
        if self.memory_mb:
            _WATCHDOG.limit = None
            _RSS_LIMIT_MB = None
            _MEM_CAP_MB = None
            if self._previous_sigusr1 is not None:
                signal.signal(signal.SIGUSR1, self._previous_sigusr1)
                self._previous_sigusr1 = None
        for which, (soft, hard) in reversed(self._saved):
            try:
                resource.setrlimit(which, (soft, hard))
            except (ValueError, OSError):
                pass                       # never mask the case's own failure
        self._saved = []

    # -- address space (opt-in) --------------------------------------------

    def _enter_address_space(self) -> None:
        import resource
        global _MEM_CAP_MB, _MEM_CAP_WARNED
        cap = int(self.address_space_mb * (1 << 20))
        used = _proc_status_kb("VmSize")
        if used is not None:
            floor = int((used * 1024) * 1.25) + self.SLACK_BYTES
            if floor > cap:
                if not _MEM_CAP_WARNED:
                    _MEM_CAP_WARNED = True
                    import warnings
                    warnings.warn(
                        f"--case-address-space-mb {self.address_space_mb:g} is "
                        f"below this process's current address space "
                        f"({used / 1024:.0f} MiB); the effective cap is "
                        f"{floor / (1 << 20):.0f} MiB.  With a CUDA context use "
                        f"--case-memory-mb (RSS) instead: the driver reserves "
                        f"the address space, not the memory",
                        RuntimeWarning, stacklevel=3)
                cap = floor
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        if hard != resource.RLIM_INFINITY:
            cap = min(cap, hard)
        if soft == resource.RLIM_INFINITY or cap < soft:
            resource.setrlimit(resource.RLIMIT_AS, (cap, hard))
            self._saved.append((resource.RLIMIT_AS, (soft, hard)))
            self.memory_bytes = cap
            _MEM_CAP_MB = round(cap / (1 << 20), 1)

    # -- CPU seconds --------------------------------------------------------

    def _enter_cpu(self) -> None:
        import resource
        seconds = max(1, int(self.cpu_seconds))
        soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
        cap = seconds if hard == resource.RLIM_INFINITY else min(seconds, hard)
        if soft == resource.RLIM_INFINITY or cap < soft:
            resource.setrlimit(resource.RLIMIT_CPU, (cap, hard))
            self._saved.append((resource.RLIMIT_CPU, (soft, hard)))


def row_key(row_or_tuple):
    """Stable identity of a case: (operator source, shape, dtype)."""
    if isinstance(row_or_tuple, dict):
        return (row_or_tuple["operator"], tuple(row_or_tuple["shape"]),
                str(row_or_tuple["dtype"]))
    return row_or_tuple


def load_done_keys(journal, *, retry_failed: bool = False) -> set:
    """Keys already recorded in an append-only journal (for ``--resume``).

    A truncated last line (killed mid-write) is ignored rather than fatal.
    ``retry_failed`` re-runs everything that did not PASS.
    """
    done = set()
    path = Path(journal)
    if not path.is_file():
        return done
    for line in path.read_text(errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
            key = row_key(row)
        except Exception:                      # noqa: BLE001 - torn last line
            continue
        if retry_failed and row.get("status") != "PASS":
            continue
        done.add(key)
    return done


def _write_heartbeat(path, *, done: int, total: int, current: str,
                     started: float, status: str = "running"):
    """Cheap progress file so a human/watchdog can tell "alive" from "hung".

    Carries the current and peak RSS plus the effective memory cap, so a
    memory blow-up is visible *before* the OOM killer acts.
    """
    if not path:
        return
    now = time.time()
    elapsed = now - started
    rate = done / elapsed if done and elapsed > 0 else 0.0
    rss = _rss_bytes()
    payload = {"status": status, "done": done, "total": total,
               "percent": round(100.0 * done / total, 1) if total else None,
               "current": current, "elapsed_s": round(elapsed, 1),
               "eta_s": round((total - done) / rate, 1) if rate else None,
               "rss_mb": round(rss / (1 << 20), 1) if rss else _peak_rss_mb(),
               "peak_rss_mb": _peak_rss_mb(), "mem_cap_mb": _MEM_CAP_MB,
               "updated": now, "pid": os.getpid()}
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload))
        os.replace(tmp, path)                  # atomic: readers never see half
    except OSError:
        pass                                   # progress must never break a run


def run_all(device, channel: str = "all", seed: int = 30, limit: int | None = None,
            group: str | None = None, use_golden: bool = True,
            operators: set[str] | None = None, paths: list[str] | None = None,
            shard: tuple[int, int] | None = None,
            journal: str | None = None, resume_keys: set | None = None,
            compile_budget: float | None = None,
            identity_tier: str = "meta",
            case_timeout: float | None = None, max_failures: int | None = None,
            heartbeat: str | None = None, progress_every: int = 0,
            case_memory_mb: float | None = None,
            case_cpu_seconds: float | None = None,
            case_address_space_mb: float | None = None,
            oom_abort: bool = False):
    """Run every case through ``device``; return one row per case.

    Each row: ``{operator, group, shape, dtype, status, detail, seconds}``
    where status is PASS / CASE_FAIL / LAUNCH_FAIL / MISMATCH / TIMEOUT.
    Cases (inputs and expected outputs) come from the golden cache when
    possible.  ``shard=(i, n)`` keeps only cases whose stable enumeration
    index is ``i mod n``.

    Kill safety / observability (all optional, all off by default):

    - ``journal``: append one flushed JSON line per finished case, so a
      killed process loses at most one case; ``resume_keys`` (from
      :func:`load_done_keys`) skips the ones already recorded.
    - ``case_timeout``: per-case wall-clock budget; overruns become a
      TIMEOUT row instead of stalling the sweep.
    - ``max_failures``: stop after this many non-PASS rows (fail fast on a
      sweep that is failing everywhere); unrun cases simply stay unjournaled
      and ``--resume`` picks them up later.
    - ``heartbeat`` / ``progress_every``: atomic status file + progress lines.
    - ``case_memory_mb`` / ``case_cpu_seconds``: kernel-enforced rlimits for
      one case (address space, CPU seconds).  A cap breach is an OOM row
      (``MemoryError``) or a SIGXCPU kill rather than an unbounded blow-up;
      ``oom_abort`` stops the sweep on the first OOM instead of continuing.
    """
    cases = list(enumerate_cases(channel, group, operators, paths))
    total = sum(1 for index, _ in enumerate(cases)
                if shard is None or index % shard[1] == shard[0])
    if limit is not None:
        total = min(total, limit)
    rows: list[dict] = []
    failures = 0
    skipped = 0
    seen_identities: set[str] = set()
    started = time.time()
    stream = None
    if journal:
        path = Path(journal)
        path.parent.mkdir(parents=True, exist_ok=True)
        stream = open(path, "a", encoding="utf-8", buffering=1)   # line buffered
    _write_heartbeat(heartbeat, done=0, total=total, current="", started=started)

    def record(row: dict) -> bool:
        """Journal + progress for one finished case; True means keep going."""
        nonlocal failures
        rows.append(row)
        if stream is not None:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        if row["status"] != "PASS":
            failures += 1
        done = len(rows) + skipped
        if progress_every and done % progress_every == 0:
            print(f"[{done}/{total}] {row['operator']} {row['shape']} "
                  f"{row['dtype']} {row['status']}", flush=True)
        _write_heartbeat(heartbeat, done=done, total=total,
                         current=f"{row['operator']} {row['shape']} {row['dtype']} "
                                 f"{row['status']}", started=started)
        return max_failures is None or failures < max_failures

    try:
        for index, (spec, shape, dtype) in enumerate(cases):
            if shard is not None and index % shard[1] != shard[0]:
                continue
            if limit is not None and len(rows) >= limit:
                break
            key = row_key({"operator": spec.source, "shape": list(shape),
                           "dtype": str(dtype)})
            base = {"operator": spec.source, "group": spec.entry["group"],
                    "shape": list(shape), "dtype": str(dtype)}
            if resume_keys and key in resume_keys:
                skipped += 1
                continue
            began = time.perf_counter()
            scope = CaseResourceScope(case_memory_mb, case_cpu_seconds,
                                      case_address_space_mb)
            try:
                with _case_deadline(case_timeout), scope:
                    case = golden.load_or_build_spec(
                        spec, shape=shape, dtype=dtype, seed=seed, use_cache=use_golden)
            except CaseTimeout:
                if not record({**base, "status": "TIMEOUT", "detail": "case build",
                               "seconds": round(time.perf_counter() - began, 3)}):
                    break
                continue
            except (MemoryError, CaseMemoryLimit):
                if not record({**base, "status": "OOM",
                               "detail": f"case build exceeded memory cap "
                                         f"({case_memory_mb:g} MiB)" if case_memory_mb
                                         else "case build ran out of memory",
                               "rss_mb": _peak_rss_mb(),
                               "seconds": round(time.perf_counter() - began, 3)}):
                    break
                if oom_abort:
                    break
                continue
            except Exception as exc:  # noqa: BLE001 - a broken case is data
                if not record({**base, "status": "CASE_FAIL",
                               "detail": f"{type(exc).__name__}: {exc}",
                               "seconds": round(time.perf_counter() - began, 3)}):
                    break
                continue
            ident = identity_lib.case_identity(spec.source, case, identity_tier)
            base["identity"] = ident
            first_of_identity = ident not in seen_identities
            try:
                with _case_deadline(case_timeout), scope:
                    staged = stage_case(case, device)
                    launch_began = time.perf_counter()
                    staged.launch()
                    launch_seconds = time.perf_counter() - launch_began
            except CaseTimeout:
                if not record({**base, "status": "TIMEOUT", "detail": "launch",
                               "seconds": round(time.perf_counter() - began, 3)}):
                    break
                continue
            except (MemoryError, CaseMemoryLimit):
                if not record({**base, "status": "OOM",
                               "detail": f"compile/launch exceeded memory cap "
                                         f"({case_memory_mb:g} MiB)" if case_memory_mb
                                         else "compile/launch ran out of memory",
                               "rss_mb": _peak_rss_mb(),
                               "seconds": round(time.perf_counter() - began, 3)}):
                    break
                if oom_abort:
                    break
                continue
            except Exception as exc:  # noqa: BLE001
                if not record({**base, "status": "LAUNCH_FAIL",
                               "detail": f"{type(exc).__name__}: {exc}",
                               "seconds": round(time.perf_counter() - began, 3)}):
                    break
                continue
            seen_identities.add(ident)
            if compile_budget is not None and first_of_identity \
                    and launch_seconds > compile_budget:
                if not record({**base, "status": "COMPILE_BUDGET_EXCEEDED",
                               "detail": (f"first compile of identity {ident} took "
                                          f"{launch_seconds:.2f}s > budget "
                                          f"{compile_budget:g}s"),
                               "launch_seconds": round(launch_seconds, 3),
                               "seconds": round(time.perf_counter() - began, 3)}):
                    break
                continue
            try:
                with _case_deadline(case_timeout), scope:
                    verdict = compare_lib.compare_case_on_device(staged, case, device)
                    if verdict is None:
                        verdict = compare_lib.compare_case(case, staged.outputs())
                    del verdict
                keep_going = record({**base, "status": "PASS", "detail": "",
                                     "rss_mb": _peak_rss_mb(),
                                     "launch_seconds": round(launch_seconds, 3),
                                     "seconds": round(time.perf_counter() - began, 3)})
            except CaseTimeout:
                keep_going = record({**base, "status": "TIMEOUT", "detail": "compare",
                                     "seconds": round(time.perf_counter() - began, 3)})
            except Exception as exc:  # noqa: BLE001
                keep_going = record({**base, "status": "MISMATCH",
                                     "detail": str(exc).splitlines()[0][:200],
                                     "seconds": round(time.perf_counter() - began, 3)})
            if not keep_going:
                print(f"[abort] {failures} failing cases recorded; "
                      f"rerun with --resume after fixing", file=sys.stderr)
                break
    finally:
        if stream is not None:
            stream.close()
        _write_heartbeat(heartbeat, done=len(rows) + skipped, total=total,
                         current="done", started=started,
                         status="aborted" if max_failures is not None and failures >= max_failures
                         else "finished")
    return rows


def summarize(rows):
    counts = Counter(row["status"] for row in rows)
    return dict(sorted(counts.items()))


def dry_run_rows(channel, group, operators=None, paths=None):
    return [{"operator": spec.source, "group": spec.entry["group"],
             "shape": list(shape), "dtype": str(dtype)}
            for spec, shape, dtype in enumerate_cases(channel, group, operators, paths)]


def identity_entries(channel, group, operators=None, seed: int = 30,
                     use_golden: bool = True, paths=None):
    """Cases with their built ``case`` dict, for identity accounting.

    Only ``make_case`` runs here -- nothing is compiled, so this is safe to
    call on a machine without the compiler or a GPU.
    """
    entries = []
    for spec, shape, dtype in enumerate_cases(channel, group, operators, paths):
        case = golden.load_or_build_spec(spec, shape=shape, dtype=dtype,
                                         seed=seed, use_cache=use_golden)
        entries.append({"operator": spec.source, "group": spec.entry["group"],
                        "shape": list(shape), "dtype": str(dtype),
                        "kernel": identity_lib.kernel_name(case), "case": case})
    return entries


def _enumeration_order(channel, group, operators=None):
    """Stable (operator, shape, dtype) key order, for merging shard reports."""
    return [(r["operator"], tuple(r["shape"]), r["dtype"])
            for r in dry_run_rows(channel, group, operators)]


def _run_jobs(args) -> list[dict]:
    """Fan the run out to N subprocesses (one --shard each) and merge."""
    forward = [sys.executable, str(Path(__file__).resolve()),
               "--channel", args.channel, "--device", args.device,
               "--seed", str(args.seed)]
    if args.no_golden:
        forward.append("--no-golden")
    if args.case_timeout:
        forward += ["--case-timeout", str(args.case_timeout)]
    if args.case_memory_mb:
        forward += ["--case-memory-mb", str(args.case_memory_mb)]
    if args.case_cpu_seconds:
        forward += ["--case-cpu-seconds", str(args.case_cpu_seconds)]
    if args.case_address_space_mb:
        forward += ["--case-address-space-mb", str(args.case_address_space_mb)]
    if args.oom_abort:
        forward.append("--oom-abort")
    if args.allow_torch:
        forward.append("--allow-torch")
    if args.max_failures:
        forward += ["--max-failures", str(args.max_failures)]
    if args.compile_budget:
        forward += ["--compile-budget", str(args.compile_budget)]
    if args.progress_every:
        forward += ["--progress-every", str(args.progress_every)]
    if args.group:
        forward += ["--group", args.group]
    if args.manifest:
        forward += ["--manifest", args.manifest]
    for op in args.operator or []:
        forward += ["--operator", op]
    gpus = [g.strip() for g in (args.gpus or "").split(",") if g.strip()]
    merged = []
    with tempfile.TemporaryDirectory(prefix="ops-shards-") as tmp:
        reports, running = [], []
        for i in range(args.jobs):
            report = Path(tmp) / f"shard-{i}.json"
            cmd = forward + ["--shard", f"{i}/{args.jobs}", "--report", str(report)]
            if args.journal:
                # 每个 shard 自己的 journal:shard 索引与枚举索引都稳定,
                # 所以 --resume 对每个 shard 也是精确的。
                cmd += ["--journal", f"{args.journal}.shard-{i}"]
            if args.resume:
                cmd.append("--resume")
            if args.retry_failed:
                cmd.append("--retry-failed")
            if args.heartbeat:
                cmd += ["--heartbeat", f"{args.heartbeat}.shard-{i}"]
            env = dict(os.environ)
            if gpus:
                env["CUDA_VISIBLE_DEVICES"] = gpus[i % len(gpus)]
            running.append(subprocess.Popen(cmd, env=env, text=True,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE))
            reports.append(report)
        for proc in running:                 # all shards run concurrently
            out, err = proc.communicate()
            if proc.returncode != 0:
                print(out[-2000:], file=sys.stderr)
                print(err[-2000:], file=sys.stderr)
                raise SystemExit(proc.returncode)
        for report in reports:
            if report.is_file():
                merged.extend(json.loads(report.read_text()))
    # restore the unsharded enumeration order
    order = {key: n for n, key in enumerate(_enumeration_order(
        args.channel, args.group, _resolve_operator_paths(args.operator) if args.operator else None))}
    merged.sort(key=lambda r: order.get(
        (r["operator"], tuple(r["shape"]), r["dtype"]), len(order)))
    if args.journal:
        path = Path(args.journal)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as stream:
            for row in merged:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    return merged


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--channel", default="all")
    parser.add_argument("--group", default=None,
                        help="one directory: basic|medium|hard|bench")
    parser.add_argument("--group-order", action="store_true",
                        help="process each directory in order, printing a per-group summary")
    parser.add_argument("--device", default="cpu",
                        help="cpu | cuda | torch-gpu | torch-cpu | module:factory")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--identities", action="store_true",
                        help="with --dry-run: print the compilation-identity census "
                             "(cases vs compiles); pairs with --schedule")
    parser.add_argument("--schedule", metavar="PATH",
                        help="write the per-identity work list a parallel driver "
                             "consumes (needs --identities)")
    parser.add_argument("--identity-tier", default="meta",
                        choices=list(identity_lib.TIERS),
                        help="identity granularity (default: meta)")
    parser.add_argument("--compile-budget", type=float, metavar="SEC",
                        help="per-identity compile budget: the first launch of an "
                             "identity is its compile; over budget becomes a "
                             "COMPILE_BUDGET_EXCEEDED row")
    parser.add_argument("--seed", type=int, default=30)
    parser.add_argument("--no-golden", action="store_true",
                        help="always rebuild cases with make_case (no disk cache)")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--report")
    parser.add_argument("--manifest", metavar="PATH",
                        help="run exactly the operators listed in a suite manifest "
                             "(suite/manifest.json), bypassing the catalog")
    parser.add_argument("--operator", action="append",
                        help="restrict to this operator file (repeatable)")
    parser.add_argument("--shard", metavar="I/N",
                        help="keep only cases whose index is I mod N")
    parser.add_argument("--jobs", type=int,
                        help="run N subprocesses (one shard each) and merge the reports")
    parser.add_argument("--gpus", default="",
                        help="with --jobs: comma-separated GPU ids, shard i "
                             "runs with CUDA_VISIBLE_DEVICES=gpus[i %% len]")
    parser.add_argument("--journal", metavar="PATH",
                        help="append one JSON line per finished case (kill-safe)")
    parser.add_argument("--resume", action="store_true",
                        help="skip cases already recorded in --journal")
    parser.add_argument("--retry-failed", action="store_true",
                        help="with --resume: also re-run cases that did not PASS")
    parser.add_argument("--case-timeout", type=float, metavar="SEC",
                        help="per-case wall-clock budget (overrun -> TIMEOUT row)")
    parser.add_argument("--case-memory-mb", type=float, metavar="MB",
                        help="per-case RSS ceiling (polling watchdog): a huge "
                             "PTX / runaway allocation becomes one OOM row "
                             "instead of OOM-killing the sweep.  Works next to "
                             "a CUDA context, unlike RLIMIT_AS")
    parser.add_argument("--case-address-space-mb", type=float, metavar="MB",
                        help="per-case RLIMIT_AS (only meaningful for CPU-only "
                             "workers: a CUDA context reserves the address space)")
    parser.add_argument("--case-cpu-seconds", type=float, metavar="SEC",
                        help="per-case CPU-time cap (RLIMIT_CPU, kernel "
                             "enforced; backstop for --case-timeout)")
    parser.add_argument("--oom-abort", action="store_true",
                        help="stop the sweep at the first OOM row")
    parser.add_argument("--max-failures", type=int, metavar="N",
                        help="stop the sweep after N non-PASS rows")
    parser.add_argument("--heartbeat", metavar="PATH",
                        help="atomically written progress file (for watchdogs)")
    parser.add_argument("--progress-every", type=int, default=0, metavar="N",
                        help="print a progress line every N finished cases")
    parser.add_argument("--block-torch", action="store_true",
                        help="force the torch meta-path blocker on (default for non-torch devices)")
    parser.add_argument("--allow-torch", action="store_true",
                        help="disable the torch meta-path blocker")
    args = parser.parse_args()

    global _TORCH_BLOCKED
    if args.block_torch and not _TORCH_BLOCKED:
        _TORCH_BLOCKED = _install_blocker()
    if args.allow_torch and _TORCH_BLOCKED:
        for finder in sys.meta_path:
            if isinstance(finder, _TorchBlocker):
                sys.meta_path.remove(finder)
        _TORCH_BLOCKED = False

    operators = _resolve_operator_paths(args.operator) if args.operator else None
    shard = None
    if args.shard:
        try:
            i, n = args.shard.split("/")
            shard = (int(i), int(n))
            assert 0 <= shard[0] < shard[1]
        except Exception:
            parser.error("--shard expects I/N with 0 <= I < N")

    paths = cases_from_manifest(args.manifest) if args.manifest else None
    if paths is not None and operators:
        parser.error("--manifest cannot be combined with --operator")

    if args.dry_run:
        total = 0
        if paths is not None:              # explicit suite manifest: one flat pass
            rows = dry_run_rows(args.channel, args.group, operators, paths)
            total += len(rows)
            print(f"{'manifest':12s} operators={len({r['operator'] for r in rows}):4d} "
                  f"cases={len(rows)}")
            if args.report:
                Path(args.report + ".manifest").write_text(json.dumps(rows, indent=2) + "\n")
            groups = ()
        else:
            groups = GROUP_ORDER if args.group_order else (args.group,)
            for group in groups:
                rows = dry_run_rows(args.channel, group, operators)
                total += len(rows)
                print(f"{group or 'all':12s} operators={len({r['operator'] for r in rows}):4d} cases={len(rows)}")
                if args.report:
                    suffix = f".{group}" if group else ""
                    Path(args.report + suffix).write_text(json.dumps(rows, indent=2) + "\n")
        print(f"{'TOTAL':12s} cases={total}")
        if args.identities and paths is not None:
            entries = identity_entries(args.channel, None, operators,
                                       seed=args.seed,
                                       use_golden=not args.no_golden, paths=paths)
            report = identity_lib.identity_census(entries, tiers=("dtype", "triton", "meta"))
            print()
            print(identity_lib.format_census(report))
            if args.schedule:
                schedule = identity_lib.build_schedule(entries, tier=args.identity_tier)
                Path(args.schedule).parent.mkdir(parents=True, exist_ok=True)
                Path(args.schedule).write_text(json.dumps(schedule, indent=2) + "\n")
                print(f"\nschedule -> {args.schedule} ({schedule['identities']} identities, "
                      f"{schedule['cases']} cases)")
            return
        if args.identities:
            entries = []
            for group in groups:
                entries.extend(identity_entries(args.channel, group, operators,
                                                seed=args.seed,
                                                use_golden=not args.no_golden))
            report = identity_lib.identity_census(entries, tiers=("dtype", "triton", "meta"))
            print()
            print(identity_lib.format_census(report))
            if args.report:
                Path(args.report + ".identities.json").write_text(
                    json.dumps({k: v for k, v in report.items()}, indent=2) + "\n")
            if args.schedule:
                schedule = identity_lib.build_schedule(entries, tier=args.identity_tier)
                Path(args.schedule).parent.mkdir(parents=True, exist_ok=True)
                Path(args.schedule).write_text(json.dumps(schedule, indent=2) + "\n")
                print(f"\nschedule -> {args.schedule} "
                      f"({schedule['identities']} identities, {schedule['cases']} cases)")
        return

    resume_keys = None
    if args.resume:
        if not args.journal:
            parser.error("--resume needs --journal")
        resume_keys = load_done_keys(args.journal, retry_failed=args.retry_failed)

    if args.jobs:
        if args.group_order:
            parser.error("--jobs does not combine with --group-order")
        rows = _run_jobs(args)
        print(json.dumps({"summary": summarize(rows), "total": len(rows)}, indent=2))
        for row in rows:
            if row["status"] != "PASS":
                print(f"{row['status']:12s} {row['operator']} {row['shape']} {row['dtype']} :: {row['detail']}")
        if args.report:
            Path(args.report).write_text(json.dumps(rows, indent=2) + "\n")
        return

    device = make_device(args.device)
    if args.group_order:
        all_rows = []
        for group in GROUP_ORDER:
            rows = run_all(device, channel=args.channel, seed=args.seed, group=group,
                           use_golden=not args.no_golden, operators=operators,
                           journal=args.journal,
                           resume_keys=resume_keys,
                           compile_budget=args.compile_budget,
                           identity_tier=args.identity_tier,
                           case_timeout=args.case_timeout,
                           max_failures=args.max_failures,
                           heartbeat=args.heartbeat,
                           progress_every=args.progress_every,
                           case_memory_mb=args.case_memory_mb,
                           case_cpu_seconds=args.case_cpu_seconds,
                           case_address_space_mb=args.case_address_space_mb,
                           oom_abort=args.oom_abort)
            all_rows.extend(rows)
            print(f"{group:12s} {summarize(rows)}")
        print(json.dumps({"summary": summarize(all_rows), "total": len(all_rows)}, indent=2))
        rows = all_rows
    else:
        rows = run_all(device, channel=args.channel, seed=args.seed,
                       limit=args.limit, group=args.group,
                       use_golden=not args.no_golden, operators=operators,
                       paths=paths,
                       shard=shard, journal=args.journal, resume_keys=resume_keys,
                       compile_budget=args.compile_budget,
                       identity_tier=args.identity_tier,
                       case_timeout=args.case_timeout,
                       max_failures=args.max_failures,
                       heartbeat=args.heartbeat,
                       progress_every=args.progress_every,
                       case_memory_mb=args.case_memory_mb,
                       case_cpu_seconds=args.case_cpu_seconds,
                       case_address_space_mb=args.case_address_space_mb,
                       oom_abort=args.oom_abort)
        print(json.dumps({"summary": summarize(rows), "total": len(rows)}, indent=2))
    for row in rows:
        if row["status"] != "PASS":
            print(f"{row['status']:12s} {row['operator']} {row['shape']} {row['dtype']} :: {row['detail']}")
    if args.report:
        Path(args.report).write_text(json.dumps(rows, indent=2) + "\n")


if __name__ == "__main__":
    main()
