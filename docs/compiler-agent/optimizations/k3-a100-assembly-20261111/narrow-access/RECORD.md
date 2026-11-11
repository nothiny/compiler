# Narrow accesses: actual address guards with the scalar path retained

The current FP16 IME listing still had expensive scalar halfword loops. The
existing C8 path already handles statically proven strided memory; the new
helper handles the residual case using actual i64 byte offsets. It checks every
active lane in each 16-lane segment and branches to contiguous masked vector
memory only when all match. A mismatch executes the previous scalar sequence.
The guard itself performs no source/destination memory access. Full type checks
on vector defaults and volatile rejection preserve the v3 experiment's fixes.
The original scratch ownership, vector state at joins and source store order
remain explicit. Eligible data groups are LMUL1 with 16/32 lanes; wider chunks
decline rather than importing an unsupported pressure assumption.

Frozen revision `1a7d104811605803`, same cases/seed30 and original comparisons:

| FP16 IME matrix multiply | Guard off | Guard on | Guest program instruction reduction |
| --- | ---: | ---: | ---: |
| Original 16^3 | 34,520 | 22,651 | 34.38% |
| Additional 128^3 | 7,438,232 | 4,589,206 | 38.30% |

Each cell has two independent repeats-1/repeats-3 difference pairs with exactly
equal program-PC counts. Assembly is reassembled and byte-checked against the
same ELF. These are functional-QEMU guest instruction counts, not chip timings.
The actual `smt.vfwmadot` instruction PCs are obtained from that ELF's GNU
objdump and joined to the raw dynamic PC counts: off/on both execute 16 IME
instructions at 16^3 and 4096 at 128^3. The former includes the original source
K padding and exceeds the mathematical minimum; this does not claim ideal tile
utilization. The benefit is surrounding memory/address work, not fewer MACs.

`semantic-checks.json` records 112 exact native checks: contiguous/segmented/
reverse/random/duplicate indices, load/store, masks including a poisoned inactive
first lane, unsigned vector defaults and volatile loads. The native runtime
executes three repeats. Forty test-only guard-removal witness executions include
22 failures, detecting an invalid shortcut for both load and store. Additional
unit checks reject the unsigned type mismatch and volatile form even when no
emission context is available. These probes are separate from corpus coverage.

`original-cases/` contains the original matmul, attention_forward and
naive_attn_decoding cases: 21 cases each at 1/2/4/8 threads, all 84 comparisons
PASS. `option-identity.json` checks both compiler entry points, all five batch
switches, twelve distinct compiled cache entries and 24 native comparisons.
Full input validation is owned by the subsequent frozen final scan, not claimed
by this component report.

`SOURCE_MANIFEST.json` binds the measurement source. During collection we found
that a symlinked `tools/run_scan.py` can prepend the shared tree to `sys.path`.
The four final records were rerun after copying that tool into the frozen root
and asserting the imported driver belongs to that root; they reproduce the
earlier numbers exactly. The uncorrected preliminary records stay in `/tmp`
and are not used as frozen evidence. `collect_pair.py` contains the assertion.

The main reusable design lesson is to make the runtime proof an explicit
lowering helper consuming the existing address tree and emitting ordinary MIR.
Typed defaults and active-lane membership are legality inputs, not hints. The
scalar implementation remains available for unproven addresses. No fourth IR,
new MIR stage, operator-name dispatch or BF16-IME claim is introduced.
