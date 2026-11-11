# Backend applicability and implementation boundary

Destination: `c8ade47` plus the explicitly preserved working tree. Source evidence:
`/tmp/a100-readonly-review-b-te2m9tiu/exploration/READ_ONLY_OPTIMIZATION_REPORT.txt`.
The source experiments remain read-only. This is human-directed work, with guest
instruction counts as a proxy; it does not change engine acceptance or assert G9.

| Source requirement | Current destination evidence | Disposition |
| --- | --- | --- |
| Full vector spill slots and aligned register groups | Allocator already reserves `target.vlenb * LMUL`; MIR has `vspill`/`vreload` | Reuse slot/IR contracts; select RVV whole-register transfers |
| VL/VTYPE preserved across spills | Old emitter changes VTYPE, restores only constant AVL; runtime AVL refuses | Whole-register transfers do not consume or modify VL/VTYPE; add executed all-byte/state checks |
| Vector state deduplication accounts for all setters | Textual peephole currently recognizes only `vsetvli` | Invalidate across `vsetivli`/`vsetvl`; preserve observable destination writes |
| Complete artifact revision dependencies | Static driver list omits factory, passes, plan tiles/stages | Hash deterministic production-source discovery; exclude tests/cache/build outputs |
| Runtime object transitive source dependencies | Runtime stamp hashes only each `.c`, flags and tool paths | Include runtime headers in object identity; verify cached and clean builds agree after a header mutation in scratch |
| Feature switches distinguish artifacts | `CompileOptions.identity_part` owns option identity | Add the three coordinated lowering options; retain off/on comparison |

Whole-register spill instructions use LMUL group sizes 1/2/4/8 and the existing
stack-owned storage. Masks remain refused by the allocator; no external memory
access moves, arithmetic changes, new IR layer, pass stage or floating-policy
change is introduced. Existing scalar/vector general lowering stays intact.
The current complete input report has two compile timeouts, so this document
does not claim a fully correct starting compiler or completed acceptance.
