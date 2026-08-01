from __future__ import annotations

from collections.abc import Mapping

from ._maintenance_value_parsing import (
    _required_bool,
    _required_enum,
    _required_field,
    _required_int,
    _required_list,
    _required_nullable_bool,
    _required_nullable_date,
    _required_nullable_datetime,
    _required_nullable_enum,
    _required_nullable_int,
    _required_nullable_string,
    _required_optional_typed_object,
    _required_string,
    _root,
    _typed_object,
    _typename,
)
from .maintenance_models import (
    MaintenancePart,
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
