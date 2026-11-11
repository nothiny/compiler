#!/usr/bin/env python3
"""T044 probe driver: decode the x load addresses of the minimized conv3d
probe kernel (tools/t044_probe_op.py) per tap, and diff against the correct
multi-axis window address.

For tap (ic, kz, ky, kx) and output channel oc, the one-hot weight makes
    y[oc * N_total + pos] = x_flat[correct_addr(pos, ic, kz, ky, kx)]
when the compiler is correct, where
    correct_addr = n*stride_xn + od*stride_xd + oh*stride_xh + ow*stride_xw
                 + ic*stride_xc + kz*stride_xd + ky*stride_xh + kx*stride_xw.
Any deviation is the address defect, position by position.

Read-only diagnostic; not part of the delivered program.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "ops" / "harness"), str(ROOT / "tools")):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np  # noqa: E402

import t044_probe_op as POP  # noqa: E402
import a100_support.native_device as nd  # noqa: E402

SHAPE = POP.SHAPES[0]
DUMP = '/tmp/t044/probe_map.txt'


def decode(tap, threads=1, verbose=True):
    n, ci, d, h, w, co, kd, kh, kw = SHAPE
    od, oh, ow = d - kd + 1, h - kh + 1, w - kw + 1
    ic, kz, ky, kx = tap
    # the weight flat index tap (ic,kz,ky,kx) reads for lane oc:
    # wT[oc + (ic*kd*kh*kw + kz*kh*kw + ky*kw + kx)*Cout]  (oc innermost)
    w_idx = (ic * kd * kh * kw + kz * kh * kw + ky * kw + kx) * co
    device = nd.make_device()
    device.threads = threads
    case = POP.probe_case(w_onehot_flat_index=w_idx)
    staged = device.stage_case(case)
    staged.launch()
    y = np.asarray(staged.outputs()["y_ptr"]).reshape(-1)
    N_total = n * od * oh * ow
    bad = 0
    rows = []
    for oc in range(co):
        for pos in range(N_total):
            nn, r = divmod(pos, od * oh * ow)
            o_d, r = divmod(r, oh * ow)
            o_h, o_w = divmod(r, ow)
            want = (nn * ci * d * h * w + o_d * h * w + o_h * w + o_w
                    + ic * d * h * w + kz * h * w + ky * w + kx)
            got = y[oc * N_total + pos]
            # the one-hot weight sits at oc=0's slot only: channel 0 must
            # read x[os] exactly; every other channel must stay zero
            expect_val = float((want + 1) * (want + 1))   # x[i] = (i+1)^2
            got_val = float(got) if oc == 0 else 0.0
            if oc == 0:
                expect = expect_val
            else:
                expect = 0.0
            if got_val != expect:
                bad += 1
                if len(rows) < 12:
                    rows.append((oc, nn, o_d, o_h, o_w, got_val, expect))
    if verbose:
        print(f"tap ic={ic} kz={kz} ky={ky} kx={kx} (w_idx={w_idx}) "
              f"threads={threads}: bad={bad}/{co*N_total}")
        # dump raw y for oc=0, first 10 positions, plus os values
        raws = []
        for oc_ in range(6):
            raws.append((f"oc{oc_}", float(y[oc_ * N_total]), float(y[oc_ * N_total + 1])))
        print("   per-oc y[0], y[1]:", raws)
        for pos in range(4):
            nn, r = divmod(pos, od * oh * ow)
            o_d, r = divmod(r, oh * ow)
            o_h, o_w = divmod(r, ow)
            osv = (nn * ci * d * h * w + o_d * h * w + o_h * w + o_w
                   + ic * d * h * w + kz * h * w + ky * w + kx)
            raws.append((pos, osv, float(y[pos])))
        print("   pos, os, y:", raws)
        for r in rows:
            oc, nn, o_d, o_h, o_w, got, want = r
            print(f"   oc={oc} n={nn} od={o_d} oh={o_h} ow={o_w}: "
                  f"read x[{got}] want x[{want}] (delta {got - want})")
        if DUMP:
            with open(DUMP, "w") as fh:
                fh.write("off_n n od oh ow want read\n")
                for oc in (0,):
                    for pos in range(N_total):
                        nn, r = divmod(pos, od * oh * ow)
                        o_d, r = divmod(r, oh * ow)
                        o_h, o_w = divmod(r, ow)
                        want = (nn * ci * d * h * w + o_d * h * w + o_h * w + o_w
                                + ic * d * h * w + kz * h * w + ky * w + kx)
                        got = y[oc * N_total + pos] - 1
                        fh.write(f"{pos} {nn} {o_d} {o_h} {o_w} {want} {int(got)}\n")
    return bad


def main() -> int:
    taps = [(0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 1, 0), (0, 0, 1, 1), (0, 1, 0, 0), (0, 1, 0, 1), (0, 1, 1, 0), (0, 1, 1, 1), (1, 0, 0, 0), (1, 1, 1, 1), (3, 1, 1, 1)]
    for tap in taps:
        decode(tap)
    return 0


if __name__ == "__main__":
    sys.exit(main())
