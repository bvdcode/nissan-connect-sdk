from __future__ import annotations

from dataclasses import dataclass

from .models import ServiceCapability


@dataclass(frozen=True, slots=True)
class VehicleCapabilitySummary:
    """Watch-optimized connected-service capability subset for one vehicle."""

    telematics_program: str
    enrollment_status: str
    services: tuple[ServiceCapability | None, ...] | None


@dataclass(frozen=True, slots=True)
class VehicleWithCapabilities:
    """Static vehicle data and the capability subset returned to wearable clients."""

    vin: str
    nickname: str | None
    image_url: str
    year: str
    model: str
    driver_type: str | None
    capabilities: VehicleCapabilitySummary | None
