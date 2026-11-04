"""Compatibility shim: the Device protocol lives in ``opslib.device``."""
from opslib.device import (  # noqa: F401
    Buffer,
    CpuDevice,
    Device,
    GpuDevice,
    HostBuffer,
    StagedCase,
    bind_arguments,
    kernel_parameters,
    patch_pointer_tables,
    run_case,
    stage_case,
)
