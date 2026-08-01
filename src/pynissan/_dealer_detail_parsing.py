from __future__ import annotations

from collections.abc import Mapping

from ._dealer_value_parsing import (
    _nullable_list,
    _optional_selected_nullable_bool,
    _optional_selected_nullable_list,
    _optional_selected_nullable_string,
    _required_bool,
    _required_nullable_float,
    _required_string_list,
)
from .account_parsing import (
    _enum,
    _required_field,
    _required_nullable_bool,
    _required_nullable_int,
    _required_nullable_string,
    _required_optional_typed_object,
    _required_string,
)
from .dealer_models import (
    Dealer,
    DealerCoupon,
    DealerCouponImage,
    DealerSchedule,
    DealerServiceSchedule,
    DealerSummary,
    MaintenanceInterval,
    MaintenanceServiceOccurrence,
    MaintenanceVisit,
    MaintenanceVisitAlignment,
)
from .exceptions import ResponseError


def _parse_dealer_summary(value: Mapping[str, object], path: str) -> DealerSummary:
    return DealerSummary(
        dealer_id=_required_nullable_string(value, "dealerId", f"{path}.dealerId"),
        name=_required_nullable_string(value, "dealerName", f"{path}.dealerName"),
        address_line_1=_required_nullable_string(
            value,
            "dealerAddressLine1",
            f"{path}.dealerAddressLine1",
        ),
    )


def _parse_dealer(value: Mapping[str, object], path: str) -> Dealer:
    return Dealer(
        dealer_id=_required_nullable_string(value, "dealerId", f"{path}.dealerId"),
        name=_required_nullable_string(value, "dealerName", f"{path}.dealerName"),
        preferred=_optional_selected_nullable_bool(value, "isDealerPreferred", path),
        address_line_1=_required_nullable_string(
            value,
            "dealerAddressLine1",
            f"{path}.dealerAddressLine1",
        ),
        address_line_2=_optional_selected_nullable_string(value, "dealerAddressLine2", path),
        latitude=_required_nullable_float(value, "dealerLatitude", f"{path}.dealerLatitude"),
        longitude=_required_nullable_float(value, "dealerLongitude", f"{path}.dealerLongitude"),
        postal_code=_optional_selected_nullable_string(value, "dealerZip", path),
        country=_optional_selected_nullable_string(value, "dealerCountry", path),
        state_code=_optional_selected_nullable_string(value, "dealerStateCode", path),
        native_service_booking=_required_bool(
            value,
            "nativeServiceBooking",
            f"{path}.nativeServiceBooking",
        ),
        online_scheduling_mobile_url=_optional_selected_nullable_string(
            value,
            "dealerOnlineSchedulingMobileUrl",
            path,
        ),
        city_name=_optional_selected_nullable_string(value, "dealerCityName", path),
        phone_number=_optional_selected_nullable_string(value, "dealerPhoneNumber", path),
        service_phone=_optional_selected_nullable_string(value, "dealerServicePhone", path),
        website=_optional_selected_nullable_string(value, "dealerWebsite", path),
        languages_spoken=(
            None
            if "languagesSpoken" not in value
            else _required_string_list(value, "languagesSpoken", path)
        ),
        email_address=_optional_selected_nullable_string(value, "dealerEmailAddress", path),
        service_hours=_optional_selected_nullable_string(value, "dealerServiceHours", path),
        service_schedules=_optional_selected_nullable_list(
            value,
            "dealerServicesSchedules",
            path,
            _parse_dealer_service_schedule,
        ),
    )


def _parse_dealer_service_schedule(
    value: Mapping[str, object],
    path: str,
) -> DealerServiceSchedule:
    return DealerServiceSchedule(
        code=_optional_selected_nullable_string(value, "code", path),
        name=_required_nullable_string(value, "name", f"{path}.name"),
        schedules=_nullable_list(value, "schedules", f"{path}.schedules", _parse_dealer_schedule),
    )


def _parse_dealer_schedule(value: Mapping[str, object], path: str) -> DealerSchedule:
    return DealerSchedule(
        day_of_week=_required_string(value, "dayOfWeek", f"{path}.dayOfWeek"),
        end_time=_required_nullable_string(value, "endTime", f"{path}.endTime"),
        opened=_required_bool(value, "opened", f"{path}.opened"),
        start_time=_required_nullable_string(value, "startTime", f"{path}.startTime"),
    )


def _parse_coupon(value: Mapping[str, object], path: str) -> DealerCoupon:
    return DealerCoupon(
        coupon_id=_required_nullable_string(value, "couponId", f"{path}.couponId"),
        title=_required_nullable_string(value, "couponTitle", f"{path}.couponTitle"),
        disclaimer=_required_nullable_string(
            value,
            "standardDisclaimer",
            f"{path}.standardDisclaimer",
        ),
    )


def _parse_coupon_image(value: Mapping[str, object], path: str) -> DealerCouponImage:
    return DealerCouponImage(
        coupon_id=_required_nullable_string(value, "couponId", f"{path}.couponId"),
        image_url=_required_nullable_string(value, "couponImageUrl", f"{path}.couponImageUrl"),
    )


def _parse_maintenance_visit(value: Mapping[str, object], path: str) -> MaintenanceVisit:
    alignment = _required_field(value, "Alignment", f"{path}.Alignment")
    interval_path = f"{path}.Interval"
    interval = _required_optional_typed_object(value, "Interval", interval_path)
    return MaintenanceVisit(
        alignment=(
            None
            if alignment is None
            else _enum(alignment, MaintenanceVisitAlignment, f"{path}.Alignment")
        ),
        interval=(
            None
            if interval is None
            else MaintenanceInterval(
                month=_required_nullable_int(interval, "Month", f"{interval_path}.Month"),
                year=_required_nullable_int(interval, "Year", f"{interval_path}.Year"),
                next=_required_nullable_bool(interval, "Next", f"{interval_path}.Next"),
                distance_miles=_required_nullable_int(
                    interval,
                    "DistanceMiles",
                    f"{interval_path}.DistanceMiles",
                ),
                distance_km=_required_nullable_int(
                    interval,
                    "DistanceKMs",
                    f"{interval_path}.DistanceKMs",
                ),
            )
        ),
        service_occurrences=_nullable_list(
            value,
            "ServiceOccurrences",
            f"{path}.ServiceOccurrences",
            _parse_maintenance_occurrence,
        ),
    )


def _parse_maintenance_occurrence(
    value: Mapping[str, object],
    path: str,
) -> MaintenanceServiceOccurrence:
    component_path = f"{path}.ServiceComponent"
    component = _required_optional_typed_object(value, "ServiceComponent", component_path)
    component_name = None
    category_name = None
    if component is not None:
        component_name = _required_nullable_string(
            component,
            "ServiceComponentName",
            f"{component_path}.ServiceComponentName",
        )
        category_path = f"{component_path}.ServiceCategory"
        category = _required_optional_typed_object(component, "ServiceCategory", category_path)
        if category is not None:
            category_name = _required_string(
                category,
                "ServiceCategoryName",
                f"{category_path}.ServiceCategoryName",
            )
    service_type_path = f"{path}.ServiceType"
    service_type = _required_optional_typed_object(value, "ServiceType", service_type_path)
    if service_type is None:
        raise ResponseError(f"{service_type_path} is null")
    group_path = f"{service_type_path}.ServiceTypeGroup"
    group = _required_optional_typed_object(service_type, "ServiceTypeGroup", group_path)
    if group is None:
        raise ResponseError(f"{group_path} is null")
    return MaintenanceServiceOccurrence(
        component_name,
        category_name,
        _required_string(
            service_type,
            "ServiceTypeName",
            f"{service_type_path}.ServiceTypeName",
        ),
        _required_string(group, "ServiceTypeGroupName", f"{group_path}.ServiceTypeGroupName"),
    )
