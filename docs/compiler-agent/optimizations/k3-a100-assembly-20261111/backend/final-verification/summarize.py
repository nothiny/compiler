#!/usr/bin/env python3
"""Interpret executed checks, preserving initial errors and witness semantics."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

OUT = Path(__file__).resolve().parent
initial = json.loads((OUT / "RESULTS.json").read_text())
extra = json.loads((OUT / "SUPPLEMENTAL_RESULTS.json").read_text())
snapshot = json.loads((OUT / "SNAPSHOT.json").read_text())
root = Path(snapshot["root"])
assert not initial["partial"] and not extra["partial"]
rows = {row["label"]: row for row in initial["results"]}
extras = {row["label"]: row for row in extra["results"]}
standalone = [row for name, row in rows.items()
              if name.startswith("test_") and name != "test_matrix_breadth"]
standalone.extend(extras[name] for name in (
    "matrix_breadth-fixture-retry", "mir_verifier-final", "t029_spill-final"))
assert len(standalone) == 22
assert all(row["actual_exit"] == 0 and not row["timeout"] for row in standalone)
log = lambda label: (OUT / (label + ".log")).read_text()
normal = [name for name in rows if name.startswith("check_") and not name.endswith("-witness")]
assert all(rows[name]["actual_exit"] == 0 for name in normal)
name_caught = rows["check_no_name_dispatch-witness"]["actual_exit"] == 1 and \
    "branch on corpus name 'matmul'" in log("check_no_name_dispatch-witness")
policy_caught = rows["check_numeric_policy-witness"]["actual_exit"] == 1 and \
    "widened tolerance" in log("check_numeric_policy-witness") and \
    "CAUGHT" in log("check_numeric_policy-witness")
assert name_caught and policy_caught
masked_observed = "tail lanes corrupted the guard region" in log("check_masked_tails-witness")
stage_vacuous = "produced correct results across all repeats" in log("check_stage_barriers-witness")
baseline_vacuous = "produced correct results across all repeats" in log("stage-barrier-baseline")
assert masked_observed and stage_vacuous and baseline_vacuous

parent_path = OUT.parent.parent / "validation/FINAL_SOURCE_SNAPSHOT.json"
parent = json.loads(parent_path.read_text())
changed = [name for name, expected in parent["files"].items()
           if not (root / name).is_file() or
           hashlib.sha256((root / name).read_bytes()).hexdigest() != expected]
assert not changed, changed
for name, destination in (("native-state-evidence/summary.json", "native-state-summary.json"),
                           ("guard-evidence.json", "guard-native-checks.json"),
                           ("options-evidence.json", "options-native-checks.json")):
    if (root / name).is_file():
        shutil.copy2(root / name, OUT / destination)
first_log = log("test_matrix_breadth")
for line in first_log.splitlines():
    if line.startswith("# evidence: "):
        source = Path(line.split(": ", 1)[1])
        if source.is_file():
            shutil.copy2(source, OUT / "matrix_breadth-initial-native-evidence.json")
census_diagnostics = [line.strip() for line in log("matrix_breadth-fixture-retry").splitlines()
                      if "RUN-ERROR ValueError" in line]
assert len(census_diagnostics) == 2
result = {
    "completed_utc": datetime.now(timezone.utc).isoformat(),
    "git_source_revision": snapshot["git_revision"], "verification_root": str(root),
    "standalone_commands_exit_zero": len(standalone),
    "standalone_commands": [{key: row[key] for key in (
        "label", "actual_exit", "pass_lines", "log", "test_source_sha256")}
        for row in standalone],
    "normal_behaviour_commands_exit_zero": normal,
    "required_no_name_dispatch_witness_caught_actual_name_branch": name_caught,
    "numeric_policy_witness_caught_actual_tolerance_widening": policy_caught,
    "advisory_witnesses": {
        "masked_tail": {"status": "MUTANT_FAILURE_OBSERVED_CLI_PROTOCOL_MISMATCH",
                        "actual_exit": rows["check_masked_tails-witness"]["actual_exit"],
                        "mutant_corrupted_poisoned_guard": masked_observed},
        "stage_barrier": {"status": "VACUOUS_NOT_PROVEN",
                          "actual_exit": rows["check_stage_barriers-witness"]["actual_exit"],
                          "normal_threads": [1, 2, 4, 8], "normal_repeats": 16,
                          "baseline_c8ade47_same_vacuity": baseline_vacuous}},
    "initial_matrix_fixture_failure": "All 14 executed form comparisons passed; five dynamic-resource checks lacked the plugin. Retained in RESULTS.json/test_matrix_breadth.log and rerun without source changes after SHA-bound private fixture copy.",
    "matrix_internal_census_diagnostics_not_passed_cases": census_diagnostics,
    "parent_snapshot_files_checked": len(parent["files"]),
    "source_changes": changed,
    "classification_note": "RESULTS.json is the raw first-run exit-only view; its stage-barrier witness PASS label is superseded by this semantic VACUOUS classification. Its overall false retains the initial missing-plugin failure.",
    "scope": "Bounded component/behaviour verification only; full 2734-case regression belongs to the independent final scanner. No engine gate or hardware performance claim.",
}
(OUT / "SEMANTIC_SUMMARY.json").write_text(json.dumps(result, indent=2))
print(json.dumps({"standalone_commands_exit_zero": len(standalone),
                  "source_files_checked": len(parent["files"]),
                  "source_changes": changed, "advisory_witnesses": result["advisory_witnesses"]}))
