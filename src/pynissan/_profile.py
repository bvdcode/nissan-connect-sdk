from dataclasses import dataclass
from typing import assert_never

from .countries import Country


@dataclass(frozen=True, slots=True)
class _CountryProfile:
    """Service endpoints and application metadata for one country."""

    token_endpoint: str
    graphql_endpoint: str
    client_id: str
    client_secret: str
    oauth_scope: str
    app_package: str
    app_version: str
    brand: str
    country: Country
    accept_language: str
    user_agent: str
    request_timeout_seconds: float = 30.0

    @property
    def apollo_client_name(self) -> str:
        """Return the Apollo client identifier sent with GraphQL requests."""

        return f"{self.app_package}:android"


_US_PROFILE = _CountryProfile(
    token_endpoint="https://services.nissanusa.com/token",
    graphql_endpoint="https://api-ccs.na.nissancloud.com/iotmw-hades-ccs/graphql",
    client_id="v9no_nW7GqHYsfAKkki6_N5AFVIa",
    client_secret="Ynn56ncVx0yVffnDHIIMTWVYiuAa",
    oauth_scope="openid device_{device_id}+internal_login",
    app_package="ca.nissan.nissanconnectservices",
    app_version="9.9.91",
    brand="Nissan",
    country=Country.US,
    accept_language="en-US",
    user_agent="okhttp/5.2.1",
)


def profile_for(country: Country) -> _CountryProfile:
    """Return the internal service profile for a supported country."""

    match country:
        case Country.US:
            return _US_PROFILE

    assert_never(country)
