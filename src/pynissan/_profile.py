from dataclasses import dataclass
from typing import assert_never
from urllib.parse import urlunsplit

from .countries import Country


@dataclass(frozen=True, slots=True)
class _CountryProfile:
    """Service endpoints and application metadata for one country."""

    token_endpoint: str
    graphql_endpoint: str
    account_namespace: str
    client_id: str
    client_secret: str
    oauth_scope: str
    app_package: str
    app_version: str
    application_client_id: str
    application_client_secret: str
    application_oauth_scope: str
    application_app_package: str
    application_app_version: str
    brand: str
    country: Country
    accept_language: str
    user_agent: str
    request_timeout_seconds: float = 30.0

    @property
    def apollo_client_name(self) -> str:
        """Return the Apollo client identifier sent with GraphQL requests."""

        return f"{self.app_package}:android"

    @property
    def application_apollo_client_name(self) -> str:
        """Return the Apollo identifier used before account authentication."""

        return f"{self.application_app_package}:android"


_ACCOUNT_NAMESPACE = "NISNNAVCS"


def _https_endpoint(host: tuple[str, ...], *path: str) -> str:
    return urlunsplit(("https", ".".join(host), "/".join(path), "", ""))


_TOKEN_ENDPOINT = _https_endpoint(("services", "nissanusa", "com"), "token")
_GRAPHQL_ENDPOINT = _https_endpoint(
    ("api-ccs", "na", "nissancloud", "com"),
    "iotmw-hades-ccs",
    "graphql",
)


_US_PROFILE = _CountryProfile(
    token_endpoint=_TOKEN_ENDPOINT,
    graphql_endpoint=_GRAPHQL_ENDPOINT,
    account_namespace=_ACCOUNT_NAMESPACE,
    client_id="iT1JQ_0O4fLcdeDOsLiFXnkDQr8a",
    client_secret="DZ_FfwmunpUUTaNZZ7yDz_fc7Loa",
    oauth_scope="ROP internal_login openid",
    app_package="com.nissan.mynissan",
    app_version="6.9.110",
    application_client_id="6wYMOME6Rs4kWVxS4i6b2RUsR4Ma",
    application_client_secret="fWp6esCzsq3vCY6RLf3p_CV_ukAa",
    application_oauth_scope="openid device_{device_id}",
    application_app_package="com.nissan.mynissan",
    application_app_version="6.9.110",
    brand="Nissan",
    country=Country.US,
    accept_language="en-US",
    user_agent="okhttp/5.2.1",
)

_CA_PROFILE = _CountryProfile(
    token_endpoint=_TOKEN_ENDPOINT,
    graphql_endpoint=_GRAPHQL_ENDPOINT,
    account_namespace=_ACCOUNT_NAMESPACE,
    client_id="v9no_nW7GqHYsfAKkki6_N5AFVIa",
    client_secret="Ynn56ncVx0yVffnDHIIMTWVYiuAa",
    oauth_scope="openid device_{device_id}+internal_login",
    app_package="ca.nissan.nissanconnectservices",
    app_version="9.9.91",
    application_client_id="v9no_nW7GqHYsfAKkki6_N5AFVIa",
    application_client_secret="Ynn56ncVx0yVffnDHIIMTWVYiuAa",
    application_oauth_scope="openid device_{device_id}",
    application_app_package="ca.nissan.nissanconnectservices",
    application_app_version="9.9.91",
    brand="Nissan",
    country=Country.CA,
    accept_language="en-CA",
    user_agent="okhttp/5.2.1",
)

_MX_PROFILE = _CountryProfile(
    token_endpoint=_TOKEN_ENDPOINT,
    graphql_endpoint=_GRAPHQL_ENDPOINT,
    account_namespace=_ACCOUNT_NAMESPACE,
    client_id="5RVUrd6tfV61TtlWFpLGm6UYoDka",
    client_secret="vI_X2L2trvXhg94Q9DxAJdHXyJ0a",
    oauth_scope="openid device_{device_id}+internal_login",
    app_package="com.nissan.droid.mynissan",
    app_version="6.2.31",
    application_client_id="5RVUrd6tfV61TtlWFpLGm6UYoDka",
    application_client_secret="vI_X2L2trvXhg94Q9DxAJdHXyJ0a",
    application_oauth_scope="openid device_{device_id}",
    application_app_package="com.nissan.droid.mynissan",
    application_app_version="6.2.31",
    brand="Nissan",
    country=Country.MX,
    accept_language="es-MX",
    user_agent="okhttp/4.12.0",
)


def profile_for(country: Country) -> _CountryProfile:
    """Return the service profile for a supported country."""

    match country:
        case Country.US:
            return _US_PROFILE
        case Country.CA:
            return _CA_PROFILE
        case Country.MX:
            return _MX_PROFILE

    assert_never(country)
