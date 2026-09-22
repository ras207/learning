from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .errors import ValidationRejected


@dataclass(frozen=True)
class InvariantResult:
    id: str
    passed: bool
    message: str


@dataclass(frozen=True)
class Invariant:
    id: str
    description: str
    validator: Callable[[dict[str, Any], dict[str, bytes]], tuple[bool, str]]


def _find_gate(state: dict[str, Any], gate_id: int) -> dict[str, Any] | None:
    current = [g for g in state.get("gate_evaluations", []) if g.get("gate_id") == gate_id and g.get("validity") == "current"]
    return current[-1] if current else None


def _blocking_items_clear(state: dict[str, Any], artifacts: dict[str, bytes]) -> tuple[bool, str]:
    if state.get("workflow", {}).get("status") != "approved":
        return True, "Not an approved terminal state"
    blocking = [w.get("id") for w in state.get("work_items", []) if w.get("blocking") and w.get("status") not in {"resolved", "superseded"}]
    return (not blocking, "No unresolved blocking work items" if not blocking else f"Blocking work items remain: {blocking}")


def _no_open_escalation(state: dict[str, Any], artifacts: dict[str, bytes]) -> tuple[bool, str]:
    if state.get("workflow", {}).get("status") != "approved":
        return True, "Not an approved terminal state"
    open_escalations = [w.get("id") for w in state.get("work_items", []) if w.get("type") == "escalation" and w.get("status") not in {"resolved", "superseded"}]
    return (not open_escalations, "No open human escalations" if not open_escalations else f"Open escalations remain: {open_escalations}")


def _terminal_gate_validity(state: dict[str, Any], artifacts: dict[str, bytes]) -> tuple[bool, str]:
    if state.get("workflow", {}).get("status") != "approved":
        return True, "Not an approved terminal state"
    missing = []
    for gate_id in range(1, 7):
        g = _find_gate(state, gate_id)
        if not g or g.get("outcome") not in {"PASS", "PASS_WITH_UNCERTAINTY"}:
            missing.append(gate_id)
    return (not missing, "All six current gate evaluations pass" if not missing else f"Required current passing gates missing: {missing}")


def _gate6_human_approval(state: dict[str, Any], artifacts: dict[str, bytes]) -> tuple[bool, str]:
    g6 = _find_gate(state, 6)
    if not g6 or g6.get("outcome") not in {"PASS", "PASS_WITH_UNCERTAINTY"}:
        if state.get("workflow", {}).get("status") == "approved":
            return False, "Gate 6 is not currently passing"
        return True, "No current passing Gate 6 evaluation"
    ids = g6.get("human_decision_ids", [])
    decisions = {d.get("id"): d for d in state.get("decisions", [])}
    for decision_id in ids:
        d = decisions.get(decision_id)
        if d and d.get("authority") == "human" and d.get("status") == "settled" and d.get("authorization_id"):
            return True, f"Gate 6 is backed by trusted human decision {decision_id}"
    return False, "Gate 6 lacks a settled trusted human approval decision"


def _approved_vision_consistency(state: dict[str, Any], artifacts: dict[str, bytes]) -> tuple[bool, str]:
    workflow = state.get("workflow", {})
    if workflow.get("status") != "approved":
        return True, "Not an approved terminal state"
    if workflow.get("vision_status") != "approved":
        return False, "Approved workflow requires vision_status approved"
    vision_path = f"projects/{state['project']['project_slug']}/ideation/vision.md"
    data = artifacts.get(vision_path)
    if data is None:
        return False, f"Approved vision artifact missing at {vision_path}"
    prefix = data.decode("utf-8", errors="replace")[:500]
    if "status: approved" not in prefix:
        return False, "Approved vision artifact does not declare status: approved"
    return True, "Approved vision state and artifact agree"


def _not_progressing_no_handoff(state: dict[str, Any], artifacts: dict[str, bytes]) -> tuple[bool, str]:
    if state.get("workflow", {}).get("status") != "not_progressing":
        return True, "Not a not_progressing terminal state"
    if state.get("workflow", {}).get("vision_status") == "approved":
        return False, "not_progressing cannot retain an approved vision status"
    return True, "not_progressing has no approved handoff"



def _not_progressing_human_authorized(state: dict[str, Any], artifacts: dict[str, bytes]) -> tuple[bool, str]:
    if state.get("workflow", {}).get("status") != "not_progressing":
        return True, "Not a not_progressing terminal state"
    decision_id = state.get("finalization", {}).get("authorized_by_decision_id")
    decisions = {d.get("id"): d for d in state.get("decisions", [])}
    decision = decisions.get(decision_id)
    if decision and decision.get("authority") == "human" and decision.get("status") == "settled" and decision.get("authorization_id"):
        return True, f"not_progressing is backed by trusted human decision {decision_id}"
    return False, "not_progressing lacks a trusted explicit human closure decision"


def _terminal_finalization_recorded(state: dict[str, Any], artifacts: dict[str, bytes]) -> tuple[bool, str]:
    status = state.get("workflow", {}).get("status")
    if status not in {"approved", "not_progressing"}:
        return True, "Run is non-terminal"
    outcome = state.get("finalization", {}).get("outcome")
    return (outcome == status, "Finalization outcome matches terminal workflow status" if outcome == status else f"Finalization outcome {outcome!r} does not match {status!r}")


INVARIANTS = [
    Invariant("INV-001", "No unresolved blocking work may remain in an approved handoff.", _blocking_items_clear),
    Invariant("INV-002", "No open human escalation may remain in an approved handoff.", _no_open_escalation),
    Invariant("INV-003", "Approved handoff requires all six current passing gate evaluations.", _terminal_gate_validity),
    Invariant("INV-004", "Approved handoff requires trusted explicit human Gate 6 approval.", _gate6_human_approval),
    Invariant("INV-005", "Approved workflow and approved vision artifact/status must agree.", _approved_vision_consistency),
    Invariant("INV-006", "not_progressing must not expose an approved handoff.", _not_progressing_no_handoff),
    Invariant("INV-007", "Terminal workflow status must have matching finalization outcome.", _terminal_finalization_recorded),
    Invariant("INV-008", "not_progressing requires a trusted explicit human closure decision.", _not_progressing_human_authorized),
]


def evaluate_invariants(state: dict[str, Any], artifacts: dict[str, bytes]) -> list[InvariantResult]:
    results: list[InvariantResult] = []
    for inv in INVARIANTS:
        passed, message = inv.validator(state, artifacts)
        results.append(InvariantResult(inv.id, passed, message))
    return results


def enforce_invariants(state: dict[str, Any], artifacts: dict[str, bytes]) -> list[dict[str, Any]]:
    results = evaluate_invariants(state, artifacts)
    failed = [r for r in results if not r.passed]
    if failed:
        raise ValidationRejected("Invariant violation: " + "; ".join(f"{r.id} {r.message}" for r in failed))
    return [{"id": r.id, "passed": r.passed, "message": r.message} for r in results]
