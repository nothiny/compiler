"""On-device allclose helper for ``CudaDevice.compare`` (torch-free).

The kernel evaluates the exact ``np.isclose`` expression
``(|x - y| <= atol + rtol*|y|) & isfinite(y) | (x == y)`` (plus the optional
both-NaN rule) in the buffers' dtype, and accumulates

  - ``bad``: count of violating elements (int32, atomic add), and
  - ``maxerr``: the informational float64 max |x - y| over elements that are
    not exactly equal.  Non-negative doubles preserve IEEE ordering under an
    int64 bitcast, so the reduction uses ``atomic_max`` on the bit patterns.

Only float32 buffers are compared on the device: python-float kernel
arguments arrive as fp32, which mirrors numpy's weak-scalar promotion for
fp32 arrays bit-for-bit, but *not* for fp16/fp64 (those fall back to the
host comparison).  ``isfinite``/``isnan`` are spelled with plain comparisons
(``|x| < inf`` and ``x != x``) because triton 3.8 has no tl.isfinite.
This is a framework helper, not a corpus operator file.
"""
import triton
import triton.language as tl


@triton.jit
def _allclose_kernel(a_ptr, b_ptr, n_elements, bad_ptr, maxerr_ptr,
                     rtol, atol, equal_nan: tl.constexpr, BLOCK: tl.constexpr):
    pid = tl.program_id(0)
    offsets = pid * BLOCK + tl.arange(0, BLOCK)
    mask = offsets < n_elements
    a = tl.load(a_ptr + offsets, mask=mask, other=0.0)
    b = tl.load(b_ptr + offsets, mask=mask, other=0.0)
    b_abs = tl.abs(b)
    finite = b_abs < float("inf")          # NaN compares False: not finite
    close = ((tl.abs(a - b) <= (atol + rtol * b_abs)) & finite) | (a == b)
    if equal_nan:
        close = close | ((a != a) & (b != b))
    bad = tl.sum(tl.where(mask & (~close), 1, 0).to(tl.int32), axis=0)
    tl.atomic_add(bad_ptr, bad)
    delta = tl.abs(a.to(tl.float64) - b.to(tl.float64))
    equal = a == b
    if equal_nan:
        equal = equal | ((a != a) & (b != b))
    error = tl.where(mask & equal, 0.0, delta)
    tl.atomic_max(maxerr_ptr, tl.max(error.to(tl.int64, bitcast=True), axis=0))
