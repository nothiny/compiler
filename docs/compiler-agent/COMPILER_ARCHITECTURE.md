# Compiler architecture — SpacemiT K3 A100, correctness-only run

Planning declaration for task T004. Every target decision below cites the
recorded Fact ids in `docs/compiler-agent/PROJECT_STATE.json` (F001–F056,
origin `input`, status `active`); corpus statements cite
`docs/compiler-agent/OPERATOR_INVENTORY.md` (workload analysis, T003) and the
corpus's own declarations in `ops/`. No target value is invented; unknowns are
named as such. This document declares the design; it creates no compiler
modules (planning does not implement).

Scope pins (F055, chip.md:12–29): `Acceptance scope: correctness_only` — no
performance metric, benchmark, timing target, speedup or measured optimization
round is scheduled; the basic optimization passes (CSE, DCE, constant
folding/propagation, copy propagation, strength reduction, LICM) remain
ordinary implementation work under their legality conditions. `Required
execution evidence: resources` (F050, F055) — representative multi-worker
cases must distribute useful work and applicable matrix cases must execute
real IME instructions, bound to the same prepared run, case and artifact.
Execution target is the pinned functional emulator (A001: QEMU guest threads
are not physical A100 cores; board porting is a later step).

## 1. Compilation path (end to end)

```text
operator source (ops/suite/{dev,perf}/*.py: one @triton.jit kernel + case layer)
  + case (compile_case payload: args/meta/grid/outputs/comparison/...)
      |
      v
  [frontend]  source loading, declared-surface check, specialization
              (identity = meta tier), constexpr folding, type/shape
              wellformedness, AST -> TIR, grid-model extraction
      |
      v   TIR (tir/v1)  -- verified
  [TIR passes]  cse, dce, const-fold/propagate, copy-propagate,
                strength-reduction, licm   (normal pipeline, switched, traced)
      |
      v   TIR (tir/v1)
  [execution planning]  work partition (1/2/4/8), stage/sync/merge plan,
                        workspace ownership, dot tiling plan
      |
      v   TIR + plan
  [lowering]  TIR -> MIR: RVV vectorization (masked tails), IME tile
              lowering, scalar/int64/atomic paths, address materialization
      |
      v   MIR (mir/v1)  -- verified (incl. IME legality)
  [legalisation]  expressible-but-illegal -> legal sequences
  [selection]     one generic matcher over the declared repertoire table
  [allocation]    32 GPRs + 32 vector regs (4 KB file), IME group parity,
                  compiler-owned spill/split
      |
      v   MIR (mir/v1), allocated
  [emission]  complete program-level RISC-V assembly (.S): entry, bundle
              argument binding, native grid evaluation, worker range loops,
              stages/barriers, constants, workspace
      |
      v
  cross as + ld + precompiled native runtime  ->  ELF64-little-RISC-V
      |
      v
  QEMU execution via a100_support transport (run-riscv.sh, bundle.bin)
      |
      v
  host readback (unpack_outputs) + independent comparison with the case's
  declared policy (never the compiler grading itself)
```

Boundaries (F043, F042, F044): the compiler generates the complete
single-operator native execution program in program-level assembly; the
declared build path is the cross GNU toolchain only (as/ld/gcc 14.3.0 /
binutils 2.43.1, lp64d sysroot); the unusable SpacemiT LLVM package (F012) and
every vendor-stack reference (F044) stay off the code-generation path. Python
participates in compilation, staging and comparison only; running the produced
`operator_exec` neither starts, embeds nor calls Python (F043).

## 2. Representations

Two verified IRs plus the emitted artifact. A middle target form earns its
place: source semantics (block tensors, masks, broadcasts, reductions, SPMD
program structure) and target structure (RVV regions, IME tiles, worker
ranges, stage barriers) are different responsibilities with different
consumers; fusing them into one transformation would leave no boundary to
bisect at (IR-REPRESENTATION-CHOICES).

### 2.1 TIR — `tir/v1` (module `a100c/ir/tir.py`)

Typed block-tensor dataflow with structured control flow. Carries, per
IR-SEMANTIC-FIDELITY, with a named owner for every check:

| source property | carrier in TIR | who checks |
|---|---|---|
| element width | `Type.width` on every value | TIR verifier; frontend type rules |
| signedness (separate from width) | `Type.signed` | TIR verifier; conversion legalisation |
| value conversion vs bit reinterpretation | distinct ops `convert` / `bitcast` (never one `cast`) | TIR verifier (no identity-fold across them); lowering |
| mask semantics + disabled-position default | `mask` operand plus per-op `other`/`none` default recorded on load/store/atomic | TIR verifier (masked op without declared default is malformed); lowering |
| shape, stride, layout order | `Shape` with per-axis extent and `broadcast` flag distinct from real extent | frontend shape inference; verifier |
| index arithmetic width / overflow | all index math typed (i32/i64) with declared wrap semantics; addresses formed in i64 | verifier; lowering |
| structured groups (blocks/tiles) | `Tensor` values with rank/extent; `dot` carries tile extents and reduction axis | verifier; tile planner |
| compile-time vs runtime boundary | constexpr-folded at the frontend; runtime scalars/pointers/grid extents remain symbolic | specialization stage; grid model |
| reduction contract | `reduce` carries op, axes, keep_dims, identity (per op × dtype, signedness-correct), tie-break for index forms | verifier; reduction lowering |
| numeric class | exact (int/index/bool) vs tolerance-class (fp) recorded per output from the case comparison policy | comparison harness reads it from the case, never the compiler |
| control flow | structured regions (if/loop) with explicit join parameters for carried values | verifier (a carried value with no join is malformed) |

Frontend producer: `a100c/frontend/lower_tir.py`. Consumers: the six basic
passes, the execution planner, the lowering. Verifier test:
`a100c/tests/test_tir_verifier.py` (rejects one hand-built malformed module
per invariant class — use-before-def, type contradiction, masked op without
default, broadcast extent consumed as real, carried value without join — and
accepts the real frontend's output for valid kernels).

### 2.2 MIR — `mir/v1` (module `a100c/ir/mir.py`)

Virtual-register dataflow over target-shaped operations with an explicit CFG
(blocks + branches + block parameters as joins). Carries:

- `vsetvli` regions: SEW, LMUL, vl and tail policy per region; region
  consistency is a verifier invariant (a vector op must belong to a region
  whose SEW matches its operand width; EEW range 8..64 per F026).
- masked vector memory ops: active-lane semantics, inactive positions perform
  no access and yield the declared default (F026; corpus pitfall: masked load
  without `other` is undefined at disabled positions — never zero-filled).
- IME tile operations carrying the sourced operand contract: LMUL=1 only, vs1
  = A tile row-major, vs2 = B tile column-major, vd even-numbered when
  MUL_C=2, destination group must not overlap vs1/vs2, operand format per
  family (F030/F031/F033/F040). The MIR verifier rejects illegal forms before
  emission (F041: these are hardware traps the compiler must prevent by
  construction).
- worker partition structure: per-worker entry, range loops over program
  instances / output tiles, stage barrier calls, merge operations, shared and
  thread-private workspace addresses.
- address materialization in i64, whole-tree (base + broadcast-applied
  per-dimension indices × strides, one expression per IR-LOWERING-CONTRACT —
  never accumulated one dimension at a time).

Verifiers: `a100c/tests/test_mir_verifier.py` (malformed per invariant class,
including constructed IME illegality: odd vd, overlap, LMUL≠1) plus
`a100c/tests/test_allocate.py` for allocation invariants.

### 2.3 Program assembly (emitted artifact)

Complete single-operator `.S` text: process entry contract (via the native
runtime's `main`), bundle argument binding, native grid evaluation, worker
range loops, computation stages, constants, workspace layout. Consumed by the
declared cross `as`/`ld` (F003, F042 — the assembler accepts `smt.`-prefixed
IME mnemonics, probed). Emission is mechanical (BE-EMISSION): every emitted
construct traces to a selected MIR op; the pre-handover check is the MIR
verifier plus emission invariants, so a rejection from `as`/`ld` is reported
with the originating construct, not as a bare tool error.

## 3. Frontend (module `a100c/frontend/`)

**Source contract (FE-SOURCE-CONTRACT).** The compile unit is one operator
file from the corpus's declared set (`suite/dev/*.py`, `suite/perf/*.py`; 500
files, T003): docstring + `OPERATOR` literal + exactly one `@triton.jit`
function + case layer (`SHAPES`, `DTYPES`, `FIXED_META`, `ref`, `_make_case`,
`make_case`). The frontend reads the module AST (it never imports the operator
module for execution semantics) and the case payload from `compile_case`
(`args`, `meta`, `launch_meta`, `grid`, `outputs`, `comparison`,
`pointer_dtypes`, `allocations`, `pointer_table_relocations`). A unit that
violates the declared invariants (two jit functions, a foreign import on the
execution path, a construct outside the declared surface) is refused with a
source location, never compiled on a guess.

**Declared surface (FE-UNSUPPORTED-SURFACE).** `a100c/frontend/surface.py`
holds the 107-construct / 280-parameter surface recorded in
`workload.api_spec` as data; every construct parameter is classified
*implemented*, *ignorable with a recorded reason* (performance-only:
`cache_modifier`, `eviction_policy`, `num_stages`, `warp_specialize`, …) or
*refused*. The enumeration test walks the declared table and asserts each
classification; the control (marking a semantic parameter ignorable) must fail
a correctness test. The exclusion table in OPERATOR_INVENTORY §3 (fp8, tf32,
backward, libdevice, `dot_scaled`/int4, `inline_asm_elementwise`, tensor
descriptors, nonexistent `tl.tanh`/`tl.pow`) is the refusal boundary;
`tl.swizzle2d` is declared with 0 corpus calls and is either implemented or
declared-unsupported with a refusal witness in FRONTEND_COVERAGE.json.

**Specialization identity (FE-COMPILE-TIME-VS-RUNTIME,
MECH-COMPILE-ONCE-PER-SPECIALIZATION).** The unit of compilation is
(kernel, specialization key) at the corpus's declared *meta* tier: source path
+ kernel name + per-pointer device dtype (`pointer_dtypes` overrides, e.g.
bfloat16 pointers on float32 host storage) + per-scalar Triton specialization
class (int: ==1 / divisible-by-16 / other; float: dtype), honoring
`do_not_specialize` / `do_not_specialize_on_alignment` + every constexpr in
`meta`/`launch_meta` (for `@triton.autotune` operators, 11 files, the
deterministically chosen config's constexprs; choice is correctness-neutral).
Shapes, grid values, buffer contents and scalar values are **runtime** and
never baked; the census target is the corpus's own 2161 identities (T003), and
the driver's compile count must match it (not the 2734 case count). The `==1`
class may be treated as constant 1 and div-16 as an alignment fact — value
classes only, never values.

**Constexpr folding.** `tl.constexpr` conditions, dtype predicates
(`is_floating()`, `is_int_signed()`, `int_bitwidth`, `ptr.type.element_ty`,
`x.dtype.element_ty` — 81/60/15 operators, T003 §6.8) and dead dispatch
branches (16 `tl.float64` branches that no declared case dtype exercises) are
folded at specialization; the folded comparison must still evaluate for
specialization purposes.

**Type rules (FE-TYPE-RULES).** Literal typing, promotion and unification for
mixed-type operations, result types, explicit conversion vs bit-level
reinterpretation (distinct constructs), zero-dimensional values — from the
pinned Triton 3.8 semantics (the reference environment pins
`triton.__version__ == 3.8.0`, F013/F049), not from what the target happens to
support. Target gaps are handled by legalisation, not by changing source
semantics.

**Shapes and broadcast (FE-SHAPE-AND-BROADCAST).** Rank/extent inference with
broadcast extents distinguished from real extents; alignment of ranks per the
language's declared rules; a shape disagreement the rules do not permit is a
diagnostic, not a silent stretch. Address expressions are lowered as whole
trees (FE-ADDRESS-EXPRESSIONS): base, per-dimension indices, strides,
broadcast extents and bounds combined under the declared rules, checkable
against an independent index computation.

**Grid model (launch geometry is runtime).** The bundle carries views and
scalars but not the grid (the a100-native-io/v1 format, F046/F047), and the
identity contract excludes it (the corpus's own economics, T003 §7). The
frontend therefore extracts the grid *expression* from the operator's case
layer (`grid = <expr>` in `_make_case`, or the `lambda meta:` form): it
evaluates the case layer at compile time under a provenance-tracking
interpreter, and every value the grid expression consumes must be proven equal
to a bundle-visible quantity (a scalar argument or a view extent); the emitted
program then contains a native grid-evaluation routine reading exactly those
quantities at run time. A compile-time equality self-check against the
compiling case's concrete grid validates the model; when a grid input cannot
be tied to a bundle-visible quantity, the operator is refused with a located
diagnostic (MECH-DIAGNOSTIC-REFUSAL) rather than baked. `tl.program_id(axis)`
decomposes from the linear worker-range index; `tl.num_programs(axis)` reads
the runtime grid extents (22 operators, T003).

## 4. Basic optimization passes (module `a100c/passes/`)

Implemented and enabled in the normal pipeline as ordinary coding/input work —
never capability/purpose/tag `optimization`, never G9 (F055; IR-BASIC-OPTIMIZATIONS):

| pass | legality condition that must survive rewriting |
|---|---|
| CSE | equivalent values and available definitions; memory reuse only with an effect/alias proof |
| DCE | observable stores, atomics, synchronization and stage effects preserved |
| constant folding/propagation | source width, signedness, overflow, rounding and path conditions |
| copy propagation | dominance, control-flow joins, value identity, pointer semantics |
| strength reduction | equivalent integer/index behavior; the declared floating policy |
| LICM | invariance, effects, aliasing, masks, and safety when a loop executes zero times |

Each pass registers in the pipeline (`a100c/passes/pipeline.py`) with a real
switch and a trace counter, and declares consumed/preserved/invalidated
analyses against one shared analysis owner (`a100c/passes/analyses.py`:
dominance, liveness, loop structure, memory effects — IR-ANALYSIS-VALIDITY,
MECH-SHARED-ANALYSIS-BUNDLE). Witness shape per pass: an eligible expression
or loop is actually rewritten (structural trace), the executed result still
compares PASS against the independent reference, and an unsafe case is
declined (e.g. hoisting a masked load across a crossing store is refused);
a legal refusal on one input never removes the pass. The full input regression
runs through the enabled pipeline before final validation. No timing, counter
quota or measured gain is required or claimed.

## 5. Execution planning (modules `a100c/plan/`)

**Work unit and distribution (TGT-EXECUTION-RESOURCES; F018, F053, F019,
F016).** The unit of parallel work is a *native work range*: a set of source
program instances (or legally repartitioned output tiles) executed by one
persistent worker thread. At launch the generated program reads `--threads N`
(N ∈ {1,2,4,8}; at most 8 A100 compute workers, F053) and computes each
worker's range from `(worker_id, N)`; the runtime creates the persistent
pthread pool once per process (probed: distinct guest tids, full coverage, one
initialization, F019). Standard Linux threads drive scalar/vector/matrix
compute alike (homogeneous fusion, F016). The source grid may be repartitioned
when semantics permit (F018): source program granularity need not be the
native scheduling granularity.

**Partition policies.** (a) strided round-robin over source program instances
— the default; preserves per-program semantics exactly (each instance executes
exactly once across all workers); (b) contiguous chunks over output tiles when
repartitioning is legal (elementwise/norm families; 484/500 operators have
disjoint output ownership, T003); (c) two-phase partial reduction with an
explicit merge stage (cross-worker reductions); (d) worker count one — the
single-thread serial configuration of the *same artifact* (no separate serial
binary; barriers degrade to no-ops).

**Stages, visibility and merge semantics (IR-EFFECTS-SYNC; F018, F054,
A006).** Cross-worker dependencies become explicit stages: partial results are
written to owned workspace regions, a stage barrier (pthread barrier from the
native runtime) establishes visibility, then a merge step combines partials
under the source's own semantics (reduction order preserved within the
declared tolerance for floating outputs; exact for integer/index/boolean).
Memory between A100 harts is assumed RVWMO with documented per-level cache
coherence (A006): generated cross-worker communication uses explicit
pthread/atomic synchronization and assumes no implicit coherence. The
source's own `tl.atomic_*` (16 operators) and `tl.debug_barrier` (7 operators)
lower to amo/atomic instructions and an intra-program fence with the case's
`sem`/`scope` mapped onto that model. Independent work stays within a worker —
no barrier is added where none is needed (F018).

**Workspace ownership (A100-NATIVE-OPERATOR).** Shared workspace (two-phase
partials, IME staging/padding buffers) and padded, aligned thread-private
buffers are allocated once before the hot loops; ownership and lifetimes are
declared in the stage plan so no two workers write one location outside the
declared merge, and buffers are re-initialized between repeated calls in one
process. Under the pinned QEMU endpoint the executable memory path is Linux
userspace virtual memory (F025); TCM/DMA/spinlock MMIO regions are not on
this path and no generated code may assume them (A007, F054).

## 6. Lowering (modules `a100c/lower/`)

**RVV vectorization (`vectorize.py`).** RVV 1.0 at VLEN=1024, ELEN=64 (F006,
F026, F028): elementwise blocks lower to `vsetvli`-sized vector loops with vl
set to the exact element count; tails are handled by mask registers (`v0`) on
loads, stores and compute — a masked load without `other` leaves disabled
lanes undefined (never zeroed, never stored), a masked store writes only
active lanes (corpus pitfall 6, T003 §6). Whole-vector bodies are emitted when
the extent divides the vector length (mask omitted); ragged extents get a
masked epilogue; zero-extent loops execute zero times and size-one works
(RT-LAUNCH-GEOMETRY: exact multiple, non-multiple, zero). LMUL=1 is the
default register configuration (1024-bit compute width at VLEN=1024); wider
LMUL is legal for ordinary RVV and chosen only under allocator pressure
tracking; IME requires LMUL=1 always (F033). Wide contiguous accesses are
selected only from proven contiguity/alignment (the `multiple_of` /
`max_contiguous` hints feed the proof); unproven accesses keep masked or
scalar forms (MECH-MASKED-VECTOR-ACCESS).

**IME matrix lowering (`matrix.py`).** Applicable families on the input path
are INT8 8×16×8 → INT32 (`smt.vmadot` with the u/us/su signedness variants)
and FP16 8×8×8 → FP32 (`smt.vfwmadot`), per the corpus dtype surface (F037:
no int4/fp8 cases; F030: tile families; F033: legality). `tl.dot(A[M,K],
B[K,N])` tiles into IME tiles: vs1 holds the A tile (row-major), vs2 the B
tile (column-major — the geometric layout statement of `C ← C + A×Bᵀ` means no
software transpose when the memory layout already provides columns; otherwise
operands are packed via RVV loads or the `smt.vpack` family, F031/F035). The
accumulator is vd, chained across the K loop through the `acc` parameter;
integer paths accumulate in 32-bit modular arithmetic with signed accumulator
and operand signedness by suffix; the floating path takes FP16 inputs and
accumulates in FP32 (F051). Register grouping: MUL_C=2 — vd even-numbered with
vd+vd+1 the group, destination group never overlapping vs1/vs2; the allocator
honors the parity/group constraints and the MIR verifier rejects violations
(F033/F040/F041). Non-divisible M/N/K shapes: the compiler writes zero-padded
staging tiles (it never reads out-of-range memory to construct a nominally
neutral term) and masks M/N tail stores; small or ragged tails may instead take
the ordinary RVV FMA path — either is legal, both are verified. Implicit
control state: MCPM.BF16 selects the 16-bit operand format for
`smt.vfwmadot*`/`smt.vmadot.hp*` (F051); under the pinned QEMU the CSR is not
userspace-accessible and the executed `smt.vfwmadot` selects the FP16 format
(F011, F034) — so only FP16 operands reach IME floating tiles, the standard
vm mask is not a mask control for matrix instructions, and no
vtype.lambda/altfmt fields exist (F032): predication is structural (staged
tiles), never assumed from ordinary vector state. **BF16 gap**: the pinned
emulator's BF16 IME format selection has not passed (F010, F034) — BF16
`tl.dot` cases lower to the vector FP32 path (BF16→FP32 conversion is exact;
results within the case's declared bf16 tolerance), the gap is recorded
separately, and FP16 or vector success is never claimed as BF16 IME execution.

**Scalar, integer and atomic paths (`scalar.py`).** int64/bool/uint logic and
index arithmetic lower to RV64 scalar (or EEW=64 vector) sequences with the
declared wrap/shift/division semantics (A003); atomics lower to
amo/atomic instructions carrying mask and signedness (a masked atomic performs
no access at disabled positions); `tl.debug_barrier` orders intra-program
effects. fp16/bf16 elementwise compute may use FP32 lanes with one final
rounding back to storage width — inside each case's declared tolerance
(fp16 1e-2, bf16 2e-2; fp32 stays IEEE) — a declared numeric decision with a
per-pass switch, so a numeric regression is attributable to one pass
(IR-NUMERIC-POLICY).

**Addresses (`addresses.py`).** Every tensor access materializes its address
as one whole tree: base pointer + Σ index_axis × stride_axis with broadcast
extents applied before accumulation, in i64, preserving casts and
signedness; a narrower index type is used only where a value class proves the
range. The lowering is checked against an independent index computation on
shapes with >2 dimensions, a broadcast dimension, a non-contiguous stride and
a bound that is not a multiple of the block extent (FE-ADDRESS-EXPRESSIONS
witness).

## 7. Backend (modules `a100c/backend/`)

**Repertoire as data (`repertoire.py`; TGT-INSTRUCTION-REPERTOIRE,
MECH-TARGET-DESCRIPTION-AS-DATA).** The target's operation set is a data
table: RVV 1.0 vector operations (EEW 8..64, LMUL 1..8 for ordinary vector,
masked load/store/compute, reductions), the IME `smt.*` set with per-family
operand constraints (tile extents, signedness variants, MUL_C, parity,
overlap, format — F029–F035, F040), and scalar RV64IMAFDC. Negative facts are
recorded in the table as refusals: the absent community forms (vmmacc etc.),
no Zvvmtls, no mixed FP16/BF16 inputs, no vm-mask for matrix instructions
(F032). Adding an operation is a table edit, never a matcher edit; a construct
with no entry is refused with a located diagnostic, never approximated by a
nearby operation.

**Legalisation (`legalize.py`; BE-LEGALIZATION).** One declared stage with a
contract: it accepts MIR constructs the target cannot execute directly
(unsupported widths, type pairs, operand forms) and rewrites them into legal
sequences; after it runs, every remaining construct is in the declared
repertoire — that guarantee is what selection relies on. Its tests feed each
declared illegal form and require a legal sequence whose result matches a
reference; the control (disabling one rewrite) makes the MIR verifier, not the
external assembler, report the illegal construct.

**Selection (`select.py`; BE-SELECTION-AS-TABLE).** One generic matcher over
the repertoire table; constraint-checked (operand width, parity, format,
alignment); a misaligned or wrong-width operand takes the legalisation path or
a refusal, never a silent match.

**Allocation (`allocate.py`; BE-ALLOCATION-CORRECTNESS).** Every live value
gets a location: 32 GPRs and the 32×128 B vector register file (F023, F028,
F039) with interference from a real liveness analysis over the real CFG (never
a linear scan of instruction order). Exceeding the vector file has no
architectural spill mechanism (F041): spill/split decisions are compiler-owned
(stack slots in the frame, restored before use, storage never reused while
live), IME group parity is an allocation constraint, and the compiler reports
its own per-function register consumption against the budget. The 1.5 MB
scratchpad and 1 MB L2 are per-cluster shared budgets (F022, F053) — never
assumed private to a worker.

**Emission (`emit.py`).** Mechanical, traceable (BE-EMISSION): the complete
program-level assembly with entry contract, bundle binding, native grid
evaluation, worker range loops, stages and barriers, constants and workspace
— every emitted construct traceable to a selected MIR op; the artifact is
checked against MIR invariants before the external assembler sees it.

## 8. Native runtime boundary (`a100c/runtime/`, precompiled C)

A reusable precompiled C runtime provides what generated assembly should not
re-implement (F043: threads, synchronization, memory, I/O; per-operator C
wrappers are not required): process `main` parsing `--bundle <path>
--threads <n> [--repeats <k>]`; the persistent pthread pool (1/2/4/8 workers,
reused across repeated calls in one process; separate process launches get
separate pools); stage barriers and C11 atomics (F054); workspace allocation;
and the bundle reader implementing the declared `a100-native-io/v1` format
(views with dtype/shape/strides/offset, typed scalars, pointer-table
relocations patched on open and restored on close — the single declared
argument layout both sides derive from, F046/F047; the format is the contract,
probed end to end with guest pointer relocation and bfloat16 value storage,
F007). `--repeats k` snapshots input storage and restores it before each
repeat so every repeat is an independent execution of the operator on the same
case — the in-process repeated-call check — with outputs read back after the
final repeat.

The runtime/helper ABI follows the RISC-V psABI (lp64d: integer args a0–a7,
FP args fa0–fa7, callee-saved rules, F045); the one internal convention the
compiler adds (the generated `operator_entry` signature and the helper call
forms) is declared once in the runtime header and consumed by both the emitter
and the runtime — never two independent assumptions (RT-ARGUMENT-MARSHALLING).
The runtime is built by the declared cross toolchain only (F002/F003/F004);
the boundary is proven with a hand-written assembly operator before the
pipeline exists (RT-EXECUTION-CONTRACT), so later failures are the compiler's.

The delivered executable runs as `./operator_exec` (via
`a100_support/run-riscv.sh` under QEMU with `-L sysroot`, F005) and neither
starts, embeds nor calls Python (F043); Python ends at compilation, staging
and comparison.

## 9. Driver, cache and a100_support integration

**Factory (the declared integration route).** `a100c/factory.py` exposes
`make_compiler()` returning an object with `compile_case(case) ->
ExecutableArtifact(executable, arguments=('--bundle','{bundle}','--threads','{threads}'),
provenance)`; setting `A100_COMPILER_FACTORY=a100c.factory:make_compiler` in
`.env` makes `a100_support.native_device.make_device()` construct the native
device (F047: it refuses until the factory is set — no reference fallback).
The device stages each case (`pack_case`), launches the artifact under QEMU,
and reads outputs back (`unpack_outputs`); the compiler never sees expected
outputs or oracle args (the transport strips them).

**Cache identity (BE-ARTIFACT-IDENTITY; F043).** Programs are cached by every
bound dependency: specialization identity (§3) + compiler revision (digest of
code-affecting files, not the whole tree) + target-model version + compile
options + argument-layout/bundle-format version. Shape, grid value, scalar
value and worker count are runtime inputs, not identity: one artifact serves
every case of an identity and every thread count (the program computes its
partition from `--threads`). The on-disk cache is shared across driver
processes and worker shards; a second sweep at the same revision compiles
nothing.

**Driver (`tools/run_scan.py`).** Enumerates cases with the corpus's own
harness (`ops/harness/compiler_api/run_cases.py --manifest … --dry-run` /
`opslib.runner.load_operator` + `make_case`, exactly as the harness does),
groups them by compile identity (compile once, run every case — the corpus's
declared economics: 2734 cases / 2161 identities), stages and executes via the
native device protocol under a per-case bound (`A100_EXECUTION_TIMEOUT`;
a case that does not return is a recorded failure, never a wait —
RT-FAULT-ISOLATION: one faulting case must not poison the next), compares
against the case's declared comparison policy (per-output comparator, rtol/
atol, equal_nan, `quantized_interval`, `allclose_sign_invariant`; integer,
index and boolean outputs exact — F052; the tolerance may be exploited, never
widened, and the reference never weakened), and writes the per-case rows of an
`input-regression/v1` report for `regression-record`, plus the manifest
builder for `regression-prepare` (every case, both tiers, per-case comparison
policies, `resource_evidence=true` on representative rows). The same driver
runs the corpus's own acceptance checks (compile count vs the identity
census ≤ 1.25×, cache-hit speed, resume-without-recompile).

**Generality checks (`tools/`).** `check_no_name_dispatch.py` — nothing below
the frontend branches on an operator, kernel or benchmark name (no
operator-name dispatch, precomputed answers or reference fallback, F052); its
`--witness` mode injects a name-keyed branch into a scratch copy of the
pipeline and must be caught (the witness exits nonzero — the check can fail).
The numeric-policy check widens a tolerance in a scratch copy and must fail
(IR-NUMERIC-POLICY control: the harness grades from the case, and a scratch
copy proves it).

## 10. Observability (IR-OBSERVABILITY, MECH-STAGE-BISECTION)

Per-stage textual dumps (TIR after the frontend and after each pass, the
execution plan, MIR after lowering/selection/allocation, the final `.S`),
requested by a compile option; source attribution carried on every node
through every stage into the emitted listing; per-pass trace counters
(fired/declined) distinguishing "fired zero times" from "disabled"; identical
inputs produce identical artifacts (RT-DETERMINISM). A wrong result is
localized by comparing the dump after each stage against that stage's declared
contract — the first incorrect stage — never by guessing from the final
symptom.

## 11. Validation route

1. **Vertical slice (gate G4, tagged `vertical-slice`)** — one small
   elementwise operator end to end: parse → TIR → plan → MIR → selection →
   allocation → emission → as/ld → QEMU execution → independent comparison,
   including its one-worker and multi-worker (2/4/8) paths on one artifact,
   and a ragged-tail case whose tail predicate removal is a recorded failing
   witness.
2. **Native runtime first** — the runtime/ABI/bundle boundary proven with a
   hand-written assembly operator and pool observation at 1/2/4/8 (F019),
   before the pipeline exists.
3. **IME slice before matrix breadth** — one INT8 and one FP16 dot case
   executing real `smt.vmadot` / `smt.vfwmadot` with counted executions bound
   to run/case/artifact (the QEMU instruction-count plugin, F008/F048),
   compared PASS — before the dot/attention/conv families at large.
4. **Breadth by feature class** (control flow and grid generality; reductions
   and scans with cross-worker merges; memory forms and atomics; layout and
   conversion; special math and bit-exact RNG; matrix breadth) — each class
   lands on the general, unoptimized path first, passes green there, then the
   basic passes are enabled on it (MECH-GENERAL-PATH-FIRST).
5. **Declared-surface coverage** — FRONTEND_COVERAGE.json records every one
   of the 107 constructs with evidence, covered parameters and the IR
   construct that carries it, or a declared-unsupported refusal witness; a
   coverage number computed against the declaration, not the corpus sample
   (VER-COVERAGE-MEANING).
6. **Full compile sweep (G6)** — every operator produces an artifact (or a
   located refusal, which is a finding, not a pass); compile count within the
   identity economics.
7. **Full scan (G7)** — all 2734 cases (suite/dev 2192 + suite/perf 542,
   both tiers in the corpus's declared order) executed and compared under the
   declared QEMU endpoint; every feature class validated at 1/2/4/8 workers
   across the scan (all cases at a primary configuration; stratified
   class subsets and representative rows at the remaining counts); failures
   classified by feature class and first incorrect stage (the census that
   drives the manager's repair rounds — two rounds, ten case-bound tasks
   each; ordinary scan failures never return to architectural planning).
8. **Parallel and resource evidence** — one compiled artifact measured at
   1/2/4/8 worker counts with the worker split recorded (generated-code
   parallelism: same artifact, per-worker completed units, overlapping
   intervals on distinct eligible units, correctness preserved at each count;
   recorded as execution evidence, not as a performance claim);
   `resource_evidence=true` manifest rows bind run/case/artifact identities,
   positive executed instruction counts for the declared IME mnemonics and
   overlapping useful work on distinct eligible units (F048, F050).
9. **Repeated-call and synchronization checks** — in-process `--repeats` with
   input restore across representative operators of every feature class
   (identical outputs; pool/workspace reuse; no cross-execution leakage);
   barrier-removal and mask-removal witnesses that must fail (a
   synchronization test that cannot fail is not one).
10. **Final regression (G8)** — clean-state rebuild, `regression-prepare`
    with the complete manifest, full executed comparison, `regression-record`;
    the declared architecture validation checks recorded with current
    evidence. Complete input success finishes the correctness-only delivery;
    no G9, no measured performance round (F055).

## 12. Refusals and known gaps (MECH-DIAGNOSTIC-REFUSAL)

- Constructs outside the declared 107-construct surface and the SUBSET
  exclusion table: refused at the frontend with a located diagnostic.
- Grid expressions whose inputs cannot be tied to bundle-visible quantities:
  refused (never baked).
- IME forms violating the operand contract (LMUL≠1, odd vd, overlap, format
  mismatch): rejected by the MIR verifier before emission (F033, F041).
- BF16 IME execution: not claimable under the pinned emulator (F010, F034);
  BF16 dot takes the vector FP32 path with the gap recorded.
- TCM/DMA/hardware-spinlock use: refused until interfaces are verified on the
  board (A007); not on the QEMU userspace path (F025).
- int4/sparse/scale IME families: not exercised by corpus dtypes (F037);
  int4 source-level dot is outside the declared surface (corpus exclusion).
- No operator-name dispatch, precomputed answers or reference fallback
  anywhere in the compiler (F052); the x86 Triton reference service never
  substitutes for candidate target execution (F049, F013).

## 13. Assumptions carried into implementation (from PROJECT_STATE)

A001 (QEMU is not a board model — resource evidence records guest threads,
partition and instruction counts, never physical cores), A002 (containerized
no-Python round trip unexercised — exercised with the first real artifact),
A003 (standard RISC-V integer/RVV FP semantics), A004 (naturally aligned
accesses with masked tails), A005 (vfwmadot rounding detail unspecified —
covered by tolerance, never claimed exact), A006 (RVWMO + explicit
synchronization), A007 (TCM/DMA unverified), A008 (IME-2.0 production pairing
unverified). Each is labelled in the state; none is promoted to a fact here.

## 14. Module and stage index

Responsibility-owned paths, pipeline stages with producer/consumer
interfaces, IR levels with their verification tests, the pass declarations,
the behavioural properties (including the required no-operator-name-dispatch
witness) and the validation checks are declared machine-readably in
`ARCHITECTURE_CONSTRAINTS.json` (project root; mirrored under
`docs/compiler-agent/`). The executable task DAG (T005–T022) is submitted to
the engine through `task-submit` and lives in `docs/compiler-agent/
PROJECT_STATE.json`; `EXECUTION_MODEL.json` (recorded via the execution-model
command) and `EXECUTION_RESOURCES.json` record the execution-model mapping and
the eligible-resource contract the resource evidence binds to.
