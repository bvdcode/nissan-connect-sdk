from __future__ import annotations

from . import operations
from ._client_base import _NissanClientBase
from .commerce_inputs import (
    AddProductToCartInput,
    CancelSubscriptionInput,
    ProductCatalogInput,
    add_product_to_cart_variables,
    cancel_pending_subscription_variables,
    cancel_subscription_variables,
    nissan_pay_order_history_variables,
    nissan_store_link_variables,
    product_catalog_variables,
)
from .commerce_models import (
    AddProductToCartResult,
    CancelPendingSubscriptionResult,
    CancelSubscriptionResult,
    NissanPayAccount,
    NissanPayOrderHistory,
    NissanStoreClientOrigin,
    ProductCatalogResult,
    UnselectedCommerceResult,
    UpsertNissanPayAccountResult,
)
from .commerce_parsing import (
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
from .content_inputs import contact_us_variables, faq_variables, live_chat_hours_variables
from .content_models import (
    CertifiedPreOwnedDetails,
    ClientType,
    ContactUsInfo,
    FrequentlyAskedQuestionCategory,
    LiveChatHours,
    MobileCarrier,
)
from .content_parsing import (
    parse_contact_us,
    parse_cpo_details,
    parse_faq,
    parse_live_chat_hours,
    parse_mobile_carriers,
)
from .graphql_input import UNSET, UnsetType


class _ContentClientMixin(_NissanClientBase):
    async def async_get_contact_us(
        self,
        client_type: ClientType = ClientType.ANDROID,
    ) -> ContactUsInfo:
        """Return account, ownership, and support contact information."""

        data = await self._transport.async_graphql(
            "ContactUs",
            operations.CONTACT_US,
            contact_us_variables(client_type),
        )
        return parse_contact_us(data)

    async def async_get_cpo_details(self) -> CertifiedPreOwnedDetails | None:
        """Return certified-pre-owned provider details."""

        data = await self._transport.async_graphql(
            "CpoDetails",
            operations.CPO_DETAILS,
            {},
        )
        return parse_cpo_details(data)

    async def async_get_faq(
        self,
        categories: tuple[str | None, ...] | UnsetType | None = UNSET,
    ) -> tuple[FrequentlyAskedQuestionCategory, ...]:
        """Return FAQ categories, optionally filtered by category name."""

        data = await self._transport.async_graphql(
            "FAQ",
            operations.FAQ,
            faq_variables(categories),
        )
        return parse_faq(data)

    async def async_get_live_chat_hours(
        self,
        departments: tuple[str | None, ...] | UnsetType | None = UNSET,
        enhanced_chat: bool | UnsetType | None = UNSET,
    ) -> tuple[LiveChatHours | None, ...] | None:
        """Return nullable live-chat hours for selected departments."""

        data = await self._transport.async_graphql(
            "LiveChatHours",
            operations.LIVE_CHAT_HOURS,
            live_chat_hours_variables(departments, enhanced_chat),
        )
        return parse_live_chat_hours(data)

    async def async_get_mobile_carriers(self) -> tuple[MobileCarrier, ...]:
        """Return the mobile-carrier catalog used by account profiles."""

        data = await self._transport.async_graphql(
            "MobileCarriers",
            operations.MOBILE_CARRIERS,
            {},
        )
        return parse_mobile_carriers(data)

    async def async_add_product_to_nissan_store_cart(
        self,
        config: AddProductToCartInput,
    ) -> AddProductToCartResult | None:
        """Add a selected product and selling model to Nissan Store cart."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "AddProductToNissanStoreCart",
            operations.ADD_PRODUCT_TO_NISSAN_STORE_CART,
            add_product_to_cart_variables(config),
        )
        return parse_add_product_to_cart(data)

    async def async_cancel_pending_subscription(
        self,
        pending_order_id: str,
    ) -> CancelPendingSubscriptionResult | UnselectedCommerceResult:
        """Cancel a pending subscription order."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CancelPendingSubscription",
            operations.CANCEL_PENDING_SUBSCRIPTION,
            cancel_pending_subscription_variables(pending_order_id),
        )
        return parse_cancel_pending_subscription(data)

    async def async_cancel_subscription(
        self,
        config: CancelSubscriptionInput,
    ) -> CancelSubscriptionResult | None:
        """Cancel an active Nissan Store subscription."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CancelSubscription",
            operations.CANCEL_SUBSCRIPTION,
            cancel_subscription_variables(config),
        )
        return parse_cancel_subscription(data)

    async def async_create_nissan_store_fod_trial_checkout_link(
        self,
        vin: str,
        client_origin: NissanStoreClientOrigin = NissanStoreClientOrigin.ONE_APP,
    ) -> str | None:
        """Create a feature-on-demand trial checkout link."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "CreateNissanStoreFODTrialCheckoutLink",
            operations.CREATE_NISSAN_STORE_FOD_TRIAL_CHECKOUT_LINK,
            nissan_store_link_variables(vin, client_origin),
        )
        return parse_trial_checkout_link(data)

    async def async_get_digital_wallet_url(self) -> str | None:
        """Return the nullable Nissan Pay digital-wallet URL."""

        data = await self._transport.async_graphql(
            "DigitalWalletURL",
            operations.DIGITAL_WALLET_URL,
            {},
        )
        return parse_digital_wallet_url(data)

    async def async_get_nissan_pay(self) -> NissanPayAccount | None:
        """Return Nissan Pay methods and digital-wallet information."""

        data = await self._transport.async_graphql(
            "NissanPay",
            operations.NISSAN_PAY,
            {},
        )
        return parse_nissan_pay(data)

    async def async_get_nissan_pay_order_history(
        self,
        vin: str,
        page_cursor: str | UnsetType | None = UNSET,
    ) -> NissanPayOrderHistory | None:
        """Return paginated Nissan Pay energy order history."""

        data = await self._transport.async_graphql(
            "NissanPayOrderHistory",
            operations.NISSAN_PAY_ORDER_HISTORY,
            nissan_pay_order_history_variables(vin, page_cursor),
        )
        return parse_nissan_pay_order_history(data)

    async def async_get_nissan_store_checkout_url(
        self,
        vin: str,
        client_origin: NissanStoreClientOrigin = NissanStoreClientOrigin.ONE_APP,
    ) -> str | None:
        """Return the nullable checkout URL for a vehicle."""

        data = await self._transport.async_graphql(
            "NissanStoreCheckoutURL",
            operations.NISSAN_STORE_CHECKOUT_URL,
            nissan_store_link_variables(vin, client_origin),
        )
        return parse_nissan_store_checkout_url(data)

    async def async_get_product_catalog(
        self,
        config: ProductCatalogInput,
    ) -> ProductCatalogResult | None:
        """Return Nissan Store product packages for an optional vehicle."""

        data = await self._transport.async_graphql(
            "ProductCatalog",
            operations.PRODUCT_CATALOG,
            product_catalog_variables(config),
        )
        return parse_product_catalog(data)

    async def async_upsert_nissan_pay_account(
        self,
    ) -> UpsertNissanPayAccountResult | None:
        """Create or synchronize the signed-in Nissan Pay account."""

        self._ensure_write_allowed()
        data = await self._transport.async_graphql(
            "UpsertNissanPayAccount",
            operations.UPSERT_NISSAN_PAY_ACCOUNT,
            {},
        )
        return parse_upsert_nissan_pay_account(data)
