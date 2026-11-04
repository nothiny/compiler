"""The cuda correctness path must complete without torch in the process."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1]     # <root>/harness
ROOT = HARNESS.parent                               # the corpus root


def _cuda_available():
    try:
        import cuda.bindings.runtime as cudart
        err, count = cudart.cudaGetDeviceCount()
        return not int(err) and count >= 1
    except Exception:
        return False


@pytest.mark.skipif(not _cuda_available(), reason="no CUDA device")
def test_run_cases_cuda_has_no_torch():
    from opslib.runner import load_operator

    op = load_operator(ROOT / "suite" / "dev" / "argmin_tiled_kernel.py")
    expected = len(op.SHAPES) * len(op.DTYPES)
    code = (
        "import sys; sys.path.insert(0, {root!r}); "
        "sys.argv = ['run_cases.py', '--device', 'cuda', "
        "'--operator', 'suite/dev/argmin_tiled_kernel.py']; "
        "from compiler_api import run_cases; run_cases.main(); "
        "print('TORCH_PRESENT' if 'torch' in sys.modules else 'TORCH_ABSENT')"
    ).format(root=str(HARNESS))
    result = subprocess.run([sys.executable, "-c", code], capture_output=True,
                            text=True, timeout=600, cwd=str(ROOT))
    assert result.returncode == 0, result.stdout + result.stderr
    assert f'"PASS": {expected}' in result.stdout, result.stdout[-2000:]
    assert "TORCH_ABSENT" in result.stdout
