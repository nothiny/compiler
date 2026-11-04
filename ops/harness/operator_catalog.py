"""Compatibility shim: the inventory lives in ``opslib.catalog``."""
from opslib.catalog import (  # noqa: F401
    channel_names,
    entries,
    entry_aliases,
    summary,
)
