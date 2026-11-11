# Guarded narrow-memory applicability

Source: `/tmp/a100-readonly-review-b-te2m9tiu/exploration/prototype_guarded_narrow_v3.py`
and its actual native probes. Destination starts at the preceding lower/backend
increments (`ba3d22e` / `728d12b`). Source files remain unchanged. The new helper
is production lowering code; it does not patch emitter methods or add an IR.

| Requirement | Destination evidence/interface | Decision |
| --- | --- | --- |
| Statically proven unit/strided access first | Existing wide proof and W2-C8 remain before `_lower_*_narrow` | Reuse; guard only the previous scalar fallback |
| Every active lane has the exact contiguous byte address | Existing whole-tree i64 materialization; each 16-lane segment compares actual byte offsets with `first + lane * element_bytes` | Adapt the v3 runtime proof; never compare truncated indices |
| Masked positions do not touch external memory | Active-only mismatch reduction; actual masked vector accesses; loads merge typed `other`; all-inactive segments can use an invalid base without access | Preserve, with poisoned +/-2^40 and first-inactive native cases |
| Typed default legality | A vector `other` with a different complete MIR type declines before guard emission | Reuse the v3 conservative fix; do not infer legality from SEW alone |
| Volatile memory semantics | Volatile load/store declines the guarded path | Preserve the previous sequence |
| Correct general fallback | Previous scalar bodies retained as `_lower_load_narrow_scalar` / `_lower_store_narrow_scalar` | Use the unchanged sequence on any guard mismatch |
| Bounded pressure and scratch | Only data LMUL1 and VL16/32; 16-lane segments; existing worker-private narrow scratch | Decline wider groups/chunks; masks/state restored at join |
| Store ordering and overlap | Segment order stays increasing; contiguous active addresses have no duplicate within a segment; values and masks dominate the branch | Extend the source load experiment to stores, with independent exact native probes |
| Observable switch and dependency identity | CompileOptions/LowerOptions/factory `guarded_narrow_access`; `A100C_GUARDED_NARROW_ACCESS=off`; new helper discovered by compiler revision | Distinct artifacts and both compile entry points tested |

No reference, corpus case, comparison policy or resource semantics changes.
This is human-guided assembly work, not an engine optimization gate.
