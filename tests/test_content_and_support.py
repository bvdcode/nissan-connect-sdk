from __future__ import annotations

import hashlib
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import cast

from aiohttp import ClientSession

from pynissan import (
    CertifiedPreOwnedDetails,
    CertifiedPreOwnedProvider,
    ClientType,
    FrequentlyAskedQuestion,
    FrequentlyAskedQuestionCategory,
    LiveChatHours,
    MobileCarrier,
    MobileCarrierCode,
    NissanClient,
    Tokens,
    operations,
)
from pynissan.content_inputs import (
    contact_us_variables,
    faq_variables,
    live_chat_hours_variables,
)
from pynissan.content_parsing import (
    parse_contact_us,
    parse_cpo_details,
    parse_faq,
    parse_live_chat_hours,
    parse_mobile_carriers,
)

EXPECTED_OPERATIONS = {
    "CONTACT_US": "1a2cb197c34dd46fa630db96c73045b2db32ba1ebdeaada4317094c5e388477a",
    "CPO_DETAILS": "72e02068df86ded6c9c68b75bcc2854a4cddfc8304d78b0e8334c5e72571753b",
    "FAQ": "5896b6271d98fa7ad09ea38a7c1cf04e371b87514719d7ce8b4999bc60c0346d",
    "LIVE_CHAT_HOURS": "92c22ee63380315cd5c61993db910e8c451495d0f822c7a008a76642282d98a9",
    "MOBILE_CARRIERS": "5092ec79bc33ce00b3955693e1ecc513c3728bfe5be2c722dbf0525bdead660d",
}


class FakeResponse:
    def __init__(self, field: str, value: object) -> None:
        self.status = 200
        self._payload = {"data": {field: value}}

    async def __aenter__(self) -> FakeResponse:
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def json(self, *, content_type: object = None) -> object:
        return self._payload


class FakeSession:
    def __init__(self, *responses: FakeResponse) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, object]] = []

    def post(self, url: str, **kwargs: object) -> FakeResponse:
        self.calls.append({"url": url, **kwargs})
        if not self.responses:
            raise AssertionError("Unexpected HTTP request")
        return self.responses.pop(0)


def test_content_operations_match_service_documents() -> None:
    for constant, expected_id in EXPECTED_OPERATIONS.items():
        document = getattr(operations, constant)
        operation_id = getattr(operations, f"{constant}_OPERATION_ID")
        assert operation_id == expected_id
        assert hashlib.sha256(document.encode()).hexdigest() == expected_id


def test_content_query_variables_preserve_apollo_optionality() -> None:
    assert contact_us_variables(ClientType.ANDROID) == {"clientType": "ANDROID"}
    assert faq_variables() == {}
    assert faq_variables(None) == {"categories": None}
    assert faq_variables(("OWNER", None)) == {"categories": ["OWNER", None]}
    assert live_chat_hours_variables(("SALES", None), enhanced_chat=None) == {
        "departments": ["SALES", None],
        "enhancedChat": None,
    }


def test_parse_contact_us_preserves_nullable_groups_and_fields() -> None:
    link_fields = (
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
    links: dict[str, object] = {field: None for field in link_fields}
    links.update({"__typename": "ContactUsLink", "privacyPolicy": "https://example.test"})

    result = parse_contact_us(
        {
            "contactUs": {
                "__typename": "ContactUs",
                "link": links,
                "phoneNumber": None,
                "email": {
                    "__typename": "ContactUsEmail",
                    "secondDeliveryCustomerSupport": None,
                },
            }
        }
    )

    assert result.links is not None
    assert result.links.privacy_policy == "https://example.test"
    assert result.links.aries_app is None
    assert result.phone_numbers is None
    assert result.email_addresses is not None
    assert result.email_addresses.second_delivery_customer_support is None


def test_parse_cpo_faq_live_chat_and_mobile_carriers() -> None:
    assert parse_cpo_details(
        {
            "cpoDetails": {
                "__typename": "CpoDetails",
                "statusCode": None,
                "statusMessage": "Ready",
                "timestamp": None,
                "data": [
                    None,
                    {
                        "__typename": "CpoData",
                        "brandName": "Nissan",
                        "preferredProvider": None,
                    },
                ],
            }
        }
    ) == CertifiedPreOwnedDetails(
        None,
        "Ready",
        None,
        (None, CertifiedPreOwnedProvider("Nissan", None)),
    )
    assert parse_faq(
        {
            "faqs": [
                {
                    "__typename": "FAQ",
                    "category": "ACCOUNT",
                    "data": [
                        {
                            "__typename": "FAQData",
                            "question": "How?",
                            "answer": "Carefully.",
                        }
                    ],
                }
            ]
        }
    ) == (
        FrequentlyAskedQuestionCategory(
            "ACCOUNT",
            (FrequentlyAskedQuestion("How?", "Carefully."),),
        ),
    )
    assert parse_live_chat_hours(
        {
            "contactUs": {
                "__typename": "ContactUs",
                "liveChatHours": [
                    None,
                    {
                        "__typename": "LiveChatHours",
                        "departmentName": "Sales",
                        "openingTime": "2026-07-31T08:00:00Z",
                        "closingTime": None,
                        "afterHourMessage": None,
                        "availableNow": True,
                    },
                ],
            }
        }
    ) == (
        None,
        LiveChatHours(
            "Sales",
            datetime(2026, 7, 31, 8, tzinfo=UTC),
            None,
            None,
            True,
        ),
    )
    assert parse_mobile_carriers(
        {
            "mobileCarriers": [
                {
                    "__typename": "MobileCarrier",
                    "id": 7,
                    "code": "FUTURE_CARRIER",
                    "name": "Carrier",
                }
            ]
        }
    ) == (MobileCarrier(7, MobileCarrierCode.UNKNOWN_VALUE, "Carrier"),)


async def test_client_wires_every_content_and_support_query() -> None:
    session = FakeSession(
        FakeResponse(
            "contactUs",
            {
                "__typename": "ContactUs",
                "link": None,
                "phoneNumber": None,
                "email": None,
            },
        ),
        FakeResponse("cpoDetails", None),
        FakeResponse("faqs", []),
        FakeResponse("contactUs", {"__typename": "ContactUs", "liveChatHours": None}),
        FakeResponse("mobileCarriers", []),
    )
    sdk = NissanClient(
        cast(ClientSession, session),
        tokens=Tokens("access-token", "refresh-token", "id-token"),
    )

    assert (await sdk.async_get_contact_us()).links is None
    assert await sdk.async_get_cpo_details() is None
    assert await sdk.async_get_faq(("ACCOUNT",)) == ()
    assert await sdk.async_get_live_chat_hours(enhanced_chat=True) is None
    assert await sdk.async_get_mobile_carriers() == ()

    payloads: list[Mapping[str, object]] = []
    for call in session.calls:
        payload = call["json"]
        assert isinstance(payload, Mapping)
        payloads.append(payload)
    assert [payload["operationName"] for payload in payloads] == [
        "ContactUs",
        "CpoDetails",
        "FAQ",
        "LiveChatHours",
        "MobileCarriers",
    ]
    assert [payload["variables"] for payload in payloads] == [
        contact_us_variables(ClientType.ANDROID),
        {},
        faq_variables(("ACCOUNT",)),
        live_chat_hours_variables(enhanced_chat=True),
        {},
    ]
