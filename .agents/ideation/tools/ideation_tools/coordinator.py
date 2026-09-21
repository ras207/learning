from __future__ import annotations

import base64
import copy
import json
from dataclasses import dataclass
from typing import Any

from .auth import LocalHarnessVerifier, mutation_requires_direct_human_authorization, verify_human_authorizations
from .backends.base import PersistenceBackend
from .content_store import ContentStore
from .errors import CommitFailed, ConcurrencyConflict, ValidationRejected, VerificationIndeterminate
from .hashing import canonical_hash, canonical_json_bytes, sha256_bytes
from .migrations import CURRENT_STATE_SCHEMA_VERSION, migrate_state
from .primitives import (
    commit_transaction, fingerprint_artifact, stage_artifact_change, stage_state_change,
    validate_policy_invariants, validate_state_snapshot, validate_transaction, validate_write_boundary,
    verify_transaction,
)
from .schema import validate
from .state import dump_state, parse_state, utc_now

PROTECTED_REFS = {"refs/heads/main", "refs/heads/master"}


@dataclass
class StageResult:
    files: dict[str, bytes]
    state: dict[str, Any]
    state_path: str
    resulting_revision: int
    artifact_fingerprints: dict[str, str]
    invariant_results: list[dict[str, Any]]


class TransactionCoordinator:
    def __init__(self, backend: PersistenceBackend, context_verifier=None):
        if not getattr(backend, "atomic_commits", False):
            raise ValueError("Persistence backend does not guarantee atomic commits")
        self.backend = backend
        self.context_verifier = context_verifier or LocalHarnessVerifier()

    @staticmethod
    def _result(*, transaction_id: str, status: str, transaction_hash: str, base_sha: str | None,
                commit_sha: str | None, resulting_revision: int | None,
                artifact_fingerprints: dict[str, str] | None = None,
                invariant_results: list[dict[str, Any]] | None = None, message: str) -> dict[str, Any]:
        result = {
            "schema_version": 1,
            "transaction_id": transaction_id or "unknown",
            "status": status,
            "transaction_hash": transaction_hash or "0" * 64,
            "base_sha": base_sha,
            "commit_sha": commit_sha,
            "resulting_revision": resulting_revision,
            "artifact_fingerprints": artifact_fingerprints or {},
            "invariant_results": invariant_results or [],
            "message": message,
        }
        validate(result, "transaction-result.schema.json")
        return result

    @staticmethod
    def _state_path(project_slug: str) -> str:
        return f"projects/{project_slug}/ideation/state.yaml"

    @staticmethod
    def _manifest(files: dict[str, bytes]) -> dict[str, str]:
        return {path: sha256_bytes(data) for path, data in sorted(files.items())}

    @staticmethod
    def _encode_manifest(manifest: dict[str, str]) -> str:
        return base64.urlsafe_b64encode(canonical_json_bytes(manifest)).decode("ascii")

    @staticmethod
    def _decode_manifest(value: str) -> dict[str, str]:
        try:
            decoded = base64.urlsafe_b64decode(value.encode("ascii"))
            result = json.loads(decoded.decode("utf-8"))
        except Exception as exc:
            raise VerificationIndeterminate("Invalid transaction file manifest in Git metadata") from exc
        if not isinstance(result, dict):
            raise VerificationIndeterminate("Transaction file manifest is not an object")
        return result

    def _verify_commit_manifest(self, commit_sha: str) -> dict[str, str]:
        message = self.backend.read_commit_message(commit_sha)
        # Backends exposing parse_metadata provide the canonical parser.
        parser = getattr(self.backend, "parse_metadata", None)
        if parser is None:
            return {}
        metadata = parser(message)
        encoded = metadata.get("file_manifest")
        if not encoded:
            return metadata
        manifest = self._decode_manifest(encoded)
        for path, expected in manifest.items():
            actual = self.backend.read_file(commit_sha, path)
            if actual is None or sha256_bytes(actual) != expected:
                raise VerificationIndeterminate(f"Git reconciliation failed for {path}")
        return metadata

    def _ensure_current_head_reconciled(self, ref: str) -> str:
        head = self.backend.resolve_ref(ref)
        self._verify_commit_manifest(head)
        return head

    def _check_identity(self, transaction: dict[str, Any], context: dict[str, Any]) -> None:
        project = transaction["project"]
        for key in ("project_id", "project_slug", "iteration"):
            if project[key] != context[key]:
                raise ValidationRejected(f"Execution context {key} does not match transaction")
        ref = context["authorized_ref"]
        if ref in PROTECTED_REFS:
            raise ValidationRejected(f"Protected ref is not writable by ideation tools: {ref}")

    def _find_replay(self, transaction: dict[str, Any], context: dict[str, Any], tx_hash: str) -> dict[str, Any] | None:
        records = self.backend.list_transaction_metadata(context["authorized_ref"], transaction["transaction_id"])
        if not records:
            return None
        hashes = {r.get("transaction_hash") for r in records}
        if hashes != {tx_hash}:
            raise ValidationRejected("Transaction ID was previously used with different content")
        record = records[0]
        commit_sha = record["commit_sha"]
        self._verify_commit_manifest(commit_sha)
        revision = int(record["state_revision"]) if record.get("state_revision") else None
        return self._result(
            transaction_id=transaction["transaction_id"], status="applied", transaction_hash=tx_hash,
            base_sha=record.get("base_sha"), commit_sha=commit_sha, resulting_revision=revision,
            message="Identical transaction was already applied; returning verified prior result",
        )

    def _load_state(self, base_sha: str, project_slug: str) -> tuple[dict[str, Any] | None, str]:
        path = self._state_path(project_slug)
        raw = self.backend.read_file(base_sha, path)
        if raw is None:
            return None, path
        state = parse_state(raw)
        if state.get("schema_version") == CURRENT_STATE_SCHEMA_VERSION:
            validate_state_snapshot(state)
        return state, path

    def _validate_state_identity(self, state: dict[str, Any] | None, transaction: dict[str, Any]) -> None:
        expected_revision = transaction["expected_revision"]
        if state is None:
            if expected_revision != 0:
                raise ConcurrencyConflict("Canonical state is absent but transaction does not expect revision 0")
            if not transaction["state_mutations"] or transaction["state_mutations"][0]["operation"] != "initialize":
                raise ValidationRejected("Absent canonical state requires initialize as the first mutation")
            return
        if state.get("schema_version") != CURRENT_STATE_SCHEMA_VERSION:
            if transaction["source"]["kind"] != "state_migration":
                raise ValidationRejected(
                    f"Canonical state schema version {state.get('schema_version')} requires an explicit deterministic migration"
                )
        project = transaction["project"]
        for key in ("project_id", "project_slug", "iteration"):
            if state.get("project", {}).get(key) != project[key]:
                raise ValidationRejected(f"Canonical state {key} does not match transaction")
        if state.get("project", {}).get("revision") != expected_revision:
            raise ConcurrencyConflict(
                f"Expected project revision {expected_revision}, found {state['project']['revision']}"
            )

    def _validate_artifact_change(self, change: dict[str, Any], base_sha: str, project_slug: str, state: dict[str, Any] | None) -> None:
        validate_write_boundary(change["path"], project_slug)
        existing = self.backend.read_file(base_sha, change["path"])
        expected = change.get("expected_fingerprint")
        if change["operation"] == "create":
            if existing is not None:
                raise ConcurrencyConflict(f"Artifact already exists: {change['path']}")
            if expected not in (None, ""):
                raise ValidationRejected("Create artifact must not declare an expected fingerprint")
        else:
            if existing is None:
                raise ConcurrencyConflict(f"Artifact to update does not exist: {change['path']}")
            actual = sha256_bytes(existing)
            if expected != actual:
                raise ConcurrencyConflict(f"Artifact fingerprint conflict for {change['path']}")
            if state:
                records = [a for a in state.get("artifacts", []) if a.get("artifact_id") == change["artifact_id"]]
                if records:
                    recorded = records[-1].get("fingerprint", {}).get("value")
                    if recorded != actual:
                        raise ConcurrencyConflict(f"Canonical artifact record fingerprint is stale for {change['artifact_id']}")

    def _stage(self, transaction: dict[str, Any], context: dict[str, Any], base_sha: str, state: dict[str, Any] | None,
               used_authorization_ids: list[str]) -> StageResult:
        content_store = ContentStore(context["content_store_root"])
        artifact_files: dict[str, bytes] = {}
        artifact_fingerprints: dict[str, str] = {}
        for change in transaction["artifact_changes"]:
            self._validate_artifact_change(change, base_sha, transaction["project"]["project_slug"], state)
            data, fingerprint = stage_artifact_change(content_store, change["content_ref"])
            artifact_files[change["path"]] = data
            artifact_fingerprints[change["artifact_id"]] = fingerprint

        staged = copy.deepcopy(state)
        if staged is not None and staged.get("schema_version") != CURRENT_STATE_SCHEMA_VERSION:
            if transaction["source"]["kind"] != "state_migration":
                raise ValidationRejected("Older state may be changed only by a state_migration transaction")
            staged = migrate_state(staged)
        for raw_mutation in transaction["state_mutations"]:
            mutation = copy.deepcopy(raw_mutation)
            if mutation_requires_direct_human_authorization(mutation) and mutation.get("authorization_id"):
                if mutation["section"] == "decisions":
                    mutation["patch"] = {**mutation["patch"], "authorization_id": mutation["authorization_id"]}
            staged = stage_state_change(staged, mutation)

        if staged is None:
            raise ValidationRejected("Transaction produced no canonical state")

        now = utc_now()
        if state is None:
            resulting_revision = staged["project"]["revision"]
            if resulting_revision != 1:
                raise ValidationRejected("Initialized state must begin at revision 1")
        else:
            resulting_revision = state["project"]["revision"] + 1
            staged["project"]["revision"] = resulting_revision
        staged["project"]["updated_at"] = now

        # Deterministically maintain artifact references for every canonical artifact write.
        records = staged.setdefault("artifacts", [])
        for change in transaction["artifact_changes"]:
            fp = artifact_fingerprints[change["artifact_id"]]
            record = next((a for a in records if a.get("artifact_id") == change["artifact_id"]), None)
            update = {
                "artifact_id": change["artifact_id"],
                "role": change["role"],
                "path": change["path"],
                "status": change["status"],
                "fingerprint": {"algorithm": "sha256", "value": fp},
                "repository_commit": None,
                "last_verified_at": now,
            }
            if record is None:
                records.append(update)
            else:
                record.update(update)

        auth_id = used_authorization_ids[0] if len(used_authorization_ids) == 1 else None
        staged.setdefault("history", []).append({
            "event_id": f"evt:{transaction['transaction_id']}",
            "timestamp": now,
            "event_type": transaction["source"]["kind"],
            "actor": context["actor"],
            "affected_record_ids": [m.get("record_id") for m in transaction["state_mutations"] if m.get("record_id")],
            "summary": transaction["summary"],
            "resulting_revision": resulting_revision,
            "transaction_id": transaction["transaction_id"],
            "authorization_id": auth_id,
            "authorization_ids": used_authorization_ids,
        })

        # The prospective artifact map used by invariants includes unchanged files on demand plus staged writes.
        prospective_artifacts = dict(artifact_files)
        vision_path = f"projects/{transaction['project']['project_slug']}/ideation/vision.md"
        if vision_path not in prospective_artifacts:
            current_vision = self.backend.read_file(base_sha, vision_path)
            if current_vision is not None:
                prospective_artifacts[vision_path] = current_vision

        validate_state_snapshot(staged)
        invariant_results = validate_policy_invariants(staged, prospective_artifacts)
        state_path = self._state_path(transaction["project"]["project_slug"])
        files = {state_path: dump_state(staged), **artifact_files}
        return StageResult(files, staged, state_path, resulting_revision, artifact_fingerprints, invariant_results)

    def _commit_message(self, transaction: dict[str, Any], tx_hash: str, base_sha: str, stage: StageResult) -> str:
        manifest = self._manifest(stage.files)
        return (
            f"Ideation transaction: {transaction['summary']}\n\n"
            f"Ideation-Transaction-ID: {transaction['transaction_id']}\n"
            f"Ideation-Transaction-Hash: {tx_hash}\n"
            f"Ideation-Base-SHA: {base_sha}\n"
            f"Ideation-State-Revision: {stage.resulting_revision}\n"
            f"Ideation-File-Manifest: {self._encode_manifest(manifest)}\n"
        )

    def execute(self, transaction: dict[str, Any], context: dict[str, Any], *, dry_run: bool = False) -> dict[str, Any]:
        tx_id = transaction.get("transaction_id", "unknown") if isinstance(transaction, dict) else "unknown"
        tx_hash = canonical_hash(transaction) if isinstance(transaction, dict) else "0" * 64
        base_sha: str | None = None
        try:
            validate_transaction(transaction)
            context = self.context_verifier.verify(context)
            self._check_identity(transaction, context)

            current_head = self._ensure_current_head_reconciled(context["authorized_ref"])
            replay = self._find_replay(transaction, context, tx_hash)
            if replay:
                return replay
            if current_head != context["expected_head_sha"]:
                raise ConcurrencyConflict("Authorized ref head differs from trusted execution context")
            base_sha = current_head

            state, _ = self._load_state(base_sha, transaction["project"]["project_slug"])
            self._validate_state_identity(state, transaction)
            used_auth = verify_human_authorizations(transaction, context, state)
            stage = self._stage(transaction, context, base_sha, state, used_auth)

            if dry_run:
                return self._result(
                    transaction_id=tx_id, status="validated", transaction_hash=tx_hash, base_sha=base_sha,
                    commit_sha=None, resulting_revision=stage.resulting_revision,
                    artifact_fingerprints=stage.artifact_fingerprints, invariant_results=stage.invariant_results,
                    message="Dry-run preflight and staging succeeded; no ref was advanced",
                )

            message = self._commit_message(transaction, tx_hash, base_sha, stage)
            commit_sha = commit_transaction(
                self.backend, ref=context["authorized_ref"], expected_base_sha=base_sha, files=stage.files, message=message
            )
            try:
                verify_transaction(self.backend, ref=context["authorized_ref"], commit_sha=commit_sha, expected_files=stage.files)
                self._verify_commit_manifest(commit_sha)
            except Exception as exc:
                return self._result(
                    transaction_id=tx_id, status="reconciliation_required", transaction_hash=tx_hash,
                    base_sha=base_sha, commit_sha=commit_sha, resulting_revision=stage.resulting_revision,
                    artifact_fingerprints=stage.artifact_fingerprints, invariant_results=stage.invariant_results,
                    message=f"Ref may have advanced but verification was inconclusive: {exc}",
                )
            return self._result(
                transaction_id=tx_id, status="applied", transaction_hash=tx_hash, base_sha=base_sha,
                commit_sha=commit_sha, resulting_revision=stage.resulting_revision,
                artifact_fingerprints=stage.artifact_fingerprints, invariant_results=stage.invariant_results,
                message="Transaction committed atomically and verified by read-back",
            )
        except ConcurrencyConflict as exc:
            return self._result(transaction_id=tx_id, status="conflict", transaction_hash=tx_hash, base_sha=base_sha,
                                commit_sha=None, resulting_revision=None, message=str(exc))
        except ValidationRejected as exc:
            return self._result(transaction_id=tx_id, status="rejected", transaction_hash=tx_hash, base_sha=base_sha,
                                commit_sha=None, resulting_revision=None, message=str(exc))
        except CommitFailed as exc:
            return self._result(transaction_id=tx_id, status="failed", transaction_hash=tx_hash, base_sha=base_sha,
                                commit_sha=None, resulting_revision=None, message=str(exc))
        except VerificationIndeterminate as exc:
            return self._result(transaction_id=tx_id, status="reconciliation_required", transaction_hash=tx_hash,
                                base_sha=base_sha, commit_sha=None, resulting_revision=None, message=str(exc))
        except Exception as exc:
            return self._result(transaction_id=tx_id, status="failed", transaction_hash=tx_hash, base_sha=base_sha,
                                commit_sha=None, resulting_revision=None, message=f"Unexpected execution failure: {exc}")

    def reconcile(self, *, transaction_id: str, transaction_hash: str, context: dict[str, Any]) -> dict[str, Any]:
        context = self.context_verifier.verify(context)
        ref = context["authorized_ref"]
        try:
            self._ensure_current_head_reconciled(ref)
            records = self.backend.list_transaction_metadata(ref, transaction_id)
            if not records:
                return self._result(transaction_id=transaction_id, status="failed", transaction_hash=transaction_hash,
                                    base_sha=context.get("expected_head_sha"), commit_sha=None, resulting_revision=None,
                                    message="Transaction is not reachable from the authorized ref")
            matching = [r for r in records if r.get("transaction_hash") == transaction_hash]
            if not matching:
                return self._result(transaction_id=transaction_id, status="rejected", transaction_hash=transaction_hash,
                                    base_sha=None, commit_sha=None, resulting_revision=None,
                                    message="Transaction ID is present in Git with different content")
            record = matching[0]
            self._verify_commit_manifest(record["commit_sha"])
            return self._result(transaction_id=transaction_id, status="applied", transaction_hash=transaction_hash,
                                base_sha=record.get("base_sha"), commit_sha=record["commit_sha"],
                                resulting_revision=int(record["state_revision"]),
                                message="Transaction reconciled from authoritative Git metadata and committed tree")
        except Exception as exc:
            return self._result(transaction_id=transaction_id, status="reconciliation_required", transaction_hash=transaction_hash,
                                base_sha=None, commit_sha=None, resulting_revision=None,
                                message=f"Reconciliation remains inconclusive: {exc}")
