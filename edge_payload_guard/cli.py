"""Command-line interface for Edge Payload Guard."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from jsonschema.exceptions import SchemaError

from . import __version__
from .validator import ExternalReferenceError, validate_payload


def _read_json(path: str) -> object:
    source = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    return json.loads(source)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="edge-payload-guard",
        description="Validate embedded and IoT telemetry JSON against a JSON Schema.",
    )
    parser.add_argument("--schema", required=True, metavar="SCHEMA.json", help="Path to a JSON Schema document.")
    parser.add_argument(
        "--payload",
        default="-",
        metavar="PAYLOAD.json",
        help="Payload file path, or '-' to read standard input (default: '-').",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format (default: text).")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return its documented process exit code."""
    args = _build_parser().parse_args(argv)

    try:
        schema = _read_json(args.schema)
    except FileNotFoundError:
        print(f"Schema file not found: {args.schema}", file=sys.stderr)
        return 2
    except (OSError, UnicodeDecodeError) as exc:
        print(f"Could not read schema '{args.schema}': {exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(
            f"Invalid JSON in schema '{args.schema}' at line {exc.lineno}, "
            f"column {exc.colno}: {exc.msg}",
            file=sys.stderr,
        )
        return 2

    try:
        payload = _read_json(args.payload)
    except FileNotFoundError:
        print(f"Payload file not found: {args.payload}", file=sys.stderr)
        return 2
    except (OSError, UnicodeDecodeError) as exc:
        print(f"Could not read payload '{args.payload}': {exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(
            f"Invalid JSON in payload '{args.payload}' at line {exc.lineno}, "
            f"column {exc.colno}: {exc.msg}",
            file=sys.stderr,
        )
        return 2

    try:
        issues = validate_payload(payload, schema)
    except SchemaError as exc:
        print(f"Invalid JSON Schema: {exc.message}", file=sys.stderr)
        return 2
    except ExternalReferenceError as exc:
        print(f"Unsupported schema reference: {exc}", file=sys.stderr)
        return 2
    except TypeError as exc:
        print(f"Invalid JSON Schema: {exc}", file=sys.stderr)
        return 2

    payload_label = "stdin" if args.payload == "-" else args.payload
    is_valid = not issues
    if args.format == "json":
        json.dump(
            {
                "valid": is_valid,
                "payload": payload_label,
                "issues": [issue.to_dict() for issue in issues],
            },
            sys.stdout,
            ensure_ascii=False,
            indent=2,
        )
        sys.stdout.write("\n")
    elif is_valid:
        print(f"VALID: {payload_label}")
    else:
        print(f"INVALID: {payload_label}")
        for issue in issues:
            print(f"  - {issue.path} [{issue.keyword}]: {issue.message}")
    return 0 if is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
