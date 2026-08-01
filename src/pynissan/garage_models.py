from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AgreementStatus(StrEnum):
    """Known agreement states returned by the APC API."""

    ACTIVATED = "ACTIVATED"
    DEACTIVATED = "DEACTIVATED"
    NO_STATUS = "NO_STATUS"
    UNKNOWN_VALUE = "UNKNOWN__"


class VehicleHologram(StrEnum):
    """Vehicle holograms accepted and returned by garage updates."""

    SINGLE_ZERO = "SINGLE_ZERO"
    DOUBLE_ZERO = "DOUBLE_ZERO"
    ONE = "ONE"
    TWO = "TWO"
    E = "E"
    UNKNOWN_VALUE = "UNKNOWN__"


class OnboardingFeatureImageType(StrEnum):
    """Known artwork categories returned for vehicle onboarding features."""

    INFO = "INFO"
    TELEMATICS = "TELEMATICS"
    NECN = "NECN"
    V1G = "V1G"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class AddVehicleSuccess:
    """Successful garage registration result."""

    vin: str


@dataclass(frozen=True, slots=True)
class RegisterGeneralError:
    """General registration failure returned by garage operations."""

    message: str


@dataclass(frozen=True, slots=True)
class RequireOwnershipVerification:
    """Registration result that requires ownership verification."""

    message: str


@dataclass(frozen=True, slots=True)
class RegisterCorporateVehicleEmailSentToPrimaryOwnerError:
    """Corporate registration result awaiting the primary owner's email action."""

    message: str


@dataclass(frozen=True, slots=True)
class RegisterCorporateVehiclePrimaryOwnerConsentIsPendingError:
    """Corporate registration result awaiting the primary owner's consent."""

    message: str


@dataclass(frozen=True, slots=True)
class VINAlreadyExistsInAnotherGarageError:
    """Registration failure for a VIN already assigned to another garage."""

    message: str


@dataclass(frozen=True, slots=True)
class UnselectedGarageResult:
    """Union result for which the operation selected only its GraphQL typename."""

    typename: str


type AddVehicleResult = (
    AddVehicleSuccess
    | RegisterGeneralError
    | RequireOwnershipVerification
    | RegisterCorporateVehicleEmailSentToPrimaryOwnerError
    | RegisterCorporateVehiclePrimaryOwnerConsentIsPendingError
    | VINAlreadyExistsInAnotherGarageError
    | UnselectedGarageResult
)

type NcarIcarAddVehicleResult = (
    AddVehicleSuccess | RegisterGeneralError | RequireOwnershipVerification | UnselectedGarageResult
)


@dataclass(frozen=True, slots=True)
class DeleteVehicleSuccess:
    """Successful garage deletion result."""

    vin: str


@dataclass(frozen=True, slots=True)
class DeleteVehicleError:
    """Garage deletion failure returned by Nissan."""

    message: str


type DeleteVehicleResult = DeleteVehicleSuccess | DeleteVehicleError | UnselectedGarageResult


@dataclass(frozen=True, slots=True)
class PendingVehicle:
    """Vehicle whose ownership-verification case is still pending."""

    vin: str
    case_status: str | None
    model: str | None
    case_id: str | None
    case_number: str | None
    year: str | None


@dataclass(frozen=True, slots=True)
class OwnershipStatus:
    """Nullable signed-in ownership state for an AVK2 vehicle."""

    is_signed_in: bool | None


@dataclass(frozen=True, slots=True)
class APCAgreement:
    """Nullable APC enrollment state for a vehicle."""

    opt_in: AgreementStatus | None


@dataclass(frozen=True, slots=True)
class APCDocument:
    """Nullable APC agreement document URL."""

    document_url: str | None


@dataclass(frozen=True, slots=True)
class APCAgreementMutationResult:
    """Nullable success flag returned by APC create and update mutations."""

    success: bool | None


@dataclass(frozen=True, slots=True)
class TermsAndConditionsResponse:
    """Nullable connected-services terms content for a VIN."""

    title: str | None
    body: str | None
    url: str | None


@dataclass(frozen=True, slots=True)
class InvalidVINError:
    """Operation failure caused by an invalid VIN."""

    message: str


@dataclass(frozen=True, slots=True)
class NonConnectedVehicleResponse:
    """Terms lookup result for a vehicle without connected services."""

    message: str


@dataclass(frozen=True, slots=True)
class ValidVINResponse:
    """Terms lookup result indicating a valid VIN without returned terms."""

    message: str


type ConnectedTermsAndConditionsResult = (
    TermsAndConditionsResponse
    | InvalidVINError
    | NonConnectedVehicleResponse
    | ValidVINResponse
    | UnselectedGarageResult
)


@dataclass(frozen=True, slots=True)
class OnboardingFeature:
    """One nullable-field onboarding feature returned for a vehicle."""

    position: int | None
    title: str | None
    body: str | None
    image_type: OnboardingFeatureImageType | None


@dataclass(frozen=True, slots=True)
class UpdateVehicleSuccess:
    """Successful license-plate or hologram update."""

    license_plate: str | None
    hologram: VehicleHologram | None


@dataclass(frozen=True, slots=True)
class UpdateVehicleInvalidLicensePlateError:
    """Vehicle update failure caused by an invalid license plate."""

    message: str


@dataclass(frozen=True, slots=True)
class UpdateVehicleHologramInvalidLengthError:
    """Vehicle update failure caused by an invalid hologram length."""

    message: str


@dataclass(frozen=True, slots=True)
class VINNotFoundError:
    """Vehicle update failure for a VIN absent from the account."""

    message: str


@dataclass(frozen=True, slots=True)
class UpdateVehicleGeneralError:
    """General vehicle update failure returned by Nissan."""

    message: str


type UpdateVehicleResult = (
    UpdateVehicleSuccess
    | UpdateVehicleInvalidLicensePlateError
    | UpdateVehicleHologramInvalidLengthError
    | InvalidVINError
    | VINNotFoundError
    | UpdateVehicleGeneralError
    | UnselectedGarageResult
)


@dataclass(frozen=True, slots=True)
class UpdateVehicleManualMileageSuccess:
    """Successful manual-mileage update with Nissan's string response scalar."""

    manual_mileage: str | None


@dataclass(frozen=True, slots=True)
class UpdateVehicleInvalidMileageError:
    """Vehicle update failure caused by an invalid manual mileage."""

    message: str


type UpdateVehicleManualMileageResult = (
    UpdateVehicleManualMileageSuccess
    | UpdateVehicleInvalidMileageError
    | InvalidVINError
    | VINNotFoundError
    | UpdateVehicleGeneralError
    | UnselectedGarageResult
)


@dataclass(frozen=True, slots=True)
class UpdateVehicleNicknameSuccess:
    """Successful nickname update."""

    nickname: str


@dataclass(frozen=True, slots=True)
class UpdateVehicleNicknameMalformedError:
    """Vehicle update failure caused by a malformed nickname."""

    message: str


type UpdateVehicleNicknameResult = (
    UpdateVehicleNicknameSuccess
    | UpdateVehicleNicknameMalformedError
    | InvalidVINError
    | VINNotFoundError
    | UpdateVehicleGeneralError
    | UnselectedGarageResult
)


@dataclass(frozen=True, slots=True)
class UploadOwnershipVerificationSuccess:
    """Successful ownership-verification upload."""

    case_number: str


type UploadOwnershipVerificationResult = (
    UploadOwnershipVerificationSuccess | RegisterGeneralError | UnselectedGarageResult
)
