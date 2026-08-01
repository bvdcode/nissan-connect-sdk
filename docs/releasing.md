# Releasing

Version tags run `.github/workflows/publish.yml`. The workflow validates the tagged source,
builds the distributions once, publishes those artifacts to PyPI with Trusted Publishing, and
then creates the matching GitHub release with the same wheel and source distribution.

## One-time PyPI setup

Create a `pypi` environment in the GitHub repository and allow only tags matching `v*` to
deploy through it. Register the following GitHub publisher for the `pynissan` project in PyPI:

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
3. Commit the release changes and wait for CI to pass on the release commit.
4. Create and push an annotated `vX.Y.Z` tag for that commit.

The workflow requires the tag to match the version in `pyproject.toml` and requires a matching,
non-empty section in `CHANGELOG.md`. That committed changelog section becomes the GitHub release
description automatically. The release is created only after the PyPI upload succeeds.

```bash
git tag -a v0.1.0 -m "pynissan 0.1.0"
git push origin v0.1.0
```

PyPI release files are immutable. Publish a new patch version instead of replacing an existing
file. If the upload succeeds but GitHub release creation fails, rerun only the failed job so the
immutable PyPI files are not uploaded again.
