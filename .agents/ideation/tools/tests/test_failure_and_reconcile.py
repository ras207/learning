from __future__ import annotations

from ideation_tools.backends.local_git import LocalGitBackend
from ideation_tools.coordinator import TransactionCoordinator
from ideation_tools.errors import CommitFailed, VerificationIndeterminate
from ideation_tools.hashing import canonical_hash

from conftest import context, git, init_tx


class CommitFailBackend(LocalGitBackend):
    def create_commit_and_advance(self, **kwargs):
        raise CommitFailed("injected commit failure")


class VerifyFailOnceBackend(LocalGitBackend):
    def __init__(self, repo):
        super().__init__(repo)
        self.failed = False

    def verify_commit(self, **kwargs):
        if not self.failed:
            self.failed = True
            raise VerificationIndeterminate("injected verification interruption")
        return super().verify_commit(**kwargs)


def test_commit_failure_does_not_advance_ref(repo, content_store):
    before = git(repo, "rev-parse", "refs/heads/work")
    coordinator = TransactionCoordinator(CommitFailBackend(repo))
    result = coordinator.execute(init_tx(), context(repo, content_store))
    assert result["status"] == "failed"
    assert git(repo, "rev-parse", "refs/heads/work") == before


def test_verification_interruption_requires_reconciliation_and_recovers_from_git(repo, content_store):
    backend = VerifyFailOnceBackend(repo)
    coordinator = TransactionCoordinator(backend)
    tx = init_tx()
    ctx = context(repo, content_store)
    result = coordinator.execute(tx, ctx)
    assert result["status"] == "reconciliation_required"
    assert result["commit_sha"] == git(repo, "rev-parse", "refs/heads/work")

    clean = TransactionCoordinator(LocalGitBackend(repo))
    reconciled = clean.reconcile(transaction_id=tx["transaction_id"], transaction_hash=canonical_hash(tx), context=context(repo, content_store))
    assert reconciled["status"] == "applied"
    assert reconciled["commit_sha"] == result["commit_sha"]


def test_non_atomic_backend_is_refused(repo):
    class NonAtomicBackend(LocalGitBackend):
        atomic_commits = False

    import pytest
    with pytest.raises(ValueError, match="atomic commits"):
        TransactionCoordinator(NonAtomicBackend(repo))
