from __future__ import annotations

import hashlib
from datetime import UTC, datetime

import pytest
from test_commerce import (
    EXPECTED_OPERATIONS,
    product_input,
)

from pynissan import (
    CancelPendingSubscriptionResult,
    CancelSubscriptionGeneralError,
    CancelSubscriptionInput,
    CancelSubscriptionSuccess,
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
    NissanStoreClientOrigin,
    NissanStoreDeliveryGroup,
    NissanStorePricingTerm,
    NissanStoreSubscription,
    ProductAddedToNissanStoreCart,
    ProductCatalogInput,
    UnselectedCommerceResult,
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
    parse_trial_checkout_link,
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
