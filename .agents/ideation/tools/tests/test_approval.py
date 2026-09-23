from __future__ import annotations

import base64
import json

import pytest

from ideation_tools.approval import build_approval_requests
from ideation_tools.auth import mutation_action_hash
from ideation_tools.cli import main
from ideation_tools.errors import ValidationRejected
from ideation_tools.hashing import canonical_hash

PAGE_URL = "https://example.test/approve/"


def decision_tx(authorization_id: str | None = "auth-1") -> dict:
    return {
        "schema_version": 1,
        "transaction_id": "human:decision:1",
        "source": {"kind": "workflow_operation", "source_id": "human-decision", "skill_id": None, "source_hash": None},
        "project": {"project_id": "demo", "project_slug": "demo", "iteration": 1},
        "expected_revision": 1,
        "state_mutations": [
            {
                "operation": "update", "section": "workflow", "record_id": None,
                "patch": {"vision_status": "draft"}, "rationale": "Record draft vision", "dependencies": [], "authorization_id": None,
            },
            {
                "operation": "create", "section": "decisions", "record_id": "dec-1",
                "patch": {"id": "dec-1", "question": "Proceed?", "decision": "Yes", "authority": "human", "status": "settled"},
                "rationale": "Human decided", "dependencies": [], "authorization_id": authorization_id,
            },
        ],
        "artifact_changes": [],
        "summary": "Record human decision",
    }


def decode_link(link: str) -> dict:
    fragment = link.split("#", 1)[1]
    return json.loads(base64.urlsafe_b64decode(fragment + "=" * (-len(fragment) % 4)))


def test_request_only_for_mutations_needing_human_authorization():
    requests = build_approval_requests(decision_tx(), page_url=PAGE_URL)
    assert len(requests) == 1
    assert requests[0]["authorization_id"] == "auth-1"
    assert requests[0]["action"]["record_id"] == "dec-1"


def test_action_hash_matches_coordinator_binding_and_is_recomputable():
    tx = decision_tx()
    request = build_approval_requests(tx, page_url=PAGE_URL)[0]
    assert request["action_hash"] == mutation_action_hash(tx, tx["state_mutations"][1])
    # The approval page must be able to recompute the hash from the action alone.
    assert canonical_hash(request["action"]) == request["action_hash"]


def test_link_carries_payload_in_fragment():
    request = build_approval_requests(decision_tx(), page_url=PAGE_URL)[0]
    assert request["link"].startswith(PAGE_URL + "#")
    payload = decode_link(request["link"])
    assert payload["action_hash"] == request["action_hash"]
    assert payload["action"] == request["action"]
    assert "link" not in payload and "description" not in payload


def test_description_shows_signed_patch_fields():
    request = build_approval_requests(decision_tx(), page_url=PAGE_URL)[0]
    assert "create decisions record dec-1" in request["description"][0]
    assert "  decision: Yes" in request["description"]


def test_missing_authorization_id_is_rejected():
    with pytest.raises(ValidationRejected):
        build_approval_requests(decision_tx(authorization_id=None), page_url=PAGE_URL)


def test_cli_request_approval(tmp_path, capsys):
    tx_path = tmp_path / "tx.json"
    tx_path.write_text(json.dumps(decision_tx()), encoding="utf-8")
    assert main(["request-approval", "--transaction", str(tx_path), "--page-url", PAGE_URL]) == 0
    output = json.loads(capsys.readouterr().out)
    assert [r["authorization_id"] for r in output] == ["auth-1"]
