from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class NissanStoreClientOrigin(StrEnum):
    """Known callers accepted by Nissan Store link operations."""

    WEB = "WEB"
    ONE_APP = "ONE_APP"
    UNKNOWN_VALUE = "UNKNOWN__"


class NissanPayPaymentProcessor(StrEnum):
    """Known Nissan Pay card processors."""

    VISA = "VISA"
    MASTERCARD = "MASTERCARD"
    AMEX = "AMEX"
    DISCOVER = "DISCOVER"
    DINERSCLUB = "DINERSCLUB"
    JCB = "JCB"
    UNKNOWN_VALUE = "UNKNOWN__"


class NissanPayPaymentMethodStatus(StrEnum):
    """Known Nissan Pay payment-method states."""

    ACTIVE = "ACTIVE"
    AWAITING_PAYMENT = "AWAITING_PAYMENT"
    ERRORED = "ERRORED"
    EXPIRED = "EXPIRED"
    UNKNOWN_VALUE = "UNKNOWN__"


class NissanPayChargeSessionType(StrEnum):
    """Known Nissan Pay energy charge-session types."""

    FOUNDATIONAL = "FOUNDATIONAL"
    PLUG_AND_CHARGE = "PLUG_AND_CHARGE"
    UNKNOWN_VALUE = "UNKNOWN__"


@dataclass(frozen=True, slots=True)
class UnselectedCommerceResult:
    """Future union branch represented only by its selected type name."""

    typename: str


@dataclass(frozen=True, slots=True)
class NissanStoreDeliveryGroup:
    """Required delivery group returned for a cart."""

    id: str


@dataclass(frozen=True, slots=True)
class NissanStoreCart:
    """Cart and its required delivery group."""

    id: str
    delivery_group: NissanStoreDeliveryGroup


@dataclass(frozen=True, slots=True)
class NissanStorePricingTerm:
    """Nullable numeric pricing term and unit."""

    value: int | None
    unit: str | None


@dataclass(frozen=True, slots=True)
class NissanStoreSubscription:
    """Subscription attached to an added product."""

    id: str
    selling_model_type: str | None
    pricing_term: NissanStorePricingTerm | None


@dataclass(frozen=True, slots=True)
class NissanStoreAddedProduct:
    """Product returned after it is added to a cart."""

    id: str
    name: str | None
    subscription: NissanStoreSubscription | None


@dataclass(frozen=True, slots=True)
class ProductAddedToNissanStoreCart:
    """Nullable cart and product returned by add-to-cart."""

    cart: NissanStoreCart | None
    product: NissanStoreAddedProduct | None


type AddProductToCartResult = ProductAddedToNissanStoreCart | UnselectedCommerceResult


@dataclass(frozen=True, slots=True)
class CancelPendingSubscriptionResult:
    """Nullable success flag returned by pending-order cancellation."""

    success: bool | None


@dataclass(frozen=True, slots=True)
class CancelSubscriptionStatus:
    """Generic nullable status branch returned by subscription cancellation."""

    success: bool | None


@dataclass(frozen=True, slots=True)
class CancelSubscriptionSuccess:
    """Detailed subscription-cancellation success branch."""

    success: bool | None
    subscription_end_date: datetime | None


@dataclass(frozen=True, slots=True)
class CancelSubscriptionGeneralError:
    """Subscription-cancellation error branch."""

    message: str


type CancelSubscriptionResult = (
    CancelSubscriptionStatus
    | CancelSubscriptionSuccess
    | CancelSubscriptionGeneralError
    | UnselectedCommerceResult
)


@dataclass(frozen=True, slots=True)
class NissanPayPaymentMethodCard:
    """Nullable card metadata selected by Nissan Pay."""

    payment_processor: NissanPayPaymentProcessor | None
    payment_icon: str | None
    is_default: bool | None
    last_four_digits: str | None
    expiry_month: int | None
    expiry_year: int | None
    status: NissanPayPaymentMethodStatus | None


type NissanPayPaymentMethod = NissanPayPaymentMethodCard | UnselectedCommerceResult


@dataclass(frozen=True, slots=True)
class NissanPayAccount:
    """Nullable payment methods and digital-wallet URL."""

    payment_methods: tuple[NissanPayPaymentMethod | None, ...] | None
    digital_wallet_url: str | None


@dataclass(frozen=True, slots=True)
class NissanPayOrderAddress:
    """Nullable address and coordinates attached to a Nissan Pay order."""

    city: str | None
    country: str | None
    country_code: str | None
    latitude: float | None
    longitude: float | None
    postal_code: str | None
    state: str | None
    state_code: str | None
    street: str | None


@dataclass(frozen=True, slots=True)
class NissanPayOrderPaymentMethod:
    """Nullable payment metadata attached to an order."""

    type: str | None
    processor: NissanPayPaymentProcessor | None
    last_four_digits: str | None


@dataclass(frozen=True, slots=True)
class NissanPayEnergyChargeSession:
    """Energy charging order returned by Nissan Pay."""

    order_date: datetime | None
    total_cost: float | None
    address: NissanPayOrderAddress | None
    payment_method: NissanPayOrderPaymentMethod | None
    cpo_brand: str | None
    session_type: NissanPayChargeSessionType | None
    charge_start_time: str | None
    charge_end_time: str | None
    charge_duration: str | None
    connector_type: str | None
    total_energy: float | None
    subtotal: float | None
    service_fee_total: float | None


type NissanPayOrder = NissanPayEnergyChargeSession | UnselectedCommerceResult


@dataclass(frozen=True, slots=True)
class NissanPayOrderHistoryPagination:
    """Nullable order-history pagination metadata."""

    next_page_cursor: str | None
    total_size: int | None


@dataclass(frozen=True, slots=True)
class NissanPayOrderHistory:
    """Required order entries and nullable pagination metadata."""

    items: tuple[NissanPayOrder | None, ...]
    pagination: NissanPayOrderHistoryPagination | None


@dataclass(frozen=True, slots=True)
class NissanStoreCatalogSellingModel:
    """Nullable pricing details for a product selling model."""

    pricing_term_unit: str | None
    retail_price: float | None
    discounted_price: float | None
    selling_model_type: str | None
    selling_model_id: str | None


@dataclass(frozen=True, slots=True)
class NissanStoreCatalogChildProduct:
    """Nullable child-product presentation data."""

    name: str | None
    customer_facing: bool | None


@dataclass(frozen=True, slots=True)
class NissanStoreCatalogPromotion:
    """Nullable Nissan Store promotion details."""

    promotion_id: str | None
    priority: int | None
    name: str | None
    monthly_price: float | None
    annual_price: float | None
    end_date: str | None
    description: str | None


@dataclass(frozen=True, slots=True)
class NissanStoreCatalogPackage:
    """Product package returned by the Nissan Store catalog."""

    short_description: str | None
    trial_duration: int | None
    product_image_url: str | None
    long_description: str | None
    selling_models: tuple[NissanStoreCatalogSellingModel | None, ...] | None
    product_id: str | None
    name: str | None
    child_products: tuple[NissanStoreCatalogChildProduct | None, ...] | None
    is_feature_on_demand: bool | None
    promotions: tuple[NissanStoreCatalogPromotion | None, ...] | None


@dataclass(frozen=True, slots=True)
class NissanStoreProductCatalog:
    """Nullable package list returned by the catalog union."""

    packages: tuple[NissanStoreCatalogPackage | None, ...] | None


type ProductCatalogResult = NissanStoreProductCatalog | UnselectedCommerceResult


@dataclass(frozen=True, slots=True)
class UpsertNissanPayAccountSuccess:
    """Successful Nissan Pay account synchronization."""

    response_message: str | None
    response_code: str | None
    response: str | None
    customer_id: str | None


@dataclass(frozen=True, slots=True)
class UpsertNissanPayAccountFailure:
    """Failed Nissan Pay account synchronization."""

    response_message: str | None
    response_code: str | None
    response: str | None


type UpsertNissanPayAccountResult = (
    UpsertNissanPayAccountSuccess | UpsertNissanPayAccountFailure | UnselectedCommerceResult
)
