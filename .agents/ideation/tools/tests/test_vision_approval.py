"""Gate 6 approval must be bound to the vision text the human actually approved."""
from __future__ import annotations

import pytest
import yaml

from ideation_tools.auth import mutation_action_hash
from ideation_tools.backends.local_git import LocalGitBackend
from ideation_tools.content_store import ContentStore
from ideation_tools.hashing import sha256_bytes, vision_content_fingerprint
from ideation_tools.reverify import verify_project

from conftest import context, git

VISION_PATH = "projects/demo/ideation/vision.md"
CANDIDATE = b"---\nstatus: candidate\nversion: 0.1\n---\n# Vision\n\nHelp learners keep what they learn.\n"
APPROVED = CANDIDATE.replace(b"status: candidate", b"status: approved")
ALTERED = APPROVED.replace(b"keep what they learn", b"forget what they learn")


class Project:
    """Drives the demo project through the coordinator one transaction at a time."""

    def __init__(self, repo, content_store, coordinator):
        self.repo = repo
        self.content_store = content_store
        self.coordinator = coordinator
        self.store = ContentStore(content_store)
        self.revision = 1
        self.count = 0

    def apply(self, mutations, *, artifact_changes=(), authorizations=None, summary="Test step"):
        self.count += 1
        tx = {
            "schema_version": 1,
            "transaction_id": f"test:vision:{self.count}",
            "source": {"kind": "workflow_operation", "source_id": f"step-{self.count}", "skill_id": None, "source_hash": None},
            "project": {"project_id": "demo", "project_slug": "demo", "iteration": 1},
            "expected_revision": self.revision,
            "state_mutations": [
                {"record_id": None, "rationale": summary, "dependencies": [], "authorization_id": None, **m} for m in mutations
            ],
            "artifact_changes": list(artifact_changes),
            "summary": summary,
        }
        auths = [
            {
                "authorization_id": m["authorization_id"], "project_id": "demo", "iteration": 1,
                "transaction_id": tx["transaction_id"], "action_hash": mutation_action_hash(tx, m),
                "actor": "ross", "issued_at": "2026-01-01T00:00:00Z",
            }
            for m in tx["state_mutations"] if m["authorization_id"]
        ]
        result = self.coordinator.execute(tx, context(self.repo, self.content_store, authorizations=auths))
        if result["status"] == "applied":
            self.revision += 1
        return result

    def vision_change(self, data: bytes, status: str) -> dict:
        existing = LocalGitBackend(self.repo).read_file(git(self.repo, "rev-parse", "refs/heads/work"), VISION_PATH)
        return {
            "artifact_id": "vision", "path": VISION_PATH, "operation": "create" if existing is None else "update",
            "content_ref": self.store.put(data), "expected_fingerprint": None if existing is None else sha256_bytes(existing),
            "role": "vision", "status": status, "rationale": "Write vision",
        }

    def state(self) -> dict:
        head = git(self.repo, "rev-parse", "refs/heads/work")
        return yaml.safe_load(LocalGitBackend(self.repo).read_file(head, "projects/demo/ideation/state.yaml"))


def gate(gate_id: int, **extra) -> dict:
    record = {"id": f"gate-{gate_id}", "gate_id": gate_id, "gate_name": f"Gate {gate_id}", "gate_class": "hard",
              "outcome": "PASS", "validity": "current", **extra}
    return {"operation": "create", "section": "gate_evaluations", "record_id": record["id"], "patch": record}


APPROVAL = {"id": "dec-approve-vision", "question": "Approve the vision?", "decision": "Approved",
            "authority": "human", "status": "settled", "vision_fingerprint": vision_content_fingerprint(CANDIDATE)}


def approve_vision(project: Project, approval: dict = APPROVAL) -> dict:
    """Candidate vision, gates 1-5, the human's signed approval decision, then a passing Gate 6.

    Returns the result of recording Gate 6, which the invariants decide.
    """
    steps = [
        dict(mutations=[{"operation": "update", "section": "workflow", "patch": {"vision_status": "candidate"}}],
             artifact_changes=[project.vision_change(CANDIDATE, "candidate")], summary="Write candidate vision"),
        dict(mutations=[gate(i) for i in range(1, 6)], summary="Record gates 1-5"),
        dict(mutations=[{
            "operation": "create", "section": "decisions", "record_id": "dec-approve-vision",
            "patch": approval,
            "authorization_id": "auth-approve-vision",
        }], summary="Record human approval of the vision"),
    ]
    for step in steps:
        result = project.apply(**step)
        assert result["status"] == "applied", result
    return project.apply([gate(6, human_decision_ids=["dec-approve-vision"])], summary="Record Gate 6")


def finalize(project: Project, vision: bytes) -> dict:
    return project.apply(
        [{"operation": "finalize_approved", "section": "finalization",
          "patch": {"checks": [], "authorized_by_decision_id": "dec-approve-vision"}}],
        artifact_changes=[project.vision_change(vision, "approved")],
        summary="Finalize approved vision",
    )


@pytest.fixture
def project(repo, content_store, coordinator, initialized) -> Project:
    return Project(repo, content_store, coordinator)


def test_approved_vision_can_be_finalized(project):
    assert approve_vision(project)["status"] == "applied"
    result = finalize(project, APPROVED)
    assert result["status"] == "applied", result
    assert project.state()["workflow"]["status"] == "approved"


def test_finalizing_a_vision_changed_after_approval_is_rejected(project):
    assert approve_vision(project)["status"] == "applied"
    result = finalize(project, ALTERED)
    assert result["status"] == "rejected"
    assert "INV-004" in result["message"] and "changed since the human approved it" in result["message"]


def test_changing_an_approved_vision_is_rejected(project):
    assert approve_vision(project)["status"] == "applied"
    assert finalize(project, APPROVED)["status"] == "applied"
    result = project.apply(
        [{"operation": "update", "section": "workflow", "patch": {"spine_context": "finalize_handoff"}}],
        artifact_changes=[project.vision_change(ALTERED, "approved")],
        summary="Edit approved vision",
    )
    assert result["status"] == "rejected"
    assert "INV-004" in result["message"]


def test_gate6_approval_without_vision_fingerprint_is_rejected(project):
    approval = {k: v for k, v in APPROVAL.items() if k != "vision_fingerprint"}
    result = approve_vision(project, approval)
    assert result["status"] == "rejected"
    assert "does not record the vision_fingerprint" in result["message"]


def test_gate6_approval_of_a_different_vision_is_rejected(project):
    result = approve_vision(project, {**APPROVAL, "vision_fingerprint": vision_content_fingerprint(ALTERED)})
    assert result["status"] == "rejected"
    assert "changed since the human approved it" in result["message"]


def test_changing_the_vision_while_gate6_passes_is_rejected(project):
    assert approve_vision(project)["status"] == "applied"
    result = project.apply(
        [{"operation": "update", "section": "workflow", "patch": {"vision_status": "candidate"}}],
        artifact_changes=[project.vision_change(ALTERED, "candidate")],
        summary="Revise vision without re-evaluating Gate 6",
    )
    assert result["status"] == "rejected"
    assert "INV-004" in result["message"]


def test_revising_the_vision_requires_a_new_approval(project):
    assert approve_vision(project)["status"] == "applied"
    revised = ALTERED.replace(b"status: approved", b"status: candidate")
    result = project.apply(
        [{"operation": "invalidate", "section": "gate_evaluations", "record_id": "gate-6", "patch": {}}],
        artifact_changes=[project.vision_change(revised, "candidate")],
        summary="Revise vision and invalidate Gate 6",
    )
    assert result["status"] == "applied", result
    assert finalize(project, ALTERED)["status"] == "rejected"


def test_verify_approvals_catches_a_vision_edited_outside_the_tools(project, tmp_path):
    assert approve_vision(project)["status"] == "applied"
    assert finalize(project, APPROVED)["status"] == "applied"
    project_dir = tmp_path / "checkout" / "projects" / "demo" / "ideation"
    project_dir.mkdir(parents=True)
    head = git(project.repo, "rev-parse", "refs/heads/work")
    backend = LocalGitBackend(project.repo)
    (project_dir / "state.yaml").write_bytes(backend.read_file(head, "projects/demo/ideation/state.yaml"))
    (project_dir / "vision.md").write_bytes(ALTERED)

    problems = verify_project(project_dir, {"approvers": []})
    assert any("INV-004" in p and "changed since the human approved it" in p for p in problems), problems
