from __future__ import annotations

from dataclasses import dataclass

from .account_models import MarketingPreferenceType
from .common_inputs import AddressInput, address_input
from .graphql_input import UNSET, UnsetType, optional_input_fields, serialize_enum


@dataclass(frozen=True, slots=True)
class NotificationPreferenceTogglesInput:
    """Optional delivery-channel toggles accepted by NCI preferences."""

    email: bool | UnsetType | None = UNSET
    text_message: bool | UnsetType | None = UNSET
    direct_mail: bool | UnsetType | None = UNSET
    in_vehicle: bool | UnsetType | None = UNSET
    in_app: bool | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class NCIMarketingPreferenceInput:
    """Required email choice and optional NCI preference categories."""

    email: bool
    offers_promotion: NotificationPreferenceTogglesInput | UnsetType | None = UNSET
    news_events: NotificationPreferenceTogglesInput | UnsetType | None = UNSET
    product_updates: NotificationPreferenceTogglesInput | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class MarketingPreferenceInput:
    """NNA marketing channels grouped by communication category."""

    newsletter: tuple[MarketingPreferenceType, ...]
    product_offers: tuple[MarketingPreferenceType, ...]
    service_offers: tuple[MarketingPreferenceType, ...]
    scheduled_maintenance: tuple[MarketingPreferenceType, ...]
    feedback: tuple[MarketingPreferenceType, ...]
    promotion_offers: tuple[MarketingPreferenceType, ...] | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class RegisterAccountAddressInput:
    """Postal address required for direct account registration."""

    address_1: str
    city: str
    state: str
    postal_code: str
    country: str
    address_2: str | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class RegisterAccountInput:
    """Complete account-registration input accepted by Nissan."""

    first_name: str
    last_name: str
    email: str
    phone_number: str
    password: str
    address: RegisterAccountAddressInput
    second_last_name: str | UnsetType | None = UNSET
    mobile_carrier_id: int | UnsetType | None = UNSET
    marketing_preferences: MarketingPreferenceInput | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class UpdateAccountInput:
    """Nullable, independently optional account fields accepted by updates."""

    first_name: str | UnsetType | None = UNSET
    last_name: str | UnsetType | None = UNSET
    email: str | UnsetType | None = UNSET
    landline_number: str | UnsetType | None = UNSET
    mobile_number: str | UnsetType | None = UNSET
    mobile_carrier_id: int | UnsetType | None = UNSET
    address: AddressInput | UnsetType | None = UNSET


def notification_preference_toggles_input(
    value: NotificationPreferenceTogglesInput,
) -> dict[str, object]:
    """Serialize NCI notification toggles with Apollo omission semantics."""

    return optional_input_fields(
        email=value.email,
        textMessage=value.text_message,
        directMail=value.direct_mail,
        inVehicle=value.in_vehicle,
        inApp=value.in_app,
    )


def nci_marketing_preference_input(value: NCIMarketingPreferenceInput) -> dict[str, object]:
    """Serialize an NCI marketing-preference input."""

    return optional_input_fields(
        email=value.email,
        offersPromotion=_optional_notification_toggles(value.offers_promotion),
        newsEvents=_optional_notification_toggles(value.news_events),
        productUpdates=_optional_notification_toggles(value.product_updates),
    )


def marketing_preference_input(value: MarketingPreferenceInput) -> dict[str, object]:
    """Serialize an NNA marketing-preference input."""

    return optional_input_fields(
        newsletter=_marketing_channels(value.newsletter),
        productOffers=_marketing_channels(value.product_offers),
        serviceOffers=_marketing_channels(value.service_offers),
        scheduledMaintenance=_marketing_channels(value.scheduled_maintenance),
        feedback=_marketing_channels(value.feedback),
        promotionOffers=_optional_marketing_channels(value.promotion_offers),
    )


def register_account_address_input(value: RegisterAccountAddressInput) -> dict[str, object]:
    """Serialize the required registration address."""

    return optional_input_fields(
        address1=value.address_1,
        address2=value.address_2,
        city=value.city,
        state=value.state,
        postalCode=value.postal_code,
        country=value.country,
    )


def register_account_input(value: RegisterAccountInput) -> dict[str, object]:
    """Serialize the direct account-registration input."""

    return optional_input_fields(
        firstName=value.first_name,
        lastName=value.last_name,
        secondLastName=value.second_last_name,
        email=value.email,
        phoneNumber=value.phone_number,
        mobileCarrierId=value.mobile_carrier_id,
        password=value.password,
        address=register_account_address_input(value.address),
        marketingPreferences=_optional_marketing_preference(value.marketing_preferences),
    )


def update_account_input(value: UpdateAccountInput) -> dict[str, object]:
    """Serialize independently optional account fields."""

    return optional_input_fields(
        firstName=value.first_name,
        lastName=value.last_name,
        email=value.email,
        landlineNumber=value.landline_number,
        mobileNumber=value.mobile_number,
        mobileCarrierId=value.mobile_carrier_id,
        address=_optional_address(value.address),
    )


def validate_nissan_id_variables(nissan_id: str) -> dict[str, object]:
    """Serialize a Nissan ID validation request."""

    return {"nissanId": nissan_id}


def register_account_variables(config: RegisterAccountInput) -> dict[str, object]:
    """Serialize account-registration variables."""

    return {"config": register_account_input(config)}


def ncar_icar_verify_account_variables(guid: str) -> dict[str, object]:
    """Serialize an NCAR/ICAR enrollment identifier."""

    return {"guid": guid}


def ncar_icar_generate_otp_variables(guid: str, phone_number: str) -> dict[str, object]:
    """Serialize NCAR/ICAR OTP generation variables."""

    return {"guid": guid, "phoneNumber": phone_number}


def ncar_icar_verify_otp_variables(
    guid: str,
    phone_number: str,
    reference_id: str,
    otp: str,
) -> dict[str, object]:
    """Serialize NCAR/ICAR OTP verification variables."""

    return {
        "guid": guid,
        "phoneNumber": phone_number,
        "referenceId": reference_id,
        "otp": otp,
    }


def generate_otp_variables(phone_number: str) -> dict[str, object]:
    """Serialize direct OTP generation variables."""

    return {"phoneNumber": phone_number}


def verify_otp_variables(phone_number: str, otp: str, reference_id: str) -> dict[str, object]:
    """Serialize direct OTP verification variables."""

    return {"phoneNumber": phone_number, "otp": otp, "referenceId": reference_id}


def pin_variables(question_id: str, answer: str, new_pin: str) -> dict[str, object]:
    """Serialize PIN creation or update variables."""

    return {"questionId": question_id, "answer": answer, "newPin": new_pin}


def update_account_variables(
    config: UpdateAccountInput | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize an optional nullable account update input."""

    if isinstance(config, UpdateAccountInput):
        serialized: object = update_account_input(config)
    else:
        serialized = config
    return optional_input_fields(config=serialized)


def update_nci_marketing_preferences_variables(
    marketing_preferences: NCIMarketingPreferenceInput,
) -> dict[str, object]:
    """Serialize required NCI marketing preferences."""

    return {"marketingPreferences": nci_marketing_preference_input(marketing_preferences)}


def update_nna_marketing_preferences_variables(
    marketing_preferences: MarketingPreferenceInput | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize optional nullable NNA marketing preferences."""

    if isinstance(marketing_preferences, MarketingPreferenceInput):
        serialized: object = marketing_preference_input(marketing_preferences)
    else:
        serialized = marketing_preferences
    return optional_input_fields(marketingPreferences=serialized)


def _marketing_channels(
    values: tuple[MarketingPreferenceType, ...],
) -> list[str]:
    return [serialize_enum(value) for value in values]


def _optional_marketing_channels(
    values: tuple[MarketingPreferenceType, ...] | UnsetType | None,
) -> object:
    if isinstance(values, tuple):
        return _marketing_channels(values)
    return values


def _optional_notification_toggles(
    value: NotificationPreferenceTogglesInput | UnsetType | None,
) -> object:
    if isinstance(value, NotificationPreferenceTogglesInput):
        return notification_preference_toggles_input(value)
    return value


def _optional_marketing_preference(
    value: MarketingPreferenceInput | UnsetType | None,
) -> object:
    if isinstance(value, MarketingPreferenceInput):
        return marketing_preference_input(value)
    return value


def _optional_address(value: AddressInput | UnsetType | None) -> object:
    if isinstance(value, AddressInput):
        return address_input(value)
    return value
