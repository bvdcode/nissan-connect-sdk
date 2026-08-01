from __future__ import annotations

from dataclasses import dataclass

from .graphql_input import UNSET, UnsetType, optional_input_fields


@dataclass(frozen=True, slots=True)
class VehicleInsuranceInput:
    """Insurance details accepted by the add and update mutations."""

    vin: str
    insurer_id: str
    policy_number: str
    expiry_date: str
    custom_insurance_name: str | UnsetType | None = UNSET
    custom_insurance_phone_number: str | UnsetType | None = UNSET


def vehicle_insurance_variables(config: VehicleInsuranceInput) -> dict[str, object]:
    """Serialize a complete vehicle-insurance mutation input."""

    return {
        "input": optional_input_fields(
            vin=config.vin,
            insurerId=config.insurer_id,
            policyNumber=config.policy_number,
            expiryDate=config.expiry_date,
            customInsuranceName=config.custom_insurance_name,
            customInsurancePhoneNumber=config.custom_insurance_phone_number,
        )
    }
