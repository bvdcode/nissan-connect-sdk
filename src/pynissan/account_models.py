from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class MarketingPreferenceType(StrEnum):
    """Known NNA marketing delivery channels."""

    EMAIL = "EMAIL"
    MAIL = "MAIL"
    SMS = "SMS"
    TELEPHONE = "TELEPHONE"
    IVM = "IVM"
    IAM = "IAM"
    UNKNOWN_VALUE = "UNKNOWN__"


class MobileCarrierCode(StrEnum):
    """Known mobile carrier codes returned by Nissan account APIs."""

    US_ECIT = "US_ECIT"
    US_BOOSTU = "US_BOOSTU"
    US_CELLULA = "US_CELLULA"
    US_CNSMRCL = "US_CNSMRCL"
    US_ALLTEL = "US_ALLTEL"
    US_APPALAC = "US_APPALAC"
    US_ATT = "US_ATT"
    US_BLUEGRA = "US_BLUEGRA"
    US_BOOST = "US_BOOST"
    US_CELLCOM = "US_CELLCOM"
    US_CELLSOU = "US_CELLSOU"
    US_CENTENN = "US_CENTENN"
    US_CINBELL = "US_CINBELL"
    US_CRICKET = "US_CRICKET"
    US_DOBSON = "US_DOBSON"
    US_IMMIX = "US_IMMIX"
    US_METROPC = "US_METROPC"
    US_MIDWEST = "US_MIDWEST"
    US_NEXTEL = "US_NEXTEL"
    US_NTELOS = "US_NTELOS"
    US_REVOL = "US_REVOL"
    US_SPRINT = "US_SPRINT"
    US_TMOBILE = "US_TMOBILE"
    US_VERIZON = "US_VERIZON"
    US_VIRGIN = "US_VIRGIN"
    US_GCI = "US_GCI"
    US_GOOGLE = "US_GOOGLE"
    CA_ALIANT = "CA_ALIANT"
    CA_VIRGIN = "CA_VIRGIN"
    CA_VIDEOTR = "CA_VIDEOTR"
    CA_KOODO = "CA_KOODO"
    CA_WIND = "CA_WIND"
    CA_BELL = "CA_BELL"
    CA_MTS = "CA_MTS"
    CA_PRIMUS = "CA_PRIMUS"
    CA_TELUS = "CA_TELUS"
    CA_FREEDOM = "CA_FREEDOM"
    CA_FIDO = "CA_FIDO"
    CA_PUBLIC = "CA_PUBLIC"
    CA_ROGERS = "CA_ROGERS"
    CA_EASTLINK = "CA_EASTLINK"
    CA_SASKTEL = "CA_SASKTEL"
    CA_OTHER = "CA_OTHER"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class NissanIdExists:
    """Validation result for a Nissan ID that already exists."""

    nissan_id: str


@dataclass(frozen=True, slots=True)
class NissanIdDoesNotExist:
    """Validation result for a Nissan ID that is available."""

    nissan_id: str


@dataclass(frozen=True, slots=True)
class NissanIdRequiresOwnerPortalPasswordReset:
    """Validation result requiring an owner-portal password reset."""

    nissan_id: str
    link: str


@dataclass(frozen=True, slots=True)
class NissanIdRequiresOwnerPortalProfileCompletion:
    """Validation result requiring owner-portal profile completion."""

    nissan_id: str
    link: str


@dataclass(frozen=True, slots=True)
class NissanIdRequiresNmacPasswordReset:
    """Validation result requiring an NMAC password reset."""

    nissan_id: str
    link: str


@dataclass(frozen=True, slots=True)
class UnselectedAccountResult:
    """Union result for which the operation selected only its typename."""

    typename: str


type NissanIdValidationResult = (
    NissanIdExists
    | NissanIdDoesNotExist
    | NissanIdRequiresOwnerPortalPasswordReset
    | NissanIdRequiresOwnerPortalProfileCompletion
    | NissanIdRequiresNmacPasswordReset
    | UnselectedAccountResult
)


@dataclass(frozen=True, slots=True)
class SecurityQuestion:
    """One account security question."""

    id: str | None
    question: str | None


@dataclass(frozen=True, slots=True)
class UserInfo:
    """Security and account-kind flags for the signed-in user."""

    pin_configured: bool | None
    security_question_id: str | None
    is_lite_account: bool | None


@dataclass(frozen=True, slots=True)
class MarketingNotificationPreferences:
    """Nullable NCI delivery-channel preferences for one category."""

    email: bool | None
    text_message: bool | None
    direct_mail: bool | None
    in_app: bool | None
    in_vehicle: bool | None


@dataclass(frozen=True, slots=True)
class NCIMarketingPreferences:
    """NCI account preferences."""

    email: bool | None
    product_updates: MarketingNotificationPreferences | None
    news_events: MarketingNotificationPreferences | None
    offers_promotion: MarketingNotificationPreferences | None


@dataclass(frozen=True, slots=True)
class NNAMarketingPreferences:
    """NNA account preferences."""

    newsletter: tuple[MarketingPreferenceType | None, ...] | None
    product_offers: tuple[MarketingPreferenceType | None, ...] | None
    service_offers: tuple[MarketingPreferenceType | None, ...] | None
    scheduled_maintenance: tuple[MarketingPreferenceType | None, ...] | None
    feedback: tuple[MarketingPreferenceType | None, ...] | None


type MarketingPreferencesResult = (
    NCIMarketingPreferences | NNAMarketingPreferences | UnselectedAccountResult
)


@dataclass(frozen=True, slots=True)
class RegisterAccountSuccess:
    """Successful account registration."""

    user_id: str


@dataclass(frozen=True, slots=True)
class AccountMessageResult:
    """Base for account union branches that contain a message."""

    message: str


@dataclass(frozen=True, slots=True)
class RegisterAccountFirstNameError(AccountMessageResult):
    """Registration failure caused by the first name."""


@dataclass(frozen=True, slots=True)
class RegisterAccountLastNameError(AccountMessageResult):
    """Registration failure caused by the last name."""


@dataclass(frozen=True, slots=True)
class RegisterAccountEmailError(AccountMessageResult):
    """Registration failure caused by the email address."""


@dataclass(frozen=True, slots=True)
class RegisterAccountAddressError(AccountMessageResult):
    """Registration failure caused by the street address."""


@dataclass(frozen=True, slots=True)
class RegisterAccountCityError(AccountMessageResult):
    """Registration failure caused by the city."""


@dataclass(frozen=True, slots=True)
class RegisterAccountStateError(AccountMessageResult):
    """Registration failure caused by the state or province."""


@dataclass(frozen=True, slots=True)
class RegisterAccountPostalCodeError(AccountMessageResult):
    """Registration failure caused by the postal code."""


@dataclass(frozen=True, slots=True)
class RegisterAccountPhoneError(AccountMessageResult):
    """Registration failure caused by the phone number."""


@dataclass(frozen=True, slots=True)
class RegisterAccountPasswordError(AccountMessageResult):
    """Registration failure caused by the password."""


@dataclass(frozen=True, slots=True)
class RegisterAccountDuplicateEmailError(AccountMessageResult):
    """Registration failure for an email already in use."""


@dataclass(frozen=True, slots=True)
class RegisterAccountGeneralError(AccountMessageResult):
    """General account-registration failure."""


type RegisterAccountResult = (
    RegisterAccountSuccess
    | RegisterAccountFirstNameError
    | RegisterAccountLastNameError
    | RegisterAccountEmailError
    | RegisterAccountAddressError
    | RegisterAccountCityError
    | RegisterAccountStateError
    | RegisterAccountPostalCodeError
    | RegisterAccountPhoneError
    | RegisterAccountPasswordError
    | RegisterAccountDuplicateEmailError
    | RegisterAccountGeneralError
    | UnselectedAccountResult
)


@dataclass(frozen=True, slots=True)
class NcarIcarAccountAvailable:
    """NCAR/ICAR account that can continue enrollment."""

    email: str
    phone_number: str
    is_otp_required: bool


@dataclass(frozen=True, slots=True)
class NcarIcarAccountUnavailable:
    """NCAR/ICAR account that cannot continue enrollment."""

    email: str
    vin: str


@dataclass(frozen=True, slots=True)
class NcarIcarCustomerEnrollmentExpiredError(AccountMessageResult):
    """Enrollment failure caused by an expired NCAR/ICAR link."""


@dataclass(frozen=True, slots=True)
class NcarIcarCustomerEnrollmentGeneralError(AccountMessageResult):
    """General NCAR/ICAR enrollment failure."""


@dataclass(frozen=True, slots=True)
class AccountGeneralError(AccountMessageResult):
    """General account operation failure."""


type NcarIcarVerifyAccountResult = (
    NcarIcarAccountAvailable
    | NcarIcarAccountUnavailable
    | NcarIcarCustomerEnrollmentExpiredError
    | NcarIcarCustomerEnrollmentGeneralError
    | AccountGeneralError
    | UnselectedAccountResult
)


@dataclass(frozen=True, slots=True)
class AccountAddress:
    """Nullable postal fields returned by account operations."""

    address_1: str | None
    address_2: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    country: str | None


@dataclass(frozen=True, slots=True)
class NcarIcarCustomerEnrollment:
    """Nullable customer details recovered from an NCAR/ICAR enrollment."""

    vin: str | None
    first_name: str | None
    last_name: str | None
    email: str | None
    phone_number: str | None
    address: AccountAddress | None


type NcarIcarCustomerEnrollmentResult = (
    NcarIcarCustomerEnrollment
    | NcarIcarCustomerEnrollmentExpiredError
    | NcarIcarCustomerEnrollmentGeneralError
    | AccountGeneralError
    | UnselectedAccountResult
)


@dataclass(frozen=True, slots=True)
class GenerateOtpSuccess:
    """Successful one-time password generation."""

    reference_id: str
    retry_available: int


@dataclass(frozen=True, slots=True)
class NcarIcarGuidDeactivated(AccountMessageResult):
    """NCAR/ICAR OTP failure caused by a deactivated identifier."""


@dataclass(frozen=True, slots=True)
class NcarIcarGenerateOtpExhausted(AccountMessageResult):
    """NCAR/ICAR OTP generation failure after all retries."""


type GenerateOtpResult = GenerateOtpSuccess | UnselectedAccountResult
type NcarIcarGenerateOtpResult = (
    GenerateOtpSuccess
    | NcarIcarGuidDeactivated
    | NcarIcarGenerateOtpExhausted
    | UnselectedAccountResult
)


@dataclass(frozen=True, slots=True)
class VerifyOtpSuccess:
    """Successful direct OTP verification."""

    message: str | None


@dataclass(frozen=True, slots=True)
class VerifyOtpFailed:
    """Failed direct OTP verification with nullable retry information."""

    message: str | None
    retry_available: int | None


@dataclass(frozen=True, slots=True)
class VerifyOtpRetryExhausted:
    """Direct OTP verification failure after all retries."""

    message: str | None


type VerifyOtpResult = (
    VerifyOtpSuccess | VerifyOtpFailed | VerifyOtpRetryExhausted | UnselectedAccountResult
)


@dataclass(frozen=True, slots=True)
class NcarIcarVerifyOtpFailed:
    """Failed NCAR/ICAR OTP verification with its next reference."""

    reference_id: str
    retry_available: int


@dataclass(frozen=True, slots=True)
class NcarIcarVerifyOtpRetryExhausted(AccountMessageResult):
    """NCAR/ICAR OTP verification failure after all retries."""


type NcarIcarVerifyOtpResult = (
    NcarIcarCustomerEnrollment
    | NcarIcarCustomerEnrollmentExpiredError
    | NcarIcarCustomerEnrollmentGeneralError
    | NcarIcarVerifyOtpFailed
    | NcarIcarVerifyOtpRetryExhausted
    | NcarIcarGuidDeactivated
    | UnselectedAccountResult
)


@dataclass(frozen=True, slots=True)
class PinOperationSuccess:
    """Nullable success flag returned by PIN operations."""

    success: bool | None


@dataclass(frozen=True, slots=True)
class CreatePinError(AccountMessageResult):
    """PIN creation failure."""


@dataclass(frozen=True, slots=True)
class PinValidationError:
    """PIN update validation failure."""

    message: str | None


type CreatePinResult = PinOperationSuccess | CreatePinError | UnselectedAccountResult
type UpdatePinResult = PinOperationSuccess | PinValidationError | UnselectedAccountResult


@dataclass(frozen=True, slots=True)
class MobileNetworkOperator:
    """Mobile carrier attached to an updated account."""

    code: MobileCarrierCode
    id: int
    name: str


@dataclass(frozen=True, slots=True)
class UpdatedAccountAddress:
    """Nullable address fields returned after an account update."""

    address_1: str | None
    address_2: str | None
    city: str | None
    state: str | None
    country: str | None
    postal_code: str | None
    district: str | None
    street_number: str | None


@dataclass(frozen=True, slots=True)
class UpdateAccountSuccess:
    """Account profile returned after a successful update."""

    first_name: str
    last_name: str
    email: str
    mobile_number: str | None
    address: UpdatedAccountAddress | None
    mobile_network_operator: MobileNetworkOperator | None


@dataclass(frozen=True, slots=True)
class UpdateAccountFirstNameError(AccountMessageResult):
    """Account update failure caused by the first name."""


@dataclass(frozen=True, slots=True)
class UpdateAccountLastNameError(AccountMessageResult):
    """Account update failure caused by the last name."""


@dataclass(frozen=True, slots=True)
class UpdateAccountAddressError(AccountMessageResult):
    """Account update failure caused by the address."""


@dataclass(frozen=True, slots=True)
class UpdateAccountPostalCodeError(AccountMessageResult):
    """Account update failure caused by the postal code."""


@dataclass(frozen=True, slots=True)
class UpdateAccountMobileNumberError(AccountMessageResult):
    """Account update failure caused by the mobile number."""


@dataclass(frozen=True, slots=True)
class UpdateAccountLandlineNumberError(AccountMessageResult):
    """Account update failure caused by the landline number."""


@dataclass(frozen=True, slots=True)
class UpdateAccountGeneralError(AccountMessageResult):
    """General account-update failure."""


type UpdateAccountResult = (
    UpdateAccountSuccess
    | UpdateAccountFirstNameError
    | UpdateAccountLastNameError
    | UpdateAccountAddressError
    | UpdateAccountPostalCodeError
    | UpdateAccountMobileNumberError
    | UpdateAccountLandlineNumberError
    | UpdateAccountGeneralError
    | UnselectedAccountResult
)


@dataclass(frozen=True, slots=True)
class DeleteAccountResult:
    """Nullable success flag returned by account deletion."""

    success: bool | None
