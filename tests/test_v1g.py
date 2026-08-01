from __future__ import annotations

import hashlib
import re
from collections.abc import Callable, Mapping

import pytest

from pynissan.exceptions import ResponseError
from pynissan.graphql_input import UNSET
from pynissan.operations import (
    V1G_CANCEL_MONITORED_CHARGING_PLAN,
    V1G_CANCEL_MONITORED_CHARGING_PLAN_OPERATION_ID,
    V1G_ENROLL_MONITORED_CHARGING_PLAN,
    V1G_ENROLL_MONITORED_CHARGING_PLAN_OPERATION_ID,
    V1G_MONITORED_CHARGING_ACCOUNT_STATUS,
    V1G_MONITORED_CHARGING_ACCOUNT_STATUS_OPERATION_ID,
    V1G_TOKENIZED_URL,
    V1G_TOKENIZED_URL_OPERATION_ID,
    V1G_UPDATE_NOTIFICATION_PREFERENCES,
    V1G_UPDATE_NOTIFICATION_PREFERENCES_OPERATION_ID,
)
from pynissan.v1g_inputs import (
    V1GNotificationCategory,
    V1GNotificationPreferenceInput,
    v1g_cancel_monitored_charging_plan_variables,
    v1g_enroll_monitored_charging_plan_variables,
    v1g_monitored_charging_account_status_variables,
    v1g_tokenized_url_variables,
    v1g_update_notification_preferences_variables,
)
from pynissan.v1g_models import (
    V1GAccountStatus,
    V1GMonitoredChargingAccountData,
    V1GMonitoredChargingAccountStatusResult,
    V1GMonitoredChargingPlanCancellationResult,
    V1GMonitoredChargingPlanEnrollmentData,
    V1GMonitoredChargingPlanEnrollmentResult,
    V1GNotificationPreference,
    V1GNotificationPreferencesUpdateResult,
    V1GTokenizedUrlData,
    V1GTokenizedUrlResult,
)
from pynissan.v1g_parsing import (
    parse_v1g_cancel_monitored_charging_plan,
    parse_v1g_enroll_monitored_charging_plan,
    parse_v1g_monitored_charging_account_status,
    parse_v1g_tokenized_url,
    parse_v1g_update_notification_preferences,
)

type V1GParser = Callable[[Mapping[str, object]], object]

OPERATION_CONTRACTS = (
    (
        V1G_MONITORED_CHARGING_ACCOUNT_STATUS,
        V1G_MONITORED_CHARGING_ACCOUNT_STATUS_OPERATION_ID,
        "0e1f8a5c0609423deb46c97710a93be95e174690f384c42723d13309f78b9ae9",
    ),
    (
        V1G_UPDATE_NOTIFICATION_PREFERENCES,
        V1G_UPDATE_NOTIFICATION_PREFERENCES_OPERATION_ID,
        "8ff5410e7f19803fe6852039984932e6de80f57679b4a75eddcf04f25211fcaa",
    ),
    (
        V1G_TOKENIZED_URL,
        V1G_TOKENIZED_URL_OPERATION_ID,
        "60f3b2476b14301438b34bcf2368f2eb14efd82a743f0f18c7deb6b158bc6ced",
    ),
    (
        V1G_ENROLL_MONITORED_CHARGING_PLAN,
        V1G_ENROLL_MONITORED_CHARGING_PLAN_OPERATION_ID,
        "8741790f53b6d85416f6fd634c4912a0a8af76411d38373d4b99abfbd94a4458",
    ),
    (
        V1G_CANCEL_MONITORED_CHARGING_PLAN,
        V1G_CANCEL_MONITORED_CHARGING_PLAN_OPERATION_ID,
        "a64cf29b9ef88e15edd58ebb9554073e79d5d3605ddd8b0722e90c0bcf72e2a6",
    ),
)


@pytest.mark.parametrize(("document", "operation_id", "token_hash"), OPERATION_CONTRACTS)
def test_v1g_operations_match_exact_persisted_contracts(
    document: str,
    operation_id: str,
    token_hash: str,
) -> None:
    tokens = " ".join(re.findall(r"\.\.\.|[_A-Za-z][_0-9A-Za-z]*|[$!():{}\[\]]", document))

    assert hashlib.sha256(document.encode()).hexdigest() == operation_id
    assert hashlib.sha256(tokens.encode()).hexdigest() == token_hash


def test_v1g_read_and_cancel_variables_use_exact_shapes() -> None:
    assert v1g_monitored_charging_account_status_variables("VIN") == {"vin": "VIN"}
    assert v1g_tokenized_url_variables("VIN") == {"vin": "VIN"}
    assert v1g_cancel_monitored_charging_plan_variables("VIN") == {"config": {"vin": "VIN"}}


def test_v1g_known_categories_and_account_states_are_exact() -> None:
    assert tuple(V1GNotificationCategory) == (
        V1GNotificationCategory.NEW_PRIME_TIME_HOURS,
        V1GNotificationCategory.PRIME_TIME_UPCOMING_REMINDER,
        V1GNotificationCategory.MONTHLY_INSIGHTS,
        V1GNotificationCategory.PRIME_TIME_STATS_UPDATES,
    )
    assert tuple(category.value for category in V1GNotificationCategory) == (
        "New PrimeTime Hours",
        "PrimeTime Upcoming Reminder",
        "Monthly Insights",
        "PrimeTime Stats Updates",
    )
    assert tuple(V1GAccountStatus) == (
        V1GAccountStatus.FAILED,
        V1GAccountStatus.ACTIVE,
        V1GAccountStatus.INACTIVE,
        V1GAccountStatus.ENROLLING,
        V1GAccountStatus.NOT_ENROLLED,
        V1GAccountStatus.CANCELLED,
        V1GAccountStatus.CLOSED,
        V1GAccountStatus.UNKNOWN_VALUE,
    )


def test_v1g_update_variables_preserve_all_apollo_optional_states() -> None:
    assert v1g_update_notification_preferences_variables("VIN") == {"config": {"vin": "VIN"}}
    assert v1g_update_notification_preferences_variables(
        "VIN",
        preferences=None,
    ) == {"config": {"vin": "VIN", "v1GNotificationPreferences": None}}
    assert v1g_update_notification_preferences_variables(
        "VIN",
        preferences=(),
    ) == {"config": {"vin": "VIN", "v1GNotificationPreferences": []}}

    variables = v1g_update_notification_preferences_variables(
        "VIN",
        preferences=(
            None,
            V1GNotificationPreferenceInput(
                V1GNotificationCategory.NEW_PRIME_TIME_HOURS,
                email_status=UNSET,
                push_status=None,
                sms_status=True,
            ),
            V1GNotificationPreferenceInput("Future category", email_status=False),
        ),
    )

    assert variables == {
        "config": {
            "vin": "VIN",
            "v1GNotificationPreferences": [
                None,
                {
                    "v1GNotificationCategory": "New PrimeTime Hours",
                    "v1GPushStatus": None,
                    "v1GSmsStatus": True,
                },
                {
                    "v1GNotificationCategory": "Future category",
                    "v1GEmailStatus": False,
                },
            ],
        }
    }


def test_v1g_enrollment_plan_has_no_hidden_default() -> None:
    assert v1g_enroll_monitored_charging_plan_variables("VIN", "ARIYA", "2025") == {
        "config": {"vin": "VIN", "model": "ARIYA", "year": "2025"}
    }
    assert v1g_enroll_monitored_charging_plan_variables(
        "VIN",
        "ARIYA",
        "2025",
        plan=None,
    ) == {"config": {"vin": "VIN", "plan": None, "model": "ARIYA", "year": "2025"}}
    assert v1g_enroll_monitored_charging_plan_variables(
        "VIN",
        "ARIYA",
        "2025",
        plan="V1G-MC1",
    ) == {
        "config": {
            "vin": "VIN",
            "plan": "V1G-MC1",
            "model": "ARIYA",
            "year": "2025",
        }
    }


def test_parse_v1g_account_status_preserves_raw_payload_and_future_values() -> None:
    data = {
        "v1GMonitoredChargingAccountStatus": {
            "__typename": "V1GMonitoredChargingAccountStatusResponse",
            "statusCode": "5000",
            "data": {
                "__typename": "V1GMonitoredChargingAccountStatusData",
                "v1GMonitoredChargingAccountStatus": "FUTURE_STATUS",
                "v1GNotificationPreferences": [
                    None,
                    {
                        "__typename": "V1GNotificationPreferencesData",
                        "v1GNotificationCategory": "Future category",
                        "v1GEmailStatus": True,
                        "v1GPushStatus": None,
                        "v1GSmsStatus": False,
                    },
                ],
                "vin": None,
            },
        }
    }

    result = parse_v1g_monitored_charging_account_status(data)

    assert result == V1GMonitoredChargingAccountStatusResult(
        status_code="5000",
        data=V1GMonitoredChargingAccountData(
            account_status=V1GAccountStatus.UNKNOWN_VALUE,
            notification_preferences=(
                None,
                V1GNotificationPreference("Future category", True, None, False),
            ),
            vin=None,
        ),
    )
    assert result.is_success is False


def test_parse_v1g_update_preserves_nullable_preference_items() -> None:
    data = {
        "v1GUpdateNotificationPreferences": {
            "__typename": "V1GUpdateNotificationPreferencesResponse",
            "statusCode": "1000",
            "statusMessage": None,
            "timestamp": "2026-07-31T12:00:00Z",
            "v1GNotificationPreferences": [
                None,
                {
                    "__typename": "V1GNotificationPreferencesData",
                    "v1GNotificationCategory": None,
                    "v1GEmailStatus": None,
                    "v1GPushStatus": True,
                    "v1GSmsStatus": False,
                },
            ],
        }
    }

    result = parse_v1g_update_notification_preferences(data)

    assert result == V1GNotificationPreferencesUpdateResult(
        status_code="1000",
        status_message=None,
        timestamp="2026-07-31T12:00:00Z",
        notification_preferences=(
            None,
            V1GNotificationPreference(None, None, True, False),
        ),
    )
    assert result.is_success is True


def test_parse_v1g_tokenized_url_and_enrollment_keep_raw_wrappers() -> None:
    url_result = parse_v1g_tokenized_url(
        {
            "v1GTokenizedUrl": {
                "__typename": "V1GTokenizedUrlResponse",
                "data": {
                    "__typename": "V1GTokenizedUrlData",
                    "url": "https://example.invalid/token",
                    "vin": "VIN",
                },
            }
        }
    )
    enrollment_result = parse_v1g_enroll_monitored_charging_plan(
        {
            "v1GEnrollMonitoredChargingPlan": {
                "__typename": "V1GEnrollMonitoredChargingPlanResponse",
                "data": {
                    "__typename": "V1GEnrollMonitoredChargingPlanData",
                    "v1GMonitoredChargingAccountStatus": "ACTIVE",
                },
            }
        }
    )

    assert url_result == V1GTokenizedUrlResult(
        V1GTokenizedUrlData("https://example.invalid/token", "VIN")
    )
    assert enrollment_result == V1GMonitoredChargingPlanEnrollmentResult(
        V1GMonitoredChargingPlanEnrollmentData(V1GAccountStatus.ACTIVE)
    )
    assert not hasattr(url_result, "is_success")
    assert not hasattr(enrollment_result, "is_success")


@pytest.mark.parametrize(
    ("status_code", "expected"),
    (("1000", True), ("5000", False), (None, False), ("", False)),
)
def test_v1g_business_success_requires_exact_code_1000(
    status_code: str | None,
    expected: bool,
) -> None:
    account = V1GMonitoredChargingAccountStatusResult(status_code, None)
    update = V1GNotificationPreferencesUpdateResult(status_code, None, None, None)
    cancellation = V1GMonitoredChargingPlanCancellationResult(status_code)

    assert account.is_success is expected
    assert update.is_success is expected
    assert cancellation.is_success is expected


@pytest.mark.parametrize(
    ("parser", "root_field"),
    (
        (
            parse_v1g_monitored_charging_account_status,
            "v1GMonitoredChargingAccountStatus",
        ),
        (parse_v1g_update_notification_preferences, "v1GUpdateNotificationPreferences"),
        (parse_v1g_tokenized_url, "v1GTokenizedUrl"),
        (
            parse_v1g_enroll_monitored_charging_plan,
            "v1GEnrollMonitoredChargingPlan",
        ),
        (
            parse_v1g_cancel_monitored_charging_plan,
            "v1GCancelMonitoredChargingPlan",
        ),
    ),
)
def test_v1g_parsers_accept_nullable_root(
    parser: V1GParser,
    root_field: str,
) -> None:
    assert parser({root_field: None}) is None


def test_v1g_parsers_preserve_nullable_nested_objects_and_lists() -> None:
    account = parse_v1g_monitored_charging_account_status(
        {
            "v1GMonitoredChargingAccountStatus": {
                "__typename": "AccountResponse",
                "statusCode": None,
                "data": None,
            }
        }
    )
    update = parse_v1g_update_notification_preferences(
        {
            "v1GUpdateNotificationPreferences": {
                "__typename": "UpdateResponse",
                "statusCode": None,
                "statusMessage": None,
                "timestamp": None,
                "v1GNotificationPreferences": None,
            }
        }
    )
    url = parse_v1g_tokenized_url({"v1GTokenizedUrl": {"__typename": "UrlResponse", "data": None}})
    enrollment = parse_v1g_enroll_monitored_charging_plan(
        {
            "v1GEnrollMonitoredChargingPlan": {
                "__typename": "EnrollmentResponse",
                "data": None,
            }
        }
    )

    assert account == V1GMonitoredChargingAccountStatusResult(None, None)
    assert update == V1GNotificationPreferencesUpdateResult(None, None, None, None)
    assert url == V1GTokenizedUrlResult(None)
    assert enrollment == V1GMonitoredChargingPlanEnrollmentResult(None)


@pytest.mark.parametrize(
    ("parser", "payload", "message"),
    (
        (
            parse_v1g_monitored_charging_account_status,
            {},
            "v1GMonitoredChargingAccountStatus is missing",
        ),
        (
            parse_v1g_monitored_charging_account_status,
            {"v1GMonitoredChargingAccountStatus": {"statusCode": None, "data": None}},
            "__typename is missing",
        ),
        (
            parse_v1g_monitored_charging_account_status,
            {
                "v1GMonitoredChargingAccountStatus": {
                    "__typename": "AccountResponse",
                    "data": None,
                }
            },
            "statusCode is missing",
        ),
        (
            parse_v1g_update_notification_preferences,
            {
                "v1GUpdateNotificationPreferences": {
                    "__typename": "UpdateResponse",
                    "statusCode": "1000",
                    "statusMessage": None,
                    "timestamp": None,
                    "v1GNotificationPreferences": {},
                }
            },
            "v1GNotificationPreferences is not a list",
        ),
        (
            parse_v1g_tokenized_url,
            {
                "v1GTokenizedUrl": {
                    "__typename": "UrlResponse",
                    "data": {"__typename": "UrlData", "url": 1, "vin": None},
                }
            },
            "url is not a string",
        ),
        (
            parse_v1g_enroll_monitored_charging_plan,
            {
                "v1GEnrollMonitoredChargingPlan": {
                    "__typename": "EnrollmentResponse",
                    "data": {
                        "__typename": "EnrollmentData",
                        "v1GMonitoredChargingAccountStatus": False,
                    },
                }
            },
            "v1GMonitoredChargingAccountStatus is not a string",
        ),
        (
            parse_v1g_cancel_monitored_charging_plan,
            {
                "v1GCancelMonitoredChargingPlan": {
                    "__typename": "CancellationResponse",
                    "statusCode": 1000,
                }
            },
            "statusCode is not a string",
        ),
    ),
)
def test_v1g_parsers_reject_malformed_or_missing_fields(
    parser: V1GParser,
    payload: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(ResponseError, match=message):
        parser(payload)
