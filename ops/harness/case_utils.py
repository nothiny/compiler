"""Compatibility shim: the implementation lives in ``opslib.case``."""
from opslib.case import (  # noqa: F401
    empty,
    empty_like,
    fast_rng,
    numel,
    parallel_chunks,
    public_make_case,
    dtype_case,
    dtype_name,
    tolerance_for,
    comparison_for,
    convert_float_arrays,
    run_case,
)
