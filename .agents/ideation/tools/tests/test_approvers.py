from __future__ import annotations

import base64
import copy
import json

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from ideation_tools.approvers import (
    DEFAULT_APPROVERS_PATH, add_approver, key_fingerprint, load_approvers, validate_approvers,
)
from ideation_tools.cli import main
from ideation_tools.errors import ValidationRejected

from test_approval import decision_tx


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def spki(curve=ec.SECP256R1()) -> bytes:
    key = ec.generate_private_key(curve)
    return key.public_key().public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)


def empty_approvers() -> dict:
    return {
        "schema_version": 1,
        "rp_id": "example.test",
        "origin": "https://example.test",
        "approval_page_url": "https://example.test/approve/",
        "approvers": [],
    }


def record_code(public_key: bytes | None = None, **overrides) -> str:
    record = {
        "schema_version": 1, "kind": "ideation_approver", "approver": "Tester", "rp_id": "example.test",
        "credential_id": "cred-1", "public_key_spki": b64url(public_key or spki()), "algorithm": -7,
    }
    record.update(overrides)
    return b64url(json.dumps(record).encode("utf-8"))


def with_one_approver() -> dict:
    data, _ = add_approver(empty_approvers(), record_code(), added_at="2026-09-23")
    return data


def test_committed_approvers_file_is_valid():
    assert load_approvers(DEFAULT_APPROVERS_PATH)["rp_id"] == "ras207.github.io"


def test_fingerprint_format_is_stable():
    assert key_fingerprint(b"abc") == "BA78-16BF-8F01-CFEA"


def test_add_approver_appends_entry_with_fingerprint():
    key = spki()
    data, entry = add_approver(empty_approvers(), record_code(key), added_at="2026-09-23")
    assert data["approvers"] == [entry]
    assert entry["fingerprint"] == key_fingerprint(key)
    assert entry["added_at"] == "2026-09-23"


def test_add_approver_does_not_modify_input():
    original = empty_approvers()
    add_approver(original, record_code(), added_at="2026-09-23")
    assert original["approvers"] == []


@pytest.mark.parametrize("code", [
    "not base64 json!",
    b64url(b"[1, 2]"),
    record_code(kind="ideation_approval"),
    record_code(rp_id="evil.test"),
    record_code(algorithm=-257),
    record_code(public_key=spki(ec.SECP384R1())),
    record_code(public_key_spki=b64url(b"not a key")),
])
def test_add_approver_rejects_bad_records(code):
    with pytest.raises(ValidationRejected):
        add_approver(empty_approvers(), code, added_at="2026-09-23")


def test_duplicate_credential_rejected():
    with pytest.raises(ValidationRejected, match="Duplicate"):
        add_approver(with_one_approver(), record_code(), added_at="2026-09-23")


def mutate(change) -> dict:
    data = copy.deepcopy(with_one_approver())
    change(data)
    return data


@pytest.mark.parametrize("data", [
    mutate(lambda d: d["approvers"][0].update(fingerprint="0000-0000-0000-0000")),
    mutate(lambda d: d["approvers"][0].update(public_key_spki=b64url(spki()))),
    mutate(lambda d: d.update(origin="https://other.test")),
    mutate(lambda d: d.update(approval_page_url="https://other.test/approve/")),
    mutate(lambda d: d["approvers"][0].pop("added_at")),
    mutate(lambda d: d.update(extra="field")),
])
def test_invalid_approvers_file_rejected(data):
    with pytest.raises(ValidationRejected):
        validate_approvers(data)


def test_cli_add_approver_writes_file(tmp_path, capsys):
    path = tmp_path / "approvers.json"
    path.write_text(json.dumps(empty_approvers()), encoding="utf-8")
    key = spki()
    assert main(["add-approver", "--record", record_code(key), "--approvers", str(path)]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["fingerprint"] == key_fingerprint(key)
    assert load_approvers(path)["approvers"][0]["fingerprint"] == key_fingerprint(key)


def test_cli_add_approver_reports_error(tmp_path, capsys):
    path = tmp_path / "approvers.json"
    path.write_text(json.dumps(empty_approvers()), encoding="utf-8")
    assert main(["add-approver", "--record", record_code(rp_id="evil.test"), "--approvers", str(path)]) == 2
    assert "evil.test" in capsys.readouterr().err
    assert load_approvers(path)["approvers"] == []


def test_request_approval_defaults_page_url_from_approvers(tmp_path, capsys):
    path = tmp_path / "approvers.json"
    path.write_text(json.dumps(empty_approvers()), encoding="utf-8")
    tx_path = tmp_path / "tx.json"
    tx_path.write_text(json.dumps(decision_tx()), encoding="utf-8")
    assert main(["request-approval", "--transaction", str(tx_path), "--approvers", str(path)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output[0]["link"].startswith("https://example.test/approve/#")
