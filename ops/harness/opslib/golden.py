"""Disk cache for golden cases: inputs and expected outputs keyed by content.

``(operator file bytes, shape, dtype, seed)`` fully determines a case's inputs
and expected outputs, so they are computed once and cached on disk instead of
being regenerated (minutes for the slow refs and RNG at steady-state shapes)
by every driver, verifier and baseline script.

Layout (one immutable directory per key, written atomically via a temp
directory + ``os.replace``)::

    <cache>/<ab>/<digest>/
        meta.json          # sanitized non-array fields, array index, provenance
        args.<name>.npy    # uncompressed .npy, one file per persisted array
        allocations.<name>.npy
        expected.<name>.npy
        oracle_args.<name>.npy

On a hit, arrays are memory-mapped (``np.load(..., mmap_mode="r")``), so a
warm run touches the page cache instead of regenerating gigabytes.  Output
buffers that are all zeros are not persisted; they are re-created with
``np.zeros``.  The kernel object (and everything else that is not data) is
re-acquired from the imported operator module.

Cases the format cannot represent faithfully are simply not cached and fall
back to ``make_case`` every time:

  - callable ``grid`` (autotune-dependent, 13 operators today);
  - ``torch_function`` / ``rng_*`` markers (no such operators today);
  - ``meta`` values that are not plain scalars (e.g. ``tl.float32`` constexprs);
  - arrays outside the four array sections, or payloads that do not survive
    the JSON round-trip;
  - cases larger than ``OPS_GOLDEN_MAX_BYTES`` (default 4 GiB) so a
    pathological shape cannot fill the disk.

CLI::

    python3 -m opslib golden --prune     # drop entries whose operator file changed
    python3 -m opslib golden --stats     # size / entry counts

The key covers the operator file *and* the shared case-building code
(``opslib/case.py``, ``opslib/mathref.py``), so changing a tolerance
policy or a math ref invalidates cached cases.  The total cache size is
capped (``OPS_GOLDEN_MAX_TOTAL``, default 64 GiB) with least-recently-used
eviction; store failures are counted and warned about, never silent.

Environment: ``OPS_GOLDEN_DIR`` (default ``~/.cache/ops-golden``),
``OPS_GOLDEN_MAX_BYTES`` (per case), ``OPS_GOLDEN_MAX_TOTAL`` (whole
cache), ``OPS_GOLDEN=0`` to disable caching globally.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import os
import shutil
import tempfile
from pathlib import Path

import numpy as np

FORMAT_VERSION = 2
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "ops-golden"
_DEFAULT_MAX_BYTES = 4 << 30
_DEFAULT_MAX_TOTAL = 64 << 30
_ARRAY_SECTIONS = ("args", "allocations", "expected", "oracle_args")
# Arrays up to this size are copied eagerly on load (writable, no mmap
# warnings in downstream torch.from_numpy); larger ones stay mmap'd.
_COPY_THRESHOLD = 16 << 20
# Eviction walks the cache directory; the walk is amortized: it always
# runs on a process's first store (short runs like --limit 3 must not grow
# the cache unbounded), then after every _EVICT_CHECK_BYTES of new data
# (or _EVICT_CHECK_STORES stores, for many small entries).
_EVICT_CHECK_BYTES = 4 << 30
_EVICT_CHECK_STORES = 64
_EVICTION = {"stores": 0, "bytes": 0, "checked": False}
_STORE_FAILURES = 0


def cache_enabled() -> bool:
    return os.environ.get("OPS_GOLDEN", "1") not in {"0", "false", "no"}


def cache_dir(explicit: str | os.PathLike | None = None) -> Path:
    if explicit is not None:
        return Path(explicit)
    env = os.environ.get("OPS_GOLDEN_DIR")
    return Path(env) if env else DEFAULT_CACHE_DIR


def max_total_bytes() -> int:
    """Total cache-size cap; entries are evicted least-recently-used
    first once it is exceeded (``OPS_GOLDEN_MAX_TOTAL`` overrides)."""
    raw = os.environ.get("OPS_GOLDEN_MAX_TOTAL")
    if raw is None:
        return _DEFAULT_MAX_TOTAL
    try:
        value = int(raw)
    except ValueError:
        raise ValueError(f"OPS_GOLDEN_MAX_TOTAL must be an integer, got {raw!r}")
    return value if value > 0 else 1 << 62


def max_bytes() -> int:
    raw = os.environ.get("OPS_GOLDEN_MAX_BYTES")
    if raw is None:
        return _DEFAULT_MAX_BYTES
    try:
        value = int(raw)
    except ValueError:
        raise ValueError(f"OPS_GOLDEN_MAX_BYTES must be an integer, got {raw!r}")
    return value if value > 0 else 1 << 62


def canon_dtype(dtype) -> str:
    if dtype is None:
        return "default"
    try:
        return np.dtype(dtype).name
    except TypeError:
        return str(dtype).rsplit(".", 1)[-1]


def canon_shape(shape) -> str:
    """Render any declared shape (flat tuples, and nested from/to pairs like
    reshape's ``((2, 3, 4), (6, 4))``) as a canonical key component."""
    if shape is None:
        return "default"
    return _render_shape(shape)


def _render_shape(value) -> str:
    if isinstance(value, (list, tuple)):
        return "(" + ",".join(_render_shape(item) for item in value) + ")"
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    return str(value)


def file_sha256(path: str | os.PathLike) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


_DEPENDENCY_SHAS: list[str] | None = None


def _dependency_shas() -> list[str]:
    """Content hashes of the shared code that shapes cached cases.

    157 operators build their cases through ``opslib/case.py``
    (``public_make_case``: tolerance and default policies) and the slow
    math refs go through ``opslib/mathref.py``; changing either must
    invalidate cached expected values and tolerances.  Computed once per
    process, relative to this opslib copy (repository or export).
    """
    global _DEPENDENCY_SHAS
    if _DEPENDENCY_SHAS is None:
        package = Path(__file__).resolve().parent
        _DEPENDENCY_SHAS = [
            f"{name}={file_sha256(package / name)}"
            for name in ("case.py", "mathref.py")
            if (package / name).is_file()
        ]
    return _DEPENDENCY_SHAS


def entry_key(path: str | os.PathLike, shape, dtype, seed) -> str:
    """Cache key digest: operator file + shared case-building code + the
    requested case parameters."""
    payload = "|".join((
        f"v{FORMAT_VERSION}",
        file_sha256(path),
        *_dependency_shas(),
        canon_shape(shape),
        canon_dtype(dtype),
        "default" if seed is None else str(int(seed)),
    ))
    return hashlib.sha256(payload.encode()).hexdigest()


# ------------------------------------------------------------------ sanitize
def _sanitizable(value) -> bool:
    """True if a *leaf* value survives the JSON round-trip (allowing only the
    semantics-preserving np-scalar -> python-scalar conversion).  Compound
    values are checked by ``_deep_ok``."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return True
    if isinstance(value, np.generic):
        return isinstance(value.item(), (bool, int, float, str))
    return False


def _deep_ok(value) -> bool:
    if value is None or isinstance(value, (bool, int, float, str)):
        return True
    if isinstance(value, np.generic):
        return isinstance(value.item(), (bool, int, float, str))
    if isinstance(value, dict):
        return _deep_ok_dict(value)
    if isinstance(value, (list, tuple)):
        return all(_deep_ok(item) for item in value)
    return False


def _deep_ok_dict(value: dict) -> bool:
    return all(isinstance(k, str) and _deep_ok(v) for k, v in value.items())


def _sanitize(value):
    """Convert one sanitizable leaf to its JSON form."""
    if isinstance(value, np.generic):
        return value.item()
    return value


def _sanitize_deep(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {k: _sanitize_deep(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_sanitize_deep(v) for v in value]
    return value


# ------------------------------------------------------------------- kernel
def _kernel_target(kernel):
    """Unwrap Autotuner/Heuristics/JITFunction down to the Python function."""
    target = kernel
    for _ in range(8):
        if inspect.isfunction(target):
            return target
        nested = getattr(target, "fn", None)
        if nested is None or nested is target:
            return target
        target = nested
    return target


def _kernel_name(kernel):
    return getattr(_kernel_target(kernel), "__name__", None)


def find_kernel(module):
    """The module's single JIT kernel (or autotune wrapper), exactly as the
    runner's implicit-kernel discovery sees it."""
    kernels = [value for value in vars(module).values()
               if hasattr(value, "fn") and hasattr(value, "__getitem__")
               and getattr(value.fn, "__module__", None) == module.__name__]
    if len(kernels) != 1:
        return None
    return kernels[0]


# --------------------------------------------------------------- load/store
def _payload_from_case(case):
    """Split a case into (payload, arrays, zero_outputs); None if uncacheable.

    ``payload`` holds every non-array field; the array sections keep only
    their non-array values.  ``arrays`` maps ``section.name`` to ndarray.
    ``zero_outputs`` maps ``section.name`` to (shape, dtype-str) for all-zero
    output buffers that need no persistence.
    """
    payload = {}
    if "torch_function" in case or "rng_cpu" in case or "rng_cuda" in case:
        return None
    # Persisting arrays as independent .npy files destroys memory sharing:
    # a case whose buffers alias (an in-place kernel observing writes
    # through the other name) would read back as unrelated buffers and
    # silently compute on stale data.  Anything aliased -- actually shared
    # storage, or an `aliases` declaration -- is not cacheable at all.
    if case.get("aliases"):
        return None
    arrays_seen = []
    for section in _ARRAY_SECTIONS:
        values = case.get(section)
        if not isinstance(values, dict):
            continue
        arrays_seen.extend(value for value in values.values()
                           if isinstance(value, np.ndarray))
    for i, left in enumerate(arrays_seen):
        for right in arrays_seen[i + 1:]:
            if np.shares_memory(left, right):
                return None
    for key, value in case.items():
        if key == "kernel" or key in _ARRAY_SECTIONS:
            continue
        if key == "grid":
            if callable(value) or value is None:
                return None
            if not all(_deep_ok(v) for v in value):
                return None
            payload[key] = [_sanitize(v) for v in value]
            continue
        if key == "pointer_dtypes":
            if not _deep_ok_dict({str(k): str(v) for k, v in (value or {}).items()}):
                return None
            payload[key] = {str(k): str(v).rsplit(".", 1)[-1]
                            for k, v in (value or {}).items()}
            continue
        if key == "meta":
            # meta values reach the kernel launcher: only exact scalars.
            if not isinstance(value, dict) or not all(
                    _sanitizable(item) for item in value.values()):
                return None
            payload[key] = {k: _sanitize(v) for k, v in value.items()}
            continue
        if not _deep_ok(value):
            return None
        payload[key] = _sanitize_deep(value)

    outputs = set(case.get("outputs") or ())
    arrays = {}
    zero_outputs = {}
    total_bytes = 0
    for section in _ARRAY_SECTIONS:
        if section not in case:
            continue                     # preserve the exact section key set
        values = case[section]
        if values is None:
            payload[section] = None
            continue
        if not isinstance(values, dict):
            return None
        clean = {}
        for name, value in values.items():
            if isinstance(value, np.ndarray):
                key = f"{section}.{name}"
                if (section in ("args", "allocations") and name in outputs
                        and not value.any()):
                    zero_outputs[key] = (list(value.shape), value.dtype.str)
                    continue
                arrays[key] = value
                total_bytes += value.nbytes
            elif _sanitizable(value):
                clean[name] = _sanitize(value)
            else:
                return None
        payload[section] = clean
    if total_bytes > max_bytes():
        return None
    return payload, arrays, zero_outputs


def _case_from_payload(payload, arrays, zero_outputs, module, kernel_name):
    case = {k: v for k, v in payload.items()}
    if "outputs" in case:
        case["outputs"] = tuple(case["outputs"])
    if case.get("grid") is not None:
        case["grid"] = tuple(int(v) for v in case["grid"])
    kernel = find_kernel(module)
    if kernel is None:
        return None
    if kernel_name and _kernel_name(kernel) != kernel_name:
        return None
    case["kernel"] = kernel
    for section in _ARRAY_SECTIONS:
        if section not in case:
            continue
        values = case[section]
        case[section] = None if values is None else dict(values)
    for key, array in arrays.items():
        section, name = key.split(".", 1)
        case[section][name] = array
    for key, (shape, dtype_str) in zero_outputs.items():
        section, name = key.split(".", 1)
        case[section][name] = np.zeros(shape, dtype=np.dtype(dtype_str))
    return case


def _load_entry(directory: Path, module, path):
    """Read one cache entry; a case dict, or None on any problem."""
    try:
        record = json.loads((directory / "meta.json").read_text())
        if record.get("format") != FORMAT_VERSION:
            return None
        if record.get("operator_sha256") != file_sha256(path):
            return None
        arrays = {}
        for key in record["arrays"]:
            array = np.load(directory / f"{key}.npy", mmap_mode="r")
            if array.nbytes <= _COPY_THRESHOLD:
                array = np.array(array)  # small: eager writable copy
            arrays[key] = array
        _touch_last_used(directory, record)
        return _case_from_payload(record["case"], arrays, record["zeros"],
                                  module, record.get("kernel"))
    except Exception:  # noqa: BLE001 - any unreadable entry is just a miss
        return None


def _touch_last_used(directory: Path, record: dict, max_age: float = 3600.0):
    """Refresh the entry's LRU stamp, throttled to once per hour per entry
    (atomic rewrite; a lost race only costs a stale stamp)."""
    import time as _time
    now = _time.time()
    stamp = record.get("last_used") or record.get("created") or 0
    if now - stamp < max_age:
        return
    record["last_used"] = now
    try:
        tmp = directory / ".meta.tmp"
        tmp.write_text(json.dumps(record))
        os.replace(tmp, directory / "meta.json")
    except OSError:
        pass                                  # stamping is best effort


def _entry_bytes(entry: Path) -> int:
    return sum(f.stat().st_size for f in entry.iterdir() if f.is_file())


def _evict_over_cap(root: Path):
    """Evict least-recently-used entries until the cache is under its
    total-size cap (with hysteresis).  Never raises."""
    cap = max_total_bytes()
    try:
        shards = [d for d in root.iterdir() if d.is_dir()]
        entries = []
        total = 0
        for shard in shards:
            for entry in shard.iterdir():
                meta = entry / "meta.json"
                if not meta.is_file():
                    continue
                try:
                    record = json.loads(meta.read_text())
                    stamp = (record.get("last_used")
                             or record.get("created")
                             or meta.stat().st_mtime)
                except (OSError, ValueError):
                    stamp = 0
                size = _entry_bytes(entry)
                entries.append((stamp, entry, size))
                total += size
        if total <= cap:
            return 0
        removed = 0
        target = cap * 95 // 100
        for stamp, entry, size in sorted(entries):   # oldest first
            if total <= target:
                break
            shutil.rmtree(entry, ignore_errors=True)
            total -= size
            removed += 1
        return removed
    except OSError:
        return 0


def _store_entry(directory: Path, record: dict, arrays: dict) -> bool:
    """Atomically write one entry; best effort, never raises (failures are
    counted and warned about once per process instead of being silent)."""
    global _STORE_FAILURES
    import time as _time
    try:
        record = {**record, "created": _time.time()}
        directory.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
                prefix=".tmp-", dir=directory.parent) as tmp:
            tmp_path = Path(tmp)
            for key, array in arrays.items():
                np.save(tmp_path / f"{key}.npy", np.ascontiguousarray(array),
                        allow_pickle=False)
            (tmp_path / "meta.json").write_text(json.dumps(record))
            try:
                os.replace(tmp, directory)
            except OSError:
                # A stale or concurrently-created entry occupies the key.
                # Drop it and retry once; readers keep their open handles.
                shutil.rmtree(directory, ignore_errors=True)
                os.replace(tmp, directory)
        return True
    except OSError as exc:
        _STORE_FAILURES += 1
        if _STORE_FAILURES == 1:
            import warnings
            warnings.warn(f"golden cache write failed ({exc}); further "
                          "failures suppressed but counted",
                          RuntimeWarning, stacklevel=3)
        return False


def _maybe_evict(root: Path, stored_bytes: int):
    """Amortized eviction check: first store of the process, then every
    _EVICT_CHECK_BYTES written (or _EVICT_CHECK_STORES stores)."""
    state = _EVICTION
    state["stores"] += 1
    state["bytes"] += stored_bytes
    if (state["checked"] and state["bytes"] < _EVICT_CHECK_BYTES
            and state["stores"] < _EVICT_CHECK_STORES):
        return
    state["stores"] = 0
    state["bytes"] = 0
    state["checked"] = True
    _evict_over_cap(root)


def load_or_build(module, path, *, shape=None, dtype=None, seed=None,
                  cache: str | os.PathLike | None = None,
                  use_cache: bool = True, stats: dict | None = None):
    """Return the case for ``(module, shape, dtype, seed)`` from cache when
    possible.  ``module`` is the imported operator module, ``path`` its file.

    ``stats`` (optional dict) is updated with ``hit`` / ``miss`` / ``skip``.
    """
    path = Path(path)
    if not (use_cache and cache_enabled()):
        if stats is not None:
            stats["skip"] = stats.get("skip", 0) + 1
        return module.make_case(shape=shape, dtype=dtype, seed=seed)

    root = cache_dir(cache)
    digest = entry_key(path, shape, dtype, seed)
    directory = root / digest[:2] / digest

    if directory.is_dir():
        case = _load_entry(directory, module, path)
        if case is not None:
            if stats is not None:
                stats["hit"] = stats.get("hit", 0) + 1
            return case
        # unreadable or stale entry: rebuild and overwrite below

    case = module.make_case(shape=shape, dtype=dtype, seed=seed)
    split = _payload_from_case(case)
    if split is not None:
        payload, arrays, zero_outputs = split
        kernel = case.get("kernel") or find_kernel(module)
        record = {
            "format": FORMAT_VERSION,
            "operator": str(path),
            "operator_sha256": file_sha256(path),
            "shape": canon_shape(shape),
            "dtype": canon_dtype(dtype),
            "seed": "default" if seed is None else int(seed),
            "kernel": _kernel_name(kernel) if kernel is not None else None,
            "arrays": sorted(arrays),
            "zeros": zero_outputs,
            "case": payload,
        }
        if _store_entry(directory, record, arrays):
            _maybe_evict(root, sum(array.nbytes for array in arrays.values()))
        if stats is not None:
            stats["miss"] = stats.get("miss", 0) + 1
    else:
        if stats is not None:
            stats["skip"] = stats.get("skip", 0) + 1
    return case


def load_or_build_spec(spec, *, shape=None, dtype=None, seed=None,
                       cache: str | os.PathLike | None = None,
                       use_cache: bool = True, stats: dict | None = None):
    """``load_or_build`` for an ``operator_entry.OperatorSpec``."""
    return load_or_build(spec.load(), spec.path, shape=shape, dtype=dtype,
                         seed=seed, cache=cache, use_cache=use_cache,
                         stats=stats)


# --------------------------------------------------------------------- CLI
def _live_operator_shas() -> set[str]:
    """sha256 of every operator file next to this opslib copy -- group
    directories in the repository, ``operators/`` directly in an export
    (collection layout)."""
    ops_root = Path(__file__).resolve().parents[2]      # <root>/harness/opslib
    shas = set()
    directories = []
    collection = ops_root / "collection.json"
    if collection.is_file():
        directories.append(ops_root / "operators")       # export layout
    else:
        # the suite lanes, plus the upstream group dirs on the maintenance branch
        directories = [ops_root / group
                       for group in ("suite/dev", "suite/perf",
                                     "basic", "medium", "hard", "bench")]
    for directory in directories:
        if not directory.is_dir():
            continue
        for path in directory.glob("*.py"):
            shas.add(file_sha256(path))
    return shas


def prune(cache: str | os.PathLike | None = None) -> dict:
    """Delete entries whose operator file no longer has the recorded sha256."""
    root = cache_dir(cache)
    live = _live_operator_shas()
    removed, kept, bytes_freed = 0, 0, 0
    if root.is_dir():
        for shard in sorted(root.iterdir()):
            if not shard.is_dir() or shard.name.startswith(".tmp-"):
                continue
            for entry in sorted(shard.iterdir()):
                if not (entry / "meta.json").is_file():
                    continue
                try:
                    record = json.loads((entry / "meta.json").read_text())
                except (OSError, ValueError):
                    continue
                if record.get("operator_sha256") in live:
                    kept += 1
                    continue
                bytes_freed += sum(f.stat().st_size for f in entry.iterdir()
                                   if f.is_file())
                shutil.rmtree(entry, ignore_errors=True)
                removed += 1
    return {"removed": removed, "kept": kept, "bytes_freed": bytes_freed}


def stats_summary(cache: str | os.PathLike | None = None) -> dict:
    root = cache_dir(cache)
    entries = files = 0
    total = 0
    if root.is_dir():
        for shard in root.iterdir():
            if not shard.is_dir():
                continue
            for entry in shard.iterdir():
                if not (entry / "meta.json").is_file():
                    continue
                entries += 1
                for f in entry.iterdir():
                    if f.is_file():
                        files += 1
                        total += f.stat().st_size
    return {"dir": str(root), "entries": entries, "files": files,
            "bytes": total, "max_total_bytes": max_total_bytes(),
            "store_failures": _STORE_FAILURES}


def _build_task_list(groups, workload_path, llc_bytes, device):
    """(source, shape, dtype, seed) tasks for --build."""
    tasks = []
    if workload_path is not None:
        import sys as _sys
        harness = Path(__file__).resolve().parents[1]
        if str(harness) not in _sys.path:
            _sys.path.insert(0, str(harness))
        from benchmark.size import resolve_shape
        workload = json.loads(Path(workload_path).read_text())
        seed = 20261008  # bench/run.py's default; keys must match exactly
        for entry in workload["entries"]:
            dtype = entry.get("dtype", workload["dtype"])
            shape = tuple(resolve_shape(entry, llc_bytes, dtype=workload["dtype"]))
            tasks.append((entry["operator"], shape, dtype, seed,
                          entry.get("ref_split") == "rows"))
    if groups:
        from opslib import catalog as _catalog
        for group in groups:
            for spec in _catalog.specs("all"):
                if spec.entry["group"] != group:
                    continue
                module = spec.load()
                for shape in getattr(module, "SHAPES", []):
                    for dtype in getattr(module, "DTYPES", []):
                        tasks.append((spec.source, tuple(shape), str(dtype), 30, False))
    return tasks


def _build_one(task):
    """Worker: construct one case and write it into the golden cache."""
    import time

    from opslib import catalog as _catalog
    from opslib.case import split_ref_scope
    source, shape, dtype, seed, split = task
    started = time.perf_counter()
    try:
        spec = _catalog.find(source)
        with split_ref_scope(spec.load(), split):
            load_or_build_spec(spec, shape=shape, dtype=dtype, seed=seed, use_cache=True)
        return {"operator": source, "shape": list(shape), "dtype": dtype,
                "seconds": round(time.perf_counter() - started, 3), "error": None}
    except Exception as exc:  # noqa: BLE001
        return {"operator": source, "shape": list(shape), "dtype": dtype,
                "seconds": round(time.perf_counter() - started, 3),
                "error": f"{type(exc).__name__}: {exc}"[:200]}


def _default_jobs():
    import os as _os
    cpus = _os.cpu_count() or 1
    try:
        available = int(next(line.split()[1] for line in
                             open("/proc/meminfo") if line.startswith("MemAvailable")))
        cap = max(1, (available * 1024) // (8 << 30))
    except OSError:
        cap = cpus
    return max(1, min(cpus, cap))


def build_cache(groups, workload_path, llc_bytes, device, jobs, cache=None):
    """Pre-build golden entries in parallel (host side only, no GPU)."""
    if workload_path is not None and llc_bytes is None:
        if device is None:
            raise SystemExit("--workload needs --llc-bytes or --device")
        from opslib.device import make_device
        props = make_device(device).properties()
        llc_bytes = props.get("llc_bytes")
        if not llc_bytes:
            raise SystemExit("device properties lack llc_bytes; pass --llc-bytes")
    tasks = _build_task_list(groups, workload_path, llc_bytes, device)
    if not tasks:
        return {"tasks": 0}
    from concurrent.futures import ProcessPoolExecutor
    workers = jobs or _default_jobs()
    records = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for record in pool.map(_build_one, tasks, chunksize=1):
            records.append(record)
            if record["error"]:
                print(f"FAIL {record['operator']} {record['shape']} :: {record['error']}", flush=True)
    slowest = sorted(records, key=lambda r: -r["seconds"])[:20]
    summary = {"tasks": len(records),
               "built": sum(1 for r in records if not r["error"]),
               "failed": sum(1 for r in records if r["error"]),
               "workers": workers, "slowest": slowest}
    return summary


def main(argv=None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="manage the golden case cache")
    parser.add_argument("--prune", action="store_true",
                        help="drop entries whose operator file changed")
    parser.add_argument("--stats", action="store_true", help="cache summary")
    parser.add_argument("--build", action="store_true",
                        help="pre-build cases in parallel (host side only, no GPU)")
    parser.add_argument("--workload", default=None,
                        help="bench/workload.json: build bench steady-state shapes")
    parser.add_argument("--llc-bytes", type=int, default=None,
                        help="last-level cache bytes for --workload sizing")
    parser.add_argument("--device", default=None,
                        help="read llc_bytes from this device's properties")
    parser.add_argument("--group", action="append",
                        help="build all cases of this group (repeatable)")
    parser.add_argument("-j", "--jobs", type=int, default=None,
                        help="parallel workers (default: min(cores, mem/8GiB))")
    parser.add_argument("--cache-dir", default=None)
    args = parser.parse_args(argv)
    if args.prune:
        result = prune(args.cache_dir)
        print(f"pruned {result['removed']} entries "
              f"({result['bytes_freed'] / 2**20:.1f} MiB freed, "
              f"{result['kept']} kept)")
    if args.build:
        summary = build_cache(args.group, args.workload, args.llc_bytes,
                              args.device, args.jobs, args.cache_dir)
        print(json.dumps({k: v for k, v in summary.items() if k != "slowest"},
                         indent=1))
        print("slowest (seconds):")
        for r in summary.get("slowest", []):
            print(f"  {r['seconds']:8.3f}  {r['operator']} {r['shape']} {r['dtype']}")
        if summary.get("failed"):
            return 1
        return 0
    if args.stats or not args.prune:
        stats = stats_summary(args.cache_dir)
        for key, value in stats.items():
            print(f"{key}: {value}")
        if stats["bytes"] > stats["max_total_bytes"]:
            print("warning: cache exceeds OPS_GOLDEN_MAX_TOTAL; the LRU will "
                  "evict entries every round -- raise OPS_GOLDEN_MAX_TOTAL "
                  "above the total and keep OPS_GOLDEN_DIR on a disk with room")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
