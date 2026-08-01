from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from typing import cast

from aiohttp import ClientSession

from pynissan import (
    NissanClient,
    Tokens,
)


class FakeResponse:
    def __init__(self, payload: Mapping[str, object]) -> None:
        self.status = 200
        self._payload = payload

    async def __aenter__(self) -> FakeResponse:
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def json(self, *, content_type: object = None) -> object:
        return self._payload


class FakeSession:
    def __init__(self, *responses: FakeResponse) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, object]] = []

    def post(self, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"url": url, **kwargs})
        if not self.responses:
            raise AssertionError("Unexpected HTTP request")
        return self.responses.pop(0)


TOKENS = Tokens("access-token", "refresh-token", "id-token")

EXPECTED_QUERY_TOKEN_HASHES = {
    "PNCServiceStatus": "8e5faf53447663be5f531982756936d5d89e67de6bb41f743da95ba3eb1a953d",
    "StartChargeSession": "0b9d134d2abd860cd43a826ec1d07fd6e260af629c8da56117410dffdca5bee7",
    "StopChargeSession": "4648f5902628a8393dc6ca401b640f3f793e8ccecd54c1f460097bd3231b01cd",
    "UpdatePnCServiceStatus": ("b295b10adb0ab3f909c79ceef445e5600bf802c37e1175f6788ccb4abd4ea6a6"),
    "RetryCertInstall": "9a8a1986b379936600807df51cb5e1b8948e55729e9b32fb306b6fcb83ae2571",
    "ChargeSessionStatus": "fea805ebe2313ced668deb5a04175f1e36ef3c004bd0d378b611f879cb0f89a5",
}


def graphql_response(data: Mapping[str, object]) -> FakeResponse:
    return FakeResponse({"data": dict(data)})


def make_client(session: FakeSession, *, read_only: bool = True) -> NissanClient:
    return NissanClient(
        cast(ClientSession, session),
        read_only=read_only,
        tokens=TOKENS,
    )


def assert_graphql_call(
    session: FakeSession,
    index: int,
    operation_name: str,
    variables: Mapping[str, object],
) -> None:
    payload = session.calls[index].get("json")
    assert isinstance(payload, Mapping)
    assert payload["operationName"] == operation_name
    assert payload["variables"] == variables
    document = payload["query"]
    assert isinstance(document, str)
    tokens = " ".join(re.findall(r"\.\.\.|[_A-Za-z][_0-9A-Za-z]*|[$!():{}\[\]]", document))
    assert (
        hashlib.sha256(tokens.encode()).hexdigest() == EXPECTED_QUERY_TOKEN_HASHES[operation_name]
    )
