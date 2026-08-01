from __future__ import annotations

from collections.abc import Mapping

from ._parsing_values import (
    _object,
    _optional_bool,
    _optional_int,
    _optional_list,
    _optional_object,
    _optional_str,
    _required_bool,
    _required_float,
    _required_str,
)
from .models import (
    AccessoryCapability,
    HvacTemperatureCapabilities,
    SeatHeaterAccessories,
    SeatHeaterCapability,
    ServiceCapability,
    SunRoofCapability,
    VehicleAccessoriesDetails,
    VehicleCapabilities,
    WayPointCapability,
)


def parse_vehicle_capabilities(data: Mapping[str, object], vin: str) -> VehicleCapabilities:
    """Parse connected services advertised for one vehicle."""

    vehicle = _object(data.get("vehicle"), "vehicle")
    capabilities = _optional_object(vehicle.get("capabilities"), "vehicle.capabilities")
    if capabilities is None:
        return VehicleCapabilities(vin, None, None, ())
    service_values = (
        _optional_list(
            capabilities.get("serviceCapability"),
            "vehicle.capabilities.serviceCapability",
        )
        or []
    )
    services: list[ServiceCapability] = []
    for index, value in enumerate(service_values):
        item = _object(value, f"vehicle.capabilities.serviceCapability[{index}]")
        services.append(
            ServiceCapability(
                type=_required_str(item.get("type"), "serviceCapability.type"),
                enabled=_required_bool(item.get("enabled"), "serviceCapability.enabled"),
                subscribed=_optional_bool(item.get("subscribed")),
            )
        )
    return VehicleCapabilities(
        vin=vin,
        telematics_program=_optional_str(capabilities.get("telematicsProgram")),
        enrollment_status=_optional_str(capabilities.get("status")),
        services=tuple(services),
        accessories_details=_parse_vehicle_accessories_details(
            capabilities.get("accessoriesDetails")
        ),
    )


def _parse_vehicle_accessories_details(value: object) -> VehicleAccessoriesDetails | None:
    details = _optional_object(value, "vehicle.capabilities.accessoriesDetails")
    if details is None:
        return None

    seat_heater = _optional_object(
        details.get("seatHeater"),
        "vehicle.capabilities.accessoriesDetails.seatHeater",
    )
    steering_heat = _optional_object(
        details.get("steeringHeat"),
        "vehicle.capabilities.accessoriesDetails.steeringHeat",
    )
    sun_roof = _optional_object(
        details.get("sunRoof"),
        "vehicle.capabilities.accessoriesDetails.sunRoof",
    )
    window_status = _optional_object(
        details.get("windowStatus"),
        "vehicle.capabilities.accessoriesDetails.windowStatus",
    )
    way_point = _optional_object(
        details.get("wayPoint"),
        "vehicle.capabilities.accessoriesDetails.wayPoint",
    )
    hvac_temperatures = _optional_object(
        details.get("hvacTemperatures"),
        "vehicle.capabilities.accessoriesDetails.hvacTemperatures",
    )

    return VehicleAccessoriesDetails(
        seat_heater=(
            _parse_seat_heater_capability(seat_heater) if seat_heater is not None else None
        ),
        steering_heat=(
            AccessoryCapability(enabled=_optional_bool(steering_heat.get("enabled")))
            if steering_heat is not None
            else None
        ),
        sun_roof=(
            SunRoofCapability(
                type=_optional_str(sun_roof.get("type")),
                enabled=_optional_bool(sun_roof.get("enabled")),
            )
            if sun_roof is not None
            else None
        ),
        window_status=(
            AccessoryCapability(enabled=_optional_bool(window_status.get("enabled")))
            if window_status is not None
            else None
        ),
        way_point=(
            WayPointCapability(
                enabled=_optional_bool(way_point.get("enabled")),
                max_number=_optional_int(way_point.get("maxNumber")),
            )
            if way_point is not None
            else None
        ),
        hvac_temperatures=(
            HvacTemperatureCapabilities(
                unit=_required_str(hvac_temperatures.get("unit"), "hvacTemperatures.unit"),
                default=_required_float(
                    hvac_temperatures.get("default"), "hvacTemperatures.default"
                ),
                minimum=_required_float(hvac_temperatures.get("min"), "hvacTemperatures.min"),
                maximum=_required_float(hvac_temperatures.get("max"), "hvacTemperatures.max"),
                resolution=_required_float(
                    hvac_temperatures.get("resolution"), "hvacTemperatures.resolution"
                ),
            )
            if hvac_temperatures is not None
            else None
        ),
    )


def _parse_seat_heater_capability(value: Mapping[str, object]) -> SeatHeaterCapability:
    accessories = _optional_object(
        value.get("accessories"),
        "vehicle.capabilities.accessoriesDetails.seatHeater.accessories",
    )
    parsed_accessories = None
    if accessories is not None:
        parsed_accessories = SeatHeaterAccessories(
            assistant_seat=_optional_str(accessories.get("assistantSeat")),
            driver_seat=_optional_str(accessories.get("driverSeat")),
            second_centre_seat=_optional_str(accessories.get("secondCentreSeat")),
            second_left_seat=_optional_str(accessories.get("secondLeftSeat")),
            second_right_seat=_optional_str(accessories.get("secondRightSeat")),
            third_left_seat=_optional_str(accessories.get("thirdLeftSeat")),
            third_right_seat=_optional_str(accessories.get("thirdRightSeat")),
        )
    return SeatHeaterCapability(
        enabled=_optional_bool(value.get("enabled")),
        accessories=parsed_accessories,
    )
