from __future__ import annotations

from pathlib import Path

from .errors import ValidationRejected
from .hashing import sha256_bytes


class ContentStore:
    """Immutable content-addressed payload store used outside canonical project state."""

    def __init__(self, root: str | Path):
        self.root = Path(root)

    @staticmethod
    def _parse_ref(content_ref: str) -> str:
        if not content_ref.startswith("sha256:"):
            raise ValidationRejected(f"Unsupported content reference: {content_ref}")
        digest = content_ref.split(":", 1)[1]
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValidationRejected(f"Invalid sha256 content reference: {content_ref}")
        return digest

    def resolve(self, content_ref: str) -> bytes:
        digest = self._parse_ref(content_ref)
        path = self.root / digest
        try:
            data = path.read_bytes()
        except FileNotFoundError as exc:
            raise ValidationRejected(f"Missing content payload: {content_ref}") from exc
        actual = sha256_bytes(data)
        if actual != digest:
            raise ValidationRejected(f"Content payload hash mismatch for {content_ref}")
        return data

    def put(self, data: bytes) -> str:
        digest = sha256_bytes(data)
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / digest
        if path.exists():
            if path.read_bytes() != data:
                raise ValidationRejected(f"Hash collision or corrupted payload for {digest}")
        else:
            path.write_bytes(data)
        return f"sha256:{digest}"
