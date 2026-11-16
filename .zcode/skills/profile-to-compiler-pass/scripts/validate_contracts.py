#!/usr/bin/env python3
"""Validate the three evidence contracts used by profile-to-compiler-pass."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


class ContractError(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"{path}: cannot read JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"{path}: top level must be an object")
    return value


def require(obj: dict[str, Any], fields: tuple[str, ...], where: str) -> None:
    object_at(obj, where)
    missing = [field for field in fields if field not in obj]
    if missing:
        raise ContractError(f"{where}: missing {', '.join(missing)}")


def object_at(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{where}: must be an object")
    return value


def nonempty(value: Any, where: str) -> None:
    if value is None or value == "" or value == [] or value == {}:
        raise ContractError(f"{where}: must not be empty")


def nonempty_string(value: Any, where: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{where}: must be a non-empty string")


def string_list(value: Any, where: str, *, allow_empty: bool = True) -> None:
    if not isinstance(value, list):
        raise ContractError(f"{where}: must be a list")
    if not allow_empty and not value:
        raise ContractError(f"{where}: must not be empty")
    for index, item in enumerate(value):
        nonempty_string(item, f"{where}[{index}]")


def _relative_path(value: Any, where: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{where}: referenced path must be a non-empty string")
    relative_path = Path(value)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ContractError(f"{where}: referenced path must stay under root")
    return relative_path


def _digest_string(value: Any, where: str) -> None:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", value):
        raise ContractError(f"{where}: must be a non-empty SHA-256 digest")


def digest(root: Path, relative: Any, where: str = "path") -> str:
    relative_path = _relative_path(relative, where)
    resolved_root = root.expanduser().resolve()
    path = (resolved_root / relative_path).resolve()
    try:
        path.relative_to(resolved_root)
    except ValueError as exc:
        # Checking the resolved path prevents a symlink under root from
        # escaping the campaign evidence directory.
        raise ContractError(f"{where}: referenced path escapes root through a symlink") from exc
    if not path.is_file():
        raise ContractError(f"{path}: referenced file is absent")
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def _plural(value: dict[str, Any], plural: str, singular: str,
            where: str) -> list[dict[str, Any]]:
    """A declaration that is a list, accepting the pre-plural single object."""
    items = value.get(plural)
    if items is None:
        items = value.get(singular)
        if isinstance(items, dict):
            items = [items]
    if not isinstance(items, list) or not items:
        raise ContractError(f"{where}.{plural}: must be a non-empty list")
    return [object_at(item, f"{where}.{plural}[{index}]")
            for index, item in enumerate(items)]


def validate_manifest(value: dict[str, Any], root: Path | None) -> None:
    require(
        value,
        ("schema_version", "campaign_id", "compiler", "target", "profiler", "reports", "observations", "attribution"),
        "manifest",
    )
    compiler = object_at(value["compiler"], "manifest.compiler")
    artifact = object_at(compiler.get("artifact"), "manifest.compiler.artifact")
    target = object_at(value["target"], "manifest.target")
    # `workloads` and `invocations` are lists.  They were single objects, and
    # that is what made "profile one case, write one pass" the only shape this
    # artifact could express: the digest-bound evidence of a whole round could
    # describe exactly one case.  A single object is still accepted as a
    # one-element list.
    workloads = _plural(value, "workloads", "workload", "manifest")
    invocations = _plural(value, "invocations", "invocation", "manifest")
    profiler = object_at(value["profiler"], "manifest.profiler")
    attribution = object_at(value["attribution"], "manifest.attribution")
    require(compiler, ("revision", "artifact"), "manifest.compiler")
    require(artifact, ("path", "sha256"), "manifest.compiler.artifact")
    require(target, ("fingerprint", "facts"), "manifest.target")
    workload_ids: set[str] = set()
    for index, workload in enumerate(workloads):
        where = f"manifest.workloads[{index}]"
        require(workload, ("id", "constructs", "shape", "type", "layout"), where)
        nonempty_string(workload["id"], f"{where}.id")
        if workload["id"] in workload_ids:
            raise ContractError(f"{where}.id: declared twice")
        workload_ids.add(workload["id"])
        # The declared constructs this workload exercises.  They are what the
        # campaign's coverage is counted against -- the project's own statement
        # of what it supports, never the corpus, which is a sample.
        string_list(workload["constructs"], f"{where}.constructs", allow_empty=False)
    for index, invocation in enumerate(invocations):
        where = f"manifest.invocations[{index}]"
        require(invocation, ("id", "configuration"), where)
        nonempty_string(invocation["id"], f"{where}.id")
        if not isinstance(invocation["configuration"], dict):
            raise ContractError(f"{where}.configuration: must be an object")
    require(profiler, ("adapter", "version", "sources"), "manifest.profiler")
    nonempty_string(compiler["revision"], "manifest.compiler.revision")
    _relative_path(artifact["path"], "manifest.compiler.artifact.path")
    _digest_string(artifact["sha256"], "manifest.compiler.artifact.sha256")
    nonempty_string(target["fingerprint"], "manifest.target.fingerprint")
    if not isinstance(value["reports"], list) or not value["reports"]:
        raise ContractError("manifest.reports: must be a non-empty list")
    require(attribution, ("status", "references"), "manifest.attribution")
    if not isinstance(attribution["status"], str) or attribution["status"] not in {"mapped", "partial", "unavailable"}:
        raise ContractError("manifest.attribution.status: invalid value")
    if not isinstance(attribution["references"], list):
        raise ContractError("manifest.attribution.references: must be a list")
    if root is not None:
        actual = digest(root, artifact["path"], "manifest.compiler.artifact.path")
        if actual != artifact["sha256"]:
            raise ContractError("manifest.compiler.artifact: sha256 mismatch")
    for index, report in enumerate(value["reports"]):
        report = object_at(report, f"manifest.reports[{index}]")
        require(report, ("path", "sha256"), f"manifest.reports[{index}]")
        _relative_path(report["path"], f"manifest.reports[{index}].path")
        _digest_string(report["sha256"], f"manifest.reports[{index}].sha256")
        if root is not None and digest(root, report["path"], f"manifest.reports[{index}].path") != report["sha256"]:
            raise ContractError(f"manifest.reports[{index}]: sha256 mismatch")
    if not isinstance(value["observations"], list):
        raise ContractError("manifest.observations: must be a list")
    statuses = {"collected", "zero", "unsupported", "missing", "parse_error", "collection_error"}
    for index, observation in enumerate(value["observations"]):
        observation = object_at(observation, f"manifest.observations[{index}]")
        where = f"manifest.observations[{index}]"
        require(observation, ("name", "unit", "scope", "status", "source"), where)
        nonempty_string(observation["name"], f"{where}.name")
        nonempty_string(observation["unit"], f"{where}.unit")
        scope = object_at(observation["scope"], f"{where}.scope")
        source = object_at(observation["source"], f"{where}.source")
        if not scope:
            raise ContractError(f"{where}.scope: must not be empty")
        if not source:
            raise ContractError(f"{where}.source: must not be empty")
        if not any(isinstance(source.get(key), str) and source.get(key).strip() for key in ("path", "location", "uri")):
            raise ContractError(f"{where}.source: must include a path, location, or uri")
        if not isinstance(observation["status"], str) or observation["status"] not in statuses:
            raise ContractError(f"manifest.observations[{index}]: invalid status")
        if observation["status"] in {"collected", "zero"}:
            require(observation, ("value",), where)
            if isinstance(observation["value"], bool) or not isinstance(observation["value"], (int, float)) or not math.isfinite(float(observation["value"])):
                raise ContractError(f"{where}.value: collected observations require a finite number")
            if observation["status"] == "zero" and float(observation["value"]) != 0.0:
                raise ContractError(f"{where}: zero status requires numeric value zero")
            if observation["status"] == "collected" and float(observation["value"]) == 0.0:
                raise ContractError(f"{where}: numeric zero must use status zero")
        elif "value" in observation and observation["value"] is not None:
            if isinstance(observation["value"], bool) or isinstance(observation["value"], (int, float)):
                raise ContractError(f"{where}.value: failed or unknown observations must not contain a numeric value")

    instances = value.get("instances")
    if instances is not None:
        if not isinstance(instances, list):
            raise ContractError("manifest.instances: must be a list")
        selected = 0
        for index, instance in enumerate(instances):
            where = f"manifest.instances[{index}]"
            instance = object_at(instance, where)
            require(instance, ("id", "identity", "selected"), where)
            nonempty_string(instance["id"], f"{where}.id")
            if not isinstance(instance["identity"], dict) or not instance["identity"]:
                raise ContractError(f"{where}.identity: must be a non-empty object")
            if not isinstance(instance["selected"], bool):
                raise ContractError(f"{where}.selected: must be boolean")
            selected += int(instance["selected"])
        consumed = [row for row in value["observations"] if row.get("status") in {"collected", "zero"}]
        if consumed and selected == 0:
            raise ContractError("manifest.instances: collected observations require an identity-matched selected instance")
        selection = value.get("instance_selection", {})
        if not isinstance(selection, dict):
            raise ContractError("manifest.instance_selection: must be an object")
        if selected > 1 and selection.get("allow_multiple") is not True:
            raise ContractError("manifest.instances: multiple selected instances require instance_selection.allow_multiple=true")


def validate_bottlenecks(value: dict[str, Any]) -> None:
    require(value, ("schema_version", "candidates"), "bottlenecks")
    if not isinstance(value["candidates"], list) or not value["candidates"]:
        raise ContractError("bottlenecks.candidates: must be a non-empty list")
    for index, candidate in enumerate(value["candidates"]):
        where = f"bottlenecks.candidates[{index}]"
        candidate = object_at(candidate, where)
        attribution = object_at(candidate.get("attribution"), f"{where}.attribution")
        next_experiment = object_at(candidate.get("next_experiment"), f"{where}.next_experiment")
        require(candidate, ("id", "workload", "evidence", "observation", "candidate_causes", "support", "contradictions", "alternatives", "unknowns", "attribution", "next_experiment", "action_layer", "status"), where)
        nonempty_string(candidate["id"], f"{where}.id")
        workload = object_at(candidate["workload"], f"{where}.workload")
        require(workload, ("id", "invocation"), f"{where}.workload")
        nonempty_string(workload["id"], f"{where}.workload.id")
        nonempty_string(workload["invocation"], f"{where}.workload.invocation")
        nonempty_string(candidate["observation"], f"{where}.observation")
        string_list(candidate["evidence"], f"{where}.evidence", allow_empty=False)
        require(next_experiment, ("question", "procedure", "success_observation", "failure_observation"), f"{where}.next_experiment")
        for field in ("question", "procedure", "success_observation", "failure_observation"):
            nonempty_string(next_experiment[field], f"{where}.next_experiment.{field}")
        require(attribution, ("status", "artifact_ranges", "ir_nodes", "passes", "limits"), f"{where}.attribution")
        if not isinstance(attribution["status"], str) or attribution["status"] not in {"exact", "range", "partial", "unavailable"}:
            raise ContractError(f"{where}.attribution.status: invalid value")
        for field in ("artifact_ranges", "ir_nodes", "passes"):
            string_list(attribution[field], f"{where}.attribution.{field}")
        nonempty_string(attribution["limits"], f"{where}.attribution.limits")
        if not isinstance(candidate["action_layer"], str) or candidate["action_layer"] not in {"pass", "existing_pass", "lowering", "runtime", "evidence_needed", "out_of_scope"}:
            raise ContractError(f"{where}.action_layer: invalid value")
        if not isinstance(candidate["status"], str) or candidate["status"] not in {"open", "rejected", "confirmed", "inconclusive"}:
            raise ContractError(f"{where}.status: invalid value")
        for field in ("candidate_causes", "support", "contradictions", "alternatives", "unknowns"):
            if not isinstance(candidate[field], list):
                raise ContractError(f"{where}.{field}: must be a list")
        if not candidate["candidate_causes"]:
            raise ContractError(f"{where}.candidate_causes: must not be empty")
        for cause_index, cause in enumerate(candidate["candidate_causes"]):
            cause_where = f"{where}.candidate_causes[{cause_index}]"
            cause = object_at(cause, cause_where)
            require(cause, ("id", "statement", "confidence"), cause_where)
            nonempty_string(cause["id"], f"{cause_where}.id")
            nonempty_string(cause["statement"], f"{cause_where}.statement")
            if not isinstance(cause["confidence"], str) or cause["confidence"] not in {"low", "medium", "high"}:
                raise ContractError(f"{cause_where}.confidence: invalid value")


def validate_recommendation(value: dict[str, Any]) -> None:
    require(value, ("schema_version", "campaign_id", "status", "recommendations"), "recommendation")
    statuses = {"proposed", "evidence_needed", "out_of_scope", "accepted", "rejected"}
    if not isinstance(value["status"], str) or value["status"] not in statuses:
        raise ContractError("recommendation.status: invalid value")
    if not isinstance(value["recommendations"], list) or not value["recommendations"]:
        raise ContractError("recommendation.recommendations: must be a non-empty list")
    for index, item in enumerate(value["recommendations"]):
        where = f"recommendation.recommendations[{index}]"
        item = object_at(item, where)
        action = object_at(item.get("action"), f"{where}.action")
        context = object_at(item.get("ir_context"), f"{where}.ir_context")
        require(item, ("id", "action", "evidence_refs", "observed_in", "ir_context", "mechanism", "legality_questions", "risks", "expected_evidence", "required_followup", "confidence"), where)
        require(action, ("category", "description", "scope", "candidate_existing_pass"), f"{where}.action")
        require(context, ("mapping_status", "level_id", "structural_properties", "references", "limits"), f"{where}.ir_context")
        nonempty_string(item["id"], f"{where}.id")
        nonempty_string(action["category"], f"{where}.action.category")
        nonempty_string(action["description"], f"{where}.action.description")
        if not isinstance(action["scope"], str) or action["scope"] not in {"existing_pass", "new_pass", "lowering", "runtime", "workload"}:
            raise ContractError(f"{where}.action.scope: invalid value")
        if action["scope"] == "existing_pass" and not isinstance(action["candidate_existing_pass"], str):
            raise ContractError(f"{where}.action.candidate_existing_pass: required for existing_pass scope")
        if action["candidate_existing_pass"] is not None and not isinstance(action["candidate_existing_pass"], str):
            raise ContractError(f"{where}.action.candidate_existing_pass: must be a string or null")
        if not isinstance(context["mapping_status"], str) or context["mapping_status"] not in {"verified", "partial", "unavailable"}:
            raise ContractError(f"{where}.ir_context.mapping_status: invalid value")
        if context["level_id"] is not None and not isinstance(context["level_id"], str):
            raise ContractError(f"{where}.ir_context.level_id: must be a string or null")
        string_list(context["structural_properties"], f"{where}.ir_context.structural_properties")
        string_list(context["references"], f"{where}.ir_context.references")
        nonempty_string(context["limits"], f"{where}.ir_context.limits")
        if not isinstance(item["confidence"], str) or item["confidence"] not in {"low", "medium", "high"}:
            raise ContractError(f"{where}.confidence: invalid value")
        # The profiled workloads this structure was actually observed in.  It
        # is what makes a *general* claim checkable: a bundle citing this
        # recommendation may claim generality only as wide as this list, and
        # one workload is a specialisation of that case however it is
        # labelled.  Required, because an absent list would read as width the
        # campaign never showed.
        string_list(item["observed_in"], f"{where}.observed_in", allow_empty=False)
        # The answer for a recommendation no bundle took up.  "accepted" is
        # deliberately not a legal state: acceptance is read from the bundles
        # that cite the recommendation, which is the one claim about it that
        # cannot be made by writing it down.
        if "disposition" in item:
            block = object_at(item["disposition"], f"{where}.disposition")
            require(block, ("state", "reason"), f"{where}.disposition")
            if block["state"] not in {"deferred", "out_of_scope"}:
                raise ContractError(
                    f"{where}.disposition.state: must be deferred or "
                    "out_of_scope (acceptance is read from the bundles that "
                    "cite this recommendation, never declared)")
            nonempty_string(block["reason"], f"{where}.disposition.reason")
        for field in ("evidence_refs", "legality_questions", "risks", "expected_evidence", "required_followup"):
            if not isinstance(item[field], list):
                raise ContractError(f"{where}.{field}: must be a list")
            string_list(item[field], f"{where}.{field}")
        if context["mapping_status"] in {"partial", "unavailable"} and not item["required_followup"]:
            raise ContractError(f"{where}.required_followup: required when IR mapping is not verified")

    mappings = [item["ir_context"]["mapping_status"] for item in value["recommendations"]]
    if value["status"] in {"proposed", "accepted"} and any(status != "verified" for status in mappings):
        raise ContractError(f"recommendation.status={value['status']}: all recommendations require verified IR mapping")
    if value["status"] == "out_of_scope" and any(item["action"]["scope"] not in {"runtime", "workload"} for item in value["recommendations"]):
        raise ContractError("recommendation.status=out_of_scope: action scope must be runtime or workload")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--bottlenecks", type=Path, required=True)
    parser.add_argument("--recommendation", type=Path, required=True)
    parser.add_argument("--root", type=Path, help="root for referenced artifact and report paths")
    args = parser.parse_args()
    try:
        validate_manifest(load(args.manifest), args.root)
        validate_bottlenecks(load(args.bottlenecks))
        validate_recommendation(load(args.recommendation))
    except ContractError as exc:
        parser.error(str(exc))
    print("profile-to-compiler-pass contracts are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
