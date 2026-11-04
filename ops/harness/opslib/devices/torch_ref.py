"""Optional torch-backed reference devices.

These adapters use torch only as a *reference host/device runtime*; the
operator files and the ``Device`` protocol stay torch-free.  For a torch-free
GPU device see ``opslib.devices.cuda``.

    from opslib.devices.torch_ref import TorchGpuDevice
    from compiler_api.run_cases import run_all
    rows = run_all(TorchGpuDevice(), channel="all")

- ``TorchGpuDevice``: torch CUDA tensors + native Triton launch.  Validated at
  **4426/4426** on the corpus (923 operators).
- ``TorchCpuInterpreterDevice``: torch CPU tensors + the Triton interpreter.
  Requires the process to start with ``TRITON_INTERPRET=1``.
"""
from __future__ import annotations

import numpy as np

try:
    import torch
except ImportError:  # pragma: no cover - optional dependency
    torch = None

from opslib.device import Buffer, Device


def _torch_dtype(name):
    return getattr(torch, str(name).rsplit(".", 1)[-1])


def _flat_bytes(start, stop):
    """Host copy of [start, stop); chunked because ctypes.string_at's size
    argument is a 32-bit C int and a >2GiB span overflows it."""
    import ctypes
    size = stop - start
    if size <= 0:
        raise ValueError(f"non-positive flat span {size}")
    chunk = 1 << 30
    if size <= chunk:
        return ctypes.string_at(start, size)
    buf = bytearray(size)
    for offset in range(0, size, chunk):
        n = min(chunk, size - offset)
        buf[offset:offset + n] = ctypes.string_at(start + offset, n)
    return bytes(buf)


class TorchBuffer(Buffer):
    def __init__(self, tensor, host_dtype=None):
        self.tensor = tensor
        self.host_dtype = host_dtype

    def data_ptr(self):
        return self.tensor.data_ptr()

    @property
    def dtype(self):
        return self.tensor.dtype

    @property
    def shape(self):
        return tuple(self.tensor.shape)


class TorchEventTimer:
    """CUDA-event timing context (torch events), mirroring CudaEventTimer."""

    def __init__(self):
        self._start = torch.cuda.Event(enable_timing=True)
        self._end = torch.cuda.Event(enable_timing=True)
        self._seconds = None

    def __enter__(self):
        self._start.record()
        return self

    def __exit__(self, *exc):
        self._end.record()
        self._end.synchronize()
        self._seconds = self._start.elapsed_time(self._end) / 1000.0
        return False

    @property
    def seconds(self):
        if self._seconds is None:
            raise RuntimeError("timer read before its context exited")
        return self._seconds


class _TorchDevice(Device):
    device = "cuda"

    def __init__(self, device: str | None = None):
        if torch is None:
            raise RuntimeError("TorchGpuDevice/TorchCpuInterpreterDevice need torch installed")
        if device is not None:
            self.device = str(device)          # e.g. "cuda" or "cuda:3"

    def _ctx(self):
        """CUDA-device context so launches and syncs hit *this* device
        (torch.cuda.synchronize() alone would target the current one)."""
        import contextlib
        if self.device == "cpu" or not str(self.device).startswith("cuda"):
            return contextlib.nullcontext()
        return torch.cuda.device(self.device)

    def alloc(self, shape, dtype):
        with self._ctx():
            return TorchBuffer(torch.empty(tuple(int(x) for x in shape),
                                           dtype=_torch_dtype(dtype),
                                           device=self.device))

    def upload(self, array, dtype=None):
        host_dtype = array.dtype
        contiguous = np.ascontiguousarray(array)
        if not contiguous.flags.writeable:    # e.g. a golden-cache mmap
            contiguous = contiguous.copy()
        tensor = torch.from_numpy(contiguous)
        if dtype is not None:
            name = str(dtype).rsplit(".", 1)[-1]
            if name == "bfloat16":
                tensor = (tensor.view(torch.bfloat16) if host_dtype == np.uint16
                          else tensor.to(torch.bfloat16))
            elif not str(tensor.dtype).endswith(name):
                tensor = tensor.to(_torch_dtype(name))
        if self.device != "cpu":
            with self._ctx():
                tensor = tensor.to(self.device)
        return TorchBuffer(tensor, host_dtype)

    def upload_aliased(self, group, pointer_types):
        """Upload host arrays that share one storage as ONE device
        allocation with strided views, preserving the aliasing the kernel
        is supposed to observe (writes through one name visible via the
        other).  ``group`` maps name -> ndarray."""
        with self._ctx():
            names = list(group)
            first = group[names[0]]
            kind = str(pointer_types.get(names[0], first.dtype)).rsplit(".", 1)[-1]
            lower, upper = [], []
            for name in names:
                array = group[name]
                entry_kind = str(pointer_types.get(name, array.dtype)).rsplit(".", 1)[-1]
                if array.dtype != first.dtype or entry_kind != kind:
                    raise ValueError("Aliased buffers must have matching storage and pointer types")
                address = array.ctypes.data
                extent = (sum((dim - 1) * stride for dim, stride in
                              zip(array.shape, array.strides)) + array.itemsize
                          if array.size else 0)
                lower.append(address)
                upper.append(address + extent)
            start, stop = min(lower), max(upper)
            dtype = _torch_dtype(kind)
            flat = np.frombuffer(_flat_bytes(start, stop),
                                 dtype=first.dtype).copy()
            tensor = torch.from_numpy(flat)
            if kind == "bfloat16" and first.dtype == np.uint16:
                tensor = tensor.view(torch.bfloat16)
            else:
                tensor = tensor.to(dtype)
            tensor = tensor.to(self.device)
            buffers = {}
            for name in names:
                array = group[name]
                offset = (array.ctypes.data - start) // array.itemsize
                strides = tuple(stride // array.itemsize for stride in array.strides)
                buffers[name] = TorchBuffer(
                    torch.as_strided(tensor, array.shape, strides, offset),
                    array.dtype)
            return buffers

    def download(self, buffer):
        tensor = buffer.tensor
        if tensor.dtype == torch.bfloat16:
            tensor = (tensor.cpu().view(torch.uint16) if buffer.host_dtype == np.uint16
                      else tensor.cpu().float())
            return tensor.numpy().copy()
        return tensor.cpu().numpy().copy()

    def launch(self, kernel, grid, positional, keywords):
        args = [v.tensor if isinstance(v, TorchBuffer) else v for v in positional]
        with self._ctx():
            if str(self.device).startswith("cuda"):
                import triton
                triton.set_allocator(self._allocate_scratch)
            return kernel[grid](*args, **keywords)

    def _allocate_scratch(self, size, alignment, stream):
        with self._ctx():
            storage = torch.empty(int(size) + int(alignment), dtype=torch.uint8,
                                  device=self.device)
            offset = (-storage.data_ptr()) % int(alignment)
            return storage[offset:offset + int(size)]

    def synchronize(self):
        if self.device != "cpu":
            with self._ctx():
                torch.cuda.synchronize()

    def timer(self):
        if self.device == "cpu":
            raise RuntimeError("event timing needs a CUDA device")
        return TorchEventTimer()

    def properties(self):
        if self.device == "cpu":
            return {}
        props = torch.cuda.get_device_properties(self.device)
        return {
            "name": props.name,
            "llc_bytes": getattr(props, "L2_cache_size", None),
            "sm_count": props.multi_processor_count,
            "driver": torch.version.cuda,
            "device": str(self.device),
        }

    def compare(self, buffer, expected, policy):
        """On-device allclose, bit-compatible with the host comparison.

        Replicates ``np.isclose``'s exact expression and dtype (python
        scalars are weak, so the tolerance math stays in the array dtype),
        and the informational float64 max-abs-error metric.
        """
        if not isinstance(buffer, TorchBuffer):
            return None
        actual = buffer.tensor
        reference = np.ascontiguousarray(expected)
        if not reference.flags.writeable:  # e.g. a golden-cache mmap
            reference = reference.copy()
        if reference.dtype.kind != "f":
            return None
        # The expected array must live in the same dtype the buffer was
        # uploaded from; otherwise the host path's dtype promotion differs.
        if buffer.host_dtype is not None and reference.dtype != buffer.host_dtype:
            return None
        desired = torch.from_numpy(reference).to(actual.device)
        rtol = float(policy["rtol"])
        atol = float(policy["atol"])
        equal_nan = bool(policy.get("equal_nan", False))
        with torch.no_grad():
            # numpy isclose: (|x-y| <= atol + rtol*|y|) & isfinite(y) | x == y
            tolerance = atol + rtol * desired.abs()
            close = (((actual - desired).abs() <= tolerance)
                     & torch.isfinite(desired) | (actual == desired))
            if equal_nan:
                close = close | (actual.isnan() & desired.isnan())
            ok = bool(close.all())
            delta = (actual.double() - desired.double()).abs()
            equal = actual == desired
            if equal_nan:
                equal = equal | (actual.isnan() & desired.isnan())
            if delta.numel():
                error = float(torch.where(equal, torch.zeros_like(delta), delta).max())
            else:
                error = 0.0
        return ok, error


class TorchGpuDevice(_TorchDevice):
    """Reference GPU device: torch CUDA tensors + native Triton launch."""
    device = "cuda"


class TorchCpuInterpreterDevice(_TorchDevice):
    """Reference CPU device: torch CPU tensors + the Triton interpreter.

    Start the process with ``TRITON_INTERPRET=1`` or the native launch will
    fail (stock Triton has no native CPU launch).
    """
    device = "cpu"


def interpret_launch(kernel, grid, positional, keywords):
    """Launch through the Triton interpreter (needs torch host tensors).

    Used by ``CpuDevice`` when the process started with
    ``TRITON_INTERPRET=1``; the only torch use outside the Torch* devices.
    """
    import torch
    from opslib.device import HostBuffer
    args = [torch.from_numpy(v.array) if isinstance(v, HostBuffer) else v
            for v in positional]
    return kernel[grid](*args, **keywords)
