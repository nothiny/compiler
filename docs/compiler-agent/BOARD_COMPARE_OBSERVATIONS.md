# Board-comparison observations (out-of-corpus, hidden-set)

Provenance: user-run board comparison (workspace `/home/i_yinzida/board-compare-001`,
54-case suite a100c vs triton-riscv on the real board, with QEMU reproduction),
reported to the manager on 2026-11-11. Facts below marked *verified* were re-derived
read-only by the audit manager on 2026-11-11 from that workspace and this project's
own records; no build or execution commands were run by the manager.

These are hidden-set / extra-capability observations. They cannot enlarge the input
completion contract (ops/ corpus, `correctness_only`); a finding that also breaks the
input contract must be repaired, and the in-corpus instance of each class is named
below.

## 1. aminmax_kernel_2 fp64 8-worker merge loss (a100c defect, out-of-corpus trigger)

User-observed symptom (QEMU-reproducible):

- `aminmax_kernel_2`, case label `262144.float32`. 1 worker: PASS on both sides.
- 8 workers: a100c MISMATCH — `max_out` and `min_out` each wrong in their single
  scalar element (max_abs 3.00 / 3.75); triton PASS.

Verified facts:

- The kernel is not in the input corpus: `ops/` contains no aminmax source and the
  full scan report (docs/compiler-agent/SCAN_T019/run/report.json, 2734 cases) has
  zero aminmax rows.
- case.json (board workspace): two independent input buffers `min_inp`/`max_inp`
  [2048] fp64, scalar outputs `min_out`/`max_out` [1] fp64, grid 1x1x1, signature
  `mid_size: i32`, `BLOCK_MID: constexpr`.
- fp64 is outside the corpus dtype surface (F037; scan dtype census: float32 957,
  float16 850, bfloat16 849, bool/int8/int16/int32/int64 only — no float64).
- The corpus-wide scan executed 2732/2734 cases at threads=1 (2 cases at threads=4);
  multi-worker coverage is the separate worker-count / resource-evidence sweep.
- Latest result.json on disk (2026-11-11 12:34) is the 1-thread PASS run; the
  8-thread failing outputs were overwritten (user noted; the bundle must be rebuilt
  for reproduction).

Classification: same defect family as T050 acceptance item (2) —
`grouped_mm_kernel [4,67,35,29]#bfloat16` 8-thread race-shaped intermittency
(PASS at 1 thread, MISMATCH on 3 of extra bounded repetitions at 8) — i.e. a
multi-worker merge ordering / synchronization defect in the shared path. Both
independent output slots (min and max) losing their partial at once points at the
shared merge mechanism (merge-frame slots, barrier ordering or combine scheduling)
rather than a single boundary off-by-one. The fp16/bf16 reduction SIGILL class seen
in the worker-count findings was a different, already-repaired defect (T042).

Manager disposition:

- No new task while T044 is in flight (`await_repairs`); T050 already owns the
  in-corpus instance of this class. Round-1 post-scan-repair budget has 1 task slot
  remaining; round 2 (up to 10) is available.
- When T050 dispatches, this file is handed to the worker as context: the
  shared-path fix is accepted on the grouped_mm corpus case (deterministic PASS at
  8 threads across repeated bounded runs); the aminmax repro below is an additional
  robustness check for the same shared path, NOT an acceptance criterion (its
  trigger dtype fp64 and its kernel are outside the input scope). If the root cause
  proves fp64-specific, record it as an out-of-surface limitation; do not expand the
  input contract.

Reproduction (user-provided, QEMU; bundle must be rebuilt because the 1-thread run
overwrote the outputs):

```bash
set -a; . ./.env; set +a
cd /home/i_yinzida/board-compare-001/work/cases/aminmax_kernel_2/262144.float32

# 1 worker (PASS)
python3 ../../../build_case_a100c.py aminmax_kernel_2 '[262144]' float32 .
timeout 120 $A100_QEMU -L $A100_SYSROOT -cpu $A100_QEMU_CPU \
  a100c/operator_exec_time --bundle a100c/bundle.bin --threads 1 --warmup 0 --repeats 1

# 8 workers (MISMATCH)
cp a100c/bundle.bin /tmp/b8.bin; cp a100c/bundle.json /tmp/b8.json
timeout 120 $A100_QEMU -L $A100_SYSROOT -cpu $A100_QEMU_CPU \
  a100c/operator_exec_time --bundle /tmp/b8.bin --threads 8 --warmup 0 --repeats 1

# compare against golden (see user's np.ndarray view-extraction snippet over
# a100c/bundle.json views/storages for max_out/min_out)
```

Worker hypotheses (user + manager; advisory, to be confirmed against the pipeline):
- `a100c/plan/stages.py` — merge-frame construction / identity propagation for
  dual-output scalar reductions under a repartitioned persistent loop (grid=1).
- `a100c/plan/partition.py` — partition-boundary computation for the split range.
- `a100c/runtime/pool.c` — stage-barrier / merge scheduling versus worker
  completion.

## 2. softmax_single_block board variant — triton-riscv missing output (NOT an a100c defect)

Verified facts:

- Corpus variant `suite/dev/softmax_single_block_forward_kernel.py` (shapes
  [1,17]/[20,17], fp32/fp16/bf16): all 6 cases PASS at threads=1 in the full scan.
- Board variant `softmax_single_block_forward_kernel_958a244559a0d001` [512,4096]
  float32 is a different source identity and an out-of-corpus shape. a100c PASS;
  triton-riscv produced no output (`Y_ptr: MISSING`).

Disposition: no a100c change. Annotate the board-comparison report as a
triton-riscv-side failure. Candidate causes to diagnose on the triton side if
pursued (user's list): runtime crash / SIGILL of the large-BLOCK ELF on the board,
a silently ignored llc error, or an output-buffer allocation failure.

## 3. User status update (2026-11-11 afternoon)

The user cancelled the T050 repair dispatch (WTI051 spawn cancelled before launch;
invocation closed via reconcile-running, T050 back to READY) and states no operator
errors remain. Verified at that moment: no fresh rerun artifact exists in the board
workspace after 12:40 (last on-disk result for aminmax is the 1-thread PASS at
12:34); the reported 8-thread MISMATCH (~12:00) was observed on the current tree
(post 09:02-09:25 fixes) and no relevant code change has landed since. If the
8-thread case now passes, intermittency of the race-shaped merge defect is the
likely explanation and a single passing run does not establish the merge race is
gone.

Disposition (manager, 2026-11-11): the user did not further specify; per their
direction no repair or verification dispatch is outstanding and the engine is
quiescent (no open invocations; T044/T045-T050 remain READY and do not run by
themselves). The determinism question for the 8-thread merge class stays open:
5 repeated bounded 8-thread executions of the aminmax repro (and the corpus-side
grouped_mm case) would settle it — record any rerun outcome here when available.

## 4. fp16/fp32 MatMul ULP mismatches — no action

- 7 fp16 cases (K=512 accumulation): last-bit rounding differences from different
  accumulation orders across GPU Triton 3.8 (golden), board a100c and board
  triton-riscv; 1–2 fp16 ULP (0.015–0.031), bad fraction < 0.007%.
- 5 fp32 cases: same accumulation-order effect; a100c bitwise-matches golden on 3
  of them while triton-riscv deviates ~2–4 fp32 ULP; on the other 2 both deviate
  with identical bad counts (65/262144, max_abs ~6.9e-5).

Disposition: inherent floating-point behavior, not compiler defects. The binding
comparisons for this project remain each corpus case's declared policy; no change.
