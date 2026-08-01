from __future__ import annotations

import hashlib
from collections.abc import Awaitable, Mapping
from datetime import UTC, datetime
from typing import cast

import pytest
from aiohttp import ClientSession

from pynissan import (
    AddressInput,
    InvalidSecondDeliveryAddress,
    NissanClient,
    ReadOnlyError,
    SecondDeliveryAddress,
    SecondDeliveryAppointmentInput,
    SecondDeliveryAppointmentMode,
    SecondDeliveryBookedAppointment,
    SecondDeliveryContactInput,
    SecondDeliveryEligibility,
    SecondDeliveryOperationError,
    SecondDeliveryOperationSuccess,
    SecondDeliveryTimeSlots,
    Tokens,
    UnselectedSecondDeliveryResult,
    operations,
)
from pynissan.second_delivery_inputs import (
    second_delivery_appointment_variables,
    second_delivery_home_slots_variables,
    second_delivery_location_slots_variables,
    second_delivery_send_auth_code_variables,
    second_delivery_verify_auth_code_variables,
    update_second_delivery_appointment_variables,
)
from pynissan.second_delivery_parsing import (
    parse_cancel_second_delivery_appointment,
    parse_create_second_delivery_appointment,
    parse_second_delivery_address_validation,
    parse_second_delivery_appointment,
    parse_second_delivery_eligibility,
    parse_second_delivery_home_time_slots,
)

EXPECTED_OPERATIONS = {
    "CANCEL_SECOND_DELIVERY_APPOINTMENT": (
        "8038b57ab8afc28fb2f5c2153bcc89dea2650492101ce5817d08e0b613114668"
    ),
    "CREATE_SECOND_DELIVERY_APPOINTMENT": (
        "b6698d3dc4e338707998f4c9d7b2afa600b7d4980d05be50cd91f72c2ea71ee6"
    ),
    "SECOND_DELIVERY_APPOINTMENT": (
        "ca4319223c37ad3874b942484c301bf4b3b93171ff58bd43da2ab242a23af8df"
    ),
    "SECOND_DELIVERY_APPOINTMENTS_AT_HOME": (
        "e2d81521613aa8074f420a5f861e0d99891d9499bf968b6115a85220a72f7a0c"
    ),
    "SECOND_DELIVERY_APPOINTMENTS_AT_HUB": (
        "285d5991246c2008726e4ed4e5a2b12003da5dd7fd09121379fb6cec4527ab40"
    ),
    "SECOND_DELIVERY_APPOINTMENTS_AT_VIRTUAL": (
        "5a24913a76195ffd03ee01cc8b41932f19f48610e3b114c27c0959f4541b3366"
    ),
    "SECOND_DELIVERY_ELIGIBILITY": (
        "a19cdb3243dd2c8ae4c78fef51a829517988ac12ba1f3e4dd295e782f1bfcfae"
    ),
    "SECOND_DELIVERY_SEND_AUTH_CODE": (
        "fcada57a54859a26e4e8dcad4ae4a3d6e4282a5d7a62e0c433a18dc205c86204"
    ),
    "SECOND_DELIVERY_VERIFY_AUTH_CODE": (
        "011c0bc00940b689bc42b3c30a96bc755632cd12cefc1bbbe62db9abee8baa9e"
    ),
    "UPDATE_SECOND_DELIVERY_APPOINTMENT": (
        "af55dd2d886a10cb014a2187786513b1c7398c72c8e0048c1cf2355b5b04529e"
    ),
    "VALIDATE_SECOND_DELIVERY_ADDRESS": (
        "dfe7c26961f631dd97c91be4b03d896db2691978b64f130d306ab5e0bb7fca12"
    ),
}


class FakeResponse:
    def __init__(self, data: Mapping[str, object]) -> None:
        self.status = 200
        self._payload = {"data": data}

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


def make_client(session: FakeSession, *, read_only: bool) -> NissanClient:
    return NissanClient(
        cast(ClientSession, session),
        tokens=Tokens("access-token", "refresh-token", "id-token"),
        read_only=read_only,
    )


def appointment() -> SecondDeliveryAppointmentInput:
    return SecondDeliveryAppointmentInput(
        vin="VIN",
        address=AddressInput(address1="1 Main St", city="Franklin"),
        contact=SecondDeliveryContactInput(
            "First",
            "Last",
            "+15555550100",
            "owner@example.test",
        ),
        time_slot_id=42,
        redelivery_notes=None,
        mode=SecondDeliveryAppointmentMode.AT_HOME,
    )


def test_second_delivery_operations_match_service_documents() -> None:
    for constant, expected_id in EXPECTED_OPERATIONS.items():
        document = getattr(operations, constant)
        operation_id = getattr(operations, f"{constant}_OPERATION_ID")
        assert operation_id == expected_id
        assert hashlib.sha256(document.encode()).hexdigest() == expected_id


def test_second_delivery_inputs_preserve_omitted_and_null_fields() -> None:
    config = appointment()
    assert second_delivery_appointment_variables(config) == {
        "vin": "VIN",
        "address": {"address1": "1 Main St", "city": "Franklin"},
        "contactInformation": {
            "firstName": "First",
            "lastName": "Last",
            "phoneNumber": "+15555550100",
            "email": "owner@example.test",
        },
        "timeSlotId": 42,
        "redeliveryNotes": None,
        "mode": "AT_HOME",
    }
    assert update_second_delivery_appointment_variables(7, config) == {
        "vin": "VIN",
        "activityId": 7,
        "address": {"address1": "1 Main St", "city": "Franklin"},
        "contactInformation": {
            "firstName": "First",
            "lastName": "Last",
            "phoneNumber": "+15555550100",
            "email": "owner@example.test",
        },
        "timeSlotId": 42,
        "redeliveryNotes": None,
    }
    with pytest.raises(ValueError, match="UNKNOWN_VALUE cannot be sent"):
        second_delivery_appointment_variables(
            SecondDeliveryAppointmentInput(
                "VIN",
                AddressInput(),
                config.contact,
                42,
                mode=SecondDeliveryAppointmentMode.UNKNOWN_VALUE,
            )
        )


def test_parse_second_delivery_appointment_and_time_slots() -> None:
    assert parse_second_delivery_appointment(
        {
            "vehicle": {
                "__typename": "Vehicle",
                "secondDelivery": {
                    "__typename": "SecondDelivery",
                    "appointment": {
                        "__typename": "SecondDeliveryExistingBookedAppointment",
                        "id": None,
                        "activityId": None,
                        "beginsAt": None,
                        "address": None,
                        "contact": None,
                        "redeliveryNotes": None,
                        "featureNotes": None,
                        "hub": None,
                        "mode": None,
                    },
                },
            }
        }
    ) == SecondDeliveryBookedAppointment(None, None, None, None, None, None, None, None, None)
    assert parse_second_delivery_home_time_slots(
        {
            "vehicle": {
                "__typename": "Vehicle",
                "secondDelivery": {
                    "__typename": "SecondDelivery",
                    "appointments": {
                        "__typename": "Appointments",
                        "atHome": {
                            "__typename": "SecondDeliveryAppointmentTimeSlotsSuccessResponse",
                            "hub": None,
                            "slotsByDate": [],
                        },
                    },
                },
            }
        }
    ) == SecondDeliveryTimeSlots(None, ())


def test_parse_eligibility_validation_and_mutation_unions() -> None:
    assert parse_second_delivery_eligibility(
        {
            "vehicle": {
                "__typename": "Vehicle",
                "secondDelivery": {
                    "__typename": "SecondDelivery",
                    "eligibility": {"__typename": "FutureEligibility"},
                    "cta": None,
                },
            }
        }
    ) == SecondDeliveryEligibility(UnselectedSecondDeliveryResult("FutureEligibility"), None)
    assert parse_second_delivery_address_validation(
        {
            "vehicle": {
                "__typename": "Vehicle",
                "secondDelivery": {
                    "__typename": "SecondDelivery",
                    "validateAddress": {
                        "__typename": "InvalidSecondDeliveryAddress",
                        "valid": False,
                        "dealerAddress": {
                            "__typename": "Address",
                            "address1": "1 Main St",
                            "address2": None,
                            "city": "Franklin",
                            "state": "TN",
                            "postalCode": "37064",
                            "country": "US",
                        },
                    },
                },
            }
        }
    ) == InvalidSecondDeliveryAddress(
        False,
        SecondDeliveryAddress("1 Main St", None, "Franklin", "TN", "37064", "US"),
    )
    assert parse_cancel_second_delivery_appointment(
        {
            "cancelSecondDeliveryAppointment": {
                "__typename": "CancelSecondDeliveryAppointmentSuccessResponse",
                "success": True,
            }
        }
    ) == SecondDeliveryOperationSuccess(True)
    assert parse_create_second_delivery_appointment(
        {
            "createSecondDeliveryAppointment": {
                "__typename": "CreateSecondDeliveryInvalidTimeSlotErrorResponse",
                "message": None,
            }
        }
    ) == SecondDeliveryOperationError(
        "CreateSecondDeliveryInvalidTimeSlotErrorResponse",
        None,
    )


async def test_client_wires_all_second_delivery_operations() -> None:
    session = FakeSession(
        FakeResponse({"vehicle": None}),
        FakeResponse({"vehicle": None}),
        FakeResponse({"vehicle": None}),
        FakeResponse({"vehicle": None}),
        FakeResponse({"vehicle": None}),
        FakeResponse({"vehicle": None}),
        FakeResponse({"cancelSecondDeliveryAppointment": None}),
        FakeResponse({"createSecondDeliveryAppointment": None}),
        FakeResponse({"secondDeliverySendAuthCode": None}),
        FakeResponse({"secondDeliveryVerifyAuthCode": None}),
        FakeResponse({"updateSecondDeliveryAppointment": None}),
    )
    sdk = make_client(session, read_only=False)
    config = appointment()
    address = AddressInput(postal_code="37064")
    start = datetime(2026, 8, 1, tzinfo=UTC)
    end = datetime(2026, 8, 31, tzinfo=UTC)

    assert await sdk.async_get_second_delivery_appointment("VIN") is None
    assert (
        await sdk.async_get_second_delivery_home_time_slots(
            "VIN",
            address,
            "HUB",
            start,
            end,
        )
        is None
    )
    assert (
        await sdk.async_get_second_delivery_hub_time_slots("HUB", "37064", start, end, "VIN")
        is None
    )
    assert (
        await sdk.async_get_second_delivery_virtual_time_slots(
            "HUB",
            "37064",
            start,
            end,
            "VIN",
        )
        is None
    )
    assert await sdk.async_get_second_delivery_eligibility("VIN") is None
    assert await sdk.async_validate_second_delivery_address("VIN", address) is None
    assert await sdk.async_cancel_second_delivery_appointment(7) is None
    assert await sdk.async_create_second_delivery_appointment(config) is None
    assert (
        await sdk.async_second_delivery_send_auth_code(
            42,
            "access-token",
            send_via_email=True,
            send_via_sms=False,
        )
        is None
    )
    assert await sdk.async_second_delivery_verify_auth_code(42, "access-token", "123456") is None
    assert await sdk.async_update_second_delivery_appointment(7, config) is None

    payloads: list[Mapping[str, object]] = []
    for call in session.calls:
        payload = call["json"]
        assert isinstance(payload, Mapping)
        payloads.append(payload)
    assert [payload["operationName"] for payload in payloads] == [
        "SecondDeliveryAppointment",
        "SecondDeliveryAppointmentsAtHome",
        "SecondDeliveryAppointmentsAtHub",
        "SecondDeliveryAppointmentsAtVirtual",
        "SecondDeliveryEligibility",
        "ValidateSecondDeliveryAddress",
        "CancelSecondDeliveryAppointment",
        "CreateSecondDeliveryAppointment",
        "SecondDeliverySendAuthCode",
        "SecondDeliveryVerifyAuthCode",
        "UpdateSecondDeliveryAppointment",
    ]
    assert payloads[1]["variables"] == second_delivery_home_slots_variables(
        "VIN",
        address,
        "HUB",
        start,
        end,
    )
    assert payloads[2]["variables"] == second_delivery_location_slots_variables(
        "HUB",
        "37064",
        start,
        end,
        "VIN",
    )
    assert payloads[8]["variables"] == second_delivery_send_auth_code_variables(
        42,
        "access-token",
        True,
        False,
    )
    assert payloads[9]["variables"] == second_delivery_verify_auth_code_variables(
        42,
        "access-token",
        "123456",
    )


async def test_read_only_mode_blocks_all_second_delivery_mutations_before_network() -> None:
    session = FakeSession()
    sdk = make_client(session, read_only=True)
    config = appointment()
    calls: tuple[Awaitable[object], ...] = (
        sdk.async_cancel_second_delivery_appointment(7),
        sdk.async_create_second_delivery_appointment(config),
        sdk.async_second_delivery_send_auth_code(
            42,
            "access-token",
            send_via_email=True,
            send_via_sms=False,
        ),
        sdk.async_second_delivery_verify_auth_code(42, "access-token", "123456"),
        sdk.async_update_second_delivery_appointment(7, config),
    )

    for call in calls:
        with pytest.raises(ReadOnlyError):
            await call

    assert session.calls == []
