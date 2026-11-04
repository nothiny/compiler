"""opslib: the single shared library for the operator corpus.

Everything the framework needs to manage, load, execute and benchmark the
corpus lives here exactly once:

  - ``opslib.mathref``   vectorized float64 erf/erfc/lgamma/erfinv for refs
  - ``opslib.golden``    disk cache of (operator file, shape, dtype, seed) cases
  - ``opslib.compare``   single-pass host comparison + optional device-side one
  - ``opslib.catalog``   the operator index (generated, AST-only)

The root-level ``runner.py`` / ``operator_entry.py`` / ``case_utils.py`` and
the per-group copies are compatibility shims over this package.
"""
