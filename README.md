# Edge Payload Guard

[![CI](https://github.com/RONALD-REX-7/edge-payload-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/RONALD-REX-7/edge-payload-guard/actions/workflows/ci.yml)
[![GHCR](https://img.shields.io/badge/GHCR-container-2496ED?logo=docker&logoColor=white)](https://github.com/RONALD-REX-7/edge-payload-guard/pkgs/container/edge-payload-guard)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)

**An offline-first JSON Schema validator for embedded and IoT telemetry payloads.**

Edge Payload Guard validates device messages against a trusted JSON Schema. It provides a small Python API, a command-line interface, and a public multi-architecture OCI container distributed through GitHub Container Registry (GHCR).

Use it for payload checks in development, test fixtures, CI pipelines, gateways, and edge-computing workflows. It is **not** a device safety controller, message broker, or substitute for firmware-side validation.

## Features

- Validate JSON objects and arrays against JSON Schema.
- Read payloads from a file or standard input.
- Produce readable terminal output or machine-readable JSON.
- Report deterministic paths such as `$.sensors[0].temperature_c`.
- Support local JSON Schema references; reject external references to keep validation offline.
- Return stable exit codes for scripts and CI.
- Run as a non-root user in a small Python container.
- Publish Linux `amd64` and `arm64` images to GHCR.

## Quick start: container

```bash
docker pull ghcr.io/ronald-rex-7/edge-payload-guard:1.0.0
```

From the repository root, validate the included example:

```bash
docker run --rm \
  -v "$PWD/examples:/examples:ro" \
  ghcr.io/ronald-rex-7/edge-payload-guard:1.0.0 \
  --schema /examples/telemetry.schema.json \
  --payload /examples/telemetry.valid.json
```

PowerShell:

```powershell
docker run --rm -v "${PWD}/examples:/examples:ro" ghcr.io/ronald-rex-7/edge-payload-guard:1.0.0 --schema /examples/telemetry.schema.json --payload /examples/telemetry.valid.json
```

## Install from source

GitHub Packages does not offer a PyPI-compatible registry. The **GitHub Package** published by this project is the OCI container image; the Python application can also be installed directly from the source repository.

```bash
git clone https://github.com/RONALD-REX-7/edge-payload-guard.git
cd edge-payload-guard
python -m venv .venv
# Activate the virtual environment, then:
python -m pip install .
edge-payload-guard --schema examples/telemetry.schema.json --payload examples/telemetry.valid.json
```

## CLI

```text
edge-payload-guard --schema SCHEMA.json --payload PAYLOAD.json
edge-payload-guard --schema SCHEMA.json --payload -
edge-payload-guard --schema SCHEMA.json --payload PAYLOAD.json --format json
```

| Option | Description |
| --- | --- |
| `--schema` | Required path to a JSON Schema document |
| `--payload` | Payload file; use `-` for standard input (default: `-`) |
| `--format` | `text` (default) or machine-readable `json` |
| `--version` | Print installed version |
| `--help` | Show command help |

Read from standard input:

```bash
cat examples/telemetry.valid.json | edge-payload-guard --schema examples/telemetry.schema.json --payload -
```

Machine-readable output:

```bash
edge-payload-guard --schema examples/telemetry.schema.json --payload examples/telemetry.invalid.json --format json
```

JSON output contains `valid`, `payload`, and `issues`. Each issue has a `path`, failed schema `keyword`, and explanatory `message`.

## Exit codes

| Code | Meaning |
| ---: | --- |
| `0` | Payload is valid |
| `1` | Payload does not satisfy the schema |
| `2` | Input, schema, or invocation error |

## Python API

```python
import json
from pathlib import Path

from edge_payload_guard import validate_payload

schema = json.loads(Path("examples/telemetry.schema.json").read_text(encoding="utf-8"))
payload = json.loads(Path("examples/telemetry.valid.json").read_text(encoding="utf-8"))

issues = validate_payload(payload, schema)
if not issues:
    print("Payload is valid")
else:
    for issue in issues:
        print(f"{issue.path}: {issue.message}")
```

## Examples and testing

- `examples/telemetry.schema.json` — sample telemetry contract.
- `examples/telemetry.valid.json` — payload satisfying the contract.
- `examples/telemetry.invalid.json` — deliberately invalid payload.

The examples are synthetic software test data, not measurements from physical sensors.

Run tests locally:

```bash
python -m pip install .
python -m unittest discover -s tests -v
```

CI tests Python 3.10–3.13 and performs a Docker build/smoke test. Pushing a semantic-version tag (`vMAJOR.MINOR.PATCH`) automatically verifies and publishes the corresponding container. A manual `workflow_dispatch` is also available for controlled publication.

## Package details

- Registry: GitHub Container Registry (`ghcr.io`)
- Image: `ghcr.io/ronald-rex-7/edge-payload-guard`
- Initial version: `1.0.0`
- Platforms: `linux/amd64`, `linux/arm64`
- Licence: MIT

## Scope and limitations

- Input and schema files must be JSON. YAML, CBOR, protobuf, MQTT transport, and device flashing are out of scope.
- Only local JSON Schema references are accepted. Remote `$ref`, `$dynamicRef`, and `$recursiveRef` targets are rejected.
- Use trusted schemas. Complex regular-expression patterns can consume substantial CPU time.
- Validation checks structure and constraints; it does not prove that sensor readings are physically accurate, fresh, authentic, or safe to act upon.
- Do not use this tool as the sole protection mechanism for machinery, battery systems, industrial controls, or other safety-critical equipment.

## Licence

MIT. See [LICENSE](LICENSE).
