"""Compatibility shim: the torch reference devices live in
``opslib.devices.torch_ref``."""
from opslib.devices.torch_ref import (  # noqa: F401
    TorchBuffer,
    TorchCpuInterpreterDevice,
    TorchGpuDevice,
)
