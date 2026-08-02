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
_MOBILE_CLIENT_ID = "v9no_nW7GqHYsfAKkki6_N5AFVIa"
_MOBILE_CLIENT_SECRET = "Ynn56ncVx0yVffnDHIIMTWVYiuAa"
_MOBILE_OAUTH_SCOPE = "openid device_{device_id}+internal_login"
_MOBILE_APP_PACKAGE = "ca.nissan.nissanconnectservices"
_MOBILE_APP_VERSION = "9.9.91"
_MOBILE_USER_AGENT = "okhttp/5.2.1"


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
    client_id=_MOBILE_CLIENT_ID,
    client_secret=_MOBILE_CLIENT_SECRET,
    oauth_scope=_MOBILE_OAUTH_SCOPE,
    app_package=_MOBILE_APP_PACKAGE,
    app_version=_MOBILE_APP_VERSION,
    application_client_id="6wYMOME6Rs4kWVxS4i6b2RUsR4Ma",
    application_client_secret="fWp6esCzsq3vCY6RLf3p_CV_ukAa",
    application_oauth_scope="openid device_{device_id}",
    application_app_package="com.nissan.mynissan",
    application_app_version="6.9.110",
    brand="Nissan",
    country=Country.US,
    accept_language="en-US",
    user_agent=_MOBILE_USER_AGENT,
)

_CA_PROFILE = _CountryProfile(
    token_endpoint=_TOKEN_ENDPOINT,
    graphql_endpoint=_GRAPHQL_ENDPOINT,
    account_namespace=_ACCOUNT_NAMESPACE,
    client_id=_MOBILE_CLIENT_ID,
    client_secret=_MOBILE_CLIENT_SECRET,
    oauth_scope=_MOBILE_OAUTH_SCOPE,
    app_package=_MOBILE_APP_PACKAGE,
    app_version=_MOBILE_APP_VERSION,
    application_client_id=_MOBILE_CLIENT_ID,
    application_client_secret=_MOBILE_CLIENT_SECRET,
    application_oauth_scope="openid device_{device_id}",
    application_app_package=_MOBILE_APP_PACKAGE,
    application_app_version=_MOBILE_APP_VERSION,
    brand="Nissan",
    country=Country.CA,
    accept_language="en-CA",
    user_agent=_MOBILE_USER_AGENT,
)

_MX_PROFILE = _CountryProfile(
    token_endpoint=_TOKEN_ENDPOINT,
    graphql_endpoint=_GRAPHQL_ENDPOINT,
    account_namespace=_ACCOUNT_NAMESPACE,
    client_id=_MOBILE_CLIENT_ID,
    client_secret=_MOBILE_CLIENT_SECRET,
    oauth_scope=_MOBILE_OAUTH_SCOPE,
    app_package=_MOBILE_APP_PACKAGE,
    app_version=_MOBILE_APP_VERSION,
    application_client_id="5RVUrd6tfV61TtlWFpLGm6UYoDka",
    application_client_secret="vI_X2L2trvXhg94Q9DxAJdHXyJ0a",
    application_oauth_scope="openid device_{device_id}",
    application_app_package="com.nissan.droid.mynissan",
    application_app_version="6.2.31",
    brand="Nissan",
    country=Country.MX,
    accept_language="es-MX",
    user_agent=_MOBILE_USER_AGENT,
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
