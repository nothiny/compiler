#!/usr/bin/env python3
"""test_runtime_smoke.py -- executed QEMU round trips for the a100c native
runtime (T005).

Drives the hand-written assembly operator stub (not pipeline output) linked
against the runtime through the declared transport: pack_case ->
a100_support/run-riscv.sh -> unpack_outputs, and asserts the acceptance
criteria:

  acceptance[0] the strided-alias case and the bfloat16 value-storage case both
                compare PASS (RT-EXECUTION-CONTRACT witness);
  acceptance[1] the persistent pool is observed at 1/2/4/8 threads with
                distinct guest tids, full item coverage and one pool
                initialization per process (F019);
  acceptance[2] --repeats 3 with input snapshot/restore produces identical
                outputs across repeats, and bundles that violate the
                a100-native-io/v1 format are rejected before execution
                (recorded refusal, never a wrong result);
  acceptance[3] is asserted on the artifact by test_build.py; this test
                additionally executes it under the declared QEMU endpoint.

Run: python3 a100c/tests/test_runtime_smoke.py   (exit 0 = all checks PASS)
"""
from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()

import numpy as np  # noqa: E402

from a100_support.native_io import pack_case, unpack_outputs  # noqa: E402

RUNNER = ROOT / "a100_support" / "run-riscv.sh"
FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}{(' | ' + detail) if detail else ''}",
          flush=True)
    if not ok:
        FAILURES.append(name)
    return ok


def run_native(exe: Path, bundle: Path, threads: int, repeats: int | None = None,
               timeout: float = 300.0):
    command = [str(RUNNER), str(exe), "--bundle", str(bundle), "--threads", str(threads)]
    if repeats is not None:
        command += ["--repeats", str(repeats)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    status = None
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    if lines:
        try:
            status = json.loads(lines[-1])
        except ValueError:
            status = None
    return result, status


def alias_case(elements: int):
    """Strided-alias case: shared storage, strided view, pointer table, scalar."""
    a = np.arange(elements, dtype=np.int32)
    b = a[1::2]
    table = np.zeros(1, dtype=np.uint64)
    case = {
        "args": {"a": a, "b": b, "table": table, "delta": 100},
        "outputs": ["a", "b"],
        "pointer_table_relocations": [
            {"table": "table", "entry": 0, "allocation": "b", "byte_offset": 0}],
    }
    return case, a, b


def expected_alias(a: np.ndarray, b: np.ndarray, delta: int = 100) -> np.ndarray:
    # Stub semantics: stage 1 adds delta to every element of b (index 0 through
    # the relocated guest pointer), the merge totals N = b.size, stage 3 adds N.
    expected = a.copy()
    expected[1::2] += delta + b.shape[0]
    return expected


def stage_case(case: dict):
    directory = Path(tempfile.mkdtemp(prefix="a100rt-smoke-"))
    info = pack_case(case, directory)
    return directory, info


def check_ok_status(name: str, result, status, threads: int, repeats: int):
    check(f"{name}:exit0", result.returncode == 0,
          f"returncode={result.returncode} stderr={result.stderr[-300:]}")
    check(f"{name}:status-ok", status is not None and status.get("status") == "ok"
          and status.get("runtime") == "a100rt/v1" and status.get("threads") == threads
          and status.get("repeats") == repeats,
          json.dumps(status)[:220] if status else "no status json")
    check(f"{name}:one-pool-init", status is not None and status.get("pool_initializations") == 1)
    return status


def corruption_targets(info: dict) -> dict:
    """File offsets of fields to corrupt, derived from the bundle's own layout."""
    nstorage = len(info["storages"])
    cursor = 32 + 16 * nstorage
    view_offset = {}
    for name in info["view_order"]:
        view = info["views"][name]
        view_offset[name] = cursor + 16  # i64 offset field inside the record
        cursor += 24 + 16 * len(view["shape"])
    cursor += 16 * len(info["scalar_order"])
    reloc_entry = cursor + 8 if info["relocations"] else None  # u64 entry field
    return {"view_offset": view_offset, "reloc_entry": reloc_entry}


def main() -> int:
    started = time.time()
    build = _bootstrap.load_build_module()
    info = build.build_operator_stub()
    exe = info["executable"]
    check("build", exe.is_file(), str(exe))

    # ---------------- acceptance[0]: strided-alias case ----------------
    case, a, b = alias_case(12)
    directory, _ = stage_case(case)
    result, status = run_native(exe, directory / "bundle.bin", threads=4)
    check_ok_status("alias", result, status, threads=4, repeats=1)
    actual = unpack_outputs(directory)
    expected = expected_alias(a, b)
    check("alias:comparison",
          np.array_equal(actual["a"], expected)
          and np.array_equal(actual["b"], expected[1::2])
          and np.shares_memory(actual["a"], actual["b"]),
          f"expected b={expected[1::2].tolist()} actual b={actual['b'].tolist()}")
    check("alias:item-coverage", status is not None
          and sum(w["items"] for w in status["workers"]) == b.shape[0],
          f"items={[w['items'] for w in status['workers']]}" if status else "")

    # ---------------- acceptance[0]: bfloat16 value-storage case ----------------
    values = np.array([1.0, -2.5, 0.125, 4.0], dtype=np.float32)
    bf16_case = {"args": {"a": values}, "outputs": ["a"],
                 "pointer_dtypes": {"a": "bfloat16"}}
    directory2, _ = stage_case(bf16_case)
    result2, status2 = run_native(exe, directory2 / "bundle.bin", threads=2)
    check_ok_status("bf16", result2, status2, threads=2, repeats=1)
    out = unpack_outputs(directory2)["a"]
    check("bf16:comparison", np.array_equal(out, -values),
          f"expected={(-values).tolist()} actual={out.tolist()}")
    check("bf16:item-coverage", status2 is not None
          and sum(w["items"] for w in status2["workers"]) == values.shape[0])

    # ---------------- acceptance[1]: pool observation at 1/2/4/8 ----------------
    # Each thread count gets its own freshly staged bundle: one execution
    # consumes its inputs in place, so runs never share a staged case.
    for threads in (1, 2, 4, 8):
        case_big, a_big, b_big = alias_case(65542)  # b has 32771 elements (F019's census size)
        directory3, _ = stage_case(case_big)
        expected_big = expected_alias(a_big, b_big)
        result_n, status_n = run_native(exe, directory3 / "bundle.bin", threads=threads)
        check_ok_status(f"pool{threads}", result_n, status_n, threads=threads, repeats=1)
        if status_n is None:
            continue
        workers = status_n["workers"]
        tids = [w["guest_tid"] for w in workers]
        items = [w["items"] for w in workers]
        check(f"pool{threads}:distinct-guest-tids",
              len(tids) == threads and len(set(tids)) == threads and all(t > 0 for t in tids),
              f"tids={tids}")
        check(f"pool{threads}:full-item-coverage",
              sum(items) == b_big.shape[0] and all(i > 0 for i in items),
              f"items={items}")
        actual_n = unpack_outputs(directory3)
        check(f"pool{threads}:comparison",
              np.array_equal(actual_n["a"], expected_big)
              and np.array_equal(actual_n["b"], expected_big[1::2]))

    # ---------------- acceptance[2]: --repeats with snapshot/restore ----------------
    case_r, a_r, b_r = alias_case(12)
    directory4, _ = stage_case(case_r)
    expected_r = expected_alias(a_r, b_r)
    result_r3, status_r3 = run_native(exe, directory4 / "bundle.bin", threads=4, repeats=3)
    check_ok_status("repeats3", result_r3, status_r3, threads=4, repeats=3)
    check("repeats3:all-equal", status_r3 is not None and status_r3.get("repeats_all_equal") is True)
    out_r3 = unpack_outputs(directory4)
    # The final repeat must have seen the ORIGINAL inputs: one execution's
    # expected values, not three accumulations.
    check("repeats3:independent-outputs",
          np.array_equal(out_r3["a"], expected_r)
          and np.array_equal(out_r3["b"], expected_r[1::2]),
          f"b={out_r3['b'].tolist()} expected={expected_r[1::2].tolist()}")

    # Cross-check against a single-repeat run of the same case: identical
    # final outputs (pool and workspace reuse, no cross-execution leakage).
    case_x, a_x, b_x = alias_case(12)
    directory5, _ = stage_case(case_x)
    result_x, status_x = run_native(exe, directory5 / "bundle.bin", threads=4, repeats=1)
    check_ok_status("repeats1", result_x, status_x, threads=4, repeats=1)
    out_x = unpack_outputs(directory5)
    check("repeats1-identical-to-repeats3",
          np.array_equal(out_x["a"], out_r3["a"]) and np.array_equal(out_x["b"], out_r3["b"]))

    # ---------------- acceptance[2]: format violations are refusals ----------------
    case_v, _, _ = alias_case(12)
    directory6, info_v = stage_case(case_v)
    valid = (directory6 / "bundle.bin").read_bytes()
    targets = corruption_targets(info_v)

    def corrupt(name: str, payload: bytes):
        path = directory6 / f"bundle-{name}.bin"
        path.write_bytes(payload)
        return path

    rejections = []
    rejections.append(("bad-magic",
                       b"X" + valid[1:]))
    rejections.append(("truncated", valid[:24]))
    damaged = bytearray(valid)
    struct.pack_into("<q", damaged, targets["view_offset"]["a"], -1)
    rejections.append(("view-offset-negative", bytes(damaged)))
    damaged = bytearray(valid)
    struct.pack_into("<Q", damaged, targets["reloc_entry"], 999)
    rejections.append(("reloc-entry-out-of-bounds", bytes(damaged)))
    rejections.append(("garbage", b"\xde\xad\xbe\xef" * 25))

    for name, payload in rejections:
        path = corrupt(name, payload)
        before = hashlib.sha256(path.read_bytes()).hexdigest()
        result_v, status_v = run_native(exe, path, threads=2)
        after = hashlib.sha256(path.read_bytes()).hexdigest()
        check(f"reject:{name}:exit3", result_v.returncode == 3,
              f"returncode={result_v.returncode}")
        check(f"reject:{name}:status-rejected",
              status_v is not None and status_v.get("status") == "rejected"
              and bool(status_v.get("reason")),
              json.dumps(status_v) if status_v else "no status json")
        # A rejected bundle is never written: the refusal leaves the file
        # untouched and produces no result at all.
        check(f"reject:{name}:file-untouched", before == after)

    # ---------------- command-line contract ----------------
    command = [str(RUNNER), str(exe), "--bundle", str(directory6 / "bundle.bin"),
               "--threads", "3"]
    result_c = subprocess.run(command, capture_output=True, text=True, timeout=300)
    check("cli:threads-3-refused", result_c.returncode == 2, f"returncode={result_c.returncode}")
    command = [str(RUNNER), str(exe), "--threads", "1"]
    result_m = subprocess.run(command, capture_output=True, text=True, timeout=300)
    check("cli:missing-bundle-refused", result_m.returncode == 2,
          f"returncode={result_m.returncode}")

    if FAILURES:
        print(f"test_runtime_smoke: {len(FAILURES)} check(s) FAILED: {FAILURES}")
        return 1
    print(f"test_runtime_smoke: all checks PASS ({time.time() - started:.1f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
