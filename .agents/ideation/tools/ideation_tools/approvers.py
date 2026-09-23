from __future__ import annotations

import base64
import binascii
import copy
import hashlib
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_der_public_key

from .errors import ValidationRejected
from .schema import validate

DEFAULT_APPROVERS_PATH = Path(__file__).resolve().parents[2] / "approvers.json"
RECORD_KIND = "ideation_approver"
ES256 = -7


def b64url_decode(text: str) -> bytes:
    try:
        return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))
    except (binascii.Error, ValueError) as exc:
        raise ValidationRejected(f"Invalid base64url data: {exc}") from exc


def key_fingerprint(spki: bytes) -> str:
    """Short, human-comparable fingerprint: first 8 bytes of SHA-256(SPKI) as XXXX-XXXX-XXXX-XXXX."""
    digest = hashlib.sha256(spki).hexdigest()[:16].upper()
    return "-".join(digest[i:i + 4] for i in range(0, 16, 4))


def load_public_key(public_key_spki: str) -> ec.EllipticCurvePublicKey:
    try:
        key = load_der_public_key(b64url_decode(public_key_spki))
    except ValueError as exc:
        raise ValidationRejected(f"Public key is not valid SPKI DER: {exc}") from exc
    if not isinstance(key, ec.EllipticCurvePublicKey) or not isinstance(key.curve, ec.SECP256R1):
        raise ValidationRejected("Public key must be an ECDSA P-256 key")
    return key


def validate_approvers(data: dict[str, Any]) -> dict[str, Any]:
    validate(data, "approvers.schema.json")
    host = urlparse(data["origin"]).hostname or ""
    if host != data["rp_id"] and not host.endswith("." + data["rp_id"]):
        raise ValidationRejected(f"Origin {data['origin']} is not within rp_id {data['rp_id']}")
    if not data["approval_page_url"].startswith(data["origin"] + "/"):
        raise ValidationRejected("approval_page_url must be served from origin")
    seen: set[str] = set()
    for entry in data["approvers"]:
        if entry["credential_id"] in seen:
            raise ValidationRejected(f"Duplicate credential_id for approver {entry['approver']}")
        seen.add(entry["credential_id"])
        load_public_key(entry["public_key_spki"])
        if key_fingerprint(b64url_decode(entry["public_key_spki"])) != entry["fingerprint"]:
            raise ValidationRejected(f"Fingerprint does not match public key for approver {entry['approver']}")
    return data


def load_approvers(path: Path = DEFAULT_APPROVERS_PATH) -> dict[str, Any]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationRejected(f"Cannot read approvers file {path}: {exc}") from exc
    return validate_approvers(data)


def parse_approver_record(code: str) -> dict[str, Any]:
    """Decode the registration code produced by the approval page."""
    try:
        record = json.loads(b64url_decode(code.strip()))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValidationRejected("Approver record is not valid JSON") from exc
    if not isinstance(record, dict) or record.get("kind") != RECORD_KIND or record.get("schema_version") != 1:
        raise ValidationRejected("Code is not an ideation approver record")
    for field in ("approver", "rp_id", "credential_id", "public_key_spki", "algorithm"):
        if field not in record:
            raise ValidationRejected(f"Approver record is missing {field}")
    return record


def add_approver(data: dict[str, Any], code: str, *, added_at: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (updated approvers data, new entry). The input data is not modified."""
    record = parse_approver_record(code)
    if record["rp_id"] != data["rp_id"]:
        raise ValidationRejected(f"Record was registered on {record['rp_id']}, expected {data['rp_id']}")
    if record["algorithm"] != ES256:
        raise ValidationRejected("Only ES256 passkeys are supported")
    entry = {
        "approver": record["approver"],
        "credential_id": record["credential_id"],
        "public_key_spki": record["public_key_spki"],
        "algorithm": record["algorithm"],
        "fingerprint": key_fingerprint(b64url_decode(record["public_key_spki"])),
        "added_at": added_at,
    }
    updated = copy.deepcopy(data)
    updated["approvers"].append(entry)
    return validate_approvers(updated), entry


def dump_approvers(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2) + "\n"
