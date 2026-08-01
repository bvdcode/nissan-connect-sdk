from __future__ import annotations

from collections.abc import Mapping

from ._maintenance_detail_parsing import (
    _parse_part,
    _parse_parts_reminder,
    _parse_parts_reminder_mutation,
    _parse_past_service_result,
    _parse_service_contract,
)
from ._maintenance_value_parsing import (
    _required_date,
    _required_datetime,
    _required_enum,
    _required_float,
    _required_int,
    _required_nullable_datetime,
    _required_nullable_list,
    _required_optional_typed_object,
    _required_string,
    _typed_object,
    _typename,
    _vehicle,
)
from .maintenance_models import (
    CollisionHistoryEntry,
    CollisionProbeReading,
    MaintenancePart,
    MaintenanceTimeline,
    PartsReminder,
    PartsReminderMutationResult,
    PastServiceResult,
    ServiceContract,
    VehiclePartsReminders,
)
from .models import DistanceUnit

_AVK2_VEHICLE_TYPENAMES = frozenset(
    {
        "AVK2Vehicle",
        "ElectricAVK2Vehicle",
        "ElectricEVOVehicle",
        "EVOVehicle",
    }
)


def parse_maintenance_timeline(
    data: Mapping[str, object],
) -> MaintenanceTimeline | None:
    """Parse the nullable maintenance timeline for a vehicle."""

    vehicle = _vehicle(data)
    if vehicle is None:
        return None

    path = "vehicle.maintenanceTimeline"
    timeline = _required_optional_typed_object(vehicle, "maintenanceTimeline", path)
    if timeline is None:
        return None

    return MaintenanceTimeline(
        last_service_date=_required_date(
            timeline,
            "lastServiceDate",
            f"{path}.lastServiceDate",
        ),
        last_service_mileage=_required_int(
            timeline,
            "lastServiceMileage",
            f"{path}.lastServiceMileage",
        ),
        next_service_date=_required_date(
            timeline,
            "nextServiceDate",
            f"{path}.nextServiceDate",
        ),
        next_service_mileage=_required_int(
            timeline,
            "nextServiceMileage",
            f"{path}.nextServiceMileage",
        ),
        remaining_service_mileage=_required_int(
            timeline,
            "remainingServiceMileage",
            f"{path}.remainingServiceMileage",
        ),
        remaining_service_months=_required_int(
            timeline,
            "remainingServiceMonths",
            f"{path}.remainingServiceMonths",
        ),
        mileage_unit=_required_enum(
            timeline,
            "mileageUnit",
            DistanceUnit,
            f"{path}.mileageUnit",
        ),
        current_mileage=_required_int(
            timeline,
            "currentMileage",
            f"{path}.currentMileage",
        ),
    )


def parse_service_contracts(
    data: Mapping[str, object],
) -> tuple[ServiceContract | None, ...] | None:
    """Parse the nullable service-contract list for a vehicle."""

    vehicle = _vehicle(data)
    if vehicle is None:
        return None

    warranty_path = "vehicle.warranty"
    warranty = _required_optional_typed_object(vehicle, "warranty", warranty_path)
    if warranty is None:
        return None

    contracts_path = f"{warranty_path}.serviceContracts"
    raw_contracts = _required_nullable_list(warranty, "serviceContracts", contracts_path)
    if raw_contracts is None:
        return None

    contracts: list[ServiceContract | None] = []
    for index, raw_contract in enumerate(raw_contracts):
        if raw_contract is None:
            contracts.append(None)
            continue
        path = f"{contracts_path}[{index}]"
        contracts.append(_parse_service_contract(raw_contract, path))
    return tuple(contracts)


def parse_add_past_service(data: Mapping[str, object]) -> PastServiceResult | None:
    """Parse the nullable AddPastService union result."""

    return _parse_past_service_result(data, "addPastService")


def parse_update_past_service(data: Mapping[str, object]) -> PastServiceResult | None:
    """Parse the nullable UpdatePastService union result."""

    return _parse_past_service_result(data, "updatePastService")


def parse_parts_reminders(
    data: Mapping[str, object],
) -> VehiclePartsReminders | None:
    """Parse the nullable AVK2 part catalog and reminder list."""

    vehicle = _vehicle(data)
    if vehicle is None:
        return None
    if _typename(vehicle, "vehicle") not in _AVK2_VEHICLE_TYPENAMES:
        return None

    parts_path = "vehicle.parts"
    raw_parts = _required_nullable_list(vehicle, "parts", parts_path)
    parts: tuple[MaintenancePart | None, ...] | None = None
    if raw_parts is not None:
        parsed_parts: list[MaintenancePart | None] = []
        for index, raw_part in enumerate(raw_parts):
            if raw_part is None:
                parsed_parts.append(None)
                continue
            parsed_parts.append(_parse_part(raw_part, f"{parts_path}[{index}]"))
        parts = tuple(parsed_parts)

    reminders_path = "vehicle.partsReminders"
    raw_reminders = _required_nullable_list(vehicle, "partsReminders", reminders_path)
    reminders: tuple[PartsReminder | None, ...] | None = None
    if raw_reminders is not None:
        parsed_reminders: list[PartsReminder | None] = []
        for index, raw_reminder in enumerate(raw_reminders):
            if raw_reminder is None:
                parsed_reminders.append(None)
                continue
            parsed_reminders.append(
                _parse_parts_reminder(raw_reminder, f"{reminders_path}[{index}]")
            )
        reminders = tuple(parsed_reminders)

    return VehiclePartsReminders(parts=parts, reminders=reminders)


def parse_create_parts_reminder(
    data: Mapping[str, object],
) -> PartsReminderMutationResult | None:
    """Parse the nullable CreatePartsReminder response."""

    return _parse_parts_reminder_mutation(
        data,
        "createPartsReminder",
        conditional_response_status=False,
    )


def parse_update_parts_reminder(
    data: Mapping[str, object],
) -> PartsReminderMutationResult | None:
    """Parse the nullable UpdatePartsReminder union response."""

    return _parse_parts_reminder_mutation(
        data,
        "updatePartsReminder",
        conditional_response_status=True,
    )


def parse_reset_parts_reminder(
    data: Mapping[str, object],
) -> PartsReminderMutationResult | None:
    """Parse the nullable ResetPartsReminder response."""

    return _parse_parts_reminder_mutation(
        data,
        "resetPartsReminder",
        conditional_response_status=False,
    )


def parse_delete_parts_reminder(
    data: Mapping[str, object],
) -> PartsReminderMutationResult | None:
    """Parse the nullable DeletePartsReminder union response."""

    return _parse_parts_reminder_mutation(
        data,
        "deletePartsReminder",
        conditional_response_status=True,
    )


def parse_collision_history(
    data: Mapping[str, object],
) -> tuple[CollisionHistoryEntry | None, ...] | None:
    """Parse nullable collision reports for a vehicle."""

    vehicle = _vehicle(data)
    if vehicle is None:
        return None

    history_path = "vehicle.collisionHistory"
    raw_history = _required_nullable_list(vehicle, "collisionHistory", history_path)
    if raw_history is None:
        return None

    history: list[CollisionHistoryEntry | None] = []
    for index, raw_entry in enumerate(raw_history):
        if raw_entry is None:
            history.append(None)
            continue
        path = f"{history_path}[{index}]"
        entry = _typed_object(raw_entry, path)
        history.append(
            CollisionHistoryEntry(
                collision_id=_required_string(entry, "collisionId", f"{path}.collisionId"),
                report_date_time=_required_nullable_datetime(
                    entry,
                    "reportDateTime",
                    f"{path}.reportDateTime",
                ),
                collision_date_time=_required_nullable_datetime(
                    entry,
                    "collisionDateTime",
                    f"{path}.collisionDateTime",
                ),
            )
        )
    return tuple(history)


def parse_collision_probe_data(
    data: Mapping[str, object],
) -> tuple[CollisionProbeReading | None, ...] | None:
    """Parse nullable AVK2 collision probe readings for a vehicle."""

    vehicle = _vehicle(data)
    if vehicle is None:
        return None
    if _typename(vehicle, "vehicle") not in _AVK2_VEHICLE_TYPENAMES:
        return None

    readings_path = "vehicle.collisionProbeReadings"
    raw_readings = _required_nullable_list(
        vehicle,
        "collisionProbeReadings",
        readings_path,
    )
    if raw_readings is None:
        return None

    readings: list[CollisionProbeReading | None] = []
    for index, raw_reading in enumerate(raw_readings):
        if raw_reading is None:
            readings.append(None)
            continue
        path = f"{readings_path}[{index}]"
        reading = _typed_object(raw_reading, path)
        readings.append(
            CollisionProbeReading(
                collision_time=_required_datetime(
                    reading,
                    "collisionTime",
                    f"{path}.collisionTime",
                ),
                latitude=_required_float(reading, "latitude", f"{path}.latitude"),
                longitude=_required_float(reading, "longitude", f"{path}.longitude"),
                mil_count=_required_int(reading, "milCount", f"{path}.milCount"),
                mil_data=_required_string(reading, "milData", f"{path}.milData"),
                odometer=_required_float(reading, "odometer", f"{path}.odometer"),
                speed=_required_float(reading, "speed", f"{path}.speed"),
                unit=_required_enum(
                    reading,
                    "unit",
                    DistanceUnit,
                    f"{path}.unit",
                ),
            )
        )
    return tuple(readings)
