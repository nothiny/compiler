# Chip analysis — SpacemiT K3 A100 (QEMU functional development)

Task T002 (gate G1), acceptance scope `correctness_only`. This document splits
the target description (`chip.md`) and its declared `## Target pack` material
into provenance-labelled facts covering every category the input compilation
path needs. Facts live in `docs/compiler-agent/PROJECT_STATE.json`
(F016–F056 for this task, on top of the environment facts F001–F015); each
statement below cites its fact id and the document anchor inside the declared
material. Provenance labels follow chip.md: **FACT** = asserted by the declared
material (anchor cited), **RUNTIME_PROBE** = measured on this host (command and
conditions recorded), **EMPIRICAL** = inferred from a probe plus reasoning,
**ASSUMPTION** = needed but not stated (validation method recorded).

## Knowledge profile

The knowledge-profile declaration **is present**: `chip.md` line 13 declares
`Knowledge profile: k3-a100`, and the declared profile matches this target's
class (SpacemiT K3 A100 AI CPU). `chip.md` also declares
`Acceptance scope: correctness_only` (line 14) and
`Required execution evidence: resources` (line 15) — see F055. No advisory is
required for a missing profile.

## Target pack reading (acceptance[2])

`chip.md`'s `## Target pack` section declares **146 paths**. All 146 were
verified to resolve inside the project root (script-extracted from chip.md and
checked against the filesystem; none missing, none outside the root, no
symlink escapes — they live under `docs/compiler-agent/target-material/sources/`).

- **25 markdown documents** — read. The large manuals (`09_memory_storage.md`
  203 KB, `17_clock_reset.md` 150 KB, `k3_ds.md` 115 KB, `dma.md` 65 KB) were
  read at their full heading structure plus every compilation-relevant section
  (on-chip memory, A100 CPU chapter, DMA features, A100 datasheet section);
  the small documents were read in full, including the complete IME matrix
  extension specification (`ime_extension.md`, 2339 lines, English v0.6) and
  its Chinese edition (same v0.6, content verified to agree).
- **27 `.search.txt` files** — read. 25 are byte-identical (sha256) to their
  `.md` base, so the `.md` reading covers them; the 2 PDF `.search.txt`
  extractions (`K3_architecture_preview.pdf.search.txt`,
  `K3_brief_zh.pdf.search.txt`) were read directly at the relevant sections.
- **2 PDFs** (`K3_architecture_preview.pdf`, `K3_brief_zh.pdf`) — present,
  valid, version-pinned; their text extractions above were read.
- **94 binary figures** (86 PNG, 5 JPEG, 1 WEBP) — present and valid
  (magic-byte and size verified for every one). They are the figures embedded
  in the text documents (block diagrams, IME tile/vmadot/fwmadot figures,
  memory map, spinlock/DMA diagrams, TCM monitoring screenshots, pinmaps);
  their informative content is described by the captions and body of the parent
  text documents that were read. This session's image viewer uploads to a CDN
  instead of rendering, so the figures were verified as files and consumed
  through their parent documents' text.

The pack is reference material: other-chip examples (K1/A60), earlier matrix
proposals and the performance chapters do not expand this project's
requirements (chip.md lines 114–116, F038).

## execution_model

(TGT-EXECUTION-RESOURCES question list; facts F016–F020.)

- **Unit of parallel work.** The source language (Triton operators) exposes a
  grid of program instances; on the target the unit of parallel work the
  language/runtime exposes is the **standard Linux thread on an A100 hart**
  — homogeneous fusion means scalar, vector and matrix compute share one
  RISC-V programming model driven by ordinary Linux threads, with no
  heterogeneous scheduler (F016; `root_overview.md.search.txt:12-14`,
  `concept.md.search.txt:11-22`). The compiler's own work unit is a **native
  work range** (element ranges / rows / output tiles) handed to a persistent
  worker pool; the source grid may be repartitioned when semantics permit
  (F018; `chip.md#3`).
- **Execution resources.** 8 A100 AI cores in 2 clusters. Preview-level
  microarchitecture (F017; `K3_architecture_preview.pdf.search.txt:680-745`):
  each cluster = 4 scalar cores + 2 vector cores + 2 local-memory banks +
  shared L2; the Tensor Core (IME-2.0) is **shared by two compute cores**
  (accepts one MMA per cycle from each); a per-core private IME-1.0 unit
  (256/512-bit, INT8→INT32) also exists; each core has an independent 512-bit
  load channel and dual-issues one 512-bit load + one MMA per cycle. The
  resources are therefore **not equivalent** for matrix work: 8 workers are
  not 8 independent matrix throughputs (F053), and the production pairing
  must be confirmed on the board (A008).
- **How many units in flight / observable concurrency.** Up to **8 compute
  workers** (1/2/4/8 configurable; chip.md requires representative
  multi-worker cases to distribute useful work) — F018, F053. The vendor's
  own stack reports "K3 provides 8 AI cores and supports up to 8-thread
  inference" (F020; `llama.cpp.md.search.txt:301`).
- **Scheduling unit — who schedules.** The **OS schedules Linux threads**;
  there is no hardware work queue exposed to userspace on this path. Probed:
  a persistent pthread pool runs with distinct guest tids at 1/2/4/8 threads,
  full item coverage and one pool initialization (F019;
  `TOOLCHAIN_PROBES.json` threads rows). QEMU guest threads are **not**
  physical A100 cores (A001/A008). The vendor stack's X100-runtime
  least-loaded dispatch onto 4-thread A100-cluster groups is a reference
  model, not this project's contract (F020; preview:1106-1120).
- **Distribution mechanism / partition policy.** The compiler's generated
  program + native runtime distribute **native work ranges** to the persistent
  pool; partitioning is by non-overlapping output tiles/ranges (matrix work
  prefers non-overlapping output tiles), with explicit stages,
  synchronization and merges for cross-worker dependencies (F018;
  `chip.md#3`). Coverage, tails, ownership, visibility and repeated execution
  at 1/2/4/8 workers must be validated.
- **Serial expression (worker count of one).** A single worker is the
  single-thread serial configuration — probed directly (threads=1: one
  distinct tid, full coverage; F019). Single-core is a debug/comparison
  configuration; multi-core and applicable IME paths are required for
  delivery (chip.md scope).

## memory

(TGT-MEMORY-MODEL question list; facts F021–F026.)

- **Address spaces.** Board (main CPU domain map, F021;
  `06_address_map.md.search.txt`): RISCV TCM 64 MB @ `0x0000_0000`; DDR DRAM
  64 GB @ `0x1_0000_0000`; 128 KB boot ROM; 512 KB SRAM shared by Main/Real
  CPU domains; hardware Spinlock (32 units) @ `0xCAC9_1C00`; Mailbox0–6;
  AIDMA_0–7 / DMA350_0–1 / HSDMA. Per-cluster (F022; `08_cpu.md.search.txt:54-59`):
  32 KB L1 I + 32 KB L1 D per core, 1 MB L2 per cluster, **1.5 MB scratchpad
  per cluster**. Per work item (per hart, F023): the private vector register
  file of 32 × 128 B = **4 KB** ("effective 4 KB ultra-fast local scratchpad",
  preview:1261-1267).
- **Access scope — who may access what.** L1 caches are per-core private; L2
  and the 1.5 MB scratchpad are **cluster-shared** (a group resource, not
  per-thread private capacity — F022); the vector register file is per-hart
  private (F023); DDR/TCM are accessible by every work item through the
  address map (F021). Under the pinned QEMU endpoint the executable path is
  **Linux userspace virtual memory** — the probed transport round trip
  (pack_case → run-riscv.sh → native_bundle → unpack_outputs) with guest
  pointer relocation and bf16 value storage (F025); the board's TCM/DMA/
  spinlock MMIO regions are **not** part of the QEMU userspace path (A007).
- **Capacity.** TCM 64 MB (SoC window); DDR up to 64 GB (map) / 32 GB at
  51 GB/s (brief); L1 32 KB I + 32 KB D per core; L2 1 MB per cluster;
  scratchpad 1.5 MB per cluster; SRAM 512 KB shared; 4 KB vector file per
  hart (F021, F022, F023).
- **Coherence.** Documented per level (F022): L1 D-cache supports **MESI**,
  L2 supports **MOESI**. The formal cross-hart memory model is not stated in
  the pack — assumed **RVWMO** (implied by RVA23 compliance) with explicit
  pthread/atomic synchronization for cross-worker visibility (A006).
- **Visibility rule.** A write by one worker becomes visible to another via
  the documented cache-coherence protocols within a cluster; between
  clusters/verification on hardware is open (A006). The compiler's contract
  is explicit: cross-worker dependencies use explicit stages,
  synchronization and merges (F018), and merge semantics obey the case's
  comparison policy. Under the pinned QEMU the guest is a single coherent
  address space (F025), so the visibility rule is exercised, not the
  interconnect.
- **Ordering primitives.** Board: hardware spinlock — 32 lock units, APB,
  read-to-lock / write-0-to-unlock, predictable acquisition < 200 cycles,
  polling or interrupt modes (F054; `spinlock.md.search.txt`); ACLINT
  hart-local software/timer interrupts and APLIC up to 1023 external MSIs.
  Under QEMU userspace these MMIO devices are unavailable, so the generated
  code's ordering primitives are the native runtime's **pthread barriers /
  mutexes / atomics** (F054, A007).
- **Access constraints.** RVV 1.0 with VLEN=1024 (vlenb=128 measured) and
  ELEN=64 → supported vector element widths **8…64 bits**; IME input data
  uses EEW 8/16 with standard linear element ordering; Int4 (not in the
  corpus dtype set) uses packed nibbles (F026, F031). Misaligned and
  out-of-range access behaviour is **not stated in the pack** — recorded as
  assumption A004: the compiler emits naturally aligned accesses with masked
  tails and does not rely on misaligned support; validation is a bounded
  misaligned-access probe under QEMU plus an on-board check.
- **Host/accelerator allocation and transfer model.** Development runs are
  not host+accelerator: the **host Python packs case inputs into a bundle,
  the guest native executable reads it (pointers relocated), computes, and
  writes outputs the host unpacks and compares** (F025/F047). Ownership:
  Python owns preparation/comparison outside the program; the native
  executable owns computation; `./operator_exec` must not start, embed or
  call Python (F043). On the board, the Preview dataflow describes
  software-managed local memory and async DMA prefetch, but those software
  interfaces (allocation, completion, visibility, lifetime) are unverified —
  no generated code may assume TCM/DMA availability until verified (F024,
  A007).

## registers

(TGT-RESOURCE-BUDGET question list; facts F039–F041.)

- **Granularity.** Per work item (per hart): 32 GPRs (RISC-V standard) +
  **32 architectural vector registers v0–v31, 128 B each** (VLEN=1024); v0
  doubles as the RVV mask register; the vector register file is per-core
  private and the IME reuses exactly these registers — no dedicated matrix
  register file, no extra architectural state (F039). Per group (cluster):
  the shared L2 (1 MB) and scratchpad (1.5 MB) budgets (F022). Per resource:
  the IME-2.0 tensor engine is shared by two compute cores (F017/F053).
- **Total / how many.** 32 × 128 B = 4 KB of vector register file per hart;
  within IME instructions: inputs A and B each occupy a **single** vector
  register (LMUL=1 only), the accumulator occupies **MUL_C** registers —
  2 for the integer and FP16/BF16→FP32 families (vd even-numbered, vd+vd+1),
  1 for the block-scaled families; sparse paths additionally consume v0/v1
  as recovery masks and scale paths v0/v1 as scale parameters, leaving 30
  generally usable vector registers on those paths (F040).
- **Failure mode when exceeded.** Two distinct modes (F041): (a) violating
  IME **legality** — LMUL≠1, odd vd where MUL_C=2, destination/source
  overlap, format inconsistent with MCPM.BF16, non-even vs1 in
  sliding-window — raises an **illegal instruction exception** at execution;
  these are hardware traps the compiler must prevent by construction (check
  before emission). (b) Exceeding the 32×128 B vector register budget has
  **no architectural spill mechanism** — spill/split decisions are
  compiler-owned; the Preview notes heavy LMUL=4/8 use is prone to
  vector-register spills, and with VLEN=1024 LMUL=1 already gives 1024-bit
  compute width (conditional guidance, below).

## isa

(TGT-INSTRUCTION-REPERTOIRE question list; facts F027–F038.)

- **Declared operations (repertoire).** Baseline: RVA23* (RVA23U64/S64,
  **excluding the Hypervisor extension**), SV39, PMU, 32 PMP, ACLINT+APLIC;
  optional zvkng/zvksg/zvbc/zfh/zbc/zvfh/zfbmin/zvfbfmin/zvfbfwma and
  sdtri/svvptc/sspm/smepmp/smstateen/smcntrpmf; RVA23U64 makes V mandatory
  with Zvfhmin/Zvbb/Zvkt (F027). Vector: **RVV 1.0, VLEN=1024**, two parallel
  vector pipelines, operator classes INT/FP/CRYPTO/FDV/IME-1.0 (F028).
  Matrix: SpacemiT IME (`Zvvm_spacemit` profile v0.6, 2026-04-13), **46
  custom instructions** with the `smt.` vendor prefix, reusing the 32 vector
  registers; the A100 supports 13 sub-extensions (collective toolchain name
  `Xsmtvdotii`): integer (i4/i8), fp16/bf16→fp32, sliding-window, 4:2
  structured sparse, block-scaled (F029). Data-layout transformation:
  `smt.vpack.vv / vupack.vv / vnpack.vv / vnspack.vv / vnpack4.vv /
  vnspack4.vv` with imm2 interleave granularity (F035).
- **Operand shapes and types.** A100 tiles (LMUL=1): INT4×INT4→INT32
  **8×32×8**; INT8×INT8→INT32 **8×16×8**; FP16/BF16×FP16/BF16→FP32
  **8×8×8**; structured sparse INT4 8×64×8 / INT8 8×32×8; block-scaled
  Int4 8×32×8 / Int8 8×16×8 → FP16/BF16 (λ=8, MUL_C=1, SEW=16) (F030).
  Layout: vs1 = tile A row-major; vs2 = tile B column-major (B^T is
  geometric only — **no software transpose required**); vd = accumulator
  with implementation-defined result layout; Int4 packed nibbles; EEW 8/16
  linear order; signedness variants none/u/us/su with signed accumulation
  (F031).
- **Legality constraints.** LMUL=1 only (all other encodings reserved →
  illegal instruction); MUL_C=2 ⇒ vd even + no destination/source overlap;
  sliding-window ⇒ vs1 even; sparse/scale use v0/v1 with imm2/imm3 selects;
  `smt.vfwmadot*` input format must match MCPM.BF16; the RVV `vm` mask bit
  is **not** a mask control for matrix multiply instructions (F033).
- **Absences (negative facts, explicit).** Community `Zvvm` instructions
  `vmmacc`, `vwmmacc`, `vfmmacc`, `vfqwmmacc`, `vf8wmmacc` are **not
  supported** (functional equivalents exist for all but vf8wimmacc-e5m2);
  the `Zvvmtls` dedicated matrix load/store extension is **not implemented**
  (use `smt.vpack`); mixed FP16/BF16 formats within one instruction are
  **not defined**; `vtype.lambda`/`vtype.altfmt*` CSR fields are not
  implemented (A100 uses MCPM) (F032). The pinned QEMU's **BF16 IME format
  selection has not passed** and remains unverified — the bf16 matrix probe
  fails while its executed `smt.vfwmadot` selects the MCPM float16 operand
  format; FP16 or ordinary vector success cannot prove BF16 IME execution,
  and BF16 cases must be preserved with the gap recorded separately (F034,
  chip.md UNKNOWN). The **MCPM control CSR is not userspace-accessible**
  under the pinned QEMU (F034/F011). A100 RVA23* **excludes the
  Hypervisor** extension (F027). The K1/A60 generation (VLEN=256, 4×8×4
  tiles, its measured figures) and the X100 core (RVV VLEN=256) are
  different targets and do not extend to A100 (F038). FP8 (E4M3/E5M2)
  conversion instructions are documented only in the Preview, are unprobed,
  and the corpus excludes fp8 — not on the current input path (F036).
- **Measured availability.** Under the declared endpoint, IME int8, int4 and
  fp16 probes are EXECUTED_AND_COMPARED_PASS with counted dynamic
  `smt.vmadot`/`smt.vfwmadot` executions (F034).
- **What the input path actually needs.** Corpus dtypes are bfloat16, bool,
  float16, float32, int16, int32, int64, int8 (no fp8/int4/fp64), so the
  applicable IME families are INT8 8×16×8 and FP16/BF16 8×8×8 — the BF16
  family currently blocked by the emulator gap, with the ordinary RVV path
  preserving BF16 correctness (F037).

## toolchain

(TGT-TOOLCHAIN-AND-BUILD-PATH question list; facts F042–F044.)

- **Build path stages.** `Triton operator + target description → this
  compiler (semantics, dependency analysis, work partition, vector/matrix
  lowering, instruction selection, allocation, stages, program-level
  assembly) → declared assembler + linker + precompiled C/C++ runtime and
  system libraries → standalone native executable → QEMU now; A100 board
  after porting` (chip.md#2). Probed end to end with a hand-written minimal
  artifact independent of the compiler (F042): `as` → `ld` → static ELF →
  QEMU execution with the guest exit code preserved — the path exists and
  works before the compiler does.
- **Artifact form per stage.** The compiler emits **program-level assembly
  text** (`.S`, rv64gcv, `smt.` mnemonics accepted by the cross assembler —
  proven by the matrix probe build); the assembler consumes it and produces
  ELF objects; the linker (with the sysroot's libc for the C runtime, static
  or dynamic — the lp64d loader is present) produces the standalone ELF64
  executable; QEMU executes the ELF with
  `-cpu max,vlen=1024,elen=64,vext_spec=v1.0`; `objdump` disassembles for
  inspection (F042). The compiler owns the complete single-operator program
  (entry/argument binding, worker range loops, stages, constants, workspace)
  — no per-operator C wrapper; a generated high-level translation unit
  replacing this compiler's lowering is not allowed; programs are cached by
  every bound source, target, option, grid/launch and argument-layout
  dependency (F043).
- **Tool versions.** Cross gcc 14.3.0 (`riscv64-unknown-linux-gnu-gcc`);
  GNU Binutils 2.43.1.20250119 (`as`/`ld`/`objdump`); qemu-riscv64 10.0.2
  (jdsk-qemu-10.0.2); sysroot with libc.so.6 + lp64d loader (F042;
  TOOLCHAIN_PROBES.json `tools`).
- **Absences.** The SpacemiT LLVM package is present but **unusable** on
  this host (GLIBC_2.36/2.38 missing, no clang) and is **not on the declared
  build path**; no tool outside the declared assembler/linker/sysroot/
  runtime may appear in code generation; the vendor reference stack
  (spine-triton CPUDriver/SMT pipeline, OpenBLAS/SLEEF, ONNXRuntime EP) is
  reference material this compiler may not call for its lowering (F044).

## abi

(TGT-TOOLCHAIN-AND-BUILD-PATH calling-side question list; facts F045–F046.)

- **Argument passing.** lp64d (double-precision hard-float) ABI with
  rv64gcv; the sysroot libc, dynamic loader and precompiled C runtime are
  lp64d; generated assembly calling the C runtime must follow the RISC-V
  psABI register conventions (integer args a0–a7, FP args fa0–fa7,
  callee-saved rules), and any internal helper-call convention the compiler
  defines must be declared once and shared by emitter and runtime (F045).
  At the transport boundary, arguments reach the program through the
  pack/unpack **bundle layout with guest pointer relocation** (strided-alias
  case probed PASS) (F046/F047).
- **Return and result path.** Results are written to the output buffers the
  bundle names and read back by the host with per-dtype decoding (bfloat16
  value storage probed PASS); the process exit code is the program's status
  and is preserved exactly through QEMU (F046, F047).
- **Entry point form.** The generated standalone executable owns entry and
  argument binding in native code; both probed forms work — a raw-syscall
  `_start` with no libc (exit code preserved) and the libc-backed `main`
  form via cross gcc (F046).

## runtime

(TGT-EXECUTION-RESOURCES launch side; facts F047–F050.)

- **Load path.** The artifact is a standalone native ELF run as
  `./operator_exec` (or via `a100_support/run-riscv.sh` under the declared
  QEMU endpoint with `-L sysroot`); the native transport
  (`native_io.pack_case` → guest `native_bundle` io_fixture →
  `unpack_outputs`) is probed end to end; `native_device.make_device`
  refuses until `A100_COMPILER_FACTORY` is set — no reference fallback for
  candidate execution (F047). A containerized no-Python execution image
  exists for candidate runs (image present; round trip to be exercised with
  the first real artifact — A002).
- **Launch and geometry.** The launch geometry (grid of program instances)
  is runtime information the generated program reads (range loops); the
  compiler generates worker range loops and program-ID calculation in native
  code, repartitioning from the source grid when semantics permit (F043,
  F018). Degenerate cases — zero work, sizes not divisible by the block
  extent (RVV masked tails), size one — are correctness requirements of the
  corpus cases (tails exercised by the masked reference probe, F049/F013).
- **Argument marshalling.** The bundle contract with guest pointer
  relocation is the single declared layout both sides derive from (F046,
  F047); the per-argument layout the emitter generates must agree with the
  runtime's marshalling (a declared single contract, not two assumptions).
- **Result readback.** `unpack_outputs` reconstructs each output with its
  declared type/shape (bf16 value-storage decoding probed) and the host
  compares against the case reference (F047).
- **Error reporting.** Guest exit codes are preserved (42 in the asm smoke);
  probes report JSON status (`passed`, `vlenb`, `mcpm_control` fields); a
  command that does not return is a recorded failure, never a pass
  (project execution rule; F042/F047 evidence).
- **Execution evidence requirement.** `Required execution evidence:
  resources`: representative multi-worker cases must distribute useful work
  and applicable matrix cases must execute real IME instructions, bound to
  the same prepared run, case and artifact via the QEMU instruction-count
  plugin (smt.* executions counted; zero-count control) — a listing or idle
  pool alone is insufficient (F048, F050).
- **Reference service.** The compiled x86 Triton CPU environment (triton
  3.8.0, single thread, IEEE fp32) validates questions independently and
  never substitutes for candidate target execution (F049).

## constraints

(TGT-MEMORY-MODEL + TGT-RESOURCE-BUDGET + TGT-NUMERIC-BEHAVIOUR; facts
F051–F056.)

- **Declared limits.** At most 8 A100 compute workers (1/2/4/8 configurable);
  the IME-2.0 engine shared by two cores (thread count ≠ matrix-engine
  count); 1.5 MB scratchpad + 1 MB L2 per cluster (shared budgets — never
  assume the whole scratchpad is privately available to every worker);
  fixed tile shapes per instruction family (λ fixed, not vtype-configurable);
  IME LMUL=1 only; MUL_C fixed per profile (F053, F030, F040).
- **Numeric behaviour.** Integer matrix paths accumulate within the 32-bit
  destination bit width (modular wrap) with the accumulator always signed;
  signedness variants u/us/su select operand interpretation; the fp path
  takes FP16/BF16 inputs, accumulates in FP32, produces FP32, with MCPM.BF16
  selecting the 16-bit format (0=FP16, 1=BF16); no mixed-format inputs (F051).
  The FMA contraction/rounding point of `smt.vfwmadot` is unspecified —
  covered by the case tolerance, never by an exactness claim (A005).
  Standard RISC-V integer semantics (overflow, div-by-zero, shift masking)
  and RVV FP rounding follow RVA23/RVV-1.0 compliance (assumption A003).
  Corpus contract: **integer, index and boolean outputs are exact; floating
  results stay within each case's original tolerance; references and
  tolerances are never modified to pass; the reference computes fp32 dot in
  IEEE mode** (F052). Denormal/special-value handling is not separately
  stated in the pack beyond the IEEE binary16/binary32/bfloat16 format
  declarations — the case tolerance governs (F051, F052).
- **What is refused.** IME illegal conditions (LMUL≠1, odd vd, overlap,
  format mismatch) raise illegal instructions — the compiler must refuse or
  prevent them before emission, and constructs outside the declared
  repertoire must be refused with a located diagnostic, never approximated
  (F033); the BF16 IME format-control gap stays unverified — never claim
  BF16 IME execution from FP16/vector success (F034); the MCPM CSR is not
  userspace-accessible under the pinned QEMU (F034); TCM/DMA/spinlock use
  is refused until interfaces are verified (A007); no operator-name
  dispatch, precomputed answers or reference fallback in the compiler
  (F052); performance anchors, timings and speedups are neither recorded
  nor required (F055 — correctness_only).
- **Performance-qualified specifications (not anchors).** The advertised
  60 TOPS is the INT4 **sparse** headline (INT4 30 dense, INT8 15 dense,
  BF16/FP16 7.5, FP8 7.5 per the Preview table) — a documented qualifier,
  explicitly not a measured target for arbitrary kernels, and unusable as a
  bound for floating or dense operators (F036, F053). No achievable rate,
  launch floor or noise figure is recorded: none is required under
  correctness_only (F055).

## Contradictions and reconciliation (acceptance[5])

No contradiction affecting code generation was found. Three documentation
framing differences were identified, reported (not averaged), and resolved by
applicability:

1. **IME λ parameter, figure captions vs tables.** The `ime_extension.md`
   tables (2.1.2, arithmetic-consistent with the program-visible semantics:
   K=λ×W×LMUL) state λ=4 for the FP16/BF16→FP32 family, while the Figure 8
   caption says λ=8. The operative contract — tile shapes 8×8×8 (stated
   identically in 2.5, 6.1.2 and Appendix A), MUL_C, register constraints —
   is consistent everywhere; the λ mismatch is a figure-caption
   documentation error with no codegen consequence (the compiler consumes
   tile shapes and constraints, not λ).
2. **X100 L2 framing.** The K3 brief says "8 MB shared L2 per 8-core
   cluster" while the CPU manual/datasheet/Preview say 4 MB L2 per cluster
   with 2 X100 clusters (2×4 MB). X100 is not the codegen target; recorded
   as an X100-side framing difference between brief and manual.
3. **A100 cluster composition, Preview vs production docs.** The Preview
   (2026-01-29) describes each A100 cluster as 4 scalar + 2 vector cores
   with the tensor core shared by two cores; production docs summarize "8
   A100 cores" and the vendor runtime maps a cluster to 4 A100 Linux
   threads (8 total, core IDs 8–15 in examples). These are different
   abstraction levels of the same 8-hart/2-cluster topology; the Preview is
   explicitly a preview to be reconciled with production hardware, which is
   assumption A008 (board verification) — it affects placement/resource
   sharing, not instruction semantics.

The English and Chinese editions of the IME v0.6 specification agree (verified
on the sub-extension, constraint and tile sections).

## Conditional design guidance (not facts)

Premise/benefit/cost, per the chip-analysis discipline; adopting any of these
requires a Decision with the measurement or probe that justified it.

- **Premise:** enough mutually non-overlapping output tiles exist. **Benefit:**
  simpler synchronization and multi-core scaling. **Cost:** imbalance and
  shared-resource contention need verification. (TARGET_SUMMARY guidance.)
- **Premise:** packing cost is amortized by compute volume or weight reuse.
  **Benefit:** use of the matrix extension. **Cost:** extra storage, packing
  and tail handling; ordinary and matrix paths must each be verified.
  (TARGET_SUMMARY guidance.)
- **Premise:** local-storage and transfer interfaces (TCM/DMA) and their
  visibility are verified. **Benefit:** reuse and overlap. **Cost:** capacity,
  synchronization, resource occupancy — do not assume availability while the
  facts are missing (A007). (TARGET_SUMMARY guidance.)
- **Premise:** a kernel's live set is well under the 4 KB vector file.
  **Benefit:** with VLEN=1024, LMUL=1 gives 1024-bit compute width and
  reduces vector-register spill likelihood (Preview 5.2.2). **Cost:** none
  when the premise holds; pressure-tracking remains the allocator's job
  (F041).
- **Premise:** representative steady-state measurements exist. **Benefit:**
  execution-setting selection (thread count, tiling) by measured time.
  **Cost:** none under correctness_only — this guidance is inert for this
  project's scope (A100-OPERATOR-TIMING applies only when performance is in
  scope).

## Open questions and assumptions

All properties the input compilation path needs are answered from the
material, measured, or recorded as assumptions with validation methods —
nothing silently defaulted. The open assumptions (beyond environment-phase
A001/A002):

| id | open question | validation method | risk |
|---|---|---|---|
| A003 | Standard RISC-V integer semantics (overflow/div-by-zero/shift) and RVV FP rounding via RVA23 compliance | bounded QEMU probes (div-by-zero, overwide shift, wrap, frm); on-board re-check | low |
| A004 | Misaligned/out-of-range access behaviour not stated | bounded misaligned-access probe under QEMU; keep aligned+masked-tail codegen | medium |
| A005 | `smt.vfwmadot` FMA contraction/rounding point unspecified | differential comparison vs fp32 reference if a case demands; otherwise tolerance-covered | low |
| A006 | Formal cross-hart memory model not stated (per-level coherence is) | on-board ordering probes at porting; explicit pthread/atomic sync meanwhile | medium |
| A007 | TCM/DMA/spinlock software interfaces unverified; not on QEMU userspace path | SDK sources + on-board probes before any use | high |
| A008 | Production matrix-engine pairing and allowed core set unverified on hardware | on-board discovery at porting (extends A001) | high |

None of these blocks the plan: the correctness path under the pinned QEMU
endpoint (userspace Linux, RVV + int8/fp16 IME, pthread pool, bundle
transport) is fully covered by recorded facts and probes; every open item has
a named validation method and an owner (the board porting step or a specific
probe).

No fact with UNKNOWN confidence is recorded, and no performance anchor,
timing or speedup is recorded or required (correctness_only).
