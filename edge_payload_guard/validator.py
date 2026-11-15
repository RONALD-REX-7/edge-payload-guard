"""JSON Schema validation primitives used by the CLI and Python API."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any

from jsonschema.validators import validator_for


class ExternalReferenceError(ValueError):
    """Raised when a schema attempts to resolve a non-local reference."""


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """One deterministic validation failure."""

    path: str
    keyword: str
    message: str

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serialisable representation."""
        return asdict(self)


_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_REFERENCE_KEYWORDS = {"$ref", "$dynamicRef", "$recursiveRef"}


def _format_path(parts: Any) -> str:
    """Format a jsonschema path as a readable JSON-like location."""
    result = "$"
    for part in parts:
        if isinstance(part, int):
            result += f"[{part}]"
            continue
        key = str(part)
        result += f".{key}" if _IDENTIFIER.fullmatch(key) else f"[{json.dumps(key, ensure_ascii=False)}]"
    return result


def _reject_external_references(schema: Any, path: str = "$") -> None:
    """Reject remote/file references so validation never fetches a resource."""
    if isinstance(schema, Mapping):
        for key, value in schema.items():
            child_path = f"{path}.{key}"
            if key in _REFERENCE_KEYWORDS and isinstance(value, str) and not value.startswith("#"):
                raise ExternalReferenceError(
                    f"External reference at {child_path} is disabled: {value}"
                )
            _reject_external_references(value, child_path)
    elif isinstance(schema, list):
        for index, value in enumerate(schema):
            _reject_external_references(value, f"{path}[{index}]")


def validate_payload(payload: Any, schema: Any) -> list[ValidationIssue]:
    """Validate a JSON-compatible value and return sorted issues.

    A schema can be an object or a boolean. Local fragment references are
    supported; network and file references are rejected by design.
    """
    if isinstance(schema, bool):
        if schema:
            return []
        return [
            ValidationIssue(
                path="$",
                keyword="falseSchema",
                message="The schema is false and therefore rejects every payload.",
            )
        ]
    if not isinstance(schema, Mapping):
        raise TypeError("A JSON Schema document must be an object or a boolean.")

    _reject_external_references(schema)
    validator_type = validator_for(schema)
    validator_type.check_schema(schema)
    validator = validator_type(schema)
    issues = [
        ValidationIssue(
            path=_format_path(error.absolute_path),
            keyword=str(error.validator),
            message=error.message,
        )
        for error in validator.iter_errors(payload)
    ]
    return sorted(issues, key=lambda issue: (issue.path, issue.keyword, issue.message))
