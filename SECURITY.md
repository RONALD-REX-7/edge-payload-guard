# Security Policy

## Supported release

Security fixes are applied to the latest published release.

## Reporting a vulnerability

Do not publish credentials, private telemetry, or exploit details in a public issue. Use GitHub's private vulnerability reporting for this repository when available. Otherwise, contact the maintainer through the email address listed on the GitHub profile.

## Security considerations

- Remote `$ref`, `$dynamicRef`, and `$recursiveRef` references are rejected.
- Use schemas from trusted sources. Complex regular expressions can consume substantial CPU time.
- Treat payload and schema files as untrusted input and apply operating-system resource limits in shared services.
- This project is a validation utility, not a safety-certified control or protection system.
