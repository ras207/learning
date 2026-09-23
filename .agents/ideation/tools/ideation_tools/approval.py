from __future__ import annotations

import base64
from typing import Any

from .auth import mutation_action_hash, mutation_action_material, mutation_requires_direct_human_authorization
from .errors import ValidationRejected
from .hashing import canonical_json_bytes
from .primitives import validate_transaction

REQUEST_KIND = "ideation_approval_request"


def _describe_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    return canonical_json_bytes(value).decode("utf-8")


def describe_action(action: dict[str, Any]) -> list[str]:
    """Deterministic plain-text description of exactly what an authorization covers."""
    project = action["project"]
    lines = [
        f"{action['operation']} {action['section']} record {action['record_id'] or '(none)'}",
        f"Project {project['project_id']} (iteration {project['iteration']}), transaction {action['transaction_id']}",
    ]
    for key in sorted(action["patch"]):
        lines.append(f"  {key}: {_describe_value(action['patch'][key])}")
    if action["dependencies"]:
        lines.append(f"Depends on: {', '.join(action['dependencies'])}")
    return lines


def encode_request(payload: dict[str, Any]) -> str:
    return base64.urlsafe_b64encode(canonical_json_bytes(payload)).decode("ascii").rstrip("=")


def build_approval_requests(transaction: dict[str, Any], *, page_url: str) -> list[dict[str, Any]]:
    """Build one approval request per mutation that needs direct human authorization.

    The request carries the exact hash material so the approval page can recompute
    `action_hash` itself rather than trusting the agent's value. `rationale` and
    `transaction_summary` are the agent's own words and are not covered by the hash.
    """
    validate_transaction(transaction)
    requests = []
    for mutation in transaction["state_mutations"]:
        if not mutation_requires_direct_human_authorization(mutation):
            continue
        if not mutation.get("authorization_id"):
            raise ValidationRejected(
                f"Mutation {mutation['operation']} on {mutation['section']} needs an authorization_id before approval can be requested"
            )
        action = mutation_action_material(transaction, mutation)
        payload = {
            "schema_version": 1,
            "kind": REQUEST_KIND,
            "authorization_id": mutation["authorization_id"],
            "action": action,
            "action_hash": mutation_action_hash(transaction, mutation),
            "unsigned_context": {"transaction_summary": transaction["summary"], "rationale": mutation["rationale"]},
        }
        requests.append({
            **payload,
            "description": describe_action(action),
            "link": f"{page_url}#{encode_request(payload)}",
        })
    return requests
