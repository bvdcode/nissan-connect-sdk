from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import FrozenInstanceError
from datetime import UTC, date, datetime

import pytest
from test_service_reads import (
    FakeSession,
    assert_graphql_call,
    graphql_response,
    make_client,
    preferred_dealer,
    recall,
    service_history_entry,
    vehicle_data,
    warranty,
)

from pynissan import (
    UNSET,
    DistanceUnit,
    PreferredDealerAddress,
    PreferredDealerLocation,
    RecallType,
    ServiceHistoryMileage,
    VehiclePreferredDealer,
    VehicleRecall,
    VehicleRoadsideAssistance,
    VehicleServiceHistoryEntry,
    VehicleServiceOperation,
    VehicleWarranty,
    VehicleWarrantyInfo,
    VehicleWarrantyPeriod,
    WarrantyInfoColorStatus,
    WarrantyInfoWarrantyStatus,
)
from pynissan.service_parsing import (
    parse_vehicle_preferred_dealer,
    parse_vehicle_recalls,
    parse_vehicle_roadside_assistance,
    parse_vehicle_service_history,
    parse_warranty_info,
)


async def test_service_reads_use_exact_operations_and_parse_full_responses() -> None:
    session = FakeSession(
        graphql_response(vehicle_data(preferredDealer=preferred_dealer())),
        graphql_response(vehicle_data(recalls=[recall()])),
        graphql_response(
            vehicle_data(
                roadsideAssistance={
                    "__typename": "RoadsideAssistance",
                    "roadsideMonths": 36,
                    "roadsideMiles": 36000,
                    "towingMonths": 60,
                    "towingMiles": 60000,
                }
            )
        ),
        graphql_response(vehicle_data(serviceHistory=[service_history_entry()])),
        graphql_response(vehicle_data(warranty=warranty())),
    )
    client = make_client(session)

    dealer_result = await client.async_get_vehicle_preferred_dealer("VIN")
    recalls_result = await client.async_get_vehicle_recalls("VIN")
    roadside_result = await client.async_get_vehicle_roadside_assistance("VIN")
    history_result = await client.async_get_vehicle_service_history("VIN")
    warranty_result = await client.async_get_warranty_info("VIN")

    assert dealer_result == VehiclePreferredDealer(
        id="dealer-id",
        hash_id="dealer-hash",
        name="Nissan San Diego",
        address=PreferredDealerAddress(
            address1="1 Main St",
            address2="Suite 2",
            city="San Diego",
            state="CA",
            postal_code="92101",
            country="US",
        ),
        hours="Mon-Fri",
        phone="555-0100",
        service_phone="555-0101",
        native_service_booking=True,
        scheduling_url_mobile="https://example.test/service",
        location=PreferredDealerLocation(latitude=32.7157, longitude=-117.1611),
        languages_spoken=("English", "Spanish"),
    )
    assert recalls_result == (
        VehicleRecall(
            effective_date=datetime.fromisoformat("2026-02-03T04:05:06-08:00"),
            nhtsa_id="26V001",
            primary_description="Primary description",
            remedy_description="Remedy description",
            risk_description="Risk description",
            title="Campaign title",
            type=RecallType.RECALL,
            recall_code="PC001",
        ),
    )
    assert roadside_result == VehicleRoadsideAssistance(36, 36000, 60, 60000)
    assert history_result == (
        VehicleServiceHistoryEntry(
            mileage=ServiceHistoryMileage(DistanceUnit.MILE, 12345),
            service_date=datetime(2026, 3, 4, 5, 6, 7, tzinfo=UTC),
            dealer_name="Nissan San Diego",
            dealer_code="CA001",
            services=("Inspection", "Tire rotation"),
            comment="Completed",
            maintenance_id=42,
            service_operation=VehicleServiceOperation(
                service_category_id="category-id",
                service_category_name="Maintenance",
                op_code_id="OP-1",
                op_code_description="Scheduled service",
            ),
        ),
    )
    assert warranty_result == VehicleWarranty(
        warranty_info=VehicleWarrantyInfo(
            color_status=WarrantyInfoColorStatus.GREEN,
            warranty_status=WarrantyInfoWarrantyStatus.ACTIVE,
            total_mileage=36000,
            total_months="36",
        ),
        start_period=VehicleWarrantyPeriod(0, date(2024, 1, 2)),
        end_period=VehicleWarrantyPeriod(36000, date(2027, 1, 2)),
        current_period=VehicleWarrantyPeriod(12000, date(2026, 7, 31)),
    )
    assert isinstance(warranty_result.current_period.date, date)
    assert recalls_result[0].effective_date.utcoffset() is not None
    assert history_result[0].service_date.utcoffset() is not None
    with pytest.raises(FrozenInstanceError):
        dealer_result.name = "Changed"

    expected_calls = (
        ("VehiclePreferredDealer", {"vin": "VIN"}),
        ("VehicleRecalls", {"vin": "VIN"}),
        ("VehicleRoadsideAssistance", {"vin": "VIN"}),
        ("VehicleServiceHistory", {"vin": "VIN"}),
        ("WarrantyInfo", {"vin": "VIN"}),
    )
    for index, (operation_name, variables) in enumerate(expected_calls):
        assert_graphql_call(session, index, operation_name, variables)


async def test_service_read_variables_preserve_unset_null_and_values() -> None:
    history_response = graphql_response(vehicle_data(serviceHistory=[]))
    warranty_response = graphql_response(vehicle_data(warranty=None))
    session = FakeSession(
        history_response,
        graphql_response(vehicle_data(serviceHistory=[])),
        graphql_response(vehicle_data(serviceHistory=[])),
        warranty_response,
        graphql_response(vehicle_data(warranty=None)),
        graphql_response(vehicle_data(warranty=None)),
    )
    client = make_client(session)

    assert await client.async_get_vehicle_service_history("VIN", unit=UNSET) == ()
    assert await client.async_get_vehicle_service_history("VIN", unit=None) == ()
    assert await client.async_get_vehicle_service_history("VIN", unit=DistanceUnit.KILOMETER) == ()
    assert await client.async_get_warranty_info("VIN", mileage=UNSET) is None
    assert await client.async_get_warranty_info("VIN", mileage=None) is None
    assert await client.async_get_warranty_info("VIN", mileage=12345) is None

    expected_calls = (
        ("VehicleServiceHistory", {"vin": "VIN"}),
        ("VehicleServiceHistory", {"vin": "VIN", "unit": None}),
        ("VehicleServiceHistory", {"vin": "VIN", "unit": "KILOMETER"}),
        ("WarrantyInfo", {"vin": "VIN"}),
        ("WarrantyInfo", {"vin": "VIN", "mileage": None}),
        ("WarrantyInfo", {"vin": "VIN", "mileage": 12345}),
    )
    for index, (operation_name, variables) in enumerate(expected_calls):
        assert_graphql_call(session, index, operation_name, variables)

    call_count = len(session.calls)
    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        await client.async_get_vehicle_service_history(
            "VIN",
            unit=DistanceUnit.UNKNOWN_VALUE,
        )
    assert len(session.calls) == call_count


def test_nullable_vehicle_and_service_response_chains_are_preserved() -> None:
    null_vehicle: dict[str, object] = {"vehicle": None}
    parsers: tuple[Callable[[Mapping[str, object]], object], ...] = (
        parse_vehicle_preferred_dealer,
        parse_vehicle_recalls,
        parse_vehicle_roadside_assistance,
        parse_vehicle_service_history,
        parse_warranty_info,
    )
    for parser in parsers:
        assert parser(null_vehicle) is None

    assert parse_vehicle_preferred_dealer(vehicle_data(preferredDealer=None)) is None
    assert parse_vehicle_roadside_assistance(vehicle_data(roadsideAssistance=None)) is None
    assert parse_warranty_info(vehicle_data(warranty=None)) is None

    dealer_result = parse_vehicle_preferred_dealer(
        vehicle_data(
            preferredDealer=preferred_dealer(
                id=None,
                hashId=None,
                name=None,
                address=None,
                hours=None,
                phone=None,
                servicePhone=None,
                nativeServiceBooking=None,
                schedulingUrlMobile=None,
                location=None,
                languagesSpoken=[],
            )
        )
    )
    recalls_result = parse_vehicle_recalls(
        vehicle_data(recalls=[recall(nhtsaId=None, recallCode=None)])
    )
    roadside_result = parse_vehicle_roadside_assistance(
        vehicle_data(
            roadsideAssistance={
                "__typename": "RoadsideAssistance",
                "roadsideMonths": None,
                "roadsideMiles": None,
                "towingMonths": None,
                "towingMiles": None,
            }
        )
    )
    history_result = parse_vehicle_service_history(
        vehicle_data(
            serviceHistory=[
                service_history_entry(
                    services=[],
                    comment=None,
                    maintenanceId=None,
                    serviceOperation=None,
                )
            ]
        )
    )

    assert dealer_result == VehiclePreferredDealer(
        id=None,
        hash_id=None,
        name=None,
        address=None,
        hours=None,
        phone=None,
        service_phone=None,
        native_service_booking=None,
        scheduling_url_mobile=None,
        location=None,
        languages_spoken=(),
    )
    assert recalls_result is not None
    assert recalls_result[0].nhtsa_id is None
    assert recalls_result[0].recall_code is None
    assert roadside_result == VehicleRoadsideAssistance(None, None, None, None)
    assert history_result is not None
    assert history_result[0].services == ()
    assert history_result[0].comment is None
    assert history_result[0].maintenance_id is None
    assert history_result[0].service_operation is None


def test_future_response_enums_map_to_unknown_sentinels() -> None:
    recalls_result = parse_vehicle_recalls(
        vehicle_data(recalls=[recall(type="FUTURE_RECALL_TYPE")])
    )
    history_result = parse_vehicle_service_history(
        vehicle_data(
            serviceHistory=[
                service_history_entry(
                    mileageWithUnit={
                        "__typename": "Mileage",
                        "unit": "FURLONG",
                        "value": 1,
                    }
                )
            ]
        )
    )
    future_info = {
        "__typename": "WarrantyInfo",
        "colorStatus": "BLUE",
        "warrantyStatus": "PAUSED",
        "totalMileage": 1,
        "totalMonths": "1",
    }
    warranty_result = parse_warranty_info(vehicle_data(warranty=warranty(warrantyInfo=future_info)))

    assert recalls_result is not None
    assert recalls_result[0].type is RecallType.UNKNOWN_VALUE
    assert history_result is not None
    assert history_result[0].mileage.unit is DistanceUnit.UNKNOWN_VALUE
    assert warranty_result is not None
    assert warranty_result.warranty_info.color_status is WarrantyInfoColorStatus.UNKNOWN_VALUE
    assert warranty_result.warranty_info.warranty_status is WarrantyInfoWarrantyStatus.UNKNOWN_VALUE


@pytest.mark.parametrize(
    ("parser", "payload"),
    [
        (parse_vehicle_preferred_dealer, vehicle_data(preferredDealer=None)),
        (parse_vehicle_recalls, vehicle_data(recalls=[])),
        (parse_vehicle_roadside_assistance, vehicle_data(roadsideAssistance=None)),
        (parse_vehicle_service_history, vehicle_data(serviceHistory=[])),
        (parse_warranty_info, vehicle_data(warranty=None)),
    ],
)
def test_nullable_top_level_service_branches_are_valid(
    parser: Callable[[Mapping[str, object]], object],
    payload: Mapping[str, object],
) -> None:
    parser(payload)
