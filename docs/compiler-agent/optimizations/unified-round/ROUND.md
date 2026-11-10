# Unified optimization round (W1 + W2 + W3-attempt + C8)

The unified plan (`../UNIFIED-OPTIMIZATION-PLAN.md`) executed under
direct human guidance ("performance per the assembly code, batch the
verification, commit early").  Criterion throughout: the declared proxy
metric -- per-call guest dynamic instructions under the calibrated QEMU
plugin -- never QEMU wall-clock, never a real-machine claim.

## Commits (this round, in order)

| commit | item | measured effect |
|---|---|---|
| c706ebb | [fix] emission peephole: vsetvli's rd is vl, not the avl | prerequisite (a latent miscompile W1 exposed; softmax_kernel_inner [97] 48 unwritten outputs) |
| 2cb9e6c | [opt] W1: fp32 vmath vector-polynomial path | softmax median -76.8%; elementwise median -87.8%; attention flash -36.4% / chunkabc -25.6% / gqa -15.5% |
| 90689c2 | [opt] W1 evidence: softmax 146/146 PASS | -- |
| 3896065 -> reverted in 974a22a | [contract] W3 mir-optimize declaration | superseded (see below) |
| 7557ef2 | [opt] W1 record | -- |
| 586dcf2 | [opt] W2-P1: pack-b full-tile peel | flagship (matmul 128^3 f16) 4.11M -> 2.92M = -29.1% |
| 4d1afb2 | [opt] W2-P1b: A-row staging full-tile peel | flagship 2.92M -> 2.04M; cumulative vs the round's original 13.28M baseline = -84.6% (6.5x) |
| 974a22a | [opt] W3 mir-licm: attempted, measured ~0-to-negative, unwired | negative result recorded (softmax-f16 -2.5% but linear-dropout +1.1%, log_softmax_linear +8.1%) |
| 9dd0bc8 | [opt] W2-C8: narrow-data strided load/store forms | ~0 on the profiled attention cases (36 sites fire; the remaining scalar-load class there is spill traffic, not the walk); kept for the genuinely strided rank-1 forms |

## Headline numbers (guest dynamic instructions per call)

| family | case | baseline (4217b79) | candidate | change |
|---|---|---:|---:|---:|
| softmax | family median, 35 groups | -- | -- | **-76.8%** |
| elementwise | family median, 8 groups | -- | -- | **-87.8%** |
| elementwise | sigmoid-f32 | 54,222 | 4,865 | -91.0% |
| softmax | softmax-f16 | 245,302 | 49,071* | -80.0% |
| matmul | flagship 128^3 f16 | 13,281,439 | 2,038,607 | **-84.6%** |
| attention | flash_varlen f16 | 953,328 | 606,347 | -36.4% |
| attention | chunk_abc f16 | 1,000,364 | 744,522 | -25.6% |
| attention | gqa f32 | 1,378,297 | 1,165,040 | -15.5% |

\* softmax-f16 at 2cb9e6c measured 50,318; the 49,071 figure is the
later re-measure (same path, measurement noise class).

Known regressions (recorded, not hidden): linear-dropout-f16 +9.1%,
log-softmax-linear-f16 +2.9%, naive_attn f16 +13.7% -- all one class:
the polynomial's per-chunk constant traffic pushes spill-bound kernels
over the register budget.  The honest fix is a pressure-aware constant
hoisting (the mir-licm follow-up) or a per-shape cost switch; both are
recorded as follow-up work.

## Verification

- Declared suites green at every landing: test_math_ops (24/24 forms +
  the W1 switch-matrix checks), test_lower_vector, test_conversions,
  test_driver_cache, test_e2e_slice, test_memory_forms, test_layout_ops,
  test_lower_matrix, test_matrix_breadth, check_no_name_dispatch
  (+ witness).
- Family scans: softmax 146/146, elementwise 683/683 (threads 1).
- The full 2734-case input regression at 9dd0bc8:
  `full-input/` (appended on completion).

## What did not work (kept honest)

- mir-licm (sconst hoisting): the allocator's one-remat-per-round
  pressure relief makes unbounded hoisting a compile-time convergence
  bomb; a cap of 4 converges everywhere but the win shrinks to noise
  and the register perturbation hurts two kernels more than the li
  savings help.  Unwired; the loop analysis module stays
  (`a100c/passes/mir_optimize.py`) for the pressure-aware follow-up.
- C8 on the profiled attention cases: the strided forms fire but the
  walk was no longer the cost there (the pre-W1 profile's estimate).
  The 2D-affine forms (two vector terms) need a chunk/row-alignment
  analysis before they can take even the strided form -- future work.

## Addendum: the second roadmap pass (P1 + the runtime floor)

The user's follow-up roadmap (the add_value#[4] assembly evidence: 1,989
instructions for 4 elements) landed two more items:

| commit | item | measured effect |
|---|---|---|
| b652bef | [opt] P1: chunk-loop live-element clamp | add_value[4] 2,007 -> 765 (-61.9%); gelu[128] 8,769 -> 2,259 (-74.2%); sigmoid -63.5%, selu -66.3%, pow -70.1% -- cumulative vs the round's original baselines all at **-96.6..-96.8% (~31x)** |
| 1ba05bc | [opt] runtime: the repeat loop restores/compares the writable span, word-wide | add_value[4] 765 -> 613 (-20%); gelu/sigmoid ~-2%; the whole-image byte loops were the small-case floor |

The clamp: when the whole function's memory ops share ONE prefix mask
`cmp.lt(arange + scalars, S)` (the standard elementwise mask) and
nothing lane-consuming can observe the masked lanes, the chunk loop's
bound is the mask's own `min(BLOCK, S - block_base)` -- the [4]-in-1024
tail chunks (31 of 32 fully masked, each running the complete body)
were pure waste.

The runtime: the --repeats protocol memcpy'd/memcmp'd the WHOLE bundle
image per repeat through byte-wise loops; only the storage-union span
is writable post-patch, and it now moves word-wide.

### The floor after both

Small cases are now dispatch-bound: gelu[128] = 2,216 per call with the
chunk loop at ~2% -- the remaining ~600 is the pool dispatch
(wake/handoff/atomics), a shared surface with diminishing returns (not
pursued; the earlier "don't touch the <10% dispatch" guidance inverted
once the kernel work collapsed, and the byte-loop fix was the cheap
9/10 of it).

### P3 analyzed and skipped (the instruction-count criterion)

The block-boundary join relays (`sd/mv/ld` through the stack scratch)
become `mv/mv/mv` through a free GPR -- the SAME three instructions for
a 2-cycle swap.  A real-hardware win (register vs memory), a zero under
the dynamic-instruction criterion.  Skipped and recorded; the real fix
is allocator phi-coalescing (the moves exist because block params and
their incoming args get different physical registers).

### Next by the roadmap (not yet implemented)

P2 (prefix mask -> exact vl, the ~9-op mask chains), P4 (pointer
recursion + chunk-invariant hoisting), P5 (LMUL m2 -- the mid/large
cases' remaining per-chunk overhead halves; the 6 hardcoded lmul sites
plus the derived regions), P6 (fp16/bf16 masked narrow accesses), P7
(sin/cos polynomials).
