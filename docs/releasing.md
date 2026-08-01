# Releasing

Every push to `main` runs `.github/workflows/publish.yml`. The workflow validates the source and
uses Conventional Commits to decide whether a release is required. When a release is required,
it updates `pyproject.toml` and `CHANGELOG.md`, creates a release commit and tag, builds the
distributions, publishes them to PyPI with Trusted Publishing, and creates the matching GitHub
release.

Do not edit the package version, release section, or version tag manually.

## Version selection

Use a Conventional Commit title for a direct commit or squash-merged pull request:

- `fix: handle an expired access token` creates a patch release.
- `perf: reduce vehicle refresh requests` creates a patch release.
- `feat: add charging schedule support` creates a minor release.
- A `BREAKING CHANGE:` paragraph in the commit body creates a major release.
- `build:`, `chore:`, `ci:`, `docs:`, `refactor:`, `style:`, and `test:` do not create a release
  by themselves.

The generated release notes use the parsed title and body of every releasable commit since the
previous version. Squash merging a focused pull request therefore produces one focused release
entry from its merge commit.

## One-time PyPI setup

Create a `pypi` environment in the GitHub repository and allow deployments from `main`. Register
the following GitHub publisher for the `pynissan` project in PyPI:

- Owner: `bvdcode`
- Repository: `nissan-connect-sdk`
- Workflow: `publish.yml`
- Environment: `pypi`

PyPI supports registering this publisher as a pending publisher before the project exists. The
first successful workflow creates the project and converts the pending publisher automatically.

## Release flow

1. Push or squash-merge a Conventional Commit into `main`.
2. CI validates linting, formatting, typing, module size, tests, and package metadata.
3. Python Semantic Release calculates the next version and generates the changelog.
4. The workflow commits the generated version, creates the corresponding `vX.Y.Z` tag, and builds
   the wheel and source distribution.
5. Trusted Publishing uploads the artifacts to PyPI.
6. The same artifacts and generated notes become the GitHub release.

PyPI release files are immutable. Fix a failed release with a new commit and version rather than
attempting to replace an uploaded file.
