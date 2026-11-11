# Independent validation and replay

The production candidate is Git `51f3c61`, compiler source digest
`92fa8b4b706f0a76`. Its frozen root is
`/tmp/a100-k3-final-frozen-xg9tlcpp`; `FINAL_SOURCE_SNAPSHOT.json` records the
complete copied source/tool inputs. The baseline is Git `c8ade47`, frozen at
`/tmp/a100-k3-baseline-review-gcdf_716`. Corpus sources and original comparison
policies are unchanged. These are direct human-guided observations, not engine
gate records or hardware timing claims.

## Paired profiles

`FINAL_PAIRED_METRICS.json` and `.csv` contain 21 matched cases: 15 original
shape/dtype samples and six larger generated shapes, always seed 30 and one
compute worker. The 14 core cases also retain the intermediate phase-1 column;
its zero-gain FP16/GELU/sigmoid measurements were not overwritten.

Each revision/case has two independent repeat-difference pairs, four native
launches. Every launch passes the original case comparator and repeat-consistency
check. Reassembled program bytes, actual instruction starts, ELF SHA and final
module import/source identities are checked. The main number is dynamic guest
instructions in the generated program symbol region. Whole-process and
outside-program counts are separate fields; no ratio is a board speedup.

To repeat the final measurement without skipping native execution, choose a
fresh output directory and use the frozen root:

```bash
A100_REVIEW_ROOT=/tmp/a100-k3-final-frozen-xg9tlcpp \
python3 -B docs/compiler-agent/optimizations/k3-a100-assembly-20261111/validation/profile_final_v1.py \
  --cases docs/compiler-agent/optimizations/k3-a100-assembly-20261111/validation/PROFILE_FINAL_CASES.json \
  --threads 1 --pairs 2 --repeat-delta 1 --case-timeout 600 \
  --max-wall 2200 --out /tmp/a100-final-profile-replay
```

The adapter is revision-bound evidence, not an assertion that another compiler
revision is the same candidate. Check the recorded source hashes and resolved
options before comparing another run. Its only compiler instrumentation adds
MIR identities to assembly comments and a diagnostic cache tag; it imports no
optimization prototypes.

`METRICS_RAW_TEXT_EVIDENCE.tar.gz` is a compact durable archive of the original
counter JSON, compare/repeat logs, generated program/MIR text and disassembly for
baseline, phase 1 and final profiles. `METRICS_RAW_TEXT_EVIDENCE.json` gives the
archive hash and every member's size/SHA. It excludes input/output bundles, ELF
binaries and object files. The original unpacked records remain in this directory.

## Complete original-input regression

The existing `tools/run_scan.py` is copied as a real file; it is not edited.
`sharded_regression_v1.py prepare` enumerates the original full manifest and
assigns each complete operator to exactly one of four shards. Each shard has a
fresh artifact/runtime-build cache. `scan_entry_v1.py` calls the unchanged runner
and asserts actual compiler/support imports stay inside the frozen root,
including lazily loaded helpers after compilation. Logical runner argv, actual
launcher argv/digest and all input/source hashes are retained.

The prepared run is `full-input-final/plan.json`. Raw reports, journals, process
logs and import bindings are under `full-input-final/shard-{0,1,2,3}/`. Its 600s
native timeout gives a separate 905s staging deadline. Any timeout remains a
failed row; it does not become a skipped PASS. Both historical deconv timeouts
remain included. Historical exact-case timings/cache states are in
`HISTORICAL_LONG_CASES.json`; timing attribution requires matched conditions.

After all shards actually finish, merge with:

```bash
python3 -B docs/compiler-agent/optimizations/k3-a100-assembly-20261111/validation/sharded_regression_v1.py \
  merge --plan docs/compiler-agent/optimizations/k3-a100-assembly-20261111/validation/full-input-final/plan.json
```

The merge rejects partial reports, omissions, duplicate/extra IDs, changed case
metadata, invalid PASS stage flags, changed frozen sources or missing real import
bindings. It retains all raw per-shard reports and resource evidence. Runner
sharding is host validation concurrency; actual multi-worker operator evidence
comes only from native resource/semantic executions.

`FINAL_RESOURCE_PLUGIN_FIXTURE.json` records the exact prepared QEMU plugin copied
into the frozen root. No compiler source changed for this fixture. The runner can
also rebuild a missing plugin from its copied source. Independent standalone
test fixture failures and advisory witness limitations are retained by the backend
owner; a missing fixture or a vacuous witness is never counted as a native pass.
