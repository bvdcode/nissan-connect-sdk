from __future__ import annotations

from dataclasses import dataclass

from .models import VehicleStatus
from .service_models import VehicleRecall


@dataclass(frozen=True, slots=True)
class VehicleModelYear:
    """Required model and year returned for a nullable vehicle."""

    vehicle_type: str
    model: str
    year: str


@dataclass(frozen=True, slots=True)
class VehicleNickname:
    """Nullable nickname returned for a nullable vehicle."""

    vehicle_type: str
    nickname: str | None


@dataclass(frozen=True, slots=True)
class VehicleStatusAndRecalls:
    """Cached non-EV dynamic status together with vehicle recalls."""

    status: VehicleStatus
    recalls: tuple[VehicleRecall, ...]
