from __future__ import annotations

import copy
import subprocess

import yaml

from ideation_tools.auth import mutation_action_hash
from ideation_tools.backends.local_git import LocalGitBackend
from ideation_tools.content_store import ContentStore
from ideation_tools.coordinator import TransactionCoordinator
from ideation_tools.hashing import canonical_hash, sha256_bytes

from conftest import context, git, init_tx


def test_dry_run_does_not_advance_ref(repo, content_store, coordinator):
    before = git(repo, "rev-parse", "refs/heads/work")
    result = coordinator.execute(init_tx(), context(repo, content_store), dry_run=True)
    assert result["status"] == "validated"
    assert git(repo, "rev-parse", "refs/heads/work") == before
    assert LocalGitBackend(repo).read_file(before, "projects/demo/ideation/state.yaml") is None


def test_apply_initialization_is_atomic_and_verified(repo, content_store, coordinator):
    before = git(repo, "rev-parse", "refs/heads/work")
    result = coordinator.execute(init_tx(), context(repo, content_store))
    assert result["status"] == "applied"
    assert result["commit_sha"] != before
    raw = LocalGitBackend(repo).read_file(result["commit_sha"], "projects/demo/ideation/state.yaml")
    state = yaml.safe_load(raw)
    assert state["project"]["revision"] == 1
    assert state["history"][-1]["transaction_id"] == "workflow:init:1"


def test_artifact_commit_does_not_touch_working_tree(repo, content_store, coordinator, initialized):
    dirty = repo / "local-note.txt"
    dirty.write_text("uncommitted\n", encoding="utf-8")
    store = ContentStore(content_store)
    vision = b"---\nstatus: draft\nversion: 0.1\n---\n# Vision\n"
    ref = store.put(vision)
    head = git(repo, "rev-parse", "refs/heads/work")
    tx = {
        "schema_version": 1,
        "transaction_id": "skill:synthesize-vision:1",
        "source": {"kind": "skill_result", "source_id": "1", "skill_id": "synthesize-vision", "source_hash": "0" * 64},
        "project": {"project_id": "demo", "project_slug": "demo", "iteration": 1},
        "expected_revision": 1,
        "state_mutations": [{
            "operation": "update", "section": "workflow", "record_id": None,
            "patch": {"vision_status": "draft"}, "rationale": "Record draft vision", "dependencies": [], "authorization_id": None,
        }],
        "artifact_changes": [{
            "artifact_id": "vision", "path": "projects/demo/ideation/vision.md", "operation": "create",
            "content_ref": ref, "expected_fingerprint": None, "role": "vision", "status": "draft", "rationale": "Write draft vision",
        }],
        "summary": "Persist synthesized vision",
    }
    result = coordinator.execute(tx, context(repo, content_store, head=head))
    assert result["status"] == "applied", result
    assert dirty.read_text() == "uncommitted\n"
    assert "local-note.txt" in subprocess.check_output(["git", "-C", str(repo), "status", "--porcelain"], text=True)
    raw = LocalGitBackend(repo).read_file(result["commit_sha"], "projects/demo/ideation/vision.md")
    assert raw == vision


def test_stale_head_is_conflict(repo, content_store, coordinator, initialized):
    stale = initialized["base_sha"]
    tx = copy.deepcopy(init_tx(txid="workflow:other:1"))
    tx["expected_revision"] = 1
    tx["state_mutations"] = [{
        "operation": "update", "section": "workflow", "record_id": None, "patch": {"spine_context": "capture_intent"},
        "rationale": "Move context", "dependencies": [], "authorization_id": None,
    }]
    result = coordinator.execute(tx, context(repo, content_store, head=stale))
    assert result["status"] == "conflict"


def test_replay_is_idempotent(repo, content_store, coordinator):
    tx = init_tx()
    ctx = context(repo, content_store)
    first = coordinator.execute(tx, ctx)
    assert first["status"] == "applied"
    replay_ctx = context(repo, content_store, head=ctx["expected_head_sha"])
    second = coordinator.execute(tx, replay_ctx)
    assert second["status"] == "applied"
    assert second["commit_sha"] == first["commit_sha"]
    assert git(repo, "rev-list", "--count", "refs/heads/work") == "2"


def test_transaction_id_reuse_with_different_content_is_rejected(repo, content_store, coordinator):
    first = coordinator.execute(init_tx(), context(repo, content_store))
    assert first["status"] == "applied"
    tx = init_tx()
    tx["summary"] = "Different content"
    result = coordinator.execute(tx, context(repo, content_store))
    assert result["status"] == "rejected"
    assert "different content" in result["message"]


def test_protected_main_is_rejected(repo, content_store, coordinator):
    tx = init_tx()
    ctx = context(repo, content_store)
    ctx["authorized_ref"] = "refs/heads/main" if subprocess.run(["git", "-C", str(repo), "show-ref", "--verify", "refs/heads/main"], capture_output=True).returncode == 0 else "refs/heads/master"
    ctx["expected_head_sha"] = git(repo, "rev-parse", ctx["authorized_ref"])
    result = coordinator.execute(tx, ctx)
    assert result["status"] == "rejected"
    assert "Protected ref" in result["message"]


def test_content_hash_mismatch_rejected(repo, content_store, coordinator, initialized):
    bad_digest = "1" * 64
    (content_store / bad_digest).write_bytes(b"not matching")
    tx = {
        "schema_version": 1,
        "transaction_id": "artifact:bad",
        "source": {"kind": "workflow_operation", "source_id": "bad", "skill_id": None, "source_hash": None},
        "project": {"project_id": "demo", "project_slug": "demo", "iteration": 1},
        "expected_revision": 1,
        "state_mutations": [],
        "artifact_changes": [{
            "artifact_id": "a", "path": "projects/demo/ideation/a.md", "operation": "create",
            "content_ref": f"sha256:{bad_digest}", "expected_fingerprint": None, "role": "note", "status": "current", "rationale": "test",
        }],
        "summary": "Bad content",
    }
    result = coordinator.execute(tx, context(repo, content_store))
    assert result["status"] == "rejected"


def test_human_decision_requires_action_bound_authorization(repo, content_store, coordinator, initialized):
    tx = {
        "schema_version": 1,
        "transaction_id": "human:decision:1",
        "source": {"kind": "workflow_operation", "source_id": "human-decision", "skill_id": None, "source_hash": None},
        "project": {"project_id": "demo", "project_slug": "demo", "iteration": 1},
        "expected_revision": 1,
        "state_mutations": [{
            "operation": "create", "section": "decisions", "record_id": "dec-1",
            "patch": {"id": "dec-1", "question": "Proceed?", "decision": "Yes", "authority": "human", "status": "settled"},
            "rationale": "Human decided", "dependencies": [], "authorization_id": "auth-1",
        }],
        "artifact_changes": [],
        "summary": "Record human decision",
    }
    no_auth = coordinator.execute(tx, context(repo, content_store))
    assert no_auth["status"] == "rejected"

    auth = {
        "authorization_id": "auth-1", "project_id": "demo", "iteration": 1, "transaction_id": tx["transaction_id"],
        "action_hash": mutation_action_hash(tx, tx["state_mutations"][0]), "actor": "ross", "issued_at": "2026-01-01T00:00:00Z",
    }
    ok = coordinator.execute(tx, context(repo, content_store, authorizations=[auth]))
    assert ok["status"] == "applied", ok
    state = yaml.safe_load(LocalGitBackend(repo).read_file(ok["commit_sha"], "projects/demo/ideation/state.yaml"))
    assert state["decisions"][0]["authorization_id"] == "auth-1"


def test_approved_invariant_rejects_missing_gate_assurance(repo, content_store, coordinator, initialized):
    tx = {
        "schema_version": 1,
        "transaction_id": "finalize:bad",
        "source": {"kind": "workflow_operation", "source_id": "finalize", "skill_id": None, "source_hash": None},
        "project": {"project_id": "demo", "project_slug": "demo", "iteration": 1},
        "expected_revision": 1,
        "state_mutations": [{
            "operation": "finalize_approved", "section": "finalization", "record_id": None,
            "patch": {"checks": [], "authorized_by_decision_id": "dec-x"}, "rationale": "Finalize", "dependencies": [], "authorization_id": None,
        }],
        "artifact_changes": [],
        "summary": "Invalid approval",
    }
    result = coordinator.execute(tx, context(repo, content_store))
    assert result["status"] == "rejected"
    assert "Invariant violation" in result["message"]


def test_write_boundary_rejected(repo, content_store, coordinator, initialized):
    store = ContentStore(content_store)
    ref = store.put(b"x")
    tx = {
        "schema_version": 1,
        "transaction_id": "boundary:1",
        "source": {"kind": "workflow_operation", "source_id": "boundary", "skill_id": None, "source_hash": None},
        "project": {"project_id": "demo", "project_slug": "demo", "iteration": 1},
        "expected_revision": 1,
        "state_mutations": [],
        "artifact_changes": [{
            "artifact_id": "bad", "path": "projects/other/ideation/a.md", "operation": "create",
            "content_ref": ref, "expected_fingerprint": None, "role": "note", "status": "current", "rationale": "bad",
        }],
        "summary": "Attempt cross-project write",
    }
    result = coordinator.execute(tx, context(repo, content_store))
    assert result["status"] == "rejected"


def test_malformed_transaction_returns_rejected(repo, content_store, coordinator):
    result = coordinator.execute({"transaction_id": "bad"}, context(repo, content_store))
    assert result["status"] == "rejected"
