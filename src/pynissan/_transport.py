from __future__ import annotations

import asyncio
import base64
import inspect
import json
import time
from collections.abc import Mapping
from dataclasses import dataclass
from typing import cast
from uuid import uuid4

from aiohttp import ClientError, ClientSession, ClientTimeout

from ._profile import _CountryProfile
from .callbacks import RequestProofProvider, TokenListener
from .exceptions import (
    ApiError,
    AuthenticationError,
    GraphQLError,
    NetworkError,
    ResponseError,
)
from .models import Tokens
from .request_proof import RequestProof

type JsonObject = dict[str, object]


@dataclass(frozen=True, slots=True)
class _ApplicationToken:
    access_token: str


class _NissanTransport:
    """OAuth and GraphQL transport using a caller-owned aiohttp session."""

    def __init__(
        self,
        session: ClientSession,
        *,
        profile: _CountryProfile,
        tokens: Tokens | None = None,
        token_listener: TokenListener | None = None,
        oauth_device_id: str | None = None,
        request_proof: RequestProof | None = None,
        request_proof_provider: RequestProofProvider | None = None,
    ) -> None:
        if request_proof is not None and request_proof_provider is not None:
            raise ValueError("request_proof cannot be combined with request_proof_provider")

        self._session = session
        self._profile = profile
        self._tokens = tokens
        self._token_listener = token_listener
        self._oauth_device_id = oauth_device_id or str(uuid4())
        self._static_request_proof = request_proof
        self._request_proof_provider = request_proof_provider
        self._latest_request_proof = request_proof
        self._application_token: _ApplicationToken | None = None
        self._refresh_lock = asyncio.Lock()
        self._application_token_lock = asyncio.Lock()
        self._request_proof_refresh_lock = asyncio.Lock()

    @property
    def tokens(self) -> Tokens | None:
        """Return the currently active token set, if authenticated."""

        return self._tokens

    @property
    def oauth_device_id(self) -> str:
        """Return the device identifier used to build mobile OAuth scopes."""

        return self._oauth_device_id

    async def async_authenticate(self, email: str, password: str) -> Tokens:
        """Authenticate with MyNISSAN credentials."""

        return await self._async_request_tokens(
            {
                "username": f"NISNNAVCS/{email.strip().lower()}",
                "password": password,
                "scope": self._oauth_scope,
                "grant_type": "password",
            }
        )

    async def async_refresh_tokens(self, *, expired_access_token: str | None = None) -> Tokens:
        """Refresh the current token set, coalescing concurrent refresh attempts."""

        async with self._refresh_lock:
            current = self._require_tokens()
            if expired_access_token is not None and current.access_token != expired_access_token:
                return current
            return await self._async_request_tokens(
                {
                    "refresh_token": current.refresh_token,
                    "grant_type": "refresh_token",
                },
                previous=current,
            )

    async def async_graphql(
        self,
        operation_name: str,
        document: str,
        variables: Mapping[str, object],
        *,
        extra_headers: Mapping[str, str] | None = None,
    ) -> Mapping[str, object]:
        """Execute one authenticated GraphQL operation."""

        tokens = self._require_tokens()
        if _tokens_have_expired_jwt(tokens):
            tokens = await self.async_refresh_tokens(expired_access_token=tokens.access_token)
        request_proof = await self._async_get_request_proof(force_refresh=False)
        status, payload = await self._async_graphql_request(
            operation_name,
            document,
            variables,
            access_token=tokens.access_token,
            id_token=tokens.id_token,
            request_proof=request_proof,
            apollo_client_name=self._profile.apollo_client_name,
            apollo_client_version=self._profile.app_version,
            extra_headers=extra_headers,
        )
        if status == 401 or (status == 403 and _tokens_have_expired_jwt(tokens)):
            tokens = await self.async_refresh_tokens(expired_access_token=tokens.access_token)
            status, payload = await self._async_graphql_request(
                operation_name,
                document,
                variables,
                access_token=tokens.access_token,
                id_token=tokens.id_token,
                request_proof=request_proof,
                apollo_client_name=self._profile.apollo_client_name,
                apollo_client_version=self._profile.app_version,
                extra_headers=extra_headers,
            )

        if status == 403 and self._request_proof_provider is not None:
            refreshed_proof = await self._async_refresh_request_proof(request_proof)
            if refreshed_proof != request_proof:
                status, payload = await self._async_graphql_request(
                    operation_name,
                    document,
                    variables,
                    access_token=tokens.access_token,
                    id_token=tokens.id_token,
                    request_proof=refreshed_proof,
                    apollo_client_name=self._profile.apollo_client_name,
                    apollo_client_version=self._profile.app_version,
                    extra_headers=extra_headers,
                )

        return _extract_graphql_data(status, payload)

    async def async_application_graphql(
        self,
        operation_name: str,
        document: str,
        variables: Mapping[str, object],
    ) -> Mapping[str, object]:
        """Execute one request requiring proof before account authentication."""

        request_proof = await self._async_get_request_proof(force_refresh=False)
        if request_proof is None:
            raise AuthenticationError(403, "This operation requires request proof")

        token = await self._async_get_application_token()
        status, payload = await self._async_application_graphql_request(
            operation_name,
            document,
            variables,
            token,
            request_proof,
        )
        if status == 401 or (status == 403 and _jwt_is_expired(token.access_token)):
            token = await self._async_get_application_token(
                force_refresh=True,
                rejected_access_token=token.access_token,
            )
            status, payload = await self._async_application_graphql_request(
                operation_name,
                document,
                variables,
                token,
                request_proof,
            )

        if status == 403 and self._request_proof_provider is not None:
            refreshed_proof = await self._async_refresh_request_proof(request_proof)
            if refreshed_proof != request_proof:
                status, payload = await self._async_application_graphql_request(
                    operation_name,
                    document,
                    variables,
                    token,
                    refreshed_proof,
                )

        return _extract_graphql_data(status, payload)

    async def _async_get_application_token(
        self,
        *,
        force_refresh: bool = False,
        rejected_access_token: str | None = None,
    ) -> _ApplicationToken:
        async with self._application_token_lock:
            current = self._application_token
            if (
                current is not None
                and rejected_access_token is not None
                and current.access_token != rejected_access_token
            ):
                return current
            if (
                current is not None
                and not force_refresh
                and not _jwt_is_expired(current.access_token)
            ):
                return current

            status, payload = await self._async_post_json(
                self._profile.token_endpoint,
                data={
                    "client_id": self._profile.application_client_id,
                    "client_secret": self._profile.application_client_secret,
                    "scope": self._application_oauth_scope,
                    "grant_type": "client_credentials",
                },
            )
            if status < 200 or status >= 300:
                raise AuthenticationError(
                    status,
                    _error_message(payload, "MyNISSAN application authentication failed"),
                )
            access_token = payload.get("access_token")
            if not isinstance(access_token, str) or not access_token:
                raise ResponseError("Application token response does not contain an access token")

            token = _ApplicationToken(access_token)
            self._application_token = token
            return token

    async def _async_application_graphql_request(
        self,
        operation_name: str,
        document: str,
        variables: Mapping[str, object],
        token: _ApplicationToken,
        request_proof: RequestProof,
    ) -> tuple[int, JsonObject]:
        return await self._async_graphql_request(
            operation_name,
            document,
            variables,
            access_token=token.access_token,
            id_token=None,
            request_proof=request_proof,
            apollo_client_name=self._profile.application_apollo_client_name,
            apollo_client_version=self._profile.application_app_version,
            extra_headers=None,
        )

    async def _async_request_tokens(
        self,
        form: Mapping[str, str],
        *,
        previous: Tokens | None = None,
    ) -> Tokens:
        credentials = f"{self._profile.client_id}:{self._profile.client_secret}".encode()
        headers = {"Authorization": f"Basic {base64.b64encode(credentials).decode()}"}
        status, payload = await self._async_post_json(
            self._profile.token_endpoint,
            data=form,
            headers=headers,
        )
        if status < 200 or status >= 300:
            raise AuthenticationError(
                status,
                _error_message(payload, "MyNISSAN authentication failed"),
            )

        access_token = payload.get("access_token")
        refresh_token = payload.get("refresh_token")
        id_token = payload.get("id_token")
        if not isinstance(access_token, str) or not access_token:
            raise ResponseError("Token response does not contain an access token")
        if not isinstance(refresh_token, str) or not refresh_token:
            refresh_token = previous.refresh_token if previous is not None else None
        if not isinstance(id_token, str) or not id_token:
            id_token = previous.id_token if previous is not None else None
        if refresh_token is None:
            raise ResponseError("Token response does not contain reusable Nissan tokens")

        tokens = Tokens(
            access_token=access_token,
            refresh_token=refresh_token,
            id_token=id_token,
        )
        self._tokens = tokens
        await self._async_publish_tokens(tokens)
        return tokens

    async def _async_graphql_request(
        self,
        operation_name: str,
        document: str,
        variables: Mapping[str, object],
        *,
        access_token: str,
        id_token: str | None,
        request_proof: RequestProof | None,
        apollo_client_name: str,
        apollo_client_version: str,
        extra_headers: Mapping[str, str] | None,
    ) -> tuple[int, JsonObject]:
        headers = dict(extra_headers or {})
        headers.update(
            {
                "Authorization": f"Bearer {access_token}",
                "User-Agent": self._profile.user_agent,
                "Brand": self._profile.brand,
                "Country": self._profile.country,
                "Accept-Language": self._profile.accept_language,
                "x-correlation-id": str(uuid4()),
                "apollographql-client-name": apollo_client_name,
                "apollographql-client-version": apollo_client_version,
            }
        )
        if id_token is not None:
            headers["id-token"] = id_token
        if request_proof is not None:
            headers["X-API-Attestation"] = request_proof.api_attestation
            headers["X-Device-Status"] = request_proof.device_status
        return await self._async_post_json(
            self._profile.graphql_endpoint,
            json={
                "operationName": operation_name,
                "query": document,
                "variables": dict(variables),
            },
            headers=headers,
        )

    async def _async_get_request_proof(
        self,
        *,
        force_refresh: bool,
    ) -> RequestProof | None:
        provider = self._request_proof_provider
        if provider is None:
            return self._static_request_proof
        request_proof = await provider(force_refresh)
        self._latest_request_proof = request_proof
        return request_proof

    async def _async_refresh_request_proof(
        self,
        rejected_proof: RequestProof | None,
    ) -> RequestProof:
        provider = self._request_proof_provider
        if provider is None:
            raise RuntimeError("Request proof refresh requires a provider")

        async with self._request_proof_refresh_lock:
            if (
                self._latest_request_proof is not None
                and self._latest_request_proof != rejected_proof
            ):
                return self._latest_request_proof
            request_proof = await provider(True)
            self._latest_request_proof = request_proof
            return request_proof

    async def _async_post_json(
        self,
        url: str,
        *,
        data: Mapping[str, str] | None = None,
        json: Mapping[str, object] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> tuple[int, JsonObject]:
        request_headers = {"User-Agent": self._profile.user_agent}
        if headers is not None:
            request_headers.update(headers)
        try:
            async with self._session.post(
                url,
                data=data,
                json=json,
                headers=request_headers,
                timeout=ClientTimeout(total=self._profile.request_timeout_seconds),
            ) as response:
                status = response.status
                try:
                    payload = await response.json(content_type=None)
                except (TypeError, ValueError) as error:
                    raise ResponseError(
                        f"Nissan returned a non-JSON response with HTTP {status}"
                    ) from error
        except (TimeoutError, ClientError) as error:
            raise NetworkError("Unable to reach the Nissan service") from error

        if not isinstance(payload, dict):
            raise ResponseError("Nissan returned a non-object JSON response")
        return status, cast(JsonObject, payload)

    async def _async_publish_tokens(self, tokens: Tokens) -> None:
        if self._token_listener is None:
            return
        result = self._token_listener(tokens)
        if inspect.isawaitable(result):
            await result

    def _require_tokens(self) -> Tokens:
        if self._tokens is None:
            raise AuthenticationError(401, "The client is not authenticated")
        return self._tokens

    @property
    def _oauth_scope(self) -> str:
        return self._profile.oauth_scope.format(device_id=self._oauth_device_id)

    @property
    def _application_oauth_scope(self) -> str:
        return self._profile.application_oauth_scope.format(device_id=self._oauth_device_id)


def _error_message(payload: Mapping[str, object], fallback: str) -> str:
    for key in ("error_description", "message", "error"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return fallback


def _extract_graphql_data(status: int, payload: Mapping[str, object]) -> Mapping[str, object]:
    if status < 200 or status >= 300:
        raise ApiError(status, _error_message(payload, "Nissan API request failed"))

    data = payload.get("data")
    errors = payload.get("errors")
    if (
        isinstance(errors, list)
        and errors
        and (not isinstance(data, Mapping) or not any(value is not None for value in data.values()))
    ):
        messages = tuple(
            str(error.get("message", "Unknown GraphQL error"))
            for error in errors
            if isinstance(error, Mapping)
        )
        raise GraphQLError(messages or ("Unknown GraphQL error",))

    if not isinstance(data, Mapping):
        raise ResponseError("GraphQL response does not contain an object data field")
    return cast(Mapping[str, object], data)


def _jwt_is_expired(token: str, *, leeway_seconds: int = 30) -> bool:
    try:
        encoded_payload = token.split(".")[1]
        encoded_payload += "=" * (-len(encoded_payload) % 4)
        payload = json.loads(base64.urlsafe_b64decode(encoded_payload))
        expires_at = payload.get("exp")
    except (IndexError, ValueError, TypeError, json.JSONDecodeError):
        return False
    return (
        isinstance(expires_at, int)
        and not isinstance(expires_at, bool)
        and expires_at <= time.time() + leeway_seconds
    )


def _tokens_have_expired_jwt(tokens: Tokens) -> bool:
    return _jwt_is_expired(tokens.access_token) or (
        tokens.id_token is not None and _jwt_is_expired(tokens.id_token)
    )
