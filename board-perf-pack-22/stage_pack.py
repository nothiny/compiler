#!/usr/bin/env python3
"""stage_pack.py -- build the K3 board performance pack (user-directed).

This is NOT part of the compiler correctness workflow: it packages already
compiled per-identity artifacts (``a100c/cache/<id>/operator_exec``) together
with freshly packed input bundles (a100-native-io/v1) for a small set of
typical TritonBench-derived perf-lane operators at their audited steady-state
shapes, so the board owner can measure 1-worker vs 8-worker wall time on the
A100 cores (CPU 8-15).

For every selected (operator, shape, dtype) case it:
  1. builds the case exactly the way the corpus harness does
     (``golden.load_or_build_spec`` = load_operator + make_case);
  2. compiles it through the public factory (``a100c.factory.make_compiler``)
     -- a cache hit reuses the existing artifact and rebuilds nothing;
  3. packs the input bundle and copies the ELF into the pack;
  4. smoke-runs the exact shipped pair (ELF + bundle copy) under the pinned
     QEMU endpoint at --threads 1 and 8 and compares the outputs against the
     case's own reference under its declared comparison policy.

Cases whose smoke fails are dropped from cases.conf and are not shipped as
runnable entries (their files stay for inspection, flagged in manifest.json).
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # project root
PACK = Path(__file__).resolve().parent              # board-perf-pack/
RUN_RISCV = ROOT / "a100_support" / "run-riscv.sh"
SEED = 30                                            # the scan/workload seed
SMOKE_TIMEOUT = float(os.environ.get("PACK_SMOKE_TIMEOUT", "600"))

# name, corpus-relative operator, steady-state shape (workload.json unless the
# op only passed at its scan shape), dtype, board repeats for the timed loop.
# Coverage: compute / memory / reduction; dtypes fp32, fp16, bf16, int8, int16,
# int32, int64, bool.  Every operator below passed 100% of its scan cases.
CASES = [
    # ---- compute (matmul / attention / linear attention / conv) ----
    ("matmul_f16",       "suite/perf/matmul.py",             (256, 256, 256),   "float16",   30),
    ("matmul_bf16",      "suite/perf/matmul.py",             (256, 256, 256),   "bfloat16",  30),
    ("matmul_f32",       "suite/perf/matmul.py",             (256, 256, 256),   "float32",   30),
    ("matmul_t2_bf16",   "suite/perf/matmul_triton2.py",     (256, 256, 256),   "bfloat16",  30),
    ("dq_matmul_bf16",   "suite/perf/dequantize_matmul.py",  (256, 32),         "bfloat16", 200),
    ("chunk_ret_bf16",   "suite/perf/chunk_retention.py",    (8, 2, 16, 32, 32),"bfloat16", 100),
    # ---- memory (elementwise / activation / gather / strided / bitwise) ----
    ("gelu_f32",         "suite/perf/gelu.py",               (262144,),         "float32",  500),
    ("add_gelu_f16",     "suite/perf/add_gelu.py",           (262144,),         "float16",  500),
    ("swiglu_bf16",      "suite/perf/swiglu_fwd.py",         (4096, 64),        "bfloat16", 500),
    ("relu_strided_bf16","suite/perf/relu_strided_buffer.py",(262144,),         "bfloat16", 500),
    ("gather_i8",        "suite/perf/gather_1d.py",          (32768, 8),        "int8",     500),
    ("gather_i32",       "suite/perf/gather_1d.py",          (32768, 8),        "int32",    500),
    ("gather_i64",       "suite/perf/gather_1d.py",          (32768, 8),        "int64",    500),
    ("signbit_i32",      "suite/perf/signbit_bitwise_and.py",(262144,),         "int32",    500),
    # ---- reduction (norm / argmax / softmax / logsumexp / mean / max) ----
    ("rmsnorm_bf16",     "suite/perf/fast_rms_layernorm.py", (64, 1024),        "bfloat16", 1000),
    ("argmax_bf16",      "suite/perf/argmax.py",             (64, 1024),        "bfloat16", 1000),
    ("max_f16",          "suite/perf/max.py",                (64, 1024),        "float16",  1000),
    ("mean_f32",         "suite/perf/mean.py",               (64, 1024),        "float32",  1000),
    ("l2norm_f16",       "suite/perf/l2_norm_triton2.py",    (64, 1024),        "float16",  1000),
    # ---- extra dtype / feature coverage (int16, bool, atomics) ----
    ("hardsig_i16",      "suite/dev/hardsigmoid_kernel_2.py",(97,),             "int16",    2000),
    ("any_bool",         "suite/dev/any_kernel_2.py",        (126,),            "bool",     2000),
    ("atomic_bitmap_i32","suite/dev/atomic_bitmap.py",       (16, 128),         "int32",    1000),
]


def _load_env() -> None:
    env_path = ROOT / ".env"
    if env_path.is_file():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key, value.strip())


def _setup_path() -> None:
    for entry in (str(ROOT), str(ROOT / "ops" / "harness")):
        if entry not in sys.path:
            sys.path.insert(0, entry)


_load_env()
_setup_path()

from compiler_api.run_cases import enumerate_cases  # noqa: E402
from opslib import compare as compare_lib           # noqa: E402
from opslib import golden                           # noqa: E402
from a100_support.native_io import pack_case, unpack_outputs  # noqa: E402
from a100c.factory import make_compiler             # noqa: E402


def spec_for(corpus_rel: str):
    """The OperatorSpec for one operator file, via the harness's own path."""
    got = list(enumerate_cases(channel="all", group=None, operators=None,
                               paths=[corpus_rel]))
    if not got:
        raise RuntimeError(f"no supported spec for {corpus_rel}")
    return got[0][0]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def smoke(exe: Path, bundle_dir: Path, case: dict, threads: int) -> dict:
    """Run the exact shipped pair under QEMU once and compare to the reference."""
    with tempfile.TemporaryDirectory(prefix="pack-smoke-") as td:
        td = Path(td)
        shutil.copy2(bundle_dir / "bundle.bin", td / "bundle.bin")
        shutil.copy2(bundle_dir / "bundle.json", td / "bundle.json")
        cmd = [str(RUN_RISCV), str(exe), "--bundle", str(td / "bundle.bin"),
               "--threads", str(threads)]
        began = time.perf_counter()
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True,
                                  timeout=SMOKE_TIMEOUT)
        except subprocess.TimeoutExpired:
            return {"ok": False, "detail": f"timeout after {SMOKE_TIMEOUT}s"}
        seconds = round(time.perf_counter() - began, 1)
        if proc.returncode:
            return {"ok": False, "detail":
                    f"exit {proc.returncode}: {(proc.stderr or proc.stdout)[-300:]}"}
        if '"status":"ok"' not in proc.stdout:
            return {"ok": False, "detail":
                    f"runtime status: {proc.stdout.strip()[:200]}"}
        try:
            verdict = compare_lib.compare_case(case, unpack_outputs(td))
            return {"ok": True, "qemu_seconds": seconds,
                    "max_abs_error": verdict.get("max_abs_error", {})}
        except Exception as exc:  # noqa: BLE001 - comparison verdict
            return {"ok": False, "detail": str(exc).splitlines()[0][:300]}


def main() -> int:
    cache_root = ROOT / "a100c" / "cache"
    pre_existing = set(os.listdir(cache_root)) if cache_root.is_dir() else set()
    compiler = make_compiler()

    (PACK / "bin").mkdir(exist_ok=True)
    (PACK / "cases").mkdir(exist_ok=True)

    manifest = {"schema": "board-perf-pack/v1",
                "created": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "seed": SEED,
                "runtime_cli": "operator_exec --bundle <b> --threads <1|2|4|8> [--repeats <k>]",
                "board_cpus": "8-15 (A100 AI cores; 0-7 are the system cores)",
                "cases": []}
    runnable = []

    for name, corpus_rel, shape, dtype, repeats in CASES:
        print(f"[{name}] {corpus_rel} shape={shape} dtype={dtype}", flush=True)
        spec = spec_for(corpus_rel)
        case = golden.load_or_build_spec(spec, shape=list(shape), dtype=dtype,
                                         seed=SEED, use_cache=True)

        compile_input = {k: v for k, v in case.items()
                         if k not in ("expected", "oracle_args")}
        artifact = compiler.compile_case(compile_input)
        exe = Path(artifact.executable).resolve()
        if not exe.is_file():
            print(f"[{name}] ERROR: no executable produced", flush=True)
            continue
        fresh = exe.parent.name not in pre_existing
        head = exe.read_bytes()[:20]
        if head[:6] != b"\x7fELF\x02\x01" or head[18:20] != b"\xf3\x00":
            print(f"[{name}] ERROR: not a RISC-V ELF64", flush=True)
            continue

        bundle_dir = PACK / "cases" / name
        if bundle_dir.exists():
            shutil.rmtree(bundle_dir)
        pack_case(case, bundle_dir)
        bin_dir = PACK / "bin" / name
        if bin_dir.exists():
            shutil.rmtree(bin_dir)
        bin_dir.mkdir(parents=True)
        shutil.copy2(exe, bin_dir / "operator_exec")
        os.chmod(bin_dir / "operator_exec", 0o755)

        entry = {"name": name, "operator": corpus_rel, "shape": list(shape),
                 "dtype": dtype, "board_repeats": repeats,
                 "artifact": {"cache_id": exe.parent.name,
                              "sha256": sha256_file(exe),
                              "fresh_compile": fresh,
                              "arguments": list(artifact.arguments)},
                 "bundle_bytes": (bundle_dir / "bundle.bin").stat().st_size,
                 "smoke": {}}
        manifest["cases"].append(entry)

        ok_all = True
        for threads in (1, 8):
            result = smoke(exe, bundle_dir, case, threads)
            entry["smoke"][f"threads_{threads}"] = result
            print(f"[{name}] smoke threads={threads}: "
                  f"{'PASS' if result['ok'] else 'FAIL ' + result.get('detail', '')}"
                  f" ({result.get('qemu_seconds', '?')}s under QEMU)", flush=True)
            ok_all = ok_all and result["ok"]
        if ok_all:
            runnable.append(f"{name}:{repeats}")
        else:
            print(f"[{name}] DROPPED from cases.conf (smoke failed)", flush=True)

        (PACK / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    (PACK / "cases.conf").write_text(
        "# name:board_repeats  (generated by stage_pack.py; only smoke-passing cases)\n"
        + "\n".join(runnable) + "\n")
    print(f"\nrunnable cases: {len(runnable)}/{len(CASES)} -> cases.conf", flush=True)
    print("manifest ->", PACK / "manifest.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
