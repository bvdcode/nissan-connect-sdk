from __future__ import annotations

from dataclasses import dataclass

from .commerce_models import NissanStoreClientOrigin
from .graphql_input import UNSET, UnsetType, optional_input_fields, serialize_enum


@dataclass(frozen=True, slots=True)
class AddProductToCartInput:
    """Required product selection and optional promotion for Nissan Store."""

    product_id: str
    quantity: int
    vin: str
    product_selling_model_id: str
    promotion_id: str | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class CancelSubscriptionInput:
    """Optional nullable subscription identifier accepted by cancellation."""

    subscription_id: str | UnsetType | None = UNSET


@dataclass(frozen=True, slots=True)
class ProductCatalogInput:
    """Optional nullable VIN filter accepted by Nissan Store catalog."""

    vin: str | UnsetType | None = UNSET


def add_product_to_cart_variables(config: AddProductToCartInput) -> dict[str, object]:
    """Serialize Nissan Store add-to-cart variables."""

    return {
        "addProductToNissanStoreCartInput": optional_input_fields(
            promotionId=config.promotion_id,
            productId=config.product_id,
            quantity=config.quantity,
            vin=config.vin,
            productSellingModelId=config.product_selling_model_id,
        )
    }


def cancel_pending_subscription_variables(pending_order_id: str) -> dict[str, object]:
    """Serialize a required pending-order identifier."""

    return {"cancelPendingSubscriptionInput": {"pendingOrderId": pending_order_id}}


def cancel_subscription_variables(config: CancelSubscriptionInput) -> dict[str, object]:
    """Serialize subscription cancellation input."""

    return {
        "cancelSubscriptionInput": optional_input_fields(
            subscriptionId=config.subscription_id,
        )
    }


def nissan_store_link_variables(
    vin: str,
    client_origin: NissanStoreClientOrigin,
) -> dict[str, object]:
    """Serialize Nissan Store checkout-link variables."""

    return {"vin": vin, "clientOrigin": serialize_enum(client_origin)}


def nissan_pay_order_history_variables(
    vin: str,
    page_cursor: str | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize paginated Nissan Pay order-history variables."""

    return optional_input_fields(vin=vin, pageCursor=page_cursor)


def product_catalog_variables(config: ProductCatalogInput) -> dict[str, object]:
    """Serialize the required product-catalog input wrapper."""

    return {"productCatalogInput": optional_input_fields(vin=config.vin)}
