from __future__ import annotations

import inspect
from importlib.metadata import version

import pynissan
from pynissan import Country, NissanClient, RequestProof, RequestProofProvider, TokenListener


def test_package_version_matches_installed_metadata() -> None:
    assert pynissan.__version__ == version("pynissan")


def test_client_configuration_uses_country_selector() -> None:
    parameters = inspect.signature(NissanClient).parameters

    assert parameters["country"].default is Country.US
    assert "config" not in parameters


def test_public_classes_and_functions_have_docstrings() -> None:
    missing = tuple(
        name
        for name in pynissan.__all__
        if (inspect.isclass(value := getattr(pynissan, name)) or inspect.isfunction(value))
        and inspect.getdoc(value) is None
    )

    assert missing == ()


def test_transport_and_service_profiles_are_not_exported() -> None:
    assert TokenListener is pynissan.TokenListener
    assert RequestProof is pynissan.RequestProof
    assert RequestProofProvider is pynissan.RequestProofProvider
    assert "_NissanTransport" not in pynissan.__all__
    assert "_CountryProfile" not in pynissan.__all__
