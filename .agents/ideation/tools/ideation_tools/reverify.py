from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import ValidationRejected
from .hashing import canonical_hash
from .invariants import enforce_invariants
from .passkey import EVIDENCE_KIND, verify_passkey_assertion
from .state import parse_state, validate_state

EVIDENCE_FIELDS = ("authorization_id", "approver", "approver_fingerprint", "action", "action_hash", "passkey")


def _load_evidence(approvals_dir: Path, problems: list[str]) -> dict[str, dict[str, Any]]:
    evidence: dict[str, dict[str, Any]] = {}
    if not approvals_dir.is_dir():
        return evidence
    for path in sorted(approvals_dir.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"{path.name}: unreadable evidence ({exc})")
            continue
        if not isinstance(record, dict) or record.get("kind") != EVIDENCE_KIND or any(f not in record for f in EVIDENCE_FIELDS):
            problems.append(f"{path.name}: not a complete approval evidence record")
            continue
        if path.stem != record["authorization_id"]:
            problems.append(f"{path.name}: file name does not match authorization_id {record['authorization_id']}")
            continue
        evidence[record["authorization_id"]] = record
    return evidence


def _check_evidence(auth_id: str, record: dict[str, Any], state: dict[str, Any], approvers: dict[str, Any]) -> list[str]:
    problems = []
    action = record["action"]
    if canonical_hash(action) != record["action_hash"]:
        problems.append(f"{auth_id}: signed fields do not match the recorded action hash")
    project = state["project"]
    if action.get("project", {}).get("project_id") != project["project_id"] or action.get("project", {}).get("project_slug") != project["project_slug"]:
        problems.append(f"{auth_id}: approval belongs to a different project")
    try:
        entry = verify_passkey_assertion(record["action_hash"], record["passkey"], approvers)
    except ValidationRejected as exc:
        problems.append(f"{auth_id}: {exc}")
    else:
        if entry["fingerprint"] != record["approver_fingerprint"] or entry["approver"] != record["approver"]:
            problems.append(f"{auth_id}: recorded approver does not match the signing key")
    return problems


def verify_project(project_dir: Path, approvers: dict[str, Any]) -> list[str]:
    """Re-verify every human approval a project's committed state relies on. Returns the problems found."""
    problems: list[str] = []
    try:
        state = parse_state((project_dir / "state.yaml").read_bytes())
        validate_state(state)
    except (OSError, ValidationRejected) as exc:
        return [f"state.yaml: {exc}"]

    vision = project_dir / "vision.md"
    artifacts = {f"projects/{state['project']['project_slug']}/ideation/vision.md": vision.read_bytes()} if vision.exists() else {}
    try:
        enforce_invariants(state, artifacts)
    except ValidationRejected as exc:
        problems.append(f"state.yaml: {exc}")

    evidence = _load_evidence(project_dir / "approvals", problems)
    for auth_id, record in evidence.items():
        problems.extend(_check_evidence(auth_id, record, state, approvers))

    used: dict[str, str] = {}
    for event in state.get("history", []):
        for auth_id in event.get("authorization_ids", []):
            if auth_id in used:
                problems.append(f"{auth_id}: used by more than one transaction")
            used[auth_id] = event.get("transaction_id")
            record = evidence.get(auth_id)
            if record is None:
                problems.append(f"{auth_id}: history event {event.get('event_id')} has no approval evidence")
            elif record["action"].get("transaction_id") != event.get("transaction_id"):
                problems.append(f"{auth_id}: evidence was signed for a different transaction than history records")
    for auth_id in evidence.keys() - used.keys():
        problems.append(f"{auth_id}: evidence is not referenced by any history event")

    for decision in state.get("decisions", []):
        if decision.get("authority") != "human" or decision.get("status") != "settled":
            continue
        auth_id = decision.get("authorization_id")
        record = evidence.get(auth_id) if auth_id else None
        if record is None:
            problems.append(f"decision {decision.get('id')}: settled human decision has no verified approval")
            continue
        action = record["action"]
        if action.get("section") != "decisions" or action.get("record_id") != decision.get("id"):
            problems.append(f"decision {decision.get('id')}: approval {auth_id} was for a different record")
            continue
        changed = sorted(k for k, v in action.get("patch", {}).items() if decision.get(k) != v)
        if changed:
            problems.append(f"decision {decision.get('id')}: changed after approval ({', '.join(changed)})")
    return problems


def verify_repository(root: Path, approvers: dict[str, Any]) -> dict[str, list[str]]:
    """Map each project slug under root/projects to the approval problems found in it."""
    return {state_path.parents[1].name: verify_project(state_path.parent, approvers)
            for state_path in sorted(Path(root).glob("projects/*/ideation/state.yaml"))}
