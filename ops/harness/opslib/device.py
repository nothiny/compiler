"""Device-agnostic, torch-free execution of one operator case.

Operator files only describe a case with NumPy arrays and a single
``@triton.jit`` kernel.  All staging (host<->device), launch and read-back
live behind a tiny ``Device`` interface, so the same corpus runs on a CPU
backend and a GPU backend, and the operator files never import torch.

A compiler only needs to implement one ``Device`` subclass:

    class MyDevice(Device):
        def alloc(self, shape, dtype): ...        # -> Buffer
        def upload(self, array): ...              # np.ndarray -> Buffer
        def download(self, buffer): ...           # Buffer -> np.ndarray
        def launch(self, kernel, grid, positional, keywords): ...

Then ``run_case(case, MyDevice(...))`` stages the case's NumPy args,
launches the kernel, and returns NumPy outputs.  ``run_case`` never calls
torch; it only uses NumPy and the kernel object.
"""
from __future__ import annotations

import inspect
import os

import numpy as np

# The suite-v3 subset declares fp32 ``tl.dot`` as IEEE: exactly two dot
# semantics exist (bf16/fp16 operands with fp32 accumulation, fp32 operands
# computed exactly).  Stock Triton's NVIDIA default is tf32, a vendor
# reduced-mantissa format, so the runner pins the knob before any operator
# imports Triton.  An explicit caller setting always wins.  Operator files
# never mention this: no operator passes ``input_precision=`` or
# ``allow_tf32=``.
os.environ.setdefault("TRITON_F32_DEFAULT", "ieee")


# --------------------------------------------------------------------- Buffer
class Buffer:
    """Opaque device buffer.

    ``data_ptr`` and ``dtype``/``shape`` are the minimal surface a Triton
    launcher needs; a GPU backend can wrap a raw CUDA pointer without torch.
    """

    def data_ptr(self):  # pragma: no cover - interface
        raise NotImplementedError

    @property
    def dtype(self):  # pragma: no cover - interface
        raise NotImplementedError

    @property
    def shape(self):  # pragma: no cover - interface
        raise NotImplementedError


class HostBuffer(Buffer):
    """A CPU buffer: just a NumPy array."""

    def __init__(self, array: np.ndarray):
        self.array = array

    def data_ptr(self):
        return self.array.ctypes.data

    @property
    def dtype(self):
        return self.array.dtype

    @property
    def shape(self):
        return self.array.shape

    def __array__(self, dtype=None):
        return np.asarray(self.array, dtype=dtype)


# --------------------------------------------------------------------- Device
class Device:
    """The compiler side of the contract.  Subclass and implement the
    primitives (``alloc``/``upload``/``download``/``launch``, and ``pointer``
    only if the corpus uses pointer tables); everything else (argument
    binding, read-back) is generic."""

    name = "abstract"

    def alloc(self, shape, dtype) -> Buffer:  # pragma: no cover - interface
        raise NotImplementedError

    def upload(self, array: np.ndarray, dtype=None) -> Buffer:  # pragma: no cover
        raise NotImplementedError

    def download(self, buffer: Buffer) -> np.ndarray:  # pragma: no cover
        raise NotImplementedError

    def pointer(self, buffer: Buffer) -> int:
        """Device address of ``buffer`` (used to patch pointer tables)."""
        return buffer.data_ptr()

    def synchronize(self) -> None:
        """Block until prior launches finish (for device-anchored timing)."""
        return None

    def compare(self, buffer: Buffer, expected: np.ndarray, policy: dict):
        """Optional on-device comparison of one output buffer.

        Implementations evaluate the plain-float ``allclose`` policy
        (``|a - b| <= atol + rtol * |b|`` with the usual NaN/equality
        handling, arithmetic in the buffers' dtype) on the device and return
        ``(ok, max_abs_error)`` with only scalars crossing back to the host.
        Return ``None`` if the buffer/policy is not supported; the caller
        then downloads the outputs and compares on the host.
        """
        return None

    def launch(self, kernel, grid, positional, keywords) -> None:  # pragma: no cover
        raise NotImplementedError


class CpuDevice(Device):
    """Reference CPU device.

    ``launcher`` is the intended path: route the launch into your compiler
    runtime with ``launcher(kernel, grid, positional, keywords)``.

    With no launcher, stock Triton 3.8 cannot run a kernel natively on the
    CPU (it requires CUDA pointers).  The only self-contained fallback is the
    Triton **interpreter**: start the process with ``TRITON_INTERPRET=1`` and
    have torch installed, and this device converts its ``HostBuffer``s to
    torch CPU tensors before launch.  Otherwise it raises a clear error
    telling you to inject a launcher.
    """

    name = "cpu"

    def __init__(self, launcher=None):
        self.launcher = launcher

    def alloc(self, shape, dtype):
        return HostBuffer(np.empty(tuple(int(x) for x in shape), dtype=np.dtype(dtype)))

    def upload(self, array, dtype=None):
        name = None if dtype is None else str(dtype).rsplit(".", 1)[-1]
        try:
            npd = np.dtype(name) if name is not None else None
        except TypeError:
            npd = None  # e.g. bfloat16: keep the raw storage (uint16) as-is
        if npd is not None and npd != array.dtype:
            return HostBuffer(array.astype(npd))
        return HostBuffer(np.array(array, copy=True))

    def download(self, buffer):
        return np.asarray(buffer.array).copy()

    def _default_launch(self, kernel, grid, positional, keywords):
        import os
        if os.environ.get("TRITON_INTERPRET") != "1":
            raise RuntimeError(
                "CpuDevice: stock Triton cannot launch a kernel natively on the CPU. "
                "Pass launcher=<your compiler runtime> to CpuDevice(...), or run with "
                "TRITON_INTERPRET=1 (plus torch) to use the Triton interpreter.")
        try:
            from opslib.devices.torch_ref import interpret_launch
        except ImportError as exc:
            raise RuntimeError(
                "CpuDevice: the CPU interpreter fallback needs torch (host tensors). "
                "Pass launcher=<your compiler runtime> instead.") from exc
        return interpret_launch(kernel, grid, positional, keywords)

    def launch(self, kernel, grid, positional, keywords):
        if self.launcher is not None:
            return self.launcher(kernel, grid, positional, keywords)
        return self._default_launch(kernel, grid, positional, keywords)


class GpuDevice(Device):
    """GPU device with pluggable, torch-free allocator and copiers.

    The caller supplies ``alloc``/``upload``/``download`` (their hand-written
    cudaMalloc / cudaMemcpy, or any non-torch CUDA binding).  ``launcher``
    defaults to the native Triton launch, which only needs the buffer objects
    to expose ``data_ptr()``/``dtype``.
    """

    name = "gpu"

    def __init__(self, alloc, upload, download, launcher=None):
        self._alloc = alloc
        self._upload = upload
        self._download = download
        self.launcher = launcher

    def alloc(self, shape, dtype):
        return self._alloc(shape, dtype)

    def upload(self, array, dtype=None):
        try:
            accepts = "dtype" in inspect.signature(self._upload).parameters
        except (TypeError, ValueError):
            accepts = False
        return self._upload(array, dtype) if accepts else self._upload(array)

    def download(self, buffer):
        return self._download(buffer)

    def launch(self, kernel, grid, positional, keywords):
        if self.launcher is not None:
            return self.launcher(kernel, grid, positional, keywords)
        kernel[grid](*positional, **keywords)


# ------------------------------------------------------------------ utilities
def _kernel_target(kernel):
    target = kernel
    for _ in range(8):
        if inspect.isfunction(target):
            return target
        nested = getattr(target, "fn", None)
        if nested is None or nested is target:
            return target
        target = nested
    return target


def kernel_parameters(kernel):
    try:
        return list(inspect.signature(_kernel_target(kernel)).parameters)
    except (TypeError, ValueError):
        return []


def bind_arguments(kernel, values):
    """Build the positional argument list for ``kernel[grid](...)`` from the
    kernel signature and the merged ``args``/``meta`` value map.

    Mirrors the runner: autotune-supplied constexprs are skipped, parameters
    with defaults fall back to the default, ``KEYWORD_ONLY`` params become
    keywords.
    """
    configs = getattr(kernel, "configs", None)
    autotune_meta = set((getattr(configs[0], "kwargs", {}) or {}).keys()) if configs else set()
    try:
        parameters = inspect.signature(_kernel_target(kernel)).parameters
    except (TypeError, ValueError):
        parameters = {}
    positional, keywords = [], {}
    for name, parameter in parameters.items():
        if name in values:
            value = values[name]
        elif name in autotune_meta:
            continue  # the autotuner supplies this constexpr itself
        elif parameter.default is not inspect.Parameter.empty:
            value = parameter.default
        else:
            raise KeyError(f"missing kernel argument {name!r}")
        if parameter.kind == inspect.Parameter.KEYWORD_ONLY:
            keywords[name] = value
        else:
            positional.append(value)
    return positional, keywords


def _device_upload(device, array, dtype):
    """Call ``device.upload`` passing ``dtype`` only if it accepts it, so a
    Device written against the 1-arg signature keeps working."""
    try:
        accepts = "dtype" in inspect.signature(device.upload).parameters
    except (TypeError, ValueError):
        accepts = False
    return device.upload(array, dtype) if accepts else device.upload(array)


def patch_pointer_tables(case, host, device, buffers):
    """Apply the case's pointer-table relocations after staging.

    Operators that pass pointers through a device-side table declare
    ``pointer_table_relocations`` (or the legacy ``pointer_relocations``);
    the entries must be overwritten with device addresses of the other
    buffers before launch.
    """
    relocations = []
    for item in case.get("pointer_table_relocations", ()) or ():
        relocations.append({
            "table": item.get("table", item.get("table_arg")),
            "entry": item.get("entry", item.get("element_index")),
            "allocation": item.get("allocation", item.get("allocation_arg")),
            "byte_offset": item.get("byte_offset", 0),
        })
    legacy = case.get("pointer_relocations", ()) or {}
    if isinstance(legacy, dict):
        for table, entries in legacy.items():
            for item in entries:
                relocations.append({
                    "table": table,
                    "entry": item.get("index", item.get("element_index")),
                    "allocation": item.get("allocation", item.get("allocation_arg")),
                    "byte_offset": item.get("element_offset", 0)
                    * int(np.asarray(host[item.get("allocation", item.get("allocation_arg"))]).itemsize)
                    + item.get("byte_offset", 0),
                })
    else:
        for item in legacy:
            relocations.append({
                "table": item.get("table", item.get("table_arg")),
                "entry": item.get("entry", item.get("element_index")),
                "allocation": item.get("allocation", item.get("allocation_arg")),
                "byte_offset": item.get("byte_offset", 0),
            })
    if not relocations:
        return
    pointer_types = case.get("pointer_dtypes", {}) or {}
    tables = {}
    for item in relocations:
        table = item["table"]
        if table not in tables:
            tables[table] = np.array(host[table], copy=True)
        tables[table].reshape(-1)[int(item["entry"])] = (
            device.pointer(buffers[item["allocation"]]) + int(item.get("byte_offset", 0)))
    for table, array in tables.items():
        buffers[table] = _device_upload(device, array, pointer_types.get(table))


class StagedCase:
    """A staged case: buffers on the device, arguments bound.

    ``launch()`` only launches the kernel(s) -- no host staging -- so a driver
    can time the **kernel**, not the host<->device copy.  ``outputs()``
    downloads the outputs for a correctness check.
    """

    def __init__(self, case, device, buffers, kernel):
        self._case = case
        self._device = device
        self._buffers = buffers
        self._kernel = kernel

    def buffer(self, name):
        """One staged device buffer (for on-device comparison)."""
        return self._buffers[name]

    def launch(self) -> None:
        case, device, buffers = self._case, self._device, self._buffers
        for overrides in case.get("launches", ({},)):
            values = {**buffers, **case.get("meta", {}), **overrides}
            values = {name: (value.item() if isinstance(value, np.generic) else value)
                      for name, value in values.items()}
            positional, keywords = bind_arguments(self._kernel, values)
            device.launch(self._kernel, case["grid"], positional,
                          {**keywords, **case.get("launch_meta", {})})

    def outputs(self) -> dict:
        return {name: self._device.download(self._buffers[name])
                for name in self._case["outputs"]}


def _overlap_groups(arrays: dict) -> list[list[str]]:
    """Union-find the array names into groups that share host memory."""
    names = list(arrays)
    parent = {name: name for name in names}

    def find(name):
        while parent[name] != name:
            parent[name] = parent[parent[name]]
            name = parent[name]
        return name

    for i, left in enumerate(names):
        for right in names[i + 1:]:
            if np.shares_memory(arrays[left], arrays[right]):
                parent[find(left)] = find(right)
    groups: dict[str, list[str]] = {}
    for name in names:
        groups.setdefault(find(name), []).append(name)
    return list(groups.values())


def stage_case(case: dict, device: Device, kernel=None) -> StagedCase:
    """Upload the case's inputs once and bind the kernel arguments.

    The returned object launches without re-staging, for kernel-anchored
    timing.  Host arrays that share one storage are uploaded as **one**
    device allocation (via the device's optional ``upload_aliased``) so the
    kernel observes the aliasing; a device without that hook fails loudly
    on such cases instead of silently staging them as unrelated buffers.
    """
    custom_stage = getattr(device, "stage_case", None)
    if callable(custom_stage):
        return custom_stage(case, kernel=kernel)
    kernel = kernel if kernel is not None else case.get("kernel")
    if kernel is None:
        raise ValueError("case has no kernel")
    host = {**case.get("allocations", {}), **case.get("args", {})}
    pointer_types = case.get("pointer_dtypes", {}) or {}
    arrays = {name: value for name, value in host.items()
              if isinstance(value, np.ndarray)}
    buffers = {}
    for group in _overlap_groups(arrays):
        members = {name: arrays[name] for name in group}
        if len(group) > 1:
            upload_aliased = getattr(device, "upload_aliased", None)
            if upload_aliased is None:
                raise RuntimeError(
                    f"{type(device).__name__} cannot stage aliased host "
                    f"buffers ({', '.join(sorted(group))}): implement "
                    "upload_aliased() or de-alias the case")
            buffers.update(upload_aliased(members, pointer_types))
        else:
            name = group[0]
            buffers[name] = _device_upload(device, members[name],
                                           pointer_types.get(name))
    for name, value in host.items():
        if not isinstance(value, np.ndarray):
            buffers[name] = value
    patch_pointer_tables(case, host, device, buffers)
    return StagedCase(case, device, buffers, kernel)


def run_case(case: dict, device: Device, kernel=None) -> dict:
    """Stage ``case`` through ``device``, launch, and return NumPy outputs.

    Pure NumPy + the kernel object: no torch.
    """
    staged = stage_case(case, device, kernel)
    staged.launch()
    return staged.outputs()


def make_device(spec: str = "cpu"):
    """Resolve a ``--device`` spec to a Device instance.

    ``cpu`` (reference), ``cuda`` / ``cuda:N`` (cuda-python, torch-free),
    ``torch-gpu`` / ``torch-cpu`` (torch reference adapters), or
    ``module:factory`` to build a compiler device.
    """
    spec = spec or "cpu"
    if spec == "cpu":
        return CpuDevice()
    if spec == "cuda" or spec.startswith("cuda:"):
        from opslib.devices.cuda import CudaDevice
        device_id = 0 if spec == "cuda" else int(spec.split(":", 1)[1])
        return CudaDevice(device_id)
    if spec == "torch-gpu":
        from opslib.devices.torch_ref import TorchGpuDevice
        return TorchGpuDevice()
    if spec == "torch-cpu":
        from opslib.devices.torch_ref import TorchCpuInterpreterDevice
        return TorchCpuInterpreterDevice()
    if ":" in spec:
        import importlib
        module_name, attribute = spec.split(":", 1)
        factory = getattr(importlib.import_module(module_name), attribute)
        return factory() if callable(factory) else factory
    raise ValueError(f"unknown --device {spec!r}")
