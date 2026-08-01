from __future__ import annotations

from collections.abc import Mapping

from .exceptions import ResponseError
from .models import ServiceCapability
from .wearable_models import VehicleCapabilitySummary, VehicleWithCapabilities


def parse_vehicles_with_capabilities(
    data: Mapping[str, object],
) -> tuple[VehicleWithCapabilities | None, ...] | None:
    """Parse the wearable client's nullable batch vehicle response."""

    if "vehicles" not in data:
        raise ResponseError("vehicles is missing")
    values = _nullable_list(data.get("vehicles"), "vehicles")
    if values is None:
        return None

    vehicles: list[VehicleWithCapabilities | None] = []
    for index, value in enumerate(values):
        if value is None:
            vehicles.append(None)
            continue
        vehicles.append(_parse_vehicle(value, f"vehicles[{index}]"))
    return tuple(vehicles)


def _parse_vehicle(value: object, path: str) -> VehicleWithCapabilities:
    vehicle = _typed_object(value, path)
    return VehicleWithCapabilities(
        vin=_string(vehicle.get("vin"), f"{path}.vin"),
        nickname=_nullable_string(vehicle.get("nickname"), f"{path}.nickname"),
        image_url=_string(vehicle.get("image"), f"{path}.image"),
        year=_string(vehicle.get("year"), f"{path}.year"),
        model=_string(vehicle.get("model"), f"{path}.model"),
        driver_type=_nullable_string(vehicle.get("driverType"), f"{path}.driverType"),
        capabilities=_parse_optional_capabilities(
            vehicle.get("capabilities"),
            f"{path}.capabilities",
        ),
    )


def _parse_optional_capabilities(
    value: object,
    path: str,
) -> VehicleCapabilitySummary | None:
    if value is None:
        return None
    capabilities = _typed_object(value, path)
    raw_services = _nullable_list(
        capabilities.get("serviceCapability"),
        f"{path}.serviceCapability",
    )
    services: tuple[ServiceCapability | None, ...] | None = None
    if raw_services is not None:
        parsed_services: list[ServiceCapability | None] = []
        for index, raw_service in enumerate(raw_services):
            if raw_service is None:
                parsed_services.append(None)
                continue
            parsed_services.append(
                _parse_service_capability(
                    raw_service,
                    f"{path}.serviceCapability[{index}]",
                )
            )
        services = tuple(parsed_services)

    return VehicleCapabilitySummary(
        telematics_program=_string(
            capabilities.get("telematicsProgram"),
            f"{path}.telematicsProgram",
        ),
        enrollment_status=_string(capabilities.get("status"), f"{path}.status"),
        services=services,
    )


def _parse_service_capability(value: object, path: str) -> ServiceCapability:
    service = _typed_object(value, path)
    return ServiceCapability(
        type=_string(service.get("type"), f"{path}.type"),
        enabled=_bool(service.get("enabled"), f"{path}.enabled"),
        subscribed=_nullable_bool(service.get("subscribed"), f"{path}.subscribed"),
    )


def _typed_object(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ResponseError(f"{path} is not an object")
    _string(value.get("__typename"), f"{path}.__typename")
    return value


def _nullable_list(value: object, path: str) -> list[object] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    return value


def _string(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise ResponseError(f"{path} is not a string")
    return value


def _nullable_string(value: object, path: str) -> str | None:
    if value is None:
        return None
    return _string(value, path)


def _bool(value: object, path: str) -> bool:
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


def _nullable_bool(value: object, path: str) -> bool | None:
    if value is None:
        return None
    return _bool(value, path)
