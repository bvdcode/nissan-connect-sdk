from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RequestProof:
    """Integrity values attached to protected service requests."""

    api_attestation: str
    device_status: str

    def __post_init__(self) -> None:
        if not self.api_attestation or not self.device_status:
            raise ValueError("Request proof values must not be empty")
