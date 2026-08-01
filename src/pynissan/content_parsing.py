from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from .account_models import MobileCarrierCode
from .account_parsing import (
    _required_enum,
    _required_field,
    _required_int,
    _required_nullable_bool,
    _required_nullable_string,
    _required_optional_typed_object,
    _required_string,
    _typed_object,
)
from .content_models import (
    CertifiedPreOwnedDetails,
    CertifiedPreOwnedProvider,
    ContactEmailAddresses,
    ContactLinks,
    ContactPhoneNumbers,
    ContactUsInfo,
    FrequentlyAskedQuestion,
    FrequentlyAskedQuestionCategory,
    LiveChatHours,
    MobileCarrier,
)
from .exceptions import ResponseError


def parse_contact_us(data: Mapping[str, object]) -> ContactUsInfo:
    """Parse account and support contact information."""

    contact = _required_typed_object(data, "contactUs", "contactUs")
    links = _required_optional_typed_object(contact, "link", "contactUs.link")
    phone_numbers = _required_optional_typed_object(
        contact,
        "phoneNumber",
        "contactUs.phoneNumber",
    )
    email_addresses = _required_optional_typed_object(
        contact,
        "email",
        "contactUs.email",
    )
    return ContactUsInfo(
        links=_parse_contact_links(links) if links is not None else None,
        phone_numbers=(_parse_phone_numbers(phone_numbers) if phone_numbers is not None else None),
        email_addresses=(
            ContactEmailAddresses(
                _required_nullable_string(
                    email_addresses,
                    "secondDeliveryCustomerSupport",
                    "contactUs.email.secondDeliveryCustomerSupport",
                )
            )
            if email_addresses is not None
            else None
        ),
    )


def parse_cpo_details(data: Mapping[str, object]) -> CertifiedPreOwnedDetails | None:
    """Parse nullable certified-pre-owned provider details."""

    value = _required_field(data, "cpoDetails", "cpoDetails")
    if value is None:
        return None
    details = _typed_object(value, "cpoDetails")
    providers = _nullable_object_list(details, "data", "cpoDetails.data")
    parsed_providers: tuple[CertifiedPreOwnedProvider | None, ...] | None = None
    if providers is not None:
        values: list[CertifiedPreOwnedProvider | None] = []
        for index, provider in enumerate(providers):
            if provider is None:
                values.append(None)
                continue
            path = f"cpoDetails.data[{index}]"
            item = _typed_object(provider, path)
            values.append(
                CertifiedPreOwnedProvider(
                    _required_nullable_string(item, "brandName", f"{path}.brandName"),
                    _required_nullable_string(
                        item,
                        "preferredProvider",
                        f"{path}.preferredProvider",
                    ),
                )
            )
        parsed_providers = tuple(values)
    return CertifiedPreOwnedDetails(
        status_code=_required_nullable_string(details, "statusCode", "cpoDetails.statusCode"),
        status_message=_required_nullable_string(
            details,
            "statusMessage",
            "cpoDetails.statusMessage",
        ),
        timestamp=_required_nullable_string(details, "timestamp", "cpoDetails.timestamp"),
        data=parsed_providers,
    )


def parse_faq(data: Mapping[str, object]) -> tuple[FrequentlyAskedQuestionCategory, ...]:
    """Parse required FAQ categories and entries."""

    categories = _required_list(data, "faqs", "faqs")
    results: list[FrequentlyAskedQuestionCategory] = []
    for index, category_value in enumerate(categories):
        path = f"faqs[{index}]"
        category = _typed_object(category_value, path)
        entries = _required_list(category, "data", f"{path}.data")
        parsed_entries: list[FrequentlyAskedQuestion] = []
        for entry_index, entry_value in enumerate(entries):
            entry_path = f"{path}.data[{entry_index}]"
            entry = _typed_object(entry_value, entry_path)
            parsed_entries.append(
                FrequentlyAskedQuestion(
                    _required_string(entry, "question", f"{entry_path}.question"),
                    _required_string(entry, "answer", f"{entry_path}.answer"),
                )
            )
        results.append(
            FrequentlyAskedQuestionCategory(
                category=_required_string(category, "category", f"{path}.category"),
                entries=tuple(parsed_entries),
            )
        )
    return tuple(results)


def parse_live_chat_hours(
    data: Mapping[str, object],
) -> tuple[LiveChatHours | None, ...] | None:
    """Parse nullable live-chat availability entries."""

    contact = _required_typed_object(data, "contactUs", "contactUs")
    values = _nullable_object_list(contact, "liveChatHours", "contactUs.liveChatHours")
    if values is None:
        return None
    results: list[LiveChatHours | None] = []
    for index, value in enumerate(values):
        if value is None:
            results.append(None)
            continue
        path = f"contactUs.liveChatHours[{index}]"
        item = _typed_object(value, path)
        results.append(
            LiveChatHours(
                department_name=_required_nullable_string(
                    item,
                    "departmentName",
                    f"{path}.departmentName",
                ),
                opening_time=_required_nullable_datetime(
                    item,
                    "openingTime",
                    f"{path}.openingTime",
                ),
                closing_time=_required_nullable_datetime(
                    item,
                    "closingTime",
                    f"{path}.closingTime",
                ),
                after_hour_message=_required_nullable_string(
                    item,
                    "afterHourMessage",
                    f"{path}.afterHourMessage",
                ),
                available_now=_required_nullable_bool(
                    item,
                    "availableNow",
                    f"{path}.availableNow",
                ),
            )
        )
    return tuple(results)


def parse_mobile_carriers(data: Mapping[str, object]) -> tuple[MobileCarrier, ...]:
    """Parse the required mobile-carrier catalog."""

    values = _required_list(data, "mobileCarriers", "mobileCarriers")
    carriers: list[MobileCarrier] = []
    for index, value in enumerate(values):
        path = f"mobileCarriers[{index}]"
        item = _typed_object(value, path)
        carriers.append(
            MobileCarrier(
                id=_required_int(item, "id", f"{path}.id"),
                code=_required_enum(item, "code", MobileCarrierCode, f"{path}.code"),
                name=_required_string(item, "name", f"{path}.name"),
            )
        )
    return tuple(carriers)


def _parse_contact_links(value: Mapping[str, object]) -> ContactLinks:
    path = "contactUs.link"
    fields = (
        "privacyPolicy",
        "dataPrivacy",
        "collisionRepair",
        "accidentHelper",
        "checkOwnersPortal",
        "warranty",
        "forgotPassword",
        "editContactInformationAndChangePassword",
        "partsAndAccessories",
        "ifsAccount",
        "ncesiInsurance",
        "roadsideAid",
        "buyProtection",
        "nissanAddedSecurityPlanVideo",
        "nissanCertifiedPreOwnedVideo",
        "nissanPrepaidMaintenancePlanVideo",
        "secondDeliveryMarketingVideo",
        "disconnectRemoteAccess",
        "deleteAccount",
        "ariesApp",
    )
    values = tuple(_required_nullable_string(value, field, f"{path}.{field}") for field in fields)
    return ContactLinks(*values)


def _parse_phone_numbers(value: Mapping[str, object]) -> ContactPhoneNumbers:
    path = "contactUs.phoneNumber"
    fields = (
        "customerCare",
        "stolenVehicleLocator",
        "stolenVehicleInfo",
        "personalAssistant",
        "roadsideAssistant",
        "ownershipVerification",
        "resetVoicePin",
        "secondDeliveryCustomerSupport",
        "plugAndChargeSupport",
        "nissanStore",
    )
    values = tuple(_required_nullable_string(value, field, f"{path}.{field}") for field in fields)
    return ContactPhoneNumbers(*values)


def _required_typed_object(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> Mapping[str, object]:
    return _typed_object(_required_field(container, field, path), path)


def _required_list(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> list[object]:
    value = _required_field(container, field, path)
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    return value


def _nullable_object_list(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> list[object] | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    return value


def _required_nullable_datetime(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> datetime | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ResponseError(f"{path} is not a date-time string")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ResponseError(f"{path} is not an ISO-8601 date-time") from error
