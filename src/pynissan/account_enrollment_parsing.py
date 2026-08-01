from __future__ import annotations

from collections.abc import Mapping

from .account_models import (
    AccountAddress,
    AccountGeneralError,
    GenerateOtpResult,
    GenerateOtpSuccess,
    NcarIcarAccountAvailable,
    NcarIcarAccountUnavailable,
    NcarIcarCustomerEnrollment,
    NcarIcarCustomerEnrollmentExpiredError,
    NcarIcarCustomerEnrollmentGeneralError,
    NcarIcarCustomerEnrollmentResult,
    NcarIcarGenerateOtpExhausted,
    NcarIcarGenerateOtpResult,
    NcarIcarGuidDeactivated,
    NcarIcarVerifyAccountResult,
    NcarIcarVerifyOtpFailed,
    NcarIcarVerifyOtpResult,
    NcarIcarVerifyOtpRetryExhausted,
    RegisterAccountAddressError,
    RegisterAccountCityError,
    RegisterAccountDuplicateEmailError,
    RegisterAccountEmailError,
    RegisterAccountFirstNameError,
    RegisterAccountGeneralError,
    RegisterAccountLastNameError,
    RegisterAccountPasswordError,
    RegisterAccountPhoneError,
    RegisterAccountPostalCodeError,
    RegisterAccountResult,
    RegisterAccountStateError,
    RegisterAccountSuccess,
    UnselectedAccountResult,
    VerifyOtpFailed,
    VerifyOtpResult,
    VerifyOtpRetryExhausted,
    VerifyOtpSuccess,
)
from .account_parsing import (
    _required_int,
    _required_nullable_int,
    _required_nullable_string,
    _required_optional_typed_object,
    _required_string,
    _root,
    _typename,
)
from .exceptions import ResponseError


def parse_register_account(data: Mapping[str, object]) -> RegisterAccountResult | None:
    """Parse every generated direct account-registration branch."""

    return _parse_register_account(data, "registerAccount")


def parse_ncar_icar_register_account(
    data: Mapping[str, object],
) -> RegisterAccountResult | None:
    """Parse every generated NCAR/ICAR account-registration branch."""

    return _parse_register_account(data, "ncarIcarRegisterAccount")


def parse_ncar_icar_verify_account(
    data: Mapping[str, object],
) -> NcarIcarVerifyAccountResult | None:
    """Parse every generated NCAR/ICAR account-availability branch."""

    root_field = "ncarIcarVerifyAccount"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if typename == "NCARICARAccountAvailable":
        return NcarIcarAccountAvailable(
            email=_required_string(root, "email", f"{root_field}.email"),
            phone_number=_required_string(
                root,
                "phoneNumber",
                f"{root_field}.phoneNumber",
            ),
            is_otp_required=_required_bool(
                root,
                "isOTPRequired",
                f"{root_field}.isOTPRequired",
            ),
        )
    if typename == "NCARICARAccountUnavailable":
        return NcarIcarAccountUnavailable(
            email=_required_string(root, "email", f"{root_field}.email"),
            vin=_required_string(root, "vin", f"{root_field}.vin"),
        )
    message = _known_enrollment_error(root, root_field, typename)
    if message is not None:
        return message
    return UnselectedAccountResult(typename)


def parse_ncar_icar_customer_enrollment(
    data: Mapping[str, object],
) -> NcarIcarCustomerEnrollmentResult | None:
    """Parse customer details recovered from an NCAR/ICAR link."""

    root_field = "ncarIcarCustomerEnrollment"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if typename == "NCARICARCustomerEnrollmentResponse":
        return _parse_customer_enrollment(root, root_field)
    error = _known_enrollment_error(root, root_field, typename)
    if error is not None:
        return error
    return UnselectedAccountResult(typename)


def parse_ncar_icar_generate_otp(
    data: Mapping[str, object],
) -> NcarIcarGenerateOtpResult | None:
    """Parse every generated NCAR/ICAR OTP-generation branch."""

    root_field = "ncarIcarGenerateOTP"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if typename == "GenerateOTPResponse":
        return _parse_generate_otp_success(root, root_field)
    if typename == "NCARICARGuidDeactivated":
        return NcarIcarGuidDeactivated(_required_string(root, "message", f"{root_field}.message"))
    if typename == "NCARICARGenerateOTPExhausted":
        return NcarIcarGenerateOtpExhausted(
            _required_string(root, "message", f"{root_field}.message")
        )
    return UnselectedAccountResult(typename)


def parse_ncar_icar_verify_otp(
    data: Mapping[str, object],
) -> NcarIcarVerifyOtpResult | None:
    """Parse every generated NCAR/ICAR OTP-verification branch."""

    root_field = "ncarIcarVerifyOTP"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if typename == "NCARICARCustomerEnrollmentResponse":
        return _parse_customer_enrollment(root, root_field)
    if typename == "NCARICARCustomerEnrollmentExpiredError":
        return NcarIcarCustomerEnrollmentExpiredError(
            _required_string(root, "message", f"{root_field}.message")
        )
    if typename == "NCARICARCustomerEnrollmentGeneralError":
        return NcarIcarCustomerEnrollmentGeneralError(
            _required_string(root, "message", f"{root_field}.message")
        )
    if typename == "NCARICARVerifyOTPFailed":
        return NcarIcarVerifyOtpFailed(
            reference_id=_required_string(
                root,
                "referenceId",
                f"{root_field}.referenceId",
            ),
            retry_available=_required_int(
                root,
                "retryAvailable",
                f"{root_field}.retryAvailable",
            ),
        )
    if typename == "NCARICARVerifyOTPRetryExhausted":
        return NcarIcarVerifyOtpRetryExhausted(
            _required_string(root, "message", f"{root_field}.message")
        )
    if typename == "NCARICARGuidDeactivated":
        return NcarIcarGuidDeactivated(_required_string(root, "message", f"{root_field}.message"))
    return UnselectedAccountResult(typename)


def parse_generate_otp(data: Mapping[str, object]) -> GenerateOtpResult | None:
    """Parse the direct OTP-generation result."""

    root_field = "nissanGenerateOTP"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if typename == "GenerateOTPResponse":
        return _parse_generate_otp_success(root, root_field)
    return UnselectedAccountResult(typename)


def parse_verify_otp(data: Mapping[str, object]) -> VerifyOtpResult | None:
    """Parse every generated direct OTP-verification branch."""

    root_field = "nissanVerifyOTP"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if typename == "VerifyOTPSuccess":
        return VerifyOtpSuccess(_required_nullable_string(root, "message", f"{root_field}.message"))
    if typename == "VerifyOTPFailed":
        return VerifyOtpFailed(
            message=_required_nullable_string(root, "message", f"{root_field}.message"),
            retry_available=_required_nullable_int(
                root,
                "retryAvailable",
                f"{root_field}.retryAvailable",
            ),
        )
    if typename == "VerifyOTPRetryExhausted":
        return VerifyOtpRetryExhausted(
            _required_nullable_string(root, "message", f"{root_field}.message")
        )
    return UnselectedAccountResult(typename)


def _parse_register_account(
    data: Mapping[str, object],
    root_field: str,
) -> RegisterAccountResult | None:
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if typename == "RegisterAccountSuccessResponse":
        return RegisterAccountSuccess(_required_string(root, "userId", f"{root_field}.userId"))
    message_path = f"{root_field}.message"
    if typename == "RegisterAccountFirstNameError":
        return RegisterAccountFirstNameError(_required_string(root, "message", message_path))
    if typename == "RegisterAccountLastNameError":
        return RegisterAccountLastNameError(_required_string(root, "message", message_path))
    if typename == "RegisterAccountEmailError":
        return RegisterAccountEmailError(_required_string(root, "message", message_path))
    if typename == "RegisterAccountAddressError":
        return RegisterAccountAddressError(_required_string(root, "message", message_path))
    if typename == "RegisterAccountCityError":
        return RegisterAccountCityError(_required_string(root, "message", message_path))
    if typename == "RegisterAccountStateError":
        return RegisterAccountStateError(_required_string(root, "message", message_path))
    if typename == "RegisterAccountPostalCodeError":
        return RegisterAccountPostalCodeError(_required_string(root, "message", message_path))
    if typename == "RegisterAccountPhoneError":
        return RegisterAccountPhoneError(_required_string(root, "message", message_path))
    if typename == "RegisterAccountPasswordError":
        return RegisterAccountPasswordError(_required_string(root, "message", message_path))
    if typename == "RegisterAccountDuplicateEmailError":
        return RegisterAccountDuplicateEmailError(_required_string(root, "message", message_path))
    if typename == "RegisterGeneralError":
        return RegisterAccountGeneralError(_required_string(root, "message", message_path))
    return UnselectedAccountResult(typename)


def _known_enrollment_error(
    root: Mapping[str, object],
    root_field: str,
    typename: str,
) -> (
    NcarIcarCustomerEnrollmentExpiredError
    | NcarIcarCustomerEnrollmentGeneralError
    | AccountGeneralError
    | None
):
    message = f"{root_field}.message"
    if typename == "NCARICARCustomerEnrollmentExpiredError":
        return NcarIcarCustomerEnrollmentExpiredError(_required_string(root, "message", message))
    if typename == "NCARICARCustomerEnrollmentGeneralError":
        return NcarIcarCustomerEnrollmentGeneralError(_required_string(root, "message", message))
    if typename == "GeneralError":
        return AccountGeneralError(_required_string(root, "message", message))
    return None


def _parse_customer_enrollment(
    root: Mapping[str, object],
    root_field: str,
) -> NcarIcarCustomerEnrollment:
    address_path = f"{root_field}.address"
    address = _required_optional_typed_object(root, "address", address_path)
    return NcarIcarCustomerEnrollment(
        vin=_required_nullable_string(root, "vin", f"{root_field}.vin"),
        first_name=_required_nullable_string(
            root,
            "firstName",
            f"{root_field}.firstName",
        ),
        last_name=_required_nullable_string(root, "lastName", f"{root_field}.lastName"),
        email=_required_nullable_string(root, "email", f"{root_field}.email"),
        phone_number=_required_nullable_string(
            root,
            "phoneNumber",
            f"{root_field}.phoneNumber",
        ),
        address=_parse_customer_address(address, address_path),
    )


def _parse_customer_address(
    value: Mapping[str, object] | None,
    path: str,
) -> AccountAddress | None:
    if value is None:
        return None
    return AccountAddress(
        address_1=_required_nullable_string(value, "address1", f"{path}.address1"),
        address_2=_required_nullable_string(value, "address2", f"{path}.address2"),
        city=_required_nullable_string(value, "city", f"{path}.city"),
        state=_required_nullable_string(value, "state", f"{path}.state"),
        postal_code=_required_nullable_string(value, "postalCode", f"{path}.postalCode"),
        country=_required_nullable_string(value, "country", f"{path}.country"),
    )


def _parse_generate_otp_success(
    root: Mapping[str, object],
    root_field: str,
) -> GenerateOtpSuccess:
    return GenerateOtpSuccess(
        reference_id=_required_string(root, "referenceId", f"{root_field}.referenceId"),
        retry_available=_required_int(
            root,
            "retryAvailable",
            f"{root_field}.retryAvailable",
        ),
    )


def _required_bool(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> bool:
    value = container.get(field)
    if field not in container:
        raise ResponseError(f"{path} is missing")
    if not isinstance(value, bool):
        raise ResponseError(f"{path} is not a boolean")
    return value
