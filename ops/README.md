# ops — the development corpus for this project

The compiler consumes **exactly these two directories**:

```
ops/
  suite/manifest.json     machine-readable list of all 500 operators
                          (path / family / semantic features / interactions /
                           case count / provenance)
  suite/dev/              400 correctness operators — semantic sizes
                          (axes <= 128; 18 verified overrides keep a keyed or
                          power-of-two upstream shape); the correctness lane runs these
  suite/perf/             100 performance operators — semantic correctness cases;
                          steady-state timing shapes are resolved from
                          suite/perf/workload.json by the performance lane
  suite/heldout.json      500 held-out pool operators by origin (maintenance branch
                          only; the release package does not contain it)
  suite/*/provenance.json origin path + sha256 of every file (drift detector)
  docs/SUBSET.md          the declared inference subset: five principles,
                          included/excluded constructs
  docs/SUITE_V3.md        how the suite was selected, before/after per family,
                          coverage, validation status, dev/holdout protocol
  docs/SUITE_V2.md        the previous (target-independent) suite, kept as history
  docs/COVERAGE_MATRIX.md operator x semantic-feature table
  docs/API_INVENTORY.md   every tl.* construct used (generated)
  docs/CORPUS_USAGE.md    short form of the corpus section of KICKOFF.md
  harness/                the runner — NOT operators
    compiler_api/         Device protocol, run_cases.py, gate.py, identity.py,
                          RUNBOOK.md (how to compile cheaply),
                          COMPILE_CONTRACT.md (adapter protocol)
    benchmark/            run.py (timing), report.py, size.py
    opslib/               shared implementation
```

500 operators / 2734 cases (dev 400 / 2192, perf 100 / 542); 2161 compile
identities (cases/identity = 1.26).  The declared subset is forward-only:
no gradient kernels, no fp8, and no `input_precision=`/`allow_tf32=` — fp32
`tl.dot` is IEEE, pinned by `TRITON_F32_DEFAULT=ieee` in the runner.  The
floating cases exercise the inference dtypes `float32` / `float16` /
`bfloat16`; bf16 is the primary perf-lane dtype.

Do not modify operator files (`SHAPES`, `DTYPES`, `ref`, `make_case`) or the
harness to make a check pass.  The upstream selection pool and the corpus
self-tests are **not shipped in this image**; this directory is self-contained.

Everything is enumerated from the same contract:

```bash
python3 harness/compiler_api/run_cases.py --manifest suite/manifest.json --dry-run --identities
```
