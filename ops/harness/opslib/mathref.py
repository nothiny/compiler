"""Vectorized float64 math for operator ``ref`` functions.

``np.vectorize(math.erf)`` (and friends) evaluates a Python function per
element, which costs minutes on the steady-state benchmark shapes (gelu's
ref alone was ~7 minutes at 2.7e8 elements).  The functions here compute the
same mathematical function on the whole array at once.

Semantics are deliberately pinned to the ``np.vectorize(math.*)`` contract:

  - input is cast to float64 first;
  - output is float64 (never float32, even for float32 input);
  - scalars in, scalars out.

``scipy.special`` provides the fast path (scipy is already a project
dependency); without it we fall back to the literal ``np.vectorize(math.*)``
implementation -- identical semantics, just not faster -- and warn once.
"""
from __future__ import annotations

import math
import warnings

import numpy as np

__all__ = ["erf", "erfc", "lgamma", "erfinv"]

_warned = False


def _fallback(name: str):
    def apply(x):
        global _warned
        if not _warned:
            warnings.warn(
                "scipy.special is unavailable; mathref falls back to the slow "
                "np.vectorize(math.*) path", RuntimeWarning, stacklevel=3)
            _warned = True
        return np.vectorize(getattr(math, name))(np.asarray(x, dtype=np.float64))
    return apply


try:
    from scipy import special as _special

    def _wrap(ufunc):
        def apply(x):
            return ufunc(np.asarray(x, dtype=np.float64))
        return apply

    erf = _wrap(_special.erf)
    erfc = _wrap(_special.erfc)
    lgamma = _wrap(_special.gammaln)

    def erfinv(x):
        return _special.erfinv(np.asarray(x, dtype=np.float64))

except ImportError:  # pragma: no cover - exercised only without scipy
    erf = _fallback("erf")
    erfc = _fallback("erfc")
    lgamma = _fallback("lgamma")

    def erfinv(x):  # math has no erfinv
        raise RuntimeError("mathref.erfinv needs scipy.special")
