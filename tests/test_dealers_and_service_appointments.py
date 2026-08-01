from __future__ import annotations

import hashlib
from collections.abc import Awaitable, Mapping
from datetime import UTC, datetime
from typing import cast

import pytest
from aiohttp import ClientSession

from pynissan import (
    CreatedServiceAppointment,
    Dealer,
    DistanceUnit,
    MaintenanceInterval,
    MaintenanceMileageInput,
    MaintenanceVisit,
    MaintenanceVisitAlignment,
    MaintenanceVisits,
    NissanClient,
    ReadOnlyError,
    ServiceAppointmentInput,
    ServiceAppointmentTimeSlot,
    ServiceCode,
    ServiceCustomerInput,
    ServiceLocationType,
    ServiceOdometerInput,
    Tokens,
    UnselectedDealerResult,
    operations,
)
from pynissan.dealer_inputs import (
    all_dealers_variables,
    dealers_by_search_variables,
    maintenance_visits_variables,
    service_appointment_variables,
    service_time_slots_variables,
    update_service_appointment_variables,
)
from pynissan.dealer_parsing import (
    parse_create_service_appointment,
    parse_dealers,
    parse_maintenance_visits,
    parse_service_appointment_time_slots,
    parse_update_service_appointment,
    parse_update_vehicle_preferred_dealer,
)

EXPECTED_OPERATIONS = {
    "ALL_DEALERS": "581b6c84a95b602859bc103577eb32e43e0a4cbbef84bb3c09940dd5d0b1dd2b",
    "CANCEL_SERVICE_APPOINTMENT": (
        "02cf1da9ff930c6352ef4e30309db2a8c4f1e84ab3f265952d85eec590b4bd39"
    ),
    "CREATE_SERVICE_APPOINTMENT": (
        "980f2a99cdde6b924e005c338dcc6185f873242f457a0b2fe42fd8d3b00f173d"
    ),
    "DEALERS": "99bcf20cccacbd902e4f112827461c5f7dcca0c3b011f3260dcc95c531f4238f",
    "DEALERS_BY_SEARCH": "c4bd356f59315ac2ef1d68fedfe7d578dfd1945386f0aa7ed4bb8f3ca0561e5d",
    "DEALS_AND_IMAGES_BY_DEALER_ID": (
        "52f73c33747c221c3a5de53bf8f19152e9827cc029a837f2de747e05fc4e26e5"
    ),
    "GENERATE_ALL_VISITS": "6a4012bcf0ec70ac7d3a36b5b178600b4c5651a2c8105cb019921db11c36b9cb",
    "GENERATE_NEXT_VISIT": "dcef3f6fdab4037776eb0887d24210c2e55113dd5b078578293c0f727b1424e8",
    "GENERATE_NEXT_VISIT_NO_SEVERITY": (
        "c53205b1dd6493a9c7813171c72985d5cb080f12bc2c598a48efb00f95f6fb92"
    ),
    "GET_DEALER_BY_ID": "eb2c4869c9e7332631a50a1720e871dc20c66f1f28cd7bdf48c36f4005b003ff",
    "SERVICE_ADVISORS": "dc0c2a11cf2f930d82387960dbbd9ca2de0cb71e72874f35a78de66e5ea44d9d",
    "SERVICE_APPOINTMENT_TIME_SLOTS": (
        "f480da9f36ebfcf7303cf64a43fa317019f79316589173f889adddd25563e644"
    ),
    "SERVICE_APPOINTMENTS": "e096a72fdf7c1e4751265df4abc9715e97cd0efa0ce990288f26b26fb70fa77b",
    "SERVICE_CATEGORIES": "7e1c8de493a29b1adeedba76185abd9fc6a75e33be48526d5c764e0780248e36",
    "SERVICE_OPERATIONS": "0b070e2e51e0fb5143aec45d1b128c7fe4dc85a633a7e92ebaac758ed4e4a2e1",
    "SERVICE_OPERATIONS_BY_MILEAGE": (
        "35d58f1328e5fa4e15722fbe3131841850530d23c1a2cad34447ae5819b502f7"
    ),
    "TRANSPORTATION_OPTIONS": ("dfb82c466e1a2597905a7e83ad944b8d7b7aba30774ec2ee6cbe941ac822e101"),
    "UPDATE_SERVICE_APPOINTMENT": (
        "10ea93855682f0dc2d4ea2a50799e6e3086bc24a61ee60c915f1c443f2d1e356"
    ),
    "UPDATE_VEHICLE_PREFERRED_DEALER": (
        "ee96579c755162d75f970f3e33d67e58bf8b2e79a36c37c653d24731653cc33d"
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


def appointment() -> ServiceAppointmentInput:
    return ServiceAppointmentInput(
        vin="VIN",
        dealer_id="DEALER",
        appointment_date=datetime(2026, 8, 5, 10, tzinfo=UTC),
        contact_methods=ServiceCustomerInput("+15555550100", "owner@example.test"),
        service_operations=(),
        odometer=ServiceOdometerInput(DistanceUnit.MILE, 12000),
    )


def test_dealer_and_service_operations_match_service_documents() -> None:
    for constant, expected_id in EXPECTED_OPERATIONS.items():
        document = getattr(operations, constant)
        operation_id = getattr(operations, f"{constant}_OPERATION_ID")
        assert operation_id == expected_id
        assert hashlib.sha256(document.encode()).hexdigest() == expected_id


def test_dealer_and_service_inputs_preserve_generated_shapes() -> None:
    assert all_dealers_variables(vin=None) == {"vin": None}
    assert dealers_by_search_variables(
        service_code=ServiceCode.SERVICE,
        radius=50,
        latitude=35.9,
        longitude=-86.8,
    ) == {
        "serviceCode": "SERVICE",
        "radius": 50,
        "latitude": 35.9,
        "longitude": -86.8,
    }
    mileage = MaintenanceMileageInput(total_mile=12000)
    assert maintenance_visits_variables("VIN", mileage, "SEVERITY", 1, 2) == {
        "vin": "VIN",
        "mileage": {"totalMile": 12000},
        "severityId": "SEVERITY",
        "pastVisits": 1,
        "futureVisits": 2,
    }
    assert service_appointment_variables(appointment()) == {
        "appointment": {
            "vin": "VIN",
            "dealerId": "DEALER",
            "appointmentDate": "2026-08-05T10:00:00+00:00",
            "contactMethods": {
                "phone": "+15555550100",
                "email": "owner@example.test",
            },
            "serviceOperations": [],
            "odometer": {"unit": "MILE", "value": 12000},
        }
    }
    with pytest.raises(ValueError, match="UNKNOWN_VALUE cannot be sent"):
        dealers_by_search_variables(service_code=ServiceCode.UNKNOWN_VALUE)


def test_parse_dealer_search_and_time_slots() -> None:
    assert parse_dealers(
        {
            "dealers": [
                {
                    "__typename": "Dealer",
                    "dealerId": "DEALER",
                    "dealerName": "Nissan Dealer",
                    "dealerAddressLine1": "1 Main St",
                    "dealerAddressLine2": None,
                    "dealerCityName": "Franklin",
                    "dealerStateCode": "TN",
                    "dealerCountry": "US",
                    "dealerZip": "37064",
                    "dealerLatitude": 35.9,
                    "dealerLongitude": -86.8,
                    "dealerPhoneNumber": None,
                    "dealerServicePhone": None,
                    "dealerServiceHours": None,
                    "dealerOnlineSchedulingMobileUrl": None,
                    "nativeServiceBooking": True,
                    "languagesSpoken": ["English"],
                }
            ]
        }
    ) == (
        Dealer(
            "DEALER",
            "Nissan Dealer",
            None,
            "1 Main St",
            None,
            35.9,
            -86.8,
            "37064",
            "US",
            "TN",
            True,
            None,
            "Franklin",
            None,
            None,
            None,
            ("English",),
            None,
            None,
            None,
        ),
    )
    assert parse_service_appointment_time_slots(
        {
            "serviceAppointmentTimeSlots": [
                {
                    "__typename": "ServiceAppointmentTimeSlot",
                    "isOpen": True,
                    "date": "2026-08-05T00:00:00Z",
                    "timeslots": [
                        {
                            "__typename": "Timeslot",
                            "time": "2026-08-05T10:00:00Z",
                        }
                    ],
                }
            ]
        }
    ) == (
        ServiceAppointmentTimeSlot(
            True,
            datetime(2026, 8, 5, tzinfo=UTC),
            (datetime(2026, 8, 5, 10, tzinfo=UTC),),
        ),
    )


def test_parse_maintenance_visits_and_union_results() -> None:
    assert parse_maintenance_visits(
        {
            "viewer": {
                "__typename": "MS_Viewer",
                "Schedule": {
                    "__typename": "MS_Schedule",
                    "Visits": [
                        {
                            "__typename": "MS_Visit",
                            "Alignment": "DistanceBased",
                            "Interval": {
                                "__typename": "MS_Interval",
                                "Month": 12,
                                "Year": 1,
                                "Next": True,
                                "DistanceMiles": 15000,
                                "DistanceKMs": None,
                            },
                            "ServiceOccurrences": None,
                        }
                    ],
                },
            }
        }
    ) == MaintenanceVisits(
        (
            MaintenanceVisit(
                MaintenanceVisitAlignment.DISTANCE_BASED,
                MaintenanceInterval(12, 1, True, 15000, None),
                None,
            ),
        )
    )
    assert parse_create_service_appointment(
        {
            "createServiceAppointment": {
                "__typename": "ServiceAppointment",
                "appointmentId": None,
            }
        }
    ) == CreatedServiceAppointment(None)
    assert parse_update_service_appointment(
        {"updateServiceAppointment": {"__typename": "FutureAppointment"}}
    ) == UnselectedDealerResult("FutureAppointment")
    assert parse_update_vehicle_preferred_dealer(
        {"updateVehicle": {"__typename": "FutureVehicleUpdate"}}
    ) == UnselectedDealerResult("FutureVehicleUpdate")


async def test_client_wires_all_dealer_and_service_operations() -> None:
    session = FakeSession(
        FakeResponse({"dealers": None}),
        FakeResponse({"dealers": None}),
        FakeResponse({"dealers": None}),
        FakeResponse({"dealsByDealerId": None, "dealsImagesByDealerId": None}),
        FakeResponse({"dealer": None}),
        FakeResponse({"viewer": None}),
        FakeResponse({"viewer": None}),
        FakeResponse({"viewer": None}),
        FakeResponse({"serviceAdvisors": None}),
        FakeResponse({"serviceAppointmentTimeSlots": []}),
        FakeResponse({"serviceAppointments": None}),
        FakeResponse({"serviceCategories": None}),
        FakeResponse({"serviceOperations": None}),
        FakeResponse({"serviceOperationsByMileage": None}),
        FakeResponse({"transportationOptions": None}),
        FakeResponse({"cancelServiceAppointment": None}),
        FakeResponse({"createServiceAppointment": None}),
        FakeResponse({"updateServiceAppointment": None}),
        FakeResponse({"updateVehicle": None}),
    )
    sdk = make_client(session, read_only=False)
    mileage = MaintenanceMileageInput(total_mile=12000)
    start = datetime(2026, 8, 5, tzinfo=UTC)
    config = appointment()

    assert await sdk.async_get_all_dealers() is None
    assert await sdk.async_get_dealers("37064") is None
    assert await sdk.async_search_dealers() is None
    await sdk.async_get_dealer_deals_and_images("DEALER")
    assert await sdk.async_get_dealer("DEALER") is None
    assert await sdk.async_generate_all_maintenance_visits("VIN", mileage, "S", 1, 2) is None
    assert await sdk.async_generate_next_maintenance_visit("VIN", mileage, "S", 1, 2) is None
    assert (
        await sdk.async_generate_next_maintenance_visit_no_severity("VIN", mileage, "S", 1, 2)
        is None
    )
    assert await sdk.async_get_service_advisors("DEALER", ("OP",)) is None
    assert (
        await sdk.async_get_service_appointment_time_slots(
            "DEALER",
            ("OP",),
            start,
            location_type=ServiceLocationType.PICK_UP,
        )
        == ()
    )
    assert await sdk.async_get_service_appointments("VIN") is None
    assert await sdk.async_get_service_categories() is None
    assert await sdk.async_get_service_operations("VIN", "DEALER") is None
    assert await sdk.async_get_service_operations_by_mileage("VIN", "DEALER", 12000) is None
    assert await sdk.async_get_transportation_options("DEALER", ("OP",)) is None
    assert await sdk.async_cancel_service_appointment("APPOINTMENT", "DEALER") is None
    assert await sdk.async_create_service_appointment(config) is None
    assert await sdk.async_update_service_appointment("APPOINTMENT", config) is None
    assert await sdk.async_update_vehicle_preferred_dealer("VIN", "DEALER") is None

    payloads: list[Mapping[str, object]] = []
    for call in session.calls:
        payload = call["json"]
        assert isinstance(payload, Mapping)
        payloads.append(payload)
    assert [payload["operationName"] for payload in payloads] == [
        "AllDealers",
        "Dealers",
        "DealersBySearch",
        "DealsAndImagesByDealerId",
        "GetDealerById",
        "GenerateAllVisits",
        "GenerateNextVisit",
        "GenerateNextVisitNoSeverity",
        "ServiceAdvisors",
        "ServiceAppointmentTimeSlots",
        "ServiceAppointments",
        "ServiceCategories",
        "ServiceOperations",
        "ServiceOperationsByMileage",
        "TransportationOptions",
        "CancelServiceAppointment",
        "CreateServiceAppointment",
        "UpdateServiceAppointment",
        "UpdateVehiclePreferredDealer",
    ]
    assert payloads[9]["variables"] == service_time_slots_variables(
        "DEALER",
        ("OP",),
        start,
        location_type=ServiceLocationType.PICK_UP,
    )
    assert payloads[16]["variables"] == service_appointment_variables(config)
    assert payloads[17]["variables"] == update_service_appointment_variables(
        "APPOINTMENT",
        config,
    )


async def test_read_only_mode_blocks_all_service_mutations_before_network() -> None:
    session = FakeSession()
    sdk = make_client(session, read_only=True)
    config = appointment()
    calls: tuple[Awaitable[object], ...] = (
        sdk.async_cancel_service_appointment("APPOINTMENT", "DEALER"),
        sdk.async_create_service_appointment(config),
        sdk.async_update_service_appointment("APPOINTMENT", config),
        sdk.async_update_vehicle_preferred_dealer("VIN", "DEALER"),
    )

    for call in calls:
        with pytest.raises(ReadOnlyError):
            await call

    assert session.calls == []
