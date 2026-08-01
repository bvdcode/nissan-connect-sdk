from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from dataclasses import FrozenInstanceError
from enum import StrEnum

import pytest

from pynissan import operations
from pynissan.energy_account_models import (
    ACCOUNT_STATUS_POLL_INTERVAL_SECONDS,
    ACCOUNT_STATUS_POLL_TIMEOUT_SECONDS,
    EnergyAccountConnector,
    EnergyAccountData,
    EnergyAccountPollingOutcome,
    EnergyAccountStatus,
    EnergyAccountStatusReason,
    EnergyAccountStatusResult,
    EnergyNacsStatus,
    EnergyPncStatus,
    EnergyToggleStatus,
    account_status_polling_outcome,
)
from pynissan.energy_account_parsing import parse_account_status
from pynissan.exceptions import ResponseError


def account_status_payload(**fields: object) -> dict[str, object]:
    data: dict[str, object] = {"__typename": "EmpAccountStatusData", **fields}
    return {
        "accountStatus": {
            "__typename": "EmpAccountStatusResponse",
            "data": data,
        }
    }


def test_account_status_operation_matches_service_document_id_and_tokens() -> None:
    document = operations.ACCOUNT_STATUS

    assert document == (
        "query AccountStatus($vin: String!) { accountStatus(vin: $vin) { "
        "__typename statusCode statusMessage timestamp data { __typename status "
        "statusReason pncStatus pncStatusReason toggleStatus nacsStatus connectors { "
        "__typename id connectorName } } } }"
    )
    assert operations.ACCOUNT_STATUS_OPERATION_ID == (
        "fa9270fd8f34b96477a72ee8b6f0207707e2173d34cc45b25fe5049db85a6def"
    )
    assert hashlib.sha256(document.encode()).hexdigest() == operations.ACCOUNT_STATUS_OPERATION_ID
    tokens = " ".join(re.findall(r"\.\.\.|[_A-Za-z][_0-9A-Za-z]*|[$!():{}\[\]]", document))
    assert hashlib.sha256(tokens.encode()).hexdigest() == (
        "8c8d9019a1fd539d4d5de07033c48f0ed2ee12d22f9a35e8adb59448262b1756"
    )


def test_parse_account_status_preserves_exact_nullable_response_shape() -> None:
    result = parse_account_status(
        {
            "accountStatus": {
                "__typename": "EmpAccountStatusResponse",
                "statusCode": "1000",
                "statusMessage": None,
                "timestamp": "2026-07-31T12:00:00Z",
                "data": {
                    "__typename": "EmpAccountStatusData",
                    "status": "ACTIVE",
                    "statusReason": "NA",
                    "pncStatus": "READY",
                    "pncStatusReason": None,
                    "toggleStatus": "ENABLED",
                    "nacsStatus": "IN_ACTIVE",
                    "connectors": [
                        None,
                        {
                            "__typename": "EmpConnector",
                            "id": "CONNECTOR-1",
                            "connectorName": None,
                        },
                    ],
                },
            }
        }
    )

    assert result == EnergyAccountStatusResult(
        status_code="1000",
        status_message=None,
        timestamp="2026-07-31T12:00:00Z",
        data=EnergyAccountData(
            status=EnergyAccountStatus.ACTIVE,
            status_reason=EnergyAccountStatusReason.NA,
            pnc_status=EnergyPncStatus.READY,
            pnc_status_reason=None,
            toggle_status=EnergyToggleStatus.ENABLED,
            nacs_status=EnergyNacsStatus.IN_ACTIVE,
            connectors=(None, EnergyAccountConnector("CONNECTOR-1", None)),
        ),
    )


def test_parse_account_status_preserves_nullable_root_envelope_and_data() -> None:
    assert parse_account_status({"accountStatus": None}) is None
    assert parse_account_status(
        {
            "accountStatus": {
                "__typename": "EmpAccountStatusResponse",
                "statusCode": None,
                "statusMessage": None,
                "timestamp": None,
                "data": None,
            }
        }
    ) == EnergyAccountStatusResult(None, None, None, None)

    with pytest.raises(ResponseError, match=r"^accountStatus is missing$"):
        parse_account_status({})


def test_parse_account_status_distinguishes_nullable_and_empty_connectors() -> None:
    nullable = parse_account_status(
        account_status_payload(
            status=None,
            statusReason=None,
            pncStatus=None,
            pncStatusReason=None,
            toggleStatus=None,
            nacsStatus=None,
            connectors=None,
        )
    )
    empty = parse_account_status(account_status_payload(connectors=[]))

    assert nullable == EnergyAccountStatusResult(
        None,
        None,
        None,
        EnergyAccountData(None, None, None, None, None, None, None),
    )
    assert empty == EnergyAccountStatusResult(
        None,
        None,
        None,
        EnergyAccountData(None, None, None, None, None, None, ()),
    )


ENUM_FIELDS: tuple[tuple[type[StrEnum], str, tuple[str, ...]], ...] = (
    (
        EnergyAccountStatus,
        "status",
        (
            "PENDING",
            "FAILED",
            "ACTIVE",
            "INACTIVE",
            "CANCELLED",
            "CLOSED",
            "ENROLLING",
            "NOT_ENROLLED",
            "UNKNOWN__",
        ),
    ),
    (
        EnergyAccountStatusReason,
        "statusReason",
        ("DECLINED_PAYMENT", "SVT", "INVALID_PAYMENT", "NA", "UNKNOWN__"),
    ),
    (
        EnergyPncStatus,
        "pncStatus",
        ("PENDING", "INSTALLING", "READY", "FAILED", "NA", "RENEWING", "UNKNOWN__"),
    ),
    (
        EnergyToggleStatus,
        "toggleStatus",
        ("ENABLING", "ENABLED", "DISABLING", "DISABLED", "PENDING", "NA", "UNKNOWN__"),
    ),
    (
        EnergyNacsStatus,
        "nacsStatus",
        ("ACTIVE", "IN_ACTIVE", "NOT_APPLICABLE", "UNKNOWN__"),
    ),
)


@pytest.mark.parametrize(
    ("enum_type", "field", "raw_value"),
    [
        (enum_type, field, raw_value)
        for enum_type, field, raw_values in ENUM_FIELDS
        for raw_value in raw_values
    ],
)
def test_parse_account_status_maps_every_service_enum_value(
    enum_type: type[StrEnum],
    field: str,
    raw_value: str,
) -> None:
    result = parse_account_status(account_status_payload(**{field: raw_value}))

    assert result is not None
    assert result.data is not None
    parsed_by_field: dict[str, StrEnum | None] = {
        "status": result.data.status,
        "statusReason": result.data.status_reason,
        "pncStatus": result.data.pnc_status,
        "toggleStatus": result.data.toggle_status,
        "nacsStatus": result.data.nacs_status,
    }
    assert parsed_by_field[field] is enum_type(raw_value)


@pytest.mark.parametrize(
    ("enum_type", "field"),
    [(enum_type, field) for enum_type, field, _ in ENUM_FIELDS],
)
def test_parse_account_status_maps_future_enums_to_unknown_value(
    enum_type: type[StrEnum],
    field: str,
) -> None:
    result = parse_account_status(account_status_payload(**{field: "FUTURE_VALUE"}))

    assert result is not None
    assert result.data is not None
    parsed_by_field: dict[str, StrEnum | None] = {
        "status": result.data.status,
        "statusReason": result.data.status_reason,
        "pncStatus": result.data.pnc_status,
        "toggleStatus": result.data.toggle_status,
        "nacsStatus": result.data.nacs_status,
    }
    assert parsed_by_field[field] is enum_type("UNKNOWN__")


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"accountStatus": []}, "accountStatus is not an object"),
        ({"accountStatus": {}}, "accountStatus.__typename is not a string"),
        (
            {
                "accountStatus": {
                    "__typename": "EmpAccountStatusResponse",
                    "statusCode": 1000,
                }
            },
            "accountStatus.statusCode is not a string",
        ),
        (
            {
                "accountStatus": {
                    "__typename": "EmpAccountStatusResponse",
                    "data": [],
                }
            },
            "accountStatus.data is not an object",
        ),
        (
            account_status_payload(status=1),
            "accountStatus.data.status is not a string",
        ),
        (
            account_status_payload(connectors="not-a-list"),
            "accountStatus.data.connectors is not a list",
        ),
        (
            account_status_payload(connectors=[1]),
            "accountStatus.data.connectors[0] is not an object",
        ),
        (
            account_status_payload(connectors=[{}]),
            "accountStatus.data.connectors[0].__typename is not a string",
        ),
        (
            account_status_payload(connectors=[{"__typename": "EmpConnector", "id": 1}]),
            "accountStatus.data.connectors[0].id is not a string",
        ),
        (
            account_status_payload(pncStatusReason=False),
            "accountStatus.data.pncStatusReason is not a string",
        ),
    ],
)
def test_parse_account_status_rejects_malformed_responses(
    payload: Mapping[str, object],
    message: str,
) -> None:
    with pytest.raises(ResponseError, match=re.escape(message)):
        parse_account_status(payload)


@pytest.mark.parametrize(
    ("result", "outcome"),
    [
        (None, EnergyAccountPollingOutcome.RETRY),
        (EnergyAccountStatusResult(None, None, None, None), EnergyAccountPollingOutcome.RETRY),
        (
            EnergyAccountStatusResult(
                None,
                None,
                None,
                EnergyAccountData(None, None, None, None, None, None, None),
            ),
            EnergyAccountPollingOutcome.RETRY,
        ),
        (
            EnergyAccountStatusResult(
                None,
                None,
                None,
                EnergyAccountData(
                    EnergyAccountStatus.ENROLLING,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ),
            ),
            EnergyAccountPollingOutcome.RETRY,
        ),
        (
            EnergyAccountStatusResult(
                None,
                None,
                None,
                EnergyAccountData(
                    EnergyAccountStatus.ACTIVE,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ),
            ),
            EnergyAccountPollingOutcome.COMPLETE,
        ),
        (
            EnergyAccountStatusResult(
                None,
                None,
                None,
                EnergyAccountData(
                    EnergyAccountStatus.UNKNOWN_VALUE,
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                ),
            ),
            EnergyAccountPollingOutcome.COMPLETE,
        ),
    ],
)
def test_account_status_polling_outcome_matches_service(
    result: EnergyAccountStatusResult | None,
    outcome: EnergyAccountPollingOutcome,
) -> None:
    assert account_status_polling_outcome(result) is outcome


def test_account_status_polling_constants_match_service() -> None:
    assert ACCOUNT_STATUS_POLL_INTERVAL_SECONDS == 2.0
    assert ACCOUNT_STATUS_POLL_TIMEOUT_SECONDS == 210.0


def test_energy_account_models_are_frozen() -> None:
    connector = EnergyAccountConnector("CONNECTOR-1", "NACS")

    with pytest.raises(FrozenInstanceError):
        connector.id = "CONNECTOR-2"  # type: ignore[misc]
