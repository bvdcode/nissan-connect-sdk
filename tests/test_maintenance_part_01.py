from __future__ import annotations

import hashlib
from collections.abc import Callable, Mapping
from dataclasses import FrozenInstanceError
from datetime import UTC, date, datetime, timedelta, timezone

import pytest
from test_maintenance import (
    EXPECTED_OPERATION_IDS,
    part,
    parts_reminder,
    service_contract,
    vehicle_data,
)

from pynissan import operations
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
    MaintenancePart,
    MaintenanceTimeline,
    PartReminderConfiguration,
    PartsReminder,
    PartsReminderConfigurationThresholds,
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
    parse_maintenance_timeline,
    parse_parts_reminders,
    parse_service_contracts,
    parse_update_past_service,
)
from pynissan.models import DistanceUnit


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
