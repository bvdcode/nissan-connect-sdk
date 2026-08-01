from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ChargePlanAccountStatus(StrEnum):
    """Enrollment states returned by the EMP charge-plan API."""

    PENDING = "PENDING"
    FAILED = "FAILED"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    CANCELLED = "CANCELLED"
    CLOSED = "CLOSED"
    ENROLLING = "ENROLLING"
    NOT_ENROLLED = "NOT_ENROLLED"
    UNKNOWN_VALUE = "UNKNOWN__"


class ChargePlanCancellationOutcome(StrEnum):
    """Upstream service outcome mapping for charge-plan cancellation status codes."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class ChargeProductData:
    """Nullable EMP product fields available for charge-plan enrollment."""

    product_sku: str | None
    price: str | None
    description: str | None


@dataclass(frozen=True, slots=True)
class ChargeProductResult:
    """Status envelope returned by the ChargeProduct query."""

    status_code: str | None
    status_message: str | None
    timestamp: str | None
    data: ChargeProductData | None


@dataclass(frozen=True, slots=True)
class ChargePlanPricingConnector:
    """Nullable tariff fields for one charging connector."""

    connector_id: str | None
    tariff: str | None


@dataclass(frozen=True, slots=True)
class ChargePlanPricingEvse:
    """Nullable connector collection for one pricing EVSE."""

    connectors: tuple[ChargePlanPricingConnector | None, ...] | None


@dataclass(frozen=True, slots=True)
class ChargePlanPricingDetails:
    """Nullable fees and EVSE tariffs returned for a charging location."""

    parking_tariff: str | None
    flat_fee: str | None
    congestion_fee: str | None
    evses: tuple[ChargePlanPricingEvse | None, ...] | None


@dataclass(frozen=True, slots=True)
class ChargePlanEnrollmentData:
    """Nullable vehicle and account status returned after enrollment."""

    vin: str | None
    status: ChargePlanAccountStatus | None


@dataclass(frozen=True, slots=True)
class ChargePlanEnrollmentResult:
    """Status envelope returned by the charge-plan enrollment mutation."""

    status_code: str | None
    status_message: str | None
    timestamp: str | None
    data: ChargePlanEnrollmentData | None


@dataclass(frozen=True, slots=True)
class ChargePlanCancellationResult:
    """Status envelope returned by the charge-plan cancellation mutation."""

    status_code: str | None
    status_message: str | None
    timestamp: str | None

    @property
    def outcome(self) -> ChargePlanCancellationOutcome:
        """Return the upstream service's interpretation of the EMP status code."""

        if self.status_code == "1000":
            return ChargePlanCancellationOutcome.SUCCESS
        if self.status_code == "5000":
            return ChargePlanCancellationOutcome.FAILED
        return ChargePlanCancellationOutcome.UNKNOWN
