from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import UTC, datetime

import pytest
from test_maintenance import (
    collision_probe_reading,
    configuration_thresholds,
    part,
    parts_reminder,
    service_contract,
    vehicle_data,
    without_field,
)

from pynissan.exceptions import ResponseError
from pynissan.maintenance_models import (
    CollisionHistoryEntry,
    CollisionProbeReading,
    PartsReminderMutationResult,
    PartsReminderStatus,
    VehiclePartsReminders,
    WarrantyServiceContractStatus,
)
from pynissan.maintenance_parsing import (
    parse_collision_history,
    parse_collision_probe_data,
    parse_create_parts_reminder,
    parse_delete_parts_reminder,
    parse_maintenance_timeline,
    parse_parts_reminders,
    parse_reset_parts_reminder,
    parse_service_contracts,
    parse_update_parts_reminder,
)
from pynissan.models import DistanceUnit


def test_parts_reminders_preserve_nullable_fields_and_future_enums() -> None:
    nullable_part = part(
        id=None,
        reminderConfiguration={
            "__typename": "PartReminderConfiguration",
            "months": configuration_thresholds(distanceUnit="FURLONG"),
            "distance": None,
        },
    )
    nullable_reminder = parts_reminder(
        date=None,
        monthsInterval=None,
        distanceInterval=None,
        nextReminderDistance=None,
        nextReminderDate=None,
        status="FUTURE_STATUS",
        parts=[],
        mileage=None,
    )
    result = parse_parts_reminders(
        vehicle_data(parts=[nullable_part], partsReminders=[nullable_reminder])
    )

    assert result is not None
    assert result.parts is not None
    assert result.parts[0] is not None
    configuration = result.parts[0].reminder_configuration
    assert configuration is not None
    assert configuration.months is not None
    assert configuration.months.distance_unit is DistanceUnit.UNKNOWN_VALUE
    assert result.reminders is not None
    assert result.reminders[0] is not None
    assert result.reminders[0].status is PartsReminderStatus.UNKNOWN_VALUE
    assert result.reminders[0].parts == ()


def test_parts_reminder_mutation_response_shapes_are_preserved() -> None:
    assert parse_create_parts_reminder(
        {"createPartsReminder": {"__typename": "ResponseStatus", "success": True}}
    ) == PartsReminderMutationResult("ResponseStatus", True)
    assert parse_update_parts_reminder(
        {"updatePartsReminder": {"__typename": "ResponseStatus", "success": None}}
    ) == PartsReminderMutationResult("ResponseStatus", None)
    assert parse_update_parts_reminder(
        {"updatePartsReminder": {"__typename": "FutureUpdateError"}}
    ) == PartsReminderMutationResult("FutureUpdateError", None)
    assert parse_reset_parts_reminder(
        {"resetPartsReminder": {"__typename": "ResponseStatus", "success": False}}
    ) == PartsReminderMutationResult("ResponseStatus", False)
    assert parse_delete_parts_reminder(
        {"deletePartsReminder": {"__typename": "FutureDeleteError"}}
    ) == PartsReminderMutationResult("FutureDeleteError", None)


def test_collision_history_and_probe_data_parse_exact_scalars() -> None:
    history = parse_collision_history(
        vehicle_data(
            collisionHistory=[
                {
                    "__typename": "CollisionHistory",
                    "collisionId": "collision-1",
                    "reportDateTime": "2026-07-29T02:03:04-07:00",
                    "collisionDateTime": None,
                },
                None,
            ]
        )
    )
    readings = parse_collision_probe_data(
        vehicle_data(collisionProbeReadings=[collision_probe_reading(), None])
    )

    assert history == (
        CollisionHistoryEntry(
            collision_id="collision-1",
            report_date_time=datetime.fromisoformat("2026-07-29T02:03:04-07:00"),
            collision_date_time=None,
        ),
        None,
    )
    assert readings == (
        CollisionProbeReading(
            collision_time=datetime(2026, 7, 29, 1, 2, 3, tzinfo=UTC),
            latitude=32.7157,
            longitude=-117.1611,
            mil_count=2,
            mil_data="P0001,P0002",
            odometer=12345.5,
            speed=21.25,
            unit=DistanceUnit.MILE,
        ),
        None,
    )


def test_nullable_response_chains_and_non_applicable_vehicle_unions() -> None:
    assert parse_maintenance_timeline({"vehicle": None}) is None
    assert parse_maintenance_timeline(vehicle_data(maintenanceTimeline=None)) is None
    assert parse_service_contracts(vehicle_data(warranty=None)) is None
    assert (
        parse_service_contracts(
            vehicle_data(warranty={"__typename": "Warranty", "serviceContracts": None})
        )
        is None
    )
    assert parse_parts_reminders(vehicle_data(typename="LegacyVehicle")) is None
    assert parse_parts_reminders(vehicle_data(parts=None, partsReminders=None)) == (
        VehiclePartsReminders(parts=None, reminders=None)
    )
    assert parse_collision_history(vehicle_data(collisionHistory=None)) is None
    assert parse_collision_probe_data(vehicle_data(typename="LegacyVehicle")) is None
    assert parse_collision_probe_data(vehicle_data(collisionProbeReadings=None)) is None
    assert parse_create_parts_reminder({"createPartsReminder": None}) is None
    assert parse_update_parts_reminder({"updatePartsReminder": None}) is None
    assert parse_reset_parts_reminder({"resetPartsReminder": None}) is None
    assert parse_delete_parts_reminder({"deletePartsReminder": None}) is None


def test_future_required_response_enums_map_to_unknown_sentinels() -> None:
    timeline = parse_maintenance_timeline(
        vehicle_data(
            maintenanceTimeline={
                "__typename": "MaintenanceTimeline",
                "lastServiceDate": "2026-01-02",
                "lastServiceMileage": 1,
                "nextServiceDate": "2026-02-02",
                "nextServiceMileage": 2,
                "remainingServiceMileage": 1,
                "remainingServiceMonths": 1,
                "mileageUnit": "FURLONG",
                "currentMileage": 1,
            }
        )
    )
    contracts = parse_service_contracts(
        vehicle_data(
            warranty={
                "__typename": "Warranty",
                "serviceContracts": [service_contract(status="PAUSED")],
            }
        )
    )
    readings = parse_collision_probe_data(
        vehicle_data(collisionProbeReadings=[collision_probe_reading(unit="FURLONG")])
    )

    assert timeline is not None
    assert timeline.mileage_unit is DistanceUnit.UNKNOWN_VALUE
    assert contracts is not None
    assert contracts[0] is not None
    assert contracts[0].status is WarrantyServiceContractStatus.UNKNOWN_VALUE
    assert readings is not None
    assert readings[0] is not None
    assert readings[0].unit is DistanceUnit.UNKNOWN_VALUE


@pytest.mark.parametrize(
    ("parser", "payload"),
    [
        (parse_maintenance_timeline, {}),
        (
            parse_maintenance_timeline,
            vehicle_data(
                maintenanceTimeline={
                    "__typename": "MaintenanceTimeline",
                    "lastServiceDate": "2026-01-02",
                    "lastServiceMileage": 1,
                    "nextServiceDate": "2026-02-02",
                    "nextServiceMileage": 2,
                    "remainingServiceMileage": 1,
                    "remainingServiceMonths": 1,
                    "mileageUnit": "MILE",
                }
            ),
        ),
        (
            parse_service_contracts,
            vehicle_data(warranty={"__typename": "Warranty"}),
        ),
        (
            parse_service_contracts,
            vehicle_data(
                warranty={
                    "__typename": "Warranty",
                    "serviceContracts": [without_field(service_contract(), "agreement")],
                }
            ),
        ),
        (
            parse_parts_reminders,
            vehicle_data(parts=[], partsReminders=[parts_reminder(parts=[None])]),
        ),
        (
            parse_parts_reminders,
            vehicle_data(parts=[], partsReminders=[parts_reminder(overdue=None)]),
        ),
        (
            parse_collision_history,
            vehicle_data(
                collisionHistory=[
                    {
                        "__typename": "CollisionHistory",
                        "collisionId": "collision-1",
                        "reportDateTime": None,
                    }
                ]
            ),
        ),
        (
            parse_collision_probe_data,
            vehicle_data(collisionProbeReadings=[collision_probe_reading(milCount=True)]),
        ),
        (
            parse_create_parts_reminder,
            {"createPartsReminder": {"__typename": "ResponseStatus"}},
        ),
        (
            parse_update_parts_reminder,
            {"updatePartsReminder": {"__typename": "ResponseStatus"}},
        ),
    ],
)
def test_missing_or_invalid_selected_fields_are_rejected(
    parser: Callable[[Mapping[str, object]], object],
    payload: Mapping[str, object],
) -> None:
    with pytest.raises(ResponseError):
        parser(payload)


@pytest.mark.parametrize(
    ("parser", "payload"),
    [
        (
            parse_maintenance_timeline,
            vehicle_data(
                maintenanceTimeline={
                    "__typename": "MaintenanceTimeline",
                    "lastServiceDate": "2026-02-30",
                    "lastServiceMileage": 1,
                    "nextServiceDate": "2026-03-01",
                    "nextServiceMileage": 2,
                    "remainingServiceMileage": 1,
                    "remainingServiceMonths": 1,
                    "mileageUnit": "MILE",
                    "currentMileage": 1,
                }
            ),
        ),
        (
            parse_collision_history,
            vehicle_data(
                collisionHistory=[
                    {
                        "__typename": "CollisionHistory",
                        "collisionId": "collision-1",
                        "reportDateTime": "2026-07-29T02:03:04",
                        "collisionDateTime": None,
                    }
                ]
            ),
        ),
        (
            parse_collision_probe_data,
            vehicle_data(
                collisionProbeReadings=[
                    collision_probe_reading(collisionTime="2026-07-29T01:02:03")
                ]
            ),
        ),
    ],
)
def test_date_and_datetime_scalars_reject_invalid_wire_values(
    parser: Callable[[Mapping[str, object]], object],
    payload: Mapping[str, object],
) -> None:
    with pytest.raises(ResponseError):
        parser(payload)
