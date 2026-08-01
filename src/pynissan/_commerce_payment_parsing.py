from __future__ import annotations

from collections.abc import Mapping

from ._commerce_value_parsing import (
    _required_nullable_datetime,
    _required_nullable_enum,
    _required_nullable_float,
    _required_typed_object,
)
from .account_parsing import (
    _required_nullable_bool,
    _required_nullable_int,
    _required_nullable_string,
    _required_optional_typed_object,
    _required_string,
)
from .commerce_models import (
    NissanPayChargeSessionType,
    NissanPayEnergyChargeSession,
    NissanPayOrderAddress,
    NissanPayOrderPaymentMethod,
    NissanPayPaymentMethodCard,
    NissanPayPaymentMethodStatus,
    NissanPayPaymentProcessor,
    NissanStoreAddedProduct,
    NissanStoreCart,
    NissanStoreDeliveryGroup,
    NissanStorePricingTerm,
    NissanStoreSubscription,
)


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
