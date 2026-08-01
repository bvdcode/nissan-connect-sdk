from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ServiceCapability:
    """A connected service advertised for a vehicle."""

    type: str
    enabled: bool
    subscribed: bool | None


@dataclass(frozen=True, slots=True)
class AccessoryCapability:
    """Whether a vehicle accessory is available."""

    enabled: bool | None


@dataclass(frozen=True, slots=True)
class SeatHeaterAccessories:
    """Heating or heating-and-cooling support by seat position."""

    assistant_seat: str | None
    driver_seat: str | None
    second_centre_seat: str | None
    second_left_seat: str | None
    second_right_seat: str | None
    third_left_seat: str | None
    third_right_seat: str | None


@dataclass(frozen=True, slots=True)
class SeatHeaterCapability:
    """Seat climate accessory support advertised by the vehicle."""

    enabled: bool | None
    accessories: SeatHeaterAccessories | None


@dataclass(frozen=True, slots=True)
class SunRoofCapability:
    """Sun roof type and availability advertised by the vehicle."""

    type: str | None
    enabled: bool | None


@dataclass(frozen=True, slots=True)
class WayPointCapability:
    """Waypoint support and the maximum number accepted by the vehicle."""

    enabled: bool | None
    max_number: int | None


@dataclass(frozen=True, slots=True)
class HvacTemperatureCapabilities:
    """Supported HVAC temperature range in the requested unit."""

    unit: str
    default: float
    minimum: float
    maximum: float
    resolution: float


@dataclass(frozen=True, slots=True)
class VehicleAccessoriesDetails:
    """Accessory capabilities advertised for a vehicle."""

    seat_heater: SeatHeaterCapability | None
    steering_heat: AccessoryCapability | None
    sun_roof: SunRoofCapability | None
    window_status: AccessoryCapability | None
    way_point: WayPointCapability | None
    hvac_temperatures: HvacTemperatureCapabilities | None


@dataclass(frozen=True, slots=True)
class VehicleCapabilities:
    """Connected service capabilities for a vehicle."""

    vin: str
    telematics_program: str | None
    enrollment_status: str | None
    services: tuple[ServiceCapability, ...]
    accessories_details: VehicleAccessoriesDetails | None = None
