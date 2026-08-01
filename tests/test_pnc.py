from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from typing import cast

import pytest
from aiohttp import ClientSession

from pynissan import (
    NissanClient,
    PlugAndChargeCertificateRetryOutcome,
    PlugAndChargeCertificateRetryResult,
    PlugAndChargeServiceData,
    PlugAndChargeServiceState,
    PlugAndChargeServiceStatus,
    PlugAndChargeStatusInput,
    PlugAndChargeUpdateOutcome,
    PublicChargeLocationCoordinates,
    PublicChargeSessionData,
    PublicChargeSessionStartData,
    PublicChargeSessionStartResult,
    PublicChargeSessionState,
    PublicChargeSessionStatus,
    PublicChargeSessionStopOutcome,
    PublicChargeSessionStopResult,
    ReadOnlyError,
    ResponseError,
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


async def test_get_pnc_service_status_parses_nullable_enrollment_data() -> None:
    session = FakeSession(
        graphql_response(
            {
                "pncServiceStatus": {
                    "__typename": "EmpPnCServiceStatusResponse",
                    "statusCode": "1000",
                    "statusMessage": None,
                    "timestamp": "2026-07-31T19:00:00Z",
                    "data": {
                        "__typename": "EmpPnCServiceStatusData",
                        "vin": "VIN",
                        "pncServiceStatus": "ENABLED",
                    },
                }
            }
        ),
        graphql_response(
            {
                "pncServiceStatus": {
                    "__typename": "EmpPnCServiceStatusResponse",
                    "data": {
                        "__typename": "EmpPnCServiceStatusData",
                        "pncServiceStatus": "FUTURE_STATE",
                    },
                }
            }
        ),
    )
    client = make_client(session)

    result = await client.async_get_pnc_service_status("VIN")
    unknown = await client.async_get_pnc_service_status("VIN")

    assert result == PlugAndChargeServiceStatus(
        status_code="1000",
        status_message=None,
        timestamp="2026-07-31T19:00:00Z",
        data=PlugAndChargeServiceData("VIN", PlugAndChargeServiceState.ENABLED),
    )
    assert unknown is not None
    assert unknown.data == PlugAndChargeServiceData(
        None,
        PlugAndChargeServiceState.UNKNOWN_VALUE,
    )
    assert_graphql_call(session, 0, "PNCServiceStatus", {"vin": "VIN"})


async def test_get_public_charge_session_status_parses_service_contract() -> None:
    session = FakeSession(
        graphql_response(
            {
                "sessionStatus": {
                    "__typename": "EmpSessionStatusResponse",
                    "statusCode": "1000",
                    "statusMessage": "active",
                    "timestamp": None,
                    "data": {
                        "__typename": "EmpChargeSessionData",
                        "sessionUid": "session-1",
                        "status": "ACTIVE",
                        "message": None,
                        "stopSessionAllowed": True,
                        "cpoName": "Operator",
                        "physicalReference": "A-12",
                        "locationAddress": "1 Main St",
                        "locationCity": "San Diego",
                        "locationState": "CA",
                        "locationCoordinates": {
                            "__typename": "EmpCoordinates",
                            "latitude": "32.1",
                            "longitude": "-117.2",
                        },
                    },
                }
            }
        )
    )

    result = await make_client(session).async_get_public_charge_session_status("VIN")

    assert result == PublicChargeSessionStatus(
        status_code="1000",
        status_message="active",
        timestamp=None,
        data=PublicChargeSessionData(
            session_uid="session-1",
            status=PublicChargeSessionState.ACTIVE,
            message=None,
            stop_session_allowed=True,
            cpo_name="Operator",
            physical_reference="A-12",
            location_address="1 Main St",
            location_city="San Diego",
            location_state="CA",
            location_coordinates=PublicChargeLocationCoordinates("32.1", "-117.2"),
        ),
    )
    assert_graphql_call(session, 0, "ChargeSessionStatus", {"vin": "VIN"})


async def test_start_public_charge_session_preserves_optional_location() -> None:
    result_data = {
        "__typename": "EmpStartChargeSessionData",
        "vin": "VIN",
        "evseId": "EVSE-1",
        "status": "PENDING",
        "message": None,
        "stopSessionAllowed": False,
    }
    session = FakeSession(
        graphql_response(
            {
                "startChargeSession": {
                    "__typename": "EmpStartChargeSessionResponse",
                    "statusCode": "1000",
                    "statusMessage": None,
                    "timestamp": "now",
                    "data": result_data,
                }
            }
        ),
        graphql_response({"startChargeSession": None}),
        graphql_response({"startChargeSession": None}),
    )
    client = make_client(session, read_only=False)

    result = await client.async_start_public_charge_session("VIN", "EVSE-1")
    explicit_null = await client.async_start_public_charge_session(
        "VIN",
        "EVSE-1",
        location_id=None,
    )
    explicit_value = await client.async_start_public_charge_session(
        "VIN",
        "EVSE-1",
        location_id="LOCATION-1",
    )

    assert result == PublicChargeSessionStartResult(
        status_code="1000",
        status_message=None,
        timestamp="now",
        data=PublicChargeSessionStartData(
            vin="VIN",
            evse_id="EVSE-1",
            status=PublicChargeSessionState.PENDING,
            message=None,
            stop_session_allowed=False,
        ),
    )
    assert explicit_null is None
    assert explicit_value is None
    base_config = {"vin": "VIN", "evseId": "EVSE-1"}
    assert_graphql_call(session, 0, "StartChargeSession", {"config": base_config})
    assert_graphql_call(
        session,
        1,
        "StartChargeSession",
        {"config": {**base_config, "locationId": None}},
    )
    assert_graphql_call(
        session,
        2,
        "StartChargeSession",
        {"config": {**base_config, "locationId": "LOCATION-1"}},
    )


async def test_stop_public_charge_session_sends_required_service_vin() -> None:
    response = {
        "stopChargeSession": {
            "__typename": "EmpStopChargeSessionResponse",
            "statusCode": "1000",
            "statusMessage": None,
            "timestamp": "now",
        }
    }
    session = FakeSession(
        graphql_response(response),
    )
    client = make_client(session, read_only=False)

    result = await client.async_stop_public_charge_session("VIN")

    expected = PublicChargeSessionStopResult("1000", None, "now")
    assert result == expected
    assert_graphql_call(session, 0, "StopChargeSession", {"config": {"vin": "VIN"}})


async def test_update_pnc_and_retry_certificate_parse_statuses() -> None:
    session = FakeSession(
        graphql_response(
            {
                "updatePnCServiceStatus": {
                    "__typename": "EmpPnCServiceStatusResponse",
                    "statusCode": "1000",
                    "statusMessage": "enabled",
                    "timestamp": "now",
                    "data": {
                        "__typename": "EmpPnCServiceStatusData",
                        "vin": "VIN",
                        "pncServiceStatus": "ENABLING",
                    },
                }
            }
        ),
        graphql_response(
            {
                "retryCertInstall": {
                    "__typename": "EmpRetryCertInstallResponse",
                    "statusCode": "1000",
                }
            }
        ),
    )
    client = make_client(session, read_only=False)

    update = await client.async_update_pnc_service_status(
        "VIN",
        PlugAndChargeStatusInput.ENABLE,
    )
    retry = await client.async_retry_pnc_certificate_install("VIN")

    assert update == PlugAndChargeServiceStatus(
        "1000",
        "enabled",
        "now",
        PlugAndChargeServiceData("VIN", PlugAndChargeServiceState.ENABLING),
    )
    assert retry == PlugAndChargeCertificateRetryResult("1000")
    assert_graphql_call(
        session,
        0,
        "UpdatePnCServiceStatus",
        {"config": {"vin": "VIN", "pncServiceStatus": "ENABLE"}},
    )
    assert_graphql_call(
        session,
        1,
        "RetryCertInstall",
        {"config": {"vin": "VIN"}},
    )


async def test_wait_for_pnc_service_status_matches_service_polling_semantics() -> None:
    session = FakeSession(
        graphql_response({"pncServiceStatus": None}),
        graphql_response(
            {
                "pncServiceStatus": {
                    "__typename": "EmpPnCServiceStatusResponse",
                    "data": {
                        "__typename": "EmpPnCServiceStatusData",
                        "pncServiceStatus": "ENABLING",
                    },
                }
            }
        ),
        graphql_response(
            {
                "pncServiceStatus": {
                    "__typename": "EmpPnCServiceStatusResponse",
                    "data": {
                        "__typename": "EmpPnCServiceStatusData",
                        "pncServiceStatus": "ENABLED",
                    },
                }
            }
        ),
    )

    result = await make_client(session).async_wait_for_pnc_service_status(
        "VIN",
        PlugAndChargeServiceState.ENABLED,
        poll_interval_seconds=0.001,
        timeout_seconds=1,
    )

    assert result is not None
    assert result.data == PlugAndChargeServiceData(
        None,
        PlugAndChargeServiceState.ENABLED,
    )
    assert len(session.calls) == 3


async def test_wait_for_public_charge_session_matches_service_terminal_states() -> None:
    def status_response(state: str) -> FakeResponse:
        return graphql_response(
            {
                "sessionStatus": {
                    "__typename": "EmpSessionStatusResponse",
                    "data": {
                        "__typename": "EmpChargeSessionData",
                        "status": state,
                        "locationCoordinates": None,
                    },
                }
            }
        )

    session = FakeSession(
        status_response("PENDING"),
        status_response("RESERVATION"),
        status_response("FUTURE_STATE"),
        status_response("ACTIVE"),
    )

    result = await make_client(session).async_wait_for_public_charge_session_status(
        "VIN",
        poll_interval_seconds=0.001,
        timeout_seconds=1,
    )

    assert result is not None
    assert result.data is not None
    assert result.data.status is PublicChargeSessionState.ACTIVE
    assert len(session.calls) == 4


async def test_public_charge_waiter_preserves_service_null_boundaries() -> None:
    missing_data_session = FakeSession(
        graphql_response(
            {
                "sessionStatus": {
                    "__typename": "EmpSessionStatusResponse",
                    "data": None,
                }
            }
        )
    )
    status_null_session = FakeSession(
        graphql_response(
            {
                "sessionStatus": {
                    "__typename": "EmpSessionStatusResponse",
                    "data": {
                        "__typename": "EmpChargeSessionData",
                        "status": None,
                        "locationCoordinates": None,
                    },
                }
            }
        )
    )

    missing_data = await make_client(
        missing_data_session
    ).async_wait_for_public_charge_session_status(
        "VIN",
        poll_interval_seconds=0.001,
        timeout_seconds=1,
    )
    status_null = await make_client(
        status_null_session
    ).async_wait_for_public_charge_session_status(
        "VIN",
        poll_interval_seconds=0.001,
        timeout_seconds=1,
    )

    assert missing_data is None
    assert status_null is not None
    assert status_null.data is not None
    assert status_null.data.status is None


async def test_pnc_waiters_raise_on_service_timeout() -> None:
    pnc_session = FakeSession(
        graphql_response(
            {
                "pncServiceStatus": {
                    "__typename": "EmpPnCServiceStatusResponse",
                    "data": {
                        "__typename": "EmpPnCServiceStatusData",
                        "pncServiceStatus": "ENABLING",
                    },
                }
            }
        )
    )
    charge_session = FakeSession(
        graphql_response(
            {
                "sessionStatus": {
                    "__typename": "EmpSessionStatusResponse",
                    "data": {
                        "__typename": "EmpChargeSessionData",
                        "status": "PENDING",
                        "locationCoordinates": None,
                    },
                }
            }
        )
    )

    with pytest.raises(TimeoutError):
        await make_client(pnc_session).async_wait_for_pnc_service_status(
            "VIN",
            PlugAndChargeServiceState.ENABLED,
            poll_interval_seconds=1,
            timeout_seconds=0.001,
        )
    with pytest.raises(TimeoutError):
        await make_client(charge_session).async_wait_for_public_charge_session_status(
            "VIN",
            poll_interval_seconds=1,
            timeout_seconds=0.001,
        )


def test_pnc_command_outcomes_match_service_mappings() -> None:
    enabled = PlugAndChargeServiceStatus(
        "1000",
        None,
        None,
        PlugAndChargeServiceData("VIN", PlugAndChargeServiceState.ENABLED),
    )
    enabling = PlugAndChargeServiceStatus(
        "1000",
        None,
        None,
        PlugAndChargeServiceData("VIN", PlugAndChargeServiceState.ENABLING),
    )
    disabled = PlugAndChargeServiceStatus(
        "1000",
        None,
        None,
        PlugAndChargeServiceData("VIN", PlugAndChargeServiceState.DISABLED),
    )
    pending = PlugAndChargeServiceStatus(
        "1000",
        None,
        None,
        PlugAndChargeServiceData("VIN", PlugAndChargeServiceState.PENDING),
    )

    assert (
        enabled.update_outcome(PlugAndChargeStatusInput.ENABLE)
        is PlugAndChargeUpdateOutcome.SUCCESS
    )
    assert (
        enabling.update_outcome(PlugAndChargeStatusInput.ENABLE)
        is PlugAndChargeUpdateOutcome.PENDING
    )
    assert (
        disabled.update_outcome(PlugAndChargeStatusInput.ENABLE)
        is PlugAndChargeUpdateOutcome.FAILED
    )
    assert (
        pending.update_outcome(PlugAndChargeStatusInput.DISABLE)
        is PlugAndChargeUpdateOutcome.FAILED
    )
    assert (
        PlugAndChargeServiceStatus("2004", None, None, None).update_outcome(
            PlugAndChargeStatusInput.DISABLE
        )
        is PlugAndChargeUpdateOutcome.DISABLE_ERROR
    )
    assert (
        PlugAndChargeServiceStatus(None, None, None, None).update_outcome(
            PlugAndChargeStatusInput.ENABLE
        )
        is PlugAndChargeUpdateOutcome.UNKNOWN
    )
    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        enabled.update_outcome(PlugAndChargeStatusInput.UNKNOWN_VALUE)

    assert (
        PublicChargeSessionStopResult("1000", None, None).outcome
        is PublicChargeSessionStopOutcome.SUCCESS
    )
    assert (
        PublicChargeSessionStopResult("3026", None, None).outcome
        is PublicChargeSessionStopOutcome.FAILED
    )
    assert (
        PublicChargeSessionStopResult("4014", None, None).outcome
        is PublicChargeSessionStopOutcome.UNEXPECTED_ERROR
    )
    assert (
        PublicChargeSessionStopResult("future", None, None).outcome
        is PublicChargeSessionStopOutcome.UNKNOWN
    )
    assert (
        PlugAndChargeCertificateRetryResult("1000").outcome
        is PlugAndChargeCertificateRetryOutcome.SUCCESS
    )
    assert (
        PlugAndChargeCertificateRetryResult("2028").outcome
        is PlugAndChargeCertificateRetryOutcome.FAILED
    )
    assert (
        PlugAndChargeCertificateRetryResult("future").outcome
        is PlugAndChargeCertificateRetryOutcome.UNKNOWN
    )


async def test_pnc_waiters_reject_invalid_polling_inputs_before_io() -> None:
    session = FakeSession()
    client = make_client(session)

    with pytest.raises(ValueError, match="ENABLED or DISABLED"):
        await client.async_wait_for_pnc_service_status(
            "VIN",
            PlugAndChargeServiceState.ENABLING,
        )
    with pytest.raises(ValueError, match="poll_interval_seconds"):
        await client.async_wait_for_public_charge_session_status(
            "VIN",
            poll_interval_seconds=0,
        )
    with pytest.raises(ValueError, match="timeout_seconds"):
        await client.async_wait_for_public_charge_session_status(
            "VIN",
            timeout_seconds=float("nan"),
        )

    assert session.calls == []


async def test_pnc_mutations_respect_read_only_mode_before_io() -> None:
    session = FakeSession()
    client = make_client(session)

    with pytest.raises(ReadOnlyError):
        await client.async_start_public_charge_session("VIN", "EVSE-1")
    with pytest.raises(ReadOnlyError):
        await client.async_stop_public_charge_session("VIN")
    with pytest.raises(ReadOnlyError):
        await client.async_update_pnc_service_status(
            "VIN",
            PlugAndChargeStatusInput.ENABLE,
        )
    with pytest.raises(ReadOnlyError):
        await client.async_retry_pnc_certificate_install("VIN")

    assert session.calls == []


async def test_pnc_unknown_input_is_rejected_and_malformed_responses_fail() -> None:
    session = FakeSession(
        graphql_response({}),
        graphql_response(
            {
                "sessionStatus": {
                    "__typename": "EmpSessionStatusResponse",
                    "data": {
                        "__typename": "EmpChargeSessionData",
                        "stopSessionAllowed": "yes",
                        "locationCoordinates": None,
                    },
                }
            }
        ),
    )
    client = make_client(session, read_only=False)

    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        await client.async_update_pnc_service_status(
            "VIN",
            PlugAndChargeStatusInput.UNKNOWN_VALUE,
        )
    assert session.calls == []

    with pytest.raises(ResponseError, match="pncServiceStatus is missing"):
        await client.async_get_pnc_service_status("VIN")
    with pytest.raises(ResponseError, match="stopSessionAllowed is not a boolean"):
        await client.async_get_public_charge_session_status("VIN")
