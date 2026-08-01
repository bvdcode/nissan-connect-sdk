from __future__ import annotations

import pytest
from test_pnc import (
    FakeResponse,
    FakeSession,
    graphql_response,
    make_client,
)

from pynissan import (
    PlugAndChargeCertificateRetryOutcome,
    PlugAndChargeCertificateRetryResult,
    PlugAndChargeServiceData,
    PlugAndChargeServiceState,
    PlugAndChargeServiceStatus,
    PlugAndChargeStatusInput,
    PlugAndChargeUpdateOutcome,
    PublicChargeSessionState,
    PublicChargeSessionStopOutcome,
    PublicChargeSessionStopResult,
    ReadOnlyError,
    ResponseError,
)


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
