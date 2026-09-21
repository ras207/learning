from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .errors import ValidationRejected

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"


def load_schema(name: str) -> dict[str, Any]:
    with (SCHEMA_DIR / name).open("r", encoding="utf-8") as f:
        return json.load(f)


def validate(instance: Any, schema_name: str) -> None:
    validator = Draft202012Validator(load_schema(schema_name))
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
    if errors:
        parts = []
        for error in errors:
            path = "/".join(str(p) for p in error.absolute_path) or "<root>"
            parts.append(f"{path}: {error.message}")
        raise ValidationRejected(f"Schema validation failed for {schema_name}: " + "; ".join(parts))
