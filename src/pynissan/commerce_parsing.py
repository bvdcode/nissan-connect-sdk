from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime
from enum import StrEnum

from .account_parsing import (
    _enum,
    _required_field,
    _required_nullable_bool,
    _required_nullable_int,
    _required_nullable_string,
    _required_optional_typed_object,
    _required_string,
    _root,
    _typed_object,
    _typename,
)
from .commerce_models import (
    AddProductToCartResult,
    CancelPendingSubscriptionResult,
    CancelSubscriptionGeneralError,
    CancelSubscriptionResult,
    CancelSubscriptionStatus,
    CancelSubscriptionSuccess,
    NissanPayAccount,
    NissanPayChargeSessionType,
    NissanPayEnergyChargeSession,
    NissanPayOrder,
    NissanPayOrderAddress,
    NissanPayOrderHistory,
    NissanPayOrderHistoryPagination,
    NissanPayOrderPaymentMethod,
    NissanPayPaymentMethod,
    NissanPayPaymentMethodCard,
    NissanPayPaymentMethodStatus,
    NissanPayPaymentProcessor,
    NissanStoreAddedProduct,
    NissanStoreCart,
    NissanStoreCatalogChildProduct,
    NissanStoreCatalogPackage,
    NissanStoreCatalogPromotion,
    NissanStoreCatalogSellingModel,
    NissanStoreDeliveryGroup,
    NissanStorePricingTerm,
    NissanStoreProductCatalog,
    NissanStoreSubscription,
    ProductAddedToNissanStoreCart,
    ProductCatalogResult,
    UnselectedCommerceResult,
    UpsertNissanPayAccountFailure,
    UpsertNissanPayAccountResult,
    UpsertNissanPayAccountSuccess,
)
from .exceptions import ResponseError


def parse_add_product_to_cart(
    data: Mapping[str, object],
) -> AddProductToCartResult | None:
    """Parse every selected Nissan Store add-to-cart union branch."""

    root_field = "addProductToNissanStoreCart"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if typename != "AddProductToNissanStoreCartOutput":
        return UnselectedCommerceResult(typename)
    cart = _required_optional_typed_object(root, "cart", f"{root_field}.cart")
    product = _required_optional_typed_object(root, "product", f"{root_field}.product")
    return ProductAddedToNissanStoreCart(
        cart=_parse_added_cart(cart, f"{root_field}.cart") if cart is not None else None,
        product=(
            _parse_added_product(product, f"{root_field}.product") if product is not None else None
        ),
    )


def parse_cancel_pending_subscription(
    data: Mapping[str, object],
) -> CancelPendingSubscriptionResult | UnselectedCommerceResult:
    """Parse pending-subscription cancellation status."""

    root_field = "cancelPendingSubscription"
    root = _required_typed_object(data, root_field, root_field)
    typename = _typename(root, root_field)
    if typename == "ResponseStatusType":
        return CancelPendingSubscriptionResult(
            _required_nullable_bool(root, "success", f"{root_field}.success")
        )
    return UnselectedCommerceResult(typename)


def parse_cancel_subscription(
    data: Mapping[str, object],
) -> CancelSubscriptionResult | None:
    """Parse every selected subscription-cancellation union branch."""

    root_field = "cancelSubscription"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if typename == "ResponseStatus":
        return CancelSubscriptionStatus(
            _required_nullable_bool(root, "success", f"{root_field}.success")
        )
    if typename == "CancelSubscriptionSuccessResponse":
        return CancelSubscriptionSuccess(
            success=_required_nullable_bool(root, "success", f"{root_field}.success"),
            subscription_end_date=_required_nullable_datetime(
                root,
                "subscriptionEndDate",
                f"{root_field}.subscriptionEndDate",
            ),
        )
    if typename == "CancelSubscriptionGeneralError":
        return CancelSubscriptionGeneralError(
            _required_string(root, "message", f"{root_field}.message")
        )
    return UnselectedCommerceResult(typename)


def parse_trial_checkout_link(data: Mapping[str, object]) -> str | None:
    """Parse the nullable feature-on-demand trial checkout link."""

    return _required_nullable_string(
        data,
        "createNissanStoreFODTrialCheckoutLink",
        "createNissanStoreFODTrialCheckoutLink",
    )


def parse_digital_wallet_url(data: Mapping[str, object]) -> str | None:
    """Parse the nullable Nissan Pay digital-wallet URL."""

    nissan_pay = _required_optional_typed_object(data, "nissanPay", "nissanPay")
    if nissan_pay is None:
        return None
    wallet = _required_optional_typed_object(
        nissan_pay,
        "digitalWallet",
        "nissanPay.digitalWallet",
    )
    if wallet is None:
        return None
    return _required_nullable_string(wallet, "url", "nissanPay.digitalWallet.url")


def parse_nissan_pay(data: Mapping[str, object]) -> NissanPayAccount | None:
    """Parse Nissan Pay methods and the nullable digital-wallet URL."""

    root = _required_optional_typed_object(data, "nissanPay", "nissanPay")
    if root is None:
        return None
    methods = _nullable_list(root, "paymentMethods", "nissanPay.paymentMethods")
    parsed_methods: tuple[NissanPayPaymentMethod | None, ...] | None = None
    if methods is not None:
        values: list[NissanPayPaymentMethod | None] = []
        for index, value in enumerate(methods):
            if value is None:
                values.append(None)
                continue
            path = f"nissanPay.paymentMethods[{index}]"
            item = _typed_object(value, path)
            typename = _typename(item, path)
            if typename == "NissanPayPaymentMethodCard":
                values.append(_parse_payment_card(item, path))
            else:
                values.append(UnselectedCommerceResult(typename))
        parsed_methods = tuple(values)
    wallet = _required_optional_typed_object(root, "digitalWallet", "nissanPay.digitalWallet")
    return NissanPayAccount(
        payment_methods=parsed_methods,
        digital_wallet_url=(
            _required_nullable_string(wallet, "url", "nissanPay.digitalWallet.url")
            if wallet is not None
            else None
        ),
    )


def parse_nissan_pay_order_history(
    data: Mapping[str, object],
) -> NissanPayOrderHistory | None:
    """Parse the nullable Nissan Pay energy order history."""

    nissan_pay = _required_optional_typed_object(data, "nissanPay", "nissanPay")
    if nissan_pay is None:
        return None
    history = _required_optional_typed_object(
        nissan_pay,
        "orderHistory",
        "nissanPay.orderHistory",
    )
    if history is None:
        return None
    item_values = _required_list(history, "items", "nissanPay.orderHistory.items")
    items: list[NissanPayOrder | None] = []
    for index, value in enumerate(item_values):
        if value is None:
            items.append(None)
            continue
        path = f"nissanPay.orderHistory.items[{index}]"
        item = _typed_object(value, path)
        typename = _typename(item, path)
        if typename == "NissanPayEnergyChargeSession":
            items.append(_parse_energy_charge_session(item, path))
        else:
            items.append(UnselectedCommerceResult(typename))
    pagination = _required_optional_typed_object(
        history,
        "pagination",
        "nissanPay.orderHistory.pagination",
    )
    return NissanPayOrderHistory(
        items=tuple(items),
        pagination=(
            NissanPayOrderHistoryPagination(
                next_page_cursor=_required_nullable_string(
                    pagination,
                    "nextPageCursor",
                    "nissanPay.orderHistory.pagination.nextPageCursor",
                ),
                total_size=_required_nullable_int(
                    pagination,
                    "totalSize",
                    "nissanPay.orderHistory.pagination.totalSize",
                ),
            )
            if pagination is not None
            else None
        ),
    )


def parse_nissan_store_checkout_url(data: Mapping[str, object]) -> str | None:
    """Parse the nullable Nissan Store checkout URL."""

    return _required_nullable_string(
        data,
        "nissanStoreCheckoutURL",
        "nissanStoreCheckoutURL",
    )


def parse_product_catalog(data: Mapping[str, object]) -> ProductCatalogResult | None:
    """Parse every selected Nissan Store product-catalog union branch."""

    root_field = "productCatalog"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if typename != "NSProductCatalog":
        return UnselectedCommerceResult(typename)
    packages = _nullable_list(root, "packages", f"{root_field}.packages")
    parsed_packages: tuple[NissanStoreCatalogPackage | None, ...] | None = None
    if packages is not None:
        values: list[NissanStoreCatalogPackage | None] = []
        for index, value in enumerate(packages):
            if value is None:
                values.append(None)
                continue
            path = f"{root_field}.packages[{index}]"
            values.append(_parse_catalog_package(_typed_object(value, path), path))
        parsed_packages = tuple(values)
    return NissanStoreProductCatalog(parsed_packages)


def parse_upsert_nissan_pay_account(
    data: Mapping[str, object],
) -> UpsertNissanPayAccountResult | None:
    """Parse every selected Nissan Pay account-upsert union branch."""

    root_field = "upsertNissanPayAccount"
    root = _root(data, root_field)
    if root is None:
        return None
    typename = _typename(root, root_field)
    if typename not in {
        "UpsertNissanPayAccountSuccessResponse",
        "UpsertNissanPayAccountFailureResponse",
    }:
        return UnselectedCommerceResult(typename)
    response_message = _required_nullable_string(
        root,
        "responseMessage",
        f"{root_field}.responseMessage",
    )
    response_code = _required_nullable_string(
        root,
        "responseCode",
        f"{root_field}.responseCode",
    )
    response = _required_nullable_string(root, "response", f"{root_field}.response")
    if typename == "UpsertNissanPayAccountSuccessResponse":
        return UpsertNissanPayAccountSuccess(
            response_message,
            response_code,
            response,
            _required_nullable_string(root, "customerId", f"{root_field}.customerId"),
        )
    return UpsertNissanPayAccountFailure(response_message, response_code, response)


def _parse_added_cart(value: Mapping[str, object], path: str) -> NissanStoreCart:
    delivery_path = f"{path}.deliveryGroup"
    delivery = _required_typed_object(value, "deliveryGroup", delivery_path)
    return NissanStoreCart(
        id=_required_string(value, "id", f"{path}.id"),
        delivery_group=NissanStoreDeliveryGroup(
            _required_string(delivery, "id", f"{delivery_path}.id")
        ),
    )


def _parse_added_product(value: Mapping[str, object], path: str) -> NissanStoreAddedProduct:
    subscription_path = f"{path}.subscription"
    subscription = _required_optional_typed_object(value, "subscription", subscription_path)
    return NissanStoreAddedProduct(
        id=_required_string(value, "id", f"{path}.id"),
        name=_required_nullable_string(value, "name", f"{path}.name"),
        subscription=(
            _parse_added_subscription(subscription, subscription_path)
            if subscription is not None
            else None
        ),
    )


def _parse_added_subscription(
    value: Mapping[str, object],
    path: str,
) -> NissanStoreSubscription:
    pricing_path = f"{path}.pricingTerm"
    pricing = _required_optional_typed_object(value, "pricingTerm", pricing_path)
    return NissanStoreSubscription(
        id=_required_string(value, "id", f"{path}.id"),
        selling_model_type=_required_nullable_string(
            value,
            "sellingModelType",
            f"{path}.sellingModelType",
        ),
        pricing_term=(
            NissanStorePricingTerm(
                value=_required_nullable_int(pricing, "value", f"{pricing_path}.value"),
                unit=_required_nullable_string(pricing, "unit", f"{pricing_path}.unit"),
            )
            if pricing is not None
            else None
        ),
    )


def _parse_payment_card(
    value: Mapping[str, object],
    path: str,
) -> NissanPayPaymentMethodCard:
    return NissanPayPaymentMethodCard(
        payment_processor=_required_nullable_enum(
            value,
            "paymentProcessor",
            NissanPayPaymentProcessor,
            f"{path}.paymentProcessor",
        ),
        payment_icon=_required_nullable_string(value, "paymentIcon", f"{path}.paymentIcon"),
        is_default=_required_nullable_bool(value, "isDefault", f"{path}.isDefault"),
        last_four_digits=_required_nullable_string(
            value,
            "last4Digits",
            f"{path}.last4Digits",
        ),
        expiry_month=_required_nullable_int(value, "expiryMonth", f"{path}.expiryMonth"),
        expiry_year=_required_nullable_int(value, "expiryYear", f"{path}.expiryYear"),
        status=_required_nullable_enum(
            value,
            "status",
            NissanPayPaymentMethodStatus,
            f"{path}.status",
        ),
    )


def _parse_energy_charge_session(
    value: Mapping[str, object],
    path: str,
) -> NissanPayEnergyChargeSession:
    address_path = f"{path}.address"
    address = _required_optional_typed_object(value, "address", address_path)
    payment_path = f"{path}.paymentMethod"
    payment = _required_optional_typed_object(value, "paymentMethod", payment_path)
    return NissanPayEnergyChargeSession(
        order_date=_required_nullable_datetime(value, "orderDate", f"{path}.orderDate"),
        total_cost=_required_nullable_float(value, "totalCost", f"{path}.totalCost"),
        address=_parse_order_address(address, address_path) if address is not None else None,
        payment_method=(
            _parse_order_payment_method(payment, payment_path) if payment is not None else None
        ),
        cpo_brand=_required_nullable_string(value, "cpoBrand", f"{path}.cpoBrand"),
        session_type=_required_nullable_enum(
            value,
            "sessionType",
            NissanPayChargeSessionType,
            f"{path}.sessionType",
        ),
        charge_start_time=_required_nullable_string(
            value,
            "chargeStartTime",
            f"{path}.chargeStartTime",
        ),
        charge_end_time=_required_nullable_string(
            value,
            "chargeEndTime",
            f"{path}.chargeEndTime",
        ),
        charge_duration=_required_nullable_string(
            value,
            "chargeDuration",
            f"{path}.chargeDuration",
        ),
        connector_type=_required_nullable_string(
            value,
            "connectorType",
            f"{path}.connectorType",
        ),
        total_energy=_required_nullable_float(value, "totalEnergy", f"{path}.totalEnergy"),
        subtotal=_required_nullable_float(value, "subtotal", f"{path}.subtotal"),
        service_fee_total=_required_nullable_float(
            value,
            "serviceFeeTotal",
            f"{path}.serviceFeeTotal",
        ),
    )


def _parse_order_address(value: Mapping[str, object], path: str) -> NissanPayOrderAddress:
    return NissanPayOrderAddress(
        city=_required_nullable_string(value, "city", f"{path}.city"),
        country=_required_nullable_string(value, "country", f"{path}.country"),
        country_code=_required_nullable_string(value, "countryCode", f"{path}.countryCode"),
        latitude=_required_nullable_float(value, "latitude", f"{path}.latitude"),
        longitude=_required_nullable_float(value, "longitude", f"{path}.longitude"),
        postal_code=_required_nullable_string(value, "postalCode", f"{path}.postalCode"),
        state=_required_nullable_string(value, "state", f"{path}.state"),
        state_code=_required_nullable_string(value, "stateCode", f"{path}.stateCode"),
        street=_required_nullable_string(value, "street", f"{path}.street"),
    )


def _parse_order_payment_method(
    value: Mapping[str, object],
    path: str,
) -> NissanPayOrderPaymentMethod:
    return NissanPayOrderPaymentMethod(
        type=_required_nullable_string(value, "type", f"{path}.type"),
        processor=_required_nullable_enum(
            value,
            "processor",
            NissanPayPaymentProcessor,
            f"{path}.processor",
        ),
        last_four_digits=_required_nullable_string(value, "last4", f"{path}.last4"),
    )


def _parse_catalog_package(
    value: Mapping[str, object],
    path: str,
) -> NissanStoreCatalogPackage:
    return NissanStoreCatalogPackage(
        short_description=_required_nullable_string(
            value,
            "shortDescription",
            f"{path}.shortDescription",
        ),
        trial_duration=_required_nullable_int(
            value,
            "npTrialDuration",
            f"{path}.npTrialDuration",
        ),
        product_image_url=_required_nullable_string(
            value,
            "productImageUrl",
            f"{path}.productImageUrl",
        ),
        long_description=_required_nullable_string(
            value,
            "longDescription",
            f"{path}.longDescription",
        ),
        selling_models=_parse_nullable_object_list(
            value,
            "sellingModels",
            path,
            _parse_catalog_selling_model,
        ),
        product_id=_required_nullable_string(value, "productId", f"{path}.productId"),
        name=_required_nullable_string(value, "name", f"{path}.name"),
        child_products=_parse_nullable_object_list(
            value,
            "childProducts",
            path,
            _parse_catalog_child_product,
        ),
        is_feature_on_demand=_required_nullable_bool(value, "isFoD", f"{path}.isFoD"),
        promotions=_parse_nullable_object_list(
            value,
            "promotions",
            path,
            _parse_catalog_promotion,
        ),
    )


def _parse_catalog_selling_model(
    value: Mapping[str, object],
    path: str,
) -> NissanStoreCatalogSellingModel:
    return NissanStoreCatalogSellingModel(
        pricing_term_unit=_required_nullable_string(
            value,
            "sellingModelPricingTermUnit",
            f"{path}.sellingModelPricingTermUnit",
        ),
        retail_price=_required_nullable_float(value, "retailPrice", f"{path}.retailPrice"),
        discounted_price=_required_nullable_float(
            value,
            "discountedPrice",
            f"{path}.discountedPrice",
        ),
        selling_model_type=_required_nullable_string(
            value,
            "sellingModelType",
            f"{path}.sellingModelType",
        ),
        selling_model_id=_required_nullable_string(
            value,
            "sellingModelId",
            f"{path}.sellingModelId",
        ),
    )


def _parse_catalog_child_product(
    value: Mapping[str, object],
    path: str,
) -> NissanStoreCatalogChildProduct:
    return NissanStoreCatalogChildProduct(
        name=_required_nullable_string(value, "name", f"{path}.name"),
        customer_facing=_required_nullable_bool(
            value,
            "npCustomerFacing",
            f"{path}.npCustomerFacing",
        ),
    )


def _parse_catalog_promotion(
    value: Mapping[str, object],
    path: str,
) -> NissanStoreCatalogPromotion:
    return NissanStoreCatalogPromotion(
        promotion_id=_required_nullable_string(
            value,
            "promotionId",
            f"{path}.promotionId",
        ),
        priority=_required_nullable_int(value, "priority", f"{path}.priority"),
        name=_required_nullable_string(value, "name", f"{path}.name"),
        monthly_price=_required_nullable_float(
            value,
            "monthlyPromotionPrice",
            f"{path}.monthlyPromotionPrice",
        ),
        annual_price=_required_nullable_float(
            value,
            "annualPromotionPrice",
            f"{path}.annualPromotionPrice",
        ),
        end_date=_required_nullable_string(value, "endDate", f"{path}.endDate"),
        description=_required_nullable_string(
            value,
            "description",
            f"{path}.description",
        ),
    )


def _parse_nullable_object_list[ResultT](
    container: Mapping[str, object],
    field: str,
    parent_path: str,
    parser: Callable[[Mapping[str, object], str], ResultT],
) -> tuple[ResultT | None, ...] | None:
    values = _nullable_list(container, field, f"{parent_path}.{field}")
    if values is None:
        return None
    results: list[ResultT | None] = []
    for index, value in enumerate(values):
        if value is None:
            results.append(None)
            continue
        path = f"{parent_path}.{field}[{index}]"
        results.append(parser(_typed_object(value, path), path))
    return tuple(results)


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


def _nullable_list(
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


def _required_nullable_float(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> float | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ResponseError(f"{path} is not a number")
    return float(value)


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


def _required_nullable_enum[EnumT: StrEnum](
    container: Mapping[str, object],
    field: str,
    enum_type: type[EnumT],
    path: str,
) -> EnumT | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    return _enum(value, enum_type, path)
