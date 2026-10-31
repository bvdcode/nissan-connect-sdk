from __future__ import annotations

from dataclasses import dataclass
from typing import Final

_DOOR_LOCK_UNLOCK_SERVICE: Final = "REMOTE_DOOR_LOCK_UNLOCK"
_DOOR_LOCK_SERVICE: Final = "REMOTE_DOOR_LOCK"
_DOOR_UNLOCK_SERVICE: Final = "REMOTE_DOOR_UNLOCK"
_HORN_LIGHTS_SERVICE: Final = "REMOTE_HORN_LIGHTS"


@dataclass(frozen=True, slots=True)
class ServiceCapability:
    """A connected service advertised for a vehicle."""

    type: str
    enabled: bool
    subscribed: bool | None

    @property
    def is_available(self) -> bool:
        """Return whether the service is enabled with a confirmed subscription."""

        return self.enabled and self.subscribed is True


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

    def supports_service(self, service_type: str) -> bool:
        """Return whether the named service is enabled and subscribed."""

        return any(
            service.type == service_type and service.is_available for service in self.services
        )

    @property
    def can_lock_doors(self) -> bool:
        """Return whether either a combined or lock-only service is available."""

        return any(
            self.supports_service(service_type)
            for service_type in (_DOOR_LOCK_UNLOCK_SERVICE, _DOOR_LOCK_SERVICE)
        )

    @property
    def can_unlock_doors(self) -> bool:
        """Return whether either a combined or unlock-only service is available."""

        return any(
            self.supports_service(service_type)
            for service_type in (_DOOR_LOCK_UNLOCK_SERVICE, _DOOR_UNLOCK_SERVICE)
        )

    @property
    def can_flash_lights(self) -> bool:
        """Return whether the remote horn/lights service is available."""

        return self.supports_service(_HORN_LIGHTS_SERVICE)

    @property
    def can_flash_lights_and_horn(self) -> bool:
        """Return whether flashing the lights with the horn is available."""

        return self.can_flash_lights
