# Contributing

Contributions are welcome. For changes that affect validation behaviour, include focused tests and update the documentation.

## Local setup

```bash
python -m pip install .
python -m unittest discover -s tests -v
```

## Pull requests

1. Keep changes scoped and explain the problem being solved.
2. Add or update tests for behaviour changes.
3. Run the full test suite locally.
4. Update README or CHANGELOG when user-facing behaviour changes.
5. Never commit credentials, private telemetry, or real device identifiers.

Submit changes through a pull request to the default branch.
