from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .errors import ValidationRejected
from .hashing import canonical_hash
from .schema import validate


class ExecutionContextVerifier(Protocol):
    def verify(self, context: dict[str, Any]) -> dict[str, Any]: ...


class LocalHarnessVerifier:
    """Test-only verifier: trusts whoever supplies the context. The CLI uses PasskeyApprovalVerifier instead."""

    def verify(self, context: dict[str, Any]) -> dict[str, Any]:
        validate(context, "execution-context.schema.json")
        if context.get("trust_mode") != "local_harness":
            raise ValidationRejected("Unsupported execution-context trust mode")
        return context


def mutation_action_material(transaction: dict[str, Any], mutation: dict[str, Any]) -> dict[str, Any]:
    """The exact fields a human authorization is bound to. Rationale and summary are deliberately excluded."""
    return {
        "project": transaction["project"],
        "transaction_id": transaction["transaction_id"],
        "operation": mutation["operation"],
        "section": mutation["section"],
        "record_id": mutation.get("record_id"),
        "patch": mutation.get("patch", {}),
        "dependencies": mutation.get("dependencies", []),
    }


def mutation_action_hash(transaction: dict[str, Any], mutation: dict[str, Any]) -> str:
    return canonical_hash(mutation_action_material(transaction, mutation))


def mutation_requires_direct_human_authorization(mutation: dict[str, Any]) -> bool:
    op = mutation["operation"]
    section = mutation["section"]
    patch = mutation.get("patch", {})
    if op == "reopen_iteration":
        return True
    if section == "decisions" and patch.get("authority") == "human" and patch.get("status") == "settled":
        return True
    if op == "reconfirm" and section == "decisions":
        return True
    return False


def verify_human_authorizations(transaction: dict[str, Any], context: dict[str, Any], state: dict[str, Any] | None) -> list[str]:
    auths = {a["authorization_id"]: a for a in context.get("human_authorizations", [])}
    used_ids: set[str] = set()
    previously_used: set[str] = set()
    if state:
        for event in state.get("history", []):
            auth_id = event.get("authorization_id")
            if auth_id:
                previously_used.add(auth_id)
            for used in event.get("authorization_ids", []):
                previously_used.add(used)

    for mutation in transaction["state_mutations"]:
        if not mutation_requires_direct_human_authorization(mutation):
            continue
        auth_id = mutation.get("authorization_id")
        if not auth_id or auth_id not in auths:
            raise ValidationRejected(f"Mutation {mutation['operation']} requires trusted human authorization")
        auth = auths[auth_id]
        if auth_id in previously_used:
            raise ValidationRejected(f"Human authorization {auth_id} has already been consumed")
        if auth["project_id"] != transaction["project"]["project_id"] or auth["iteration"] != transaction["project"]["iteration"]:
            raise ValidationRejected(f"Human authorization {auth_id} is bound to a different project or iteration")
        if auth["transaction_id"] != transaction["transaction_id"]:
            raise ValidationRejected(f"Human authorization {auth_id} is bound to a different transaction")
        expected = mutation_action_hash(transaction, mutation)
        if auth["action_hash"] != expected:
            raise ValidationRejected(f"Human authorization {auth_id} does not match the exact action")
        used_ids.add(auth_id)
    return sorted(used_ids)
