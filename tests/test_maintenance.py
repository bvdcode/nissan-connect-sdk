from __future__ import annotations

import hashlib
from collections.abc import Callable, Mapping
from dataclasses import FrozenInstanceError
from datetime import UTC, date, datetime, timedelta, timezone

import pytest

from pynissan import operations
from pynissan.exceptions import ResponseError
from pynissan.maintenance_inputs import (
    CreatePartsReminderInput,
    DistanceInput,
    PastServiceInput,
    ReminderInterval,
    ResetPartsReminderInput,
    UpdatePartsReminderInput,
    UpdatePastServiceInput,
    add_past_service_variables,
    collision_history_variables,
    collision_probe_data_variables,
    create_parts_reminder_variables,
    delete_parts_reminder_variables,
    distance_input,
    get_maintenance_timeline_variables,
    get_service_contracts_variables,
    parts_reminders_variables,
    reset_parts_reminder_variables,
    update_parts_reminder_variables,
    update_past_service_variables,
)
from pynissan.maintenance_models import (
    CollisionHistoryEntry,
    CollisionProbeReading,
    MaintenancePart,
    MaintenanceTimeline,
    PartReminderConfiguration,
    PartsReminder,
    PartsReminderConfigurationThresholds,
    PartsReminderMutationResult,
    PartsReminderStatus,
    PastServiceExists,
    PastServiceGeneralError,
    PastServiceSuccess,
    ReminderDistance,
    ServiceContract,
    UnknownPastServiceResult,
    VehiclePartsReminders,
    WarrantyServiceContractStatus,
)
from pynissan.maintenance_parsing import (
    parse_add_past_service,
    parse_collision_history,
    parse_collision_probe_data,
    parse_create_parts_reminder,
    parse_delete_parts_reminder,
    parse_maintenance_timeline,
    parse_parts_reminders,
    parse_reset_parts_reminder,
    parse_service_contracts,
    parse_update_parts_reminder,
    parse_update_past_service,
)
from pynissan.models import DistanceUnit

EXPECTED_OPERATION_IDS = {
    "GET_MAINTENANCE_TIMELINE": (
        "6bad114fbfd471b87bd47b5648b5f0637a93d0c23bd2eb6d274a39550dcf32d8"
    ),
    "GET_SERVICE_CONTRACTS": ("e962736c9aae011b2a36e6e58389149f31918e7857ce18600764875de90119ed"),
    "ADD_PAST_SERVICE": ("cafadb5455f97421a20e39cd512e4f6d330571bec51ead159d4475b4dcd232f4"),
    "UPDATE_PAST_SERVICE": ("fa9c97a384127dffe11abb854538bfa76f8d21420c043c4414a2fef348586b7b"),
    "PARTS_REMINDERS": ("4b5fb536d6007cd8c5f17a64a93dc6511ae69954c522f211ca4d42a69b0aeb7b"),
    "CREATE_PARTS_REMINDER": ("488ccc2a7e7a0af3112ab1a91ce224e2c83f7dbcdcf824df99049fdf0ab607f4"),
    "UPDATE_PARTS_REMINDER": ("08531ffe6e151b3bf7c8b6f33d04ca3408232f0c83bc743948e9dda9b2efd5ce"),
    "RESET_PARTS_REMINDER": ("2e015a323d69646298637c701cc5fb6842dfdb9e295ac18a6b93b68d9b582ea5"),
    "DELETE_PARTS_REMINDER": ("237b3f40451ba30e043a8b0b1dccd679bfd389924c16e1026c15ebdf10542b77"),
    "COLLISION_HISTORY": ("ca2779551c7312455dbe80dce6dac3199494f71a1010f53bc211616ce8776622"),
    "COLLISION_PROBE_DATA": ("f151d6ce54b3bc683412838ff8ce6460e06874e61a671da481d7d6238723c547"),
}


def vehicle_data(
    *,
    typename: str = "ElectricAVK2Vehicle",
    **fields: object,
) -> dict[str, object]:
    return {"vehicle": {"__typename": typename, **fields}}


def service_contract(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "__typename": "WarrantyServiceContract",
        "status": "ACTIVE",
        "coverage": "FULL",
        "coverageDescription": "Scheduled maintenance",
        "coverageName": "Maintenance Care",
        "planEffectiveDate": "2025-01-02",
        "planEffectiveMiles": 10,
        "planExpirationDate": "2028-01-02",
        "planExpirationOdometer": 36010,
        "planCancelledDate": None,
        "planCancelledOdometer": None,
        "agreement": "AG-1",
        "deductibleAmount": 25,
        "expiringSoon": False,
    }
    result.update(overrides)
    return result


def configuration_thresholds(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "__typename": "PartsReminderConfigurationThresholds",
        "min": 1,
        "max": 24,
        "interval": 1,
        "distanceUnit": "MILE",
    }
    result.update(overrides)
    return result


def part(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "__typename": "Part",
        "id": "engine-air-filter",
        "name": "Engine air filter",
        "reminderConfiguration": {
            "__typename": "PartReminderConfiguration",
            "months": configuration_thresholds(),
            "distance": configuration_thresholds(
                min=500,
                max=30000,
                interval=500,
                distanceUnit="MILE",
            ),
        },
    }
    result.update(overrides)
    return result


def reminder_distance(value: int = 12000) -> dict[str, object]:
    return {"__typename": "Distance", "unit": "MILE", "value": value}


def parts_reminder(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "__typename": "PartsReminder",
        "id": "reminder-1",
        "overdue": True,
        "date": "2026-07-30T10:20:30Z",
        "monthsInterval": 6,
        "distanceInterval": reminder_distance(5000),
        "nextReminderDistance": reminder_distance(17000),
        "nextReminderDate": "2027-01-30T10:20:30-08:00",
        "status": "OVERDUE",
        "parts": [part()],
        "mileage": reminder_distance(),
    }
    result.update(overrides)
    return result


def collision_probe_reading(**overrides: object) -> dict[str, object]:
    result: dict[str, object] = {
        "__typename": "CollisionProbeReading",
        "collisionTime": "2026-07-29T01:02:03Z",
        "latitude": 32.7157,
        "longitude": -117.1611,
        "milCount": 2,
        "milData": "P0001,P0002",
        "odometer": 12345.5,
        "speed": 21.25,
        "unit": "MILE",
    }
    result.update(overrides)
    return result


def without_field(value: Mapping[str, object], field: str) -> dict[str, object]:
    result = dict(value)
    del result[field]
    return result


def test_maintenance_operation_documents_match_service_persisted_hashes() -> None:
    for name, expected_id in EXPECTED_OPERATION_IDS.items():
        document = getattr(operations, name)
        operation_id = getattr(operations, f"{name}_OPERATION_ID")
        assert isinstance(document, str)
        assert operation_id == expected_id
        assert hashlib.sha256(document.encode()).hexdigest() == expected_id


def test_required_read_and_identity_variables_are_exact() -> None:
    assert get_maintenance_timeline_variables("VIN", DistanceUnit.MILE) == {
        "vin": "VIN",
        "mileageUnit": "MILE",
    }
    assert get_service_contracts_variables("VIN", 12345) == {
        "vin": "VIN",
        "mileage": 12345,
    }
    assert collision_history_variables("VIN") == {"vin": "VIN"}
    assert collision_probe_data_variables("VIN") == {"vin": "VIN"}
    assert delete_parts_reminder_variables("VIN", "reminder-id") == {
        "vin": "VIN",
        "reminderId": "reminder-id",
    }


def test_past_service_inputs_preserve_omitted_null_and_date_values() -> None:
    assert add_past_service_variables() == {}
    assert add_past_service_variables(None) == {"input": None}
    assert add_past_service_variables(
        PastServiceInput(
            vin="VIN",
            dealer_id=42,
            invoice_date=date(2026, 7, 30),
            odometer=12345,
        )
    ) == {
        "input": {
            "vin": "VIN",
            "dealerId": 42,
            "invoiceDate": "2026-07-30",
            "odometer": 12345,
        }
    }
    assert add_past_service_variables(
        PastServiceInput(
            vin="VIN",
            dealer_id=42,
            invoice_date=date(2026, 7, 30),
            odometer=12345,
            op_code_id=None,
            comment="Done",
        )
    ) == {
        "input": {
            "vin": "VIN",
            "dealerId": 42,
            "opCodeID": None,
            "invoiceDate": "2026-07-30",
            "odometer": 12345,
            "comment": "Done",
        }
    }
    assert update_past_service_variables(
        UpdatePastServiceInput(
            vin="VIN",
            dealer_id=42,
            invoice_date=date(2026, 7, 31),
            odometer=12350,
            maintenance_id=7,
            op_code_id="OP-1",
            comment=None,
        )
    ) == {
        "input": {
            "vin": "VIN",
            "dealerId": 42,
            "opCodeID": "OP-1",
            "invoiceDate": "2026-07-31",
            "odometer": 12350,
            "comment": None,
            "maintenanceId": 7,
        }
    }


def test_parts_reminder_inputs_preserve_nested_apollo_optionality() -> None:
    assert parts_reminders_variables("VIN") == {"vin": "VIN"}
    assert parts_reminders_variables("VIN", unit=None) == {"vin": "VIN", "unit": None}
    assert parts_reminders_variables("VIN", unit=DistanceUnit.KILOMETER) == {
        "vin": "VIN",
        "unit": "KILOMETER",
    }

    assert create_parts_reminder_variables(
        "VIN",
        CreatePartsReminderInput(parts=("part-1",)),
    ) == {"vin": "VIN", "reminder": {"parts": ["part-1"]}}
    assert create_parts_reminder_variables(
        "VIN",
        CreatePartsReminderInput(
            parts=("part-1", "part-2"),
            mileage=DistanceInput(12345, DistanceUnit.MILE),
            date=datetime(2026, 7, 31, 8, 9, 10, tzinfo=timezone(timedelta(hours=-7))),
            interval=ReminderInterval(
                months_interval=None,
                distance_interval=DistanceInput(5000),
            ),
        ),
    ) == {
        "vin": "VIN",
        "reminder": {
            "mileage": {"value": 12345, "unit": "MILE"},
            "date": "2026-07-31T08:09:10-07:00",
            "interval": {
                "monthsInterval": None,
                "distanceInterval": {"value": 5000},
            },
            "parts": ["part-1", "part-2"],
        },
    }
    assert update_parts_reminder_variables(
        "VIN",
        UpdatePartsReminderInput(
            id="reminder-1",
            parts=(),
            mileage=None,
            date=None,
            interval=None,
        ),
    ) == {
        "vin": "VIN",
        "reminder": {
            "id": "reminder-1",
            "mileage": None,
            "date": None,
            "interval": None,
            "parts": [],
        },
    }
    assert reset_parts_reminder_variables(
        "VIN",
        ResetPartsReminderInput(
            id="reminder-1",
            parts=("part-1",),
            interval=ReminderInterval(months_interval=12, distance_interval=None),
        ),
    ) == {
        "vin": "VIN",
        "reminder": {
            "id": "reminder-1",
            "interval": {"monthsInterval": 12, "distanceInterval": None},
            "parts": ["part-1"],
        },
    }


def test_input_enums_and_datetime_scalars_are_validated() -> None:
    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        get_maintenance_timeline_variables("VIN", DistanceUnit.UNKNOWN_VALUE)
    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        parts_reminders_variables("VIN", unit=DistanceUnit.UNKNOWN_VALUE)
    with pytest.raises(ValueError, match="UNKNOWN_VALUE"):
        distance_input(DistanceInput(1, DistanceUnit.UNKNOWN_VALUE))
    with pytest.raises(ValueError, match="UTC offset"):
        create_parts_reminder_variables(
            "VIN",
            CreatePartsReminderInput(
                parts=(),
                date=datetime(2026, 7, 31, 8, 9, 10),
            ),
        )


def test_maintenance_input_models_are_immutable() -> None:
    value = DistanceInput(100)
    with pytest.raises(FrozenInstanceError):
        value.value = 200


def test_maintenance_timeline_and_service_contracts_parse_exact_scalars() -> None:
    timeline = parse_maintenance_timeline(
        vehicle_data(
            maintenanceTimeline={
                "__typename": "MaintenanceTimeline",
                "lastServiceDate": "2026-01-02",
                "lastServiceMileage": 10000,
                "nextServiceDate": "2026-07-02",
                "nextServiceMileage": 15000,
                "remainingServiceMileage": 2500,
                "remainingServiceMonths": 3,
                "mileageUnit": "MILE",
                "currentMileage": 12500,
            }
        )
    )
    contracts = parse_service_contracts(
        vehicle_data(
            warranty={
                "__typename": "Warranty",
                "serviceContracts": [service_contract(), None],
            }
        )
    )

    assert timeline == MaintenanceTimeline(
        last_service_date=date(2026, 1, 2),
        last_service_mileage=10000,
        next_service_date=date(2026, 7, 2),
        next_service_mileage=15000,
        remaining_service_mileage=2500,
        remaining_service_months=3,
        mileage_unit=DistanceUnit.MILE,
        current_mileage=12500,
    )
    assert contracts == (
        ServiceContract(
            status=WarrantyServiceContractStatus.ACTIVE,
            coverage="FULL",
            coverage_description="Scheduled maintenance",
            coverage_name="Maintenance Care",
            plan_effective_date=date(2025, 1, 2),
            plan_effective_miles=10,
            plan_expiration_date=date(2028, 1, 2),
            plan_expiration_odometer=36010,
            plan_cancelled_date=None,
            plan_cancelled_odometer=None,
            agreement="AG-1",
            deductible_amount=25,
            expiring_soon=False,
        ),
        None,
    )


@pytest.mark.parametrize(
    ("parser", "root_field"),
    [
        (parse_add_past_service, "addPastService"),
        (parse_update_past_service, "updatePastService"),
    ],
)
def test_past_service_union_members_are_preserved(
    parser: Callable[[Mapping[str, object]], object],
    root_field: str,
) -> None:
    assert parser({root_field: {"__typename": "PastServiceSuccess", "success": True}}) == (
        PastServiceSuccess(True)
    )
    assert parser(
        {root_field: {"__typename": "RegisterGeneralError", "message": "Failed"}}
    ) == PastServiceGeneralError("Failed")
    assert parser(
        {root_field: {"__typename": "PastServiceExists", "message": "Exists"}}
    ) == PastServiceExists("Exists")
    assert parser({root_field: {"__typename": "FuturePastServiceResult"}}) == (
        UnknownPastServiceResult("FuturePastServiceResult")
    )
    assert parser({root_field: None}) is None


def test_parts_reminders_parse_full_nested_response() -> None:
    result = parse_parts_reminders(
        vehicle_data(parts=[part(), None], partsReminders=[parts_reminder(), None])
    )

    thresholds = PartsReminderConfigurationThresholds(
        min=1,
        max=24,
        interval=1,
        distance_unit=DistanceUnit.MILE,
    )
    distance_thresholds = PartsReminderConfigurationThresholds(
        min=500,
        max=30000,
        interval=500,
        distance_unit=DistanceUnit.MILE,
    )
    expected_part = MaintenancePart(
        id="engine-air-filter",
        name="Engine air filter",
        reminder_configuration=PartReminderConfiguration(
            months=thresholds,
            distance=distance_thresholds,
        ),
    )
    assert result == VehiclePartsReminders(
        parts=(expected_part, None),
        reminders=(
            PartsReminder(
                id="reminder-1",
                overdue=True,
                date=datetime(2026, 7, 30, 10, 20, 30, tzinfo=UTC),
                months_interval=6,
                distance_interval=ReminderDistance(DistanceUnit.MILE, 5000),
                next_reminder_distance=ReminderDistance(DistanceUnit.MILE, 17000),
                next_reminder_date=datetime.fromisoformat("2027-01-30T10:20:30-08:00"),
                status=PartsReminderStatus.OVERDUE,
                parts=(expected_part,),
                mileage=ReminderDistance(DistanceUnit.MILE, 12000),
            ),
            None,
        ),
    )


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
