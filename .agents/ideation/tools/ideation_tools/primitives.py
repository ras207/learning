from __future__ import annotations

from typing import Any

from .backends.base import PersistenceBackend
from .content_store import ContentStore
from .errors import ValidationRejected
from .hashing import sha256_bytes
from .invariants import enforce_invariants
from .schema import validate
from .state import apply_mutation, validate_state


def validate_transaction(transaction: dict[str, Any]) -> None:
    validate(transaction, "transaction-proposal.schema.json")


def validate_state_snapshot(state: dict[str, Any]) -> None:
    validate_state(state)


def validate_policy_invariants(state: dict[str, Any], artifacts: dict[str, bytes]) -> list[dict[str, Any]]:
    return enforce_invariants(state, artifacts)


def validate_write_boundary(path: str, project_slug: str) -> None:
    prefix = f"projects/{project_slug}/ideation/"
    if not path.startswith(prefix):
        raise ValidationRejected(f"Path crosses project write boundary: {path}")


def fingerprint_artifact(data: bytes) -> str:
    return sha256_bytes(data)


def stage_state_change(state: dict[str, Any] | None, mutation: dict[str, Any]) -> dict[str, Any]:
    return apply_mutation(state, mutation)


def stage_artifact_change(content_store: ContentStore, content_ref: str) -> tuple[bytes, str]:
    data = content_store.resolve(content_ref)
    return data, fingerprint_artifact(data)


def commit_transaction(
    backend: PersistenceBackend,
    *,
    ref: str,
    expected_base_sha: str,
    files: dict[str, bytes],
    message: str,
) -> str:
    return backend.create_commit_and_advance(
        ref=ref, expected_base_sha=expected_base_sha, files=files, message=message
    )


def verify_transaction(
    backend: PersistenceBackend,
    *,
    ref: str,
    commit_sha: str,
    expected_files: dict[str, bytes],
) -> None:
    backend.verify_commit(ref=ref, commit_sha=commit_sha, expected_files=expected_files)
