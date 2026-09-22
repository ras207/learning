from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from ideation_tools.backends.local_git import LocalGitBackend
from ideation_tools.content_store import ContentStore
from ideation_tools.coordinator import TransactionCoordinator


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def base_state(slug: str = "demo") -> dict:
    return {
        "schema_version": 1,
        "project": {
            "project_id": slug,
            "project_slug": slug,
            "iteration": 1,
            "revision": 1,
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        },
        "agent_provenance": {"repository_commit": "0" * 40},
        "workflow": {"status": "active", "vision_status": "not_started", "spine_context": "orient_and_initialize"},
        "session": {"status": "active", "checkpointed_at": None, "resume_summary": None, "pending_interaction_id": None},
        "routing": {"saved_focus_id": None},
        "artifacts": [],
        "decisions": [],
        "assumptions": [],
        "work_items": [],
        "evidence": [],
        "gate_evaluations": [],
        "finalization": {"outcome": None, "checks": [], "authorized_by_decision_id": None},
        "history": [],
    }


def init_tx(slug: str = "demo", txid: str = "workflow:init:1") -> dict:
    return {
        "schema_version": 1,
        "transaction_id": txid,
        "source": {"kind": "workflow_operation", "source_id": "initialize", "skill_id": None, "source_hash": None},
        "project": {"project_id": slug, "project_slug": slug, "iteration": 1},
        "expected_revision": 0,
        "state_mutations": [{
            "operation": "initialize", "section": "project", "record_id": None,
            "patch": base_state(slug), "rationale": "Initialize project state", "dependencies": [], "authorization_id": None,
        }],
        "artifact_changes": [],
        "summary": "Initialize ideation state",
    }


def context(repo: Path, content_store: Path, slug: str = "demo", *, head: str | None = None, authorizations=None) -> dict:
    head = head or git(repo, "rev-parse", "refs/heads/work")
    return {
        "schema_version": 1,
        "trust_mode": "local_harness",
        "run_id": "run-1",
        "actor": "test-harness",
        "project_id": slug,
        "project_slug": slug,
        "iteration": 1,
        "authorized_ref": "refs/heads/work",
        "expected_head_sha": head,
        "content_store_root": str(content_store),
        "policy_version": 1,
        "human_authorizations": authorizations or [],
    }


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    r = tmp_path / "repo"
    r.mkdir()
    subprocess.check_call(["git", "init", "-q", str(r)])
    git(r, "config", "user.name", "Tester")
    git(r, "config", "user.email", "tester@example.com")
    (r / "README.md").write_text("base\n", encoding="utf-8")
    git(r, "add", "README.md")
    git(r, "commit", "-q", "-m", "base")
    git(r, "branch", "work")
    return r


@pytest.fixture
def content_store(tmp_path: Path) -> Path:
    p = tmp_path / "content"
    p.mkdir()
    return p


@pytest.fixture
def coordinator(repo: Path) -> TransactionCoordinator:
    return TransactionCoordinator(LocalGitBackend(repo))


@pytest.fixture
def initialized(repo: Path, content_store: Path, coordinator: TransactionCoordinator):
    result = coordinator.execute(init_tx(), context(repo, content_store))
    assert result["status"] == "applied", result
    return result
