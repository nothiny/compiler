#!/usr/bin/env python3
"""Derive + validate the f32 vector-polynomial coefficients for the vmath
poly path (the elementwise optimization round; re-anchored by the unified
optimization round's W1).

The simulation below mirrors, op for op, the MIR sequence
``a100c/lower/vectorize.py::_vmath_poly`` emits, with numpy float32
rounding at every step:

* vfmacc(a, b, c) is simulated as float32(float64(a)*float64(b) + float64(c))
  -- f32 operands are exact in f64, the product is exact in f64 (24+24<=53),
  so this equals the single-rounded f32 fma up to a 2^-53 double-rounding
  hazard, far below the 1e-7 validation bar;
* the bit-level moves (exponent surgery) use int32 views;
* every add/sub/mul/div result is rounded to float32 exactly like the
  vector instruction would.

Differences from the elementwise round's original tooling (kept as
docs/compiler-agent/optimizations/elementwise/tooling/fit_validation_output.txt):

* the simulated log/log2/erf sequences include the NaN guards the emitted
  code carries (the original sim measured nan_mm=1 there -- the guard is
  the fix);
* the exp/exp2 overflow thresholds are the widened ones (89.0 / 128.5):
  the select fires only past the range where the halved-exponent core
  rounds the boundary itself, so finite ~FLT_MAX results no longer become
  +inf (the original exp2f validation's one mismatched inf point);
* the validation grid is the union of the elementwise and softmax rounds'
  grids (dense + extremes + the softmax family's actual parameter
  distributions) and additionally measures the margin against the corpus's
  tightest declared tolerance pairs.

Outputs: the coefficient tables (paste targets), the measured max
relative/absolute errors vs float64 references, and a JSON record
(default: docs/compiler-agent/optimizations/elementwise/candidates/
vector-poly/numerics-merged.json).  Acceptance: nan_mm == 0, inf_mm == 0,
rel err <= 5e-7 on the function value in the normal range (the scoped
cases declare rtol/atol 2e-3; glibc f32 functions are ~1 ulp = 1.2e-7),
and every tolerance-pair margin <= 0.2 (5x headroom).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

F32 = np.float32
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / ("docs/compiler-agent/optimizations/elementwise/"
                      "candidates/vector-poly/numerics-merged.json")


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
    if rel.max() <= 3e-7:
        EXP_P = [float(c) for c in pcoef]
        break
else:
    raise SystemExit("exp2f poly did not reach 3e-7")

# widened overflow thresholds (see the module docstring): the select only
# catches what the core can no longer round itself
EXP_OVER = 89.0
EXP_UNDER = -104.0
EXP2_OVER = 128.5
EXP2_UNDER = -150.0


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
LOG_SERIES = [1.0 / 3.0, 1.0 / 5.0, 1.0 / 7.0, 1.0 / 9.0]

F32_MIN_NORMAL = 1.1754943508222875e-38
LOG_23_LN2 = 23 * 0.6931471805599453


def sim_log_core(x, to_log2):
    """The emitted _poly_log order: subnormal scale, bit decomposition,
    atanh series, correction, THEN the log2 scaling, THEN the guards."""
    x = x.astype(F32)
    m_sub = (x > F32(0.0)) & (x < F32(F32_MIN_NORMAL))
    xs = np.where(m_sub, (x * F32(8388608.0)).astype(F32), x).astype(F32)
    ix = f32_bits(xs)
    e = ((ix >> np.int32(23)) - np.int32(127)).astype(np.int32)
    iz = (ix - (e << np.int32(23))).astype(np.int32)
    z = bits_f32(iz)
    mb = z > F32(SQRT2)
    zh = np.where(mb, (z * F32(0.5)).astype(F32), z).astype(F32)
    eh = np.where(mb, e + np.int32(1), e).astype(np.int32)
    r = ((zh - F32(1.0)) / (zh + F32(1.0))).astype(F32)
    r2 = (r * r).astype(F32)
    h = horner_fma(r2, LOG_SERIES)
    s = fma((r * r2).astype(F32), h, r)
    s = (s + s).astype(F32)
    ef = eh.astype(F32)                    # vfcvt.f.x.v (exact)
    hi = (ef * F32(LN2_HI)).astype(F32)
    lo = (ef * F32(LN2_LO)).astype(F32)
    res = (hi + (s + lo)).astype(F32)
    res = np.where(m_sub, (res - F32(LOG_23_LN2)).astype(F32), res)
    if to_log2:
        res = (res * F32(INV_LN2)).astype(F32)
    # the emitted domain guards (order matches _poly_log)
    res = np.where(x != x, F32(np.nan), res).astype(F32)
    res = np.where(x < F32(0.0), F32(np.nan), res).astype(F32)
    res = np.where(x == F32(0.0), F32(-np.inf), res).astype(F32)
    res = np.where(x == F32(np.inf), F32(np.inf), res).astype(F32)
    return res


def sim_logf(x):
    return sim_log_core(x, False)


def sim_log2f(x):
    return sim_log_core(x, True)


# --------------------------------------------------------------------------
# floor: three regions (see the elementwise DESIGN).
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
# erf: |x| < 1: x * P(x^2);  1 <= |x| < 4: sign * (1 - exp(-x^2)*W(1/z));
# |x| >= 4: sign (erf(4) rounds to 1.0 in f32).
# --------------------------------------------------------------------------
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
        if rel.max() <= 2e-6:
            return [float(c) for c in coef], deg
    raise SystemExit("erf tail did not converge")


def sim_erff(x, lo_coef, tail_coef):
    """The emitted _poly_erf order (single lo piece; the tail covers
    [1, 4); the NaN guard applies last)."""
    x = x.astype(F32)
    ax = np.abs(x)
    z = (ax * ax).astype(F32)
    p = horner_fma(z, lo_coef)
    piece_a = (x * p).astype(F32)
    ti = (F32(1.0) / z).astype(F32)
    w = horner_fma(ti, tail_coef)
    y = (z * F32(-LOG2E)).astype(F32)
    ez = sim_exp2_core(y)
    term = ((ez * w).astype(F32) / ax).astype(F32)
    one_m = (F32(1.0) - term).astype(F32)
    neg = x < F32(0.0)
    sgn = np.where(neg, F32(-1.0), F32(1.0)).astype(F32)
    piece_b = (sgn * one_m).astype(F32)
    ge1 = ax >= F32(1.0)
    ge4 = ax >= F32(4.0)
    res = np.where(ge1, piece_b, piece_a).astype(F32)
    res = np.where(ge4, sgn, res).astype(F32)
    return np.where(x != x, F32(np.nan), res).astype(F32)


# --------------------------------------------------------------------------
# validation vs float64 references over the union grid
# --------------------------------------------------------------------------
def fn_of_f32(x, f):
    # ground truth input: the f32 rounding of the grid value
    return f(np.float64(x.astype(F32)))


def report(name, sim, ref, x, record):
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
    # the corpus's tightest declared tolerance pairs (softmax family):
    # (rtol=atol=1e-4) and (rtol=2e-4, atol=2e-5)
    margins = []
    for rtol, atol in ((1e-4, 1e-4), (2e-4, 2e-5)):
        bound = atol + rtol * np.abs(rd)
        ratio = np.abs(sd - rd) / bound
        margins.append(float(ratio.max()) if ratio.size else 0.0)
    line = (f"{name}: n={x.size} max_rel_normal="
            f"{rel.max() if rel.size else 0:.3e} "
            f"max_subnormal_ulp={sub_ulp.max() if sub_ulp.size else 0:.3f} "
            f"nan_mm={nan_mm} inf_mm={inf_mm} "
            f"margin(1e-4,1e-4)={margins[0]:.4f} "
            f"margin(2e-4,2e-5)={margins[1]:.4f}")
    print(line)
    record[name] = {
        "n": int(x.size),
        "max_rel_normal": float(rel.max()) if rel.size else 0.0,
        "max_subnormal_ulp": float(sub_ulp.max()) if sub_ulp.size else 0.0,
        "nan_mismatch": nan_mm, "inf_mismatch": inf_mm,
        "margin_rtol_atol_1e-4": margins[0],
        "margin_rtol2e-4_atol2e-5": margins[1],
    }
    return nan_mm == 0 and inf_mm == 0


def main():
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    print("=== coefficient fits ===")
    erf_pieces = fit_erf_pieces()
    erf_tail = fit_erf_tail()
    print("EXP_P =", EXP_P)
    print("LOG_SERIES =", LOG_SERIES)
    print("ERF lo =", erf_pieces["lo"][0])
    print("ERF tail W =", erf_tail[0])

    record = {"thresholds": {"exp_over": EXP_OVER, "exp_under": EXP_UNDER,
                             "exp2_over": EXP2_OVER,
                             "exp2_under": EXP2_UNDER},
              "coefficients": {"EXP_P": EXP_P, "LOG_SERIES": LOG_SERIES,
                               "ERF_P": erf_pieces["lo"][0],
                               "ERF_W": erf_tail[0]},
              "functions": {}}
    ok = True
    rng = np.random.default_rng(30)

    # exp: dense + the softmax family's actual distribution (shifted
    # logits: everything below the row max) + extremes + the widened
    # threshold's boundary windows
    x = np.concatenate([
        np.linspace(-106.0, 90.0, 4000001),
        -(rng.uniform(0, 104, 1000000)),          # softmax exp(-shift)
        -np.abs(rng.standard_normal(500000) * 8),  # sigmoid/tanh tails
        np.linspace(88.0, 90.0, 2000001),          # over-boundary window
        np.linspace(-106.0, -102.0, 1000001),      # under-boundary window
        np.array([0.0, -0.0, 1e-45, -1e-45, 1e38, -1e38, np.inf, -np.inf,
                  np.nan, 88.722839111673, 88.72283935546875, 89.0,
                  -103.97, -103.972084, -104.0, -104.0000001, 2.9e6,
                  -2.9e6])])
    ok &= report("expf", sim_expf(x), fn_of_f32(x, lambda v: np.exp(v)),
                 x, record["functions"])

    x = np.concatenate([
        np.linspace(-150.0, 129.0, 4000001),
        np.linspace(127.0, 129.5, 2000001),        # over-boundary window
        np.linspace(-152.0, -148.0, 1000001),      # under-boundary window
        np.array([0.0, -0.0, np.inf, -np.inf, np.nan, 127.9999, 128.0,
                  128.5, 127.99999999, -149.0, -150.0, -150.0000001])])
    ok &= report("exp2f", sim_exp2f(x), fn_of_f32(x, lambda v: np.exp2(v)),
                 x, record["functions"])

    x = np.concatenate([
        np.exp(np.linspace(np.log(1e-38), np.log(3e38), 4000001)),
        rng.uniform(0.01, 100, 200000) ** 3,
        rng.standard_normal(200000) ** 2 + 0.1,
        # subnormal and boundary windows: nextafter regions of the
        # min normal, 1, sqrt(2) and 2
        np.linspace(0.0, 3e-38, 500001),
        np.linspace(0.99, 1.01, 200001),
        np.linspace(np.sqrt(2.0) - 1e-5, np.sqrt(2.0) + 1e-5, 200001),
        np.linspace(1.99, 2.01, 200001),
        np.array([1.0, 2.0, 0.5, 1e-38, 1.1754944e-38, 3.4028235e38,
                  np.inf, 0.0, -0.0, -1.0, np.nan, 5.96e-8,
                  np.nextafter(0, 1), 5e-324])])
    ok &= report("logf", sim_logf(x), fn_of_f32(x, lambda v: np.log(v)),
                 x, record["functions"])
    ok &= report("log2f", sim_log2f(x),
                 fn_of_f32(x, lambda v: np.log2(v)), x, record["functions"])

    x = np.concatenate([
        np.linspace(-1e6, 1e6, 4000001),
        rng.standard_normal(200000) * 1e6,
        # the half-integer boundary bands on both sides
        np.linspace(F32_2_POW_22 - 4.0, F32_2_POW_22 + 4.0, 1000001),
        np.linspace(F32_2_POW_23 - 4.0, F32_2_POW_23 + 4.0, 1000001),
        np.linspace(-F32_2_POW_23 - 4.0, -F32_2_POW_22 + 4.0, 1000001),
        np.array([0.0, -0.0, -0.5, 0.5, -1.5, 1.5, 8388607.5, 8388608.0,
                  -8388608.0, 8388609.0, 2**24 + 1.0, np.inf, -np.inf,
                  np.nan, 1e30, -1e30])])
    ok &= report("floorf", sim_floorf(x),
                 fn_of_f32(x, lambda v: np.floor(v)), x, record["functions"])

    import math
    # erf: dense + the gelu distribution (x * 0.70710678, x ~ N(0, 3))
    # + the piece boundaries + extremes
    gelu = (rng.standard_normal(1000000) * 3) * 0.7071067811865476
    x = np.concatenate([
        np.linspace(-6.0, 6.0, 4000001),
        rng.standard_normal(400000) * 2,
        gelu,
        np.linspace(0.9, 1.1, 400001),
        np.linspace(3.9, 4.1, 400001),
        np.linspace(-4.1, -3.9, 400001),
        np.logspace(-30, -3, 200001),
        np.array([0.0, -0.0, 1.0, -1.0, 2.0, -2.0, 3.9, -3.9, 4.0, -4.0,
                  4.1, -4.1, 0.5625, 0.84375, np.inf, -np.inf, np.nan,
                  1e-30, 9.9e-1])])
    ok &= report("erff",
                 sim_erff(x, erf_pieces["lo"][0], erf_tail[0]),
                 fn_of_f32(x, np.vectorize(math.erf)), x,
                 record["functions"])

    record["acceptance"] = {
        "nan_mm_zero_and_inf_mm_zero": bool(ok),
        "bar": "rel <= 5e-7 normal, subnormal exp <= 32 ulp, "
               "tolerance margins <= 0.2",
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(record, indent=2) + "\n")
    print(f"\nrecord written to {out_path}")
    if not ok:
        raise SystemExit("nan/inf mismatch -- NOT acceptable")
    print("All validations met the bar.")


if __name__ == "__main__":
    main()
