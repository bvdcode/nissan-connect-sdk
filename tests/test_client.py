from __future__ import annotations

import base64
import json
from collections.abc import Mapping
from typing import Any, cast

from aiohttp import ClientSession

from pynissan import (
    NissanClient,
    Tokens,
)


class FakeResponse:
    def __init__(
        self,
        status: int,
        payload: object = None,
        *,
        body: str = "",
        url: str = "",
        headers: Mapping[str, str] | None = None,
    ) -> None:
        self.status = status
        self._payload = payload
        self._body = body
        self.url = url
        self.headers = dict(headers or {})

    async def __aenter__(self) -> FakeResponse:
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def json(self, *, content_type: object = None) -> object:
        return self._payload

    async def text(self) -> str:
        return self._body


class FakeSession:
    def __init__(self, *responses: FakeResponse) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def get(self, url: str, **kwargs: object) -> FakeResponse:
        return self._request("GET", url, kwargs)

    def post(self, url: str, **kwargs: object) -> FakeResponse:
        return self._request("POST", url, kwargs)

    def _request(self, method: str, url: str, kwargs: Mapping[str, object]) -> FakeResponse:
        self.calls.append({"method": method, "url": url, **kwargs})
        response = self.responses.pop(0)
        if not response.url:
            response.url = url
        return response


TOKENS = Tokens("access-token", "refresh-token", "id-token")


def jwt_with_expiration(expires_at: int) -> str:
    encoded_payload = (
        base64.urlsafe_b64encode(json.dumps({"exp": expires_at}).encode()).decode().rstrip("=")
    )
    return f"header.{encoded_payload}.signature"


def make_client(
    session: FakeSession,
    *,
    read_only: bool = True,
    tokens: Tokens | None = TOKENS,
) -> NissanClient:
    return NissanClient(
        cast(ClientSession, session),
        read_only=read_only,
        tokens=tokens,
    )


def vehicle_subscription_product_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "__typename": "VehicleSubscriptionProduct",
        "productId": "product-1",
        "marketingName": "Premium",
        "description": "Connected services",
        "services": ["REMOTE_ENGINE"],
    }
    payload.update(overrides)
    return payload


def vehicle_subscription_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "__typename": "VehicleSubscription",
        "subscriptionId": "subscription-1",
        "subscriptionServiceType": "Paid",
        "purchaseType": "SUBSCRIPTION",
        "productType": "TELEMATICS",
        "nextBillingDate": None,
        "goodwillEndDate": None,
        "goodwillStartDate": None,
        "graceEndDate": None,
        "subscriptionStartDate": "2026-01-01T12:00:00Z",
        "subscriptionEndDate": None,
        "isActive": True,
        "npSubscriptionPrice": None,
        "product": vehicle_subscription_product_payload(),
        "pendingOrder": None,
    }
    payload.update(overrides)
    return payload
