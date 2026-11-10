# OPT-2026-11-10-W1-VMATH-POLY: fp32 vmath vector-polynomial path

Record id: OPT-2026-11-10-W1-VMATH-POLY (unified optimization round, W1;
the elementwise round's OPT-2026-11-10-ELEMENTWISE-VMATH-POLY design,
implemented, extended and re-validated).

Status: **accepted (implementation + verification in flight)** — all
declared test suites green; softmax family 146/146 PASS; the remaining
family scans (elementwise 683, matmul 312, attention), the metric
on/off comparison and the full 2734-case regression are the open
verification items, appended here as they complete.

## Goal and outcome

The human directed the unified optimization plan
(`../../UNIFIED-OPTIMIZATION-PLAN.md` §2.W1): replace the per-element
libm `vmath` call for the six fp32 transcendentals with fitted
vector-polynomial MIR sequences at the lowering level, one rollback
switch, no contract change. Baseline revision 4217b79 (the softmax,
elementwise and matmul rounds' verified baselines); candidate commits
`c706ebb` (a prerequisite emitter fix, see below) + `2cb9e6c` (the W1
implementation).

## Why this optimization

Measured (the declared proxy metric: per-call guest dynamic
instructions, calibrated QEMU plugin): softmax-f16 84.2% libm expf body
+ 5.0% PLT per call; elementwise erf/gelu ~89%; decisive in the
exp-heavy attention classes. The vmath op lowers to a stack round-trip
plus a per-element scalar loop calling the sysroot libm (~40-150 guest
instructions per element); `emit.py`'s expansion is the cost. A TIR
pass was rejected (the matmul round's L5 lesson: the producer is the
lowering; a TIR-level rewrite would also interact with the constant
folding that already runs before lowering); a detail change at the
lowering needs no new pass, no repertoire change, no emit change.

## Transformation and reuse contract

- Structural guard: `(fn, sew)` only -- `expf/exp2f/logf/log2f/erff/
  floorf` at SEW 32 emit polynomial sequences; sin/cos/ceil and every
  other width keep the vmath form; `_scalar_math_unary` inherits via
  splat-compute-extract. No operator/kernel name appears anywhere
  (`tools/check_no_name_dispatch.py` + witness).
- Algorithms (op-for-op the host simulation in
  `tools/profiling/fit_math_coeffs.py`): exp/exp2 share the
  halved-exponent core (1.5*2^23 rne magic, 2^f polynomial, k1+k2
  split for gradual underflow and the k=128 overflow); the domain
  selects test the ORIGINAL x (the magic is invalid where they fire)
  and sit ABOVE the natural boundary (89.0 / 128.5) so the core rounds
  the boundary itself. log/log2: subnormal 2^23 scaling, signed-e bit
  decomposition (the [1,2) mantissa built directly), reduction to
  [sqrt(2)/2, sqrt(2)), atanh series with the explicit *2, ln2 hi/lo,
  and the four domain guards (NaN, negative, zero, +inf) the
  simulation proved necessary. floor: three bands, the 2x parity test
  in the ulp=0.5 band. erf: piecewise with the 1/z tail basis and the
  NaN guard.
- Region discipline: the i32 views share the (32, lmul, vl) region --
  zero vsetvli switches inside a polynomial body; every vsel's mask is
  pinned to v0 at its consumer (`_vmovmask_of`).
- On/off: `A100C_VMATH_LIBM=1` -> `LowerOptions.vmath_libm` ->
  identity part `vmath-libm` (the `matrix_scalar_pack` wiring in
  vectorize/driver/factory; the plain driver now also passes
  `matrix_scalar_pack` through, fixing the pre-existing omission where
  the identity recorded a switch the compile ignored).
- Files: `a100c/lower/vectorize.py` (tables + `_vmath_poly` family),
  `a100c/driver.py`, `a100c/factory.py`,
  `a100c/tests/test_math_ops.py`, `tools/profiling/fit_math_coeffs.py`.

## Numerical validation

`tools/profiling/fit_math_coeffs.py` (the union of the elementwise and
softmax round's grids: dense + softmax parameter distributions +
boundary windows + extremes; references computed on the f32-rounded
inputs; every vfmacc single-rounded): nan/inf mismatch 0 on all six
functions (the log/erf guards and the widened exp/exp2 thresholds fixed
the two mismatch classes the original elementwise validation flagged);
max relative error exp 3.9e-6 (the x*log2e single rounding at |x|~88),
exp2 1.19e-7, log 2.26e-7, log2 2.42e-7, floor 0, erf 4.24e-7; the
tightest corpus tolerance pairs (1e-4/1e-4 and 2e-4/2e-5) hold with
margin <= 0.039. Record: `numerics-merged.json` beside this file.

## Prerequisite fix (accepted as part of this round)

The first softmax scan surfaced 3 MISMATCHes (softmax_kernel_inner
[97], all dtypes: 48 unwritten outputs) -- NOT the polynomial path: an
identity passthrough reproduced them. Root cause: the emission
peephole's li dedup modeled `vsetvli rd, rs1` as rd := avl, but rd
receives vl = min(avl, VLMAX); an e64,m1 region at avl 32 on VLEN 1024
writes 16, the following `li avl, 32` was wrongly deduped, and the
staged N-splat's store ran at vl 16 (half its lanes) -- the mask then
disabled the upper 16 lanes of the chunk. Latent since the emission
peephole round (0f84bdc): the vmath call's caller-saved clobber forced
a reload that kept the li alive; W1 removing vmath exposed it. Fixed
in `c706ebb` (the vsetvli now invalidates the li-dedup state for its
destination). Reproduction and the asm-replay evidence chain (unmasked
store, workspace dump) are summarized in the commit message.

## Validation and measurements

- Unit/integration (all green at `2cb9e6c`):
  `a100c/tests/test_math_ops.py` (24/24 declared forms through the real
  pipeline and QEMU execution; the new W1 switch-matrix checks: default
  has vfmacc and no vmath, the libm position and sin keep vmath, the
  identity changes with the switch, both positions execute and compare
  PASS with cross-position agreement 9.5e-7 (exp) / 1.2e-7 (erf)),
  test_lower_vector, test_conversions, test_driver_cache,
  test_e2e_slice, check_no_name_dispatch (+ witness).
- Family scans (threads 1, this candidate revision):
  softmax 146/146 PASS (`../../softmax/candidates/vector-poly/scan/`).
- PENDING (appended as they complete): elementwise 683, matmul 312,
  attention ~135; the metric on/off comparison (softmax 44 groups,
  elementwise 13 cases, attention 6 cases, 1/2/4/8 workers); the full
  2734-case regression.

## Good practices and bad practices

(to be completed with the metric results at round close; the peephole
lesson is already recorded in the fix commit: a value-tracking
optimization must model every instruction that writes the tracked
register, including the vl result of vsetvli -- and a "conservative
unknown" beats an exact-but-wrong model when the exact model needs
target state the optimization does not own.)
