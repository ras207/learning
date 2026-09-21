from __future__ import annotations

from typing import Any, Callable

from .errors import ValidationRejected

CURRENT_STATE_SCHEMA_VERSION = 1
Migration = Callable[[dict[str, Any]], dict[str, Any]]
_MIGRATIONS: dict[int, Migration] = {}


def register_migration(from_version: int, fn: Migration) -> None:
    if from_version in _MIGRATIONS:
        raise RuntimeError(f"Migration from version {from_version} already registered")
    _MIGRATIONS[from_version] = fn


def migrate_state(state: dict[str, Any], target_version: int = CURRENT_STATE_SCHEMA_VERSION) -> dict[str, Any]:
    version = state.get("schema_version")
    if not isinstance(version, int):
        raise ValidationRejected("State has no valid schema_version; best-effort interpretation is prohibited")
    if version > target_version:
        raise ValidationRejected(f"State schema version {version} is newer than supported version {target_version}")
    current = state
    while version < target_version:
        fn = _MIGRATIONS.get(version)
        if fn is None:
            raise ValidationRejected(f"No explicit deterministic migration registered from state schema version {version}")
        current = fn(current)
        next_version = current.get("schema_version")
        if next_version != version + 1:
            raise ValidationRejected(f"Migration from version {version} did not produce version {version + 1}")
        version = next_version
    return current
