from __future__ import annotations

from .graphql_input import UNSET, UnsetType, optional_input_fields, serialize_enum
from .pnc_models import PlugAndChargeStatusInput


def start_charge_session_variables(
    vin: str,
    evse_id: str,
    *,
    location_id: str | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Build the public-session start input with optional location identity."""

    return {
        "config": optional_input_fields(
            vin=vin,
            evseId=evse_id,
            locationId=location_id,
        )
    }


def stop_charge_session_variables(
    vin: str,
) -> dict[str, object]:
    """Build the public-session stop input used by every upstream service call site."""

    return {"config": {"vin": vin}}


def update_pnc_service_status_variables(
    vin: str,
    status: PlugAndChargeStatusInput,
) -> dict[str, object]:
    """Build an enable or disable request for Plug & Charge enrollment."""

    return {
        "config": {
            "vin": vin,
            "pncServiceStatus": serialize_enum(status),
        }
    }


def retry_certificate_install_variables(vin: str) -> dict[str, object]:
    """Build the EMP certificate-install retry input."""

    return {"config": {"vin": vin}}
