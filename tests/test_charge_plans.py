from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Mapping
from dataclasses import FrozenInstanceError
from typing import cast

import pytest
from aiohttp import ClientSession

from pynissan import (
    NissanClient,
    ReadOnlyError,
    Tokens,
    operations,
)
from pynissan.charge_plan_inputs import (
    cancel_charge_plan_variables,
    charge_product_variables,
    enroll_charge_plan_variables,
    pricing_details_variables,
)
from pynissan.charge_plan_models import (
    ChargePlanAccountStatus,
    ChargePlanCancellationOutcome,
    ChargePlanCancellationResult,
    ChargePlanEnrollmentData,
    ChargePlanEnrollmentResult,
    ChargePlanPricingConnector,
    ChargePlanPricingDetails,
    ChargePlanPricingEvse,
    ChargeProductData,
    ChargeProductResult,
)
from pynissan.charge_plan_parsing import (
    parse_cancel_charge_plan,
    parse_charge_product,
    parse_enroll_charge_plan,
    parse_pricing_details,
)
from pynissan.exceptions import ResponseError

EXPECTED_OPERATIONS = {
    "ChargeProduct": (
        operations.CHARGE_PRODUCT,
        operations.CHARGE_PRODUCT_OPERATION_ID,
        "8c707418299ea7636b8b80f307e4cbad719c8bd348eb8243dc4e7c50ae037a9a",
    ),
    "PricingDetails": (
        operations.PRICING_DETAILS,
        operations.PRICING_DETAILS_OPERATION_ID,
        "fc33f94f7659158617ad457cf5a3a92ea6a906f45f1b0086bf38626594e3c2c9",
    ),
    "EnrollChargePlan": (
        operations.ENROLL_CHARGE_PLAN,
        operations.ENROLL_CHARGE_PLAN_OPERATION_ID,
        "04aa3a8cafdb0be5fd0a51927b6f5a0a2bd0318a6519957a6b3a466406924ea7",
    ),
    "CancelChargePlan": (
        operations.CANCEL_CHARGE_PLAN,
        operations.CANCEL_CHARGE_PLAN_OPERATION_ID,
        "6143736732d743059868f2a9ac3688791892fcb3d5849f4b7d7bc32e95948eab",
    ),
}


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


def make_client(session: FakeSession, *, read_only: bool = True) -> NissanClient:
    return NissanClient(
        cast(ClientSession, session),
        tokens=Tokens("access-token", "refresh-token", "id-token"),
        read_only=read_only,
    )


def graphql_response(data: Mapping[str, object]) -> FakeResponse:
    return FakeResponse({"data": dict(data)})


@pytest.mark.parametrize(
    ("operation_name", "document", "operation_id", "token_hash"),
    [(operation_name, *values) for operation_name, values in EXPECTED_OPERATIONS.items()],
)
def test_charge_plan_operations_match_service_documents_and_ids(
    operation_name: str,
    document: str,
    operation_id: str,
    token_hash: str,
) -> None:
    assert document.startswith((f"query {operation_name}", f"mutation {operation_name}"))
    assert hashlib.sha256(document.encode()).hexdigest() == operation_id
    tokens = " ".join(re.findall(r"\.\.\.|[_A-Za-z][_0-9A-Za-z]*|[$!():{}\[\]]", document))
    assert hashlib.sha256(tokens.encode()).hexdigest() == token_hash


def test_charge_plan_variables_match_non_null_service_inputs() -> None:
    assert charge_product_variables("VIN") == {"vin": "VIN"}
    assert pricing_details_variables("VIN", "LOCATION-1") == {
        "locationId": "LOCATION-1",
        "vin": "VIN",
    }
    assert enroll_charge_plan_variables(
        "VIN",
        "SKU-1",
        "ARIYA",
        "2026",
    ) == {
        "config": {
            "vin": "VIN",
            "productSku": "SKU-1",
            "model": "ARIYA",
            "year": "2026",
        }
    }
    assert cancel_charge_plan_variables("VIN") == {"config": {"vin": "VIN"}}


async def test_charge_plan_client_wires_all_four_operations() -> None:
    session = FakeSession(
        graphql_response({"chargeProduct": None}),
        graphql_response({"pricingDetails": None}),
        graphql_response({"enrollChargePlan": None}),
        graphql_response({"cancelChargePlan": None}),
    )
    client = make_client(session, read_only=False)

    assert await client.async_get_charge_product("VIN") is None
    assert await client.async_get_charge_plan_pricing_details("VIN", "LOCATION-1") is None
    assert await client.async_enroll_charge_plan("VIN", "SKU-1", "ARIYA", "2026") is None
    assert await client.async_cancel_charge_plan("VIN") is None

    payloads = [call["json"] for call in session.calls]
    assert all(isinstance(payload, Mapping) for payload in payloads)
    assert [payload["operationName"] for payload in payloads] == [
        "ChargeProduct",
        "PricingDetails",
        "EnrollChargePlan",
        "CancelChargePlan",
    ]
    assert [payload["variables"] for payload in payloads] == [
        {"vin": "VIN"},
        {"locationId": "LOCATION-1", "vin": "VIN"},
        {
            "config": {
                "vin": "VIN",
                "productSku": "SKU-1",
                "model": "ARIYA",
                "year": "2026",
            }
        },
        {"config": {"vin": "VIN"}},
    ]


async def test_charge_plan_mutations_respect_read_only_before_io() -> None:
    session = FakeSession()
    client = make_client(session)

    with pytest.raises(ReadOnlyError):
        await client.async_enroll_charge_plan("VIN", "SKU-1", "ARIYA", "2026")
    with pytest.raises(ReadOnlyError):
        await client.async_cancel_charge_plan("VIN")

    assert session.calls == []


def test_parse_charge_product_preserves_nullable_status_and_product_fields() -> None:
    result = parse_charge_product(
        {
            "chargeProduct": {
                "__typename": "EmpChargeProductResponse",
                "statusCode": "1000",
                "statusMessage": None,
                "timestamp": "2026-07-31T12:00:00Z",
                "data": {
                    "__typename": "EmpChargeProductData",
                    "productSKU": "SKU-1",
                    "price": "12.50",
                    "description": None,
                },
            }
        }
    )

    assert result == ChargeProductResult(
        status_code="1000",
        status_message=None,
        timestamp="2026-07-31T12:00:00Z",
        data=ChargeProductData(
            product_sku="SKU-1",
            price="12.50",
            description=None,
        ),
    )


def test_parse_pricing_details_preserves_nullable_lists_and_items() -> None:
    result = parse_pricing_details(
        {
            "pricingDetails": {
                "__typename": "EmpPricingDetailsResponse",
                "data": {
                    "__typename": "EmpPricingDetailsData",
                    "parkingTariff": "5.00",
                    "flatFee": None,
                    "congestionFee": "2.00",
                    "evses": [
                        None,
                        {
                            "__typename": "EmpEVSE",
                            "connectors": [
                                None,
                                {
                                    "__typename": "EmpConnector",
                                    "connectorId": "CONNECTOR-1",
                                    "tariff": None,
                                },
                            ],
                        },
                    ],
                },
            }
        }
    )

    assert result == ChargePlanPricingDetails(
        parking_tariff="5.00",
        flat_fee=None,
        congestion_fee="2.00",
        evses=(
            None,
            ChargePlanPricingEvse(
                connectors=(
                    None,
                    ChargePlanPricingConnector("CONNECTOR-1", None),
                )
            ),
        ),
    )


@pytest.mark.parametrize(
    "raw_status",
    [
        "PENDING",
        "FAILED",
        "ACTIVE",
        "INACTIVE",
        "CANCELLED",
        "CLOSED",
        "ENROLLING",
        "NOT_ENROLLED",
    ],
)
def test_parse_enrollment_maps_every_service_account_status(raw_status: str) -> None:
    result = parse_enroll_charge_plan(
        {
            "enrollChargePlan": {
                "__typename": "EmpEnrollChargePlanResponse",
                "statusCode": "1000",
                "statusMessage": "accepted",
                "timestamp": "now",
                "data": {
                    "__typename": "EmpEnrollChargePlanData",
                    "vin": "VIN",
                    "status": raw_status,
                },
            }
        }
    )

    assert result == ChargePlanEnrollmentResult(
        "1000",
        "accepted",
        "now",
        ChargePlanEnrollmentData("VIN", ChargePlanAccountStatus(raw_status)),
    )


def test_parse_enrollment_maps_future_status_to_unknown_value() -> None:
    result = parse_enroll_charge_plan(
        {
            "enrollChargePlan": {
                "__typename": "EmpEnrollChargePlanResponse",
                "data": {
                    "__typename": "EmpEnrollChargePlanData",
                    "vin": None,
                    "status": "FUTURE_STATE",
                },
            }
        }
    )

    assert result == ChargePlanEnrollmentResult(
        None,
        None,
        None,
        ChargePlanEnrollmentData(None, ChargePlanAccountStatus.UNKNOWN_VALUE),
    )


@pytest.mark.parametrize(
    ("status_code", "outcome"),
    [
        ("1000", ChargePlanCancellationOutcome.SUCCESS),
        ("5000", ChargePlanCancellationOutcome.FAILED),
        ("4011", ChargePlanCancellationOutcome.UNKNOWN),
        ("future", ChargePlanCancellationOutcome.UNKNOWN),
        (None, ChargePlanCancellationOutcome.UNKNOWN),
    ],
)
def test_cancel_charge_plan_outcome_matches_service(
    status_code: str | None,
    outcome: ChargePlanCancellationOutcome,
) -> None:
    result = parse_cancel_charge_plan(
        {
            "cancelChargePlan": {
                "__typename": "EmpCancelChargePlanResponse",
                "statusCode": status_code,
                "statusMessage": None,
                "timestamp": None,
            }
        }
    )

    assert result == ChargePlanCancellationResult(status_code, None, None)
    assert result is not None
    assert result.outcome is outcome


@pytest.mark.parametrize(
    ("parser", "root_field"),
    [
        (parse_charge_product, "chargeProduct"),
        (parse_pricing_details, "pricingDetails"),
        (parse_enroll_charge_plan, "enrollChargePlan"),
        (parse_cancel_charge_plan, "cancelChargePlan"),
    ],
)
def test_charge_plan_parsers_preserve_nullable_roots(
    parser: Callable[[Mapping[str, object]], object | None],
    root_field: str,
) -> None:
    assert parser({root_field: None}) is None
    with pytest.raises(ResponseError, match=rf"^{root_field} is missing$"):
        parser({})


def test_nullable_data_and_lists_remain_distinct_from_empty_lists() -> None:
    assert (
        parse_pricing_details(
            {
                "pricingDetails": {
                    "__typename": "EmpPricingDetailsResponse",
                    "data": None,
                }
            }
        )
        is None
    )
    details = parse_pricing_details(
        {
            "pricingDetails": {
                "__typename": "EmpPricingDetailsResponse",
                "data": {
                    "__typename": "EmpPricingDetailsData",
                    "evses": [],
                },
            }
        }
    )
    assert details == ChargePlanPricingDetails(None, None, None, ())

    product = parse_charge_product(
        {
            "chargeProduct": {
                "__typename": "EmpChargeProductResponse",
                "data": None,
            }
        }
    )
    enrollment = parse_enroll_charge_plan(
        {
            "enrollChargePlan": {
                "__typename": "EmpEnrollChargePlanResponse",
                "data": None,
            }
        }
    )
    assert product == ChargeProductResult(None, None, None, None)
    assert enrollment == ChargePlanEnrollmentResult(None, None, None, None)


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"chargeProduct": {}}, "chargeProduct.__typename is not a string"),
        (
            {
                "chargeProduct": {
                    "__typename": "EmpChargeProductResponse",
                    "statusCode": 1000,
                }
            },
            "chargeProduct.statusCode is not a string",
        ),
        (
            {
                "pricingDetails": {
                    "__typename": "EmpPricingDetailsResponse",
                    "data": {
                        "__typename": "EmpPricingDetailsData",
                        "evses": "not-a-list",
                    },
                }
            },
            "pricingDetails.data.evses is not a list",
        ),
        (
            {
                "pricingDetails": {
                    "__typename": "EmpPricingDetailsResponse",
                    "data": {
                        "__typename": "EmpPricingDetailsData",
                        "evses": [{"__typename": "EmpEVSE", "connectors": [{}]}],
                    },
                }
            },
            "pricingDetails.data.evses[0].connectors[0].__typename is not a string",
        ),
        (
            {
                "enrollChargePlan": {
                    "__typename": "EmpEnrollChargePlanResponse",
                    "data": {
                        "__typename": "EmpEnrollChargePlanData",
                        "status": 1,
                    },
                }
            },
            "enrollChargePlan.data.status is not a string",
        ),
        ({"cancelChargePlan": []}, "cancelChargePlan is not an object"),
    ],
)
def test_charge_plan_parsers_reject_malformed_responses(
    payload: Mapping[str, object],
    message: str,
) -> None:
    root_field = next(iter(payload))
    parser_by_root: dict[str, Callable[[Mapping[str, object]], object | None]] = {
        "chargeProduct": parse_charge_product,
        "pricingDetails": parse_pricing_details,
        "enrollChargePlan": parse_enroll_charge_plan,
        "cancelChargePlan": parse_cancel_charge_plan,
    }
    with pytest.raises(ResponseError, match=re.escape(message)):
        parser_by_root[root_field](payload)


def test_charge_plan_models_are_frozen() -> None:
    result = ChargePlanCancellationResult("1000", None, None)

    with pytest.raises(FrozenInstanceError):
        result.status_code = "5000"  # type: ignore[misc]
