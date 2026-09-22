from __future__ import annotations

from typing import Any

from .state import utc_now


def build_initial_state(*, project_id: str, project_slug: str, agent_fingerprint: str) -> dict[str, Any]:
    """Build the deterministic revision-1 state for a minimal-seed project.

    This function performs no qualitative interpretation of PROJECT.md.
    """
    now = utc_now()
    return {
        "schema_version": 1,
        "project": {
            "project_id": project_id,
            "project_slug": project_slug,
            "iteration": 1,
            "revision": 1,
            "created_at": now,
            "updated_at": now,
        },
        "workflow": {
            "status": "active",
            "vision_status": "not_started",
            "spine_context": "orient_and_initialize",
        },
        "session": {
            "status": "paused",
            "checkpointed_at": now,
            "resume_summary": "Project deterministically initialized from minimal seed; ideation has not begun.",
            "pending_interaction_id": None,
        },
        "routing": {"saved_focus_id": None},
        "artifacts": [
            {
                "artifact_id": "agent:ideation",
                "role": "agent_provenance",
                "path": ".agents/ideation",
                "status": "reference",
                "fingerprint": {"algorithm": "git-commit", "value": agent_fingerprint},
                "repository_commit": agent_fingerprint,
                "last_verified_at": now,
            }
        ],
        "decisions": [],
        "assumptions": [],
        "work_items": [],
        "evidence": [],
        "gate_evaluations": [],
        "finalization": {"outcome": None, "checks": [], "authorized_by_decision_id": None},
        "history": [],
    }


def build_initialization_transaction(
    *, project_id: str, project_slug: str, agent_fingerprint: str, transaction_id: str
) -> dict[str, Any]:
    state = build_initial_state(
        project_id=project_id,
        project_slug=project_slug,
        agent_fingerprint=agent_fingerprint,
    )
    return {
        "schema_version": 1,
        "transaction_id": transaction_id,
        "source": {
            "kind": "workflow_operation",
            "source_id": "initialize_project",
            "skill_id": None,
            "source_hash": None,
        },
        "project": {"project_id": project_id, "project_slug": project_slug, "iteration": 1},
        "expected_revision": 0,
        "state_mutations": [{
            "operation": "initialize",
            "section": "project",
            "record_id": None,
            "patch": state,
            "rationale": "Deterministically initialize project from minimal seed",
            "dependencies": [],
            "authorization_id": None,
        }],
        "artifact_changes": [],
        "summary": "Initialize ideation project",
    }
