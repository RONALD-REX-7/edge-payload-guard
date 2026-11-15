"""CLI integration tests using only the Python standard library."""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from edge_payload_guard.cli import main


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.schema_path = self.root / "schema.json"
        self.payload_path = self.root / "payload.json"
        self.schema_path.write_text(
            json.dumps(
                {
                    "$schema": "https://json-schema.org/draft/2020-12/schema",
                    "type": "object",
                    "required": ["device_id"],
                    "properties": {"device_id": {"type": "string"}},
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_valid_payload_returns_zero(self):
        self.payload_path.write_text('{"device_id":"node-01"}', encoding="utf-8")
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--schema", str(self.schema_path), "--payload", str(self.payload_path)])
        self.assertEqual(code, 0)
        self.assertIn("VALID", output.getvalue())

    def test_invalid_payload_returns_one(self):
        self.payload_path.write_text('{"device_id":42}', encoding="utf-8")
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(["--schema", str(self.schema_path), "--payload", str(self.payload_path)])
        self.assertEqual(code, 1)
        self.assertIn("INVALID", output.getvalue())

    def test_json_output_is_machine_readable(self):
        self.payload_path.write_text('{"device_id":42}', encoding="utf-8")
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(
                ["--schema", str(self.schema_path), "--payload", str(self.payload_path), "--format", "json"]
            )
        result = json.loads(output.getvalue())
        self.assertEqual(code, 1)
        self.assertFalse(result["valid"])
        self.assertTrue(result["issues"])

    def test_reads_payload_from_stdin(self):
        output = io.StringIO()
        with patch("sys.stdin", io.StringIO('{"device_id":"node-stdin"}')):
            with redirect_stdout(output):
                code = main(["--schema", str(self.schema_path), "--payload", "-"])
        self.assertEqual(code, 0)
        self.assertIn("stdin", output.getvalue())

    def test_invalid_json_returns_two(self):
        self.payload_path.write_text("{bad json", encoding="utf-8")
        errors = io.StringIO()
        with redirect_stderr(errors):
            code = main(["--schema", str(self.schema_path), "--payload", str(self.payload_path)])
        self.assertEqual(code, 2)
        self.assertIn("Invalid JSON", errors.getvalue())

    def test_missing_schema_returns_two(self):
        errors = io.StringIO()
        with redirect_stderr(errors):
            code = main(["--schema", str(self.root / "missing.json"), "--payload", "-"])
        self.assertEqual(code, 2)
        self.assertIn("Schema file not found", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
