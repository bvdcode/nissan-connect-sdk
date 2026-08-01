from __future__ import annotations

from collections.abc import Awaitable, Mapping
from typing import cast

import pytest
from aiohttp import ClientSession

from pynissan import (
    AccountAddress,
    CreatePinError,
    DeleteAccountResult,
    GenerateOtpSuccess,
    MarketingPreferenceInput,
    MarketingPreferenceType,
    MobileCarrierCode,
    MobileNetworkOperator,
    NcarIcarAccountAvailable,
    NcarIcarCustomerEnrollment,
    NcarIcarVerifyOtpFailed,
    NCIMarketingPreferenceInput,
    NissanClient,
    PinOperationSuccess,
    PinValidationError,
    ReadOnlyError,
    RegisterAccountAddressInput,
    RegisterAccountDuplicateEmailError,
    RegisterAccountInput,
    RegisterAccountSuccess,
    RequestProof,
    Tokens,
    UpdateAccountInput,
    UpdateAccountSuccess,
    UpdatedAccountAddress,
    VerifyOtpFailed,
)
from pynissan.account_enrollment_parsing import (
    parse_generate_otp,
    parse_ncar_icar_customer_enrollment,
    parse_ncar_icar_generate_otp,
    parse_ncar_icar_register_account,
    parse_ncar_icar_verify_account,
    parse_ncar_icar_verify_otp,
    parse_register_account,
    parse_verify_otp,
)
from pynissan.account_inputs import (
    generate_otp_variables,
    ncar_icar_generate_otp_variables,
    ncar_icar_verify_account_variables,
    ncar_icar_verify_otp_variables,
    pin_variables,
    register_account_variables,
    update_account_variables,
    update_nci_marketing_preferences_variables,
    update_nna_marketing_preferences_variables,
    validate_nissan_id_variables,
    verify_otp_variables,
)
from pynissan.account_parsing import (
    parse_create_pin,
    parse_delete_account,
    parse_update_account,
    parse_update_pin,
)


class FakeResponse:
    def __init__(self, field: str, value: object = None) -> None:
        self.status = 200
        self._payload = {"data": {field: value}}

    async def __aenter__(self) -> FakeResponse:
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def json(self, *, content_type: object = None) -> object:
        return self._payload


class FakeApplicationTokenResponse(FakeResponse):
    def __init__(self) -> None:
        super().__init__("applicationToken")
        self._payload = {"access_token": "application-access-token"}


class FakeSession:
    def __init__(self, *responses: FakeResponse) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, object]] = []

    def post(self, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"url": url, **kwargs})
        if not self.responses:
            raise AssertionError("Unexpected HTTP request")
        return self.responses.pop(0)


def account() -> RegisterAccountInput:
    return RegisterAccountInput(
        first_name="Ada",
        last_name="Lovelace",
        email="ada@example.test",
        phone_number="+15555550100",
        password="secret",
        address=RegisterAccountAddressInput(
            address_1="1 Main St",
            city="Franklin",
            state="TN",
            postal_code="37064",
            country="US",
        ),
    )


def nna_preferences() -> MarketingPreferenceInput:
    return MarketingPreferenceInput(
        newsletter=(),
        product_offers=(),
        service_offers=(),
        scheduled_maintenance=(),
        feedback=(MarketingPreferenceType.EMAIL,),
    )


def client(session: FakeSession, *, read_only: bool) -> NissanClient:
    return NissanClient(
        cast(ClientSession, session),
        tokens=Tokens("access-token", "refresh-token", "id-token"),
        read_only=read_only,
        request_proof=RequestProof("api-attestation", "device-status"),
    )


def payloads(session: FakeSession) -> list[Mapping[str, object]]:
    values: list[Mapping[str, object]] = []
    for call in session.calls:
        value = call.get("json")
        if not isinstance(value, Mapping):
            continue
        values.append(value)
    return values


def test_account_enrollment_parsers_cover_success_error_and_nullable_results() -> None:
    assert parse_register_account(
        {
            "registerAccount": {
                "__typename": "RegisterAccountSuccessResponse",
                "userId": "user-id",
            }
        }
    ) == RegisterAccountSuccess("user-id")
    assert parse_ncar_icar_register_account(
        {
            "ncarIcarRegisterAccount": {
                "__typename": "RegisterAccountDuplicateEmailError",
                "message": "Already registered",
            }
        }
    ) == RegisterAccountDuplicateEmailError("Already registered")
    assert parse_ncar_icar_verify_account(
        {
            "ncarIcarVerifyAccount": {
                "__typename": "NCARICARAccountAvailable",
                "email": "ada@example.test",
                "phoneNumber": "+15555550100",
                "isOTPRequired": True,
            }
        }
    ) == NcarIcarAccountAvailable("ada@example.test", "+15555550100", True)

    enrollment = {
        "__typename": "NCARICARCustomerEnrollmentResponse",
        "vin": None,
        "firstName": "Ada",
        "lastName": None,
        "email": "ada@example.test",
        "phoneNumber": None,
        "address": {
            "__typename": "Address",
            "address1": "1 Main St",
            "address2": None,
            "city": "Franklin",
            "state": "TN",
            "postalCode": "37064",
            "country": "US",
        },
    }
    expected_enrollment = NcarIcarCustomerEnrollment(
        None,
        "Ada",
        None,
        "ada@example.test",
        None,
        AccountAddress("1 Main St", None, "Franklin", "TN", "37064", "US"),
    )
    assert (
        parse_ncar_icar_customer_enrollment({"ncarIcarCustomerEnrollment": enrollment})
        == expected_enrollment
    )
    assert parse_ncar_icar_verify_otp({"ncarIcarVerifyOTP": enrollment}) == expected_enrollment


def test_otp_and_pin_parsers_cover_the_selected_union_shapes() -> None:
    generated = {
        "__typename": "GenerateOTPResponse",
        "referenceId": "reference-id",
        "retryAvailable": 2,
    }
    assert parse_generate_otp({"nissanGenerateOTP": generated}) == GenerateOtpSuccess(
        "reference-id",
        2,
    )
    assert parse_ncar_icar_generate_otp({"ncarIcarGenerateOTP": generated}) == GenerateOtpSuccess(
        "reference-id", 2
    )
    assert parse_verify_otp(
        {
            "nissanVerifyOTP": {
                "__typename": "VerifyOTPFailed",
                "message": None,
                "retryAvailable": 1,
            }
        }
    ) == VerifyOtpFailed(None, 1)
    assert parse_ncar_icar_verify_otp(
        {
            "ncarIcarVerifyOTP": {
                "__typename": "NCARICARVerifyOTPFailed",
                "referenceId": "next-reference-id",
                "retryAvailable": 1,
            }
        }
    ) == NcarIcarVerifyOtpFailed("next-reference-id", 1)
    assert parse_create_pin(
        {"createPin": {"__typename": "CreatePINError", "message": "Invalid PIN"}}
    ) == CreatePinError("Invalid PIN")
    assert parse_update_pin(
        {"updatePin": {"__typename": "ResponseStatus", "success": None}}
    ) == PinOperationSuccess(None)
    assert parse_update_pin(
        {"updatePin": {"__typename": "ValidationError", "message": None}}
    ) == PinValidationError(None)


def test_update_and_delete_account_parsers_preserve_exact_output_shapes() -> None:
    assert parse_update_account(
        {
            "updateAccount": {
                "__typename": "User",
                "firstName": "Ada",
                "lastName": "Lovelace",
                "email": "ada@example.test",
                "mobileNumber": None,
                "address": {
                    "__typename": "Address",
                    "address1": "1 Main St",
                    "address2": None,
                    "city": "Franklin",
                    "state": "TN",
                    "country": "US",
                    "postalCode": "37064",
                    "district": None,
                    "streetNumber": None,
                },
                "mobileNetworkOperator": {
                    "__typename": "MobileNetworkOperator",
                    "code": "FUTURE_CARRIER",
                    "id": 7,
                    "name": "Carrier",
                },
            }
        }
    ) == UpdateAccountSuccess(
        "Ada",
        "Lovelace",
        "ada@example.test",
        None,
        UpdatedAccountAddress(
            "1 Main St",
            None,
            "Franklin",
            "TN",
            "US",
            "37064",
            None,
            None,
        ),
        MobileNetworkOperator(MobileCarrierCode.UNKNOWN_VALUE, 7, "Carrier"),
    )
    assert parse_delete_account(
        {"deleteAccount": {"__typename": "ResponseStatus", "success": True}}
    ) == DeleteAccountResult(True)


async def test_account_client_wires_every_operation() -> None:
    session = FakeSession(
        FakeApplicationTokenResponse(),
        FakeResponse("validateNissanID"),
        FakeResponse("securityQuestions"),
        FakeResponse("user"),
        FakeResponse("termsAndConditions"),
        FakeResponse("user"),
        FakeResponse("registerAccount"),
        FakeResponse("ncarIcarRegisterAccount"),
        FakeResponse("ncarIcarVerifyAccount"),
        FakeResponse("ncarIcarCustomerEnrollment"),
        FakeResponse("ncarIcarGenerateOTP"),
        FakeResponse("ncarIcarVerifyOTP"),
        FakeResponse("nissanGenerateOTP"),
        FakeResponse("nissanVerifyOTP"),
        FakeResponse("createPin"),
        FakeResponse("updatePin"),
        FakeResponse("updateAccount"),
        FakeResponse("deleteAccount"),
        FakeResponse("updateNCIAccountPreferences"),
        FakeResponse("updateAccountPreferences"),
    )
    sdk = client(session, read_only=False)
    registration = account()
    nci = NCIMarketingPreferenceInput(email=True)
    nna = nna_preferences()

    assert await sdk.async_validate_nissan_id("ada@example.test") is None
    assert await sdk.async_get_security_questions() is None
    assert await sdk.async_get_user_info() is None
    assert await sdk.async_get_terms_and_conditions() is None
    assert await sdk.async_get_marketing_preferences() is None
    assert await sdk.async_register_account(registration) is None
    assert await sdk.async_register_ncar_icar_account(registration) is None
    assert await sdk.async_verify_ncar_icar_account("guid") is None
    assert await sdk.async_get_ncar_icar_customer_enrollment("guid") is None
    assert await sdk.async_generate_ncar_icar_otp("guid", "+15555550100") is None
    assert (
        await sdk.async_verify_ncar_icar_otp(
            "guid",
            "+15555550100",
            "reference-id",
            "123456",
        )
        is None
    )
    assert await sdk.async_generate_otp("+15555550100") is None
    assert await sdk.async_verify_otp("+15555550100", "123456", "reference-id") is None
    assert await sdk.async_create_pin("question-id", "answer", "1234") is None
    assert await sdk.async_update_pin("question-id", "answer", "5678") is None
    assert await sdk.async_update_account(UpdateAccountInput(first_name="Ada")) is None
    assert await sdk.async_delete_account() is None
    assert await sdk.async_update_nci_marketing_preferences(nci) is None
    assert await sdk.async_update_nna_marketing_preferences(nna) is None

    requests = payloads(session)
    application_token_call = session.calls[0]
    assert application_token_call["data"] == {
        "client_id": "6wYMOME6Rs4kWVxS4i6b2RUsR4Ma",
        "client_secret": "fWp6esCzsq3vCY6RLf3p_CV_ukAa",
        "scope": "openid device_" + sdk.oauth_device_id,
        "grant_type": "client_credentials",
    }
    assert [request["operationName"] for request in requests] == [
        "ValidateNissanID",
        "SecurityQuestions",
        "UserInfo",
        "TermsAndConditions",
        "MarketingPreferences",
        "RegisterAccount",
        "NcarIcarRegisterAccount",
        "NcarIcarVerifyAccount",
        "NcarIcarCustomerEnrollment",
        "NcarIcarGenerateOTP",
        "NcarIcarVerifyOTP",
        "GenerateOTP",
        "VerifyOTP",
        "CreatePin",
        "UpdatePin",
        "UpdateAccount",
        "DeleteAccount",
        "UpdateNCIMarketingPreferences",
        "UpdateNNAMarketingPreferences",
    ]
    assert [request["variables"] for request in requests] == [
        validate_nissan_id_variables("ada@example.test"),
        {},
        {},
        {},
        {},
        register_account_variables(registration),
        register_account_variables(registration),
        ncar_icar_verify_account_variables("guid"),
        ncar_icar_verify_account_variables("guid"),
        ncar_icar_generate_otp_variables("guid", "+15555550100"),
        ncar_icar_verify_otp_variables(
            "guid",
            "+15555550100",
            "reference-id",
            "123456",
        ),
        generate_otp_variables("+15555550100"),
        verify_otp_variables("+15555550100", "123456", "reference-id"),
        pin_variables("question-id", "answer", "1234"),
        pin_variables("question-id", "answer", "5678"),
        update_account_variables(UpdateAccountInput(first_name="Ada")),
        {},
        update_nci_marketing_preferences_variables(nci),
        update_nna_marketing_preferences_variables(nna),
    ]


async def test_read_only_mode_blocks_every_account_mutation_before_network() -> None:
    session = FakeSession()
    sdk = client(session, read_only=True)
    registration = account()
    calls: tuple[Awaitable[object], ...] = (
        sdk.async_register_account(registration),
        sdk.async_register_ncar_icar_account(registration),
        sdk.async_verify_ncar_icar_account("guid"),
        sdk.async_get_ncar_icar_customer_enrollment("guid"),
        sdk.async_generate_ncar_icar_otp("guid", "+15555550100"),
        sdk.async_verify_ncar_icar_otp(
            "guid",
            "+15555550100",
            "reference-id",
            "123456",
        ),
        sdk.async_generate_otp("+15555550100"),
        sdk.async_verify_otp("+15555550100", "123456", "reference-id"),
        sdk.async_create_pin("question-id", "answer", "1234"),
        sdk.async_update_pin("question-id", "answer", "5678"),
        sdk.async_update_account(UpdateAccountInput(first_name="Ada")),
        sdk.async_delete_account(),
        sdk.async_update_nci_marketing_preferences(NCIMarketingPreferenceInput(email=True)),
        sdk.async_update_nna_marketing_preferences(nna_preferences()),
    )

    for call in calls:
        with pytest.raises(ReadOnlyError):
            await call

    assert session.calls == []
