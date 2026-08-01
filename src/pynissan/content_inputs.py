from __future__ import annotations

from .content_models import ClientType
from .graphql_input import UNSET, UnsetType, optional_input_fields, serialize_enum


def contact_us_variables(client_type: ClientType) -> dict[str, object]:
    """Serialize the required contact-link client type."""

    return {"clientType": serialize_enum(client_type)}


def faq_variables(
    categories: tuple[str | None, ...] | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize optional nullable FAQ category filters."""

    serialized: object = list(categories) if isinstance(categories, tuple) else categories
    return optional_input_fields(categories=serialized)


def live_chat_hours_variables(
    departments: tuple[str | None, ...] | UnsetType | None = UNSET,
    enhanced_chat: bool | UnsetType | None = UNSET,
) -> dict[str, object]:
    """Serialize optional live-chat department and implementation filters."""

    serialized: object = list(departments) if isinstance(departments, tuple) else departments
    return optional_input_fields(
        departments=serialized,
        enhancedChat=enhanced_chat,
    )
