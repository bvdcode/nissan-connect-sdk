from __future__ import annotations

from collections.abc import Mapping

from .exceptions import ResponseError
from .models import (
    BatteryStatus,
    BoundaryAlert,
    ClimateStatus,
    CurfewAlert,
    DoorsStatus,
    SpeedAlert,
    ValetAlert,
    VehicleStatus,
)
from .parsing import parse_vehicle_alerts, parse_vehicle_status
from .service_parsing import parse_vehicle_recalls
from .vehicle_detail_models import (
    VehicleModelYear,
    VehicleNickname,
    VehicleStatusAndRecalls,
)


def parse_vehicle_battery_status(
    data: Mapping[str, object],
    vin: str,
) -> BatteryStatus | None:
    """Parse the nullable battery fragment from VehicleBatteryStatus."""

    if _nullable_vehicle(data) is None:
        return None
    return parse_vehicle_status(data, vin).battery


def parse_vehicle_boundary_alerts(
    data: Mapping[str, object],
) -> tuple[BoundaryAlert | None, ...] | None:
    """Parse the nullable boundary-alert collection."""

    alerts = parse_vehicle_alerts(data)
    return alerts.boundary_alerts if alerts is not None else None


def parse_vehicle_climate_status(
    data: Mapping[str, object],
    vin: str,
) -> ClimateStatus | None:
    """Parse the nullable climate fragment from VehicleClimateStatus."""

    if _nullable_vehicle(data) is None:
        return None
    return parse_vehicle_status(data, vin).climate


def parse_vehicle_curfew_alerts(
    data: Mapping[str, object],
) -> tuple[CurfewAlert | None, ...] | None:
    """Parse the nullable curfew-alert collection."""

    alerts = parse_vehicle_alerts(data)
    return alerts.curfew_alerts if alerts is not None else None


def parse_vehicle_doors_status(
    data: Mapping[str, object],
    vin: str,
) -> DoorsStatus | None:
    """Parse the nullable doors fragment from VehicleDoorsStatus."""

    if _nullable_vehicle(data) is None:
        return None
    return parse_vehicle_status(data, vin).doors


def parse_vehicle_model_year(data: Mapping[str, object]) -> VehicleModelYear | None:
    """Parse the required model and year for a nullable vehicle."""

    vehicle = _nullable_vehicle(data)
    if vehicle is None:
        return None
    return VehicleModelYear(
        vehicle_type=_required_string(vehicle, "__typename", "vehicle.__typename"),
        model=_required_string(vehicle, "model", "vehicle.model"),
        year=_required_string(vehicle, "year", "vehicle.year"),
    )


def parse_vehicle_nickname(data: Mapping[str, object]) -> VehicleNickname | None:
    """Parse the nullable nickname for a nullable vehicle."""

    vehicle = _nullable_vehicle(data)
    if vehicle is None:
        return None
    return VehicleNickname(
        vehicle_type=_required_string(vehicle, "__typename", "vehicle.__typename"),
        nickname=_required_nullable_string(vehicle, "nickname", "vehicle.nickname"),
    )


def parse_vehicle_speed_alerts(
    data: Mapping[str, object],
) -> tuple[SpeedAlert | None, ...] | None:
    """Parse the nullable speed-alert collection."""

    alerts = parse_vehicle_alerts(data)
    return alerts.speed_alerts if alerts is not None else None


def parse_vehicle_core_status(
    data: Mapping[str, object],
    vin: str,
) -> VehicleStatus | None:
    """Parse the nullable non-EV dynamic VehicleStatus response."""

    if _nullable_vehicle(data) is None:
        return None
    return parse_vehicle_status(data, vin)


def parse_vehicle_status_and_recalls(
    data: Mapping[str, object],
    vin: str,
) -> VehicleStatusAndRecalls | None:
    """Parse cached dynamic status and the non-null recall list."""

    if _nullable_vehicle(data) is None:
        return None
    recalls = parse_vehicle_recalls(data)
    if recalls is None:
        raise ResponseError("vehicle.recalls is missing")
    return VehicleStatusAndRecalls(
        status=parse_vehicle_status(data, vin),
        recalls=recalls,
    )


def parse_vehicle_valet_alert(data: Mapping[str, object]) -> ValetAlert | None:
    """Parse the nullable valet-alert object."""

    alerts = parse_vehicle_alerts(data)
    return alerts.valet_alert if alerts is not None else None


def _nullable_vehicle(data: Mapping[str, object]) -> Mapping[str, object] | None:
    if "vehicle" not in data:
        raise ResponseError("vehicle is missing")
    value = data.get("vehicle")
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ResponseError("vehicle is not an object")
    return value


def _required_string(
    value: Mapping[str, object],
    field: str,
    path: str,
) -> str:
    raw = value.get(field)
    if not isinstance(raw, str):
        raise ResponseError(f"{path} is not a string")
    return raw


def _required_nullable_string(
    value: Mapping[str, object],
    field: str,
    path: str,
) -> str | None:
    raw = value.get(field)
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise ResponseError(f"{path} is not a string")
    return raw
