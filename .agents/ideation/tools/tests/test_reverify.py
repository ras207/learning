from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import yaml

from ideation_tools.approvers import add_approver, load_approvers
from ideation_tools.auth import mutation_action_hash
from ideation_tools.cli import main
from ideation_tools.reverify import verify_project, verify_repository
from ideation_tools.passkey import approval_evidence, build_authorization

from conftest import git
from test_approval import decision_tx
from test_approvers import empty_approvers
from test_passkey import FakePasskey, approvers, approvers_path, passkey_context, passkey_coordinator, phone  # noqa: F401  (fixtures)

REPO_ROOT = Path(__file__).resolve().parents[4]
PROJECT = Path("projects/demo/ideation")


@pytest.fixture
def approved(repo, content_store, phone, approvers, passkey_coordinator) -> Path:
    """A checked-out repo whose demo project holds one passkey-approved human decision."""
    tx = decision_tx()
    auth, _ = build_authorization(tx, phone.approval_code("auth-1", mutation_action_hash(tx, tx["state_mutations"][1])),
                                  approvers, issued_at="now")
    result = passkey_coordinator.execute(tx, passkey_context(repo, content_store, [auth]))
    assert result["status"] == "applied", result
    git(repo, "checkout", "-q", "work")
    return repo


def edit_state(repo: Path, change) -> None:
    path = repo / PROJECT / "state.yaml"
    state = yaml.safe_load(path.read_text(encoding="utf-8"))
    change(state)
    path.write_text(yaml.safe_dump(state, sort_keys=False), encoding="utf-8")


def edit_evidence(repo: Path, change, name: str = "auth-1.json") -> None:
    path = repo / PROJECT / "approvals" / name
    record = json.loads(path.read_text(encoding="utf-8"))
    change(record)
    path.write_text(json.dumps(record), encoding="utf-8")


def problems(repo: Path, approvers: dict) -> list[str]:
    return verify_project(repo / PROJECT, approvers)


def test_committed_projects_pass():
    results = verify_repository(REPO_ROOT, load_approvers())
    assert results, "expected at least one committed project"
    assert all(not p for p in results.values()), results


def test_approved_decision_passes(approved, approvers):
    assert problems(approved, approvers) == []


def test_state_without_approvals_passes(repo, passkey_coordinator, approvers):
    git(repo, "checkout", "-q", "work")
    assert problems(repo, approvers) == []


def test_decision_edited_after_approval(approved, approvers):
    edit_state(approved, lambda s: s["decisions"][0].update(decision="No"))
    assert any("changed after approval (decision)" in p for p in problems(approved, approvers))


def test_decision_added_directly_without_approval(approved, approvers):
    def add(state):
        state["decisions"].append({**copy.deepcopy(state["decisions"][0]), "id": "dec-forged", "authorization_id": None})
    edit_state(approved, add)
    assert any("dec-forged: settled human decision has no verified approval" in p for p in problems(approved, approvers))


def test_evidence_deleted(approved, approvers):
    (approved / PROJECT / "approvals" / "auth-1.json").unlink()
    found = problems(approved, approvers)
    assert any("has no approval evidence" in p for p in found)
    assert any("has no verified approval" in p for p in found)


def test_evidence_signature_tampered(approved, approvers):
    def tamper(record):
        sig = record["passkey"]["signature"]
        record["passkey"]["signature"] = sig[:-2] + ("AA" if sig[-2:] != "AA" else "BB")
    edit_evidence(approved, tamper)
    assert any("auth-1:" in p and "signature" in p for p in problems(approved, approvers))


def test_signed_fields_edited_in_evidence(approved, approvers):
    edit_evidence(approved, lambda r: r["action"]["patch"].update(decision="No"))
    assert any("do not match the recorded action hash" in p for p in problems(approved, approvers))


def test_key_only_in_pr_approvers_is_not_trusted(approved, approvers):
    # The PR's own approvers.json might list the signing key; CI checks against main's copy instead.
    main_approvers, _ = add_approver(empty_approvers(), FakePasskey("main-key").registration_code(), added_at="2026-09-23")
    assert any("not a registered approver" in p for p in problems(approved, main_approvers))


def test_valid_signature_for_another_transaction(approved, phone, approvers):
    other = decision_tx()
    other["transaction_id"] = "human:decision:other"
    mutation = other["state_mutations"][1]
    auth, entry = build_authorization(other, phone.approval_code("auth-1", mutation_action_hash(other, mutation)),
                                      approvers, issued_at="now")
    auth["approver_fingerprint"] = entry["fingerprint"]
    path = approved / PROJECT / "approvals" / "auth-1.json"
    path.write_text(json.dumps(approval_evidence(other, mutation, auth)), encoding="utf-8")
    assert any("different transaction" in p for p in problems(approved, approvers))


def test_evidence_for_another_project(approved, approvers):
    edit_evidence(approved, lambda r: r["action"]["project"].update(project_id="other"))
    assert any("different project" in p for p in problems(approved, approvers))


def test_orphan_evidence_flagged(approved, approvers):
    source = approved / PROJECT / "approvals" / "auth-1.json"
    record = json.loads(source.read_text(encoding="utf-8"))
    record["authorization_id"] = "auth-9"
    (approved / PROJECT / "approvals" / "auth-9.json").write_text(json.dumps(record), encoding="utf-8")
    assert any("auth-9: evidence is not referenced" in p for p in problems(approved, approvers))


def test_evidence_file_name_mismatch(approved, approvers):
    (approved / PROJECT / "approvals" / "auth-1.json").rename(approved / PROJECT / "approvals" / "other.json")
    assert any("does not match authorization_id" in p for p in problems(approved, approvers))


def test_invalid_state_reported(approved, approvers):
    edit_state(approved, lambda s: s["project"].update(revision="two"))
    assert problems(approved, approvers)[0].startswith("state.yaml:")


def test_cli_verify_approvals(approved, approvers_path, capsys):
    assert main(["verify-approvals", "--root", str(approved), "--approvers", str(approvers_path)]) == 0
    assert "ok   demo" in capsys.readouterr().out
    edit_state(approved, lambda s: s["decisions"][0].update(decision="No"))
    assert main(["verify-approvals", "--root", str(approved), "--approvers", str(approvers_path)]) == 1
    assert "FAIL demo" in capsys.readouterr().out
