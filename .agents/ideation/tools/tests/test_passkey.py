from __future__ import annotations

import copy
import hashlib
import json

import pytest
import yaml
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from ideation_tools.approvers import add_approver, b64url_decode, dump_approvers
from ideation_tools.auth import mutation_action_hash
from ideation_tools.backends.local_git import LocalGitBackend
from ideation_tools.cli import main
from ideation_tools.coordinator import TransactionCoordinator
from ideation_tools.errors import ValidationRejected
from ideation_tools.hashing import canonical_hash
from ideation_tools.passkey import PasskeyApprovalVerifier, build_authorization, verify_passkey_assertion

from conftest import context, git, init_tx
from test_approval import decision_tx
from test_approvers import b64url, empty_approvers, record_code


class FakePasskey:
    """Signs WebAuthn assertions exactly as a phone would, with a key generated for the test."""

    def __init__(self, credential_id: str = "cred-1"):
        self.credential_id = credential_id
        self.key = ec.generate_private_key(ec.SECP256R1())
        self.spki = self.key.public_key().public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)

    def registration_code(self) -> str:
        return record_code(self.spki, credential_id=self.credential_id)

    def assertion(self, action_hash: str, *, origin="https://example.test", rp_id="example.test", flags=0x05,
                  type_="webauthn.get", challenge: bytes | None = None, cross_origin=False) -> dict:
        client_data = json.dumps({
            "type": type_,
            "challenge": b64url(challenge if challenge is not None else bytes.fromhex(action_hash)),
            "origin": origin,
            "crossOrigin": cross_origin,
        }).encode("utf-8")
        auth_data = hashlib.sha256(rp_id.encode("utf-8")).digest() + bytes([flags]) + (0).to_bytes(4, "big")
        signature = self.key.sign(auth_data + hashlib.sha256(client_data).digest(), ec.ECDSA(hashes.SHA256()))
        return {
            "credential_id": self.credential_id,
            "authenticator_data": b64url(auth_data),
            "client_data_json": b64url(client_data),
            "signature": b64url(signature),
        }

    def approval_code(self, authorization_id: str, action_hash: str, **kwargs) -> str:
        approval = {"schema_version": 1, "kind": "ideation_approval", "authorization_id": authorization_id,
                    "action_hash": action_hash, **self.assertion(action_hash, **kwargs)}
        return b64url(json.dumps(approval).encode("utf-8"))


@pytest.fixture
def phone() -> FakePasskey:
    return FakePasskey()


@pytest.fixture
def approvers(phone) -> dict:
    data, _ = add_approver(empty_approvers(), phone.registration_code(), added_at="2026-09-23")
    return data


@pytest.fixture
def approvers_path(tmp_path, approvers):
    path = tmp_path / "approvers.json"
    path.write_text(dump_approvers(approvers), encoding="utf-8")
    return path


def passkey_context(repo, content_store, authorizations=None) -> dict:
    ctx = context(repo, content_store, authorizations=authorizations)
    ctx["trust_mode"] = "passkey"
    return ctx


ACTION_HASH = "ab" * 32


def test_valid_assertion_returns_approver(phone, approvers):
    entry = verify_passkey_assertion(ACTION_HASH, phone.assertion(ACTION_HASH), approvers)
    assert entry["approver"] == "Tester"


def tampered(assertion: dict, field: str, change) -> dict:
    result = dict(assertion)
    raw = bytearray(b64url_decode(result[field]))
    change(raw)
    result[field] = b64url(bytes(raw))
    return result


def flip_last_byte(raw: bytearray) -> None:
    raw[-1] ^= 0x01


@pytest.mark.parametrize("make, reason", [
    (lambda p: {**p.assertion(ACTION_HASH), "credential_id": "unknown"}, "not a registered approver"),
    (lambda p: FakePasskey().assertion(ACTION_HASH), "signature is invalid"),
    (lambda p: p.assertion(ACTION_HASH, challenge=bytes.fromhex("cd" * 32)), "different action"),
    (lambda p: p.assertion(ACTION_HASH, origin="https://evil.test"), "evil.test"),
    (lambda p: p.assertion(ACTION_HASH, cross_origin=True), "cross-origin"),
    (lambda p: p.assertion(ACTION_HASH, rp_id="evil.test"), "different site"),
    (lambda p: p.assertion(ACTION_HASH, flags=0x01), "Face ID"),
    (lambda p: p.assertion(ACTION_HASH, flags=0x04), "Face ID"),
    (lambda p: p.assertion(ACTION_HASH, type_="webauthn.create"), "not a WebAuthn authentication"),
    (lambda p: tampered(p.assertion(ACTION_HASH), "signature", flip_last_byte), "signature is invalid"),
    (lambda p: tampered(p.assertion(ACTION_HASH), "authenticator_data", flip_last_byte), "signature is invalid"),
])
def test_invalid_assertions_rejected(phone, approvers, make, reason):
    # FakePasskey() in the second case signs with an unregistered key under the registered credential ID.
    with pytest.raises(ValidationRejected, match=reason):
        verify_passkey_assertion(ACTION_HASH, make(phone), approvers)


def test_altered_client_data_after_signing_rejected(phone, approvers):
    assertion = phone.assertion(ACTION_HASH)
    client_data = json.loads(b64url_decode(assertion["client_data_json"]))
    client_data["extra"] = "added later"
    assertion["client_data_json"] = b64url(json.dumps(client_data).encode("utf-8"))
    with pytest.raises(ValidationRejected, match="signature is invalid"):
        verify_passkey_assertion(ACTION_HASH, assertion, approvers)


def test_build_authorization_binds_to_exact_mutation(phone, approvers):
    tx = decision_tx()
    action_hash = mutation_action_hash(tx, tx["state_mutations"][1])
    auth, entry = build_authorization(tx, phone.approval_code("auth-1", action_hash), approvers, issued_at="now")
    assert auth["action_hash"] == action_hash
    assert auth["actor"] == "Tester" == entry["approver"]
    assert auth["transaction_id"] == tx["transaction_id"]


def test_build_authorization_rejects_changed_mutation(phone, approvers):
    tx = decision_tx()
    code = phone.approval_code("auth-1", mutation_action_hash(tx, tx["state_mutations"][1]))
    tx["state_mutations"][1]["patch"]["decision"] = "No"
    with pytest.raises(ValidationRejected, match="different version"):
        build_authorization(tx, code, approvers, issued_at="now")


def test_build_authorization_rejects_unknown_authorization_id(phone, approvers):
    tx = decision_tx()
    code = phone.approval_code("auth-2", mutation_action_hash(tx, tx["state_mutations"][1]))
    with pytest.raises(ValidationRejected, match="auth-2"):
        build_authorization(tx, code, approvers, issued_at="now")


def test_verifier_rejects_local_harness_mode(repo, content_store, approvers_path):
    with pytest.raises(ValidationRejected, match="passkey"):
        PasskeyApprovalVerifier(approvers_path).verify(context(repo, content_store))


def test_verifier_takes_actor_from_key_not_caller(repo, content_store, phone, approvers, approvers_path):
    tx = decision_tx()
    auth, _ = build_authorization(tx, phone.approval_code("auth-1", mutation_action_hash(tx, tx["state_mutations"][1])),
                                  approvers, issued_at="now")
    auth["actor"] = "Someone Else"
    verified = PasskeyApprovalVerifier(approvers_path).verify(passkey_context(repo, content_store, [auth]))
    assert verified["human_authorizations"][0]["actor"] == "Tester"


@pytest.fixture
def passkey_coordinator(repo, content_store, approvers_path) -> TransactionCoordinator:
    coordinator = TransactionCoordinator(LocalGitBackend(repo), context_verifier=PasskeyApprovalVerifier(approvers_path))
    result = coordinator.execute(init_tx(), passkey_context(repo, content_store))
    assert result["status"] == "applied", result
    return coordinator


def test_approved_decision_commits_reverifiable_evidence(repo, content_store, phone, approvers, passkey_coordinator):
    tx = decision_tx()
    auth, _ = build_authorization(tx, phone.approval_code("auth-1", mutation_action_hash(tx, tx["state_mutations"][1])),
                                  approvers, issued_at="now")
    result = passkey_coordinator.execute(tx, passkey_context(repo, content_store, [auth]))
    assert result["status"] == "applied", result

    backend = LocalGitBackend(repo)
    state = yaml.safe_load(backend.read_file(result["commit_sha"], "projects/demo/ideation/state.yaml"))
    assert state["decisions"][0]["authorization_id"] == "auth-1"
    evidence = json.loads(backend.read_file(result["commit_sha"], "projects/demo/ideation/approvals/auth-1.json"))
    assert evidence["approver"] == "Tester"
    assert evidence["approver_fingerprint"] == approvers["approvers"][0]["fingerprint"]
    # Anyone holding the evidence and the approvers file can re-check it independently.
    assert canonical_hash(evidence["action"]) == evidence["action_hash"]
    verify_passkey_assertion(evidence["action_hash"], evidence["passkey"], approvers)


def test_unsigned_authorization_rejected(repo, content_store, passkey_coordinator):
    tx = decision_tx()
    forged = {
        "authorization_id": "auth-1", "project_id": "demo", "iteration": 1, "transaction_id": tx["transaction_id"],
        "action_hash": mutation_action_hash(tx, tx["state_mutations"][1]), "actor": "Tester", "issued_at": "now",
    }
    result = passkey_coordinator.execute(tx, passkey_context(repo, content_store, [forged]))
    assert result["status"] == "rejected"
    assert "no passkey signature" in result["message"]


def test_approval_cannot_be_reused(repo, content_store, phone, approvers, passkey_coordinator):
    tx = decision_tx()
    auth, _ = build_authorization(tx, phone.approval_code("auth-1", mutation_action_hash(tx, tx["state_mutations"][1])),
                                  approvers, issued_at="now")
    assert passkey_coordinator.execute(tx, passkey_context(repo, content_store, [auth]))["status"] == "applied"
    second = copy.deepcopy(tx)
    second["transaction_id"] = "human:decision:2"
    second["expected_revision"] = 2
    second["state_mutations"] = [dict(second["state_mutations"][1], record_id="dec-2",
                                      patch={**second["state_mutations"][1]["patch"], "id": "dec-2"})]
    result = passkey_coordinator.execute(second, passkey_context(repo, content_store, [auth]))
    assert result["status"] == "rejected"
    assert "consumed" in result["message"] or "different transaction" in result["message"], result["message"]


def write_json(path, data) -> str:
    path.write_text(json.dumps(data), encoding="utf-8")
    return str(path)


def test_cli_attach_then_apply(tmp_path, repo, content_store, phone, approvers_path, passkey_coordinator, capsys):
    tx = decision_tx()
    tx_path = write_json(tmp_path / "tx.json", tx)
    ctx_path = write_json(tmp_path / "ctx.json", passkey_context(repo, content_store))
    code = phone.approval_code("auth-1", mutation_action_hash(tx, tx["state_mutations"][1]))

    assert main(["attach-approval", "--transaction", tx_path, "--context", ctx_path, "--approval", code,
                 "--approvers", str(approvers_path)]) == 0
    assert "Valid approval from Tester" in capsys.readouterr().out

    assert main(["apply", "--repo", str(repo), "--transaction", tx_path, "--context", ctx_path,
                 "--approvers", str(approvers_path)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "applied"
    assert "projects/demo/ideation/approvals/auth-1.json" in git(repo, "show", "--name-only", "--format=", result["commit_sha"])


def test_cli_attach_rejects_bad_approval(tmp_path, repo, content_store, phone, approvers_path, capsys):
    tx = decision_tx()
    tx_path = write_json(tmp_path / "tx.json", tx)
    ctx_path = write_json(tmp_path / "ctx.json", passkey_context(repo, content_store))
    code = FakePasskey().approval_code("auth-1", mutation_action_hash(tx, tx["state_mutations"][1]))
    assert main(["attach-approval", "--transaction", tx_path, "--context", ctx_path, "--approval", code,
                 "--approvers", str(approvers_path)]) == 2
    assert "signature is invalid" in capsys.readouterr().err
    assert json.loads((tmp_path / "ctx.json").read_text())["human_authorizations"] == []


def test_cli_apply_refuses_local_harness(tmp_path, repo, content_store, approvers_path, capsys):
    tx_path = write_json(tmp_path / "tx.json", init_tx())
    ctx_path = write_json(tmp_path / "ctx.json", context(repo, content_store))
    assert main(["apply", "--repo", str(repo), "--transaction", tx_path, "--context", ctx_path,
                 "--approvers", str(approvers_path)]) == 2
    assert "passkey" in json.loads(capsys.readouterr().out)["message"]
