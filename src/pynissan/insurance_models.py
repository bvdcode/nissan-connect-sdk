from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class InsuranceStatus(StrEnum):
    """Known vehicle-insurance policy states."""

    ACTIVE = "active"
    EXPIRED = "expired"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class InsuranceContact:
    """Nullable contact details published by an insurer."""

    location: str | None
    phone_number: str | None


@dataclass(frozen=True, slots=True)
class VehicleInsurer:
    """Insurer identity and required nullable-item contact list."""

    id: str
    name: str
    contacts: tuple[InsuranceContact | None, ...]


@dataclass(frozen=True, slots=True)
class VehicleInsurance:
    """Insurance policy attached to a vehicle."""

    id: str
    policy_number: str
    expiration_date: str
    status: InsuranceStatus
    insurer: VehicleInsurer


@dataclass(frozen=True, slots=True)
class VehicleInsuranceMutationSuccess:
    """Successful insurance add or update result."""

    success: bool


@dataclass(frozen=True, slots=True)
class VehicleInsuranceMutationError:
    """Insurance add or update failure."""

    message: str


@dataclass(frozen=True, slots=True)
class UnselectedInsuranceResult:
    """Future insurance union branch selected only by type name."""

    typename: str


type VehicleInsuranceMutationResult = (
    VehicleInsuranceMutationSuccess | VehicleInsuranceMutationError | UnselectedInsuranceResult
)
