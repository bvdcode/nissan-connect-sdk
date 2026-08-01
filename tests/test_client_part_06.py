from __future__ import annotations

import hashlib
from collections.abc import Mapping
from datetime import datetime
from typing import cast

import pytest
from test_client import (
    FakeResponse,
    FakeSession,
    make_client,
    vehicle_subscription_payload,
    vehicle_subscription_product_payload,
)

from pynissan import (
    ProductType,
    PurchaseType,
    ReadOnlyError,
    ResponseError,
    VehiclePreferences,
    VehicleSubscription,
    VehicleSubscriptionPendingOrder,
    VehicleSubscriptionProduct,
    VehicleSubscriptions,
)


@pytest.mark.asyncio
async def test_get_vehicle_preferences_preserves_nullable_mil_data_sharing_flags() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "preferences": {
                            "communication": {
                                "milDataSharing": {
                                    "enabled": True,
                                    "text": False,
                                    "phone": None,
                                    "email": True,
                                }
                            }
                        }
                    }
                }
            },
        )
    )

    result = await make_client(session).async_get_vehicle_preferences("JN1TESTVIN")

    assert result == VehiclePreferences(
        enabled=True,
        text=False,
        phone=None,
        email=True,
    )
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "VehiclePreferences"
    assert payload["variables"] == {"vin": "JN1TESTVIN"}
    query = cast(str, payload["query"])
    assert "preferences" in query
    assert "communication" in query
    assert "milDataSharing" in query
    assert all(field in query for field in ("enabled", "text", "phone", "email"))


@pytest.mark.asyncio
async def test_get_vehicle_preferences_preserves_nullable_response_chain() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"vehicle": None}}),
        FakeResponse(200, {"data": {"vehicle": {"preferences": None}}}),
        FakeResponse(
            200,
            {"data": {"vehicle": {"preferences": {"communication": None}}}},
        ),
        FakeResponse(
            200,
            {"data": {"vehicle": {"preferences": {"communication": {"milDataSharing": None}}}}},
        ),
    )
    client = make_client(session)

    assert await client.async_get_vehicle_preferences("VIN") is None
    assert await client.async_get_vehicle_preferences("VIN") is None
    assert await client.async_get_vehicle_preferences("VIN") is None
    assert await client.async_get_vehicle_preferences("VIN") is None


@pytest.mark.asyncio
async def test_update_vehicle_preferences_sends_complete_snapshot_with_nulls() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {"data": {"updateVehiclePreferences": {"success": True}}},
        )
    )
    preferences = VehiclePreferences(
        enabled=True,
        text=False,
        phone=None,
        email=True,
    )

    result = await make_client(
        session,
        read_only=False,
    ).async_update_vehicle_preferences("JN1TESTVIN", preferences)

    assert result is True
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "UpdateVehiclePreferences"
    assert payload["variables"] == {
        "vin": "JN1TESTVIN",
        "communication": {
            "milDataSharing": {
                "enabled": True,
                "text": False,
                "phone": None,
                "email": True,
            }
        },
    }
    query = cast(str, payload["query"])
    assert "$communication: UpdateVehiclePreferencesCommunicationInput!" in query
    assert "... on ResponseStatus { success }" in query
    assert "... on GeneralError { message }" in query


@pytest.mark.asyncio
async def test_update_vehicle_preferences_respects_read_only_mode() -> None:
    session = FakeSession()
    preferences = VehiclePreferences(None, None, None, None)

    with pytest.raises(ReadOnlyError):
        await make_client(session).async_update_vehicle_preferences("VIN", preferences)

    assert session.calls == []


@pytest.mark.asyncio
async def test_update_vehicle_preferences_raises_server_message() -> None:
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "updateVehiclePreferences": {
                        "__typename": "GeneralError",
                        "message": "Rejected",
                    }
                }
            },
        )
    )
    preferences = VehiclePreferences(True, False, None, None)

    with pytest.raises(ResponseError, match="Rejected"):
        await make_client(
            session,
            read_only=False,
        ).async_update_vehicle_preferences("VIN", preferences)


@pytest.mark.asyncio
async def test_get_vehicle_subscriptions_preserves_wire_values_and_exact_query() -> None:
    subscription = vehicle_subscription_payload(
        subscriptionServiceType="Paid",
        nextBillingDate="2027-02-03T04:05:06Z",
        goodwillEndDate="2027-01-01T00:00:00+00:00",
        goodwillStartDate="2026-12-01T00:00:00-08:00",
        graceEndDate=None,
        subscriptionStartDate="2099-01-01T12:00:00+05:30",
        isActive=False,
        npSubscriptionPrice=" $12.99 ",
        product=vehicle_subscription_product_payload(services=[None, "REMOTE_ENGINE"]),
        pendingOrder={
            "__typename": "VehicleSubscriptionPendingOrder",
            "pendingOrderId": "pending-1",
            "packageName": "Different package",
            "activationDate": None,
        },
    )
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "__typename": "BaseConnectedVehicle",
                        "capabilities": {
                            "__typename": "VehicleCapability",
                            "subscriptions": [None, subscription],
                        },
                    }
                }
            },
        )
    )

    result = await make_client(session).async_get_vehicle_subscriptions("JN1TESTVIN")

    assert result == VehicleSubscriptions(
        vin="JN1TESTVIN",
        subscriptions=(
            None,
            VehicleSubscription(
                subscription_id="subscription-1",
                subscription_service_type="Paid",
                purchase_type=PurchaseType.SUBSCRIPTION,
                product_type=ProductType.TELEMATICS,
                next_billing_date=datetime.fromisoformat("2027-02-03T04:05:06+00:00"),
                goodwill_end_date=datetime.fromisoformat("2027-01-01T00:00:00+00:00"),
                goodwill_start_date=datetime.fromisoformat("2026-12-01T00:00:00-08:00"),
                grace_end_date=None,
                subscription_start_date=datetime.fromisoformat("2099-01-01T12:00:00+05:30"),
                subscription_end_date=None,
                is_active=False,
                np_subscription_price=" $12.99 ",
                product=VehicleSubscriptionProduct(
                    product_id="product-1",
                    marketing_name="Premium",
                    description="Connected services",
                    services=(None, "REMOTE_ENGINE"),
                ),
                pending_order=VehicleSubscriptionPendingOrder(
                    pending_order_id="pending-1",
                    package_name="Different package",
                    activation_date=None,
                ),
            ),
        ),
    )
    payload = cast(Mapping[str, object], session.calls[0]["json"])
    assert payload["operationName"] == "VehicleSubscriptions"
    assert payload["variables"] == {"vin": "JN1TESTVIN"}
    query = cast(str, payload["query"])
    assert hashlib.sha256(query.encode()).hexdigest() == (
        "f73083b80399d14527938d7dfd92db232b5376ea2d36d9bc481e561bae67f566"
    )


@pytest.mark.asyncio
async def test_get_vehicle_subscriptions_distinguishes_nullable_response_branches() -> None:
    session = FakeSession(
        FakeResponse(200, {"data": {"vehicle": None}}),
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "__typename": "BaseVehicle",
                        "capabilities": None,
                    }
                }
            },
        ),
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "__typename": "BaseVehicle",
                        "capabilities": {
                            "__typename": "VehicleCapability",
                            "subscriptions": [],
                        },
                    }
                }
            },
        ),
    )
    client = make_client(session)

    assert await client.async_get_vehicle_subscriptions("VIN") is None
    assert await client.async_get_vehicle_subscriptions("VIN") == VehicleSubscriptions(
        vin="VIN",
        subscriptions=None,
    )
    assert await client.async_get_vehicle_subscriptions("VIN") == VehicleSubscriptions(
        vin="VIN",
        subscriptions=(),
    )


@pytest.mark.asyncio
async def test_get_vehicle_subscriptions_preserves_novel_enums_nulls_and_order() -> None:
    first = vehicle_subscription_payload(
        subscriptionId="duplicate",
        purchaseType="LOYALTY",
        productType="FUTURE_PRODUCT",
        isActive=None,
        npSubscriptionPrice=None,
    )
    second = vehicle_subscription_payload(
        subscriptionId="duplicate",
        purchaseType=None,
        productType=None,
        isActive=False,
        npSubscriptionPrice="",
    )
    session = FakeSession(
        FakeResponse(
            200,
            {
                "data": {
                    "vehicle": {
                        "__typename": "BaseVehicle",
                        "capabilities": {
                            "__typename": "VehicleCapability",
                            "subscriptions": [first, second],
                        },
                    }
                }
            },
        )
    )

    result = await make_client(session).async_get_vehicle_subscriptions("VIN")

    assert result is not None
    assert result.subscriptions is not None
    first_result, second_result = result.subscriptions
    assert first_result is not None
    assert first_result.purchase_type == "LOYALTY"
    assert not isinstance(first_result.purchase_type, PurchaseType)
    assert first_result.product_type == "FUTURE_PRODUCT"
    assert not isinstance(first_result.product_type, ProductType)
    assert first_result.is_active is None
    assert first_result.np_subscription_price is None
    assert second_result is not None
    assert second_result.subscription_id == first_result.subscription_id
    assert second_result.purchase_type is None
    assert second_result.product_type is None
    assert second_result.is_active is False
    assert second_result.np_subscription_price == ""
