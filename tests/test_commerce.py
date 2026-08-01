from __future__ import annotations

import hashlib
from collections.abc import Awaitable, Mapping
from datetime import UTC, datetime
from typing import cast

import pytest
from aiohttp import ClientSession

from pynissan import (
    AddProductToCartInput,
    CancelPendingSubscriptionResult,
    CancelSubscriptionGeneralError,
    CancelSubscriptionInput,
    CancelSubscriptionSuccess,
    NissanClient,
    NissanPayAccount,
    NissanPayChargeSessionType,
    NissanPayEnergyChargeSession,
    NissanPayOrderAddress,
    NissanPayOrderHistory,
    NissanPayOrderHistoryPagination,
    NissanPayOrderPaymentMethod,
    NissanPayPaymentMethodCard,
    NissanPayPaymentMethodStatus,
    NissanPayPaymentProcessor,
    NissanStoreAddedProduct,
    NissanStoreCart,
    NissanStoreCatalogChildProduct,
    NissanStoreCatalogPackage,
    NissanStoreCatalogPromotion,
    NissanStoreCatalogSellingModel,
    NissanStoreClientOrigin,
    NissanStoreDeliveryGroup,
    NissanStorePricingTerm,
    NissanStoreProductCatalog,
    NissanStoreSubscription,
    ProductAddedToNissanStoreCart,
    ProductCatalogInput,
    ReadOnlyError,
    Tokens,
    UnselectedCommerceResult,
    UpsertNissanPayAccountFailure,
    operations,
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
    parse_add_product_to_cart,
    parse_cancel_pending_subscription,
    parse_cancel_subscription,
    parse_digital_wallet_url,
    parse_nissan_pay,
    parse_nissan_pay_order_history,
    parse_nissan_store_checkout_url,
    parse_product_catalog,
    parse_trial_checkout_link,
    parse_upsert_nissan_pay_account,
)

EXPECTED_OPERATIONS = {
    "ADD_PRODUCT_TO_NISSAN_STORE_CART": (
        "eed0e98dfe2cc937bc49082ee698ec7c5a160f7e1ede1aa0006f79cb5bfdd4af"
    ),
    "CANCEL_PENDING_SUBSCRIPTION": (
        "7c58341746585b1af72ceb9d106da15c99d9660016b35fab59cdf3b6ae27e20f"
    ),
    "CANCEL_SUBSCRIPTION": ("582a6770133943805e710c65e4b27ade68e9f81530f88b417e2623e9cac277d2"),
    "CREATE_NISSAN_STORE_FOD_TRIAL_CHECKOUT_LINK": (
        "9c6c28d802fca574a547c921840ebb9397093a213d6f4dfd05c522e12757b990"
    ),
    "DIGITAL_WALLET_URL": ("6ebdf2e75a646b0905f99afa77af67e9e6b6b58461b0d2bce71be4bc072fd30e"),
    "NISSAN_PAY": "6f08f0f64f7bebe3ce087dcdda08ef0198d3f926dec70c43941dd54e84fc660b",
    "NISSAN_PAY_ORDER_HISTORY": (
        "03eceb4c138de1b971d5c1415b29327cd990c4ba5392a82504aa429ded0c96bb"
    ),
    "NISSAN_STORE_CHECKOUT_URL": (
        "814f25c745f3e438233e812c89e1a9dc67bdf8c7416b54e983c1e5f9a3872cfe"
    ),
    "PRODUCT_CATALOG": ("03e4214e129ea35a0a2d8255aaac2481373ef478c611cfb9684e7281d812f30f"),
    "UPSERT_NISSAN_PAY_ACCOUNT": (
        "f4483575cf435a5fa6693606a4915b97cb609fe110a74a58dbc162ba41feb0a4"
    ),
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


def make_client(session: FakeSession, *, read_only: bool) -> NissanClient:
    return NissanClient(
        cast(ClientSession, session),
        tokens=Tokens("access-token", "refresh-token", "id-token"),
        read_only=read_only,
    )


def product_input() -> AddProductToCartInput:
    return AddProductToCartInput(
        product_id="product-id",
        quantity=1,
        vin="VIN",
        product_selling_model_id="selling-model-id",
        promotion_id=None,
    )


def test_commerce_operations_match_service_documents() -> None:
    for constant, expected_id in EXPECTED_OPERATIONS.items():
        document = getattr(operations, constant)
        operation_id = getattr(operations, f"{constant}_OPERATION_ID")
        assert operation_id == expected_id
        assert hashlib.sha256(document.encode()).hexdigest() == expected_id


def test_commerce_inputs_preserve_required_optional_and_nullable_fields() -> None:
    assert add_product_to_cart_variables(product_input()) == {
        "addProductToNissanStoreCartInput": {
            "promotionId": None,
            "productId": "product-id",
            "quantity": 1,
            "vin": "VIN",
            "productSellingModelId": "selling-model-id",
        }
    }
    assert cancel_pending_subscription_variables("pending-id") == {
        "cancelPendingSubscriptionInput": {"pendingOrderId": "pending-id"}
    }
    assert cancel_subscription_variables(CancelSubscriptionInput()) == {
        "cancelSubscriptionInput": {}
    }
    assert cancel_subscription_variables(CancelSubscriptionInput(None)) == {
        "cancelSubscriptionInput": {"subscriptionId": None}
    }
    assert product_catalog_variables(ProductCatalogInput()) == {"productCatalogInput": {}}
    assert product_catalog_variables(ProductCatalogInput(None)) == {
        "productCatalogInput": {"vin": None}
    }
    assert nissan_pay_order_history_variables("VIN") == {"vin": "VIN"}
    assert nissan_store_link_variables("VIN", NissanStoreClientOrigin.ONE_APP) == {
        "vin": "VIN",
        "clientOrigin": "ONE_APP",
    }
    with pytest.raises(ValueError, match="UNKNOWN_VALUE cannot be sent"):
        nissan_store_link_variables("VIN", NissanStoreClientOrigin.UNKNOWN_VALUE)


def test_parse_add_to_cart_and_subscription_cancellations() -> None:
    assert parse_add_product_to_cart(
        {
            "addProductToNissanStoreCart": {
                "__typename": "AddProductToNissanStoreCartOutput",
                "cart": {
                    "__typename": "Cart",
                    "id": "cart-id",
                    "deliveryGroup": {"__typename": "DeliveryGroup", "id": "group-id"},
                },
                "product": {
                    "__typename": "Product",
                    "id": "product-id",
                    "name": None,
                    "subscription": {
                        "__typename": "Subscription",
                        "id": "subscription-id",
                        "sellingModelType": "MONTHLY",
                        "pricingTerm": {
                            "__typename": "PricingTerm",
                            "value": 12,
                            "unit": "MONTH",
                        },
                    },
                },
            }
        }
    ) == ProductAddedToNissanStoreCart(
        NissanStoreCart("cart-id", NissanStoreDeliveryGroup("group-id")),
        NissanStoreAddedProduct(
            "product-id",
            None,
            NissanStoreSubscription(
                "subscription-id",
                "MONTHLY",
                NissanStorePricingTerm(12, "MONTH"),
            ),
        ),
    )
    assert parse_cancel_pending_subscription(
        {
            "cancelPendingSubscription": {
                "__typename": "ResponseStatusType",
                "success": None,
            }
        }
    ) == CancelPendingSubscriptionResult(None)
    assert parse_cancel_subscription(
        {
            "cancelSubscription": {
                "__typename": "CancelSubscriptionSuccessResponse",
                "success": True,
                "subscriptionEndDate": "2026-08-01T00:00:00Z",
            }
        }
    ) == CancelSubscriptionSuccess(True, datetime(2026, 8, 1, tzinfo=UTC))
    assert parse_cancel_subscription(
        {
            "cancelSubscription": {
                "__typename": "CancelSubscriptionGeneralError",
                "message": "Unable to cancel",
            }
        }
    ) == CancelSubscriptionGeneralError("Unable to cancel")


def test_parse_nissan_pay_methods_and_urls() -> None:
    assert (
        parse_trial_checkout_link(
            {"createNissanStoreFODTrialCheckoutLink": "https://example.test/trial"}
        )
        == "https://example.test/trial"
    )
    assert (
        parse_nissan_store_checkout_url({"nissanStoreCheckoutURL": "https://example.test/checkout"})
        == "https://example.test/checkout"
    )
    assert (
        parse_digital_wallet_url(
            {
                "nissanPay": {
                    "__typename": "NissanPay",
                    "digitalWallet": {"__typename": "DigitalWallet", "url": None},
                }
            }
        )
        is None
    )
    assert parse_nissan_pay(
        {
            "nissanPay": {
                "__typename": "NissanPay",
                "paymentMethods": [
                    None,
                    {
                        "__typename": "NissanPayPaymentMethodCard",
                        "paymentProcessor": "VISA",
                        "paymentIcon": None,
                        "isDefault": True,
                        "last4Digits": "1234",
                        "expiryMonth": 8,
                        "expiryYear": 2030,
                        "status": "ACTIVE",
                    },
                    {"__typename": "FuturePaymentMethod"},
                ],
                "digitalWallet": {
                    "__typename": "DigitalWallet",
                    "url": "https://example.test/wallet",
                },
            }
        }
    ) == NissanPayAccount(
        (
            None,
            NissanPayPaymentMethodCard(
                NissanPayPaymentProcessor.VISA,
                None,
                True,
                "1234",
                8,
                2030,
                NissanPayPaymentMethodStatus.ACTIVE,
            ),
            UnselectedCommerceResult("FuturePaymentMethod"),
        ),
        "https://example.test/wallet",
    )


def test_parse_nissan_pay_order_history() -> None:
    assert parse_nissan_pay_order_history(
        {
            "nissanPay": {
                "__typename": "NissanPay",
                "orderHistory": {
                    "__typename": "OrderHistory",
                    "items": [
                        None,
                        {
                            "__typename": "NissanPayEnergyChargeSession",
                            "orderDate": "2026-07-31T12:00:00Z",
                            "totalCost": 8.5,
                            "address": {
                                "__typename": "Address",
                                "city": "Franklin",
                                "country": "United States",
                                "countryCode": "US",
                                "latitude": 35.9,
                                "longitude": -86.8,
                                "postalCode": "37064",
                                "state": "Tennessee",
                                "stateCode": "TN",
                                "street": "1 Main St",
                            },
                            "paymentMethod": {
                                "__typename": "PaymentMethod",
                                "type": "CARD",
                                "processor": "FUTURE_PROCESSOR",
                                "last4": "1234",
                            },
                            "cpoBrand": "Network",
                            "sessionType": "PLUG_AND_CHARGE",
                            "chargeStartTime": "start",
                            "chargeEndTime": "end",
                            "chargeDuration": "PT30M",
                            "connectorType": "CCS",
                            "totalEnergy": 15.2,
                            "subtotal": 7.5,
                            "serviceFeeTotal": 1.0,
                        },
                    ],
                    "pagination": {
                        "__typename": "Pagination",
                        "nextPageCursor": None,
                        "totalSize": 1,
                    },
                },
            }
        }
    ) == NissanPayOrderHistory(
        (
            None,
            NissanPayEnergyChargeSession(
                datetime(2026, 7, 31, 12, tzinfo=UTC),
                8.5,
                NissanPayOrderAddress(
                    "Franklin",
                    "United States",
                    "US",
                    35.9,
                    -86.8,
                    "37064",
                    "Tennessee",
                    "TN",
                    "1 Main St",
                ),
                NissanPayOrderPaymentMethod(
                    "CARD",
                    NissanPayPaymentProcessor.UNKNOWN_VALUE,
                    "1234",
                ),
                "Network",
                NissanPayChargeSessionType.PLUG_AND_CHARGE,
                "start",
                "end",
                "PT30M",
                "CCS",
                15.2,
                7.5,
                1.0,
            ),
        ),
        NissanPayOrderHistoryPagination(None, 1),
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
