# Backend state, spill and cache increment

This component preserves the existing MIR operations and pipeline. It changes
vector stack transfers to constraint-checked RVV whole-register instructions,
retaining all group bytes at LMUL 1/2/4/8 without changing VL/VTYPE. Runtime AVL
no longer causes the old spill refusal. The mask-spill refusal remains explicit.
The textual vector-state peephole invalidates state across both other setters;
neither emitter-level nor textual elimination discards an observable VL-result
write. Tail/mask policies participate in configuration identity.

The complete-program revision discovers all production Python sources and native
runtime source/header inputs, pruning generated directories before traversal.
Program identity also binds native build flags, actual gcc/as/ld binaries,
resolved sysroot and the SDK lock. Runtime object identities bind local runtime
headers, compiler binary and SDK lock as well. This assumes the declared locked
SDK/sysroot installation is not modified in place independently of its lock;
arbitrary system-header mutation is not monitored. A new header or production
module is discovered without editing another dependency list.

`APPLICABILITY.md` records the source-to-destination map. `verification.json`
separates the bounded component checks from the subsequently required full scan.
The raw 15 all-byte/VL/VTYPE/GPR-preservation native witnesses and their exact
assembly are under `native-state/`. The header mutation test executes old native
code with usage exit 2, then both reused-cache and clean-build programs with the
new declared exit 42; it also proves SDK-lock changes rebuild all three C
objects. Both compile entry points forward all three coordinated lowering
switches: eight distinct compiled cache entries and sixteen original-reference
comparisons at 1/8 threads pass. `option-identity.json` preserves those rows.

The actual backend-only paired profiles are deliberately a zero-gain result:
FP16 matmul 128^3 remains 7,438,232 guest program instructions and GELU 262144
remains 1,990,955, identically in both repeat-difference pairs. These samples
have only scalar spills or no spills. `metrics-summary.json` links the unchanged
baseline, exact candidate artifacts and raw records. The component is retained
for vector-spill correctness, dynamic-AVL support and reliable evidence/cache
identity; it is not presented as a measured performance improvement. Scalar
spill traffic and immediate selection are separate opportunities, not part of
this commit. There is no new engine optimization phase or G9 assertion.

Final component verification at source commit `51f3c61` is recorded under
`final-verification/`; use `SEMANTIC_SUMMARY.json` for the interpreted result,
and retain `RESULTS.json` as the initial exit-only history. Twenty-two explicit
standalone commands completed with exit zero against a private hard copy,
including the affected lowering/backend/build/cache suites, the new native
tests, MIR rejection checks and T029 spill regressions. All 183 parent-snapshot
files still match their recorded SHA256s. The matrix breadth suite's first
attempt lacked its fixed-location prepared counter plugin; the same-SHA plugin
was copied only into the private verification root and the suite was actually
rerun, passing 24 checks including its dynamic IME observations. Both attempts
are retained. Its two internal census shape/comparator errors remain explicit
diagnostics and are not counted as passed cases; the full corpus scanner owns
their original-case comparisons.

The no-name normal check passes and its witness actually catches the injected
name branch/file literal; the numeric-policy witness actually catches widened
tolerance. Normal masked-tail and stage-barrier checks pass, including 16
repeats at each 1/2/4/8 worker count for the latter. Their advisory limitations
remain: the masked-tail mutant corrupts the guard but the CLI returns zero;
the stage-barrier mutant remains correct, so this witness is vacuous despite
returning one. One actual c8ade47 baseline execution of the identical barrier
script reproduces that vacuity. This is not recorded as a successful witness
or a new output regression. No production source, corpus, harness, engine
policy or reference was changed by this final verification task.
