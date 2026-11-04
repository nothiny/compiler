"""Torch-free, device-agnostic execution interface for the operator corpus.

See ``compiler_api/README.md`` for the contract and
``compiler_api/manifest.py`` / ``compiler_api/run_cases.py`` for the entry
points an agent consumes.
"""
from compiler_api.device import (  # noqa: F401
    Buffer,
    HostBuffer,
    Device,
    CpuDevice,
    GpuDevice,
    bind_arguments,
    kernel_parameters,
    run_case,
)
