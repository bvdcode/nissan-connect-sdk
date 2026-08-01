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
    "VehiclePreferredDealer": ("0f31228d3c3f194d4951c8eda4477e79a4f59f44006a6b2a9299f1f7d8f57f41"),
    "VehicleRecalls": "7990ac9acf158db899f2bec6ba65034216db0f4c660078572c41a8c3b30f9748",
    "VehicleRoadsideAssistance": (
        "be0546f4ee9a7eab4243b1378caa301d15fcc02ee6bedccc33c5b6e8720252b3"
    ),
    "VehicleServiceHistory": ("6df1797f48fb3832587e2d9407c38106632cc3c4ac40056d26223a0359ec4b11"),
    "WarrantyInfo": "4be940f109c5d0f868acf7f8700da4d332bd34cf52bc28300811d6524512f26a",
}


def graphql_response(data: Mapping[str, object]) -> FakeResponse:
    return FakeResponse({"data": dict(data)})


def vehicle_data(**fields: object) -> dict[str, object]:
    return {"vehicle": {"__typename": "AVKVehicle", **fields}}


def preferred_dealer(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "__typename": "Dealer",
        "id": "dealer-id",
        "hashId": "dealer-hash",
        "name": "Nissan San Diego",
        "address": {
            "__typename": "Address",
            "address1": "1 Main St",
            "address2": "Suite 2",
            "city": "San Diego",
            "state": "CA",
            "postalCode": "92101",
            "country": "US",
        },
        "hours": "Mon-Fri",
        "phone": "555-0100",
        "servicePhone": "555-0101",
        "nativeServiceBooking": True,
        "schedulingUrlMobile": "https://example.test/service",
        "location": {
            "__typename": "Location",
            "latitude": 32.7157,
            "longitude": -117.1611,
        },
        "languagesSpoken": ["English", "Spanish"],
    }
    result.update(overrides)
    return result


def recall(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "__typename": "Recall",
        "effectiveDate": "2026-02-03T04:05:06-08:00",
        "nhtsaId": "26V001",
        "primaryDescription": "Primary description",
        "remedyDescription": "Remedy description",
        "riskDescription": "Risk description",
        "title": "Campaign title",
        "type": "RECALL",
        "recallCode": "PC001",
    }
    result.update(overrides)
    return result


def service_history_entry(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "__typename": "ServiceHistory",
        "mileageWithUnit": {
            "__typename": "Mileage",
            "unit": "MILE",
            "value": 12345,
        },
        "serviceDate": "2026-03-04T05:06:07Z",
        "dealerName": "Nissan San Diego",
        "dealerCode": "CA001",
        "services": ["Inspection", "Tire rotation"],
        "comment": "Completed",
        "maintenanceId": 42,
        "serviceOperation": {
            "__typename": "ServiceOperation",
            "serviceCategoryId": "category-id",
            "serviceCategoryName": "Maintenance",
            "opCodeID": "OP-1",
            "opCodeDescription": "Scheduled service",
        },
    }
    result.update(overrides)
    return result


def warranty(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "__typename": "Warranty",
        "warrantyInfo": {
            "__typename": "WarrantyInfo",
            "colorStatus": "GREEN",
            "warrantyStatus": "ACTIVE",
            "totalMileage": 36000,
            "totalMonths": "36",
        },
        "startPeriod": {
            "__typename": "WarrantyPeriod",
            "mileage": 0,
            "date": "2024-01-02",
        },
        "endPeriod": {
            "__typename": "WarrantyPeriod",
            "mileage": 36000,
            "date": "2027-01-02",
        },
        "currentPeriod": {
            "__typename": "WarrantyPeriod",
            "mileage": 12000,
            "date": "2026-07-31",
        },
    }
    result.update(overrides)
    return result


def without_field(value: Mapping[str, object], field: str) -> dict[str, object]:
    result = dict(value)
    del result[field]
    return result


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
