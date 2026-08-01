from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime

from .account_parsing import (
    _required_field,
    _required_nullable_string,
    _required_string,
    _root,
    _typename,
)
from .exceptions import ResponseError
from .second_delivery_models import (
    SecondDeliveryOperationError,
    SecondDeliveryOperationResult,
    SecondDeliveryOperationSuccess,
    UnselectedSecondDeliveryResult,
)


def _parse_operation_result(
    data: Mapping[str, object],
    field: str,
    success_typename: str,
    error_typenames: set[str],
) -> SecondDeliveryOperationResult | None:
    root = _root(data, field)
    if root is None:
        return None
    typename = _typename(root, field)
    if typename == success_typename:
        success = _required_field(root, "success", f"{field}.success")
        if not isinstance(success, bool):
            raise ResponseError(f"{field}.success is not a boolean")
        return SecondDeliveryOperationSuccess(success)
    if typename in error_typenames:
        return SecondDeliveryOperationError(
            typename,
            _required_nullable_string(root, "message", f"{field}.message"),
        )
    return UnselectedSecondDeliveryResult(typename)


def _required_nullable_float(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> float | None:
    value = _required_field(container, field, path)
    if value is None:
        return None
    if not isinstance(value, int | float) or isinstance(value, bool):
        raise ResponseError(f"{path} is not a number")
    return float(value)


def _required_datetime(container: Mapping[str, object], field: str, path: str) -> datetime:
    value = _required_string(container, field, path)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ResponseError(f"{path} is not an ISO date-time") from None


def _required_nullable_datetime(
    container: Mapping[str, object],
    field: str,
    path: str,
) -> datetime | None:
    value = _required_nullable_string(container, field, path)
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ResponseError(f"{path} is not an ISO date-time") from None
