#!/usr/bin/env python3
"""Derive + validate the f32 vector-polynomial coefficients for the vmath
poly path (elementwise optimization round).

The simulation below mirrors, op for op, the MIR sequence the lowering will
emit, with numpy float32 rounding at every step:

* vfmacc(a, b, c) is simulated as float32(float64(a)*float64(b) + float64(c))
  -- f32 operands are exact in f64, the product is exact in f64 (24+24<=53),
  so this equals the single-rounded f32 fma up to a 2^-53 double-rounding
  hazard, far below the 1e-7 validation bar;
* the bit-level moves (exponent surgery) use int32 views;
* every add/sub/mul/div result is rounded to float32 exactly like the vector
  instruction would.

Outputs: the coefficient tables (paste targets) and the measured max
relative/absolute errors vs float64 references over dense grids including
extremes.  Acceptance bar: rel err <= 5e-7 on the function value (the scoped
cases declare rtol/atol 2e-3; glibc f32 functions are ~1 ulp = 1.2e-7).
"""
from __future__ import annotations

import numpy as np

F32 = np.float32


def fma(a, b, c):
    return F32(np.float64(a) * np.float64(b) + np.float64(c))


def bits_f32(i):
    return i.view(np.float32) if isinstance(i, np.ndarray) \
        else np.int32(i).view(F32)


def f32_bits(x):
    return np.ascontiguousarray(x, dtype=F32).view(np.int32)


def horner_fma(x, coeffs):
    """p = c[n]; for c in reversed: p = fma(p, x, c)  (single-rounded)."""
    p = np.full_like(x, F32(coeffs[-1]), dtype=F32)
    for c in reversed(coeffs[:-1]):
        p = fma(p, x, F32(c))
    return p


# --------------------------------------------------------------------------
# exp: y = x*log2e; k = rne(y) via the 1.5*2^23 magic add; f = y-k in
# [-0.5,0.5]; 2^f = 1 + f*P(f); scale by 2^k through a halved-exponent pair.
# --------------------------------------------------------------------------
LOG2E = 1.4426950408889634
MAGIC = 12582912.0  # 1.5 * 2^23

# P(f) = (2^f - 1)/f on [-0.5, 0.5]; fit degree 6 and 7, keep the smaller
# one that passes.
fgrid = np.linspace(-0.5, 0.5, 200001)
target = (np.exp2(fgrid.astype(np.float64)) - 1.0) / fgrid
target[fgrid == 0.0] = np.log(2.0)
fgrid_fit = fgrid[fgrid != 0.0]
target_fit = target[fgrid != 0.0]
for deg in (5, 6, 7):
    cheb = np.polynomial.chebyshev.chebfit(fgrid_fit, target_fit, deg)
    pcoef = np.polynomial.chebyshev.cheb2poly(cheb)
    sim = (horner_fma(fgrid.astype(F32), pcoef).astype(np.float64)
           * fgrid + 1.0)
    exact = np.exp2(fgrid)
    rel = np.abs(sim - exact) / np.maximum(np.abs(exact), 1e-300)
    print(f"exp2f poly deg {deg}: max rel err {rel.max():.3e}")
    if rel.max() <= 3e-7:
        EXP_P = [float(c) for c in pcoef]
        break
else:
    raise SystemExit("exp2f poly did not reach 3e-7")

EXP_OVER = 88.72283935546875    # ln(3.4028235e38): above -> +inf
EXP_UNDER = -104.0              # below -> 0 (underflow)


def sim_exp2_core(y):
    """y already in units of log2(e) (exp) or raw (exp2)."""
    y = y.astype(F32)
    t = (y + F32(MAGIC)).astype(F32)
    k = (t - F32(MAGIC)).astype(F32)
    f = (y - k).astype(F32)
    p = horner_fma(f, EXP_P)
    two_f = (fma(f, p, F32(1.0))).astype(F32)
    ki = k.astype(np.int32)                 # rtz; k integral
    k1 = ki >> 1                            # vsra: floor(k/2)
    k2 = ki - k1
    s1 = bits_f32(((k1 + np.int32(127)) << np.int32(23)).astype(np.int32))
    s2 = bits_f32(((k2 + np.int32(127)) << np.int32(23)).astype(np.int32))
    res = (two_f * s1).astype(F32)
    res = (res * s2).astype(F32)
    return res


def sim_expf(x):
    x = x.astype(F32)
    y = (x * F32(LOG2E)).astype(F32)
    res = sim_exp2_core(y)
    res = np.where(x > F32(EXP_OVER), F32(np.inf), res).astype(F32)
    res = np.where(x < F32(EXP_UNDER), F32(0.0), res).astype(F32)
    return res


EXP2_OVER = 127.9999          # 2^x > f32max here -> +inf
EXP2_UNDER = -150.0           # below -> 0 (underflow)


def sim_exp2f(x):
    x = x.astype(F32)
    res = sim_exp2_core(x)
    res = np.where(x > F32(EXP2_OVER), F32(np.inf), res).astype(F32)
    res = np.where(x < F32(EXP2_UNDER), F32(0.0), res).astype(F32)
    return res


# --------------------------------------------------------------------------
# log: reduce to z in [sqrt(2)/2, sqrt(2)), r = (z-1)/(z+1),
# log(z) = r + r^3/3 + r^5/5 + ... (atanh series, |r| <= 0.1716)
# --------------------------------------------------------------------------
LN2_HI = 0.693359375            # exactly representable
LN2_LO = -2.12194440e-4
INV_LN2 = 1.4426950408889634
SQRT2 = 1.4142135623730951

# series coefficients (odd powers): r + r^3*(1/3 + r2*(1/5 + r2*(1/7 + r2/9)))
LOG_SERIES = [1.0 / 3.0, 1.0 / 5.0, 1.0 / 7.0, 1.0 / 9.0]


F32_MIN_NORMAL = 1.1754943508222875e-38
LOG_23_LN2 = 23 * 0.6931471805599453


def sim_log_core(x):
    x = x.astype(F32)
    m_sub = (x > F32(0.0)) & (x < F32(F32_MIN_NORMAL))
    xs = np.where(m_sub, (x * F32(8388608.0)).astype(F32), x).astype(F32)
    x = xs
    ix = f32_bits(x)
    e = ((ix >> np.int32(23)) - np.int32(127)).astype(np.int32)
    iz = (ix - (e << np.int32(23))).astype(np.int32)
    z = bits_f32(iz)
    mb = z > F32(SQRT2)
    zh = np.where(mb, (z * F32(0.5)).astype(F32), z).astype(F32)
    eh = np.where(mb, e + np.int32(1), e).astype(np.int32)
    r = ((zh - F32(1.0)) / (zh + F32(1.0))).astype(F32)
    r2 = (r * r).astype(F32)
    # series: 2*(r + r^3*(1/3 + r2*(1/5 + r2*(1/7 + r2/9))))
    h = horner_fma(r2, LOG_SERIES)
    s = fma((r * r2).astype(F32), h, r)
    s = (s + s).astype(F32)
    ef = eh.astype(F32)                    # vfcvt.f.x.v (exact)
    hi = (ef * F32(LN2_HI)).astype(F32)
    lo = (ef * F32(LN2_LO)).astype(F32)
    res = (hi + (s + lo)).astype(F32)
    return np.where(m_sub, (res - F32(LOG_23_LN2)).astype(F32), res).astype(F32)


def sim_logf(x):
    x = x.astype(F32)
    res = sim_log_core(x)
    res = np.where(x < F32(0.0), F32(np.nan), res).astype(F32)
    res = np.where(x == F32(0.0), F32(-np.inf), res).astype(F32)
    res = np.where(x == F32(np.inf), F32(np.inf), res).astype(F32)
    return res


def sim_log2f(x):
    return (sim_logf(x) * F32(INV_LN2)).astype(F32)


# --------------------------------------------------------------------------
# floor: three regions.
#   |x| < 2^22:  r = rne(x) via the 1.5*2^23 magic add (sum in (2^23,2^24),
#                ulp=1); floor = r - (r > x ? 1 : 0).
#   2^22 <= |x| < 2^23: ulp(x) = 0.5, so x is integral or half-integral;
#                w = x+x lands on the integer grid; w odd <=> x = k + 0.5
#                <=> floor = x - 0.5, else x.
#   |x| >= 2^23: x is already integral -> x.
# --------------------------------------------------------------------------
F32_2_POW_22 = 4194304.0
F32_2_POW_23 = 8388608.0


def sim_floorf(x):
    x = x.astype(F32)
    t = (x + F32(MAGIC)).astype(F32)
    r = (t - F32(MAGIC)).astype(F32)
    adj = (r > x)
    rf = (r - F32(1.0)).astype(F32)
    res_small = np.where(adj, rf, r).astype(F32)
    w = (x + x).astype(F32)
    wi = np.ascontiguousarray(w).view(np.int32)
    odd = (wi & np.int32(1)) != 0
    res_mid = np.where(odd, (x - F32(0.5)).astype(F32), x).astype(F32)
    mid = np.abs(x) >= F32(F32_2_POW_22)
    res = np.where(mid, res_mid, res_small).astype(F32)
    big = np.abs(x) >= F32(F32_2_POW_23)
    return np.where(big, x, res).astype(F32)


# --------------------------------------------------------------------------
# erf: |x| < 1: x * P(x^2);  1 <= |x| < 4: sign * (1 - exp(-x^2)*Q(x^2));
# |x| >= 4: sign (erf(4) rounds to 1.0 in f32).
# --------------------------------------------------------------------------
# fit P(z) = erf(sqrt(z))/sqrt(z) on the two sub-intervals [0, 1^2] and
# [1^2, 2^2] (boundary |x| = 1.0 keeps the fit degrees low)
def fit_erf_pieces():
    pieces = {}
    for name, lo, hi in (("lo", 0.0, 1.0), ("hi", 1.0, 2.0)):
        t = np.linspace(lo, hi, 400001)
        z = (t * t).astype(np.float64)
        target = np.where(t == 0, 2 / np.sqrt(np.pi),
                          np.vectorize(__import__("math").erf)(t) / t)
        for deg in range(8, 17):
            cheb = np.polynomial.chebyshev.chebfit(z, target, deg)
            coef = np.polynomial.chebyshev.cheb2poly(cheb)
            sim = horner_fma(z.astype(F32), coef).astype(np.float64) * t
            exact = np.vectorize(__import__("math").erf)(t)
            err = np.abs(sim - exact)
            rel = err / np.maximum(np.abs(exact), 1e-300)
            print(f"erf piece {name} z-deg {deg}: max rel {rel.max():.3e}")
            if rel.max() <= 5e-7:
                pieces[name] = ([float(c) for c in coef], deg)
                break
        else:
            raise SystemExit(f"erf piece {name} did not converge")
    return pieces


def fit_erf_tail():
    """W(t) = e^z*erfc(sqrt(z))*sqrt(z) with t = 1/z, t in [1/16, 1]
    (|x| in [1, 4]): the asymptotic series is a power series in t;
    erfc = e^{-z}*W(t)/|x|."""
    import math
    t = np.linspace(1.0, 4.0, 600001)
    z = (t * t).astype(np.float64)
    ti = (1.0 / z)
    target = np.array([math.exp(zz) * math.erfc(tt) * tt
                       for zz, tt in zip(z[::37], t[::37])])
    ts = ti[::37]
    for deg in range(5, 15):
        cheb = np.polynomial.chebyshev.chebfit(ts, target, deg)
        coef = np.polynomial.chebyshev.cheb2poly(cheb)
        simq = horner_fma(ts.astype(F32), coef).astype(np.float64)
        exactq = target
        rel = np.abs(simq - exactq) / np.maximum(np.abs(exactq), 1e-300)
        print(f"erf tail W t-deg {deg}: max rel {rel.max():.3e}")
        if rel.max() <= 2e-6:
            return [float(c) for c in coef], deg
    raise SystemExit("erf tail did not converge")


def main():
    print("=== coefficient fits ===")
    erf_pieces = fit_erf_pieces()
    erf_tail = fit_erf_tail()

    print("\n=== EXP_P ===")
    print("EXP_P =", EXP_P)
    print("\n=== LOG_SERIES ===", LOG_SERIES)
    print("\n=== ERF lo ===", erf_pieces["lo"][0])
    print("=== ERF hi ===", erf_pieces["hi"][0])
    print("=== ERF tail Q ===", erf_tail[0])

    # ---------------- validation vs float64 references ----------------
    print("\n=== validation (dense + extremes) ===")

    def fn_of_f32(x, f):
        # ground truth input: the f32 rounding of the grid value
        return f(np.float64(x.astype(F32)))

    rng = np.random.default_rng(30)

    def report(name, sim, ref, x):
        # ground truth for an f32 function = the f32 rounding of the f64
        # reference (the boundary inf cases compare equal classes then)
        ref32 = ref.astype(F32)
        both = np.isfinite(sim) & np.isfinite(ref32)
        sd = sim[both].astype(np.float64)
        rd = ref32[both].astype(np.float64)
        normal = np.abs(rd) >= 2.0 ** -126
        rel = (np.abs(sd[normal] - rd[normal])
               / np.maximum(np.abs(rd[normal]), 1e-300))
        sub_ulp = np.abs(sd[~normal] - rd[~normal]) / 2.0 ** -149
        nan_mm = int((np.isnan(sim) != np.isnan(ref32)).sum())
        inf_mm = int(((np.isinf(sim) != np.isinf(ref32))
                      | (np.isinf(sim) & np.isinf(ref32)
                         & (np.signbit(sim) != np.signbit(ref32)))).sum())
        print(f"{name}: n={x.size} max_rel_normal={rel.max() if rel.size else 0:.3e} "
              f"max_subnormal_ulp={sub_ulp.max() if sub_ulp.size else 0:.3f} "
              f"nan_mm={nan_mm} inf_mm={inf_mm}")

    # exp: dense in [-106, 90] + extremes
    x = np.concatenate([
        np.linspace(-106.0, 90.0, 4000001),
        rng.standard_normal(200000) * 3,
        np.array([0.0, -0.0, 1e-45, -1e-45, 1e38, -1e38, np.inf, -np.inf,
                  np.nan, 88.72283935546875, 88.72283945, -103.97,
                  -103.972084, -104.0, -104.0000001, 2.9e6, -2.9e6])])
    report("expf", sim_expf(x), fn_of_f32(x, lambda v: np.exp(v)), x)

    x = np.concatenate([
        np.linspace(-150.0, 128.0, 4000001),
        np.array([0.0, -0.0, np.inf, -np.inf, np.nan, 127.9999, 128.0])])
    report("exp2f", sim_exp2f(x), fn_of_f32(x, lambda v: np.exp2(v)), x)

    x = np.concatenate([
        np.exp(np.linspace(np.log(1e-38), np.log(3e38), 4000001)),
        rng.uniform(0.01, 100, 200000) ** 3,
        rng.standard_normal(200000) ** 2 + 0.1,
        np.array([1.0, 2.0, 0.5, 1e-38, 1.1754944e-38, 3.4028235e38,
                  np.inf, 0.0, -0.0, -1.0, np.nan, 5.96e-8])])
    report("logf", sim_logf(x), fn_of_f32(x, lambda v: np.log(v)), x)
    report("log2f", sim_log2f(x), fn_of_f32(x, lambda v: np.log2(v)), x)

    x = np.concatenate([
        np.linspace(-1e6, 1e6, 4000001),
        rng.standard_normal(200000) * 1e6,
        np.array([0.0, -0.0, -0.5, 0.5, -1.5, 1.5, 8388607.5, 8388608.0,
                  -8388608.0, 8388609.0, 2**24 + 1.0, np.inf, -np.inf,
                  np.nan, 1e30, -1e30])])
    report("floorf", sim_floorf(x), fn_of_f32(x, lambda v: np.floor(v)), x)

    # erf: dense + extremes
    import math
    x = np.concatenate([
        np.linspace(-6.0, 6.0, 4000001),
        rng.standard_normal(400000) * 2,
        np.array([0.0, -0.0, 1.0, -1.0, 2.0, -2.0, 3.9, -3.9, 4.0, -4.0,
                  4.1, -4.1, 0.5625, 0.84375, np.inf, -np.inf, np.nan,
                  1e-30, 9.9e-1])])
    report("erff", sim_erff(x, erf_pieces, erf_tail),
           fn_of_f32(x, np.vectorize(math.erf)), x)

    print("\nAll validations above must meet the bar before emitting.")


def sim_erff(x, pieces, tail):
    x = x.astype(F32)
    ax = np.abs(x)
    z = (ax * ax).astype(F32)
    # piece A: two sub-polys selected at |x| = 1.0
    p_lo = horner_fma(z, pieces["lo"][0])
    p_hi = horner_fma(z, pieces["hi"][0])
    mhi = ax > F32(1.0)
    p = np.where(mhi, p_hi, p_lo).astype(F32)
    piece_a = (x * p).astype(F32)
    # piece B: sign * (1 - exp(-z) * W(1/z) / |x|)   (|x| >= 1, z >= 1)
    ti = (F32(1.0) / z).astype(F32)
    w = horner_fma(ti, tail[0])
    ez = sim_exp2_core((-z * F32(LOG2E)).astype(F32))
    term = ((ez * w).astype(F32) / ax).astype(F32)
    one_m = (F32(1.0) - term).astype(F32)
    neg = x < F32(0.0)
    sgn = np.where(neg, F32(-1.0), F32(1.0)).astype(F32)
    piece_b = (sgn * one_m).astype(F32)
    res = np.where(ax < F32(4.0),
                   np.where(ax < F32(1.0), piece_a, piece_b),
                   sgn).astype(F32)
    return res


if __name__ == "__main__":
    main()
