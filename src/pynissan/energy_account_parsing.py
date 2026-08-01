from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum

from .energy_account_models import (
    EnergyAccountConnector,
    EnergyAccountData,
    EnergyAccountStatus,
    EnergyAccountStatusReason,
    EnergyAccountStatusResult,
    EnergyNacsStatus,
    EnergyPncStatus,
    EnergyToggleStatus,
)
from .exceptions import ResponseError


def parse_account_status(
    data: Mapping[str, object],
) -> EnergyAccountStatusResult | None:
    """Parse the nullable Nissan Energy account status response."""

    root_field = "accountStatus"
    root = _root(data, root_field)
    if root is None:
        return None

    raw_data = _optional_typed_object(root.get("data"), f"{root_field}.data")
    account_data = None
    if raw_data is not None:
        connectors_path = f"{root_field}.data.connectors"
        raw_connectors = _nullable_list(raw_data.get("connectors"), connectors_path)
        connectors: tuple[EnergyAccountConnector | None, ...] | None = None
        if raw_connectors is not None:
            parsed_connectors: list[EnergyAccountConnector | None] = []
            for index, raw_connector in enumerate(raw_connectors):
                if raw_connector is None:
                    parsed_connectors.append(None)
                    continue
                parsed_connectors.append(
                    _parse_connector(raw_connector, f"{connectors_path}[{index}]")
                )
            connectors = tuple(parsed_connectors)

        account_data = EnergyAccountData(
            status=_nullable_enum(
                raw_data.get("status"),
                EnergyAccountStatus,
                f"{root_field}.data.status",
            ),
            status_reason=_nullable_enum(
                raw_data.get("statusReason"),
                EnergyAccountStatusReason,
                f"{root_field}.data.statusReason",
            ),
            pnc_status=_nullable_enum(
                raw_data.get("pncStatus"),
                EnergyPncStatus,
                f"{root_field}.data.pncStatus",
            ),
            pnc_status_reason=_nullable_string(
                raw_data.get("pncStatusReason"),
                f"{root_field}.data.pncStatusReason",
            ),
            toggle_status=_nullable_enum(
                raw_data.get("toggleStatus"),
                EnergyToggleStatus,
                f"{root_field}.data.toggleStatus",
            ),
            nacs_status=_nullable_enum(
                raw_data.get("nacsStatus"),
                EnergyNacsStatus,
                f"{root_field}.data.nacsStatus",
            ),
            connectors=connectors,
        )

    return EnergyAccountStatusResult(
        status_code=_nullable_string(root.get("statusCode"), f"{root_field}.statusCode"),
        status_message=_nullable_string(
            root.get("statusMessage"),
            f"{root_field}.statusMessage",
        ),
        timestamp=_nullable_string(root.get("timestamp"), f"{root_field}.timestamp"),
        data=account_data,
    )


def _parse_connector(value: object, path: str) -> EnergyAccountConnector:
    connector = _typed_object(value, path)
    return EnergyAccountConnector(
        id=_nullable_string(connector.get("id"), f"{path}.id"),
        connector_name=_nullable_string(
            connector.get("connectorName"),
            f"{path}.connectorName",
        ),
    )


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


def _nullable_enum[EnumT: StrEnum](
    value: object,
    enum_type: type[EnumT],
    path: str,
) -> EnumT | None:
    raw_value = _nullable_string(value, path)
    if raw_value is None:
        return None
    try:
        return enum_type(raw_value)
    except ValueError:
        unknown_value = getattr(enum_type, "UNKNOWN_VALUE", None)
        if isinstance(unknown_value, enum_type):
            return unknown_value
        raise ResponseError(f"{path} has an unsupported value: {raw_value}") from None
