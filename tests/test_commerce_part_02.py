from __future__ import annotations

from collections.abc import Awaitable, Mapping

import pytest
from test_commerce import (
    FakeResponse,
    FakeSession,
    make_client,
    product_input,
)

from pynissan import (
    CancelSubscriptionInput,
    NissanStoreCatalogChildProduct,
    NissanStoreCatalogPackage,
    NissanStoreCatalogPromotion,
    NissanStoreCatalogSellingModel,
    NissanStoreClientOrigin,
    NissanStoreProductCatalog,
    ProductCatalogInput,
    ReadOnlyError,
    UnselectedCommerceResult,
    UpsertNissanPayAccountFailure,
)
from pynissan.commerce_inputs import (
    add_product_to_cart_variables,
    cancel_pending_subscription_variables,
    cancel_subscription_variables,
    nissan_pay_order_history_variables,
    nissan_store_link_variables,
    product_catalog_variables,
)
from pynissan.commerce_parsing import (
    parse_product_catalog,
    parse_upsert_nissan_pay_account,
)


def test_parse_product_catalog_and_upsert_result() -> None:
    assert parse_product_catalog(
        {
            "productCatalog": {
                "__typename": "NSProductCatalog",
                "packages": [
                    None,
                    {
                        "__typename": "Package",
                        "shortDescription": "Package",
                        "npTrialDuration": None,
                        "productImageUrl": None,
                        "longDescription": None,
                        "sellingModels": [
                            {
                                "__typename": "SellingModel",
                                "sellingModelPricingTermUnit": "MONTH",
                                "retailPrice": 10,
                                "discountedPrice": 8.5,
                                "sellingModelType": "SUBSCRIPTION",
                                "sellingModelId": "model-id",
                            }
                        ],
                        "productId": "product-id",
                        "name": "Feature",
                        "childProducts": [
                            {
                                "__typename": "ChildProduct",
                                "name": "Child",
                                "npCustomerFacing": True,
                            }
                        ],
                        "isFoD": True,
                        "promotions": [
                            {
                                "__typename": "Promotion",
                                "promotionId": "promotion-id",
                                "priority": 1,
                                "name": "Offer",
                                "monthlyPromotionPrice": 7,
                                "annualPromotionPrice": 70,
                                "endDate": "2026-12-31",
                                "description": None,
                            }
                        ],
                    },
                ],
            }
        }
    ) == NissanStoreProductCatalog(
        (
            None,
            NissanStoreCatalogPackage(
                "Package",
                None,
                None,
                None,
                (
                    NissanStoreCatalogSellingModel(
                        "MONTH",
                        10.0,
                        8.5,
                        "SUBSCRIPTION",
                        "model-id",
                    ),
                ),
                "product-id",
                "Feature",
                (NissanStoreCatalogChildProduct("Child", True),),
                True,
                (
                    NissanStoreCatalogPromotion(
                        "promotion-id",
                        1,
                        "Offer",
                        7.0,
                        70.0,
                        "2026-12-31",
                        None,
                    ),
                ),
            ),
        )
    )
    assert parse_upsert_nissan_pay_account(
        {
            "upsertNissanPayAccount": {
                "__typename": "UpsertNissanPayAccountFailureResponse",
                "responseMessage": None,
                "responseCode": "FAILED",
                "response": None,
            }
        }
    ) == UpsertNissanPayAccountFailure(None, "FAILED", None)
    assert parse_upsert_nissan_pay_account(
        {"upsertNissanPayAccount": {"__typename": "FutureUpsertResult"}}
    ) == UnselectedCommerceResult("FutureUpsertResult")


async def test_client_wires_all_commerce_operations() -> None:
    session = FakeSession(
        FakeResponse("addProductToNissanStoreCart", None),
        FakeResponse("cancelPendingSubscription", {"__typename": "FutureStatus"}),
        FakeResponse("cancelSubscription", None),
        FakeResponse("createNissanStoreFODTrialCheckoutLink", None),
        FakeResponse("nissanPay", None),
        FakeResponse("nissanPay", None),
        FakeResponse("nissanPay", None),
        FakeResponse("nissanStoreCheckoutURL", None),
        FakeResponse("productCatalog", None),
        FakeResponse("upsertNissanPayAccount", None),
    )
    sdk = make_client(session, read_only=False)
    product = product_input()
    cancellation = CancelSubscriptionInput("subscription-id")
    catalog = ProductCatalogInput("VIN")

    assert await sdk.async_add_product_to_nissan_store_cart(product) is None
    assert await sdk.async_cancel_pending_subscription("pending-id") == UnselectedCommerceResult(
        "FutureStatus"
    )
    assert await sdk.async_cancel_subscription(cancellation) is None
    assert await sdk.async_create_nissan_store_fod_trial_checkout_link("VIN") is None
    assert await sdk.async_get_digital_wallet_url() is None
    assert await sdk.async_get_nissan_pay() is None
    assert await sdk.async_get_nissan_pay_order_history("VIN") is None
    assert await sdk.async_get_nissan_store_checkout_url("VIN") is None
    assert await sdk.async_get_product_catalog(catalog) is None
    assert await sdk.async_upsert_nissan_pay_account() is None

    payloads: list[Mapping[str, object]] = []
    for call in session.calls:
        payload = call["json"]
        assert isinstance(payload, Mapping)
        payloads.append(payload)
    assert [payload["operationName"] for payload in payloads] == [
        "AddProductToNissanStoreCart",
        "CancelPendingSubscription",
        "CancelSubscription",
        "CreateNissanStoreFODTrialCheckoutLink",
        "DigitalWalletURL",
        "NissanPay",
        "NissanPayOrderHistory",
        "NissanStoreCheckoutURL",
        "ProductCatalog",
        "UpsertNissanPayAccount",
    ]
    assert [payload["variables"] for payload in payloads] == [
        add_product_to_cart_variables(product),
        cancel_pending_subscription_variables("pending-id"),
        cancel_subscription_variables(cancellation),
        nissan_store_link_variables("VIN", NissanStoreClientOrigin.ONE_APP),
        {},
        {},
        nissan_pay_order_history_variables("VIN"),
        nissan_store_link_variables("VIN", NissanStoreClientOrigin.ONE_APP),
        product_catalog_variables(catalog),
        {},
    ]


async def test_read_only_mode_blocks_every_commerce_mutation_before_network() -> None:
    session = FakeSession()
    sdk = make_client(session, read_only=True)
    calls: tuple[Awaitable[object], ...] = (
        sdk.async_add_product_to_nissan_store_cart(product_input()),
        sdk.async_cancel_pending_subscription("pending-id"),
        sdk.async_cancel_subscription(CancelSubscriptionInput("subscription-id")),
        sdk.async_create_nissan_store_fod_trial_checkout_link("VIN"),
        sdk.async_upsert_nissan_pay_account(),
    )

    for call in calls:
        with pytest.raises(ReadOnlyError):
            await call

    assert session.calls == []
