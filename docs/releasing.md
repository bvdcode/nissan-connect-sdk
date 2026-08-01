# Releasing

Releases are built and uploaded by `.github/workflows/publish.yml`. The workflow uses PyPI
Trusted Publishing and does not require a long-lived API token.

## One-time PyPI setup

Create a `pypi` environment in the GitHub repository and configure it with the desired
deployment protection rules. Register the following GitHub publisher for the `pynissan`
project in PyPI:

- Owner: `bvdcode`
- Repository: `nissan-connect-sdk`
- Workflow: `publish.yml`
- Environment: `pypi`

PyPI also supports registering this publisher as a pending publisher when the project does not
exist yet.

## Release checklist

1. Update the version in `pyproject.toml` and move the release notes from `Unreleased` into a
   dated section in `CHANGELOG.md`.
2. Run the complete local quality gate from `CONTRIBUTING.md`.
3. Commit the release changes and create a GitHub release with a matching `vX.Y.Z` tag.
4. Publish the GitHub release. The workflow verifies that the tag and package versions match,
   builds wheel and source distributions, checks their metadata, and uploads them to PyPI.

PyPI release files are immutable. Publish a new patch version instead of replacing an existing
file.
