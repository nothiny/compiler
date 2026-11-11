# Pressure-aware elementwise widths

Phase two adds an internal width choice to the existing lowering stage,
using the same TIR/MIR representations. Production changes were committed
with the compatible narrow-memory work in `51f3c61`; the first three
lowering mechanisms remain separately reviewable at `ba3d22e`.

The source algorithm is the immutable exploration's
`prototype_vector_width_v4.py` and `factory_width_experiment_v2.py` in
`/tmp/a100-readonly-review-b-te2m9tiu/exploration/`. The destination adaptation
deliberately narrows applicability and adds explicit runtime alias safety.
The previous global LMUL-m2 attempt is not reused: this choice operates on
actual eligible chunk CFGs and predicts their live register groups.

`a100c/lower/vector_width.py` recognizes simple 32-lane strip-mined loops
inside the native program-instance loop. The static block bound must be
divisible by the new width; a runtime prefix clamp remains symbolic. It
never selects a width from the bound case's actual runtime N. Candidate
factors four then two are tried on private copies; both failing returns
the original module. An explicit opcode whitelist excludes reduction,
shuffle/gather/slide, packed register reinterpretation, scalar math service,
matrix/ordered operations, narrow indexed/scalar fallback and dynamic AVL.
Any scalar load/store inside the chunk body also declines the candidate.
Unknown control flow, memory roots or counters are not assumed safe.

The cost query `allocate.register_pressure(fn)` is read-only and reuses
the allocator's real CFG liveness and implied indexed-memory EMUL groups.
Inputs/results are conservatively live together, masks consume registers,
and all analyses are freshly computed on each candidate. The budget is
28 vector registers and no more GPR demand than max(25, original demand).
MIR verification must pass before selection; allocation still owns actual
coloring and spills. Candidate-local unused pure temporaries are removed,
while memory/state/unknown operations remain roots. If no width succeeds,
that cleanup is discarded with the candidate.

## Runtime alias guard

Different pointer parameters can alias. Increasing width without an alias
proof could alter the load/store interleaving of overlapping views. The
selector therefore resolves every TIR load/store root to an existing
ArgumentLayout view index and forms all read/write and write/write pairs.
A pointer loaded from a table is not replaced by the table's storage;
such unknown roots decline the transformation. Volatile access and an
already-identical read/write root also decline it.

Generated native code reads each involved view's backing `storage` once in
the dominating entry block. The ABI already provides this field at offset
48 in a 56-byte record, checked by `a100rt.h` static assertions. Distinct
bundle storages are disjoint payloads. Only when every required pair has
different storage does the selected width become 64 or 128. Otherwise
both AVL and the chunk induction step are 32. They consume the same native
runtime width, with no Python decision and no alias relation in the cache
key. The selected LMUL group stays large enough for either active width.
Unmasked work counters advance by that same runtime width; masked counters
use the original vpopc at the active VL. Runtime/zero-AVL-safe whole-register
spills are provided by the preceding backend fix.

The ABI probe source/result are `width-abi-probe.c` / `width-abi-probe.log`.
Its cross-compiled native result was `distinct=128 shifted=32 same=32`,
with `storage_offset=48 view_size=56`.

This preserves the old 32-lane memory ordering for aliased views. It does
not repair pre-existing cross-chunk source alias/race semantics, and makes
no guarantee about inter-program schedules with source data races.

## Executed checks

`a100c/tests/test_elementwise_width.py` executes 44 native checks, each with
three repeats:

* Original and selected paths at N=0/1/17/97/257, preserving guarded tails,
  negative values, NaN/Inf/signed zero, observable NaN-payload bitcast and
  exact INT32 wrapping arithmetic. Independent expected values are built
  from snapshots before native execution; on/off bytes also agree.
* One artifact handles disjoint buffers, in-place aliases, positive-shift
  overlap within one original chunk (N=17), and negative-shift forward-safe
  overlap (N=97), all with independently computed expected outputs. Both
  variants have one cache key across these runtime alias relationships.
* One factory handles original GELU's 128 -> 262144 -> 128 sequence with
  exactly one compile and two cache hits per on/off variant, passing the
  unchanged original reference. Factor four is rejected by the live-vector
  budget and factor two selected. The native outputs are bit-identical.

See `width-contract.log`. The separate original small-size t8 smoke has
10/10 PASS (`width-guarded-smoke/`); full-corpus verification is independently
owned by the final validation task, not replaced by these probes.

## Paired instruction evidence

The collector and invariant checks are described in [RECORD.md](RECORD.md).
The frozen source is a real directory copy, not symlinked tools/source;
the collector asserts every imported a100c module belongs to that root.
`WIDTH_SNAPSHOT.json` production hashes match the committed phase-two source.
Both sides explicitly disable guarded narrow access, leaving all other
lowering choices equal and changing only `elementwise_width`.

| Extra large FP32 sample | Off instructions/launch | On | Reduction | Width |
|---|---:|---:|---:|---:|
| GELU 262144, 1 thread | 1,990,955 | 987,191 | 50.42% | 64 |
| GELU 262144, 8 threads | 1,991,256 | 987,576 | 50.40% | 64 |
| sigmoid 262144, 1 thread | 991,531 | 487,479 | 50.84% | 64 |
| add_value 262144, 1 thread | 401,715 | 100,414 | 75.00% | 128 |

All 32 profile launches pass their unchanged original case comparisons and
repeat consistency. Each shipped program's text bytes match an independently
assembled program.S. Every stable program-PC difference is nonnegative and
divisible by the repeat delta, and two independent repeat pairs produce
exactly the same launch count. Full raw paths/hashes and selection pressure
are recorded in [WIDTH_METRICS.json](WIDTH_METRICS.json) and
`width-metrics/*/{off,on}/profile.json`.

These samples use the unchanged case generators at additional sizes; they
do not count toward 2734 original-case coverage. The unit is dynamic guest
program instructions per complete native launch, all workers summed.
It is not a silicon time/speedup result or evidence that eight threads
make the operator faster. The off switch is
`A100C_ELEMENTWISE_WIDTH=off`, and both compiler entry points bind it to
their artifact identity.
