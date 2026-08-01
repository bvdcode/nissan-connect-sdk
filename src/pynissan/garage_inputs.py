from __future__ import annotations

from dataclasses import dataclass

from .garage_models import VehicleHologram
from .graphql_input import UNSET, UnsetType, optional_input_fields, serialize_enum


@dataclass(frozen=True, slots=True)
class NcarIcarRegisterAccountAddressInput:
    """Complete non-null address required by an NCAR/ICAR account registration."""

    address_1: str
    address_2: str
    city: str
    state: str
    postal_code: str
    country: str


@dataclass(frozen=True, slots=True)
class NcarIcarRegisterAccountInput:
    """Complete non-null account accepted by NCAR/ICAR vehicle registration."""

    first_name: str
    last_name: str
    email: str
    phone_number: str
    address: NcarIcarRegisterAccountAddressInput


def add_vehicle_variables(
    vin: str,
    terms_and_conditions_accepted: bool,
) -> dict[str, object]:
    """Serialize direct garage registration variables."""

    return {
        "vin": vin,
        "termsAndConditionsAccepted": terms_and_conditions_accepted,
    }


def delete_vehicle_variables(vin: str) -> dict[str, object]:
    """Serialize the required VIN for garage deletion."""

    return {"vin": vin}


def ncar_icar_add_vehicle_variables(
    terms_and_conditions_accepted: bool,
    guid: str,
    *,
    account: NcarIcarRegisterAccountInput | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize NCAR/ICAR registration while preserving account omission and null."""

    return optional_input_fields(
        termsAndConditionsAccepted=terms_and_conditions_accepted,
        guid=guid,
        account=_optional_ncar_icar_account(account),
    )


def pending_vehicles_variables() -> dict[str, object]:
    """Return the empty variables object used by PendingVehicles."""

    return {}


def ownership_status_variables(vin: str) -> dict[str, object]:
    """Serialize the required VIN for ownership status."""

    return {"vin": vin}


def apc_agreement_variables(vin: str) -> dict[str, object]:
    """Serialize the required VIN for APC agreement status."""

    return {"vin": vin}


def apc_document_url_variables(vin: str) -> dict[str, object]:
    """Serialize the required VIN for the APC document URL."""

    return {"vin": vin}


def create_apc_agreement_variables(vin: str, opt_in: bool) -> dict[str, object]:
    """Serialize APC agreement creation variables."""

    return {"optIn": opt_in, "vin": vin}


def update_apc_agreement_variables(vin: str, opt_in: bool) -> dict[str, object]:
    """Serialize APC agreement update variables."""

    return {"optIn": opt_in, "vin": vin}


def connected_terms_and_conditions_by_vin_variables(vin: str) -> dict[str, object]:
    """Serialize the required VIN for connected-services terms lookup."""

    return {"vin": vin}


def onboarding_features_variables(vin: str) -> dict[str, object]:
    """Serialize the required VIN for onboarding features."""

    return {"vin": vin}


def update_vehicle_variables(
    vin: str,
    *,
    license_plate: str | UnsetType | None = UNSET,
    hologram: VehicleHologram | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize vehicle metadata updates with Apollo omission semantics."""

    return optional_input_fields(
        vin=vin,
        licensePlate=license_plate,
        hologram=_optional_hologram(hologram),
    )


def update_vehicle_manual_mileage_variables(
    vin: str,
    *,
    manual_mileage: int | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize a nullable or omitted manual-mileage update."""

    return optional_input_fields(vin=vin, manualMileage=manual_mileage)


def update_vehicle_nickname_variables(vin: str, nickname: str) -> dict[str, object]:
    """Serialize the required nickname update variables."""

    return {"vin": vin, "nickname": nickname}


def upload_ownership_verification_variables(
    vin: str,
    filename: str,
    attachment: str,
    opt_in_sms: bool,
) -> dict[str, object]:
    """Serialize the complete ownership-verification upload variables."""

    return {
        "vin": vin,
        "filename": filename,
        "attachment": attachment,
        "optInSMS": opt_in_sms,
    }


def ncar_icar_register_account_address_input(
    value: NcarIcarRegisterAccountAddressInput,
) -> dict[str, object]:
    """Serialize an NCAR/ICAR account address with schema field names."""

    return {
        "address1": value.address_1,
        "address2": value.address_2,
        "city": value.city,
        "state": value.state,
        "postalCode": value.postal_code,
        "country": value.country,
    }


def ncar_icar_register_account_input(
    value: NcarIcarRegisterAccountInput,
) -> dict[str, object]:
    """Serialize the nested NCAR/ICAR account input."""

    return {
        "firstName": value.first_name,
        "lastName": value.last_name,
        "email": value.email,
        "phoneNumber": value.phone_number,
        "address": ncar_icar_register_account_address_input(value.address),
    }


def _optional_ncar_icar_account(
    value: NcarIcarRegisterAccountInput | UnsetType | None,
) -> object:
    if isinstance(value, UnsetType) or value is None:
        return value
    return ncar_icar_register_account_input(value)


def _optional_hologram(
    value: VehicleHologram | UnsetType | None,
) -> object:
    if isinstance(value, VehicleHologram):
        return serialize_enum(value)
    return value
