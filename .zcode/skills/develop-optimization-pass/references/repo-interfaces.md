# Repo interfaces: commands that do the work

Environment first — every shell session:

```bash
cd /home/i_yinzida/compiler-a100-experiment-001
set -a; . ./.env; set +a
```

## Compile one case and inspect every stage

```python
import importlib.util
from a100c.factory import make_compiler
spec = importlib.util.spec_from_file_location("op", "ops/suite/perf/matmul.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
case = m.make_case(shape=(16,16,16), dtype="float16", seed=30)
art = make_compiler().compile_case(case)
print(art.executable)      # a100c/cache/<key>/operator_exec
```

The cache entry (`a100c/cache/<key>/`) holds `program.S` (full assembly, every
instruction annotated `[opN]` with its source location; peephole rewrites
appear as `[peephole-*]` comments), `stage.tir.txt`, `stage.passes.txt`
(per-pass fired/declined counters with refusal reasons), `stage.plan.txt`,
`stage.mir.lowered.txt` / `stage.mir.legalized.txt` / `stage.mir.allocated.txt`,
`stage.selection.txt`, `artifact.json` (identity, sha256, per-stage stats).
The cache key covers specialization identity + compiler revision + options +
argument layout + pass configuration; switches like `A100C_<NAME>=off` change
the key, so on/off artifacts never collide.

## Static census of emitted forms

Grep/scan `program.S` of freshly compiled cases (see the census pattern in the
branch-fuse round's evidence scripts). Always census artifacts you compiled
yourself from `ops/` (the inner ring) — cached entries may carry other
revisions or heldout provenance, which must never guide development.

## Correctness: run and compare

```bash
python3 tools/run_scan.py run --operator suite/dev/absolute_kernel.py            # one operator, all cases
python3 tools/run_scan.py run --operator <op> --threads 4                        # multi-worker
python3 tools/run_scan.py run --report <dir>/report.json --run-id <id> \
    --journal <dir>/journal.jsonl                          # full corpus, resumable
python3 tools/run_scan.py run --journal <dir>/journal.jsonl --resume            # resume
```

Statuses: `PASS` (executed + compared under the case's own policy),
`COMPILE_REFUSED`, `LAUNCH_FAIL`, `TIMEOUT`, `MISMATCH`, `CASE_FAIL`,
`EVIDENCE_FAIL`. Exit code 0 = the run completed (per-case failures are rows,
not exit failures). Numeric policy comes from the case; never widen it.

## The four witness checks (each `--witness` must exit nonzero)

```bash
python3 tools/check_no_name_dispatch.py [--witness]   # required: no name branching
python3 tools/check_numeric_policy.py   [--witness]
python3 tools/check_masked_tails.py     [--witness]
python3 tools/check_stage_barriers.py   [--witness]
```

## The proxy metric: guest dynamic instructions per call

```bash
python3 -B tools/profiling/collect_metrics.py --operator <op> --shape <s> \
    --dtype <dt> --threads 1 --out <evidence-dir>/<name>
```

Stages the case exactly like the scan, runs it twice under QEMU with the full
instruction-count plugin (`--repeats 1` and `--repeats 1+R`), differences to a
steady-state per-call profile, and joins per-pc counts with the compiler-side
manifest (origins: spill/reload/vec-config/memory/const/branch/...).
`metrics.json` → `steady_state.per_call_total` and `.per_call_categories`;
`asm_join` gives per-source-block attribution. Judge quantity: per-call guest
dynamic instructions; QEMU wall time is auxiliary only. The established paired
case set (attn, fd2, lindrop, matmul16, sm17, sm97, softmax, synth — exact
identities in the latest round's RECORD.md) makes before/after comparable.

Three-way comparison: baseline tree (or the recorded baseline numbers) vs
candidate-with-switch-off vs candidate-with-switch-on, same case identities.
The off side's `program.S` should be byte-identical to the baseline emission
for unchanged paths (the `asm_join` digest check).

## Tests

Each module in `a100c/tests/` is standalone runnable: `python3 a100c/tests/test_emit.py`.
Round tests live beside them (`test_local_materialization.py`,
`test_guarded_narrow_access.py`, `test_k3_lowering_optimizations.py`, ...).
Follow that pattern for a new round's tests; exercise positive rewrites,
refusals and the off-switch in one module.

## Records

One directory per round under `docs/compiler-agent/optimizations/`:
`RECORD.md` (goal/outcome, why, transformation & reuse contract — the seven
fields, validation & measurements, practices, migration recipe) is THE
deliverable the human reads; update `INDEX.md` with one row linking
transformation, IR/structure and outcome. Record format: the
optimization-record guide in the optimization skill's references. Failed
attempts keep their records; a later success links them, never overwrites.

**Logs, raw counter dumps, staged objects and archives never enter git**
(user directives 2026-11-16; `.gitignore` enforces the classes; two history
rewrites removed them retroactively — see
`docs/compiler-agent/GIT_HISTORY_REWRITE-2.json` for the commit map): the
round's RECORD.md plus the small structured summaries (metrics.json, scan
journals/report.jsons) are the record. `collect_metrics.py` writes raw
per-PC counter dumps (`counts.r*.json`) and a staged `asm/program.o` into
its `--out` directory — delete them (or gzip-and-keep-outside-git) after
reading; never `git add` them. A round that left any of these in the tree
did the bookkeeping wrong.
