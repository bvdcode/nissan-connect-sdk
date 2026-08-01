from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Final

from .charge_plan_models import ChargePlanAccountStatus

EnergyAccountStatus = ChargePlanAccountStatus

ACCOUNT_STATUS_POLL_INTERVAL_SECONDS: Final = 2.0
ACCOUNT_STATUS_POLL_TIMEOUT_SECONDS: Final = 210.0


class EnergyAccountStatusReason(StrEnum):
    """Reasons reported for a Nissan Energy account state."""

    DECLINED_PAYMENT = "DECLINED_PAYMENT"
    SVT = "SVT"
    INVALID_PAYMENT = "INVALID_PAYMENT"
    NA = "NA"
    UNKNOWN_VALUE = "UNKNOWN__"


class EnergyPncStatus(StrEnum):
    """Certificate state reported for Plug & Charge enrollment."""

    PENDING = "PENDING"
    INSTALLING = "INSTALLING"
    READY = "READY"
    FAILED = "FAILED"
    NA = "NA"
    RENEWING = "RENEWING"
    UNKNOWN_VALUE = "UNKNOWN__"


class EnergyToggleStatus(StrEnum):
    """Toggle transition state reported by the Nissan Energy account API."""

    ENABLING = "ENABLING"
    ENABLED = "ENABLED"
    DISABLING = "DISABLING"
    DISABLED = "DISABLED"
    PENDING = "PENDING"
    NA = "NA"
    UNKNOWN_VALUE = "UNKNOWN__"


class EnergyNacsStatus(StrEnum):
    """North American Charging Standard status for an energy account."""

    ACTIVE = "ACTIVE"
    IN_ACTIVE = "IN_ACTIVE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN_VALUE = "UNKNOWN__"


class EnergyAccountPollingOutcome(StrEnum):
    """Upstream service control-flow outcome for one AccountStatus response."""

    RETRY = "RETRY"
    COMPLETE = "COMPLETE"


@dataclass(frozen=True, slots=True)
class EnergyAccountConnector:
    """Nullable identity fields for one account charging connector."""

    id: str | None
    connector_name: str | None


@dataclass(frozen=True, slots=True)
class EnergyAccountData:
    """Nullable Nissan Energy enrollment and connector details."""

    status: EnergyAccountStatus | None
    status_reason: EnergyAccountStatusReason | None
    pnc_status: EnergyPncStatus | None
    pnc_status_reason: str | None
    toggle_status: EnergyToggleStatus | None
    nacs_status: EnergyNacsStatus | None
    connectors: tuple[EnergyAccountConnector | None, ...] | None


@dataclass(frozen=True, slots=True)
class EnergyAccountStatusResult:
    """Status envelope returned by the AccountStatus query."""

    status_code: str | None
    status_message: str | None
    timestamp: str | None
    data: EnergyAccountData | None


def account_status_polling_outcome(
    result: EnergyAccountStatusResult | None,
) -> EnergyAccountPollingOutcome:
    """Return whether the upstream service would repeat or finish account-status polling."""

    if result is None or result.data is None:
        return EnergyAccountPollingOutcome.RETRY
    if result.data.status is None or result.data.status is EnergyAccountStatus.ENROLLING:
        return EnergyAccountPollingOutcome.RETRY
    return EnergyAccountPollingOutcome.COMPLETE
