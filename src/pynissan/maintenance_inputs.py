from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime

from .graphql_input import (
    UNSET,
    UnsetType,
    optional_input_fields,
    serialize_datetime,
    serialize_enum,
)
from .models import DistanceUnit


@dataclass(frozen=True, slots=True)
class PastServiceInput:
    """Fields accepted when adding a completed service record."""

    vin: str
    dealer_id: int
    invoice_date: date
    odometer: int
    op_code_id: str | UnsetType | None = UNSET
    comment: str | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class UpdatePastServiceInput:
    """Fields accepted when replacing a completed service record."""

    vin: str
    dealer_id: int
    invoice_date: date
    odometer: int
    maintenance_id: int
    op_code_id: str | UnsetType | None = UNSET
    comment: str | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class DistanceInput:
    """Integer reminder distance whose non-null unit may be omitted."""

    value: int
    unit: DistanceUnit | UnsetType = UNSET


@dataclass(frozen=True, slots=True)
class ReminderInterval:
    """Optional calendar and distance intervals for a parts reminder."""

    months_interval: int | UnsetType | None = UNSET
    distance_interval: DistanceInput | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class CreatePartsReminderInput:
    """Fields accepted when creating a parts reminder."""

    parts: tuple[str, ...]
    mileage: DistanceInput | UnsetType | None = UNSET
    date: datetime | UnsetType | None = UNSET
    interval: ReminderInterval | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class UpdatePartsReminderInput:
    """Fields accepted when replacing a parts reminder."""

    id: str
    parts: tuple[str, ...]
    mileage: DistanceInput | UnsetType | None = UNSET
    date: datetime | UnsetType | None = UNSET
    interval: ReminderInterval | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class ResetPartsReminderInput:
    """Fields accepted when resetting a parts reminder schedule."""

    id: str
    parts: tuple[str, ...]
    interval: ReminderInterval | UnsetType | None = UNSET


def get_maintenance_timeline_variables(
    vin: str,
    mileage_unit: DistanceUnit,
) -> dict[str, object]:
    """Serialize required GetMaintenanceTimeline variables."""

    return {"vin": vin, "mileageUnit": serialize_enum(mileage_unit)}


def get_service_contracts_variables(vin: str, mileage: int) -> dict[str, object]:
    """Serialize required GetServiceContracts variables."""

    return {"vin": vin, "mileage": mileage}


def add_past_service_variables(
    service: PastServiceInput | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize the nullable and omittable AddPastService input variable."""

    return optional_input_fields(
        input=_optional_serialized(service, past_service_input),
    )


def update_past_service_variables(service: UpdatePastServiceInput) -> dict[str, object]:
    """Serialize the required UpdatePastService input variable."""

    return {"input": update_past_service_input(service)}


def parts_reminders_variables(
    vin: str,
    *,
    unit: DistanceUnit | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize PartsReminders variables while preserving Apollo optionality."""

    return optional_input_fields(vin=vin, unit=_optional_distance_unit(unit))


def create_parts_reminder_variables(
    vin: str,
    reminder: CreatePartsReminderInput,
) -> dict[str, object]:
    """Serialize required CreatePartsReminder variables."""

    return {"vin": vin, "reminder": create_parts_reminder_input(reminder)}


def update_parts_reminder_variables(
    vin: str,
    reminder: UpdatePartsReminderInput,
) -> dict[str, object]:
    """Serialize required UpdatePartsReminder variables."""

    return {"vin": vin, "reminder": update_parts_reminder_input(reminder)}


def reset_parts_reminder_variables(
    vin: str,
    reminder: ResetPartsReminderInput,
) -> dict[str, object]:
    """Serialize required ResetPartsReminder variables."""

    return {"vin": vin, "reminder": reset_parts_reminder_input(reminder)}


def delete_parts_reminder_variables(vin: str, reminder_id: str) -> dict[str, object]:
    """Serialize required DeletePartsReminder variables."""

    return {"vin": vin, "reminderId": reminder_id}


def collision_history_variables(vin: str) -> dict[str, object]:
    """Serialize required CollisionHistory variables."""

    return {"vin": vin}


def collision_probe_data_variables(vin: str) -> dict[str, object]:
    """Serialize required CollisionProbeData variables."""

    return {"vin": vin}


def past_service_input(value: PastServiceInput) -> dict[str, object]:
    """Serialize PastServiceInput without adding application defaults."""

    return optional_input_fields(
        vin=value.vin,
        dealerId=value.dealer_id,
        opCodeID=value.op_code_id,
        invoiceDate=value.invoice_date.isoformat(),
        odometer=value.odometer,
        comment=value.comment,
    )


def update_past_service_input(value: UpdatePastServiceInput) -> dict[str, object]:
    """Serialize UpdatePastServiceInput without adding application defaults."""

    return optional_input_fields(
        vin=value.vin,
        dealerId=value.dealer_id,
        opCodeID=value.op_code_id,
        invoiceDate=value.invoice_date.isoformat(),
        odometer=value.odometer,
        comment=value.comment,
        maintenanceId=value.maintenance_id,
    )


def distance_input(value: DistanceInput) -> dict[str, object]:
    """Serialize DistanceInput while omitting its optional non-null unit."""

    unit: str | UnsetType
    if isinstance(value.unit, DistanceUnit):
        unit = serialize_enum(value.unit)
    else:
        unit = value.unit
    return optional_input_fields(value=value.value, unit=unit)


def reminder_interval_input(value: ReminderInterval) -> dict[str, object]:
    """Serialize ReminderInterval while preserving omitted and null fields."""

    return optional_input_fields(
        monthsInterval=value.months_interval,
        distanceInterval=_optional_serialized(
            value.distance_interval,
            distance_input,
        ),
    )


def create_parts_reminder_input(value: CreatePartsReminderInput) -> dict[str, object]:
    """Serialize CreatePartsReminderInput exactly as supplied."""

    return optional_input_fields(
        mileage=_optional_serialized(value.mileage, distance_input),
        date=_optional_datetime(value.date),
        interval=_optional_serialized(value.interval, reminder_interval_input),
        parts=list(value.parts),
    )


def update_parts_reminder_input(value: UpdatePartsReminderInput) -> dict[str, object]:
    """Serialize UpdatePartsReminderInput exactly as supplied."""

    return optional_input_fields(
        id=value.id,
        mileage=_optional_serialized(value.mileage, distance_input),
        date=_optional_datetime(value.date),
        interval=_optional_serialized(value.interval, reminder_interval_input),
        parts=list(value.parts),
    )


def reset_parts_reminder_input(value: ResetPartsReminderInput) -> dict[str, object]:
    """Serialize ResetPartsReminderInput exactly as supplied."""

    return optional_input_fields(
        id=value.id,
        interval=_optional_serialized(value.interval, reminder_interval_input),
        parts=list(value.parts),
    )


def _optional_serialized[InputT](
    value: InputT | UnsetType | None,
    serializer: Callable[[InputT], object],
) -> object:
    if isinstance(value, UnsetType) or value is None:
        return value
    return serializer(value)


def _optional_datetime(value: datetime | UnsetType | None) -> object:
    if isinstance(value, UnsetType) or value is None:
        return value
    return serialize_datetime(value)


def _optional_distance_unit(value: DistanceUnit | UnsetType | None) -> object:
    if isinstance(value, DistanceUnit):
        return serialize_enum(value)
    return value
