from __future__ import annotations

from collections.abc import Mapping

from .exceptions import ResponseError
from .pnc_models import (
    PlugAndChargeCertificateRetryResult,
    PlugAndChargeServiceData,
    PlugAndChargeServiceState,
    PlugAndChargeServiceStatus,
    PublicChargeLocationCoordinates,
    PublicChargeSessionData,
    PublicChargeSessionStartData,
    PublicChargeSessionStartResult,
    PublicChargeSessionState,
    PublicChargeSessionStatus,
    PublicChargeSessionStopResult,
)


def parse_pnc_service_status(
    data: Mapping[str, object],
) -> PlugAndChargeServiceStatus | None:
    """Parse the nullable Plug & Charge service-status response."""

    return _parse_pnc_service_status(data, "pncServiceStatus")


def parse_update_pnc_service_status(
    data: Mapping[str, object],
) -> PlugAndChargeServiceStatus | None:
    """Parse the nullable Plug & Charge enrollment-update response."""

    return _parse_pnc_service_status(data, "updatePnCServiceStatus")


def parse_start_charge_session(
    data: Mapping[str, object],
) -> PublicChargeSessionStartResult | None:
    """Parse the nullable public-session start response."""

    root_field = "startChargeSession"
    root = _required_optional_object(data, root_field, root_field)
    if root is None:
        return None
    _typename(root, root_field)
    raw_details = _required_optional_object(root, "data", f"{root_field}.data")
    details = None
    if raw_details is not None:
        path = f"{root_field}.data"
        _typename(raw_details, path)
        details = PublicChargeSessionStartData(
            vin=_nullable_string(raw_details.get("vin"), f"{path}.vin"),
            evse_id=_nullable_string(raw_details.get("evseId"), f"{path}.evseId"),
            status=_nullable_session_state(raw_details.get("status"), f"{path}.status"),
            message=_nullable_string(raw_details.get("message"), f"{path}.message"),
            stop_session_allowed=_nullable_bool(
                raw_details.get("stopSessionAllowed"),
                f"{path}.stopSessionAllowed",
            ),
        )
    return PublicChargeSessionStartResult(
        status_code=_nullable_string(root.get("statusCode"), f"{root_field}.statusCode"),
        status_message=_nullable_string(
            root.get("statusMessage"),
            f"{root_field}.statusMessage",
        ),
        timestamp=_nullable_string(root.get("timestamp"), f"{root_field}.timestamp"),
        data=details,
    )


def parse_stop_charge_session(
    data: Mapping[str, object],
) -> PublicChargeSessionStopResult | None:
    """Parse the nullable public-session stop response."""

    root_field = "stopChargeSession"
    root = _required_optional_object(data, root_field, root_field)
    if root is None:
        return None
    _typename(root, root_field)
    return PublicChargeSessionStopResult(
        status_code=_nullable_string(root.get("statusCode"), f"{root_field}.statusCode"),
        status_message=_nullable_string(
            root.get("statusMessage"),
            f"{root_field}.statusMessage",
        ),
        timestamp=_nullable_string(root.get("timestamp"), f"{root_field}.timestamp"),
    )


def parse_charge_session_status(
    data: Mapping[str, object],
) -> PublicChargeSessionStatus | None:
    """Parse the nullable current public charging-session response."""

    root_field = "sessionStatus"
    root = _required_optional_object(data, root_field, root_field)
    if root is None:
        return None
    _typename(root, root_field)
    raw_details = _required_optional_object(root, "data", f"{root_field}.data")
    details = None
    if raw_details is not None:
        path = f"{root_field}.data"
        _typename(raw_details, path)
        raw_coordinates = _required_optional_object(
            raw_details,
            "locationCoordinates",
            f"{path}.locationCoordinates",
        )
        coordinates = None
        if raw_coordinates is not None:
            coordinates_path = f"{path}.locationCoordinates"
            _typename(raw_coordinates, coordinates_path)
            coordinates = PublicChargeLocationCoordinates(
                latitude=_nullable_string(
                    raw_coordinates.get("latitude"),
                    f"{coordinates_path}.latitude",
                ),
                longitude=_nullable_string(
                    raw_coordinates.get("longitude"),
                    f"{coordinates_path}.longitude",
                ),
            )
        details = PublicChargeSessionData(
            session_uid=_nullable_string(
                raw_details.get("sessionUid"),
                f"{path}.sessionUid",
            ),
            status=_nullable_session_state(raw_details.get("status"), f"{path}.status"),
            message=_nullable_string(raw_details.get("message"), f"{path}.message"),
            stop_session_allowed=_nullable_bool(
                raw_details.get("stopSessionAllowed"),
                f"{path}.stopSessionAllowed",
            ),
            cpo_name=_nullable_string(raw_details.get("cpoName"), f"{path}.cpoName"),
            physical_reference=_nullable_string(
                raw_details.get("physicalReference"),
                f"{path}.physicalReference",
            ),
            location_address=_nullable_string(
                raw_details.get("locationAddress"),
                f"{path}.locationAddress",
            ),
            location_city=_nullable_string(
                raw_details.get("locationCity"),
                f"{path}.locationCity",
            ),
            location_state=_nullable_string(
                raw_details.get("locationState"),
                f"{path}.locationState",
            ),
            location_coordinates=coordinates,
        )
    return PublicChargeSessionStatus(
        status_code=_nullable_string(root.get("statusCode"), f"{root_field}.statusCode"),
        status_message=_nullable_string(
            root.get("statusMessage"),
            f"{root_field}.statusMessage",
        ),
        timestamp=_nullable_string(root.get("timestamp"), f"{root_field}.timestamp"),
        data=details,
    )


def parse_retry_certificate_install(
    data: Mapping[str, object],
) -> PlugAndChargeCertificateRetryResult | None:
    """Parse the nullable certificate-install retry result."""

    root_field = "retryCertInstall"
    root = _required_optional_object(data, root_field, root_field)
    if root is None:
        return None
    _typename(root, root_field)
    return PlugAndChargeCertificateRetryResult(
        status_code=_nullable_string(root.get("statusCode"), f"{root_field}.statusCode")
    )


def _parse_pnc_service_status(
    data: Mapping[str, object],
    root_field: str,
) -> PlugAndChargeServiceStatus | None:
    root = _required_optional_object(data, root_field, root_field)
    if root is None:
        return None
    _typename(root, root_field)
    raw_details = _required_optional_object(root, "data", f"{root_field}.data")
    details = None
    if raw_details is not None:
        path = f"{root_field}.data"
        _typename(raw_details, path)
        details = PlugAndChargeServiceData(
            vin=_nullable_string(raw_details.get("vin"), f"{path}.vin"),
            state=_nullable_service_state(
                raw_details.get("pncServiceStatus"),
                f"{path}.pncServiceStatus",
            ),
        )
    return PlugAndChargeServiceStatus(
        status_code=_nullable_string(root.get("statusCode"), f"{root_field}.statusCode"),
        status_message=_nullable_string(
            root.get("statusMessage"),
            f"{root_field}.statusMessage",
        ),
        timestamp=_nullable_string(root.get("timestamp"), f"{root_field}.timestamp"),
        data=details,
    )


def _required_optional_object(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> Mapping[str, object] | None:
    if field not in container:
        raise ResponseError(f"{path} is missing")
    value = container.get(field)
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ResponseError(f"{path} is not an object")
    return value


def _typename(value: Mapping[str, object], path: str) -> None:
    _string(value.get("__typename"), f"{path}.__typename")


def _string(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise ResponseError(f"{path} is not a string")
    return value


def _nullable_string(value: object, path: str) -> str | None:
    if value is None:
        return None
    return _string(value, path)


def _nullable_bool(value: object, path: str) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value


def _nullable_service_state(
    value: object,
    path: str,
) -> PlugAndChargeServiceState | None:
    raw_value = _nullable_string(value, path)
    if raw_value is None:
        return None
    try:
        return PlugAndChargeServiceState(raw_value)
    except ValueError:
        return PlugAndChargeServiceState.UNKNOWN_VALUE


def _nullable_session_state(
    value: object,
    path: str,
) -> PublicChargeSessionState | None:
    raw_value = _nullable_string(value, path)
    if raw_value is None:
        return None
    try:
        return PublicChargeSessionState(raw_value)
    except ValueError:
        return PublicChargeSessionState.UNKNOWN_VALUE
