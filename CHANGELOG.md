# Changelog

All notable changes to `pynissan` are documented in this file.

The project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

- Added application authentication and request-proof support for protected onboarding flows.
- Split service clients, models, parsers, and tests into focused modules.
- Added a CI-enforced 500-line limit for handwritten Python modules.

## [0.1.0] - 2026-07-31

- Added async authentication, token refresh, and reusable token persistence.
- Added typed vehicle discovery and connected-vehicle telemetry.
- Added battery, charging, climate, doors, location, maintenance, and history reads.
- Added remote climate, charging, lock, horn, lights, engine, and refresh commands.
- Added read-only mode as the default client policy.
- Added United States account support and Nissan Ariya vehicle support.
- Added an automated, attested PyPI and GitHub release process.

[Unreleased]: https://github.com/bvdcode/nissan-connect-sdk/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/bvdcode/nissan-connect-sdk/releases/tag/v0.1.0
