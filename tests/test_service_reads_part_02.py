from __future__ import annotations

from collections.abc import Callable, Mapping

import pytest
from test_service_reads import (
    preferred_dealer,
    recall,
    service_history_entry,
    vehicle_data,
    warranty,
    without_field,
)

from pynissan import (
    ResponseError,
)
from pynissan.service_parsing import (
    parse_vehicle_preferred_dealer,
    parse_vehicle_recalls,
    parse_vehicle_roadside_assistance,
    parse_vehicle_service_history,
    parse_warranty_info,
)


@pytest.mark.parametrize(
    ("parser", "payload"),
    [
        (parse_vehicle_preferred_dealer, {}),
        (
            parse_vehicle_preferred_dealer,
            vehicle_data(preferredDealer=preferred_dealer(languagesSpoken=None)),
        ),
        (
            parse_vehicle_preferred_dealer,
            vehicle_data(preferredDealer=preferred_dealer(languagesSpoken=[None])),
        ),
        (parse_vehicle_recalls, vehicle_data(recalls=None)),
        (parse_vehicle_recalls, vehicle_data(recalls=[None])),
        (
            parse_vehicle_recalls,
            vehicle_data(recalls=[without_field(recall(), "title")]),
        ),
        (
            parse_vehicle_roadside_assistance,
            vehicle_data(
                roadsideAssistance={
                    "__typename": "RoadsideAssistance",
                    "roadsideMonths": None,
                    "roadsideMiles": None,
                    "towingMonths": None,
                }
            ),
        ),
        (parse_vehicle_service_history, vehicle_data(serviceHistory=None)),
        (parse_vehicle_service_history, vehicle_data(serviceHistory=[None])),
        (
            parse_vehicle_service_history,
            vehicle_data(serviceHistory=[service_history_entry(services=None)]),
        ),
        (
            parse_vehicle_service_history,
            vehicle_data(serviceHistory=[service_history_entry(services=[None])]),
        ),
        (
            parse_warranty_info,
            vehicle_data(warranty=warranty(warrantyInfo=None)),
        ),
        (
            parse_warranty_info,
            vehicle_data(warranty=warranty(startPeriod=None)),
        ),
    ],
)
def test_required_fields_and_non_null_lists_reject_invalid_responses(
    parser: Callable[[Mapping[str, object]], object],
    payload: Mapping[str, object],
) -> None:
    with pytest.raises(ResponseError):
        parser(payload)


@pytest.mark.parametrize(
    ("parser", "payload"),
    [
        (
            parse_vehicle_recalls,
            vehicle_data(recalls=[recall(effectiveDate="2026-02-03T04:05:06")]),
        ),
        (
            parse_vehicle_service_history,
            vehicle_data(serviceHistory=[service_history_entry(serviceDate="2026-03-04T05:06:07")]),
        ),
    ],
)
def test_datetime_scalars_require_an_explicit_offset(
    parser: Callable[[Mapping[str, object]], object],
    payload: Mapping[str, object],
) -> None:
    with pytest.raises(ResponseError, match="with an offset"):
        parser(payload)


@pytest.mark.parametrize("raw_date", ["2026-02-30", "2026-03-04T05:06:07Z"])
def test_warranty_date_scalars_reject_invalid_dates(raw_date: str) -> None:
    invalid_period = {
        "__typename": "WarrantyPeriod",
        "mileage": 0,
        "date": raw_date,
    }
    with pytest.raises(ResponseError, match="ISO-8601 date"):
        parse_warranty_info(vehicle_data(warranty=warranty(startPeriod=invalid_period)))
