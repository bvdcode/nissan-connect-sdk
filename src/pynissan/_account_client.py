from __future__ import annotations

from . import operations
from ._client_base import _NissanClientBase
from .account_enrollment_parsing import (
    parse_generate_otp,
    parse_ncar_icar_customer_enrollment,
    parse_ncar_icar_generate_otp,
    parse_ncar_icar_register_account,
    parse_ncar_icar_verify_account,
    parse_ncar_icar_verify_otp,
    parse_register_account,
    parse_verify_otp,
)
from .account_inputs import (
    MarketingPreferenceInput,
    NCIMarketingPreferenceInput,
    RegisterAccountInput,
    UpdateAccountInput,
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
from .account_models import (
    CreatePinResult,
    DeleteAccountResult,
    GenerateOtpResult,
    MarketingPreferencesResult,
    NcarIcarCustomerEnrollmentResult,
    NcarIcarGenerateOtpResult,
    NcarIcarVerifyAccountResult,
    NcarIcarVerifyOtpResult,
    NissanIdValidationResult,
    RegisterAccountResult,
    SecurityQuestion,
    UpdateAccountResult,
    UpdatePinResult,
    UserInfo,
    VerifyOtpResult,
)
from .account_parsing import (
    parse_create_pin,
    parse_delete_account,
    parse_marketing_preferences,
    parse_security_questions,
    parse_terms_and_conditions,
    parse_update_account,
    parse_update_nci_marketing_preferences,
    parse_update_nna_marketing_preferences,
    parse_update_pin,
    parse_user_info,
    parse_validate_nissan_id,
)
from .graphql_input import UNSET, UnsetType


class _AccountClientMixin(_NissanClientBase):
    async def async_validate_nissan_id(
        self,
        nissan_id: str,
    ) -> NissanIdValidationResult | None:
        """Return the account state associated with a Nissan ID."""

        data = await self._transport.async_application_graphql(
            "ValidateNissanID",
            operations.VALIDATE_NISSAN_ID,
            validate_nissan_id_variables(nissan_id),
        )
        return parse_validate_nissan_id(data)

    async def async_get_security_questions(
        self,
    ) -> tuple[SecurityQuestion | None, ...] | None:
        """Return the account security-question catalog."""

        data = await self._transport.async_graphql(
            "SecurityQuestions",
            operations.SECURITY_QUESTIONS,
            {},
        )
        return parse_security_questions(data)

    async def async_get_user_info(self) -> UserInfo | None:
        """Return the signed-in user's PIN and account-kind flags."""

        data = await self._transport.async_graphql(
            "UserInfo",
            operations.USER_INFO,
            {},
        )
        return parse_user_info(data)

    async def async_get_terms_and_conditions(self) -> str | None:
        """Return the nullable account terms content."""

        data = await self._transport.async_graphql(
            "TermsAndConditions",
            operations.TERMS_AND_CONDITIONS,
            {},
        )
        return parse_terms_and_conditions(data)

    async def async_get_marketing_preferences(
        self,
    ) -> MarketingPreferencesResult | None:
        """Return country-specific marketing preferences."""

        data = await self._transport.async_graphql(
            "MarketingPreferences",
            operations.MARKETING_PREFERENCES,
            {},
        )
        return parse_marketing_preferences(data)

    async def async_register_account(
        self,
        config: RegisterAccountInput,
    ) -> RegisterAccountResult | None:
        """Register a MyNISSAN account."""

        self._ensure_write_allowed()
        data = await self._transport.async_application_graphql(
            "RegisterAccount",
            operations.REGISTER_ACCOUNT,
            register_account_variables(config),
        )
        return parse_register_account(data)

    async def async_register_ncar_icar_account(
        self,
        config: RegisterAccountInput,
    ) -> RegisterAccountResult | None:
        """Register an account through the NCAR/ICAR flow."""

        self._ensure_write_allowed()
        data = await self._transport.async_application_graphql(
            "NcarIcarRegisterAccount",
            operations.NCAR_ICAR_REGISTER_ACCOUNT,
            register_account_variables(config),
        )
        return parse_ncar_icar_register_account(data)

    async def async_verify_ncar_icar_account(
        self,
        guid: str,
    ) -> NcarIcarVerifyAccountResult | None:
        """Check account availability for an NCAR/ICAR enrollment."""

        self._ensure_write_allowed()
        data = await self._transport.async_application_graphql(
            "NcarIcarVerifyAccount",
            operations.NCAR_ICAR_VERIFY_ACCOUNT,
            ncar_icar_verify_account_variables(guid),
        )
        return parse_ncar_icar_verify_account(data)

    async def async_get_ncar_icar_customer_enrollment(
        self,
        guid: str,
    ) -> NcarIcarCustomerEnrollmentResult | None:
        """Recover customer details from an NCAR/ICAR enrollment link."""

        self._ensure_write_allowed()
        data = await self._transport.async_application_graphql(
            "NcarIcarCustomerEnrollment",
            operations.NCAR_ICAR_CUSTOMER_ENROLLMENT,
            ncar_icar_verify_account_variables(guid),
        )
        return parse_ncar_icar_customer_enrollment(data)

    async def async_generate_ncar_icar_otp(
        self,
        guid: str,
        phone_number: str,
    ) -> NcarIcarGenerateOtpResult | None:
        """Generate a one-time password for NCAR/ICAR enrollment."""

        self._ensure_write_allowed()
        data = await self._transport.async_application_graphql(
            "NcarIcarGenerateOTP",
            operations.NCAR_ICAR_GENERATE_OTP,
            ncar_icar_generate_otp_variables(guid, phone_number),
        )
        return parse_ncar_icar_generate_otp(data)

    async def async_verify_ncar_icar_otp(
        self,
        guid: str,
        phone_number: str,
        reference_id: str,
        otp: str,
    ) -> NcarIcarVerifyOtpResult | None:
        """Verify an NCAR/ICAR enrollment one-time password."""

        self._ensure_write_allowed()
        data = await self._transport.async_application_graphql(
            "NcarIcarVerifyOTP",
            operations.NCAR_ICAR_VERIFY_OTP,
            ncar_icar_verify_otp_variables(guid, phone_number, reference_id, otp),
        )
        return parse_ncar_icar_verify_otp(data)

    async def async_generate_otp(self, phone_number: str) -> GenerateOtpResult | None:
        """Generate a one-time password for direct account verification."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "GenerateOTP",
            operations.GENERATE_OTP,
            generate_otp_variables(phone_number),
        )
        return parse_generate_otp(data)

    async def async_verify_otp(
        self,
        phone_number: str,
        otp: str,
        reference_id: str,
    ) -> VerifyOtpResult | None:
        """Verify a direct account one-time password."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "VerifyOTP",
            operations.VERIFY_OTP,
            verify_otp_variables(phone_number, otp, reference_id),
        )
        return parse_verify_otp(data)

    async def async_create_pin(
        self,
        question_id: str,
        answer: str,
        new_pin: str,
    ) -> CreatePinResult | None:
        """Create the account PIN and security answer."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CreatePin",
            operations.CREATE_PIN,
            pin_variables(question_id, answer, new_pin),
        )
        return parse_create_pin(data)

    async def async_update_pin(
        self,
        question_id: str,
        answer: str,
        new_pin: str,
    ) -> UpdatePinResult | None:
        """Replace the account PIN and security answer."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdatePin",
            operations.UPDATE_PIN,
            pin_variables(question_id, answer, new_pin),
        )
        return parse_update_pin(data)

    async def async_update_account(
        self,
        config: UpdateAccountInput | UnsetType | None = UNSET,
    ) -> UpdateAccountResult | None:
        """Update independently optional account profile fields."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateAccount",
            operations.UPDATE_ACCOUNT,
            update_account_variables(config),
        )
        return parse_update_account(data)

    async def async_delete_account(self) -> DeleteAccountResult | None:
        """Permanently delete the signed-in MyNISSAN account."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "DeleteAccount",
            operations.DELETE_ACCOUNT,
            {},
        )
        return parse_delete_account(data)

    async def async_update_nci_marketing_preferences(
        self,
        marketing_preferences: NCIMarketingPreferenceInput,
    ) -> MarketingPreferencesResult | None:
        """Replace NCI account preferences."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateNCIMarketingPreferences",
            operations.UPDATE_NCI_MARKETING_PREFERENCES,
            update_nci_marketing_preferences_variables(marketing_preferences),
        )
        return parse_update_nci_marketing_preferences(data)

    async def async_update_nna_marketing_preferences(
        self,
        marketing_preferences: MarketingPreferenceInput | UnsetType | None = UNSET,
    ) -> MarketingPreferencesResult | None:
        """Replace NNA account preferences."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpdateNNAMarketingPreferences",
            operations.UPDATE_NNA_MARKETING_PREFERENCES,
            update_nna_marketing_preferences_variables(marketing_preferences),
        )
        return parse_update_nna_marketing_preferences(data)
