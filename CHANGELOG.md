# Changelog

All notable changes to `pynissan` are documented in this file.

The project follows [Semantic Versioning](https://semver.org/).

<!-- version list -->

## v0.1.0 (2026-08-01)

### Bug Fixes

- Harden command status and enum inputs
  ([`415326b`](https://github.com/bvdcode/nissan-connect-sdk/commit/415326b528332d6c835c9a6a3ea6743a39d15dd4))

- Surface polling timeouts consistently
  ([`527172e`](https://github.com/bvdcode/nissan-connect-sdk/commit/527172ee532c4d7955ba2d3cbe7b44540962ea66))

### Continuous Integration

- Automate semantic releases
  ([`f2bb388`](https://github.com/bvdcode/nissan-connect-sdk/commit/f2bb38822fe8aaba230e441a4201ba74898c421a))

- Automate tagged releases
  ([`2d63335`](https://github.com/bvdcode/nissan-connect-sdk/commit/2d6333561aa02ee60744d03dce4e3673722855c9))

- Automate validation and PyPI publishing
  ([`697274a`](https://github.com/bvdcode/nissan-connect-sdk/commit/697274aeb91d95da5e39bc529bec8a479efcd99a))

- Enforce Python module size limit
  ([`5192435`](https://github.com/bvdcode/nissan-connect-sdk/commit/5192435c10fdb132f474842c260b3b03bd63053f))

- Install release build tooling
  ([`c5cf9c2`](https://github.com/bvdcode/nissan-connect-sdk/commit/c5cf9c26dd637f170897d95e1d7bc5affbf7b792))

### Documentation

- Describe protected request configuration
  ([`f304cf8`](https://github.com/bvdcode/nissan-connect-sdk/commit/f304cf84e596a22bbd35dcb977e41dc7cc9937c2))

- Prepare the package for release
  ([`1087b74`](https://github.com/bvdcode/nissan-connect-sdk/commit/1087b74f2563a90b98c3f9103b881637cc8c7d8b))

### Features

- Add the pynissan async client
  ([`21f8dbc`](https://github.com/bvdcode/nissan-connect-sdk/commit/21f8dbcd439c68afa1e72c4ae8b889fddccd22cb))

- Support protected onboarding requests
  ([`c68dce3`](https://github.com/bvdcode/nissan-connect-sdk/commit/c68dce32dfa741c34144da1631d967808f1e95e3))

### Refactoring

- Keep transport internals private
  ([`92e4c9c`](https://github.com/bvdcode/nissan-connect-sdk/commit/92e4c9cf5b0bff599091edc87bc4a6f5f59a47f0))

- Split account feature parsers
  ([`397dd50`](https://github.com/bvdcode/nissan-connect-sdk/commit/397dd505b9fe2931a56a42242842ff430aac946c))

- Split client by service domain
  ([`26d71a4`](https://github.com/bvdcode/nissan-connect-sdk/commit/26d71a414c597b833626740b2357230f13ded855))

- Split core domain models
  ([`1df47fb`](https://github.com/bvdcode/nissan-connect-sdk/commit/1df47fb07f5eea54b07ff8aaa99964020cedb6e7))

- Split oversized test modules
  ([`50247a8`](https://github.com/bvdcode/nissan-connect-sdk/commit/50247a8368d2a884443f37bf0cb84153864d1d67))

- Split vehicle service parsers
  ([`9408521`](https://github.com/bvdcode/nissan-connect-sdk/commit/9408521515e8e225f9864eb5ec7dc05640f53a1c))

### Testing

- Cover connected vehicle operations
  ([`6129b49`](https://github.com/bvdcode/nissan-connect-sdk/commit/6129b49a1b451eae5bddf42c9761b3fdbd08b275))
