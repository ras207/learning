from __future__ import annotations

import copy
from typing import Any, Callable

from .hashing import canonical_hash
from .schema import validate


def normalize_skill_result(
    skill_result: dict[str, Any],
    *,
    project_id: str,
    project_slug: str,
    iteration: int,
    expected_revision: int,
    resolve_content_ref: Callable[[str], str] | None = None,
) -> dict[str, Any]:
    """Deterministically adapt one skill result into the canonical transaction shape.

    `resolve_content_ref` may convert a source-local immutable reference into the
    canonical sha256:<digest> form. It must not change the referenced bytes.
    """
    source_hash = canonical_hash(skill_result)
    mutations = []
    for proposal in skill_result.get("state_change_proposals", []):
        mutations.append({
            "operation": proposal["operation"],
            "section": proposal["section"],
            "record_id": proposal.get("record_id"),
            "patch": copy.deepcopy(proposal["patch"]),
            "rationale": proposal["rationale"],
            "dependencies": list(proposal.get("dependencies", [])),
            "authorization_id": None,
        })
    artifacts = []
    for proposal in skill_result.get("artifact_change_proposals", []):
        ref = proposal["proposed_content_ref"]
        if resolve_content_ref:
            ref = resolve_content_ref(ref)
        artifacts.append({
            "artifact_id": proposal["artifact_id"],
            "path": proposal["path"],
            "operation": proposal["operation"],
            "content_ref": ref,
            "expected_fingerprint": proposal.get("expected_fingerprint"),
            "role": "project_artifact",
            "status": "current",
            "rationale": proposal["rationale"],
        })
    tx = {
        "schema_version": 1,
        "transaction_id": f"skill:{skill_result['skill_id']}:{skill_result['invocation_id']}",
        "source": {
            "kind": "skill_result",
            "source_id": skill_result["invocation_id"],
            "skill_id": skill_result["skill_id"],
            "source_hash": source_hash,
        },
        "project": {"project_id": project_id, "project_slug": project_slug, "iteration": iteration},
        "expected_revision": expected_revision,
        "state_mutations": mutations,
        "artifact_changes": artifacts,
        "summary": skill_result["summary"],
    }
    validate(tx, "transaction-proposal.schema.json")
    return tx


def build_workflow_transaction(
    *,
    transaction_id: str,
    source_id: str,
    project: dict[str, Any],
    expected_revision: int,
    state_mutations: list[dict[str, Any]],
    artifact_changes: list[dict[str, Any]],
    summary: str,
) -> dict[str, Any]:
    tx = {
        "schema_version": 1,
        "transaction_id": transaction_id,
        "source": {"kind": "workflow_operation", "source_id": source_id, "skill_id": None, "source_hash": None},
        "project": copy.deepcopy(project),
        "expected_revision": expected_revision,
        "state_mutations": copy.deepcopy(state_mutations),
        "artifact_changes": copy.deepcopy(artifact_changes),
        "summary": summary,
    }
    validate(tx, "transaction-proposal.schema.json")
    return tx
