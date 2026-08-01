from __future__ import annotations

from collections.abc import Mapping

from .charge_plan_models import (
    ChargePlanAccountStatus,
    ChargePlanCancellationResult,
    ChargePlanEnrollmentData,
    ChargePlanEnrollmentResult,
    ChargePlanPricingConnector,
    ChargePlanPricingDetails,
    ChargePlanPricingEvse,
    ChargeProductData,
    ChargeProductResult,
)
from .exceptions import ResponseError


def parse_charge_product(data: Mapping[str, object]) -> ChargeProductResult | None:
    """Parse the nullable EMP charge product and status envelope."""

    root_field = "chargeProduct"
    root = _root(data, root_field)
    if root is None:
        return None

    raw_product = _optional_typed_object(root.get("data"), f"{root_field}.data")
    product = None
    if raw_product is not None:
        product = ChargeProductData(
            product_sku=_nullable_string(
                raw_product.get("productSKU"),
                f"{root_field}.data.productSKU",
            ),
            price=_nullable_string(
                raw_product.get("price"),
                f"{root_field}.data.price",
            ),
            description=_nullable_string(
                raw_product.get("description"),
                f"{root_field}.data.description",
            ),
        )

    return ChargeProductResult(
        status_code=_nullable_string(root.get("statusCode"), f"{root_field}.statusCode"),
        status_message=_nullable_string(
            root.get("statusMessage"),
            f"{root_field}.statusMessage",
        ),
        timestamp=_nullable_string(root.get("timestamp"), f"{root_field}.timestamp"),
        data=product,
    )


def parse_pricing_details(
    data: Mapping[str, object],
) -> ChargePlanPricingDetails | None:
    """Parse nullable charging-location fees and connector tariffs."""

    root_field = "pricingDetails"
    root = _root(data, root_field)
    if root is None:
        return None

    raw_details = _optional_typed_object(root.get("data"), f"{root_field}.data")
    if raw_details is None:
        return None

    evses_path = f"{root_field}.data.evses"
    raw_evses = _nullable_list(raw_details.get("evses"), evses_path)
    evses: tuple[ChargePlanPricingEvse | None, ...] | None = None
    if raw_evses is not None:
        parsed_evses: list[ChargePlanPricingEvse | None] = []
        for index, raw_evse in enumerate(raw_evses):
            if raw_evse is None:
                parsed_evses.append(None)
                continue
            parsed_evses.append(_parse_pricing_evse(raw_evse, f"{evses_path}[{index}]"))
        evses = tuple(parsed_evses)

    return ChargePlanPricingDetails(
        parking_tariff=_nullable_string(
            raw_details.get("parkingTariff"),
            f"{root_field}.data.parkingTariff",
        ),
        flat_fee=_nullable_string(
            raw_details.get("flatFee"),
            f"{root_field}.data.flatFee",
        ),
        congestion_fee=_nullable_string(
            raw_details.get("congestionFee"),
            f"{root_field}.data.congestionFee",
        ),
        evses=evses,
    )


def parse_enroll_charge_plan(
    data: Mapping[str, object],
) -> ChargePlanEnrollmentResult | None:
    """Parse the nullable EMP charge-plan enrollment result."""

    root_field = "enrollChargePlan"
    root = _root(data, root_field)
    if root is None:
        return None

    raw_enrollment = _optional_typed_object(root.get("data"), f"{root_field}.data")
    enrollment = None
    if raw_enrollment is not None:
        enrollment = ChargePlanEnrollmentData(
            vin=_nullable_string(
                raw_enrollment.get("vin"),
                f"{root_field}.data.vin",
            ),
            status=_nullable_account_status(
                raw_enrollment.get("status"),
                f"{root_field}.data.status",
            ),
        )

    return ChargePlanEnrollmentResult(
        status_code=_nullable_string(root.get("statusCode"), f"{root_field}.statusCode"),
        status_message=_nullable_string(
            root.get("statusMessage"),
            f"{root_field}.statusMessage",
        ),
        timestamp=_nullable_string(root.get("timestamp"), f"{root_field}.timestamp"),
        data=enrollment,
    )


def parse_cancel_charge_plan(
    data: Mapping[str, object],
) -> ChargePlanCancellationResult | None:
    """Parse the nullable EMP charge-plan cancellation result."""

    root_field = "cancelChargePlan"
    root = _root(data, root_field)
    if root is None:
        return None
    return ChargePlanCancellationResult(
        status_code=_nullable_string(root.get("statusCode"), f"{root_field}.statusCode"),
        status_message=_nullable_string(
            root.get("statusMessage"),
            f"{root_field}.statusMessage",
        ),
        timestamp=_nullable_string(root.get("timestamp"), f"{root_field}.timestamp"),
    )


def _parse_pricing_evse(value: object, path: str) -> ChargePlanPricingEvse:
    evse = _typed_object(value, path)
    connectors_path = f"{path}.connectors"
    raw_connectors = _nullable_list(evse.get("connectors"), connectors_path)
    connectors: tuple[ChargePlanPricingConnector | None, ...] | None = None
    if raw_connectors is not None:
        parsed_connectors: list[ChargePlanPricingConnector | None] = []
        for index, raw_connector in enumerate(raw_connectors):
            if raw_connector is None:
                parsed_connectors.append(None)
                continue
            connector_path = f"{connectors_path}[{index}]"
            connector = _typed_object(raw_connector, connector_path)
            parsed_connectors.append(
                ChargePlanPricingConnector(
                    connector_id=_nullable_string(
                        connector.get("connectorId"),
                        f"{connector_path}.connectorId",
                    ),
                    tariff=_nullable_string(
                        connector.get("tariff"),
                        f"{connector_path}.tariff",
                    ),
                )
            )
        connectors = tuple(parsed_connectors)
    return ChargePlanPricingEvse(connectors)


def _root(
    data: Mapping[str, object],
    root_field: str,
) -> Mapping[str, object] | None:
    if root_field not in data:
        raise ResponseError(f"{root_field} is missing")
    return _optional_typed_object(data.get(root_field), root_field)


def _typed_object(value: object, path: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ResponseError(f"{path} is not an object")
    _string(value.get("__typename"), f"{path}.__typename")
    return value


def _optional_typed_object(
    value: object,
    path: str,
) -> Mapping[str, object] | None:
    if value is None:
        return None
    return _typed_object(value, path)


def _nullable_list(value: object, path: str) -> list[object] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        raise ResponseError(f"{path} is not a list")
    return value


def _string(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise ResponseError(f"{path} is not a string")
    return value


def _nullable_string(value: object, path: str) -> str | None:
    if value is None:
        return None
    return _string(value, path)


def _nullable_account_status(
    value: object,
    path: str,
) -> ChargePlanAccountStatus | None:
    raw_value = _nullable_string(value, path)
    if raw_value is None:
        return None
    try:
        return ChargePlanAccountStatus(raw_value)
    except ValueError:
        return ChargePlanAccountStatus.UNKNOWN_VALUE
