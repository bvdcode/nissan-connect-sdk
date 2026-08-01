from __future__ import annotations

from collections.abc import Mapping

from ._commerce_catalog_parsing import _parse_catalog_package
from ._commerce_payment_parsing import (
    _parse_added_cart,
    _parse_added_product,
    _parse_energy_charge_session,
    _parse_payment_card,
)
from ._commerce_value_parsing import (
    _nullable_list,
    _required_list,
    _required_nullable_datetime,
    _required_typed_object,
)
from .account_parsing import (
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
    NissanPayOrder,
    NissanPayOrderHistory,
    NissanPayOrderHistoryPagination,
    NissanPayPaymentMethod,
    NissanStoreCatalogPackage,
    NissanStoreProductCatalog,
    ProductAddedToNissanStoreCart,
    ProductCatalogResult,
    UnselectedCommerceResult,
    UpsertNissanPayAccountFailure,
    UpsertNissanPayAccountResult,
    UpsertNissanPayAccountSuccess,
)


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
