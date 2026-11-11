# K3 A100 lowering applicability

Source: immutable exploratory snapshot fc3ccea383db5f55 in /tmp/a100-readonly-review-b-te2m9tiu/exploration/. Destination began at c8ade47. Source instruction reductions are historical; destination results are collected separately. No engine optimization gate is asserted.

| Mechanism | Destination mapping / legality | Disposition |
|---|---|---|
| Kept-axis sum SIMD | _preduce_general still walks every output and reduced position scalarly; dense FP32 private records, contiguous reduced axes followed by kept suffix, suffix-dividing SIMD width, unchanged per-output addition order | Ported locally; K-pointer recurrence removes repeated coordinate work |
| Neutral padding trim | Existing P1 clamp excludes every reduce and every multi-pass kernel; shared rank-one mask plus explicit sum/max/min identity at each reduction makes wholly inactive chunks unobservable | Separate proof, unshifted signed prefix only; unsupported effects/index/bitcast/volatile/layout forms decline |
| Matrix row reuse | _Composed.emit_vector still reloads B once per output row and reconstructs A/B addresses inside K | MR2 on complete staged rows/N chunks at LMUL1; K-ordered FMA/conversion boundaries unchanged; odd M and partial N keep old kernel |
| Chunk geometry | Scalar segments can open a loop before a later pass changes VL/SEW/extent; old code only compared merge frames | Correctness prerequisite: close old loop before changing geometry; independent commit |
| Guarded narrow accesses | Existing C8 covers proven rank-one arithmetic progressions, not multi-term 2D matrix address trees | Not added in this batch |
| Broadcast views / arena | Historical SVD counterexample remains | Not ported |

All three performance switches live in CompileOptions and LowerOptions and change artifact identity when disabled. The production factory forwards them explicitly. Existing source hashing covers vectorize.py/matrix.py; the concurrent backend work completes transitive dependency coverage. New metadata records actual matched reductions, domain proofs, row blocks and geometry-boundary closures. No new IR, semantic contract, corpus source, reference or comparison policy is introduced.
