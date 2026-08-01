from __future__ import annotations

from test_pnc import (
    FakeSession,
    assert_graphql_call,
    graphql_response,
    make_client,
)

from pynissan import (
    PlugAndChargeCertificateRetryResult,
    PlugAndChargeServiceData,
    PlugAndChargeServiceState,
    PlugAndChargeServiceStatus,
    PlugAndChargeStatusInput,
    PublicChargeLocationCoordinates,
    PublicChargeSessionData,
    PublicChargeSessionStartData,
    PublicChargeSessionStartResult,
    PublicChargeSessionState,
    PublicChargeSessionStatus,
    PublicChargeSessionStopResult,
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
