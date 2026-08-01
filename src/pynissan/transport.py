from __future__ import annotations

import asyncio
import base64
import inspect
import json
import time
from collections.abc import Awaitable, Callable, Mapping
from typing import cast
from uuid import uuid4

from aiohttp import ClientError, ClientSession, ClientTimeout

from ._profile import _CountryProfile
from .exceptions import (
    ApiError,
    AuthenticationError,
    GraphQLError,
    NetworkError,
    ResponseError,
)
from .models import Tokens

type JsonObject = dict[str, object]
type TokenListener = Callable[[Tokens], Awaitable[None] | None]


class NissanTransport:
    """OAuth and GraphQL transport using a caller-owned aiohttp session."""

    def __init__(
        self,
        session: ClientSession,
        *,
        profile: _CountryProfile,
        tokens: Tokens | None = None,
        token_listener: TokenListener | None = None,
        oauth_device_id: str | None = None,
    ) -> None:
        self._session = session
        self._profile = profile
        self._tokens = tokens
        self._token_listener = token_listener
        self._oauth_device_id = oauth_device_id or str(uuid4())
        self._refresh_lock = asyncio.Lock()

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
        status, payload = await self._async_graphql_request(
            operation_name,
            document,
            variables,
            tokens,
            extra_headers,
        )
        if status == 401 or (status == 403 and _tokens_have_expired_jwt(tokens)):
            tokens = await self.async_refresh_tokens(expired_access_token=tokens.access_token)
            status, payload = await self._async_graphql_request(
                operation_name,
                document,
                variables,
                tokens,
                extra_headers,
            )

        if status < 200 or status >= 300:
            raise ApiError(status, _error_message(payload, "Nissan API request failed"))

        data = payload.get("data")
        errors = payload.get("errors")
        if (
            isinstance(errors, list)
            and errors
            and (
                not isinstance(data, Mapping)
                or not any(value is not None for value in data.values())
            )
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
        tokens: Tokens,
        extra_headers: Mapping[str, str] | None,
    ) -> tuple[int, JsonObject]:
        headers = dict(extra_headers or {})
        headers.update(
            {
                "Authorization": f"Bearer {tokens.access_token}",
                "User-Agent": self._profile.user_agent,
                "Brand": self._profile.brand,
                "Country": self._profile.country,
                "Accept-Language": self._profile.accept_language,
                "x-correlation-id": str(uuid4()),
                "apollographql-client-name": self._profile.apollo_client_name,
                "apollographql-client-version": self._profile.app_version,
            }
        )
        if tokens.id_token is not None:
            headers["id-token"] = tokens.id_token
        return await self._async_post_json(
            self._profile.graphql_endpoint,
            json={
                "operationName": operation_name,
                "query": document,
                "variables": dict(variables),
            },
            headers=headers,
        )

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


def _error_message(payload: Mapping[str, object], fallback: str) -> str:
    for key in ("error_description", "message", "error"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    return fallback


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
