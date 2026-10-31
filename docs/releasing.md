# Releasing

Every push to `main` runs `.github/workflows/publish.yml`. The workflow validates the source and
uses GitVersion to calculate the next version. It builds the distributions, tags the source
commit, publishes to PyPI with Trusted Publishing, and creates the matching GitHub release.
The workflow does not create commits or push changes to a branch.

Do not edit the package version or create version tags manually. Package versions are read from
Git metadata by setuptools-scm; release builds use the exact version calculated by GitVersion.

## Version selection

GitVersion uses the branch history, existing `vX.Y.Z` tags, and `GitVersion.yml`. Conventional
Commit prefixes are not required. Each new version reaching `main` is published automatically.

The title and body of the final commit on `main` become the GitHub release notes verbatim.
Describe the completed changes in the first line and add plain-text details after a blank line.
For example:

```text
Added charging estimates and subscription-aware vehicle controls

Charging status now includes remaining duration and estimated completion time.
Remote controls require confirmed vehicle support and an active subscription.
```

Release notes are published on the [GitHub releases page](https://github.com/bvdcode/nissan-connect-sdk/releases).

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

1. Develop focused changes on `develop`, then merge into `main` with the release description as
   the merge commit message.
2. CI validates linting, formatting, typing, module size, tests, and package metadata.
3. GitVersion calculates the next version.
4. The workflow builds and validates the wheel and source distribution, then creates the
   corresponding `vX.Y.Z` tag on the existing source commit.
5. Trusted Publishing uploads the artifacts to PyPI.
6. The same artifacts and commit message become the GitHub release.

PyPI release files are immutable. Fix a failed release with a new commit and version rather than
attempting to replace an uploaded file.
