from __future__ import annotations

from collections.abc import Mapping

from ._parsing_values import (
    _list,
    _nullable_aware_datetime,
    _nullable_graphql_bool,
    _nullable_graphql_string,
    _nullable_product_type,
    _nullable_purchase_type,
    _object,
    _optional_bool,
    _optional_object,
    _required_aware_datetime,
    _required_datetime,
    _required_float,
    _required_graphql_string,
)
from .models import (
    VehiclePreferences,
    VehicleSubscription,
    VehicleSubscriptionPendingOrder,
    VehicleSubscriptionProduct,
    VehicleSubscriptions,
    VehicleWifiConsumption,
)


def parse_vehicle_wifi_consumption(
    data: Mapping[str, object],
) -> VehicleWifiConsumption | None:
    """Parse nullable vehicle Wi-Fi consumption with required inner fields."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None:
        return None
    capabilities = _optional_object(
        vehicle.get("capabilities"),
        "vehicle.capabilities",
    )
    if capabilities is None:
        return None
    consumption = _optional_object(
        capabilities.get("wifiConsumption"),
        "vehicle.capabilities.wifiConsumption",
    )
    if consumption is None:
        return None
    return VehicleWifiConsumption(
        usage_percent=_required_float(
            consumption.get("usagePercent"),
            "vehicle.capabilities.wifiConsumption.usagePercent",
        ),
        usage_amount_gb=_required_float(
            consumption.get("usageAmount"),
            "vehicle.capabilities.wifiConsumption.usageAmount",
        ),
        data_cap_amount_gb=_required_float(
            consumption.get("dataCapAmount"),
            "vehicle.capabilities.wifiConsumption.dataCapAmount",
        ),
        updated_at=_required_datetime(
            consumption.get("updatedAt"),
            "vehicle.capabilities.wifiConsumption.updatedAt",
        ),
    )


def parse_vehicle_preferences(
    data: Mapping[str, object],
) -> VehiclePreferences | None:
    """Parse nullable MIL/DTC maintenance-data sharing preferences."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None:
        return None
    preferences = _optional_object(
        vehicle.get("preferences"),
        "vehicle.preferences",
    )
    if preferences is None:
        return None
    communication = _optional_object(
        preferences.get("communication"),
        "vehicle.preferences.communication",
    )
    if communication is None:
        return None
    mil_data_sharing = _optional_object(
        communication.get("milDataSharing"),
        "vehicle.preferences.communication.milDataSharing",
    )
    if mil_data_sharing is None:
        return None
    return VehiclePreferences(
        enabled=_optional_bool(mil_data_sharing.get("enabled")),
        text=_optional_bool(mil_data_sharing.get("text")),
        phone=_optional_bool(mil_data_sharing.get("phone")),
        email=_optional_bool(mil_data_sharing.get("email")),
    )


def parse_vehicle_subscriptions(
    data: Mapping[str, object],
    vin: str,
) -> VehicleSubscriptions | None:
    """Parse the vehicle subscription capability without app-level coercion."""

    vehicle = _optional_object(data.get("vehicle"), "vehicle")
    if vehicle is None:
        return None
    _required_graphql_string(vehicle.get("__typename"), "vehicle.__typename")

    capabilities = _optional_object(
        vehicle.get("capabilities"),
        "vehicle.capabilities",
    )
    if capabilities is None:
        return VehicleSubscriptions(vin=vin, subscriptions=None)
    _required_graphql_string(
        capabilities.get("__typename"),
        "vehicle.capabilities.__typename",
    )

    values = _list(
        capabilities.get("subscriptions"),
        "vehicle.capabilities.subscriptions",
    )
    subscriptions: list[VehicleSubscription | None] = []
    for index, raw_subscription in enumerate(values):
        if raw_subscription is None:
            subscriptions.append(None)
            continue
        path = f"vehicle.capabilities.subscriptions[{index}]"
        subscriptions.append(_parse_vehicle_subscription(_object(raw_subscription, path), path))

    return VehicleSubscriptions(vin=vin, subscriptions=tuple(subscriptions))


def _parse_vehicle_subscription(
    value: Mapping[str, object],
    path: str,
) -> VehicleSubscription:
    _required_graphql_string(value.get("__typename"), f"{path}.__typename")
    product_path = f"{path}.product"
    product = _parse_vehicle_subscription_product(
        _object(value.get("product"), product_path),
        product_path,
    )
    pending_order_path = f"{path}.pendingOrder"
    pending_order_value = _optional_object(value.get("pendingOrder"), pending_order_path)
    pending_order = (
        _parse_vehicle_subscription_pending_order(pending_order_value, pending_order_path)
        if pending_order_value is not None
        else None
    )
    return VehicleSubscription(
        subscription_id=_required_graphql_string(
            value.get("subscriptionId"),
            f"{path}.subscriptionId",
        ),
        subscription_service_type=_required_graphql_string(
            value.get("subscriptionServiceType"),
            f"{path}.subscriptionServiceType",
        ),
        purchase_type=_nullable_purchase_type(
            value.get("purchaseType"),
            f"{path}.purchaseType",
        ),
        product_type=_nullable_product_type(
            value.get("productType"),
            f"{path}.productType",
        ),
        next_billing_date=_nullable_aware_datetime(
            value.get("nextBillingDate"),
            f"{path}.nextBillingDate",
        ),
        goodwill_end_date=_nullable_aware_datetime(
            value.get("goodwillEndDate"),
            f"{path}.goodwillEndDate",
        ),
        goodwill_start_date=_nullable_aware_datetime(
            value.get("goodwillStartDate"),
            f"{path}.goodwillStartDate",
        ),
        grace_end_date=_nullable_aware_datetime(
            value.get("graceEndDate"),
            f"{path}.graceEndDate",
        ),
        subscription_start_date=_required_aware_datetime(
            value.get("subscriptionStartDate"),
            f"{path}.subscriptionStartDate",
        ),
        subscription_end_date=_nullable_aware_datetime(
            value.get("subscriptionEndDate"),
            f"{path}.subscriptionEndDate",
        ),
        is_active=_nullable_graphql_bool(value.get("isActive"), f"{path}.isActive"),
        np_subscription_price=_nullable_graphql_string(
            value.get("npSubscriptionPrice"),
            f"{path}.npSubscriptionPrice",
        ),
        product=product,
        pending_order=pending_order,
    )


def _parse_vehicle_subscription_product(
    value: Mapping[str, object],
    path: str,
) -> VehicleSubscriptionProduct:
    _required_graphql_string(value.get("__typename"), f"{path}.__typename")
    raw_services = _list(value.get("services"), f"{path}.services")
    services = tuple(
        None
        if raw_service is None
        else _required_graphql_string(raw_service, f"{path}.services[{index}]")
        for index, raw_service in enumerate(raw_services)
    )
    return VehicleSubscriptionProduct(
        product_id=_required_graphql_string(value.get("productId"), f"{path}.productId"),
        marketing_name=_required_graphql_string(
            value.get("marketingName"),
            f"{path}.marketingName",
        ),
        description=_required_graphql_string(
            value.get("description"),
            f"{path}.description",
        ),
        services=services,
    )


def _parse_vehicle_subscription_pending_order(
    value: Mapping[str, object],
    path: str,
) -> VehicleSubscriptionPendingOrder:
    _required_graphql_string(value.get("__typename"), f"{path}.__typename")
    return VehicleSubscriptionPendingOrder(
        pending_order_id=_required_graphql_string(
            value.get("pendingOrderId"),
            f"{path}.pendingOrderId",
        ),
        package_name=_required_graphql_string(
            value.get("packageName"),
            f"{path}.packageName",
        ),
        activation_date=_nullable_aware_datetime(
            value.get("activationDate"),
            f"{path}.activationDate",
        ),
    )
