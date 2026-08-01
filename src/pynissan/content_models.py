from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from .account_models import MobileCarrierCode


class ClientType(StrEnum):
    """Known client types accepted by contact links."""

    IOS = "IOS"
    ANDROID = "ANDROID"
    OTHER = "OTHER"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class ContactLinks:
    """Nullable account, ownership, assistance, and informational links."""

    privacy_policy: str | None
    data_privacy: str | None
    collision_repair: str | None
    accident_helper: str | None
    check_owners_portal: str | None
    warranty: str | None
    forgot_password: str | None
    edit_contact_information_and_change_password: str | None
    parts_and_accessories: str | None
    ifs_account: str | None
    ncesi_insurance: str | None
    roadside_aid: str | None
    buy_protection: str | None
    nissan_added_security_plan_video: str | None
    nissan_certified_pre_owned_video: str | None
    nissan_prepaid_maintenance_plan_video: str | None
    second_delivery_marketing_video: str | None
    disconnect_remote_access: str | None
    delete_account: str | None
    aries_app: str | None


@dataclass(frozen=True, slots=True)
class ContactPhoneNumbers:
    """Nullable support phone numbers published by Nissan."""

    customer_care: str | None
    stolen_vehicle_locator: str | None
    stolen_vehicle_info: str | None
    personal_assistant: str | None
    roadside_assistant: str | None
    ownership_verification: str | None
    reset_voice_pin: str | None
    second_delivery_customer_support: str | None
    plug_and_charge_support: str | None
    nissan_store: str | None


@dataclass(frozen=True, slots=True)
class ContactEmailAddresses:
    """Nullable support email addresses published by Nissan."""

    second_delivery_customer_support: str | None


@dataclass(frozen=True, slots=True)
class ContactUsInfo:
    """Contact links, phone numbers, and email addresses."""

    links: ContactLinks | None
    phone_numbers: ContactPhoneNumbers | None
    email_addresses: ContactEmailAddresses | None


@dataclass(frozen=True, slots=True)
class CertifiedPreOwnedProvider:
    """Nullable certified-pre-owned brand and preferred provider."""

    brand_name: str | None
    preferred_provider: str | None


@dataclass(frozen=True, slots=True)
class CertifiedPreOwnedDetails:
    """Certified-pre-owned service response."""

    status_code: str | None
    status_message: str | None
    timestamp: str | None
    data: tuple[CertifiedPreOwnedProvider | None, ...] | None


@dataclass(frozen=True, slots=True)
class FrequentlyAskedQuestion:
    """A required question and answer."""

    question: str
    answer: str


@dataclass(frozen=True, slots=True)
class FrequentlyAskedQuestionCategory:
    """FAQ category and its required entries."""

    category: str
    entries: tuple[FrequentlyAskedQuestion, ...]


@dataclass(frozen=True, slots=True)
class LiveChatHours:
    """Nullable availability window for one support department."""

    department_name: str | None
    opening_time: datetime | None
    closing_time: datetime | None
    after_hour_message: str | None
    available_now: bool | None


@dataclass(frozen=True, slots=True)
class MobileCarrier:
    """Mobile carrier accepted by account registration and updates."""

    id: int
    code: MobileCarrierCode
    name: str
