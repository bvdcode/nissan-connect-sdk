from __future__ import annotations

from collections.abc import Mapping

from ._extended_vehicle_value_parsing import (
    _list,
    _nullable_bool,
    _nullable_list,
    _nullable_string,
    _optional_typed_object,
    _parse_nullable_int_items,
    _string,
    _typed_object,
)
from .extended_vehicle_models import (
    ShareableCapability,
    ShareableCapabilityGroup,
    TariffCongestionFees,
    TariffCongestionFeeTier,
    TariffDetail,
    TariffEnergyFees,
    TariffEnergyFeeTier,
    TariffIdleFees,
    TariffIdleFeeTier,
    TariffLocalizedText,
    TariffPricingData,
)


def _parse_shareable_capability_group(
    value: object,
    path: str,
) -> ShareableCapabilityGroup:
    group = _typed_object(value, path)
    raw_capabilities = _list(group.get("capabilities"), f"{path}.capabilities")
    capabilities: list[ShareableCapability | None] = []
    for index, raw_capability in enumerate(raw_capabilities):
        if raw_capability is None:
            capabilities.append(None)
            continue
        item_path = f"{path}.capabilities[{index}]"
        capability = _typed_object(raw_capability, item_path)
        capabilities.append(
            ShareableCapability(
                id=_string(capability.get("id"), f"{item_path}.id"),
                name=_nullable_string(capability.get("name"), f"{item_path}.name"),
                shareable=_nullable_bool(
                    capability.get("shareable"),
                    f"{item_path}.shareable",
                ),
            )
        )
    return ShareableCapabilityGroup(
        id=_string(group.get("id"), f"{path}.id"),
        name=_nullable_string(group.get("name"), f"{path}.name"),
        shared=_nullable_bool(group.get("shared"), f"{path}.shared"),
        capabilities=tuple(capabilities),
    )


def _parse_tariff_pricing_data(
    value: Mapping[str, object],
    path: str,
) -> TariffPricingData:
    raw_details = _nullable_list(value.get("tariffDetails"), f"{path}.tariffDetails")
    details: tuple[TariffDetail | None, ...] | None = None
    if raw_details is not None:
        parsed_details: list[TariffDetail | None] = []
        for index, raw_detail in enumerate(raw_details):
            if raw_detail is None:
                parsed_details.append(None)
                continue
            parsed_details.append(
                _parse_tariff_detail(raw_detail, f"{path}.tariffDetails[{index}]")
            )
        details = tuple(parsed_details)
    return TariffPricingData(
        location_id=_nullable_string(value.get("locationId"), f"{path}.locationId"),
        max_charge_limit=_nullable_string(
            value.get("maxChargeLimit"),
            f"{path}.maxChargeLimit",
        ),
        tariff_details=details,
    )


def _parse_tariff_detail(value: object, path: str) -> TariffDetail:
    detail = _typed_object(value, path)
    return TariffDetail(
        connector_type=_nullable_string(
            detail.get("connectorType"),
            f"{path}.connectorType",
        ),
        connector_power=_nullable_string(
            detail.get("connectorPower"),
            f"{path}.connectorPower",
        ),
        session_fee=_nullable_string(detail.get("sessionFee"), f"{path}.sessionFee"),
        alternative_text=_parse_optional_tariff_text(
            detail.get("tariffAltText"),
            f"{path}.tariffAltText",
        ),
        idle_fees=_parse_optional_idle_fees(detail.get("idleFees"), f"{path}.idleFees"),
        congestion_fees=_parse_optional_congestion_fees(
            detail.get("congestionFees"),
            f"{path}.congestionFees",
        ),
        energy_fees=_parse_optional_energy_fees(
            detail.get("energyFees"),
            f"{path}.energyFees",
        ),
    )


def _parse_optional_tariff_text(
    value: object,
    path: str,
) -> TariffLocalizedText | None:
    text = _optional_typed_object(value, path)
    if text is None:
        return None
    return TariffLocalizedText(
        en=_nullable_string(text.get("en"), f"{path}.en"),
        fr=_nullable_string(text.get("fr"), f"{path}.fr"),
    )


def _parse_optional_idle_fees(value: object, path: str) -> TariffIdleFees | None:
    fees = _optional_typed_object(value, path)
    if fees is None:
        return None
    raw_tiers = _nullable_list(fees.get("idleFeesTier"), f"{path}.idleFeesTier")
    tiers: tuple[TariffIdleFeeTier | None, ...] | None = None
    if raw_tiers is not None:
        parsed_tiers: list[TariffIdleFeeTier | None] = []
        for index, raw_tier in enumerate(raw_tiers):
            if raw_tier is None:
                parsed_tiers.append(None)
                continue
            parsed_tiers.append(_parse_idle_fee_tier(raw_tier, f"{path}.idleFeesTier[{index}]"))
        tiers = tuple(parsed_tiers)
    return TariffIdleFees(
        grace_period=_nullable_string(fees.get("gracePeriod"), f"{path}.gracePeriod"),
        tiers=tiers,
    )


def _parse_idle_fee_tier(value: object, path: str) -> TariffIdleFeeTier:
    tier = _typed_object(value, path)
    return TariffIdleFeeTier(
        congestion_level=_nullable_string(
            tier.get("congestionLevel"),
            f"{path}.congestionLevel",
        ),
        time_start=_nullable_string(tier.get("timeStart"), f"{path}.timeStart"),
        time_end=_nullable_string(tier.get("timeEnd"), f"{path}.timeEnd"),
        duration_start=_nullable_string(
            tier.get("durationStart"),
            f"{path}.durationStart",
        ),
        duration_end=_nullable_string(tier.get("durationEnd"), f"{path}.durationEnd"),
        duration_unit=_nullable_string(tier.get("durationUnit"), f"{path}.durationUnit"),
        price=_nullable_string(tier.get("price"), f"{path}.price"),
        unit=_nullable_string(tier.get("unit"), f"{path}.unit"),
    )


def _parse_optional_congestion_fees(
    value: object,
    path: str,
) -> TariffCongestionFees | None:
    fees = _optional_typed_object(value, path)
    if fees is None:
        return None
    raw_tiers = _nullable_list(fees.get("congestionTier"), f"{path}.congestionTier")
    tiers: tuple[TariffCongestionFeeTier | None, ...] | None = None
    if raw_tiers is not None:
        parsed_tiers: list[TariffCongestionFeeTier | None] = []
        for index, raw_tier in enumerate(raw_tiers):
            if raw_tier is None:
                parsed_tiers.append(None)
                continue
            parsed_tiers.append(
                _parse_congestion_fee_tier(raw_tier, f"{path}.congestionTier[{index}]")
            )
        tiers = tuple(parsed_tiers)
    return TariffCongestionFees(
        grace_period=_nullable_string(fees.get("gracePeriod"), f"{path}.gracePeriod"),
        tiers=tiers,
    )


def _parse_congestion_fee_tier(
    value: object,
    path: str,
) -> TariffCongestionFeeTier:
    tier = _typed_object(value, path)
    return TariffCongestionFeeTier(
        congestion_level=_nullable_string(
            tier.get("congestionLevel"),
            f"{path}.congestionLevel",
        ),
        vehicle_soc_limit=_nullable_string(
            tier.get("vehicleSOCLimit"),
            f"{path}.vehicleSOCLimit",
        ),
        price=_nullable_string(tier.get("price"), f"{path}.price"),
        unit=_nullable_string(tier.get("unit"), f"{path}.unit"),
    )


def _parse_optional_energy_fees(value: object, path: str) -> TariffEnergyFees | None:
    fees = _optional_typed_object(value, path)
    if fees is None:
        return None
    raw_tiers = _nullable_list(fees.get("energyFeeTier"), f"{path}.energyFeeTier")
    tiers: tuple[TariffEnergyFeeTier | None, ...] | None = None
    if raw_tiers is not None:
        parsed_tiers: list[TariffEnergyFeeTier | None] = []
        for index, raw_tier in enumerate(raw_tiers):
            if raw_tier is None:
                parsed_tiers.append(None)
                continue
            parsed_tiers.append(_parse_energy_fee_tier(raw_tier, f"{path}.energyFeeTier[{index}]"))
        tiers = tuple(parsed_tiers)
    return TariffEnergyFees(tiers=tiers)


def _parse_energy_fee_tier(value: object, path: str) -> TariffEnergyFeeTier:
    tier = _typed_object(value, path)
    applicable_day = _parse_nullable_int_items(
        tier.get("applicableDay"),
        f"{path}.applicableDay",
    )
    return TariffEnergyFeeTier(
        applicable_day=applicable_day,
        time_start=_nullable_string(tier.get("timeStart"), f"{path}.timeStart"),
        time_end=_nullable_string(tier.get("timeEnd"), f"{path}.timeEnd"),
        duration_start=_nullable_string(
            tier.get("durationStart"),
            f"{path}.durationStart",
        ),
        duration_end=_nullable_string(tier.get("durationEnd"), f"{path}.durationEnd"),
        duration_unit=_nullable_string(tier.get("durationUnit"), f"{path}.durationUnit"),
        min_range=_nullable_string(tier.get("minRange"), f"{path}.minRange"),
        max_range=_nullable_string(tier.get("maxRange"), f"{path}.maxRange"),
        range_unit=_nullable_string(tier.get("rangeUnit"), f"{path}.rangeUnit"),
        price=_nullable_string(tier.get("price"), f"{path}.price"),
        unit=_nullable_string(tier.get("unit"), f"{path}.unit"),
    )
