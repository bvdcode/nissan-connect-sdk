from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
from enum import StrEnum

from .exceptions import ResponseError
from .maintenance_models import (
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
    PastServiceResult,
    PastServiceSuccess,
    ReminderDistance,
    ServiceContract,
    UnknownPastServiceResult,
    VehiclePartsReminders,
    WarrantyServiceContractStatus,
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


def _parse_service_contract(value: object, path: str) -> ServiceContract:
    contract = _typed_object(value, path)
    return ServiceContract(
        status=_required_nullable_enum(
            contract,
            "status",
            WarrantyServiceContractStatus,
            f"{path}.status",
        ),
        coverage=_required_nullable_string(contract, "coverage", f"{path}.coverage"),
        coverage_description=_required_nullable_string(
            contract,
            "coverageDescription",
            f"{path}.coverageDescription",
        ),
        coverage_name=_required_nullable_string(
            contract,
            "coverageName",
            f"{path}.coverageName",
        ),
        plan_effective_date=_required_nullable_date(
            contract,
            "planEffectiveDate",
            f"{path}.planEffectiveDate",
        ),
        plan_effective_miles=_required_nullable_int(
            contract,
            "planEffectiveMiles",
            f"{path}.planEffectiveMiles",
        ),
        plan_expiration_date=_required_nullable_date(
            contract,
            "planExpirationDate",
            f"{path}.planExpirationDate",
        ),
        plan_expiration_odometer=_required_nullable_int(
            contract,
            "planExpirationOdometer",
            f"{path}.planExpirationOdometer",
        ),
        plan_cancelled_date=_required_nullable_date(
            contract,
            "planCancelledDate",
            f"{path}.planCancelledDate",
        ),
        plan_cancelled_odometer=_required_nullable_int(
            contract,
            "planCancelledOdometer",
            f"{path}.planCancelledOdometer",
        ),
        agreement=_required_nullable_string(contract, "agreement", f"{path}.agreement"),
        deductible_amount=_required_nullable_int(
            contract,
            "deductibleAmount",
            f"{path}.deductibleAmount",
        ),
        expiring_soon=_required_nullable_bool(
            contract,
            "expiringSoon",
            f"{path}.expiringSoon",
        ),
    )


def _parse_past_service_result(
    data: Mapping[str, object],
    root_field: str,
) -> PastServiceResult | None:
    root = _root(data, root_field)
    if root is None:
        return None

    typename = _typename(root, root_field)
    if typename == "PastServiceSuccess":
        return PastServiceSuccess(_required_bool(root, "success", f"{root_field}.success"))
    if typename == "RegisterGeneralError":
        return PastServiceGeneralError(_required_string(root, "message", f"{root_field}.message"))
    if typename == "PastServiceExists":
        return PastServiceExists(_required_string(root, "message", f"{root_field}.message"))
    return UnknownPastServiceResult(typename)


def _parse_part(value: object, path: str) -> MaintenancePart:
    part = _typed_object(value, path)
    configuration_path = f"{path}.reminderConfiguration"
    raw_configuration = _required_optional_typed_object(
        part,
        "reminderConfiguration",
        configuration_path,
    )
    configuration = None
    if raw_configuration is not None:
        months_path = f"{configuration_path}.months"
        distance_path = f"{configuration_path}.distance"
        raw_months = _required_optional_typed_object(
            raw_configuration,
            "months",
            months_path,
        )
        raw_distance = _required_optional_typed_object(
            raw_configuration,
            "distance",
            distance_path,
        )
        configuration = PartReminderConfiguration(
            months=(
                _parse_configuration_thresholds(raw_months, months_path)
                if raw_months is not None
                else None
            ),
            distance=(
                _parse_configuration_thresholds(raw_distance, distance_path)
                if raw_distance is not None
                else None
            ),
        )

    return MaintenancePart(
        id=_required_nullable_string(part, "id", f"{path}.id"),
        name=_required_string(part, "name", f"{path}.name"),
        reminder_configuration=configuration,
    )


def _parse_configuration_thresholds(
    value: object,
    path: str,
) -> PartsReminderConfigurationThresholds:
    thresholds = _typed_object(value, path)
    return PartsReminderConfigurationThresholds(
        min=_required_int(thresholds, "min", f"{path}.min"),
        max=_required_int(thresholds, "max", f"{path}.max"),
        interval=_required_int(thresholds, "interval", f"{path}.interval"),
        distance_unit=_required_nullable_enum(
            thresholds,
            "distanceUnit",
            DistanceUnit,
            f"{path}.distanceUnit",
        ),
    )


def _parse_parts_reminder(value: object, path: str) -> PartsReminder:
    reminder = _typed_object(value, path)
    parts_path = f"{path}.parts"
    raw_parts = _required_list(reminder, "parts", parts_path)
    parts: list[MaintenancePart] = []
    for index, raw_part in enumerate(raw_parts):
        parts.append(_parse_part(raw_part, f"{parts_path}[{index}]"))

    return PartsReminder(
        id=_required_string(reminder, "id", f"{path}.id"),
        overdue=_required_bool(reminder, "overdue", f"{path}.overdue"),
        date=_required_nullable_datetime(reminder, "date", f"{path}.date"),
        months_interval=_required_nullable_int(
            reminder,
            "monthsInterval",
            f"{path}.monthsInterval",
        ),
        distance_interval=_required_nullable_distance(
            reminder,
            "distanceInterval",
            f"{path}.distanceInterval",
        ),
        next_reminder_distance=_required_nullable_distance(
            reminder,
            "nextReminderDistance",
            f"{path}.nextReminderDistance",
        ),
        next_reminder_date=_required_nullable_datetime(
            reminder,
            "nextReminderDate",
            f"{path}.nextReminderDate",
        ),
        status=_required_nullable_enum(
            reminder,
            "status",
            PartsReminderStatus,
            f"{path}.status",
        ),
        parts=tuple(parts),
        mileage=_required_nullable_distance(
            reminder,
            "mileage",
            f"{path}.mileage",
        ),
    )


def _required_nullable_distance(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> ReminderDistance | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    distance = _typed_object(value, path)
    return ReminderDistance(
        unit=_required_enum(distance, "unit", DistanceUnit, f"{path}.unit"),
        value=_required_int(distance, "value", f"{path}.value"),
    )


def _parse_parts_reminder_mutation(
    data: Mapping[str, object],
    root_field: str,
    *,
    conditional_response_status: bool,
) -> PartsReminderMutationResult | None:
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if conditional_response_status and typename != "ResponseStatus":
        return PartsReminderMutationResult(typename=typename, success=None)
    return PartsReminderMutationResult(
        typename=typename,
        success=_required_nullable_bool(root, "success", f"{root_field}.success"),
    )


def _vehicle(data: Mapping[str, object]) -> Mapping[str, object] | None:
    return _root(data, "vehicle")


def _root(
    data: Mapping[str, object],
    root_field: str,
) -> Mapping[str, object] | None:
    if root_field not in data:
        raise ResponseError(f"{root_field} is missing")
    return _optional_typed_object(data[root_field], root_field)


def _required_field(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> object:
    if field not in container:
        raise ResponseError(f"{path} is missing")
    return container[field]


def _typed_object(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ResponseError(f"{path} is not an object")
    _typename(value, path)
    return value


def _optional_typed_object(
    value: object,
    path: str,
) -> Mapping[str, object] | None:
    if value is None:
        return None
    return _typed_object(value, path)


def _required_optional_typed_object(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> Mapping[str, object] | None:
    return _optional_typed_object(_required_field(container, field, path), path)


def _typename(container: Mapping[str, object], path: str) -> str:
    return _required_string(container, "__typename", f"{path}.__typename")


def _required_list(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> list[object]:
    value = _required_field(container, field, path)
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    return value


def _required_nullable_list(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> list[object] | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    return value


def _string(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise ResponseError(f"{path} is not a string")
    return value


def _required_string(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> str:
    return _string(_required_field(container, field, path), path)


def _required_nullable_string(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> str | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    return _string(value, path)


def _int(value: object, path: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ResponseError(f"{path} is not an integer")
    return value


def _required_int(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> int:
    return _int(_required_field(container, field, path), path)


def _required_nullable_int(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> int | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    return _int(value, path)


def _float(value: object, path: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ResponseError(f"{path} is not numeric")
    return float(value)


def _required_float(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> float:
    return _float(_required_field(container, field, path), path)


def _required_bool(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> bool:
    value = _required_field(container, field, path)
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


def _required_nullable_bool(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> bool | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


def _required_enum[EnumT: StrEnum](
    container: Mapping[str, object],
    field: str,
    enum_type: type[EnumT],
    path: str,
) -> EnumT:
    return _enum(_required_field(container, field, path), enum_type, path)


def _required_nullable_enum[EnumT: StrEnum](
    container: Mapping[str, object],
    field: str,
    enum_type: type[EnumT],
    path: str,
) -> EnumT | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    return _enum(value, enum_type, path)


def _enum[EnumT: StrEnum](
    value: object,
    enum_type: type[EnumT],
    path: str,
) -> EnumT:
    raw_value = _string(value, path)
    try:
        return enum_type(raw_value)
    except ValueError:
        try:
            return enum_type("UNKNOWN__")
        except ValueError:
            raise ResponseError(f"{path} has an unsupported value: {raw_value}") from None


def _required_datetime(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> datetime:
    return _datetime(_required_field(container, field, path), path)


def _required_nullable_datetime(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> datetime | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    return _datetime(value, path)


def _datetime(value: object, path: str) -> datetime:
    raw_value = _string(value, path)
    normalized = f"{raw_value[:-1]}+00:00" if raw_value.endswith("Z") else raw_value
    try:
        result = datetime.fromisoformat(normalized)
    except ValueError as error:
        raise ResponseError(f"{path} is not an ISO-8601 date-time") from error
    if result.tzinfo is None or result.utcoffset() is None:
        raise ResponseError(f"{path} is not an ISO-8601 date-time with an offset")
    return result


def _required_date(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> date:
    return _date(_required_field(container, field, path), path)


def _required_nullable_date(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> date | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    return _date(value, path)


def _date(value: object, path: str) -> date:
    raw_value = _string(value, path)
    try:
        return date.fromisoformat(raw_value)
    except ValueError as error:
        raise ResponseError(f"{path} is not an ISO-8601 date") from error
