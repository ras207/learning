from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

from .approvers import DEFAULT_APPROVERS_PATH, b64url_decode, load_approvers, load_public_key
from .auth import mutation_action_hash, mutation_action_material
from .errors import ValidationRejected
from .schema import validate

APPROVAL_KIND = "ideation_approval"
EVIDENCE_KIND = "ideation_approval_evidence"
ASSERTION_FIELDS = ("credential_id", "authenticator_data", "client_data_json", "signature")

# WebAuthn authenticator data flags (byte 32).
FLAG_USER_PRESENT = 0x01
FLAG_USER_VERIFIED = 0x04


def verify_passkey_assertion(action_hash: str, assertion: dict[str, Any], approvers: dict[str, Any]) -> dict[str, Any]:
    """Check a WebAuthn assertion signs `action_hash` with a registered approver key.

    Returns the matching approver entry. The signature counter is not checked:
    synced passkeys report 0. Replay is prevented by single-use, transaction-bound
    authorizations instead.
    """
    entry = next((a for a in approvers["approvers"] if a["credential_id"] == assertion["credential_id"]), None)
    if entry is None:
        raise ValidationRejected("Approval was signed by a passkey that is not a registered approver")

    client_data_bytes = b64url_decode(assertion["client_data_json"])
    try:
        client_data = json.loads(client_data_bytes)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValidationRejected("Approval client data is not valid JSON") from exc
    if client_data.get("type") != "webauthn.get":
        raise ValidationRejected("Approval is not a WebAuthn authentication")
    if b64url_decode(client_data.get("challenge", "")) != bytes.fromhex(action_hash):
        raise ValidationRejected("Approval signs a different action")
    if client_data.get("origin") != approvers["origin"]:
        raise ValidationRejected(f"Approval was signed on {client_data.get('origin')}, expected {approvers['origin']}")
    if client_data.get("crossOrigin"):
        raise ValidationRejected("Approval was signed inside a cross-origin frame")

    auth_data = b64url_decode(assertion["authenticator_data"])
    if len(auth_data) < 37:
        raise ValidationRejected("Approval authenticator data is too short")
    if auth_data[:32] != hashlib.sha256(approvers["rp_id"].encode("utf-8")).digest():
        raise ValidationRejected("Approval was signed for a different site")
    flags = auth_data[32]
    if not flags & FLAG_USER_PRESENT or not flags & FLAG_USER_VERIFIED:
        raise ValidationRejected("Approval did not use Face ID, fingerprint or device PIN")

    try:
        load_public_key(entry["public_key_spki"]).verify(
            b64url_decode(assertion["signature"]),
            auth_data + hashlib.sha256(client_data_bytes).digest(),
            ec.ECDSA(hashes.SHA256()),
        )
    except InvalidSignature as exc:
        raise ValidationRejected("Approval signature is invalid") from exc
    return entry


class PasskeyApprovalVerifier:
    """Execution-context verifier that accepts human authorizations only with valid passkey signatures."""

    def __init__(self, approvers_path: Path = DEFAULT_APPROVERS_PATH):
        self.approvers_path = Path(approvers_path)

    def verify(self, context: dict[str, Any]) -> dict[str, Any]:
        validate(context, "execution-context.schema.json")
        if context.get("trust_mode") != "passkey":
            raise ValidationRejected("Execution context must use trust_mode 'passkey'")
        approvers = load_approvers(self.approvers_path)
        verified = copy.deepcopy(context)
        for auth in verified["human_authorizations"]:
            if "passkey" not in auth:
                raise ValidationRejected(f"Human authorization {auth['authorization_id']} has no passkey signature")
            entry = verify_passkey_assertion(auth["action_hash"], auth["passkey"], approvers)
            # The approver's identity comes from the verified key, never from the caller.
            auth["actor"] = entry["approver"]
            auth["approver_fingerprint"] = entry["fingerprint"]
        return verified


def parse_approval_code(code: str) -> dict[str, Any]:
    """Decode the approval code produced by the approval page."""
    try:
        approval = json.loads(b64url_decode(code.strip()))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValidationRejected("Approval code is not valid JSON") from exc
    if not isinstance(approval, dict) or approval.get("kind") != APPROVAL_KIND or approval.get("schema_version") != 1:
        raise ValidationRejected("Code is not an ideation approval")
    for field in ("authorization_id", "action_hash", *ASSERTION_FIELDS):
        if not isinstance(approval.get(field), str):
            raise ValidationRejected(f"Approval code is missing {field}")
    return approval


def build_authorization(transaction: dict[str, Any], code: str, approvers: dict[str, Any], *,
                        issued_at: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Verify an approval code against a transaction; return (context authorization, approver entry)."""
    approval = parse_approval_code(code)
    mutation = next((m for m in transaction["state_mutations"]
                     if m.get("authorization_id") == approval["authorization_id"]), None)
    if mutation is None:
        raise ValidationRejected(f"Transaction has no mutation awaiting authorization {approval['authorization_id']}")
    action_hash = mutation_action_hash(transaction, mutation)
    if approval["action_hash"] != action_hash:
        raise ValidationRejected("Approval is for a different version of this change")
    assertion = {field: approval[field] for field in ASSERTION_FIELDS}
    entry = verify_passkey_assertion(action_hash, assertion, approvers)
    authorization = {
        "authorization_id": approval["authorization_id"],
        "project_id": transaction["project"]["project_id"],
        "iteration": transaction["project"]["iteration"],
        "transaction_id": transaction["transaction_id"],
        "action_hash": action_hash,
        "actor": entry["approver"],
        "issued_at": issued_at,
        "passkey": assertion,
    }
    return authorization, entry


def approval_evidence(transaction: dict[str, Any], mutation: dict[str, Any], auth: dict[str, Any]) -> dict[str, Any]:
    """Self-contained record that lets anyone re-verify a committed human approval."""
    return {
        "schema_version": 1,
        "kind": EVIDENCE_KIND,
        "authorization_id": auth["authorization_id"],
        "approver": auth["actor"],
        "approver_fingerprint": auth["approver_fingerprint"],
        "action": mutation_action_material(transaction, mutation),
        "action_hash": auth["action_hash"],
        "passkey": auth["passkey"],
    }
