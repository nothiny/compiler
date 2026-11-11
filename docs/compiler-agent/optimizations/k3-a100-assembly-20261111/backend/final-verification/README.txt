Final bounded component verification: source commit 51f3c61

Read SEMANTIC_SUMMARY.json for the final classifications. RESULTS.json retains
the first run including the missing-plugin failure and its mechanical exit-only
labels; its stage-barrier witness PASS label does not mean that the mutant
failed. SUPPLEMENTAL_RESULTS.json records the actual fixture retry, final MIR
and spill tests, and one actual baseline barrier execution.

Execution used /tmp/a100-final-suites-vj2_9v9h, a private hard copy of the final
source. PYTHONPATH and per-command imports were pinned to that copy. No shared
candidate cache or runtime build directory was used. Commands had bounded
timeouts and process-group termination. The final 183-file SHA comparison
matches the parent snapshot, including compiler, adapters and tools.

22 standalone commands exited zero after the counter fixture was supplied and
matrix_breadth was rerun. Its 14/14 actual dot forms and dynamic IME checks pass;
two internal census shape/comparator errors remain in the log and are not
passed cases. The full original-input runner determines those cases separately.

Required no-name dispatch: normal zero, actual injected name branch caught.
Numeric comparison policy: normal zero, actual widened tolerance caught.
Masked-tail advisory: real artifact correct; mutant corrupts poisoned guard;
CLI returns zero, contrary to the declared witness-exit protocol.
Stage-barrier advisory: normal 1/2/4/8 workers, 16 repeats each, are correct;
mutant still correct, so the witness is VACUOUS / unproven. The unchanged
c8ade47 baseline reproduces it. No synchronization redesign was attempted.

PLUGIN_FIXTURE.json records the prepared plugin's SHA and private copy; no
binary is committed here. BARRIER_BASELINE_FIXTURE.json records the original
script and its source commit. The first baseline setup error (the old source
copy omitted that tool) is retained in stage-barrier-baseline-setup.log; no test
ran during that setup failure. The subsequent log is the one actual baseline
witness execution. The completed matrix/MIR/spill commands were not repeated
when resuming that last fixture step.

All logs are real standalone-script runs, not unittest discovery. Native test
summaries retain artifact SHAs and commands. This component record does not
claim completion of the independent full 2734-case scan, an engine gate or
hardware performance.
