from __future__ import annotations

import pytest

from ideation_tools.errors import ValidationRejected
from ideation_tools.hashing import canonical_hash
from ideation_tools.migrations import migrate_state
from ideation_tools.normalization import normalize_skill_result


def test_skill_normalization_preserves_provenance():
    result = {
        "schema_version": 1,
        "skill_id": "model-problem",
        "invocation_id": "inv-1",
        "status": "completed",
        "summary": "Modelled the problem",
        "payload": {},
        "unresolved_items": [],
        "state_change_proposals": [{
            "operation": "create", "section": "work_items", "record_id": "w1", "expected_revision": 3,
            "patch": {"id": "w1", "type": "question", "title": "Q", "status": "open", "blocking": False, "owner": "agent"},
            "rationale": "Need follow-up", "dependencies": [],
        }],
        "artifact_change_proposals": [],
        "human_escalation": None,
        "evidence_refs": [],
        "warnings": [],
    }
    tx = normalize_skill_result(result, project_id="demo", project_slug="demo", iteration=1, expected_revision=3)
    assert tx["source"]["source_hash"] == canonical_hash(result)
    assert tx["state_mutations"][0]["patch"] == result["state_change_proposals"][0]["patch"]
    assert tx["transaction_id"] == "skill:model-problem:inv-1"


def test_unknown_state_version_is_not_best_effort_migrated():
    with pytest.raises(ValidationRejected, match="No explicit deterministic migration"):
        migrate_state({"schema_version": 0})
