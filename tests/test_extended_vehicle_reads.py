from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from typing import cast

from aiohttp import ClientSession

from pynissan import NissanClient, Tokens


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
    "DrivingHistory": "55c6560e71d7b5f267e7edfabced0c4dbe9e5240d034b3e8ab579d2ad5b0152e",
    "EVChargeStations": "18b57f6f03c5c1552323f1a95c25af0929be916e190ca7c2be04ab19fa78e383",
    "eVehicleEligibility": "7c2bcccfa5c0d963a580c8aa536a1354b34ac84e69502cc1d66f2e7ce3adca8c",
    "LastKnownCameraUsageCounter": (
        "975fb5c31998d845d5546d71233e53ca45d2c377d823d00fee0c373af111599e"
    ),
    "LocationDetails": "a17394651892824a08fc8ddec625d9aa1641f89f101fad2139235986ca174ffc",
    "ParkingChargeable": "6ec1a2169360a3edd23aab2321a1efa54b81e22f6a0e83a456cbc3413182ee30",
    "ShareableCapabilities": ("46ce25e824af31aea94723979e168bc0494a51a210287c3a314e0d9e0df00c25"),
    "TariffPricing": "8fe80027d8aad800cef5c59ed797854822a2f5c09aaaa684ac49151208823f4f",
}


def graphql_response(data: Mapping[str, object]) -> FakeResponse:
    return FakeResponse({"data": dict(data)})


def make_client(session: FakeSession) -> NissanClient:
    return NissanClient(
        cast(ClientSession, session),
        read_only=True,
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
