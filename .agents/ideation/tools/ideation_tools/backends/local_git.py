from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

from ..errors import CommitFailed, ConcurrencyConflict, ValidationRejected, VerificationIndeterminate

TRAILER_RE = re.compile(r"^Ideation-([A-Za-z-]+):\s*(.+)$")


class LocalGitBackend:
    """Working-tree-independent Git persistence using plumbing commands and a temporary index."""

    atomic_commits = True

    def __init__(self, repo: str | Path):
        self.repo = Path(repo).resolve()
        self._git("rev-parse", "--git-dir")

    def _git(self, *args: str, input_bytes: bytes | None = None, env: dict[str, str] | None = None) -> bytes:
        full_env = os.environ.copy()
        if env:
            full_env.update(env)
        proc = subprocess.run(
            ["git", "-C", str(self.repo), *args],
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=full_env,
        )
        if proc.returncode != 0:
            raise CommitFailed(proc.stderr.decode("utf-8", errors="replace").strip() or f"git {' '.join(args)} failed")
        return proc.stdout

    def resolve_ref(self, ref: str) -> str:
        try:
            return self._git("rev-parse", "--verify", ref).decode().strip()
        except CommitFailed as exc:
            raise ValidationRejected(f"Authorized ref does not exist: {ref}") from exc

    def read_file(self, commit_sha: str, path: str) -> bytes | None:
        proc = subprocess.run(
            ["git", "-C", str(self.repo), "show", f"{commit_sha}:{path}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if proc.returncode != 0:
            return None
        return proc.stdout

    def read_commit_message(self, commit_sha: str) -> str:
        return self._git("show", "-s", "--format=%B", commit_sha).decode("utf-8", errors="replace")

    @staticmethod
    def parse_metadata(message: str) -> dict[str, str]:
        out: dict[str, str] = {}
        for line in message.splitlines():
            m = TRAILER_RE.match(line.strip())
            if m:
                out[m.group(1).lower().replace("-", "_")] = m.group(2).strip()
        return out

    def list_transaction_metadata(self, ref: str, transaction_id: str) -> list[dict[str, str]]:
        raw = self._git("log", ref, "--format=%H%x1f%B%x1e").decode("utf-8", errors="replace")
        found = []
        for record in raw.split("\x1e"):
            if not record.strip() or "\x1f" not in record:
                continue
            sha, message = record.split("\x1f", 1)
            meta = self.parse_metadata(message)
            if meta.get("transaction_id") == transaction_id:
                meta["commit_sha"] = sha.strip()
                found.append(meta)
        return found

    def create_commit_and_advance(self, *, ref: str, expected_base_sha: str, files: dict[str, bytes], message: str) -> str:
        if self.resolve_ref(ref) != expected_base_sha:
            raise ConcurrencyConflict("Authorized ref moved before commit")
        fd, index_path = tempfile.mkstemp(prefix="ideation-index-")
        os.close(fd)
        os.unlink(index_path)
        try:
            env = {"GIT_INDEX_FILE": index_path}
            self._git("read-tree", expected_base_sha, env=env)
            for path, data in sorted(files.items()):
                blob = self._git("hash-object", "-w", "--stdin", input_bytes=data).decode().strip()
                self._git("update-index", "--add", "--cacheinfo", f"100644,{blob},{path}", env=env)
            tree = self._git("write-tree", env=env).decode().strip()
            commit_env = {
                **env,
                "GIT_AUTHOR_NAME": "Ideation Coordinator",
                "GIT_AUTHOR_EMAIL": "ideation@local",
                "GIT_COMMITTER_NAME": "Ideation Coordinator",
                "GIT_COMMITTER_EMAIL": "ideation@local",
            }
            commit_sha = self._git("commit-tree", tree, "-p", expected_base_sha, input_bytes=message.encode("utf-8"), env=commit_env).decode().strip()
        finally:
            try:
                os.unlink(index_path)
            except FileNotFoundError:
                pass
        proc = subprocess.run(
            ["git", "-C", str(self.repo), "update-ref", ref, commit_sha, expected_base_sha],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if proc.returncode != 0:
            raise ConcurrencyConflict(proc.stderr.decode("utf-8", errors="replace").strip() or "Atomic ref update failed")
        return commit_sha

    def verify_commit(self, *, ref: str, commit_sha: str, expected_files: dict[str, bytes]) -> None:
        try:
            if self.resolve_ref(ref) != commit_sha:
                raise VerificationIndeterminate("Authorized ref does not point to the committed transaction")
            for path, expected in expected_files.items():
                actual = self.read_file(commit_sha, path)
                if actual != expected:
                    raise VerificationIndeterminate(f"Read-back mismatch for {path}")
        except VerificationIndeterminate:
            raise
        except Exception as exc:
            raise VerificationIndeterminate(str(exc)) from exc
