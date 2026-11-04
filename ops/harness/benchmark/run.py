"""The unified benchmark driver: verify + time every workload entry.

Replaces ``bench/driver.py`` + ``bench/triton_baseline.py`` (one code path,
selected by flags) and ``bench/verify.py`` (``--verify-only``).  Per entry:

    load_or_build (golden cache)
      -> stage_case (inputs reused across adjacent identical entries,
                     output buffers freshly allocated and zeroed)
      -> first launch, timed separately as ``compile_s`` (JIT compile time)
      -> verify against the operator's own oracle (on device when supported)
      -> warmup -> adaptive sampling -> release buffers

Methodology:

  - timing prefers the device's own event timer (``device.timer()``); the
    record says which (``timer: "device" | "host"``);
  - sampling is adaptive: at least ``--min-samples`` launches (default 50),
    until ``--min-time-s`` of accumulated kernel time (default 0.2 s), hard
    cap ``--max-samples`` (default 1000); the primary metric is the
    **median** (``--stat mean --samples 5 --warmups 1`` reproduces the old
    fixed-sample mean methodology);
  - every record carries its provenance (operator sha256, workload sha256,
    resolved shape, device properties, versions, git commit), and
    ``report.py`` only pairs records whose operator sha256 and shape both
    match -- a changed operator is reported as a stale baseline, never
    silently compared.

Results go to ``<out-dir>/<device-fingerprint>/`` -- ``--out-dir`` defaults
to ``results/`` inside this corpus (gitignored); a compiler project passes
its own directory so the evidence is committed with the project, not
written into the corpus it reads.  The committed ``bench/BENCH_*.json``
history lives on in ``results/reference/``.

Output file by role: ``BENCH_REPORT.json`` + ``evidence/`` (a compiler run,
verified unless ``--no-verify``), ``BENCH_TRITON.json`` + ``evidence-triton/``
(``--baseline``: the stock-Triton reference timing, unverified),
``BENCH_VERIFY.json`` + ``evidence-verify/`` (``--verify-only``).
Every record says ``verified: true|false``; ``report.py`` never scores an
unverified compiler record.

    python3 bench/run.py --device cuda --baseline          # Triton baseline
    python3 bench/run.py --device mycompiler:make_device   # your compiler
    python3 bench/run.py --device torch-gpu --verify-only  # correctness only
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HARNESS = Path(__file__).resolve().parents[1]     # <root>/harness
ROOT = HARNESS.parent                               # the corpus root
sys.path.insert(0, str(HARNESS))

from benchmark.size import MULTIPLE, resolve_shape  # noqa: E402
from opslib import compare as compare_lib  # noqa: E402
from opslib import golden  # noqa: E402
from opslib.device import StagedCase, patch_pointer_tables  # noqa: E402
from compiler_api.run_cases import make_device  # noqa: E402


# ------------------------------------------------------------------ staging
def stage_with_reuse(case, device, reuse):
    """Stage ``case`` on ``device``, reusing byte-identical input uploads.

    A buffer is reusable only when **both** the previous and the current
    case declare it in ``inputs`` and not in ``outputs``: a kernel may
    write a buffer it received, so anything not provably a pure input is
    re-uploaded (the contract: declared inputs are not mutated).  Output
    buffers are freshly allocated and **zeroed** every entry, so a previous
    entry's result can never pass for this one's.  Returns
    ``(StagedCase, arrays, buffers)`` describing the inputs eligible for
    the next entry's reuse.
    """
    host = {**case.get("allocations", {}), **case["args"]}
    pointer_types = case.get("pointer_dtypes", {}) or {}
    outputs = set(case.get("outputs") or ())
    inputs = set(case.get("inputs") or ())
    previous_arrays, previous_buffers = reuse if reuse else ({}, {})
    buffers = {}
    reusable_arrays = {}
    reusable_buffers = {}
    for name, value in host.items():
        if not isinstance(value, np.ndarray):
            buffers[name] = value
            continue
        pure_input = name in inputs and name not in outputs
        previous = previous_arrays.get(name)
        if (pure_input and previous is not None
                and previous.dtype == value.dtype
                and previous.shape == value.shape
                and np.array_equal(previous, value)):
            buffers[name] = previous_buffers[name]     # byte-identical: reuse
            reusable_arrays[name] = value
            reusable_buffers[name] = previous_buffers[name]
            continue
        if name in outputs and name not in inputs:
            # fresh, zeroed scratch: content is irrelevant (the oracle owns
            # correctness) and zeros make "kernel did not write" visible
            # instead of masked by a previous entry's result.  Buffers that
            # are also *inputs* (in-place operators read before writing)
            # keep their real data.
            payload = np.zeros(value.shape, value.dtype)
        else:
            payload = value
        buffer = device.upload(payload, pointer_types.get(name))
        buffers[name] = buffer
        if pure_input:
            reusable_arrays[name] = value
            reusable_buffers[name] = buffer
    patch_pointer_tables(case, host, device, buffers)
    kernel = case.get("kernel")
    if kernel is None:
        raise ValueError("case has no kernel")
    staged = StagedCase(case, device, buffers, kernel)
    return staged, reusable_arrays, reusable_buffers


def _release(device, staged, carried):
    """Explicitly free this entry's buffers, keeping the carried ones."""
    release = getattr(device, "release", None)
    if release is None:
        return
    doomed = {name: buffer for name, buffer in staged._buffers.items()
              if buffer not in carried}
    release(doomed)


# ------------------------------------------------------------------- timing
# Hard floor: a slow kernel would otherwise stop after very few samples
# (one 88 ms launch already exceeds the default 0.2 s budget), leaving a
# median computed from two or three noisy measurements.
_MIN_SAMPLES_FLOOR = 10


def _enough(times, args):
    if args.samples:
        return len(times) >= args.samples
    # stop once EITHER threshold is reached (>= min_samples launches OR
    # >= min_time_s accumulated), but never before the hard floor
    return (len(times) >= max(args.min_samples, _MIN_SAMPLES_FLOOR)
            or (len(times) >= _MIN_SAMPLES_FLOOR
                and sum(times) >= args.min_time_s)
            or len(times) >= args.max_samples)


def measure(staged, device, args, timer):
    for _ in range(args.warmups):
        staged.launch()
    device.synchronize()
    times = []
    while True:
        if timer is not None:
            with timer:
                staged.launch()
            times.append(timer.seconds)
        else:
            device.synchronize()
            start = time.perf_counter()
            staged.launch()
            device.synchronize()
            times.append(time.perf_counter() - start)
        if _enough(times, args):
            return times


def _percentile(values, fraction):
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, round(fraction * (len(ordered) - 1)))]


def summarize(times, stat):
    mean = statistics.fmean(times)
    stdev = statistics.pstdev(times) if len(times) > 1 else 0.0
    return {
        "kernel_s": statistics.median(times) if stat == "median" else mean,
        "stat": stat,
        "median_s": statistics.median(times),
        "mean_s": mean,
        "p10_s": _percentile(times, 0.10),
        "p90_s": _percentile(times, 0.90),
        "stdev_s": stdev,
        "cov": (stdev / mean) if mean else 0.0,
        "steady": (stdev / mean if mean else 0.0) < 0.05,
        "n_samples": len(times),
        "times_s": times,
    }


# --------------------------------------------------------------- one entry
def run_entry(entry, device, workload, *, llc, args, common, reuse):
    dtype = entry.get("dtype", workload["dtype"])
    shape = resolve_shape(entry, llc, args.multiple, workload["dtype"])
    record = {
        "id": entry["id"], "operator": entry["operator"], "class": entry["class"],
        "family": entry["family"], "dtype": dtype, "shape": shape,
        "size_class": f"llc_x{args.multiple}", "warmups": args.warmups,
        "timer": args.timer, "operator_sha256": golden.file_sha256(
            ROOT / entry["operator"]),
        **common,
    }
    try:
        # bench operators live in bench/operators/, outside the catalog's
        # group directories: load them by path
        from opslib.case import split_ref_scope
        from opslib.runner import load_operator
        path = ROOT / entry["operator"]
        module = load_operator(path)
        # entries whose oracle is row-independent (checked by select.py)
        # build their expected values on row blocks in threads
        with split_ref_scope(module, entry.get("ref_split") == "rows"):
            case = golden.load_or_build(
                module, path, shape=tuple(shape), dtype=dtype,
                seed=args.seed, use_cache=not args.no_golden)
    except Exception as exc:  # noqa: BLE001
        record.update({"status": "CASE_FAIL",
                       "error": f"{type(exc).__name__}: {exc}"[:200]})
        return record, None

    try:
        staged, arrays, buffers = stage_with_reuse(case, device, reuse)
        start = time.perf_counter()
        staged.launch()                     # first launch: JIT compile + run
        device.synchronize()
        record["compile_s"] = time.perf_counter() - start
    except Exception as exc:  # noqa: BLE001
        record.update({"status": "LAUNCH_FAIL",
                       "error": f"{type(exc).__name__}: {exc}"[:200]})
        return record, None

    handed_on = (arrays, buffers)
    phase = "launch"
    try:
        if not args.no_verify:
            phase = "verify"
            verdict = compare_lib.compare_case_on_device(staged, case, device)
            if verdict is None:
                # host fallback: a failed download is infrastructure
                # (LAUNCH_FAIL), not a wrong answer (MISMATCH)
                phase = "readback"
                outputs = staged.outputs()
                phase = "verify"
                verdict = compare_lib.compare_case(case, outputs)
            record["max_abs_error"] = verdict["max_abs_error"]
        record["verified"] = not args.no_verify
        if not args.verify_only:
            phase = "measure"
            timer = device.timer() if args.timer == "device" else None
            times = measure(staged, device, args, timer)
            record.update(summarize(times, args.stat))
        record["status"] = "PASS"
        return record, handed_on
    except Exception as exc:  # noqa: BLE001
        # a failure while verifying is a wrong answer, not a crash: the
        # kernel ran but its output missed the oracle
        record.update({"status": "MISMATCH" if phase == "verify" else "LAUNCH_FAIL",
                       "error": str(exc).splitlines()[0][:200],
                       "detail": str(exc).splitlines()[0][:200]})
        return record, handed_on
    finally:
        _release(device, staged, set(buffers.values()) if buffers else set())


# --------------------------------------------------------------------- main
def _git_commit():
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                              capture_output=True, text=True,
                              timeout=10).stdout.strip()
    except Exception:  # noqa: BLE001
        return None


def _device_fingerprint(device):
    props = device.properties() if hasattr(device, "properties") else {}
    digest = hashlib.sha256(json.dumps(props, sort_keys=True,
                                       default=str).encode()).hexdigest()[:8]
    name = "".join(ch if ch.isalnum() else "-" for ch in str(props.get("name", "gpu")))
    return f"{type(device).__name__}-{name}-{digest}".strip("-").lower()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workload", default=str(ROOT / "suite" / "perf" / "workload.json"))
    parser.add_argument("--device", required=True,
                        help="cuda | torch-gpu | torch-cpu | module:factory")
    parser.add_argument("--llc-bytes", type=int, default=None,
                        help="working-set target; default: the device's L2 size")
    parser.add_argument("--multiple", type=int, default=MULTIPLE)
    parser.add_argument("--group", default=None, help="filter by class")
    parser.add_argument("--only", default=None,
                        help="run a single entry id (compat with the old triton_baseline.py)")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--seed", type=int, default=20261008)
    parser.add_argument("--no-golden", action="store_true",
                        help="always rebuild cases with make_case")
    parser.add_argument("--verify-only", action="store_true",
                        help="correctness check only (old verify.py)")
    parser.add_argument("--no-verify", action="store_true",
                        help="skip verification (records are marked verified=false "
                             "and report.py will not score them)")
    parser.add_argument("--baseline", action="store_true",
                        help="this run is the stock-Triton reference: implies "
                             "--no-verify and writes BENCH_TRITON.json")
    parser.add_argument("--warmups", type=int, default=3)
    parser.add_argument("--samples", type=int, default=None,
                        help="fixed sample count (old methodology); default: adaptive")
    parser.add_argument("--min-samples", type=int, default=50)
    parser.add_argument("--min-time-s", type=float, default=0.2)
    parser.add_argument("--max-samples", type=int, default=1000)
    parser.add_argument("--stat", choices=("median", "mean"), default="median")
    parser.add_argument("--timer", choices=("device", "host"), default=None,
                        help="default: device events when the device has timer()")
    parser.add_argument("--out-dir", default=str(ROOT / "results"),
                        help="results root; output goes to <out-dir>/<device-fingerprint>/ "
                             "(a compiler project should pass its own directory)")
    parser.add_argument("--out", default=None,
                        help="exact output json path (overrides --out-dir)")
    parser.add_argument("--evidence", default=None)
    args = parser.parse_args(argv)
    if args.baseline:
        if args.verify_only:
            parser.error("--baseline and --verify-only are exclusive")
        args.no_verify = True

    workload_path = Path(args.workload)
    workload = json.loads(workload_path.read_text())
    device = make_device(args.device)

    llc = args.llc_bytes
    if llc is None:
        props = device.properties() if hasattr(device, "properties") else {}
        llc = props.get("llc_bytes")
        if not llc:
            raise SystemExit("cannot determine the device's last-level cache "
                             "size; pass --llc-bytes explicitly")
    if args.timer is None:
        args.timer = "device" if getattr(device, "timer", None) is not None else "host"

    import triton
    common = {
        "workload_sha256": hashlib.sha256(workload_path.read_bytes()).hexdigest(),
        "device_properties": (device.properties()
                              if hasattr(device, "properties") else {}),
        "triton": triton.__version__,
        "numpy": np.__version__,
        "git_commit": _git_commit(),
        "llc_bytes": llc,
        "device": args.device,
    }

    fingerprint = _device_fingerprint(device)
    out = Path(args.out) if args.out else (
        Path(args.out_dir) / fingerprint /
        ("BENCH_VERIFY.json" if args.verify_only else
         "BENCH_TRITON.json" if args.baseline else "BENCH_REPORT.json"))
    # one evidence directory per role, so a baseline and a compiler run on the
    # same device fingerprint never overwrite each other's per-entry files
    role_dir = ("evidence-verify" if args.verify_only else
                "evidence-triton" if args.baseline else "evidence")
    evidence = Path(args.evidence) if args.evidence else out.parent / role_dir
    out.parent.mkdir(parents=True, exist_ok=True)
    evidence.mkdir(parents=True, exist_ok=True)

    entries = [entry for entry in workload["entries"]
               if not args.group or entry["class"] == args.group]
    if args.only is not None:
        entries = [entry for entry in entries if entry["id"] == args.only]
    if args.limit is not None:
        entries = entries[:args.limit]

    rows = []
    reuse = None
    started = time.perf_counter()
    for entry in entries:
        row, reuse = run_entry(entry, device, workload, llc=llc, args=args,
                               common=common, reuse=reuse)
        rows.append(row)
        (evidence / f"{entry['id'].replace('/', '_')}.json").write_text(
            json.dumps(row, indent=2) + "\n")
        kernel = row.get("kernel_s")
        print(f"{row['status']:11s} {entry['class']:9s} {entry['id']:30s} "
              f"kernel={(kernel or 0) * 1e3:10.4f}ms "
              f"compile={row.get('compile_s', 0):7.3f}s "
              f"n={row.get('n_samples', 0):4d} {row.get('stat', '')}", flush=True)
        out.write_text(json.dumps(
            {"schema": "tritonbench-bench-run/2", "metric": "kernel_time_s",
             "device": args.device, "timer": args.timer, "llc_bytes": llc,
             "multiple": args.multiple, "seed": args.seed,
             "device_fingerprint": fingerprint, "entries": rows},
            indent=2) + "\n")

    passed = sum(1 for row in rows if row["status"] == "PASS")
    print(f"\nwrote {out}: {passed}/{len(rows)} PASS "
          f"in {time.perf_counter() - started:.0f}s")
    return 0 if rows and passed == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
