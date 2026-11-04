"""CudaDevice: the torch-free CUDA path (cuda-python + raw pointers).

The GPU tests run natively on the card in a subprocess with a scrubbed
environment: other test modules set ``TRITON_INTERPRET=1`` per call (the
host-interpreter executor), and whether a kernel is interpreted is decided
at ``@triton.jit`` decoration time -- so sharing one process would poison
either side.  In the subprocess there is no interpreter: kernels launch on
the GPU exactly like the benchmark paths do.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1]     # <root>/harness
ROOT = HARNESS.parent                               # the corpus root

cudart = pytest.importorskip("cuda.bindings.runtime")

# GPU availability via cuda-python itself: these tests must run in
# torch-free environments -- that is the device they cover.
err, _count = cudart.cudaGetDeviceCount()
pytestmark = pytest.mark.skipif(
    int(err) != 0 or _count < 1, reason="requires a CUDA GPU")


# ----------------------------------------------------------- native payload
def _payload() -> int:
    """Runs in the subprocess: real GPU launches, no interpreter."""
    import numpy as np
    from opslib import compare as compare_lib
    from opslib.devices import cuda as cuda_mod
    from opslib.devices.cuda import CudaDevice, _type_name
    from triton.runtime.jit import mangle_type

    failures = []

    def check(name, fn):
        try:
            fn()
            print(f"PASS {name}", flush=True)
        except Exception as exc:  # noqa: BLE001
            failures.append(name)
            print(f"FAIL {name}: {type(exc).__name__}: {exc}", flush=True)

    device = CudaDevice()

    def dtype_markers_are_singletons():
        """Regression: triton's specialization cache keys by object identity;
        a recycled dtype marker made an fp16 cubin run on fp32 pointers and
        silently write half the buffer."""
        assert _type_name("float32") is _type_name("float32")
        assert _type_name("float16") is not _type_name("float32")
        assert str(_type_name("int64")) == "int64"
        err, ptr = cuda_mod.cudart.cudaMalloc(64)
        try:
            results = []
            for _ in range(50):  # object churn: recycled memory slots
                buffer = cuda_mod.CudaBuffer(ptr, _type_name("float16"), (8,), None)
                results.append(mangle_type(buffer, True))
                del buffer
            assert set(results) == {"*fp16"}
        finally:
            cuda_mod.cudart.cudaFree(ptr)

    def upload_download_roundtrip():
        rng = np.random.default_rng(3)
        for dtype in (np.float16, np.float32, np.float64, np.int32, np.int64,
                      np.uint16, np.int8):
            array = (rng.standard_normal(4097) * 3).astype(dtype)
            buffer = device.upload(array)
            assert str(buffer.dtype) == np.dtype(dtype).name
            np.testing.assert_array_equal(device.download(buffer), array)
            buffer.free()

    def bf16_view_and_cast():
        bits = np.array([0x3F80, 0xBF80, 0x0000, 0x7FC0], dtype=np.uint16)
        buffer = device.upload(bits, "bfloat16")
        assert str(buffer.dtype) == "bfloat16"
        np.testing.assert_array_equal(device.download(buffer), bits)
        buffer.free()
        # host float32 -> RNE cast; download widens back to the host dtype
        values = np.array([1.0, -1.0, 0.5, 1e-40, np.nan, 3.0], dtype=np.float32)
        buffer = device.upload(values, "bfloat16")
        back = device.download(buffer)
        expected = cuda_mod._from_bf16_bits(cuda_mod._to_bf16_bits(values))
        np.testing.assert_array_equal(back, expected)
        assert np.isnan(back[4])
        np.testing.assert_array_equal(back[:3], values[:3])
        assert 0.0 < back[3] < 1e-35        # 1e-40 rounds to a bf16 subnormal
        buffer.free()

    def pointer_table_relocation():
        from opslib import runner
        from opslib.device import run_case
        op = runner.load_operator(ROOT / "suite" / "dev" / "scatter_atomic_kernel.py")
        case = op.make_case(shape=op.SHAPES[0], dtype=op.DTYPES[0], seed=30)
        outputs = run_case(case, device)
        compare_lib.compare_case(case, outputs)

    def device_compare_matches_host():
        rng = np.random.default_rng(11)
        for trial in range(30):
            n = 4096
            reference = rng.standard_normal(n).astype(np.float32)
            scale = [0.0, 1e-5, 1e-4, 1e-2][trial % 4]
            actual = reference + (rng.standard_normal(n) * scale).astype(np.float32)
            if trial % 5 == 0:
                actual[7] = np.inf
            if trial % 7 == 0:
                actual[11] = np.nan
                reference[11] = np.nan
            actual_buf = device.upload(actual)
            ok_dev, err_dev = device.compare(actual_buf, reference,
                                             {"rtol": 1e-4, "atol": 1e-4,
                                              "equal_nan": True})
            actual_buf.free()
            close = np.isclose(actual, reference, rtol=1e-4, atol=1e-4, equal_nan=True)
            delta = np.abs(actual.astype(np.float64) - reference.astype(np.float64))
            equal = actual == reference
            equal = equal | (np.isnan(actual) & np.isnan(reference))
            err_host = float(np.where(equal, 0.0, delta).max(initial=0.0))
            assert ok_dev == bool(close.all())
            assert err_dev == pytest.approx(err_host, rel=1e-12, abs=1e-300), trial

    def timer_and_properties():
        buffer = device.upload(np.zeros(64, np.float32))
        with device.timer() as timer:
            device.synchronize()
        assert 0.0 <= timer.seconds < 5.0
        buffer.free()
        props = device.properties()
        assert props["name"]
        assert props["llc_bytes"] > 1 << 20
        assert props["sm_count"] > 0

    def h2d_bandwidth():
        size = 1 << 30
        data = np.random.default_rng(0).standard_normal(size // 4).astype(np.float32)
        import time
        buffer = device.alloc(data.shape, "float32")
        device._copy_to_device(buffer, data.ctypes.data, data.nbytes)  # warm
        best = None
        for _ in range(3):
            t0 = time.perf_counter()
            device._copy_to_device(buffer, data.ctypes.data, data.nbytes)
            best = min(best or 1e9, time.perf_counter() - t0)
        buffer.free()
        gbs = data.nbytes / best / 2**30
        print(f"INFO h2d-pinned-1GiB {gbs:.1f} GiB/s", flush=True)
        assert gbs > 1.0        # a healthy pinned path clears PCIe-ish rates

    for name, fn in (("dtype-markers", dtype_markers_are_singletons),
                     ("roundtrip", upload_download_roundtrip),
                     ("bf16", bf16_view_and_cast),
                     ("pointer-tables", pointer_table_relocation),
                     ("device-compare", device_compare_matches_host),
                     ("timer-properties", timer_and_properties),
                     ("h2d-bandwidth", h2d_bandwidth)):
        check(name, fn)
    return 1 if failures else 0


# ---------------------------------------------------------- pytest wrappers
def _run_native(selection: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.pop("TRITON_INTERPRET", None)
    return subprocess.run(
        [sys.executable, str(Path(__file__)), "--native", selection],
        capture_output=True, text=True, timeout=600, env=env, cwd=str(ROOT))


def test_cuda_device_native_suite():
    result = _run_native("all")
    assert result.returncode == 0, result.stdout + result.stderr
    for line in result.stdout.splitlines():
        if line.startswith("INFO"):
            print(line)      # bandwidth evidence for the commit message


def test_cuda_device_survives_dtype_churn():
    """The full perf lane through the cuda device (f16/f32 churn was the
    original silent-corruption trigger)."""
    import json
    env = dict(os.environ)
    env.pop("TRITON_INTERPRET", None)
    script = (
        "import sys; sys.path.insert(0, 'harness')\n"
        # stock Triton's autotuner imports torch (do_bench); the perf lane has
        # autotuned operators, so this reference run allows it
        "sys.argv.append('--allow-torch')\n"
        "from collections import Counter\n"
        "from compiler_api.run_cases import run_all\n"
        "from opslib.devices.cuda import CudaDevice\n"
        "rows = run_all(CudaDevice(), channel='local', group='suite/perf')\n"
        "print(Counter(r['status'] for r in rows), len(rows))\n"
    )
    result = subprocess.run([sys.executable, "-c", script], capture_output=True,
                            text=True, timeout=900, env=env, cwd=str(ROOT))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "CASE_FAIL" not in result.stdout and "LAUNCH_FAIL" not in result.stdout \
        and "MISMATCH" not in result.stdout, result.stdout + result.stderr
    import re as _re
    counted = _re.search(r"PASS': (\d+)\}\) (\d+)", result.stdout)
    assert counted and int(counted.group(1)) == int(counted.group(2)) >= 100, \
        result.stdout + result.stderr


if __name__ == "__main__":
    sys.path.insert(0, str(HARNESS))
    raise SystemExit(_payload())
