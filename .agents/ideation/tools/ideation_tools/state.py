from __future__ import annotations

import copy
from datetime import datetime, timezone
from typing import Any

import yaml

from .errors import ValidationRejected
from .schema import validate

LIST_SECTIONS = {"artifacts", "decisions", "assumptions", "work_items", "evidence", "gate_evaluations", "history"}
SINGLETON_SECTIONS = {"project", "workflow", "session", "routing", "finalization"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_state(data: bytes) -> dict[str, Any]:
    try:
        value = yaml.safe_load(data.decode("utf-8"))
    except Exception as exc:
        raise ValidationRejected(f"Unable to parse state YAML: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationRejected("State YAML must contain an object")
    return value


def dump_state(state: dict[str, Any]) -> bytes:
    return yaml.safe_dump(state, sort_keys=False, allow_unicode=True).encode("utf-8")


def validate_state(state: dict[str, Any]) -> None:
    validate(state, "ideation-state.schema.json")
    seen: set[str] = set()
    for section in LIST_SECTIONS - {"history"}:
        for record in state.get(section, []):
            rid = record_identifier(record)
            if rid:
                if rid in seen:
                    raise ValidationRejected(f"Duplicate cross-record identifier: {rid}")
                seen.add(rid)


def record_identifier(record: dict[str, Any]) -> str | None:
    for key in ("id", "artifact_id", "event_id"):
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _deep_merge(target: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(target)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


def _find_record(records: list[dict[str, Any]], record_id: str) -> tuple[int, dict[str, Any]]:
    for i, record in enumerate(records):
        if record_identifier(record) == record_id:
            return i, record
    raise ValidationRejected(f"Record {record_id} does not exist")


def apply_mutation(state: dict[str, Any] | None, mutation: dict[str, Any]) -> dict[str, Any]:
    op = mutation["operation"]
    section = mutation["section"]
    record_id = mutation.get("record_id")
    patch = mutation.get("patch", {})

    if op == "initialize":
        if state is not None:
            raise ValidationRejected("initialize is valid only when canonical state does not exist")
        new_state = copy.deepcopy(patch)
        validate_state(new_state)
        return new_state

    if state is None:
        raise ValidationRejected("Canonical state does not exist; initialize it first")
    out = copy.deepcopy(state)

    if op in {"finalize_approved", "finalize_not_progressing"}:
        if section != "finalization":
            raise ValidationRejected(f"{op} must target finalization")
        outcome = "approved" if op == "finalize_approved" else "not_progressing"
        out["workflow"]["status"] = outcome
        if outcome == "approved":
            out["workflow"]["vision_status"] = "approved"
        out["finalization"] = _deep_merge(out.get("finalization", {}), patch)
        out["finalization"]["outcome"] = outcome
        return out

    if op == "checkpoint":
        if section != "session":
            raise ValidationRejected("checkpoint must target session")
        out["session"] = _deep_merge(out["session"], patch)
        return out

    if op == "reopen_iteration":
        if section != "project":
            raise ValidationRejected("reopen_iteration must target project")
        if out["workflow"]["status"] not in {"approved", "not_progressing"}:
            raise ValidationRejected("reopen_iteration requires a terminal iteration")
        out["project"] = _deep_merge(out["project"], patch)
        out["project"]["iteration"] = state["project"]["iteration"] + 1
        out["workflow"]["status"] = "active"
        out["workflow"]["vision_status"] = "not_started"
        return out

    if section in SINGLETON_SECTIONS:
        if op not in {"update", "migrate"}:
            raise ValidationRejected(f"Operation {op} is not valid for singleton section {section}")
        out[section] = _deep_merge(out[section], patch)
        return out

    if section not in LIST_SECTIONS or section == "history":
        raise ValidationRejected(f"Unsupported mutable section: {section}")

    records = out[section]
    if op == "create":
        candidate = copy.deepcopy(patch)
        candidate_id = record_identifier(candidate) or record_id
        if not candidate_id:
            raise ValidationRejected(f"create in {section} requires a record identifier")
        if record_identifier(candidate) is None:
            candidate["id"] = candidate_id
        if any(record_identifier(r) == candidate_id for r in records):
            raise ValidationRejected(f"Record {candidate_id} already exists in {section}")
        records.append(candidate)
        return out

    if not record_id:
        raise ValidationRejected(f"Operation {op} in {section} requires record_id")
    idx, current = _find_record(records, record_id)

    if op == "update":
        records[idx] = _deep_merge(current, patch)
    elif op == "resolve":
        records[idx] = _deep_merge(current, {**patch, "status": "resolved"})
    elif op == "supersede":
        records[idx] = _deep_merge(current, {**patch, "status": "superseded"})
    elif op == "invalidate":
        if section == "gate_evaluations":
            records[idx] = _deep_merge(current, {**patch, "validity": "re_evaluation_required"})
        elif section == "decisions":
            records[idx] = _deep_merge(current, {**patch, "status": "reconfirmation_required"})
        else:
            records[idx] = _deep_merge(current, patch)
    elif op == "reconfirm":
        if section != "decisions":
            raise ValidationRejected("reconfirm is valid only for decisions")
        records[idx] = _deep_merge(current, {**patch, "status": "settled"})
    else:
        raise ValidationRejected(f"Unsupported operation {op} for section {section}")
    return out
