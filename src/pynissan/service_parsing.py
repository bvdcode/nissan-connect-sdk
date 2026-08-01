from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
from enum import StrEnum

from .exceptions import ResponseError
from .models import DistanceUnit
from .service_models import (
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


def parse_vehicle_preferred_dealer(
    data: Mapping[str, object],
) -> VehiclePreferredDealer | None:
    """Parse the nullable preferred dealer associated with a vehicle."""

    vehicle = _vehicle(data)
    if vehicle is None:
        return None

    path = "vehicle.preferredDealer"
    dealer = _required_optional_typed_object(vehicle, "preferredDealer", path)
    if dealer is None:
        return None

    address = _parse_preferred_dealer_address(
        _required_field(dealer, "address", f"{path}.address"),
        f"{path}.address",
    )
    location = _parse_preferred_dealer_location(
        _required_field(dealer, "location", f"{path}.location"),
        f"{path}.location",
    )
    raw_languages = _list(
        _required_field(dealer, "languagesSpoken", f"{path}.languagesSpoken"),
        f"{path}.languagesSpoken",
    )
    languages: list[str] = []
    for index, raw_language in enumerate(raw_languages):
        languages.append(_string(raw_language, f"{path}.languagesSpoken[{index}]"))

    return VehiclePreferredDealer(
        id=_required_nullable_string(dealer, "id", f"{path}.id"),
        hash_id=_required_nullable_string(dealer, "hashId", f"{path}.hashId"),
        name=_required_nullable_string(dealer, "name", f"{path}.name"),
        address=address,
        hours=_required_nullable_string(dealer, "hours", f"{path}.hours"),
        phone=_required_nullable_string(dealer, "phone", f"{path}.phone"),
        service_phone=_required_nullable_string(
            dealer,
            "servicePhone",
            f"{path}.servicePhone",
        ),
        native_service_booking=_required_nullable_bool(
            dealer,
            "nativeServiceBooking",
            f"{path}.nativeServiceBooking",
        ),
        scheduling_url_mobile=_required_nullable_string(
            dealer,
            "schedulingUrlMobile",
            f"{path}.schedulingUrlMobile",
        ),
        location=location,
        languages_spoken=tuple(languages),
    )


def parse_vehicle_recalls(
    data: Mapping[str, object],
) -> tuple[VehicleRecall, ...] | None:
    """Parse the non-null standalone recall list for a nullable vehicle."""

    vehicle = _vehicle(data)
    if vehicle is None:
        return None

    path = "vehicle.recalls"
    raw_recalls = _list(_required_field(vehicle, "recalls", path), path)
    recalls: list[VehicleRecall] = []
    for index, raw_recall in enumerate(raw_recalls):
        recall_path = f"{path}[{index}]"
        recall = _typed_object(raw_recall, recall_path)
        recalls.append(
            VehicleRecall(
                effective_date=_datetime(
                    _required_field(recall, "effectiveDate", f"{recall_path}.effectiveDate"),
                    f"{recall_path}.effectiveDate",
                ),
                nhtsa_id=_required_nullable_string(
                    recall,
                    "nhtsaId",
                    f"{recall_path}.nhtsaId",
                ),
                primary_description=_required_string(
                    recall,
                    "primaryDescription",
                    f"{recall_path}.primaryDescription",
                ),
                remedy_description=_required_string(
                    recall,
                    "remedyDescription",
                    f"{recall_path}.remedyDescription",
                ),
                risk_description=_required_string(
                    recall,
                    "riskDescription",
                    f"{recall_path}.riskDescription",
                ),
                title=_required_string(recall, "title", f"{recall_path}.title"),
                type=_enum(
                    _required_field(recall, "type", f"{recall_path}.type"),
                    RecallType,
                    f"{recall_path}.type",
                ),
                recall_code=_required_nullable_string(
                    recall,
                    "recallCode",
                    f"{recall_path}.recallCode",
                ),
            )
        )
    return tuple(recalls)


def parse_vehicle_roadside_assistance(
    data: Mapping[str, object],
) -> VehicleRoadsideAssistance | None:
    """Parse nullable roadside-assistance coverage for a vehicle."""

    vehicle = _vehicle(data)
    if vehicle is None:
        return None

    path = "vehicle.roadsideAssistance"
    assistance = _required_optional_typed_object(vehicle, "roadsideAssistance", path)
    if assistance is None:
        return None
    return VehicleRoadsideAssistance(
        roadside_months=_required_nullable_int(
            assistance,
            "roadsideMonths",
            f"{path}.roadsideMonths",
        ),
        roadside_miles=_required_nullable_int(
            assistance,
            "roadsideMiles",
            f"{path}.roadsideMiles",
        ),
        towing_months=_required_nullable_int(
            assistance,
            "towingMonths",
            f"{path}.towingMonths",
        ),
        towing_miles=_required_nullable_int(
            assistance,
            "towingMiles",
            f"{path}.towingMiles",
        ),
    )


def parse_vehicle_service_history(
    data: Mapping[str, object],
) -> tuple[VehicleServiceHistoryEntry, ...] | None:
    """Parse the non-null service-history list for a nullable vehicle."""

    vehicle = _vehicle(data)
    if vehicle is None:
        return None

    path = "vehicle.serviceHistory"
    raw_entries = _list(_required_field(vehicle, "serviceHistory", path), path)
    entries: list[VehicleServiceHistoryEntry] = []
    for index, raw_entry in enumerate(raw_entries):
        entry_path = f"{path}[{index}]"
        entry = _typed_object(raw_entry, entry_path)
        entries.append(_parse_service_history_entry(entry, entry_path))
    return tuple(entries)


def parse_warranty_info(data: Mapping[str, object]) -> VehicleWarranty | None:
    """Parse nullable warranty information for a vehicle."""

    vehicle = _vehicle(data)
    if vehicle is None:
        return None

    path = "vehicle.warranty"
    warranty = _required_optional_typed_object(vehicle, "warranty", path)
    if warranty is None:
        return None

    info_path = f"{path}.warrantyInfo"
    info = _required_typed_object(warranty, "warrantyInfo", info_path)
    return VehicleWarranty(
        warranty_info=VehicleWarrantyInfo(
            color_status=_enum(
                _required_field(info, "colorStatus", f"{info_path}.colorStatus"),
                WarrantyInfoColorStatus,
                f"{info_path}.colorStatus",
            ),
            warranty_status=_enum(
                _required_field(info, "warrantyStatus", f"{info_path}.warrantyStatus"),
                WarrantyInfoWarrantyStatus,
                f"{info_path}.warrantyStatus",
            ),
            total_mileage=_required_int(
                info,
                "totalMileage",
                f"{info_path}.totalMileage",
            ),
            total_months=_required_string(
                info,
                "totalMonths",
                f"{info_path}.totalMonths",
            ),
        ),
        start_period=_parse_warranty_period(
            _required_field(warranty, "startPeriod", f"{path}.startPeriod"),
            f"{path}.startPeriod",
        ),
        end_period=_parse_warranty_period(
            _required_field(warranty, "endPeriod", f"{path}.endPeriod"),
            f"{path}.endPeriod",
        ),
        current_period=_parse_warranty_period(
            _required_field(warranty, "currentPeriod", f"{path}.currentPeriod"),
            f"{path}.currentPeriod",
        ),
    )


def _parse_preferred_dealer_address(
    value: object,
    path: str,
) -> PreferredDealerAddress | None:
    address = _optional_typed_object(value, path)
    if address is None:
        return None
    return PreferredDealerAddress(
        address1=_required_nullable_string(address, "address1", f"{path}.address1"),
        address2=_required_nullable_string(address, "address2", f"{path}.address2"),
        city=_required_nullable_string(address, "city", f"{path}.city"),
        state=_required_nullable_string(address, "state", f"{path}.state"),
        postal_code=_required_nullable_string(
            address,
            "postalCode",
            f"{path}.postalCode",
        ),
        country=_required_nullable_string(address, "country", f"{path}.country"),
    )


def _parse_preferred_dealer_location(
    value: object,
    path: str,
) -> PreferredDealerLocation | None:
    location = _optional_typed_object(value, path)
    if location is None:
        return None
    return PreferredDealerLocation(
        latitude=_required_nullable_float(location, "latitude", f"{path}.latitude"),
        longitude=_required_nullable_float(location, "longitude", f"{path}.longitude"),
    )


def _parse_service_history_entry(
    entry: Mapping[str, object],
    path: str,
) -> VehicleServiceHistoryEntry:
    mileage_path = f"{path}.mileageWithUnit"
    mileage = _required_typed_object(entry, "mileageWithUnit", mileage_path)
    operation_path = f"{path}.serviceOperation"
    operation = _required_optional_typed_object(entry, "serviceOperation", operation_path)
    raw_services = _list(
        _required_field(entry, "services", f"{path}.services"),
        f"{path}.services",
    )
    services: list[str] = []
    for index, raw_service in enumerate(raw_services):
        services.append(_string(raw_service, f"{path}.services[{index}]"))

    return VehicleServiceHistoryEntry(
        mileage=ServiceHistoryMileage(
            unit=_enum(
                _required_field(mileage, "unit", f"{mileage_path}.unit"),
                DistanceUnit,
                f"{mileage_path}.unit",
            ),
            value=_required_int(mileage, "value", f"{mileage_path}.value"),
        ),
        service_date=_datetime(
            _required_field(entry, "serviceDate", f"{path}.serviceDate"),
            f"{path}.serviceDate",
        ),
        dealer_name=_required_string(entry, "dealerName", f"{path}.dealerName"),
        dealer_code=_required_string(entry, "dealerCode", f"{path}.dealerCode"),
        services=tuple(services),
        comment=_required_nullable_string(entry, "comment", f"{path}.comment"),
        maintenance_id=_required_nullable_int(
            entry,
            "maintenanceId",
            f"{path}.maintenanceId",
        ),
        service_operation=(
            _parse_service_operation(operation, operation_path) if operation is not None else None
        ),
    )


def _parse_service_operation(
    operation: Mapping[str, object],
    path: str,
) -> VehicleServiceOperation:
    return VehicleServiceOperation(
        service_category_id=_required_nullable_string(
            operation,
            "serviceCategoryId",
            f"{path}.serviceCategoryId",
        ),
        service_category_name=_required_nullable_string(
            operation,
            "serviceCategoryName",
            f"{path}.serviceCategoryName",
        ),
        op_code_id=_required_nullable_string(
            operation,
            "opCodeID",
            f"{path}.opCodeID",
        ),
        op_code_description=_required_nullable_string(
            operation,
            "opCodeDescription",
            f"{path}.opCodeDescription",
        ),
    )


def _parse_warranty_period(value: object, path: str) -> VehicleWarrantyPeriod:
    period = _typed_object(value, path)
    return VehicleWarrantyPeriod(
        mileage=_required_int(period, "mileage", f"{path}.mileage"),
        date=_date(_required_field(period, "date", f"{path}.date"), f"{path}.date"),
    )


def _vehicle(data: Mapping[str, object]) -> Mapping[str, object] | None:
    if "vehicle" not in data:
        raise ResponseError("vehicle is missing")
    return _optional_typed_object(data.get("vehicle"), "vehicle")


def _required_field(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> object:
    if field not in container:
        raise ResponseError(f"{path} is missing")
    return container[field]


def _object(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ResponseError(f"{path} is not an object")
    return value


def _typed_object(value: object, path: str) -> Mapping[str, object]:
    result = _object(value, path)
    _required_string(result, "__typename", f"{path}.__typename")
    return result


def _optional_typed_object(value: object, path: str) -> Mapping[str, object] | None:
    if value is None:
        return None
    return _typed_object(value, path)


def _required_typed_object(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> Mapping[str, object]:
    return _typed_object(_required_field(container, field, path), path)


def _required_optional_typed_object(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> Mapping[str, object] | None:
    return _optional_typed_object(_required_field(container, field, path), path)


def _list(value: object, path: str) -> list[object]:
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


def _required_nullable_float(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> float | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    return _float(value, path)


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


def _date(value: object, path: str) -> date:
    raw_value = _string(value, path)
    try:
        return date.fromisoformat(raw_value)
    except ValueError as error:
        raise ResponseError(f"{path} is not an ISO-8601 date") from error
