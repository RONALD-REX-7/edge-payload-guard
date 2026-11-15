"""Unit tests for the validation API."""

import unittest

from jsonschema.exceptions import SchemaError

from edge_payload_guard import ExternalReferenceError, validate_payload


class ValidatePayloadTests(unittest.TestCase):
    def setUp(self):
        self.schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "required": ["device_id", "temperature_c"],
            "properties": {
                "device_id": {"type": "string", "minLength": 1},
                "temperature_c": {"type": "number", "maximum": 125},
            },
            "additionalProperties": False,
        }

    def test_accepts_valid_payload(self):
        self.assertEqual(validate_payload({"device_id": "node-01", "temperature_c": 24.5}, self.schema), [])

    def test_reports_multiple_failures_in_stable_order(self):
        issues = validate_payload({"device_id": "", "temperature_c": 150, "extra": True}, self.schema)
        self.assertGreaterEqual(len(issues), 3)
        self.assertEqual(
            issues,
            sorted(issues, key=lambda item: (item.path, item.keyword, item.message)),
        )
        self.assertTrue(any(issue.keyword == "minLength" for issue in issues))
        self.assertTrue(any(issue.keyword == "maximum" for issue in issues))
        self.assertTrue(any(issue.keyword == "additionalProperties" for issue in issues))

    def test_reports_required_property(self):
        self.assertTrue(any(issue.keyword == "required" for issue in validate_payload({}, self.schema)))

    def test_supports_local_references(self):
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$defs": {"device_id": {"type": "string", "minLength": 1}},
            "type": "object",
            "properties": {"device_id": {"$ref": "#/$defs/device_id"}},
            "required": ["device_id"],
        }
        self.assertEqual(validate_payload({"device_id": "node-01"}, schema), [])
        self.assertTrue(validate_payload({"device_id": ""}, schema))

    def test_rejects_external_references(self):
        schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$ref": "https://example.invalid/schema.json",
        }
        with self.assertRaises(ExternalReferenceError):
            validate_payload({}, schema)

    def test_rejects_malformed_schema(self):
        with self.assertRaises(SchemaError):
            validate_payload({}, {"type": "not-a-json-schema-type"})

    def test_supports_boolean_schemas(self):
        self.assertEqual(validate_payload({"any": "value"}, True), [])
        self.assertEqual(validate_payload({"any": "value"}, False)[0].keyword, "falseSchema")


if __name__ == "__main__":
    unittest.main()
