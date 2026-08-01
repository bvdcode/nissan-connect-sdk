from __future__ import annotations

from datetime import datetime

from .graphql_input import serialize_datetime, serialize_enum
from .ota_models import DataWipeType


def download_ota_update_input(ota_update_id: str) -> dict[str, object]:
    """Serialize a download request using Nissan's GraphQL field names."""

    return {"otaUpdateId": ota_update_id}


def ota_activation_schedule_input(
    ota_update_id: str,
    scheduled_date: datetime,
) -> dict[str, object]:
    """Serialize a scheduled OTA activation input."""

    return {
        "otaUpdateId": ota_update_id,
        "scheduledDate": serialize_datetime(scheduled_date),
    }


def data_wipe_type_input(value: DataWipeType) -> str:
    """Serialize a schema-valid data-wipe target."""

    return serialize_enum(value)
