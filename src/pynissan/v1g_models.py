from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class V1GAccountStatus(StrEnum):
    """Known monitored-charging account states returned by V1G."""

    FAILED = "FAILED"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ENROLLING = "ENROLLING"
    NOT_ENROLLED = "NOT_ENROLLED"
    CANCELLED = "CANCELLED"
    CLOSED = "CLOSED"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class V1GNotificationPreference:
    """Raw nullable V1G notification-category and channel values."""

    notification_category: str | None
    email_status: bool | None
    push_status: bool | None
    sms_status: bool | None


@dataclass(frozen=True, slots=True)
class V1GMonitoredChargingAccountData:
    """Raw nullable V1G account details for one VIN."""

    account_status: V1GAccountStatus | None
    notification_preferences: tuple[V1GNotificationPreference | None, ...] | None
    vin: str | None


@dataclass(frozen=True, slots=True)
class V1GMonitoredChargingAccountStatusResult:
    """Status envelope returned by the V1G account-status query."""

    status_code: str | None
    data: V1GMonitoredChargingAccountData | None

    @property
    def is_success(self) -> bool:
        """Return the upstream service's exact business-success interpretation."""

        return self.status_code == "1000"


@dataclass(frozen=True, slots=True)
class V1GTokenizedUrlData:
    """Nullable tokenized URL and VIN returned by V1G."""

    url: str | None
    vin: str | None


@dataclass(frozen=True, slots=True)
class V1GTokenizedUrlResult:
    """Nullable data wrapper returned by the tokenized-URL query."""

    data: V1GTokenizedUrlData | None


@dataclass(frozen=True, slots=True)
class V1GMonitoredChargingPlanEnrollmentData:
    """Nullable account status returned by V1G enrollment."""

    account_status: V1GAccountStatus | None


@dataclass(frozen=True, slots=True)
class V1GMonitoredChargingPlanEnrollmentResult:
    """Nullable data wrapper returned by V1G enrollment."""

    data: V1GMonitoredChargingPlanEnrollmentData | None


@dataclass(frozen=True, slots=True)
class V1GMonitoredChargingPlanCancellationResult:
    """Status code returned by V1G monitored-plan cancellation."""

    status_code: str | None

    @property
    def is_success(self) -> bool:
        """Return the upstream service's exact business-success interpretation."""

        return self.status_code == "1000"


@dataclass(frozen=True, slots=True)
class V1GNotificationPreferencesUpdateResult:
    """Status envelope and raw preferences returned by a V1G patch."""

    status_code: str | None
    status_message: str | None
    timestamp: str | None
    notification_preferences: tuple[V1GNotificationPreference | None, ...] | None

    @property
    def is_success(self) -> bool:
        """Return the upstream service's exact business-success interpretation."""

        return self.status_code == "1000"
