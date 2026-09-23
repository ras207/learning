from __future__ import annotations

import hashlib
import json
from typing import Any


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_ref(data: bytes) -> str:
    return f"sha256:{sha256_bytes(data)}"


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonical_hash(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


def vision_content_fingerprint(data: bytes) -> str:
    """SHA-256 of a vision artifact with the value of its header `status:` line blanked.

    Approval flips the header from `status: candidate` to `status: approved`; every
    other byte of the approved text must stay exactly as the human signed it. The
    header is every line before the first Markdown heading (a line starting with `#`),
    so a `status:` line in the body is never ignored. Only the first header `status:`
    line is blanked, and the line itself is kept so it cannot move unnoticed.
    """
    lines = data.split(b"\n")
    for i, line in enumerate(lines):
        if line.startswith(b"#"):
            break
        if line.startswith(b"status:"):
            lines[i] = b"status:" + (b"\r" if line.endswith(b"\r") else b"")
            break
    return sha256_bytes(b"\n".join(lines))
