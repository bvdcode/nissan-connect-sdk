from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PlugAndChargeStatusInput(StrEnum):
    """Requested Plug & Charge enrollment state."""

    ENABLE = "ENABLE"
    DISABLE = "DISABLE"
    UNKNOWN_VALUE = "UNKNOWN__"


class PlugAndChargeServiceState(StrEnum):
    """Plug & Charge service state reported by Nissan Energy."""

    PENDING = "PENDING"
    ENABLING = "ENABLING"
    ENABLED = "ENABLED"
    DISABLING = "DISABLING"
    DISABLED = "DISABLED"
    UNKNOWN_VALUE = "UNKNOWN__"


class PublicChargeSessionState(StrEnum):
    """Status of a Nissan Energy public charging session."""

    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PENDING = "PENDING"
    RESERVATION = "RESERVATION"
    UNKNOWN_VALUE = "UNKNOWN__"


class PlugAndChargeUpdateOutcome(StrEnum):
    """High-level outcome derived from an enrollment update response."""

    SUCCESS = "SUCCESS"
    PENDING = "PENDING"
    FAILED = "FAILED"
    DISABLE_ERROR = "DISABLE_ERROR"
    UNKNOWN = "UNKNOWN"


class PublicChargeSessionStopOutcome(StrEnum):
    """Upstream service outcome mapping for public-session stop status codes."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    UNEXPECTED_ERROR = "UNEXPECTED_ERROR"
    UNKNOWN = "UNKNOWN"


class PlugAndChargeCertificateRetryOutcome(StrEnum):
    """Upstream service outcome mapping for certificate-install retry status codes."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class PlugAndChargeServiceData:
    """Nullable vehicle and enrollment fields in a Plug & Charge response."""

    vin: str | None
    state: PlugAndChargeServiceState | None


@dataclass(frozen=True, slots=True)
class PlugAndChargeServiceStatus:
    """Status envelope returned by Plug & Charge reads and updates."""

    status_code: str | None
    status_message: str | None
    timestamp: str | None
    data: PlugAndChargeServiceData | None

    def update_outcome(
        self,
        requested_status: PlugAndChargeStatusInput,
    ) -> PlugAndChargeUpdateOutcome:
        """Interpret this response relative to the requested enrollment state."""

        match requested_status:
            case PlugAndChargeStatusInput.ENABLE:
                terminal_state = PlugAndChargeServiceState.ENABLED
                transitional_state = PlugAndChargeServiceState.ENABLING
            case PlugAndChargeStatusInput.DISABLE:
                terminal_state = PlugAndChargeServiceState.DISABLED
                transitional_state = PlugAndChargeServiceState.DISABLING
            case _:
                raise ValueError("UNKNOWN_VALUE cannot be sent as a GraphQL input")

        state = self.data.state if self.data is not None else None
        if state is None and self.status_code == "2004":
            return PlugAndChargeUpdateOutcome.DISABLE_ERROR
        if state is None:
            return PlugAndChargeUpdateOutcome.UNKNOWN
        if state is terminal_state:
            return PlugAndChargeUpdateOutcome.SUCCESS
        if state is transitional_state:
            return PlugAndChargeUpdateOutcome.PENDING
        return PlugAndChargeUpdateOutcome.FAILED


@dataclass(frozen=True, slots=True)
class PublicChargeSessionStartData:
    """Nullable details returned after starting a public charging session."""

    vin: str | None
    evse_id: str | None
    status: PublicChargeSessionState | None
    message: str | None
    stop_session_allowed: bool | None


@dataclass(frozen=True, slots=True)
class PublicChargeSessionStartResult:
    """Status envelope returned by the public-session start mutation."""

    status_code: str | None
    status_message: str | None
    timestamp: str | None
    data: PublicChargeSessionStartData | None


@dataclass(frozen=True, slots=True)
class PublicChargeSessionStopResult:
    """Status envelope returned by the public-session stop mutation."""

    status_code: str | None
    status_message: str | None
    timestamp: str | None

    @property
    def outcome(self) -> PublicChargeSessionStopOutcome:
        """Return the upstream service's interpretation of the EMP status code."""

        if self.status_code == "1000":
            return PublicChargeSessionStopOutcome.SUCCESS
        if self.status_code in {"3026", "3028"}:
            return PublicChargeSessionStopOutcome.FAILED
        if self.status_code in {"3027", "3029", "4011", "4014", "5000"}:
            return PublicChargeSessionStopOutcome.UNEXPECTED_ERROR
        return PublicChargeSessionStopOutcome.UNKNOWN


@dataclass(frozen=True, slots=True)
class PublicChargeLocationCoordinates:
    """Nullable string coordinates reported for a public charging session."""

    latitude: str | None
    longitude: str | None


@dataclass(frozen=True, slots=True)
class PublicChargeSessionData:
    """Nullable details for the current Nissan Energy charging session."""

    session_uid: str | None
    status: PublicChargeSessionState | None
    message: str | None
    stop_session_allowed: bool | None
    cpo_name: str | None
    physical_reference: str | None
    location_address: str | None
    location_city: str | None
    location_state: str | None
    location_coordinates: PublicChargeLocationCoordinates | None


@dataclass(frozen=True, slots=True)
class PublicChargeSessionStatus:
    """Status envelope for the current Nissan Energy charging session."""

    status_code: str | None
    status_message: str | None
    timestamp: str | None
    data: PublicChargeSessionData | None


@dataclass(frozen=True, slots=True)
class PlugAndChargeCertificateRetryResult:
    """Nullable EMP status code returned by certificate-install retry."""

    status_code: str | None

    @property
    def outcome(self) -> PlugAndChargeCertificateRetryOutcome:
        """Return the upstream service's interpretation of certificate-retry status."""

        if self.status_code == "1000":
            return PlugAndChargeCertificateRetryOutcome.SUCCESS
        if self.status_code in {None, "", "2024", "2028", "2029", "2030", "4011", "5000"}:
            return PlugAndChargeCertificateRetryOutcome.FAILED
        return PlugAndChargeCertificateRetryOutcome.UNKNOWN
