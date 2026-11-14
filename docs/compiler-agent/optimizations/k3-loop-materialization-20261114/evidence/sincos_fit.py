#!/usr/bin/env python3
"""Fit sin/cos minimax-ish coefficients for the fp32 vector-polynomial path
and validate the EXACT op sequence (every step rounded to fp32) against the
f64-computed reference over the union grid.

Algorithm under test (the sequence _poly_sincos will emit):
  t  = f32(x * R2PI)
  q  = f32(f32(t + MAGIC) - MAGIC)            # rint, |t| < 2^22
  r  = f32(f32(f32(x - f32(q*PIO2_1)) - f32(q*PIO2_2)) - f32(q*PIO2_3))
  qi = int(q)  (exact, q integral)
  quad = qi & 3
  z  = f32(r*r)
  s  = f32(r * S(z))          # S: horner in z, every step f32
  c  = C(z)                   # C: horner in z, leading 1
  base = (quad & 1) ? c : s   # sin; swapped for cos
  res = bitflip(base, (quad & 2) << 30)       # sin; cos flips on ((quad+1)&2)<<30

Guard domain: |x| < XMAX (all lanes), else the libm path (not simulated).
"""
import numpy as np

R2PI = np.float32(2.0 / np.pi)
MAGIC = np.float32(12582912.0)  # 1.5 * 2^23
XMAX = np.float32(1024.0)


def _split_trunc(value, bits):
    """Truncate ``value`` to ``bits`` significant bits (a float32-exact
    prefix with headroom for an exact integer multiply)."""
    v = float(value)
    if v == 0.0:
        return np.float32(0.0)
    e = np.floor(np.log2(abs(v)))
    keep = np.floor(np.log2(np.floor(2.0 ** (bits - 1)))) if False else bits
    scale = 2.0 ** (e - (keep - 1))
    return np.float32(np.floor(abs(v) / scale) * scale * np.sign(v))


# the 3-way Cody-Waite split of pi/2: each term keeps <= 11 significant
# bits so q * term is exact in fp32 for |q| < 2^13
PIO2_1 = _split_trunc(np.pi / 2, 11)
PIO2_2 = _split_trunc(np.pi / 2 - float(PIO2_1), 11)
PIO2_3 = _split_trunc(np.pi / 2 - float(PIO2_1) - float(PIO2_2), 11)
_residual = (np.pi / 2 - float(PIO2_1) - float(PIO2_2) - float(PIO2_3))


def fit(kind):
    """Least-squares fit on Chebyshev nodes over z in [0, (pi/4)^2]."""
    # S(z): sin(r)/r = 1 + s1 z + ... (odd function -> poly in z, leading 1)
    # C(z): cos(r)   = 1 + c1 z + ...
    n = 2400
    k = np.arange(n)
    z = (0.5 * (1 - np.cos(np.pi * (2 * k + 1) / (2 * n)))) * (np.pi / 4) ** 2
    r = np.sqrt(z)
    if kind == "S":
        target = np.sin(r) / r
        deg = 5
    else:
        target = np.cos(r)
        deg = 5
    A = np.stack([z ** k for k in range(1, deg + 1)], axis=1)
    c = np.linalg.lstsq(A, target - 1.0, rcond=None)[0]
    return np.concatenate(([1.0], c))


def horner_f32(z, coeffs):
    p = np.full_like(z, np.float32(coeffs[-1]), dtype=np.float32)
    for c in reversed(coeffs[:-1]):
        p = np.float32(p * z + np.float32(c))
    return p


def sequence(x, kind, S, C):
    x = np.asarray(x, dtype=np.float32)
    t = np.float32(x * R2PI)
    q = np.float32(np.float32(t + MAGIC) - MAGIC)
    r = np.float32(np.float32(np.float32(
        x - np.float32(q * PIO2_1)) - np.float32(q * PIO2_2))
        - np.float32(q * PIO2_3))
    qi = q.astype(np.int64)
    quad = qi & np.int64(3)
    z = np.float32(r * r)
    s = np.float32(r * horner_f32(z, S))
    c = horner_f32(z, C)
    pick = (quad & 1).astype(bool)
    base = np.where(pick, c, s) if kind == "sin" else np.where(pick, s, c)
    flip = (quad & 2) if kind == "sin" else ((quad + 1) & 2)
    bits = base.view(np.int32) ^ (flip.astype(np.int64) << 30).astype(np.int32)
    return bits.view(np.float32)


def main():
    S = [np.float32(c) for c in fit("S")]
    C = [np.float32(c) for c in fit("C")]
    print("S coeffs:", [repr(c) for c in S])
    print("C coeffs:", [repr(c) for c in C])
    print("PIO2 split:", repr(PIO2_1), repr(PIO2_2), repr(PIO2_3),
          "residual:", _residual)

    # union grid
    grids = [
        np.linspace(-1030, 1030, 400001),
        np.linspace(-np.pi / 2 - 1e-3, np.pi / 2 + 1e-3, 20001),
        (np.arange(-40, 40) * np.pi / 2 + np.array(
            [-1e-4, -1e-6, 0.0, 1e-6, 1e-4]).reshape(-1, 1)).ravel(),
        np.linspace(-13, 13, 26) + 0.123456789,          # blackman-ish
        np.array([0.0, -0.0, 1e-38, -1e-38, 1.1754944e-38,
                  np.pi / 2, np.pi, 2 * np.pi, -np.pi / 2, 1023.9, -1023.9,
                  1024.0, -1024.0, np.float32(2**10 - 2**-12)]),
    ]
    rng = np.random.default_rng(30)
    grids.append(rng.standard_normal(200000))
    grids.append(rng.random(200000) * 2 * np.pi)
    x = np.concatenate([np.asarray(g, dtype=np.float64) for g in grids])

    for kind, ref in (("sin", np.sin), ("cos", np.cos)):
        # exact-domain subset (the guarded path only runs |x| < XMAX)
        m = (np.abs(x) < float(XMAX))
        xs = x[m]
        got = sequence(xs, kind, S, C)
        want = ref(xs).astype(np.float32)
        err = np.abs(got.astype(np.float64) - want.astype(np.float64))
        ulp = np.abs((got.view(np.int32).astype(np.int64)
                      - want.view(np.int32).astype(np.int64)))
        # NaN policy: specials (NaN/inf) do not enter the guarded domain
        print(f"{kind}: n={len(xs)} max_abs_err={err.max():.3e} "
              f"max_ulp={ulp.max()} "
              f"p999_abs={np.percentile(err, 99.9):.3e} "
              f"worst_x={xs[err.argmax()]:.6g}")
        # specials through the sequence (outside guard these take libm; the
        # sequence's behavior on them is informational)
        sp = np.array([np.inf, -np.inf, np.nan], np.float32)
        print(f"{kind}: inf/nan -> {sequence(sp, kind, S, C)}")


if __name__ == "__main__":
    main()
