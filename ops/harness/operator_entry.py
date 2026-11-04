"""Compatibility shim: the loader lives in ``opslib.catalog``."""
from opslib.catalog import OperatorSpec, load_operator, summary  # noqa: F401
from opslib.catalog import specs as entries  # noqa: F401  (yields OperatorSpec)
