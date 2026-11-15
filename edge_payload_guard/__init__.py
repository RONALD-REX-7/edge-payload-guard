"""Offline-first JSON Schema validation for embedded and IoT telemetry."""

from .validator import ExternalReferenceError, ValidationIssue, validate_payload

__version__ = "1.0.0"

__all__ = ["ExternalReferenceError", "ValidationIssue", "validate_payload", "__version__"]
